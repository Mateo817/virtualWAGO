> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-081 — FW31 `IoDrvKbus` callback at ELF VA/file offset `0x2704`

## Ergebnis

**VERIFIZIERT:** Der Kandidat bei geladener Adresse `0x12704` ist eine 112-Byte-Funktion `FUN_00012704`. REA ordnet dieser Adresse Dateioffset `0x2704` zu; laut Eingabe stimmen dort ELF-VA und Dateioffset überein. Der einzige erkannte ausgehende Call ist `blx r3` bei `0x12758`. Der Caller lädt zuvor `libpackbus_Push`, übergibt die Adresse einer mit `param_2` initialisierten lokalen Zelle und prüft nach dem Call sowohl dessen äußeren Rückgabewert als auch den neu gelesenen Zellwert. Das belegt den caller-seitigen Push-Pfad; die Provider-Implementierung des benannten Handlers wird hier nicht untersucht.

**VERIFIZIERT:** `IoDrvKbus_Init` referenziert die Kandidatenadresse als Datenwert bei `0x14868`; sein dekompilierter Store schreibt einen 64-Bit-Wert `0x136c000012704` ab `param_1+0x3c`, dessen Low-Word `0x12704` ist. Das belegt einen veröffentlichten Funktionszeiger im Callback-Werteblock, nicht einen direkten Code-Call. Die genaue Bedeutung der benachbarten Felder wird nicht aus den Offsets abgeleitet.

**OFFEN:** Ob `*(short *)(DAT_0002920c+4)` oder `param_2` fachlich genau den vorherigen `WriteEnd`-Status darstellen, ist aus den verfügbaren lokalen Aufruf-/Referenzbelegen nicht entscheidbar. Der Binärcode belegt nur die folgenden Bedingungen: fehlender globaler Zeiger führt zu `3`; ein nichtnulliges 16-Bit-Feld bei `DAT_0002920c+4` führt zu `12`; nulles erstes Argument oder `param_2==0` führt zu `2`. Die Statussemantik dieser Werte bleibt unbenannt. Falls ein externer Callback-Vertrag `param_2` als vorheriges `WriteEnd`-Ergebnis definiert, wird bei `param_2==0` der Push-Pfad übersprungen und `2` zurückgegeben; bei `param_2!=0` ist dieser Guard passiert.

## Beobachtung

- Eingangshash geprüft: `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`, 38 584 Bytes; **PASS**.
- Koordinatenabbildung REA: geladene Adresse `0x12704` → Dateioffset `0x2704`, `ev_20491a1c61330bcb5b64af30305e4c89351ac78b22631b3c88a08d87c5adbaf7`. Funktionskörper `0x12704..0x12773` inklusiv, 112 Bytes. Dossier mit Pseudocode, kompletter Assemblerliste, Stringreferenz, Call, Guards, CFG und Wertfluss: `ev_f1d3890d6dd0d06557df036599b38281c6aa29436635b495809cbbad62fbe878`.
- Eingehende Referenzen enthalten drei interne bedingte Sprünge zum gemeinsamen Epilog und einen `DATA`-Verweis aus `IoDrvKbus_Init` bei `0x14868`; kein eingehender `CALL`-Verweis. Die direkte Caller-Abfrage liefert leer. Evidence: `ev_f1d3890d6dd0d06557df036599b38281c6aa29436635b495809cbbad62fbe878`, `ev_6a7ebaa76fab927ca4b9d9de00f4552fdfd92defea97bd67341605c6c6890cac`.
- Init-Publikation: `IoDrvKbus_Init` bei `0x147fc` speichert laut Pseudocode `0x136c000012704` ab `param_1+0x3c`; der Kandidatenzeiger ist durch die incoming `DATA`-Referenz bei `0x14868` gebunden. Evidence: `ev_5959ab945c4e15c6d011169876dbb4659cf754c2dfee61b49f02876e430ce`, `ev_f1d3890d6dd0d06557df036599b38281c6aa29436635b495809cbbad62fbe878`.
- Push-Zuordnung beruht auf String- und Kontrollflussbelegen aus demselben Dossier: Stringobjekt `libpackbus_Push` wird als Call-Argument geladen, danach kommt der einzige berechnete `blx r3` bei `0x12758`; der aufgerufene Zeiger wird aus `*(int *)(*param_1+0x61c)+0x70` geladen. Die Adresse von `local_c`, initialisiert aus `param_2`, wird übergeben und danach getrennt vom äußeren `r0` ausgewertet. Ghidra-Typen und Pseudocode bleiben Werkzeugableitungen, keine Herstellerdeklarationen. Evidence: `ev_f1d3890d6dd0d06557df036599b38281c6aa29436635b495809cbbad62fbe878`.
- Der Call ist dynamisch/indirekt. Ein statisches Ziel und der vollständige Vertrag des Callbacks hinter diesem Zeiger sind nicht beobachtet. Ghidra meldet bei der Dossier-Calleeabdeckung einen ungelösten indirekten Call; das ist kein Nachweis über das Laufzeit-Ziel.
- Die begrenzten Prozedurnamensuchen `WriteStart` und `WriteEnd` fanden keine so benannten Prozeduren. Das sagt nichts über unbenannte oder indirekte Callback-Rollen aus. Evidence: `ev_8ee41ea2fce3c0444325ec3eefa328b4766b7ba44fd5ee6e2829bd67ba0fafc7`, `ev_798b9e24a2d29dad48d4f4d385e43250537996736d8d743e16f0feb4d9169be4`.

## Schlussfolgerung und Rückgabewert

**VERIFIZIERT:** Die Entscheidung lässt sich durch die Zeilen in `flow.tsv` vollständig für den analysierten Funktionskörper ausdrücken.

1. `DAT_0002920c == 0` → `r0=3`, gemeinsamer Return.
2. Andernfalls wird ein 16-Bit-Wert bei `DAT_0002920c+4` geladen. Ist er ungleich null → `r0=12`, gemeinsamer Return.
3. Andernfalls: `param_1==NULL || param_2==0` → `r0=2`, gemeinsamer Return.
4. Sonst erfolgt genau ein indirekter Call mit Push-Identifikator. Danach ist `r0` das äußere Call-Ergebnis; `local_c` wird erneut aus dem Stack gelesen und ist die innere, per Pointer zurückgegebene Ergebniszelle. `r0==0 && local_c==0` → Return `0`; alle übrigen Kombinationen → Return `1`.

Damit sind äußeres und inneres Push-Ergebnis logisch getrennt, aber durch die abschließende OR-Verknüpfung gleich gewichtet: nur `outer==0` **und** `inner==0` ergibt Rückgabewert `0` (Nullrückgabe). Ein einzelnes Nichtnull-Ergebnis liefert `1`. Der vorherige `WriteEnd`-Status ist als solcher **OFFEN**; er beeinflusst den Return nur dann, wenn er durch den externen Aufrufer als eines der beobachteten Guard-Inputs übergeben wird. Bedingte Beziehung: ein als `param_2` übergebener Nullwert bewirkt `2`; ein nichtnulliger `param_2` lässt den Ablauf nach den vorherigen Guards zum Push-Call weitergehen.

## Alternative Erklärung und Restunsicherheit

Die Funktion kann eine allgemeine Rückruf-/Dispatch-Hülle sein, bei der `param_2` lediglich ein beliebiger erforderlicher Eingabewert und `DAT_0002920c+4` ein separates Freigabe-/Zustandsfeld ist. Der Binary-Befund allein nennt diese Felder nicht `WriteEnd`. Das externe WriteEnd-zu-Callback-Argument-Mapping sowie der Vertrag, der `local_c` durch den indirekten Callback befüllt, bleiben **OFFEN**. Keine Aussage zu Handler-Interna, Runtime oder Geräteverhalten.

## Toolprofil und Prüfgrenze

- Primärtool: REA 6.5.0 MCP, Provider Ghidra 12.1.4; ARM:LE:32:v8; Image-Base `0x10000`; Analyseprofil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- REA zuerst in einer frischen ephemeren Sitzung auf demselben Artifact-Hash: `open_binary`, `address_to_file_offset`, `analyze_function` (nur Kandidat und Init), `procedure_callers` (nur Kandidat), `search_procedures` (`WriteStart`, `WriteEnd`) und `export_evidence_bundle`.
- Keine `readelf`-/`objdump`-Fallbackanalyse erforderlich: der Funktionskörper ist im REA-Dossier vollständig dekodiert (112 Bytes) und CFG/Branches/Call/Return sind ausgewiesen. Keine Geräte-, Netzwerk- oder VM-Aktion.
- Das separate Werkzeugprofil mit Loaderdomäne, Coverage und verwendeten Operationen steht in `tool-profile.md`.
- Pseudocode ist Werkzeugableitung, keine Originalquelle. Keine API, Strukturdefinition, Offsetsemantik oder Handlerfunktion wurde erfunden.

## Evidenz-IDs

Die frische, scope-reine REA-Sitzung enthielt genau 6 Records; ihr unveränderter kanonischer Export steht in `evidence-bundle.json`. Bericht und Tabellen zitieren ausschließlich IDs dieses Bundles. Das frühere 65-Record-Bundle ist separat als `evidence-bundle-rejected-audit-65.json` aufbewahrt, ausdrücklich **nicht** Befundbasis und im Manifest als `BLOCKED` markiert; es enthält außerhalb des vereinbarten Umfangs liegende explorative Analysen.
