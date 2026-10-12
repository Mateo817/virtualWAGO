# Versuchsplan: reale Referenzsteuerung mit virtuellen I/O

Stand: 12.10.2026; **Einbau BLOCKED, P4/P5 NOT_RUN**. Ziel: die autorisierte reale WAGO mit originaler CODESYS-Runtime, nativem I/O-Manager und originalen WAGO-I/O-Treibern. [ADR-0003](adr-0003.md) priorisiert dieses Ziel; [ADR-0004](adr-0004.md) beschreibt den aktualisierten Eigenadapter. [Fortsetzung und Evidence](adi-digital8-continuation-2026-10-12.md) ersetzen die früheren Annahmen über fehlenden Bootbestand und ausschließlich sequenzielle 16-Bit-Tests.

Dieser Plan beschreibt den Versuch und konkrete Abnahmekriterien. Der private ausführbare Start-/Stop-/Restorepayload ist noch nicht qualifiziert; deshalb ist dies **noch keine Vorlage zur Ausführungsfreigabe**. Bereits erteilte Softwarefreigaben gelten weiter. Keine zusätzliche Lizenz für eine vollständig virtuelle Runtime ist Voraussetzung dieses realen Referenzziels.

## Ersatzstelle und Originalkomponenten

Kandidat: der Provider `libdal.so` hinter `adi_GetApplicationInterface()`, dessen 34-Slot-Tabelle der originale IoDrvDal kopiert. Runtime, nativer Manager, IoDrvDal und IoDrvKbus bleiben bytegleich. Das eigene Modell stellt Eingangssignale bereit und verarbeitet Ausgangsbefehle; die IEC-Anwendung enthält die SPS-Entscheidung.

Der Provider liegt ausschließlich in einem privaten Versuchsverzeichnis und wird für genau einen Runtimeprozess ausgewählt. Kein globales Überschreiben von `/usr/lib`, kein Treiberpatch, keine zweite Runtime und kein zusätzlicher DAL-/K-Bus-Master. Ein Hotwechsel der bereits kopierten Tabelle ist nicht belegt; Speicherpatching ist kein geplanter Weg.

Das Mapping von `libpackbus` allein zeigt keinen Hardwarezugriff: der untersuchte Async-Verbraucher importiert keine packbus-Funktionen direkt, seine Wrapper benutzen Dal/VCall, und die untersuchten packbus-Loaderkonstruktoren initialisieren keinen Bus. Originale Komponenten werden deshalb nicht vorsorglich durch weitere Shims ersetzt. **OFFEN:** transitive Dienste, weitere erreichbare Hardware-/D-Bus-/Diagnosepfade und konsistente Loaderauflösung. Diese müssen vor Start mit dem tatsächlichen Payload geschlossen werden.

## Bestand und Sicherung

Reale Frontbestückung: 750-430 → 750-530 → 750-600 laut Eigentümerfoto; Modulrevisionen und erfolgreiche aktuelle zyklische Kommunikation sind offen. Der bestehende Runtimecache zeigt zwei achtbitige Terminalrecords. Der neue native Offlinekandidat verwendet authentische 430/530-Descriptions, ein DI- und ein DO-Byte, zwei native BYTE-Zuordnungen, 20-ms-Task und `OutputPermit=FALSE`. Er wurde erfolgreich gebaut; kein Download auf das Gerät. Vollständige separate Wiederöffnungsprüfung bleibt nach Skriptfehler und inzwischen belegter IDE-Belegung **FAIL/BLOCKED**.

Die vorher bereits vorhandene `Application` bleibt STOP. Root erzeugte mit der echten Online-Bootfunktion persistente Dateien und sicherte APP, CRC und aktualisierte Konfiguration mit vor/nach identischen Hashes privat. Die frühere eigene `VirtualWAGO_Research` ist separat gesichert und war bereits entfernt. Diese Programme sind nicht zu verwechseln.

**Behobenes Gate:** fehlender Bootbestand. **Verbleibend:** Restore/Reboot nicht getestet, ursprüngliches Quellprojekt und Retain-/Persistenzumfang offen. Booterzeugung ergänzt die Startkonfiguration; ein späterer Neustart kann die bisher gestoppte Anwendung starten. Das weiterhin gelöschte Prozess-CWD wird nicht blind repariert. Vor jedem Prozesswechsel müssen Konfigurationsbasis, Boot-Auswahl und STOP-Verhalten konkret gebunden sein. Keine Löschung oder Überschreibung der bestehenden Anwendung als Vorbereitung.

Private Manifestbestandteile: vorhandene APP/CRC/Config, Sicherung der Originalruntime/-libraries/-konfiguration, Device-Description-Versionen/-hashes, eigenes Projekt/APP/CRC/CSV, Adapterquellen und getestete Binaryhashes. Herstellerdateien, Serien-/Lizenzidentitäten und Zugangsdaten bleiben privat.

## Ausführungsfolge und Abnahme

| Stufe | Auszuführende Handlung | Status und Eintrittsgate |
|---|---|---|
| P0: Bindung | Einzielrichtlinie/Hostkey, genau einen Runtimeprozess, Originalhashes, Anwendung STOP und private Sicherung frisch bestätigen | Begrenzte Beobachtung und Bootdateisicherung ausgeführt; kein zusätzlicher Master. Vor Einbau erneut binden. |
| P1: Vertrag | Digitalscan, vier Terminalinfofelder, nativen BYTE-Pfad, VCall-Argumente und Fehlerzweige an exakte Binaries binden | Statisch 22 ADI-Slots belegt; echte native Transaktionsausführung noch NOT_RUN. |
| P2: Eigenadapter | Profil8, Thread-/Generationsbindung, monotone Uhr, verriegelte Fehler und sichtbare Push-/Diagnosefehler prüfen | Eigene ARM-/Shared-/Defaultprüfungen plus Isolationskontrollen PASS. Originalconsumer-Akzeptanz folgt separat. |
| P3: vollständiger Payload | Start-/Stop-/Restorebefehle, Loaderauswahl, prozessbezogenen Geräteschutz, Dienstzugriffe und Modellkanal implementieren und offline reviewen | BLOCKED: unten benannte konkrete technische Lücken. Erst ein gebundener Payload wird zur separaten Freigabe vorgelegt. |
| P4: geschützter Einbau | Bestehenden Prozess über geprüften Weg beenden; genau eine originale Runtime mit privaten Provider-/Konfigurationsdaten und gesperrten physischen Endpunkten starten | NOT_RUN. Erfordert vollständiges P3 und separate Freigabe der Provider-/Busumschaltung; keine neue pauschale Softwareabfrage. |
| P5: Original-I/O-Abnahme | Native Enumeration/Zuordnungen, DI-Muster, angeforderte/wirksame DO, Stop, Fehler und Rücknahme erfassen | NOT_RUN. PASS erst mit Originaltreibern/Runtime und praktisch überprüfter Endpunktsperre. |

Der vorhandene Originalprozess hält `/dev/kbus0` und ein UIO-Mapping. Der Versuch muss diese Zugriffsmöglichkeiten für den **neuen** Prozess technisch ausschließen. Eine Libraryauswahl oder ein Modellpermit allein reicht nicht. Kein globaler/VM-weiter Firewallumbau; kein Host-D-Bus-/Hardwarefallback aus Emulatorprüfungen.

## Signale, sichere Werte und Fehler

Startzustand des 8-Bit-Modells: Eingang `0x00`, angeforderter/wirksamer Ausgang `0x00`, eigenes Permit FALSE, IEC-OutputPermit FALSE, Anwendung STOP. Die elektrische Aktortrennung bleibt Eigentümeraussage; kein physischer Aktortest ist enthalten.

1. Bei STOP definierte DI-Muster `0x00`, `0x01`, `0x80`, `0xA5`, `0x5A`, `0xFF` über den noch zu implementierenden eigenen Modellkanal setzen. Native Enumeration muss zwei achtbitige Module mit den bewusst gewählten Descriptorwerten melden.
2. Nur die eindeutig zugeordnete eigene Testanwendung laden/starten, wenn vorhandene Anwendungssicherung und nicht überschreibende Namens-/Bootstrategie konkret geprüft sind. Die bisherige Offline-App heißt `Application`; sie ist deshalb **nicht direkt ein Downloadpayload** für den bestehenden gleichnamigen Bestand.
3. Zunächst IEC-Permit FALSE: native InputByte muss den Modellmustern folgen, OutputByte bleibt null. Danach nur im technisch hardwarefreien Versuch IEC-Permit TRUE setzen: angeforderter DO-Frame muss die IEC-Reaktion spiegeln. Modellpermit bleibt zunächst FALSE; wirksame DO bleiben null. Eine spätere eigene Modellpermit-Prüfung betrifft ausschließlich virtuelle Werte.
4. Negative Kontrolle: eigener Operationsfehler verriegelt wirksame Ausgänge auf null, behält angeforderte Werte und meldet `BusFault` sowie Push inner `-1`. Der Originalverbraucher prüft statisch äußere/innere Push-Rückgabe; die tatsächliche Runtimefehleranzeige ist noch zu beobachten. Ignorierte ReadEnd/WriteEnd-Rückgaben sind kein ausreichender Nachweis.
5. Watchdog-/Permitverlust, Anwendung STOP und Lifecyclewechsel prüfen. Ein gültiger neuer Frame oder Trigger entriegelt einen Operationsfehler nicht. Explizite gültige Reconfiguration bzw. Close/Open plus neuer vollständiger Frame sind eigene Recoverypolitik.

Hostmonotonzeit, IEC-Taskzeit, Bus-/Cachezeit und logische Modellzeit getrennt erfassen. Laufzeitkandidat wird ausdrücklich mit DIGITAL8/CLOCK_MONOTONIC gebaut. Die Originalruntime benutzt unsere Eingangs-/Permit-/Ausgangserweiterungsfunktionen nicht selbst: eine begrenzte eigene Signal-/Beobachtungsbrücke im Providerprozess fehlt noch. Kein Debugger-/Speicherinjektionskanal und keine nachgeschriebene SPS-Logik als Ersatz.

## Abbruch und konkreter Rückweg

Bei P0–P2: eigene Sitzung schließen, eigene IDE-Prozesse beenden, fremde IDE unangetastet lassen und VM auf ihren Eintrittszustand zurückführen. Der aktuelle VM-Eintrittszustand war laufend; die freigegebene eigene Sitzung lässt sie deshalb laufend. Bestehende Runtime bleibt erhalten.

Für den späteren freigegebenen P4/P5 muss der Payload diese Reihenfolge umsetzen: Modellgate schließen → eigene Testanwendung STOP → einen identifizierten Versuchsruntimeprozess über geprüften gezielten Stopweg beenden → private Provider-/Loaderauswahl zurücknehmen → gesicherte APP/CRC/Config und Originalhashes prüfen/wiederherstellen → genau eine Originalruntime mit kontrolliertem STOP-Start herstellen → lesende Bestands-/I/O-Diagnose gegen P0 vergleichen. Keine parallelen Master, kein pauschales killall, Factory Reset oder physische Ausgabe. Wenn ein Stop nicht bestätigt wird, **keinen zweiten Prozess und keinen Originalhardwarefallback starten**.

Die gesicherte originale `/etc/init.d/runtime` ist kein blind verwendbarer Payload: sie enthält Typenschild-/Lizenz-/Homevorbereitung, Ereignishooks und nach Timeout `killall -9`. Der Versuch benötigt einen gezielten geprüften Prozessweg und darf unveränderte Lizenzidentität/Passwörter nicht durch Nebenaktionen verändern. Der Restoreweg muss die neue Bootpersistenz berücksichtigen; bloßes Entfernen der Adapterbibliothek stellt keinen STOP-Zustand her.

## Präzise Restblocker

- **Prozess-/Startpayload:** Loaderauflösung und vollständige erreichbare Service-/Gerätepfade, technische K-Bus-/UIO-Sperre, gezielter Stop, Boot-Auswahl und STOP-Wiederanlauf sind noch nicht praktisch qualifiziert. Ein Providerwechsel erfordert einen neuen Prozess; für die laufende kopierte Tabelle gibt es keinen belegten Hotwechsel.
- **Modellkanal und Originalakzeptanz:** Eingänge setzen, angeforderte/wirksame Ausgänge lesen und Fehler injizieren haben bislang nur eigene Harnessaufrufe. Es fehlt die konkrete Brücke für den tatsächlichen Runtimeprozess; zudem ist Thread-/Framepolitik mit dem nativen Consumer noch nicht getestet.
- **Geschützte Umschaltung:** Erst nach Schließen dieser Lücken und Hashbindung des fertigen Payloads separat freigeben. Eine Freigabe allein behebt die technischen Lücken nicht.

Diese Grenze stoppt den Einbau, nicht unabhängige Offlineentwicklung. Der Plan behauptet keinen bereits verlustfreien Wiederanlauf und keinen Hardware-/Originalruntime-PASS.
