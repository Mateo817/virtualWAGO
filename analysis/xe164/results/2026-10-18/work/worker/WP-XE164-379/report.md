> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-379 — independent review of WP-XE164-370

**Review result: PASS with one wording qualification.** I independently checked the retained WP370 manifest, the four complete artifacts, all 1,004 selected instruction words, the noncontiguous code ranges, all eleven static loader rows, their nine relative path fixups, and the byte candidate computed from L3. `python3 validate.py` passes 2,104 read-only checks. This review does not modify WP370.

The four binary pairs are byte-for-byte equal: libpackbus is 148,792 bytes and L1/L2/L3 are 32/266/16,598 bytes. All hashes match the copied WP370 identity table. This establishes identity for these exact files only, not general firmware or ABI equality.

The exact instruction set is 1,004 words: reader 588 bytes at ELF 0x97f0, boot entry 1,048 bytes at 0xa470, and orchestrator 2,380 bytes across [0x9a78,0x9e78) and [0x9f24,0xa470). The interval [0x9e78,0x9f24) is a 172-byte gap and is not counted as code. I parsed the retained REA address lists independently and checked each word against libpackbus raw bytes.

The original table bytes cover ELF [0x335c4,0x337a8) and file [0x235c4,0x237a8): eleven 44-byte records. Each listed field and full row hex matches direct parsing. The relative relocations occur at path-word cells for rows 0,1,2,3,5,6,7,8,9; adding the ELF image base 0x10000 to these nine raw pointer words exactly reproduces the 484-byte REA preview. The other two record path words are zero. Path strings at the raw addends match the three retained file names. These are static ELF data pointers, not runtime addresses.

Source instructions support the reported numeric field positions: the reader loads record size at +8 and path at +4; orchestrator instructions read selector word +0x0c, prefix/control byte +0x14 (decimal 20), acknowledgement byte +0x15 (decimal 21), response word +0x18 (decimal 24), response/count word +0x1c (decimal 28), and XOR/control byte +0x20 (decimal 32). The inspected instructions include selector compare/branch at 0x9bd0–0x9bd8, prefix and acknowledgement reads at 0x9bdc/0x9be8, response handling at 0x9c08/0x9c10 and 0x9e2c–0x9e50, XOR-control branch at 0x9f24, REV at 0x9bf8, and EOR at 0x9ffc. These instructions establish accesses and operations, not an entire transfer outcome.

All eleven initial selector words are zero. Rows 4 and 10 each have leading word 1 and a null path; that evidence does not assign either row terminator semantics. Row 8 and row 9 both carry the L3 path addend and sentinel size. Row 8 has zero Ack/XOR cells. Row 9 has Ack byte 1, expected response word 0x81, count word 1, and XOR-control byte 1. The XOR control is also read by the source branch at 0x9f24. Thus “row 9 XOR” is supported as a static flag/source-path distinction; the stronger sentence in WP370 that raw data belongs exclusively to row 8 and row 9 does not send it again is not established by table contents alone. The repeated L3 path and sentinel in row 9 remain visible, and this bounded audit does not trace a reachable transfer to settle that question. Treat exclusivity/no-resend as HYPOTHESE or remove it.

For the exact L3 file, size 16,598 gives candidate prefix bytes `00 00 40 d6`; XOR of all L3 bytes is `83`. The candidate sequence length and SHA-256 independently match `configured-byte-candidates.json`. This is arithmetic over static bytes and a source-observed REV/EOR route; it is not a capture, configured boot proof, actual transfer, or C166 placement result.

| Claim | Status | Review basis |
|---|---|---|
| Four exact FW31/worker004 file identities | VERIFIZIERT | Full size, SHA-256 and byte equality |
| 1,004 instruction words and excluded 172-byte gap | VERIFIZIERT | Independent REA range parsing and source-byte comparison |
| Eleven table records, 44-byte stride and nine R_RELATIVE path fixups | VERIFIZIERT | Direct raw bytes, relocation file and REA fixed-up preview |
| Numeric selector/Ack/prefix/XOR/response cells and cited accesses | VERIFIZIERT | Raw row positions plus bounded source instructions |
| Candidate prefix `000040d6` and XOR byte `83` | VERIFIZIERT | Computed from exact L3 size and bytes; candidate only |
| Selected rows form an active boot sequence | HYPOTHESE | Configuration/runtime selection and reachability not established |
| Row 9 cannot resend/read L3 data already referenced by row 8 | OFFEN | Static row 9 itself has the same L3 path and sentinel size |
| Actual transfer, full payload response, runtime reachability, C166 address placement | OFFEN | Not shown by source bytes or this audit |
| Rows 4 or 10 are terminators | OFFEN | No evidence or semantics assigned |

Validation command: `python3 validate.py` — PASS (2,104 independent checks). No target or native execution, runtime/VM/device/network access, or REA import was used. Physical and runtime tests are NOT_RUN.
