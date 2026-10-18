> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-072 — FW30-IPK/FW31-provider identity reconciliation

## Result

**VERIFIZIERT**, bounded artifact-identity scope: the manifested 77,686-byte
`libpackbus_1.0.3_armhf.ipk` contains the five regular files and three symbolic
links listed in `payload-inventory.tsv`, including the regular payload member
`./usr/lib/libpackbus.so.1.0.1`. The accepted prior extraction of that member is
148,792 bytes and has SHA-256
`3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`.

The revision-bound public contract report, itself bound in `inputs.tsv`, names
that same digest as the actual backed-up FW31 `libpackbus.so.1.0.1`. Equality
of SHA-256 and byte size binds the extracted file to the documented FW31
provider artifact. This makes the extracted provider suitable for bounded
static questions such as the implementation of its `Push` handler.

The IPK data archive contains no member named `libIoDrvDal` or `libIoDrvKbus`.
It therefore does not supply the exact ARM consumer artifacts needed to extend
the existing partial manager-lifecycle reconstruction.

## Method and observations

- Recomputed the IPK, extracted provider, and public report byte sizes and
  SHA-256 values.
- Listed the `ar` members and streamed `data.tar.gz` into tar for a
  format-aware payload listing; originals were not modified.
- Recomputed hashes for the five regular extracted payload files and recorded
  link targets separately.
- `file`/`readelf` identify the provider as a stripped ELF32 little-endian ARM
  EABI5 shared object with hard-float ABI and build-id
  `1e025c5f82908ba6d9f9676d2de99c0cf6e56a04`.
- REA was not invoked for package identity: archive inventory and hashing are
  the sufficient format-aware operations. Handler analysis is separated into
  WP-XE164-073 and is REA-first.

## Alternatives, limits, and status

The matching digest is an artifact-identity statement only. It does not make
other FW30 libraries, headers, configuration, or XE164 stages a FW31 ABI, and
does not prove which image was active at runtime. The public report is a
revision-bound record of the backed-up FW31 identity, not a fresh device
inventory. No runtime, device, target network, VM, or hardware action occurred.

- Package/hash/inventory validation: **PASS**.
- FW31-provider digest reconciliation: **PASS**.
- Runtime provenance and active-load verification: **NOT_RUN**.
- Hardware verification: **NOT_RUN**.
- Full original manager lifecycle from this package alone: **BLOCKED** by the
  absence of exact `libIoDrvDal` and `libIoDrvKbus` payload members.

Review: GPT-6.1 SOL root **Self-Review**. No independent review is claimed.
