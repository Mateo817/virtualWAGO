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
        cmd = [readelf, "-W", "-h", "-d", "-s", "-A", "-V", "--", str(snapshot)]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15,
                                env={**os.environ, "LC_ALL": "C"}, check=False)
    if result.returncode != 0:
        raise ValueError("readelf rejected ELF: " + result.stderr[:500])
    text = result.stdout
    header = {}
    for key in ("Class", "Data", "Machine", "OS/ABI", "Flags"):
        match = re.search(r"^\s*" + re.escape(key) + r":\s*(.+)$", text, re.M)
        header[key] = match.group(1) if match else None
    return {"path": str(p), "sha256": hashlib.sha256(data).hexdigest(),
            "bytes": len(data), "header": header,
            "needed": re.findall(r"\(NEEDED\).*?\[(.*?)\]", text),
            "soname": re.findall(r"\(SONAME\).*?\[(.*?)\]", text),
            "candidate_symbol_lines": [l.strip() for l in text.splitlines()
                                       if PATTERN.search(l)],
            "abi_attributes": [l.strip() for l in text.splitlines() if "Tag_" in l],
            "version_lines": [l.strip() for l in text.splitlines()
                              if "GLIBC_" in l or "GLIBCXX_" in l],
            "scope": "static-only; symbol presence does not prove execution/interposition",
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
