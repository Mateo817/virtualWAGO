> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-116 — Klassifikation und statische Zuordnung des zweiten Stringfunds

## Befund

**VERIFIZIERT:** Das separate Literal `IoMgrConfigGetParameterValuePointer` bei Datei-Offset `0x39e618` nimmt an einem wiederkehrenden, statisch gespeicherten Funktions-/Namenszeiger-Paarmuster teil. Der Funktionszeiger steht bei Datei-Offset `0x39de1c` (Ghidra `0x3ade1c`) und enthält `0x0032e814`; der folgende Namenszeiger bei Datei-Offset `0x39de20` (Ghidra `0x3ade20`) enthält `0x003ae618`.

**VERIFIZIERT:** Die statische Paarung bindet den separaten Namen an Entry `0x32e814`, der als `IoMgrConfigGetParameterValuePointer` identifiziert ist. Damit lautet die Antwort auf die konkrete Frage: ja, das zweite Vorkommen nimmt an dieser statischen Paarung teil.

**VERIFIZIERT:** Die angrenzenden Wörter bestätigen die wiederkehrende 16-Byte-Form `[Funktionszeiger, Namenszeiger, 0, 0]`. Ein konkreter C-Structtyp oder Feldvertrag wird daraus nicht abgeleitet.

**OFFEN:** Tatsächlicher Tabellenverbrauch und Resolver-Laufzeitpfad sind statisch nicht belegt.

## Identität, Werkzeuge und Koordinaten

| Gegenstand | Beobachtung | Status |
|---|---|---|
| Eingabe | `codesys3`, 5.181.396 Bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | VERIFIZIERT |
| REA | `rea-agents` 6.5.0; Ghidra 12.1.4; ARM ELF; Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de` | VERIFIZIERT |
| enger Relokations-Fallback | GNU `readelf` aus Binutils 2.44; nur `readelf -rW` auf Relokationen mit Bezug zu den exakt geprüften Slots/Entries gefiltert | VERIFIZIERT |
| WP112-Quellinventar | `string_hits.csv`, SHA-256 `b4d0d2df7230aeb8005f94f5d7aeaceddbd99582de6746a9acb30a9ea2cbb358`; genannte Dateioffsets `0x45ec8` und `0x39e618` | VERIFIZIERT |
| WP114-Referenz | Bericht SHA-256 `f68c6e9ed33559d25df4c65c0c69018c4be96a943faed86171f5e2bdb23d0fe6`; Bundle SHA-256 `05dab16a4688c42c8bbe0dbca6aac4abfd4062a540dfcc749f25dd0b64c1fe3f` | VERIFIZIERT |

### Stringvorkommen

| Ursprünglicher Dateioffset | Ghidra Default-Space | Abschnitt/Typ | Befund | Status |
|---|---:|---|---|---|
| `0x45ec8` | `0x55ec8` | `.dynstr`; 36 Byte UTF-8 laut Ghidra | Der String liegt im dynamischen ELF-Stringbereich. Ghidras exakte Quellenabbildung liefert Datei-Offset `286408` (`0x45ec8`). Ghidras `xrefs` meldet an dieser Stringadresse keine materialisierten Referenzen. | VERIFIZIERT |
| `0x39e618` | `0x3ae618` | `.rodata`; 36 Byte US-ASCII laut Ghidra | Separates Literal. Ghidras Quellenabbildung liefert Datei-Offset `3794456` (`0x39e618`). `list_strings` gibt exakt den Namen aus. `xrefs` meldet an dieser Adresse keine materialisierten Referenzen. | VERIFIZIERT |

Beide exakten Zeichenfolgen wurden mit REA `search_strings` gefunden. Die Ghidra-Adresse `0x3ae618` ist kein aus dem Offset erratener ELF-VA: `address_to_file_offset` ordnet sie direkt auf Datei-Offset `0x39e618` ab. Das Accessor-Identitätsanker `IoMgrConfigGetParameterValuePointer` bei ELF/Ghidra-Adresse `0x32e814` wird hier nur zur Namensunterscheidung benutzt; dessen Body ist außerhalb des WP-Bereichs.

### Rohdaten und Kandidatenzuordnung

REA `read_bytes` las vollständig 128 Byte ab `0x3ade00`. Der relevante Ausschnitt lautet:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Die Wörter ergeben:

| Datei-Offset / Ghidra-Adresse | Beobachteter Wert | Zuordnung | Status |
|---|---|---|---|
| `0x39de1c` / `0x3ade1c` | `0x0032e814` | Funktionszeiger auf Entry `IoMgrConfigGetParameterValuePointer` | VERIFIZIERT |
| `0x39de20` / `0x3ade20` | `0x003ae618` | Namenszeiger auf das separate Literal `IoMgrConfigGetParameterValuePointer` | VERIFIZIERT |
| `0x39de2c` / `0x3ade2c` | `0x00333ed8` | Funktionszeiger auf Entry `IoMgrConfigGetParameterValueByte` | VERIFIZIERT |
| `0x39de30` / `0x3ade30` | `0x003ae63c` | Namenszeiger auf String `IoMgrConfigGetParameterValueByte` | VERIFIZIERT |

Die korrigierte Record-Phase beginnt bei `0x3ade0c`/Datei-Offset `0x39de0c`, nicht beim Namenswort. Das bestehende REA-Fenster enthält `0x3ade0c=0x00330718`, `0x3ade10=0x003ae5f8`, `0x3ade1c=0x0032e814`, `0x3ade20=0x003ae618`, `0x3ade2c=0x00333ed8` und `0x3ade30=0x003ae63c`. `list_strings` bestätigt `0x3ae5f8` als `IoMgrConfigGetFirstConnector`; Ghidras `procedure_info` identifiziert `0x333ed8` als Entry `IoMgrConfigGetParameterValueByte`. Die Rohwörter `0x3ade1c/20` zeigen die abgefragte statische Paarung.

Root-Audit-Korrektur: Die erste Auswertung begann die 16-Byte-Blöcke um vier Byte phasenverschoben am Namenswort. Die Root-Rohwortprüfung bestätigt zusätzlich das vorangehende Paar bei Datei-Offsets `0x39ddfc/0x39de00` (`0x00330780` / `0x003ae5dc`, GetNextConnector) sowie die Paare `0x39de0c/0x39de10` (GetFirstConnector), `0x39de1c/0x39de20` (Pointer) und `0x39de2c/0x39de30` (ValueByte). Die Phasenkorrektur ändert die ursprüngliche Schlussfolgerung; das exportierte REA-Bundle mit den Rohbytes bleibt unverändert.

### Vollbereichssuchen, Xrefs und Relokationen

**VERIFIZIERT:** Die REA-Byte-Suche war für den gesamten initialisierten Ghidra-Speicher vollständig (`complete=true`, 6.273.971 Bytes; nicht initialisierte `EXTERNAL`- und nicht geladene ELF-Metadatenbereiche sind separat ausgewiesen). Sie fand das genaue Wort `14 e8 32 00` nur bei:

- VA `0x43a6c`, `.dynsym`, Datei-Offset `0x33a6c` — dynamischer Symbolwert, konsistent mit WP114s `FUNC` bei `0x32e814`.
- VA `0x3ade1c`, `.rodata`, Datei-Offset `0x39de1c` — Funktionszeiger des Zielpaars.

Die Suche nach `18 e6 3a 00` fand genau einen Treffer bei VA `0x3ade20`, `.rodata`, Datei-Offset `0x39de20`: den Namenszeiger des Zielpaars. Die REA-Byte-Suche nach `14 e8 32 00` fand den Funktionszeiger desselben Paars bei VA `0x3ade1c`, `.rodata`, Datei-Offset `0x39de1c`, sowie den dynamischen Symbolwert bei VA `0x43a6c`, `.dynsym`, Datei-Offset `0x33a6c`. Ghidras `xrefs`-Abfragen zu den Stringadressen `0x55ec8`, `0x3ae618`, den Zeigerslots `0x3ade1c`, `0x3ade20` und den Function Entries `0x32e814`, `0x333ed8` waren leer. Das Fehlen materialisierter Ghidra-Xrefs löscht die unabhängig beobachteten Rohpointerbytes nicht aus; Ghidra materialisiert keine Xref-Kante für das Paar.

Der gezielte Fallback `readelf -rW` (GNU Binutils 2.44) ergab keine Relokationszeile für Slots `0x3ade1c` oder `0x3ade20` beziehungsweise die beiden Function Entries. Der Befehl prüfte die Relokationstabelle des gegebenen ELF; er rekonstruierte keine Laufzeitbindung. Keine weiteren Disassemblierungs- oder Binary-CLI-Fallbacks wurden benötigt.

## Evidenz und Unsicherheiten

REA-Evidence-IDs für die Kernbeobachtungen:

- Stringsuche: `ev_4482d2bcbc61a702b56c68cf217d49b1cf9aeaf01823bd1de34ccae9343c7d1a`
- Dateiabbildung Literal `0x3ae618 → 0x39e618`: `ev_5574e0b0682163eaeb358b0fabe992654f62373e8d919f54a25983fe1ef0f0ae`
- Dateiabbildung Entry `0x32e814 → 0x31e814`: `ev_84f4d8a66d6f73ffbeaa1966029feff6351625c4c8f2751b971c3c52cee70c71`
- Quellenabbildungen der zwei Zielslots `0x3ade1c → 0x39de1c` und `0x3ade20 → 0x39de20`: `ev_26783f565eff5eb9ef4b2268b17203a0473ef0353250f681c7095099ac3c93b9`, `ev_bf03b89335d8827cf15da945c4b627c965506e8b72e847922080d02fcb0b71bc`
- Vollständiger 128-Byte-Datenausschnitt ab `0x3ade00`: `ev_a227bb29bc3a7282ac42e7a83bfbf2127526af7afab45458b33783f041bec47f`
- vollständige Bytes des Identitätsanker-Entrys: `ev_0084cf1e82424f3e51245c2f5f1e58e8980a5b5121b47debdfa779b658e63601`
- Function-Info bei `0x333ed8`: `ev_a9d4cf8492554479dbd8c5d91c2e4ba5e1e9b2cd17950298cd9099fe196fc4ba`
- Byte-Suchen nach `14e83200` und `18e63a00`: `ev_bee53991daec8ba4d3c150f19e1736d3b65779291c5c53fa375f5f233aee2c4e`, `ev_14e0030d01eaf97f37443605dd6f205bfa6ab4e5281b3cfaf10a2c14b70a86c4`
- leere Xrefs zu den Zeigerslots und Entries: `ev_357561b425c49a0f33ff038055d590da5398a4679b06ec572c3dbf134dfce82d`, `ev_6c168e35ddb0a1091a8033f62820d0737004568293ea9b5db77379b5f6ef8e81`, `ev_73c7700eb823f08bbe5215807efdfd2e9e41b49ae14f0fdb1e26977e7b26c230`, `ev_7977b3f2d5dc109de5375fe2d4718092986fb7ea963fe5379e4e4335f95de32b`

**OFFEN:** Es ist nicht belegt, welcher Code den wiederkehrenden Datenbereich konsumiert, ob alle Blöcke gültige Einträge sind oder wie das Ziel bei Laufzeit aufgelöst/registriert wird. Die statische Paarung ist verifiziert; daraus folgt keine Ausführung oder Resolversemantik.

**HYPOTHESE:** Eine alternative Deutung ist ein inaktiver oder anders konsumierter Metadaten-/Dispatch-Datensatzbereich statt einer zur Laufzeit aktiven Registrierung. Die beobachtete statische Paarung bleibt davon unberührt.

## Prüfungen und erzeugte Dateien

| Prüfung | Status |
|---|---|
| Eingabegröße und SHA-256 gegen WP-XE164-116-Vorgabe | PASS |
| Beide Strings in REA-Suche; Ghidra-Dateiabbildung des separaten Literals | PASS |
| Byte-Suche nach Funktionszeiger und Literalzeiger über initialisierten Speicher vollständig | PASS |
| `readelf -rW` gezielt auf betroffene Slots/Entries gefiltert; keine passende Relokation | PASS |
| Runtime-/Resolververhalten | NOT_RUN |
| Validator und `SHA256SUMS` | PASS |

Erzeugt in diesem Workpackage-Verzeichnis: `report.md`, `rea-evidence-bundle.json`, `validate.py`, `SHA256SUMS`. Das REA-Bundle enthält 28 kanonische Sitzungsdatensätze, null Unknowns und die vollständigen ausgegebenen Rohresultate. Der aktive REA-Zielkontext wurde nach dem Export geschlossen.

Self-Review: Die Prüfungen und Textaussagen wurden anhand des eigenen Bundles und der genannten Quellhashes gegengeprüft. Kein unabhängiger Review oder Worker-Lauf wird behauptet.
