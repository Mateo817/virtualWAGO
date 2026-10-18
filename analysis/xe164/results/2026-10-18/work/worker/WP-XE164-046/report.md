> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-046 — E02DDA / E02DF6 Seed-CFG-Vergleich

## Ergebnis

**VERIFIZIERT (statisch, nur für die zwei vorgegebenen Seeds und diese Composite-Revision):** Die getrennt dekodierten Seed-CFGs bilden zwei rückkehrterminierte Kontrollflusskomponenten, deren beobachtete Instruktionsspannen exakt benachbart sind. E02DDA deckt `[0x2DDA, 0x2DF6)` ab (28 Bytes); E02DF6 deckt `[0x2DF6, 0x2E14)` ab (30 Bytes). Die erste endet mit `rets` an `0x2DF4`; die zweite beginnt unmittelbar danach bei `0x2DF6`. Es gibt in den beiden Seed-CFGs keine Fallthrough-Kante über diese Grenze. Der jeweilige direkte bedingte Rücksprung bleibt innerhalb seiner eigenen Spanne.

Die zwei isoliert vorgegebenen Caller-Instruktionen stimmen mit diesen Zielen überein: Offset `0x1AF8` dekodiert zu `calls 0xe02dda` (Bytes `dae0da2d`), Offset `0x1AFC` zu `calls 0xe02df6` (Bytes `dae0f62d`). Diese Beobachtung bestätigt nur die beiden konkreten Callsite-Instruktionen, nicht Caller-Bodies oder weitere Aufrufer.

## Exakte Beobachtung

| Seed | Bytebereich inklusiv | Exklusives Ende | Bytes | Instruktionen | CFG-Kern |
|---|---:|---:|---:|---:|---|
| E02DDA | `0x2DDA..0x2DF5` | `0x2DF6` | 28 | 10 | Bedingter Sprung `0x2DF2 -> 0x2DE6`, Fallthrough `0x2DF4`; `rets` bei `0x2DF4` |
| E02DF6 | `0x2DF6..0x2E13` | `0x2E14` | 30 | 11 | Bedingter Sprung `0x2E10 -> 0x2DF8`, Fallthrough `0x2E12`; `rets` bei `0x2E12` |

Alle dekodierten Instruktionen mit Bytes und alle Kanten stehen in [instructions.tsv](instructions.tsv) und [edges.tsv](edges.tsv). Die Bytes direkt am Composite stimmen für jede Tabellenzeile. Die rohen Bytefolgen lauten:

- E02DDA: `e6fc0020e6fd8103e6fe0010e6ffdb00dc4db8fc08c2a01e3df9db00`
- E02DF6: `e00cf0fc5c2fe6fd0060e6fee000c4df027cc4ef047c08c148c48df3db00`

## Quellen und Methode

- Eingabe: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`, 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Vor der Analyse verifizierter Hash: identisch mit dem vorgegebenen Hash.
- REA zuerst: `open_binary` gab `target_unavailable` / `unsupported binary format` für die rohe Composite-Datei zurück. Damit blieb eine konkrete REA-Abdeckungslücke für die gewünschte C166-Dekodierung.
- Dokumentierter Rizin-C166-Fallback: `-N -q`; je Kommando `e io.va=false; e asm.arch=c166; e asm.bits=16; e cfg.bigendian=false`. Die Finding-Records führen die Seeds getrennt und exakt begrenzt ab (`p8 28` plus `pdj 10` bei `0x2DDA`; `p8 30` plus `pdj 11` bei `0x2DF6`). Die zweite Abfrage endet im ausgegebenen Instruktionsarray mit `rets` bei `0x2E12`; sie enthält keinen Eintrag ab `0x2E14`. Es wurde kein globales `aaa`-Projekt und keine Caller-Analyse angelegt.
- Rizin lokal verfügbar: `0.9.1 @ linux-x86-64`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. Der REA-Provider selbst meldet die Version als `null`; diese Versionslücke bleibt deshalb für die Evidence-Metadaten bestehen.
- Finding-Bundle: [finding-bundle.json](finding-bundle.json), REA-kanonisch normalisiert und auf 3 exakt ausgewählte Records projiziert; Seed E02DDA `ev_1dc88673301ce219ba45dda2a38b2f3bfd3441d2d44f0d881e28d2653881a8d9`, Seed E02DF6 `ev_f325c8ea8c891d20cc5ae6352dd08240d10d4bf75f3194ce5580068594fc63a7`, Callsite-Paar `ev_5068e380bc8307b7ba52c75849ba3f545af11cca858068ac0248aedd6e0e2dbe`.
- Der überlange E02DF6-Record `ev_ab3b18c439ec1396a86626b1c908e36187051ced4ac55022370e36ddfaf5b6ea` ist ausdrücklich **REJECTED AUDIT** und nur separat in [rejected-overscope-audit.json](rejected-overscope-audit.json) aufbewahrt. Seine 15-Instruktions-Abfrage umfasste zusätzliche Dekodierungen ab `0x2E14`; sie wird für keine Tabelle oder Schlussfolgerung herangezogen und ist nicht im Finding-Bundle.
- Callsite-Fundstellen samt Bytefolgen: [callsites.tsv](callsites.tsv). Vergleich: [comparison.tsv](comparison.tsv).

## Status und Grenzen

- **VERIFIZIERT:** Bytes, C166-Dekodierungen, direkte Sprungziele/Fallthroughs, terminale Rückkehrinstruktionen, exakte Instruktionsspannen und die zwei vorgegebenen Callsite-Ziele für den gebundenen Composite-Hash.
- **HYPOTHESE:** Die zuvor vermuteten Größen von 28 und 30 Bytes gelten hier nur als zu prüfende Größenkandidaten; die Tabellen stützen sie durch gezählte dekodierte Instruktionslängen und die jeweilige `rets`-Grenze unabhängig von Ghidra-Funktionsobjekten.
- **OFFEN:** Ob weitere, nicht untersuchte Einstiege außerhalb der zwei Seeds in die Bereiche springen; Funktionsbesitz/Compilergrenzen jenseits dieser Seed-CFGs; die semantische Bedeutung von Operanden und Instruktionen.
- **BLOCKED:** Nichts innerhalb der begrenzten Seed-CFG-Frage. Eine unabhängige Ghidra-Prüfung blieb wegen REAs abgelehnter roher Composite-Datei unausgeführt und war für die beobachteten Rizin-Kanten nicht erforderlich.
- **PASS:** `validate.py` prüft Eingabegröße/Hash, Tabellenbytes, Instruktionslängen, Spannen, Adjazenz, terminale Rückkehr, bedingte CFG-Ziele und die isolierten Caller-Bytes. Der Validator läuft ohne Geräte- oder Netzverbindung.

## Alternative und Restunsicherheit

Die Größenangaben allein würden keine getrennten Kontrollflusskomponenten beweisen: benachbarte Ghidra-Funktionskandidaten könnten auch aus einer willkürlichen Aufteilung oder einer über die Grenze laufenden Instruktionsfolge stammen. Hier sprechen die unabhängig an den Seeds dekodierten `rets`-Instruktionen und die getrennten inneren Rücksprungkanten gegen eine solche Fallthrough-Lesart. Nicht ausgeschlossen ist ein weiterer, nicht untersuchter externer Einstieg oder eine andere Interpretation bei abweichender C166-Konfiguration; daher bezieht sich VERIFIZIERT ausschließlich auf die hier dokumentierten statischen Seed-CFGs und Eingabebytes.

## Validierung und Hashes

`python3 validate.py` prüft auch die Bundle-Grenze: nur die drei Finding-IDs sind zugelassen; der zweite Body enthält 30 Bytes und exakt 11 Instruktionen bis `rets` bei `0x2E12`; kein Instruktionsoffset oder -ende erreicht `0x2E14`. Der Overscope-Record muss isoliert im REJECTED-AUDIT-Bundle liegen. `sha256sum -c SHA256SUMS` bindet alle WP-Ausgabedateien außer sich selbst.
