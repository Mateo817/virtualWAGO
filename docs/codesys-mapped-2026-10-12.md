# CODESYS-Mapping-Kandidat, 12.10.2026

Dieser **Self-Review** dokumentiert einen separaten, hardwarefreien CODESYS-Kandidaten mit nativem DI/DO-Mapping. Zusätzlich prüfte ein tatsächlicher separater Luna-Worker mit low Quellen, private Metadaten und CSV unabhängig; keine must-fix-Befunde. Er führte keine IDE- oder Geräteoperationen aus. Der Builder [`tools/codesys_mapped_candidate.py`](../tools/codesys_mapped_candidate.py), SHA-256 `a57fe8bf0700f8adbd51a0f94974341197b44cc3c3ef1cf3723e98aa26f43f67`, erzeugt ein eigenes Projekt und importiert/prüft die Mapping-CSV über die installierte ScriptEngine. Die ST-Datei [`prototype/iec/minimal_io.st`](../prototype/iec/minimal_io.st) wurde nicht verändert (SHA-256 `e757410d9d9efc4f363e666190514af130d2a6be9fd46916a805cd7551588dcc`). `OutputPermit` ist beim Start `FALSE`.

## Offline-Build und persistiertes Mapping

**VERIFIZIERT / PASS, enger Scope:** CODESYS 3.5.21.50 (SP21 Patch 5) kompilierte den Kandidaten mit null Fehlern und null Warnungen. Das installierte Projekt-API lieferte beim getrennten Wiederöffnen erneut die Compiler-Version 3.5.21.50. Der Offline-Projektbaum enthält den LocalBus sowie die Beschreibungen 750-1405 und 750-1504; alle drei Knoten waren aktiviert. Diese Aussagen betreffen den Projektbaum und den Offline-Engineeringlauf.

Der native Readback des gespeicherten Projekts ordnet den vollständigen WORD-Eingangsparameter `_IN` der IEC-Variablen `Application.PLC_PRG.InputWord` und den WORD-Ausgangsparameter `_OUT` `Application.PLC_PRG.OutputWord` zu. Beide Parameter enthalten je 16 Bit-Unterelemente; diese Unterelemente besitzen keine eigenen Variablenzuordnungen. Die qualifizierten IEC-Ausdrücke wurden nach erneutem Öffnen bestätigt. Die Mapping-CSV wurde erneut exportiert und war bytegleich mit der gespeicherten CSV (1797 Bytes). Das gespeicherte Projekt blieb beim Readback unverändert.

Die CSV zeigt als **konkretes Offline-Beispiel** DI-Bits `%IX2.0` bis `%IX3.7` und DO-Bits `%QX0.0` bis `%QX1.7`. Das beschreibt die erzeugte Projektkonfiguration, nicht eine verifizierte physische Prozessabbildlage oder Verdrahtung. Es gab keine Verbindung zu Gateway oder Steuerung, keinen Download, keinen Runtime-Start und keinen physischen I/O-Test. Physische Anwesenheit und Identität der Terminals bleiben **OFFEN**.

Das korrigierte Ergebnis ist an den Builder-Hash und das verwendete Profil gebunden. Das tatsächliche IDE-Programm hatte SHA-256 `0f483fae5ac32e25207c38b9afdf08aa12680c5959fc692062f27db050f310b2`; das tatsächlich gewählte Engineeringprofil hatte SHA-256 `fb09099380f40dc0270e35a7555c50b9b271a2e977a03675aed812c09b33ca1b`. Die vier privaten Offlineartefakte sind im Evidence-JSON mit Größe und SHA-256 gebunden. Projekt-, APP-, CRC- und CSV-Dateien sowie Rohprotokolle bleiben außerhalb dieses öffentlichen Repositories.

## Korrektur und Prüfumfang

Der erste echte Buildversuch (**FAIL**, 2 Fehler, 0 Warnungen) verwendete `PLC_PRG.InputWord` und `PLC_PRG.OutputWord` als Mappingausdrücke. Die IDE meldete für beide Zuordnungen „Invalid application“. Der Kandidat wurde auf `Application.PLC_PRG...` korrigiert. Der anschließende Build und der separate Readback des gespeicherten Projekts ergaben jeweils **PASS**, 0 Fehler und 0 Warnungen. Der fehlgeschlagene Versuch wird nicht als erfolgreicher Lauf gezählt.

Sieben lokale Hilfstests prüfen positive CSV-Konsistenz sowie falsche Richtung/Präfixe, fehlende oder doppelte Kanäle und Konflikte. **7/7 PASS** unter Python 3.13.5; zusätzlich bestanden `py_compile` und `git diff --check`. Dies sind reine Hilfsprüfungen und kein Ersatz für den CODESYS-Lauf. Die breitere hardwarefreie Suite wurde anschließend durch den Integrator ausgeführt: **99 PASS** unter Python 3.13.5; Bindung im [Blocknachweis](../evidence/originalstack-block-validation-2026-10-12.json).

Die verwendeten ScriptEngine-Eigenschaften und Methoden sind in der [CODESYS-Dokumentation zu ScriptDeviceParameters](https://content.helpme-codesys.com/en/ScriptingEngine/ScriptDeviceParameters.html) und [ScriptDeviceObject](https://content.helpme-codesys.com/en/ScriptingEngine/ScriptDeviceObject.html) beschrieben. Der hier berichtete native Parameter-Readback stammt zusätzlich aus dem tatsächlich installierten Engineeringstand. Diese Nachweise qualifizieren weder Lizenzen noch Nutzungsrechte an Herstellerdateien.

## Statusgrenzen

| Gegenstand | Status | Aussagegrenze |
|---|---|---|
| Native Zuordnung der beiden WORD-Parameter, gespeichert und wieder geöffnet | **VERIFIZIERT / PASS** | Nur eigenes Offlineprojekt und installierte CODESYS-Version |
| Builddiagnostik | **PASS** | 0 Fehler, 0 Warnungen; keine Zielausführung |
| Drei Geräteknoten im Offlineprojekt aktiviert | **VERIFIZIERT** | Keine Aussage über angeschlossene Hardware |
| CSV-Konsistenz und sieben Hilfstests | **PASS** | Hilfsvalidierung; keine Hardwareakzeptanz |
| Physische Terminalpräsenz, Identität, Verdrahtung und wirksames I/O | **OFFEN / NOT_RUN** | Nicht geprüft |
| Gateway/Runtime-Verbindung, Download, Runtimeverhalten | **NOT_RUN** | Nicht Teil des Offlineversuchs |
| Unabhängiger Review | **PASS** | Tatsächlicher Luna-Worker, nur Offlinequellen/Metadaten/CSV und sieben Hilfstests |

Die berichteten Fakten, Versionen, Quell- und Artefakthashes sowie Statusmatrix sind maschinenlesbar in [`evidence/codesys-mapped-validation-2026-10-12.json`](../evidence/codesys-mapped-validation-2026-10-12.json) gebunden.
