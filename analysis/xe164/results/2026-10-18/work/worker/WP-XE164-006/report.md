> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-006 — static scope at E00C1A

## Result

**VERIFIZIERT (replay-local):** In the bound composite, raw file offset `0x0C1A` maps to analysis address `0xE00C1A` when the replay base is `0xE00000`. A focused Ghidra C166 replay seeded at that address creates a single function candidate whose exact observed body AddressSet has one inclusive range, `E00C1A..E00C71`, containing 88 addresses (`0x58` bytes). The final instruction at `E00C70` is `RETI`; no semantic identity or interrupt meaning is asserted.

The function has no external incoming references to any address in its body in this replay, hence no statically found immediate caller. It has no call instruction or direct callee. One internal conditional direct jump is observed (`E00C4C -> E00C52`) and its fall-through is `E00C4E`. No computed/indirect control-flow instruction or unresolved computed edge was observed within this body. The complete operand reference inventory is in `references.tsv`; control-flow and negative call/caller results are in `edges.tsv`.

## Inputs and integrity

| Input | Size | SHA-256 | Status |
|---|---:|---|---|
| `XE164-composite-e00000.bin` | 17,110 bytes | `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` | VERIFIED; unchanged before/after Rizin |
| `composite-replay.md` | 2,169 bytes | `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5` | VERIFIED |
| `Xe164Probe.java` | 4,315 bytes | `9289f41396180a3478ce3e64e70f54d38a397e5f4f7247b89bd8e8bf2808490f` | VERIFIED |

The task-provided origin is E-XE164-012 jump-row index 36 at composite offset `0x0290`, which decodes to `0xE00C1A`. That provenance is accepted as the seed reason; this package did not reanalyze the other jump-row destinations.

## Method and address domains

1. **REA-first focused Rizin:** Rizin 0.9.1, commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`; command settings `asm.arch=c166`, `asm.bits=16`, `io.va=false`, seek `0x0C1A`, then disassemble 37 instructions. This yields raw-file-offset addresses (e.g. `0x00000c1a`). One initial invocation incorrectly supplied Rizin CLI flags as an in-command string and returned `Command '-a' does not exist`; it made no artifact change and is retained in the REA evidence bundle. The corrected command and captured output are preserved in `rizin.log` and the bundle (`ev_b1ffa94de86d5e6c59251ed40c277a416920ee47c5ceeb564ebfb04853387a92`); its SHA-256 stayed equal to the bound input digest.
2. **Bound replay recipe fallback:** Ghidra 12.1.4, language `C166:LE:16:default`, compiler spec `tasking`, BinaryLoader, base address `0xE00000`, `-readOnly`, one CPU, 45-second file analysis timeout, temporary project under `/tmp`, network namespace via `unshare -Un --map-current-user`. This maps file offset `f` to replay address `0xE00000+f`; thus offset `0x0C1A` is address `0xE00C1A`. The custom seed probe is `Xe164LocalProbe.java`. It disassembles/creates a function at the seed and records its body, instructions, references into every body address, and pseudocode. Import completed; script completed; the temporary project was deleted.

Addresses below `0xE00000` such as `0x00FE00` and `0x007C1C` are Ghidra operand-reference endpoints, not file offsets into the mapped composite. They are preserved literally without assigning device or hardware semantics. Rizin's offset output and Ghidra's replay-address output are separate coordinate systems.

## Instruction-level findings

**VERIFIZIERT (tool observations):** Rizin at file offset `0x0C1A` and Ghidra at address `0xE00C1A` agree on instruction boundaries and the local sequence. Ghidra reports 37 instructions in the 88-address body:

- `E00C1A`: `mov 0xf636,r0`.
- `E00C1E..E00C46`: context save/setup sequence; references are exhaustively listed in `references.tsv`.
- `E00C48`: `mov r12,0x7c1c`, with a READ reference to `007C1C`.
- `E00C4C`: `jmpr cc_EQ,0xe00c52` (conditional direct edge).
- `E00C4E`: `add 0x7c1c,0xff1e`, with READ_WRITE reference to `007C1C`.
- `E00C52..E00C6E`: restore sequence; references are exhaustively listed in `references.tsv`.
- `E00C70`: `reti`.

The return-like endpoint and save/restore pattern support the **HYPOTHESE** that the candidate is an interrupt-style context wrapper. An alternative is that the supplied composite/seed or decoder has merged a handler-like routine with a different purpose; neither naming nor intended entry mechanism is available from this local body. This hypothesis is not needed for the exact address/body or edge inventory.

## Edge and reference accounting

- Immediate callers: **VERIFIZIERT none found** by scanning ReferenceManager incoming references to every address in the exact body. The seed's jump-row provenance is data provenance external to this function body and is not counted as a decoded code caller.
- Immediate callees: **VERIFIZIERT none found**; all 37 body instructions were enumerated and none has CALL flow/reference classification.
- Direct control flow: **VERIFIZIERT** conditional branch from `E00C4C` to `E00C52`; the not-taken path falls through to `E00C4E`.
- Data/operand references: **VERIFIZIERT** 32 rows in `references.tsv`, comprising 31 data references and one conditional-branch reference marked as control flow; Ghidra classifies the data references as READ, WRITE, or READ_WRITE.
- Unresolved computed edges: **VERIFIZIERT none observed**; no instruction in the body reports computed flow and no indirect or unresolved call appears. This is limited to the replay's analyzed instruction/body representation; static analysis cannot rule out unmodeled dispatch or edges encoded outside this function.
- Pseudocode: the decompiler completed and emitted a tool-derived reconstruction. It is not source and is not treated as an independent ABI or semantic contract.

## Uncertainty and status

**OFFEN:** Why jump-row index 36 points here, the exact semantic identity of the routine, meanings of referenced low-address operands, whether any runtime dispatch reaches it, and whether the composite omits context needed to classify the routine. No hardware, interrupt, SFR, or K-Bus semantics are inferred.

Alternative boundary explanation: the body range is the replay's seeded Ghidra function body, not proof of original source-level function boundaries. Because the function is manually seeded at the supplied target and ends at `RETI`, Ghidra's body construction may reflect analysis assumptions. The result is therefore stated as an exact **replay-body** range, not a firmware-symbol boundary.

Tests: `PASS` for focused Rizin decode at the correct raw offset; `PASS` for named Ghidra C166 replay/import/script/decompilation; scope is the single seeded function candidate only. These statuses do not establish runtime behavior or validate other functions. Review: Self-review only; no independent review or worker run is claimed.

## Output integrity

`SHA256SUMS` contains SHA-256 values for every output file in this WP directory except itself. Its own hash is reported in the handoff accompanying this package.
