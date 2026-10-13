#!/usr/bin/env python3
"""Summarize pinned descriptor channel declarations, never a native bus ABI."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

try:
    from .device_description_audit import AuditError, audit_bytes, _read_stable_regular_file
except ImportError:
    from device_description_audit import AuditError, audit_bytes, _read_stable_regular_file


# IEC scalar widths; these are neither byte offsets nor C struct sizes.
IEC_BITS = {"std:BOOL": 1, "std:BYTE": 8, "std:USINT": 8, "std:SINT": 8,
            "std:WORD": 16, "std:UINT": 16, "std:INT": 16,
            "std:DWORD": 32, "std:UDINT": 32, "std:DINT": 32,
            "std:LWORD": 64, "std:ULINT": 64, "std:LINT": 64}


def summarize(data: bytes, expected_sha256: str) -> dict:
    if not re.fullmatch(r"[0-9a-f]{64}", expected_sha256):
        raise AuditError("expected SHA-256 must be 64 lowercase hex digits")
    audit = audit_bytes(data)
    if audit["sha256"] != expected_sha256:
        raise AuditError("descriptor SHA-256 does not match the supplied pin")
    types = {(t["namespace"] + ":" + t["name"]): t
             for t in audit["local_type_summaries"]}
    channels, configuration = [], []
    totals = {"input": 0, "output": 0}
    unresolved = []
    for parameter in audit["host_parameters"]:
        direction = parameter["attributes"]["channel"]
        row = {"parameter_id": parameter["parameter_id"], "type": parameter["type"],
               "attributes": parameter["attributes"], "default": parameter["default"]}
        if direction not in ("input", "output"):
            if direction != "none":
                raise AuditError("missing or unsupported parameter channel direction")
            configuration.append(row)
            continue
        type_name = parameter["type"]
        bits = IEC_BITS.get(type_name)
        if bits is None and type_name in types:
            declaration = types[type_name]
            if declaration["kind"] == "bitfield":
                bits = IEC_BITS.get(declaration["base_type"])
        row["declared_scalar_bits"] = bits
        row["width_status"] = "VERIFIZIERT" if bits is not None else "OFFEN"
        channels.append(row)
        if bits is None:
            unresolved.append(parameter["parameter_id"])
            totals[direction] = None
        elif totals[direction] is not None:
            totals[direction] += bits
    return {
        "schema": "virtualwago-descriptor-channel-declarations/1",
        "test_status": "PASS", "statement_status": "VERIFIZIERT",
        "sha256": audit["sha256"], "bytes": audit["bytes"],
        "device_identification": audit["device_identification"],
        "device_info": audit["device_info"], "connectors": audit["connectors"],
        "channel_declarations": channels, "configuration_declarations": configuration,
        "declared_scalar_bit_totals": totals, "unresolved_width_parameter_ids": unresolved,
        "native_process_image": "OFFEN", "register_contract": "OFFEN",
        "runtime_test": "NOT_RUN", "hardware_test": "NOT_RUN",
        "scope": "Pinned XML declarations and IEC scalar widths only; totals do not establish packing, offsets, byte order, register replies or module revision",
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("descriptor", type=Path)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args(argv)
    try:
        result = summarize(_read_stable_regular_file(str(args.descriptor)), args.sha256)
    except (OSError, AuditError) as exc:
        print(json.dumps({"test_status": "FAIL", "reason": str(exc)}))
        return 1
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
