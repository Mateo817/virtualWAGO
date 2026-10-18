> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-038 — Kontrollfluss bei E033B8 bis vor E0340E

## Ergebnis

**VERIFIZIERT (statisch, begrenzter Umfang):** Im angegebenen Composite ist der per `E03696` aufgerufene Eintritt `E033B8` bis `E033EE` eine lineare Folge von 17 dekodierten C166-Instruktionen. Die Folge endet mit `rets` an `E033EE`. Ab `E033F0` liegt eine weitere lineare Folge von zehn Instruktionen bis zu einem zweiten `rets` an `E0340C`. Beide Bereiche enthalten je nur Fallthrough-Kanten innerhalb ihrer linearen Folge; ein Fallthrough über `rets` hinweg wird nicht angenommen. Im gesamten dekodierten Fenster `0x33B8..0x340D` gibt es keine bedingte Verzweigung oder Call-Instruktion. Das Fenster endet exakt vor dem bekannten Ziel `E0340E`.

Der isoliert vorgegebene Caller enthält an `E03696` die vier Byte `dae0b833`, von REA/Rizin als `calls 0xe033b8` dekodiert; die lineare Fortsetzung dieser Call-Instruktion ist `E0369A`. Dies belegt die Verbindung dieses Callsite-Eintrags zu `E033B8`, aber keine vollständige Caller-Inventur.

## Eingabe, Methode und Evidence

- Eingabe: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`, 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- REA zuerst: `open_binary` lehnte das rohe Composite als nicht unterstütztes Binärformat ab (`unsupported binary format`). Danach nutzte ich REAs dokumentiertes `execute_rizin_command` mit `-N -q`, `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false` und `io.va=false`. Kein Ziel wurde ausgeführt und keine globale Analyse/Xref-Suche gestartet.
- Der exakte Fensterdump wurde mit `px 86 @ 0x33b8` erhoben: `ev_be3a3a97f57d722c3f5a55c5148293b6b7c858024e211dfbb57cc17998106efc`.
- Die C166-Dekodierung des genau 86 Byte großen Fensters wurde mit `pDj 86 @ 0x33b8` erhoben: `ev_ae9278fc277faebf13c7035b282256f2f0678ae7f2218ec2ac5e39e829643ac1`.
- Der isolierte Caller wurde mit `pdj 1 @ 0x3696` erhoben: `ev_c690d5a6235e9b79d2b90491c9f5f9926fcd05d7e2f8a2de235be94e37523257`.
- Das kanonische finding-only REA-Bundle mit genau diesen drei Evidence-Records liegt in `evidence/rea-finding-bundle.json`; Provider-Version ist nicht bekannt (`rizin.version = null`).
- Adressbindung in den Tabellen: Datei-Offset plus Basis `0xE00000`; dies ist eine notierte Replay-Adresskonvention und keine Aussage zu Runtime-Mapping.

Die vollständigen dekodierten Instruktions-, Fallthrough- und Caller-Tabellen stehen in `instructions.tsv`, `edges.tsv` und `calls.tsv`.

## Status und Grenzen

- **VERIFIZIERT:** Dekodierung und Bytebindung für exakt 86 Bytes; zwei lokale lineare Komponenten mit 17 bzw. zehn Instruktionen, getrennt durch den `rets` bei `E033EE`; ein weiterer terminaler `rets` bei `E0340C`; kein beobachteter Branch oder Call im abgegrenzten Fenster; vorgegebener Callsite bei `E03696` zeigt auf den Start `E033B8`.
- **HYPOTHESE:** Die zweite lineare Komponente könnte separat über einen Eintritt innerhalb ihres Bereichs erreicht werden. Das Fenster allein belegt keinen solchen Eintritt und identifiziert keine Funktionseinheiten.
- **OFFEN:** Ob andere Caller oder Sprünge in den Bereich oder insbesondere in `E033F0..E0340C` führen; globale Xrefs wurden absichtlich nicht gesucht. Ebenso offen bleiben Funktionseinstiege, Semantik, Runtime-Wirkung, Register-/Speicherbedeutungen, C166-Untervariante, Calling Convention und Verhalten auf Hardware.
- **NOT_RUN:** Unabhängige Ghidra-Dekodierung. Sie könnte Instruktionslängen und die zwei `rets` als alternative Disassemblierung prüfen; derzeit verbleibt die Provider-/Disassemblerabhängigkeit von Rizin (Version nicht gemeldet).
- **Alternative:** Unabhängige Prüfung der exakt begrenzten Bytes mit Ghidra `C166:LE:16:default`, ohne Erweiterung auf Nachbarcode. Eine Abweichung würde die dekodierte Instruktionsgrenze und CFG-Aussage offenlassen.
- Die Belege sind statische Beobachtungen im angegebenen Composite; es gab keine Geräte-, Netzwerk-, VM- oder Runtime-Arbeit.

## Validierung

`validate.py` (Self-Review) prüft Quellgröße und SHA-256, alle 86 Bytes, Tabellenlängen und Adressbindungen, die dekodierte JSON-Ausgabe gegen `instructions.tsv`, beide Terminalgrenzen, alle 25 internen Fallthrough-Kanten, den isolierten Caller und die drei Evidence-IDs im finding-only Bundle. Ergebnis: **PASS**. `sha256sum -c SHA256SUMS`: **PASS**.
