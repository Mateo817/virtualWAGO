# Lokales Übergabepaket und Prototyp

Die öffentliche Repositorybasis enthält Befunde, Vorschläge und Arbeitsverträge. Das vollständige lokale Paket enthält zusätzlich die unveränderte 46-seitige Machbarkeitsstudie in PDF/Markdown/HTML, drei ausführliche Forschungs-ADRs, Quelleninventar, Prototyp, Tests, Werkzeuge und private Ausgangsunterlagen. Konkrete Gerätezuordnung und Zugangsdaten sind separat und nicht für Git bestimmt.

## Unveränderter ursprünglicher Forschungsbestand

Originaldatei: `WAGO_PFC200_Forschungspaket.zip`

SHA-256: `34b8910b6015468e2b6401629060ba0e792f90ba91bec7841ec59b2032e891f8`

Enthaltenes Root: `wago-virtualization-research/`. Im neuen privaten Übergabepaket liegt die entpackte, inhaltlich unveränderte Fassung unter `private/research/`. Ihr `MANIFEST.sha256` bindet die ursprünglichen Dateien; ergänzende aktuelle Evidence liegt außerhalb dieses historischen Verzeichnisses.

## Ausführen im Forschungspaket

Umgebung: Python 3.11+ mit Standardbibliothek; tatsächlich erneut getestet auf Python 3.13.5 / Linux x86-64. ELF-Audit benötigt GNU Binutils. Keine WAGO-/CODESYS-Runtime enthalten.

```bash
cd private/research
sha256sum -c MANIFEST.sha256
python3 --version
python3 -m unittest discover -s tests -v
python3 -m prototype --config config/minimal.json < config/demo.jsonl
python3 tools/closed_loop_demo.py
```

Python/Binutils nur bei Bedarf auf dem isolierten Debian-Forschungsrechner installieren, nicht pauschal auf der WAGO:

```bash
sudo apt-get update
sudo apt-get install --no-install-recommends python3 binutils
```

Paketinstallation in dieser Übergabe NOT_RUN, weil die Werkzeuge vorhanden waren. Windows-Ausführung NOT_RUN. Keine Hardware wurde kontaktiert.

## Selektiver Codeimport

Der lokale Agent darf den eigenen Forschungscode nach Prüfung in einen Entwicklungsbranch von virtualWAGO übernehmen. Kandidaten sind `prototype/`, `tests/`, `tools/` sowie die geprüften synthetischen `config/`-Dateien. Vorher Inhalte, Referenzen, Tests und Herkunft prüfen; private Originalquellen, Inventare, Vollstudie und Traces nicht mitkopieren. Historische Quellhashes erhalten und nach dem Import für den neuen Git-HEAD neu testen. Kein blindes Gesamtverzeichnis-Importieren.

Der bestehende Collector kennt die neue Zielrichtlinie noch nicht. Sein Dry-Run ist keine durchgesetzte Remote-Hostprüfung; vor Remoteeinsatz zusätzliche Ziel-/Identitätsprüfung und lokale Netzisolation umsetzen.
