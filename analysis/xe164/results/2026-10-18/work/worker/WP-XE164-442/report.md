> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-442 — independent audit of frozen WP441 DTB evidence

**VERIFIZIERT, bounded inventory and byte-string evidence.** WP441 remains byte-for-byte frozen at manifest hash `290b551d625f8744a6164e14ca49dea16841cf1def5c7d98fca2e0d128bbeb50`; its validator and manifest checks pass. I independently checked the retained image/inventory identities, the ten listed regular DTBs, every extracted size/hash and the bounded string summaries from the local extracted bytes. I did not redump or modify any source.

The pinned partition inventory and retained `debugfs ls -l /boot` output agree: regular DTBs occupy inodes 14 through 23, exactly ten files; inode 24 is `emmc0/`, mode `40755`, a directory. The ten retained files match their paths, inode rows, sizes and SHA-256 values in `extraction.json` and the partition inventory. The image and inventory hashes match WP441's recorded pins. This resolves the original count discrepancy in favor of ten DTBs; inode 24 is not an eleventh DTB.

Independent printable-run searches over all ten bytes find the exact strings `kbus@0`, `wago,spi-kbus`, and `kbus,tty-device` in each artifact. The exact printable run `ttyKbus` is absent from all ten. Each file also has one raw WAGO board-ID-like string and one model label, with two PFC100 variants and eight PFC200 variants as summarized in WP441. These observations are byte strings only. No parsed node, `compatible` property, property-to-node relation, enabled state, active firmware tree, TTY pathname, or runtime driver binding is established. The task and report correctly do not infer these from text occurrences.

The raw token-context file contains bounded case-insensitive occurrences for its five search patterns; it is consistent with recomputed offsets/contexts. Those raw hits include substring matches and do not constitute an FDT decode. The absence check is limited to the exact printable string; it does not exclude alternate encodings or runtime name creation.

| Claim | Status | Independent finding | Limit |
|---|---|---|---|
| FW31 image/inventory pins and WP441 freeze | VERIFIZIERT | Hashes match recorded pins and frozen manifest | Static provenance only |
| Candidate DTB count and inode 24 classification | VERIFIZIERT | Ten regular rows at inodes 14–23; `emmc0/` directory at 24 | Corrects initial eleven-file expectation |
| Ten extracted path/size/hash bindings | VERIFIZIERT | All retained bytes match corresponding inventory and extraction records | No new extraction was performed |
| Three candidate strings in all ten files; exact `ttyKbus` absence | VERIFIZIERT | Independently recomputed printable strings | No property/node association |
| Active DTB, node enablement, compatible binding, runtime TTY, driver/device behavior | OFFEN | Not established by raw strings | DTB parse and runtime evidence absent; NOT_RUN |

No upstream package changed. No DTB parser, target, device, VM, network, or native target code was used. The independent read-only validator recomputes the inventory joins and raw string observations from retained files and verifies source/package hashes; it is not a DTB parser.
