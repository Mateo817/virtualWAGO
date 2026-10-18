> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-350 — bounded helper composition for `libpackbus_open`

**VERIFIZIERT, source-local:** the two call sites decoded in WP342 resolve to retained helper bodies in the same exact FW31 `libpackbus.so.1.0.1` image. Under explicit register and memory preconditions, the first helper stores the return word from a PLT target named `calloc` through the caller-supplied `+0xdc` pointer and returns 0 only when that word is nonzero. The second helper copies six post-call current words from an image-relative global-data base into its caller-supplied `+0xa4` output range. The WP342 caller checks the first helper’s result, but immediately after the second helper call it publishes current r8 through current r9 without testing r0. These are conditional source-level joins; no ABI, allocation, synchronization, callback, runtime binding, or field meaning is inferred.

## Pinned evidence and bounds

The subject is the exact 148,792-byte FW31 `libpackbus.so.1.0.1`, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`; its ELF type is ET_DYN with load-segment virtual address zero. Thus the module RVA equals the ELF VA in this package, while Ghidra addresses are module RVA plus `0x10000`. Root WP348 is frozen with manifest digest `eaf91c9c840e71edcc3335f6941f35944cf9d45c1a6d9f71f40adbcee1efdd08`; its retained source contains 50 instruction words (two 22-word bodies plus six thunk words) and four separate literal-pool words. WP342 is frozen and separately pinned. `source-pins.tsv` records local copied-input hashes and retained Evidence IDs. `helper-*-words.tsv` and `literal-pool-words.tsv` were byte-checked against the exact ELF; the validator does the same check again.

Relevant retained REA records are CreateWatchdog body `ev_265b5bbd1b7b07e746a19e92ab5fb7c5961f33dfcee8352dd6a84e7fcc1bfdf3`, procedure metadata `ev_ca93d85103618ff759594375b230e4302622711345361ae919578e66401dc887`, and thunk `0x18220` body `ev_f2923447304ca640cbb38985eee431600599d7d10549dc29d9c591b0a23c9402`; vGet body `ev_b061b99838fe3bde082ce0592991578e1b94820e4ccf448850dd95baab1f6d24`, procedure metadata `ev_ab8ab848ddd8430f51331bad81a0219f0da2a8b217febcf12a4b9de9ad497f25`, and thunk `0x17d7c` body `ev_e6001a57da1394b836b80ce9c66dc0e425400118c0bf2802596e9c18fe0636f3`. The global-data literals are pinned as `ev_8f0a7bbb6d2fcda7cb28facdfe54b956803ffe2e3a180a7d643b54d39b6b12f6` and `ev_98fff2efe2a6e6c41b6134391eb8edc4e5b21eeef1fe52bc10ffd68afe77eb3c`. WP342 callback word rows are also copied and pinned to distinguish the same-image consumers at `+0xdc` and `+0xd4`.

No new caller, helper, imported target body, runtime object, or callback body was analyzed. The only callback address recorded is the argument calculated locally by vGet. The retained procedure-info request for `0x24774` failed with “No procedure exists at the requested address”; it is pinned as a missing-procedure record and supplies no callback code.

## CreateWatchdog path and `+0xdc`

The WP342 direct call at Ghidra `0x20b40` is an ARM `BL` word `0xebffddb6`, target Ghidra `0x18220` / module RVA `0x8220`. That 12-byte thunk transfers to body `0x24c68` (module RVA `0x14c68`). At the caller, `0x20b34` forms current r10 from the allocator-call return plus `0xdc`, `0x20b38` copies that return word to current r8, and `0x20b3c` moves current r10 to r0 before the helper call. This establishes the helper’s entry argument as `allocationBase+0xdc` only for the current register values produced by those instructions.

Inside the complete 22-word helper, `0x24c70` copies entry r0 to current r4, and the source sets current r0 to 1 and r1 to `0x2c` before the PLT call at `0x24c78` named `calloc`. On return, `CMP r0,#0` at `0x24c7c` is followed by `STR r0,[r4]` at `0x24c80`, then `BEQ` at `0x24c84`. If the imported call returns a nonzero word and current r4 still equals the writable output pointer, that word is stored and the helper returns 0. If it returns zero under the same conditions, zero is stored, and the helper follows an opaque error path through PLTs named `__errno_location`, `strerror`, and `syslog`, then returns `0xffffffff`. The source does not dereference the output word or inspect its contents after the store. The symbol name `calloc` does not establish zero-fill behavior here; no allocation or zeroing effect is inferred.

The caller at `0x20b44` compares the helper return and branches to cleanup at `0x20dd8` when it is nonzero. Therefore the local success route requires the helper to return zero; within the helper’s own local branch structure, that occurs when the imported call return is nonzero. This maps an imported-call result into the conditional `+0xdc` output cell. The word’s validity, allocation behavior, fill contents, and API role are not established from the imported name. There is no evidence here that it initializes `+0xd4`.

## vGetVPI_Values path and six output words

The WP342 direct call at Ghidra `0x20ba4` is word `0xebffdc74`, target Ghidra `0x17d7c` / module RVA `0x7d7c`. That thunk transfers to body `0x24a50` (module RVA `0x14a50`). The caller computes current r0 as current r8 plus `0xa4`; under the condition that r8 still contains the allocation base, this supplies the helper output pointer at `allocationBase+0xa4`.

In the helper, current r4 captures entry r0. The first pool word at `0x24aa8` is `0x00033144`; the `ADD` at `0x24a60` uses architectural PC `0x24a68`, yielding the local data base B=`0x57bac` (module RVA `0x47bac`). The second pool word at `0x24aac` is `0xfffffd08`; the `ADD` at `0x24a64` uses PC `0x24a6c`, forming the callback argument `0x24774`. The source then passes current r0=`B+0x30` and r1=`0x24774` to PLT `0x178a8`, whose retained symbol name is `pthread_once`. Next it passes current r0=B to thunk `0x17650` (target `0x18624`), named `MISC_threads_acquire_lock`.

After those two calls, the helper forms current r12=B+`0x18` and performs `LDMIA r12!` loads. The first load reads current words at B+`0x18`, `+0x1c`, `+0x20`, and `+0x24`, then stores them to current r4 offsets 0, 4, 8, and `0xc`. The next load reads current words at B+`0x28` and `+0x2c`, then stores them to r4 offsets `0x10` and `0x14`. The loaded values are post-call current memory values; the source does not establish their contents or which call, if any, wrote them. It also does not establish that either call preserves r4 or r5. Those registers, the saved stack frame/stack memory used by the epilogue, readable B memory, and writable 24-byte output memory are explicit continuation preconditions.

The helper then sets current r0=B, restores its saved frame, and tail-branches to PLT `0x17a70`, whose retained name is `pthread_mutex_unlock`. No behavior or return value of that target is assumed. In the caller, the instruction immediately after `BL 0x17d7c` is `STR r8,[r9]` at `0x20ba8`; that store does not consume r0, and there is no local check of the vGet return. Reaching it still requires current r8 to retain the allocation base, current r9 to retain G, and the preceding opaque calls to permit that path. The local output writes happen before publication.

Under those conditions, the six output stores map to allocation offsets `+0xa4`, `+0xa8`, `+0xac`, `+0xb0`, `+0xb4`, and `+0xb8`. If the caller then stores the same allocation base at G and the cell/object remains unchanged, those addresses correspond to S offsets. That is a source-derived conditional association only; later callback invocation, same-object reads, persistence, and opaque memory effects remain open.

## Keep `+0xdc` and `+0xd4` separate

The WP342 callback source words bind `DiagGetDeviceState` at `0x1f9e0` to `LDR r0,[r3,#0xdc]`, while the separately bounded `ReadStart` path at `0x1ff64` has `ADD r1,r1,#0xd4`. Both records belong to the exact same pinned libpackbus image. CreateWatchdog conditionally stores through the caller’s `+0xdc` argument; neither helper in WP350 writes `+0xd4`. The `+0xdc` producer fact must not be transferred to the distinct `+0xd4` consumer. This comparison assigns neither callback meaning nor runtime binding.

## What remains open

- Effects, register clobbers, return meaning, and memory behavior of imported calls and the `MISC_threads_acquire_lock` thunk.
- Whether callback argument `0x24774` executes or writes any B memory; no body exists in retained Ghidra metadata.
- Source values at B+`0x18..0x2c`, allocation fill/validity, and readable/writable memory preconditions.
- Runtime relation between allocation base, G, later S reads, callback order, object lifetime, concurrency, and persistent output values.
- ABI, C/API signature, structure layout, field names, watchdog/VPI semantics, and initialization contract.

`validate.py` is read-only and checks package/input hashes, frozen WP342/WP348 manifests, exact helper and pool bytes, raw ARM branch targets, the two caller argument vectors and continuation instructions, the six-word transfer sequence, the retained missing-procedure result at `0x24774`, and the `+0xdc`/`+0xd4` separation. Static body reconstruction is not target execution. **Native ELF/runtime/VM/device/network: NOT_RUN.**
