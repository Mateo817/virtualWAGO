# Roadmap und objektive Abnahme

**Fortsetzung, 12.10.2026:** [Nativer Digital-8-Zyklus](native-cyclic-2026-10-12.md): originale Runtime, nativer I/O-Manager und Originaltreiber verarbeiten virtuelle 750-430/750-530. TCM 0 ist nativ offline gesetzt und wieder geöffnet geprüft; Init und zyklische angeforderte Ausgangsframes bei dauerhaftem Modellpermit 0 PASS. Original-STOP-Rücknahme und frische APP-/CRC-/Config-/Binary-Hashes PASS. [Controllerzugang](controller-metadata-2026-10-12.md) und frühere Abbrüche bleiben separat belegt. Sämtliche Moduldaten stammen aus dem Modell; echte Controllerdaten bleiben auf derselben Platine.

**Früherer Nachweis, 12.10.2026:** [Modellkanal und geschützter Runtimeversuch](runtime-bridge-2026-10-12.md). Der konkret freigegebene Providerwechsel wurde versucht: originale Runtime und I/O-Treiber luden den Eigenprovider, native Initialisierung **FAIL**, DI/DO-Abnahme **NOT_RUN**. Die gezielte Rücknahme und der frische originale STOP-Wiederanlauf sind **PASS**; bestehende APP/CRC/Config und Originalbinaries sind hashgleich. Der aktuelle Prozess arbeitet im vorhandenen Runtimehome; das frühere gelöschte CWD ist historisch. Damals blockierten Boardmetadaten-/Signatur- und Hilfskomponentenpfade den Start. Die anschließende Controller-/TCM 0-/Zyklusqualifikation oben beschreibt den heutigen begrenzten Erfolg.


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

Der Eigentümer beauftragt zusätzlich den [Modulkatalog](module-catalog-2026-10-12.md): weitere Digitalmodule, Analog und autonom konfigurierte PWM. Offlinearbeit darf parallel zur offenen vollständigen R3-Abnahme laufen und benötigt keine vollständig virtuelle Steuerung. [ADR-0007](adr-0007.md) trennt Dokumentation, Eigenmodelle, native Runtime und Hardwarevergleich.

- [x] Versionierter Katalog, Kanalgrenzen und gemischte Digital-/Analog-/PWM-Signalmodelle.
- [x] Autonomes PWM Frq in eigener logischer Zeit; angeforderte/wirksame Werte und eigene Watchdoglease getrennt.
- [ ] Neue native Digital-8-Regression und Digital-16-Abnahme 750-1405/1504 mit frischen Artefakten/Rückweg.
- [ ] 750-466: native Prozessabbild-/Diagnose-/Registerprojektion und Vergleich definierter Analogreize mit gebundener Modulrevision.
- [ ] 750-677: originaler Konfigurations-/Start-/Statusvertrag, benötigte weitere Modi, native und später freigegebene Messvergleiche.
- [ ] Weitere Artikel nach belegtem Daten-/Verhaltensvertrag freischalten; kein generisches Erfolgsstub.
- [ ] Virtuelle serielle Kommunikation: originale FW31-SysCom-/WAGO-Komponenten und Portauswahl lesen; isolierter virtueller Endpunkt/Gegenstellenmodell, dann native Anfrage/Antwort-/Timeoutprüfung.
- [ ] Andere PFC200-Ausstattungen: Schnittstellenfähigkeiten und Gerätebeschreibungs-/Controllertypprüfungen getrennt untersuchen. Controlleridentität erhalten; Zusatzschnittstelle ist keine vollständige andere Controlleremulation.

Der [Eigentümerfotobeleg](reference-module-photo-2026-10-12.md) zeigt 750-430 → 750-530 → 750-600. Frontartikel und fotografierte Reihenfolge sind damit belegt; Revisionen, elektronische Zuordnung und aktuelle Kommunikation bleiben offen. Die vorhandene Anwendung bleibt STOP; online erzeugte Bootdateien und aktualisierte Konfiguration wurden privat gesichert. Der aktuelle gezielte STOP-Wiederanlauf ist geprüft; Geräte-Reboot bleibt NOT_RUN. Kein blinder Neustart, Löschen oder Überschreiben. [Fortsetzung](adi-digital8-continuation-2026-10-12.md): authentischer Digital-8-Offlinestand und eigene ARM-Adapterprüfungen; die spätere native Abnahme steht im aktuellen Zyklusbericht. Der Root-Agent bleibt alleiniger Geräte-/VM-Integrator. Der konkrete Ablauf steht in [next-originalstack-block.md](next-originalstack-block.md), die datierten Aufzeichnungen in [Versuchsplan](real-controller-plan-2026-10-12.md) und [Beobachtungsprotokoll](real-controller-observation-2026-10-12.md).

Die bisherigen 750-1405/750-1504 Artefakte bleiben Offline-Modellkandidaten. Sie setzen nicht die tatsächliche Bestückung. Die bisherigen 99 hardwarefreien Tests, Adapter- und Harnessläufe, Offline-Engineering-Builds sowie begrenzten internen Runtimebeobachtungen bleiben PASS ausschließlich in den jeweils verlinkten, revisionsgebundenen Scopes. Sie erfüllen R0–R3 nicht.

## Statussprache

PASS bedeutet tatsächlich erfolgreich für den dokumentierten Stand und Scope. FAIL bedeutet ausgeführt und fehlgeschlagen. NOT_RUN bedeutet nicht ausgeführt, mit Grund. BLOCKED benennt eine konkret fehlende Voraussetzung. Aussagen werden als VERIFIZIERT, HYPOTHESE, OFFEN oder BLOCKED gekennzeichnet. Softwareberechtigung für die Referenz bleibt bestehen; Austausch/Ersetzung geschützter Bus- oder Herstellerbibliotheken benötigt eine eigene konkrete Freigabe. Unabhängige Offlinearbeit wird durch einen Teilblocker nicht angehalten.

R3 ist im begrenzten Digital-8-Byte-/Befehls-Scope mit geschlossenem Modellgate erreicht. Die vollständige R3-Abnahme bleibt offen: reale Modulrevisionen, aktive wirksame Modellausgänge sowie umfassende Fehler-/STOP-/Lifecycle- und Zeitverträge sind noch nicht bestätigt. Die ursprünglichen Abnahmekriterien werden dadurch nicht als vollständig erfüllt ausgegeben.
