> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-064 — `effective_outputs` Quellenanalyse

## Ergebnis

**VERIFIZIERT (statische Quelltextbeobachtung, begrenzt auf die vorgegebenen Dateien):** Im sichtbaren normalen Kontrollfluss kann `effective_outputs` nur an `adapter_write_end` einen möglicherweise von null verschiedenen Wert erhalten (C-Datei Zeile 549). Diese Zuweisung schreibt `staged_outputs` genau dann, wenn `effective_permit()` wahr ist. Das Prädikat verlangt gleichzeitig `app_running`, `permit`, `watchdog_healthy` und `!fault_latched` (Zeilen 150–153). Daher ist im analysierten Quelltext kein Pfad gefunden, der einen nichtnulligen Wert publiziert, während eines dieser vier Gates falsch ist.

**VERIFIZIERT (statische Quelltextbeobachtung):** Jede sichtbare Mutation, die eines dieser Gates auf falsch setzen kann, setzt `effective_outputs` im selben unter `state_mutex` serialisierten Aufruf auf null: Permit-Setter (Zeilen 242–250), beide App-State-Einstiege (253–265, 679–691), Watchdog-Ablauf (128–135) und Watchdog-Start/Stop (814–839). Der Fault-Latch setzt Fault und effektive Ausgänge gemeinsam (155–159); alle sichtbaren Fehlerpfade, die Fault setzen, laufen über ihn. Init, Exit, Reset und Close löschen den Zustand beziehungsweise den Wert (201–208, 289–323, 356–376). Für diese sichtbaren Übergänge wurde kein stale nichtnulliger `effective_outputs`-Wert nach Gate-Verlust gefunden.

**Einschränkung der Aussage:** Das ist eine manuelle Def/Use- und Pfadbedingungsanalyse des exakt gehashten C-Quelltexts, kein Laufzeit-, Compiler-, Binär-, ABI- oder Hardwarebeweis. Die Aussage gilt unter der Annahme regulärer, definierter C-Ausführung und dass alle Zugriffe auf das statische `state` über die sichtbaren Funktionen erfolgen. Der Mutex serialisiert die sichtbaren State-Operationen; eine externe Speicherbeschädigung, undefiniertes Verhalten oder nicht sichtbarer Code außerhalb des abgegrenzten Callgraphs wurde nicht bewiesen oder ausgeschlossen.

## Datenfluss und Publikationspfade

- `effective_permit()` ist die einzige positive Gate-Prüfung: `app_running && permit && watchdog_healthy && !fault_latched` (150–153).
- `adapter_write_start` verlangt `ready_device(id)` (initialisiert, geöffnet, konfiguriert), kopiert nur `requested_outputs` nach `staged_outputs` und startet die Transaktion (137–141, 456–468).
- `adapter_write_bytes`, `adapter_write_bit` und `adapter_write_bool` ändern nur `staged_outputs` und die Touch-Maske (470–530); sie publizieren keine effektiven Ausgänge.
- `adapter_write_end` prüft Bereitschaft und Transaktionsbesitz, verwirft fehlerhafte/unvollständige Frames, aktualisiert bei vollständigem Frame `requested_outputs`, und schreibt dann `effective_outputs = effective_permit() ? staged_outputs : 0u` (532–554). Ein von null verschiedener Wert ist somit nur bei erfülltem Gate möglich. `staged_outputs` stammt aus dem angefangenen Transaktionsframe; das Profilmaskieren und Vollständigkeitskriterium sind Modellregeln, keine Aussage über Herstellersemantik.
- Snapshot/Getter lesen den Wert nur (177–189, 280–287). Die Model-Bridge hat in diesem Quelltext keinen direkten Schreibzugriff auf `state`; öffentlich sichtbare Setter durchlaufen dieselbe Sperre.
- `requested_outputs` wird nur bei erfolgreichem vollständigem `WriteEnd` aktualisiert (547); Close setzt es auf null (371), Init/Exit/Reset löschen es mit `memset`. Fehlerhafte oder unvollständige Enden stellen nur den Staging-Wert wieder her (537–545). `requested_outputs` kann daher absichtlich von `effective_outputs` abweichen.

Vollständige Fundstellen direkter Zuweisungen und Gate-Mutationen stehen in [effective-output-paths.tsv](effective-output-paths.tsv).

## Übergänge und Fehlerfälle

| Pfad | Sichtbare Wirkung auf effektive Ausgänge | Ergebnis für stale Werte |
|---|---|---|
| Init | `memset(state, 0, ...)`, anschließend `initialized=true`, Watchdog unhealthy (299–304) | Null; wiederholtes Init schlägt fehl, ohne Zustand zu ändern (295). |
| Exit | Generation erhöhen und `memset` (314–317) | Null; bei nicht initialisiertem Zustand Fehler ohne Mutation (314). |
| Reset | Watchdog refresh, dann Generation erhöhen und `memset` (201–208) | Null. |
| Close | Bei erfolgreicher Schließung werden `app_running`, `permit`, Watchdog und Ausgänge gelöscht (356–376) | Null. Ungültige ID, nicht geöffnet oder aktive Read/Write-Transaktion: Fehler vor Änderungen, daher kann ein zuvor gültiger Wert bestehen bleiben (359–361); das ist kein erfolgreicher Lifecycle-Übergang. |
| Fault / Modellfehler | `latch_fault_locked()` setzt Fault und Ausgänge auf null (155–159); u. a. ungültige Write-/Read-Argumente sowie nicht unterstützte oder fehlerhafte Device-Specific-Aufrufe rufen es auf | Kein stale Wert nach einem tatsächlich gelatchten Fault. Ein bloß zurückgegebener Fehler, der den Latch nicht ausführt, ändert den Wert nicht. |
| Permit wird false | Permit wird gesetzt, danach wird bei falschem Gesamtgate der Wert null (242–250) | Kein stale Wert. Permit wird true setzt den Wert nicht wieder her. |
| App läuft nicht | App-State-Setter setzt Status und nullt bei falschem Gesamtgate (253–265, 679–691) | Kein stale Wert. Wechsel auf Running publiziert nicht erneut. |
| Watchdog-Ablauf | Refresh setzt `watchdog_healthy=false` und Ausgänge null (128–135) | Kein stale Wert nach einem beobachteten Ablauf. Zeit wird bei den öffentlichen/Interface-Aufrufen aktualisiert; ohne Aufruf ist die gespeicherte Momentaufnahme nicht aktiv neu berechnet. Getter/Snapshot rufen Refresh vor dem Lesen auf. |
| Watchdog Start/Stop | Erfolgreicher Start setzt unhealthy und null; Stop ebenfalls (814–839) | Kein stale Wert. Trigger setzt healthy/deadline, aber publiziert keinen Output (841–851). |
| Configure erfolgreich | Setzt `configured=true`, löscht Fault, schreibt `effective_outputs` nicht (430–454) | Kein neuer nichtnulliger Wert. Bereits vorhandener Wert bleibt erhalten, sofern er vorher nicht durch Fault oder Gate-Verlust genullt wurde. Configure selbst ist kein Gate im `effective_permit`; `configured` ist jedoch notwendige Write-End-Bereitschaft. |
| Configure ungültig | Bei geöffnetem Gerät und fehlerhaften/unsupported Daten wird Fault gelatcht (435–449) | Wert wird null. Ungültige ID oder nicht geöffnet kehrt vor Latch zurück (433–434) und erhält den bisherigen Zustand. |
| ConfigureSubdevice | Stets Fehler; nur Watchdog-Refresh davor (420–428) | Kein eigener Gate-/Output-Wechsel; kann vorhandenen Wert erhalten, sofern Refresh keinen Ablauf erkennt. |
| Sonstige Fehler | Viele Argument-, Zustands- oder Slotfehler kehren ohne Fault-Latch zurück | Ein gültiger bisheriger Wert kann bestehen bleiben. Das ist keine Publikation eines neuen Werts bei falschem Gate. Beispiele: ungültiger App-Enumwert (256–258, 682–684), fehlgeschlagener Watchdog-Set-Time/Start ohne Übergang (806–808, 817–821), falsche Write-Task/Ownership (459, 475, 500, 518, 535–536). |

Die Fault- und Gate-Mutationen sind in einer gemeinsamen Sperre ausgeführt. Schreibtransaktionen werden zusätzlich bei Permit-/App-/Watchdog-/Fault-Änderungen als fehlgeschlagen markiert, falls aktiv. Ein fehlgeschlagener oder unvollständiger `WriteEnd` publiziert nicht; Fault wird bei Unvollständigkeit gelatcht, und ein schon fehlgeschlagener Frame wird verworfen (537–545).

## Status, Tooling, Inputs und Restunsicherheit

- **VERIFIZIERT:** Die aufgeführten direkten Zuweisungen, Lesestellen und Bedingungen stehen in den angegebenen Quellzeilen.
- **VERIFIZIERT, statisch begrenzt:** Kein sichtbarer positiver Publikationspfad ohne alle vier Modellgates; Gate-Verlustpfade nullen den gespeicherten Wert.
- **OFFEN:** Laufzeitverhalten des gebauten Artefakts, Optimierer-/Compiler-Verhalten, ABI-Aufrufdisziplin und Verhalten außerhalb der bereitgestellten Quelle. Diese Analyse erhebt keinen unbeschränkten symbolischen Beweis.
- **Tests: NOT_RUN.** Keine Tests, Builds, Binaryläufe, Geräte-, Netzwerk-, VM-, Runtime- oder Herstellersemantik-Prüfungen durchgeführt.
- **Tooling:** GNU bash 5.2.37; ripgrep 15.2.0; GNU coreutils `sha256sum` 9.7. Nur Dateilesen, Hashprüfung und Textsuche; keine Test-/Build-Tools ausgeführt.
- **Alternativerklärung / Alias und Concurrency:** `state` ist statisch und wird in diesem File nur unter `STATE_GUARD` gelesen/geändert; Bridge-Snapshot gibt Kopien aus. Die sichtbaren Aufrufe sind durch `state_mutex` serialisiert. Falls nicht sichtbarer Code Speicher überschreibt, außerhalb der API auf Daten zugreift oder undefiniertes Verhalten vorliegt, gilt die Invariante nicht als nachgewiesen. Der ausgelieferte Binärstand könnte von diesen Eingabe-Hashes abweichen.
- **Worker-Self-Review:** Selbstprüfung der Fundstellen durch `rg`-Inventar plus zeilenweise Sichtprüfung; kein unabhängiger Review. Die Eingabe-Hashes wurden gegen die Vorgaben abgeglichen. Ausgabedateien und ihre Hashes werden separat in `sha256sums.txt` protokolliert.

## Eingabedateien

Die exakten Pfade, Bytes und SHA-256-Werte stehen in [inputs.tsv](inputs.tsv). Alle drei Werte stimmen mit den im Auftrag genannten Hashes überein.
