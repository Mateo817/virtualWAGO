from __future__ import print_function

"""Build the mapped offline CODESYS candidate without changing minimal_io.st.

Creates a fresh native project, uses the real terminal descriptions, maps the
two 16-bit parent channels through the documented CSV import API, exports and
checks the resulting mapping, then performs an offline build. There are no
online, gateway, scan, login, download, upload, or runtime calls.

Keep this script and every generated artifact in the private build directory.
"""

from scriptengine import *
import csv
import hashlib
import json
import os


ROOT = os.path.dirname(os.path.abspath(__file__))
OUTPUT_PATH = os.path.join(ROOT, "mapped-io-offline.project")
APP_PATH = os.path.join(ROOT, "mapped-io.app")
CRC_PATH = os.path.join(ROOT, "mapped-io.crc")
CSV_PATH = os.path.join(ROOT, "mapped-io-mapping.csv")
OUTPUT_FILES = (OUTPUT_PATH, APP_PATH, CRC_PATH, CSV_PATH)

CONTROLLER = (4096, "1006 120C", "6.4.6.11")
LOCALBUS = (32778, "Wago 750-Series Local Bus Interface", "2.1.0.1")
BUS_INTERFACE = "Wago.Kbus"
TERMINAL_TYPE = 32776
TERMINALS = [
    ("750-1405", "9001_0750140500000000", "2.0.0.14"),
    ("750-1504", "9002_0750150400000000", "2.0.0.14"),
]

SOURCE_SHA256 = "e757410d9d9efc4f363e666190514af130d2a6be9fd46916a805cd7551588dcc"
SOURCE_ST = """PROGRAM PLC_PRG
VAR
    // Internal candidate signals only; no physical I/O mapping is supplied.
    InputWord : WORD := WORD#0;
    OutputWord : WORD := WORD#0;
    OutputPermit : BOOL := FALSE;
    CycleCounter : UDINT := UDINT#0;
END_VAR

// Default the requested output to zero on every scan.
OutputWord := WORD#0;
IF OutputPermit THEN
    OutputWord := InputWord;
END_IF;

// Saturate at the UDINT maximum so behavior does not depend on wrap settings.
IF CycleCounter < UDINT#16#FFFFFFFF THEN
    CycleCounter := CycleCounter + UDINT#1;
END_IF;
"""


def fail(message):
    raise Exception("MAPPED OFFLINE CODESYS candidate stopped: " + message)


def device_id(obj):
    ident = obj.get_device_identification()
    return (ident.type, ident.id, ident.version)


def devices_under(tree_object):
    return [obj for obj in tree_object.get_children(True) if getattr(obj, "is_device", False)]


def diagnostic_counts():
    # Count all IDE diagnostics in the fresh ScriptEngine session; the earlier
    # project filter relied on an unverified proxy property.
    counts = {"errors": 0, "warnings": 0}
    for category in system.get_message_categories():
        category_id = category.ToString("B")
        counts["errors"] += len(system.get_message_objects(category_id, Severity.FatalError | Severity.Error))
        counts["warnings"] += len(system.get_message_objects(category_id, Severity.Warning))
    return counts


def require_clean(stage, counts):
    if counts["errors"] or counts["warnings"]:
        fail(stage + " diagnostics are not clean: " + str(counts))


def read_mapping(path):
    rows = []
    with open(path, "r") as stream:
        for row in csv.reader(stream, delimiter=";"):
            if not row or row[0].startswith("//"):
                continue
            if len(row) != 6:
                fail("mapping CSV row does not match observed six-column export schema")
            rows.append([field.strip() for field in row])
    return rows


def mapping_identity(row):
    # Mapped variable; parameter name; unit; description; IEC address; device.
    return row[1], row[5]


def map_parent_words_in_csv(path, input_variable, output_variable):
    rows = read_mapping(path)
    with open(path, "r") as stream:
        comment_lines = [line.rstrip("\r\n") for line in stream if line.startswith("//")]
    targets = {
        ("_IN", "_750_1405"): input_variable,
        ("_OUT", "_750_1504"): output_variable,
    }
    seen = set()
    for row in rows:
        key = mapping_identity(row)
        if key in targets:
            if key in seen:
                fail("duplicate parent WORD channel in generated mapping CSV: " + repr(key))
            # Modify only the first CSV column, as directed by this export's
            # own header. Preserve descriptor-generated addresses verbatim.
            row[0] = targets[key]
            seen.add(key)
    if seen != set(targets.keys()):
        fail("mapping export is missing an expected parent WORD channel: " + repr(set(targets.keys()) - seen))
    with open(path, "w") as stream:
        for line in comment_lines:
            stream.write(line + "\r\n")
        writer = csv.writer(stream, delimiter=";", lineterminator="\r\n")
        for row in rows:
            writer.writerow(row)
    return {"_IN@_750_1405": targets[("_IN", "_750_1405")],
            "_OUT@_750_1504": targets[("_OUT", "_750_1504")]}


def verify_export_rows(rows, input_variable, output_variable):
    indexed = {}
    for row in rows:
        key = mapping_identity(row)
        if key in indexed:
            fail("duplicate parameter/device row in mapping export: " + repr(key))
        indexed[key] = row

    expected = {
        ("_IN", "_750_1405"): (input_variable, "Input Channels", "%IW"),
        ("_OUT", "_750_1504"): (output_variable, "Output Channels", "%QW"),
    }
    for key, (variable, description, required_direction) in expected.items():
        row = indexed.get(key)
        if (row is None or row[0] != variable or row[3] != description
                or not row[4].startswith(required_direction)):
            fail("parent WORD mapping readback mismatch for " + repr(key) + ": " + repr(row))

    channel_specs = (
        ("_IN@", "_750_1405", "Digital input", "%IX"),
        ("_OUT@", "_750_1504", "Digital output", "%QX"),
    )
    counts = {}
    for prefix, device, description, required_direction in channel_specs:
        found = [row for row in rows if row[1].startswith(prefix) and row[5] == device]
        names = set(row[1] for row in found)
        expected_names = set(prefix + str(n) for n in range(1, 17))
        if names != expected_names or len(found) != 16:
            fail("expected exactly 16 exported bit channels for " + device + "; got " + repr(sorted(names)))
        if any(row[3] != description or not row[4].startswith(required_direction) for row in found):
            fail("digital channel description/address direction mismatch for " + device)
        addresses = [row[4] for row in found]
        if len(set(addresses)) != 16:
            fail("duplicate bit-channel address in exported " + device + " rows")
        if any(row[0] for row in found):
            fail("unexpected bit child variable mapping conflicts with parent WORD on " + device)
        counts[device] = 16
    return {"parent_words": 2, "digital_inputs": counts["_750_1405"],
            "digital_outputs": counts["_750_1504"], "csv_consistency": "PASS"}


def verify_export(path, input_variable, output_variable):
    return verify_export_rows(read_mapping(path), input_variable, output_variable)


def verify_native_parameter_facts(facts, expected_id, expected_channel, expected_type,
                                  expected_variable, child_variables):
    if (int(facts["id"]) != expected_id or facts["channel_type"].lower() != expected_channel.lower()
            or facts["param_type"] != expected_type or not facts["has_sub_elements"]
            or int(facts["subelement_count"]) != 16 or facts["mapped_variable"] != expected_variable
            or not facts["maps_to_existing_variable"]):
        fail("native ScriptDataElement.io_mapping readback mismatch: " + repr(facts))
    if len(child_variables) != 16 or any(value for value in child_variables):
        fail("native child bit mappings are missing or conflict with parent WORD: " + repr(child_variables))


def native_word_mapping_readback(terminal, parameter_name, expected_id, expected_channel, expected_type, expected_variable):
    matches = []
    for connector in terminal.connectors:
        for parameter in connector.host_parameters:
            if parameter.name == parameter_name:
                matches.append(parameter)
    if len(matches) != 1:
        fail("expected one native host WORD parameter " + parameter_name + "; got " + str(len(matches)))
    parameter = matches[0]
    mapping = parameter.io_mapping
    variable = mapping.variable
    facts = {
        "parameter": parameter.name,
        "id": int(parameter.id),
        "channel_type": str(parameter.channel_type),
        "param_type": str(parameter.param_type),
        "has_sub_elements": bool(parameter.has_sub_elements),
        "subelement_count": len(parameter),
        "mapped_variable": variable,
        "maps_to_existing_variable": bool(mapping.maps_to_existing_variable),
    }
    child_variables = [child.io_mapping.variable for child in parameter]
    verify_native_parameter_facts(facts, expected_id, expected_channel, expected_type,
                                  expected_variable, child_variables)
    facts["child_subelements"] = 16
    facts["child_variable_mappings"] = child_variables
    return facts


def run():
    system.script_prompt_handling = (ScriptPromptHandling.ForwardUnknownPrompts
                                     | ScriptPromptHandling.LogPrompts)
    existing = [path for path in OUTPUT_FILES if os.path.exists(path)]
    if existing:
        fail("output already exists; preserve it and choose a fresh private build directory: " + ", ".join(existing))
    digest = hashlib.sha256(SOURCE_ST.encode("utf-8")).hexdigest()
    if digest != SOURCE_SHA256:
        fail("embedded IEC source hash mismatch: " + digest)
    assert projects.primary is None, "Existing project unexpectedly loaded"

    project = projects.create(OUTPUT_PATH, primary=True)
    if project is None:
        fail("projects.create() returned no project")
    project.add("ReferenceController", CONTROLLER[0], CONTROLLER[1], CONTROLLER[2])
    controllers = [obj for obj in devices_under(project) if device_id(obj) == CONTROLLER]
    if len(controllers) != 1:
        fail("controller project-tree readback mismatch: " + str(len(controllers)))
    controller = controllers[0]
    buses = [obj for obj in devices_under(controller) if device_id(obj) == LOCALBUS]
    if len(buses) != 1:
        fail("expected exactly one pinned LocalBus: " + str(len(buses)))
    local_bus = buses[0]

    for index, (name, ident, version) in enumerate(TERMINALS):
        allowed = local_bus.allowed_interfaces_at(index)
        if not allowed or BUS_INTERFACE not in allowed:
            fail("LocalBus rejects Wago.Kbus at insertion index " + str(index))
        local_bus.insert(name, index, TERMINAL_TYPE, ident, version)
    actual_order = [device_id(obj) for obj in local_bus.get_children(False)
                    if getattr(obj, "is_device", False) and device_id(obj)[0] == TERMINAL_TYPE]
    expected_order = [(TERMINAL_TYPE, ident, version) for _, ident, version in TERMINALS]
    if actual_order != expected_order:
        fail("terminal order mismatch: " + repr(actual_order))
    terminal_objects = [obj for obj in devices_under(local_bus)
                        if device_id(obj)[0] == TERMINAL_TYPE]
    if [device_id(obj) for obj in terminal_objects] != expected_order:
        fail("active terminal device lookup/order mismatch")
    for obj in [local_bus] + terminal_objects:
        obj.enable()
        if not obj.is_enabled():
            fail("native device remains disabled after enable(): " + repr(device_id(obj)))

    apps = [obj for obj in project.get_children(True) if getattr(obj, "is_application", False)]
    if len(apps) != 1:
        fail("expected one auto-created Application: " + str(len(apps)))
    app = apps[0]
    project.active_application = app
    app_name = app.get_name()
    if app_name != "Application":
        fail("unexpected application name; refusing to guess mapping qualification: " + app_name)
    input_variable = app_name + ".PLC_PRG.InputWord"
    output_variable = app_name + ".PLC_PRG.OutputWord"
    split = SOURCE_ST.index("END_VAR") + len("END_VAR")
    declaration, implementation = SOURCE_ST[:split], SOURCE_ST[split:].lstrip("\r\n")
    matches = app.find_ignore_transient_objects("PLC_PRG", True)
    if len(matches) > 1:
        fail("multiple PLC_PRG objects found")
    pou = matches[0] if matches else app.create_program("PLC_PRG", ImplementationLanguages.st)
    if not getattr(pou, "has_textual_declaration", False) or not getattr(pou, "has_textual_implementation", False):
        fail("PLC_PRG lacks textual declaration or implementation")
    pou.textual_declaration.replace(new_text=declaration)
    pou.textual_implementation.replace(new_text=implementation)
    if pou.textual_declaration.text != declaration or pou.textual_implementation.text != implementation:
        fail("PLC_PRG source readback mismatch")

    task_configs = [obj for obj in app.get_children(True) if getattr(obj, "is_task_configuration", False)]
    if len(task_configs) > 1:
        fail("multiple task configurations found")
    task_config = task_configs[0] if task_configs else app.create_task_configuration()
    tasks = [obj for obj in task_config.get_children(False) if getattr(obj, "is_task", False)]
    if len(tasks) > 1:
        fail("multiple tasks found; refusing to select schedule")
    task = tasks[0] if tasks else task_config.create_task("MainTask")
    task.kind_of_task, task.interval, task.interval_unit = KindOfTask.Cyclic, "20", "ms"
    while len(task.pous):
        task.pous.remove(len(task.pous) - 1)
    task.pous.add("PLC_PRG")
    if task.kind_of_task != KindOfTask.Cyclic or task.interval != "20" or task.interval_unit != "ms" or len(task.pous) != 1:
        fail("task configuration readback mismatch")

    # The generated mapping export supplies the descriptor-bound parameter and
    # current addresses. Only its first column is edited for parent WORDs.
    controller.export_io_mappings_as_csv(CSV_PATH)
    requested_mappings = map_parent_words_in_csv(CSV_PATH, input_variable, output_variable)
    controller.import_io_mappings_from_csv(CSV_PATH)
    project.save()
    controller.export_io_mappings_as_csv(CSV_PATH)
    mapping_result = verify_export(CSV_PATH, input_variable, output_variable)
    native_mappings = [
        native_word_mapping_readback(terminal_objects[0], "_IN", 0x01000000,
                                     "Input", "local:InputField", input_variable),
        native_word_mapping_readback(terminal_objects[1], "_OUT", 0x03000000,
                                     "Output", "local:OutputField", output_variable),
    ]

    before = diagnostic_counts()
    require_clean("pre-build", before)
    app.rebuild()
    rebuilt = diagnostic_counts()
    project.save()
    require_clean("rebuild", rebuilt)
    app.generate_code()
    generated = diagnostic_counts()
    project.save()
    require_clean("code generation", generated)
    app.create_boot_application(APP_PATH, True, False)
    final = diagnostic_counts()
    require_clean("offline boot image", final)
    controller.export_io_mappings_as_csv(CSV_PATH)
    project.save()
    mapping_result = verify_export(CSV_PATH, input_variable, output_variable)

    print("VIRTUALWAGO_RESULT:" + json.dumps({
        "scope": "Own native mapped offline project and boot image; no online or hardware operation",
        "status": "PASS", "source_sha256": digest, "controller": CONTROLLER,
        "terminal_order": actual_order,
        "diagnostics": {"prebuild": before, "rebuild": rebuilt, "codegen": generated, "final": final},
        "task_interval_ms": 20, "output_permit_initial": False,
        "requested_parent_mappings": requested_mappings, "mapping": mapping_result,
        "native_word_mappings": native_mappings,
        "enabled_nodes": [repr(device_id(obj)) for obj in [local_bus] + terminal_objects],
    }))
    print("MAPPED_OFFLINE_BUILD_NO_ERRORS_OR_WARNINGS: " + OUTPUT_PATH)
    print("IEC source SHA-256: " + digest)
    print("No target connection or runtime operation was performed.")


if __name__ == "__main__":
    run()
    projects.primary.close()
