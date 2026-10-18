> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-301 — bounded LoadSymbol call and callback gates

## Finding

**VERIFIZIERT (source-local):** In the pinned `libdal.so.1.0.1` source body, the direct call at ELF `0x224c` branches to PLT entry `0x13f0`, labeled `LibraryLoader_LoadSymbol` by the accepted WP205 instruction map. The pinned thunk words at `0x13f0..0x13f8` compute its JUMP_SLOT address `0x14040`, which `readelf -rW` names `LibraryLoader_LoadSymbol` (see `plt-binding.tsv`). This call is reached only on the prior local branch where the `LibraryLoader_LibraryOpen` return at `0x2238` is not `0xffffffff`; equality branches to `0x2388`. Immediately before it, the local register expressions are `r0=[current r6+0x104]`, `r1=current r4`, and `r2=current fp-32`. At the next instruction, the body reads `r3=[current fp-32]`. This is an address/dataflow relationship; the source does not prove that the opaque call writes that output word or that `fp` remains unchanged across it.

**VERIFIZIERT (source-local):** The code compares the current LoadSymbol return `r0` against `0xffffffff` using `cmn r0,#1`. If equal, the branch at `0x2258` goes to `0x2388` and skips the first indirect call and the following byte store. If not equal, execution reaches `blx r3` at `0x226c` with current `r0=current r6+0x110`, current `r1=0x141e8`, and `r3` the word read at `[current fp-32]`. No null test of `r3` appears on this path. No success/error meaning is assigned to the `-1` comparison.

**VERIFIZIERT (source-local):** After that indirect call returns, the body sets `r8` from its current `r0`, sets `r3=1` only when that return is zero and `r3=0` otherwise, then stores one byte at `[current r6+0x170]`. A nonzero first-callback return branches to `0x2388`. On the zero-return fallthrough, the separate slot `[current r6+0x158]` is loaded at `0x2284`; zero branches to `0x2368`, while nonzero reaches a distinct `blx r3` at `0x2290`. On this second-call path, current `r0` remains zero through the intervening local load/compare instructions. The second callback target is therefore a separate source-loaded word at `r6+0x158`, not the word read from the LoadSymbol output at `fp-32`.

## Source-derived symbol suffix

At `0x2210`, the code loads a PC-relative word from ELF `0x2390`; raw value `0x1b24` is added to architectural PC `0x221c`, yielding source address `0x3d40`. The bytes at `0x3d40` are exactly `_open\0` within the file-backed `PT_LOAD` and `.rodata` range. The code then computes `r1=current r4+current r0`, copies that current length to `r3`, loads a word and halfword from the suffix bytes, and stores them at `[current r4+r3]` and `[current r1+4]`. Thus the visible local store sequence appends the six source bytes `_open\0` at the address expression derived from the current `r4` and the current return from the preceding call at `0x220c`.

Earlier, the body initializes byte `[current sp+8]` to zero, passes current `r4` and current `r6` as `r0/r1` to PLT `0x160c` (relocation label `strcat`), then passes current `r4` as `r0` to PLT `0x14f8` (relocation label `strlen`). The labels do not prove their implementations or API contracts. Under conventional behavior for those names, if calls preserve the relevant state and buffer contents, the candidate text would be the incoming string followed by `_open`; that complete string is **HYPOTHESE**, not a source-proven call result. In particular, `LibraryLoader_LibraryOpen` is called at `0x2234` between the suffix stores and the later `LoadSymbol` call, and its effects on registers and memory are opaque. The LoadSymbol boundary is therefore reported as receiving current `r4`, not as receiving a proven immutable string value.

## Direct-PC values and data domains

`direct-pc-data.tsv` records the three nearby literal uses. Pool word `0x2390` yields the source suffix address `0x3d40`. Pool word `0x2394` is `0x11f74`; the ADD at `0x2264` uses architectural PC `0x226c`, yielding ELF-domain address `0x141e0`, and the following ADD makes ELF-domain `r1=0x141e8`. At runtime, under a same-image load bias B, these PC-relative expressions yield `B+0x141e0` and `B+0x141e8`. Pool word `0x2398` is `0x11f28`; the ADD at `0x22b0` uses architectural PC `0x22b8` and also yields ELF-domain `0x141e0` (runtime `B+0x141e0`). The latter values fall in the source ELF's memory-only `.bss` tail, not in source file bytes, so no static string scan or current runtime value is asserted for those addresses.

The earlier WP299 producer evidence says a word `0x7c8` is stored at `[current r5+0x110]`. The present callback argument is `[current r6+0x110]` as an address, with `r6` as the current base at `0x2260`. The bases and operations differ; this package does not equate them, infer a callback field at either offset, or claim the producer value is passed as the callback argument.

## Preservation conditions and limits

The inspected source body copies function-entry `r0` into `r6` at `0x21dc`, but it uses current `r6` again after opaque calls at `0x21e0`, `0x2204`, `0x220c`, and `0x2234`. Equating later `[r6+...]` expressions with entry-r0-relative addresses requires each relevant opaque call to preserve `r6`; no ABI rule is assumed. Likewise, `r4` is computed as current `sp+8` and reused after opaque calls; `fp-32` is passed before LoadSymbol and read after it, with address identity conditional on `fp` preservation. The loaded word at that output location is not proven initialized, and `r3` has no local null gate before `blx r3`.

The second indirect target at `[current r6+0x158]` is independently null-checked. Its incoming `r0` is zero on the local fallthrough from the first callback's zero-return gate, but `r1/r2` at the second call depend on opaque callback effects. No body is expanded. No prototype, field/type name, API/ABI contract, actual loaded binding, runtime callback population, or callback semantics is claimed.

The static producer's `current r5+0x110` word and this consumer's `current r6+0x110` argument expression remain distinct. Any relation between their bases, a loaded callback address, and the `0x7c8` word is **OFFEN**.

## Validation

The read-only validator checks all source pins, the selected instruction words against the exact ELF bytes and ELF load mapping, all three literal values and their A32 PC calculations, bounded `_open\0` bytes, the branch destinations and conditions, the exact local argument expressions, and the separate callback slots. It also checks the `LibraryLoader_LoadSymbol` relocation-name record through local `readelf -rW`. This is static source validation only. It does not execute the ELF or expand any called implementation. Static checks: **PASS**. Runtime binding, call effects, constructor reachability, callback target validity, ABI, and memory behavior: **NOT_RUN / OFFEN**.
