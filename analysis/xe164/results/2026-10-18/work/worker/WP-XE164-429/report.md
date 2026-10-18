> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-429 — independent audit of SPI_Init’s local body

**VERIFIZIERT, bounded:** I independently checked Root WP428 against the exact FW31 `libpackbus.so.1.0.1` image, ELF dynamic symbol table, PT_LOAD segments, raw A32 words, and the retained WP428 REA records. The image SHA-256 is `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. ELF Dynsym identifies `SPI_Init` as a global function at ELF `0xa960` with size 8 bytes. The two words uniquely map through PT_LOAD at `0xa960` and `0xa964`: `0xe3a00000` and `0xe12fff1e`.

Raw field decoding agrees with REA: the first word is an unconditional A32 MOV-immediate to r0 of zero, with S clear, so it writes only r0 and does not update NZCV. The second is BX using LR as its register operand. There are no load/store encodings, no stack operation, no BL, and no other explicit GPR write in the body. BX transfers control through the current LR; its execution-state selection depends on the low bit of that current value. The body itself does not establish a valid LR or return target.

WP428’s local-body conclusion is therefore supported: when execution is bound to these exact bytes and reaches the body with a valid current LR, it sets r0 to zero and transfers control through LR. This is a static leaf-body result only. It does not prove the caller’s PLT/GOT slot at `0x33250` resolves to this body, the runtime-selected provider, or a whole SCPU_Init/boot/reset contract. Those remain **OFFEN**. Native/vendor/runtime/VM/network/device execution is **NOT_RUN**.

The read-only validator parses the ELF header, PT_LOADs, Dynsym and linked string table, checks the unique file mappings and original words, decodes the two A32 instruction fields, verifies the WP428 REA body/procedure records and frozen-package hash, and checks its own package inventory. No upstream file was changed.
