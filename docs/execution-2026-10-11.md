# Ausführung: Offlinebestand, Zielisolation und Original-ADI-Befund

Stand: 11.10.2026. Basis: `main` / `0bdddbf77d688fd9e1cce7165d718fa6a30efe2c`, Forschungsbranch `research/originalstack-m1-m2`. Der genaue veröffentlichte HEAD und seine CI-Läufe werden im PR gebunden. Die Roadmap-Abnahmen bleiben unverändert.

## Tatsächlich erreicht

**VERIFIZIERT:** Beide Manifestprüfungen des privaten Übergabepakets bestanden. ZIP-SHA-256: `04361f3203454f4bdc32efd115e3a987fc972d0f1e68cf0a69c035320541de5f`. Die ursprünglichen 52 Backend-/Werkzeugtests wurden auf unveränderten Paketquellen neu ausgeführt. Eigener Code wurde selektiv übernommen; Vollstudie, private Projektquellen, Zugangsdaten, Originalheader, Firmware, Lizenzcontainer und Rohtraces bleiben außerhalb von Git. Der alte ungebundene Hardwarecollector wurde ausgeschlossen.

**VERIFIZIERT:** Der aktuelle Host ist Debian 13.7 / Linux x86-64, Kernel `6.12.111+deb13-cloud-amd64`, Python 3.13.5 und GNU Binutils 2.44. Vorhanden sind GCC 14.2.0, `arm-linux-gnueabihf-gcc` 14.2.0 und QEMU-User 10.0.13. `qemu-system-arm` wurde im PATH nicht gefunden. Ein natives CODESYS-Engineeringprofil, aktuelle Gerätebeschreibungen und eine nutzbare Lizenzzuordnung wurden in den geprüften Standardinstallationsorten nicht gefunden bzw. bereitgestellt. Archivierte Inventare aus Produktquellen sind keine heutigen Installationsnachweise. Keine fremde VM, Containerinstanz, CI oder Toolchain wurde verändert.

**VERIFIZIERT:** [reference_netns.py](../tools/reference_netns.py) setzt für geprüfte Referenzbefehle eine neue User-/Netzwerknamespace mit `inet`-Default-Drop und ausgewählten TCP-Ports zur exakten lokalen Allowlist auf. Der lokale Kernel-Negativtest nutzt ausschließlich einen eigenen Loopbacklistener. Die Payload kann die Regeln nicht administrieren. [Konfiguration, Hash und Grenzen](network-isolation.md) sind dokumentiert. Das Werkzeug ist keine Firmware-Dateisystem-/Geräte-/IPC-Sandbox.

**VERIFIZIERT, enger Scope:** Der [FW30-Originalbestand](abi-research-2026-10-11.md) belegt den ADI-Import des originalen `libIoDrvDal`, `DT_NEEDED`, zusätzliche Diagnose-/D-Bus-/Async-/Zeit-/Retainpfade sowie echte Header. Die ARM32-Sonde misst unter GCC 14.2 eine 136-Byte-Tabelle mit 34 Zeigern. `GetDeviceList` erwartet Slots, nicht Bytes; der Nullkapazitätspfad schreibt keine Einträge. Die statische Analyse wurde unabhängig geprüft und vor Veröffentlichung korrigiert. Der abweichende SDK-Compilerstand 11.3.1 und jede andere Firmware bleiben unqualifiziert.

## Gerätebestand und Eingriffsgrenzen

**VERIFIZIERT als Eigentümeraussage:** Der Eigentümer bestätigt, dass alle realen Aktoren elektrisch abgetrennt sind und das dedizierte Gerät eingeschaltet und lokal erreichbar ist. Details wurden angekündigt. Eine eigene elektrische Inspektion wurde nicht durchgeführt. Die Aussage wird nicht als unabhängige physische Messung ausgegeben.

**FAIL für diesen Zugriffspfad:** Nach lokaler Policy-/Routenprüfung und technischer Egress-Sperre liefen SSH- und HTTPS-Verbindungen in Timeouts; auch der initiale HTTP-Zugriff lieferte keine Verbindung. Ein begrenzter, ausschließlich auf die erlaubte SSH-Zielverbindung gefilterter Hostmitschnitt zeigte ausgehende SYNs ohne SYN-ACK. Die Namespace-Regel erlaubte diese Pakete. Daraus folgt weder eine bestätigte Geräteidentität noch die allgemeine Nichterreichbarkeit des Geräts vom Eigentümernetz. Keine Subnetzsuche und kein Ausweichgerät wurden verwendet.

**BLOCKED:** SSH-Hostkey, Artikel/Hardwarestand, Serienidentität, Firmware-Build, Kernel des Geräts, Runtimeprozesse, geladene Libraries/Maps, Init-/Runtimekonfiguration, Klemmenbestand und Originalbackup konnten mangels Verbindung nicht erhoben werden. Das admin-Protokoll und die Kontorechte bleiben **OFFEN**; es wurde keine erfolgreiche Anmeldung erreicht. Keine Zugangsdatenänderung, Installation, Service-/Autostartänderung, DAL-Initialisierung, K-Bus-Masteränderung oder Aktorprüfung wurde vorgenommen. Die gesperrte Anlage wurde nicht kontaktiert, auch nicht zum Sperrtest.

Produktrepositories wurden über GitHub frisch als Quellen gebunden; Quellrevisionen und begrenzte Konfigurationsscreenings bleiben im privaten Evidenzbereich. Es wurden keine aktiven Produktkonfigurationen, Geräteidentitäten, privaten Schlüssel oder Lizenzen übernommen. Kein Deploymentartefakt wurde gestartet. Deshalb liegt auch kein freigegebener Installations-/Rollbacknachweis vor; dieser hängt vom noch fehlenden ursprünglichen Gerätebestand ab.

## Checks und Nachweisstufen

| Check | Status | Konfiguration und Scope |
|---|---|---|
| Übergabe- und Forschungsmanifest | PASS | Unveränderte private ZIP-Inhalte, Hash oben |
| Ursprüngliche 52 Tests | PASS | Python 3.13.5, historische Paketquellen |
| Erweiterte 64 Tests | PASS | Eigener importierter Backend-/Werkzeugcode; zusätzlich unabhängiger Reviewlauf |
| JSONL- und geschlossene Modelldemo | PASS | Synthetische Konfiguration; Stimuli und Modellzeit, keine SPS-Ausführung |
| Netzpolicyparser und Standardplan | PASS | Bereinigte Ausgabe; kein Netzwerk im Unit-Test |
| Kernel-Negativtest und Capabilityentzug | PASS | Lokaler Loopbacklistener; keine externe Zielverbindung |
| Original-ELF-/Headeranalyse | PASS | Statisch, exakter FW30-SDK-Pin, Hashes im ABI-Bericht |
| Eigene ARM32-ABI-Sonde | PASS | Compile-only, FW30-Header + GCC 14.2; Objekt bleibt privat |
| Unverändertes Herstellerbeispiel | PASS | Compile-only mit zwei Warnungen; nicht gelinkt oder ausgeführt |
| Referenz-SSH/Webverbindung | FAIL | Isolierter freigegebener Zugriffspfad; Timeouts |
| Geräteidentität, Originalbackup, admin-Rechte | BLOCKED | Kein Handshake; keine erfundenen Inventardaten |
| ABI-Abgleich zum tatsächlichen Gerät | BLOCKED | Gerätefirmware und Originalkomponenten fehlen |
| Original-I/O-Verbraucher Init/DI/DO/Negativkontrolle | BLOCKED | Keine qualifizierte Ausführungsumgebung oder echte Modul-/Parameterverträge |
| Originalruntime, unverändertes IEC-Programm | NOT_RUN | Eigener nachfolgender Nachweis; Rechte/Lizenzbedarf offen |
| Hardware-/PWM-/Register-/Mehrinstanztests | NOT_RUN | Kein Bus-/Aktorzugriff oder Runtimebenchmark |

GitHub Actions testet ausschließlich die eigene Suite auf Python 3.11 und 3.13. Actions sind auf frisch aufgelöste Git-SHAs gepinnt. Der Kernel-Namespace-Test und proprietäre Artefakte werden nicht in CI ausgeführt oder hochgeladen. Die aktuellen CI-Ergebnisse gehören zum veröffentlichten PR-HEAD; keine alte CI wird als neuer Runtimebeleg verwendet.

Ein erster Werkzeug-Regressionslauf scheiterte wegen des vollen geteilten `/tmp`, ohne Produktfehlernachweis. Wiederholung mit eigenem privatem `TMPDIR` bestand. Fremde Dateien wurden nicht bereinigt. Eigene technische Prüfung ist **Self-Review**; der separate Sol-Worker führte tatsächlich einen unabhängigen Code-/Artefaktreview und 64 hardwarefreie Tests aus. Gefundene Dateiaustausch-, Namespace-Kontext- und statische Kontrollflussfehler wurden behoben. Keine unabhängige Hardware-, Rechts- oder Runtimefreigabe wird behauptet.

## Architekturentscheidung und nächster Einstieg

**HYPOTHESE bestätigt als Forschungsrichtung:** B+C bleibt bevorzugt. Der FW30-Binärimport macht ADI/DAL belastbarer als eine bloße Buildregel. Eine vollständig kleinere DDI-Grenze oder ein Bedarf an Boardemulation ist weiterhin nicht belegt. Die bestehende Produktsteuerung und interne SPS-Simulation werden nicht umgebaut.

M1 ist wegen des Geräteinventars **nicht abgeschlossen**. M2 besitzt belastbare statische FW30-Ergebnisse, aber **keine Abnahme für die noch unbekannte Gerätefirmware**. M3 besitzt nur eine unveränderte Hersteller-Compile-only-Vorbereitung und den synthetischen DI/DO-Modellkern. Es gibt keinen Shim-PASS, Original-I/O-PASS oder Runtime-PASS.

Nächster technischer Einstieg ist ein SSH-Handshake aus dem dokumentierten Referenzprozess mit geprüfter exakter Zieladresse, deaktivierten übernommenen SSH-Proxys/Weiterleitungen und lokal gebundenem Hostkey. Danach ausschließlich Inventar und gesicherte Originaldateien erfassen: Runtime, `libIoDrvDal`, `libIoDrvKbus`, `libdal`, relevante Konfigurationen und Metadaten. Erst der tatsächlich gemessene Firmwarestand bestimmt die nächste Header-/ELF-/Compilerkombination; FW31 ist keine Voraussetzung, die dem Gerät vorab zugeschrieben wird. Danach Init-/Modul-/Parameter-/Callbackvertrag vervollständigen und einen isolierten originalen DI/DO-Verbraucher einschließlich Negativkontrolle qualifizieren. Runtimeausführung, Installation und weitere Hardwareversuche behalten ihre eigenen Gates.
