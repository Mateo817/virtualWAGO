> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-010 — statischer Kontrollfluss ab E00634

## Ergebnis und Befundstatus

**Befundstatus: VERIFIZIERT** für die begrenzte statische Dekodierung des Startpunkts E00634 im gebundenen Composite-Abbild. Der von Rizin dekodierte Funktionsbereich reicht von Analyseadresse `E00634` bis einschließlich `E006C2` (Ende exklusiv `E006C4`), entsprechend Dateioffsets `0x634..0x6C3` im Composite mit Basis `E00000`. Er umfasst 54 dekodierte Instruktionen und acht aus dem Listing abgeleitete Basicblocks. Die vollständige Instruktionsliste, internen Kanten, direkten Call-Kanten und materialisierten direkten Referenzen stehen in den TSV-Dateien.

Der im Auftrag genannte Aufruferbeginn `E00F18` liegt im Dateioffset `0xF18`. Der Call auf E00634 steht innerhalb dieses Aufruferbereichs bei `E00F24` (Dateioffset `0xF24`). Die beobachtete Instruktion ist `CALLS E00634`. E00634 wird ab dort als eigenständiger Einstieg dekodiert; ausgehende direkte Calls werden nur als Adresskanten aufgeführt.

Die Bereichsbindung ist **VERIFIZIERT** gegen `PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md` (2,169 Byte, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`) und gegen das Composite (17,110 Byte, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`). Das in der Aufgabenmeldung zunächst genannte `evidence/composite-replay.md` existiert nicht; nach der Korrektur des Auftraggebers wurde das vorhandene `work/ghidra/composite-replay.md` frisch gebunden. Der Replay-Vermerk dokumentiert Ghidra 12.1.4, Sprache `C166:LE:16:default`, Compiler-Spec `tasking`, BinaryLoader-Basis `0xe00000` und den Hash des zugehörigen Scripts `Xe164Probe.java` (`9289f41396180a3478ce3e64e70f54d38a397e5f4f7247b89bd8e8bf2808490f`). Für dieses Worker-Paket wurde das Script nicht ausgeführt.

## Beobachtete Struktur

Rizin erkannte nach manuellem Funktionsstart bei Dateioffset `0x634` den zusammenhängenden Codebereich `0x634..0x6C3`. Die Kontrollflusskanten umfassen Verzweigungen bei `E0066E`, `E00680`, `E00686`, `E006AA` und `E006B0`; `E006AA` führt zurück nach `E00670`. Der Pfad erreicht den gemeinsamen Abschluss ab `E006AC` und endet mit `RETS` bei `E006C2`. Die genaue Basicblock-Kantenliste steht in `edges.tsv`.

Im Bereich liegen fünf direkte Call-Instruktionen: `E0064C`, `E00654`, `E0067A`, `E00698` und `E0069E`. Die TSV-Datei hält die von Rizin dekodierten Operanden `0x054A`, `0x0556`, `0x05A2`, `0x0562` und `0x05EC` fest. Die daneben gezeigten `E005xx`-Ziele sind ausschließlich eine Basisabbildung dieser Operanden unter `E00000`; sie beanspruchen keine Rekursion oder Funktionsanalyse dieser Ziele.

Als absolute Operanden sind `0xFF10.11` (bei `E00646`, `E0064A`, `E006B4`) und `0xFF12` (bei `E006AC`) dekodiert. Sie werden nur als Adress-/Bit-Tokens geführt; es wird keine SFR-, Interrupt- oder K-Bus-Semantik zugeordnet. Register-indirekte Speicherzugriffe wie `[r0]` bleiben ohne Datenfluss-/Laufzeitbeleg dynamisch und ungelöst.

## Verfahren und Toolkonfiguration

Die Eingabehashes wurden vor dem REA-Aufruf frisch festgestellt. REA `execute_rizin_command` wurde auf der unveränderten Composite-Datei benutzt. REA-Provider war Rizin; die lokale Binärversion wurde als `rizin 0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`, festgestellt. Das Raw-Importprofil von REA weist die Architektur als unbekannt aus; für gezielte Befehle wurde deshalb explizit `asm.arch=c166`, `asm.bits=16`, `asm.cpu=xe164` eingestellt. Die Rizin-Adressen sind dabei Dateioffsets ab 0; Analyseadressen in diesem Report entstehen durch Addition der dokumentierten Composite-Basis `0xE00000`.

Erfolgreiche gezielte REA-Befehle:

- `e asm.arch=c166; s 0x634; pd 32` — lokaler Dekodiercheck am Seed.
- `e asm.arch=c166; e asm.bits=16; e asm.cpu=xe164; af @ 0x634; pdf @ 0x634` — manuelles Markieren und rekursives Listing des Seed-Bereichs samt CFG.
- `e asm.arch=c166; e asm.bits=16; e asm.cpu=xe164; s 0xf18; pd 16` — gezielter Ausschnitt für den direkten eingehenden Call bei `0xF24`.

Ein globaler Rizin-Xref-Lauf (`aaa; axt @ 0x634`) brach mit einer C166-Assertion (`c166_activate_ext: assertion 'ext.i <= 3' failed`) ab und lieferte keine Xrefs. Deshalb ist der nachgewiesene eingehende Verweis die explizit dekodierte Call-Instruktion bei `E00F24`; ob der Replay weitere eingehende Verweise materialisiert, bleibt **OFFEN**. Es gab nach erfolgreicher lokaler Dekodierung keine verbleibende Architektur- oder CFG-Lücke, die einen Ghidra-Fallback für diesen Workerbereich erforderlich machte. Die Rizin-Xref-Ausnahme ist als Test **FAIL** protokolliert, nicht als erfolgreiche globale Vollständigkeitsprüfung.

## Status, Alternativerklärung und Restunsicherheit

- **Befundstatus:** VERIFIZIERT für die statische Seed-Dekodierung und die aufgeführten lokalen CFG-/Call-/Operandreferenzen; OFFEN für Vollständigkeit aller eingehenden Replay-Xrefs.
- **Teststatus:** PASS für den gezielten Rizin-C166-Disassembly-/CFG-Lauf und für den maschinellen Kontiguitätscheck (`python3 check_contiguity.py`); FAIL für den globalen Rizin-Xref-Versuch wegen Assertion; NOT_RUN für Ghidra in diesem Workerpaket.
- **Alternative Erklärung:** `E00F18` kann als Beginn des aufrufenden Blocks/Funktionskandidaten gemeint sein. Der tatsächlich auf E00634 zielende Call steht vier Instruktionsbytes später bei `E00F24`; die bei `E00F18` stehende Call-Instruktion selbst zielt laut gezieltem Listing nicht auf E00634.
- **Restunsicherheit:** Das Listing belegt die dekodierte Kontrollflussstruktur dieser Bytes unter dem angegebenen C166-Modell. Es weist keine Laufzeitpfade, tatsächlichen Dateninhalte, Hardwarewirkung oder Semantik absoluter Speicheradressen nach. Der globale REA-Xref-Scan schlug fehl, daher wird keine Ausschließlichkeit des einzigen gefundenen Callers behauptet.

Pseudocode wurde nicht erzeugt. Falls aus den Tabellen ein Ablauftext formuliert wird, wäre dieser ausdrücklich Werkzeugableitung und keine Hersteller- oder Laufzeitaussage.

## Tatsächliche Workeraktivität und erzeugte Dateien

Der Worker hat die beiden gebundenen Eingaben gelesen/gehasht, die oben aufgeführten lokalen REA-Kommandos ausgeführt und das REA-Evidence-Bundle mit sechs Evidenzdatensätzen exportiert. Keine Geräte-, Netzwerk- oder VM-Aktion; keine Repositorydateien, Originalbinärdatei oder Ghidra-Projektdateien geändert. Es gab keinen unabhängigen Review oder separaten Worker-Lauf.

Bei Self-Review wurde die ursprüngliche Tabellengröße von 2 Byte für `E006B0` als Fehler erkannt: Die nächste Instruktion beginnt bei Dateioffset `0x6B4`, und die gebundenen Bytes an `0x6B0` sind `9a f8 01 f0`, daher ist die tabellierte Instruktionslänge auf 4 Byte korrigiert. Der neue reproduzierbare `check_contiguity.py` vergleicht maschinell jede tabellierte Instruktion mit dem Abstand zum Folgeoffset, prüft die exklusive Endgrenze `0x6C4`, die Abbildung der Analyseadressen und diese vier Bytes; sein Laufstatus ist im Worker-Log dokumentiert.

Erzeugte Payload-Dateien; die vollständigen SHA-256-Werte sowie der Hash dieses Reports stehen in `SHA256SUMS`:

- `instructions.tsv` — 54 gelistete Instruktionen des begrenzten Bereichs.
- `edges.tsv` — abgeleitete Basicblock-Kanten.
- `calls.tsv` — direkte Call-Kanten ohne Callee-Rekursion.
- `references.tsv` — eine beobachtete eingehende Call-Referenz und statische Operand-/Indirektreferenzen.
- `check_contiguity.py` — reproduzierbare Kontiguitäts- und Grenzprüfung der Instruktionstabelle.
- `contiguity-check.log` — protokollierter PASS-Lauf des Checkers.
- `REA-Evidence-Bundle` — REA-Export, 85,887 Byte, sechs Datensätze.
- `report.md` — dieser Befundbericht.

`SHA256SUMS` ist konventionell mit relativen Pfaden angelegt; `sha256sum -c SHA256SUMS` wurde im Worker-Ausgabeverzeichnis ausgeführt und muss für alle Payloads PASS liefern.
