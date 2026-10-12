# Lokaler Agent: öffentlicher Übergabevertrag

Aktueller Stand: [Referenzbestand und tatsächliche ABI](reference-abi-2026-10-11.md), [Offline-Carrier-Befunde](offline-carrier-2026-10-11.md), [CODESYS-Verträge](codesys-contract-2026-10-11.md) und [Engineering-Baseline vom 12.10.2026](codesys-engineering-2026-10-12.md). Die hardwarefreie Suite umfasst jetzt 99 Tests. Der [neue Blockbericht](originalstack-block-2026-10-12.md) bindet den tatsächlich gemappten Offlinekandidaten und den eigenen geprüften ADI-Adapter an ihre Artefakte. Eigene ARM- und Isolationskontrollen sind PASS; originaler I/O-Verbraucher und virtuelle Originalruntime bleiben separat BLOCKED/NOT_RUN. Ein eigenes natives Projekt mit dem unveränderten ST-Kandidaten wurde tatsächlich erstellt und offline mit null Fehlern und Warnungen kompiliert. Eine gezielte CODESYS-Verbindung zur Referenz und ein Keep-Login beobachteten eine geladene, gestoppte Anwendung; das war ein separater lesender Schritt. Anschließend lief eine eindeutig benannte interne Testanwendung tatsächlich auf der originalen Referenzruntime: Zähler 30 → 92, Ausgangswerte null, eigener I/O-Zweig deaktiviert. Die eigene Anwendung wurde danach gestoppt und anwendungsspezifisch entfernt; die vorherige Anwendung blieb geladen und gestoppt. Das ist kein virtueller I/O-Nachweis. Die aktuelle lokale Eigentümeranweisung gestattet die normale installierte IDE, ohne zusätzliche AppContainer-Grenze. Der historische Schutztest bleibt FAIL. Die VM wurde wieder auf Datenträger pausiert und als gestoppt bestätigt. Der [aktuell präzisierte Originalstack-Plan](next-originalstack-block.md) erhält Runtime, Manager und Originaltreiber. Fehlende interne Header betreffen einen optionalen Standalone-Harness; der untere Hardwarevertrag und tatsächliche Klemmenbestand bleiben offen; virtuelle Originalverbraucher-/Runtimeakzeptanz ist weiterhin nicht belegt.

Arbeite am Repository `Mateo817/virtualWAGO`. Das Ziel ist Virtualisierung unterhalb der IEC-Anwendung, nicht ein zusätzlicher OPC-UA-Variablensimulator. Prüfe die Dokumentation kritisch, bestätige oder revidiere Annahmen anhand von Originalquellen und arbeite bis zu einem belastbaren M1/M2-Abschluss und einem möglichen begrenzten M3-Kandidaten.

## Modelle und Delegation

Bitte nutze gpt-6 luna worker mit reasoning low, Medium, high oder extra high für einfache Aufgaben. Nutze sie so oft wie sinnvoll möglich. Du darfst bei schwierigen Aufgaben, Entscheidungen oder für reviews auch gezielt  gpt-6.1 Sol mit reasoning low, medium, high oder extra high nutzen.  Setzte Sol mit hohen reasoning bitte wirklich nur bei wenigen ausgewählten Aufgaben ein.

Nutze nur tatsächlich verfügbare Modell-/Workerfunktionen. Melde fehlende Fähigkeiten; erfinde keine Workerläufe und installiere nicht nur dafür ein Orchestrierungsframework. Halte einen verantwortlichen Integrator; parallele Arbeiter dürfen nicht zugleich das Referenzgerät, eine geteilte VM oder denselben K-Bus besitzen.

## Erst lesen

README, AGENTS, research, ADR, roadmap, safety und package. Die vollständige private lokale Übergabe ergänzt Zieladressen, Zugänge, historische Studie und Quellpaket. Fehlt die lokale Richtlinie, bleiben Gerätezugriffe blockiert; Offlinearbeit geht weiter. Die konkrete geschützte Anlage ist absolut ausgeschlossen, auch als Quelle für Software oder Konfigurationskopien.

## Reihenfolge

1. Git- und lokale Werkzeugumgebung frisch inventarisieren; laufende fremde Jobs/VMs erhalten. Eigentümereigene Softwarequellen nur lesend als Referenz nutzen.
2. Paketmanifest prüfen und die aktuelle hardwarefreie Suite frisch ausführen (zuletzt 99 PASS; frühere 52-/65-Teststände sind historische Zwischenstände). Eigenen Prototypcode selektiv im Forschungsbranch übernehmen. Keine Firmware oder privaten Anhänge committen.
3. Lokale Target-Allowlist, geschützte Ziele und Isolation praktisch absichern. Kein globaler Scan, keine unerlaubten Redirects oder automatischen Discoverypakete.
4. Neues Referenzgerät zunächst read-only inventarisieren: Artikel, Firmware, Kernel, Runtime, Bibliotheken, Maps, Konfiguration, Gerätepfade und I/O-Bestand. Engineeringversion und Runtimeversion trennen. Keine Firmwareangleichung nur zur Vereinheitlichung.
5. Originaldateien rechtmäßig und gehasht offline sichern, benötigte Header/DevDesc/SDKs lokalisieren. Privatmaterial aus Git und Logs heraushalten. Zuerst statische Analyse, danach begrenzte nichtinvasive Beobachtungen auf der Test-WAGO.
6. API-Verbraucher, vollständige ABI und parallele Async-/Register-/Zeit-/Retainpfade rekonstruieren. Header nicht aus Callstellen erfinden. B+C bleibt eine gestützte Hypothese. Device-Descriptions sind verfügbar. Originalruntime und Original-I/O-Manager stellen ihre eigenen nativen Objekte bereit; keine erfundenen internen Strukturen und kein obligatorischer Standalone-Harness. Den konkreten ersetzten ADI/DAL-Vertrag anhand gebundener Originalquellen, Firmware und begrenzter Referenzbeobachtungen schließen; dessen Fehler-/Callback-/Lifecyclelücken bleiben echte nachweisbezogene Gates.
7. Bei belegter Grenze kleinen DI/DO-Originalverbraucher-PoC entwickeln. Fehlende Geräte/API-Aufrufe als negative Kontrollen. Ein Mock oder Eigenclient ist keine Originalruntime-Evidence.
8. Erst anschließend Analog/PWM und Mehrinstanzenbetrieb. Softwareinstallationen auf dem erlaubten Testgerät nur nach safety.md; keine produktive SPS verändern.

## Ergebnis

Dokumentiere Revisionen, Artefakthashes, Befunde, verworfene Varianten, tatsächliche Tests, Risiken und nächsten Einstiegspunkt. Forschungs- und Teststatus getrennt. Keine universelle Kompatibilität, Echtzeit oder Hardwarefreigabe aus Backendtests ableiten. Materialle Entscheidungen als ADR, Änderungen als PR; spätere Merges nur mit geltender Autorisierung und erfolgreicher Evidence. Bei externem Blocker unabhängige sinnvolle Arbeit abschließen statt den Gesamtauftrag abzubrechen.
