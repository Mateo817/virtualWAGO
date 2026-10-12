# Forschungsergebnisse und Machbarkeitsentscheidung

**Aktueller Nachweis, 12.10.2026:** [Modellkanal und geschützter Runtimeversuch](runtime-bridge-2026-10-12.md). Der konkret freigegebene Providerwechsel wurde versucht: originale Runtime und I/O-Treiber luden den Eigenprovider, native Initialisierung **FAIL**, DI/DO-Abnahme **NOT_RUN**. Die gezielte Rücknahme und der frische originale STOP-Wiederanlauf sind **PASS**; bestehende APP/CRC/Config und Originalbinaries sind hashgleich. Der aktuelle Prozess arbeitet im vorhandenen Runtimehome; das frühere gelöschte CWD ist historisch. Konkrete Blocker sind originale Boardmetadaten-/Signatur- und Hilfskomponentenabhängigkeiten, keine fehlende pauschale Software- oder Umschaltfreigabe.


Stand: 12.10.2026. Die technischen Befunde weiter unten sind historische, revisions- und scopegebundene Forschungsergebnisse, keine neue Hardwaremessung. Die aktuelle Priorität wurde in [ADR-0003](adr-0003.md) festgelegt: zuerst die autorisierte reale Referenz-WAGO mit laufender Originalruntime, nativen I/O-Manager und originalen WAGO-I/O-Treibern; Simulation erst unterhalb einer belegten Hardwaregrenze. Eine vollständig virtuelle Steuerung folgt später. Quellenkennungen beziehen sich auf [sources.md](sources.md). Private Projektinventare und vollständige Evidence verbleiben im lokalen Übergabepaket. Die Original-ELF-/Headeranalyse steht in [abi-research-2026-10-11.md](abi-research-2026-10-11.md), der gebundene historische Geräte-/ABI-Stand in [reference-abi-2026-10-11.md](reference-abi-2026-10-11.md). Die erste Offline-/Verbindungsetappe bleibt in [execution-2026-10-11.md](execution-2026-10-11.md) dokumentiert.

## 1. Forschungsziel und Priorität

Langfristig soll eine virtuelle PFC200 nach Möglichkeit originale IEC-Logik, I/O-Mapping und WAGO-Gerätebaum verwenden. Der erste Nachweis erfolgt jedoch auf der realen autorisierten Referenz-WAGO mit Originalruntime und originalem I/O-Stack; eine spätere virtuelle Anbindung muss unterhalb der Anwendung liegen. Ein OPC-UA-Simulator oder ein in ST eingebautes Anlagenmodell erfüllt den Hardwareemulationsnachweis nicht.

**Erstes Ziel:** Auf der autorisierten Referenz-WAGO den Originalstack mit der bereits laufenden Runtime, dem nativen I/O-Manager und originalen WAGO-I/O-Treibern untersuchen und nutzen. Erst unterhalb der kleinsten vollständig belegten Hardwaregrenze soll eine Simulation erfolgen. Der [Eigentümerfotobeleg](reference-module-photo-2026-10-12.md) identifiziert die Frontartikel und Reihenfolge 750-430 → 750-530 → 750-600. Revisionen, elektronische Zuordnung und aktueller Kommunikationszustand bleiben offen. Die Modellkandidaten 750-1405/750-1504 sind keine Annahme über diesen Bestand.

**HYPOTHESE:** Eine geeignete untere Grenze lässt sich simulieren, während der Originalstack erhalten bleibt. Die konkrete ADI-Providerbindung ist freigegeben und im Startupversuch nachgewiesen; der vollständige native I/O-Vertrag bleibt offen. Die vollständig virtuelle Steuerung ist ein nachgelagertes Ziel. Eine zusätzliche Runtime-Lizenz für eine virtuelle Instanz blockiert das erste reale Referenzziel nicht pauschal; Rechte für konkrete Software-/Bus-/Bibliotheksänderungen bleiben eigenständige Gates. Kein fertiger Emulator wird behauptet.

**Aktuelle Zustandsschranke:** Die vorhandene Anwendung bleibt STOP; Root hat online Bootdateien erzeugt und privat mit bytegleichen Kopierhashes gesichert. Der aktuelle kontrollierte STOP-Wiederanlauf ist PASS; die frühere Ausgangslage steht in der [Fortsetzung](adi-digital8-continuation-2026-10-12.md). Kein blindes Neustarten, Löschen, Überschreiben oder anderer zustandsverändernder Schritt, bis Anwendung und persistenter Zustand sicher verstanden und gesichert sind. Das ist kein Anlass, unabhängige Offlinearbeit einzustellen.

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

Historische Offline-Modellpriorität: **750-1405 + 750-1504**; weitere Forschungsmodelle: **750-466** und **750-677**. Diese Kandidaten sind nicht die Priorität für den realen Referenzversuch und sagen nichts über dessen angeschlossene Module aus. Der spätere [Fotobeleg](reference-module-photo-2026-10-12.md) zeigt zwei I/O-Module 750-430/750-530 plus Abschluss 750-600. Modulrevisionen und elektronische/zyklische Zuordnung bleiben OFFEN. [S30–S34]

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

## 8. Historische Evidenz und aktuelle offene Punkte

Inzwischen erhoben sind Device-Tree-Modell, Firmwaremarker, Kernel, Runtime-/Libraryhashes, Prozess-Maps, ausgewählte Init-/Runtimekonfigurationen sowie statisch analysierte installierte CODESYS-Beschreibungen. Die [tatsächliche Referenzanalyse](reference-abi-2026-10-11.md) belegt die ADI-Grenze des originalen Verbrauchers; der [CODESYS-Vertragsbericht](codesys-contract-2026-10-11.md) dokumentiert aktuelle Engineeringprofile und Device-Description-Verträge. Die Verfügbarkeit der beiden relevanten Digitalklemmenbeschreibungen ist nicht länger ein Blocker. Weiterhin fehlen Hardwarestand, Serienidentität, aktive Projektkonfiguration, tatsächliche Klemmenreihenfolge/-position und vollständiger CODESYS-Komponentenvertrag. Ein installiertes Engineeringprofil belegt weder ein geladenes IEC-Projekt noch Runtimeakzeptanz.

Der [Engineeringnachweis vom 12.10.2026](codesys-engineering-2026-10-12.md) ergänzt inzwischen einen fehlerfreien nativen Offline-Build und einen tatsächlich ausgeführten internen IEC-Test auf der originalen Referenzruntime. Der eigene I/O-Zweig blieb dabei deaktiviert. Die Testanwendung wurde danach entfernt, die zuvor vorhandene Anwendung blieb geladen und gestoppt. Damit ist der reguläre Engineering-/Referenzpfad praktisch belegt; virtuelle Klemmenakzeptanz, Mapping, Wiederanlauf und der vollständige native I/O-Vertrag bleiben offen.

Diese Absätze beschreiben die früheren Stände und behalten ihren jeweiligen Scope; spätere Referenzlauf- oder Verbindungsbefunde sind kein rückwirkender PASS. Der Fotobeleg schließt Frontartikel und fotografierte Reihenfolge. Aktuell offen sind Modulrevisionen und elektronische Zuordnung der zwei I/O-Module, Klärung des RAM-/Bootprojektzustands ohne Neustart oder Überschreiben, sowie der Vertrag und die Freigabe jeder konkret zu ersetzenden unteren Schnittstelle. Die tatsächlich verbundenen Module bestimmen den ersten realen I/O-Strang. Die 750-1405/750-1504 bleiben bewusst wählbare Modellkandidaten; eine Übereinstimmung mit dem realen Bestand ist nicht belegt. Plan und datiertes Protokoll: [Versuchsplan](real-controller-plan-2026-10-12.md), [Beobachtungsprotokoll](real-controller-observation-2026-10-12.md).

Eine zusätzliche virtuelle Runtime-Lizenz ist kein pauschaler Blocker für die erste Referenz-WAGO. Softwareberechtigung für den Referenzpfad besteht fort; Austausch/Ersetzung geschützter Bus- oder Herstellerbibliotheken ist ein separater Freigabepunkt und darf nicht aus der Softwareberechtigung abgeleitet werden. Unabhängige Offlineanalyse bleibt möglich.
