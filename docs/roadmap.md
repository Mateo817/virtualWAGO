# Roadmap und objektive Abnahme

Zielpriorität gemäß [ADR-0003](adr-0003.md): zuerst ein realer, autorisierter Referenzversuch mit originaler CODESYS-Runtime, nativen I/O-Manager und originalen WAGO-I/O-Treibern. Eine Simulation darf erst unterhalb einer vollständig belegten und separat freigegebenen Hardwaregrenze eingreifen. Vollständige Controller-Virtualisierung kommt später. Historische PASS gelten nur für ihre dokumentierte Revision und Evidenzstufe.

| Stufe | Ergebnis | Abnahme |
|---|---|---|
| R0: Zustand sichern und Identität binden | Read-only Bestandsaufnahme von Runtime/Anwendung und Identität der Referenz; zwei verbundene Module identifiziert | Keine Neustarts, Löschungen, Downloads oder Überschreibungen. RAM-Anwendung, gelöschtes Arbeitsverzeichnis und fehlendes wiederherstellbares Bootprojekt nachvollziehbar bewertet; Modulart, Revision, Position und Kommunikationsbefund mit Quelle dokumentiert. Unlesbare/unsichere Merkmale bleiben OFFEN. |
| R1: Originalstack-Vertrag am Referenzgerät | Native Runtime, I/O-Manager und originale WAGO-I/O-Treiber samt tatsächlichem Projekt-/I/O-Pfad gebunden | Quelle, Hashes/Versionen, Konfiguration, Zustände und erwartete I/O-Wirkung belegt. Nur ausdrücklich freigegebene, reversible Softwareaktionen; bestehende Ausgänge/Anlage bleiben sicher. Keine Annahmen aus Offline-Modellkandidaten. |
| R2: Simulationsgrenze qualifizieren | Kleinste ersetzbare untere Hardwaregrenze und Simulationsadapter | Vollständiger Funktions-, ABI-, Fehler-, Lifecycle-, Callback- und Nebenläufigkeitsvertrag aus passenden Quellen und begrenzter Beobachtung; separat geklärte Berechtigung für Bus-/Bibliotheksersetzung; wirksame Isolation ohne physischen Buszugriff. Unbekannte Vertragsstellen verhindern den Simulationseinsatz. |
| R3: Referenz-WAGO mit unterer Simulation | Originalruntime, nativer Manager und Originaltreiber bedienen nachweislich modellierte I/O unterhalb der Grenze | Zuerst konkret identifizierte reale Modultypen/Revisionen. Originalverbraucher und echter Runtime-I/O-Pfad, erwartete Eingänge/Ausgänge, Fehler- und Rückkehrfälle mit gebundenen Artefakten; keine nicht freigegebene Busumschaltung oder Aktorwirkung. |
| V1: Vollständig virtuelle Steuerung | Späterer, eigenständiger Nachweis einer virtuellen Controllerinstanz | Runtime-/Lizenzrechte, Boot/Dateisystem, Zeit, Ressourcen, Netz- und Geräteisolation separat qualifiziert. Zusätzliche virtuelle Runtime-Lizenz ist kein R0–R3-Blocker. |
| V2: Erweiterung | Weitere Module, Analog/PWM, Diagnose, Parallelbetrieb und Zeitverhalten | Exakte Modulrevision und Quellvertrag, je Pfad eigene Abnahmekriterien. Hardwarefreie CI bleibt getrennt von Referenz-/Hardwareevidence. |

## Aktueller Einstieg

Der Eigentümer berichtet zwei angeschlossene Module, deren Identität und Kommunikation unbekannt sind. Eine Anwendung ist im RAM geladen und gestoppt; das Arbeitsverzeichnis wurde gelöscht, ein wiederherstellbares Bootprojekt ist nicht gesichert. Daher beginnt R0 mit Zustandserhalt und read-only Klärung; kein Neustart, Löschen oder Überschreiben. Der Root-Agent bleibt alleiniger Geräte-/VM-Integrator. Der konkrete Ablauf steht in [next-originalstack-block.md](next-originalstack-block.md), die datierten Aufzeichnungen in [Versuchsplan](real-controller-plan-2026-10-12.md) und [Beobachtungsprotokoll](real-controller-observation-2026-10-12.md).

Die bisherigen 750-1405/750-1504 Artefakte bleiben Offline-Modellkandidaten. Sie setzen nicht die tatsächliche Bestückung. Die bisherigen 99 hardwarefreien Tests, Adapter- und Harnessläufe, Offline-Engineering-Builds sowie begrenzten internen Runtimebeobachtungen bleiben PASS ausschließlich in den jeweils verlinkten, revisionsgebundenen Scopes. Sie erfüllen R0–R3 nicht.

## Statussprache

PASS bedeutet tatsächlich erfolgreich für den dokumentierten Stand und Scope. FAIL bedeutet ausgeführt und fehlgeschlagen. NOT_RUN bedeutet nicht ausgeführt, mit Grund. BLOCKED benennt eine konkret fehlende Voraussetzung. Aussagen werden als VERIFIZIERT, HYPOTHESE, OFFEN oder BLOCKED gekennzeichnet. Softwareberechtigung für die Referenz bleibt bestehen; Austausch/Ersetzung geschützter Bus- oder Herstellerbibliotheken benötigt eine eigene konkrete Freigabe. Unabhängige Offlinearbeit wird durch einen Teilblocker nicht angehalten.
