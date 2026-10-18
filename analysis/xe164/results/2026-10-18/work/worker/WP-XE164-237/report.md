> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-237 — unabhängige Gegenprüfung von WP-XE164-235

## Ergebnis

**VERIFIZIERT** — Die drei hashgebundenen WP235-Eingaben und das Zielartefakt stimmen mit den im Auftrag angegebenen SHA-256-Werten überein. GNU ARM objdump 2.44 dekodiert im gebundenen Bereich `[0x180000,0x280000)` 262.144 lückenlose 32-Bit-Wörter. Der Originalvalidator endet mit `PASS`.

**VERIFIZIERT** — Alle 22 im Bericht gelisteten Lade-/`blx`-Zeilen und alle 17 `mov* r0,#15`-Zeilen stimmen an ihren Adressen mit dem bounded Disassembly überein. Für alle 22 gelisteten Paare stimmen Lade- und `blx`-Zielregister überein; im lokalen Stück dazwischen fand sich kein Call oder Zielregister-Schreibzugriff. Die in WP235 angegebenen `r0`-Quellen wurden an allen 22 Callstellen geprüft.

**FAIL** — Die Vollständigkeit des 22er-Zielketteninventars ist nicht reproduzierbar, wenn direkte Branchkanten innerhalb des angegebenen Bereichs mitverfolgt werden. Eine vollständige bounded A32-Abfrage mit direkter Branch-/Fallthrough-Suche findet das zusätzliche Paar `0x19402c → 0x19343c`, das in WP235 nicht aufgeführt ist. Die Instruktion `0x194030` verzweigt direkt nach `0x19342c`; dort bleibt das bei `0x19402c` geladene `r7` erhalten und wird bei `0x19343c` als `blx r7` verwendet.

**VERIFIZIERT** — Diese zusätzliche Kette belegt kein `r0=15`: bei `0x19342c` steht `ldr r0,[r2,#8]`, dessen Speicherwert unbekannt ist. Die 17 unmittelbaren `r0=15`-Schreibstellen und ihre in WP235 beschriebenen lokalen Ausschlusssequenzen wurden vollständig geprüft. Damit bleibt der begrenzte Nullbefund über *sichtbar konstantes* `r0=15` im Rahmen der dort gelisteten lokalen Setups intakt; der exakte Umfang einer weiter reichenden Branchpfad-Suche bleibt wegen nicht definierter „lokaler“ Pfadgrenze **OFFEN**.

## Identität, Bereich und Werkzeuge

Alle Werte wurden im privaten WP237-Ausgabebereich geprüft; WP235 und gemeinsame Dateien wurden nicht geändert. Die vom Auftrag vorgegebenen Hashes sind:

| Eingabe | Sollhash | Status |
|---|---|---|
| `WP-XE164-235/report.md` | `707c5a9bf9aa25f7c3f12be8172483f265c79c1bda7ccb161323c362016d3ead` | **PASS** |
| `WP-XE164-235/validate.py` | `bbb22e5112183d4ec324a2e7cc72ae9febbfad13a619801fa323ad264911b512` | **PASS** |
| `WP-XE164-235/validator-result.txt` | `6144a04da5c21a4a783e839e1af9faf6571421dc8d9d396b5a8447e925281e28` | **PASS** |
| `codesys3` | 5.181.396 Byte; `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | **PASS** |

**VERIFIZIERT** — Unabhängige Befehle: GNU ARM objdump 2.44, GNU readelf 2.44, Python 3.13.5. Der Originalvalidator wurde unverändert ausgeführt. Die zusätzliche Gegenprüfung disassembliert ausschließlich `.text` ELF-VA `[0x180000,0x280000)`, entsprechend Datei-Offsets `[0x170000,0x270000)` bei der im WP235-Bericht dokumentierten Abbildung `Offset = VA − 0x10000`. Es gab keinen REA-Aufruf: keine der adressgebundenen Zeilen blieb nach dem bytegebundenen Gegencheck ungeklärt.

## Adressgebundene Gegenprüfung: die 22 WP235-Zielketten

Die Datei-Offsets stehen jeweils in Klammern und ergeben sich aus `VA − 0x10000`. Alle folgenden Zeilen: **PASS** für Instruktionsbytes, Registergleichheit und lokale Nicht-Clobber-/Nicht-Call-Kette; `r0`-Quelle wie angegeben.

| LDR VA (Offset) → BLX VA (Offset) | `r0`-Quelle am BLX | Prüfung |
|---|---|---|
| `0x187edc (0x177edc) → 0x187ef0 (0x177ef0)` | `ldr r0,[r2,#8]` | **PASS** — Wert aus Speicher, nicht als 15 belegt |
| `0x188004 (0x178004) → 0x188010 (0x178010)` | `ldr r0,[r0,#8]` | **PASS** — Speicherwert unbekannt |
| `0x189764 (0x179764) → 0x189770 (0x179770)` | `ldr r0,[r0,#8]` | **PASS** — Speicherwert unbekannt |
| `0x189a94 (0x179a94) → 0x189aa4 (0x179aa4)` | `ldr r0,[r2,#8]` | **PASS** — Speicherwert unbekannt |
| `0x189d70 (0x179d70) → 0x189d80 (0x179d80)` | `ldr r0,[r2,#8]` | **PASS** — Speicherwert unbekannt |
| `0x189e5c (0x179e5c) → 0x189e70 (0x179e70)` | `ldr r0,[r2,#8]` | **PASS** — Speicherwert unbekannt |
| `0x189fc0 (0x179fc0) → 0x189fd0 (0x179fd0)` | `ldr r0,[r2,#8]` | **PASS** — Speicherwert unbekannt |
| `0x18c364 (0x17c364) → 0x18c374 (0x17c374)` | `ldr r0,[r0,#8]` | **PASS** — Speicherwert unbekannt |
| `0x18c51c (0x17c51c) → 0x18c528 (0x17c528)` | `ldr r0,[r0,#8]` | **PASS** — Speicherwert unbekannt |
| `0x18c7f0 (0x17c7f0) → 0x18c7fc (0x17c7fc)` | `ldr r0,[r0,#8]` | **PASS** — Speicherwert unbekannt |
| `0x18db3c (0x17db3c) → 0x18db48 (0x17db48)` | `ldr r0,[r1,#8]` | **PASS** — Speicherwert unbekannt |
| `0x18e308 (0x17e308) → 0x18e314 (0x17e314)` | `ldr r0,[r2,#8]` | **PASS** — Speicherwert unbekannt |
| `0x18e76c (0x17e76c) → 0x18e778 (0x17e778)` | `ldr r0,[r2,#8]` | **PASS** — Speicherwert unbekannt |
| `0x18eb94 (0x17eb94) → 0x18eba4 (0x17eba4)` | `ldr r0,[r0,#8]` | **PASS** — Speicherwert unbekannt |
| `0x18fb9c (0x17fb9c) → 0x18fba8 (0x17fba8)` | `ldr r0,[r1,#8]` | **PASS** — Speicherwert unbekannt |
| `0x190d70 (0x180d70) → 0x190d78 (0x180d78)` | `ldr r0,[r0,#8]` | **PASS** — Speicherwert unbekannt |
| `0x193c5c (0x183c5c) → 0x193c68 (0x183c68)` | `ldr r0,[r2,#8]` | **PASS** — Speicherwert unbekannt |
| `0x194118 (0x184118) → 0x194128 (0x184128)` | `ldr r0,[r2,#8]` | **PASS** — Speicherwert unbekannt |
| `0x1950e4 (0x1850e4) → 0x1950f0 (0x1850f0)` | `ldr r0,[ip,#8]` | **PASS** — Speicherwert unbekannt |
| `0x1a790c (0x19790c) → 0x1a7924 (0x197924)` | `mov r0,r7` | **PASS** — Registerquelle nicht konstant belegt; bedingter Sprung bietet BLX-Pfad |
| `0x1bcbfc (0x1acbfc) → 0x1bcc08 (0x1acc08)` | `mov r0,#260` | **PASS** — sichtbar nicht 15 |
| `0x1d5400 (0x1c5400) → 0x1d5408 (0x1c5408)` | `ldr r0,[r0,#8]` | **PASS** — Speicherwert unbekannt |

Zusätzliche durch Branch-/Fallthrough-Verfolgung gefundene Kette:

| LDR VA (Offset) → Branch → BLX VA (Offset) | `r0`-Quelle | Abweichung |
|---|---|---|
| `0x19402c (0x18402c) → 0x194030: b 0x19342c (0x18342c) → 0x19343c (0x18343c)` | `0x19342c: ldr r0,[r2,#8]` | **FAIL** — im WP235-Inventar nicht enthalten; Speicherwert unbekannt, daher kein sichtbares 15 |

WP235-Validierungsabgrenzung: Der dortige Validator bestätigt die fest codierten 22 Adresspaare gegen ihre Instruktionen und Zielregister, die 17 `mov* r0,#15`-Stellen, Eingabeidentität und lineare Bereichsabdeckung. Er implementiert jedoch keine Suche, die alle Lade-/Branch-/`blx`-Pfade selbst entdeckt. Der Original-`PASS` kann daher nicht als unabhängiger Beleg für die Vollständigkeit der 22 Kandidaten gelesen werden. Die zusätzliche WP237-Suche verfolgt im abgegrenzten Bereich direkte bedingte/unbedingte Branchkanten und Fallthrough, bricht Wertfortschreibung an Calls ab und stoppt bei Registerüberschreibung. Sie fand 23 `ldr #32`→`blx`-Ketten; kein entsprechender Pfad aus den acht `ldrd #32`-Stellen wurde gefunden.

## Adressgebundene Gegenprüfung: die 17 `r0=15`-Stellen

Alle 17 Stellen sind exakte direkte `mov* r0,#15`-Instruktionen im bounded Disassembly und jeweils im WP235-Bericht aufgeführt. **PASS** bedeutet, dass die angegebene lokale Sequenz an der VA verifiziert wurde.

| VA (Datei-Offset) | Verifizierte lokale Folge / Ausschluss | Status |
|---|---|---|
| `0x181328 (0x171328)` | `movt r0,#1`, dann direktes `bl` — Gesamtwert ist nicht mehr 15 | **PASS** |
| `0x181484 (0x171484)` | `movt r0,#1`, dann direktes `bl` | **PASS** |
| `0x187054 (0x177054)` | `blt 0x1870f0`; Ziel führt zu `ldm ... pc`-Epilog | **PASS** |
| `0x1a75bc (0x1975bc)` | direkt folgendes `ldm sp,{...,pc}` | **PASS** |
| `0x1aeb60 (0x19eb60)` | direkt folgendes `ldm sp,{...,pc}` | **PASS** |
| `0x1aebec (0x19ebec)` | direkt folgendes `ldm sp,{...,pc}` | **PASS** |
| `0x1c8b9c (0x1b8b9c)` | `movt r0,#1`, dann `str` und direktes `bl` | **PASS** |
| `0x1cdf0c (0x1bdf0c)` | stack restore, Tail-Branch `0x184368`; am Ziel `mov r0,r3` vor direktem `bl` | **PASS** |
| `0x1cdf30 (0x1bdf30)` | stack restore, Tail-Branch `0x184138`; am Ziel `mov r0,r3` vor direktem `bl` | **PASS** |
| `0x1d6bb0 (0x1c6bb0)` | vorausgehendes direktes `bl` bei `0x1d6ba8`, danach `ldm ... pc`-Epilog | **PASS** |
| `0x1e0f3c (0x1d0f3c)` | `movt r0,#1`, dann Argument-Setup und direktes `bl` | **PASS** |
| `0x1e7764 (0x1d7764)` | direkt folgendes stack restore / `ldm ... pc` | **PASS** |
| `0x1f17d4 (0x1e17d4)` | direkt folgendes `ldm ... pc` | **PASS** |
| `0x1fcfb4 (0x1ecfb4)` | `movt r0,#1`, dann `str` und direktes `bl` | **PASS** |
| `0x211af4 (0x201af4)` | Branch nach `0x2119e4`; auf dem Pfad wird r0 gespeichert oder aus r6 neu gesetzt, dann direktes `bl` | **PASS** |
| `0x21a848 (0x20a848)` | stack restore / `ldm ... pc`-Epilog | **PASS** |
| `0x237394 (0x227394)` | `str r0,[r9,#16]`, dann Branch nach `0x2360dc` und `ldm ... pc`-Epilog | **PASS** |

## Status, Alternative und Restunsicherheit

**VERIFIZIERT** — Kein Berichtssatz behauptet eine universelle Binär- oder Laufzeiteigenschaft: WP235 bindet seinen Nullbefund ausdrücklich an den file-backed VA-Bereich `[0x180000,0x280000)`, lineare A32-Dekodierung und seine lokale Ziel-/`r0`-Methode. Daher ist keine überbreite globale Aussage zu markieren. Die Formulierung darf nicht als Beweis gelesen werden, dass alle möglichen CFG-Datenflüsse oder Laufzeitwerte ausgeschlossen sind.

**HYPOTHESE** — Die ausgelassene 23. Kette könnte aufgrund einer impliziten, engeren Definition von „lokal“ absichtlich außerhalb der 22-Zeilen-Kandidatenmethode liegen. WP235 benennt jedoch weder eine maximale Distanz noch eine Regel, die direkte Branchkanten aus der Zielketteninventur ausschließt. Deshalb bewertet diese Gegenprüfung die 22er-Vollständigkeit unter natürlicher direkter CFG-Fortschreibung als **FAIL**, nicht als bewiesenen Befund, dass r0 dort 15 wäre.

**OFFEN** — Laufzeitwerte sämtlicher Speicherquellen, erreichbare reale Pfade, nicht modellierte indirekte Kontrollflüsse und semantische Bedeutung. Keine Runtime-, Hardware-, Netzwerk- oder Geräteprüfung.

## Validator und erzeugte Dateien

**PASS** — `python3 validate.py` bestätigt Eingabe-/WP235-Hashes, Originalvalidator-PASS, 262.144 lückenlose Wörter, alle 22 WP235-Zeilen, alle 17 unmittelbaren Schreibstellen und die adressgebundene Zusatzkette. Seine Ausgabe weist die WP235-Kandidatenvollständigkeit ausdrücklich als **FAIL** aus; das ist ein Auditbefund, kein Validator-Abbruch.

**VERIFIZIERT** — Die erzeugten Dateien liegen ausschließlich unter `work/worker/WP-XE164-237/`. `manifest.sha256` ist self-reference-frei und listet Bericht und Validator.
