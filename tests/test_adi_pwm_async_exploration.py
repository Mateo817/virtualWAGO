"""Optional private-header checks for the explicitly synthetic PWM experiment."""
from pathlib import Path
import os
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
DAL = Path(os.environ.get("VIRTUALWAGO_PRIVATE_DAL_INCLUDE", ""))
PACKBUS = Path(os.environ.get("VIRTUALWAGO_PRIVATE_LIBPACKBUS_INCLUDE", ""))
HEADERS = (DAL / "dal/adi_application_interface.h").is_file() and (PACKBUS / "libpackbus.h").is_file()


class PwmAsyncExplorationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cc") and HEADERS,
                         "NOT_RUN: compiler or authorized private ADI headers unavailable")
    def test_opt_in_handles_lifecycle_and_default_unsupported(self):
        with tempfile.TemporaryDirectory() as directory:
            for enabled in (False, True):
                with self.subTest(exploration=enabled):
                    executable = str(Path(directory) / ("on" if enabled else "off"))
                    flags = ["-DVIRTUALWAGO_PWM_ASYNC_EXPLORATION"] if enabled else []
                    subprocess.run([
                        "cc", "-std=gnu11", "-O2", "-Wall", "-Wextra", "-Werror",
                        "-pthread", "-Itools", f"-I{DAL}", f"-I{PACKBUS}",
                        "-DVIRTUALWAGO_ADI_TRACE", "-DVIRTUALWAGO_DEFAULT_PWM677", *flags,
                        "tools/adi_digital_adapter.c", "tools/adi_pwm_async_exploration_test.c",
                        "-o", executable,
                    ], cwd=ROOT, check=True, capture_output=True, timeout=30)
                    result = subprocess.run([executable], check=True, capture_output=True,
                                            text=True, timeout=10)
                    self.assertEqual(result.stdout, "PWM_ASYNC_EXPLORATION_TEST_PASS\n")
                    self.assertEqual("synthetic_async_open" in result.stderr, enabled)
