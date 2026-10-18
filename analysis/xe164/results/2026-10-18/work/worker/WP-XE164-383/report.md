> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-383 — independent review of WP380

**VERIFIZIERT:** The frozen WP380 package (manifest SHA-256 `a5c5fdd967321a7b1f5f5fe3b0cb9ededa2b73352f7d0f93a1773cc54bdc652b`) is correctly bound to the exact FW31 `libpackbus.so.1.0.1` bytes. I independently verified the PT_LOAD mapping, full GetCnfFromRail source extent, every word/pool byte, six literal-PC calculations, selected store expressions, and branch conditions. I found no raw-source, extent, base, or store-encoding contradiction.

The useful precision for the later stores is local: `c89c` reads the current word at `r2+8`, adds current `r0`, and stores through that same current `r2`; `cA4c` does likewise at current `r1+0xc`. WP380 does not prove either current base is always `B+I*16` or a particular runtime object. That restraint is necessary: the body writes other values into `[SP+0x28]` at `c920` and conditionally at `c944`, and into `[SP+0x24]` at `cd74`, conditionally at `ce3c` and `ce58`.

## Independent source checks

The subject is 148,792 bytes with SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. The reviewer parses its ELF32 little-endian ARM program headers independently and checks the function code at ELF `0xc5b4..0xd4a7` and literal area `0xd4a8..0xd4cc` through unique file-backed PT_LOAD mappings. The complete REA body and both procedure metadata records agree on Ghidra entry `0x1c5b4`, inclusive end `0x1d4a7`, one contiguous range, 3,828 bytes / 957 words. Each of the 957 assembly PCs maps to the listed word and exact ELF bytes. The ten address references in the assembly equal the ten separate pool rows and each pool word is checked against raw bytes.

The six independently evaluated literal sequences are:

- `c724/c728 -> B=0x4013c`
- `c75c/c764 -> B=0x4013c`
- `c774/c77c -> B=0x4013c`
- `c988/c990 -> B=0x4013c`
- `c5e4/c5f0 -> 0x4017c`
- `c5f8/c5fc -> 0x33000`

For each LDR, the encoded unconditional PC-relative literal load yields the expected pool address using `PC+8`; the following raw `ADD r3,pc,r3` adds the literal to its own architectural `PC+8`. Independent PT_LOAD parsing also places ELF address `0x4013c` inside the second load segment's memory extent but beyond its file-backed extent, consistent with BSS. This is an address result only; no backing file bytes at B are inferred.

## Selected stores and conditions

At `c71c`, the current frame word at `[SP+0x3c]` loads into `r0`; at `c720`, current `r10` is shifted left by 3 into `r2`. `c724/c728` materialize B. The exact `c734` encoding is `STR r2,[r3,r0,LSL #4]`, so its local address expression is `U32(r3 + U32(r0<<4))`; `c738` then adds the separately computed `r0<<4` to the current `r3`, and `c740` stores zero at that current `r3+8`. This supports the stated B-plus-current-index expressions if the local register/frame values are as established at those source instructions. It does not trace `[SP+0x3c]` back across earlier calls to an immutable input argument.

The lane gates are source-explicit. `c70c/c710` branch to `c974` when bit `0x20` of the current byte is set. Otherwise `c714/c718` branch to `c984` when current `r6==1`, with the not-equal case falling into `c71c`. From `c974`, `TST r10,#1` and conditional `ADDNE r10,r10,#1` may round the current `r10` upward; `c97c/c980` then return non-1 `r6` to `c71c`, while equal-to-1 falls through to `c984`. Thus the non-1 lane writes at `+0/+8`; the equal-to-1 lane writes at `+4/+0xc`, with possible rounding only on the route through `c974`.

At `c984..c9a8`, current `[SP+0x3c]` becomes the shifted index, `c988/c990` materialize B, and `c994` forms current `B+index`. `c99c` makes current `r10<<3`; `c9a0` stores it at current base `+4`, and `c9a8` stores zero at `+0xc`.

The later additions are not unconditional evidence of a stable table base. At `c89c`, the current `r2` was formed from current `[SP+0x28] + [SP+0x1c]`; the function loads `[r2+8]`, adds current `r0`, and stores back at `[r2+8]`. Beforeward, `c878` reduces `r0` to its low nibble and `c880` replaces it with a halfword from `[r5+0xc]` only if that nibble is nonzero. At `cA4c`, current `[SP+0x24]` supplies `r1`, and the code loads/adds/stores at `[r1+0xc]`. Those expressions are verified; object identity and complete register/value history are not.

**PASS:** `validate.py` checks copied source pins and its own manifest, ELF identity/headers/PT_LOAD byte mapping, all 957 words and ten pools, six PC equations, selected store encodings/gates, frame prologue/exit words, and that it leaves the review package unchanged. No full control-flow/value replayer is claimed. **NOT_RUN:** native ELF execution, runtime, target, VM, network, or device access. API/ABI, input mapping, actual object identity, call effects, and units remain **OFFEN**.
