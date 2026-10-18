> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-112 — FW31-Namenshits und ELF-Metadaten

## Ergebnis

**VERIFIZIERT:** Im hashgebundenen FW31-SD-Image enthält Partition 2 insgesamt 23 exakte, case-sensitive ASCII-Bytevorkommen der Namen `IoMgrConfigGetParameterValuePointer` und `pfIoMgrConfigGetParameterValuePointer`, verteilt auf neun reguläre Dateien. Vollständige Dateiliste, Größe, SHA-256 und extrahierter Pfad stehen in `hit_files.csv`; alle einzelnen Byteoffsets stehen in `string_hits.csv`.

`IoMgrConfigGetParameterValuePointer` hat 16 Bytevorkommen. In der dynamischen Symboltabelle von `/usr/bin/codesys3` ist es als definiertes Symbol `FUNC GLOBAL DEFAULT`, Wert `0x32e814`, Größe 84, Abschnittsindex 14 eingetragen. Ein exakter Import/Undefined-Eintrag und eine passende Relocationzeile für diesen unpräfixierten Namen wurden nicht gefunden.

`pfIoMgrConfigGetParameterValuePointer` hat sieben Bytevorkommen. In sieben Treiberbibliotheken ist es jeweils als definiertes `.dynsym`-Symbol `OBJECT GLOBAL DEFAULT` eingetragen. Sechs dieser Dateien enthalten außerdem je eine `R_ARM_GLOB_DAT`-Relocationzeile für den längeren Namen; `libIoDrvCanL2.so.1.0.2` hat keine passende Relocationzeile. Für den längeren Namen wurden keine exakten Import/Undefined-Einträge gefunden.

Die unpräfixierte Bytefolge überlappt siebenmal mit einem Treffer des längeren Namens: ihr Beginn liegt jeweils zwei Bytes nach dem Beginn von `pfIoMgrConfigGetParameterValuePointer`. Die übrigen neun unpräfixierten Bytevorkommen sind separate Texttreffer, deren Bedeutung nicht aus diesem Scan folgt.

## Identität und Suchgrenze

| Ebene | Identität | Befundstatus |
|---|---|---|
| Image | `PFC-G2-Linux_sd_V040901_31_r9d0900aaed.img`; 287.309.824 Bytes; SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` | VERIFIZIERT — Größe und SHA-256 geprüft |
| Partition 2 | Offset 25.165.824 Bytes, Länge 262.144.000 Bytes; ext-Magie `0xEF53`; UUID `373f7dc3-cbe8-44a1-b974-a3c99d616970` | VERIFIZIERT — Grenzen und Superblockidentität aus dem Image geprüft |
| Dateisysteminhalt | Read-only `debugfs`-Traversal von Partition 2; 489 besuchte Verzeichnisse; 3.058 reguläre Dateien | VERIFIZIERT — null Traversierungs-, Parse-, Datei-Lese- oder Größenfehler |
| Trefferdateien | Neun extrahierte Dateien in `hit_files/`; jeweils Größe und SHA-256 in `hit_files.csv` | VERIFIZIERT — jede extrahierte Datei gegen die gelistete Partitionsdateigröße geprüft und gehasht |
| WP107-Methodenbericht | `WP-XE164-107/report.md`; 5.134 Bytes; SHA-256 `abb13e7162237132ce6852af546c88eb449e6e8fbe144146da7b501483b84aab` | VERIFIZIERT — korrigierte lokale Identität stimmt mit der korrigierten Aufgabenangabe überein |

Die Suche gilt ausschließlich den zwei exakten ASCII-Bytefolgen in regulären Dateien von Partition 2. Symlinks, Dateinamen, andere Partitionen und imagefremde Inhalte waren keine Suchziele. Binärdateien wurden nicht ausgeführt.

## ELF-Metadaten je Trefferdatei

Alle neun Trefferdateien sind laut `readelf -hW` ELF32, little-endian, Maschine ARM. `/usr/bin/codesys3` ist `ET_EXEC`; die übrigen acht Dateien sind `ET_DYN`. `readelf -Ws` gab für alle Trefferdateien `.dynsym` aus und keine `.symtab`-Tabelle. Vollständige Headerklassifikation ist in `elf_headers.csv`; exakte Symbol- und Relocationzeilen stehen in `elf_findings.csv` und `elf_metadata.txt`.

| Datei | Exakte Byte-Namen | ELF-Symbolbefund | Exakte Relocations |
|---|---|---|---|
| `/usr/bin/codesys3` | `IoMgrConfigGetParameterValuePointer` | `.dynsym`: `FUNC GLOBAL DEFAULT`, Wert `0x32e814`, Größe 84, Ndx 14; definiert | keine |
| `/usr/lib/libIoDrvBacnet.so.1.5.0` | beide | `pf...`: `.dynsym OBJECT GLOBAL DEFAULT`, Wert `0x131ac`, Größe 4, Ndx 21; definiert | `R_ARM_GLOB_DAT` bei `0x13124`, referenziert `pf...` |
| `/usr/lib/libIoDrvCanL2.so.1.0.2` | beide | `pf...`: `.dynsym OBJECT GLOBAL DEFAULT`, Wert `0x12128`, Größe 4, Ndx 21; definiert | keine |
| `/usr/lib/libIoDrvCanM.so.1.0.2` | beide | `pf...`: `.dynsym OBJECT GLOBAL DEFAULT`, Wert `0x16470`, Größe 4, Ndx 21; definiert | `R_ARM_GLOB_DAT` bei `0x16134`, referenziert `pf...` |
| `/usr/lib/libIoDrvCanS.so.1.0.3` | beide | `pf...`: `.dynsym OBJECT GLOBAL DEFAULT`, Wert `0x164ac`, Größe 4, Ndx 21; definiert | `R_ARM_GLOB_DAT` bei `0x1615c`, referenziert `pf...` |
| `/usr/lib/libIoDrvDal.so.1.0.2` | unpräfixierter Name | kein passender Eintrag in `.dynsym` | keine passende Relocation |
| `/usr/lib/libIoDrvDps.so.0.0.2` | beide | `pf...`: `.dynsym OBJECT GLOBAL DEFAULT`, Wert `0x159a4`, Größe 4, Ndx 22; definiert | `R_ARM_GLOB_DAT` bei `0x15128`, referenziert `pf...` |
| `/usr/lib/libIoDrvKbus.so.0.0.1` | beide | `pf...`: `.dynsym OBJECT GLOBAL DEFAULT`, Wert `0x1a224`, Größe 4, Ndx 21; definiert | `R_ARM_GLOB_DAT` bei `0x190c4`, referenziert `pf...` |
| `/usr/lib/libTscDrm.so.1.7.0` | beide | `pf...`: `.dynsym OBJECT GLOBAL DEFAULT`, Wert `0x16128`, Größe 4, Ndx 22; definiert | `R_ARM_GLOB_DAT` bei `0x160b8`, referenziert `pf...` |

Die `R_ARM_GLOB_DAT`-Zeilen belegen statische dynamische Relocationeinträge. Sie zeigen hier jeweils auf das in derselben Datei definierte `pf...`-Symbol. Sie belegen nicht, wie oder wann eine konkrete Runtime die Relocation auflöst. Das `OBJECT`-Metadatum klassifiziert diese Einträge nicht als Funktion. Der `FUNC`-Eintrag in `codesys3` belegt den exportierten dynamischen Symboltabelleneintrag für den unpräfixierten Namen, aber keinen vollständigen Aufrufvertrag.

## Vollständige und begrenzte Zähler

| Zähler | Wert | Teststatus |
|---|---:|---|
| Besuchte Verzeichnisse | 489 | PASS |
| Reguläre Dateien in Partition 2 | 3.058 | PASS |
| Verzeichnisfehler | 0 | PASS |
| Listing-Parsefehler | 0 | PASS |
| Datei-Lese-/Größenfehler | 0 | PASS |
| Dateien mit Bytehits | 9 | PASS |
| Bytevorkommen `IoMgrConfigGetParameterValuePointer` | 16 | PASS |
| Bytevorkommen `pfIoMgrConfigGetParameterValuePointer` | 7 | PASS |
| Exakte `.dynsym`-Symbolzeilen für unpräfixierten Namen | 1 | PASS |
| Exakte `.dynsym`-Symbolzeilen für `pf...` | 7 | PASS |
| Exakte Relocationzeilen für unpräfixierten Namen | 0 | PASS |
| Exakte Relocationzeilen für `pf...` | 6 | PASS |
| Trefferdateien ohne passenden Symbol-/Relocationeintrag | 1 (`libIoDrvDal.so.1.0.2`, nur unpräfixierter Bytehit) | PASS |

Nullbefunde gelten nur für die exakten Namen, die extrahierten Trefferdateien und die Standardtabellen von `readelf -Ws`/`readelf -rW`. Sie belegen weder fehlendes Laufzeitverhalten noch Abwesenheit in anderen Inhalten oder Kodierungen.

## Methode und Werkzeuge

Der Image-/Dateisystem-Scan folgt der read-only `debugfs`-Traversierungs- und inode-basierten Dump-Methode aus `WP-XE164-107/scan.py`, implementiert in diesem Workpackage durch `scan.py`. Das Image wurde größen- und hashgeprüft; Partition 2 wurde temporär im eigenen Workpackage-Verzeichnis abgelegt, mit UUID/Magie validiert und am Ende entfernt. Nur neun Dateien mit Treffern wurden nach `hit_files/` extrahiert. Keine weiteren Partitionsdateien wurden persistent kopiert.

Werkzeuge: Python 3.13.5; `/sbin/debugfs` e2fsprogs 1.47.2 / EXT2FS Library 1.47.2; GNU `readelf` / Binutils 2.44. Die Standardmetadaten wurden mit `readelf -hW`, `readelf -Ws` und `readelf -rW` erhoben. Der REA-Aufruf aus der ursprünglichen Zwei-Dateien-Auswertung wurde entsprechend der Korrektur nicht wiederholt; für diese vollständige Offline-Auswertung wurden die genannten Standardwerkzeuge eingesetzt.

Reproduktion:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`validate.py` prüft erneut Image- und WP107-Berichtsidentität, führt die komplette Traversierung und Byte-Suche erneut aus, vergleicht Tabellen byteidentisch und vergleicht die extrahierten Trefferdateien nach Pfad und SHA-256.

## Audit der verworfenen Eingabeannahme

Die erste lokale Auswertung verwendete den damals angegebenen `sources/.../rootfs`-Pfad. Dieser Pfad war nur eine Zwei-Dateien-Auswahl und wurde vom Auftraggeber als falsche Scopeannahme korrigiert. Die daraus stammenden vier Bytehits, Tabellen und ELF-Schlüsse sind verworfen und nicht kanonisch. Die obenstehenden Tabellen wurden aus dem direkt hashgebundenen Image und der vollständigen Partition-2-Inventur neu erzeugt.

Der ursprüngliche Aufgabenhinweis nannte einen falschen Hash für den WP107-Bericht. Korrigierte Größe und Hash wurden für diese Reproduktion geprüft. Die bisherige Zwei-Dateien-Interpretation der Rootfs-Vollständigkeit wird zurückgezogen.

## Alternativerklärung und Restunsicherheit

Rohe Textvorkommen außerhalb von ELF-Symbolnamen können Konstanten, Beschreibungen oder andere Daten sein; ihre Bedeutung wurde nicht rekonstruiert. Symbolbindungen, `OBJECT`-/`FUNC`-Typen und Relocations sind ELF-Metadaten, kein vollständiger API-Vertrag und kein Beleg tatsächlicher Laufzeitnutzung. Es gab keine Runtime-, Geräte-, Netzwerk- oder VM-Prüfung.

Self-Review: Imageidentität, Partitionsidentität, Inventarzähler, Trefferoffsets, Trefferdatei-Hashes und ELF-Ausgaben wurden durch den vollständigen deterministischen Wiederholungslauf validiert. Kein unabhängiger Review oder Worker-Lauf wird behauptet.

## Erzeugte Dateien

- `scan.py` — vollständiger Image-/Partition-2-Scanner, Trefferextraktion und ELF-Metadaten
- `validate.py` — Identitäts- und vollständiger Re-Scan-Validator
- `inventory.csv` — alle 3.058 regulären Partitionsdateien: Pfad, Inode, Modus, Größe
- `string_hits.csv` — exakter Name und jeder Byteoffset
- `hit_files.csv` — neun Trefferdateien mit Größe, SHA-256 und Extraktionspfad
- `hit_files/` — ausschließlich die neun extrahierten Trefferdateien
- `elf_headers.csv` — ELF-Klassifikation und Dateidentität je Trefferdatei
- `elf_findings.csv` — exakte Symbol- und Relocationzeilen mit Dynsym-Bindung/Definition
- `elf_metadata.txt` — passende Standard-`readelf`-Ausgabe je ELF-Treffer
- `scan_summary.json` — Image-/Partitionsbindung und Zähler
- `report.md` — Befunde, Scope, Grenzen und Audit
- `SHA256SUMS` — SHA-256 aller persistenten Dateien außer `SHA256SUMS` selbst

SHA-256 der Scanner-, Validator- und Ergebnistabellen:

| Datei | SHA-256 |
|---|---|
| `scan.py` | `a7a955f3917fdb358020ee553c0a3246072ca6b0ac8716ccda41e59991d0abfb` |
| `validate.py` | `df4c1e1e126c2448cf87ecc46356abd292438fdd9dc841c4d732c3529a213751` |
| `inventory.csv` | `d2e0921893cde71275e9e0748fb3e012ee70ec457cc19dcd86a11c0864e3b1f4` |
| `string_hits.csv` | `b4d0d2df7230aeb8005f94f5d7aeaceddbd99582de6746a9acb30a9ea2cbb358` |
| `hit_files.csv` | `64633aafcfbdfd2af85f9d8c2c564ddb6e7b9ab2d28005d88f38d58d9e885654` |
| `elf_headers.csv` | `32d64b6bb0ff4132077c330df6f1ea2b08396a47bef3a72d4f9712333af61f64` |
| `elf_findings.csv` | `43de6fb26d5335e0189cca0b9f71f397b7d2740d111971568b5623d8e8214a88` |
| `elf_metadata.txt` | `0b8a7c8ad56ee52772adc11a572532f953f954cc35c16bcc20092e759d61eb85` |
| `scan_summary.json` | `0182bf7e008915a337dcdbfc2a35296d7d045e713ffea6f35714fbc9717c1f44` |

Die Größen und SHA-256 aller neun extrahierten Dateien stehen in `hit_files.csv`; Hashes dieses Berichts, der extrahierten Dateien und übrigen persistenten Artefakte sind in `SHA256SUMS` enthalten.
