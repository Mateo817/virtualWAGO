> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-163 — lokaler Kontrollfluss um `SettgGetStringValue`

## Ergebnis

**VERIFIZIERT:** Für den exakt gebundenen ARM ELF32 little-endian `codesys3` belegt der Bereich `[0x002FEAD4,0x002FEB78)` 41 lückenlose 4-Byte-Instruktionen. Die vollständige VMA-/Dateioffset-/Byte-Tabelle steht in [`instructions.tsv`](instructions.tsv). Der Call bei `0x002FEB4C` erhält die vier Registerargumente `r0 = 0x003A41A8`, `r1 = r11−0x94`, `r2 = r11−0xB4`, `r3 = r11−0xBC`, sowie die zwei sichtbaren Stackargumente `[sp] = 0x00370440` und `[sp+4] = 0`. Danach prüft der lokale Code ausschließlich, ob der direkte Rückgabewert in `r0` null ist. Er wird nicht an einen weiteren Call weitergereicht.

Bei Rückgabe `r0 == 0` springt der Code zu `0x002FEB68`, setzt dort `r0 = r11−0xB4` und ruft Zieladresse `0x002FCB48` auf. Dessen Rückgabewert wird bei `0x002FEB70` unverändert von `r0` nach `r1` kopiert; `subs` setzt dabei die Flags für den Nullvergleich. `bne` bei `0x002FEB74` springt zurück zu `0x002FEB60`, wenn dieser Rückgabewert ungleich null ist. Bei Rückgabe `r0 != 0` von `SettgGetStringValue` wird stattdessen `r4` mit 1 verglichen: `r4 > 1` verzweigt zu `0x002FEC10` außerhalb des Untersuchungsbereichs; andernfalls erhöht der Code `r4` und springt zu `0x002FEB14` zurück.

Keiner der Calls wird semantisch aus seinem Symbol-/Stringnamen interpretiert. Insbesondere wird nicht behauptet, dass der Call bei `0x00304B64` schreibt oder formatiert oder dass der Call bei `0x002FCB48` den übergebenen Speicher liest oder verändert. Ihre Callee-Bodies sind nicht Teil dieses Berichts.

## Artefaktidentität und Adressräume

| Eingabe | Größe | SHA-256 | Status |
|---|---:|---|---|
| `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3` | 5.181.396 Byte | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | **VERIFIZIERT** |

`readelf -l` identifiziert einen ausführbaren `PT_LOAD` mit Dateioffset `0`, VMA `0x00010000`, Dateigröße `0x3a0340`. Für den untersuchten Bereich und die hier referenzierten Konstanten gilt damit Dateioffset = VMA − `0x10000`. Der Bereich `[0x002FEAD4,0x002FEB78)` entspricht `[0x002EEAD4,0x002EEB78)` in der Datei, insgesamt 164 Bytes. Das exklusive Ende `0x002FEB78` ist nicht dekodiert.

Die fünf aus `movw`/`movt` gebildeten Konstanten (jeweils `(imm16_movt << 16) | imm16_movw`) sind: `r8=0x00370440`, `r7=0x003A4EC0`, `r6=0x00348EFC`, `r5=0x003A41A8`, `r10=0x003A43D0`. Nur diese Adressen und die unmittelbar sichtbaren Immediates werden hier ausgewertet. [`literal_bytes.tsv`](literal_bytes.tsv) trennt VMA und Dateioffset und listet je Adresse ausschließlich die Bytes bis einschließlich des ersten NUL-Bytes.

| Register | Geladener 32-Bit-Wert | Datei-Offset | Bytes ab exakt dieser Adresse bis erstes NUL | Beobachtete Verwendung innerhalb des Bereichs |
|---|---:|---:|---|---|
| `r8` | `0x00370440` | `0x00360440` | `00` (leerer NUL-terminierter Byteinhalt) | bei `0x002FEB48` nach `[sp]` kopiert |
| `r7` | `0x003A4EC0` | `0x00394EC0` | `43 6f 6d 70 6f 6e 65 6e 74 00` (`Component\0`) | bei `0x002FEB14` nach `r3` kopiert |
| `r6` | `0x00348EFC` | `0x00338EFC` | `25 73 2e 25 64 00` (`%s.%d\0`) | bei `0x002FEB18` nach `r2` kopiert |
| `r5` | `0x003A41A8` | `0x003941A8` | `43 6f 6d 70 6f 6e 65 6e 74 4d 61 6e 61 67 65 72 00` (`ComponentManager\0`) | bei `0x002FEB44` nach `r0` kopiert |
| `r10` | `0x003A43D0` | `0x003943D0` | `2a 2a 2a 20 45 72 72 6f 72 3a 20 43 6f 6d 70 6f 6e 65 6e 74 20 3c 63 6d 70 3e 25 73 3c 2f 63 6d 70 3e 20 4e 4f 54 20 6c 6f 61 64 65 64 00` (`*** Error: Component <cmp>%s</cmp> NOT loaded\0`) | kein Register-/Speicheroperand von `r10` nach seiner Bildung innerhalb des Bereichs beobachtet |

Die Bytefolgen sind rohe, statisch begrenzte Artefaktinhalte. Aus ihren Texten wird keine Funktionalität abgeleitet.

## Calls und sichtbarer Argumentzustand

`sp` in der Tabelle ist der aktuelle Stackpointer nach `0x002FEB10: sub sp,sp,#180`; beide späteren Calls in diesem Bereich verwenden denselben Wert. `r11` ist durch `0x002FEB0C` an `r12−4` gebunden, wobei `r12` in `0x002FEAD4` als ursprünglicher `sp` kopiert wurde. `?` heißt: Der Bereich setzt vor dem Call keinen lokalen Wert für dieses Argument; eine Weiterverfolgung eines caller-saved Registers nach dem vorherigen Call wäre nicht belastbar. Stackslots werden nur dann als Argumentwerte genannt, wenn ihre Stores im Bereich sichtbar sind.

| Callsite → Zieladresse | `r0` | `r1` | `r2` | `r3` | sichtbare Stackargumente | Folgeverwendung lokaler Rückgabe |
|---|---|---|---|---|---|---|
| `0x002FEB2C → 0x00304B64` | `r11−0x94` | `50` (`0x32`) | `0x00348EFC` | `0x003A4EC0` | `[sp]=0` bei `0x002FEB24`; `[sp+4]` wird davor innerhalb des Bereichs nicht initialisiert | `r0` wird danach im Bereich nicht gelesen; keine Aussage über Call-Wirkung |
| `0x002FEB4C → 0x0033CE44` (`SettgGetStringValue`, ELF-Disassemblerannotation) | `0x003A41A8` | `r11−0x94` | `r11−0xB4` | `r11−0xBC` | `[sp]=0x00370440` bei `0x002FEB48`; `[sp+4]=0` bei `0x002FEB38` | `cmp r0,#0`; Null → `0x002FEB68`, ungleich null → `0x002FEB58`. `r0` wird nicht lokal weitergereicht. |
| `0x002FEB6C → 0x002FCB48` (`CMGetInstance`, ELF-Disassemblerannotation) | `r11−0xB4` | nach vorherigem Call nicht lokal neu gesetzt; caller-saved-Wert hier unbekannt | unbekannt | unbekannt | kein neuer Stackargument-Store unmittelbar davor; weitere Stackargumente nicht behauptet | `subs r1,r0,#0` kopiert den Rückgabewert unverändert nach `r1` und setzt Flags; `bne` bei `0x002FEB74` testet ungleich null. |

Das Argumentbild dokumentiert Register und Stackstores, keine C-Prototypen. Beim ersten Call ist allein `[sp]` im vorangehenden Bereich explizit geschrieben; über `[sp+4]` wird deshalb kein Argumentwert behauptet. Bei den beiden Calls nach `0x002FEB4C` werden `r0-r3` nach ARM-Aufrufkonvention als caller-saved behandelt; `r4` bleibt als Schleifenzähler nur unter der üblichen ABI-Annahme erhalten (callee-saved). Die Körper und ABI-Konformität der aufgerufenen Ziele wurden nicht untersucht.

## Lokaler Kontrollfluss

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Der lokale Initialwert `r4=0` kommt von `0x002FEB04`. Der Body enthält damit einen begrenzten Wiederholungspfad für nicht-null Rückgaben von `SettgGetStringValue`: `r4` wird bei den ersten zwei solchen Durchläufen inkrementiert; bei einem weiteren nicht-null Rückgabepfad führt `r4 > 1` aus dem Bereich. Das ist eine reine Kontrollflussableitung, keine Aussage über Zweck oder erwartete Rückgabewerte.

## Toolweg und Evidence-Lücke

REA wurde zuerst nach retained Evidence für SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` gefragt. Die exakte Filterabfrage lieferte `total_retained_records=0`, `matching_records=0`, `unknown_revisions=0`; daher existiert für diese Abfrage keine passende REA Evidence-ID. Das ist die dokumentierte Import-/retention-Lücke. Es wurde kein Ghidra-Import gestartet oder ein bekanntermaßen hängender Import wiederholt.

Begrenzter Offline-Fallback: GNU `arm-linux-gnueabihf-objdump` 2.44, ausschließlich `--start-address=0x002FEAD4 --stop-address=0x002FEB78`, plus GNU `arm-linux-gnueabihf-readelf` 2.44 für ELF-/PT_LOAD-Mapping. `instructions.tsv` wurde aus der begrenzten Dekodierung erstellt; jedes disassemblierte Wort wurde als little-endian Bytefolge gegen den Input und den zugeordneten Offset validiert. `literal_bytes.tsv` wurde ausschließlich durch Lesen ab den fünf unmittelbar gebildeten Adressen bis zum ersten NUL-Byte erzeugt. Das Paket enthält [`disassembly.raw.txt`](disassembly.raw.txt), [`generate.py`](generate.py), [`validate.py`](validate.py) und [`tool_versions.txt`](tool_versions.txt).

## Befundstatus, Tests und Grenzen

| Aussage / Prüfung | Status | Begründung |
|---|---|---|
| Eingabegröße und -SHA-256 | VERIFIZIERT | stimmen mit der Aufgabenbindung überein |
| Vollständige Byteabdeckung von `[0x002FEAD4,0x002FEB78)` | VERIFIZIERT | 41 fortlaufende 4-Byte-Instruktionen, 164 Bytes; Endadresse exklusiv |
| Callargumente, direkte Rückgabetests und lokale Branches | VERIFIZIERT | nur durch Instruktionen innerhalb des Bereichs belegt |
| Strings an den fünf direkt gebildeten Adressen bis zum ersten NUL | VERIFIZIERT | exakte, offsetgebundene Rohbytes; keine darüber hinausgehende Semantik |
| Wirkung der Callkörper und Speicherwirkung auf Argumentpointern | OFFEN | Callkörper ausgeschlossen; lokale Stores oder Lesevorgänge durch Callees werden nicht behauptet |
| externe ABI-Konformität und Aliasbeziehungen der lokalen Adressen | OFFEN | aus diesem Bereich allein nicht entscheidbar |
| `python3 validate.py` | PASS | prüft Artefaktbindung, Range, Kontiguität, Bytes, Callsites und Stringgrenzen |
| `sha256sum -c SHA256SUMS` | PASS | alle gelisteten Ausgabedateien stimmen |

Alternative Erklärung: Die Inhalte an den fünf Adressen können zufällige oder anderweitig genutzte Bytefolgen sein; allein ihre Rohbytes und lokalen Adressverwendungen sind belegt. Die Disassembler-Symbolannotation ist kein Beweis für einen Funktionsvertrag.

Restunsicherheit: statische Offlineanalyse belegt weder Laufzeitausführung noch den Inhalt von Registern, die durch ausgeschlossene Callees verändert werden dürfen, noch die Wirkung auf Speicher. Dieser Bericht ist Worker-Self-Review; unabhängiges Review sowie Runtime- oder Hardwarebeleg werden nicht behauptet. Tests des Zielprogramms wurden **NOT_RUN**.

## Dateien

- `report.md` — Befunde und Einordnung
- `instructions.tsv` — vollständige Instruktions-/Byte-Tabelle mit getrennten Adressräumen
- `literal_bytes.tsv` — fünf Konstantenadressen und exakt begrenzte NUL-Bytes
- `disassembly.raw.txt` — begrenzte GNU-objdump-Ausgabe
- `generate.py`, `validate.py` — Reproduktion und Paketvalidator
- `tool_versions.txt`, `validator_result.txt`, `SHA256SUMS` — Werkzeuge, Prüfergebnis und Hashmanifest

SHA-256 der erzeugten Dateien (der Hash von `report.md` selbst ist ebenfalls im Manifest geführt):

| Datei | SHA-256 |
|---|---|
| `instructions.tsv` | `3adab74ccb97d9fd6c8ccc0f1d0527da27e84e4b4ab18beb58426ebfe27a1243` |
| `literal_bytes.tsv` | `93120265bbb613d54bf5acd0e1caef2191ee1129929fd6eb2df394c914ead95b` |
| `disassembly.raw.txt` | `3bfb28c4b6ccfe60abf893c206e5ea16be6e871c7bcd533f7c0436876f74af0d` |
| `generate.py` | `fcd7b913ca03756af70252ac35050e8e38576111ce4a2e4f7f21bc05ecf5724b` |
| `validate.py` | `b2542a89d8e4b9b60d9770b4058a2993d3c5863589db0acde0620ca2242b4a7f` |
| `tool_versions.txt` | `4a1fdb859fe18b496a0ac6e1dd5fb052391c3119fdf1a6dbd2c224e9340a3a7c` |
| `validator_result.txt` | `c23ec158de62fc7bae9cb638497ce1d668f8eb4ec445efef34b1f835d3a491a5` |
