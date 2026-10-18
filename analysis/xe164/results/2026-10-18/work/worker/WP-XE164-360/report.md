> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-360 — selected watchdog numeric source replay

**VERIFIZIERT, bounded source model:** The selected static paths in FW31 `SetTime` and the complete local comparison helper were replayed from the frozen WP354 instructions. The model shows low-word input multiplication, the exact unsigned gate, the source UMULL/high-word shift/MLS sequence, selected store bytes, and signed helper branches at exact 1,000,000,000 and +1. Invalid SetTime witnesses stop at the opaque log-call boundary; no call effects are invented. **OFFEN:** API parameter meanings, units, field meanings, physical-watchdog meaning, lifecycle, ABI, and runtime behavior. **PASS:** source-bound arithmetic and selected path checks. **NOT_RUN:** native ELF/runtime/VM/device/network.

## Source and model boundary

The exact subject is FW31 `libpackbus.so.1.0.1`, 148,792 bytes, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. All code, literal-pool and REA inputs are copied from frozen root WP354; its manifest SHA-256 is `2e79978dcbadbcaa16838a9e17ad66c9224a71d3bc1b40899155fa9d1eceac85`. The copied retained inventory is 263 instruction words across four wrapper bodies plus the separate 64-word helper body, and 18 pool words. `validate.py` checks those parent pins and every source word and pool value against the exact ELF; it then checks each recorded trace PC and word. `replay.py` is a pure Python arithmetic/path generator. It neither loads nor executes the native ELF.

The synthetic fixtures use aligned, valid, writable, nonaliasing buffers and an explicit saved-frame setup. These are replay premises, not target observations. No ABI preservation or actual pointer validity is presumed. Invalid logger paths are traced through argument setup and stopped immediately before the opaque BL; a source return of `0xffffffff` is conditional on that call returning normally and the saved frame remaining usable.

## SetTime: wrapped product gate and reciprocal path

At Ghidra `0x24cd4`, `MUL r2,r1,r2` retains the low 32-bit product `N=U32(r1*r2)`. The next source gate tests `N==0`; if nonzero, `CMN r2,#0xc0000001` and `BHI` reject unsigned `N>0x3fffffff`. Thus the locally accepted numeric interval is `1..0x3fffffff`, after multiplication has already wrapped. The instructions do not perform a wider-input overflow check.

`settime-cases.tsv` contains selected interior and endpoint controls: N=1, 999999, 1000000, 1000001, and the largest accepted `0x3fffffff`; it also tests `0xffffffff*0xffffffff`, which wraps to 1 and follows the accepted path, and `65536*65536`, which wraps to zero and branches to the invalid logger lane. `0x40000000*1` takes the unsigned BHI invalid lane; the exact maximum is accepted. Invalid lanes perform no success stores before the opaque call boundary. The return-word field for an invalid case is explicitly conditional on a normal opaque logger return.

For accepted N, source loads `M=0x431bde83`, performs `UMULL r12,r1,M,N`, and shifts the high product word right by 18 to form Q. It then computes `R=N-1,000,000*Q` with `MLS`. The table retains both UMULL halves and the selected outputs, rather than substituting a conventional division instruction.

The reciprocal equality is also bounded arithmetically over the source gate’s entire accepted interval. With `K=2^50`, `d=1,000,000`, and `e=M*d-K=157,376`, `N*M/K = N/d + N*e/(d*K)`. For `N<=0x3fffffff`, `N*e<K`, so the added fraction is `<1/d`; for `N=q*d+r` with `0<=r<d`, it cannot move the fractional remainder `r/d` to the next integer. Therefore the observed high-word shift gives `Q=floor(N/d)` for every accepted N. Since `R<d`, the following 32-bit multiplication by 1000 is below 1,000,000,000 for this accepted path.

`settime-trace.tsv` gives instruction-by-instruction PCs, instruction words, register snapshots, NZCV state, stack pointer, selected memory events, and next PC for a maximum-boundary successful case, the wrapped `0xffffffff` square, a zero-product invalid case, an above-maximum invalid case, and a null-pointer invalid case. Successful source stores are: N to `P+4`, 1 to `P`, Q to `P+8`, `R*1000` to `P+0x0c`, then eight zero bytes at `P+0x10..0x17`; `settime-memory.tsv` records their exact fixture values. The source order writes N before the status word. Memory access, alignment, aliasing, fault behavior, and concurrent mutation are not modeled as target facts.

## Local helper: exact threshold and +1 paths

The complete 64-word helper at Ghidra `0x24b68` is call-free. In the selected model, `r0` is a synthetic H base, the body copies it to `r2`, and `r1` points to a separate comparison pair J. The first `r3` value is the 32-bit sum `[H+0x0c]+[H+0x20]`; `r0` is `[H+8]+[H+0x1c]`. The local threshold is formed as `r12=1,000,000,000`. Pair and object words are stipulated current memory words solely for replay.

`helper-trace.tsv` records every PC reached on two selected paths, including skipped predicated instructions, actual encoded word, NZCV, register state, reads/stores, and SP/frame restoration. In the first fixture, the first sum equals exactly 1,000,000,000. `CMP` gives `Z=1`; signed `BLE` is taken and no first normalization is done. Pair word J[0] equals the resulting r0, and J[1] is at least r3, so the second pair is visited. Its sum is 1,000,000,001. The signed `GT` path computes a difference of 1; `CMP 1,1,000,000,000` yields `N=1,Z=0,C=0,V=0`, so `CPYLE r3,r4` and `CPYLE r0,lr` execute, while all `ADDGT` operations are skipped. The resulting r3=1 and r0=7 are then compared with J[0]=6; signed `BLT` reaches the counter path. In this fixture the counter comparison is `1-0`, yielding C=1; `STRBCS` writes byte 1 at H+0x28 and the helper returns numeric 1.

In the second fixture, the first sum is 1,000,000,001. The same signed GT then signed LE sequence produces r3=1 and r0=7. Since J[0]=0, signed `BLT` returns numeric 0 directly; there is no helper store. The exact 1,000,000,000 and +1 values are machine-word comparison witnesses only. No timestamp normalization, unit, API status, or field meaning is inferred.

The helper uses signed `BLE/GT/LT/GE` for its threshold and pair comparisons. Its counter store is instead predicated by unsigned `CS` after a separate `CMP`. `flag-controls.tsv` records controls where signed and unsigned readings differ and where a wrapped counter equality still sets carry; these prevent replacing the encoded conditions with a generic numeric comparison. The helper may perform 32-bit wrapped adds/subtracts, and no general overflow or normalization theorem beyond these selected paths is claimed.

## Claim limits

The constructor/initializer source does not establish that these synthetic H/J words exist at runtime, that SetTime inputs represent seconds or nanoseconds, or that a physical watchdog consumes the fields. Symbol names and offsets do not define an API or layout. Callback, lifecycle, synchronization, actual PLT/GOT binding, logger effects, and all runtime outcomes remain open.
