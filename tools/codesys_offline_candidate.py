from __future__ import print_function
from scriptengine import *
import json
import os
import hashlib


# Offline CODESYS engineering candidate for the pinned 3.5.21.50 profile.
# Creates a new project, adds the pinned WAGO controller and local terminals,
# writes the own IEC source, configures its cyclic task, builds/code-generates,
# creates an offline boot artifact and exports the mapping table. It contains
# no online, gateway, scan, login, download, upload, or runtime operations and
# assigns no process-image variable mappings.
#
# Official API references:
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptProjects.html
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptProject.html
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptDeviceObject.html
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptDeviceParameters.html
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptIecLanguageObjectContainer.html
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptTextualObject.html
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptApplication.html
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptTaskConfigObject.html
# https://content.helpme-codesys.com/en/ScriptingEngine/ScriptSystem.html


OUTPUT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "minimal-io-offline.project")
OUTPUT_FILES = (
    OUTPUT_PATH,
    os.path.join(os.path.dirname(OUTPUT_PATH), "minimal-io.app"),
    os.path.join(os.path.dirname(OUTPUT_PATH), "minimal-io.crc"),
    os.path.join(os.path.dirname(OUTPUT_PATH), "minimal-io-mapping.csv"),
)

CONTROLLER_TYPE = 4096
CONTROLLER_ID = "1006 120C"
CONTROLLER_VERSION = "6.4.6.11"

LOCALBUS_TYPE = 32778
LOCALBUS_ID = "Wago 750-Series Local Bus Interface"
LOCALBUS_VERSION = "2.1.0.1"
LOCALBUS_CHILD_INTERFACE = "Wago.Kbus"

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
    raise Exception("OFFLINE CODESYS candidate stopped: " + message)


def device_id(obj):
    ident = obj.get_device_identification()
    return (ident.type, ident.id, ident.version)


def devices_under(tree_object):
    result = []
    for obj in tree_object.get_children(True):
        if getattr(obj, "is_device", False):
            result.append(obj)
    return result


def diagnostic_counts():
    # Count all diagnostics in the fresh IDE session, across every category.
    counts = {"errors": 0, "warnings": 0}
    for category in system.get_message_categories():
        counts["errors"] += len(system.get_message_objects(category.ToString("B"), Severity.FatalError | Severity.Error))
        counts["warnings"] += len(system.get_message_objects(category.ToString("B"), Severity.Warning))
    return counts


def require_no_errors(stage, counts):
    if counts["errors"] != 0:
        fail(stage + " left IDE-wide fatal/error diagnostics: " + str(counts))


def run_offline_candidate():
    existing_outputs = [path for path in OUTPUT_FILES if os.path.exists(path)]
    if existing_outputs:
        fail("generated output already exists; preserve it and choose a new unique script/output directory: "
             + ", ".join(existing_outputs))
    digest = hashlib.sha256(SOURCE_ST.encode("utf-8")).hexdigest()
    if digest != SOURCE_SHA256:
        fail("embedded IEC source SHA-256 mismatch: " + digest)

    assert projects.primary is None, "Existing project unexpectedly loaded"
    project = projects.create(OUTPUT_PATH, primary=True)
    if project is None:
        fail("projects.create() returned no project")

    project.add("ReferenceController", CONTROLLER_TYPE, CONTROLLER_ID, CONTROLLER_VERSION)
    controllers = [obj for obj in devices_under(project)
                   if device_id(obj) == (CONTROLLER_TYPE, CONTROLLER_ID, CONTROLLER_VERSION)]
    if len(controllers) != 1:
        fail("controller project-tree readback mismatch: " + str(len(controllers)))
    controller = controllers[0]

    buses = [obj for obj in devices_under(controller)
             if device_id(obj) == (LOCALBUS_TYPE, LOCALBUS_ID, LOCALBUS_VERSION)]
    if len(buses) != 1:
        fail("expected the fixed generic LocalBus 2.1.0.1 child; got " + str(len(buses)))
    local_bus = buses[0]

    # insert() accepts the target position; verify the interface at each slot
    # and verify the resulting order after insertion.
    for index, (terminal_name, terminal_id, terminal_version) in enumerate(TERMINALS):
        allowed = local_bus.allowed_interfaces_at(index)
        if not allowed or LOCALBUS_CHILD_INTERFACE not in allowed:
            fail("LocalBus does not accept Wago.Kbus at insertion index " + str(index))
        local_bus.insert(terminal_name, index, TERMINAL_TYPE, terminal_id, terminal_version)

    terminal_order = []
    for obj in local_bus.get_children(False):
        if getattr(obj, "is_device", False):
            ident = device_id(obj)
            if ident[0] == TERMINAL_TYPE:
                terminal_order.append(ident)
    expected_order = [(TERMINAL_TYPE, row[1], row[2]) for row in TERMINALS]
    if terminal_order != expected_order:
        fail("LocalBus terminal order/readback mismatch: " + str(terminal_order))

    applications = [obj for obj in project.get_children(True)
                     if getattr(obj, "is_application", False)]
    if len(applications) != 1:
        fail("expected exactly one auto-created Application; got " + str(len(applications)))
    app = applications[0]
    project.active_application = app

    # CODESYS stores the declaration and implementation separately.
    declaration_end = SOURCE_ST.index("END_VAR") + len("END_VAR")
    declaration = SOURCE_ST[:declaration_end]
    implementation = SOURCE_ST[declaration_end:].lstrip("\r\n")
    pou_matches = app.find_ignore_transient_objects("PLC_PRG", True)
    if len(pou_matches) > 1:
        fail("application contains multiple PLC_PRG objects")
    pou = pou_matches[0] if pou_matches else app.create_program("PLC_PRG", ImplementationLanguages.st)
    if not getattr(pou, "has_textual_declaration", False) or not getattr(pou, "has_textual_implementation", False):
        fail("PLC_PRG does not expose textual IEC declaration and implementation")
    pou.textual_declaration.replace(new_text=declaration)
    pou.textual_implementation.replace(new_text=implementation)
    if pou.textual_declaration.text != declaration or pou.textual_implementation.text != implementation:
        fail("PLC_PRG source readback mismatch")

    task_configs = [obj for obj in app.get_children(True)
                    if getattr(obj, "is_task_configuration", False)]
    if len(task_configs) > 1:
        fail("application has multiple task configurations")
    task_config = task_configs[0] if task_configs else app.create_task_configuration()
    tasks = [obj for obj in task_config.get_children(False) if getattr(obj, "is_task", False)]
    if len(tasks) > 1:
        fail("task configuration has multiple tasks; refusing to choose a schedule")
    task = tasks[0] if tasks else task_config.create_task("MainTask")
    task.kind_of_task = KindOfTask.Cyclic
    task.interval = "20"
    task.interval_unit = "ms"
    while len(task.pous) > 0:
        task.pous.remove(len(task.pous) - 1)
    task.pous.add("PLC_PRG")
    if (task.kind_of_task != KindOfTask.Cyclic or task.interval != "20"
            or task.interval_unit != "ms" or len(task.pous) != 1):
        fail("task configuration readback mismatch")

    project.save()
    baseline = diagnostic_counts()
    require_no_errors("pre-build", baseline)
    app.rebuild()
    after_rebuild = diagnostic_counts()
    project.save()
    require_no_errors("rebuild", after_rebuild)
    app.generate_code()
    after_codegen = diagnostic_counts()
    project.save()
    require_no_errors("generate_code", after_codegen)

    app.create_boot_application(os.path.join(os.path.dirname(OUTPUT_PATH), "minimal-io.app"), True, False)
    final_counts = diagnostic_counts()
    require_no_errors("offline boot image", final_counts)
    controller.export_io_mappings_as_csv(os.path.join(os.path.dirname(OUTPUT_PATH), "minimal-io-mapping.csv"))
    project.save()
    print("VIRTUALWAGO_RESULT:" + json.dumps({"scope":"Own native offline project and ARM boot image; no online or hardware operation", "status":"PASS", "source_sha256":digest, "controller":[CONTROLLER_TYPE,CONTROLLER_ID,CONTROLLER_VERSION], "terminal_order":terminal_order, "diagnostics":final_counts, "task_interval_ms":20, "mapping_assignment":"NONE", "initial_output_permit":False}))
    print("OFFLINE_BUILD_NO_ERRORS: " + OUTPUT_PATH)
    print("CODESYS engineering profile: 3.5.21.50 (SP21 Patch 5)")
    print("Pinned controller: type 4096 / 1006 120C / 6.4.6.11")
    print("Fixed LocalBus: type 32778 / Wago 750-Series Local Bus Interface / 2.1.0.1")
    print("Terminals, verified order: 750-1405 then 750-1504; each 2.0.0.14")
    print("PLC_PRG source SHA-256: " + digest)
    print("IDE-wide diagnostics before/rebuild/codegen: " + str(baseline) + " / "
          + str(after_rebuild) + " / " + str(after_codegen))
    print("No process-image variable mapping was assigned; an offline boot image was created. No runtime operation was performed.")


run_offline_candidate()
projects.primary.close()
