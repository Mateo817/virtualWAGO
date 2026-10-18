> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-141 — Post-call reads and copyback in `0x002FC530`

## Ergebnis und Status

**VERIFIZIERT (statische Instruktionsbeobachtung):** Im Erfolgszweig liest der Helper fünf Bereiche des von `ComponentEntry` erhaltenen Stackobjekts mit Basis `L = fp - 0x5c` und bildet sie vor der Rückkehr auf Caller-Blockbasis `B = r4` ab: `L+0x00 → B+0x00`, `L+0x04..0x0b → B+0x14..0x1b`, `L+0x0c → B+0x1c`, `L+0x10..0x17 → B+0x24..0x2b`, `L+0x18 → B+0x20`. Falls der kopierte Wert `L+0x0c` ungleich null ist, wird er zusätzlich als Ziel eines optionalen `blx r0` verwendet; dessen Rückgabewert wird separat nach `B+0x0c` geschrieben. Auf dem Fehlerpfad wird unabhängig vom zweiten Helperparameter `3` als Halbwort nach `B+0x2c` geschrieben. `B+0x2e` wird nur auf einem Unterzweig des Erfolgswegs gelesen.

Feld-, API- und Structsemantik wird daraus nicht abgeleitet. Die Bindung des vorangehenden `blx r2` an den aufgelösten `ComponentEntry` stammt aus den mitgegebenen WP-XE164-125 Angaben. Dieser Bericht behandelt den Bereich ab der Rückkehr bei `0x2fc5cc`; die Pre-call-Initialisierung wird nicht erneut analysiert.

## Eingabeidentität und Adressraum

- Binärdatei: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`
- Größe: 5,181,396 Byte
- SHA-256: `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` (erneut geprüft)
- Adressraum: ARM ELF `.text`, virtuelle Adresse; `0x2fc5cc..0x2fc707` inklusive, objdump-Stoppadresse `0x2fc708` exklusiv. Das enthält 79 4-Byte-Instruktionen, die letzte bei `0x2fc704`.
- Übergabebericht: WP-XE164-125 `report.md`, SHA-256 `5008f6d6f1ff8b5259c3a59543bd73e210a655fe1865861a201581d1c5dece16`.
- Übergabe-Disassembly: WP-XE164-125 `function-disassembly.txt`, SHA-256 `de11be1f744ffd81096202a80d8ec0c971049c9cfcd2357c8b47756b738f7621`.

Der neue Ausschnitt mit den tatsächlich verwendeten Instruktionen ist in `post-call-disassembly.txt` enthalten. Er wurde mit folgendem begrenztem Offline-Fallback erzeugt:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Tool: GNU `arm-linux-gnueabihf-objdump` / Binutils 2.44. Der Fallback wurde erst nach der beobachteten REA-Lücke verwendet. Rizin wurde nicht benötigt.

## REA-Versuch und Evidenzaufbewahrung

REA 6.5.0, Ghidra 12.1.4, OpenJDK 21.0.12.1, Linux x86_64 Host; Ziel vom Provider als ARM ELF gebunden. Der gezielte `read_function_instructions(procedure="0x2fc530")`-Aufruf endete nach 300 Sekunden mit `timed out awaiting tools/call`. Das entspricht dem in WP-XE164-125 dokumentierten Ghidra-Startup-Timeout; der gleiche fehlgeschlagene Aufruf wurde nicht wiederholt. Der aktuelle REA-Export `rea-evidence-bundle-current-WP-XE164-141-empty.json` bewahrt den Zustand des neuen Versuchs, hat aber 0 Records und enthält deshalb keine neue Evidence-ID.

Die angeforderte Providerkonfiguration war `provider_id="ghidra"`; ein aktueller Profil-Digest oder ein Funktionsdossier wurde vor dem Timeout nicht zurückgegeben.

Das vorherige REA-Bundle aus WP-XE164-123, auch in WP-XE164-125 mitgeführt, wurde unverändert als `rea-evidence-bundle-upstream-WP-XE164-123-125.json` übernommen (SHA-256 `e4835580ec10347a93f7271d0638cb9bf302f0d4d8eb20d32dba99d49bea5a32`, 8 Records, 0 Unknowns). Die erhaltenen Evidence-IDs sind:

| Evidence-ID | Operation |
| --- | --- |
| `ev_0cf9f4b5877a009c8bf610cc122e9234d1c5da4a1b964fc482a5f05ab100e211` | `analyze_function` |
| `ev_157ab758baa60e437ab6cef9a40f2a3261343163577c633a87d2c70225185515` | `search_bytes` |
| `ev_3255ab9024dd5f9517abcce92366adc81a345307f7ccfb57fbe8b3e9d4681666` | `analyze_function` |
| `ev_460a34c9aa551bceef068e66b01f21bbf2be0362eb055649bbd752d9b0848b5f` | `inspect_native_instruction` |
| `ev_4f2dd15410d2b7317c7e1c0fc0465a2e70aa66ae92ef629b2dc96168fa24d130` | `find_xrefs_to_name` |
| `ev_bc6d54fc1eddcfec46be7b3beb8e8c69576303b809727a975e05bb8dbad87f2f` | `xrefs` |
| `ev_c267eac2bdd4a75459f410e21bc6e7787b1322db3c427f055f0e5660bb6af1b7` | `search_strings` |
| `ev_deabf162e0ffa3eb4279fa240e9d941054498ae47a68fd61916d41e5e84289a3` | `analyze_function` |

Diese Vorgänger-Evidenz stützt die im WP-XE164-125 Bericht dokumentierte Loader-/Caller-Zuordnung. Sie enthält keinen frischen `FUN_002FC530`-Bodyrecord und ersetzt nicht den hier begrenzten ObjDump-Beleg.

## Register- und Basisbezug nach dem Call

Bei Einstieg in den betrachteten Bereich gilt aufgrund des übergebenen Kontextes aus WP-XE164-125: `r4 = B`, die Basis des ursprünglichen Caller-Blocks; `r5` hält den zweiten Helperparameter; `r6 = 0`. Der über `r2` ausgeführte Call ist bereits zurückgekehrt und hat sein Ergebnis in `r0` abgelegt. Der ausgehende Stackobjekt-Basiszeiger beim Call war `L = fp - 0x5c`; die folgende Tabelle verwendet diese Basis nur als Positionsreferenz. Sie weist keine Typen oder fachliche Bedeutung zu.

## Lokale Positionen → Caller-Blockpositionen

| Lokale Position im aufgelösten Call-Objekt `L` | Tatsächlicher Frame-Ausdruck / Zugriff | Caller-Blockposition `B` | Instruktionswirkung |
| --- | --- | --- | --- |
| `L+0x00` (`fp-0x5c`, 4 Byte) | `ldr r2, [fp, #-92]` bei `0x2fc630` | `B+0x00` (4 Byte) | `str r2, [r3], #20` bei `0x2fc640`, mit `r3=B`; Post-Increment ergibt danach `B+0x14`. |
| `L+0x04..L+0x0b` (`fp-0x58..fp-0x51`, 8 Byte) | `vld1.32 {d16}, [r3]` bei `0x2fc634`, `r3=fp-0x58` | `B+0x14..B+0x1b` (2 Wörter) | `vst1.32 {d16}, [r3]` bei `0x2fc644`, `r3=B+0x14`; schreibt die beiden geladenen 32-bit Wörter nach `B+0x14` und `B+0x18`. |
| `L+0x0c` (`fp-0x50`, 4 Byte) | `ldr r0, [fp, #-80]` bei `0x2fc628` | `B+0x1c` (4 Byte) | `str r0, [r4, #28]` bei `0x2fc648`; dieselbe geladene Position wird zuvor bei `0x2fc638` auf Null geprüft und bei Nicht-Null in `0x2fc650` als `blx r0` verwendet. |
| Rückgabewert des optionalen Calls (kein lokaler Objektplatz) | `r0` nach `blx r0` bei `0x2fc650`; wenn der Call übersprungen wird, bleibt `r0=0` aus `L+0x0c` | `B+0x0c` (4 Byte) | `str r0, [r4, #12]` bei `0x2fc660`. |
| `L+0x10..L+0x17` (`fp-0x4c..fp-0x45`, 8 Byte) | `ldrd r2, [fp, #-76]` bei `0x2fc65c` | `B+0x24..B+0x2b` (2 Wörter) | `strd r2, [r4, #36]` bei `0x2fc668`; schreibt nach `B+0x24` und `B+0x28`. |
| `L+0x18` (`fp-0x44`, 4 Byte) | `ldr r1, [fp, #-68]` bei `0x2fc654` | `B+0x20` (4 Byte) | `str r1, [r4, #32]` bei `0x2fc664`. |

Die Offsetrechnung der lokalen Referenzbasis ist direkt: `L=fp-0x5c`; daher sind `fp-0x58=L+0x04`, `fp-0x50=L+0x0c`, `fp-0x4c=L+0x10` und `fp-0x44=L+0x18`. Für `B` gilt `r4` als gespeicherte Blockbasis; Adressdisplacements sind die unmittelbar beobachteten `str`/`vst1`-Offsets. Die Reihenfolge der Stores ist `B+0x00`, `B+0x14..0x1b`, `B+0x1c`, optionaler Call, danach `B+0x0c`, `B+0x20`, `B+0x24..0x2b`.

## Guards, Pfade und Rückgaben

1. **Nicht-Null-Ergebnis des ursprünglichen Calls (`0x2fc5cc..0x2fc628`).** `cmp r0,r6; beq 0x2fc628` nimmt nur bei Null den Copyback-Pfad. Bei Nicht-Null wird unbedingt `3` als Halbwort nach `B+0x2c` geschrieben (`0x2fc5d8..0x2fc5dc`). Dann wird `r5` geprüft. Bei `r5==0` wird `1` zurückgegeben und der Helper kehrt direkt zurück (`0x2fc5e0..0x2fc5ec`). Bei `r5!=0` folgt `LogAdd` bei `0x2fc618`, danach Rückgabe `1` (`0x2fc61c..0x2fc624`). Dieser Fehlerpfad liest keine der oben aufgelisteten Objektpositionen.

2. **Null-Ergebnis und Copyback (`0x2fc628..0x2fc668`).** `L+0x00`, `L+0x04..0x0b` und `L+0x0c` werden gelesen/kopiert. Wenn `L+0x0c==0`, `beq 0x2fc654` überspringt den optionalen indirekten Call und `r0` bleibt null. Wenn der Wert nicht null ist, `blx r0` bei `0x2fc650` ruft ihn auf. In beiden Fällen folgt danach der Store des aktuellen `r0` nach `B+0x0c`; anschließend werden `L+0x18` und `L+0x10..0x17` nach `B+0x20` und `B+0x24..0x2b` kopiert.

3. **Zweiter Helperparameter null (`0x2fc658..0x2fc6ec`).** `beq 0x2fc6e4` überspringt die Prüfung von `B+0x2e` und beide Logging-/String-Hilfsaufrufe. Der Helper gibt `0` zurück.

4. **Zweiter Helperparameter nicht null (`0x2fc670..0x2fc6e0`).** `ldrh r3,[r4,#46]` liest nur hier `B+0x2e`; `ands r3,r3,#2` prüft Bitmaske `0x2`. Ist das Ergebnis null, schreibt `strbeq` den Bytewert null in die lokale temporäre Position `fp-0x70`, dann wird `LogAdd` bei `0x2fc6e0` aufgerufen. Ist das Ergebnis nicht null, `bne 0x2fc6f0` ruft zuerst `CMUtlSafeStrCpy` bei `0x2fc700` mit lokalem Ziel `fp-0x70` und Längenoperand `20` auf; anschließend springt `0x2fc704` zurück zu `0x2fc684` und führt denselben `LogAdd`-Aufbau aus. Beide Unterzweige kehren bei `0x2fc6e4..0x2fc6ec` mit `0` zurück.

Die Diagnosetemporäre `fp-0x70` ist kein Copyback in `B`: sie wird durch `strbeq` initialisiert und als Argument für `CMUtlSafeStrCpy` beziehungsweise `LogAdd` verwendet. Die Helper-Instruktionen nach dem Copyback enthalten keine weiteren direkten Stores in Caller-Positionen `B+0x00..B+0x2b`; auf dem Erfolgsweg wird `B+0x2e` gelesen. Die beobachteten Storepositionen `B+0x2c` und die Erfolgsstores sind disjunkte Pfadbereiche. Auswirkungen innerhalb der indirekt oder direkt gerufenen Callee-Bodies sind außerhalb des Umfangs.

## Direkte Effekte und Abgrenzung

- Caller-Block-Stores: Fehlercode-Halbwort nach `B+0x2c`; Erfolgsstores nach `B+0x00`, `B+0x0c`, `B+0x14..0x1c` und `B+0x20..0x28` gemäß Tabelle.
- Caller-Block-Read: Halbwort `B+0x2e`, ausschließlich bei Null-Ergebnis des ursprünglichen Calls und `r5!=0`.
- Weitere Caller-Block-Reads nur im Logging-Unterzweig: Wörter `B+0x00`, `B+0x04`, `B+0x0c` an `0x2fc68c`, `0x2fc694` und `0x2fc684`. Diese Reads sind nicht Teil der Stackobjekt→Copyback-Tabelle.
- Calls innerhalb des Bereichs: optionales indirektes `blx r0` (`0x2fc650`), direktes `LogAdd` (`0x2fc618`, `0x2fc6e0`) und bedingtes `CMUtlSafeStrCpy` (`0x2fc700`). Callee-Bodies wurden nicht verfolgt.
- Der `+0x10`-basierte `blx r2` liegt vor dem angeforderten Anfang und wird hier nicht neu untersucht. Der Helper endet nach dem Rücksprung `0x2fc6ec`; der alternative Erfolgsunterzweig bei `0x2fc704` springt zurück in den Helper und erreicht danach denselben Rücksprung.

## Alternativerklärung und Restunsicherheit

Die lokale Referenz `L` ist hier per Call-Site-Registerwert auf `fp-0x5c` verankert. Die Lage und Bytebreite jeder Kopie folgen den adressierten ARM-Instruktionen; die Bezeichnung „Objekt“ ist keine Behauptung über ein C-/C++-Structlayout. Der Wert an `L+0x0c` wird als indirektes Ziel verwendet, aber sein API-Vertrag bleibt unbekannt. Die Bezeichnung `ComponentEntry` ist eine Übergabezuordnung aus WP-XE164-125, nicht aus den Post-call-Instruktionen selbst. Statische Instruktionen belegen nicht, dass jeder Guard-Zweig zur Laufzeit erreicht wird. Ghidra lieferte für diesen Auftrag wegen des 300-s-Timeouts keine frische Instruktions-Evidence.

## Tests und Self-Review

- Tests: **NOT_RUN** (keine Softwaretests angefordert; Paket-Validator ist eine Reproduzierbarkeits-/Konsistenzprüfung des Artefaktausschnitts, kein Produkt-Test).
- Self-Review: durchgeführt. Alle Instruktionen im abgegrenzten Fenster, alle direkten Kontrollflussziele und die Rückkehrpfade wurden gegen den begrenzten ObjDump-Ausschnitt abgeglichen. Keine unabhängige Prüfung behauptet.
- Reproduzierbarer Validator: `semantic_validator.js`. Ausführung aus diesem Ordner: `node semantic_validator.js`. Er prüft Eingabe-SHA, Binutils-Version, den erneut erzeugten begrenzten Assembly-Ausschnitt, die lückenlose 79-Instruktions-Adressfolge und definierte Copyback-/Guard-Operanden.

## Dateien und Hashes

`SHA256SUMS` enthält SHA-256 für alle Paketdateien außer sich selbst. Dateien außerhalb von `WP-XE164-141` wurden nicht geändert; keine Geräte-, Netzwerk-, VM- oder Laufzeitoperationen wurden ausgeführt.
