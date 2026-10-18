# Fachliche Übergabe des Ergebnisstands

Stand der konsolidierten Offlineanalyse: 18.10.2026. **444 Evidence-IDs / 303 Funktionszuordnungen / zwölf CSV-Spalten.** Die Analyse ist unvollständig; Geräte-, VM-, Netzwerk- und native Herstellerprogrammausführung waren in dieser Fortsetzung NOT_RUN. Vorhandene Ergebnisse bleiben an Originalversion, Hash, Konfiguration und Scope gebunden.

## Tragfähige Ergebnisse

1. Die ursprüngliche Provider-Tabelle und die in Dal kopierte Tabelle sind getrennt. Ein nachträglich überschriebener Eintrag verhindert eine pauschale Gleichsetzung. Die Bedingung C=T+0x110 gilt genau einmal. Der ausgewählte selector15-Pfad ist unter expliziten Speicher-/Listen-/Registerbedingungen statisch verträglich; tatsächliche Managerobjekte und Runtimebindung bleiben OFFEN.
2. Provider-/Backendpositionen und ausgewählte libffi-Aufrufe sind quellengebunden. Die Rückkehrprämisse des ausgewählten FFI-Pfads umfasst 15 später gelesene Wörter; die ältere Vier-Wort-Annahme reicht nicht. Das ist kein allgemeiner ABI-Nachweis.
3. SSC-Anfangszeilen, Update-/Open-Gates und ausgewählte erzeugte Kopierdatensätze sind untersucht. Drei reale Anfangszeilen bilden auf 1/2/3 ab. Ein isolierter GetCnf-Erfolg beweist keinen ganzen Update-Durchlauf. Numerische Allokationsintervalle allein begründen keinen tatsächlichen Speicherfehler.
4. Codec-Blätter und ausgewählte Modelle belegen lokale Bytefolgen, Aliasreihenfolge, Status-/Längenauswahl und NEON-Writebacks. Bei Noargs wird das Halfword an Ausgabe+2 vor den Opcodebytes geschrieben. Synthetische Puffer sind keine echten Geräteantworten.
5. Der untersuchte Kind4-Append liegt auf dem J>11999-Zweig und führt über einen Logger. Eine reale Verbindung dieses Appends zu einem gültigen Kind4-Verbraucher ist nicht belegt.
6. SCPU- und SPI-Aufrufpositionen sowie die numerischen ioctl-Werte 0x40184b01 / 0x401c4b02 / 0x40084b03 und ihre 24-/28-/8-Byte-Argumentbilder sind untersucht. Dies ist noch kein Kernel-UAPI-Vertrag. Das lokale SPI_Init-Blatt besteht aus MOV r0,0 und BX LR; tatsächliche Bindung bleibt Voraussetzung.
7. Die Bootquelle enthält zusätzlich eine serielle Datei-/Termios-/Write-/Select-/Read-/Close-Kette. Der Firmware-Orchestrator war bereits im älteren Paket370 erfasst; die spätere engere Analyse und der Aufrufer-/Reader-Abgleich präzisieren dessen Einbindung. Zustandsschreibvorgänge bleiben an gültige aktuelle Register, Frames und Speicherinhalte gebunden.
8. Vier exakt aus dem FW31-Image gebundene Kernelmetadatendateien nennen den Built-in-Kandidaten spi_kbus. Eine unabhängige frische Extraktion bestätigt die Bytes. Aktiver Kernel, konkrete Major-Nummer, Gerätezuordnung, ioctl-Handler und tatsächliche Bindung bleiben OFFEN.
9. Die Datei /boot/linux ist mit Inode50, 8213856Bytes und SHA-256 f6e03d6452e4648cd86f58ff5c869af0ebdcc6e8f3123458c73d6e81ccfede65 gebunden. uImage-CRCs und innerer zImage-Header sind geprüft. Ein LZO-Kandidat ist sichtbar, wurde aber nicht dekomprimiert.
10. Der serielle Konfigurationshelfer ist als begrenzter Rohquellenslice untersucht: 120Byte lokale Nullung, sechs gesicherte Wörter, 144Byte Gesamtframe, vier Konfigurationsaufrufe plus memcmp. Spätere FD-/Buffer-/Speedwerte benötigen erhaltene aktuelle Register; ein konkreter Baudwert oder Termios-Structvertrag wird nicht erfunden.

## Fertig, noch nicht in die 444 IDs integriert

- [WP440](work/worker/WP-XE164-440/report.md): begrenzte Suche nach vorhandenen Host-Decodern. Kein kompatibler, validierter LZO-Decoder gefunden; lokale Bibliotheksquellen und ein anders formatiertes Beispiel sind kein geprüfter Decoder für den Kandidaten.
- [WP441](work/worker/WP-XE164-441/report.md): zehn reguläre DTBs an Inodes14–23. Inode24 ist ein Verzeichnis; die anfängliche Annahme von elf DTBs wurde korrigiert. Kandidatenzeichenfolgen sind in allen zehn Dateien vorhanden. Knoten-/Propertyzuordnung und aktiver Gerätebaum bleiben offen.
- [WP442](work/worker/WP-XE164-442/report.md): unabhängiger begrenzter Inventar-/Hash-/Zeichenfolgenreview zu WP441. Keine neue DTB-Dekodierung und keine Runtimebeobachtung.

## Nächste fachliche Fragen

- Tatsächliche Manager-/Provider-/Backendidentität und erreichbare Aufrufzustände binden.
- Opaque Aufrufwirkungen, Lebenszyklus, Synchronisation, Zeit-, Diagnose- und Fehlerpfade vervollständigen.
- DTB-Zeichenfolgen anhand eines gebundenen Formats konkreten Knoten/Properties zuordnen.
- Vorhandene SDK-Quellen auf geeignete Decoder-/FDT-Werkzeuge und Treiberschnittstellen prüfen; FW30-Quellen qualifizieren keine FW31-ABI.
- Erst nach validierter statischer Kerneldekodierung konkrete Handler und UAPI untersuchen.

Das Forschungsende dieses Laufs war eine vereinbarte Kontingentgrenze, keine fachliche Fertigmeldung. Die Sicherung erteilt keine Geräte-, Firmware-, Kernelersetzungs- oder Busumschaltfreigabe. Der bestehende Repository-Sicherheitsvertrag bleibt maßgeblich.
