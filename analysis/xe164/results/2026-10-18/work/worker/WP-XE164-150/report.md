> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-150 — `cds3-custom-components` in FW31 Partition 2

## Ergebnis

**VERIFIZIERT:** Im exakt gebundenen FW31-Image enthält Partition 2 insgesamt 3.058 reguläre Dateien, 786 Symlinks, 14 sonstige Pfade und 489 Verzeichnisse einschließlich Root. Die vollständige reguläre Dateiinventur und Bytesuche lief ohne Traversierungs-, Parse-, Lese- oder Größenfehler.

**VERIFIZIERT:** Der exakte ASCII-Text `cds3-custom-components` kommt in 39 regulären Dateien vor. Es gibt 79 Vorkommen des Basistexts und 79 Vorkommen des vollen Pfads `/usr/lib/cds3-custom-components`; der volle Pfad enthält den Basistext, weshalb beide Suchmuster an denselben Stellen ausgewiesen werden. Alle 158 einzelnen Pattern-Treffer sind in `occurrences.csv` mit Pfad, Dateigröße, SHA-256, Datei-Offset und begrenztem druckbarem Kontext aufgeführt. `case_variants.csv` ist leer: keine anders geschriebene ASCII-Variante wurde gefunden. 40 Symlinks befinden sich unter `/usr/lib/cds3-custom-components/`; alle sind mit Zieltext und `debugfs stat`-Ausgabe in `symlinks.csv` erfasst.

**VERIFIZIERT:** Der einzige Treffer unter den eigentlichen Runtime-/Startup-/Konfigurationsartefakten ist `/usr/bin/codesys3` (5.181.396 Bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`). Im ELF-Stringbereich bei Offset `0x39fe4c` steht wörtlich:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Die vier Bytes bei `0x39fe30–0x39fe33` sind NUL; `Components.Directory` beginnt exakt bei `0x39fe34`. Vier weitere NUL-Bytes folgen dem Schlüssel; der volle Pfad beginnt bei `0x39fe4c`. `key_evidence.csv` zeichnet diese Bytebereiche separat auf; `occurrences.csv` enthält beide exakten Pfadpattern-Treffer mit dem umgebenden Rohkontext. Das ist eine Folge von ELF-Strings. Im untersuchten Datensatz steht weder eine textuelle Zuweisung wie `Components.Directory=/usr/lib/cds3-custom-components` noch eine Kommandozeilenoption, ein Serviceparameter oder ein Konfigurationsdatensatz, der den Pfad an `codesys3` oder einen Komponentenloader übergibt. **Aus dieser Stringfolge allein folgt kein Loaderverhalten.**

**VERIFIZIERT:** Die übrigen 38 Trefferdateien sind `/usr/share/opkg/info/*.list`-Dateien, darunter `codesys3.list` sowie Komponentenpaketlisten. Diese Installationslisten enthalten Pfade, Dateimodi und Symlinkziele unter dem Komponentenverzeichnis. Sie dokumentieren Paketdateiinhalte/-pfade, keine Startup-Übergabe. Die vollständige Dateiidentitätstabelle steht in `hit_files.csv`; sämtliche 39 getroffenen regulären Dateien liegen unverändert unter `hit_files/` in ihrem Partitionspfad.

## Vollständige Tabellen und Bestandsdateien

| Datei | Vollständiger Inhalt |
|---|---|
| `partition_inventory.csv` | Alle nicht-root Verzeichnisse und Partitionseinträge mit Pfad, Inode, Modus, Typ und Größe; 4.346 Pfade, Root als Traversierungsstart separat gezählt. |
| `symlinks.csv` | Alle 786 Symlinks einschließlich Pfad, Inode, Modus, Größe, gespeichertes Ziel und `debugfs stat`-Beleg. |
| `path_hits.csv` | Jeder Pfad- und Symlinkzieltreffer für beide Suchmuster; die 40 Symlinkpfade des Komponentenverzeichnisses sind enthalten. |
| `hit_files.csv` | Alle 39 regulären Trefferdateien mit Partitionspfad, Größe, SHA-256 und Pattern-Trefferanzahl. |
| `key_evidence.csv` | Rohbyte-Beleg für `Components.Directory` in `/usr/bin/codesys3`, einschließlich exaktem Schlüssel-/Pfadoffset sowie den vier NUL-Bytes davor und dazwischen. |
| `occurrences.csv` | Alle 158 exakten Bytesuchen: je Treffer Suchmuster und tatsächlich gespeicherte ASCII-Schreibung, dezimaler/hexadezimaler Offset, Dateigröße, SHA-256, begrenztes druckbares Umfeld und vorsichtige Kontextklasse. |
| `case_variants.csv` | Anders geschriebene ASCII-Varianten; leer außer Kopfzeile. |
| `hit_files/` | Byteidentische Kopien aller 39 regulären Trefferdateien in ihrer vollständigen Partitionspfadstruktur. |

## Beobachtung, Schlussfolgerung, Unbekanntes

| Kategorie | Aussage | Status |
|---|---|---|
| Beobachtung | Partition 2 enthält `/usr/lib/cds3-custom-components` und darunter 40 Symlinks. Deren Ziele sind relative Pfade in das übergeordnete `/usr/lib`-Verzeichnis, zum Beispiel `libIoDrvDal.so → ../libIoDrvDal.so`. | VERIFIZIERT |
| Beobachtung | `/usr/bin/codesys3` enthält vier NUL-Bytes bei `0x39fe30`, `Components.Directory` ab `0x39fe34`, vier NUL-Bytes danach und `/usr/lib/cds3-custom-components` ab `0x39fe4c`. | VERIFIZIERT |
| Beobachtung | Die Treffer in `/usr/share/opkg/info/*.list` listen installierte Pfade, einschließlich Symlinks im Komponentenverzeichnis. | VERIFIZIERT |
| Schlussfolgerung | Kein einzelner Startup-, Konfigurations-, Skript- oder Service-Datensatz enthält eine explizite Zuweisung oder Argumentübergabe dieses Pfads an die Runtime bzw. einen Komponentenloader. | VERIFIZIERT im vollständigen Scan von Partition 2 |
| Unbekannt | Ob `Components.Directory` im ELF-Code zur Laufzeit als Schlüssel mit dem folgenden Pfad als Wert verwendet wird, ob Konfiguration den Wert überschreibt oder ob der Pfad beim Start tatsächlich gelesen wird. | OFFEN |
| Unbekannt | Ob der Komponentenloader die 40 Symlinks scannt, einzelne Namen direkt lädt oder das Verzeichnis anderweitig nutzt. | OFFEN |

Keine Deassemblierung, Funktionskörper, Aufrufgraphen oder Laufzeitbeobachtung wurden untersucht. Die ELF-Stringfolge ist Literal-Evidence, kein Beleg für eine vollständige Parser- oder Loadersemantik. `codesys3.list` und die Paketlisten sind keine Runtime-Konfiguration.

## Eingabe, Methode und Status

| Beleg | Wert | Status |
|---|---|---|
| Image | `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/PFC-G2-Linux_sd_V040901_31_r9d0900aaed.img`; 287.309.824 Bytes; SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` | VERIFIZIERT |
| Partition 2 | Byteoffset 25.165.824 (`49152 × 512`), Länge 262.144.000 Bytes (`512000 × 512`), ext UUID `373f7dc3-cbe8-44a1-b974-a3c99d616970` | VERIFIZIERT |
| Methode | REA zuerst am exakten Image versucht. Danach Partition 2 per read-only `debugfs` traversiert und jedes reguläre Inode vollständig ausgelesen; die Suche erfasste exakte ASCII-Treffer und Varianten getrennt. Extraktions-/Temporärdaten lagen unter diesem WP-Ordner und wurden beim Scanende entfernt. | VERIFIZIERT |
| Werkzeuge | `debugfs 1.47.2`, `Python 3.13.5`; Scanner `scan.py` | VERIFIZIERT |
| REA | Einmaliger Aufruf `inspect_firmware_regions` auf dem exakten Image: `capability_unavailable` / `unsupported_provider`; erforderlich ist ein absoluter `REA_BINWALK_COMMAND`-Pfad zu einem caller-supplied Binwalk. Keine Wiederholung. Kein REA-Bundle verfügbar. | BLOCKED |
| Scannerstatus | 489 Verzeichnisse besucht; 3.058 reguläre Dateien, 786 Symlinks, 14 sonstige Einträge; 0 Lese-/Parsefehler. | PASS |
| Validatorstatus | Vollständiger zweiter Partition-2-Scan stimmt für alle Tabellen und alle 39 retained Trefferdateien bytegenau überein; der Validator bestätigt zusätzlich die Schlüssel-/Pfadbytes und exakten Rohoffsets in `/usr/bin/codesys3`. | PASS |

Die REA-Providerlücke ist der einzige untersuchte REA-Weg; die vorgegebene Offlinealternative wurde vollständig ausgeführt. Die Zähler gelten ausschließlich für die in der Tabelle hashgebundene Image-Revision und Partition 2. Es gab keine Geräte-, VM-, Netzwerk- oder Hardwareaktion. Keine Ergebnisse außerhalb dieses Worker-Ausgabeordners wurden erzeugt.

## Reproduktion und Validierung

Im Verzeichnis dieses Pakets:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`scan.py` prüft zuerst Größe und SHA-256 des Images, Partitionsoffset/-länge, ext-Magie und UUID. Dann durchsucht es alle regulären Dateien, inventarisiert Pfade und Symlinks und behält jede Trefferdatei byteidentisch. `validate.py` prüft direkt die Rohbytes in der retained `/usr/bin/codesys3`-Datei (`0x39fe30–0x39fe33` NUL, Schlüsselstart `0x39fe34`, vier NULs nach dem Schlüssel, Pfadstart `0x39fe4c`), wiederholt den vollständigen Scan in einem temporären Unterordner und vergleicht jede Tabelle sowie jede gespeicherte Trefferdatei. Reviewstatus: Self-Review; kein unabhängiger Review oder separater Worker-Lauf wird behauptet.
