> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-024 — lokaler CFG- und Referenzbefund

## Ergebnis

Unter der vorgegebenen Zuordnung Dateioffset 0 ↔ E00000 ist für den Seed E008C2 eine zusammenhängende lokale Instruktionsfolge bis einschließlich E00925 (letzte Instruktion ab E00924) beobachtet. Zwei RETS-Instruktionen liegen bei E00912 und E00924. Innerhalb der Grenze ist damit eine explizite Rückkehrinstruktion belegt; Aussagen über weitere Caller oder ein darüber hinausgehendes Funktionsende werden nicht abgeleitet.

Statische bedingte Kanten und Call-Kanten sind in [edges.tsv](edges.tsv) festgehalten. Der direkte Call bei E008E0 zielt auf E00926, exakt auf die ausgeschlossene Grenze; sein Body wurde nicht analysiert. Die einzige zusätzlich gelesene Caller-Instruktion ist E00ABA: calls E008C2, Bytes da e0 c2 08 am Dateioffset 0x0aba.

## CFG-Beobachtung

Die sequentiell dekodierten Instruktionen decken Dateioffsets 0x08c2..0x0925 lückenlos ab. Bedingte Kanten sind Rizin jump/fail-Felder mit unter der angenommenen Basis addierten Analyseadressen. Callsites und Returns sind separat als Kanten erfasst. Die Fallthrough-Kante nach calls ist der im Decoder ausgewiesene Fortsetzungspunkt; sie belegt keine Ausführung des Callee-Bodys.

Numerische Operanden und Ziele sind in [references.tsv](references.tsv) bytegebunden aufgeführt. Die Paare 0xfe06:0x2a26 und 0xfe06:0x2a2c bleiben opak; es wird keine DPP-, SFR-, ABI- oder K-Bus-Bedeutung behauptet. Pseudocode wurde nicht erzeugt. Eine etwaige strukturierende Lesart wäre Werkzeugableitung, keine unabhängige Semantik.

## Methode und Inputbindung

- Artifact DERIVED-XE164-COMPOSITE-E00000, 17110 Bytes, SHA-256 5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983.
- Replay-Hinweis composite-replay.md, 2169 Bytes, SHA-256 842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5.
- REA zuerst: open_binary erkannte das headerlose Composite als nicht unterstütztes Format. Danach lieferte REA execute_rizin_command zwei erfolgreiche, unveränderte Artefaktbeobachtungen. Deren Evidence-IDs stehen im kanonischen Bundle.
- Dekodierprofil: raw file offsets, asm.arch=c166, asm.bits=16, cfg.bigendian=false, io.va=false; Adressabbildung analysis_address = 0x00e00000 + file_offset. Die vollständige Instruktionsabfrage dekodierte exakt 37 Instruktionen ab Offset 0x08c2 und genau eine Instruktion am Caller-Offset 0x0aba.
- Lokale CLI-Version: Rizin 0.9.1 (rizin -v). REA protokolliert den aus seiner Umgebung eingesetzten Rizin-Build nicht zuverlässig; daher ist dessen genaue Version OFFEN. Die aufgerufenen Kommandos stehen im kanonischen Bundle.

## Status und Restunsicherheit

- VERIFIZIERT — Bytewerte, Offsets, Instruktionstexte, direkte Sprungziele, Call-Ziele und Decoder jump/fail-Kanten in diesem begrenzten Bereich.
- HYPOTHESE — keine funktionale Hypothese benötigt; Seed E008C2 und Basisabbildung E00000 sind Vorgaben der Aufgabe.
- OFFEN — Rizin-Buildversion innerhalb REA; unabhängige Zweitdekodierung; Semantik numerischer Paare/Bitzugriffe; ob der Aufruf bei E008E0 dynamisch erreicht wird; Verhalten jenseits der Bereichsgrenze.
- BLOCKED — nichts für diese begrenzte statische Ausgabe. Die abgelehnte REA-Headererkennung verhinderte nicht die anschließende raw-offset Rizin-Beobachtung.

Alternative Deutung der 0xfe06:...-Operanden wurde nicht vorgenommen, weil diese Semantik ausdrücklich ausgeschlossen ist. Caller-Body, Callee-Body E00926, Seed E00888, Bereich ab E00926 sowie der separate Bereich bei E00972 sind nicht analysiert.

validate.py bindet Inputhash, Größe, Zeilenoffsets, Bytes, dekodierte Größen, Adressabbildung, CFG-Kanten, Calls, numerische Referenzen und Caller-Bytefolge. SHA256SUMS enthält die ausgegebenen Dateihashes; eigene Prüfung ist Self-Review. Keine unabhängige Review oder Worker-Ausführung wird behauptet.
