"""Offline tests for the native digital bridge acceptance checker."""
from __future__ import annotations

import math
import os
from pathlib import Path
import socket
import tempfile
import threading
import unittest

from tools import native_digital_acceptance as acceptance


class FakeSeqpacketBridge:
    """Transport fixture for the existing bridge text protocol only."""

    def __init__(self, profile: str, mode: str = "normal") -> None:
        self.profile = profile
        self.mode = mode
        self.xor = acceptance.PROFILES[profile]["xor"]
        self.tmp = tempfile.TemporaryDirectory()
        os.chmod(self.tmp.name, 0o700)
        self.path = str(Path(self.tmp.name) / "model.sock")
        self.server = socket.socket(socket.AF_UNIX, socket.SOCK_SEQPACKET)
        self.server.bind(self.path)
        os.chmod(self.path, 0o600)
        self.server.listen(1)
        self.server.settimeout(0.1)
        self.commands: list[str] = []
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._state = {
            "input": 0, "requested": 0, "permit": 0, "effective": 0,
            "watchdog": 1, "fault": 0, "generation": 7, "frames": 100,
            "opened": 1, "configured": 1, "running": 1, "latched_input": 0,
        }
        baseline_modes = {
            "baseline_permit": ("permit", 1),
            "baseline_effective": ("effective", 1),
            "baseline_fault": ("fault", 1),
            "baseline_closed": ("opened", 0),
            "baseline_unconfigured": ("configured", 0),
            "baseline_stopped": ("running", 0),
            "baseline_watchdog": ("watchdog", 0),
        }
        if mode in baseline_modes:
            field, value = baseline_modes[mode]
            self._state[field] = value
        self._regress_once = False
        self._regressed = threading.Event()
        self._regression_release = threading.Event()
        self._stale_cycles = 0
        self._cycle_interval = 0.015 if mode == "inflight_stale" else 0.005
        self._cycle_thread = threading.Thread(target=self._cycle, daemon=True)
        self._thread = threading.Thread(target=self._serve, daemon=True)
        self._cycle_thread.start()
        self._thread.start()

    def _cycle(self) -> None:
        """Advance model state independently; STATUS is strictly read-only."""
        while not self._stop.wait(self._cycle_interval):
            if self.mode in ("stale", "pre_increment_freeze"):
                continue
            regressed = False
            with self._lock:
                if self._regress_once:
                    self._state["frames"] -= 1
                    self._regress_once = False
                    regressed = True
                else:
                    # Model a one-cycle input/output pipeline: this cycle writes
                    # the previously latched input, then latches the current one.
                    prior_input = self._state["latched_input"]
                    requested = prior_input ^ self.xor
                    if self.mode == "wrong_xor":
                        requested ^= 1
                    if self._stale_cycles:
                        self._stale_cycles -= 1
                    else:
                        self._state["requested"] = requested
                    self._state["latched_input"] = self._state["input"]
                    self._state["frames"] += 1
            if regressed:
                self._regressed.set()
                self._regression_release.wait(1.0)

    def _serve(self) -> None:
        try:
            while not self._stop.is_set():
                try:
                    client, _ = self.server.accept()
                    break
                except socket.timeout:
                    continue
            else:
                return
            with client:
                status_count = 0
                while not self._stop.is_set():
                    try:
                        request = client.recv(128).decode("ascii")
                    except OSError:
                        break
                    if not request:
                        break
                    self.commands.append(request)
                    if request.startswith("INPUT "):
                        with self._lock:
                            self._state["input"] = int(request[6:])
                            if self.mode == "inflight_stale":
                                self._stale_cycles = 3
                            if self.mode == "pre_increment_freeze":
                                # A completed frame happened before ACK, then
                                # the cyclic producer freezes. It cannot satisfy
                                # the subsequent post-ACK watermark requirement.
                                self._state["frames"] += 1
                                self._state["requested"] = self._state["input"] ^ self.xor
                            elif self.mode == "generation_change":
                                self._state["generation"] += 1
                        response = "OK INPUT"
                    elif request == "STATUS":
                        status_count += 1
                        if self.mode == "disconnect":
                            return
                        if self.mode == "err":
                            response = "ERR STATE"
                            client.send(response.encode("ascii"))
                            continue
                        if self.mode == "timeout":
                            threading.Event().wait(0.2)
                        with self._lock:
                            snapshot = dict(self._state)
                            if self.mode == "regression" and status_count == 2:
                                # The next periodic frame regresses after the
                                # post-ACK watermark has been observed.
                                self._regress_once = True
                            elif self.mode == "regression" and status_count >= 3:
                                # Let this STATUS observe the regressed frame
                                # before the periodic producer resumes.
                                self._regression_release.set()
                        if self.mode == "regression" and status_count == 2:
                            self._regressed.wait(0.5)
                        response = (
                            "STATUS input={input} permit={permit} requested={requested} effective={effective} "
                            "watchdog={watchdog} fault={fault} generation={generation} frames={frames} "
                            "opened={opened} configured={configured} running={running}"
                        ).format(input=snapshot["input"], requested=snapshot["requested"],
                                 permit=snapshot["permit"], effective=snapshot["effective"],
                                 watchdog=snapshot["watchdog"], fault=snapshot["fault"],
                                 generation=snapshot["generation"], frames=snapshot["frames"],
                                 opened=snapshot["opened"], configured=snapshot["configured"],
                                 running=snapshot["running"])
                        if self.mode == "unknown_field":
                            response += " extra=1"
                        if self.mode == "oversized":
                            response += " x" * 300
                    else:
                        response = "ERR COMMAND"
                    try:
                        client.send(response.encode("ascii"))
                    except OSError:
                        break
        except OSError:
            pass

    def close(self) -> None:
        self._stop.set()
        self._regression_release.set()
        self.server.close()
        self._thread.join(timeout=1)
        self._cycle_thread.join(timeout=1)
        self.tmp.cleanup()

    def __enter__(self) -> "FakeSeqpacketBridge":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()


class NativeDigitalAcceptanceTests(unittest.TestCase):
    def test_di8_and_di16_accept_fresh_xor_samples_without_opening_permit(self) -> None:
        for profile in ("DI8", "DI16"):
            with self.subTest(profile=profile), FakeSeqpacketBridge(profile) as bridge:
                result = acceptance.run_acceptance(bridge.path, profile, timeout_seconds=1.0)
                self.assertEqual(result["status"], "PASS", result)
                self.assertEqual(result["configuration"]["output_permit_command_sent"], False)
                self.assertNotIn(bridge.path, str(result))
                self.assertNotIn("PERMIT", bridge.commands)
                self.assertEqual(len(result["samples"]), len(acceptance.PROFILES[profile]["patterns"]))
                generation = result["baseline"]["generation"]
                previous_frames = result["baseline"]["frames"]
                for sample in result["samples"]:
                    self.assertEqual(sample["generation"], generation)
                    self.assertGreater(sample["frames"], previous_frames)
                    self.assertGreater(sample["frames"], sample["post_ack_watermark_frames"])
                    self.assertEqual(sample["requested"], sample["expected_requested"])
                    self.assertEqual(sample["effective"], 0)
                    self.assertEqual(sample["permit"], 0)
                    previous_frames = sample["frames"]

    def test_status_is_read_only_and_fresh_stale_output_is_waited_out(self) -> None:
        with FakeSeqpacketBridge("DI8", "inflight_stale") as bridge:
            result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=1.0)
        self.assertEqual(result["status"], "PASS", result)
        self.assertTrue(any(sample["stale_fresh_frames"] > 0 for sample in result["samples"]))
        self.assertTrue(all(sample["frames"] > sample["post_ack_watermark_frames"]
                            for sample in result["samples"]))

    def test_unknown_status_fields_are_structured_failures(self) -> None:
        with FakeSeqpacketBridge("DI8", "unknown_field") as bridge:
            result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=0.5)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["failure"]["code"], "UNKNOWN_STATUS_FIELD")

    def test_unsafe_baseline_states_abort_before_any_input_command(self) -> None:
        cases = (
            ("baseline_permit", "FAIL", "PERMIT_ALREADY_OPEN"),
            ("baseline_effective", "FAIL", "EFFECTIVE_OUTPUT_NONZERO"),
            ("baseline_fault", "BLOCKED", "MODEL_FAULT"),
            ("baseline_closed", "BLOCKED", "MODEL_NOT_RUNNING"),
            ("baseline_unconfigured", "BLOCKED", "MODEL_NOT_RUNNING"),
            ("baseline_stopped", "BLOCKED", "MODEL_NOT_RUNNING"),
            ("baseline_watchdog", "BLOCKED", "MODEL_NOT_RUNNING"),
        )
        for mode, expected_status, expected_code in cases:
            with self.subTest(mode=mode), FakeSeqpacketBridge("DI8", mode) as bridge:
                result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=0.5)
            self.assertEqual(result["status"], expected_status)
            self.assertEqual(result["failure"]["code"], expected_code)
            self.assertEqual(bridge.commands, ["STATUS"])
            self.assertFalse(result["configuration"]["output_permit_command_sent"])

    def test_changed_generation_blocks_sample_acceptance(self) -> None:
        with FakeSeqpacketBridge("DI8", "generation_change") as bridge:
            result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=0.5)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["failure"]["code"], "GENERATION_CHANGED")

    def test_stale_frame_counter_times_out_as_blocked(self) -> None:
        with FakeSeqpacketBridge("DI8", "stale") as bridge:
            result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=0.08)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["failure"]["code"], "TIMEOUT")

    def test_pre_ack_frame_cannot_satisfy_post_ack_sample_watermark(self) -> None:
        with FakeSeqpacketBridge("DI8", "pre_increment_freeze") as bridge:
            result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=0.08)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["failure"]["code"], "TIMEOUT")
        self.assertEqual(result["samples"], [])

    def test_fresh_wrong_transform_fails(self) -> None:
        with FakeSeqpacketBridge("DI8", "wrong_xor") as bridge:
            result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=0.08)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["failure"]["code"], "XOR_MISMATCH")

    def test_bridge_err_disconnect_timeout_and_oversized_packet_are_structured(self) -> None:
        cases = (
            ("err", "FAIL", "BRIDGE_ERROR"),
            ("disconnect", "BLOCKED", "DISCONNECT"),
            ("timeout", "BLOCKED", "TIMEOUT"),
            ("oversized", "FAIL", "OVERSIZED_RESPONSE"),
        )
        for mode, expected_status, expected_code in cases:
            with self.subTest(mode=mode), FakeSeqpacketBridge("DI8", mode) as bridge:
                result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=0.06)
            self.assertEqual(result["status"], expected_status)
            self.assertEqual(result["failure"]["code"], expected_code)

    def test_frame_counter_regression_is_checked_at_every_status_observation(self) -> None:
        with FakeSeqpacketBridge("DI8", "regression") as bridge:
            result = acceptance.run_acceptance(bridge.path, "DI8", timeout_seconds=0.5)
        self.assertEqual(result["status"], "FAIL")
        self.assertEqual(result["failure"]["code"], "FRAME_COUNTER_REGRESSED")

    def test_socket_symlink_is_blocked_before_connect(self) -> None:
        with FakeSeqpacketBridge("DI8") as bridge:
            alias = str(Path(bridge.tmp.name) / "alias.sock")
            os.symlink(bridge.path, alias)
            result = acceptance.run_acceptance(alias, "DI8", timeout_seconds=0.5)
        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["failure"]["code"], "UNSAFE_SOCKET_ENDPOINT")

    def test_status_parser_requires_exact_field_set_and_canonical_values(self) -> None:
        fields = "input=0 permit=0 requested=150 effective=0 watchdog=1 fault=0 generation=1 frames=2 opened=1 configured=1 running=1"
        parsed = acceptance.parse_status("STATUS " + fields)
        self.assertEqual(parsed["requested"], 150)
        for response, code in (
            ("STATUS " + fields + " future=9", "UNKNOWN_STATUS_FIELD"),
            ("STATUS " + fields.replace("fault=0 ", ""), "MISSING_STATUS_FIELDS"),
            ("STATUS " + fields.replace("permit=0", "permit=2"), "STATUS_VALUE_RANGE"),
            ("STATUS " + fields.replace("frames=2", "frames=02"), "INVALID_STATUS_VALUE"),
        ):
            with self.subTest(code=code), self.assertRaises(acceptance.AcceptanceError) as caught:
                acceptance.parse_status(response)
            self.assertEqual(caught.exception.code, code)

    def test_timeout_must_be_finite_and_positive(self) -> None:
        for timeout in (0, -1, math.nan, math.inf, 60.01, 1e308):
            with self.subTest(timeout=timeout):
                result = acceptance.run_acceptance("/unused", "DI8", timeout_seconds=timeout)
                self.assertEqual(result["status"], "FAIL")
                self.assertEqual(result["failure"]["code"], "INVALID_TIMEOUT")


if __name__ == "__main__":
    unittest.main()
