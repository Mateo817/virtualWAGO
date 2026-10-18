> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# Bedingte Verbindung bis zu den Backend-Callbacks

Die privaten Originalbytes verbinden sechs zyklische libdal-Positionen und eine getrennte Diagnoseposition bedingt mit benannten `libpackbus`-Callbacks. Die Tabelle `backend-positions-reviewed.tsv` führt für jede Position das libdal-Ziel, den inneren Callback-Offset, den exakten ELF-Symbolnamen und seine Linkadresse auf. Dies ist eine **HYPOTHESE über die zusammengesetzte Instanz** aus jeweils **VERIFIZIERTEN lokalen Quellbeobachtungen**. Root Self-Review; die tatsächliche unabhängige Prüfung318 ist separat benannt.

Die entscheidende Adresse lautet `C = T+0x110`. Der Aufruf bei ELF0x226c liegt in **libdal.so**, bildet diese Adresse als r0 und springt indirekt. Falls er den untersuchten `libpackbus_open`-Einstieg erreicht, übernimmt dieser zunächst genau r0 nach r4. Bei erhaltenem aktuellem r4 schreibt das Backend seine Felder daher an `C+Offset = T+0x110+Offset`. Ein weiteres `+0x110` auf das Backend-r4 wäre falsch. Original311 bleibt als revisionsgebundener Stand erhalten;318 korrigiert dessen Schlussabsatz.

Der Backend-GOT hat ELF-Linkadresse0x33000, Ghidra-Adresse0x43000 und bedingt Laufzeitadresse `PackbusBias+0x33000`. Diese Domänen sind getrennt. Die19 Symbolnamen stammen aus exakten Relokationen. Sie beweisen weder Prototypen noch Callback-Verhalten.

Die beiden numerischen Längenwörter an C+4/C+8 erhalten auf dem untersuchten Schreibpfad jeweils0x2ee0. Die sichtbaren Sized-Provider testen diese Positionen, nachdem sie den Callback auf null geprüft haben. Die getrennte Diagnoseposition+0x58 des Listen-Kontexts wird weiterhin **nicht** mit dem primären Getter-/Kopierkontext gleichgesetzt.

[Code-/Listingblock bleibt im privaten Nachweispaket.]

O und D bleiben getrennte Objekte; die führenden D-Positionen werden teilweise überschrieben. Der abgeschlossene synthetische ComponentEntry-Pfad und seine unveränderten sechs zyklischen Zellen ersetzen keinen Beleg, dass der native Treiberkontext tatsächlich D enthält. Ebenso beweist der passende Backend-Schreibpfad keine erfolgreiche Initialisierung oder eine ausgeführte Veröffentlichung.

**OFFEN:** tatsächliche Objekt-/Datensatzidentität, durchgehend erhaltene Register/D-Register/Speicher über opake Calls, aufgelöste Import-/Relokationswerte, erreichbare Tabellenbefüllung, Callback-Effekte und Runtime/API/ABI. **PASS:** lokale Quellen-/Symbol-/Positionszuordnung und Prüfsummen. **NOT_RUN:** Hersteller-ELF, Runtime, VM, Zielnetz oder Hardware. Interne Originalmechanik wird durch diese Zuordnung nicht automatisch zur Anforderung an einen Ersatzprovider.
