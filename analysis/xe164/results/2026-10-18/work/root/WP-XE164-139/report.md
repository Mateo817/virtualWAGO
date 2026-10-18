> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-139 — Selector-3 control flow before the IoDrvDal loader call

## Result

**VERIFIZIERT:** For incoming dispatcher `r0=3`, the exact ARM jump-table
mechanics at ELF/file `0x362c..0x3650` select slot `0x3650`, which branches
directly to `0x3738`. The separate slot at `0x367c` enters `0x3684`, whose
bounded lane contains the possible zero store at `0x36a8`. Therefore the
selector-3 path that reaches the loader call at `0x37bc` does **not**
necessarily execute that zero store first; the observed bounded route bypasses
it.

On the continuing selector-3 branch, a guard must be zero, the indirect call
at `0x3770` must return zero, and the word loaded at `sp+0x60` must pass the
unsigned `<=10` check. The indirect-call result is copied to `r4`, so `r4=0`
on the continuing lane. The code jumps to the loop precheck before its first
body execution. A first loader call is reached only if signed comparison
`r4 < [sp+0x60]` holds; with `r4=0`, the bounded call path therefore requires
a signed-positive loop bound.

At that first reachable call, `r4` is zero, but the third positional register
argument is not `r4`: `r2` receives the prior value of `.bss` word ELF
`0x163d4`, after which the word is set to `r2+1` immediately before the call.
Consequently the first call's loop variable is statically zero while the
preincrement word passed in `r2` remains **OFFEN**. No first loader index or
semantic counter name follows from this bounded result.

## Inputs and identity

| Input | Size | SHA-256 | Use |
|---|---:|---|---|
| `libIoDrvDal.so.1.0.2` | 25,976 bytes | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` | exact ARM ELF |
| WP097 `report.md` | 9,161 bytes | `d0378dfe088702c8193b07e854519d4843ad22d48d64136a9b26f1cc60cbbd94` | accepted REA-gap and publication/caller context |
| WP097 `rea-evidence.json` | 322,297 bytes | `d39509c92c3a701adc99c55464de8df10451537d227281305660b5694a69394a` | retained REA records |
| WP138 `report.md` | 8,338 bytes | `4636602283315e20aa4409197014372c8e5aa9f3a49e5f0903ce1fa6977fea12` | exact preincrement-word/Xref context |
| WP138 `evidence.json` | 7,870 bytes | `66bf5aa4d603c5baa1e73bc81d4883df21bb68d67cc0889b69ff03a47b844400` | structured word/Xref evidence |

All addresses below are ELF link VMAs and file offsets for this `.text` range.
Ghidra's imported addresses add image base `0x10000`; no runtime load address
was observed.

## Method and exact path

REA was used first through the accepted WP097 session. It records that Ghidra
12.1.4 does not recognize dispatcher `0x1362c` or call `0x137bc` as lying in a
procedure: `resolve_containing_procedure` returned `not_in_procedure`, and
`procedure_info` returned `No procedure exists`. Relevant retained IDs include
`ev_0a50b88262089651ff8aa3d837d2dca34379ed8a742a8bfe52ea5c507ddbaf39`
for selector slot `0x13650` and
`ev_57b0db97c6961be0399ff36e36887ffee5c5d63818c49251faaad4f996a068b7`
for direct call `0x137bc`. The same failed function-boundary request was not
repeated.

The bounded fallback was GNU ARM objdump 2.44 over exact ELF VMA
`0x362c..0x37ff`. The control/data-flow rows are preserved in `flow.tsv` and
the validator reruns this exact disassembly from the hash-bound ELF.

The decisive machine-code steps are:

- `0x3634: sub r3,r0,#2`; for input `3`, `r3=1`.
- `0x3644: addls pc,pc,r3,lsl #2` selects branch slot `0x3650`, whose target
  is `0x3738`.
- The possible zero-store lane starts only at distinct slot `0x367c`, which
  branches to `0x3684`; `0x36a4` sets `r4=0` and `0x36a8` stores it.
- On the selector-3 continuation, `0x3770` is an unresolved indirect call and
  `0x3774` copies its result into `r4`. Nonzero takes `0x377c..0x3780` away
  from the loader lane; zero continues with `r4=0`.
- `0x3784..0x378c` loads `n=[sp+0x60]` and rejects unsigned `n>10`.
- `0x37a0` branches to precheck `0x37ec`; `0x37f4` enters the loop body only
  on signed `r4<n`.
- `0x37a4..0x37bc` loads the previous global word to `r2`, passes the other
  observed positional values, writes old+1 to the global word, and calls the
  loader at `0x2ddc`.

This proves a bypass of `0x36a8` on one exact selector-3 route to the loader;
it does not prove that no other invocation or dispatcher branch can write the
word beforehand. The nonzero guard branch at `0x3748 -> 0x3800`, the indirect
callee at `0x3770`, neighboring selector bodies, loader internals, later
runtime invocations and hidden aliases are excluded.

## Observation, conclusion, and remaining uncertainty

**Observation:** selector-3 slot and zero-store slot are different direct
jump-table entries. The bounded selector-3 call lane establishes `r4=0` before
the first loop precheck, then obtains `r2` independently from the `.bss` word.

**Conclusion:** zeroing at `0x36a8` is not a mandatory static predecessor of
the first loader call reachable through the bounded selector-3 null branch.
This strengthens E-XE164-156: the call-position word is still unknown even
though the local loop variable is zero.

**OFFEN:** prior invocations through other selector entries, ordinary runtime
`.bss` handling, the nonzero branch at `0x3800`, indirect callee effects,
global aliases, semantic meanings of the selector, loop bound and positional
arguments, runtime execution and hardware.

Pseudocode is not used as original source. The described flow is an
instruction-level tool derivation only.

## Tests

| Check | Status |
|---|---|
| Input sizes and SHA-256 | PASS |
| Recorded REA-first gap and cited Evidence IDs | PASS |
| Exact selector arithmetic and branch targets | PASS |
| Zero-store bypass on bounded selector-3 call lane | PASS |
| First loop-variable and third-argument separation | PASS |
| Reproducible bounded ARM disassembly assertions | PASS |
| Runtime, VM, network, device and hardware | NOT_RUN |
| Independent review | NOT_RUN |
| Root Self-Review | PASS |

The first validator invocation was **FAIL** because the root report and
validator contained three unmeasured context-size transcription errors
(1,329,576/8,075/8,537 instead of 322,297/8,338/7,870 bytes). They were
corrected from `stat`; all hashes were unchanged. The corrected validator was
then rerun. The second invocation was **FAIL** because the WP097 REA-bundle
full hash had also been transcribed with the wrong suffix; fresh `sha256sum`
fixed it to `d39509c9...a69394a`. Both repairs affect package metadata, not the
instruction evidence. The final corrected validator was then rerun.
