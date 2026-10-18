> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-026 — XE164 E00720 bounded static CFG

## Status

- CFG/disassembly: **VERIFIZIERT** against the selected composite bytes with Rizin C166 decoding, subject to the stated base-address assumption and decoder limitations.
- Caller `E007EA → E00720`: **VERIFIZIERT** at the call-instruction byte/operand level; the caller relationship was also supplied by E-XE164-031.
- Calls inside `E00720..E00779`: **VERIFIZIERT** none in this byte-bounded decode.
- Numeric segment:offset / bit-base values: **OFFEN** as to meaning. They are preserved literally and deliberately not interpreted as SFR, ABI, DPP, or hardware semantics.
- Validator: **PASS** (`python3 validate.py`, self-review).
- Hash manifest: **PASS** after generation and `sha256sum -c SHA256SUMS`.
- REA bundle: **PASS** export (4 records, 0 unknowns) and import validation (0 new records; 4 already present).

## Inputs and scope

Composite: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`, 17,110 bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.

Replay metadata consulted: `PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md`, 2,169 bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`. It identifies the composite replay as Ghidra 12.1.4, `C166:LE:16:default`, `tasking`; no new Ghidra analysis was needed because Rizin produced a complete, bounded decode and both local return instructions are in scope.

Analyzed raw offsets are exactly `[0x0720,0x077a)`, inclusive `0x0720..0x0779`. Listings map raw offset `x` to `E00000 + x` under the supplied base assumption. The only additional location inspected is the single caller instruction at raw `0x07EA` (`E007EA`). No call target body or neighboring function was traversed.

## Tool profile and evidence

REA operation: `execute_rizin_command`, provider `rizin` (version not reported), target digest matching the composite above. Rizin command profile used for the successful bounded disassembly and caller decode:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`pD 90` decoded a 90-byte window, exactly raw `0x0720..0x0779`. Successful callee evidence: `ev_99f5679f2398a323c80f2c8d6431a0d7a8d0ed9442af9138537d28af460c9dd8`. Caller evidence: `ev_7fd63f0dc66e105fe94efd1d02204093925f9ad5b12396914eafd510cff6ac59`. A preliminary invocation incorrectly supplied Rizin command-line flags inside the REA command field and yielded a Rizin error, not analysis; it is retained in the evidence ledger as `ev_d5b3d86ad5c2f15c69d9637805b238e86bf159fd48fbc60d2a3058dbb09b2437` and is not used for findings.

## Findings

The decoded local graph has nine basic blocks (see `blocks.tsv`), fourteen conditional/fallthrough edges, and two abstract return exits (`edges.tsv`). All branch destinations are within the requested raw interval. The two terminal paths end at `E00774` (`rets`) or `E00778` (`rets`). Branch destinations at `E00776` and `E00772` stay within scope. No edge or instruction crosses `E0077A`.

No `calls` instruction occurs in `E00720..E00779`. At the separately allowed caller slot, Rizin decodes bytes `da e0 20 07` at raw `0x07EA` as `calls 0xe00720`; the byte-level target is the function entry under the `E00000` mapping. Call traversal stops at that boundary.

`numeric_references.tsv` records branch targets, literal operands, and opaque numeric memory/bit-base operands. In particular, `0xfe06:0x31b8`, `0xfe06:0x30bc`, and `0xf1b8` are not assigned SFR or peripheral meanings. No DPP, ABI/calling convention, K-Bus, or hardware interpretation is made.

## Alternative and residual uncertainty

Rizin is the primary disassembler used here; the supplied Ghidra replay establishes an available alternative profile, but a second Ghidra run was unnecessary because the scoped byte window decoded completely and ends in visible `rets`. The base `E00000` is assumed from the supplied replay and is not independently established by this worker. Rizin's recorded version is unknown; its printed offsets and bytes are preserved in the evidence bundle, and the validator independently binds every listed instruction byte to the source file. The static graph does not establish runtime reachability, meaning of opaque operands, or behavior outside the boundary.

## Worker artifacts

- `disassembly.tsv`: byte-bound instruction listing.
- `blocks.tsv`, `edges.tsv`: bounded CFG.
- `calls.tsv`, `direct_calls_in_scope.tsv`: separately byte-bound caller and in-scope call result.
- `numeric_references.tsv`: direct targets and numeric operands with interpretation limits.
- `validate.py`: local structural and source-byte validator.
- `SHA256SUMS`: hashes of worker outputs, generated after final verification.
- `evidence-bundle.json`: canonical REA export for this worker's records; importability check is performed after export.
