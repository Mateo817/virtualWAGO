> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-273 — conditional resolved-getter path and provider cells

## Result

**VERIFIZIERT (source words and local arithmetic):** The pinned Dal instruction at ELF VA `0x45a4` calls its PLT entry at `0x9d4`. On the specifically stipulated route where Dal GOT slot `0x16030` contains the selected provider address `P+0x3464`, the three PLT instructions transfer control to the exact three-instruction getter body at `P+0x3464`. That body returns `P+0x14154` in `r0`, using literal `0x10ce4` at ELF VA `0x3470`. The Dal caller then reaches its next call boundary at `0x45bc` with `r0=G+0x1a270`, `r1=P+0x14154`, and `r2=136` for the given initial `r6=G+0x163c4` and `r5=r6+0x3000`. Here `G` and `P` are separate Dal and provider load biases.

The sequence preserves `r5`, `r7`, `d8`, `d9`, `SP`, and `F` across these listed caller, PLT, and getter instructions based only on their explicit operands. This makes no ABI or opaque-target claim. The caller instruction at `0x45b8` changes `r6` from its pre-instruction value `G+0x163c4` to `G+0x1a2c4`; both values are recorded separately. The `0x45bc` BL itself is the next call boundary and writes LR when executed. The target body is outside scope.

**VERIFIZIERT (provider data/relocation source):** Provider ELF cells `0x14184`, `0x14190`, and `0x14194` contain raw REL addends `0x2f98`, `0x2e5c`, and `0x2e04`. Each cell has a unique `R_ARM_RELATIVE` record. Each addend falls within the provider's file-backed executable `.text` section metadata. Under the usual relative-relocation arithmetic, the conditional post-relocation words are `P+0x2f98`, `P+0x2e5c`, and `P+0x2e04`. No target instruction/body, symbol name, function identity, API, or ABI is inferred from these address values. These are source facts that may help position an interface-source analysis; they do not establish the cells' runtime use or meaning.

## Scope and source binding

This report is limited to Dal ELF VAs `[0x45a4,0x45c0)`, PLT `[0x9d4,0x9e0)`, provider getter `[0x3464,0x3470)` and its four-byte literal at `0x3470`, plus the three provider cells and their relocation/section metadata. The assigned source SHA-256 values and sizes are in `source-pins.tsv`. `WP-XE164-202` supplies the retained hash-bound getter REA finding and correct Ghidra mapping (`Ghidra VA = ELF VA + 0x10000`); WP-XE164-206 supplies the static import/export and JUMP_SLOT context, not a runtime resolution result. WP-XE164-144/249 and root WP-XE164-211 are used only as hash-bound positional/entry context summaries. No WP272 output is used or pinned.

| Artifact | Exact range/value | Finding |
|---|---|---|
| Dal caller | `0x45a4..0x45bc` | `BL 0x9d4`; copy size 136; result to `r1`; destination from old `r6+0x3eac`; then `r6=old_r6+0x3f00`; BL to `0x9c8` boundary |
| Dal PLT | `0x9d4..0x9dc` | Adds to form GOT address `0x16030`, then preindexed load to PC |
| Provider getter | `0x3464..0x346c` | Loads literal, adds PC, branches through LR; local returned ELF-relative VA is `0x14154` |
| Provider literal | `0x3470` | Word `0x10ce4`; not an executed fourth instruction |
| Provider cells | `0x14184/0x14190/0x14194` | Raw REL addends and `R_ARM_RELATIVE` relocations; executable-section membership only |

The PLT address chain is: at `0x9d4`, A32 PC is `0x9dc`, so the first add forms `r12=0x9dc`; the second forms `0x159dc`; the final preindexed load uses `0x159dc+0x654=0x16030`, writes that effective address back to `r12`, and loads PC from the slot. The exact selected route therefore depends on the explicit stipulation that the slot contains `P+0x3464`. The loader's selection, lazy-resolution path, and actual slot contents are not verified here. A fixed negative validator case with a different GOT value is rejected as outside this route.

The getter computes `P+0x14154`: the LDR at `0x3464` uses architectural PC `0x346c` plus 4 to read `0x3470`; the ADD at `0x3468` uses PC `0x3470` and adds `0x10ce4`; `BX LR` returns with that result in `r0`. The mapped Ghidra addresses in WP202 are `0x13464..0x13470`, not ELF VAs; the source addresses in this report remain ELF VAs.

For the caller arithmetic, before instruction `0x45b8` let `R6=G+0x163c4`. The destination setup is `R6+0x3e80+0x2c=G+0x1a270`; the getter result is copied to `r1`; and the size is `136`. Instruction `0x45b8` separately updates `r6` to `G+0x163c4+0x3f00=G+0x1a2c4`. Given `r5=R6+0x3000`, its value is `G+0x193c4` and remains unchanged through the scoped sequence.

## Explicit register effects and limits

Within the caller sequence before the `0x45bc` BL executes, the explicit destination writes are `r0`, `r1`, `r2`, `r6`, and LR at the `0x45a4` BL. The PLT explicitly writes `r12` and PC; the getter explicitly writes `r0` and PC (return). Their instructions do not name `r5`, `r7`, `d8`, `d9`, SP, or F as destinations. No ABI is used to extend the proof. The result does not cover dynamic resolver code, any nonmatching GOT destination, execution after the next BL, or the behavior of the target at `0x9c8`.

The `0x45bc` destination is a `memcpy` PLT boundary by its local branch target only. The report stops before that call's implementation and claims neither copy semantics nor preservation across it. Likewise, this static route is conditional and does not establish that any source instruction executes at runtime.

## Validation

`validate.py` reads the two pinned ELFs only. It checks identity, exact instruction words, decoded caller branch targets, PLT/GOT and getter/literal address derivations, provider REL records and raw addends, and executable file-backed target-section metadata. Three synthetic bias pairs reconstruct the call arguments and check unchanged sentinel values for `r5`, `r7`, `d8`, `d9`, SP, and F while requiring the expected before/after `r6` change. A negative case supplies a nonmatching GOT target and rejects the exact-route conclusion. These are mathematical source-derived cases, not runtime observations.

Tests: validator **PASS**. Runtime/device/VM/network: **NOT_RUN**. Static route conditional on stipulated GOT contents; actual runtime binding and cell usage remain **OFFEN**. This is a self-review, not an independent review.
