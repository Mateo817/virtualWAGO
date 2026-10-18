> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-303 — bounded synthetic wrapper composition

## Result

For two synthetic, non-aliasing memory fixtures, a source-word-driven A32 stepper follows each selected libdal wrapper path through the exact GLib lookup path, the exact integer hash/equality callbacks, and the divisor-one nested arithmetic fast path. Under the listed premises, helper `0x2194` returns byte `1` loaded from `[T+0x170]`; helper `0x1ecc` returns `T+0x110`. These are conditional source-model results, not claims about a live process, runtime binding, ABI, or the semantic API contract.

The traces contain 78 executed instructions for each wrapper in each fixture. The four paths return:

| Fixture | Wrapper | Return | Entry/final SP |
|---|---|---:|---:|
| A | `0x2194` | `0x1` | `0x70001000` |
| A | `0x1ecc` | `0x25000510` (`T+0x110`) | `0x70003000` |
| B | `0x2194` | `0x1` | `0x78002000` |
| B | `0x1ecc` | `0x5500c510` (`T+0x110`) | `0x78004000` |

Each wrapper receives numeric `r0=7`. Its own instructions save that value at entry `SP-12` and pass the address of that local word as the lookup query pointer. The fixture's stored key word and cached first-bucket word are also `7`. The table divisor is `1`, so the selected nested route reaches its divisor-one fast path. The lookup returns `T`; the wrappers then read `[T+0x170]` or add `0x110` to `T` respectively.

## Source and route

The source inputs are pinned in `source-pins.tsv`; exact instruction words and their assembly labels are in `source-words.tsv`. The model fetches only those pinned words. For this route it independently decodes and steps the GLib raw instruction at ELF `0x45e60` (`LDR r3,[r2,r11]`), then `0x45e64` (`CMP r3,#1`) and `0x45e68` (`BLS`). With the fixture's status word `7`, the compare produces `N=0,Z=0,C=1,V=0`, so `BLS` is not taken. This matters because the earlier WP300 stepper used an incorrect interpretation of that lane; WP303 does not rely on its functional replay or expected outputs.

The selected routes stay inside the listed libdal bodies, the three-word PLT, the GLib lookup body, the two callback bodies, and the divisor-one arithmetic route. `trace.tsv` records object-relative source PC, runtime PC, word, condition evaluation, flags, resulting registers, and next PC for every step. `effects.tsv` records each actual modeled memory read/write and call event. `plt-resolution.tsv` records the three PLT steps; the final read is from `DalBias+0x140ec`. Raw ELF relocation metadata identifies that cell as `R_ARM_JUMP_SLOT` for `g_hash_table_lookup`; the value `GLibBias+0x45d6c` is stipulated by the synthetic fixture, not established as a live binding.

The literal words derive the wrapper's table-global address `DalBias+0x141e0`. The fixture supplies a readable table pointer there, callback pointers at table offsets `+0x24/+0x28`, and the lookup data words listed in `fixture-setup.tsv`. These are explicit memory premises. This package does not establish how a constructor creates or populates such a table, nor the runtime identity of its callback bindings.

## Frame and limits

`fixture-ranges.tsv` gives each code, table, array, target-byte, GOT/global cell, literal, and private stack range. The stack key is at wrapper entry `SP-12`; the wrapper, GLib lookup, and nested arithmetic stack frames occupy disjoint intervals within the corresponding private stack mapping. All modeled stack reads/writes are mapped, each wrapper returns with its entry SP, and code/data/stack mappings are disjoint in both fixtures. Return sentinels are opaque and are not executed.

The direct-resolved lookup value, table contents, callback addresses, equality/hash input words, divisor, target pointer, and target byte are fixture premises. `negative-controls.tsv` records rejection or changed outcomes for altered GOT, missing global/table/query mappings, divisor, key/bucket values, callback order, byte, target pointer, and aliasing conditions. The stepper is a bounded mathematical A32 model for the traced source subset; it is not ELF execution or a general ARM emulator. Fault handling, concurrency, other lookup cases, unselected control flow, runtime loader behavior, actual table construction, ABI, and application/API meaning remain **OFFEN**.

## Status

- **VERIFIZIERT:** pinned source-word path and the four conditional step traces, including the corrected status-lane flags and not-taken `BLS` branch.
- **HYPOTHESE:** synthetic memory, direct-resolved GOT value, callback pointer contents, and all fixture data/range premises.
- **OFFEN:** live runtime binding/state, general lookup behavior, API contract, ABI, concurrency, fault behavior, and all unselected paths.
- **Test:** `PASS` — read-only validator checks source pins, source words, generated trace/effect equality, path conditions, frame/range premises, and negative controls. No ELF/runtime execution: `NOT_RUN`.
