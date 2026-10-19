# Native Analog-/PWM-Integration, 19. Oktober 2026

**Späterer begrenzter Versuch:** [Zwei synthetische PWM-UID-Antworten](pwm-synthetic-uid-2026-10-19.md) erreichen jeweils RUN und den noch nicht unterstützten Async-Open-Dispatch. Keine echte UID und keine vollständige PWM-Abnahme daraus abgeleitet.

Dieser Block setzt die neue Priorität des Eigentümers um: ausgewählte virtuelle
Module zuerst erfolgreich in CODESYS einbinden; reale Modulvergleiche folgen
später. [ADR-0009](adr-0009.md) trennt diese Softwarekompatibilität von
Hardwaretreue. Der ältere [Modulerweiterungsbericht](module-extension-2026-10-19.md)
bleibt die revisionsgebundene Ausgangsevidence.

## Aktuelle Abnahme

| Profil | CODESYS Build/Reopen | Eigener ARM-Provider | Originalruntime-Zyklus | Hardwarevergleich |
|---|---|---|---|---|
| 750-430 / 750-530 (8 DI/DO) | PASS, gebundenes vorhandenes Artefakt | PASS | PASS, 4 Muster | NOT_RUN |
| 750-1405 / 750-1504 (16 DI/DO) | PASS, gebundenes vorhandenes Artefakt | PASS | PASS, 8 Muster | NOT_RUN |
| 750-466 / 750-550 (Analogpaar) | PASS, unverändertes vorhandenes Artefakt | PASS | PASS, 6 Muster | NOT_RUN |
| 750-677#16 (PWM) | PASS, frisch | PASS | RUN PASS; Frameabnahme BLOCKED (UID-/Modellfehler) | NOT_RUN |

**VERIFIZIERT:** Das Analogpaar durchläuft mit dem endgültigen Provider die
originalen Terminal-/Table9-/R16-/R29-/R30-Prüfungen sowie zyklische Lese- und
Schreibzugriffe. Beide Digitalpaare wurden mit diesem Implementierungsstand
frisch regressionsgeprüft. Alle vollständigen angeforderten Ausgangsframes
entsprachen den separat gebundenen IEC-Prüfprogrammen. Diese Softwareprüfungen
sind kein allgemeines „fehlerfrei“ und kein physikalischer Modulnachweis.

## Implementierte virtuelle Profile

| Profil | Native Gerätebeschreibung | Virtuelles ADI-Prozessabbild | Unterstützte Konfiguration |
|---|---|---|---|
| `AI466_AO550` | 750-466 und 750-550, jeweils 2.0.0.9 | Zwei Klemmen; 4 Byte Eingang und 4 Byte Ausgang | Table9 0x01D2/0x0226, R16/R29/R30 jeweils 0 |
| `PWM677` | 750-677#16, 2.0.0.3 | Eine bidirektionale Klemme; 16 Byte je Richtung | Table9 0x02A5, R16/R29/R30 jeweils 0 |

Diese Registerwerte sind explizite eigene Profilkonfigurationen. Sie sind keine
behaupteten Werkseinstellungen. Unbekannte Register, UID-Anfragen und unbekannte
Operationen liefern Fehler. Die negative UID-Antwort erzeugt keine Identität.
Die bestehende Modellfehlerreaktion kann dabei das Fault-Latch setzen und
wirksame Ausgänge schließen. Eine abgelehnte Profilauswahl lässt die zuvor
gewählte Konfiguration unverändert.

Die Profile verwenden die originale ADI-Grenze und genuine private Header;
Runtime, I/O-Manager und originale I/O-Treiber werden nicht nachgeschrieben.
Der V2-Transport akzeptiert jetzt zusätzlich die beiden exakten Profilnamen.
Die alte 16-Bit-Schnittstelle ist für Analog/PWM gesperrt, damit größere Frames
nicht unbemerkt abgeschnitten werden. Eine optionale, begrenzte Instrumentierung
protokolliert Initialisierung, Größen, Terminal-/Registeranfragen und erste
zyklische Zugriffe ohne Speicheradressen.

## Engineering und zyklische Prüfprogramme

Das Analogpaar verwendet die unveränderte, am selben Tag bereits erfolgreich
gebaute und schreibfrei wieder geöffnete APP: zwei Eingangswörter
`%IW1/%IW2` auf `%QW0/%QW1`, TCM 0, 20-ms-Task. Quell- und Artefakthashes
wurden erneut verglichen; kein erneuter Analog-IDE-Build wird behauptet.

Der PWM-Prüfbaustein wurde neu gebaut und unverändert wieder geöffnet: alle
24 Felder bleiben gemappt; vier Eingangswörter werden in vier Ausgangswörter
kopiert. Control- und reservierte Ausgangsbytes werden in jedem IEC-Zyklus
auf 0 gesetzt. Das prüft rohe WORD-Datenwege. Bedeutung der PWM-Eingangswerte,
Frequenz, Tastgradwirkung und elektrische Wellenform werden damit nicht belegt.
Die Gerätebeschreibung ergibt 16 Byte je Richtung einschließlich reservierter
Bytes; die 12-Byte-Darstellung des Modulhandbuchs bleibt ein später separat zu
qualifizierender Hardwarevertrag.

## Nachweisgrenzen

Reale Analog-/PWM-Module, elektrische Ausgänge, vollständige Moduldiagnose,
Registerschreiben, alternative PWM-Modi, freie gemischte Bestückungen und
Langzeit-/Echtzeitverhalten sind nicht durch diese festen Profile qualifiziert.
DI8/DO8-Hardware kann später für den digitalen Abgleich dienen; ihre Ergebnisse
übertragen sich nicht auf Analog/PWM. Der CAN-/DALI-Pfad erhält durch diese
Arbeit keinen neuen Kommunikationsnachweis.

## Zusätzliche Startaufrufe

Die neue Instrumentierung machte zwei zuvor nicht namentlich protokollierte
Aufrufe sichtbar: `bac_PROXY_PostTscInterface` und
`bac_PROXY_AssignPlcReadEventItf`. Der gebundene FW31-Producer ist
`libTscIoBacnet.so.2.2.0` (SHA-256
`bd5aa8a420c0a91931328f39ff649654a9c9c23aac090cd87426b926622f996e`).
Seine Funktion `TscIoBacnet_PostTscInterface` wertet weder den äußeren
Dispatcher-Rückgabewert noch den lokalen Ergebnisplatz dieser beiden Aufrufe
aus. Der erste Aufruf ist an ein vorhandenes Eventhandle gebunden, der zweite
folgt innerhalb dieser Funktion ohne solche Bedingung. Das ist ein statischer
Befund dieses Producers, keine allgemeine Aussage über BACnet-Verbraucher.

Der virtuelle Provider liefert für diese nicht implementierten Erweiterungen
`DAL_NOTUSED` zurück und beschreibt den inneren Ergebnisplatz nicht.
Der endgültige Trace kennzeichnet das als `inner=not_written`.
Die vorherige Diagnose hatte dort irreführend einen konstanten inneren Wert
protokolliert; Sentinel-Tests und der frische Lauf prüfen die Korrektur.
Die bestandenen Analogläufe belegen, dass diese Antworten den geprüften
K-Bus-Pfad nicht blockieren. BACnet-Funktion und ein etwaiger Fallback bleiben
**NOT_RUN / OFFEN**. Keine Ersatz-Erfolgsantwort wurde hinzugefügt.

## Prüfstand und ausgeführte Tests

Implementierung: `b651d99` (Profilcode `7f9ff78`) auf Basis `8ba94bf7bf733e120d24bb16c68f1ebbc1faa12d`.
Die [maschinenlesbare Evidence](../evidence/native-integration-2026-10-19.json)
bindet Quell-, Provider-, APP-, CRC- und private Receipthashes. Herstellerdateien,
Zieladressen und Rohlogs bleiben privat. Referenzsoftware: originale Runtime
3.5.21.50, Kernel 6.6.94-rt56-w05.08.02, 750-8213; kein übertragener
Nachweis für einen anderen Controller. Host-Monotonic-Zeit dient nur der
begrenzten Abnahme; 20-ms-IEC-Task und Laufzeit-/Gerätezeit sind keine gemessene
Echtzeitgarantie. Die Uhrzeit in alten Runtime-Logformaten ist keine Testdatierung.

- **PASS:** 285 lokale Tests ohne Skip mit den autorisierten privaten DAL- und
  libpackbus-Headern; unveränderte Quellen durch SHA-256 an den Commit gebunden.
  Kataloggeneratorprüfung, XE164-Snapshotvalidator und `git diff --check` PASS.
- **PASS:** vier eigene ARM-Shared-Provider-Harnesses unter QEMU 10.0.13 und
  Bubblewrap; DI8, DI16, Analog und PWM. Kein Originalconsumer in diesen Harnesses.
- **PASS:** zusätzliche statische ARM-Harnesses für Bytepuffer und native
  Profile/Socketprotokoll. ARM GCC 14.2.0, eigene isolierte `/tmp`-/Netz-/IPC-/PID-
  Umgebung. Der frühere dynamische QEMU-Lauf mit anderem Sysroot scheiterte vor
  Socket-Bind an widersprüchlicher absoluter Pfad-/`openat`-Auflösung (**FAIL**);
  die neue statische Konfiguration mit `-L /` behebt die Testumgebung, ohne
  Providerquellen zu ändern.
- **PASS:** PWM-Projekt frisch gebaut und schreibfrei wieder geöffnet, 24
  Feldzuordnungen; Analogprojekt unverändert aus dem vorherigen Build/Reopen
  übernommen und erneut hashgeprüft. Zusätzliche schreibfreie Bibliotheksinventur
  bestätigt die automatisch eingebundenen PWM-Bibliotheken. Zwei Inventurläufe
  scheiterten an lokalisierter Textserialisierung; der dritte IDE-Lauf beendete
  erfolgreich, sein ASCII-Escaping wurde beim lokalen JSON-Import normalisiert.
- **PASS:** praktische Netzwerk-/Namespaceprüfung mit eigenen Kontrollendpunkten;
  keine geschützte Anlage als Negativkontrolle. Modellpermit blieb 0, wirksame
  Ausgänge blieben 0. Die Tests prüfen angeforderte Frames.

Ein früher Zwischenstand der lokalen Suite fand einen Fehler in den
synthetischen Bytepuffer-Testoffsets; die Korrektur und der erfolgreiche
vollständige Wiederholungslauf bleiben von diesem **FAIL** getrennt. Ebenso
bleiben die drei früheren Analogläufe auf ihre jeweiligen Provider-/Trace-
Revisionen begrenzt; der vierte Lauf verwendet den endgültigen Provider.

Root führte Self-Review und alle Geräte-/VM-Aktionen aus. Tatsächliche getrennte
Offline-Reviews prüften Profilverträge/Fehlerrückgaben, Tracekorrekturen und
Versuchspakete. Sie ersetzen keine Runtime- oder Hardwareprüfung. Es wurde
kein unabhängiger Hardwaretest behauptet.

## PWM-Fehlversuche und nächster Vertrag

Der erste tatsächlich ausgeführte native PWM-Versuch (Paket 2; Paket 1 wurde
nur vorbereitet) konnte die APP wegen `LED_SET_BLINK` nicht laden. Die
Gerätebeschreibung fordert `WagoSysModule_75x_677` und `WagoSysKbusServices`;
diese Bibliotheken erscheinen zusätzlich im nativen PWM-Projekt. Im
Analogprojekt fehlen sie. Die erforderliche Modulbibliothek wurde beibehalten.

Paket 3 nahm ausschließlich die unveränderte originale
`libTscLED.so.0.0.3` (SHA-256
`7a2f51f1f844609a2e4157e74837c3ca0089a5046c21f3ccc62aadbee38dcd8d`)
in die isolierte Komponentenliste auf. Die frisch gelesene Zielhashsumme stimmt
mit dem offline untersuchten FW31-Artefakt überein. Statt 36 wurden 37 originale
Zusatzkomponenten geladen; RunLed, Oms und ChCfgOnline blieben ausgeschlossen.
Host-D-Bus und physische LED-Endpunkte blieben verborgen. **FAIL:** TscLED wurde
geladen, erlitt jedoch eine behandelte `AccessViolation` in `CH_INIT`; die
Runtime verweigerte Bootprojekte im Safe Mode. Das ist eine andere Fehlerstufe
als der vorangegangene unaufgelöste APP-Import. Kein nativer PWM-Zyklus und keine
Auflösung aller APP-Imports werden daraus abgeleitet.

Die weitere statische Analyse bindet den Pfad `CH_INIT` → `LEDCTL_Init` →
`log_EVENT_Init` → `com_GEN_Init`. Dieser fordert eine System-D-Bus-Verbindung
an und übergibt sie vor der NULL-Prüfung an die GLib-Anbindung. Der konkrete
NULL-Zeiger wurde nicht live beobachtet; die Ursachenzuordnung bleibt eine
stark gestützte **HYPOTHESE**. Die beiden darunterliegenden Originalbibliotheken
wurden anschließend frisch auf dem Ziel hashgleich zu den analysierten
FW31-Artefakten geprüft.

[ADR-0010](adr-0010.md) ergänzt deshalb einen echten privaten `dbus-daemon`
1.15.12 ausschließlich innerhalb der vorhandenen Sandbox, auf frischem
`/run`-tmpfs, ohne Host-Bus, Serviceaktivierung oder LED-Dienst. Die originale
LED-Komponente und die erforderlichen Modulbibliotheken bleiben erhalten.
Paket 4 scheiterte zunächst vor Runtime-Start, weil das eigene Startskript
gebrochene `sleep`-Argumente nutzte, die das Ziel-BusyBox nicht unterstützt.
Die Korrektur verwendet ganze Sekunden bei unverändert fünf Sekunden Grenze.
Paket 5 kam danach über Komponenten-/APP-Start und Klemmenprüfung hinaus,
verfehlte aber die bisherige feste Einsekunden-Prozessbindung; sein Checker
blieb **NOT_RUN**. Paket 6 wartet stattdessen begrenzt unter Beibehaltung aller
PID-/Startzeit-/Executable-/Abstammungs-/Namespace-Prüfungen.

**VERIFIZIERT in Paket 6:** originale Runtime **RUN**, Terminal-/Table9-/
R16-/R29-/R30-Prüfungen und zyklische Lese-/Schreibzugriffe erreicht. Die
vorherigen LED-Import-/CH_INIT-Blockaden treten in diesem Pfad nicht mehr auf.
Der externe Frameprüfer blockiert jedoch vor dem ersten Eingangsmuster mit
`MODEL_FAULT`: Der Adapter beantwortet die jetzt erreichte `get_uid`-Anfrage
explizit mit innerem -1 und setzt dabei sein eigenes Fault-Latch. Dies ist
**kein Beleg**, dass die Originalruntime diese Antwort zurückweist; sie war
in RUN. Ebenso ist RUN allein kein vollständiges Modul-PASS. Die sieben
vorgesehenen PWM-Muster sind noch nicht abgenommen.

GET_UID liefert laut exaktem FW31-Provider einen aus der Railbeschreibung
berechneten 32-Bit-Modulidentifikationswert, keine ausgelesene Seriennummer und
keinen Sitzungs-Handle. Die konkrete Zuordnung der 750-677 zum erwarteten
UDINT bleibt **OFFEN**. Weder die Gerätebeschreibungs-ID noch 0x02A5 wird
ungeprüft als UID eingesetzt. Die automatisch eingebundene Bibliotheksversion
1.0.0.3 und ihre installierten Metadaten sind inzwischen privat hashgebunden.
Die lesbaren Metadaten enthalten weder den erwarteten numerischen UID noch
einen belegten Unsupported-Pfad dieses FB. Die REA-Archivinventur erkannte
die compiled library als ZIP, scheiterte aber an ihrer Integritätsprüfung;
kompilierte Payloads wurden nicht ausgewertet und daraus kein Vertrag abgeleitet.
Beim Rückbau sichtbare `libpackbus_async_com_close`-Aufrufe sind ebenfalls
noch nicht unterstützt; ihr benötigter Vertrag bleibt separat offen.

Alle fünf tatsächlich ausgeführten PWM-Pakete 2–6 wurden ordnungsgemäß
zurückgenommen; frischer Original-STOP und sieben unveränderte Originalhashes
jeweils **PASS**. Es gibt keine Ersatz-Erfolgsantwort für LED-/Modul-APIs.

## Abschlusszustand

Die abschließende Geräteprüfung bestätigt Original-STOP, genau einen originalen
Runtimeprozess, keine laufenden eigenen Versuchshilfen oder privaten D-Bus-Daemons und sieben unveränderte
Originaldateien. CAN blieb DOWN/STOPPED mit null RX-/TX-Paketen; CAN-/DALI-
Kommunikation **NOT_RUN**, Koppler-/Datenvertrag weiterhin **BLOCKED**.
Die bereits zu Beginn laufende Windows-VM bleibt laufend; zum Abschluss waren
keine CODESYS-IDE-Prozesse mehr aktiv. Keine Firmware-, Kernel-, Originaltreiber-
oder K-Bus-Masteränderung und kein physischer Aktortest wurden ausgeführt.


## Veröffentlichung und nächste Abnahme

Der Branch baut auf dem offenen Modulerweiterungs-PR auf und bleibt ein
separater Draft-PR; kein Merge in main. Die CI bleibt hardwarefrei und installiert
nun zusätzlich den echten D-Bus-Daemon für zwei isolierte Infrastrukturtests.
Die zwei Harnesses mit privaten Herstellerheadern werden dort explizit
übersprungen; lokale Header-/ARM-/Runtimebelege bleiben getrennt.

Nächster PWM-Abnahmeschritt: die konkrete Railfeld-/UID-Zuordnung und benötigte
Async-Verträge für die gebundene 750-677-Bibliothek belegen, anschließend
gezielte Profil-/Negativtests und erneut alle sieben vollständigen Frames.
Bis dahin keine allgemeine PWM-Fehlerfreiheit oder vollständige Initialisierung
der Modulbibliothek behaupten. Hardwareabgleich folgt unabhängig später.
