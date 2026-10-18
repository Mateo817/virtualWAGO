> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-381 — independent review of WP-XE164-374

**Review outcome:** source identity, literal/PLT arithmetic, finite hash/division values, and bounded branch/PC evidence check out. The positive T result remains conditional on an opaque `strcmp` premise that is too weakly represented in the event ledger for a fully closed return-state claim. WP374 itself and all upstream packages remain frozen.

## Raw source and address checks

I independently parsed the ELF32 little-endian program headers for both pinned objects and mapped all 237 WP374 ledger words through unique file-backed `PT_LOAD` ranges. Each recorded word matches the actual source bytes. Counts are 5 helper20b0, 3 Dal lookup PLT, 79 GLib lookup, 11 `g_str_hash`, 5 `g_str_equal`, 3 candidate `strcmp` PLT, and 131 divide words.

The helper literal contains word `0x00012120` at ELF VA **and file offset** `0x20c4`; those coordinates coincide because the executable PT_LOAD begins at file offset/VA zero. `0x12120` is the literal's value, not its file offset (the complete DSO is only 18,076 bytes). WP374's prose has that coordinate/value transcription bug; its raw-byte validator reads offset `0x20c4` and checks value `0x12120`, so this is report-only. The LDR at `0x20b0` uses architectural PC `0x20b8` plus `0xc` to read that literal. At `0x20b8`, architectural PC `0x20c0` plus the loaded value forms ELF-relative `0x141e0`; the actual LDR at `0x20bc` adds four and reads DalBias+`0x141e4`. The deliberately separate `+0x141e0` decoy is not the table-pointer read.

The encoded Dal PLT words at ELF `0x15f4..0x15fc` resolve the indirect cell at `0x140ec`, whose pinned relocation is `g_hash_table_lookup`. The candidate GLib strcmp PLT at `0x1c0c4..0x1c0cc` resolves candidate ELF cell `0x134044` (Ghidra VA `0x144044`), and the pinned relocation identifies `strcmp@GLIBC_2.4`. Neither the relocation nor the candidate file proves runtime provider selection.

For the two exact ASCII names, independent recurrence gives `0x106b2344` and `0xc703821f`. U32 multiplication by 11 gives `0xb49a83ec` and `0x8d269755`; unsigned divide by 7 yields quotient/remainder pairs `0x19ccee46/2` and `0x142a159e/3`. ASCII bytes are nonnegative under the signed-byte loads, so sign extension does not alter these two recurrences. The full 131-word divide route is present in the ledger.

## Trace review

The copied trace has 1,096 instruction rows over the four expected `(two names × two biases)` fixtures. Every row's PC/word pair maps back to one of the pinned words. Conditional branch executions are consistent with encoded conditions and their recorded pre-instruction NZCV. The stack source sequence has the expected GLib lookup 40-byte save, `g_str_equal` 8-byte save, then corresponding restore path; register/SP snapshots at the saved frame boundaries are internally consistent. This is an independent consistency audit against source bytes and trace state, not a second full A32 executor.

I confirmed the finite path arithmetic and the final value load is consistent with T when the stipulated equality return is zero. The empty control takes its source empty-return branch without equality. The mismatch control returns from the stipulated opaque boundary with one, lets `g_str_equal` return zero, follows the finite next-probe edge, and stops before executing that next probe.

One summary defect is concrete: `control-summary.tsv` writes `return=0x00000000` for `unequal_to_probe_edge` because the summary builder defaults a missing return value to zero. The control's `controls.json` has `stopped_before=('glib',0x45de0)` and no source return. The prose correctly says it stops at the edge and does not force a termination result, but the TSV's return column should be blank or replaced by an explicit stopped status. This does not change the positive route.

## Opaque strcmp boundary

At strcmp entry, the source has SP `entrySP-48`: 40 bytes belong to `g_hash_table_lookup`'s saved frame and 8 bytes to `g_str_equal`'s `{r4,lr}` frame. The event explicitly stipulates return r0, normal return PC, SP, r6=table, and r11=slot byte offset. The post-call source first restores g_str_equal's saved r4/PC from `[SP,SP+8)`, compares r0, then uses r6/r11 to read table+`0x1c`, the bucket hash at slot, table+`0x20`, and the value pointer at slot; its final pop consumes the saved lookup frame through `entrySP`.

The model executes the opaque event as a control transfer and changes only r0, so it implicitly leaves all mapped memory untouched. However, the serialized event and validator do not state or check preservation of `[SP,entrySP)` or the four post-call table/bucket/value words. The report says the needed saved frame remains, but it does not identify the byte extent or encode the required post-call data footprint. A normal return and preservation of SP/r6/r11 alone are insufficient to derive the modeled T if the opaque target may overwrite saved return words or those table entries. The closed fixture premise should explicitly preserve the 48-byte active stack range and the four post-call words; this is not an ABI conclusion, merely the memory condition needed by this selected path. The first post-return pointer load is at ELF `0x45ea0` (this positive `NE` route), followed by reads at `0x45e60`, `0x45e6c`, and `0x45e70`. `opaque-premise-audit.tsv` enumerates the required fields and missing event data.

No flags need be preserved over `strcmp`: `g_str_equal` uses CLZ/LSR and its pop, then the lookup executes `CMP r0,#0` before the result branch. The selected continuation does not rely on r1-r5/r7-r10/r12 after the boundary. Do not broaden this to a general callee-saved-register contract.

## Status and limits

Source words, encoded literal/PLT arithmetic, static relocation identities, and the two finite hash/division results are **VERIFIZIERT**. The four positive T returns are **fixture-conditional** on equality result zero and the saved-frame/current-data preservation premises above. The `strcmp` candidate/runtime binding, actual table construction, general probing/hash semantics, ABI/API guarantees, and runtime behavior remain **OFFEN**. No device, VM, target, network, or native ELF execution occurred.
