> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-441 — bounded FW31 DTB metadata inventory

**Result: VERIFIZIERT** for the exact static extraction and raw-string observations described here. No DTB was selected for a device or decoded as a live configuration.

The task initially described eleven `/boot/am335x-pfc-*.dtb` files with inodes 14–24. Fresh read-only `debugfs ls -l /boot` and the pinned WP145 inventory show ten regular DTB files at inodes 14–23. Inode 24 is the `emmc0/` directory, not a DTB. I extracted exactly those ten listed files by inode from the FW31 image's temporary partition copy; each path, inode, size and SHA-256 matches the inventory. The image and inventory SHA-256 values match the established pins. No mount or source-image writes occurred.

The host has no `dtc`, `fdtget`, or `fdtdump`, so analysis is limited to finite raw byte matching and printable ASCII runs. Every one of the ten extracted files contains the byte strings `kbus@0`, `wago,spi-kbus`, and `kbus,tty-device`, alongside a model/board-ID string. The model strings vary: two PFC100 strings (`750-8110/8111`, `750-8112`) and eight PFC200 strings (`750-8210` through `750-8217`), each paired with a distinct raw `wago,am335x-pfc-*` identifier recorded in `raw-string-summary.json`. The exact printable string `ttyKbus` is absent in all ten. This establishes candidate strings in each artifact, not that `wago,spi-kbus` is a parsed `compatible` property or that `kbus,tty-device` belongs to a particular node. The bounded raw hit list is retained in `raw-token-hits.json`; it includes incidental substring matches and must not be read as a decoded tree.

These files add a plausible SPI-KBUS-compatible metadata lead across the ten candidate DTBs, but cannot establish which tree was loaded, whether a node is enabled, a selected SPI controller/device path, the runtime TTY name, or actual driver binding. No UAPI/ioctl or hardware behavior is inferred. Runtime configuration and node/property associations remain **OFFEN**. No device, VM, network, or native target code was run.

Validation: source and inventory pins, all ten inode/path/size/hash bindings, bounded raw hits, summary strings and unchanged package inventory PASS. DTB parsing, runtime selection, and hardware testing NOT_RUN.
