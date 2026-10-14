from __future__ import print_function

"""Read-only CODESYS project inventory for a private project artifact.

Run this file only inside the installed CODESYS ScriptEngine. The project and
report paths are supplied through environment variables. The script never
saves, builds, logs in, scans, downloads, starts, or stops an application.
"""

from scriptengine import *
import hashlib
import json
import os


PROJECT_PATH = os.environ.get("VIRTUALWAGO_PROJECT_PATH")
OUTPUT_PATH = os.environ.get("VIRTUALWAGO_INVENTORY_OUTPUT")
MAPPING_PATH = os.environ.get("VIRTUALWAGO_MAPPING_OUTPUT")
ERROR_PATH = os.environ.get("VIRTUALWAGO_INVENTORY_ERROR_OUTPUT")
COLLECT_LIBRARIES = os.environ.get("VIRTUALWAGO_COLLECT_LIBRARIES") == "1"


def fail(message):
    raise Exception("CODESYS PROJECT INVENTORY stopped: " + message)


def require(condition, message):
    if not condition:
        fail(message)


def digest(path):
    value = hashlib.sha256()
    with open(path, "rb") as stream:
        while True:
            block = stream.read(1024 * 1024)
            if not block:
                break
            value.update(block)
    return value.hexdigest()


def canonical_path(path):
    return os.path.normcase(os.path.abspath(path)) if path else None


def require_distinct_outputs(*paths):
    normalized = [canonical_path(path) for path in paths if path]
    require(len(normalized) == len(set(normalized)),
            "inventory, mapping and error outputs must be distinct paths")


def write_exclusive(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL)
    try:
        with os.fdopen(descriptor, "wb") as stream:
            descriptor = None
            stream.write(content)
    finally:
        if descriptor is not None:
            os.close(descriptor)


def object_name(obj):
    try:
        return str(obj.get_name())
    except Exception:
        return str(getattr(obj, "name", "<unnamed>"))


def device_identity(obj):
    ident = obj.get_device_identification()
    return {
        "type": int(ident.type),
        "id": str(ident.id),
        "version": str(ident.version),
    }


def walk_tree(root):
    devices = []
    applications = []

    def visit(parent, path):
        for child in parent.get_children(False):
            name = object_name(child)
            child_path = path + [name]
            if getattr(child, "is_device", False):
                record = {
                    "path": child_path,
                    "name": name,
                    "identity": device_identity(child),
                    "enabled": bool(child.is_enabled()),
                }
                devices.append(record)
            if getattr(child, "is_application", False):
                applications.append({"path": child_path, "name": name})
            visit(child, child_path)

    visit(root, [])
    return devices, applications


def collect_tasks(project):
    result = []
    for obj in project.get_children(True):
        if not getattr(obj, "is_task_configuration", False):
            continue
        for task in obj.get_children(False):
            if not getattr(task, "is_task", False):
                continue
            result.append({
                "name": object_name(task),
                "kind": str(task.kind_of_task),
                "interval": str(task.interval),
                "interval_unit": str(task.interval_unit),
                "priority": str(task.priority),
                "pous": [str(pou) for pou in task.pous],
            })
    return result


def collect_library_managers(project):
    result = []
    candidates = [("<project>", project)]
    candidates.extend((object_name(obj), obj) for obj in project.get_children(True))
    for owner, obj in candidates:
        if not getattr(obj, "has_library_manager", False):
            continue
        manager = obj.get_library_manager()
        references = []
        for reference in manager.references:
            record = {
                "name": str(reference.name),
                "namespace": str(reference.namespace),
                "is_placeholder": bool(reference.is_placeholder),
                "is_managed": bool(reference.is_managed),
                "system_library": bool(reference.system_library),
            }
            if reference.is_placeholder:
                record.update({
                    "placeholder_name": str(reference.placeholder_name),
                    "default_resolution": str(reference.default_resolution),
                    "effective_resolution": str(reference.effective_resolution),
                    "resolution_info": str(reference.resolution_info),
                })
            references.append(record)
        result.append({"owner": owner, "references": references})
    return result


def validate_inventory(payload):
    require(payload.get("scope") == "read-only offline project inventory",
            "unexpected report scope")
    require(payload.get("project_sha256_before") == payload.get("project_sha256_after"),
            "project bytes changed during read-only inventory")
    identities = []
    for record in payload.get("devices", []):
        identity = record.get("identity", {})
        key = (identity.get("type"), identity.get("id"), identity.get("version"))
        require(None not in key and "" not in key, "device identity is incomplete")
        identities.append(key)
    require(len(identities) == len(payload.get("devices", [])),
            "device inventory accounting mismatch")
    mapping = payload.get("mapping_export")
    if mapping is not None:
        require(mapping.get("sha256") and mapping.get("size_bytes", 0) > 0,
                "mapping export evidence is incomplete")
    return payload


def select_controller(devices):
    controllers = [record for record in devices
                   if record.get("identity", {}).get("type") == 4096]
    require(len(controllers) == 1,
            "expected exactly one controller (device type 4096)")
    return controllers[0]


def run():
    require_distinct_outputs(OUTPUT_PATH, MAPPING_PATH, ERROR_PATH)
    require(PROJECT_PATH and os.path.isfile(PROJECT_PATH),
            "set VIRTUALWAGO_PROJECT_PATH to an existing private project")
    require(OUTPUT_PATH and os.path.isdir(os.path.dirname(OUTPUT_PATH)),
            "set VIRTUALWAGO_INVENTORY_OUTPUT to a path in an existing private directory")
    require(not os.path.exists(OUTPUT_PATH), "refusing to overwrite an existing inventory report")
    if MAPPING_PATH:
        require(os.path.isdir(os.path.dirname(MAPPING_PATH)),
                "set VIRTUALWAGO_MAPPING_OUTPUT inside an existing private directory")
        require(not os.path.exists(MAPPING_PATH),
                "refusing to overwrite an existing mapping export")
    require(projects.primary is None, "another project is already loaded")

    system.script_prompt_handling = (ScriptPromptHandling.ForwardUnknownPrompts
                                     | ScriptPromptHandling.LogPrompts)
    project_hash_before = digest(PROJECT_PATH)
    project = None
    try:
        project = projects.open(PROJECT_PATH, primary=True)
        devices, applications = walk_tree(project)
        mapping_export = None
        if MAPPING_PATH:
            controller_record = select_controller(devices)
            controller_matches = [obj for obj in project.get_children(True)
                                  if getattr(obj, "is_device", False)
                                  and device_identity(obj) == controller_record["identity"]]
            require(len(controller_matches) == 1,
                    "controller object is not unique")
            controller_matches[0].export_io_mappings_as_csv(MAPPING_PATH)
            require(os.path.isfile(MAPPING_PATH) and os.path.getsize(MAPPING_PATH) > 0,
                    "CODESYS did not create a non-empty mapping export")
            mapping_export = {
                "sha256": digest(MAPPING_PATH),
                "size_bytes": os.path.getsize(MAPPING_PATH),
            }
        tasks = collect_tasks(project)
        library_managers = collect_library_managers(project) if COLLECT_LIBRARIES else None
        active = None
        if project.active_application is not None:
            active = object_name(project.active_application)
        report = {
            "schema": "virtualwago-codesys-project-inventory/1",
            "scope": "read-only offline project inventory",
            "project_sha256_before": project_hash_before,
            "project_sha256_after": None,
            "devices": devices,
            "applications": applications,
            "active_application": active,
            "tasks": tasks,
            "library_managers": library_managers,
            "mapping_export": mapping_export,
            "operations": {
                "save": "NOT_RUN",
                "build": "NOT_RUN",
                "online": "NOT_RUN",
                "download": "NOT_RUN",
                "start_stop": "NOT_RUN",
                "library_resolution": ("READ_ONLY" if COLLECT_LIBRARIES else "NOT_RUN"),
            },
        }
        project.close()
        project = None
        report["project_sha256_after"] = digest(PROJECT_PATH)
        validate_inventory(report)
        encoded_report = (json.dumps(report, sort_keys=True, indent=2) + "\n").encode("utf-8")
        write_exclusive(OUTPUT_PATH, encoded_report)
        print("VIRTUALWAGO_PROJECT_INVENTORY_RESULT:" + json.dumps({
            "status": "PASS",
            "scope": report["scope"],
            "project_sha256": report["project_sha256_after"],
            "device_count": len(devices),
            "application_count": len(applications),
            "task_count": len(tasks),
            "library_manager_count": (len(library_managers)
                                      if library_managers is not None else None),
            "mapping_sha256": (mapping_export or {}).get("sha256"),
            "report_sha256": digest(OUTPUT_PATH),
        }, sort_keys=True))
    finally:
        if project is not None:
            project.close()


if __name__ == "__main__":
    try:
        run()
    except Exception as error:
        if ERROR_PATH and not os.path.exists(ERROR_PATH):
            error_payload = (json.dumps({
                "status": "FAIL",
                "error_type": str(type(error)),
                "message": str(error),
            }, sort_keys=True, indent=2) + "\n").encode("utf-8")
            write_exclusive(ERROR_PATH, error_payload)
        raise
