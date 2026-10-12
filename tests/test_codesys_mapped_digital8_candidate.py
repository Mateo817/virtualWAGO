"""Pure contracts for the offline digital-eight candidate; no CODESYS proxy is mocked as PASS."""

import csv
import hashlib
import importlib.util
import pathlib
import sys
import tempfile
import types
import unittest


SCRIPTENGINE_STUB = types.ModuleType("scriptengine")
_PREVIOUS_SCRIPTENGINE = sys.modules.get("scriptengine")
sys.modules["scriptengine"] = SCRIPTENGINE_STUB
ROOT = pathlib.Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools" / "codesys_mapped_digital8_candidate.py"
SPEC = importlib.util.spec_from_file_location("codesys_mapped_digital8_candidate", str(MODULE_PATH))
candidate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate)
if _PREVIOUS_SCRIPTENGINE is None:
    del sys.modules["scriptengine"]
else:
    sys.modules["scriptengine"] = _PREVIOUS_SCRIPTENGINE


class MappedDigital8CandidateTests(unittest.TestCase):
    def test_source_and_descriptor_pins_match_checked_in_candidate(self):
        source = (ROOT / "prototype" / "iec" / "minimal_io_8.st").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), candidate.SOURCE_SHA256)
        self.assertEqual(candidate.TERMINALS, [
            ("750-430", "8801_0750043000000000", "2.0.0.14"),
            ("750-530", "8802_0750053000000000", "2.0.0.15"),
        ])
        self.assertEqual(candidate.DESCRIPTOR_SHA256, {
            "750-430": "26d302678905d2e8f4c7e34880cf830c4ad56361ebd647e6ed82a9e02c81dd91",
            "750-530": "84b4043d448c44155a36916a1b65a39f20ba0560459d3c0ffac53fba351daa5d",
        })

    def test_native_parent_byte_readback_requires_eight_unmapped_children(self):
        facts = {
            "id": 0x01000000, "channel_type": "Input", "param_type": "local:InputField",
            "has_sub_elements": True, "subelement_count": 8,
            "mapped_variable": "Application.PLC_PRG.InputByte",
            "maps_to_existing_variable": True,
        }
        candidate.verify_native_parameter_facts(
            facts, 0x01000000, "Input", "local:InputField",
            "Application.PLC_PRG.InputByte", [None] * 8)
        for bad_facts in (
            dict(facts, subelement_count=16),
            dict(facts, id=0x03000000),
            dict(facts, channel_type="Output"),
            dict(facts, param_type="local:WordField"),
        ):
            with self.subTest(bad_facts=bad_facts), self.assertRaises(Exception):
                candidate.verify_native_parameter_facts(
                    bad_facts, 0x01000000, "Input", "local:InputField",
                    "Application.PLC_PRG.InputByte", [None] * 8)
        conflicting_children = [None] * 8
        conflicting_children[2] = "Application.PLC_PRG.OtherInput"
        with self.assertRaises(Exception):
            candidate.verify_native_parameter_facts(
                facts, 0x01000000, "Input", "local:InputField",
                "Application.PLC_PRG.InputByte", conflicting_children)

    def test_parent_mapping_edit_changes_only_variable_column(self):
        rows = [
            ["", "_IN", "", "Input Channels", "%IB1", "_750_430"],
            ["", "_OUT", "", "Output Channels", "%QB0", "_750_530"],
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "mapping.csv"
            with path.open("w", newline="") as stream:
                writer = csv.writer(stream, delimiter=";")
                writer.writerow(["// Generated schema header"])
                writer.writerows(rows)
            result = candidate.map_parent_bytes_in_csv(
                str(path), "Application.PLC_PRG.InputByte", "Application.PLC_PRG.OutputByte")
            self.assertEqual(result["_IN@_750_430"], "Application.PLC_PRG.InputByte")
            self.assertEqual(result["_OUT@_750_530"], "Application.PLC_PRG.OutputByte")
            self.assertEqual(candidate.read_mapping(str(path)), [
                ["Application.PLC_PRG.InputByte", "_IN", "", "Input Channels", "%IB1", "_750_430"],
                ["Application.PLC_PRG.OutputByte", "_OUT", "", "Output Channels", "%QB0", "_750_530"],
            ])

    def test_export_checks_real_byte_address_shape_and_conflicting_bit_maps(self):
        # Captured native export uses IB1 after Kbus diagnostics, whereas QB0
        # starts output data. These are IEC addresses, not DAL byte offsets.
        rows = [
            ["", "K-BUS diagnostics", "", "K-BUS diagnostics", "%IB0", "Kbus"],
            ["Application.PLC_PRG.InputByte", "_IN", "", "Input Channels", "%IB1", "_750_430"],
            ["Application.PLC_PRG.OutputByte", "_OUT", "", "Output Channels", "%QB0", "_750_530"],
        ]
        for prefix, label, address, device in (
                ("_IN@", "Digital input", "%IX1.", "_750_430"),
                ("_OUT@", "Digital output", "%QX0.", "_750_530")):
            rows.extend([["", prefix + str(n + 1), "", label, address + str(n), device]
                         for n in range(8)])
        self.assertEqual(candidate.verify_export_rows(
            rows, "Application.PLC_PRG.InputByte", "Application.PLC_PRG.OutputByte"),
            {"parent_bytes": 2, "digital_inputs": 8, "digital_outputs": 8,
             "csv_consistency": "PASS"})
        for column, value in ((0, "Application.PLC_PRG.BitAlias"),
                              (4, "%QX1.0"), (4, "%IX1.1")):
            damaged = [row[:] for row in rows]
            damaged[3][column] = value
            with self.subTest(column=column, value=value), self.assertRaises(Exception):
                candidate.verify_export_rows(
                    damaged, "Application.PLC_PRG.InputByte", "Application.PLC_PRG.OutputByte")

    def test_missing_or_duplicate_parent_parameter_fails_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "mapping.csv"
            path.write_text(";_IN;;; ;_750_430\n", encoding="utf-8")
            with self.assertRaises(Exception):
                candidate.map_parent_bytes_in_csv(
                    str(path), "Application.PLC_PRG.InputByte", "Application.PLC_PRG.OutputByte")
            path.write_text(
                ";_IN;;; ;_750_430\n;_IN;;; ;_750_430\n;_OUT;;; ;_750_530\n",
                encoding="utf-8")
            with self.assertRaises(Exception):
                candidate.map_parent_bytes_in_csv(
                    str(path), "Application.PLC_PRG.InputByte", "Application.PLC_PRG.OutputByte")


if __name__ == "__main__":
    unittest.main()
