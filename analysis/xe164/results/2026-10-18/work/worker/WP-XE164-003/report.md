> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-003 — Startup initialization records

## Scope and result

Offline static analysis of control/data flow in analysis addresses `0xE0387A..0xE03A95` and the two directly referenced table bases `0x0033A8` and `0x000B84`, limited to record stepping, tags, fields, and byte copy/zero mechanics. No device, network, VM, firmware execution, SFR naming, or peripheral interpretation was used. E00F18 is mentioned only as the visible unknown-tag call anchor.

**VERIFIZIERT (statische Mechanik):** the startup code compares word tags 1, 5, 6, and 7; it advances past tag-1 records by 12 bytes after consuming the tag (14-byte total stride), handles tag 5/6 as single-range byte copy or zero operations depending on which table loop is active, and tag 7 as a two-count range operation. The primary bytes contain one 14-byte tag-1 record followed by tag 0; that tag takes the default branch to the secondary table base `0x000B84`. The secondary table contains twelve 6-byte tag-5 records followed by tag 0. The secondary reader has no tag-0 case and routes it to the visible E00F18 call path. This bounds the observed streams, but leaves why the secondary stream ends in that path and its runtime outcome **OFFEN**.

No PASS is assigned to runtime behavior. The result is a static-mechanism verification only.

## Rebound inputs

| Input | Size | SHA-256 | Recheck |
|---|---:|---|---|
| `XE164-composite-e00000.bin` | 17,110 bytes | `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` | exact |
| `composite-replay.md` | 2,169 bytes | `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5` | exact |
| `Xe164Probe.java` | 4,315 bytes | `9289f41396180a3478ce3e64e70f54d38a397e5f4f7247b89bd8e8bf2808490f` | exact |

## Tooling and address coordinates

- REA Rizin provider; toolchain binding records Rizin `0.9.1`, commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. The successful commands set `asm.arch=c166`, `asm.bits=16`, disabled color where applicable, then sought by **file offset** (`0x387a`, `0x3978`, `0xb84`). The artifact digest was unchanged in every observation.
- Ghidra direct-import fallback/replay binding: Ghidra `12.1.4`, language `C166:LE:16:default`, compiler spec `tasking`, BinaryLoader base `0xE00000`; the bound script hash is above. Existing manifest-bound PASS logs report 1,401 instructions, 45 functions and successful startup decompilation. This is supporting analysis evidence, not an independent verification.
- Exact documented fallback command, from `composite-replay.md` (with the documented network-isolated temporary project path and retained private log arguments omitted here only as optional additions): `unshare -Un --map-current-user PRIVATE_LOCAL_PATH "$xe164_replay_dir" xe164-replay -import PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin -loader BinaryLoader -loader-baseAddr 0xe00000 -processor C166:LE:16:default -cspec tasking -scriptPath PRIVATE_ANALYSIS_ROOT/work/ghidra/scripts -postScript Xe164Probe.java -analysisTimeoutPerFile 45 -max-cpu 1 -readOnly -deleteProject`.
- With the replay loader base, candidate linear analysis address is `0xE00000 + file offset`. Thus startup `0xE0387A..0xE03A95` corresponds to offsets `0x387A..0x3A95`; next function starts at `0xE03A96`. Rizin raw seek addresses in captured evidence are offsets, not rebased analysis addresses.
- The code stores words at locations `0xFE00..0xFE06` at offsets `0x38B8..0x38C4` and again at `0x38F8..0x3900`; the Ghidra output names some of these DPP0/1/2. No register semantics are inferred. A conventional C166 DPP paging interpretation with page value `0x0380` would map logical `0x33A8` to the composite image near `0xE033A8` and `0x0B84` near `0xE00B84`. This is explicitly an **assumption**, not verified XE164 runtime mapping. Alternative segment/page interpretation or different runtime contents would change which physical bytes those logical pointers read. File offsets listed in `init-records.tsv` are direct observations; `analysis_addr_assumed` is conditional on the composite linear mapping.

## Mechanical decoding

### Control flow and fields

- `0xE03904..0xE03908` loads logical table pointer `0x33A8` and sets the DPP-like word at `0xFE00` to `0x0380`; `0xE0390E` reads a word tag through the post-incrementing pointer. `0xE03910..0xE0391E` dispatches tags 1, 5, 6, 7; unrecognized tags branch to `0xE039CE`.
- Tag 1: `0xE039C8` adds `0x000C` to the already advanced pointer, then `0xE039CC` returns to the tag read. The observed total record stride is 14 bytes: two-byte tag plus twelve skipped bytes. The six payload words are opaque to this path.
- Primary tag 5: `0xE039B4..0xE039C6` reads destination, source, and count as three words; copies one byte per iteration while incrementing source and destination; total record size 8 bytes including tag.
- Primary tag 6: `0xE03982..0xE039B2` reads destination offset/page, source offset/page, and count; copies bytes while incrementing both logical pointers. The two page values are loaded into DPP-like state and the low 14-bit offsets are combined with `0x4000`/`0x8000` window selectors in the pseudocode. The reader advances 12 bytes total. Exact segment-address interpretation is unresolved.
- Primary tag 7: `0xE03920..0xE03980` reads destination offset/page, source offset/page and two word counts. It copies bytes until both counts reach zero, with explicit handling when the offset reaches `0x7FFF`/`0xBFFF`; total record size is 14 bytes including tag. Those wrap points are observed mechanically; their physical address semantics are not asserted.
- Primary tag 0 at the observed end of the tag-1 record: the dispatcher has no explicit tag-0 comparison, so it takes the default branch at `0xE0391E` to `0xE039CE`, which switches the table pointer to `0x0B84`; control reaches the secondary table reader at `0xE039D8`. This default behavior also applies to other tags not matched by 1/5/6/7; their semantics are not generalized here.
- Secondary tag 5: `0xE03A44..0xE03A56` reads destination and count and stores zero byte-by-byte; total record size 6 bytes.
- Secondary tag 6: `0xE03A22..0xE03A42` reads destination offset/page and count and stores zero byte-by-byte; total record size 8 bytes.
- Secondary tag 7: `0xE039E6..0xE03A20` reads destination offset/page and two counts, then stores zero until both counts are exhausted; total record size 12 bytes.
- Secondary tag 0 at `0x0BCC`: no tag-0 branch is present in the secondary reader. Its unmatched-tag path reaches the visible `0xE00F18` call at `0xE03A8C`, then the idle loop at `0xE03A90..0xE03A94`. The call is only an anchor; its callee is not inspected and no callee semantics are inferred.

The opcode/field lists describe only address-bound mechanics. No meaning is assigned to the `0xFExx`/`0xFFxx` locations or bit operations.

### Directly referenced bytes and record balance

At file offset `0x33A8`, bytes decode as a 14-byte tag-1 record:

`01 00 | 07 00 | 00 3D | 03 00 | C2 31 | 80 03 | 01 00`

The next word at offset `0x33B6` is `00 00`. It is an observed tag-0 value. The dispatcher does not compare against 0 explicitly, but its default branch switches to the secondary table at `0x0B84`; the selected table thus has one complete tag-1 skip record followed by a table-switch marker. The remaining bytes are not claimed as primary records.

At file offset `0x0B84`, twelve consecutive tag-5 records occupy offsets `0x0B84..0x0BCB` (12 × 6 bytes). Each has destination and count fields, listed in the TSV. The next word at `0x0BCC` is `00 00`, also not a recognized tag in this dispatcher. This is 12 completely bounded observed records plus one unresolved tag word.

| Table | Recognized complete records | Unresolved next tag | Bytes in recognized records | Byte-operation classification |
|---|---:|---|---:|---|
| Primary `0x33A8` | 1 (tag 1) plus tag-0 table switch | none in observed stream | 14 + 2-byte selector | opaque 12-byte payload skipped; selector switches to secondary table |
| Secondary `0x0B84` | 12 (tag 5) | `0x0BCC = 0` | 72 | 12 destination/count zero-fill operations by the secondary reader |

## Evidence and uncertainty

Observed: REA disassembly at startup and branch tails; raw bytes at the referenced table offsets; direct Ghidra replay pseudocode and exact input hashes. The pseudocode confirms the mechanics summarized above, but its types are analysis-tool types and not recovered source layouts. Evidence IDs are recorded here, and each observation is preserved in `rea-evidence.json` (five records; all five are this worker's Rizin operations, including one failed syntax attempt):

- `ev_0c4347764721762b3ef37486d03bcac1ae9d758bf017321fefc1971a32b68654` — Rizin disassembly from file offset `0x387A` (broader view, clipped in tool presentation only).
- `ev_d0fb07927300ef611ad298be486cd008505de3da5c237b39605fda5a5365003c` — focused Rizin disassembly from `0x387A`.
- `ev_a887c0abf35c0d44fd509cb8c39bd8ca1733276971445ef76bc418504f5a670c` — focused branch-tail disassembly from `0x3978`.
- `ev_978007baa6305aa3fd32892e42d315c6212019795424b74e9b49565c1cd93062` — bytes at `0x0B84`.
- `ev_9d9dbd76f1da2e2517c1225a30b86d5aa2be3d281e24db401f08a8951335ff15` — initial malformed Rizin command; it did not alter the artifact and is retained as a failed probe.

Derived: type-to-operation classification follows dispatch and byte-loop instructions; record boundaries follow explicit pointer increments and observed post-increment reads. It does not establish that the processor reaches every record or that these bytes are the runtime backing store.

Open questions: (1) why the secondary table's tag-0 value reaches the unmatched-tag path; (2) whether the DPP/segment mapping is exactly the conventional composite-linear mapping assumed above; (3) whether the composite contains the actual startup-time table contents at those logical pointers; (4) the status of bytes following the observed secondary tag. These prevent a claim that startup completes normally or that any copy/zero occurs at runtime. The direct Ghidra run is a reproducible static cross-check, not an independent reviewer.

## Generated outputs

- `report.md` — this report.
- `init-records.tsv` — observed records and unresolved tags, with coordinates separated.
- `ranges.tsv` — instruction/table ranges and static mechanical classifications.
- `rea-evidence.json` — exported REA bundle, 129,357 bytes, five worker-owned records, zero unknowns; SHA-256 is in `SHA256SUMS`.
- `SHA256SUMS` — SHA-256 inventory of all output files except itself.
