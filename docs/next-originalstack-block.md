# Nächster Originalstack-Block und Übergabe

**Modulerweiterung, 19.10.2026:** [Bytepuffer und frische Digitalregression](module-extension-2026-10-19.md): virtuelle 750-1405/750-1504 (16 DI/DO) und 750-430/750-530 mit Originalruntime/Originaltreibern **PASS**, Modellpermit 0; Original-STOP und unveränderte Dateien wieder bestätigt. 750-550-Signalmodell ergänzt; Analogpaar und PWM-Projekt Build/Reopen **PASS**. Native Analog-/PWM-Ausführung bleibt wegen Register-/Projektionsverträgen **BLOCKED / NOT_RUN**. 281 lokale Tests ohne Skip; der private Header benötigende Bytepuffer-Harness ist in öffentlicher CI ohne diese Header explizit NOT_RUN.

**Neuer getrennter 750-8212-Zwischenstand, 14.10.2026:** Der
[read-only Bericht](reference-8212-2026-10-14.md) bindet einen anderen
Controller mit unverändertem RUN-Zustand. Sichtbar sind 1405×2, 1504×2, 466,
677 und 600; die Offline-Projektfolge weicht ab. Elektronische Enumeration,
Revisionen und Runtimezuordnung bleiben offen. Die folgenden 750-430/530- und
STOP-Aussagen gehören zum früheren 750-8213 und sind kein Live-Inventar des
8212.

**Offline-Vertragsblock, 13.10.2026:** [750-466](native-analog-contract-2026-10-13.md): exakter Descriptor, zwei WORD-Eingänge, FW31-Registeranforderungen sowie frischer nativer IDE-Build/Reopen PASS. Untere ADI-/Status-/Registerprojektion und Native466-Runtime bleiben offen. [ADR-0008](adr-0008.md) legt den Bytepufferausbau fest; [PWM/Onboard-Serial/750-652](pwm-serial-contracts-2026-10-13.md) sind getrennt untersucht; [digitaler Lifecycleplan](native-model-lifecycle-plan-2026-10-13.md) vorbereitet, NOT_RUN. Kein SPS-Zugriff in diesem Block, kein Merge.

**Fortsetzung, 13.10.2026:** [Neue native Digitaltests](native-digital-tests-2026-10-13.md) qualifizieren den aktuellen Digitaladapter für 750-430/530 und 750-1405/1504 bei Modellpermit 0. Der erste WORD16-Versuch fand eine eigene 8-Bit-Kanalgrenze; Korrektur und erfolgreicher vollständiger Wiederholungslauf sind getrennt dokumentiert. [Kurze neue Chat-Übergabe](new-chat-handoff-2026-10-13.md) bindet Entscheidungen und nächste Tests. Hardwarevergleich und native Analog-/PWM-/Seriellpfade bleiben offen.

**Fortsetzung, 12.10.2026:** [Nativer Digital-8-Zyklus](native-cyclic-2026-10-12.md): originale Runtime, nativer I/O-Manager und Originaltreiber verarbeiten virtuelle 750-430/750-530. TCM 0 ist nativ offline gesetzt und wieder geöffnet geprüft; Init und zyklische angeforderte Ausgangsframes bei dauerhaftem Modellpermit 0 PASS. Original-STOP-Rücknahme und frische APP-/CRC-/Config-/Binary-Hashes PASS. [Controllerzugang](controller-metadata-2026-10-12.md) und frühere Abbrüche bleiben separat belegt. Sämtliche Moduldaten stammen aus dem Modell; echte Controllerdaten bleiben auf derselben Platine.

**Früherer Nachweis, 12.10.2026:** [Modellkanal und geschützter Runtimeversuch](runtime-bridge-2026-10-12.md). Der konkret freigegebene Providerwechsel wurde versucht: originale Runtime und I/O-Treiber luden den Eigenprovider, native Initialisierung **FAIL**, DI/DO-Abnahme **NOT_RUN**. Die gezielte Rücknahme und der frische originale STOP-Wiederanlauf sind **PASS**; bestehende APP/CRC/Config und Originalbinaries sind hashgleich. Der aktuelle Prozess arbeitet im vorhandenen Runtimehome; das frühere gelöschte CWD ist historisch. Damals blockierten Boardmetadaten-/Signatur- und Hilfskomponentenpfade den Start. Die anschließende Controller-/TCM 0-/Zyklusqualifikation oben beschreibt den heutigen begrenzten Erfolg.


Stand: 12.10.2026. Diese Reihenfolge setzt [ADR-0003](adr-0003.md) um. Erstes Ziel ist der Originalstack auf der autorisierten realen Referenz-WAGO: vorhandene CODESYS-Runtime, nativer I/O-Manager und originale WAGO-I/O-Treiber. Eine eigene I/O-Schicht oder ein Ersatzconsumer ist kein Ziel. Eine Simulation wird erst nach Nachweis und Freigabe unterhalb der kleinsten vollständigen Hardwaregrenze eingesetzt. Vollständige Controller-Virtualisierung ist nachgelagert.

## Gegenwärtig bekannte Grenzen

Beim früheren 750-8213 zeigt der
[Eigentümerfotobeleg](reference-module-photo-2026-10-12.md) die Frontartikel
750-430 → 750-530 → 750-600. Dessen Anwendung bleibt STOP; Bootdateien,
Konfiguration und STOP-Rückweg sind revisionsgebunden dokumentiert. Beim neuen
750-8212 zeigt das Foto dagegen 1405×2/1504×2/466/677/600, während das
Offlineprojekt die zweite 1504 hinter der 677 anordnet. Diese Inventare,
Anwendungszustände und Rückwege bleiben strikt getrennt. Kein blinder Neustart.

Softwarearbeit und der konkrete Provider-/Buswechsel im gebundenen Versuchsplan
sind für den früheren 750-8213 freigegeben. Diese Freigabe gilt nicht für den
neuen 750-8212; dort belegt der aktuelle Zwischenstand ausschließlich read-only
Arbeit. Jeder weitere geschützte Eingriff benötigt weiterhin einen
zielkonkreten Plan. Root bleibt alleiniger Geräte-/VM-Integrator; kein
Netzwerkzugriff aus alten Dokumenten ableiten.

## Block A: Zustand erhalten und Bestand read-only binden

Zuerst je Ziel den aktuellen Gerätezustand, Runtime-/Treiber-/DAL-Versionen und
Hashes, laufende Prozesse, Anwendungszustand, verfügbare persistente
Projekt-/Bootartefakte und vorhandene Rückkehrmöglichkeiten dokumentieren.
Keine Handlung, die RAM-Anwendung oder Wiederherstellungschance verändert. Beim
früheren 8213 sind die tatsächlichen zwei I/O-Module zu qualifizieren; beim 8212
ist die sichtbare Mehrmodulfolge von der abweichenden Projektfolge und einer
noch fehlenden elektronischen Enumeration zu trennen. Keine unklare
EEPROM-/Typenschildabfrage und keine Busumschaltung.

**Abnahme:** Identität und Zustand sind belastbar gebunden oder jeweilige Lücken
explizit OFFEN/BLOCKED; keine zustandsverändernde Operation fand statt.
Misslingt eine sichere Identifikation, bleibt diese Teilfrage offen und
Offlinearbeit läuft weiter. Der 8213-Befund steht im
[Beobachtungsprotokoll](real-controller-observation-2026-10-12.md), der
getrennte 8212-Befund im [read-only Zwischenstand](reference-8212-2026-10-14.md).

## Block B: nativen Original-I/O-Pfad verstehen

Anhand der aktuellen Anwendung, tatsächlich installierten Komponenten, Projekt-/Gerätebeschreibung und sicher lesbarer Runtimebeobachtung klären, welche I/O-Knoten und Originaltreiber aktiv sind und wie Ein-/Ausgänge die Anwendung erreichen. Zuerst nur lesende/risikoarme Beobachtung. Einen eigenen internen IEC-Lauf oder Download nicht beginnen, solange RAM-/Bootzustand und Auswirkungen nicht verstanden sind. Outputwerte und reale Aktorwirkung bleiben getrennt; ohne bestätigte sichere Verdrahtung keine physische Ausgabe.

Vor einem konkreten Test dokumentiert der Integrator Trigger, erwartete Zustände, erlaubte Lese-/Schreibaktionen, sichere Ausgangswerte, Stop-/Rückkehrweg und Abbruchbedingungen. Eigentümerfreigabe für Software gilt; geschützte Bus-/Bibliotheksersetzung, K-Bus-Masterwechsel und Aktortests bleiben eigene Freigabegates.

**Abnahme:** konkreter Originalstack und Anwendungspfad sind versions-/hashgebunden; jede Beobachtung besitzt eng abgegrenzten Scope. Keine Mock-, Offline-Build- oder Adapter-Evidence wird als realer I/O-Nachweis ausgegeben.

## Block C: kleinste ersetzbare Hardwaregrenze belegen

Die bisherigen FW30-Header-, FW31-Verbraucher- und ADI/DAL-Befunde sind historische, quell- und hashgebundene Evidenz. Für genau den aktuellen Stack müssen Verbraucher, Provider, Signaturen/Layout, Aufrufphasen, Größen/Offsets, Rückgaben, Fehlerfälle, Lifecycle, Callback-Lebensdauer, Synchronisation sowie relevante Async-/Register-/Zeit-/Diagnosepfade neu zugeordnet werden. Keine unbekannten Strukturen, Offsets, Modulkennungen oder APIs erraten. ADI/DAL bleibt Kandidat, bis alle für den angestrebten Strang nötigen Pfade belegt sind.

**Abnahme:** jede für den begrenzten realen I/O-Strang benötigte Funktion hat authentische Quelle oder ausreichend begrenzte direkte Evidence; verbleibende Lücken und Auswirkungen sind benannt. Vor Ersetzung der geschützten Bus-/Bibliotheksgrenze liegt ein konkreter separat freigegebener Versuch mit Sicherung und Rollback vor. Fehlt diese Freigabe, bleibt Einbau BLOCKED, während Analyse weitergehen kann.

## Block D: gezielte Simulation unterhalb des Originalstacks

Für den früheren 750-8213 ist der reale Zielstrang nach Fotobeleg 750-430/750-530
(je acht Kanäle), Abschluss 750-600. Für den neuen 750-8212 belegt das Foto
stattdessen 1405×2/1504×2/466/677/600, aber noch keine elektronische
Reihenfolge oder wirksame Runtimezuordnung; sein Offlineprojekt ist eine eigene,
abweichende Evidenzstufe. Erst nach Block A–C und einer zielkonkreten Freigabe
den qualifizierten Adapter/Modellkern einsetzen. Originalruntime, nativer
Manager und originale Treiber bleiben erhalten. Kein virtueller Testbaum wird
ohne Gerätebeleg zur Zuordnung eines realen Bestands erklärt. Modell beschreibt
Signale und physikalische Reaktionen, keine nachgeschriebene SPS-Logik.
Angeforderte und wirksame Ausgänge sowie Fehler-/Watchdogreaktion bleiben
getrennt.

Zuerst mit vollständiger Isolation gegen den Originalconsumer, dann den originalen Runtime-I/O-Pfad qualifizieren. Keine Hostgeräte, realen Klemmen, Host-D-Bus, Hostservices oder physischen Busse als Fallback. Praktische Netz-, Datei-, Geräte- und IPC-Isolation wird für den konkreten Prozess geprüft; Dokumentation allein implementiert keine Sperre.

**Abnahme:** originale Komponentenpfade bleiben nachweislich aktiv; erwartete Eingangsdaten, vollständige Ausgangsframes, negative Kontrolle und definierte Fehler-/Rückkehrfälle stimmen mit dem belegten Modulvertrag überein. Jeder PASS gilt nur für konkrete Revision, Hashes, Konfiguration und Scope.

## Später: vollständig virtuelle Steuerung

Eine eigenständige virtuelle Runtime/Controllerinstanz folgt erst nach dem realen Referenzpfad. Für sie sind Lizenz-/Ausführungsrechte, Loader-/Service-/Dateisystem-/IPC-/Geräteabhängigkeiten, Zeitverhalten, Ressourcen und Isolation separat zu qualifizieren. Eine zusätzliche Runtime-Lizenz ist kein pauschales Hindernis für die Schritte A–D.

## Historische Befunde

Der [Engineeringbericht](codesys-engineering-2026-10-12.md), [Referenz-ABI-Bericht](reference-abi-2026-10-11.md), [Offline-Blockbericht](originalstack-block-2026-10-12.md) und [Carrier-/Isolationsbericht](offline-carrier-2026-10-11.md) belegen jeweils nur ihren damaligen Stand und Scope. Sie enthalten keinen neuen Nachweis über die aktuell verbundenen Module, den aktuellen RAM-/Bootprojektzustand oder die Simulation unter dem gegenwärtigen Originalstack. Die historische Ausführung einer internen Testanwendung ist kein virtueller I/O-Nachweis.
