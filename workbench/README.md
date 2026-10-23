# virtualWAGO Simulationswerkstatt

Lokale Offline-Anwendung mit Rust-Kern und Weboberfläche. Module grafisch
zusammenstellen, Testausgänge vorgeben, Eingangssignale beobachten und
Reaktionen skripten. Keine WAGO-/CODESYS-Verbindung, keine VM-Nutzung.

## Start

Linux x86_64, Rust 1.99.0 und Node 24.21.0/npm 11.19.0 sind die geprüfte
Entwicklungsumgebung. Alle Abhängigkeiten stehen in den beiden Lockdateien.
Vom Repositoryroot:

```sh
cd workbench/web
npm ci --ignore-scripts
npm run build
cd ..
cargo run --locked
```

Danach [http://127.0.0.1:8787](http://127.0.0.1:8787) öffnen.
Der Server lauscht ausschließlich auf Loopback; es gibt kein `--host`-Argument.
Eigener Port: `cargo run --locked -- --port 8788`.
`--state-dir PATH` wählt das private Projektverzeichnis, `--assets PATH` die
gebauten Webdateien. Ohne Optionen liegen sie in `workbench/state/` und
`workbench/web/dist/`; beide Verzeichnisse sind nicht versioniert.

Zum Entwickeln baut `npm run dev` die statischen Dateien bei Änderungen erneut.
Die Oberfläche weiterhin über den Rustserver öffnen. Kein separater Node-Dienst
und keine Lockerung der Browser-Originprüfung erforderlich.

## Bedienung

1. Ein Modul aus dem Katalog hinzufügen. Reihenfolge per Drag-and-drop oder den
   Links-/Rechts-Schaltflächen der Eigenschaften ändern. Instanz-IDs bleiben
   erhalten; Bezeichnungen sind frei wählbar.
2. Änderungen sind Entwürfe. **Übernehmen** validiert und speichert das gesamte
   Projekt; Fehler lassen das aktive Projekt unverändert. Vorher pausieren.
   Jede Aktivierung beginnt bei Modellzeit 0 und geschlossener Freigabe.
3. Im ausgewählten Ausgang einen **Testwert** vorgeben. **Modellfreigabe**
   einschalten, anschließend **Start** oder **Einzelschritt** ausführen.
4. Das Beispiel `Ventilrückmeldung` liest DO1 und liefert DI1. Bei geschlossenem
   Gate bleibt der wirksame Ausgang 0, auch wenn die Anforderung 1 ist.
5. **Pause** friert Modellzeit/Reaktionen ein; **Stopp** entzieht zusätzlich die
   Freigabe. **Zurücksetzen** löscht auch Zeit, Fehler und transiente Werte.

Projekt-Export enthält Module, exakte Paketversionen und Skripte. Er enthält
keine laufenden Werte oder automatisch wiederherzustellende Freigaben. Import
lädt zuerst einen geprüften Entwurf; Aktivierung erfolgt mit **Übernehmen**.
Ein Browser-Neuladen übernimmt bestätigte Testbefehle nicht erneut.

## Reaktionsskripte

Rhai ist eine eingebettete Sprache. Jedes Skript bindet optional einen Ausgang
und genau einen Eingang. Es liefert ausschließlich den neuen Eingangswert:

```rust,ignore
fn react(output, previous, dt_s, time_s) {
    // Beispiel: träge Rückmeldung von 4 bis 20 mA auf 0 bis 10 V.
    let target = 4.0 + output * 1.6;
    previous + (target - previous) * dt_s / (1.0 + dt_s)
}
```

`output`: wirksamer Ausgang oder 0 bei reinem Zeitmodell.
`previous`: letzter Eingangswert. `dt_s`: Modellschritt in Sekunden.
`time_s`: Modellzeit am Beginn des Schritts. Rückgaben müssen endliche Zahlen
im Zielbereich sein; digitale Eingänge akzeptieren nur 0 oder 1.

Alle Skripte lesen denselben alten Zustand. Erst nach vollständiger Prüfung
werden ihre Ergebnisse gemeinsam übernommen. Fehler entziehen das Gate und
verriegeln den Lauf, ohne einen halben Eingangsframe zu übernehmen. Rückweg:
Skript im pausierten Entwurf korrigieren und übernehmen oder zurücksetzen.
Eigene `.rhai`-Dateien lassen sich im Skripteditor laden und wieder exportieren.

Kein Skript darf Ausgänge schreiben, Dateien/Netze/Prozesse öffnen, Module
importieren oder Hostzeit abfragen. Globale Anweisungen werden nicht ausgeführt.
Es gelten 20.000 Operationen pro Aufruf sowie Größen-/Tiefengrenzen. Ein aktives
Skript besitzt seinen Eingang exklusiv. Das ist ein begrenztes Reaktionsmodell,
keine allgemeine Python-/JavaScript-Laufzeit und keine SPS-Steuerlogik.

## Nachladbare Module und Übergabe an die Modellentwicklung

[Paketvertrag](../docs/workbench-module-contract.md),
[Architekturentscheidung](../docs/adr-0013.md) und
[Folgearbeit](../docs/workbench-handoff.md) sind der Einstieg für den nächsten Agenten.
Die sieben gebündelten Beispiele liegen in `module-packs/`. Pakete können als
JSON über **Modulpaket laden** importiert werden; das erfordert keinen neuen
Produktbuild, solange sie unterstützte Kanalcodecs verwenden.

Die Module besitzen eigene Signalmodelle. Rohcodes sind keine native ADI-Lage,
Register-/Diagnoseemulation oder Hardwarequalifikation. 750-466 ist auf normale
4–20 mA begrenzt; 750-550 auf normale 0–10 V. Spezialvarianten, PWM, CAN/DALI
und Serial werden durch diese Werkstatt nicht zusätzlich freigeschaltet.

## Prüfungen

Vom Repositoryroot:

```sh
cargo fmt --manifest-path workbench/Cargo.toml --check
cargo test --manifest-path workbench/Cargo.toml --locked --all-targets
cargo build --manifest-path workbench/Cargo.toml --locked
cd workbench/web
npm ci --ignore-scripts
npm run build
npx playwright install chromium
npm test
```

Browserprüfungen verwenden ausschließlich eigene Loopbackserver und temporäre
Projekte, keine Referenzgeräte. Sie testen die gebauten statischen Dateien mit
dem echten Rustdienst. Die Pythonvergleichsdaten in `tests/fixtures/` stammen aus
den öffentlichen Modellfunktionen, nicht von Hardware. Die bestehende
Python-Forschungssuite und ihre CI bleiben getrennt bestehen.
