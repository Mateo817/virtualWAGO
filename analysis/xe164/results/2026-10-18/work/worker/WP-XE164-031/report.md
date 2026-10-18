> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-031 — begrenzter Kontrollfluss ab E005A2

## Ergebnis

**VERIFIZIERT** — Im abgegrenzten Fenster `0x05A2..0x05EB` liegt eine lineare Folge von 34 C166-dekodierten Instruktionen in genau einem Basic Block. Es gibt darin keinen bedingten oder unbedingten Sprung und keinen weiteren Call. Die letzte Instruktion ist `ret` bei `0x05EA`; damit endet der beobachtete Block bei `0x05EC`. Der separat angeforderte Caller bei `0x067A` enthält einen direkten `calla+ cc_UC` mit Ziel `0x05A2`.

Die Aussage beschreibt nur die statisch dekodierte Struktur dieses Fensters, keine Funktion über dessen Grenzen hinaus und keine Laufzeitausführung.

## Quelle, Grenzen und Methode

- Eingabe: `XE164-composite-e00000.bin`, 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Adressbindung: Der verwendete Rizin-Rohdatei-Offset ist zugleich Analyseadresse. `E00000` wird hier nur als vorgegebene syntaktische Basis benutzt; keine weitere Adresssemantik wird behauptet.
- Callee-Fenster: inklusive `0x05A2..0x05EB`, exakt 74 Bytes; Ende exklusiv `0x05EC`.
- Caller-Fenster: ausschließlich Instruktion an `0x067A`, dekodiert als 4-Byte-Call zu `0x05A2`.
- Harte Grenzen: keine verwendete Instruktion vor `0x05A2` oder ab `0x05EC`; keine anderen Caller, Zielbereiche, Architektursemantik, ABI oder Hardwareaussagen.

REA `open_binary` wurde zuerst aufgerufen und wies den Rohdump mit `target_unavailable` / `unsupported binary format` zurück (die Abweisung selbst lieferte keine Evidence-ID). Das ist die dokumentierte Decoderlücke. Der vorgesehene direkte Rizin-C166-Fallback wurde danach verwendet: `rizin 0.9.1`, Plugininventar meldet den C166-Decoder; die Kommandos setzten `asm.arch=c166`, `asm.bits=16` und dekodierten die gewählten Adressen. Rizin wurde über REA `execute_rizin_command` ausgeführt. REA Evidence IDs: `ev_1c1d718d64fe6b0adaa354613f22dea70660c145c626e8efac3478638e776998` (erste Disassemblierung; siehe Abweichung unten), `ev_f7917cc479e8ac6daa3fe109c4e7e85b6d2cffbd80b33e3065b2dab7c451eab2` (Rohbytes, Instruktions-JSON und einzelner Caller).

Der erste Fallback-Aufruf gab für den Caller versehentlich 8 statt 4 Bytes an und dekodierte daher auch nachfolgende Instruktionen. Diese zusätzlichen Bytes wurden nicht für Bericht, Tabellen oder Folgerungen verwendet. Der zweite Fallback-Aufruf isolierte den Caller korrekt mit `aoj @ 0x67a`; nur sein direkter Call-Datensatz wird in der Tabelle geführt. Die kanonische Evidence-Datei enthält beide Toolbeobachtungen, damit die Abweichung nachvollziehbar bleibt.

## Tabellen

Die vollständige Instruktionstabelle einschließlich Adresse, Länge, Bytes, Mnemonic und Rizin-Typ steht in [instructions.csv](instructions.csv). Die Basic-Block-Tabelle steht in [cfg.csv](cfg.csv); Call und statische Kontrollflussreferenz stehen in [calls.csv](calls.csv) und [references.csv](references.csv).

| Block | Start | Ende exklusiv | Instruktionen | Terminator | Successors |
| --- | --- | --- | ---: | --- | --- |
| B0 | `0x05A2` | `0x05EC` | 34 | `ret` bei `0x05EA` | Exit |

| Call site | Ziel | Dekodierung |
| --- | --- | --- |
| `0x067A` | `0x05A2` | `calla+ cc_UC`, direkt |

Es wurden keine Sprung-/Call-Referenzen im Callee-Fenster beobachtet. Speicheroperanden in den Instruktionen sind keine Kontrollflussreferenzen.

## Status, Alternative und Unsicherheit

- **VERIFIZIERT** — Dateigröße und SHA-256 stimmen; die dekodierten Instruktionsbytes bilden ohne Lücke oder Überlappung exakt die 74 Bytes `0x05A2..0x05EB` ab.
- **VERIFIZIERT** — Der Maschinenvalidator bestätigt 34 Instruktionen, einen linearen Block, `ret` bei `0x05EA` und das direkte Callziel `0x05A2` vom isolierten Caller `0x067A`.
- **HYPOTHESE** — Der Caller ist ein Aufrufer des betrachteten Callee-Ausschnitts; diese Deutung stützt sich auf den direkten Call-Operand. Eine vollständige Caller-/Funktionsinventur war ausdrücklich ausgeschlossen.
- **OFFEN** — Ob die vorgegebene C166-Dekodierung die ursprünglich gemeinte Instruktionsgrenze repräsentiert, falls das Abbild an diesen Adressen nicht als C166-Code verwendet wird. Es gibt keine Laufzeitbeobachtung.
- **OFFEN** — Bedeutung der Datenoperationen, Register, Zeiger, ABI sowie Kontrollfluss außerhalb der festgelegten Fenster.

## Prüfung

`python3 validate.py` meldet `PASS`, wenn Eingabeidentität, Grenzen, Instruktionstabelle, CFG, Callerziel und Referenztabelle mit dem kanonischen REA-Evidence-Export übereinstimmen. Ein unabhängiger Reviewer oder Worker wurde nicht eingesetzt.

## Ausgabedateien

`SHA256SUMS` enthält SHA-256 für alle erzeugten Ergebnisdateien außer sich selbst. Der Validator ist keine Firmware-/Geräteprüfung; es wurden keine Geräte, Netzwerkverbindungen oder VMs verwendet.
