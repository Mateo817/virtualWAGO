> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-370 — FW31: Loadercode, Starttabelle und Bytekandidaten

Root **Self-Review**. **VERIFIZIERT** sind die konkreten Dateiidentitäten, die frisch erfassten Code- und Tabellenbytes sowie die berechneten Bytekandidaten. Ablaufwahl und E00000-Platzierung bleiben **HYPOTHESE/OFFEN**. **PASS**: Hashes, Quellbytes, Tabelle und Arithmetik. Native Ausführung, Runtime, VM, Gerät und Netzwerk: **NOT_RUN**.

Die FW31-Extraktion WP310 liefert libpackbus.so.1.0.1 mit 148.792 Byte und SHA-256 3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. WP335 liefert L1/L2/L3 aus den Inodes 782/783/784 mit 32/266/16.598 Byte. Hier werden alle vier Dateien vollständig mit ihren Kopien aus dem älteren WP004-IPK verglichen: jeweils bytegleich. Das IPK trägt die Paketversion 1.0.3, die Bibliotheksdatei den Namen 1.0.1. Damit ist die Identität dieser Artefakte belegt, keine allgemeine Gleichheit von Firmwareimages, Konfigurationen, Kernel oder ABI.

Nach frischer Metadatenabfrage wurden 1.004 ARM-Instruktionswörter aus der FW31-Datei erfasst: Reader bei ELF 0x97f0 mit 588 Byte, Orchestrator bei 0x9a78 mit 2.380 Byte und SCPU_boot_slave bei 0xa470 mit 1.048 Byte. Der Orchestrator besteht aus [0x9a78,0x9e78) und [0x9f24,0xa470); die 172 Byte dazwischen werden nicht als Code gezählt. E014/WP004 betrifft denselben ELF-Hash. Dieses Paket übernimmt keine alten Ausführungs-PASS oder verworfenen Pseudocodeaussagen.

Die Reader-Gleichung 0x9848 + word[0x9a40] = 0x335c4 bindet elf initiale Datensätze mit je 44 Byte an ELF [0x335c4,0x337a8), Datei [0x235c4,0x237a8). Beobachtete Positionen: Pfad +4, Größenwort +8, Selektor +12, Präfixbyte +20, Ack-Byte +21, XOR-Byte +32, Antwortwort +24 und Antwortanzahl +28. Alle initialen Selektoren sind null. Neun Pfadfelder haben R_ARM_RELATIVE. Der Validator rekonstruiert Ghidras Fixups aus den rohen Relokationen und vergleicht die gesamten 484 REA-Tabellenbytes. Analysewerte sind keine Laufzeitzeiger.

Die statischen Dateizeilen konfigurieren:

- 0/5: L1, explizit 32 Byte, Rohdaten.
- 1/6: L2 mit Größensentinel ffffffff, Rohdaten mit Ack a0 beziehungsweise a1.
- 2/7: vier REV-transformierte L3-Längenbytes; Ack nur in 7.
- 3/8: L3-Rohdaten; Ack nur in 3, Antwortwort 42.
- 9: ein XOR-Byte mit Ack 81. Die Rohdaten gehören zur separaten Zeile 8; Zeile 9 sendet sie nicht erneut.
- 4/10: kein Dateipfad; keine weitergehende Bedeutung wird zugewiesen.

Die initialen Selektoren wählen den vorhandenen SPI-Zweig mit Selektor 1 nicht aus. Laufzeitänderungen und tatsächlich erreichte Zeilen bleiben offen.

Die Wörter an ELF 0x9bd0/0x9bdc/0x9be8/0x9f24 binden die Feldzugriffe; REV bei 0x9bf8 und EOR bei 0x9ffc binden die Transformationen. Aus den konkreten FW31-L3-Bytes folgen das Kandidatenpräfix 00 00 40 d6 und XOR-Byte 83. configured-byte-candidates.json enthält den Hash der hypothetischen Folge Präfix + L3 + XOR. Es wird weder ein Mitschnitt behauptet noch eine weitere Payloadkopie geschrieben.

Write-Rückgaben, Antwortbytes, Teilübertragungen, Timing, Bootkonfiguration, Zielausführung und Speicherplatzierung sind damit nicht belegt. Die frühere passende C166-L2-Handschlaganalyse E018 kann mit den nun bytegleichen Dateien verglichen werden; Derivat/SFR-Bezug und E00000-Platzierung bleiben offen. Geräteschnittstellen und Resetpfade erscheinen nur als gelesene Artefaktdaten. Es fand kein Firmwaredownload, Reset oder physischer Versuch statt.
