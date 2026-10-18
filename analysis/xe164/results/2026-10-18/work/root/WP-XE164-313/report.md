> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-313 — Root review of helper and lookup boundaries

Root Self-Review, not an independent worker review. WP303's four78-PC routes independently decode exact A32 source words across libdal helpers, resolved PLT and GLib's divisor1 selected query. Source-model instruction semantics were inspected, including load/store widths, PC+8, BL/BX LR transitions, explicit frame save/restore, status LDR/CMP/BLS, and hash/equality leaves. Unused generic shift/carry cases are not generalized.

The supplement additionally snapshots all entry registers immutably and checks current r4-r11 and SP after each complete modeled helper return, plus the exact return PC. All four fixtures pass. LR itself is **not** restored to entry LR: final LR is GLibBias+0x45e2c, the most recent equality-callback return. Control returns via the helper's saved PC. This distinction matters for any later composition.

WP306 corrects the rejected original300 PC semantics. Independent actual Luna309 supports the corrected state/flags/stack model. Its phrase “constructible provider table” is not adopted: the canonical claim is only a stipulated synthetic path, with constructor reachability **OFFEN**. Original306 and309 are frozen to preserve their reciprocal pins. Constructor304 writes divisor7; the current fixtures use divisor1. A separate314 composition is being built for numeric fields8/7/7; it will still require table/population/binding premises.

**VERIFIZIERT:** exact source-derived conditional helper returns byte1 and u32(T+110), with actual modeled GP4..11/SP retention and saved return-PC control. **HYPOTHESE:** all stipulated source-ELF bindings, memory mappings/table data/callback slots and no-fault/no-concurrency conditions. **OFFEN:** actual object/table/constructor/API/ABI/runtime identity and all unselected paths. **PASS:** private source/model validators and this explicit state supplement. **NOT_RUN:** vendor execution, VM, target network, hardware or runtime tests.
