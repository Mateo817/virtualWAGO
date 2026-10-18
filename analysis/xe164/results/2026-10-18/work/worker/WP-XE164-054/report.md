> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-054 — Direktaufrufe nach E0355C

## Befund

**VERIFIZIERT, begrenzte Kodierungsform:** Im Composite gibt es im vollständigen Dateibereich `0x0000..0x42D5` keine Bytefolge `DA E0 5C 35`. Das ist genau die direkte C166-Call-Kodierung, die aus dem bytegebunden neu dekodierten Vergleichs-Call an `0x3692` abgeleitet wird. Daher ist kein Treffer und keine Callstelle für diese Kodierungsform vorhanden.

Die Referenzstelle `0x3692` enthält `DA E0 28 35`; Rizin dekodiert vier Bytes dort als `calls 0xe03528` (Evidence `ev_8845fae468d01e0a94d15ba6fd5a027b6e1fa7b4c5a7dddfd72ade04a880c422`). Die Zieladresse entspricht nicht E0355C und dient allein zur Bindung der unmittelbaren Call-Kodierung. Unter der aus dem benachbarten Composite abgeleiteten syntaktischen Basis `E00000 + Dateioffset` ist die Referenzstelle E03692.

Die reproduzierbare Tabelle `candidates.tsv` enthält die vollständige Negativsuche und die Referenzdekodierung. `validate.py` prüft Größe, Hash, Bereich, bytegenaue Suche und Decoder-Evidence.

## Eingabebindung und Methode

- **PASS:** 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- **REA zuerst:** `open_binary` wurde als erster Schritt auf das exakte Composite angewendet.
- **Benannter Fallback:** REA `execute_rizin_command`, Rizin C166-Decoder mit `e io.va=false; e asm.arch=c166; e asm.bits=16; e cfg.bigendian=false`. Die Ausführung an Offset `0x3692` liefert vier Bytes `dae02835`, Typ `call`, Mnemonik `calls 0xe03528`. Rizin meldet keine verlässliche Versionsnummer (`null`).
- **Vollständigkeit:** Python-Validator untersucht alle Startpositionen, an denen vier Bytes im inklusiven Bereich `0x0000..0x42D5` liegen, auf exakt `dae05c35`; Trefferzahl `0`.
- Die Rizin-Referenzdekodierung ist im kanonischen finding-only Bundle enthalten. Rizin-CLI-Evidence bindet den Composite-Digest vor/nach dem Aufruf und meldet keine Artefaktänderung.

## Status und Grenzen

- **VERIFIZIERT:** Keine Instanz von `DA E0 5C 35` im vollständigen Composite-Dateibereich; exakte Eingabegröße und Hash stimmen.
- **OFFEN:** Andere direkte C166-Call-Kodierungen oder Varianten, die nicht aus dem beobachteten `calls`-Encoding `DA E0 imm16-le` ableitbar sind.
- **OFFEN:** Instruktionsgrenzen für andere Bytes, mögliche überlagerte Dekodierungen sowie indirekte Callformen. Die rohe Signatursuche behauptet nichts darüber.
- **Alternativerklärung:** E0355C könnte durch eine andere direkte Kodierung, einen indirekten Kontrolltransfer oder aus einem außerhalb des Composites liegenden Aufruf erreicht werden. Diese Möglichkeiten wurden nicht untersucht.
- Die Offset-zu-Analyseadresse-Beziehung `E00000 + Offset` ist syntaktische Composite-Adressierung; aus diesem Befund folgt keine Funktionszugehörigkeit oder Ausführung.
- Keine Aussage zu ABI, Hardware, Runtime, I/O, Semantik oder Funktionseigentum. Eigene Prüfung ist Self-review, kein unabhängiger Review, Runtime- oder Hardware-Nachweis.

## Einmalige REA-Fehlernotiz

Der erste `open_binary`-Aufruf wurde mit `target_unavailable`, Kategorie `unsupported_target`, Grund `unsupported binary format` und Constraint `file_format_rejected` zurückgewiesen. Der erste Rizin-Aufruf übergab CLI-Optionen als Rizin-Befehl; REA zeichnete `ERROR: Command '-N' does not exist.` bei Exitcode 0 auf. Dieser Aufruf ist nicht als Analysebefund gewertet und wurde nicht identisch wiederholt. Der korrigierte Rizin-Aufruf übergab nur Rizin-Kommandos.

## Tests und Dateien

- Validator: **PASS** — `python3 validate.py`; Offline-Artefaktidentität, Tabelle, Suchvollständigkeit und Evidence geprüft.
- Analysis test: **NOT_RUN** — keine Emulation, Runtime oder Hardware.
- Dateien und SHA-256 werden in `SHA256SUMS` festgehalten.
