> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-312 — independent review of the 77 / 7 route

The arithmetic and visible caller conclusions in WP305 are consistent with an independent source-driven calculation for the selected `r0=77, r1=7` path. All 131 words in the 123-word nested body and adjacent eight-word caller slice match the exact pinned GLib file. `route-matrix.tsv` records the 31 executed nested PCs, including every condition result, computed target, shifted compare, ADC carry input, and conditional subtraction. `caller-effects.tsv` records the corresponding two synthetic stack/LR cases.

The computed-PC step is correct: the instruction at Ghidra `0xcaaac` has A32 PC operand `0xcaaac+8`; preceding instructions calculate `r3=81`, so the next PC is `0xcaaac+8+(81<<2)=0xcabf8`. This is within the pinned nested body. The prefix conditions are also correct: `SUBS r2,r1,#1` gives `r2=6,C=1`; `BXEQ` and `BCC` fall through; `CMP 77,7` sets C; `BLS` falls through; and `TST 7,6` leaves Z clear, so `BEQ` falls through.

At the computed target, shifts 4 through 0 compare `r0` with `r1<<shift`. C is clear for shift 4, set at shift 3, clear at shift 2, and set at shifts 1 and 0. Each ADC consumes that comparison's carry, and each `SUBCS` executes exactly when C is set. The resulting `(r0,r2)` states after each triple are `(77,0)`, `(21,1)`, `(21,2)`, `(7,5)`, and `(0,11)`. `MOV r0,r2` therefore returns `r0=11`, followed by the normal `BX LR`.

The selected nested route contains no data-memory or stack operation, and its raw instruction destinations do not write `r4-r11`, SP, or LR. On normal return, the eight caller words save original `r0`, `r1`, and LR in a 12-byte frame, call the nested body, restore those saved values into `r1`, `r2`, and LR, then calculate `r3=7*11=77` and `r1=77-77=0`. It returns with `r0=11`, original SP and LR, and the caller's LR target. These are bounded instruction effects under the two mapped synthetic stack fixtures, not ABI claims.

There is a material operational defect in WP305's claimed read-only validator. The pinned `validate.py` opens `trace.tsv` and `results.json` in write mode and later opens `controls.tsv` in write mode (lines 136, 142, and 161). Running it regenerates those package artifacts. I did not run it or change WP305. Its frozen trace's nested PC sequence, raw words, computed-target row, and normal-return endpoints were separately checked against this review; the full reported results were not treated as an independent replay. This package's own `validate.py` is read-only and passes 539 checks.

The retained WP304 initializer evidence directly shows `MOV r0,#8`, `MOV r2,#7`, `STMIA r4,{r0,r2}`, followed by `STR r2,[r4,#8]`: source stores `+0=8`, `+4=7`, `+8=7` before the first opaque call. That supports the narrow divisor-seven initializer observation. It does not prove that the initializer is reached by a live constructor, that later opaque calls preserve state, or that any runtime table has those contents. Constructor reachability and runtime state remain **OFFEN**.

The boundary controls agree with their visible source conditions: divisor 1 makes the first `SUBS` set Z and takes `BXEQ LR`; divisor 0 makes C clear and branches to `0xcac58`, where this review stops; changing the numerator to 84 retains the computed target and yields a distinct bounded-path result `r0=12`. The injected unmapped-target case in WP305 is reviewed as a whitelist guard in its code, not executed through the output-writing validator.

## Review status

- **VERIFIZIERT:** exact source words, the selected branch/flag route, the computed-PC target, all five LSL/ADC/SUBCS stages, the nested normal-return effects, and the eight-word caller behavior in two synthetic frames.
- **FAIL:** WP305's validator is not read-only because it overwrites three output files when run.
- **VERIFIZIERT:** the pinned WP304 initializer source contains the stated immediate stores before its first opaque call.
- **OFFEN:** general division semantics, alternate computed-PC targets and handlers, constructor reachability, runtime state, ABI/API meaning, and preservation across opaque functions.
- **NOT_RUN:** native ELF execution, runtime/ABI tests, and device or concurrency behavior.
