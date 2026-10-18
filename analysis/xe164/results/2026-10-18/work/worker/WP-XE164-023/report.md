> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-023 — E00888 lokale CFG und numerische Referenzen

## Ergebnis

**VERIFIZIERT** — Unter angenommener Analysebasis `E00000` ist der Seed `E00888` ab Datei-Offset `0x0888` als 20 Instruktionen bis `0x08C1` inklusive dekodiert. Der letzte Befehl beginnt bei `E008C0` und ist `RETS` (`db00`); seine zwei Bytes enden genau bei `0x08C2`. Damit ist eine lokale Returngrenze innerhalb der untersuchten Grenze belegt. Die statische CFG enthält 21 Kanten: 15 unbedingte sequenzielle Fall-through-Kanten sowie Taken-/Not-taken-Kanten an drei bedingten Verzweigungen. Alle Ziele liegen innerhalb des Seedbereichs. Beide lokalen terminalen Pfade enden bei `RETS` in `E008BC` oder `E008C0`; kein beobachteter Pfad verlässt den Bereich.

Im erlaubten Caller-Snapshot ist die einzelne Instruktion bei Datei-Offset `0x0AAE` als `CALLS E00888` belegt. Ihre vier Bytes sind `dae08808`. Es wurden keine Callee-Bodies verfolgt. Im Bereich `E00888..E008C1` wurden keine direkten Calls dekodiert.

`references.tsv` enthält 26 byte- und instruktionsgebundene numerische Operanden: unmittelbare Werte, numerische Adressausdrücke, Bitindizes und die Ziele der drei bedingten Sprünge. Dies sind syntaktische Referenzen ohne Zuschreibung von DPP-, SFR-, ABI-, K-Bus- oder Hardwarebedeutung.

## Eingaben und Methode

- Composite `DERIVED-XE164-COMPOSITE-E00000`, 17 110 Bytes; SHA-256 erwartet und geprüft: `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` (**PASS**).
- Replay `composite-replay.md`, 2 169 Bytes; SHA-256 erwartet und geprüft: `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5` (**PASS**). Daraus wurde nur die Basisbeziehung Analyseadresse `E00000 + Datei-Offset` übernommen.
- Primärwerkzeug: REA `execute_rizin_command`, Provider `Rizin`; der von REA ausgegebene Provider-Versionswert ist `null`. Ein zusätzlicher CLI-Versionsnachweis wurde nicht erhoben.
- Exakt bestätigte Einstellungen in jeder akzeptierten Rizin-Aufrufgruppe: `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`; Rizin-Wrapperargumente `-N -q`. Bereichsbefehl: `pD 0x3a @ 0x888`, begrenzt auf genau 58 Bytes von `0x0888` bis `0x08C1`. Die rohe Byteansicht nutzte `px 0x3a @ 0x888` über denselben Bereich.
- Caller: `pd 1 @ 0xaae`, dazu `p8 4 @ 0xaae`; letzterer lieferte genau die vier Instruktionsbytes. Keine Folgeinstruktion wurde dekodiert.
- Akzeptierte REA-Evidence: `ev_7dd990c58e8fadb72510ccc4265fd7926f4b0695cc6727ec105d76f5ab7be2e4` (begrenzte Disassemblierung), `ev_c6abc90a1b5eda2456e4bba213d24342849a204a290d6f7830170f5c4cfd04b0` (begrenzte Rohbytes), `ev_1257a81c7557b1ce233eb2601e482de5ac048665c1db7af476b8b4119bfe9927` (ein Caller-Befehl), `ev_8107e4f0665c72d1421fdcb37f2e288b49489fa2605c7b500320a1604869051e` (genau vier Callerbytes). Das Profil wurde von Rizin in jedem Aufruf in der Ausgabe als `c166 / 16 / false / false` bestätigt.
- REA-Bundle: mit `export_evidence_bundle` kanonisch erzeugt, nicht handgefertigt. Umfang beim Export: 5 Records, 0 Unknowns. Darin ist ein explorativer Aufruf mit einer auf sechs Bytes dimensionierten Caller-Byteansicht enthalten. Die zwei Bytes hinter dem erlaubten Caller-Befehl sind **Overscope**, separat ausgeschlossen und keine Grundlage für Tabellen oder Befunde; die akzeptierte Caller-Byteansicht ist allein das exakte Vier-Byte-Record `ev_8107…`.
- Ghidra-Fallback war nicht erforderlich: Der Rizin-C166-Decoder lieferte gültige Instruktionen und exakte Bytes innerhalb des begrenzten Bereichs.

## Fundstellen, Status und Scope

- `instructions.tsv`: alle 20 linearen Instruktionsbytes, -adressen und Decoder-Mnemonics. Jeder Eintrag ist gegen die Quelldatei geprüft (**VERIFIZIERT**).
- `edges.tsv`: lokale Fall-through- und bedingte Kanten, mit getrennten Taken-/Not-taken-Kanten (**VERIFIZIERT**).
- `calls.tsv`: ausschließlich die freigegebene Caller-Instruktion (**VERIFIZIERT**).
- `references.tsv`: 26 syntaktische numerische Operanden, an Instruktionsadresse und Operand gebunden (**VERIFIZIERT**).
- `validate.py`: prüft Eingabehash, Instruktionsbytes/-längen/-adressen, lückenlose Bereichsabdeckung, CFG-Endpunkte und Kanten, Returngrenzen, Callsitebytes/-target sowie Operandbindungen.
- Analyseende: vor Byte-Offset `0x08C2`. Offset `0x08C2` und spätere Bytes wurden nicht dekodiert. `E00808`, `E008C2`, Caller-Body `E00972` und Callee-Bodies sind ausgeschlossen.

## Alternative und Restunsicherheit

Die CFG gilt für den beobachteten C166-Decoder und die angenommene Ladebasis `E00000`; die Replay-Notiz stützt diese Adresse-Offset-Abbildung, während die Tabellen Roh-Offsets und Bytes separat binden. Eine andere Ladebasis verschöbe Analyseadressen, nicht Roh-Offsets. Die Darstellung belegt statische Decoder- und Kontrollflussbeziehungen, keine Ausführung oder Bedingungswerte. Die numerischen Werte haben keine hier belegte DPP-/SFR-, Registerbank-, Calling-Convention-, K-Bus- oder Hardwaresemantik. REA attestierte keine konkrete Rizin-Version; daher bleibt die Toolversion **OFFEN**. Es wird keine ABI- oder Laufzeitvollständigkeit behauptet.

## Prüfstatus

- Composite-/Replay-Hashes: **PASS**.
- Tabellenvalidator: **PASS** — 20 Instruktionen, volle Abdeckung `0x0888..0x08C1`, 21 lokale Kanten, 2 Returngrenzen, 1 Caller-Instruktion und 26 numerische Operandbindungen geprüft.
- Kanonischer Bundle-Export: **PASS** — REA erzeugte 5 Evidence-Records, 0 Unknowns.
- Bundle-Importprüfung: **PASS** — REA validierte das exportierte Bundle (`imported=0`, `total=5`, `unknowns_added=0`); die Records waren bereits vorhanden.
- Self-review: durchgeführt. Kein unabhängiger Worker-Review oder Lauf beansprucht.

Alle Statusvokabeln folgen `VERIFIZIERT | HYPOTHESE | OFFEN | BLOCKED`; Teststatus `PASS | FAIL | NOT_RUN | BLOCKED`.

## Dateien

`instructions.tsv`, `edges.tsv`, `calls.tsv`, `references.tsv`, `validate.py`, `report.md`, `rea-evidence-bundle.json`, `SHA256SUMS`.
