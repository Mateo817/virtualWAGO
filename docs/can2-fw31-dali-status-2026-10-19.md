# CAN2, FW31 und reale DALI-Prozessdaten

**Spätere Fortsetzung vom 20.10.2026:** Der [aktuelle Originalstack-Bericht](can-native-boundary-2026-10-20.md) korrigiert die PDO-Auswahl anhand realer Schreibantworten, beschreibt den implementierten vcan-Linkadapter und trennt erfolgreiche Startup-SDOs vom fehlgeschlagenen vollständigen Runtime-/DALI-Lauf. Die folgenden PASS-/NOT_RUN-Angaben bleiben an ihre jeweiligen älteren Varianten gebunden.

Historischer Erststand: 19.10.2026. Fortsetzung: 20.10.2026 (siehe unten). Basis: `c446e2903c35c0253a0c315c8715d9f6ac1b8371`.
Private Kundenprojekte, Zielbindung, Herstellerartefakte und Rohlogs bleiben
außerhalb dieses öffentlichen Repositorys. Kein Firmwareupdate.

## Reale Beobachtung

**VERIFIZIERT / PASS:** Ein eigener, begrenzter SocketCAN-SDO-Leseclient
erreichte CANopen-Knoten 5 mit 125 kbit/s. Objekt `1018` lieferte Vendor 33,
Product 337 und Revision `0x00010020`. Das ist Koppleridentität, keine
Firmwareversionsbestimmung des DALI-Moduls.

Die read-only physische Modulliste `5202` enthält zwei Einträge einschließlich
Koppler: `0x02EE015100000000` (750-337) und `0x02EE028700000000` (750-647).
Der Eigentümer bestätigt die physische Folge 750-337 → 753-620 → 753-647 →
750-600. Versorgung und Abschluss sind keine zusätzlichen Prozessdatenmodule
in dieser gelesenen Liste. Die zuvor projektierten sechs weiteren I/O-Module
gehören nicht zu diesem Koppler.

`3800:00` lieferte 24. Alle 24 Eingangsbytes `3800:01..18` (hex) ließen sich
lesen: `01 00`, sechzehnmal `AA`, sechsmal `00`. Die Bedeutung dieser Rohbytes
im tatsächlichen DALI-Mailboxzustand bleibt **OFFEN**. Weder ein ACK noch ein
Leuchtenzustand wird aus diesem Muster erfunden.

**OFFEN: Fehlerfreier Betrieb.** Das Kopplerfehlerregister war zunächst `0x91`,
später `0x81`. Die Fehlerhistorie `1003` enthielt `0x00030000`, `0x00038120`
und `0x00015000`. Die Fehlercodes verweisen unter anderem auf Error Passive
und Hardwarekonfiguration; historische Einträge beweisen keine fortbestehende
Ursache. Das optionale Herstellerstatusregister ist deaktiviert
(`5200:06 = 0`); es wurde nicht aktiviert und die Historie nicht gelöscht.

## Engineering

Die bereitgestellte CAN2-Konfiguration verwendete den 750-8213 mit
Gerätebeschreibung 6.3.0.12 / FW27, EDS FileVersion 1.19 und vier DALI-Ports.
Alle 18 CAN-Teilnehmer waren bereits optional. Ein optionaler CAN-Teilnehmer
macht fehlende lokale Klemmen innerhalb eines vorhandenen Kopplers nicht
optional.

Eine private, reduzierte Testkopie ist auf 6.4.6.11 / FW31 umgestellt:
ein Koppler, ein 647-Modul, ein DALI-Port; andere Anlagenteile entfernt.
WagoAppDALI 1.3.1.15 ersetzt die nicht installierte 1.3.1.10;
WagoSysFieldbusModule bleibt 1.9.4.5. Eine alte Weiterleitung auf die fehlende
WagoSysModuleBase 2.0.2.10 wird auf die installierte 2.0.2.11 korrigiert.
Die EDS 1.19 ist nicht im Gerätekatalog installiert. Für den neu aufgebauten
Koppler wird ausdrücklich die bereitgestellte EDS 1.17 verwendet. Der
importierte Herstellerdescriptor bindet den 647 an Modul-ID 187; die
EDS-Abschnittsnummer 188 darf nicht als CODESYS-Modul-ID verwendet werden.
Ein eigener Zwischenversuch hatte dadurch zunächst ein 650-Modul ausgewählt;
die Exportprüfung erkannte das, und der Zwischenstand wurde nie eingesetzt.

Die automatische Konfiguration liefert für den korrekten 647 keine passende
24-Byte-PDO-Projektion. Deshalb werden die sechs vorhandenen DALI-PDOs aus
dem Originalprojekt übernommen. Die drei PDOs der fehlenden I/O-Module,
ihre Kanäle und ihre 26 Startup-SDO-Einträge werden entfernt. Es verbleiben
48 Byte-Kanäle und 96 Startup-SDO-Einträge. Diese Transformation benutzt
belegte native Exportdaten; sie ist allein noch kein Laufzeitnachweis.

Der DALI-Masteraufruf besitzt einen
anfänglich geschlossenen Software-Enable und unterdrückt ausdrücklich
`xWriteStandardSensorConfig`. Adressierung, Identifikation/Blinken und
Dimm-/Schaltbausteine gehören nicht in diesen Test.

**VERIFIZIERT / PASS:** Die endgültige Kopie wurde in CODESYS V3.5 SP21
Patch 5 nativ importiert und mit **0 Fehlern, 0 Warnungen** gebaut. Der danach
erzeugte Export bestätigt Modul-ID 187, die sechs PDOs und 96 Startup-SDOs.
Die lokale Prüfung kontrolliert alle 48 Variablen und die tatsächlichen
SDO-Mappingwörter: `3800:01..18` und `3900:01..18`, jeweils acht Bit.
Die IEC-Adressen sind `%IB1..24` und `%QB0..23`. Lokaler Kbus und Ethernet
sind deaktiviert. Aktive Gatewaybindung und Adresse sind leer; historische
Scanmetadaten bleiben ausschließlich in der privaten Projektdatei.

Projekt-SHA256:
`50a3a58ac196cef1be77dff5dac0ea3e0f606b337651c27bb7b79db0d01343c1`.
Weitere Hashes und Ergebnisse stehen in der
[sanitisierten Evidence](../evidence/can2-fw31-dali-status-2026-10-19.json).
Das Originalprojekt blieb hashgleich.

**NOT_RUN:** Ein eigenständiger erneuter Öffnungstest wurde nicht ausgeführt,
nachdem der Eigentümer die anderweitige Nutzung der Windows-VM bestätigte.
Es wurde danach kein weiterer IDE-Lauf gestartet. Die bereits laufende VM
bleibt für die andere Arbeit verfügbar.

**OFFEN / NOT_RUN:** Nativer CAN-/DALI-Laufzeitnachweis. Das reduzierte Projekt
wurde weder heruntergeladen noch gestartet. Der Software-Enable des
DALI-Masters verhindert nicht die Startup-SDO-/PDO-Schreibzugriffe des
CAN-Managers. Vor dessen Onlineversuch sind insbesondere der bestehende
PDO-Zustand des Kopplers, unbenutzte PDOs, Startup-Antworten und die weiterhin
aktive Fehleranzeige gezielt zu prüfen. Ein erfolgreicher Build ersetzt
diese Abnahme nicht.

## Versuchsgrenzen und Rücknahme

Die originale Runtime blieb während sämtlicher SDO-Abfragen derselbe Prozess
im STOP. Die Anwendung wurde nicht heruntergeladen, gestartet oder ersetzt.
APP, CRC und Runtimekonfiguration waren nachher hashgleich.

Vorher war `can0` DOWN ohne konfigurierte Bitrate. Die begrenzten Abfragen
aktivierten die Schnittstelle mit 125 kbit/s und brachten sie jeweils wieder
DOWN. Die zuletzt konfigurierte Bitrate 125 kbit/s und die Queuekonfiguration
bleiben gesetzt; eine bytegenaue Rücknahme der vorher unkonfigurierten
Schnittstelle wird ausdrücklich nicht behauptet.

Die Clients senden ausschließlich SDO-Uploads und bei der 64-Bit-Modulliste
die zugehörigen Upload-Segmentanforderungen. Keine SDO-Downloads, NMT-Befehle,
PDO-Ausgänge, Resets, DALI-Adressierung oder physische Aktortests. Pro Versuch
acht Sekunden Prozesslimit; Uploadantworten mit 700-ms-Frist. SSH-Zugriffe
liefen durch die vorhandene Zielnamespace mit ausschließlich freigegebenem
TCP/22 und strikter Hostkeyprüfung. Frischer lokaler Sperrtest PASS, kein
Kontakt zur geschützten Anlage.

| Nachweisstufe | Ergebnis |
|---|---|
| FW31-Projekt: nativer Import und Build | PASS, 0 Fehler / 0 Warnungen |
| Exportprüfung von Modultyp, Mapping und Startup-SDOs | PASS |
| Eigenständiges erneutes Öffnen | NOT_RUN, VM anderweitig genutzt |
| Gezielte Koppleridentität per SDO | PASS |
| Physische elektronische Modulliste | PASS |
| 24 DALI-Eingangsbytes per SDO | PASS |
| Kopplerfehlerregister gleich null | FAIL |
| Original-CODESYS-CAN-Treiber mit reduziertem Projekt | NOT_RUN |
| DALI-Leuchtenabfrage / Adressierung / Schalten | NOT_RUN |
| Virtueller CAN-/DALI-Teilnehmer | NOT_RUN |
| Originalanwendung/Config unverändert, Runtime STOP, CAN DOWN | PASS |

Eigene Implementierungs-/Ergebnisprüfung: **Self-Review**. Ein tatsächlicher
Luna-Worker recherchierte offline Herstellerverträge und Fehlerdiagnose;
er führte keine Geräte-, VM- oder unabhängigen Laufzeittests aus.

## Quellen

- [WAGO 750-337-Handbuch, Version 4.1.0, Herstellertext im Distributor-Mirror](https://www.e-motionsupply.com/v/750-337.pdf):
  Eingangsprozessdaten, physische Modulliste 5202, Fehlerobjekte und
  Unterscheidung von der schreibbaren virtuellen Konfiguration 4500.
- [CODESYS: CANopen Remote Device](https://content.helpme-codesys.com/en/CODESYS%20CANbus/_can_edt_canopen_remote_device_general.html):
  optionale Teilnehmer und Projektkonfiguration.
- [WAGO WagoAppDALI-Handbuch, Version 1.3.0.36, Herstellertext im Distributor-Mirror](https://assets.heizung-billiger.de/documents/wago_f2c9c0643d7e890e.pdf):
  dokumentierter Schreibeffekt von `xWriteStandardSensorConfig`; ältere
  Handbuchversion nicht als vollständiger Binärvertrag von 1.3.1.15 behandeln.


## Fortsetzung am 20.10.2026

Der Eigentümer gab die VM wieder frei und bat, ein gegebenenfalls noch offenes
Projekt lokal zu sichern. Die frische Prüfung fand keinen CODESYS-Prozess;
ein solches Projekt musste deshalb nicht gespeichert werden. Die VM war
bereits aktiv und wurde aktiv belassen; eigene IDE-Prozesse sind geschlossen.

**VERIFIZIERT / PASS:** Die am Vortag gelieferte Projektdatei wurde mit
`NoUpdates` erneut geöffnet. Dateihash und Mapping-CSV blieben bytegleich.
Der native Export ist nach Sortierung ausschließlich der Dictionary-Einträge
semantisch identisch. Der frühere Reopen-Blocker ist damit aufgehoben.

Eine weitere private Kopie schaltet die übernommene Manageroption
`NMTStartAll` (belegte Parameter-ID 263) von TRUE auf FALSE. Damit wird die
projektierte globale Startoption entfernt. Das ist ein Konfigurationsnachweis,
noch kein beobachteter NMT-Trace. Topologie, sechs PDOs und 24+24-Byte-Zuordnung
bleiben erhalten. Rebuild, Codegenerierung und Bootdateierzeugung: jeweils
**PASS, 0 Fehler / 0 Warnungen**. Eigenständiges erneutes Öffnen dieser neuen
Kopie ebenfalls **PASS**, Datei unverändert, Export semantisch gleich und
Mapping-CSV bytegleich.

Neue Projekt-SHA256:
`d3bb3b32f717694618562e63cb6c9e462eae21e2427fffd3989cc7a3c50e048a`.
Die erzeugten APP-/CRC-Dateien wurden nicht auf die Steuerung geladen.
[Neue Evidence mit Artefakthashes](../evidence/can2-fw31-dali-status-2026-10-20.json).

**VERIFIZIERT / PASS:** 49 gezielte SDO-Uploads lasen die Koppleridentität,
die ersten fünf RX-/TX-PDO-Kommunikations- und Mappingobjekte sowie das
Fehlerregister. Alle zehn gelesenen PDO-COB-IDs haben ihr Deaktivierungsbit
gesetzt. Bei PDO Nummer 5 sind jeweils acht Bytes ab `3900:01` beziehungsweise
`3800:01` eingetragen. Die ersten vier haben Mappinganzahl null. Dies ist
kein vollständiges Inventar der jeweils 32 möglichen PDOs. Keine
SDO-Downloads, NMT-Befehle oder Ausgangs-PDOs wurden gesendet.
Fehlerregister weiterhin `0x81`: fehlerfreier Betrieb bleibt **OFFEN**.

**VERIFIZIERT / PASS, enger Scope:** Der vorhandene Kernel unterstützt vcan.
Ein virtuelles Interface namens `can0` ließ sich in einem frischen, getrennten
Netzwerk-Namensraum erzeugen und aktivieren. Dort existierte kein physisches
CAN-Interface und keine Bridge. Ein Bitraten-Setzversuch mit 125 kbit/s lieferte
`Operation not supported` (**FAIL** für diesen Aufruf). Das beweist weder
Socket-Datenverkehr noch die Kompatibilität der originalen CAN-Bibliothek;
ein originaler Treiber-/Runtimeversuch auf vcan wurde **NOT_RUN** gelassen.

**OFFEN / NOT_RUN:** Der vollständige reale CODESYS-Anlauf wartet auf die
Klärung, ob DALI-Geräte angeschlossen oder die DALI-Leitung abgeklemmt ist.
Die reine VM-Freigabe belegt diesen Anschlusszustand nicht. Die zusätzliche
Offlineprüfung des vorhandenen Herstellertexts belegt keine garantiert
wirkungslose All-zero-Ausgabe im Full-Modus und keinen vollständigen
nebenwirkungsfreien Master-Initialisierungspfad. Daher kein Start der
Bootdatei als improvisierter Leuchtentest. Der vorhandene DALI-Master-Enable
ist weiterhin geschlossen, aber kein technisches Gate für CAN-Manager-PDOs.

Die abschließende frische Prüfung bestätigt denselben ursprünglichen
Runtimeprozess in STOP, unveränderte APP-/CRC-/Config-Hashes und physisches
CAN DOWN mit derselben Bitrate wie vor diesem Block. Der private Namespace
wurde beim Prozessende aufgelöst. Keine Herstellerdateien oder privaten
Projekte werden veröffentlicht. Eigene Prüfung: **Self-Review**; der erneute
Luna-Quellencheck war ausschließlich offline.
