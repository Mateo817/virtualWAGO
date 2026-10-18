> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-351 — independent backend G/S producer-chain audit

**VERIFIZIERT (static, conditional source composition):** WP342’s 407-word `libpackbus_open` body derives image-relative Ghidra cell address `0x54420` / ELF-relative `0x44420`, loads its current word S, and has one direct store through the G-carrying register at ELF `0x10ba8`. The local producer route is gated by numeric source conditions and opaque-call outcomes. Two of those calls are now bound to exact static JUMP_SLOT symbol metadata and their retained 22-word source bodies from WP348: the call at ELF `0x10b40` reaches the local `lpkb_CreateWatchdog` symbol through PLT `0x8220`, and the call at `0x10ba4` reaches local `vGetVPI_Values` through PLT `0x7d7c`. Under the explicit source-register, readable/writable memory, matching relocation, normal-return and helper-preservation conditions below, the composed stores write a value at base `+0xdc` and copy six current global words to base `+0xa4..+0xb8` before the open body’s `STR r8,[r9]` publication.

**HYPOTHESE:** A runtime path binds these local definitions, preserves the stipulated values across opaque calls and exposes this same object to callbacks. **OFFEN:** Runtime PLT winner/preemption, object identity over time, caller lifecycle/order, allocator contents and opaque effects. No ABI, API, structure or application meaning is inferred. No ELF execution occurred.

## Frozen sources and independent checks

The exact FW31 `libpackbus.so.1.0.1` is 148,792 bytes, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. WP342’s frozen manifest is `c9655acb71b39908997a0484866a838c9427e4732f6637d8592dcb400e900129`; Root WP348’s is `eaf91c9c840e71edcc3335f6941f35944cf9d45c1a6d9f71f40adbcee1efdd08`; WP350’s frozen composition package is `b65d6877c332abe5063f8ff2b7c243e94fe16de6fa62fa364c3cb268282a99cb`. I checked their manifest members, copied source words against raw bytes at each recorded file offset, and independently decoded the caller branches, PLT GOT-cell arithmetic, helper literal equations, and helper store destinations. WP342/WP348/WP350/WP325/WP338/WP324/WP336 inputs were not modified.

The three-word PLT at ELF `0x8220` computes its GOT load address as `0x8228 + 0x2b000 + 0x290 = 0x334b8`; the exact `R_ARM_JUMP_SLOT` there names `lpkb_CreateWatchdog`, symbol value `0x14c68`. The three-word PLT at ELF `0x7d7c` computes `0x7d84 + 0x2b000 + 0x5a8 = 0x3332c`; its `R_ARM_JUMP_SLOT` names `vGetVPI_Values`, symbol value `0x14a50`. These are static relocation associations. They do not establish the runtime-resolved target.

## Numeric gates and open-body producer route

The first literal arithmetic and second rebase in WP342 both yield Ghidra `0x54420`, corresponding to ELF-relative `0x44420`. G is the address of the mutable cell; each `LDR` through current G obtains a current S word. The first G calculation crosses an opaque call and therefore requires current `r9` still to hold the literal before the ADD. The direct publication later requires current `r9=G` and `r8` still to hold the allocation base.

The selected source route is not unconditional:

- The entry selector compares `r1` with zero and conditionally compares `r0`; both nonzero values take a separate route. This is a numeric source branch, not a parameter contract.
- After an opaque call, `ORRS r2,r4,r6` followed by `BNE` sends nonzero current `r4|r6` to an alternate route. Only current `r4=r6=0` falls through toward the cell test. Entry values are not substituted for current registers.
- A zero result at `0x108c8` takes a separate recovery route that may loop back; terminal failure or convergence is not proven.
- At `0x108e8`, the body loads current S and compares it with zero. Nonzero S skips the allocation block; observed zero S enters it. Pointer validity and stable S are not inferred.
- On the allocation route, `0x10b30` receives `(r0=0xe4,r1=1)` at an opaque target. The caller copies its current return into `r8` and forms `r8+0xdc` without a local null check.
- The call at `0x10b40` receives that current `r8+0xdc` address. Its return is tested at `0x10b44`; nonzero branches to cleanup at `0x20dd8`, before G publication. Zero continues to the `r8+0xe0` call. The latter’s nonzero result branches to failure at `0x20e08`, loads the saved first-helper result and stores it at `r8+0xe0`, then returns the encoded failure word. It also precedes publication.
- The path that passes both numeric helper gates sends addresses `r8+0x10`, `+0x30`, `+0x48`, `+0x60`, `+0x7c`, and `+0xa4` to opaque calls and writes local zero at `+0x78`. The call at `0x10ba4` then receives `r8+0xa4`; `0x10ba8` stores current `r8` through current `r9` to G. Subsequent open-body status handling can still fail, so this store alone does not mean the function completed successfully.

The existing-cell and publication facts are source-local conditional effects, not evidence of object lifetime, locking, or later callback order.

## Composition with the two helper bodies

`lpkb_CreateWatchdog` saves entry `r0` into `r4`, sets calloc-call arguments to 1 and `0x2c`, and calls an opaque PLT. It then compares its current `r0` and stores that word through current `r4` before branching on zero. Therefore, if open’s PLT call reaches this body with `r0=base+0xdc`, and `r4` still retains that destination across the opaque allocation call, the helper stores the allocation return at `base+0xdc`. A nonzero allocation return takes the source path returning zero; a zero return is stored at the destination first, then takes the error/logging path and returns `0xffffffff`. Open treats that nonzero status as failure and does not publish G. The store is source-derived; allocation validity/contents, helper register preservation, and runtime PLT binding are conditions.

`vGetVPI_Values` saves entry `r0` to current `r4`. Its pool words and PC-relative ADDs derive a current global data base `0x47bac` and callback argument address `0x14774`. It calls opaque once/lock targets, sets `r12` to current `r5+0x18`, loads four words then two words from current `r5+0x18..+0x2c`, and stores them through current `r4` at offsets `0,4,8,0xc,0x10,0x14`. Open supplies entry `r0=r8+0xa4`; hence if its current `r8` remains the object base, the helper is bound to this local body, the destination is writable, current `r4/r5` survive the opaque calls, and the source range is readable and nonaliasing with the destination, the six stores land at base `+0xa4,+0xa8,+0xac,+0xb0,+0xb4,+0xb8`. The global words are read at execution time; no static initializer values or semantic callback identities are claimed. The helper restores its saved registers then tail-branches to an opaque unlock target; normal return through that target is also a premise.

Together with WP342’s source-local zeros at `+0xa0/+0xa1` and `+0xa2`, this conditionally covers all callback consumer offsets in WP324/WP336’s seven-method matrix: ReadStart `+0xd4` remains without a producer in these bounded bodies; ReadEnd consumes `+0/+4` plus call positions `+0x30/+0x10`; ReadBytes consumes `+0xa2/+0xa4/+0xa8/+0xac`; WriteStart consumes `+0/+4` and uses `+0x48/+0xa4`; WriteEnd consumes `+0` and uses `+0x48/+0x10`; WriteBytes consumes `+0xa0/+0xa2/+0xb0/+0xb4/+0xb8`; DiagGetDeviceState uses `+0xdc`. A matching offset and source store do not prove a callback later runs on this allocation or sees its current contents.

## Frozen WP342 cross-reference erratum

WP342’s final paragraph says “WP325/WP338 concerns a distinct provider.” That is incorrect. WP325 and WP338 pin the same exact FW31 `libpackbus.so.1.0.1` SHA-256 and their source arithmetic derives the same ELF-relative cell `0x44420` (Ghidra `0x54420`). The error is a prose cross-reference, not a defect in the raw body words or the WP342 validator. Correct wording should identify WP325/WP338 as same-provider evidence while preserving the existing qualification that equal source-relative G does not establish persistent runtime object identity. Frozen WP342/WP325/WP338 files were left untouched.

## Validation and limits

**PASS:** `python3 -B validate.py` checks source and manifest hashes; every copied word against raw ELF bytes; both PLT-to-relocation equations; the open-body numeric branches and failure routes (including no intervening flag-setting instruction before the entry-selector branch); helper store/control words and literal equations; the callback offset coverage; and the WP325/WP338 same-provider erratum. WP342’s, WP348’s, and WP350’s own read-only validators were inspected and run with before/after inventories; they passed and left their packages unchanged. No source generator was run.

**NOT_RUN:** runtime loading/resolution, native ELF execution, target, network, VM, device, hardware. The result remains a bounded source composition with explicit opaque-call, pointer, memory, and normal-return conditions.
