> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-040 — Kontrollfluss von E00EE8 bis vor E00F18

## Ergebnis

**VERIFIZIERT (statische Syntax):** Der begrenzte Ausschnitt `0x0EE8..0x0F17` dekodiert als ein linearer Fall-through-Block mit 17 Instruktionen. Er enthält einen direkten `CALLS` an `E00F00` mit Ziel `E00DAA`; bei Rückkehr läuft die Folge bei `E00F04` weiter. `RETS` bei `E00F16` ist der einzige im Ausschnitt dekodierte Kontrolltransfer, der den Block beendet. Ein bedingter oder unbedingter Sprung ist im Ausschnitt nicht dekodiert. Der isolierte Caller-Befund `E0364A: calls E00EE8` bestätigt den direkten Eintritt in den Bereich.

Das ist ein Befund zur Dekodierung und zum sichtbaren Kontrollfluss, keine Aussage über die Wirkung der Operanden oder über tatsächliche Laufzeit. Die Rückkehr vom Aufruf bei `E00F00` ist eine Bedingung für den sichtbaren linearen Fortgang, nicht durch diesen Ausschnitt bewiesen.

## Beobachtungsgrundlage

- Eingabe: `XE164-composite-e00000.bin`, 17,110 Bytes; SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` (Größe und Hash vor Analyse geprüft).
- REA `open_binary` lehnte den headerlosen Composite als `unsupported binary format` ab. Daraufhin wurde der dokumentierte Rizin-C166-Fallback über REA `execute_rizin_command` verwendet.
- Rizin `0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`; Einstellungen: `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`, `scr.color=0`, `asm.lines=false`. Es wurde kein globaler Analysepass angefordert.
- REA-Evidence: `ev_63b5a3bddd6d5ad5c225af6e2a735773cca480447a9dca79bae47f7661d3ab21`, Authority `shipped-artifact`, Confidence `observed`, Exit Code `0`, kein gekürzter Output, Artefakt danach unverändert.
- Die Rizin-Ausgabe stellt die Adressen als Offsets dar. Für diese Arbeitspaket-Zuordnung entspricht Offset `0x0EE8` der Analyseadresse `E00EE8`; relative Offsets und Bytes bleiben in [instructions.csv](./instructions.csv) ausdrücklich ausgewiesen.

## Exakte Bytes und Fundstellen

Die exakte 48-Byte-Folge des abgegrenzten Bereichs lautet:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Jede dekodierte Instruktion mit Startoffset, Analyseadresse und Bytes steht in [instructions.csv](./instructions.csv). Der Startoffset des letzten Instruktionswortes `db 00` ist `0x0F16`; sein Ende liegt exakt am exklusiven Bereichsende `0x0F18`. Der isolierte Caller-Befund ist auf die 4 Bytes `da e0 e8 0e` bei Offset `0x364A` begrenzt und dekodiert als `calls 0xE00EE8`.

Kontrollfluss aus dieser Dekodierung:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

## Alternative und Restunsicherheit

Eine alternative Erklärung für den scheinbar linearen Block ist, dass der Composite einen Ausschnitt oder eine anders segmentierte Abbildung repräsentiert und ein anderer Einsprung von außerhalb in einen inneren Offset führt. Diese Abgrenzung untersucht keine eingehenden Referenzen außer dem ausdrücklich zugewiesenen Caller. Ebenfalls offen bleibt, ob der direkte Aufruf bei `E00F00` zurückkehrt; deshalb ist der Folgepfad ab `E00F04` nur als Fortsetzung nach Rückkehr dargestellt. Es wurde weder ausgeführt noch die Funktion am Ziel `E00DAA` analysiert.

Status der engeren Aussagen:

- **VERIFIZIERT:** Die angegebenen Bytes und Rizin-Dekodierungen im exakt begrenzten 48-Byte-Bereich sowie der einzelne Caller-Aufruf bei `0x364A` sind in der REA-Beobachtung enthalten.
- **HYPOTHESE:** Keine semantische Hypothese erforderlich. Der lineare Grundblock ist eine syntaktische Interpretation dieser Dekodierung.
- **OFFEN:** Externe Einsprünge in den Bereich, tatsächliche Rückkehr am Call-Ziel und jede Laufzeitbedeutung.
- **BLOCKED:** Keine für die gestellte statische Kontrollflussfrage.

## Dateien

- `report.md` — Befund und Grenzen.
- `instructions.csv` — vollständige instruktionsgenaue Fundstellentabelle.
- `rea-finding.json` — kanonisch exportiertes, einzelnes REA-Evidence-Record für diese Beobachtung.
- `validate.py` — lokaler Integritäts- und Scope-Validator.
- `SHA256SUMS` — Prüfsummen der Ausgabedateien (außer dieser Prüfsummendatei).
