# Reale Referenz: begrenzte Beobachtung und Vertragsdelta

Stand: 12.10.2026 UTC. Ausgangsrevision `acff577c59dc3235247b14a47eacbd2cd4066cf6`, Base `0bdddbf77d688fd9e1cce7165d718fa6a30efe2c`; Draft-PR #2 frisch geprüft. Root war alleiniger Geräte-/VM-Integrator. Quellen, Testscope und bereinigte Metadaten: [Evidence-JSON](../evidence/real-controller-observation-2026-10-12.json). Rohdaten, Gerätezuordnung, Zugangsdaten und Herstellerdateien bleiben privat.

## Frische Bindung und Zustandserhalt

**VERIFIZIERT:** strikte SSH-Hostkeybindung und lokale Einzielrichtlinie; Route ohne Netzwerkprobe geprüft. Der prozessbezogene Namespace-Selbsttest bestand mit eigenem Loopbacklistener und erhöhtem Kernelzähler; kein ausgeschlossenes Ziel wurde dafür kontaktiert. Keine globale oder VM-weite Firewalländerung.

**VERIFIZIERT:** Referenzmodell `750-8213`, Kernel `6.6.94-rt56-w05.08.02`, Firmwaremarker `04.09.01(31)` aus `/etc/REVISIONS`. Genau ein `codesys3`-Prozess; originale Runtime-, DAL-, I/O-Treiber-, packbus- und Konfigurationshashes stimmen mit den privaten Sicherungen überein. Die Runtimeversionszeichenfolge `3.5.21.50` bleibt an diese Bytes gebunden. Serienidentität und Hardwarestand bleiben **OFFEN**; unklare EEPROM-/Typenschildgetter wurden nicht ausgeführt.

Der erneute gezielte CODESYS-Login `Keep, False` beobachtete `STOP / program_loaded`. Kein Download, Start, Stop, Reset, Löschvorgang oder Runtime-Neustart wurde angefordert. Die IDE meldete einen Zertifikatshinweis; Zertifikate und Zugänge wurden nicht geändert. Tatsächlicher IDE-Exit 0, keine eigene IDE übrig; Hashbindung von Payload/IDE/Profil im Evidence-JSON. Die VM wurde nach eigener Nutzung wieder auf Datenträger pausiert; Status und inaktive Sitzung separat bestätigt.

**VERIFIZIERT:** das Runtime-Arbeitsverzeichnis ist weiterhin gelöscht; der aktuelle gleichnamige Pfad enthält bei der begrenzten Dateisuche nur `CODESYSControl.cfg`. **OFFEN/BLOCKED:** wiederherstellbares Projekt/Bootprojekt der bisherigen RAM-Anwendung. Das ist kein vollständiger Datenträger- oder RAM-Forensikbefund. Keine Wiederherstellung, Reparatur oder Speicherextraktion wurde versucht.

## Tatsächlich beobachtete Anbindung

Die vorhandene Runtime mappt `libIoDrvDal`, `libIoDrvKbus`, `libdal`, `libpackbus`, `libwago_dbus` und `libdiagnostic`. Sie hält einen Deskriptor auf `/dev/kbus0` und ein Mapping von `/dev/uio0`. Gelesen wurden ausschließlich `/proc`-Metadaten; diese Endpunkte wurden durch den Collector nicht geöffnet, gelesen oder geschrieben.

Beobachtete Taskklassen umfassen zwei DAL-Tasks, zwei KBUS-Tasks, zwölf bekannte WagoAsync-Worker und einen Terminalregisterworker. Threadnamen zeigen vorhandene Ausführungskontexte, keine gemessene Callbacküberlappung oder garantierte Thread-Sicherheit. Bibliotheksmapping und Gerätebindung zeigen keinen Nachweis erfolgreicher aktueller zyklischer I/O oder des IEC-Mappings.

Der neue eigene [Offlineparser](../tools/runtime_observation.py) verarbeitet explizit gespeicherte Maps-, FD-, Task- und CWD-Texte. Er gibt nur feste Komponenten-/Taskklassen und boolesche Beobachtungen aus, niemals Rohadressen, beliebige Pfade, Tasktexte oder Socket-Inodes. Fehlende Eingaben bleiben OFFEN; Syntaxfehler werden zurückgewiesen. Die CLI prüft direkte `/proc`-/`sys`-/`dev`-Pfade und regulären Dateityp vor dem Öffnen sowie Dateityp/Inode danach. Sie setzt vertrauenswürdige zuvor gespeicherte gewöhnliche Dateien voraus; diese Prüfungen verhindern Fehlbedienung und ersetzen keine Dateisystem-/Mountisolation gegen feindliche Aliasse oder Namespaceänderungen. Der Parser ist kein Gerätecollector und keine Einsatzfreigabe. Er wurde mit dem vollständig abgeschlossenen privaten Snapshot ausgeführt.

## Belegter passiver D-Bus-Weg

Ein tatsächlicher Sol-Worker prüfte offline die exakten FW31-Binaries `libpackbus` und `libwago_dbus`. Root prüfte die relevanten Callbackpfade ebenfalls statisch und band deren Hashes frisch am Gerät. Die registrierten Getter für Status und Prozessbildmetadaten lesen den vorhandenen Cache. Ihr Dispatch zählt die Anfrage und kopiert interne Snapshotdaten; er ruft keinen Moduswechsel, `Push`, Masterstart oder Geräte-`ioctl` auf. Autonome Buszyklen der bereits laufenden Runtime bleiben davon unabhängig.

Vor dem Getter wurde der bestehende Eigentümer von `wago.kbus` über den D-Bus-Daemon ermittelt und dessen PID an den einen Originalruntimeprozess gebunden. Anfragen gingen ausschließlich an diesen **bestehenden eindeutigen Eigentümer**, mit 2000-ms-Antwortgrenze, ohne Dienstaktivierung oder Fallback. Kein neuer DAL-/K-Bus-Client wurde initialisiert. Vier einmalige Cacheabfragen wurden ausgeführt; keine periodische Abfrage, kein generisches Introspection-/Modus-/Registerprobieren. Ein Antworttimeout würde den Callback nicht abbrechen; die geprüften Blätter enthalten keine Busaktion.

| Beobachtung | Anfrage / Typ | Ergebnis / enger Scope |
|---|---|---|
| Status | `/wago/kbus/status`, `wago.kbus.get`, `uint16:0` | Neun `uint16`: `[32, 2, 0, 0, 0, 0, 0, 8, 8]`; zweites Wort ist der gecachte Terminalcount 2. |
| Offsets | `/wago/kbus/terminals/pi/offset`, gleicher Typ/Wert | Zwei `uint16`: `[0, 0]`; aus gecachten SSC-Feldern durch Division durch acht abgeleitet. |
| Positionen, direkter Selektor 0 | `/wago/kbus/terminals/pi/pos`, `uint16:0` | Zehn Nullwörter. Nicht als zwei Module ohne Prozessdaten interpretiert. |
| Positionen, belegter Selektor 1 | gleicher Getter, `uint16:1` | Zwei Records: `[0, 0, 8, 0, 0]`, `[0, 0, 0, 8, 0]`. |

Die Selektoren sind **nicht austauschbar**: der FW31-Status-/Offsetpfad übersetzt öffentlichen PI-Index 0 über seine 12-Byte-Deskriptortabelle auf internen Cache-Selektor 1. Der Positionsgetter benutzt den Anfragewert direkt. Die zweite Positionsabfrage wurde erst nach diesem statischen Nachweis gewählt, nicht durch Durchprobieren unbekannter Indizes. Die Tabelle liegt bei VMA `0x337d0`; der erste Eintrag beginnt mit Selektor 1. Der passende Setter verändert das dritte Tabellenwort, keine identifizierte Schreibstelle verändert dieses erste Wort. Dies bindet den statischen und beobachteten Pfad, keine allgemeine API aller Firmwarestände.

Die ersten vier Positionswörter stammen aus den vier 32-Bit-SSC-Cachefeldern und werden auf `uint16` begrenzt. Der authentische FW30-Header benennt diese als Eingangs-/Ausgangsbitoffset und Eingangs-/Ausgangsbitlänge; der FW31-Getter kopiert dieselben vier Positionen. **HYPOTHESE, quell-/binarygestützt:** im beobachteten Cache hat der erste Record acht Eingangsbits, der zweite acht Ausgangsbits, je Offset null in der eigenen Richtung. Das fünfte Wort ist ein anderes rohes Rail-Deskriptorfeld und **kein belegter Artikel-/Modul-Identifier**. Alle Requests blieben im statisch belegten Cachebereich; Terminalcount 2 wurde vor Positionsabfragen geprüft. Separate Getter sind kein global atomarer Snapshot. Gerätezeit und Log-/D-Bus-Zeitstempel weichen vom Hostdatum ab; sie wurden nicht als kalibrierte UTC-Messzeit übernommen.

**VERIFIZIERT als Eigentümeraussage:** zwei physisch angeschlossene Module und fortgeltende elektrische Aktortrennung. **VERIFIZIERT im Cache-Scope:** bestehende Runtime meldet zwei Terminals. **OFFEN:** genaue Artikelnummern, Revisionen, physische Reihenfolge, elektrische Verdrahtung und erfolgreiche aktuelle zyklische Kommunikation. Cachecount und Recordform ersetzen diese Belege nicht. Es wird insbesondere keine Bestückung mit 750-1405/750-1504 behauptet.

## Konsequenzen für den Adaptervertrag

1. Der vorhandene 16-Bit-DI/16-Bit-DO-Adapter samt 2-Byte-Packung bildet einen bewusst eigenen 1405/1504-Kandidaten ab. Die neue 8-Bit-Cacheform qualifiziert diesen Kandidaten nicht für den beobachteten Bestand und darf dessen Typen nicht automatisch festlegen. Eine neue Belegung benötigt Identitäts-, Größen- und Parameterbelege.
2. DAL-, D-Bus-, Register-, Watchdog- und Async-Ausführungskontexte sind tatsächlich vorhanden. Der sequenzielle Adapter bleibt auf Eigenclienttests begrenzt. Synchronisation, Transaktionszuordnung, Callbackende und Close/Exit müssen für den ausgewählten Originalpfad belegt und implementiert werden; ein globales Mutex ohne Lifecyclevertrag wäre kein Nachweis.
3. Die logische Watchdoguhr und vollständigen Frame-/Latchregeln aus ADR-0002 bleiben Modellpolitik. Kein Cachegetter beweist Watchdogdauer, zyklische Scanreihenfolge, Atomarität oder Originalfehlerreaktion.
4. Der Originalruntimeprozess benutzt bereits physische K-Bus-/UIO-Endpunkte. Der geplante ADI-Ersatz muss alle verbleibenden Pfade erklären und technisch schließen, ohne Originalmanager oder Originaltreiber umzuschreiben. Der passive reale D-Bus-Leseweg darf nicht als Hardwarefallback in den Simulator gelangen.

Die authentischen cached `read_table_9`- und `get_kbus_status`-Handler sind zusätzlich statisch gebunden; ihre Ausführung über einen neuen DAL-Client wäre trotzdem ungeeignet, weil dessen Open/Init den Hardwarepfad erneut aufbauen könnte. Der D-Bus-Weg oben nutzt die bestehende Instanz. Er schließt die Diagnosebeobachtung, nicht den gesamten ADI-/Modulvertrag.

## Tests, Fehler und verbleibende Gates

**PASS:** 116 hardwarefreie Python-Tests unter Python 3.13.5, davon 17 neue Parsertests; Parserlauf auf dem vollständigen privaten Snapshot. **PASS im engen Scope:** Einziel-Netzwerk-Selbsttest, vollständiger lesender Snapshot, bestehender D-Bus-Eigentümer/PID, vier geprüfte Cachegetter, frischer `Keep`-Login und VM-Rückführung. Tests/CI werden zusätzlich am finalen Commit gebunden; alte C-/IDE-Build-PASS werden nicht auf diesen neuen Stand übertragen.

**FAIL, transparent erhalten:** zwei frühe Snapshotläufe endeten wegen nicht vorhandener regulärer Pfade (`/etc/RELEASE`, `/usr/bin/config-tools`); eine weitere Metadatenabfrage endete nach gültigen Library-/Toolhashes wegen des fehlenden `/etc/dbus-1/system.d`. Keine unbekannten Geräte-APIs wurden daraufhin ausprobiert. Der vollständige korrigierte Snapshot ist separat gebunden. Der erste Parserlauf lehnte legitime anonyme Maps mit trailing Whitespace ab; der Parser wurde korrigiert und erhielt einen Regressionstest. Rohfehler und erfolgreiche Nachläufe bleiben privat.

Integratorprüfung: **Self-Review**. Tatsächliche Luna-Worker bearbeiteten offline Dokumente, Diagnostikquellen und Parser; gezielter Sol-Worker prüfte die passiven FW31-D-Bus-Blätter und den Plan. Kein Worker führte Hardware-/VM-Tests aus. Statische Analyse, Review und Root-Ausführung sind getrennte Nachweisstufen.

**BLOCKED / NOT_RUN:** Adaptereinbau, Provider-/Masterwechsel, Original-I/O gegen Simulation und Wiederanlauf. Konkrete Gates: wiederherstellbare bisherige Anwendung, Modul-/Projektzuordnung, vollständiger Ersatzschnitt und Parallel-/Fehlervertrag, qualifizierter Prozessschutz/Adapter sowie separate Freigabe des fertigen Wechselpayloads. Zusätzliche vollständig virtuelle Runtime-Lizenz ist kein pauschaler Blocker dieses ersten Ziels. [Versuchsplan und Rückweg](real-controller-plan-2026-10-12.md). Kein Merge.
