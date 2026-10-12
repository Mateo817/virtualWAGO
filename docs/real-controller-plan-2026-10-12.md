# Versuchsplan: reale Referenzsteuerung mit virtuellen I/O

Stand: 12.10.2026; **HYPOTHESE / Einbau BLOCKED**. Dieser reviewbare Plan konkretisiert [ADR-0003](adr-0003.md). Ziel ist die reale autorisierte Referenzsteuerung mit ihrer Originalruntime, nativem I/O-Manager und originalen WAGO-I/O-Treibern. Er ist keine Ausführungsfreigabe für einen Hardware-/Providerwechsel. Aktuelle Beobachtungen und Hashbindung: [Beobachtungsbericht](real-controller-observation-2026-10-12.md).

## Ersatzstelle und Erhalt der Originalkomponenten

Die konkrete Kandidatengrenze ist die 34-Slot-ADI-Tabelle hinter `adi_GetApplicationInterface()`. Der gebundene `libIoDrvDal.so.1.0.2` importiert `libdal.so`, kopiert die Tabelle und benutzt ihre Methoden; `IoDrvDal.cfg` bindet `libpackbus` an `IoDrvKbus_Init`. Originale Runtime, nativer Manager, `IoDrvDal` und `IoDrvKbus` bleiben bytegleich. Das Modell liefert Signale und verarbeitet Ausgangsbefehle unter dieser Grenze; die IEC-Anwendung enthält weiterhin die SPS-Entscheidungen.

Der eigene Provider soll in einem privaten Versuchsverzeichnis liegen und ausschließlich für den einen geplanten Runtimeprozess ausgewählt werden. Keine globale Ersetzung von `/usr/lib`, kein Patch der Originaltreiber, keine zweite Runtime mit Zugriff auf den realen Bus und kein zusätzlicher DAL-/K-Bus-Master. Die private Loaderkonfiguration muss vor Einbau nachweisen, dass der originale Hardwareprovider `libpackbus` nicht als Fallback geladen wird. Die aktuelle Adapterbibliothek ist nur ein sequenzielles Eigenclientmodell; sie ist **kein einbaufähiger Runtimeadapter**.

**OFFEN:** Der vollständige Ersatzschnitt umfasst möglicherweise mehr als die ADI-Tabelle. Im bestehenden Prozess sind K-Bus-Gerätepfad, UIO-Mapping, D-Bus, Diagnose, DAL-Watchdog und Async-Threads beobachtet. Jede erreichbare Umgehung der ADI-Grenze muss aus den exakten Originalkomponenten erklärt und gegen physische K-Bus-Anbindung geschlossen werden. Eine erfolgreiche Symbolauflösung allein erfüllt dieses Gate nicht. Fehlende interne CODESYS-Header sind kein pauschales Gate, solange der Originalmanager seine eigenen Objekte erzeugt.

## Vorhandene Anwendung und Sicherung

Die vorhandene Anwendung wurde erneut mittels `Keep, False` als `STOP / program_loaded` beobachtet. Der Runtimeprozess verwendet weiterhin ein gelöschtes Arbeitsverzeichnis. Im aktuellen Pfad wurde nur die Konfiguration gefunden; es gibt kein gesichertes wiederherstellbares Bootprojekt dieser Anwendung. Das vorhandene PKI-/Konfigurationsbackup ersetzt dieses Projekt nicht.

**Konkrete Sperre:** Keine Runtimebeendigung, kein Neustart, kein Download, kein Anwendungsreset und keine Reparatur des Arbeitsverzeichnisses als Versuchsvorbereitung. Ein neuer Prozess würde die einzige bekannte geladene Kopie verlieren. Ein belegter sicherer Hot-Wechsel der bereits kopierten ADI-Tabelle ist ebenfalls nicht verfügbar; Speicherpatching oder Debuggerinjektion sind kein Rückweg.

Vor einem Wechsel sind privates Originalprojekt bzw. ein tatsächlich wiederherstellbares Bootprojekt, zugehörige Bibliotheken/Device Descriptions, Retain-/Persistenzdaten soweit relevant und Originalkonfiguration versions-/hashgebunden zu sichern. Die Eigentümerquelle der bisherigen Anwendung und deren Wiederherstellung müssen geklärt sein. Ein Backupcheck benötigt lesbare Archive/Manifeste und einen belegten Restoreweg; ein bloßer Dateihash ist kein Restoretest. Falls die Anwendung nicht wiederherstellbar ist, benötigt ihr bewusster Verlust eine eigene konkrete Eigentümerentscheidung und einen angepassten Plan. Diese Entscheidung wurde nicht eingeholt und nicht angenommen.

Originale Runtime-/DAL-/I/O-Dateien und Konfiguration liegen bereits privat vor; ihre zentralen Hashes wurden frisch verglichen. Unbekannte Geräte-/Modulrevisionen bleiben eigene Inventarlücken. Herstellerdateien, Identitäten, Lizenzdaten, Rohlogs und Zugangsdaten bleiben lokal. Die vorhandene berechtigte Runtime auf demselben Referenzgerät bleibt das Ziel; keine zusätzliche vollständig virtuelle Runtime oder geklonte Lizenzidentität wird vorausgesetzt.

## Stufen und Freigabegrenzen

| Stufe | Konkrete Aktion und Ergebnis | Eintritt / Abbruch |
|---|---|---|
| P0: lesende Referenz | Hostkey/Allowlist/Route, Hashes, genau ein Runtimeprozess, `Keep`-Zustand, begrenzte belegte Cachegetter und Bestandsquellen prüfen | Keine Dienststarts, Scans, Prozessbild-/Registerschreiboperationen. Bei Identitätswechsel, unbekanntem Handler oder falschem D-Bus-Eigentümer abbrechen. |
| P1: Vertrag offline | Reale Beobachtungen mit FW31-Verbrauchern/Provider und authentischen Headern verbinden; Funktions-, Fehler-, Zeit-, Callback- und Parallelvertrag vervollständigen | Unbekannte Typen/Layouts/Offsets bleiben OFFEN. Cachewerte sind kein elektrischer oder zyklischer Kommunikationsnachweis. |
| P2: Adapter offline | Eigenen Provider für den bewusst festgelegten virtuellen Modulstrang qualifizieren; Originalverbraucherpfade, Fehlerkontrolle und Prozessisolation prüfen | Framepackung, vollständige DO-Frames und Watchdogpolitik sind zunächst Modellannahmen. Eigenclient-PASS ersetzt keine Originaltreiberakzeptanz. Kein Geräte-/Host-D-Bus-Fallback. |
| P3: Wechsel vorbereiten | Wiederherstellung der bisherigen Anwendung, Quellenmanifest, exakter Loader-/Dienststart, Port-/IPC-/Gerätezugriffe, Ausgangsgates, Rücknahme und Abnahmeskript vollständig binden | Jetzt BLOCKED: RAM-App-Rückweg, vollständiger Parallel-/Dienstvertrag, Prozessschutz und qualifizierter Adapter fehlen. Erst dann den vollständigen Payload separat für Provider-/Buswechsel vorlegen. Bestehende Softwarefreigabe bleibt bestehen. |
| P4: freigegebener Einbau | Genau einen Originalruntimeprozess mit dem qualifizierten privaten ADI-Provider und Originaltreibern starten; reale Busendpunkte im Versuchspfad technisch ausgeschlossen | Nur nach separater konkreter Freigabe des Provider-/K-Bus-Wechsels und erfülltem P3. Keine globalen oder VM-weiten Firewalländerungen. Keine Änderungen an Passwörtern, Firmware, Bootloader oder Kernel. |
| P5: Original-I/O-Abnahme | Native Enumeration, definierte DI-Muster und angeforderte/wirksame DO getrennt, Stop und negative Kontrolle beobachten; danach Rücknahme | Keine physische Ausgabe. Unerwartete Komponenten, Buszugriff, Datenumfang, Fehlerantwort oder fehlendes Ausgangsgate: sofort Versuchsgate schließen und belegte Rücknahme. |

Die vorhandenen zwei Module sind eine Referenzquelle, keine bereits identifizierten 750-1405/750-1504. Ein virtueller 1405/1504-Strang kann bewusst als eigener Offline-/Testbaum gewählt werden; das macht ihn nicht zum Abbild des realen Bestands. Der Plan für einen anderen Modultyp benötigt dessen eigenen belegten Vertrag. Kein unbekannter Modultyp erhält erfundene Erfolgsantworten.

## Sichere Werte, Zeit und Nachweis

Für den vorhandenen digitalen Modellkandidaten: `OutputPermit=FALSE`, angeforderter Startframe `0x0000`, wirksamer Frame `0x0000`, Anwendung zunächst STOP, Watchdog zunächst nicht gesund. Ausgänge werden erst nach vollständigem gültigem Frame und sämtlichen Modellgates wirksam. Gateverlust, unbekannte Operation, fehlendes Modul und Modell-Timeout setzen die wirksamen Ausgänge auf null. Für Analog-/PWM-/Spezialmodule muss ein eigener sicherer Zustand belegt werden; numerisch null ist dort keine allgemeine Sicherheitszusage.

Die elektrische Aktortrennung ist eine fortgeltende Eigentümeraussage, keine eigene Messung. Der Versuch führt keine physischen Aktortests durch. Die technisch ausgeschlossene Busanbindung muss praktisch geprüft werden; ein im Modell gesetztes Permit sperrt keinen realen Gerätepfad.

Das native gespeicherte Offlineprojekt ist ein Kandidat mit zwei WORD-Zuordnungen und 20-ms-Task; kein vorhandenes Referenzmapping. Nach Klärung der Anwendung wird ausschließlich eine eindeutig benannte eigene Testanwendung mit deaktiviertem Autostart vorgesehen, ohne fremde Anwendungen zu löschen. DI-Signalfolge z. B. `0x0000`, `0x0001`, `0x8000`, `0xA55A` wird durch das Modell geliefert; die IEC-Logik verarbeitet sie unverändert. DO wird zunächst nur als angeforderter Frame beobachtet, wirksame Werte bleiben gesperrt. Eine negative Kontrolle muss im Originaltreiber bzw. in der Runtime sichtbar werden, da beobachtete Verbraucher End-Rückgaben teilweise verwerfen. Eigenes Fehlerrückgabeverhalten allein genügt nicht.

Hostmesszeit, Runtime-/Taskzeit, Bus-/Cachezeit und logische Modellzeit werden getrennt erfasst. `virtual_adi_advance_time_us` ist weiterhin eine eigene logische Uhr. Aus einem Cachegetter werden weder Watchdogdeadline, Scanrate noch Frameatomarität des Originalproviders abgeleitet. Stop/Start der eigenen Anwendung und Runtime-Neustart sind getrennte Versuche; Neustart ist keine automatische Fehlerbehandlung.

## Konkreter Rückweg und seine gegenwärtige Grenze

Bei P0–P2 bleibt der vorhandene Runtimeprozess unangetastet; eigene Lesesitzungen werden geschlossen, die eigene IDE beendet und die VM auf ihren vorherigen Zustand zurückgeführt. Das ist der gegenwärtig ausführbare Rückweg.

Nach einem erst später freigegebenen P4: Ausgangsgate schließen, ausschließlich die eigene Testanwendung stoppen; dann den einen Versuchsruntimeprozess über den zuvor geprüften Stopweg beenden. Private Loaderauswahl/Versuchskonfiguration entfernen, Originaldateihashes und Originalstartkonfiguration bestätigen, gesicherte ursprüngliche Anwendung mit belegtem Restoreweg wiederherstellen und im vereinbarten STOP-Zustand starten. Original-I/O- und Diagnosezustand lesend gegen P0 vergleichen. Keine parallel laufenden Master; keine pauschalen `killall`-/Factory-Reset-/Autostartaktionen. Die Rückkehr zur physischen Busanbindung ist Teil desselben gesondert freizugebenden Plans.

**BLOCKED:** Heute kann dieser Wechselrückweg die bisherige RAM-Anwendung nicht rekonstruieren. Deshalb sind P4/P5 **NOT_RUN**. Der Plan macht die fehlenden Voraussetzungen konkret; er stellt keinen verlustfreien Rollback in Aussicht. Vor P4 ist der genaue Start-/Stop-/Restorepayload zu ergänzen und zu reviewen, einschließlich Quell-/Binaryhashes und erwarteter Ausgänge. Keine pauschale neue Softwareerlaubnis ist dafür erforderlich; die geschützte Umschaltung bleibt separat.
