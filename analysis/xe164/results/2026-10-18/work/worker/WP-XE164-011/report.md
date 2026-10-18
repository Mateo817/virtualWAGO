> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-011 — E00BEE bounded static structure

## Ergebnis

Im gebundenen Composite liegt der von `E00BEE` statisch erreichbare, zusammenhängende Funktionsbereich bei `E00BEE..E00C0F` (inklusive), Dateioffset `0x0BEE..0x0C0F`. Die gezielte Ghidra-C166-Auswertung dekodierte darin neun Instruktionen in einem linearen Basicblock. Es gibt zwei direkte ausgehende Calls (`E00BEE → E0043C`, `E00C0A → E0045C`); deren Ziele wurden nur als Call-Adressen erfasst und nicht weiterverfolgt. Der Block endet mit `rets` bei `E00C0E`.

Die behauptete eingehende Kante von `E00F18` zu `E00BEE` bestätigt sich nicht: die einzelne dort manuell dekodierte Instruktion ist `calls 0xE004CA` (Offset `0x0F18`, Bytes `DAE0CA04`). `E004CA` ist ausgeschlossen und wurde nicht analysiert. Die materialisierte direkte eingehende Referenz auf `E00BEE` kommt stattdessen von `E00F28` (Offset `0x0F28`, Bytes `DAE0EE0B`, `UNCONDITIONAL_CALL`). `E00F28` wurde ausschließlich als einzelne Callsite zur Referenzprüfung dekodiert; seine Funktion und sein Kontrollfluss wurden nicht verfolgt.

## Beobachtungen und Status

- Composite-Identität vor Analyse geprüft: 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` — **VERIFIZIERT**.
- Replay-Konfiguration: [composite-replay.md](PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md), 2,169 Bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`. Sie bindet die Composite, Ghidra 12.1.4, Language `C166:LE:16:default`, Compiler-Spec `tasking`, BinaryLoader-Basis `0xE00000` sowie das unveränderte Originalscript. Dieses Originalscript wurde für den begrenzten Lauf nicht ausgeführt.
- REA zuerst: der erste `execute_rizin_command`-Versuch (Evidence `ev_691325e1a1d9420359abfaf0c48fe08b2723f36abe6a2d67158532550988f84`) suchte fälschlich bei der Analyseadresse als Datei-Offset und meldete `Failed to read chunk of size 0x101 at 0xe00bee from io`; diese Instruktionsausgabe wird nicht als gültige C166-Dekodierung verwendet. Danach bestätigte Evidence `ev_83195fa2c5771b70ddb3c728087b5ddd24d8a55803f9fa93cf51267620851dff` die wirksame Konfiguration `asm.arch=c166`, `asm.bits=16`, `asm.cpu=c166`. Mit dem korrigierten Datei-Offset ergab `e asm.arch=c166; e asm.bits=16; s 0xbee; pd 9` (Evidence `ev_ed55114c824eafd30c2951dfb05a2785d8d6008d56896e2fbd3faf8587613680`) neun Instruktionen von `0x0BEE` bis `0x0C0E`, übereinstimmend mit dem Ghidra-Befund. Ein weiterer REA-Konfigurationsaufruf zeigte Defaultwerte x86/64 bei nicht gesetzter Architektur (Evidence `ev_e777854f816a6a8a6b63865dbc830298192e934e91bb2ba7e0d2fcf2df267063`); er diente nur der Einordnung des Fehlversuchs. Die Toolversion bleibt durch REA unbekannt. Der gezielte Ghidra-Fallback war weiterhin erforderlich, weil REA-Rizin hier keine manuelle CFG-/Basicblock-/Referenzstruktur ausgibt. Kein erneuter `open_binary`-Versuch.
- Ghidra 12.1.4 Headless, Raw Binary / BinaryLoader, `C166:LE:16:default`, `tasking`, Basis `0xE00000`; `-noanalysis`, `-readOnly`, `-deleteProject`, ein Worker, Timeout 45 s, unter `unshare -Un --map-current-user`. Der Lauf verwendete ausschließlich die manuelle Seed-Auswertung E00BEE und zwei isolierte Callsite-Probes E00F18/E00F28. Das vollständige Replay-Originalscript mit seinen anderen Seeds wurde nicht ausgeführt.
- Der Seed-Ablauf ist linear: Calls haben jeweils Fall-through-Kanten; sieben normale Fall-throughs führen bis zum terminalen `rets`. Ein zusammenhängender Bereich umfasst 34 Bytes; neun Instruktionen. Die Tabellen [instructions.tsv](instructions.tsv), [edges.tsv](edges.tsv), [calls.tsv](calls.tsv) und [references.tsv](references.tsv) enthalten die dekodierten Details.
- Ghidra-Referenzen an den neun Seed-Instruktionen weisen zwei Call-Edges aus, keine beobachteten Nicht-Call-Referenz-Edges. Die Operanden wie `0xFE1C`, `0xFF48`, `0xFE48` und `0xFE4A` werden nur als dekodierte Instruktionsoperanden dokumentiert; daraus werden weder Referenztyp noch Register-/SFR-Semantik abgeleitet.
- Kontrollfluss-/Call-Struktur **VERIFIZIERT** für diese explizite statische Auswertung. Direkte Eingangsreferenz im frisch importierten Replay-Memory **VERIFIZIERT** nach dem isolierten Decode von E00F28. Die gegenteilige Prämisse E00F18 → E00BEE **widerlegt** durch den Ein-Instruktions-Probe E00F18 → E004CA.
- Teststatus: Eingabehash-Gate **PASS**; erster Rizin-Aufruf **FAIL** als Analyseadress-/Dateioffset-Verwechslung; korrigierter Rizin-C166/16 Decode bei Datei-Offset `0x0BEE` **PASS** für neun Instruktionen; gezielter Ghidra-Lauf **PASS** (Headless meldet Import succeeded, Script-Ausgabe enthält erwartete Sprache, Compiler, CFG und References); TSV-Validator **PASS** für alle vier TSVs und den Byteabgleich mit dem gebundenen Composite. Frühe Script-Kompilierversuche hatten Importfehler, wurden vor dem erfolgreichen finalen Lauf korrigiert; `ghidra-success.log` und `script-success.log` stammen vom fehlerfreien Endlauf. Full-program autoanalysis **NOT_RUN**.

## Reproduzierbarkeit und Grenzen

Das verwendete eigene Ghidra-Script ist [E00BEEProbe.java](E00BEEProbe.java), 8,125 Bytes. Es enthält die CFG-Wanderung mit Ausschluss direkter Callees, begrenzt auf den gemappten Composite-Bereich, und begrenzt die zusätzlichen Callsite-Probes auf je eine Instruktion bei E00F18 und E00F28. Das reproduzierbare Aufrufskript ist [run.sh](run.sh). Das fremde/originale [Xe164Probe.java](PRIVATE_ANALYSIS_ROOT/work/ghidra/scripts/Xe164Probe.java) wurde nicht benutzt; laut Replay-Dokument hat es andere Seeds und hätte den hier verlangten engen Scope überschritten. Für dieses Originalscript: 4,315 Bytes, SHA-256 `9289f41396180a3478ce3e64e70f54d38a397e5f4f7247b89bd8e8bf2808490f`.

Ghidras Instruktionsstrings und alle Tabellenwerte sind **Werkzeugableitungen**, keine Quelltextrekonstruktion. Es wurde kein Pseudocode erstellt. Die per Script ermittelte Basicblock-Grenze ist eine Ableitung aus Instruktionsfluss und Terminalfluss; sie ist keine Laufzeitbeobachtung. Der beschränkte `-noanalysis`-Lauf belegt keine Vollständigkeit beliebiger Datenreferenzen außerhalb der dekodierten Instruktionen und der zwei Callsite-Probes. Es werden keine SFR-, Interrupt-, K-Bus- oder Registersemantiken zugewiesen. Alternative Erklärung für nicht beobachtete weitere eingehende Kanten: sie sind möglicherweise im begrenzten Replay nicht materialisiert; die Suche wurde nicht auf weitere Funktionen/Calls erweitert. Kein unabhängiger Review; die Prüfung ist Self-Review durch den Worker.

## Erzeugte Artefakte

Neben diesem Report wurden `instructions.tsv`, `edges.tsv`, `calls.tsv`, `references.tsv`, `REA-Evidence-Bundle.json`, `E00BEEProbe.java`, `run.sh`, `validate_outputs.py` sowie Ghidras `ghidra-success.log` und `script-success.log` erzeugt. Die initiale Serialisierung von `instructions.tsv` und `edges.tsv` enthielt wörtliche Escape-Sequenzen beziehungsweise Patch-Artefakte; nach dem Self-Review wurde sie in echte TSV-Zeilen korrigiert. `validate_outputs.py` parst alle vier TSVs und prüft Zeilenanzahl, Kontiguität, Bytes gegen das gebundene Composite, Edge-/Call-Kanten und beide Caller-Probes. Die vier zusätzlichen Logdateien `ghidra.log`, `script.log`, `ghidra-final.log` und `script-final.log` bewahren frühere tatsächliche Workerläufe einschließlich korrigierter Script-Kompilierfehler auf; der erfolgreiche Endlauf steht separat in `*-success.log`. Das REA-Bundle enthält vier Datensätze aus den Rizin-Command-Beobachtungen. Die Bytegrößen und SHA-256 aller aufgeführten Ausgabe-Dateien (einschließlich dieses Reports) sind in `SHA256SUMS` aufgeführt; `sha256sum -c SHA256SUMS` wurde nach der TSV-Korrektur erneut ausgeführt und war PASS.

SHA-256 der übrigen Dateien:

| Datei | SHA-256 |
|---|---|
| `calls.tsv` | `ad5836809f724daec9344985ea273cd379209ef8a88e04fc36b3758e9268a547` |
| `edges.tsv` | `b738ba1e69a7829de6d14b2ddf8b95c4911e17f3406f92e2f29059372f26a964` |
| `instructions.tsv` | `9286455cc30f050d17c14ebf1b02be35a84bb51d0b748d0e4e1256a45bc24080` |
| `references.tsv` | `c462b0e46bae696a9776e34988d4a309fcefe88d71d3730dc8442c873fef72fe` |
| `REA-Evidence-Bundle.json` | `c7c427693631bbe9ca4c1da4e278e2f98f1a8c0368518709c2e12685a1e850cd` |
| `E00BEEProbe.java` | `2c755a6e2fc721a9ff266b772c1f4e0589bdfe5e07c9c0ca729b17bbdc549d6a` |
| `run.sh` | `4a38ca6a2356497fa573dbb7751eb04c31552d402644e7f67673e9d662b362b4` |
| `validate_outputs.py` | `54b00551e940e4a70ebf530159ccdf0e012e9fab37c138c20b9ed95238a9a9a8` |
| `ghidra-success.log` | `5bea0a95428263ce5ba616ae642d07f6c8c235961c9ad8b2370a60c34aec6af8` |
| `script-success.log` | `d2b009fcebad4ecd32043b0362b647e866d2cff47d155ab5737a7bf9fbe93d70` |
| `ghidra.log` | `850d8c72afb5ebb1204b955a7508f13a95f304be26304287cca09e102214ee95` |
| `script.log` | `2a218f811d9b601d0b2c4432462ff54c7c37d68eb569f93a94519d24fb182654` |
| `ghidra-final.log` | `d6305d8664d381a599a98c43d435c3ecfad489ab6de5911d707adebf74d7f9eb` |
| `script-final.log` | `c7ffc12186556bab52040fdd2d413c44dbf9f2c27b64fad13293af007657c02b` |

Der Report selbst ist ebenfalls in `SHA256SUMS` gebunden.
