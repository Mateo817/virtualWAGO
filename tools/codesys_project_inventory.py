from __future__ import print_function

"""Read-only CODESYS project inventory for a private project artifact.

Run this file only inside the installed CODESYS ScriptEngine. The project and
report paths are supplied through environment variables and must all stay below
the local, private ``VIRTUALWAGO_PRIVATE_ROOT``. The script never saves, builds,
logs in, scans, downloads, starts, or stops an application.

Linux OverlayFS needs ``VIRTUALWAGO_ALLOW_OVERLAY=1`` only after its backing
storage has been independently bound as local. Windows ACL checks use .NET and
fail closed when they are unavailable.
"""

from scriptengine import *
import hashlib
import errno
import json
import ntpath
import os
import re
import stat
import sys


PROJECT_PATH = os.environ.get("VIRTUALWAGO_PROJECT_PATH")
OUTPUT_PATH = os.environ.get("VIRTUALWAGO_INVENTORY_OUTPUT")
MAPPING_PATH = os.environ.get("VIRTUALWAGO_MAPPING_OUTPUT")
ERROR_PATH = os.environ.get("VIRTUALWAGO_INVENTORY_ERROR_OUTPUT")
COLLECT_LIBRARIES = os.environ.get("VIRTUALWAGO_COLLECT_LIBRARIES") == "1"
PRIVATE_ROOT = os.environ.get("VIRTUALWAGO_PRIVATE_ROOT")
ALLOW_OVERLAY = os.environ.get("VIRTUALWAGO_ALLOW_OVERLAY") == "1"
ERROR_OUTPUT_VALIDATED = False
LOCAL_POSIX_FILESYSTEMS = frozenset((
    "bcachefs", "btrfs", "ecryptfs", "erofs", "ext2", "ext3", "ext4",
    "f2fs", "fuseblk", "jfs", "overlay", "ramfs", "reiserfs", "squashfs",
    "tmpfs", "ubifs", "xfs", "zfs"))


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


def decode_mount_field(value):
    return (value.replace("\\040", " ").replace("\\011", "\t")
            .replace("\\012", "\n").replace("\\134", "\\"))


def linux_mount_type(path, mountinfo_path="/proc/self/mountinfo"):
    matches = []
    with open(mountinfo_path, "r") as stream:
        for raw in stream:
            left, separator, right = raw.partition(" - ")
            if not separator:
                continue
            fields = left.split()
            trailing = right.split()
            if len(fields) < 5 or not trailing:
                continue
            mountpoint = decode_mount_field(fields[4])
            if path == mountpoint or path.startswith(mountpoint.rstrip(os.sep) + os.sep):
                matches.append((mountpoint, trailing[0]))
    require(matches, "cannot bind path to a mounted filesystem")
    seen_mountpoints = set()
    for mountpoint, _filesystem in matches:
        require(mountpoint not in seen_mountpoints,
                "ambiguous stacked mountpoint")
        seen_mountpoints.add(mountpoint)
    deepest_length = max(len(match[0]) for match in matches)
    deepest = [match for match in matches if len(match[0]) == deepest_length]
    return deepest[0][1]


def require_local_posix_filesystem(path, label):
    require(sys.platform.startswith("linux"),
            "cannot verify local filesystem type for " + label)
    try:
        filesystem = linux_mount_type(path)
    except Exception as error:
        fail("cannot verify local filesystem type for " + label + ": " + str(type(error)))
    require(filesystem != "overlay" or ALLOW_OVERLAY,
            label + " uses overlay; set VIRTUALWAGO_ALLOW_OVERLAY=1 only after "
            "binding its backing storage as local")
    require(filesystem in LOCAL_POSIX_FILESYSTEMS,
            label + " must use a verified local filesystem, not " + filesystem)


def require_no_link_components(path, label):
    absolute = os.path.abspath(path)
    drive, tail = os.path.splitdrive(absolute)
    current = drive + os.sep if drive else os.sep
    for part in tail.strip(os.sep).split(os.sep):
        if not part:
            continue
        current = os.path.join(current, part)
        if os.name == "posix":
            require_local_posix_filesystem(current, label)
        try:
            metadata = os.lstat(current)
        except OSError as error:
            if error.errno == errno.ENOENT:
                break
            raise
        reparse_flag = getattr(stat, "FILE_ATTRIBUTE_REPARSE_POINT", 0x400)
        file_attributes = getattr(metadata, "st_file_attributes", None)
        require(os.name != "nt" or file_attributes is not None,
                "cannot verify Windows reparse-point state for " + label)
        require(not stat.S_ISLNK(metadata.st_mode)
                and not (file_attributes is not None
                         and file_attributes & reparse_flag),
                label + " must not traverse a symlink or reparse point")


def require_windows_private_acl(path, is_directory=True):
    try:
        from System.IO import Directory, File
        from System.Security.AccessControl import AccessControlType, FileSystemRights
        from System.Security.Principal import SecurityIdentifier, WindowsIdentity
        current = str(WindowsIdentity.GetCurrent().User.Value)
        allowed = frozenset((current, "S-1-5-18", "S-1-5-32-544", "S-1-3-0"))
        security = (Directory.GetAccessControl(path) if is_directory
                    else File.GetAccessControl(path))
        owner = str(security.GetOwner(SecurityIdentifier).Value)
        require(owner in allowed, "private root owner is not the current user/system/admin")
        sensitive = int(FileSystemRights.ReadData | FileSystemRights.WriteData
                        | FileSystemRights.ReadAttributes
                        | FileSystemRights.ReadExtendedAttributes
                        | FileSystemRights.ChangePermissions
                        | FileSystemRights.TakeOwnership
                        | FileSystemRights.FullControl)
        rules = security.GetAccessRules(True, True, SecurityIdentifier)
        for rule in rules:
            if (rule.AccessControlType == AccessControlType.Allow
                    and int(rule.FileSystemRights) & sensitive
                    and str(rule.IdentityReference.Value) not in allowed):
                fail("private path grants file access to an additional Windows principal")
    except Exception as error:
        if str(error).startswith("CODESYS PROJECT INVENTORY stopped:"):
            raise
        fail("cannot verify private Windows ACL: " + str(type(error)))


def require_private_permissions(root, path, label):
    relative = os.path.relpath(path, root)
    parts = [] if relative == os.curdir else relative.split(os.sep)
    current = root
    candidates = [(root, True)]
    for part in parts[:-1]:
        current = os.path.join(current, part)
        if not os.path.exists(current):
            break
        candidates.append((current, True))
    if os.path.exists(path):
        candidates.append((path, os.path.isdir(path)))
    seen = set()
    for candidate, is_directory in candidates:
        normalized = canonical_path(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        if os.name == "posix":
            mode = stat.S_IMODE(os.stat(candidate).st_mode)
            require(mode & 0o077 == 0,
                    label + " path must not grant group/other permissions")
        elif os.name == "nt":
            require_windows_private_acl(candidate, is_directory)


def require_local_path(path, label):
    require(path, label + " is required")
    normalized = str(path).replace("/", "\\")
    require(not normalized.startswith("\\\\"),
            label + " must be a local path, not a UNC/device path")
    raw_tail = ntpath.splitdrive(str(path))[1] if os.name == "nt" else str(path)
    separators = r"[\\/]" if os.name == "nt" else "/"
    require(".." not in re.split(separators, raw_tail),
            label + " must not contain a parent-directory component")
    if os.name == "nt":
        drive, tail = ntpath.splitdrive(str(path))
        require(drive and tail.startswith(("\\", "/")),
                label + " must use an absolute local drive path")
        try:
            import ctypes
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive + "\\")
        except Exception:
            try:
                from System.IO import DriveInfo, DriveType
                drive_type = int(DriveInfo(drive + "\\").DriveType)
                remote_type = int(DriveType.Network)
            except Exception:
                fail("cannot verify that " + label + " is on a local Windows drive")
        else:
            remote_type = 4
        require(drive_type != remote_type,
                label + " must not use a mapped network drive")
    candidate = canonical_path(path)
    if os.name == "posix":
        require_local_posix_filesystem(candidate, label)
    require_no_link_components(candidate, label)
    return candidate


def require_within_private_root(path, root, label):
    candidate = require_local_path(path, label)
    relative = os.path.relpath(candidate, root)
    require(relative != os.pardir and not relative.startswith(os.pardir + os.sep),
            label + " must stay inside VIRTUALWAGO_PRIVATE_ROOT")
    return candidate


def validate_private_paths(project_path, output_path, mapping_path, error_path,
                           private_root):
    root = require_local_path(private_root, "VIRTUALWAGO_PRIVATE_ROOT")
    require(os.path.isdir(root), "VIRTUALWAGO_PRIVATE_ROOT must be an existing directory")
    for path, label in ((project_path, "project path"),
                        (output_path, "inventory output"),
                        (mapping_path, "mapping output"),
                        (error_path, "error output")):
        if path:
            candidate = require_within_private_root(path, root, label)
            require_private_permissions(root, candidate, label)
    return root


def require_distinct_outputs(*paths):
    normalized = [canonical_path(path) for path in paths if path]
    require(len(normalized) == len(set(normalized)),
            "inventory, mapping and error outputs must be distinct paths")


def write_exclusive(path, content):
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
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
    global ERROR_OUTPUT_VALIDATED
    ERROR_OUTPUT_VALIDATED = False
    validate_private_paths(PROJECT_PATH, OUTPUT_PATH, MAPPING_PATH, ERROR_PATH,
                           PRIVATE_ROOT)
    require_distinct_outputs(OUTPUT_PATH, MAPPING_PATH, ERROR_PATH)
    require(PROJECT_PATH and os.path.isfile(PROJECT_PATH),
            "set VIRTUALWAGO_PROJECT_PATH to an existing private project")
    require(OUTPUT_PATH and os.path.isdir(os.path.dirname(OUTPUT_PATH)),
            "set VIRTUALWAGO_INVENTORY_OUTPUT to a path in an existing private directory")
    if MAPPING_PATH:
        require(os.path.isdir(os.path.dirname(MAPPING_PATH)),
                "set VIRTUALWAGO_MAPPING_OUTPUT inside an existing private directory")
    if ERROR_PATH:
        require(os.path.isdir(os.path.dirname(ERROR_PATH)),
                "set VIRTUALWAGO_INVENTORY_ERROR_OUTPUT inside an existing private directory")
    ERROR_OUTPUT_VALIDATED = True
    require(not os.path.exists(OUTPUT_PATH), "refusing to overwrite an existing inventory report")
    if MAPPING_PATH:
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


def write_error_receipt(error):
    if not ERROR_OUTPUT_VALIDATED or not ERROR_PATH or os.path.exists(ERROR_PATH):
        return False
    error_payload = (json.dumps({
        "status": "FAIL",
        "error_type": str(type(error)),
        "message": str(error),
    }, sort_keys=True, indent=2) + "\n").encode("utf-8")
    write_exclusive(ERROR_PATH, error_payload)
    return True


if __name__ == "__main__":
    try:
        run()
    except Exception as error:
        write_error_receipt(error)
        raise
