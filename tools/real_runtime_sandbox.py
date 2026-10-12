"""Render the bounded same-board runtime trial; never contact or start a PLC.

The integrator must bind the exact board, original files and staged artifacts
before using this argv on the reference. This is a mount/network policy, not
proof that a runtime starts or that its I/O driver accepts the own provider.
"""
from __future__ import annotations

from pathlib import PurePosixPath


def _absolute(value: str) -> str:
    path = PurePosixPath(value)
    if not value.startswith("/") or str(path) != value or ".." in path.parts:
        raise ValueError("canonical absolute path required")
    return value


def build_namespace_prefix(bwrap: str, stage: str) -> list[str]:
    bwrap, stage = _absolute(bwrap), _absolute(stage)
    if stage in ("/", "/usr", "/etc", "/home", "/tmp", "/var"):
        raise ValueError("dedicated staged directory required")
    return [
        bwrap, "--unshare-pid", "--unshare-net", "--unshare-ipc",
        "--unshare-uts", "--die-with-parent", "--new-session",
        "--cap-drop", "ALL", "--clearenv",
        "--ro-bind", "/usr", "/usr", "--ro-bind", "/bin", "/bin",
        "--symlink", "usr/lib", "/lib", "--ro-bind", "/etc", "/etc",
        "--ro-bind", stage + "/cfg", "/etc/codesys3.d",
        "--ro-bind", stage + "/drivers", "/usr/lib/IoDrvDal",
        "--ro-bind", stage + "/libdal.so", "/usr/lib/libdal.so.1.0.1",
        "--ro-bind", stage + "/roprobe", "/opt/research",
        "--tmpfs", "/sys", "--ro-bind", "/sys/firmware", "/sys/firmware",
        "--dev", "/dev", "--proc", "/proc", "--tmpfs", "/run",
        "--tmpfs", "/tmp", "--dir", "/var", "--symlink", "../run", "/var/run",
        "--dir", "/home", "--bind", stage + "/home", "/home/codesys_root",
        "--symlink", "codesys_root", "/home/codesys",
        "--chdir", "/home/codesys_root",
        "--setenv", "HOME", "/home/codesys_root",
        "--setenv", "PATH", "/usr/bin:/bin",
        "--setenv", "VIRTUALWAGO_MODEL_SOCKET", "/home/codesys_root/model/model.sock",
    ]


def build_runtime_command(bwrap: str, stage: str) -> list[str]:
    return build_namespace_prefix(bwrap, stage) + [
        "/usr/bin/codesys3", "/etc/codesys3.d/CODESYSControl_User.cfg",
    ]
