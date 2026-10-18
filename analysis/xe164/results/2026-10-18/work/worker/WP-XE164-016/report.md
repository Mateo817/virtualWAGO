> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-016 — E03878 bounded static structure

## Result

**VERIFIZIERT** for the requested narrow static question: at composite raw offset `0x3878` (address `E03878` with binary base `0xE00000`), the instruction is the two-byte `rets` (`db00`). Its minimal statically reachable body therefore contains exactly this one instruction. It terminates at the return; there are no intra-body CFG edges, outgoing direct calls, or address-bearing/data-reference instructions in that body.

The five allowed candidate callsite instructions at raw offsets `0x04EE`, `0x04FA`, `0x0504`, `0x050E`, and `0x0518` each decode as `calls E03878`. They are recorded as incoming edges in `calls.tsv`. No surrounding caller body was followed. The following bytes at `E0387A` are excluded from the bounded body. The replay note reports a seeded startup candidate at `E0387A`; this is consistent with the boundary and is used only as a scope cross-check, not as a function-contract claim.

## Evidence and method

- Artifact: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`, 17,110 bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Replay reference: `PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md`, 2,169 bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`.
- First analysis action was `REA execute_rizin_command` at raw offset `0x3878`, with `io.va=false`, `asm.arch=c166`, `asm.bits=16`, and `cfg.bigendian=false`; only local offline artifact input was supplied. The initial linear probe requested 80 instructions; it exposed `rets` as the first instruction, after which all bytes beyond its 2-byte terminal instruction were excluded from the selected evidence bundle and all result tables. The separate retained decode reads only the single return and the five explicitly allowed one-instruction candidates. Rizin 0.9.1 (`c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`). No global `aaa` was used.
- A separate bounded single-instruction command decoded only the five named callsite candidates and `E03878`. A byte-read command confirmed the five callsite byte sequences are `da e0 78 38` and the seed bytes are `db 00`. The call destinations in the disassembly are all `E03878`.
- Selected REA evidence IDs: `ev_6b362318eaa0f3a0065574acb4f454095608cf598e060c587d222544fe2994d6` (five candidate instructions and seed) and `ev_13651d08600eb67155d682214df2b826f4b0eef4a0711843c8fad3cf254b2b02` (bounded bytes). `rea-evidence.json` retains these two complete records. The initial exploratory decode record, `ev_e356309684afdf607a16edce6b38e5397ec7aba2e58e1c08ae5510aabf23af59`, is expressly excluded because its requested linear count exceeded the discovered terminal bound.
- Canonical complete REA session export: `REA-Evidence-Bundle.json`, produced by `REA export_evidence_bundle`, 48,821 bytes, SHA-256 `e5f1d42ddb560b5bfd19249ad7f285dbe74029aabeacc43e0023ad41805087bc`, 3 records and 0 unknowns. It contains the two WP-relevant IDs above plus the exploratory record noted above; `rea-evidence.json` remains the narrower audit selection and is not represented as the canonical full-session export.
- No Ghidra fallback was needed: the reachable body stops at the return instruction, so no unresolved CFG or body-reference question remained. No tool-derived pseudocode was necessary; the bounded structure is stated directly from the decoded instruction.

## Machine-readable scope

- `instructions.tsv`: one decoded instruction, exactly at `0x3878`.
- `edges.tsv`: header only; the return instruction has no static successor.
- `calls.tsv`: only the five explicitly permitted incoming callsite instructions; no caller bodies and no outgoing callee calls.
- `references.tsv`: header only; no address/data reference is present inside the bounded body.

The empty CFG/reference tables mean none were observed in this one-instruction body, not that global or indirect references elsewhere in the composite were exhaustively searched. The direct incoming list is restricted to the five supplied candidates and is not claimed as a complete global xref inventory.

## Status and limitations

- Finding: **VERIFIZIERT** for instruction bytes, bounded body, and the five inspected direct callsite decodes.
- Interpretation: **OFFEN** beyond the literal static structure. No ABI, SFR, K-Bus, register, runtime, or FW31 meaning is assigned to `rets` or to its callers.
- Tests: validator **PASS** after execution; `sha256sum -c SHA256SUMS` **PASS** after manifest creation. No emulator or hardware test was run (`NOT_RUN`, out of scope).
- Residual uncertainty: Rizin's rendered address is the composite address (`E03878`) while the table offsets are file offsets. The validator checks that mapping against base `0xE00000`, verifies exact bytes/length and each call destination encoding, and confirms that the CFG/reference tables remain empty. Rizin's provider evidence reports its executable version as unknown; the local `rizin -v` probe identified 0.9.1. No original-toolchain/runtime contract follows from this inspection.
