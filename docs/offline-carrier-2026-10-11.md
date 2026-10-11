# Offline-Carrier- und Isolationsbefunde

Stand: 11.10.2026. Dieser Bericht beschreibt begrenzte, eigene ARM-Carrier- und Namespace-Probes. Er belegt weder eine gestartete WAGO-Komponente noch eine Firmware-/Runtime-Sandbox. Maschinenlesbare, bereinigte Prüfbilanz und weitere Hashes: [offline-carrier-validation-2026-10-11.json](../evidence/offline-carrier-validation-2026-10-11.json).

## Ergebnis und Scope

**PASS, eigene Probe:** Ein ARM-Layout-/Carrierprogramm lief mit originalem GNU-Lader und originaler libc. Es führte keinen DAL-, IoDrv- oder Runtime-Code aus. Die Grundlage ist Repository-Revision `4bca28bc4dc40d2602b0b6aa4763a994bf3bc889` und der gepinnte FW30-SDK-Stand `252209115885442bac7359a2ff1cfa4efb3a9c84`. Der vollständige private Evidence-Datensatz wurde auf SHA-256 `002d3032761ca4cca98205712f6a9df6b688dbc681eec4de1ca1c3efbcd16d4a` geprüft; private Quelldateien und Rohdaten bleiben außerhalb dieses Repositories.

Die ARM-Sonde maß mit GCC 14.2 die Layouts aus den originalen FW30-Headern: Pointer 4 Byte, `size_t` 4 Byte, `bool` 1 Byte, ADI-Tabelle 136 Byte, Geräteinfo 8 Byte, Gerätekennung 4 Byte, Ereignisse 4 Byte, Funktionszeiger-Offsets für `GetDeviceList` 12 Byte, `ReadBytes` 80 Byte und `WriteBytes` 60 Byte; Erfolgs- und Fehlerwerte 0 beziehungsweise -1. Der Hersteller-SDK-Compiler GCC 11.3.1 wurde hierfür nicht verwendet. Das Ergebnis ist eine Header-/Layoutmessung, keine vollständige ABI- oder Aufrufqualifikation. B+C bleibt eine **HYPOTHESE**; eine Boardemulation wurde nicht gebaut.

## Isolationsprobe

`tools/offline_sandbox.py` zeigt standardmäßig nur einen Plan. In der aktiven, eigens gestarteten Probe kamen User-, Netzwerk-, Mount-, PID-, IPC- und UTS-Namespaces, ein privates Read-only-Root mit vier Dateien und QEMU zum Einsatz. `tools/offline_isolation_probe.c` bestätigte fünf getrennte Namespace-Identitäten, null Capabilities, `no_new_privs=1`, Read-only-Root und eine bereinigte Umgebung. Im Gast waren weder der Host-Sentinel noch `/sys`, die geprüften Pfade `/dev/kbus0`, `/dev/uio0`, `/dev/eeprom`, `/dev/ttyKbus` sowie Host-D-Bus- oder Docker-Sockets verfügbar. Zwei kontrollierte, ausschließlich eigene Hostlistener waren vom Gast nicht erreichbar; die Host-Baseline war PASS.

Die synthetische Negativkontrolle legte eine Gastdatei mit demselben Sentinel-Namen an. Die Probe erkannte sie wie erwartet und endete mit `exit 1`. Dabei wurde kein Host-Mount eingebunden. Dies ist **PASS** für die begrenzte Probe einschließlich Negativkontrolle. Es gibt keinen aggregierten cgroup-Ressourcenvertrag. Die Ergebnisse gelten nur für diese geprüften eigenen Programme und Konfigurationen; sie sind kein pauschaler Firmware-Sandbox-PASS und keine M3-Negativkontrolle.

## Statische ELF-Verfügbarkeit

126 gesicherte ELF-Dateien wurden statisch untersucht. Bei den vier unten genannten Startkomponenten fehlen im über SONAME/Dateinamen aufgebauten Index keine transitiven `DT_NEEDED`-Dateien; Mehrdeutigkeiten wurden dort ebenfalls nicht gefunden. Die untersuchten ELF-Gruppen umfassen Runtime 14, DAL 9, IoDrvDal 14 und Kbus 25 Dateien. Diese statische Prüfung zeigt nur, dass die referenzierten Dateien auffindbar waren. Sie löst keine dynamische Loader-Closure auf und prüft weder `dlopen`-Pfade noch Serviceversionen.

## Getrennte Nachweisstufen und offene Gates

| Stufe | Stand |
|---|---|
| Modell und hardwarefreie Backend-Suite | **PASS**, aktuell 82 Tests; keine Hersteller-Runtime-Evidence |
| Eigene ARM-Layout-/Carrier-Probe | **PASS**, originaler Lader und libc; kein DAL-/IoDrv-/Runtime-Code |
| Eigene Namespace-/Isolationsprobe | **PASS** für die dokumentierten Probes und Konfigurationen; keine pauschale Firmware-Sandbox-Freigabe |
| Originaler I/O-Verbraucher und zyklisches DI/DO | **BLOCKED**, CODESYS-Generikverträge und vollständige Modulverträge fehlen |
| Originale CODESYS-Runtime | **NOT_RUN** |
| Hardware und Klemmen | **OFFEN**, vollständige M1-Hardwareidentität und Klemmenbestand fehlen |

Der nächste M1/M2-Einstieg sind die echten CODESYS-Headerverträge für `INIT_STRUCT`, `IoConfigConnectorMap` und die Komponentenregistrierung sowie die DeviceDescriptions für 750-1405 und 750-1504. Vollständige Hardwareidentität und Klemmenbestand sind weiterhin offen.

## Öffentliche Versionsquelle

Die [WAGO Release Notes für 750-8x1x](https://downloadcenter.wago.com/api/uploads/2026_04_30_Release_Notes_750_8x1x_d0696a9a8d.pdf) führen Firmware 04.09.01 (31) als getestet und freigegeben mit CODESYS IDE 64 Bit 3.5.21.5 und Device Description 2.0.9.2; darin ist auch der Artikel 750-8213 aufgeführt. Das ist die Herstellerzuordnung der Engineering-/Gerätebeschreibungsversion, nicht die Runtime-Versionszeichenfolge. Der gesicherte Runtime-ELF-String `3.5.21.50` bleibt ein separater Binärbefund. Ein installierter Windows-Engineeringstand ist **OFFEN**. SHA-256 des verwendeten Release-Notes-PDF: `7504776b952f84eb93ff50f53898025f4372eea98976396e7d7cb255b4e73378`.

Dieses Dokument ist ein **Self-Review** der begrenzten Carrier-Evidence. Es beansprucht keine unabhängige Hardware-, Lizenz- oder Laufzeitfreigabe.

## Reproduzierbarer Einstieg

Der Standardaufruf erzeugt nur einen Plan, ohne Namespace oder Gastprogramm zu starten:

```sh
python3 tools/offline_sandbox.py
```

Zur Ausführung müssen der tatsächlich vorhandene vertrauenswürdige Bubblewrap-Pfad, ein ausdrücklich zusammengestelltes privates Minimal-Root und das statische Host-QEMU gebunden werden. Die folgenden Variablen sind vom Betreiber zu setzen, keine angenommenen Installationspfade:

```sh
python3 tools/offline_sandbox.py \
  --bwrap "$RESEARCH_BWRAP" --rootfs "$RESEARCH_ROOTFS" --qemu "$RESEARCH_QEMU" \
  --execute --timeout-seconds 15 -- \
  /lib/ld-linux-armhf.so.3 --library-path /usr/lib /opt/research/abi-layout
```

Diese Gastpfade gehören zum dokumentierten Vierdateien-Root. `tools/abi_layout_probe.c` bleibt standardmäßig Compile-only; sein optionales eigenes `main` wird ausschließlich durch `RESEARCH_RUNTIME_LAYOUT_PROBE` eingeschaltet und ruft keine DAL-Funktion auf. Die Isolation-Sonde erhält einen eigens erzeugten Host-Sentinel, die tatsächlichen Namespace-Inodes und zwei zuvor positiv geprüfte lokale Listener vom privaten Elternprozess; beliebige Beispielwerte würden diesen Nachweis ungültig machen. Die Rootprüfung erkennt bestimmte sensible Dateinamen, aber keine beliebig benannten Geheimnisse. Deshalb wird niemals ein vollständiges Geräte-Dateisystem als Gastroot übernommen.

**PASS, unabhängiger Offline-Review:** Ein separater Sol-Worker prüfte den endgültigen Code, ELF-Metadaten und Artefakthashes und führte selbst alle 82 hardwarefreien Tests aus. Er führte keine Gastprogramme oder Hardwaretests aus. Sein Review ersetzt weder den durch den Integrator ausgeführten Carrier-Test noch eine Lizenz-/Hardwarefreigabe; Quelle und Scope stehen in der maschinenlesbaren Evidence.
