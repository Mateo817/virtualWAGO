> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-062 — lokale sourcegebundene Testabdeckung

## Ergebnis

**VERIFIZIERT:** Die eingereichten neun Quell-/Testdateien und die WP-060-Matrix stimmen mit allen angegebenen SHA-256-Werten überein. In den Quellen existieren direkte Assertions für die ausgewählten Digital-8/16-Verhaltensweisen: Enumeration und Konfiguration, gelatchte Eingabeframes, gestufte Ausgangsframes, Diagnose, Application-State, Watchdog, Device-specific-Aufrufe einschließlich VCall, Permit-/Fault-Sperre sowie Bridge-Leaseverlust und konkurrierendes Init/Exit.

**OFFEN:** Das ist Assertion-Inventar, kein Testergebnis. In diesem Arbeitspaket wurden keine Tests, Compiler-Builds, ARM-/VM-/Runtime-Binaries oder Geräte ausgeführt. Für alle aufgeführten Tests gilt deshalb `NOT_RUN`. Ein `PASS`-Text im C/Python-Quelltext ist nur eine Ausgabeformulierung und kein hier beobachteter Lauf.

## Abgleich mit den zwölf WP-060-Gruppen

Die TSV-Datei klassifiziert jede der zwölf `operation`-Zeilen aus `boundary-matrix.tsv`. Sie enthält zusätzlich die einzeln angefragten ADI-Aufrufe und Gate-Fälle, damit beispielsweise VCall, Lease und Fault sichtbar bleiben, obwohl WP-060 sie innerhalb breiterer Gruppen führt.

Direkte Abdeckung bedeutet: eine Assertion im angegebenen Testsource prüft Rückgabewert, Zustand oder Signal. Indirekte Abdeckung bedeutet: angrenzendes Verhalten wird geprüft, aber nicht der behauptete Vertrag selbst. `Keine` bedeutet: in den gelieferten Tests fand sich keine sourcegebundene Assertion dafür. Diese Einstufung sagt nichts darüber aus, ob die Implementierung das Verhalten tatsächlich erfüllt.

### Beobachtete Schwerpunkte

- `tools/adi_digital_adapter_test.c` ist der breiteste eigene Adapter-Harness. Er prüft Listenränder und ungültige ID, die ausgewählten 8-/16-Bit-Profile, Input-Latching und Bounds, atomare Write-Frames, mehrere Fail-closed-Übergänge, Diagnosezustände, Device-specific-Metadaten, VCall, Watchdog und einfache Close/Exit/Reopen-Pfade (insbesondere Zeilen 45–70, 73–116, 118–149, 151–284, 286–471, 474–549).
- `tools/adi_model_bridge_integration_test.c` bindet den echten eigenen Adapter an die lokale Bridge: Input-/Permit-/Fault-/Status-Interaktion, Leaseverlust nach Client-Schließen, Digital-16-Wortwerte und 64 konkurrierende Init/Exit-Iterationen werden durch Assertions geprüft (Zeilen 59–85 und 88–175). Dies bleibt ein eigener Offline-IPC-Test und kein Test eines originalen WAGO-Verbrauchers.
- `tools/adi_model_bridge_test.c` prüft Bridge-Protokoll, Socket-Berechtigungen, Eingabevalidierung, Fault-Latching und Permit-Widerruf bei Client-Disconnect/Timeout (Zeilen 155–287). Die Setter und Modellzustände dieses Tests sind Test-Doubles; daher ist das keine Adapter- oder Herstellersemantik-Evidence.
- Die Default-Build-Tests prüfen je Profil Grundpfade, Read/Write, Permit und Watchdog-Ablauf sowie Close/Exit: Digital-16 in `tools/adi_digital16_default_test.c:11–76`, Digital-8 in `tools/adi_digital8_default_test.c:11–50`.

## Priorisierte ungetestete oder nur indirekte Fälle

1. **Adapter-ABI-/Tabellenvertrag:** `adi_GetApplicationInterface() != NULL` wird geprüft (`adi_digital_adapter_test.c:507–512`); vollständige 34-Slot-Tabellenform, Nicht-NULL-Belegung jedes Slots, ABI-/Aufrufkonvention oder alle Callback-Signaturen werden nicht durch Assertions geprüft. Kleinster hardwarefreier Test: gegen die im Scope zugelassenen Header alle erwarteten Funktionszeiger bzw. den verfügbaren Tabellenvertrag prüfen und jeden freigegebenen Slot mit einem minimalen Gültigkeits-/Fehlerfall aufrufen. Keine Struktur oder Slotzahl aus diesen Tests neu ableiten.
2. **Init-/Scan-/Close-/Exit-Fehlerpfade:** Erfolgsfälle, Reopen und konkurrierendes Init/Exit sind abgedeckt; direkte Assertions zu wiederholtem Close, ungültiger Close-ID, Exit während eines wirksamen Ausgangs, Bridge-Startfehler durch Adapter-Init sowie Scan-Fehler/rollback fehlen. Kleinster hardwarefreier Test: isolierte Prozessfälle mit kontrolliert ungültigem lokalen Socket-Endpunkt und Zustands-Snapshots vor/nach Close/Exit; für Fehler, die Adapterzustand betreffen, direkte Assertions auf Rückgabewert und wirksame Ausgänge ergänzen.
3. **Read-/Write-Fehlerzustände:** Bounds, falscher Read-Task, unvollständige/fehlerhafte Write-Frames, ungültiges Bit und Thread-Eigentum werden teilweise direkt geprüft (`adi_digital_adapter_test.c:129–149`, `169–176`, `370–384`, `423–459`). Ungültige Device-ID bzw. Transaktionen ohne Start/mit falschem Task für alle Read-/Write-Varianten sowie BOOL-Einstiege sind nicht systematisch belegt. Kleinster Test: kleine Parametertabelle aus ungültiger ID, Task, Offset/Größe und fehlendem Start; je Assertion Status und Fail-closed-Ausgänge prüfen.
4. **Application-State und Watchdog-Kombinationen:** Staged-Frame wird nach Stop→Running vergiftet; Watchdog-Stop und Ablauf sind abgedeckt. Ein direkter Assert, dass STOP den bereits veröffentlichten wirksamen Ausgang sofort auf null setzt, fehlt; ebenso ist die genaue Grenzzeit-/Restart-/Cadence-Policy nur begrenzt geprüft. Kleinster Test: Modelluhr verwenden, laufenden effektiven Ausgang herstellen und an den dokumentierten Modellübergängen Snapshot prüfen. Das wäre eine Prüfung der expliziten eigenen Modellpolitik, keine Herstellersemantik.
5. **Diagnosis-Detail-/Subdevice- und Device-specific-Fehlerformen:** Healthy/BusFault und einige Device-specific-Fehlerstatus sind abgedeckt; Subdevice-Diagnose, GetLastError, UID-Erfolg, unbekannte/alle nicht unterstützten Operationen und deren vollständige outer-/inner-status-Matrix sind nicht systematisch assertionsgebunden. Kleinster Test: zulässige und absichtlich nicht modellierte Namen/Argumente getrennt auf outer- und inner-status sowie unveränderte Buffer/Outputs prüfen, ohne unbewiesene Rückgabeverträge festzuschreiben.
6. **Originalstack-/Runtime-Nachweis:** Keiner der gelieferten eigenen C-Harnesses ruft den originalen libIoDrvDal/libIoDrvKbus-Verbraucher auf. `tests/test_native_descriptor_contract.py` prüft synthetische XML-Deklarationen und markiert selbst `native_process_image`/`register_contract` als `OFFEN` (`:22–67`); es ist keine ADI-Boundary-Abdeckung. Kleinster Offline-Schritt ist ein statischer, hashgebundener Konsument-/Slot-Abgleich; ein Laufzeitnachweis ist damit weiterhin nicht erbracht.

## Alternativerklärungen und Grenzen

Ein fehlender Test-Assert beweist nicht, dass ein Verhalten fehlerhaft ist: es kann durch nicht gelieferte Testdateien, einen getrennten statischen Nachweis oder einen historischen Lauf geprüft worden sein. Umgekehrt beweist eine Assertion in Source weder, dass der Test kompiliert noch dass sie im betreffenden Build aktiv war; etwaige bedingte Builds/Assertions wurden hier nicht ausgeführt. Die Default- und Integrationsquellen deklarieren ausdrücklich eigene Client-/IPC-Tests, daher sind ihre Aussagen keine direkte Bestätigung des Originalverbraucher-Vertrags. Historische CI-/Test-PASS-Ergebnisse wurden nicht übertragen.

## Methode, Werkzeugversionen, Status und Self-Review

Methode: ausschließlich statische Source-/Matrix-Reconciliation. Eingaben wurden mittels `sha256sum` validiert; Assertions und Fundstellen wurden mit `rg`, `nl` und `sed` gelesen. Versionen: GNU coreutils `sha256sum 9.7`, ripgrep `15.2.0`, Debian `cc 14.2.0`, Python `3.13.5`. Compiler und Python-Versionen wurden nur abgefragt; sie wurden nicht zum Bauen oder Ausführen der Testquellen verwendet. Keine Netzwerk-, Geräte-, VM-, Runtime-, Git- oder privaten Header-/Binary-Zugriffe.

Statussprache: Aussagen sind als `VERIFIZIERT`, `OFFEN` oder in der TSV als `DIREKT`, `INDIREKT`, `KEINE` gekennzeichnet. Teststatus ist ausschließlich `NOT_RUN`; es gibt in diesem Bericht kein `PASS`, `FAIL` oder `BLOCKED` für einen ausgeführten Test. Alle Aussagen sind Worker-Self-Review, kein unabhängiges Review.

## Eingabeidentitäten

Die vollständigen Pfade, Größen (wo vorgegeben) und Hashes stehen in `inputs.tsv`. Die Matrix hatte den vorgegebenen Hash `0a67a8…e11337c`; alle neun Projektdateien entsprachen ebenfalls den Eingabe-Hashes. `sha256sums.txt` bindet die drei erzeugten Artefakte.
