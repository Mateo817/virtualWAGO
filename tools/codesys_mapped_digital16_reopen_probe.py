from __future__ import print_function

"""Read-only reopen verification for the native offline WORD16 bridge probe.

Run from the installed CODESYS Script environment after the builder has saved
its project and mapping CSV. The only created file is a temporary mapping CSV
inside VIRTUALWAGO_PRIVATE_BUILD_DIR, removed after inspection.
"""

from scriptengine import *
import hashlib
import imp
import json
import os


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TOOLS_DIR = os.path.dirname(os.path.abspath(__file__))
BUILD_DIR = os.environ.get("VIRTUALWAGO_PRIVATE_BUILD_DIR")
BUILDER_PATH = os.path.join(TOOLS_DIR, "codesys_mapped_digital16_bridge_probe.py")
PROJECT_PATH = os.path.join(BUILD_DIR, "mapped-digital16-bridge-probe.project") if BUILD_DIR else None
CSV_PATH = os.path.join(BUILD_DIR, "mapped-digital16-bridge-probe-mapping.csv") if BUILD_DIR else None
SOURCE_PATH = os.path.join(REPO_ROOT, "prototype", "iec", "minimal_io_16_bridge_probe.st")
REOPEN_CSV_PATH = os.path.join(BUILD_DIR, "mapped-digital16-bridge-probe-reopened-mapping.csv") if BUILD_DIR else None


def fail(message):
    raise Exception("DIGITAL16 READ-ONLY REOPEN stopped: " + message)


def digest(path):
    value = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            value.update(block)
    return value.hexdigest()


def read_bytes(path):
    with open(path, "rb") as stream:
        return stream.read()


def require(condition, message):
    if not condition:
        fail(message)


def verify_saved_task_facts(facts):
    if (facts.get("task_count") != 1 or not facts.get("kind_is_cyclic")
            or str(facts.get("interval")) != "20" or str(facts.get("interval_unit")) != "ms"
            or facts.get("pous") != ["PLC_PRG"]):
        fail("saved MainTask configuration mismatch: " + repr(facts))


def verify_saved_tcm_facts(facts):
    if (facts.get("id") != 41 or facts.get("param_type") != "std:UDINT"
            or str(facts.get("value")) != "0"):
        fail("saved TCM parameter 41 std:UDINT zero readback mismatch: " + repr(facts))


def run():
    require(bool(BUILD_DIR), "set VIRTUALWAGO_PRIVATE_BUILD_DIR to the builder's private directory")
    require(os.path.isfile(BUILDER_PATH), "own WORD16 builder is missing")
    require(os.path.isfile(PROJECT_PATH), "saved native project is missing")
    require(os.path.isfile(CSV_PATH), "saved mapping CSV is missing")
    require(os.path.isfile(SOURCE_PATH), "pinned IEC source is missing")
    require(not os.path.exists(REOPEN_CSV_PATH), "temporary reopen CSV already exists; preserve it")
    b = imp.load_source("digital16_bridge_probe_reopen_validation", BUILDER_PATH)

    project_hash_before = digest(PROJECT_PATH)
    csv_hash_before = digest(CSV_PATH)
    source_hash = digest(SOURCE_PATH)
    builder_hash = digest(BUILDER_PATH)
    require(source_hash == b.SOURCE_SHA256, "IEC source differs from immutable builder pin")
    project = projects.open(PROJECT_PATH, primary=True)
    reopen_csv_created = False
    try:
        apps = [obj for obj in project.get_children(True) if getattr(obj, "is_application", False)]
        require(len(apps) == 1, "expected one saved Application")
        app = apps[0]
        require(app.get_name() == "Application", "unexpected application name")
        pou_matches = app.find_ignore_transient_objects("PLC_PRG", True)
        require(len(pou_matches) == 1, "expected one saved PLC_PRG")
        pou = pou_matches[0]
        source_text = read_bytes(SOURCE_PATH).decode("utf-8")
        split = source_text.index("END_VAR") + len("END_VAR")
        require(pou.textual_declaration.text == source_text[:split], "saved IEC declaration differs from pinned source")
        require(pou.textual_implementation.text == source_text[split:].lstrip("\r\n"),
                "saved IEC implementation differs from pinned source")

        devices = b.devices_under(project)
        expected_terminals = [(b.TERMINAL_TYPE, ident, version) for _, ident, version in b.TERMINALS]
        terminal_objects = [obj for obj in devices if b.device_id(obj)[0] == b.TERMINAL_TYPE]
        actual_terminal_order = [b.device_id(obj) for obj in terminal_objects]
        require(actual_terminal_order == expected_terminals,
                "saved terminal order/identities mismatch: " + repr(actual_terminal_order))
        local_buses = [obj for obj in devices if b.device_id(obj) == b.LOCALBUS]
        require(len(local_buses) == 1, "expected one pinned LocalBus")
        tcm_parameters = [p for c in local_buses[0].connectors for p in c.host_parameters if int(p.id) == 41]
        require(len(tcm_parameters) == 1, "unique TCM41 connector parameter required")
        tcm = tcm_parameters[0]
        tcm_readback = {"id": int(tcm.id), "param_type": str(tcm.param_type),
                        "value": str(tcm.value), "default": str(tcm.default_value)}
        verify_saved_tcm_facts(tcm_readback)
        enabled_nodes = local_buses + terminal_objects
        require(all(obj.is_enabled() for obj in enabled_nodes), "LocalBus or terminal is disabled")

        task_configs = [obj for obj in app.get_children(True) if getattr(obj, "is_task_configuration", False)]
        require(len(task_configs) == 1, "expected one saved task configuration")
        tasks = [obj for obj in task_configs[0].get_children(False) if getattr(obj, "is_task", False)]
        require(len(tasks) == 1, "expected one saved cyclic task")
        task = tasks[0]
        task_facts = {
            "task_count": len(tasks),
            "kind": str(task.kind_of_task),
            "kind_is_cyclic": task.kind_of_task == KindOfTask.Cyclic,
            "interval": str(task.interval),
            "interval_unit": str(task.interval_unit),
            "pous": [str(item) for item in task.pous],
        }
        verify_saved_task_facts(task_facts)

        native_mappings = [
            b.native_word_mapping_readback(
                terminal_objects[0], "_IN", 0x01000000, "Input", "local:InputField",
                "Application.PLC_PRG.InputWord"),
            b.native_word_mapping_readback(
                terminal_objects[1], "_OUT", 0x03000000, "Output", "local:OutputField",
                "Application.PLC_PRG.OutputWord"),
        ]

        controllers = [obj for obj in devices if b.device_id(obj) == b.CONTROLLER]
        require(len(controllers) == 1, "expected one pinned controller")
        reopen_csv_created = True
        controllers[0].export_io_mappings_as_csv(REOPEN_CSV_PATH)
        reopened_csv_bytes = read_bytes(REOPEN_CSV_PATH)
        original_csv_bytes = read_bytes(CSV_PATH)
        mapping_result = b.verify_export(
            REOPEN_CSV_PATH, "Application.PLC_PRG.InputWord", "Application.PLC_PRG.OutputWord")
        require(reopened_csv_bytes == original_csv_bytes, "reopened mapping export is not byte-identical")
        reopened_csv_sha256 = hashlib.sha256(reopened_csv_bytes).hexdigest()
        diagnostics = b.diagnostic_counts()
        b.require_clean("read-only reopen", diagnostics)
        enabled_node_ids = [repr(b.device_id(obj)) for obj in enabled_nodes]
        project.close()
        project = None
    finally:
        if project is not None:
            project.close()
        if reopen_csv_created and os.path.exists(REOPEN_CSV_PATH):
            os.remove(REOPEN_CSV_PATH)

    project_hash_after = digest(PROJECT_PATH)
    csv_hash_after = digest(CSV_PATH)
    source_hash_after = digest(SOURCE_PATH)
    require(project_hash_before == project_hash_after, "project bytes changed during read-only reopen")
    require(csv_hash_before == csv_hash_after, "saved mapping CSV changed during read-only reopen")
    require(source_hash == source_hash_after, "pinned IEC source changed during read-only reopen")
    print("VIRTUALWAGO_DIGITAL16_BRIDGE_PROBE_REOPEN_RESULT:" + json.dumps({
        "status": "PASS",
        "scope": "Read-only reopen and mapping export; no save, build, download, gateway, or device operation",
        "builder_sha256": builder_hash,
        "source_sha256": source_hash,
        "source_sha256_after": source_hash_after,
        "project_sha256_before": project_hash_before,
        "project_sha256_after": project_hash_after,
        "mapping_csv_sha256": csv_hash_before,
        "reopened_mapping_csv_sha256": reopened_csv_sha256,
        "mapping_csv_byte_identical": True,
        "terminal_order": actual_terminal_order,
        "terminals": [{"article": name, "type": b.TERMINAL_TYPE, "id": ident,
                       "version": version, "descriptor_sha256": b.DESCRIPTOR_SHA256[name]}
                      for name, ident, version in b.TERMINALS],
        "controller": b.CONTROLLER,
        "enabled_nodes": enabled_node_ids,
        "native_word_mappings": native_mappings,
        "tcm_readback": tcm_readback,
        "saved_task": task_facts,
        "task_interval_ms": 20,
        "output_permit_initial": b.OUTPUT_PERMIT_INITIAL,
        "requested_output_transform": "InputWord XOR WORD#16#A596",
        "mapping": mapping_result,
        "report_counts": {"parent_words": 2, "digital_inputs": 16, "digital_outputs": 16},
        "diagnostics": diagnostics,
        "save_build_download": "NOT_RUN",
    }))
    print("PROJECT_UNCHANGED:" + project_hash_after)



if __name__ == "__main__":
    run()
