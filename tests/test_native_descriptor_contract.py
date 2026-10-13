"""Synthetic declarations exercise width/pin boundaries without vendor files."""
import hashlib
import unittest

from tools.device_description_audit import AuditError
from tools.native_descriptor_contract import summarize


def fixture(parameters, types=""):
    return ('''<DeviceDescription xmlns="http://www.3s-software.com/schemas/DeviceDescription-1.0.xsd">
      %s<Device><DeviceIdentification><Type>1</Type><Id>SYNTHETIC</Id><Version>1</Version>
      </DeviceIdentification><DeviceInfo><OrderNumber>SYNTHETIC</OrderNumber></DeviceInfo>
      <Connector><HostParameterSet>%s</HostParameterSet></Connector></Device></DeviceDescription>'''
            % (types, parameters)).encode()


def parameter(pid, type_name, channel):
    return ('<Parameter ParameterId="%s" type="%s"><Attributes channel="%s"/></Parameter>'
            % (pid, type_name, channel))


class NativeDescriptorContractTests(unittest.TestCase):
    def test_two_words_are_declared_bits_without_bus_layout(self):
        data = fixture(parameter(1, "std:WORD", "input") + parameter(2, "std:WORD", "input"))
        result = summarize(data, hashlib.sha256(data).hexdigest())
        self.assertEqual(result["declared_scalar_bit_totals"], {"input": 32, "output": 0})
        self.assertEqual(result["native_process_image"], "OFFEN")
        self.assertEqual(result["register_contract"], "OFFEN")
        self.assertNotIn("offset", result["channel_declarations"][0])

    def test_source_pin_rejects_mismatch_and_noncanonical_digest(self):
        data = fixture(parameter(1, "std:WORD", "input"))
        for pin in ("0" * 64, "F" * 64, "xyz", ""):
            with self.subTest(pin=pin), self.assertRaises(AuditError):
                summarize(data, pin)

    def test_unknown_local_type_does_not_acquire_size_from_its_name(self):
        data = fixture(parameter(1, "local:DATA48", "input") + parameter(2, "std:BYTE", "input"))
        result = summarize(data, hashlib.sha256(data).hexdigest())
        self.assertIsNone(result["declared_scalar_bit_totals"]["input"])
        self.assertEqual(result["unresolved_width_parameter_ids"], ["1"])
        self.assertEqual(result["channel_declarations"][0]["width_status"], "OFFEN")

    def test_bitfield_uses_declared_base_width_without_summing_children(self):
        types = ('<Types namespace="local"><BitfieldType name="flags" basetype="std:WORD">'
                 '<Component identifier="one" type="std:BOOL"/></BitfieldType></Types>')
        data = fixture(parameter(1, "local:flags", "output"), types)
        result = summarize(data, hashlib.sha256(data).hexdigest())
        self.assertEqual(result["declared_scalar_bit_totals"]["output"], 16)

    def test_configuration_string_is_not_added_to_process_size(self):
        data = fixture(parameter(10, "std:STRING", "none") + parameter(1, "std:BYTE", "input"))
        result = summarize(data, hashlib.sha256(data).hexdigest())
        self.assertEqual(len(result["configuration_declarations"]), 1)
        self.assertEqual(result["declared_scalar_bit_totals"]["input"], 8)

    def test_missing_and_unsupported_directions_reject(self):
        for channel in ("inout", ""):
            data = fixture(parameter(1, "std:WORD", channel))
            with self.subTest(channel=channel), self.assertRaises(AuditError):
                summarize(data, hashlib.sha256(data).hexdigest())

    def test_duplicate_parameters_and_dtd_reject(self):
        for data in (fixture(parameter(1, "std:WORD", "input") * 2),
                     b'<!DOCTYPE DeviceDescription>' + fixture("")):
            with self.assertRaises(AuditError):
                summarize(data, hashlib.sha256(data).hexdigest())
