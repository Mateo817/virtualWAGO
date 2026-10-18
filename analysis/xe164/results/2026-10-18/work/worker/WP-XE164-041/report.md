> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-041 — Kontrollfluss vor E01FFC

## Ergebnis

**VERIFIZIERT (statisch, syntaktische C166-Dekodierung):** Im Bereich der
Dateioffsets `0x1F98..0x1FFB` dekodiert Rizin ab `0x1F98` eine lineare Folge
ohne bedingte oder unbedingte Sprunginstruktionen. Bei `0x1FCA` liegt ein
direkter `CALLS`-Aufruf nach `0xE004B8`; die lineare Folge setzt beim
Rückkehrpunkt `0x1FCE` fort und endet bei `0x1FFA` mit `RETS`. Der isolierte
Aufrufer bei Dateioffset `0x3646` enthält `CALLS 0xE01F98` (`DA E0 98 1F`).
Das belegt diesen Aufrufpfad syntaktisch, nicht dessen Laufzeitverhalten.

Die Tabelle [exact-tables.csv](exact-tables.csv) führt jede Instruktion samt
exakter Bytefolge auf. Für den Zielbereich wurden genau 100 Bytes ab Offset
`0x1F98` gelesen; die Dekodierung wurde ebenfalls auf 100 Bytes begrenzt. Der
Nachbar `E01FFC` wurde nicht eingelesen oder untersucht.

## Beobachtungen und Nachweis

- Eingabe vor Analyse geprüft: 17,110 Bytes; SHA-256
  `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- REA zuerst: GNU objdump meldete Binutils 2.44 und beworbene BFD-Ziele ohne
  C166. Diese Lücke begründet den dokumentierten Rizin-C166-Fallback.
- Fallback-Profil aus vorherigem Rizin-Laufprotokoll: Rizin 0.9.1,
  Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. Aktuelle lokale
  Versionsabfrage bestätigte dieselbe Version und denselben Commit.
- Rizin-Aufruf: `e scr.color=0; e io.va=false; e asm.arch=c166;
  e asm.bits=16; e asm.cpu=xe164; e cfg.bigendian=false; px 0x64 @ 0x1f98;
  pD 0x64 @ 0x1f98`. Exit-Code 0, leere stderr, keine Ausgabe abgeschnitten,
  Eingabe unverändert; SHA-256 danach identisch.
- Caller-Abfragen begrenzten sich auf die eine Instruktion bei `0x3646` und
  anschließend exakt deren vier Bytes. Rizin meldete `CALLS 0xE01F98`;
  Dateibytes `DA E0 98 1F`.
- Die drei einschlägigen Rizin-Beobachtungen sind als vollständige
  REA-Evidence-Datensätze im [finding-only Bundle](rea-evidence-bundle.json)
  enthalten. Das Bundle enthält keine fremden bzw. nicht zu diesem Befund
  gehörenden Records.

## Alternative und Restunsicherheit

**HYPOTHESE (Alternative):** Eine lineare C166-Dekodierung eines Bytebereichs
beweist allein nicht, dass jeder dekodierte Bytewert auf jedem Ausführungspfad
als Instruktion ausgeführt wird. Überlappende Einstiege oder eine abweichende
Codierung/Interpretation können mit dieser gezielten statischen Abfrage nicht
ausgeschlossen werden. Der direkte Aufruf bei `0x3646` stützt den Einstieg bei
`0x1F98`, beweist aber keine Caller-Eindeutigkeit.

Die Dekodierung stammt von einem einzigen C166-Disassembler. Es erfolgte kein
zweiter unabhängiger Decoderabgleich, keine Runtime-/Emulator-/Hardwareprüfung
und keine semantische Interpretation der Operanden. Die Bedeutung des Aufrufs
bei `0x1FCA`, der Bitoperationen und der adressierten Speicherstellen bleibt
außerhalb dieses Befunds. E01FFC und alle weiteren Caller wurden ausgeschlossen.

## Status

| Gegenstand | Status | Geltungsbereich |
|---|---|---|
| Eingabegröße und SHA-256 | VERIFIZIERT | Eingabe vor und nach den REA-Aufrufen |
| Bytefolge und Rizin-Dekodierung | VERIFIZIERT | `0x1F98..0x1FFB`, Rizin 0.9.1 / C166 / 16 Bit / xe164 / little endian |
| Linearer Kontrollfluss mit direktem Call und Return | VERIFIZIERT | Statische Dekodierung ab `0x1F98`; kein Laufzeitnachweis |
| Aufruf von `E01F98` am isolierten Caller `0x3646` | VERIFIZIERT | Genau eine Instruktion plus deren vier Bytes |
| Eindeutigkeit aller Caller / Laufzeit-Ausführung | OFFEN | Nicht untersucht bzw. durch Offline-Statisik nicht belegt |

## Erzeugte Dateien

| Datei | Zweck |
|---|---|
| `report.md` | Befund, Methode, Status und Unsicherheiten |
| `exact-tables.csv` | Exakte Instruktions- und Caller-Tabelle |
| `rea-evidence-bundle.json` | Kanonisches finding-only REA-Bundle, drei Datensätze |
| `validate.py` | Prüft Hashes, Umfang, Byteabdeckung und Bundle-Record-Auswahl |
| `SHA256SUMS` | SHA-256 der vier vorgenannten Dateien |

Worker-Eigenprüfung ist erfolgt. Root Self-Review steht noch aus; es wird kein unabhängiger Review behauptet.
