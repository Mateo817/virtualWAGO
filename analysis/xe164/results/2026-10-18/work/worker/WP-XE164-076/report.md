> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-076 — FW31 SD image library presence

## Befund

**VERIFIZIERT:** Das angegebene, hashgebundene Image enthält beide exakten regulären Dateien im Dateisystem der zweiten Partition. Beide wurden bytegetreu mit `debugfs dump` unter diesem Worker-Paket extrahiert.

| Datei | Partition / Dateisystempfad | ext-Inode, Modus | Größe | SHA-256 der extrahierten Bytes |
|---|---|---:|---:|---|
| `libIoDrvDal.so.1.0.2` | Partition 2, ext3 `/usr/lib/libIoDrvDal.so.1.0.2` | 1419, `0640` | 25,976 B | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` |
| `libIoDrvKbus.so.0.0.1` | Partition 2, ext3 `/usr/lib/libIoDrvKbus.so.0.0.1` | 1421, `0750` | 38,584 B | `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` |

Exakte Kette: Image SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` → DOS/MBR (512-Byte-Sektoren) → Partition 2, Sektoren 49,152–561,151, 512,000 Sektoren / 262,144,000 Bytes → ext3, Blockgröße 1,024 Bytes, UUID `373f7dc3-cbe8-44a1-b974-a3c99d616970` → `/usr/lib/...`. Die Partitionstabelle weist außerdem Partition 1 bei Sektor 16,384 mit 32,768 Sektoren als FAT32-LBA aus; ihr Inhalt ist für die beiden positiven Funde nicht Teil des ext3-Pfads.

Der exakte Namensscan über **alle 489 erreichbaren echten Verzeichnisse** der ext3-Partition hatte null Verzeichnisfehler und je einen Eintrag für beide Namen. Treffer waren ausschließlich `/usr/lib/libIoDrvDal.so.1.0.2` und `/usr/lib/libIoDrvKbus.so.0.0.1` im untersuchten ext3-Namensraum. Die FAT-Bootpartition wurde nicht rekursiv nach Duplikaten durchsucht; die positiven Image-Aussagen hängen davon nicht ab. Eine imageweite Aussage über weitere Kopien wird daher nicht getroffen.

## Symlinks und Paketmetadaten

Die aus ext3 gelesenen Symlink-Inhalte lauten:

- `/usr/lib/libIoDrvDal.so` → `libIoDrvDal.so.1.0.2`
- `/usr/lib/libIoDrvDal.so.1` → `libIoDrvDal.so.1.0.2`
- `/usr/lib/cds3-custom-components/libIoDrvDal.so` → `../libIoDrvDal.so`
- `/usr/lib/IoDrvDal/libIoDrvKbus.so` → `../libIoDrvKbus.so.0.0.1`

`/etc/opkg/opkg.conf` benennt `/usr/share/opkg/status` als Statusdatei und `/usr/share/opkg/info` als Metadatenverzeichnis. Der Status führt `cds3-iodrvdal` Version `1.0.2` und `cds3-iodrvkbus` Version `0.0.1`, beide mit `Status: install user installed` und `Architecture: armhf`. Die zugehörigen `.control`-Dateien bestätigen die jeweiligen Paketversionen. Die `.list`-Datei von `cds3-iodrvdal` ordnet die reguläre Datei und zwei Symlinks `/usr/lib` zu; `cds3-iodrvkbus.list` ordnet die reguläre Kbus-Datei sowie den Symlink unter `/usr/lib/IoDrvDal` zu. Kopien dieser sechs Metadatendateien liegen im Unterverzeichnis `metadata/`; Größen und Hashes stehen in `manifest.tsv`.

`manifest.tsv` listet das Eingabeartefakt und alle weiteren Paketdateien einschließlich dieses Berichts mit Größe und SHA-256. Die Manifestdatei selbst ist von ihrer eigenen Liste ausgenommen.

## Eingang, REA und Methode

Eingabegröße: **287,309,824 Bytes**. Eingangshash erneut geprüft: **PASS**, SHA-256 wie oben.

REA wurde zuerst mit `inspect_firmware_regions` auf dem exakten absoluten Imagepfad aufgerufen. Der einmalige Fehler lautete: `capability_unavailable` / `unsupported_provider`: `This integration requires Linux and an absolute REA_BINWALK_COMMAND path to the caller-supplied tool`. REA gab dabei keine Evidence-ID und keine Firmwareregionen zurück. Die identische Operation wurde nicht wiederholt; mangels REA-Ergebnis gibt es keine REA-Evidence-IDs und kein kanonisches REA-Evidence-Bundle für diesen Lauf.

Darauf folgte der lokale, rein lesende Fallback. Es wurde nichts gemountet, installiert, heruntergeladen oder ausgeführt. Partitionen wurden mit `dd` in Paketdateien kopiert. `blkid -p`, `fdisk -l`, `dumpe2fs -h` und `debugfs` lasen die Partitionstabelle bzw. Dateisystemstrukturen. Die exakten Dateien wurden über `debugfs dump` aus dem ext3-Dateisystem extrahiert. `scan_names.py` traversiert per `debugfs ls -p -l` die erreichbaren Verzeichnisse, folgt keinen Symlinks und vergleicht die vollständigen Basenames exakt.

Verwendete Werkzeugversionen: `file` 5.46; util-linux `fdisk` 2.41.5 und `blkid` 2.41.5; e2fsprogs `debugfs`/`dumpe2fs` 1.47.2; Python 3.13.5; GNU coreutils 9.7 (`dd`, `stat`, `sha256sum`).

Relevante reproduzierbare Kommandos (Pfade wie in `validate.sh`):

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`validate.sh` wiederholt Eingangshash- und Größenprüfung, Partitionsextraktion und Dateisystemerkennung, extrahiert die beiden Dateien in ein temporäres Verzeichnis innerhalb dieses Pakets und vergleicht sie byteweise (`cmp`) mit den abgelegten Ergebnissen. Es prüft zusätzlich Symlinkziele, opkg-Versionen und den vollständigen ext3-Namensscan. Ergebnis dieses Laufs: **PASS**.

## Alternativerklärung und Restunsicherheit

Die Pfade, Inodes, unveränderten extrahierten Bytes und opkg-Metadaten belegen die enthaltenen Dateien und deren Paketzuordnung im Image. `install user installed` ist ein gespeicherter Paketstatus im Image; daraus folgt nicht, dass die Bibliotheken auf einem Gerät geladen oder zur Laufzeit verwendet werden. Dateiname, Paketzuordnung und Hash belegen weder Funktionsvertrag noch ABI. Bibliothekssemantik wurde nicht disassembliert oder dekompiliert. Die FAT-Bootpartition wurde für weitere Kopien nicht rekursiv inventarisiert; vollständige Suche und Null-Fehler gelten für den erreichbaren ext3-Namensraum.

## Status

- Eingangsintegrität — **PASS**
- Partitionen und Dateisysteme — **PASS**
- Exakte Treffer, Metadaten und Symlinks im ext3-Namensraum — **VERIFIZIERT**
- Bytegleiche Extraktion und Hashes — **PASS**
- REA Firmwareanalyse — **BLOCKED** (REA-Binwalk-Voraussetzung fehlt; lokaler Fallback abgeschlossen)
- Tests der Laufzeit-/ABI-Semantik — **NOT_RUN** (außerhalb des Auftragsbereichs)
