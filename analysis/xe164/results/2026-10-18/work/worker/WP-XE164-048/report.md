> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-048 — statischer Kontrollfluss ab E00DAA

## Finding

**VERIFIZIERT** für die vom Rizin-C166-Fallback gelieferten statischen Bytes und Decode-Beobachtungen: Das Fenster `[0x0DAA,0x0EE8)` umfasst exakt 318 Bytes und dekodiert linear in 97 lückenlos aneinander anschließende Instruktionen. Vom Seed `E00DAA` gibt es im beobachteten Bereich nur den sequentiellen Fortgang bis `E00EE6: RETS`; innerhalb des Fensters liegt kein bedingter/unbedingter Sprung und kein Call. Damit stimmen hier Seed-Erreichbarkeit und lineare Dekodierung bytegenau überein. Es bleibt unter dieser linearen Interpretation kein unverbundener Rest im Fenster.

Das belegt eine begrenzte statische Kontrollflussstruktur, keine vollständige Funktionsgröße. `0x0EE8` ist das exklusive Fensterende und wurde nicht dekodiert. Der isolierte Caller bei `0x0F00` wird ausschließlich als einzelner Callsite-Befund aufgeführt.

## Eingabe und Scope

- Composite: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`
- Vorab geprüft: 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Analysiertes Bytefenster: `[0x0DAA,0x0EE8)` = 318 Bytes; die Adresslabels E00DAA–E00EE7 folgen der vorgegebenen syntaktischen Basisabbildung.
- Isolierter Caller: genau eine Instruktion bei `0x0F00`.
- E00EE8, Nachbarbytes, weitere Caller und Callees blieben unangetastet.

## Exakte Tabellen

- `instructions.tsv`: alle 97 Instruktionsstarts, Längen, Bytes und Rizin-Texte.
- `edges.tsv`: die 96 sequentiellen Kanten plus terminale RETS-Kante. Keine Sprungkanten oder Callkanten wurden beobachtet.
- `components.tsv`: ein vom Seed belegter Bereich; null unverbundene Bytes nach der linearen Dekodierung innerhalb des Fensters.
- `caller.tsv`: nur die isolierte Caller-Instruktion.

Die 97 Längen summieren sich zu 318 Bytes; Startoffset und Ende sind exakt `0x0DAA` und exklusiv `0x0EE8`. Die Tabellen bilden Werkzeugbeobachtungen ab und deuten keine Register, SFRs oder Effekte semantisch aus.

## Methode, Evidence und Alternative

REA `open_binary` wurde auf dem Composite zuerst versucht und meldete `target_unavailable / unsupported binary format`. Die dort verfügbare Raw-Binary-Auswahl bietet keine C166-Architektur. Diese konkrete Providerlücke führte zum dokumentierten REA-`execute_rizin_command`-Fallback mit `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`, Farben aus. Die lokale CLI meldet Rizin 0.9.1, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`; REA selbst weist als Provider-Version `null` aus.

- `ev_6832bd7e3727ed68638cb53fef397847c4193058699a3d9c7a5dff35c8a6cb62`: Bytefenster und `pD 318`-Ausgabe ab Seed.
- `ev_857bcf6a9bda1d4ff214fb26fac1a544ebaa9976394b5ed0955a764e0f145478`: lineare `pd 97`-Ausgabe und genau ein `pdj 1`-Befund bei Caller `0x0F00`.
- Beide Rizin-Records: Exitcode 0, vollständige Ausgabe ohne Trunkierung, SHA-256 nach Ausführung unverändert.

Als Alternative ist der rohe Byteausschnitt im Evidence-Record enthalten; er ermöglicht Byteabgleich, ist jedoch kein unabhängiger Decoder. Kein zweiter Decoder wurde eingesetzt. Ghidra-Bereichsgröße bleibt **HYPOTHESE** und wurde nicht als Funktionsgrenze vorausgesetzt.

## Status und Restunsicherheit

- **VERIFIZIERT:** Eingabegröße/Hash; 318 beobachtete Bytes; 97 Rizin-Instruktionsstarts und vollständige lineare Byteabdeckung; sequenzielle Kette bis `RETS` bei `0x0EE6`; ein isolierter direkter Call von `0x0F00` nach `0x0DAA`.
- **OFFEN:** unabhängige C166-Dekodierung; ob die lineare Dekodierung semantisch Code statt eingebetteter Daten repräsentiert; ob `RETS` eine tatsächliche Funktionsgrenze ist; Rückkehrverhalten des Call-Targets.
- **HYPOTHESE:** die vorgegebene Fenstergröße als Ghidra-Funktionsgröße.
- **Nicht abgeleitet:** Bedeutung, ABI, SFRs, Runtime, Hardware oder physikalische Wirkung.

Die erreichbare Sequenz wird statisch aus dem Fehlen von Transfers vor dem terminalen Return abgeleitet; sie ist keine Laufzeitbeobachtung. Ein Call wurde nicht beobachtet, folglich war keine automatische Rückkehrannahme nötig. Rizin-Plugins und externe Dateizugriffe sind durch REA nicht an Evidence gebunden; verwendet wurde der explizite lokale Pfad, ohne Netzwerk-, Geräte- oder VM-Zugriff.

## Verifikation

`python3 validate.py` ist ein Worker-Self-Check, kein unabhängiges Review.

- `python3 validate.py`: **PASS** (Self-Check).
- `sha256sum -c SHA256SUMS`: **PASS**.
- Teststatusvokabular: `PASS | FAIL | NOT_RUN | BLOCKED`.
