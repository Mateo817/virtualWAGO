#!/usr/bin/env python3
"""Plan or launch a bounded ARM userspace command in a private bubblewrap sandbox.

The default mode is plan-only. This tool never configures host networking,
opens hardware, installs software, or runs original code unless an operator
explicitly supplies all execution inputs and ``--execute``.
"""
from __future__ import annotations

import argparse
import ctypes
import json
import os
from pathlib import Path, PurePosixPath
import resource
import selectors
import signal
import stat
import subprocess
import sys
import tempfile
import time
from typing import Any, Sequence


MAX_ROOTFS_ENTRIES = 100_000
MAX_ROOTFS_BYTES = 1024**3
MAX_QEMU_BYTES = 512 * 1024**2
MAX_OUTPUT_BYTES = 64 * 1024
MAX_TIMEOUT_SECONDS = 3600
QEMU_GUEST_PATH = "/opt/research/qemu-arm"
DEFAULT_TIMEOUT_SECONDS = 300
RLIMITS = (
    ("RLIMIT_CORE", 0),
    ("RLIMIT_FSIZE", 512 * 1024**2),
    ("RLIMIT_NOFILE", 256),
    ("RLIMIT_AS", 8 * 1024**3),
)
SENSITIVE_BASENAMES = {
    "authorized_keys", "known_hosts", "id_rsa", "id_dsa", "id_ecdsa", "id_ed25519",
    "ssh_host_rsa_key", "ssh_host_dsa_key", "ssh_host_ecdsa_key", "ssh_host_ed25519_key",
    "license.dat", "license.bin", "license.lic", "license.key", "licence.dat", "licence.bin",
}


class SandboxError(ValueError):
    """Input cannot be represented safely by this limited sandbox launcher."""


def _absolute_path(value: str, label: str) -> Path:
    path = Path(value)
    if not path.is_absolute():
        raise SandboxError(f"{label} must be an explicit absolute path")
    return path


def _open_pinned_regular(path: Path, label: str, *, max_size: int = MAX_ROOTFS_BYTES,
                         executable: bool = False) -> tuple[int, int, os.stat_result]:
    """Pin a pathname with O_PATH before opening data through its verified inode."""
    try:
        metadata_fd = os.open(path, os.O_PATH | os.O_NOFOLLOW)
    except OSError as exc:
        raise SandboxError(f"{label} must be an available regular non-symlink file") from exc
    try:
        info = os.fstat(metadata_fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > max_size:
            raise SandboxError(f"{label} must be a bounded regular non-symlink file")
        if executable and not info.st_mode & 0o111:
            raise SandboxError(f"{label} must be executable")
        try:
            data_fd = os.open(f"/proc/self/fd/{metadata_fd}", os.O_RDONLY | os.O_NONBLOCK)
        except OSError as exc:
            raise SandboxError(f"{label} inode could not be safely reopened") from exc
        reopened = os.fstat(data_fd)
        if (reopened.st_dev, reopened.st_ino) != (info.st_dev, info.st_ino) or not stat.S_ISREG(reopened.st_mode):
            os.close(data_fd)
            raise SandboxError(f"{label} changed during safe open")
        return metadata_fd, data_fd, info
    except Exception:
        os.close(metadata_fd)
        raise


def _open_pinned_regular_at(directory_fd: int, name: str, label: str,
                            max_size: int = MAX_ROOTFS_BYTES) -> tuple[int, int, os.stat_result]:
    try:
        metadata_fd = os.open(name, os.O_PATH | os.O_NOFOLLOW, dir_fd=directory_fd)
    except OSError as exc:
        raise SandboxError(f"{label} changed during safe open") from exc
    try:
        info = os.fstat(metadata_fd)
        if not stat.S_ISREG(info.st_mode) or info.st_size > max_size:
            raise SandboxError(f"{label} is not a bounded regular file")
        try:
            data_fd = os.open(f"/proc/self/fd/{metadata_fd}", os.O_RDONLY | os.O_NONBLOCK)
        except OSError as exc:
            raise SandboxError(f"{label} inode could not be safely reopened") from exc
        reopened = os.fstat(data_fd)
        if (reopened.st_dev, reopened.st_ino) != (info.st_dev, info.st_ino) or not stat.S_ISREG(reopened.st_mode):
            os.close(data_fd)
            raise SandboxError(f"{label} changed during safe open")
        return metadata_fd, data_fd, info
    except Exception:
        os.close(metadata_fd)
        raise


def _regular_executable(value: str, label: str) -> Path:
    path = _absolute_path(value, label)
    try:
        info = path.lstat()
    except OSError as exc:
        raise SandboxError(f"{label} is unavailable") from exc
    if not stat.S_ISREG(info.st_mode) or not info.st_mode & 0o111:
        raise SandboxError(f"{label} must be a regular executable file, not a symlink")
    return path


def _guest_symlink_stays_inside(parent: str, target: str) -> bool:
    if not target:
        return False
    stack: list[str] = [] if target.startswith("/") else [part for part in parent.split("/") if part]
    for component in target.split("/"):
        if component in ("", "."):
            continue
        if component == "..":
            if not stack:
                return False
            stack.pop()
        else:
            stack.append(component)
    return True


def _is_sensitive_guest_path(relative: str) -> bool:
    path = PurePosixPath(relative)
    parts = tuple(part.lower() for part in path.parts)
    name = path.name.lower()
    if ".ssh" in parts or name in SENSITIVE_BASENAMES:
        return True
    if name.startswith("ssh_host_") and name.endswith("_key"):
        return True
    if name.endswith((".lic", ".license", ".wbb")):
        return True
    return False


def scan_rootfs(path_value: str) -> dict[str, int]:
    """Validate a rootfs tree without following guest symlinks or opening specials."""
    root = _absolute_path(path_value, "rootfs")
    try:
        root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        raise SandboxError("rootfs must be an available explicit directory, not a symlink") from exc
    counts = {"directories": 0, "regular_files": 0, "symlinks": 0, "bytes": 0, "entries": 0}
    inode_links: dict[tuple[int, int], tuple[int, int]] = {}
    def walk(directory_fd: int, relative_parent: str) -> None:
        before = os.fstat(directory_fd)
        try:
            with os.scandir(directory_fd) as iterator:
                names = [entry.name for entry in iterator]
        except OSError as exc:
            raise SandboxError("rootfs cannot be completely inspected") from exc
        for name in names:
            relative = f"{relative_parent}/{name}" if relative_parent else name
            counts["entries"] += 1
            if counts["entries"] > MAX_ROOTFS_ENTRIES:
                raise SandboxError("rootfs exceeds the bounded entry count")
            if _is_sensitive_guest_path(relative):
                raise SandboxError("rootfs contains a host-key or license-like path")
            try:
                info = os.stat(name, dir_fd=directory_fd, follow_symlinks=False)
            except OSError as exc:
                raise SandboxError("rootfs changed or became unreadable during inspection") from exc
            mode = info.st_mode
            if stat.S_ISDIR(mode):
                counts["directories"] += 1
                try:
                    child_fd = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                       dir_fd=directory_fd)
                except OSError as exc:
                    raise SandboxError("rootfs directory changed during inspection") from exc
                try:
                    actual = os.fstat(child_fd)
                    if (actual.st_dev, actual.st_ino) != (info.st_dev, info.st_ino):
                        raise SandboxError("rootfs directory changed during inspection")
                    walk(child_fd, relative)
                finally:
                    os.close(child_fd)
            elif stat.S_ISREG(mode):
                counts["regular_files"] += 1
                counts["bytes"] += info.st_size
                key = (info.st_dev, info.st_ino)
                prior_count, prior_nlink = inode_links.get(key, (0, info.st_nlink))
                inode_links[key] = (prior_count + 1, prior_nlink)
                if counts["bytes"] > MAX_ROOTFS_BYTES:
                    raise SandboxError("rootfs exceeds the bounded regular-file size")
            elif stat.S_ISLNK(mode):
                counts["symlinks"] += 1
                try:
                    target = os.readlink(name, dir_fd=directory_fd)
                except OSError as exc:
                    raise SandboxError("rootfs symlink changed during inspection") from exc
                if not _guest_symlink_stays_inside(relative_parent, target):
                    raise SandboxError("rootfs contains a guest symlink that escapes its root")
            else:
                raise SandboxError("rootfs contains a device, socket, FIFO, or unsupported special file")
        after = os.fstat(directory_fd)
        if (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns) != (
                after.st_dev, after.st_ino, after.st_mtime_ns, after.st_ctime_ns):
            raise SandboxError("rootfs directory changed during inspection")

    try:
        counts["directories"] = 1
        walk(root_fd, "")
    finally:
        os.close(root_fd)
    if any(actual != links for actual, links in inode_links.values()):
        raise SandboxError("rootfs contains a regular file hard-linked outside the inspected tree")
    return counts


def _copy_fd_contents(source_fd: int, destination_fd: int, expected_size: int) -> None:
    copied = 0
    while True:
        chunk = os.read(source_fd, 1024 * 1024)
        if not chunk:
            break
        copied += len(chunk)
        if copied > expected_size or copied > MAX_ROOTFS_BYTES:
            raise SandboxError("rootfs file changed or exceeds the bounded snapshot size")
        view = memoryview(chunk)
        while view:
            written = os.write(destination_fd, view)
            view = view[written:]
    if copied != expected_size:
        raise SandboxError("rootfs file changed while the private snapshot was created")


def _copy_rootfs_directory(source_fd: int, destination_fd: int, relative_parent: str,
                           counts: dict[str, int], inode_links: dict[tuple[int, int], tuple[int, int]]) -> None:
    before = os.fstat(source_fd)
    try:
        with os.scandir(source_fd) as iterator:
            names = [entry.name for entry in iterator]
    except OSError as exc:
        raise SandboxError("rootfs cannot be completely snapshotted") from exc
    for name in names:
        relative = f"{relative_parent}/{name}" if relative_parent else name
        counts["entries"] += 1
        if counts["entries"] > MAX_ROOTFS_ENTRIES:
            raise SandboxError("rootfs exceeds the bounded entry count")
        if _is_sensitive_guest_path(relative):
            raise SandboxError("rootfs contains a host-key or license-like path")
        try:
            info = os.stat(name, dir_fd=source_fd, follow_symlinks=False)
        except OSError as exc:
            raise SandboxError("rootfs changed during the private snapshot") from exc
        if stat.S_ISDIR(info.st_mode):
            counts["directories"] += 1
            os.mkdir(name, 0o700, dir_fd=destination_fd)
            child_source = child_destination = None
            try:
                child_source = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                       dir_fd=source_fd)
                child_destination = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW,
                                            dir_fd=destination_fd)
            except OSError as exc:
                if child_source is not None:
                    os.close(child_source)
                raise SandboxError("rootfs directory changed during the private snapshot") from exc
            try:
                actual = os.fstat(child_source)
                if (actual.st_dev, actual.st_ino) != (info.st_dev, info.st_ino):
                    raise SandboxError("rootfs directory changed during the private snapshot")
                _copy_rootfs_directory(child_source, child_destination, relative, counts, inode_links)
                os.fchmod(child_destination, stat.S_IMODE(info.st_mode) & 0o0777 & ~0o6000)
            finally:
                os.close(child_source)
                os.close(child_destination)
        elif stat.S_ISREG(info.st_mode):
            counts["regular_files"] += 1
            counts["bytes"] += info.st_size
            if counts["bytes"] > MAX_ROOTFS_BYTES:
                raise SandboxError("rootfs exceeds the bounded regular-file size")
            source_pin = source_file = destination_file = None
            try:
                source_pin, source_file, pinned_info = _open_pinned_regular_at(
                    source_fd, name, "rootfs regular file")
                destination_file = os.open(name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
                                           0o600, dir_fd=destination_fd)
            except OSError as exc:
                if source_pin is not None:
                    os.close(source_pin)
                if source_file is not None:
                    os.close(source_file)
                raise SandboxError("rootfs regular file changed during the private snapshot") from exc
            try:
                actual = os.fstat(source_file)
                if ((actual.st_dev, actual.st_ino) != (info.st_dev, info.st_ino)
                        or (pinned_info.st_dev, pinned_info.st_ino) != (info.st_dev, info.st_ino)):
                    raise SandboxError("rootfs regular file changed during the private snapshot")
                inode = (actual.st_dev, actual.st_ino)
                prior_count, prior_nlink = inode_links.get(inode, (0, actual.st_nlink))
                inode_links[inode] = (prior_count + 1, prior_nlink)
                _copy_fd_contents(source_file, destination_file, actual.st_size)
                final = os.fstat(source_file)
                stable_fields = ("st_size", "st_mtime_ns", "st_ctime_ns")
                if any(getattr(final, field) != getattr(actual, field) for field in stable_fields):
                    raise SandboxError("rootfs file changed during the private snapshot")
                os.fchmod(destination_file, stat.S_IMODE(actual.st_mode) & 0o0777 & ~0o6000)
            finally:
                os.close(source_file)
                os.close(source_pin)
                os.close(destination_file)
        elif stat.S_ISLNK(info.st_mode):
            counts["symlinks"] += 1
            try:
                target = os.readlink(name, dir_fd=source_fd)
            except OSError as exc:
                raise SandboxError("rootfs symlink changed during the private snapshot") from exc
            if not _guest_symlink_stays_inside(relative_parent, target):
                raise SandboxError("rootfs contains a guest symlink that escapes its root")
            os.symlink(target, name, dir_fd=destination_fd)
        else:
            raise SandboxError("rootfs contains a device, socket, FIFO, or unsupported special file")
    after = os.fstat(source_fd)
    if (before.st_dev, before.st_ino, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_dev, after.st_ino, after.st_mtime_ns, after.st_ctime_ns):
        raise SandboxError("rootfs directory changed during the private snapshot")


def snapshot_rootfs(path_value: str, destination: str) -> dict[str, int]:
    """Copy a validated guest tree into an owner-private directory without following host links."""
    source = _absolute_path(path_value, "rootfs")
    target = Path(destination)
    try:
        root_fd = os.open(source, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        target_stat = target.lstat()
    except OSError as exc:
        if "root_fd" in locals():
            os.close(root_fd)
        raise SandboxError("rootfs snapshot source/destination is unavailable") from exc
    if not stat.S_ISDIR(target_stat.st_mode):
        os.close(root_fd)
        raise SandboxError("private rootfs snapshot destination must be a real directory")
    counts = {"directories": 1, "regular_files": 0, "symlinks": 0, "bytes": 0, "entries": 0}
    inode_links: dict[tuple[int, int], tuple[int, int]] = {}
    try:
        target_fd = os.open(target, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
        try:
            _copy_rootfs_directory(root_fd, target_fd, "", counts, inode_links)
            if any(actual != links for actual, links in inode_links.values()):
                raise SandboxError("rootfs contains a regular file hard-linked outside the inspected tree")
            os.fchmod(target_fd, stat.S_IMODE(os.fstat(root_fd).st_mode) & 0o0777 & ~0o6000)
        finally:
            os.close(target_fd)
    finally:
        os.close(root_fd)
    return counts


def snapshot_qemu(path_value: str, destination: str) -> Path:
    """Copy one explicitly selected static executable through a no-follow fd."""
    source = _regular_executable(path_value, "qemu")
    target = Path(destination)
    source_pin = source_fd = destination_fd = None
    try:
        source_pin, source_fd, info = _open_pinned_regular(
            source, "qemu", max_size=MAX_QEMU_BYTES, executable=True)
        if not info.st_mode & 0o111:
            raise SandboxError("QEMU source must be a bounded regular executable file")
        destination_fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0o600)
    except OSError as exc:
        if source_pin is not None:
            os.close(source_pin)
        if source_fd is not None:
            os.close(source_fd)
        raise SandboxError("QEMU source or private snapshot destination is unavailable") from exc
    try:
        _copy_fd_contents(source_fd, destination_fd, info.st_size)
        final = os.fstat(source_fd)
        if (final.st_dev, final.st_ino, final.st_size, final.st_mtime_ns, final.st_ctime_ns) != (
                info.st_dev, info.st_ino, info.st_size, info.st_mtime_ns, info.st_ctime_ns):
            raise SandboxError("QEMU source changed during the private snapshot")
        os.fchmod(destination_fd, 0o555)
    finally:
        os.close(source_fd)
        os.close(source_pin)
        os.close(destination_fd)
    _verify_static_elf(target)
    return target


def _guest_mountpoint(root: Path, relative: str, *, required: bool = True) -> Path | None:
    candidate = root.joinpath(*PurePosixPath(relative).parts)
    try:
        info = candidate.lstat()
    except FileNotFoundError:
        if required:
            raise SandboxError(f"minimal rootfs is missing required {relative} directory")
        return None
    except OSError as exc:
        raise SandboxError(f"cannot inspect required rootfs path {relative}") from exc
    if not stat.S_ISDIR(info.st_mode):
        raise SandboxError(f"minimal rootfs {relative} mount point must be a real directory")
    return candidate


def validate_rootfs_layout(rootfs: str, with_proc: bool) -> Path:
    root = _absolute_path(rootfs, "rootfs")
    _guest_mountpoint(root, "tmp")
    _guest_mountpoint(root, "dev")
    _guest_mountpoint(root, "opt/research")
    if with_proc:
        _guest_mountpoint(root, "proc")
    qemu_dest = root / "opt/research/qemu-arm"
    try:
        existing = qemu_dest.lstat()
    except FileNotFoundError:
        return root
    except OSError as exc:
        raise SandboxError("cannot inspect the private QEMU mount destination") from exc
    if not stat.S_ISREG(existing.st_mode):
        raise SandboxError("QEMU mount destination must be absent or a regular placeholder file")
    return root


def _prepare_qemu_mountpoint(rootfs: Path) -> None:
    """Create an empty mountpoint in the private snapshot before it is read-only."""
    target = rootfs / "opt/research/qemu-arm"
    try:
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW, 0)
    except FileExistsError:
        info = target.lstat()
        if not stat.S_ISREG(info.st_mode):
            raise SandboxError("QEMU mount destination must be absent or a regular placeholder file")
        return
    except OSError as exc:
        raise SandboxError("cannot prepare the private QEMU mount destination") from exc
    else:
        os.close(fd)


def _terminate_and_reap(proc: subprocess.Popen[bytes]) -> None:
    """Stop the process group and bound both graceful and forced reaping."""
    try:
        os.killpg(proc.pid, signal.SIGTERM)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=2)
        return
    except subprocess.TimeoutExpired:
        pass
    try:
        os.killpg(proc.pid, signal.SIGKILL)
    except ProcessLookupError:
        pass
    try:
        proc.wait(timeout=2)
    except subprocess.TimeoutExpired as exc:
        raise SandboxError("sandbox launcher could not be reaped after bounded termination") from exc


def _verify_static_elf(path: Path) -> None:
    """Require ELF without PT_INTERP or DT_NEEDED; never execute the input."""
    metadata_fd = data_fd = None
    try:
        metadata_fd, data_fd, info = _open_pinned_regular(
            path, "QEMU ELF", max_size=MAX_QEMU_BYTES, executable=True)
        ident = os.read(data_fd, 16)
        if len(ident) != 16 or ident[:4] != b"\x7fELF" or ident[4] not in (1, 2) or ident[5] not in (1, 2):
            raise SandboxError("QEMU must be a supported ELF executable")
        endian = "<" if ident[5] == 1 else ">"
        if ident[4] == 1:
            header = os.read(data_fd, 36)
            if len(header) != 36:
                raise SandboxError("QEMU ELF header is truncated")
            phoff = int.from_bytes(header[12:16], "little" if endian == "<" else "big")
            phentsize = int.from_bytes(header[26:28], "little" if endian == "<" else "big")
            phnum = int.from_bytes(header[28:30], "little" if endian == "<" else "big")
            min_size = 32
        else:
            header = os.read(data_fd, 48)
            if len(header) != 48:
                raise SandboxError("QEMU ELF header is truncated")
            phoff = int.from_bytes(header[16:24], "little" if endian == "<" else "big")
            phentsize = int.from_bytes(header[38:40], "little" if endian == "<" else "big")
            phnum = int.from_bytes(header[40:42], "little" if endian == "<" else "big")
            min_size = 56
        if phentsize < min_size or phnum > 4096 or phoff + phentsize * phnum > info.st_size:
            raise SandboxError("QEMU ELF program-header table is invalid")
        for index in range(phnum):
            os.lseek(data_fd, phoff + index * phentsize, os.SEEK_SET)
            program_header = os.read(data_fd, phentsize)
            if len(program_header) != phentsize:
                raise SandboxError("QEMU ELF program-header table is truncated")
            p_type = int.from_bytes(program_header[:4], "little" if endian == "<" else "big")
            if p_type == 3:  # PT_INTERP
                raise SandboxError("QEMU must be static (PT_INTERP is present)")
            if p_type == 2:  # PT_DYNAMIC: static PIE may have relocations, but no DT_NEEDED.
                order = "little" if endian == "<" else "big"
                if ident[4] == 1:
                    offset = int.from_bytes(program_header[4:8], order)
                    size = int.from_bytes(program_header[16:20], order)
                    width = 4
                else:
                    offset = int.from_bytes(program_header[8:16], order)
                    size = int.from_bytes(program_header[32:40], order)
                    width = 8
                if size > 1024 * 1024 or offset + size > info.st_size or size % (2 * width):
                    raise SandboxError("QEMU ELF dynamic segment is invalid or oversized")
                terminated = False
                for entry in range(0, size, 2 * width):
                    tag = os.pread(data_fd, width, offset + entry)
                    if len(tag) != width:
                        raise SandboxError("QEMU ELF dynamic segment is truncated")
                    kind = int.from_bytes(tag, order)
                    if kind == 1:
                        raise SandboxError("QEMU must be static (DT_NEEDED is present)")
                    if kind == 0:
                        terminated = True
                        break
                if not terminated:
                    raise SandboxError("QEMU ELF dynamic segment has no terminator")
    except OSError as exc:
        raise SandboxError("QEMU executable cannot be inspected") from exc
    finally:
        if data_fd is not None:
            os.close(data_fd)
        if metadata_fd is not None:
            os.close(metadata_fd)


def validate_qemu(path_value: str) -> Path:
    path = _regular_executable(path_value, "qemu")
    _verify_static_elf(path)
    return path


def _bounded_rlimits(timeout_seconds: int):
    limits = []
    values = {"RLIMIT_CPU": (timeout_seconds, timeout_seconds + 1)}
    values.update({name: (limit, limit) for name, limit in RLIMITS})
    for name, requested in values.items():
        if not hasattr(resource, name):
            continue
        resource_id = getattr(resource, name)
        current_soft, current_hard = resource.getrlimit(resource_id)
        soft = requested[0] if current_hard == resource.RLIM_INFINITY else min(requested[0], current_hard)
        hard = requested[1] if current_hard == resource.RLIM_INFINITY else min(requested[1], current_hard)
        limits.append((resource_id, soft, hard))
    return limits


def _preexec_limits(timeout_seconds: int):
    limits = _bounded_rlimits(timeout_seconds)
    libc = ctypes.CDLL(None, use_errno=True)
    prctl = libc.prctl
    prctl.argtypes = (ctypes.c_int, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong, ctypes.c_ulong)
    prctl.restype = ctypes.c_int

    def apply() -> None:
        for resource_id, soft, hard in limits:
            resource.setrlimit(resource_id, (soft, hard))
        # Set this in the launcher child before exec; bwrap and the guest inherit
        # it. Fail closed on kernels that do not support the required control.
        if prctl(38, 1, 0, 0, 0) != 0:  # PR_SET_NO_NEW_PRIVS
            error = ctypes.get_errno()
            raise OSError(error, os.strerror(error))
    return apply


def build_bwrap_command(bwrap: str, rootfs: str, qemu: str, guest_argv: Sequence[str],
                        with_proc: bool = False) -> list[str]:
    if not guest_argv or not guest_argv[0].startswith("/"):
        raise SandboxError("guest command must start with an absolute path inside the rootfs")
    guest_exec = PurePosixPath(guest_argv[0])
    if ".." in guest_exec.parts:
        raise SandboxError("guest executable path must not contain parent traversal")
    cmd = [
        bwrap,
        "--die-with-parent",
        "--new-session",
        "--unshare-all",
        "--unshare-user",
        "--clearenv",
        "--ro-bind", rootfs, "/",
        "--tmpfs", "/tmp",
        "--dev", "/dev",
    ]
    if with_proc:
        cmd.extend(["--proc", "/proc"])
    cmd.extend([
        "--ro-bind", qemu, QEMU_GUEST_PATH,
        "--chdir", "/",
        "--setenv", "HOME", "/tmp",
        "--setenv", "TMPDIR", "/tmp",
        "--setenv", "PATH", "/usr/bin:/bin:/usr/sbin:/sbin",
        "--setenv", "LANG", "C",
        "--setenv", "LC_ALL", "C",
        "--disable-userns",
        "--cap-drop", "ALL",
        "--",
        QEMU_GUEST_PATH, "-L", "/", *guest_argv,
    ])
    return cmd


def _guest_executable(rootfs: str, guest_argv: Sequence[str]) -> None:
    if not guest_argv or not guest_argv[0].startswith("/"):
        raise SandboxError("guest command must start with an absolute path inside the rootfs")
    guest_path = PurePosixPath(guest_argv[0])
    if ".." in guest_path.parts:
        raise SandboxError("guest executable path must not contain parent traversal")
    root = Path(rootfs)
    candidate = root.joinpath(*guest_path.parts[1:])
    try:
        resolved = candidate.resolve(strict=True)
        resolved.relative_to(root.resolve(strict=True))
        info = resolved.stat()
    except (OSError, ValueError) as exc:
        raise SandboxError("guest executable is missing or escapes the supplied rootfs") from exc
    if not stat.S_ISREG(info.st_mode) or not info.st_mode & 0o111:
        raise SandboxError("guest command must resolve to a regular executable file")


def plan(rootfs: str | None = None, qemu: str | None = None, bwrap: str | None = None,
         with_proc: bool = False) -> dict[str, Any]:
    root_counts = None
    if rootfs is not None:
        root_counts = scan_rootfs(rootfs)
        validate_rootfs_layout(rootfs, with_proc)
    if qemu is not None:
        validate_qemu(qemu)
    if bwrap is not None:
        _regular_executable(bwrap, "bwrap")
    return {
        "status": "PLAN_ONLY",
        "execution_requested": False,
        "setup_performed": False,
        "guest_code_executed": False,
        "network_access_attempted": False,
        "rootfs_counts": root_counts,
        "qemu_static_elf_validated": qemu is not None,
        "bwrap_explicit_path_validated": bwrap is not None,
        "mount_policy": ["rootfs read-only at /", "private tmpfs at /tmp", "private minimal /dev",
                         "no host /proc, /sys, /run, /home, or Unix sockets"],
        "namespaces": ["user", "pid", "net", "ipc", "uts", "private mount"],
        "private_proc": "only when explicitly requested",
        "environment": "clearenv; minimal HOME/TMPDIR/PATH/LANG; no host LD_* variables",
        "stdin": "closed; interactive prompts unsupported",
        "scope": "explicitly selected guest command only; original runtime and unreviewed payloads are outside this verification",
        "privileges": "launcher sets PR_SET_NO_NEW_PRIVS before bwrap; all capabilities dropped; kernel probe remains required",
        "limits": {"timeout_seconds": DEFAULT_TIMEOUT_SECONDS, "cpu_seconds": DEFAULT_TIMEOUT_SECONDS,
                   "address_space_bytes": 8 * 1024**3, "file_size_bytes": 512 * 1024**2,
                   "open_files": 256, "core_bytes": 0, "captured_output_bytes_each": MAX_OUTPUT_BYTES,
                   "scope": "per process; no aggregate cgroup quota is configured"},
        "evidence": "NOT_RUN: plan or parser tests do not verify kernel isolation or ARM execution",
    }


def _capture_bwrap(command: Sequence[str], timeout_seconds: int) -> dict[str, Any]:
    proc = subprocess.Popen(command, stdin=subprocess.DEVNULL, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, start_new_session=True, close_fds=True,
                            preexec_fn=_preexec_limits(timeout_seconds))
    assert proc.stdout is not None and proc.stderr is not None
    selector = selectors.DefaultSelector()
    output = {proc.stdout: bytearray(), proc.stderr: bytearray()}
    truncated = {proc.stdout: False, proc.stderr: False}
    for stream in output:
        os.set_blocking(stream.fileno(), False)
        selector.register(stream, selectors.EVENT_READ)
    deadline = time.monotonic() + timeout_seconds
    timed_out = False
    try:
        while selector.get_map():
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
                break
            for key, _ in selector.select(min(remaining, 0.2)):
                stream = key.fileobj
                try:
                    chunk = os.read(stream.fileno(), 65536)
                except BlockingIOError:
                    continue
                if not chunk:
                    selector.unregister(stream)
                    stream.close()
                    continue
                data = output[stream]
                room = MAX_OUTPUT_BYTES - len(data)
                if room > 0:
                    data.extend(chunk[:room])
                if len(chunk) > room:
                    truncated[stream] = True
        # Pipe EOF is not proof that the process exited: a guest can close
        # stdout/stderr and continue running. Keep enforcing the deadline.
        if not timed_out and proc.poll() is None:
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                timed_out = True
            else:
                try:
                    proc.wait(timeout=remaining)
                except subprocess.TimeoutExpired:
                    timed_out = True
        if timed_out:
            _terminate_and_reap(proc)
    finally:
        for stream in (proc.stdout, proc.stderr):
            if not stream.closed:
                stream.close()
        if proc.poll() is None:
            _terminate_and_reap(proc)
    return {
        "status": "TIMEOUT" if timed_out else ("PASS" if proc.returncode == 0 else "FAIL"),
        "exit_code": proc.returncode,
        "timed_out": timed_out,
        "stdout": bytes(output[proc.stdout]).decode("utf-8", errors="replace"),
        "stderr": bytes(output[proc.stderr]).decode("utf-8", errors="replace"),
        "stdout_truncated": truncated[proc.stdout],
        "stderr_truncated": truncated[proc.stderr],
        "capture_limit_bytes_each": MAX_OUTPUT_BYTES,
    }


def execute(bwrap: str, rootfs: str, qemu: str, guest_argv: Sequence[str],
            timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS, with_proc: bool = False) -> dict[str, Any]:
    if not 1 <= timeout_seconds <= MAX_TIMEOUT_SECONDS:
        raise SandboxError(f"timeout must be between 1 and {MAX_TIMEOUT_SECONDS} seconds")
    bwrap_path = _regular_executable(bwrap, "bwrap")
    # Never mount the caller's mutable rootfs/QEMU inode into the guest. Copy
    # from no-follow descriptors into a mode-0700 private snapshot, then bind
    # only those snapshots read-only.
    with tempfile.TemporaryDirectory(prefix="virtualwago-sandbox-") as temporary:
        private_dir = Path(temporary)
        root_snapshot = private_dir / "rootfs"
        root_snapshot.mkdir(mode=0o700)
        counts = snapshot_rootfs(rootfs, str(root_snapshot))
        _prepare_qemu_mountpoint(root_snapshot)
        validate_rootfs_layout(str(root_snapshot), with_proc)
        qemu_snapshot = snapshot_qemu(qemu, str(private_dir / "qemu-arm"))
        _guest_executable(str(root_snapshot), guest_argv)
        command = build_bwrap_command(str(bwrap_path), str(root_snapshot), str(qemu_snapshot),
                                      guest_argv, with_proc)
        result = _capture_bwrap(command, timeout_seconds)
        result["rootfs_snapshot_counts"] = counts
        result["rootfs_snapshot_private_mode"] = "0700 directory; read-only bind in guest"
        result["qemu_mountpoint_prepared_in_snapshot"] = True
        result["guest_code_execution"] = "REQUESTED"
        result["execution_scope"] = "explicit guest command only; no claim for original runtime or unreviewed payloads"
        result["resource_limit_scope"] = "per process; no aggregate cgroup quota is configured"
        return result


def _parse_args(argv: Sequence[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bwrap", help="explicit trusted absolute bubblewrap executable path")
    parser.add_argument("--rootfs", help="explicit minimal guest rootfs directory")
    parser.add_argument("--qemu", help="explicit static host QEMU user-mode ELF path")
    parser.add_argument("--execute", action="store_true", help="execute the guest command; default is plan-only")
    parser.add_argument("--with-proc", action="store_true", help="mount private procfs in the PID namespace")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("guest_argv", nargs=argparse.REMAINDER,
                        help="guest executable and arguments after --; guest path must be absolute")
    args = parser.parse_args(argv)
    if args.guest_argv and args.guest_argv[0] == "--":
        args.guest_argv = args.guest_argv[1:]
    return args


def main(argv: Sequence[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        if args.execute:
            if not all((args.bwrap, args.rootfs, args.qemu)) or not args.guest_argv:
                raise SandboxError("--execute requires --bwrap, --rootfs, --qemu, and guest argv after --")
            result = execute(args.bwrap, args.rootfs, args.qemu, args.guest_argv,
                             args.timeout_seconds, args.with_proc)
            print(json.dumps(result, indent=2, sort_keys=True))
            return 0 if result["status"] == "PASS" else 1
        if args.guest_argv:
            raise SandboxError("guest argv is accepted only with --execute")
        if args.timeout_seconds != DEFAULT_TIMEOUT_SECONDS:
            raise SandboxError("--timeout-seconds is only valid with --execute")
        print(json.dumps(plan(args.rootfs, args.qemu, args.bwrap, args.with_proc), indent=2, sort_keys=True))
        return 0
    except (SandboxError, OSError) as exc:
        print(f"offline_sandbox: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
