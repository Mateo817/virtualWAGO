> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-247 — direct caller and selector-window inventory

Status: **OFFEN** for runtime invocation and complete caller-side semantics. The bounded direct-site census and visible local definitions are **VERIFIZIERT** for the stated source and scopes.

## Source and census

Target `codesys3` SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`, size 5,181,396 bytes. GNU disassembler: `GNU objdump (GNU Binutils for Debian) 2.44`. `executable-sections.tsv` records all file-backed ELF sections with `SHF_EXECINSTR`. The census scans only aligned 4-byte words in those sections and decodes A32 B/BL encodings (`cond != 0xf`, bits 27:25 = `101`), computing targets with `PC = site + 8` and sign-extended imm24. Every match is bound by site VA, source file offset, raw word, target and containing section in `direct-caller-inventory.tsv`.

The raw scan found 23 direct sites to `CMCallHook` at `0x2fecc4` and 2 to `CMCallHook2` at `0x300308` (25 BL, 0 B). REA xrefs returned 23 locations for CMCallHook and 2 for CMCallHook2. The raw scan overlaps 22/23 and 2/2 sites respectively. The CMCallHook xref list has unmatched address(es) `0x2fc5a0` and omits raw site(s) `0x1757f4`; unmatched addresses remain untyped and their instructions were not inspected. Ghidra `procedure_callers` returns caller procedure entries, not branch sites; its CMCallHook coverage is partial and omits one call reference, so it is a distinct corroborating method, not the source of the direct-site count. Exact REA records and their limitations are retained in `rea-evidence.json`.

## Local windows and selector position

For every direct site S, `caller-windows.objdump.txt` contains only the mechanically assigned `[max(section_start,S-96), min(section_end,S+20))` window. `visible-inputs.tsv` traces r0-r3 through local conditional branches, overwrites and opaque calls. `CMCallHook` selector position is r0, sourced only from accepted WP246 report/positional evidence; `CMCallHook2` selector position is r1, established by the exact body `[0x300308,0x300440)`.

REA procedure metadata confirms CMCallHook2's exact contiguous 312-byte extent. Its raw instruction, local CFG and forwarding matrix are in the three `cmcallhook2-*` TSVs. At `0x30038c`, the body sets helper-call r1 from the saved incoming r1; it therefore forwards CMCallHook2 entry-r1 to the accepted helper's selector position. The other visible helper-call inputs are separately recorded and are not assigned semantic names.

Caller-window selector classifications: CMCallHook: 18 OTHER_CONSTANTS_IN_FIXED_LOCAL_WINDOW, 5 UNKNOWN_NOT_EXCLUDING_15; CMCallHook2: 2 OTHER_CONSTANTS_IN_FIXED_LOCAL_WINDOW. `PROVEN_15_IN_FIXED_LOCAL_WINDOW` means only that every value in the bounded local abstract state is constant 15; it does not prove the whole function's incoming edges or runtime invocation. `UNKNOWN_NOT_EXCLUDING_15` and mixed/computed states do not imply “not 15”. Calls invalidate r0-r12, sp, lr and memory is not modeled; no preservation crosses an opaque call. Direct branches leaving a fixed window, unresolved indirect PC transfers, unsupported writes and REA-only xrefs are listed in `gaps.tsv`.

## Limits

The complete census claim is limited to aligned A32 direct B/BL words in file-backed `SHF_EXECINSTR` sections. It does not census Thumb, BLX-immediate, indirect calls/tail transfers, dynamic references or code outside those sections. Caller interpretation is limited to the fixed windows plus CMCallHook2's exact 312-byte body; no earlier caller code or CMCallHook body is newly analyzed. The accepted WP246 helper finding is consumed by its hash-bound report/positional matrix only. No ABI, runtime identity, registered-object identity or actual call with selector 15 is inferred. No execution, device, VM or network action was performed.

## Validation

`python3 validate.py` checks hashes, reruns the scoped ELF census and bounded GNU disassembly, compares every generated artifact byte-for-byte, and verifies the self-reference-free manifest without writing. `python3 validate.py --write` is the explicit generator.
