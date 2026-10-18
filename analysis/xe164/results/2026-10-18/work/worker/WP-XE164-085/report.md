> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-085 — Fragment at ELF VA/file offset `0x210c`

## Finding

**Status: VERIFIZIERT** for the observed instruction-level guard and return behavior and the static Init publication. **OFFEN** for the meaning of either input register and either numeric return value. No API status name or semantic function name is assigned here.

The exact byte range `0x210c..0x211f` contains five 32-bit ARM instructions (four input-sensitive compare/result instructions and one common return). The hard upper boundary is `0x2120`; no instruction at or beyond it was decoded. The conditional instructions implement this contract:

| ELF VA / file offset | Instruction | Effect / path |
|---|---|---|
| `0x210c` | `cmp r1, #0` | Sets condition flags from `r1 == 0`. |
| `0x2110` | `cmpne r2, #0` | Runs only when `r1 != 0`; then sets flags from `r2 == 0`. If skipped, flags still represent `r1 == 0`. |
| `0x2114` | `movne r0, #12` | If both `r1 != 0` and `r2 != 0`, sets return register `r0` to `12`. |
| `0x2118` | `moveq r0, #2` | If `r1 == 0` or `r2 == 0`, sets `r0` to `2`. |
| `0x211c` | `bx lr` | Returns through the link register; no branch target or behavior past this instruction is included. |

The four input combinations are fully covered by those instructions:

| `r1` | `r2` | Path through conditional operations | Return `r0` |
|---|---|---|---:|
| zero | zero | second compare skipped; `moveq` | `2` |
| zero | nonzero | second compare skipped; `moveq` | `2` |
| nonzero | zero | second compare executes; `moveq` | `2` |
| nonzero | nonzero | second compare executes; `movne` | `12` |

The caller's intended interpretation of `r1`, `r2`, `2`, and `12` is not established by this fragment. In particular, their names or meanings must not be inferred from a slot number, position, or an assumed status convention.

## Static Init publication

`readelf` identifies `IoDrvKbus_Init` at ELF VA `0x47fc` (size 3432). Only the minimal publication sequence was retained for this finding:

| ELF VA / file offset | Evidence |
|---|---|
| `0x48c4` | `ldr r3, [pc, #2696]` reads the word at `0x5354`. |
| `0x5354` | The file word is little-endian `0xffffd83c`. |
| `0x48c8` | `add r3, pc, r3`; ARM's PC value here is `0x48d0`, so the computed value is `0x48d0 + 0xffffd83c = 0x210c`. |
| `0x48cc` | `str r3, [r0, #0x54]` stores that value at byte displacement `0x54` from the pointer in `r0`. REA reports a data reference from this instruction to Ghidra address `0x1210c`. |

This binds the code address statically in Init's output data. The evidence establishes the store and its value, but not the type or semantic name of the destination field. This is static evidence; it does not show a runtime call through the stored value.

## Address spaces and byte identity

The ELF is 32-bit little-endian ARM `ET_DYN`. Its first `PT_LOAD` maps file offset `0` to ELF virtual address `0`, and `.text` likewise has `Addr=Off=0x1eb8`; therefore the fragment is file offset `0x210c` and ELF VA `0x210c`. Ghidra's measured image base is `0x10000`, mapping the same byte to Ghidra address `0x1210c`. A runtime address was not observed; for a shared object it depends on the loader's runtime mapping and is not equated here with either static address.

The source artifact SHA-256 was checked before analysis and matches the supplied value: `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`.

## Evidence and method

All evidence IDs below refer to the canonical, scope-pure `rea-evidence.json` export (3 records, 0 unknowns):

| Evidence ID | Operation | Use |
|---|---|---|
| `ev_60f4d42546dfd23dc305730552b638ed02722aab522ecfac237d909e1ad553e9` | `inspect_native_load_image` | Ghidra image base and source mapping for ELF VA `0x210c` → Ghidra `0x1210c`. |
| `ev_f526bf04c1d96157b49b038524307e578668d9804c447415685c8f8acf6570a8` | `xrefs` | Exact incoming reference to `0x1210c` from Ghidra address `0x148cc`. |
| `ev_6d9c7b739b2a48277ab93c7590d4c04598ddc372c264edb13b8dfe3edbefa147` | `inspect_native_instruction` | At `0x148cc`, REA decodes the store and records its data reference to `0x1210c`. |

The REA first attempt was `analyze_function({procedure:"0x210c"})`. Exact error, preserved here because the failed request is not an Evidence record in the export: `No procedure exists at the requested address: 0x210c; Ghidra image base: 0x10000. Choose an observed analysis address.` This is a function-boundary gap, not evidence that the bytes are absent. REA tool/provider: `rea-agents 6.5.0`, Ghidra `12.1.4`, ARM language `ARM:LE:32:v8`, compiler spec `default`; analysis profile digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

As instructed after that rejection, the bounded fallback used GNU ARM Binutils `2.44`: `arm-linux-gnueabihf-objdump -D -w -m arm --start-address=0x210c --stop-address=0x2120` for the fragment; a separately bounded Init excerpt `0x48c4..0x48cf`; `arm-linux-gnueabihf-readelf -h -l -S -sW -rW` for ELF mapping and symbols/relocations; and a four-byte read at file offset `0x5354`. No C166 decoding was used. The disassembly confirms the fragment bytes are `00 00 51 e3 00 00 52 13 0c 00 a0 13 02 00 a0 03 1e ff 2f e1` (five ARM words). No byte at `0x2120` was requested from objdump.

## Alternative explanation and remaining uncertainty

The nearest symbol annotation printed by objdump is a relative-to-symbol label, not a function entry at `0x210c`. REA's exact-address function lookup independently rejected the address. Accordingly, the verified claim is limited to the five decoded ARM instructions and the Init data publication; the fragment may be an interior block of a larger routine. Caller semantics, calling convention at this interior point, and runtime reachability remain **OFFEN**.

The verifier is a local artifact-integrity and scope check. Result: **PASS** when run as `python3 validate.py`; it checks the source and output hashes, the exact required Evidence IDs/operations, the bounded address claims, and the five instruction addresses without reading or decoding any address beyond `0x211f`.
