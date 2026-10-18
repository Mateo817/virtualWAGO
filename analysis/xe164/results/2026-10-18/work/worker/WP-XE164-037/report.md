> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-037 — bounded structure E004B8..E004C9

## Finding

**VERIFIZIERT** for the static C166 decode of the supplied byte window and the one requested caller instruction. Eight consecutive instructions occupy exactly `[0x04B8,0x04CA)` (18 bytes). The decode shows two conditional branches: E004BE targets E004C8 and falls through to E004C0; E004C6 branches back to E004C4 and otherwise continues to E004C8. E004C8 is `RETS`. The requested instruction at E03682 is a direct `CALLS E004B8`.

This is a bounded instruction and edge description. It does not establish that E004B8 is a complete function entry, enumerate all callers, or describe any behavior beyond the decoded instructions.

## Input and coordinate binding

- Composite: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`
- Size: 17,110 bytes.
- SHA-256: `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Callee byte offsets: `[0x04B8,0x04CA)`; the supplied composite base is rendered as E00000 for address labels only, so these offsets label E004B8 through E004C9.
- Caller: exactly one instruction at file offset `0x3682`, labeled E03682 under the same syntactic mapping.
- No bytes at or after `0x04CA` were disassembled for the callee window. No other caller or call target was followed.

## Exact tables

`instructions.tsv` records every decoded instruction start, length and byte sequence in the bounded window. `edges.tsv` records sequential edges, both outcomes of the two conditional branches, and the terminal return. The conditions are reproduced as Rizin's disassembly text; no additional condition semantics are asserted. `caller.tsv` contains only the requested caller instruction.

| Measure | Observation |
|---|---:|
| Window | `[0x04B8, 0x04CA)` = 18 bytes |
| Instructions | 8, contiguous |
| Conditional branches | 2 |
| Branch destinations | E004BE → E004C8; E004C6 → E004C4 |
| Terminal instruction | E004C8, `db00` (`rets`) |
| Requested caller instruction | E03682, `dae0b804` (`calls 0xe004b8`) |

## Method, Evidence and alternative

REA `open_binary` was attempted first on the exact composite. It returned `target_unavailable / unsupported binary format` because the headerless image was not admitted through the normal binary route. The current REA raw-binary selector has no C166 architecture choice, so no other ISA was substituted.

The documented fallback was REA `execute_rizin_command` against the explicit local composite, with `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, and `io.va=false`. The first focused observation captured the 18 callee bytes, the entry instruction, and exactly one instruction at caller offset `0x3682` (Evidence `ev_37c645167a41eafd7a26e64cd6c44a7ca973be428ae255d00edd3801d0b78ae5`). The second decoded one instruction at each remaining start through E004C8 (Evidence `ev_74a5fdeb35ffd78586e463225d0cb388a9c255b3b462230af6f7b2849eadd616`). Both report complete output, exit code 0, no truncation, and unchanged source digest. The local Rizin CLI reports version 0.9.1, commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`; REA's provider version field is null.

The canonical REA session export contains only those two finding-bearing records in `evidence/rea-evidence-bundle.json` (2 records, 0 unknowns). No independent second disassembler was run; the byte listing is the non-disassembly alternative retained for exact byte-level checking. Independent instruction-boundary confirmation is **OFFEN**.

## Limits and remaining uncertainty

- Static decoding does not show runtime execution, actual branch frequencies, or effects of the instructions.
- The branch mnemonics and targets are Rizin observations. A different decoder may render condition labels differently; no independent cross-check was performed.
- The window's terminal `RETS` does not prove a complete body boundary, and the supplied caller is not a global caller inventory.
- No CPU/SFR names, API, ABI, calling convention, or runtime/hardware behavior is inferred.
- The Rizin Evidence limitations note that external files or plugins are not digest-bound. This investigation supplied only the local artifact path and performed no device, network, or VM operation.

## Verification

`python3 validate.py` checks artifact size/hash, finding-only canonical bundle membership, exact byte coverage and instruction boundaries, the two branch edges, the terminal return, and the isolated caller target. This is a worker self-check, not an independent review.

- `python3 validate.py`: **PASS** (self-check).
- `sha256sum -c SHA256SUMS`: **PASS**.
- Finding status: `VERIFIZIERT`; independent cross-disassembly: `OFFEN`.
- Test status vocabulary: `PASS | FAIL | NOT_RUN | BLOCKED`.
