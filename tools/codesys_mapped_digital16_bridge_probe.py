from __future__ import print_function

"""Build a fresh offline native CODESYS WORD16 bridge probe.

Uses documented project/device-description, CSV mapping, task and build APIs
also present in the established WORD16 builder. No online or runtime calls.
Set VIRTUALWAGO_PRIVATE_BUILD_DIR to a fresh private directory.
"""

from scriptengine import *
import csv
import hashlib
import json
import os
import re


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SOURCE_PATH = os.path.join(REPO_ROOT, "prototype", "iec", "minimal_io_16_bridge_probe.st")
OUTPUT_DIR = os.environ.get("VIRTUALWAGO_PRIVATE_BUILD_DIR")
OUTPUT_PATH = os.path.join(OUTPUT_DIR, "mapped-digital16-bridge-probe.project") if OUTPUT_DIR else None
APP_PATH = os.path.join(OUTPUT_DIR, "mapped-digital16-bridge-probe.app") if OUTPUT_DIR else None
CRC_PATH = os.path.join(OUTPUT_DIR, "mapped-digital16-bridge-probe.crc") if OUTPUT_DIR else None
CSV_PATH = os.path.join(OUTPUT_DIR, "mapped-digital16-bridge-probe-mapping.csv") if OUTPUT_DIR else None
OUTPUT_FILES = (OUTPUT_PATH, APP_PATH, CRC_PATH, CSV_PATH)

CONTROLLER = (4096, "1006 120C", "6.4.6.11")
LOCALBUS = (32778, "Wago 750-Series Local Bus Interface", "2.1.0.1")
BUS_INTERFACE = "Wago.Kbus"
TERMINAL_TYPE = 32776
TERMINALS = [
    ("750-1405", "9001_0750140500000000", "2.0.0.14"),
    ("750-1504", "9002_0750150400000000", "2.0.0.14"),
]
DESCRIPTOR_SHA256 = {
    "750-1405": "2ea6fb96d1db35228450ccd94454f1e51b562a6e1982e416f34eed2feb056273",
    "750-1504": "207e7d654f98a180b06cb75117e282ac2a85f956cbb5d057113d76846a6dc991",
}
SOURCE_SHA256 = "1b954ff156e2b1cedecd77a4e7152ee2ac774ef93da8b5cd65f5dc9c93d2cef6"
OUTPUT_PERMIT_INITIAL = True

# Exact whole-string IEC address syntax; compatible with CODESYS IronPython 2.
IEC_WORD_INPUT = re.compile(r"\A%IW([0-9]+)\Z")
IEC_WORD_OUTPUT = re.compile(r"\A%QW([0-9]+)\Z")
IEC_BIT_INPUT = re.compile(r"\A%IX([0-9]+)\.([0-7])\Z")
IEC_BIT_OUTPUT = re.compile(r"\A%QX([0-9]+)\.([0-7])\Z")


def read_source():
    with open(SOURCE_PATH, "rb") as stream:
        source = stream.read()
    digest = hashlib.sha256(source).hexdigest()
    if digest != SOURCE_SHA256:
        fail("IEC source hash mismatch: " + digest)
    return source.decode("utf-8"), digest



def fail(message):
    raise Exception("MAPPED OFFLINE DIGITAL16 bridge probe stopped: " + message)


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
            # Preserve IEC addresses and mapping identities verbatim; trimming
            # could turn malformed source text into an accepted contract.
            rows.append(row)
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
        if len(row) != 6:
            fail("mapping export row does not match observed six-column schema")
        key = mapping_identity(row)
        if key in indexed:
            fail("duplicate parameter/device row in mapping export: " + repr(key))
        indexed[key] = row

    expected = {
        ("_IN", "_750_1405"): (input_variable, IEC_WORD_INPUT),
        ("_OUT", "_750_1504"): (output_variable, IEC_WORD_OUTPUT),
    }
    parent_words = {}
    for key, (variable, word_address_pattern) in expected.items():
        row = indexed.get(key)
        match = word_address_pattern.match(row[4]) if row is not None else None
        if row is None or row[0] != variable or match is None:
            fail("parent WORD mapping readback mismatch for " + repr(key) + ": " + repr(row))
        parent_words[key] = int(match.group(1), 10)

    channel_specs = (
        ("_IN@", "_750_1405", IEC_BIT_INPUT, ("_IN", "_750_1405")),
        ("_OUT@", "_750_1504", IEC_BIT_OUTPUT, ("_OUT", "_750_1504")),
    )
    counts = {}
    for prefix, device, bit_address_pattern, parent_key in channel_specs:
        found = [row for row in rows if row[1].startswith(prefix)]
        if any(row[5] != device for row in found):
            fail("digital channel parameter is bound to an unexpected device for " + prefix)
        names = set(row[1] for row in found)
        expected_names = set(prefix + str(n) for n in range(1, 17))
        if names != expected_names or len(found) != 16:
            fail("expected exactly 16 exported bit channels for " + device + "; got " + repr(sorted(names)))
        addresses = [row[4] for row in found]
        matches = [bit_address_pattern.match(address) for address in addresses]
        if any(match is None for match in matches):
            fail("digital channel IEC address syntax/direction mismatch for " + device)
        if len(set(addresses)) != 16:
            fail("duplicate bit-channel address in exported " + device + " rows")
        if any(row[0] for row in found):
            fail("unexpected bit child variable mapping conflicts with parent WORD on " + device)
        parent_byte = parent_words[parent_key] * 2
        for row, match in zip(found, matches):
            channel_number = int(row[1][len(prefix):], 10)
            address_byte = int(match.group(1), 10)
            address_bit = int(match.group(2), 10)
            expected_byte = parent_byte + ((channel_number - 1) // 8)
            expected_bit = (channel_number - 1) % 8
            if address_byte != expected_byte or address_bit != expected_bit:
                fail("digital channel address does not match parent WORD/bit ordering for " + row[1])
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
    print("VIRTUALWAGO_TCM_OFFLINE_READBACK:" + json.dumps({
        "id": int(parameter.id), "param_type": str(parameter.param_type),
        "default": default, "before": before, "after": after}))


def run():
    if not OUTPUT_DIR:
        fail("set VIRTUALWAGO_PRIVATE_BUILD_DIR to a fresh private directory")
    if not os.path.isdir(OUTPUT_DIR):
        fail("private build directory does not exist")
    system.script_prompt_handling = (ScriptPromptHandling.ForwardUnknownPrompts
                                     | ScriptPromptHandling.LogPrompts)
    existing = [path for path in OUTPUT_FILES if os.path.exists(path)]
    if existing:
        fail("output already exists; preserve it and choose a fresh private build directory: " + ", ".join(existing))
    source_text, digest = read_source()
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
    select_disabled_tcm(local_bus)

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

    print("VIRTUALWAGO_DIGITAL16_BRIDGE_PROBE_RESULT:" + json.dumps({
        "scope": "Own native mapped offline WORD16 bridge probe project and boot image; no online or runtime operation",
        "status": "PASS", "source_sha256": digest, "controller": CONTROLLER,
        "terminals": [{"article": name, "type": TERMINAL_TYPE, "id": ident, "version": version,
                       "descriptor_sha256": DESCRIPTOR_SHA256[name]} for name, ident, version in TERMINALS],
        "terminal_order": actual_order,
        "diagnostics": {"prebuild": before, "rebuild": rebuilt, "codegen": generated, "final": final},
        "task_interval_ms": 20, "tcm_control_parameter_id": 41,
        "tcm_value_readback": 0, "output_permit_initial": OUTPUT_PERMIT_INITIAL,
        "requested_output_transform": "InputWord XOR WORD#16#A596",
        "requested_parent_mappings": requested_mappings, "mapping": mapping_result,
        "native_word_mappings": native_mappings,
        "enabled_nodes": [repr(device_id(obj)) for obj in [local_bus] + terminal_objects],
    }))
    print("MAPPED_OFFLINE_DIGITAL16_BRIDGE_PROBE_NO_ERRORS_OR_WARNINGS: " + OUTPUT_PATH)
    print("IEC source SHA-256: " + digest)
    print("No target connection or runtime operation was performed.")


if __name__ == "__main__":
    run()
    projects.primary.close()
