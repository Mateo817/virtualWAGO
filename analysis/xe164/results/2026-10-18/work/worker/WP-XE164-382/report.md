> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-382 — independent review of WP-XE164-377

**Review verdict: PASS with two boundary qualifications.** WP377 is pinned to worker manifest SHA-256 `15b61ebfeb9ebf96dfca613e1da15853913f6ca8dcd5f4b7a60ef59eafa34c55`. This package independently replays the 48 selected raw words against all 45 source traces. Its read-only verifier passes 23,052 checks: 562 instruction steps, 290 instruction memory effects, 180 separately stipulated opaque memory effects, and 72 opaque call boundaries. No upstream package was changed.

The selected source words match the exact FW31 DSO SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`; each Root362 word is checked against its ELF file offset. The independent replay decodes A32 conditions, arithmetic/compare flag changes, branches and BL return PCs, loads/stores, stack push/pop, BX, and the exact VLD1.32 / VREV64.32 / VST1.32 encodings. It compares before/after r0-r14, PC transitions, NZCV, D16, and ordered memory effects for every trace row. This includes all six permutations crossed with byte values 0, 1, and 128 for both mutators, null paths, leaf null/nonnull paths, and the mapped-memory boundary for the out-of-range read.

The frame handling is supported by the actual instructions. Each nonnull mutator first executes `STMDB SP!, {r4,lr}`. The trace ledger shows the actual writes of entry r4 `0x44444444` and entry LR `0x12345678` to SP-8 and SP-4. After the stipulated unlock return, the source `LDMIA SP!, {r4,pc}` reads those two saved words, restores r4/SP, and returns to the saved LR token. The opaque call may clobber current LR; the source returns through the saved stack word. Null mutators take the source pop without either opaque call. Leaf paths use BX through their stipulated entry LR.

Byte `P+0x24` is not written by the retained create body’s explicit stores. The pinned WP362 store inventory and the exact create words show initialization of `P+0x20`, the 64-bit fields at `P+0x18..+0x1f`, `P+0x28`, and words at `P+0x2c`, `P+0x30`, and `P+0x34`; no explicit source store initializes `P+0x24`. The WP377 pre-acquire object image uses `0xaa` only as a sentinel, then records an explicit post-acquire premise event that installs the tested byte 0/1/128 alongside the current tuple. It does not claim that create or allocator behavior supplies this byte.

The opaque boundaries are correctly treated as premises rather than extracted effects. Acquire is stipulated to return normally, preserve current r4=P, SP and the pushed frame, and make the current `(I18,I1c,I20,B24)` values available. Unlock is separately stipulated to return normally while preserving SP, the pushed frame, and the bytes `P+0x18..P+0x24`; this is needed only to interpret the reported final object bytes. Source after unlock writes r0=0 and restores saved r4/PC. These assumptions are not verified properties of either callee, lock behavior, or an ABI.

Two trace qualifications remain. First, recorded fixtures change r0-r3, r12 and LR at acquire (while preserving current r4=P, SP/frame) and leave seeded r5-r11 unchanged. At unlock they change r0-r4, r12 and LR while preserving r5-r11 and SP/frame. The model’s phrase “other scratch clobbered” is broader than its concrete boundary vectors. This does not change selected outputs because resumed instructions do not consume the seeded r5-r11 values, but the report/contract should enumerate the concrete fixture vector or call it one finite choice.

Second, D16 is not recorded in `opaque-events.tsv`; the model leaves it unchanged across both opaque calls. The D16 values at following source steps therefore reflect a fixture choice, not a verified callee effect. Selected outputs are insensitive to this gap: `flip` overwrites D16 with VLD1.32 after acquire before using it; `snapshot` has no D16 source operation; and neither body reads D16 after unlock. `opaque-boundary-audit.tsv` records these source-liveness checks. The trace reflects the chosen unchanged-state placeholder, not evidence that either callee preserves D16.

The positive memory outputs are conditional on the two opaque premises. There is no evidence here that a real acquire supplies the current tuple or preserves r4/frame, or that unlock leaves those bytes unchanged. The finite formulas and raw source routes are VERIFIED; arbitrary bounds, allocation/constructor reachability, runtime/API/ABI/lock guarantees and physical effects remain OFFEN. Target/runtime/native/VM/device/network tests are NOT_RUN.

## Review matrix

| Area | Result | Evidence / limit |
|---|---|---|
| Root362 source identity and all 48 selected words | PASS — VERIFIZIERT | Replayed from pinned raw ELF and 109-word source table |
| 45 scenarios and 562 per-step traces | PASS — VERIFIZIERT | Independent decoder checks PC, GPR0-14, NZCV, D16 and control flow |
| 290 source memory effects | PASS — VERIFIZIERT | Independent ordered address/width/byte replay |
| 180 opaque memory premises and 72 call boundaries | PASS, conditional — VERIFIZIERT as model premises | Acquire tuple installation and unlock byte preservation are stipulations only |
| Actual saved r4/LR handling | PASS — VERIFIZIERT | Push stores entry values; actual pop restores r4 and returns via saved LR |
| Create initializes byte +0x24 | Not established — OFFEN | No explicit write in the retained create body; allocator behavior unknown |
| Six-permutation finite transform results | PASS — source-local | Exact branch/state/memory replay; no API or locking meaning inferred |
| D16 across opaque boundaries | Finite unchanged-state placeholder | OFFEN as callee effect; outputs unaffected because overwritten or unused |
| OOB `get_read` result | PASS — boundary only | Trace stops at unmapped synthetic address 0x3048 before load commits |
| Opaque scratch wording | Qualification needed | Concrete model vectors preserve r5-r11 despite broad “other scratch clobbered” wording |

Validation: `PYTHONDONTWRITEBYTECODE=1 python3 validate.py` — PASS. The checker is separate from and does not import the WP377 model or writer. No target execution or REA import occurred.
