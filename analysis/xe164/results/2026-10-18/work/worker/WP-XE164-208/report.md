> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-208 — r5/r7 Alias and Cross-Call Preservation

## Scope and source identity

Offline, static analysis only. The sole code range examined is IoDrvDal ELF-VA
`[0x2f08,0x2f7c)`. No callee body or adjacent code was analyzed. Source artifact
`FW31-IODRVDAL-1.0.2` is 25,976 bytes, SHA-256
`853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` (PASS).
The requested VA window maps to file offset `0x2f08` in `.text` (VMA and file
offset both `0x0a34` for the section). Its exact 116 raw bytes have SHA-256
`415f85d8d5fdb5581989c9b635467f6e25e7e93e96cbe98ff3be8e10d8b7a907`.

The previous WP208 pass recorded the single REA coverage gap: Ghidra 12.1.4
returned zero bytes for `read_bytes(0x2f08, 88)`. For this corrected, expanded
window, the documented fallback was used: GNU `arm-linux-gnueabihf-objdump`
2.44 and an exact 116-byte raw read at file offset `0x2f08`. Addresses,
opcodes, and bytes below agree. No neighboring bytes were used for the
disassembly.

## Complete instruction table for the requested window

All words are ARM little-endian instruction words as printed by objdump.

| ELF VA | Opcode | Instruction |
|---:|---:|---|
| `0x2f08` | `ebfff6b1` | `bl 0x9d4` (`adi_GetApplicationInterface@plt`) |
| `0x2f0c` | `e1a02008` | `mov r2, r8` |
| `0x2f10` | `e1a01005` | `mov r1, r5` |
| `0x2f14` | `e590300c` | `ldr r3, [r0, #0x0c]` |
| `0x2f18` | `e3a0000a` | `mov r0, #10` |
| `0x2f1c` | `e12fff33` | `blx r3` |
| `0x2f20` | `e2506000` | `subs r6, r0, #0` |
| `0x2f24` | `1a0000f1` | `bne 0x32f0` (outside window) |
| `0x2f28` | `e1a07005` | `mov r7, r5` |
| `0x2f2c` | `ea00000c` | `b 0x2f64` |
| `0x2f30` | `e59d101c` | `ldr r1, [sp, #0x1c]` |
| `0x2f34` | `e5970004` | `ldr r0, [r7, #4]` |
| `0x2f38` | `ebfff6b1` | `bl 0xa04` (`strcmp@plt`) |
| `0x2f3c` | `e3500000` | `cmp r0, #0` |
| `0x2f40` | `1a000006` | `bne 0x2f60` |
| `0x2f44` | `e5973000` | `ldr r3, [r7]` |
| `0x2f48` | `e5843618` | `str r3, [r4, #0x618]` |
| `0x2f4c` | `ebfff6a0` | `bl 0x9d4` (`adi_GetApplicationInterface@plt`) |
| `0x2f50` | `e5903010` | `ldr r3, [r0, #0x10]` |
| `0x2f54` | `e5970000` | `ldr r0, [r7]` |
| `0x2f58` | `e12fff33` | `blx r3` |
| `0x2f5c` | `e1a06000` | `mov r6, r0` |
| `0x2f60` | `e2877008` | `add r7, r7, #8` |
| `0x2f64` | `e59d306c` | `ldr r3, [sp, #0x6c]` |
| `0x2f68` | `e0853183` | `add r3, r5, r3, lsl #3` |
| `0x2f6c` | `e1570003` | `cmp r7, r3` |
| `0x2f70` | `3affffee` | `bcc 0x2f30` |
| `0x2f74` | `e3560000` | `cmp r6, #0` |
| `0x2f78` | `1a0000dc` | `bne 0x32f0` (outside window) |

The exact raw bytes in increasing address order are:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

## Register, address and call observations

- At `0x2f10`, `r5` is copied into argument register `r1`. The subsequent
  indirect call at `0x2f1c` uses a function pointer loaded from the object
  returned in `r0` at `+0x0c`; at the call, `r0=10`, `r1=r5`, and `r2=r8`.
- After that call returns zero (`0x2f20`/`0x2f24`), `0x2f28` copies the
  then-current `r5` into `r7`. Locally, this establishes a register-value
  alias at that instruction. Whether the opaque `+0x0c` callee preserved
  `r5`, so that this is the same address passed in `r1`, is OPEN.
- In the scanned path, `[r7+4]` is loaded as the second argument to
  `strcmp` (`0x2f34`–`0x2f38`). If the comparison is equal, `[r7+0]` is loaded
  at `0x2f44`, then stored at `[r4+0x618]` (`0x2f48`). After another call to
  `adi_GetApplicationInterface`, the function pointer at returned-object
  `+0x10` is loaded (`0x2f50`), and `[r7+0]` is loaded again into `r0`
  (`0x2f54`) immediately before the indirect call (`0x2f58`).
- The loop path is visible through its backedge. `0x2f60` advances `r7` by
  eight bytes. At `0x2f64`–`0x2f68`, the code loads a word from `[sp+0x6c]`
  and computes `r3 = r5 + (loaded_word << 3)`. `0x2f6c` compares `r7` with
  that endpoint; unsigned-below at `0x2f70` branches back to `0x2f30`.
  The initial branch at `0x2f2c` enters this check before the first entry.
  Thus the local code verifies an eight-byte stride and the loop's unsigned
  bound expression, without assigning a type or semantic name to the stack
  word. If the comparison is not unsigned-below, execution leaves the scan at
  `0x2f74`, compares `r6` with zero, and conditionally branches to `0x32f0` at
  `0x2f78`.
- Calls within the window are `adi_GetApplicationInterface` at `0x2f08`, the
  `+0x0c` indirect call at `0x2f1c`, `strcmp` at `0x2f38`,
  `adi_GetApplicationInterface` at `0x2f4c`, and the `+0x10` indirect call at
  `0x2f58`. The local instructions do not reveal callee bodies or prove
  register or memory preservation across any of them. `r5` is used again for
  endpoint computation and `r7` is used after `strcmp` and the second
  `adi_GetApplicationInterface` call. Whether those opaque callees preserve
  `r5` or `r7` is OPEN. No Calling Convention is bound.

## Finding and status

**VERIFIZIERT — local register/address alias:** the code copies the `r5`
register value into `r7` at `0x2f28`; within the selected local instructions,
`r7+0` and `r7+4` are the two accessed offsets. This is an address/register
relationship, not proof of stable contents.

**HYPOTHESE — conditional application of E-XE164-230/231:** if the opaque
`+0x0c` callee preserves `r5`, the `r7=r5` assignment establishes the same
base address as the value supplied through `r1`; if the prior conditional
getter contract applies, this is the same buffer base described by
E-XE164-230/231. Whether the callee preserves `r5` is OPEN. No Calling
Convention is bound. The conditional contract does not establish runtime
binding or buffer immutability.

**Alternative:** if the opaque `+0x0c` callee changes `r5`, then `r7=r5` copies
its post-call value, which may differ from the address passed through `r1`. If
a later opaque callee changes `r7`, subsequent loads and the loop test may use
a changed base. These are unverified alternatives, not observed callee
behavior.

**OFFEN — cross-callee contents and values:** the `+0x0c` callee may write to
memory addressed by `r5`; subsequent `strcmp` and `adi_GetApplicationInterface`
calls may have effects not visible here. The word read at `r7+0` at `0x2f44`
is not proven unchanged when it is read again at `0x2f54`. The store through
`r4+0x618` also cannot be proven disjoint from the buffer from this window.
No buffer contents are asserted as facts.

**VERIFIZIERT — local traversal arithmetic/control:** `r7` advances by `8`,
the end value is recomputed as `r5 + ([sp+0x6c] << 3)`, and the unsigned
`r7 < end` test returns to `0x2f30`. The exact number of body executions and
stability of the base/count across opaque calls are not asserted.

**Rest uncertainty:** the opaque callees' register and memory effects, whether
the stack word at `[sp+0x6c]` remains stable, the concrete runtime target, and
the meaning or contents of the traversed entries remain outside this evidence.

**Provenance:** this is a GPT-6 Luna, HIGH reasoning worker report. No
independent review is claimed.

**Runtime/Hardware: NOT_RUN.** This finding is static and limited to the
specified ELF window. No device, VM, network, runtime attach, or bus access was
used.

## Reproduction and validation

Fallback version: `GNU objdump (GNU Binutils for Debian) 2.44`.
Exact-range commands and input identity are checked by `validate.py`.
Validator result: see its `Overall` line. `SHA256SUMS` covers the report,
manifest, and validator; it omits itself. The exact 116-byte extraction is
reproduced directly from the source by the validator and is not stored as a
separate binary file.
