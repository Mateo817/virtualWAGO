import json
import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from tools.elf_audit import inspect
from tools.extract_xml_inventory import extract
ROOT = Path(__file__).resolve().parents[1]

class ToolsTests(unittest.TestCase):
    def test_inspect_real_host_elf(self):
        result = inspect(str(Path(sys.executable).resolve()))
        self.assertEqual(result["header"]["Class"], "ELF64")
        self.assertEqual(result["runtime_execution"], "NOT_RUN")
        self.assertEqual(len(result["sha256"]),64)
    def test_reject_non_elf(self):
        with self.assertRaises(ValueError): inspect(str(ROOT/"README.md"))
    def test_reject_device_before_open(self):
        with self.assertRaises(ValueError): inspect("/dev/null")
    def test_reject_symlink(self):
        with tempfile.TemporaryDirectory() as d:
            link=Path(d)/"linked"; link.symlink_to(Path(sys.executable).resolve())
            with self.assertRaises(ValueError): inspect(str(link))
    def test_reject_fifo_before_open(self):
        with tempfile.TemporaryDirectory() as d:
            candidate = Path(d) / "fifo"
            os.mkfifo(candidate)
            with self.assertRaises(ValueError):
                inspect(str(candidate))
    def test_path_replaced_with_fifo_before_open_is_not_read(self):
        with tempfile.TemporaryDirectory() as d:
            candidate = Path(d) / "candidate"
            candidate.write_bytes(b"ordinary")
            original_open = os.open
            def replace_then_open(path, flags, *args, **kwargs):
                if Path(path) == candidate:
                    candidate.unlink()
                    os.mkfifo(candidate)
                return original_open(path, flags, *args, **kwargs)
            with patch("tools.elf_audit.os.open", side_effect=replace_then_open):
                with self.assertRaises(ValueError):
                    inspect(str(candidate))
    def test_path_replaced_with_symlink_before_open_is_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            candidate = Path(d) / "candidate"
            candidate.write_bytes(b"ordinary")
            original_open = os.open
            def replace_then_open(path, flags, *args, **kwargs):
                if Path(path) == candidate:
                    candidate.unlink()
                    candidate.symlink_to("/dev/null")
                return original_open(path, flags, *args, **kwargs)
            with patch("tools.elf_audit.os.open", side_effect=replace_then_open):
                with self.assertRaises(ValueError):
                    inspect(str(candidate))
    def test_readelf_uses_hashed_snapshot_after_original_replacement(self):
        with tempfile.TemporaryDirectory() as d:
            candidate = Path(d) / "candidate"
            data = Path(sys.executable).resolve().read_bytes()
            candidate.write_bytes(data)
            original_run = subprocess.run
            def replace_then_run(command, *args, **kwargs):
                candidate.write_text("changed while auditing")
                self.assertNotEqual(Path(command[-1]), candidate)
                self.assertEqual(Path(command[-1]).read_bytes(), data)
                return original_run(command, *args, **kwargs)
            with patch("tools.elf_audit.subprocess.run", side_effect=replace_then_run):
                result = inspect(str(candidate))
            self.assertEqual(result["sha256"], hashlib.sha256(data).hexdigest())
            self.assertEqual(result["header"]["Class"], "ELF64")
    def test_xml_extract_declarations(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.xml"
            p.write_text('<project><task name="t" interval="PT0.02S"/><variable name="x" address="%IX0.0"/><Library Name="Example"/></project>')
            x=extract(p)
            self.assertEqual(x["addresses"][0]["address"],"%IX0.0")
            self.assertEqual(len(x["libraries"]),1)
    def test_reject_xml_dtd(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"x.xml"; p.write_text('<!DOCTYPE project><project/>')
            with self.assertRaises(ValueError): extract(p)
    def test_cli_end_to_end_and_error(self):
        commands='{"op":"run","running":true}\n{"op":"cycle","outputs_hex":"0100"}\n{"op":"unsupported"}\n'
        r=subprocess.run([sys.executable,"-m","prototype","--config","config/minimal.json"],
                         cwd=ROOT,input=commands,capture_output=True,text=True,check=True)
        rows=[json.loads(l) for l in r.stdout.splitlines()]
        self.assertTrue(rows[0]["ok"])
        self.assertEqual(rows[1]["result"]["effective_hex"],"0100")
        self.assertFalse(rows[2]["ok"])
    def test_cli_oversize_session_closed(self):
        r=subprocess.run([sys.executable,"-m","prototype","--config","config/minimal.json"],
                         cwd=ROOT,input=" "*65537+"\n",capture_output=True,text=True)
        self.assertEqual(r.returncode,2)
        self.assertFalse(json.loads(r.stdout)["ok"])
