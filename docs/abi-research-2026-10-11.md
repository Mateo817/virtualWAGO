# M2-Schnittstellenrecherche: WAGO-ADI/DAL und parallele Komponenten

Stand: 11.10.2026. Offline-Auswertung öffentlicher Herstellerquellen; keine Verbindung zu einer SPS oder Anlage, kein Firmwarestart und kein Firmwarebuild. Diese Evidence gilt ausschließlich für den unten genannten FW30-SDK-Snapshot. Sie belegt weder die FW31-Installation des Prüfstands noch die Laufzeitakzeptanz eines Shims.

## Ergebnis

**VERIFIZIERT:** Der angegebene SDK-Pin ist der öffentliche Tag `FW30-V04.08.09` im Repository [`WAGO/pfc-firmware-sdk-G2`](https://github.com/WAGO/pfc-firmware-sdk-G2/tree/252209115885442bac7359a2ff1cfa4efb3a9c84), Commit `252209115885442bac7359a2ff1cfa4efb3a9c84`. `git ls-remote` bestätigte die Tag-Auflösung auf genau diesen Commit. Das Repository war auf den Commit `252209115885442bac7359a2ff1cfa4efb3a9c84` gesetzt; seine Projekt-README warnt, Binär- und Installationspakete verschiedener Firmwarestände nicht zu mischen.

**VERIFIZIERT:** Dieser Commit enthält vollständige DAL-Headerarchive und CODESYS-Komponenten-Headerarchive im ARMHF-Plattformpaket. Das wichtigste Archiv `dal_1.0.1_armhf.tgz` enthält unter anderem `usr/include/dal/adi_application_interface.h` und `dal_types.h`. SHA-256 des Archivs: `dd385c0199affca31a8cc5771290871bc161a8066fcf009e5228f7cfb2bf5b35`; Git-Blob des Archivs: `56e9d43f78571ff3431ed4415c12fd881a63bf62`. Das Header-Archiv `cds3-iodrvdal_1.0.2_armhf.tgz` enthält die IoDrvDal- und CmpDal-Header; Git-Blob `a4fd1d87f0284f0c2a2a05d61b0807c71ffd6f09`.

**Rechtevorbehalt:** Die DAL-, libpackbus- und IoDrvDal-Header enthalten WAGO-Hinweise zu proprietären Rechten und verweisen auf eine Lizenzvereinbarung. Die allgemeine MPL-2.0-Datei des SDK hebt diesen individuellen Hinweis nicht auf. Die Archive sind öffentlich abrufbar und als Herstellerheader echt; öffentliche Abrufbarkeit ist keine Freigabe, die Header in dieses Repository zu kopieren oder weiterzuverteilen. Die hier beauftragte Offlineanalyse und Compile-only-Prüfung wurde lokal ausgeführt; Rechte für spätere Runtime-/Shim-Nutzung bleiben separat **OFFEN**. Quellarchive und extrahierte Header liegen nur lokal im privaten Research-Verzeichnis; dieses Dokument gibt keine Herstellerdateien wieder.

## ADI-Verbraucher und nachgewiesene Aufrufoberfläche

**VERIFIZIERT für den FW30-Paketstand:** Das ARMHF-Paket `cds3-iodrvdal_1.0.2_armhf.ipk` enthält `libIoDrvDal.so.1.0.2`. Dessen ELF ist ELF32, little-endian, ARM, mit ARMv7/VFP-Argumentübergabe. Statische `readelf`-Auswertung zeigt `DT_NEEDED: libdal.so` und den undefinierten dynamischen Import `adi_GetApplicationInterface`. Der untersuchte Binärhash ist SHA-256 `1c1d3a4857823b01f5592118c90a9a7032192fa7f018e4b149e4c5b39d0a4d09`. Dies ist direkter Nachweis, dass der FW30-IoDrvDal-Binärbestand den ADI-Einstieg dynamisch konsumiert. Kein ELF wurde ausgeführt.

Das ebenfalls enthaltene `libIoDrvKbus.so.0.0.1` benötigt `libIoDrvDal.so`, `libdiagnostic.so`, `libwago_dbus.so` und mehrere GLib-/D-Bus-Libraries; es importiert `adi_GetApplicationInterface` nicht direkt. Das belegt im FW30-Paketgraphen eine mittelbare K-Bus→IoDrvDal→DAL-Beziehung sowie separate Diagnose-/D-Bus-Abhängigkeiten, aber nicht deren vollständige Aufrufreihenfolge. SHA-256 des untersuchten K-Bus-ELFs: `090611c4077ee8302e7e998b5e133614d123918f3e6844e5529fc621acc83bde`.

Der echte Header `adi_application_interface.h` deklariert `adi_GetApplicationInterface(void)` mit Rückgabe `tApplicationDeviceInterface *`. Die Funktionstabelle enthält im FW30-Header diese Felder:

`Init`, `Exit`, `ScanDevices`, `GetDeviceList`, `OpenDevice`, `CloseDevice`, `IsDeviceOpen`, `GetDeviceName`, `GetDeviceFlags`, `GetIoSizes`, `ConfigureSubdevice`, `ConfigureDevice`, `WriteStart`, `WriteBit`, `WriteBool`, `WriteBytes`, `WriteEnd`, `ReadStart`, `ReadBit`, `ReadBool`, `ReadBytes`, `ReadEnd`, `DiagnoseGetDeviceState`, `DiagnoseGetSubdeviceState`, `RegisterEventHandler`, `UnregisterEventHandler`, `GetLastError`, `ApplicationStateChanged`, `CallDeviceSpecificFunction`, `VCallDeviceSpecificFunction`, `WatchdogSetTime`, `WatchdogStart`, `WatchdogStop`, `WatchdogTrigger`.

Das Interface beschreibt damit Prozessdaten-Transaktionen, Enumeration/Konfiguration, Diagnose, Events und Watchdog-Funktionen als getrennte Operationen. Die Headerdeklarationen liefern Typen und Feldreihenfolge für diesen FW30-Stand; die ARM32-`sizeof`-/`offsetof`-Sonde wurde mit GCC 14.2.0 kompiliert. Das ergibt keine Herstellerbuild- oder FW31-ABI.

**VERIFIZIERTE Herstellerbeispiele:** [`WAGO/pfc-howtos`](https://github.com/WAGO/pfc-howtos/tree/a116875ddfa9154f6a9be38e1a02ac5759e1af29) enthält mehrere Verbraucher von `adi_GetApplicationInterface`, darunter `kbusdemo.c`, `getkbusinfo.c` und `getkbusheader.c` aus `HowTo_ADI-MyKBusApplikation`, sowie ein serielles K-Bus-Beispiel und ein Registerzugriffsbeispiel. Das Repo-HEAD zum Abruf war `a116875ddfa9154f6a9be38e1a02ac5759e1af29`; die ADI-Anleitung wurde in Commit `1d29f9dc1557759e2b7e9c74591a731f55d0fdec` hinzugefügt. Der bekannte C-Blob `kbusdemo.c` ist `c6af1246395d525d8340ce4616aa9e8c9c09d390`; `adi_functions.txt` ist `c9fc10d017f6d4f895a86c0341feb1ed3154edf7`.

Das Beispiel demonstriert `Init`, `ScanDevices`, `GetDeviceList`, `OpenDevice`, `ApplicationStateChanged`, den gerätespezifischen Dispatch `libpackbus_Push`, `WatchdogTrigger`, eingerahmtes `ReadStart/ReadBytes/ReadEnd` und `WriteStart/WriteBytes/WriteEnd`, anschließend Schließen und `Exit`. Es ist ein Herstellerbeispiel mit eigener C-Anwendung, kein Nachweis, welche Funktionen die Firmware-31-CODESYS-Runtime aufruft.

**VERIFIZIERT – Compile-only-Vorbereitung mit Originalbeispiel:** Unverändertes `kbusdemo.c` aus dieser HowTos-Revision ließ sich mit den privaten Originalheadern aus dem genannten FW30-DAL-Archiv als ARM32-Objekt kompilieren. Eingabe-Git-Blob `c6af1246395d525d8340ce4616aa9e8c9c09d390`, SHA-256 `4ddc141d9826063df5a0445f30b816c7bbbe99388b3512038198059cf5d89d3d`; Objekt-SHA-256 `116f59d8366adf5b32baefcd503ce76862097f782958ced2e14d9cc8cb261e81`, privat abgelegt unter `sdk-research/kbusdemo-fw30-gcc14.o`. Der Compile-only-Aufruf nutzte `/usr/bin/arm-linux-gnueabihf-gcc` 14.2.0 mit `-std=gnu11 -Wall -Wextra -O2 -fno-common -march=armv7-a -mtune=cortex-a8 -mfpu=neon -mfloat-abi=hard`, die privaten FW30-Header und `-c`; es gab zwei Vorzeichenvergleich-Warnungen im Original bei den Zeilen 119 und 129. `readelf` bestätigt ELF32 little-endian ARM EABI5, ARMv7-A und VFP-Argumentübergabe. Undefinierte Symbole sind `__time64`, `adi_GetApplicationInterface`, `memset`, `printf`, `putchar`, `puts`, `sched_setscheduler`, `strcmp` und `usleep`.

Das Quellverzeichnis enthält eine MIT-Lizenzdatei, während der C-Quellkopf zugleich proprietäre Rechte und einen Lizenzvertrag nennt; diese unterschiedlichen Hinweise werden hier nicht rechtlich ausgelegt. Der Quelltext wurde nicht ins öffentliche Repository kopiert. Es erfolgten weder Linken noch Ausführen. Das Ergebnis zeigt nur, dass dieses unveränderte FW30-Beispiel mit diesen Headern und GCC 14.2.0 zu einem ARM-Objekt übersetzt werden kann. Es ist weder ein Hersteller-Toolchain-Build noch ein FW31-ABI-Nachweis, Runtimebeleg oder Original-I/O-M3-PASS.

**VERIFIZIERT im FW30-DAL-Binärbestand:** Statische Disassemblierung von `libdal.so.1.0.1` (SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`) löst die bisherige Header-/Beispiel-Unklarheit für diesen Binärstand: Parameter 1 wird als Gerätezahl behandelt, nicht als Bytezahl. Die Implementierung iteriert den Gerätehash, schreibt `tDeviceInfo`-Einträge mit 8-Byte-Schrittweite und beendet das Kopieren anhand des Indexvergleichs mit `listCapacity`. `*deviceNumber` erhält davor die Gesamtzahl der gefundenen Geräte, auch wenn der Ausgabepuffer kleiner ist. Das stimmt mit dem Headerkommentar „number of devices fitting“ überein. Das Beispiel übergibt `sizeof(deviceList)` und behandelt damit die Bytezahl eines Arrays als Kapazität; bei mehr als einem Element ist dieser Wert größer als die Elementanzahl, wird von der FW30-Implementierung jedoch als Slotzahl gelesen.

**VERIFIZIERT – Nullkapazität im selben FW30-Binärstand:** Der Kontrollfluss prüft die Kapazität vor dem ersten Store; bei `listCapacity == 0` werden keine `tDeviceInfo`-Einträge geschrieben. `*deviceNumber` wird dennoch zuvor auf die Gesamtzahl der gefundenen Geräte gesetzt. Das ist die Interpretation der statischen Disassemblierung dieses Binaries; ob FW31 dasselbe Verhalten hat, bleibt **OFFEN**.

## Compile-only-ABI-Sonde und konkrete FW30-Layouts

Die bestehende eigene Sonde [abi_layout_probe.c](../tools/abi_layout_probe.c) wurde um alle 34 ADI-Funktionsfelder, zentrale Typgrößen/-offsets, Headerenumwerte und Signaturasserts für `GetDeviceList`, `ReadBytes` und `WriteBytes` erweitert. Sie inkludiert nur originale Header aus `dal_1.0.1_armhf.tgz`; kein Herstellerheader und kein Herstellerquelltext wurde ins Repository kopiert.

Kompiliert wurde mit `/usr/bin/arm-linux-gnueabihf-gcc` 14.2.0, Target `arm-linux-gnueabihf`, Flags `-std=c11 -Wall -Wextra -Werror -ffreestanding -fno-common -O0 -march=armv7-a -mtune=cortex-a8 -mfpu=neon -mfloat-abi=hard`, `-c` und Include-Pfad zum privat extrahierten Originalheader. SHA-256 der Sonde: `caba15625e61c6c1be4dc254341de4c36117abe114444a32479caab3fa8ee6e4`. SHA-256 des privaten Probeobjekts: `a10444d43d0535cbf7bbd54a2d17f73e3303e5c7c38b79fef5c2d7ffe055c8f4`. Der SDK-Snapshot nennt GCC 11.3.1; unser GCC 14.2.0 ist daher ein anderer Compilerstand. Das Objekt ist ELF32 little-endian ARM EABI5, ARMv7, `Tag_ABI_VFP_args: VFP registers`. Es wurde nur kompiliert und mit `readelf`/`objdump` gelesen, nicht gelinkt oder ausgeführt.

**PASS, enger Scope:** Die Sonde kompiliert mit diesen echten FW30-Headern und dem vorliegenden ARM32-Hard-Float-GCC. Die Sonde misst Layouts der Header unter GCC 14.2.0; sie zertifiziert weder GCC 11.3.1 noch den Herstellerbuild, FW31, noch eine Laufzeit-ABI.

| Typ/Größe oder Feld | GCC 14.2 Layout aus dem Probeobjekt |
|---|---:|
| `sizeof(void *)`, `sizeof(size_t)`, Funktionszeiger | 4, 4, 4 |
| `sizeof(bool)`, `sizeof(tDeviceId)` | 1, 4 |
| `sizeof(tApplicationDeviceInterface)` | 136 (`0x88`); 34 Zeigerfelder, je 4 Byte |
| `sizeof(tDeviceInfo)` | 8; `DeviceId` Offset 0, `DeviceName` Offset 4 |
| `sizeof(tApplicationStateChangedEvent)` | 4; `State` Offset 0 |
| `sizeof(tApplicationState)`, `tBusState`, `tDiagnoseState`, `tError` | jeweils 4 |
| `sizeof(tCommonEvent_IoSizeChanged)` | 16; `size_t` Felder bei 0, 4, 8, 12 |

ADI-Funktionsfelder liegen in der Headerreihenfolge lückenlos bei Offsets `0x00, 0x04, …, 0x84`; damit liegt z. B. `GetDeviceList` bei `0x0c`, `ReadBytes` bei `0x50` und `WatchdogTrigger` bei `0x84`. Die extrahierten Enumwerte: `DAL_FAILURE=-1`, `DAL_SUCCESS=0`, `DAL_NOTUSED=1`; Application-State `BASE=0`, `Running=1`, `Stopped=2`, `Unconfigured=3`; Bus-State `NotEnabled=0`, `BusOk=1`, `BusFault=2`, `BusNotCommunicating=3`, `BusStopped=4`; Diagnose-State `InvalidInputParameter=-1`, dann `NotEnabled=0`, `GetDiagInfo=1`, `DiagInfoAvailable=2`, `DiagInfoNotAvailable=3`; BusMember-Flags `Configured=1`, `Alive=2`, `Faulted=4`. Alle Angaben sind nur Layout/Enumwerte dieses Headers mit diesem Compiler.

### Längenprüfung und Eventcallbacks in `libdal.so.1.0.1`

**VERIFIZIERT per statischer ARM-Disassemblierung:** Die DAL-Wrapper für `ReadBytes` und `WriteBytes` prüfen `offset + size` auf Überlauf und verlangen, dass das Ende innerhalb der konfigurierten Eingangs- bzw. Ausgangsgröße liegt; erst dann rufen sie die gerätespezifische Bytes-Funktion auf. Der Bytebereich wird also auf der generischen DAL-Grenze geprüft. Der Gerätehandler bleibt für Semantik jenseits dieses Bereichs verantwortlich.

Der `GetDeviceName`-Pfad prüft einen nichtleeren Zielpuffer, kopiert höchstens `bufferSize` Bytes und setzt das letzte Pufferbyte auf NUL. Die Länge der tatsächlich kopierten Zeichenfolge wird über den `nameLength`-Ausgabeparameter geliefert; der Wrapper gibt Status `0` bei nichtleerer Länge und `-1` bei leerem Ergebnis zurück. Das ist eine Beobachtung für diesen FW30-Pfad, kein Vertrag zur ungekürzten ursprünglichen Namenslänge.

Der ADI-Header deklariert Eventhandler als `void (*)(tEventSource, tEventId, tEventArgs, void *userData)`. Der `RegisterEventHandler`-Wrapper leitet Handler und `userData` an den Eventpfad des geöffneten Geräts weiter; `UnregisterEventHandler` leitet Gerätebezug und Handler weiter. Header und sichtbarer DAL-Wrapper reichen nicht aus, um Lebensdauer nach erfolgreicher Abmeldung, parallele Callbackzustellung, Aufrufthread oder garantierte Beendigung bereits gestarteter Callbacks festzulegen: diese Punkte bleiben **OFFEN**.

## Register, Async, Diagnose, Zeit und Retain

**VERIFIZIERT als Herstellerdokumentation für diesen historischen Beispielstand:** `adi_functions.txt` beschreibt den Dispatch über `CallDeviceSpecificFunction` für `libpackbus_Push`, digitale Offsets, Tabellen-/Konfigurationsregister, UID und asynchrone Registerkommunikation. Für Async sind `OPEN/CLOSE`, `START/POLL` für Registerlesen und -schreiben sowie Varianten für Registerlisten und Parameter dokumentiert. Die Anleitung warnt, dass gestarteter Registerzugriff den Prozessdatenaustausch über mehrere Zyklen mehrfach unterbricht. Sie dokumentiert damit eine relevante Zeit-/Bussemantik, aber keine Garantie, dass ein konkretes Projekt oder FW31 diese Funktion aufruft. Im Beispiel selbst wird nur der explizite Push-/Watchdog-/Prozessdatenpfad gezeigt.

**VERIFIZIERT im FW30-SDK-Paketgraphen:**

| Pfad | Beleg | Aussagegrenze |
|---|---|---|
| K-Bus Async | `cds3-cmpkbusasynccom_0.0.1_armhf.ipk` hängt von `cds3-iodrvdal`, `cds3-iodrvkbus`, `cds3-tscexttask`, `codesys3` und `libpackbus` ab; gleichnamiges Headerarchiv enthält `WagoSysKbusAsyncCom_Internal_PFCItf.h`. | Komponenten-/Paketbeziehung, kein Runtime-Callgraph und kein allgemeiner stabiler API-Vertrag. |
| Asynchrone Zeitdienste | `cds3-tsctime_0.0.6_armhf.ipk` hängt von `cds3-tscasyncmgr`, `cds3-tscsharedpointer` und `codesys3` ab; Headerarchiv enthält `TscTimeItf.h` und `wagotime.h`. | Zusätzlicher CODESYS-/WAGO-Zeitpfad im Build; keine bewiesene ADI-Abhängigkeit oder FW31-Verwendung. |
| Retain | `cds3-tscretainuio_0.0.2_armhf.ipk` hängt von `codesys3` und `wretain` ab; im Headerarchiv liegt nur `TscRetainUIODep.h`. | Retain ist ein separater Runtime-/UIO-Pfad, kein durch ADI allein erklärter Zustand. |
| Diagnose | `libIoDrvKbus.so.0.0.1` benötigt `libdiagnostic.so`; die ADI-Tabelle enthält zusätzlich Diagnoseabfragen und Event-Registrierung. | Vorhandensein und Abhängigkeit sind belegt; konkrete Fehlerereignisse, Callback-Lebensdauer und Statusabbildung bleiben offen. |

Die SDK-Regeln referenzieren die Quellen von `TscAsyncMgr`, `TscTime`, `TscRetainUIO` und `CmpKbusAsyncCom` unter `wago_intern/codesys3-Component/...`; das DAL-Rezept referenziert `wago_intern/dal`. Der öffentliche Snapshot enthält somit genuine Komponenten-Header und vorkompilierte Pakete, aber nicht die kompletten zugrundeliegenden Herstellerquellen. Die angebotenen Headerarchive für K-Bus-Async, TscIoDrvKbus, Zeit und Retain tragen dieselbe Rechte-/Versionsgrenze und sind kein FW31-Abgleich.

## Was diese Evidence für B+C ändert

**HYPOTHESE:** ADI/DAL bleibt ein gut begründeter Untersuchungseinstieg: jetzt gibt es einen direkten FW30-Binärimport durch `libIoDrvDal` und einen echten, zugehörigen ARMHF-Headerbestand. Das stützt die technische Existenz der Grenze, bestätigt aber nicht ihre Austauschbarkeit im angepeilten FW31-Betrieb.

**OFFEN:** Vor einem gerätegebundenen Shim fehlen die Header/ELFs des tatsächlich inventarisierten Firmwarestands, der Runtime-Verbraucher und dessen vollständige Symbol-/Komponentenkette, Rechte zur Verwendung der proprietär gekennzeichneten Interfaces, Strukturgrößen/Offsets mit dem passenden Herstellercompiler, Async-/Register- und Diagnoseaufrufe des konkreten Gerätebaums, Geräte-/Konfigurationsdaten sowie Zeit-/Retain-Abhängigkeiten eines Minimalstarts. FW31 ist lediglich historischer Zielkontext; die zweite WAGO wurde noch nicht inventarisiert. Die FW30-`GetDeviceList`-Beispielstelle übergibt Bytegröße statt dokumentierter Slotzahl; die FW30-Binärimplementierung belegt Slotzahlsemantik und Nullkapazitätsverhalten, andere Builds bleiben offen.

**BLOCKED:** ABI-Probe und jegliche Verbraucherqualifikation für FW31 bleiben blockiert, bis der rechtmäßig nutzbare, exakt passende Firmware-/Engineeringbestand mit seinen echten ARM32-Headern und Binaries vorliegt. Keine Ersatzheader oder geschätzten Offsets erstellen.

## Nächster konkreter Offline-Einstieg

1. Im frisch inventarisierten tatsächlichen Firmware-/Engineeringbestand unverändert Hashes von `libdal`, `libIoDrvDal`, `libIoDrvKbus`, Runtime, Komponentenmanifesten und Konfiguration erfassen; die Dateiquellen an das Manifest binden.
2. Die passenden Originalheader aus demselben Build bzw. autorisierten SDK lokalisieren und das dortige `GetDeviceList`-Verhalten gegen den FW30-Binärbefund abgleichen. Proprietäre Header nicht ins öffentliche Repo kopieren.
3. Mit rein statischer Analyse am exakten Runtime- und Komponentenbestand Imports, `DT_NEEDED`, Symbolversionen, Suchpfade, direkte Hardwarezugriffe, `dlopen`/`dlsym` und zusätzliche Zeit-/Retain-/Diagnosekomponenten erfassen. Danach die kleinste benötigte Funktionsmenge für einen Original-DI/DO-Verbraucher bestimmen.
4. Erst nach Rechte- und Versionsklärung die vorhandene Compile-only-Sonde gegen echte passende ARM32-Header und den passenden Toolchainstand laufen lassen. Ein erfolgreiches Kompilieren belegt Layoutkonsistenz zum Header, noch keine Laufzeitkompatibilität.

## Test- und Evidence-Status

- Quellrevisionen, Git-Blob-IDs, Archive, Paketmetadaten und ELF-Eigenschaften: **VERIFIZIERT**, Scope FW30-Tag bzw. angegebene HowTos-Revision.
- Statische `readelf`-Analyse der beiden ARM-ELFs: **PASS** für das Lesen von ELF-Metadaten auf dem Host, kein Ausführen der Dateien.
- ARM32-ABI-Sonde gegen FW30-Header mit GCC 14.2.0: **PASS** compile-only; kein Link und kein Lauf. GCC-Version stimmt nicht mit der SDK-Angabe 11.3.1 überein.
- Unverändertes Hersteller-`kbusdemo.c` gegen FW30-Header mit GCC 14.2.0: **PASS** compile-only mit zwei Vorzeichenvergleich-Warnungen; kein Link und kein Lauf. Kein Original-I/O-M3-PASS.
- `GetDeviceList`-Kapazitätsverhalten, `ReadBytes`-/`WriteBytes`-Grenzprüfungen und `GetDeviceName`-Pufferpfad: **VERIFIZIERT** durch statische Disassemblierung von `libdal.so.1.0.1`, nur FW30.
- FW31-ELF-Abgleich, Original-Runtime, Calltrace, Init/DI/DO und Fehlerkontrolle: **NOT_RUN**; passende FW31-Artefakte/Rechte liegen in dieser Aufgabe nicht vor.
- Geräte-, Netzwerk- und Hardwaretests: **NOT_RUN**; diese Aufgabe war offline und rein lesend.
- Review: Self-Review durch den Rechercheworker und Integrator; zusätzlich tatsächlich ausgeführter unabhängiger statischer Artefaktreview durch einen separaten `gpt-6.1-sol`-Worker. Er prüfte Header-/Binärhashes, den Tabellen-/Kontrollfluss, die Grenzen und die Objektlayouts mit `readelf`/ARM-`objdump`. Er korrigierte die ursprüngliche Nullkapazitätsinterpretation und präzisierte `GetDeviceName`. Keine unabhängige Buildwiederholung, Firmwareausführung oder physische Freigabe behauptet.

## Quellenanker

- FW30-Headerpakete: [`dal_1.0.1_armhf.tgz`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/configs/wago-pfcXXX/packages/dal_1.0.1_armhf.tgz), [`cds3-iodrvdal_1.0.2_armhf.tgz`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/configs/wago-pfcXXX/packages/cds3-iodrvdal_1.0.2_armhf.tgz).
- FW30-ELF-Pakete: [`cds3-iodrvdal_1.0.2_armhf.ipk`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/configs/wago-pfcXXX/packages/cds3-iodrvdal_1.0.2_armhf.ipk), [`cds3-iodrvkbus_0.0.1_armhf.ipk`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/configs/wago-pfcXXX/packages/cds3-iodrvkbus_0.0.1_armhf.ipk).
- FW30-DAL-Implementierung: [`dal_1.0.1_armhf.ipk`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/configs/wago-pfcXXX/packages/dal_1.0.1_armhf.ipk).
- SDK-Bauregeln: [`wago-codesys3-002-wagocmp-dal.make`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/rules/wago-codesys3-002-wagocmp-dal.make), [`wago-codesys3-003-iodrvkbus.make`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/rules/wago-codesys3-003-iodrvkbus.make), [`wago-codesys3-008-wagocmpkbusasynccom.make`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/rules/wago-codesys3-008-wagocmpkbusasynccom.make), [`wago-codesys3-018-wagocmp-tsctime.make`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/rules/wago-codesys3-018-wagocmp-tsctime.make), [`wago-codesys3-018-wagocmp-tscretainuio.make`](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/rules/wago-codesys3-018-wagocmp-tscretainuio.make).
- WAGO-Beispiel und Funktionsdokument: [`kbusdemo.c`](https://github.com/WAGO/pfc-howtos/blob/a116875ddfa9154f6a9be38e1a02ac5759e1af29/HowTo_ADI-MyKBusApplikation/ptxproj/src_kbusdemo/kbusdemo.c), [`adi_functions.txt`](https://github.com/WAGO/pfc-howtos/blob/a116875ddfa9154f6a9be38e1a02ac5759e1af29/HowTo_ADI-MyKBusApplikation/ptxproj/src_kbusdemo/adi_functions.txt).
