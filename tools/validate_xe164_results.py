"""Validate the public result snapshots without private inputs or hardware."""
from pathlib import Path
import csv
import hashlib
import io
import json
import re

ROOT = Path(__file__).resolve().parents[1]
SNAPSHOTS = ROOT / "analysis" / "xe164" / "results"
FORBIDDEN = (
    r"(?<![A-Za-z0-9_.-])/(?:home|tmp|root)/",
    r"(?i)[A-Z]:[\\/](?:Users|Temp)[\\/]",
    r"\b(?:192\.168\.\d{1,3}\.\d{1,3}|10\.(?:\d{1,3}\.){2}\d{1,3}|172\.(?:1[6-9]|2\d|3[01])\.\d{1,3}\.\d{1,3})\b",
    r"(?i)\b(?:[0-9a-f]{2}:){5}[0-9a-f]{2}\b",
    r"(?i)(?:github_pat_|ghp_|sk-proj-|BEGIN [A-Z ]*PRIVATE KEY)",
    r"(?m)^\s*(?:0x)?[0-9a-fA-F]{4,8}:\s+(?:stmdb|ldr|str|cmp|mov|bl|bx)\b",
)

def check(snapshot):
    manifest = json.loads((snapshot / "export-manifest.json").read_text())
    if manifest["schema"] != 1:
        raise ValueError("Unsupported result snapshot schema")
    records = manifest["files"]
    allowed = {"README.md", "handoff.md", "export-manifest.json"}
    paths = set()
    for record in records:
        relative = Path(record["export_path"])
        if relative.is_absolute() or ".." in relative.parts:
            raise ValueError("Export path escapes snapshot")
        if str(relative) in paths:
            raise ValueError("Duplicate export path")
        paths.add(str(relative))
        path = snapshot / relative
        if path.suffix not in {".md", ".csv", ".tsv"} or path.is_symlink():
            raise ValueError("Unexpected input artifact in result snapshot")
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != record["export_sha256"]:
            raise ValueError(f"Export hash mismatch: {relative}")
        if not re.fullmatch(r"[0-9a-f]{64}", record["source_sha256"]):
            raise ValueError("Invalid original identity")
    actual = {str(p.relative_to(snapshot)) for p in snapshot.rglob("*") if p.is_file()}
    if actual != paths | allowed:
        raise ValueError("Unmanifested or missing result files")
    index = (snapshot / "evidence/index.md").read_text()
    ids = re.findall(r"^\| (E-XE164-\d+) \|", index, re.M)
    if len(ids) != len(set(ids)) or len(ids) != manifest["evidence_count"]:
        raise ValueError("Evidence count/uniqueness mismatch")
    rows = list(csv.reader(io.StringIO((snapshot / "notes/function-map.csv").read_text())))
    if len(rows) - 1 != manifest["function_map_rows"]:
        raise ValueError("Function row count mismatch")
    if not all(len(row) == manifest["function_map_columns"] for row in rows):
        raise ValueError("Function schema mismatch")
    for row in rows[1:]:
        for eid in re.findall(r"E-XE164-\d+", ",".join(row)):
            if eid not in ids:
                raise ValueError(f"Missing evidence reference: {eid}")
    if sum(r["kind"] == "report" for r in records) != manifest["report_count"]:
        raise ValueError("Report count mismatch")
    for relative in sorted(actual):
        path = snapshot / relative
        if path.is_symlink():
            raise ValueError("Snapshot contains a symlink")
        text = path.read_text(encoding="utf-8")
        if "\x00" in text or any(re.search(pattern, text) for pattern in FORBIDDEN):
            raise ValueError(f"Unexpected private/raw content: {relative}")
    print(f"PASS {snapshot.name}: {len(ids)} evidence IDs, {len(rows)-1} function rows, "
          f"{manifest['report_count']} reports, {len(records)} export hashes; "
          "public snapshot integrity only")

if __name__ == "__main__":
    manifests = sorted(SNAPSHOTS.glob("*/export-manifest.json"))
    if not manifests:
        raise SystemExit("No public result snapshot found")
    for file in manifests:
        check(file.parent)
