> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-378 — independent review of WP375 SetTime replay

**VERIFIZIERT, bounded instruction/state replay:** I independently checked the frozen WP375 package at manifest SHA-256 `803adf7ff6c44cb3071de5e890297c564ae5496f76a0c8c161f207b5bd650636`. Against the exact FW31 DSO bytes, all 54 instruction words and six pool words map correctly. A separate decoder reconstructs every instruction transition across WP375’s 18 selected paths: all 394 fetched rows’ PC progression, condition result, GPR0–14 before/after, NZCV, D16, and next PC match. The selected UMULL/shift/MLS/store arithmetic and 132 ordered memory events also match.

**Concrete evidence limitation:** WP375’s 36 prologue push events report their `before` bytes as zero. The model initializes `self.bytes` empty (apart from the output buffer) and `write()` uses `self.bytes.get(address, 0)` for its before-image. Thus those zeros are default-filled by the model; the stack locations below entry SP have no explicit synthetic preimage and no source-derived prior contents. This does not change the post-push frame, selected pop values, register transitions, or local return path. It means the event table’s push preimages must be read as an implicit zero-fill assumption, not verified memory contents.

## Checks performed

The copied subject is FW31 `libpackbus.so.1.0.1`, 148,792 bytes, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. I checked its ELF32 little-endian shared-object header, all 54 instruction words at ELF `0x14cc8..0x14d9c`, six adjacent words at `0x14da0..0x14db4`, their corresponding Ghidra address bias, and each little-endian byte encoding. WP375, WP360, and WP373 manifest hashes are pinned in `source-pins.tsv`.

The reviewer validator uses no WP375 model/generator. It decodes each trace’s raw word into branch, multiply, data-processing, literal/data memory, block-transfer, or the two exact NEON operations; recomputes arithmetic/flags and source-derived register/PC effects; and chains each supplied pre-state to the preceding computed post-state. It independently rebuilds ordered literal, output, stack-push, and stack-pop events. It also recomputes the selected wrapped low-word product, unsigned accepted range, UMULL halves, `Q`, MLS remainder, and scaled remainder. All selected arithmetic values agree, including `0xffffffff * 0xffffffff -> 1`, `65536 * 65536 -> 0` rejection, the first above-range value, and the `0x3fffffff` boundary.

All three rejected routes end before the actual opaque logger instruction: wrapped-zero at Ghidra `0x24d4c`, above-limit at `0x24d70`, and null-pointer at `0x24d94`. No BL executes and no logger result or effect is assumed. Accepted paths complete the local epilogue under the synthetic writable stack premise: the recorded push words are subsequently popped, r4 and SP are restored, and PC takes the saved local LR value. This is conditional source-path behavior, not an ABI or caller claim.

I also ran WP375’s default read-only validator once. It reported `PASS WP375`. Its own manifest verified both before and after; `sha256sum -c` output was byte-identical and no `__pycache__` was created. This validates its in-memory regeneration and frozen output comparisons; the independent review above does not rely on that validator as the instruction-execution oracle.

## Limits

The independent result covers only the selected source paths and synthetic input/memory fixtures. It does not establish API semantics, parameter or field meanings, units, caller-supplied registers, ABI, runtime/lifecycle behavior, logger effects, or hardware behavior. The zero push preimages are the sole concrete review qualification found; no arithmetic, branch, decoded transition, post-write value, event ordering, stack restore, return endpoint, or rejected-path boundary mismatch was found.

**PASS:** independent validator, WP375 default validator, source and manifest pins. **NOT_RUN:** native ELF execution, runtime, VM, target, network, or device access.
