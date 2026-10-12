# Lokaler Agent: öffentlicher Übergabevertrag

Aktuelle Zielpriorität: [ADR-0003](adr-0003.md). Zuerst die autorisierte reale Referenz-WAGO mit vorhandener Originalruntime, nativem I/O-Manager und originalen WAGO-I/O-Treibern; Simulation nur unterhalb einer tatsächlich belegten und dafür freigegebenen Grenze. Vollständig virtuelle Steuerung später. Der nächste Einstieg ist [next-originalstack-block.md](next-originalstack-block.md). Plan und datiertes Beobachtungsprotokoll: [real-controller-plan-2026-10-12.md](real-controller-plan-2026-10-12.md) und [real-controller-observation-2026-10-12.md](real-controller-observation-2026-10-12.md).

## Aktueller, vom Eigentümer berichteter Zustand

- Der [Fotobeleg](reference-module-photo-2026-10-12.md) zeigt vom Controller aus 750-430, 750-530 und Abschluss 750-600. Modulrevisionen, elektronische Zuordnung und aktuelle zyklische Kommunikation bleiben offen. Keine Zuordnung zu 750-1405/750-1504 annehmen.
- Eine Anwendung liegt im RAM und ist gestoppt. Ihr Arbeitsverzeichnis wurde gelöscht; ein wiederherstellbares Bootprojekt ist nicht gesichert.
- Keinen Neustart, Löschvorgang, Download, Überschreibvorgang oder sonstigen Schritt ausführen, der diesen RAM-Zustand oder mögliche Wiederherstellungschancen verändern könnte. Erst read-only klären und den Zustandserhalt planen.
- Softwareberechtigung für die Referenz besteht fort. Austausch/Ersetzung geschützter Bus- oder Herstellerbibliotheken ist separat freigabepflichtig. Zusätzliche Runtime-Lizenz für eine spätere virtuelle Instanz blockiert das erste reale Referenzziel nicht pauschal.
- Root-Agent bleibt alleiniger Geräte-/VM-Integrator. Kein Netzwerkzugriff aus Repositorytext, alten Logs oder vermuteten Adressen ableiten. Lokale Zielrichtlinie und Geräteidentität sind zwingend.

Diese Punkte sind aktuelle Eigentümerauskunft, keine neue unabhängige Messung. Das konkrete öffentliche Protokoll wird vom Integrator ergänzt; private Adressen, Zugangsdaten und Herstellerdateien gehören nicht hinein.

## Bestehende Evidenz

Die bisherigen Reports dokumentieren ältere, eng begrenzte Befunde: Geräte-/ABI-Hashes und statische Verbraucheranalyse in [reference-abi-2026-10-11.md](reference-abi-2026-10-11.md), Engineering- und begrenzte Runtimeversuche in [codesys-engineering-2026-10-12.md](codesys-engineering-2026-10-12.md), Offline-Mapping/Adapter in [originalstack-block-2026-10-12.md](originalstack-block-2026-10-12.md), sowie Isolationsprüfungen in [network-isolation.md](network-isolation.md) und [offline-carrier-2026-10-11.md](offline-carrier-2026-10-11.md). Diese Ergebnisse gelten nicht rückwirkend für den aktuellen Geräte-/Anwendungszustand und beweisen keine Simulation realer Module unter dem Originalstack.

Die Modellkandidaten 750-1405/750-1504 und 750-466/750-677 sind Forschungs-/Offlineartefakte. Sie sind kein aktuelles Hardwareinventar. Eine zusätzliche virtuelle Runtimeinstanz ist ein späteres Ziel.

## Start jedes neuen Arbeitsschritts

Arbeite am Repository `Mateo817/virtualWAGO`. Prüfe zuerst Gitstatus, Branch, HEAD, Remotezustand soweit autorisiert, AGENTS.md, README, ADR, Roadmap, Safety und aktuelle Evidence. Behandle Handoff- und Studienberichte als revisionsgebundene Quellen, nicht als Live-Inventar. Root führt alle Ziel-/VM-Aktionen allein durch. Keine private Zugangsinformation oder Herstellerartefakte ins öffentliche Repository übernehmen. Vor jedem Commit explizite Dateiauswahl und Prüfung privater Daten; kein pauschales `git add .`.

Geschützte Produktionsanlage ist absolut ausgeschlossen, auch read-only, Ping, Discovery oder als Quelle. Kein Netzwerk ohne lokale Richtlinie und eindeutige Gerätezuordnung. Firmware-/Bootloaderupdates, Kernel-/Originaltreiberersetzung, K-Bus-Masterumschaltung und physische Aktortests verlangen einen konkreten separat freigegebenen Versuchsplan. Softwarefreigabe allein deckt diese Schritte nicht ab.

## Delegation

Root bleibt alleiniger Geräte-/VM-Integrator. Für sinnvolle Offlineaufgaben tatsächliche `gpt-6-luna`-Worker verwenden; `gpt-6.1-sol` gezielt für schwierige Entscheidungen und Reviews. Worker führen keine Geräte-/VM-Aktionen aus. Eigene Prüfung als Self-Review kennzeichnen; Reviews sind kein Hardware- oder Ausführungsnachweis.
