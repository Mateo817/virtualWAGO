# PWM: synthetische UID-Antworten, 19. Oktober 2026

**VERIFIZIERT:** Zwei unterschiedliche synthetische UID-Werte (`750677` und
`60500768`, jeweils dezimal) mit Erfolgsstatus erreichen im gebundenen
750-677-Projekt denselben nächsten Dispatch `libpackbus_async_com_open`.
Die originale Runtime erreicht in beiden Versuchen RUN. **OFFEN:** Daraus
folgt keine allgemeine Aussage, dass die UID nie geprüft oder verwendet wird.
Ein exakter Vergleich mit einer einzigen festen erwarteten Zahl als zwingende
Bedingung vor diesem Dispatch erklärt die beiden Beobachtungen nicht.
Maskierte Prüfungen, Wertebereiche und spätere Verwendung bleiben möglich.

## Aufbau und tatsächliche Ergebnisse

Basis ist Commit `78d73a2d37102d244ac1802d8b71083c2a9dcdd1` mit unveränderter
PWM-APP, Gerätebeschreibung 2.0.0.3 und Modulbibliothek 1.0.0.3. Die Originalruntime,
der I/O-Manager und die Originaltreiber bleiben erhalten. Die private
Adaptervariante ersetzt ausschließlich die Antwort von GET_UID für PWM-Slot 1:
UDINT-Wert schreiben, inneren Status 0 zurückgeben, keinen UID-Fehler setzen.
Alle anderen Fehlerpfade bleiben unverändert. Modellpermit und wirksame
Ausgänge bleiben 0; kein elektrischer PWM-Test und keine VM-Änderung.

Der Eigentümer hat beide Zahlen ausdrücklich als synthetische Testwerte
freigegeben. `750677` bildet die Artikelnummer ohne Bindestrich ab;
`60500768` ist die auf dem Verpackungsfoto sichtbare ID. Beide sind **keine
belegten echten Modul-UIDs**. Die normale Repository-Implementierung wurde
nicht auf diese Werte umgestellt.

| Prüfung | UID 750677 | UID 60500768 |
|---|---|---|
| Lokaler 32-Bit-Puffer-/Canary-/ungültiger-Slot-Test | PASS | PASS |
| ARM-Shared-Library-Build | PASS | PASS |
| Praktische Ziel-/Prozessisolation | PASS | PASS |
| Antwort mit exaktem Wert, outer 0 / inner 0 im Trace | PASS | PASS |
| Originalruntime RUN | PASS | PASS |
| Folgender Dispatch `libpackbus_async_com_open` | VERIFIZIERT | VERIFIZIERT |
| Vollständige Prozessdatenabnahme | BLOCKED, 0 Muster | BLOCKED, 0 Muster |
| Automatische Rücknahme | PASS | FAIL; kontrollierte Wiederherstellung PASS |
| Abschließend originaler STOP und sieben unveränderte Dateien | PASS | PASS |

Der eigene Provider unterstützt Async-Open noch nicht: outer 1, inneres
Ergebnis unbeschrieben. Dabei entsteht erneut der eigene Modellfehler;
der Frameprüfer stoppt vor dem ersten Eingangsmuster. Zyklische Lese-/
Schreibaufrufe sind beobachtet, aber kein vollständiger PWM-Datenweg abgenommen.
Die ursprüngliche Open-Implementierung wurde in diesen Versuchen nicht ausgeführt.

Der historische Lauf mit innerem GET_UID-Status -1 erreichte ebenfalls RUN,
aber nicht den jetzt beobachteten Open-Dispatch. Dieser Vergleich ändert sowohl
Antwortstatus als auch den eigenen UID-Fehlerzustand. Er isoliert daher nicht
vollständig, welcher der beiden Faktoren den veränderten Ablauf verursacht.

Beim zweiten Versuch endete die automatische Rücknahme mit Exit 4 vor dem
Originalneustart. Eine frische Prüfung fand keine Runtime und keine eigenen
aktiven Helfer; die Originaldateien waren unverändert. Nach dieser Prüfung
wurde die originale Runtime kontrolliert mit vorübergehendem Start=0 neu
begonnen, STOP bestätigt und die Konfiguration bytegleich zurückgesetzt.
Der genaue auslösende Rücknahmerennfall bleibt OFFEN. Die abschließende Prüfung
bestätigt einen originalen STOP-Prozess, sieben unveränderte Dateien, keine
eigenen aktiven Helfer/privaten D-Bus-Prozesse und CAN STOPPED. Das anfängliche
Rücknahme-FAIL wird durch die erfolgreiche Wiederherstellung nicht umetikettiert.

## Getrennte statische Untersuchung des Originalcodes

Die hashgebundenen FW31-Binaries ergeben folgende begrenzte Aussagen:

- `fugetunifiedid` in `libCmpKbusAsyncCom` übersetzt äußeren und inneren
  GET_UID-Rückgabestatus. In diesem Wrapper gibt es keinen Zahlenvergleich
  des UID-Ausgabewerts mit einer erwarteten Modulkennung.
- `fuopenchannel` prüft keinen eingehenden Handlewert gegen eine UID. Es
  übergibt eine lokale Handlezelle und prüft nach dem Aufruf den äußeren
  DAL-Status sowie einen nichtnulligen Ausgabehandle.
- `eAsyncCom_Open` im originalen `libpackbus` liest den vorherigen Inhalt
  dieser Zelle nicht. Nach seinen Ressourcen-/Zustandsprüfungen schreibt es
  einen neuen Handle hinein. Das ist keine Prüfung einer eingehenden UID.

Die Aufrufimplementierung der kompilierten 750-677-Modulbibliothek wurde
nicht ausgewertet. Die beiden Runtime-Traces enthalten weder ihre genaue
Aufrufadresse noch den an Open übergebenen Argumentwert. Es wird deshalb
**nicht** behauptet, dass UID und Handle dieselbe Variable sind oder dass der
Modulbaustein keine weiteren Vergleiche enthält. Der separat bekannte
GET_UID-Vergleich in `libIoDrvKbus` ist nicht an diesen beobachteten Aufrufpfad
gebunden und darf ebenfalls nicht unbesehen übertragen werden.

## Reproduzierbarkeit und Nachweisgrenzen

[Sanitisierte Evidence](../evidence/pwm-synthetic-uid-2026-10-19.json) bindet
Basisrevision, APP, Provider, eigene Quellen, Originalbinaries und private
Messprotokolle über SHA-256. Der [experimentelle Patch](../evidence/pwm-synthetic-uid-2026-10-19.patch)
ist ausschließlich ein reproduzierbares Experimentartefakt; er ist nicht
auf den normalen Adapter angewendet. `git apply --check` auf der Basisquelle
ist PASS. Beim Kompilieren ist jeweils `-DSYNTHETIC_TEST_UID=750677u` oder
`-DSYNTHETIC_TEST_UID=60500768u` erforderlich. Die restlichen Providerflags
entsprechen dem gebundenen PWM-Build; private Originalheader bleiben lokal.
Der [eigene Puffertest](../evidence/pwm-synthetic-uid-buffer-test.c) prüft den
vollen UDINT und unveränderte angrenzende Wächterwerte sowie die Ablehnung von
Slot 0. Diese Tests belegen den Eigenprovider, keine Herstellersemantik.

Die native Ausführung bleibt außerhalb von CI. Kein vollständiger Original-
Moduldiagnosestatus wurde ausgelesen; RUN ist keine Fehlerfreiheitsbescheinigung.
Weitere Zahlenwerte, ein vollständiger Async-Kanal, Parametrierung und reale
PWM-Wirkung wurden nicht getestet. Statische Aussagen sind getrennt von den
Runtime-Beobachtungen dokumentiert. Root-Prüfung als Self-Review; separate
Agentenanalyse des Originalcodes, kein behaupteter unabhängiger Code-Review.
