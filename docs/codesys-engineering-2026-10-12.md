# CODESYS-Engineering-Baseline, 12.10.2026

Dieser Nachweis ergänzt das frühere Device-Description-Inventar. Er bindet einen eigenen nativen CODESYS-Projekt-Build an das installierte Engineeringprofil 3.5.21.50 (SP21 Patch 5). Er trennt den Offline-Build vom anschließend tatsächlich ausgeführten internen IEC-Test auf dem Referenzgerät. Die Akzeptanz virtueller Klemmen durch originale I/O-Komponenten oder Runtime ist damit noch nicht belegt.

## Tatsächlicher Offline-Build

**VERIFIZIERT / PASS, enger Scope:** Ein eigenes neues CODESYS-Projekt wurde mit der installierten IDE 3.5.21.50 erzeugt und offline kompiliert. Das Projekt verwendet die zuvor inventarisierten Beschreibungen für PFC200 750-8213 (Version 6.4.6.11), LocalBus (2.1.0.1) und die Terminals 750-1405/750-1504 (je 2.0.0.14). `PLC_PRG` stammt unverändert aus [`prototype/iec/minimal_io.st`](../prototype/iec/minimal_io.st), SHA-256 `e757410d9d9efc4f363e666190514af130d2a6be9fd46916a805cd7551588dcc`.

Der Build-Lauf meldete vor dem Build, nach Rebuild und nach Codegenerierung jeweils null Fehler und null Warnungen. Die IDE meldete `Compile complete -- 0 errors, 0 warnings` und `Build complete -- 0 errors, 0 warnings`. Das ist ein **PASS für Syntax, Typisierung und Codegenerierung in diesem Engineeringstand**. Der Build endete mit „Ready for download“; ein Download fand nicht statt.

Das private Manifest bindet die erzeugten Artefakte, ohne die Projektdatei zu veröffentlichen: `minimal-io-offline-v4.project` SHA-256 `2ef9f384771cb056ec5b1c5ffd330abb105bc80d1225052d3a84609b9467e3dd`; erzeugtes `minimal-io.app` SHA-256 `937218e493d92b2c2d86c300aaa2935304d1115b3af7805ce0c34b0c2b594b53`; Mapping-CSV SHA-256 `cde0bc87c239e8281fc16fc0f800a37eb3a424f523a53a67785d0903ae45f9f0`. Rohprojekt, Laufprotokolle und Laufmanifeste bleiben privat.

Die Variablen `InputWord`, `OutputWord`, `OutputPermit` und `CycleCounter` sind interne Kandidatensignale. Es wurde keine physische Prozessabbildadresse belegt. Die Mapping-CSV und der erfolgreiche Build belegen daher weder tatsächliche Slot-/Scanreihenfolge noch eine reale Klemmenpräsenz, einen Eingangswechsel oder eine Ausgangswirkung.

## Ausführbarer eigener Offline-Builder

[`tools/codesys_offline_candidate.py`](../tools/codesys_offline_candidate.py), SHA-256 `d0302ccc25bffb33161663b49f5fdcf5a61160a49a3909795222789f7e145a32`, enthält ausschließlich eigenen Projekt-/Build-/Exportcode und den unveränderten ST-Quelltext. Er wird über `--runscript` in der installierten CODESYS-ScriptEngine ausgeführt, nicht mit gewöhnlichem Python. Ein neues eigenes Skriptverzeichnis ist erforderlich; bei vorhandenen Projekt-, APP-, CRC- oder Mappingausgaben bricht er vor der Projekterzeugung ab. Es gibt keine Online-, Gateway-, Scan-, Download- oder Startaufrufe.

**PASS:** Genau dieser öffentliche Quelltext wurde unter der inventarisierten IDE in einem frischen eigenen Verzeichnis tatsächlich ausgeführt. Diagnostik: null Fehler und null Warnungen. Sein Bericht hat SHA-256 `158b91af81818d14f9c76184ea79a11374afa56c8e53debec5df543e8f9d09e9`; das erzeugte Projekt `3d9e1dc9d2ba6ebce51ff60a3c721697c0fd339bff9fdf08d62a6cdcc3976f63`, die Offline-APP `ba26ae656a6ac8331ec898ec4ecc7d185f690a4fc4e1ee9b12ead96de8dc0e7e`. Die Mapping-CSV ist bytegleich zur ersten Baseline. Diese private Offlineausgabe wurde nicht auf das Referenzgerät geladen; dessen separat benannte Variante besitzt einen deaktivierten I/O-Zweig.

Die tatsächlich verwendete IDE-Datei hat SHA-256 `0f483fae5ac32e25207c38b9afdf08aa12680c5959fc692062f27db050f310b2`, das über die bestehende AdditionalFolders-Auswahl geladene Profil `fb09099380f40dc0270e35a7555c50b9b271a2e977a03675aed812c09b33ca1b`. Das früher inventarisierte gleichnamige Profil aus einem anderen Profilverzeichnis ist damit nicht automatisch dieselbe Datei. Die normale IDE wurde nach ausdrücklicher Änderung des lokalen Arbeitsauftrags verwendet. Der historische AppContainer-FAIL wurde nicht repariert oder in PASS umgedeutet.

## Begrenzter Keep-Login

**VERIFIZIERT, read-only Aktionsumfang:** Ein separater, projektgebundener Keep-Login auf die Referenz wurde protokolliert. Der gelesene Anwendungszustand war STOP / Programm geladen. Der Lauf führte kein Löschen fremder Anwendungen, kein Update, keinen Download und keinen Runtime-Start aus. Dies ist kein Runtime- oder I/O-Test und ändert nicht den Compile-Nachweis. Zielidentität, Gateway und Zugangsdaten verbleiben im privaten Inventar.

## Rename-Prompt: konkreter Offlinefall

Beim Rename eines Anwendungsobjekts in einer **eigenen Offlinekopie** erschien `PromptRenameApplication` mit den Optionen Yes/No und Default No. Der Dialog warnt, dass eine Umbenennung Online-Change verhindert. Das ist ein eigener Offline-Projektvorgang; die Online-Verbindung oder ein geladenes Zielprogramm werden dafür nicht benötigt.

**PASS, eigener Offlineprojekt-Rename:** Der konkrete Prompt-Key `PromptRenameApplication` wurde mit den Optionen Yes/No und Default No aufgezeichnet. Ein eigener neuer Offlineprojekt-Rename wurde anschließend mit genau `system.prompt_answers["PromptRenameApplication"] = PromptResult.Yes` bestätigt; der Eintrag wurde direkt danach entfernt. Der Lauf endete mit IDE-Exitcode 0 und null Buildfehlern/-warnungen. Das belegt ausschließlich diesen Rename in der eigenen Offlinekopie. Andere Prompt-Keys blieben unbeantwortet; es gab keinen globalen Auto-Accept. Diese Antwort wurde nicht auf verbundene Projekte, Zieloperationen, Download oder Start übertragen. Ein Rename ist für den Build nicht erforderlich.

Eine separate Offlinekontrolle mit geschlossenem stdin ließ Yes/No- und Yes/No/Cancel-Prompts unbeantwortet und erhielt wie erwartet `IOError`. Damit ist für diesen Kontrolllauf kein stiller positiver Prompt-Fallback belegt. [CODESYS Prompt-Handling](https://content.helpme-codesys.com/en/CODESYS%20Scripting/_script_message_handling_with_scripting.html), [CODESYS ScriptSystem API](https://content.helpme-codesys.com/en/ScriptingEngine/ScriptSystem.html), [CODESYS-Beispiel für gezielte Antworten](https://forge.codesys.com/tol/scripting/snippets/17/).

## Originalruntime-Baseline

**PASS, begrenzte Runtimebaseline auf dem Referenzgerät:** Eine eindeutige eigene Anwendung `VirtualWAGO_Research` wurde projektgebunden mit `login_option=Never` und `delete_foreign_apps=False` behandelt. Sie meldete zunächst STOP; nach dem expliziten Start wechselte sie zu RUN. Zwei gelesene Samples zeigten `CycleCounter` von `UDINT#30` auf `UDINT#92`; `InputWord` und `OutputWord` blieben `WORD#0`, `OutputPermit` blieb `FALSE`. Alle drei Geräteknoten des eigenen I/O-Zweigs waren deaktiviert: Kbus sowie je ein DI- und DO-Terminal. Der unveränderte Quelltext hat weiterhin SHA-256 `e757410d9d9efc4f363e666190514af130d2a6be9fd46916a805cd7551588dcc`.

Danach wurde ausschließlich die eigene Anwendung gestoppt. Das Zurücksetzen auf Originalzustand wurde mit `False` angefordert; der zurückgemeldete Zustand und die Operation waren `none`. Es gab keinen zweiten Runtime-/K-Bus-Master, keinen Gerätereinitialisierungs- oder Runtime-Restart, keinen expliziten Online-Boot und keine I/O-Aktivierung. Der Ablauf belegt Codeausführung in der vorhandenen Originalruntime für diese eigene interne Testanwendung; er belegt weder geladene Binäridentität zwischen Offline-`.app` und Downloadbytes noch Original-WAGO-I/O-Akzeptanz.

Der tatsächliche Lauf ist an die private Ergebnisdatei `engineering-reference-baseline.output.private.bin` (SHA-256 `372b4d92aa028401fb15a7a8814491b585a51688477becfcfe525864d94cd74e`) und den Quellskript-Hash `b6172b961e3fad6792f8d8546fe18da7bb10029be9e9ba7b1e31e6135f4da05f` gebunden. Der unabhängige Sol-Review prüfte das konkrete Skript vor dem Schreibversuch; zwei Reviewbefunde wurden eingearbeitet. Rohprotokoll, Zielinformationen und Payload bleiben privat.

Die getrennte reine Offlinebaseline wurde mit Projekt-SHA-256 `b04a2f0b8cf941c62a9d8a290e4906cedc12224aa55afc94bf00da29c67038ba` und erzeugter Offline-`.app`-Datei SHA-256 `4830eebd3cc8b02b69cc812f9fb29c1757bda096b00011eab3d120a53b613dc3` manifestiert. Der nachfolgende Online-Login löste nach der Ziel-/Gateway-Einstellung einen erneuten Codegenerierungslauf mit null Fehlern und Warnungen aus. Die `.app`-Hash bindet nur die lokale Offline-Datei; sie ist kein Hash der tatsächlich heruntergeladenen Bytes.

Die zuvor beobachtete Keep-Prüfung einer vorhandenen Anwendung ist kein Ersatz für die eigene Runtimebaseline. **PASS:** Die erneute Keep-Verifikation der vorhandenen Altanwendung nach dieser Baseline meldete weiterhin STOP / Programm geladen. Der Nachlauf besitzt Bericht-SHA-256 `27a99314def9ace279044686a7020f003f320c55990c714319b742c99cc859b9`. Die anschließende strikte SSH-Kontrolle bestätigte denselben Runtimeprozess und unveränderte Hashes von Runtime, DAL, IoDrvDal, IoDrvKbus sowie Runtime-/IoDrv-Konfiguration. Sie besitzt Bericht-SHA-256 `39ef68a0a6b292e9b0fafceed95c359abe77be7e9cbdfe654dec8d53c6676098`. Der bereits zuvor gelöschte Runtime-Arbeitsordner bleibt unverändert; ein Runtime-Neustart und Wiederanlauf wurden nicht geprüft.

## Statusmatrix

| Nachweis | Status | Aussagegrenze |
|---|---|---|
| Nativer Offline-Build `minimal-io-offline-v4` | **PASS** | IDE 3.5.21.50; 0 Fehler/0 Warnungen; keine Zielausführung |
| Offline-Rename des eigenen Projekts mit einer gezielten Antwort | **PASS** | Nur `PromptRenameApplication=Yes`; Key direkt entfernt |
| Unbeantwortete Offline-Promptkontrolle | **PASS** | Geschlossenes stdin lieferte erwartetes `IOError`; keine globale Annahme |
| Eigene interne Anwendung auf Originalruntime | **PASS** | Ein App-Start/Stop; Kbus und DI/DO deaktiviert; nur interner Zähler beobachtet |
| Keep-Verifikation der vorhandenen Altanwendung nach dem Runtime-Lauf | **PASS** | Weiterhin STOP / Programm geladen; kein Update oder Download |
| Originaler I/O-Verbraucher mit Init/Enumeration und DI/DO | **NOT_RUN** | M3-Abnahmekriterien nicht erfüllt |
| Virtuelle/isolierte Originalruntime | **NOT_RUN** | Keine virtuelle Runtime gestartet oder qualifiziert |
| Unveränderte gemappte IEC-Anwendung im M4-Scope | **NOT_RUN** | Kein M4-I/O-Mapping-/Wiederanlaufnachweis |

## M3-Status und nächste Grenze

**M3: NOT_RUN. M4: NOT_RUN. Virtuelle Originalruntime: NOT_RUN.** Der M3-Abnahmepunkt verlangt einen originalen Verbraucher unter der belegten I/O-Grenze, Initialisierung, Geräteerkennung, zyklische DI/DO-Übernahme und eine negative Kontrolle. Ein eigener ST-Kandidat, sein erfolgreicher Build und die begrenzte Ausführung in der bestehenden Originalruntime erfüllen diese Kriterien nicht. Es wurde kein originaler `IoDrv`-Verbraucher an ein virtuelles Backend angebunden oder gegen dieses ausgeführt. M4 verlangt eine unverändert gemappte IEC-Anwendung mit Runtime-Verhaltens-/Wiederanlaufnachweis; das wurde ebenfalls nicht geprüft.

Der Engineering-Baseline-Build ist ein tatsächlicher Vorbereitungsschritt für M3. Offen bleiben insbesondere die passenden CmpIoDrvItf-/IoConfigConnectorMap- und Plattformheader sowie Komponentenregistrierung, Mapping und Lifecycle-Verträge, wie in [codesys-contract-2026-10-11.md](codesys-contract-2026-10-11.md) festgehalten. B+C bleibt eine **HYPOTHESE**.

## Nachweisbindung

IDE/Profileinordnung: CODESYS 3.5.21.50, SP21 Patch 5. Die Build- und Keep-Läufe besitzen getrennte Skript-/Profilhashes im privaten Evidence-Verzeichnis. Dieser öffentliche Bericht veröffentlicht keine Zieladresse, Gateway-/Benutzerdaten, Rohprojekte, Herstellerdateien oder unbereinigten Logs. Der Build-PASS gilt nur für den oben genannten Projekt-/Quellstand und diese IDE; er überträgt sich nicht auf Runtime, FW31-ABI, Original-I/O oder Hardware.

## Abschluss des Forschungsblocks

Die lokale hardwarefreie Suite ergab frisch **92 PASS** unter Python 3.13.5. Alle 25 ausgewählten Quellmanifest-Einträge stimmen. Die Engineering-VM wurde nach Beendigung der eigenen IDE-Prozesse wieder auf Datenträger pausiert; Status gestoppt wurde separat bestätigt. Die Referenz enthält weiterhin die vorherige gestoppte Anwendung; die eigene Testanwendung ist entfernt. [Bereinigte Prüfdaten](../evidence/codesys-engineering-validation-2026-10-12.json) binden Quellen, private Berichtshashes, getrennte Offlineartefakte und Checks ohne Originaldateien oder Gerätezugänge zu veröffentlichen.
