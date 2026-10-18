> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-017 — E00ACC lokale CFG und Referenzen

## Ergebnis

**VERIFIZIERT** — Im begrenzten Seedbereich liegt eine linear dekodierte C166-Sequenz von Datei-/Roh-Offset `0x0ACC` bis einschließlich `0x0B41`. Der letzte Befehl beginnt bei `0x0B40` (`RETS`, Bytes `db00`); damit ist im untersuchten lokalen Pfad eine Returngrenze vor `0x0B42` belegt. Der Pfad enthält 32 Instruktionen, 31 sequentielle Fall-through-Kanten, keine lokalen Sprunginstruktionen und keine direkten Calls. Das ist die vollständige statisch erreichbare Sequenz ab dem durch den Caller belegten Entry `E00ACC` innerhalb der Grenze.

Die einzelne erlaubte Caller-Instruktion bei Datei-Offset `0x04D0` ist bytegebunden als `CALLS E00ACC` (`dae0cc0a`) verifiziert. Caller-Inhalt vor oder nach dieser Instruktion wurde nicht untersucht.

Die numerischen Operanden stehen unverändert und ohne Semantikzuschreibung in `references.tsv`: darunter C166-Segment:Offset-Ausdrücke und unmittelbare Konstanten/Masken. Das sind syntaktische numerische Referenzen, keine Behauptungen über DPP, SFR, ABI, K-Bus oder Hardwarefunktion.

## Eingabe und Methode

- Composite: `DERIVED-XE164-COMPOSITE-E00000`, 17 110 Bytes.
- Erwarteter und beobachteter SHA-256: `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` (**PASS**).
- Replay-Hinweis: `composite-replay.md`, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`; daraus wurde nur die bestätigte Basisbeziehung Analyseadresse `E00000 + Datei-Offset` übernommen.
- Primärwerkzeug: REA `execute_rizin_command`; lokaler Rizin-CLI-Versionsaufruf meldete `0.9.1` (Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`). REA selbst meldete Provider `Rizin`, Provider-Version und Analysis-Profile jedoch `null`; daher ist die Zuordnung dieser separat gelesenen Version zum REA-Prozess nicht eigenständig belegt.
- Exakte Befehlsprofileinstellungen für akzeptierte Disassemblierung: `e scr.color=0; e asm.arch=c166; e asm.bits=16; e cfg.bigendian=false; e io.va=false; e asm.bytes=true`; danach `pd 1 @ 0x4d0; pD 118 @ 0xacc`. Ein eigener Konfigurationsabruf bestätigte `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`. `-N -q` wurden vom REA-Rizin-Wrapper übergeben.
- Korrektur des Capability-Vorchecks: Eine anfängliche Filterung von `rizin -L` ergab keinen C166-Treffer, war aber kein belastbarer Beleg fehlender Architekturunterstützung. Der direkte Test mit `asm.arch=c166` gelang; deshalb war kein Ghidra-Fallback erforderlich.
- Fundstellen der akzeptierten Evidence: REA IDs `ev_3073753611e47c8e1683a34d2ac661658c8b08b2aac9caf25b73b0e47be2b550` (Caller + Bereich), `ev_8c11a1a184f25e79ecc24fdb01c0994ec59c9a975f5481565fb3e4eb30a1cdbf` (Instruktionsbytes), `ev_ec019bf73c4ed99fd1e30656df4285ce33f3771330054daa1070478b812a6bfe` (Profilbestätigung). Bundle: `rea-evidence-bundle.json`.

Kein Ghidra-Fallback war erforderlich: Rizin lieferte eine gültige C166-Disassemblierung im exakten Offsetprofil. Es wurden keine Callee-Bodies verfolgt.

## Overscope und Evidenztrennung

Ein explorativer REA-Aufruf nach `list_documents` (kein Binary war offen) verwendete `execute_rizin_command` direkt. Ein Folgeaufruf setzte keine flüchtigen Decoderoptionen erneut und lief daher im Rizin-Standardprofil `x86/64`, `io.va=true`; dessen Ausgabe zeigte fehlerhafte x86-Decodierung und ging außerdem über die zulässige Grenze hinaus. Ein danach falsch dimensionierter Aufruf verwendete 1142 statt 118 Bytes und gab ebenfalls Daten jenseits `0x0B41` aus. Diese beiden Ausgaben sind **explorativer Overscope**, nicht akzeptierte Evidenz, nicht Grundlage der Tabellen und nicht als CFG-Befund gewertet. Die Overscope-Records bleiben als transparentes Auditmaterial im kanonischen REA-Bundle enthalten. Die akzeptierten Tabellen beruhen ausschließlich auf den späteren, explizit konfigurierten Aufrufen mit `pD 118 @ 0xacc` und dem einzelnen `pd 1 @ 0x4d0`.

## Tabellen und Grenzen

- `instructions.tsv`: alle 32 linear dekodierten Instruktionen; jede Bytefolge ist gegen den Composite validiert.
- `edges.tsv`: 31 sequentielle Fall-through-Kanten innerhalb des Seeds. `RETS` ist der lokale Abschluss; Rücksprungziel/Caller-Nachlauf wurde nicht verfolgt.
- `calls.tsv`: nur die freigegebene Caller-Instruktion. Im Seed selbst wurden keine direkten Calls beobachtet.
- `references.tsv`: 32 syntaktische numerische Operandfundstellen, jeweils an Instruktion und Operand gebunden.
- `validate.py`: prüft Eingabehash, Instruktionsbytes, Bereichsvollständigkeit, Basis-/Adressbindung, CFG-Tabellenkonsistenz, Caller-Bytes und -Ziel sowie Bindungen aller numerischen Referenzen.

## Alternativerklärung und Restunsicherheit

Die Auswertung belegt den statischen Kontrollfluss nur unter der Analysebasis `E00000` und dem direkten Caller-Target `E00ACC`. Eine andere Ladebasis würde die Analyseadressen verschieben; die Roh-Offsets und Bytes blieben gleich. Rizin-Version/Profil-Metadaten des REA-Prozesses sind nicht vollständig attestiert, weshalb die verwendete lokale CLI-Version ergänzende, nicht vollständig gebundene Umgebungsinformation ist. Der Nachweis sagt nichts über die Bedeutung der numerischen Operanden oder über Laufzeitwirkung, aufrufseitigen Zustand, Flags/Seiteneffekte oder Zielhardware aus.

## Prüfstatus

- Eingabehash: **PASS**.
- Akzeptierte Byte-/Disassemblierungsbindung und lokale Returngrenze: **PASS**.
- Tabellenvalidator: **PASS** — 32 Instruktionsbytes/-adressen, vollständige Bereichsabdeckung, 31 CFG-Kanten, Caller-Bytes/Ziel und 32 Operandbindungen geprüft.
- Bundle-Erzeugung: REA `export_evidence_bundle`, kanonisch erzeugt, keine handgefertigte Importbundle-JSON.
- Bundle-Importprüfung: **PASS** — REA `import_evidence_bundle` validierte das exportierte Bundle (`imported=0`, `total=7`, `unknowns_added=0`); vorhandene Evidence-Records wurden nicht dupliziert.
- Self-review: durchgeführt; kein unabhängiger Worker-Review behauptet.

## Dateien

`instructions.tsv`, `edges.tsv`, `calls.tsv`, `references.tsv`, `validate.py`, `report.md`, `rea-evidence-bundle.json`, `SHA256SUMS`.

| Datei | SHA-256 |
|---|---|
| `instructions.tsv` | `1b9d1ff0b75e2b01c1ebc8424ca89d1a31f7b015ff988bc38a2699177b669d53` |
| `edges.tsv` | `fae05b09e4fcbcd64029f4c14d7027e2e39c32a3a1276ecdd40cd7793c8341d7` |
| `calls.tsv` | `f1709627e7ab09daf522404ef8079a9904bd0e7ce7ea005642770035655d10cc` |
| `references.tsv` | `581b8a130ecb7295f51b7eccf0f496ab59f3c41da2a8ea1fbf68f05cdd2cf236` |
| `validate.py` | `e409e2948e0c5b93f0a50d2cec20748fd5f7bf160cb63646bf2253c8bac8309d` |
| `rea-evidence-bundle.json` | `ced7b00a91376145c7baecdd9781315e692bf26ad11dbf3c4588ccd3302970b9` |

`SHA256SUMS` enthält außerdem den Hash dieses Berichts. Der Selbsthash von `SHA256SUMS` ist nicht in sich selbst enthalten.
