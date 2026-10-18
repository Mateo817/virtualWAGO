> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-084 — Kandidat `0x36c0`

## Ergebnis

**HYPOTHESE:** `0x36c0` ist ein nicht von Ghidra als Funktion angelegter, aber von `IoDrvKbus_Init` als Codeadresse referenzierter Kandidat. Die instruktionsgebundene Reachability beginnt bei `0x36c0` und bleibt unter der harten Obergrenze `0x3e54`. Sie beobachtet 460 erreichbare, dekodierte Instruktionen, 23 Call-Sites und einen Return bei `0x376c`. Direkte Calls wurden nur an ihren Sites klassifiziert; ihre Bodies wurden nicht untersucht.

**VERIFIZIERT:** `IoDrvKbus_Init` stellt vier 32-Bit-Codeadressen aus Stackpositionen `[sp+0x08..0x14]` zusammen und schreibt sie mit `vst1.32 {d18,d19},[r3]` an `r3 = r0 + 0x34`. Die beiden letzten Werte sind `0x12704` und danach `0x136c0`; damit ist der Kandidat der vierte sequenzielle Eintrag (Index 3, Zielausdruck `r0+0x40`) in dieser Veröffentlichung. `0x12704` (Dateioffset `0x2704`) ist der unmittelbar vorhergehende Eintrag (Index 2, `r0+0x3c`). Die konkrete Semantik dieser Positionen ist **OFFEN**. Die Nachbarschaft belegt die Position, aber keinen Callbacknamen oder Vertrag.

## Adressräume, Eingabe und Toolprofil

- Eingabe: ELF32 little-endian ARM, 38,584 Bytes; SHA-256 vor Analyse erneut geprüft: `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`.
- Angegebene ELF-VA und Dateioffset: Kandidat `0x36c0`; Nachbargrenze `0x3e54`; Vergleichseintrag `0x2704`.
- Ghidra-Ladeadresse: REA meldet Image Base `0x10000`; die korrespondierenden Provider-Adressen sind `0x136c0`, `0x13e54` und `0x12704`. `address_to_file_offset` bindet diese an die Dateioffsets `0x36c0`, `0x3e54` und `0x2704`.
- Laufzeitadressen: **OFFEN**. Es wurde keine Runtime geladen oder ausgeführt; aus dem Ghidra-Image-Base wird keine Runtime-Basis abgeleitet.
- REA/Ghidra: Ghidra 12.1.4, Profil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`, ELF-Loader, ARM:LE:32:v8, Standard-Autoanalyse, ephemeral/import read-only. Pseudocode ist nicht verfügbar, da Ghidra bei `0x136c0` keinen Funktionskörper besitzt.
- Die kleinste REA-Funktionsgrenze für den Eintritt ist deshalb **kein Ghidra-Funktionskörper**: `resolve_containing_procedure(0x136c0)` meldet `not_in_procedure`. Der Befund bleibt streng instruktionsgebundene Reachability ab dem exakt dekodierten Einstieg, nicht eine erfundene Funktion. `0x3e54` ist als nächster Dynsym-Start die exklusive harte Obergrenze.
- Einstieg: `resolve_containing_procedure(0x136c0)` meldet `not_in_procedure` (Evidence `ev_eb5f3ad169849c0e2a146b5fbbeab940b727a67bbefe7b2583107fc029ad8bc0`). Die exakte Instruktionsabfrage dekodiert dort dennoch `sub r3,r0,#1` ohne zugeordnetes Ghidra-Procedure (Evidence `ev_fb250a617831a7c58a7f676d4d972cd6736d73f3486473ab463ca0c3709df5e2`).
- Obere Nachbargrenze: Ghidra bindet `0x13e54` an `idk_ExtendMaxTerm_4_DevicesInFieldAccording_2_PM_Decision` (Evidence `ev_e6b95ab23d3ad9d1391702fb9d22297b730864855beeee9d16d2cb19e39541b4`). Der nachgewiesene nächste Dynsym-Eintrag ist zusätzlich durch GNU readelf bestätigt (Fallback-Notiz unten). Die Grenze wird exklusiv behandelt; sie beweist keine vollständige Funktionsextent für `0x136c0`.

## Kontrollfluss und Calls

Die Reachability ist vom exakten Start `0x136c0` aus der REA-Instruktionsbeobachtung aufgebaut. Bei `call` wird nur der Call-Site notiert und danach die Instruktionsfortsetzung verfolgt; kein Callee wird betreten. Bei bedingtem Sprung werden Ziel und Fallthrough aufgenommen, bei unbedingtem direktem Sprung nur das Ziel. Der Suchraum ist `[0x136c0,0x13e54)`. Kein beobachteter Reachability-Edge verlässt diese Grenze. Die komplette Site-Tabelle samt Ghidra-Evidence-IDs steht in [controlflow-callsites.tsv](./controlflow-callsites.tsv); sie enthält alle 74 Sprung-, 23 Call- und einen Return-Sites.

| Beobachtung | Ergebnis | Status |
|---|---:|---|
| Erreichbare dekodierte Instruktionen | 460 | VERIFIZIERT |
| Bedingte Sprünge | 55 | VERIFIZIERT |
| Unbedingte direkte Sprünge | 19 | VERIFIZIERT |
| Direkte Calls | 11 Sites | VERIFIZIERT |
| Indirekte Calls | 12 `blx rN` Sites; kein Ziel in den Instruktionsreferenzen | VERIFIZIERT |
| Erreichbare Architektur-Returns | 1: `0x1376c`, `ldmia sp!,{r4,r5,r6,r7,r8,r9,r10,r11,pc}` | VERIFIZIERT |
| Kontrollfluss ausserhalb der harten Obergrenze | 0 beobachtete Kanten | VERIFIZIERT |

Der unabhängige, strikt begrenzte Crosscheck mit `/usr/bin/arm-linux-gnueabihf-objdump` (GNU Binutils 2.44) lief mit `-d --start-address=0x36c0 --stop-address=0x3e54`. Er deckt 1,940 Bytes / 485 Wortpositionen ab. ARM objdump lieferte 485 dekodierte Zeilen im gesamten Intervall (einschließlich nicht über die Start-Reachability erreichter Wörter); für alle 460 erreichbaren Instruktionen stimmen die Bytes mit REA überein: **460/460, 0 Abweichungen**. Die Flow-Zählung aus REA bleibt 23 Calls, 74 Sprünge, 1 Return, 362 Fallthroughs. Detailtabellen und rohe begrenzte Ausgabe: [arm-objdump-crosscheck.tsv](./arm-objdump-crosscheck.tsv) und [arm-objdump-bounded.txt](./arm-objdump-bounded.txt). Der wiederholbare Prüfer ist [arm_objdump_crosscheck.py](./arm_objdump_crosscheck.py).

Die direkten Calls sind in der Site-Tabelle nach den exakten Zieladressen klassifiziert. Beobachtete Ziele enthalten lokale Helper (`0x11fdc`, `0x12074`, `0x1277c`) und Thunks (`0x11d1c`, `0x11d40`, `0x11de8`, `0x11e18`, `0x11d10`); Thunkauflösungen sind dort ausgewiesen. Die 12 indirekten Calls bleiben ohne statisch aufgelöstes Ziel. Keine Callee-Bodies wurden rekursiv analysiert.

## Datenbindung und publizierte Position

Die relevanten Instruktionsfolgen in `IoDrvKbus_Init` sind im Datenbindungstisch mit Evidence-IDs aufgeführt:

1. `0x14868`: `str r3,[sp,#0x10]`, Ghidra-Referenz auf `0x12704`.
2. `0x14874`: `str r3,[sp,#0x14]`, Ghidra-Referenz auf `0x136c0`.
3. `0x14878` und `0x1487c`: Laden der zwei Doppelregister aus den benachbarten Stackpaaren `[sp+0x08]` und `[sp+0x10]`.
4. `0x148a4`: `r3 = r0 + 0x34`.
5. `0x148a8`: `vst1.32 {d18,d19},[r3]` schreibt die vier 32-Bit-Einträge ab diesem Ziel. Dadurch wird der Wert `0x136c0` an Position `r0+0x40` gebunden; der gepaarte `0x12704` liegt davor an `r0+0x3c`.

Die Ghidra-Referenzen auf die beiden Adressen stammen von den Stores bei `0x14868`/`0x14874`; der lokale, nicht typisierte Speicher wird nicht als erfundener Structtyp benannt. `r0+0x34` und die Indizes sind Instruktionsableitungen, keine behaupteten Feldnamen oder API-Structs. Weitere Init-Logik wird für diese Aussage nicht ausgewertet. Siehe [data-bindings.tsv](./data-bindings.tsv).

**Alternativerklärung (OFFEN):** Die vier Wörter könnten eine generische Funktionszeigerliste oder eine herstellerspezifische Tabelle sein. Weder Feldnamen noch ein Laufzeitverbraucher werden durch die Nachbarschaft der Werte identifiziert. Die Tabelle belegt die Veröffentlichung in Speicher, aber nicht, dass der Kandidat im betrachteten Lauf tatsächlich aufgerufen wird.

## Fallback und Grenzen

Der REA-generische GNU-objdump-Versuch bleibt als Audit **BLOCKED**: `ELF32 little`, `architecture UNKNOWN`, Exit 1 (Evidence `ev_57b8652888cdb876d5b4cad7558c462c93ca8f69416fc26743edf9b7574b541e`). Davon getrennt war `/usr/bin/arm-linux-gnueabihf-objdump` vorhanden; der oben beschriebene eng begrenzte ARM-Crosscheck ist **PASS**. GNU readelf 2.44 bestätigte den nächsten Dynsym-Eintrag:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

**Restunsicherheit (OFFEN):** Ohne Ghidra-Funktionskörper ist die 460-Instruktionen-Menge eine statische Reachability unter dem angegebenen Instruktions-/CFG-Modell, keine bewiesene vollständige Routine. Indirekte Call-Ziele und deren Rückkehrverhalten sind unbekannt. Der einzelne beobachtete Return darf nicht als Laufzeitbeobachtung oder vollständiger Exitvertrag gelesen werden. Dynsym bei `0x3e54` ist eine harte, nachvollziehbare Suchgrenze; die Analyse behauptet nicht, dass Kandidatencode direkt davor endet.

## Status und Prüfergebnis

- Kandidateninstruktion und Ghidra-Procedure-Lücke: VERIFIZIERT.
- Publikationsbindung `0x136c0` → vierter Wortplatz ab `r0+0x34`: VERIFIZIERT.
- Semantik dieses Wortplatzes und dynamische Aufrufrolle: OFFEN.
- Erfasste, begrenzte CFG-/Callsite-Tabelle: VERIFIZIERT.
- Generischer REA-objdump-Audit: BLOCKED (BFD meldete `architecture UNKNOWN`; erhaltenes REA-Evidence).
- Begrenzter GNU ARM objdump-Crosscheck: PASS (460 erreichbare Instruktionen, 0 Byteabweichungen; GNU Binutils 2.44).
- Runtimeausführung und Geräte-/Netzwerkzugriff: NOT_RUN.
- Validator: PASS (siehe `validate_bundle.py` und `SHA256SUMS`).

REA Evidence ist der **unveränderte vollständige deterministische Export einer frischen scope-reinen REA-Sitzung**: [rea-evidence.json](./rea-evidence.json), 503 Records (483 einzelne Instruktionsabfragen, 16 punktuelle Procedure-Auflösungen, 3 Adressabbildungen und der generische objdump-Audit). Es wurden keine weiteren REA-Operationen in dieser Sitzung ausgeführt und der Export wurde nicht gefiltert oder manuell projiziert. Die frühere gefilterte Projektion verbleibt ausschließlich als abgelehnter Audit [rea-evidence-scope.rejected-projection.json](./rea-evidence-scope.rejected-projection.json); sie ist nicht die Belegquelle für die Abnahme.
