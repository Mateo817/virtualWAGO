> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-281 — conditional shared early-failure join

## Finding

For each of the three WP274 candidate bodies, the exact static body has a first direct call to the local leaf at ELF `0x2180`. That leaf makes no nested call and reads one byte derived from its PC literal. If the byte at `P+0x14208` is zero, the leaf returns zero to the immediate first `CMP`/`BEQ` pair. The candidate then sets `r0=0xffffffff`, restores its saved frame, loads the original saved LR into PC, and returns. No call to helpers `0x2194` or `0x1ecc` occurs on this conditional path.

This is a bounded conditional source result. It does not establish that the runtime byte is zero, that a loaded application selects these candidate bodies, or that loaded bytes match the pinned ELF. It is not a global all-path failure claim and says nothing about callback-selected paths or code replacement/patching; the actual loaded provider/code binding remains conditional. The byte-one control instead passes the first gate and reaches the next direct call to `0x2194`; the replay stops immediately before that call and assumes nothing about its result.

## Source and helper contracts

The exact ELF is `libdal.so.1.0.1`, 18,076 bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. WP277's complete 32-word helper witness and WP274's 85-word caller witness are copied under `upstream-277/` and `upstream-274/`; their package hashes and every word are checked against this same ELF. The WP277 REA procedure/body Evidence IDs and WP274 REA body IDs remain hash-pinned; no fresh analysis import or new callee/caller expansion was used.

At `0x2180`, `LDR r3,[pc,#8]` reads literal `0x12054` from `0x2190`. The following `ADD r3,pc,r3` at `0x2184` uses A32 PC `0x218c`, so `r3=P+0x141e0`. `LDRB r0,[r3,#0x28]` at `0x2188` reads `[P+0x14208]` and returns a zero-extended byte in `r0`. The body then executes `BX lr`. It has no nested call, stack operation, store, or instruction writing `r4-r7`, SP, or LR. Thus, for this call, the candidate's BL-set LR remains the return address and the leaf leaves the caller's current frame and `r4-r7` intact.

The other two WP277 helper contracts were independently checked against their full word streams. `0x2194` uses its own literal and PC value to derive `P+0x141e0`, saves entry `r0` at `S-12`, and conditionally calls PLT `0x15f4` with `r0` equal to the current cell value and `r1=S-12`. If the call returns with a usable frame, it returns zero for a zero cell, zero nested result, or zero byte at current returned `r0+0x170`; otherwise it returns that byte. `0x1ecc` has the same frame/cell setup, then returns zero for zero cell/result or `u32(current r0+0x110)`, which may wrap to zero. Both wrappers' raw PLT entry and jump-slot metadata identify only the undefined dynamic symbol name `g_hash_table_lookup`; no target behavior, prototype, or ABI contract is inferred. The wrappers' saved frames are 16 bytes total and restore SP only if the opaque PLT call returns without damaging that frame.

## Three candidate prefixes and saved-frame return

Let `S` be entry SP. The source instruction words and addresses are in `early-failure-matrix.tsv` and `upstream-274/instructions.tsv`.

- Candidate `0x2f98` first executes `PUSH {r4,lr}` at `0x2f98` (SP=`S-8`), then `MOV r4,r0`, then `BL 0x2180` at `0x2fa0`. The link value is `0x2fa4`. On byte zero, `CMP r0,#0` at `0x2fa4` sets equality and `BEQ` at `0x2fa8` targets `0x2fe8`; `MVN r0,#0` at `0x2fe8` yields `0xffffffff`, and `POP {r4,pc}` at `0x2fec` restores SP to `S` and loads the saved entry LR into PC.
- Candidate `0x2e04` uses the same 8-byte frame pattern. Its first `BL 0x2180` at `0x2e0c` links to `0x2e10`; the first `CMP`/`BEQ` at `0x2e10`/`0x2e14` targets `0x2e54`; `MVN` at `0x2e54` and `POP {r4,pc}` at `0x2e58` return `0xffffffff` with SP=`S`.
- Candidate `0x2e5c` saves `r4-r8,lr` at `0x2e5c` (24 bytes, SP=`S-24`), reads `[sp+0x18]=[S]` into `r7`, and copies entry `r0/r2/r3` into `r4/r5/r6` before its first call. `BL 0x2180` at `0x2e70` links to `0x2e74`; the first `CMP`/`BEQ` at `0x2e74`/`0x2e78` targets `0x2ef8`; `MVN` at `0x2ef8` and `POP {r4-r8,pc}` at `0x2efc` restore SP to `S` and return `0xffffffff`.

On the byte-one control, the leaf returns `r0=1`, each first `BEQ` is not taken, and the caller executes `MOV r0,r4` before reaching its next BL (`0x2fb0`, `0x2e1c`, or `0x2e80`) to `0x2194`. Because the leaf does not modify `r4`, this particular input equals the current `r4` set by each caller's own prologue; the result after that next call is outside this join.

## Valid frame and nonalias premises

For the 8-byte candidates, the prologue writes `[S-8,S)` (saved `r4` and entry LR); for `0x2e5c`, it writes `[S-24,S)` (saved `r4-r8` and entry LR), then reads `[S,S+4)`. The first helper itself neither reads nor writes SP or stack memory. The local failure POP reads the saved register/LR words, loads the old LR into PC, and restores SP to `S`.

The conditional join requires a valid writable/readable saved frame and valid saved return address; for `0x2e5c`, `[S,S+4)` must also be readable. It does not assume a calling convention or stack alignment rule. The byte read must be readable and must not overlap the caller's preceding push writes: `[P+0x14208,P+0x14209)` is disjoint from `[S-8,S)` or `[S-24,S)` as applicable. If aliased, the push may overwrite the nominal byte before the helper reads it; the negative controls in `byte-counterprobes.tsv` demonstrate why that premise matters. The `0x2e5c` read of `[S]` may share memory with the byte read; it is a read, not a write.

## Candidate/table join and limits

WP274 and WP277 bind the local bodies and table-position candidates at `+0x30 -> 0x2f98`, `+0x3c -> 0x2e5c`, and `+0x40 -> 0x2e04` from static source and relocation metadata. Treating those as the selected runtime entries additionally requires the same provider instance, correct relocation/load bias, matching table identity, publication/copy path, and runtime selection. The shared byte is likewise a current memory value, not a fact about the installed device. No callback or later-helper result is generalized from this early path.

The requested STOP-QUOTA.json was absent at the specified path when checked. No runtime/native execution, VM, hardware, target network, or public-repository modification occurred. Static checks pass; runtime source-byte value and candidate binding remain **OFFEN**.

## Verification

`python3 validate.py` checks the exact source hash, both retained instruction witnesses, PC/literal equations, the three caller branches/return blocks, wrapper-local code and PLT relocation metadata, frame arithmetic, byte-zero and byte-one control probes, and alias/no-alias controls. These are read-only source and mathematical checks, not execution of the firmware.
