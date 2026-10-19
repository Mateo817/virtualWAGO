from __future__ import print_function

"""Pinned offline 750-466 input to 750-550 output mapping/build probe.

This creates or reopens a private CODESYS project only. It does not connect to
a controller, model analog scaling, or prove an ADI/runtime/hardware contract.
"""
from scriptengine import *
import csv
import hashlib
import imp
import json
import os
import re


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD_DIR = os.environ.get("VIRTUALWAGO_PRIVATE_BUILD_DIR")
REOPEN = os.environ.get("VIRTUALWAGO_REOPEN_ONLY") == "1"
TERMINALS = [
    (32776, "07500466000000000400", "2.0.0.9"),
    (32776, "07500550000000000004", "2.0.0.9"),
]
DESCRIPTOR_SHA256 = {
    "466": "aa9bb802e2d2656ec9e101f1537aebc23f79487437513bdc9588f0d283ecca51",
    "550": "8edb68d2b02370398251890035552779fb1edce5e6d039c2d7312d26f6927105",
}
SOURCE_PATH = os.path.join(ROOT, "prototype", "iec", "native_analog466_550_pair_probe.st")
SOURCE_SHA256 = "f1e9e10dca3e9c58ac834cb9ad6068af10fdbd4858f597e6d1f48e47c1c0d10d"
CHANNELS = [
    ("466", 16777216, "_IW 1", "input", "Application.PLC_PRG.InputWord1", re.compile(r"\A%IW[0-9]+\Z")),
    ("466", 16777217, "_IW 2", "input", "Application.PLC_PRG.InputWord2", re.compile(r"\A%IW[0-9]+\Z")),
    ("550", 50331648, "_QW 1", "output", "Application.PLC_PRG.OutputWord1", re.compile(r"\A%QW[0-9]+\Z")),
    ("550", 50331649, "_QW 2", "output", "Application.PLC_PRG.OutputWord2", re.compile(r"\A%QW[0-9]+\Z")),
]
DEVICE_NAMES = {"466": "_750_466", "550": "_750_550"}


def fail(message):
    raise Exception("ANALOG466+550 OFFLINE stopped: " + message)


def digest(path):
    with open(path, "rb") as stream:
        data = stream.read()
    if not data:
        fail("empty source or artifact: " + os.path.basename(path))
    return hashlib.sha256(data).hexdigest()


def verify_descriptor_paths():
    for suffix, key in (("466", "466"), ("550", "550")):
        path = os.environ.get("VIRTUALWAGO_" + suffix + "_DESCRIPTOR_FILE")
        if not path or digest(path) != DESCRIPTOR_SHA256[key]:
            fail("set VIRTUALWAGO_" + suffix + "_DESCRIPTOR_FILE to the pinned installed description")


def verify_mapping_rows(rows):
    result = []
    expected_keys = set()
    for suffix, pid, name, direction, variable, pattern in CHANNELS:
        device = DEVICE_NAMES[suffix]
        key = (name, device)
        expected_keys.add(key)
        matches = [row for row in rows if len(row) == 6 and (row[1], row[5]) == key]
        if len(matches) != 1:
            fail("expected exactly one native mapping row for " + repr(key))
        row = matches[0]
        if row[0] != variable or not pattern.match(row[4]):
            fail("native WORD mapping or direction mismatch for " + repr(key) + ": " + repr(row))
        result.append({"descriptor": suffix, "parameter_id": pid, "name": name,
                       "direction": direction, "variable": variable, "iec_address": row[4]})
    terminal_rows = [row for row in rows if len(row) == 6 and row[5] in DEVICE_NAMES.values()]
    if len(terminal_rows) != 4 or set((row[1], row[5]) for row in terminal_rows) != expected_keys:
        fail("unexpected or missing process mapping rows for the 466+550 pair")
    if len(set(item["iec_address"] for item in result)) != 4:
        fail("native WORD addresses alias")
    return result


def native_readback(terminal, suffix):
    rows = []
    for device_suffix, pid, name, direction, variable, _ in CHANNELS:
        if device_suffix != suffix:
            continue
        matches = [p for c in terminal.connectors for p in c.host_parameters if int(p.id) == pid]
        if len(matches) != 1:
            fail("native parameter not unique: " + str(pid))
        p = matches[0]
        facts = {"parameter_id": int(p.id), "name": p.name, "type": str(p.param_type),
                 "channel": str(p.channel_type), "has_sub_elements": bool(p.has_sub_elements),
                 "variable": p.io_mapping.variable,
                 "maps_to_existing_variable": bool(p.io_mapping.maps_to_existing_variable)}
        if (facts["name"] != name or facts["type"] != "std:WORD"
                or facts["channel"].lower() != direction or facts["has_sub_elements"]
                or facts["variable"] != variable or not facts["maps_to_existing_variable"]):
            fail("native WORD mapping mismatch: " + repr(facts))
        rows.append(facts)
    return rows


def run():
    if not BUILD_DIR or not os.path.isdir(BUILD_DIR):
        fail("set VIRTUALWAGO_PRIVATE_BUILD_DIR to a private directory")
    verify_descriptor_paths()
    system.script_prompt_handling = (ScriptPromptHandling.ForwardUnknownPrompts
                                     | ScriptPromptHandling.LogPrompts)
    b = imp.load_source("analog_pair_existing_offline_helpers",
                        os.path.join(HERE, "codesys_mapped_digital16_bridge_probe.py"))
    prefix = "native-analog466-550-pair"
    project_path = os.path.join(BUILD_DIR, prefix + ".project")
    mapping_path = os.path.join(BUILD_DIR, prefix + ".csv")
    export_path = os.path.join(BUILD_DIR, prefix + "-reopen.csv") if REOPEN else mapping_path
    app_path = os.path.join(BUILD_DIR, prefix + ".app")
    crc_path = os.path.join(BUILD_DIR, prefix + ".crc")
    source_hash = digest(SOURCE_PATH)
    if source_hash != SOURCE_SHA256:
        fail("IEC source hash mismatch")
    with open(SOURCE_PATH, "rb") as stream:
        source = stream.read().decode("utf-8")
    if projects.primary is not None:
        fail("existing project loaded")
    project = None
    before_hashes = None
    export_created = False
    try:
        if REOPEN:
            if os.path.exists(export_path):
                fail("temporary export already exists")
            before_hashes = [digest(path) for path in (project_path, mapping_path, app_path, crc_path)]
            project = projects.open(project_path, primary=True)
        else:
            if any(os.path.exists(path) for path in (project_path, mapping_path, app_path, crc_path)):
                fail("fresh build outputs required")
            project = projects.create(project_path, primary=True)
            project.add("ReferenceController", b.CONTROLLER[0], b.CONTROLLER[1], b.CONTROLLER[2])
        devices = b.devices_under(project)
        controllers = [o for o in devices if b.device_id(o) == b.CONTROLLER]
        buses = [o for o in devices if b.device_id(o) == b.LOCALBUS]
        if len(controllers) != 1 or len(buses) != 1:
            fail("expected pinned controller and local bus")
        controller, bus = controllers[0], buses[0]
        if not REOPEN:
            b.select_disabled_tcm(bus)
            for index in range(len(TERMINALS)):
                if b.BUS_INTERFACE not in bus.allowed_interfaces_at(index):
                    fail("Wago.Kbus interface unavailable at insertion index " + str(index))
            bus.insert("750-466", 0, TERMINALS[0][0], TERMINALS[0][1], TERMINALS[0][2])
            bus.insert("750-550", 1, TERMINALS[1][0], TERMINALS[1][1], TERMINALS[1][2])
        terminals = [o for o in b.devices_under(bus) if b.device_id(o)[0] == TERMINALS[0][0]]
        if len(terminals) != 2 or [b.device_id(o) for o in terminals] != TERMINALS:
            fail("expected exactly the pinned 750-466 followed by 750-550 descriptors")
        analog_in, analog_out = terminals
        for obj in (bus, analog_in, analog_out):
            if not REOPEN:
                obj.enable()
            if not obj.is_enabled():
                fail("required node disabled")
        apps = [o for o in project.get_children(True) if getattr(o, "is_application", False)]
        if len(apps) != 1 or apps[0].get_name() != "Application":
            fail("one Application required")
        app = apps[0]
        project.active_application = app
        matches = app.find_ignore_transient_objects("PLC_PRG", True)
        if not matches and not REOPEN:
            matches = [app.create_program("PLC_PRG", ImplementationLanguages.st)]
        if len(matches) != 1:
            fail("one PLC_PRG required")
        pou = matches[0]
        split = source.index("END_VAR") + len("END_VAR")
        declaration, implementation = source[:split], source[split:].lstrip("\r\n")
        if not REOPEN:
            pou.textual_declaration.replace(new_text=declaration)
            pou.textual_implementation.replace(new_text=implementation)
        if pou.textual_declaration.text != declaration or pou.textual_implementation.text != implementation:
            fail("saved source differs")
        configs = [o for o in app.get_children(True) if getattr(o, "is_task_configuration", False)]
        if not configs and not REOPEN:
            configs = [app.create_task_configuration()]
        if len(configs) != 1:
            fail("one task configuration required")
        tasks = [o for o in configs[0].get_children(False) if getattr(o, "is_task", False)]
        if not tasks and not REOPEN:
            tasks = [configs[0].create_task("MainTask")]
        if len(tasks) != 1:
            fail("one task required")
        task = tasks[0]
        if not REOPEN:
            task.kind_of_task, task.interval, task.interval_unit = KindOfTask.Cyclic, "20", "ms"
            while len(task.pous):
                task.pous.remove(len(task.pous) - 1)
            task.pous.add("PLC_PRG")
        if (task.kind_of_task != KindOfTask.Cyclic or str(task.interval) != "20"
                or str(task.interval_unit) != "ms" or [str(p) for p in task.pous] != ["PLC_PRG"]):
            fail("task readback differs")
        tcm = [p for c in bus.connectors for p in c.host_parameters if int(p.id) == 41]
        if len(tcm) != 1 or str(tcm[0].value) != "0" or str(tcm[0].param_type) != "std:UDINT":
            fail("TCM0 readback differs")
        if REOPEN:
            export_created = True
        controller.export_io_mappings_as_csv(export_path)
        if not REOPEN:
            rows = b.read_mapping(export_path)
            with open(export_path, "r") as stream:
                headers = [line for line in stream if line.startswith("//")]
            by_target = {("_IW 1", "_750_466"): "Application.PLC_PRG.InputWord1",
                         ("_IW 2", "_750_466"): "Application.PLC_PRG.InputWord2",
                         ("_QW 1", "_750_550"): "Application.PLC_PRG.OutputWord1",
                         ("_QW 2", "_750_550"): "Application.PLC_PRG.OutputWord2"}
            for row in rows:
                target = by_target.get((row[1], row[5]))
                if target is not None:
                    row[0] = target
            with open(export_path, "w") as stream:
                for line in headers:
                    stream.write(line)
                writer = csv.writer(stream, delimiter=";")
                writer.writerows(rows)
            controller.import_io_mappings_from_csv(export_path)
            controller.export_io_mappings_as_csv(export_path)
        mapping = verify_mapping_rows(b.read_mapping(export_path))
        native = {"750-466": native_readback(analog_in, "466"),
                  "750-550": native_readback(analog_out, "550")}
        b.require_clean("prebuild/reopen", b.diagnostic_counts())
        if not REOPEN:
            app.rebuild()
            b.require_clean("rebuild", b.diagnostic_counts())
            app.generate_code()
            b.require_clean("codegen", b.diagnostic_counts())
            app.create_boot_application(app_path, True, False)
            b.require_clean("boot", b.diagnostic_counts())
            controller.export_io_mappings_as_csv(export_path)
            mapping = verify_mapping_rows(b.read_mapping(export_path))
            project.save()
        elif digest(export_path) != digest(mapping_path):
            fail("reopened mapping bytes differ")
        project.close()
        project = None
        after_hashes = [digest(path) for path in (project_path, mapping_path, app_path, crc_path)]
        if REOPEN and before_hashes != after_hashes:
            fail("reopen changed saved files")
        if digest(SOURCE_PATH) != source_hash:
            fail("source changed during operation")
        print("VIRTUALWAGO_ANALOG466_550_PAIR_RESULT:" + json.dumps({
            "status": "PASS", "operation": "read-only reopen" if REOPEN else "offline build",
            "source_sha256": source_hash, "script_sha256": digest(__file__),
            "helper_sha256": digest(os.path.join(HERE, "codesys_mapped_digital16_bridge_probe.py")),
            "descriptor_sha256": DESCRIPTOR_SHA256, "terminals_in_order": TERMINALS,
            "mapping": mapping, "native_readback": native, "artifact_sha256": after_hashes,
            "task_interval_ms": 20, "tcm": 0, "diagnostics": b.diagnostic_counts(),
            "scope": "native offline IDE mapping/build or read-only reopen only; no scaling, runtime, ADI, register or hardware proof"}))
    finally:
        if project is not None:
            project.close()
        if export_created and os.path.exists(export_path):
            os.remove(export_path)


if __name__ == "__main__":
    run()
