> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-082 — FW31 `idk_IoDrvReadInputs`

## Ergebnis

**VERIFIZIERT:** Die Funktion startet zunächst über einen indirekten Tabellenaufruf. Bei Erfolg durchläuft sie eine Liste von 16-Byte-Einträgen. Der Selektor `0x800a` aktualisiert ein globales Byte und überträgt dessen Bitwert in konfigurierte Zielbytes. Der Selektor `0x8008` findet passende 20-Byte-Einträge, ruft einen Eintragscallback auf und verwendet anschließend entweder den lokalen Helfer bei `0x5b5c` oder die indirekte Kopierfunktion bei Tabellenoffset `0x50`. Beide zuletzt genannten Wege liefern den Wert, aus dem der abschließende Funktionsstatus gebildet wird.

Der Status ist keine ODER-Aggregation über alle Kopien: Er ist `0`, wenn kein qualifizierter Transfer einen von null verschiedenen Rückgabewert hinterlässt; sonst wird `2` zurückgegeben. Bei mehreren qualifizierten Transfers überschreibt jeder spätere Transfer den gespeicherten Wert. Frühe Reject-Verzweigungen liefern unmittelbar `2`.

## Umfang und Adressräume

Eingabe: `libIoDrvKbus.so.0.0.1`, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` (**VERIFIZIERT**, vor Analyse erneut berechnet).

| Koordinate | Beobachtung |
|---|---|
| ELF-VA und Dateioffset | Symbol `idk_IoDrvReadInputs`: `0x6120`, Größe `904` (`0x388`), also Bytebereich `[0x6120, 0x64a8)`. Für diesen `.text`-Ausschnitt stimmen ELF-VA und Dateioffset überein (`.text`: VA/Offset `0x1eb8`). |
| Ghidra-Ladeadresse | Funktionseinstieg `0x16120`; beobachteter Bias gegenüber ELF-VA `+0x10000`. Body `0x16120..0x1649b`, 892 Bytes (`0x37c`). |
| Rest des ELF-Symbolbereichs | `0x649c..0x64a7` (12 Bytes) sind Literal-/Konstantenwörter, keine vom Ghidra-Funktionsbody dekodierten Instruktionen. Sie werden aus dem Body bei `0x6158`, `0x61fc` und `0x63f4` gelesen. Damit ist der gesamte symbolgebundene Bereich untersucht, obwohl der Instruktionsbody kürzer ist. |
| Laufzeitadresse | **OFFEN:** Statische ELF- und Ghidra-Koordinaten belegen keine konkrete Laufzeit-Ladeadresse; die Bibliothek wurde nicht ausgeführt. |

Ghidra-Evidence **E1** meldet genau den vollständigen, zusammenhängenden Bodybereich `0x16120..0x1649b` mit 892 Bytes, vollständige Assembly und CFG, aber sechs Call-Ziele ohne aufgelöste Adresse. Die ELF-Symbolgröße und die letzten zwölf Bytes wurden wegen dieser beobachteten Grenzdifferenz mit dem benannten `readelf`-/ARM-`objdump`-Fallback geprüft. GNU Binutils-Version beider Werkzeuge: `2.44`. Das systemweite `objdump` 2.44 konnte die Architektur nicht dekodieren; `arm-linux-gnueabihf-objdump` 2.44 dekodierte das ARM-ELF korrekt. Diese Befunde sind statische Artefaktbeobachtungen, keine Laufzeitmessungen.

## Kontrollfluss und Rückgaben

Fundstellen in der Tabelle sind ELF-VA; Ghidra-Adressen ergeben sich durch `+0x10000`.

| Fundstelle | Bedingung/Aktion | Folgezweig oder Rückgabe |
|---|---|---|
| `0x6144–0x614c` | Indirekter Aufruf über Tabellenoffset `+0x44`; Argumente: Kontextzeiger aus `[param_1]` und `0`. | Nichtnull: gemeinsamer früher Rejectpfad `0x6494`, Rückgabe `2`, kein Tabellenaufruf bei `+0x54`. Null: Verarbeitung fortsetzen. |
| `0x6150–0x6174` | Berechnet das Ende einer Liste aus `param_2` und `param_3 * 16`; Schleife über Einträge mit Schrittweite 16. | Leere Liste: Abschlussaufruf `+0x54`, danach Rückgabe aus dem Transferstatus. |
| `0x61a4–0x61b0` | Liest das 16-Bit-Feld am Eintragsziel und vergleicht mit `0x800a`. | Treffer: Statusbyte-/Bitabbildungszweig. Sonst wird `0x8008` geprüft. |
| `0x61b4–0x6258` | Für `0x800a`: falls Feld `+8` nicht null, indirekter Callback über dessen Tabellenoffset `+0x58`, dann Ableitung eines Bytes `0/1` und einer Maske `0/0x100`; aktualisiert das globale Byte und Bit `0x100` im Primärziel sowie optionalen verknüpften Zielen. | Feld `+8` null: Statusbyte bleibt aus vorherigem Zustand; Eintragsliste wird trotzdem verarbeitet. Feld nicht null: setzt internes Gate auf `1`. |
| `0x6264–0x6288` | Schleife über zugehörige 20-Byte-Einträge (`count * 0x14`). | Erreichtes Listenende: nächster 16-Byte-Eintrag; sonst wird Typfeld `+0xc` geprüft. |
| `0x6290–0x62a0` | Typfeld `+0xc == 1`; Quellbitindex aus `+8` muss höchstens `7` sein. | Größer als `7`: gemeinsamer früher Rejectpfad, Rückgabe `2`. Gültig: Quellbit des globalen Bytes auf Zielbitindex `(+10 & 7)` abbilden; Zielbyte bei `(+10 >> 3)` per Read-Modify-Write ändern. |
| `0x6300–0x6324` | Alternativ Typfeld `+0xc == 8`; die unteren 19 Bits des 32-Bit-Feldes `+8` müssen null sein. | Ungleich `8` oder Maskenwert ungleich null: früher Rejectpfad, Rückgabe `2`. Sonst wird das globale Byte bei Zielbyte `(+10 >> 3)` geschrieben. |
| `0x6328–0x6360` | Typfeld `0x8008`; wenn das interne Gate null ist, direkter Aufruf `FUN_0001590c` mit Feld `+20` und Ausgabezeiger. Aktualisiert danach Bitmaske `0x100` des Selektoreintrags. | Verarbeitung der zugehörigen 20-Byte-Einträge beginnt. Rückgabewert des Helfers wird nicht direkt in den abschließenden Transferstatus übernommen. |
| `0x6378–0x63c0` | Filtert 20-Byte-Einträge: eingebetteter Zeiger nicht null, dessen erstes Wort entspricht dem Kontextwert `[ctx+0x618]`; bei eingebettetem Feld `+0x18 == 3` muss Feld `+0x1c` auf den aktuellen 16-Byte-Eintrag zeigen; Callback-Zeiger bei Eintrag `+0x10` muss nicht null und ungleich dem eingebetteten Zeiger sein. | Nicht passende Einträge werden übersprungen. Passende Einträge gehen zum Callback-/Transferpfad. |
| `0x63c4–0x6414` | Indirekter Eintragscallback, Argumente: 20-Byte-Eintrag und Stackpuffer. Wenn eingebettetes Feld `+0x10` null ist oder die Prüfungen bei `0x63e4–0x63fc` fehlschlagen, direkter Aufruf `FUN_00015b5c`. | Rückgabewert von `FUN_00015b5c` wird als aktueller Transferstatus gespeichert. Sonst weiter zum Kopierpfad. |
| `0x6418–0x6470` | Kopierpfad: berechnet Byte-Länge (`Feld +0xc >> 3`), setzt vor dem Kopieren den Zielbereich mit `memset` auf null, wenn die angeforderte Länge das beobachtete Feld `+8` des eingebetteten Objekts überschreitet; Kopierlänge wird auf das Minimum beider Längen begrenzt. Dann indirekter Kontextaufruf über Tabellenoffset `+0x50`. | Rückgabewert dieses Aufrufs wird als aktueller Transferstatus gespeichert. |
| `0x6474–0x6490` | Ruft den Callback aus Eintrag `+0x10`, Tabellenoffset `+4`, mit Callback-Ergebnis und Eintragszeiger auf; iteriert weiter. | Callback-Rückgabe wird nicht in den Transferstatus übernommen. |
| `0x6494–0x6498` | Gemeinsamer früher Rückgabeblock. | Rückgabe `2`. |
| `0x6178–0x619c` | Normalabschluss: indirekter Aufruf über Kontexttabellenoffset `+0x54`; danach wird nur geprüft, ob der Transferstatus null ist. | Null → `0`; nicht null → `2`. Rückgabe des Aufrufs `+0x54` wird nicht aggregiert. |

### Direkte und indirekte Call-Sites

Ghidra zählt sechs Calls ohne aufgelöstes Ziel. Die Tabelle ordnet jeden anhand seiner Instruktion und der dabei geladenen Zieladresse bzw. Tabellenposition ein; die Bodies der Callees wurden nicht rekursiv analysiert.

| ELF-VA | Klasse und Zielbeobachtung | Beobachtete Argument-/Rückgabeverwendung |
|---|---|---|
| `0x6144` | Indirekt, `[ctx+0x61c] + 0x44` | Kontextwert `[ctx+0x618]`, `0`; Nichtnull-Rückgabe steuert den sofortigen Rejectpfad. |
| `0x6188` | Indirekt, `[ctx+0x61c] + 0x54` | Kontextwert `[ctx+0x618]`, `0`; Rückgabe ignoriert. |
| `0x61d8` | Indirekt, Objekt aus Selektorfeld `+8`, dessen Tabelle `+0x58` | Objektwert `+0x618`, zwei Nullargumente, Zeiger auf lokales Wort; Rückgabewert und Ausgabewort bestimmen Statusbyte/`0x100`-Maske. |
| `0x6344` | Direkt, `FUN_0001590c` (Ghidra `0x1590c`, ELF-VA `0x590c`) | Zeiger aus Selektorfeld `+20`, Zeiger auf lokales Wort; Rückgabe setzt Gate `iVar4`. |
| `0x63d0` | Indirekt, Funktionszeiger aus passendem 20-Byte-Eintrag `+0x10` | Eintragszeiger und Stackpuffer; Rückgabe dient als Ziel-/Kontextwert des nachfolgenden Transferpfads. |
| `0x6410` | Direkt, `FUN_00015b5c` (Ghidra `0x15b5c`, ELF-VA `0x5b5c`) | Eingebetteter Zeiger, Eintragszeiger, `[ctx+0x61c]`, Callback-Ergebnis; Rückgabewert wird Transferstatus. |
| `0x6434` | PLT, `memset` (`0x1d40`; Relokationssymbol `memset@GLIBC_2.4`) | Füllt berechneten Zielbereich mit null; Rückgabe wird hier nicht für den Funktionsstatus verwendet. |
| `0x6470` | Indirekt, `[ctx+0x61c] + 0x50` | Eingebetteter Zeiger, `0`, Quellbyteoffset, begrenzte Länge, Zielzeiger; Rückgabewert wird Transferstatus. |
| `0x6488` | Indirekt, Funktionszeiger aus Eintrag `+0x10`, Tabellenoffset `+4` | Callback-Ergebnis und Eintragszeiger; Rückgabe ignoriert. |

`0x6344` und `0x6410` sind direkte lokale Ziele innerhalb der Datei; `0x6434` ist ein PLT-Aufruf. Zieladressen der sechs indirekten Calls bleiben **OFFEN**. Es wurden keine Callee-Bodies untersucht.

## Beobachtete Datenbindungen

Alle folgenden Feldbezüge sind bytegenaue Beobachtungen aus der ARM-Assembly bzw. dem Ghidra-Pseudocode; sie erhalten bewusst keine erfundenen API-, Struktur- oder Statusnamen.

- `param_1`: erster gelesener Zeiger ist der Kontext; von ihm stammen die Wörter `+0x618` und `+0x61c`.
- `param_2`: Beginn der 16-Byte-Eintragsliste; `param_3` ist die Eintragszahl. Jeder Listeneintrag liefert unter anderem Zeiger/Felder `+0`, `+8`, `+0xc` und `+0x14`.
- Selektor `0x800a`: Feld `+8` enthält bei Nichtnull ein Objekt, dessen Tabelle bei `+0x61c` und dessen Argument-/Kontextwort bei `+0x618` gelesen wird. Feld `+4` mehrerer verbundener Ziele wird mit `& ~0x100 | statusmaske` aktualisiert.
- Selektor `0x8008`: Feld `+0x14` wird an `FUN_0001590c` gegeben. Zugehörige 20-Byte-Einträge werden mit Schrittweite `0x14` verarbeitet. Ihre Felder `+8`, `+0xa`, `+0xc`, `+0x10` und `+0x14` steuern Filter, Bytebereiche und Callbacks.
- Statusbyte: ARM-Literal bei ELF-VA `0x649c` ergibt bei PC-relativer Addition das ELF-Ziel `0xd5ac8` (Ghidra-Adresse `0xe5ac8`). Das liegt im `.bss`-Bereich. Es wird in der `0x800a`-Verzweigung beschrieben und in den Bitabbildungszweigen gelesen. `0x64a0` referenziert dieselbe Adresse. Die Bezeichnung `DAT_000e5ac8` ist ein Ghidra-Label, keine semantische Typaussage.
- Konstante: Wort bei ELF-VA `0x64a4` ist `0x00070007`, im Kopierzweig mit `&` auf das Wort bei Eintragsoffset `+8` angewandt.
- Direkte Relokationsbindung: `.rel.plt` bindet `memset` an `0x1902c`; im Funktionsbody wird der Aufruf an `0x1d40` als `memset@plt` ausgegeben. Andere indirekte Tabellenoffsets werden nicht als API-Namen interpretiert.

## Befundstatus, Alternativerklärung und Restunsicherheit

- **VERIFIZIERT:** Symbolgrenze, Name, Größe, Bibliotheks-Hash, Ghidra-Funktionsbody, Assembly, CFG und die sechs unaufgelösten indirekten Calls sind statisch belegt.
- **VERIFIZIERT:** Frühe Reject-Verzweigungen und Eintragskodierungen außerhalb der gezeigten Bedingungen liefern `2`; Normalabschluss liefert `0` oder `2` nach Nichtnulltest des zuletzt gespeicherten Transferergebnisses.
- **HYPOTHESE:** Das globale Byte und Bit `0x100` scheinen einen gemeinsamen Zustand zwischen Einträgen/verbundenen Zielen abzubilden. Der Code belegt die Schreib-/Lesebeziehungen, aber nicht deren Domänenbedeutung.
- **Alternativerklärung — OFFEN:** Der Wert `2` könnte ein allgemeiner Fehlercode sein oder einen spezifischen Fehler-/Statusfall bezeichnen. Numerik allein erlaubt keine Benennung.
- **OFFEN:** Semantik und Nebenwirkungen der sechs indirekten Callziele sowie der beiden lokalen Helfer bleiben unanalysiert (Scope-Vorgabe); deshalb ist die fachliche Bedeutung ihrer Rückgabewerte unbekannt.
- **OFFEN:** Laufzeit-Basisadresse, tatsächliche Objekte und Ausführungsverhalten wurden nicht beobachtet.
- **OFFEN:** Ghidras Liste kennt drei direkte Ziele. Der verwendete ARM-`objdump` ordnet zusätzlich den PLT-Call `memset@plt` bei `0x6434` eindeutig zu. Keine dynamische Ausführung oder Rekursivanalyse.

## Werkzeuge, Profil und Validierung

- REA MCP `open_binary` und `analyze_function`; Provider Ghidra `12.1.4`, ARM, ELF; Analyseprofil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Kanonischer Scope-Export: `rea-evidence-bundle.json`, genau ein Evidence-Datensatz, **E1** = `ev_2b274ea632f2bf3339ba59b8cf1d282c3337e63aa20b3c5aee6a4c9d392c14e0`. `rea-evidence-canonical.json` ist die vom lokalen REA-CLI erneut validierte byteidentische Kopie.
- Fallback nach beobachteter REA-Layout-Providerlücke: GNU `readelf 2.44` und `arm-linux-gnueabihf-objdump 2.44`. `readelf -Ws` bestätigte Symboleintrag `0x6120`, Größe `904`, und Nachbarsymbol ab `0x64a8`; `readelf -SW` bestätigte `.text`-VA/Offset-Gleichheit. ARM-Disassembly des ausgewählten Bereichs zeigte Instruktionen bis `0x6498` und die drei Literalwörter `0x649c..0x64a7`. Normales `objdump 2.44` meldete `architecture UNKNOWN`; kein stiller Ersatz durch dieses Ergebnis.
- `rea evidence-export` validierte den Export und erzeugte byteidentischen kanonischen JSON-Export (548180 Bytes, 1 Datensatz). Validator: `validate.sh`.
- Prüfung: **PASS** — Hash der Eingabe stimmt; kanonischer Evidence-Export lässt sich erneut validieren und ist byteidentisch; der einzige zitierte Evidence-ID ist in diesem Bundle vorhanden; Scope-/Reportdateien liegen ausschließlich in diesem Ausgabeverzeichnis.
- Ausführung/Hardwaretests: **NOT_RUN** (statische Offlineanalyse, keine Runtimeausführung).

## Erzeugte Dateien

| Datei | Zweck | SHA-256 |
|---|---|---|
| `report.md` | Befundbericht für WP-XE164-082 | siehe `SHA256SUMS` |
| `rea-evidence-bundle.json` | kanonischer, auf den Funktionsdossier-Datensatz beschränkter REA-Evidence-Export | siehe `SHA256SUMS` |
| `rea-evidence-canonical.json` | byteidentische REA-CLI-Kanonisierungs-/Validierungsreferenz | siehe `SHA256SUMS` |
| `validate.sh` | lokaler Offline-Validator für Hash, kanonischen Export und Evidence-ID | siehe `SHA256SUMS` |
| `SHA256SUMS` | Hashmanifest für Eingabe und erzeugte Dateien (Selbsthash ausgenommen) | siehe Einträge |
