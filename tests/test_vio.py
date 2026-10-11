import copy
import json
from pathlib import Path
import unittest
from prototype.vio import (Rail, ContractError, Unsupported, canonical,
                           encode_ai466_standard, decode_pwm677_frq)
from prototype.__main__ import dispatch
ROOT = Path(__file__).resolve().parents[1]

def config():
    return json.loads((ROOT / "config/minimal.json").read_text())

class RailTests(unittest.TestCase):
    def setUp(self): self.r = Rail(config())
    def test_initial_outputs_closed(self):
        self.assertFalse(self.r.observe()["armed"])
        self.assertEqual(self.r.observe()["effective_hex"], "0000")
    def test_no_invented_kbus_identity(self):
        self.assertTrue(all(m["kbus_uid"] is None for m in self.r.enumerate()))
    def test_exact_di_size(self):
        with self.assertRaises(ContractError): self.r.set_input("di", "01")
    def test_bad_hex_rejected(self):
        for value in ("000g", "00 0", "", 1, None):
            with self.subTest(value=value), self.assertRaises(ContractError):
                self.r.set_input("di", value)
    def test_input_latched_only_at_cycle(self):
        self.r.set_input("di", "0180")
        self.assertEqual(self.r.observe()["input_hex"], "0000")
        self.assertEqual(self.r.cycle()["input_hex"], "0180")
    def test_running_fresh_command_applies(self):
        self.r.run(True)
        self.assertEqual(self.r.cycle("0180")["effective_hex"], "0180")
    def test_stopped_command_is_observable_but_not_applied(self):
        result = self.r.cycle("ffff")
        self.assertEqual(result["command_hex"], "ffff")
        self.assertEqual(result["effective_hex"], "0000")
    def test_stop_start_requires_fresh_frame(self):
        self.r.run(True); self.r.cycle("ffff"); self.r.run(False); self.r.run(True)
        self.assertFalse(self.r.cycle()["armed"])
        self.assertTrue(self.r.cycle("0100")["armed"])
    def test_watchdog_exact_boundary(self):
        self.r.run(True); self.r.cycle("ffff")
        self.assertTrue(self.r.advance(99_999_999)["armed"])
        self.assertFalse(self.r.advance(1)["armed"])
        self.assertEqual(self.r.observe()["command_hex"], "ffff")
    def test_read_does_not_feed_watchdog(self):
        self.r.run(True); self.r.cycle("ffff"); self.r.advance(50_000_000)
        self.r.cycle(); self.r.advance(50_000_000)
        self.assertFalse(self.r.observe()["armed"])
    def test_bus_loss_preserves_request(self):
        self.r.run(True); self.r.cycle("0100"); self.r.fault("bus_lost", True)
        self.assertEqual(self.r.observe()["effective_hex"], "0000")
        self.assertEqual(self.r.observe()["command_hex"], "0100")
    def test_bus_restore_does_not_rearm(self):
        self.r.run(True); self.r.cycle("0100"); self.r.fault("bus_lost", True)
        self.r.fault("bus_lost", False)
        self.assertFalse(self.r.cycle()["armed"])
    def test_missing_module_no_silent_repacking(self):
        self.r.set_input("di", "ffff"); self.r.cycle()
        self.r.fault("missing", True, "di")
        result = self.r.cycle()
        self.assertEqual(result["input_hex"], "ffff")
        self.assertEqual(result["input_quality"], "BUS_FAULT")
    def test_frozen_input_keeps_old_sample(self):
        self.r.set_input("di", "0100"); self.r.cycle(); self.r.fault("freeze", True, "di")
        self.r.set_input("di", "0200")
        self.assertEqual(self.r.cycle()["input_hex"], "0100")
        self.assertEqual(self.r.observe()["input_quality"], "FROZEN")
    def test_invalid_frame_is_atomic(self):
        before = self.r.snapshot()
        with self.assertRaises(ContractError): self.r.cycle("ff")
        self.assertEqual(before, self.r.snapshot())
    def test_unknown_module(self):
        with self.assertRaises(ContractError): self.r.set_input("missing", "0000")
    def test_output_only_has_no_input(self):
        with self.assertRaises(ContractError): self.r.set_input("do", "")
    def test_unmodeled_fault_rejected(self):
        before = self.r.snapshot()
        with self.assertRaises(Unsupported): self.r.fault("short_circuit", True, "do")
        self.assertEqual(before, self.r.snapshot())
    def test_invalid_boolean_not_coerced(self):
        with self.assertRaises(ContractError): self.r.run(1)
        with self.assertRaises(ContractError): self.r.fault("bus_lost", 1)
    def test_negative_or_boolean_time_rejected(self):
        for value in (-1, True, 0.1):
            with self.subTest(value=value), self.assertRaises(ContractError): self.r.advance(value)
    def test_clock_overflow_is_atomic(self):
        self.r.advance(2**63-1); before = self.r.snapshot()
        with self.assertRaises(ContractError): self.r.advance(1)
        self.assertEqual(before, self.r.snapshot())
    def test_snapshot_replay_identical(self):
        self.r.run(True); self.r.cycle("0100"); snapshot = self.r.snapshot()
        def trace():
            rows = []
            for i in range(1, 6):
                self.r.advance(20_000_000); self.r.set_input("di", f"{i:02x}00")
                rows.append(self.r.cycle())
            return canonical(rows)
        first = trace(); self.r.restore(snapshot)
        self.assertEqual(first, trace())
    def test_snapshot_is_copy(self):
        snapshot = self.r.snapshot(); snapshot["state"]["running"] = True
        self.assertFalse(self.r.observe()["running"])
    def test_snapshot_wrong_config_rejected(self):
        snapshot = self.r.snapshot(); snapshot["config_sha256"] = "0" * 64
        with self.assertRaises(ContractError): self.r.restore(snapshot)
    def test_inconsistent_snapshot_rejected_atomically(self):
        before = self.r.snapshot(); modified = copy.deepcopy(before)
        modified["state"]["armed"] = True
        with self.assertRaises(ContractError): self.r.restore(modified)
        self.assertEqual(before, self.r.snapshot())
    def test_reset_restores_initial_state(self):
        before = self.r.snapshot(); self.r.run(True); self.r.cycle("ffff"); self.r.advance(12)
        self.r.reset(); self.assertEqual(before, self.r.snapshot())
    def test_64_independent_instances(self):
        rails = [Rail(config()) for _ in range(64)]
        for i, r in enumerate(rails):
            r.run(True); r.set_input("di", i.to_bytes(2,"little").hex()); r.cycle("0100")
        rails[0].fault("bus_lost", True)
        self.assertFalse(rails[0].observe()["armed"])
        for i, r in enumerate(rails[1:], 1):
            self.assertTrue(r.observe()["armed"])
            self.assertEqual(r.observe()["input_hex"], i.to_bytes(2,"little").hex())
    def test_overlap_rejected(self):
        c = config(); c["modules"].append(dict(c["modules"][0], id="di2"))
        with self.assertRaises(ContractError): Rail(c)
    def test_duplicate_id_rejected(self):
        c=config(); c["modules"][1]["id"]="di"
        with self.assertRaises(ContractError): Rail(c)
    def test_unknown_model_rejected(self):
        c=config(); c["modules"][0]["model"]="750-unknown"
        with self.assertRaises(Unsupported): Rail(c)
    def test_extra_config_key_rejected(self):
        c=config(); c["pretend_original_runtime"]=True
        with self.assertRaises(ContractError): Rail(c)
    def test_offsets_explicit_not_slot_derived(self):
        c = config(); c["input_size"]=8; c["modules"][0]["input_offset"]=6
        r=Rail(c); r.set_input("di", "0180")
        self.assertEqual(r.cycle()["input_hex"], "0000000000000180")
    def test_nonzero_unmapped_output_rejected(self):
        c=config(); c["output_size"]=3; r=Rail(c)
        with self.assertRaises(Unsupported): r.cycle("000001")
    def test_research_profile(self):
        r=Rail(json.loads((ROOT/"config/research-layout.json").read_text()))
        self.assertEqual(len(r.enumerate()),4)
        self.assertEqual(len(bytes.fromhex(r.cycle()["input_hex"])),20)
    def test_unknown_protocol_operation_and_extra_fields(self):
        for req in ({"op":"take_real_kbus"}, {"op":"run","running":True,"target":"wago"}):
            with self.subTest(req=req), self.assertRaises(ContractError): dispatch(self.r,req)

class CodecTests(unittest.TestCase):
    def test_analog_documented_points(self):
        self.assertEqual([encode_ai466_standard(v) for v in (4000,6000,12000,20000)],
                         [0x0000,0x1000,0x4000,0x7ff8])
    def test_analog_diagnostic_bits_not_used_as_measurement(self):
        for current in range(4000,20001,37):
            self.assertEqual(encode_ai466_standard(current) & 7,0)
    def test_analog_out_of_range_is_not_silently_clamped(self):
        with self.assertRaises(Unsupported): encode_ai466_standard(3999)
        with self.assertRaises(ContractError): encode_ai466_standard(20001)
    def test_pwm_little_endian_and_pair_enable(self):
        raw=bytes.fromhex("01e80300d007000000006400")
        self.assertEqual(decode_pwm677_frq(raw),(1000,2000,0,0))
    def test_pwm_second_pair_enabled(self):
        raw=bytes.fromhex("00e80300d00701640000c800")
        self.assertEqual(decode_pwm677_frq(raw),(0,0,100,200))
    def test_pwm_regcom_is_explicitly_unsupported(self):
        with self.assertRaises(Unsupported): decode_pwm677_frq(bytes.fromhex("81e803000000000000000000"))
    def test_pwm_out_of_range_reserved_bits_and_length(self):
        for raw in (bytes.fromhex("02e803000000000000000000"),
                    bytes.fromhex("01214e000000000000000000")):
            with self.subTest(raw=raw), self.assertRaises(Unsupported): decode_pwm677_frq(raw)
        with self.assertRaises(ContractError): decode_pwm677_frq(b"\0")

if __name__ == "__main__": unittest.main()
