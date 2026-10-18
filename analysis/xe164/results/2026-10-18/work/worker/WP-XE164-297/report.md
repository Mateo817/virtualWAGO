> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-297 — independent review of WP292

## Result

**VERIFIZIERT under the stated source-bound synthetic premises, with two review qualifications.** The post-helper return remains valid despite WP292’s manual Dal composition omitting several scratch-register assignments: the exact local leaf/common words establish `r0=0`, the Dal frame restores SP and loads the saved core continuation into PC, and the core postlude returned the same result in 12 explicit pinned source-word replay variants with selected `r1/r2/r3/r12` and flag values. I found no scratch-clobber counterexample to the local return.

WP292 should explicitly list its initial core gate premises, and its reported wrong-GOT/wrong-slot controls are scalar comparisons rather than changed-memory control-flow tests. These are report/evidence defects, not a contradiction of the positive conditional route: its fixture constructor does set the missing gate values, and the accepted source route is still valid when those conditions are stated.

## Route checks

The getter PLT’s encoded immediates derive Dal `r12=G+0x159dc` and GOT slot `G+0x16030`. Under the stipulated GOT content `P+0x3464`, the three getter words calculate `r0=P+0x14154`; its LR is the caller continuation `G+0x42f8`. The provider cell at ELF `0x14158` is independently found as one symbol-zero `R_ARM_RELATIVE` record, and its raw source word is `0x1dc0`; the conditional relocated target is `P+0x1dc0`.

The exact early +4 path reads byte `P+0x14208`. With zero there, `r3` retains the computed base `P+0x141e0` and `LDRB` writes zero to `r2`; `CMP` sets Z, BNE at `0x1dd0` falls through, `MOV r0,#0` executes, and BX returns through LR `0x4300`. SP is unchanged; `r1` remains zero in this fixture. The PLT LDR-PC uses writeback, leaving `r12=G+0x16030`. This is a local register/effect statement and does not depend on an ABI.

At `0x4194`, the Dal path sets `r4=0`. The common sequence loads `r5=G+0x163c4`, reads gate `[G+0x163d0]=1` to `r6`, compares it with zero, and therefore does not take the conditional BEQ at `0x3728`. It then moves `r4` to `r0`, adds back the 188 local bytes, and loads the saved `r4-r11` and return PC from the Dal push area. Thus `r0=0`, SP returns to the core call SP, PC becomes `0x2fedd8`, and LR itself remains the leaf link value `0x4300`. The common words write `r5/r6`; they do not write `r3/r12`. The source-derived post-Dal boundary vector is `r0=0, r1=0, r2=0, r3=P+0x141e0, r12=G+0x16030, SP=0x71000fc0, LR=G+0x4300, PC=0x2fedd8`, with NZCV `0,0,1,0`; fixture `r4-r11` are `(0, HEAD, HEAD+16, 15, 0xfffffff4, 0, HEAD, 0x71000ffc)`. The full machine-readable vector is in `review-results.json`. The common block at `0x3710` is `LDR r5,[pc,#0xc2c]`, followed by `ADD r5,pc,r5`; it does not load `r3`.

Starting from the verified source-derived boundary vector, I independently replayed the pinned raw-A32 core postlude for 12 explicit combinations of `r1/r2/r3/r12` and flags, with each accepted helper halfword represented in the fixture setup. Each tested variant returns `r0=0`, restores SP to `0x71001000`, returns to `0x2ff770`, and restores core `r4-r11`. These tests begin at the postlude boundary with `r0=0`, saved frame intact, and the chosen null-callback/single-head gates. They directly test the postlude’s insensitivity to the omitted scratches; they do not infer the leaf or Dal result from that test.

The core fixture also requires the initial gate `[0x510868]=0x60000000 != 0xffffffff`, a readable manager base and word `[M+0x1c]=HEAD=0x60001000`, optional callback slot `[0x5fc5b0]=0`, readable nonzero head, and a readable object through `HEAD+0x3e`. WP292’s constructor supplies these values. Its report’s generic “valid synthetic head/object” wording should be expanded because the independent initial global gate is a separate path predicate previously identified in WP270.

For the synthetic frames, the core call SP is `0x71000fc0`; the Dal 36-byte save area is `[0x71000f9c,0x71000fc0)`, and the 188-byte local allocation places its frame base at `0x71000ee0`. The three argument spill words occupy `[0x71000f0c,0x71000f18)`, inside the Dal local allocation and outside the saved-register area. The Dal frame is adjacent to, not overlapping, the core frame `[0x71000fc0,0x71001000)`. The fixture object and manager words are at separate synthetic ranges.

## Countercontrols and report corrections

The existing byte-one narrative is correct: BNE at `0x1dd0` is taken to `0x1ddc`; with first word 1, CMP at `0x1de4` makes BEQ at `0x1de8` not taken; the path reaches the first opaque BL at `0x1df4` (target `0x13b4`). The review validator checks those raw source words and targets. Any shorthand claiming “BEQ at `0x1dd0`” is an erratum; the actual branch mnemonic is BNE.

WP292’s `wrong_got` control sets the scalar `0x16034` and compares it with `0x16030`; it does not change `[G+0x16030]` or follow the PLT’s LDR-PC. Its `wrong_slot` control compares `0x1bec` and `0x1dc0`; it does not change the relocated cell or follow Dal’s LDR/BLX. These do not substantiate a branch-level negative control. This review adds counterfactual memory contents: a GOT target `P+0x3468` enters the getter at its second instruction, where incoming selector `r0=15` yields `P+0x347f`, not the getter’s source-base value; `P+0x4000` leaves the scoped code maps. A wrong cell content `P+0x1bec` makes Dal’s encoded LDR/BLX target that different address, outside the selected `[P+0x1dc0,P+0x1ea4)` body. No alternative target body is expanded.

## Scope and limits

The review uses the exact pinned artifacts, WP255 path, WP259 mathematical A32 interpreter, and bounded WP262/WP224 source records. It does not execute an ELF or claim a loader winner, runtime mapping, C/API contract, ABI, or mandatory lifecycle phase. Wrong-binding controls stop at the actual destination transfer and do not assign behavior to unreviewed targets.

Status: synthetic local chain **VERIFIZIERT under stated premises**; initial-gate statement and two negative-control records require qualification; runtime behavior **OFFEN**. WP292 was not edited.
