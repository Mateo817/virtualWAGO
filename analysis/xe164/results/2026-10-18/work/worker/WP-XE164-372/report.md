> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-372 — independent WP364 helper trace audit

**VERIFIZIERT, bounded:** independently source-checked the 48 selected WP364 fixture traces against the exact FW31 `libpackbus.so.1.0.1` candidate and WP363 body words. The computed-PC selector table, selected NZCV conditions, per-instruction load/store widths and effective addresses, key alias orderings, selector-4 XOR iterations, and stack return events agree with the encoded instructions. **OFFEN:** descriptor/API meaning, arbitrary overlap behavior, runtime binding/reachability, native fault semantics, concurrency, and behavior outside these fixture states. **PASS:** this package’s read-only validator. **NOT_RUN:** native, vendor-runtime, VM, network, or device execution.

The source candidate SHA-256 is `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. Frozen WP363 manifest SHA-256 is `3785657ec174cf250f5cc1973596c8b86642c070e4da88b98b1a852232f8ac82`; frozen WP364 manifest SHA-256 is `074020812594146a288a86ef3698466c563f93a7554653ffeffa07e55cb2dd77`. Both copied packages pass their retained manifest checks. WP363 contributes exactly 24 `read_bits` and 50 `write_bits` source words. Each fetched PC/word in the 48 traces matches that source table and the raw ELF bytes. The 48-row case matrix also agrees with the traces’ body, bias, selector, alias, status, steps, access counts and stack endpoints.

## Dispatch and path audit

Raw A32 decoding of `write_bits` word `0x908ff103` at ELF `0xd4e0` gives condition LS, ADD, destination PC, base PC, and `r3 LSL #2`. Architectural PC is instruction address plus eight, so selector `s` first forms `r3=U32(s-1)` and, when the unsigned `r3<=4` condition is true, indexes the inline branch words at `0xd4e8 + 4*r3`. Decoding each branch immediate from its own PC+8 gives:

| Selector | Table word | Decoded next source PC |
|---:|---:|---:|
| 1 | `0xd4e8` | `0xd56c` |
| 2 | `0xd4ec` | `0xd55c` |
| 3 | `0xd4f0` | `0xd510` |
| 4 | `0xd4f4` | `0xd514` |
| 5 | `0xd4f8` | `0xd4fc` |

Selectors 0 and 6 produce `0xffffffff` and 5 after subtraction respectively. `CMP r3,#4` sets flags for which LS is false in both cases, so the computed-PC add is skipped and the fallback branch at `0xd4e4` reaches the `0xd510` epilogue without the selected destination store. This establishes only encoded local control flow for the numeric selectors.

The audit recomputes CMP/SUBS flags and evaluates raw condition fields for the read-selector equality branches, write-selector LS dispatch, selector-4 BMI, and selector-4 BNE loop. For the transfer instructions, it decodes single and halfword load/store fields to check each recorded access address and width against the current register state. This includes indexed byte/word accesses and the current stack reads/writes. The tests are finite to the recorded source paths and do not model CPU faults or unrelated instructions.

## Aliases, masks and selector 4

In the explicit read selector-1 alias fixture, `Z` equals `B+word[M+4]`. At `0xd5c8` the destination byte becomes `0xf0`; the later source load at `0xd5cc` reads that same `0xf0`. The checked final byte remains `0xf0`. In the explicit write selector-1 alias fixture, the clear store at `0xd57c` writes `0xf3` before `0xd580` reads `Z` at the same address. The later output remains `0xf3`. This confirms the source ordering in these byte maps; entry-state algebra that reads the aliased byte before the clear would give a different result.

For the selected one-hot, multibit, and zero-mask fixtures, the independently evaluated clear/test/conditional-OR equations agree with the recorded final bytes. Read selectors 2/5 and write selector 2 copy the current byte read in the trace; write selector 5 stores the current source byte AND the selected mask byte. These are local numeric effects, not enum or descriptor interpretations.

For selector 4, source order computes `A+2N`, decrements N by two, reads the halfword at `A+2N-2`, and uses its value as an offset into B before the BMI test. The N=1/2/3 traces then take the source loop as encoded: reverse-order entry reads followed by XOR, exactly N byte reads in each selected fixture, and a byte store at the current halfword value loaded from `D+8`. The raw `SUBS` flags distinguish N=1’s direct BMI path from N=2/3’s loop path; loop CMP flags decide whether BNE repeats. At N=0, the attempted halfword read is at `A-2` and occurs at `0xd528` before `0xd530` BMI. The synthetic map leaves that address unmapped, so the model records an attempted read and stops before the branch or store. No native exception behavior is claimed.

Stack traces match the encoded frame operations: `write_bits` pushes r4/LR at entrySP-8/-4 and normal epilogues read those words in order, restoring SP and setting terminal PC to saved LR. Read selector 1 saves LR at entrySP-4 and restores through its post-index load. Other selected return paths use `BX LR`. The model proves these fixture transitions only.

## Review limitation

WP364’s `replay.py` interprets retained REA assembly strings after checking that trace words match WP363’s pinned word table; it does not independently decode every instruction’s A32 fields. That is a model-method limitation, not a source mismatch. This audit independently decodes the computed-PC table, conditional path gates, data-transfer footprints and selector-4 loop branches identified above. Full runtime or arbitrary-input execution remains outside scope. `review-matrix.tsv` records this distinction and the verified claims.
