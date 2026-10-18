> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-168 — direkter A32-BL-Callsite-Scan auf `CMAddComponent`

## Ergebnis und Eingabeidentität

**VERIFIZIERT:** Das exakt angegebene `/usr/bin/codesys3` ist 5.181.396 Bytes groß, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`. GNU readelf identifiziert es als ELF32, little-endian, ARM `EXEC`. Der Dynsym-Eintrag ist `CMAddComponent`, VMA `0x002FD0F0`, Größe 520, `FUNC GLOBAL DEFAULT`.

Der vollständige direkte A32-`BL`-Scan der ausführbaren Sections `.init`, `.plt`, `.text`, `.fini` fand genau sieben Branches auf `0x002FD0F0`. Ein unabhängiger roher Opcode-Scan der vier executable Bereiche mit ARM-PC-Regel `PC=call+8` und vorzeichenerweiterter `imm24<<2` ergab dieselben sieben Adressen. GNU objdump dekodierte an jeder Adresse denselben direkten Zielwert; Dateiwort, Instruktionswort und Zielberechnung wurden validiert. Inventar und Kodierungen stehen in [`callscan.tsv`](callscan.tsv).

| Callsite | A32-Wort | Begrenztes Fenster | Dynsym-Funktion, deren Extent den Callsite einschließt |
|---:|---:|---|---|
| `0x00086BFC` | `0xEB09D93B` | `[0x00086BAC,0x00086C0C)` | keine Dynsym-Zuordnung im gebundenen Inventar |
| `0x002FE298` | `0xEBFFFB94` | `[0x002FE248,0x002FE2A8)` | keine Dynsym-Zuordnung im gebundenen Inventar |
| `0x002FE574` | `0xEBFFFADD` | `[0x002FE524,0x002FE584)` | `cmaddcomponent`, Dynsym `[0x002FE514,0x002FE594)` |
| `0x002FE6D4` | `0xEBFFFA85` | `[0x002FE684,0x002FE6E4)` | `cmaddcomponent2`, Dynsym `[0x002FE594,0x002FE6F4)` |
| `0x002FEC08` | `0xEBFFF938` | `[0x002FEBB8,0x002FEC18)` | keine Dynsym-Zuordnung im gebundenen Inventar; WP166-Fensterüberlappung ausdrücklich nur als Gegenprüfung |
| `0x002FFDA0` | `0xEBFFF4D2` | `[0x002FFD50,0x002FFDB0)` | `CMLoadComponent3`, Dynsym `[0x002FFC84,0x002FFE08)` |
| `0x00301F30` | `0xEBFFEC6E` | `[0x00301EE0,0x00301F40)` | `CMInit3`, Dynsym `[0x00301A50,0x003021E4)` |

Dynsym-Zuordnungen gelten nur, wenn `st_value <= Callsite < st_value+st_size`. Die Sites `0x86BFC`, `0x2FE298` und `0x2FEC08` liegen außerhalb der Extents ähnlich benannter Dynsym-Einträge (`getsyncinformation`, `CMGetAPI`, `cmremovecomponent`). In den begrenzten GNU-objdump-Ausgaben sichtbare nächstgelegene Labels sind Disassembler-Symbolisierung und kein Ownership-Nachweis.

## Begrenzte Disassemblierung

Für jeden Call wurde ausschließlich `[call-0x50, call+0x10)` dekodiert. Alle Callsites liegen in `.text`, fern genug von dessen Grenzen; daher war kein Fenster zu kappen. Jedes Fenster ist eine Folge von 24 vier Byte breiten Instruktionen (96 Bytes) ohne Lücke. [`windows.tsv`](windows.tsv) enthält pro Zeile Callsite, VMA, Datei-Offset, vier Dateibytes in little-endian Reihenfolge und Disassemblierung. Die Daten sind nach Callsite gruppiert und je Gruppe vollständig/adresskontinuierlich. [`windows.raw.txt`](windows.raw.txt) enthält getrennt die zugehörige unverarbeitete objdump-Ausgabe.

## r0/r1-Formen und Call-Clobber-Grenzen

Registerwerte werden innerhalb des jeweiligen Fensters bis zu einer frischen Definition oder einer opaken `BL`-Grenze verfolgt. Ein opaker Call invalidiert r0-r3; frühere r0/r1-Werte werden nicht über ihn fortgeschrieben. Adressformen wie `fp-...` sind Registerausdrücke, keine Aussage über Typ oder Zweck.

| Callsite | r0 am Call | r1 am Call | Grundlage / Clobber-Behandlung |
|---:|---|---|---|
| `0x00086BFC` | Wert am Fenstereintritt, im Fenster nicht definiert/rückverfolgbar | Wert am Fenstereintritt, im Fenster nicht definiert/rückverfolgbar | Keine r0/r1-Definition und kein vorangehender Call im begrenzten Fenster; `fp-848`/`fp-852` stammen aus `0x86B94/98`, außerhalb der Schranke, daher nicht belegt und ausgeschlossen. |
| `0x002FE298` | `fp-88` | `fp-100` | Vorher `strcmp` bei `0x2FE27C`; danach frische r1-Definition bei `0x2FE280`, Vergleich bei `0x2FE284`, frische r0-Definition bei `0x2FE288` |
| `0x002FE574` | `fp-72` | aktueller Rohwert aus `[r4+12]` | `ldr r1,[r4,#12]` bei `0x2FE558`, `sub r0,fp,#72` bei `0x2FE55C`; beide Definitionen sind lokal vor dem Call sichtbar |
| `0x002FE6D4` | `fp-80` | aktueller Rohwert aus `[r4+12]` | Opaker `MemPoolUnlock`-Call bei `0x2FE6A0`; danach frische r0-Definition `sub r0,fp,#80` bei `0x2FE6C8` und r1-Definition `ldr r1,[r4,#12]` bei `0x2FE6B0` |
| `0x002FEC08` | `fp-96` | `fp-184` | Lokal frische Adressformen bei `0x2FEBF4/F8`; kein opaker Call im Fenster vor dem Ziel. WP166-Überlappung für Call und Argumentformen als Gegenprüfung markiert; WP166-Report nennt dieselben Werte. |
| `0x002FFDA0` | `fp-88` | `fp-92` | Opaker `CMCallHook`-Call bei `0x2FFD94`; `r1` und `r0` werden danach frisch bei `0x2FFD98/9C` gesetzt |
| `0x00301F30` | Wert von `r8` am Fenstereintritt, innerhalb des Fensters nicht weiter rückverfolgbar | `fp-124` | `r0 := r8` frisch bei `0x301F18`, RHS-Historie liegt vor dem Fenster; `r1 := fp-124` bei `0x301F10` |

## Unmittelbarer Return-use innerhalb der Schranke

Nur Instruktionen bis einschließlich `call+0x0C` wurden hierfür berücksichtigt. „Kein Test“ bedeutet nur: innerhalb dieser unmittelbaren lokalen Schranke kein sichtbarer Test/Use des Rückgabewerts.

| Callsite | Sichtbare Instruktionen nach Call | Befund zum r0-Return |
|---:|---|---|
| `0x00086BFC` | `+0x04 ldr r2,[fp,#-852]`; `+0x08 cmp r2,r5`; `+0x0C str r0,[r4,#4]` | Kein Return-Test; r0 wird bei `+0x0C` gespeichert. |
| `0x002FE298` | `+0x04 cmp r9,#0`; `+0x08 ldreq r9,[fp,#-100]`; `+0x0C ldr r4,[r5,#12]` | Kein sichtbarer r0-Return-use/test innerhalb des Fensters. |
| `0x002FE574` | `+0x04 cmn r0,#1`; `+0x08 str r0,[r4,#16]`; `+0x0C beq ...` | Rückgabe wird unmittelbar auf `-1` geprüft; Branch nimmt das vom Test gesetzte Flag. Keine weitergehende Fehlersemantik abgeleitet. |
| `0x002FE6D4` | `+0x04 cmn r0,#1`; `+0x08 str r0,[r4,#16]`; `+0x0C beq ...` | Rückgabe wird unmittelbar auf `-1` geprüft; Branch nimmt das vom Test gesetzte Flag. |
| `0x002FEC08` | `+0x04 b ...`; anschließender Code folgt nicht im Fenster | Kein unmittelbarer r0-Return-use/test sichtbar. |
| `0x002FFDA0` | `+0x04 cmn r0,#1`; `+0x08 mov r6,r0`; `+0x0C beq ...` | Rückgabe wird auf `-1` geprüft und in r6 kopiert; Branch nutzt die Testflags. |
| `0x00301F30` | `+0x04 ldr r3,[fp,#-132]`; `+0x08 cmp r3,#0`; `+0x0C ldreq r3,[fp,#-124]` | Kein sichtbarer r0-Return-use/test innerhalb des unmittelbaren Fensters. |

Für `0x002FE574` und `0x002FE6D4` schreibt der Store nach dem Vergleich r0, ändert aber nicht die Vergleichsflags; damit folgt der Branch lokal auf den `cmn`-Test. Dies beschreibt ausschließlich sichtbare Instruktionen und nicht die Bedeutung des Werts `-1`.

## REA, Toolchain und Reproduktion

REA wurde zuerst mit `open_binary` auf genau diesem lokalen ELF verwendet; die Rückgabe bestätigte ARM-ELF und denselben SHA-256. Der zielgerichtete `xrefs(0x002FD0F0)`-Versuch über REA/Ghidra wurde nicht innerhalb des Zeitfensters zurückgegeben. Das Retained-Evidence-Summary enthält einen passenden xrefs-Datensatz, aber kein für diese Operation verfügbares Analyse-View; dieser Pfad lieferte daher keine verwertbare Callsite-Tabelle. Es wurde kein weiterer langlaufender Ghidra-Versuch gestartet.

Der danach ausgeführte reproduzierbare Fallback ist [`scan_and_validate.py`](scan_and_validate.py). Er prüft Größe/Hash, die vier `AX`-Section-Grenzen mit readelf, scannt jedes ausgerichtete 32-Bit-Wort auf ein A32-BL-Encoding mit exakt berechnetem Ziel, vergleicht Rohscan und objdump-Decode, validiert Dynsym und erzeugt die Call-Inventur sowie die sieben Fensterdateien. Aufruf: `python3 scan_and_validate.py` im WP-Ordner oder direkt per absolutem Pfad. GNU ARM `objdump` und `readelf`, Python sowie die erfolgreichen Validatorausgaben sind in [`tool_versions.txt`](tool_versions.txt) und [`validator_result.txt`](validator_result.txt) festgehalten.

## Status, Alternativen und Restunsicherheit

| Aussage / Prüfung | Status | Grund |
|---|---|---|
| Angegebene Dateigröße und SHA-256 | VERIFIZIERT | Direkte Dateiprüfung |
| Dynsym-Identität `CMAddComponent`, `0x002FD0F0`, 520 Bytes | VERIFIZIERT | GNU readelf; Validator |
| Vollständigkeit der direkten A32-BL-Treffer in allen vier `AX`-Sections | VERIFIZIERT | Rohopcode-Zielscan deckt sich vollständig mit ARM objdump; sieben eindeutige Sites |
| Fenstergrenzen, 24 Instruktionen/96 Bytes je Site, Dateibytes | VERIFIZIERT | Script prüft jedes VMA, den zugehörigen ELF-Dateibereich und die durchgehende Abdeckung |
| Lokale r0/r1-Formen und immediate Return-use innerhalb der Fenster | VERIFIZIERT | Sichtbare, begrenzte Instruktionsfolge mit expliziten Clobbergrenzen |
| Frühere Register-/Symbolzuordnungen | FAIL | Erste Berichtsfassung verwendete Definitionen vor Fensterbeginn, enthielt eine unzutreffende r0-Quelle für `0x2FE6D4` und übernahm nearest objdump labels als Caller-Namen. Korrigierte Fassung streicht diese Aussagen und weist Dynsym ownership nur über extents aus. |
| Werte/Wirksamkeit über opake Callees und vor Fensterbeginn | OFFEN | Nicht propagiert; lokal nicht etablierte Ursprünge bleiben unbekannt |
| API-, Struct-, Feld- oder Komponentenbedeutung | OFFEN | Ausdrücklich außerhalb des Umfangs |
| Erklärungsalternative für die sichtbaren Formen | HYPOTHESE | Adressformen und Rohwerte können nur temporäre lokale Call-Eingaben sein; aus diesem Ausschnitt folgt keine fachliche Rolle. |
| Target-Lauf oder Hardwaretest | NOT_RUN | Nicht angefordert; ausschließlich offline-statische Analyse |
| Paketvalidator und Checksums | PASS | Siehe `validator_result.txt`, `SHA256SUMS` |

Alternativ hätte der Ghidra-xrefs-Bericht Callers sammeln können; sein ausbleibendes Ergebnis wurde nicht als Vollständigkeitsbeleg verwendet. Der unabhängige Opcode/objdump-Fallback prüft ausschließlich direkt encodierte A32-`BL`-Ziele in den ELF-`AX`-Sections. Nicht erfasst werden indirekte Calls, Thumb-Callformen, dynamisch konstruierte Transfers oder Laufzeitpfade. Der A32-Scope entspricht der angefragten direkten `bl`-Menge. Die Vollständigkeit bezieht sich auf das gebundene ELF und diese Opcode-/Section-Definition.

Self-Review: Hashbindung, ELF-Sectiongrenzen, Raw-Encoding-Zielformel, GNU-Decode, Callsite-Inventar, Dynsym-Extents und alle Fenster wurden gegeneinander validiert. Die vorige Berichtsfassung überschritt bei `0x86BFC` den Register-Window-Scope und enthielt eine unzutreffende r0-Quelle für `0x2FE6D4`; beide Befunde bleiben als FAIL dokumentiert und werden nicht als belastbare Argumentformen ausgegeben. Keine Call- oder Callee-Semantik, Structlayouts, Feldnamen oder Typen wurden abgeleitet. WP166-Überlappung ist ausschließlich als Gegenprüfung markiert. Unabhängiges Review wird nicht behauptet.
