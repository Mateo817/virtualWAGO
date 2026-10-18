> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-144 — `ComponentEntry` stores into the incoming object

## Question and bound inputs

Which direct stores in the complete FW31 `libIoDrvDal.so.1.0.2` function body
write through its incoming `r0` pointer at byte offsets `+0x00..+0x38`, what
values do they write, and which local branch conditions affect them?

The ELF is 25,976 bytes, SHA-256
`853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.
REA/Ghidra identifies `ComponentEntry` at Ghidra address `0x14448`, exactly
covering `0x14448..0x14623` (inclusive; 476 bytes), corresponding to ELF file
offsets `0x4448..0x4623` in the requested mapping. Accepted positional context
is WP-XE164-143 `report.md`, SHA-256
`c1b113da9623dd9351e0055d63bd28f53b9601e4f90217c5b83458ae98d39cce`.

## Finding

**VERIFIZIERT (statische Instruktionssemantik):** the body has four direct
store instructions whose effective target is derived from the original input
pointer. All execute unconditionally before the only conditional branch:

| ELF file offset | Ghidra address | Instruction | Input-object bytes written | Width and written value |
|---:|---:|---|---|---|
| `0x4490` | `0x14490` | `str r3, [r0,#0x18]` | `+0x18..+0x1b` | 4 bytes; code-address value `0x0001362c` |
| `0x4498` | `0x14498` | `str r1, [r0,#0x0]` | `+0x00..+0x03` | 4 bytes; numeric `0x10062001` |
| `0x44d0` | `0x144d0` | `vst1.32 {d16,d17}, [r3]`, with `r3 = r0 + 4` from `0x144cc` | `+0x04..+0x13` | 16 bytes; four 32-bit values: `+0x04 = 0x00011704`, `+0x08 = 0x00010b58`, `+0x0c = 0x00011570`, `+0x10 = 0x000133b4` |
| `0x44e0` | `0x144e0` | `str r3, [r0,#0x14]` | `+0x14..+0x17` | 4 bytes; code-address value `0x0001157c` |

The `0x144d0` vector store is one 16-byte instruction; the four table rows it
covers are not four separate machine instructions. The adjacent values are
also shown as 64-bit pairs in Ghidra pseudocode: `0x10b5800011704` at
`+0x04/+0x08`, and `0x133b400011570` at `+0x0c/+0x10`, in little-endian word
order. The pseudocode also renders the last two stores as `&LAB_0001157c` and
`&LAB_0001362c`; numeric addresses above retain that exact Ghidra address
representation and do not claim a runtime relocation or a source-level type.

There are no other direct stores into incoming-object positions `+0x00..+0x38`
in the analyzed body. The other stores after the initial sequence use stack or
global/register-derived destinations. The body reads incoming values at
`+0x1c`, `+0x20`, `+0x24`, `+0x28`, `+0x2c`, `+0x30`, and `+0x34`; those loads
are not stores through the incoming pointer.

**VERIFIZIERT (local branch):** `0x14510` loads a word from input offset
`+0x28`; `cmp r2,#0` at `0x14518` and `beq 0x14530` at `0x14524` skip the
indirect call at `0x1452c` when that word is zero. When nonzero, the call is
made with `r0` set from `r1`. All four input-object stores above precede this
branch, so neither the null nor nonnull lane changes whether those stores run.
Both lanes converge at `0x14530`; `r0` is set to zero at `0x145d8`, then the
common epilogue returns at `0x14620`. The only observed return value is zero.

**VERIFIZIERT (bounded positional join):** WP-XE164-143 establishes that its
caller copies the then-current input-block positions `L+0x04` and `L+0x08`
back to caller positions `B+0x14` and `B+0x18` only on a zero entry result.
Thus this function's writes at `+0x04/+0x08` occupy the same positions as the
two values observed by that bounded copyback. This join establishes position
only; it does not assign field or callback names.

## Full direct-store / branch table

| Store address | Effective input base and offset | Width | Source value at store | Branch condition required | Result/status |
|---:|---|---:|---|---|---|
| `0x14498` (`file 0x4498`) | original `r0 + 0x00` | 32-bit | `r1 = 0x10062001` (loaded literal at `0x14460`) | none; unconditional | **VERIFIZIERT** |
| `0x144d0` (`file 0x44d0`) | `r3 + 0`, where `r3 = original r0 + 0x04` at `0x144cc` | 128-bit total; four 32-bit lanes | `d16/d17` read stack temporaries at `0x144c8`: words `0x00011704`, `0x00010b58`, `0x00011570`, `0x000133b4` | none; unconditional | **VERIFIZIERT** |
| `0x144e0` (`file 0x44e0`) | original `r0 + 0x14` | 32-bit | PC-relative code address `0x0001157c` | none; unconditional | **VERIFIZIERT** |
| `0x14490` (`file 0x4490`) | original `r0 + 0x18` | 32-bit | PC-relative code address `0x0001362c` | none; unconditional | **VERIFIZIERT** |

| Branch address | Test and target | Affected operation | Null/zero lane | Nonzero lane | Result/status |
|---:|---|---|---|---|---|
| `0x14518` compare; `0x14524` branch (`file 0x4518`, `0x4524`) | `r2 = *(original r0 + 0x28)`; `cmp r2,#0`; `beq 0x14530` | Indirect call at `0x1452c` only; no input-object store | Branch directly to `0x14530`; call skipped | `r0 = r1` at `0x14528`, then `blx r2` at `0x1452c` | **VERIFIZIERT** |

## Evidence and method

REA-first analysis opened the supplied ELF and ran `analyze_function` on
`0x14448`. Evidence ID:
`ev_83dd313f76e8abe38946a299a444f5b337faca6e5bf8ac8619cb65ba98f53ede`.
Provider: Ghidra 12.1.4; ARM; analysis profile digest
`7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
The dossier reports a complete inclusive body, assembly, pseudocode, CFG, and
non-truncated high-p-code value-flow (`truncated=false`, omitted-operation
lower bound 0). No callee bodies were analyzed. The complete available REA
session bundle is `rea-evidence-bundle.json` in this package.

The evidence is static analysis of a shipped artifact, not execution. No
objdump/readelf fallback was needed: REA returned the full body assembly and
resolved pseudocode constants for all stores. No other artifact, runtime,
device, VM, network, or hardware was accessed.

## Alternative explanation and residual uncertainty

**HYPOTHESE:** the four values at `+0x04..+0x10` and the code addresses at
`+0x14/+0x18` may be intended as later callable slots, consistent with the
accepted positional caller context. This report does not establish those
semantics, names, complete calling convention, or runtime use.

**OFFEN:** this static pass cannot establish whether the function executes,
whether its incoming memory is writable or aliased, how the code addresses are
relocated/mapped at runtime, or what the unresolved semantic purpose of each
position is. It also does not establish behavior inside the conditional
callee. The only branch-specific conclusion is that the call is skipped for
zero `+0x28` and attempted for nonzero `+0x28` after the unconditional stores.

## Validation and package files

The semantic validator `validate.py` rehashes both bound inputs, selects the
unique REA record by evidence ID, checks provider/body identity and exact
instruction/value/branch substrings, and compares the complete observed store
instruction set against the four input-directed store instructions. Its
recorded run is `validation.txt`.

- Validator: **PASS** if the recorded output is `PASS`; see `validation.txt`.
- Runtime tests: **NOT_RUN** (out of scope).
- This is a bounded static finding, not independent review.

Generated files:

| File | Purpose |
|---|---|
| `report.md` | Findings, full store and branch tables, boundaries, alternatives, and uncertainty |
| `validate.py` | Reproducible semantic checks against hashes and the retained REA bundle |
| `validation.txt` | Validator output |
| `rea-evidence-bundle.json` | Exported REA session evidence bundle |
| `SHA256SUMS` | SHA-256 manifest for all package files other than this manifest |
