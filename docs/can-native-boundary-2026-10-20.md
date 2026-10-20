# Originaler CAN-Stack: vcan-Grenze und reale Mappingprüfung

Fortsetzung vom 20.10.2026 auf Basis `d20d07a2a1d5fc78d5f8139bde21d9cfac1558b1`.
Dieser Bericht ergänzt den [CAN2-Erststand](can2-fw31-dali-status-2026-10-19.md).
Private Projekte, Herstellerdateien, vollständige Traces und Zielbindung bleiben
lokal. Gerätezeit und Hostzeit weichen ab; Beobachtungsfenster verwenden relative
Zeiten. Keine Firmwareänderung.

## Virtueller Originalstack

**VERIFIZIERT / PASS, Versuch M:** Originalruntime, originaler I/O-Manager,
`IoDrvCanM`, `libcanopen` und SocketCAN-Transport laufen in einer eigenen
Netzwerk-Namespace mit ausschließlich Loopback und `vcan can0`. Die Anwendung
wurde extern in RUN beobachtet. Der vollständige Mitschnitt enthält 275 Frames:
219 SYNC, 28 Manager-Heartbeats, 18 SDO-Anfragen und 10 gezielte NMT-Telegramme.
NMT war ausschließlich `80 05` (Pre-Operational für Knoten 5).
Es existierte kein virtueller CANopen-Teilnehmer und deshalb keine SDO-Antwort.
Teilnehmerabnahme und DALI-Nachbildung sind damit **NOT_RUN**.

Der [Adapter](../tools/vcan_link_compat.c) ersetzt nur drei Funktionen der
Linkverwaltung; [ADR-0012](adr-0012.md) beschreibt den Vertrag. Unverändertes
vcan lehnt die vom Originaltreiber angeforderte physische Bitratenkonfiguration
mit `EOPNOTSUPP` ab. Akzeptierte Metadaten für 125 kbit/s und eine begrenzte
UP/DOWN-Zustandsprojektion schließen genau diese beobachtete Lücke.
Die Unterstützung von Restart-Metadaten ist durch den separaten Probe geprüft;
sie wurde im erfolgreichen Managerlauf nicht als aufgerufen beobachtet.

Die gehärtete native Probe bestand für DOWN und UP. Vor potentiell ändernden
Bibliotheksaufrufen kontrolliert sie den Kernel-Linktyp, ausschließlich lo/can0
und den tatsächlich nicht vorhandenen negativen Kontrollnamen. Ein Offline-
Worker fand die fehlende Vorprüfung in der ersten Probe; sie ist behoben.
Andere Interfaces werden vom Adapter an die echte Bibliothek weitergegeben.
Deshalb gehört der Adapter ausschließlich in den ausdrücklich isolierten Test.

Fünf IEC-Datensätze mit Zykluszählern 20 bis 100 wurden aus der Testanwendung
aufgezeichnet. Eingangsdaten blieben null; Ausgangsdaten waren `00 32` gefolgt
von 22 Nullbytes. Der Bibliothekstext „DALI-Configurator has access to the DALI
module“ erschien dabei **ohne vorhandenen CAN-Teilnehmer**. Dieser Text allein
belegt folglich weder Masterkontakt noch einen DALI-Gerätekontakt.

## Reales Mapping und korrigierte Engineering-Kopie

Der Eigentümer bestätigt ausschließlich zwei DALI-Adern am Lunatone
DALI-2 PD 300W RL, Artikel 86458618-300, ohne Netzanschluss und Last.
Die bestehende Freigabe umfasst Statuskommunikation. Schalten, Dimmen,
Szenenaufrufe und Adressvergabe gehören weiterhin nicht zum Versuch.

**VERIFIZIERT / FAIL:** Ein begrenzter Same-Value-Probeversuch auf `1602:05`
erhielt SDO-Abort `06020000`, bevor irgendein Mappingdownload bestätigt wurde.
Die EDS beschreibt für PDO 3 und 4 nur vier Mappingeinträge. Ein erfolgreicher
Upload außerhalb dieser deklarierten Einträge hatte irreführend Nullwerte
zurückgegeben; Lesen beweist somit keine Schreib-/Mappingunterstützung.
Die aus dem Kundenprojekt übernommenen acht Byte-Einträge waren dort ungeeignet.

Die korrigierte Kopie verwendet PDO 5–7: `1404..1406` / `1604..1606` sowie
`1804..1806` / `1A04..1A06`. Diese besitzen laut EDS acht Einträge. Alle 83
von den Startup-SDOs betroffenen Werte wurden frisch vom Koppler gelesen und
privat gesichert. Die 48 Mappingwerte entsprechen bereits den vorgesehenen
24 Ein- und 24 Ausgangsbytes; die sechs COB-IDs waren deaktiviert.

**VERIFIZIERT / PASS:** CODESYS-Import, Rebuild, Codegenerierung, Bootdateien und
frisches Wiederöffnen der korrigierten Kopie mit Gerätebeschreibung 6.4.6.11
(FW31) und EDS 1.17. Null Fehler und Warnungen. Der native Re-Export bestätigt
alle 96 erwarteten Startup-SDOs einschließlich Reihenfolge und Nutzdaten.
Die Mapping-CSV ist bytegleich: `%IB1..24`, `%QB0..23` und unveränderte IEC-Namen.
Eine reine Änderung der generierten SDO-Liste wurde beim Rebuild verworfen;
erst die konsistente Änderung der zugrunde liegenden PDO-Parameter und
Kanalzuordnungen blieb nach Neuaufbau und Wiederöffnen erhalten.

Projekt-SHA256: `b8e43f4387f1128c53217282fb85969d7456f16cc3d9e75e4425fddfcba59277`.
Mapping-SHA256: `7135bc9f70f2ebdc5c82d8e420281f1067d8fa110009f692a8711d1a6574b3c6`.
Das unveränderte Kundenprojekt ist eine andere Datei.

## Rücknahme und fehlgeschlagene Vorversuche

Die erste Rücknahmeprobe setzte sechs Mappingzähler auf null und scheiterte
anschließend beim unnötigen erneuten Schreiben der bereits identischen EMCY-
COB-ID `1014:00` mit `08000022`. Die korrigierte Rücknahme liest vor jedem
Download und überspringt identische Werte. Sie stellte die sechs Zähler wieder
her und prüfte anschließend **alle 83 Werte, Identität und NMT 127** erfolgreich.
Die native Startup-Sequenz deaktiviert und aktiviert die EMCY-COB-ID explizit;
sie ist nicht mit diesem fehlgeschlagenen Same-Value-Download gleichzusetzen.

Weitere eigene Vorversuche sind getrennt archiviert: falsche Archivbesitzer,
unvollständige CAN-Instanzkonfiguration, fehlende Thread-Berechtigung,
unvollständige vcan-Linkanpassung und eine zu langsame Prozesssuche.
Die Suche filtert jetzt günstig nach Prozessname und bindet anschließend
Executable, Startzeit, Elternkette und Namespaces. Absolute IEC-Dateipfade
wurden abgelehnt; beim relativen Append-Zugriff zeigte der Syscall-Trace eine
fehlende Datei. Eine vorab angelegte Datei im privaten IEC-Verzeichnis löste
das Problem. Ein erster physischer Runner lehnte die eigene ungültige
Broker-Zeitgrenze vor Runtime-Start ab. Diese Fehler sind keine bestandenen
CAN-/DALI-Abnahmen.

## Reale Runtimeversuche B und C

**VERIFIZIERT / PASS im Teilumfang:** Der unveränderte Originaltreiber tauschte
98 SDO-Anfragen und 98 Antworten mit dem realen Koppler aus. Kein SDO-Abort
trat auf. Die korrigierte Startup-PDO-Konfiguration wurde quittiert.

**FAIL:** Der vollständige Lauf blieb nicht bis zum Ende des Beobachtungsfensters
stabil. In Versuch B wurde RUN extern gesehen, aber nur vier IEC-Datensätze
aufgezeichnet. Es gab keine PDOs; Knoten 5 blieb Pre-Operational. Versuch C
zeichnete mit zusätzlichem Prozess-/Signaltrace zwei `SIGSEGV` bei Adresse
`0x1c`, anschließend `SIGABRT` und die Meldung `corrupted double-linked list`
auf. Trace-Overhead und fehlende Hilfsdienste der Isolation sind als mögliche
Einflussgrößen getrennt zu berücksichtigen. Der verursachende Code ist damit
noch nicht identifiziert. Kein DALI-Gerätekontakt ist belegt.

Beide Versuche stellten die 83 gesicherten Kopplerwerte wieder her und
verifizierten sie durch Upload. Originalanwendung, CRC, Konfiguration und
geprüfte Originalbinaries blieben hashgleich; die Originalruntime wurde wieder
in STOP gestartet. Der physische CAN-Link wurde DOWN mit 125 kbit/s,
Restart-ms 0 und Tx-Queue 10 zurückgegeben. Ein Namespacewechsel kann die
qdisc verändern; keine Behauptung eines bitgleichen gesamten Interfacezustands.
Diagnosehistorie und interner DALI-Modulzustand sind kein Bestandteil des
83-Objekt-Konfigurationsbackups.

## Kontrolllauf D: CAN-Transport getrennt von IEC/DALI

**VERIFIZIERT / PASS für den Transport:** Eine neu gebaute Kontrollkopie mit
identischer CAN-Konfiguration und `xEnableMaster=FALSE` umgeht sämtliche
DALI-Bausteinaufrufe. Der Originalmanager sendete gezielt `80 05`, danach
`01 05`. Knoten 5 erreichte damit den zyklischen Datenaustausch: alle sechs
PDO-Ströme enthalten jeweils 303 Frames. Die drei Eingangstelegramme ergeben
`01 00`, sechzehnmal `AA` und sechs Nullbytes. Alle drei Ausgangstelegramme
enthielten Nullbytes. Wieder 98 SDO-Anfragen/Antworten ohne Abort.

Der eigene Runtimeprozess überlebte das 16-Sekunden-Beobachtungsfenster.
RUN wurde am Fensteranfang abgefragt; der Endzustand der IEC-Anwendung wurde
nicht erneut abgefragt. **FAIL für die zyklische IEC-Abnahme:** Es liegen
nur vier Logdatensätze mit Zählern 20..80 vor, alle vor dem PDO-Austausch und
mit Nulleingängen. Damit ist die fortlaufende Übergabe der echten Modulbytes
bis zur IEC-Variable nicht belegt. Die Kombination aus laufendem CAN-Transport
und endender IEC-Protokollierung ist die nächste präzise Untersuchungsgrenze.
Die Ursache des Speicherfehlers bei aktiven DALI-Aufrufen bleibt **OFFEN**;
der Kontrolllauf allein ordnet ihn noch keinem konkreten Baustein zu.

**NOT_RUN:** Ein belegter Query/Response-Austausch mit dem Lunatone-Gerät.
Die verwendete Diagnosebibliothek liefert eine Adresstabelle; ohne fortlaufende
IEC-/Mailbox-Daten ist daraus kein tatsächlicher Geräteantwortnachweis möglich.
Kein Ausweichen auf Adressierung, Schalten oder erfundene DALI-Befehlsbytes.

Nach Kontrolllauf D: Rücknahme aller 83 Kopplerwerte, Identität, NMT 127,
Original-STOP und Hashvergleich **PASS**. Frische Schlusskontrolle: CAN DOWN,
keine eigenen bwrap-/strace-/candump-/sleep-Testprozesse verblieben. Die vorher
laufende Windows-VM bleibt laufend; eigene IDE-Läufe sind geschlossen.

## Prüfstand und Grenzen

**PASS:** 287 lokale Tests ohne Skip mit explizit bereitgestellten privaten
Headern und isolierter bwrap-Testumgebung. Der erste Lauf ohne diese Umgebung
hatte zwei Fehler und vier Skips; er ist nicht als PASS umgedeutet.
Öffentliche CI bleibt hardwarefrei. Sie prüft insbesondere die Weiterleitung
an einen Testprovider, nicht einen realen CAN-Controller.

Self-Review und tatsächlicher Offline-Worker-Review sind getrennt:
Der Worker prüfte die vcan-Probe und die native PDO-Transformation, führte
aber keine VM-/Controlleraktionen aus. Positive Liveprüfungen führte der
leitende Agent aus. Keine unabhängige Hardwareabnahme wird behauptet.

Die [sanitisierte Evidence](../evidence/can-native-boundary-2026-10-20.json)
bindet Quellen, Projekte, private Rohlog-Hashes und getrennte Prüfstufen.
