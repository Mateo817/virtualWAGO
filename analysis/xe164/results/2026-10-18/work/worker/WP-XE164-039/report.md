> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-039 — Kontrollflussfenster E03528 bis E03585

## Ergebnis

**VERIFIZIERT (statisch, begrenzter Umfang):** Der isolierte Call bei Datei-Offset `0x3692` dekodiert als `calls 0xe03528` (4 Bytes `dae02835`; Evidence `ev_8845fae468d01e0a94d15ba6fd5a027b6e1fa7b4c5a7dddfd72ade04a880c422`). Mit der nur syntaktischen Basisabbildung `E00000 + Datei-Offset` lautet die Zieladresse `E03528`.

Vom Seed `0x3528` läuft der dekodierte Strom linear bis zum bedingten Sprung bei `0x354a`. Der Sprung hat Ziel `0x355a` und Fallthrough `0x354e`. Der Fallthrough-Pfad liest bei `0x354e/0x3552` und prüft bei `0x3556` erneut: dessen Ziel ist `0x354e`, sein Fallthrough ist `0x355a`. Beide beobachteten Wege erreichen `RETS` bei `0x355a`. Es gibt in diesem Seed-CFG keine Kante von dort zu `0x355c`.

Die im zugewiesenen Fenster danach einzeln dekodierten Bytes `0x355c..0x3585` enthalten bei linearer Saat `0x355c` eine eigene bedingte Struktur und zwei terminale `RETS`-Anweisungen (`0x357e`, `0x3584`). **OFFEN:** Für diesen späteren Bereich wurde weder ein Eintritt noch eine Kante aus dem Seed-CFG belegt. Daher ist er ein separater Einstiegskandidat, keine verifizierte Fortsetzung oder Funktionsgrenze. `0x3586` und der dort bekannte Body wurden nicht gelesen.

## Bindung und Methode

- Eingabe: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`; 17,110 Bytes; SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- REA `open_binary` zuerst versucht; es lehnte das rohe Composite als `unsupported binary format` ab. Danach dokumentierter REA-`execute_rizin_command`-Fallback: `-N -q`, Einstellungen `io.va=false`, `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`; begrenzter Hexdump `px 94 @ 0x3528`, danach `pdj 1` pro einzelnem Offset. Keine globale Analyse.
- Provider: Rizin (`version: null`). Die Bytes wurden gegen das Composite geprüft. Die Abbildung von Datei-Offset auf `E`-Adresse mit Basis `0xE00000` ist ausschließlich syntaktisch.
- Tabellen: `instructions.tsv` enthält 31 einzeln beobachtete Instruktionen im zugewiesenen Fenster; `edges.tsv` trennt den Seed-CFG vom nach-RETS-Bereich; `calls.tsv` enthält ausschließlich den isoliert vorgegebenen Caller.

## Status und Grenzen

- **VERIFIZIERT:** Dateigröße, SHA-256, Bytefenster, 31 Rizin-Dekodierungen ohne Überschreitung von `0x3586`, Seed-CFG-Kanten und isolierter Caller gemäß den Tabellen/Evidence.
- **OFFEN:** Ob der Bereich ab `0x355c` ein eigener Body, alternate entry, Daten oder anders zugeordnet ist; die isolierte Aufgabe liefert dazu keinen Caller-/Ownership-Nachweis.
- **OFFEN:** Unabhängige Bestätigung der Rizin-C166-Instruktionslängen und Kontrollflusskanten. Die Version von Rizin ist nicht zuverlässig festgestellt (`null`).
- Keine Aussagen über Semantik, Runtime, Hardware, Register-/Speicherbedeutung, ABI oder Calling Convention. Keine Zielausführung, Geräte- oder Netzwerkzugriffe.
- **Alternative:** Der dokumentierte Replay verwendet Ghidra 12.1.4 mit `C166:LE:16:default` und Compiler-Spec `tasking`; diese unabhängige Dekodierung wurde für dieses Fenster in diesem Auftrag nicht durchgeführt. Sie wäre eine Verifikationsmöglichkeit, kein hier beobachteter Befund.

## Prüfung

- Validator: **PASS** — `python3 validate.py`.
- Analysis test: **NOT_RUN** — statische Einzeldekodierung und Tabellenvalidierung, kein Emulator oder Zielgerät.
- Review: Self-review; kein unabhängiger Review-Worker.
