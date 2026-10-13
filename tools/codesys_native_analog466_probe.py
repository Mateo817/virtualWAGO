from __future__ import print_function

"""Pinned native 750-466 offline build or read-only reopen; no online API."""
from scriptengine import *
import csv
import hashlib
import imp
import json
import os


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD_DIR = os.environ.get("VIRTUALWAGO_PRIVATE_BUILD_DIR")
REOPEN = os.environ.get("VIRTUALWAGO_REOPEN_ONLY") == "1"
TERMINAL = (32776, "07500466000000000400", "2.0.0.9")
DESCRIPTOR_SHA256 = "aa9bb802e2d2656ec9e101f1537aebc23f79487437513bdc9588f0d283ecca51"
SOURCE_PATH = os.path.join(ROOT, "prototype", "iec", "native_analog466_probe.st")
SOURCE_SHA256 = "f499b6c11e97e7f520b8008191eb95fc7efe224b98d86d9ec800550bf51766f8"
CHANNELS = [(16777216, "_IW 1", "Application.PLC_PRG.InputWord1"),
            (16777217, "_IW 2", "Application.PLC_PRG.InputWord2")]


def fail(message):
    raise Exception("ANALOG466 OFFLINE stopped: " + message)


def digest(path):
    with open(path, "rb") as stream:
        data = stream.read()
    if not data:
        fail("empty source or artifact: " + os.path.basename(path))
    return hashlib.sha256(data).hexdigest()


def verify_mapping_rows(rows):
    result = []
    for pid, name, variable in CHANNELS:
        matches = [row for row in rows if row[1] == name and row[5] == "_750_466"]
        if len(matches) != 1:
            fail("expected one exported input WORD: " + name)
        row = matches[0]
        if row[0] != variable or not row[4].startswith("%IW"):
            fail("mapped variable or input WORD direction mismatch: " + name)
        result.append({"parameter_id": pid, "name": name, "variable": variable,
                       "iec_address": row[4]})
    if len(set(row["iec_address"] for row in result)) != 2:
        fail("analog channel addresses alias")
    terminal_rows = [row for row in rows if row[5] == "_750_466"]
    if len(terminal_rows) != 2:
        fail("unexpected additional native analog mapping rows")
    return result


def native_readback(terminal):
    rows = []
    for pid, name, variable in CHANNELS:
        matches = [p for c in terminal.connectors for p in c.host_parameters if int(p.id) == pid]
        if len(matches) != 1:
            fail("native parameter not unique: " + str(pid))
        p = matches[0]
        facts = {"parameter_id": int(p.id), "name": p.name, "type": str(p.param_type),
                 "channel": str(p.channel_type), "has_sub_elements": bool(p.has_sub_elements),
                 "variable": p.io_mapping.variable,
                 "maps_to_existing_variable": bool(p.io_mapping.maps_to_existing_variable)}
        if (facts["name"] != name or facts["type"] != "std:WORD"
                or facts["channel"].lower() != "input" or facts["has_sub_elements"]
                or facts["variable"] != variable or not facts["maps_to_existing_variable"]):
            fail("native input WORD mapping mismatch: " + repr(facts))
        rows.append(facts)
    return rows


def run():
    if not BUILD_DIR or not os.path.isdir(BUILD_DIR):
        fail("set VIRTUALWAGO_PRIVATE_BUILD_DIR to a private directory")
    descriptor_path = os.environ.get("VIRTUALWAGO_DESCRIPTOR_FILE")
    if not descriptor_path or digest(descriptor_path) != DESCRIPTOR_SHA256:
        fail("set VIRTUALWAGO_DESCRIPTOR_FILE to the pinned installed description")
    system.script_prompt_handling = (ScriptPromptHandling.ForwardUnknownPrompts
                                     | ScriptPromptHandling.LogPrompts)
    b = imp.load_source("analog466_existing_offline_helpers",
                        os.path.join(HERE, "codesys_mapped_digital16_bridge_probe.py"))
    project_path = os.path.join(BUILD_DIR, "native-analog466.project")
    mapping_path = os.path.join(BUILD_DIR, "native-analog466.csv")
    export_path = os.path.join(BUILD_DIR, "native-analog466-reopen.csv") if REOPEN else mapping_path
    app_path = os.path.join(BUILD_DIR, "native-analog466.app")
    crc_path = os.path.join(BUILD_DIR, "native-analog466.crc")
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
            if b.BUS_INTERFACE not in bus.allowed_interfaces_at(0):
                fail("Wago.Kbus interface unavailable")
            bus.insert("750-466", 0, TERMINAL[0], TERMINAL[1], TERMINAL[2])
        terminals = [o for o in b.devices_under(bus) if b.device_id(o)[0] == TERMINAL[0]]
        if len(terminals) != 1 or b.device_id(terminals[0]) != TERMINAL:
            fail("exact analog descriptor required")
        terminal = terminals[0]
        for obj in (bus, terminal):
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
            for row in rows:
                for _, name, variable in CHANNELS:
                    if row[1] == name and row[5] == "_750_466":
                        row[0] = variable
            with open(export_path, "w") as stream:
                for line in headers:
                    stream.write(line)
                writer = csv.writer(stream, delimiter=";")
                writer.writerows(rows)
            controller.import_io_mappings_from_csv(export_path)
            controller.export_io_mappings_as_csv(export_path)
        mapping = verify_mapping_rows(b.read_mapping(export_path))
        native = native_readback(terminal)
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
        else:
            if digest(export_path) != digest(mapping_path):
                fail("reopened mapping bytes differ")
        project.close()
        project = None
        after_hashes = [digest(path) for path in (project_path, mapping_path, app_path, crc_path)]
        if REOPEN and before_hashes != after_hashes:
            fail("reopen changed saved files")
        if digest(SOURCE_PATH) != source_hash:
            fail("source changed during operation")
        print("VIRTUALWAGO_ANALOG466_RESULT:" + json.dumps({
            "status": "PASS", "operation": "read-only reopen" if REOPEN else "offline build",
            "source_sha256": source_hash, "script_sha256": digest(__file__),
            "helper_sha256": digest(os.path.join(HERE, "codesys_mapped_digital16_bridge_probe.py")),
            "descriptor_sha256": DESCRIPTOR_SHA256, "terminal": TERMINAL,
            "mapping": mapping, "native_readback": native, "artifact_sha256": after_hashes,
            "task_interval_ms": 20, "tcm": 0, "diagnostics": b.diagnostic_counts(),
            "scope": "native IDE mapping/build or read-only reopen only; no runtime, register or hardware proof"}))
    finally:
        if project is not None:
            project.close()
        if export_created and os.path.exists(export_path):
            os.remove(export_path)


if __name__ == "__main__":
    run()
