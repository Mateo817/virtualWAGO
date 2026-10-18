> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-265 — FW31 dynamic-loader image provenance and metadata

**Scope:** exact firmware-image provenance for `/lib/ld-linux-armhf.so.3` and metadata that narrows the dynamic-resolution question. This is evidence about the FW31 image’s installed filesystem, not proof of what a running device loaded. The image was not mounted or executed. Only the assigned regular inode was extracted into this private package. No function body, disassembly, call graph, runtime binding, or function address was examined or inferred.

## Provenance

The input image is 287,309,824 bytes with SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c`. Partition 2 is the 262,144,000-byte filesystem slice beginning at byte 25,165,824; the prior inventory records ext UUID `373f7dc3-cbe8-44a1-b974-a3c99d616970`. The fresh image hash was checked immediately before extraction.

The requested path resolves within that partition as `/lib` (symlink inode 981, target `usr/lib`) followed by `/usr/lib/ld-linux-armhf.so.3`, a regular file at inode 1396, mode `100755`, size 175,592 bytes. `extract_loader.py` sliced the exact partition to a temporary file and used `/sbin/debugfs` read-only `stat`/`dump`; it did not mount the image. The extracted loader SHA-256 is `366d9f2f5584ce374cb1a7a2222067d0c99aabee4bac6a475c160ce04ed4dd33`. Inventory and symlink evidence are hash-pinned in `sourcepins/pins.tsv`; raw filesystem metadata and extraction results are retained in `metadata/extraction.json`.

The exact image `/usr/bin/codesys3` inventory entry is inode 1033, size 5,181,396, and its hash matches the independently retained file used for context. `/usr/lib/libIoDrvDal.so.1.0.2` is inode 1419, size 25,976, and matches the prior exact-image extraction. Their hashes and reports are pinned; these two binaries are used only for ELF dynamic-import context.

## ELF and loader-layout observations

GNU `readelf` identifies the extracted loader as ELF32, little-endian, ARM, type `DYN`, EABI version 5 with the hard-float ABI flag. ARM attributes declare ARMv7-A, Thumb-2, VFPv3, NEON, and VFP register arguments. The GNU build ID is `be2cac06e4dff92341528393c00b1b328d704130`. Full header, program-header, dynamic, section, note, ARM-attribute, and version metadata are retained under `metadata/`.

The loader’s dynamic table declares SONAME `ld-linux-armhf.so.3`, no `DT_NEEDED` entries, `DT_PLTRELSZ=40` bytes, `DT_PLTREL=REL`, and `DT_JMPREL` metadata. Its declared `.dynsym` contains 42 entries. The ELF has no other declared symbol table in the readelf output. Neither `_dl_runtime_resolve` nor `_dl_fixup` appears in the available declared symbol table. This is strictly a symbol-coverage result: it does not show that resolver code is absent from the binary, identify local or stripped symbols, or establish lazy-binding behavior.

I attempted REA `inspect_binary_layout` first. It was **BLOCKED** because the configured pwntools provider environment (`REA_PWNTOOLS_PYTHON`) is unset; the operation requires caller-supplied pwntools, pyelftools, and Unicorn versions. No tool was installed. Ghidra 12.1.4 was available, so I opened the extracted ELF read-only and requested only `list_segments`. Evidence `ev_d1a6659d2f0b98f55bde4d16f4762d84ad59a8157e6b8306be1f43acbb31a2f1` binds to the extracted hash and reports the ARM memory-block/section layout, including executable `.plt` and `.text` blocks, non-executable data, and uninitialized `.bss`. The retained segment table records section boundaries only; no function inventory or body was requested.

## Exact-object dynamic-import context

The pinned `codesys3` ELF declares `/lib/ld-linux-armhf.so.3` as `PT_INTERP`. Its dynamic metadata lists nine `DT_NEEDED` libraries, 7,569 `.dynsym` entries (711 undefined), and 708 `.rel.plt` entries. The undefined dynamic symbols include versioned `dlopen`, `dlsym`, and `dlclose` imports. The pinned `libIoDrvDal.so.1.0.2` has 31 `.dynsym` entries (21 undefined), 11 `DT_NEEDED` libraries, and 17 `.rel.plt` entries. Complete dependency-name and relevant-import counts are in `metadata/dynamic_import_context.json`; relocation addresses and loader behavior are intentionally omitted.

Together, these observations bind the image interpreter path to the exact loader inode and show dynamic-link metadata in the exact `codesys3` and DAL objects. They narrow the previous lazy-resolution provenance gap at the artifact level. They do not prove that a device booted this image, that the loader ran, that a specific relocation was lazily or eagerly resolved, or how any component entry symbol was found or invoked.

## Validation and retained evidence

`python3 validate.py` is read-only. It verifies input, tool, and extracted-file pins; reconstructs the `/lib` symlink resolution from the hash-pinned filesystem inventory; checks ELF metadata against fresh `readelf` output; checks symbol coverage without emitting symbol values; and validates the context import summaries and Ghidra segment evidence binding. `manifest.sha256` covers every package file except itself, including the private extracted vendor ELF. Self-review only; no independent review is claimed.

The package contains `extract_loader.py`, the private `extracted/ld-linux-armhf.so.3`, source and tool pins, metadata files, `validate.py`, and the self-free manifest. Do not copy the extracted vendor bytes into the public repository.
