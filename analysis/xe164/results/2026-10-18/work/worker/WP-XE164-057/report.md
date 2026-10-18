> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-057 — FW31 ADI/DAL Verbrauchergrenze

## Auditstatus / Revisionskorrektur

Diese Fassung korrigiert die erste Auslieferung, die auf drei Eingaben beruhte und deshalb nur 21 Slots als direkt beobachtet aufführte. Sie ist für diesen Befund **superseded**. Die verbindliche Ergänzung `docs/adi-digital8-continuation-2026-10-12.md` dokumentiert einen 22. Slot: `Dal_CallDeviceSpecificFunction` reicht die Argumentliste über `VCallDeviceSpecificFunction` weiter (`:40`). Die Matrix und Slotzählung unten enthalten diese Korrektur. Die erste Fassung bleibt im Arbeitsverlauf als Auditspur nachvollziehbar; ihre zuvor ausgegebenen Hashes gelten nicht für diese korrigierte Fassung.

## Ergebnis

**VERIFIZIERT:** Die vorgelegte statische Evidence berichtet direkte Aufrufe beziehungsweise dokumentierte Weiterleitung für 22 der 34 ADI-Slots durch die exakten FW31-Verbraucher `libIoDrvDal` und `libIoDrvKbus`: `IoDrvDal` verwendet 17 Slots, `IoDrvKbus` 11; zehn Slots sind im `IoDrvDal`-Satz zusätzlich, Slot 29 kommt als dokumentierte Weiterleitung hinzu. Die ursprüngliche Matrix beschreibt 21 Aufrufslots (`docs/adi-contract-2026-10-12.md:15-56`); die Ergänzung dokumentiert zusätzlich Slot 29 (`docs/adi-digital8-continuation-2026-10-12.md:40`). Callsites belegen Aufrufvorkommen und teilweise konkrete Kontrollflussreaktionen, aber keinen vollständigen Start-/Stop-/Nebenläufigkeitsvertrag.

Die vollständige Zeilenmatrix steht in [boundary-static.tsv](boundary-static.tsv). Sie führt alle 34 Header-Slotpositionen auf, markiert jeden Eintrag als **VERIFIZIERT** oder **OFFEN** und trennt direkten FW31-Verbraucherbefund von Provider-, Header- und Eigenmodellbefunden. Direkte Calls sind an die FW31-Dateihashes gebunden, die im Vertragsbericht `:11` und im Validierungs-JSON unter `/reference_refresh/original_hashes` stehen. Die FW30-Header liefern Slotnamen, Signaturen und Offsets, nicht den Nachweis, dass FW31 mit diesen Headern gebaut wurde (`adi-contract-2026-10-12.md:9-13,17-19`).

Konkret direkt beobachtet sind:

- Init, ScanDevices, GetDeviceList, OpenDevice, Exit und ApplicationStateChanged in `IoDrvDal`.
- ConfigureDevice, zyklische Kbus-Lese-/Schreibpfade und Diagnose in `IoDrvKbus`; generische Read-/Write-Aufrufe auch in `IoDrvDal`.
- Alle vier Watchdog-Slots in `IoDrvDal`.
- CallDeviceSpecificFunction in `IoDrvKbus`; eine Teilmenge der Namen und Handlerreaktionen ist zusätzlich an die exakten FW31-`libpackbus`-Bytes gebunden.

Nicht direkt belegt sind unter anderem CloseDevice, IsDeviceOpen, GetDeviceName/Flags/IoSizes, ConfigureSubdevice, Bool-Transfers, Subdevice-Diagnose, Register/UnregisterEventHandler und GetLastError. Diese Slots bleiben **OFFEN** für die beiden untersuchten Verbraucher; die Abwesenheit aus den erfassten Callsites beweist keine allgemeine Nichterreichbarkeit (`adi-contract-2026-10-12.md:17,25-31,35,40,44-50,56`). Slot 29 ist jetzt **VERIFIZIERT** ausschließlich für die in der Fortsetzung genannte Argumentlisten-Weiterleitung. Die Fortsetzung nennt dafür keinen Binärhash und keine address-level Callsite, obwohl sie auf separate Evidence verweist; diese Details bleiben **OFFEN**.

## Lifecycle-, Fehler- und Beweisgrenzen

`IoDrvDal` enumeriert mit Kapazität 10, sucht einen passenden Gerätenamen, öffnet das Gerät und hält die erhaltene DeviceId im Native-Driver-Objekt. Seine beobachteten zyklischen Start-, Transfer- und End-Rückgaben werden ignoriert. Der Kbus-Verbraucher wertet Start- und Datenoperationsfehler über beobachtete Fehlerzweige aus; ReadEnd/WriteEnd werden aufgerufen, aber ihr Ergebnis wird verworfen beziehungsweise der vorherige Status wiederhergestellt. Daraus folgt keine End-Fehlerreaktion. Diese Befunde und ihre Grenzen sind in `adi-contract-2026-10-12.md:69-73` beschrieben.

Der Aufruf `ConfigureDevice` in Kbus übergibt ein 12-Byte-Objekt mit Typ-III-Discriminator, runtimeabhängigem Steuerwort und falschem Flag. Die Bytes und der FW30-Typ-III-Abgleich belegen diese konkrete Callsite, nicht alle Konfigurationspfade oder die Zulässigkeit des eigenen Modellwerts (`adi-contract-2026-10-12.md:79`). Diagnosecalls und ein Zweig, der erfolgreiche Diagnose plus erwarteten Buszustand vor Modulsuche verlangt, sind beobachtet; das vollständige Fehler-zu-CODESYS-Status-Mapping bleibt offen (`:73`).

Providerverhalten ist separat zu lesen: Das untersuchte `libdal.so.1.0.1` ist laut Bericht byteidentisch mit dem gebundenen FW30-SDK-Provider (`adi-contract-2026-10-12.md:9`). Nur für diesen Provider sind unter anderem Entry-Kapazität/Begrenzung bei GetDeviceList, Überlauf-/Extent-Prüfungen für ReadBytes/WriteBytes, GetDeviceName-Pufferverhalten sowie Event-Handler-Weiterleitung statisch berichtet (`:62-68`). Das ist kein FW31-Header- oder FW31-Providerbeleg und kein Nachweis, dass die betreffenden FW31-Consumer-Slots aufrufen.

Die FW30-Headeraussage zu Statuswerten (`DAL_FAILURE=-1`, `DAL_SUCCESS=0`, `DAL_NOTUSED=1`) bleibt historische Header-Evidence (`:60`). Sie wird nicht auf jede beobachtete FW31-Rückgabebehandlung übertragen. Bei `CallDeviceSpecificFunction` sind nur die separat ausgewiesenen exakten FW31-`libpackbus`-Deskriptoren/Handler für Teiloperationen als Providerbytes behandelt; der Consumer-Call allein bestimmt weder Variadic-Argumentvertrag noch innere Ergebnissemantik (`:75-81`).

Eigenmodell und Eigenharness bleiben eine eigene Evidence-Stufe. Die dortigen Prozessabbildlängen, deterministischen Read-/Write-Frames, Output-Gates, Watchdogpolitik sowie Close/Reopen-Verhalten sind Modellpolitik; der Harness ist kein Beleg für Originalverbraucherannahme, Geräteverhalten oder Hersteller-Lifecycle (`adi-contract-2026-10-12.md:90-92`; `originalstack-block-2026-10-12.md:34-40`; JSON `/own_adapter`).

## Alternativerklärung und Restunsicherheit

Eine nicht beobachtete Slotnutzung kann schlicht außerhalb der untersuchten `libIoDrvDal`-/`libIoDrvKbus`-Callsites liegen, beispielsweise in einer anderen Komponente oder einem nicht analysierten Pfad. Darum lautet der Status für die genannten fehlenden Callsites **OFFEN**, nicht „ungenutzt“. Ebenso können beobachtete Aufrufe in einem anderen Runtimepfad oder Zustand liegen als die tatsächlich ausgewählte Anwendung; die Unterlagen nennen die Bindung der Offlinekonfiguration an den ausgewählten originalen Start-/Hook-/Scanpfad ausdrücklich als Restpunkt (`originalstack-block-2026-10-12.md:52-57`; JSON `/remaining_gates/original_consumer`).

Nicht geschlossen sind Caller-/Hook-Auswahl und vollständige Lifecycle-Reihenfolge, Push-Ergebnisinterpretation und aktive Terminalauswahl, zusätzliche Opcode-Erreichbarkeit, Callback-Threading/Reentrancy/Lebensdauer, echte Parallelitäts- und Synchronisationsgarantien sowie die vollständige Dienst-/Runtimeauflösung. Die Quellen sagen ausdrücklich, dass untersuchte Aufrufstellen keine vollständige Start-/Nebenläufigkeitsgarantie liefern (`adi-contract-2026-10-12.md:56,81,85,93`; `originalstack-block-2026-10-12.md:54-57`; JSON `/remaining_gates`).

## Eingaben, Methoden und Status

Vor dem Lesen jeder Eingabe wurden Größe und SHA-256 mit `wc -c` und `sha256sum` geprüft. Die ersten drei Eingaben wurden vor der ersten Fassung gebunden; die Fortsetzung wurde vor dieser Korrektur separat gebunden. Alle vier erwarteten Größen und Hashes stimmten überein:

| Eingabe | Bytes | SHA-256 |
|---|---:|---|
| `docs/adi-contract-2026-10-12.md` | 23771 | `c3133e5269de7be5ac887ea1c126fde72b97ef9224b25f582b678446dcd9db9d` |
| `docs/originalstack-block-2026-10-12.md` | 9336 | `929d031611751b44c7cfbdf984907a7f6857b6604879b68049c631cb3d8c7125` |
| `evidence/originalstack-block-validation-2026-10-12.json` | 9256 | `28726b73319c155e1846df29170de6f425fef0b21272ddd592996cfb08ee17ac` |
| `docs/adi-digital8-continuation-2026-10-12.md` | 7912 | `defe2e9da7e747674f32d37a9e17ff3bbfd52167b1d9405358263d9878f367c8` |

Verwendete lokale Werkzeuge: GNU bash 5.2.37, GNU coreutils `sha256sum` 9.7, `wc` 9.7, GNU sed 4.9, GNU `nl` 9.7. Die Analyse war reine statische Dokument-/Evidence-Reconciliation. Keine Repositorydatei wurde geändert; es gab keine Binär-, Geräte-, Netzwerk- oder VM-Aktion.

**PASS — Eingabehash-/Größenkonsistenz.** **PASS — Matrixkonsistenz:** 34 Datenzeilen, je eine für ADI-Slot 0 bis 33, eindeutige Slotnummern; genau 22 Zeilen tragen den direkten Verbraucherstatus VERIFIZIERT, einschließlich der ausschließlich als Argumentlisten-Weiterleitung dokumentierten Slot-29-Zeile. Diese Status gelten ausschließlich für Eingabebindung und Tabellenvollständigkeit; es wurde kein Runtime- oder Hardwareverhalten getestet.

Reviewstatus: **Worker-Self-Review**, nicht unabhängig. Der übergeordnete Integratorbericht nennt separate frühere Reviews, aber diese Arbeit beansprucht sie nicht als Review dieses Work Package (`originalstack-block-2026-10-12.md:48`; JSON `/reviews`).

## Erzeugte Dateien

| Datei | Inhalt |
|---|---|
| `report.md` | Befund, Fundstellen, Grenzen, Methodik und Reviewstatus; SHA-256 wird im Handoff genannt |
| `boundary-static.tsv` | 34 zeilenweise ADI-Slot-/Operationseinträge; der aktuelle SHA-256 steht in `sha256sums.txt` |
| `sha256sums.txt` | SHA-256 von `report.md` und `boundary-static.tsv`; die Datei selbst wird im Handoff gehasht |

Die Selbstreferenz der Prüfsummendatei wird ausgelassen, wie bei üblichen Prüfsummenmanifesten.
