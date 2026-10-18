> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-355 — numeric VPI-global getter, setter, reset and callback slice

**VERIFIZIERT, source-local:** all PC-relative global-base calculations in the three complete bodies and the bounded callback slice resolve to the same Ghidra coordinate `B=0x57bac`, corresponding to module/ELF RVA `0x47bac` in the pinned ET_DYN image. Each body also computes numeric callback target Ghidra `0x24774` / module RVA `0x14774` and passes it to a call named `pthread_once`. The getter’s source implements two unsigned saturation/fallback lanes; the setter’s `BHI` comparisons are unsigned and divide the query words by eight before comparison. The reset body stores zero over `B+0x18..B+0x2f` after its opaque once call. All results are conditional on the current registers, stack/frame contents, readable/writable memory, and opaque-call effects described below.

No ABI, API argument meaning, enum, data layout, synchronization effect, callback execution, initialization lifecycle, runtime binding or behavior from symbol names is inferred. Synthetic arithmetic controls are source calculations only; no native code was executed.

## Pinned source

The subject is the exact 148,792-byte FW31 `libpackbus.so.1.0.1` with SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. It is ELF32 little-endian ET_DYN with zero-based first `PT_LOAD`, so the module RVA equals the ELF VA and Ghidra addresses in these records are `RVA+0x10000`. Frozen root WP352 manifest digest: `9292ad4dae0381b22883e95ced15c3bcb7195a6ee8bbdc6047d1dbbda0023a34`. The exact retained body counts are 63 words (`ulGetDigOffset`), 88 (`ulSetDigOffset`), and 12 (`vResetDigOffset`), plus nine bounded raw fallback instructions at `0x24774` and eleven separate pool words. `source-pins.tsv` identifies copied files and hashes; the validator rechecks the WP352 manifest, copied subject bytes, all 172 instruction words, and 11 pools against the exact ELF.

The bounded nine-instruction callback slice is not a Ghidra procedure: metadata lookup at `0x24774` returned no procedure. Its 40-byte read includes nine instructions through a tail branch and the following literal word, but the model treats only the nine instruction words as code. The callback’s execution by any once-named call is not established.

## Global and callback address arithmetic

`global-base-ledger.tsv` records every PC/literal sum. The `ulGetDigOffset` source derives B from pool literals at `0x24898`, `0x248a0`, and `0x248a4`; `ulSetDigOffset` derives the same B from `0x24a08`, `0x24a10`, and `0x24a14`; `vResetDigOffset` derives it from `0x24a48`; the bounded callback derives it from `0x14798`. For each, the literal is added to the architectural PC (`instruction PC+8`) at the indicated `ADD`, yielding `0x57bac` / `0x47bac`. No distinct base is assigned to the setter’s two zero lanes.

The callback argument is separately derived from negative pool displacements: getter `0xfffffdb4` at the `ADD` PC, setter `0xfffffea8`, and reset `0xfffffd40` each resolve to Ghidra `0x24774` / module RVA `0x14774`. In the bounded raw slice, literal `0x33428` added to architectural PC `0x24784` resolves back to B. The nine source words zero B+0 through B+0x2f using a 16-byte `VST1.8` and four 8-byte `VSTR.64` stores, then branch to module RVA `0x77d0` / Ghidra `0x177d0`. This describes the bounded code if reached, not pthread-once behavior.

## Getter numeric paths

The complete body captures current entry r0 in r7, r1 in r4, and r2 in r5. Its first gate tests current r4 and, conditionally, current r5 for zero. If either is zero, it sets r0 to numeric 1 and returns before the process-image query call. Otherwise it builds the query call with current r0-r3 all zero and stack arguments containing the exact output addresses in `query-stack-vectors.tsv`; the call result itself is not tested. The query words later consumed are current `[sp+0x10]` and `[sp+0x14]` after that opaque call.

After the call, current `r7==0` selects Q0=`[sp+0x10]` and global halfword `[B+0x18]`; current `r7!=0` selects Q1=`[sp+0x14]` and `[B+0x24]`. The two branches implement the same arithmetic. `CMP Q,#0x80000` sets the unsigned condition: for `Q<0x80000`, the stored value is `Q>>3` and the local result is numeric 0; for `Q>=0x80000`, the stored value is `0xffff` and the local result is numeric 2. At the threshold itself, the saturated lane is taken.

The body writes that value as a halfword through current r5, then loads the selected global halfword. A nonzero loaded halfword is copied as a halfword through current r4. If it is zero, the body first stores zero through r4, then reloads current `[r5]` and stores that halfword through r4. Thus with distinct, nonaliasing output/global addresses, the zero case falls back to the just-written shifted/saturated value. Pointer aliasing changes this exact sequence: for example, if r4==r5, the zero store through r4 overwrites the prior value before fallback reload. If r5 aliases the selected B field, the earlier size store can change the subsequent global load. The code has no alias or memory-access check; the controls demonstrate both the nonalias fixture and a pointer-alias counterexample.

The numeric returns 1, 0, and 2 are reported as source words/paths only. They are not given API status meaning. Stack query values, live r4/r5/r7, B, saved frame words, and pointer memory must remain usable across the opaque calls for the stated paths.

## Setter branch and store matrix

The complete setter captures current entry r0 into r4 and current entry r1 into r5, derives B in r6, calls the once-named target with current r0=B+0x30 and r1=0x24774, then calls the query target with the exact vectors in `query-stack-vectors.tsv`. Its return is not tested. Afterward it compares the current r5 value, then current r4 selector. The setter’s branches require those registers still to carry the captured words; no ABI preservation is presumed.

When current r5 is zero, the query call has already occurred, but its output words are not read on that lane. Current r4==0 chooses the first zero route: `STRH 0` at B+0x18..19 and an 8-byte zero vector at B+0x1c..23. The two bytes at B+0x1a..1b are not written. Current r4!=0 chooses the other: `STRH 0` at B+0x24..25 and an 8-byte zero vector at B+0x28..2f; B+0x26..27 is not written. Both routes set numeric r0=0 before return.

For nonzero r5 and current r4==0, Q0 is current `[sp+0x10]`; for nonzero r5 and current r4!=0, Q1 is current `[sp+0x14]`. At each comparison, `CMP r5,r3,LSR #3` compares the current 32-bit r5 against the logical-right-shifted current query word. The subsequent `BHI` means unsigned `r5 > Q>>3`, not an assumed `r5<=Q>>3` guard. If less, the function returns numeric 1 without the local B update. If equal, it takes that selector’s zero lane and returns 0. If greater, it updates the matching block and returns 0.

The r4==0 greater-than update stores the low 16 bits of current r5 at B+0x18, then copies current stack words `[sp+0x18]` and `[sp+0x20]` to B+0x1c and B+0x20. The r4!=0 greater-than update stores low16(r5) at B+0x24 and copies current `[sp+0x1c]` / `[sp+0x24]` as two words at B+0x28 / B+0x2c. These query words are separate from Q0/Q1 and remain opaque current stack contents.

A concrete source arithmetic counterexample is r5=`65536` and Q=`524280`: `Q>>3=65535`, so unsigned BHI selects the greater-than store path, but `STRH r5` writes low16=`0` to the selected B halfword. For the equality control (r5=65535), the zero lane executes; for r5=65534, the less lane returns 1. `numeric-controls.tsv` repeats this for both selectors and includes an unsigned-vs-signed control. This is a finite machine-width fact, not a conclusion that the application has a bug or unsafe behavior.

Lock/unlock call returns are not used as branch decisions; subsequent stores or explicit r0 moves define the local return. The process-image query return also is not tested. Call target effects, query contents, and registers/stack after calls are conditional; there is no lock contract inferred.

## Reset stores and opaque return

The reset body derives B, passes current r0=B+0x30 and r1=0x24774 to the once-named call, then locally zeros Q8 and stores `VST1.8 {d16,d17}` at B+0x18 (16 bytes) and `VSTR.64 d16` at B+0x28 (8 bytes). Those adjacent regions cover exactly `[B+0x18,B+0x30)`, 24 bytes. This body’s stores occur after the opaque call and are source-local. They require current r4 to remain B and the stack frame and destination memory to remain valid.

Unlike the getter/setter query and lock/unlock returns, reset does not write r0 after the once call. The opaque current r0 result flows through the vector stores and epilogue as the function’s returned word, if execution reaches the epilogue. Its meaning is unknown; it is not represented as an ignored return.

## Limits and verification

All caller-supplied current values, stack output words, memory aliasing/validity, opaque call clobbers/effects, actual callback invocation, and persistence across later reads remain open. The numeric selector/value lanes do not establish names, statuses, fields, process-image units, lifecycle, synchronization, or ABI.

`validate.py` is read-only. It validates both frozen input manifests, exact raw code and pool bytes, every PC/literal sum, branch targets and source register/stack rows, getter/setter numeric boundaries including the 65536/524280 truncation fixture, and exact footprints/gaps. **Native ELF, runtime, VM, device, and network: NOT_RUN.**
