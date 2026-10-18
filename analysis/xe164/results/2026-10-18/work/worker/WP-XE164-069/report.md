> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-069: belegte Consumer-Lifecycle-Reihenfolge

Stand: 2026-10-15. Methode: ausschließlich offline gebundene Berichte und deren TSV-Auszüge abgeglichen. Alle fünf Eingaben stimmen bytegenau in Größe und SHA-256 mit dem Arbeitsauftrag überein; Details in `inputs.tsv`.

## Ergebnis

Die Berichte belegen keine vollständige ursprüngliche Reihenfolge `Init -> Scan -> GetList -> Open -> Configure -> AppState/Watchdog -> Read/Write -> Close -> Exit`, und auch keine vollständige Rollback-/Restart-Sequenz des Consumers. Slotnummern, Tabellenpositionen und geordnete Listen von Callsite-Adressen wurden nicht als Aufrufreihenfolge interpretiert.

Als Consumer-Reihenfolge sind nur diese lokalen Beziehungen belegt:

- Im beschriebenen IoDrvDal-Pfad wird eine Geräteliste geholt, ein passender Gerätename gesucht und danach `OpenDevice` aufgerufen; die zurückgegebene DeviceId wird gespeichert. Der Bericht bindet diese Relation an direkte statische Consumer-Evidence, aber nicht an einen ausgewählten vollständigen Startup-Aufrufer oder an `Init`/`ScanDevices` als Vorgänger.
- Kbus-Eingabe: `ReadStart`, danach gemappte Bit-/Byte-Transfers, danach `ReadEnd`.
- Kbus-Ausgabe: `WriteStart`, danach gemappte Bit-/Byte-Transfers, danach `WriteEnd`.

Für `Init`, `ScanDevices`, `ConfigureDevice`, `ApplicationStateChanged`, die vier Watchdogslots und `Exit` sind direkte Callsites belegt, aber die verlangten Relationen und Lifecycle-Übergänge nicht. Für `CloseDevice` melden die Berichte keine exakte FW31-Callsite; das beweist keine Unerreichbarkeit. `ConfigureDevice` hat eine belegte statische Kbus-Callsite und native Läufe mit Zustand `configured=1`, aber keine per-Slot Laufspur, die es zu `OpenDevice`, AppState oder Watchdog ordnet.

Der native Bericht beobachtet eigene Providertelemetrie und Laufzustände wie `opened=1`, `configured=1`, `running=1`, Watchdog-/Fehlerwerte und vollständige Frames. Das ist ein echter Lauf des Originalstacks in einer begrenzten Konfiguration, isoliert aber keine einzelnen ADI-Aufrufe und liefert keine vollständige zeitliche Lifecycle-Spur. Der dokumentierte Rollback ist dagegen eine konkrete Betriebssequenz: Originalruntime mit STOP-Bootguard wiederherstellen, danach Originalkonfigurationsbytes zurückstellen, anschließend frisch STOP und Hashgleichheit abfragen. Sie beschreibt die kontrollierte Rücknahme des Versuchs, nicht `CloseDevice`/`Exit`-Semantik oder einen nativen App-Neustartpfad.

Die eigenen Adapterregeln für Close/reopen, Frame-Latching/Commit, Ausgangsgate und logischen Watchdog sind Modellpolitik. Sie sind keine Rekonstruktion der ursprünglichen Consumer- oder Hersteller-Lifecycle-Semantik.

## Aussageklassen und Status

`VERIFIZIERT` bezeichnet hier nur die konkrete in den Quellen verankerte Callsite, lokale Callreihenfolge oder dokumentierte Laufbeobachtung. `OFFEN` bezeichnet nicht nachgewiesene Relationen bzw. Semantik; kein fehlender Callsite-Nachweis wird zu Nichterreichbarkeit hochgestuft. `HYPOTHESE` und `BLOCKED` sind für die Reihenfolgeaussage nicht erforderlich. Tests: `NOT_RUN` (dieses Paket führt keine Tests oder Runtime-/Geräteaktionen aus).

Die vollständige Einzelzuordnung mit Quellenstellen, Evidence-Tier, alternativer Erklärung und Begrenzungen steht in `lifecycle-evidence.tsv`. Zentrale Gegenbelege gegen eine überzogene Sequenz sind `adi-contract-2026-10-12.md:56,69,71,94,102`, `boundary-static.tsv:2-7,13-14,18-24,29,32-35`, `boundary-matrix.tsv:3-11` und `native-cyclic-2026-10-12.md:22,26,32-34`.

## Restunsicherheit und Nicht-Nachweise

Nicht bewiesen sind: ein vollständiger ausgewählter Startup-/Shutdown-Aufrufer; `Init` vor `ScanDevices` oder beide vor der Enumeration; exakte Laufzeitreihenfolge und Fehler-/Rollbackzweige von Enumeration/Open/Configure; Lifecycle-Semantik und Reihenfolge von AppState- und Watchdogaufrufen; Close oder seine Unerreichbarkeit; Exit auf allen Beendigungspfaden; Zuordnung der Telemetrie zu einzelnen ADI-Calls; native App-STOP-/Wiederanlauf- und Watchdog-/Ausgangsreaktion; Callback-Lebensdauer, Synchronisation sowie globale Atomizität zwischen Tasks. Die lokale Reihenfolge der Kbus Read-/Write-Transaktionen beweist weder globale Serialisierung noch vollständigen I/O-Lifecycle.

Alternative Erklärungen bleiben möglich: mehrere Pfade oder Aufrufer können die Callsites unterschiedlich nutzen; native Status-/Zählerwerte können aus Adapterzustand, Runtimezustand oder anderen Pfaden stammen; erfolgreiches `configured=1` ersetzt keine per-call Spur. Die eigenen Close-/Reopen- und Watchdogregeln erklären Modellbeobachtungen, aber nicht Herstellerverhalten.

## Werkzeuge und Durchführung

Nur Datei-Lesezugriffe, SHA-256/Größenprüfung und Ausgabeerstellung. Keine Netzwerk-, Geräte-, VM-, Runtime- oder Binäranalyseoperation. Verwendete lokale Werkzeuge: GNU Bash 5.2.37, GNU coreutils 9.7 (`sha256sum`, `wc`, `nl`), ripgrep 15.2.0. Repository-HEAD bei Erstellung: `e56bb8ed488137f3d9276bfcbec6f33d2917114a`.

Keine Repositorydatei wurde geändert. Tests: `NOT_RUN`. Paketdatei-Hashes: siehe `sha256sums.txt`.
