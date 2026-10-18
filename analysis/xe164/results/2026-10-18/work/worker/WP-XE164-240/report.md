> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-240 — Low codesys3 indexed-PC dispatch window

**Status:** `OFFEN` for the requested cross-instruction path; all 34 dispatch/table mappings are `VERIFIZIERT`.
**Review type:** worker self-review. No independent review is claimed.
**Date:** 2026-10-18 UTC.

## Question and scope

For the exact `codesys3` ELF below, this package checks whether any of the 34 assigned `indexed_pc_dispatch` rows in ELF-VA `[0x7cb10,0xc58e4)` statically supplies a `[base,#0x20]`-loaded target and visible `r0=15` to the same register-indirect `blx`.

The package accounts for exactly the 34 rows selected from `WP-XE164-234/cfg-gap-inventory.tsv` and the 11 associated symbol markers. No neighboring dispatch rows, code symbols, or other ranges were used to classify the result.

## Bound inputs and method

- `codesys3`: 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`; extracted from manifested FW31 PFC100/PFC200 SD image SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c`.
- Gap inventory: SHA-256 `da464c51810a1a728eccddd7b6141e56502b8f7368dec55b9149a418b8bc40f3`.
- Bounded GNU ARM objdump input: SHA-256 `a0bcaec911083963c573bead0b28ee8c0b3106c3b8aa5eb595a556fbc5e75110`. Its producer identity is GNU objdump 2.44 per the bound toolchain record.
- REA provider: Ghidra 12.1.4, profile digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

I queried assembly at each of the 11 assigned symbol starts, exact guard-plus-dispatch bytes for each row, and the exact bounded table byte range for each row. The successful REA records are preserved in `rea-evidence.json` (79 records total); the matrix carries the record ID for each dispatch, table read, and associated symbol assembly query.

Ghidra's function model leaves a concrete CFG gap: the assembly record for symbol start `0x7e6b0` ends at `0x7e710`, while assigned dispatch `0x7e858` is beyond that body; a direct `procedure_assembly(0x7e858)` request reported that no procedure exists at the address. I recorded that gap and used only the pre-bound, hash-checked GNU ARM disassembly plus direct byte reads from the same REA target for the table fallback. I did not switch targets.

## Verified dispatch mechanics

For every matrix row, the dispatch word decodes as ARM `ldrls pc, [pc, selector, lsl #2]`. The applicable comparison is recorded beside it. The ARM-state table base is dispatch VA + 8. ELF32 PT_LOAD mapping places the assigned bytes at file offset `VA - 0x10000`; the validator checks that mapping from the source ELF's program headers. The unsigned LS condition selects indices 0 through the recorded maximum, inclusive. The special row at `0xa6278` compares `r3` with `r2`; a call-free local sequence sets `r2=11` at `0xa6268`, so its table contains twelve entries.

The 34 bounded tables contain 593 little-endian words and 260 unique destinations. Each word is recorded as its raw value and the corresponding loaded PC target. Every destination falls within the parser-bound label interval for the associated assigned symbol (from its marker to the byte before the next parsed marker) and coincides with a listed linear A32 objdump word start. This is not by itself proof of code or function ownership. The validator independently recomputes all table bases, file offsets, bounds, words, and destination checks against the three bound inputs.

## Requested path result

No dispatch row provides a verified `+0x20 load → r0=15 → same-register blx` path in this evidence package. A bounded textual scan across the 11 parser-bound label intervals found no explicit simple immediate `mov r0,#15` or `mov r0,#0xf` instruction. This is only that literal-pattern search: it does not resolve `r0` values formed by `movw`/`movt`, arithmetic, other write forms, memory loads, or opaque-call effects. The dispatch/table facts alone do not prove a struct-field meaning, a callback contract, or the value of `r0`.

The overall path question remains `OFFEN`, rather than a global negative claim. Statically computed `r0` values and alternative write forms remain unresolved; the analysis does not infer values across opaque calls, assign ABI preservation rules, or resolve memory/runtime inputs. No execution, runtime observation, target device, network, or VM action was performed.

## Validation

Run from this directory:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Result: `PASS` — all three input hashes, exactly 34 matrix rows, the 11 assigned symbol markers, PT_LOAD mappings, 593 table words, 260 targets, parser-bound marker intervals, listed linear A32 objdump word starts, and the limited simple-`mov r0,#15` text search were checked.

Evidence statements apply only to the exact manifested `codesys3` ELF bytes extracted from the FW31 PFC100/PFC200 SD image identified above, and to this static analysis configuration. They do not establish execution, ABI, hardware behavior, or the semantics of the named functions.
