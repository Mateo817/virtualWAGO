> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-155 — `SettgGetStringValue` body at `0x0033ce44`

## Ergebnis

**VERIFIZIERT:** Als statischer Maschinenkode belegt der Dynsym-Eintrag `SettgGetStringValue` in der vorgegebenen ELF-Datei den Bereich VMA `0x0033ce44..0x0033ce9f`, 92 Bytes inklusive. Der erste ausführbare `PT_LOAD` bildet Dateioffset 0 auf VMA `0x10000` ab; der Körper liegt deshalb bei ELF-Dateioffsets `0x0032ce44..0x0032ce9f`. 23 aufeinanderfolgende 4-Byte-ARM-A32-Instruktionen decken diesen Bereich bytegenau und ohne Lücke ab. Die Byteprüfung gegen die Eingabedatei ist PASS.

**VERIFIZIERT:** Im lokal sichtbaren Kontroll- und Datenfluss werden vier Eingangsregister gesichert (`r0`→`r4`, `r1`→`r5`, `r2`→`r6`, `r3`→`r8`). Der Körper liest außerdem zwei 32-Bit-Wörter vom Eintritts-Stack: `[entry_sp]` und `[entry_sp+4]`. Er vergleicht das zweite Wort mit `1`. Bei Ungleichheit stellt er `r0-r3` aus den gesicherten Eingangsregistern wieder her, schreibt das erste Stackwort unverändert an dieselbe Adresse zurück, restauriert Register und Stackzeiger und führt einen direkten Tail-Branch nach `0x00341f44` aus. Bei Gleichheit ruft er direkt `0x00340b58` auf. Ein nichtnuller Rückgabewert dieses Aufrufs wird unverändert in `r0` zurückgegeben; bei null restauriert der Körper die Eingangsargumente und führt denselben Tail-Branch nach `0x00341f44` aus.

Die zwei Dynsym-Namen werden hier nur zur Bezeichnung statisch bestimmter Sprungziele verwendet. Daraus folgt keine Semantik der Zielroutinen. Der Disassemblername des Körpers selbst liefert ebenfalls keinen zusätzlichen Funktionsvertrag.

## Instruktionen, vollständiger Extent

`instructions.tsv` enthält alle 23 Instruktionen mit VMA, ELF-Dateioffset, exakten Quellbytes und beobachtetem Effekt. `raw-evidence.md` hält den vollständigen fokussierten Rizin-Text, 92 Quellbytes, Dynsym-Einträge und Segmentmapping fest. Die Bytefolge in den Tabellen ist ELF-Dateireihenfolge; dekodiert wird sie als ARM A32 im little-endian ELF.

| VMA | Instruktion | sichtbarer Effekt |
|---:|---|---|
| `0x33ce44` | `mov ip, sp` | Merkt Eintritts-SP `S0` in `ip`. |
| `0x33ce48` | `push {r4-r8,sb,fp,ip,lr,pc}` | Schreibt 10 Wörter in `S0-40..S0-1`; SP wird `S0-40`. `sb` ist `r9`. |
| `0x33ce4c` | `sub fp, ip, #4` | `fp = S0-4`. |
| `0x33ce50` | `mov r4, r0` | Sichert Eingangs-`r0`. |
| `0x33ce54` | `mov r5, r1` | Sichert Eingangs-`r1`. |
| `0x33ce58` | `ldr ip, [fp,#8]` | Liest `[S0+4]`. |
| `0x33ce5c` | `mov r6, r2` | Sichert Eingangs-`r2`. |
| `0x33ce60` | `ldr r7, [fp,#4]` | Liest `[S0]`. |
| `0x33ce64` | `mov r8, r3` | Sichert Eingangs-`r3`. |
| `0x33ce68` | `cmp ip,#1` | Vergleicht das gelesene `[S0+4]` mit 1. |
| `0x33ce6c` | `beq 0x33ce90` | Bei Gleichheit zum direkten Aufrufpfad. |
| `0x33ce70` | `mov r3,r8` | Bereitet ursprüngliches `r3` wieder vor. |
| `0x33ce74` | `mov r2,r6` | Bereitet ursprüngliches `r2` wieder vor. |
| `0x33ce78` | `mov r1,r5` | Bereitet ursprüngliches `r1` wieder vor. |
| `0x33ce7c` | `mov r0,r4` | Bereitet ursprüngliches `r0` wieder vor. |
| `0x33ce80` | `str r7,[fp,#4]` | Schreibt den unveränderten Wert zurück nach `[S0]`. |
| `0x33ce84` | `sub sp,fp,#0x24` | Setzt SP auf `S0-40`, den Anfang des Save-Bereichs. |
| `0x33ce88` | `ldm sp,{r4-r8,sb,fp,sp,lr}` | Restauriert gesicherte Register und setzt SP zurück auf `S0`. |
| `0x33ce8c` | `b 0x341f44` | Direkter Branch ohne Link: Tail-Transfer. |
| `0x33ce90` | `bl 0x340b58` | Direkter Call, Rückkehradresse `0x33ce94`. |
| `0x33ce94` | `cmp r0,#0` | Prüft den Call-Rückgabewert in `r0`. |
| `0x33ce98` | `beq 0x33ce70` | Bei null zur Argumentwiederherstellung und zum Tail-Transfer. |
| `0x33ce9c` | `ldm sp,{r4-r8,sb,fp,sp,pc}` | Restauriert Register/SP und kehrt durch Laden des gesicherten PC zurück. |

## Kontrollfluss, Calls und Ergebnisprüfungen

| Pfad | Ausführung und sichtbares Ergebnis |
|---|---|
| `[S0+4] != 1` | `0x33ce6c` fällt durch; `r0-r3` werden aus den Sicherungen restauriert; `[S0]` wird mit demselben zuvor gelesenen Wort beschrieben; der Frame wird abgebaut; `b 0x341f44` überträgt direkt. Der lokale Körper erhält die Kontrolle auf diesem Pfad nicht wieder. |
| `[S0+4] == 1`, Call-Ergebnis `r0 != 0` | `bl 0x340b58`; `cmp r0,#0` fällt nicht gleich aus; `ldm ... pc` restauriert den Frame und gibt das unveränderte `r0` zurück. |
| `[S0+4] == 1`, Call-Ergebnis `r0 == 0` | `beq 0x33ce70`; ursprüngliches `r0-r3` werden wiederhergestellt, `[S0]` wird unverändert zurückgeschrieben, dann `b 0x341f44`. |

Der Aufruf an `0x33ce90` erfolgt mit den unveränderten Eingangsregistern `r0-r3`; zu diesem Zeitpunkt zeigt SP noch auf den 40-Byte-Save-Bereich (`S0-40`). Die vorher gelesenen Wörter bei `S0` und `S0+4` bleiben an ihren Adressen. Dieser Befund behauptet nicht, dass diese alten Slots gemäß einem Callee-Vertrag als Stackargumente des Calls gelten. Der Tail-Branch an `0x33ce8c` erfolgt erst nach SP-Restaurierung auf `S0` und stellt `r0-r3` wieder her.

Die Rückkehrstellen sind vollständig abgegrenzt: lokaler Rücksprung allein über `0x33ce9c`; zwei Tail-Transfers über `0x33ce8c`, einer direkt nach dem Vergleich, einer nach nuller Call-Antwort. Innerhalb dieses Körpers gibt es keinen indirekten Call. Der andere Call ist der direkte `BL` bei `0x33ce90`. Der Zielcode beider Übertragungen liegt außerhalb des angeforderten Bereichs und wurde nicht analysiert.

`memory.tsv`, `inputs_outputs.tsv`, `calls.tsv` und `flow.tsv` halten die sichtbaren Speicheroperationen, Register-/Stackwerte, beide direkten Ziele und alle Kanten separat fest. Speicherzugriffe der Zielroutinen sowie mögliche weitere Wirkungen eines Calls sind aus diesem Körper nicht bestimmbar.

## REA und Alternativerklärung

Vor dem Disassembler-Fallback wurde der vorhandene gleichnamige Bericht WP-XE164-153 und dessen eingebettetes WP-XE164-118-Bundle geprüft. Das Bundle hat die erwartete SHA-256 der ELF, aber keine Evidence für `0x33ce44`; seine benannten Instruction-/Call-Records betreffen `0x330610` / `0x330664`. WP153 dokumentiert einen abgebrochenen Rizin-Autoanalyseversuch sowie, dass der identische Ghidra-Neuimport wegen des beobachteten Hängers nicht wiederholt wurde. Entsprechend wurde in diesem Paket kein gleicher Importversuch gestartet. Es gibt daher keine REA-Evidence-ID für den hier dekodierten Körper; die vorhandenen, in `raw-evidence.md` aufgeführten IDs sind ausdrücklich sachfremd zu diesem Bereich.

Gezielter Fallback: Rizin 0.9.1 dekodierte genau 23 ARM-A32-Instruktionen. GNU `readelf` 2.44 lieferte Dynsym und LOAD-Mapping. Der generische `objdump`-Befehl auf PATH (GNU Binutils 2.44 Host-Build) konnte diese ARM-Datei nicht dekodieren (`can't disassemble for architecture UNKNOWN!`) und wurde nicht als Disassembler-Evidence verwendet. `/usr/bin/arm-linux-gnueabihf-objdump` wurde in diesem Paket nicht getestet; der Fehler des generischen Befehls belegt nicht, dass GNU objdump ARM nicht dekodieren kann.

Alternative Erklärung für den Vergleichswert: statisch ist nur belegt, dass das zweite beim Eintritt liegende Stackwort exakt mit `1` verglichen wird und der Gleichheitspfad den direkten Call ausführt. Es kann ein Auswahl-, Modus- oder sonstiger Wert sein; die konkrete Bedeutung ist aus diesen Bytes nicht sichtbar. Ebenso belegen die Zielnamen weder Implementierungsverhalten noch den semantischen Zweck der Stackwerte.

## Status, Tests und Grenzen

| Aussage | Status |
|---|---|
| 92-Byte-Umfang, ELF-Dateioffsets, alle 23 dekodierten Instruktionen und Quellbytes | VERIFIZIERT |
| lokaler CFG, sichtbare Stack-/Registerbewegungen, zwei direkte Transfers, Ergebnisvergleich und lokaler Return | VERIFIZIERT |
| API-/Argumentrollen der Werte, Wirkung der Zielroutinen, Laufzeitresultate | OFFEN |
| unabhängige Ghidra-FunctionManager-Bestätigung dieses Bodys (WP153 dokumentiert einen Autoanalyse-Hänger; derselbe Import wurde nicht wiederholt) | BLOCKED |
| `python3 validate.py` | PASS |
| `sha256sum -c SHA256SUMS` | PASS |

Validator und Hashmanifeste prüfen Identität, Extent, Instruktionsadressen, Dateioffsetabbildung und jede der 92 Bytes. Die Zuordnung von Kontroll-/Datenfluss ist statische Analystenprüfung der gespeicherten Dekodierung (**Self-Review**). Es wurde kein unabhängiger Reviewer, Worker, Laufzeit-, Hardware- oder Geräteversuch behauptet. Laufzeitverhalten ist nicht Gegenstand dieses Befunds.

## Paketinhalt

| Datei | Inhalt |
|---|---|
| `report.md` | Befund, Tabellenzusammenfassung, Status und Grenzen |
| `raw-evidence.md` | vollständige Quellbytes/Instruktionen, ELF-Mapping, Dynsym und geprüfte REA-Bundle-/ID-Grenze |
| `instructions.tsv` | lückenlose 23-Instruktions-Tabelle mit VMA, Dateioffset und Bytes |
| `flow.tsv` | CFG-Kanten und Pfade |
| `calls.tsv` | direkte Call-/Branch-Ziele und sichtbarer Zustand |
| `inputs_outputs.tsv` | sichtbare Register-, Stack- und Rückgabewerte |
| `memory.tsv` | sichtbare Speicherreads/writes und Umfang |
| `tool_versions.txt` | eingesetzte Versionen und Disassemblergrenze |
| `validate.py` | reproduzierbare Offline-Byte-/Extent-Validierung |
| `validator_result.txt` | Ergebnis des Validators und Hashprüfung |
| `SHA256SUMS` | Hashes der übrigen Paketdateien |

Der SHA-256-Katalog listet jede Paketdatei außer sich selbst; `sha256sum -c SHA256SUMS` prüft alle gelisteten Dateien.
