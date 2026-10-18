> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-322 — independent review of WP314's lookup fixture

## Result

WP314's selected 8/7/7 numeric initializer match and 77/7 lookup composition are consistent with the pinned source words and WP312's independent arithmetic review. The main fixtures support a bounded synthetic route through the two wrappers, lookup, hash/equality callbacks, the selected GLib arithmetic route, and the lookup return. This finding is conditional on the explicitly mapped synthetic memory, callback/GOT targets, readable/writable non-alias ranges, valid frames, and normal source returns. It does not show a real constructor creates or populates this arrangement.

WP304's pinned initializer words set r0=8 and r2=7, store those at base+0/base+4, then store 7 at base+8. This verifies the numeric word pattern only. It does not identify a live object's structure or prove constructor reachability or state retention.

## Arithmetic audit

The 77/7 route starts with `SUBS r2,r1,#1`: r2 becomes 6 and C=1, so `BXEQ` and `BCC` are not taken. `CMP r0,r1` compares 77 and 7 and sets C; `BLS` is not taken. `TST r1,r2` yields 6 with Z clear, so `BEQ` is not taken. The two CLZs give 25 and 29; subsequent subtraction and reverse subtraction give selector r3=27; conditional `ADDNE r3,r3,r3,LSL #1` yields 81. At ELF 0xbaaac, the A32 PC operand is current PC+8, so the computed target is `0xbaaac+8+(81*4)=0xbabf8`, corresponding to Ghidra `0xcabf8`. The target remains inside the exact pinned 123-word body.

At that target, the CMP/ADC/SUBCS triples process shifts 4 down through 0. The compare carry results are C=0,1,0,1,1. The resulting states are `(r0,r2)=(77,0),(21,1),(21,2),(7,5),(0,11)`. The final MOV copies 11 into r0 and BX LR returns. I independently derived these values from the selected words and cross-checked the complete 31-PC sequence and flags against WP312's separate route matrix. This is a selected-input route, not a general division claim.

The adjacent eight-word caller saves original r0, r1 and LR in a 12-byte frame, calls the arithmetic body, restores the saved words into r1, r2 and LR, computes r3=7*11=77, then r1=77-77=0 and returns through the restored LR. The nested path itself has no selected data-memory operation and writes only its arithmetic registers and PC; r4-r11, SP and LR remain unchanged on this normal route. The wrappers' visible prologue/epilogues also restore their saved frame under mapped-stack and normal-return conditions. These are instruction effects under the fixtures, not ABI claims.

## Lookup composition and controls

Under WP314's stipulated mappings, the wrappers load the table pointer and pass query word 7 at entry SP-12. The lookup reads the hash callback slot and the key pointer; the selected callback path returns hash 7. The table size/mask words lead to the bounded 77/7 route. The stipulated first bucket word and callback slots then yield an equality hit and value T. Wrapper 0x2194 reads byte `[T+0x170]` and returns that byte (1 in the positive fixtures); wrapper 0x1ecc returns the source-derived 32-bit expression `T+0x110`.

WP314's five finite controls are consistent with their listed conditions: divisor 1 takes the direct return, a zero target byte returns zero from wrapper 0x2194, zero T takes the wrapper zero path, and the hash mismatch/empty-slot witness reaches a finite zero return. The controls test only their specified states and do not generalize lookup behavior.

The package includes the exact WP314 word ledger, fixtures, traces/effects, controls, pins and validator for auditability. My read-only review validator checks raw bytes and pins, all four primary 107-row traces and all 500 control rows against the 249-word source whitelist, validates the selected arithmetic route against WP312's matrix, and confirms the finite endpoints. WP314's own read-only validator and manifest also pass. WP305's writing validator is hash-pinned and statically reviewed but was not run; its output-writing defect is recorded in WP312 and remains applicable.

## Evidence boundary

| Claim | Status | Limit |
|---|---|---|
| 8/7/7 initializer stores and numeric fixture match | VERIFIZIERT | No object identity, constructor reachability or persistence proof |
| 77/7 branch/flag path, computed target and return 11 | VERIFIZIERT | Selected exact operands and route only |
| Lookup-to-T and wrapper results | VERIFIZIERT | Conditional on all synthetic memory, GOT, callback, stack and normal-return premises |
| Actual constructor allocation/population or reachable instance | OFFEN | Not established by initializer words or fixture |
| Runtime binding, process behavior, API/ABI contract | OFFEN | No process inspection or contract evidence |
| Native execution and device behavior | NOT_RUN | No vendor execution, VM, network or target interaction |

**Review method:** independent source/trace audit with explicit reuse of WP314's bounded source-driven traces and WP303's prior divisor-one baseline; the 77/7 arithmetic is independently checked against WP312's route matrix and the exact raw words. The source packages remain unchanged.
