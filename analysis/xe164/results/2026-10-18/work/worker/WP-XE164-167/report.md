> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-167 — `CMAddComponent` bounded instruction analysis

## Scope, evidence, and validation

Target: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`, 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`. ELF32 little-endian ARM, executable. `readelf -Ws` reports Dynsym `CMAddComponent` at `0x002fd0f0`, size 520, GLOBAL FUNC; the next GLOBAL FUNC is `CMGetInstanceList` at `0x002fd2f8`. The analyzed half-open virtual range is `[0x002fd0f0,0x002fd2f8)`, exactly 130 four-byte instructions. It maps to file offsets `[0x002ed0f0,0x002ed2f8)`: the executable LOAD maps VA `0x10000` to file offset 0, and `.text` independently maps VA `0x7cb10` to file offset `0x6cb10`.

REA check: `get_evidence_bundle(detail=summary, target_sha256=..., procedure_address=0x002FD0F0)` returned zero matching retained records (`total_retained_records=0`). This is a documented exact-hash/address retention gap, not evidence about function behavior. GNU `objdump` 2.44 on the host could not decode the ARM ELF (`architecture UNKNOWN`); GNU `arm-linux-gnueabihf-objdump` 2.44 decoded the requested bounded range. `readelf` is GNU Binutils 2.44; Rizin 0.9.1 is installed but was not needed. No Ghidra run, target execution, network, device, VM, or callee-body inspection was performed.

The table below is the complete bounded disassembly. Encoded words are printed in the file's little-endian byte order as four-byte groups; addresses increment by four throughout this ARM-state range. Self-check: 130 rows, first VA `0x002fd0f0`, last VA `0x002fd2f4`, last instruction ends at `0x002fd2f8`; source SHA-256 and symbol boundary match the values above. File-range SHA-256: `511e93b1da8f5aa6df7d4046f529756849426e34a248905a658240ae93f776b6`.

## Complete instruction table

| VA | File bytes | Instruction |
|---|---|---|
| 002fd0f0 | 0d c0 a0 e1 | mov ip, sp |
| 002fd0f4 | f0 db 2d e9 | push {r4, r5, r6, r7, r8, r9, fp, ip, lr, pc} |
| 002fd0f8 | 68 78 00 e3 | movw r7, #0x868 |
| 002fd0fc | 51 70 40 e3 | movt r7, #0x51 |
| 002fd100 | 04 b0 4c e2 | sub fp, ip, #4 |
| 002fd104 | 08 d0 4d e2 | sub sp, sp, #8 |
| 002fd108 | 00 50 a0 e1 | mov r5, r0 |
| 002fd10c | 00 00 97 e5 | ldr r0, [r7] |
| 002fd110 | 01 80 a0 e1 | mov r8, r1 |
| 002fd114 | 22 08 fa eb | bl 0x0017f1a4 |
| 002fd118 | 00 90 97 e5 | ldr r9, [r7] |
| 002fd11c | 00 40 a0 e3 | mov r4, #0 |
| 002fd120 | 1c 60 99 e5 | ldr r6, [r9, #28] |
| 002fd124 | 00 00 54 e3 | cmp r4, #0 |
| 002fd128 | 16 00 00 0a | beq 0x002fd188 |
| 002fd12c | 00 40 94 e5 | ldr r4, [r4] |
| 002fd130 | 00 30 54 e2 | subs r3, r4, #0 |
| 002fd134 | 01 30 a0 13 | movne r3, #1 |
| 002fd138 | 00 00 53 e3 | cmp r3, #0 |
| 002fd13c | 15 00 00 0a | beq 0x002fd198 |
| 002fd140 | bc 33 d4 e1 | ldrh r3, [r4, #60] |
| 002fd144 | 02 00 53 e3 | cmp r3, #2 |
| 002fd148 | f5 ff ff 1a | bne 0x002fd124 |
| 002fd14c | 04 10 95 e5 | ldr r1, [r5, #4] |
| 002fd150 | 14 00 94 e5 | ldr r0, [r4, #20] |
| 002fd154 | 2f fc f5 eb | bl 0x0007c218 |
| 002fd158 | 00 00 50 e3 | cmp r0, #0 |
| 002fd15c | f0 ff ff 1a | bne 0x002fd124 |
| 002fd160 | 09 00 a0 e1 | mov r0, r9 |
| 002fd164 | e7 07 fa eb | bl 0x0017f108 |
| 002fd168 | 00 00 58 e3 | cmp r8, #0 |
| 002fd16c | 12 30 a0 13 | movne r3, #18 |
| 002fd170 | 00 40 e0 13 | mvnne r4, #0 |
| 002fd174 | 00 30 88 15 | strne r3, [r8] |
| 002fd178 | 5a 00 00 0a | beq 0x002fd2e8 |
| 002fd17c | 04 00 a0 e1 | mov r0, r4 |
| 002fd180 | 24 d0 4b e2 | sub sp, fp, #36 |
| 002fd184 | f0 ab 9d e8 | ldmia sp, {r4, r5, r6, r7, r8, r9, fp, sp, pc} |
| 002fd188 | 00 30 56 e2 | subs r3, r6, #0 |
| 002fd18c | 06 40 a0 e1 | mov r4, r6 |
| 002fd190 | 01 30 a0 13 | movne r3, #1 |
| 002fd194 | e7 ff ff ea | b 0x002fd138 |
| 002fd198 | 09 00 a0 e1 | mov r0, r9 |
| 002fd19c | d9 07 fa eb | bl 0x0017f108 |
| 002fd1a0 | 00 00 97 e5 | ldr r0, [r7] |
| 002fd1a4 | 28 10 4b e2 | sub r1, fp, #40 |
| 002fd1a8 | 48 08 fa eb | bl 0x0017f2d0 |
| 002fd1ac | 00 40 50 e2 | subs r4, r0, #0 |
| 002fd1b0 | 02 00 00 0a | beq 0x002fd1c0 |
| 002fd1b4 | 28 30 1b e5 | ldr r3, [fp, #-40] |
| 002fd1b8 | 00 00 53 e3 | cmp r3, #0 |
| 002fd1bc | 17 00 00 0a | beq 0x002fd220 |
| 002fd1c0 | 00 00 97 e5 | ldr r0, [r7] |
| 002fd1c4 | 01 20 a0 e3 | mov r2, #1 |
| 002fd1c8 | f4 11 04 e3 | movw r1, #0x41f4 |
| 002fd1cc | 3a 10 40 e3 | movt r1, #0x3a |
| 002fd1d0 | 0c 0d fa eb | bl 0x00180608 |
| 002fd1d4 | 00 00 50 e3 | cmp r0, #0 |
| 002fd1d8 | 28 00 0b e5 | str r0, [fp, #-40] |
| 002fd1dc | 07 00 00 0a | beq 0x002fd200 |
| 002fd1e0 | 00 00 58 e3 | cmp r8, #0 |
| 002fd1e4 | 3f 00 00 0a | beq 0x002fd2e8 |
| 002fd1e8 | 00 40 e0 e3 | mvn r4, #0 |
| 002fd1ec | 11 30 a0 e3 | mov r3, #17 |
| 002fd1f0 | 04 00 a0 e1 | mov r0, r4 |
| 002fd1f4 | 00 30 88 e5 | str r3, [r8] |
| 002fd1f8 | 24 d0 4b e2 | sub sp, fp, #36 |
| 002fd1fc | f0 ab 9d e8 | ldmia sp, {r4, r5, r6, r7, r8, r9, fp, sp, pc} |
| 002fd200 | 00 00 97 e5 | ldr r0, [r7] |
| 002fd204 | 28 10 4b e2 | sub r1, fp, #40 |
| 002fd208 | 30 08 fa eb | bl 0x0017f2d0 |
| 002fd20c | 00 40 50 e2 | subs r4, r0, #0 |
| 002fd210 | f2 ff ff 0a | beq 0x002fd1e0 |
| 002fd214 | 28 30 1b e5 | ldr r3, [fp, #-40] |
| 002fd218 | 00 00 53 e3 | cmp r3, #0 |
| 002fd21c | ef ff ff 1a | bne 0x002fd1e0 |
| 002fd220 | 05 e0 a0 e1 | mov lr, r5 |
| 002fd224 | 04 c0 a0 e1 | mov ip, r4 |
| 002fd228 | 0f 00 be e8 | ldmia lr!, {r0, r1, r2, r3} |
| 002fd22c | 0f 00 ac e8 | stmia ip!, {r0, r1, r2, r3} |
| 002fd230 | 0f 00 be e8 | ldmia lr!, {r0, r1, r2, r3} |
| 002fd234 | 0f 00 ac e8 | stmia ip!, {r0, r1, r2, r3} |
| 002fd238 | 0f 00 be e8 | ldmia lr!, {r0, r1, r2, r3} |
| 002fd23c | 0f 00 ac e8 | stmia ip!, {r0, r1, r2, r3} |
| 002fd240 | be 32 d4 e1 | ldrh r3, [r4, #46] |
| 002fd244 | 00 20 9e e5 | ldr r2, [lr] |
| 002fd248 | 02 0c 13 e3 | tst r3, #512 |
| 002fd24c | 01 3c 83 03 | orreq r3, r3, #256 |
| 002fd250 | 00 20 8c e5 | str r2, [ip] |
| 002fd254 | be 32 c4 01 | strheq r3, [r4, #46] |
| 002fd258 | 30 60 d5 e5 | ldrb r6, [r5, #48] |
| 002fd25c | 00 00 56 e3 | cmp r6, #0 |
| 002fd260 | 0e 00 00 1a | bne 0x002fd2a0 |
| 002fd264 | 04 00 95 e5 | ldr r0, [r5, #4] |
| 002fd268 | dc fa f5 eb | bl 0x0007bde0 |
| 002fd26c | 06 20 a0 e1 | mov r2, r6 |
| 002fd270 | 04 60 84 e5 | str r6, [r4, #4] |
| 002fd274 | 01 70 80 e2 | add r7, r0, #1 |
| 002fd278 | f4 01 04 e3 | movw r0, #0x41f4 |
| 002fd27c | 3a 00 40 e3 | movt r0, #0x3a |
| 002fd280 | 07 10 a0 e1 | mov r1, r7 |
| 002fd284 | 4b fd f5 eb | bl 0x0007c7b8 |
| 002fd288 | 00 00 50 e3 | cmp r0, #0 |
| 002fd28c | 04 00 84 e5 | str r0, [r4, #4] |
| 002fd290 | 10 00 00 0a | beq 0x002fd2d8 |
| 002fd294 | 04 20 95 e5 | ldr r2, [r5, #4] |
| 002fd298 | 07 10 a0 e1 | mov r1, r7 |
| 002fd29c | 2f 1d 00 eb | bl 0x00304760 |
| 002fd2a0 | 04 00 a0 e1 | mov r0, r4 |
| 002fd2a4 | d0 0a fa eb | bl 0x0017fdec |
| 002fd2a8 | 08 35 0c e3 | movw r3, #0xc508 |
| 002fd2ac | 5f 30 40 e3 | movt r3, #0x5f |
| 002fd2b0 | 00 00 58 e3 | cmp r8, #0 |
| 002fd2b4 | 38 20 93 e5 | ldr r2, [r3, #56] |
| 002fd2b8 | 01 20 82 e2 | add r2, r2, #1 |
| 002fd2bc | 38 20 83 e5 | str r2, [r3, #56] |
| 002fd2c0 | ad ff ff 0a | beq 0x002fd17c |
| 002fd2c4 | 00 30 a0 e3 | mov r3, #0 |
| 002fd2c8 | 04 00 a0 e1 | mov r0, r4 |
| 002fd2cc | 00 30 88 e5 | str r3, [r8] |
| 002fd2d0 | 24 d0 4b e2 | sub sp, fp, #36 |
| 002fd2d4 | f0 ab 9d e8 | ldmia sp, {r4, r5, r6, r7, r8, r9, fp, sp, pc} |
| 002fd2d8 | 04 00 a0 e1 | mov r0, r4 |
| 002fd2dc | 21 08 fa eb | bl 0x0017f368 |
| 002fd2e0 | 00 00 58 e3 | cmp r8, #0 |
| 002fd2e4 | bf ff ff 1a | bne 0x002fd1e8 |
| 002fd2e8 | 00 40 e0 e3 | mvn r4, #0 |
| 002fd2ec | 04 00 a0 e1 | mov r0, r4 |
| 002fd2f0 | 24 d0 4b e2 | sub sp, fp, #36 |
| 002fd2f4 | f0 ab 9d e8 | ldmia sp, {r4, r5, r6, r7, r8, r9, fp, sp, pc} |

## Input-relative accesses and all explicit memory operations

Register tracking: entry `r0` is copied to callee-saved `r5` at `0x002fd108`; entry `r1` is copied to callee-saved `r8` at `0x002fd110`. Calls may clobber `r0-r3`, `r12`/`ip`, and `lr`; `r5` and `r8` survive because the routine saves/restores them. `lr` and `ip` become cursors only after the last relevant call before the copy sequence.

Input `r0` / `r5` reads (no stores through this base):

| VA | Access and byte range relative to entry `r0` | Detail |
|---|---|---|
| 002fd14c | read 4 bytes at `+0x04..+0x07` | `ldr r1,[r5,#4]`; passed as the second argument to the call at `0x002fd154`. |
| 002fd228 | read 16 bytes at `+0x00..+0x0f` | `lr=r5`; `ldmia lr!` loads four words, then advances `lr` to `r5+0x10`. |
| 002fd230 | read 16 bytes at `+0x10..+0x1f` | Second `ldmia lr!`; then `lr=r5+0x20`. |
| 002fd238 | read 16 bytes at `+0x20..+0x2f` | Third `ldmia lr!`; then `lr=r5+0x30`. |
| 002fd244 | read 4 bytes at `+0x30..+0x33` | `ldr r2,[lr]`, with `lr=r5+0x30`. |
| 002fd258 | read 1 byte at `+0x30` | `ldrb r6,[r5,#48]`; this is a second access to that starting offset with byte width. |
| 002fd264 | read 4 bytes at `+0x04..+0x07` | `ldr r0,[r5,#4]`; pointer passed to the call at `0x002fd268`. |
| 002fd294 | read 4 bytes at `+0x04..+0x07` | `ldr r2,[r5,#4]`; value passed as third argument to the call at `0x002fd29c`. |

Input `r1` / `r8` accesses (status stores only; no loads):

| VA | Access | Control condition / stored value |
|---|---|---|
| 002fd174 | write 4 bytes at `[r8+0]` | Conditional `strne`; writes `18` when the preceding `cmp r8,#0` found nonzero. |
| 002fd1f4 | write 4 bytes at `[r8+0]` | Writes `17` on the nonzero-`r8` error path. |
| 002fd2cc | write 4 bytes at `[r8+0]` | Writes `0` on the nonzero-`r8` completion path. |

Other explicit loads/stores, listed so bases and offsets are accounted for without assigning field meanings:

| VA | Instruction | Base / offset or effective range |
|---|---|---|
| 002fd0f4 | `push {r4,r5,r6,r7,r8,r9,fp,ip,lr,pc}` | Writes 10 words through `sp` with decrement-before semantics (40 bytes). |
| 002fd10c | `ldr r0,[r7]` | `r7+0`, word read. |
| 002fd118 | `ldr r9,[r7]` | `r7+0`, word read. |
| 002fd120 | `ldr r6,[r9,#28]` | `r9+0x1c`, word read. |
| 002fd12c | `ldr r4,[r4]` | prior `r4+0`, word read; traversal base is data-derived, not entry `r0` as such. |
| 002fd140 | `ldrh r3,[r4,#60]` | `r4+0x3c`, halfword read. |
| 002fd150 | `ldr r0,[r4,#20]` | `r4+0x14`, word read. |
| 002fd184 / 1fc / 2d4 / 2f4 | `ldmia sp,{r4,r5,r6,r7,r8,r9,fp,sp,pc}` | Reads 9 words starting at `sp+0`; restores saved registers and transfers control through loaded `pc`. |
| 002fd1a0 | `ldr r0,[r7]` | `r7+0`, word read. |
| 002fd1b4 | `ldr r3,[fp,#-40]` | `fp-0x28`, word read. |
| 002fd1c0 | `ldr r0,[r7]` | `r7+0`, word read. |
| 002fd1d8 | `str r0,[fp,#-40]` | `fp-0x28`, word write. |
| 002fd200 | `ldr r0,[r7]` | `r7+0`, word read. |
| 002fd214 | `ldr r3,[fp,#-40]` | `fp-0x28`, word read. |
| 002fd228 / 230 / 238 | `ldmia lr!,{r0,r1,r2,r3}` | Each reads 4 words at `lr+0..+0xc`; successive initial `lr` values are `r5`, `r5+0x10`, `r5+0x20`. Included in the input-relative table above. |
| 002fd22c / 234 / 23c | `stmia ip!,{r0,r1,r2,r3}` | Each writes 4 words at `ip+0..+0xc`; successive initial `ip` values are `r4`, `r4+0x10`, `r4+0x20`. |
| 002fd240 | `ldrh r3,[r4,#46]` | `r4+0x2e`, halfword read. |
| 002fd244 | `ldr r2,[lr]` | `lr+0`; in this path `lr=r5+0x30`, see input-relative table. |
| 002fd250 | `str r2,[ip]` | `ip+0`; at this point `ip=r4+0x30`, word write. |
| 002fd254 | `strheq r3,[r4,#46]` | Conditional halfword write at `r4+0x2e`. |
| 002fd258 | `ldrb r6,[r5,#48]` | `r5+0x30`, byte read; included above. |
| 002fd264 | `ldr r0,[r5,#4]` | `r5+0x04`, word read; included above. |
| 002fd270 | `str r6,[r4,#4]` | `r4+4`, word write. |
| 002fd28c | `str r0,[r4,#4]` | `r4+4`, word write. |
| 002fd294 | `ldr r2,[r5,#4]` | `r5+4`, word read; included above. |
| 002fd2b4 | `ldr r2,[r3,#56]` | `r3+0x38`, word read. |
| 002fd2bc | `str r2,[r3,#56]` | `r3+0x38`, word write. |
| 002fd174 / 1f4 / 2cc | `str{ne} r3,[r8]` / `str r3,[r8]` | `r8+0`, word writes; included in input-`r1` table. |

`mov`, arithmetic, tests, comparisons, and branches have no explicit memory operand. Calls below can of course perform memory effects inside their bodies, which were excluded and are not claimed here. No function body after `0x002fd2f8` or before `0x002fd0f0` was inspected.

## Calls, call-clobber-aware values, and local return paths

No indirect call instruction occurs in the bounded body. The `bl` targets and call-site argument registers are:

| Call VA | Direct target / symbol label from local disassembly | Visible `r0,r1,r2,r3` at call | Return use in this body |
|---|---|---|---|
| 002fd114 | `0x0017f1a4` (`MemPoolLock` label) | `r0=[r7]`; `r1=entry r1`; `r2=entry r2`; `r3=entry r3`. | Ignored; subsequent useful state is read/reloaded after the call. |
| 002fd154 | `0x0007c218` (`strcmp@plt` label) | `r0=[r4+0x14]`; `r1=[r5+4]`; `r2` is residual caller-saved state; `r3=2` on this fallthrough path (the preceding halfword comparison branches back unless it equals 2). | `r0` compared with zero at `0x002fd158`; nonzero loops to `0x002fd124`, zero proceeds to `0x002fd160`. |
| 002fd164 | `0x0017f108` (`MemPoolUnlock` label) | `r0=r9`; `r1-r3` are residual caller-saved state after the preceding call. | Ignored. |
| 002fd19c | `0x0017f108` (`MemPoolUnlock` label) | `r0=r9`; `r1/r2` are residual caller-saved state; `r3=0` on the paths entering `0x002fd198`. | Ignored. |
| 002fd1a8 | `0x0017f2d0` (`MemPoolGetBlock` label) | `r0=[r7]`; `r1=fp-40`; `r2/r3` are residual caller-saved state after the preceding call. | `r0` copied/tested as `r4` at `0x002fd1ac`; null branches to `0x002fd1c0`; non-null checks local word `[fp-40]` at `0x002fd1b4`. |
| 002fd1d0 | `0x00180608` (`MemPoolExtendDynamic` label) | `r0=[r7]`; `r1=0x003a41f4`; `r2=1`; `r3` is path-dependent residual state (on the non-null block path it is the loaded `[fp-40]` value; on the null-return path it is not set after the preceding call). | `r0` compared with zero and stored to `[fp-40]` at `0x002fd1d4/1d8`; zero branches to `0x002fd200`, nonzero proceeds to optional status-17 failure. |
| 002fd208 | `0x0017f2d0` (`MemPoolGetBlock` label) | `r0=[r7]`; `r1=fp-40`; `r2/r3` are residual caller-saved state after the preceding call. | `r0` copied/tested as `r4`; null branches to `0x002fd1e0`; non-null checks `[fp-40]` and either branches there or continues at `0x002fd220`. |
| 002fd268 | `0x0007bde0` (`strlen@plt` label) | `r0=[r5+4]`; `r1` is the word loaded from input offset `+0x24` by the third `ldmia`; `r2` is the word loaded from `+0x30`; `r3` is the loaded halfword at `[r4+0x2e]`, conditionally ORed with `0x100` when the `tst` result is zero. `r2` is overwritten after the call. | `r0` used at `0x002fd274` to form `r7=r0+1`. |
| 002fd284 | `0x0007c7b8` (`SysMemAllocData@plt` label) | `r0=0x003a41f4`; `r1=r7` (prior length plus one); `r2=r6`; `r3` is residual caller-saved state after `strlen`. | `r0` tested and stored at `[r4+4]` at `0x002fd288/28c`; null branches to `0x002fd2d8`. |
| 002fd29c | `0x00304760` (`CMUtlSafeStrCpy` label) | `r0` is the allocation return preserved since `0x002fd284`; `r1=r7`; `r2=[r5+4]`; `r3` is residual caller-saved state after allocation. | Ignored. |
| 002fd2a4 | `0x0017fdec` (`MemPoolAppendUsedBlock` label) | `r0=r4`; if the byte test at `0x002fd25c` was nonzero, `r1-r3` retain the source/copy values from the preceding instructions; on the zero-byte branch they are residual caller-saved state after the call at `0x002fd29c`. | Ignored. |
| 002fd2dc | `0x0017f368` (`MemPoolPutBlock` label) | `r0=r4`; `r1-r3` are residual caller-saved state after the allocation call. | Ignored; then `r8` selects status-17 return or status-untouched return. |

Register note: EABI caller-saved registers are not treated as stable across `bl`. The table gives the values established immediately at each call site, and labels a call-clobbered residue as unknown/path-dependent rather than attributing a callee effect. No callee body or API meaning was used.

Local CFG and local output/result paths (addresses are within this function only):

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Return/status summary, strictly local: on the completion path, `r4` is the block value returned by the call at `0x002fd1a8` or `0x002fd208`; 52 bytes from entry `r0` (held in `r5`) are then copied into that block, and the block value is returned in `r0`. The block pointer itself is not computed from entry `r0` in this body. Error returns set `r0=-1` (`mvn r4,#0; mov r0,r4`, or earlier `r4=-1` on the path where the values compared through the call at `0x002fd154` compare equal). Status output is written only when `r8` (entry `r1`) is nonzero: value 18 on that equal-comparison path, value 17 on the shown allocation/block failure branches, and value 0 after the append call. On error paths with null `r8`, `r0=-1` returns without a status store. The block-put path selects the same status-17 versus status-untouched behavior. These are immediate values and control paths; no semantic interpretation of those values is asserted.

## Assessment

Status: VERIFIZIERT for the bounded decode, direct access offsets, call sites, visible call-site register values, and local CFG as observed in the identified shipped ELF using the stated disassembler and independent ELF metadata. OFFEN for the behavior of callees and any memory effects they cause, values of residual caller-saved registers, and the meaning of offsets/status values. Tests: PASS — artifact identity/size, Dynsym size, next GLOBAL FUNC boundary, 130 bounded instruction rows, and range-byte digest were checked. No runtime test was performed (`NOT_RUN` for dynamic behavior). Self-review: analyst self-review only; no independent review is claimed.

Alternative/fallback: exact retained REA record was absent; host GNU objdump lacked the target architecture; the GNU ARM objdump fallback succeeded on the exact source range. Rizin was available but unnecessary. Residual uncertainty is confined to absent retained REA corroboration and out-of-scope callee/runtime behavior; no conclusion depends on symbol/API names beyond using them as labels for direct branch targets.

Output files: `report.md`, `validate.sh`, and `SHA256SUMS`. Hashes are recorded in `SHA256SUMS`.
