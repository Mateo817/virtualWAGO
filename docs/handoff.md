# Lokaler Agent: öffentlicher Übergabevertrag

**CAN2/DALI, 20.10.2026:** [FW31-Testkopie und reale SDO-Abfragen](can2-fw31-dali-status-2026-10-19.md): Reopen des bisherigen Projekts **PASS**. Neue Kopie mit `NMTStartAll=FALSE`: Build, Codegenerierung, Bootdateien und Reopen **PASS**, 0 Fehler / 0 Warnungen. Erste fünf reale RX-/TX-PDOs read-only geprüft, deaktiviert; Fehlerregister weiterhin `0x81`. vcan-Erzeugung isoliert **PASS**, Bitraten-Setzen dort nicht unterstützt. Original-CODESYS-CAN-/DALI-Laufzeit **NOT_RUN**; DALI-Anschlusszustand noch zu klären. Originalruntime unverändert STOP, CAN DOWN.

**PWM-Erkundung, 19.10.2026:** [Begrenzter Async-Kanal](pwm-async-exploration-2026-10-19.md): Originalruntime RUN und sieben wechselnde angeforderte PWM-Ausgangsframes **PASS** mit explizit synthetischer UID/Registerantwort, Modellpermit 0. Original-STOP und sieben unveränderte Dateien nach Rücknahme **PASS**. 286 lokale Tests ohne Skip. Original-Moduldiagnose, PWM-Skalierung und Hardwareabgleich bleiben **OFFEN / NOT_RUN**. Die folgenden Meldungen dokumentieren frühere Stände.

**Native Integration, 19.10.2026:** [Analogeingang/-ausgang und digitale Regression](native-integration-2026-10-19.md): virtuelle 750-466/750-550, 750-430/750-530 und 750-1405/750-1504 mit Originalruntime und Originaltreibern **PASS**, Modellpermit 0. Explizite virtuelle Registerkonfiguration gemäß [ADR-0009](adr-0009.md); Hardwareabgleich **NOT_RUN**. PWM-Build/Reopen und Eigenprovider **PASS**, originale PWM-Runtime erreicht mit privatem D-Bus RUN; Frameabnahme **BLOCKED** am Modellfehler nach nicht unterstützter UID-Anfrage. 285 lokale Tests ohne Skip. Die folgenden Meldungen dokumentieren frühere Stände.

**Modulerweiterung, 19.10.2026:** [Bytepuffer und frische Digitalregression](module-extension-2026-10-19.md): virtuelle 750-1405/750-1504 (16 DI/DO) und 750-430/750-530 mit Originalruntime/Originaltreibern **PASS**, Modellpermit 0; Original-STOP und unveränderte Dateien wieder bestätigt. 750-550-Signalmodell ergänzt; Analogpaar und PWM-Projekt Build/Reopen **PASS**. Native Analog-/PWM-Ausführung bleibt wegen Register-/Projektionsverträgen **BLOCKED / NOT_RUN**. 281 lokale Tests ohne Skip; der private Header benötigende Bytepuffer-Harness ist in öffentlicher CI ohne diese Header explizit NOT_RUN.

**Aktueller Block, 18.10.2026:** [Begrenzter Prototyp](prototype-kbus-can-dali-2026-10-18.md)
mit neuem Acceptance-Prüfer und frischem DI8-IDE-Build/Reopen sowie echtem
Originalruntime-Zyklus PASS. Die aktuelle private Bindung führte zu einem
750-8213, dessen ursprünglicher STOP und Originaldateien nach dem Versuch
frisch wiederhergestellt geprüft wurden. CAN blieb DOWN ohne Pakete;
Koppleridentität, EDS/DCF, Prozessdaten-/DALI-Vertrag fehlen: dieser Teil
BLOCKED, Kommunikation NOT_RUN. Nicht den unten beschriebenen 8212 oder
historische Modulfolgen als aktuelle Zielbindung übernehmen. Die private
Übergabe dieses Auftrags liegt getrennt vom XE164-Forschungsstopp; neue
Zugriffe erfordern wie immer frische Ziel-/Zustandsbindung.

**Neuer getrennter Referenzaufbau, 14.10.2026:** Der
[750-8212-Zwischenstand](reference-8212-2026-10-14.md) bindet read-only einen
anderen Controller. `Application` blieb RUN; Foto und Offlineprojekt zeigen
unterschiedliche Modulreihenfolgen. Das Drei-Dateien-Backup ist kein
Vollzustandsnapshot. Keine STOP-/Runtime-/Hardware-PASS-Aussage des früheren
750-8213 darf auf diesen Aufbau übertragen werden.

**Offline-Vertragsblock, 13.10.2026:** [750-466](native-analog-contract-2026-10-13.md): exakter Descriptor, zwei WORD-Eingänge, FW31-Registeranforderungen sowie frischer nativer IDE-Build/Reopen PASS. Untere ADI-/Status-/Registerprojektion und Native466-Runtime bleiben offen. [ADR-0008](adr-0008.md) legt den Bytepufferausbau fest; [PWM/Onboard-Serial/750-652](pwm-serial-contracts-2026-10-13.md) sind getrennt untersucht; [digitaler Lifecycleplan](native-model-lifecycle-plan-2026-10-13.md) vorbereitet, NOT_RUN. Kein SPS-Zugriff in diesem Block, kein Merge.

**Fortsetzung, 13.10.2026:** [Neue native Digitaltests](native-digital-tests-2026-10-13.md) qualifizieren den aktuellen Digitaladapter für 750-430/530 und 750-1405/1504 bei Modellpermit 0. Der erste WORD16-Versuch fand eine eigene 8-Bit-Kanalgrenze; Korrektur und erfolgreicher vollständiger Wiederholungslauf sind getrennt dokumentiert. [Kurze neue Chat-Übergabe](new-chat-handoff-2026-10-13.md) bindet Entscheidungen und nächste Tests. Hardwarevergleich und native Analog-/PWM-/Seriellpfade bleiben offen.

**Fortsetzung, 12.10.2026:** [Nativer Digital-8-Zyklus](native-cyclic-2026-10-12.md): originale Runtime, nativer I/O-Manager und Originaltreiber verarbeiten virtuelle 750-430/750-530. TCM 0 ist nativ offline gesetzt und wieder geöffnet geprüft; Init und zyklische angeforderte Ausgangsframes bei dauerhaftem Modellpermit 0 PASS. Original-STOP-Rücknahme und frische APP-/CRC-/Config-/Binary-Hashes PASS. [Controllerzugang](controller-metadata-2026-10-12.md) und frühere Abbrüche bleiben separat belegt. Sämtliche Moduldaten stammen aus dem Modell; echte Controllerdaten bleiben auf derselben Platine.

**Früherer Nachweis, 12.10.2026:** [Modellkanal und geschützter Runtimeversuch](runtime-bridge-2026-10-12.md). Der konkret freigegebene Providerwechsel wurde versucht: originale Runtime und I/O-Treiber luden den Eigenprovider, native Initialisierung **FAIL**, DI/DO-Abnahme **NOT_RUN**. Die gezielte Rücknahme und der frische originale STOP-Wiederanlauf sind **PASS**; bestehende APP/CRC/Config und Originalbinaries sind hashgleich. Der aktuelle Prozess arbeitet im vorhandenen Runtimehome; das frühere gelöschte CWD ist historisch. Damals blockierten Boardmetadaten-/Signatur- und Hilfskomponentenpfade den Start. Die anschließende Controller-/TCM 0-/Zyklusqualifikation oben beschreibt den heutigen begrenzten Erfolg.


Aktuelle Zielpriorität: [ADR-0003](adr-0003.md). Zuerst eine ausdrücklich
gebundene reale Referenz-WAGO mit vorhandener Originalruntime, nativem
I/O-Manager und originalen WAGO-I/O-Treibern; Simulation nur unterhalb einer
tatsächlich belegten und für genau dieses Ziel freigegebenen Grenze. Der
[Versuchsplan](real-controller-plan-2026-10-12.md) und das
[Beobachtungsprotokoll](real-controller-observation-2026-10-12.md) gehören zum
früheren 750-8213. Für den 750-8212 gilt der separate read-only Bericht.

## Aktueller Zustand und Eigentümerscope

- Beim früheren 750-8213 zeigt der [Fotobeleg](reference-module-photo-2026-10-12.md) vom Controller aus 750-430, 750-530 und Abschluss 750-600. Modulrevisionen, elektronische Zuordnung und aktuelle zyklische Kommunikation bleiben offen. Dessen `Application` bleibt STOP; Bootdateien und Konfiguration wurden privat gesichert. Siehe [Fortsetzung](adi-digital8-continuation-2026-10-12.md).
- Beim neuen 750-8212 zeigt das private Foto sichtbar 750-1405 ×2, 750-1504 ×2, 750-466, 750-677 und 750-600. Die Offline-Projektfolge weicht ab; elektronische Reihenfolge und wirksame Runtimezuordnung bleiben offen. `Application` blieb RUN. Siehe [8212-Bericht](reference-8212-2026-10-14.md).
- Kein blinder Neustart, Löschen oder Überschreiben der bestehenden Anwendung. Vor einem weiteren autorisierten Prozesswechsel am 8213 dessen STOP, gesicherten Bootbestand, unveränderte Hashes und gebundenen Start-/Stop-/Restorepayload erneut prüfen. Beim 8212 ist RUN nur Beobachtungszustand; STOP/START oder ein anderer Prozesswechsel bleibt ohne eigenen Plan und eigene Freigabe gesperrt.
- Softwareberechtigung und die konkrete Provider-/Busumschaltfreigabe des gebundenen Versuchsplans gelten für den früheren 8213. Sie werden nicht auf den 8212 übertragen. Jeder weitere geschützte Eingriff benötigt einen zielkonkreten, separat freigegebenen Plan.
- Root-Agent bleibt alleiniger Geräte-/VM-Integrator. Kein Netzwerkzugriff aus Repositorytext, alten Logs oder vermuteten Adressen ableiten. Lokale Zielrichtlinie und Geräteidentität sind zwingend.

Foto/Aktortrennung stammen vom Eigentümer; Runtimeversuch und STOP-/Hashprüfungen sind tatsächliche Root-Beobachtungen mit getrenntem Scope. Das konkrete öffentliche Protokoll wird vom Integrator ergänzt; private Adressen, Zugangsdaten und Herstellerdateien gehören nicht hinein.

## Bestehende Evidenz

Die bisherigen Reports dokumentieren ältere, eng begrenzte Befunde: Geräte-/ABI-Hashes und statische Verbraucheranalyse in [reference-abi-2026-10-11.md](reference-abi-2026-10-11.md), Engineering- und begrenzte Runtimeversuche in [codesys-engineering-2026-10-12.md](codesys-engineering-2026-10-12.md), Offline-Mapping/Adapter in [originalstack-block-2026-10-12.md](originalstack-block-2026-10-12.md), sowie Isolationsprüfungen in [network-isolation.md](network-isolation.md) und [offline-carrier-2026-10-11.md](offline-carrier-2026-10-11.md). Diese Ergebnisse gelten nicht rückwirkend für den aktuellen Geräte-/Anwendungszustand und beweisen keine Simulation realer Module unter dem Originalstack.

Aktuell besitzen 750-1405/750-1504 und das feste virtuelle 750-466/750-550-Paar begrenzte native Runtimeevidence bei Modellpermit 0; 750-677 hat inzwischen eine begrenzte native Rohframeabnahme im synthetischen Erkundungsmodus; vollständige Moduldiagnose und PWM-Projektion bleiben offen. Sie sind kein aktuelles Hardwareinventar. Eine zusätzliche virtuelle Runtimeinstanz ist ein späteres Ziel.

## Start jedes neuen Arbeitsschritts

Arbeite am Repository `Mateo817/virtualWAGO`. Prüfe zuerst Gitstatus, Branch, HEAD, Remotezustand soweit autorisiert, AGENTS.md, README, ADR, Roadmap, Safety und aktuelle Evidence. Behandle Handoff- und Studienberichte als revisionsgebundene Quellen, nicht als Live-Inventar. Root führt alle Ziel-/VM-Aktionen allein durch. Keine private Zugangsinformation oder Herstellerartefakte ins öffentliche Repository übernehmen. Vor jedem Commit explizite Dateiauswahl und Prüfung privater Daten; kein pauschales `git add .`.

Geschützte Produktionsanlage ist absolut ausgeschlossen, auch read-only, Ping, Discovery oder als Quelle. Kein Netzwerk ohne lokale Richtlinie und eindeutige Gerätezuordnung. Firmware-/Bootloaderupdates, Kernel-/Originaltreiberersetzung, K-Bus-Masterumschaltung und physische Aktortests verlangen einen konkreten separat freigegebenen Versuchsplan. Softwarefreigabe allein deckt diese Schritte nicht ab.

## Delegation

Root bleibt alleiniger Geräte-/VM-Integrator. Für sinnvolle Offlineaufgaben tatsächliche `gpt-6-luna`-Worker verwenden; `gpt-6.1-sol` gezielt für schwierige Entscheidungen und Reviews. Worker führen keine Geräte-/VM-Aktionen aus. Eigene Prüfung als Self-Review kennzeichnen; Reviews sind kein Hardware- oder Ausführungsnachweis.
