> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-184 — r6/r7 reaching definitions at `0x30cc`

**Befundstatus: VERIFIZIERT** for visible definitions, uses, and gates inside `[0x2f80,0x30fc)`. **OFFEN** for the actual defining instructions and provenance of the incoming `r6` and `r7` values.

## Ergebnis

At ELF VA/file offset `0x30cc`, the call-site setup is `0x30c4: mov r1,r7`, `0x30c8: mov r0,r6`, `0x30cc: bl 0x277c`. There is no instruction writing either `r6` or `r7` before the call in the inspected interval. The epilogue instruction `0x30f0: pop {r4,r5,r6,r7,r8,r9,sl,fp,pc}` restores them after the call and cannot reach its operands. Therefore the only visible reaching values at the call are the values already held on entry to this interval: incoming `r6` is copied to `r0`, and incoming `r7` is copied to `r1`. The instructions that defined either incoming value are **OFFEN** because their provenance is outside the permitted pre-call slice or otherwise not established here. No semantic identity is assigned to either register.

Memory-source/use observations are limited to the interval: `0x3074: ldr r3,[r6,#0x61c]` reads memory through the value in `r6` but does not define `r6`; `0x2f9c: mov r0,r7` and `0x3048: mov r0,r7` read `r7`; no instruction before the call loads into `r6` or `r7`. The post-call `pop` at `0x30f0` restores both from the stack. The exact per-claim rows `F1`, `F2`, and `F3` are in `flow.tsv`.

## Path gates visible in the interval

On the fall-through path shown by the bounded disassembly, control reaches `0x30cc` only after the visible earlier branch conditions permit continued execution. In the immediate block, `0x30a8: bne 0x30f4` requires equality at `0x30a4`; `0x309c: bne 0x30f4` requires the OR result from `0x3098` to be zero; and `0x30bc: bne 0x30d0` skips the call unless the halfword comparison at `0x30b4` succeeded. Earlier fall-through gates include `0x3034` (`r3==0`), `0x303c` (`r4==3`), and `0x3070` (the stack value tested at `0x3068` is zero). These are instruction-level conditions only; they do not identify records, profiles, or API meanings. Because caller ownership and incoming control-flow edges are outside this bounded question, this is not a proof of global reachability or execution.

## Evidence and method

REA-first evidence review reused accepted E-XE164-210 and WP096 context. E-XE164-210 binds the exact artifact and identifies `0x30cc` as the direct A32 callsite. WP096's accepted REA report/bundle does not contain a caller range for this site or its caller-register provenance; this missing caller-range evidence is documented once here. No fresh Ghidra import/query was made.

Fallback: `arm-linux-gnueabihf-objdump`, GNU Binutils `objdump` **2.44**, command bounds `--start-address=0x2f80 --stop-address=0x30fc`; the only interpreted instructions are fully contained in `[0x2f80,0x30fc)`. Address levels are ELF VA/file offset (equal for this examined interval); Ghidra's `+0x10000` address level is not used. The validator recomputes the complete input size and sequential whole-file SHA-256 for identity, then separately reads and checks instruction words only from the bounded interval. It also verifies the interval limits and `flow.tsv` claim rows. The full-file pass is identity verification only; no out-of-range instructions are decoded or interpreted.

Input identity: exact FW31-IoDrvKbus ELF, size `38584`, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` (accepted E-XE164-210).

Alternative explanation: a control-flow edge from outside the bounded interval could enter a later block, or incoming register values could have been established by any earlier caller setup. Neither possibility changes the local fact that no in-range instruction defines `r6` or `r7`, but it limits any claim about which paths execute and what the values represent.

## Status

- Static bounded observations: **VERIFIZIERT**.
- `r6`/`r7` source instructions, semantic identity, caller ownership, global reachability, and execution: **OFFEN**.
- Runtime/VM/network/device/hardware checks: **NOT_RUN**.
- Scope compliance: **PASS**; no instruction outside `[0x2f80,0x30fc)` was interpreted. The sole REA-first evidence gap is documented above.
- Review: worker Self-Review; no independent review claimed.
- Validator: **PASS** after creation.

## Output files and SHA-256

`SHA256SUMS` lists the hashes of `assignment.md`, `report.md`, `flow.tsv`, and `validate.py`. Its own SHA-256 is reported in the completion handoff because a manifest cannot include its own final digest.
