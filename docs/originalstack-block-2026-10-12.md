# Originalstack-Block: Mapping, Vertrag und eigener ADI-Adapter

Stand: 12.10.2026. Ausgangsrevision `89f2e57a1879be144160d51e17c3ed0fd75d235b`, Branch `research/originalstack-m1-m2`, Draft-PR #2. Die endgültigen Quellen sind über das [30-Dateien-Manifest](../evidence/source-manifest.sha256) gebunden; Tests und CI werden gegen den daraus entstehenden Commit geprüft. Bereinigte Einzelbelege: [Block-Evidence](../evidence/originalstack-block-validation-2026-10-12.json).

## Ergebnis

**VERIFIZIERT / PASS:** frische lesende Referenzbindung, unverändert kompilierter und nativ gemappter Offlinekandidat, 34-Slot-ABI-Sonde sowie eigener digitaler ADI-Adapter mit ausgeführten ARM-Vertragstests. Der eigene Adapter lief sowohl direkt im eigenen Harness als auch als dynamisch geladene Ersatzbibliothek. **BLOCKED / NOT_RUN:** der originale WAGO-Verbraucher beziehungsweise die virtuelle Originalruntime wurden noch nicht mit diesem Adapter ausgeführt. Diese Nachweisstufen bleiben getrennt.

B+C bleibt die Forschungsentscheidung: originale Runtime, nativer I/O-Manager und originale WAGO-I/O-Treiber bleiben erhalten; der virtuelle Ersatz sitzt unter diesen Komponenten. Der Adapter erzeugt keine CODESYS-Manager-, Connector- oder Mappingobjekte. Fehlende interne CODESYS-Header sind für diesen Weg keine pauschale Voraussetzung.

## Frische Referenzbindung

Der Integrator prüfte ausschließlich das lokal gebundene Referenzgerät über die vorhandene exakte Zielrichtlinie und den gepinnten SSH-Schlüssel. Ein frischer lokaler Kernel-Test bestätigte die Egress-Sperre des eigenen Werkzeugprozesses; ausgeschlossene Ziele wurden nicht kontaktiert. Es gab keine globale oder VM-weite Firewalländerung.

**VERIFIZIERT:** Modellmarker 750-8213, Firmwaremarker 04.09.01(31), Kernel `6.6.94-rt56-w05.08.02`. Die sechs Hashes von Runtime, DAL, IoDrvDal, IoDrvKbus und den beiden geprüften Konfigurationen stimmen vor und nach der Arbeit mit der gesicherten Baseline überein. Der Runtimeprozess und sein gelöschter Arbeitsordner bestehen unverändert. Kein Neustart, Download, Start/Stop, Reset, Treiberwechsel oder zweiter K-Bus-Master wurde angefordert.

Der separate CODESYS-Keep-Login beobachtete `stop / program_loaded`; die abschließende originale Metadatenabfrage nennt weiterhin die vorherige Anwendung. Letztere liefert keinen Zustand, deshalb wird STOP ausschließlich dem Keep-Lauf zugeschrieben. Der aktive Referenzprojektbaum und die physische Klemmenliste bleiben **OFFEN**: sichere Datei-/Sysfs-Metadaten liefern hier keine Liste. Unsichere EEPROM-Abfragen und ein neuer ADI-Busmaster wurden nicht als Inventarersatz gestartet. Die elektrische Trennung bleibt Eigentümeraussage, ohne eigene Messung.

## Gemappter Offlinekandidat

Der [Mappingbericht](codesys-mapped-2026-10-12.md) bindet den unveränderten ST-Quelltext, IDE, Profil, Compiler 3.5.21.50, Controllerbeschreibung 6.4.6.11, LocalBus 2.1.0.1 und Terminalbeschreibungen 2.0.0.14 an Hashes. Die vier tatsächlich verwendeten Device Descriptions wurden in der VM frisch gehasht.

| Native Zuordnung | Export des eigenen Offlineprojekts |
|---|---|
| 750-1405 `_IN` → `Application.PLC_PRG.InputWord` | `%IW1`, 16 Bits `%IX2.0` bis `%IX3.7` |
| 750-1504 `_OUT` → `Application.PLC_PRG.OutputWord` | `%QW0`, 16 Bits `%QX0.0` bis `%QX1.7` |

**PASS:** Build und Codegenerierung mit null Fehlern/Warnungen; LocalBus und beide Terminals aktiv; `OutputPermit` initial FALSE. Ein eigener Wiederöffnungslauf bestätigte die gespeicherten nativen Zuordnungen, 16 Unterelemente je Kanal und keine kollidierenden Unterelementzuordnungen. Der erneute CSV-Export ist bytegleich, das Projekt vor/nach dem Leselauf hashgleich. Die privaten PROJECT-/APP-/CRC-/CSV-Dateien wurden mit Größe und Hash zurückübertragen; es erfolgte kein Zieldownload. Der erste fehlgeschlagene Build mit zwei unvollständig qualifizierten Mappingausdrücken bleibt als FAIL dokumentiert.

## Untere Grenze und eigener Adapter

Die [Vertragsmatrix](adi-contract-2026-10-12.md) bindet echte Header an den byteidentischen DAL-Provider und die abweichenden tatsächlichen FW31-Verbraucher. Sie dokumentiert alle 34 Signaturen/Slots und eine statisch belegte Verwendungsunion von 21 Slots, einschließlich Init/Enumeration/Open, zyklischen Bit-/Bytepfaden, Zustandswechseln und Watchdogs. Konfiguration III, Terminal-info32, Kapazitäts-/Fehlerregeln und die digitale Modulvergleichsabkürzung für 9001/9002 sind weiter geschlossen. Untersuchte Aufrufstellen sind keine vollständige Start-/Nebenläufigkeitsgarantie.

Der [eigene Adapter](../tools/adi_digital_adapter.c) verwendet echte, ausschließlich private Header. Die gebundenen Modulvergleichswerte stammen aus den Gerätebeschreibungen; DeviceId, 2-Byte-Prozessabbilder, Packung und Ausgabepolitik sind ausdrücklich eigene Modellentscheidungen. [ADR-0002](adr-0002.md) trennt diese Entscheidungen von Herstellerverhalten. Das Modell stellt Signale bereit und verarbeitet Ausgangsframes; es enthält keine SPS-Entscheidungslogik.

**PASS, eigener Scope:** alle 34 Signatur-/Offsetasserts kompilieren mit ARMHF GCC 14.2.0. Adapter und Harness bauen mit aktivierten Assertions. Der ausgeführte Harness prüft Enumeration, Konfigurationsgrenzen, Terminaldaten und Kapazitäten, Eingangs-Latching, vollständige atomare Ausgangsframes, ungültige Transfers, getrennte angeforderte/wirksame Ausgänge, geschlossene Initialwerte, Stop/Close, Freigabewechsel und logischen Watchdogablauf. Ein neuer vollständiger Frame ist nach Gateverlust erforderlich. Unbekannte Operationen, unmodellierte Register/UIDs und Callbacks liefern explizite Fehler.

Zusätzlich wurde eine ARMHF-Bibliothek mit SONAME `libdal.so` gebaut und vom eigenen ARM-Harness dynamisch geladen. Die eigene Bibliothek benötigt nur libc; der Getterexport ist tatsächlich vorhanden. Das ist ein Provider-/Eigenclient-Nachweis, kein Originalmanager- oder M3-Lauf.

Modellzeit ist ausschließlich die manuell fortgeschaltete Mikrosekundenuhr des Adapters. Runtime-, Bus- und Hostzeit sind nicht damit qualifiziert. Der Adapter ist auf eine sequenzielle Einzelinstanz begrenzt; es gibt keine Callback- oder Multithreadgarantie.

## Praktische Isolation und Prüfung

Beide konkreten ARM-Roots wurden mit dem bestehenden Launcher geprüft: privates Read-only-Dateisystem, getrennte User-/Netz-/Mount-/PID-/IPC-Namespaces, keine Capabilities, `no_new_privs`, keine Hostdatei, Hardwarepfade, Host-D-Bus- oder Docker-Sockets. Eigene positiv geprüfte Hostlistener blieben unerreichbar. Die synthetische Negativkontrolle fügte ausschließlich eine Gastdatei hinzu; die Sonde meldete erwartungsgemäß FAIL/Exit 1. **PASS** gilt für die Erkennung dieser künstlichen Verletzung. Es wurde kein Hostmount hinzugefügt und kein ausgeschlossenes Gerät kontaktiert.

Originaler GNU-Lader und libc liefen mit den eigenen Programmen. Originale WAGO-Runtime, I/O-Treiber, DAL und packbus wurden dabei nicht geladen oder ausgeführt. Die vorhandenen Prozesslimits sind kein aggregierter cgroup-Vertrag; diese Prüfung qualifiziert die konkreten eigenen Roots, keine beliebige Firmware.

**PASS:** 99 hardwarefreie Python-Tests unter 3.13.5. CI benötigt weiterhin keine Herstellerheader oder Hardware und führt diese Suite aus; die C-/IDE-Prüfungen bleiben separate, hashgebundene lokale Evidence. Integratorprüfung ist **Self-Review**. Ein tatsächlicher Luna-Worker mit low prüfte den Mappingcode und die privaten Metadaten/CSV unabhängig; ein Sol-Worker mit high prüfte gezielt ABI und Adapter. Konkrete Adapter-/Harnessbefunde wurden vor dem Lauf behoben. Kein Reviewer führte Geräte- oder Firmwaretests aus.

Die Engineering-VM wurde nach Nutzung wieder auf Datenträger pausiert. Eigene Session inaktiv; ein separater Statuslauf bestätigte `stopped / saved_to_disk`.

## Präziser Restblock

1. Die deklarierte Offlinekonfiguration an den tatsächlich ausgewählten originalen Start-/Hook-/Scanpfad binden: TCM-Auswahl, Diagnose-/Push-Auswertung, weitere Aufrufe sowie Ende-/Fehlerreaktionen. Der generische IoDrvDal ignoriert beobachtete zyklische Rückgaben; Kbus verwirft End-Rückgaben. Fehlererkennung im Eigenclient genügt deshalb nicht.
2. Dynamische Originalkomponenten und die Kbus-D-Bus-/Diagnose-/Async-Dienste in einer konkreten privaten Instanz schließen. Die statische DT_NEEDED-Verfügbarkeit enthält keine fehlenden Dateien, beweist aber keine vollständige dlopen-/Symbol-/Dienstauflösung. Originale Async-/Zeit-/Retainpfade dürfen keine physische packbus-/UIO-Anbindung behalten.
3. Für tatsächlich erreichbare parallele oder registrierte Callbackpfade den Lifecycle-/Synchronisationsvertrag belegen und den Adapter erweitern. Sein jetziger sequentieller Scope reicht dafür nicht.
4. Nutzungsrechte und gültige Lizenzzuordnung für die konkrete virtuelle Originalruntime binden, ohne Identitätskopie oder Bypass. Dann Originalverbraucher-Init/DI/DO plus negative Kontrolle; erst danach gemappte IEC-M4-Abnahme mit Stop/Restart/Watchdogfällen.

Physische Referenzbestückung und der fremde aktive Referenzprojektbaum bleiben eigene offene Inventarpunkte. Sie sind keine Voraussetzung, um den eigenen Offlinebaum weiterzuentwickeln. Keine Installation des virtuellen Adapters auf dem Referenzgerät und kein Merge wurden durchgeführt.
