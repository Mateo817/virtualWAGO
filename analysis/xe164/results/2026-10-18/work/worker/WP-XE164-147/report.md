> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-147 — zweiter publizierter Zielkörper (`0x0B58..0x145F`)

## Ergebnis

**VERIFIZIERT (statische Instruktionssemantik):** Der untersuchte Körper beginnt bei Ghidra `0x10B58` und endet inklusiv bei `0x1145F`. Im hier bestätigten Mapping entspricht das ELF-VA und Dateioffset `0x0B58..0x145F` (Ghidra-Adresse minus `0x10000`). Eintrittsregister `r0` wird nur auf den Stack geschrieben; der gespeicherte Wert wird vor dem ersten Call mit `0` überschrieben und im Körper nicht zurückgelesen. Eintritts-`r1` wird auf `[sp+4]` gespeichert und bleibt dort; Ghidra-Pseudocode zeigt ihn als zusätzlichen Stackwert beim ersten Call. Eintritts-`r2` und `r3` werden vor dem ersten Call überschrieben und nicht zuvor gelesen. Daher ändert eingehendes `r0=0` den beobachteten Ablauf nicht; der gespeicherte Nullwert wird an `[sp+0]` durch denselben Nullwert ersetzt.

**VERIFIZIERT:** Der Körper führt 62 indirekte `blx`-Calls in der Reihenfolge aus `calls.tsv` aus. Alle 62 Ziele sind in REA/Ghidra unaufgelöst; es wurden keine Callee-Körper untersucht. Der Aufruftransport ist in der Tabelle auf die beobachteten Register-/Stackwerte begrenzt: `r0` erhält jeweils eine Stringliteral-Adresse, `r1` die Adresse einer sukzessiven 32-Bit-Zelle, `r2` ist bei Call 1 und 2 `2`, danach `0`; `r3=0`; `[sp+0]=0`. `[sp+4]` enthält weiterhin Eintritts-`r1`; nur der erste Call wird im Ghidra-Pseudocode mit diesem zusätzlichen Wert dargestellt. Literaltexte und von Ghidra dargestellte Callausdrücke sind keine nachgewiesenen API-Verträge.

**VERIFIZIERT:** Die ersten zwei Call-Ergebnisse werden verworfen; danach folgt auf jeden Call 3 bis 61 ein Vergleich `SUBS r3,r0,#0` und ein `BNE 0x11454`. Ein Nichtnullergebnis springt zum gemeinsamen Returnpfad; Null setzt die Kette fort. Call 62 wird nicht geprüft. Sein `r0`-Wert wird bei `0x11450` nach `r3` kopiert. Der gemeinsame Tail `0x11454..0x1145C` kopiert `r3` zurück nach `r0` und kehrt zurück. Der statisch begrenzte Rückgabemechanismus ist somit: erstes Nichtnull-Ergebnis unter Calls 3–61, sonst Ergebnis von Call 62. Welche Werte die unaufgelösten Ziele tatsächlich liefern können, ist **OFFEN**; daher wird keine enger begrenzte numerische Rückgabedomäne behauptet.

## Call- und Branch-Mechanik

Die vollständige Instruktionsliste steht in `instructions.tsv` (578 Instruktionen), die geordnete Callliste in `calls.tsv` (62 Sites), die Status-Branches einschließlich zugehörigem `SUBS` in `branches.tsv` (59), der Ghidra-CFG-Blockgraph in `cfg.tsv` (61 Blöcke) und die Pfad-/Ergebnisklassifikation in `results.tsv`. Diese Tabellen wurden reproduzierbar aus dem vollständigen REA-Datensatz erzeugt. Callsite-Adressen und Dateioffsets stehen jeweils nebeneinander.

An der ersten Callsite `0x10B84` steht in `r0` die Adresse des Literals `LogAdd`, in `r1` die Adresse `0x26094`, in `r2=2`, `r3=0` und `[sp+0]=0`; `[sp+4]` enthält Eintritts-`r1`. Bei `0x10BA4` sind Literal und Zelle `CMUtlMemCpy` beziehungsweise `0x26098`, mit denselben beobachteten Register-/Stackwerten. Ab `0x10BC4` ist `r2=0`. Danach werden Stringliteral-Adressen und Zellen in der Tabellenreihenfolge fortgeschaltet. Die Indirektziele werden jeweils aus dem an Ghidra `0x26090` bezeichneten Wort geladen; ihr tatsächlicher Wert/Ziel ist nicht durch REA-Referenzen aufgelöst.

`branches.tsv` bindet jeden Statusbranch an den unmittelbar davor liegenden `SUBS`-Vergleich. Alle 59 Branches sind `BNE 0x11454`. Die zwei nicht geprüften Ergebnisse am Anfang und der direkte Rückgabepfad nach Call 62 sind separat in `results.tsv` ausgewiesen. Der genaue Inhalt der Statuswerte und Nebenwirkungen innerhalb der Calls bleiben außerhalb dieser Körpergrenze.

## Gegenprüfung der Eintrittswerte und des Falls `r0=0`

| Eintrittswert | Körperbeobachtung | Status |
|---|---|---|
| `r0` | Gesichert durch `STMDB` bei `0x10B58`; erstes späteres Stackwort `[sp+0]` wird bei `0x10B80` auf `0` geschrieben. Es gibt keinen Load des gespeicherten Eintrittswerts. | **VERIFIZIERT** |
| `r1` | Gesichert durch `STMDB` bei `0x10B58`; `[sp+4]` bleibt unverändert. Ghidra-Pseudocode zeigt den Wert nur am ersten Call als zusätzlichen Stackwert. | **VERIFIZIERT** |
| `r2` | Wird bei `0x10B6C` auf `2` gesetzt, vor einem möglichen Lesen des Eintrittswerts. Danach für die Resolverkette auf `0` gesetzt. | **VERIFIZIERT** |
| `r3` | Wird bei `0x10B64` aus `r5=0` gesetzt, bevor es als Argumentquelle verwendet wird. | **VERIFIZIERT** |

Für `r0=0` wird am Prolog ein Nullwert gesichert; bei `0x10B80` wird genau dieses Stackwort explizit wieder auf Null gesetzt, bevor `blx r6` ausgeführt wird. Der beobachtete Codepfad ist deshalb für diesen Eingangswert derselbe wie für beliebiges Eintritts-`r0`. Das belegt weder Gültigkeit noch Nutzung der übrigen Eingaben durch die unbekannten Call-Ziele.

## Gegenprüfung von E-XE164-087 und vorherige Evidenz

**VERIFIZIERT (Übereinstimmung):** Die frische Instruktionsanalyse stimmt mit E-XE164-087 überein, dessen akzeptiertes Quellpaket WP-XE164-077 ist (Report-SHA-256 `578a98557944915b188b7a6ab9d8177e2324ff1b99a630ff3bf6c31645878e42`). Beide belegen für diesen selben `libIoDrvDal.so`-Körper zwei anfängliche Calls ohne Ergebnisprüfung, gefolgt von geordneten Statusprüfungen, bei denen der erste Nichtnullstatus zum gemeinsamen Rückgabepfad gelangt. Es besteht kein Befundkonflikt. Diese Übereinstimmung gilt für die Instruktions-/Statusmechanik; sie ergänzt keine Callee-Signaturen oder semantischen API-Verträge.

WP-XE164-144 (Inputreport SHA-256 `ed6dfcec73f4bb1e74b711a0304fa150809c19514422a5391da7a96a9d5060ab`) betrifft den getrennten `ComponentEntry`-Körper und belegt hier keine zusätzlichen Callee-Verträge.

## Evidenz, Umfang und Status

- Eingabe: `libIoDrvDal.so.1.0.2`, 25.976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.
- REA-Beleg: `ev_de10eed02c5be89e715d5aba6aae06852dc9c8a123c9e99c1ffe68addc13848c`; Ghidra 12.1.4, ARM, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Body: Ghidra inclusive `0x10B58..0x1145F`; ELF-VA und Datei `0x0B58..0x145F`; 2.312 Bytes, zusammenhängend.
- REA meldet 578 Assemblyinstruktionen, 61 CFG-Blöcke, vollständigen Ghidra-High-Pcode mit 371 Operationen, `truncated=false`, ausgelassene Operationen-Untergrenze `0`. Es gibt 62 `unresolved_calls` und keine aufgelösten Callees. Der REA-Export umfasst einen Datensatz und null Unknowns.
- REA-first: `open_binary`, `analyze_function(0x10b58)`, dann `export_evidence_bundle`. Es gab keinen Timeout oder fehlende erforderliche Körperfacette; deshalb kein Fallback-Disassembly.
- Keine Runtime-, VM-, Netzwerk-, Geräte- oder Hardwareaktion. Keine Callee-Körper, Caller oder außerhalb dieses Körpers liegenden Funktionen wurden untersucht.

Alternative Erklärung (**HYPOTHESE**): Die Folge kann ein geordneter Resolver-/Initialisierungsbatch sein, bei dem die ersten zwei Ergebnisse absichtlich unberücksichtigt bleiben. Die beobachteten Literaltexte passen dazu, beweisen aber weder Namensvertrag noch Zweck, Erfolgskonvention oder Rollbackverhalten.

Restunsicherheit (**OFFEN**): tatsächliche Ziele und Effekte aller indirekten Calls; Semantik und Wertebereich der zurückgegebenen Statuswörter; ob ein früher Nichtnullpfad bereits vorgenommene Änderungen rückgängig macht; tatsächliche Laufzeit-Ausführung und Speicher-/Relokationszustand. Statische Analyse belegt keine Ausführung.

## Validator und Artefakte

`validate.py` prüft die drei vorgegebenen Eingabehashes und -größen, wählt den REA-Datensatz eindeutig über seine Evidence-ID, validiert Provider/Profil/Body/Value-Flow und erzeugt die vollständigen Maschinen- und Ergebnis-Tabellen. Es prüft zusätzlich semantisch jede Spalte für alle 62 Callzeilen und 59 Branchzeilen auf Adresse, ELF-VA, Dateioffset, Instruktion, Ziel-/Argumentquelle und Ergebniszuordnung. Ausgabe: `validation.txt`, **PASS**. Runtime-Tests: **NOT_RUN**; unabhängige Prüfung: **NOT_RUN**. Die pseudocodebasierten Zeilen sind Ghidra-Werkzeugausgabe, kein Quellcode.

`rea-evidence-bundle.json` ist der unveränderte REA-Export. `SHA256SUMS` enthält Hashes der Paketdateien außer sich selbst.
