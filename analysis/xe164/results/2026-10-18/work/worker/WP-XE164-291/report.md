> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-291 — independent review of the getter-object +0x58 candidate

## Finding

**VERIFIZIERT (bounded source):** In the exact 18,076-byte `libdal.so.1.0.1` (`c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`), the word at getter-object ELF VA `0x14154+0x58 = 0x141ac` is raw addend `0x2ba8`. There is exactly one symbol-zero `R_ARM_RELATIVE` relocation at that cell. If that relocation is applied to the same loaded object with bias `P`, the conditional code-address candidate is `P+0x2ba8`. This does not establish that the old ReadInputs call uses this object or target at runtime.

The retained procedure-info query precedes full-body analysis and bounds one contiguous 112-byte body at Ghidra `0x12ba8..0x12c17` (28 words), corresponding to ELF VA `0x2ba8..0x2c17`. Every word, all three direct call targets, and all local branch destinations are checked against the exact ELF here. No additional callee or caller body was opened.

## Body mechanics and local outcomes

The entry prologue pushes `{r4-r8,lr}` (24 bytes), then copies entry `r0/r1/r2/r3` into `r4/r5/r7/r6`, respectively. It makes direct calls in order: `BL 0x2180` at `0x2bbc`, `BL 0x2194` at `0x2bcc`, and `BL 0x1ecc` at `0x2bdc`. Each call is followed by `CMP r0,#0` and a `BEQ` to `0x2c10`. That local block sets `r0=0xffffffff`, restores the saved registers and returns through the saved LR. Thus any tested zero result has the same local failure edge, assuming a valid saved frame and return.

Using WP277's hash-pinned local helper summary, a readable and nonaliased zero byte at `[P+0x14208]` makes helper `0x2180` return zero. Under that conditional binding and a valid frame, the first gate takes `0x2bc4 -> 0x2c10` and returns locally with `r0=0xffffffff`; the second and third calls and callback load are skipped. If the first result is nonzero, control falls through to helper `0x2194`; this report does not assume that call's result. WP277's `0x2194` and `0x1ecc` summaries are recorded separately in `helper-gates.tsv`: both depend on opaque PLT behavior, and no ABI, key stability, or equality of their nested results is assumed.

After all three tested returns are nonzero, the body loads a word from `[current r0+0x3c]` into `r3`. If this word is zero, `0x2bf0` branches to `0x2c08`, sets local `r0=1`, restores the frame, and returns through the saved LR. If it is nonzero, the body copies **current** `r6` to outgoing `r2`, **current** `r7` to outgoing `r1`, and **current** `r5` to outgoing `r0`; it restores `{r4-r8,lr}` and executes `BX r3`. The selected target's return value, register/memory effects, and any output-word update are unknown. The body itself has no local store through the entry output pointer.

## Register provenance and conditional E225 comparison

The assignments `entry r1→r5`, `entry r2→r7`, and `entry r3→r6` are only entry provenance. Helper calls intervene before the tail setup. The exact target arguments therefore come from the then-current `r5/r7/r6`; they equal entry `r1/r2/r3` only if the opaque helpers preserve those registers. The helper `0x2180` body locally preserves `r4-r7`, per WP277, but helpers `0x2194` and `0x1ecc` include opaque nested calls. No calling-convention assumption fills that gap.

WP199/E225 is pinned only as separate caller context: its list-entry `+0x58` call visibly supplies `r0=[r8+0x618]`, `r1=0`, `r2=0`, and `r3=sp+0x24` (an output-word address). If that exact call were conditionally bound to this body, the body would capture `r4=[r8+0x618]`, `r5=0`, `r7=0`, and `r6=sp+0x24`. Its tail would then be `(r0=0,r1=0,r2=sp+0x24)` only if opaque helper effects preserve `r5/r7/r6`. Equal second/third helper keys additionally require `r4` to survive the opaque effects inside helper `0x2194`. These are conditional register relations, not a new ABI or proof of shared object identity. The list-entry context `r8` is not equated to the primary `r9` or this getter object; getter-object `+0x58` remains only a candidate.

## Controls, preconditions, and limits

`instructions.tsv`, `call-branch-review.tsv`, `register-provenance.tsv`, and `frame-and-control.tsv` record all 28 words and local control edges. `counterprobes.tsv` tests each zero gate separately, first-byte zero versus nonzero, callback-null versus callback-nonnull, current-register mutations, and invalid-frame/nonalias premises. These controls expose why a tail-argument match cannot be inferred from entry values alone.

For the first-byte early return, the frame `[entrySP-24,entrySP)` must be readable/writable for push and readable for pop, the saved return must be valid, and `[P+0x14208]` must be readable. That byte must not alias the initial push range, which could otherwise change it before helper `0x2180` reads it. No stack-alignment ABI rule is asserted. The callback word at `[current r0+0x3c]` also requires a valid readable address after the third call.

Runtime provider selection, relocation application in a process, caller/provider object identity, callback meaning, output-word effects, target return, API semantics, and physical behavior remain **OFFEN**. Native execution, runtime, VM, device, and network actions are **NOT_RUN**. This is an independent static source review of the assigned body and hash-bound summaries only.
