> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-238 — unabhängige Gegenprüfung von WP-XE164-236

## Ergebnis

**VERIFIZIERT** — Die drei erlaubten Intervalle, die zwei ausgeschlossenen Intervalle, acht adressgebundene `[base,#0x20]`-LDR→indirekte-BLX-Ketten sowie zwölf unmittelbare `r0=15`-Stellen aus WP236 sind im exakt hashgebundenen Bericht reproduzierbar. Die Nullbefundsprache bleibt für diese statische Methode begrenzt und behauptet kein Laufzeitverhalten.

**FAIL** — WP236 enthält eine falsche Datei-Offset-Angabe in der 20-Zeilen-Tabelle: `0x341d30 / 0x340d30` müsste unter der dort erklärten Formel `Datei-Offset = ELF-VA − 0x10000` `0x341d30 / 0x331d30` lauten.

**FAIL** — WP236s Bezeichnung der 473 `ldr`-Stellen ist überbreit. Der Validator verwendet `ldr(?:\w*)` und zählt damit auch `ldrb`, `ldrh`, `ldrsh`, `ldrd` und bedingte Mnemoniken. Von den 473 Treffern entfallen 378 auf den exakten Mnemonik `ldr`; 95 auf die anderen gezählten Mnemoniken (Aufteilung siehe Validatorausgabe). Die acht Zielketten selbst verwenden jeweils den exakten Mnemonik `ldr` und sind dadurch nicht betroffen.

## Eingaben, Methode und Toolstand

Die drei Assignmenteingaben wurden exakt gehasht: WP236 `report.md` SHA-256 `38a2d09cb7a099c5243552dd1036b6ef54fad9ea06d355e7b679bc81b164e36b`; WP236 `validate.py` `52b7f090cdc7070fc1af3f254e8c8d010b1707cad70b9362e7d68f7fa487c9c2`; ELF `codesys3` `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`, 5,181,396 Byte — jeweils **PASS**.

Ich habe zuerst den hashgebundenen WP236-Validator unverändert ausgeführt; Ergebnis **PASS** mit Python 3.13.5 und GNU ARM objdump 2.44. Danach habe ich unabhängig und ausschließlich offline drei separate `objdump -D -z --section=.text --start-address=... --stop-address=...`-Abfragen für exakt die erlaubten Bereiche ausgeführt. `readelf` 2.44 bestätigte `.text` VA `0x7cb10`, Datei-Offset `0x6cb10`; dadurch ist die belegte affine Abbildung `Datei-Offset = ELF-VA − 0x10000` an dieser Sektion verankert. Die Intervallgrenzen liegen vollständig innerhalb `.text`.

| Prüfpunkt | Beobachtung | Status |
|---|---|---|
| Bereich 1 `[0x280000,0x300b10)` | 131.780 lückenlose A32-Wörter | PASS |
| Ausschluss 1 `[0x300b10,0x300e38)` | keine Adresse in den drei disassemblierten Ausgaben | PASS |
| Bereich 2 `[0x300e38,0x301394)` | 343 lückenlose A32-Wörter | PASS |
| Ausschluss 2 `[0x301394,0x3018b8)` | keine Adresse in den drei disassemblierten Ausgaben | PASS |
| Bereich 3 `[0x3018b8,0x344fc0)` | 69.058 lückenlose A32-Wörter | PASS |
| Summe erlaubter Bereiche | 201.181 Wörter / 804.724 Byte | PASS |
| Quelle / WP236-Dateihashes | alle Werte exakt wie Assignment | PASS |

Die Disassemblierung ist eine lineare A32-Bytebereichsabdeckung, nicht der Beweis, dass jedes Wort erreichbarer Code ist. Es wurden keine Adressen außerhalb der drei erlaubten Intervalle abgefragt.

## Adressgebundene Matrix — acht Zielketten

Jede Zeile ist durch den unabhängigen Decode an beiden Endpunkten, den Zielregistervergleich, die VAs und die im WP236-Bericht geschriebenen Datei-Offsets geprüft. `base` ist das adressierte Basisregister des Load-Operanden. Diese Matrix bestätigt die Instruktionskette, nicht einen statisch bekannten Laufzeitwert.

| Nr. | LDR VA / Datei-Offset | BLX VA / Datei-Offset | LDR-Register / Basis | r0-Beobachtung aus Bericht | Prüfung |
|---:|---|---|---|---|---|
| 1 | `0x2b5958 / 0x2a5958` | `0x2b5960 / 0x2a5960` | `r3 / r5` | `mov r0,r6`; kein Weitertragen über opaque Calls | PASS |
| 2 | `0x2b5b78 / 0x2a5b78` | `0x2b5b80 / 0x2a5b80` | `r3 / r3` | `mov r0,r4`; Eingangswert unbekannt | PASS |
| 3 | `0x2b64ac / 0x2a64ac` | `0x2b64b0 / 0x2a64b0` | `r3 / r3` | nicht konstant gesetzter Funktionseingang | PASS |
| 4 | `0x30c810 / 0x2fc810` | `0x30c818 / 0x2fc818` | `r3 / r3` | `ldr r0,[r2,#8]`; Speicherwert unbekannt | PASS |
| 5 | `0x32df5c / 0x31df5c` | `0x32df6c / 0x31df6c` | `r5 / r4` | Literal bei `0x32dfa0`: `0x003ac940`, nicht 15 | PASS |
| 6 | `0x32df78 / 0x31df78` | `0x32df88 / 0x31df88` | `r4 / r4` | Literal bei `0x32dfa4`: `0x003ad1c0`, nicht 15 | PASS |
| 7 | `0x32fc30 / 0x31fc30` | `0x32fc38 / 0x31fc38` | `r3 / r8` | `ldr r0,[r2,#8]`; Speicherwert unbekannt | PASS |
| 8 | `0x32fcec / 0x31fcec` | `0x32fcf4 / 0x31fcf4` | `r3 / r8` | `ldr r0,[r2,#8]`; Speicherwert unbekannt | PASS |

## Adressgebundene Matrix — zwölf unmittelbare `r0=15`-Stellen

Alle zwölf Maschinenwortdekodierungen stimmen mit den im WP236-Bericht aufgeführten bedingten/unbedingten `mov* r0,#15` überein. Die Tabelle gibt den dort behaupteten Offset wieder; der letzte wird zusätzlich als Abweichung ausgewiesen.

| Nr. | VA / berichteter Datei-Offset | Instruktion | Ausschlussbeobachtung im WP236-Bericht | Offsetstatus |
|---:|---|---|---|---|
| 1 | `0x3047d8 / 0x2f47d8` | `movcc r0,#15` | unmittelbarer Epilog | PASS |
| 2 | `0x30485c / 0x2f485c` | `movcc r0,#15` | unmittelbarer Epilog | PASS |
| 3 | `0x3048c8 / 0x2f48c8` | `movhi r0,#15` | Gegenpfad setzt r0 aus r2; danach Epilog | PASS |
| 4 | `0x304934 / 0x2f4934` | `movhi r0,#15` | Gegenpfad setzt r0 aus r3; danach Epilog | PASS |
| 5 | `0x304a90 / 0x2f4a90` | `movne r0,#15` | unmittelbarer Epilog | PASS |
| 6 | `0x3058c4 / 0x2f58c4` | `mov r0,#15` | unmittelbarer Epilog | PASS |
| 7 | `0x305974 / 0x2f5974` | `mov r0,#15` | unmittelbarer Epilog | PASS |
| 8 | `0x30626c / 0x2f626c` | `mov r0,#15` | Branch-/Vergleichspfad geht über `0x3062a8` zum Epilog `0x3062b4`; keine der acht Zielketten in diesem Körper | PASS |
| 9 | `0x312738 / 0x302738` | `movne r0,#15` | Return-Pfad; Gegenpfad überschreibt r0 vor direktem Call | PASS |
| 10 | `0x31860c / 0x30860c` | `mov r0,#15` | Wert gespeichert; r0 überschrieben vor direktem Call | PASS |
| 11 | `0x31e700 / 0x30e700` | `mov r0,#15` | nachfolgendes `movt` ändert Gesamtwert vor direktem Call | PASS |
| 12 | `0x341d30 / 0x340d30` | `mov r0,#15` | Branch zurück; keine der acht Zielketten in diesem Körper | **FAIL** — richtig ist `0x341d30 / 0x331d30` |

## Korrigierte Domäne und Befundsprache

**PASS** — Die WP236-Zieladressen sind unverschobene ELF-VA innerhalb der erlaubten Domain. Es findet sich keine alte Provider-Adresse durch Addition von `0x10000` im akzeptierten Berichtsbefund. Die `+0x10000`-Fehladressierung wurde also nicht übernommen. Die VA→Dateiabbildung ist dagegen an einer Zeile nicht korrekt angewendet: `0x341d30 − 0x10000 = 0x331d30`; `0x340d30` ist falsch.

**PASS** — Nullbefundsprache: der Bericht behauptet keinen Laufzeitbeweis und lässt unbekannte Eingangs-/Speicherwerte **OFFEN**. Die beiden statisch aus Literalen gelesenen Werte wurden unabhängig anhand der Quellbytes im erlaubten Bereich bestätigt. Die zwölf unmittelbaren Konstantenschreibstellen werden als Kandidatenprüfung dargestellt und nicht als Laufzeitbeobachtung.

**OFFEN** — Bei den Zeilen 1–4 der `r0=15`-Tabelle liegt vor dem Rücksprungwort noch eine gegenseitig bedingte `movcs`- bzw. `movls`-Instruktion. Auf dem Pfad, auf dem die `movcc`/`movhi`-Anweisung gesetzt wird, ist diese Gegenbedingung falsch und der Rücksprung folgt. Damit bleibt der Ausschluss inhaltlich konsistent; „unmittelbarer Epilog“ sollte nicht als „nächstes dekodiertes Wort“ gelesen werden.

**HYPOTHESE** — Der fehlerhafte Offset `0x340d30` ist möglicherweise ein Übertragungs-/Tippfehler. Das erklärt die Form, wird aber nicht als Ursache verifiziert.

**OFFEN** — Laufzeitwerte der als unbekannt ausgewiesenen Speicher-/Eingangsquellen, erreichbare Pfade im realen Programm und semantische Bedeutung sind nicht Gegenstand dieser Gegenprüfung. Die unabhängige Prüfung bestätigt keine Geräte- oder Runtime-Eigenschaft.

## Validator und Artefakte

`python3 validate.py` ist der reproduzierbare Prüfer dieser Gegenprüfung; sein Lauf endet mit Exit-Code 0, weil alle Prüfschritte ausführbar waren, gibt aber die zwei inhaltlichen **FAIL**-Abweichungen ausdrücklich aus. Die PASS/FAIL-Entscheidungen sind in der Konsolenausgabe und in `validator-result.txt` festgehalten. Die Eingabe- und Quellenhashes bleiben unverändert. Eigenständige Offlineprüfung; kein unabhängiger Dritt-Review behauptet.
