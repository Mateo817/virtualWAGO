> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-399 — independent review of frozen Root WP397

**VERIFIZIERT, source-bounded:** WP397's manifest matches the requested hash. Its 283 listed words and eight literal words match the pinned FW31 object through ELF `PT_LOAD` mappings. I independently confirmed the three 12-byte initial records at ELF `0x337d0` / file offset `0x237d0`, the word-0 mapping arithmetic used by WP388, the distinct word-8 Set-description target, the local count/bounds source, and the two VST1 writeback encodings. No raw-byte or numeric contradiction was found. **OFFEN:** any complete SSC_Update execution, effects across opaque calls, runtime PLT binding, object construction/lifetime, API/ABI meaning, and physical behavior.

## Pins and checks

WP397 manifest SHA-256 is `03078c8ffaa2dbfed529166be169d35b0682dd43067c531883919e6b2b99c7ba`; its report SHA-256 is `61caec6541cb4ccb37268972ceac5f84ee3939531603a48fd1861c640036b969`. The exact `libpackbus.so.1.0.1` SHA-256 is `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. My read-only audit maps every listed code/pool word to its ELF file offset and compares all four source bytes and the decoded little-endian word. It confirms 283 total words grouped as 210 Update, 15 Set-description, 14 Get-description, two local count words plus its three-word PLT, and thirteen other three-word PLTs. WP397's own validator also passes and leaves its recorded package inventory unchanged.

The independently read raw data rows are:

| Row | Word 0 | Word 4 | Word 8 | Raw 12 bytes |
|---:|---:|---:|---:|---|
| 0 | 1 | 3 | `0x40e3` | `0100000003000000e3400000` |
| 1 | 2 | 1 | `0x44ae7` | `0200000001000000e74a0400` |
| 2 | 3 | 3 | `0x40e3` | `0300000003000000e3400000` |

The file offsets are respectively `0x237d0`, `0x237dc`, and `0x237e8`; each is exactly 12 bytes apart. With WP388's checked query equation, `mappedIndex = word0` and `L=0x4013c+(mappedIndex<<4)`, the initial rows yield query entry index 0/1/2 → mapped index 1/2/3 → `L=0x4014c/0x4015c/0x4016c`. These static initial words differ from WP388's explicit synthetic index-1 fixture that stipulated mapped index 1. WP397 correctly preserves that distinction. Word 8 is the Set-description store target; it is not the mapped index.

The two-word local count source loads numeric 3 then returns. Set-description compares its saved index against that count and stores its current second input at `tableBase + 12*index + 8` only on the in-range route; its other local return is numeric 2. Get-description subtracts one from the count and uses an unsigned lower-than branch to reject indexes above 2, otherwise loads `tableBase + 12*index + 8`; the rejected route returns zero. This proves only the selected local source behavior and not a public index contract. WP390 separately accepts Open entry index 3; that Open fact does not change Set/Get-description's local 0..2 source range.

## Update and caller relationships

Raw PC-relative literal loads/adds reproduce WP397's distinct numerical bases: `0x337d0` for the three-row table and `0x443f4` for the Update global pointer cell. WP397's eight initial branches are equality branches to the local `r0=1` return. Their checked source reads are `[S]`, `[S+8]`, `[S+0xc]`, and the separate pointer-cell words at `G+4`, `G+8`, `G+0xc`, `G+0x10`, and `G+0x14`. These are source predicates; no initialization or runtime reachability is established.

The conditional comparison with WP389 is correctly bounded. If the selected descriptor call in Update returns numeric zero and the same current instance field at `+4` still contains that value at its later null test, the source takes the error continuation before the later main body/GetCnf calls. Update does invoke an allocation-named call before that test, but neither its effect nor persistence across opaque calls follows from this review. Thus WP389's synthetic empty-`G_RAIL` GetCnf path does not establish a successful full Update path. The result depends on same-object/current-field premises after opaque calls and remains conditional.

## VST1 writeback detail

The exact words are `0xf4450a0d` at ELF `0xd8dc` and `0xf445070f` at `0xd8e0`. In the Advanced SIMD multiple-store encoding both name base register `r5`; the first has low `Rm=13`, the architectural post-index/writeback encoding, while the second has `Rm=15`, the no-writeback encoding. The retained `objdump` output independently renders the first operand as `[r5]!`. For the stated current pointer `r5=S+0x10` at the first instruction, the first instruction writes 16 bytes and advances `r5` by 16; the next writes 8 bytes at that advanced pointer without another update. The adjacent local store interval is `[S+0x10,S+0x28)`, 24 bytes. The omitted `!` in Ghidra's displayed assembly does not support a same-address overlap claim.

That span is conditional on the current `r5` value at `0xd8dc`. Two opaque calls occur between the earlier `r5` calculation and these stores, so this review does not prove that an actual composed Update execution preserves `r5=S+0x10` across them. WP397's phrasing as a current-register case and its explicit open treatment of opaque effects are appropriate; the conditional premise should remain attached to any reuse of the 24-byte result.

## Result and limits

`python3 audit.py` independently passes raw word/pool mapping, all three table rows, query arithmetic, local count/range facts, the eight null-gate branch targets, and the VST1 base/writeback fields. `python3 ../root/WP-XE164-397/validate.py` also passes its raw-source and package-inventory check. This review did not execute any target, VM, runtime, device, or native code and does not infer APIs, units, ABI, allocation behavior, or successful lifecycle semantics.
