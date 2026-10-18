> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-190 report

## Result

**VERIFIZIERT (bounded raw scan):** The exact input is ELF32 little-endian ARM, 25,976 bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. A complete aligned A32 B/BL scan of all four file-backed `SHF_EXECINSTR` sections examined 3,918 words and found exactly two transfers to ELF VA `0x2ddc`:

| Site | Encoding | Word | Target | Fixed window (section-clipped) |
|---|---|---|---|---|
| `.text+0x29ac` = `0x33e0` | `B` | `0xeafffe7d` | `0x2ddc` | `[0x33b0,0x33f0)` |
| `.text+0x2d88` = `0x37bc` | `BL` | `0xebfffd86` | `0x2ddc` | `[0x378c,0x37cc)` |

**VERIFIZIERT (within those windows only):** Neither fixed window contains an `r4` write, load, or move, so neither exposes an `r4` definition. In the first window, the visible path immediately before the transfer is `mov r1,r0; add r0,r12,#20; B 0x2ddc`; the preceding visible guard is `cmp r0,r2; bne 0x33e4`. In the second, the immediately preceding instructions are `str r3,[r5,#16]; add r3,sp,#92; BL 0x2ddc`; the window also shows the subsequent `ldr r3,[sp,#92]` and `cmp r3,#0`. These are instruction observations only; no callee effect is inferred.

## Complete executable-section coverage

The raw scanner selects every section header with `SHF_EXECINSTR` set and `SHT_NOBITS` clear, validates each file range, then checks each 4-byte-aligned ELF VA whose full word lies in the section. It applies the A32 B/BL encoding mask (bits 27:25 = `101`, condition field other than `1111`) and computes `site + 8 + SignExtend(imm24 << 2)` modulo 32 bits. No code/function boundaries or transfer destinations were followed.

| Section | ELF VA range | File range | Bytes | SHA-256 |
|---|---:|---:|---:|---|
| `.init` | `[0x948,0x954)` | `[0x948,0x954)` | 12 | `a30ad5b1b49e3b6d7751749a7051dbbb5e65b58c3de6fe5dea5767e4d9226f24` |
| `.plt` | `[0x954,0xa34)` | `[0x954,0xa34)` | 224 | `14ad36204d1390674e00da0927202cbe85cd6f17f58187ba31df02e49c35594e` |
| `.text` | `[0xa34,0x4678)` | `[0xa34,0x4678)` | 15,428 | `4739c5f5d2abd2d515ba9bed1859284ba718c78c1cea0024a17f5b56f38a6fe9` |
| `.fini` | `[0x4678,0x4680)` | `[0x4678,0x4680)` | 8 | `39ab1abb22de080633441980e06f54fa5e8b8467b1e10ed3e702055c487f7eb3` |

The enumerated section lengths total 15,672 bytes and contain 3,918 aligned words. No executable file-backed section was omitted by the section-flag/type rule. Executable `SHT_NOBITS` is excluded because it has no file-backed bytes to scan.

## Fixed-window evidence

The only disassembly requests were GNU `arm-linux-gnueabihf-objdump` over `.text` at `[0x33b0,0x33f0)` and `[0x378c,0x37cc)`. The returned output begins and ends at those requested addresses. Visible words/instructions in those windows contain no `r4` operands. `callers.tsv` records each hit and the bounded `r4` result. No disassembly or semantic interpretation of the body at `0x2ddc` was performed.

The first excerpt begins with a word decoded as an instruction (`0x00001d1f` at `0x33b0`) and contains literal-looking data at `0x33ec`; this is why the conclusion is phrased as what the bounded disassembly visibly shows, not as a complete path or function-level dataflow claim. The target-body candidate `0x2ddc` remains **OFFEN** as a FunctionManager-qualified entry.

## Evidence provenance and alternative explanation

REA same-hash evidence lookup (`get_evidence_bundle`, filtered by the exact SHA-256) returned 0 retained records (0 matching records; 0 unknown revisions). This is the single documented prior-evidence gap; the requested raw scan and bounded GNU objdump fallback were then used.

An alternative explanation consistent with these observations is that any relevant `r4` value was established before the fixed window or is irrelevant to these paths; the windows alone cannot distinguish those possibilities. The direct `B` site and `BL` site establish only machine-encoded transfer targets. They do not establish caller ownership, function boundaries, the target's role, or any behavior at `0x2ddc`.

## Uncertainty and exclusions

- **OFFEN:** Whether `0x2ddc` is a FunctionManager-qualified function entry.
- **OFFEN:** Any `r4` definition/use outside each prescribed window, including earlier control-flow predecessors.
- **OFFEN:** Caller ownership, whole-function dataflow, destination behavior/effects, API/ABI/structure meaning, and runtime behavior; these were outside scope and not examined.
- No indirect transfers were searched. No claim is made about other transfer forms or non-A32 interpretations.
- No REA native import, Ghidra import, device, VM, network, or target execution was used.

## Tools and validation

- `readelf -h` and `readelf -SW`: ELF identity and section inventory.
- `sha256sum`: exact artifact identity.
- `validate.py`: standalone Python standard-library ELF32 section-header parser, per-section hashes, exhaustive aligned raw A32 B/BL target arithmetic, identity and coverage output. Run: `python3 validate.py`.
- `arm-linux-gnueabihf-objdump -d -M reg-names-std -j .text --start-address=... --stop-address=...`: two clipped hit-window views only.
- Tool versions observed: GNU Binutils `objdump` 2.44, GNU `readelf` 2.44, Python 3.13.5.
- **Tests: PASS** — `validate.py` confirmed the expected input size/hash, four executable file-backed sections, 3,918 aligned words, and exactly two target hits. Both disassembly ranges were bounded to the prescribed windows.
- Scope: **PASS** — no overbroad disassembly output was requested or returned.

`SHA256SUMS` covers all deliverable files except itself. The target ELF is not copied into this output directory.
