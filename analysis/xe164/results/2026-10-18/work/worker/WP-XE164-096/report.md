> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-096 — Dispatch-Prädikate und Statuspfade

## Ergebnis

**VERIFIZIERT** (statische Ghidra-Beobachtung): Beide Dispatches sind nur innerhalb des Hauptzweigs param_1 != 0 und *(param_1+0x61c) != 0 erreichbar. Die Record-Tabelle beginnt bei param_2+0x10, die Anzahl steht bei param_2+0x0c, die Iteration geht in Schritten von 0x14 Bytes. Die erste 32-Bit-Zelle und die 16-Bit-Zelle bei Record-Offset +8 sind die beobachteten Discriminator-/Typvergleiche; daraus wird keine Parameternamenssemantik abgeleitet.

REA/Ghidra identifiziert den vollständigen zusammenhängenden Procedure-Body 0x1277c..0x12e7f, inklusive Endadresse, 1796 Bytes. ELF-Virtual-/Ghidra-Adressen liegen für den Code um 0x10000 über den entsprechenden Dateioffsets: 0x12bb4 ↔ file 0x2bb4 und 0x12d6c ↔ file 0x2d6c. Die Auswertung bleibt in diesem Body. Angrenzende Pool-/Datenadressen werden nur als referenzierte Eingaben erwähnt.

## Rückwärtsslices: Guards, Werte und Dispatch-Argumente

| Dispatch und Adresse (Dateioffset) | Vorbedingungen und konkrete Discriminator | Aufrufargumente aus Ghidra-Pseudocode/Assembly | Ergebnis am ersten gemeinsamen Statuspfad |
|---|---|---|---|
| libpackbus_get_uid, 0x12bb4 (0x2bb4) | Hauptgates: param_1 != 0 und *(param_1+0x61c) != 0. Im Hauptloop muss param_3 == 1 gelten oder der alternative Slot-Zweig erfolgreich sein. Der Slot uVar19 muss beim Record >= 0 (signed Test) sein. Record-Zelle *piVar17 == 10. Die 16-Bit-Zelle [record+8] ist 4 oder 12: Ghidra-Ausdruck ((type-0x0c)&0xfffb)==0 führt für type!=0x10 zum DWORD-Accessor; type==4 führt ebenfalls dorthin. Accessor-Status local_34 muss 0 sein. | Funktionszeiger bei *(iVar12+0x70). Quellen: Name libpackbus_get_uid; &local_30 als Dispatch-Ausgabe 1; aktueller Slot uVar19; local_2c als Dispatch-Ausgabe 2, deren erste Zelle verglichen wird. Assembly: blx r7 bei 0x12bb4, Slot in r2, Ausgabezeiger im Stackargument. | Nur wenn äußerer Dispatch-Rückgabewert iVar10 == 0, local_30 == 0 und der aus dem Record gelesene DWORD iVar9 == local_2c[0], setzt der Loop-Akkumulator uVar18=0x20 und fährt mit den Records fort. Fehler springen zu 0x127b0, setzen uVar19=1 und uVar18=0. Der gemeinsame Pfad bildet dann uVar15=0x10, ORt 0x10 in [param_2+4] und gibt 0x10 zurück. |
| libpackbus_read_conf_reg, 0x12d6c (0x2d6c) | Gleiche Hauptgates und Slot-Schleife. Record-Discriminator *piVar17 liegt mit unsigned Vergleich record_value-0x0b < 10 im Bereich 11..20 inklusive. [record+8] == 5; Pointer-Accessor mit &local_34 muss local_34==0 und einen nichtnull Pointer liefern. Pointer-Bytes +5==0 und +6==0; Byte +7 erfüllt (flags&0xec)==0. Der externe Dispatch wird nur bei zusätzlich (flags&0x10)==0 genommen. cVar2 ist Byte [pointer+4]. | Funktionszeiger erneut bei *(iVar12+0x70). Quellen: Name libpackbus_read_conf_reg; local_2c als innere Ausgabe; uVar19 Slot; cVar2 aus [pointer+4]; &local_30 als weitere Ausgabe. Assembly: blx r12 bei 0x12d6c. | Vergleich erst bei äußerem Dispatch-Rückgabewert iVar9==0 und innerer Ausgabe local_2c[0]==0. Verglichen werden local_30 und [pointer+2] als 16-Bit-Werte, unter Maske *pointer und Modus flags&3. Erfolg setzt keinen eigenen Status, sondern erhöht den Recordzeiger um 0x14 und fährt fort. Äußerer Fehler, innere Fehlerausgabe, ungültiger Pointer/Guard oder Comparator-Miss führen zu 0x12cfc: uVar19=1; gemeinsamer Pfad 0x127b8 setzt Statuswert 0x10, ORt ihn in [param_2+4] und liefert 0x10. |

Der alternative Eingangs-Zweig (param_3 != 1) fragt pfIoMgrConfigGetParameter(param_2, 4) ab. Nur bei nichtnull Parameter und 16-Bit-Zelle +8 == 2 wird ein Bytewert gelesen. Der beobachtete Gate-Ausdruck akzeptiert Werte 1..0xfa nur bei Accessor-Fehlerzelle local_34==0, danach zusätzlich value <= DAT_000291d0; der Sonderfall value==0xfa passiert die Statuszelle ohne diese Nullprüfung. Ghidra-Bytes an 0x291d0 sind fa000000e0910200; der erste little-endian DWORD ist 0x000000fa. Erst dann wird dieselbe Record-Schleife erreicht. Dies sind rohe Konstanten, keine semantischen Typzuweisungen.

## Vergleichsbedingungen für den Read-Dispatch

Ghidra deutet flags als Byte [pointer+7], M als *pointer, E als word [pointer+2] und R als 16-Bit-Wert local_30. Der Modus ist m=flags&3.

| m | Bedingung zum Fortsetzen der Schleife | Fehlkante |
|---:|---|---|
| 0 | ((R XOR E) AND M) == 0 | ungleich maskiert → 0x12cfc |
| 1 | (R AND M) < (E AND M) | gleich oder größer → 0x12cfc |
| 2 | (R AND M) > (E AND M) | gleich oder kleiner → 0x12cfc |
| 3 | ((R XOR E) AND M) != 0 | gleich maskiert → 0x12cfc |

Modus 3 unterscheidet sich im Gleichheitsfall von Modus 0. Es wird kein fachlicher Operatorname behauptet. Wenn flags&0x10 gesetzt ist, wird der externe Dispatch umgangen: nur cVar2==0 bzw. cVar2==1 wählt die entsprechenden geladenen Tabellenzugriffe; andere Werte führen zu 0x12cfc. Tabellenbytes an 0x29208/0x2920c und weitere Poolbereiche waren über Ghidra read_bytes nicht initialisiert/verfügbar. Die Inhalte bleiben OFFEN; der Report nennt nur Indexformeln und Guards, keine Tabellenwerte oder Semantik.

## Gemeinsamer und terminaler Statuspfad

Nach einem erfolgreichen UID-Record bleibt uVar18=0x20; nach Ende der Records wird bei uVar19>=0 der Wert 0x40 ergänzt. Nur uVar15=uVar18|0x10==0x70 erreicht den besonderen Terminalzweig. Dort prüft der Code das Feld [DAT_0002a2d8+(uVar19-1)*0xc00+4] und ruft bei Null idk_CheckTerminalPiSize(param_2, tableA[slot-1], tableB[slot-1]) auf.

- Feld Null und idk_CheckTerminalPiSize liefert 0: [param_2+8]=param_1, Status-OR-Wert uVar18|0x90, Rückgabewert 0.
- Feld Null, Check liefert nicht 0: Status-OR-Wert (uVar18&~0x40)|0x10; Rückgabewert ist der nichtnullige Rückgabewert des Checks.
- Feld nicht Null: 0x70 bleibt der in [param_2+4] zu ORende Wert; Rückgabewert wird auf 0x10 gesetzt.
- uVar15 ungleich 0x70: Rückgabewert 0x10 und OR des aktuellen Statuswerts in [param_2+4]. Die konkreten Dispatch-Fehlerpfade kommen mit uVar15=0x10 an.

Eine frühere Dispatch-unabhängige Vorprüfung scannt Records ebenfalls mit Schrittweite 0x14. Bei *record==7, [record+8]==0 und Byte-Accessor-Rückgabe ungleich null bei local_2c[0]==0 kehrt das Verfahren früh mit 0 zurück. Zwei Discriminatorbereiche werden gezählt: *record-0x01000000 < 0x02000000 bzw. *record+0xfd000000 < 0x02000000. Überschreitet eine Zählung 0x30, wird [param_2+4]|=0x200 und das Rückgabeziel 0x1a erreicht. Diese Vorprüfung kann die Dispatches vor ihrem Hauptzweig abbrechen.

## Evidence, Grenzen und Status

- VERIFIZIERT: Procedure-Body/Bereich durch Ghidra FunctionManager; Aufrufstellen und Guards durch Ghidra-Pseudocode und disassemblierte Instruktionen. Evidence: ev_25b965e867e7e080ae7f538d2d3c8494926026183f299d60218f09bbc6802002, ev_452305961efe6bbf6724af9b3337823cc20a7de5c3b7441f6646faa52cebf260.
- VERIFIZIERT: Assemblyseiten mit Calls und nachfolgenden Branches: ev_f135cf920556bc60d03b7051f7964fec2c3986fcc955f29f5640861f1bf02b72 (UID-Kontext), ev_3b6a3f28ebaa00ce95288be3e8f2b16f05515974472fe2e82383a16d40ea3db3 (Read-Kontext), ev_0685df988e9d350cfc6fe2e10e5400dd1d2c4e709d728d2ad0a39463417eaad5 (Procedure-Ende), plus ev_a10ec82c1e2b13ed0a3931d40b0f15c005a27e00bcf79af5ffe982e31409dc05 und ev_2cac92c28aac75edba921ad7eca8424d0f16c557c441e4d9b9771d5fa0104aed.
- VERIFIZIERT: DAT_000291d0 Bytes und Initialisierungsgrenze: ev_46bf93fa2d82256f23cf2198b7910381c1232068740aaf671a144b813841fb87.
- OFFEN: Inhalte der alternativen flags&0x10-Tabellen-/Poolpfade. Ghidra meldete die Bytes an 0x29208, 0x29210, 0x29218 und 0x2a2d8 nicht initialisiert/verfügbar: ev_13bb68e605fe592137751a31d494f13c7c03e44acb16022c50dbf8d9061ff2ee, ev_3b19deea8b487ae8ea6186106227ed8193448f584ab287d8131887d580fb4028, ev_57cc98eec983f8ea77e5ca6374ad9472a64143ace85ea76d0c9cfdd53ea36309 und ev_9f8fcdc20e3f38c59bf195b7b2c82afa37f859150b4ebb38a27b765c69b99825.
- Alternativerklärung: Ghidra-Pseudocode ist decompiler-abgeleitet; Register-/Stackvariablen und Argumentdarstellung indirekter Calls können ABI-/Decompilerartefakte enthalten. Die call-nahen Assembly-Instruktionen stützen Guard- und Ergebnisbranchs, belegen jedoch keine Laufzeit-Ausführung.
- Restunsicherheit: Kein semantisches Mapping für rohe Recordwerte, Flags oder Pools; keine Behauptung zur Zielprofil-Reachability ohne externe Mappingquelle. Providerkörper/Dispatch-Implementierungen sind nicht untersucht.

Tool: REA/Ghidra 12.1.4; Analysis Profile Digest 7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de. Eingabe ELF-Größe 38584, SHA-256 543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8. Das kanonische Bundle rea-evidence-bundle.json enthält 12 Records und 0 Unknowns. Der semantische Validator prüft Hash, Recordzahl, Unknownzahl, Provider, Scope und zitierte Evidence IDs.

## Teststatus

- REA/static evidence capture: PASS
- Binary execution/runtime test: NOT_RUN
- Target-profile reachability: NOT_RUN (keine Mappingquelle im Work-Package-Scope)
