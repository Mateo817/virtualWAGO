> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-089 — bounded static observation

## Conclusion

Status: VERIFIZIERT — the bytes at ELF VA/file offset `0x33b0` are decoded as an ARM instruction at Ghidra address `0x133b0`. Ghidra’s exact-address reference result for that address is `0x148c0`. In the containing procedure `IoDrvKbus_Init`, the bounded sequence at `0x148b8/0x148bc/0x148c0` loads the signed PC-relative literal `0xffffeaec`, adds it to ARM PC (`0x148c4`) to form `0x133b0`, then stores that value through `[r0,#0x44]`. This is a minimal, address-bound publication of the candidate address to the observed destination. The destination has no inferred field or callback meaning.

Status: VERIFIZIERT — all 183 aligned words in the candidate interval `[0x33b0, 0x368c)` were inspected as instructions; the last instruction begins at `0x3688`. The separate 13-word literal pool occupies `[0x368c, 0x36c0)`, ending at `0x36bc`. The hard neighbor at `0x36c0` was not queried or decoded. The candidate has entry tests, a computed PC-relative branch dispatch, loopbacks, direct and register-indirect call sites, one observed return instruction, and a branch leaving the bounded area. Direct/indirect call targets were not inspected for semantics.

Status: OFFEN — Ghidra reports no containing procedure at `0x133b0`, so a Ghidra procedure boundary/complete function contract for this candidate is not established. The observed direct branch at `0x13464` goes to `0x12074`, outside scope; its target body is intentionally not inspected.

## Identity, scope, and address domains

Input: `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvKbus.so.0.0.1`; 38,584 bytes. SHA-256 was freshly rechecked as `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` (PASS).

| Domain | Candidate start | Candidate end | Notes |
|---|---:|---:|---|
| ELF virtual address | `0x33b0` | `0x3688` inclusive | Candidate instructions, 183 ARM words |
| File offset | `0x33b0` | `0x3688` inclusive | REA maps Ghidra `0x133b0` to file offset 13232 = `0x33b0` |
| Ghidra address | `0x133b0` | `0x13688` inclusive | Observed image base `0x10000`; not a runtime address |
| Literal pool, ELF VA/file offset | `0x368c` | `0x36bf` inclusive | 52 bytes / 13 words; no instruction interpretation |
| Runtime address | unknown | unknown | No runtime evidence collected |
| Hardware address | unknown | unknown | No hardware evidence collected |

Scope checked: candidate instructions begin at ELF VA/file offset `0x33b0` and end at `0x3688` inclusive. Literal-pool bytes occupy `[0x368c, 0x36c0)` (last byte `0x36bf`). Only the Init publication instructions required to bind `0x33b0` were additionally inspected: ELF VA `0x48b8/0x48bc/0x48c0` (Ghidra `0x148b8/0x148bc/0x148c0`), plus its literal at Ghidra `0x15350`. No instruction at or after ELF VA `0x36c0` was examined.

## Tooling and evidence

- REA: 6.5.0 (offline local artifact analysis; shipped-artifact authority).
- Provider: Ghidra 12.1.4; ARM:LE:32:v8 listing. Ghidra’s observed image base is `0x10000`.
- JVM: OpenJDK 21.0.12.1.
- No objdump/readelf fallback was used: REA decoded the bounded instruction interval, read the literal pool, mapped the file offset, returned the reference, and located the Init procedure. The Ghidra candidate-procedure association gap is reported rather than repaired with another tool.
- REA profile digest: `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Canonical REA export: [rea-evidence-bundle.json](./rea-evidence-bundle.json). It is a direct REA export; not hand-edited. The additional [rea-init-evidence-bundle.json](./rea-init-evidence-bundle.json) is the direct export of the minimal publication-only query set.

Evidence IDs below are genuine REA record IDs in those exports.

| Evidence ID | Observation |
|---|---|
| `ev_859766b7e2c7d2918651239b29ea6511e345f782e391b723e758f5d4712189d9` | Ghidra `0x133b0` → file offset 13232 |
| `ev_30bf5da4b764381919f89a0ae1f2f443b1571ee31634e8e6e21628ff998f0df7` | exact references to `0x133b0` include `0x148c0` |
| `ev_abb04a23623eeaa3c4defca4d243af449f9c8e59b3fd3fefa7adbbf218d57cf4` | Init `0x148b8`: load literal at `0x15350` |
| `ev_ad5211659338525d401d9e656fc2f0d30785468844a921f5f11c8f16aaedd1c2` | Init `0x148bc`: `add r3,pc,r3` |
| `ev_4f5dd64f03ea2a078f5da08c35b6af07987ae4fcfdb5e0477b9587d4d56c145f` | Init `0x148c0`: `str r3,[r0,#0x44]`; typed data reference to `0x133b0` |
| `ev_3df03c8f35124c83cde2a642a92a268ed2aba8a0d42769746974e8e48e007c2f` | literal bytes at `0x15350`: `ec ea ff ff` as bytes `eceaffff` (little-endian `0xffffeaec`) |
| `ev_0846d4d238b6faa89bde93745edc9888903cb8375025be9bd1c3e10c4bcff963` | `0x148c0` belongs to Ghidra procedure `IoDrvKbus_Init`, entry `0x147fc` |
| `ev_2702ba52fd4ac6c7e763e0d38bbfe9c64171367d4a67c3708ff9733d2530530c` | Ghidra does not associate `0x133b0` with a containing procedure |
| `ev_d73ec0a93e75d14e9c68e5bc21212e6568a97f300b6c1823b94fd22b3569c73d` | pool bytes `[0x1368c, 0x136c0)` (ELF VA/file offset `[0x368c, 0x36c0)`), complete 52-byte read |

The address-bound full instruction inventory (one row per word, with bytes, assembly, flow class, and per-instruction Evidence ID) is [instruction-table.tsv](./instruction-table.tsv). The pool read ends before the excluded hard neighbor. ARM PC arithmetic for the binding is `0x148bc + 8 = 0x148c4`; `0x148c4 + sign_extend(0xffffeaec) = 0x133b0`. The little-endian literal value and the observed PC-add/store chain independently agree.

## Control-flow table

This is a bounded CFG summary derived from the address-indexed instruction observations; it does not claim a complete Ghidra procedure graph.

| ELF VA | Observed control | Bounded successor(s) / effect | Status |
|---|---|---|---|
| `0x33b0–0x33d0` (inclusive) | `cmp r0,#0`; conditional `cmpne r1,#0`; conditional writes to r0; `beq 0x3428` | Entry guard selects the epilogue when the tested values compare equal; otherwise proceeds at `0x33d4`. The immediate Boolean-like values are observed, their API meaning is not. | VERIFIZIERT |
| `0x33d4–0x33f0` (inclusive) | compare/conditional branch sequence; `bhi` and `bne` | Branches to `0x3430`; other path enters the subsequent table/global driven path. | VERIFIZIERT |
| `0x3420` | `blx r4` | Register-indirect call; return continuation `0x3424`. Target semantics not examined. | VERIFIZIERT |
| `0x3428–0x342c` (inclusive) | stack restore; `ldmia ... pc` | Observed return instruction at `0x342c`. | VERIFIZIERT |
| `0x3434` | direct `bl 0x11fdc` | Direct call; target body not examined; return continuation `0x3438`. | VERIFIZIERT |
| `0x3454` | conditional branch to `0x3678` | Exit/alternate path within bounded range. | VERIFIZIERT |
| `0x3464` | unconditional branch to `0x12074` | Leaves this bounded scope; tail-vs-ordinary branch interpretation and target behavior are not asserted. No target body inspected. | VERIFIZIERT |
| `0x3484–0x34ac` (inclusive), `0x34b8` | compare/conditional branch; loop increments at `0x34a0`; back branch to `0x3450` | Loop path also branches back to `0x3468`; bounds/roles are left unnamed. | VERIFIZIERT |
| `0x34dc` | `addls pc,pc,r0,lsl #2` after compare with 3 | Computed dispatch. When LS holds it selects one of the branch words at `0x34e4/0x34e8/0x34ec/0x34f0`; when LS does not hold execution falls through to `0x34e0`. The branch words lead to `0x34f4`, `0x3500`, `0x355c`, and `0x3500`; `0x34e0` leads to `0x3568`. | VERIFIZIERT |
| `0x3514` | `blx r1` | Register-indirect call; target semantics not examined. | VERIFIZIERT |
| `0x3524,;0x352c,;0x3538` | conditional branches | Select bounded paths to `0x3588`, `0x3654`, and `0x358c`; otherwise continue sequentially. | VERIFIZIERT |
| `0x3558`, `0x3564`, `0x3584` | unconditional branches | Forward join `0x3598` or back edges to `0x3500`. | VERIFIZIERT |
| `0x35a4,;0x35b0` | conditional branches | Back edges to `0x34bc` and `0x34a0`. | VERIFIZIERT |
| `0x35c8,;0x35ec,;0x35f4` | register-indirect calls `blx r3`, `blx r3`, `blx r11` | Continuations observed; target bodies not examined. | VERIFIZIERT |
| `0x3610,;0x361c` | conditional branches | Back edge to `0x34a0`. | VERIFIZIERT |
| `0x364c` | `blx r6`; followed by branch at `0x3650` | Register-indirect call then back edge to `0x34a0`; target not examined. | VERIFIZIERT |
| `0x3658` | unconditional branch | Join at `0x358c`. | VERIFIZIERT |
| `0x3668` | `blx r3`; conditional branch at `0x3670` | Register-indirect call, then loop back to `0x35d4` or branch to `0x34a0`. Target not examined. | VERIFIZIERT |
| `0x3688` | unconditional branch to `0x34a4` | Bounded back edge. This is the last instruction; pool data begins at `0x368c`. | VERIFIZIERT |

The direct and indirect call sites observed inside the candidate are `0x3420, 0x3434, 0x3514, 0x35c8, 0x35ec, 0x35f4, 0x364c, 0x3668`. No callee bodies or meanings were analyzed.

## Minimal Init binding table

| ELF VA | Ghidra address | Bytes / instruction | Dataflow interpretation | Evidence |
|---|---:|---|---|---|
| `0x48b8` | `0x148b8` | `903a9fe5`; `ldr r3,[0x15350]` | Reads the four-byte literal at Ghidra `0x15350`. | `ev_abb04a23623eeaa3c4defca4d243af449f9c8e59b3fd3fefa7adbbf218d57cf4` |
| `0x48bc` | `0x148bc` | `03308fe0`; `add r3,pc,r3` | ARM PC is `0x148c4`; adding signed literal `-0x1514` yields `0x133b0`. | `ev_ad5211659338525d401d9e656fc2f0d30785468844a921f5f11c8f16aaedd1c2`, `ev_3df03c8f35124c83cde2a642a92a268ed2aba8a0d42769746974e8e48e007c2f` |
| `0x48c0` | `0x148c0` | `443080e5`; `str r3,[r0,#0x44]` | Stores the formed candidate address at base register `r0` plus `0x44`. The base’s origin and storage semantics are not established here. | `ev_4f5dd64f03ea2a078f5da08c35b6af07987ae4fcfdb5e0477b9587d4d56c145f` |

REA xrefs to `0x133b0` report only `0x148c0` in this observation. The instruction’s reference type is DATA (not a call). Thus the verifiable claim is an address-value store/publication, not invocation or callback semantics.

## Data-flow table

| Range / point | Observed flow | Bounded conclusion |
|---|---|---|
| `0x33b0–0x33cc` (inclusive) | tests r0; conditionally tests r1; conditional moves write 0 or 1 to r0; r8 is formed using PC-relative data from pool word at `0x368c` | Entry guard and early result shaping are observed. Argument names and full return contract are not inferred. |
| `0x33d4–0x3418` (inclusive) | r2-derived compare value, reads via r1 and r8, pool-derived values at `0x3690/94/98`, stack values | Pointer/index arithmetic and loads are visible; object/table meanings remain unnamed. |
| `0x3418–0x3420` (inclusive) | loads r4 from r3 and calls through r4 | Indirect control transfer; no target semantics. |
| `0x3430–0x3464` (inclusive) | direct call, flag tests, PC-relative materialization, stack store; branch either to bounded path `0x3678` or out-of-scope `0x12074` | Return and tail/exit decisions cannot be given higher-level meaning. |
| `0x3468–0x34b8` (inclusive) | indexed loads, compare, increments, conditional/back branches | Bounded loop/control structure observed; no item semantic naming. |
| `0x34bc–0x34f0` (inclusive) | tests loaded values and an indexed PC update, followed by branch words | Guarded computed dispatch and its branch destinations observed. |
| `0x3500–0x3584` (inclusive) | loads via pool-derived addresses, indirect call through r1; writes to stack and register-relative locations; several forward/back branches | Stores and branch flow are observed without assigning field/slot names. |
| `0x3588–0x3688` (inclusive) | additional pool-relative/indexed reads, comparisons, indirect calls through r3/r11/r6, loopbacks, and a final branch to `0x34a4` | Candidate has cyclic paths; no call target body or semantics inspected. |

Pseudocode is not used as evidence. Any source-like interpretation here is a transcription of observed instructions and bounded control-flow arithmetic.

## Alternative explanation and residual uncertainty

Alternative: the word computed at `0x148bc` and stored at `[r0,#0x44]` may be an address-valued field in a larger initialization record, table, or other opaque structure rather than a callback slot. REA marks the reference as DATA, and no use of the destination or called target was analyzed. A second alternative is that Ghidra’s missing procedure association at `0x133b0` reflects an analysis-boundary gap; a matching instruction sequence and the Init reference alone do not establish that the bytes are a standalone function entry.

Residual uncertainty: no procedure boundary or full callee/caller contract for `0x133b0`; no semantics for the direct call at `0x13434`, register-indirect calls, or branch target `0x12074`; no caller-derived proof of r0’s base/object identity; no runtime relocation/load address; no validation of execution or hardware behavior. Literal pool words are reported as bytes, not assigned names.

## Tests and validation

| Test | Status | Result |
|---|---|---|
| Input SHA-256 identity | PASS | Expected hash matches freshly computed hash |
| Candidate address coverage | PASS | Exactly 183 word-aligned decoded instruction rows from `0x33b0` through `0x3688` inclusive |
| Candidate body scope guard | PASS | Canonical bundle contains no candidate instruction outside the stated interval and minimal Init chain |
| Literal-pool boundary | PASS | Complete 52-byte read ends at `0x36bf` |
| Init address binding | PASS | Literal+ARM PC arithmetic equals `0x133b0`; store is at base+`0x44` |
| Ghidra procedure attribution query | PASS | REA explicitly reports no containing procedure; limitation is preserved |
| Runtime/hardware behavior | NOT_RUN | Explicitly out of scope |
| Reproducible validator | PASS | `python3 validate.py` |

## Output files and hashes

Files: `report.md`, `instruction-table.tsv`, `rea-evidence-bundle.json`, `rea-init-evidence-bundle.json`, `validate.py`, `SHA256SUMS`. Their SHA-256 values are recorded in `SHA256SUMS`; as usual, that manifest lists every deliverable except itself to avoid a self-referential hash. Input hash is recorded above and rechecked by the validator.
