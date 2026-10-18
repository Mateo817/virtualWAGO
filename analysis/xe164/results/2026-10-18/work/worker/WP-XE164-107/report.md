> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-107 — FW31 Digital-8/16 exakte Bytefolgen

## Ergebnis

**VERIFIZIERT** — Im hier abgegrenzten Scan aller erreichbaren regulären Dateien aus Partition 2 des angegebenen FW31-SD-Images wurde keine der acht geforderten ASCII-Bytefolgen gefunden. Damit ist keine statische Firmwarequelle für diese Record-Strings im gescannten Dateisysteminhalt belegt.

Das Nullresultat belegt ausschließlich die Abwesenheit dieser Bytefolgen in den 3.058 vollständig gelesenen regulären Dateien dieser ext3-Partition. Es belegt weder Runtime- noch Applikationsabwesenheit und erklärt nicht, ob Strings außerhalb dieses Scopes, kodiert, dynamisch erzeugt oder in nicht regulären Datenbereichen vorliegen.

## Eingabe und Kontextprüfung

- Image: `PFC-G2-Linux_sd_V040901_31_r9d0900aaed.img`
- Imagegröße: 287.309.824 Bytes
- Image SHA-256 geprüft: `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c`
- Partition: 2, Byteoffset 25.165.824 (Sektor 49.152), 262.144.000 Bytes (512.000 Sektoren)
- ext-Superblockmagie geprüft: `0xEF53`
- ext-Dateisystem-UUID geprüft: `373f7dc3-cbe8-44a1-b974-a3c99d616970`

**Korrekturvermerk / Audit:** Der ursprüngliche Arbeitsauftrag nannte irrtümlich `work/worker/WP-XE164-093/report.md` und einen aus der kanonischen Tabelle falsch expandierten Hash. Der korrekte akzeptierte Kontext ist `work/worker/WP-XE164-093/observations.md`; frisch geprüft: 9.977 Bytes, SHA-256 `5132eab71e12fcb31a58650ac1dda610d3cffd5d19b7dad5823138d0605fcf80`. Diese Datei dokumentiert den verwendeten read-only `debugfs`-Traversierungs-/Dump-Fallback, die Partitionsgrenzen und den REA-Blocker. Die anfängliche Abweichung lag in der Auftragsreferenz; der erfolgreiche Scan wird dadurch nicht geändert.

## Suchumfang und Befund

Exakte, case-sensitive ASCII-Bytefolgen — ausschließlich diese acht:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Scanner traversierte von `/` alle erreichbaren echten Verzeichnisse. Symlinks wurden nicht verfolgt. Jeder als regulär gelistete Dateiinhalt wurde inode-basiert mit `debugfs dump` gelesen, gegen die gelistete Größe geprüft und vollständig byteweise auf die acht Folgen durchsucht. Dateinamen, numerische Rohmuster, weitere Partitionen, Container und Archivdateien außerhalb des Dateisysteminhalts wurden nicht als separate Suchziele ausgewertet.

| Zähler | Wert |
|---|---:|
| Erreichbare Verzeichnisse | 489 |
| Reguläre Dateien gefunden | 3.058 |
| Verzeichnisfehler | 0 |
| Listing-Parsefehler | 0 |
| Datei-Lese-/Größenfehler | 0 |
| Dateien mit mindestens einem Treffer | 0 |
| Bytefolgen-Treffer insgesamt | 0 |

Da es keine Trefferdateien gibt, existieren keine Trefferpfade, Dateigrößen, Hashes oder Byteoffsets. `hits.tsv` enthält nur den Header.

## Methode und Werkzeugversion

REA wurde in diesem Auftrag nicht ausgeführt. Der lokale read-only Fallback verwendete `/sbin/debugfs` über die aus dem Image bytegenau extrahierte Partition. Das Originalimage wurde nicht verändert. Die extrahierte Partition wurde nur während des Laufs im Ausgabeordner abgelegt und danach entfernt. Es gab keine VM-, Netzwerk-, Geräte- oder Runtimeaktion.

- `/sbin/debugfs`: e2fsprogs 1.47.2, EXT2FS Library 1.47.2
- Python: 3.13.5
- Python Standardbibliothek: `hashlib`, `os`, `re`, `shlex`, `struct`, `subprocess`, `tempfile`, `pathlib`

Reproduktion aus diesem Verzeichnis:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`scan.py` prüft Imagegröße/-hash, Partitionsoffset/-größe, ext-Magie und UUID, traversiert die Partition mit `debugfs`, liest alle regulären Dateien und schreibt `hits.tsv` sowie `scan-summary.txt`. `validate.py` führt denselben Scan erneut aus einem temporären Unterordner aus und verlangt byteidentische Ergebnisdateien sowie die erwarteten Inventar-/Fehlerzähler. `SHA256SUMS` deckt alle persistenten Arbeitsergebnisse außer sich selbst ab.

## Status

- Imageidentität und Partitionbindung — **PASS**
- Vollständige reguläre Dateiinventur im angegebenen Scope — **PASS**
- Exakte Bytefolgensuche und Trefferinventar — **PASS** (null Treffer)
- Akzeptierter WP093-Methodenkontext (Pfad, Größe, SHA-256) — **PASS**
- REA-Scan — **NOT_RUN**
- Runtime-/Applikationsverhalten — **NOT_RUN**

## Alternativerklärung und Restunsicherheit

Die Strings können in anderen Partitionen oder nicht regulären Dateisystemobjekten, in außerhalb des Dateisystems liegenden Bereichen, in komprimierten/verschlüsselten/kodierten Inhalten oder nur durch Runtime/Applikation zusammengesetzt sein. Diese Möglichkeiten wurden nicht geprüft und werden durch den Nulltreffer weder bestätigt noch ausgeschlossen. Die Suche erlaubt daher nur eine Aussage über die acht exakten ASCII-Bytefolgen in den gelesenen regulären Dateien von Partition 2.

Self-Review: Imageidentität, Dateisystembindung, Zähler und reproduzierbare TSV wurden durch den lokalen Validator nachgeprüft. Kein unabhängiger Review oder zusätzlicher Worker-Lauf behauptet.
