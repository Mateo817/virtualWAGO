# Werkstatt: Modul-, Projekt- und Reaktionsvertrag v1

Scope: eigenes Offline-Signalmodell gemäß [ADR-0013](adr-0013.md).
Keine native ADI-Struktur, K-Bus-Typkennung oder Hersteller-ABI daraus ableiten.
Die verbindliche maschinenlesbare Implementierung ist
`workbench/src/model.rs`; unbekannte Felder und Varianten werden abgewiesen.

## Modulpaket

Ein Paket hat `schema: 1`, stabile `id`, eigene Modell-`version`, `article`,
`title`, `family`, `description`, `evidence`, `assumptions` und `channels`.
`version` ist keine Firmware- oder physische Modulrevision. Familien sind
`di`, `do`, `ai`, `ao`, `passive`. Passive Pakete haben keine Kanäle; alle
anderen 1–64. Ein Kanal besitzt:

| Feld | Vertrag |
|---|---|
| `id`, `label` | stabile Kennung und veränderbare Bezeichnung |
| `direction` | `input` oder `output`, passend zur Familie |
| `kind` | `digital` oder `analog` |
| `unit`, `min`, `max`, `initial` | Einheit, endliche Grenzen und Anfangswert; Ausgänge starten bei 0 |
| `encoding` | `codec` plus ausschließlich die zur Variante gehörenden Felder |

Codecs: `bit` (0/1), `ai466_standard` (4–20 mA → Normbereichs-WORD),
`ao550_standard` (0–10 V → approximierte inverse Normbereichsquantisierung),
`linear` (`scale`, `offset`, `max_raw`, gerundet und auf den Rohbereich begrenzt).
Der lineare Codec ist eine explizite Eigenmodellpolitik und kein Herstellerprofil.
Skalierungsänderungen verlangen neue Modellversion und entsprechende Vergleiche.

Ein fremdes Paket lässt sich mit
`POST /api/packages/validate` prüfen. Antwort: normalisiertes `package` und
`sha256`. SHA-256 bezieht sich auf die kompakte, durch Rusts Structschema geordnete
JSON-Serialisierung, nicht auf beliebig eingerückte Eingabebytes. Instanzen
binden `package` und `package_sha256`. Bei gleichem ID-Paket ersetzt die UI im
Entwurf das Paket und aktualisiert die betroffenen Pins; eine spätere Aktivierung
prüft alle Kanal-/Skriptreferenzen erneut. Alte exportierte Projekte behalten
ihre vollständigen alten Pakete.

## Projekt und Aktivierung

Projekt: `schema`, `name`, `tick_ms`, `packages`, `modules`, `reactions`.
Instanz: `id`, `package`, `package_sha256`, `label`. Instanz-IDs sind unabhängig
von der Position; Skripte binden `{module, channel}`. Höchstens 64 Instanzen,
64 Pakete, 1024 Kanäle, 32 Reaktionen und 512 KiB gesamtes JSON.

`POST /api/project/validate` prüft Schema und Skriptkompilierung ohne Aktivierung.
`PUT /api/project` nimmt `{generation, project}` an; der passende aktive Stand
muss pausiert sein. Erfolgreiche Aktivierung erhöht die Generation, speichert
Konfiguration atomar per Rename und setzt Modellzeit/Gate/Werte zurück.
Fehler bei Schema, Hashbindung, Skript oder Persistenz vor dem Rename aktivieren
keinen neuen Stand. Ein Generationenkonflikt ist HTTP 409 und wird nie automatisch
mit einem neueren Token erneut gesendet.
Nach einem bereits erfolgreichen Rename ist die Konfiguration übernommen.
Eine anschließend fehlgeschlagene Verzeichnis-Synchronisierung wird als
Warnereignis gemeldet; Kern und gespeicherte Datei bleiben auf demselben Stand,
während Dauerhaftigkeit bei Stromausfall ausdrücklich unbestätigt ist.

## Skript

Reaktion: `id`, `name`, `enabled`, `source` (Ausgang oder null), `target`
(Eingang), `code`. Funktionsvertrag und Grenzen stehen in der
[Werkstattanleitung](../workbench/README.md). Ein aktiver Eingangsschreiber ist
exklusiv. Alle Ergebnisse eines Ticks werden vor Zustandsübernahme geprüft.

## HTTP und Beobachtung

- `GET /api/bootstrap`: vollständige Projektkonfiguration und aktueller Zustand.
- `POST /api/command`: `{generation, command:{action,...}}`.
- Aktionen: `run`, `pause`, `stop`, `step`, `reset`, `permit` (`enabled`),
  `speed` (`factor`: 1–10), `set_signal` (`signal`, `value`).
- `GET /api/stream`: beobachtender WebSocket mit Zustands-Snapshots ca. alle
  100 ms. Keine Befehlsausführung über WebSocket und keine vollständige Eventqueue.
- Mutationen benötigen `Content-Type: application/json` und
  `X-VirtualWago-Client: workbench` sowie `X-VirtualWago-Instance` aus dem
  Bootstrap-Zustand. Alte Instanzkennungen werden auch nach einem Neustart bei
  wieder gleicher Generation abgewiesen. Host und gegebenenfalls Origin müssen zur
  lokalen Instanz passen. Das ist kein LAN-Authentifizierungssystem.

Snapshot: `instance`, `generation`, String-`sequence`, String-`tick`, numerische `time_ms`
(höchstens JavaScript-sicherer Integer), `running`, `permit`, `speed`, `fault`,
`signals`, höchstens 100 `events` und expliziter `scope`.
Ein Ausgang hält `requested`, `effective` und beide Rohcodes getrennt.
`source` ist `test`, `manual` oder `reaction:<id>`. Unveränderte Werte können
weiter gültige Modellsignale sein. Unterbrochene Browserverbindung ist kein
frischer Samplebeleg; die Oberfläche sperrt Bedienung und kennzeichnet alte Werte.

## Additive Erweiterungen vom 23.10.2026

[ADR-0014](adr-0014.md) ergänzt Schema 1. Fehlende Felder werden bei alten
Projekten mit `sources:[]`, `stateful:false` und `scenarios:[]` ergänzt.
Alte Binärdateien unterstützen diese Erweiterungen nicht.

Reaktion zusätzlich: `sources:[SignalRef]`, `stateful:boolean`. Insgesamt mit
`source` höchstens 16 verschiedene Ausgangsquellen. Bei `stateful:true` gilt
`react_state(outputs, previous, state, dt_s, time_s) -> #{value, state}`.
`outputs` bindet `instanz/kanal` auf wirksame Werte. `state` ist eine Map von
höchstens 16 Kennungen auf endliche Zahlen mit Betrag ≤ 1e9. Sie ist transient.
Bei `stateful:false` müssen zusätzliche `sources` leer bleiben.

Szenario: `{id,name,steps}`. Schritt: `{at_ms,permit?:bool|null,set:[],expect:[]}`.
Vorgabe: `{signal,value}`; Erwartung: `{signal,min,max,within_ms}`. Prüfsignal ist
ein Eingang. Zeitwerte liegen auf dem Projektraster, Schrittzeiten sind strikt
aufsteigend. Keine Vorgaben auf skriptgeführte Eingänge. Grenzen siehe ADR.

- `POST /api/scripts/validate`: `{code,stateful}` → `{valid,diagnostic}`;
  Diagnostic ist null oder `{message,line,column}` mit optionaler Position.
  Syntax und Signatur, keine Ausführung.
- `POST /api/scenarios/run`: `{project,id}` →
  `{id,passed,elapsed_ms,assertions,fault,samples}`. Keine Aktivierung oder
  Persistenz; frische Modellinstanz. HTTP 503, wenn bereits eine Prüfung läuft.
- Assertion: `{step,signal,min,max,deadline_ms,passed_at_ms,actual}`. `step` ist
  nullbasiert; `passed_at_ms:null` bedeutet kein Treffer. `actual` ist der letzte
  geprüfte Wert vor Treffer oder Frist. Modellfehler stoppen den Bericht mit FAIL.
- Sample: `{time,values:{"instanz/kanal":number}}`. Szenario: je Tick, bis zu acht
  Prüfsignale. Browseraufnahme: ca. 100 ms, bis zu vier Kanäle, Lücken möglich.
