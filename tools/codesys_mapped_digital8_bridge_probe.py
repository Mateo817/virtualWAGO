from __future__ import print_function

"""Offline builder for a separate virtual-only cyclic IEC probe.

The probe computes IEC input XOR 16#96; model output permission starts false.
Only use its boot image in the reviewed isolated original-runtime trial.
No online, gateway, physical I/O, or runtime operations occur in this builder.
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import codesys_mapped_digital8_candidate as builder

builder.SOURCE_PATH = os.path.join(builder.REPO_ROOT, "prototype", "iec", "minimal_io_8_bridge_probe.st")
builder.OUTPUT_PERMIT_INITIAL = True
builder.SOURCE_SHA256 = "6fb5bf46bf5e817bb6b8fddac1ba2cbf9129e83935a375648859e6bac9271dab"

if __name__ == "__main__":
    builder.run()
    builder.projects.primary.close()
