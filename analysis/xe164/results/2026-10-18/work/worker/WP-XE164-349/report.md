> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-349 — independent audit of frozen WP340 marshaller paths

**VERIFIZIERT (static, hash-bound):** Frozen WP340 manifest `c57025aa792692bb21fb674f479903d4cae4767de167d1772dd7f0d0b63284b6` matches, and every retained WP340 instruction word in the audited body matches bytes read directly from the pinned libdal file at its recorded file offset. I independently decoded the two selected inline A32 branch tables and checked every fetched trace PC/word and successor. The selected argument fixtures (5/7/9/14, zero arguments, unsupported tag 4) and separately stipulated normal-return fixtures (5/7/9/14/4) follow the source routes and register/data equations described below. **HYPOTHESE:** A real caller could reach the stipulated metadata and register state. **OFFEN:** Runtime reachability and binding, behavior of opaque helpers/callee, ABI/API interpretation, and actual callbacks. No runtime/native/VM/device/network/hardware execution was performed.

## Source and method

The target source is the exact private `libdal.so.1.0.1`, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. The copied WP340 word inventory is pinned and checked byte-for-byte against that file at its listed offsets. In the covered region, ELF VA equals file offset; the analysis/Ghidra listing uses ELF VA plus `0x10000`. The exact WP340 manifest and its report, source-word list, trace artifacts, and stepper are retained in `pins/`. The WP330, WP331, WP334 and WP339 manifest hashes are checked as fixed upstream evidence identities; I did not amend those packages.

The audit independently computes A32 immediate-branch targets as `PC + 8 + sign_extend(imm24)*4`. At `0x28ac`, word `0xebfffb14` therefore targets ELF `0x1504` (analysis address `0x11504`). The target is only the source branch destination; runtime resolution is outside scope. For the `ADDLS pc,pc,lr,LSL #2` at `0x282c`, the computed table base is `0x2834`; for the corresponding instruction at `0x28bc`, it is `0x28c4`. Each table entry is executable `B` code, not a data pointer.

## Argument dispatch and call boundary

The four supported selected tags route as follows: tag 5 → `0x2848` → `0x2918` and `STRB`; tag 7 → `0x2850` → `0x2900` and `STRH`; tags 9 and 14 → `0x2858`/`0x286c` → `0x2880` and `STR`. Each supported lane first loads one 32-bit source word from `[r4]` with post-increment, reserves an 8-byte stack cell, stores the low 1/2/4 bytes, then writes that cell address into the current vector cell. The four fixture results (`0x44`, `0x7788`, `0x99aabbcc`, `0xddeeff00`) match those source widths. At `0x2898`, `CMP r1,r12` followed by `BNE 0x2820` loops until the vector cursor equals its end; the final equality skips the branch.

At the call boundary, the source words at `0x28a0..0x28a8` directly establish `r1=[r5+4]`, `r0=r5+8`, and `r2=r8`; the earlier loop leaves `r3` at the vector base for nonzero arity. From the explicit fixture premise `r5=0x1000`, source value `[r5+4]=0x0abcde00`, and initial boundary SP `0x9000`, the return scratch allocation is 8 bytes, vector allocation is `align8(4*n)`, and each selected supported lane allocates one 8-byte value cell. This reproduces the recorded call state:

- Tags `[5,7,9,14]`: `r0=0x1008`, `r1=0x0abcde00`, `r2=0x8ff8`, `r3=0x8fe8`, SP `0x8fc8`, `r7=0`.
- Zero arguments: the count comparison at `0x27e4` sets EQ; `MOVEQ` at `0x27ec` and `BEQ` at `0x27f4` take the no-vector edge to `0x28a0`. The BL entry has `r3=0`, SP `0x8ff8`, and `r7=0`.
- Unsupported tag 4: `0x282c` selects `0x2844`, then `0x2950` sets `r7=0xffffffff`. The common cursor increment and loop continue to the call. This arm performs no store to the argument-vector cell; the fixture’s initially mapped bytes do not constitute source initialization. The BL is still reached with `r3=0x8ff0`, SP `0x8ff0`.

These are instruction-derived states conditional on the fixture’s `0x27c8` starting registers, memory, and nonzero success result. The preceding `0x2180`, `0x20b0`, and `0x2194` helper calls are opaque here. No register preservation across them is inferred. The synthetic start state also does not prove that its `r11` and SP relation is reachable from the body prologue; no actual caller continuation is claimed.

## Opaque-return suffix

The return fixtures begin at `0x28b0`, after a stipulated normal opaque return. They supply the record and result memory and stipulate preservation of the current `r5`, `r6`, `r7`, `r8`, and SP needed by this suffix; this is a fixture condition, not an ABI finding. At `0x28bc`, the second computed branch table routes tag 5 to `0x29c0` (`LDRB/STRB`), tag 7 to `0x29a8` (`LDRH/STRH`), and tags 9/14 to `0x299c` (`LDR/STR`). With scratch word `0x89abcdef`, source writes respectively one byte `0xef`, two bytes `0xcdef`, or four bytes `0x89abcdef`, then reaches `0x2874`, which moves `r7` to `r0`. Unsupported tag 4 routes to `0x2870`, sets `r7=-1`, performs no destination store, and reaches `0x2874`; output sentinel bytes remain unchanged. Traces stop before the frame-reset/pop epilogue, so they do not show a complete function return.

## Evidence limits and verification

**PASS:** `python3 -B validate.py` checks the raw ELF bytes, both complete computed branch tables, source-PC/word equality and trace continuity, boundary register/allocation equations, selected-width data, and no-store behavior for unsupported cases. The package checker independently verifies raw-file bytes, both complete computed branch tables, source-PC/word equality and trace continuity, boundary register/allocation equations, selected-width data, and no-store behavior for unsupported cases. WP340’s `validate.py` was inspected as read-only and run with bytecode generation disabled; it passed, and a before/after file-hash inventory showed the frozen WP340 package unchanged. WP340’s separate `build_traces.py` was not run. WP340 itself reports the selected fixtures as a source-driven replay; this audit confirms the audited paths against the retained raw words and emitted traces, but does not claim general verification of every instruction in the 168-word acquired source scope.

**NOT_RUN:** runtime/library binding, constructor or caller reachability, native ELF execution, C/ABI/varargs behavior, callbacks, VM, device, network, hardware. Status scope: selected static source routes only.
