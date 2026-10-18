# Begrenzter Originalstack-Prototyp, 18. Oktober 2026

**VERIFIZIERT / PASS:** Ein frisch gebautes natives DI8-Projekt verarbeitet
virtuelle 750-430/750-530 durch CODESYS 3.5.21.50, den nativen I/O-Manager und
die originalen WAGO-I/O-Treiber. Ersetzt wird der bereits belegte untere
ADI-Provider. **BLOCKED:** Das angefragte CAN-/DALI-Teilprofil ist mangels
gebundener Teilnehmeridentität und Prozessdatenverträge nicht implementiert.
Reale CAN-/DALI-Kommunikation ist **NOT_RUN**. Der Auftrag ist damit nur für
den lokalen digitalen Teil durchgehend erfüllt.

Implementierungsstand: `27facec0ffb8d8f84a3eb468e28cf50bb771a0ee`, auf dem
gestapelten Forschungsstand `ec4ea6e3ccef391b76c291b44609e86ace3bc9e5`.
Die [bereinigte Evidence](../evidence/prototype-kbus-can-dali-2026-10-18.json)
bindet Quelltexte, Artefakte, tatsächliche Samples und private Rohbelege per
SHA-256. Spätere reine Berichtscommits ändern diese geprüften Quellen nicht.
CI muss zusätzlich am jeweiligen PR-HEAD geprüft werden.

## Frische Bindung und Implementierung

Die aktuelle private Zielbindung führte zu einem **750-8213**, Kernel
`6.6.94-rt56-w05.08.02`, Runtime `3.5.21.50`, ursprüngliche Anwendung STOP.
Der ältere read-only Bericht zum 750-8212 ist keine Bestandsaufnahme dieses
Versuchs. Die aktuelle Konfiguration unterschied sich vom historischen
Backup; deshalb wurden Bestand, Originaldateien und Rücknahme frisch gebunden.
Der vollständige Bestand der gesicherten Runtimehome-/Konfigurationsverzeichnisse
liegt privat. Das ist kein RAM-/Retain- oder vollständiger Maschinensnapshot.
Die ursprüngliche Anwendung wurde nicht heruntergeladen oder ersetzt.

Der neue [Acceptance-Prüfer](../tools/native_digital_acceptance.py) benutzt
ausschließlich einen privaten AF_UNIX-SOCK_SEQPACKET-Endpunkt des bestehenden
Modellkanals. Er prüft exakte Statusfelder, Kanalwerte, unveränderte Generation,
steigende Framezähler und einen nach INPUT-ACK genommenen Frame-Wasserstand.
Eine Antwort zählt erst mit einem späteren Frame und passendem IEC-Ergebnis.
Noch laufende ältere Zyklen dürfen innerhalb des Gesamtzeitlimits auslaufen.
Ein eigenes Testfixture erzeugt Zyklen unabhängig von STATUS-Abfragen.

Der Prüfer sendet niemals PERMIT. Offene Freigabe, wirksame Ausgänge ungleich
null, Fehlerzustand und fehlende Betriebsbereitschaft brechen kontrolliert ab.
Die sieben negativen Baseline-Fälle prüfen ausdrücklich, dass nur STATUS und
kein INPUT gesendet wird. Weitere Tests binden falsche XOR-Ergebnisse,
Generation-/Zählerrückschritt, veraltete Frames, Disconnect, Timeout,
unbekannte Felder, übergroße Pakete und unsichere Socketpfade. DI16 wird im
Prüfer hardwarefrei getestet, in diesem Block aber nicht nativ ausgeführt.
Ein Prüfer-PASS allein belegt keinen originalen Verbraucher.

Der erste neue IDE-Build scheiterte an englischen Anzeigetexten im vorhandenen
CSV-Prüfer; die IDE exportierte deutsche Beschreibungen. Der
[DI8-Builder](../tools/codesys_mapped_digital8_candidate.py) bindet nun stabile
Parameter-/Gerätekennungen und Variablen. Er prüft vollständige IEC-Adressen,
Richtung, Parent-Byte und Bitreihenfolge; lokalisierte Anzeigetexte sind kein
ABI-Vertrag. Das nachfolgende native Projekt wurde mit null Fehlern und
Warnungen gebaut und schreibfrei wieder geöffnet. Projekt-, Quelltext- und
Mappinghash blieben beim Reopen gleich. Die installierten Descriptor-Dateien
wurden separat tatsächlich gehasht; im Builder hinterlegte Pins allein wären
dafür kein Nachweis.

## Tatsächliche native Signalprüfung

Konfiguration: 750-430 `2.0.0.14`, 750-530 `2.0.0.15`, je acht Kanäle,
TCM 0, 20-ms-Task. `InputByte` liegt nativ auf `%IB1`, `OutputByte` auf `%QB0`;
die Diagnose belegt `%IB0`. IEC-Adressen sind nicht DAL-Prozessdatenoffsets.
Der unveränderte eigene IEC-Test berechnet `InputByte XOR BYTE#16#96`.
Diese Entscheidung läuft ausschließlich in der IEC-Anwendung, nicht im Modell.

| Eingang | Angeforderter Ausgang | Wirksamer Ausgang | Frame nach ACK | Akzeptierter Frame |
|---:|---:|---:|---:|---:|
| 0 | 150 | 0 | 296 | 297 |
| 129 | 23 | 0 | 297 | 298 |
| 90 | 204 | 0 | 298 | 299 |
| 255 | 105 | 0 | 299 | 300 |

Alle Samples: Permit 0, Fault 0, Watchdog 1, opened/configured/running 1,
Generation 1. Der Prüfer benötigte 0,842 Sekunden Host-Monotonzeit bei einem
Gesamtlimit von vier Sekunden. Eine separate native Zustandsabfrage meldete
RUN. Prozessabstammung, PID/Startzeit, Namespaces, geladene Originaltreiber,
eigener Provider und Bootartefakte wurden im privaten Transaktionsbeleg
gebunden. Erst diese Kombination liefert den Originalstack-Nachweis.

Die bestehenden ADI- und Modellquellen wurden frisch mit ARM-Hard-Float-GCC
14.2.0 gebaut. Vier eigene ARM-Harnesses liefen in isoliertem QEMU erfolgreich;
sie sind eine andere Nachweisstufe als die native Prüfung. Der DI8-Provider
ist hashgleich zum früheren korrigierten Provider. Diesmal wurde die
Bootanwendung jedoch frisch mit dem korrigierten Builder erstellt.

Die technische Grenze folgt unverändert [ADR-0005](adr-0005.md) und
[ADR-0006](adr-0006.md): separater Prozess-/Mount-/Netz-/IPC-Namensraum,
Originaldateien schreibgeschützt, keine Bus-/Aktorgeräte, kein Host-D-Bus oder
Docker-Socket. Der bestehende Broker vermittelt ausschließlich genuine
Controller-Metadaten derselben Platine über den schreibgeschützten
EEPROM-Endpunkt. Es gibt keine geklonte Identität und keinen Lizenzbypass.
Der reale Versuch war durch den Broker auf höchstens 30 Sekunden begrenzt.
Seine drei geschützten Metadatenoperationen wurden ohne Pfadfehler vermittelt.

Die praktische Isolationssonde bestand: getrennte Namespaces, keine
Capabilities, schreibgeschützte Originalpfade und nicht erreichbare
Host-Testlistener für Loopback und abstrakte Unix-Sockets. Die SSH-Steuerung
lief unter der exakten privaten Egress-Allowlist mit geprüfter Hostkeybindung;
die negative Netzprüfung verwendete nur einen eigenen lokalen Listener.
Die geschützte Anlage wurde nicht kontaktiert. Der kleine SSH-Stdio-Relay
erlaubte nur STATUS und die vier konkreten INPUT-Kommandos; er verbindet
keinen CAN-Bus.

## CAN und DALI: konkreter Teilblocker

**VERIFIZIERT:** Die Referenz besitzt `can0`; vor und nach dem Versuch war es
DOWN/STOPPED, RX- und TX-Paketzähler jeweils null. Es gab damit keinen bereits
aktiven Verkehr für einen passiven Mitschnitt. Es wurden weder Bitrate noch
Interfacezustand verändert und kein zusätzlicher Master gestartet.

Die aktuelle Runtime lädt CAN-Manager-/Slave-/Layer2-Komponenten. Hashgleiche
lokale Bibliotheken zeigen Socket-/libsocketcan-Imports und `can0`-Strings.
**HYPOTHESE:** Eine Grenze unterhalb des Originalstacks an einem isolierten
SocketCAN-Netdevice könnte kleiner sein als die CAN-Controlleremulation.
Die Imports beweisen weder einen vollständigen Aufrufvertrag noch die
Akzeptanz von vcan oder die Auswahl eines virtuellen Interfaces durch diesen
Treiber. Ein funktionierender virtueller CAN-Transport ist **NOT_RUN**.

Die untersuchten privaten 8213-Projektpakete enthalten CANopen-/EDS-Import-
Paketmetadaten, aber keine gebundene entfernte Gerätebeschreibung, EDS/DCF,
Node-ID/Bitrate, PDO-/SDO-Konfiguration oder DALI-Mailbox. Installierte DALI-
Bibliotheken in einem getrennten IDE-Inventar belegen keine aktive Topologie.
Die allgemeine CANopen-Fähigkeit des Controllers bestätigt nicht das Protokoll
des konkret angeschlossenen Kopplers.

| Lücke / auslösender Schritt | Beobachtung und fehlende Bindung | Kleinster nächster Schritt |
|---|---|---|
| Teilnehmer für gezielte Identitätsabfrage auswählen | Kein Artikel-/Revisionsstand oder belegter Knoten; Interface inaktiv | Eigentümergebundenen Koppler-/Modulbestand und passende native Projekt-/EDS-/DCF-Datei beschaffen |
| Originaltreiber an virtuellen Transport binden | SocketCAN-Imports; Interface-Auswahl/Managementvertrag offen | Nach gebundener Projektkonfiguration den konkreten Caller-/Konfigurationspfad prüfen; isolierten Transport ohne physische Bridge testen |
| CAN-Teilnehmermodell implementieren | Keine belegten Objektindizes, Zustände, Prozessdatenlängen oder PDOs | Tatsächlich genutztes Profil samt Negativantworten aus passenden Herstellerquellen und gezielter Kommunikation binden |
| DALI-Statuspfad und Timeout modellieren | Masterartikel, Mailbox/Busy/Ack und realer Teilnehmer unbekannt | Passende Modulbeschreibung und Bibliotheksbindung ermitteln; dokumentierte Statusabfrage ohne Ausgangsänderung planen |

Reale CAN-Identitäts-/Statuskommunikation, CANopen-SDO/PDO/Heartbeat-Negativfälle
und DALI-Master-/Leuchtenkontakt sind **NOT_RUN/BLOCKED**, ebenso ihre virtuelle
Entsprechung. Es wurden keine Erfolgstelegramme, Objektindizes, CAN-IDs oder
DALI-Befehle erfunden. Ein ADR für eine neue CAN-Architektur wäre erst mit
einem tragfähigen Vertrag sinnvoll; die aktuelle Hypothese ist keine Entscheidung.

## Abnahmematrix, Rücknahme und Grenzen

| Ebene | Ergebnis dieses Blocks | Grenze |
|---|---|---|
| Backend/Werkzeuge | PASS: 247 Tests ohne Skip; vier private ARM-Harnesses | Eigene Modelle und Verträge; kein Hardwarevergleich |
| Digitaler Modelltransport | PASS: echtes AF_UNIX-Protokoll, vier frische native Frames | Kein CAN-Transport; Runtimeherkunft separat gebunden |
| Nativer I/O-Verbraucher | PASS: originales IoDrvDal/IoDrvKbus und nativer Manager | Nur das gebundene DI8-Profil bei TCM 0 |
| Runtime | PASS: neue BootAPP, native RUN-Abfrage, vier IEC-Ergebnisse | Keine neue DI16-, Analog-, PWM- oder Serielle-Abnahme |
| Reale Hardware | PASS nur für Controllerbindung/Isolation/Rücknahme | Modulrevisionen und elektrischer Vergleich OFFEN; Aktortests NOT_RUN |
| CAN/DALI | BLOCKED; Kommunikation und Simulation NOT_RUN | Konkretes Teilnehmerprofil und Vertrag fehlen |

Nach dem begrenzten Versuch wurden nur die gebundenen eigenen Testprozesse
beendet. Der Originalprozess wurde mit temporärem STOP-Startschutz neu
gestartet, danach die exakten ursprünglichen Konfigurationsbytes atomar
wiederhergestellt. Eine weitere Zustandsabfrage bestätigte STOP. Frischer
Postflight: genau eine originale Runtime, keine laufenden Stagingprogramme,
APP/CRC/Konfiguration und vier Originalbinaries hashgleich; CAN unverändert
DOWN mit null Paketen. Das qualifiziert die ausgeführte Rücknahme, keine
allgemeine native STOP-/Watchdog-/Fehlersemantik. Modellpermit 0 allein ist
keine physische Abschaltung; hier kamen Geräteisolation und die private
Eigentümerbindung der Aktortrennung hinzu.

Host-Monotonzeit, konfigurierte IEC-Taskzeit, Modellzeit und Geräteuhr sind
getrennt zu behandeln. Die Geräteuhr war abweichend; Gerätelog-Zeitstempel
sind keine UTC-Belege des heutigen Versuchstags. Framezähler und 20-ms-
Konfiguration beweisen keine elektrische Frequenz oder harte Echtzeit.

Vorstufen bleiben getrennt: erster Tar-Aufruf FAIL wegen eines fehlenden
historischen Servicepfads, korrigierte Verzeichnissicherung PASS; erste
BusyBox-Metadatenabfrage FAIL wegen nicht unterstützter stat-Option;
erste Isolationssonde FAIL wegen Eigentümerrechten der eigenen Stagingdateien,
nach Korrektur ausschließlich dieser Dateien PASS; erster DI8-Harnesslauf
FAIL wegen DI16-Auflösung unter gleichem SONAME, getrennte Profile danach PASS;
erster lokaler Gesamttest mit einem Skip wegen fehlender bwrap-Auswahl,
abschließend 247 PASS ohne Skip. Der frühere IDE-Lokalisierungsfehler wurde
vor dem erfolgreichen nativen Build behoben. Keiner dieser Fehlversuche
wird als erfolgreicher nativer Lauf dargestellt.

Root führte Ziel-/VM-Aktionen und Self-Review aus. Tatsächliche getrennte
Luna-HIGH-Worker prüften offline Quellen, ARM-Build, Code und Transaktion.
Reviewkorrekturen betrafen unter anderem unabhängige Fixturezyklen,
Timeoutgrenzen, Gate-Negativtests und die vollständigen Zeitbudgets des
Rollbackversuchs. Ein Workerreview ist kein zusätzlicher Hardwarelauf.
CI bleibt hardwarefrei; private Artefakte und unbereinigte Traces bleiben lokal.
