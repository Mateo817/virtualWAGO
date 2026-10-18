> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-335 — exact FW31 XE164 inputs

**VERIFIZIERT:** The hash-bound FW31 SD image's partition2 contains regular files `/etc/specific/XE164L1.bin`, `XE164L2.bin`, and `XE164L3.bin`, inodes782/783/784 and sizes32/266/16598bytes. A readonly debugfs stat/dump of those three exact inodes from one temporary bounded partition slice freshly extracted each file. Their complete bytes and SHA256 hashes equal the previously bound FW30 counterparts. The same whole-artifact equality for FW31 libpackbus is separately E321.

| Input | Bytes | SHA256 |
|---|---:|---|
| L1 |32|42549d93b538a898203f90488c8d98fc5715e7fd506c5d645de9a00793e20084|
| L2 |266|b4a7eddb47ca3d31040a5d567a847af3da75b5db9b8b49b59ef104b01f079245|
| L3 |16598|26fe2560d12ed794a572186d4f66217a430838f6e1f345f5f6f2f2f0df734abf|

The FW31-source composite independently assembles L1 at fileoffset0, L2 at32, zero gap298..511, and L3 at512. It is17110bytes and byte-equal to the earlier composite, SHA256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`. The proposed E00000 memory base and placement are still **HYPOTHESE**. File byte equality does not observe loading, startup, processor derivative, DPP/SFR meanings or execution.

This closes the prior source question of whether these particular FW31-installed payload bytes differ from the studied FW30 blobs. Historical static analyses remain bound to their original records/configuration/hashes; the new evidence makes the identical-byte correspondence explicit. No old runtime/test PASS is relabeled as a new FW31 run. New C166 analysis/replay, target tests and hardware behavior are **NOT_RUN**. Runtime provider selection, image/device equivalence and a general FW30/FW31 ABI remain **OFFEN**.

`artifact-additions.tsv` is a separate four-row catalog. It preserves the existing revision-bound manifest/artifacts.tsv without altering older pinned inputs. Manufacturer bytes remain private, LOCAL_OFFLINE_USE; no repository upload or deployment occurs. Source identity/extraction/comparison/byteassembly validation: **PASS**. Method: Root Self-Review, independent Luna source audit requested separately.
