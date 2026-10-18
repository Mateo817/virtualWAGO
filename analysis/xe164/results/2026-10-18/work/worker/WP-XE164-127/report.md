> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-127 — Exakter FW31-Partition-2-Bytehit `CmpIoMgr__Entry`

## Ergebnis

**VERIFIZIERT:** Die angegebene, hashgebundene FW31-Partition 2 enthält die exakte case-sensitive ASCII-Bytefolge `CmpIoMgr__Entry` genau einmal in genau einer regulären Datei: `/usr/bin/codesys3`. Der Byteoffset innerhalb dieser Datei ist dezimal `353036` (`0x5630c`). Die Datei ist 5.181.396 Bytes groß und hat SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.

**VERIFIZIERT:** `readelf -hW` klassifiziert die extrahierte Trefferdatei als ELF32, little-endian, `EXEC (Executable file)`, ARM. `readelf -Ws` enthält in `.dynsym` die exakte Zeile:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Damit ist der Name ein definierter dynamischer Symboltabelleneintrag (Index 3631, Wert `00336a84`, Größe 348, Typ `FUNC`, Bindung `GLOBAL`, Sichtbarkeit `DEFAULT`, Abschnittsindex 14). Dies ist ELF-Metadatum, kein vollständiger API- oder Aufrufvertrag. `readelf -rW` enthält in dieser Datei keine Zeile mit dem exakten Symbolnamen. Der Bytehit und der definierte `.dynsym`-Eintrag belegen weder einen tatsächlichen Aufruf noch Laufzeitnutzung.

## Identität und Suchgrenze

| Objekt | Identität | Status |
|---|---|---|
| Firmwareimage | `PFC-G2-Linux_sd_V040901_31_r9d0900aaed.img`, 287.309.824 Bytes, SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` | VERIFIZIERT — vor Scan geprüft |
| Partition 2 | Offset 25.165.824 Bytes, Länge 262.144.000 Bytes, ext UUID `373f7dc3-cbe8-44a1-b974-a3c99d616970`, ext-Magie `53 ef` | VERIFIZIERT — Imagegrenze, Superblockmagie und UUID geprüft |
| Inventur | 489 besuchte Verzeichnisse, 3.058 reguläre Dateien | VERIFIZIERT — kompletter read-only `debugfs`-Traversal |
| Fehlerzähler | 0 Verzeichnis-, 0 Listing-Parse-, 0 Datei-Lese-/Größenfehler | PASS |
| Byte-Suche | nur die exakte ASCII-Folge `CmpIoMgr__Entry` in regulären Dateien der Partition 2 | VERIFIZIERT |

`inventory.csv` enthält das vollständige reguläre-Datei-Inventar mit Rootfs-Pfad, Inode, Modus und Größe. `scan_summary.json` bindet die Inventur an Imagehash, Partitionsgrenze und UUID. `validate.py` führt die vollständige Inventur und Byte-Suche erneut aus und vergleicht alle Scanprodukte und extrahierten Trefferdateien byte-/hashgenau. Symlinks, Verzeichnisnamen, andere Partitionen und andere Namenssuchmuster waren nicht Teil des Scopes.

## Treffer- und ELF-Metadaten

| Rootfs-Pfad | Größe | SHA-256 | Byteoffset | ELF-/Symbolmetadaten | Relocationmetadaten |
|---|---:|---|---:|---|---|
| `/usr/bin/codesys3` | 5.181.396 | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | 353036 (`0x5630c`) | ELF32, little-endian, `EXEC`, ARM; `.dynsym`: `3631: 00336a84   348 FUNC    GLOBAL DEFAULT   14 CmpIoMgr__Entry` — definiert, nicht `UND` | Keine passende Zeile in `readelf -rW` |

Die obige `readelf -Ws`-Zeile ist in `elf_metadata.txt` wortgetreu festgehalten. `elf_findings.csv` hält zusätzlich die getrennten Symbolfelder und den unveränderten Zeilentext fest. Für die extrahierte Trefferdatei wurden ausschließlich `readelf -hW`, `readelf -Ws` und `readelf -rW` verwendet. Keine andere Datei erhielt eine ELF-Analyse.

Ein roher Bytehit ist ausschließlich ein Vorkommen der verlangten Bytes. `.dynsym` definiert hier einen `FUNC`-Eintrag mit `GLOBAL DEFAULT` und Abschnittsindex 14; er ist kein Undefined-/Importeintrag. Eine Relocationreferenz wurde in der Standardausgabe nicht gefunden. Weder der Name, der Export noch das Fehlen einer Relocationzeile zeigen, ob Runtimecode den Eintrag aufruft oder wie ein vollständiger Funktionsvertrag aussieht.

## Methode und Werkzeuge

Die Eingabehases wurden zu Beginn gegen die angegebenen Werte geprüft:

- Firmwareimage: SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c`, 287.309.824 Bytes.
- WP112-Methodenbericht: SHA-256 `af887649aee9bdd435f5e5fe41e395edecb07501340fb12d5bdde2191ee44051`, 11.269 Bytes.
- WP112-Referenzscanner: SHA-256 `a7a955f3917fdb358020ee553c0a3246072ca6b0ac8716ccda41e59991d0abfb`, 13.049 Bytes.

WP112 dokumentiert bereits die Lücke des REA/file-level Scopes: er inventarisiert nicht den vollständigen Inhalt des ext-Dateisystems. Diese bekannte Lücke wurde für die hier geforderte Vollständigkeit nicht erneut als Inventurmethode verwendet. Der WP112-Bericht und Scanner dienten als verifizierte Methodenreferenz; der neue `scan.py` ist auf den einen hier gefragten Suchnamen beschränkt.

Der REA-Aufruf `inspect_firmware_regions` wurde zuerst auf dem angegebenen Image versucht. Er war BLOCKED, da in der Sitzung kein absoluter `REA_BINWALK_COMMAND` konfiguriert ist (`capability_unavailable`, Provider `binwalk`). Damit ist keine Binwalk-Signaturabdeckung beansprucht. Der anschließende gezielte read-only Fallback kopierte nur Partition 2 temporär aus dem geprüften Image, prüfte ext-Magie und UUID und traversierte mit `debugfs` inode-basiert alle regulären Dateien. Die temporäre Partitionskopie wurde beim Scanende entfernt. Persistiert wurde nur die eine Trefferdatei.

Werkzeuge: Python 3.13.5; `/sbin/debugfs` 1.47.2 / EXT2FS Library 1.47.2; GNU `readelf` / Binutils 2.44. Der Validator wiederholt den Scan in einem temporären Ausgabeverzeichnis und vergleicht Inventar, Treffer, Tabellen, Zusammenfassung und extrahierte Treffer. Reproduktion aus diesem Verzeichnis:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

## Status, Alternativerklärung und Restunsicherheit

| Aussage / Prüfung | Status |
|---|---|
| Imagehash und Imagegröße | VERIFIZIERT |
| Partitionsgrenze, ext-Magie und UUID | VERIFIZIERT |
| Vollständiger regulärer-Datei-Traversal, null Fehler | VERIFIZIERT |
| Exaktes Bytevorkommen, Rootfs-Pfad, Offset, Größe und Datei-SHA-256 | VERIFIZIERT |
| ELF-Header-, `.dynsym`- und Relocationausgabe | VERIFIZIERT |
| REA-Firmware-Signaturinspektion | BLOCKED — `REA_BINWALK_COMMAND` nicht verfügbar |
| Laufzeitaufruf, Verhalten, Semantik oder API-Vertrag | OFFEN |

Eine plausible Alternativerklärung ist, dass die Bytes im ELF-Dateiinhalt als Symbolname gespeichert sind, ohne dass daraus ein tatsächlicher Runtimeaufruf folgt. Der definierte `FUNC`-Dynsym-Eintrag beschreibt Linker-/Loader-Metadaten; kein dynamischer Aufrufgraph, Decompilation, Xref oder Laufzeittest wurde durchgeführt. Standard-`readelf`-Nullbefunde begrenzen sich auf diese Trefferdatei und die ausgegebenen Symbol-/Relocationtabellen. Es gab keine Runtime-, Geräte-, Netzwerk- oder VM-Aktion.

Self-Review: Eingabeidentität, vollständige Inventur, exakter Treffer, extrahierte Dateibindung, ELF-Metadaten und reproduzierbarer Validator wurden geprüft. Kein unabhängiger Review oder Worker-Lauf wird behauptet. Tests/Validierung: PASS nach erfolgreichem `validate.py` und `sha256sum -c SHA256SUMS`.

## Erzeugte Dateien

- `report.md` — Befund, Scope, Status, Grenzen und Methode.
- `scan.py` — hash- und partitionsgebundener Vollscan; schreibt ausschließlich Trefferdateien dauerhaft.
- `validate.py` — deterministischer Vollscan- und Artefaktvergleich.
- `inventory.csv` — alle 3.058 regulären Dateien in Partition 2.
- `string_hits.csv` — jeder exakte Treffer und Byteoffset.
- `hit_files.csv` — Rootfs-Pfad, Größe, SHA-256, Offset(s) und Extraktionspfad je Trefferdatei.
- `hit_files/usr/bin/codesys3` — einzige extrahierte Trefferdatei.
- `elf_headers.csv`, `elf_findings.csv`, `elf_metadata.txt` — Standard-ELF-Metadaten ausschließlich für die Trefferdatei.
- `scan_summary.json` — Image-/Partitionbindung, Zähler und Fehlerliste.
- `SHA256SUMS` — Hashes aller persistenten Dateien außer `SHA256SUMS` selbst.

SHA-256 aller erzeugten Dateien sind in `SHA256SUMS` festgehalten.
