> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-292 — conditional selector-15 local return chain

## Result

**VERIFIZIERT** — Within the exact pinned source words and stipulated memory/pointer predicates, the 15 lane is closed from `CMCallHook(15,0,0,0)` through its local helper transfer, Dal selector-15 body, resolved getter, provider `+4` body, Dal common return, and the core postlude. Three admitted halfwords (2, 4, 5) produce the same conditional local result: `r0=0` returned to `0x2ff770`. The model uses the retained mathematical A32 source-word replay for the core caller/helper/postlude and explicit word-bound arithmetic/state transitions for the bounded Dal/getter/+4 route. Synthetic Dal bias `G=0x70000000` and provider bias `P=0x73000000` are separate fixtures, not observed load addresses. It does not execute native ELF instructions.

## Source pins and retained evidence

**VERIFIZIERT** — `codesys3` is 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`; `libIoDrvDal.so.1.0.2` is 25,976 bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`; provider `libdal.so.1.0.1` is 18,076 bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. The package pins the accepted WP246 helper/CMCallHook REA, WP255 selector-15 prefix, WP259 raw-A32 replay, WP262 Dal dispatcher/PLT/common REA, WP202 getter, WP224 full +4 body and WP273 source-address trace. No new function bodies or callers are expanded.

## Conditional route and exact returns

**VERIFIZIERT** — Core prefix starts at `0x2fecc4`, reaches `BL 0x2fec58` at `0x2fedd4` with `r0=object`, `r1=15`, `r2=0`, `r3=0`; the instruction after BL is `0x2fedd8`. Its prologue word at `0x2fecc8` is `STMDB sp!,{r4-r12,lr,pc}` and the recorded epilogue at `0x2fef18` is `LDMIA sp,{r4-r11,sp,pc}`. The helper saves `{r4,r11,r12,lr,pc}` at `0x2fec5c`, restores `{r4,r11,sp,lr}` at `0x2fecb4`, then executes `BX r3` at `0x2fecb8`. It accepts object halfword 2/4/5, loads the stipulated target from object `+0x20`, and forwards `(15,0,0,target)` with LR `0x2fedd8`. Core optional callback slot is zero and the synthetic single-head next word is zero.

**VERIFIZIERT** — At Dal `0x362c`, `r0=15` gives `r3=15-2=13`, which satisfies the unsigned `<=13` table condition. The `ADDLS pc,pc,r3,LSL #2` at `0x3644` uses PC `0x364c`, selecting `0x3680`; its branch reaches `0x42f4`. The Dal `BL` at `0x42f4` saves LR=`0x42f8` and reaches its PLT at `0x9d4`. The exact PLT/GOT route is conditional on GOT word `0x16030=P+0x3464`; the getter body at `P+0x3464` returns `P+0x14154`. Dal instruction `0x42f8` loads `[r0+4]`. Provider cell ELF `0x14158` has `R_ARM_RELATIVE` and raw source addend `0x1dc0`, so under the stipulated relocation result this cell selects `P+0x1dc0`. The following `BLX` at `0x42fc` writes LR=`0x4300`. Dal's encoded prologue `STMDB sp!,{r4-r11,lr}` and `SUB sp,#0xbc` reserve 224 bytes; its epilogue `ADD sp,#0xbc; LDMIA sp!,{r4-r11,pc}` restores the saved general registers and returns to `0x2fedd8`.

**VERIFIZIERT** — The exact +4 body starts with literal load/add, then reads byte `[P+0x14208]`. If that byte is zero, `CMP` sets Z, `BNE` at `0x1dd0` is not taken, `MOV r0,#0` executes at `0x1dd4`, and `BX lr` at `0x1dd8` returns to Dal `0x4300` with `r0=0`. This early leaf path executes no opaque call. Dal then branches `0x4300→0x4194→0x3710`. With the explicit synthetic common gate `[G+0x163d0]=1` (the loaded `base+0xc` word), the callback loop is skipped; `r4` is the zero set at `0x4194`, so common code returns zero and encoded `POP {r4-r11,pc}` restores the Dal frame and returns PC=`0x2fedd8`. Core continuation follows the pinned posthelper path with `head.next=0`, restores its encoded saved registers/SP, and returns `r0=0` to stipulated incoming LR `0x2ff770`.

The three positive machine-readable traces are in `positive-cases.json`; `path-words.tsv` binds each scoped word to source bytes. The recorded selected call return addresses are getter-call continuation `0x42f8`, leaf BLX return `0x4300`, Dal return `0x2fedd8`, and final core return `0x2ff770`.

## Predicates, countercontrols, and limits

**VERIFIZIERT** — The closed source instance requires exact artifacts/words; selector 15; helper halfword 2/4/5; null core optional callback slot; valid synthetic head/object and stack; target word bound to Dal `0x362c`; GOT `0x16030=P+0x3464`; provider relocation applied so `[P+0x14158]=P+0x1dc0`; byte `[P+0x14208]=0`; and Dal common `[G+0x163d0] != 0`. The core postlude additionally requires the stipulated `head.next=0`. Negative controls show byte=1, with first body word `[P+0x141e0]=1`, reaches the first opaque +4 call and therefore cannot establish this result; wrong GOT/slot stop the binding chain; nonnull optional core callback, nonzero head link, or Dal callback gate with positive count diverge from the closed route; invalid helper halfword returns 1.

**HYPOTHESE** — These pointer, relocation, stack, object/list, and global-memory predicates hold together in one runtime instance. The source establishes the relocation record/addend and local code only; it does not observe loader resolution or process memory.

**OFFEN** — Runtime reachability, actual callback binding, API/ABI meaning, universal lifecycle or mandatory phase claims, effects of the first opaque +4 callee on the byte-nonzero route, concurrent mutation/fault behavior, and any behavior beyond the selected source bodies. Selector 15 is a verified local route under stated premises, not a universal runtime phase contract.

## Validation

`validate.py` is read-only by default and checks source and upstream pins, exact raw words, generated traces and negative controls, plus a self-reference-free manifest. `countercontrol-results.json` contains computed branch/address outcomes for the byte=1 stop, wrong target bindings, optional callback/list gates, the positive Dal count, and invalid helper data. It validates a mathematical fixture model only. Tests **PASS**; native execution, runtime, VM, device, and network **NOT_RUN**. Review status: self-review; independent review **NOT_RUN**.
