> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-318 — independent review of callback publication

## Result

**VERIFIZIERT (bounded source mapping):** In the pinned FW31 `libpackbus.so.1.0.1`, the retained source inventory covers 407 A32 words in the bounded body and a separate 54-word pool. The 16 early `R_ARM_GLOB_DAT` values are addressed through the computed GOT base, loaded to core registers and staged in stack words, then loaded into D-registers for four `VST1.32` stores. Three more late GOT-derived values are written individually. The independent matrix reproduces the numeric destinations, source lanes, exact relocation symbol names, ELF GOT slots, and store PCs. This verifies the bounded source arithmetic and store layout, not a runtime callback table or public structure contract.

The four vector instructions publish lanes in this order: `{d14,d15}` at current `r4+0x14`, `{d10,d11}` at `+0x24`, `{d12,d13}` at `+0x34`, and `{d8,d9}` at `+0x44`. Their lane-by-lane numeric mapping is in `callback-publication-matrix.tsv`. The separate scalar stores at `+0x54`, `+0x58`, and `+0x5c` come from late loads through current `r11`; the first two use `r2`, the last uses `r3`. All 19 exact names and slots are `R_ARM_GLOB_DAT` entries in the pinned ELF relocation metadata. Exact symbol spellings establish names only, not callable prototypes or behavior.

The source writes `0x2ee0` at current `r4+4` and `r4+8`, and writes current `r6` at `r4+0x10`. It reaches the publication block only on the local `r4 != r6` path: `CMP r4,r6` at Ghidra `0x209ec` followed by `BEQ 0x20a58` at `0x209f4`, which skips the stores. The local body copies entry `r0` to `r4` at `0x20738` and entry `r1` to `r6` at `0x20730`; later calls are opaque. The late loads require current `r11` to remain the GOT base, the destination stores require current `r4` to remain the intended writable output address, and the staged values require the D-register contents to survive opaque calls before publication. The epilogue restores `d8-d15` and the saved core frame only under the usual visible-path condition that opaque calls have not invalidated the active stack or saved state. These are source-path conditions, not ABI claims.

## Address join correction

WP311's final address-join paragraph needs correction. The retained WP301 callsite at ELF `0x226c` belongs to **`libdal.so.1.0.1`**, not IoDrvDal. Its preceding instruction computes `current r0 = current r6+0x110`; the indirect call at `0x226c` uses that value. In `libpackbus_open`, Ghidra `0x20738` copies entry `r0` into current `r4`. Therefore, if this provider entry receives that pointer and current `r4` still names it at publication, the provider writes at `current r4+field_offset`, conditionally equivalent to `(caller current r6+0x110)+field_offset`. The provider expression is **not** `current r4+0x110`; adding another `0x110` would double the caller's offset. The equation is only a conditional pointer-expression match. It does not establish that this exact provider call occurs, that object identity survives, or that any runtime table was published. See `address-join.tsv`.

Address domains are kept separate: the code's Ghidra analysis domain yields GOT base `0x43000`; the corresponding ELF address is `0x33000`; runtime address arithmetic would require an image load bias and would be `B+0x33000`. No runtime base is asserted.

## Consumer labels and limits

The six cyclic names are cross-referenced positionally against the retained WP057 consumer summary. WP057's consumer slot labels/offsets and the provider's numeric `r4` offsets are separate namespaces. This match does not prove runtime binding, prototypes, API contract, or lifecycle meaning. In particular, vector `+0x3c` is the exact relocation named `libpackbus_DiagGetDeviceState`; the separate backend `+0x58` is `libpackbus_WatchdogStop`.

WP311's source artifacts remain unchanged. This independent review's own findings, pins, and read-only validator are in this worker package. The validator confirms the hash pins, body/pool inventory, exact ELF bytes at the recorded file offsets, relocation names/slots, store offsets and lanes, local gate, literals, and corrected join evidence. It is a static file check and does not execute the ELF or a native model.

**Review status: VERIFIZIERT** for bounded source mapping and arithmetic; runtime binding, object identity, and semantic/API claims remain **OFFEN**. **Validation: PASS**; target execution: **NOT_RUN**. This is an independent worker review, not a claim of a separate external review.
