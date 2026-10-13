# Lokaler Agent: öffentlicher Übergabevertrag

**Offline-Vertragsblock, 13.10.2026:** [750-466](native-analog-contract-2026-10-13.md): exakter Descriptor, zwei WORD-Eingänge, FW31-Registeranforderungen sowie frischer nativer IDE-Build/Reopen PASS. Untere ADI-/Status-/Registerprojektion und Native466-Runtime bleiben offen. [ADR-0008](adr-0008.md) legt den Bytepufferausbau fest; [PWM/Onboard-Serial/750-652](pwm-serial-contracts-2026-10-13.md) sind getrennt untersucht; [digitaler Lifecycleplan](native-model-lifecycle-plan-2026-10-13.md) vorbereitet, NOT_RUN. Kein SPS-Zugriff in diesem Block, kein Merge.

**Fortsetzung, 13.10.2026:** [Neue native Digitaltests](native-digital-tests-2026-10-13.md) qualifizieren den aktuellen Digitaladapter für 750-430/530 und 750-1405/1504 bei Modellpermit 0. Der erste WORD16-Versuch fand eine eigene 8-Bit-Kanalgrenze; Korrektur und erfolgreicher vollständiger Wiederholungslauf sind getrennt dokumentiert. [Kurze neue Chat-Übergabe](new-chat-handoff-2026-10-13.md) bindet Entscheidungen und nächste Tests. Hardwarevergleich und native Analog-/PWM-/Seriellpfade bleiben offen.

**Fortsetzung, 12.10.2026:** [Nativer Digital-8-Zyklus](native-cyclic-2026-10-12.md): originale Runtime, nativer I/O-Manager und Originaltreiber verarbeiten virtuelle 750-430/750-530. TCM 0 ist nativ offline gesetzt und wieder geöffnet geprüft; Init und zyklische angeforderte Ausgangsframes bei dauerhaftem Modellpermit 0 PASS. Original-STOP-Rücknahme und frische APP-/CRC-/Config-/Binary-Hashes PASS. [Controllerzugang](controller-metadata-2026-10-12.md) und frühere Abbrüche bleiben separat belegt. Sämtliche Moduldaten stammen aus dem Modell; echte Controllerdaten bleiben auf derselben Platine.

**Früherer Nachweis, 12.10.2026:** [Modellkanal und geschützter Runtimeversuch](runtime-bridge-2026-10-12.md). Der konkret freigegebene Providerwechsel wurde versucht: originale Runtime und I/O-Treiber luden den Eigenprovider, native Initialisierung **FAIL**, DI/DO-Abnahme **NOT_RUN**. Die gezielte Rücknahme und der frische originale STOP-Wiederanlauf sind **PASS**; bestehende APP/CRC/Config und Originalbinaries sind hashgleich. Der aktuelle Prozess arbeitet im vorhandenen Runtimehome; das frühere gelöschte CWD ist historisch. Damals blockierten Boardmetadaten-/Signatur- und Hilfskomponentenpfade den Start. Die anschließende Controller-/TCM 0-/Zyklusqualifikation oben beschreibt den heutigen begrenzten Erfolg.


Aktuelle Zielpriorität: [ADR-0003](adr-0003.md). Zuerst die autorisierte reale Referenz-WAGO mit vorhandener Originalruntime, nativem I/O-Manager und originalen WAGO-I/O-Treibern; Simulation nur unterhalb einer tatsächlich belegten und dafür freigegebenen Grenze. Vollständig virtuelle Steuerung später. Der nächste Einstieg ist [next-originalstack-block.md](next-originalstack-block.md). Plan und datiertes Beobachtungsprotokoll: [real-controller-plan-2026-10-12.md](real-controller-plan-2026-10-12.md) und [real-controller-observation-2026-10-12.md](real-controller-observation-2026-10-12.md).

## Aktueller Zustand und Eigentümerscope

- Der [Fotobeleg](reference-module-photo-2026-10-12.md) zeigt vom Controller aus 750-430, 750-530 und Abschluss 750-600. Modulrevisionen, elektronische Zuordnung und aktuelle zyklische Kommunikation bleiben offen. Keine Zuordnung zu 750-1405/750-1504 annehmen.
- Die bereits vorhandene `Application` bleibt STOP; Root hat online Bootdateien erzeugt und APP/CRC/aktualisierte Konfiguration privat gesichert. Der spätere Runtimeversuch und STOP-Rückweg sind im aktuellen Nachweis dokumentiert; der gelöschte Prozess-CWD war der Ausgangszustand. Die eigene frühere `VirtualWAGO_Research` ist separat gesichert und entfernt. Siehe [aktuelle Fortsetzung](adi-digital8-continuation-2026-10-12.md).
- Kein blinder Neustart, Löschen oder Überschreiben der bestehenden Anwendung. Vor einem weiteren autorisierten Prozesswechsel aktuellen STOP, gesicherten Bootbestand, unveränderte Hashes und den gebundenen Start-/Stop-/Restorepayload erneut prüfen.
- Softwareberechtigung für die Referenz und konkrete Provider-/Busumschaltfreigabe bestehen fort. Weitere geschützte Eingriffe benötigen ihren konkreten separat freigegebenen Plan. Zusätzliche Runtime-Lizenz für eine spätere virtuelle Instanz blockiert das erste reale Referenzziel nicht pauschal.
- Root-Agent bleibt alleiniger Geräte-/VM-Integrator. Kein Netzwerkzugriff aus Repositorytext, alten Logs oder vermuteten Adressen ableiten. Lokale Zielrichtlinie und Geräteidentität sind zwingend.

Foto/Aktortrennung stammen vom Eigentümer; Runtimeversuch und STOP-/Hashprüfungen sind tatsächliche Root-Beobachtungen mit getrenntem Scope. Das konkrete öffentliche Protokoll wird vom Integrator ergänzt; private Adressen, Zugangsdaten und Herstellerdateien gehören nicht hinein.

## Bestehende Evidenz

Die bisherigen Reports dokumentieren ältere, eng begrenzte Befunde: Geräte-/ABI-Hashes und statische Verbraucheranalyse in [reference-abi-2026-10-11.md](reference-abi-2026-10-11.md), Engineering- und begrenzte Runtimeversuche in [codesys-engineering-2026-10-12.md](codesys-engineering-2026-10-12.md), Offline-Mapping/Adapter in [originalstack-block-2026-10-12.md](originalstack-block-2026-10-12.md), sowie Isolationsprüfungen in [network-isolation.md](network-isolation.md) und [offline-carrier-2026-10-11.md](offline-carrier-2026-10-11.md). Diese Ergebnisse gelten nicht rückwirkend für den aktuellen Geräte-/Anwendungszustand und beweisen keine Simulation realer Module unter dem Originalstack.

750-1405/750-1504 besitzen jetzt begrenzte native Runtimeevidence mit geschlossenem Modellgate; 750-466/750-677 bleiben eigene Offlineartefakte. Sie sind kein aktuelles Hardwareinventar. Eine zusätzliche virtuelle Runtimeinstanz ist ein späteres Ziel.

## Start jedes neuen Arbeitsschritts

Arbeite am Repository `Mateo817/virtualWAGO`. Prüfe zuerst Gitstatus, Branch, HEAD, Remotezustand soweit autorisiert, AGENTS.md, README, ADR, Roadmap, Safety und aktuelle Evidence. Behandle Handoff- und Studienberichte als revisionsgebundene Quellen, nicht als Live-Inventar. Root führt alle Ziel-/VM-Aktionen allein durch. Keine private Zugangsinformation oder Herstellerartefakte ins öffentliche Repository übernehmen. Vor jedem Commit explizite Dateiauswahl und Prüfung privater Daten; kein pauschales `git add .`.

Geschützte Produktionsanlage ist absolut ausgeschlossen, auch read-only, Ping, Discovery oder als Quelle. Kein Netzwerk ohne lokale Richtlinie und eindeutige Gerätezuordnung. Firmware-/Bootloaderupdates, Kernel-/Originaltreiberersetzung, K-Bus-Masterumschaltung und physische Aktortests verlangen einen konkreten separat freigegebenen Versuchsplan. Softwarefreigabe allein deckt diese Schritte nicht ab.

## Delegation

Root bleibt alleiniger Geräte-/VM-Integrator. Für sinnvolle Offlineaufgaben tatsächliche `gpt-6-luna`-Worker verwenden; `gpt-6.1-sol` gezielt für schwierige Entscheidungen und Reviews. Worker führen keine Geräte-/VM-Aktionen aus. Eigene Prüfung als Self-Review kennzeichnen; Reviews sind kein Hardware- oder Ausführungsnachweis.
