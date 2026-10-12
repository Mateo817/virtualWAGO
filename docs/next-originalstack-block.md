# Nächster Originalstack-Block und Übergabe

Stand: 12.10.2026. Dieser Bericht konkretisiert den nächsten Arbeitsschritt für die Forschungsentscheidung B+C. Er ist keine neue Architekturentscheidung, Hardwarefreigabe oder Herstellerzusage. Die ausführliche lokale Übergabe bleibt privat.

## Ausführungsstand

Der [ausgeführte Blockbericht vom 12.10.2026](originalstack-block-2026-10-12.md) ergänzt diesen Plan: frische lesende Referenzbindung, natives Offline-DI/DO-Mapping, 34-Slot-Vertragsmatrix und eigener sequenzieller ARM-ADI-Adapter samt ausgeführten eigenen Vertragstests. Physische Klemmenpräsenz bleibt OFFEN. Originalverbraucher-M3 und virtuelle Runtime-M4 sind noch nicht ausgeführt; die präzisen Start-/Service-/Nebenläufigkeits-/Lizenzgates stehen im neuen Bericht. Die folgenden Blockkriterien bleiben Abnahmevorgaben und sind keine pauschale PASS-Erklärung.

## Zielbild bleibt der Originalstack

Die Forschungsfrage bleibt: dieselbe CODESYS-Runtime, derselbe native CODESYS-I/O-Manager und möglichst dieselben originalen WAGO-I/O-Treiber sollen unverändert erhalten bleiben. Der virtuelle Ersatz sitzt ausschließlich an der **kleinsten tatsächlich belegten unteren Hardwaregrenze**. Aktuell führt die Evidence zu ADI/DAL und weiter zur K-Bus-Hardwareanbindung; welche untere Funktion/Komponente sich vollständig ersetzen lässt, wird erst nach dem Verbraucher-/Vertragsabgleich festgelegt. Weder eine eigene CODESYS-I/O-Schicht noch ein selbst geschriebener Ersatzverbraucher ist das Ziel.

**VERIFIZIERT:** Die Runtime auf dem Referenzgerät führte eine eigene interne Testanwendung aus; die Zählervariable lief von 30 auf 92. Kbus und die DI-/DO-Knoten waren dabei deaktiviert, es gab keine reale Klemmenübernahme. Ein eigenes natives Projekt mit den vorhandenen Device Descriptions wurde unter CODESYS 3.5.21.50 offline ohne Fehler/Warnungen kompiliert. Belege und enge Grenzen: [Engineeringbericht](codesys-engineering-2026-10-12.md).

**VERIFIZIERT, statischer Scope:** Der gesicherte DAL-Provider ist bytegleich mit dem gepinnten FW30-Artefakt. Der tatsächlich installierte `IoDrvDal`-Verbraucher ist ein anderer Build; der tatsächliche `IoDrvKbus` ist ebenfalls gesichert. Der ABI-Bericht belegt konkrete ADI-Verwendung und Verbraucherpfade, aber weder erfolgreichen Austausch noch zyklische I/O-Akzeptanz. [Referenz-ABI-Bericht](reference-abi-2026-10-11.md), [FW30-ABI-Bericht](abi-research-2026-10-11.md).

**HYPOTHESE:** Originalruntime plus nativer I/O-Manager und originale I/O-Treiber bleiben aktiv, während nur die bewiesene Schnittstelle zur unteren Hardware-/DAL-Seite virtuell bedient wird. **NOT_RUN:** virtueller Originalverbraucher und virtuelle Originalruntime. **OFFEN:** tatsächliche Klemmenbestückung, aktiver Projekt-/Mappingstand und vollständiger Vertrag der zu ersetzenden Grenze.

## Was jetzt kein pauschaler Blocker ist

Die passenden internen CODESYS-Header `CmpIoDrvItf.h`, `IoConfigConnectorMap` und Plattformdefinitionen sind erforderlich, **wenn** wir diese CODESYS-Objekte außerhalb des Original-I/O-Managers selbst konstruieren, interpretieren oder deren Methoden direkt aufrufen wollen, etwa in einem optionalen Standalone-Instrumentierungsharness. Sie sind kein allgemeiner Startblocker für den bevorzugten Weg, bei dem der originale CODESYS-I/O-Manager die originalen Treiber und Strukturen selbst erzeugt.

Für den Originalstack-Pfad muss stattdessen zuerst der Vertrag der konkret zu ersetzenden unteren ADI/DAL-Grenze aus Originalheadern, dem byteidentischen Provider, dem tatsächlichen FW31-Verbraucher und den bereits autorisierten, eng begrenzten Referenzbeobachtungen rekonstruiert werden. FW30-Headerbefunde gelten dabei nur mit ihrem expliziten FW30-Scope. Keine Struktur, Signatur, Fehlerantwort oder Offset aus Nachbaraufrufen erraten.

## Nächster Arbeitsplan

### Block 1: frische Bestandsbindung und offline gemappter Kandidat

Root bleibt alleiniger Geräte-/VM-Integrator. Der freigegebene Referenzbestand wird mit einem begrenzten Leselauf frisch geprüft: genaue Runtime-/Treiber-/DAL-Hashes, laufende Anwendung und Zustand, Klemmenpräsenz/-reihenfolge sowie die verwendeten Device Descriptions. Das ist read-only. Unsichere EEPROM-/Typenschildpfade bleiben unangetastet; fehlende physische Abtrennung oder Identität blockiert nur den davon abhängigen Gerätebefund.

Parallel wird aus dem unveränderten eigenen [`minimal_io.st`](../prototype/iec/minimal_io.st) ein neues **Offlineprojekt mit aktiven 750-1405-/750-1504-Knoten und explizitem DI-/DO-Mapping** erstellt. Compiler-, Profil-, Geräte-, Bus- und Terminalversionen sowie Descriptor-/Quellhashes werden gepinnt. Das Projekt und Mapping bleiben private Buildartefakte; öffentliche Dokumentation enthält nur bereinigte Metadaten und Hashes.

**Ausgaben von Block 1:**

- eine frische, datierte Bestandsmatrix mit Softwarehashes, Anwendung/Zustand und, sofern sicher lesbar, tatsächlichem Terminalbestand/-reihenfolge;
- ein privates natives Projekt, offline erzeugte Anwendung und Mappingexport mit Manifest; dokumentierte Quellen-, IDE-/Compiler-, Geräte- und Buspins;
- ein bereinigtes Compilerprotokoll und eine Mappingtabelle, die zeigt, welche IEC-Signale auf die deklarierten Input-/Outputkanäle der richtigen Terminalknoten gehen.

**PASS-Kriterium für den Block:** Die frische Lesebaseline ist revisions-/hashgebunden und widerspricht keiner unaufgelösten Identitäts- oder Zustandsannahme; das neue, offline erzeugte Projekt baut mit null Fehlern und null Warnungen; das Mapping ist im nativen Projekt und im Export konsistent auf 750-1405 Eingang und 750-1504 Ausgang nachgewiesen; der laufenden SPS wurde nichts heruntergeladen, geschrieben, gestartet, gestoppt oder zurückgesetzt. Offline-Mapping beweist dabei keine physische Präsenz oder korrekte reale Verdrahtung. Fehlt sichere Klemmenpräsenz, bleibt dieser Teil OFFEN; der Offline-Build darf dennoch separat PASS sein.

### Block 2: Vertrag der tatsächlich ersetzten unteren Grenze

Für die konkrete installierte Version wird eine Funktionsmatrix erstellt: Verbraucher und Quellstelle; Providerfunktion/Tabellenslot; aufrufende Phase; Argument-/Längenregeln; Rückgaben/Fehlerfälle; Geräte-/Prozessabbildbezug; Callbackregistrierung und -lebensdauer; Synchronisation und Parallelaufrufe. Sie umfasst zyklische Read/Write, Init/Enumeration/Öffnen/Schließen, Zustands-/Watchdogpfade, Diagnose, Eventcallbacks sowie tatsächlich referenzierte Async-, Register-, Zeit- und Retainabhängigkeiten. Jede Zeile erhält Quelle, ELF-/Headerhash und Evidenzscope. Nicht aufgerufene Slots werden nicht als erforderlich oder unbenötigt behauptet.

Der byteidentische FW30-DAL-Provider kann seine statisch belegten Verträge für genau diese Bytes stützen. Für den abweichenden tatsächlichen Verbraucher muss jede verwendete Stelle am tatsächlichen Binary erneut gebunden werden. Die begrenzte Referenzbeobachtung stützt nur die dort beobachteten Zustände/Operationen; sie ersetzt keine Signatur- oder Nebenläufigkeitsanalyse. Verbleibende Funktions-/Fehler-/Callbacklücken bleiben **OFFEN**.

**PASS-Kriterium:** Jede vom unveränderten originalen Verbraucher tatsächlich referenzierte und für den Minimalstrang benötigte Funktion ist mit authentischer Signatur/Layoutquelle und implementierungsgebundenem Verhalten oder eng begrenzter Beobachtung belegt. Fehlende Fehlerpfade oder Lebensdauerregeln werden explizit als offene Freigabegates geführt. Kein eigener CODESYS-Manager-/Connector-Aufbau wird als Umweg eingeführt.

### Block 3: eigene Minimaladapter- und Modellarbeit

Erst nach Block 2 entsteht ein eigener ARM32-ABI-kompatibler Adapter an der freigegebenen unteren Grenze plus Python-Backendmodell für 750-1405/750-1504. Adapter und Modell werden unabhängig von Herstellerdateien im öffentlichen Repo gehalten; proprietäre Header/Binaries bleiben privat und werden nicht kopiert. ABI-Probe, negativer Fehlerfall, Längen-/Kapazitätsgrenzen, Callbackende und Read/Write-Frameatomarität bekommen eigene testspezifische Evidence. Host-GCC-Layoutmessungen sind kein Target-ABI-PASS; Compiler/ABI müssen explizit gebunden werden.

**PASS-Kriterium:** Eigene compile-/unit-/contract-tests zeigen korrektes Mapping, atomare Frames und dokumentierte Fehlerreaktionen am nachgewiesenen Vertrag; private Herstellerartefakte sind nicht im Repository. Dieser PASS qualifiziert nur Adapter/Modell, noch keinen Originalverbraucher.

### Block 4: gestufter Originalstack-Aufbau in isolierter Ausführungsumgebung

Vor jedem Start werden die fehlenden dynamischen Loader-, `dlopen`-/`dlsym`-, Dienst-, Dateisystem-, Device- und IPC-Abhängigkeiten des exakt gewählten Runtime-/Treiberpfads auditiert. Rechte für Originaldateien und Runtimeausführung sowie eine pro Instanz gültige Lizenz sind echte Freigabegates. Keine Lizenzidentität klonen oder umgehen. Die gesicherten Originalfirmwaredateien der freigegebenen Referenz bleiben private Analyse-/Ausführungsartefakte; ausgeschlossene Geräte sind keine Kopierquelle und Produktrepositories werden nicht verändert.

Der gestufte Start erhält Originalruntime, originalen I/O-Manager und originale K-Bus-Treiber; nur die bestätigte untere Hardwaregrenze erhält den eigenen Provider/Adapter. Es werden keine Hostgeräte, realen Klemmen, Host-D-Bus oder Host-Services als stillschweigende Fallbacks durchgereicht. Kein beliebiges Full-Firmware-Sandboxversprechen: jede Namespace-, Mount-, Device-, IPC-, Dienst- und Netzgrenze wird für den konkreten Startpfad einzeln geprüft. Fehlende Abhängigkeit oder unbekannte Nebenwirkung stoppt genau die betroffene Stufe.

**Nicht vorsehen:** kein ADI-Initialisierungsbeispiel oder zweiter Master auf einem belegten/aktiven realen K-Bus. Keine zweite aktive Masterinstanz auf demselben realen K-Bus; eine getrennte virtuelle Runtime darf diesen Bus nicht erreichen. Der vorhandene Referenzruntime-Pfad bleibt während isolierter Bring-up-Schritte unberührt; die Test-WAGO ist kein stillschweigend verfügbarer Emulationsbus.

### Block 5: Originalverbraucher-M3, danach IEC-M4

M3 beginnt mit dem unveränderten Originalverbraucher und virtueller unterer Grenze: Initialisierung/Enumeration, erwartete 750-1405-/750-1504-Erkennung, zyklische DI-Muster und vollständige DO-Frames, Stop/Close sowie mindestens eine negative Kontrolle bei fehlendem oder nicht unterstütztem Gerät. Native Originaltreiber und I/O-Manager bleiben Teil des Pfads. Jeder virtuelle Erfolgsfall muss dem gebundenen Mapping entsprechen; Mock-/Eigenclienterfolg ist kein M3-PASS.

M4 ist ein eigener Schritt mit der eigenen gemappten IEC-Anwendung: Quell-/Build-/Runtimebindung, bestätigte DI-/DO-Werte, definierte Stop-/Start-/Restart- und Watchdogfälle und keine physischen Endpunkte. M3-PASS ersetzt M4 nicht; M4-PASS ersetzt keine längeren Fehler-, Zeit- oder Skalierungstests.

## Optionale Instrumentierung und reale Gates

Ein Standalone-Harness zum Beobachten des Originalverbrauchers ist **optionale Instrumentierung**, kein obligatorisches Forschungsziel. Es darf nur mit den echten passenden CODESYS-Headern und vollständig belegtem Lifecycle gebaut werden. Es ist kein Grund, für den Originalmanager-Pfad unbekannte `INIT_STRUCT`-/Connectorlayouts nachzubilden.

Lizenzrechte, Nutzungsrechte für Herstellerartefakte, Quell-/Binärversion, Ressourcenbudget, Zeitverhalten und physische Testbedingungen sind echte Gates. Solange sie nicht für eine konkrete Stufe geklärt sind, bleibt deren Lauf **NOT_RUN** oder **BLOCKED**; unabhängige Offline-Analyse und Modelltests gehen weiter. Die bestehenden konkreten Eigentümerfreigaben für Softwarearbeit auf dem Referenzgerät gelten weiter; dieser Plan widerruft sie nicht und verlangt keine neue pauschale Bestätigung. Firmware-/Bootloaderupdates, Kernel-/Originaltreiberersetzung, K-Bus-Masterwechsel und physische Aktortests bleiben separat plan- und freigabepflichtig. Einen virtuellen Ersatz zuerst ausschließlich in der isolierten Forschungsumgebung einsetzen, nicht auf dem Referenzgerät installieren.

## Übergabe für einen frischen Chat

Repository: `Mateo817/virtualWAGO`, Forschungsbranch `research/originalstack-m1-m2`. Bei dieser Dokumentvorbereitung stand der lokale HEAD auf `69e8a9b93b66f44437740eb8a69bd8d35aa2ed76`; das ist die abgeschlossene Engineering-Baseline. Dies ist der Referenzstand, nicht die zwingende Startrevision des nächsten Chats. Bei Chatstart zuerst `git status`, Branch, HEAD, Remotes, AGENTS/README/ADR/Roadmap/Safety und die neueren Engineering-/ABI-Berichte frisch prüfen. GitHub ist Source of Truth; diese Dokumentvorbereitung hat keine Netzwerkaktualisierung vorgenommen. Keine fremden Änderungen verwerfen oder pauschal übernehmen; keine Commits/PRs aus einem ungeprüften gemischten Arbeitsbaum.

Die privaten Rohprojekte, Laufprotokolle, Zielzuordnung, Zugänge, Firmware und Herstellerheader liegen ausschließlich in der lokalen Übergabe. Nur Root ist Ziel-/VM-Integrator; im frischen Chat keine Geräteverbindung aus alten Adressen oder Logs ableiten. Bereits erteilte Softwarefreigaben fortführen; daraus folgt keine Freigabe für K-Bus-Umschaltung, Originaltreiberersetzung oder Aktortests.

Lesereihenfolge: diesen Bericht, [ADR-0001](adr-0001.md), [Referenz-ABI](reference-abi-2026-10-11.md), [CODESYS-Verträge](codesys-contract-2026-10-11.md), [Engineering-Baseline](codesys-engineering-2026-10-12.md), [Safety](safety.md) und die private lokale Handoff. Ältere Abschnitte, die „Runtime nicht ausgeführt“ sagen, gelten nur für den dort dokumentierten früheren Stand: der begrenzte eigene App-Lauf auf Originalruntime ist inzwischen im Engineeringbericht belegt. Er ist weder virtuelle Runtime noch M3/M4.

**Auftrag für den nächsten Chat:** zuerst Block 1 als konkrete Artefakte mit obigen PASS-Kriterien abschließen; Root bleibt alleiniger Geräteintegrator. Danach die Funktionsmatrix der ersetzten unteren Grenze als tatsächliches M2-Deliverable schließen. Erst dann Adapter-/Modellverhalten und einen isolierten Originalverbraucher planen. Vor M3/M4 Rechte, exact target/source hashes, Runtime-/Komponentenabhängigkeiten und jeden Start-/Stop-/Rollbackeffekt erneut binden. Der Lauf muss sinnvoll begrenzt sein; weder vollständige Firmware-Rekonstruktion noch ein Standalone-Harness sind pauschale Vorbedingungen für den kleinen Originalstack-PoC.
