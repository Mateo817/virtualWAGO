"""Public socket-transport verification; no vendor API or hardware."""
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


class ModelBridgeTransportTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("cc"), "native C compiler unavailable")
    def test_bounded_transport_permissions_protocol_and_disconnect(self):
        root = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as directory:
            executable = str(Path(directory) / "bridge-transport")
            subprocess.run([
                "cc", "-std=gnu11", "-Wall", "-Wextra", "-Werror", "-pthread",
                "-DVIRTUALWAGO_ENABLE_MODEL_BRIDGE", "-DADI_MODEL_BRIDGE_STANDALONE_TEST",
                str(root / "tools/adi_model_bridge.c"),
                str(root / "tools/adi_model_bridge_test.c"), "-o", executable,
            ], check=True, capture_output=True, timeout=30)
            result = subprocess.run([executable], check=True, capture_output=True,
                                    text=True, timeout=10)
            self.assertEqual(result.stdout,
                             "ADI_MODEL_BRIDGE_TRANSPORT_TEST: PASS (own-only IPC test double)\n")
