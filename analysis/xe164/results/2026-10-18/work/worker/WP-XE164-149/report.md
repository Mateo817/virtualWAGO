> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-149 — FW31 `[IoDrvDal.8]` / DALI name consistency

## Ergebnis

**OFFEN — Die Evidenz belegt den Datensatz als intern kohärenten DALI-spezifischen Konfigurationseintrag, aber nicht, dass er zweifelsfrei ein eigenständiger, beabsichtigter Treiber und weder Alias noch Tippfehler ist.**

**VERIFIZIERT:** Der exakt hashgebundene Abschnitt `[IoDrvDal.8]` enthält sechs lexikalisch zusammenpassende DALI-Bezeichner: `DalName="libdali"`, `ConfigLibrary="libIoDrvDali"`, `DeviceName="WAGO_SRC_DALI"`, `DriverName="Wago SRC Dali IO Driver"`, `EntryFunction="IoDrvDali_Init"` und `Name="Dali IO"`. Die unmittelbar folgende Zeile `[IoDrvDal.9]` ist nur als Abschnittsgrenze aufgenommen. `ModuleType` und andere Werte sind nicht semantisch gedeutet.

**VERIFIZIERT im Inventarscope:** Der vollständige read-only Durchlauf durch alle 489 Verzeichnisse und 3.858 Einträge der ext-Partition 2 fand weder einen Pfad-Basename passend zu `libIoDrvDali*` oder `libdali*` noch ein Symlinkziel mit einem solchen Basename. Folglich gab es unter diesen Kandidaten keine DSO, deren Dynsym-Metadaten `IoDrvDali_Init` hätten belegen können. Die leeren Kandidatentabellen sind mit Kopfzeile gespeichert; sie bedeuten null Treffer im dokumentierten Suchmuster, nicht null DALI-Implementierungen im gesamten Image unter beliebigen anderen Namen.

## Beobachtungen, Schluss und unbekannt

| Kategorie | Aussage | Status |
|---|---|---|
| Beobachtung | Die sechs ausgewählten Felder desselben Datensatzes verwenden konsistente DALI-Schreibweisen; nur die Abschnitts-ID lautet `IoDrvDal.8`. | VERIFIZIERT |
| Beobachtung | Die vollständige Partition 2 enthält keine Pfad- oder Symlinkzielkandidaten `libIoDrvDali*` / `libdali*`; daher gibt es aus diesem Suchraum kein Kandidaten-DSO und keine passende Dynsym-Zeile. | VERIFIZIERT |
| Schluss | Der Datensatz ist ein eigenständiger DALI-spezifischer *Konfigurationseintrag* und lässt sich lexikalisch von der ähnlich benannten `libIoDrvDal`-Bibliothek unterscheiden. | HYPOTHESE |
| Schluss | Dass der Eintrag absichtlich ein eigenständiger Treiber ist und kein Alias, Tippfehler, veralteter Datensatz oder nicht mehr ausgeliefertes Modul bezeichnet, ist mit diesen Belegen nicht bewiesen. | OFFEN |
| Unbekannt | Ob ein Alias an anderer Stelle, ein anderer Bibliotheksname, ein Paket außerhalb dieser Partition, ein dynamisch erzeugtes Objekt oder Laufzeit-Loaderverhalten die Bezeichner auflöst. | OFFEN |

Alternative Erklärung: Der Konfigurationsblock könnte ein absichtlich erhaltener oder veralteter Eintrag für eine DALI-Komponente sein, deren Datei im Image fehlt oder anders heißt; ebenso könnte `libIoDrvDali` ein Alias-/Tippfehlerziel sein. Ein zusammenpassender Textdatensatz unterscheidet diese Möglichkeiten nicht. Es wurde keine Loadersemantik untersucht.

## Gebundene Eingaben und Methode

| Eingabe | Größe | SHA-256 | Verwendung |
|---|---:|---|---|
| FW31 `PFC-G2-Linux_sd_V040901_31_r9d0900aaed.img` | 287.309.824 Bytes | `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` | vollständige Imageidentität; Partition 2 vollständig inventarisiert |
| `IoDrvDal.cfg` (WP145-retained, `/etc/codesys3.d/IoDrvDal.cfg`) | 2.389 Bytes | `91fc4013c5bd87fab459f13bba60787e9f1256d4423cfd47eefdef307161af13` | exakte Abschnitts-/Datensatzquelle |
| WP145 `partition_inventory.csv` | 239.212 Bytes | `16badcbae1785928eb38afbc9329c4dfb75743c979b95dbf6b4706519d90d23e` | Identitäts-/Methodenkontext; Kandidatenbefund in diesem Paket erneut reproduziert |
| WP145 `report.md` | 9.374 Bytes | `898935f0f69c2cbcb08d9f7497c05c77becfe01a54031e10ca846d10932174fd` | dokumentiert den read-only `debugfs`-Fallback und die Partitiongrenzen |

Die FW31-Imagepartition 2 beginnt bei Byteoffset 25.165.824 (`0x01800000`) und ist 262.144.000 Bytes groß. Der Worker prüft Imagegröße/Hash, extrahiert die Partition temporär, validiert ext-Magie und UUID `373f7dc3-cbe8-44a1-b974-a3c99d616970`, traversiert Verzeichnisse mit `debugfs` und liest Symlinkziele über `debugfs stat`. Er filtert Pfad-Basenamen und Symlinkziel-Basenamen anhand der exakten Muster `libIoDrvDali*` und `libdali*`. Nur bei passenden regulären `.so`-Dateien würde er die Datei extrahieren und `readelf --dyn-syms --wide` ausführen; bei null Kandidaten wurde `readelf` auf kein Firmware-DSO angewandt. Der vollständige `IoDrvDal.cfg`-Inhalt wurde nicht erneut ausgelesen: Die beibehaltene Datei ist vor Verwendung größen- und hashgeprüft.

REA wurde zuerst genau einmal auf dem vollständigen, exakten Imagepfad mit `inspect_firmware_regions` aufgerufen. **BLOCKED:** REA meldete `capability_unavailable` / `unsupported_provider`, da kein absoluter caller-supplied `REA_BINWALK_COMMAND` gesetzt war. Der Fehler wurde nicht wiederholt. Ein REA-Bundle ist daher nicht verfügbar. Anschließend wurde ausschließlich der in WP145 dokumentierte read-only `debugfs`-Pfad reproduziert und auf die benannten Kandidaten fokussiert.

Werkzeuge: Python 3.13.5; `debugfs` 1.47.2 (1-Jan-2025), ext2fs library 1.47.2; GNU `readelf` / Binutils 2.44. Kein Binary wurde ausgeführt. Keine Funktionskörper, Disassemblierung, Aufrufgraphen, Laufzeit-Loadersemantik, VM, Netzwerk, Gerät oder Hardware wurden untersucht.

## Reproduktion und Selbstprüfung

Im Paketverzeichnis:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`scan.py` verifiziert gepinnte Image- und Config-Identitäten und inventarisiert Partition 2 vollständig; `validate.py` wiederholt den kompletten read-only Scan in einem temporären Verzeichnis und vergleicht die gespeicherten Ergebnisdateien bytegenau. Ergebnis: **PASS**, keine Traversierungs-, Parse-, Lese- oder `readelf`-Fehler; null Pfad-/Symlinkzielkandidaten, null Kandidaten-DSOs und null Kandidaten-Dynsymzeilen. Dies ist eine Selbstprüfung, kein unabhängiger Review oder Worker-Lauf.

`REA_RESULT.txt` hält den einzelnen REA-Fehler fest. Es gibt kein REA-Bundle. Die Kandidatensuche ist auf Namen im genannten Muster und Partition 2 begrenzt; sie beweist nicht, dass die Firmware keine DALI-Funktion unter einem anderslautenden Pfad oder eingebetteten Objekt enthält.
