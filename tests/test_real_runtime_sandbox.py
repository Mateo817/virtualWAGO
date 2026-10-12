import unittest
from tools.real_runtime_sandbox import (build_runtime_command,
                                       build_board_metadata_prefix,
                                       build_board_metadata_probe_command,
                                       build_board_metadata_runtime_command)


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

    def test_board_metadata_adds_single_readonly_endpoint_binding(self):
        baseline = build_runtime_command("/opt/own/bwrap", "/opt/own/trial")[:-2]
        command = build_board_metadata_prefix("/opt/own/bwrap", "/opt/own/trial")
        index = command.index("--proc") - 3
        self.assertEqual(command[index:index + 3],
                         ["--ro-bind", "/dev/eeprom", "/dev/eeprom"])
        self.assertEqual(command[:index] + command[index + 3:], baseline)

    def test_metadata_probe_is_staged_bounded_and_does_not_start_runtime(self):
        probe = "/home/codesys_root/bin/typelabel-read-probe"
        command = build_board_metadata_probe_command(
            "/opt/own/bwrap", "/opt/own/trial", probe)
        self.assertEqual(command[-5:], ["/home/codesys_root/bin/readonly-metadata-broker",
                                      "--timeout", "10", "--", probe])
        self.assertNotIn("/usr/bin/codesys3", command)
        with self.assertRaises(ValueError):
            build_board_metadata_probe_command(
                "/opt/own/bwrap", "/opt/own/trial", "/usr/bin/codesys3")

    def test_init_candidate_changes_only_provider_components_and_bounded_child(self):
        command = build_board_metadata_runtime_command("/opt/own/bwrap", "/opt/own/trial")
        self.assertEqual(command[-7:], ["/home/codesys_root/bin/readonly-metadata-broker",
                                      "--diagnostics", "--timeout", "30", "--", "/usr/bin/codesys3",
                                      "/etc/codesys3.d/CODESYSControl_User.cfg"])
        prefix = command[:-7]
        index = prefix.index("/opt/own/trial/components-board") - 1
        self.assertEqual(prefix[index:index + 3],
                         ["--ro-bind", "/opt/own/trial/components-board",
                          "/usr/lib/cds3-custom-components"])
        del prefix[index:index + 3]
        prefix[prefix.index("/opt/own/trial/libdal-board.so")] = "/opt/own/trial/libdal.so"
        self.assertEqual(prefix, build_board_metadata_prefix(
            "/opt/own/bwrap", "/opt/own/trial"))
