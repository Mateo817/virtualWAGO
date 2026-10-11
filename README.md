# virtualWAGO

Forschung zur Virtualisierung einer WAGO PFC200 G2 samt originaler SPS-Runtime und virtuellen K-Bus-I/O-Modulen. Unabhängiges Forschungsprojekt; keine behauptete Herstellerfreigabe.

**Stand: 11. Oktober 2026.** Zielprofil: 750-8213 / ARMv7, Firmware 31 als bisherige Zielannahme. Engineering 3.5.21.50 ist keine verifizierte Runtime-Binärversion. Das neu bereitgestellte Referenzgerät muss vollständig neu inventarisiert werden.

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

Dieses Repository startet mit einer **Dokumentationsbasis**. Der bereits vorhandene, separat ausgelieferte Python-Forschungsprototyp ist noch nicht in diesen Git-Baum importiert. Sein vollständiger Quellcode, 52 Tests, die 46-seitige Studie und historische Evidence liegen im lokalen Übergabepaket. Das ist kein bereits lauffähiger Original-WAGO-Emulator.

Die vorhandenen 52 Tests wurden bei der Übergabe auf dem unveränderten Paket erneut erfolgreich ausgeführt. Dieser PASS gilt nur für dessen Backend-/Werkzeugquellen, nicht für eine originale Runtime, reale Klemmen oder diesen Dokumentationscommit. Im Bootstrap sind keine GitHub-Actions-Workflows eingerichtet.

## Vertraulichkeit

Das Repository ist öffentlich. Keine Passwörter, konkreten privaten Geräteadressen, Firmwarekopien, Lizenzcontainer, privaten Projektarchive oder unbereinigten Referenztraces veröffentlichen. Vollständige Unterlagen und Gerätezuordnung bleiben im privaten Übergabepaket. Ein Klon allein erteilt keine Hardwarefreigabe; ohne lokale Zielrichtlinie sind Netzwerkaktionen gesperrt.
