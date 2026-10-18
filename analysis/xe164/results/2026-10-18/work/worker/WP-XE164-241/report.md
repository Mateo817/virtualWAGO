> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-241 — bounded offline dispatch analysis

## Ergebnis

**Gesamtstatus: OFFEN.** Für alle 23 zugewiesenen `indexed_pc_dispatch`-Zeilen sind die lokale `CMP`-Grenze, der unmittelbar folgende bedingte `LDRLS pc,[pc,index,LSL #2]`-Dispatch, die Default-Branch und alle quellseitigen LE32-Tabellenwörter verifiziert und mit dem gebundenen GNU-ARM-Disassembly verglichen. Jede Zeile ist in `dispatch-matrix.tsv` separat dokumentiert. Unter dem lokalen CMP→LDRLS-Guard ist die Tabellenkante konditional: Der LS-Transfer gilt für die unsigned Lower-or-Same Bedingung; die Tabelle allein beweist weder volle CFG-Reachability noch einen Laufzeit-Selectorpfad.

Die Frage nach einem statisch belegten Pfad, der einen `[base,#0x20]`-Load und sichtbar `r0=15` zum selben registerindirekten `blx` führt, bleibt offen. Der begrenzte, call-konservative Scan fand über 19 geprüfte Dispatchzeilen in 14 eindeutigen REA-Funktionskörpern keinen solchen same-site Kandidaten; vier weitere Dispatches haben im eigenen Ghidra-Provider keine zugehörige Procedure (`not_in_procedure`) und sind BLOCKED. Es gibt daher keinen globalen Positiv- oder Negativschluss. Ein sichtbarer Immediate-Scan auf `mov`/`movw r0,#15` innerhalb des exakt zugewiesenen ELF-VA-Fensters ergab null Treffer; andere Konstruktionen oder Werte aus Daten und Calls sind damit nicht ausgeschlossen.

## Identität und Umfang

- ELF: `codesys3`, 5,181,396 Byte, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.
- Exakter Analysebereich: ELF-VA `[0xc58e4,0x154dc4)`; keine angrenzenden Gap-Zeilen oder Nachbarbereiche ausgewertet.
- Genau 23 Zeilen mit `kind=indexed_pc_dispatch` aus `WP-XE164-234/cfg-gap-inventory.tsv` (SHA-256 `da464c51810a1a728eccddd7b6141e56502b8f7368dec55b9149a418b8bc40f3`).
- Gebundene Eingabe für lokale Dekodierung und Rohwort-Gegenprüfung: `WP-XE164-234/bounded.objdump.txt` (SHA-256 `a0bcaec911083963c573bead0b28ee8c0b3106c3b8aa5eb595a556fbc5e75110`). GNU ARM objdump 2.44; VA/Fileoffset-Abbildung mit Bias `0x10000`. Python 3.13.5.
- REA-Ziel wurde im eigenen REA-Client als genau dasselbe ELF mit Provider Ghidra geöffnet; exportierte Records binden Quellhash, Provider Ghidra 12.1.4 und Analysis-Profile `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

## REA-first und begrenzter Fallback

Für alle 23 Dispatchadressen wurde REA zuerst auf `read_function_instructions` abgefragt. 19 Abfragen lieferten Instructions und Function-Body-AddressSets; vier Antworten schlugen mit „No procedure exists“ fehl. Die anschließende `resolve_containing_procedure`-Prüfung bestätigte für genau diese vier Adressen `found=false`, `reason=not_in_procedure`; die jeweiligen Evidence-IDs sind in `dispatch-matrix.tsv` referenziert und vollständige Records in `rea-evidence.json` enthalten. Ein früher `analyze_function`-Aufruf einer Symbolmarke überschritt das Zeitfenster und wurde beendet. Die 13 Inventar-Symbolmarken wurden außerdem gegen Ghidras Procedure-Namen geprüft; exakte `@@Base`-Namen wurden vom Provider nicht angenommen. Deshalb stützen sich die verwertbaren REA-Körper auf die 19 adressbezogenen Function-Reads, nicht auf erfundene Symbolgleichsetzungen. Danach wurde ausschließlich die bestehende, hashgebundene lokale Disassembly für das zugewiesene Fenster als Fallback genutzt.

Die vier Provider-Gaps liegen bei `0x12ea08`, `0x135da4`, `0x136d84` und `0x144574`. Sie bleiben BLOCKED, auch wenn ihre rohen Tabellenwörter/Targets unabhängig verifiziert sind.

## Dispatch- und Tabellenbefunde

Für jede der genau 23 Matrixzeilen bestätigt der Validator:

1. Inventar-VA und VA/Fileoffset-Abbildung stimmen überein.
2. Direkt vor dem Dispatch steht ein adressbenachbartes `CMP` auf demselben Indexregister mit Immediate `n`.
3. Der Dispatch ist `LDRLS pc,[pc,index,LSL #2]`; direkt danach liegt die Default-Branch.
4. Die PC-relativ berechnete Tabellenbasis ist `dispatch VA + 8`; es wurden `n+1` little-endian 32-bit Wörter gelesen.
5. Jedes Rohwort stimmt mit dem dekodierten Wort an derselben Adresse überein. Insgesamt sind es 305 Wörter; alle 305 Werte liegen als Zieladressen im exakt zugewiesenen ELF-VA-Bereich.

Das sind Bytes, lokale Guard-Beziehung und Tabellen-Target-Werte. `SCANNED` in `flow-coverage.tsv` bezeichnet nur, dass der beschriebene konservative lokale Graph-Scan den Dispatch und die dekodierten Tabellenziele innerhalb des jeweiligen REA-Body-AddressSet erreicht hat. Es bedeutet keine vollständige CFG, keinen Laufzeitpfadbeweis und keine Auflösung indirekter Kontrollflüsse. Für vier nicht vorhandene REA-Bodies ist der Coverage-Status `BLOCKED`.

## Begrenzter Load/r0/blx-Scan und Unsicherheit

Der reproduzierbare Validator verknüpft auf dem bounded GNU-ARM-Decode nur direkt dargestellte Registerkonstanten aus unterstützten `mov`/`movw`/`movt`-Formen sowie sichtbare Loads mit Displacement `#0x20` und Register-`BLX`-Sites. Unbekannte Instruktionswirkungen werden konservativ als unbekannt weitergereicht. Jeder `BL`/`BLX`-Rückkehrpunkt invalidiert im Scan **alle** allgemeinen Registerwerte; es wird keine ABI-Erhaltung und kein Cross-call-Wert unterstellt. Bedingte Instruktionen und Branches werden überapproximiert; nicht dekodierte oder indirekte Ziele, Tabellen-/Speicherinhalte, Eingabewerte sowie semantische Typen werden nicht rekonstruiert. Der sichtbare `r0=15`-Immediate-Suchbereich ist exakt `[0xc58e4,0x154dc4)` und prüft geparste Mnemonik/Operanden für `mov` und `movw` samt Bedingungssuffixen. Der Validator prüft die Predicate-Erkennung zusätzlich an synthetischen `mov r0,#15`- und `movwne r0,#0xf`-Zeilen; der reale gebundene Decode enthält 0 passende Schreibformen.

Ergebnis dieses eingeschränkten Tests: 0 same-site Kandidaten, 19 geprüfte Dispatchzeilen in 14 eindeutigen REA-Bodies, 4 Provider-Gaps. Die Spalte `body_reachable_instruction_addresses` in der Coverage-Tabelle wiederholt pro Dispatch die Instruktionsabdeckung seines Bodys; diese Zeilenwerte dürfen daher nicht über Dispatches aufsummiert werden. Der Validator zählt eindeutige Body-Einträge separat und summiert keine mehrfachen Reachability-Zahlen. Das ist ein begrenzter statischer Nullfund unter den dokumentierten Darstellungs- und Kontrollflussannahmen, keine Aussage, dass keiner der 23 Dispatches einen solchen Pfad haben kann.

## Artefakte und Reproduktion

- `dispatch-matrix.tsv`: exakt 23 Zeilen, je Status OFFEN mit Fundstelle, Tabellenwörtern/-targets, Alternativerklärung und Restunsicherheit.
- `flow-coverage.tsv`: je Dispatch erreichte Procedure/Targets oder konkreter Provider-Gap.
- `flow-results.tsv`: same-site Kandidaten; derzeit nur Header, weil der begrenzte Scan keine Kandidaten meldete.
- `rea-evidence.json`: vollständige exportierte Evidence-Records für 19 Instruction-Reads und 4 Procedure-Gap-Queries.
- `validate.py`: rekonstruiert Ergebnisse im Speicher und vergleicht im Defaultmodus bytegenau die vorhandenen TSVs; der Default ist nicht mutierend. `python3 validate.py --write` ist der explizite Generatorlauf. Validator und Ausgabe binden ELF-/Gap-/Disassembly-Hashes, REA-Quelle, Provider/Version, Profile, Queryparameter und Function-Body-Ranges. Das SHA-256-Manifest schließt sich selbst aus.

Verifikation: `python3 validate.py --write` PASS, danach `python3 validate.py` PASS (read-only). Keine Hardware-, VM- oder Netzwerkaktion.
