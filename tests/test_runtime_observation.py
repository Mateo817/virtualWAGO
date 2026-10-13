"""Offline parser contract: bounded allowlisted observations only."""

import contextlib
import io
import os
import stat
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

from tools.runtime_observation import _read_optional, main, summarize_runtime


MAPS = """00400000-00401000 r-xp 00000000 08:01 10 /opt/runtime/libIoDrvDal.so.1
00600000-00601000 r--p 00000000 00:00 0 /dev/uio2
00800000-00801000 rw-p 00000000 00:00 0 [heap]
"""
FD_LINKS = """total 2
lrwx------ 1 root root 10 Oct 12 10:30 3 -> /dev/kbus0
lrwx------ 1 root root 10 Oct 12 10:30 4 -> socket:[987654]
"""
TASKS = """DAL evt dispatc
DAL_TriggerWdg
KBUS dbus
KBUS_CYCLE_TASK
WagoAsyncRtHigh
WagoAsyncBusEvt
wdbw_TermReg_Fq
not-a-DAL-task
"""


class RuntimeObservationTests(unittest.TestCase):
    def test_outputs_only_allowlisted_component_endpoint_and_thread_facts(self):
        result = summarize_runtime(MAPS, FD_LINKS, TASKS, "/srv/private/runtime")
        self.assertEqual(result["inventory"], "OFFEN")
        self.assertEqual(result["communication"], "OFFEN")
        self.assertFalse(result["integration_qualification"])
        observations = result["observations"]
        self.assertEqual(observations["components"]["libraries"], ["IoDrvDal"])
        self.assertTrue(observations["endpoints"]["kbus0_fd_present"])
        self.assertTrue(observations["endpoints"]["uio_mapping_present"])
        self.assertEqual(
            observations["threads"]["counts"],
            {"DAL": 2, "KBUS": 2, "WagoAsync": 2, "wdbw": 1},
        )
        self.assertFalse(observations["cwd"]["deleted"])
        serialized = repr(result)
        for private_value in ("/opt/runtime", "/dev/kbus0", "987654", "/srv/private"):
            self.assertNotIn(private_value, serialized)

    def test_missing_evidence_is_open_and_never_means_absent(self):
        result = summarize_runtime(None, None, None, None)
        observations = result["observations"]
        self.assertEqual(observations["components"]["evidence"], "OFFEN")
        self.assertIsNone(observations["components"]["libraries"])
        self.assertEqual(observations["endpoints"]["evidence"], "OFFEN")
        self.assertIsNone(observations["endpoints"]["kbus0_fd_present"])
        self.assertIsNone(observations["endpoints"]["uio_mapping_present"])
        self.assertIsNone(observations["threads"]["counts"])
        self.assertIsNone(observations["cwd"]["deleted"])

    def test_mapping_names_are_exact_allowlisted_basenames_and_uio_paths(self):
        maps = """1000-2000 r-xp 00000000 08:01 1 /x/libIoDrvKbus.so
2000-3000 r-xp 00000000 08:01 2 /x/fakeIoDrvDal.so
3000-4000 r-xp 00000000 08:01 3 /x/libIoDrvKbus.so.backup
4000-5000 r-xp 00000000 08:01 4 /x/dal
5000-6000 r-xp 00000000 08:01 5 /x/libdal
6000-7000 r-xp 00000000 08:01 6 /dev/uio1
7000-8000 r-xp 00000000 08:01 7 /tmp/uio0
"""
        result = summarize_runtime(maps, "total 0\n", "worker\n", None)
        self.assertEqual(result["observations"]["components"]["libraries"], ["IoDrvKbus"])
        self.assertTrue(result["observations"]["endpoints"]["uio_mapping_present"])
        self.assertFalse(result["observations"]["endpoints"]["kbus0_fd_present"])

    def test_canonical_library_filename_is_recognized_without_leaking_version_or_path(self):
        maps = "1000-2000 r-xp 00000000 08:01 1 /private/libIoDrvKbus.so.3.2\n"
        result = summarize_runtime(maps, None, None, None)
        self.assertEqual(result["observations"]["components"]["libraries"], ["IoDrvKbus"])
        self.assertNotIn("/private", repr(result))

    def test_anonymous_mapping_accepts_trailing_separator_without_path(self):
        maps = "1000-2000 rw-p 0 00:00 0 \n"
        result = summarize_runtime(maps, None, None, None)
        self.assertEqual(result["observations"]["components"]["libraries"], [])
        self.assertFalse(result["observations"]["endpoints"]["uio_mapping_present"])

    def test_kbus_descriptor_requires_exact_device_target(self):
        fds = """total 2
lrwx------ 1 root root 10 Oct 12 10:30 3 -> /dev/kbus1
lrwx------ 1 root root 10 Oct 12 10:30 4 -> /dev/kbus0-extra
"""
        result = summarize_runtime("1000-2000 rw-p 0 00:00 0 [heap]\n", fds, "worker\n", None)
        self.assertFalse(result["observations"]["endpoints"]["kbus0_fd_present"])

    def test_deleted_cwd_is_only_exposed_as_boolean(self):
        result = summarize_runtime(None, None, None, "/private/path (deleted)\n")
        cwd = result["observations"]["cwd"]
        self.assertEqual(cwd, {"evidence": "cwd_observed", "deleted": True})

    def test_cwd_accepts_one_record_newline_but_rejects_multiple_records(self):
        result = summarize_runtime(None, None, None, "/private/path\r\n")
        self.assertFalse(result["observations"]["cwd"]["deleted"])
        with self.assertRaises(ValueError):
            summarize_runtime(None, None, None, "/private/path\n/second\n")

    def test_known_runtime_task_names_are_classified_but_unknown_suffixes_are_not(self):
        names = """DAL evt dispatc
DAL_TriggerWdg
KBUS dbus
KBUS_CYCLE_TASK
WagoAsyncRtHigh
WagoAsyncBusEvt
wdbw_TermReg_Fq
WagoAsyncX
not-DAL
"""
        result = summarize_runtime(None, None, names, None)
        self.assertEqual(
            result["observations"]["threads"]["counts"],
            {"DAL": 2, "KBUS": 2, "WagoAsync": 2, "wdbw": 1},
        )

    def test_all_observed_async_worker_classes_and_repeated_events_are_counted(self):
        names = "\n".join([
            "WagoAsyncRtHigh", "WagoAsyncRtMed", "WagoAsyncRtLow",
            "WagoAsyncHigh", "WagoAsyncMed", "WagoAsyncLow", "WagoAsyncBg",
            "WagoAsyncBusCyc", "WagoAsyncBusEvt", "WagoAsyncBusEvt",
            "WagoAsyncBusEvt", "WagoAsyncBusEvt",
        ])
        result = summarize_runtime(None, None, names, None)
        self.assertEqual(result["observations"]["threads"]["counts"]["WagoAsync"], 12)

    def test_malformed_supplied_inputs_fail_closed(self):
        valid_maps = "1000-2000 rw-p 0 00:00 0 [heap]\n"
        cases = (
            ("bad map line\n", FD_LINKS, TASKS, "/tmp"),
            (valid_maps, "not an ls row\n", TASKS, "/tmp"),
            (valid_maps, FD_LINKS, "task name is too long here\n", "/tmp"),
            (valid_maps, FD_LINKS, TASKS, "relative/path"),
        )
        for args in cases:
            with self.subTest(args=args):
                with self.assertRaises(ValueError):
                    summarize_runtime(*args)

    def test_each_input_is_size_bounded(self):
        with self.assertRaisesRegex(ValueError, "size limit"):
            summarize_runtime("x" * (2 * 1024 * 1024 + 1), None, None, None)

    def test_cli_reader_rejects_device_paths_before_reading(self):
        with self.assertRaisesRegex(ValueError, "device paths"):
            _read_optional("/dev/null", 1024)

    def test_cli_reader_rejects_fifo_without_blocking(self):
        with tempfile.TemporaryDirectory() as directory:
            fifo_path = os.path.join(directory, "snapshot")
            os.mkfifo(fifo_path)
            with self.assertRaisesRegex(ValueError, "regular offline file"):
                _read_optional(fifo_path, 1024)

    def test_cli_reader_rejects_device_type_before_open(self):
        fake_device_stat = SimpleNamespace(st_mode=stat.S_IFCHR, st_dev=1, st_ino=2)
        with mock.patch("tools.runtime_observation.os.stat", return_value=fake_device_stat):
            with mock.patch("tools.runtime_observation.os.open") as open_mock:
                with self.assertRaisesRegex(ValueError, "regular offline file"):
                    _read_optional("/tmp/not-actually-a-device", 1024)
                open_mock.assert_not_called()

    def test_cli_reader_rejects_replaced_inode_without_echoing_path(self):
        with tempfile.TemporaryDirectory() as directory:
            input_path = os.path.join(directory, "captured-input")
            replacement_path = os.path.join(directory, "different-file")
            with open(input_path, "wb") as stream:
                stream.write(b"expected")
            with open(replacement_path, "wb") as stream:
                stream.write(b"replacement")
            real_open = os.open
            with mock.patch(
                "tools.runtime_observation.os.open",
                side_effect=lambda _path, flags: real_open(replacement_path, flags),
            ):
                with self.assertRaisesRegex(ValueError, "changed during open") as raised:
                    _read_optional(input_path, 1024)
            self.assertNotIn(input_path, str(raised.exception))

    def test_cli_error_does_not_echo_an_input_path(self):
        private_path = "/private/snapshot-with-secret-label"
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            result = main(["--maps", private_path])
        self.assertEqual(result, 2)
        self.assertNotIn(private_path, stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
