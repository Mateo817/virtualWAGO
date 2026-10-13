# Modulbestand aus Eigentümerfoto, 12.10.2026

**VERIFIZIERT im Foto-Scope / Self-Review:** Der Eigentümer ergänzte die Referenzbestandsfrage mit einem Foto. Darauf sind vom Controller aus die folgenden Frontbeschriftungen und ihre Reihenfolge lesbar. Die Zuordnung zur autorisierten Referenz erfolgt über diesen Eigentümerkontext; es gab in diesem Nachtrag keine elektronische Geräteabfrage.

| Position vom Controller aus | Lesbare Artikelnummer | Herstellerbeschreibung |
|---|---|---|
| Controller | 750-8213 | Controller-Artikel auf dem Foto; passt zum früheren Device-Tree-Modell |
| I/O 1 | 750-430 | [8 digitale Eingänge, 24 V DC, 3 ms](https://www.wago.com/us/controllers-bus-couplers-i-o/8-channel-digital-input/p/750-430) |
| I/O 2 | 750-530 | [8 digitale Ausgänge, 24 V DC, 0,5 A](https://www.wago.com/us/controllers-bus-couplers-i-o/8-channel-digital-output/p/750-530) |
| Abschluss | 750-600 | [Endmodul](https://www.wago.com/us/controllers-bus-couplers-i-o/end-module/p/750-600), kein zusätzlicher aktiver DI/DO-Kanalstrang |

Die Artikelnummern stammen aus dem Foto; Kanalzahl und Nennwerte aus den verlinkten offiziellen WAGO-Produktseiten. Das Foto liegt wegen sichtbarer Geräteidentitätsdaten ausschließlich privat. Öffentliche Metadaten binden die unveränderten Bildbytes durch SHA-256, enthalten aber keine Serien-/Aufklebernummern: [Evidence](../evidence/reference-module-photo-2026-10-12.json). Aufnahmezeit und Modul-Hardware-/Firmwarerevisionen sind aus dieser Frontansicht **OFFEN**. Es werden keine Revisionen aus anderen Aufkleberzahlen abgeleitet.

## Abgleich mit den früheren Cachebefunden

Der [vorherige Leselauf](real-controller-observation-2026-10-12.md) meldete zwei gecachte Terminals und Positionsrecords `[0, 0, 8, 0, 0]`, `[0, 0, 0, 8, 0]`. **HYPOTHESE, konsistent mit Foto und Herstellerangaben:** erstes I/O-Modul acht Eingänge, zweites acht Ausgänge. Der Abschluss 750-600 erklärt keinen dritten aktiven Prozessdatenrecord. Die Übereinstimmung ist keine formale Bindung von Artikelnummern an Buskennungen, DevDesc-IDs, aktive Projektknoten oder die aktuellen physischen Geräte; das fünfte Cachewort bleibt unklassifiziert.

**OFFEN:** Modulrevisionen, tatsächlich verwendete Gerätebeschreibungen, elektronische Modul-/Buskennung, aktives Anwendungs-/Prozessmapping, Parameter, Verdrahtung und erfolgreiche aktuelle zyklische Kommunikation. Das Foto beweist weder Versorgung noch Funktion oder elektrischen Sicherheitszustand. Die fortgeltende elektrische Aktortrennung bleibt eine getrennte Eigentümeraussage.

## Auswirkung auf den nächsten Arbeitsblock

Die frontseitigen Artikelnummern und fotografierte Reihenfolge sind damit keine unbekannten Inventarpunkte mehr. Der reale Minimalstrang ist jetzt **750-430 → 750-530**, mit Abschluss **750-600**. Die bisherigen 750-1405/750-1504 bleiben ein anderer eigener 16-Bit-Modell-/Mappingkandidat.

Als unabhängige Offlinearbeit sind für 750-430/750-530 die authentischen Device Descriptions, Kanal-/Parameter- und Prozessdatenverträge zu lokalisieren und mit dem vorhandenen FW31-Verbraucher zu verbinden. Aus acht Kanälen darf nicht ungeprüft das vollständige ADI-Prozessabbild, eine Buskennung oder ein Mappingoffset abgeleitet werden. Die 2-Byte-Packung, Sequenzialität und Watchdogpolitik des vorhandenen Eigenadapters werden durch das Foto nicht bestätigt und hier nicht umgebaut.

Die [Versuchsgrenzen](real-controller-plan-2026-10-12.md) bleiben bestehen: gelöschtes Runtime-Arbeitsverzeichnis, ungesicherte RAM-Anwendung, fehlender vollständiger Ersatz-/Parallelvertrag und separat freizugebender Provider-/Buswechsel. **NOT_RUN:** Geräte-/VM-Zugriff, Adapteränderung, Runtime-Neustart, Download, elektrische Tests oder neue Original-I/O-Abnahme in diesem Fotonachtrag. Frühere PASS bleiben an den früheren Stand gebunden. Kein Merge.
