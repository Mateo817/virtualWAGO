> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-275 — independent conditional BSS-position overwrite audit

## Finding

**VERIFIZIERT (source arithmetic and interval check):** The three provider words are at offsets `+0x30`, `+0x3c`, and `+0x40` from provider getter result ELF address `0x14154`, at source cells `0x14184`, `0x14190`, and `0x14194`. The exact provider ELF cells contain raw addends `0x2f98`, `0x2e5c`, and `0x2e04`, and each has one `R_ARM_RELATIVE` relocation with symbol index zero. Under the usual relative-relocation calculation, the candidate runtime cell values are `P+0x2f98`, `P+0x2e5c`, and `P+0x2e04`; `P` is the provider load bias, which is not observed.

**VERIFIZIERT (conditional interval result):** Under the explicit route and register conditions below, the Dal call-boundary arguments are `(r0=D, r1=P+0x14154, r2=0x88)`, with `D=DalBias+0x1a270`. If the call reads/copies exactly 136 bytes from that provider object range to `[D,D+0x88)`, the three positions above are included. Independently decoded post-call source stores leave all three intervals untouched when current `r5=DalBias+0x193c4` and current post-call `r6=DalBias+0x1a2c4` before the local `ADD #0x24`. The vector store is then `[D+0x78,D+0x88)`; the fixed `r5` stores independently land at offsets `+0,+4,+0x10,+0x14,+0x6c,+0x88,+0x8c,+0x94,+0x98`. Neither the vector interval under its `r6` condition nor the scalar intervals under their `r5` condition intersects `[+0x30,+0x34)`, `[+0x3c,+0x40)`, or `[+0x40,+0x44)`. The stores at `+0x88` and later are outside the copied half-open interval; there is no store at `+0x90` in the complete assigned body.

This is an independent byte/interval audit of the pinned source windows. It does not establish that the copy occurs, that copied bytes carry relocated values, that a runtime BSS location exists, or that the output has an interface meaning.

## Exact route and premises

**VERIFIZIERT (source facts):** Dal `ComponentEntry` body ELF `[0x4448,0x4624)` is 476 bytes; its adjacent pool `[0x4624,0x4678)` is 84 bytes. WP272's retained complete REA and witness inventory bind all 119 body words and 21 pool words to the exact Dal ELF; this audit rechecks the bytes. The initial base literal at `0x4650` is `0x11e80`; the instruction at `0x453c` uses A32 PC `0x4544`, deriving Dal-relative `G=0x163c4`, and `0x4540` gives Dal-relative `r5=G+0x3000=0x193c4`. At `0x45b0..0x45b4`, `r0` is formed from the pre-`0x45b8` value `R6old` as `R6old+0x3eac`; `r1=current r0`, and `r2=136`. Instruction `0x45b8` then updates `r6=R6old+0x3f00` before the `0x45bc` call.

**VERIFIZIERT (stipulated getter route only):** WP273's bounded route requires Dal GOT slot `0x16030` to contain the exact provider getter target. Its local PLT/getter sequence yields `r0=ProviderBias+0x14154` and has explicit instruction writes only to the listed scratch/result/control registers; no ABI rule is used. This route preserves `r5`/`r6` through those local instructions, but the exact runtime binding and load biases remain **HYPOTHESE**. The earlier optional `BLX r2` at `0x452c` occurs before the body reloads `r6` from its literal at `0x4534`, rebuilds `r6` at `0x453c`, and derives `r5` at `0x4540`; therefore this earlier call is not a preservation requirement for those later `r5`/`r6` formulas. It can affect the current `r4` source pointer copied to `r12` at `0x4530`, source bytes, and pre-copy state; those must satisfy the explicit source/memory premises. The exact register relations required at the getter and copy boundaries are stated below and are not inferred from a function name or convention.

To claim the three conditional values at `D+offset`, all of these additional premises are required: the selected provider's three relative relocations have been applied with bias `P`; source cells at `[P+0x14154,P+0x141dc)` are readable and contain the resulting words when copied; the Dal call at `0x45bc` performs the exact 136-byte source-to-destination byte copy; source and destination ranges do not overlap; destination `[D,D+0x88)` is writable; and preceding stores/calls do not corrupt the source bytes before the copy. At the getter setup, the pre-`0x45b8` `r6` value must be `DalBias+0x163c4` so `r0` is set to `D`; the exact getter route must leave that `r6` and the previously derived `r5` unchanged through `0x45b8`. Instruction `0x45b8` then changes `r6` to `DalBias+0x1a2c4` before the `0x45bc` BL. Thus at the call boundary `r0=pre-0x45b8 r6+0x3eac`, equivalently `r0=current call-boundary r6-0x54`; it is not `current call-boundary r6+0x3eac`. After the opaque call, current `r5` must equal `DalBias+0x193c4` for the tabulated scalar stores, and current `r6` (`Q`) before `0x45c4` must equal `DalBias+0x1a2c4` for the vector interval. The local `0x45c4` add is included in that vector address. `r4`, `r7`, and `d8/d9` affect values written elsewhere or vector data, but under those address conditions do not change the three-position overlap result.

**WP272 prose erratum (independent review):** WP272's phrase “at the imported call `0x45bc` ... `r0=current r6+0x3eac`” is temporally misleading if `current r6` means the register at the call boundary. The raw order has `r0` formed from the pre-`0x45b8` value, then `r6` is incremented by `0x3f00`. The correct call-boundary equality is `r0=call-boundary r6-0x54`. This audit used the corrected ordering and does not edit WP272.

The complete body has three call boundaries: the optional `BLX r2` at `0x452c`, getter `BL` at `0x45a4`, and the `0x45bc` imported-call boundary. The post-call interval audit covers every direct word store and the 16-byte vector store through the epilogue. It stops at the body end and does not inspect callee bodies. The pre-getter 60-byte staging write uses current `r4` and current `r5`; its conditional baseline range ends exactly at `D`, but the earlier callback/register/source effects remain open.

## Conditional positions

| Candidate byte interval | Provider source cell | Conditional copied word | Baseline post-store overlap | Status |
|---|---|---|---|---|
| `[D+0x30,D+0x34)` | `P+0x14184` | `P+0x2f98` | none | **HYPOTHESE**: copy, binding, relocation, memory, and current-register premises |
| `[D+0x3c,D+0x40)` | `P+0x14190` | `P+0x2e5c` | none | **HYPOTHESE**: copy, binding, relocation, memory, and current-register premises |
| `[D+0x40,D+0x44)` | `P+0x14194` | `P+0x2e04` | none | **HYPOTHESE**: copy, binding, relocation, memory, and current-register premises |

`D` is the candidate Dal destination, `DalBias+0x1a270`; `P` is the separate provider bias. These are not observed runtime addresses or interface fields.

## Counterexamples and context

**VERIFIZIERT (counterexamples to unconditional preservation):** With synthetic `DalBias=0x70000000`, a changed current post-copy `r6= D+0x0c` makes the local `ADD #0x24` place the 16-byte vector store at `[D+0x30,D+0x40)`, overwriting the first two positions. A changed current post-copy `r5=D+0x40-0xeb0` makes the instruction at `0x45ec` store directly at `D+0x40`. These are arithmetic counterexamples, not claims about real call clobbers; no ABI preservation is assumed.

Hash-bound legacy summaries are context only: WP209 says its bounded IoDrvKbus path reaches a first `[r7+4]` load after a local null-return route; WP213 leaves an older store/scan alias question open; WP214 says the Dal ELF metadata does not require eager binding and a lazy first resolution remains statically possible. They do not establish that these three cells are consumed by that caller, and no caller body is newly interpreted here.

## Limits and validation

**OFFEN:** actual loader/provider selection and GOT contents; load biases; runtime relocation and copy execution; copy implementation and effects; input callback effects; runtime memory mapping, aliasing, and final cell contents; identity or semantics of any structure/API. No C layout, prototype, or meaning is inferred from names or offsets. No target was executed and no VM, device, network, or public repository was used.

**PASS:** `validate.py` is read-only by default. It verifies both source identities, pinned upstream packages/summaries, WP272 byte coverage, provider RELATIVE cells, all 10 post-call stores, all three protected intervals, counterexamples, generated tables, and a self-reference-free manifest.
