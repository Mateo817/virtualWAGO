# Reale Originalruntime mit virtuellen Digital-8-Modulen

Stand: 12.10.2026. **PASS für native zyklische Eingangsdaten und angeforderte Ausgangsframes bei geschlossenem Modellausgangsgate.** Die reale Referenzsteuerung führte die originale Runtime, den nativen I/O-Manager und originale IoDrvDal-/IoDrvKbus-Dateien aus. Nur die belegte ADI-Providerdatei war innerhalb der isolierten Sicht durch den Eigenprovider ersetzt. Kein allgemeiner WAGO-Hardwareemulator und kein physischer Aktortest.

## Konfiguration und tatsächlicher Lauf

Das eigene native CODESYS-Projekt enthält 750-430 und 750-530 mit je acht Kanälen und gespeicherter BYTE-Zuordnung auf PLC_PRG.InputByte/OutputByte. Controller- und Modulbeschreibungen blieben original. Die originale LocalBus-Beschreibung aktiviert Parameter 41 TCM standardmäßig mit 16777216. Der eigene Provider unterstützt diesen Modus noch nicht. Der originale K-Bus-Treiber übersetzt jede nicht erfolgreiche ConfigureDevice-Antwort an diesem Rückweg in16. Ein eigenes frisches Projekt setzte daher den dokumentierten Wert0 über die reguläre [ScriptValueDataElement.value-API](https://content.helpme-codesys.com/en/ScriptingEngine/ScriptDeviceParameters.html); Build und schreibfreies Wiederöffnen bestätigen TCM 0, unveränderte Zuordnungen und null Fehler/Warnungen. Der Provider lehnt unmodelliertes TCM weiterhin ab.

Mit TCM 0 konfiguriert die originale Runtime den Eigenprovider erfolgreich. Die native Bootanwendung bleibt im Initversuch STOP; Modell geöffnet1/konfiguriert1/Fehler0. Fehler16 ist in diesem Lauf nicht mehr vorhanden. Das qualifiziert den Initpfad dieser Konfiguration; es ersetzt keine explizite Einzelprüfung der vollen Signaturfunktion.

Der anschließende separate IEC-Zyklusprobe lief tatsächlich in RUN. Sein IEC-Ausgangspermit war TRUE; Ein- und Ausgangsvariable starten0. Das zusätzliche Modellpermit blieb während des gesamten Versuchs0. Seine Berechnung läuft im kompilierten IEC-Programm; der Adapter stellt Eingänge bereit und übernimmt echte Ausgangsbefehle. Die vorhandene Anwendung und ihr Bootprojekt wurden dafür nicht überschrieben.

Der erste tatsächlich ausgeführte Probe kopierte InputByte auf OutputByte. Die vier Modellkommandos änderten ausschließlich Eingänge; STATUS beobachtete danach:

| Eingang | Angeforderter Ausgang | Wirksamer Ausgang | Vollständige Frames |
|---:|---:|---:|---:|
|0|0|0|376|
|129|129|0|438|
|90|90|0|500|
|255|255|0|568|

Alle vier Samples meldeten zugleich konfiguriert1, laufend1, Fehler0 und Modellpermit 0. Native RUN-Abfrage, Originalkomponentenmaps, eigener Providerhash und die vollständigen Frames sind getrennt gebunden. Die Taskkonfiguration ist 20 ms; aus diesen Framezahlen folgt keine harte Echtzeit- oder Frequenzgarantie.

## Grenzen der Fehlerprobe

Ein eigenes FAULT-Kommando setzte Fehler1. Angeforderter Ausgang255 blieb beobachtbar, wirksamer Ausgang blieb0; die Anwendung bliebRUN und der Framezähler stieg auf630. Damit sind nur die Modellfehlervariable und der weiterhin geschlossene Ausgang belegt. Ein Übergang eines zuvor wirksamen, nichtnulligen Ausgangs auf0 wurde nicht getestet. Es folgt kein PASS einer allgemeinen nativen WAGO-Fehler-/Watchdog-/STOP-Reaktion.

Controllerdaten wurden ausschließlich von derselben echten Platine schreibgeschützt gelesen. K-Bus/UIO/Mem, Host-D-Bus und Netzwerk-Egress waren weiterhin verborgen. Alle Moduldaten stammen aus dem Eigenmodell; kein echter Modulcache als Laufzeitfallback. Das erlaubt diesen I/O-PoC trotz angeschlossener echter Klemmen, beweist aber keinen Versuch nach deren physischem Entfernen.

## Rücknahme und Restumfang

Root stellte nach jedem Versuch die einzelne Originalruntime mit STOP-Bootguard wieder her und stellte anschließend die Originalconfigbytes zurück. Frische Nachabfrage: Original-STOP, normales Runtimehome und unveränderte APP-/CRC-/Config-/Runtime-/Provider-/Treiberhashes. Die IDE-VM wurde nach Root-Nutzung wieder auf Datenträger pausiert. Worker führten ausschließlich Offlinearbeiten und Reviews durch.

Modellpermit 1, Verlust seiner Verbindungslease, ein eigener nativer STOP-/Wiederanlauf des laufenden virtuellen Programms, kanalgenaue physische Bitreihenfolge und reale Modulrevisionen bleiben offen. Packung, logische/monotone Watchdogpolitik und sequenzielle Framebehandlung bleiben ausdrücklich eigene Modellregeln. Vollständige TCM-/Register-/Analogmodule und eine vollständig virtuelle Steuerung folgen später. Eine zusätzliche virtuelle Runtime-Lizenz ist kein pauschaler Blocker dieses erreichten realen Referenzpfads.

## Zusätzliche IEC-Kontrollrechnung

Der aktuelle [IEC-Probe](../prototype/iec/minimal_io_8_bridge_probe.st) berechnet OutputByte := InputByte XOR BYTE#16#96. Sein [Offline-Builder](../tools/codesys_mapped_digital8_bridge_probe.py) verwendet das gleiche TCM 0-/BYTE-Projekt in einem frischen privaten Zielordner. Quelle, gespeichertes Projekt, Boot-APP und CRC sind separat vom früheren Copy-Probe gebunden. Echter Build und schreibfreies Wiederöffnen PASS, null Fehler/Warnungen.

Auch dieser neue Stand lief danach tatsächlich in der originalen Runtime. Die vier beobachteten Samples stimmen mit der im IEC-Code berechneten XOR-Funktion überein:

| Eingang | Nativer Ausgangsbefehl (XOR 150) | Wirksamer Modellausgang | Vollständige Frames |
|---:|---:|---:|---:|
|0|150|0|360|
|129|23|0|422|
|90|204|0|484|
|255|105|0|546|

Konfiguriert1/laufend1/Fehler0/Modellpermit 0 in allen vier Samples. Die Berechnung befindet sich ausschließlich im kompilierten SPS-Programm; Eigenadapter und Modellbrücke sind bytegleich zum Copy-Versuch. Das Modellkommando INPUT verändert nur Eingangssignale. Hier ist damit die echte IEC-Verarbeitung mit anschließenden vollständigen Ausgangsbefehlen belegt.

Die anschließende Modellfehlerprobe meldet Fehler1, angefordert105, wirksam0, weiterhinRUN und608 Frames. Ihre Grenzen sind dieselben wie oben. Kind/Wrapper enden bei der kontrollierten Rücknahme mit0; drei genuine Controlleröffnungen vermittelt, keine eigenen Kill-/Kontroll-/Pfadfehler. Frischer Original-STOP-/Hashnachweis und pausierte VM PASS. [Gebundene Evidence](../evidence/native-cyclic-2026-10-12.json). [Controllerzugang und frühere Fehler](controller-metadata-2026-10-12.md), [Versuchsplan](real-controller-plan-2026-10-12.md).
