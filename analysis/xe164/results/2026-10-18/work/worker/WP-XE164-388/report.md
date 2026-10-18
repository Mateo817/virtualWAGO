> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-388 — selected `length` query source replay

**Self-Review. VERIFIZIERT** for the selected 45-word `length` body, 3-word PLT, 4-word local getter, four literal words, the raw-word stepper traces and conditional numeric relationships in the listed synthetic fixtures. **PASS** for the read-only validator. Runtime GOT/provider identity, actual global contents, caller reachability/object construction, index bounds, API/prototype/units, ABI, hardware/runtime execution are **OFFEN**. Native, VM, network, device and runtime tests are **NOT_RUN**.

This package uses the exact FW31 `libpackbus.so.1.0.1` artifact, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`, retained from WP310. WP356 supplies the `length` instruction evidence and WP363 supplies the selected PLT/getter instruction evidence. The copied reports/tables and raw object are hash-pinned under `pins/`. For every selected instruction, file offset equals ELF VA and its word matches the little-endian raw bytes. Relevant source extent is exactly `d5f8..d6a8` (45 words), `81cc..81d4` (3 words), and `bec4..bed0` (4 words). Separate literal words are at `d6ac`, `d6b0`, `d6b4`, and `bed4`; none is counted as executable code.

The body’s numeric path is derived instruction by instruction. Entry `r0` is multiplied by 12 and used to read one word at `0x337d0 + U32(12*entry_r0)`. That word becomes the argument to the exact local PLT at `0x81cc`. The pinned raw relocation table has `R_ARM_JUMP_SLOT` at `0x3349c` for `SSC_parse_get_content_lengths`, with static symbol value `0x0000bec4`. The replay assigns that value to the GOT slot, so it executes the retained local getter under this explicit binding premise. Dynamic-loader interposition/runtime winner is still open. The getter computes `0x4013c + U32(mappedIndex << 4)` and returns that address in `r0`. No contents or meaning are assigned to the mapped-index word from the source alone.

For getter result `L`, the body’s first four optional output writes follow this exact source order:

1. If entry `r1 != 0`, read `[L+0]` and store to `[entry r1]` (`d634`, `d638`).
2. If entry `r2 != 0`, read `[L+4]` and store to `[entry r2]` (`d640`, `d644`).
3. If `[entrySP] != 0`, read `[L+0xc]` and store through that pointer (`d64c`, `d650`).
4. If entry `r3 != 0`, read `[L+8]` and store to `[entry r3]` (`d658`, `d65c`).

Two further optional outputs use the same pointer cell. If `[entrySP+4] != 0`, load a source word from `globalBase + U32(index+2)*8`, shift it left by three with 32-bit arithmetic, and store through that output pointer (`d678..d680`). If `[entrySP+8] != 0`, load from `globalBase + U32(index)*8 + 0x14`, shift left by three, and store through its output pointer (`d690..d6a4`). Both literal/PC calculations derive the pointer cell address `0x443f4`; in fixtures that cell contains synthetic base `0x530000`. The four source-side words are distinct numeric fixture values; no public field layout or units are inferred.

The source order matters under aliasing. In the alias fixture, entry `r1` points to `L+4`. The first write stores the word from `L+0` into `L+4`; the later load at `d640` then reads that new value. It stores the overwritten value to the second output. This is the observed instruction order under the fixture’s readable/writable-memory premises, not a general contract for arbitrary aliasing or mapped objects.

After either selected epilogue, `r0` remains the getter result address `L`; none of the copy paths overwrites it, and the pop restores `SP` and returns through the saved incoming `LR`. For index `1`, the replay returns `r0=0x4014c`. The all-null case exits through the conditional pop at `d688`; other listed cases exit through `d6a8`. These are numeric source results, not a success code or a claim about a named API.

`output-matrix.tsv` records all six source positions, gates, loads, stores and transforms. `fixture-premises.tsv` identifies every synthetic mapping, pointer and output-memory assumption. `traces/cases.json` retains per-instruction GPR/PC/NZCV snapshots and memory reads/writes for four cases: all six pointers non-null; all pointers null; selected pointers null; and the explicit `r1=L+4` alias. The model does not impose an index limit. An index whose mapping address is unreadable would stop at that modeled read boundary; no bounds-safety conclusion is made.

The validator checks every selected code word against both the accepted tables and exact raw bytes, checks the four literal words directly, independently derives the mapping base, getter base, PLT slot and global pointer-cell address, and reconstructs output-matrix rows and fixture writes from the traces. `python3 model.py` and `python3 validate.py` both pass. This is a source-only model with stipulated memory/GOT state, not execution of the ELF or proof of any runtime binding.
