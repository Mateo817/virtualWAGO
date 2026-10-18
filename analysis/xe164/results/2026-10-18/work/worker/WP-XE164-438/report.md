> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-438 — independent review of WP437

**Result: VERIFIZIERT** for WP437's static artifact binding and container arithmetic. This review is independent static analysis; WP437 remained unchanged.

I recomputed all eight WP437 manifest hashes and ran its read-only validator. I independently checked the FW31 image and WP145 inventory hashes, copied the partition range to temporary storage, and used `debugfs stat`/`dump` for inode 50. The fresh `/boot/linux` dump is exactly 8,213,856 bytes and byte-identical to WP437's pinned file, SHA-256 `f6e03d6452e4648cd86f58ff5c869af0ebdcc6e8f3123458c73d6e81ccfede65`. No mount was used.

Independent parsing confirms a 64-byte legacy uImage header, magic `0x27051956`, payload length 8,213,792 bytes, header CRC `0x75c25a9e` after zeroing the CRC field, and payload CRC `0x5f20e326`. The image length equals 64 plus payload length. Fields decode as OS 5, ARM architecture 2, kernel-image type 2, compression ID 0, and load/entry values `0xffffffff`. The name bytes encode `Linux-6.6.94-rt56-w05.08.02`. The inner payload has little-endian zImage magic `0x016f2818` at offset `0x24`, start `0`, end `0x7d5520`; the end-start difference equals the full payload length. The host `file` utility also identifies the full container as an uncompressed legacy uImage. These checks validate the header and lengths, not that the image is bootable or running.

The nine-byte LZO signature occurs at file offsets `0x467c` and `0x488c`. The first occurrence is amid decompressor-related strings and is not evidence of compressed data. A 256-byte slice beginning at `0x488c` is classified by host `file` as lzop 1.040 / LZO1X-999 / Unix. That is only a candidate-byte classification. The outer compression field is zero, and no stream validation, decompression, or kernel execution was performed. WP437 correctly leaves actual LZO payload validity and code analysis open.

No evidence here establishes kernel loadability/start, current kernel identity, driver binding, UAPI/ioctl details, device mapping, or a replacement contract. Native execution, VM, network, and hardware tests were NOT_RUN. CRCs are internal consistency checks; source identity comes from the pinned image/inventory hashes and exact inode dump.

Validation: all package/source hashes, exact inode/size binding, CRCs, inner header relation, and signature offsets PASS; decompression and execution NOT_RUN.
