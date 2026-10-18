> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-025 — lokale statische Analyse ab E00926

## Ergebnis

Unter der angenommenen Abbildung Fileoffset `0x0000` → Analyseadresse `E00000` ist der lineare Instruktionsbereich `E00926` bis einschließlich `E00971` vollständig durch Rizin dekodiert. Die Instruktionen enden genau mit `rets` bei `E00970`; dessen zweites Byte liegt bei `E00971`. Alle erkannten bedingten Sprünge bleiben im Bereich. Die statische CFG hat zwei Return-Senken (`E0096C`, `E00970`). Im Seed-Bereich gibt es keinen direkten Call. Die einzige hier untersuchte Caller-Instruktion bei Fileoffset `0x07F4` ist ein bytegebundener `calls E00926`.

Das ist ein lokaler statischer Befund, keine Aussage zu Laufzeitverhalten oder zur Bedeutung der Operanden. Der Ausschnitt belegt nicht, dass `E00926` die vollständige Compiler-Funktion ist; er belegt die Returngrenze der ab dem Seed erreichbaren dargestellten Pfade innerhalb dieses begrenzten Bereichs.

## Beobachtungen und Fundstellen

- Eingabe `DERIVED-XE164-COMPOSITE-E00000`: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`, 17 110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Replay-Referenz `PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md`, 2 169 Bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`.
- REA 6.5.0 (`execute_rizin_command`), Rizin 0.9.1, Linux x86-64. REA startete `rizin -N -q -c <command> <artifact>`; `-N` unterdrückt Nutzereinstellungen und Skripte. Konkretes Instruktionsprofil in jedem Disassembly-Aufruf: `e asm.arch=c166; e asm.bits=16; e cfg.bigendian=false; e io.va=false`. Ein separater REA-Befehl las die wirksamen Werte zurück: `c166`, `16`, `false`, `false`. Rizin-Werte/Bytefolgen sind Werkzeugbeobachtungen; die Abbildung auf `E0xxxx` addiert die vorgegebene Basis `E00000` zu den Fileoffsets.
- Der Seed-Bereich wurde in begrenzten Batches gelesen: `aoj 16 @ 0x0926` (endet bei Offset `0x095D`) und `aoj 7 @ 0x095E` (endet bei Offset `0x0971`). Die 23 Zeilen in [instructions.tsv](instructions.tsv) enthalten alle beobachteten Bytefolgen, Instruktionsgrößen und die abgeleiteten Analyseadressen. [edges.tsv](edges.tsv) enthält bedingte und lineare Kanten.
- Die exakt eine Caller-Instruktion wurde unabhängig bytegebunden bei Offset `0x07F4` mit `aoj 1` gelesen: Bytes `da e0 26 09`, Größe 4, `calls 0xe00926`. Dieser Callsite entspricht der zuvor bekannten Referenz E-XE164-031; kein Caller-Body wurde analysiert.
- Direkte Zahlenoperanden sind in [references.tsv](references.tsv) wörtlich erfasst: relative Sprungziele, `0xfe06:0x31be`, `0xfe06:0x30bc`, `0xf1be.15` sowie Immediate-Werte. Die beiden `0xfe06:...`-Operanden und `0xf1be.15` bleiben uninterpretierte numerische Operanden; daraus wird keine DPP-, SFR-, ABI- oder Hardwaresemantik abgeleitet.
- In [calls.tsv](calls.tsv) ist der eine außerhalb des Bereichs erlaubte Callsite festgehalten. Im Seed-Bereich selbst meldet Rizin keinen `call`-Typ. Direkte Calls wurden nicht traversiert; keine Callee-Bodies wurden geöffnet.
- Die REA-Beobachtungen sind im kanonischen [REA Evidence Bundle](rea-evidence-bundle.json) exportiert. Die darin enthaltene REA-Ausgabe nennt als Einschränkung, dass Version/Formaterkennung nicht zuverlässig probiert wurde; die Rizin-Version 0.9.1 stammt aus einer lokalen `rizin -v`-Abfrage. Der Validator bindet Eingabedigest, Tabellenbytes, Offset/Adressabbildung, Kanten, Caller und Referenzen.

## CFG-Zusammenfassung

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Die Kanten sind aus Rizin-Branch- und Fallthrough-Adressen abgeleitet; sie beweisen keine Pfadbedingungen über den dargestellten Maschinencode hinaus.

## Bereichsschutz und Restunsicherheit

Ein anfänglicher Darstellungsaufruf `pd 8 @ 0x095e` gab zusätzlich eine Instruktion bei `0x0972` aus und las somit über die Grenze hinaus. Diese Werkzeugausgabe ist als Overscope isoliert; die dortigen Bytes und Instruktion werden nicht ausgewertet, zitiert oder in Befundtabellen aufgenommen. Die beschränkte Folgeabfrage `aoj 7 @ 0x095e` deckt exakt bis einschließlich `0x0971` ab. Im Bundle bleibt der ursprüngliche Overscope-Aufruf als Werkzeugbeobachtung sichtbar, nicht als Befund. Die übrigen Analyseschritte halten die Bereichsgrenze ein.

`extr #1` bei `E0094E` hat in Rizin `type: "unk"`; seine dekodierte Größe und der nachfolgende Fallthrough sind beobachtet, aber sein semantischer Effekt bleibt offen. Der hier relevante CFG-Transfer wird durch die nachfolgenden Sprung- und Return-Instruktionen bestimmt. Es wurde keine unabhängige Ghidra-Funktionsanalyse ergänzt: nach Vorliegen der bytegebundenen Branches und der abschließenden Return-Instruktion blieb keine konkrete Lücke in der gestellten lokalen Frage. Rizin übernimmt keine Garantie für ABI- oder Funktionsgrenzen.

Statusvokabular: **VERIFIZIERT** = durch die hier genannten Bytes/Werkzeugbeobachtungen belegt; **HYPOTHESE** = abgeleitete, nicht direkt beobachtete Deutung; **OFFEN** = mit dieser Eingrenzung nicht bestimmt; **BLOCKED** = Prüfung mangels Voraussetzung gestoppt. Status der lokalen CFG, ihrer Sprungziele, der Caller-Bytes und Returngrenze: **VERIFIZIERT**. Bedeutung der numerischen Operanden und Semantik von `extr`: **OFFEN**. Kein hardware- oder runtimebezogener Status wird beansprucht.

## Self-Review und Prüfergebnis

Self-Review (keine unabhängige Prüfung): Tabellenadressen und Bytefolgen gegen das Eingabeartefakt verglichen; der Validator erzwingt lückenlose Abdeckung der erlaubten Instruktionsbytes `0x0926..0x0971`, prüft alle Tabellenreferenzen und weist jeden Eintrag außerhalb des Seed-Bereichs als ausschließlich den Caller bei `0x07F4` aus. SHA-256-Digests der Ausgabedateien stehen in `SHA256SUMS`.
