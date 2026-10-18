> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-266 — conditional selector17-to-zero-return source replay

## Identity and scope

**VERIFIZIERT** — The source inputs are `codesys3` SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` and `libIoDrvDal.so.1.0.2` SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. Core helper/caller instruction evidence is pinned through WP246 REA and the exact candidate prefix through WP255. Dal instructions and the PC-relative literal are pinned through WP262 REA and byte-bound to the exact DSO. The core caller/helper paths use WP259's hash-pinned mathematical raw-A32 instruction decoder. The selected Dal path uses hand-derived register, condition, and address equations tied to the pinned Dal words; it does not run through a generic Dal instruction decoder. Neither ELF is executed.

**VERIFIZIERT** — For `CMCallHook(17,0,0,0)`, the model replays the exact 68-word selector17 core prefix to the helper call. Its unsigned subtract/branch flags select the default Dal helper path. The stipulated synthetic list has one head, the optional core callback slot is null, and the object halfword is one of 2, 4, or 5. The helper restores its frame and branches to the stipulated synthetic Dal address with forwarded arguments `(17,0,0,target)` and LR `0x2fedd8`. The runtime pointer binding is a **HYPOTHESE**, not an observed target mapping.

**VERIFIZIERT** — At Dal ELF `0x362c`, selector 17 yields unsigned `17-2=15 > 13`, taking the default route to `0x4194`, where `r4=0`. The model uses a synthetic Dal load bias `0x70000000` to evaluate the exact PC-relative literal at `0x4344`; this bias is not observed. Under the chosen global-word conditions `[base+0xc]=0` and `[base+0x10]=0`, the callback-loop precheck at `0x4334` is false at index zero, so no Dal callback executes. The common return moves `r4` to `r0`, producing zero.

**VERIFIZIERT** — Dal's encoded `PUSH {r4-r11,lr}` saves the live values, and its `SUB sp,#0xbc` gives a 224-byte frame including the push. The `STRD r0,r1,[sp,#0x2c]` at `0x3638` and `STR r2,[sp,#0x34]` at `0x363c` are modeled as fixture writes of the forwarded arguments at offsets 44, 48, and 52 from the frame bottom. Assertions place all 12 bytes inside the Dal-owned frame and below, without overlap with, its 36-byte push-save area or the caller core frame. The encoded `ADD sp,#0xbc; POP {r4-r11,pc}` restores those registers, SP, and PC `0x2fedd8`. The Dal frame is also disjoint from the full stipulated list object and global words. These are explicit model predicates, not ABI claims.

**VERIFIZIERT** — Core's posthelper instructions are replayed from `0x2fedd8` using the WP259 mathematical A32 model. With returned `r0=0` and `head.next=0`, the recorded branch trace reaches the source epilogue and returns `r0=0` to stipulated LR `0x2ff770`. The core encoded save/restore path restores `r4-r11` and the entry SP from their synthetic sentinel values. The 17 selector side stores remain `0x5fc554=17` and `0x5fc5b8=17`; these are addresses/effects only, with no API meaning assigned.

## Conditions and negative controls

**VERIFIZIERT** — The complete local conditions for this closed instance are: exact pinned source words; stipulated helper target binding; selector 17; accepted helper halfword 2/4/5; null optional core callback; one head with `head.next=0`; Dal default globals `[base+0xc]=0`, `[base+0x10]=0`; distinct nonoverlapping synthetic code, object, globals, and stack ranges; and the recorded stack fixture. `negative-controls.tsv` demonstrates that mismatched helper data, null target, a nonnull optional core callback, nonzero `head.next`, or positive Dal count leaves the selected closed path.

**HYPOTHESE** — Runtime binding of the object's target word to Dal ELF entry `0x362c`, actual runtime load bias, manager/list/object identities, and all synthetic memory/stack values.

**OFFEN** — Runtime ABI, callback/API meaning, lifecycle meaning, actual process state, all non-fixture memory, and behavior outside the exact source paths. The positive-count Dal callback body and non-singleton core list paths are not modeled. The results are conditional source-level evidence only.

**PASS** — `validate.py` is read-only by default. It rechecks pinned source/upstream evidence, generated path words/results/negative controls, and a self-reference-free manifest. No VM, network, native execution, or public repository was used.
