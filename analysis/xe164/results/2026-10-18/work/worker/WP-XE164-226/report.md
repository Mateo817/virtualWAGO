> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-226 — Gegenprüfung der Lifecycle-Matrix R1–R7

## Ergebnis

Die Prüfung ist eine textuelle Gegenprüfung der sieben Matrixzeilen gegen die im Assignment hashgebundenen Reports WP-XE164-202, -222, -223, -224 und -225. Die fünf Reporthashes und der Matrixhash stimmen mit dem Assignment überein.

Ergebnis: R1–R5 bestehen die Textprüfung mit den in den Quellen genannten Grenzen. R6 ist überdehnt: „No direct A32 caller exists“ lässt die Begrenzung des zugrunde liegenden Scans weg. R7 ist innerhalb dieses Auftrags nicht verifizierbar, weil es für die bisherige Provider-Hypothese auf WP237 verweist, dessen Report nicht zu den hashgebundenen Eingaben gehört. Die statusgemäße Behandlung als **HYPOTHESE** bleibt erforderlich; der fehlende Report macht die konkrete Quellenbehauptung **OFFEN**, nicht falsch.

## Siebenzeilige Prüfmatrix

`PASS`/`FAIL` bewertet hier nur, ob die Matrixzeile durch die angegebenen, hashgebundenen Reports textuell gedeckt ist und ihre materiellen Grenzen einhält. Es ist kein Test der Binärdatei.

| Zeile | Prüfung | Begründung |
|---|---|---|
| R1 | PASS | WP202 rechnet den sichtbaren Getter-Rückgabewert auf ELF-relative Adresse `0x14154` zurück und hält Load Bias, geladenes Objekt und Laufzeitaufruf **OFFEN**. R1 bleibt bei einem Kandidaten und erfindet keine Laufzeitadresse. |
| R2 | PASS | WP202 bindet den Slot an `0x14154`; WP222 beschreibt die `.data`-Quellen bei `+0/+4`, die beobachteten Zieladdends und die Xrefs. Die Aussage zu fehlenden direkten aligned A32 B/BL-Sites entspricht dem explizit so begrenzten Scan. Der Report bindet den Scan an file-backed `SHF_EXECINSTR`-Sektionen und schließt BLX immediate aus; die Matrix sollte diese Grenze bei späterer Wiederverwendung mitführen. |
| R3 | PASS | WP223 zeigt am Body `0x1bec` den Nullbyte-Zweig mit sichtbarem `r0=0`, einen begrenzten Pfad mit `strb 1` auf der berechneten Basis `+0x28` und sichtbare Fehlerpfade mit `r0=0xffffffff`. Die Matrix nennt diese sichtbaren Pfade und hält Callee-Wirkungen, Reachability und Ausführung **OFFEN**. „Erfolg“ ist dabei nur eine Pfadbezeichnung, kein belegter semantischer Vertrag. |
| R4 | PASS | WP224 zeigt den frühen Rückweg bei Bytewert null mit `r0=0`; auf dem aktiven lokalen Pfad wird `0` nach `+0x28` geschrieben und die sichtbaren Ausgänge setzen `r0=0`. R4 bewahrt die offenen Callee-, Reachability- und Laufzeitfragen. |
| R5 | PASS | WP223 und WP224 berechnen lokal dieselbe Basis `0x141e0` und dokumentieren die komplementären Byte-Schreibwerte an Offset `+0x28`. „Lifecycle-like“ und „Kandidat“ bleiben ausdrücklich **HYPOTHESE**; Aufrufreihenfolge, Namen und Laufzeit sind ausgeschlossen. |
| R6 | FAIL | WP222s Negativbefund ist nicht „keine direkten A32-Aufrufer“ ohne Einschränkung: geprüft wurden aligned A32 `B`/`BL`-Encodings in file-backed ausführbaren ELF-Sektionen; `cond=0xf`/BLX immediate wurde ausgeschlossen. Der Report sagt außerdem ausdrücklich, dass indirekter Aufruf und computed control flow unberührt bleiben. Ersatzformulierung: „Der gebundene Scan fand keine aligned A32 B/BL-Site in file-backed `SHF_EXECINSTR`-Sektionen; indirekter/computed Aufruf und andere Encodings bleiben **OFFEN**.“ |
| R7 | FAIL | Die Gegenüberstellung von R5 mit einer vorherigen Hypothese zu `+0x0c/+0x10` ist in der Matrix E-XE164-237 zugeordnet. WP237 ist unter den fünf hashgebundenen Reports des Assignments nicht enthalten; WP225s Synthese belegt die neue Kandidatenerweiterung, aber nicht unabhängig den Inhalt der früheren WP237-Hypothese. Die Aussage bleibt **HYPOTHESE** und ihre konkrete Vorquellenbehauptung **OFFEN**, bis WP237 hashgebunden vorliegt oder die Zeile enger auf die hier geprüften Quellen gestützt wird. |

## Überdehnung oder fehlende Bedingung

- R6: Scope der Negativaussage erweitern die Matrixworte über den Scan hinaus. Die Eingrenzung muss mindestens die file-backed `SHF_EXECINSTR`-Sektionen und das A32-B/BL-Encoding nennen; indirekte Ziele, computed control flow und BLX immediate sind damit nicht ausgeschlossen.
- R7: Die angegebene Evidenz E-XE164-237 ist nicht durch die Eingaben dieses Reviews gebunden. Das ist ein Quellen-/Prüfbarkeitsmangel, kein Gegenbeweis zur Hypothese. R7 darf nicht zu **VERIFIZIERT** aufgewertet werden.
- R2: Kein FAIL, weil die Matrix die Negativaussage ausdrücklich auf aligned A32 B/BL beschränkt und WP222 die vollständigen Scan-Grenzen dokumentiert. Für eine eigenständige Wiederverwendung außerhalb dieses Dossiers sollte der Sektionenumfang ergänzt werden.

## Methode, Werkzeuge und Restunsicherheit

Methode: Offline-Lesen der Assignmentdatei, der Matrix TSV und der fünf gebundenen Reports; Hashvergleich mit `sha256sum`; anschließend zeilenweiser Abgleich von Status, Beobachtung, Mindestfolgerung, Grenzen und Evidence-Referenzen. Kein REA-Aufruf, keine neue Disassemblierung/Binäranalyse, keine Runtime-, Geräte-, Netzwerk- oder VM-Aktivität. Der mitgelieferte Validator prüft Hashbindung, Matrixzeilenzahl und die beiden expliziten Reviewbefunde; er ist ein Konsistenzcheck und kein unabhängiger Binärnachweis.

Restunsicherheit (**OFFEN**): WP237s ursprünglicher Inhalt und Hash sind hier nicht enthalten, sodass der dortige vorherige Befund nicht nachgeprüft werden konnte. Auch die von den Reports selbst offengelassenen indirekten Aufrufe, Signaturen, Callee-Effekte, Laufzeitbindung, Reachability und Hardwarewirkung werden durch diese textuelle Gegenprüfung nicht gelöst.

Prüfstatus: **PASS** für Hash- und Strukturvalidator; Reviewbefunde R6 und R7 sind die oben ausgewiesenen **FAIL**-Zeilen. Dies ist Self-Review und keine unabhängige Prüfung der Originaldatei.
