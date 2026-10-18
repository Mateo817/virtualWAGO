> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-393 — independent review of WP389

**VERIFIZIERT (bounded synthetic source replay review):** WP389 is manifest-consistent and its 16 saved GetCnfFromRail traces match the exact pinned source-word tables for the selected local-binding fixture. I independently checked every executed PC/word against the raw FW31 object, reconstructed input stack/config/global/output/literal/GOT memory, checked source conditions and branch targets, and replayed loads/stores and stack transfers against that memory. The recorded outputs, both biases, both numeric modes, both config-byte values, and both optional third-pointer cases are consistent. **OFFEN:** runtime symbol binding, whether `G` is zero in any actual process, constructor/reachability of the fixture, external API/ABI meaning, and device behavior.

## Scope and pins

WP389 manifest SHA-256 is `0a6ec57daf6d4fc8b63d5d4f1d00a8cc1cfc9b19edd6007d911e8b98f37baf24`; it matches the requested target. I read its report, `fixtures.json`, `replay.py`, `validate.py`, and all 16 traces without changing them. WP380 and WP385 manifests match `a5c5fdd967321a7b1f5f5fe3b0cb9ededa2b73352f7d0f93a1773cc54bdc652b` and `dc95fcc67847f2d4cf3bfb33edc967d8d2340d480936d0d0fe27bce04f193319`. The exact pinned `libpackbus.so.1.0.1` SHA-256 is `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`.

The independent checker maps each of WP380's 957 instruction words plus 10 literal words and WP385's 130 instruction words plus five literal words through the ELF `PT_LOAD` file mapping and compares the bytes directly. It also confirms the two JUMP_SLOT records used by the local-binding fixture: `0x334d4 -> 0x117ec` and `0x334d8 -> 0x116e0`. These fixture bindings establish a reproducible local source route only.

## Trace and fixture findings

All 16 metadata tuples are unique and cover two biases (`0x10000000`, `0x20000000`) crossed with modes 1/2, config byte 0/`0x20`, and third pointer null/non-null. The independently reconstructed initial bytes include entry stack words `(config-byte, 0x1234, third-pointer)`, the config bytes, `word[G]=0` at `G=0x4442c+bias`, the four distinct slot canaries at `C+0x20..0x2f` for `C=0x4013c+bias`, five source literals, and both selected GOT cell values. The trace's first snapshot follows the entry save instruction, so its SP is entry SP minus 36; accounting for this, the initial stack premises and final restored entry SP match.

For every instruction row, the checker verifies the raw source word, the condition result from the previous row's NZCV, and each direct branch's next PC from its signed PC-relative displacement. It independently executes the traced immediate/register-offset loads and stores and multiple-register stack transfers over the seeded and subsequently updated memory. Thus getter loads really read the seeded zero global, and selected caller writes land at the claimed addresses rather than merely matching a summary row.

Each trace visits descriptor getter entry `0x116e0` twice and count getter entry `0x117ec` twice. The source path reads zero at `G`, takes the corresponding conditional return/pop, and does not reach the first later-call PCs `0x116fc`, `0x11714`, `0x1171c`, `0x11804`, or `0x11818`. Under these stipulated local target cells and `G=0`, the trace therefore has no intervening opaque call on the selected path. This does not determine actual runtime binding or global initialization.

The four caller slots at index 2 finish as follows: mode 1 has `[C+0x20,C+0x24,C+0x28,C+0x2c] = [0xa5000000,0,0xa5000002,0]`; mode 2 has `[0,0xa5000001,0,0xa5000003]`. The unselected pair retains its distinct canaries. For config byte `0x20`, each trace visits `0xc974` and `0xc978`; TST sees current `r10=0` and sets Z, so the NE add is skipped. The third output pointer is read from the third entry-stack word (the stack location is later addressed through the caller frame); when non-null, the guarded store writes zero at that pointer, and when null the store is skipped. All traces return numeric zero and restore SP to the fixture's entry SP.

I ran WP389's read-only validator and my separate `audit.py`; both passed. My checker is independent for fixture reconstruction, raw-source byte mapping, condition/branch checks, and memory/stack-transfer consistency. It is not a second complete A32 arithmetic engine: data-processing result values and final trace generation are additionally supported by WP389's bounded source-word stepper and validator. That is the review's principal limit; it does not affect the direct load/store address checks or the raw branch/condition assertions above.

## WP384/WP386 correction review

The correction in WP389 is accurate. The pinned WP384 report (`c7ebaaa84d2126dbdee8dac31c01a724c9419c159ff346582c8341fe32bec2c2`) says “lokale PLT-Adresse7998” in the two relevant passages; it does not label `0x17998` as an ELF VA. WP386's report (`37fc1c4fd430eafa0ec069dc7d63a01bf8c38f92ef4cd0ba5159c70b09a680c1`) introduced that mistaken claim in its own review prose. The corresponding raw target is ELF `0x7998`, Ghidra `0x17998`; the WP386 erratum is properly withdrawn. WP384 and WP386 remain unchanged.

No runtime, VM, network, device, or native target execution was performed. This is a source-artifact review and synthetic replay only; native/runtime/device tests are **NOT_RUN**.
