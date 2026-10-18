> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-047 — Seed-Kontrollfluss E00D10 bis E00DAA

## Ergebnis

**VERIFIZIERT (statisch, begrenzte syntaktische C166-Dekodierung):** Vom isolierten Aufruf bei `E01F60` führt der syntaktische `CALLS`-Operand zu `E00D10`. Im vorgegebenen Bytefenster `0x0D10..0x0DA9` dekodiert Rizin 51 lückenlos aneinandergrenzende Instruktionen über exakt 154 Bytes. Es gibt darin keine bedingte oder unbedingte Sprunginstruktion. Zwei direkte `CALLS` gehen zu Zielen außerhalb des untersuchten Umfangs (`E00C72`, `E03ABA`); bei Rückkehr verläuft die Folge an `E00D16` bzw. `E00D6C` weiter. Sie endet mit `RETS` bei `E00DA8`, dessen zwei Bytes genau bei `E00DAA` enden. `E00DAA` und seine Nachbarn wurden nicht eingelesen.

Die lineare Dekodierung und die Seed-Erreichbarkeit sind getrennt markiert: Alle 51 Tabellenzeilen sind im linearen Fenster dekodiert. Vom Seed ist `E00D10` direkt erreicht; spätere Instruktionen sind entlang der Fall-through-Folge erreichbar, jeweils unter der Bedingung, dass vorangehende `CALLS` zurückkehren. Es wurde keine weitere, vom Seed getrennte lineare Komponente innerhalb des Fensters beobachtet. Das schließt überlappende alternative Einstiege oder nicht erkannte Dekodierinterpretationen nicht aus.

## Beobachtungen und Fundstellen

- Eingabe vor Analyse geprüft: 17.110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- REA `open_binary` wurde zuerst auf genau diese Eingabe angewandt. Ergebnis: `target_unavailable / unsupported binary format`. Die aktive REA-Raw-Binary-Auswahl bietet keine C166-Architektur; deshalb wurde keine andere Architektur substituiert.
- Nach der beobachteten REA-Lücke wurde der dokumentierte Rizin-C166-Fallback über REA `execute_rizin_command` verwendet. Rizin-Version: `0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`; REA-Providerfeld `version` ist `null`.
- Dekodierprofil: `asm.arch=c166`, `asm.bits=16`, `asm.cpu=xe164`, `cfg.bigendian=false`, `io.va=false`, `scr.color=0`. Begrenzter Aufruf: `px 0x9a @ 0x0d10; pD 0x9a @ 0x0d10; pd 1 @ 0x1f60`. Exit-Code 0, stderr leer, Ausgabe nicht abgeschnitten, Artefakt unverändert; Eingabehash nachher identisch.
- Der isolierte Caller wurde in einem gesonderten Aufruf mit genau vier Bytes und einer Instruktion abgefragt: `px 4 @ 0x1f60; pd 1 @ 0x1f60`. Rizin-Ausgabe: Bytes `DA E0 10 0D`, `CALLS 0xE00D10`.
- Der Export enthält die beiden zu diesem Befund gehörenden, vollständigen REA-Evidence-Datensätze: `ev_effaae3f6c7b9a631253e2a6f5bf3312972c703a6ba016dccfcf380e3e839c26` (Fenster plus Caller-Disassemblierung) und `ev_01e37eda792dc1050268bc6743668372db766020fd89cd3963eb81734f50f391` (Caller-Bytes). Das kanonische finding-only Bundle enthält zwei Records und keine Unknowns.
- [instructions.tsv](instructions.tsv) enthält alle Instruktionsstarts, Längen, Bytefolgen und Rizin-Texte; [edges.tsv](edges.tsv) enthält lokale Fall-through-, Call-, call-return-Fortsetzungs- und Terminalkanten. [caller.tsv](caller.tsv) enthält nur die angeforderte einzelne Caller-Instruktion.

## Alternative und Restunsicherheit

**HYPOTHESE (Alternative):** Die zusammenhängende lineare C166-Dekodierung kann eine alternative Instruktionsgrenze mit überlappendem Einstieg übersehen. Ein syntaktisch erreichbarer Caller beweist weder, dass der Code zur Laufzeit ausgeführt wird, noch dass er der einzige Caller ist. Die Fortsetzungen nach beiden `CALLS` setzen Rückkehr voraus; weder die Rückkehr noch die Kontrollwirkungen der Ziele wurden untersucht. Die als 154 Byte angenommene Ghidra-Größe wird durch die lückenlose Dekodierung und `RETS` unmittelbar vor `E00DAA` gestützt, aber nicht als Funktionsgröße oder exklusive Funktionseinheit bewiesen.

Es gab keinen zweiten unabhängigen Disassemblerabgleich und keine Laufzeit-, Emulator-, Geräte- oder Hardwareprüfung. Operandenbedeutungen, ABI, SFRs, Runtime- und Hardwareverhalten sind nicht Gegenstand dieser Aussage. Andere Caller, `E00DAA` und angrenzende Bytes bleiben ausdrücklich ausgeschlossen.

## Status

| Aussage | Status | Begründung / Umfang |
|---|---|---|
| Größe und SHA-256 der Eingabe | VERIFIZIERT | Vor und nach den Rizin-Aufrufen unverändert |
| Byteabdeckung und lineare Dekodierung | VERIFIZIERT | `0x0D10..0x0DA9`, 51 Instruktionen, Rizin 0.9.1 C166-Profil |
| Seed-Aufruf durch `E01F60` | VERIFIZIERT | Genau eine Caller-Instruktion samt vier Bytes |
| Seed-Erreichbarkeit der Folge | VERIFIZIERT | Statische Kanten; Fortsetzungen nach Calls jeweils rückkehrabhängig |
| Funktionsgrenze bei `E00DAA` | HYPOTHESE | `RETS` endet genau davor; Funktions-/Blockzugehörigkeit nicht unabhängig belegt |
| Eindeutigkeit der Caller, Laufzeitpfad, Operandenbedeutung | OFFEN | Nicht untersucht und außerhalb des Umfangs |

## Dateien und Prüfung

`instructions.tsv`, `edges.tsv` und `caller.tsv` sind die exakten Tabellen. `rea-evidence-bundle.json` ist der kanonische finding-only REA-Export. `validate.py` prüft Eingabehash, Eingabegröße, zusammenhängende Byteabdeckung, Tabellenbytes, Kantenumfang und Bundle-Auswahl. `SHA256SUMS` enthält Hashes aller Ergebnisdateien außer sich selbst.

Worker-Eigenprüfung: `validate.py` und SHA-256-Prüfung. Root Self-Review steht noch aus; es wird kein unabhängiger Review behauptet.

Prüfstatus: Validator `PASS`. Unabhängiger Decoderabgleich und Runtime-/Emulator-/Hardwareprüfung `NOT_RUN` (letztere außerhalb des Offline-Umfangs).
