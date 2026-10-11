import json
import os
from pathlib import Path
import stat
import subprocess
import sys
import tempfile
import unittest

from tools.offline_sandbox import (
    SandboxError,
    build_bwrap_command,
    _capture_bwrap,
    _prepare_qemu_mountpoint,
    plan,
    scan_rootfs,
    snapshot_qemu,
    snapshot_rootfs,
    validate_qemu,
)

ROOT = Path(__file__).resolve().parents[1]


def make_elf64(path: Path, interpreter: bool = False, needed: bool = False) -> None:
    ident = bytearray(16)
    ident[:7] = b"\x7fELF\x02\x01\x01"
    header = bytearray(48)
    header[0:2] = (2).to_bytes(2, "little")
    header[2:4] = (62).to_bytes(2, "little")
    header[4:8] = (1).to_bytes(4, "little")
    header[16:24] = (64).to_bytes(8, "little")
    header[36:40] = (64).to_bytes(4, "little")
    header[38:40] = (56).to_bytes(2, "little")
    header[40:42] = (1).to_bytes(2, "little")
    program = bytearray(56)
    program[0:4] = (2 if needed else (3 if interpreter else 1)).to_bytes(4, "little")
    dynamic = b""
    if needed:
        program[8:16] = (120).to_bytes(8, "little")
        program[32:40] = (32).to_bytes(8, "little")
        dynamic = (1).to_bytes(8, "little") + bytes(24)
    path.write_bytes(bytes(ident + header + program) + dynamic)
    path.chmod(0o755)


class OfflineSandboxTests(unittest.TestCase):
    def make_rootfs(self, root: Path) -> Path:
        for relative in ("tmp", "dev", "proc", "opt/research", "bin"):
            (root / relative).mkdir(parents=True, exist_ok=True)
        executable = root / "bin/probe"
        executable.write_bytes(b"synthetic guest fixture\n")
        executable.chmod(0o755)
        return root

    def test_default_plan_is_sanitized_and_does_not_execute(self):
        rendered = plan()
        self.assertEqual(rendered["status"], "PLAN_ONLY")
        self.assertFalse(rendered["setup_performed"])
        self.assertFalse(rendered["guest_code_executed"])
        self.assertFalse(rendered["network_access_attempted"])
        self.assertIsNone(rendered["rootfs_counts"])
        self.assertNotIn("/home/", json.dumps(rendered))

    def test_default_cli_prints_plan_only(self):
        result = subprocess.run([sys.executable, "tools/offline_sandbox.py"], cwd=ROOT,
                                capture_output=True, text=True, check=True)
        plan_row = json.loads(result.stdout)
        self.assertEqual(plan_row["status"], "PLAN_ONLY")
        self.assertFalse(plan_row["guest_code_executed"])

    def test_rootfs_scan_accepts_safe_guest_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "rootfs"
            root.mkdir()
            (root / "bin").mkdir()
            (root / "bin/probe").write_bytes(b"probe")
            (root / "probe-link").symlink_to("bin/probe")
            counts = scan_rootfs(str(root))
            self.assertEqual(counts["regular_files"], 1)
            self.assertEqual(counts["symlinks"], 1)
            self.assertEqual(counts["bytes"], 5)

    def test_rootfs_scan_rejects_escaping_symlink(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "rootfs"
            root.mkdir()
            (root / "escape").symlink_to("../../host-private")
            with self.assertRaisesRegex(SandboxError, "escapes"):
                scan_rootfs(str(root))

    def test_rootfs_scan_rejects_special_files(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "rootfs"
            root.mkdir()
            os.mkfifo(root / "fifo")
            with self.assertRaisesRegex(SandboxError, "special file"):
                scan_rootfs(str(root))

    def test_rootfs_scan_rejects_host_keys_and_license_material(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "rootfs"
            ssh = root / "etc/ssh"
            ssh.mkdir(parents=True)
            (ssh / "ssh_host_ed25519_key").write_text("synthetic secret fixture")
            with self.assertRaisesRegex(SandboxError, "host-key or license"):
                scan_rootfs(str(root))

    def test_rootfs_scan_rejects_external_hardlinks(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "rootfs"
            root.mkdir()
            inside = root / "file"
            inside.write_bytes(b"fixture")
            os.link(inside, base / "outside-link")
            with self.assertRaisesRegex(SandboxError, "hard-linked outside"):
                scan_rootfs(str(root))

    def test_rootfs_snapshot_is_private_and_preserves_safe_links(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            root = base / "source"
            root.mkdir()
            (root / "bin").mkdir()
            (root / "bin/probe").write_bytes(b"guest probe")
            (root / "probe-link").symlink_to("bin/probe")
            target = base / "private-snapshot"
            target.mkdir(mode=0o700)
            counts = snapshot_rootfs(str(root), str(target))
            self.assertEqual(counts["regular_files"], 1)
            self.assertEqual((target / "bin/probe").read_bytes(), b"guest probe")
            self.assertEqual(os.readlink(target / "probe-link"), "bin/probe")
            self.assertEqual(stat.S_IMODE(base.stat().st_mode), 0o700)

    def test_private_snapshot_gets_regular_qemu_mountpoint(self):
        with tempfile.TemporaryDirectory() as directory:
            root = self.make_rootfs(Path(directory) / "rootfs")
            mountpoint = root / "opt/research/qemu-arm"
            self.assertFalse(mountpoint.exists())
            _prepare_qemu_mountpoint(root)
            self.assertTrue(stat.S_ISREG(mountpoint.lstat().st_mode))
            self.assertEqual(mountpoint.stat().st_size, 0)
            self.assertEqual(stat.S_IMODE(mountpoint.stat().st_mode), 0)

    def test_scan_and_snapshot_do_not_leak_directory_descriptors(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory) / "source"
            root.mkdir()
            for index in range(70):
                (root / str(index)).mkdir()
            target = Path(directory) / "target"
            target.mkdir()
            before = len(os.listdir('/proc/self/fd'))
            scan_rootfs(str(root))
            snapshot_rootfs(str(root), str(target))
            self.assertEqual(len(os.listdir('/proc/self/fd')), before)

    def test_static_qemu_validation_and_private_snapshot(self):
        with tempfile.TemporaryDirectory() as directory:
            base = Path(directory)
            source = base / "qemu-arm"
            make_elf64(source)
            self.assertEqual(validate_qemu(str(source)), source)
            snapshot = snapshot_qemu(str(source), str(base / "private-qemu"))
            self.assertTrue(snapshot.stat().st_mode & 0o111)
            dynamic = base / "dynamic-qemu"
            make_elf64(dynamic, interpreter=True)
            with self.assertRaisesRegex(SandboxError, "must be static"):
                validate_qemu(str(dynamic))
            needed_only = base / "needed-without-interpreter"
            make_elf64(needed_only, needed=True)
            with self.assertRaisesRegex(SandboxError, "DT_NEEDED"):
                validate_qemu(str(needed_only))

    def test_bwrap_command_has_only_private_mounts(self):
        command = build_bwrap_command("/trusted/bwrap", "/private/root", "/private/qemu",
                                      ["/bin/probe", "arg"])
        self.assertIn("--unshare-all", command)
        self.assertIn("--unshare-user", command)
        self.assertIn("--clearenv", command)
        self.assertIn("--tmpfs", command)
        self.assertIn("--dev", command)
        self.assertIn("--disable-userns", command)
        self.assertEqual(command.count("--cap-drop"), 1)
        self.assertIn("--ro-bind", command)
        self.assertNotIn("--proc", command)
        self.assertNotIn("/home", command)
        self.assertNotIn("/run", command)
        self.assertEqual(command[-5:], ["/opt/research/qemu-arm", "-L", "/", "/bin/probe", "arg"])

    def test_guest_command_must_be_absolute_and_cannot_traverse_root(self):
        for argv in ([], ["bin/probe"], ["/bin/../home/probe"]):
            with self.subTest(argv=argv), self.assertRaises(SandboxError):
                build_bwrap_command("bwrap", "root", "qemu", argv)

    def test_timeout_still_applies_after_child_closes_output_pipes(self):
        script = "import os,time; os.close(1); os.close(2); time.sleep(10)"
        result = _capture_bwrap([sys.executable, "-c", script], timeout_seconds=1)
        self.assertEqual(result["status"], "TIMEOUT")
        self.assertTrue(result["timed_out"])

    def test_launcher_child_inherits_no_new_privileges(self):
        script = "print(next(line.split()[1] for line in open('/proc/self/status') if line.startswith('NoNewPrivs:')))"
        result = _capture_bwrap([sys.executable, "-c", script], timeout_seconds=5)
        self.assertEqual(result["status"], "PASS")
        self.assertEqual(result["stdout"].strip(), "1")


if __name__ == "__main__":
    unittest.main()
