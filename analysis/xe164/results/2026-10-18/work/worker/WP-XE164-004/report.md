> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-004 — ARM-seitige XE164-Loaderpfade (FW30)

## Ergebnis

**VERIFIZIERT (statische ARM-Beobachtung):** Das exakt gebundene FW30-IPK enthält die drei vorgegebenen Dateien bytegleich unter `/etc/specific/` und die ARM32-ELF-Bibliothek `/usr/lib/libpackbus.so.1.0.1` (Symlink-Kopien davon liegen unter `/usr/lib/libpackbus.so` und `/usr/lib/dal/libpackbus.so`). Im ELF zeigen Ghidra und die auf die Stringtabellen begrenzte Rizin-Prüfung die drei absoluten Pfade. Der Aufrufpfad führt von `SCPU_boot_slave` (`0x1a470`) zu `FUN_00019a78` und von dort zu `FUN_000197f0`; die letztere Funktion liest step-indiziert Dateiinhalt über `stat`, `open` und `read`. `FUN_00019a78` enthält serielle Schreib-/Ack-Logik sowie einen separaten bedingten SPI-Zweig.

Die statisch initialisierten Einträge belegen Pfadzuordnung, Größenbehandlung sowie getrennte Längenpräfix-, Rohdaten- und XOR-Stufen. Korrektur nach erneuter Feldprüfung: der Präfixzweig prüft Tabellenbyte +20; das Ack-Flag liegt separat bei +21, das XOR-Flag bei +32. L1-Einträge 0/5 konfigurieren Rohdaten. L2-Einträge 1/6 konfigurieren ebenfalls Rohdaten (Ack in beiden); L3-Einträge 2/7 konfigurieren ein vier Byte langes Längenpräfix (Ack nur in 7), Eintrag 3 Rohdaten mit Ack, Eintrag 8 Rohdaten ohne Ack und Eintrag 9 Rohdaten plus XOR-Byte mit Ack. Alle geprüften Transferselektoren bei +12 sind null; der separate `type == 1` SPI-Payloadzweig wird von den statischen Zeilen nicht ausgewählt. Das sind statisch konfigurierte Schritte und keine Laufzeitbeobachtung, dass jeder Schritt tatsächlich durchlaufen oder Bytes am Ziel platziert wurden. **Die frühere Aussage „kein L2/L3 Payloadtransfer“ ist verworfen.**

**Korrelation zu C166 — HYPOTHESE/OFFEN:** WP-XE164-001 korrigierte den Vergleich: Composite-Offsets `0x200..0x3ff` entsprechen L3-Quelloffsets `0x000..0x1ff`; 128/128 Vierbytezeilen bzw. 512/512 Bytes sind identisch. Dies ist eine statische Dateikorrelation, nicht der Nachweis, dass ARM genau diese Bytes überträgt oder sie an Composite-Adresse `0xe00200` platziert. Die C166-Ausschnitte belegen weder die ARM-seitigen seriellen Längen-/Rohdaten-/XOR-Stufen noch deren tatsächliche Ausführung.

## Gebundene Eingaben

| Eingabe | Größe | SHA-256 |
|---|---:|---|
| `sources/fw30-sdk-libpackbus-1.0.3/libpackbus_1.0.3_armhf.ipk` | 77,686 | `f06340a7e0285582c3517efcbe8c50c63fb1dbc2a9773ae83e3cce065a2de0fe` |
| `sources/fw30-sdk-libpackbus-1.0.3/XE164L1.bin` | 32 | `42549d93b538a898203f90488c8d98fc5715e7fd506c5d645de9a00793e20084` |
| `sources/fw30-sdk-libpackbus-1.0.3/XE164L2.bin` | 266 | `b4a7eddb47ca3d31040a5d567a847af3da75b5db9b8b49b59ef104b01f079245` |
| `sources/fw30-sdk-libpackbus-1.0.3/XE164L3.bin` | 16,598 | `26fe2560d12ed794a572186d4f66217a430838f6e1f345f5f6f2f2f0df734abf` |

`ar`-extrahierte Dateien und die drei Paketkopien der Blobs wurden im exklusiven WP-Ausgabeverzeichnis gehasht. Die Paketkopien haben dieselben SHA-256-Werte wie die vorgegebenen Blobs.

## Methode, Tooling und Bindung

REA `open_binary` wurde zuerst auf dem unveränderten IPK aufgerufen. REA gab `target_unavailable`, Kategorie `unsupported_target`, Meldung `Cannot open artifact: unsupported binary format`, Detailgrund `unsupported binary format` und Constraint `file_format_rejected` zurück. Für diesen Paketaufruf gab es keinen Provider-/Architektur-Bind. Ohne denselben Versuch zu wiederholen, wurde der erlaubte formatbewusste Offline-Fallback verwendet: GNU `ar` 2.44 und GNU `tar` 1.35 für die `.ipk`-/`tar.gz`-Hülle, `readelf` 2.44 für ELF-Metadaten und Rizin 0.9.1 für begrenzte String-/Referenzprüfung.

Der extrahierte ELF-Träger wurde danach erfolgreich mit REA 6.5.0 / Ghidra 12.1.4 analysiert. Import: `loader=auto-from-header`, `ARM:LE:32:v8:default`, Compiler-Spec `auto-default`, Analyzer-Preset `ghidra-default`, `ephemeral-source-immutable`; Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. REA-Ghidra-Abbildbasis ist `0x10000`; Rizin-Stringadressen sind ELF-virtuelle Adressen ohne diesen Analyse-Offset. Ghidra meldete nicht aufgelöste externe Bibliotheken, die Funktions-/Datenbefunde hier beruhen deshalb auf dem importierten ELF und seinen internen Symbolen/Bytes, nicht auf einer aufgelösten Runtime.

Die REA-`xrefs`-Abfragen an den drei Stringadressen lieferten leere Listen. Dies wurde als begrenztes negatives Ergebnis festgehalten, nicht als Abwesenheit von Referenzen. Rizin `izz` bestätigte die Strings im ELF `.rodata`; `aaa; axt` fand Verweise aus `fcn.000097f0`. Ghidra-Pseudocode zeigt den Datenfluss zusätzlich über die intern indexierte Datenstruktur. Kein Target wurde ausgeführt; es gab keine Geräte-, Netzwerk- oder VM-Aktion.

## Träger und ELF-Metadaten

Das IPK ist ein `ar`-Archiv mit `debian-binary`, `control.tar.gz` und `data.tar.gz`. Paketmetadaten nennen `libpackbus` 1.0.3, `armhf`. Der relevante Code liegt im exakt extrahierten Paketpfad `rootfs/usr/lib/libpackbus.so.1.0.1`: 148,792 Byte, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. ELF32, little-endian, `ET_DYN`, ARM, EABI5, hard-float ABI, kein Entry-Point (`0x0`), GNU Build-ID `1e025c5f82908ba6d9f9676d2de99c0cf6e56a04`. Der Pfad steht als vollständiger Hash-/Metadatensatz in `artifact-inventory.tsv`.

## Loaderpfade und begrenzte Callsite-Befunde

- `SCPU_Download` bei REA-Adresse `0x1884c` (ELF-Symbolwert `0x884c`) dekompiliert zu `return 0;`. Der Exportname allein ist hier kein Beleg für den Dateilader.
- `SCPU_boot_slave` bei `0x1a470` öffnet `/dev/ttyKbus`, prüft den Dateideskriptor als TTY und ruft unter anderem `FUN_00019a78` auf. Direkter Caller-Befund für `FUN_00019a78`: ausschließlich `0x1a470` im Ghidra-Callgraph.
- `FUN_00019a78` bei `0x19a78` ist anhand seiner eigenen Logtexte als `scpu_boot_download_data` wiedererkennbar (Name nicht als ELF-Symbol behauptet). Die Funktion ruft `FUN_000197f0` auf, behandelt Schritt-/Baudratenfelder, schreibt Header/Prüfbyte/Nutzdaten, wartet auf Antwortbytes und vergleicht sie mit Tabellenwerten. `FUN_000197f0` hat Ghidra-Caller `0x19a78` und lädt für Index 0–10 Dateien oder zuvor abgelegte Daten.
- `FUN_000197f0` bei `0x197f0` liest Pfad und Länge aus einer mit `0x2c`-Schritt indizierten globalen Tabelle; `0xffffffff` führt zu `stat(path)`, danach werden Speicher reserviert und die Datei mit `open`/`read` eingelesen. Die Ghidra-Suche findet die drei Pfade bei `0x2d930`, `0x2d94c`, `0x2d968`. Die von Rizin beobachteten ELF-VA derselben Literale sind `0x1d930`, `0x1d94c`, `0x1d968`.
- Die öffentlichen `SCPU_boot_reset`-/`SCPU_boot_slave`-Namen sind im ELF mehrfach vorhanden; Funktionsnamen wurden daher nur zusammen mit exakten Adressen verwendet. Der tatsächliche Payloadpfad ist über die Adressfolge und nicht über Bezeichner allein ausgewertet.

Die für diese Daten abgefragten Tabellenbytes stehen in `loader-callsites.tsv`. Korrekte Zugriffsbedeutung aus `FUN_00019a78`: +12 Transferselektor; +20 Präfixbyte; +21 Ack-Flag; +32 XOR-Flag. Die voneinander getrennten Branches sind: wenn +20 gesetzt, Länge als vier bytegetauschte Bytes schreiben; sonst, wenn +32 gesetzt, Payloadbytes XOR-verknüpfen und ein Byte schreiben; andernfalls rohe Payload schreiben. Die Ack-Auswertung folgt nach jeder dieser Schreibstufen, sofern +21 gesetzt ist. L1 rows 0/5 raw; L2 rows 1/6 raw+Ack; L3 row 2 length, row 3 raw+Ack, row 7 length+Ack, row 8 raw, row 9 raw+XOR+Ack. Diese Stufenkonfiguration ist statisch belegt; tatsächliche Ausführung und Zielplatzierung bleiben offen.

Die Indizierung hier ist nur als beobachtete Codearithmetik beschrieben: die Funktion greift auf Einträge im Abstand `0x2c` zu; ein relativer Wortzugriff bei `+4` liefert den Pfadzeiger, `+8` die angeforderte Größe, `+12` den vom SPI-Zweig geprüften Selektor; separate Bytezugriffe bei `+20` (Präfix), `+21` (Ack) und `+32` (XOR) steuern die seriellen Stufen. Das sind Zugriffsoffsets der dekompilierten Funktion und gelesene Initialwerte, keine behaupteten Hersteller-Structnamen oder ABI-Definitionen.

Framingbeobachtung: der Präfixzweig bildet aus der Länge ein bytegetauschtes 32-Bit-Wort und schreibt vier Bytes. In den hier ausgewerteten Tabellen ist dieser Präfixschritt bei L3 row 2 und row 7 aktiviert. L2 length=266 (`0x10a`) und L3 length=16,598 (`0x40d6`) sind Dateigrößen, aber L2 schaltet den Präfixzweig nicht ein. Der Pseudocode belegt die Transformation, kein serieller Mitschnitt.

Checksummebeobachtung: der bedingte Ein-Byte-Zweig XOR-verknüpft alle Bytes des geladenen Puffers und schreibt das Ergebnis. L3 row 9 hat +32=1 und +20=0, daher konfiguriert diese Zeile den XOR-Zweig (neben +21 Ack). Der untersuchte Funktionskörper zeigt hier keinen CRC-Polynom-/Mehrbyte-CRC-Ablauf. Das ist ein statisch konfigurierter Einbyte-Prüfwert, nicht der Nachweis eines beobachteten oder vom Empfänger verifizierten Checksums.

Transferzweigbeobachtung: ein separater `type == 1`-Zweig konfiguriert SPI, schreibt eine L3-Länge und überträgt Puffer über `ioctl` in Blöcken bis `0x800`; der Fehlertext nennt den Boot-Code-Transfer. Das Selektionsfeld dieses Zweigs ist in den gelesenen statischen Tabellenzeilen null. Das ist positive Evidenz für vorhandenen SPI-Code, aber negative Evidenz für seine Auswahl durch die unveränderte statische Initialisierung. Nachträgliche Laufzeitänderungen wurden nicht untersucht.

Übergang: die serielle Route wartet mit `select`, liest die konfigurierte Antwortlänge und vergleicht Antwortbytes. Eine alternative Antwort kann gemäß Tabellenfeldern einen anderen Schritt indexieren; ansonsten wird beim unerwarteten Antwortwert mit Fehler beendet. Das belegt eine statische Ack-/Schrittsteuerung, keinen tatsächlich erfolgten Boot- oder Startübergang.

## C166-Korrelation, Alternativen und Restunsicherheit

**Beobachtung aus getrennten C166-Arbeiten:** Der abgeleitete Composite `XE164-composite-e00000.bin` (17,110 Byte, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`) war Gegenstand begrenzter C166-Analysen. WP-XE164-001 dekodiert 128 vier Byte lange `jmps`-Einträge im Composite-Fenster `0x200..0x3ff`; der korrigierte bytegenaue Vergleich richtet dieses Fenster auf L3-Quelloffset `0x000..0x1ff` aus und findet 128/128 Zeilen sowie 512/512 Bytes identisch. WP-XE164-003 untersucht einen Startbereich und Tabellen bei Datei-Offsets `0x33a8`/`0x0b84`, mit beobachteten Tags 1, 5, 6, 7. Diese Befunde gelten für die jeweiligen Dateien/Offsets/Replaykonfigurationen.

Die vorhandene Replaybeschreibung nennt Seeds bei Analyseadressen `0xE00000` (L1-Kandidat), `0xE00020` (L2-Kandidat), `0xE00200` und `0xE00400`, mit `BinaryLoader`-Basis `0xE00000`; in diesem WP werden die beiden zusätzlichen Seeds semantisch nicht zugeordnet. Die Replaybeschreibung weist außerdem separat darauf hin, dass ein direkter L3-Import bei Basis `0xE00200` kein Composite-Replay ist. Das sind dokumentierte Analysekoordinaten/Seeds. Sie sind keine beobachteten Ziele des ARM-Transfers und bestätigen keine physische/virtuelle Platzierung.

**Korrelation — HYPOTHESE:** ARM-Tabellen konfigurieren getrennte L1/L2/L3 Datei- und Übertragungsstufen; unabhängig davon stimmt Composite `0x200..0x3ff` exakt mit L3-Quelle `0x000..0x1ff` überein. Das passt zu einer Loader-/Payload-Kette. Es beweist weder, dass ARM den Composite erzeugt, noch dass L3-Bytes übertragen oder auf der in C166 verwendeten Analysebasis `0xe00000` platziert werden.

**Negativ / OFFEN:** Der untersuchte C166-Startcode hat keinen sichtbaren Parser für die ARM-seitig beobachteten 4-Byte-Längenpräfixe oder das XOR-Prüfbyte. Die betrachtete C166-Passage liest stattdessen tagbasierte Recordfelder; ein gleichartiger Checksummentest ist in den referenzierten bounded Berichten nicht belegt. Dies gilt nur für diese Ausschnitte; andere C166-Funktionen/Loaderphasen sind nicht ausgeschlossen. Auch die 128 `jmps`-Einträge belegen keinen ARM-Transfer oder dessen Zielplatzierung.

Alternativerklärungen: die Pfade können für verschiedene Revisionen oder alternative Bootschritte hinterlegt sein; die table-indexierten Zustände können zur Laufzeit geändert werden; der SPI-Zweig kann andere Hardware-/Konfigurationszustände bedienen; von Ghidra nicht aufgelöste Abhängigkeiten und nicht aufgelöste indirekte Kontrollflüsse können zusätzliche Caller-/Transferpfade verbergen. Die genaue Relation zwischen L1/L2/L3, Composite-Adressen, C166-Segmentierung, Loaderzustand und Start wird durch diese statische Analyse nicht entschieden. FW31-Aussagen werden nicht abgeleitet.

## Evidence, Reproduzierbarkeit und Status

Die Evidence-IDs stehen in `loader-callsites.tsv`; der REA-Bundle-Export liegt als `rea-evidence-bundle.json` vor. Er enthält 19 Records, alle zum extrahierten ELF-Hash `3b7b7ca4…4bc5d6`; es sind keine fremden Artefakt-/Provider-Records im exportierten Bundle enthalten. SHA-256 der JSON-Datei ist in `SHA256SUMS` und unten als generierte Datei aufgeführt.

| Frage | Status |
|---|---|
| Exakter Loaderträger im IPK samt ELF-Identität | VERIFIZIERT |
| Pfadreferenzen und Datei-/Schritt-Ladefunktion | VERIFIZIERT (statisch) |
| Konkrete Übertragung einer Nutzlast auf einem Gerät | OFFEN; keine Laufzeitmessung |
| L1/L2/L3 konfigurierte Rohdaten-, Längenpräfix-, XOR- und Ack-Stufen | VERIFIZIERT (Code + statische Tabellenwerte); konkrete Ablaufwahl/Zielwirkung OFFEN |
| C166-Zielplatzierung/Start durch diese ARM-Route | OFFEN |

Keine unabhängige Prüfung oder Worker-Ausführung wird behauptet.

## Erzeugte Dateien

Abgabedateien: `report.md`, `artifact-inventory.tsv`, `loader-callsites.tsv`, `correlation.tsv`, `rea-evidence-bundle.json`, `SHA256SUMS`. Extrahierte Kopien und Archivmitglieder zur Offlineanalyse liegen ebenfalls ausschließlich in diesem Worker-Ausgabeverzeichnis. Alle regulären Dateien dort außer dem Manifest selbst sind in `SHA256SUMS` erfasst.
