"""Tests for the offline CODESYS mapping coverage summarizer."""
import importlib.util
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "codesys_mapping_summary", ROOT / "tools/codesys_mapping_summary.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class CodesysMappingSummaryTests(unittest.TestCase):
    def write_mapping(self, directory):
        path = Path(directory) / "mapping.csv"
        path.write_text(
            "//CoDeSys Mapping Export V1.2\n"
            ";_IN;;;%%IW1;DI_1\n"
            ";_IN@1;;;%%IX2.0;DI_1\n"
            ";_STA 1;;;%%IB10;PWM_1\n"
            ";_IW 1;;;%%IW6;PWM_1\n"
            ";_CTR 1;;;%%QB4;PWM_1\n"
            ";_QW 1;;;%%QW3;PWM_1\n".replace("%%", "%"),
            encoding="utf-8")
        return path

    def test_collapses_aliases_and_keeps_gaps(self):
        with tempfile.TemporaryDirectory() as directory:
            devices = summary.summarize(summary.read_rows(self.write_mapping(directory)))
        self.assertEqual(devices, [
            {"device": "DI_1", "direction": "input", "byte_ranges_inclusive": [[2, 3]],
             "covered_byte_count": 2, "address_count": 2},
            {"device": "PWM_1", "direction": "input",
             "byte_ranges_inclusive": [[10, 10], [12, 13]],
             "covered_byte_count": 3, "address_count": 2},
            {"device": "PWM_1", "direction": "output",
             "byte_ranges_inclusive": [[4, 4], [6, 7]],
             "covered_byte_count": 3, "address_count": 2},
        ])

    def test_rejects_bad_address_and_short_row(self):
        for data, message in ((";;;;%IX0.8;D\n", "invalid bit"),
                              (";;;;%IB0\n", "fewer than six")):
            with self.subTest(data=data), tempfile.TemporaryDirectory() as directory:
                path = Path(directory) / "mapping.csv"
                path.write_text(data, encoding="utf-8")
                with self.assertRaisesRegex(ValueError, message):
                    summary.read_rows(path)

    def test_scales_doubleword_and_longword_offsets_to_bytes(self):
        self.assertEqual(summary.parse_address("%ID2"), {
            "direction": "I", "kind": "D", "byte_start": 8, "byte_end": 11})
        self.assertEqual(summary.parse_address("%QL1"), {
            "direction": "Q", "kind": "L", "byte_start": 8, "byte_end": 15})

    def test_run_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_mapping(directory)
            output = Path(directory) / "summary.json"
            output.write_text("preserve", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                summary.run(source, output)
            self.assertEqual(output.read_text(encoding="utf-8"), "preserve")


if __name__ == "__main__":
    unittest.main()
