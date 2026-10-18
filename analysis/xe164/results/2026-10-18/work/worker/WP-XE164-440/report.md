> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-440 — local decoder availability for the frozen kernel candidate

**VERIFIZIERT:** The exact WP437 candidate is preserved byte-for-byte at `inputs/linux` with SHA-256 `f6e03d6452e4648cd86f58ff5c869af0ebdcc6e8f3123458c73d6e81ccfede65`. Its WP437 source remains unchanged. The environment has no `lzop` or `lzo` executable, no BusyBox, no Python LZO/LZOP module, and no installed LZO headers or discoverable host `liblzo` shared library. `ldconfig` itself is absent, so no ldconfig cache inventory was available. `xz`, `unxz`, `gzip`, and `uncompress` are present but do not provide the needed LZO decoding path.

A local SDK archive `lzo-2.10.tar.gz` is present and hash-pinned. It contains LZO library decoder source (`src/lzo1x_d1.c`) and an `examples/lzopack.c` example with its own `00 e9 4c 5a 4f ff 1a` format and compress/decompress/test modes. That is source, not an installed host decoder. Its example format has not been shown compatible with the kernel candidate's stream. The archive contains no `lzop` CLI source. The system also contains x86 GRUB `lzopio.mod` modules and GRUB host tools; these were classified and hash-pinned, but no validated route was established for using them as a host decoder for this ARM kernel stream.

`file` classifies a candidate region as an lzop/LZO1X stream, but that is only a format guess from file signatures. With no compatible validated host decoder identified, the stream was not unpacked or checksum-verified. No unpacked-data hash or KBus string inventory is claimed. The candidate and its original WP437 evidence remain frozen. Kernel execution, installation, network access, and hardware access were **NOT_RUN**.

Validation: **PASS** — `validate.py` checks the candidate hash against WP437, the pinned archive and source-member hashes, recorded tool/library/module availability, absence of any decoded output, manifest coverage, and package immutability. The check reads archive members to stdout only; it does not extract or run them.
