"""Real private D-Bus integration; no host bus, activation or vendor service."""
import os
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]


class NativePrivateBusTests(unittest.TestCase):
    def run_isolated(self, command):
        bwrap = os.environ.get("VIRTUALWAGO_TEST_BWRAP") or shutil.which("bwrap")
        self.assertTrue(bwrap, "namespace-test dependency bwrap is required")
        args = [bwrap, "--die-with-parent", "--unshare-net", "--unshare-ipc",
                "--unshare-pid", "--cap-drop", "ALL", "--clearenv",
                "--ro-bind", "/usr", "/usr", "--ro-bind", "/bin", "/bin",
                "--symlink", "usr/lib", "/lib", "--ro-bind", "/etc", "/etc",
                "--ro-bind", str(ROOT), "/research", "--dev", "/dev",
                "--proc", "/proc", "--tmpfs", "/run", "--tmpfs", "/tmp",
                "--tmpfs", "/sys", "--dir", "/var", "--symlink", "../run",
                "/var/run", "--setenv", "PATH", "/usr/bin:/bin"]
        if Path("/lib64").exists():
            args += ["--ro-bind", "/lib64", "/lib64"]
        return subprocess.run(args + ["/bin/sh", "-c", command],
                              capture_output=True, text=True, timeout=15)

    def test_real_bus_has_no_led_service_or_activation(self):
        result = self.run_isolated("""
exec /bin/sh /research/tools/native_private_bus.sh \
 /research/config/native-private-dbus.conf /bin/sh -c '
set -eu
dbus-send --system --print-reply --reply-timeout=1000 \
 --dest=org.freedesktop.DBus /org/freedesktop/DBus \
 org.freedesktop.DBus.ListActivatableNames
if dbus-send --system --print-reply --reply-timeout=1000 \
 --dest=org.freedesktop.DBus /org/freedesktop/DBus \
 org.freedesktop.DBus.StartServiceByName string:wago.ledserver uint32:0; then
 exit 91
fi
'
""")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('string "org.freedesktop.DBus"', result.stdout)
        self.assertNotIn('string "wago.', result.stdout)
        self.assertIn("org.freedesktop.DBus.Error.ServiceUnknown", result.stderr)

    def test_child_exit_is_preserved_and_daemon_is_reaped(self):
        result = self.run_isolated("""
set +e
/bin/sh /research/tools/native_private_bus.sh \
 /research/config/native-private-dbus.conf /bin/sh -c 'exit 23'
result=$?
[ "$result" = 23 ] || exit 92
for p in /proc/[0-9]*/comm; do
 [ -r "$p" ] || continue
 read -r name < "$p"
 [ "$name" != dbus-daemon ] || exit 93
done
exit 0
""")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
