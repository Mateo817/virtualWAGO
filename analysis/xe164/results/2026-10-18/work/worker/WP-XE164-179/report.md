> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-179 — Befund

## Ergebnis

**Befundstatus: VERIFIZIERT. Teststatus: NOT_RUN.** Der Befund gilt für den sauberen, getrackten Repositorybaum bei HEAD e56bb8ed488137f3d9276bfcbec6f33d2917114a und Tree 1ddb1777f301d6c99801fba4ac242eec3ecd9f0f. Vollständiger git status --porcelain=v1 war leer.

Der Workflow startet laut .github/workflows/python.yml:35 den Einstieg python -m unittest discover -s tests -v. Nach dem Python-Standardverhalten (Default-Muster test*.py) passen tests/test_adi_model_bridge.py und tests/test_native_descriptor_contract.py zur Discovery. Die Zeile belegt statische Verdrahtung, nicht einen ausgeführten CI-Job.

Die vollständige git grep -n-Suche über HEAD nach allen fünf exakten C-Basenames ergab **21 Treffer**. Der vollständige Rohoutput ist in tracked-reference-scan.txt; seine Klassifikation pro Treffer steht in tracked-reference-scan.tsv. Ergebnis der Trefferklassifikation:

- tools/adi_model_bridge_test.c: ein aktueller Compilerinput-Treffer in tests/test_adi_model_bridge.py:19, zwei Evidence-Treffer und ein C-Selbstkommentar. Die Python-Testmethode test_bounded_transport_permissions_protocol_and_disconnect wird bei vorhandenem cc kompiliert und gestartet (tests/test_adi_model_bridge.py:9-23); skipUnless(shutil.which("cc")) in Zeile 10 lässt sie bei fehlendem Compiler ausfallen/überspringen. Der Workflow installiert bubblewrap, aber keinen Compiler ausdrücklich (.github/workflows/python.yml:24-35). Klassifikation: **BEDINGT_UEBERSPRINGBAR**.
- tools/adi_digital_adapter_test.c: neun Treffer, davon zwei Dokumentation und sieben Evidence; kein Build-, Compiler- oder Importtreffer. Klassifikation: **LOKAL_NICHT_CI_VERDRAHTET**.
- tools/adi_digital16_default_test.c: ein Evidence-Treffer, keine Build-/Compiler-/Importeinbindung. **LOKAL_NICHT_CI_VERDRAHTET**.
- tools/adi_digital8_default_test.c: ein Evidence-Treffer, keine Build-/Compiler-/Importeinbindung. **LOKAL_NICHT_CI_VERDRAHTET**.
- tools/adi_model_bridge_integration_test.c: sechs Evidence-Treffer, keine Build-/Compiler-/Importeinbindung. **LOKAL_NICHT_CI_VERDRAHTET**.

Die einzige aktive Compilerstelle übergibt tools/adi_model_bridge.c und tools/adi_model_bridge_test.c an cc (test_adi_model_bridge.py:15-20). test_native_descriptor_contract.py enthält über die vollständigen Zeilen 1–67 keinen Compiler-/Subprocess-Einstieg. Dokumentations- und Evidence-Treffer belegen Erwähnungen bzw. gespeicherte Nachweisartefakte, keine gegenwärtige Verdrahtung in diesen unittest-Lauf.

## Beobachtungen und Alternativerklärung

- Alle neun vorgegebenen Eingaben stimmen in Bytezahl und SHA-256 mit den Pins überein; validate.py prüft sie erneut. Die Matrix enthält jede der fünf Provider-Testquellen genau einmal samt Pin, Klassifikation, Fundstelle und Scan-Zusammenfassung.
- Der vollständige Scan ist an den angegebenen Commit gebunden und wird vom Validator erneut ausgeführt und mit dem gespeicherten Rohoutput verglichen. Der Validator prüft außerdem HEAD, Tree, sauberen Porcelain-Status und den erwarteten einzelnen buildrelevanten Treffer.
- Ein anderer lokaler oder historischer Build-/Testeinstieg kann C-Dateien unabhängig kompilieren. Die Evidence-Treffer sagen etwas über gespeicherte historische Nachweise, nicht darüber, ob deren Läufe erfolgreich waren oder ob sie Teil des aktuellen GitHub-Workflows sind.

## Restunsicherheit

Es wurde kein Workflow und kein Test ausgeführt; der konkrete Hosted-Runner-Zustand sowie die tatsächliche Verfügbarkeit von cc im Job sind unbekannt. Daher gibt es keinen PASS-Nachweis und keine Behauptung, dass der bedingt eingebundene Bridge-Test in einem konkreten CI-Lauf lief. Bewertet wurden die angegebenen fünf Basenames im getrackten Baum des angegebenen Commits und der beschriebene unittest-Einstieg; nicht bewertet wurden anderer Workflowinhalt außerhalb dieser Basename-Suche, andere Buildsysteme oder Implementierungssemantik.

## Methoden- und Toolstand

Offline, statische Hash-/Datei-/Git-Indexprüfung. Verwendet: Python 3.13.5; ripgrep 15.2.0; GNU coreutils nl, sha256sum, wc 9.7; GNU sed 4.9; cc 14.2.0 nur als Versionsabfrage, nicht zum Kompilieren. git grep -n lief gegen HEAD; keine Tests/CI/Builds, keine Netzwerk-, VM-, Geräte- oder Hardwareaktionen. validate.py ist ein Artefakt- und Quellenanker-Validator, keine Repository-Testausführung.

## Erzeugte Artefakte

assignment.md, report.md, wiring-matrix.tsv, gap-list.tsv, tracked-reference-scan.txt, tracked-reference-scan.tsv, validate.py, SHA256SUMS. Hashes der sieben übrigen Artefakte stehen im Manifest; es listet sich selbst nicht, da ein selbstreferenzieller SHA-256-Eintrag nicht stabil definierbar ist.
