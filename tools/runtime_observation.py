"""Parse supplied proc snapshot text into bounded, allowlisted observations.

The parsing functions operate only on their text arguments.  The CLI reads
trusted, previously captured ordinary local files; path and file-type checks
are misuse prevention, not filesystem, mount, or hostile-namespace isolation.
It does not capture a live process or contact a runtime/device/network.  Output
contains no input paths or arbitrary task strings.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from typing import Optional


MAX_MAPS_BYTES = 2 * 1024 * 1024
MAX_FD_BYTES = 1024 * 1024
MAX_TASK_BYTES = 1024 * 1024
MAX_CWD_BYTES = 8192

_MAP_LINE = re.compile(
    r"^[0-9a-fA-F]+-[0-9a-fA-F]+\s+"
    r"[r-][w-][x-][ps]\s+[0-9a-fA-F]+\s+"
    r"[0-9a-fA-F]+:[0-9a-fA-F]+\s+\d+"
    r"(?:\s+(.*))?$"
)
_LIBRARY = re.compile(
    r"^lib(IoDrvDal|IoDrvKbus|dal|packbus|wago_dbus|diagnostic)"
    r"\.so(?:\.[0-9]+)*$"
)
_UIO_DEVICE = re.compile(r"^/dev/uio[0-9]+$")
_FD_ROW = re.compile(
    r"^(?P<mode>[bcdlps-][rwxStTs-]{9})\s+\d+\s+\S+\s+\S+\s+\d+\s+"
    r"\S+\s+\S+\s+\S+\s+(?P<fd>[0-9]+)(?:\s+->\s+(?P<target>[^\r\n]+))?$"
)
_TASK_TEXT = re.compile(r"^[\x20-\x7e]{1,15}$")
_TASK_CLASSES = ("DAL", "KBUS", "WagoAsync", "wdbw")
_TASK_CLASS_PATTERNS = {
    # DAL/KBUS allow a bounded comm suffix after a separating space/underscore.
    # Async and wdbw names are exact known comm names; arbitrary suffixes do
    # not become evidence merely because their prefix looks familiar.
    "DAL": re.compile(r"^(?:DAL evt dispatc|DAL_TriggerWdg|DAL[ _][A-Za-z0-9 _-]{1,11})$"),
    "KBUS": re.compile(r"^(?:KBUS dbus|KBUS_CYCLE_TASK|KBUS[ _][A-Za-z0-9 _-]{1,10})$"),
    "WagoAsync": re.compile(r"^WagoAsync(?:RtHigh|RtMed|RtLow|High|Med|Low|Bg|BusCyc|BusEvt)$"),
    "wdbw": re.compile(r"^wdbw_TermReg_Fq$"),
}


def _validate_text(value: Optional[str], limit: int, label: str) -> Optional[str]:
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("%s input must be text or None" % label)
    try:
        encoded_size = len(value.encode("utf-8"))
    except UnicodeEncodeError:
        raise ValueError("%s input is not valid Unicode text" % label) from None
    if encoded_size > limit:
        raise ValueError("%s input exceeds the size limit" % label)
    return value


def _required_lines(text: str, label: str) -> list[str]:
    if not text or not text.strip():
        raise ValueError("%s input is empty" % label)
    lines = text.splitlines()
    if any(not line for line in lines):
        raise ValueError("%s input contains an empty line" % label)
    return lines


def _parse_maps(text: str) -> tuple[list[str], bool]:
    libraries: set[str] = set()
    uio_mapping = False
    for line in _required_lines(text, "maps"):
        match = _MAP_LINE.fullmatch(line)
        if not match:
            raise ValueError("maps input contains a malformed line")
        start_end = line.split(None, 1)[0].split("-", 1)
        if int(start_end[0], 16) >= int(start_end[1], 16):
            raise ValueError("maps input contains an invalid address range")
        path = match.group(1)
        if not path:
            continue
        if any(ord(char) < 0x20 or ord(char) == 0x7f for char in path):
            raise ValueError("maps input contains an invalid pathname field")
        clean_path = path[:-10] if path.endswith(" (deleted)") else path
        filename = clean_path.rsplit("/", 1)[-1]
        library_match = _LIBRARY.fullmatch(filename)
        if library_match:
            libraries.add(library_match.group(1))
        if _UIO_DEVICE.fullmatch(clean_path):
            uio_mapping = True
    return sorted(libraries), uio_mapping


def _parse_fd_links(text: str) -> bool:
    kbus0_present = False
    saw_entry = False
    for line in _required_lines(text, "fd links"):
        if re.fullmatch(r"total\s+[0-9]+", line):
            if saw_entry:
                raise ValueError("fd links input contains a misplaced total line")
            saw_entry = True
            continue
        match = _FD_ROW.fullmatch(line)
        if not match:
            raise ValueError("fd links input contains a malformed line")
        saw_entry = True
        mode = match.group("mode")
        target = match.group("target")
        if (mode[0] == "l") != (target is not None):
            raise ValueError("fd links input has inconsistent symlink metadata")
        if target is not None and any(ord(char) < 0x20 or ord(char) == 0x7f for char in target):
            raise ValueError("fd links input contains an invalid link target")
        if target == "/dev/kbus0":
            kbus0_present = True
    if not saw_entry:
        raise ValueError("fd links input contains no listing")
    return kbus0_present


def _parse_task_names(text: str) -> dict[str, int]:
    counts = {name: 0 for name in _TASK_CLASSES}
    for line in _required_lines(text, "task names"):
        if not _TASK_TEXT.fullmatch(line):
            raise ValueError("task names input contains an invalid comm name")
        for class_name, pattern in _TASK_CLASS_PATTERNS.items():
            if pattern.fullmatch(line):
                counts[class_name] += 1
                break
    return counts


def _parse_cwd(text: str) -> bool:
    # readlink-style snapshot files conventionally end with one record newline.
    if text.endswith("\r\n"):
        text = text[:-2]
    elif text.endswith("\n"):
        text = text[:-1]
    if "\n" in text or "\r" in text or not text.startswith("/"):
        raise ValueError("cwd input is malformed")
    if any(ord(char) < 0x20 or ord(char) == 0x7f for char in text):
        raise ValueError("cwd input is malformed")
    return text.endswith(" (deleted)")


def summarize_runtime(
    maps_text: Optional[str],
    fd_links_text: Optional[str],
    task_names_text: Optional[str],
    cwd_text: Optional[str],
) -> dict:
    """Summarize explicitly supplied proc snapshot text without leaking it.

    A missing input is represented by ``None``. Its derived fields remain
    ``None`` and carry ``OFFEN`` evidence status instead of implying absence.
    Malformed supplied input raises ``ValueError`` and produces no summary.
    """
    maps_text = _validate_text(maps_text, MAX_MAPS_BYTES, "maps")
    fd_links_text = _validate_text(fd_links_text, MAX_FD_BYTES, "fd links")
    task_names_text = _validate_text(task_names_text, MAX_TASK_BYTES, "task names")
    cwd_text = _validate_text(cwd_text, MAX_CWD_BYTES, "cwd")

    libraries = uio_mapping = kbus0_fd = task_counts = deleted_cwd = None
    if maps_text is not None:
        libraries, uio_mapping = _parse_maps(maps_text)
    if fd_links_text is not None:
        kbus0_fd = _parse_fd_links(fd_links_text)
    if task_names_text is not None:
        task_counts = _parse_task_names(task_names_text)
    if cwd_text is not None:
        if not cwd_text:
            raise ValueError("cwd input is empty")
        deleted_cwd = _parse_cwd(cwd_text)

    return {
        "inventory": "OFFEN",
        "communication": "OFFEN",
        "integration_qualification": False,
        "observations": {
            "components": {
                "evidence": "component_observed" if libraries else "OFFEN",
                "libraries": libraries,
            },
            "endpoints": {
                "evidence": "endpoint_observed" if kbus0_fd is True or uio_mapping is True else "OFFEN",
                "kbus0_fd_present": kbus0_fd,
                "uio_mapping_present": uio_mapping,
            },
            "threads": {
                "evidence": "thread_observed" if task_counts and any(task_counts.values()) else "OFFEN",
                "counts": task_counts,
            },
            "cwd": {
                "evidence": "cwd_observed" if deleted_cwd is not None else "OFFEN",
                "deleted": deleted_cwd,
            },
        },
    }


def _read_optional(path: Optional[str], limit: int) -> Optional[str]:
    if path is None:
        return None
    try:
        resolved = os.path.realpath(path)
        if any(os.path.commonpath((root, resolved)) == root for root in ("/proc", "/sys", "/dev")):
            raise ValueError("procfs, sysfs, and device paths are not accepted")
        before_open = os.stat(resolved)
        if not stat.S_ISREG(before_open.st_mode):
            raise ValueError("input must be a regular offline file")
        flags = os.O_RDONLY | getattr(os, "O_NONBLOCK", 0) | getattr(os, "O_NOFOLLOW", 0)
        fd = os.open(resolved, flags)
        try:
            after_open = os.fstat(fd)
            if not stat.S_ISREG(after_open.st_mode):
                raise ValueError("input must be a regular offline file")
            if (before_open.st_dev, before_open.st_ino) != (after_open.st_dev, after_open.st_ino):
                raise ValueError("input changed during open")
            stream = os.fdopen(fd, "rb")
            fd = -1
            with stream:
                data = stream.read(limit + 1)
        finally:
            if fd >= 0:
                os.close(fd)
    except ValueError:
        raise
    except OSError:
        raise ValueError("an input file could not be read") from None
    if len(data) > limit:
        raise ValueError("an input file exceeds the size limit")
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        raise ValueError("an input file is not UTF-8 text") from None


def main(argv: Optional[list[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--maps", help="previously captured maps text file")
    parser.add_argument("--fd-links", help="previously captured fd listing text file")
    parser.add_argument("--task-names", help="previously captured task-name text file")
    parser.add_argument("--cwd", help="previously captured cwd text file")
    args = parser.parse_args(argv)
    try:
        result = summarize_runtime(
            _read_optional(args.maps, MAX_MAPS_BYTES),
            _read_optional(args.fd_links, MAX_FD_BYTES),
            _read_optional(args.task_names, MAX_TASK_BYTES),
            _read_optional(args.cwd, MAX_CWD_BYTES),
        )
    except ValueError as exc:
        print("runtime observation rejected: %s" % exc, file=sys.stderr)
        return 2
    print(json.dumps(result, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
