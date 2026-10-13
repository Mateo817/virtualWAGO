# Übergabe für einen neuen Chat, 13. Oktober 2026

## Ziel und Arbeitsweise

Das Projekt untersucht I/O-Simulation unterhalb der originalen WAGO/CODESYS-I/O-Schicht. Vorrang hat die autorisierte Referenzsteuerung mit unveränderter Originalruntime, nativem I/O-Manager und originalen I/O-Treibern. Geräte- und VM-Aktionen führt ausschließlich Root aus. Lies vor einem neuen Arbeitsschritt `AGENTS.md`, `README.md`, [ADR-0001](adr-0001.md), [ADR-0003](adr-0003.md), [ADR-0005](adr-0005.md), [ADR-0007](adr-0007.md), [ADR-0008](adr-0008.md), [Roadmap](roadmap.md), [Safety](safety.md), [öffentliche Übergabe](handoff.md) und [nächsten Originalstack-Block](next-originalstack-block.md). Öffentliche Berichte und frühere Studien sind revisions- und scopegebunden, kein aktuelles Live-Inventar.

## Aktueller Digital-Nachweis

[Nativer Digital-Testbericht](native-digital-tests-2026-10-13.md) dokumentiert getrennt:

- Digital-8: frische Regression des korrigierten Providers PASS für vier Eingangsmuster und angeforderte XOR-Ausgaben bei Modellpermit0. Frühere Provider bleiben separat gebunden.
- Digital-16: erster Runtimeversuch FAIL, weil der eigene INPUT-Parser 256 bei Maximum 255 ablehnte. Eine separate `STATUS`-Maske `0xff` war ein weiterer Codefehler, aber nicht die Ursache des `ERRCOMMAND`.
- Digital-16: korrigierter eigener Provider PASS für acht 16-Bit-Eingabemuster und angeforderte XOR-Ausgaben bei dauerhaftem Modellpermit 0. Der eigene FAULT-Latch wurde separat beobachtet; das ist keine Qualifikation allgemeiner Fehler-, STOP- oder Watchdogsemantik.
- Die ursprüngliche Anwendung wurde danach in STOP wiederhergestellt und sieben ursprüngliche Hashes wurden geprüft. Physische Ausgänge blieben gesperrt. Die isolierten Testprozesse hatten keinen Zugriff auf physische Module; ein physischer Verhaltensvergleich fand nicht statt. Modulrevisionen bleiben offen.

Die Offline-IDE-Generierung und das read-only Reopen des Digital-16-Projekts sind ein eigener Nachweis und kein Runtime- oder Hardwarebeleg.

## Neuer Offline-Vertragsstand

[750-466-Analyse](native-analog-contract-2026-10-13.md) bindet Description2.0.0.9, zwei WORD-Eingänge und den tatsächlichen FW31-Table9-/Konfigregisterpfad. Der frische native IDE-Build und das schreibfreie Reopen der V2-Quelle sind PASS; `%IW1`/`%IW2` gelten nur für das gespeicherte Projekt. Untere Größen/Offsets, Statusfilter, Registerwerte/Fehler und Runtimequalifikation bleiben offen. [ADR-0008](adr-0008.md) enthält den gestuften Bytepufferplan; kein neuer Analogprovider ist implementiert.

[PWM/Serial](pwm-serial-contracts-2026-10-13.md): 677-Descriptor deklariert16Bytes je Richtung gegenüber12Outputbytes im Eigenmodell; drei652-Descriptions8/24/48 separat. FW31-SysCom/ComSwitch/ComExtra sind statisch gebunden; `/dev/ttyRUNTIME`-Auflösung, Caller-/Portvertrag offen. [Digitaler Lifecycleplan](native-model-lifecycle-plan-2026-10-13.md) ist vorbereitet, NOT_RUN. STATUS erneuert die eigene IPC-Idlefrist; keine absolute Lease behaupten. [Evidence](../evidence/native-contracts-2026-10-13.json) bindet die neuen Quellen. Dieser Block hat keine SPS kontaktiert; die verwendete IDE-VM wurde wieder auf Datenträger pausiert.

## Nächste Arbeit

1. Die nächsten nativen Digitaltests auf wirksame Modellausgänge, Permit-/Leaseverlust und STOP-/Wiederanlauf ausarbeiten. Hardwareisolation und Erhalt der ursprünglichen Anwendung bleiben Voraussetzung; der bisherige Permit0-PASS ist keine vollständige Watchdog-/Lifecyclequalifikation.
2. Parallel offline die 750-466-Unterlagen binden: exakte Descriptorversion und Hash, native Parameter/Typen/Richtungen/Größen, FW31-Verbraucher und tatsächliche Prozessabbild-/Diagnose-/Registerprojektion. Die vorhandene Sechs-Byte-Projektion bleibt eine eigene Forschungsannahme. Der native Offline-Build/Reopen ist jetzt getrennt PASS; als Nächstes die konkrete untere Projektion und tatsächlich benötigte Registerantworten binden. Keine unbelegten IDs, Offsets oder Statusantworten ergänzen.
3. Für 750-677 erst PWM-Frq-Konfiguration, Initialisierung/RegCom, Status und vollständige native Prozessdaten aus gebundenen Originalartefakten klären. PWM DC ist ein anderer Modus. Keine native Erweiterung oder elektrische Behauptung aus dem bisherigen Offlinecodec ableiten.
4. Serielle Kommunikation getrennt untersuchen: onboard virtuelle RS485 und K-Bus-Modul 750-652 haben verschiedene Verträge. Für onboard RS485 zuerst tatsächlich installierte FW31-Komponenten, Portauswahl und API-Vertrag belegen; allgemeine CODESYS-SysCom-Dokumentation ist nur eine Hypothese. Andere Controllerausstattungen benötigen eine Fähigkeitsmatrix mit echter Controlleridentität, keine Identitätskopie.

Die unabhängigen Offlineblöcke können parallel weiterlaufen. Ein unbekannter Originalvertrag blockiert nur die davon abhängige Umsetzung.

## Grenzen und Ablage

Im öffentlichen Git liegen freigegebene Quelltexte, ADRs, Roadmap, bereinigte Evidence und begrenzte Ergebnisberichte. Private Übergabe enthält Zugangs- und Zielrichtlinie, Credentials, tatsächliche Gerätezuordnung, Herstellerdateien, Rohprotokolle, Projekt-/Runtimeartefakte und vollständige private Evidence. Keine privaten Adressen, Passwörter, Gerätekennungen, Herstellerdateien oder unbereinigten Traces nach Git kopieren.

Vor jedem aktiven Schritt die lokale `OWNER_SCOPE`- und `START_HIER`-Übergabe lesen und Zielrichtlinie, Geräteidentität, aktuellen STOP-Zustand, Backup, Quellenbindung, Isolation und Rückweg prüfen. Fehlt diese lokale Bindung, sind Netzwerk- und Gerätezugriffe gesperrt. Die geschützte Produktionsanlage bleibt ausgeschlossen, auch read-only, per Ping, Discovery oder als Kopierquelle. Firmware-/Bootloaderupdates, Kernel-/Originaltreiberersetzung, K-Bus-Masterumschaltung und physische Aktortests benötigen jeweils einen konkreten separat freigegebenen Plan.

Diese Übergabe ist ein Einstiegspunkt, keine neue Hardwarefreigabe und kein Ersatz für die lokalen Schutzregeln.
