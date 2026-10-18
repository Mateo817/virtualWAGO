> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-182 — Direct A32-BL callers of ELF VA `0x277c`

## Finding

**OFFEN (caller ownership); VERIFIZIERT (raw call sites).** A complete raw scan of all file-backed executable ELF sections finds exactly two little-endian A32 direct `BL` encodings whose PC-relative destination is ELF VA `0x277c` (Ghidra `0x1277c`): file/ELF VA `0x30cc` and `0x3de0`. Their Ghidra-form addresses under the documented `+0x10000` image base are `0x130cc` and `0x13de0`.

The two call sites are exact direct callers at the instruction level. Their local containing-function names and definitive FunctionManager owner ranges remain **OFFEN**: neither supplied bundle contains an incoming-xref/caller query for `0x277c` or a procedure dossier covering either caller, and the REA session was closed. Per assignment, the known hanging Ghidra import was not repeated. The ELF dynamic symbol table does not label either call-site owner.

| ELF VA / file offset | Raw A32 word | Destination | Bounded `r0`–`r3` provenance at call | Immediate return use |
|---|---|---|---|---|
| `0x30cc` | `0xebfffdaa` | `0x277c` | `r0 <- r6` at `0x30c8`; `r1 <- r7` at `0x30c4`; `r2 = 2` at `0x30c0`; `r3 = 0x8008` at `0x30b0`. The sources behind `r6`/`r7` are outside the bounded window and unknown. | `0x30d0`: stores `r0` to `[sp,#8]`. |
| `0x3de0` | `0xebfffa65` | `0x277c` | `r0 <- r7` at `0x3ddc`; `r1 <- r5` at `0x3dd8`; `r2 = 1` at `0x3dd4`; `r3` is the zero-extended halfword loaded from `[r5]` at `0x3dbc`. The call path follows the equality branch at `0x3dc4` against `r8`; the value provenance of `r8` is outside this window. | `0x3de4`: compares returned `r0` with zero; `0x3de8`: branches to `0x3dcc` on zero. |

No semantic meaning is assigned to either object register, constants, or record bytes. No callee effects or runtime reachability are claimed. Full instruction windows and source-word checks are in `window-30cc.txt` and `window-3de0.txt`; machine-readable facts are in `caller-scan.json` and `.tsv`.

## Scan and address bases

Target identity verified: `libIoDrvKbus.so.0.0.1`, 38,584 bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`.

The ELF is ELF32, little-endian, ARM, EABI5. `readelf -SW` identifies four file-backed `SHF_EXECINSTR` sections, all fully scanned as aligned 32-bit words:

| Section | File offset = ELF VA | Size |
|---|---:|---:|
| `.init` | `0x1cc0` | `0x0c` |
| `.plt` | `0x1ccc` | `0x1e8` |
| `.text` | `0x1eb8` | `0x6174` |
| `.fini` | `0x802c` | `0x08` |

For each word, the raw scan selected A32 branch-class encodings with link bit set and condition field other than `0xf`; it decoded `site + 8 + sign_extend(imm24 << 2)`. Exactly two decoded to `0x277c`. `objdump` independently prints both as `bl 0x277c` at the same addresses. The scan excludes indirect calls, Thumb, runtime execution, and non-executable sections.

Ghidra's existing WP096 records bind the target function body to Ghidra `0x1277c` and the ELF artifact hash above. WP096 supplies no caller query for the two sites. WP113 is same-artifact context, but its records concern `IoDrvKbus_Init` and do not establish these caller owners. REA-first review therefore reused the exact supplied REA evidence; no fresh focused Ghidra incoming-xref query was available without repeating the known import hang. This gap is recorded once.

## Bounded windows and limits

`window-30cc.txt` covers `[0x309c,0x30fc)`, exactly 96 bytes around `0x30cc`. `window-3de0.txt` covers `[0x3db0,0x3dec)`, 60 bytes: 48 bytes preceding the call and 12 bytes following it. The second range stops at the adjacent code/data transition candidate `0x3dec`; that is an objdump-derived clipping point, not independently confirmed Ghidra function ownership. Accordingly the exact function boundary and both containing procedure names remain **OFFEN**. The validator checks each manifest range exactly, verifies every listed word against the ELF, and confirms each call's raw branch arithmetic; it cannot promote a disassembly-derived boundary to FunctionManager evidence.

**Alternative explanation:** An A32 BL-shaped word in executable-section bytes could be embedded data rather than executed code. Here each candidate is aligned in `.text`; GNU ARM `objdump` decodes it as a direct `bl`, its destination arithmetic agrees, and the bounded surrounding instructions exhibit register setup and immediate result handling. That supports classifying both as static direct-call sites, but does not prove either executes.

## Scope deviation, uncertainty, and status

During exploration, one initial `objdump` command requested wider ranges (`0x305c..0x313c` and `0x3d70..0x3e30`) than the authorized caller windows. Those outputs were overbroad. No out-of-window register provenance or caller conclusion is included in this report or manifest; the final extracts and validator are restricted to the declared windows. This is recorded as a method scope deviation, so the overall work-package status remains **OFFEN** even though the raw scan and in-window byte checks pass.

Remaining uncertainty:

- Local function names/entries and exact owner boundaries for `0x30cc` and `0x3de0` are not established by the supplied REA evidence or dynamic symbol table.
- The `0x3de0` window's end is a code/data boundary candidate only.
- Static bytes do not establish runtime reachability, object semantics, or target function effects.

## Tools, tests, and evidence status

- **VERIFIZIERT:** ELF identity; complete executable-section inventory; exhaustive aligned raw direct-A32-BL scan; two matching call encodings and PC-relative destinations.
- **VERIFIZIERT:** Bounded in-window `r0`–`r3` definitions and immediate result use, as encoded in disassembly and source bytes.
- **OFFEN:** Exact caller function ownership, names, and provider-confirmed boundaries.
- REA: `rea-agents 6.5.0`; supplied reports identify Ghidra `12.1.4`. Existing WP096/WP113 profile digest: `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. No fresh REA query was run because the target session was closed and a known hanging Ghidra import must not be repeated.
- Countercheck: GNU `arm-linux-gnueabihf-objdump` 2.44 and GNU `readelf` 2.44; raw scan and validator use Python 3.13.5 standard library.

| Check | Status | Result |
|---|---|---|
| Input identity | PASS | All five supplied inputs match their expected byte sizes and SHA-256 values. |
| Executable section coverage and raw BL arithmetic | PASS | All four executable sections scanned; exactly two matches at `0x30cc` and `0x3de0`. |
| Window source bytes and exact manifest bounds | PASS | Every listed 32-bit word and file range validated against the ELF. |
| REA incoming-xref query | NOT_RUN | No retained caller query; avoids repeating known hanging import. |
| Runtime/VM/network/device/hardware | NOT_RUN | Outside scope. |
| Caller function ownership/boundary confirmation | BLOCKED | Existing REA evidence does not cover the caller procedures; fresh import prohibited by task constraint. |
| Strict window-only tool-output discipline | FAIL | One exploratory objdump invocation exceeded the authorized windows; deviation is disclosed above, and out-of-window bytes are excluded from the findings. |

Generated files and SHA-256 values are listed in `SHA256SUMS`.
