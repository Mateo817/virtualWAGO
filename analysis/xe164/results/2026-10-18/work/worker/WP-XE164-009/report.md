> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-009 — E004CA

## Ergebnis und Status

**VERIFIZIERT (begrenzte statische Struktur):** Unter Ghidra 12.1.4 mit `C166:LE:16:default`, Compiler-Spec `tasking` und `BinaryLoader`-Basis `0xE00000` bildet der am Seed `E004CA` analysierte Funktionskörper 128 Adressbytes von `E004CA` bis `E00549`. Der kontrollflussbasierte Walk enthält 43 dekodierte Instruktionen und 14 Basic Blocks. Er enthält zehn direkte Call-Sites zu sechs Zieladressen. Die Instruktionen, Blockgrenzen, Kontrollflusskanten, Calls und von Ghidra materialisierten Referenzen stehen in den TSV-Dateien.

**OFFEN:** In diesem nur auf `E004CA` begrenzten Import lieferte Ghidras ReferenceManager keine eingehende Referenz auf `E004CA`; insbesondere materialisierte er hier keinen Caller bei `E00F18`. Das widerlegt den im Auftrag genannten Aufrufkontext nicht: `E00F18` wurde in diesem gezielten Lauf nicht als Quelle dekodiert. Eine Aussage „keine eingehenden Aufrufe“ ist daher nicht belegt.

**Teststatus:** PASS für den gezielten Ghidra-C166-Lauf, die Tabellenproduktion, die Eingabehash-Prüfung und den korrigierten fokussierten Rizin-Rohoffset-Cross-check bis zum `rets` bei `0x548` (Exit-Code 0, stderr leer, Eingabe unverändert). BLOCKED bleibt ein Rizin-Funktions-/CFG-Dossier; der erste generische Rizin-Versuch fand bei unbekannter Architektur keinen Funktionskopf, der korrigierte Lauf dient nur als Listing-/Byte-Cross-check. NOT_RUN für eine Vollständigkeitsprüfung eingehender Referenzen aus dem mehrsaatigen Composite-Replay.

## Eingaben und Bindung

| Eingabe | Größe | SHA-256 |
|---|---:|---|
| `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin` | 17110 bytes | `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` |
| `PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md` | 2169 bytes | `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5` |
| Gebundenes Replay-Script `PRIVATE_ANALYSIS_ROOT/work/ghidra/scripts/Xe164Probe.java` | 4315 bytes | `9289f41396180a3478ce3e64e70f54d38a397e5f4f7247b89bd8e8bf2808490f` |

Die drei Eingabeidentitäten wurden vor dem Ghidra-Lauf geprüft. Die Binary-Identität blieb nach dem Lauf unverändert. Das gebundene Replay-Dokument nennt Ghidra 12.1.4, dieselbe Sprache, denselben Compiler-Spec und dieselbe Load-Basis. Sein vorhandenes Script setzt weitere Seeds außerhalb dieses Arbeitspakets; es wurde deshalb nicht ausgeführt. Der Fallback importierte die Binary frisch und setzte ausschließlich `E004CA` als manuell bearbeiteten Seed. Er ist damit an dieselbe Loader-/Sprachkonfiguration gebunden, nicht an einen unverändert reproduzierten Mehrseed-Program-Zustand.

## Beobachtungen

- Datei-Offset ist im Tabellenmaterial `Analyseadresse − 0xE00000` gemäß `BinaryLoader`-Basis. Damit liegt Seed `E004CA` bei Offset `0x4CA`; der beobachtete Funktionskörper liegt bei Offsets `0x4CA..0x549`.
- Die 14 beobachteten Blockbereiche sind `E004CA–E004CF`, `E004D0–E004D3`, `E004D4–E004D7`, `E004D8–E004DD`, `E004DE–E004E1`, `E004E2–E004E7`, `E004E8–E004F1`, `E004F2–E004FD`, `E004FE–E00507`, `E00508–E00511`, `E00512–E0051B`, `E0051C–E0051F`, `E00520–E00545` und `E00546–E00549`. Exakte Offsets und Instruktionszahlen stehen in `basic_blocks.tsv`.
- Die drei bedingten Sprungkanten sind `E004E0 → E00520`, `E004E6 → E00520` und `E0051E → E004E8`; die zugehörigen Fallthrough-Kanten sind in `edges.tsv` ausgewiesen.
- Die direkten Call-Sites und Ziele sind: `E004CC → E0043C`, `E004D0 → E00ACC`, `E004D4 → E00972`, `E004DA → E00B42`, `E004EE → E03878`, `E004FA → E03878`, `E00504 → E03878`, `E0050E → E03878`, `E00518 → E03878` und `E00542 → E0045C`. Ziele sind nur als Adressen/Edges dokumentiert; sie wurden nicht rekursiv analysiert.
- `references.tsv` enthält 13 ausgehende ReferenceManager-Referenzen der erreichten Instruktionen: zehn Calls und drei bedingte Sprünge. Für die erreichten Instruktionen materialisierte der Provider hier keine Datenreferenz. Das ist ein Befund über diese Ghidra-Referenzdatenbank, kein Beleg, dass die adressierten Operanden keine Datenwirkung haben.
- Der fokussierte REA-Rizin-Cross-check (Evidence `ev_750e8b2a7a65cf24651b4f5b42ebde732a02eb5c52e8edb91bdc1ceee5cf24cc`) setzte `io.va=false`, `asm.arch=c166`, `asm.bits=16`, `asm.cpu=xe164`, `cfg.bigendian=false`, seekte auf Datei-Offset `0x4CA` und gab `px 128` sowie `pd 50` aus. Die Bytes und das Listing stimmen im begrenzten Zielbereich bis `rets` bei Offset `0x548` mit dem Ghidra-Lauf überein; Rizin liefert damit einen Raw-offset-Cross-check, keinen Ersatz für Ghidras CFG-/ReferenceManager-Struktur. Der feste Disassemblierumfang lief nach dem Terminal noch sieben sequenzielle Instruktionen von `0x54A` bis `0x558` weiter. Diese Post-Terminal-Ausgabe wird als Scope-Überlauf offengelegt und nicht ausgewertet oder in die Tabellen aufgenommen.
- Im Code werden Operandtexte und Bytes unverändert als Listing-Beobachtung festgehalten. Es werden keine SFR-, Interrupt-, K-Bus- oder sonstigen Hardwaresemantiken zugewiesen.
- Es wurde kein Pseudocode erzeugt. Die Tabellen sind direkte Werkzeugableitungen aus Ghidra Listing, Instruktionsfluss und ReferenceManager; sie sind kein Originalquelltext.

## Werkzeuge, Konfiguration und tatsächliche Aktivität

REA meldete Version `rea-agents 6.5.0`. Der vorhandene REA-Binary-Session-Status war geschlossen; es gab keinen aktiven Provider. Es wurde deshalb kein `open_binary`-Versuch für C166 unternommen. Der erste gezielte `execute_rizin_command`-Versuch verwendete `aaa; s 0xE004CA; af @ 0xE004CA; pdf @ 0xE004CA; agf @ 0xE004CA; axt @ 0xE004CA`. Evidence `ev_8e2670a7b4e469e6624a37e500aa935d6039b870847f198163d03949eba98e49` bindet die Binary und meldet `ERROR: Cannot find function at 0x00e004ca`, leere stdout, keine erkannte Architektur und `artifact_changed=false`. Danach lief genau ein geänderter fokussierter REA-Aufruf ohne `aaa`: `e io.va=false; e asm.arch=c166; e asm.bits=16; e asm.cpu=xe164; e cfg.bigendian=false; s 0x4ca; px 128 @ 0x4ca; pd 50 @ 0x4ca`. Seine Evidence-ID ist `ev_750e8b2a7a65cf24651b4f5b42ebde732a02eb5c52e8edb91bdc1ceee5cf24cc`; die vollständige Aufnahme liegt in `REA-Evidence-Bundle-rizin-offset-crosscheck.json`. Der zuvor versuchte Rizin-interne Versionsbefehl `?V` wurde nicht geparst (Evidence `ev_07ff84b036c984c15c00d966b296a59e534e86bcb2b78e894036a1c1d9e1c8b7`). Der lokale CLI-Versionsaufruf meldete Rizin `0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`.

Auf die beobachtete Architektur-/CFG-Lücke folgte der direkte Ghidra-C166-Fallback. Verwendet wurde Ghidra 12.1.4 mit C166-Modul `c166-ghidra-module-v1.2.2`, Java 21.0.12.1, `BinaryLoader`, Basis `0xE00000`, Sprache `C166:LE:16:default`, Compiler-Spec `tasking`, `-analysisTimeoutPerFile 45`, `-max-cpu 1`, `-readOnly` und `-deleteProject`. Ein temporäres Projekt lag unter `/tmp`; Import, Post-Script und Exportlogs liegen ausschließlich in diesem Worker-Ausgabeverzeichnis. Der Prozess lief unter `unshare -Un --map-current-user`. Praktischer Namespace-Vergleich: außen `net:[4026531840]`, innerhalb `net:[4026532555]`.

Das lokale Script `Xe164Seed.java` markiert keine zusätzlichen Entry Points und traversiert nur statisch bekannte Flows ab `E004CA`. Calls werden als Kanten erfasst, ihre Ziele nicht traversiert. Bereits bestehende abweichende Function-Einträge und die explizit ausgeschlossenen Adressen `E00634`, `E00BEE`, `E03586`, `E0369C` sind Walk-Grenzen. Das Script wurde dreimal ausgeführt, um die Blocktabelle und eindeutige Call-Edges zu vervollständigen; `ghidra.log`/`script.log` dokumentieren den letzten Lauf, `*-prior-runs.log` die beiden vorherigen Läufe. Der letzte Lauf meldet `Import succeeded`, 43 Instruktionszeilen, 14 Blockstarts und keine eingehende Seed-Referenz. Es gab keinen unabhängigen Review und keinen weiteren Worker.

## Alternative Erklärung und Restunsicherheit

Die fehlende eingehende Referenz kann dadurch erklärt werden, dass dieser gezielte Import `E00F18` und andere Caller-Quellen nicht dekodiert hat. Das ist mit dem im Auftrag genannten Call von `E00F18` vereinbar. Es bleibt offen, welche direkten eingehenden Referenzen der umfassendere, mehrsaatige Composite-Replay tatsächlich materialisiert. Außerdem sind indirekte bzw. nicht auflösbare Flows grundsätzlich nicht als konkrete Kanten belegt. Die Ergebnisse begründen keine Laufzeitbeobachtung.

## Dateien dieses Arbeitspakets

SHA-256 ist für alle Ergebnisdateien außer `report.md` und `SHA256SUMS` angegeben; `SHA256SUMS` bindet auch den Report. Der Checksum-Manifest selbst ist konventionell nicht in sich selbst enthalten.

| Datei | Größe | SHA-256 |
|---|---:|---|
| `REA-Evidence-Bundle.json` | 4979 | `7159d57370c1b47942afbec0fdfeebd548a7ea009e7edb57f36c6159d264b801` |
| `REA-Evidence-Bundle-rizin-offset-crosscheck.json` | 39265 | `c52d4ce5694098d837d661418b8f18ea70484c9917325b32c300958b9c6c5603` |
| `Xe164Seed.java` | 9331 | `bdd99c721903af0d8e719d471d078fd8a7cd86057b748615a2cdf5791ac4dbb5` |
| `basic_blocks.tsv` | 455 | `b0b58083774e9ad48cfe45d46e864d555a1a797c662dca051055612f4f106947` |
| `calls.tsv` | 618 | `f14776bbccd54efd30db4f7d3513e3ad822e6f31cd40abecc59f5170627059fe` |
| `edges.tsv` | 3246 | `a843ed97b67024a43b6332a9dbce05bda0aa2517301c6b032d7e2012549dfa2b` |
| `ghidra-prior-runs.log` | 9673 | `e8e7e9667732579cc17babeded569ce16930fa61abad5b749a6fd0487b88b725` |
| `ghidra.log` | 9674 | `39ebaaf83868bbdb5f7b53a391f660ff1030a6a40f357c6ab9bd3f5dfbd67ed4` |
| `instructions.tsv` | 2237 | `d53a365fa086f9b3ccd99eddbd3722beb8705fd01ecb4ac94dbe9083dd6476da` |
| `references.tsv` | 806 | `1fa9d90fed9ff7b82f719b0cda441116bb75d7e74fa8ddd59e0c49ddc0c44229` |
| `script-prior-runs.log` | 1457 | `ed37ea0f003ab9c81b3a9f5dfcba30b28ea8d661d36d4f54fd91d5a26f587aa0` |
| `script.log` | 1457 | `71b9f3453a6b87b971eb4eff9c523e0e15b6032e3dab4c72f2c3090f517f3d71` |
