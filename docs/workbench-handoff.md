# Folgearbeit: Offline-Werkstatt und Modulqualifikation

Einstieg: [Werkstatt starten](../workbench/README.md),
[ADR-0013](adr-0013.md), [Paket-/API-Vertrag](workbench-module-contract.md).

## Eigentümerscope vom 23.10.2026

Der aktuelle Auftrag erlaubt Offline-Softwarearbeit. Reale WAGOs, CODESYS und
die VM sind aktuell nicht freigegeben. Das hebt frühere zielgebundene Belege
nicht auf, erteilt aber keine neue Hardware-/Runtimefreigabe. Kein Agent darf aus
Modulnamen, Offlineprojekten oder alten Receipts aktuelle Zielzuordnung ableiten.

## Zuständigkeiten und Erweiterungsstellen

- `workbench/src/model.rs`: strikter Paket-/Projektvertrag, Signalcodierung,
  Paketdigest, stabile Referenzen. Neue unterstützte Metadaten/Skripte werden
  zur Laufzeit geladen; neue Codecs brauchen eine explizite Kernänderung.
- `workbench/src/engine.rs`: alleiniger Simulationszustand, logische Zeit,
  Schreibbesitz, Gate, atomare Reaktionsschritte und Fehlerverriegelung.
- `workbench/src/api.rs`: lokaler Webadapter, Grenzen und Persistenz.
- `workbench/web/`: modulunabhängige grafische Klemmenleiste, I/O und Skripte.
- `workbench/module-packs/`: eigene, öffentlich bereinigte Modulpakete.
- Bestehendes `prototype/` und `tools/adi_*`: Forschungs-/Originalstackpfade.
  Deren Firmware- und Runtimeevidence nicht auf den neuen Rustpfad übertragen.

## Sinnvolle nächste Modellarbeit

1. Pro Artikel die tatsächlichen Quellen, Modellannahmen und Codecgrenzen prüfen.
   Fixturevergleich gegen Python ist Softwarekonsistenz, kein Hardwarevergleich.
2. Neue Reaktionsmodelle als versionierte Pakete/Projektbeispiele ergänzen.
   Keine SPS-Entscheidungslogik nachbauen; Ausgangsreaktion und Sensoren modellieren.
3. Diagnose-, Unter-/Überbereichs- und Fehlermodelle benötigen eigene Verträge.
   Aktuelle Normbereichsprofile nicht stillschweigend erweitern.
4. PWM-Projektion, CANopen/DALI und Serial bleiben eigene Arbeitsblöcke. Nicht
   durch generische Erfolgsmeldungen oder erfundene Register/Offsets freischalten.
5. Eine spätere Originalstackbrücke benötigt einen expliziten exklusiven
   Ausgangsschreiber. Testvorgaben aus dem Browser dürfen keine parallele
   Befehlsquelle zur originalen SPS werden. Hardware-/ABI-/Zielgates gelten weiter.

## Tests und Integrationsgrenze

Die neue Rust-/Browser-CI ist hardwarefrei. Modelländerungen brauchen belastbare
Referenz-/Negativfälle, Grenzwerte und passende Projekt-/Skripttests. Stabilität,
Fehlerverhalten und Zustandserhaltung sind wichtiger als bloße Testzahlen.
Jeder PASS gilt nur für seinen geprüften Tree/Commit. Self-Review bleibt
Self-Review; kein unabhängiger Hardware- oder Agentenreview wird daraus abgeleitet.

## Ergänzte Werkzeuge für die Modulqualifikation

[ADR-0014](adr-0014.md) dokumentiert zustandsbehaftete Mehrquellenreaktionen,
Szenarien und getrennte Beobachtungsaufnahmen. Neue Erkenntnisse möglichst als
Projekt-Szenario mit positiver Prüfung, Gate-/Negativfall und expliziter Frist
ablegen. Der Bericht ist Softwaremodellevidence; die Quellen-/Hardwarestufe
weiter getrennt angeben. Beispielprüfungen: `workbench/tests/workflows.rs`.
Szenarioläufe verändern die aktive Sitzung nicht.
