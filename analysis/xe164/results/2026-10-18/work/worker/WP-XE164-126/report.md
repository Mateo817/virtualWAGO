> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-126 — Statischer Direktbezug 0x334790 / 0x32EA90

## Ergebnis

**VERIFIZIERT (bounded):** Im exakten ELF `codesys3` ist bei `0x00334790` ein 24-Byte ARM-Stub beobachtet. Die sechs Instruktionen richten kurz den Stackframe ein, stellen `fp`, `sp` und `lr` wieder her und führen bei `0x003347A4` einen unbedingten direkten Branch nach `0x00334648` aus. Es gibt in diesem Stub keinen `bl`/`blx`-Call, keinen Speicherzugriff außer Stack-Saves/Restores und keinen direkten Branch auf `0x0032EA90`.

**VERIFIZIERT (bounded):** Der vollständige von Rizin abgegrenzte Körper bei `0x0032EA90` umfasst 68 Byte: inklusive `0x0032EA90..0x0032EAD3`, entsprechend exklusiv `[0x0032EA90,0x0032EAD4)`. Er hat keine Call-Instruktionen. Im beobachteten Registerverhalten wird `r0` zuerst auf null geprüft. Falls nicht-null, wird ein 32-Bit-Wert aus `[r0+8]` geladen; bei nicht-null `r1` wird bedingt `0` nach `[r1]` geschrieben, und der Körper kehrt unmittelbar zurück. Falls `r0` null ist, wird `r1` geprüft. Bei nicht-null `r1` wird `2` nach `[r1]` geschrieben; die unmittelbar folgende Instruktion `ldm ... pc` kehrt zurück, bevor `mov r0,r1` bei `0x32EACC` erreicht werden kann. In diesem Zweig bleibt `r0` null. Bei null `r1` springt der Ablauf zu `mov r0,r1` (`0x32EACC`), setzt damit `r0` ebenfalls auf null und kehrt zurück. Also geben beide `r0==0`-Zweige `0` zurück; nur der `r1!=0`-Zweig schreibt zusätzlich den Statuswert `2`. Die Storewerte `0` und `2` liegen auf getrennten Rückkehrpfaden. Diese Beschreibung ist eine Übersetzung der beobachteten Instruktionen, kein API-Vertrag.

**Direkter Call-/Datenflussbezug: NEIN, innerhalb der begrenzten Abdeckung.** Der Stub bei `0x334790` verzweigt statisch nach `0x334648`, nicht nach `0x32EA90`. Der begrenzte Funktionskörper bei `0x32EA90` enthält keine Calls. Die gezielte Rizin-Xref-Abfrage für `0x32EA90` lieferte keinen Treffer. Im Stub sind keine globalen oder sonstigen Datenreferenzen zu sehen; der zweite Körper greift auf `[r0+8]` und `[r1]` zu, ohne einen statischen Bezug zum Stub oder zu dessen Nachfolgeradresse zu zeigen. Daher ist weder ein direkter Call noch ein direkter Datenfluss zwischen den zwei untersuchten Körpern belegt.

Der Stub-Zielkörper `0x334648` wurde nur als unmittelbarer Branch-Nachfolger begrenzt betrachtet. Rizin meldet dessen Körpergröße 328 Byte mit Ende direkt vor `0x334790`; in dieser Funktionsanalyse erscheinen direkte Calls bei `0x334688`, `0x3346D8`, `0x3346B0`, `0x334718` sowie der Tail-Branch bei `0x3347A4` ist außerhalb dieses Körpers. Der Name an `0x334648` ist als beobachtete Symbolschreibweise `iomgrconfiggetdriver` verzeichnet. Keiner dieser beobachteten direkten Callziele ist `0x32EA90`. Das ist kein Beleg für fehlenden indirekten, datengetriebenen oder laufzeitvermittelten Zusammenhang.

## Bounded Körper und minimale Pseudocode-Skizze

Die folgende Skizze enthält ausschließlich aus den beobachteten Instruktionen abgeleitete Register-/Speicheraktionen. Registerkonventionen werden nur soweit benannt, wie Rizin sie für die beiden Körper meldet (`r0`, `r1`).

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Auf dem Pfad mit ursprünglichem `r0 != 0` wird `r0` aus `[r0+8]` gelesen und als Register-Rückgabewert belassen; optional wird `0` an `[r1]` geschrieben. Bei ursprünglichem `r0 == 0` und `r1 != 0` schreibt der Körper `2` an `[r1]` und kehrt mit unverändertem `r0==0` zurück. Bei ursprünglichem `r0 == 0` und `r1 == 0` setzt `mov r0,r1` den Wert auf null und kehrt zurück. Keine globale Adresse oder globale Speicherstelle wurde in diesen zwei Körpern beobachtet.

## Beweismittel, Adressräume und Werkzeuge

- Eingabedatei: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`
- Größe: `5,181,396` Byte; SHA-256: `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`
- Adressen: REA/Ghidra meldete ELF/ARM, Default-space- und ELF-VMA-Adressen in Little-Endian ARM32. Für die Rizin-Fallbackbeobachtungen lauten die inklusiven Funktionsgrenzen `0x334790..0x3347A7` (24 Byte) und `0x32EA90..0x32EAD3` (68 Byte), entsprechend den exklusiven Bereichen `[0x334790,0x3347A8)` und `[0x32EA90,0x32EAD4)`.
- REA: `rea-agents 6.5.0`, Ghidra Provider `12.1.4`, Profilhash `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. `open_binary` band die erwartete Datei. `analyze_function(0x334790)` und `procedure_pseudo_code(0x334790)` liefen jeweils in den gemeldeten Provider-Timeout (300 s / 330 s); Ghidra stellte wegen nicht abgeschlossener Auto-Analyse keine partiellen Funktionsbeobachtungen bereit.
- Benannter Fallback, einmalig nach dem beobachteten REA-Timeout: `rizin 0.9.1`, Build `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. `afij`/`pdf` für die exakten Adressen, `pdj` für den Branch bei `0x3347A4`, `is` für Symbolzuordnung und gezielte `axt`-Abfragen an `0x334790` und `0x32EA90`.
- `objdump` GNU Binutils `2.44` war als weiterer Fallback nicht verwendbar: Host-Objdump meldete `can't disassemble for architecture UNKNOWN`; es wurde nicht weiter genutzt.
- Datei [rea-evidence-bundle.json](rea-evidence-bundle.json) ist der kanonische REA-Export dieses Laufs. Er enthält 0 Records/0 Unknowns: REA meldete die exakte Dateiöffnung, aber wegen Provider-Timeouts wurden keine Funktions-Evidence-Records erzeugt. Rizin-Ausgaben werden daher als Fallbackbeobachtung dokumentiert, nicht als REA-Evidence.

## Alternative Erklärung und Restunsicherheit

**HYPOTHESE:** Der Stub bei `0x334790` kann als separater Einstieg dienen, der in den vorangehenden Körper `0x334648` weiterleitet. Die Namensähnlichkeit zwischen beobachteten Literalen/Symbolen und `0x32EA90` beweist weder Alias noch gemeinsamen Vertrag.

**Alternative Erklärung:** Die zwei Namen können gleichartige oder verwandte Routinen in getrennten Codepfaden benennen, während der Stub-Branch und die beobachteten direkten Calls nur einen anderen Pfad abbilden. Ein indirekter Verweis, eine dynamische Bindung oder eine gemeinsame, nicht in den Körpern enthaltene Datenquelle bleibt möglich; die hier untersuchten Instruktionen entscheiden das nicht.

**OFFEN:** Kein globaler all-callers/all-dataflow Vollständigkeitsnachweis; kein indirektes Ziel- oder Laufzeitverhalten; keine API-/Struct-/Feldsemantik; keine Bedeutung der gespeicherten Werte `0` und `2` jenseits ihrer unmittelbaren Konstanten; keine Aussage über weitere Tabellenpositionen. Rizin ist die benannte Fallbackquelle und keine unabhängige Bestätigung von REA. Kein Target-Execution-, Geräte-, VM- oder Netzwerkzugriff.

## Status

| Tätigkeit | Status |
|---|---|
| Eingabegröße und SHA-256 | PASS |
| REA-Dateibindung durch `open_binary` | PASS |
| REA vollständige Funktionsanalyse | BLOCKED — Provider-Zeitüberschreitung; keine partielle Evidence |
| Einmaliger exakter Rizin-Fallback: beide Körper und gezielte Xrefs | PASS |
| Direkter statischer Call-/Datenflussbezug der beiden Körper, bounded | PASS — keiner beobachtet |
| Indirekte/laufzeitvermittelte Relation | NOT_RUN |
| Geräte, Runtime, VM, Netzwerk | NOT_RUN |
| Self-Review dieses Berichts/Validators | PASS |
| Unabhängige Prüfung | NOT_RUN |

## Prüfer und erzeugte Dateien

`validate.py` prüft Quelldateiidentität, Grenzen, alle im Bericht aufgeführten Instruktions-/Datenflussclaims, die REA-Bundle-Schemabindung und Datei-SHA-256-Werte. Der Validator ist ein Self-Review; ein unabhängiger Reviewer oder weiterer Workerlauf wird nicht beansprucht.

- `report.md` — Ergebnis und begrenzte Begründung.
- `rea-evidence-bundle.json` — kanonischer REA-Export (0 Evidence-Records; siehe Timeout-Einschränkung oben).
- `validate.py` — semantischer Validator.
- `SHA256SUMS` — SHA-256 aller erzeugten Dateien außer dieser Manifestdatei.
