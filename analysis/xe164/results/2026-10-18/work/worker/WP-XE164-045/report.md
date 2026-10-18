> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-045 — zwei benachbarte Seed-Komponenten

## Ergebnis

**VERIFIZIERT** — Für die beiden separat angesetzten Seeds `E01DFA` und `E01E10` bildet der verwendete C166-Decoder jeweils einen seed-erreichbaren, zusammenhängenden Kontrollflussgraphen über genau 22 Datei-Bytes ab. Jeder Graph umfasst neun Instruktionsstarts, endet auf dem nicht genommenen bedingten Schleifenzweig in `RETS`, und sämtliche direkten Ziele bleiben innerhalb des jeweiligen 22-Byte-Fensters. Die Instruktionsmengen sind disjunkt. Die zwei isolierten Caller dekodieren als direkte `calls` zu den jeweiligen Seeds.

Das verifiziert zwei seed-erreichbare statische Komponenten in den untersuchten Fenstern. Es verifiziert keine umfassenden Funktionsgrenzen, Laufzeitwirkung, Schnittstellen- oder Hardwarebedeutung. Die zuvor aus Ghidra Replay stammenden 22-Byte-Kandidaten wurden als Hypothese behandelt; die Größe folgt hier aus dem separaten Rizin-Dekodier- und Reachability-Befund.

## Eingabe und Verfahren

| Element | Beobachtung |
|---|---|
| Eingabe | `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin` |
| Größe / SHA-256 | 17,110 Bytes / `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` (vor Analyse geprüft) |
| REA-Versuch | `open_binary` lehnte das headerlose Composite als `unsupported binary format` (`file_format_rejected`) ab. Das ist die beobachtete REA-Lücke und begründet den im Work-Package zugelassenen Rizin-C166-Fallback. |
| Decoder | REA `execute_rizin_command`, Provider Rizin; lokal offline geprüfte CLI-Version `0.9.1 @ linux-x86-64`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. |
| Konfiguration | `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`; alle Dekodierungen und Rohreads mit expliziten Datei-Offsets. Keine Geräte-, Netzwerk- oder VM-Nutzung. |
| Integrität | Alle Rizin-Beobachtungen meldeten Exitcode 0, vollständige Ausgabe, keine Änderung und dieselbe Eingabe-SHA-256. |

Die Adressbezeichnungen `E0xxxx` werden gemäß der vorgegebenen Basis `E00000` den Datei-Offsets zugeordnet (`E01DFA` → `0x1DFA`); es wird daraus keine Laufzeit- oder Load-Adresssemantik abgeleitet. Die vollständigen von Rizin gelieferten Bytes und Dekodierungen liegen in `rea-evidence-bundle.json`.

## Exakte Bereiche und Reachability

| Seed | Datei-Offsetbereich, Ende exklusiv | Länge | Instruktionsstarts | erreichbare Instruktionen | lokaler CFG-Kantenbestand |
|---|---:|---:|---:|---:|---:|
| `E01DFA` | `[0x1DFA, 0x1E10)` | 22 Bytes | 9 | 9/9 | 9 |
| `E01E10` | `[0x1E10, 0x1E26)` | 22 Bytes | 9 | 9/9 | 9 |

Für `E01DFA` lautet der beobachtete Ablauf: lineares Präfix `E01DFA → E01DFE → E01E00 → E01E04`; der Rizin-Bedingungscode `cc_UC`/`cond=al` führt von `E01E04` zu `E01E0A`. Der Vergleich bei `E01E0A` folgt nach `E01E0C`; der `NZ/NE`-Zweig geht zurück zu `E01E06`, dann linear über `E01E08` erneut zum Vergleich. Der nicht genommene Zweig führt zu `RETS` bei `E01E0E`.

Für `E01E10` ist die entsprechende, unabhängig ab Seed berechnete Folge `E01E10 → E01E14 → E01E16 → E01E1A`, der `cc_UC`-Sprung zu `E01E20`, der `NZ/NE`-Rückzweig von `E01E22` zu `E01E1C`, und der nicht genommene Zweig zu `RETS` bei `E01E24`. Jeder in `edges.tsv` gelistete Quell- und Zielknoten gehört zur eigenen Instruktionsmenge. Die aus Rizin gemeldeten sequentiellen `fail`-Adressen bei `cc_UC` wurden nicht als ausführbare Fallthrough-Kanten gewertet; der gemeldete Bedingungscode ist `al`. Selbst wenn man diese Decoder-Fail-Adresse nur als konservative Kandidatenkante notiert, bleibt sie im selben 22-Byte-Fenster und verändert die Disjunktheit der beiden Komponenten nicht.

`instructions.tsv` enthält die instruktionsgenauen, am Eingabeartefakt gegengeprüften Bytes und die Rizin-Dekodierung; `edges.tsv` enthält die beiden separat berechneten seed-lokalen Kantenmengen. Kein Ziel führt aus seinem Seed-Fenster heraus.

## Caller und Bytevergleich

| Caller | Datei-Offset | exakte Bytes | Rizin-Dekodierung | Ziel |
|---|---:|---|---|---|
| `E01F92` | `0x1F92` | `da e0 fa 1d` | `calls 0xe01dfa` | `E01DFA` |
| `E01F8E` | `0x1F8E` | `da e0 10 1e` | `calls 0xe01e10` | `E01E10` |

Die 22-Byte-Sequenzen sind bytegleich mit Ausnahme des unmittelbaren Operanden-Bytes im ersten Vier-Byte-Befehl: `e6 fc 00 d0` gegenüber `e6 fc 00 c0`. Die übrigen 18 Bytes sind identisch. Diese reine Bytebeobachtung begründet keine Interpretation der Operanden.

## Befundstatus, Alternativerklärung und Grenzen

- **VERIFIZIERT** — Beide Seeds erreichen innerhalb ihrer getrennten Fenster je neun instruktionsgenaue Dekodierungen; die Rohbytes decken die Fenster lückenlos ab. Die direkten Sprung- und Schleifenkanten sowie `RETS` bleiben jeweils intern.
- **VERIFIZIERT** — Die angegebenen Caller-Offsets enthalten vier Byte lange direkte `calls` mit den jeweiligen Seed-Zielen.
- **HYPOTHESE** — Dass diese Fenster die beabsichtigten vollständigen Funktionen im Sinn des ursprünglichen Ghidra-Replays darstellen. Der Befund zeigt seed-erreichbare Komponenten und eine lokale terminale Instruktion, aber keine unabhängige Funktionsmetadaten- oder Runtime-Bestätigung.
- **OFFEN** — Ob dieser statische Composite-Stream zur Laufzeit in diesen Grenzen ausgeführt wird oder welche Bedeutung die Instruktionen haben. Dies war ausdrücklich nicht Untersuchungsziel.

Eine alternative Erklärung ist, dass die 22 Bytes jeweils ein begrenzter, callbarer Codepfad beziehungsweise Fragment sind, während angrenzende Funktions- oder Laufzeitstruktur außerhalb der Fenster liegt. Die vorliegenden Beobachtungen widerlegen das nicht; sie belegen nur die getrennte seed-erreichbare lokale CFG-Struktur und die expliziten Caller-Ziele. Rizin-Disassemblierung ist Decoder-Evidence, keine Laufzeitbeobachtung und keine unabhängige Funktionsgrenzen-Bestätigung.

## Evidence und Prüflauf

REA-Bundle: `rea-evidence-bundle.json`, kanonischer Export mit sechs vollständigen `execute_rizin_command`-Records und null Unknowns. Die Records enthalten ausschließlich Beobachtungen zu den beiden Seed-Fenstern und den zwei vorgegebenen Callers. Zentraler Bundle-Record für 22-Byte-Rohdaten/terminale Dekodierungen: `ev_aee6e8f8e5de670023f08caa1d7f52e70f56f669dbbd985a66af9e2e4a596c69`. Caller- und erste Seed-Beobachtung: `ev_e9a10bd894e4a5abfa5bab2d370596a68fd1ed201cef1bc401fb91fddea024f3`.

Validator: `validate.py`. Ausführungsergebnis: **PASS** — Quellidentität, Instruktionsbytes, lückenlose 22-Byte-Abdeckung, Tabellenkanten, seed-getrennte Reachability, Mengen-Disjunktheit, Caller-Bytes/-Ziele und sechs an dieselbe Eingabe gebundene REA-Records geprüft. Der Validator prüft die Tabellenkonsistenz und Quelle, ersetzt keine unabhängige C166-Decoderprüfung.

## Ausgabedateien

| Datei | SHA-256 |
|---|---|
| `report.md` | wird nach Eintrag der übrigen Hashes berechnet; siehe `SHA256SUMS` |
| `instructions.tsv` | `bc313915c02984c135f8fea8e4e70cc2728e5f41e316960e6b07e06998caaa9c` |
| `edges.tsv` | `bea78b42e61da0b6f9fc26a2971f7082071f3d06c7a10454e1e6b53672f1e8ce` |
| `callers.tsv` | `0dd6b17ed1467d05a67370f6e12975038f732ac85e02d0ae4f8e05b8bfcdfb35` |
| `rea-evidence-bundle.json` | `efd434f21bdb69fae06f83ffa487c55d61aff7758034ac95db8b7f8b77e05da4` |
| `validate.py` | `b05e3ab35552144164ed0a30848d0497aa384469b2cfbdc83542e446006c6561` |
| `SHA256SUMS` | Selbst-Hash ausgelassen |
