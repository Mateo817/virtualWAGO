> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-277 — local contracts for three `libdal` helper bodies

**Status: VERIFIZIERT within the three exact bodies; conditional at their opaque-call boundaries.** This offline report uses only the exact WP202 `libdal.so.1.0.1` source, the three assigned bodies, their directly referenced literal words, and the PLT/dynamic metadata for the one call made by two bodies. The WP274 reports are used only as hash-pinned summaries of the three candidate gate sequences. There is no call-target body expansion, runtime execution, or hardware inference.

## Source and body identity

The source is 18,076 bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. WP202 binds this same file and states that the first PT_LOAD maps ELF VA to equal file offset for the queried code region; its Ghidra import uses a `+0x10000` display bias. WP202 and the three WP274 source-summary files are independently pinned in `source-pins.tsv`.

REA `procedure_info` ran first for Ghidra addresses `0x12180`, `0x12194`, and `0x11ecc`. Each returned one unique contiguous body under the 768-byte cap: ELF `0x2180` is 16 bytes/one block; `0x2194` and `0x1ecc` are each 56 bytes/three blocks. Exact ranges and REA evidence IDs are in `rea-evidence.tsv`. The complete instruction words are source-reconstructed in `instructions.tsv` and checked byte-for-byte by `validate.py`.

## Local instruction-derived behavior

At ELF `0x2180`, the body loads literal `0x12054`, adds the A32 PC value `0x218c`, and obtains base `P+0x141e0` (where `P` is the ELF load bias). It reads one unsigned byte at `[P+0x14208]`, places that zero-extended value in `r0`, and returns through the entry `lr`. Entry `r0` is not read. The body has no store or nested call. Its instructions do not write `r4-r7`, `sp`, or `lr`, so their local values are preserved across this body.

At `0x2194`, the body saves entry `lr` at `[entrySP-4]`, reserves 12 bytes, and stores entry `r0` at `[entrySP-12]`. It computes the same base `P+0x141e0` and loads the word `C=[P+0x141e0]`. If `C==0`, it returns zero. Otherwise it calls the PLT entry at `0x15f4` with `r0=C`, `r1=entrySP-12`; the body does not explicitly initialize `r2` or `r3`. If the nested call returns `Q==0`, it returns zero; otherwise it loads the byte `[Q+0x170]` into `r0`. Consequently the local return is zero when `C==0`, `Q==0`, or that byte is zero, and otherwise is that byte in `1..255`. The code itself gives no stronger contract for the nested target.

At `0x1ecc`, the prologue and table-cell load are structurally the same, again using `C=[P+0x141e0]` and saving entry `r0` at `[entrySP-12]`. When `C!=0`, it calls `0x15f4` with `r0=C`, `r1=entrySP-12`; `r2` and `r3` are not explicitly initialized. A zero nested result returns zero. A nonzero result `T` is changed to `u32(T+0x110)` and returned. That arithmetic can wrap and can itself produce zero; thus the local return is nonzero exactly when `C!=0`, `T!=0`, and `u32(T+0x110)!=0`.

The two wrapper call instructions resolve to PLT entry `0x15f4`. The exact PLT words calculate the relocation slot at ELF VA `0x140ec`, which `readelf` identifies as `R_ARM_JUMP_SLOT`, dynsym index 64, undefined function name `g_hash_table_lookup`. This establishes relocation-linked identity only. It does not establish the target implementation, lookup semantics, side effects, or ABI behavior. See `literals-and-plt.tsv`.

## Register and memory limits

`register-effects.tsv` records the instruction-local register facts. `0x2180` preserves `r4-r7`, `sp`, and `lr` by direct inspection. The wrappers do not explicitly write `r4-r7`, but their opaque PLT call can affect them; no preservation is proven without expanding that target or assuming an ABI. Each wrapper’s own stack arithmetic reserves 16 bytes total and restores `sp` on its visible return path, with the saved entry LR loaded directly into `pc` by `ldr pc,[sp],#4`. Net return and stack restoration are conditional on the nested call returning with a usable wrapper frame. The wrappers’ direct memory writes are only to their current stack frame. Their reads include the fixed table cell and, on nonzero nested return, memory based on the returned `r0`. Nested-call memory effects remain unknown.

## Conditional connection to WP274 gates

WP274 pins three caller candidates at `0x2f98`, `0x2e5c`, and `0x2e04`. Its summary says each invokes these helpers in order, tests current `r0` after each return, and fails locally with `r0=0xffffffff` on a zero result. The first helper’s nonzero gate is exactly the condition `[P+0x14208] != 0`, independent of candidate entry `r0`. Before each later helper the candidate sets `r0` from then-current `r4`.

The second helper’s gate is nonzero only under the local conditions above: the common table cell is nonzero, the opaque nested call returns a nonzero `Q`, and `[Q+0x170]` is nonzero. The third helper’s gate requires a nonzero cell and nested return `T`, plus nonzero `u32(T+0x110)`. These are distinct nested calls; the code does not establish `Q==T` or a stable mapping.

The third helper’s incoming key equals the second helper’s incoming key only if the opaque call inside helper `0x2194` leaves current `r4` unchanged. The bodies do not establish that. Likewise, WP274’s later `r5/r6/r7` checks or forwarded values remain current-register values after opaque calls, not proven entry copies. `gate-matrix.tsv` records these per-candidate conditions and limits. The results are local conditional gates only, not proof of application-level API purpose, device behavior, or a successful transfer.

## Evidence and validation

REA `procedure_info` and `analyze_function` evidence IDs are pinned in `rea-evidence.tsv`; the REA profile and exact ranges are recorded there. `validate.py` reconstructs the full 32-instruction byte stream from the pinned ELF, checks every source and summary pin, checks the three literal words and their PC-derived common base, decodes both nested BL targets, and executes fixed local-model cases for zero/nonzero gate outcomes, wrapped addition, and the conditional r4 relationship. It is read-only and claims no runtime validation.

Run: `python3 work/worker/WP-XE164-277/validate.py` — expected **PASS**, source-and-summary pins, instruction stream, local arithmetic/control-flow model, and qualified gate matrix. This is a deterministic self-check, not an independent review.
