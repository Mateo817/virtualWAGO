> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-032 — begrenzter Kontrollfluss ab E005EC

## Ergebnis

**VERIFIZIERT** — Für den gebundenen Composite ist der isolierte Caller bei Datei-/Analyseoffset `0x069E` ein vier Byte langer direkter `calla+ cc_UC` mit Ziel `0x05EC`. Im ab dort angesetzten, ausdrücklich begrenzten C166-Dekodierstrom liegen 31 Instruktionen, die ohne Lücke oder Überlappung `0x05EC..0x0633` abdecken. Der Strom ist ein Basic Block ohne internen Call oder Sprung und endet mit `ret` bei `0x0632`; der Block endet exklusiv bei `0x0634`.

Das belegt eine begrenzte statische Kontrollflussstruktur, keine Laufzeitausführung und keine vollständige Funktionserkennung über den angefragten Ausschnitt hinaus.

## Eingabe, Methode und harte Grenzen

- Eingabe: `XE164-composite-e00000.bin`, 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Offset-/Adressbindung: die Rizin-Rohdateioffsets sind hier die Analyseadressen; `E00000` dient nur als vorgegebene syntaktische Basis. Es wird keine weitere Adresssemantik behauptet.
- Callee-Fenster: `0x05EC..0x0633` einschließlich, 72 Bytes; Ende exklusiv `0x0634`.
- Caller-Fenster: ausschließlich Instruktion bei `0x069E`.
- Ausschlüsse: keine Instruktionen vor `0x05EC` oder ab `0x0634`; keine anderen Caller, Zielbereiche, DPP/SFR/ABI/K-Bus-Semantik, Runtime oder Hardware.

REA `open_binary` wurde zuerst aufgerufen, meldete `target_unavailable` mit `unsupported binary format` und `file_format_rejected`; es gab dafür keine Evidence-ID. Das begründet den in der Zuweisung erlaubten direkten C166-Fallback. Über REA `execute_rizin_command` wurde mit `e asm.arch=c166; e asm.bits=16` dekodiert. Pro Instruktionsstart wurde ausschließlich `aoj @ address` verwendet; der separate Rohbyte-Read war exakt 72 Bytes ab `0x05EC` und enthielt zusätzlich nur den isolierten `aoj @ 0x69e`. Der kanonische REA-Export umfasst genau diese 31 Instruktionsrecords und eine Rohbyte-/Caller-Beobachtung (32 Records insgesamt). Overscope-Instruktionen sind nicht enthalten.

REA Provider: Rizin; Versionsnummer **OFFEN** (keine verlässliche Versionsbeobachtung in den Evidence Records). Die verwendeten Rizin-Kommandos und ihre vollständigen Ausgaben sind in `rea-evidence-bundle.json` enthalten.

## Tabellen

Die exakten Instruktionszeilen stehen in [instructions.csv](instructions.csv); CFG-, Call- und Referenztabellen stehen in [cfg.csv](cfg.csv), [calls.csv](calls.csv) und [references.csv](references.csv).

| Block | Start | Ende exklusiv | Instruktionen | Terminator | Nachfolger |
| --- | --- | --- | ---: | --- | --- |
| B0 | `0x05EC` | `0x0634` | 31 | `ret` bei `0x0632` | Exit |

| Caller | Ziel | Dekodierung |
| --- | --- | --- |
| `0x069E` | `0x05EC` | direkter `calla+ cc_UC` |

Es gibt in diesem Callee-Fenster keine beobachtete Sprung-/Call-Referenz. Zwei `exts`-Mnemonics tragen im Rizin-Feld den Flowtyp `unk`; das wird nicht über das Feld hinaus interpretiert und ändert die beobachtete Adressfolge nicht.

## Status, Alternativerklärung und Restunsicherheit

- **VERIFIZIERT** — Eingabegröße/-hash, 72 Bytes, fortlaufende Adressen/Bytes, Endegrenze, 31 Instruktionsrecords, einzelner Basic Block und Caller-Call stimmen im Validator überein.
- **HYPOTHESE** — `0x05EC` ist der Einstieg des durch diesen Caller angesprochenen Codeabschnitts; das folgt aus dem direkten Call-Operand, nicht aus einer vollständigen Funktionserkennung.
- **OFFEN** — Ob der lineare C166-Dekodierstrom an diesen Offsets dem tatsächlich ausgeführten Code entspricht; es gab keine Laufzeitbeobachtung.
- **OFFEN** — Ob es alternative Einstiege oder indirekte Kontrolltransfers in den Ausschnitt gibt; solche Beziehungen und weitere Caller waren ausgeschlossen.
- **OFFEN** — Semantik der Datenoperationen, ABI/Calling Convention, interne Adressräume sowie Verhalten außerhalb des Fensters.

## Prüfung

`python3 validate.py` — **PASS**: Eingabeidentität, bytegenaue Grenzen, Adresse/Offset-Bindung, jede Instruktionszeile gegen den kanonischen REA-Export, einzelner CFG-Block, Callerziel, Referenzzeile und Export-Scope stimmen. Kein unabhängiger Reviewer/Worker eingesetzt.
