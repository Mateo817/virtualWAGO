> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-152 — `cds3-custom-components` in FW31 `codesys3`

## Ergebnis

Im hashgeprüften ELF ist genau eine exakte ASCII-Sequenz `cds3-custom-components` enthalten. Sie ist 22 Byte lang, unmittelbar NUL-terminiert und Bestandteil des vollständigen ASCII-C-Strings `/usr/lib/cds3-custom-components`. Der String beginnt bei Datei-Offset `0x39fe4c` / ELF-VMA `0x3afe4c`; die angefragte Teilfolge beginnt bei Datei-Offset `0x39fe55` / ELF-VMA `0x3afe55`.

Für beide Adressen materialisierten die begrenzten aktuellen Code-Xref-Abfragen keine direkten Xrefs. Daher gibt es in diesem Bericht keinen akzeptierten konsumierenden Bereich und keine zugehörige Instruktionsfolge oder sichtbaren Argumente. Das ist ein begrenztes Nullresultat dieser statischen Verfahren, kein Beleg, dass die Zeichenfolge nicht verwendet wird.

## Befunde

| Befund | Status | Evidenz und Grenze |
|---|---|---|
| Dateiidentität und Größe entsprechen der Vorgabe. | VERIFIZIERT | 5,181,396 Byte; SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`; ELF32 little-endian ARM EABI5 ET_EXEC. |
| Exakte ASCII-Suche über alle Dateibytes ergibt einen Treffer, direkt gefolgt von NUL. | VERIFIZIERT | Byte-Treffer in `occurrences.tsv`; lokale Bytes in `raw-evidence.md`; vollständige Suche im Validator reproduziert. |
| Der Treffer liegt in `/usr/lib/cds3-custom-components`. | VERIFIZIERT | Rohbytes, `.rodata`-Mapping und hashgebundene REA-Namensbeobachtung `ev_a109c01f038b67a875d15913e9a8854d87be2542184151d79acf9d62311b4fcc`. Der Stringname ist kein Verbrauchsnachweis. |
| Direkte konsumierende Referenzen zu Stringanfang oder Teilstringanfang. | VERIFIZIERT | Kein Referenzsatz von Rizin 0.9.1 nach `aa; aar` für `.text`, beide `axtj`-Ergebnisse leer; vollständiger GNU ARM objdump-Adressfilter ohne Treffer. Diese Nullbeobachtung ist auf diese Provider-/Methodenabdeckung begrenzt. |
| Funktionszuordnung, Instruktionsfluss und Argumente bis zum ersten Aufruf. | OFFEN | Ohne akzeptierten direkten Xref gibt es in diesem Work-Package keinen konsumierenden Instruktionsbereich, für den solche Flüsse dokumentiert werden könnten. |

## Fundstellen- und Xref-Abdeckung

`occurrences.tsv` führt den einzigen Treffer auf. `xrefs.tsv` führt für diese Fundstelle sowohl die Adresse des gesamten C-Strings als auch die Startadresse des exakten Teilstrings als getrennte Referenzziele auf und vermerkt das Nullresultat der begrenzten Referenzverfahren. Der REA-Nameintrag bei `0x3afe4c` wird nur als String-/Labelbeobachtung gewertet. Die REA-Suche nach dem Literal war einmal gestartet, aber vor Abschluss der Ghidra-Autoanalyse abgebrochen; sie ist kein negativer Suchbeleg. Lauf-ID, Fehler und Profile-Digest stehen in `raw-evidence.md`.

Die angeforderte Instruktionstabelle `instructions.tsv` enthält nur die Kopfzeile, weil kein konsumierender Xref akzeptiert wurde. Es gibt daher weder erfundene Instruktionsfenster noch angenommene Register-/Stackargumente.

## Adressdomänen und Suchgrenzen

Die Dateioffsets `0x39fe4c` und `0x39fe55` sind Bytepositionen im konkreten ELF. Die zugehörigen ELF-VMAs `0x3afe4c` und `0x3afe55` werden über den file-backed `.rodata`-Bereich (`sh_offset=0x334fc8`, `sh_addr=0x344fc8`) berechnet. Das sind statische ELF-Adressen, keine Laufzeitadressen.

Die vollständige Bytefolge wurde über die gesamte 5,181,396-Byte-Datei gesucht. Rizin `aar` prüfte Codeverweise im gesamten `.text`-Bereich VMA `0x7cb10`, Länge `0x2c84b0`; die `axtj`-Abfragen zielten auf beide Zeichenadressen. GNU ARM objdump disassemblierte ausführbare ELF-Sektionen und ein Literalfilter suchte nach den beiden VMAs. Zusätzlich wurde die komplette Datei auf rohe little-endian 32-Bit-Pointerbytes für beide Adressen (`4cfe3a00`, `55fe3a00`) geprüft. Diese Suche deckt unmittelbare Adressreferenzen ab, nicht jede berechnete, relocierte oder indirekte Konstruktion.

## Alternative Erklärung und Restunsicherheit

Der String kann unreferenzierter/archivierter Datenbestand sein. Ebenso könnte eine Referenz über anders berechnete oder indirekte Adressbildung, Daten-/Tabellenzugriff außerhalb des `.text`-Scans, oder durch eine von den eingesetzten Verfahren nicht erkannte Instruktions-/Relokationsform zustande kommen. Die Nullergebnisse erlauben keine Entscheidung zwischen diesen Erklärungen und belegen keine Runtime-, Load-Reihenfolge- oder Pfadsemantik.

## Evidence und Werkzeuge

- Primäre Identität: angegebene Datei; Größe und SHA-256 wurden vor Analyse und im Validator geprüft.
- Hashgebundene REA-Evidence: `ev_a109c01f038b67a875d15913e9a8854d87be2542184151d79acf9d62311b4fcc` (`list_names`, Ghidra 12.1.4), gefilterter Auszug in `rea-evidence-excerpt.json`.
- Abgebrochene REA-Anfrage: `search_strings`, Lauf-ID `58c4a1c8-721b-48a5-abf7-2d4188a69fd0`; Status `cancelled` wegen Ghidra-Start/Autoanalyse. Kein identischer Wiederholungslauf.
- Rizin 0.9.1, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`.
- GNU ARM objdump und GNU readelf 2.44.
- Vollständige reproduzierbare Kommandos und Rohbeobachtungen: `raw-evidence.md`.

## Ausgabedateien

`SHA256SUMS` listet die SHA-256 aller übrigen Dateien in diesem Ausgabeverzeichnis; es nimmt sich selbst aus, weil ein selbstreferenzieller Datei-Hash nicht definierbar ist. Validatoraufruf: `python3 validate.py`. Prüfsummenaufruf: `sha256sum -c SHA256SUMS`.
