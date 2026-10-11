# CODESYS-Engineering- und Device-Description-Verträge

Stand: 11.10.2026. Öffentliche Zusammenfassung einer read-only Inventaraufnahme und statischen Offlineanalyse. Dieser Bericht enthält keine Hersteller-XML, Header, privaten Pfade, GUIDs, Benutzer- oder Lizenzidentitäten. Bereinigte Hash- und Statusdaten: [codesys-contract-validation-2026-10-11.json](../evidence/codesys-contract-validation-2026-10-11.json).

## Versionsbefunde

**VERIFIZIERT:** Im installierten Engineeringbestand sind mehrere getrennte Versionsangaben vorhanden. Das tatsächlich gefundene ältere CODESYS-Profil und die ausführbare IDE gehören zur Version 3.5.21.50 und zum Service Pack 21, Patch 5. Ein Registryfeld enthält separat `3.5.21.500`; dieses Feld ist nicht die Versionsangabe der tatsächlich gefundenen IDE-Datei. Eine neuere IDE 3.5.22.10 ist ebenfalls vorhanden, wurde in diesem Forschungslauf nicht verwendet. Diese Bestandsbefunde beweisen weder ein aktives IEC-Projekt noch eine Geräteverbindung oder eine Runtimeausführung.

Die PFC200-Beschreibung für Firmwarestand 31 ist Version 6.4.6.11 und führt den Runtime-Zielstring 3.5.21.50. Die Firmwarestand-30-Beschreibung ist Version 6.4.5.11 und führt 3.5.21.30. Die lokalen Beschreibungen für 750-1405 und 750-1504 sind jeweils Version 2.0.0.14; die generische lokale Busbeschreibung ist Version 2.1.0.1. Der Runtime-Zielstring in einer Engineeringbeschreibung ist Metadatum; er beweist nicht für sich allein die aktuell laufende Runtimeversion.

## Geräte- und Kanalverträge

**VERIFIZIERT, statische Beschreibungen:** Die PFC200-Beschreibung hat numerischen Gerätetyp 4096 und beschreibt Artikel 750-8213. Sie bindet einen lokalen Bus mit numerischen Typen 32777/32778 an eine generische Busbeschreibung Version 2.1.0.1. Die K-Bus-Schnittstelle verwendet in ihrer Beschreibung zusätzlich den Connector-Typ 32779. Diese Werte gehören zu unterschiedlichen Geräte- und Connectorfeldern; gleiche Zahlen begründen keine gemeinsame globale Typen-ABI.

Die Beschreibungen für 750-1405 und 750-1504 verwenden Gerätetyp 32776. Der beschriebene K-Bus-Terminalconnector hat ID 0 und Connector-Typ 32776. Der 750-1405-Eingang deklariert Parameter-ID `0x01000000` als 16-Bit-`WORD` mit 16 `BOOL`-Teilfeldern auf dem `input`-Kanal und Lesezugriff. Der 750-1504-Ausgang deklariert Parameter-ID `0x03000000` als 16-Bit-`WORD` mit 16 `BOOL`-Teilfeldern auf dem `output`-Kanal und Lese-/Schreibzugriff. Das sind Engineeringdeklarationen. Sie belegen keine physische Prozessabbildadresse, Byte-Reihenfolge, Slotreihenfolge, Scanzeit, Klemmenpräsenz oder Aktorwirkung.

Die lokale Offlineprüfung extrahierte und prüfte sieben bereinigte Device-Description-Befunde (**7/7 PASS**). Eine Validierung gegen ein Hersteller-XSD wurde **NOT_RUN**. Die Parserfälle prüfen die statisch deklarierten Struktur-/Kanalwerte; sie simulieren weder Runtime-Verhalten noch physische Zuordnung.

## CODESYS-Header und erreichbare Grenze

**VERIFIZIERT, eng begrenzt:** Ein `CmpItf.h` aus C Integration 3.5.17.0 ist im installierten Bestand vorhanden. Die FW31-Komponenteneinstiegsroutine greift statisch auf ein Präfix zu, das strukturell mit einer 15-Wort-`INIT_STRUCT`-Anordnung unter 32-Bit-Annahmen übereinstimmt. Das ist eine plausible Cross-Version-Strukturkorrelation, keine vollständige Header- oder ABI-Qualifikation und kein Nachweis, dass genau dieser Header zum FW31-Binary gehört.

**BLOCKED:** Die passende `CmpIoDrvItf.h`, `IoConfigConnectorMap`-/Connector-Definitionen und die vollständigen Plattformheader fehlen. Damit bleiben exakte Ziel-Header-ABI, Manager-/Treiberregistrierung, Callback-Lifecycle und Mappingvertrag offen. Der ältere CODESYS-Headerfund schließt diese Lücken nicht. Keine originale WAGO-I/O-Bibliothek wurde im Forschungsprozess geladen oder ausgeführt.

Die Verfügbarkeit der benötigten Device-Descriptions ist damit kein M3-Blocker mehr. Die tatsächliche Projektkonfiguration, installierte Auswahl im aktiven Projekt, vollständige Hardwareidentität und der Klemmenbestand bleiben **OFFEN**. B+C bleibt eine **HYPOTHESE**, nun mit stärkerer statischer Originalvertragsevidence. Original-`IoDrv`-/Runtimeausführung im Forschungsprozess und IEC-Projektdownload fanden nicht statt; der virtuelle Runtime-Status bleibt **NOT_RUN**. Die VM wurde nach der Inventaraufnahme wieder auf Datenträger pausiert.

## Prüfstatus

Die lokale hardwarefreie Suite ergab 92 Tests **PASS** in 1,419 Sekunden: 82 bestehende Tests plus 10 Device-Description-Parserfälle. Der statische Device-Description-Audit ergab 7/7 PASS. XSD-Validierung, Original-I/O-Komponenten, Runtime, IEC-Projektdownload und Hardwaretests sind **NOT_RUN**. Die VM ist gestoppt und auf Datenträger gesichert.

Integratorprüfung: **Self-Review**. Ein separater `gpt-6.1-sol`-Worker prüfte die Dateien und Quellen tatsächlich unabhängig, führte die zehn synthetischen Parserfälle erneut aus und auditierte die sieben Originalbeschreibungen offline. Zwei Parserhinweise und eine zu weit gefasste Aussage zur neueren IDE wurden korrigiert und nachgeprüft. Der Review bestätigt keine Lizenz-, Hardware- oder Herstellerfreigabe.

## Minimaler IEC-Forschungskandidat

Ein eigenes, neues Forschungsprogramm liegt in [`prototype/iec/minimal_io.st`](../prototype/iec/minimal_io.st); seine SHA-256 lautet `e757410d9d9efc4f363e666190514af130d2a6be9fd46916a805cd7551588dcc`. `PLC_PRG` deklariert `InputWord`, `OutputWord`, `OutputPermit` und `CycleCounter` mit den festgelegten Null-/False-Startwerten. Es setzt `OutputWord` in jedem Scan zuerst auf null und spiegelt den Eingang nur bei `OutputPermit=TRUE`. Der Zähler saturiert bei `UDINT`-Maximum, ohne Wrap-Verhalten vorauszusetzen.

Die synthetische [Descriptor-Pin-Konfiguration](../config/minimal-iec-candidate.json) bindet den Kandidaten an IDE-Profil 3.5.21.50 SP21 Patch 5 und pinnt die vier ausgewählten Standard-DeviceIDs samt Descriptor-SHA-256. Ihre SHA-256 lautet `456ef8cd6ce01e9ce0681db580282fbf5e1bd4466fb2469fadc9866f25c91817`. Sie ist ausdrücklich weder Backendkonfiguration noch natives CODESYS-Projekt. Es gibt keine Geräteziele, Adressen, Ports, physischen Prozessabbildzuordnungen, Bibliotheken, Retain- oder Autostartdefinitionen.

**NOT_RUN:** Das ST-Programm wurde nicht mit CODESYS kompiliert, in ein natives Projekt überführt, ausgeführt oder heruntergeladen. Nächster Schritt ist nach praktisch nachgewiesener Abschirmung des Forschungsprozesses ein neues, leeres CODESYS-Projekt mit den gepinnten Beschreibungen anzulegen, das Programm unverändert aufzunehmen und offline zu kompilieren. Danach kann der native Connector-/Kanalmappingdialog geprüft und ein Projektartefakt privat gesichert werden. Solange die exakte Prozessabbildzuordnung nicht verifiziert ist, bleiben Ein-/Ausgänge interne Kandidatensignale; kein physisches oder symbolisches Mapping wird erfunden. Eine Zielverbindung oder ein Download gehört nicht zu diesem Schritt.

## Eigener Windows-Schutztest: FAIL, CODESYS weiter BLOCKED

Der Integrator kompilierte und startete ausschließlich eine eigene, fest begrenzte C#-Sonde mit dem inventarisierten .NET-Framework-Compiler 4.8.9221.0 auf Windows (OSVersion-API: 10.0.26100.0). Die normalen Benutzerzugriffe auf eine eigene Datei, einen eigenen TCP-Loopbacklistener und eine eigene Named Pipe waren **PASS**. Die anschließende positive AppContainer-Kontrolle startete, endete jedoch mit `0x8007045A`; sie bestätigte weder Token noch den erlaubten Dateizugriff. Ihr Low Word ist 1114, in der [Microsoft-Fehlertabelle](https://learn.microsoft.com/en-us/windows/win32/debug/system-error-codes--1000-1299-) `ERROR_DLL_INIT_FAILED`. Die konkrete Bibliothek und Ursache bleiben **OFFEN**. Das belegt keine allgemeine CODESYS-/LPAC-Inkompatibilität.

Damit ist die gesamte Schutzqualifikation **FAIL** und die nachfolgende LPAC-Prüfung **NOT_RUN**. CODESYS-Start und IEC-Kompilierung im Forschungsprozess bleiben **BLOCKED**; IDE, Original-WAGO-Verbraucher und Projektdownload wurden nicht gestartet. Die normalen Verbindungen der VM bleiben erhalten. Globale Firewall-, Gateway-, SDK- und Dienstberechtigungen wurden nicht verändert.

Ein früherer eigener Probelauf scheiterte zusätzlich an der Rücknahme temporärer Rechte auf genau zwei eigene Programmobjekte. Diese eigenen Rechte wurden entfernt und überprüft; spätere Läufe bestätigten beide ursprünglichen DACLs sowie null verbliebene eigene Probeprozesse. Der zwischenzeitlich gemeldete Startfehler 203 trat nach den Environment-/Fehlererfassungskorrekturen nicht mehr auf; daraus folgt keine isolierte Ursachenzuordnung. Privates Arbeitsverzeichnis und Einmalprofil wurden laut Launcher bereinigt. Rohdaten, SIDs, Originaldateien und Hilfsskripte bleiben lokal. Der [bereinigte Prüfdatensatz](../evidence/windows-own-probe-2026-10-11.json) bindet den letzten tatsächlichen Lauf an Quellen-, Compiler-, Binary- und Berichtshashes.

**Nächster technischer Einstieg:** Die Startabhängigkeit der fehlgeschlagenen Kontrollsonde unter der bestehenden Prozessgrenze gezielt bestimmen, ohne Zugriffsrechte auf gemeinsame Dienste auszuweiten. Erst nach positiver Kontroll- und Sperrprüfung ein neues, verbindungsloses CODESYS-Projekt aus dem eigenen ST-Kandidaten erstellen und offline kompilieren. Ein solches Projekt ersetzt weder den fehlenden nativen I/O-Managervertrag noch den Originalverbraucher-PoC. Die Architekturentscheidung B+C bleibt unverändert eine **HYPOTHESE**.
