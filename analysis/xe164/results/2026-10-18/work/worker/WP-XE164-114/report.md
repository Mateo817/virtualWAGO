> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-114 — `IoMgrConfigGetParameterValuePointer`

## Ergebnis

**VERIFIZIERT:** Im exakt hashgebundenen `codesys3` ist das Dynsym-Symbol `IoMgrConfigGetParameterValuePointer` eine definierte `FUNC GLOBAL DEFAULT` mit ELF-VA `0x32e814` und deklarierter Größe 84 Byte. Ghidra 12.1.4 bildet es auf die Default-Space-Adresse `0x32e814` ab und erkennt genau einen zusammenhängenden Funktions-Body von `0x32e814` bis einschließlich `0x32e867` (exklusives Ende `0x32e868`). REAs Quellabbildung ordnet den Entry der Datei-Offset `0x31e814` (3.270.676 dezimal) zu. Die vollständige Ghidra-Instruktionsliste enthält 21 ARM-Instruktionen à 4 Byte.

**VERIFIZIERT:** Der sichtbare Maschinenvertrag verwendet `r0` und `r1`. Bei nicht-null `r0` liest die Funktion ein 32-Bit-Wort bei `[r0+0x0c]` und prüft Bit `0x2`. Ist dieses Bit gesetzt, liest sie das 32-Bit-Wort `[r0+0x4]`, schreibt bei nicht-null `r1` den Wert `0` nach `[r1]` und gibt das gelesene Wort in `r0` zurück. Andernfalls (einschließlich `r0 == 0`) gibt sie `0` zurück und schreibt bei nicht-null `r1` den Wert `2` nach `[r1]`. Bei `r1 == 0` erfolgt kein Schreibzugriff. Das sind beobachtete Datenfluss- und Kontrollflussfakten; Bezeichner, Feldlayout und API-Semantik folgen daraus nicht.

**VERIFIZIERT:** Ghidra meldet keine aufgelösten direkten Callees, keine aufgelösten direkten Caller und keine exakten Xrefs auf die Entry-Adresse. Die begrenzte Callsite-Liste ist damit leer; es gibt keine statische direkte Callsite, deren Argumentformen hier anzugeben wären. Das schließt indirekte, laufzeitaufgelöste oder anderweitig nicht referenzierte Aufrufe nicht aus.

## Identität und Koordinaten

| Koordinate/Identität | Beobachtung | Status |
|---|---|---|
| Artifact | `codesys3`, 5.181.396 Bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | VERIFIZIERT |
| ELF-Dynsym | `FUNC GLOBAL DEFAULT`, ELF-VA `0x32e814`, Größe 84, Abschnitt 14 | VERIFIZIERT; WP112-Bericht und erneutes GNU-`readelf`-Listing |
| Ghidra-Adresse | Default-Space `0x32e814`; Ghidra-Body `0x32e814–0x32e867` inklusiv, 84 Byte | VERIFIZIERT; Evidence `ev_4afbc2536c563b83fad40ec48e896432c78e724663b1cb961a915ceae6578778` |
| Datei-Offset | `0x31e814` = 3.270.676 dezimal, ermittelt über Ghidra-Quellabbildung | VERIFIZIERT; Evidence `ev_84f4d8a66d6f73ffbeaa1966029feff6351625c4c8f2751b971c3c52cee70c71` |
| Ursprungsimage | 287.309.824 Bytes, SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` | VERIFIZIERT; WP112-Identität erneut gehasht |

ELF-VA und Ghidra-Adresse sind zwei Namensräume mit hier gleichem Zahlenwert; der Datei-Offset ist verschieden. Ghidra meldet in der Quellabbildung Datei-Offset 3.270.676. Der ELF-Programm-Header platziert die Adresse außerdem im ersten `PT_LOAD`-Segment (Dateioffset 0, VA `0x10000`); das stimmt als unabhängige Konsistenzprüfung mit `0x32e814 - 0x10000 = 0x31e814` überein. Die Ghidra-Quellabbildung bleibt der maßgebliche Offsetnachweis.

## Argument-, Rückgabe- und Kontrollflussvertrag

Ghidras High-Function-Rekonstruktion meldet mit niedriger Konfidenz `__stdcall`, 32-Bit-Rückgabe in `r0`, Parameter 0 (`int`) in `r0` und Parameter 1 (`undefined4 *`) in `r1`. Diese Typen und die Calling-Convention sind Decompiler-Inferenzen, keine Quell-Deklaration. Direkt aus dem Instruktions-/Datenfluss folgt:

| Pfadbedingung | Speicherzugriffe | Rückgabewert |
|---|---|---|
| `r0 != 0` und `(*(uint32_t *)(r0+0x0c) & 2) != 0` | Liest 4 Byte von `r0+0x0c` und 4 Byte von `r0+0x4`; falls `r1 != 0`, schreibt 32-Bit-`0` nach `r1` | 32-Bit-Wert von `r0+0x4` in `r0` |
| `r0 == 0` oder geprüftes Bit `0x2` ist nicht gesetzt | Falls `r1 != 0`, schreibt 32-Bit-`2` nach `r1`; sonst kein Speicherzugriff | 32-Bit-`0` in `r0` |

Es gibt drei Return-Instruktionen: `0x32e848`, `0x32e850`, `0x32e864`. Der gemeinsame Erfolgs-Return lädt zuvor `[r0+4]`; die zwei Fehlerpfade setzen `r0` auf null (im null-`r1`-Fehlerpfad durch Kopie von `r1`, das dort null ist). Es gibt keine Call-Instruktion innerhalb des Extents.

## Vollständige Instruktionstabelle

Ghidra-Adressen sind Default-Space-Adressen. Alle 21 gelisteten Instruktionen sind im ARM-Modus 4 Byte lang; damit deckt die Liste 84 Byte ohne Lücke vom Entry bis zum exklusiven Ende ab.

| Adresse | Instruktion |
|---|---|
| `0x32e814` | `cmp r0, #0x0` |
| `0x32e818` | `cpy r12, sp` |
| `0x32e81c` | `stmdb sp!,{r11,r12,lr,pc}` |
| `0x32e820` | `sub r11, r12, #0x4` |
| `0x32e824` | `beq 0x0032e834` |
| `0x32e828` | `ldr r3, [r0,#0xc]` |
| `0x32e82c` | `tst r3, #0x2` |
| `0x32e830` | `bne 0x0032e854` |
| `0x32e834` | `cmp r1, #0x0` |
| `0x32e838` | `beq 0x0032e84c` |
| `0x32e83c` | `mov r3, #0x2` |
| `0x32e840` | `mov r0, #0x0` |
| `0x32e844` | `str r3, [r1,#0x0]` |
| `0x32e848` | `ldmia sp,{r11,sp,pc}` |
| `0x32e84c` | `cpy r0, r1` |
| `0x32e850` | `ldmia sp,{r11,sp,pc}` |
| `0x32e854` | `cmp r1, #0x0` |
| `0x32e858` | `ldr r0, [r0,#0x4]` |
| `0x32e85c` | `movne r3, #0x0` |
| `0x32e860` | `strne r3, [r1,#0x0]` |
| `0x32e864` | `ldmia sp,{r11,sp,pc}` |

## Datenreferenzen, Calls und Caller

**VERIFIZIERT:** Keine direkten globalen Datenreferenzen, Stringreferenzen oder Call-Referenzen sind im Funktions-Body erfasst. Die gelesenen und geschriebenen Adressen entstehen aus den Eingaberegistern: Lesezugriff `[r0+0x0c]` bei `0x32e828`, Lesezugriff `[r0+0x4]` bei `0x32e858`, Fehlerstatus-Schreibzugriff `[r1] = 2` bei `0x32e844`, Erfolgsstatus-Schreibzugriff `[r1] = 0` bei `0x32e860` (bedingt durch `r1 != 0`). Die Ghidra-Referenzen zu `0x32e834`, `0x32e84c` und `0x32e854` sind interne bedingte Kontrollflussreferenzen.

Begrenztes Caller-Inventar: `procedure_callers` für `0x32e814` ergab eine leere, als vollständig für aufgelöste Ghidra-Call-Referenzen markierte Liste (Evidence `ev_35a748a2b897b21b712e662f0bc15ac056d61d6555ab4c40916c2a4a2ae4fb73`). `xrefs` exakt auf `0x32e814` ergab ebenfalls leer (Evidence `ev_73c7700eb823f08bbe5215807efdfd2e9e41b49ae14f0fdb1e26977e7b26c230`). Der Callee-Aufruf ergab leer (Evidence `ev_70830d8c519b32c9761f677fbad519a1989173df755665176e2e329b1c734997`). Diese Inventare behaupten keine Vollständigkeit für indirekte oder dynamische Ziele.

## Methode und Grenzen

REA zuerst: `open_binary` auf dem WP112-Extrakt, danach `analyze_function` für `0x32E814`, anschließend `address_to_file_offset`, `procedure_callers`, `procedure_callees` und `xrefs`. Analyseprofil-Digest: `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Werkzeuge: REA `6.5.0`, Ghidra `12.1.4`; für die unabhängige Dynsym-/PT_LOAD-Konsistenzprüfung GNU `readelf` aus Binutils `2.44` (WP112 protokollierte diese Version). Analyse blieb statisch und lokal. Kein Netzwerk, keine VM, kein Gerät und keine Laufzeitbeobachtung.

Die REA-Instruktionsliste und Pseudocode sind Ghidra-Ausgaben, keine Originalquelle. Die allgemeine Ghidra-Unsicherheit über nicht aufgelöste indirekte Kontrollflüsse bleibt bestehen. Das leere Caller-Inventar ist auf aufgelöste statische Call-Referenzen und exakte Ghidra-Xrefs zur Entry-Adresse beschränkt. Der Name `IoMgrConfigGetParameterValuePointer` beweist für sich keine API-Semantik. `r0+4`, `r0+0xc` und `r1`-Output werden nicht zu erfundenen Structfeldern oder Typen umbenannt. Alternative Erklärung: Die niedrige Decompiler-Typisierung könnte die konkreten Quelltypen verfehlen; die gezeigten Register- und Speicheroperationen bleiben davon unberührt.

## Tests und Artefakte

| Prüfung | Status |
|---|---|
| Ghidra-Body umfasst genau 84 Byte; Tabelle enthält 21 fortlaufende 4-Byte-Adressen | PASS |
| REA-Evidence-Bundle enthält Funktionsdossier, Dateiabbildung, Caller-, Callee- und Xref-Abfragen | PASS |
| Input- und WP112-Identität anhand Größe/Hash | PASS |
| Validator und `SHA256SUMS` | PASS |

Erzeugte Dateien im Workpackage-Verzeichnis: `report.md`, `validate.py`, `rea-evidence-bundle.json`, `SHA256SUMS`. Hashes stehen in `SHA256SUMS`; die Datei selbst wird nicht in sich selbst aufgenommen.

Self-Review: Die Prüfpunkte wurden mit `validate.py` und `sha256sum -c SHA256SUMS` gegen das erzeugte Bundle und die Eingabeidentitäten geprüft. Kein unabhängiger Review oder Worker-Lauf wird behauptet.
