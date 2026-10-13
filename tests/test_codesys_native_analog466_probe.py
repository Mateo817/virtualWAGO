"""Mapping validation for the native offline analog candidate, no IDE mock PASS."""
import hashlib
import importlib.util
from pathlib import Path
import sys
import tempfile
import types
import unittest
from unittest.mock import patch


ROOT = Path(__file__).resolve().parents[1]
previous = {key: sys.modules.get(key) for key in ("scriptengine", "imp")}
sys.modules["scriptengine"] = types.ModuleType("scriptengine")
sys.modules["imp"] = types.ModuleType("imp")
try:
    spec = importlib.util.spec_from_file_location("analog466", ROOT / "tools/codesys_native_analog466_probe.py")
    candidate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(candidate)
finally:
    for key, module in previous.items():
        if module is None:
            del sys.modules[key]
        else:
            sys.modules[key] = module


class NativeAnalog466CandidateTests(unittest.TestCase):
    def rows(self):
        return [["Application.PLC_PRG.InputWord1", "_IW 1", "", "Input word 1", "%IW1", "_750_466"],
                ["Application.PLC_PRG.InputWord2", "_IW 2", "", "Input word 2", "%IW2", "_750_466"]]

    def test_source_pin_and_exact_description(self):
        self.assertEqual(hashlib.sha256((ROOT / "prototype/iec/native_analog466_probe.st").read_bytes()).hexdigest(),
                         candidate.SOURCE_SHA256)
        self.assertEqual(candidate.TERMINAL, (32776, "07500466000000000400", "2.0.0.9"))

    def test_distinct_word_mappings(self):
        result = candidate.verify_mapping_rows(self.rows())
        self.assertEqual([r["parameter_id"] for r in result], [16777216, 16777217])
        self.assertEqual([r["iec_address"] for r in result], ["%IW1", "%IW2"])

    def test_empty_build_artifact_rejects(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "synthetic.app"
            path.touch()
            with self.assertRaisesRegex(Exception, "empty source or artifact"):
                candidate.digest(str(path))

    def test_truncation_alias_output_direction_and_wrong_variable_reject(self):
        mutations = [self.rows()[:1], self.rows() + [self.rows()[0]]]
        for column, value in ((4, "%IW1"), (4, "%QW2"), (0, "Application.PLC_PRG.InputWord1")):
            rows = self.rows()
            rows[1][column] = value
            mutations.append(rows)
        for rows in mutations:
            with self.subTest(rows=rows), self.assertRaises(Exception):
                candidate.verify_mapping_rows(rows)

    def test_reopen_preserves_preexisting_export_on_abort(self):
        with tempfile.TemporaryDirectory() as directory:
            export = Path(directory) / "native-analog466-reopen.csv"
            export.write_bytes(b"existing private evidence")
            fake_imp = types.SimpleNamespace(load_source=lambda *args: object())
            fake_prompts = types.SimpleNamespace(ForwardUnknownPrompts=1, LogPrompts=2)
            with (patch.object(candidate, "BUILD_DIR", directory),
                  patch.object(candidate, "REOPEN", True),
                  patch.object(candidate, "digest", side_effect=lambda p: candidate.DESCRIPTOR_SHA256
                               if p == "synthetic-descriptor" else candidate.SOURCE_SHA256),
                  patch.object(candidate, "imp", fake_imp),
                  patch.object(candidate, "system", types.SimpleNamespace(), create=True),
                  patch.object(candidate, "ScriptPromptHandling", fake_prompts, create=True),
                  patch.object(candidate, "projects", types.SimpleNamespace(primary=None), create=True),
                  patch.dict(candidate.os.environ, {"VIRTUALWAGO_DESCRIPTOR_FILE": "synthetic-descriptor"})):
                with self.assertRaisesRegex(Exception, "temporary export already exists"):
                    candidate.run()
            self.assertEqual(export.read_bytes(), b"existing private evidence")
