> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-027 — XE164 E0077A local control flow and references

## Status

**VERIFIZIERT** — raw bytes, Rizin C166 decoding, in-scope direct control-flow edges, two return boundaries, and the caller instruction at E007DC are tied to the supplied composite by `validate.py`. This is a static, artifact-local result; it does not identify an API, register meaning, ABI, or runtime behavior.

## Scope and inputs

- Composite: `XE164-composite-e00000.bin`, 17,110 bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Replay note: `composite-replay.md`, 2,169 bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`.
- Requested raw range: `[0x077A,0x07D4)`; analysis labels use the assumed composite base E00000, so E0077A–E007D3. The only extra observation is the four-byte direct caller instruction at raw 0x07DC (E007DC).
- The interval stops at E007D4. No instruction or data at E00720/E007D4, no caller body, and no call target body was inspected.

## Findings

Rizin decodes 28 contiguous instructions spanning exactly raw 0x077A–0x07D3. Direct conditional edges are:

| Source | Edge | Destination |
|---|---|---|
| E00786 | taken | E007D0 |
| E00786 | fallthrough | E00788 |
| E0079C | taken | E007B0 |
| E0079C | fallthrough | E007A0 |
| E007A4 | taken | E007B0 |
| E007A4 | fallthrough | E007A8 |
| E007AC | taken | E007CC |
| E007AC | fallthrough | E007B0 |
| E007B8 | taken | E007D0 |
| E007B8 | fallthrough | E007BC |
| E007C0 | taken | E007D0 |
| E007C0 | fallthrough | E007C4 |
| E007C8 | taken | E007D0 |
| E007C8 | fallthrough | E007CC |

The reachable terminal instructions are RETS at E007CE and E007D2; their instruction bytes end at the exclusive boundary E007D4. No direct call occurs within the inspected block. The separately permitted caller instruction at E007DC is `calls 0xe0077a`, bytes `dae07a07`, so its direct target is E0077A. This reports only the call instruction; no caller or callee body was read.

Observed numeric operands are preserved literally in `numeric_refs.tsv`: repeated `0xfe06:0x31ba` and `0xfe06:0x30bc` operands, `0xf1ba.15`, immediate masks/constants, and direct branch destinations. These encodings are not assigned DPP, SFR, pointer, ABI, or hardware meaning. The `extr #1` decoding at E007B0 is retained as Rizin output; its semantic operation is not inferred.

## Tool profile and evidence

REA was queried first; no REA document was open. REA's Rizin command observations are retained in `evidence-bundle.json` (7 canonical records; round-trip import accepted with total 7). Provider command arguments: executable `rizin`, arguments `-N -q -c <command> <artifact>`, where the command explicitly sets `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`, then reads bytes/disassembly at raw offsets. Rizin reported version 0.9.1 locally. `pdj 28` supplies all 28 instruction offsets, sizes, bytes, opcodes and direct branch jump/fail values; `p8` independently supplies the exact 90-byte interval and caller bytes. An exploratory uppercase `pDj` query returned only a partial/inconsistent listing and is not used for any table or conclusion. Artifact digest after each REA invocation remained the expected SHA-256.

Ghidra was not needed: Rizin provided complete, contiguous decoding through both in-range returns and the direct caller instruction. No provider function-boundary claim is made. The caller relation supplied in the task is independently confirmed at the instruction level by the four bytes and decoded direct target.

## Alternative and residual uncertainty

The analysis is linear over the exact requested byte interval and includes the direct conditional destinations/fallthroughs. All reported direct branch destinations lie on decoded instruction boundaries within that interval. Indirect flow is not established by this work; no call target is traversed. Register and segmented memory operands remain numeric only. No claim is made about original device behavior, calling convention, or meanings of the encoded locations. `extr` semantics and any provider-specific interpretation beyond the printed disassembly remain **OFFEN**.

## Validation

`python3 validate.py` verifies the input and replay hashes, the contiguous instruction coverage and byte encodings, each listed CFG edge, literal numeric-reference sources, and the exact caller bytes/target; it also rejects out-of-scope addresses and call traversal. `SHA256SUMS` records output artifact hashes. This is an analyst self-check, not an independent review.
