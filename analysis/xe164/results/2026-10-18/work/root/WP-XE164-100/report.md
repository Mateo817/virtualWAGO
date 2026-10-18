> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-100 — kleinste belegte Ersatzgrenze für Digital-8/16

## Frage und Ergebnis

Welche untere Schnittstelle muss virtualWAGO für die bereits demonstrierten
Digital-8/16-Profile nach den neuen FW31-Loader- und Consumerbefunden
nachbilden?

**HYPOTHESE, jetzt stärker statisch und durch die getrennten Runtimeläufe
gestützt:** Die kleinste derzeit belegte Ersatzgrenze bleibt der von
`adi_GetApplicationInterface()` gelieferte Provider unterhalb der erhaltenen
originalen Komponenten IoDrvDal und IoDrvKbus. Für die exakt demonstrierten
Digital-8/16-Profile ist keine Nachbildung des physischen K-Bus-Protokolls oder
des XE164-Laufzeitverhaltens belegt notwendig. Erforderlich ist eine
kompatible Reaktion an der beobachteten Providergrenze: Discovery/Open,
begrenzte Konfiguration und Terminalbeschreibung, getrennte äußere/innere
DeviceSpecific-Ergebnisse, zyklische Read-/Write-Transaktionen,
Diagnose/Application-State/Watchdog und eine explizit fail-closed gehaltene
Modellseite.

Die Aussage ist **keine** Vollständigkeitsbehauptung für einen allgemeinen
K-Bus, weitere Modultypen oder eine vollständig virtuelle WAGO. Insbesondere
bleiben get-uid/read-conf-reg für konkrete Zielrecords, nicht beobachtete
Provider-Slots, Seiteneffekte der Finish-Aufrufe sowie umgebende Board-,
Signatur-, D-Bus-, Diagnose-, Zeit- und Retain-Dienste getrennt **OFFEN**.

## Neue statische Kette

**VERIFIZIERT:** Die gespeicherte FW31-Konfiguration nennt
`libIoDrvKbus`/`IoDrvKbus_Init`. Der generische IoDrvDal-Loader berechnet eine
Instanzbasis mit Schrittweite `0x63c`, löst das konfigurierte Symbol auf und
ruft es mit der Basis als einzigem sichtbaren Argument auf. `ComponentEntry`
veröffentlicht seinerseits einen numerischen Dispatcher bei Ausgabeoffset
`+0x18`; dessen Fall `3` kann bedingt die direkte Loader-Schleife erreichen.
Damit ist die statische Kette vom benannten Komponenteneinstieg bis zum
konfigurierten Init deutlich enger als in WP-XE164-060. Die semantischen Namen
des Felds `+0x18` und des Selektors `3`, der erste Instanzindex und tatsächliche
Ausführung bleiben **OFFEN**.

**VERIFIZIERT:** IoDrvKbus publiziert mehrere Kandidaten in dem vom Init-Aufruf
befüllten Bereich. Die zentrale Record-Validierungsprozedur hat zwei direkte
statische Aufrufer in bereits belegten Init-publizierten Kandidaten. Innerhalb
der Validierung sind die Rohguards für get-uid/read-conf-reg, vier maskierte
Vergleichsmodi und die Statusakkumulation belegt. Feldnamen, Recordsemantik und
Digitalprofil-Reachability folgen daraus nicht.

## Bedeutung für die virtuelle Schnittstelle

1. **Originalstack behalten — HYPOTHESE/Architekturentscheidung:** IoDrvDal und
   IoDrvKbus bleiben Verbraucher. virtualWAGO stellt den darunterliegenden
   ADI-Provider bereit. So bleiben deren Scan-, Mapping- und Zyklusentscheidungen
   im Originalcode statt in einem nachgeschriebenen K-Bus-Modell.
2. **Provideroberfläche — VERIFIZIERT im gebundenen Stand:** Die exakten
   Consumer kopieren beziehungsweise verwenden die 34 Einträge große
   32-Bit-Tabelle und die akzeptierten Analysen berichten 22 direkt
   aufgerufene/weitergereichte Slots. Der aktuelle Eigenadapter belegt alle 34
   Einträge und implementiert diese 22. Die Slotnamen stammen teilweise aus
   dem FW30-Headerbeleg und sind keine pauschale FW31-ABI-Zertifizierung.
3. **Digitaler Mindestpfad — VERIFIZIERT für getrennte Nachweisstufen:** Die
   statischen Consumerbefunde verlangen Discovery/Open, TCM-0-Konfiguration,
   Terminalinformationen/Tabellenkennung, Push sowie ReadStart/Transfer/End
   und WriteStart/Transfer/End mit getrennten Resultaten und beobachteter
   Statusbehandlung. Hashgebundene Originalconsumer-Läufe zeigen, dass der
   Eigenprovider damit die ausgewählten Digital-8/16-Signalfolgen verarbeiten
   konnte. Sie sind kein interner Calltrace.
4. **Nicht physisch simulieren — HYPOTHESE im begrenzten Scope:** Prozesswerte,
   angeforderte Ausgänge und Modellreaktionen genügen unter dieser Grenze; ein
   Bit-/Telegramm-/Timingmodell des echten K-Bus ist für die bereits gezeigten
   Digitalprofile nicht als zusätzliche Voraussetzung belegt.
5. **Unsichere Operationen — OFFEN:** Der aktuelle Adapter liefert für
   get-uid/read-conf-reg außen Erfolg und innen `-1`. Das widerspricht den
   erfolgreichen Digitaltrials nicht nachweislich, weil deren konkrete Calls
   nicht protokolliert sind. Wenn die in E-XE164-106 gebundenen Pfade erreicht
   werden, verfehlt `-1` jedoch deren Erfolgsprädikat. Vor Erweiterung auf
   andere Records/Profile ist daher zuerst Reachability oder ein exakter
   Profilvertrag nötig.

## Entscheidung und nächster Schritt

**VERIFIZIERT als Analysepriorität:** Breite weitere XE164-Decompilation ist
für die schon demonstrierten Digital-8/16-Profile nicht der nächste kritische
Schritt. Der nächste kleine Offlineblock soll stattdessen entweder

- die aktuelle Providerimplementierung gegen die nun konsolidierte
  Mindestmatrix automatisiert prüfen, besonders getrennte äußere/innere
  Ergebnisse und Finish-Seiteneffekte, oder
- eine lokal vorhandene, exakt hashgebundene Profil-/Recordquelle finden, die
  get-uid/read-conf-reg-Reachability für genau 750-430/530 beziehungsweise
  750-1405/1504 entscheidet.

Ohne eine solche Quelle bleibt die Reachability **OFFEN**; sie wird nicht aus
Modulnamen, erfolgreichen Ausgabemustern oder Rohdiscriminatoren erfunden.

## Eingaben, Methode und Grenzen

Die neun Eingaben und ihre SHA-256 stehen in `inputs.tsv`. Sie verbinden die
frühere Grenzmatrix WP-XE164-060, die zyklische Detailsynthese WP-XE164-086
und die akzeptierten WP-XE164-095 bis -099. Methode: integrative statische
Self-Review durch Root; keine neue Binäranalyse, kein Build, kein Runtime-,
VM-, Netzwerk-, Geräte- oder Hardwarezugriff. `contract-matrix.tsv` trennt
Beobachtung, minimale Konsequenz und Restunsicherheit.

Alternativerklärung: Die erfolgreiche begrenzte Nativevidence kann von
erhaltenen Originaldiensten oder nicht protokollierten Provideraufrufen
abhängen. Deshalb ist die ADI-Grenze für den nachgewiesenen Digitalpfad die
führende, nicht die global bewiesene Schnittstelle. Ein später ausgewähltes
Analog-, PWM-, serielles oder vollständiges Plattformprofil kann zusätzliche
Operationen oder Dienste benötigen.

Tests: Eingabehash-/Matrixvalidator **PASS**. Neue Builds und öffentliche
Tests **NOT_RUN**; Originalconsumer-Runtime und Hardware **NOT_RUN**.
