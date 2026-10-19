"""Real local SOCK_SEQPACKET fixtures for the V2 complete-frame checker."""
from __future__ import annotations

import copy
import json
import math
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest

from tools import native_frame_acceptance as acceptance


def sample_plan(timeout=0.7):
    return {
        "schema": acceptance.PLAN_SCHEMA,
        "expected_profile": "DI16",
        "input_bytes": 2,
        "input_bits": 16,
        "output_bytes": 2,
        "output_bits": 16,
        "timeout_seconds": timeout,
        "vectors": [
            {"input_hex": "0102", "expected_output_hex": "a5a5"},
            {"input_hex": "ff00", "expected_output_hex": "1234"},
        ],
    }


class FakeV2SeqpacketBridge:
    """Independent cycle producer; reads of STATUS do not advance state."""

    def __init__(self, plan=None, mode="normal"):
        self.plan = acceptance.validate_plan(sample_plan() if plan is None else plan)
        self.mode = mode
        self.oracle = {v["input_hex"]: v["expected_output_hex"]
                       for v in self.plan["vectors"]}
        self.tmp = tempfile.TemporaryDirectory()
        os.chmod(self.tmp.name, 0o700)
        self.path = str(Path(self.tmp.name) / "model.sock")
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.server.bind(self.path)
        os.chmod(self.path, 0o600)
        self.server.listen(1)
        self.server.settimeout(0.05)
        self.commands = []
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._client = None
        self._stale_cycles = 0
        self._status_count = 0
        self._last_status_frames = None
        self._state = {
            "generation": 23, "input_bytes": self.plan["input_bytes"],
            "input_bits": self.plan["input_bits"], "output_bytes": self.plan["output_bytes"],
            "output_bits": self.plan["output_bits"], "input": "00" * self.plan["input_bytes"],
            "latch": "00" * self.plan["input_bytes"],
            "requested": "00" * self.plan["output_bytes"],
            "staged": "00" * self.plan["output_bytes"],
            "coverage": "00" * self.plan["output_bytes"],
            "effective": "00" * self.plan["output_bytes"],
            "initialized": 1, "opened": 1, "configured": 1,
            "running": 1, "permit": 0, "watchdog": 1, "fault": 0,
            "read_active": 0, "write_active": 0, "write_failed": 0,
            "frames": 100,
        }
        for mode_name, field, value in (
            ("baseline_permit", "permit", 1),
            ("baseline_effective", "effective", "0001"),
            ("baseline_fault", "fault", 1),
            ("baseline_uninitialized", "initialized", 0),
            ("baseline_closed", "opened", 0),
            ("baseline_unconfigured", "configured", 0),
            ("baseline_stopped", "running", 0),
            ("baseline_watchdog", "watchdog", 0),
        ):
            if mode == mode_name:
                self._state[field] = value
        if mode == "baseline_profile":
            self._state["profile"] = "DI8"
        elif mode == "baseline_extent":
            self._state["output_bytes"] += 1
            self._state["output_bits"] += 8
            self._state["requested"] += "00"
            self._state["staged"] += "00"
            self._state["coverage"] += "00"
            self._state["effective"] += "00"
        self._cycle_thread = threading.Thread(target=self._cycle, daemon=True)
        self._serve_thread = threading.Thread(target=self._serve, daemon=True)
        self._cycle_thread.start()
        self._serve_thread.start()

    def _cycle(self):
        while not self._stop.wait(0.004):
            if self.mode in ("stale", "pre_increment_freeze"):
                continue
            with self._lock:
                prior = self._state["latch"]
                output = self.oracle.get(prior, "00" * self.plan["output_bytes"])
                if self.mode == "wrong_output":
                    output = ("01" if output[:2] != "01" else "02") + output[2:]
                if self._stale_cycles > 0:
                    self._stale_cycles -= 1
                else:
                    self._state["requested"] = output
                self._state["latch"] = self._state["input"]
                self._state["frames"] += 1

    def _status_packet(self):
        with self._lock:
            snapshot = dict(self._state)
        profile = snapshot.pop("profile", self.plan["expected_profile"])
        if self.mode == "baseline_not_ready":
            return "NOT_READY"
        if self.mode == "status_err":
            return "ERR STATE"
        if self.mode == "status_unknown":
            snapshot["future"] = 1
        if self.mode == "status_duplicate":
            snapshot["duplicate_generation"] = snapshot["generation"]
        if self.mode == "status_bad_hex":
            snapshot["input"] = "z1"
        if self.mode == "status_bad_decimal":
            snapshot["frames"] = "01"
        if self.mode == "status_bad_length":
            snapshot["input"] = "01"
        if self.mode == "regression" and self._status_count >= 3:
            snapshot["frames"] = max(0, (self._last_status_frames or 1) - 1)
        number_order = ("generation", "input_bytes", "input_bits", "output_bytes", "output_bits")
        hex_order = ("input", "latch", "requested", "staged", "coverage", "effective")
        tail_order = ("initialized", "opened", "configured", "running", "permit", "watchdog", "fault",
                      "read_active", "write_active", "write_failed", "frames")
        tokens = ["V2", "STATUS", profile]
        tokens.extend("%s=%s" % (key, snapshot[key]) for key in number_order)
        tokens.extend("%s=%s" % (key, snapshot[key]) for key in hex_order)
        tokens.extend("%s=%s" % (key, snapshot[key]) for key in tail_order)
        if self.mode == "status_unknown":
            tokens.append("future=1")
        if self.mode == "status_duplicate":
            tokens.append("generation=%s" % snapshot["generation"])
        response = " ".join(tokens)
        if self.mode == "oversized":
            response += " x=" + ("a" * 5000)
        return response

    def _serve(self):
        try:
            while not self._stop.is_set():
                try:
                    client, _ = self.server.accept()
                    self._client = client
                    break
                except socket.timeout:
                    continue
            else:
                return
            with client:
                while not self._stop.is_set():
                    try:
                        packet = client.recv(700).decode("ascii")
                    except OSError:
                        break
                    if not packet:
                        break
                    self.commands.append(packet)
                    if packet == "V2 STATUS":
                        self._status_count += 1
                        if self.mode == "disconnect":
                            return
                        if self.mode == "timeout":
                            self._stop.wait(0.3)
                        response = self._status_packet()
                        try:
                            client.send(response.encode("ascii"))
                        except OSError:
                            break
                        if self.mode != "oversized":
                            try:
                                self._last_status_frames = acceptance.parse_v2_status(response)["frames"]
                            except acceptance.AcceptanceError:
                                pass
                        if self.mode == "pre_increment_freeze":
                            self.mode = "stale"
                        continue
                    if packet.startswith("V2 INPUT "):
                        if self.mode == "input_err":
                            response = "ERR PROFILE"
                        else:
                            parts = packet.split(" ")
                            if len(parts) != 6:
                                response = "ERR FRAME"
                            else:
                                _, _, profile, generation, size, frame = parts
                                if profile != self.plan["expected_profile"]:
                                    response = "ERR PROFILE"
                                elif int(generation) != self._state["generation"]:
                                    response = "ERR GENERATION"
                                elif int(size) != self.plan["input_bytes"] or len(frame) != int(size) * 2:
                                    response = "ERR LENGTH"
                                else:
                                    with self._lock:
                                        if self.mode == "pre_increment_freeze":
                                            self._state["frames"] += 1
                                            self._state["requested"] = self.oracle.get(
                                                frame, "00" * self.plan["output_bytes"])
                                        if self.mode == "generation_change":
                                            self._state["generation"] += 1
                                        if self.mode != "input_watermark_mismatch":
                                            self._state["input"] = frame
                                        if self.mode == "inflight_stale":
                                            self._stale_cycles = 1
                                    response = "OK FRAME"
                        try:
                            client.send(response.encode("ascii"))
                        except OSError:
                            break
                        continue
                    response = "ERR COMMAND"
                    client.send(response.encode("ascii"))
        except OSError:
            pass

    def close(self):
        self._stop.set()
        if self._client is not None:
            try:
                self._client.shutdown(socket.SHUT_RDWR)
            except OSError:
                pass
            self._client.close()
        self.server.close()
        self._serve_thread.join(timeout=1)
        self._cycle_thread.join(timeout=1)
        self.tmp.cleanup()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()


class NativeFrameAcceptanceTests(unittest.TestCase):
    def test_explicit_vectors_require_fresh_post_ack_cycle_and_keep_gate_closed(self):
        with FakeV2SeqpacketBridge() as bridge:
            result = acceptance.run_acceptance(bridge.path, sample_plan())
        self.assertEqual(result["status"], "PASS", result)
        self.assertNotIn(bridge.path, str(result))
        self.assertFalse(result["configuration"]["output_permit_command_sent"])
        self.assertTrue(all(command == "V2 STATUS" or command.startswith("V2 INPUT ")
                            for command in bridge.commands))
        self.assertFalse(any("PERMIT" in command for command in bridge.commands))
        self.assertEqual(len(result["samples"]), 2)
        previous = result["baseline"]["frames"]
        for sample in result["samples"]:
            self.assertGreater(sample["frames"], sample["post_ack_watermark_frames"])
            self.assertGreater(sample["frames"], previous)
            self.assertEqual(sample["generation"], result["baseline"]["generation"])
            self.assertEqual(sample["observed_requested_hex"], sample["expected_output_hex"])
            self.assertEqual(sample["observed_effective_hex"], "0000")
            previous = sample["frames"]

    def test_old_pre_ack_output_and_inflight_stale_cycle_cannot_pass(self):
        with FakeV2SeqpacketBridge(mode="inflight_stale") as bridge:
            result = acceptance.run_acceptance(bridge.path, sample_plan())
        self.assertEqual(result["status"], "PASS", result)
        self.assertTrue(all(sample["frames"] > sample["post_ack_watermark_frames"]
                            for sample in result["samples"]))
        self.assertTrue(all(sample["frames"] > sample["post_latch_watermark_frames"]
                            for sample in result["samples"]))
        same_stale_output = sample_plan()
        same_stale_output["vectors"] = [
            {"input_hex": "0102", "expected_output_hex": "0000"},
        ]
        with FakeV2SeqpacketBridge(same_stale_output, mode="inflight_stale") as bridge:
            result = acceptance.run_acceptance(bridge.path, same_stale_output)
        self.assertEqual(result["status"], "PASS", result)
        self.assertGreater(result["samples"][0]["frames"],
                           result["samples"][0]["post_latch_watermark_frames"])
        with FakeV2SeqpacketBridge(mode="pre_increment_freeze") as bridge:
            result = acceptance.run_acceptance(bridge.path, sample_plan(timeout=0.06))
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["failure"]["code"], "TIMEOUT")
        self.assertEqual(result["samples"], [])

    def test_baseline_gates_and_readiness_are_checked_before_input(self):
        cases = (
            ("baseline_permit", "FAIL", "PERMIT_ALREADY_OPEN"),
            ("baseline_effective", "FAIL", "EFFECTIVE_OUTPUT_NONZERO"),
            ("baseline_fault", "BLOCKED", "MODEL_FAULT"),
            ("baseline_uninitialized", "BLOCKED", "MODEL_NOT_RUNNING"),
            ("baseline_closed", "BLOCKED", "MODEL_NOT_RUNNING"),
            ("baseline_unconfigured", "BLOCKED", "MODEL_NOT_RUNNING"),
            ("baseline_stopped", "BLOCKED", "MODEL_NOT_RUNNING"),
            ("baseline_watchdog", "BLOCKED", "MODEL_NOT_RUNNING"),
        )
        for mode, status, code in cases:
            with self.subTest(mode=mode), FakeV2SeqpacketBridge(mode=mode) as bridge:
                result = acceptance.run_acceptance(bridge.path, sample_plan())
            self.assertEqual(result["status"], status)
            self.assertEqual(result["failure"]["code"], code)
            self.assertEqual(bridge.commands, ["V2 STATUS"])

    def test_generation_profile_and_extent_must_remain_stable(self):
        cases = (("generation_change", "GENERATION_CHANGED"),
                 ("baseline_profile", "PROFILE_MISMATCH"),
                 ("baseline_extent", "EXTENT_MISMATCH"))
        for mode, code in cases:
            with self.subTest(mode=mode), FakeV2SeqpacketBridge(mode=mode) as bridge:
                result = acceptance.run_acceptance(bridge.path, sample_plan())
            self.assertEqual(result["status"], "BLOCKED")
            self.assertEqual(result["failure"]["code"], code)

    def test_output_oracle_mismatch_and_every_status_counter_regression_fail(self):
        with FakeV2SeqpacketBridge(mode="wrong_output") as bridge:
            result = acceptance.run_acceptance(bridge.path, sample_plan(timeout=0.06))
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["failure"]["code"], "OUTPUT_MISMATCH")
        with FakeV2SeqpacketBridge(mode="regression") as bridge:
            result = acceptance.run_acceptance(bridge.path, sample_plan(timeout=0.2))
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["failure"]["code"], "FRAME_COUNTER_REGRESSED")

    def test_error_disconnect_timeout_unknown_fields_and_packet_truncation(self):
        cases = (
            ("status_err", "FAIL", "BRIDGE_ERROR"),
            ("input_err", "FAIL", "BRIDGE_ERROR"),
            ("disconnect", "BLOCKED", "DISCONNECT"),
            ("timeout", "BLOCKED", "TIMEOUT"),
            ("status_unknown", "FAIL", "UNKNOWN_STATUS_FIELD"),
            ("status_duplicate", "FAIL", "DUPLICATE_STATUS_FIELD"),
            ("status_bad_hex", "FAIL", "INVALID_STATUS_HEX"),
            ("status_bad_decimal", "FAIL", "INVALID_STATUS_VALUE"),
            ("status_bad_length", "FAIL", "STATUS_FRAME_LENGTH"),
            ("oversized", "FAIL", "OVERSIZED_RESPONSE"),
        )
        for mode, status, code in cases:
            with self.subTest(mode=mode), FakeV2SeqpacketBridge(mode=mode) as bridge:
                result = acceptance.run_acceptance(bridge.path, sample_plan(timeout=0.07))
            self.assertEqual(result["status"], status, result)
            self.assertEqual(result["failure"]["code"], code)

    def test_post_ack_input_mismatch_does_not_sample(self):
        with FakeV2SeqpacketBridge(mode="input_watermark_mismatch") as bridge:
            result = acceptance.run_acceptance(bridge.path, sample_plan(timeout=0.07))
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["failure"]["code"], "INPUT_WATERMARK_MISMATCH")

    def test_symlink_socket_is_blocked_before_connect(self):
        with FakeV2SeqpacketBridge() as bridge:
            alias = str(Path(bridge.tmp.name) / "alias.sock")
            os.symlink(bridge.path, alias)
            result = acceptance.run_acceptance(alias, sample_plan())
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["failure"]["code"], "UNSAFE_SOCKET_ENDPOINT")
        self.assertEqual(bridge.commands, [])

    def test_parser_requires_exact_fields_canonical_values_and_frame_lengths(self):
        base = FakeV2SeqpacketBridge()
        try:
            response = base._status_packet()
        finally:
            base.close()
        self.assertEqual(acceptance.parse_v2_status(response)["profile"], "DI16")
        mutations = (
            (response + " future=1", "UNKNOWN_STATUS_FIELD"),
            (response + " generation=23", "DUPLICATE_STATUS_FIELD"),
            (response.replace(" read_active=0", ""), "MISSING_STATUS_FIELDS"),
            (response.replace(" read_active=0", " read_active=2"), "STATUS_VALUE_RANGE"),
            (response.replace("frames=100", "frames=0100"), "INVALID_STATUS_VALUE"),
            (response.replace("input=0000", "input=0z00"), "INVALID_STATUS_HEX"),
            (response.replace("input_bytes=2", "input_bytes=3"), "STATUS_FRAME_LENGTH"),
        )
        for packet, code in mutations:
            with self.subTest(code=code), self.assertRaises(acceptance.AcceptanceError) as caught:
                acceptance.parse_v2_status(packet)
            self.assertEqual(caught.exception.code, code)

    def test_private_plan_shape_extents_hex_vectors_and_timeout(self):
        valid = sample_plan()
        self.assertEqual(acceptance.validate_plan(valid)["expected_profile"], "DI16")
        mutations = []
        plan = copy.deepcopy(valid)
        plan["unexpected"] = 1
        mutations.append(plan)
        plan = copy.deepcopy(valid)
        plan["input_bytes"] = True
        mutations.append(plan)
        plan = copy.deepcopy(valid)
        plan["input_bits"] = 17
        mutations.append(plan)
        plan = copy.deepcopy(valid)
        plan["vectors"][0]["input_hex"] = "ABCD"
        mutations.append(plan)
        plan = copy.deepcopy(valid)
        plan["vectors"][0]["input_hex"] = "010"
        mutations.append(plan)
        plan = copy.deepcopy(valid)
        plan["vectors"].append(copy.deepcopy(plan["vectors"][0]))
        mutations.append(plan)
        for plan in mutations:
            with self.subTest(plan=plan), self.assertRaises(acceptance.AcceptanceError):
                acceptance.validate_plan(plan)
        for timeout in (0, -1, math.nan, math.inf, 60.01, 1e308, 10 ** 1000):
            plan = sample_plan(timeout=timeout)
            with self.subTest(timeout=timeout), self.assertRaises(acceptance.AcceptanceError) as caught:
                acceptance.validate_plan(plan)
            self.assertEqual(caught.exception.code, "INVALID_TIMEOUT")

    def test_private_plan_file_and_evidence_are_mode_0600_and_exclusive(self):
        with tempfile.TemporaryDirectory() as directory:
            os.chmod(directory, 0o700)
            plan_path = Path(directory) / "plan.json"
            plan_path.write_text(json.dumps(sample_plan()), encoding="utf-8")
            os.chmod(plan_path, 0o600)
            self.assertEqual(acceptance._load_plan(str(plan_path))["expected_profile"], "DI16")
            unsafe = Path(directory) / "unsafe.json"
            unsafe.write_text(json.dumps(sample_plan()), encoding="utf-8")
            os.chmod(unsafe, 0o644)
            with self.assertRaises(acceptance.AcceptanceError) as caught:
                acceptance._load_plan(str(unsafe))
            self.assertEqual(caught.exception.code, "UNSAFE_PLAN")


if __name__ == "__main__":
    unittest.main()
