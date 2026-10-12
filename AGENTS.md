# Arbeitsregeln für virtualWAGO

## Scope und Arbeitsablauf

GitHub ist Source of Truth für dieses Forschungsprojekt. Vor Änderungen Default-Branch, offene PRs, Regeln, relevante Quellen, Tests und CI frisch lesen. Entwicklung auf eigenem Branch; zusammenhängende Änderungen über PR. Keine direkten Entwicklungscommits auf main, kein Force-Push, keine Änderungen an fremden Produktrepositories. Die erstmalige Übernahme der Forschungsdokumentation nach main wurde vom Eigentümer beauftragt; daraus folgt keine pauschale Freigabe späterer Entwicklungsmerges.

Lies README.md, docs/research.md, docs/adr-0001.md, docs/roadmap.md, docs/safety.md und docs/handoff.md sowie docs/next-originalstack-block.md. Ältere Studien und Übergaben sind revisionsgebundene Ausgangsinformationen, keine Live-Inventare.

## Verbindliche Grenzen

- Emulator, dediziertes Referenzgerät und produktive Anlage strikt trennen. Die konkrete Allowlist und geschützte Anlage stehen ausschließlich in der lokalen, nicht versionierten Übergabe.
- Ohne lokale Zielrichtlinie und eindeutige Gerätezuordnung keine Netzwerkzugriffe. Die geschützte Anlage nicht einmal lesend, per Ping, Discovery oder als Kopierquelle verwenden.
- CI bleibt hardwarefrei. Keine produktiven Geräte, Host-D-Bus, Hostgeräte oder Docker-Sockets in Emulatoren durchreichen. Netzwerkisolation muss praktisch geprüft werden; diese Dokumentation implementiert noch keine Firewall.
- Der Eigentümer erlaubt bei Bedarf PLC-/Gateway-Installation ausschließlich auf dem neuen Referenzgerät. Zuerst Identität, Bestand, physische Isolation, Backup, Quellenbindung, Zielkonfiguration und Rollback prüfen. Passwörter unverändert lassen.
- Firmware-/Bootloaderupdates, Kernel-/Originaltreiberersetzung, K-Bus-Masterumschaltung und physische Aktortests verlangen einen konkreten separat freigegebenen Versuchsplan. Ein Teilblocker stoppt unabhängige Offlinearbeit nicht.
- Kein Lizenzbypass und kein Klonen geschützter Identitäten. Herstellerdateien nur bei geklärten Rechten verwenden; nicht in dieses öffentliche Repository hochladen.

## Technik und Evidence

Der bevorzugte Originalstack-Pfad erhält Runtime, nativen I/O-Manager und originale I/O-Treiber; ersetzt wird nur die belegte untere Hardwareanbindung. Fehlende interne CODESYS-Header sind keine pauschale Voraussetzung, solange deren Objekte durch den Originalmanager bereitgestellt werden. Ein Standalone-Harness ist optional und darf keinen Umweg mit erfundenen Strukturen erzwingen. Der Vertrag der tatsächlich ersetzten Grenze muss weiterhin belegt werden.

Keine erfundenen APIs, Structlayouts, Offsets, Modulkennungen oder Tools. FW30-Quellen nicht als FW31-ABI behandeln. Ein Exportname ist kein vollständiger Funktionsvertrag. Backend-Mock, Herstellerbeispiel, originaler I/O-Verbraucher, Runtime und Hardware sind getrennte Nachweisstufen.

Aussagen: VERIFIZIERT | HYPOTHESE | OFFEN | BLOCKED. Tests: PASS | FAIL | NOT_RUN | BLOCKED. Jeweils Version, Revision/Hashes, Konfiguration, Scope und Gründe festhalten. Alte PASS nicht auf neue Stände übertragen. Eigene Prüfung als Self-Review kennzeichnen; keine erfundenen unabhängigen Reviews oder Workerläufe.

Modelle stellen Signale und physikalische Reaktionen bereit, nicht nachgeschriebene SPS-Entscheidungslogik. Angeforderte und wirksame Ausgänge bleiben getrennt. Zeitdomänen, Modellannahmen und Fehlerreaktionen explizit dokumentieren. Materialle Architekturentscheidungen benötigen ein ADR mit Problem, Ist, Ziel, Alternativen, Entscheidung, Risiken und Verifikation.

Vor jedem Commit explizite Dateiauswahl und Prüfung auf private Daten. Kein blindes git add . aus einem gemischten Übergabeverzeichnis. Repository- und lokale Zugangsprompts niemals verwechseln.
