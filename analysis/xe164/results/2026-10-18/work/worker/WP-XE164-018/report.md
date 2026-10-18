> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-018 — Seed E00972: lokaler CFG-Befund

## Ergebnis

VERIFIZIERT: Die statisch dekodierte lokale Instruktionsfolge beginnt bei Dateioffset 0x0972 (Analyseadresse E00972) und endet mit `RETS` bei Dateioffset 0x0ACA (E00ACA). Der letzte Instruktionsbyte liegt bei 0x0ACB. Die beobachtete Returngrenze liegt damit innerhalb des erlaubten Bereichs `0x0972..0x0ACB`. Lokale Sprungziele verbleiben in diesem Bereich. Alle direkten Calls führen aus dem Bereich; nur Callsite und Zielwert sind erfasst, kein Callee-Body wurde traversiert.

Der lokale Kontrollfluss hat konditionale Abzweige zum gemeinsamen Pfad E00AC2/E00AC6 sowie Rückwärtsschleifen bei E009D8, E00A0E und E00A8C. Alle Instruktionen, Kanten, direkten Calls und Zahlenreferenzen sind in den TSV-Dateien aufgeführt. Es werden keine DPP/SFR/ABI/K-Bus-Semantiken behauptet.

## Beobachtungen und Fundstellen

- Eingabe: `XE164-composite-e00000.bin`, 17,110 Byte, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` (PASS: Hash stimmt mit Vorgabe überein).
- Einzelne Caller-Instruktion am Offset 0x04D4 / E004D4: Bytes `dae07209`, `calls 0xe00972`; direktes Ziel E00972. Caller-Body nicht analysiert.
- Seed-Instruktion bei Offset 0x0972 / E00972: Bytes `8880`, `mov [-r0], r8`.
- Return bei Offset 0x0ACA / E00ACA: Bytes `db00`, `rets`.
- Caller-Bytes und sämtliche Seed-Instruktionsbytes werden vom Validator direkt gegen den Composite gebunden.

## Methode und Werkzeugprofil

REA zuerst: `open_binary` lehnte das headerlose C166-Composite mit `unsupported binary format` ab. Diese konkrete Formatlücke erforderte Rizin. REA `execute_rizin_command` funktionierte mit Argumenten `-N -q -c` und folgendem Kommando:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Für den Caller wurde dasselbe Profil und `pd 1 @ 0x04d4` verwendet. Rizin-Version: `0.9.1 @ linux-x86-64`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. Rizin-Adressen entsprechen Dateioffsets; Analyseadressen sind Offset + Basis E00000. Das REA-Evidence-Bundle stammt aus `export_evidence_bundle`.

## Evidenzgrenze und Overscope

Akzeptierte Evidenz: gebundener Composite-Hash, REA-Rizin-Disassembly der Offsets 0x0972..0x0ACB, genau eine Caller-Instruktion bei 0x04D4, daraus mechanisch erstellte Tabellen sowie erfolgreiche Byte- und Konsistenzvalidierung. Explorative Befunde, die nicht als Codeevidenz akzeptiert werden: REA-`open_binary` meldete `unsupported binary format`; ein separater Rizin-`?V`-Probeversuch endete mit Parserfehler, bevor die angehängte Disassembly lief. Die bestätigte Versionsabfrage erfolgte separat mit `rizin -v`. Kein Ghidra-Fallback wurde ausgeführt. Außerhalb des Seedbereichs wurde kein Byte disassembliert. Beim Caller wurde nur die eine erlaubte Instruktion betrachtet. E00ACC/E00B42-Bereiche, Rest des Caller-Bodys und alle Callee-Bodies sind ausdrücklich ausgeschlossen.

## Status, Alternativerklärung und Restunsicherheit

- Befundstatus: VERIFIZIERT für Instruktionsfolge, lokale direkte Sprungziele, direkte Calls, Zahlenoperandliterale und Bytebindung.
- Teststatus: PASS für Composite-Hash, Instruktionsgrenzen/-bytes, Caller-Bindung und Tabellenkonsistenz, einschließlich Abgleich aller Instruktionszeilen mit dem REA-Bundle; PASS für `sha256sum -c SHA256SUMS`. Das Bundle ist JSON-lesbar und seine Artefaktidentität wird geprüft. Der REA-Import wurde NOT_RUN, weil `import_evidence_bundle` den persistenten REA-Evidenzbestand zusammenführt und damit außerhalb des vorgegebenen Worker-Ausgabebereichs schreiben würde.
- Alternative: Ein anderer Einstieg oder andere Laufzeitbedingungen könnten andere Pfade auslösen. Der CFG beschreibt nur im gewählten C166-Profil statisch von E00972 erreichbare Kanten; Laufzeitverhalten wird nicht behauptet.
- Restunsicherheit: REA-Evidence weist keinen Profil-Digest aus; Version und Kommando sind daher im Bericht fixiert. Disassembly bleibt Werkzeugableitung, kein Originalquelltext. Decoderfehler oder ein anderes ISA-Profil sind durch diese Probe nicht ausgeschlossen.
- Bundle-Importstatus: NOT_RUN; kanonischer Export und lokale JSON-/Inhaltsvalidierung PASS. Der Import-API-Schreibeffekt würde einen ausgeschlossenen gemeinsamen Evidenzspeicher verändern.

## Ausgabedateien

- `report.md`
- `instructions.tsv`
- `edges.tsv`
- `calls.tsv`
- `references.tsv`
- `validate.py`
- `rea-evidence-bundle.json` (kanonischer REA-Export, 39,455 Bytes, 5 Records)
- `SHA256SUMS` (Ergebnisdateien außer dem Manifest selbst)
