> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-125 — `FUN_002FC530` / `ComponentEntry`-Zeiger

## Ergebnis

**VERIFIZIERT (statischer Artefaktbefund):** Der Helfer lädt das Wort des übergebenen Caller-Blocks bei `+0x10` in `r2` und ruft den geladenen Wert bei `0x2fc5c8` tatsächlich indirekt mit `blx r2` auf. Beim Aufruf enthält `r0` die Adresse eines vom Helfer angelegten lokalen Stackobjekts ab `fp-0x5c`; der übergebene Caller-Block selbst ist zu diesem Zeitpunkt in `r4` erhalten und nicht das erste Argument. Im Loader-Kontext aus WP-XE164-123 ist der Wert an Caller-Block `+0x10` der zuvor aufgelöste `ComponentEntry`-Zeiger. Damit ist der sichtbare indirekte Aufruf des so bezeichneten Exportzeigers belegt, statisch, nicht als Laufzeitbeobachtung.

Der Helfer verändert den Zeiger an `+0x10` nicht. Auf dem Erfolgsweg schreibt er Werte des lokalen Stackobjekts in Caller-Blockpositionen `+0x00`, `+0x0c`, `+0x14..+0x1c` und `+0x20..+0x28`. Auf jedem Nicht-Null-Rückgabefehler des `+0x10`-abgeleiteten Calls schreibt er den Halbwortwert `3` nach `+0x2c`; dieser Store ist unbedingt. Erst danach unterscheiden `moveq` und `bne` anhand des zweiten Helperparameters zwischen direkter Rückkehr und Fehlerprotokollierung. Die Position `+0x2e` wird auf dem Erfolgsweg gelesen. Keine dieser beobachteten Operationen überschreibt `+0x10`.

## Adress- und Eingabebindung

- Ziel: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`, 5,181,396 Bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.
- Mitgelieferter Vorgängerbericht: WP-XE164-123 `report.md`, SHA-256 `b96bf455d44125ed91835119399cd90fd04410888e74ee48afaf3525a4b513ee`.
- Mitgeliefertes Vorgängerbundle: WP-XE164-123 `rea-evidence-bundle.json`, SHA-256 `e4835580ec10347a93f7271d0638cb9bf302f0d4d8eb20d32dba99d49bea5a32`.
- Codeadressen sind ARM-ELF virtuelle Adressen (objdump VMA; REA/Ghidra default space). `readelf -SW` zeigt `.text` bei VMA `0x0007cb10`, Dateioffset `0x0006cb10`; für diese `.text`-Stellen entspricht der Dateioffset VMA minus `0x10000`. Damit liegt `0x2fc530` bei Dateioffset `0x2ec530`; der hier beigelegte Caller-Kontext `0x2ffd00..0x2ffd80` liegt bei Dateioffsets `0x2efd00..0x2efd80`.
- REA-Erstversuch: Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. `analyze_function(0x2fc530)` endete nach 300 s mit Timeout; die parallel gestarteten `procedure_assembly` und `procedure_pseudo_code` endeten ebenfalls mit Timeout. Der REA-Diagnoseeintrag nennt `Ghidra startup deadline elapsed` (REA run `d1de8b2a-f129-4ac2-aaab-fcc85d5802ef`). Daher wurde genau ein adressierter statischer Fallback benutzt: `arm-linux-gnueabihf-objdump` 2.44 für den Procedure-Ausschnitt und den erlaubten Caller-Handoff-Kontext, sowie `readelf` 2.44 für ELF-/`.text`-Adressbindung. Generische Host-`objdump` 2.44 kann die ARM-Architektur nicht disassemblieren; der ARM-Cross-`objdump` ist der verwendete Fallback.

## Beobachtungen

Die vollständige beobachtete Instruktionsfolge des hier begrenzten Bodies steht in [function-disassembly.txt](function-disassembly.txt). Der Body beginnt bei `0x2fc530`: Prolog, Setup; am `0x2fc554` lädt `ldr r2,[r0,#16]` das Wort an Blockbasis `r0 + 0x10`. `r4` bewahrt die Blockbasis (`0x2fc54c`). Bei `0x2fc55c` wird `r0` auf `fp-0x5c` gesetzt; danach initialisiert der Helfer weitere Stackplätze und Konstanten. `0x2fc5c8: blx r2` ist ein indirekter Call. Zu diesem Zeitpunkt ist also als erstes Registerargument `r0 = fp-0x5c` sichtbar. `r1` bewahrt den zweiten Helferparameter in `r5`; daraus folgt nicht, dass ein vollständiger Funktionsprototyp oder Objektlayout bekannt wäre.

Auf dem Zweig, in dem der indirekte Call `r0 == 0` zurückgibt, lädt der Helfer lokale Werte und kopiert sie in den ursprünglichen Block (dessen Basis `r4` ist):

| Caller-Blockposition | beobachtete Quelle / Wirkung |
| --- | --- |
| `+0x00` | `[fp-0x5c]` |
| `+0x0c` | `r0` nach optionalem separatem `blx r0` bei `0x2fc650` (der Zeiger dafür kommt aus `[fp-0x50]`) |
| `+0x14`, `+0x18` | zwei 32-bit Wörter ab `[fp-0x58]`, via `vld1.32`/`vst1.32` |
| `+0x1c` | Zeiger aus `[fp-0x50]`, vor dem optionalen Call gespeichert |
| `+0x20` | `[fp-0x44]` |
| `+0x24`, `+0x28` | zwei 32-bit Wörter aus `[fp-0x4c]`, via `ldrd`/`strd` |
| `+0x2c` | bei jedem Nicht-Null-Rückgabefehler des indirekten Calls: unbedingt gespeichertes Halbwort `3` |
| `+0x2e` | Halbwort wird auf dem Erfolgsweg geprüft |

Das optionale `blx r0` bei `0x2fc650` ist ein weiterer Call mit Ziel aus dem Stacklokalwert `[fp-0x50]`; es ist nicht der aus `+0x10` abgeleitete `blx r2`. Der Erfolgsweg gibt zuletzt `0` zurück. Gibt der `+0x10`-abgeleitete Call einen Nicht-Nullwert zurück, schreibt der Helfer zuerst unbedingt `3` nach `+0x2c`. Ist der zweite Helperparameter null (`r5 == 0`), folgt `moveq r0,#1` und direkte Rückkehr mit `1`. Ist er nicht null, wird `moveq` übersprungen und `bne 0x2fc5f0` führt zur Fehlerprotokollierung; danach Rückkehr mit `1`.

Der erlaubte Caller-Kontext zeigt die Blockbasis bei `CMLoadComponent3` als `fp-0x58` (`0x2ffd04`/`0x2ffd00`); `0x2ffd2c` speichert den vom Caller vorbereiteten Wert bei `fp-0x48`, also Basis `+0x10`, und `0x2ffd44` ruft `0x2fc530` mit Basis in `r0` und `1` in `r1` auf. WP-XE164-123 bindet den Wert an dieser Callerposition an das aufgelöste `ComponentEntry`-Callbackziel. Bei `0x2ffd60` und `0x2ffd78` folgende Caller-Calls laden andere Slots (`fp-0x44` und `fp-0x40`); sie sind nicht der Nachweis für den `+0x10`-Aufruf. Der direkte Beleg ist `0x2fc554` plus `0x2fc5c8` im Helfer.

Der zusammengefasste kanonische REA-Bundle [`rea-evidence-bundle.json`](rea-evidence-bundle.json) enthält 8 Records aus dem importierten WP-XE164-123 Bundle und 0 Unknowns. Es stützt den Caller-/Loader-Kontext, enthält aber wegen der REA-Timeouts keinen neuen `FUN_002FC530`-Funktionsrecord. Der neue Bodybefund ist aus dem angegebenen cross-`objdump`-Auszug und bleibt als statische Binärbeobachtung ausgewiesen.

## Alternative Erklärung und Restunsicherheit

Die Instruktionen beweisen die indirekte Verwendung des Wortes bei `+0x10`, aber nicht den zur Laufzeit tatsächlich dort gespeicherten Wert. Die Zuordnung zu `ComponentEntry` stammt aus dem gebundenen Loader-Handoff in WP-XE164-123; bei einem abweichenden Laufzeitblock oder einer anderen Aufrufquelle wäre `+0x10` lediglich ein indirektes Callbackziel. Die Bedeutung und genaue Größe des Stackobjekts bei `fp-0x5c`, die Typen der kopierten Werte und das vollständige API-Verhalten bleiben offen. Auch der `objdump`-Ausschnitt ist kein Laufzeitnachweis. Ghidras Funktionsgrenzen/Pseudocode konnten wegen des beobachteten Startup-Timeouts nicht frisch bestätigt werden.

## Status und Validierung

- Befund: **VERIFIZIERT** als statische Codebeobachtung; Zuordnung des Callerwortes zu `ComponentEntry`: **VERIFIZIERT** im angegebenen WP-XE164-123 Evidenzkontext.
- Reichweite: genau Body ab `0x2fc530` bis einschließlich Rücksprung `0x2fc704` und Callerfenster `0x2ffd00..0x2ffd80`; nächster klarer Prolog bei `0x2fc708`. Kein breiterer Callgraph analysiert.
- Tests: **NOT_RUN** (keine Softwaretests angefordert oder ausgeführt).
- Validator: [semantic_validator.js](semantic_validator.js), Laufresultat in `validator-result.txt`.
- Self-Review: durchgeführt. Kein unabhängiger Review oder Worker-Lauf behauptet.

## Dateien und Hashes

`SHA256SUMS` listet die SHA-256-Hashes der Paketdateien außer der Hashliste selbst. Keine Dateien außerhalb dieses WP-Ausgabeordners wurden geändert.
