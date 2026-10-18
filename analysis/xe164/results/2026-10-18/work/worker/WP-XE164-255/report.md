> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-255 — conditional zero-auxiliary CMCallHook route

## Finding

**HYPOTHESE (conditional static consistency):** If `CMCallHook` at `0x2fecc4` is entered with `r0=15, r1=0, r2=0, r3=0`, the two required memory gates hold, and the listed memory is readable/writable, the exact local instruction path reaches helper BL `0x2fedd4` without crossing a call. The optional BLX at `0x2fed2c` is skipped only when its exact slot `[0x005fc5b0]` is zero. On this path the first list head is used directly; no first-head-next-word-zero condition is read or needed before the helper call.

The direct-helper arguments are `r0=firstHead+16`, `r1=15`, `r2=0`, `r3=0`. Root246's accepted, complete helper evidence shows that it forwards incoming r1 to tail r0, gates on the halfword at helper-entry-r0+0x2c, loads its target from helper-entry-r0+0x20, and uses `BX r3` after its epilogue. Under the separate target/object conditions recorded in `obligations.tsv`, the corresponding tail arguments are `r0=15, r1=0, r2=0, r3=target`. The halfword values 2, 4, and 5 survive for forwarded selector 15; a null target returns locally. These are conditional byte-level facts, not observed execution.

## Path and exact flags

`candidate-path.tsv` lists all instructions on the chosen lane in execution order. The initial global compare continues only when `[0x00510868] != 0xffffffff`. The optional callback slot is loaded from `[0x005fc5b0]`; zero makes `cmp r4,#0` set Z and takes the branch to `0x2fed34`, skipping BLX `0x2fed2c`.

For selector 15, `r3=(r7-23) mod 2^32 = 0xfffffff8`. The compare against 290 is non-equal, so `cmpne r3,#27` executes and produces `C=1,Z=0`; the unsigned `BHI` at `0x2fed44` is taken to `0x2fef40`. That side lane stores 15 to `[0x005fc554]` then rejoins at `0x2fed48`; it is not a rejecting selector gate. `r8=(15-27) mod 2^32 = 0xfffffff4`; `cmp r8,#1` yields `C=1,Z=0`, so `MOVLS` is skipped and `ANDHI` runs, leaving r4 zero. These wraparound values and conditions are ARM32 arithmetic.

With r9 and initial r5 zero, the saved boolean remains zero. At `0x2fed70` and `0x2fed80`, `cmp r5,#0` sets Z, so the path loads the first head at `[ip+0x1c]` and branches to `0x2fee00`. It copies the head into r5, sets r2 to 1 for a nonnull head, forms r6 as head+16, and later takes `0x2fedc0 -> 0x2fef7c -> 0x2fedc4`. The selected path does not execute a `LDR` of `[firstHead]`; the head's next pointer is therefore not constrained to zero for this first callback. It also does not cross any call before `0x2fedd4`.

The helper is entered with object pointer `firstHead+16`. Its local guard allows halfword values 2, 4, and 5 for forwarded selector 15 and rejects a null target. For target nonzero and an accepted halfword, it restores its frame and executes `BX r3` using the word at `(firstHead+16)+0x20`. No object schema, function identity, ABI, runtime registration, or actual invocation is inferred.

## Evidence and limits

Source is the exact `codesys3` ELF from the private FW31 SD-image artifact path, 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`. `source-inputs.tsv` records the fresh hash. The copied `rea-evidence.json` retains both complete WP246 REA records for exactly helper `[0x2fec58,0x2fecc4)` and CMCallHook `[0x2fecc4,0x2ff0a0)`, with the matching source digest; local objdump windows are kept for raw-word cross-check. The package validator rechecks the source bytes, both complete record ranges, the path words/branches, and the accepted WP246 read-only validator and pinned report/flow/manifest hashes.

Memory values and alias noninterference are conditional assumptions, not facts observed in the ELF. The specific nonzero first-head condition permits reaching the candidate helper; the first head's next word is not read on this lane. The selected lane avoids the optional opaque call, so no ABI or cross-call register preservation is used. Other lanes, callbacks, runtime state, table-to-invocation binding, target identity and function ownership remain **OFFEN**. Static consistency with entry vector `(15,0,0,0)` does not prove that a CMExit table row or any runtime caller actually supplies it.

This is source-level static analysis only: no ELF execution, device, VM, network, or shared canonical-file action was performed. Root246 is the accepted upstream evidence record; this package makes no independent-review claim.
