import unittest
from tools.real_runtime_sandbox import build_runtime_command


class RuntimeSandboxPolicyTests(unittest.TestCase):
    def test_original_program_and_realpath_provider_with_private_bus_endpoints(self):
        command = build_runtime_command("/opt/own/bwrap", "/opt/own/trial")
        self.assertEqual(command[-2:], ["/usr/bin/codesys3",
                                      "/etc/codesys3.d/CODESYSControl_User.cfg"])
        bindings = []
        for index, value in enumerate(command):
            if value in ("--bind", "--ro-bind"):
                bindings.append(tuple(command[index + 1:index + 3]))
        self.assertIn(("/opt/own/trial/libdal.so", "/usr/lib/libdal.so.1.0.1"), bindings)
        self.assertNotIn(("/dev", "/dev"), bindings)
        self.assertNotIn(("/run", "/run"), bindings)
        self.assertNotIn(("/sys", "/sys"), bindings)
        self.assertNotIn(("/", "/"), bindings)
        for required in ("--unshare-pid", "--unshare-net", "--unshare-ipc", "--clearenv"):
            self.assertIn(required, command)
        self.assertNotIn("--share-net", command)
        self.assertNotIn("--cap-add", command)

    def test_invalid_or_global_stage_paths_are_rejected(self):
        for value in ("/", "/usr", "/tmp", "relative", "/opt/../tmp/a", "/opt//a"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                build_runtime_command("/opt/own/bwrap", value)
