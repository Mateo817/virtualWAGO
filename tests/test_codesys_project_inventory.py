"""Pure validation tests for the read-only CODESYS project inventory tool."""
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest


ROOT = Path(__file__).resolve().parents[1]
SCRIPTENGINE_STUB = types.ModuleType("scriptengine")
PREVIOUS_SCRIPTENGINE = sys.modules.get("scriptengine")
sys.modules["scriptengine"] = SCRIPTENGINE_STUB
try:
    spec = importlib.util.spec_from_file_location(
        "codesys_project_inventory", ROOT / "tools/codesys_project_inventory.py")
    inventory = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(inventory)
finally:
    if PREVIOUS_SCRIPTENGINE is None:
        del sys.modules["scriptengine"]
    else:
        sys.modules["scriptengine"] = PREVIOUS_SCRIPTENGINE


class CodesysProjectInventoryTests(unittest.TestCase):
    def payload(self):
        return {
            "scope": "read-only offline project inventory",
            "project_sha256_before": "a" * 64,
            "project_sha256_after": "a" * 64,
            "devices": [{"identity": {
                "type": 4096, "id": "1006 1209", "version": "6.4.6.11"}}],
            "mapping_export": {"sha256": "b" * 64, "size_bytes": 123},
        }

    def test_accepts_complete_unchanged_inventory(self):
        payload = self.payload()
        self.assertIs(inventory.validate_inventory(payload), payload)
        self.assertEqual(inventory.select_controller(payload["devices"]), payload["devices"][0])

    def test_rejects_changed_project(self):
        payload = self.payload()
        payload["project_sha256_after"] = "c" * 64
        with self.assertRaisesRegex(Exception, "project bytes changed"):
            inventory.validate_inventory(payload)

    def test_rejects_incomplete_device_identity(self):
        payload = self.payload()
        payload["devices"][0]["identity"]["version"] = ""
        with self.assertRaisesRegex(Exception, "identity is incomplete"):
            inventory.validate_inventory(payload)

    def test_rejects_empty_mapping_evidence(self):
        payload = self.payload()
        payload["mapping_export"]["size_bytes"] = 0
        with self.assertRaisesRegex(Exception, "mapping export evidence"):
            inventory.validate_inventory(payload)

    def test_requires_unique_controller(self):
        with self.assertRaisesRegex(Exception, "exactly one controller"):
            inventory.select_controller([])
        with self.assertRaisesRegex(Exception, "exactly one controller"):
            inventory.select_controller(self.payload()["devices"] * 2)

    def test_collects_placeholder_resolution_without_dependencies(self):
        reference = types.SimpleNamespace(
            name="#WagoSysKbusServices", namespace="Kbus", is_placeholder=True,
            is_managed=False, system_library=False,
            placeholder_name="WagoSysKbusServices", default_resolution="default",
            effective_resolution="WagoSysKbusServices, 1.2.3.4 (WAGO)",
            resolution_info="device resolution")
        manager = types.SimpleNamespace(references=[reference])
        application = types.SimpleNamespace(
            get_name=lambda: "Application", has_library_manager=True,
            get_library_manager=lambda: manager)
        project = types.SimpleNamespace(has_library_manager=False,
                                        get_children=lambda recursive: [application])
        self.assertEqual(inventory.collect_library_managers(project), [{
            "owner": "Application",
            "references": [{
                "name": "#WagoSysKbusServices", "namespace": "Kbus",
                "is_placeholder": True, "is_managed": False,
                "system_library": False,
                "placeholder_name": "WagoSysKbusServices",
                "default_resolution": "default",
                "effective_resolution": "WagoSysKbusServices, 1.2.3.4 (WAGO)",
                "resolution_info": "device resolution",
            }],
        }])

    def test_output_paths_must_be_distinct_after_normalization(self):
        with tempfile.TemporaryDirectory() as directory:
            report = str(Path(directory) / "report.json")
            alias = str(Path(directory) / "subdir" / ".." / "report.json")
            with self.assertRaisesRegex(Exception, "must be distinct"):
                inventory.require_distinct_outputs(report, alias, None)

    def test_exclusive_write_preserves_existing_file(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "receipt.json"
            inventory.write_exclusive(str(path), b"first")
            with self.assertRaises(OSError):
                inventory.write_exclusive(str(path), b"second")
            self.assertEqual(path.read_bytes(), b"first")


if __name__ == "__main__":
    unittest.main()
