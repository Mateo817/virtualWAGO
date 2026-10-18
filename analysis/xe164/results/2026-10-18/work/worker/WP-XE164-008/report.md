> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-008: Beziehung der Jump-Ziele E021AA und E021E0

## Ergebnis

**VERIFIZIERT (statische Struktur):** `E021AA` und `E021E0` liegen an zwei unmittelbar aufeinanderfolgenden, je 54 Byte langen C166-Basicblocks. Jeder Block beginnt mit derselben Save-Sequenz, endet mit `RETI`, und die disassemblierten Instruktionsfolgen sind bis auf genau ein Bitfeld-Operand identisch: `bset 0xFD00.0x5` bei `E021C4` gegenüber `bset 0xFD00.0x6` bei `E021FA`. Der zweite Block beginnt direkt nach dem ersten terminalen `RETI` und besitzt selbst ein terminales `RETI`; der Ghidra-Control-Flow-Modell lieferte zwischen ihnen keine ausgehende Kante.

Damit sind die beiden Ziele **keine zwei Blöcke derselben vom Analyzer erkannten Funktion**: Ghidra meldet für beide `FUNCTION=NONE`. Die Befunde passen strukturell zu zwei getrennten Entry-Targets mit wiederholtem Handler-Muster. Ob sie im Firmware-Kontext eigenständige Funktionen/Handler sind, bleibt **HYPOTHESE**, weil Ghidra keine Funktionseigentümerschaft erzeugt hat und die übergebene Jump-Tabelle nur Zieladresse und Zeilenindex, nicht die adressierende Quellinstruktion enthält. Eine gemeinsame Semantik folgt aus dem Muster nicht.

## Eingaben und Integrität

| Eingabe | Größe | SHA-256 |
|---|---:|---|
| `XE164-composite-e00000.bin` | 17110 B | `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` |
| `composite-replay.md` | 2169 B | `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5` |
| `Xe164Probe.java` | 4315 B | `9289f41396180a3478ce3e64e70f54d38a397e5f4f7247b89bd8e8bf2808490f` |

Der SHA-256 des Firmware-Composites blieb nach Rizin-Aufrufen unverändert. Die Zieladressen entsprechen bei Ghidra-Basis `0xE00000` den Dateioffsets `0x21AA` und `0x21E0`.

## Werkzeug und Konfiguration

- REA `execute_rizin_command` mit Provider Rizin. Die Profilantwort meldete Rizin-Version und erkanntes Format als unbekannt. `px 96 @ 0x21aa` und `px 96 @ 0x21e0` lieferten Rohbytes. `pd 24 @ 0x21aa` decodierte als x86 und produzierte für diese C166-Daten ungültige bzw. nicht aussagekräftige Befehle; diese Disassemblierung wurde nicht als Evidenz verwendet.
- Ghidra 12.1.4, `C166:LE:16:default`, Compiler Spec `tasking`, Raw Binary Loader, Base Address `0xE00000`, `-readOnly`, CPU-Limit 1, Netzwerk-Namespace via `unshare -Un --map-current-user`. Installiertes C166-Modul wurde im Laufzeitprotokoll unter `Ghidra/Extensions/c166-ghidra-module-v1.2.2` geladen.
- Das dokumentierte Replay mit `Xe164Probe.java` war erfolgreich (`INSTRUCTION_COUNT=1401`, `FUNCTION_COUNT=45`). Ein fokussierter Zusatzlauf disassemblierte ausschließlich die beiden Zieladressen und gab deren Basicblock-/Referenzdetails aus. Der Zusatzlauf meldete beide als außerhalb einer erkannten Funktion. Er legte keine künstlichen Funktionen an.
- Der erste Kompilierlauf des Zusatzscripts schlug fehl, weil die Ghidra-API für Blockziele einen Iterator statt eines Arrays liefert. Das Script wurde korrigiert und der erfolgreiche Lauf ist in `target-probe-disasm-script.log` erhalten; der Fehlversuch steht in `target-probe.log` (`target-probe-script.log` war dabei leer).

## Befunde pro Ziel

| Ziel | Dateioffset | Jump-Row-Eingang | Funktion | Basicblock (inklusive) | Abschluss |
|---|---:|---|---|---|---|
| `E021AA` | `0x21AA` | E-XE164-012, Row 83 | keine erkannt | `E021AA..E021DF` | `E021DE: reti` |
| `E021E0` | `0x21E0` | E-XE164-012, Row 84 | keine erkannt | `E021E0..E02215` | `E02214: reti` |

Die Jump-Row-Zuordnung stammt aus der Aufgabeneingabe. Im fokussierten Ghidra-Lauf wurden beim Prüfen der beiden Zieladressen keine eingehenden Code-Referenzen ausgegeben; deshalb ist hier keine Quellinstruktionsadresse erfunden. Beide `disassemble()`-Aufrufe waren erfolgreich. Das Blockmodell lieferte keine `BLOCK_OUT`-Zielkante für einen der beiden `RETI`-Blöcke.

## Byte- und Instruktionsvergleich

Rohbytes an beiden Blöcken haben je 54 Bytes. Der Vergleich ist für denselben Offset im Block identisch, ausgenommen Offset `+0x14`:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Am Ziel `E021E0` ist das Byte bei `+0x14` `0x6F` statt `0x5F`; alle anderen 53 Bytes stimmen überein. Ghidra decodiert den abweichenden Befehl jeweils bei `+0x1A`: `E021C4 bset 0xfd00.0x5` gegenüber `E021FA bset 0xfd00.0x6`. Alle restlichen Instruktionen einschließlich `reti` haben gleiche Reihenfolge und gleiche relative Offsets. Beide Blöcke sind 24 Instruktionen lang und liegen genau `0x36` Bytes auseinander.

Direkte Datenreferenzen der Instruktionen sind in [references.tsv](references.tsv) aufgeführt. Die beiden Blöcke haben dasselbe Referenzmuster mit derselben Verschiebung um `0x36`; die Operandenadressen werden hier nur als Referenzziele berichtet und nicht semantisch interpretiert.

## Evidenzgrenzen und Alternativen

- Die Abwesenheit einer Ghidra-Funktion ist keine Aussage, dass die Bytes keine eigenständigen Routinen darstellen. Das fokussierte Script hat zwei Startadressen disassembliert und die Basicblocks betrachtet, aber keine Funktionseigentümerschaft hergeleitet.
- Die separaten `RETI`-Terminatoren, Row-83/84-Zielzuordnung und wiederholte Save/Restore-Folge stützen die Lesart zweier getrennter Entry-Targets. Alternative: dieselbe generierte/templatisierte Routine wurde zweimal als unabhängige Codekopie abgelegt; das ist im Binärbild ebenfalls nur als zwei disjunkte Codeblöcke sichtbar.
- Da die Jump-Row-Quellinstruktionen im bereitgestellten Material nicht enthalten sind und Ghidra für diese Targets keine eingehenden Code-Xrefs auswies, ist die genaue Herkunft der beiden Sprünge offen.
- Keine Laufzeit-, Hardware-, K-Bus-, SFR- oder Interruptsemantik wurde untersucht. Die Instruktionsnamen und Pseudocode-Eigenschaften sind Werkzeugableitungen, keine Beobachtung einer Ausführung.

## Status

- Beziehung der beiden Zieladressen als zwei direkt benachbarte, je terminale und stark wiederholte Basicblocks: **VERIFIZIERT** (statische Bytes plus Ghidra-C166-Decode/Blockmodell).
- Separate Ghidra-Funktionen: **OFFEN**; beide Funktionseigentümer fehlen im Analyseergebnis.
- Eigenständige Handler-/Entry-Routine-Interpretation: **HYPOTHESE**; strukturell plausibel, Semantik nicht belegt.
- Netzwerk- und Zielaktionen: **NOT_RUN**. Geräte/VMs wurden nicht verwendet.

## Output-Hashes

Die SHA-256-Prüfsummen aller Ausgabedateien außer der Prüfsummenliste selbst stehen in `SHA256SUMS`. Der Export enthält drei REA-Evidence-Datensätze (zwei Rizin-Bytefenster und ein Rizin-Disassemblierungsversuch). `SHA256SUMS` wird als konventionelle Manifestdatei nicht selbst referenziert.
