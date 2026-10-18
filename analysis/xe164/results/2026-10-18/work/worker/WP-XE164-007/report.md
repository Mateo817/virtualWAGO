> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-007 — XE164 jump-target structural comparison

## Scope and inputs

Question: determine the static structural relationship among jump targets `0xE01D5A`, `0xE01D90`, and `0xE01DC6`. Scope is limited to these target fragments and their immediate control/data references. No hardware, device, network, VM, or target actions were performed.

| Input | Size | SHA-256 |
|---|---:|---|
| `XE164-composite-e00000.bin` | 17,110 bytes | `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` |
| `composite-replay.md` | 2,169 bytes | `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5` |
| `Xe164Probe.java` | 4,315 bytes | `9289f41396180a3478ce3e64e70f54d38a397e5f4f7247b89bd8e8bf2808490f` |

All three supplied digests and sizes matched. The composite is mapped at `0xE00000`, so each address corresponds to file offset `address - 0xE00000`.

## Tooling and configuration

- Focused REA `execute_rizin_command` was run separately at the three raw file offsets. Each command used `e io.va=false` (file-offset addressing), `e asm.arch=c166`, `e asm.bits=16`, `e cfg.bigendian=false`, `px` for the fragment bytes, and `pd` long enough to include the terminating instruction. All three completed with exit code 0, no stderr, no output truncation, and the input digest unchanged. REA reported provider `rizin` but did not expose its executable version; the separately installed Rizin CLI reports `0.9.1` (`c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`). Evidence IDs for the final complete cross-sections: `ev_f62697194c3dacd5871a8604f06f37d479e955f0632a615b6c010c1aa3beb724` (offset `0x1D5A`), `ev_5f2dee1bc217ba89cb74a025c014d61155946290e6f692cd4f92912d3d1fb292` (`0x1D90`), `ev_f828d5a072cca8cc2fa73208cdff9f101d3aa1aeea40fe9f9443bde382e7231a` (`0x1DC6`). The exported REA bundle contains 5 records (the three final queries plus two earlier narrower queries), 0 unknowns.
- The earlier Ghidra replay and its logs remain in this WP directory as prior exploratory artifacts. They are not used to support the corrected structural conclusion; no Ghidra import or known `open_binary` C166 admission check was repeated in this correction.

## Findings

### Addresses, ranges, and incoming rows

| Target | Raw file offset | Jump-row provenance | Function boundary | Minimum linear fragment (inclusive start, exclusive end) | End instruction |
|---|---:|---|---|---|---|
| `0xE01D5A` | `0x1D5A` | E-XE164-012 row 89 (provided) | not established by REA | `[0xE01D5A, 0xE01D90)` | `RETI` at `0xE01D8E` |
| `0xE01D90` | `0x1D90` | E-XE164-012 row 90 (provided) | not established by REA | `[0xE01D90, 0xE01DC6)` | `RETI` at `0xE01DC4` |
| `0xE01DC6` | `0x1DC6` | E-XE164-012 row 91 (provided) | not established by REA | `[0xE01DC6, 0xE01DFA)` | `RETI` at `0xE01DF8` |

The row indices and target mapping are upstream-provided from E-XE164-012, not independently re-derived here; its source addresses/table bytes were not included in this bounded input set. The raw-file disassemblies show that each target begins a straight-line instruction sequence ending at a decoded `RETI`. The first two target-to-terminator ranges are each `0x36` bytes; the third is `0x34` bytes because it omits the 2-byte `bset` instruction. These minimum fragments are not claims about containing function boundaries. The command evidence binds the selected artifact path and digest, while the explicit `io.va=false` parameter and seek operands establish the inspected locations as raw file offsets.

### Byte and instruction pattern

Each fragment begins with the same ordered save/setup prefix (`push 0xffde`, `push 0xfe5c`, `push 0xfe5e`, `push 0xffdc`, `scxt 0xffda,#0`, `push 0xff08`, `push 0xff0a`, `extr #4`) and then has matching push/bit-or-`extr`/pop/return structure. The first and second instruction streams are identical except the `bset` immediate: `bset 0xfd00.4` at `0xE01D74` versus `bset 0xfd00.3` at `0xE01DAA`. Their 54-byte raw windows differ at that immediate-bearing byte (`4f 00` versus `3f 00`).

The third stream has the same prefix shape, but at the corresponding point it contains `extr #4` and omits the `bset` instruction. It then restores the same listed memory operands and terminates with `RETI`. Its 54-byte window therefore includes the first two bytes of the following code at `0xE01DFA`; the target fragment itself ends at `0xE01DFA` exclusive. Exact 54-byte windows are recorded in `targets.tsv` and the raw Rizin transcript.

Within each decoded range, the instructions before the final `RETI` are sequential and no direct jump or call instruction is decoded. The final `RETI` ends each observed fragment; no outgoing jump/call destination is present. Direct memory operands displayed by Rizin are listed in `references.tsv` as operands only; their higher-level meaning is not established.

## Conclusion and evidence status

**VERIFIZIERT — structural relationship:** these are three distinct jump-entry fragments with a repeated code template, each ending independently at a `RETI` terminator. They are not three entries/blocks that flow through one shared linear routine: neither of the first two falls through into the next entry, and the third also terminates before the following bytes. The first two are byte-identical apart from the `bset` immediate; the third is a shorter variant omitting that instruction.

**OFFEN — function identity/meaning:** the available REA/Rizin command evidence does not establish containing function boundaries, and the row-source addresses were not re-derived in this bounded package. The static result does not establish why the fragments were created, what the operand addresses mean, or whether the repeated template shares semantics. Repeated bytes are evidence of structure only.

## Alternative explanations and limits

- The fragments may be independent entry routines, interrupt-related routines, or pieces of a larger dispatch arrangement; the task scope excludes interpreting hardware/interrupt semantics. `RETI` only supplies the observed instruction-level terminator here.
- The target rows might be independently dispatched code fragments or might participate in a larger structure not visible in the supplied row metadata. The evidence here establishes instruction sequences and terminators, not function membership.
- The jump-row indices come from the supplied E-XE164-012 provenance and were not checked against the row table’s source bytes in this package.
- The conclusion relies on the focused REA/Rizin raw-offset observations. The retained earlier Ghidra logs are historical artifacts, not independent support in this corrected report. Decoder-derived pseudocode, if any, is not treated as original source.

## Output inventory

`targets.tsv`, `edges.tsv`, `references.tsv`, `rizin-cross-sections.txt`, `Xe164TargetProbe.java`, the nonempty `rea-evidence-bundle.json`, and the retained exploratory Ghidra logs are in this WP directory. `SHA256SUMS` uses standard `sha256sum` format and covers every output file except itself; byte sizes are reported separately by `stat` and in this report where relevant.

The current output sizes are:

| File | Bytes |
|---|---:|
| `Xe164TargetProbe.java` | 2,363 |
| `edges.tsv` | 529 |
| `ghidra-script.log` | 11,097 |
| `ghidra-targets-final-script.log` | 30,585 |
| `ghidra-targets-final.log` | 50,188 |
| `ghidra-targets-script.log` | 15,168 |
| `ghidra-targets.log` | 35,611 |
| `ghidra.log` | 29,876 |
| `rea-evidence-bundle.json` | 36,561 |
| `references.tsv` | 7,728 |
| `report.md` | 7,624 |
| `rizin-cross-sections.txt` | 2,502 |
| `targets.tsv` | 902 |
| `SHA256SUMS` | 1,108 |
