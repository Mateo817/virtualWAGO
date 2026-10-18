> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-136 — exakter Körper `CMGetComponent` bei `0x002FC820`

## Ergebnis

**VERIFIZIERT — statischer Binary-Befund:** Der exakte Ghidra-Einstieg `CMGetComponent` hat einen zusammenhängenden Funktionskörper von `0x002FC820` bis einschließlich `0x002FC8A7`, also 136 Byte bzw. 34 ARM-Instruktionen. Der Körper sichert das eingehende `r0`, ruft `MemPoolLock( *(uint32_t *)0x00510868 )` auf und durchsucht eine über das Wort bei `0x00510868` plus Offset `0x1C` erreichbare verkettete Folge. Es wird jeweils das Wort bei Listenelement `+0x10` mit dem gesicherten Eingangswert verglichen. Bei Treffer ruft der Körper `MemPoolUnlock()` auf und gibt `element+0x10` in `r0` zurück. Bei Listenende ruft er ebenfalls `MemPoolUnlock()` auf und gibt `0` zurück. Im Funktionskörper ist kein direkter Store in globale oder Listendaten sichtbar; Stack-Sicherung/-Wiederherstellung und die beiden Callee-Aufrufe sind separat zu berücksichtigen.

**HYPOTHESE — nur konditional auf WP134-Callerwerte angewandt:** Falls an den in WP134 beschriebenen Aufrufen von `0x002FC820` tatsächlich `r0=0x10062001` anliegt, vergleicht dieser Körper diesen Wert gegen jedes gelesene Wort an Listenelement `+0x10`. Bei Treffer ist der beobachtete Rückgabewert die Adresse dieses Wortes (`element+0x10`); ohne Treffer ist er `0`. Das sagt weder aus, dass `0x10062001` ein Pointer oder eine bestimmte Identität ist, noch ob ein Treffer vorliegt. WP134 beschreibt zwei Aufrufe; die Bindung des WP132-Werts an diese Laufzeitaufrufe bleibt konditional und wird hier nicht eigenständig nachanalysiert.

## Identität, Adresse und Toolkonfiguration

| Gegenstand | Beobachtung |
|---|---|
| Binary | `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3` |
| Binary-Größe / SHA-256 | 5,181,396 Byte / `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` |
| WP134-Kontextbericht SHA-256 | `04efe7e92aa3ea89561fc9d41a9ea500f372386d9789f6e0f5b0d7a8eab60474` |
| ELF | ELF32, little-endian, `ET_EXEC`, ARM, EABI5 hard-float |
| Adressräume | Ghidra Default-Space-Adresse = ELF-Link-VA für den beobachteten Code. Das erste `PT_LOAD` bildet `p_offset=0` auf `p_vaddr=0x10000` ab; somit Dateioffset = VA − `0x10000` für diesen Funktionsbereich. |
| Bereich | Ghidra / ELF-Link-VA `0x002FC820..0x002FC8A7` inkl.; Datei `0x002EC820..0x002EC8A7` inkl.; 136 Byte |
| Provider | Ghidra 12.1.4 über REA 6.5.0, Linux x86-64 Host, Java 21.0.12.1; ARM/ELF Import, ephemeral immutable source, Ghidra-default Analyzer-Preset |
| Profil-Digest | `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de` |

REA öffnete genau das angegebene ELF und bestätigte den SHA-256. Ghidra meldet am exakten Einstieg die Funktion `CMGetComponent`, `external=false`, `thunk=false`, zusammenhängende Body-AddressSet `0x2fc820..0x2fc8a7`, `total_bytes=136`, `span_bytes=136`, `basicblock_count=8`. Adressen in diesem Bericht sind keine Dateioffsets, außer wenn die Dateioffset-Spalte ausdrücklich genannt ist.

## Vollständige Instruktionsabdeckung

Ghidra `procedure_assembly` lieferte eine Instruktion an jeder 4-Byte-Adresse von `0x2fc820` bis `0x2fc8a4`, insgesamt 34 Einträge. Die letzte Instruktion ist vier Byte lang und endet bei `0x2fc8a7`, passend zur inklusiven Ghidra-Range. Die folgende vollständige Liste ist Ghidra-Listing-Text, nicht Originalquelltext:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

## Register-, Kontroll- und Rückgabefluss

- **Eingang:** `0x2fc834` kopiert eingehendes `r0` in das gesicherte Register `r4`; der Vergleich verwendet dieses gesicherte Wort bei `0x2fc868`. Im Funktionskörper wird kein weiteres eingehendes Register als Parameter erhalten. Die Ghidra-Signatur `undefined CMGetComponent()` ist keine belastbare Parameterdeklaration; der Pseudocode leitet `int param_1` ab. Beides bleibt Werkzeugdarstellung.
- **Pool-/Listenquelle:** `movw/movt` bei `0x2fc828/0x2fc82c` bilden `r5=0x00510868`. `0x2fc838` lädt das Wort `[0x00510868]` in `r0` und übergibt es an den direkten Call `MemPoolLock` bei `0x2fc83c`. Nach dem Call wird das Wort erneut bei `0x2fc840` geladen. `0x2fc848` lädt `[r0+0x1C]` als möglichen Startknoten in `r1`.
- **Suche:** `r3` startet als Nullwert. Bei `0x2fc870..0x2fc884` wird, falls noch kein Knoten vorliegt, `r1` als Startknoten gewählt; bei Listenende (`r1==0`) geht der Pfad nach `0x2fc888`. Für einen vorhandenen Knoten vergleicht `0x2fc864/0x2fc868` `[r3+0x10]` mit gesichertem Eingangs-`r0` (`r4`). Bei Ungleichheit führt `0x2fc874` über `0x2fc850` zur nächsten Kante `[r3]` und die Schleife wiederholt sich.
- **Treffer:** Der Gleichheitssprung von `0x2fc86c` führt nach `0x2fc898`; dort wird `r4=r3+0x10` gebildet, bei `0x2fc89c` `MemPoolUnlock()` aufgerufen, anschließend `r0=r4` gesetzt und mit `0x2fc8a4` zurückgekehrt. Rückgabe ist damit `Knotenadresse+0x10`, also dieselbe Adresse, deren Inhalt verglichen wurde, nicht der gelesene Inhalt.
- **Kein Treffer:** `0x2fc888` setzt `r4=r2` (am Listenende `r2=0`), ruft bei `0x2fc88c` `MemPoolUnlock()` auf, setzt bei `0x2fc890` `r0=r4` und kehrt bei `0x2fc894` zurück. Rückgabewert ist `0`.
- **Seiteneffekte des Körpers:** explizite direkte Loads aus der genannten globalen Stelle und der über Zeiger erreichbaren Liste; Stack-Sicherung und -Wiederherstellung; zwei direkte Unlock-Callsites auf demselben Ziel. Keine direkte Store-Instruktion im Funktionskörper. Zusätzliche Callee-Wirkungen oder Alias-/Nebenwirkungen außerhalb des sichtbaren Körpers sind nicht ausgeschlossen und wurden nicht rekursiv untersucht.

## Direkte Calls und Datenreferenzen

| Quelle | Ziel / Operand | Befund |
|---|---|---|
| `0x2fc838` | Wort an `0x00510868` | Ghidra-Referenz `READ`; das geladene Wort geht in `r0` für den folgenden Call. |
| `0x2fc83c` | `0x0017F1A4` (`MemPoolLock`) | Direkter, aufgelöster Call. Das am Aufruf anliegende `r0` stammt aus `[0x00510868]`. |
| `0x2fc840` | Wort an `0x00510868` | Ghidra-Referenz `READ`; der geladene Wert ist Basispointer für den Folgeload. |
| `0x2fc848` | `[r0+0x1C]` | Maschinenoperand liest Offset `+0x1C` relativ zum soeben geladenen Basispointer. Ghidras ReferenceManager führt für diese Instruktion eine `READ`-Referenz mit Ziel `0x1B`; diese Analyzer-Referenz wird hier nicht als eigenständige absolute Datenvariable bei `0x1B` interpretiert. |
| `0x2fc850` | `[r3]` | Laufzeitabhängiger Folgeknoten-Load; kein statisch auflösbarer absoluter Zielwert. |
| `0x2fc864` | `[r3+0x10]` | Laufzeitabhängiger Knotenfeld-Load für den Vergleich; kein statisch auflösbarer absoluter Zielwert. |
| `0x2fc88c`, `0x2fc89c` | `0x0017F108` (`MemPoolUnlock`) | Zwei direkte, aufgelöste Calls, je einer pro Rückgabepfad. |
| kompletter Body | — | Kein direkter Speicher-Store in globale oder Listendaten; direkte ausgehende Data-Refs umfassen nur die gelesene globale Stelle / die vom Analyzer projizierte `+0x1C` Referenz. Keine unaufgelösten Calls wurden im vollständigen Referenzergebnis gemeldet. |

Die Callee-Namen und Adressen sind Ghidra-Funktionsidentitäten im selben ELF. Ihre Bodies wurden nicht dekompiliert oder rekursiv analysiert; deren Verhalten ist daher nicht Teil dieses Befunds. Insbesondere wird die Semantik von „Lock“, „Unlock“, „Pool“ oder „Component“ nicht über Instruktionsfluss und beobachtete Symbolnamen hinaus erweitert.

## Konditionale Bindung des WP134-Werts

WP134 dokumentiert zwei Callsites zu `CMGetComponent` im Körper `0x30066C..0x3007BF`: `0x300740` und `0x300784`. Im dokumentierten Caller wird jeweils `r0` unmittelbar vor dem Call aus gesichertem `r7` gesetzt; `r7` enthält dort den eingehenden `r0` des Callers. WP134 übernimmt aus WP132 für diese Stelle `r0=0x10062001`. Falls dieser Registerwert an genau der jeweiligen Callsite gilt, empfängt der hier untersuchte Körper daher `0x10062001` in `r0`. Dann wird dieser 32-Bit-Wert an jeder Iteration mit `[node+0x10]` verglichen und nicht als Argument an `MemPoolLock` weitergereicht. Der Aufruf an `MemPoolLock` erhält stattdessen `[0x00510868]` in `r0`.

Diese Verknüpfung ist ausdrücklich **HYPOTHESE/konditional**: ein statischer Registerfluss im WP134-Caller und die dort überlieferte Laufzeitbeobachtung beweisen nicht ohne Weiteres, dass die WP132-Werte bei den zwei Calls zu `0x2FC820` anlagen. Dieser Worker analysiert keine weiteren Caller und keine Identitäts-/Pointersemantik.

## Evidence, Methodenlücke und Grenzen

REA zuerst: `open_binary` band das angegebene Binary; anschließend wurden Ghidra `procedure_info`, `procedure_assembly`, `procedure_pseudo_code`, `procedure_references(direction=outgoing)` und `procedure_callees` für ausschließlich den exakten Einstieg `0x2FC820` gelesen. Vollständiger breiter REA-Dossieraufruf `analyze_function(0x2FC820)` überschritt 300 Sekunden und endete mit `timed out awaiting tools/call after 300s`. Dieser identisch fehlgeschlagene Request wurde nicht wiederholt. Die getrennten REA-Facetten lieferten Funktionsrange, vollständige Assembly, Pseudocode, Referenztypen und aufgelöste Callziele; daher wurde kein Disassembler-Fallback benötigt.

| REA-Evidence | Inhalt |
|---|---|
| `ev_eda25bb2c26344c835786288aeb08447b6e61d5aa3f05b66b072cb32dd6c3805` | Ghidra-Funktionsidentität, exakte vollständige Range, Umfang, Basicblockanzahl, Classification |
| `ev_c0c9a04ebeac2dc2a055fa1871f8de25336b6a40c2d3a11f9e6c52f5c92043a0` | vollständige Ghidra-Assembly |
| `ev_b44145d6fbaa6ac4faec4f56aca78f6b5b8b8dcd4931ee5ef29720d47f5413c1` | Ghidra-Pseudocode, ausdrücklich Decompilerableitung |
| `ev_d5acc55a898b897fde7313d8e9e0963e020c4d4e4aaf398d128438ba19bd21dc` | direkte ausgehende Referenzen mit Ghidra-Referenztypen und Zielen |
| `ev_07220a732b7fde457038157efd669bfe3b487ec95279b308e1a8d21e3e59a41e` | direkte Callee-Adressen und Coverage-Hinweis zu ungelösten indirekten Calls |

**Alternativerklärungen / Restunsicherheit:** `MemPoolLock`/`MemPoolUnlock`-Namen sind Labels und keine vollständigen Verträge; der direkt beobachtete Calloperand sagt nur, welcher Wert in `r0` übergeben wird. Die dynamisch gelesenen Knoten können auf ungültige oder unerwartete Speicherbereiche zeigen; statische Analyse belegt keine Laufzeitgültigkeit. Ghidras Funktionskörper-/Instruktionsdecodierung und Pseudocode sind Providerinterpretationen. Das breite Dossier hat einen Timeout; die verwendeten Einzelabfragen weisen jedoch keine fehlenden Instruktionen oder ungeklärten direkten Calls aus. Eingehende Aufrufwerte `0x10062001` bleiben nur unter der oben genannten WP134-Bedingung gültig. Callee-Seiteneffekte, Aliaswege außerhalb dieses Funktionskörpers, tatsächliche Laufzeitlisteninhalte und die Semantik der Daten sind offen.

## Prüfstatus

| Prüfung / Behauptung | Status |
|---|---|
| Eingabe-Binary SHA-256 und WP134-Bericht-SHA-256 | PASS |
| ELF-VA zu Datei-Offset per `PT_LOAD`-Mapping | PASS |
| Exakter Ghidra-Körperumfang, 136 Byte, 34 Instruktionen | PASS |
| Direkter Registerfluss, bedingte Rückgabe und sichtbare Data-Refs/Calls | PASS |
| Breiter `analyze_function`-Dossierrequest | BLOCKED — Toolrequest endete nach 300 s; nicht wiederholt |
| Reproduzierbarer Bericht-/Eingabe-Hashvalidator | PASS |
| Targetausführung, VM, Netzwerk, Geräte, Hardware | NOT_RUN |
| Unabhängiger Review | NOT_RUN |
| Self-Review | PASS |

Pseudocode und Assembly in diesem Bericht sind Ghidra-Werkzeugableitungen bzw. Listingtext, kein Originalquelltext. Geltung: genau das gehashte ELF und die oben begrenzte statische Funktion. Es wurden keine Repositorydateien verändert, keine anderen Caller untersucht und keine Callee-Bodies dekompiliert.
