#!/usr/bin/env python3
"""Summarize byte coverage from a private CODESYS I/O mapping CSV.

The summary keeps device names and address coverage, but deliberately omits
mapped IEC variable names and descriptions. It is an offline parser and never
opens CODESYS or contacts a controller.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path
import re


ADDRESS = re.compile(r"^%([IQ])([XBWDL])(\d+)(?:\.(\d+))?$")
WIDTH_BYTES = {"X": 1, "B": 1, "W": 2, "D": 4, "L": 8}


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


def read_rows(path):
    rows = []
    with Path(path).open("r", encoding="utf-8-sig", newline="") as stream:
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


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run(input_path, output_path):
    source = Path(input_path)
    output = Path(output_path)
    if not source.is_file():
        fail("input CSV does not exist")
    if output.exists():
        fail("refusing to overwrite an existing summary")
    report = {
        "schema": "virtualwago-codesys-mapping-summary/1",
        "scope": "offline CSV address coverage; no runtime or hardware proof",
        "source_sha256": digest(source),
        "devices": summarize(read_rows(source)),
    }
    with output.open("x", encoding="utf-8") as stream:
        stream.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = run(args.input, args.output)
    print(json.dumps({"status": "PASS", "source_sha256": report["source_sha256"],
                      "device_direction_count": len(report["devices"])}, sort_keys=True))


if __name__ == "__main__":
    main()
