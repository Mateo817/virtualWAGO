from __future__ import annotations

import copy
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace

from prototype.catalog import Catalog
from tools import generate_module_catalog as generator


ROOT = Path(__file__).resolve().parents[1]


class NativeCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        catalog = Catalog()
        self.profiles = catalog.native_profiles
        self.modules = catalog.entries()
        self.digest = catalog.sha256

    def catalog_view(self, profiles=None, modules=None):
        selected_modules = copy.deepcopy(self.modules if modules is None else modules)
        view = SimpleNamespace(
            native_profiles=copy.deepcopy(self.profiles if profiles is None else profiles),
            sha256=self.digest,
            bundled=True,
        )
        view.entries = lambda: copy.deepcopy(selected_modules)
        return view

    def test_reviewed_profiles_have_pinned_sizes_masks_ids_and_offsets(self) -> None:
        profiles = {p["name"]: p for p in self.profiles}
        self.assertEqual(set(profiles), {"digital8", "digital16"})
        p8 = profiles["digital8"]
        self.assertEqual(p8["c_enum"], "VIRTUAL_ADI_PROFILE_DIGITAL8_DI8_DO8")
        self.assertEqual(p8["modules"], ["750-430", "750-530"])
        self.assertEqual(p8["module_ids"], [0x8801, 0x8802])
        self.assertEqual(p8["input_offsets_bits"], [0, 0])
        self.assertEqual(p8["output_offsets_bits"], [0, 0])
        p16 = profiles["digital16"]
        self.assertEqual(p16["c_enum"], "VIRTUAL_ADI_PROFILE_DIGITAL16")
        self.assertEqual(p16["modules"], ["750-1405", "750-1504"])
        self.assertEqual(p16["module_ids"], [0x9001, 0x9002])
        self.assertEqual(p16["input_offsets_bits"], [0, 16])
        self.assertEqual(p16["output_offsets_bits"], [0, 0])

        normalized = {p["name"]: p for p in generator.validate_catalog(Catalog())}
        self.assertEqual((normalized["digital8"]["input_bytes"],
                          normalized["digital8"]["output_bytes"],
                          normalized["digital8"]["input_mask"],
                          normalized["digital8"]["output_mask"]),
                         (1, 1, 0x00ff, 0x00ff))
        self.assertEqual((normalized["digital16"]["input_bytes"],
                          normalized["digital16"]["output_bytes"],
                          normalized["digital16"]["input_mask"],
                          normalized["digital16"]["output_mask"]),
                         (2, 2, 0xffff, 0xffff))

    def test_generated_header_tracks_offsets_and_known_descriptor_pins(self) -> None:
        text = generator.render_header()
        self.assertIn(f"Bundled catalog canonical SHA-256: {self.digest}", text)
        self.assertIn("{0u, 16u}", text)
        self.assertIn("{0u, 0u}", text)
        self.assertIn("{0x8801u, 0x8802u}", text)
        self.assertIn("{0x9001u, 0x9002u}", text)
        self.assertIn('"UUUU8801UUUUUUUU", "UUUU8802UUUUUUUU"', text)

        bad_modules = copy.deepcopy(self.modules)
        next(m for m in bad_modules if m["article"] == "750-430")["descriptor"]["sha256"] = "0" * 64
        with self.assertRaisesRegex(ValueError, "known pin"):
            generator.validate_catalog(self.catalog_view(modules=bad_modules))

    def test_unknown_native_profile_and_arbitrary_profile_addition_are_blocked(self) -> None:
        unknown = copy.deepcopy(self.profiles)
        unknown.append({"name": "serial"})
        with self.assertRaisesRegex(ValueError, "only bundled digital8 and digital16"):
            generator.validate_catalog(self.catalog_view(profiles=unknown))

        renamed = copy.deepcopy(self.profiles)
        renamed[0]["name"] = "invented"
        with self.assertRaisesRegex(ValueError, "unknown or duplicate"):
            generator.validate_catalog(self.catalog_view(profiles=renamed))

    def test_external_catalog_instance_cannot_authorize_native_generation(self) -> None:
        external = Catalog(Catalog().data)
        self.assertFalse(external.bundled)
        with self.assertRaisesRegex(ValueError, "requires bundled Catalog"):
            generator.validate_catalog(external)

    def test_cli_has_no_external_catalog_authority_and_generated_file_is_current(self) -> None:
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools/generate_module_catalog.py"), "--help"],
            cwd=ROOT, capture_output=True, text=True, check=True,
        )
        self.assertNotIn("--catalog", result.stdout)
        check = subprocess.run(
            [sys.executable, str(ROOT / "tools/generate_module_catalog.py"), "--check"],
            cwd=ROOT, capture_output=True, text=True,
        )
        self.assertEqual(check.returncode, 0, check.stderr or check.stdout)



if __name__ == "__main__":
    unittest.main()
