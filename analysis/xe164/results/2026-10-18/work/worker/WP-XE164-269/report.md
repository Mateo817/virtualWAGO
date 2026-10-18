> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-269 — provider cleanup call boundaries

## Result

**VERIFIZIERT (bounded static evidence).** On the pinned 18,076-byte `libdal.so.1.0.1`, the accepted caller span `[ELF-VA 0x1dc0,0x1ea4)` contains the eight direct calls listed below. Six targets are exact 12-byte ARM PLT entries and resolve through their matching `.rel.plt` `R_ARM_JUMP_SLOT` records to six dynsym names, including version suffixes where present. The seventh distinct destination is the one permitted internal body at `0x3c34`; the eighth callsite repeats the `0x13b4` target. No API contract, runtime binding, interposition behavior, return guarantee, or cleanup effect is inferred from a symbol name.

The accepted source-body/literal bounds and its word listing are pinned to WP-224. The new `matrices.tsv` reconstructs the caller and internal machine-word sequences, plus only the six assigned PLT entries and their relocation resolution. All source bytes are read-only.

## Source and address identity

The exact ELF SHA-256 is `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`, size 18,076 bytes, ELF32 little-endian ARM ET_DYN. The caller body and five literal-pool words retain WP-224 bounds `[0x1dc0,0x1ea4)` and `[0x1ea4,0x1eb8)`, respectively. WP-224 reports the prior body as 57 A32 words and binds Ghidra addresses as ELF virtual address + `0x10000`. The same mapping is confirmed for this sole internal target: REA procedure metadata at Ghidra `0x13c34` reports one contiguous 76-byte body, ELF VA/file offset `[0x3c34,0x3c80)`, with 19 words. Its address is inside the assignment's 512-byte cap.

REA 6.5.0 / Ghidra 12.1.4 returned the internal extent in evidence `ev_da2563852624ff2ac17089c076c2397ef57a14a7acd02d3b01d577ae77794b66`, and the complete instruction sequence in `ev_6c314c16aaaa21721595f3c8e27ba380dc19096c42001a492909a176d2647002`. Profile digest: `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. The observed body is single-range and complete by Ghidra's function-body address set. Ghidra notes its terminal call at ELF VA `0x3c74` to `0x148c` and excludes fallthrough from its flow model; this does not establish whether the resolved destination returns.

## PLT and import identity

The `.plt` section is at VA/file offset `0x1340`, size `0x374`; `.rel.plt` contains 72 eight-byte relocation records. For this ARM PLT layout, entries begin at `0x1354` and advance by 12 bytes. Each selected entry's ordinal was calculated from that grid, then its third instruction's GOT displacement was used to locate the corresponding `R_ARM_JUMP_SLOT` relocation. The symbol name and version suffix below come from that relocation's linked dynsym row, not from the PLT label alone.

| PLT ELF VA | `.rel.plt` ordinal | GOT relocation offset | Relocation-linked dynsym identity | Caller sites |
|---:|---:|---:|---|---|
| `0x13b4` | 8 | `0x1402c` | `g_hash_table_destroy` | `0x1df4`, `0x1e14` |
| `0x151c` | 38 | `0x140a4` | `LibraryLoader_Destroy` | `0x1e34` |
| `0x1378` | 3 | `0x14018` | `fileno@GLIBC_2.4` | `0x1e7c` |
| `0x163c` | 62 | `0x14104` | `flock@GLIBC_2.4` | `0x1e84` |
| `0x1408` | 15 | `0x14048` | `fclose@GLIBC_2.4` | `0x1e90` |
| `0x148c` | 26 | `0x14074` | `free@GLIBC_2.4` | `0x1e98`; internal tail transfer at `0x3c74` |

Each exact PLT entry contains the same three-instruction ARM sequence shape: `add r12,pc,#0`, `add r12,r12,#0x12000`, then pre-indexed `ldr pc,[r12,#disp]!`. Entry-specific displacements and relocation offsets are in `matrices.tsv`. Identity is statically verified only as the image's dynamic symbol request. The actual process provider, symbol interposition, loaded implementation, ABI details, and effects remain **OFFEN**.

## Caller call-boundary and argument inventory

All paths below are local to the accepted 57-word caller body. The local literal-plus-PC calculation yields ELF VA `0x141e0` at each initialization site, as documented in WP-224; “base” below means only that recalculated address and carries no application-level object interpretation. `r0` is the only argument register whose value is locally established at selected calls, except the known `r1=8` at `0x1e84`. Other argument registers and effects across an opaque call are **OFFEN**.

| Callsite → target | Reachability condition | Call-visible register evidence | Local qualification |
|---|---|---|---|
| `0x1df4 → 0x13b4` `g_hash_table_destroy` | The value loaded at `0x1de0` compares nonzero; `beq 0x1df8` skips the call on zero. | `r0` remains the just-loaded word from `[base+0]`; `r2=0` was stored to `[base+0]` immediately before the call. | Base was computed at `0x1dc0–0x1dc4`; no opaque call intervenes. Callee effects are unknown. |
| `0x1e14 → 0x13b4` `g_hash_table_destroy` | The value loaded at `0x1e00` compares nonzero; `beq 0x1e18` skips the call on zero. | `r0` remains the just-loaded word from `[base+4]`; `r2=0` was stored to `[base+4]`. | Base is recomputed at `0x1df8–0x1dfc` after the earlier call. No call intervenes between this load/store sequence and this target. |
| `0x1e34 → 0x151c` `LibraryLoader_Destroy` | The value loaded at `0x1e20` compares nonzero; `beq 0x1e38` skips the call on zero. | `r0` remains the word from `[base+0x1c]`; `r2=0` was stored to that slot. | Base is recomputed at `0x1e18–0x1e1c` after the prior call. Callee effects are unknown. |
| `0x1e54 → 0x3c34` internal body | The value loaded at `0x1e40` compares nonzero; `beq 0x1e58` skips the call on zero. | `r0` remains the word from `[base+0x14]`; `r2=0` was stored to that slot. | Base is recomputed at `0x1e38–0x1e3c`. No callee expansion beyond `0x3c34` is included. |
| `0x1e7c → 0x1378` `fileno` | Initial `r6` loaded at `0x1e64` is nonzero; `beq 0x1e9c` skips this later block on zero. | `r0=r6`, with `r6` locally loaded from `[base+0x24]`; this occurs before any call in this block. | `r4` base computed at `0x1e58–0x1e60`. The target's effects on all registers remain unknown. |
| `0x1e84 → 0x163c` `flock` | Same branch-selected block as above. | `r1=8` is established at `0x1e80`. **`r0` is unknown after the opaque call at `0x1e7c`**; no argument value is inferred from the earlier `r0=r6`. | The name does not establish operation, flags, lock state, or effect. |
| `0x1e90 → 0x1408` `fclose` | Same branch-selected block. | `r0` is set from the **current** `r6` at `0x1e88`, after calls at `0x1e7c` and `0x1e84`; its relation to the earlier loaded word is unknown. | The store at `0x1e8c` also uses current `r4/r5` after those calls; the initial base relation is not proven. |
| `0x1e98 → 0x148c` `free` | Same branch-selected block. | `r0` is freshly loaded at `0x1e94` from `[current r4+0x20]`, after calls at `0x1e7c`, `0x1e84`, and `0x1e90`. | The syntactic offset is exact; the post-call `r4` relation to the body-local base is unknown. No freeing or ownership effect is asserted from the symbol name. |

The four initial conditional stores at `0x1df0`, `0x1e10`, `0x1e30`, and `0x1e50` are one word (four bytes) each; the argument values remain in `r0` because no intervening body instruction writes `r0`. This establishes only what reaches each local call boundary, not callee behavior. The final three calls are separated by opaque targets, so post-call register values are not carried forward by an ABI assumption.

## The one permitted internal body at ELF VA `0x3c34`

Local observation from the full 19-word body:

1. The prologue saves `r4,lr`; `r4` is assigned the entry `r0` value before any call. A zero entry value branches to the local epilogue at `0x3c78`, which restores the stack/registers and returns through `pc`. This path has no local field write or helper call.
2. On the nonzero path, `r3=0` and `r1=sp+4` are set, then `strb r3,[r4,#0xc]` writes one zero byte at entry-`r0+0xc`. Since no opaque call precedes this store, the entry pointer relation is locally established for this write.
3. At `0x3c50`, `r0` is loaded from entry-`r4+0` and `r1` still contains `sp+4`; both are call-visible at direct call `0x3c54 → 0x3598`. The target is opaque and was not expanded.
4. At `0x3c58`, `r0` is loaded from `[current r4+8]` and passed to `0x36d8`. Because `0x3598` intervenes, the current `r4` and its relation to entry `r0` are **OFFEN**.
5. At `0x3c60`, `r0` is loaded from `[current r4+4]` and passed to `0x1540`. Since two opaque calls intervene, the current base relation is **OFFEN**.
6. `0x3c68` moves current `r4` to `r0`, restores stack and saved registers, then `0x3c74` transfers control to the PLT entry at `0x148c`, relocation-bound to `free@GLIBC_2.4`. The call-visible value is current `r4` after the preceding opaque calls; relation to entry `r0` is not established. This is a branch into the PLT sequence, not evidence about a C prototype, return behavior, resource ownership, or cleanup effect.

The call at `0x3c74` is Ghidra's reported terminal flow. This report does not convert that provider classification into a runtime non-return claim. The targets at `0x3598` and `0x36d8` were not investigated. `0x1540` falls within the ELF `.plt` section but is outside the six-entry scope; its entry bytes, relocation, and import identity were not inspected.

## Evidence, validator, and limits

- `source-pins.tsv` binds the exact ELF, the accepted WP-224 report/validator/manifest, and retained REA evidence IDs.
- `matrices.tsv` contains all 57 caller words, the 19-word internal body, and exact 12-byte contents plus `.rel.plt` resolution for only the six assigned PLT entries.
- `validate.py` is read-only. It hashes and sizes the exact input, rebuilds both bounded instruction matrices via `arm-linux-gnueabihf-objdump`, reconstructs the eight direct call targets, parses the `.plt` section bounds and all `.rel.plt` records for selected GOT offsets, checks relocation-linked identities and the six PLT instruction sequences, and checks instruction anchors used for the call-boundary qualifications. It does not invoke target code or alter any artifact.
- **PASS**: `python3 validate.py`; **PASS**: package manifest verification. This is self-review; no independent reviewer or worker run is claimed.
- **NOT_RUN**: runtime, loader execution, host/VM/device activity, and API/ABI validation. None is part of this static scope.

Static names do not prove the actual runtime implementation. The exact process load bias, dynamic loader resolution, symbol interposition, callee register effects, data ownership, and cleanup side effects remain **OFFEN**.
