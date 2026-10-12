# virtualWAGO

Forschung zur I/O-Simulation unterhalb des originalen WAGO/CODESYS-I/O-Stacks. Erstes Ziel ist die autorisierte Referenz-WAGO mit ihrer bereits laufenden originalen Runtime, dem nativen I/O-Manager und originalen WAGO-I/O-Treibern; die untere Hardwareanbindung soll erst nach Beleg ihrer Schnittstelle simuliert werden. Eine vollständig virtuelle Steuerung ist ein späteres Ziel. Unabhängiges Forschungsprojekt; keine behauptete Herstellerfreigabe.

**Stand: 12. Oktober 2026.** Das [Eigentümerfoto](docs/reference-module-photo-2026-10-12.md) belegt **750-430 → 750-530 → 750-600**; Revisionen und zyklische Kommunikation bleiben offen. Der [aktuelle Runtimeversuch](docs/runtime-bridge-2026-10-12.md) lud die originale Runtime und originalen I/O-Treiber mit dem Eigenprovider. Die native Initialisierung scheiterte an konkret beobachteten Boardmetadaten-/Signatur-/Hilfskomponentenpfaden. Virtuelle DI/DO sind noch nicht durch die Runtime bestätigt. Der kontrollierte Original-STOP-Wiederanlauf und unveränderte Hashes des bestehenden Bootprojekts und der Originalkomponenten sind geprüft. Der Eigenadapter besitzt nun einen begrenzten lokalen Modellkanal; eigene ARM-/IPC- und native Isolationsprüfungen bestanden.

Der [neue Controller-Lesezugang](docs/controller-metadata-2026-10-12.md) ist mit der unveränderten Originalbibliothek auf derselben Platine geprüft. Mit korrigiertem Vermittler startet die Originalruntime stabil; ihre I/O-Konfiguration scheitert jetzt mit Fehler16. Der Modellkanal bleibt konfiguriert0/Frames0. Vorhandene physische Module sind kein künftiger Laufzeitfallback.

## Entscheidung und Einstieg

Priorität hat zunächst ein realer Referenzversuch: originale Runtime, nativer I/O-Manager und originale WAGO-I/O-Treiber bleiben aktiv; simuliert wird erst unterhalb der nachgewiesenen Grenze. Die vorhandene verbundene Modulbestückung wird identifiziert, nicht aus den bisherigen Offlinekandidaten abgeleitet. Der konkrete ADI-Providerwechsel wurde vom Eigentümer freigegeben und begrenzt versucht; die native I/O-Abnahme steht aus. Vollständige Controller-Virtualisierung folgt später. Eine zusätzliche Runtime-Lizenz für eine virtuelle Instanz ist kein pauschaler Blocker des ersten Referenzziels. Details und Gates: [ADR-0003](docs/adr-0003.md).

- [Forschungsbefunde und Grenzen](docs/research.md)
- [Genuine Controllerdaten, Schreibschutz und nächste Abhängigkeiten](docs/controller-metadata-2026-10-12.md)
- [Modellkanal, Runtimeversuch und konkrete Fehler](docs/runtime-bridge-2026-10-12.md)
- [Modellkanal und isolierter Originalruntimeversuch](docs/adr-0005.md)
- [Architekturentscheidung](docs/adr-0001.md)
- [Priorität: reale Referenzsteuerung zuerst](docs/adr-0003.md)
- [Roadmap und Abnahmekriterien](docs/roadmap.md)
- [Ausgeführter Mapping-/ADI-Adapterblock](docs/originalstack-block-2026-10-12.md)
- [Konkreter Originalstack-Plan und Restgates](docs/next-originalstack-block.md)
- [Referenzversuchsplan](docs/real-controller-plan-2026-10-12.md) · [Beobachtungsprotokoll](docs/real-controller-observation-2026-10-12.md)
- [Sicherheits- und Zugriffsvertrag](docs/safety.md)
- [Öffentliche Quellen](docs/sources.md)
- [Lokaler Agent: Übergabe ohne Zugangsdaten](docs/handoff.md)
- [Vollständiges lokales Paket und Prototyp](docs/package.md)
- [Arbeitsregeln](AGENTS.md)

## Stand der Umsetzung

Der eigene Python-Forschungsprototyp, geprüfte synthetische Konfigurationen und Offlinewerkzeuge sind jetzt selektiv importiert. Die private Studie, Originalquellen, Herstellerheader/-binaries und Gerätezugänge bleiben außerhalb von Git. Das ist kein bereits lauffähiger Original-WAGO-Emulator.

Der frühere Mapping-/Adapterblock umfasst **99 PASS**: die damaligen 92 Tests plus sieben Mapping-Vertragstests. Der aktuelle Stand umfasst **130 PASS** (einschließlich eigenem IPC-Transport und Namespace-Argumentprüfung), einschließlich fünf neuer Digital-8-Builderprüfungen und der bisherigen 17 Offline-Parserprüfungen; frische Runtime-/Cachebeobachtungen und Grenzen stehen im [Beobachtungsbericht](docs/real-controller-observation-2026-10-12.md). Frühere Stände mit 52 und 65 Tests sind historische Zwischenstände, keine Fehler. Backend-/Werkzeug-PASS belegt keine originale Runtime oder reale Klemmen. Der [eigene IEC-Testquelltext](prototype/iec/minimal_io.st) wurde jetzt mit CODESYS 3.5.21.50 in ein natives Projekt übernommen und fehlerfrei offline kompiliert. Der [Engineeringbericht vom 12.10.2026](docs/codesys-engineering-2026-10-12.md) belegt außerdem einen begrenzten Lauf der internen Testanwendung auf der originalen Referenzruntime. Die Anwendung wurde danach entfernt; virtuelle I/O-Akzeptanz ist noch nicht nachgewiesen. Der frühere Windows-AppContainer-Test bleibt FAIL; nach ausdrücklicher Änderung des Arbeitsauftrags wird die regulär installierte IDE verwendet.

Der [neue Block](docs/originalstack-block-2026-10-12.md) ergänzt ein tatsächlich gespeichertes und wieder geöffnetes DI/DO-Mapping mit null Compilerfehlern/Warnungen. Die 34-Slot-Vertragsmatrix und der eigene ADI-Adapter sind implementiert; eigene statische und dynamisch geladene ARM-Harnessläufe sowie ihre Isolationskontrollen sind PASS. Das qualifiziert den eigenen sequenziellen Adapter, noch keinen originalen I/O-Verbraucher oder virtuellen Runtime-Lauf. [ADR-0002](docs/adr-0002.md) bindet Modellpackung, vollständige Frames und die eigene logische Watchdogzeit.

Neue [FW30-ABI-Befunde](docs/abi-research-2026-10-11.md) belegen den direkten ADI-Import durch originales `libIoDrvDal`, echte Headerlayouts und den Gerätezahlvertrag von `GetDeviceList`. Die Compile-only-Sonde verwendet ARM-Hard-Float-GCC 14.2 statt SDK-GCC 11.3.1. Der [tatsächliche Referenzbestand](docs/reference-abi-2026-10-11.md) ist jetzt selektiv gesichert: Der DAL-Provider ist bytegleich zum FW30-Artefakt, die originalen I/O-Verbraucher unterscheiden sich. ADI-Import, 136-Byte-Tablecopy und indirekte Lese-/Schreibeinträge sind für den aktuellen Verbraucher statisch belegt; die spätere originale Initialisierung wurde versucht und scheiterte; zyklische DI-/DO-Ausführung bleibt blockiert.

- [Aktuelles Geräte-/ABI-Ergebnis und Originalverbraucher-Kandidat](docs/reference-abi-2026-10-11.md)
- [M1/M2-Ausführung, Gates und nächster Einstieg](docs/execution-2026-10-11.md)
- [Prozessbezogene Referenz-Netzsperre](docs/network-isolation.md)
- [Offline-Carrier- und Isolationsbefunde, 11.10.2026](docs/offline-carrier-2026-10-11.md)
- [CODESYS-Engineering- und Device-Description-Verträge, 11.10.2026](docs/codesys-contract-2026-10-11.md)

```sh
python3 -m unittest discover -s tests -v
python3 -m prototype --config config/minimal.json < config/demo.jsonl
python3 tools/closed_loop_demo.py
```

Der öffentliche IPC-Transporttest benötigt zusätzlich einen nativen C-Compiler und wird ohne ihn übersprungen. Die private ARM-Adapterqualifikation benötigt authentische Herstellerheader; sie bleibt außerhalb der CI. Python 3.11+ und Standardbibliothek genügen für den Modellkern; ELF-Audit benötigt Linux und Binutils. `tools/reference_netns.py` zeigt standardmäßig nur einen bereinigten Plan. Seine aktive Nutzung braucht die private Zielrichtlinie und die in der Werkzeugdokumentation genannten Linux-Werkzeuge.

## Vertraulichkeit

Das Repository ist öffentlich. Keine Passwörter, konkreten privaten Geräteadressen, Firmwarekopien, Lizenzcontainer, privaten Projektarchive oder unbereinigten Referenztraces veröffentlichen. Vollständige Unterlagen und Gerätezuordnung bleiben im privaten Übergabepaket. Ein Klon allein erteilt keine Hardwarefreigabe; ohne lokale Zielrichtlinie sind Netzwerkaktionen gesperrt.
