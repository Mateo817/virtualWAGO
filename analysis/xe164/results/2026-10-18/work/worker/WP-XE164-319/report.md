> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-319 — libdal method paths to backend tail boundary

## Result

**VERIFIZIERT, conditional on the listed synthetic memory and binding premises:** The exact source words for six libdal method candidates and the separate getter `+0x58` candidate were stepped from each method entry through their three direct helpers (`0x2180`, `0x2194`, `0x1ecc`), the lookup PLT, the pinned GLib lookup/callback/arithmetic words, and the method’s final local branch. Fourteen primary traces cover two address-bias fixtures and seven method positions/context cases in each. Every trace stops at the provider method's `BX r3` to a stipulated backend code pointer; no backend callback instruction is executed.

The source-local joined route is: helper `0x2180` returns byte 1 from `DalBias+0x14208`; helper `0x2194` stores key word 7, follows the WP314 divisor-7 GLib route to stipulated `T`, reads `[T+0x170]=1`, and returns 1; helper `0x1ecc` repeats the exact table lookup and returns `C=T+0x110`. These observed return values make the method-local three nonzero gates pass on the selected path. The method then reads its candidate callback word from a specific offset relative to current `C`, restores its source frame, and transfers to that pointer when nonzero.

The field values and pointer joins are fixture premises. WP304 proves only that its bounded initializer writes the numeric words `8,7,7` at offsets `+0,+4,+8`; this package does not prove the memory ranges, arrays, `C` record, callback words, or the selected `libpackbus` instance are constructed together in a running system. Constructor reachability, runtime relocation/provider selection, and the identity of `T` and `C` remain **OFFEN**.

## Six cyclic positions and separate `+0x58` context

The getter candidate cells and body addends are source-bound as numeric relocation facts: `+0x30→0x2f98`, `+0x3c→0x2e5c`, `+0x40→0x2e04`, `+0x44→0x2dac`, `+0x50→0x2c70`, and `+0x54→0x2c18`. The local bodies read the following fields relative to current `C`:

| Getter position | Local body reads | WP311 numeric callback position/name | Local path |
|---|---:|---|---|
| `+0x30` | `C+0x2c` | `+0x2c`, `libpackbus_WriteStart` | Nonzero word: tail `BX`; zero: local return 1 |
| `+0x3c` | `C+0x20` | `+0x20`, `libpackbus_WriteBytes` | Null check, then unsigned size gate, then tail `BX` or local return |
| `+0x40` | `C+0x30` | `+0x30`, `libpackbus_WriteEnd` | Nonzero word: tail `BX`; zero: local return 1 |
| `+0x44` | `C+0x24` | `+0x24`, `libpackbus_ReadStart` | Nonzero word: tail `BX`; zero: local return 1 |
| `+0x50` | `C+0x18` | `+0x18`, `libpackbus_ReadBytes` | Null check, then unsigned size gate, then tail `BX` or local return |
| `+0x54` | `C+0x28` | `+0x28`, `libpackbus_ReadEnd` | Nonzero word: tail `BX`; zero: local return 1 |

These are numeric provider-cell and local-body relationships. The names are exact dynamic-symbol/relocation names, not prototypes or callback behavior. The six position matches are conditional on the same record being published and reached at runtime.

The separate getter `+0x58` candidate `0x2ba8` reads `C+0x3c`; the stipulated target address comes from the exact `libpackbus_DiagGetDeviceState` GOT symbol. WP291's other `+0x58` record is a **separate list-entry caller context**. Its summarized entry registers are retained only as a conditional shape (`r0` from a list entry, `r1=r2=0`, `r3=caller SP+0x24`); they are not equated to the getter object, a shared allocation, or this method's runtime inputs. For the numeric synthetic route, the list-key value is set to 7 solely to reuse the bounded WP314 lookup model.

## Source execution, registers, and sized gates

`source-words.tsv` contains 451 bounded words: the seven assigned libdal method bodies, exact helper `0x2180`, both WP314 wrappers and lookup PLT, and the retained GLib lookup/hash/equality/selected arithmetic route. All executed PCs are checked against that ledger and exact ELF bytes. The local `0x2180` literal at ELF `0x2190` is data, not a fifth instruction; its `0x12054` word and the two wrapper literals produce the same Dal-relative table-global address `0x141e0` using their encoded A32 PC values.

The current DAL helper path does not rely on an opaque-helper GP preservation premise. The stepper executes each helper and nested GLib word on every method route, so the method's actual r4-r11 state at each post-call gate and tail is read from the resulting instruction trace. In these two fixtures the source saves/restores produce the recorded entry/tail states. That is a fact about these executed bytes and stipulated maps, not an ABI assertion or a claim about other callees.

For the two sized bodies, current `r5=0x100`, `r6=0x40`, and `r7=0x35000000` are captured from method-entry registers/stack. The full helper/GLib execution leaves those current values intact on the traced route, which is confirmed at each body’s post-helper compare and tail. `C+8=0x2ee0` for the write-side `+0x3c` body; `C+4=0x2ee0` for the read-side `+0x50` body. Each accepts the exact selected source gate and tails with `(r0,r1,r2)=(0x100,0x40,0x35000000)`. The gate computes `s=(r5+r6) mod 2^32` and `m=max_unsigned(r5,r6)` and rejects when `m>s` or `length<s`; it does not use `r7`. This follows the WP276 correction and the raw body words.

On simple-body traces, `r0=C` and `r3` is the exact callback pointer at the final `BX`; the source-derived current `r1/r2` values are recorded in `tail-boundaries.tsv` (for this fixture, the second helper's stack key address and the bucket address). These are scratch-state snapshots at the source boundary, not API arguments or a calling-convention claim. The `+0x58` trace records the then-current `r5/r7/r6` tail words after the same executed helpers.

## Backend target words and tail snapshots

`backend-symbols.tsv` records the exact dynamic-symbol values and sizes from the pinned private `libpackbus.so.1.0.1`; `backend-got-values.tsv` joins the WP311 `R_ARM_GLOB_DAT` relocation slots and numeric record offsets to those source-derived values. Fixture GOT words and `C` callback fields are stipulated as `BackendBias + st_value`. This gives the exact callback pointer values in each synthetic trace, but it does not prove that a loader applied a relocation or that the runtime wrote these fields.

The two fixtures use Dal/GLib/backend biases `(0x60000000,0x61000000,0x62000000)` and `(0x68000000,0x69000000,0x6a000000)`. All fourteen primary paths restore entry SP and entry LR before the tail transfer. The full `r0-r14` tail snapshot and target pointer are in `tail-boundaries.tsv`; `trace.tsv` includes before/after registers and flags at every word. The final instruction is the pinned `BX r3` word `0xe12fff13`; its recorded effect is `TAIL_TRANSFER`, and the next PC is the stipulated backend pointer. The backend body is not in the executed PC set.

## Finite controls

`controls.tsv` and the complete control traces exercise these source paths:

- A zero callback word returns local value 1 without a backend transfer.
- `[T+0x170]=0` makes helper `0x2194` return zero and the provider method takes its `0xffffffff` early-return path.
- `[DalBias+0x14208]=0` makes helper `0x2180` return zero and the first provider gate returns `0xffffffff`.
- Both sized methods reject a length one below `0x140` and accept equality at `0x140` for `r5=0x100,r6=0x40`.
- Both sized callback-null cases return 1 before loading the length word.
- The sized write case with current `r5=0xfffffff0,r6=0x40` takes the encoded unsigned rejection route after 32-bit wrap.

These are bounded source witnesses for the listed initial words, branches, and frame mappings; they do not establish general callback semantics, transfer behavior, or arbitrary range safety.

## Evidence boundary and validation

| Claim | Status | Limit |
|---|---|---|
| Exact local source words, literal arithmetic, direct calls, branch/return/tail words | VERIFIZIERT | Pinned artifacts and bounded ranges only |
| Fourteen composed paths to their local callback tail | VERIFIZIERT | Conditional on the two explicitly mapped memory/binding fixtures |
| Sized gate uses current r5/r6, length word, and excludes r7 | VERIFIZIERT | Exact traced source route; no public signature inference |
| Getter-cell to backend record identity/publication | HYPOTHESE | Numerical position and callback-symbol matching only |
| Separate getter `+0x58` versus E225 list-entry `+0x58` identity | OFFEN | Contexts remain distinct |
| Constructor/allocator/table population/runtime GLOB_DAT winner | OFFEN | Not established by static source or synthetic memory |
| Backend callback effects, return values, runtime ABI, or physical I/O | OFFEN | Execution stops before the callback; no ABI used |

Read-only source-word, dynamic-symbol, trace, memory-effect, frame, and control checks are in `validate.py`. Expected validation: **PASS**. Native code, runtime, VM, network, device, and physical tests: **NOT_RUN**.
