> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-176 — minimaler Abnahmevertrag Digital-8/16

## Ergebnis

Der kleinste belegte Vertrag ist eng an die aufgezeichneten Digital-8/16 Trials gebunden: Provider-Eingaben werden verarbeitet, die erwarteten angeforderten Ausgangswerte erscheinen in der eigenen Provider-Telemetrie, und in genau dieser Konstellation bleiben Permit und wirksamer Ausgang null (E-XE164-068; Profilbezug E-XE164-112). Diese vorherige native Beobachtung ist der einzige PASS im Sinne einer tatsächlichen Demonstration. Sie ist kein neuer Lauf.

Für eine prüfbare Nachbildung kommen die statisch belegten sichtbaren Consumerreaktionen hinzu: die lokale Enumerate/Name-match/Open-Folge, ReadStart/Transfers/ReadEnd und WriteStart/Transfers/WriteEnd (E-XE164-079); Startfehler als numerischer Wert 2, verworfene Finish-Rückgaben und Endstatus aus dem letzten statussetzenden Transfer (E-XE164-092/093); beim Write zusätzlich separat gehaltenes Gate-Ergebnis und als Adress-/Basispositionen verwendete Rückgaben (E-XE164-093); sowie getrennte äußere und Pointerzellen-Push-Ergebnisse und die Null-Bedingung des Kbus-Callbacks (E-XE164-083/084/091). Das sind genaue statische Beobachtungen, aber die daraus abgeleitete providerseitige Akzeptanz ist HYPOTHESE und nicht als Laufzeit-PASS ausgewiesen (E-XE164-094).

Damit ist der Vertrag klein genug, um die nachgewiesene Signalverarbeitung und Rückgabemechanik abzunehmen, ohne Bedeutungen für Rohwerte, Strukturen oder Callbackpositionen zu erfinden. Keine physischen Transportinternas oder elektrische Aktorreaktionen werden für diesen begrenzten Abnahmescope verlangt (E-XE164-070/110, HYPOTHESE). Das schließt weder allgemeine K-Bus-Vollständigkeit noch andere Profile oder Dienste.

## Matrix und Beleglage

`acceptance-contract.tsv` führt zwölf Muss/Soll-Nicht/Offen-Kriterien samt Evidence-IDs, Stufe und Abnahmestatus. `evidence-coverage.tsv` ordnet sämtliche in der Matrix zitierten IDs ihrem im kanonischen Index geführten Evidenzstatus und der hier relevanten Grenze zu. PASS steht ausschließlich für die bereits dokumentierte Trial-Beobachtung; die statischen Consumer-/Handlerforderungen sind NOT_RUN. Die Grenzen, die mangels Ausführung oder dynamischer Bindung nicht prüfbar sind, bleiben OFFEN oder BLOCKED.

## Fundstellen und Beobachtungen

- Kanonischer Index: E-XE164-067..074, 078..079, 083..094, 105..113, 164, 200..203. Insbesondere E068 dokumentiert native begrenzte Trials; E079 die drei lokalen Ordnungen; E083/084/091 die Push-Rückgaben; E092/093 die Zyklusreaktionen; E094 deren begrenzte Abnahmeableitung; E110/202 die weiterhin hypothetische Grenzziehung.
- `notes/protocols.md`: zusammenfassende Zeilen für diese IDs und explizite Status-/Scope-Vorbehalte; keine neue Analyse.
- WP-XE164-174 `report.md` und `boundary-matrix.tsv`: integrierte Ausgangssynthese einschließlich Offenheit der Profilreichweite und Loader-/Callbackbindung.

Evidenzstufen bezeichnen die jeweilige Aussageart, nicht ein pauschales Testurteil. E068 VERIFIZIERT ist eine dokumentierte frühere Laufzeitbeobachtung; E092/093 VERIFIZIERT bezeichnet statische Consumermechanik; E094 und E110/202 bleiben HYPOTHESE. E201 bleibt HYPOTHESE. Der Validator prüft die vier festgelegten Inputhashes, bekannte Evidence-IDs, zulässige Statuswörter, Tabellenform/Vollständigkeit und Dateimanifest.

## Alternativerklärung

Die beobachteten Provider-Telemetriewerte könnten allein den begrenzten Modell-/Testzustand spiegeln, während nicht getrackte parallele Dienste oder andere Callbackpfade beteiligt sind. Das ist mit E-XE164-069/073 vereinbar: die bisherige Evidence schließt solche Pfade nicht generell aus. Ebenso ist statische Rückgabemechanik kein Beleg, dass jeder beschriebene Callback im aufgezeichneten Profil dynamisch aufgerufen wurde.

## Restunsicherheit

Offen bleiben dynamische Erreichbarkeit und konkrete Provider-/DAL-Bindung, vollständiger ABI- und Lebenszyklusvertrag, vollständige DeviceSpecific/VCall-/Slot-29-Propagation, tatsächliche Erreichung von get_uid/read_conf_reg im ausgewählten Profil, aktive Permit-/Ausgangsfälle, weitere Module und sämtliche Hardware-/Elektroreaktionen. E-XE164-201 bleibt ausdrücklich HYPOTHESE; weder DSO-Identität noch Laufzeitverhalten wird aus statischen Loaderpositionen hochgestuft. Keine unabhängige Runtime- oder Hardware-Review wird behauptet.

## Methoden, Tools und Prüfergebnis

Offline-Reconciliation der vier vorgegebenen Dokumente; kein REA-Lauf, keine Binaryanalyse, keine Tests oder externe Zugriffe. Exakte Eingangshashes wurden vor der Auswertung mit `sha256sum` verglichen und stimmten. Verwendete CLI-Werkzeuge: GNU coreutils `sha256sum` 9.7, ripgrep `rg` 15.2.0, GNU sed 4.9, Python 3.13.5 für den beigefügten Validator. Worker-Eigene Evidenzprüfung; kein unabhängiger Review.

Validatorstatus: PASS (Inputs, Evidence-IDs, Statusvokabular, Tabellenvollständigkeit und Manifest). Laufzeit-/Hardware-Abnahmetest: NOT_RUN. Das Ergebnis gilt nur für den vorgegebenen Evidence-Stand und die explizit begrenzte Digital-8/16 Demonstration.

## Erzeugte Dateien und SHA-256

Werte stehen in `SHA256SUMS` und schließen alle fünf fachlichen Dateien sowie den Validator ein. Das Manifest selbst ist aus Gründen der üblichen Manifestkonvention nicht selbstreferenziert.
