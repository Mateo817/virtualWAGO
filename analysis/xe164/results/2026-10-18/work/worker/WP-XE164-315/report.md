> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-315 — read-only validator erratum for WP305

WP305's published `validate.py` is not read-only: it opens `trace.tsv` and `results.json` in write mode, then writes `controls.tsv` (pinned source lines 136, 142, 161). Running it regenerates those artifacts before returning its PASS result. The original WP305 directory and its manifest remain unchanged and are preserved here as pinned references.

This package separates the bounded replay into `replay.py::generate_outputs()`. It reads the exact source pins and 131-word source ledger, computes replay state and serializes the three expected artifacts into in-memory strings. Importing the module does not execute replay. The default `validate.py` imports it with bytecode writes disabled, verifies source/reference hashes and copied inputs, calls the replay, then byte-compares the in-memory `trace.tsv`, `results.json`, and `controls.tsv` against frozen WP305 copies. It records the package file-hash inventory before import and after replay and requires it to remain identical. It never opens outputs for writing.

Validation result: **PASS**, 41 read-only checks. All three regenerated strings match the frozen artifacts byte-for-byte: trace 27,324 bytes; results 51,651 bytes; controls 463 bytes. Before/after inventory hashes match, so the default validator and replay module leave package files unchanged. The manifest separately covers every local package file except itself.

**VERIFIZIERT:** the pinned WP305 script has output-file write operations at the cited lines. **PASS:** WP315's default validator imports/replays in memory, matches all three frozen serialized outputs byte-for-byte, and observes an unchanged package hash inventory. The selected-route arithmetic remains supported by WP305's source replay and WP312's separate independent review; WP315 adds no new arithmetic verification or source/runtime/ABI/constructor/API conclusion. Native execution and runtime/device tests are **NOT_RUN**.
