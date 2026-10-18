> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-236 — Bereichsscan nach `r0=15` vor indirektem `blx`

## Ergebnis und Identität

**VERIFIZIERT** — Eingabe `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-127/hit_files/usr/bin/codesys3`: 5.181.396 Byte; SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.

**VERIFIZIERT** — Für den deklarierten statischen Suchtest wurde kein Pfad gefunden, der am geprüften indirekten `blx` nachweisbar `r0=15` liefert, ohne Werte über Calls fortzuschreiben. Es gibt acht bestätigte `LDR [base,#0x20]`→`BLX register`-Kandidaten; die `r0`-Quelle ist an keinem Kandidaten statisch `15`.

**OFFEN** — Ein Laufzeitwert könnte aus einem unbekannten Funktionseingang oder Speicherzustand 15 sein. Das ist keine statische Feststellung dieses Befunds.

## REA, Bereich und begrenzter Fallback

**VERIFIZIERT** — REA 6.5.0 mit Ghidra 12.1.4 öffnete die Eingabe als ARM ELF. Der verfügbare native Pfad bietet Punktabfragen (`inspect_native_instruction`) und funktionsgebundene Abfragen (`read_function_instructions`/`analyze_function`), aber keine bereichsvollständige Instruktions- und Datenflussabfrage für das verlangte Intervall. Das ist der beobachtete Gap.

**VERIFIZIERT** — GNU ARM objdump 2.44 (`arm-linux-gnueabihf-objdump`) wurde deshalb als benannter begrenzter Fallback verwendet: `-D -z --section=.text` separat auf den drei erlaubten Intervallen `[0x280000,0x300b10)`, `[0x300e38,0x301394)` und `[0x3018b8,0x344fc0)`. Die beiden ausgeschlossenen Körper `[0x300b10,0x300e38)` und `[0x301394,0x3018b8)` lagen zwischen diesen Aufrufen; keiner wurde disassembliert.

**VERIFIZIERT** — Die vollständigen bounded Ausgaben enthalten 131.780 + 343 + 69.058 = 201.181 A32-Wörter (804.724 Byte); `-z` verhindert das Unterdrücken von Nullwörtern. Es wurden keine Ausgaben aus Nachbarbereichen jenseits des Hauptbereichs verwendet. Der lokale Validator inventarisiert 374 als `blx register` dekodierte Stellen und 473 `ldr*`-Familien-Instruktionen mit Offset `#0x20`: davon exakt 378 plain `ldr` und 95 andere `ldr*`-Mnemoniken. Die acht bestätigten Ziel-Lade-/`blx`-Kandidaten sind alle plain `ldr`. Eine CFG-Suche trägt nur den sichtbaren geladenen Zielregisterwert weiter, folgt direkten/bedingten Branchkanten und einfachen Registerkopien und beendet Wertfortschreibung an Calls. Ghidra bestätigte die acht resultierenden Instruktionsketten einzeln.

**VERIFIZIERT** — Adressbindung: In diesem ELF ist Provider-VA gleich ELF-VA; `address_to_file_offset` bestätigte unter anderem `0x2b5b78 → 0x2a5b78`. Für die deklarierte `.text`-Abbildung gilt durchgehend `Datei-Offset = ELF-VA − 0x10000`, wie auch das Assignment für Intervallgrenzen festhält.

## Alle akzeptierten Ziel-Lade-/Aufrufketten

**VERIFIZIERT** — Alle acht Kandidaten wurden per `inspect_native_instruction` an beiden Enden als A32-`ldr ...,#0x20` und indirektes `blx` bestätigt. Das Feld „`r0` am `blx`“ bindet den jeweils sichtbaren Quellwert; `unbekannt` wird nicht zu 15 fortgeschrieben.

| LDR ELF-VA / Datei-Offset | BLX ELF-VA / Datei-Offset | sichtbarer Pfad und `r0` am BLX | Bewertung für `r0=15` |
|---|---|---|---|
| `0x2b5958 / 0x2a5958` | `0x2b5960 / 0x2a5960` | `ldr r3,[r5,#0x20]`; `0x2b595c: mov r0,r6`; `blx r3`. `r6` stammt aus einem früheren opaken `blx`; vor der Nutzung liegt außerdem ein opaker `bl` bei `0x2b5944`. | **OFFEN** — nicht als 15 fortgeschrieben |
| `0x2b5b78 / 0x2a5b78` | `0x2b5b80 / 0x2a5b80` | `ldr r3,[r3,#0x20]`; `0x2b5b7c: mov r0,r4`; `blx r3`. Im Funktionskörper wird `r4` zuvor aus dem eingehenden `r2` kopiert. | **OFFEN** — Eingangswert unbekannt |
| `0x2b64ac / 0x2a64ac` | `0x2b64b0 / 0x2a64b0` | `ldr r3,[r3,#0x20]`; `blx r3`. `r0` ist der nicht konstant gesetzte Funktionseingang. | **OFFEN** — Eingangswert unbekannt |
| `0x30c810 / 0x2fc810` | `0x30c818 / 0x2fc818` | `ldr r3,[r3,#0x20]`; `0x30c814: ldr r0,[r2,#8]`; `blx r3`. | **OFFEN** — Speicherwert unbekannt |
| `0x32df5c / 0x31df5c` | `0x32df6c / 0x31df6c` | `ldr r5,[r4,#0x20]`; `0x32df60: ldr r0,[0x32dfa0]`; `blx r5`. Die bounded REA-Datenlesung ergab bei `0x32dfa0` Bytes `40c93a00` (Little Endian: `0x003ac940`). | **VERIFIZIERT** — sichtbar nicht 15 |
| `0x32df78 / 0x31df78` | `0x32df88 / 0x31df88` | `ldr r4,[r4,#0x20]`; `0x32df84: ldr r0,[0x32dfa4]`; `blx r4`. Die bounded REA-Datenlesung ergab bei `0x32dfa4` Bytes `c0d13a00` (Little Endian: `0x003ad1c0`). | **VERIFIZIERT** — sichtbar nicht 15 |
| `0x32fc30 / 0x31fc30` | `0x32fc38 / 0x31fc38` | `ldr r3,[r8,#0x20]`; `0x32fc34: ldr r0,[r2,#8]`; `blx r3`. | **OFFEN** — Speicherwert unbekannt |
| `0x32fcec / 0x31fcec` | `0x32fcf4 / 0x31fcf4` | `ldr r3,[r8,#0x20]`; `0x32fcf0: ldr r0,[r2,#8]`; `blx r3`. | **OFFEN** — Speicherwert unbekannt |

**VERIFIZIERT** — In der ersten Kette wird `r6` nicht über den opaken Call fortgeschrieben; folglich ist daraus kein `r0=15`-Beleg ableitbar. Die zweite und dritte Kette erhalten `r0` aus einem nicht als Konstante belegten Eingangswert/Register. Die drei Speicherladefälle bleiben bezüglich ihres Werts **OFFEN**. Die zwei PC-relativen Literale sind dagegen sichtbar ungleich 15.

## Vollständige sichtbare `r0=15`-Schreibstellen

**VERIFIZIERT** — Im bounded Disassembly und in den dazugehörigen REA-Punktabfragen wurden diese zwölf `mov* r0,#15`-Instruktionen gefunden. Ihre Datei-Offsets folgen der oben angegebenen Abbildung. Keine gehört zu einem der acht bestätigten Ziel-Lade-/`blx`-Funktionskörper.

| ELF-VA / Datei-Offset | Instruktion | adressgebundene Ausschlussbeobachtung |
|---|---|---|
| `0x3047d8 / 0x2f47d8` | `movcc r0,#15` | unmittelbarer Epilog danach |
| `0x30485c / 0x2f485c` | `movcc r0,#15` | unmittelbarer Epilog danach |
| `0x3048c8 / 0x2f48c8` | `movhi r0,#15` | Gegenpfad setzt `r0` aus `r2`; danach Epilog |
| `0x304934 / 0x2f4934` | `movhi r0,#15` | Gegenpfad setzt `r0` aus `r3`; danach Epilog |
| `0x304a90 / 0x2f4a90` | `movne r0,#15` | unmittelbarer Epilog danach |
| `0x3058c4 / 0x2f58c4` | `mov r0,#15` | unmittelbarer Epilog danach |
| `0x305974 / 0x2f5974` | `mov r0,#15` | unmittelbarer Epilog danach |
| `0x30626c / 0x2f626c` | `mov r0,#15` | weiterer Pfad endet am Epilog; in diesem Funktionskörper liegt keine der acht Zielketten |
| `0x312738 / 0x302738` | `movne r0,#15` | Return-Pfad; Gegenpfad überschreibt `r0`, danach direkter `bl` |
| `0x31860c / 0x30860c` | `mov r0,#15` | Wert wird nach `[sp,#8]` gespeichert; danach überschreibt `ldmia r3,{r0,r1,r2,r3}` `r0` vor direktem `bl` |
| `0x31e700 / 0x30e700` | `mov r0,#15` | `0x31e704: movt r0,#1` ändert den Gesamtwert vor späterem direktem Call; Ghidra ordnet die Stelle keiner Procedure zu |
| `0x341d30 / 0x331d30` | `mov r0,#15` | danach Branch zurück; in diesem Funktionskörper liegt keine der acht Zielketten |

**VERIFIZIERT** — Zusätzlich wurde `0x30ffdc: movt r0,#15` als bloße Teilregister-Schreibstelle ausgeschlossen: der vorherige `movw r0,#0x2da3` setzt den unteren Teil; nach `movt` ist `r0` nicht 15.

## Status, Alternativerklärung und Restunsicherheit

**VERIFIZIERT** — Befund für die deklarierte statische Methode: keine adressgebundene Kette mit sichtbar konstantem `r0=15` erreicht einen der acht `blx`-Aufrufe, deren Ziel zuvor sichtbar aus `[base,#0x20]` geladen wurde. Encoding-/Pfadgrenze: A32-32-Bit-Wortdekodierung in den drei angegebenen bounded Intervallen; Registerwertverfolgung über direkte CFG-Kanten und einfache Kopien, mit Abbruch an jedem Call. Bereichsgrenze: ELF-VA `[0x00280000,0x00344fc0)`, abzüglich der beiden explizit ausgeschlossenen Körper.

**HYPOTHESE** — Ein Kandidat könnte zur Laufzeit `r0=15` erhalten, wenn ein unbekannter Aufrufer einen solchen Wert übergibt oder ein Speicherzugriff diesen Wert liefert. Ohne passende statische Definition im untersuchten Pfad ist das nicht belegt; Werte werden nicht über opake Calls angenommen.

**OFFEN** — Semantik der Zahlenwerte, Speicherinhalte außer den zwei für `r0` verwendeten Literalen, Aufrufer jenseits des geprüften Wertpfads und Laufzeitverhalten sind nicht abgeleitet. Keine Aussage zu Bedeutungen, ABI, Strukturen, Feldern, Geräten oder Laufzeitumgebung.

## Validator und Artefakte

**PASS** — `python3 validate.py` berechnet Eingabegröße und vollständigen SHA-256, disassembliert exakt die drei erlaubten Intervalle mit GNU ARM objdump und bestätigt lückenlose 4-Byte-Abdeckung, Ausschlussgrenzen, 374 `blx`, die `ldr*`-Familienaufteilung `378 plain ldr + 95 andere ldr* = 473 gesamt`, die zwölf `r0=15`-Fundstellen sowie die acht CFG-Pfade. Außerdem prüft er, dass alle acht Zielketten plain `ldr` verwenden. Version: Python 3.13.5; GNU objdump 2.44.

**VERIFIZIERT** — `manifest.sha256` enthält Hashes nur von `report.md` und `validate.py`, nicht von sich selbst.
