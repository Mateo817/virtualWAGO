> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-367 — independent GLib string callback and hash audit

**VERIFIZIERT, bounded and static:** I independently checked the frozen WP346 source words against the exact GLib ELF and recomputed all 28 retained ASCII-name hash values from the hash-bound WP334 inventory. The source hash recurrence uses signed-byte loads and 32-bit wrap. The equality wrapper maps its opaque current return word through CLZ/LSR, and the exact PLT arithmetic reaches the statically named `strcmp@GLIBC_2.4` JUMP_SLOT slot. **OFFEN:** table construction, actual callback/PLT binding, lookup execution, input-memory validity beyond the local path premise, API/ABI and runtime behavior. **PASS:** local read-only validation. **NOT_RUN:** native/vendor/runtime/VM/device/network.

## Exact source and address domains

The subject is `libglib-2.0.so.0.8200.2`, 1,199,352 bytes, SHA-256 `3f927b8aae0e3e1b1296bde9009ba9fb9380f64ac26ebe8b7675638e3250cbc5`. Frozen WP346 manifest SHA-256: `a0730ff5d39fb2991957e4ac73c1752c59b70a04e8efd9754ec4263555201c62`. Its 19 selected words are the complete retained 5-word `g_str_equal` body at ELF `0x47504`, 11-word `g_str_hash` body at ELF `0x47518`, and 3-word `strcmp` PLT slice at ELF `0x1c0c4`. Raw file offsets equal ELF VAs for these instruction records; Ghidra addresses are ELF VA plus `0x10000`. `raw-binding.tsv` repeats the exact source inventory and the validator compares each word and byte sequence to the copied ELF and retained REA body.

The GLib file is the pinned local candidate, not proof that it wins loader binding in a process. `WP334 record-inventory.tsv` supplies the 28 ordered names and their 32-byte name-field bytes; WP346 supplies the recorded finite hash outputs. The validator independently checks the names and byte lengths, then computes each value from ASCII bytes rather than using WP346's builder or hash function. All 28 values match WP346 exactly. This is finite arithmetic evidence, not a function-list lookup replay or callback-table reachability claim.

## Hash leaf

The first source word is `LDRSB r3,[r0]`; the code then copies the input pointer into r2, loads seed `0x1505` (5381) into r0, tests the sign-extended byte and returns on zero. For nonzero bytes it executes `r0 = U32(r0 + (r0 << 5))`, then `r0 = U32(r3 + r0)`. It advances r2 and sign-loads the next byte with post-index writeback, compares that byte to zero, loops to the multiply-by-33 additions while nonzero, and otherwise returns current r0. No stack frame or call appears in the 11-word body. Source effects include writes to r0/r2/r3 and condition flags; other consequences are not expanded.

`independent-hashes.tsv` contains all 28 names, ASCII byte lengths, independently computed 32-bit words, retained WP346 words, and equality checks. The finite controls distinguish signed from unsigned load behavior: for byte sequence `80 00`, the source recurrence's first update is `0x0002b525` (signed -128), while an unsigned-byte control would produce `0x0002b625`. For ASCII byte sequences the values coincide because bytes are below 0x80. An empty sequence returns the initial 5381 after the first zero comparison and does not perform a recurrence update. Nonterminated input, faults, concurrent writes, and arbitrary high-byte sequences beyond the explicit controls are not bounded here.

## Equality wrapper and conditional PLT resolution

The wrapper saves r4/LR, calls the local three-instruction PLT slice, applies `CLZ r0,r0`, shifts current r0 right by five, and pops r4/PC. For any current 32-bit word from a normally returning opaque target, zero gives CLZ 32 then result 1; any nonzero word has CLZ 0..31 then result 0. The wrapper does not establish what the word means, and the export/import spelling does not supply a comparison contract. Reaching the pop requires an intact usable saved frame/stack. No ABI preservation is assumed.

The PLT arithmetic is in `plt-ledger.tsv`: at Ghidra PC `0x2c0c4`, ADR uses architectural PC `0x2c0cc` plus decoded immediate `0x00100000`, yielding `0x12c0cc`. The next ADD gives `0x1430cc`; the preindexed LDR slot is `0x1430cc+0xf78=0x144044` Ghidra / ELF `0x134044`. The retained relocation at ELF `0x134044` is `R_ARM_JUMP_SLOT strcmp@GLIBC_2.4`. It is a relocation address and symbol/version record, not runtime slot contents or the eventual winner. The wrapper's current r0 after this opaque target remains an explicit precondition for the local CLZ mapping.

## Scope limits

No actual module binding, table construction, callback registration, runtime lookup, or equality invocation is proved. The GLib symbol names and static table records do not establish an API prototype or ABI. The hash recurrence does not establish that an input pointer is valid or NUL-terminated in a process. Static source and finite arithmetic are **VERIFIZIERT** within the pins; loader winner, source producer/consumer identity, runtime values and external effects remain **OFFEN**. No native ELF, vendor code, runtime, VM, target device or network execution occurred.

## Independent review findings

No incorrect instruction words, register expressions, or conditional source claims were found in the bounded WP346 slice. The independent checks confirm the 19 raw instructions, complete five- and eleven-word REA bodies, ELF/PT_LOAD byte mapping, signed-byte recurrence, finite names and PLT relocation arithmetic. `review-findings.tsv` records each claim and its boundary. WP334 inventory row 28 is an explicit zero sentinel; only rows 0–27 are names and are compared to the 28-value WP346 table.

The local validator recomputes from raw input bytes and does not import or invoke WP346's builder. It checks the frozen WP346 package manifest, the pinned GLib bytes, source-to-REA instruction agreement, all 28 name/value rows, signed/unsigned high-byte controls, equality-wrapper integer controls, decoded PLT immediates, and exact static relocation record. Its PASS covers these checks only.
