> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-001 — XE164 composite entry window

Correction revision: the initial report aligned L3 at the same numeric file offsets as the composite. Self-review established that the composite's `0x200` region corresponds to L3 source offset `0x000`; this revision replaces that irrelevant comparison with the aligned comparison and updates the CSV and hashes.

## Result

**PASS — 128/128 entries accounted for**, for the explicitly bounded byte window only. Each entry is four bytes; every row was decoded by REA's Rizin C166 disassembler as `jmps` and has a target. The analysis does not establish what the entries mean in the full image or on a device.

The requested window is Composite file offsets `0x200..0x3FF` (inclusive), treated under the supplied mapping hypothesis as analysis addresses `0xE00200..0xE003FF`. `entries.csv` contains one row per entry, indexed `0..127`.

## Inputs and integrity

| Input | Size | SHA-256 |
|---|---:|---|
| `XE164-composite-e00000.bin` | 17,110 bytes | `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` |
| `XE164L3.bin` | 16,598 bytes | `26fe2560d12ed794a572186d4f66217a430838f6e1f345f5f6f2f2f0df734abf` |

Both sizes and hashes were re-read and matched the supplied identities. Composite raw bytes were read only at `0x200..0x3FF`; the aligned L3 source bytes were read only at `0x000..0x1FF`. The mapping used for this comparison is `L3 source offset = Composite file offset - 0x200`, as indicated by the composite's `+0x200` placement of L3.

## Method and evidence

REA was used first. Its `execute_rizin_command` operation analyzed the hash-identified composite with:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

REA Evidence ID: `ev_5ae947acd0beef66eb2b281582c2d827f9e764705d7359d13fc21105f3711cb4`. REA reports the command completed, output was not truncated, no artifact change occurred, and the observed pre/post SHA-256 was the supplied composite digest. The Rizin provider did not return a version (`version: null`); the executable version probe `rizin -v` reported **Rizin 0.9.1**, commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`.

Import/address assumptions: Rizin opened the headerless composite as a generic raw file, where its displayed instruction locations are file offsets (`0x200` through `0x3FC`). The C166 decode used `asm.bits=16`; the listing's decoded targets carry the `E0` segment. The `analysis_address` column is calculated as `0xE00000 + file_offset`, exactly the requested composite-base mapping assumption. Neither this decode nor the table proves that the composite is actually mapped at that base. The earlier documented raw-Ghidra C166 failure was not repeated.

The 4-byte raw entries and aligned L3 source bytes were independently recorded from only the bounded slices. The CSV target field follows the Rizin decode; the raw C166 form observed in every composite row is `FA E0` followed by a little-endian 16-bit target offset, consistent with that listing. The C166 decode and seven non-self targets were rechecked in this correction run using REA Evidence `ev_5ae947acd0beef66eb2b281582c2d827f9e764705d7359d13fc21105f3711cb4`, without expanding the byte scope. `rea-evidence-bundle.json` was exported from this worker session and contains that one own-session record; no foreign records are present.

## 128-row accounting and classifications

- Indices: `0..127`, exactly once each; CSV has 128 data rows plus one header.
- File offsets: `0x200, 0x204, …, 0x3FC`; analysis addresses: `0xE00200, 0xE00204, …, 0xE003FC`.
- Readable/decoded entries: 128; unknown or unreadable entries: 0.
- Self-target entries: 121.
- Non-self-target entries: 7 — indices `0, 36, 83, 84, 89, 90, 91`; details are in the CSV. Index 0 targets `0xE00400`; the others target `0xE00C1A`, `0xE021AA`, `0xE021E0`, `0xE01D5A`, `0xE01D90`, and `0xE01DC6`, respectively.
- Duplicate raw-entry groups: 0. Duplicate decoded-target groups: 0. Therefore no entry repeats another target in this 128-entry window.
- Aligned Composite versus L3: 128/128 four-byte rows and 512/512 bytes match exactly (`Composite 0x200..0x3FF` ↔ `L3 0x000..0x1FF`). `entries.csv` records the source offset, both byte sequences, and a row match flag for every entry.

## Observations, conclusions, and limits

**VERIFIZIERT (bounded observations):** the input identities, 128 four-byte composite rows, their observed Rizin C166 `jmps` decodes/targets, exact 128-row/512-byte equality against the aligned L3 source slice, and the stated duplicate counts. These are verified only for the named files, hashes, method, and offsets.

**HYPOTHESE:** the supplied composite-base mapping `file offset + 0xE00000` is used to label the requested analysis addresses. This mapping contract remains unproven.

**OFFEN:** the semantic role of this region and of each target, the correctness of the broader composite construction/mapping, and whether the off-pattern targets are deliberate. No SFR, protocol, interrupt, vector, or hardware meaning is assigned.

Alternative explanation: the seven non-self targets may be intentional entries in a generated or patched table; they may instead result from the assumed address base being incomplete or incorrect. The byte equality establishes the stated source-slice correspondence, but does not establish the composite's address mapping or target roles. No target execution or bytes outside the stated Composite/L3 slices were analyzed.

## Generated files and integrity

- `entries.csv` — 128-entry machine-readable table with aligned L3 source offsets/bytes/match flags; its SHA-256 is recorded in `SHA256SUMS`.
- `report.md` — this report; its SHA-256 is recorded in `SHA256SUMS`.
- `rea-evidence-bundle.json` — complete session Evidence bundle exported by REA; its SHA-256 is recorded in `SHA256SUMS`. The bundle includes records from this worker session only; it is not a record authored by another worker.
- `SHA256SUMS` — standard manifest containing hashes for all generated artifacts above (the manifest does not hash itself).
