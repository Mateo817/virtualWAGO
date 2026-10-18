> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-043 — E01AB8 within the 78-byte boundary candidate

## Ergebnis

**VERIFIZIERT (statisch, Rizin-C166-Fallback):** Der begrenzte Decoder liefert im Fenster `0x1AB8..0x1B05` 28 Instruktionen über exakt 78 Bytes. Er meldet den Sprung `0x1AEE -> 0x1AF4` mit Fail-Kante nach `0x1AF0` sowie den Rücksprung `0x1AF6 -> 0x1AF0` mit Fail-Kante nach `0x1AF8`. Es folgen Calls von `0x1AF8` und `0x1AFC` zu Zielen außerhalb des Fensters. Der isolierte Caller `0x368A` ist `DAE0B81A`, dekodiert als `calls 0xe01ab8`.

Die lineare Dekodierung endet im Bereich bei `0x1B04` (`cmp r12, #0`); der nächste lineare Offset `0x1B06` liegt außerhalb des Auftragsbereichs und wurde hier nicht dekodiert. Somit bestätigt das Fenster keinen Funktionsabschluss bei `0x1B06`. Der Providergraph stellt einen Pfad vom Seed zum ersten Call bei `0x1AF8` bereit; dessen Bedingungsfeasibilität ist nicht unabhängig bestätigt. Eine Erreichbarkeit der Fortsetzung `0x1AFC` setzt eine Rückkehr von `0xE02DDA` voraus; `0x1B00` setzt Rückkehr von `0xE02DDA` und `0xE02DF6` voraus. Beide Fortsetzungen sind daher **HYPOTHESE**, Rückkehr bleibt **OFFEN**. Die 28 Instruktionen sind dekodiert, aber nicht pauschal als ausgeführt oder seed-erreichbar behauptet. Details stehen in [reachability.tsv](reachability.tsv).

## Identität, Scope und Methode

- Eingabe: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`; vor Analyse geprüft: 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Analysierter Ausschnitt: Dateioffsets/Analyseadressen `0x1AB8..0x1B05`, Ende exklusiv `0x1B06`, Länge 78 Bytes. Seed: `0x1AB8`.
- REA wurde zuerst versucht. `open_binary` lehnte das headerlose Composite mit `unsupported binary format` ab. Daraufhin wurde der dokumentierte Rizin-Fallback über `mcp__rea__execute_rizin_command` verwendet; konkrete Einstellungen: `asm.arch=c166`, `asm.bits=16`, Farben aus. Die lokalen Versionsabfrage meldete Rizin `0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`; REA-Evidence selbst meldet für die ausführbare Version `null`.
- Maßgebliche REA-Evidence: `ev_2d8ec2aad5dd06fed3394943364cf943e1890597a3a37c087bf67f9a28af4b30` (`px 78` und bytebegrenztes `pD 78`), `ev_c2ce537e5bb554f50b5b691902ff2b8b3f2c26f8a75c5bbe1665cdd7fb073931` (genau 28 `pdj`-Instruktionen, Summenlänge 78 Bytes) und `ev_f836f8293fa4c42c611b42bfbf3bc285d4eb269d74aa0343999003f7548a1a3b` (Caller `px 4`/`pD 4` bei `0x368A`). Instruktions-/Byte-Tabelle: [disassembly.tsv](disassembly.tsv); Caller-Tabelle: [caller.tsv](caller.tsv); Provider-Kanten: [flow.tsv](flow.tsv).
- Eingabeintegrität wurde von REA vor/nach dem begrenzten Kommando als unverändert gemeldet (`artifact_changed=false`). SHA-256 wird zusätzlich durch den Validator geprüft.

## Exakte Instruktions- und Kontrollflussbeobachtungen

`disassembly.tsv` protokolliert je Instruktion Adresse, Dateioffset, Bytes, Rizin-Text und Länge. Die Bytesumme beträgt 78. Der rohe Hexdump reicht genau von `0x1AB8` bis `0x1B05`.

| Caller-Adresse | Bytes | Instruktion | statisches Ziel | Länge |
|---|---|---|---|---|
| `0x368A` | `DAE0B81A` | `calls 0xe01ab8` | `0xE01AB8` | 4 |

Diese Beobachtung bindet nur die dekodierte Call-Kante des isolierten Callers an den Seed. Sie belegt keine Laufzeitausführung.

| Quelle | Rizin-Klassifizierung | gemeldetes Ziel | weiterer gemeldeter Pfad |
|---|---|---|---|
| `0x1AEE` (`0D02`) | `cjmp`, `jmpr cc_UC` | `0x1AF4` | `fail=0x1AF0` |
| `0x1AF6` (`3DFC`) | `cjmp`, `jmpr cc_NZ/NE` | `0x1AF0` | `fail=0x1AF8` |
| `0x1AF8` (`DAE0DA2D`) | `call` | `0xE02DDA` | Fortsetzung `0x1AFC` |
| `0x1AFC` (`DAE0F62D`) | `call` | `0xE02DF6` | Fortsetzung `0x1B00` |
| `0x1B04` (`48C0`) | lineare Instruktion `cmp` | — | nächster Offset wäre `0x1B06` (nicht dekodiert) |

Die Tabellen halten Provider-Ausgaben fest, nicht die tatsächliche Ausführung. `0x1AF0..0x1AF2` und `0x1AF4..0x1AF6` bilden im ausgegebenen CFG eine Rücksprungstruktur. Der CFG-Fail-Pfad vom Vergleich bei `0x1AF6` führt zum ersten Call bei `0x1AF8`. Die Call-Instruktionen haben Provider-Fortsetzungen `0x1AFC` und `0x1B00`; deren seed-Erreichbarkeit bleibt **HYPOTHESE**, solange die jeweilige externe Call-Rückkehr nicht belegt ist. Es werden keine Eigenschaften der Ziele behauptet. Die isolierte Caller-Beobachtung steht in [caller.tsv](caller.tsv).

## Status, Alternativerklärung und Restunsicherheit

- **VERIFIZIERT:** Eingabegröße/-hash; die beschränkten Bytes; 28 Instruktionsanfänge und Längen; die von Rizin ausgegebenen Branch-/Call-Ziele, `fail`-Offsets; der 4-Byte-Befund am Caller `0x368A`; und der 78-Byte-Bereich.
- **HYPOTHESE:** Die Ghidra-Größe von 78 Bytes bleibt nur ein Grenzkandidat. Diese Auswertung bestätigt keinen Ghidra-Body und keinen Funktionsabschluss an `0x1B06`.
- **OFFEN:** Rückkehr der externen Calls `0xE02DDA` und `0xE02DF6`; tatsächlicher Nachfolger und Kontrollfluss ab `0x1B06`; unabhängige ISA-Prüfung, ob Rizin `jmpr cc_UC` als bedingten Sprung mit erreichbarer Fail-Kante korrekt modelliert. Die Flow-Tabelle gibt genau die Providerbeobachtung wieder.
- **Alternativerklärung:** Der Ausschnitt kann Teil einer größeren Routine sein: `0x1B04` ist ein Vergleich und kein Kontrolltransfer; die lineare Fortsetzung liegt außerhalb des Scopes. Der Caller-Befund `0x368A -> 0xE01AB8` könnte ein statischer Verweis sein, ohne dass der Caller zur Laufzeit aufgerufen wird.
- **Restunsicherheit:** Keine Semantik von Registern, SFRs, ABI, Runtime oder Hardware abgeleitet. Der lokale `rizin -v`-Befund ergänzt die Versionsangabe, die in den REA-Records selbst fehlt. Ein erfolgreicher Call-Rücklauf kann aus den Bytes allein nicht abgeleitet werden.

## Scopeabweichung bei einem verworfenen Explorationsrecord

> Während der Exploration wurde einmal ein instruktionsanzahlbegrenztes `pdj 39 @ 0x1AB8` angefragt. Weil `pdj` nach Instruktionsanzahl statt Bytegrenze zählt, enthielt die rohe Antwort auch Material ab `0x1B06`. Diese Antwort wurde für den Befund nicht verwendet und ist nicht im finding-only Bundle enthalten. Die Tabellen stammen aus dem auf exakt 78 Bytes begrenzten `pD`-Record, dem auf 28 Instruktionen begrenzten `pdj 28`-Record (dessen dekodierte Längen 78 Bytes ergeben) und dem separaten `px 4`/`pD 4`-Caller-Record. Der globale REA-Recordspeicher kann den Explorationsrecord weiterhin enthalten.

## Ausgabedateien und Hashes

Alle Ausgaben liegen in diesem Work-Package-Verzeichnis. Hashes stehen in `SHA256SUMS`; `validate.py` prüft Eingabeidentität, genau zwei begrenzte Body-Records plus den isolierten Caller-Record im Finding-Bundle, Zeilenanzahl/Adressen/Bytegröße und Berichtmarker. Der kanonische REA-Export wurde auf genau diese drei Records projiziert; der verworfene `pdj 39`-Explorationsrecord bleibt ausgeschlossen.
