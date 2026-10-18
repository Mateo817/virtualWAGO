> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-262 — selector 17/15 common result lane

## Identity and scope

**VERIFIZIERT** — Source is `libIoDrvDal.so.1.0.2`, 25,976 bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. REA Ghidra 12.1.4 opened this exact hash with analysis profile `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. The provider image mapping used here is Ghidra VA = ELF VA + `0x10000`, as independently recorded for this DSO in bounded package WP-XE164-229.

**VERIFIZIERT** — The six scoped instruction windows partition the assigned code ranges as ELF `[0x362c,0x3680)`, `[0x3680,0x3684)`, `[0x4194,0x419c)`, `[0x3710,0x3738)`, `[0x4304,0x433c)`, and `[0x42f4,0x4304)`. The only data read is four bytes at ELF `0x4344`. `root-rea.json` retains exact per-instruction REA responses and the literal read; `scoped-instructions.tsv` binds every instruction word to the exact source ELF bytes. No neighboring instruction, callee body, or global storage bytes are included.

## Selector paths

**VERIFIZIERT** — At dispatcher ELF `0x3634`, `r3 = r0 - 2`; `0x3640` compares `r3` with 13 and the unsigned conditional PC-add at `0x3644` selects a table cell only for `r3 <= 13`. For input selector 17, `r3=15`, so control branches to `0x4194`, which sets `r4=0` and branches to common code at `0x3710`.

**VERIFIZIERT** — For input selector 15, `r3=13`, so the dispatch selects cell ELF `0x3680`; that instruction branches to `0x42f4`. The scoped sequence at `0x42f4..0x4300` is `BL 0x09d4; LDR r3,[r0,#4]; BLX r3; B 0x4194`. The body and effects of the `BLX` target are outside this package. The later branch reaches the same `0x4194`, which sets `r4=0` before entering `0x3710`. The earlier indirect call may affect memory later read by common code, so the two paths share local code and an `r4` value, not a proven identical memory state. No getter, interface, slot, or lifecycle semantics are assigned.

## Common return and conditional callbacks

**VERIFIZIERT** — The four bytes at ELF `0x4344` are `a82c0100`, little-endian value `0x12ca8`. At Ghidra provider VA `0x13714`, `ADD r5,pc,r5` uses A32 PC `0x1371c`, yielding provider VA `0x263c4`, corresponding to ELF VA `0x163c4` under the recorded `+0x10000` mapping. This is local address arithmetic; the contents or runtime identity of the addressed global storage are not read here.

**VERIFIZIERT** — Common code loads `[r5,#0xc]` into `r6`. If it is nonzero, the zero-conditional initialization and branch are skipped; execution reaches `MOV r0,r4` and return. Since both selector paths set `r4=0` immediately before common code, this local lane returns `r0=0` when `[base+0xc] != 0`.

**VERIFIZIERT** — If `[base+0xc] == 0`, common code sets `r7=base`, `r8=0x63c`, keeps `r6=0`, then branches to the loop precheck. The precheck loads `[r7,#0x10]` and takes `BHI` to the callback body only while that unsigned word is greater than the current index. Thus a zero `[base+0x10]` skips the loop body and returns the still-zero `r4` through `r0` without a `BLX`.

**VERIFIZIERT** — For a positive count, the local loop may execute repeated iterations. Each iteration loads a candidate from `[r5,#0x638]`; zero skips that iteration's indirect call, while nonzero reaches `BLX r3`. The loop then increments `r6` and advances `r5` by `0x63c` before rechecking the count. The loop reloads the count on each check, so opaque call effects may change whether later iterations execute. After a call, the body compares current `r4` with zero and copies current `r0` into `r4` only if that comparison is equal. The indirect callee's register and memory effects are unknown, so no ABI-based preservation or unconditional result claim is made for this lane.

**VERIFIZIERT** — The bounded local conditions proving a zero return on these two incoming paths are: (a) `[base+0xc] != 0`; or (b) `[base+0xc] == 0` and `[base+0x10] == 0`. A zero return is also compatible with positive-count loop states, but the result then depends on the loaded callback pointers and indirect callee effects; that outcome is **OFFEN** here.

## Observation and limits

**VERIFIZIERT** — `global-path.tsv` records the selector mapping, branch sequence, gate predicates, callback-loop mechanics, and the stated unknowns. The reported “base” is only the address expression locally formed by the instructions. Memory contents, aliasing, callback targets, call effects, API meaning, ABI, lifecycle meaning, runtime state, VM, hardware, and network behavior remain **OFFEN** or outside scope. No binary was executed.

**PASS** — `validate.py` is read-only by default and verifies source identity, REA target/profile/evidence identity, exact scoped instruction coverage, byte-for-byte source binding, the literal read, derived address arithmetic, generated TSV/report contents, and the self-reference-free manifest. `--write` is explicit regeneration mode.
