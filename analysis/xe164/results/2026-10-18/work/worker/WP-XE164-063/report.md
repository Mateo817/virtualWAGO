> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-063 — Parallele Dienste und digitaler Zielpfad

## Ergebnis

**VERIFIZIERT, eng begrenzt:** Der native Digital-8-Erfolg erhielt die originale Runtime, den nativen I/O-Manager sowie originale IoDrvDal-/IoDrvKbus-Dateien. Er ersetzte nur den belegten ADI-Provider in einer isolierten Sicht; physische K-Bus-/UIO-/Mem-Endpunkte und Host-D-Bus waren verborgen. Die native Runtime konfigurierte und verarbeitete den ausgewählten Digitalpfad mit TCM=0, lief in der separaten IEC-Probe und erzeugte die erwarteten angeforderten Ausgangsframes. Das ist ein Beleg für diesen Aufbau, kein vollständiger Beleg jedes Dienstes, jedes dynamischen Zugriffs oder einer vollvirtuellen WAGO.

**Entscheidung:** Für diese begrenzte Zielkonfiguration authentische Board-/Runtimekomponenten und die originalen umgebenden Komponenten erhalten; keine Identitäts-/Signaturdaten oder Herstellerdienste nachbauen. Host-D-Bus, UIO und physischer Retain-SRAM-Zugriff waren in dem erfolgreichen isolierten Fall verborgen bzw. umgangen. Daraus folgt nur, dass sie für genau diesen Lauf keinen sichtbaren Blocker darstellten. Ein Ersatz dieser Dienste ist nicht durch die vorliegenden Belege qualifiziert. Für ein vollständig virtuelles Ziel bleiben deren Servicevertrag und gegebenenfalls eine zulässige Emulation **OFFEN**.

## Dienstgrenzen

Die Tabelle `service-boundary.tsv` enthält je beobachteter Grenze Consumer/Provider, Phase, Symptom, Erfolgsevidenz sowie Preserve/Emulate/Open-Empfehlung. In Kurzform:

- **Board MARKING/MAXTERM:** Originaler IoDrvKbus liest MARKING, verlangt PFC, liest anschließend MAXTERM und akzeptiert 1..250. Fehlendes/unpassendes MARKING führte zum Fehler „Number of supported modules out of limits“; die Initialisierung endete mit Fehler 33. Den echten Boardpfad erhalten. Der spätere Erfolg lief mit originalen Komponenten, aber die Erfolgsreceipts weisen die einzelnen Board-Leseaufrufe nicht separat aus.
- **SysTarget-Signatur:** Der originale Signaturpfad liest echte Boardfelder über dieselbe Bibliothek. Im fehlgeschlagenen Start wurde „SysTarget signature mismatch“ beobachtet. Der spätere Digital-8-Erfolg ist kein Einzelbeleg für die vollständige Signaturfunktion: das Init-Receipt nennt deren explizite Akzeptanz weiterhin **OFFEN**. Originalen Pfad erhalten; genaue dynamische Signaturausführung bleibt offen.
- **`libwago_dbus` / `wago.kbus`:** Die Bibliothek war im Prozess gemappt; ein passiver Getter wurde zuvor an den bestehenden eindeutigen Eigentümer gebunden und las Cachezustand. In der erfolgreichen isolierten Digitalprobe war Host-D-Bus verborgen. Das qualifiziert weder eine allgemeine D-Bus-Dienstemulation noch beweist es, dass jeder interne oder externe D-Bus-Pfad unnötig ist. Originale Bibliothek erhalten, keine D-Bus-Emulation für den begrenzten Digitalpfad belegt; externer Dienstbedarf bleibt offen.
- **`libdiagnostic` / Tsc-Diagnose:** `libdiagnostic` war gemappt; im fehlgeschlagenen Start traten zugleich TscLED-, TscRunLed-, TscChCfgOnline- und TscOms-Initialisierungsfehler auf. Eine kausale Zuordnung dieser Meldungen zu `libdiagnostic` ist nicht belegt. Der digitale Erfolg behielt die originale Komponentenbasis bei und bestand, isoliert aber nicht jeden Diagnosecall. Original erhalten, Details/Abhängigkeiten offen.
- **UIO, Retain/SRAM, Zeit und Serial:** Im Beobachtungslauf war `/dev/uio0` gemappt; K-Bus/UIO/Mem waren im erfolgreichen Digitalaufbau verborgen. Positiver simulierter Retain-Umfang vermied den statisch belegten physischen SRAM-Ereignispfad. `IoDrvSerial` war trotz K-Bus-Konfiguration gemappt; daraus folgt keine vollständige Begrenzung seiner Verbraucher. Taskperiode 20 ms bzw. eigene monotone Modelluhr qualifizieren keine allgemeine Originalzeit-/Watchdogsemantik. UIO-/Serial-Seitenpfade und vollständige Retain-/Zeitverträge bleiben daher **OFFEN**; nur der konkret konfigurierte Retain-Ersatz ist eine Modellannahme, keine authentische WAGO-Semantik.

## Beobachtungen und Grenzen

Die Realbeobachtung bindet den Prozess an `libIoDrvDal`, `libIoDrvKbus`, `libdal`, `libpackbus`, `libwago_dbus`, `libdiagnostic`, `/dev/kbus0`, `/dev/uio0`, zwei DAL- und zwei KBUS-Tasks, zwölf bekannte WagoAsync-Worker und einen Terminalregisterworker. Das sind Mapping-/Kontextbeobachtungen, kein Beleg erfolgreicher aktueller Buskommunikation, einer Callbackreihenfolge oder Thread-Sicherheit.

Der erste begrenzte Providerstart scheiterte in der Initialisierung (Fehler 33) mit den genannten Modulzahl-, Signatur- und Tsc-Meldungen. Die statische Analyse ordnet den Modulzahlpfad dem originalen IoDrvKbus zu. Der spätere Erfolg änderte unter anderem TCM auf den dokumentierten Wert 0 und erhielt Originalruntime, I/O-Manager und originale I/O-Treiber. Das native Init-Receipt meldet `opened=1/configured=1/fault=0`; der spätere native IEC-Lauf erreichte RUN und vollständige angeforderte Ausgangsframes bei geschlossenem Modellpermit. Wirksame Ausgänge blieben null. Ein expliziter voller SysTarget-Signatur-PASS ist ausdrücklich nicht vorhanden.

Die spätere Evidence zeigt den Erfolg bei versteckten physischen K-Bus-/UIO-/Mem-Endpunkten und verborgenem Host-D-Bus. Sie beweist nicht, dass beliebige dynamische Verbraucher, andere Konfigurationen oder Dienste auf einer vollständig virtuellen Runtime sicher entbehrlich sind. Auch folgt aus `IoDrvSerial`-Mapping keine serielle Nutzung im erfolgreichen Versuch. Keine Aussage wird auf andere Firmwarestände oder Boardidentitäten übertragen.

## Alternativerklärungen und Restunsicherheit

Die ursprünglichen Initialisierungsfehler können mehrere Ursachen gleichzeitig gehabt haben. Dass die TCM=0-Konfiguration später funktionierte, isoliert nicht, welche Board-/Signatur-/Tsc-Hilfswege im Erfolg tatsächlich aufgerufen wurden oder welche vorhandenen Dienste nötig waren. Verborgene Endpunkte schließen nur den Zugriff in der gebundenen isolierten Sicht aus; sie belegen keine vollständige statische Unerreichbarkeit. Der D-Bus-Getter ist ein passiver Cachelesepfad und kein Nachweis sämtlicher D-Bus-Methoden. Die erfolgte Zyklusprobe belegt angeforderte Prozessdaten im Digital-8-Profil, nicht echte Modulkommunikation, elektrische Äquivalenz, effektive Ausgangsfreigabe, allgemeine Fehlerreaktion oder Retain-Wiederherstellung.

## Statussprache, Tests und Werkzeug

Status verwendet **VERIFIZIERT | HYPOTHESE | OFFEN | BLOCKED**; Teststatus **PASS | FAIL | NOT_RUN | BLOCKED**. Die Statuswörter beziehen sich jeweils auf den genannten Scope und die gebundenen Revisionen/Hashes. Die Eingabeberichte nennen für ihre jeweiligen Läufe PASS und FAIL; dieses Work-Package führte keine Tests, Geräte-, Netzwerk- oder VM-Aktionen aus: **NOT_RUN**. Offline-Reconciliation und Worker-Self-Review: **PASS** für Eingabe-Fingerprintprüfung und Quellenabgleich, keine unabhängige Review.

Werkzeuge: GNU coreutils `sha256sum 9.7`; Python `3.13.5` für JSON-Lesen/-Formatierung. `jq` war nicht installiert. Keine Binäranalyse (REA nicht anwendbar), keine Repositoryänderung, keine API-/SFR-Erfindung.

## Worker-Self-Review

Ich habe geprüft, dass die sechs übergebenen Input-SHA-256-Werte mit den Dateien übereinstimmen; `inputs.tsv` hält diese Bindung fest. Die Unterscheidung zwischen original erhaltenem Umfeld und einzeln belegtem Dienstaufruf ist in Bericht und TSV explizit. Der Bericht behauptet keine vollständige ADI-Abdeckung, keinen vollständigen Signatur-PASS und keine neue Runtimeeigenschaft. **Self-Review**, kein unabhängiges Review.

## Erzeugte Dateien

- `report.md`
- `service-boundary.tsv`
- `inputs.tsv`
- `sha256sums.txt` (Hashes der drei Inhaltsdateien; nicht selbstreferenziert)
