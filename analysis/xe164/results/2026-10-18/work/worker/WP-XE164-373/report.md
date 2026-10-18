> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-373 — independent audit of WP354/WP360 SetTime evidence

**VERIFIZIERT, bounded source arithmetic and helper paths:** Independent checks against the exact FW31 DSO confirm WP354's retained code words and literal pools, WP360's low-word SetTime multiplication and unsigned acceptance interval, the UMULL/shift/MLS quotient and remainder on selected fixtures, and the reciprocal bound over the full accepted interval. A small source-word-anchored A32 interpreter independently reproduced every recorded row in both selected local-helper traces, including predicates, NZCV, branch targets, stack save/restore, fixture reads and the conditional byte store. No arithmetic, selected helper condition, frame or memory-event mismatch was found.

**Qualification:** WP360's SetTime data/case outputs are independently recomputed here, and its recorded PCs/words, branch endpoints, stack endpoints and memory footprint are checked. Its SetTime register snapshots are not fully replayed instruction-by-instruction by this audit. WP360's `replay.py` constructs those rows through manually scripted register/flag changes, so those snapshots alone are not independent instruction-execution evidence. No specific SetTime numeric or output defect was found. **OPEN:** full SetTime trace-state replay, API/parameter/field meanings, units, runtime behavior, ABI, lifecycle, physical watchdog behavior and opaque logging effects. **PASS:** independent bounded checks in `validate.py`. **NOT_RUN:** native execution, runtime, VM, device, network.

## Evidence and method

The exact subject is FW31 `libpackbus.so.1.0.1`, 148,792 bytes, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. The frozen WP354 manifest is pinned by SHA-256 `2e79978dcbadbcaa16838a9e17ad66c9224a71d3bc1b40899155fa9d1eceac85`; the WP360 manifest by `b8771d3511fc988fee69504bdf19f76ecfaa266455adbe0f9854fdb2a664de8e`. The validator checks both upstream manifests and their files without invoking upstream code, then binds all 263 retained instruction words and 18 literal words to the raw ELF bytes.

I inspected WP360's validator and writer before using either. I did not execute its writer (`replay.py`). Its validator checks arithmetic and binds trace PC/word pairs, plus selected branch and result assertions, but does not execute the recorded instruction stream to reconstruct all register and memory snapshots. WP373 independently replays both selected helper traces from the explicit H/J word fixtures using a bounded A32 subset: each current state is advanced from the raw-word-selected instruction, with ARM conditions, flags, branch displacement, loads/stores, stack frame and return modeled. It compares all recorded registers, flags, next PCs and read/store events. This is a synthetic mathematical model, not processor execution.

For SetTime, the audit independently decodes the critical source words and immediate, recomputes each fixture from raw operands, derives flags using 32-bit ARM add/subtract rules, recomputes UMULL halves, `Q`, `MLS` remainder, scaled remainder, accepted/rejected path, and the ten successful memory-footprint rows. It also checks each trace row's PC/word binding, three invalid stop-before-BL endpoints, success epilogues, stack endpoints and no success stores on invalid paths. That establishes the selected numeric and footprint claims, but it does not authenticate every register snapshot in the SetTime trace.

## SetTime gate and arithmetic

At Ghidra `0x24cd4`, the raw word is `MUL r2,r1,r2`; its result is the low 32 bits, `N=U32(r1*r2)`. The `CMP N,#0` branch rejects zero. `CMN N,#0xc0000001` followed by `BHI` rejects unsigned values greater than `0x3fffffff`. Thus the local accepted range is `1..0x3fffffff` after multiplication has wrapped. It is not a wide-input overflow test.

For accepted `N`, source constructs `M=0x431bde83`, computes the 64-bit product with `UMULL`, shifts the high word right by 18 to obtain `Q`, then uses `MLS` for `R=N-1,000,000*Q`. The subsequent multiply by 1000 and stores match the retained cases. The exact `0xffffffff * 0xffffffff` witness wraps to 1 and takes the accepted path; `65536 * 65536` wraps to zero and takes the invalid path. The first above-range witness is rejected by unsigned `BHI`.

The whole-range quotient equality follows from the source constant. Let `K=2^50`, `d=1,000,000`, `M=0x431bde83`, and `e=M*d-K=157,376`. For every accepted `N<=0x3fffffff`, `N*e<K`. Writing `N=q*d+r` with `0<=r<d` gives `N*M/K=q+r/d+N*e/(d*K)`, where the final term is strictly less than `1/d`; therefore the fractional part cannot reach 1, and `Q=floor(N/d)`. Hence `R=N mod d`, and `R*1000 < 1,000,000,000`. This proves the local numeric relation, not the meaning of those values.

On the successful selected paths, stores match source order and values: `P+4=N`, then `P=1`, `P+8=Q`, `P+0x0c=R*1000`, then the eight-byte zero vector at `P+0x10..0x17`. Invalid zero, over-limit and null-pointer paths stop at the source instructions immediately before the opaque logging BL. The conditional invalid return depends on that call returning normally and is not an observed call effect.

## Local helper branches and effects

The complete helper is call-free over these selected routes. The bounded replay reproduces all rows in both `helper-trace.tsv` fixtures, not just their endpoint values. The `CMP` results and signed predicates match the encoded branches and conditional operations. Exact equality at 1,000,000,000 follows signed `BLE` without normalization. At +1, signed `GT` enters the difference sequence; the subsequent `CMP 1,1,000,000,000` yields `N=1,Z=0,C=0,V=0`, so `CPYLE` executes and each `ADDGT` is skipped. The first fixture then compares `J[0]=6` against normalized `r0=7`, takes signed `BLT`, increments the fixture counter from zero, and `CMP 1,0` yields carry set so `STRBCS` writes byte 1 at `H+0x28`. It returns 1 through the local pop. In the second fixture, `J[0]=0 < 7` takes the local return-0 route with no counter store. The replay confirms the recorded input reads, all state snapshots, flags, branch PCs, frame word restoration and selected memory effects.

These are conditions over stipulated fixture words and a synthetic writable frame. They establish neither actual object availability nor a caller contract. The unsigned `CS` counter predicate is distinct from the helper's signed `LE/GT/LT/GE` comparisons.

## Claim matrix

| Claim | Status | Audit result |
|---|---|---|
| Exact DSO, frozen WP354 and WP360 artifact identities | VERIFIZIERT | Hashes and raw word/pool mappings checked |
| SetTime low-word product and accepted interval | VERIFIZIERT | Independent U32 arithmetic and source NZCV/branch calculations |
| UMULL/LSR/MLS selected outputs and whole-range quotient bound | VERIFIZIERT | Independent selected-case recomputation and strict error bound |
| Selected SetTime store values/footprint and stop-before-log boundaries | VERIFIZIERT | Independent arithmetic and source/event endpoint checks; full register snapshots remain un-replayed |
| Both selected helper paths, trace registers/flags/PCs/stack and events | VERIFIZIERT | Fresh bounded source-word interpreter matched every recorded row |
| WP360 SetTime trace snapshots as a complete instruction replay | OFFEN | Writer scripts state changes; this audit does not reconstruct every SetTime transition |
| API units, field meanings, ABI, lifecycle, runtime, hardware effects | OFFEN | Not established by these local source paths |
