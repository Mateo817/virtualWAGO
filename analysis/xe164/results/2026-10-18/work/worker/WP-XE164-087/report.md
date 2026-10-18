> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-087 — Guard-/Tail-Dispatch-/Rückgabevertrag

## Ergebnis

**Status: VERIFIZIERT** für den statisch beobachtbaren Vertrag des 60-Byte-Kandidaten `ELF-VA 0x2614..0x264f` und die begrenzte Init-Wertbindung. Dies belegt keine Ausführung und keine Bedeutung eines Parameters, Slots oder Statuscodes.

Nach den Instruktionen lautet der effektive Guard: Rückgabe `2`, falls `r2_in == 0`, oder `r1_in == 0`, oder `r0_in == 0xffffffff`. Andernfalls erfolgt an `0x2644` ein bedingungsloser Tail-Transfer auf `idk_CalculateSlotNumber@plt`; in diesem Transferzustand sind `r0=r1_in`, `r1=r2_in`, `r2=0`, `r3=0`. Der direkte Rückgabepfad setzt `r0=2` und kehrt mit `bx lr` zurück. `0x264c` ist das letzte Instruktionswort im Scope.

## Koordinaten und Herkunft

- Eingabedatei: `libIoDrvKbus.so.0.0.1`, 38,584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` (Hash vor Analyse geprüft).
- ELF: `ET_DYN`, ARM little-endian. Der erste ausführbare `LOAD` hat `p_offset=0`, `p_vaddr=0`; damit sind im untersuchten Bereich ELF-VA und Dateioffset gleich (`0x2614..0x264f`). Beleg: begrenzter GNU `readelf -lW`-Fallback, Binutils 2.44.
- REA/Ghidra-Koordinaten: REA `address_to_file_offset(0x12614)` liefert Dateioffset dezimal `9748` (`0x2614`). Zusammen mit dem ELF-LOAD-Mapping ergibt sich die Ghidra-Ladeadresse `0x12614` als ELF-VA `0x2614` plus `0x10000`. Dieser Basisversatz ist eine abgeleitete Koordinatendifferenz, kein Laufzeit-Load-Bias.
- Laufzeitadresse/Load-Bias: **OFFEN**. Aus statischer ELF-Analyse nicht festgestellt.
- REA-Exportprofil: `rea-agents 6.5.0`, Provider Ghidra `12.1.4`, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; ARM:LE:32:v8. Analyse statisch/offline, keine Zielausführung.
- Fallback: `arm-linux-gnueabihf-objdump` GNU Binutils 2.44 mit exakt `--start-address=0x2614 --stop-address=0x2650`; kein Byte ab `0x2650` wurde disassembliert. Es bestätigt die REA-Instruktionen und löst den direkten Branch als `idk_CalculateSlotNumber@plt` auf.

## Scope-Abweichung in der Exploration

In einer frühen, anschließend geschlossenen REA-Sitzung wurde versehentlich genau eine Instruktion bei Ghidra-VA `0x12650` (ELF-VA `0x2650`, harte Nachbargrenze) abgefragt. Das war außerhalb des freigegebenen Body-Scopes. Die Beobachtung ist bewusst nicht in den finalen Export aufgenommen und nicht für die Schlussfolgerung verwendet; der finale Export stammt aus einer danach frisch geöffneten, scope-reinen Sitzung, deren adressgebundene Abfragen bei `0x264c` enden. Kein weiterer Inhalt ab `0x2650` wurde untersucht. Diese Abweichung bleibt als Prozessrisiko dokumentiert.

## Guard-, Dispatch- und Rückgabepfade

Die ABI-Parameter werden hier nicht benannt. `r0_in..r3_in` bezeichnen nur die vier bei Eintritt beobachteten ARM-Registerwerte.

| Pfad | Instruktionsbeleg | Beobachtbarer Vertrag |
|---|---|---|
| Setup | `0x2614`, `0x2618` | `r3 := r0_in`; `r0 := r1_in`. |
| Null-Guard | `0x261c..0x262c` | `cmp r2,#0`; nur bei NE folgt `cmpne r0,#0`; danach `r1 := r2_in`; `r2 := 1` bei EQ, sonst `0`. Damit ist das temporäre `r2` genau dann `1`, wenn `r2_in==0` oder `r1_in==0`. |
| Sentinelflag | `0x2630..0x2638` | `cmn r3,#1` setzt EQ genau dann, wenn `r0_in == 0xffffffff`; danach wird `r3 := 1` bei EQ, sonst `0`. |
| Zusammenführung | `0x263c..0x2640` | `orrs r3,r3,r2`; NE verzweigt zu `0x2648`. Also direkter Fehler-/Guard-Rückgabepfad, wenn mindestens eine der drei obigen Bedingungen zutrifft. |
| Guard-Rückgabe | `0x2648`, `0x264c` | `r0 := 2`; `bx lr`. Rückgabewert im beobachteten Register `r0` ist exakt `2`. |
| Tail-Transfer | `0x2644` | Unbedingter `b` (kein `bl`), von Ghidra als `CALL_TERMINATOR`/`UNCONDITIONAL_CALL` klassifiziert, an Ghidra-VA `0x11ddc` = ELF-VA `0x1ddc`. REA nennt dort das Primärsymbol `idk_CalculateSlotNumber`; Binutils löst es am Transfer als `idk_CalculateSlotNumber@plt` auf. Zielbody absichtlich nicht untersucht. Auf diesem Pfad gelten `r0=r1_in`, `r1=r2_in`, `r2=0`, `r3=0`; der Tail-Transfer setzt keinen neuen Link-Registerwert. |

## Minimale Init-Bindung

REA ordnet `IoDrvKbus_Init` dem Einstieg Ghidra-VA `0x147fc` zu; REA-Beleg `ev_18238ec691cd75b4c4bac8f29b12e867e49f26020cd600d1dafe6dd2eb084cd5`. Die Minimalfolge (ohne semantischen Feld- oder Slotnamen) ist:

1. Bei `0x14804` lädt `ldr r3,[0x15320]` das Literal; Bytes an Ghidra-Adresse `0x15320` sind `fcddffff` (`-0x2204` als vorzeichenbehafteter 32-Bit-Wert), Beleg `ev_3dc0e805757d436aaa22a4dcb115b78da5bae1b41ea5b8371ba9bbb4672f8c8e`, `ev_8adc4e9564e2eadf7055eca9610f1bb1736ab9f190c090c2a2f9804a112a1bbb`.
2. Bei `0x14810` führt `add r3,pc,r3` aus. Im ARM-Zustand ist der PC-Operand hier `0x14818`; `0x14818 + 0xffffddfc = 0x12614`, also der Kandidat. Instruktionsbeleg `ev_da505a9333180be7003756d0e77dc02ba43164e5fe2f937c63e1f1893f414a5a`.
3. Bei `0x14814` speichert `str r3,[sp,#0x18]` diesen Wert in einem Init-Stack-Temporär. Ghidra führt von genau diesem Store eine DATA-Referenz auf `0x12614` (ELF-VA/Dateioffset `0x2614`), Beleg `ev_3b4f13afe664fb8eec1dc7b332848323a18239878daf011ed005b46d5f0c5fc0`. Das ist die statische Bindung der Publikationsvorbereitung; kein Slot-/Callbackname wird daraus abgeleitet.

## Evidence, Status und Unsicherheit

Die vollständigen 15 Instruktions-Evidence-IDs und die Pfadzuordnung stehen in `instructions.tsv`. Die Init-Minimalfolge steht in `init-publication.tsv`. Der unveränderte vollständige REA-Export der scope-reinen Sitzung ist `rea-evidence-bundle.json` (27 Records, 0 Unknowns; Export direkt durch REA).

**VERIFIZIERT:** Hashidentität, Bereichsdisassembly, beobachtete Instruktionsfolge, berechnete Flags und Pfad-Rückgabewert, unbedingter Transfer am `0x2644`, Dateiabbildung des Kandidaten sowie die statische Init-Literal-/PC-relative-/Stack-Store-Kette. Ghidra meldet für die Instruktionen `0x12614..0x1264c` keine Procedure-Zugehörigkeit; die festgelegte Bereichsgrenze folgt der Aufgabenvorgabe, nicht einer erfundenen Funktionsdefinition.

**OFFEN:** semantische Bedeutung der vier Eingabewerte, der Rückgabe `2`, der Vorbedingungen und des gespeicherten Stack-Werts für einen späteren Consumer; Laufzeitadresse und tatsächliche Ausführung. Der spätere Init-Consumer wurde nicht verfolgt.

**Alternativerklärung:** Die Vergleiche könnten Fehler-/Gültigkeitsprüfungen auf Null- und `0xffffffff`-Sentinelwerte implementieren. Das ist eine plausible Interpretation, aber ohne Vertrag des Aufrufers nicht belegt; beobachtet sind nur die Registervergleiche, Flagbildung und Transfers.

## Tests und Validator

Tests: **PASS** für Hash- und Bundle-/Evidence-Referenzprüfung in `validate.py`; **NOT_RUN** für Laufzeit, Hardware und unabhängige Gegenprüfung. `validate.py` prüft auch, dass die Instruktionstabelle genau `0x2614..0x264f` abdeckt und keine Instruktion bei oder nach der Nachbargrenze `0x2650` enthält.
