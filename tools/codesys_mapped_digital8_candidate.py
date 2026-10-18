from __future__ import print_function

"""Build an offline native candidate for the captured 750-430/750-530 pair.

This script uses only offline CODESYS project/device-description APIs. It does
not connect to a gateway, scan, login, download, upload, or start a runtime.
Set VIRTUALWAGO_PRIVATE_BUILD_DIR to a fresh private directory before running;
all generated project, mapping, and boot-image artifacts stay there.
"""

from scriptengine import *
import csv
import hashlib
import json
import os
import re


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_PATH = os.path.join(REPO_ROOT, "prototype", "iec", "minimal_io_8.st")
OUTPUT_DIR = os.environ.get("VIRTUALWAGO_PRIVATE_BUILD_DIR")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "mapped-digital8-offline.project") if OUTPUT_DIR else None
APP_PATH = os.path.join(OUTPUT_DIR, "mapped-digital8.app") if OUTPUT_DIR else None
CRC_PATH = os.path.join(OUTPUT_DIR, "mapped-digital8.crc") if OUTPUT_DIR else None
CSV_PATH = os.path.join(OUTPUT_DIR, "mapped-digital8-mapping.csv") if OUTPUT_DIR else None
OUTPUT_FILES = (OUTPUT_PATH, APP_PATH, CRC_PATH, CSV_PATH)

CONTROLLER = (4096, "1006 120C", "6.4.6.11")
LOCALBUS = (32778, "Wago 750-Series Local Bus Interface", "2.1.0.1")
BUS_INTERFACE = "Wago.Kbus"
TERMINAL_TYPE = 32776
TERMINALS = [
    ("750-430", "8801_0750043000000000", "2.0.0.14"),
    ("750-530", "8802_0750053000000000", "2.0.0.15"),
]
DESCRIPTOR_SHA256 = {
    "750-430": "26d302678905d2e8f4c7e34880cf830c4ad56361ebd647e6ed82a9e02c81dd91",
    "750-530": "84b4043d448c44155a36916a1b65a39f20ba0560459d3c0ffac53fba351daa5d",
}
AUDIT_SHA256 = "1bc897fb198e4720c00390ee62db5d382f7a132604d67efc587c158c4f7df000"
OUTPUT_PERMIT_INITIAL = False
SOURCE_SHA256 = "8004d8ef15ec5fea33ef096896c82f102e58f8a6326ff1846a5327fa09052fa8"

# Exact whole-string IEC address syntax; supported by CODESYS IronPython 2.
IEC_BYTE_INPUT = re.compile(r"\A%IB([0-9]+)\Z")
IEC_BYTE_OUTPUT = re.compile(r"\A%QB([0-9]+)\Z")
IEC_BIT_INPUT = re.compile(r"\A%IX([0-9]+)\.([0-7])\Z")
IEC_BIT_OUTPUT = re.compile(r"\A%QX([0-9]+)\.([0-7])\Z")


def fail(message):
    raise Exception("MAPPED OFFLINE DIGITAL8 candidate stopped: " + message)


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


def read_source():
    with open(SOURCE_PATH, "rb") as stream:
        source = stream.read()
    digest = hashlib.sha256(source).hexdigest()
    if digest != SOURCE_SHA256:
        fail("IEC source hash mismatch: " + digest)
    return source.decode("utf-8"), digest


def read_mapping(path):
    rows = []
    with open(path, "r") as stream:
        for row in csv.reader(stream, delimiter=";"):
            if not row or row[0].startswith("//"):
                continue
            if len(row) != 6:
                fail("mapping CSV row does not match observed six-column export schema")
            # Preserve fields verbatim: trimming IEC addresses or parameter
            # names would turn malformed export text into a passing contract.
            rows.append(row)
    return rows


def mapping_identity(row):
    # Mapped variable; parameter name; unit; description; IEC address; device.
    return row[1], row[5]


def map_parent_bytes_in_csv(path, input_variable, output_variable):
    rows = read_mapping(path)
    with open(path, "r") as stream:
        comment_lines = [line.rstrip("\r\n") for line in stream if line.startswith("//")]
    targets = {
        ("_IN", "_750_430"): input_variable,
        ("_OUT", "_750_530"): output_variable,
    }
    seen = set()
    for row in rows:
        key = mapping_identity(row)
        if key in targets:
            if key in seen:
                fail("duplicate parent BYTE channel in generated mapping CSV: " + repr(key))
            # Preserve every descriptor-generated IEC address verbatim.
            row[0] = targets[key]
            seen.add(key)
    if seen != set(targets.keys()):
        fail("mapping export is missing an expected parent BYTE channel: " + repr(set(targets.keys()) - seen))
    with open(path, "w") as stream:
        for line in comment_lines:
            stream.write(line + "\r\n")
        writer = csv.writer(stream, delimiter=";", lineterminator="\r\n")
        for row in rows:
            writer.writerow(row)
    return {"_IN@_750_430": input_variable, "_OUT@_750_530": output_variable}


def verify_export_rows(rows, input_variable, output_variable):
    indexed = {}
    for row in rows:
        if len(row) != 6:
            fail("mapping export row does not match observed six-column schema")
        key = mapping_identity(row)
        if key in indexed:
            fail("duplicate parameter/device row in mapping export: " + repr(key))
        indexed[key] = row

    expected = {
        ("_IN", "_750_430"): (input_variable, IEC_BYTE_INPUT),
        ("_OUT", "_750_530"): (output_variable, IEC_BYTE_OUTPUT),
    }
    parent_bytes = {}
    for key, (variable, byte_address_pattern) in expected.items():
        row = indexed.get(key)
        match = byte_address_pattern.match(row[4]) if row is not None else None
        if row is None or row[0] != variable or match is None:
            fail("parent BYTE mapping readback mismatch for " + repr(key) + ": " + repr(row))
        parent_bytes[key] = int(match.group(1), 10)

    channel_specs = (
        ("_IN@", "_750_430", IEC_BIT_INPUT, ("_IN", "_750_430")),
        ("_OUT@", "_750_530", IEC_BIT_OUTPUT, ("_OUT", "_750_530")),
    )
    counts = {}
    for prefix, device, bit_address_pattern, parent_key in channel_specs:
        found = [row for row in rows if row[1].startswith(prefix)]
        if any(row[5] != device for row in found):
            fail("digital channel parameter is bound to an unexpected device for " + prefix)
        names = set(row[1] for row in found)
        expected_names = set(prefix + str(n) for n in range(1, 9))
        if names != expected_names or len(found) != 8:
            fail("expected exactly 8 exported bit channels for " + device + "; got " + repr(sorted(names)))
        addresses = [row[4] for row in found]
        matches = [bit_address_pattern.match(address) for address in addresses]
        if any(match is None for match in matches):
            fail("digital channel IEC address syntax/direction mismatch for " + device)
        if len(set(addresses)) != 8:
            fail("missing or duplicate descriptor-exported bit-channel address for " + device)
        if any(row[0] for row in found):
            fail("unexpected bit child variable mapping conflicts with parent BYTE on " + device)
        parent_byte = parent_bytes[parent_key]
        for row, match in zip(found, matches):
            channel_number = int(row[1][len(prefix):], 10)
            address_byte = int(match.group(1), 10)
            address_bit = int(match.group(2), 10)
            if address_byte != parent_byte or address_bit != channel_number - 1:
                fail("digital channel address does not match parent BYTE/bit ordering for " + row[1])
        counts[device] = 8
    return {"parent_bytes": 2, "digital_inputs": counts["_750_430"],
            "digital_outputs": counts["_750_530"], "csv_consistency": "PASS"}


def verify_export(path, input_variable, output_variable):
    return verify_export_rows(read_mapping(path), input_variable, output_variable)


def verify_native_parameter_facts(facts, expected_id, expected_channel, expected_type,
                                  expected_variable, child_variables):
    if (int(facts["id"]) != expected_id or facts["channel_type"].lower() != expected_channel.lower()
            or facts["param_type"] != expected_type or not facts["has_sub_elements"]
            or int(facts["subelement_count"]) != 8 or facts["mapped_variable"] != expected_variable
            or not facts["maps_to_existing_variable"]):
        fail("native ScriptDataElement.io_mapping readback mismatch: " + repr(facts))
    if len(child_variables) != 8 or any(value for value in child_variables):
        fail("native child bit mappings are missing or conflict with parent BYTE: " + repr(child_variables))


def native_byte_mapping_readback(terminal, parameter_name, expected_id, expected_channel,
                                 expected_type, expected_variable):
    matches = []
    for connector in terminal.connectors:
        for parameter in connector.host_parameters:
            if parameter.name == parameter_name:
                matches.append(parameter)
    if len(matches) != 1:
        fail("expected one native host BYTE parameter " + parameter_name + "; got " + str(len(matches)))
    parameter = matches[0]
    mapping = parameter.io_mapping
    facts = {
        "parameter": parameter.name,
        "id": int(parameter.id),
        "channel_type": str(parameter.channel_type),
        "param_type": str(parameter.param_type),
        "has_sub_elements": bool(parameter.has_sub_elements),
        "subelement_count": len(parameter),
        "mapped_variable": mapping.variable,
        "maps_to_existing_variable": bool(mapping.maps_to_existing_variable),
    }
    child_variables = [child.io_mapping.variable for child in parameter]
    verify_native_parameter_facts(facts, expected_id, expected_channel, expected_type,
                                  expected_variable, child_variables)
    facts["child_subelements"] = 8
    facts["child_variable_mappings"] = child_variables
    return facts


def select_disabled_tcm(local_bus):
    matches = []
    for connector in local_bus.connectors:
        for parameter in connector.host_parameters:
            if int(parameter.id) == 41:
                matches.append(parameter)
    if len(matches) != 1:
        fail("TCM parameter41 needs unique original connector binding: " + str(len(matches)))
    parameter = matches[0]
    before = str(parameter.value)
    default = str(parameter.default_value)
    parameter.value = "0"
    after = str(parameter.value)
    if int(after, 0) != 0:
        fail("TCM disabled value readback mismatch: " + after)
    print("VIRTUALWAGO_TCM_OFFLINE_READBACK:" + json.dumps({"id": int(parameter.id), "param_type": str(parameter.param_type), "default": default, "before": before, "after": after}))


def run():
    if not OUTPUT_DIR:
        fail("set VIRTUALWAGO_PRIVATE_BUILD_DIR to a fresh private directory")
    if not os.path.isdir(OUTPUT_DIR):
        fail("private build directory does not exist: " + OUTPUT_DIR)
    existing = [path for path in OUTPUT_FILES if os.path.exists(path)]
    if existing:
        fail("output already exists; preserve it and choose a fresh private build directory: " + ", ".join(existing))
    source_text, source_digest = read_source()
    assert projects.primary is None, "Existing project unexpectedly loaded"
    system.script_prompt_handling = (ScriptPromptHandling.ForwardUnknownPrompts
                                     | ScriptPromptHandling.LogPrompts)

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
    select_disabled_tcm(local_bus)

    for index, (name, ident, version) in enumerate(TERMINALS):
        allowed = local_bus.allowed_interfaces_at(index)
        if not allowed or BUS_INTERFACE not in allowed:
            fail("LocalBus rejects Wago.Kbus at insertion index " + str(index))
        local_bus.insert(name, index, TERMINAL_TYPE, ident, version)
    expected_order = [(TERMINAL_TYPE, ident, version) for _, ident, version in TERMINALS]
    actual_order = [device_id(obj) for obj in local_bus.get_children(False)
                    if getattr(obj, "is_device", False) and device_id(obj)[0] == TERMINAL_TYPE]
    if actual_order != expected_order:
        fail("terminal order mismatch: " + repr(actual_order))
    terminal_objects = [obj for obj in devices_under(local_bus) if device_id(obj)[0] == TERMINAL_TYPE]
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
    input_variable = app_name + ".PLC_PRG.InputByte"
    output_variable = app_name + ".PLC_PRG.OutputByte"
    split = source_text.index("END_VAR") + len("END_VAR")
    declaration, implementation = source_text[:split], source_text[split:].lstrip("\r\n")
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

    controller.export_io_mappings_as_csv(CSV_PATH)
    requested_mappings = map_parent_bytes_in_csv(CSV_PATH, input_variable, output_variable)
    controller.import_io_mappings_from_csv(CSV_PATH)
    project.save()
    controller.export_io_mappings_as_csv(CSV_PATH)
    mapping_result = verify_export(CSV_PATH, input_variable, output_variable)
    native_mappings = [
        native_byte_mapping_readback(terminal_objects[0], "_IN", 0x01000000,
                                    "Input", "local:InputField", input_variable),
        native_byte_mapping_readback(terminal_objects[1], "_OUT", 0x03000000,
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
    project.save()
    require_clean("offline boot image", final)
    controller.export_io_mappings_as_csv(CSV_PATH)
    project.save()
    mapping_result = verify_export(CSV_PATH, input_variable, output_variable)

    print("VIRTUALWAGO_DIGITAL8_RESULT:" + json.dumps({
        "scope": "Own native mapped offline project and boot image; no online or hardware operation",
        "status": "PASS", "source_sha256": source_digest, "controller": CONTROLLER,
        "terminals": [{"article": name, "type": TERMINAL_TYPE, "id": ident, "version": version,
                       "descriptor_sha256": DESCRIPTOR_SHA256[name]} for name, ident, version in TERMINALS],
        "descriptor_audit_sha256": AUDIT_SHA256,
        "terminal_order": actual_order,
        "diagnostics": {"prebuild": before, "rebuild": rebuilt, "codegen": generated, "final": final},
        "task_interval_ms": 20, "output_permit_initial": OUTPUT_PERMIT_INITIAL,
        "requested_parent_mappings": requested_mappings, "mapping": mapping_result,
        "native_byte_mappings": native_mappings,
        "report_counts": {"parent_bytes": 2, "digital_inputs": 8, "digital_outputs": 8},
        "enabled_nodes": [repr(device_id(obj)) for obj in [local_bus] + terminal_objects],
    }))
    print("MAPPED_OFFLINE_DIGITAL8_BUILD_NO_ERRORS_OR_WARNINGS: " + OUTPUT_PATH)
    print("IEC source SHA-256: " + source_digest)
    print("No target connection or runtime operation was performed.")


if __name__ == "__main__":
    run()
    projects.primary.close()
