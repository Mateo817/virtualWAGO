import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from tools.reference_netns import (
    PolicyError, _verify_namespace_context, load_policy, nft_rules, plan, validate_ports,
)


ROOT = Path(__file__).resolve().parents[1]
TEST_ALLOWED = "10.254.253.252"
TEST_PROTECTED = "10.254.253.253"


class ReferenceNetnsTests(unittest.TestCase):
    def policy_file(self, directory, value=None):
        path = Path(directory) / "target-policy.local.json"
        path.write_text(json.dumps(value or {
            "allowed_reference_ipv4": [TEST_ALLOWED],
            "protected_ipv4": [TEST_PROTECTED],
        }), encoding="utf-8")
        return path

    def test_policy_and_plan_are_read_only(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.policy_file(directory)
            policy = load_policy(path)
            rendered = plan(policy, [443], include_targets=True)
            self.assertEqual(rendered["status"], "PLAN_ONLY")
            self.assertFalse(rendered["setup_performed"])
            self.assertFalse(rendered["network_access_attempted"])
            self.assertEqual(rendered["allowed_tcp_ports"], [443])
            self.assertIn(f"ip daddr {TEST_ALLOWED} tcp dport {{ 443 }} accept", rendered["nftables"])
            self.assertNotIn(TEST_PROTECTED, rendered["nftables"])
            self.assertIn("policy drop", rendered["nftables"])

    def test_no_ports_means_no_permits(self):
        policy = {"allowed_reference_ipv4": [TEST_ALLOWED], "protected_ipv4": [TEST_PROTECTED]}
        rules = nft_rules(policy, [])
        self.assertIn("policy drop", rules)
        self.assertNotIn(" accept", rules)

    def test_policy_schema_is_exact_and_fail_closed(self):
        invalid_values = [
            {"allowed_reference_ipv4": [TEST_ALLOWED], "protected_ipv4": [TEST_PROTECTED], "comment": "x"},
            {"allowed_reference_ipv4": ["reference-device"], "protected_ipv4": [TEST_PROTECTED]},
            {"allowed_reference_ipv4": ["2001:db8::1"], "protected_ipv4": [TEST_PROTECTED]},
            {"allowed_reference_ipv4": ["10.0.0.0/8"], "protected_ipv4": [TEST_PROTECTED]},
            {"allowed_reference_ipv4": [TEST_ALLOWED], "protected_ipv4": [TEST_ALLOWED]},
            {"allowed_reference_ipv4": [TEST_ALLOWED, TEST_ALLOWED], "protected_ipv4": [TEST_PROTECTED]},
            {"allowed_reference_ipv4": [], "protected_ipv4": [TEST_PROTECTED]},
            {"allowed_reference_ipv4": ["192.0.2.3"], "protected_ipv4": [TEST_PROTECTED]},
        ]
        with tempfile.TemporaryDirectory() as directory:
            for value in invalid_values:
                with self.subTest(value=value):
                    path = self.policy_file(directory, value)
                    with self.assertRaises(PolicyError):
                        load_policy(path)

    def test_versioned_local_authorization_metadata_is_accepted_without_widening_permits(self):
        metadata = {
            "schema": "virtualwago-local-authorization/1",
            "nature": "OWNER_INSTRUCTION_ONLY_NOT_AN_ENFORCED_NETWORK_CONTROL",
            "issued_date": "2026-01-01",
            "protected_access": "DENY_ALL_INCLUDING_READ_ONLY_DISCOVERY_AND_TRANSITIVE_ACCESS",
            "private_network_default": "DENY_EXCEPT_EXPLICITLY_AUTHORIZED_REFERENCE_TARGET",
            "local_development_infrastructure": "test fixture only",
            "credentials_file": "local.private",
            "password_change_allowed": False,
            "reference_read_only_inventory_authorized": True,
            "plc_gateway_software_installation": {
                "authorized_on_reference_only": True,
                "requires": ["identity_verification"],
            },
            "requires_separate_scoped_authorization": ["physical_actuator_test"],
            "hardware_in_ci": False,
            "reference_identity_observed": False,
            "physical_actuator_isolation_observed": False,
            "target_policy_enforced_and_tested": False,
            "reference_model": None,
            "reference_firmware": None,
            "reference_runtime": None,
            "reference_ssh_host_key_fingerprint": None,
            "open_tasks": [],
        }
        value = {"allowed_reference_ipv4": [TEST_ALLOWED], "protected_ipv4": [TEST_PROTECTED], **metadata}
        with tempfile.TemporaryDirectory() as directory:
            path = self.policy_file(directory, value)
            policy = load_policy(path)
            self.assertEqual(policy["allowed_reference_ipv4"], [TEST_ALLOWED])
            self.assertNotIn(TEST_PROTECTED, nft_rules(policy, [22]))

    def test_duplicate_json_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "target-policy.local.json"
            path.write_text(
                '{"allowed_reference_ipv4":["10.254.253.252"],'
                '"allowed_reference_ipv4":["10.254.253.253"],'
                '"protected_ipv4":["10.254.253.254"]}', encoding="utf-8")
            with self.assertRaises(PolicyError):
                load_policy(path)

    def test_worker_context_rejects_current_host_namespaces(self):
        host_context = {
            "netns_inode": os.stat("/proc/self/ns/net").st_ino,
            "userns_inode": os.stat("/proc/self/ns/user").st_ino,
            "uid": os.getuid(),
            "gid": os.getgid(),
        }
        with self.assertRaisesRegex(RuntimeError, "distinct from its launcher"):
            _verify_namespace_context(host_context)

    def test_only_known_ports_can_be_selected(self):
        self.assertEqual(validate_ports([443, 22]), [22, 443])
        for ports in ([23], [0], [22, 22]):
            with self.subTest(ports=ports), self.assertRaises(PolicyError):
                validate_ports(ports)

    def test_default_cli_prints_plan_without_setup(self):
        with tempfile.TemporaryDirectory() as directory:
            path = self.policy_file(directory)
            result = subprocess.run(
                [sys.executable, "tools/reference_netns.py", "--policy", str(path),
                 "--allow-tcp-port", "22"],
                cwd=ROOT, capture_output=True, text=True, check=True,
            )
            output = json.loads(result.stdout)
            self.assertEqual(output["status"], "PLAN_ONLY")
            self.assertFalse(output["setup_performed"])
            self.assertFalse(output["network_access_attempted"])
            self.assertNotIn(TEST_ALLOWED, result.stdout)
            self.assertIsNone(output["nftables"])


if __name__ == "__main__":
    unittest.main()
