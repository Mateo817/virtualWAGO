> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-172 — direct A32 BL callers of `CMInitComponent`

Status: **PASS (static, bounded, corrected)**. Scope is exact Dynsym `CMInitComponent` at `0x00301394`, aligned A32 immediate-BL target scan over `.init/.plt/.text/.fini`, and only effective caller windows after enforcing the target-body boundary.

Correction record: the first worker report had **SCOPE FAIL**: for `0x003018d8`, it disassembled the nominal pre-call range beginning at `0x00301888`, overlapping the excluded WP170 target body. That first version is not a valid evidence basis; its out-of-scope rows/findings are withdrawn. The corrected window is clipped to the exact target Dynsym end `0x003018b8` and begins there. The raw full-section opcode scan is unaffected.

Input: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`; 5,181,396 bytes; SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.

## Search and identity

REA ran first: Ghidra 12.1.4 bound the exact input. Exact-address `xrefs` returned `0x003018d8` and `0x0031a66c`; exact instruction inspection independently decoded both as unconditional direct `BL 0x00301394` (Evidence IDs in `rea-evidence.json`). GNU fallback was used for exhaustive section scanning because REA xrefs are an address-reference result, not an exhaustive aligned-opcode scan; no broad caller or callee analysis was run.

Raw scan definition: for every 4-byte aligned word in the file-backed executable bytes of each requested section, test A32 immediate `BL` (`cond != 0xf`, `bits[27:25]=101`, `L=1`) and compute `PC+8+sign_extend(imm24)*4`. The raw target set equals the GNU ARM objdump exact-target set. GNU objdump was invoked at discovered callsites/windows only; no bytes outside discovered windows were disassembled.

| Section | VMA | File offset | Size | SHA-256 of section bytes |
|---|---:|---:|---:|---|
| `.init` | `0x0007a9bc` | `0x6a9bc` | `0xc` | `2be5414c82be580ba17c04cb8617c597a1e9ffd563240cdd67af0d9569b37ccd` |
| `.plt` | `0x0007a9c8` | `0x6a9c8` | `0x2144` | `7314d36cf5256618a312190356ffbe477cc71aff719a5ebc60f8681970f67190` |
| `.text` | `0x0007cb10` | `0x6cb10` | `0x2c84b0` | `f794903ddb28b803728bc2d02e0a2b7b5734b4259b65109aaa972363dcecf73d` |
| `.fini` | `0x00344fc0` | `0x334fc0` | `0x8` | `39ab1abb22de080633441980e06f54fa5e8b8467b1e10ed3e702055c487f7eb3` |

Exact target Dynsym entry: `CMInitComponent`, table index 3135, FUNC/GLOBAL/DEFAULT, `st_value=0x00301394`, `st_size=0x524`, section index 14; extent `[0x00301394,0x003018b8)`. Ownership below is assigned only if the callsite satisfies the strict Dynsym extent test `[st_value,st_value+st_size)`.

| Callsite | Section | File offset | Raw opcode bytes (LE) | A32 word | Decoded target | Dynsym owner (strict extent) | Caller extent |
|---:|---|---:|---:|---:|---:|---|---|
| `0x003018d8` | `.text` | `0x2f18d8` | `adfeffeb` | `0xebfffead` | `0x00301394` | `cminitcomponent` | `[0x003018b8,0x003018e4)` |
| `0x0031a66c` | `.text` | `0x30a66c` | `489bffeb` | `0xebff9b48` | `0x00301394` | `AppLoadCIntegrationModule` | `[0x0031a628,0x0031a680)` |

Raw scan sites: 2; GNU objdump exact sites: 2; equality: **True**. REA xrefs and exact instruction results agree.

## Window instruction tables

### `0x003018d8` — `cminitcomponent`

Nominal window start: `0x00301888`. Effective window: `[0x003018b8,0x003018e8)`; clipped at target Dynsym end: `True`; SHA-256 `b2f1ebc592e809d6585d32479e99d5d5a1f58757cb149219f481ef8c2b18932f`; 12 contiguous A32 instructions; coverage validator: `True`.

| Address | Bytes (file order) | Instruction |
|---:|---|---|
| `0x003018b8` | `0dc0a0e1` | `mov ip, sp` |
| `0x003018bc` | `30d82de9` | `push {r4, r5, fp, ip, lr, pc}` |
| `0x003018c0` | `0040a0e1` | `mov r4, r0` |
| `0x003018c4` | `000090e5` | `ldr r0, [r0]` |
| `0x003018c8` | `04b04ce2` | `sub fp, ip, #4` |
| `0x003018cc` | `000050e3` | `cmp r0, #0` |
| `0x003018d0` | `0200a003` | `moveq r0, #2` |
| `0x003018d4` | `0000000a` | `beq 3018dc <cminitcomponent@@Base+0x24>` |
| `0x003018d8` | `adfeffeb` | `bl 301394 <CMInitComponent@@Base>` |
| `0x003018dc` | `040084e5` | `str r0, [r4, #4]` |
| `0x003018e0` | `30a89de8` | `ldm sp, {r4, r5, fp, sp, pc}` |
| `0x003018e4` | `0dc0a0e1` | `mov ip, sp` |

### `0x0031a66c` — `AppLoadCIntegrationModule`

Nominal window start: `0x0031a61c`. Effective window: `[0x0031a61c,0x0031a67c)`; clipped at target Dynsym end: `False`; SHA-256 `7ccffdd7f5392810854c235759f1da8cb706625d2e658ebcf23e107e4abf0aa7`; 24 contiguous A32 instructions; coverage validator: `True`.

| Address | Bytes (file order) | Instruction |
|---:|---|---|
| `0x0031a61c` | `0200a0e3` | `mov r0, #2` |
| `0x0031a620` | `1cd04be2` | `sub sp, fp, #28` |
| `0x0031a624` | `f0a89de8` | `ldm sp, {r4, r5, r6, r7, fp, sp, pc}` |
| `0x0031a628` | `0dc0a0e1` | `mov ip, sp` |
| `0x0031a62c` | `0100a0e1` | `mov r0, r1` |
| `0x0031a630` | `00d82de9` | `push {fp, ip, lr, pc}` |
| `0x0031a634` | `04b04ce2` | `sub fp, ip, #4` |
| `0x0031a638` | `08d04de2` | `sub sp, sp, #8` |
| `0x0031a63c` | `10304be2` | `sub r3, fp, #16` |
| `0x0031a640` | `0210a0e1` | `mov r1, r2` |
| `0x0031a644` | `1020a0e3` | `mov r2, #16` |
| `0x0031a648` | `8d95ffeb` | `bl 2ffc84 <CMLoadComponent3@@Base>` |
| `0x0031a64c` | `10301be5` | `ldr r3, [fp, #-16]` |
| `0x0031a650` | `010070e3` | `cmn r0, #1` |
| `0x0031a654` | `0100000a` | `beq 31a660 <AppLoadCIntegrationModule@@Base+0x38>` |
| `0x0031a658` | `000053e3` | `cmp r3, #0` |
| `0x0031a65c` | `0200000a` | `beq 31a66c <AppLoadCIntegrationModule@@Base+0x44>` |
| `0x0031a660` | `0300a0e1` | `mov r0, r3` |
| `0x0031a664` | `0cd04be2` | `sub sp, fp, #12` |
| `0x0031a668` | `00a89de8` | `ldm sp, {fp, sp, pc}` |
| `0x0031a66c` | `489bffeb` | `bl 301394 <CMInitComponent@@Base>` |
| `0x0031a670` | `0030a0e1` | `mov r3, r0` |
| `0x0031a674` | `0300a0e1` | `mov r0, r3` |
| `0x0031a678` | `0cd04be2` | `sub sp, fp, #12` |

## Window-local r0/r1 and immediate return use

| Callsite | r0 at call | r1 at call | Immediate return use |
|---:|---|---|---|
| `0x003018d8` | Fresh window-local `ldr r0,[r0]` at `0x003018c4`; the local `cmp`/conditional `moveq #2`/`beq` show the call path falls through with nonzero loaded r0. The source address register value itself is outside the permitted inference unless defined in this window, so the loaded value is described only as a load through the window-entry r0. | No r1 write in this window; value is unknown at the call. No pre-window register definition used. | At `0x003018dc`, `str r0,[r4,#4]` stores the returned r0 value. |
| `0x0031a66c` | The opaque `BL` at `0x0031a648` defines the raw return in r0. `cmn r0,#1` followed by `beq 0x0031a660` sends the -1 case around the target call; the target path therefore has raw r0 != -1. Then `cmp r3,#0` / `beq 0x0031a66c` reaches the target only when r3==0. No instruction overwrites r0 before the target BL. This is a raw value/path constraint only; callee semantics are unknown. | `r1` was written at `0x0031a640`, invalidated by the opaque call at `0x0031a648`, and is not rewritten before the target call; its value is unknown. | At `0x0031a670`, `mov r3,r0`, then at `0x0031a674`, `mov r0,r3`. `0x0031a678` adjusts sp. The actual return instruction is at the exclusive window boundary and was not decoded. |

These statements use only writes and calls visible inside each effective window. Values in r0–r3 are treated as invalid immediately after any opaque `BL`; no register definition before the effective window start is consulted. The branch/call relationship is static evidence, not proof of runtime reachability.

## Method, versions, status, alternatives, and uncertainty

- REA: Ghidra 12.1.4; profile digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Direct xrefs plus exact instruction inspection; Evidence IDs are recorded in `rea-evidence.json`.
- Fallback: GNU readelf / GNU ARM objdump 2.44. Raw A32 scan and GNU exact target set agree: **True**. Python 3 was used only for deterministic ELF32 section extraction, immediate-target arithmetic, bounded objdump parsing, report generation, and validation.
- Alternative explanation: an exact direct callsite can be conditionally reachable or unreachable in a particular execution. This inventory establishes static A32 BL encodings and the exact target only; it does not establish execution.
- Residual uncertainty: indirect transfers, Thumb code, runtime control flow, and behavior of the target function are outside scope. No ABI/API/structure meaning is inferred. Ghidra's instruction procedure attribution is retained as corroboration; caller ownership is taken only from Dynsym extents.
- Validator: `validate.py` rejects a changed input hash/size, stale scan record, nonmatching site sets, altered target, nonstrict Dynsym ownership, gaps/overlaps, bad window hashes, any first-window row before `0x003018b8`, stale key-branch/register facts, or a site-2 r0 claim that says unknown.

## Checksums

`SHA256SUMS` covers all deliverables except itself. Validator output: PASS.

## Deliverables

- `scan.json`: exact ELF sections, target Dynsym record, raw and objdump site sets, all window instructions and hashes.
- `rea-evidence.json`: REA evidence identifiers and exact instruction observations.
- `scan.py`, `validate.py`, `render_report.py`: reproducible scanner, bounded validator, and report renderer.
