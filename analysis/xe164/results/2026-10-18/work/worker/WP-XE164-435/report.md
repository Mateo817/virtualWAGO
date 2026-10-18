> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-435 — independent review of WP434

**Result: VERIFIZIERT** for the bounded metadata and extraction claims in WP434. This is an independent static review, not a runtime test. WP434 remained unchanged.

I recomputed the ten entries in WP434's manifest and ran its default validator with bytecode writing disabled; every hash matched and the validator passed. I independently checked the FW31 image SHA-256 and WP145 partition-inventory SHA-256, then copied the pinned partition range to a temporary file and used read-only `debugfs stat`/`dump` for the four exact inodes. The fresh files matched WP434 byte-for-byte, including path, inode, size, and SHA-256. No mount was used. The temporary extraction was discarded after comparison.

The bounded case-insensitive search over NUL/newline-separated fields for `kbus|wago|scpu|xe164` exactly reproduces the ten saved hits. They include `kernel/drivers/spi/spi-kbus.ko`, plus author strings; the latter do not identify interfaces. The NUL fields bind `spi_kbus.file=drivers/spi/spi-kbus`, `spi_kbus.description=WAGO KBUS SPI Driver`, `spi_kbus.license=GPL v2`, `spi_kbus.parm=major:Set the kbus major number statically instead of dynamically if a non-zero value is given.`, and `spi_kbus.parmtype=major:int`. This supports a built-in metadata candidate and the text/type of a parameter. It does not establish the configured numerical major, active kernel, loaded/bound driver, device node, ioctl surface, TTY relation, or implementation contract.

`modules.devname` names only `cuse` and `uinput`; `modules.alias` has no kbus alias. This absence is bounded to those files and is not proof that no other binding path exists. The path `6.6.94-rt56-w05.08.02` is artifact metadata, not an active-kernel observation. `/boot/linux` remained inventory-only. No code, kernel, VM, network, or hardware was executed.

Evidence limits: actual UAPI/ioctl handlers and layouts, TTY path and binding, runtime registration, concrete major number, device-tree association, and a lower replacement boundary remain **OFFEN**. This review does not join the similarly named WP408 numeric ioctl values or WP430 TTY path to `spi_kbus`.

Validation: package hashes, source-image/inventory identities, exact object hashes, bounded hits, and field assertions PASS; actual kernel/device behavior NOT_RUN.
