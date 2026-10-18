> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-252 — bounded selector-source audit

Status: VERIFIZIERT local call-free value chains where stated; post-opaque and memory-dependent sources remain OFFEN. This self-review uses exact static bytes and retained Ghidra records, not runtime evidence.

Target `codesys3` is 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`. Four exact Ghidra bodies are byte-bound in `instructions.tsv` and `function-disassembly.objdump.txt`; per-instruction B/BL edges are in `cfg-edges.tsv`. The record IDs and used windows are explicit in `rea-scope.tsv`. My own mapping query hung and was canceled with no result; mapping is grounded in the first RX PT_LOAD and all disassembled words are compared against raw bytes.

The direct aligned A32 B/BL scan over file-backed executable sections is recorded in `direct-callers.tsv`; the exact fixed caller windows are in `caller-windows.objdump.txt`. This does not exclude indirect or dynamic entry. At 0x2ff368 local paths reaching the call set r0=20 at 0x2ff380 with no opaque call between. At 0x2ff6d4 the call-free path likewise sets r0=20. At 0x2ff588 r8 is loaded and tested against 20, but opaque BL 0x7b1d4 occurs before r8 is copied to r0; no preservation or ABI assumption is made. At 0x2ff76c r0 reloads `[r4,#-4]` after an opaque call; both base register and memory value remain unknown.

The separate gate at 0x2ff65c performs LDR, SUB 15, and BICS 2; its matching path admits exactly 15 or 17 as the tested word. This does not establish the later post-opaque selector load at 0x2ff76c.

CMExit's exact body shows loop limits of 0x22 (34) and 8-byte row indexing. Static `.rodata` bytes `[0x3a30c0,0x3a31d0)` are inventoried in `table-34.tsv`; row 20 has first word 15, adjacent rows have 17 and 16. This is membership only. r5 is initialized from r4 at 0x300eec, but opaque calls intervene before the loops; runtime association and selection stay conditional. The word at 0x301390 is separately recorded as a literal.

Remaining limits are in `gaps.tsv`, including stack state for caller 0x2ff8e8 and the WP251-owned 0x2ffbd4 path. No global selector-15 exclusion is claimed. `validate.py` is read-only; manifest excludes itself.
