#!/usr/bin/env python3
"""Bounded checker for explicit complete-frame vectors on the local V2 bridge.

The plan supplies the expected output bytes as a test oracle. This tool does
not embed IEC logic, open output permit, use network sockets, or prove which
runtime/consumer produced the observed frames.
"""
from __future__ import annotations

import argparse
import json
import math
import os
from pathlib import Path
import re
import select
import socket
import stat
import sys
import time
from typing import Any

try:
    from tools import native_digital_acceptance as _digital
except ImportError:  # Also support direct execution as ``python tools/...py``.
    import native_digital_acceptance as _digital


PLAN_SCHEMA = "virtualwago.native-frame-plan.v1"
PLAN_KEYS = {"schema", "expected_profile", "input_bytes", "input_bits",
             "output_bytes", "output_bits", "vectors", "timeout_seconds"}
STATUS_NUMBER_FIELDS = {
    "generation", "input_bytes", "input_bits", "output_bytes", "output_bits",
    "initialized", "opened", "configured", "running", "permit", "watchdog",
    "fault", "read_active", "write_active", "write_failed", "frames",
}
STATUS_HEX_FIELDS = {"input", "latch", "requested", "staged", "coverage", "effective"}
STATUS_FIELDS = STATUS_NUMBER_FIELDS | STATUS_HEX_FIELDS
STATUS_BOOLEAN_FIELDS = {"initialized", "opened", "configured", "running",
                         "permit", "watchdog", "fault", "read_active",
                         "write_active", "write_failed"}
UINT64_MAX = (1 << 64) - 1
UINT32_MAX = (1 << 32) - 1
MAX_FRAME_BYTES = 256
MAX_VECTORS = 64
MAX_PACKET_BYTES = 4096
MAX_REQUEST_BYTES = 600
MAX_TIMEOUT_SECONDS = _digital.MAX_TIMEOUT_SECONDS
DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)\Z", re.ASCII)
PROFILE = re.compile(r"[A-Z][A-Z0-9_-]{0,31}\Z", re.ASCII)
HEX_FRAME = re.compile(r"(?:[0-9a-f]{2})*\Z", re.ASCII)


AcceptanceError = _digital.AcceptanceError
_fail = _digital._fail
_blocked = _digital._blocked
_remaining = _digital._remaining


def _uint(value: Any, name: str, maximum: int) -> int:
    if type(value) is not int or value < 0 or value > maximum:
        raise _fail("INVALID_PLAN", name + " must be an unsigned integer in range.")
    return value


def validate_plan(plan: Any) -> dict[str, Any]:
    if type(plan) is not dict or set(plan) != PLAN_KEYS:
        raise _fail("INVALID_PLAN", "Plan must contain the exact required field set.")
    if plan["schema"] != PLAN_SCHEMA:
        raise _fail("INVALID_PLAN", "Plan schema is unsupported.")
    profile = plan["expected_profile"]
    if type(profile) is not str or PROFILE.fullmatch(profile) is None:
        raise _fail("INVALID_PLAN", "expected_profile must be a canonical profile identifier.")
    input_bytes = _uint(plan["input_bytes"], "input_bytes", MAX_FRAME_BYTES)
    output_bytes = _uint(plan["output_bytes"], "output_bytes", MAX_FRAME_BYTES)
    input_bits = _uint(plan["input_bits"], "input_bits", MAX_FRAME_BYTES * 8)
    output_bits = _uint(plan["output_bits"], "output_bits", MAX_FRAME_BYTES * 8)
    if min(input_bytes, output_bytes, input_bits, output_bits) <= 0:
        raise _fail("INVALID_PLAN", "Frame extents must be positive.")
    if input_bits > input_bytes * 8 or output_bits > output_bytes * 8:
        raise _fail("INVALID_PLAN", "Bit extents exceed their byte frames.")
    timeout = plan["timeout_seconds"]
    if (type(timeout) not in (int, float) or timeout <= 0
            or timeout > MAX_TIMEOUT_SECONDS or not math.isfinite(timeout)):
        raise _fail("INVALID_TIMEOUT", "Timeout must be finite, positive, and no greater than 60 seconds.")
    vectors = plan["vectors"]
    if type(vectors) is not list or not 1 <= len(vectors) <= MAX_VECTORS:
        raise _fail("INVALID_PLAN", "vectors must contain 1..64 complete frames.")
    normalized = []
    seen_inputs = set()
    for index, vector in enumerate(vectors):
        if type(vector) is not dict or set(vector) != {"input_hex", "expected_output_hex"}:
            raise _fail("INVALID_PLAN", "Each vector must contain only input_hex and expected_output_hex.")
        input_hex, output_hex = vector["input_hex"], vector["expected_output_hex"]
        if type(input_hex) is not str or HEX_FRAME.fullmatch(input_hex) is None:
            raise _fail("INVALID_PLAN", "Vector input_hex must be lowercase complete-byte hex.")
        if type(output_hex) is not str or HEX_FRAME.fullmatch(output_hex) is None:
            raise _fail("INVALID_PLAN", "Vector expected_output_hex must be lowercase complete-byte hex.")
        if len(input_hex) != input_bytes * 2 or len(output_hex) != output_bytes * 2:
            raise _fail("INVALID_PLAN", "Vector frame length does not match configured extents.")
        if input_hex in seen_inputs:
            raise _fail("INVALID_PLAN", "Vector inputs must be unique.")
        seen_inputs.add(input_hex)
        request_length = len("V2 INPUT %s %d %d %s" %
                             (profile, UINT64_MAX, input_bytes, input_hex))
        if request_length > MAX_REQUEST_BYTES:
            raise _fail("INVALID_PLAN", "V2 INPUT request exceeds the bridge request bound.")
        normalized.append({"input_hex": input_hex,
                           "expected_output_hex": output_hex,
                           "index": index})
    return {
        "schema": PLAN_SCHEMA, "expected_profile": profile,
        "input_bytes": input_bytes, "input_bits": input_bits,
        "output_bytes": output_bytes, "output_bits": output_bits,
        "vectors": normalized, "timeout_seconds": float(timeout),
    }


def _load_plan(path: str) -> dict[str, Any]:
    try:
        info = os.lstat(path)
    except OSError as exc:
        raise _blocked("PLAN_UNAVAILABLE", "Private JSON plan is unavailable.") from exc
    if (stat.S_ISLNK(info.st_mode) or not stat.S_ISREG(info.st_mode)
            or info.st_uid != os.geteuid() or stat.S_IMODE(info.st_mode) != 0o600):
        raise _blocked("UNSAFE_PLAN", "Plan must be a user-owned regular file with mode 0600.")
    try:
        parent_info = os.stat(os.path.dirname(os.path.abspath(path)), follow_symlinks=False)
    except OSError as exc:
        raise _blocked("UNSAFE_PLAN", "Plan parent directory is unavailable.") from exc
    if (stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode)
            or parent_info.st_uid != os.geteuid() or stat.S_IMODE(parent_info.st_mode) != 0o700):
        raise _blocked("UNSAFE_PLAN", "Plan parent directory must be user-owned with mode 0700.")
    try:
        with open(path, "r", encoding="utf-8") as stream:
            plan = json.load(stream, object_pairs_hook=_unique_json_object)
    except (OSError, ValueError) as exc:
        raise _fail("INVALID_PLAN", "Private JSON plan could not be parsed.") from exc
    return validate_plan(plan)


def _unique_json_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("duplicate JSON object key")
        result[key] = value
    return result


def parse_v2_status(response: str) -> dict[str, Any]:
    if response == "NOT_READY":
        raise _blocked("NOT_READY", "ADI model bridge reports NOT_READY.")
    if response.startswith("ERR "):
        raise _fail("BRIDGE_ERROR", "ADI model bridge returned an ERR response.")
    if not response.startswith("V2 STATUS "):
        raise _fail("UNKNOWN_RESPONSE", "Bridge returned an unknown V2 response.")
    tokens = response.split(" ")
    if len(tokens) < 4 or tokens[0:2] != ["V2", "STATUS"]:
        raise _fail("MALFORMED_STATUS", "V2 STATUS header is malformed.")
    profile = tokens[2]
    if PROFILE.fullmatch(profile) is None:
        raise _fail("MALFORMED_STATUS", "V2 STATUS profile is malformed.")
    fields: dict[str, Any] = {}
    for token in tokens[3:]:
        if not token or token.count("=") != 1:
            raise _fail("MALFORMED_STATUS", "V2 STATUS contains a malformed field.")
        name, value = token.split("=", 1)
        if name not in STATUS_FIELDS:
            raise _fail("UNKNOWN_STATUS_FIELD", "V2 STATUS contains an unknown field.")
        if name in fields:
            raise _fail("DUPLICATE_STATUS_FIELD", "V2 STATUS contains a duplicate field.")
        if name in STATUS_NUMBER_FIELDS:
            if DECIMAL.fullmatch(value) is None:
                raise _fail("INVALID_STATUS_VALUE", "V2 STATUS contains a non-canonical unsigned integer.")
            maximum = UINT64_MAX if name in ("generation", "frames") else UINT32_MAX
            parsed = int(value)
            if parsed > maximum or (name in STATUS_BOOLEAN_FIELDS and parsed not in (0, 1)):
                raise _fail("STATUS_VALUE_RANGE", "V2 STATUS contains an out-of-range value.")
            fields[name] = parsed
        else:
            if HEX_FRAME.fullmatch(value) is None:
                raise _fail("INVALID_STATUS_HEX", "V2 STATUS frame is not canonical lowercase byte hex.")
            fields[name] = value
    if set(fields) != STATUS_FIELDS:
        raise _fail("MISSING_STATUS_FIELDS", "V2 STATUS does not contain the exact field set.")
    fields["profile"] = profile
    for name in ("input", "latch"):
        if len(fields[name]) != fields["input_bytes"] * 2:
            raise _fail("STATUS_FRAME_LENGTH", "V2 STATUS input frame length disagrees with input_bytes.")
    for name in ("requested", "staged", "coverage", "effective"):
        if len(fields[name]) != fields["output_bytes"] * 2:
            raise _fail("STATUS_FRAME_LENGTH", "V2 STATUS output frame length disagrees with output_bytes.")
    return fields


def _send_receive(client: socket.socket, request: str, deadline: float) -> str:
    payload = request.encode("ascii")
    if len(payload) > MAX_REQUEST_BYTES:
        raise _fail("REQUEST_TOO_LARGE", "Bridge request exceeded its protocol bound.")
    _, writable, exceptional = select.select([], [client], [client], _remaining(deadline))
    if exceptional or not writable:
        raise _blocked("TIMEOUT", "Timed out waiting to send a bridge request.")
    try:
        sent = client.send(payload)
    except OSError as exc:
        raise _blocked("DISCONNECT", "Bridge disconnected while sending a request.") from exc
    if sent != len(payload):
        raise _blocked("SHORT_SEND", "Bridge request was not sent as one complete packet.")
    ready, _, exceptional = select.select([client], [], [client], _remaining(deadline))
    if exceptional:
        raise _blocked("DISCONNECT", "Bridge reported a socket error.")
    if not ready:
        raise _blocked("TIMEOUT", "Timed out waiting for a bridge response.")
    try:
        response, _, flags, _ = client.recvmsg(MAX_PACKET_BYTES)
    except OSError as exc:
        raise _blocked("DISCONNECT", "Bridge disconnected while receiving a response.") from exc
    if flags & getattr(socket, "MSG_TRUNC", 0):
        raise _fail("OVERSIZED_RESPONSE", "Bridge packet exceeded the 4096-byte receive bound.")
    if not response:
        raise _blocked("DISCONNECT", "Bridge closed the connection.")
    if len(response) > MAX_PACKET_BYTES:
        raise _fail("OVERSIZED_RESPONSE", "Bridge packet exceeded the 4096-byte receive bound.")
    try:
        return response.decode("ascii")
    except UnicodeDecodeError as exc:
        raise _fail("NON_ASCII_RESPONSE", "Bridge response was not ASCII.") from exc


def _status(client: socket.socket, deadline: float) -> dict[str, Any]:
    return parse_v2_status(_send_receive(client, "V2 STATUS", deadline))


def _validate_status(status: dict[str, Any], plan: dict[str, Any],
                     generation: int | None = None) -> None:
    if status["profile"] != plan["expected_profile"]:
        raise _blocked("PROFILE_MISMATCH", "Bridge profile differs from the explicit plan.")
    for name in ("input_bytes", "input_bits", "output_bytes", "output_bits"):
        if status[name] != plan[name]:
            raise _blocked("EXTENT_MISMATCH", "Bridge extent differs from the explicit plan: " + name)
    if generation is not None and status["generation"] != generation:
        raise _blocked("GENERATION_CHANGED", "Bridge lifecycle generation changed during acceptance.")
    if status["permit"] != 0:
        raise _fail("PERMIT_ALREADY_OPEN", "Model output permit is not zero; checker did not change it.")
    if status["effective"] != "00" * plan["output_bytes"]:
        raise _fail("EFFECTIVE_OUTPUT_NONZERO", "Effective output frame is not all zero.")
    if status["fault"] != 0:
        raise _blocked("MODEL_FAULT", "Model fault is latched.")
    if not all(status[name] == 1 for name in
               ("initialized", "opened", "configured", "running", "watchdog")):
        raise _blocked("MODEL_NOT_RUNNING", "Bridge is not initialized, opened, configured, running, and watchdog-healthy.")


def run_acceptance(socket_path: str, plan_value: dict[str, Any]) -> dict[str, Any]:
    started = time.monotonic()
    raw_profile = plan_value.get("expected_profile") if type(plan_value) is dict else None
    raw_input_bytes = plan_value.get("input_bytes") if type(plan_value) is dict else None
    raw_output_bytes = plan_value.get("output_bytes") if type(plan_value) is dict else None
    raw_timeout = plan_value.get("timeout_seconds") if type(plan_value) is dict else None
    profile = raw_profile if type(raw_profile) is str else None
    input_bytes = raw_input_bytes if type(raw_input_bytes) is int and raw_input_bytes >= 0 else None
    output_bytes = raw_output_bytes if type(raw_output_bytes) is int and raw_output_bytes >= 0 else None
    if (type(raw_timeout) in (int, float) and raw_timeout > 0
            and raw_timeout <= MAX_TIMEOUT_SECONDS and math.isfinite(raw_timeout)):
        timeout = float(raw_timeout)
    else:
        timeout = None
    evidence: dict[str, Any] = {
        "schema": "virtualwago.native-frame-acceptance.v1", "status": "NOT_RUN",
        "scope": "local AF_UNIX SOCK_SEQPACKET V2 bridge checker; no runtime provenance or physical I/O proof",
        "external_runtime_binding": "REQUIRED; not established by this checker",
        "clock": "host monotonic observation timestamps; no IEC or real-time semantics claimed",
        "configuration": {"expected_profile": profile, "input_bytes": input_bytes,
                           "output_bytes": output_bytes, "timeout_seconds": timeout,
                           "vector_count": (len(plan_value.get("vectors", []))
                                            if type(plan_value) is dict
                                            and type(plan_value.get("vectors")) is list else None),
                           "output_permit_command_sent": False},
        "started_monotonic_seconds": started, "samples": [],
    }
    client = None
    try:
        plan = validate_plan(plan_value)
        evidence["configuration"].update({
            "expected_profile": plan["expected_profile"],
            "input_bytes": plan["input_bytes"], "input_bits": plan["input_bits"],
            "output_bytes": plan["output_bytes"], "output_bits": plan["output_bits"],
            "timeout_seconds": plan["timeout_seconds"], "vectors": plan["vectors"],
        })
        deadline = started + plan["timeout_seconds"]
        safe_path = _digital._validate_socket_path(socket_path)
        _remaining(deadline)
        client = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        client.setblocking(False)
        try:
            client.connect(safe_path)
        except BlockingIOError:
            pass
        except OSError as exc:
            raise _blocked("CONNECT_FAILED", "Could not connect to local V2 bridge socket.") from exc
        _, writable, exceptional = select.select([], [client], [client], _remaining(deadline))
        if exceptional or not writable or client.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR):
            raise _blocked("CONNECT_FAILED", "Local V2 bridge connection did not complete.")

        baseline = _status(client, deadline)
        _validate_status(baseline, plan)
        generation = baseline["generation"]
        last_frames = baseline["frames"]
        previous_latch = baseline["latch"]
        evidence["baseline"] = baseline
        for vector in plan["vectors"]:
            request = "V2 INPUT %s %d %d %s" % (
                plan["expected_profile"], generation, plan["input_bytes"], vector["input_hex"])
            reply = _send_receive(client, request, deadline)
            if reply.startswith("ERR "):
                raise _fail("BRIDGE_ERROR", "Bridge rejected a complete input frame.")
            if reply != "OK FRAME":
                if reply == "NOT_READY":
                    raise _blocked("NOT_READY", "Bridge became NOT_READY after frame submission.")
                raise _fail("INPUT_RESPONSE", "Bridge returned an unexpected V2 INPUT response.")

            # Record a status watermark after the exact frame ACK. A frame
            # completed before this observation can never qualify a sample.
            watermark = _status(client, deadline)
            _validate_status(watermark, plan, generation)
            if watermark["frames"] < last_frames:
                raise _fail("FRAME_COUNTER_REGRESSED", "Bridge frame counter regressed.")
            if watermark["input"] != vector["input_hex"]:
                raise _fail("INPUT_WATERMARK_MISMATCH", "Post-ACK status did not contain the submitted input frame.")
            if previous_latch == vector["input_hex"]:
                raise _blocked("INPUT_LATCH_NOT_DISTINGUISHABLE",
                               "Submitted input matches the prior read latch; a fresh input latch cannot be established.")
            last_frames = watermark["frames"]

            sample = None
            fresh_wrong_output = None
            latch_watermark = None
            try:
                while sample is None:
                    current = _status(client, deadline)
                    _validate_status(current, plan, generation)
                    if current["frames"] < last_frames:
                        raise _fail("FRAME_COUNTER_REGRESSED", "Bridge frame counter regressed.")
                    if current["input"] == vector["input_hex"] and current["latch"] == vector["input_hex"]:
                        if latch_watermark is None:
                            # A successful write must follow a newly observed read latch. This
                            # excludes an in-flight output commit based on the previous input.
                            latch_watermark = current["frames"]
                        elif current["frames"] > latch_watermark:
                            if current["requested"] == vector["expected_output_hex"]:
                                sample = current
                            else:
                                fresh_wrong_output = current
                    elif current["input"] == vector["input_hex"]:
                        # The V2 setter changes input_signals immediately, while ReadStart
                        # refreshes read_latch separately. Do not treat the old latch as a sample.
                        pass
                    last_frames = current["frames"]
                    if sample is None:
                        remaining = _remaining(deadline)
                        time.sleep(min(0.01, remaining))
            except AcceptanceError as exc:
                if exc.code == "TIMEOUT" and fresh_wrong_output is not None:
                    raise _fail("OUTPUT_MISMATCH", "Fresh complete frames did not match the explicit output oracle.") from exc
                raise
            evidence["samples"].append({
                "vector_index": vector["index"], "input_hex": vector["input_hex"],
                "expected_output_hex": vector["expected_output_hex"],
                "observed_requested_hex": sample["requested"],
                "observed_effective_hex": sample["effective"],
                "generation": sample["generation"], "frames": sample["frames"],
                "post_ack_watermark_frames": watermark["frames"],
                "post_latch_watermark_frames": latch_watermark,
                "accepted_monotonic_seconds": time.monotonic(),
            })
            previous_latch = sample["latch"]
        evidence["status"] = "PASS"
    except AcceptanceError as exc:
        evidence["status"] = exc.status
        evidence["failure"] = {"code": exc.code, "message": exc.message}
    except OSError:
        evidence["status"] = "BLOCKED"
        evidence["failure"] = {"code": "LOCAL_SOCKET_ERROR", "message": "Local socket operation failed."}
    finally:
        if client is not None:
            try:
                client.close()
            except OSError:
                pass
    finished = time.monotonic()
    evidence["finished_monotonic_seconds"] = finished
    evidence["duration_seconds"] = finished - started
    return evidence


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True, help="local private AF_UNIX bridge socket")
    parser.add_argument("--plan", required=True, help="user-owned 0600 JSON vector plan")
    parser.add_argument("--evidence", help="write evidence JSON to a new file with mode 0600")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        plan = _load_plan(args.plan)
        evidence = run_acceptance(args.socket, plan)
    except AcceptanceError as exc:
        now = time.monotonic()
        evidence = {"schema": "virtualwago.native-frame-acceptance.v1",
                    "status": exc.status, "failure": {"code": exc.code, "message": exc.message},
                    "scope": "local V2 transport checker; no runtime or physical I/O proof",
                    "external_runtime_binding": "REQUIRED; not established by this checker",
                    "clock": "host monotonic observation timestamps; no IEC or real-time semantics claimed",
                    "configuration": {"expected_profile": None, "input_bytes": None,
                                       "output_bytes": None, "timeout_seconds": None,
                                       "vectors": [], "output_permit_command_sent": False},
                    "started_monotonic_seconds": now,
                    "finished_monotonic_seconds": now, "duration_seconds": 0.0,
                    "samples": []}
    serialized = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if args.evidence:
        target = Path(args.evidence)
        try:
            parent_info = os.stat(str(target.parent.resolve()), follow_symlinks=False)
        except OSError as exc:
            raise _blocked("UNSAFE_EVIDENCE_PATH", "Evidence parent directory is unavailable.") from exc
        if (stat.S_ISLNK(parent_info.st_mode) or not stat.S_ISDIR(parent_info.st_mode)
                or parent_info.st_uid != os.geteuid() or stat.S_IMODE(parent_info.st_mode) != 0o700):
            raise _blocked("UNSAFE_EVIDENCE_PATH", "Evidence parent directory must be user-owned with mode 0700.")
        fd = os.open(target, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(serialized)
    else:
        sys.stdout.write(serialized)
    return 0 if evidence["status"] == "PASS" else 1 if evidence["status"] == "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
