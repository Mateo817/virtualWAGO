> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-020 — E006C4 bis strikt vor E007D4

## Ergebnis

**VERIFIZIERT:** Vom Seed `E006C4` (Fileoffset `0x06C4`, bei Basis `E00000`) ist in der bytegebundenen C166-Disassemblierung der lokale Kontrollfluss bis zu den beiden `rets` bei `E0071A` und `E0071E` erreichbar. Die erreichbare Anweisungsfolge endet bei Offset `0x0720`; der direkt analysierte Seed-Kandidat besitzt damit 27 dekodierte Instruktionen und 34 lokale CFG-Kanten. In diesem Seed-Kontrollfluss wurde kein direkter Call beobachtet.

**VERIFIZIERT:** Die einzelne Caller-Instruktion bei `E0098A` ist bytegebunden `calls 0xe006c4`, Länge 4, Bytes `dae0c406`. Die Caller-Analyse endet an dieser Instruktion; Caller-Body und aufgerufene Bodies wurden nicht traversiert.

Die Rizin-Ausgabe nennt Sprungziele als raw offsets. Die zugehörigen Analyseadressen in den Tabellen werden mit der vom Replay angegebenen Basis `E00000` gebildet. Das belegt keine ABI-, SFR-, DPP- oder K-Bus-Semantik. Die Zahlentabelle hält nur dargestellte Operanden und Ziele fest.

## Scope und Eingaben

- Composite: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`
- Größe und SHA-256: `17110` Byte; `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`
- Replay-Bindung: `PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md`, `2169` Byte; SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`
- Der Replay weist Ghidra `12.1.4`, Language `C166:LE:16:default`, Compiler Spec `tasking` und Basis `0xE00000` aus. Diese Ghidra-Analyse wurde für dieses Paket nicht erneut ausgeführt.
- REA-Server/Package: `rea-agents 6.5.0`; REA-Evidence-Bundle-Export und -Import wurden genutzt.
- Rizin: `0.9.1` (`linux-x86-64`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`).
- Bearbeitete Bereiche: Seed `0x06C4..0x07D3` (exklusives Ende `0x07D4`) und genau eine Caller-Instruktion ab `0x098A`. Tatsächlich erreichbare Instruktionen aus dem Seed liegen in `0x06C4..0x071F`.
- Ausgeschlossen: Offset `0x07D4+`, Vorgängerbody ab `E00634`, Caller-Body ab `E00972`, sämtliche Callee-Bodies und Geräte, Netzwerk, VM, Laufzeitattach.

## Methode und Fundstellen

REA wurde zuerst abgefragt. Die erste REA-Session-Inventur meldete keinen offenen Binary-Target und Ghidra `12.1.4` verfügbar. Danach wurden die lokal bereitgestellten Composite- und Replay-Hashes geprüft. Die verwendeten Rizin-Optionen waren:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`1732` dezimal ist Fileoffset `0x06C4`; `pD 92` begrenzt die Ausgabe bytegenau vor Offset `0x0720`. Ergänzende REA/Rizin-Abfragen waren `pd 1 @ 2442` und `ao 1 @ 2442` für ausschließlich Offset `0x098A`; `2442` dezimal ist `0x098A`. Der `ao`-Befund nennt vier Bytes, Instruktionslänge und direktes Ziel. Die erfolgreiche unabhängige CLI-Invocation für den größeren orientierenden Dump verwendete `rizin -q -e scr.color=false -e scr.utf8=false -e io.va=false -a c166 -b 16 -E little -c 'pD 272 @ 1732' <composite>`. Der Dump reichte nur bis `0x07D3`; seine außerhalb des erreichbaren Seed-CFG liegenden Inhalte werden nicht als Findings ausgewertet.

Ein erster CLI-Aufruf mit `-e cfg.bigendian=false` wurde von Rizin mit `ERROR: use -E argument for setting the endianness` beendet. Diese fehlgeschlagene Invocation liefert keine Befunde; der nachfolgende CLI-Aufruf verwendete `-E little`. Die REA-Kommandos liefen erfolgreich mit `e cfg.bigendian=false`. Es wurde kein Netzwerkzugriff, Gerätezugriff oder VM-Lauf ausgeführt.

Bytegebundene REA-Fundstellen:

- `ev_8612fd6da1889049f0d1653f18dd7e62c573c33652a6ba2463cc0f7df2a4daee`: enger Disassembly-Scan, exakt 92 Bytes ab `0x06C4`.
- `ev_e63a44ff3e4572885bdcf2483a44983fd1b432127dcd7bc7c602d187d5c357d1`: genau eine Instruktion an `0x098A`; `calls 0xe006c4`, Bytes `dae0c406`, Größe 4.
- `ev_cb39e4264b31774f580f0e3d602c0d1c1d7554b7167abd9dbdb062916ee7b769`: ergänzende Ein-Instruktions-Disassemblierung bei `0x098A`.
- `ev_638713260f8001f436845f45d25f27ce7416f6d1fdce085b7d57d4dc11bbe72b`: Opcode-Record für `jmpr` bei `0x06CE`, Länge 2, Bytes `2d26`.
- `ev_fb7a391e4ecc8357c1b50797e8eadb29a7024f812dd9f1bdc603af53be56e827`: Opcode-Record für `mov` bei `0x06D0`, Länge 4, Bytes `f6fcbcf1`.
- `ev_229bd975c00fa15d9b352eb924217277fc43a388d35285c428a4e0676f11f607`: explorative Ausgabe für 272 Bytes ab `0x06C4`. **Overscope:** Sie enthält nach den Returns bei `0x071A`/`0x071E` weitere Bytes bis `0x07D3`; diese späteren linearen Dekodierungen sind aus allen Befundtabellen und CFG-Schlüssen ausgeschlossen.

Der Validator deckte während der Tabellenerstellung eine fehlerhafte Byte-/Längenübertragung an der `jmpr`-Instruktion auf; zwei gezielte Opcode-Records bestätigten die korrigierten Instruktionsbytes und -längen. Die ausgegebene Tabelle wurde danach erneut validiert.

Der exportierte kanonische REA-Bundle enthält alle sechs REA-Aufzeichnungen einschließlich der ausdrücklich als Overscope gekennzeichneten explorativen Aufzeichnung. Der REA-Import akzeptierte den Bundle mit `total=6`, `unknowns_added=0`; bereits vorhandene Records wurden zusammengeführt (`imported=0`). Die Befundtabellen verwenden die fünf scope-lokalen Aufzeichnungen; die breite explorative Aufzeichnung ist explizit ausgeschlossen. Im Bundle enthaltene Rohdaten bleiben Analyseartefakte, keine zusätzlichen Scope-Befunde.

## CFG und Calls

`instructions.tsv` bindet für jede der 27 Instruktionen Offset, gemappte Analyseadresse, Bytefolge, Größe, Mnemonic und Operanden an den Composite. `edges.tsv` enthält die 34 aus diesen Instruktionen abgeleiteten Fallthrough-/Taken-Kanten. Die `rets` bei `0x071A` und `0x071E` sind terminal; es gibt von ihnen keine lokale Kante nach `0x0720`. Alle gelisteten bedingten Ziele liegen innerhalb dieses erreichbaren Seed-CFG.

**VERIFIZIERT:** Kein `call`, `calls`, `calla` oder `calli` erscheint in den vom Seed erreichbaren 27 Instruktionen. Die separate Caller-Zeile in `calls.tsv` ist die einzige externe Call-Beobachtung dieses Pakets. Der Rizin-Decoder bezeichnet sie als `calls`, mit Ziel `0x00e006c4`. Das Paket analysiert den Zielbody nicht zusätzlich.

## Numerische Referenzen

`references.tsv` verzeichnet alle hier beobachteten zahlenhaltigen Operanden des erreichbaren Codes, jeweils mit Quellinstruktion und deren Composite-Bytes: raw-addressartige Operanden `0xfe06:0x31bc` (Offsets `0x06C4`, `0x06D0`), `0xfe06:0x30bc` (acht Instruktionen von `0x06D4` bis `0x0710`), `0xf1bc.15` (`0x06F6`), Immediate `0x03ff`, `1`, `0x04`, `0x00`, die Bitzahl `7` sowie die bedingten Branch-Ziele. Diese Oberflächenwerte werden nicht als SFRs, Registerlayout, Speichersemantik oder ABI interpretiert.

## Status, Alternativen und Restunsicherheit

- Byte-/Offset-/Adressbindung: **VERIFIZIERT**; Validator: **PASS**.
- Lokale bedingte CFG-Kanten und terminal dekodierte `rets`: **VERIFIZIERT** als statische Rizin-Ableitung; Validator: **PASS**.
- Caller-Bytes und direktes Ziel: **VERIFIZIERT**; Validator: **PASS**.
- Numerische Operandenerfassung: **VERIFIZIERT** als Rizin-Oberflächendarstellung mit Quellbytebindung; Validator: **PASS**.
- Export/Import des REA-Bundles: **PASS**.
- Ghidra: **NOT_RUN**. Der enge Scan und `ao` lieferten die benötigten Bytes, Instruktionslängen, Branch-Ziele und Call-Ziel; es blieb keine scope-lokale Lücke, die einen weiteren Whole-Program-Importer rechtfertigt.
- Rückkehrgrenze/Funktionsbesitz: **HYPOTHESE** nur hinsichtlich der Zuordnung als Seed-Kandidat. Die Bytes belegen erreichbare Rückkehrinstruktionen, beweisen jedoch nicht unabhängig die Ghidra-Funktionszuordnung oder eine Quellfunktionsgrenze.
- Semantik der Operanden, Laufzeitverhalten, indirekte Kontrollflüsse außerhalb der sichtbaren Instruktionen und Gerätewirkung: **OFFEN**. Es wurden keine nicht kodierten Semantiken ergänzt.

Alternative Erklärung: Die linearen Bytes ab `0x0720` können nach einem Seed-Return eine benachbarte Routine oder Daten enthalten. Die explorative Ausgabe ist für diese Einordnung kein Beweis; solche Bytes wurden nicht in den Seed-CFG aufgenommen. Eine andere Funktionsbesitz-Zuordnung ändert nicht die hier bytegebunden beobachteten Branch-Ziele und Return-Bytes, begrenzt aber Aussagen über Funktionsgrenzen.

## Dateien und Integritätsprüfung

- `instructions.tsv`, `edges.tsv`, `calls.tsv`, `references.tsv`: bytegebundene Tabellen.
- `validate.py`: prüft Eingabehash/-größe, Instruktionsbytes, Offsets/Analyseadressen, zusammenhängende Instruktionsspanne, CFG-Kanten, Caller-Instruktion, Referenzquellen/-operanden und Scope.
- `rea-evidence-bundle.json`: kanonischer REA-Export, erfolgreich importiert.
- `SHA256SUMS`: SHA-256 aller oben genannten Ausgabedateien außer dem Manifest selbst.

Die SHA-256 jedes Paketinhalts ist in `SHA256SUMS` aufgeführt. Prüfergebnis nach Ausführung: dokumentiert in der SHA-256-Prüfung und im Validator-Status dieses Reports.
