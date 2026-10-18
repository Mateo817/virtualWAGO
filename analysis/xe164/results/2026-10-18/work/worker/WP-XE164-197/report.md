> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-197 — локальный поток `r10` к аргументу при `0x2fe4`

## Результат

**HYPOTHESE.** При входе в блок создания объекта инструкция `0x327c` начинает новую локальную цепочку: `r3 := r4 + 0x10c`, `r10 := r3 + 0x400`, затем `r10 := r10 + 6` в `0x3284`. Поэтому значение, скопированное в `r2` в `0x328c`, арифметически равно текущему `r4 + 0x512`. По локальному CFG переход `0x32ec -> 0x2f08` ведёт позже к `0x2fe4`, где `r10` копируется в `r1`, второй регистр аргументов следующего вызова `0x2fec`.

Между `0x3284` и `0x2fe4` есть вызовы, включая непосредственно следующий `blx ip` в `0x3298`, затем вызовы на пути через `0x32ec -> 0x2f08` и к `0x2fe4`. Тело не задаёт и не доказывает их влияние на `r10`. Следовательно, **OFFEN**, равно ли значение `r10` в `0x2fe4` локально вычисленному `r4 + 0x512`. Локальные инструкции подтверждают факт `r1 := r10` при `0x2fe4` и арифметику `r10` перед `0x328c`; они не подтверждают сохранение этого значения между точками.

## Идентичность и метод

- Вход: `sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`, 25 976 bytes.
- SHA-256: `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` — **PASS**.
- REA: `rea-agents` / REA server 6.5.0; Ghidra 12.1.4; provider `ghidra`; architecture `ARM:LE:32:v8`; analysis profile `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Same-hash search in the active REA evidence ledger returned zero retained records before analysis. Reused the existing WP-XE164-196 same-hash assembly/dossier identity as corroborating prior evidence, then obtained focused REA assembly in this session: `ev_c384b3fa751d09bd0489acbfeb8f53366a78dafcf7607dfd1592644396435ca6` (`procedure_assembly`, procedure `0x12ddc`).
- Ghidra image base is `0x10000`. Thus Ghidra address = ELF VA + `0x10000`; e.g. ELF `0x2fe4` is Ghidra `0x12fe4`, and the bounded ELF range `[0x2ddc,0x331c)` corresponds to Ghidra `[0x12ddc,0x1331c)`.
- Exact opcode words were cross-checked with `arm-linux-gnueabihf-objdump`, GNU Binutils 2.44, disassembling only `[0x2ddc,0x331c)`. No target execution occurred.

## Vollständige `r10`-Vorkommen im begrenzten Körper

`r10` is printed as `sl` by GNU objdump at these locations. The following list includes register reads, writes, read-modify-writes and the prologue/epilogue save/restore. Opcode words are the exact 32-bit words from the input file.

| ELF VA | Ghidra VA | Opcode | Instruction | Local role |
|---:|---:|---:|---|---|
| `0x2ddc` | `0x12ddc` | `e92d4ff0` | `push {r4,r5,r6,r7,r8,r9,sl,fp,lr}` | Reads incoming `r10` and saves it with the register block. |
| `0x2f04` | `0x12f04` | `e8bd8ff0` | `pop {r4,r5,r6,r7,r8,r9,sl,fp,pc}` | Restores `r10` from the saved block on return. |
| `0x2fe4` | `0x12fe4` | `e1a0100a` | `mov r1,sl` | Reads current `r10`; writes its value to `r1`. |
| `0x318c` | `0x1318c` | `e597a0a0` | `ldr sl,[r7,#0xa0]` | Defines `r10` from a memory load. |
| `0x31a8` | `0x131a8` | `e12fff3a` | `blx sl` | Reads `r10` as an indirect branch/call target. |
| `0x31dc` | `0x131dc` | `e1a0a000` | `mov sl,r0` | Defines `r10` from `r0`. |
| `0x3218` | `0x13218` | `e18aa000` | `orr sl,sl,r0` | Reads and writes `r10` (read-modify-write). |
| `0x3250` | `0x13250` | `e18aa000` | `orr sl,sl,r0` | Reads and writes `r10` (read-modify-write). |
| `0x326c` | `0x1326c` | `e18a3000` | `orr r3,sl,r0` | Reads `r10` as an input; writes `r3`. |
| `0x327c` | `0x1327c` | `e283ab01` | `add sl,r3,#0x400` | Defines `r10` from `r3` and immediate `0x400`. |
| `0x3284` | `0x13284` | `e28aa006` | `add sl,sl,#6` | Reads and redefines `r10`; completes the local offset calculation. |
| `0x328c` | `0x1328c` | `e1a0200a` | `mov r2,sl` | Reads `r10`; copies it into `r2` for the call at `0x3298`. |

There are no other disassembled instructions in `[0x2ddc,0x331c)` whose operand text names `r10`/`sl`; the validator checks this exact occurrence set and each listed opcode word.

## Локальная арифметика и связанный call path

Observed instructions:

1. `0x3274: e2843f43  add r3,r4,#0x10c` gives local `r3 = r4 + 0x10c`.
2. `0x327c: e283ab01  add sl,r3,#0x400` gives local `r10 = r3 + 0x400`.
3. `0x3284: e28aa006  add sl,sl,#6` gives local `r10 = r3 + 0x400 + 6 = r4 + 0x10c + 0x400 + 6 = r4 + 0x512`.
4. `0x328c: e1a0200a  mov r2,sl` copies that then-current value to `r2`; `0x3298: e12fff3c  blx ip` is the immediately following call after setup. No callee effect is inferred.
5. `0x32ec: 0affff05  beq 0x2f08` is the observed edge returning from this setup region to the library path. On the resulting path, `0x2fe4: e1a0100a  mov r1,sl` copies the then-current `r10` into `r1`; `0x2fec: ebfff66c  bl 0x9a4` is the following direct call. The imported PLT label observed by objdump is `LibraryLoader_LoadSymbol@plt`.

The `r10` value reaching `0x2fe4` has no later *local instruction* definition after `0x3284` on this path. That alone does not show it survives calls. The bounded path contains these calls after the `0x3284` definition and before the `0x2fe4` use:

| ELF VA | Opcode | Instruction / observed target | Path note |
|---:|---:|---|---|
| `0x3298` | `e12fff3c` | `blx ip` | Immediately follows `mov r2,sl` at `0x328c`. |
| `0x32c0` | `e12fff3c` | `blx ip` | In the same setup region. |
| `0x32e4` | `e12fff37` | `blx r7` | Followed by branch `0x32ec -> 0x2f08` when the condition holds. |
| `0x2f08` | `ebfff6b1` | `bl 0x9d4` (`adi_GetApplicationInterface@plt`) | At the branch destination. |
| `0x2f1c` | `e12fff33` | `blx r3` | Indirect call in that path. |
| `0x2f38` | `ebfff6b1` | `bl 0xa04` (`strcmp@plt`) | Conditional loop body; may execute zero or more times. |
| `0x2f4c` | `ebfff6a0` | `bl 0x9d4` (`adi_GetApplicationInterface@plt`) | Conditional loop body. |
| `0x2f58` | `e12fff33` | `blx r3` | Conditional loop body. |
| `0x2f9c` | `ebfff68f` | `bl 0x9e0` (`LibraryLoader_GetLibraryList@plt`) | Before the list lookup. |
| `0x2fb8` | `ebfff68b` | `bl 0x9ec` (`g_slist_find_custom@plt`) | Before the successful continuation to `0x2fe4`. |
| `0x2fd4` | `ebfff687` | `bl 0x9f8` (`LibraryLoader_LibraryOpen@plt`) | Before the successful continuation to `0x2fe4`. |

These are observed call instructions/targets only. The body does not prove whether any callee changes or preserves `r10`; no calling-convention contract or callee effect is assumed. Conditional call `0x2ffc` occurs after the `r1` setup and is on the nonzero-return branch, which jumps away from `0x2fe4`; it is not an intervening call for the use in question.

## Beobachtung, Schlussfolgerung, Alternative, Restunsicherheit

- **VERIFIZIERT — Beobachtung:** `0x2fe4` executes `mov r1,sl` (`e1a0100a`). `0x3274/0x327c/0x3284` locally compute `r10 = r4 + 0x512`, and `0x328c` locally copies the then-current `r10` to `r2`. The branch `0x32ec -> 0x2f08` and the later instruction order through `0x2fe4` are address-bound in the body.
- **HYPOTHESE — Schlussfolgerung:** If intervening calls leave `r10` unchanged, the second register argument at `0x2fe4` carries `r4 + 0x512` from `0x3284`.
- **Alternative explanation:** One or more intervening callees may change `r10`; then `0x2fe4` still copies the current register value into `r1`, but that value need not equal the local arithmetic result at `0x3284` (or the value passed in `r2` at `0x328c`). This is a possible explanation, not a claim that a particular callee does so.
- **OFFEN — Restunsicherheit:** Callee bodies/effects and a proven register-preservation contract for the listed calls are outside this work package. Static body evidence does not establish runtime register contents. The equality asked about therefore remains **OFFEN**.

## Reproduzierbare Validierung

Run `python3 validate.py` from this worker directory. The validator checks the input digest, bounded disassembly extent, all in-range `r10`/`sl` occurrences, opcode words for those occurrences plus the address arithmetic and consumers, and the arithmetic `0x10c + 0x400 + 6 = 0x512`. Expected test status: **PASS**.

## Erzeugte Dateien

See `SHA256SUMS` for file digests. All generated files are within `work/worker/WP-XE164-197/`.
