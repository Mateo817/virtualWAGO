#!/usr/bin/env python3
"""Bounded local acceptance checker for the existing ADI model bridge.

This checks only bridge status against the two existing IEC XOR probe
contracts. A PASS is transport/checker evidence; it does not prove which
runtime or I/O consumer produced the status. The checker never opens output
permit and never uses network sockets.
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


PROTOCOL_FIELDS = {
    "input", "permit", "requested", "effective", "watchdog", "fault",
    "generation", "frames", "opened", "configured", "running",
}
BOOLEAN_FIELDS = {"permit", "watchdog", "fault", "opened", "configured", "running"}
UINT64_MAX = (1 << 64) - 1
MAX_TIMEOUT_SECONDS = 60.0
PROFILES = {
    "DI8": {"bits": 8, "xor": 0x96, "patterns": (0, 129, 90, 255)},
    "DI16": {"bits": 16, "xor": 0xA596,
             "patterns": (0, 1, 129, 255, 256, 32768, 42390, 65535)},
}
DECIMAL = re.compile(r"(?:0|[1-9][0-9]*)\Z", re.ASCII)


class AcceptanceError(Exception):
    def __init__(self, status: str, code: str, message: str):
        super().__init__(message)
        self.status = status
        self.code = code
        self.message = message


def _fail(code: str, message: str) -> AcceptanceError:
    return AcceptanceError("FAIL", code, message)


def _blocked(code: str, message: str) -> AcceptanceError:
    return AcceptanceError("BLOCKED", code, message)


def _validate_socket_path(socket_path: str) -> str:
    """Require the bridge's private directory/socket shape without symlinks."""
    if not os.path.isabs(socket_path) or "\x00" in socket_path:
        raise _blocked("INVALID_SOCKET_PATH", "Socket path must be absolute.")
    path = Path(socket_path)
    if any(part in (".", "..") for part in path.parts):
        raise _blocked("INVALID_SOCKET_PATH", "Socket path contains a dot component.")

    # lstat each component so no parent or socket symlink is followed.
    cursor = Path("/")
    parts = path.parts[1:]
    if not parts:
        raise _blocked("INVALID_SOCKET_PATH", "Socket path has no filename.")
    for part in parts[:-1]:
        cursor = cursor / part
        try:
            info = os.lstat(cursor)
        except OSError as exc:
            raise _blocked("SOCKET_DIRECTORY_UNAVAILABLE", "Socket directory is unavailable.") from exc
        if stat.S_ISLNK(info.st_mode) or not stat.S_ISDIR(info.st_mode):
            raise _blocked("UNSAFE_SOCKET_PATH", "Socket path has a symlink or non-directory component.")
    try:
        parent_info = os.stat(path.parent, follow_symlinks=False)
        socket_info = os.lstat(path)
    except OSError as exc:
        raise _blocked("SOCKET_UNAVAILABLE", "Socket endpoint is unavailable.") from exc
    if (parent_info.st_uid != os.geteuid() or stat.S_IMODE(parent_info.st_mode) != 0o700):
        raise _blocked("SOCKET_DIRECTORY_PERMISSIONS", "Socket directory must be owned by this user with mode 0700.")
    if stat.S_ISLNK(socket_info.st_mode) or not stat.S_ISSOCK(socket_info.st_mode):
        raise _blocked("UNSAFE_SOCKET_ENDPOINT", "Endpoint is not a non-symlink Unix socket.")
    if socket_info.st_uid != os.geteuid() or stat.S_IMODE(socket_info.st_mode) != 0o600:
        raise _blocked("SOCKET_PERMISSIONS", "Socket must be owned by this user with mode 0600.")
    return os.fspath(path)


def _remaining(deadline: float) -> float:
    remaining = deadline - time.monotonic()
    if remaining <= 0:
        raise _blocked("TIMEOUT", "Whole acceptance run exceeded its monotonic timeout.")
    return remaining


def _send_receive(client: socket.socket, request: str, deadline: float) -> str:
    payload = request.encode("ascii")
    _, writable, _ = select.select([], [client], [], _remaining(deadline))
    if not writable:
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
        response = client.recv(513)
    except OSError as exc:
        raise _blocked("DISCONNECT", "Bridge disconnected while receiving a response.") from exc
    if not response:
        raise _blocked("DISCONNECT", "Bridge closed the connection.")
    if len(response) > 512:
        raise _fail("OVERSIZED_RESPONSE", "Bridge response exceeded 512 bytes.")
    try:
        return response.decode("ascii")
    except UnicodeDecodeError as exc:
        raise _fail("NON_ASCII_RESPONSE", "Bridge response was not ASCII.") from exc


def parse_status(response: str) -> dict[str, int]:
    if response == "NOT_READY":
        raise _blocked("NOT_READY", "ADI model bridge reports NOT_READY.")
    if response.startswith("ERR "):
        raise _fail("BRIDGE_ERROR", "ADI model bridge returned an ERR response.")
    if not response.startswith("STATUS "):
        raise _fail("UNKNOWN_RESPONSE", "Bridge returned an unknown response.")
    fields: dict[str, int] = {}
    for token in response[len("STATUS "):].split(" "):
        if not token or token.count("=") != 1:
            raise _fail("MALFORMED_STATUS", "STATUS response contains a malformed field.")
        name, value = token.split("=", 1)
        if name not in PROTOCOL_FIELDS:
            raise _fail("UNKNOWN_STATUS_FIELD", "STATUS response contains an unknown field.")
        if name in fields:
            raise _fail("DUPLICATE_STATUS_FIELD", "STATUS response contains a duplicate field.")
        if DECIMAL.fullmatch(value) is None:
            raise _fail("INVALID_STATUS_VALUE", "STATUS response contains a non-canonical unsigned integer.")
        parsed = int(value)
        maximum = UINT64_MAX if name in {"generation", "frames"} else 65535
        if parsed > maximum or (name in BOOLEAN_FIELDS and parsed not in (0, 1)):
            raise _fail("STATUS_VALUE_RANGE", "STATUS response contains an out-of-range value.")
        fields[name] = parsed
    if fields.keys() != PROTOCOL_FIELDS:
        raise _fail("MISSING_STATUS_FIELDS", "STATUS response does not contain the exact bridge field set.")
    return fields


def _status(client: socket.socket, deadline: float) -> dict[str, int]:
    response = _send_receive(client, "STATUS", deadline)
    return parse_status(response)


def _validate_ready(status: dict[str, int]) -> None:
    if status["permit"] != 0:
        raise _fail("PERMIT_ALREADY_OPEN", "Model output permit is not zero; checker stopped without changing it.")
    if status["effective"] != 0:
        raise _fail("EFFECTIVE_OUTPUT_NONZERO", "Effective outputs must remain zero for this gated acceptance run.")
    if status["fault"] != 0:
        raise _blocked("MODEL_FAULT", "Model fault is latched.")
    if not all(status[field] == 1 for field in ("opened", "configured", "running", "watchdog")):
        raise _blocked("MODEL_NOT_RUNNING", "Bridge is not opened, configured, running, and watchdog-healthy.")


def run_acceptance(socket_path: str, profile: str, timeout_seconds: float = 10.0) -> dict[str, Any]:
    started = time.monotonic()
    deadline = started + timeout_seconds
    profile_key = profile.upper()
    config = PROFILES.get(profile_key)
    result: dict[str, Any] = {
        "schema": "virtualwago.native-digital-acceptance.v1",
        "status": "NOT_RUN",
        "scope": "local AF_UNIX SOCK_SEQPACKET bridge checker; no runtime provenance or physical I/O proof",
        "external_runtime_binding": "REQUIRED; not established by this checker",
        "configuration": {
            "profile": profile_key,
            "input_bits": config["bits"] if config else None,
            "iec_transform": ("BYTE XOR 16#96" if profile_key == "DI8" else "WORD XOR 16#A596") if config else None,
            "patterns": list(config["patterns"]) if config else [],
            "timeout_seconds": timeout_seconds,
            "output_permit_command_sent": False,
        },
        "clock": "host monotonic; timestamps are observation times, not IEC or real-time semantics",
        "started_monotonic_seconds": started,
        "samples": [],
    }
    client: socket.socket | None = None
    try:
        if config is None:
            raise _fail("INVALID_PROFILE", "Profile must be DI8 or DI16.")
        if (not math.isfinite(timeout_seconds) or timeout_seconds <= 0
                or timeout_seconds > MAX_TIMEOUT_SECONDS):
            raise _fail("INVALID_TIMEOUT", "Timeout must be finite, positive, and no greater than 60 seconds.")
        safe_path = _validate_socket_path(socket_path)
        _remaining(deadline)
        client = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        client.setblocking(False)
        try:
            client.connect(safe_path)
        except BlockingIOError:
            pass
        except OSError as exc:
            raise _blocked("CONNECT_FAILED", "Could not connect to local bridge socket.") from exc
        # AF_UNIX connect is normally immediate; SO_ERROR resolves EINPROGRESS.
        _, writable, exceptional = select.select([], [client], [client], _remaining(deadline))
        if exceptional or not writable:
            raise _blocked("CONNECT_FAILED", "Local bridge connection did not complete.")
        error = client.getsockopt(socket.SOL_SOCKET, socket.SO_ERROR)
        if error:
            raise _blocked("CONNECT_FAILED", "Local bridge connection failed.")

        baseline = _status(client, deadline)
        _validate_ready(baseline)
        generation = baseline["generation"]
        last_observed_frames = baseline["frames"]
        result["baseline"] = baseline
        for pattern in config["patterns"]:
            reply = _send_receive(client, "INPUT %d" % pattern, deadline)
            if reply.startswith("ERR "):
                raise _fail("BRIDGE_ERROR", "Bridge rejected an INPUT request with ERR.")
            if reply != "OK INPUT":
                if reply == "NOT_READY":
                    raise _blocked("NOT_READY", "Bridge became NOT_READY after INPUT.")
                raise _fail("INPUT_RESPONSE", "Bridge returned an unexpected INPUT response.")

            # This STATUS is a post-ack watermark. A frame that completed
            # before this observation must not qualify the new input pattern.
            watermark = _status(client, deadline)
            _validate_ready(watermark)
            if watermark["generation"] != generation:
                raise _blocked("GENERATION_CHANGED", "Bridge generation changed during acceptance.")
            if watermark["frames"] < last_observed_frames:
                raise _fail("FRAME_COUNTER_REGRESSED", "Bridge frame counter regressed.")
            if watermark["input"] != pattern:
                raise _fail("INPUT_WATERMARK_MISMATCH", "Post-ack status did not reflect the accepted input pattern.")
            last_observed_frames = watermark["frames"]

            expected = pattern ^ config["xor"]
            sample = None
            fresh_wrong_output = None
            stale_fresh_frames = 0
            try:
                while sample is None:
                    current = _status(client, deadline)
                    _validate_ready(current)
                    if current["generation"] != generation:
                        raise _blocked("GENERATION_CHANGED", "Bridge generation changed during acceptance.")
                    if current["frames"] < last_observed_frames:
                        raise _fail("FRAME_COUNTER_REGRESSED", "Bridge frame counter regressed.")
                    if current["frames"] > watermark["frames"] and current["input"] == pattern:
                        if current["requested"] == expected:
                            sample = current
                        else:
                            fresh_wrong_output = current
                            stale_fresh_frames += 1
                    last_observed_frames = current["frames"]
                    if sample is None:
                        remaining = _remaining(deadline)
                        time.sleep(min(0.01, remaining))
            except AcceptanceError as exc:
                if exc.code == "TIMEOUT" and fresh_wrong_output is not None:
                    raise _fail("XOR_MISMATCH", "Fresh bridge frames did not match the configured IEC XOR transform.") from exc
                raise
            if sample["permit"] != 0 or sample["effective"] != 0:
                raise _fail("OUTPUT_GATE_VIOLATION", "Permit or effective outputs became nonzero.")
            observed = dict(sample)
            observed.update({
                "pattern": pattern,
                "expected_requested": expected,
                "observed_requested": sample["requested"],
                "post_ack_watermark_frames": watermark["frames"],
                "stale_fresh_frames": stale_fresh_frames,
                "accepted_monotonic_seconds": time.monotonic(),
            })
            result["samples"].append(observed)
        result["status"] = "PASS"
    except AcceptanceError as exc:
        result["status"] = exc.status
        result["failure"] = {"code": exc.code, "message": exc.message}
    except OSError:
        result["status"] = "BLOCKED"
        result["failure"] = {"code": "LOCAL_SOCKET_ERROR", "message": "Local socket operation failed."}
    finally:
        if client is not None:
            try:
                client.close()
            except OSError:
                pass
    result["finished_monotonic_seconds"] = time.monotonic()
    result["duration_seconds"] = result["finished_monotonic_seconds"] - started
    return result


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--socket", required=True, help="local private AF_UNIX bridge socket")
    parser.add_argument("--profile", required=True, choices=("DI8", "DI16"))
    parser.add_argument("--timeout", type=float, default=10.0,
                        help="whole run deadline in host monotonic seconds, 0 < timeout <= 60 (default: 10)")
    parser.add_argument("--evidence", help="write evidence JSON to this file; default is stdout")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    evidence = run_acceptance(args.socket, args.profile, args.timeout)
    serialized = json.dumps(evidence, indent=2, sort_keys=True) + "\n"
    if args.evidence:
        target = Path(args.evidence)
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        fd = os.open(target, flags, 0o600)
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(serialized)
    else:
        sys.stdout.write(serialized)
    return 0 if evidence["status"] == "PASS" else 1 if evidence["status"] == "FAIL" else 2


if __name__ == "__main__":
    raise SystemExit(main())
