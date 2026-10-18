> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-044 — Kontrollfluss innerhalb des 118-Byte-Grenzkandidaten

## Ergebnis

**VERIFIZIERT (begrenzte statische Beobachtung):** Der Seed `E03C38` beginnt in der angegebenen 118-Byte-Spanne einen linearen C166-Dekodierpfad. Der Fallback-Decoder liefert 32 lückenlos aufeinanderfolgende Instruktionen: 31 `mov`-Instruktionen mit sequenziellem Fallthrough, danach `rets` bei `E03CAC`. Im begrenzten Decode sind weder bedingte noch unbedingte Sprünge oder interne Calls enthalten. Alle 32 dekodierten Instruktionsstarts werden daher vom Seed über Fallthrough erreicht; im so gebildeten Kontrollflussgraphen bleibt kein dekodierter Instruktionsstart unverbunden.

Der einzelne zugelassene Caller bei Dateioffset `0x3686` dekodiert als `calls E03C38`. Das belegt die statische direkte Call-Kante von diesem Callsite zum Seed; es belegt keine übergeordnete Funktionsgrenze.

## Umfang und Methode

Eingabe: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`; vor der Analyse geprüfte Größe **17,110 Bytes** und SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.

Zuerst wurde REA `open_binary` für genau diese Composite-Datei mit Provider `ghidra` versucht. REA wies das headerlose `.bin` als `unsupported binary format` zurück (`target_unavailable`, `file_format_rejected`); damit liegt die im Auftrag geforderte beobachtete Lücke vor. Kein Ghidra-Disassembly und keine Ghidra-Funktionsgröße werden als Ergebnis behauptet. Danach wurde der dokumentierte REA/Rizin-C166-Fallback verwendet. REA-Version **6.5.0**; Rizin-CLI **0.9.1** (`c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`), Linux x86-64. Die Rizin-Kommandos liefen über REA mit `-N -q`, also ohne Benutzereinstellungen und Skripte. Dekoderkonfiguration: `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`.

Für die Intervallbeobachtung wurden exakt 118 Bytes ab Dateioffset `0x3c38` gelesen (`p8 118`) und mit einem auf 118 Bytes beschränkten linearen C166-Decode (`pD 118`) abgeglichen. Der Decode endet bei `0x3cac`, also unmittelbar vor exklusivem Ende `0x3cae`; es wurde kein Byte ab `0x3cae` abgefragt. Der Caller wurde isoliert bei `0x3686` untersucht: `p8 4` plus `pd 1`. Damit wurden keine anderen Caller verfolgt.

Die Tabellen zeigen zusätzlich zur Rohdatei-Position die vom Auftrag vorgegebene syntaktische Adressabbildung `E00000 + Dateioffset`. Das ist eine Darstellungsannahme für Adressen und kein unabhängiger Nachweis einer tatsächlichen Speicherabbildung.

## Beobachtete Struktur

`instructions.tsv` enthält alle 32 Instruktionen samt exakten Quellbytes; `edges.tsv` listet die 31 sequenziellen Fallthrough-Kanten sowie den abschließenden Return. `callsite.tsv` hält den einzelnen erlaubten Caller samt Bytes fest.

| Merkmal | Beobachtung | Status |
|---|---|---|
| Bereich | `0x3c38..0x3cad`, Ende exklusiv `0x3cae`, 118 Bytes | VERIFIZIERT |
| Linearer Decode | 32 Instruktionen, lückenlos und bytegenau | VERIFIZIERT |
| Seed-Erreichbarkeit | 32/32 Instruktionsstarts über Fallthrough ab `E03C38` | VERIFIZIERT |
| Kontrollfluss | 31 Fallthrough-Kanten; keine Branches oder internen Calls beobachtet | VERIFIZIERT |
| Terminal | `E03CAC`, Bytes `DB 00`, Rizin-Mnemonik `rets` | VERIFIZIERT |
| Zugelassener Caller | `E03686`, Bytes `DA E0 38 3C`, `calls E03C38` | VERIFIZIERT |
| Ghidra-Grenzkandidat 118 Bytes als Funktionskörper | Nicht unabhängig geprüft; Größe bleibt Kandidat/Hypothese | HYPOTHESE |

## Alternative Erklärung und offene Grenzen

Die durchgehend gültige C166-Lineardekodierung und das abschließende `RETS` passen zu einem linearen Routinefragment. Eine alternative Erklärung bleibt, dass die 118-Byte-Spanne lediglich ein Ghidra-Grenzkandidat ist: Ohne erfolgreiches Ghidra-Listing lässt sich nicht bestätigen, dass Ghidra tatsächlich dieselben Instruktionsstarts oder einen zusammenhängenden Funktionskörper annimmt. Ebenfalls offen bleibt, ob einzelne Bytes aus einer anderen Einstiegsperspektive Daten oder überlappender Code sein könnten. „Keine unverbundene Komponente“ gilt daher nur für den hier ausgewiesenen linearen Decode und den Startseed, nicht für alternative Einsprünge oder fremde Bytes außerhalb des Untersuchungsfensters.

**OFFEN:** unabhängige Ghidra-Bestätigung der Funktionsgrenze und alternative Einsprungpunkte. Nicht untersucht und nicht behauptet werden Operandensemantik, ABI, SFR-Bedeutung, Runtime- oder Hardwareverhalten. Die explizite `E00000`-Adressabbildung ist nur die im Auftrag vorgegebene Offsetdarstellung. Der Ghidra-Read-Failure bleibt als beobachtete REA-Lücke dokumentiert.

## Evidenz

Das kanonische, finding-only REA-Bundle enthält genau die drei zum Befund gehörenden Records und keine Unknowns:

| Evidence ID | Inhalt |
|---|---|
| `ev_5e9c49ddbc5c07ef46ec0d0416d74556ef89691a4ac6d5fbbf25edea552312f0` | Exakte 118-Byte-Rohfolge und linearer C166-Decode ab `0x3c38` |
| `ev_999c7e795fcd24984cc550f986e9644b74d5308fcf4d5ea37802b72297e1ac23` | Vier Callsite-Bytes und einzelner Decode bei `0x3686` |
| `ev_04eb32437faba97a47e4c7e36d22179f0348f926c80a1b8b20640af8cabd5003` | Isolierter Callsite-Decode `calls E03C38` |

Die Analysebefehle meldeten Exit-Code 0, vollständige Ausgabe, keine Trunkierung und keinen beobachteten Artefaktwechsel; der Post-Run-Hash entsprach dem Eingabehash. Der Ghidra-Open-Fehler wurde im REA-MCP-Rückgabewert beobachtet, hat aber keinen erfolgreichen Analyse-Record und ist daher nicht Teil des Finding-Bundles.

## Self-Review und Dateien

Self-Review: Der Paketvalidator gleicht Eingabehash und -größe, jede Instruktionsbytefolge gegen die Originaldatei, lückenlose 118-Byte-Abdeckung, Adressmapping, Kantenfolge, Callerbytes und die exakte Evidence-ID-Menge ab. Validatorlauf: **PASS** (Self-Review; kein unabhängiger Review wird behauptet).

| Datei | Zweck |
|---|---|
| `report.md` | Ergebnis, Methode, Einschränkungen und Evidenz |
| `instructions.tsv` | Vollständige lineare Instruktionstabelle mit Bytes und Seed-Erreichbarkeit |
| `edges.tsv` | Alle lokalen Fallthrough-Kanten plus terminaler Return |
| `callsite.tsv` | Nur der beauftragte Caller `E03686` |
| `rea-evidence-bundle.json` | Kanonischer finding-only REA-Export (3 Records, 0 Unknowns) |
| `validate_outputs.py` | Offline-Prüfung des Pakets gegen Originaleingabe und REA-Bundle |
| `SHA256SUMS` | Hashes aller erzeugten Paketdateien außer dieser Manifestdatei |
