> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-402 — independent review of frozen Root WP401

**VERIFIZIERT (bounded source review):** WP401 manifest matches the requested value. Its 274 instruction words and 14 separate literal words match the exact pinned FW31 DSO through ELF `PT_LOAD` mappings. An independent raw-byte audit confirms the 18-byte input walk, H=0 local return, J arithmetic and numeric maximum, selected bit-mask branch formulas, the stated producer write positions, and the bounded cleanup loop's clear-before-free ordering. No raw instruction contradiction was found. **OFFEN:** complete producer execution, runtime PLT resolution, allocation contents/validity, object identity and lifecycle, API/ABI meaning, and physical effects.

WP401 is a root self-review. My checker does not reproduce a full CPU trace: it independently verifies selected words, file mappings, direct address/arithmetic formulas, and loop/store ordering from the encoded instructions. WP401's validator likewise explicitly reports finite arithmetic/source checks, not CPU replay. This finding does not upgrade the producer path to a full replay or establish current register/memory values after opaque calls.

## Source and boundaries

The exact source object `libpackbus.so.1.0.1` has SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. The requested WP401 manifest is `695e514f50ff30f2ec51e89e2590dbff80db6bf39ea6a17074f82dc0ddcee92d`; its report hash is recorded in `source-pins.tsv`. All 274 words and 14 literal values in WP401's tables were independently checked against the exact file offsets and ELF bytes. The stated bounded instruction spans are producer ELF `0xc164..0xc540` (247 words), cleanup `0xc578..0xc5b4` (15), and four PLTs (12 total). Its retained validator passes and checks inventory before/after.

The producer reads `H=U16[S]` and branches to the local zero return before later calls if H is zero. The two raw halfword loads at `0xc224` and `0xc254` encode `[r4,#0x12]!`, confirming an 18-byte record advance; the subsequent zero compare/branch is the source terminator. This proves only the encoded sentinel loop. It does not prove that a caller supplies a well-formed or accessible terminated sequence.

The source forms `J=U16[S+2]+(U8[S+6]>>3)`. The largest operands give `65535+31=65566`, a positive 32-bit value. Thus the selected signed `BGT` against `0x2edf` (11999) is equivalent to the ordinary positive numeric greater-than boundary for this local J range. The statement does not cover arbitrary values that might be present in registers after opaque calls.

## Selected producer fields and arithmetic

For the `S+0xa == 0` route, raw instructions form the outer slot from `T+(J<<4)`, write J at outer `+0`, and write 1 at outer `+4`. A null current pointer at outer `+8` leads to a calloc-named call with numeric inputs `(r0,r1)=(8,0x10)`; the current return is written to `+8` and 8 to `+0xc`. The source does not itself prove zeroed returned bytes. When a valid current pointer R is present, K=`U8[S+6]&7` selects `M=R+16*K`. The selected path stores the one-hot `1<<K` at `M+9`, `U8[S+0x10]` at `M+0xc`, and a source-derived byte mask at `M+8`; it stores the computed numeric address at `M+4` and selector 1 at `M+0`.

For `n=H&15`, the source uses `2*(H>>4)` and `1<<(15-n)` when `n>=8`. When `n<8`, the encoded path adds one byte to the address and uses `1<<(7-n)`. The instruction sequence around `RSB r2,r12,#15`, `CMP r2,#7`, the conditional zero of the address delta, and alternate `RSB #7` matches these two cases. Exhaustive finite enumeration of n in 0..15 and K in 0..7 confirms both mask exponents are 0..7. This is numeric source evidence only; it establishes no physical bit ordering, units, or API meaning.

For the selected nonzero `S+0xa` routes, the allocator call vector has a 16-byte request. The source stores selector 2 or 5 at the inner base, the computed V at inner `+4`, and the current flag byte at `+0xc`. Selector 2 additionally stores numeric 1 at inner `+8`; selector 5 instead stores `U8[S+8]` there. The distinct current allocations and their contents remain conditional on opaque allocator results and valid current registers.

The group branch forms a current pointer D with numeric calloc request `(12,1)`, then a malloc request of 96. The current malloc return is stored to `D+4`; when it is nonzero, the source stores halfword 48 to `D+0`. The append sequence reads `N=U16[D+2]`, reads A from `D+4`, forms `A+2*N`, stores the selected halfword, and increments/stores N. In this selected append sequence no `N<48` comparison precedes that store. This is a source observation, not a claim of overflow, invalid input, or allocation defect: D/A construction, N's initial value, N's caller-visible range, and reachability are open. WP401's cited consumer-side N=0 pre-read is explicitly a separate synthetic premise, not a state proven from this producer.

The existing numeric consumer comparison is consistent with the accepted, pinned WP363/364/372 summaries: selected consumer code reads selector/mask positions in the inner 16-byte records, and selector 4 reads a D-like target at M+4 with numeric positions D+2/+4/+8. This corroborates same-position hypotheses only; it does not establish one concrete allocation or lifecycle joining producer and consumer.

## Cleanup and qualifications

Cleanup computes the end as `T+0x2ee00`; `0x2ee00/16=12000`, so its selected stride/equality loop visits 12000 outer slots when the current basis/end and memory premises hold. At each slot, it reads `+8`; on nonzero it writes zero to that slot before issuing the free-named PLT call. Null values skip the call. It advances by 16 and returns local zero. This bounded source body does not follow any inner 16-byte records or D/A references. It proves neither actual free behavior nor completeness of ownership cleanup elsewhere.

The status remains **OFFEN** for calls' effects, bindings, allocations, and object construction. In particular, concrete stores after allocator or logger calls need valid current pointers and register/frame values; no generic ABI preservation assumption was used. Target/runtime/device/network tests are **NOT_RUN**.

`python3 audit.py` passes the independent raw-byte, range, producer arithmetic, and cleanup loop checks. `python3 ../root/WP-XE164-401/validate.py` also passes the frozen source-table and inventory checks.
