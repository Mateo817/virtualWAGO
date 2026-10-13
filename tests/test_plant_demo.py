import unittest
from prototype.vio import canonical
from tools.closed_loop_demo import run

class PlantDemoTests(unittest.TestCase):
    def test_exact_preset_pulse_integral_and_stop(self):
        rows=run()
        self.assertEqual(rows[24]["position_mm"],"205")
        self.assertEqual(rows[-1]["position_mm"],"205")
        self.assertEqual(len(rows),40)
    def test_deterministic_demo_and_next_cycle_sensor(self):
        a=run(); self.assertEqual(canonical(a),canonical(run()))
        first_word=a[0]["new_sensor_word"]
        actual_second_word=int.from_bytes(bytes.fromhex(a[1]["sample"]["input_hex"])[1:3],"little")
        self.assertEqual(first_word,actual_second_word)
