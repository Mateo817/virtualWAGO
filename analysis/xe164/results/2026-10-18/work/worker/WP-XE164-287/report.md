> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-287 — independent review of corrected WP282

## Result

**VERIFIZIERT:** I rechecked WP282 against the exact installed libc source, the complete WP279 312-word inventory, retained REA body bounds, the raw A32 words at the 48 fetched PCs, and the corrected trace. The two requested fixes are present and correct: the PLD at `0x91e6c` uses the already post-incremented `r1=S+0x40`, giving hint address `S+0x140`; and preservation comparisons use immutable `pre_regs` / `pre_dregs` snapshots, with an injected `r5` mutation rejected. I found no source/trace contradiction in the assigned route.

This is a bounded instruction-path review, not a second runtime execution or an ABI finding. Runtime symbol resolution, caller/provider identity, actual mappings, platform fault behavior, cache state, and concurrent modification remain **OFFEN**.

## Independent source and path checks

The pinned source is the 1,434,296-byte private extracted libc with SHA-256 `dc47ee066e2c2d73ff9186440787543c3020711611f09002b6ab187d97d9dfa2`. Retained REA identifies one contiguous 1,248-byte body at ELF `[0x919c0,0x91ea0)` and Ghidra `[0xa19c0,0xa1ea0)`. The full 312-word WP279 inventory agrees with the exact little-endian source words. The final trace contains the independently expected 48-PC sequence; each PC/word pair is checked against source, and the selected branch destinations are recalculated from A32 `PC+8` and sign-extended branch displacement.

For the assigned page-aligned biases, `D=0x5001a270` and `S=0x62014154`. The entry compare computes `136-64=72` with carry set, so `BCS` reaches the large route. `r1&7=4` and `r12&7=0`; the compare selects the unequal-alignment route. `MOVS r8,r12,LSL #29` yields zero, so the conditional shortcut enters the vector path. The two length decrements produce 72 then 8 with carry set; therefore the `BCC` at `0x91e68` is not taken. The next decrement produces `0xffffffc8` with carry clear; the `BCS` at `0x91e84` is not taken. These values and condition outcomes match the final trace.

The six selected NEON words match the retained objdump forms: four-register structure transfers cover 32 bytes and advance their base by 32; the one-register tail transfer covers 8 bytes and advances by 8. Independently replaying those chunks over two distinct byte patterns yields exact output `[D,D+136)` equal to the pre-state source `[S,S+136)`, while leaving the source unchanged under nonoverlap. The ordinary access order is: save `r8`; read source blocks `[S,S+32)`, `[S+32,S+64)`; write `[D,D+32)`; read `[S+64,S+96)`; write `[D+32,D+64)`; read `[S+96,S+128)`; write `[D+64,D+96)` and `[D+96,D+128)`; restore `r8`; read/write the final 8-byte blocks. The exact per-PC intervals and PLD list are in `memory-review.tsv`.

The tail dispatcher uses `r2=8`, computes `r3=0x34-(8&0x38)=0x2c`, and at `0x919d4` reads architectural PC as `0x919dc`, giving target `0x91a08`. It performs the final 8-byte transfer. `TST r2,#4` sets Z; the subsequent `MOVS r2,r2,LSL #31` yields zero and keeps Z set, so halfword and byte conditional operations do not execute before `BX LR`.

The corrected PLD sequence is `S`, `S+0x40`, `S+0x80`, `S+0xc0`, `S+0x100`, `S+0x140`. In particular, `0x91e6c` occurs after the `0x91e5c/60` loads have advanced `r1` by 64. These are advisory hint addresses, not ordinary reads; the last hint lies beyond the required 136-byte ordinary source interval. The trace therefore does not establish that the hint address is mapped or characterize hardware prefetch behavior.

## Register, memory, and model-boundary review

The final stepper takes integer-register entry snapshots as a tuple of values and D-register snapshots as a tuple of immutable `bytes` before executing. It compares final preserved registers against those snapshots. The existing injected `r5` corruption check is non-tautological; this review independently tests mutations to every claimed preserved GPR (`r0,r4-r11,sp,lr`) and to `d8/d9`, and verifies the check does not incorrectly require unchanged `r3` or `d0`. Direct instruction use confirms `r0`, `r4-r7`, `r9-r11`, `sp`, and `lr` are unchanged at return; `r8` is saved/restored; `r1/r12` advance 136, `r2` becomes zero, `r3` is used by dispatch, and `d0-d7` are written. The report's narrower `d8-d9` untouched statement is true; no ABI is inferred.

The result depends on readable/writable ordinary ranges, nonoverlapping source/destination and stack intervals, valid entry/return state, page-aligned nonwrapping biases, reached body instructions, NEON support, and no fault that interrupts the selected route. The stepper cannot establish a real process mapping, fault behavior, partial multi-register transfer behavior, execution concurrency, or PLD side effects. It treats exact selected NEON words as their audited transfer forms, not as a general ARM emulator. The final WP282 report acknowledges these boundaries. A compatibility caveat remains: source and destination aliasing is rejected rather than modeled; independent partial-overlap controls also reject. This is material to interpreting the byte-copy equality.

No changes or expansions were made to WP278, WP279, or WP282. No other function was inspected. Native execution, runtime, VM, device, and network checks are **NOT_RUN**. This package is an independent static/model review.
