> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-012 — begrenzter Startbereich E03586

Gesamtstatus: **PASS** für den akzeptierten, eng begrenzten Offline-Lauf. Der frühere Overscope-Lauf bleibt als verworfene Auditspur erhalten und ist nicht Grundlage der folgenden Aussagen.

## Ergebnis

Im akzeptierten Caller-Probe ist bei Dateioffset `0x0f2c` / Replay-Analyseadresse `E00F2C` genau eine Instruktion dekodiert: `calls E03586`. Im akzeptierten Seed-Probe dekodiert `pd 50 @ 0x3586` genau 50 Instruktionen, von Offset `0x3586` bis zum Startoffset `0x3632` der letzten dekodierten Instruktion (Analyseadressen `E03586..E03632`). Die Folge ist im erfassten Bereich linear: sie enthält einen direkten Call bei Offset `0x361c` / Adresse `E0361C` an `E0340E`, danach die Fortsetzung bei `E03620`, und endet mit `rets` bei `E03632`. Es wurde kein bedingter oder unbedingter Sprung innerhalb dieser 50 Instruktionen dekodiert. Der Callee `E0340E` wurde nur als Zieladresse/Edge notiert, nicht analysiert.

Die Referenztabelle enthält 18 explizit adressähnliche Speicheroperanden plus zwei indirekte `[r12]`-Operanden. Das sind rohe Decoderformen; Speicherziele, Register, SFRs oder gerätespezifische Bedeutung werden nicht interpretiert. Der akzeptierte `pd`-Record liefert Instruktionsstarts, aber keine Byte-Längen; deshalb beansprucht der Bericht keinen exakten Byteumfang für diesen Bereich.

## Befunde

- **VERIFIZIERT** — Caller-Aufruf `E00F2C → E03586`, Fileoffset `0x0f2c`, aus einer einzelnen dekodierten Instruktion. Evidence `ev_fa7e4460fc086d0b97642437fff9388b68f8f4500e737294e451e4575a142571`.
- **VERIFIZIERT** — Exakt 50 fortlaufend dekodierte Instruktionen bei Offset `0x3586..0x3632`, ohne Sprunginstruktion im abgefragten Bereich; direkter Call bei `E0361C → E0340E`, Fortsetzung `E03620`, Return `E03632`. Evidence `ev_103edf54b38e66ebcd2974213a0118cbed26af73a678a5544d8faf15fc25ec04`.
- **HYPOTHESE** — Die im abgefragten linearen Ausschnitt erkennbare Pfadstruktur entspricht einem Basicblock der beabsichtigten Funktion; dieser akzeptierte Lauf hat keine separate Funktions-/CFG-Analyse aufgerufen.
- **OFFEN** — Effektive Laufzeitadressen der beiden indirekten Speicherzugriffe, Bedeutung adressähnlicher Operanden und Verhalten der nicht rekursiv untersuchten Callees.

## Methode und Bindung

REA `execute_rizin_command`; installierte Rizin-Version `0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7` (die REA-Provider-Metadaten selbst melden Version `null`). Beide akzeptierten Befehle explizit mit `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Fileoffset `x` wird anhand der gebundenen Replay-Konfiguration als Analyseadresse `E00000+x` dargestellt. Es wurde kein Script ausgeführt, kein `open_binary`, kein globales `aaa` und kein Ghidra-Fallback verwendet.

Vor dem Lauf gebundene Eingaben: Composite, 17110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`; Replay-Notiz, 2169 Bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`. Beide REA-Befunde melden nachher unveränderten Binary-Hash und `artifact_changed=false`.

Der REA-Ledger-Export enthielt sieben Records. `extract_and_validate.py` selektiert daraus explizit ausschließlich die beiden oben genannten Evidence-IDs in `REA-Evidence-Bundle-accepted.json`; die ausgewählten Record-Objekte bleiben unverändert. Der vollständige Ledger-Export wird als `REA-Evidence-Bundle-ledger-current.json` aufbewahrt. Die früheren breiten Bundle-/Report-Artefakte sind unter den Namen `REA-Evidence-Bundle-rejected-overscope.json` und `report.rejected-overscope.md` erhalten; beide bilden den verworfenen Overscope-Lauf ab.

## Grenzen, alternative Erklärung und Tests

Alternative Erklärung: ein statischer linearer Decode belegt nur die Instruktionen und unmittelbaren Transfers im erfassten Bereich; dynamische Ziele und Laufzeitausführung sind nicht beobachtet. Der mögliche Basicblock-Charakter bleibt daher als Hypothese markiert.

E0369C bleibt im akzeptierten Lauf ausdrücklich nicht ausgewertet: die Seed-Abfrage endet genau bei `RETS` an `0x3632`, und die Caller-Abfrage umfasst ausschließlich eine Instruktion an `E00F2C`. Die verworfene Overscope-Auditspur enthält noch rohe Bytes aus einer früheren breiten linearen Ausgabe; sie ist nicht im akzeptierten Evidence-Bundle und nicht Grundlage dieses Reports.

Restunsicherheit: Operandauflösung für indirekte `[r12]`-Zugriffe, Laufzeitpfad und Grenzen der ursprünglichen Funktion über die abgefragte Endinstruktion hinaus.

Tests: **PASS** — Validator bestätigt exakte REA-Kommandos und Eingabeidentität, Auswahl nur der beiden unveränderten Records, Instruktionsumfang, Referenzanzahl sowie TSV-Tabulatoren/Spalten. `sha256sum -c SHA256SUMS`: **PASS**. **NOT_RUN** — unabhängiger Review; die Arbeit ist durch den Worker ausgeführt und geprüft, nicht unabhängig reviewed.

## Dateien und Hashes

Die Prüfsummen sämtlicher Lieferdateien und Auditspuren stehen in `SHA256SUMS`; der Manifest-Hash selbst ist wegen der konventionellen Nicht-Selbstreferenzierung separat in der Übergabe genannt.
