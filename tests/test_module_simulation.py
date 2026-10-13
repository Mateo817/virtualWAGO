import unittest

from prototype.catalog import Catalog
from prototype.contracts import ContractError, Unsupported
from prototype.module_simulation import ModuleSimulation


def pwm_frame(frequencies=(0, 0, 0, 0), enabled=(True, True)):
    controls = (int(enabled[0]), 0, int(enabled[1]), 0)
    return b"".join(bytes((controls[i],)) + frequency.to_bytes(2, "little")
                    for i, frequency in enumerate(frequencies))


def rail_output(articles, parts):
    """Pack per-index bytes using the catalog's own consecutive model layout."""
    config = Catalog().research_layout(articles)
    frame = bytearray(config["output_size"])
    for index, payload in parts.items():
        module = config["modules"][index]
        size = Catalog().model_for_article(articles[index])["output_bytes"]
        if len(payload) != size:
            raise AssertionError("test payload does not match model output size")
        offset = module["output_offset"]
        frame[offset:offset + size] = payload
    return frame.hex()


class ModuleSimulationTests(unittest.TestCase):
    def test_mixed_catalog_composes_digital_analog_and_pwm_behaviors(self):
        sim = ModuleSimulation(["750-430", "750-530", "750-466", "750-677"])
        self.assertTrue(sim.observe()["catalog_sha256"])
        initial = sim.observe()["modules"]
        self.assertEqual(initial["m2"]["input_status"], "NOT_SAMPLED")
        self.assertNotIn("input_bytes_hex", initial["m2"])
        self.assertEqual(initial["m3"]["input_status"], "NOT_GENERATED")
        sim.set_running(True)
        sim.set_digital_input("m0", 0x85)
        sim.set_currents_uA("m2", (12_000, 20_000))
        frame = rail_output(
            ["750-430", "750-530", "750-466", "750-677"],
            {1: b"\x05", 3: pwm_frame((100, 200, 300, 400), (True, False))},
        )
        observed = sim.cycle(frame)
        self.assertEqual(observed["modules"]["m0"]["requested_input_value"], 0x85)
        self.assertEqual(observed["modules"]["m2"]["currents_uA"], [12_000, 20_000])
        self.assertEqual(observed["modules"]["m2"]["input_bytes_hex"], "00004000f87f")
        pwm = observed["modules"]["m3"]
        self.assertEqual(pwm["input_status"], "NOT_GENERATED")
        self.assertNotIn("input_bytes_hex", pwm)
        self.assertEqual(pwm["behavior"]["requested_frequency_hz"], [100, 200, 300, 400])
        self.assertEqual(pwm["behavior"]["frequency_hz"], [100, 200, 0, 0])
        self.assertEqual(pwm["behavior"]["running"], True)

    def test_duplicate_articles_create_independent_named_instances(self):
        sim = ModuleSimulation(["750-466", "750-466"])
        sim.set_currents_uA("m0", (20_000, 20_000))
        sim.set_currents_uA("m1", (4000, 4000))
        observed = sim.cycle()
        self.assertEqual(list(observed["modules"]), ["m0", "m1"])
        self.assertEqual(observed["modules"]["m0"]["currents_uA"], [20_000, 20_000])
        self.assertEqual(observed["modules"]["m1"]["currents_uA"], [4000, 4000])

    def test_pwm_runs_autonomously_without_repeated_rail_writes(self):
        articles = ["750-530", "750-677"]
        sim = ModuleSimulation(articles)
        sim.set_running(True)
        frame = rail_output(articles, {0: b"\x01", 1: pwm_frame((1000, 0, 0, 0))})
        first = sim.cycle(frame)
        self.assertTrue(first["rail"]["armed"])
        command = first["rail"]["command_hex"]
        after = sim.advance(50_000_000)
        self.assertEqual(after["modules"]["m1"]["behavior"]["pulse_count"], [50, 0, 0, 0])
        self.assertEqual(after["rail"]["command_hex"], command)
        self.assertEqual(after["rail"]["time_ns"], 50_000_000)
        self.assertTrue(after["modules"]["m1"]["behavior"]["running"])

    def test_large_advance_matches_split_advances_at_watchdog_expiry(self):
        articles = ["750-677"]
        frame = rail_output(articles, {0: pwm_frame((1000, 0, 0, 0))})
        whole, split = ModuleSimulation(articles), ModuleSimulation(articles)
        for sim in (whole, split):
            sim.set_running(True)
            sim.cycle(frame)
        one = whole.advance(150_000_000)
        split.advance(100_000_000)
        two = split.advance(50_000_000)
        self.assertEqual(one, two)
        self.assertEqual(one["modules"]["m0"]["behavior"]["pulse_count"], [100, 0, 0, 0])
        self.assertFalse(one["rail"]["armed"])
        self.assertFalse(one["modules"]["m0"]["behavior"]["running"])

    def test_watchdog_exact_boundary_closes_pwm_lease(self):
        sim = ModuleSimulation(["750-677"])
        sim.set_running(True)
        sim.cycle(rail_output(["750-677"], {0: pwm_frame((1000, 0, 0, 0))}))
        before = sim.advance(99_999_999)
        self.assertTrue(before["rail"]["armed"])
        self.assertEqual(before["modules"]["m0"]["behavior"]["pulse_count"], [99, 0, 0, 0])
        exact = sim.advance(1)
        self.assertFalse(exact["rail"]["armed"])
        self.assertEqual(exact["modules"]["m0"]["behavior"]["pulse_count"], [100, 0, 0, 0])
        self.assertEqual(exact["modules"]["m0"]["behavior"]["frequency_hz"], [0, 0, 0, 0])

    def test_stop_bus_loss_and_missing_restore_need_fresh_complete_frame(self):
        articles = ["750-677"]
        sim = ModuleSimulation(articles)
        sim.set_running(True)
        frame = rail_output(articles, {0: pwm_frame((1000, 0, 0, 0))})
        sim.cycle(frame)
        sim.set_running(False)
        self.assertFalse(sim.observe()["modules"]["m0"]["behavior"]["running"])
        sim.set_running(True)
        sim.advance(10_000_000)
        self.assertEqual(sim.observe()["modules"]["m0"]["behavior"]["pulse_count"], [0, 0, 0, 0])
        sim.cycle(frame)
        sim.fault("bus_lost", True)
        self.assertFalse(sim.observe()["modules"]["m0"]["behavior"]["running"])
        sim.fault("bus_lost", False)
        sim.advance(10_000_000)
        self.assertEqual(sim.observe()["modules"]["m0"]["behavior"]["pulse_count"], [0, 0, 0, 0])
        sim.cycle(frame)
        sim.fault("missing", True, "m0")
        sim.fault("missing", False, "m0")
        sim.advance(10_000_000)
        self.assertFalse(sim.observe()["modules"]["m0"]["behavior"]["running"])
        sim.cycle(frame)
        self.assertTrue(sim.observe()["modules"]["m0"]["behavior"]["running"])

    def test_multiple_pwm_frames_validate_before_any_model_changes(self):
        articles = ["750-677", "750-677"]
        sim = ModuleSimulation(articles)
        sim.set_running(True)
        before = sim.observe()
        invalid_second = bytearray(pwm_frame((200, 0, 0, 0)))
        invalid_second[0] = 0x80  # RegCom path is unsupported.
        frame = rail_output(articles, {0: pwm_frame((100, 0, 0, 0)), 1: bytes(invalid_second)})
        with self.assertRaises(Unsupported):
            sim.cycle(frame)
        self.assertEqual(sim.observe(), before)

    def test_invalid_inputs_and_operations_leave_state_unchanged(self):
        sim = ModuleSimulation(["750-430", "750-466", "750-677"])
        before = sim.observe()
        for value in (-1, True, 0x100):
            with self.subTest(value=value), self.assertRaises(ContractError):
                sim.set_digital_input("m0", value)
            self.assertEqual(sim.observe(), before)
        for currents in ((4000,), (4000, 20_001), (4000, True)):
            with self.subTest(currents=currents), self.assertRaises(ContractError):
                sim.set_currents_uA("m1", currents)
            self.assertEqual(sim.observe(), before)
        with self.assertRaises(Unsupported):
            sim.set_currents_uA("m2", (4000, 4000))
        self.assertEqual(sim.observe(), before)
        with self.assertRaises(ContractError):
            sim.advance(True)
        with self.assertRaises(ContractError):
            sim.set_running(1)
        self.assertEqual(sim.observe(), before)

    def test_invalid_output_and_fault_are_atomic(self):
        sim = ModuleSimulation(["750-530", "750-677"])
        before = sim.observe()
        invalid_pwm = bytearray(pwm_frame())
        invalid_pwm[0] = 0x80
        for frame in ("00", "zz" * 13, rail_output(["750-530", "750-677"],
                                                    {0: b"\x01", 1: bytes(invalid_pwm)})):
            with self.subTest(frame=frame), self.assertRaises((ContractError, Unsupported)):
                sim.cycle(frame)
            self.assertEqual(sim.observe(), before)
        for args in (("bus_lost", True, "m0"), ("missing", True, None),
                     ("invented", True, None), ("bus_lost", 1, None)):
            with self.subTest(args=args), self.assertRaises((ContractError, Unsupported)):
                sim.fault(*args)
            self.assertEqual(sim.observe(), before)

    def test_documentation_only_modules_and_partial_snapshots_are_rejected(self):
        with self.assertRaises(Unsupported):
            ModuleSimulation(["750-454"])
        sim = ModuleSimulation(["750-677"])
        with self.assertRaises(Unsupported):
            sim.snapshot()
        with self.assertRaises(Unsupported):
            sim.restore({})


if __name__ == "__main__":
    unittest.main()
