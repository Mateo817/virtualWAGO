# Roadmap und objektive Abnahme

**Getrennter 750-8212-Zwischenstand, 14.10.2026:** Der
[read-only Bericht](reference-8212-2026-10-14.md) bindet einen neuen Aufbau mit
unverändertem RUN-Zustand, sichtbarer Frontfolge 1405×2/1504×2/466/677/600 und
abweichender Offline-Projektfolge. Er ersetzt weder den früheren
750-8213-Digitalnachweis noch überträgt er dessen STOP-/Runtime-PASS. Für den
8212 sind elektronische Reihenfolge, Revisionen, Runtimezuordnung und alle
elektrischen Versuche weiter OFFEN/BLOCKED.

**Offline-Vertragsblock, 13.10.2026:** [750-466](native-analog-contract-2026-10-13.md): exakter Descriptor, zwei WORD-Eingänge, FW31-Registeranforderungen sowie frischer nativer IDE-Build/Reopen PASS. Untere ADI-/Status-/Registerprojektion und Native466-Runtime bleiben offen. [ADR-0008](adr-0008.md) legt den Bytepufferausbau fest; [PWM/Onboard-Serial/750-652](pwm-serial-contracts-2026-10-13.md) sind getrennt untersucht; [digitaler Lifecycleplan](native-model-lifecycle-plan-2026-10-13.md) vorbereitet, NOT_RUN. Kein SPS-Zugriff in diesem Block, kein Merge.

**Fortsetzung, 13.10.2026:** [Neue native Digitaltests](native-digital-tests-2026-10-13.md) qualifizieren den aktuellen Digitaladapter für 750-430/530 und 750-1405/1504 bei Modellpermit 0. Der erste WORD16-Versuch fand eine eigene 8-Bit-Kanalgrenze; Korrektur und erfolgreicher vollständiger Wiederholungslauf sind getrennt dokumentiert. [Kurze neue Chat-Übergabe](new-chat-handoff-2026-10-13.md) bindet Entscheidungen und nächste Tests. Hardwarevergleich und native Analog-/PWM-/Seriellpfade bleiben offen.

**Fortsetzung, 12.10.2026:** [Nativer Digital-8-Zyklus](native-cyclic-2026-10-12.md): originale Runtime, nativer I/O-Manager und Originaltreiber verarbeiten virtuelle 750-430/750-530. TCM 0 ist nativ offline gesetzt und wieder geöffnet geprüft; Init und zyklische angeforderte Ausgangsframes bei dauerhaftem Modellpermit 0 PASS. Original-STOP-Rücknahme und frische APP-/CRC-/Config-/Binary-Hashes PASS. [Controllerzugang](controller-metadata-2026-10-12.md) und frühere Abbrüche bleiben separat belegt. Sämtliche Moduldaten stammen aus dem Modell; echte Controllerdaten bleiben auf derselben Platine.

**Früherer Nachweis, 12.10.2026:** [Modellkanal und geschützter Runtimeversuch](runtime-bridge-2026-10-12.md). Der konkret freigegebene Providerwechsel wurde versucht: originale Runtime und I/O-Treiber luden den Eigenprovider, native Initialisierung **FAIL**, DI/DO-Abnahme **NOT_RUN**. Die gezielte Rücknahme und der frische originale STOP-Wiederanlauf sind **PASS**; bestehende APP/CRC/Config und Originalbinaries sind hashgleich. Der aktuelle Prozess arbeitet im vorhandenen Runtimehome; das frühere gelöschte CWD ist historisch. Damals blockierten Boardmetadaten-/Signatur- und Hilfskomponentenpfade den Start. Die anschließende Controller-/TCM 0-/Zyklusqualifikation oben beschreibt den heutigen begrenzten Erfolg.


Zielpriorität gemäß [ADR-0003](adr-0003.md): zuerst ein realer, autorisierter Referenzversuch mit originaler CODESYS-Runtime, nativen I/O-Manager und originalen WAGO-I/O-Treibern. Eine Simulation darf erst unterhalb einer vollständig belegten und separat freigegebenen Hardwaregrenze eingreifen. Vollständige Controller-Virtualisierung kommt später. Historische PASS gelten nur für ihre dokumentierte Revision und Evidenzstufe.

| Stufe | Ergebnis | Abnahme |
|---|---|---|
| R0: Zustand sichern und Identität binden | Read-only Bestandsaufnahme von Runtime/Anwendung und Identität des ausdrücklich benannten Referenzgeräts; dessen verbundene Module getrennt inventarisiert | Keine Neustarts, Löschungen, Downloads oder Überschreibungen. Anwendungs-/Persistenzzustand je Ziel bewertet; Modulart, Revision, Position und Kommunikationsbefund mit Quelle dokumentiert. Foto, Offlineprojekt und elektronische Enumeration bleiben getrennte Evidenzstufen; unlesbare/unsichere Merkmale bleiben OFFEN. |
| R1: Originalstack-Vertrag am Referenzgerät | Native Runtime, I/O-Manager und originale WAGO-I/O-Treiber samt tatsächlichem Projekt-/I/O-Pfad gebunden | Quelle, Hashes/Versionen, Konfiguration, Zustände und erwartete I/O-Wirkung belegt. Nur ausdrücklich freigegebene, reversible Softwareaktionen; bestehende Ausgänge/Anlage bleiben sicher. Keine Annahmen aus Offline-Modellkandidaten. |
| R2: Simulationsgrenze qualifizieren | Kleinste ersetzbare untere Hardwaregrenze und Simulationsadapter | Vollständiger Funktions-, ABI-, Fehler-, Lifecycle-, Callback- und Nebenläufigkeitsvertrag aus passenden Quellen und begrenzter Beobachtung; separat geklärte Berechtigung für Bus-/Bibliotheksersetzung; wirksame Isolation ohne physischen Buszugriff. Unbekannte Vertragsstellen verhindern den Simulationseinsatz. |
| R3: Referenz-WAGO mit unterer Simulation | Originalruntime, nativer Manager und Originaltreiber bedienen nachweislich modellierte I/O unterhalb der Grenze | Zuerst konkret identifizierte reale Modultypen/Revisionen. Originalverbraucher und echter Runtime-I/O-Pfad, erwartete Eingänge/Ausgänge, Fehler- und Rückkehrfälle mit gebundenen Artefakten; keine nicht freigegebene Busumschaltung oder Aktorwirkung. |
| V1: Vollständig virtuelle Steuerung | Späterer, eigenständiger Nachweis einer virtuellen Controllerinstanz | Runtime-/Lizenzrechte, Boot/Dateisystem, Zeit, Ressourcen, Netz- und Geräteisolation separat qualifiziert. Zusätzliche virtuelle Runtime-Lizenz ist kein R0–R3-Blocker. |
| V2: Erweiterung | Weitere Module, Analog/PWM, Diagnose, Parallelbetrieb und Zeitverhalten | Exakte Modulrevision und Quellvertrag, je Pfad eigene Abnahmekriterien. Hardwarefreie CI bleibt getrennt von Referenz-/Hardwareevidence. |

## Aktueller Einstieg

Der Eigentümer beauftragt zusätzlich den [Modulkatalog](module-catalog-2026-10-12.md): weitere Digitalmodule, Analog und autonom konfigurierte PWM. Offlinearbeit darf parallel zur offenen vollständigen R3-Abnahme laufen und benötigt keine vollständig virtuelle Steuerung. [ADR-0007](adr-0007.md) trennt Dokumentation, Eigenmodelle, native Runtime und Hardwarevergleich.

- [x] Versionierter Katalog, Kanalgrenzen und gemischte Digital-/Analog-/PWM-Signalmodelle.
- [x] Autonomes PWM Frq in eigener logischer Zeit; angeforderte/wirksame Werte und eigene Watchdoglease getrennt.
- [x] Neue native Digital-8-Regression und Digital-16-Abnahme 750-1405/1504 mit frischen Artefakten/Rückweg: begrenzte Eingangs-/Ausgangsbefehlsprüfung bei Modellpermit 0; kein Hardwarevergleich.
- [ ] 750-466: native Prozessabbild-/Diagnose-/Registerprojektion und Vergleich definierter Analogreize mit gebundener Modulrevision.
- [ ] 750-677: originaler Konfigurations-/Start-/Statusvertrag, benötigte weitere Modi, native und später freigegebene Messvergleiche.
- [ ] Weitere Artikel nach belegtem Daten-/Verhaltensvertrag freischalten; kein generisches Erfolgsstub.
- [ ] Virtuelle serielle Kommunikation: originale FW31-SysCom-/WAGO-Komponenten und Portauswahl lesen; isolierter virtueller Endpunkt/Gegenstellenmodell, dann native Anfrage/Antwort-/Timeoutprüfung.
- [ ] Andere PFC200-Ausstattungen: Schnittstellenfähigkeiten und Gerätebeschreibungs-/Controllertypprüfungen getrennt untersuchen. Controlleridentität erhalten; Zusatzschnittstelle ist keine vollständige andere Controlleremulation.

Der [750-8213-Eigentümerfotobeleg](reference-module-photo-2026-10-12.md) zeigt
750-430 → 750-530 → 750-600. Bei diesem früheren Ziel bleibt die vorhandene
Anwendung STOP; online erzeugte Bootdateien und aktualisierte Konfiguration
wurden privat gesichert. Der gezielte STOP-Wiederanlauf ist geprüft;
Geräte-Reboot bleibt NOT_RUN. Die [750-8212-Evidence](reference-8212-2026-10-14.md)
bindet dagegen einen separaten RUN-Bestand und die sichtbare Folge
1405×2/1504×2/466/677/600. Ihr Backup ist kein Vollsnapshot; Projekt- und
Fotoreihenfolge unterscheiden sich. Kein blinder Neustart, Löschen oder
Überschreiben an irgendeinem Ziel. Root bleibt alleiniger Geräte-/VM-Integrator.

Die virtuellen 750-1405/750-1504 sind inzwischen im begrenzten nativen WORD16-Test geprüft; Sie setzen nicht die tatsächliche Bestückung. Die bisherigen 99 hardwarefreien Tests, Adapter- und Harnessläufe, Offline-Engineering-Builds sowie begrenzten internen Runtimebeobachtungen bleiben PASS ausschließlich in den jeweils verlinkten, revisionsgebundenen Scopes. Sie erfüllen R0–R3 nicht.

## Statussprache

PASS bedeutet tatsächlich erfolgreich für den dokumentierten Stand und Scope.
FAIL bedeutet ausgeführt und fehlgeschlagen. NOT_RUN bedeutet nicht ausgeführt,
mit Grund. BLOCKED benennt eine konkret fehlende Voraussetzung. Aussagen werden
als VERIFIZIERT, HYPOTHESE, OFFEN oder BLOCKED gekennzeichnet. Zielgebundene
Software- oder Busfreigaben werden nicht zwischen 8213 und 8212 übertragen;
Austausch/Ersetzung geschützter Bus- oder Herstellerbibliotheken benötigt eine
eigene konkrete Freigabe. Unabhängige Offlinearbeit wird durch einen
Teilblocker nicht angehalten.

R3 ist ausschließlich am früheren 750-8213 im begrenzten
Digital-8-Byte-/Befehls-Scope mit geschlossenem Modellgate erreicht. Die
vollständige R3-Abnahme bleibt dort offen. Der neue 750-8212 besitzt bislang
read-only Geräte-, Foto- und Offline-Projektevidence, aber keinen nativen
Runtime-Digitaltest. Reale Modulrevisionen, aktive wirksame Modellausgänge sowie
umfassende Fehler-/STOP-/Lifecycle- und Zeitverträge sind nicht bestätigt.
