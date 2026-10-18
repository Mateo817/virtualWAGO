> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-326 — independent audit of WP317 first-empty insert evidence

Status: **VERIFIZIERT** for the inspected raw source words and the local, conditional branch/store deductions below. **HYPOTHESE** for the stipulated `g_memdup2` normal-return and live-state premise. WP317's 105-row-per-fixture trace is **not** a complete source-driven instruction replay: it contains gaps and inconsistent machine state. The WP317 package's default validator is read-only and passed when independently run; its separate `replay.py` is a writing generator and was not run during this audit. Test status: **PASS** for this package's read-only pin and consistency audit; **NOT_RUN** for native execution, runtime, VM, device, and network tests.

## Evidence checked

I checked WP317's 178-word source ledger against the pinned GLib ELF and its WP316-retained REA bodies: 79 words at `g_hash_table_insert`, 89 words at `FUN_000555c8`, two `g_int_hash` words, and the accepted eight-word `FUN_000cac64` caller slice. Ghidra/ELF addresses retain the stated `+0x10000` relation. The ledger and input hashes are pinned in `source-pins.tsv`; this package does not alter WP317 or its upstream evidence.

For the stipulated empty bucket `C[0]=0`, `CMP r6,#1` at `0x555e4` followed by `BLS 0x556c0` at `0x555e8` takes the empty lane and skips `0x555ec..0x5560c`. The `r7=K` write at `0x555cc` therefore remains in force. With the stipulated aliased array pointers, `SUB` at `0x55610` yields zero; `CLZ` and `LSR #5` yield discriminator 1. For distinct K and T with K<T, `CMP r7,r10` at `0x55614` sets N=1,Z=0,C=0,V=0. `MOVEQ` is skipped, `CMP r3,#0` yields 1, and `BNE` at `0x55628` reaches the `g_memdup2` call setup. The branch outcome recorded by WP317 is right, but the trace's NZCV at `0x55614` is wrong (it records N=0).

The selected local path makes the call at `0x556e0` with r0=B and r1=32. The call's target effects remain opaque. Under an explicit normal-return premise of r0=V plus the necessary live-register/frame preservation, source instructions then store V at H+0x20, K at B[0], and T at V[0], update the selected counters, skip the larger resize call at `0x55724`, and encode return value r0=1. These are conditional source effects, not allocator/copy semantics or a hash-table API contract. The selected source path does not load B[0] before the opaque call.

## Replay defects in WP317

Each fixture has 105 rows but only 104 unique PCs: `0x556e0` appears twice, once for the actual BL row and once for a synthetic opaque-return event. These are not 105 executed instruction PCs. More materially, the 8-word caller BL at `0xcac70` records next PC `0xcaa78`, while the next row is `0xcac74`. The 31 selected PCs in WP312's 77/7 arithmetic route are absent from WP317's 178-word ledger and trace. A complete selected composition would need those 31 nested instructions between the BL and caller continuation, while still treating `g_memdup2` as an opaque boundary.

WP317 also assigns r0=11 before recording the BL row at `0xcac70`; at that instruction, the incoming operands are r0=77 and r1=7, and the recorded next PC is the nested entry. The r0=11 result belongs after the nested route. At caller continuation `0xcac74`, the nested route's final `CMP 7,7` leaves N=0,Z=1,C=1,V=0, but WP317 records Z=0. The helper comparison at `0x55614` likewise has wrong N as noted above. Thus the hand-built rows do not constitute a consistent per-instruction register/flag replay.

Inspection of `replay.py` confirms it directly assigns machine state and supplies predetermined PC/event rows; it is not a decoder or source-stepper. WP317's validator checks source-PC membership and selected endpoints/branch assertions, but does not regenerate semantics or require next-PC continuity. Its three negative controls are prose/source-branch checks, not executed control traces. The reported positive final values may agree with the conditional source-store deductions, but the trace cannot substantiate full instruction-state fidelity.

## Fixture and scope qualifications

WP317's assignment stipulates B[0]=T, but both positive fixture memories initialize B[0] to `0xdead0001` / `0xdead0002`. The source path does not read B[0] before the opaque call, so this mismatch does not alter the local K/T branch analysis. It does mean the fixtures do not instantiate every stated assignment condition. The opaque call's behavior on the passed pointer remains outside this audit.

The source branch controls support only bounded conclusions: T=K clears the discriminator and avoids the g_memdup2 branch; C[0]=7 takes the occupied-slot branch; without a stipulated normal opaque return, post-call stores are not claimed. Constructor reachability, runtime table state, copy/allocation effects, API meaning, and ABI behavior remain **OFFEN** and are not inferred.

## Self-review

This is an independent static source and artifact audit, not native execution. I verified source hashes, the 178 source-word bytes, trace rows, decisive PC/flag/state discrepancies, and the 31 omitted arithmetic PCs with the read-only validator. WP317 files were not modified. Its read-only validator was run separately and passed; the writing trace generator was not invoked. Manifest validation and before/after hash inventory for WP317 inputs are recorded in the handoff to the parent reviewer.
