# virtualWAGO

**Offline-Werkstatt, 23.10.2026:** Der neue [Rust-/Web-Produktpfad](workbench/README.md)
ergänzt eine grafische Klemmenleiste, Live-I/O, versionierte nachladbare
Modulbeschreibungen und Reaktionsskripte. Er arbeitet ausschließlich mit eigenen
Signalmodellen; WAGO, CODESYS und VM sind im aktuellen Auftrag nicht freigegeben.
Architektur: [ADR-0013](docs/adr-0013.md). Erweiterungsstellen und Folgearbeit:
[Werkstattübergabe](docs/workbench-handoff.md). Die folgenden Runtime-/Hardware-
Berichte bleiben historische, getrennte Evidenzstufen.

**CAN2/DALI, 20.10.2026:** [Original-CAN-Stack und korrigierte PDO-Zuordnung](docs/can-native-boundary-2026-10-20.md): FW31-Projekt Build/Codegen/Reopen **PASS**. vcan-Linkadapter mit Originalruntime **PASS** im begrenzten Fenster; noch kein virtueller Teilnehmer. Reale Startup-SDOs und sechs zyklische PDO-Ströme **PASS** in der Kontrollkopie. IEC-/DALI-Abnahme **FAIL / OFFEN**: ausbleibende IEC-Protokollierung beziehungsweise Speicherfehler mit aktiven DALI-Bausteinen. Rücknahme aller 83 gesicherten Kopplerwerte und Original-STOP **PASS**. Keine DALI-Adressierung oder Lasttests. Die folgenden Meldungen sind historische Zwischenstände.

**PWM-Erkundung, 19.10.2026:** [Begrenzter Async-Kanal](docs/pwm-async-exploration-2026-10-19.md): Originalruntime RUN und sieben wechselnde angeforderte PWM-Ausgangsframes **PASS** mit explizit synthetischer UID/Registerantwort, Modellpermit 0. Original-STOP und sieben unveränderte Dateien nach Rücknahme **PASS**. 286 lokale Tests ohne Skip. Original-Moduldiagnose, PWM-Skalierung und Hardwareabgleich bleiben **OFFEN / NOT_RUN**. Die folgenden Meldungen dokumentieren frühere Stände.

**Native Integration, 19.10.2026:** [Analogeingang/-ausgang und digitale Regression](docs/native-integration-2026-10-19.md): virtuelle 750-466/750-550, 750-430/750-530 und 750-1405/750-1504 mit Originalruntime und Originaltreibern **PASS**, Modellpermit 0. Explizite virtuelle Registerkonfiguration gemäß [ADR-0009](docs/adr-0009.md); Hardwareabgleich **NOT_RUN**. PWM-Build/Reopen und Eigenprovider **PASS**, originale PWM-Runtime erreicht mit privatem D-Bus RUN; Frameabnahme **BLOCKED** am Modellfehler nach nicht unterstützter UID-Anfrage. 285 lokale Tests ohne Skip. Die folgenden Meldungen dokumentieren frühere Stände.

**Modulerweiterung, 19.10.2026:** [Bytepuffer und frische Digitalregression](docs/module-extension-2026-10-19.md): virtuelle 750-1405/750-1504 (16 DI/DO) und 750-430/750-530 mit Originalruntime/Originaltreibern **PASS**, Modellpermit 0; Original-STOP und unveränderte Dateien wieder bestätigt. 750-550-Signalmodell ergänzt; Analogpaar und PWM-Projekt Build/Reopen **PASS**. Native Analog-/PWM-Ausführung bleibt wegen Register-/Projektionsverträgen **BLOCKED / NOT_RUN**. 281 lokale Tests ohne Skip; der private Header benötigende Bytepuffer-Harness ist in öffentlicher CI ohne diese Header explizit NOT_RUN.

Forschung zur I/O-Simulation unterhalb des originalen WAGO/CODESYS-I/O-Stacks. Erstes Ziel ist die autorisierte Referenz-WAGO mit ihrer bereits laufenden originalen Runtime, dem nativen I/O-Manager und originalen WAGO-I/O-Treibern; die untere Hardwareanbindung soll erst nach Beleg ihrer Schnittstelle simuliert werden. Eine vollständig virtuelle Steuerung ist ein späteres Ziel. Unabhängiges Forschungsprojekt; keine behauptete Herstellerfreigabe.

**Aktueller Prototypblock, 18. Oktober 2026:** [Frischer nativer DI8-Lauf und
CAN-/DALI-Befund](docs/prototype-kbus-can-dali-2026-10-18.md): neuer
Acceptance-Prüfer, korrigierter nativer Builder und vier Signalpaare durch
Originalruntime/Originaltreiber **PASS**; Modellgate geschlossen. Die frisch
gebundene Referenz ist ein 750-8213, nach Rücknahme wieder STOP mit
unveränderten Originaldateien. CAN/DALI bleibt **BLOCKED**: Interface DOWN,
konkreter Koppler und Prozessdatenvertrag ungebunden; keine reale oder
virtuelle CAN-/DALI-Kommunikation behauptet. 247 hardwarefreie Tests PASS
ohne Skip am im Bericht gebundenen Implementierungsstand.

**Getrennter Referenzaufbau, 14. Oktober 2026:** Der [read-only gebundene
750-8212-Zwischenstand](docs/reference-8212-2026-10-14.md) hält eine bestehende
`Application` unverändert in RUN. Das private Frontfoto belegt im sichtbaren
Scope 750-1405 ×2, 750-1504 ×2, 750-466, 750-677 und 750-600; die abweichende
Offline-Projektfolge ist kein elektronisches Businventar. Es gab keinen
STOP/START, Download, Reboot, Provider-/Masterwechsel oder elektrischen I/O-Test.

**Früherer 750-8213-Referenzaufbau, Stand 13. Oktober 2026:** Die [reale
Originalruntime verarbeitet virtuelle Digitalmodule mit acht und 16
Kanälen](docs/native-digital-tests-2026-10-13.md): 750-430/750-530 und
750-1405/750-1504. Native Konfiguration, wechselnde Eingänge und vollständige
angeforderte Ausgangsframes sind bei dauerhaftem Modellpermit 0 **PASS**.
Wirksame Modellausgänge bleiben 0. Die ursprüngliche Anwendung dieses
750-8213-Aufbaus wurde nach jedem begrenzten Versuch unverändert in STOP
wiederhergestellt; die IDE-VM ist auf Datenträger pausiert. Diese Aussagen
beschreiben nicht den RUN-Zustand des neuen 750-8212. Hardwarevergleich, reale
Modulrevisionen, allgemeine Watchdog-/Fehler-/STOP-Semantik und aktives
Modellgate bleiben offen.

Das [frühere 750-8213-Eigentümerfoto](docs/reference-module-photo-2026-10-12.md)
belegt 750-430 → 750-530 → 750-600. Der damalige
[Controllerzugang](docs/controller-metadata-2026-10-12.md) liest genuine Daten
derselben 8213-Platine schreibgeschützt. TCM wurde im eigenen Projekt regulär
auf den dokumentierten Wert 0 gesetzt; Originalruntime, nativer I/O-Manager und
originale I/O-Treiber bleiben erhalten. Frühere
[Initfehler](docs/runtime-bridge-2026-10-12.md) bleiben revisionsgebunden
dokumentiert und werden nicht auf den 8212-Aufbau übertragen.

Der neue [Offline-Vertragsblock für750-466](docs/native-analog-contract-2026-10-13.md) bindet zwei native WORD-Eingänge und zusätzliche FW31-Registeranforderungen. Frischer nativer IDE-Build und schreibfreies Reopen sind PASS. Native Analogausführung bleibt offen. [ADR-0008](docs/adr-0008.md) beschreibt den Bytepufferausbau; [PWM und beide seriellen Pfade](docs/pwm-serial-contracts-2026-10-13.md) sowie der [digitale Lifecycleplan](docs/native-model-lifecycle-plan-2026-10-13.md) sind getrennt vorbereitet. Dieser Block kontaktierte keine SPS.

## Entscheidung und Einstieg

Priorität hat zunächst ein realer, ausdrücklich gebundener Referenzversuch:
originale Runtime, nativer I/O-Manager und originale WAGO-I/O-Treiber bleiben
aktiv; simuliert wird erst unterhalb der nachgewiesenen Grenze. Bestückung,
Zustand und Freigaben werden je Ziel gebunden, nicht aus Offlinekandidaten oder
dem jeweils anderen Gerät abgeleitet. Der konkrete ADI-Providerwechsel und die
native zyklische Byte-/Befehlsabnahme gehören zum früheren 750-8213. Der neue
750-8212-Block war ausschließlich read-only und erteilt keine solche
Umschaltfreigabe. Vollständige Controller-Virtualisierung folgt später.
Details und Gates: [ADR-0003](docs/adr-0003.md).

- [Forschungsbefunde und Grenzen](docs/research.md)
- [Genuine Controllerdaten, Schreibschutz und nächste Abhängigkeiten](docs/controller-metadata-2026-10-12.md)
- [Modellkanal, Runtimeversuch und konkrete Fehler](docs/runtime-bridge-2026-10-12.md)
- [Modellkanal und isolierter Originalruntimeversuch](docs/adr-0005.md)
- [Architekturentscheidung](docs/adr-0001.md)
- [Priorität: reale Referenzsteuerung zuerst](docs/adr-0003.md)
- [Roadmap und Abnahmekriterien](docs/roadmap.md)
- [Ausgeführter Mapping-/ADI-Adapterblock](docs/originalstack-block-2026-10-12.md)
- [Konkreter Originalstack-Plan und Restgates](docs/next-originalstack-block.md)
- [Private XE164/C166-Analyseablage und SOL/Luna-Leitprompt](analysis/xe164/README.md)
- [Gesicherte XE164-Analyseergebnisse, 18.10.2026](analysis/xe164/results/2026-10-18/README.md)
- [Referenzversuchsplan](docs/real-controller-plan-2026-10-12.md) · [Beobachtungsprotokoll](docs/real-controller-observation-2026-10-12.md)
- [Sicherheits- und Zugriffsvertrag](docs/safety.md)
- [Öffentliche Quellen](docs/sources.md)
- [Lokaler Agent: Übergabe ohne Zugangsdaten](docs/handoff.md)
- [Vollständiges lokales Paket und Prototyp](docs/package.md)
- [Arbeitsregeln](AGENTS.md)

## Stand der Umsetzung

Der ursprüngliche [Modulkatalog](docs/module-catalog-2026-10-12.md) dokumentiert 14 Standardartikel und neun ausführbare eigene Offlineprofile: Digital mit 2/4/8/16 Kanälen, normale Analogsignale der 750-466 und autonomes PWM Frq der 750-677. Gemischte Bestückungen, Kanalgrenzen und eigene Watchdoglease sind implementiert; die damalige lokale Suite umfasste **197 PASS**. Weitere dokumentierte Kandidaten bleiben unimplementiert. Dieser Katalogbericht ist historisch. Der neue Integrationsbericht oben qualifiziert beide Digitalprofile und ein festes Analogpaar; PWM, serielle Abnahme und Hardwarevergleich bleiben gesondert offen. Standalone-Modelle bedeuten keine entsprechend vielen nativen Runtimeprofile. Serielle Schnittstellen und andere PFC200-Ausstattungen stehen in der Roadmap.

```sh
python3 tools/module_catalog.py list
python3 tools/module_catalog.py demo 750-677
python3 tools/module_catalog.py simulate 750-430 750-530 750-466 750-677 < config/catalog-demo.jsonl
```

Der eigene Python-Forschungsprototyp, geprüfte synthetische Konfigurationen und Offlinewerkzeuge sind jetzt selektiv importiert. Die private Studie, Originalquellen, Herstellerheader/-binaries und Gerätezugänge bleiben außerhalb von Git. Das ist kein bereits lauffähiger Original-WAGO-Emulator.

Der frühere Mapping-/Adapterblock umfasst **99 PASS**: die damaligen 92 Tests plus sieben Mapping-Vertragstests. Der frühere Digital-8-Stand umfasst **130 PASS** (einschließlich eigenem IPC-Transport und Namespace-Argumentprüfung), einschließlich fünf neuer Digital-8-Builderprüfungen und der bisherigen 17 Offline-Parserprüfungen; frische Runtime-/Cachebeobachtungen und Grenzen stehen im [Beobachtungsbericht](docs/real-controller-observation-2026-10-12.md). Frühere Stände mit 52 und 65 Tests sind historische Zwischenstände, keine Fehler. Backend-/Werkzeug-PASS belegt keine originale Runtime oder reale Klemmen. Der [eigene IEC-Testquelltext](prototype/iec/minimal_io.st) wurde jetzt mit CODESYS 3.5.21.50 in ein natives Projekt übernommen und fehlerfrei offline kompiliert. Der [Engineeringbericht vom 12.10.2026](docs/codesys-engineering-2026-10-12.md) belegt außerdem einen begrenzten Lauf der internen Testanwendung auf der originalen Referenzruntime. Die Anwendung dieses historischen internen Versuchs wurde danach entfernt; er belegte damals keine virtuelle I/O-Akzeptanz. Der neue separate Digital-8-Zyklus ist oben gebunden. Der frühere Windows-AppContainer-Test bleibt FAIL; nach ausdrücklicher Änderung des Arbeitsauftrags wird die regulär installierte IDE verwendet.

Der [neue Block](docs/originalstack-block-2026-10-12.md) ergänzt ein tatsächlich gespeichertes und wieder geöffnetes DI/DO-Mapping mit null Compilerfehlern/Warnungen. Die 34-Slot-Vertragsmatrix und der eigene ADI-Adapter sind implementiert; eigene statische und dynamisch geladene ARM-Harnessläufe sowie ihre Isolationskontrollen sind PASS. Das qualifiziert den eigenen sequenziellen Adapter, noch keinen originalen I/O-Verbraucher oder virtuellen Runtime-Lauf. [ADR-0002](docs/adr-0002.md) bindet Modellpackung, vollständige Frames und die eigene logische Watchdogzeit.

Neue [FW30-ABI-Befunde](docs/abi-research-2026-10-11.md) belegen den direkten ADI-Import durch originales `libIoDrvDal`, echte Headerlayouts und den Gerätezahlvertrag von `GetDeviceList`. Die Compile-only-Sonde verwendet ARM-Hard-Float-GCC 14.2 statt SDK-GCC 11.3.1. Der [tatsächliche Referenzbestand](docs/reference-abi-2026-10-11.md) ist jetzt selektiv gesichert: Der DAL-Provider ist bytegleich zum FW30-Artefakt, die originalen I/O-Verbraucher unterscheiden sich. ADI-Import, 136-Byte-Tablecopy und indirekte Lese-/Schreibeinträge sind für den aktuellen Verbraucher statisch belegt; die ersten originalen Initversuche scheiterten. Die inzwischen erreichte begrenzte native Digital-8-/Digital-16-Abnahme steht im aktuellen Testbericht; frühere Fehler bleiben separat belegt.

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

Für einen neuen Chat: [kurze Übergabe mit Entscheidungen und nächsten Tests](docs/new-chat-handoff-2026-10-13.md). Öffentliche Quellen und Evidence stehen in Git; konkrete Zielrichtlinie, Zugänge, Herstellerartefakte und unbereinigte Geräte-/IDE-Belege bleiben in der privaten lokalen Übergabe.
