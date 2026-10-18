> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-416 — correction to the WP413 post-allocator read-set audit

**Self-Review. VERIFIZIERT** for the event-ordered post-return reads and fixture writes listed here, using the pinned WP407 trace/event records and source-level fixture premises. WP407 itself remains unchanged and its model is not rejected: the correction concerns WP413’s own audit logic, which filtered events by numerically increasing PC and therefore dropped loop-back accesses at lower PCs. WP413 also contained a no-op assertion equivalent to `True` for the 0xc3ac route. WP416 replaces that check with explicit executed-lane/call checks and event-order read validation.

WP407 is pinned by manifest SHA-256 `e0c8ae6ded5f5e76c30f778205df5ece3a9557b9d20e90f02b7820f5b8cea491`; WP413’s frozen package manifest is pinned by its recorded SHA-256 `bb75ea51de8743b4fcc458eb1073a6b74896ec10c25285785baaf795a5215574`. The exact FW31 image remains `libpackbus.so.1.0.1`, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. WP416 is a separate correction package and does not modify either upstream package.

For all 48 selected producer traces, the ordered memory-read events after the `opaque-malloc-normal-return` event contain 12 reads:

1. The local word at active `SP+0xc` (the kind-2 path returns at 0xc3d8; kind-5 at 0xc41c).
2. The input byte at `S+0xd`, reached after a loop-back to 0xc284.
3. The terminating halfword at `S+0x12`, reached at 0xc224.
4. Nine saved-frame words, `SP+20` through `SP+52`, loaded by the actual 0xc268 epilogue: saved r4-r11 followed by the entry LR that becomes the caller return PC.

The validator uses event-list order rather than comparing PCs numerically, verifies addresses, widths and values against the trace, and checks that stack/local values were stored before the opaque boundary. The fixture source pins establish `S+0xd=0` and a zero halfword at `S+0x12`; the recorded post-boundary reads match. The saved-frame reads match the pre-boundary frame stores and the restored final r4-r11/SP/PC values. Therefore the earlier WP413 statement that the selected continuation read only `SP+0xc` is incorrect; it arose because later loop reads use lower numeric PCs. The actual ordered read list validates memory preservation for the active frame and the two input values.

The opaque event’s prior outer-field preservation ranges are `[O,O+8)` and `[O+0xc,O+0x10)`. The trace shows O+0 and O+4 and O+0xc written before the opaque event, then O+8 assigned R after return; the final outer word vector is `[17,1,R,1]`. These prior outer bytes are output state that survives the modeled opaque event, not post-return reads. The source and event check also retain the explicit 16-byte A5 allocator-return fixture and kind-dependent R field writes. None of this establishes real allocator behavior, allocation size, runtime GOT target, or caller reachability.

The producer branch chosen by kind and the BL instruction are both checked as executed in the recorded trace, in addition to raw PC/word/NZCV condition consistency. The 48-record matrix still covers two code-image biases, both kinds, all three S+4 banks, the stated kind-5 masks, and both flag values. The separately entered helpers retain their numeric copy/mask results. The local WP407 read-only validator passed earlier; WP416’s corrected independent checker also passes. Neither checker is a second full A32 interpreter: WP416 validates source associations, recorded PC/condition transitions, ordered memory events and independently recomputed fixture/output relations.

Runtime binding, actual allocation and object identity, API/configuration meaning, ABI, lifecycle, and hardware behavior remain **OFFEN**. Native/target/runtime/VM/network/device execution is **NOT_RUN**.
