> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-158 — bounded call, branch, and caller-store paths

## Result

**VERIFIZIERT (instruction/dataflow):** Within VMA `[0x0033F870, 0x0033F994)`, the code calls the symbol `CMUtlStrIStr` with `r0=fp-300`, first `r1=r4`, then conditionally `r1=r8`. If the first call's `r0` is zero, control tests three bytes addressed from `fp-300`; if nonzero, a second call is made, and its zero result goes directly to `0x33f8b8`, while its nonzero result falls through to the byte tests (`ldrh == 0x696c`, then byte `== 0x62`). Mismatch branches to `0x33f854`. At `0x33f8b8`, the caller sets up a call named `strcpy` with `r0=fp-556`, `r1=fp-297`; the body and memory effect are not established. It then calls `strstr` with `r0=fp-556`, `r1=r4`; the caller writes byte zero to the address held in `r0` after that call. It next calls `CMUtlStrICmp` with `r0=fp-556`, `r1=fp-812`, then branches based on the post-call `r0` value.

The range does **not** establish the runtime contents of `r4`, `r8`, or `fp-812`. Two nearby file-backed objects requested as candidates contain `.so\0` and `.so.\0`, but no instruction in this range materializes either address or proves that either object is passed in `r4` or `r8`. Therefore those bytes are reported as exact candidate data, not asserted as the two filter needles.

After the call at `0x33f8e4`, the caller compares its post-call `r0` with zero. On the zero path, the caller reads `[r7]` when `r7!=0`, calls `strlen` with `r0=fp-556`, compares `r8` to the post-call `r0`, and uses that value to set up later calls named `memcpy` or `strncpy`. It directly stores the saved post-call value through `[r7]` only on the `memcpy` call path. When `r7==0`, it calls `strcpy` with `r0=[fp-1368]`, `r1=fp-556`. These are callsite arguments and direct caller stores only; no callee memory effect or destination termination is established. Exact instructions and bytes are in `instructions.tsv` and `disassembly.raw.txt`.

## Input identity and method

| Item | Result |
|---|---|
| Target | `WP-XE164-112/hit_files/usr/bin/codesys3` |
| Size / SHA-256 | 5,181,396 bytes / `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` — PASS |
| Prior WP156 report SHA-256 | `4034de59acf2ef4106962116b02b4ee606bbc92d482c523b2fca040be7c49191` — PASS |
| Prior WP156 instructions SHA-256 | `a938f66ee530f4fb12647bd0466c91be340634e1e73da8545892697ad6404159` — PASS |
| Disassembly / ELF mapping | GNU ARM objdump, bounded start `0x33f870`, exclusive stop `0x33f994`; every decoded word checked against file bytes at `file_offset = VMA - 0x10000`. GNU readelf `-lW` shows the first `PT_LOAD` at file offset `0`, VMA `0x10000`, file size `0x3a0340`; both candidate VMAs lie inside it and map to the listed file offsets. |
| REA | REA 6.5.0 exact-target retained-record query: zero records, zero matching evidence IDs; no binary opened and no Ghidra import repeated |
| Evidence class | Worker analysis; no independent review |

WP156 instructions stop at `0x33f86c`, and its report hash matches the supplied identity. WP156 was used only to confirm adjacent bounded evidence identity; no pre-range code is expanded here. The bounded disassembly has 73 contiguous 4-byte ARM instructions, from `0x33f870` through `0x33f990`. ELF VMA and file offset are distinct; runtime relocation/loading is not analyzed.

## Exact referenced candidate data

The requested candidate VMAs were read directly from the file-backed load image. Bytes include the NUL terminator.

| VMA | File offset | Bytes | Exact ASCII | Scope result |
|---:|---:|---|---|---|
| `0x003a9750` | `0x00399750` | `2e 73 6f 00` | `.so\0` | File-backed object verified; no direct address materialization or use proven in this instruction range |
| `0x003afe7c` | `0x0039fe7c` | `2e 73 6f 2e 00` | `.so.\0` | File-backed object verified; no direct address materialization or use proven in this instruction range |

## Filter and comparison mechanics

`fp` denotes `r11`. The following are mechanical instruction effects; register/string meanings outside the listed addresses are unknown.

| VMA(s) | Exact operation and effect |
|---|---|
| `0x33f870..0x33f878` | `r1=r4`; `r0=fp-300`; `bl CMUtlStrIStr`. On return `r0` is tested at `0x33f880`. |
| `0x33f880..0x33f88c` | If first return is zero, branch to `0x33f898`. Otherwise set `r0=fp-300`, retain `r1=r8` (set at `0x33f87c`), and call `CMUtlStrIStr` again. |
| `0x33f890..0x33f894` | If second return is zero, branch to `0x33f8b8`; if nonzero, fall through to the prefix test. |
| `0x33f898..0x33f8a8` | Load halfword `[fp-300]`; compare with immediate `0x696c`; if unequal branch to `0x33f854`. |
| `0x33f8ac..0x33f8b4` | Load byte `[fp-298]`; compare with immediate `0x62`; if unequal branch to `0x33f854`. Together with the prior halfword compare, the three checked bytes are `6c 69 62` in memory (`lib`). |
| `0x33f8b8..0x33f8c4` | Set `r1=fp-296`, then subtract one to `fp-297`; set `r0=fp-556`; call target is named `strcpy`. Source argument address is three bytes after `fp-300`; callee memory effect is unknown. |
| `0x33f8c8..0x33f8d0` | Call target is named `strstr`, with `r0=fp-556`, `r1=r4`; callee contract is unknown. |
| `0x33f8d4..0x33f8dc` | Set `r3=0`; set `r1=fp-812`; execute `strb r3,[r0]`, directly writing one zero byte at the address value in `r0` after the preceding call. No guard on that value is visible before the store. |
| `0x33f8e0..0x33f8e4` | Set `r0=fp-556`; call target is named `CMUtlStrICmp`, with `r1=fp-812`; callee contract is unknown. |
| `0x33f8e8..0x33f8ec` | Compare post-call `r0` with zero; if nonzero, branch to `0x33f854`; zero falls through. |

Boolean branch form for reaching `0x33f8b8`: `first_call_r0 == 0` reaches the `lib` byte test; `first_call_r0 != 0 && second_call_r0 == 0` bypasses that byte test; `first_call_r0 != 0 && second_call_r0 != 0` reaches the byte test. After the subsequent `CMUtlStrICmp` callsite, post-call `r0==0` falls through and nonzero branches to `0x33f854`. These are branch conditions on register values, not asserted callee semantics.

This establishes the visible argument and branch mechanics, but not a natural-language filename policy: dynamic values and callee contracts are unknown, and runtime reachability is not observed. The `lib` byte test is literal and byte-exact. No meaning is inferred from symbol names.

## Call arguments and caller-side stores

| VMA(s) | Branch / write effect |
|---|---|
| `0x33f8f0..0x33f8f4` | If `r7==0`, branch to `0x33f960`; otherwise load `r8=[r7]`. |
| `0x33f8f8..0x33f900` | Set `r0=fp-556`; call target is named `strlen`; after return, caller uses `r0`. Callee contract is unknown. |
| `0x33f904..0x33f90c` | Compare unsigned `r8` with post-call `r0`; move that value to `r4`; `bcc 0x33f970` when unsigned `r8 < r0`. |
| `0x33f910..0x33f91c` | Set `r2=post-call r0+1`; call target is named `memcpy`, with `r0=[fp-1368]`, `r1=fp-556`, and `r2=post-call r0+1`. Callee memory effect is unknown. |
| `0x33f920` | Directly store `r4` through `[r7]`; `r4` was loaded from post-call `r0` at `0x33f908`. No semantic meaning for this value is established here. |
| `0x33f924..0x33f928` | Store zero to local `[fp-1352]`; this is not a store through `r7`. |
| `0x33f960..0x33f968` | Set `r0=[fp-1368]`, `r1=fp-556`; call target is named `strcpy`. This path is taken when `r7==0`; this range has no store through `r7` on this path. Callee memory effect is unknown. |
| `0x33f970..0x33f97c` | Branch path with unsigned `r8 < post-call r0`; call target is named `strncpy`, with `r0=[fp-1368]`, `r1=fp-556`, `r2=r8`. Callee memory effect is unknown. |
| `0x33f980` | Branch to the direct local-zero store at `0x33f924`; this path skips the direct store through `r7` at `0x33f920`. This code range contains no later explicit destination-byte store on this path. Whether the callee writes or terminates the destination remains unknown. |
| `0x33f92c..0x33f930` | Call `SysDirClose(r0=r6)`; callee body excluded. |
| `0x33f934..0x33f944` | Load local `[fp-1352]`, compare with zero, store it to `[fp-1360]`; if nonzero branch to `0x33f650`, otherwise unconditional branch to `0x33f7e4` (outside range). |
| `0x33f948..0x33f95c` | Separate branch target: set `r2=entry r0+1`; call target is named `memcpy` with `r0=[fp-1368]`, `r1=fp-300`, `r2=entry r0+1`; then directly store `r4` through `[r7]` and branch outside to `0x33f7c8`. Entry `r0` and `r4` are inherited and unknown here. Callee memory effect is unknown. |
| `0x33f984..0x33f990` | Separate branch target: call target is named `strcpy` with `r0=[fp-1368]`, `r1=fp-300`, then branch outside to `0x33f7c8`. Callee memory effect is unknown. |

All call bodies and their memory/return contracts are excluded. For every callsite, this report records the symbol label shown by the disassembler and the argument-register values set by caller instructions. Post-call register tests and direct caller stores are separately identified; no callee memory effect, copying, comparison behavior, or termination behavior is asserted from an export name.

## Bounded CFG and outside targets

The range entry can be reached by fallthrough from `0x33f86c`; the predecessor is not expanded. It can also be reached by the in-range unconditional branch at `0x33f850`. Direct branches from this range to earlier/outside addresses are recorded without expanding their targets:

| Source | Edge / condition | Target | Status |
|---:|---|---:|---|
| `0x33f884` | `beq` when first `StrIStr` result is zero | `0x33f898` | In range |
| `0x33f894` | `beq` when second `StrIStr` result is zero | `0x33f8b8` | In range |
| `0x33f8a8`, `0x33f8b4`, `0x33f8ec` | `bne` from prefix or final compare check | `0x33f854` | Outside range; branch rejoins prior code, not expanded |
| `0x33f8f4` | `beq` when `r7==0` | `0x33f960` | In range |
| `0x33f90c` | `bcc` when unsigned `r8 < post-call r0` | `0x33f970` | In range |
| `0x33f940` | `bne` when local `[fp-1352] != 0` | `0x33f650` | Outside range; backedge not expanded |
| `0x33f944` | unconditional branch | `0x33f7e4` | Outside range; not expanded |
| `0x33f95c`, `0x33f990` | unconditional branch | `0x33f7c8` | Outside range; not expanded |
| `0x33f96c`, `0x33f980` | unconditional branch | `0x33f924` | In range |
| `0x33f850` | unconditional branch | `0x33f870` | In range; returns to window start |
| `0x33f994` | next instruction/function boundary | — | Exclusive stop; not decoded |

Adjacent prior WP-XE164-156 bounded evidence records these incoming cross-window targets; the source instructions are not re-decoded or expanded here: `0x33f79c -> 0x33f984`, `0x33f7b4 -> 0x33f948`, and the block ending at `0x33f86c` branches to `0x33f92c`. These are additional entry edges into the separately listed in-range blocks. WP156 also records an in-range predecessor `0x33f850 -> 0x33f870`.

Call targets are not CFG-expanded. Calls in this range and visible register arguments are:

| Callsite | Target | Visible arguments at call entry |
|---:|---|---|
| `0x33f878` | `CMUtlStrIStr` | `r0=fp-300`, `r1=r4` |
| `0x33f88c` | `CMUtlStrIStr` | `r0=fp-300`, `r1=r8` |
| `0x33f8c4` | `strcpy` | `r0=fp-556`, `r1=fp-297` |
| `0x33f8d0` | `strstr` | `r0=fp-556`, `r1=r4` |
| `0x33f8e4` | `CMUtlStrICmp` | `r0=fp-556`, `r1=fp-812` |
| `0x33f900` | `strlen` | `r0=fp-556` |
| `0x33f91c` | `memcpy` | `r0=[fp-1368]`, `r1=fp-556`, `r2=post-call r0+1` |
| `0x33f930` | `SysDirClose` | `r0=r6` |
| `0x33f954` | `memcpy` | `r0=[fp-1368]`, `r1=fp-300`, `r2=entry r0+1` as prepared at `0x33f948` (inherited value) |
| `0x33f968` | `strcpy` | `r0=[fp-1368]`, `r1=fp-556` |
| `0x33f97c` | `strncpy` | `r0=[fp-1368]`, `r1=fp-556`, `r2=r8` |
| `0x33f98c` | `strcpy` | `r0=[fp-1368]`, `r1=fp-300` |

## Alternative explanations and residual uncertainty

**HYPOTHESE:** The candidate `.so` / `.so.` objects may be related to the dynamic values in `r4` or `r8`, but this range does not establish any pointer binding. The report makes no claim about what the named callees do with their arguments.

**OFFEN:** Runtime values and provenance of `r4`, `r8`, `r7`, `r6`, `fp-812`, `fp-1368`, and the frame buffers; whether post-call `r0` at the `strstr`-labelled callsite is a valid address on reachable paths; actual execution/reachability; memory aliasing; stack/callee effects; whether candidate strings are used by this function; VMA-to-runtime relocation. Function naming is not used as semantic evidence.

## Tools, validator, and package status

Tool versions are recorded in `tool-versions.txt`. `generate.py` reproduces the bounded raw disassembly and data bytes after exact-hash assertions. `validate.py` checks input identity, 73 contiguous in-range instruction words against input file bytes, and both exact candidate data objects.

| Check | Status | Result |
|---|---|---|
| Input size and SHA-256 | PASS | Exact specified target |
| WP156 report and instructions identities | PASS | Both supplied SHA-256 values match |
| Instruction bounds and bytes | PASS | 73 words; `[0x33f870,0x33f994)` only |
| Candidate objects | PASS | Exact file-backed bytes and NUL terminators |
| Bounded static CFG/dataflow | VERIFIZIERT | Edges and writes listed above; runtime path not claimed |
| REA matching evidence | NOT_RUN | No matching retained record; REA evidence gap is explicit |
| Runtime/VM/device/hardware | NOT_RUN | Outside task scope |
| Independent review | NOT_RUN | Worker report only |
| Final validator and manifest | PASS | See `validator-result.txt` and `SHA256SUMS` |

Residual limitations: dynamic input strings, callee implementations/effects, and execution have not been established. No instructions before `0x33f870`, at/after `0x33f994`, or inside callees were expanded.
