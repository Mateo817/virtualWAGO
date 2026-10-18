> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-066 — Source-seitiger Audit der Modellbrücke

## Ergebnis

**VERIFIZIERT (statische Quellprüfung):** Die Bridge exponiert ausschließlich die unten aufgeführten fünf Paketformen: vier Kommandotypen, wobei `PERMIT` zwei feste Varianten hat, und `STATUS`. Es gibt keinen Befehl zum Schreiben von Ausgangsbits. Die Bridge setzt Eingabesignale, setzt beziehungsweise löscht Permit, kann einen Modellfehler verriegeln und liest einen Snapshot; die SPS-/ADI-Ausgangsschreibpfade werden nicht vom Bridge-Parser aufgerufen.

**VERIFIZIERT mit Einschränkung:** Bei gewöhnlichem Client-Disconnect, 500-ms-Leerlauf-Timeout, zu großem Paket, ungültigem/unerkanntem Befehl und beim Stop mit einer gerade bearbeiteten Verbindung wird die Verbindung abgebaut; der Worker ruft dann `virtual_adi_set_permit(false)` auf. Der Adapter setzt dabei unter `state_mutex` Permit auf false und löscht den wirksamen Ausgang, sofern die Modellinstanz initialisiert ist. Die Parserablehnung selbst führt diesen Widerruf nicht aus: ein ungültiger Befehl erhält zuerst `ERR COMMAND`; erst anschließender Verbindungsteardown widerruft Permit.

**OFFEN / begrenzt:** `virtual_model_bridge_stop()` widerruft Permit nicht bedingungslos. Der Worker widerruft bei normalem Stop nur dann über `disconnect_client`, wenn gerade ein Client-FD aktiv ist. Beim Stop im Listen-/Leerlaufpfad gibt es keinen allgemeinen Permit-Aufruf. Normalerweise hat ein vorheriger Client-Teardown Permit bereits gelöscht; dennoch ist ein bedingungsloser Stop-Widerruf source-seitig nicht garantiert, falls Permit über den eigenen Adapter-Setter gesetzt wurde, während keine Clientverbindung offen war. Auch bei einem im Adapter gelatchten, tatsächlich abgelaufenen Watchdog bleibt das gespeicherte Permit-Bit true; `effective_outputs` wird auf null gesetzt. Das sind getrennte Zustände.

`virtual_adi_set_inputs` und `virtual_adi_set_permit` können nach einem vorangehenden Snapshot auf Fehler laufen, wenn sich der Modell-Lifecycle dazwischen ändert. In diesem Fall antwortet der Parser `ERR STATE`, hält die Verbindung aber offen (`close_after` bleibt false); ein solcher Setterfehler allein widerruft Permit nicht. Die einzelnen Adapteraufrufe nehmen jeweils den State-Lock, aber Snapshot, Setter und Senden bilden keine gemeinsame atomare Transaktion.

## Umfang und Beleglage

Nur die fünf im Auftrag genannten Dateien wurden gelesen; ihre Bytes und SHA-256 stimmen mit den übergebenen Werten überein (siehe `inputs.tsv`). Prüfung statischer Quelltext und Aufrufpfade, insbesondere `adi_model_bridge.c:275-374,376-399,401-495,497-564` sowie `adi_digital_adapter.c:128-158,175-198,234-250,289-323`. Keine Socket-, Prozess-, Netzwerk-, Geräte-, VM- oder Runtime-Ausführung. Keine Hersteller-ABI-Aussage. `adi_model_client.c` ist nur als eigener Client mitgelesen; er ist kein zusätzlicher Serververtrag und kein Laufzeitnachweis.

## Endpunkt, Berechtigungen und Transport

- Der Endpunkt wird nur gestartet, wenn `VIRTUALWAGO_MODEL_SOCKET` gesetzt ist. Nicht gesetzt: `virtual_model_bridge_start()` liefert Erfolg und startet keinen Worker (`adi_model_bridge.c:497-513`). Leer oder ungeeignet: Startfehler.
- Der Pfad muss absolut, mindestens zwei Zeichen lang, ohne abschließenden Slash und kürzer als `sun_path` sein. Pfadkomponenten des Elternpfads werden mit `openat(... O_DIRECTORY | O_NOFOLLOW)` geöffnet; leere Komponenten sowie `.` und `..` werden abgewiesen (`:75-137`). Das letzte Elternverzeichnis muss dem effektiven UID gehören, Modus `0700` haben und mit dem geöffneten Verzeichnis inode-/device-identisch sein (`:129-136`).
- Ein vorhandener Socketname wird niemals ersetzt oder entfernt (`:181-184`). Server: `AF_UNIX`, `SOCK_SEQPACKET`, nonblocking, close-on-exec; gebundener Socket muss euid gehören, wird auf `0600` gesetzt und per device/inode erneut geprüft; Listen-Backlog ist 1 (`:186-222`). Beim Entfernen wird nur der zuvor identifizierte Socket-Inode gelöscht (`:139-165`).
- Jeder akzeptierte Peer muss bei `SO_PEERCRED` exakt dieselbe effektive UID wie der Serverprozess haben (`:382-399`). Das beschränkt nicht andere Prozesse derselben UID; dieser Vorbehalt steht auch im Quellkommentar (`:386-388`). Ein Peer mit falscher UID wird geschlossen, ohne den normalen `disconnect_client`-Pfad aufzurufen.
- Die Sitzung wird nach 500 ms ohne empfangenes Paket beendet; Poll-Schritte sind höchstens 50 ms (`:34-35,401-423`). Die Antwortsendung wartet höchstens 100 ms (`:257-273`). Beides verwendet monotone Zeit. Ein vollständiger Serverantwortdatensatz muss in einem `SOCK_SEQPACKET`-Send passen (`:257-273`).

## Akzeptierte Paketgrammatik

Ein Paket ist ein einzelner `SOCK_SEQPACKET`-Datensatz. Die Grammatik wird bytegenau geprüft, ohne Zeilenende oder NUL-Abschluss im Paket. Leerzeichen sind Teil der exakten Schlüsselwörter; Zusätze, CR/LF oder sonstige Bytes passen nicht. `INPUT` akzeptiert ausschließlich ASCII-Dezimalziffern ohne führende Null (außer dem Einzelwert `0`), maximal fünf Stellen und Werte 0 bis 65535 (`adi_model_bridge.c:275-291`). Der Adapter maskiert die gesetzten Eingänge danach zusätzlich mit dem Profil-Eingabemaskenwert (`adi_digital_adapter.c:234-239`).

| Paket | Wirkung | Antwort bei Erfolg |
|---|---|---|
| exakt `STATUS` | Snapshot lesen | `STATUS input=N permit=0|1 requested=N effective=N watchdog=0|1 fault=0|1 generation=N frames=N opened=0|1 configured=0|1 running=0|1` |
| `INPUT ` gefolgt von kanonischer Dezimalzahl `0`…`65535` | eigene Modelleingänge setzen | `OK INPUT` |
| exakt `PERMIT 0` | Permit false; wirksame Ausgänge werden vom Adapter neu bewertet und bei fehlendem effektivem Permit auf 0 gesetzt | `OK PERMIT` |
| exakt `PERMIT 1` | Permit true anfordern; wirksame Ausgänge bleiben ohne alle Adapterfreigabebedingungen 0 | `OK PERMIT` |
| exakt `FAULT` | Modellfehler latchen; wirksame Ausgänge nullen | `OK FAULT LATCHED` |

`STATUS` enthält ausschließlich die oben gelisteten Felder in dieser Reihenfolge. `requested` und `effective` werden getrennt ausgegeben. Der Snapshot refreshed zuvor den Watchdog und kopiert Werte unter Adapter-State-Lock (`adi_digital_adapter.c:175-189`). Der Parser enthält keinen Aufruf eines Ausgangs-Setters; Ausgangsschreibungen erfolgen in anderen Adapterpfaden, nicht über diese Control Plane (`adi_model_bridge.c:312-374`; Vergleich `adi_digital_adapter.c:456-554`).

## Ablehnung und Fehlerantworten

- Paket über 64 Bytes beziehungsweise `MSG_TRUNC`: wenn möglich `ERR TOO_LONG`, danach Client-Teardown und Permit-Widerruf. Empfangslänge 0 (EOF) oder negativer Empfang: kein Protokollfehlerdatensatz, sofortiger Teardown (`adi_model_bridge.c:424-447`).
- Unbekannter oder syntaktisch falscher Befehl bei initialisiertem Modell: `ERR COMMAND`, `close_after=true`; Antwort wird zuerst gesendet, danach endet `handle_client`, Worker ruft `disconnect_client` (`:312-374,442-447,481-487`). Das umfasst etwa führende Nullen, Out-of-range-Werte, falsche Groß-/Kleinschreibung, angehängte Newlines und falsche `PERMIT`-Syntax.
- Vor jeglicher nicht-`STATUS`-Parserprüfung wird ein Snapshot angefordert. Snapshotfehler liefert `ERR STATE`; nicht initialisiertes Modell liefert `NOT_READY`. Beide Antworten lassen die Verbindung offen (`:328-336`). `STATUS` hat denselben Fehler-/Not-ready-Fall (`:315-326`).
- Setter- oder Fault-Latch-Fehler liefert `ERR STATE` und lässt die Verbindung offen (`:338-369`). Damit ist die Ablehnung nicht allgemein ein Disconnect-Signal. Der normale Ablauf kann die Setterfehler vermeiden, aber Lifecycle-Wechsel zwischen Snapshot und Setter sind nicht ausgeschlossen.
- Kann die Antwort nicht gesendet werden, scheitert `process_packet`, endet wegen Stop, schlägt monotone Zeit fehl oder meldet Poll/Socket Fehler/Hangup, wird der Clientpfad verlassen und `disconnect_client` ausgeführt (`:230-273,401-452`). Ist die Antwort wegen geschlossenem Peer nicht zustellbar, geschieht der Teardown ebenfalls.
- Nicht erlaubte UID: FD wird direkt geschlossen und die Accept-Schleife fortgesetzt (`:389-398,481-484`); dieser Ablehnungszweig setzt Permit nicht selbst zurück.

## Cleanup, Permit und wirksame Ausgänge

`disconnect_client()` schließt zuerst den FD und ruft danach `virtual_adi_set_permit(false)`; der Rückgabewert wird ignoriert (`adi_model_bridge.c:376-380`). Er wird nach jedem beendeten aktiven Client aufgerufen, einschließlich EOF, Idle-Timeout, Protokollablehnung, Antwortsendefehler und Stop-Wakeup (`:401-452,481-489`). Bei fatalem Listener-Pollfehler setzt der Worker Permit zusätzlich zurück und markiert `bridge_worker_failed` (`:468-493`).

Im Adapter prüft der Setter unter `state_mutex` auf initialisierten Zustand. Bei Erfolg setzt er `state.permit=false`; `effective_permit()` verlangt zusätzlich laufende Anwendung, gesunden Watchdog und keinen gelatchten Fehler, sodass das wirksame Bitfeld auf 0 geht, sobald eine Bedingung falsch ist (`adi_digital_adapter.c:150-153,242-250`). Die Sperre gilt jeweils nur während dieses Setteraufrufs. `requested_outputs` bleibt beim Permit-Widerruf erhalten (`:242-250`), es wird also der wirksame Ausgang gelöscht, nicht notwendigerweise die zuletzt angeforderte SPS-Ausgabe.

Timeouts sind zweierlei:

1. **Bridge-Client-Leerlauf (500 ms):** Teardown → `set_permit(false)` → bei erfolgreichem Adapteraufruf Permit false und effektive Ausgabe 0.
2. **Modell-Watchdog-Deadline:** Snapshot/andere Adapteroperation ruft `refresh_watchdog_locked()` auf. Bei Ablauf werden `watchdog_healthy=false` und `effective_outputs=0` gesetzt; `permit` wird dabei nicht zurückgesetzt (`adi_digital_adapter.c:128-135`). Ein Fehler-/Leerlaufpfad der Bridge kann danach zusätzlich Permit widerrufen, der reine Watchdogablauf nicht.

Beim `virtual_model_bridge_stop()` wird Stop atomar angefordert und die Wake-Pipe signalisiert, danach wird der Worker gejoint und bei Join-Erfolg der Endpunkt geschlossen (`adi_model_bridge.c:533-560`). Ist währenddessen ein Client aktiv, kehrt dessen Handler wegen Wake/Stop zurück und der Worker nimmt den Disconnect-Pfad. Ist kein Client-FD aktiv, ruft der Worker am normalen Loop-Ende nicht allgemein `virtual_adi_set_permit(false)` auf; nur der fatale Pollpfad tut das (`:455-495`). Adapter-`Exit` löscht den gesamten Adapter-State vor seinem Bridge-Stop und räumt so in diesem Lifecycle-Pfad Permit/Ausgänge auf (`adi_digital_adapter.c:307-322`); daraus folgt keine allgemeine Garantie des Bridge-Stop-Einstiegs, etwa beim Destructor.

## Alternative Erklärung und Restunsicherheit

Eine mögliche Lesart ist, dass jeder Fehler bereits die Safety-Reaktion auslöst. Der Quellpfad zeigt eine engere Aussage: Nur Fehler, die zur Verbindungsschließung führen, erreichen `disconnect_client`; `ERR STATE` nach Snapshot-/Setterfehler hält die Sitzung offen. Der ungültige Befehl selbst setzt Permit nicht zurück, obwohl der darauffolgende Teardown es tut. Weiterhin ist ein Listener-Fatal explizit behandelt, ein gewöhnlicher Stop ohne Client dagegen nicht mit einem eigenen Widerruf.

Dies ist eine Source-only Aussage über die benannten Modellfunktionen. Nicht belegt sind Laufzeitverhalten des Betriebssystems, tatsächliche Socket-Permissions nach Deployment, zeitliche Obergrenzen unter Schedulinglast, Nebenläufigkeitsverhalten außerhalb der sichtbaren Mutexes oder Verhalten anderer Buildvarianten. Die Bridge ist laut Makro nur aktiv, wenn `VIRTUALWAGO_ENABLE_MODEL_BRIDGE` definiert ist; ohne Makro sind Start/Stop inert (`adi_model_bridge.c:5-6,566-570`). Kein Nachweis für eine physische Anlage, Runtime, Hersteller-API oder Hardwarewirkung.

## Status, Werkzeuge und Prüfung

- Aussage-Status: `VERIFIZIERT` für sichtbare Grammatik, direkte Aufrufpfade und Adapter-Lock/State-Übergänge; `OFFEN` für Laufzeit-/Deploymenteffekte sowie den allgemeinen Stop-Aufruf ohne aktiven Client; keine `HYPOTHESE` als beobachtete Tatsache ausgegeben.
- Tests: `NOT_RUN` — ausdrücklich keine Tests, Builds, Client- oder Serverausführung.
- Worker-Self-Review: die fünf Quellhashes gegen Auftrag geprüft; Befehlsliste mit Parserzweigen abgeglichen; alle `handle_client`-Rückkehrpfade sowie Worker-Fatal-/Stop-Enden nachverfolgt. Dies ist kein unabhängiger Review.
- Werkzeuge für diese statische Prüfung: Debian `cc` 14.2.0, GNU coreutils `sha256sum` 9.7, ripgrep 15.2.0, Git 2.47.3. Compiler und Git dienten nur der Versionsabfrage; es wurde kein Build oder Git-Schreibvorgang ausgeführt.
- Generierte Dateien und SHA-256: siehe `sha256sums.txt`.
