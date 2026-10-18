> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-121 — Rohrecordfolge bei 0x3AD9FC und Vergleich

## Befund

**VERIFIZIERT:** In `codesys3` beginnt bei Ghidra-Default-Space-Adresse / ELF-VMA `0x003AD9FC` eine vollständige Folge aus 18 direkt angrenzenden 16-Byte-Rohrecords (288 Byte, inklusives Ende `0x003ADB1B`). REA/Ghidra 12.1.4 las genau 288/288 Byte. Die Quelle ist ELF-Datei-Offset `0x0039D9FC`; REA ordnet dem zweiten, getrennten Bereich `0x003ADD1C` Offset `0x0039DD1C` zu. Die CSV enthält beide Fenster vollständig, als Little-Endian-Wörter zerlegt, plus Rohbytes und die vom REA-Stringinventar an den jeweiligen `word1`-Zeigern gelieferten Literale. Die Datei-Offsets zweier Fenster sind separat nachgewiesen; Zwischenadressen wurden nicht gelesen.

**VERIFIZIERT:** Im Bereich ab `0x003AD9FC` unterscheiden sich alle 18 `word0`-Werte (rohe Funktionszeigerwerte) von den gleichordinalen `word0`-Werten des getrennten Bereichs. Alle 18 `word1`-Zeigerwerte und alle 18 Literalnamen sind ebenfalls verschieden. `word2` ist in beiden Folgen bei allen 18 Records `0`. `word3` ist im getrennten Bereich bei allen 18 Records `0`; in der Folge ab `0x003AD9FC` ist es bei Record 1 `0`, bei Record 2 `0x03010200` und bei Records 3–18 `0x03051100`. Dies sind ausschließlich byte-/wortweise Beobachtungen; den Feldwerten wird keine API-, Struct- oder Dispatch-Bedeutung zugewiesen.

Die vollständige Folge ab `0x003AD9FC` (Index/Ordinal, `word0`/`word1`/`word2`/`word3`, roh und Literale) steht zusammen mit der getrennten Folge in [records.csv](records.csv). Für jeden `word1`-Zeiger hat REA zusätzlich die gemeldete Stringlänge bytegenau gelesen und die Startadresse in einen Datei-Offset abgebildet: alle 36 Reads sind vollständig, und der Validator vergleicht ihre Bytes mit der Quelldatei. Die 18 ersten Literale sind US-ASCII, unter anderem `iomgrregisterinstance`, `iomgrwriteoutputs` und `iomgrscanmodules`; die 18 zweiten umfassen `IoMgrCopyOutputBE`, `IoMgrConfigGetDriver` und `IoMgrConfigGetParameterValueByte`. CSV-Spalten trennen sichtbare ASCII-Länge von REAs `byte_length`; alle String-Evidence-Records melden `termination=present_or_not_required`. Diese Schreibweisen sind beobachtete Dateiliterale und keine Funktionsverträge. `word0`-Ziele wurden nicht aufgelöst oder verfolgt.

## Callkontext und Adressräume

REA-Instruktionsevidence für `FUN_00330610` enthält innerhalb des angeforderten Kontextfensters `0x330630..0x330650`: `mov r2,#1` bei `0x330630`; Funktionszeigerladen `ldr r5,[r4,#0x150]` bei `0x330634`; `mov r3,#0x12` bei `0x330638`; Laden von `r0=0x003AD9FC` durch `movw r0,0xd9fc` / `movt r0,0x3a` bei `0x330640`/`0x330644`; und `blx r5` bei `0x330648`. Das ist Call-Site-Kontext und identifiziert keine Callee-Semantik, keine Bedeutung von `r2`/`r3` und keinen Zielslotinhalt. Der vorangehende WP-XE164-118-Bericht bindet diese Instruktionen und Callsite an denselben `codesys3`-Hash und bezeichnet den Call als indirekt, ohne Zielauflösung.

Koordinaten:

| Folge | Ghidra-Adresse und ELF-VMA | Datei-Offset | Umfang |
|---|---:|---:|---:|
| erste Call-`r0`-Folge | `0x003AD9FC..0x003ADB1B` | `0x0039D9FC..0x0039DB1B` | 288 Byte |
| getrennte Folge | `0x003ADD1C..0x003ADE3B` | `0x0039DD1C..0x0039DE3B` | 288 Byte |

Jede 16-Byte-Zeile in der CSV besitzt Ghidra-Adresse = ELF-VMA und einen auf REA-Mapping-Evidence basierenden Datei-Offset. Dateiidentität: Größe 5,181,396 Byte; SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.

## Status, Alternative und Restunsicherheit

**VERIFIZIERT:** Die 36 begrenzten Records, ihre vier little-endian Wörter, die Rohbytes, die 36 vollständigen REA-Stringobjekte sowie die beiden Adress-zu-Datei-Offset-Abbildungen sind durch REA-Evidence und den dateigebundenen Validator überprüfbar.

**HYPOTHESE:** Die zwei Folgen könnten getrennte Callback-/Funktionsmengen aus unterschiedlichen Erzeugungs- oder Konfigurationspfaden abbilden. Die beobachteten `word3`-Differenzen im ersten Fenster könnten dabei ein klassifizierendes Datenfeld sein.

**Alternative Erklärung:** Die beiden Folgen könnten unabhängig erzeugte Registrierungslisten oder anders parametrierte Tabellen sein, deren gleiches 16-Byte-Muster keine identische Verarbeitung impliziert. Die Unterschiede könnten auch Folge unterschiedlicher Tabellenrollen oder Versionierungs-/Initialisierungszustände sein. Diese Alternativen werden von den begrenzten Bytes und Namen allein nicht entschieden.

**OFFEN:** Keine Funktion hinter `word0` wurde untersucht; kein Callee-Target-/Slot-Provenienztrace wurde durchgeführt. Keine Bedeutung von `word2`, `word3`, `r2` oder `r3`, keine Structbeschreibung und keine Semantik der beiden Folgen ist belegt. Der Name `IoMgr...` ist hier nur ein Literalfund. Das semantische Verhältnis zwischen den Listen und die Laufzeitverwendung bleiben offen. Kein Runtime-, VM-, Geräte- oder Netzwerkbefund.

## Methode und Prüfstatus

REA-first: `open_binary` auf dem angegebenen ELF mit Provider Ghidra; zwei `read_bytes`-Operationen von genau 288 Byte; 36 adressgefilterte `list_strings`-Abfragen; 36 exakte `read_bytes`-Abfragen für Stringlängen plus 36 dazugehörige `address_to_file_offset`-Mappings; `address_to_file_offset` für beide Bereichsanfänge; `read_function_instructions` für Prozedur `0x330610`, aus dem Bericht nur Callkontext `0x330630..0x330650` berichtet. REA `binary_session` meldete rea-agents 6.5.0, Ghidra 12.1.4 und Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Für diese Beobachtungen gab es keine REA-Lücke; daher kein readelf/objdump/raw-byte-Fallback.

| Prüfung / Tätigkeit | Status |
|---|---|
| Eingabegröße und SHA-256 | PASS |
| REA-Bundle: Quellhash, 113 eindeutige Evidence-Records, benötigte Reads/Maps/Callkontext | PASS |
| 36 CSV-Records gegen genau die beiden 288-Byte-Eingabefenster und 36 file-bound Name-Reads | PASS |
| Little-Endian-Wörter, Indizes/Ordinalzahlen und Dateioffsets | PASS |
| Funktionszielauflösung, Callsemantik, API-/Structlayout | NOT_RUN |
| Runtime, VM, Netzwerk, Geräte | NOT_RUN |

Self-Review: Validator lief lokal erfolgreich; keine unabhängige Prüfung oder Worker-Ausführung wird behauptet.

## Erzeugte Dateien

- `records.csv` — beide vollständigen Folgen, zusammen 36 Records.
- `rea-evidence-bundle.json` — kanonisches REA-Bundle, 113 Records, 0 Unknowns.
- `build_artifacts.py` — erzeugt `records.csv` reproduzierbar aus den vollständig beobachteten REA-Bytes und Stringresultaten.
- `validate.py` — vergleicht Quellenidentität, Evidence-Bundle und CSV mit den exakten Eingabebereichen.
- `SHA256SUMS` — Hashes aller erzeugten Dateien.
