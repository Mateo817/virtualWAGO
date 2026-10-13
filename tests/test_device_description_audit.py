import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.device_description_audit import AuditError, audit_bytes, inspect

ROOT = Path(__file__).resolve().parents[1]
NS = "http://www.3s-software.com/schemas/DeviceDescription-1.0.xsd"


def document(extra: str = "", *, namespace: str = NS) -> str:
    components = "".join(
        f'<Component identifier="Bit{i}" type="std:BOOL"><Default>{i % 2}</Default></Component>'
        for i in range(16)
    )
    return f'''<?xml version="1.0" encoding="UTF-8"?>
<DeviceDescription xmlns="{namespace}" xmlns:evil="urn:spoof">
  <Device>
    <DeviceIdentification><Type>0001</Type><Id>750-1405</Id><Version>1.2.3.4</Version></DeviceIdentification>
    <DeviceInfo><OrderNumber>750-1405</OrderNumber><Name>Digital input</Name><Vendor>WAGO</Vendor></DeviceInfo>
    <Connector moduleType="750-1405" role="child" interface="KBus" connectorId="0" hostpath="1"/>
    <HostParameterSet>
      <Parameter ParameterId="FilterTime" type="local:FilterEnum">
        <Attributes channel="1" onlineaccess="true" offlineaccess="false"/>
        <Default>2</Default>
      </Parameter>
      <Parameter ParameterId="Unknown" type="local:MissingType"/>
    </HostParameterSet>
    {extra}
  </Device>
  <Types namespace="local">
    <Type name="FilterEnum"><BitfieldType basetype="std:WORD">{components}</BitfieldType></Type>
    <Type name="Opaque"/>
  </Types>
</DeviceDescription>'''


class DeviceDescriptionAuditTests(unittest.TestCase):
    def test_extracts_declared_metadata_and_bitfield_summary_only(self):
        data = document().encode()
        result = audit_bytes(data, display_name="synthetic.xml")
        self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
        self.assertEqual(result["device_identification"],
                         {"Type": "0001", "Id": "750-1405", "Version": "1.2.3.4"})
        self.assertEqual(result["device_info"]["OrderNumber"], "750-1405")
        self.assertEqual(result["connectors"], [{
            "moduleType": "750-1405", "role": "child", "interface": "KBus",
            "connectorId": "0", "hostpath": "1",
        }])
        params = result["host_parameters"]
        self.assertEqual(params[0]["parameter_id"], "FilterTime")
        self.assertEqual(params[0]["type_resolution"], "RESOLVED_LOCAL_DECLARATION")
        self.assertEqual(params[0]["attributes"], {
            "channel": "1", "onlineaccess": "true", "offlineaccess": "false",
        })
        self.assertEqual(params[1]["type_resolution"], "UNRESOLVED")
        bitfield = result["local_type_summaries"][0]
        self.assertEqual(bitfield["base_type"], "std:WORD")
        self.assertEqual(bitfield["component_count"], 16)
        self.assertEqual(bitfield["std_bool_component_count"], 16)
        self.assertEqual(bitfield["components_with_default_count"], 16)
        self.assertFalse(bitfield["layout_claim"])
        self.assertIn("no offsets", result["scope"])
        self.assertEqual(result["device_access"], "NOT_ATTEMPTED")
        self.assertEqual(result["network_access"], "NOT_ATTEMPTED")

    def test_foreign_namespace_spoof_is_not_treated_as_connector(self):
        data = document('<evil:Connector moduleType="spoof" connectorId="99"/>').encode()
        result = audit_bytes(data)
        self.assertEqual(len(result["connectors"]), 1)
        self.assertNotIn("spoof", json.dumps(result["connectors"]))

    def test_wrong_root_namespace_is_rejected(self):
        with self.assertRaisesRegex(AuditError, "root must be"):
            audit_bytes(document(namespace="urn:spoof").encode())

    def test_unverified_root_tag_is_rejected(self):
        with self.assertRaisesRegex(AuditError, "root must be"):
            audit_bytes(document().replace("<DeviceDescription", "<rootDeviceDescription", 1)
                        .replace("</DeviceDescription>", "</rootDeviceDescription>").encode())

    def test_device_description_root_and_direct_local_bitfield_are_supported(self):
        xml = f'''<DeviceDescription xmlns="{NS}">
          <Device>
            <DeviceIdentification><Type>32776</Type><Id>synthetic</Id><Version>1</Version></DeviceIdentification>
            <DeviceInfo><OrderNumber>synthetic</OrderNumber><Name>fixture</Name><Vendor>fixture</Vendor></DeviceInfo>
            <Connector moduleType="1" role="child" interface="fixture" connectorId="0">
              <HostParameterSet><Parameter ParameterId="P" type="local:Bits"><Default>0</Default></Parameter></HostParameterSet>
            </Connector>
          </Device>
          <Types namespace="local"><BitfieldType name="Bits" basetype="std:WORD">
            <Component identifier="Bit0" type="std:BOOL"><Default>FALSE</Default></Component>
          </BitfieldType></Types>
        </DeviceDescription>'''.encode()
        result = audit_bytes(xml)
        self.assertEqual(result["host_parameters"][0]["parameter_id"], "P")
        self.assertEqual(result["host_parameters"][0]["type_resolution"], "RESOLVED_LOCAL_DECLARATION")
        self.assertEqual(result["local_type_summaries"][0]["component_count"], 1)

    def test_dtd_rejected_in_utf8_and_utf16(self):
        xml = document().replace(
            "<?xml version=\"1.0\" encoding=\"UTF-8\"?>",
            '<!DOCTYPE rootDeviceDescription [<!ENTITY x "expanded">]>',
        )
        for data in (xml.encode("utf-8"), xml.encode("utf-16")):
            with self.subTest(encoding=data[:4]), self.assertRaisesRegex(AuditError, "DTD"):
                audit_bytes(data)

    def test_malformed_xml_and_missing_qname_are_rejected_or_left_unresolved(self):
        with self.assertRaisesRegex(AuditError, "malformed"):
            audit_bytes(b"<rootDeviceDescription>")
        # An absent local declaration is reported as unresolved rather than
        # borrowing a similarly named declaration from another namespace.
        result = audit_bytes(document().replace("local:MissingType", "localTypes:MissingType").encode())
        self.assertEqual(result["host_parameters"][1]["type_resolution"], "UNRESOLVED")

    def test_bitfield_count_is_declaration_not_physical_mapping(self):
        result = audit_bytes(document().encode())
        summary = result["local_type_summaries"][0]
        self.assertEqual(summary["component_count"], 16)
        self.assertFalse(summary["layout_claim"])
        self.assertNotIn("offset", json.dumps(summary).lower())
        self.assertNotIn("bus", json.dumps(summary).lower())

    def test_input_rejects_symlink_and_fifo_without_opening_them(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            target = base / "source.xml"
            target.write_text(document())
            link = base / "link.xml"
            link.symlink_to(target)
            with self.assertRaisesRegex(AuditError, "regular non-symlink"):
                inspect(str(link))
            fifo = base / "pipe.xml"
            os.mkfifo(fifo)
            with self.assertRaisesRegex(AuditError, "regular non-symlink"):
                inspect(str(fifo))

    def test_cli_audits_synthetic_file_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.xml"
            path.write_text(document())
            result = subprocess.run([sys.executable, "tools/device_description_audit.py", str(path)],
                                    cwd=ROOT, capture_output=True, text=True, check=True)
            report = json.loads(result.stdout)[0]
            self.assertEqual(report["status"], "PASS")
            self.assertEqual(report["display_name"], "fixture.xml")
            self.assertEqual(report["device_access"], "NOT_ATTEMPTED")


if __name__ == "__main__":
    unittest.main()
