> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-272 — bounded ComponentEntry-to-BSS address and call-vector analysis

## Finding

**VERIFIZIERT (bounded local source):** The exact `libIoDrvDal.so.1.0.2` `ComponentEntry` body is Ghidra `[0x14448,0x14624)` (476 bytes); the immediately following literal pool `[0x14624,0x14678)` is 84 bytes. The retained WP144 REA record has the same ELF SHA-256 and supplies the complete body and data references. This package cross-checks all 119 body instruction words and all 21 pool words against the original ELF bytes.

The local body forms these candidate addresses:

- `G = 0x263c4` Ghidra / ELF `0x163c4`, from the PC-relative add at `0x1453c`.
- `P = G + 0x3000 = 0x293c4` Ghidra / ELF `0x193c4`.
- The 60-byte register-copy sequence writes from **current `r4` at `0x14530`** to current `r5+0xe70`; if the derived `P` remains in `r5`, the candidate range is Ghidra `[0x2a234,0x2a270)` / ELF `[0x1a234,0x1a270)`. The source equals the original ComponentEntry input only if the optional `+0x28` indirect call is skipped or returns with `r4` unchanged. That call can also change the bytes later read, so the source is not treated as the entry pointer or as an immutable object.
- At `0x145a4`, the body calls the imported `adi_GetApplicationInterface`. It then sets `r1` from the getter’s current `r0`, sets `r2=0x88` (136), and computes `r0 = current r6 + 0x3e80 + 0x2c` at `0x145b0..0x145b4`. If the getter leaves `r6=G`, the numerical candidate is Ghidra `0x2a270`, ELF `0x1a270`. It then increments `r6` by `0x3f00` before the next call. After the imported call returns, instruction `0x145c4` (`e2866024`) adds another `0x24` to current `r6` before the vector store. At the imported call `0x145bc`, before its local `ADD r6,#0x24` return-path adjustment, the exact register vector is `(r0=current r6 + 0x3eac, r1=getter return, r2=0x88, r3=current post-getter r3)`. The post-call store uses current r6 after that adjustment. `call-argument-matrix.tsv` preserves the raw register values and limits.

The callsite relocation metadata identifies the two imports as `adi_GetApplicationInterface` (dynsym 14, unversioned `R_ARM_JUMP_SLOT`, GOT `0x16030`, PLT `0x9d4`) and `memcpy` (dynsym 13, `GLIBC_2.4` `R_ARM_JUMP_SLOT`, GOT `0x1602c`, PLT `0x9c8`). Only these two 12-byte PLT entries are retained. The symbol name `memcpy` is metadata; this analysis does not infer its prototype, copy semantics, return behavior, or register/memory effects from that name.

The exact getter provider remains conditional. The pinned WP202 summary states that its local three-instruction body returns ELF-relative address `0x14154` and locally writes `r0` only. WP206/207 summaries provide a matching static dependency/export candidate. If runtime binding reaches that exact body directly, its local instructions leave `r6` unchanged. Static dependency/export metadata does not establish the loaded instance, resolved PLT target, first-call lazy-resolver effects, load bias, or interposition, so `D=0x1a270` is not unconditional.

## Candidate 136-byte range and later stores

The `.bss` section is ELF `[0x16088,0x1a30c)` and is zero-fill. Candidate `[0x1a270,0x1a2f8)` (Ghidra `[0x2a270,0x2a2f8)`) lies within it. This is a **candidate** 136-byte range computed from current registers; no runtime BSS address or memory content was observed.

If the getter leaves `r6=G`, then the call’s first raw register is `0x2a270`; if the post-getter address value is also the target, and the imported implementation performs the expected data movement, the call may populate `[0x2a270,0x2a2f8)`. Those are separate premises, not a conclusion from `memcpy`’s name. `store-overlap.tsv` derives each subsequent direct store from its instruction and states the register identity needed for the candidate target:

- With current post-call `r5=P`, the local post-call stores land at candidate offsets `+0`, `+4`, `+0x10`, `+0x14`, `+0x78..+0x87` (16 bytes), and `+0x6c` inside the 136-byte range.
- The word store at `+0x88` is exactly at the half-open range’s end and therefore outside the copied 136 bytes. Stores at `+0x8c`, `+0x94`, and `+0x98` are also outside. There is no store at `+0x90` in the complete bounded body.
- The fixed PC-derived values at `+0`, `+4`, `+0x10`, `+0x14`, and `+0x6c` are derived locally from literals and A32 PC values. The vector uses **current post-add `r6`, `d8`, and `d9`**. The post-memcpy `ADD r6,r6,#0x24` at `0x145c4` means the baseline target is `G+0x3f24=0x2a2e8`, or candidate offset `+0x78` from `D=G+0x3eac`, only if the getter leaves `r6=G` and memcpy leaves the pre-call `r6=G+0x3f00` intact; the explicit local `+0x24` adjustment then yields the vector start. Exact instruction and staged provenance are retained in `instruction-witness.tsv` and `vector-provenance.tsv`. The `+0x88` store sources current `r4`, not an assumed zero. The last three outside-range stores load through current `r7` plus `0x58`, `0x5c`, and `0x68`.

The post-call target formulas all use current `r5`; their tabulated `D+offset` values require current `r5=P`. `countercases.tsv` includes fixed register changes showing the output candidate shift under getter `r6` change and the post-store/vector separation under imported-call `r5`/`r6` changes. In particular, a different post-memcpy `r5` shifts every `r5`-derived store, and a changed post-memcpy `r6` can move the vector out of the candidate range. No opaque-call register preservation, alias absence, or object identity is assumed.

## Scope, provenance, and validation

`source-pins.tsv` binds the task, exact ELF, full WP144 body/literal REA, WP249 context, and accepted getter/import-candidate reports. The 84-byte pool is retained as raw bytes and as a per-word table. WP202/206/207, WP236, and WP241 are hash-pinned summaries only; the latter call-scan reports are contextual and are not transferred as an ABI or effect contract for IoDrvDal. No additional function body was expanded. No target ELF was executed and no VM, device, or network was accessed.

Status: exact body, literal pool, immediate/register equations, and static relocation metadata **VERIFIZIERT**. The 60-byte source identity, output destination `0x1a270`, imported call’s data movement, and post-call overwrite locations are **HYPOTHESIS_REQUIRED** under the listed conditions. Runtime object identity, target mapping, actual import resolution, aliasing, and opaque effects **OFFEN**. The requested STOP-QUOTA.json was not present at its specified path when checked; work remained bounded to local evidence and static calculations.
