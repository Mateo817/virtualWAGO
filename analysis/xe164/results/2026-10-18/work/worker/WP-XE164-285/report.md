> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-285 — independent ReadInputs target-body review

## Finding

**VERIFIZIERT (bounded source):** On the exact 18,076-byte provider ELF, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`, the three WP284 cells are `0x14198` (+0x44) → relative target addend `0x2dac` (88-byte body), `0x141a4` (+0x50) → `0x2c70` (164 bytes), and `0x141a8` (+0x54) → `0x2c18` (88 bytes). Each cell has one symbol-zero `R_ARM_RELATIVE` entry. This is a conditional loaded-address candidate `P+addend`, not proof of runtime binding or object publication.

The three complete bodies each directly call numeric local targets `0x2180`, `0x2194`, and `0x1ecc` in that order, with one zero-return gate after each. For the sized body at `0x2c70`, the first-call failure is `0x2c88 CMP r0,0` → `0x2c8c BEQ 0x2d0c` → `0x2d0c MVN r0,#0` → `0x2d10 POP {r4-r8,pc}`. The simple bodies have corresponding exact paths in `early-failure-join.tsv`. Under WP277's accepted local summary for helper `0x2180`, a readable, nonaliased zero byte at `P+0x14208` makes that first call return zero, so each candidate follows its local `r0=0xffffffff` return edge without reaching a later call. This remains conditional on the actual helper binding and valid entry frame. A byte value of one is a counterexample to that early edge: the first branch falls through to the next direct call; no later call outcome is modeled.

## Body differences and register evidence

The two simple read candidates load their post-call callback words at different displacements: candidate `+0x44` reads `[current r0+0x24]`, while `+0x54` reads `[current r0+0x28]`. These are not the write-side displacements in WP274 (`+0x30` reads `[current r0+0x2c]`; `+0x40` reads `[current r0+0x30]`). Each simple body returns `1` when its callback word is zero; otherwise it restores its local save area and branches with `BX` to that current word. No callback behavior is inferred.

The sized read candidate at `+0x50` reads the callback from `[current r0+0x18]`, then, only if nonzero, reads its length word from `[current r0+0x4]`. The sized write candidate (`+0x3c`, WP274/276) instead reads `[current r0+0x20]` and `[current r0+0x8]`. The read body computes `s=(current r5+current r6) mod 2^32`, selects `m=max_unsigned(current r5,current r6)`, and rejects when `m>s` or `length<s`. Thus pass requires `m<=s` and `length>=s`, including the no-overflow condition. The three instructions that select/compare the maximum do not use `r7`: it is copied to outgoing `r2` only after the gate passes. On pass, outgoing values are current `r5`, current `r6`, current `r7`, and the saved callback word, followed by local register restoration and `BX`.

No ABI preservation is assumed. In the sized prologue, `r5/r6/r7` start as entry `r2/r3/[entry SP]`; opaque direct calls then intervene before the comparisons and transfer. They may modify those registers. Similarly, `r4` starts as entry `r0`, and the body resets `r0` from then-current `r4` before calls two and three; it does not reload `r4` from entry state. Callback and length accesses use the current `r0` after the third call. Therefore the initial values are provenance at function entry, not proven values at later use. The exact call, branch, frame, and current-register records are in the TSV matrices.

## Read ordering, counterprobes, and boundary conditions

The sized candidate checks the callback for zero before reading the length. A null callback returns `1` on that local path; the length load and unsigned gate are skipped. Synthetic unsigned controls distinguish equality, one-byte-short length, high-bit operands, and wrapped sums. The `r7` counterprobe changes only `r7`: the unsigned gate result remains fixed while the forwarded outgoing `r2` changes. Current-call-state controls also change `r4`/`r5`/`r6`/`r7` between opaque calls, demonstrating which later instructions consume current values; they establish no real callee effects.

The early-failure join requires a valid readable/writable local stack frame, readable saved return state, and a readable helper byte. The helper byte must not overlap the initial push range, or the prologue could change the byte before the helper reads it. For the sized candidate, `[entry SP, entry SP+4)` must also be readable. No stack-alignment ABI rule is asserted. Full preconditions and negative controls are recorded in `frame-premises.tsv` and `counterprobes.tsv`.

## Evidence and limits

WP284 retained the three procedure-info results followed by complete bounded REA function records; all six JSON files are copied and hash-pinned here. Every decoded instruction in the three full bodies is copied into `instructions.tsv` with ELF VA, Ghidra VA, source word, and bytes, then checked against the exact ELF by this package's read-only validator. The three table words and relocation records are rechecked from ELF section data. WP274/276's already bounded write-side instruction witnesses and WP277's accepted helper summary are included as bounded comparison/context only; no additional function was opened.

The `+0x58` location mentioned in older ReadInputs context is a separate list-entry context and is not joined to getter-object `+0x58`. Runtime provider winner, relocation application, table identity, publication/copy path, callback targets, opaque helper effects, callback contract, API semantics, and physical I/O remain **OFFEN**. No ABI is inferred; native execution, runtime, VM, device, and network checks are **NOT_RUN**. This is an independent static source review.
