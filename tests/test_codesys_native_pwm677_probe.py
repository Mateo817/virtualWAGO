"""Pure validator tests for the native offline 750-677 project probe."""
import csv
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest


ROOT = Path(__file__).resolve().parents[1]
previous = sys.modules.get("scriptengine")
sys.modules["scriptengine"] = types.ModuleType("scriptengine")
try:
    spec = importlib.util.spec_from_file_location(
        "native_pwm677", ROOT / "tools/codesys_native_pwm677_probe.py")
    candidate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate)
finally:
    if previous is None:
        del sys.modules["scriptengine"]
    else:
        sys.modules["scriptengine"] = previous


class NativePwm677ProbeTests(unittest.TestCase):
    def rows(self):
        rows = []
        for field in candidate.process_fields():
            offset = len([r for r in rows if r[5] == candidate.DEVICE_NAME and
                          (r[4].startswith("%IB") if field["direction"] == "input"
                           else r[4].startswith("%QB"))])
            # Parameter order is BYTE, BYTE, WORD for each channel. The
            # byte cursor must account for the preceding WORD's second byte.
            prior = [r for r in rows if r[5] == candidate.DEVICE_NAME and
                     (r[4].startswith("%I") if field["direction"] == "input"
                      else r[4].startswith("%Q"))]
            offset = 0
            for row in prior:
                match = (candidate.IEC_BYTE_INPUT.match(row[4]) or
                         candidate.IEC_WORD_INPUT.match(row[4]) or
                         candidate.IEC_BYTE_OUTPUT.match(row[4]) or
                         candidate.IEC_WORD_OUTPUT.match(row[4]))
                value = int(match.group(1))
                width = 2 if "W" in row[4] else 1
                offset = max(offset, (value * 2 if "W" in row[4] else value) + width)
            address = ("%I" if field["direction"] == "input" else "%Q")
            address += "B" if field["type"] == "std:BYTE" else "W"
            index = offset if field["type"] == "std:BYTE" else offset // 2
            variable = ("Application.PLC_PRG." + field["variable"]
                        if field["variable"] else "")
            rows.append([variable,
                         candidate.export_parameter_name(field),
                         "beliebig", "", address + str(index), candidate.DEVICE_NAME])
        return rows

    def test_pinned_descriptor_manual_and_source(self):
        self.assertEqual(candidate.TERMINAL,
                         (32776, "07500677000000001616", "2.0.0.3"))
        self.assertEqual(candidate.DESCRIPTOR_SHA256,
                         "15dcba17a7186fc3dd91fc2b47c806bf7016e6e0ebc949b352c9549f5124c780")
        self.assertEqual(candidate.MANUAL_SHA256,
                         "df130ee3f7f22e81d3439b6d1797d123194626b9091a0e9ec0f4ea149b6035f0")
        self.assertEqual(hashlib.sha256(
            (ROOT / "prototype/iec/native_pwm677_probe.st").read_bytes()).hexdigest(),
            candidate.SOURCE_SHA256)
        self.assertEqual(len(candidate.process_fields()), 24)

    def test_mapping_reports_actual_16_byte_image_per_direction(self):
        rows = self.rows()
        result = candidate.verify_mapping_rows(rows)
        self.assertEqual(result["input"]["image_bytes"], 16)
        self.assertEqual(result["output"]["image_bytes"], 16)
        self.assertEqual(result["input"]["declared_scalar_bytes"], 16)
        self.assertEqual(result["output"]["declared_scalar_bytes"], 16)
        self.assertEqual([f["parameter"] for f in result["output"]["fields"][:3]],
                         ["_CTR 1", "_RES 1", "_QW 1"])
        self.assertEqual(result["input"]["fields"][2]["iec_address"], "%IW1")

    def test_duplicate_reserved_names_are_resolved_by_direction(self):
        rows = self.rows()
        reserved = [r for r in rows if r[1] in ("_RES 1", "_RES 1@1")]
        self.assertEqual(len(reserved), 2)
        self.assertEqual({(candidate.mapping_key(r)[0], candidate.mapping_key(r)[2])
                          for r in reserved},
                         {("_RES 1", "input"), ("_RES 1@1", "output")})
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "mapping.csv"
            with path.open("w", newline="") as stream:
                csv.writer(stream, delimiter=";").writerows(rows)
            candidate.assign_variables(str(path))
            readback = candidate.read_mapping(str(path))
            self.assertEqual(candidate.verify_mapping_rows(readback)["csv_consistency"], "PASS")

    def test_observed_ide_reserved_output_alias_is_retained_as_export_identity(self):
        rows = self.rows()
        self.assertEqual([r[1] for r in rows if r[2] == "beliebig" and
                          r[5] == candidate.DEVICE_NAME and r[4].startswith("%QB") and
                          "RES" in r[1]],
                         ["_RES 1@1", "_RES 2@1", "_RES 3@1", "_RES 4@1"])
        result = candidate.verify_mapping_rows(rows)
        aliases = [field["export_parameter"] for field in result["output"]["fields"]
                   if field["parameter"].startswith("_RES")]
        self.assertEqual(aliases, ["_RES 1@1", "_RES 2@1", "_RES 3@1", "_RES 4@1"])
        next(row for row in rows if row[1] == "_RES 1@1")[1] = "_RES 1@2"
        with self.assertRaises(Exception):
            candidate.verify_mapping_rows(rows)

    def test_labels_are_not_part_of_the_mapping_contract(self):
        rows = self.rows()
        for row in rows:
            row[2] = ""
            row[3] = ""
        self.assertEqual(candidate.verify_mapping_rows(rows)["output"]["image_bytes"], 16)

    def test_malformed_addresses_direction_alias_shift_and_gaps_fail(self):
        mutations = []
        rows = self.rows()
        rows[0][4] = "%IB0junk"
        mutations.append(rows)
        rows = self.rows()
        rows[0][4] = "%QB0"
        mutations.append(rows)
        rows = self.rows()
        rows[2][4] = "%IW0"  # overlaps the two preceding byte parameters
        mutations.append(rows)
        rows = self.rows()
        rows[3][4] = "%IB5"  # shifted channel introduces a non-descriptor stride
        mutations.append(rows)
        rows = self.rows()
        rows.pop()
        mutations.append(rows)
        for rows in mutations:
            with self.subTest(rows=rows), self.assertRaises(Exception):
                candidate.verify_mapping_rows(rows)

    def test_native_readback_rejects_wrong_type_or_unmapped_variable(self):
        class Mapping(object):
            def __init__(self, variable, exists=True):
                self.variable = variable
                self.maps_to_existing_variable = exists

        class Parameter(object):
            def __init__(self, field, bad_type=False, missing=False):
                self.id = field["id"]
                self.name = field["name"]
                self.param_type = "std:DWORD" if bad_type else field["type"]
                self.channel_type = field["direction"]
                self.has_sub_elements = False
                variable = ("Application.PLC_PRG." + field["variable"]
                            if field["variable"] else "")
                self.io_mapping = Mapping(variable, bool(variable) and not missing)

        class Connector(object):
            def __init__(self, parameters):
                self.host_parameters = parameters

        class Terminal(object):
            def __init__(self, parameters):
                self.connectors = [Connector(parameters)]

        fields = candidate.process_fields()
        valid = [Parameter(field) for field in fields]
        self.assertEqual(len(candidate.native_readback(Terminal(valid))), 24)
        inventory = candidate.native_parameter_inventory(Terminal(valid))
        self.assertEqual(len(inventory), 24)
        self.assertFalse([item for item in inventory if "mode" in item["name"].lower()])
        for index, parameter in ((0, Parameter(fields[0], bad_type=True)),
                                 (0, Parameter(fields[0], missing=True))):
            invalid = list(valid)
            invalid[index] = parameter
            with self.subTest(parameter=parameter.param_type), self.assertRaises(Exception):
                candidate.native_readback(Terminal(invalid))

    def test_reserved_output_bytes_keep_export_alias_and_explicit_zero_mapping(self):
        rows = self.rows()
        reserved = [row for row in rows if row[1].startswith("_RES") and
                    row[5] == candidate.DEVICE_NAME and row[4].startswith("%QB")]
        self.assertEqual(len(reserved), 4)
        self.assertEqual([row[0] for row in reserved], [
            "Application.PLC_PRG.PwmReservedOutput1",
            "Application.PLC_PRG.PwmReservedOutput2",
            "Application.PLC_PRG.PwmReservedOutput3",
            "Application.PLC_PRG.PwmReservedOutput4",
        ])
        result = candidate.verify_mapping_rows(rows)
        self.assertEqual(result["output"]["image_bytes"], 16)
        reserved_fields = [field for field in candidate.process_fields()
                           if field["direction"] == "output" and field["name"].startswith("_RES")]
        self.assertEqual([field["variable"] for field in reserved_fields], [
            "PwmReservedOutput1", "PwmReservedOutput2",
            "PwmReservedOutput3", "PwmReservedOutput4",
        ])


if __name__ == "__main__":
    unittest.main()
