> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-151 — FW31 custom-component Symlink-/Dynsym-Matrix

## Ergebnis

**VERIFIZIERT:** Die begrenzte Population umfasst genau 40 Symlink-Einträge direkt unter `/usr/lib/cds3-custom-components` in Partition 2 des identitätsgeprüften FW31-Images. Der Validator weist eine Eins-zu-eins-Abdeckung aller 40 Einträge nach. Jeder Link löst nach Normalisierung innerhalb des Partition-Dateisystems auf eine reguläre ELF-Datei auf; die 40 Endpfade und SHA-256-Hashes sind paarweise verschieden. Alle 40 Dateien sind ELF32-DSOs. Die vollständige Pfad-, Linkziel-, Auflösungsketten-, Größe-, Hash- und Dynsym-Matrix steht in `symlink_dso_dynsym_matrix.csv`.

**VERIFIZIERT:** Jedes der 40 aufgelösten DSO-Objekte hat in `readelf --dyn-syms --wide` genau eine Zeile, deren Dynsym-Name exakt `ComponentEntry` ist. Die CSV-Matrix enthält für jede Linkzeile diese vollständige rohe Symbolzeile; `readelf_dynsym_raw.txt` enthält die Dynsym-Zeilen je finalem DSO zusammen mit Zielpfad und DSO-SHA-256. Damit ist jeder Symbolbefund an die aufgelöste Datei und deren Hash gebunden. Diese Beobachtung belegt weder den Inhalt noch den vollständigen Funktionsvertrag des Symbols.

**VERIFIZIERT:** `/usr/lib/cds3-custom-components/libIoDrvDal.so` folgt der Kette

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Das finale DSO ist 25.976 Bytes groß, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. Seine exakte Dynsym-Zeile lautet:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Im abgegrenzten Verzeichnisbestand ist `libIoDrvDal.so` damit ein Mitglied der allgemeinen 40-von-40-Konvention: auch die übrigen finalen DSO-Dateien exportieren im ELF-Dynsym genau einen Eintrag dieses Namens. Die `libIoDrvDal`-Kette hat zwei aufeinanderfolgende Symlinks bis zur regulären DSO-Datei. Weitere Link- und Zielstufen, Größen, Hashes und Symbolzeilen sind in der Matrix ausgewiesen.

## Beobachtungen, Alternativerklärungen und Grenzen

| Kategorie | Aussage | Status |
|---|---|---|
| Beobachtung | Alle 40 direkten Symlinks lösen innerhalb der geprüften Partition auf reguläre ELF32-Dateien auf; alle Endpfade und DSO-Hashes sind verschieden. | VERIFIZIERT |
| Beobachtung | 40 von 40 finalen DSOs enthalten jeweils genau eine exakte `.dynsym`-Zeile namens `ComponentEntry`. | VERIFIZIERT |
| Einordnung | Der `libIoDrvDal.so`-Link gehört ohne erkennbaren Symbolnamen-Ausreißer in diese abgegrenzte Verzeichnispopulation. | VERIFIZIERT, nur statisch |
| Alternative | Ein exportierter Dynsym-Name kann allein weder einen vollständigen Aufrufvertrag noch Runtime-Registrierung oder Loaderverhalten beweisen. | OFFEN außerhalb des Prüfumfangs |
| Unbekannt | Ob, wann oder in welcher Reihenfolge ein Runtime-Loader die DSOs lädt und `ComponentEntry` aufruft. | OFFEN |

Der Negativ- und Vollständigkeitsbereich endet an den direkten Symlink-Einträgen in genau diesem Verzeichnis und Partition 2. Nicht-Symlinks im Verzeichnis, Unterverzeichnisse, andere Firmwarestände sowie Laufzeit- oder Hardwareverhalten sind keine Aussage dieses Pakets. Es wurden keine Funktionskörper dekompiliert oder untersucht. Dateinamen dienen hier nur der Pfadidentifikation, nicht als Beleg eines Funktionsvertrags.

## Eingabeidentität und Methode

| Eingabe | Größe | SHA-256 | Befund |
|---|---:|---|---|
| FW31-Image `PFC-G2-Linux_sd_V040901_31_r9d0900aaed.img` | 287.309.824 | `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` | VERIFIZIERT |
| Partition-Inventar aus WP-XE164-145 | 239.212 | `16badcbae1785928eb38afbc9329c4dfb75743c979b95dbf6b4706519d90d23e` | VERIFIZIERT |
| `symlinks.csv` aus WP-XE164-145 | 487.667 | `43e1890ac6d58932bc7f9cabc2069b6cbaeb1bdb75f5ddde61df4e0d3a617a15` | VERIFIZIERT |
| `report.md` aus WP-XE164-145 | 9.374 | `898935f0f69c2cbcb08d9f7497c05c77becfe01a54031e10ca846d10932174fd` | VERIFIZIERT |

Der Auftrag nannte den Pfad `partition2_inventory.csv`; unter WP-XE164-145 existiert stattdessen `partition_inventory.csv`. Der vorhandene Pfad hat die angegebene Größe und exakt den vorgegebenen SHA-256. Dies ist eine Metadaten-/Pfadkorrektur; eine Eingabeartefakt-Abweichung wurde nicht festgestellt.

Die im WP-XE164-145-Bericht bereits festgehaltene REA-Abfrage auf dasselbe Image wurde nicht wiederholt. Die hier relevante REA-Abdeckung bietet keine Dateisystem-Traversierung für die verlangte vollständige Symlinkauflösung und ELF-Dynsym-Matrix; die genaue einmalige Provider-Lücke und der anschließende Fallback stehen in `summary.json`. Fallback: Partition 2 aus dem unveränderten Image in ein temporäres Paket-Unterverzeichnis ausschneiden, Ext-Magie prüfen, Einträge aus den hashgebundenen WP145-Inventaren lesen, Zielinodes mittels `/sbin/debugfs` `dump` ausgeben und alle Enddateien mit `readelf` als ELF sowie im Dynamic-Symboltisch prüfen. Ziel-Inodes, Pfadketten, Roh-Linkbelege und Roh-Dynsym-Ausgabe werden durch Matrix und Belegdateien zusammengehalten. Das Originalimage wurde nicht verändert.

Werkzeuge: Python 3.13.5; `debugfs 1.47.2 (1-Jan-2025)`; GNU `readelf` (GNU Binutils for Debian) 2.44; `sha256sum` (GNU coreutils) 9.7. Die konkreten Aufrufe und Eingabepfade sind in `extract_matrix.py` festgehalten.

## Prüfung

`validate.py` gleicht die direkten Symlink-Pfade vollständig mit `symlinks.csv` ab, löst jedes Ziel anhand des partitionweiten Inventars rekursiv auf, prüft regulären Zieltyp, Inode und Größe, hasht jedes extrahierte DSO erneut und gleicht die exakten `readelf`-Dynsym-Zeilen ab. Es bindet zusätzlich den `libIoDrvDal`-Endpfad, Hash und Symbolnamen. Ergebnis: **PASS**, protokolliert in `validator_result.txt`.

Status: Validator **PASS**. `sha256sum -c SHA256SUMS`: **PASS** nach Erzeugung des Manifests. Self-Review dieses Workers; kein unabhängiger Review, kein Runtime- oder Hardwarelauf.

## Paketdateien

- `report.md` — Ergebnisse, Umfang, Methoden, Grenzen und Status
- `symlink_dso_dynsym_matrix.csv` — vollständige Eins-zu-eins-Matrix aller direkten Symlinks
- `dso_population_summary.csv` — eindeutige finale DSO-Population und Linkanzahl pro Hash
- `readelf_dynsym_raw.txt` — Dynsym-Rohzeilen je finalem Pfad und SHA-256
- `debugfs_stat_raw.txt` — debugfs-Inodebelege für finale DSO-Dateien und zugehörige Links
- `dsos/` — aus Partition 2 ausgegebene DSO-Dateien, nach SHA-256 benannt
- `extract_matrix.py` — reproduzierbare Extraktion und Matrixerzeugung
- `validate.py`, `validator_result.txt` — Validator und PASS-Protokoll
- `summary.json` — Zähler, Eingabepfade, Toolversionen und einmalige REA-Lücke
- `SHA256SUMS` — SHA-256 aller übrigen persistenten Paketdateien
