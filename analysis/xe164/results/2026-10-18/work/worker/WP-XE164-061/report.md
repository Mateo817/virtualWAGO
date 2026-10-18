> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-061 — ADI-Slot-Implementierung im begrenzten Digitalvertrag

## Ergebnis

**VERIFIZIERT (Source-Level, begrenzter Scope):** Der aktuelle eigene Adapter initialisiert alle 34 ADI-Slots eindeutig mit einer Funktion. Die 22 `VERIFIZIERT`-Marker und 12 `OFFEN`-Marker stimmen exakt mit WP-XE164-057 überein. Jeder der 22 beobachteten Slots ist implementiert. In der geprüften Quelle wurde keine Abweichung vom akzeptierten, begrenzten Vertrag in WP-XE164-060 gefunden.

Das Ergebnis ist keine ABI- oder Vendorsemantik-Zertifizierung. Die Quelle bezeichnet den Adapter ausdrücklich als eigenes In-Memory-Modell. Profile, Fail-Closed-Gate, Watchdog-Uhr, Diagnoseabbild und nicht beobachtete Slotsemantik bleiben Modellpolitik. Es wurde weder gegen private Herstellerheader kompiliert noch Laufzeitverhalten geprüft.

## Beobachtungen

- Die Eingabedateien stimmen in SHA-256 und Byte-Größe mit dem Arbeitsauftrag überein; Details stehen in `inputs.tsv`.
- `interface_table` weist Slots 0–33 in Reihenfolge explizit zu: `tools/adi_digital_adapter.c:854-889`. Es gibt keine ausgelassenen oder doppelten designated initializer in dieser Tabelle.
- Die WP057-Marker sind 22 `VERIFIZIERT` und 12 `OFFEN`. Genau diese Marker stehen pro Slot in `slot-implementation.tsv`; insbesondere slot 29 bleibt gemäß WP057 markiert, obwohl sein FW31-Aufrufprovenienzbeleg dort begrenzt ist.
- Slot 29 (`VCallDeviceSpecificFunction`) reicht `name`, `ret` und dieselbe `va_list args` ohne Rekonstruktion an `device_specific` weiter und gibt dessen äußeres Resultat direkt zurück (`tools/adi_digital_adapter.c:795-800`). Die gemeinsame Behandlung konsumiert Argumente namensspezifisch mit `va_arg`, schreibt gegebenenfalls innere Rückgabewerte und setzt in Modellfehlerfällen das eigene Fault-Latch (`:715-782`). `va_start`/`va_end` gehören nur zur variadischen Slot-28-Wrapperfunktion (`:784-793`). Das deckt den in WP057 begrenzten Forwarding-Befund ab; Argumentliste, genaue FW31-Callsite und weitergehendes `va_list`-Verhalten sind damit nicht belegt.
- Die observed Lebenszyklus-, Listen-, Öffnen-, Konfigurations-, Zyklus-, Diagnose-, Zustands-, Dispatch- und Watchdog-Slots haben zugewiesene Funktionen; Detailbedingungen und Mutationen stehen in der TSV.
- Alle 12 laut WP057 nicht direkt beobachteten Slots sind ebenfalls initialisiert. Fünf davon sind explizite Fehler-Stubs: ConfigureSubdevice, Diagnose-Subdevice, RegisterEventHandler, UnregisterEventHandler und GetLastError (Slots 10, 23–26). Die übrigen liefern eigenes modelliertes Verhalten. Das belegt keine Erreichbarkeit oder Kompatibilität auf nicht beobachteten Pfaden.

## Abweichungen und priorisierte Kandidaten

**Bestätigte Vertragsabweichungen: keine gefunden.** Die WP060-Mindestanforderungen passen auf Source-Level zum Code: stabile eigene DeviceId und begrenzte Ein-Geräte-Liste; einzig beobachtete Typ-III-Konfiguration mit TCM 0; begrenzte digitale Ein-/Ausgabeprofile; getrennte requested/effective outputs; explizites Diagnose-/Fault-Modell; begrenzte Dispatch-Untermenge und unbekannte Operationen werden abgewiesen. Das sind Strukturvergleiche, keine Laufzeitnachweise.

**P1 — Dispatch-Statuspfade als offene Kompatibilitätsstelle, keine bestätigte Abweichung.** `device_specific` liefert bei unterstützten Namen äußeren `DAL_SUCCESS`, während Statuswerte teilweise in `return_value` liegen; UID/Config-Register werden als innerer Wert `-1` abgewiesen (`:721-781`). WP057 belegt für terminal-info32 eine Consumer-Prüfung des inneren Werts und beschreibt für andere Namen teils offene Ergebnisinterpretation. WP060 lässt UID/Register- und Push-Handlersemantik ausdrücklich offen. Falls ein beobachteter Consumer nur den äußeren Status oder andere Rückgabepointerkonventionen prüft, könnte das abweichen; die akzeptierte Evidence reicht nicht für die Einstufung als Fehler.

**P2 — `VCall`-ABI und Lebensdauer sind nicht zertifiziert.** Der direkte Forwarder ist sichtbar und stimmt mit der bounded forwarding observation überein (`:795-800`), aber ein Source-Review kann weder private Header-Signatur/Compiler-ABI noch Consumer-Aufrufkonvention oder Inhalt/Lebensdauer der Argumentliste bestätigen. Keine belegte Abweichung.

**P3 — Nicht beobachtete Slots haben teils nur Modell- oder Fehlerpfade.** Bool-Varianten, Namen/Flags/Größen, Close/Open-Status, Subdevice-, Event- und Last-Error-Slots sind Tabellen-implementiert, aber WP057 markiert sie als `OFFEN`. Das verletzt den begrenzten beobachteten Digitalvertrag nicht; ihre Nutzung durch weitere Komponenten bleibt unbewiesen.

## Status, Alternativerklärung und Restunsicherheit

- **Status:** `VERIFIZIERT` für eindeutige Initialisierung und Source-Verhalten innerhalb der hier verglichenen Grenzen; `OFFEN` für ABI-Korrektheit, nicht beobachtete Callpaths, genaue Dispatch-Resultatverträge und Laufzeitfehlerreaktionen. Keine `BLOCKED`-Bewertung erforderlich.
- **Alternativerklärung:** Ein scheinbar unterstützter oder abgelehnter Slotpfad kann ausschließlich eine bewusste Policy des eigenen Simulators darstellen. Die Kommentare und Header kennzeichnen dies an zentralen Stellen als Modell, nicht als Herstellerverhalten. Ebenso folgt aus statischer Consumer-Beobachtung kein Nachweis, dass ein erfolgreicher Originalstack-Pfad zur Laufzeit jede einzelne Slotfunktion aufgerufen hat.
- **Restunsicherheit:** Keine Prüfung privater Header, Compiler-Layout, ARM32-Aufrufkonvention, dynamischer Originalstack-Fehlerpfade, Callback-Kontrakte oder Laufzeittraces. Die source-level Abdeckung sagt nichts über vollständige Hardware-/XE164-Äquivalenz.

## Prüfstatus und Werkzeuge

- Eingabehashes/-größen: **PASS**.
- TSV-Reconciliation: **PASS** — 34 eindeutige Slotnummern 0–33, genau 22 `VERIFIZIERT`- und 12 `OFFEN`-Marker gemäß WP057, alle observed Zeilen mit Implementierungsfunktion und Sourcezeilen.
- Kompilierung, Tests, Geräte-, Netzwerk-, VM- oder Runtime-Prüfung: **NOT_RUN** gemäß Arbeitsumfang.
- **Worker-Self-Review:** Die Schlussfolgerung beschränkt sich auf die vier gehashten Eingaben und sichtbaren C-Quelltext. Modellpolitik wurde nicht als Vendorvertrag ausgegeben; offene Evidence wurde nicht in eine bestätigte Abweichung umgedeutet. Keine unabhängige Prüfung behauptet.
- Toolversionen: GNU coreutils `sha256sum 9.7`; mawk `1.3.4 20250131`; ripgrep `15.2.0`. Quelltextzeilen wurden mit `nl -ba` referenziert. Keine Binäranalyse/REA.

## Erzeugte Dateien und Prüfsummen

`sha256sums.txt` listet SHA-256 für `report.md`, `slot-implementation.tsv` und `inputs.tsv`; die Prüfsumme des Manifests selbst wird bewusst nicht in sich selbst eingetragen. Es wurden ausschließlich Dateien im WP-XE164-061-Ausgabeverzeichnis erzeugt.
