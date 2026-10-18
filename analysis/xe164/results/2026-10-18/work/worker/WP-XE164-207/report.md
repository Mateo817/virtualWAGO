> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-207 — Symlink- und Dynsym-Abgleich

## Befund

**VERIFIZIERT — installierter statischer Pfad:** Die hashgebundene WP201-Tabelle enthält exakt die Symlinkzeile `/usr/lib/libdal.so`, Inode `1601`, Symlinkgröße `15`, Zieltext `libdal.so.1.0.1`. Relativ zum Verzeichnis `/usr/lib` normalisiert sich das Ziel exakt zu `/usr/lib/libdal.so.1.0.1`. Die gleichnamige reguläre Datei ist in WP201s vollständigem Partition-2-Census als `DEF` für `adi_GetApplicationInterface` erfasst; WP202 bindet den extrahierten Inhalt dieses Pfades an Größe 18.076 Bytes und SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`.

**VERIFIZIERT — Kandidatenzahl im vollständigen WP201-Census:** Die vollständige Dynsym-Tabelle enthält genau drei Zeilen für `adi_GetApplicationInterface`: eine `DEF` in `/usr/lib/libdal.so.1.0.1`, zwei `UND` in `/usr/lib/libIoDrvDal.so.1.0.2` und `/usr/sbin/dalshell`, sowie null `ABS` und null `OTHER`. Damit gibt es in diesem Census keinen zweiten definierten Dynsym-Kandidaten. Der benannte Kandidat ist ein statischer Installationsbefund, keine beobachtete Runtime-Auswahl.

## Beobachtung, Schlussfolgerung, Alternative und Restunsicherheit

- **Beobachtung — VERIFIZIERT:** Die Symlinkzeile und normalisierte Partition-2-Zielzeichenfolge passen exakt zu dem Pfad der einzigen `DEF`-Zeile. Die 3.058-Datei-/803-ELF-Population und Zähler `DEF=1`, `UND=2`, `ABS=0`, `OTHER=0` stimmen mit dem hashgebundenen WP201-Summary überein; WP201 meldet null Scanfehler.
- **Schlussfolgerung — VERIFIZIERT:** Der installierte Symlink `/usr/lib/libdal.so` zeigt statisch auf `/usr/lib/libdal.so.1.0.1`. Im vollständigen WP201-Partition-2-Census existiert eine definierte Dynsym-Zeile für den exakten Namen und keine zweite Definition.
- **Alternativerklärung:** Ein Loader könnte zur Laufzeit einen anderen Objektpfad wählen oder eine Definition interponieren; ein Prozess könnte den Symlink umgehen oder andere Objekte außerhalb dieses Census einbeziehen. Die statische Symlinkbeziehung legt keine dieser Laufzeitbedingungen fest.
- **Restunsicherheit — OFFEN:** Konkrete Ladeobjekte, Lookup-Reihenfolge, Interposition und tatsächliche Bindung wurden nicht beobachtet. Der Census deckt nur reguläre Dateien und ELF-Dynsym der angegebenen Partition 2 des exakten Images ab. Laufzeit und Hardware: **NOT_RUN**.

## REA-Kontext und Methode

Der WP201-Ordner enthält kein REA-Evidence-Bundle für diesen Census. Der vorhandene WP201-Report bindet den Census jedoch an das exakte Image und berichtet, dass eine frühere REA-Dateisystemtraversierung wegen des fehlenden Binwalk-Providers nicht verfügbar war; die Evidenz beruht auf dem dokumentierten `debugfs`-/Python-/GNU-`readelf`-Fallback. Es wurde keine neue REA-Analyse angefordert.

Diese Arbeit ist eine eng begrenzte Versöhnung der vorgegebenen, hashgebundenen WP201-TSVs und des WP201-Summaries mit der WP202-Hashbindung der Zieldatei. Kein neuer Census, keine anderen ELF-Dateien, keine Disassembly und keine Runtime-/Hardwarehandlung.

## Eingabeidentität und Verifikation

Alle Eingaben wurden lokal gehasht und Größe sowie SHA-256 stimmten mit dem Auftrag überein:

| Eingabe | Größe | SHA-256 | Status |
|---|---:|---|---|
| FW31 Image | 287.309.824 | `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` | PASS |
| WP201 `symlinks.tsv` | 39.425 | `fb3ee24fd13c0252f0d832c5fac5e275b888bd285f86bd3f7d5562b32aa3fd07` | PASS |
| WP201 `dynsym_hits.tsv` | 486 | `38e90d1658dab9a80b9b3886b8b0e6f91edad312a55c930b4dd6132a682102ec` | PASS |
| WP201 `scan-summary.txt` | 946 | `33047e942c5c522e549f3b3f49c936757e77afb7219add61c701359edd5ab7a8` | PASS |
| WP202 `libdal.so.1.0.1` | 18.076 | `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` | PASS |

Werkzeuge dieser Reconciliation: Python 3.13.5 und GNU coreutils `sha256sum` 9.7. Eingebettete WP201-Toolversionen: `debugfs 1.47.2 (1-Jan-2025)`, GNU `readelf` aus Binutils 2.44, Python 3.13.5. Der Validator liest nur die fünf oben genannten Eingaben, verifiziert deren Hashes, die exakte Symlinkzeile samt lexikalisch normalisiertem Ziel, die drei Dynsym-Zeilen und die Summary-Zähler. Validator: **PASS**. SHA-Manifest: **PASS**.

## Status

| Aussage | Status |
|---|---|
| Installierter statischer Symlinkpfad `/usr/lib/libdal.so` → `/usr/lib/libdal.so.1.0.1` | VERIFIZIERT |
| Dynsym-Zahl im vollständigen Census: 1 DEF, 2 UND; kein zweiter DEF-Kandidat | VERIFIZIERT |
| Konkrete Laufzeitwahl und Interposition | OFFEN |
| Runtime / Hardware | NOT_RUN |

Self-review: Eingabehashes, Zeilen, Zähler, Validator und Manifest lokal geprüft. Dies ist ein Luna HIGH Workerbericht; er ist kein unabhängiger Review und kein Runtime-/Hardware-Nachweis.
