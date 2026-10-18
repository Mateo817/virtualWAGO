> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-142 — `CMLoadComponent3` post-helper consumer lane

## Ergebnis

**VERIFIZIERT als statischer Caller-Befund:** Nach Rückkehr von `0x002FC530` vergleicht `CMLoadComponent3` `r0` mit null und speichert das Rückgabewort bei `0x2FFD4C` unbedingt nach `[fp-0x5c]`. Erst danach entscheidet `0x2FFD50`: Nichtnull springt zum Rückgabe-/Ausgabepfad `0x2FFDD4`; nur Null erreicht die beiden Block-Consumer. Der Caller liest Basis `fp-0x58`, zuerst Position `+0x14` (`[fp-0x44]`), dann `+0x18` (`[fp-0x40]`). Jedes Wort wird als indirektes Ziel nur dann aufgerufen, wenn es ungleich null ist. Bei beiden Calls steht `r3` auf dem Ziel und `r0` ist auf dem durch Kontrollfluss erreichten Call-Punkt null. Der Caller richtet zwischen Rückkehr des Helpers und diesen Calls keine neuen Argumente in `r1`/`r2` oder auf dem Stack ein. Deren Werte sind daher aus dieser Lane nicht verifizierbar; nach AAPCS sind `r1` und `r2` zudem volatile über den Helper- bzw. ersten indirekten Call.

Nach jedem ausgeführten indirekten Call prüft `cmp r0,#0` dessen Rückgabewort. Ein Nichtnullwert verzweigt zu `0x2FFDE8`; dort wird, falls der ursprüngliche Ausgabezeiger `r5` nicht null ist, Null nach `*r5` geschrieben, anschließend kehrt der Pfad über `0x2FFCC4` mit `r4` zurück. Ein Nullziel überspringt den jeweiligen Call. Ein Null-Callresultat oder übersprungener Call führt zum nächsten Consumer. Wenn beide Pfade passieren, folgen `CMCallHook` und `CMAddComponent`.

Die Rohwerte der beiden Zielpositionen sind ohne Laufzeitdaten nicht bekannt. Der übergebene Helper-Report beschreibt die von `0x2FC530` geschriebenen Blockpositionen `+0x14` und `+0x18` als zwei 32-bit Wörter aus dessen lokalem Objekt; dieser Bericht wird hier nur als begrenzter Helper-Kontext verwendet, nicht als neuer Helper-Befund. Die Caller-Instruktionen belegen die Loads, Guards und Calls unabhängig davon.

## Identität, Grenzen und Adressrechnung

- Ziel: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`, 5,181,396 Byte, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`; ELF32 little-endian ARM.
- WP-XE164-123 Caller-Kontext: `report.md`, SHA-256 `b96bf455d44125ed91835119399cd90fd04410888e74ee48afaf3525a4b513ee`; REA-Bundle, SHA-256 `e4835580ec10347a93f7271d0638cb9bf302f0d4d8eb20d32dba99d49bea5a32`.
- WP-XE164-125 Helper-Kontext: `report.md`, SHA-256 `5008f6d6f1ff8b5259c3a59543bd73e210a655fe1865861a201581d1c5dece16`.
- Procedure-Grenze aus Caller-Disassembly: `0x2FFC84..0x2FFE07` einschließlich; betrachtete Post-Helper-Lane beginnt beim Rückkehrpunkt `0x2FFD48` nach dem `bl 0x2FC530` bei `0x2FFD44`.
- Prologrechnung: `0x2FFC84` kopiert `sp` nach `ip`; Push umfasst `pc`, dann setzt `0x2FFC8C` `fp = ip - 4`. `0x2FFD00` bildet `r2 = fp - 0x58`, und `0x2FFD04` bildet `r0 = fp - 0x58`; dies ist die an den Helper übergebene Blockbasis. Für jede Position gilt Adresse = `fp - 0x58 + Offset`: `+0x10 = fp-0x48`, `+0x14 = fp-0x44`, `+0x18 = fp-0x40`. `0x2FFD08` setzt vor dem Helper `r1=1`. Die Rückkehr kann `r1`/`r2` überschreiben.
- Vor-Helper-Lane wurde nur bis zur Blockbasis und Helper-Aufrufadresse für diese Rechnung verwendet.
- In der hier betrachteten Post-Helper-Lane wird Position `+0x10` nicht erneut geladen; der Caller liest als indirekte Ziele nur `+0x14` und `+0x18`.

## Caller-Block-Consumer nach Helper-Rückkehr

| Blockposition / Wert | Exakte Caller-Lesestelle | Verwendung und Kontrollfluss |
| --- | --- | --- |
| Helper-Rückgabe `r0` | `0x2FFD48`, `0x2FFD4C`, `0x2FFD50` | `cmp r0,#0`; unconditionaler Store des Werts nach `[fp-0x5c]`; danach branch. Nichtnull geht zu `0x2FFDD4`, Null erreicht die zwei indirekten Calls. Der gespeicherte Wert wird später bei `0x2FFDB0` gelesen. |
| `+0x14` = `[fp-0x44]` | `0x2FFD54` | Wort in `r3`; `cmp r3,#0`; Null verzweigt zu `0x2FFD6C`; Nichtnull wird bei `0x2FFD60` als `blx r3` aufgerufen. |
| Resultat des Calls aus `+0x14` | `0x2FFD64` | `cmp r0,#0`; Nichtnull verzweigt zu Fehlerpfad `0x2FFDE8`; Null geht weiter. |
| `+0x18` = `[fp-0x40]` | `0x2FFD6C` | Wort in `r3`; `cmp r3,#0`; Null verzweigt zu `0x2FFD84`; Nichtnull wird bei `0x2FFD78` als `blx r3` aufgerufen. |
| Resultat des Calls aus `+0x18` | `0x2FFD7C` | `cmp r0,#0`; Nichtnull verzweigt zu Fehlerpfad `0x2FFDE8`; Null geht weiter. |
| Blockbasis `fp-0x58` | `0x2FFD9C` | Als `r0` an `CMAddComponent` bei `0x2FFDA0` übergeben, nachdem `CMCallHook` erfolgreich zurückgekehrt ist. Keine Feld-/API-Semantik wird daraus abgeleitet. |
| lokaler Status `[fp-0x5c]` | `0x2FFDB0` | Nach `CMAddComponent` nach `r7` geladen; `r7!=0` verzweigt zu `0x2FFDF8`, sonst wird `CMGetAPI` aufgerufen. |
| Ausgabezeiger `r5` | `0x2FFDC8`, `0x2FFDD4`, `0x2FFDE8`, `0x2FFDF8` | Je nach Pfad Nullprüfung; Stores an `*r5` nur bei `r5!=0`. |

### Register-/Stackwerte am indirekten Aufruf

| Aufruf | Zielregister | `r0` | `r1`, `r2` | Stack / Ergebnis |
| --- | --- | --- | --- | --- |
| `0x2FFD60: blx r3` | `r3 = *(fp-0x44) = Block[+0x14]`, nach Guard ungleich null | Null: der Helperstatus wurde bei `0x2FFD48` auf Null verglichen; nur der Nullzweig erreicht `0x2FFD54..60`. | In dieser Lane nicht neu gesetzt; nach Helper-Rückkehr nicht belegt. | Caller bereitet keine neuen Stackargumente vor. Rückgabewert in `r0`; Null fährt fort, Nichtnull geht zu `0x2FFDE8`. |
| `0x2FFD78: blx r3` | `r3 = *(fp-0x40) = Block[+0x18]`, nach Guard ungleich null | Null: entweder der erste Zielslot war Null (Call übersprungen) oder dessen Callresultat war Null. | In dieser Lane nicht neu gesetzt; der erste indirekte Call darf sie ebenfalls clobbern. | Caller bereitet keine neuen Stackargumente vor. Rückgabewert in `r0`; Null fährt fort, Nichtnull geht zu `0x2FFDE8`. |

„Keine neuen Stackargumente“ ist eine Beobachtung dieser Caller-Lane, kein Beweis über eine vollständige unbekannte Signatur oder ABI-Konvention des indirekten Ziels.

## Vollständige Instruktionstabelle der Post-Helper-Lane

GNU ARM objdump-Ausgabe, Adressgrenze inklusive bis `0x2FFE07`. Die annotierten Abzweige geben die beobachteten ARM-Bedingungen wieder.

| Adresse | Instruktion | Effekt im betrachteten Datenfluss |
| --- | --- | --- |
| `0x2FFD48` | `cmp r0, #0` | Vergleicht Helper-Rückgabe. |
| `0x2FFD4C` | `str r0, [fp, #-92]` | Speichert den Helperstatus unbedingt bei `fp-0x5c`, sowohl für Null- als auch Nichtnullpfad. |
| `0x2FFD50` | `bne 0x2FFDD4` | Nichtnull-Helperstatus wechselt nach dem Store zum Rückgabe-/Ausgabepfad; Null läuft zu den Zielslot-Loads. |
| `0x2FFD54` | `ldr r3, [fp, #-68]` | Liest Block `+0x14` in `r3`. |
| `0x2FFD58` | `cmp r3, #0` | Guard für erstes indirektes Ziel. |
| `0x2FFD5C` | `beq 0x2FFD6C` | Nullziel überspringt ersten Call. |
| `0x2FFD60` | `blx r3` | Ruft erstes Ziel auf; `r0` ist null, `r1/r2` nicht durch diesen Caller neu gesetzt. |
| `0x2FFD64` | `cmp r0, #0` | Testet erstes Callresultat. |
| `0x2FFD68` | `bne 0x2FFDE8` | Nichtnullresultat geht auf Fehlerpfad. |
| `0x2FFD6C` | `ldr r3, [fp, #-64]` | Liest Block `+0x18` in `r3`. |
| `0x2FFD70` | `cmp r3, #0` | Guard für zweites indirektes Ziel. |
| `0x2FFD74` | `beq 0x2FFD84` | Nullziel überspringt zweiten Call. |
| `0x2FFD78` | `blx r3` | Ruft zweites Ziel auf; `r0` ist null, `r1/r2` sind nicht belegt. |
| `0x2FFD7C` | `cmp r0, #0` | Testet zweites Callresultat. |
| `0x2FFD80` | `bne 0x2FFDE8` | Nichtnullresultat geht auf Fehlerpfad. |
| `0x2FFD84` | `mov r3, #0` | Bereitet Nullwert vor. |
| `0x2FFD88` | `mov r1, r6` | Setzt zweites Argument des folgenden direkten Calls. |
| `0x2FFD8C` | `mov r2, r3` | Setzt drittes Argument auf Null. |
| `0x2FFD90` | `mov r0, #25` | Setzt erstes Argument auf 25. |
| `0x2FFD94` | `bl 0x2FECC4` | Direkter Aufruf `CMCallHook`. |
| `0x2FFD98` | `sub r1, fp, #92` | Setzt `r1=fp-0x5c`. |
| `0x2FFD9C` | `sub r0, fp, #88` | Setzt `r0=Blockbasis fp-0x58`. |
| `0x2FFDA0` | `bl 0x2FD0F0` | Ruft `CMAddComponent` auf. |
| `0x2FFDA4` | `cmn r0, #1` | Prüft Resultat gegen `-1`. |
| `0x2FFDA8` | `mov r6, r0` | Bewahrt Resultat in `r6`. |
| `0x2FFDAC` | `beq 0x2FFDF8` | Resultat `-1` wechselt zum bedingten Ausgabestore. |
| `0x2FFDB0` | `ldr r7, [fp, #-92]` | Liest Helperstatus aus `[fp-0x5c]`. |
| `0x2FFDB4` | `cmp r7, #0` | Prüft gespeicherten Helperstatus. |
| `0x2FFDB8` | `bne 0x2FFDF8` | Nichtnullstatus wechselt zum Ausgabepfad. |
| `0x2FFDBC` | `sub r0, fp, #88` | Setzt `r0=Blockbasis`. |
| `0x2FFDC0` | `mov r4, r6` | Kopiert `CMAddComponent`-Resultat nach `r4`. |
| `0x2FFDC4` | `bl 0x2FE37C` | Direkter Call `CMGetAPI`. |
| `0x2FFDC8` | `cmp r5, #0` | Guard für Ausgabezeiger. |
| `0x2FFDCC` | `strne r7, [r5]` | Falls `r5!=0`, speichert `r7` (hier nach Nulltest Null) an `*r5`. |
| `0x2FFDD0` | `b 0x2FFCC4` | Gemeinsamer Rückgabepfad. |
| `0x2FFDD4` | `cmp r5, #0` | Nichtnull-Helperstatuspfad; prüft Ausgabezeiger. |
| `0x2FFDD8` | `strne r0, [r5]` | Falls `r5!=0`, speichert den Helperstatus an `*r5`. |
| `0x2FFDDC` | `mov r0, r4` | Setzt Rückgaberegister auf `r4`. |
| `0x2FFDE0` | `sub sp, fp, #32` | Epilog-Stackwiederherstellung. |
| `0x2FFDE4` | `ldm sp, {r4, r5, r6, r7, r8, fp, sp, pc}` | Stellt Register wieder her und kehrt zurück. |
| `0x2FFDE8` | `cmp r5, #0` | Indirekter-Call-Fehlerpfad; prüft Ausgabezeiger. |
| `0x2FFDEC` | `movne r3, #0` | Falls `r5!=0`, bereitet Null vor. |
| `0x2FFDF0` | `strne r3, [r5]` | Falls `r5!=0`, speichert Null an `*r5`. |
| `0x2FFDF4` | `b 0x2FFCC4` | Springt zum Pfad, der `r4` nach `r0` lädt und zurückkehrt. |
| `0x2FFDF8` | `cmp r5, #0` | Alternativer Ergebnis-/Statuspfad; prüft Ausgabezeiger. |
| `0x2FFDFC` | `ldrne r3, [fp, #-92]` | Falls `r5!=0`, liest gespeicherten Helperstatus. |
| `0x2FFE00` | `strne r3, [r5]` | Falls `r5!=0`, speichert Helperstatus an `*r5`. |
| `0x2FFE04` | `b 0x2FFCC4` | Gemeinsamer Rückgabepfad. |

## Toolweg und Evidenzgrenzen

- REA 6.5.0 war verbunden; Session-Status zunächst geschlossen. Ziel mit `open_binary(provider_id="ghidra")` geöffnet; REA meldete ELF / ARM und den erwarteten SHA-256.
- `read_function_instructions("0x2ffc84")` wurde genau einmal aufgerufen und endete nach 300 s mit `timed out awaiting tools/call`. Diese Operation wurde nicht wiederholt. Ghidra 12.1.4 / Linux x64; Profil-Digest des gebundenen vorherigen REA-Kontexts `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Begrenzter GNU-Fallback: `arm-linux-gnueabihf-objdump` GNU Binutils 2.44, Argumente `-d --start-address=0x2ffc84 --stop-address=0x2ffe08 <codesys3>`. Die Disassemblierung umfasst genau die Procedure-Ausschnittgrenze bis exklusiv `0x2FFE08`; letztes Tabellenwort bei `0x2FFE04` ist 4 Byte.
- Die mitgelieferte WP-XE164-123 REA-Bundle-Datei wurde bytegleich als `rea-evidence-bundle.json` übernommen; darin bleiben acht vorhandene Evidence-IDs erhalten (`ev_0cf9…`, `ev_157a…`, `ev_3255…`, `ev_460a…`, `ev_4f2d…`, `ev_bc6d…`, `ev_c267…`, `ev_deab…`). Das Bundle enthält Vorgängerbefunde, keinen erfolgreichen REA-Record aus diesem WP. Keine neuen REA-Evidence-IDs werden behauptet.
- Beobachtung: Caller-Assembly, Bedingungen, Loads, Calls, lokale Stores und Branches oben.
- Schlussfolgerung: Die zwei indirekten Ziele stammen callerseitig aus Basisoffsets `+0x14` und `+0x18`; ihre tatsächlichen Werte und die Semantik der Ziele sind unbekannt.
- Unbekannt: Laufzeitwerte, indirekte Callee-Bodies, vollständige Callee-Signaturen, Werte in `r1/r2` an den Calls und mögliche semantische Funktion der Wörter. Der Analysebereich verfolgt keine indirekten Callees.
- Alternative: Die zwei Wörter können zur Laufzeit null sein und die Calls auslassen; andernfalls können unbekannte Zielkonventionen Register oder Stackbereiche zusätzlich nutzen. Der statische Caller allein entscheidet das nicht.
- Restunsicherheit: GNU disassembly ist der begrenzte Fallback nach REA-Timeout; kein frischer Ghidra-Instruktionsrecord und keine Laufzeitbeobachtung. Die Vorgängerberichte liefern nur akzeptierten Caller-/Helper-Kontext.

## Status und Dateiliste

- Tests: **NOT_RUN**; keine Softwaretests angefordert. Artefakt-Validator: **PASS** (siehe `validator-result.txt`).
- Ergebnisstatus: Call-Zielpositionen, Nullguards und Resultatbranches **VERIFIZIERT** als statische Caller-Beobachtungen; Laufzeitwerte **OFFEN**.
- Self-Review: durchgeführt. Keine unabhängige Review oder Worker-Ausführung behauptet.
- Kein Pseudocode erzeugt; Schlussfolgerungen beruhen auf der tabellierten statischen Instruktionsfolge.
- Paketdateien: `report.md`, `rea-evidence-bundle.json` (bytegleiche WP-123-Kopie), `semantic_validator.js`, `validator-result.txt`, `SHA256SUMS`.
