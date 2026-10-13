"""Pure mapping-contract checks; no CODESYS proxy/runtime is mocked as PASS."""

import importlib.util
import pathlib
import sys
import types
import unittest


SCRIPTENGINE_STUB = types.ModuleType("scriptengine")
_PREVIOUS_SCRIPTENGINE = sys.modules.get("scriptengine")
sys.modules["scriptengine"] = SCRIPTENGINE_STUB
MODULE_PATH = pathlib.Path(__file__).resolve().parents[1] / "tools" / "codesys_mapped_candidate.py"
SPEC = importlib.util.spec_from_file_location("codesys_mapped_candidate", str(MODULE_PATH))
candidate = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(candidate)
if _PREVIOUS_SCRIPTENGINE is None:
    del sys.modules["scriptengine"]
else:
    sys.modules["scriptengine"] = _PREVIOUS_SCRIPTENGINE


def valid_rows():
    rows = [
        ["Application.PLC_PRG.InputWord", "_IN", "", "Input Channels", "%IW1", "_750_1405"],
        ["Application.PLC_PRG.OutputWord", "_OUT", "", "Output Channels", "%QW0", "_750_1504"],
    ]
    for index in range(16):
        rows.append(["", "_IN@%d" % (index + 1), "", "Digital input",
                     "%%IX%d.%d" % (2 + index // 8, index % 8), "_750_1405"])
    for index in range(16):
        rows.append(["", "_OUT@%d" % (index + 1), "", "Digital output",
                     "%%QX%d.%d" % (index // 8, index % 8), "_750_1504"])
    return rows


class MappedCandidateContractTests(unittest.TestCase):
    def test_complete_two_terminal_word_and_bit_map_passes(self):
        result = candidate.verify_export_rows(valid_rows(), "Application.PLC_PRG.InputWord",
                                              "Application.PLC_PRG.OutputWord")
        self.assertEqual(result["digital_inputs"], 16)
        self.assertEqual(result["digital_outputs"], 16)
        self.assertEqual(result["csv_consistency"], "PASS")

    def test_wrong_terminal_identity_fails(self):
        rows = valid_rows()
        rows[0][5] = "_750_1504"
        with self.assertRaises(Exception):
            candidate.verify_export_rows(rows, "Application.PLC_PRG.InputWord",
                                         "Application.PLC_PRG.OutputWord")

    def test_input_mapped_as_output_fails(self):
        rows = valid_rows()
        rows[2][4] = "%QX30.0"
        with self.assertRaises(Exception):
            candidate.verify_export_rows(rows, "Application.PLC_PRG.InputWord",
                                         "Application.PLC_PRG.OutputWord")

    def test_output_mapped_as_input_fails(self):
        rows = valid_rows()
        rows[-1][4] = "%IX1.7"
        with self.assertRaises(Exception):
            candidate.verify_export_rows(rows, "Application.PLC_PRG.InputWord",
                                         "Application.PLC_PRG.OutputWord")

    def test_missing_channel_fails(self):
        rows = valid_rows()
        rows.pop(9)
        with self.assertRaises(Exception):
            candidate.verify_export_rows(rows, "Application.PLC_PRG.InputWord",
                                         "Application.PLC_PRG.OutputWord")

    def test_duplicate_channel_fails(self):
        rows = valid_rows()
        rows.append(list(rows[2]))
        with self.assertRaises(Exception):
            candidate.verify_export_rows(rows, "Application.PLC_PRG.InputWord",
                                         "Application.PLC_PRG.OutputWord")

    def test_conflicting_child_mapping_fails(self):
        facts = {"id": 0x01000000, "channel_type": "Input", "param_type": "local:InputField",
                 "has_sub_elements": True, "subelement_count": 16,
                 "mapped_variable": "Application.PLC_PRG.InputWord", "maps_to_existing_variable": True}
        child_variables = [None] * 16
        child_variables[3] = "Application.PLC_PRG.OtherInput"
        with self.assertRaises(Exception):
            candidate.verify_native_parameter_facts(facts, 0x01000000, "Input", "local:InputField",
                                                    "Application.PLC_PRG.InputWord", child_variables)


if __name__ == "__main__":
    unittest.main()
