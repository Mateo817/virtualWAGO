import contextlib
import copy
import io
import json
from pathlib import Path
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch

from prototype.catalog import Catalog
from prototype.contracts import ContractError, Unsupported
from prototype.vio import Rail
from tools.module_catalog import demo, main, dispatch_simulation
from prototype.module_simulation import ModuleSimulation


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog()

    def test_documentary_and_executable_coverage_are_distinct(self):
        self.assertEqual(len(self.catalog.entries()), 14)
        self.assertEqual(len(self.catalog.model_specs), 9)
        for article in ("750-454", "750-455", "750-550", "750-600", "750-652"):
            with self.subTest(article=article):
                self.assertIsNone(self.catalog.entry(article)["model"])
                with self.assertRaises(Unsupported):
                    self.catalog.research_layout([article])

    def test_variants_and_unknown_articles_never_alias(self):
        for article in ("750-677/040-000", "753-466", "750-466/000-200", "750-9999"):
            with self.subTest(article=article), self.assertRaises(Unsupported):
                self.catalog.model_for_article(article)

    def test_metadata_access_cannot_mutate_registry(self):
        data = self.catalog.data
        data["modules"][0]["model"]["input_bytes"] = 100
        entries = self.catalog.entries()
        entries.clear()
        spec = self.catalog.model("750-430.di8")
        spec["input_mask"] = 0
        self.assertEqual(self.catalog.model("750-430.di8")["input_mask"], 255)
        self.assertEqual(len(self.catalog.entries()), 14)

    def test_duplicate_articles_models_and_extra_keys_rejected(self):
        cases = []
        data = self.catalog.data
        data["modules"].append(copy.deepcopy(data["modules"][0]))
        cases.append(data)
        data = self.catalog.data
        data["modules"][0]["native_success"] = True
        cases.append(data)
        data = self.catalog.data
        data["unknown_schema_extension"] = 1
        cases.append(data)
        for data in cases:
            with self.subTest(data=data.keys()), self.assertRaises(ContractError):
                Catalog(data)

    def test_bad_width_mask_direction_and_codec_are_rejected(self):
        for field, value in (("input_bytes", 2), ("input_mask", 0xFFFF),
                             ("layout_scope", "NATIVE"), ("codec", "ai466_standard")):
            data = self.catalog.data
            data["modules"][0]["model"][field] = value
            with self.subTest(field=field), self.assertRaises(ContractError):
                Catalog(data)
        data = self.catalog.data
        data["modules"][0]["channels"] = True
        with self.assertRaises(ContractError):
            Catalog(data)

    def test_unknown_native_profiles_cannot_enter_catalog(self):
        data = self.catalog.data
        data["native_profiles"][0]["name"] = "analog"
        with self.assertRaises(Unsupported):
            Catalog(data)

    def test_duplicate_json_keys_fail_loading(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "duplicate.json"
            path.write_text('{"schema":1,"schema":1}')
            with patch("prototype.catalog.CATALOG_PATH", path), self.assertRaises(ContractError):
                Catalog()

    def test_credential_source_url_rejected(self):
        data = self.catalog.data
        data["modules"][0]["sources"][0]["url"] = "https://user:secret@example.test/path"
        with self.assertRaises(ContractError):
            Catalog(data)

    def test_changed_metadata_changes_digest(self):
        data = self.catalog.data
        data["modules"][0]["limits"].append("Additional explicit model assumption")
        self.assertNotEqual(Catalog(data).sha256, self.catalog.sha256)


class CatalogRailTests(unittest.TestCase):
    def setUp(self):
        self.catalog = Catalog()

    def test_mixed_digital_sizes_and_duplicate_instances(self):
        layout = self.catalog.research_layout(["750-400", "750-1405", "750-504", "750-504"])
        rail = Rail(layout)
        rail.set_input("m0", "03")
        rail.set_input("m1", "cdab")
        rail.run(True)
        result = rail.cycle("0108")
        self.assertEqual(result["input_hex"], "03cdab")
        self.assertEqual(result["effective_hex"], "0108")
        self.assertEqual(result["catalog_sha256"], self.catalog.sha256)
        self.assertTrue(all(e["kbus_uid"] is None for e in rail.enumerate()))

    def test_reserved_input_bits_rejected_atomically(self):
        rail = Rail(self.catalog.research_layout(["750-400", "750-402"]))
        before = rail.snapshot()
        for instance, raw in (("m0", "04"), ("m1", "10")):
            with self.subTest(instance=instance), self.assertRaises(Unsupported):
                rail.set_input(instance, raw)
            self.assertEqual(rail.snapshot(), before)

    def test_reserved_output_bits_rejected_without_refreshing_watchdog(self):
        rail = Rail(self.catalog.research_layout(["750-504"]))
        rail.run(True)
        rail.cycle("0f")
        rail.advance(99_999_999)
        before = rail.snapshot()
        with self.assertRaises(Unsupported):
            rail.cycle("10")
        self.assertEqual(rail.snapshot(), before)
        self.assertFalse(rail.advance(1)["armed"])

    def test_snapshot_rejects_changed_catalog_even_same_config(self):
        config = self.catalog.research_layout(["750-430"])
        rail = Rail(config)
        data = self.catalog.data
        data["revision"] = "changed-research-contract"
        other = Rail(config, catalog=Catalog(data))
        before = other.snapshot()
        with self.assertRaises(ContractError):
            other.restore(rail.snapshot())
        self.assertEqual(other.snapshot(), before)

    def test_snapshot_digital_mask_applies_to_physical_and_latched_inputs(self):
        rail = Rail(self.catalog.research_layout(["750-402"]))
        before = rail.snapshot()
        for latched in (False, True):
            modified = copy.deepcopy(before)
            if latched:
                modified["state"]["input_hex"] = "10"
            else:
                modified["state"]["physical"]["m0"] = "10"
            with self.subTest(latched=latched), self.assertRaises(Unsupported):
                rail.restore(modified)
            self.assertEqual(rail.snapshot(), before)

    def test_snapshot_digital_mask_applies_to_outputs(self):
        rail = Rail(self.catalog.research_layout(["750-504"]))
        before = rail.snapshot()
        modified = copy.deepcopy(before)
        modified["state"]["command_hex"] = "80"
        with self.assertRaises(Unsupported):
            rail.restore(modified)
        self.assertEqual(rail.snapshot(), before)

    def test_old_unbound_snapshot_is_explicitly_rejected(self):
        rail = Rail(self.catalog.research_layout(["750-430"]))
        old = rail.snapshot()
        old.pop("catalog_sha256")
        old["format"] = 1
        old["model_version"] = "0.1.0"
        with self.assertRaises(ContractError):
            rail.restore(old)

    def test_legacy_research_config_remains_compatible(self):
        path = Path(__file__).resolve().parents[1] / "config/research-layout.json"
        rail = Rail(json.loads(path.read_text()))
        self.assertEqual(len(rail.enumerate()), 4)
        self.assertEqual(rail.snapshot()["format"], 2)


class CatalogCliTests(unittest.TestCase):
    def test_list_reports_no_transplanted_native_pass(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["list"]), 0)
        report = json.loads(output.getvalue())
        self.assertEqual(len(report["entries"]), 14)
        self.assertTrue(all(e["this_revision_native_runtime"] == "NOT_RUN" for e in report["entries"]))

    def test_documentation_only_demo_returns_explicit_failure(self):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(main(["demo", "750-550"]), 2)
        self.assertFalse(json.loads(output.getvalue())["ok"])

    def test_autonomous_pwm_demo_and_gate_loss(self):
        result = demo(Catalog(), "750-677")
        self.assertEqual(result["closed_gate"]["frequency_hz"], [0] * 4)
        autonomous = result["after_one_second_without_new_command"]
        self.assertEqual(autonomous["pulse_count"], [1000, 2000, 0, 20_000])
        self.assertEqual(result["after_gate_loss"]["effective_frequency_hz"], [0] * 4)
        self.assertEqual(result["after_gate_loss"]["requested_frequency_hz"], [1000, 2000, 0, 20_000])

    def test_analog_demo_normal_range_points(self):
        result = demo(Catalog(), "750-466")
        self.assertEqual(result["sample"]["input_hex"], "00004000f87f")
        self.assertIn("STANDALONE", result["scope"])

    def test_stdin_mixed_simulation_and_watchdog_boundary(self):
        root = Path(__file__).resolve().parents[1]
        commands = (root / "config/catalog-demo.jsonl").read_text()
        result = subprocess.run([sys.executable, str(root / "tools/module_catalog.py"),
                                 "simulate", "750-430", "750-530", "750-466", "750-677"],
                                input=commands, text=True, capture_output=True, timeout=10)
        self.assertEqual(result.returncode, 0, result.stderr)
        reports = [json.loads(line) for line in result.stdout.splitlines()]
        self.assertEqual(len(reports), 9)
        self.assertTrue(all(report["ok"] for report in reports))
        self.assertEqual(reports[5]["result"]["modules"]["m3"]["behavior"]["pulse_count"],
                         [20, 40, 0, 400])
        self.assertFalse(reports[6]["result"]["rail"]["armed"])
        self.assertEqual(reports[6]["result"]["modules"]["m3"]["behavior"]["pulse_count"],
                         [100, 200, 0, 2000])
        self.assertFalse(reports[7]["result"]["rail"]["armed"])

    def test_protocol_rejects_unknown_or_extra_fields_without_mutation(self):
        sim = ModuleSimulation(["750-430"])
        before = sim.observe()
        for request in ({"op": "native_start"}, {"op": "input", "module": "m0", "value": 1, "extra": 2}):
            with self.subTest(request=request), self.assertRaises(ContractError):
                dispatch_simulation(sim, request)
            self.assertEqual(sim.observe(), before)


if __name__ == "__main__":
    unittest.main()
