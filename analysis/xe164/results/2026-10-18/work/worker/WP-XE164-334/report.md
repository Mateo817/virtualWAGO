> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-334 — bounded `GetDeviceSpecificFnList` inventory

**VERIFIZIERT (statisch, hashgebunden):** The retained 12-byte `GetDeviceSpecificFnList` body at ELF `0x0ec88` (REA/Ghidra `0x1ec88`) loads its nearby literal and returns a pointer to ELF `0x337f8` (REA/Ghidra `0x437f8`). The exact libpackbus source is 148,792 bytes, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`; its Ghidra mapping in this bounded region is `ELF VA + 0x10000`. The four-byte pool word at ELF `0x0ec94` is retained by the accepted WP329 body evidence.

The pointer addresses a 29-record, 52-byte-stride window `[0x337f8,0x33ddc)` (1,508 bytes). The first 28 records contain names and nonzero loader-fixed function-pointer words at `+0x24`; record 28 at `0x33da8` is the first full 52-byte zero record. The independently retained prefix, three table reads, their Ghidra evidence bytes, raw ELF `PT_LOAD` mapping and relocation records agree after their distinct loader-fixup transformations. The table is file-backed through the RW `PT_LOAD` mapping (`p_offset=0x22aa8`, `p_vaddr=0x32aa8`): ELF table VA `0x337f8` maps to file offset `0x237f8`. The argument-type span is separately retained as ELF `[0x33ddc,0x33f98)` / REA `[0x43ddc,0x43f98)`, file offsets `[0x25ddc,0x25f98)`, 444 bytes. It contains 110 referenced argument-type pointer cells across the 28 non-sentinel records. No data after the first zero record was treated as another table row.

The raw row layout, confirmed from the exact bytes and call-site summary, is:

| Row-relative offset | Observed contents |
|---:|---|
| `+0x00..+0x1f` | 32-byte inline name field; shorter names have NUL padding, while a 32-byte name may fill the field exactly |
| `+0x20` | zero word in all 28 populated rows |
| `+0x24` | function-pointer relocation field; nonzero in each populated REA-fixed row and zero in the sentinel |
| `+0x28` | argument count, 0–7 |
| `+0x2c` | pointer to argument-type pointer cells, or zero when count is zero |
| `+0x30` | return-type relocation field |

The retained WP205/WP301 registration summary reports a 52-byte iteration stride, tests `[record+0x24]` for the nonnull sentinel, supplies the row name, passes `+0x28` as the count, `+0x2c` as the fifth `ffi_prep_cif` input on the stack, `+0x30` in `r3`, and sets `r1` to numeric `2`. These caller details are recorded as accepted prior-source context; this package does not expand the caller again or assign a meaning to the numeric `2`, infer a prototype/ABI, or establish that this registration path is reached at runtime. The table bytes independently confirm the offsets and sentinel shape stated above.

`record-inventory.tsv` gives each of the 28 records with its name, raw function-field addend, REA-fixed word, relocation kind/symbol, statically derived local target where defined, argument count/vector, each versioned argument-type relocation, return-type relocation, and REA external token. `argument-type-relocations.tsv` enumerates all 110 argument positions. Function associations are by record position: name strings and relocation symbols are shown separately, including cases where their spellings differ. No referenced function body is expanded.

## Loader-fixup comparison

Raw bytes and REA/Ghidra bytes are not always equal. For `R_ARM_RELATIVE` fields, the raw word is the ELF addend and the retained REA word is that addend plus the observed `0x10000` analysis mapping. For defined internal-symbol `R_ARM_ABS32` fields, the raw addend plus the symbol value maps to the corresponding observed Ghidra word with the same `+0x10000` mapping. This verifies the static source/analysis correspondence only; these are not measured process addresses.

All argument-type and return-type words use `R_ARM_ABS32` references to versioned external symbols. Their source-file addends are zero. REA represents these external references with synthetic values such as `0x5816c`, `0x581f0`, `0x5808c`, `0x58058`, and `0x58148`. `loader-fixup-matrix.tsv` preserves raw addends, REA-observed values and exact relocation names side by side; the REA synthetic values must not be read as runtime pointers.

The 110 argument cells reference `ffi_type_uint8`, `ffi_type_pointer`, and `ffi_type_uint16` at the exact version `LIBFFI_BASE_8.0`. The 28 return-type relocations name `ffi_type_sint32` in 26 rows and `ffi_type_uint32` in two. The exact local WP331 candidate `libffi.so.8.1.4` is 46,764 bytes, SHA-256 `d162a9b28a30f10bd8baacac3a62b32148563e3b1e4d25c81361211d3172c4f5`; its dynamic symbols contain the five referenced type objects at ELF VAs `0xa300`, `0xa324`, `0xa330`, `0xa348`, and `0xa360`, each reported as a 12-byte object with `LIBFFI_BASE_8.0` version. This pins an exact local candidate and symbol metadata, not the runtime library winner or runtime relocation results.

## Limits and status

**OFFEN:** Actual module binding and load bias; whether the getter and registration path execute; runtime values after loader relocation; constructor/reachability; dynamic callback invocation; meanings of type names in application terms; ABI details; and all behavior of the 28 referenced functions. This inventory does not establish that the exact WP331 libffi file wins at runtime. No backend function or libffi implementation body was analyzed.

Static read-only consistency validation: **PASS** (`python3 validate.py`). Runtime, device, network, VM and product tests: **NOT_RUN**. `build_inventory.py` reconstructs the bounded evidence tables; `validate.py` is a separate read-only checker and does not write package outputs.
