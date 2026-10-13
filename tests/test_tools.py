import json
import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
from tools.elf_audit import inspect, parse_function_symbols, parse_interpreter, parse_search_paths
from tools.extract_xml_inventory import extract
ROOT = Path(__file__).resolve().parents[1]

class ToolsTests(unittest.TestCase):
    def test_inspect_real_host_elf(self):
        binary = Path(sys.executable).resolve()
        result = inspect(str(binary))
        self.assertEqual(result["header"]["Class"], "ELF64")
        self.assertEqual(result["runtime_execution"], "NOT_RUN")
        self.assertEqual(len(result["sha256"]),64)
        self.assertIsInstance(result["defined_function_symbols"], list)
        self.assertIsInstance(result["interpreter"], str)
        self.assertTrue(result["interpreter"].startswith("/"))

        # Compare with a direct readelf view of this real host ELF; never execute it.
        readelf = shutil.which("readelf")
        self.assertIsNotNone(readelf)
        headers = subprocess.run(
            [readelf, "-W", "-l", "-d", "--", str(binary)],
            capture_output=True, text=True, timeout=15, check=True,
            env={**os.environ, "LC_ALL": "C"},
        ).stdout
        expected = re.search(
            r"^\s*\[Requesting program interpreter:\s*(.*?)\]\s*$",
            headers, re.M,
        )
        self.assertIsNotNone(expected)
        self.assertEqual(result["interpreter"], expected.group(1))
        self.assertEqual(result["rpath"], parse_search_paths(headers)["rpath"])
        self.assertEqual(result["runpath"], parse_search_paths(headers)["runpath"])
        self.assertIn("declared ELF metadata", result["scope"])

    def test_loader_metadata_parser_handles_missing_interpreter_and_search_paths(self):
        program_headers = """
Elf file type is DYN (Position-Independent Executable file)
Program Headers:
  Type           Offset   VirtAddr           PhysAddr           FileSiz  MemSiz   Flags Align
  LOAD           0x000000 0x0000000000000000 0x0000000000000000 0x001000 0x001000 R E 0x1000
"""
        dynamic = """
Dynamic section at offset 0x1000 contains 1 entry:
  Tag        Type                         Name/Value
 0x0000000000000001 (NEEDED)             Shared library: [libc.so.6]
"""
        self.assertIsNone(parse_interpreter(program_headers))
        self.assertEqual(parse_search_paths(dynamic), {"rpath": [], "runpath": []})

    def test_loader_metadata_parser_preserves_declared_path_components(self):
        dynamic = """
Dynamic section at offset 0x2000 contains 2 entries:
 0x000000000000000f (RPATH)              Library rpath: [/opt/lib::/vendor/lib]
 0x000000000000001d (RUNPATH)            Library runpath: [$ORIGIN/../lib:/app/lib]
"""
        self.assertEqual(parse_search_paths(dynamic), {
            "rpath": ["/opt/lib", "", "/vendor/lib"],
            "runpath": ["$ORIGIN/../lib", "/app/lib"],
        })
    def test_function_symbol_metadata_uses_declared_size_not_next_symbol(self):
        fixture = """
Symbol table '.dynsym' contains 4 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     1: 0000000000002d20   140 FUNC    GLOBAL DEFAULT   12 namefoo
     2: 0000000000003000     0 FUNC    LOCAL  DEFAULT   12 size_unknown
     3: 0000000000001234    16 FUNC    GLOBAL DEFAULT  UND unresolved
Symbol table '.symtab' contains 2 entries:
   Num:    Value          Size Type    Bind   Vis      Ndx Name
     4: 00000000000034d0    32 FUNC    GLOBAL DEFAULT   13 later
     5: 0000000000040000 0x20000 FUNC    GLOBAL DEFAULT   13 wide
"""
        symbols = parse_function_symbols(fixture)
        foo = next(symbol for symbol in symbols if symbol["name"] == "namefoo")
        size_unknown = next(symbol for symbol in symbols if symbol["name"] == "size_unknown")
        later = next(symbol for symbol in symbols if symbol["name"] == "later")
        wide = next(symbol for symbol in symbols if symbol["name"] == "wide")
        self.assertEqual(foo, {
            "table": ".dynsym", "name": "namefoo", "value": 0x2D20,
            "size": 140, "section_index": "12", "type": "FUNC",
        })
        self.assertEqual(foo["value"] + foo["size"], 0x2DAC)
        self.assertGreaterEqual(later["value"], foo["value"] + foo["size"])
        self.assertEqual(later["table"], ".symtab")
        self.assertEqual(wide["size"], 131072)
        self.assertEqual(wide["value"], 0x40000)
        self.assertEqual(size_unknown["size"], 0)
        self.assertNotIn("range_end", size_unknown)
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
