> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-101 — signed Table-9 result and local read-conf dispatches

## Status

**VERIFIZIERT** within the bounded static control-flow graph of the exact exported function body. Given any of the supplied raw 16-bit test values as the value loaded at `local_36`, the body takes the signed-negative arm and bypasses every local call to `FUN_00016d24`. This does not establish what the value means or whether any external or out-of-body operation is needed.

## Target and method

- Input: `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvKbus.so.0.0.1`
- SHA-256: `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`; size 38,584 bytes. The supplied identity was checked before REA analysis.
- REA operation: `open_binary`, then Ghidra `analyze_function` at exact entry `0x170a4` (file offset `0x70a4`, Ghidra load bias `+0x10000`). REA 6.5.0; Ghidra 12.1.4.
- Canonical bundle: `rea-bundle.json`; the relevant record is `ev_862e51ee495e066f738b0eed277336910e9b7b89966056746525a1524d57a6d5`. A second successful identical analysis record is retained in the bundle (`ev_2d9f4078b1dd753e58d8a4b129e7aa2b685fff9aaff4502466490f2a8bb69147`). The name-only lookup was ambiguous because it also matched a thunk; all conclusions use the exact entry address.
- Tool/provider evidence: Ghidra reports ARM little-endian 32-bit code and exact inclusive body `[0x170a4, 0x175af]`, 1,292 bytes, contiguous, containing the entry. The earlier name-only procedure `0x11dc4` is an observed 12-byte thunk to this body, not the analyzed body.
- No `objdump`/`readelf` fallback was used: REA supplied exact assembly, decompiler pseudocode, complete body range, local CFG blocks, calls and value-flow data needed for this question.

## Observations and finding

1. At `0x17330`, the body calls through the function pointer loaded from `[iVar9 + 0x70]`, passing the string `"libpackbus_read_table_9"`, an output buffer, `uVar3 + 1`, and the address of `local_36`. This is the Table-9-result-producing call site observed in this body. No table/provider implementation was inspected.
2. At `0x17338`, `ldrsh r2, [sp,#0x32]` loads `local_36` with signed 16-bit extension. The subsequent `cmp r2,#0` at `0x1734c` and `bge 0x17384` at `0x17350` implement the split: signed values `>= 0` branch to the read-conf path at `0x17384`; signed values `< 0` fall through to `0x17354`. The decompiler expresses the same condition as `if ((short)local_36 < 0)`.
3. The fall-through block `0x17354..0x17367` calls `snprintf` at `0x17364` with format `"%04X_075"`; control then reaches `0x17368` and the loop continuation. Within this export, this path does not reach any `FUN_00016d24` call.
4. The nonnegative arm contains three unconditional calls to `FUN_00016d24` at `0x17398`, `0x173b4`, and `0x173d4`. A fourth call is at `0x1740c`, after `FUN_00017ffc` at `0x173e4` and a separate test: `uxth r1,r1` (`0x173e8`), `cmp r1,#9` (`0x173ec`), and `bne 0x17414` (`0x173f4`). Thus, even on the nonnegative arm, the fourth call is conditional on the low 16 bits of that helper's returned `r1` being exactly `9`. No helper body was used to infer further semantics.
5. For the requested arithmetic-only raw test values:

   | Raw uint16 | Unsigned value | Signed int16 | `ldrsh` / branch result | Three calls at `0x17398/0x173b4/0x173d4` | Conditional call at `0x1740c` |
   |---|---:|---:|---|---|---|
   | `0x8801` | 34,817 | -30,719 | negative; `bge` not taken | Not-reachable | Not-reachable |
   | `0x8802` | 34,818 | -30,718 | negative; `bge` not taken | Not-reachable | Not-reachable |
   | `0x9001` | 36,865 | -28,671 | negative; `bge` not taken | Not-reachable | Not-reachable |
   | `0x9002` | 36,866 | -28,670 | negative; `bge` not taken | Not-reachable | Not-reachable |

   These are arithmetic test inputs only. No module identity or protocol meaning is assigned.

## Reachability answer (bounded to this body)

Assuming the Table-9 call at `0x17330` supplies the stated raw value to `local_36`, the signed comparison at `0x17350` makes the signed-negative arm **Must-reachable** for each test value. The four body-local `FUN_00016d24` sites at `0x17398`, `0x173b4`, `0x173d4`, and `0x1740c` are each **Not-reachable** for each test value in the observed local CFG. None is classified May-reachable on these fixed values. The Table-9 call at `0x17330` itself is reached before the comparison when the loop has an item and reaches block `0x17310`.

Consequently, whether one of those local calls is needed *for these values within this exact exported body's path* is statically decidable: none is executed on that path. This says nothing about other functions, hidden effects, helper implementation behavior, actual runtime values, or a broader system-level requirement.

## Alternative explanation and residual uncertainty

The signed-negative arm could be formatting or classifying a special high-bit value, or could be an error/reporting path. Those are plausible interpretations of the branch and format string, not verified semantics. Table-9/provider code, local helper bodies, and external consumers are excluded. Ghidra CFG and pseudocode are static analysis evidence; they do not demonstrate that a runtime call returns any supplied test value. No claim is made that `FUN_00016d24` is universally equivalent to a named API beyond its role as the body-local repeated call site under investigation.

## Evidence and verification status

- Body boundary, pseudocode, assembly, CFG and direct callees: REA evidence record `ev_862e51ee495e066f738b0eed277336910e9b7b89966056746525a1524d57a6d5` in the canonical bundle.
- Semantically relevant assembly locations: `0x17330`, `0x17338`, `0x1734c`, `0x17350`, `0x17354`, `0x17364`, `0x17384`, `0x17398`, `0x173b4`, `0x173d4`, `0x173e4`, `0x173e8`, `0x173ec`, `0x173f4`, `0x1740c`.
- Validator: `validate.js` checks bundle identity, body bounds, signed-load/branch instructions, call sites, and the signed arithmetic outcomes above. **PASS** when run against `rea-bundle.json`.
- Hash manifest verification: `sha256sum -c SHA256SUMS` — **PASS** after manifest generation.
- Remaining test status: `NOT_RUN` (no runtime or hardware tests requested or performed).
