import unittest

from prototype.module_models import Analog466, AnalogOutput550, Pwm677
from prototype.vio import ContractError, Unsupported


def pwm_frame(frequencies=(0, 0, 0, 0), enabled=(True, True)):
    controls = (int(enabled[0]), 0, int(enabled[1]), 0)
    return b"".join(bytes((controls[i],)) + frequency.to_bytes(2, "little")
                    for i, frequency in enumerate(frequencies))


class Analog466Tests(unittest.TestCase):
    def test_research_input_layout_uses_two_status_then_word_groups(self):
        model = Analog466()
        model.set_currents_uA((4000, 20_000))
        # The interleaved zero status bytes are this model's research layout.
        self.assertEqual(model.input_bytes(), bytes.fromhex("00000000f87f"))
        self.assertEqual(len(model.input_bytes()), 6)
        self.assertEqual(model.research_input_bytes(), model.input_bytes())
        self.assertEqual(model.descriptor_input_words(), (0x0000, 0x7ff8))
        self.assertEqual(model.descriptor_word_payload(), bytes.fromhex("0000f87f"))
        self.assertEqual(len(model.descriptor_word_payload()), 4)

    def test_documented_normal_range_midpoint(self):
        model = Analog466()
        model.set_currents_uA((12_000, 6000))
        self.assertEqual(model.input_bytes(), bytes.fromhex("000040000010"))

    def test_all_inputs_validate_before_update(self):
        model = Analog466()
        original = model.input_bytes()
        for values in ((5000,), (5000, 3999), (5000, True), (5000, 20_001), "5000,6000"):
            with self.subTest(values=values), self.assertRaises(ContractError):
                model.set_currents_uA(values)
            self.assertEqual(model.input_bytes(), original)


class Pwm677Tests(unittest.TestCase):
    def test_permit_is_required_and_pair_frequencies_run_independently(self):
        model = Pwm677()
        model.configure((20_000, 10_000, 2, 1))
        model.start()  # default permit is closed
        model.set_permit(True)
        model.start()
        model.advance(1_000_000_000)
        observed = model.observe()
        self.assertEqual(observed["frequency_hz"], [20_000, 10_000, 2, 1])
        self.assertEqual(observed["pulse_count"], [20_000, 10_000, 2, 1])
        self.assertTrue(observed["running"])

    def test_fractional_periods_are_exact_at_boundary(self):
        model = Pwm677()
        model.configure((3, 0, 0, 0))
        model.set_permit(True)
        model.start()
        model.advance(333_333_333)
        self.assertEqual(model.observe()["pulse_count"], [0, 0, 0, 0])
        model.advance(1)
        self.assertEqual(model.observe()["pulse_count"], [1, 0, 0, 0])

    def test_split_advances_match_single_advance(self):
        whole, split = Pwm677(), Pwm677()
        for model in (whole, split):
            model.configure((7, 1234, 20_000, 0))
            model.set_permit(True)
            model.start()
        whole.advance(1_234_567_891)
        for dt in (1, 12_345_678, 999_999_999, 222_222_213):
            split.advance(dt)
        self.assertEqual(whole.observe()["pulse_count"], split.observe()["pulse_count"])
        self.assertEqual(whole.observe()["time_ns"], split.observe()["time_ns"])

    def test_stop_discards_fractional_phase_and_preserves_cumulative_counts(self):
        model = Pwm677()
        model.configure((3, 0, 0, 0))
        model.set_permit(True)
        model.start()
        model.advance(200_000_000)  # 0.6 of a pulse
        model.stop()
        model.start()
        model.advance(200_000_000)
        self.assertEqual(model.observe()["pulse_count"], [0, 0, 0, 0])
        model.advance(133_333_334)
        self.assertEqual(model.observe()["pulse_count"], [1, 0, 0, 0])

    def test_pair_disable_retains_requested_words_but_closes_effective_output(self):
        model = Pwm677()
        model.set_permit(True)
        model.apply_output_frame(pwm_frame((100, 200, 300, 400), (False, True)))
        model.start()
        observed = model.observe()
        self.assertEqual(observed["requested_frequency_hz"], [100, 200, 300, 400])
        self.assertEqual(observed["frequency_hz"], [0, 0, 300, 400])
        self.assertEqual(observed["effective_pair_enabled"], [False, True])
        model.advance(1_000_000_000)
        self.assertEqual(model.observe()["pulse_count"], [0, 0, 300, 400])

    def test_gate_loss_and_fault_need_a_fresh_start(self):
        model = Pwm677()
        model.configure((1000, 0, 0, 0))
        model.set_permit(True)
        model.start()
        model.advance(100_000_000)
        self.assertEqual(model.observe()["pulse_count"][0], 100)
        model.set_permit(False)
        model.set_permit(True)
        model.advance(100_000_000)
        self.assertFalse(model.observe()["running"])
        self.assertEqual(model.observe()["pulse_count"][0], 100)
        model.start()
        model.advance(100_000_000)
        self.assertEqual(model.observe()["pulse_count"][0], 200)
        model.set_fault(True)
        model.set_fault(False)
        model.advance(100_000_000)
        self.assertFalse(model.observe()["running"])
        self.assertEqual(model.observe()["pulse_count"][0], 200)
        model.start()
        model.advance(100_000_000)
        self.assertEqual(model.observe()["pulse_count"][0], 300)

    def test_invalid_frame_and_time_are_atomic(self):
        model = Pwm677()
        model.configure((100, 200, 300, 400))
        before = model.observe()
        for frame in (b"\0", pwm_frame((20_001, 0, 0, 0)),
                      bytes.fromhex("81e803000000000000000000")):
            with self.subTest(frame=frame), self.assertRaises((ContractError, Unsupported)):
                model.apply_output_frame(frame)
            self.assertEqual(model.observe(), before)
        for dt in (-1, True, 0.5):
            with self.subTest(dt=dt), self.assertRaises(ContractError):
                model.advance(dt)
            self.assertEqual(model.observe(), before)

    def test_invalid_configuration_and_gates_are_atomic(self):
        model = Pwm677()
        model.configure((1, 2, 3, 4))
        before = model.observe()
        for values in ((1, 2, 3), (1, 2, 3, True), (1, 2, 3, 20_001), "1,2,3,4"):
            with self.subTest(values=values), self.assertRaises(ContractError):
                model.configure(values)
            self.assertEqual(model.observe(), before)
        for setter in (model.set_permit, model.set_fault):
            with self.assertRaises(ContractError):
                setter(1)
            self.assertEqual(model.observe(), before)

    def test_clock_overflow_is_atomic(self):
        model = Pwm677()
        model.advance(2**63 - 1)
        before = model.observe()
        with self.assertRaises(ContractError):
            model.advance(1)
        self.assertEqual(model.observe(), before)


class AnalogOutput550Tests(unittest.TestCase):
    def test_documented_normal_points_decode_to_millivolts(self):
        model = AnalogOutput550()
        model.set_output_words((0x0000, 0x1000))
        self.assertEqual(model.observe()["requested_voltage_mV"], [0, 1250])
        model.set_output_payload(bytes.fromhex("0040ff7f"))
        self.assertEqual(model.observe()["requested_voltage_mV"], [5000, 10000])
        self.assertEqual(model.observe()["requested_word"], [0x4000, 0x7fff])

    def test_payload_is_four_bytes_little_endian_and_channels_independent(self):
        model = AnalogOutput550()
        model.set_permit(True)
        model.set_output_payload(bytes.fromhex("00100070"))
        observed = model.observe()
        self.assertEqual(observed["requested_word"], [0x1000, 0x7000])
        self.assertEqual(observed["requested_voltage_mV"], [1250, 8750])
        self.assertEqual(observed["effective_voltage_mV"], [1250, 8750])
        model.set_channel_word(0, 0x4000)
        self.assertEqual(model.observe()["requested_word"], [0x4000, 0x7000])
        self.assertEqual(model.observe()["effective_voltage_mV"], [5000, 8750])
        model.set_channel_word(1, 0x0000)
        self.assertEqual(model.observe()["effective_voltage_mV"], [5000, 0])

    def test_closed_permit_retains_request_but_effective_outputs_are_zero(self):
        model = AnalogOutput550()
        model.set_output_words((0x1000, 0x4000))
        observed = model.observe()
        self.assertEqual(observed["requested_voltage_mV"], [1250, 5000])
        self.assertEqual(observed["effective_voltage_mV"], [0, 0])
        self.assertEqual(observed["effective_payload_hex"], "00000000")
        model.set_permit(True)
        self.assertFalse(model.observe()["armed"])
        model.set_output_words((0x1000, 0x4000))
        self.assertEqual(model.observe()["effective_voltage_mV"], [1250, 5000])
        model.set_permit(False)
        model.set_permit(True)
        self.assertEqual(model.observe()["requested_voltage_mV"], [1250, 5000])
        self.assertEqual(model.observe()["effective_voltage_mV"], [0, 0])
        model.set_output_words((0x1000, 0x4000))
        self.assertEqual(model.observe()["effective_voltage_mV"], [1250, 5000])

    def test_fault_is_fail_closed_and_needs_fresh_command_after_clear(self):
        model = AnalogOutput550()
        model.set_permit(True)
        model.set_output_words((0x2000, 0x6000))
        before = model.observe()
        model.set_fault(True)
        self.assertEqual(model.observe()["requested_voltage_mV"], [2500, 7500])
        self.assertEqual(model.observe()["effective_voltage_mV"], [0, 0])
        model.set_fault(False)
        self.assertEqual(model.observe()["effective_voltage_mV"], [0, 0])
        self.assertFalse(model.observe()["armed"])
        model.set_output_words(before["requested_word"])
        self.assertEqual(model.observe()["effective_voltage_mV"], [2500, 7500])

    def test_invalid_frames_values_and_gate_types_are_atomic(self):
        model = AnalogOutput550()
        model.set_permit(True)
        model.set_output_words((0x1000, 0x2000))
        before = model.observe()
        for payload in (b"", b"\0" * 3, b"\0" * 5, bytearray(4), "00000000"):
            with self.subTest(payload=payload), self.assertRaises(ContractError):
                model.set_output_payload(payload)
            self.assertEqual(model.observe(), before)
        for words in ((0x1000,), (0x1000, 0x8000), (0x1000, True), "1000,2000"):
            with self.subTest(words=words), self.assertRaises((ContractError, Unsupported)):
                model.set_output_words(words)
            self.assertEqual(model.observe(), before)
        for channel, word in ((True, 0), (2, 0), (0, 0x8000)):
            with self.subTest(channel=channel, word=word), self.assertRaises((ContractError, Unsupported)):
                model.set_channel_word(channel, word)
            self.assertEqual(model.observe(), before)
        with self.assertRaises(ContractError):
            model.set_permit(1)
        with self.assertRaises(ContractError):
            model.set_fault(1)
        self.assertEqual(model.observe(), before)


if __name__ == "__main__":
    unittest.main()
