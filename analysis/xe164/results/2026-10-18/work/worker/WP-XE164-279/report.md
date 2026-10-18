> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-279 — exact `memcpy` lane for the 136-byte source copy

## Finding

For the supplied offsets and page-aligned `DalBias` and `ProviderBias`, the actual 32-bit ARM body takes the unequal-low-three-bits path. `D = DalBias + 0x1a270` has `D mod 16 = 0`; `S = ProviderBias + 0x14154` has `S mod 16 = 4`, so `S mod 8 = 4` while `D mod 8 = 0`. This corrects the task’s initial “both 16-byte aligned” premise; no offset was changed to force another path.

The source is the private extracted `/usr/lib/libc.so.6`, inode 1548, size 1,434,296, SHA-256 `dc47ee066e2c2d73ff9186440787543c3020711611f09002b6ab187d97d9dfa2`. Its dynamic symbol is `memcpy@@GLIBC_2.4`, FUNC, value `0x919c0`, size `0x4e0` (1,248 bytes), version `GLIBC_2.4`; this body is in executable `.text`. The retained Ghidra 12.1.4 REA procedure/body records bind that entry to Ghidra range `[0xa19c0,0xa1ea0)` and report a contiguous 1,248-byte body. The mapping observed in the retained source is Ghidra address = ELF VA + `0x10000`; the ELF VA and file offset coincide for this `.text` range. `instruction-inventory.tsv` checks all 312 sequential words against these source bytes. `objdump-body.txt` is an independent rendering of those same source bytes, not runtime evidence.

## Exact path, control values, and copy effect

At entry, the body sets `ip/r12 = r0`, compares `r2` with `0x40`, and branches to the large-copy path for 136. It saves incoming `r8` on the stack, computes `r1 & 7` and `r12 & 7`, and branches at ELF `0x91a44` to the unequal-alignment block at `0x91e10` because the values are 4 and 0. In that block, `r12 << 29` is zero, so the branch at `0x91e20` skips the conditional scalar alignment prefix. No source/destination alignment is fabricated: the NEON lane accepts the supplied source address as encoded in this body.

The length and control-flow arithmetic on this concrete route is:

| ELF VA | Instruction effect | `r2` after | Result |
|---|---|---:|---|
| `0x91e4c` | subtract `0x40` | 72 | no underflow; continue |
| `0x91e64` | subtract `0x40` | 8 | underflow on the next `0x40` test; branch to `0x91e88` |
| `0x91e90` | `r2 &= 0x3f` | 8 | restore saved `r8`, branch to common small-tail dispatcher |
| `0x919d4` | `r3 = 0x34 - (8 & 0x38) = 0x2c`; add to architectural PC | 8 | lands at `0x91a08` (PC for ARM add is instruction address + 8) |
| `0x91a1c` | `r2 = r2 << 31`, setting flags | 0 | 8-byte vector tail has already run; halfword/byte conditionals are skipped |

On the large path, the two `VLD1.8` multiple-register loads read exactly `[S,S+64)` and `[S+64,S+128)`. The matching stores write exactly `[D,D+64)` and `[D+64,D+128)`. The dispatcher then executes the 8-byte `VLD1.8 {d0}` / `VST1.8 {d0}` pair, reading `[S+128,S+136)` and writing `[D+128,D+136)`. Thus this path performs ordinary source data reads over exactly `[S,S+136)` and ordinary destination writes over exactly `[D,D+136)`. Loads occur before the corresponding 64-byte stores in each group; for nonoverlapping ranges, the byte result is `mem_after[D+i] = mem_before[S+i]` for each `i in [0,136)`. Bytes outside the destination interval are not changed by the modeled body path.

The `PLD` instructions issue address hints at `S+0x00`, `S+0x40`, `S+0x80`, `S+0xc0`, and `S+0x100` on this path. Those are recorded separately in `memory-access-model.tsv`; they do not supply values to the program and are not counted as ordinary data reads. The last hints extend beyond the 136-byte source interval. This analysis does not model cache behavior or platform-specific prefetch side effects.

The only stack access on this path is the 4-byte save of incoming `r8` at `[SP-4,SP)` and the matching reload; SP is restored. No `BL` or other call appears on the selected path, and `LR` is not written before `BX LR`. By direct instruction accounting, incoming `r0` is unchanged; `r1` and `r12` advance by 136; `r2` is zero at return; `r8` is restored; `r3` is used by the small-tail dispatch. `r4-r7`, `r9-r11`, and `d8-d9` are not written on this path. The body uses/clobbers `d0-d7`; exact final values of caller-clobbered state are not treated as a contract. These are observations about this exact instruction path, not an ABI assertion or a claim about how a caller obtains this provider.

## Preconditions, counterchecks, and model limits

For each arithmetic replay, both biases are page-aligned 32-bit bases and all additions are nonwrapping. `S..S+136` is readable, `D..D+136` is writable, and these half-open ranges are disjoint. The stack word `[SP-4,SP)` is readable and writable and disjoint from both data ranges; SP is suitable for these instructions. The fixture return address is an aligned ARM-state address in a stipulated executable interval, making the return premise explicit; actual mapping/executability is not established by this model. The selected processor context supports the NEON instructions shown. These are explicit model preconditions, not claims about an actual process mapping or runtime dispatch.

The validator runs two positive mathematical fixtures with distinct page-aligned bias pairs and distinct source patterns. It checks exact 136-byte output, unchanged surrounding destination bytes, untouched source, the `D mod 8 = 0` / `S mod 8 = 4` route predicate, `r1/r12` increments, zero final `r2`, restored `r8`/SP, and untouched listed preserved registers. It also checks that a deliberately aliased range is rejected; that a source range shortened by one byte is rejected; that an invalid stack mapping is rejected; and that a non-page-aligned source bias that makes `S mod 8 = 0` is not mislabeled as this selected lane. No native code or ELF is executed.

The byte replay abstracts each decoded vector load/store to its corresponding contiguous byte interval and models the explicitly decoded integer/stack effects. It does not model instruction timing, faults partway through a multi-register instruction, memory ordering, cache state, concurrent mutation, CPU feature dispatch outside this body, dynamic symbol resolution, or caller/provider identity. The retained Ghidra pseudocode is supplementary; the path and ranges above are derived from the retained instruction list reconciled against the exact source words. `objdump-body.txt` provides the independent rendering used to resolve Ghidra’s omitted post-index punctuation on NEON instructions.

## Evidence and status

- **VERIFIED (artifact metadata/body bounds):** source hash, ELF symbol metadata, executable-section membership, Ghidra body bounds, and 312 source-word matches. Source and REA evidence hashes are in `source-pins.tsv`.
- **VERIFIED (bounded instruction-path replay):** the 136-byte route and effects under the listed preconditions, by source instruction decoding plus mathematical byte/register replay; `validate.py` passes.
- **OPEN:** whether any concrete runtime call uses this provider/body with the supplied addresses, whether the surrounding process satisfies the model preconditions, and any higher-level API or lifecycle meaning.

This is an independent self-review of the exact WP278 source evidence and a source-derived model. It is not native execution, runtime evidence, or an independent second reviewer.
