> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-276 — independent review of WP274

## Result

WP274's reported body bounds are consistent with the exact source ranges; its retained REA IDs establish procedure/body coverage, and this review independently rechecks all 85 instruction words and bytes. The direct call destinations, local return constants, callback loads, and conditional register-flow conclusions agree with the source. The review found one factual overstatement in its range-gate prose: **the `+0x3c` body's unsigned gate does not use `r7`**. It compares current `r5` and `r6`, their wrapped 32-bit sum, and a word loaded through current `r0+8`. The body reads `r7` only after the gate passes, when it copies current `r7` to transfer argument register `r2`.

WP274's validator is not generally tautological: it pins the exact source, checks all 85 instruction words, branch targets, relocation cells, and tests distinct gate outcomes. Its high-level call models do not independently exercise register mutation across opaque calls, however. The added WP276 synthetic call-state traces check that subsequent call inputs and the eventual range/transfer values are the then-current registers. They do not imply anything about real callee effects.

## Exact body and call review

The exact provider ELF is 18,076 bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. WP274 retained procedure-info and full-function REA IDs for the three unique, nonoverlapping contiguous bodies. This package rechecks every byte/word in the 85-row witness against the ELF:

- ELF `[0x2e04,0x2e5c)`, 88 bytes; candidate Ghidra entry `0x12e04`.
- ELF `[0x2e5c,0x2f00)`, 164 bytes; candidate Ghidra entry `0x12e5c`.
- ELF `[0x2f98,0x2ff0)`, 88 bytes; candidate Ghidra entry `0x12f98`.

The body instructions contain nine direct `BL` instructions, three per body, plus thirteen conditional local branches. All calls branch directly to numeric addresses `0x2180`, `0x2194`, and `0x1ecc` inside this ELF's executable `.text`; none is a PLT call. Those helper bodies are out of scope. No indirect call occurs until the final `BX r3`, and no call contract is inferred from target names or ABI convention.

For the `+0x30` and `+0x40` candidates, the body checks each post-call current `r0` for zero. Before calls two and three it executes `MOV r0,r4`; `r4` is not locally restored from entry state between calls. Thus those call inputs are then-current `r4`, which opaque calls can change. If any tested return is zero, the body locally returns `0xffffffff`. After three nonzero returns, it reads the callback word at current `r0+0x2c` (`+0x30` candidate) or current `r0+0x30` (`+0x40`). A zero word returns `1`; a nonzero word becomes `r3`, and the body restores its local save area and executes `BX r3`. At that transfer, `r0` remains the current nonzero third-call return. `r1` and `r2` have no local reaching definitions after opaque calls, so their values remain unclassified.

The `+0x3c` body has the same three nonzero call-return gates and current-`r4` setup before calls two and three. After the last call it loads a word from current `r0+0x20`; zero returns `1`. It then loads the length candidate from current `r0+8`. Its actual comparison sequence is unsigned:

`sum = (current_r5 + current_r6) mod 2^32`

`max = max_unsigned(current_r5, current_r6)`

The body rejects when `max > sum` or `length < sum`; it transfers only when `max <= sum` and `length >= sum`. It does not read `r7` in these comparisons. On success it copies current `r7` to outgoing `r2`, current `r6` to `r1`, current `r5` to `r0`, and the previously loaded callback word to `r3`, restores saved registers, then executes `BX r3`. The current values of `r5/r6/r7` after opaque helpers are used; none is assumed equal to the entry `r2/r3/stack word` initially copied in the prologue.

There is no copy loop, explicit copy instruction, named length parameter, 8-byte pair operation, or queue processing in these three bodies. The `+0x3c` body has an arithmetic length/range check, but no source establishes that the checked words represent a byte count or a physical I/O transfer. This finding is limited to the three bounded bodies; opaque callees may have other effects.

## Table-position join and limits

The pinned WP273 report and WP274's source check bind the provider-relative cells `+0x30`, `+0x3c`, and `+0x40` to REL addends `0x2f98`, `0x2e5c`, and `0x2e04`. The local target bodies are source-verified candidates. Relocation at load, provider identity, table identity, publication/copy path, and runtime selection remain unverified. The accepted WP183/WP209/WP224 reports are used only as hash-pinned conditional context; no caller body was expanded here.

The three WP274 REA IDs and raw witness rows are pinned in this package. The current REA bundle lookup returned no retained record matching the target SHA, so this review uses the WP274-retained report/IDs and checks its full raw instruction witness directly against the pinned ELF; it did not issue fresh REA body queries. The requested STOP-QUOTA.json was absent at its specified path when checked. No VM, device, runtime, network, native execution, or public-repository action occurred. This package is an independent static review, not a new REA run.

## Verification

`python3 validate_review.py` passes. It independently checks the exact file identity, every byte and word in all three bodies, all 22 branch targets and the 13 conditional branch conditions, the nine direct call sites, table-cell addends and unique `R_ARM_RELATIVE` records, the executable-section bounds, return/transfer anchor words, and synthetic state-transition counterprobes for helper clobbers, null slots, each zero-return gate, unsigned high-bit and wrap cases, equality boundaries, and `r7` variation.

Status: bounded source mechanics **VERIFIZIERT**; `r7`'s nonparticipation in the gate **VERIFIZIERT**; table publication and runtime target behavior **OFFEN**; opaque helper effects, ABI, callback semantics, source-level interface identity, and physical I/O **OFFEN**. Tests are synthetic arithmetic/control-flow checks only; native execution is **NOT_RUN**.
