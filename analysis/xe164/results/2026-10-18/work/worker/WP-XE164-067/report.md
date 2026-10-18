> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-067 — Reconciliation von Bridge-STOP, Reset und Lifecycle

## Ergebnis

**VERIFIZIERT:** Die öffentliche Aussage, jeder Bridge-STOP entziehe das Permit, ist für den Quellpfad „Worker ohne aktiven Client“ zu weit gefasst. `virtual_model_bridge_stop()` setzt das Stop-Flag und weckt den Worker; wenn dieser im Listenerpoll ohne Client steht, beendet er die Schleife ohne `disconnect_client()` und ohne den fatalen Workerpfad. Auf diesem Pfad wird `virtual_adi_set_permit(false)` nicht aufgerufen. Ein aktiver Client wird dagegen beim Wakeup getrennt und sein Disconnect entzieht das Permit.

**VERIFIZIERT:** `virtual_adi_reset()` setzt Modellzustand, gewähltes Profil und Uhrenmodus zurück und erhöht die Generation, stoppt aber keine Bridge und schließt keine Clientverbindung. Die Adapter-Tests rufen Reset nur nach `Exit()` bzw. vor `Init()` auf. Ein Reset bei laufender Bridge oder verbundenem Client wird in den vorliegenden Tests nicht abgedeckt. Daraus folgt ein nicht getesteter Lifecycle-Fall: der Worker bzw. Socket kann über Reset hinweg bestehen; nach erneuter Init kann ein bereits verbundener Client weiter mit derselben Workerinstanz kommunizieren.

**VERIFIZIERT:** Der reguläre Adapter-Exit ist enger als der allgemeine Bridge-STOP-Fall: `adapter_exit()` erhöht die Generation und leert den Adapterzustand unter dem State-Lock, bevor es `virtual_model_bridge_stop()` aufruft. Das dokumentierte „Exit löscht Zustand vor Join“ passt zum Quellpfad. Diese Reihenfolge lässt sich jedoch nicht als Beleg lesen, dass `virtual_model_bridge_stop()` selbst in jedem Pfad das Permit entzieht.

## Dokumentbehauptung, Quellpfad und Assertion

| Thema | Öffentliche Aussage | Tatsächlicher Quellpfad | Vorhandene Assertion / Lücke |
|---|---|---|---|
| Bridge-STOP | Lifecycle-Plan, Z. 14 und ADR-0005, Z. 11 sagen pauschal, Bridge-STOP entziehe das Permit. | `adi_model_bridge.c:533-560` setzt Stop-Flag, weckt und joint. Bei keinem Client läuft der Worker über `:459-479` aus; `:489-493` ruft das Permit nur bei `fatal` zurück. Bei aktivem Client führt Wakeup über `:404-422` zur Rückkehr und danach `disconnect_client()` (`:484-485`, Funktion `:376-380`), was das Permit entzieht. | Bridge-Test prüft Disconnect/Idle/Fehler, dann Socketentfernung bei Stop (`adi_model_bridge_test.c:251-292`). Vor dem abschließenden Stop wurde das Permit bereits durch Disconnect/Fehler entzogen; der Stop-Assert prüft nur den Socketpfad. Kein Test setzt Permit direkt bei bestehendem Worker ohne Client auf 1 und prüft dessen Zustand nach Stop. **Korrekturbedarf:** Aussage auf aktive Clienttrennung bzw. fatalen Workerpfad eingrenzen oder unconditional revoke belegen. |
| Reset während laufender Bridge | Lifecycle-Plan, Z. 43 fordert nach Wiederanlauf u.a., dass kein alter Socket/Client stillschweigend Permit erlangt; Z. 56 nennt saubere Lease-/Generationstrennung als offen. | `adi_digital_adapter.c:201-208` leert Adapterzustand und erhöht Generation, aber ruft keinen Bridge-Stop auf. `adapter_init()` (`:289-305`) startet die Bridge; wenn deren Worker schon läuft, `virtual_model_bridge_start()` (`adi_model_bridge.c:497-507`) gibt Erfolg zurück und behält Worker/Socket bei. Ein bestehender Client kann während uninitialized `NOT_READY` erhalten und nach Re-Init wieder Nachrichten verarbeiten; Bridge-Protokollpfad prüft kein Clientgenerationstoken (`adi_model_bridge.c:312-374`). | Adaptertest nutzt Reset nach Exit und vor Init (`adi_digital_adapter_test.c:507-547`); keine aktive-Bridge-/verbundener-Client-Resetsequenz. Bridge-Test modelliert `virtual_adi_reset` nicht und testet keinen Re-Init über bestehenden Client. **Korrekturbedarf:** Lifecycle-Plan muss Reset als separaten Pfad mit bestehender Socket-/Clientgeneration behandeln oder die Aussage auf Exit/Stop-Zyklen begrenzen; Nachweis für Reset-Recovery fehlt. |
| Exit vor Bridge-Join | Lifecycle-Plan, Z. 14 und 17; ADR-Rücknahme beschreibt geordnetes Stoppen. | `adapter_exit()` (`adi_digital_adapter.c:307-322`) leert Zustand bei `:311-317`, gibt den State-Lock frei und stoppt/joint anschließend die Bridge (`:318-321`). Damit wird Permit als Teil des gesamten Adapterzustands gelöscht, auch wenn Bridge-Worker gerade keinen Client bedient. | Adaptertest prüft wiederholte Lifecycleaufrufe nur in einer sequenziellen Testfolge; kein direkter Assertion-Check von Bridge-Threadjoin/Socket/Permit über `adapter_exit()` im integrierten Build ist in den zwei angegebenen C-Testdateien erkennbar. Bridge-Test prüft Bridge-Stop separat mit eigenem Test-Double. **Korrekturbedarf:** Belegstufe klar benennen; Unit-/Transportassertionen sind kein zusätzlicher nativer Rollback-Nachweis. |
| Reset-/Init-/Exit-Testbehauptung | Lifecycle-Plan, Z. 18 schreibt dem vorhandenen Harness Reinit und paralleles Init/Exit zu. | Die hier gepinnten Adapter-Testzeilen zeigen `Init`/`Exit`-Aufrufe und Reset nach Exit; die gepinnten Dateien enthalten keine Threads, die Init/Exit parallel aufrufen (Adaptertest-Threads betreffen Write/Watchdog, Z. 370-384). | Der Hinweis „parallel Init/Exit“ wird durch die beiden hier gepinnten Testquellen nicht als Assertion belegt. Es kann separate, nicht in diesem Paket enthaltene Harness-Evidence geben. **Korrekturbedarf:** Testquelle und Hash für diese Behauptung benennen oder die Assertion nicht diesen beiden Tests zuschreiben. |

## Quellen und Testumfang

- Reset: [adi_digital_adapter.c](REPOSITORY_ROOT/tools/adi_digital_adapter.c:201). **VERIFIZIERT**, statische Quellprüfung.
- Adapter Init/Exit: dieselbe Quelle, Z. 289-322. **VERIFIZIERT**, statische Quellprüfung.
- Bridge-Worker, Stop und Destruktor: [adi_model_bridge.c](REPOSITORY_ROOT/tools/adi_model_bridge.c:455), Z. 455-564, insbesondere Z. 459-494 und 533-564. **VERIFIZIERT**, statische Quellprüfung.
- Bridge-Assertions: [adi_model_bridge_test.c](REPOSITORY_ROOT/tools/adi_model_bridge_test.c:136), Z. 136-143, 247-292. Das Test-Double hält Modellzustand selbst; sein abschließender Stop-Assert prüft Socketentfernung, nicht Permit-Reset.
- Adapter-Lifecycle-Assertions: [adi_digital_adapter_test.c](REPOSITORY_ROOT/tools/adi_digital_adapter_test.c:205), Z. 205-220 und 507-547. Die STOP-/RUN-Callbackprobe vergiftet einen gestagten Frame; die Lifecyclefolge ruft Reset erst nach Exit auf.
- Dokumentfundstellen: [native-model-lifecycle-plan-2026-10-13.md](REPOSITORY_ROOT/docs/native-model-lifecycle-plan-2026-10-13.md:14), Z. 14, 18, 43, 54-56, 66-70; [adr-0005.md](REPOSITORY_ROOT/docs/adr-0005.md:11), Z. 11, 13, 47, 59-69; [real-controller-plan-2026-10-12.md](REPOSITORY_ROOT/docs/real-controller-plan-2026-10-12.md:23), Z. 23, 34-35, 38-45, 51, 55-57.

## Status, Alternativerklärung und Restunsicherheit

**VERIFIZIERT:** Quellpfadbeobachtungen und die Übereinstimmung der eng gefassten Exit-vor-Join-Aussage mit dem Adaptercode.

**OFFEN:** Ungetestete Kombinationen sind Bridge-Stop ohne aktiven Client bei zuvor gesetztem Permit, Reset bei laufender Bridge, Reset mit altem Client über anschließende Re-Init sowie Bridge-Join/Socketzustand durch Adapter-Exit im gemeinsamen Build. Diese Arbeit hat die Tests nicht ausgeführt.

**Alternativerklärung:** Der produktionsnahe Rücknahmeablauf schließt erst Client/Permit, beendet den isolierten Prozess und prüft danach frischen nativen STOP; beim Adapter-Exit wird der Zustand vor dem Join geleert. Dadurch kann der dokumentierte normale Exit-/Rollbackpfad fail-closed bleiben, obwohl der eigenständige Bridge-STOP ohne Client keine Permit-Revoke-Anweisung enthält. Der erfolgreiche native Rollback aus ADR-0005 belegt die konkrete Wiederherstellung und frische STOP-Beobachtung, nicht die Semantik aller lokalen Bridge-/Resetpfade.

**Restunsicherheit:** Ob `virtual_adi_reset()` außerhalb der Tests jemals mit laufender Bridge oder verbundenem Client verwendet werden soll, wird in den gepinnten Dokumenten nicht als API-Vertrag geklärt. Ebenso ist ein eventuell separat existierender paralleler Init/Exit-Harness nicht Teil der sieben geprüften Eingaben. Kein nativer STOP-/Rollbackbefund wird hier aus Offline-Quellpfaden abgeleitet.

## Werkzeuge und Ausführungsstatus

Statische Reconciliation; keine Builds, Tests, Netz-/Geräte-/VM-Zugriffe und keine Repositoryänderung. Tests: **NOT_RUN** (explizite Aufgabengrenze). Erkannte Werkzeugversionen: ripgrep 15.2.0, GNU coreutils `sha256sum` 9.7, Git 2.47.3, GNU bash 5.2.37. Eingabegrößen und SHA-256 sind vor der Analyse geprüft; siehe `inputs.tsv`.

## Erzeugte Dateien

- `report.md` — SHA-256 wird in `sha256sums.txt` festgehalten.
- `statement-test-matrix.tsv` — SHA-256 wird in `sha256sums.txt` festgehalten.
- `inputs.tsv` — SHA-256 wird in `sha256sums.txt` festgehalten.
- `sha256sums.txt` — Hashes aller vier gelieferten Eingaben und der drei übrigen Ergebnisdateien; der Hash dieser Datei selbst ist absichtlich nicht selbstreferenziell.
