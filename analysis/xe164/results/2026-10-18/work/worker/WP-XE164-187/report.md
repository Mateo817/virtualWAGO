> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-187 — begrenzte Provenienz des Stores bei `0x2f94`

## Ergebnis

**VERIFIZIERT:** Der Quellwert des Stores ist innerhalb der erlaubten Instruktionen vollständig berechenbar. Beim Store `0x2f94: str r2,[r4,#0x61c]` enthält `r2` den numerischen Wert `0x1a270`, abgeleitet aus dem 4-Byte-Literal bei Datei-Offset `0x3360` und den folgenden ARM-Additionen.

**OFFEN:** Die Speicherbasis `r4` lässt sich nicht auf einen konkreten numerischen Wert oder ein Objekt zurückführen. Im begrenzten, über den Funktionspfad zu `0x2f94` erreichbaren Instruktionsbereich gibt es keine explizite lokale Zuweisung an `r4`; der Prolog bei `0x2ddc` sichert den Eintrittswert. Wegen der ausgeschlossenen Callee-Effekte wird nicht behauptet, dass unbekannte Aufrufe `r4` unverändert lassen. Seine Herkunft und Objektidentität bleiben unbekannt. Daher ist der effektive Zielwert nur als `r4 am Store + 0x61c` gebunden, nicht als konkrete Adresse.

## Quelle und Grenzen

Vollständiger Input-Hashread (Identitätsprüfung): Größe `25976`, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.

| Zulässiger Bereich | Ebene | Länge | SHA-256 |
|---|---|---:|---|
| `[0x2c00,0x2fb8)` | Datei-Offset; A32-Codebereich im adressierten Disassembly | 952 Byte / 238 Wörter | `9fd4438ad19995ddfea8a89e3335bbd4265d652c23e1346f2e896c34f9d10a80` |
| `[0x3360,0x3364)` | Datei-Offset; DATA-only Literalwort | 4 Byte | `e88c98749d7991a20a4c4ee258b8f07acba58b71fb2a29e64e6597b0d6040077` |

REA-first: akzeptierte same-hash Evidence E-XE164-213/WP-XE164-186 wurde wiederverwendet. Deren Bericht dokumentiert, dass eine aktive REA-Suche nach dem exakten Hash keine Records ergab; die vorhandenen begrenzten same-hash Dossiers enthalten keinen Provenienz-Trace für `r4`/`r2` an diesem Store. **Coverage-Lücke einmalig dokumentiert:** REA deckt die hier benötigte lokale Registerbindung nicht ab. Danach wurde ausschließlich der exakt begrenzte Raw-Codebereich mit GNU ARM `objdump` 2.44 dekodiert, mit den vier Literalbytes separat gelesen und per Python 3.13.5 rechnerisch sowie gegen die eingegrenzten Bytes validiert. Es erfolgte kein neuer Ghidra-Import.

Die Auswertung des Eingabeartefakts ist auf Instruktionen in `[0x2c00,0x2fb8)` und das Wort `[0x3360,0x3364)` begrenzt. `flow.tsv` enthält die relevanten Befehle und CFG-Gates. Der restliche Binärinhalt wurde nicht interpretiert.

**Scope-Audit — FAIL:** Bei einer anfänglichen breiten `rg`-Suche in den vorhandenen XE164-Text-/Evidence-Dateien zeigte die Toolausgabe neben WP186 auch bestehende Evidence-Index-Zeilen zu E-XE164-105, -108, -124, -126, -128 und -131 sowie einen Ausschnitt aus einem früheren WP-XE164-146-Bundle mit Instruktions-/Referenzbeobachtungen um `0x11704`, `0x144a0` und `0x1454c`. Diese außerhalb des freigegebenen Codebereichs liegenden Beobachtungen wurden nicht zur Schlussfolgerung verwendet; die direkte Suche las keine Binärbytes außerhalb der freigegebenen Bereiche. Da die außerhalb des erlaubten Analysebereichs liegenden Interpretationen in der Ausgabe sichtbar waren, wird der Gesamt-Scope gemäß Auftrag dennoch als **FAIL** gewertet. Die nachfolgenden bounded findings bleiben nachvollziehbar, heben diesen Scope-Verstoß aber nicht auf.

## Reaching definitions und Kontrollfluss

`0x2f94` hat im begrenzten CFG genau den unmittelbaren Vorgänger `0x2f90` (Fallthrough). Die lineare Sequenz `0x2f7c` bis `0x2f94` enthält keine Verzweigung: `r3` wird bei `0x2f7c` aus dem Literal gelesen, bei `0x2f84` gebildet und bei `0x2f8c` verändert; `r2` wird bei `0x2f88` neu berechnet und bei `0x2f90` ergänzt. Zwischen `0x2f88` und dem Store schreibt keine Instruktion erneut nach `r2`.

Der Store-Pfad wird über die Schleife bei `0x2f30..0x2f70` erreicht. `0x2f24` verzweigt bei nicht-null `r6` nach `0x32f0`; andernfalls geht der Pfad durch die Schleife. In jeder Schleifenrunde kann `0x2f40` bei nicht-null Prüfergebnis zum Inkrement `0x2f60` springen. Der Nullpfad führt über `0x2f44..0x2f5c`, wobei `r6` den Rückgabewert einer indirekten Instruktion erhält. `0x2f70` wiederholt bei `r7 < obere Grenze` die Runde. Danach verzweigt `0x2f78` bei nicht-null `r6` ebenfalls nach `0x32f0`; nur der Null-Fall fällt in die Literal-/Store-Sequenz. `0x32f0` liegt außerhalb des erlaubten Codebereichs und wird hier nur als kodiertes Branchziel benannt, nicht dekodiert oder interpretiert.

| Register am Store | Reaching definition aus erlaubtem Code | Alternativpfade / Befund |
|---|---|---|
| `r4` (Basis) | Keine explizite lokale Instruktionsdefinition vor dem Store auf dem sichtbaren Pfad vom Prolog `0x2ddc`; der Prolog sichert den Eintrittswert. | Null- und Schleifenpfade enthalten keine sichtbare `r4`-Zuweisung. Nicht-null Gates bei `0x2f24` und `0x2f78` umgehen den Store. Wegen ausgeschlossener Callee-Effekte bleibt der tatsächliche Registerwert am Store **OFFEN**. |
| `r2` (Storequelle) | `0x2f7c` lädt Literal in `r3`; `0x2f84` setzt `r3`; `0x2f88` definiert `r2`; `0x2f90` definiert `r2` erneut; `0x2f94` liest es. | Vor `0x2f7c`-Fallthrough gibt es keinen konkurrierenden Registerpfad in der lokalen Sequenz. Der Pfad mit `r6 != 0` bei `0x2f78` umgeht den Store. Auf allen lokal sichtbaren Pfaden, die den Store erreichen, gilt derselbe berechnete Wert `r2=0x1a270`. |

Die Aussage zu `r4` ist eine bounded reaching-definition-Aussage: sie beschreibt sichtbare lokale Instruktionsdefinitionen im erlaubten Code. Sie setzt keine Registererhaltung über unbekannte Aufrufe voraus und behauptet weder eine API-/Struct-Identität noch eine außerhalb des Bereichs geprüfte Eintrittsbeziehung.

## Literal- und PC-Arithmetik; getrennte Adressebenen

Das Wort an Datei-Offset `0x3360` hat Bytes `38 34 01 00`, also little-endian `0x00013438`. Die ARM-Literalinstruktion bei Instruktionsadresse `0x2f7c` kodiert `ldr r3,[pc,#0x3dc]`. In A32 ist der sichtbare PC-Wert Instruktionsadresse plus 8:

`0x2f7c + 8 + 0x3dc = 0x3360`.

Damit referenziert die Instruktion genau den erlaubten Literal-Datei-Offset `0x3360`. Die Folge rechnet im Code-/PC-Adressraum:

`r3 = (0x2f84 + 8) + 0x13438 = 0x2f8c + 0x13438 = 0x163c4`

`r2 = 0x163c4 + 0x3e80 = 0x1a244` bei `0x2f88`

`r3 = 0x163c4 + 0x3000 = 0x193c4` bei `0x2f8c`

`r2 = 0x1a244 + 0x2c = 0x1a270` bei `0x2f90`.

Die unmittelbare Store-Adressbildung ist damit `r4 am Store + 0x61c`, mit geschriebenem 32-Bit-Wert `0x1a270`. Der numerische `r2`-Wert ist eine durch Instruktionen berechnete Adresse im Code-/PC-Adressraum; es wird keine Aussage über Mapping, Inhalt oder Bedeutung des Ziels `0x1a270` getroffen. Der Store steht bei ELF-VA/Datei-Offset `0x2f94` gemäß akzeptiertem WP186 `.text`-Mapping. Das Literal ist direkt als Datei-Offset `0x3360` gebunden; die PC-Addition landet ebenfalls auf `0x3360`.

## Status, Alternative und Restunsicherheit

**VERIFIZIERT:** Wortbytes, Literal-load-PC-Arithmetik, beide Addition-Definitionen für `r2`, Storeoperand und lokaler CFG-Eintritt zum Store.

**OFFEN:** Konkreter `r4`-Wert am Store und damit absolute Storeadresse; Eintrittsursprung; mögliche nichtlokale Kontrolltransfers; alle Callee-Effekte; Speicherbelegung oder Bedeutung des Wertes `0x1a270`; Runtime und Hardware.

**HYPOTHESE:** `0x1a270` könnte im umgebenden Programm eine Adresse oder einen Zeigerwert darstellen. Das ist allein aus dem erlaubten Bereich nicht weiter bestimmbar.

Alternativerklärung: Falls ein Aufrufer den Store-Pfad mit einem anderen `r4`-Wert erreicht, wird derselbe literalberechnete Wert `0x1a270` an eine andere relative Speicherposition geschrieben. Der vorliegende Befund bindet nur die Storequelle; er identifiziert keinen Zielgegenstand.

Scope: **FAIL** wegen des oben offengelegten Evidence-Text-Reads außerhalb des freigegebenen Code-/Literalbereichs. Die Eingabeartefakt-Byteinterpretation selbst blieb auf die beiden freigegebenen Bereiche beschränkt. Keine IoDrvKbus-Datei oder -Verbindung, keine API-/Struct-/Feldsemantik, keine Callee-Effekte und keine Runtime/VM/Netz/Gerät/Hardware. Tests/Validierung: siehe `validate.py`; unabhängiger Review: **NOT_RUN**; Worker Self-Review: **PASS**.
