"""Compile and run the own ADI byte-buffer harness with authentic local headers.

Vendor/private headers are intentionally not committed. Set
VIRTUALWAGO_PRIVATE_DAL_INCLUDE and VIRTUALWAGO_PRIVATE_LIBPACKBUS_INCLUDE in
engineering environments that have the authorized headers; public CI skips
this source-bound harness when those local inputs are unavailable.
"""
from pathlib import Path
import os
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


class AdiByteBufferTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cc"), "native C compiler unavailable")
    @unittest.skipUnless(
        HAS_PRIVATE_HEADERS,
        "NOT_RUN: authorized private ADI headers unavailable",
    )
    def test_bounded_byte_frames_and_full_bit_coverage(self):
        with tempfile.TemporaryDirectory() as directory:
            executable = str(Path(directory) / "adi-byte-buffer")
            subprocess.run([
                "cc", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror",
                "-pthread", "-DVIRTUALWAGO_ENABLE_MODEL_BRIDGE",
                "-DVIRTUALWAGO_TEST_PROFILE_EXTENTS", "-Itools",
                f"-I{DAL_INCLUDE}", f"-I{PACKBUS_INCLUDE}",
                str(ROOT / "tools/adi_digital_adapter.c"),
                str(ROOT / "tools/adi_model_bridge.c"),
                str(ROOT / "tools/adi_byte_buffer_test.c"), "-o", executable,
            ], cwd=ROOT, check=True, capture_output=True, timeout=30)
            result = subprocess.run([executable], check=True, capture_output=True,
                                    text=True, timeout=15)
            self.assertEqual(result.stdout,
                             "ADI byte buffer harness: PASS (own test-profile adapter only)\n")
