> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-325 — numeric application-state stores and watchdog transfer boundary

## Result and evidence scope

**VERIFIZIERT, conditional on source-local registers, global pointers, and opaque-call boundaries:** The exact `ApplicationStateChanged` body contains numeric store paths keyed by its current `r4`, with branch inputs from a word at `[P+0x0c]`, a policy word at `[P+0x9c]`, and on one branch a byte at `[P+0xa1]`. Literal arithmetic from five distinct pool entries resolves to the same ELF-relative pointer cell `0x44420`; this package calls the object loaded through that cell `P`. Different literals and code paths do not establish different objects.

The four watchdog wrappers likewise load `P` from this same cell. They return local `0xffffffff` for a null `P`; otherwise they load `[P+0xdc]` into `r0` and transfer through a three-word PLT stub. Exact dynamic relocations identify the four local `lpkb_Watchdog*` targets. No function name is treated as a semantic contract, and no target body is expanded.

Opaque direct callees may change registers, the global pointer cell, pointed-to memory, SP/LR, and return normally or abnormally. The app body later relies on `r4/r5/r6`, reloaded pointers, and object fields across those calls. Therefore rows below describe encoded local stores and branch conditions when the current register and memory predicates hold; they do not prove a stable final object state. There is no ABI preservation assumption.

## Pinned input and address calculation

The source provider ELF is SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6` (148,792 bytes). WP321 retains the exact REA body/procedure artifacts, 193 selected instruction words, nine pool words, and body summaries; all selected instruction and pool words are checked against the raw ELF here. The application body is 142 instructions (568 code bytes) plus a 20-byte pool. The watchdog wrappers contain 12 primary code words (48 bytes) for SetTime and 9 words (36 bytes) for each other method, followed by an included three-word (12-byte) far PLT stub and one 4-byte literal word. WP321’s total instruction counts are therefore 15/12/12/12; the far Ghidra spans are not treated as contiguous code.

For `ApplicationStateChanged`, the literals at Ghidra `0x1fe7c`, `0x1fe80`, `0x1fe84`, `0x1fe88`, and `0x1fe8c` are used with their distinct ADD-PC instructions. In each case `architectural PC + literal` equals Ghidra `0x54420`, corresponding to ELF-relative `0x44420`. The four watchdog wrapper literals independently compute the same cell. These are source-relative addresses under an ELF load bias; runtime pointer contents and object identity are open.

## ApplicationStateChanged numeric transition paths

At entry, `r0` is copied to `r4`. The body makes three direct calls before its first state dispatch; later tests use current `r4`, so relating those tests to entry `r0` requires the opaque calls to preserve `r4`. Uses of `r5` for the pointer cell and `r6` for prior state likewise require continuity across the calls that bracket them. The global cell is checked for null first: if it reads zero, the body returns `0xffffffff` before object stores. On a nonnull path it stores byte `1` to `[P+0x78]` before the rest of the transition logic.

When the body reaches the state logic and the retry condition does not divert it, the source has these numeric local store paths:

| Current `r4` value | Branch predicates | Local stores encoded by the selected path |
|---:|---|---|
| `0` | `r4 != 3`; prior `[P+0x0c] != 3`; unsigned `(r4-1) <= 1` is false | `[P+0xa0]=0`, `[P+0xa2]=0`, `[P+0x0c]=0`, then `[P+0x78]=0` |
| `1` | `r4 != 3`; prior `[P+0x0c] != 3`; unsigned `(r4-1) <= 1` is true | `[P+0xa0]=0`, `[P+0xa2]=1`, `[P+0x0c]=1`, then `[P+0x78]=0`; a separate opaque call follows |
| `2` | `r4 != 3`; prior `[P+0x0c] != 3`; reread `[P+0x0c]` selects common (`==1`) or special (`!=1`) call route | `[P+0xa2]=1`, `[P+0x0c]=2`, and `[P+0x78]=0` in either completion route; special route stores `[P+0x78]=0` at a different instruction site |
| `3` | `r4 == 3` enters timeout path before the retry test | `[P+0xa0]=0`, `[P+0xa2]=0`, `[P+0x0c]=3`, then `[P+0x78]=0` |
| Other unsigned value | `r4 != 3`; prior `[P+0x0c] != 3`; unsigned `(r4-1) <= 1` is false | `[P+0xa0]=0`, `[P+0xa2]=0`, `[P+0x0c]=current r4`, then `[P+0x78]=0` |

State `2` has one conditional byte dependency: if `[P+0x9c]==1`, a later read of `[P+0x0c]` equals `1`, and current `r4==2`, the body reads `[P+0xa1]`, normalizes zero/nonzero to `0/1`, and stores that byte to `[P+0xa0]`. Other state-2 routes do not write `[P+0xa0]`. The route also rereads `[P+0x0c]` to choose between the special and common opaque-call sequences. The source explicitly computes the unsigned comparison `(r4-1) <= 1` modulo `2^32`; this makes `0`, `1`, `2`, and values above `2` follow the cases shown.

A non-3 current value with the prior word `[P+0x0c]==3` branches to an opaque retry: it passes numeric zero arguments to one target, passes the captured prior word to another, then returns to reread the state. No convergence or termination result is claimed. For current state `3`, the body passes the captured previous word and numeric `0x3e8` to an opaque target, compares prior `[P+0x0c]` with `[P+0x9c]`, and uses exact `0`/`3` tests to select an optional opaque chain. `0x3e8` is reported as a numeric argument without a unit or meaning.

The matrix describes instruction-level writes, not the final values after opaque callees. Calls occur between some reads, writes, and pointer reloads; `r4/r5/r6`, the pointer-cell content, memory, and stack continuity must hold for the source path to have the stated relationships. See `callee-boundaries.tsv` and `route-predicates.tsv` for those qualifications.

## Numeric relation to the provider byte gates

The exact WP320 `WriteBytes` source loads byte `[callback_base+0xa0]`: nonzero selects local branch target `0x1f238`, while zero continues to load `[callback_base+0xa2]`; zero at `+0xa2` selects the same target and nonzero falls through. WP320 `ReadBytes` loads `[callback_base+0xa2]`; zero selects `0x1eeb4` and nonzero falls through. These statements are branch behavior only; they do not label either route as acceptance or rejection.

The numeric offsets match bytes written by `ApplicationStateChanged`, but the consumer’s callback base must equal the producer’s loaded object `P` at runtime for this to become a joined contract. That identity is **HYPOTHESE**. No public callback signature, output request, effective output, or physical behavior follows from these matching byte offsets.

## Watchdog wrapper and exact PLT boundary

For all four methods, the wrapper first reads the global pointer cell at ELF-relative `0x44420` and tests only `P`. On null it returns `0xffffffff` via its local `mvn`/`bx lr` sequence. On nonnull it loads `[P+0xdc]` into current `r0` and transfers through the exact far PLT stub. The wrapper does not separately test `[P+0xdc]`; zero is not a source-local failure case.

| Wrapper | Tail `r0` | Tail `r1` | Tail `r2` | Stub / GOT slot | Exact relocation target |
|---|---|---|---|---|---|
| `WatchdogSetTime` | `[P+0xdc]` | entry `r0` | entry `r1` | `0x7b24` / `0x33264` | `lpkb_WatchdogSetTime` `0x14cc8` |
| `WatchdogStart` | `[P+0xdc]` | entry `r1` | entry `r2` | `0x7e24` / `0x33364` | `lpkb_WatchdogStart` `0x14db8` |
| `WatchdogStop` | `[P+0xdc]` | entry `r1` | entry `r2` | `0x7c20` / `0x332b8` | `lpkb_WatchdogStop` `0x14f50` |
| `WatchdogTrigger` | `[P+0xdc]` | entry `r1` | entry `r2` | `0x8214` / `0x334b4` | `lpkb_WatchdogTrigger` `0x14f94` |

`WatchdogSetTime` saves entry `r0` in `r12` and entry `r1` in `r2` before the null check, then copies the saved entry `r0` to `r1` on the nonnull path. The other wrappers leave `r1/r2` untouched. Each PLT stub computes its GOT slot from its encoded PC-relative `ADR`, `ADD #0x2b000`, and pre-indexed `LDR pc`; it writes back the slot address in `r12` and loads `pc`. Those three words do not modify `r0-r3`, SP, or LR. The wrapper bodies themselves do not allocate a frame. The exact target’s behavior, later register use, return convention, and runtime GOT winner remain open; no ABI is presumed.

## Evidence boundary and validation

| Claim | Status | Limit |
|---|---|---|
| Selected body words, literal arithmetic, numeric stores, local branch predicates | VERIFIZIERT | Exact bounded source words; conditional on current register/memory predicates |
| Four PLT stubs and `R_ARM_JUMP_SLOT` target names/values | VERIFIZIERT | Pinned ELF metadata only |
| Application byte stores feed the provider byte gates | HYPOTHESE | Offset match only; runtime object/callback-base identity unproved |
| Opaque callees’ register, GP, frame, global, and memory effects | OFFEN | No callee expansion or ABI assumption |
| State enum meaning, API/prototype meaning, watchdog behavior | OFFEN | Not inferred from names or numeric offsets |
| Effective output, physical reaction, runtime binding | OFFEN | No runtime or device evidence |

`validate.py` checks every source pin, all 193 raw instruction words and nine pool words, each PC-relative target calculation, the exact application stores and WP320 guard bytes, direct call targets, and all four exact JUMP_SLOT relocations. Expected validation: **PASS**. Native code, runtime, VM, network, device, and physical tests: **NOT_RUN**.
