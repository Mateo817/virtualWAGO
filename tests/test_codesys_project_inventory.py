"""Pure validation tests for the read-only CODESYS project inventory tool."""
import importlib.util
from pathlib import Path
import stat
import sys
import tempfile
import types
import unittest
from unittest import mock


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
    def setUp(self):
        self.overlay = mock.patch.object(inventory, "ALLOW_OVERLAY", True)
        self.overlay.start()

    def tearDown(self):
        self.overlay.stop()

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

    def test_private_root_rejects_escape_unc_and_public_permissions(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project.project"
            output = root / "report.json"
            project.write_bytes(b"project")
            project.chmod(0o600)
            inventory.validate_private_paths(
                str(project), str(output), None, None, str(root))
            with self.assertRaisesRegex(Exception, "inside VIRTUALWAGO_PRIVATE_ROOT"):
                inventory.validate_private_paths(
                    str(project), str(root.parent / "report.json"), None, None, str(root))
            with self.assertRaisesRegex(Exception, "local path"):
                inventory.require_local_path(r"\\server\share\project.project", "project")
            if inventory.os.name == "posix":
                root.chmod(0o755)
                with self.assertRaisesRegex(Exception, "group/other"):
                    inventory.validate_private_paths(
                        str(project), str(output), None, None, str(root))

    def test_private_root_rejects_permissive_nested_output_directory(self):
        if inventory.os.name != "posix":
            self.skipTest("POSIX permission test")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project.project"
            project.write_bytes(b"project")
            project.chmod(0o600)
            nested = root / "nested"
            nested.mkdir(mode=0o755)
            with self.assertRaisesRegex(Exception, "group/other"):
                inventory.validate_private_paths(
                    str(project), str(nested / "report.json"), None, None, str(root))

    def test_private_root_rejects_permissive_project_file(self):
        if inventory.os.name != "posix":
            self.skipTest("POSIX permission test")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project.project"
            project.write_bytes(b"project")
            project.chmod(0o644)
            with self.assertRaisesRegex(Exception, "group/other"):
                inventory.validate_private_paths(
                    str(project), str(root / "report.json"), None, None, str(root))

    def test_windows_mapped_drive_is_rejected(self):
        with mock.patch.object(inventory.os, "name", "nt"), \
                mock.patch.object(inventory.os.path, "splitdrive", return_value=("Z:", "\\x")), \
                mock.patch.object(inventory.os.path, "abspath", return_value="Z:\\x"), \
                mock.patch.object(inventory, "require_no_link_components"), \
                mock.patch.dict(sys.modules, {"ctypes": types.SimpleNamespace(
                    windll=types.SimpleNamespace(kernel32=types.SimpleNamespace(
                        GetDriveTypeW=lambda path: 4)))}):
            with self.assertRaisesRegex(Exception, "mapped network drive"):
                inventory.require_local_path("Z:\\x", "project")

    def test_parent_component_is_rejected_before_path_resolution(self):
        with mock.patch.object(inventory, "linux_mount_type",
                               side_effect=AssertionError("must not inspect mounts")):
            with self.assertRaisesRegex(Exception, "parent-directory component"):
                inventory.require_local_path(
                    "/private/root/link/../project.project", "project")
        with mock.patch.object(inventory.os, "name", "nt"):
            with self.assertRaisesRegex(Exception, "parent-directory component"):
                inventory.require_local_path(r"C:..\project.project", "project")
            with self.assertRaisesRegex(Exception, "absolute local drive"):
                inventory.require_local_path(r"C:project.project", "project")

    def test_windows_missing_reparse_metadata_fails_closed(self):
        metadata = types.SimpleNamespace(st_mode=stat.S_IFREG)
        with mock.patch.object(inventory.os, "name", "nt"), \
                mock.patch.object(inventory.os, "lstat", return_value=metadata):
            with self.assertRaisesRegex(Exception, "cannot verify Windows reparse"):
                inventory.require_no_link_components("/private/project", "project")

    def test_error_receipt_is_suppressed_until_all_paths_are_validated(self):
        previous_path = inventory.ERROR_PATH
        previous_validated = inventory.ERROR_OUTPUT_VALIDATED
        try:
            inventory.ERROR_PATH = r"\\server\share\error.json"
            inventory.ERROR_OUTPUT_VALIDATED = False
            with mock.patch.object(inventory.os.path, "exists",
                                   side_effect=AssertionError("must not inspect path")), \
                    mock.patch.object(inventory, "write_exclusive") as write:
                self.assertFalse(inventory.write_error_receipt(Exception("failure")))
                write.assert_not_called()
        finally:
            inventory.ERROR_PATH = previous_path
            inventory.ERROR_OUTPUT_VALIDATED = previous_validated

    def test_run_does_not_enable_error_receipt_for_missing_parent(self):
        previous = (inventory.PROJECT_PATH, inventory.OUTPUT_PATH,
                    inventory.MAPPING_PATH, inventory.ERROR_PATH,
                    inventory.PRIVATE_ROOT, inventory.ERROR_OUTPUT_VALIDATED)
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            project = root / "project.project"
            project.write_bytes(b"project")
            project.chmod(0o600)
            inventory.PROJECT_PATH = str(project)
            inventory.OUTPUT_PATH = str(root / "report.json")
            inventory.MAPPING_PATH = None
            inventory.ERROR_PATH = str(root / "missing" / "error.json")
            inventory.PRIVATE_ROOT = str(root)
            inventory.ERROR_OUTPUT_VALIDATED = False
            try:
                with self.assertRaisesRegex(Exception, "ERROR_OUTPUT"):
                    inventory.run()
                self.assertFalse(inventory.ERROR_OUTPUT_VALIDATED)
                self.assertFalse(inventory.write_error_receipt(Exception("original")))
            finally:
                (inventory.PROJECT_PATH, inventory.OUTPUT_PATH,
                 inventory.MAPPING_PATH, inventory.ERROR_PATH,
                 inventory.PRIVATE_ROOT,
                 inventory.ERROR_OUTPUT_VALIDATED) = previous

    def test_linux_mount_type_uses_deepest_mount_and_rejects_network(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as stream:
            mountinfo = Path(stream.name)
            stream.write("1 0 0:1 / / rw - overlay overlay rw\n")
            stream.write("2 1 0:2 / /private rw - nfs server:/share rw\n")
        try:
            self.assertEqual(inventory.linux_mount_type(
                "/private/data", str(mountinfo)), "nfs")
            with mock.patch.object(inventory, "linux_mount_type", return_value="nfs"):
                with self.assertRaisesRegex(Exception, "verified local filesystem"):
                    inventory.require_local_posix_filesystem("/private/data", "project")
        finally:
            mountinfo.unlink()

    def test_linux_mount_type_rejects_stacked_same_path(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as stream:
            mountinfo = Path(stream.name)
            stream.write("1 0 0:1 / / rw - overlay overlay rw\n")
            stream.write("2 1 0:2 / /private rw - ext4 /dev/local rw\n")
            stream.write("3 2 0:3 / /private rw - nfs server:/share rw\n")
        try:
            with self.assertRaisesRegex(Exception, "ambiguous stacked mountpoint"):
                inventory.linux_mount_type("/private/data", str(mountinfo))
        finally:
            mountinfo.unlink()

    def test_linux_mount_type_rejects_stacked_ancestor(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as stream:
            mountinfo = Path(stream.name)
            stream.write("1 0 0:1 / / rw - ext4 /dev/root-a rw\n")
            stream.write("2 1 0:2 / /private rw - ext4 /dev/private rw\n")
            stream.write("3 0 0:3 / / rw - nfs server:/root-b rw\n")
        try:
            with self.assertRaisesRegex(Exception, "ambiguous stacked mountpoint"):
                inventory.linux_mount_type("/private/data", str(mountinfo))
        finally:
            mountinfo.unlink()

    def test_posix_mount_is_checked_before_any_path_metadata(self):
        with mock.patch.object(inventory, "linux_mount_type", return_value="nfs"), \
                mock.patch.object(inventory.os, "lstat",
                                  side_effect=AssertionError("must not touch path")):
            with self.assertRaisesRegex(Exception, "verified local filesystem"):
                inventory.require_local_path("/network/private/project", "project")

    def test_overlay_requires_explicit_backing_storage_gate(self):
        with mock.patch.object(inventory, "ALLOW_OVERLAY", False), \
                mock.patch.object(inventory, "linux_mount_type", return_value="overlay"):
            with self.assertRaisesRegex(Exception, "VIRTUALWAGO_ALLOW_OVERLAY"):
                inventory.require_local_posix_filesystem("/private", "project")


if __name__ == "__main__":
    unittest.main()
