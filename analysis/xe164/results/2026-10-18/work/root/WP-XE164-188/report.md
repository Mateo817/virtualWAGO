> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-188 — numerischer Storewert bei `0x2f94`

## Ergebnis

**VERIFIZIERT:** Auf der lokal linearen, verzweigungsfreien Sequenz `0x2f7c..0x2f94` erreicht `r2` den Store mit dem numerischen Wert `0x1a270`.

Das DATA-Wort bei Datei-Offset `0x3360` hat little-endian Bytes `38 34 01 00`, also `0x00013438`. `0x2f7c: ldr r3,[pc,#0x3dc]` referenziert mit A32-PC `0x2f84` genau `0x3360`. Danach:

1. `0x2f84: add r3,pc,r3`, mit A32-PC `0x2f8c`: `r3=0x2f8c+0x13438=0x163c4`.
2. `0x2f88: add r2,r3,#0x3e80`: `r2=0x1a244`.
3. `0x2f8c` verändert nur `r3` und nicht `r2`.
4. `0x2f90: add r2,r2,#0x2c`: `r2=0x1a270`.
5. `0x2f94: str r2,[r4,#0x61c]` schreibt diesen Wert an die weiterhin relative Zielbildung.

**OFFEN:** Der konkrete Wert und die Herkunft von `r4`, die absolute Storeadresse, Objektidentität, Bedeutung oder Mapping von `0x1a270`, eine Verbindung zum separaten IoDrvKbus-ELF, dynamische Pfaderreichbarkeit, Runtime und Hardware. Der Befund behauptet nur den numerischen Storequellwert auf der sichtbaren Sequenz.

## Methode und Grenzen

Eingabe: 25.976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. Codebereich `[0x2c00,0x2fb8)` ist 952 Bytes mit SHA-256 `9fd4438ad19995ddfea8a89e3335bbd4265d652c23e1346f2e896c34f9d10a80`; DATA-Bereich `[0x3360,0x3364)` ist vier Bytes mit SHA-256 `e88c98749d7991a20a4c4ee258b8f07acba58b71fb2a29e64e6597b0d6040077`.

REA-first: E-XE164-213/WP186 bindet denselben Hash und den Store, deckt jedoch die vollständige Literal-/PC-Arithmetik nicht ab. Der bekannte Ghidra-Import-Hänger wurde nicht wiederholt. Root verwendete GNU ARM Objdump 2.44 nur mit `--start-address=0x2c00 --stop-address=0x2fb8`, GNU `od` nur für vier Bytes ab `0x3360`, sowie Python 3.13.5 zur Wiederholungsprüfung. Keine Beobachtung aus dem scope-fehlerhaften WP187 dient als Evidenzbasis.

Alternative Erklärung: `0x1a270` ist ein numerisch berechneter adressähnlicher Wert, kann aber ohne weitere gebundene Daten- und Laufzeitabbildung nicht als bestimmtes Objekt oder Interface benannt werden.

Prüfungen: Eingabeidentität **PASS**; Bereichshashes/Opcodewörter/Arithmetik **PASS**; Scope-Compliance **PASS**; Runtime/VM/Netz/Gerät/Hardware **NOT_RUN**. Review: Root Self-Review; kein unabhängiger Review behauptet.
