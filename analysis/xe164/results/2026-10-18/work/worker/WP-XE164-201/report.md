> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-201 — Exact name census `adi_GetApplicationInterface`

## Ergebnis

**VERIFIZIERT:** Vollständiger, read-only Census von Partition 2 im hashgebundenen FW31-SD-Image: 3.058 reguläre Dateien, 786 Symlinks, 14 sonstige Einträge und 489 besuchte Verzeichnisse. Es wurden 3.058 reguläre Datei-Inhalte byteweise geprüft und alle 803 ELF-Dateien auf `.dynsym`-Einträge für den exakten Namen `adi_GetApplicationInterface` geprüft. Traversierung, Dumps und `readelf`-Aufrufe meldeten null Fehler.

**VERIFIZIERT:** Die exakte ASCII-Bytefolge kommt in drei regulären Dateien vor. Alle drei enthalten jeweils eine exakte `.dynsym`-Zeile für den Namen: ein `DEF` und zwei `UND`. Es wurden keine `ABS`- oder sonstigen Abschnittsindizes beobachtet. Byte-Treffer und Dynsym-Einträge sind in den getrennten Tabellen aufgeführt; bloße Bytesuche und Symbolklassifikation werden damit nicht gleichgesetzt.

| Pfad | Größe | SHA-256 | `.dynsym`-Befund |
|---|---:|---|---|
| `/usr/lib/libIoDrvDal.so.1.0.2` | 25.976 | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` | `UND`, `GLOBAL`, `FUNC`, `DEFAULT` |
| `/usr/lib/libdal.so.1.0.1` | 18.076 | `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` | `DEF`, `GLOBAL`, `FUNC`, `DEFAULT`, Abschnitt 12 |
| `/usr/sbin/dalshell` | 69.588 | `e19af95c6ac36f31a1db9ac1027ac465ed04e68d7f642665187f2db7be04a725` | `UND`, `GLOBAL`, `FUNC`, `DEFAULT` |

Der `DEF`-Eintrag ist eine statische Definition im `.dynsym`-Eintrag der genannten Datei. Die beiden `UND`-Einträge sind Importe. Daraus werden keine Runtime-Auflösung, Ladefolge, Provider-Identität oder API-Semantik abgeleitet.

## Scope und abweichender Auftragspfad

Der Assignment-Pfad `sources/fw31-040901-31/rootfs/` enthält lokal nur die zwei regulären Dateien `libIoDrvDal.so.1.0.2` und `libIoDrvKbus.so.0.0.1`; er ist eine Teilauswahl, nicht die vollständige installierte Partition. Die zuerst ausgeführte Pfadprüfung fand darin nur einen Byte-Treffer und einen `UND`-Eintrag in `libIoDrvDal`. Dieser Teilbefund wurde nicht als Vollcensus ausgegeben.

Nach ausdrücklicher Autorisierung des Root-Agenten wurde die vollständige Partition 2 temporär ausschließlich unter diesem Worker-Paket aus dem exakten SD-Image rekonstruiert und mit `debugfs` read-only traversiert. Das Image hat 287.309.824 Bytes und SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c`; Partition 2 liegt bei Byteoffset 25.165.824, ist 262.144.000 Bytes groß und hat UUID `373f7dc3-cbe8-44a1-b974-a3c99d616970`. Die Partition wurde nach abgeschlossenem Census automatisch entfernt; persistiert sind nur kompakte Treffer-/Inventartabellen und Scanner/Report. Das Originalimage wurde nicht geändert.

Die gemessene Grundgesamtheit stimmt mit dem Erwartungswert 3.058 überein und unabhängig mit dem gleichen Image zugeordneten Zählern aus WP-XE164-145/WP-XE164-151. Das konkrete IoDrvDal-Objekt wurde erneut mit Größe und SHA-256 gegen die Vorgabe geprüft. Die vorhandene frühere REA-Abfrage auf diesem Image war laut WP-XE164-145 wegen fehlendem Binwalk-Provider `BLOCKED`; sie wurde nicht wiederholt. WP-XE164-151 dokumentiert die fehlende REA-Dateisystemtraversierung. Der verwendete Fallback ist daher lokale `debugfs`-Traversal plus exakte Byteprüfung und GNU `readelf` auf jedes ELF.

## Beobachtung, Alternative und Restunsicherheit

- **Beobachtung — VERIFIZIERT:** Drei der 3.058 installierten regulären Dateien enthalten den exakten ASCII-Namen; die drei gleichnamigen `.dynsym`-Zeilen bestehen aus einer Definition und zwei Importen.
- **Alternative:** Die Definition in `/usr/lib/libdal.so.1.0.1` könnte über weitere, nicht untersuchte Loader- oder Konfigurationsbedingungen verwendet werden; diese Analyse prüfte nur Installationsdateien und ELF-Dynsym.
- **Restunsicherheit — OFFEN:** Ob und wann ein Runtime-Loader die beiden `UND`-Symbole bindet, welche Definition gegebenenfalls gewählt wird und welche Funktionalität der Name bezeichnet, wurde nicht untersucht. Andere Firmwarestände und Dateien außerhalb der installierten Partition 2 liegen außerhalb des Befunds.

## Werkzeuge und Verifikation

Python 3.13.5; `debugfs 1.47.2 (1-Jan-2025)`; GNU `readelf` (GNU Binutils for Debian) 2.44; `sha256sum` (GNU coreutils) 9.7. Der reproduzierbare Lauf ist:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

| Prüfung | Status | Ergebnis |
|---|---|---|
| Image-Identität und Partition-Signatur/UUID | PASS | Größe, SHA-256, ext-Magie und UUID stimmen. |
| Verzeichnis-Traversierung | PASS | 489 Verzeichnisse, 3.058 reguläre Dateien, 786 Symlinks, 14 sonstige Einträge, null Fehler. |
| Byte-Census | PASS | 3.058 reguläre Datei-Inhalte geprüft; drei Dateien mit exakter Bytefolge. |
| ELF-Dynsym-Census | PASS | 803 ELF-Dateien geprüft; drei exakte Symbolzeilen: 1 DEF, 2 UND, 0 ABS, 0 OTHER. |
| IoDrvDal-Größe und Hash | PASS | stimmen mit der Eingabevorgabe überein. |
| Reproduzierbarer Validator | PASS | zweiter vollständiger Lauf erzeugte identische Treffer-, Symlink-, Fehler- und Summary-Dateien. |
| VM, Netzwerk, Geräte, Binärausführung | NOT_RUN | keine solchen Aktionen vorgenommen. |

## Paketdateien

| Datei | Zweck |
|---|---|
| `assignment.md` | Eingabeauftrag, unverändert |
| `report.md` | Ergebnis, Scope, Beobachtungen und Grenzen |
| `scan.py` | reproduzierbarer Image-/Partition-/Byte-/Dynsym-Census |
| `validate.py` | erneuter kompletter Lauf in temporärem Paketpfad und bytegenauer Vergleich |
| `byte_hits.tsv` | vollständige Byte-Trefferliste mit Pfad, Größe, Hash |
| `dynsym_hits.tsv` | vollständige Klassifikation der exakt passenden Dynsym-Zeilen |
| `symlinks.tsv` | inventarisierte Symlinkpfade und Ziele |
| `scan_errors.tsv` | Laufzeitfehlerliste, leer außer Kopfzeile |
| `scan-summary.txt` | Identitäten, Populationszähler und Toolversionen |
| `SHA256SUMS` | Prüfsummen der übrigen Paketdateien |

Self-Review: Eingabeidentität, Zähler, Treffer und Scannerverhalten selbst geprüft. Kein unabhängiger Review wird behauptet.
