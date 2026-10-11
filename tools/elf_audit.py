#!/usr/bin/env python3
"""Static inspection of explicitly supplied regular ELF files. NEVER executes them.

Only trusted host readelf runs. No ldd, ptrace, /dev, package scripts or network.
The report shows ELF dependencies/symbol references, not dynamic call evidence.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import tempfile

MAX_FILE = 256 * 1024 * 1024
PATTERN = re.compile(r"adi_|dal_|[Kk][Bb]us|[Ii]o[Dd]rv|TscTime|Retain|[Dd]rm|clock_gettime|ioctl|mmap|dlopen")
SYMBOL_TABLE = re.compile(r"^Symbol table '([^']+)' contains", re.M)
SYMBOL_ROW = re.compile(
    r"^\s*\d+:\s+([0-9a-fA-F]+)\s+((?:0[xX][0-9a-fA-F]+|\d+))\s+(\S+)\s+\S+\s+\S+\s+(\S+)(?:\s+(.*?))?\s*$"
)
INTERPRETER = re.compile(
    r"^\s*\[Requesting program interpreter:\s*(.*?)\]\s*$", re.M
)
DYNAMIC_PATH = re.compile(
    r"^\s*0x[0-9a-fA-F]+\s+\((RPATH|RUNPATH)\)\s+"
    r"Library (?:rpath|runpath):\s*\[(.*?)\]\s*$", re.M
)


def parse_interpreter(text: str) -> str | None:
    """Return the PT_INTERP string declared in readelf -l output, if present."""
    match = INTERPRETER.search(text)
    return match.group(1) if match else None


def parse_search_paths(text: str) -> dict[str, list[str]]:
    """Return declared DT_RPATH and DT_RUNPATH colon-separated components.

    These are raw ELF declarations. Empty components are preserved, and no
    loader lookup, variable expansion, or path resolution is attempted.
    """
    paths = {"rpath": [], "runpath": []}
    for match in DYNAMIC_PATH.finditer(text):
        key = match.group(1).lower()
        paths[key].extend(match.group(2).split(":"))
    return paths

def parse_function_symbols(text: str) -> list[dict]:
    """Parse defined ELF function symbols from wide readelf -s output.

    Values and sizes are the symbol table's declared fields. `value` is the raw
    ELF symbol value, not a runtime address or normalized ARM/Thumb code
    address. A zero size makes no range claim, and no neighboring symbol is
    used to infer one.
    """
    table = None
    symbols = []
    for line in text.splitlines():
        table_match = SYMBOL_TABLE.match(line)
        if table_match:
            table = table_match.group(1)
            continue
        if table is None:
            continue
        row = SYMBOL_ROW.match(line)
        if not row:
            continue
        value, size, symbol_type, section_index, name = row.groups()
        if symbol_type not in {"FUNC", "IFUNC", "GNU_IFUNC"} or section_index == "UND":
            continue
        symbols.append({
            "table": table,
            "name": (name or "").strip(),
            "value": int(value, 16),
            "size": int(size, 16) if size.lower().startswith("0x") else int(size, 10),
            "section_index": section_index,
            "type": symbol_type,
        })
    return symbols

def inspect(path: str) -> dict:
    p = Path(path).absolute()
    # Reject known special paths before opening, then recheck the actual fd:
    # a concurrently replaced pathname must never make us read a device/FIFO.
    st = p.lstat()
    if not stat.S_ISREG(st.st_mode):
        raise ValueError("only explicit regular, non-symlink files are allowed")
    if st.st_size > MAX_FILE:
        raise ValueError("ELF exceeds 256 MiB inspection bound")
    try:
        metadata_fd = os.open(p, os.O_PATH | os.O_NOFOLLOW)
    except OSError as exc:
        raise ValueError("cannot open a stable regular, non-symlink file") from exc
    try:
        st = os.fstat(metadata_fd)
        if not stat.S_ISREG(st.st_mode):
            raise ValueError("only explicit regular, non-symlink files are allowed")
        if st.st_size > MAX_FILE:
            raise ValueError("ELF exceeds 256 MiB inspection bound")
        # O_PATH takes an inode reference without invoking device open methods.
        # Reopen only this verified regular inode, never the mutable source path.
        fd = os.open(f"/proc/self/fd/{metadata_fd}", os.O_RDONLY | os.O_NONBLOCK)
        try:
            chunks, count = [], 0
            while True:
                chunk = os.read(fd, min(1024 * 1024, MAX_FILE + 1 - count))
                if not chunk:
                    break
                chunks.append(chunk)
                count += len(chunk)
                if count > MAX_FILE:
                    raise ValueError("ELF exceeds 256 MiB inspection bound")
            data = b"".join(chunks)
        finally:
            os.close(fd)
    finally:
        os.close(metadata_fd)
    if len(data) < 20 or data[:4] != b"\x7fELF":
        raise ValueError("not an ELF file")
    readelf = shutil.which("readelf")
    if readelf is None:
        raise ValueError("BLOCKED: host binutils/readelf missing")
    # Analyze a private snapshot of exactly the hashed bytes. The original
    # pathname can change without changing the reported hash/metadata pairing.
    with tempfile.TemporaryDirectory(prefix="virtualwago-elf-") as directory:
        snapshot = Path(directory) / "input.elf"
        snapshot.write_bytes(data)
        cmd = [readelf, "-W", "-h", "-l", "-d", "-s", "-A", "-V", "--", str(snapshot)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                                env={**os.environ, "LC_ALL": "C"}, check=False)
    if result.returncode != 0:
        raise ValueError("readelf rejected ELF: " + result.stderr[:500])
    text = result.stdout
    header = {}
    for key in ("Class", "Data", "Machine", "OS/ABI", "Flags"):
        match = re.search(r"^\s*" + re.escape(key) + r":\s*(.+)$", text, re.M)
        header[key] = match.group(1) if match else None
    search_paths = parse_search_paths(text)
    return {"path": str(p), "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data), "header": header,
            "needed": re.findall(r"\(NEEDED\).*?\[(.*?)\]", text),
            "soname": re.findall(r"\(SONAME\).*?\[(.*?)\]", text),
            "interpreter": parse_interpreter(text),
            "rpath": search_paths["rpath"],
            "runpath": search_paths["runpath"],
            "candidate_symbol_lines": [l.strip() for l in text.splitlines()
                                       if PATTERN.search(l)],
            "defined_function_symbols": parse_function_symbols(text),
            "abi_attributes": [l.strip() for l in text.splitlines() if "Tag_" in l],
            "version_lines": [l.strip() for l in text.splitlines()
                              if "GLIBC_" in l or "GLIBCXX_" in l],
            "scope": "static-only; declared ELF metadata, no loader-resolution claim",
            "runtime_execution": "NOT_RUN"}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+")
    args = parser.parse_args()
    rows, failed = [], False
    for f in args.files:
        try:
            rows.append({"status": "PASS", "inspection": inspect(f)})
        except (OSError, ValueError, subprocess.TimeoutExpired) as e:
            failed = True
            rows.append({"path": f, "status": "BLOCKED" if "BLOCKED:" in str(e) else "FAIL",
                         "reason": str(e)})
    print(json.dumps(rows, indent=2, sort_keys=True))
    return 1 if failed else 0

if __name__ == "__main__":
    raise SystemExit(main())
