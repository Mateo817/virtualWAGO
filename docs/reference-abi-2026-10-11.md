# Referenzbestand und tatsächliche ADI-Grenze

Stand: 11.10.2026, Fortsetzung nach wiederhergestellter SSH-Erreichbarkeit. Basis der Entwicklung ist `910dd9d849dfa4e1ef7d7a1725e4720b7214b520` auf `research/originalstack-m1-m2`; Veröffentlichung erfolgt über PR #2. Geräteadressen, Zugangsdaten, Identitätsbindung, Herstellerdateien und Rohbefunde bleiben privat. Maschinenlesbare, bereinigte Artefaktbindung: [reference-validation-2026-10-11.json](../evidence/reference-validation-2026-10-11.json).

## M1: Erhobener Bestand

**VERIFIZIERT, Softwaremetadaten:** Der Device Tree meldet `WAGO PFC200 750-8213`, `board_variant` meldet `pfc200v3`. `/etc/REVISIONS` enthält `FIRMWARE=04.09.01(31)`; SHA-256 `2efb783642bb019dc090d965d9ead2377c3a2a43b4caac02090a072f1b617433`. Die gesicherte Buildmetadatendatei `/etc/SVNREVISION` hat SHA-256 `83ec47e06c01bf98325921981a8a1174050bad2f69ddc774ef2e56172d7b5ace` und nennt den Buildtag 29.04.2026. Dies ist kein vollständiger Quellcommit-Pin und keine nachträgliche Übernahme des historischen Zielinventars.

**VERIFIZIERT, laufendes Gerät:** `uname` meldet ARMv7 und Kernel `6.6.94-rt56-w05.08.02`. Das lesbare Bootversionsattribut meldet `2021.10.0-w04.03.04_15`; kein Bootloader wurde verändert. Firmwaremarker, Kernelkennung und Dateizeitstempel bleiben getrennte Beobachtungen. Unterschiedliche Versionsbezeichnungen wurden nicht durch ein Update angeglichen.

**VERIFIZIERT:** Die bereits laufende Runtime ist `/usr/bin/codesys3`; `pp_codesys3` läuft als separater Parameterdienst. Runtime-Maps enthalten `libIoDrvDal`, `libIoDrvKbus`, `libdal`, `libpackbus`, K-Bus-Async-, Zeit- und Retainkomponenten. Sie enthalten auch ein `/dev/uio0`-Mapping: das ist eine reale Hardwareabhängigkeit des Referenzprozesses, kein im Emulator bereitgestellter Endpunkt. Kein Prozessspeicher oder Device-Node wurde ausgelesen.

**VERIFIZIERT, unterschiedliche Versionsquellen:** Die Paketdatenbank bezeichnet `codesys3` als Paketversion `6.4.6.4`; im gesicherten Runtime-ELF stehen `3.5.21.50` und ein Übersetzungsdatum vom 01.12.2024. Der ELF-String ist ein Binärbefund, keine über ein Runtimeprotokoll abgefragte Version. Ein lokal installiertes Engineeringprofil, passende Gerätebeschreibungen, Bibliotheksstände des IEC-Projekts und eine für Emulation nutzbare Lizenz sind weiterhin **OFFEN**.

**PASS, Sicherung:** 143 ausgewählte Originaldateien wurden per strikt gebundenem SSH in ein privates Archiv übertragen. Jeder Tar-Eintrag ist eine reguläre Datei und entspricht einzeln dem Gerätehash vor und nach der Übertragung. Beide 143-zeiligen Hashlisten sind bytegleich, SHA-256 `4f6486feb8d76076225ede6cf25d9776332261780bf6d317c953ae278678fa0e`. Archiv-SHA-256 `12580f43158b577b3f6e01ace8b4aec711da86342182aad92d4ec11f2f23726d`. Zusätzliche ausgewählte Web-/Authentifizierungsquellen, Init- und Runtimekonfigurationen wurden ebenso geprüft: insgesamt 167 eindeutige reguläre Dateipfade, privates Gesamtmanifest-SHA-256 `bc2ece1013fed19aa6802652453dc6407439243df675ce1f7f9c81c17b467e1a`. Das ist eine selektive Forschungsbestandssicherung, kein vollständiges wiederherstellbares Geräteimage. Private Schlüssel, Lizenzcontainer und Herstellerdateien werden nicht veröffentlicht oder in einen Emulator übernommen.

**VERIFIZIERT, Zugriffsscope:** SSH verwendete die exakte lokale Allowlist, einen lokal gebundenen Hostkey und deaktivierte Proxys, Agenten sowie Weiterleitungen. Die technische Egress-Sperre galt jeweils für die neue Forschungsnamespace, nicht für fremde/global betriebene Prozesse. Der HTTPS-Zertifikatsinhalt wurde zuerst über gebundenes SSH gewonnen; vor Zugangsdatenübertragung wurde das Zertifikat der HTTPS-Verbindung bytegleich geprüft. Redirects wurden einzeln auf denselben erlaubten Ursprung geprüft, keine fremden Ziele verfolgt.

**PASS:** Der bereitgestellte `admin`-Zugang funktioniert über HTTPS-WBM mit OAuth2 Authorization Code und PKCE. Der originale User-Info-Endpunkt meldet Rollen `guest`, `user`, `admin` und kein abgelaufenes Passwort. Linux-Gruppen und originale Rollenlogik stützen die WBM-Administratorzuordnung; weder Rootrechte dieses Kontos noch konkrete Schreiboperationen wurden damit getestet. Passwörter blieben unverändert. Ein Logout lieferte HTTP 200, das vollständige Löschen der eigenen Sitzung wurde jedoch nicht bestätigt; der geprüfte Sitzungsvertrag nennt 900 Sekunden. Es wurden keine fremden Sitzungsdateien bearbeitet. Zugangsdaten, Cookies und Tokens wurden nicht in Ausgaben, Git, PR oder CI gespeichert.

**OFFEN:** Serienidentität, Hardwarestand und tatsächlicher Klemmenbestand. Device Tree und erlaubte IP-/SSH-Zuordnung ersetzen kein vollständiges Typenschildinventar. `get_typelabel_value` wurde **NOT_RUN**: statisch sind ein `O_RDWR`-EEPROM-Open und Sync-/Getterpfade sichtbar. Die Bibliothek besitzt Schreibpfade, aber die untersuchten Standardflags wählen den Sync-Lesepfad; eine EEPROM-Schreiboperation durch die konkrete einzelne Abfrage ist nicht bewiesen. Der noch nicht geschlossene Nebenwirkungsvertrag rechtfertigt keinen unqualifizierten Aufruf.

**OFFEN, aktive Konfiguration:** Der Runtime-CWD zeigt auf ein gelöschtes, leeres Verzeichnis; der aktuelle `/home/codesys_root` hat einen anderen Inode. Deshalb beweisen dessen heutige Dateien weder das beim Start geladene Projekt noch dessen Abwesenheit im laufenden Prozess. Init-Script, aktuelle Konfigurationen und Prozess-Maps sind gesichert, es erfolgte kein Restart zur Vereinheitlichung. Zehn ausgewählte Runtime-/Modbus-/Initkonfigurationen enthalten keinen Literalverweis auf das geschützte Ziel; dies ist ein statischer Literalcheck, kein Nachweis sämtlicher dynamischer Zielauflösungen oder Autostarts. Keine aktive Konfiguration aus Produktquellen wurde übernommen oder gestartet.

Die elektrische Abtrennung bleibt **VERIFIZIERT als Eigentümeraussage**, ohne eigene elektrische Inspektion. Keine Installation, Ausgangsfreigabe, DAL-Initialisierung, Busmasterübernahme oder Aktorprüfung fand statt. Vor einer Installation fehlen insbesondere vollständige Identität, aktiver Projektzustand, benötigte ursprüngliche Projektbestände und ein konkreter, getesteter Rollback. Die vorhandene Erlaubnis wird dadurch nicht erneut pauschal zur Frage gestellt.

## M2: Versionsgebundene Grenze

**VERIFIZIERT:** Der vorgefundene `libdal.so.1.0.1` ist bytegleich zum untersuchten FW30-SDK-Artefakt, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. SDK-Pin: `252209115885442bac7359a2ff1cfa4efb3a9c84`. Damit gelten die bereits statisch geprüften DAL-Implementierungsbefunde auch für diese gesicherten Providerbytes: `GetDeviceList` zählt Einträge, Nullkapazität schreibt keine Einträge, und die belegten generischen Bytebereichsprüfungen sowie der `GetDeviceName`-Vertrag bleiben gebunden. Das qualifiziert weder alle FW31-Komponenten noch ununtersuchte Callback-/Fehlerpfade.

| Tatsächliches Original | SHA-256 | Scope |
|---|---|---|
| `codesys3` | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | Gesichertes Runtime-ELF; keine virtuelle Ausführung |
| `libIoDrvDal.so.1.0.2` | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` | Originaler ADI-Verbraucher, anderer Build als FW30 |
| `libIoDrvKbus.so.0.0.1` | `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` | Originaler K-Bus-Verbraucher, anderer Build als FW30 |
| `IoDrvDal.cfg` | `91fc4013c5bd87fab459f13bba60787e9f1256d4423cfd47eefdef307161af13` | Aktueller Dateibestand; aktiver Speicherzustand offen |

**VERIFIZIERT:** Der tatsächliche `libIoDrvDal` importiert `adi_GetApplicationInterface` und benötigt `libdal.so`. In `ComponentEntry` liegt der ADI-Aufruf bei ELF-Adresse `0x45a4`; bei `0x45bc` kopiert der Verbraucher `0x88` Bytes. Der exakte Provider und die passende FW30-Header-/ARM32-Sonde verankern die 136-Byte-/34-Zeiger-Tabelle. Numerische Tabellennutzung im abweichenden Verbraucher ist separat statisch belegt. Die Runtime-Maps bestätigen, dass diese Dateien in den Referenzprozess eingebunden sind; sie beweisen keine Akzeptanz eines Ersatzes.

**VERIFIZIERT:** `IoDrvKbus` benötigt `libIoDrvDal.so.1`, Diagnose- und WAGO-D-Bus-Komponenten, importiert ADI aber nicht direkt. Der K-Bus-Async-Verbraucher benötigt zusätzlich `libpackbus.so.1`. Zeit und Retain führen eigene Library-/UIO-Abhängigkeiten. Es existiert somit ein tatsächlicher Verbraucherpfad `IoDrvKbus → IoDrvDal → DAL` mit parallelen Abhängigkeiten; eine reine Austauschbarkeit eines einzigen Exports wird nicht behauptet.

**VERIFIZIERT, aktuelle Datei:** Die K-Bus-Zeile in `IoDrvDal.cfg` nennt `DalName=libpackbus`, `ConfigLibrary=libIoDrvKbus`, `EntryFunction=IoDrvKbus_Init`, `DeviceName=Kbus`, `ModuleType=0x800a` und `Version=0x01000000`. Diese Modulkennung bezeichnet hier den konfigurierten Treibertyp; sie ist keine nachgewiesene Kennung einer 750-1405 oder 750-1504. Watchdog-/Instanzparameter sind gesichert; ihre aktive Verwendung ist **OFFEN**.

**VERIFIZIERT, Paketunterschied:** Die FW30-`.ipk`- und `.tgz`-Archive enthalten trotz gleicher IoDrvDal-Versionsbezeichnung unterschiedliche Binaries: `.ipk`-Library-SHA `1c1d3a4857823b01f5592118c90a9a7032192fa7f018e4b149e4c5b39d0a4d09`, `.tgz`-Library-SHA `689c50d8e7e15b30c44ddb8420cb48c5d3213b85a294f53e9cfb35e35f40a885`. Der aktuelle Verbraucher unterscheidet sich von beiden. Der ältere [FW30-Bericht](abi-research-2026-10-11.md) verwendet korrekt das `.ipk`-Artefakt; der Entwicklungsheaderbestand bleibt ein eigener Comparator.

## M3-Kandidat und präziser nächster Einstieg

**HYPOTHESE:** Der kleinste derzeit begründete Originalverbraucher-Kandidat ist der gesicherte `IoDrvDal`-/`IoDrvKbus`-Pfad mit Ersatz der nachgewiesenen ADI/DAL-Grenze und einem virtuellen 750-1405-/750-1504-Strang. B+C bleibt die Forschungsentscheidung. Eine kleinere vollständige DDI-Grenze oder ein Bedarf an Boardemulation ist nicht belegt.

**VERIFIZIERT, statische Operationen:** Im abweichenden IoDrvDal sind Init-/Scan-/List-/Open-, Zustands- und Watchdog-Tabellenzugriffe vorhanden. Eine rekonstruierte unbenannte Routine ab `0x33f4` enthält `ReadStart/ReadBytes/ReadEnd`; eine ab `0x2134` enthält `WriteStart/WriteBit/WriteBytes/WriteEnd`. **HYPOTHESE:** Argument-/Schleifenstruktur und echte Entwicklungsheader passen zu `IIoDrvReadInputs`/`IIoDrvWriteOutputs`. Die konkrete CODESYS-Registrierung, Vtable-/Callerbindung und zyklische DI/DO-Wirkung bleiben **OFFEN**. Eine Tabellenoperation allein ist kein DI/DO-PASS.

**VERIFIZIERT, unabhängiger statischer Folgecheck:** Die Aufbauroutine ab `0x2ddc` berechnet beide Funktionsadressen mittels PC-relativer Literale und kopiert sie in eine Instanztabelle: `0x33f4` an Instanzoffset `0x34`, `0x2134` an `0x4c`. Der Instanzindex ist auf 0 bis 9 begrenzt, der Abstand beträgt 1596 Bytes. Das belegt tatsächliche indirekte Einträge im untersuchten Binary; fehlende direkte `BL`-Aufrufe oder Relokationseinträge waren kein Beweis fehlender Referenzen. Welche CODESYS-Interfacemethode diese Instanzfelder verwendet und ob sie im laufenden Projekt aufgerufen werden, bleibt **OFFEN**. Diese Offsets beschreiben diesen Originalverbraucher, keine Strukturdefinition für einen nachgeschriebenen Harness.

Der unabhängige Review korrigierte eine zunächst falsche Zuordnung anhand benachbarter `objdump`-Symbolnamen: `Dal_DiagnoseGetDeviceState` endet nach deklarierter Größe bei `0x2dac`, `FuIoDrvUpdateMapping_dynamic_s` bei `0x1ad0`. Die betrachteten späteren Aufrufe liegen außerhalb dieser Bereiche. Der ELF-Audit liefert jetzt tatsächliche Symbolwerte, deklarierte Größen und Ursprungstabellen; ein Regressionstest verhindert eine Ableitung von Funktionsgrenzen aus dem nächsten Symbol. Größe null liefert keine Bereichsaussage.

**BLOCKED, ausführbarer Originalverbraucher:** Die echten Entwicklungsheader zeigen, dass `IoDrvKbus_Init` ein vollständig aufgebautes `IoDrvDalInfo` mit ADI, CODESYS-Initdiensten und Hookzustand benötigt. Ein direkter Aufruf mit erfundener Minimalstruktur wäre kein Originalstack-Test. Es fehlen die passenden Komponentenverträge `CmpItf.h`/`INIT_STRUCT`, `CmpIoDrvItf.h`/`ICmpIoDrv` und `IoConfigConnectorMap`, die konkrete Registrierung und Init-/Exit-/Rollbackfolge sowie echte Geräte-/Parameterverträge für die beiden Digitalklemmen. Die vollständig geschlossene dynamische Loader-/Servicekette und eine praktisch geprüfte Dateisystem-/Geräte-/IPC-Isolation fehlen ebenfalls. Die vorhandene Referenz-Netzsperre allein genügt nicht für Herstellerbinary-Ausführung.

Der nächste technische Einstieg ist deshalb die CODESYS-Komponentenregistrierung dieses exakten IoDrvDal-Builds samt echten Manager-/Mappingheadern. Danach folgt ein begrenzter originaler Init-/Enumerationslauf ohne physische Endpunkte; zyklische DI/DO und Negativkontrolle sind dessen eigene nachfolgende Abnahme. Die bytegleiche DAL-Datei nimmt die pauschale Suche nach einem weiteren FW31-DAL-Header aus dem kritischen Pfad; die abweichenden Verbraucher bleiben separat zu qualifizieren. Kein Herstellerbinary wurde im Forschungsprozess gestartet. Die laufende Hardware-Runtime ist Inventarquelle und kein virtueller Runtime-PASS.

## Checks, Review und Gerätezustand

| Check | Status | Scope |
|---|---|---|
| Guarded SSH und strikte Hostkeybindung | PASS | Exakte lokale Allowlist, kein Proxy/Forwarding |
| Selektive Originalbestandssicherung | PASS | 167 reguläre Dateipfade, Einzelhashes vor/nach Transfer |
| HTTPS-Zertifikatsbindung und admin-Rollenabfrage | PASS | WBM-Anmeldung, keine Konfigurationsschreibprüfung |
| Eigene Websitzung vollständig gelöscht | FAIL | HTTP 200 reichte nicht; normaler Timeoutvertrag, keine fremden Sitzungsänderungen |
| Modell-/FW-/Kernel-/Maps-Erfassung | PASS | Beobachtete Softwaremetadaten, kein Serien-/Klemmenvollinventar |
| Vollständiger M1-/Installationsrollback-Nachweis | BLOCKED | Hardwarestand, Serienidentität, Klemmen, aktiver Projektzustand fehlen |
| Tatsächlicher ADI-Import/Tablecopy/Providervergleich | PASS | Statisch, genaue ELF-Hashes; kein vollständiger M2-Verhaltensnachweis |
| Konkrete I/O-Manager-Callerbindung und Callbackvertrag | BLOCKED | Komponentenheader/Lifecycle/Registrierung unvollständig |
| Originalverbraucher Init/DI/DO/Negativkontrolle | BLOCKED | Kein ausgeführter M3-Test |
| Virtuelle Originalruntime mit unverändertem IEC-Programm | NOT_RUN | Getrennte Abnahme, Mapping und Lizenzzuordnung fehlen |
| K-Bus-Masterwechsel, Aktor-, PWM-/Register-/Mehrinstanztest | NOT_RUN | Kein solcher Eingriff durchgeführt |

Integrator- und Workerprüfung sind **Self-Review**. Ein separater `gpt-6.1-sol`-Worker prüfte tatsächlich Sicherung, Original-ELFs, Symbolgrenzen und Typenschildpfade unabhängig. Luna-Worker bearbeiteten offline die ABI-/Identitätsanalyse und die Werkzeugänderung; ausschließlich der Integrator führte Referenzzugriffe aus. Private Rohdaten bleiben außerhalb von Git. Keine unabhängige elektrische, Lizenz- oder Hardwarefreigabe wird behauptet.

Das Referenzgerät behält seine ursprüngliche Runtime und Einstellungen. Abschließend wurden Runtimeprozess und ausgewählte Originalhashes erneut gelesen. Keine Produktrepositoryänderung, kein geschützter Gerätezugriff, keine Installation, Passwortänderung, Firmware-/Kerneländerung oder Busmasterumschaltung fand statt. Die neu erhobenen Befunde ergänzen die Forschung; die Mesokosmen-Produktsteuerung und ihre interne Anlagensimulation wurden nicht umgebaut.
