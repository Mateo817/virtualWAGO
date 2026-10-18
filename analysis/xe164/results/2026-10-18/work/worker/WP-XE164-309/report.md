> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-309 — independent review of WP306

## Review result

**VERIFIZIERT** — WP306 corrects WP300’s status-lane state error. The exact provider words are `0xe1a0b108` at `0x55e5c` (`MOV r11,r8,LSL #2`), `0xe792300b` at `0x55e60` (`LDR r3,[r2,r11]`), `0xe3530001` at `0x55e64` (`CMP r3,#1`), and `0x9afffff9` at `0x55e68` (`BLS 0x55e54`). For the positive equality-hit route, the unconditional branch at `0x55ea4` targets `0x55e60`, skipping `0x55e5c`; `r11` therefore remains the value assigned at `0x55e10`. The correction records `r2`, `r11`, read address, loaded `r3`, and flags at the right instruction boundaries.

For both A and B, the read is `[bucket base + 0] = 7`. The LDR preserves the preceding flags `NZCV=0010`; CMP 7,1 sets `NZCV=0010` (C=1,Z=0); BLS is not taken and falls through to `0x55e6c`. The A/B trace event rows match WP306’s source-stepper events for all three PCs. This directly resolves the defect WP302 found in WP300, where `0x55e60` and `0x55e64` had been assigned the wrong operations and BLS reused stale flags.

**VERIFIZIERT** — The isolated boundary cases correctly re-evaluate flags from the actual CMP word. Status word 1 gives C=1,Z=1; status word 0 gives C=0,Z=0. Both take BLS to `0x55e54`, execute `MOV r0,#0`, and reach the modeled pop at `0x55e58`. These are independent synthetic lane inputs; they are not reachable positive A/B states and do not establish constructor or runtime state.

## Effect and assertion review

WP306 replaces WP300’s self-comparison snapshot and standalone frame arithmetic with checks against state produced by the source-stepper. The input memory dictionary is copied before route execution and compared at return; push/pop track the actual 10 lookup words and 3 helper words by address; the sorted write/read address sets and counts are checked; restored `r3-r11`, SP, and LR are checked against entry state; and status events are compared with independently recorded pre/post values. These assertions are connected to modeled instructions and mutated state, not identities that are true by construction. The visible instruction paths support the described no-ordinary-data-store result under the explicit callback-normal-return, readable-memory, and non-aliasing premises.

The isolated status-word runner starts at the status lane and supplies a stipulated saved frame for the later pop. That control validates the lane’s zero return and restore handling, but it does not re-execute the earlier lookup prologue; the positive A/B full stepper is the evidence for dynamically generated save/restore traffic.

## One wording qualification

WP306’s opening status line calls the stipulated callback tokens and memory “a constructible provider table.” Treat that only as a hypothesis; the package does not prove constructibility or reachability. Retained WP304 evidence shows the inspected initializer writes numeric `+0=8`, `+4=7`, and `+8=7`, whereas WP306’s synthetic fixture stipulates `+4=1`. The exact initializer therefore does not establish the divisor-1 fixture. This does not disprove a later mutation or another construction path, and no such path is reviewed here. Recommended wording: “HYPOTHESE: these stipulated values define a synthetic source route; actual construction, mutation, and reachability remain OFFEN.”

This is the sole material review qualification. WP306 correctly keeps constructor reachability, live callback binding, runtime selection, and ABI **OFFEN** elsewhere in its report and conditions. The corrected package should retain the fixture as a conditional synthetic example; WP300 remains frozen history and its fixture must not be presented as constructor-derived.

## Claim matrix

| Reviewed claim | Status | Independent finding |
|---|---|---|
| Status PC/opcode order and equality-hit branch target | VERIFIZIERT | Raw provider bytes and decoded A32 branch targets agree |
| A/B status read address, current `r11`, flags, BLS decision | VERIFIZIERT | Both rows read bucket base + 0, load 7, CMP to `0010`, then fall through |
| Isolated status 1 and 0 branch outcomes | VERIFIZIERT | CMP overwrites stale flags; both cases take BLS and return zero |
| Dynamic positive-route stack/effect assertions | VERIFIZIERT | Source-stepper tracks concrete writes/reads and restored state |
| Isolated boundary runner’s pre-status prologue/frame history | OFFEN | Frame is stipulated at lane entry; no earlier route asserted |
| WP300 fixture is constructed or reachable from WP304 initializer | OFFEN | WP304 initializes `+4=7`; no mutation/reachability path established |
| WP306’s phrase “constructible provider table” | HYPOTHESE; wording should be narrowed | Current evidence supports a synthetic fixture, not constructibility |
| Runtime, ABI, memory faults, concurrency, physical effects | OFFEN | Outside assigned offline static review |
| ELF execution and target/runtime tests | NOT_RUN | Not part of assigned review |

## Validation

Run `python3 validate.py` from this package. It independently checks provider words/branch targets, A/B status-event values, isolated CMP/BLS arithmetic, actual memory/stack/register assertions in WP306, and executes the read-only WP300/WP302/WP306 validators plus their manifests. Result: **PASS** for these scoped checks. No ELF execution or runtime testing was performed.
