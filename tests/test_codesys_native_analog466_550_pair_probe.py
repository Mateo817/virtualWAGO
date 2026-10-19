"""Hardware-free validation for the paired native analog mapping probe."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
previous = {key: sys.modules.get(key) for key in ("scriptengine", "imp")}
sys.modules["scriptengine"] = types.ModuleType("scriptengine")
sys.modules["imp"] = types.ModuleType("imp")
try:
    spec = importlib.util.spec_from_file_location(
        "analog466_550_pair", ROOT / "tools/codesys_native_analog466_550_pair_probe.py")
    probe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(probe)
finally:
    for key, module in previous.items():
        if module is None:
            del sys.modules[key]
        else:
            sys.modules[key] = module


class NativeAnalogPairProbeTests(unittest.TestCase):
    def rows(self):
        return [
            ["Application.PLC_PRG.InputWord1", "_IW 1", "", "Input word 1", "%IW1", "_750_466"],
            ["Application.PLC_PRG.InputWord2", "_IW 2", "", "Input word 2", "%IW2", "_750_466"],
            ["Application.PLC_PRG.OutputWord1", "_QW 1", "", "Output word 1", "%QW1", "_750_550"],
            ["Application.PLC_PRG.OutputWord2", "_QW 2", "", "Output word 2", "%QW2", "_750_550"],
        ]

    def test_source_and_descriptor_pins(self):
        source = ROOT / "prototype/iec/native_analog466_550_pair_probe.st"
        self.assertEqual(hashlib.sha256(source.read_bytes()).hexdigest(), probe.SOURCE_SHA256)
        self.assertEqual(probe.TERMINALS, [
            (32776, "07500466000000000400", "2.0.0.9"),
            (32776, "07500550000000000004", "2.0.0.9"),
        ])
        self.assertEqual([row[2] for row in probe.CHANNELS], ["_IW 1", "_IW 2", "_QW 1", "_QW 2"])

    def test_four_distinct_native_word_mappings(self):
        result = probe.verify_mapping_rows(self.rows())
        self.assertEqual([row["parameter_id"] for row in result],
                         [16777216, 16777217, 50331648, 50331649])
        self.assertEqual([row["direction"] for row in result],
                         ["input", "input", "output", "output"])

    def test_incomplete_extra_duplicate_wrong_device_or_direction_reject(self):
        base = self.rows()
        mutations = [base[:3], base + [base[0]]]
        for index, column, value in (
                (1, 4, "%IW1"), (2, 4, "%QW2"), (3, 4, "%QW1"),
                (2, 5, "_750_466"), (0, 0, "Application.PLC_PRG.OutputWord1")):
            rows = [row[:] for row in base]
            rows[index][column] = value
            mutations.append(rows)
        for rows in mutations:
            with self.subTest(rows=rows), self.assertRaises(Exception):
                probe.verify_mapping_rows(rows)

    def test_pinned_descriptor_hashes_required(self):
        env = {"VIRTUALWAGO_466_DESCRIPTOR_FILE": "466.xml",
               "VIRTUALWAGO_550_DESCRIPTOR_FILE": "550.xml"}
        def fake_digest(path):
            return probe.DESCRIPTOR_SHA256["466" if path == "466.xml" else "550"]
        with patch.object(probe.os, "environ", env), patch.object(probe, "digest", side_effect=fake_digest):
            probe.verify_descriptor_paths()
        with patch.object(probe.os, "environ", {"VIRTUALWAGO_466_DESCRIPTOR_FILE": "466.xml"}), \
             patch.object(probe, "digest", side_effect=fake_digest):
            with self.assertRaisesRegex(Exception, "VIRTUALWAGO_550_DESCRIPTOR_FILE"):
                probe.verify_descriptor_paths()


if __name__ == "__main__":
    unittest.main()
