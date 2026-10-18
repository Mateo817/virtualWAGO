> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-042 — Kontrollfluss am Seed E01E26

## Ergebnis

**HYPOTHESE — bedingte statische Erreichbarkeit.** Rizin dekodiert ab dem Seed E01E26 eine lückenlose Folge von 114 Instruktionen bis E01F96, mit Dateioffsets 0x1E26 bis 0x1F97. In dieser linearen Dekodierung gibt es keine bedingten oder unbedingten Sprünge. Die einzigen lokalen Kontrollfluss-Schnittstellen sind drei direkte CALLS-Instruktionen; Rizin weist für jede eine Fortsetzung nach dem Call aus. Die Folge endet mit RETS bei E01F96, unmittelbar vor der ausgeschlossenen Grenze E01F98. Erreichbarkeit hinter jedem Call setzt die Rückkehr des jeweiligen, hier nicht untersuchten Ziels voraus.

## Identität und Methode

- Eingabe: XE164-composite-e00000.bin, 17,110 Bytes, SHA-256 5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983.
- Syntaktische Adressabbildung: Datei-Offset 0 wird auf E00000 abgebildet; E01E26 entspricht Offset 0x1E26. Rizin-Map: FD 3, Größe 0x42d6, physischer Offset 0, virtueller Start E00000.
- REA: rea-agents 6.5.0, MCP client 0.162.1, Catalog SHA-256 405725e736ec8dc8483435b970acbf20f9f26b9f1fd25203b992f5ab4cd2a4f4. Der Versuch mit open_binary wies das headerlose Eingabeartefakt als unsupported format ab (BLOCKED; kein C166-Raw-Profil in dieser Route).
- Vorgesehener lokaler Fallback: Rizin 0.9.1, commit c3a90e9226d977f58f4e9c75f78fa6b07afe13c7; über REA execute_rizin_command mit asm.arch=c166, asm.bits=16 und expliziter Raw-Map.
- Bereichs-Observation: ev_4507f7d5f18ed78c7230d3391932b1b53512c66250218372b1eb2206adab4202. Caller-Observation: ev_8f6c4fb581ab140f4d25b2efcedc8e1cd03271ad98ffdd17771d803d068c225d. Beide REA-Resultate meldeten unveränderte Quellbytes.

## Exakte Kontrollflussstruktur

| Block | Adressbereich (Ende exklusiv) | Dateioffset | Instruktionen | Terminale Kodierung | Ausgehende Kante |
|---|---|---:|---:|---|---|
| B1 | E01E26–E01F64 | 0x1E26–0x1F64 | 99 | E01F60: dae0100d, CALLS E00D10 | Callziel außerhalb der Analyse; Fortsetzung E01F64 falls der Call zurückkehrt |
| B2 | E01F64–E01F92 | 0x1F64–0x1F92 | 13 | E01F8E: dae0101e, CALLS E01E10 | Callziel außerhalb der Analyse; Fortsetzung E01F92 falls der Call zurückkehrt |
| B3 | E01F92–E01F96 | 0x1F92–0x1F96 | 1 | E01F92: dae0fa1d, CALLS E01DFA | Callziel außerhalb der Analyse; Fortsetzung E01F96 falls der Call zurückkehrt |
| B4 | E01F96–E01F98 | 0x1F96–0x1F98 | 1 | E01F96: db00, RETS | Rückkehr zur Caller-Fortsetzung E03646 gemäß isolierter Callsite |

Die [Instruktionstabelle](instructions.csv) enthält alle 114 Dekodierungen und Einzelbytes; [cfg.csv](cfg.csv) bindet Blockgrenzen und Kanten. Die Instruktionsgrößen ergeben exakt 0x172 Bytes: Dateioffset 0x1E26 bis ausschließlich 0x1F98. Die letzte erfasste Instruktion beginnt bei E01F96, Offset 0x1F96, Bytes db00. Bei E01F98 wurde keine Instruktion dekodiert.

Isolierter Caller: Die [Caller-Tabelle](caller_edges.csv) hält bei E03642 die Bytes dae0261e (CALLS E01E26) und an Fortsetzung E03646 die Bytes dae0981f (CALLS E01F98) fest. Für diesen Zusammenhang wurden nur diese 8 Caller-Bytes dekodiert. Das Ziel E01F98 wurde nicht geöffnet oder analysiert.

## Beobachtung, Alternative und Restunsicherheit

**VERIFIZIERT:** Eingabegröße und SHA-256 stimmen mit der Vorgabe überein. Die isolierte Caller-Instruktion adressiert E01E26. Der begrenzte lineare Rizin-Output enthält 114 Instruktionsstarts mit lückenloser Byteabdeckung und endet vor E01F98 mit RETS. Als Kontrolltransfer sind in diesem Output nur drei CALLS und ein RETS ausgewiesen.

**Alternative Erklärung — HYPOTHESE:** Die gewählte Seed-Adresse könnte bei einer anderen Abgrenzung Daten oder den Einstieg in einen größeren oder überlappenden Bereich markieren. Eine einzelne lineare Dekodierung plus syntaktische Caller-Kante beweist weder Funktionsgrenzen noch, dass jeder nachfolgende Call zurückkehrt.

**Restunsicherheit — OFFEN:** Für diesen Work-Package-Scope wurde keine unabhängige zweite Disassemblierung oder Execution erhoben. Die drei Callziele außerhalb des Untersuchungsbereichs wurden nicht verfolgt; daher ist die Fortsetzung über jeden Call hinaus nur eine mögliche statische Kante. Die Aussage betrifft ausschließlich den Bytecode unter der angegebenen syntaktischen Abbildung, nicht ABI, Bedeutung oder tatsächliches Verhalten.

## Validierung und Artefakte

validate.py prüft Quellhash und -größe, Byte-für-Byte-Übereinstimmung und lückenlose Abdeckung der Instruktionstabelle, Caller-Bytes, CFG-Grenzen sowie die zwei gebundenen REA-Evidence-IDs samt Zielhash. Ergebnis: **PASS**.

Erzeugte Dateien und SHA-256 stehen in SHA256SUMS; die Liste bindet Bericht, Tabellen, Validator und das finding-only REA-Bundle.
