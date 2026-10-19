"""Own analog/PWM ADI profile checks compiled with authorized local headers.

This harness validates only the project's virtual adapter and V2 bridge. The
private vendor headers remain local and are never copied into this repository.
"""
from pathlib import Path
import os
import re
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DAL_INCLUDE = Path(os.environ.get("VIRTUALWAGO_PRIVATE_DAL_INCLUDE", ""))
PACKBUS_INCLUDE = Path(os.environ.get("VIRTUALWAGO_PRIVATE_LIBPACKBUS_INCLUDE", ""))
HAS_PRIVATE_HEADERS = (
    (DAL_INCLUDE / "dal/adi_application_interface.h").is_file()
    and (PACKBUS_INCLUDE / "libpackbus.h").is_file()
)


class AdiNativeIntegrationProfileTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cc"), "native C compiler unavailable")
    @unittest.skipUnless(
        HAS_PRIVATE_HEADERS,
        "NOT_RUN: authorized private ADI headers unavailable",
    )
    def test_analog_pwm_profiles_registers_frames_and_bounded_trace(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = str(Path(directory) / "adi-native-profiles")
            subprocess.run([
                "cc", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-pthread", "-DVIRTUALWAGO_ENABLE_MODEL_BRIDGE",
                "-DVIRTUALWAGO_ADI_TRACE", "-Itools",
                f"-I{DAL_INCLUDE}", f"-I{PACKBUS_INCLUDE}",
                str(ROOT / "tools/adi_digital_adapter.c"),
                str(ROOT / "tools/adi_model_bridge.c"),
                str(ROOT / "tools/adi_native_integration_profile_test.c"),
                "-o", executable,
            ], cwd=ROOT, check=True, capture_output=True, timeout=30)
            result = subprocess.run([executable], check=True, capture_output=True,
                                    text=True, timeout=20)
            self.assertEqual(result.stdout,
                             "ADI_NATIVE_INTEGRATION_PROFILE_TEST: PASS (own adapter/bridge only)\n")
            lines = result.stderr.splitlines()
            self.assertTrue(lines)
            for event in ("init", "get_iosizes", "terminal_info", "table9",
                          "read_conf_reg", "get_uid", "unknown_op",
                          "read_bytes", "write_bytes", "write_bit", "write_bool"):
                self.assertTrue(any(f" {event} " in line for line in lines), event)
            self.assertTrue(any(
                "unknown_op" in line and
                "name=DAL_capabilityProbe7" in line and
                "inner=not_written" in line
                for line in lines
            ))
            self.assertTrue(any(
                "unknown_op" in line and
                "name=UNSUPPORTED_PRIVATE_OP" in line and
                "inner=not_written" in line
                for line in lines
            ))
            self.assertTrue(any(
                "unknown_op" in line and "name=<redacted>" in line
                for line in lines
            ))
            self.assertFalse(any("UNSUPPORTED PRIVATE_OP" in line
                                 for line in lines))
            self.assertIsNone(re.search(r"0x[0-9a-fA-F]+", result.stderr))
            for event in ("init", "get_iosizes", "terminal_info", "table9",
                          "read_conf_reg", "get_uid", "unknown_op",
                          "read_bytes", "write_bytes"):
                count = sum(f" {event} " in line for line in lines)
                self.assertLessEqual(count, 8, event)


if __name__ == "__main__":
    unittest.main()
