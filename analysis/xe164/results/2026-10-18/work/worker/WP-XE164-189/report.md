> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-189 — FW31 IoDrvDal ELF VA `0x1a270`

Status: VERIFIZIERT for the static ELF/file observations and bounded direct materialization below. Runtime and Ghidra correspondence: OFFEN. Test status: PASS for the included validator and checksums.

## Identity and method

The input is the 25,976-byte ELF32 little-endian ARM EABI5 shared object at the assigned path. A fresh SHA-256 is `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`, matching the requested identity. `readelf` is GNU Binutils 2.44; the available cross disassembler is GNU ARM `objdump` 2.44. REA was attempted first: exact-hash retained-evidence search returned zero records, and the single `inspect_binary_layout` attempt was BLOCKED by unavailable caller-supplied Python dependencies (`REA_PWNTOOLS_PYTHON` unset). No REA setup was attempted.

The fallback examined all 25 ELF section headers, the complete available dynamic symbol table and both relocation sections, all 25,976 file bytes for the exact little-endian target word/byte pattern, and all 3,918 aligned A32 words (15,672 bytes) in the four file-backed executable sections. The A32 scan checked direct ARM data-processing modified immediates, literal-load references whose loaded word equals `0x1a270`, and MOVW/MOVT immediate halves that could contribute to a direct constant construction. All 349 PC-relative literal loads mapped to file-backed sections; zero resolved to the target word, and zero were unmapped. Mapping uses the containing section formula `file_offset = section_file_offset + (literal_VA - section_VA)` and verifies that the entire four-byte literal lies inside that section and the input file. Full-section disassembly was used as a mechanical scan input only; instruction interpretation is confined to the one hit window below. This does not claim completeness for indirect/dynamic references, arbitrary instruction/data-flow paths, runtime relocations, or values formed through unscanned non-A32 encodings.

## Exact section membership and address domains

`0x1a270` is inside `.bss`, section 22: `SHT_NOBITS`, ELF VA range `[0x16088, 0x1a30c)`, size `0x4284`, flags `WA`. Its displacement within `.bss` is `0x41e8`. It has no corresponding file byte and therefore no file offset. The displayed `sh_offset=0x6084` is the NOBITS section's ELF file-layout marker; it does not mean bytes for `.bss` are stored there. The final file-backed writable section ends at file offset `0x6084` / ELF VA `0x16084`; `.bss` begins at ELF VA `0x16088` and is zero-fill storage represented by memory size, not file contents.

Address domains remain separate: file offsets are the raw byte positions cited in `references.tsv`; ELF VAs are the link-time values shown by the ELF and ARM disassembly. Runtime load base/address and any Ghidra address mapping are OFFEN. No conversion to either is asserted.

## Symbols and relocations

The file has `.dynsym` with 31 entries and no `.symtab` section. The complete `.dynsym` has no entry whose `st_value` is `0x1a270`; the target is not a named exported or dynamic symbol in this ELF. `.rel.dyn` has 33 entries and `.rel.plt` has 17, 50 total. No relocation has `r_offset=0x1a270`, and no displayed relocation symbol value is `0x1a270`. These are exact table results, not claims about runtime lookup or references outside the tables.

## Raw and materialized direct-reference census

No exact four-byte little-endian encoding (`70 a2 01 00`) of `0x1a270` occurs anywhere in the file. The complete aligned A32 executable-word scan found no single data-processing modified immediate equal to the target, no PC-relative literal load whose literal word equals the target, and no direct MOVW/MOVT half pair materializing it. These negative results are limited to those explicitly scanned encodings and sections.

One direct static materialization was found at ELF VA `0x2f90`, with the immediately following store at `0x2f94` consuming the value. The window `[0x2f78,0x2fac)` shows:

| ELF VA | File offset | Bytes / instruction | Arithmetic observation |
|---|---:|---|---|
| `0x2f7c` | `0x2f7c` | `e59f33dc` `ldr r3,[pc,#0x3dc]` | A32 PC is `0x2f84`; literal address is `0x3360`. |
| `0x3360` | `0x3360` | word `0x00013438` | File-backed literal; loaded into `r3`. |
| `0x2f84` | `0x2f84` | `e08f3003` `add r3,pc,r3` | A32 PC is `0x2f8c`; `r3 = 0x2f8c + 0x13438 = 0x163c4`. |
| `0x2f88` | `0x2f88` | `e2832dfa` `add r2,r3,#0x3e80` | `r2 = 0x163c4 + 0x3e80 = 0x1a244`. |
| `0x2f90` | `0x2f90` | `e282202c` `add r2,r2,#0x2c` | `r2 = 0x1a244 + 0x2c = 0x1a270`. |
| `0x2f94` | `0x2f94` | `e584261c` `str r2,[r4,#0x61c]` | The statically materialized value is stored through the base held in `r4`. |

This proves the numeric value and its consumption by that store in the exact ELF instruction sequence. It does not establish what `r4` points to, the identity or meaning of the stored value, or an absolute memory access to address `0x1a270`. No result from IoDrvKbus was used.

## Tooling, alternative, residual uncertainty

`readelf -h -S -sW -rW`, GNU ARM `objdump -D -w` on the file-backed executable sections, a raw byte search, and a little-endian A32 immediate/literal scan were used. REA's missing Python provider was documented once and not retried. The validator rechecks the input identity, section membership, table counts/bindings, executable scan coverage, raw word census, exact instruction/literal bytes, arithmetic, required report claims, TSV rows, and the SHA256SUMS manifest.

OFFEN: runtime load base and address; Ghidra mapping; indirect or dynamically selected references; references created by other data-flow encodings or external runtime state; meaning of the stored numeric value and of the base register. Tests of runtime/device behavior were NOT_RUN.
