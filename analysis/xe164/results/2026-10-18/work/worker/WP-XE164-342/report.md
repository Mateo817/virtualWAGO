> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-342 — bounded `libpackbus_open` producer contract

**VERIFIZIERT, source-local:** the seven callback bodies reviewed in WP324/WP336 derive the same image-relative address `G` (Ghidra `0x54420`, ELF-relative `0x44420`) and load a current word from that cell, denoted here `S=[G]`. `G` is the cell address; `S` is its current contents. They are not interchangeable. The exact 407-word `libpackbus_open` body has one identified direct store to the cell: `STR r8,[r9]` at Ghidra `0x20ba8` / ELF `0x10ba8`, reached only on the local allocation-success route. The source expression supports a conditional producer association. It does not establish that callbacks later read the same object at runtime.

The acquisition pins the exact FW31 `libpackbus.so.1.0.1` bytes (148,792 bytes, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`), WP310’s complete REA body/procedure metadata, WP311’s full 407-word/body-pool ledgers, and WP318’s independent matching source. The reviewed callback source remains the previously closed seven-method WP324/WP336 scope: 415 body words and 11 separate pool words. This package expands no helper or callee. It validates all copied code/pool words against the exact ELF at their recorded file offsets and checks the frozen upstream manifests. No code was executed.

## Cell and allocation routes

`libpackbus_open` first loads a literal at Ghidra `0x20d6c` (`0x33b34`) into `r9`, calls an opaque target, then adds architectural PC `0x208ec`; if the current `r9` still contains that literal, the result is `0x54420`. It loads the current word there at `0x208e8` and branches to allocation at `0x20b28` when that observed word is zero. Since the call at `0x208e0` intervenes before the address calculation, preserving `r9` is an explicit condition, not an ABI assumption.

The body later reloads a second literal at `0x20d70` (`0x33b10`) and adds architectural PC `0x20910`, independently deriving the same `0x54420` cell address. The allocation lane reaches this later rebase only after the allocation block; its publication store at `0x20ba8` uses the earlier `r9`, so `r9` must remain the computed cell address across the opaque allocation and initialization calls. `r8` must likewise still hold the return word from the allocator-like call for `STR r8,[r9]` to publish that base.

The source sets `r0=0xe4`, `r1=1`, then calls an opaque target at `0x20b30`. It copies the returned word into current `r8` and forms `r8+0xdc` for another opaque call. There is no local zero comparison on the allocator return before this offset is formed. A nonzero result of the `+0xdc` helper gate branches to cleanup at `0x20dd8` and returns the encoded `0xffffffff`; a zero result continues to a second opaque call on `r8+0xe0`. A nonzero result there branches to `0x20e08`, writes the previously saved first-helper return word to the un-published allocation at `r8+0xe0`, performs opaque cleanup and returns `0xffffffff`. These failure routes do not execute the direct store to `G`.

On the local success route, the body passes addresses based on `r8` at `+0x10`, `+0x30`, `+0x48`, `+0x60`, `+0x7c`, and `+0xa4` to opaque calls. It then stores zero at `r8+0x78`, calls an opaque target with `r8+0xa4`, and stores current `r8` through current `r9` at `0x20ba8`. The new word at G is thus supplied by an opaque call return under these gates. The code does not establish that the allocation routine zeroes memory, that any helper writes its pointer argument, or that `r9/r8` survive each call. The gate at `0x208e8` also has a distinct existing-word route: an observed nonzero S skips the allocation block, so the `0x20ba8` store is not executed on that route.

The early setup contains further opaque gates. For example, the zero result tested by `SUBS r7,r0,#0` at `0x208c8` branches to `0x20adc`, which can take an opaque recovery sequence back to `0x208d0`; this is not classified as a terminal failure and no retry convergence is claimed. The entry selector at `0x20824` routes both-nonzero input words to a separate body path. There is then another gate after opaque calls: `ORRS r2,r4,r6` at `0x20844` followed by `BNE 0x20ce4` at `0x20848`. Only if the *current* r4 and r6 are both zero does that local branch fall through toward the later setup and G-cell path. Since opaque calls intervene, neither current register is equated to its entry value, and the entry selector alone does not establish the producer route. None of these local paths proves a lifecycle order or a runtime call sequence.

## Writes to the current S word

The complete requested field inventory is in `S-store-ledger.tsv`. The primary distinctions are:

| Current offset | Source-local producer fact | Callback comparison |
|---|---|---|
| `+0` | Store at `0x2090c` writes current `r0` after an opaque call; the prior `r8` came from `[G]` before that call. | ReadEnd/WriteStart/WriteEnd gate on words derived from S+0; the stored word’s value and pointer validity are unknown. |
| `+4` | Store at `0x20924` writes an opaque call’s current `r0`; the call was entered with `r0=0`. | ReadEnd/WriteStart gate on this word. Entry argument zero does not prove the return word is nonzero or usable. |
| `+0xa0..+0xa1` | `STRH r6,[r2,#0xa0]` writes one 16-bit zero after `r6` is locally set to zero. | WriteBytes reads byte `+0xa0`; no separate direct byte store at `+0xa1` was found. |
| `+0xa2` | `STRB r6,[r2,#0xa2]` writes zero from that same local zero value. | ReadBytes and WriteBytes both gate on this byte. If this value reaches either callback unchanged, their zero-byte early path is source-supported; persistence is not. |
| `+0xa4` | No direct store. On fresh allocation, its address is passed to an opaque call before publication. | ReadBytes reads it; WriteStart uses it in a call vector. Its contents/effect are unknown. |
| `+0xa8`, `+0xac` | No direct store or field-address initializer in the bounded body. | ReadBytes reads these words; their values are not produced by this body. |
| `+0xb0`, `+0xb4`, `+0xb8` | No direct store or field-address initializer in the bounded body. | WriteBytes reads these words; their values are not produced by this body. |
| `+0xdc` | No direct store. Fresh-allocation path passes `r8+0xdc` to an opaque helper. | ReadStart’s bounded helper uses `+0xd4`; DiagGetDeviceState reads `+0xdc`. No target/value contract is established. |

The source’s two `+0` and `+4` writes are different call-return words, not explicit constants. The `+0x94` write stores current `r6`; despite entry `r1 -> r6` at function entry, opaque calls occur before that write, so entry identity is not asserted. `+0x9c` receives the local literal 2. `+0x8` receives a fresh load from the then-current `[S+4]`, so it is not proven to match the earlier `+4` store absent cell/object and memory continuity. Further direct writes include `+0xa2=0`, `+0xc=0`, `+0xa0/+0xa1=0`, `+0xc8/+0xcc=0x2ee0`, `+0xd0=0`, dynamic values at `+0xbc/+0xc0/+0xc4`, and the conditional `+0x98` store discussed below.

`+0xbc` and `+0xc0` receive the same stack word saved from current `r6` before opaque calls; the code then reads the pair back, masks bit `0x100000` in both lanes, writes it back, and stores a derived word at `+0xc4`. Their final words therefore depend on current registers, valid stack/frame memory and opaque effects. These extra fields are documented to distinguish direct writes from untouched callback inputs, not to assign a structure type.

A separate conditional block publishes callback words through current `r4`, the entry-`r0` copy, at `+4..+0x5c`. That table is not presumed to be S. Only on the local `r4!=r6` branch, the block also loads current `[G]` to `r0`, reads `[r4+0xc]` to `r3`, then stores that word at current `r0+0x98`. This is a conditional direct write to current `S+0x98`; it is not evidence that `r4` and S are the same base. The equality branch skips the callback-table publication block.

## What the seven callback reads can rely on

The callback field comparison uses the existing WP324/WP336 source scope. It does not imply these callbacks execute after `libpackbus_open` or observe the same S. Source-local correspondences are:

- ReadStart’s separately bounded helper uses current S+`0xd4`; the open body has no direct write to that location.
- ReadEnd reads the current words at S+0 and S+4 and uses S+`0x30` and a reloaded S+`0x10` in later calls. The open body supplies stores at +0/+4 from opaque return values, and passes +0x30/+0x10 addresses to opaque initializers, but it proves no returned pointer or helper effect.
- ReadBytes reads S+`0xa2`, `+0xa4`, `+0xa8`, and `+0xac`. The open body locally writes `+0xa2=0`; it passes +0xa4 to an opaque helper and has no direct writes to +a8/+ac. If the local zero reaches the method unchanged, ReadBytes takes its source-local early return before its data call.
- WriteStart reads +0/+4 and uses +0x48/+0xa4 call positions. The open body writes +0/+4 from opaque calls and passes +0x48/+0xa4 addresses to opaque calls; no values or effects are inferred.
- WriteEnd consumes +0 and uses +0x48/+0x10 call positions. The open body gives the same qualified +0 store and passes +0x48/+0x10 to opaque calls.
- WriteBytes reads bytes +0xa0/+0xa2 and words/halfwords +0xb0/+0xb4/+0xb8. The open body writes zeros to +a0/+a1/+a2, but none of the +b range. If the zero at +a2 reaches the method unchanged, its local early path returns zero before SSC_Put; no later-state guarantee follows.
- DiagGetDeviceState reads +0xdc. The open body passes +dc to an opaque initializer, with no direct store to that location.

Therefore the producer body supports a conditional explanation for the zero gates at +a2 and the zero bytes +a0/+a1; it supplies only opaque call-return writes at +0/+4 and opaque initializer address arguments for +0x48/+0xa4/+0xdc and lock-related locations. It does not source the required values at +a8/+ac/+b0/+b4/+b8 or ReadStart +d4. No allocator behavior or call contract may fill those gaps by inference.

## Limits and validation

The stored word at G may be reloaded multiple times; no equality of S across loads or across calls is assumed. The report never assigns an ABI, API prototype, structure layout, field meaning, object lifetime, initialization order, callback execution order or runtime binding. Imported callees, memory writes through pointer arguments, allocation contents and concurrency remain open. WP325/WP338 concerns a distinct provider and is not used to infer these `libpackbus` fields.

`validate.py` is read-only. It verifies all source pins and frozen manifests, exact raw bytes for 407 open-body instructions, 54 pool words, 415 callback instructions and 11 callback pool words; cross-checks the independent 311/318 source ledgers; recomputes G address expressions and branch targets; verifies the direct store set and allocation gates; and validates the seven-method input coverage. It executes no ELF. Canonical claim statuses are in `claim-matrix.tsv`.

**VERIFIZIERT:** bounded source arithmetic and writes. **OFFEN:** opaque initializer/callee effects, allocator contents, persistent S identity, runtime call order and binding. **NOT_RUN:** native ELF, runtime, VM, device and network execution.
