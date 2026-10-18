> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-395 — Frische Query-Rekonstruktion und unabhängige Speicherketten

Root **Self-Review**. **VERIFIZIERT** ist die Konsistenz der vier WP388-Modelle mit frisch berechneten Ausgaben und einer getrennten, aus expliziten Ausgangsbytes aufgebauten Speicherprüfung. **PASS**:186 Instruktionszeilen,86 Reads,48 Stores, sämtliche endgültigen Modellbytes und sämtliche gespeicherten Ergebnisobjekte. Native Ausführung, Runtime, VM, Netzwerk und Geräte: **NOT_RUN**. Tatsächliche Bindung, Eingaben, Speicherinhalte und API/ABI bleiben **OFFEN**.

WP392 hat die rohen Instruktionen, Register-/Flag-Übergänge und Eventpositionen unabhängig geprüft, verwendete dabei aber die aufgezeichneten Readwerte als Eingaben und rekonstruierte kein anfängliches Fixture-Speicherbild. Der ursprüngliche WP388-Validator prüft gespeicherte Tabellen, ohne vollständige Neugenerierung. Dieses Paket schließt genau diese beiden begrenzten Nachweislücken für die vier vorhandenen Fixtures.

Der genaue WP388-Manifesthash wird in source-pins.tsv festgehalten; dessen sämtliche Ausgaben werden vor und nach dem Check geprüft. Das Ziel bleibt ausschließlich die bereits gepinnte Datei3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Es wurde kein Sourcegenerator eines gefrorenen Pakets aufgerufen.

Nach Inspektion des vollständigen WP388/model.py wird das Modul mit deaktiviertem Bytecode geladen. Dessen optionaler main-Schreiber ist durch den Python-Nameguard geschützt und wird nicht aufgerufen. Nur die lesende run_case-Funktion mit den vier expliziten Cases wird ausgeführt. Die neu erzeugten PC-/GPR-/NZCV-Zeilen, sämtliche Memory-Events, Metadaten, Ergebnisse und endgültigen Speicherbytes stimmen genau mit den eingefrorenen Daten überein. Diese Neuberechnung verwendet denselben Modellcode und wird ausdrücklich nicht als unabhängiger CPU-Decoder ausgegeben.

Davon getrennt initialisiert der Root-Checker eine eigene Byte-Map: Lookupzelle337d0+12*Index, die vier Literalwörter, GOT3349c mit lokalem Getterbec4, die aktuelle SSC-Zelle443f4, zwei weitere Quellwörter, vier Worte beiL=4013c+16*Index und drei Eingangs-Stackwörter. Die Werte sind deklarierte Fixture-Voraussetzungen. Der Checker liest **keinen aufgezeichneten Readwert als neue Eingabe**: jeder Read muss Byte für Byte aus diesem anfänglichen Bild plus allen vorhergehenden Stores folgen. Ein nicht gemappter Read schlägt fehl. Für jedes Store-Event werden die konkreten Bytes fortgeschrieben. Am Ende muss dieses eigene Speicherbild mit dem frisch berechneten vollständigen Modellbild übereinstimmen.

Damit wird insbesondere die Aliasfolge bestätigt: erster Store nachL+4, späterer Read vonL+4 beobachtet genau diesen Store. Auch die tatsächlichen PUSH-Stores und POP-Reads werden über dieselbe Kette geprüft; frühere Stackbytes werden nicht als bekannte Nullen ausgegeben.

Die vier Counts sind:
all-six52 Zeilen/25 Reads/14 Stores;
all-null37/15/8;
selected-null45/21/12;
alias-output0-to-L4 52/25/14.
Alle liefern unter den deklarierten Index1-Fixtures den lokalen Rückgabewert4014c, SP600000 und den gespeicherten Rückkehrtoken. Das ist weder ein allgemeiner Indexvertrag noch eine Runtime-Successmeldung.

Die Kombination aus WP392s unabhängigem Instruktionscheck und diesem Speicher-/Neugenerierungscheck stärkt die begrenzten vorhandenen Fixtures. Sie beweist keine Laufzeitkonfiguration, realen Caller, allgemeine Speicherüberlappung oder CPU-/ABI-Eigenschaft außerhalb des ausgewählten Quellpfades. Der Validator ist standardmäßig lesend; nach der Prüfung sind Inventar und Hashes des gesamten WP388-Pakets identisch.
