> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-145 — FW31 `libIoDrvDal` / `ComponentEntry` name binding

## Ergebnis

**VERIFIZIERT:** Partition 2 des hashgebundenen FW31-Images enthält 3.058 reguläre Dateien, 786 Symlinks und 14 sonstige Einträge. Der vollständige read-only Scan umfasste 489 Verzeichnisse ohne Traversierungs-, Parse-, Lese- oder Größenfehler. Die vollständigen Inventar-, Namen-, Symlink- und Trefferdateitabellen liegen in den CSV-Dateien dieses Pakets.

**VERIFIZIERT:** `/usr/lib/libIoDrvDal.so.1.0.2` ist 25.976 Bytes groß und hat SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`, identisch mit der separat bereitgestellten DSO. Seine `.dynsym` enthält genau den hier gesuchten Eintrag `ComponentEntry`: Symbolindex 24, ELF-Wert `0x4448`, Größe 560, Typ `FUNC`, Bindung `GLOBAL`, Sichtbarkeit `DEFAULT`, Abschnittsindex 12. Der Wert ist ein ELF-Symbolwert, kein Datei-Offset. Vollständige Zeile: `dynsym.csv` und `dynsym_matching.txt`.

**VERIFIZIERT:** Die Symlinkkette im Image ist:

| Pfad im Image | Typ und Ziel | nächste Stufe |
|---|---|---|
| `/usr/lib/cds3-custom-components/libIoDrvDal.so` | Symlink → `../libIoDrvDal.so` | `/usr/lib/libIoDrvDal.so` |
| `/usr/lib/libIoDrvDal.so` | Symlink → `libIoDrvDal.so.1.0.2` | `/usr/lib/libIoDrvDal.so.1.0.2` |
| `/usr/lib/libIoDrvDal.so.1` | Symlink → `libIoDrvDal.so.1.0.2` | `/usr/lib/libIoDrvDal.so.1.0.2` |
| `/usr/lib/libIoDrvDal.so.1.0.2` | reguläre Datei, 25.976 Bytes | Ziel-DSO |

Die Zielpfade stammen aus `debugfs stat` für die jeweiligen Symlink-Inodes; `symlinks.csv` enthält den vollständigen Symlinkbestand der Partition 2 mit Inode, Modus, Größe und Rohbeleg.

**VERIFIZIERT:** Das Paketmanifest `/usr/share/opkg/info/cds3-iodrvdal.list` (358 Bytes, SHA-256 `7b80f47425982fbfa9508bef420498ca4dbb370a00a4385074096287d21e2440`) listet in Zeilen 2, 3, 7 und 10 die drei Symlinks und die reguläre DSO. Diese vier vollständigen Zeilen stehen in `config_records.csv`.

**VERIFIZIERT:** Die Konfigurationsdatei `/etc/codesys3.d/IoDrvDal.cfg` ist 2.389 Bytes groß, SHA-256 `91fc4013c5bd87fab459f13bba60787e9f1256d4423cfd47eefdef307161af13`. Zeile 92 lautet `ConfigLibrary="libIoDrvDali"`. Das ist eine nahe Schreibweise, aber kein exakter Treffer für `libIoDrvDal`; der letzte Buchstabe `i` schließt einen Token-Treffer aus. Der Dateiname und diese Zeile belegen daher keine exakte Konfiguration des Bibliotheksnamens `libIoDrvDal`. Die Zeile ist separat in `config_near_misses.csv` festgehalten.

**VERIFIZIERT:** Der partitionweite ASCII-Scan berücksichtigte exakte, tokenbegrenzte Namen unabhängig von ASCII-Groß-/Kleinschreibung: `libIoDrvDal`, `libIoDrvDal.so` einschließlich versionssuffixierter Schreibweisen sowie `ComponentEntry`. Es gibt 60 Bytevorkommen in 49 regulären Dateien. `name_hits.csv` nennt für jedes Vorkommen Pfad, tatsächlich gespeicherte Schreibung, Datei-Offset dezimal/hex, Dateigröße und SHA-256. `hit_files.csv` bindet jede Trefferdatei an Pfad, Größe, Hash und Trefferanzahl. `path_hits.csv` erfasst passende Partitionspfade und Symlinkziele. `config_records.csv` enthält alle matching unmittelbar umgebenden druckbaren Textzeilen aus dem Partitionsscan; `config_near_misses.csv` enthält die nicht passende, aber relevante `ConfigLibrary`-Zeile. Es wurde keine Konfiguration gefunden, deren einzelner Datensatz sowohl einen exakten Modul-/Bibliotheksnamen als auch den Namen `ComponentEntry` enthält.

**VERIFIZIERT — Schlussfolgerung im statischen Scope:** Es gibt keine statische Modulname-zu-Entry-Paarung in einem einzelnen Konfigurations- oder Manifestdatensatz. Die DSO selbst enthält den Dynsym-Namen `ComponentEntry`, während Dateiname und Symlinks `libIoDrvDal` benennen; das ist eine Paarung durch gemeinsames Artefakt-/Pfadumfeld, nicht durch denselben ELF-Symbol- oder Konfigurationsdatensatz. Die ähnlich geschriebene `ConfigLibrary`-Zeile ist `libIoDrvDali` und bildet keine exakte Paarung.

## Beobachtungen, Schluss und unbekannt

| Kategorie | Aussage | Status |
|---|---|---|
| Beobachtung | Die Partition enthält die oben dokumentierte Symlinkkette und das DSO mit passender Größe und Hash. | VERIFIZIERT |
| Beobachtung | Die `.dynsym` des DSO hat einen globalen Funktionssymbol-Eintrag `ComponentEntry` mit Wert `0x4448` und Größe 560. | VERIFIZIERT |
| Beobachtung | Konfigurationsdatei, Paketmanifest, ELF-Treffer und Pfadtreffer sind in den Tabellen mit Dateiidentitäten gebunden. | VERIFIZIERT |
| Schluss | Es wurde keine einzelne statische Konfigurations- oder Manifestzeile mit exaktem Modulnamen und `ComponentEntry` gefunden. | VERIFIZIERT im beschriebenen Scan-Scope |
| Unbekannt | Ob/wie ein Loader den DSO-Namen und `ComponentEntry` zur Laufzeit bindet oder aufruft. | OFFEN |
| Unbekannt | Ob `libIoDrvDali` in der Konfiguration ein eigenständiger, absichtlich anderer Bibliotheksname, ein Tippfehler oder ein Alias sein soll. | OFFEN |

Alternative Erklärung: ein Loader könnte Modulname und Entry-Symbol aus getrennten statischen ELF-/Konfigurationsfeldern kombinieren; der hier geforderte Einzelrecord-Nachweis würde das nicht erfassen. Ein bloßer String oder gemeinsamer DSO-Pfad beweist keine Laufzeitbindung.

## Identität, Methode und Grenze

| Eingabe | Größe | SHA-256 | Befund |
|---|---:|---|---|
| FW31 Image `PFC-G2-Linux_sd_V040901_31_r9d0900aaed.img` | 287.309.824 | `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` | VERIFIZIERT, vor Scan erneut gemessen |
| Partition 2 | Offset 25.165.824 (`0x01800000`), Länge 262.144.000 Bytes | — | VERIFIZIERT, ext UUID `373f7dc3-cbe8-44a1-b974-a3c99d616970`, ext-Magie `0xEF53` |
| `libIoDrvDal.so.1.0.2` aus dem Image | 25.976 | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` | VERIFIZIERT, gleich der genannten DSO-Eingabe |
| Codesys3-Hitdatei aus WP-XE164-112 | 5.181.396 | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | VERIFIZIERT, Identitätskontext erneut gemessen |
| WP-XE164-112 `report.md` | 5.134 | `af887649aee9bdd435f5e5fe41e395edecb07501340fb12d5bdde2191ee44051` | VERIFIZIERT, Hash vor Verwendung erneut gemessen |

Die begrenzte bereitgestellte `sources/.../rootfs`-Auswahl diente nur zur erneuten Identitätsprüfung des exakten DSO-Artefakts. Die vollständige Inventur und alle Trefferbefunde stammen aus Partition 2 des Images, nicht aus dieser Teilauswahl. Der WP-XE164-112-Bericht liefert einen bereits akzeptierten Inventarkontext; dessen Zähler wurden durch den vorliegenden vollständigen Lauf unabhängig reproduziert.

REA wurde zuerst mit `inspect_firmware_regions` auf dem exakten Image aufgerufen. **BLOCKED:** REA meldete einmal `capability_unavailable` / `unsupported_provider`, weil kein absoluter `REA_BINWALK_COMMAND`-Pfad zu einem caller-supplied Binwalk vorhanden ist. Diese Einschränkung wurde nicht durch Wiederholungen untersucht. Es gibt daher kein REA-Bundle. Danach erfolgte der im Auftrag vorgesehene Offline-Fallback: Image-Partition 2 in temporäre Datei ausschneiden, ext-Magie/UUID prüfen, mit `debugfs 1.47.2` Verzeichnisse und Inodes read-only traversieren und reguläre Dateien inodebasiert in ein temporäres Verzeichnis dumpen. Nur die DSO und die konkrete Konfigurationsdatei wurden als Rohdateien dauerhaft in diesem Worker-Paket behalten. ELF-Metadaten kamen aus GNU `readelf` / Binutils 2.44. Laufumgebung: Python 3.13.5.

Kein Binary wurde ausgeführt. Es wurden keine Funktionskörper, Deassemblierung, Aufrufgraphen oder Laufzeit-Loadersemantik untersucht. Es gab keine VM-, Netzwerk-, Geräte- oder Hardwareaktion. Die DSO-Symbolzeile belegt nur Dynsym-Metadaten und keinen Aufrufvertrag.

## Reproduktion und Selbstprüfung

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`scan.py` prüft die Image-Identität und Partition, traversiert Partition 2 vollständig und erzeugt sämtliche Tabellen neu. `validate.py` prüft die Identitäten von Image-Nachweisen, DSO und WP-XE164-112-Kontext, führt einen kompletten zweiten Scan in einem temporären Unterverzeichnis aus und vergleicht alle gespeicherten Scannergebnisse bytegenau. Selbstprüfung: der Validatorlauf ist PASS; kein unabhängiger Review oder Workerlauf wird behauptet.

## Dateien

- `report.md` — Befunde, Identitäten, Scope, Schlussfolgerung und Unsicherheiten
- `scan.py`, `validate.py` — reproduzierbarer Scanner und vollständiger Validator
- `partition_inventory.csv` — alle regulären Dateien, Symlinks und sonstigen Partitionspfade
- `name_hits.csv`, `path_hits.csv`, `hit_files.csv` — vollständige exakte Namen-, Pfad-/Symlinkziel- und Trefferdateitabellen
- `symlinks.csv` — vollständiges Symlinkinventar mit Zieltext und `debugfs stat`-Beleg
- `config_records.csv`, `config_near_misses.csv` — matching Textdatensätze aus Manifesten sowie relevante abweichende Konfigurationszeile
- `IoDrvDal.cfg` — direkt aus Partition 2 extrahierte Konfigurationsdatei mit dem near-miss-Datensatz
- `libIoDrvDal.so.1.0.2` — direkt aus Partition 2 extrahierte und hashgeprüfte DSO
- `dynsym.csv`, `dynsym_matching.txt`, `elf_header.txt` — ausschließlich Dynsym-Treffer und ELF-Header des DSO
- `scan_summary.json` — Identitäten, Zähler, Werkzeuge und REA-Lücke
- `SHA256SUMS` — Hashmanifest aller persistenten Paketdateien außer sich selbst
