> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-282 — source-driven 136-byte `memcpy` path

## Corrected path finding

WP279’s source-word inventory remains valid, but its high-level replay was incomplete: it treated each four-D-register NEON structure instruction as 64 bytes and constructed the expected output/register values rather than stepping the selected conditional path. This package keeps WP279 frozen and replaces that replay with a bounded mathematical A32 stepper over the same exact body words.

For `D = DalBias + 0x1a270`, `S = ProviderBias + 0x14154`, `r2 = 136`, and page-aligned biases, `D mod 16 = 0` and `S mod 16 = 4`. Thus `(r12 & 7)=0` and `(r1 & 7)=4`; the branch at ELF `0x91a44` takes the unequal-alignment route `0x91e10`. The check `r12 << 29` at `0x91e18` yields zero, so the route skips the conditional scalar prefix at `0x91e24..0x91e44`.

The stepper fetches and decodes 48 source-bound PCs through `BX LR`. Its full per-instruction trace, with source word, condition result, NZCV before/after, next PC, and effect, is [execution-trace.tsv](./execution-trace.tsv). The validator uses the pinned 312-word WP279 inventory and verifies each inventory word against the exact ELF bytes and retained REA listing. The source is the private extracted `/usr/lib/libc.so.6` (inode 1548, size 1,434,296, SHA-256 `dc47ee066e2c2d73ff9186440787543c3020711611f09002b6ab187d97d9dfa2`). Retained REA identifies a contiguous 1,248-byte body at Ghidra `[0xa19c0,0xa1ea0)`; source ELF VA/file offsets are `[0x919c0,0x91ea0)`. The symbol metadata pins `memcpy@@GLIBC_2.4` as FUNC at `0x919c0`, size 1,248, in executable `.text`.

The taken path’s length/flag logic is material:

- At `0x91e4c`, `136 - 64 = 72`, carry set; `POPCC` and `BCC` at `0x91e50/54` are skipped.
- The two initial vector loads at `0x91e5c/60` each read **32 bytes** (`{d0-d3}` and `{d4-d7}`), advancing `r1` to `S+64`. At `0x91e64`, `72 - 64 = 8`, carry remains set; `BCC` at `0x91e68` is not taken.
- The loop body therefore runs once. Its `PLD [r1,#0x100]` at `0x91e6c` observes effective address `S+0x140` because `r1` is now `S+0x40`. It stores 32 bytes from `d0-d3`, loads the next 32 source bytes, stores 32 bytes from `d4-d7`, and loads another 32 source bytes. These four structure transfers at `0x91e70/74/78/7c` advance `r12/r1` by a further 64 each.
- At `0x91e80`, `8 - 64` underflows and clears carry. `BCS` at `0x91e84` is not taken; the two final stores at `0x91e88/8c` write the staged 64 bytes. `r2 &= 63` at `0x91e90` leaves 8.
- After restoring `r8`, the branch to `0x919cc` selects `r3 = 0x34 - (8 & 0x38) = 0x2c`. The computed-PC instruction at `0x919d4` reads architectural PC as instruction address + 8 and lands at `0x91a08`. There the one-D-register vector load/store pair copies the final 8 bytes. The following shift makes `r2` zero, and all halfword/byte conditional transfers are skipped before return.

## Memory and register results

The stepper’s chronological ordinary data-memory sequence for symbols `S`, `D`, `SP` is:

| Order | Operation | Interval / effective address |
|---|---|---|
| 1 | stack write, save `r8` | `[SP-4,SP)` (4 bytes) |
| 2 | vector source read | `[S,S+0x20)` (32 bytes) |
| 3 | vector source read | `[S+0x20,S+0x40)` (32 bytes) |
| 4 | vector destination write | `[D,D+0x20)` (32 bytes) |
| 5 | vector source read | `[S+0x40,S+0x60)` (32 bytes) |
| 6 | vector destination write | `[D+0x20,D+0x40)` (32 bytes) |
| 7 | vector source read | `[S+0x60,S+0x80)` (32 bytes) |
| 8–9 | vector destination writes | `[D+0x40,D+0x60)`, `[D+0x60,D+0x80)` (32 bytes each) |
| 10 | stack read, restore `r8` | `[SP-4,SP)` (4 bytes) |
| 11 | tail source read | `[S+0x80,S+0x88)` (8 bytes) |
| 12 | tail destination write | `[D+0x80,D+0x88)` (8 bytes) |

The `PLD` hints are separate from ordinary reads. On this selected path the stepper records, in order, `S+0`, `S+0x40`, `S+0x80`, `S+0xc0`, `S+0x100`, and `S+0x140`. No hinted value is consumed by the program model. Cache state, platform-specific prefetch effects, and faults are outside scope.

Under the stated nonoverlap and mapped-range conditions, the stepped memory result satisfies `memory_after[D+i] = memory_before[S+i]` for `0 <= i < 136`; the source interval is unchanged. No ordinary writes occur outside `[D,D+136)` and the explicit stack save word. The stack word is overwritten with incoming `r8`, read back by the pop, and SP is restored; it is not claimed to retain its pre-call sentinel.

On this path, instruction-derived return state is `r0` unchanged, `r1=S+136`, `r2=0`, `r3=0x2c`, `r8` restored, `r12=D+136`, SP restored, LR unchanged, and return via `BX LR`. `r4-r7` and `r9-r11` are untouched; `d8-d9` are untouched. The code writes `d0-d7`. These are only observed effects of this path and do not establish an ABI contract or runtime provider/caller identity.

## Preconditions and controls

The model assumes execution of these decoded A32 instructions with the observed NEON operations supported; it requires 32-bit nonwrapping addresses, page-aligned biases, exact assigned offsets, source readable and destination writable for 136 bytes, disjoint source/destination half-open intervals, and the selected `D mod 8 = 0`, `S mod 8 = 4` lane. `[SP-4,SP)` must be readable/writable, disjoint from both data intervals, and SP must satisfy the observed 4-byte push/pop. The fixture return address is stipulated to be an aligned ARM-state address in a synthetic executable interval; the model does not establish any real mapping or processor deployment.

`validate.py` is a read-only source/stepper validation by default. The separate `--emit-trace` option explicitly writes the trace TSV. Two fixtures use different page-aligned bias pairs and different source patterns. Both run the instruction stepper against a byte-addressed memory map; output checks are derived from stepped memory/register state and immutable entry snapshots for GPRs and D-registers. Seven negative precondition controls reject exact aliasing, short read/write extents, stack overlap, non-page-aligned bias, a different source-alignment lane, and a misaligned return target. The preservation checker also has a positive mutation control: an injected post-step `r5` clobber must fail against immutable entry snapshots. No ELF/native code execution occurs.

The bounded decoder supports only instructions reached on this route: the used A32 data-processing, immediate branch, condition evaluation, word/byte transfer, `BX`, PLD, and six exact NEON structure words. It is not a general ARM emulator. It models instruction effects for this path, not timing, partial faults, concurrency, cache behavior, or runtime dispatch.

## Evidence status

- **VERIFIZIERT:** source identity, REA body bounds, symbol/section metadata, all 312 word bindings, and the 48-PC bounded path trace.
- **VERIFIZIERT:** 136-byte copy and register/stack effects under the stated model preconditions; `python3 validate.py` reports PASS.
- **OFFEN:** whether any actual caller reaches this provider with these inputs, whether a concrete process meets the modeled mapping conditions, or the surrounding API/lifecycle meaning.

This is self-review of retained source evidence and a mathematical instruction model. It is not native execution or an independent second review.
