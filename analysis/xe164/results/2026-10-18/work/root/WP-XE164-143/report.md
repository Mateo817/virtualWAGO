> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-143 — preinit → entry → copyback → consumer synthesis

## Question and artifact

Which exact positional pipeline links pre-call local values through the resolved
entry call and helper copyback to the two `CMLoadComponent3` indirect consumers?

Input is exact `FW31-CODESYS3`, 5,181,396 bytes, SHA-256
`b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`,
at `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`.

Accepted bounded inputs are WP-XE164-140 report SHA-256
`8dac495cf3a22ef1d495008595bacd15ff43a00a439c06ba9fab6066f9362c1f`,
WP-XE164-141 report SHA-256
`9798ed34455f285f467ddb9840f8e1f5ba37a370c0db4f896f8814431752fd8d`,
and corrected WP-XE164-142 report SHA-256
`71cb30f66e86ec093e06837c20e7065ebc0dcf0ac6349c9a1053f84cb7e001c2`.

## Result

**VERIFIZIERT (positional static mechanics):** helper `0x2fc530` initializes
local words `L+0x04` and `L+0x08` to zero before the indirect resolved-entry
call at `0x2fc5c8`. A zero entry result selects the copyback lane, which copies
the then-current eight bytes `L+0x04..+0x0b` to caller block
`B+0x14..+0x1b`. Exact `CMLoadComponent3` then independently loads the two
32-bit words `B+0x14` and `B+0x18`, skips each if zero, otherwise invokes it as
an indirect target, and requires a zero return before continuing.

No ordinary instruction between the pre-call zeroing and the copyback writes
either local word. The intervening resolved entry call is the only explicit
call in that interval. Therefore any nonzero value observed by the two caller
consumers must differ from its bounded pre-call zero value during or as a side
effect of that call. This does not by itself identify which callee instruction,
alias, or external effect changed it.

**HYPOTHESE:** the two local positions are publication slots populated by a
successful component entry for later lifecycle calls. This description fits
the verified zero-initialize/call/copy/guard/invoke sequence, but no field name,
signature, semantic lifecycle phase, or concrete IoDrvDal binding is proven.

## Exact pipeline

The machine-readable table `flow.tsv` records both words separately. Common
steps are:

1. `0x2fc534` and `0x2fc564` zero `L+0x04..+0x0b`.
2. `0x2fc5c8` calls the resolved entry with `r0=L`.
3. Only entry result zero reaches the copyback lane.
4. `0x2fc604..0x2fc60c` copies the current eight-byte value to
   `B+0x14..+0x1b`.
5. `CMLoadComponent3` loads `B+0x14` at `0x2ffd54` and `B+0x18` at
   `0x2ffd6c`; nonnull values are called at `0x2ffd60` and `0x2ffd78`.
6. At each reachable indirect call, `r0=0`. This lane does not establish
   `r1`, `r2`, additional stack arguments, or a complete signature.
7. A nonzero indirect-call result takes the common error branch; zero or a
   skipped null target continues.

## Scope and alternatives

Observation is limited to `codesys3` helper `0x2fc530..0x2fc704` and
`CMLoadComponent3` post-helper range `0x2ffd48..0x2ffe07`. The entry target and
the two later indirect targets are not followed here. IoDrvDal, IoDrvKbus,
callee bodies, named field layouts, other callers, runtime and hardware are
excluded.

Alternative explanations retained: the entry can leave both words zero so
both calls are skipped; it can cause one or both to become nonzero through
direct writes, alias-visible writes or another side effect; an unknown target
can use conventions not established by this caller. Static ordering does not
select among those mechanisms.

## Method and status

This is a GPT-6.1 SOL root integrative Self-Review of the three accepted,
hash-bound Luna HIGH packages. REA-first provenance and bounded fallback
details remain in those packages; no new reverse-engineering tool query was
needed for the cross-range positional join. `validate.py` rehashes the exact
binary and three reports, then checks every address/offset/status row in
`flow.tsv` against a fixed expected table.

- Finding: **VERIFIZIERT** for the exact positional pipeline.
- Publication-slot interpretation: **HYPOTHESE**.
- Runtime/hardware tests: **NOT_RUN**.
- Package validator: recorded separately as **PASS** or **FAIL**.

Pseudocode is not used; this report is a derived static analysis, not original
source.
