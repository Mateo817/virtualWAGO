> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-214 — statische Bindungsanforderung des Getter-PLT-Slots

## Ergebnis

**VERIFIZIERT (file-backed):** Die eigenen ELF-Metadaten von `libIoDrvDal.so.1.0.2` verlangen keine eager Bindung für `adi_GetApplicationInterface`. Der Import hat in `.rel.plt` eine `R_ARM_JUMP_SLOT`-Relokation am ELF-GOT-VA `0x16030`. Die Dynamic Section enthält weder `DT_BIND_NOW`, `DT_FLAGS` mit `DF_BIND_NOW` noch `DT_FLAGS_1` mit `DF_1_NOW`. Das ELF lässt damit statisch einen ersten Lazy-Resolver-Durchlauf zu; das belegt keinen tatsächlich erfolgten Lazy-Lauf.

Die Zielrelokation liegt außerhalb des durch `PT_GNU_RELRO` beschriebenen Bereichs. `PT_GNU_RELRO` deckt `[0x15e20, 0x16000)` ab; der Slot `0x16030` liegt dahinter. Das ist zusätzliche file-backed Einordnung, kein Laufzeitnachweis.

## Eingabe und Werkzeuge

- Artefakt: `FW31-IODRVDAL-1.0.2`, `sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`
- Frisch gemessen: 25,976 Bytes; SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.
- REA zuerst aufgerufen: `mcp__rea__inspect_binary_layout`, `detail=summary`, auf genau diesem Pfad. Es lieferte `provider_unavailable`: erforderlich sei ein absolutes `REA_PWNTOOLS_PYTHON` mit pwntools 4.15.0, pyelftools 0.33 und Unicorn 2.1.2; der beobachtete konfigurierte `executable_path` war leer. Daher wurde kein REA-Evidence erzeugt; es wurde keine identische REA-Operation wiederholt.
- Zulässiger Fallback: GNU readelf 2.44 und GNU objdump 2.44 (GNU Binutils for Debian), lokal vorhanden.
- `objdump -d -j .plt` meldete `can't disassemble for architecture UNKNOWN!` und fand die angegebene Section unter dieser hostseitigen Architekturbehandlung nicht. Kein Wiederholungsversuch. Die file-backed PLT-/GOT-Worte wurden mit `objdump -s` gelesen; `.plt`-Bytes liegen in den ELF-Abschnitten und Phdrs, `.got`-Bytes und Linkage zusätzlich in readelf-Ausgaben.

## Beobachtungen

ELF-Header: ELF32, little-endian, `ET_DYN`, ARM, EABI5, hard-float; Header 52 Bytes, 6 Program Header, 25 Section Header. Program Header Table bei Dateioffset `0x34`, Section Header Table bei `0x6190`. Der Entry Point ist `0x0`.

Relevante vollständige Program-Header-Zeilen aus `readelf -lW`:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Die zugehörigen Section Header aus `readelf -SW` sind:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`PT_DYNAMIC` and `.dynamic` both bind the dynamic table to file offset `0x5ebc`, ELF VA `0x15ebc`, size `0x140` (320 bytes). `DT_PLTGOT` is `0x16000`, `DT_JMPREL` is `0x8c0`, `DT_PLTRELSZ` is 136, and `DT_PLTREL` is `REL`. `.rel.plt` is file offset `0x8c0`, ELF VA `0x8c0`, size `0x88`; each ARM REL entry is 8 bytes. The getter is dynamic symbol index 14 and its complete relocation line is:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

The relocation target is ELF-GOT VA `0x16030`; its `.got` section-relative offset is `0x30`, and its file offset is `0x6030`. The original file-backed bytes there are `54 09 00 00` (little-endian word `0x00000954`). This is the on-disk initial word only, not a process address or proof of runtime slot contents. `.plt` begins at ELF VA/file offset `0x954`; its complete raw section bytes were emitted by `objdump -s -j .plt`. The tenth `.rel.plt` entry (zero-based index 9, the getter) corresponds to raw PLT bytes at ELF VA/file offset `[0x9d4, 0x9e0)`: `00 c6 8f e2 15 ca 8c e2 54 f6 bc e5`. This is a byte-range association only; `objdump -d` could not decode ARM here. `objdump -s` reports the same `.got` bytes; in particular the row at `0x16030` begins `54090000`.

`readelf -dW` reports 36 dynamic entries. Binding-related complete lines:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

The dump contains no `BIND_NOW` entry, no `FLAGS` entry, and no `FLAGS_1` entry. The relevant version metadata lists the getter as an unversioned undefined `FUNC` symbol; version needs are only `GLIBC_2.4` and `GCC_3.5` for other imports. No version requirement supplies an eager-binding flag.

## Schlussfolgerung, Alternativen und Grenzen

The observed `R_ARM_JUMP_SLOT` is the file-backed PLT relocation for the getter. The ELF declares PLT relocations and has no encoded eager-binding request, so a lazy first resolution remains statically permitted by the file metadata. This answers only whether this ELF itself demands eager binding.

An environment such as `LD_BIND_NOW`, an already executed getter call, or other loader/process state could change when binding occurs; these are runtime questions and were not inspected. No runtime loading, symbol resolution, relocation write, resolver register effect, API/ABI contract, or calling convention was tested or inferred. The initial GOT word is not treated as evidence of a resolver protocol. No code body or library implementation was analyzed.

The result is bounded by file-backed metadata parsed by GNU binutils 2.44 after the REA provider gap. The independent REA layout evidence was not available. The host objdump could not decode the ARM PLT instructions, so the raw PLT bytes are retained rather than decoded. These limits do not obscure the dynamic binding tags or the getter relocation itself, which readelf decoded from the exact input.

## Reproduktion und Ausgabeintegrität

`python3 validate.py` checks the exact input size and SHA-256, invokes GNU readelf, verifies the getter's relocation and key dynamic/program-header facts, and validates the output hashes in `SHA256SUMS`. `metadata.tsv` records raw file ranges, ELF virtual addresses, relocation identity, binding tags, and evidence status. No REA bundle was generated because REA returned no analysis record.

Validation status: `python3 validate.py` — **PASS**; `sha256sum -c SHA256SUMS` — **PASS**; runtime binding observation — **NOT_RUN**; ARM PLT disassembly through host objdump — **BLOCKED**.

`SHA256SUMS` covers `report.md`, `metadata.tsv`, and `validate.py`.
