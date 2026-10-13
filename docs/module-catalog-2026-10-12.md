# Modulkatalog und ausführbare eigene Hardwaremodelle

**Fortsetzung am 13.10.2026:** [Native Digitaltests](native-digital-tests-2026-10-13.md) qualifizieren jetzt beide festen C-Digitalprofile mit der realen Originalruntime. Hardwarevergleich, weitere Digitalprofile und native Analog-/PWM-/Seriellabnahme bleiben offen. Die folgende Tabelle und die 12.10.-Evidence beschreiben den historischen Offlineausbau.

Stand: 12.10.2026. **14 exakte Standardartikel, neun ausführbare Standalone-Modellprofile.** Kein Hardwareinventar. Dieser Ausbau erfolgte offline, ohne neue Geräte-/VM-/Originalruntimeversuche. Der frühere native 750-430/530-Nachweis bleibt an seine damaligen Quellen gebunden. [ADR-0007](adr-0007.md), [Quellenprüfung](module-catalog-sources-2026-10-12.md).

## Abdeckung

| Artikel | Eigene Modellabdeckung | Neuer nativer Nachweis |
|---|---|---|
|750-400|2 digitale Eingänge in einem eigenen gepaddeten Byte|NOT_RUN|
|750-402|4 digitale Eingänge in einem eigenen gepaddeten Byte|NOT_RUN|
|750-430|8 digitale Eingänge|NOT_RUN; frühere Digital-8-Referenz separat|
|750-530|8 digitale Ausgangsbefehle / wirksame Modellbits|NOT_RUN; frühere Digital-8-Referenz separat|
|750-504|4 digitale Ausgänge in einem eigenen gepaddeten Byte|NOT_RUN|
|750-1405|16 digitale Eingänge|NOT_RUN|
|750-1504|16 digitale Ausgangsbefehle / wirksame Modellbits|NOT_RUN|
|750-466|2 normale 4–20-mA-Signale, begrenzter Standardcodec|NOT_RUN|
|750-677|4 autonome PWM-Frq-Kanäle, paarweise Enablebits, eigene logische Zeit|NOT_RUN|
|750-454 / 750-455|Dokumentierte Analogkandidaten; kein ausführbares Modell|NOT_RUN|
|750-550|Dokumentierter Analogausgang; kein ausführbares Modell|NOT_RUN|
|750-652|Dokumentierte serielle K-Bus-Schnittstelle; Handshake/Format offen|NOT_RUN|
|750-600|Passiver Abschluss, kein erfundener ADI-Prozessdatenknoten|NOT_RUN|

Die Modelle nutzen [Katalogdatei](../config/module-catalog.json), [strengen Loader](../prototype/catalog.py) und [gemischte Simulation](../prototype/module_simulation.py). Ein fehlender Modellvertrag bleibt explizit unimplementiert. Suffixe, XTR- und andere Varianten werden nicht automatisch eingeschlossen.

## Benutzung ohne Gerätezugriff

```sh
python3 tools/module_catalog.py list
python3 tools/module_catalog.py show 750-466
python3 tools/module_catalog.py validate
python3 tools/module_catalog.py demo 750-677
python3 tools/module_catalog.py layout 750-430 750-530 750-466 750-677
python3 tools/module_catalog.py simulate 750-430 750-530 750-466 750-677 < config/catalog-demo.jsonl
python3 tools/generate_module_catalog.py --check
```

Der Layoutbefehl erzeugt ausschließlich eigene Forschungsoffsets. Wiederholte Artikel erhalten unabhängige Instanzen `m0`, `m1`, …; bestehende Railkonfigurationen mit expliziten Offsets bleiben nutzbar. Der native C-Adapter unterstützt weiterhin seine zwei gebundenen Digitalprofile und keine beliebige Pythonbestückung.

`simulate` verarbeitet pro Zeile eine eigene JSON-Anfrage: `observe`; `run` mit `running`; `input` mit `module`/`value`; `currents` mit `module`/`uA`; `cycle` mit vollständigem `outputs_hex` oder null zum Sampling; `advance` mit `dt_ns`; `fault` mit `kind`/`active`/`module`. Ausgabe enthält separate angeforderte/wirksame Daten und Scope. Unbekannte Operationen, Zusatzfelder und unimplementierte Artikel werden abgewiesen. Keine Runtimeverwaltung, Gerätekommunikation oder Netzwerkdienste.

Der gemischte Ablauf stellt DI 133 sowie 12/20 mA bereit und übernimmt voreingestellte DO-/PWM-Testbefehle. Keine SPS-Entscheidungslogik. Ein vollständiger Frame startet PWM mit 1000/2000/0/20000 Hz; nach 20 ms entstehen 20/40/0/400 Modellpulse. Beim eigenen Leaseablauf 100 ms sind 100/200/0/2000 Pulse gezählt und alle wirksamen Ausgänge geschlossen. Ein Lesezyklus verlängert die Lease nicht.

## Verhaltensgrenzen

- Digitale Bytepackung, Kanalnummern, Watchdog und Wiederfreigabe sind eigene Regeln. Filter/Spannungsschwellen, Ausgangsstrom und elektrische Fehler sind nicht modelliert.
- Analog: normale Stützwerte dokumentiert, Zwischenwert-Floorquantisierung eigene Annahme. Sechs Byte Status-/Wortprojektion ist kein nativer WAGO-I/O-Vertrag. Keine automatische Unter-/Überbereichs- oder Drahtbruchdiagnose.
- PWM: nur PWM Frq, nicht PWM DC oder alle Modi. Konfigurierte Frequenzen laufen autonom; originale Registerkonfiguration und Statusantworten fehlen. Eingangsstatus `NOT_GENERATED`, zugehörige Rohbereiche sind keine erzeugten Herstellerantworten. Zeitintegral, Phasenreset und Ausgangsgate sind eigene Regeln, keine gemessenen Flanken.
- Gemischte Simulation: vollständige Frames werden vor Änderung über alle Module geprüft. Busverlust, fehlendes Modul, Stop und Watchdog schließen wirksame Ausgänge; frischer kompletter Frame zur Wiederfreigabe nötig. Keine vollständigen Simulator-Snapshots; Teil-Rail-Restore würde Hilfszustände verlieren.
- Rail-Snapshots verwenden Format 2/Modell 0.2.0 und Katalogdigest. Alte Format 1-Snapshots werden abgewiesen; Vertragsänderungen dürfen nicht unbemerkt in alte Replays eingehen.

## Verifikation und nächste Aufgaben

[Gebundene Evidence](../evidence/module-catalog-2026-10-12.json) dokumentiert tatsächliche lokale Tests, eigene ARM-Regression und Reviews. Der Generator erhält bestehende Modulwerte, Descriptorpins und eigene Offsets. GNU-Lader/libc laufen in der eigenen Offline-ARM-Probe; originale IoDrv/Runtime und Hardware wurden dort nicht ausgeführt. Keine Herstellerartefakte ins Git.

Zum historischen Stand12.10. blieben neue native Digital-8-Regression und Digital-16-Abnahme offen. Die [Fortsetzung13.10.](native-digital-tests-2026-10-13.md) qualifiziert inzwischen beide festen Digitalprofile bei Modellpermit0. Analog-/PWM-ADI-/Registerverträge sowie Hardwarevergleiche mit gebundenen Revisionen bleiben offen. Diese Standalone-Modelle sind noch nicht an den originalen Runtime-Modellkanal für Analog/PWM angeschlossen; dessen heutiges Protokoll transportiert digitale Werte. Der frühere Digital-8-PASS wird nicht übertragen.

Virtuelle serielle Kommunikation auf der CAN-PFC200 und andere PFC200-Ausstattungen stehen in der [Roadmap](roadmap.md). Zuerst originale FW31-Komponenten, Portauswahl und Zusatzanforderungen prüfen. Die [CODESYS-Linux-Control-SL-Dokumentation](https://content.helpme-codesys.com/en/CODESYS%20Control/_rtsl_configure_modbus_rtu_linux.html) liefert einen Forschungsansatz für SysCom-Gerätedateien, keinen WAGO-FW31-Nachweis. Onboard-RS485 und K-Bus 750-652 sind verschiedene Verträge; echte Controlleridentität bleibt erhalten.
