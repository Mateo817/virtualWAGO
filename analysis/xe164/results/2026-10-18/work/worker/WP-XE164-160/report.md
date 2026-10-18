> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-160 — Dynsym `CMUtlSafeStrCpy` at ELF VMA `0x00304760`

## Ergebnis

**VERIFIZIERT:** The exact Dynsym entry is `CMUtlSafeStrCpy`, `FUNC GLOBAL DEFAULT`, size 132 (`0x84`) bytes. Its complete scope is `[0x00304760,0x003047e4)`, with the last included instruction at `0x003047e0`. The adjacent `CMUtlSafeStrCpy2` begins at `0x003047e4` and is excluded. The first `PT_LOAD` maps file offset 0 to ELF VMA `0x00010000`, so this body's file range is `[0x002f4760,0x002f47e4)`. `codesys3` is ELF32 little-endian ARM, type `EXEC`; no runtime address was observed or inferred. This claim is based on the bounded instruction and ELF-table evidence.

**VERIFIZIERT:** Entry values are denoted `a0`, `a1`, and `a2` for `r0`, `r1`, and `r2`. The function tests all three for zero; if any is zero it returns `2`. On the nonzero path it saves `a0/a1/a2` in `r4/r6/r5`, respectively. At the second direct call, the visible setup is `r0=a0`, `r1=a2`, and `r2=min_unsigned(a1,L+1)`, where `L` is only the raw `r0` value returned from the first direct call and `L+1` is 32-bit addition. The function then directly writes byte `0x00` to `a0+a1-1` (32-bit address arithmetic). Its own return setup is `15` when unsigned `a1 < L+1`, otherwise `0`. These effects are instruction-bound to the body.

**VERIFIZIERT:** The two direct branch-with-link instructions target VMA `0x0007bde0` (objdump label `strlen@plt`) and `0x0007b804` (label `strncpy@plt`). At the first call, `r0=a2`; the body consumes post-call `r0` only to form `L+1`. At the second call the register setup described above is visible, but the return value is overwritten on both branches. Symbol labels do not establish callee behavior: neither callee's memory effects nor its return semantics are claimed. In particular, the direct byte store at `0x003047d4` is established by this function's own instruction, independent of any callee label.

## Complete instruction and CFG tables

`instructions.tsv` lists every 4-byte instruction in the 132-byte Dynsym extent, in order, with ELF VMA, file offset, exact bytes as laid out in the file, decoded instruction, and its local role or edge. `cfg.tsv` lists all five local blocks and their branch/return edges. The body is straight-line apart from the invalid-input branch, then two call boundaries, followed by a conditional return-value selection.

The entry comparisons and conditional moves implement this local gate:

| Input condition | Local result |
|---|---|
| `a1==0` | Does not compare `a2`; candidate-valid flag remains zero |
| `a1!=0` and `a2==0` | Candidate-valid flag is zero |
| `a1!=0` and `a2!=0` | Candidate-valid flag becomes one |
| `a0==0` | Clears candidate-valid flag |
| all three nonzero | Branch to first direct call |

The result after the gate is therefore `r0=2` if any input is zero; otherwise the body follows the call path. No caller-facing role beyond these observed register and address uses is inferred.

## Direct writes

`writes.tsv` enumerates the complete local write set within the extent:

| VMA | Address | Value |
|---:|---|---|
| `0x0030476c` | `[entry_sp-32, entry_sp)` | Saved `r4,r5,r6,r7,fp,ip,lr,pc` words |
| `0x003047d4` | `a0+a1-1` | byte `0x00` |

There are no other explicit store instructions in the extent. The calls may have effects, but those are outside the analyzed body and remain **OFFEN**. A readable/writable mapping for the computed address is not established here.

## Calls, comparisons, and returns

At `0x003047a8`, immediately before the call, visible core-register state is `r0=a2`, `r1=a1`, `r2=a2`, `r3=1`; only `r0` is described as an argument candidate by the call label, and the full caller-visible register state is retained in `calls_returns.tsv`. The returned `r0` is read at `0x003047b0` and incremented by one into `r7`. The increment is 32-bit; wraparound is possible and no bounds check or overflow branch follows it.

At `0x003047b8`, `cmp r6,r7` compares unsigned `a1` against `L+1`. `movcc` at `0x003047c0` selects `a1` if lower; otherwise `movcs` at `0x003047c4` selects `L+1`. Those instructions establish the exact `r2` value immediately before the call at `0x003047c8`. `r3` there is not established locally after the first call and is recorded as unknown. The same comparison is repeated at `0x003047cc`; `strb` at `0x003047d4` is unconditional on this valid path. Then `movcc` yields return `15` for `a1<L+1`; `movcs` yields return `0` for `a1>=L+1`. The invalid path returns constant `2` at `0x003047a0`.

These are exact machine-level comparisons and register values. No string length, copy, termination guarantee, or API contract is inferred from names of direct-call targets.

## E-XE164-177 caller substitution

Separately from the callee-body evidence, substitute the caller-visible values given for E-XE164-177: `a0=fp-1324`, `a2=default-path address`, and `a1` remains unknown in the supplied context. The body then prepares the first call with `r0=default-path address`; at the second call it prepares `r0=fp-1324`, `r1=default-path address`, and `r2=min_unsigned(a1,L+1)`. Its direct byte write is at `fp-1324+a1-1`, and its local result comparison uses unknown `a1` versus `L+1`. This is a register substitution only; it does not expand or validate the caller, define `a1`, prove the default path's contents, or establish either callee's memory effects.

## Evidence, method, and limits

- Input: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`, 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.
- Prior report identities were checked: WP-XE164-157 `report.md` SHA-256 `25db8b4ad47baa009de73d0dd2da5648d7cc78d31149f7544646cd60beb1425d`; WP-XE164-153 `report.md` SHA-256 `fab40a1259ae5fe2c9a0d3e692f61f6c60486353619fab5a71bf6bc420b39489`.
- REA-first result and evidence gap are recorded in `rea_evidence.txt`. The retained exact-hash records inspected do not contain a dossier for this function body; no fresh Ghidra import was attempted because the same-hash autoanalysis hang is documented in WP-XE164-157 and re-import is expressly excluded here.
- Bounded fallback: GNU `readelf` for the Dynsym entry and program-header mapping; `/usr/bin/arm-linux-gnueabihf-objdump` for only `[0x304760,0x3047e4)`; `od` for exact little-endian instruction bytes at the mapped file offset. No Rizin run was needed. Tool versions are recorded in `tool_versions.txt`.
- VMA and file offsets are distinct in all tables. Runtime address is **OFFEN**. Dynsym bounds and byte coverage are **VERIFIZIERT**. Local branch, call setup, direct writes and return register setup are **VERIFIZIERT** by the listed instructions. Callee effects, semantic interpretation of `L`, caller `a1`, memory validity, aliasing, and runtime behavior are **OFFEN**. REA body dossier is **BLOCKED** by the documented import hang; no attempt was repeated.
- No VM, network, device, hardware, download, or upload activity occurred. Neighbor, caller body, and direct callee bodies were not expanded.

Worker report; self-review only. Independent review: **NOT_RUN**. Runtime/hardware tests: **NOT_RUN**.
