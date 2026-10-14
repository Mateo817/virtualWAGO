#!/usr/bin/env python3
"""Summarize byte coverage from a private CODESYS I/O mapping CSV.

The summary keeps device names and address coverage, but deliberately omits
mapped IEC variable names and descriptions. It is an offline parser and never
opens CODESYS or contacts a controller. Input and output must stay below the
explicit local ``--private-root``.

On Linux, OverlayFS is refused unless ``VIRTUALWAGO_ALLOW_OVERLAY=1`` is set
after its backing storage has been independently bound as local. On Windows,
ACL validation requires a .NET-capable Python host and otherwise fails closed.
"""
import argparse
import csv
import errno
import hashlib
import io
import json
import ntpath
import os
from pathlib import Path
import re
import stat
import sys


ADDRESS = re.compile(r"^%([IQ])([XBWDL])(\d+)(?:\.(\d+))?$")
WIDTH_BYTES = {"X": 1, "B": 1, "W": 2, "D": 4, "L": 8}
ALLOW_OVERLAY = os.environ.get("VIRTUALWAGO_ALLOW_OVERLAY") == "1"
LOCAL_POSIX_FILESYSTEMS = frozenset({
    "bcachefs", "btrfs", "ecryptfs", "erofs", "ext2", "ext3", "ext4",
    "f2fs", "fuseblk", "jfs", "overlay", "ramfs", "reiserfs", "squashfs",
    "tmpfs", "ubifs", "xfs", "zfs"})


def fail(message):
    raise ValueError("CODESYS mapping summary stopped: " + message)


def parse_address(value):
    match = ADDRESS.fullmatch(value)
    if not match:
        fail("unsupported IEC address: " + repr(value))
    direction, kind, offset_text, bit_text = match.groups()
    logical_offset = int(offset_text)
    if kind == "X":
        if bit_text is None or not 0 <= int(bit_text) <= 7:
            fail("invalid bit address: " + repr(value))
        byte_start = logical_offset
    elif bit_text is not None:
        fail("non-bit address has a bit suffix: " + repr(value))
    else:
        byte_start = logical_offset * WIDTH_BYTES[kind]
    return {
        "direction": direction,
        "kind": kind,
        "byte_start": byte_start,
        "byte_end": byte_start + WIDTH_BYTES[kind] - 1,
    }


def read_rows_bytes(content):
    rows = []
    text = content.decode("utf-8-sig")
    with io.StringIO(text, newline="") as stream:
        for raw in stream:
            if raw.startswith("//") or not raw.strip():
                continue
            row = next(csv.reader([raw], delimiter=";"))
            if len(row) < 6:
                fail("mapping row has fewer than six columns")
            address = row[4].strip()
            device = row[5].strip()
            if not address:
                continue
            if not device:
                fail("addressed mapping row has no device")
            rows.append({"parameter": row[1].strip(), "address": address,
                         "device": device, "parsed": parse_address(address)})
    if not rows:
        fail("mapping contains no addressed rows")
    return rows


def read_rows(path):
    return read_rows_bytes(Path(path).read_bytes())


def contiguous_ranges(byte_offsets):
    values = sorted(set(byte_offsets))
    if not values:
        return []
    ranges = []
    start = previous = values[0]
    for value in values[1:]:
        if value != previous + 1:
            ranges.append([start, previous])
            start = value
        previous = value
    ranges.append([start, previous])
    return ranges


def summarize(rows):
    coverage = {}
    for row in rows:
        parsed = row["parsed"]
        key = (row["device"], parsed["direction"])
        entry = coverage.setdefault(key, {"bytes": set(), "addresses": set()})
        entry["bytes"].update(range(parsed["byte_start"], parsed["byte_end"] + 1))
        entry["addresses"].add(row["address"])
    devices = []
    for (device, direction), entry in sorted(coverage.items()):
        byte_ranges = contiguous_ranges(entry["bytes"])
        devices.append({
            "device": device,
            "direction": "input" if direction == "I" else "output",
            "byte_ranges_inclusive": byte_ranges,
            "covered_byte_count": len(entry["bytes"]),
            "address_count": len(entry["addresses"]),
        })
    return devices


def decode_mount_field(value):
    return (value.replace("\\040", " ").replace("\\011", "\t")
            .replace("\\012", "\n").replace("\\134", "\\"))


def linux_mount_type(path, mountinfo_path="/proc/self/mountinfo"):
    matches = []
    with open(mountinfo_path, "r", encoding="utf-8") as stream:
        for raw in stream:
            left, separator, right = raw.partition(" - ")
            if not separator:
                continue
            fields = left.split()
            trailing = right.split()
            if len(fields) < 5 or not trailing:
                continue
            mountpoint = decode_mount_field(fields[4])
            value = str(path)
            if value == mountpoint or value.startswith(mountpoint.rstrip(os.sep) + os.sep):
                matches.append((mountpoint, trailing[0]))
    if not matches:
        fail("cannot bind path to a mounted filesystem")
    seen_mountpoints = set()
    for mountpoint, _filesystem in matches:
        if mountpoint in seen_mountpoints:
            fail("ambiguous stacked mountpoint")
        seen_mountpoints.add(mountpoint)
    deepest_length = max(len(match[0]) for match in matches)
    deepest = [match for match in matches if len(match[0]) == deepest_length]
    return deepest[0][1]


def require_local_posix_filesystem(path, label):
    if not sys.platform.startswith("linux"):
        fail("cannot verify local filesystem type for " + label)
    try:
        filesystem = linux_mount_type(path)
    except Exception as error:
        fail("cannot verify local filesystem type for " + label + ": " + str(type(error)))
    if filesystem == "overlay" and not ALLOW_OVERLAY:
        fail(label + " uses overlay; set VIRTUALWAGO_ALLOW_OVERLAY=1 only after "
             "binding its backing storage as local")
    if filesystem not in LOCAL_POSIX_FILESYSTEMS:
        fail(label + " must use a verified local filesystem, not " + filesystem)


def require_no_link_components(path, label):
    absolute = os.path.abspath(str(path))
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
        if os.name == "nt" and file_attributes is None:
            fail("cannot verify Windows reparse-point state for " + label)
        if (stat.S_ISLNK(metadata.st_mode)
                or file_attributes is not None and file_attributes & reparse_flag):
            fail(label + " must not traverse a symlink or reparse point")


def require_windows_private_acl(path, is_directory=True):
    try:
        from System.IO import Directory, File
        from System.Security.AccessControl import AccessControlType, FileSystemRights
        from System.Security.Principal import SecurityIdentifier, WindowsIdentity
        current = str(WindowsIdentity.GetCurrent().User.Value)
        allowed = frozenset({current, "S-1-5-18", "S-1-5-32-544", "S-1-3-0"})
        security = (Directory.GetAccessControl(str(path)) if is_directory
                    else File.GetAccessControl(str(path)))
        owner = str(security.GetOwner(SecurityIdentifier).Value)
        if owner not in allowed:
            fail("private root owner is not the current user/system/admin")
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
        if str(error).startswith("CODESYS mapping summary stopped:"):
            raise
        fail("cannot verify private Windows ACL: " + str(type(error)))


def require_private_permissions(root, path, label):
    try:
        relative = path.relative_to(root)
    except ValueError:
        fail(label + " must stay inside the private root")
    current = root
    candidates = [(root, True)]
    for part in relative.parts[:-1]:
        current = current / part
        if not current.exists():
            break
        candidates.append((current, True))
    if path.exists():
        candidates.append((path, path.is_dir()))
    seen = set()
    for candidate, is_directory in candidates:
        normalized = str(candidate)
        if normalized in seen:
            continue
        seen.add(normalized)
        if (os.name == "posix"
                and stat.S_IMODE(candidate.stat().st_mode) & 0o077):
            fail(label + " path must not grant group/other permissions")
        if os.name == "nt":
            require_windows_private_acl(candidate, is_directory)


def require_local_path(path, label):
    raw = str(path)
    normalized = raw.replace("/", "\\")
    if normalized.startswith("\\\\"):
        fail(label + " must be a local path, not a UNC/device path")
    raw_tail = ntpath.splitdrive(raw)[1] if os.name == "nt" else raw
    separators = r"[\\/]" if os.name == "nt" else "/"
    if ".." in re.split(separators, raw_tail):
        fail(label + " must not contain a parent-directory component")
    if os.name == "nt":
        drive, tail = ntpath.splitdrive(raw)
        if not drive or not tail.startswith(("\\", "/")):
            fail(label + " must use an absolute local drive path")
        try:
            import ctypes
            drive_type = ctypes.windll.kernel32.GetDriveTypeW(drive + "\\")
        except Exception as error:
            fail("cannot verify that " + label + " is on a local Windows drive: "
                 + str(type(error)))
        if drive_type == 4:
            fail(label + " must not use a mapped network drive")
    candidate = Path(os.path.abspath(raw))
    if os.name == "posix":
        require_local_posix_filesystem(candidate, label)
    require_no_link_components(candidate, label)
    return candidate


def validate_private_paths(input_path, output_path, private_root):
    root = require_local_path(private_root, "private root")
    if not root.is_dir():
        fail("private root must be an existing directory")
    for path, label in ((input_path, "input CSV"), (output_path, "output report")):
        candidate = require_local_path(path, label)
        try:
            candidate.relative_to(root)
        except ValueError:
            fail(label + " must stay inside the private root")
        require_private_permissions(root, candidate, label)
    return root


def write_exclusive(path, content):
    descriptor = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="") as stream:
            descriptor = None
            stream.write(content)
    finally:
        if descriptor is not None:
            os.close(descriptor)


def run(input_path, output_path, private_root):
    validate_private_paths(input_path, output_path, private_root)
    source = Path(input_path)
    output = Path(output_path)
    if not source.is_file():
        fail("input CSV does not exist")
    if output.exists():
        fail("refusing to overwrite an existing summary")
    source_bytes = source.read_bytes()
    report = {
        "schema": "virtualwago-codesys-mapping-summary/1",
        "scope": "offline CSV address coverage; no runtime or hardware proof",
        "source_sha256": hashlib.sha256(source_bytes).hexdigest(),
        "devices": summarize(read_rows_bytes(source_bytes)),
    }
    write_exclusive(output, json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--private-root", required=True)
    args = parser.parse_args()
    report = run(args.input, args.output, args.private_root)
    print(json.dumps({"status": "PASS", "source_sha256": report["source_sha256"],
                      "device_direction_count": len(report["devices"])}, sort_keys=True))


if __name__ == "__main__":
    main()
