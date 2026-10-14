"""Tests for the offline CODESYS mapping coverage summarizer."""
import importlib.util
from pathlib import Path
import stat
import tempfile
import types
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "codesys_mapping_summary", ROOT / "tools/codesys_mapping_summary.py")
summary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(summary)


class CodesysMappingSummaryTests(unittest.TestCase):
    def setUp(self):
        self.overlay = mock.patch.object(summary, "ALLOW_OVERLAY", True)
        self.overlay.start()

    def tearDown(self):
        self.overlay.stop()

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
        path.chmod(0o600)
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
            output.chmod(0o600)
            with self.assertRaisesRegex(ValueError, "refusing to overwrite"):
                summary.run(source, output, directory)
            self.assertEqual(output.read_text(encoding="utf-8"), "preserve")

    def test_run_hashes_the_same_snapshot_that_it_parses(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_mapping(directory)
            original = source.read_bytes()
            output = Path(directory) / "summary.json"
            with mock.patch.object(summary.Path, "read_bytes", autospec=True,
                                   side_effect=[original]) as read_bytes:
                report = summary.run(source, output, directory)
            self.assertEqual(read_bytes.call_count, 1)
            self.assertEqual(report["source_sha256"], summary.hashlib.sha256(original).hexdigest())

    def test_private_root_and_unc_paths_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_mapping(directory)
            outside = Path(directory).parent / "outside-summary.json"
            with self.assertRaisesRegex(ValueError, "inside the private root"):
                summary.run(source, outside, directory)
            with self.assertRaisesRegex(ValueError, "local path"):
                summary.require_local_path(r"\\server\share\mapping.csv", "input CSV")

    def test_parent_component_is_rejected_before_path_resolution(self):
        with mock.patch.object(summary, "linux_mount_type",
                               side_effect=AssertionError("must not inspect mounts")):
            with self.assertRaisesRegex(ValueError, "parent-directory component"):
                summary.require_local_path(
                    "/private/root/link/../mapping.csv", "input CSV")
        with mock.patch.object(summary.os, "name", "nt"):
            with self.assertRaisesRegex(ValueError, "parent-directory component"):
                summary.require_local_path(r"C:..\mapping.csv", "input CSV")
            with self.assertRaisesRegex(ValueError, "absolute local drive"):
                summary.require_local_path(r"C:mapping.csv", "input CSV")

    def test_windows_missing_reparse_metadata_fails_closed(self):
        metadata = types.SimpleNamespace(st_mode=stat.S_IFREG)
        with mock.patch.object(summary.os, "name", "nt"), \
                mock.patch.object(summary.os, "lstat", return_value=metadata):
            with self.assertRaisesRegex(ValueError, "cannot verify Windows reparse"):
                summary.require_no_link_components("/private/mapping.csv", "input CSV")

    def test_private_root_rejects_permissive_nested_output_directory(self):
        if summary.os.name != "posix":
            self.skipTest("POSIX permission test")
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_mapping(directory)
            nested = Path(directory) / "nested"
            nested.mkdir(mode=0o755)
            with self.assertRaisesRegex(ValueError, "group/other"):
                summary.validate_private_paths(source, nested / "report.json", directory)

    def test_private_root_rejects_permissive_input_file(self):
        if summary.os.name != "posix":
            self.skipTest("POSIX permission test")
        with tempfile.TemporaryDirectory() as directory:
            source = self.write_mapping(directory)
            source.chmod(0o644)
            with self.assertRaisesRegex(ValueError, "group/other"):
                summary.validate_private_paths(
                    source, Path(directory) / "report.json", directory)

    def test_linux_mount_type_uses_deepest_mount_and_rejects_network(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as stream:
            mountinfo = Path(stream.name)
            stream.write("1 0 0:1 / / rw - overlay overlay rw\n")
            stream.write("2 1 0:2 / /private rw - nfs server:/share rw\n")
        try:
            self.assertEqual(summary.linux_mount_type(
                "/private/data", str(mountinfo)), "nfs")
            with mock.patch.object(summary, "linux_mount_type", return_value="nfs"):
                with self.assertRaisesRegex(ValueError, "verified local filesystem"):
                    summary.require_local_posix_filesystem("/private/data", "input")
        finally:
            mountinfo.unlink()

    def test_linux_mount_type_rejects_stacked_same_path(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as stream:
            mountinfo = Path(stream.name)
            stream.write("1 0 0:1 / / rw - overlay overlay rw\n")
            stream.write("2 1 0:2 / /private rw - ext4 /dev/local rw\n")
            stream.write("3 2 0:3 / /private rw - nfs server:/share rw\n")
        try:
            with self.assertRaisesRegex(ValueError, "ambiguous stacked mountpoint"):
                summary.linux_mount_type("/private/data", str(mountinfo))
        finally:
            mountinfo.unlink()

    def test_linux_mount_type_rejects_stacked_ancestor(self):
        with tempfile.NamedTemporaryFile("w", delete=False) as stream:
            mountinfo = Path(stream.name)
            stream.write("1 0 0:1 / / rw - ext4 /dev/root-a rw\n")
            stream.write("2 1 0:2 / /private rw - ext4 /dev/private rw\n")
            stream.write("3 0 0:3 / / rw - nfs server:/root-b rw\n")
        try:
            with self.assertRaisesRegex(ValueError, "ambiguous stacked mountpoint"):
                summary.linux_mount_type("/private/data", str(mountinfo))
        finally:
            mountinfo.unlink()

    def test_posix_mount_is_checked_before_any_path_metadata(self):
        with mock.patch.object(summary, "linux_mount_type", return_value="nfs"), \
                mock.patch.object(summary.os, "lstat",
                                  side_effect=AssertionError("must not touch path")):
            with self.assertRaisesRegex(ValueError, "verified local filesystem"):
                summary.require_local_path("/network/private/mapping.csv", "input CSV")

    def test_overlay_requires_explicit_backing_storage_gate(self):
        with mock.patch.object(summary, "ALLOW_OVERLAY", False), \
                mock.patch.object(summary, "linux_mount_type", return_value="overlay"):
            with self.assertRaisesRegex(ValueError, "VIRTUALWAGO_ALLOW_OVERLAY"):
                summary.require_local_posix_filesystem("/private", "input CSV")


if __name__ == "__main__":
    unittest.main()
