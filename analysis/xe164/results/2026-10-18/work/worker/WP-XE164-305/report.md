> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-305 — bounded nested arithmetic replay for 77 / 7

**VERIFIZIERT** — Against the exact GLib candidate SHA-256 `3f927b8aae0e3e1b1296bde9009ba9fb9380f64ac26ebe8b7675638e3250cbc5`, all 123 nested-body instruction words from Ghidra `0xcaa78..0xcac63` agree with ELF bytes at `ELF VA = Ghidra VA - 0x10000`. The complete selected body coverage and the eight-word caller slice `FUN_000cac64` are source-pinned in `source-words.tsv`; complete WP294 REA and assembly evidence is hash-pinned in `source-pins.tsv`.

## Selected path and resulting values

The nested entry state is stipulated as `r0=77`, `r1=7`. The initial flags do not matter because the first instruction is `SUBS r2,r1,#1`: it produces `r2=6`, `N=0,Z=0,C=1,V=0`. `BXEQ LR` is not taken, `BCC` is not taken, and `CMP r0,r1` sets C. `BLS` is therefore not taken. `TST r1,r2` yields `7 & 6 = 6`, sets `Z=0` while preserving C/V, and `BEQ` is not taken.

`CLZ(77)=25` and `CLZ(7)=29`, so the next values are `r3=29-25=4`, then `r3=31-4=27` after `RSBS`, and `r3=27+(27<<1)=81` after the conditional non-flag-setting add. `r2` is cleared to zero. At Ghidra `0xcaaac`, `ADDNE pc,pc,r3,LSL#2` uses the A32 current-instruction PC value `0xcaaac+8`; the resulting target is `0xcaaac+8+(81*4)=0xcabf8`. That target is inside the pinned body and is the compare step for `r1<<4`. No general computed-PC table or target outside the exact route is inferred.

The selected compare/ADC/conditional-subtract tail visits every shift from 4 down to 0. The compare at shift 4 finds `77 < 112`, so C=0 and that quotient bit stays clear. At shift 3, `77 >= 56`, so `r2` becomes 1 and `r0` becomes 21. Shift 2 finds `21 < 28`, leaving `r2=2,r0=21`. Shift 1 finds `21 >= 14`, producing `r2=5,r0=7`. Shift 0 compares equal (`7 == 7`), setting `Z=1,C=1`; ADC makes `r2=11`, and conditional subtraction makes `r0=0`. The final `MOV r0,r2` gives `r0=11`; the immediately following `BX LR` returns to `0xcac74`. This derives a value on this path from the exact instructions; it does not assert quotient semantics for all inputs.

**VERIFIZIERT** — The adjacent eight-word `FUN_000cac64` source slice, under caller entry `r0=77,r1=7`, does not take its zero-input branch. It pushes those two values and LR in 12 bytes, BLs to the nested body, then `LDMIA sp!,{r1,r2,lr}` restores saved `r0` into `r1=77`, saved divisor into `r2=7`, and the original LR while restoring SP. With nested `r0=11`, `MUL r3,r2,r0` yields 77 modulo 2^32 and `SUB r1,r1,r3` yields `r1=0`. At caller `BX LR`, nested-output `r0=11` remains and caller LR is restored. Two fixtures at distinct stack/LR values produce the same arithmetic state while restoring their own stack and return values.

## Effects and controls

`trace.tsv` records pre/post registers and NZCV for each selected nested instruction, plus caller events; both fixtures’ computed and branch destinations are checked against the exact word map. In this route, the nested body performs no data-memory reads or writes, and does not modify `r4-r11`, SP, or LR; its normal return uses the incoming LR. The stepper seeds `r4-r11` with distinct sentinels and checks they remain unchanged. The caller slice writes three stack words for saved `r0`, `r1`, and LR, then reads those same words on restore. It restores SP/LR but intentionally returns the nested value in r0 and computes the separate index in r1. These are source-path effects under the stipulated mapped, non-aliasing synthetic stack and normal-return premises, not ABI facts.

The `r1=1` control takes the two-instruction `BXEQ LR` path and returns original r0; it does not reach the selected 77/7 route. The `r1=0` control branches to `0xcac58`, which is inside the nested body's overall range but outside the selected nonzero route and outside the adjacent eight-word caller slice. This package stops at that boundary and makes no zero-handler claim. A changed numerator `84/7` exercises the same source map with a distinct result. An injected computed target outside the audited map is rejected. No native ELF execution is performed.

WP304’s retained constructor/initializer evidence adds a useful boundary check: the observed initializer at `0x54fb4` stores numeric words `+0=8`, `+4=7`, `+8=7` in the passed base and then calls opaque allocators. Thus WP300’s stipulated divisor word `+4=1` is not produced by this initializer; that does not invalidate its explicitly synthetic fixture, but confirms it is not established as constructor-reachable. Neither constructor metadata nor this replay establishes actual table layout, API semantics, runtime binding, or an ABI.

## Claim matrix

| Claim | Status | Bound |
|---|---|---|
| Selected source words, 123-word nested coverage, and eight caller words match pinned ELF bytes | VERIFIZIERT | Exact provider hash and retained WP294 REA inputs |
| Nested `r0=77,r1=7` selected path returns `r0=11` at normal `BX LR` | VERIFIZIERT | Source-whitelist replay; all PCs remain in 123-word body |
| Caller computes `r1=77-(7*11)=0`, preserves `r0=11`, restores caller SP/LR | VERIFIZIERT | Exact eight-word slice and two explicit synthetic frames |
| General quotient/division semantics, arbitrary divisor route closure, out-of-body handlers | OFFEN | Not claimed or expanded |
| Constructor-produced WP300 divisor-1 fixture/live table binding/runtime lookup | OFFEN | WP304 initializer stores +4=7; allocator semantics and runtime state not established |
| Actual constructor reachability, runtime binding/provider selection, ABI behavior, memory faults, concurrency | OFFEN | Outside source evidence and synthetic replay |
| Native ELF execution and target/runtime tests | NOT_RUN | Not part of this static task |

## Validation

Run `python3 validate.py` from this directory. Result: **PASS** for source pins, source-byte mapping, bounded path, flags, computed target, caller save/restore, second frame, and controls. **NOT_RUN** for native execution/runtime and all ABI/device behavior. `results.json` and `trace.tsv` are generated by the read-only validator from the pinned source-word table.
