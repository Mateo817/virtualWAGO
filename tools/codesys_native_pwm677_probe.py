from __future__ import print_function

"""Build/reopen a pinned offline CODESYS 750-677 raw-WORD cycle probe.

This observes the IDE's exported process image for the supplied engineering
description and compiles a deterministic IEC passthrough cycle. It does not
connect to a controller or establish the physical meaning of module inputs,
runtime execution, or PWM/terminal behavior. Keep the mode at the
vendor-documented PWM DC default; this description exposes no operating-mode
parameter to this probe.
"""
from scriptengine import *
import csv
import hashlib
import json
import os
import re


HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
BUILD_DIR = os.environ.get("VIRTUALWAGO_PRIVATE_BUILD_DIR")
REOPEN = os.environ.get("VIRTUALWAGO_REOPEN_ONLY") == "1"
CONTROLLER = (4096, "1006 120C", "6.4.6.11")
LOCALBUS = (32778, "Wago 750-Series Local Bus Interface", "2.1.0.1")
BUS_INTERFACE = "Wago.Kbus"
TERMINAL = (32776, "07500677000000001616", "2.0.0.3")
DEVICE_NAME = "_750_677"
DESCRIPTOR_SHA256 = "15dcba17a7186fc3dd91fc2b47c806bf7016e6e0ebc949b352c9549f5124c780"
MANUAL_SHA256 = "df130ee3f7f22e81d3439b6d1797d123194626b9091a0e9ec0f4ea149b6035f0"
MANUAL_URL = "https://www.wago.com/wagoweb/documentation/750/eng_manu/modules/m07500677_00000000_0en.pdf"
SOURCE_PATH = os.path.join(ROOT, "prototype", "iec", "native_pwm677_probe.st")
SOURCE_SHA256 = "9bd225d6f40169d14d9c43a147a41a2cf9b724a4460b97f18356a39215482357"
CYCLE_ASSIGNMENTS = tuple(
    line for channel in range(1, 5) for line in (
        "PwmControl%d := BYTE#0;" % channel,
        "PwmReservedOutput%d := BYTE#0;" % channel,
        "PwmOutputValue%d := PwmInputValue%d;" % (channel, channel),
    )
)

PROJECT_PATH = os.path.join(BUILD_DIR, "native-pwm677.project") if BUILD_DIR else None
MAPPING_PATH = os.path.join(BUILD_DIR, "native-pwm677-mapping.csv") if BUILD_DIR else None
REOPEN_MAPPING_PATH = os.path.join(BUILD_DIR, "native-pwm677-reopen.csv") if BUILD_DIR else None
APP_PATH = os.path.join(BUILD_DIR, "native-pwm677.app") if BUILD_DIR else None
CRC_PATH = os.path.join(BUILD_DIR, "native-pwm677.crc") if BUILD_DIR else None
ARTIFACT_PATHS = (PROJECT_PATH, MAPPING_PATH, APP_PATH, CRC_PATH)

IEC_BYTE_INPUT = re.compile(r"\A%IB([0-9]+)\Z")
IEC_WORD_INPUT = re.compile(r"\A%IW([0-9]+)\Z")
IEC_BYTE_OUTPUT = re.compile(r"\A%QB([0-9]+)\Z")
IEC_WORD_OUTPUT = re.compile(r"\A%QW([0-9]+)\Z")


def fail(message):
    raise Exception("PWM677 OFFLINE stopped: " + message)


def digest(path):
    with open(path, "rb") as stream:
        data = stream.read()
    if not data:
        fail("empty source or artifact: " + os.path.basename(path))
    return hashlib.sha256(data).hexdigest()


def device_id(obj):
    ident = obj.get_device_identification()
    return (ident.type, ident.id, ident.version)


def devices_under(tree_object):
    return [obj for obj in tree_object.get_children(True) if getattr(obj, "is_device", False)]


def diagnostic_counts():
    counts = {"errors": 0, "warnings": 0}
    for category in system.get_message_categories():
        category_id = category.ToString("B")
        counts["errors"] += len(system.get_message_objects(category_id, Severity.FatalError | Severity.Error))
        counts["warnings"] += len(system.get_message_objects(category_id, Severity.Warning))
    return counts


def require_clean(stage, counts):
    if counts["errors"] or counts["warnings"]:
        fail(stage + " diagnostics are not clean: " + str(counts))


def process_fields():
    fields = []
    for channel in range(1, 5):
        base = 0x01000000 + (channel - 1) * 3
        fields.extend([
            {"id": base, "name": "_STA " + str(channel), "type": "std:BYTE",
             "direction": "input", "variable": "PwmStatus" + str(channel), "width": 1},
            {"id": base + 1, "name": "_RES " + str(channel), "type": "std:BYTE",
             "direction": "input", "variable": "PwmReservedInput" + str(channel), "width": 1},
            {"id": base + 2, "name": "_IW " + str(channel), "type": "std:WORD",
             "direction": "input", "variable": "PwmInputValue" + str(channel), "width": 2},
        ])
    for channel in range(1, 5):
        base = 0x03000000 + (channel - 1) * 3
        fields.extend([
            {"id": base, "name": "_CTR " + str(channel), "type": "std:BYTE",
             "direction": "output", "variable": "PwmControl" + str(channel), "width": 1},
            {"id": base + 1, "name": "_RES " + str(channel), "type": "std:BYTE",
             # The IDE's observed six-column export disambiguates the output
             # reserved byte from the input parameter with the same name by
             # appending its per-device duplicate counter.
             "export_name": "_RES " + str(channel) + "@1",
             "direction": "output", "variable": "PwmReservedOutput" + str(channel), "width": 1},
            {"id": base + 2, "name": "_QW " + str(channel), "type": "std:WORD",
             "direction": "output", "variable": "PwmOutputValue" + str(channel), "width": 2},
        ])
    return fields


def read_mapping(path):
    rows = []
    with open(path, "r") as stream:
        for row in csv.reader(stream, delimiter=";"):
            if not row or row[0].startswith("//"):
                continue
            if len(row) != 6:
                fail("mapping CSV row does not match observed six-column export schema")
            rows.append(row)
    return rows


def mapping_key(row):
    if row[4].startswith("%I"):
        direction = "input"
    elif row[4].startswith("%Q"):
        direction = "output"
    else:
        direction = "unknown"
    return row[1], row[5], direction


def export_parameter_name(field):
    return field.get("export_name", field["name"])


def assign_variables(path):
    rows = read_mapping(path)
    with open(path, "r") as stream:
        comments = [line.rstrip("\r\n") for line in stream if line.startswith("//")]
    expected = dict(((export_parameter_name(field), field["direction"]),
                     "Application.PLC_PRG." + field["variable"])
                    for field in process_fields())
    seen = set()
    for row in rows:
        key = mapping_key(row)
        if row[5] != DEVICE_NAME or (row[1], key[2]) not in expected:
            continue
        assignment_key = (row[1], key[2])
        if assignment_key in seen:
            fail("duplicate descriptor parameter in generated mapping CSV: " + repr(assignment_key))
        row[0] = expected[assignment_key]
        seen.add(assignment_key)
    if seen != set(expected):
        fail("mapping export omitted descriptor process fields: " + repr(sorted(set(expected) - seen)))
    with open(path, "w") as stream:
        for line in comments:
            stream.write(line + "\r\n")
        writer = csv.writer(stream, delimiter=";", lineterminator="\r\n")
        writer.writerows(rows)


def verify_mapping_rows(rows):
    fields = process_fields()
    indexed = {}
    for row in rows:
        if len(row) != 6:
            fail("mapping CSV row does not match observed six-column schema")
        key = mapping_key(row)
        if key in indexed:
            fail("duplicate parameter/device mapping row: " + repr(key))
        indexed[key] = row
    expected_keys = set((export_parameter_name(field), DEVICE_NAME, field["direction"])
                        for field in fields)
    actual_keys = set(key for key in indexed if key[1] == DEVICE_NAME)
    if actual_keys != expected_keys:
        fail("unexpected or missing 750-677 process parameters: " + repr(actual_keys ^ expected_keys))
    direction_specs = {
        "input": {"std:BYTE": (IEC_BYTE_INPUT, "IB"), "std:WORD": (IEC_WORD_INPUT, "IW")},
        "output": {"std:BYTE": (IEC_BYTE_OUTPUT, "QB"), "std:WORD": (IEC_WORD_OUTPUT, "QW")},
    }
    image = {"input": [], "output": []}
    for field in fields:
        row = indexed[(export_parameter_name(field), DEVICE_NAME, field["direction"])]
        expected_variable = "Application.PLC_PRG." + field["variable"]
        address_pattern, address_kind = direction_specs[field["direction"]][field["type"]]
        match = address_pattern.match(row[4])
        if row[0] != expected_variable or match is None:
            fail("mapping variable or IEC address direction/type mismatch: " + repr(row))
        address_index = int(match.group(1), 10)
        offset = address_index if address_kind.endswith("B") else address_index * 2
        image[field["direction"]].append({
            "parameter_id": field["id"], "parameter": field["name"],
            "export_parameter": row[1],
            "variable": expected_variable, "iec_address": row[4],
            "byte_offset": offset, "byte_width": field["width"],
        })

    extents = {}
    for direction, mapped in image.items():
        mapped.sort(key=lambda item: item["parameter_id"])
        occupied = {}
        for item in mapped:
            for byte in range(item["byte_offset"], item["byte_offset"] + item["byte_width"]):
                if byte in occupied:
                    fail(direction + " process fields overlap at byte " + str(byte))
                occupied[byte] = item["parameter"]
        offsets = sorted(occupied)
        if not offsets or offsets != list(range(offsets[0], offsets[-1] + 1)):
            fail(direction + " process fields contain an unexplained byte gap")
        for previous, current in zip(mapped, mapped[1:]):
            if current["byte_offset"] != previous["byte_offset"] + previous["byte_width"]:
                fail(direction + " fields do not follow descriptor order without padding/gaps")
        extents[direction] = {
            "first_byte_offset": offsets[0],
            "end_byte_offset_exclusive": offsets[-1] + 1,
            "image_bytes": len(offsets),
            "declared_scalar_bytes": sum(item["byte_width"] for item in mapped),
            "fields": mapped,
        }
    return {"input": extents["input"], "output": extents["output"],
            "csv_consistency": "PASS"}


def native_readback(terminal):
    fields = process_fields()
    actual = {}
    for connector in terminal.connectors:
        for parameter in connector.host_parameters:
            actual.setdefault(int(parameter.id), []).append(parameter)
    results = []
    for field in fields:
        matches = actual.get(field["id"], [])
        if len(matches) != 1:
            fail("native host parameter not unique: " + str(field["id"]))
        parameter = matches[0]
        facts = {
            "parameter_id": int(parameter.id), "name": parameter.name,
            "type": str(parameter.param_type), "channel": str(parameter.channel_type),
            "has_sub_elements": bool(parameter.has_sub_elements),
            "variable": parameter.io_mapping.variable,
            "maps_to_existing_variable": bool(parameter.io_mapping.maps_to_existing_variable),
        }
        if (facts["name"] != field["name"] or facts["type"] != field["type"]
                or facts["channel"].lower() != field["direction"]
                or facts["has_sub_elements"]
                or facts["variable"] != "Application.PLC_PRG." + field["variable"]
                or not facts["maps_to_existing_variable"]):
            fail("native process parameter mapping mismatch: " + repr(facts))
        results.append(facts)
    return results


def native_parameter_inventory(terminal):
    """Expose all host parameters, without interpreting unknown settings."""
    result = []
    for connector in terminal.connectors:
        for parameter in connector.host_parameters:
            facts = {
                "parameter_id": int(parameter.id), "name": parameter.name,
                "type": str(parameter.param_type), "channel": str(parameter.channel_type),
            }
            if hasattr(parameter, "value"):
                facts["current_value"] = str(parameter.value)
            if hasattr(parameter, "default_value"):
                facts["default_value"] = str(parameter.default_value)
            result.append(facts)
    result.sort(key=lambda item: item["parameter_id"])
    return result


def validate_descriptor_pin():
    descriptor_path = os.environ.get("VIRTUALWAGO_DESCRIPTOR_FILE")
    if not descriptor_path or digest(descriptor_path) != DESCRIPTOR_SHA256:
        fail("set VIRTUALWAGO_DESCRIPTOR_FILE to the pinned standard 750-677 description")


def validate_cycle_program(source):
    """Require the exact raw-word passthrough and zero control-output cycle."""
    split = source.index("END_VAR") + len("END_VAR")
    declaration, implementation = source[:split], source[split:].lstrip("\r\n")
    actual = [line.strip() for line in implementation.splitlines()
              if line.strip() and not line.strip().startswith("//")]
    if tuple(actual) != CYCLE_ASSIGNMENTS:
        fail("IEC implementation differs from the pinned raw-WORD cycle contract")
    return declaration, implementation


def run():
    if not BUILD_DIR or not os.path.isdir(BUILD_DIR):
        fail("set VIRTUALWAGO_PRIVATE_BUILD_DIR to an existing private directory")
    validate_descriptor_pin()
    source_hash = digest(SOURCE_PATH)
    if source_hash != SOURCE_SHA256:
        fail("IEC source hash mismatch")
    with open(SOURCE_PATH, "rb") as stream:
        source = stream.read().decode("utf-8")
    declaration, implementation = validate_cycle_program(source)
    system.script_prompt_handling = (ScriptPromptHandling.ForwardUnknownPrompts
                                     | ScriptPromptHandling.LogPrompts)
    if projects.primary is not None:
        fail("existing project loaded")
    if REOPEN:
        if os.path.exists(REOPEN_MAPPING_PATH):
            fail("temporary reopen export already exists")
        if any(not os.path.isfile(path) for path in ARTIFACT_PATHS):
            fail("reopen requires the preserved build artifacts")
        before_hashes = [digest(path) for path in ARTIFACT_PATHS]
        project = projects.open(PROJECT_PATH, primary=True)
        export_path = REOPEN_MAPPING_PATH
    else:
        if any(os.path.exists(path) for path in ARTIFACT_PATHS):
            fail("fresh build outputs required; preserve existing evidence")
        before_hashes = None
        project = projects.create(PROJECT_PATH, primary=True)
        if project is None:
            fail("projects.create() returned no project")
        project.add("ReferenceController", CONTROLLER[0], CONTROLLER[1], CONTROLLER[2])
        export_path = MAPPING_PATH

    try:
        devices = devices_under(project)
        controllers = [obj for obj in devices if device_id(obj) == CONTROLLER]
        buses = [obj for obj in devices if device_id(obj) == LOCALBUS]
        if len(controllers) != 1 or len(buses) != 1:
            fail("expected pinned ReferenceController and LocalBus")
        controller, bus = controllers[0], buses[0]
        if not REOPEN:
            matches = [p for c in bus.connectors for p in c.host_parameters if int(p.id) == 41]
            if len(matches) != 1:
                fail("TCM parameter 41 must be uniquely exposed")
            matches[0].value = "0"
            if int(str(matches[0].value), 0) != 0:
                fail("TCM0 readback mismatch")
            if BUS_INTERFACE not in bus.allowed_interfaces_at(0):
                fail("Wago.Kbus interface unavailable")
            bus.insert("750-677", 0, TERMINAL[0], TERMINAL[1], TERMINAL[2])
        terminals = [obj for obj in devices_under(bus) if device_id(obj)[0] == TERMINAL[0]]
        if len(terminals) != 1 or device_id(terminals[0]) != TERMINAL:
            fail("exact pinned 750-677 descriptor required")
        terminal = terminals[0]
        for obj in (bus, terminal):
            if not REOPEN:
                obj.enable()
            if not obj.is_enabled():
                fail("required native node is disabled")

        apps = [obj for obj in project.get_children(True) if getattr(obj, "is_application", False)]
        if len(apps) != 1 or apps[0].get_name() != "Application":
            fail("exactly one Application is required")
        app = apps[0]
        project.active_application = app
        matches = app.find_ignore_transient_objects("PLC_PRG", True)
        if not matches and not REOPEN:
            matches = [app.create_program("PLC_PRG", ImplementationLanguages.st)]
        if len(matches) != 1:
            fail("exactly one PLC_PRG is required")
        pou = matches[0]
        if not REOPEN:
            pou.textual_declaration.replace(new_text=declaration)
            pou.textual_implementation.replace(new_text=implementation)
        if (pou.textual_declaration.text != declaration
                or pou.textual_implementation.text != implementation):
            fail("saved IEC source differs")

        configs = [obj for obj in app.get_children(True) if getattr(obj, "is_task_configuration", False)]
        if not configs and not REOPEN:
            configs = [app.create_task_configuration()]
        if len(configs) != 1:
            fail("exactly one task configuration is required")
        tasks = [obj for obj in configs[0].get_children(False) if getattr(obj, "is_task", False)]
        if not tasks and not REOPEN:
            tasks = [configs[0].create_task("MainTask")]
        if len(tasks) != 1:
            fail("exactly one task is required")
        task = tasks[0]
        if not REOPEN:
            task.kind_of_task, task.interval, task.interval_unit = KindOfTask.Cyclic, "20", "ms"
            while len(task.pous):
                task.pous.remove(len(task.pous) - 1)
            task.pous.add("PLC_PRG")
        if (task.kind_of_task != KindOfTask.Cyclic or str(task.interval) != "20"
                or str(task.interval_unit) != "ms" or [str(p) for p in task.pous] != ["PLC_PRG"]):
            fail("task readback differs")

        if REOPEN:
            export_created = True
        controller.export_io_mappings_as_csv(export_path)
        if not REOPEN:
            assign_variables(export_path)
            controller.import_io_mappings_from_csv(export_path)
            controller.export_io_mappings_as_csv(export_path)
        mapping = verify_mapping_rows(read_mapping(export_path))
        native = native_readback(terminal)
        parameter_inventory = native_parameter_inventory(terminal)
        if not REOPEN:
            project.save()
            require_clean("prebuild", diagnostic_counts())
            app.rebuild()
            require_clean("rebuild", diagnostic_counts())
            app.generate_code()
            require_clean("code generation", diagnostic_counts())
            app.create_boot_application(APP_PATH, True, False)
            require_clean("boot image", diagnostic_counts())
            controller.export_io_mappings_as_csv(MAPPING_PATH)
            mapping = verify_mapping_rows(read_mapping(MAPPING_PATH))
            project.save()
        elif digest(export_path) != digest(MAPPING_PATH):
            fail("reopened mapping export differs from preserved build export")

        project.close()
        project = None
        after_hashes = [digest(path) for path in ARTIFACT_PATHS]
        if REOPEN and before_hashes != after_hashes:
            fail("read-only reopen changed saved artifacts")
        if digest(SOURCE_PATH) != source_hash:
            fail("IEC source changed during operation")
        print("VIRTUALWAGO_PWM677_OFFLINE_RESULT:" + json.dumps({
            "status": "PASS", "operation": "read-only reopen" if REOPEN else "offline native build",
            "source_sha256": source_hash, "script_sha256": digest(__file__),
            "descriptor_sha256": DESCRIPTOR_SHA256, "terminal": TERMINAL,
            "mapping": mapping, "native_readback": native,
            "native_host_parameter_inventory": parameter_inventory,
            "artifact_sha256": after_hashes,
            "task_interval_ms": 20, "tcm_value": 0,
            "mode": {"setting": "PWM DC", "basis": "official manual default, HW/FW 01",
                     "configured_by_probe": False,
                     "limitation": "device description exposes no mode parameter; PWM Frq not configured"},
            "cycle_probe": {"kind": "raw WORD passthrough integration probe",
                            "input_meaning": "not established; raw mapped WORD values only",
                            "assignments": list(CYCLE_ASSIGNMENTS),
                            "control_and_reserved_bytes": "assigned zero every IEC cycle",
                            "physical_PWM_effect": "not tested or claimed"},
            "manual": {"sha256": MANUAL_SHA256, "url": MANUAL_URL,
                       "pages": "11-17", "scope": "manufacturer process-image and mode description"},
            "scope": "native IDE process-image and IEC raw-WORD integration build or read-only reopen only; no runtime, physical module-input meaning, PWM effect, or hardware proof"}))
    finally:
        if project is not None:
            project.close()
        if REOPEN and 'export_created' in locals() and export_created and os.path.exists(export_path):
            os.remove(export_path)


if __name__ == "__main__":
    run()
