"""Hardware-free check that the shim preserves calls for non-vcan links.

The positive vcan checks are a separate namespace-only native probe, not CI
claims about a WAGO driver or a CANopen participant.
"""
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]


@unittest.skipUnless(shutil.which("cc"), "native C compiler required")
class VcanLinkCompatTests(unittest.TestCase):
    def test_non_vcan_calls_reach_next_provider(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            shim = tmp / "shim.so"
            provider = tmp / "provider.so"
            source = tmp / "provider.c"
            source.write_text(
                "#include <stdint.h>\n"
                "int can_set_bitrate(const char *n, uint32_t v) "
                "{return n && v == 125000 ? 71 : 72;}\n"
                "int can_set_restart_ms(const char *n, uint32_t v) "
                "{return n && v == 2000 ? 81 : 82;}\n"
                "int can_get_state(const char *n, int *v) "
                "{if (n && v) {*v = 91; return 0;} return -1;}\n"
            )
            for src, out in (
                (ROOT / "tools/vcan_link_compat.c", shim),
                (source, provider),
            ):
                subprocess.run(
                    ["cc", "-shared", "-fPIC", "-Wall", "-Wextra", "-Werror",
                     str(src), "-ldl", "-o", str(out)],
                    check=True, capture_output=True,
                )
            script = """
import ctypes
library = ctypes.CDLL(None)
for name, value, expected in [
    ("can_set_bitrate", 125000, 71),
    ("can_set_restart_ms", 2000, 81),
]:
    fn = getattr(library, name)
    fn.argtypes = [ctypes.c_char_p, ctypes.c_uint32]
    fn.restype = ctypes.c_int
    for interface in (b"lo", b"vw-missing"):
        assert fn(interface, value) == expected
state = ctypes.c_int(-1)
get_state = library.can_get_state
get_state.argtypes = [ctypes.c_char_p, ctypes.POINTER(ctypes.c_int)]
assert get_state(b"lo", ctypes.byref(state)) == 0
assert state.value == 91
"""
            result = subprocess.run(
                [shutil.which("python3"), "-c", script],
                env={**os.environ, "LD_PRELOAD": f"{shim}:{provider}"},
                text=True, capture_output=True, timeout=10,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn("VW_VCAN_METADATA", result.stderr)


if __name__ == "__main__":
    unittest.main()
