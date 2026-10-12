"""Tests for the bounded seccomp open mediator; protected test file is synthetic."""
from pathlib import Path
import os
import re
import signal
import time
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
TEST_PATH = "/dev/shm/virtualwago-metadata-test"


# Linked only into own test binaries. Real kernel notification ioctls still run
# except the explicitly injected transient; no hardware paths are exercised.
FAULT_SHIM = r"""
#define _GNU_SOURCE
#include <errno.h>
#include <linux/seccomp.h>
#include <poll.h>
#include <stdarg.h>
#include <stdlib.h>
#include <string.h>
#include <sys/ioctl.h>
#include <time.h>
#include <unistd.h>
int __real_ioctl(int, unsigned long, ...);
int __real_poll(struct pollfd *, nfds_t, int);
static long started_ms;
static int injected, received;
static long milliseconds(void) {
  struct timespec now;
  if (clock_gettime(CLOCK_MONOTONIC, &now) != 0) _exit(90);
  return now.tv_sec * 1000L + now.tv_nsec / 1000000L;
}
static const char *fault(void) {
  const char *mode = getenv("VIRTUALWAGO_OWN_TEST_FAULT");
  return mode == NULL ? "" : mode;
}
int __wrap_ioctl(int fd, unsigned long request, ...) {
  va_list arguments;
  va_start(arguments, request);
  void *argument = va_arg(arguments, void *);
  va_end(arguments);
  if (started_ms == 0) started_ms = milliseconds();
  const char *mode = fault();
  if (milliseconds() - started_ms >= 120 && !injected &&
      ((request == SECCOMP_IOCTL_NOTIF_SEND && strcmp(mode, "send_once") == 0) ||
       (request == SECCOMP_IOCTL_NOTIF_ID_VALID && strcmp(mode, "id_once") == 0) ||
       (request == SECCOMP_IOCTL_NOTIF_ADDFD && strcmp(mode, "addfd_once") == 0))) {
    injected = 1;
    errno = EINTR;
    return -1;
  }
  if (request == SECCOMP_IOCTL_NOTIF_SEND && strcmp(mode, "send_forever") == 0) {
    errno = EINTR;
    return -1;
  }
  if (request == SECCOMP_IOCTL_NOTIF_ADDFD && strcmp(mode, "addfd_delayed") == 0 &&
      !injected && milliseconds() - started_ms >= 120) {
    injected = 1;
    /* The old periodic signal interrupts a blocking atomic-grant interval;
     * the new handler timer leaves it uninterrupted until the global bound. */
    if (__real_poll(NULL, 0, 180) < 0) return -1;
  }
  int result = __real_ioctl(fd, request, argument);
  if (request == SECCOMP_IOCTL_NOTIF_RECV && result == 0) received = 1;
  return result;
}
int __wrap_poll(struct pollfd *fds, nfds_t count, int timeout) {
  const char *mode = fault();
  if (received && count == 1 && fds[0].fd >= 0 &&
      milliseconds() - started_ms >= 120 &&
      (strcmp(mode, "pollerr_forever") == 0 ||
       (!injected && strcmp(mode, "pollerr_once") == 0))) {
    injected = 1;
    fds[0].revents = POLLERR;
    return 1;
  }
  return __real_poll(fds, count, timeout);
}
"""


class ReadonlyMetadataBrokerTests(unittest.TestCase):
    def _compile_broker(self, output: Path, *, test_path: str | None = None,
                        fault_shim: bool = False) -> None:
        command = ["cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-O2"]
        if test_path is not None:
            command.append(f'-DVIRTUALWAGO_METADATA_TEST_FILE="{test_path}"')
        command += [str(ROOT / "tools/readonly_metadata_broker.c")]
        if fault_shim:
            shim = output.with_suffix(".shim.c")
            shim.write_text(FAULT_SHIM)
            command += [str(shim), "-Wl,--wrap=ioctl,--wrap=poll"]
        command += ["-o", str(output)]
        subprocess.run(command, check=True, capture_output=True, timeout=30)

    def _compile_probe(self, output: Path, test_path: str) -> None:
        command = ["cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-O2",
                   f'-DVIRTUALWAGO_METADATA_TEST_FILE="{test_path}"',
                   str(ROOT / "tools/readonly_metadata_broker_test.c"), "-o", str(output)]
        subprocess.run(command, check=True, capture_output=True, timeout=30)

    @unittest.skipUnless(shutil.which("cc"), "C compiler unavailable")
    def test_native_supervisor_bounds(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            broker = Path(temp_dir) / "readonly_metadata_broker"
            harness = Path(temp_dir) / "readonly_metadata_broker_test"
            self._compile_broker(broker)
            subprocess.run(["cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-O2",
                            str(ROOT / "tools/readonly_metadata_broker_test.c"),
                            "-o", str(harness)], check=True, capture_output=True, timeout=30)
            native = subprocess.run([str(harness), str(broker)], capture_output=True,
                                    text=True, timeout=10)
            if native.returncode == 77:
                self.skipTest(native.stdout.strip())
            self.assertEqual(native.returncode, 0, native.stderr)
            self.assertIn("PASS (native supervisor bounds only)", native.stdout)
            diagnostic = subprocess.run([str(broker), "--diagnostics", "--timeout", "3",
                                         "--", "/bin/true"], capture_output=True,
                                        text=True, timeout=6)
            self.assertEqual(diagnostic.returncode, 0, diagnostic.stderr)
            self.assertIn("METADATA_BROKER_EXEC_ATTEMPT\n", diagnostic.stderr)
            self.assertRegex(diagnostic.stderr,
                             r"METADATA_BROKER exit=0 notified=\d+ continued=\d+ "
                             r"protected=0 mediated=0 path_errors=0 last_path_errno=0")
            self.assertNotIn("/bin/true", diagnostic.stderr)
            self.assertNotIn("/dev/eeprom", diagnostic.stderr)

        # A tmpfs regular file without a read-only mount must be refused before
        # the broker opens a data descriptor. This test never references eeprom.
        if not Path("/dev/shm").is_dir():
            self.skipTest("tmpfs fixture directory unavailable")
        with tempfile.TemporaryDirectory(dir="/dev/shm") as fixture_dir:
            protected = str(Path(fixture_dir) / "metadata")
            content = b"synthetic-writable-tmpfs-fixture\n"
            Path(protected).write_bytes(content)
            with tempfile.TemporaryDirectory() as build_dir:
                broker = Path(build_dir) / "broker-test-variant"
                probe = Path(build_dir) / "probe-test-variant"
                self._compile_broker(broker, test_path=protected)
                self._compile_probe(probe, protected)
                refusal = subprocess.run([str(broker), "--timeout", "3", "--",
                                          str(probe), "--probe-readonly"],
                                         capture_output=True, timeout=6)
                self.assertEqual(refusal.returncode, 51,
                                 "broker did not fail closed on writable tmpfs")
            self.assertEqual(Path(protected).read_bytes(), content)

    @unittest.skipUnless(shutil.which("cc"), "C compiler unavailable")
    def test_sustained_opens_interruption_and_control_faults(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            broker = Path(temp_dir) / "broker"
            probe = Path(temp_dir) / "probe"
            self._compile_broker(broker, fault_shim=True)
            self._compile_probe(probe, TEST_PATH)
            command = [str(broker), "--diagnostics", "--timeout", "3", "--",
                       str(probe), "--stress-unprotected"]
            for mode in ("", "send_once", "id_once", "pollerr_once"):
                with self.subTest(mode=mode):
                    environment = dict(os.environ, VIRTUALWAGO_OWN_TEST_FAULT=mode)
                    before = time.monotonic()
                    result = subprocess.run(command, env=environment, capture_output=True,
                                            text=True, timeout=6)
                    self.assertEqual(result.returncode, 0, result.stderr)
                    self.assertGreaterEqual(time.monotonic() - before, 0.6)
                    self.assertRegex(result.stderr, r"kill_reason=0 .*child_signal=0")
                    if mode in ("send_once", "id_once"):
                        self.assertIn("last_control_errno=4", result.stderr)
            for mode, expected in (("send_forever", 137), ("pollerr_forever", 124)):
                with self.subTest(mode=mode):
                    environment = dict(os.environ, VIRTUALWAGO_OWN_TEST_FAULT=mode)
                    before = time.monotonic()
                    result = subprocess.run(command[:3] + ["1"] + command[4:],
                                            env=environment, capture_output=True,
                                            text=True, timeout=4)
                    self.assertEqual(result.returncode, expected, result.stderr)
                    self.assertLess(time.monotonic() - before, 2.5)
                    if mode == "send_forever":
                        self.assertIn("kill_reason=5 last_control_errno=4", result.stderr)
            # Signals are sent only to this own broker PID, never its child or
            # another process. Sustained unrelated traffic must tolerate them.
            with subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  text=True) as runner:
                time.sleep(0.18)
                for _ in range(15):
                    if runner.poll() is not None:
                        break
                    os.kill(runner.pid, signal.SIGALRM)
                    time.sleep(0.012)
                stdout, stderr = runner.communicate(timeout=6)
                self.assertEqual(runner.returncode, 0, stderr)
                self.assertIn("kill_reason=0", stderr)
                self.assertNotIn("/dev/eeprom", stdout + stderr)
            external = subprocess.run(command[:-1] + ["--self-kill"], capture_output=True,
                                      text=True, timeout=6)
            self.assertEqual(external.returncode, 137, external.stderr)
            self.assertIn("kill_reason=0 last_control_errno=0 child_signal=9", external.stderr)

    @unittest.skipUnless(shutil.which("cc"), "C compiler unavailable")
    def test_synthetic_readonly_file_mediation(self):
        configured_bwrap = os.environ.get("VIRTUALWAGO_TEST_BWRAP")
        if configured_bwrap:
            bwrap_path = Path(configured_bwrap)
            if (not bwrap_path.is_absolute() or bwrap_path.is_symlink() or
                    not bwrap_path.is_file() or not os.access(bwrap_path, os.X_OK)):
                self.fail("VIRTUALWAGO_TEST_BWRAP must name an absolute executable regular file")
            bwrap = str(bwrap_path)
        else:
            bwrap = shutil.which("bwrap")
        if bwrap is None:
            self.skipTest("bubblewrap unavailable; protected-file mediation not run")
        if not hasattr(os, "memfd_create"):
            self.skipTest("memfd_create unavailable for isolated tmpfs fixture")
        with tempfile.TemporaryDirectory() as temp_dir:
            variant = Path(temp_dir) / "readonly_metadata_broker_tmpfs_test"
            probe = Path(temp_dir) / "readonly_metadata_probe"
            # The isolated test variant accepts only this private synthetic path
            # and TMPFS_MAGIC; the release binary accepts only /dev/eeprom/SYSFS.
            self._compile_broker(variant, test_path=TEST_PATH, fault_shim=True)
            self._compile_probe(probe, TEST_PATH)
            fixture_fd = os.memfd_create("metadata-fixture", flags=0)
            payload = b"synthetic-metadata-v1\n"
            os.write(fixture_fd, payload)
            os.lseek(fixture_fd, 0, os.SEEK_SET)
            script = (
                "set -e; "
                f"test \"$(cat {TEST_PATH})\" = synthetic-metadata-v1; "
                f"if printf damage > {TEST_PATH} 2>/dev/null; then exit 41; fi; "
                f"if printf damage >> {TEST_PATH} 2>/dev/null; then exit 44; fi; "
                f"test \"$(cat {TEST_PATH})\" = synthetic-metadata-v1"
            )
            prefix = [bwrap, "--die-with-parent", "--unshare-all", "--cap-drop", "ALL",
                      "--clearenv", "--setenv", "PATH", "/usr/bin:/bin"]
            for system_path in ("/usr", "/bin", "/lib", "/lib64"):
                if Path(system_path).exists():
                    prefix += ["--ro-bind", system_path, system_path]
            base_prefix = prefix + ["--dev", "/dev", "--proc", "/proc",
                       "--tmpfs", "/tmp", "--tmpfs", "/opt",
                       "--ro-bind", str(variant), "/opt/metadata-broker",
                       "--ro-bind", str(probe), "/opt/metadata-probe"]
            prefix = base_prefix + ["--ro-bind-data", str(fixture_fd), TEST_PATH]
            command = prefix + ["--", "/bin/sh", "-c",
                       "/opt/metadata-broker --timeout 5 -- /opt/metadata-probe --probe-readonly && "
                       f"/opt/metadata-broker --timeout 5 -- /bin/sh -c '{script}'"]
            probe_result = subprocess.run(base_prefix + ["--", "/bin/true"],
                                          capture_output=True, text=True, timeout=10)
            if probe_result.returncode != 0:
                os.close(fixture_fd)
                message = "bubblewrap namespace unavailable: " + probe_result.stderr[-300:]
                if configured_bwrap:
                    self.fail(message)
                self.skipTest(message)
            result = subprocess.run(command, pass_fds=(fixture_fd,), capture_output=True,
                                    text=True, timeout=10)
            os.lseek(fixture_fd, 0, os.SEEK_SET)
            self.assertEqual(os.read(fixture_fd, len(payload)), payload)
            self.assertEqual(result.returncode, 0, result.stderr)
            try:
                for mode, expected in (("", 0), ("send_once", 0), ("id_once", 0),
                                       ("pollerr_once", 0), ("addfd_delayed", 0),
                                       ("addfd_once", 137)):
                    with self.subTest(protected_fault=mode):
                        protected_command = prefix + ["--setenv", "VIRTUALWAGO_OWN_TEST_FAULT", mode,
                            "--", "/opt/metadata-broker", "--diagnostics", "--timeout", "3",
                            "--", "/opt/metadata-probe", "--stress-protected"]
                        os.lseek(fixture_fd, 0, os.SEEK_SET)
                        before = time.monotonic()
                        stress = subprocess.run(protected_command, pass_fds=(fixture_fd,),
                                                capture_output=True, text=True, timeout=6)
                        self.assertEqual(stress.returncode, expected, stress.stderr)
                        if expected == 0:
                            self.assertGreaterEqual(time.monotonic() - before, 0.6)
                            self.assertIn("kill_reason=0", stress.stderr)
                            match = re.search(r"protected=(\d+) mediated=(\d+)", stress.stderr)
                            self.assertIsNotNone(match, stress.stderr)
                            self.assertGreater(int(match[1]), 2)
                            self.assertEqual(match[1], match[2])
                        else:
                            self.assertIn("kill_reason=9 last_control_errno=4 child_signal=9",
                                          stress.stderr)
                os.lseek(fixture_fd, 0, os.SEEK_SET)
                self.assertEqual(os.read(fixture_fd, len(payload)), payload)
            finally:
                os.close(fixture_fd)


if __name__ == "__main__":
    unittest.main()
