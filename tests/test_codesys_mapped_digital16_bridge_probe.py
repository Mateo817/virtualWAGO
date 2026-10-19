"""Offline contracts for the WORD16 original-runtime probe candidate."""

import csv
import hashlib
import importlib.util
import json
import pathlib
import sys
import tempfile
import types
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[1]
SCRIPTENGINE_STUB = types.ModuleType("scriptengine")
IMP_STUB = types.ModuleType("imp")
_PREVIOUS_SCRIPTENGINE = sys.modules.get("scriptengine")
_PREVIOUS_IMP = sys.modules.get("imp")
sys.modules["scriptengine"] = SCRIPTENGINE_STUB
sys.modules["imp"] = IMP_STUB
MODULE_PATH = ROOT / "tools" / "codesys_mapped_digital16_bridge_probe.py"
SPEC = importlib.util.spec_from_file_location("codesys_mapped_digital16_bridge_probe", MODULE_PATH)
candidate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate)
REOPEN_PATH = ROOT / "tools" / "codesys_mapped_digital16_reopen_probe.py"
REOPEN_SPEC = importlib.util.spec_from_file_location("codesys_mapped_digital16_reopen_probe", REOPEN_PATH)
reopen_probe = importlib.util.module_from_spec(REOPEN_SPEC)
REOPEN_SPEC.loader.exec_module(reopen_probe)
if _PREVIOUS_SCRIPTENGINE is None:
    del sys.modules["scriptengine"]
else:
    sys.modules["scriptengine"] = _PREVIOUS_SCRIPTENGINE
if _PREVIOUS_IMP is None:
    del sys.modules["imp"]
else:
    sys.modules["imp"] = _PREVIOUS_IMP


class Digital16BridgeProbeTests(unittest.TestCase):
    def test_pins_match_catalog_and_source_hash(self):
        config = json.loads((ROOT / "config" / "minimal-iec-candidate.json").read_text())
        entries = {entry["product"]: entry for entry in config["device_tree_candidate"]
                   if entry.get("role") in ("digital_input_terminal", "digital_output_terminal")}
        self.assertEqual(candidate.TERMINALS, [
            ("750-1405", entries["750-1405"]["device_id"], "2.0.0.14"),
            ("750-1504", entries["750-1504"]["device_id"], "2.0.0.14"),
        ])
        self.assertEqual(candidate.DESCRIPTOR_SHA256, {
            article: entries[article]["descriptor_sha256"] for article in candidate.DESCRIPTOR_SHA256
        })
        source = (ROOT / "prototype" / "iec" / "minimal_io_16_bridge_probe.st").read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(), candidate.SOURCE_SHA256)

    def test_word_parent_and_sixteen_descriptor_bit_rows_are_consistent(self):
        rows = [
            ["Application.PLC_PRG.InputWord", "_IN", "", "Eingangskanäle", "%IW1", "_750_1405"],
            ["Application.PLC_PRG.OutputWord", "_OUT", "", "Ausgangskanäle", "%QW0", "_750_1504"],
        ]
        rows.extend([["", "_IN@%d" % (i + 1), "", "Digitaleingang",
                      "%%IX%d.%d" % (2 + i // 8, i % 8), "_750_1405"] for i in range(16)])
        rows.extend([["", "_OUT@%d" % (i + 1), "", "Digitalausgang",
                      "%%QX%d.%d" % (i // 8, i % 8), "_750_1504"] for i in range(16)])
        self.assertEqual(candidate.verify_export_rows(
            rows, "Application.PLC_PRG.InputWord", "Application.PLC_PRG.OutputWord"),
            {"parent_words": 2, "digital_inputs": 16, "digital_outputs": 16,
             "csv_consistency": "PASS"})
        broken = [row[:] for row in rows]
        broken[8][4] = "%QX9.0"
        with self.assertRaises(Exception):
            candidate.verify_export_rows(
                broken, "Application.PLC_PRG.InputWord", "Application.PLC_PRG.OutputWord")

        for label in ("", "Eingangskanäle", "Anzeige unbekannt"):
            relabeled = [row[:] for row in rows]
            for row in relabeled:
                row[3] = label
            self.assertEqual(candidate.verify_export_rows(
                relabeled, "Application.PLC_PRG.InputWord", "Application.PLC_PRG.OutputWord")["csv_consistency"],
                "PASS")

    def test_word_and_bit_addresses_are_exact_and_bound_to_parent_word(self):
        rows = [
            ["Application.PLC_PRG.InputWord", "_IN", "", "", "%IW1", "_750_1405"],
            ["Application.PLC_PRG.OutputWord", "_OUT", "", "", "%QW0", "_750_1504"],
        ]
        rows.extend([["", "_IN@%d" % (i + 1), "", "",
                      "%%IX%d.%d" % (2 + i // 8, i % 8), "_750_1405"] for i in range(16)])
        rows.extend([["", "_OUT@%d" % (i + 1), "", "",
                      "%%QX%d.%d" % (i // 8, i % 8), "_750_1504"] for i in range(16)])
        malformed = (
            (0, "%IW1suffix"),
            (0, " %IW1 "),
            (2, "%IX2.0suffix"),
            (2, "%IX2.8"),
            (2, "%QX2.0"),
            (2, "%IX1.0"),
            (2, "%IX2.1"),
            (2, "%IX2.0\n"),
            (18, "%QX0.7garbage"),
            (1, "%IW0"),
        )
        for row_index, address in malformed:
            damaged = [row[:] for row in rows]
            damaged[row_index][4] = address
            with self.subTest(row=row_index, address=address), self.assertRaises(Exception):
                candidate.verify_export_rows(
                    damaged, "Application.PLC_PRG.InputWord", "Application.PLC_PRG.OutputWord")

        wrong_device = [row[:] for row in rows]
        wrong_device.append(["", "_IN@1", "", "", "%IX2.0", "_750-other"])
        with self.assertRaises(Exception):
            candidate.verify_export_rows(
                wrong_device, "Application.PLC_PRG.InputWord", "Application.PLC_PRG.OutputWord")

    def test_native_mapping_contract_requires_word_parent_and_unmapped_children(self):
        facts = {
            "id": 0x01000000, "channel_type": "Input", "param_type": "local:InputField",
            "has_sub_elements": True, "subelement_count": 16,
            "mapped_variable": "Application.PLC_PRG.InputWord",
            "maps_to_existing_variable": True,
        }
        candidate.verify_native_parameter_facts(
            facts, 0x01000000, "Input", "local:InputField",
            "Application.PLC_PRG.InputWord", [None] * 16)
        with self.assertRaises(Exception):
            candidate.verify_native_parameter_facts(
                dict(facts, subelement_count=8), 0x01000000, "Input", "local:InputField",
                "Application.PLC_PRG.InputWord", [None] * 16)

    def test_csv_edit_preserves_descriptor_generated_address_and_other_columns(self):
        rows = [
            ["", "_IN", "", "Input Channels", "%IW1", "_750_1405"],
            ["", "_OUT", "", "Output Channels", "%QW0", "_750_1504"],
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = pathlib.Path(directory) / "mapping.csv"
            with path.open("w", newline="") as stream:
                writer = csv.writer(stream, delimiter=";")
                writer.writerow(["// native export header"])
                writer.writerows(rows)
            result = candidate.map_parent_words_in_csv(
                str(path), "Application.PLC_PRG.InputWord", "Application.PLC_PRG.OutputWord")
            self.assertEqual(result["_IN@_750_1405"], "Application.PLC_PRG.InputWord")
            exported = candidate.read_mapping(str(path))
            self.assertEqual([row[0] for row in exported], [
                "Application.PLC_PRG.InputWord", "Application.PLC_PRG.OutputWord"])
            self.assertEqual([row[4] for row in exported], ["%IW1", "%QW0"])
            self.assertEqual([row[5] for row in exported], ["_750_1405", "_750_1504"])

    def test_readonly_reopen_requires_saved_task_and_tcm_contracts(self):
        reopen_probe.verify_saved_task_facts({
            "task_count": 1, "kind": "Cyclic", "kind_is_cyclic": True,
            "interval": "20", "interval_unit": "ms", "pous": ["PLC_PRG"],
        })
        reopen_probe.verify_saved_tcm_facts({
            "id": 41, "param_type": "std:UDINT", "value": "0",
        })
        with self.assertRaises(Exception):
            reopen_probe.verify_saved_task_facts({
                "task_count": 1, "kind": "Cyclic", "kind_is_cyclic": True,
                "interval": "10", "interval_unit": "ms", "pous": ["PLC_PRG"],
            })
        with self.assertRaises(Exception):
            reopen_probe.verify_saved_tcm_facts({
                "id": 41, "param_type": "std:UDINT", "value": "1",
            })

if __name__ == "__main__":
    unittest.main()
