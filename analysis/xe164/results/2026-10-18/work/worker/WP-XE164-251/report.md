> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-251 — bounded table and CMCallHook selector trace

Status: **VERIFIZIERT** for the exact source table, bounded caller scans and local register expressions; **OFFEN** whether table row 20 is passed through the opaque helper path into CMCallHook r0 or invoked at runtime.

## Source, scope and REA

Target `codesys3`, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`, 5,181,396 bytes; GNU objdump `GNU objdump (GNU Binutils for Debian) 2.44`; REA/Ghidra 12.1.4 profile `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Original scope is `assignment.md`; root's authorized extension is `scope-amendment.md` (SHA-256 `496815fe49696dc10951e58a728f6696ee38e2c490ae450c2213fa153dd9bb35`). Complete REA records are retained in `rea-evidence.json`.

The aligned A32 B/BL census is limited to file-backed executable ELF sections. It found 2 direct BLs to `FUN_002ff0a0`, 3 to `CMInitSequence`, and 4 to `CMExitSequence`. REA xrefs exactly match those site sets. REA caller procedure entries are listed separately because they are not call-site addresses. Every direct site is interpreted only in its fixed clipped `[S-96,S+20)` window; the only full code ranges are the originally assigned helper, CMInitSequence and CMExitSequence bodies.

## Static table found in the amended caller windows

The `CMInit3` caller window for `0x3020c0` constructs base `0x3a30c0`, loops with index `0..33` (`cmp r3,#34`), tests the first word against 2, and passes the matching row pointer with count 1. Its unique source row is index 2, whose first word is 2. The `CMExit` caller window for `0x300f3c` constructs the same base and loads an exact PC literal at `0x301390` whose value is end pointer `0x3a31d0`; that proves a 34-entry range. Its local scan selects the unique first-word-12 row at index 16. The raw loop replay starts with r0=r1=0: the match at index 16 sets r0 and increments r1 to 1; the non-14 row at index 17 increments r1 to 2; index 18's word 14 exits before increment. The `movcc r1,#1` minimum clamp leaves count 2, so the call passes row-16 pointer and count 2. `exit-loop-replay.tsv` records these three relevant iterations. The `CMExit` window for `0x30133c` constructs the same base and end `base+272`; its bounded loop includes the unique first-word-10 row at index 13, but r0 derives from unknown entry-r1 after an opaque call, so its selected pointer/count remain conditional. These static source-table facts do not rely on callees preserving registers or memory.

The proven data range `[0x3a30c0,0x3a31d0)` is file-backed `.rodata` and contains 34 stride-8 numeric rows. `table-word-inventory.tsv` records both raw words and byte offsets for every row. First word 15 occurs at index 20, VA `0x3a3160`; its paired second word is retained numerically without assigning a structure or pointer meaning. Thus a bounded static source table **does contain** 15. The fully selected static caller windows choose indices 2 and 16, with first words 2 and 12. Window `0x30133c` scans for 10 and includes its unique source row at index 13, but selection remains conditional on the unknown initial r0. The call at `0x300fd8` scans memory for 14 but its fixed window does not contain the write establishing r5 as static table base, so no base is borrowed from earlier code. Other CMInit callers likewise have no proven static table base in their windows; `0x300ec0` passes r0/r1 as zero.

## Table reads to CMCallHook r0

Inside `FUN_002ff0a0`, the word loaded into r0 at `0x2ff0f0` or `0x2ff148` reaches CMCallHook sites `0x2ff0f8` or `0x2ff188` without an intervening call. Accepted, hash-bound WP246 evidence identifies CMCallHook r0 as the selector position. The helper saves its incoming r0/r1 in frame slots, but the later frame reloads follow opaque BL `0x2ff140`; no memory preservation is assumed. The loaded pointer and count therefore cannot be equated to the original incoming arguments. The table expression is verified; its particular backing row is open.

For the static `CMInit3` path, `CMInitSequence` receives the row-2 pointer and count 1. The sequence overwrites incoming r2 at `0x2ff1f0` with a fresh load from `[0x5fc538]`; therefore the caller's r2 does not establish the branch outcome. A callfree path to helper call `0x2ff268` exists conditionally when bit 2 of that freshly loaded word is clear, causing the branch at `0x2ff204` to skip opaque call `0x2ff23c`. On that conditional lane r0/r1 are copied from the incoming arguments, but the subsequent `FUN_002ff0a0` access still follows opaque `0x304b64`, so WP251 does not claim that row-2 word 2 reaches CMCallHook r0. The row-20 value 15 is inventoried separately, but no permitted direct caller proves that row 20 backs either post-opaque helper load.

`CMExitSequence` forwards r0/r1 toward opaque `BL 0x2ff594` on a local lane; that callee is outside scope. No CMCallHook route from the exit-selected table rows is asserted. Literal values appear in `literal-words.tsv`; only the exact end pointer at `0x301390` is used to prove a table bound.

## Limits

No table words outside the exact proven 34-row range were read. The row-20 membership result establishes only static source data, not a runtime reference, invocation, or delivery to CMCallHook. No opaque register or memory preservation, ABI, runtime behavior, or object identity is inferred. Other caller windows with dynamic/unknown bases remain open; this bounded result is not a global negative. No out-of-scope bytes, device, VM, network or runtime action were used.

`python3 validate.py` is read-only and verifies pinned inputs, all 12 REA evidence identities, three raw direct-call target censuses, exact fixed windows, complete scoped instruction ranges, literal and file mapping, the proven table range and words, replay of the `0x300f3c` table loop from its explicit zero initialization, TSV widths, and self-reference-free manifest. `python3 validate.py --write` is the explicit generator.
