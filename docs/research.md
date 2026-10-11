# Forschungsergebnisse und Machbarkeitsentscheidung

Stand: 11.10.2026. Dies ist die öffentliche, bereinigte Zusammenfassung der vorhandenen Studie, keine neue Hardwaremessung. Quellenkennungen beziehen sich auf [sources.md](sources.md). Private Projektinventare und vollständige Evidence verbleiben im lokalen Übergabepaket. Die nachfolgende Original-ELF-/Headeranalyse steht in [abi-research-2026-10-11.md](abi-research-2026-10-11.md), der aktuelle Geräte-/ABI-Stand in [reference-abi-2026-10-11.md](reference-abi-2026-10-11.md). Die erste Offline-/Verbindungsetappe bleibt in [execution-2026-10-11.md](execution-2026-10-11.md) dokumentiert.

## 1. Ziel und Ergebnis

Eine virtuelle PFC200 soll nach Möglichkeit originale IEC-Logik, I/O-Mapping und WAGO-Gerätebaum verwenden. Die virtuelle Anbindung muss unterhalb der Anwendung liegen. Ein OPC-UA-Simulator oder ein in ST eingebautes Anlagenmodell erfüllt diesen Hardwareemulationsnachweis nicht.

**HYPOTHESE / bevorzugte Forschungslinie:** Originaler ARM-Userspace mit originaler Runtime und möglichst originalen WAGO-I/O-Komponenten kann an einer begrenzten Hardwareabstraktionsgrenze virtualisiert werden. **OFFEN:** Austauschbarkeit dieser Grenze in der tatsächlich eingesetzten Firmware. **NOT_RUN:** Original-Runtimeboot und Akzeptanz virtueller Klemmen. Ein fertiger Emulator wird nicht behauptet.

## 2. Belegte Referenzarchitektur

Öffentlich analysierter SDK-Snapshot: `FW30-V04.08.09`, Commit `252209115885442bac7359a2ff1cfa4efb3a9c84`. Dieser Referenzstand ist nicht automatisch die Firmware des neuen Geräts. [S11]

Die Plattformkonfiguration nennt ARMv7, Hard-Float, `arm-linux-gnueabihf`, Cortex-A8-Optimierung, AM335x-DTS-Dateien, barebox/MLO und Linux. Der Snapshot nennt glibc 2.35, eine Toolchainprüfung auf 11.3.1 sowie Kernel 6.6.94 mit RT-Patch rt56. Das sind **VERIFIZIERTE Buildangaben**, keine Messung einer FW31-Installation. [S12]

Das CODESYS-Komponentenmenü nennt `IoDrvDal`, `IoDrvKbus`, `TscIoDrvKbus`, K-Bus-Async-Komponenten sowie Zeit-, Retain- und Lizenzkomponenten. Das libpackbus-Rezept nennt unter anderem `/usr/lib/dal/libpackbus.so`, `/etc/specific/kbusconf.xml` und `XE164L*.bin`. Geräteverlinkung und Konfiguration enthalten `/dev/kbus0`, `/dev/ttyKbus` und WAGO-Sysfs-Informationen. [S15–S17]

```text
IEC-Anwendung + Gerätebaum + I/O-Zuordnung
                 |
        CODESYS-Runtime / I/O-Manager
                 |
    WAGO-I/O-Komponenten und Async-Helfer
                 |
     ADI / DAL: zu prüfende Ersatzgrenze
                 |
             libpackbus
                 |
    Linux-Gerätepfade / Busanbindung
                 |
          K-Bus / I/O-Module
```

Dieses Diagramm rekonstruiert Komponentenbeziehungen. Es ist kein vollständiger Callgraph des neuen Geräts. Insbesondere Runtime → ADI/DAL, Async-/Registerzugriffe und zusätzliche Hardwareabhängigkeiten müssen anhand des konkreten Bestands belegt werden.

## 3. Konkreter API-Einstieg statt erfundener ABI

Das offizielle K-Bus-C-Beispiel inkludiert `dal/adi_application_interface.h`, verwendet `tApplicationDeviceInterface`, `tDeviceInfo`, `tDeviceId` und ruft `adi_GetApplicationInterface()` auf. Beispiele zeigen `Init`, `ScanDevices` und `GetDeviceList`. Das belegt eine reale API-Verwendung, nicht das vollständige aktuelle binäre Layout. [S18–S20]

Vor einem Shim sind Header, Export-/Importsymbole, ELF-Attribute, DT_NEEDED, Konfiguration, Funktionszeigerreihenfolge, Strukturgrößen, Packing, ARM32-Typbreiten, Fehlercodes, Callback-Lebensdauer und Synchronisationsvertrag zu bestimmen. Compiler-/Header-Abgleich muss auf dem passenden ARM-Ziel erfolgen. Ein x86-64-Structdump qualifiziert keine ARM32-ABI.

Der SDK-Bestand enthält Buildrezepte für proprietäre Komponenten mit Pfaden unter `wago_intern` und Wiederherstellung aus Header-/Binärpaketen. Daraus folgt gerade nicht, dass vollständiger DAL-/K-Bus-/Runtimequellcode offenliegt. Originalpakete dürfen offline analysiert werden, soweit die konkreten Nutzungsrechte dies erlauben; Lizenzidentitäten werden nicht nachgebildet oder umgangen. [S13, S16]

## 4. Variantenvergleich

| Variante | Stärke | Hauptunsicherheit | Entscheidung |
|---|---|---|---|
| A: Originalfirmware mit Boardemulation | Höchste potenzielle Systemtreue | AM335x-/WAGO-Peripherie, K-Bus, Boot und Identitäten | Zurückstellen |
| B: ARM-Userspace in isolierter Ausführungsumgebung | Originale Binaries bleiben erhalten | Loader-/Kernel-/Dienst-/Geräteabhängigkeiten | Träger für C |
| C: Belegte ADI-/DAL-/Treibergrenze ersetzen | Direkter Ansatz unterhalb der Anwendung | ABI, Initialisierung, Async-/Diagnosepfade | Bevorzugter begrenzter PoC |
| D: Virtual Control mit eigenem I/O-Treiber | Alternative virtuelle Runtimeplattform | Anderes Ziel, WAGO-Libraries und Gerätebaum | Getrennter Ausweichpfad |
| E: Hybrid mit Referenztraces | Qualifikation einzelner Verhaltensverträge | Reale Fehler-/Timingabdeckung | Ergänzend |

Die Wertung ist eine Forschungsentscheidung, keine gemessene Aufwandsschätzung. QEMU `virt` ist kein PFC200-Board; Docker emuliert keinen eigenen Kernel oder K-Bus. ARM-Userspace-Emulation benötigt weiterhin Lösungen für Hardwareabhängigkeiten. Die CODESYS-I/O-Treiberdokumentation belegt Erweiterungsmöglichkeiten, keine automatische Kompatibilität originaler WAGO-Gerätebeschreibungen. [S24–S28]

Der WAGO-K-Bus-Modbus-Container arbeitet auf einem realen PFC, benötigt dessen Bus und verlangt, dass eine konkurrierende PLC-Runtime den Bus freigibt. Er ist kein vorhandener K-Bus-Emulator und darf nicht ungeprüft parallel zur Runtime gestartet werden. [S22]

## 5. Virtuelle Klemmen und Layout

Erster Kompatibilitätsstrang: **750-1405 + 750-1504**. Weitere Forschungsmodelle: **750-466** und **750-677**. Dies ist eine Modellpriorisierung; die Bestückung des neuen Referenzgeräts ist OFFEN. [S30–S34]

Artikelnummer, echte Buskennung, Kanalstruktur, Modulrevision, Prozessdatenlayout und Geräteparameter sind unterschiedliche Informationen. Offsets niemals allein aus Klemmenreihenfolge, Variablennamen oder Artikelnummer ableiten. Ein passender Name im virtuellen Gerätebaum belegt keine Busidentität.

Für Analogmodule Rohwert, Skalierung, Statusbits, Diagnose und Controllerprojektion getrennt erfassen. Der vorhandene 750-466-Encoder deckt nur den normalen Standard-4–20-mA-Bereich ab. Für PWM Betriebsart, Freigabe, Status-/Controlwörter, Registerkommunikation und Zeitverhalten getrennt behandeln. Der vorhandene 750-677-Decoder deckt einen begrenzten PWM-Frq-Pfad ab und weist Registerkommunikation zurück. Keine erfundenen Erfolgsantworten für unbekannte Operationen.

Ein Anlagenmodell darf PWM-/Ausgangsdaten zu Position und Endlagen umsetzen. Funktionale Scan-Nachbildung ist keine elektrische oder flankengetreue Emulation. Das Modell darf einen problematischen SPS-Befehl nicht stillschweigend reparieren.

## 6. Gelieferter Backendkern und seine Grenzen

Im lokalen Forschungspaket: kompletter Python-Standardbibliotheksprototyp, Tests, JSON-Konfigurationen, CLI, ELF-Audit, XML-Inventarwerkzeug, compile-only ABI-Sonde und Read-only-Collector mit Dry-Run.

Abgedeckt: komplette atomare Ausgangsframes, scanweise Eingangslatches, getrennte angeforderte/wirksame Ausgänge, eigene Busverlust-/Watchdogpolitik, fehlende oder eingefrorene Eingänge, Reset und Modell-Snapshot-Replay. Eigene Forschungsbelegung und Watchdogpolitik sind keine nachgewiesene WAGO-Semantik. 64 unabhängige Backendobjekte sind kein Benchmark von 64 originalen Runtimes.

Die 52 Pakettests bestanden ursprünglich und erneut bei der früheren Übergabe; 65 war ein weiterer historischer Suite-Zwischenstand. Der Integrator bestätigte aktuell 92 lokale hardwarefreie Tests PASS: 82 bestehende Tests plus 10 Device-Description-Parserfälle. Die hardwarefreie CI führt die gesamte Suite auf Python 3.11 und 3.13 aus; ihr Prüfergebnis ist an die jeweilige Git-Revision gebunden. Kein originaler I/O-Verbraucher, keine Runtime und keine Hardware wurden damit getestet. Eigenentwicklungscode und geprüfte synthetische Konfigurationen sind selektiv importiert; der ungebundene alte Hardwarecollector wurde nicht übernommen. [package.md](package.md)

## 7. Skalierung, Zeit und Reproduzierbarkeit

Pro Instanz eigene Konfiguration, Prozessbilder, Dateisystemzustände, Ports, Trace-IDs und berechtigte Lizenzzuordnung. Ressourcenbedarf erst mit echten Runtimeinstanzen messen. Eine Schätzung anhand des Python-Backends wäre irreführend.

Runtimezeit, Buszeit, Modellzeit und Hostmesszeit separat erfassen. Ein schneller Rechner beschleunigt einen zeitgesteuerten IEC-Task nicht automatisch. QEMU-Instruktionszählung ist nicht gleich zyklusgenaue Hardwarezeit. Zuerst normale Runtimezeit; deterministische Beschleunigung erst nach Zeitquellenanalyse und eigenem Nachweis. Snapshots eigener Modelle sind keine Runtime-Retain- oder Lizenzcontainer-Snapshots. [S29]

Realistisch qualifizierbare Ziele: Rohdaten-/Mappingfehler, Init-/Gerätefehler, ausgewählte Diagnosepfade und scanbasierte Regressionen. Weiterhin echte Referenztests nötig: elektrische Fehler, PWM-Flanken, EMV, Versorgungseinbruch, Bus-Worst-Case-Timing und mechanische Sicherheit.

## 8. Jetzt fehlende Nachweise

Inzwischen erhoben sind Device-Tree-Modell, Firmwaremarker, Kernel, Runtime-/Libraryhashes, Prozess-Maps, ausgewählte Init-/Runtimekonfigurationen sowie statisch analysierte installierte CODESYS-Beschreibungen. Die [tatsächliche Referenzanalyse](reference-abi-2026-10-11.md) belegt die ADI-Grenze des originalen Verbrauchers; der [CODESYS-Vertragsbericht](codesys-contract-2026-10-11.md) dokumentiert aktuelle Engineeringprofile und Device-Description-Verträge. Die Verfügbarkeit der beiden relevanten Digitalklemmenbeschreibungen ist nicht länger ein Blocker. Weiterhin fehlen Hardwarestand, Serienidentität, aktive Projektkonfiguration, tatsächliche Klemmenreihenfolge/-position und vollständiger CODESYS-Komponentenvertrag. Ein installiertes Engineeringprofil belegt weder ein geladenes IEC-Projekt noch Runtimeakzeptanz.

Die zentrale nächste Entscheidung folgt aus diesen Daten: Wo ist die kleinste vollständige emulierbare Grenze, welche Originalkomponenten bleiben unangetastet, welche Funktionen sind für einen DI/DO-Originalverbraucher notwendig? Fehlende Hardware oder Lizenzen blockieren jeweils den betroffenen Nachweis, nicht Header-, Quellen-, Modell- oder Dokumentationsarbeit insgesamt.
