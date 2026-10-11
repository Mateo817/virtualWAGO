# virtualWAGO

Forschung zur Virtualisierung einer WAGO PFC200 G2 samt originaler SPS-Runtime und virtuellen K-Bus-I/O-Modulen. Unabhängiges Forschungsprojekt; keine behauptete Herstellerfreigabe.

**Stand: 11. Oktober 2026.** Das Referenzgerät meldet im Device Tree 750-8213 / ARMv7 und im Firmwaremarker 04.09.01(31). Die gesicherte Runtime enthält die Versionszeichenfolge 3.5.21.50; ein aktuelles Engineeringprofil ist damit nicht belegt. Hardwarestand, Serienidentität, Klemmenbestand und aktiver Projektzustand bleiben offen.

## Entscheidung und Einstieg

Bevorzugt wird **originaler ARM-Userspace + belegte Hardwareabstraktionsgrenze (B+C)**. Originale Runtime und I/O-Komponenten sollen möglichst erhalten bleiben; Ersatz erst an einer tatsächlich nachgewiesenen ADI-/DAL-/Treiber-ABI. Vollständige Boardemulation wird zunächst zurückgestellt. CODESYS Virtual Control mit eigener I/O-Schicht bleibt ein ausdrücklich andersartiger Alternativpfad.

- [Forschungsbefunde und Grenzen](docs/research.md)
- [Architekturentscheidung](docs/adr-0001.md)
- [Roadmap und Abnahmekriterien](docs/roadmap.md)
- [Sicherheits- und Zugriffsvertrag](docs/safety.md)
- [Öffentliche Quellen](docs/sources.md)
- [Lokaler Agent: Übergabe ohne Zugangsdaten](docs/handoff.md)
- [Vollständiges lokales Paket und Prototyp](docs/package.md)
- [Arbeitsregeln](AGENTS.md)

## Stand der Umsetzung

Der eigene Python-Forschungsprototyp, geprüfte synthetische Konfigurationen und Offlinewerkzeuge sind jetzt selektiv importiert. Die private Studie, Originalquellen, Herstellerheader/-binaries und Gerätezugänge bleiben außerhalb von Git. Das ist kein bereits lauffähiger Original-WAGO-Emulator.

Die 52 ursprünglichen Pakettests wurden frisch ausgeführt. Die erweiterte Suite umfasst 65 hardwarefreie Tests; zusätzlich wurde die Netzsperre lokal im Kernel geprüft. GitHub Actions führt die Python-Suite aus. Backend-/Werkzeug-PASS belegt keine originale Runtime oder reale Klemmen.

Neue [FW30-ABI-Befunde](docs/abi-research-2026-10-11.md) belegen den direkten ADI-Import durch originales `libIoDrvDal`, echte Headerlayouts und den Gerätezahlvertrag von `GetDeviceList`. Die Compile-only-Sonde verwendet ARM-Hard-Float-GCC 14.2 statt SDK-GCC 11.3.1. Der [tatsächliche Referenzbestand](docs/reference-abi-2026-10-11.md) ist jetzt selektiv gesichert: Der DAL-Provider ist bytegleich zum FW30-Artefakt, die originalen I/O-Verbraucher unterscheiden sich. ADI-Import, 136-Byte-Tablecopy und indirekte Lese-/Schreibeinträge sind für den aktuellen Verbraucher statisch belegt; originale Init-/DI-/DO-Ausführung bleibt blockiert.

- [Aktuelles Geräte-/ABI-Ergebnis und Originalverbraucher-Kandidat](docs/reference-abi-2026-10-11.md)
- [M1/M2-Ausführung, Gates und nächster Einstieg](docs/execution-2026-10-11.md)
- [Prozessbezogene Referenz-Netzsperre](docs/network-isolation.md)

```sh
python3 -m unittest discover -s tests -v
python3 -m prototype --config config/minimal.json < config/demo.jsonl
python3 tools/closed_loop_demo.py
```

Python 3.11+ und Standardbibliothek genügen für den Modellkern; ELF-Audit benötigt Linux und Binutils. `tools/reference_netns.py` zeigt standardmäßig nur einen bereinigten Plan. Seine aktive Nutzung braucht die private Zielrichtlinie und die in der Werkzeugdokumentation genannten Linux-Werkzeuge.

## Vertraulichkeit

Das Repository ist öffentlich. Keine Passwörter, konkreten privaten Geräteadressen, Firmwarekopien, Lizenzcontainer, privaten Projektarchive oder unbereinigten Referenztraces veröffentlichen. Vollständige Unterlagen und Gerätezuordnung bleiben im privaten Übergabepaket. Ein Klon allein erteilt keine Hardwarefreigabe; ohne lokale Zielrichtlinie sind Netzwerkaktionen gesperrt.
