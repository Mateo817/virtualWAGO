> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-185 — sichtbare Registerdefinitionen am Call `0x3de0`

## Ergebnis

**Befundstatus: VERIFIZIERT für die statisch sichtbaren Definitionen und Gates im festen Ausschnitt.** Beim direkten A32-Call `0x3de0: ebfffa65` (`bl 0x277c`) wird `r5` als `r1`, `r7` als `r0` übergeben; `r2` erhält unmittelbar zuvor den Wert 1. `r8` ist kein Callargument, wird aber für das Dispatch-Gate verwendet.

| Register | Im Bereich sichtbare reaching definition am Call | Belegbare Grenze |
|---|---|---|
| `r5` | Am ersten sichtbaren Eintritt kann ein unbekannter eingehender Wert weiterlaufen. Auf Loop-Runden ist die letzte sichtbare Definition `0x3dcc: add r5,r5,#24`; die Kopie in `r1` erfolgt bei `0x3dd8`. | Der Anfangswert, die Adresse/Identität des referenzierten Speicherbereichs und die Anzahl der vorherigen Schleifenrunden sind OFFEN. `r5` ist der Basisregisterwert für die sichtbaren Loads `[r5+0x14]`, `[r5+4]` und `[r5]`. |
| `r7` | Keine Definition im gesamten Fenster. `0x3ddc: mov r0,r7` kopiert den aktuellen, eingehenden Wert in das erste Callargument. | Die definierende Instruktion und Herkunft von `r7` liegen außerhalb des Ausschnitts oder sind anderweitig unbekannt. |
| `r8` | `0x3d74: movw r8,#0x8008`. Für den sichtbaren sequenziellen Pfad ab `0x3d70` ist dies die Definition, die `0x3dc0` liest. | Das gate-vergleichene Halbwort kommt von `0x3dbc: ldrh r3,[r5]`; der Callpfad von `0x3dc4` verlangt Gleichheit mit `0x8008`. Ein alternativer Eintritt von außerhalb mitten in den Ausschnitt ist mit diesem begrenzten Scan nicht ausgeschlossen. |

Die sichtbaren Pfadgates sind: `0x3da4` vergleicht das Wort `[r5+0x14]` mit `r6`; `0x3db4` testet Bit 0 des Worts `[r5+4]`; `0x3dbc` lädt das Halbwort `[r5]`; `0x3dc0` vergleicht es mit `r8`; nur der Gleichheitszweig `0x3dc4` erreicht die Callvorbereitung bei `0x3dd4..0x3ddc`. Der `r5`-Loop-Schritt ist `0x3dcc`, gefolgt von `0x3dd0` zurück nach `0x3d84`. Diese Beobachtungen belegen keine Ausführung.

## Beobachtungen und Fundstellen

- `[0x3c80,0x3dec)` umfasst 364 Bytes; Dekodierung vollständig innerhalb dieser Range.
- `0x3d74` definiert `r8` via `movw` auf `0x8008`.
- `0x3dbc` liest `r3` als 16-Bit-Halbwort aus `[r5]`; `0x3dc0` vergleicht `r3` und `r8`; `0x3dc4` verzweigt bei Gleichheit zur Setup-Sequenz.
- `0x3dcc` verändert `r5` um `0x18`; `0x3dd8` kopiert `r5` nach `r1`, und `0x3ddc` kopiert `r7` nach `r0`.
- `0x3de0` ist `bl 0x277c`; `0x3de4` vergleicht das zurückgelieferte `r0` mit null und `0x3de8` verzweigt bei Gleichheit zurück zu `0x3dcc`.
- Alle Aussagen stammen nur aus den Instruktionen im festgelegten Bereich. Registerherkunft vor `0x3c80` sowie Daten-/Funktionssemantik bleiben unbekannt.

## Methode, Werkzeuge und Grenzen

REA-first: akzeptierte WP096-Evidence gelesen; sie deckt den Zielkörper, nicht den Callerbereich ab. Lücke einmal dokumentiert in [assignment.md](assignment.md). Der bekannte Ghidra-Import-Hänger wurde nicht wiederholt.

Danach wurde ausschließlich der 364-Byte-Ausschnitt bei Fileoffset `0x3c80` extrahiert. GNU ARM Objdump 2.44 (`arm-linux-gnueabihf-objdump`, Binutils 2.44) dekodierte ihn als `-b binary -m arm`, mit VMA-Basis `0x3c80`. Python 3.13.5 wurde für den begrenzten Fenster-Fingerabdruck/Validator verwendet. Window SHA-256: `2ab3bd5107aa6f16f364cb8994b632ae0c3e27ea90c8871ba68b6b54f6d69082`.

Die vollständige Eingabe-SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` wurde im Validator sequenziell über alle 38.584 Eingabebytes neu berechnet und stimmt mit dem erwarteten Hash überein. Dieser Pass diente ausschließlich der Eingabeidentität. Interpretierte/dekodierte Bytes und der Fallback-Disassembly blieben strikt auf `[0x3c80,0x3dec)` begrenzt. Adressebenen: Zahlen in der Instruktionstabelle sind ELF-VA; im untersuchten Fenster stimmen die Dateioffsets numerisch mit den ELF-VA überein.

## Status, Tests und Unsicherheit

- Befundstatus: **VERIFIZIERT** für sichtbare Instruktionen, Definitionen, Registerkopien und lokale Gates.
- Teststatus Validator: **PASS**; überprüft erwarteten Eingabepfad, Größe und den vollständig neu berechneten ELF-SHA-256, Fenstergrenzen, 364-Byte-Fensterhash sowie Claim-Zeilen/Opcode-Wörter.
- Binary-Ausführung, Runtime, Geräte-/Netz-/VM-/Hardware-Zugriffe: **NOT_RUN**.
- Alternativerklärung: Der aufrufende Pfad könnte außerhalb des Fensters in die sichtbare Sequenz eintreten, wodurch die lokal beobachtete `r8`-Definition umgangen würde. Zudem ist eine sichtbare Registerdefinition allein kein Beweis für dynamische Erreichbarkeit.
- Restunsicherheit: Ursprung von `r5` und `r7`, externe CFG-Eingänge, tatsächliche dynamische Callausführung und sämtliche semantische Bedeutung der Werte bleiben **OFFEN**.

## Erzeugte Dateien

`assignment.md`, `report.md`, `flow.tsv`, `validate.py`, `SHA256SUMS`. Die individuellen Dateihashes sind im SHA256SUMS-Manifest beziehungsweise beim Abschluss für das Manifest selbst angegeben.
