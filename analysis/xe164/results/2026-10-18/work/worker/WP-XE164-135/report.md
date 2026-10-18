> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-135 — `CMGetAPI3` at `0x002FDD20`

## Finding

**VERIFIZIERT — begrenzte statische Instruktions-, Kontroll- und Datenflussbeobachtung:** In this `codesys3` ELF, `CMGetAPI3` is the exact symbol at ELF VMA `0x002fdd20`. Its dynamic symbol entry has `st_size=1036` (`0x40c`). Ghidra 12.1.4 and Rizin 0.9.1 independently delimit the executable function body as the contiguous inclusive range `0x002fdd20..0x002fe123`, exactly 1,028 bytes (257 4-byte ARM instructions), 8 bytes shorter than the symbol size. The remaining symbol-span bytes `0x002fe124..0x002fe12b` are two literal words, `0x005fc560` and `0x005fc544`; Rizin reports code references loading those words as data at `0x002fdf5c` and `0x002fdf8c`. GNU `objdump` also shows those eight bytes, though it decodes them as conditional ARM instructions when asked to disassemble through the symbol-size end. They are not part of either tool's function body. Thus all 1,036 symbol-span bytes are accounted for; function-instruction coverage is complete for the 1,028-byte tool-bounded body.

At entry, the machine code copies incoming `r3` to callee-saved `r6` (`0x002fdd34`). The immediate caller `CMGetAPI2` stores its own incoming `r3` at `[fp-0x10]` (`0x002fe140`) and passes that address in `r3` (`0x002fe148`, call at `0x002fe14c`). Consequently, in this call context, `r6` in `CMGetAPI3` carries a pointer to that caller stack slot. `CMGetAPI3` reads the pointed 4-byte value when the pointer is non-null (`0x002fdd84`, conditional load at `0x002fdd90`, then global store at `0x002fdda8`). On the later non-null path it reads the pointed word again (`0x002fde84`). If the current pointed value is nonzero, the value loaded at `0x002fde78` is nonzero, and they differ, instruction `0x002fde94` stores the latter word through the same pointer (`strne r1, [r6]`), sets `r9=0x1e` at `0x002fde98`, and returns to the loop at `0x002fde9c`. This is a conditional write to the caller-provided stack slot, not evidence for a named API field. No other store through the preserved incoming-`r3` pointer appears in the complete body instruction table.

The body has four return epilogues. Their actual returned `r0` values are:

| Return epilogue | `r0` source / bounded classification |
|---|---|
| `0x002fe0d8` | `r9`, explicitly set to `2` at `0x002fe0cc` on the null-`r0` entry path. |
| `0x002fdf18` | Current `r9`, loaded to `r0` at `0x002fdf10`. Static paths set it to `0x0f` for the `strlen`-greater-than-63 branch (`0x002fdd64`), `1` (`0x002fddf0` or `0x002fe094`), `0x1e` (`0x002fde98`), `0x1f` (`0x002fe050`), zero on successful paths (`0x002fdee0`), or copy the result of the unresolved indirect call (`0x002fdfa0`) into `r9` at `0x002fdfac`. The bounded code does not establish a closed set for that indirect-call result. |
| `0x002fdf58` | `r9` was set to zero at `0x002fdf44`; returns `0`. The output pointer at `[r1]` is separately written from the local word at `0x002fdf50`. |
| `0x002fe010` | `r9` is set to zero at `0x002fdffc` and copied to `r0` at `0x002fe004`; returns `0`. |

The table records instruction-level mechanics only. It does not assign API meaning to numeric results, globals, strings, or words. The pseudocode in the REA evidence is decompiler output, not source. The machine return register and epilogue instructions govern the classifications above.

## Complete bounded tables and evidence

`instructions.tsv` contains every Ghidra assembly line in the 1,028-byte function body. `blocks.tsv` and `edges.tsv` encode all 52 Ghidra basic blocks and all 85 successor edges. `calls.tsv` contains all 11 call instructions found in that body, including the two unresolved indirect sites (`0x002fde60`, `0x002fdfa0`). `coverage.tsv` records generated counts. These are reproducible from the retained REA record with `node generate_tables.mjs`; validation is `./validate.sh`.

REA Evidence ID: `ev_cb1742b0f1f3f661d8e15319fdcdbf41b35674445afe1319beb21790360c94e3`. It is preserved in `rea-evidence-bundle.json` (one record, 896,070 bytes). Provider: Ghidra 12.1.4; analysis profile digest: `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. REA CFG has 52 blocks and 85 edges; REA direct callee inventory has seven resolved target entries and two unresolved call sites. The full retained instruction and CFG tables are the authoritative generated facets.

The only caller context admitted here is WP-XE164-129's exact `CMGetAPI2` body and instruction table: file size 5,319 bytes, SHA-256 `e7b87195cf01718c18792ec83cbe14c306e8f88706d3229a1db02741bd59cc72`; its `function-instructions.tsv` is 779 bytes, SHA-256 `c0b79d1ada8d1e9888c5330866b4f8f426d8448d831bf141ab79fadde5436c48`. The actual binary is 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.

## Address domain, method, and limits

All instruction and CFG addresses above are ELF VMAs in the default ARM code space, not file offsets. The binary is ELF32 little-endian ARM. The two tail words are at ELF VMA `0x002fe124` and `0x002fe128`; in the executable `PT_LOAD` mapping beginning at file offset `0` / VMA `0x00010000`, their file offsets are `0x002ee124` and `0x002ee128`.

REA was attempted first and completed once successfully; the retained dossier supplies the entire instruction stream, body extent, CFG, direct-callee inventory, pseudocode, and native-value-flow record. Native value flow was available and not truncated (609 operations); it warns that def-use does not cross calls and may omit memory aliasing or call side effects. The pointer analysis above is independently checked against the raw assembly and the one allowed caller's raw assembly. Rizin 0.9.1's bounded `af`/`afij` confirms the same 1,028-byte body, 52 blocks, 85 edges, and the two data references into the eight-byte tail. GNU ARM binutils 2.44 bounded disassembly and `readelf` 2.44 confirm the symbol size and tail bytes. No callee body, other API, or broader caller was used.

Alternatives and residual uncertainty: `st_size=1036` could be mistaken for a 1,036-byte instruction body; Ghidra and Rizin instead agree on 1,028 bytes, and Rizin's references plus the exact two words support treating the terminal eight bytes as literal data included in the symbol span. GNU `objdump`'s fallback disassembly renders those data bytes as instructions, so that decode is not treated as function-body evidence. **OFFEN:** Ghidra cannot resolve the destinations of indirect calls at `0x002fde60` and `0x002fdfa0`; the return contribution from the latter flows into `r9`, so its possible value is not bounded here. This report does not inspect callees or claim runtime effects.

| Check | Status |
|---|---|
| Supplied input identities (size and SHA-256) | PASS |
| Exact dynamic symbol name, address, and size | PASS |
| Ghidra and Rizin body range/count agreement | PASS |
| All 1,028 tool-bounded body bytes represented by 257 4-byte instructions | PASS |
| All eight extra symbol-span bytes accounted as two literal words | PASS |
| CFG instruction/block/edge coverage | PASS |
| Call-site inventory and two unresolved sites retained | PASS |
| Incoming `r3` pointer read/write traced within body and immediate caller | PASS |
| Runtime, VM, network, device, hardware, and PLC operation | NOT_RUN |
| Independent review | NOT_RUN |
| Self-review | PASS |

Statuses use `VERIFIZIERT`, `HYPOTHESE`, `OFFEN`, `BLOCKED`; checks use `PASS`, `FAIL`, `NOT_RUN`, `BLOCKED`. SHA-256 values for this package's generated files are in `SHA256SUMS` (the checksum manifest does not checksum itself).
