> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-083 — `idk_IoDrvWriteOutputs`

## Ergebnis

**VERIFIZIERT** — Der beobachtete Kontrollfluss führt zunächst einen indirekten Vorbereitungsaufruf aus. Bei dessen Rückgabewert ungleich null kehrt die Funktion sofort mit `2` zurück. Andernfalls durchläuft sie eine äußere Folge von 16-Byte-Schritten und darin eine Folge von 20-Byte-Schritten. Sie bearbeitet nur äußere Einträge mit dem beobachteten Halbwort `0x8008` und innere Einträge, deren verknüpfter Zeiger und Kontextzeiger die gezeigten Gleichheits-/Nulltests passieren. Je nach Zeigervergleich wird ein direkter oder indirekter Callback ausgeführt. Danach folgt für geeignete Datensätze entweder `FUN_00015e38` oder ein indirekter Schreibaufruf. Nur deren Rückgaben überschreiben das finale Register `sl`; bleibt beides aus, bleibt dessen Initialwert null erhalten. Nach dem Durchlauf wird ein indirekter Abschlussaufruf ausgeführt, dessen Rückgabewert verworfen wird. Der abschließende Rückgabecode ist `0`, falls `sl` null ist, sonst `2`.

Die Callrückgaben haben getrennte Datenflüsse. `r8` erhält ausschließlich die Rückgabe von `FUN_0001590c` und steuert, ob dieser Call für spätere passende äußere Einträge erneut ausgeführt wird; sie speist nicht `sl`. Die Rückgaben von `FUN_00015b24`/dem indirekten Callback werden als Basis-/Adresswert weiterverwendet und speisen ebenfalls nicht unmittelbar `sl`. `sl` erhält Rückgaben nur von `FUN_00015e38` oder dem indirekten Schreibcall bei `0x6648`; spätere solche Calls überschreiben frühere Werte. Der Abschlusscall bei `0x6508` verändert `sl` nicht. Diese Statusaggregation ist keine ODER-Verknüpfung: falls mindestens einer der beiden `sl`-schreibenden Calls vorkommt, entscheidet der letzte davon über den abschließenden Null-/Nichtnulltest; sonst bleibt `sl` null. Die Bedeutung der Rückgabewerte als Erfolg/Fehler ist **OFFEN**.

## Identität, Adressräume und Befundstatus

| Eigenschaft | Beobachtung |
|---|---|
| Artefakt | `libIoDrvKbus.so.0.0.1`, ELF32 little-endian ARM |
| SHA-256 | `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` |
| Dynsym | `idk_IoDrvWriteOutputs`, ELF-VA `0x64a8`, Größe 436 (`0x1b4`), Abschnitt 12 |
| ELF-VA / Dateioffset | Im ersten LOAD-Segment beginnt beides bei 0; für diese Funktion stimmen ELF-VA und Dateioffset daher numerisch überein: `0x64a8..0x665b` inklusive. |
| Ghidra-Ladeadresse | Ghidra meldet Eintritt `0x164a8`, Körper `0x164a8..0x16657` inklusive. Die hier beobachtete Differenz zur ELF-VA beträgt `+0x10000`; dies ist eine Ladeadressabbildung, keine Laufzeitadresse. |
| Ghidra-Körper | 432 Bytes; zusammenhängend, vollständiger FunctionManager-AddressSet, Eintritt enthalten. |
| Rest der Dynsym-Größe | Die letzten vier Bytes `0x6658..0x665b` sind im Disassembler als Literal `0x00070007` beobachtet; sie gehören zur Dynsym-Größe, aber nicht zum Ghidra-Instruktionskörper. |
| Laufzeitadresse | **OFFEN** — keine Laufzeitmessung und keine Laufzeitabbildung erhoben. |
| Haupt-Evidence | `ev_6194ece0a7a14aec68e5779961be70c5f415e05d5ad28a9fdb09d461539ae983` in `evidence.json` |

Ghidra zeigte symbolgebundene Instruktionen unter `0x164a8..0x16657`; GNU ARM objdump zeigte denselben Instruktionsstrom unter ELF-VA `0x64a8..0x6654` und das Literal bei ELF-VA `0x6658`. Die Instruktionen werden unten nach ELF-VA referenziert. Eine Dateioffset-Angabe ist nur für ELF-Bytes, nicht für Ghidras um `0x10000` versetzte Ladeadresse gemeint.

## Kontrollfluss- und Callsite-Tabelle

Callsite-Adressen in dieser Tabelle sind ELF-VA; der passende Ghidra-VA liegt jeweils `0x10000` höher. „Indirekt, Ziel OFFEN“ bedeutet, dass Ghidra/REA den Call-Instruktionsort beobachtet, aber kein Ziel auflösen konnte. Call-Namen wie `FUN_...` sind ausschließlich die von Ghidra vergebenen Bezeichner; ihr Body wurde nicht untersucht.

| ELF-VA / Ghidra-VA | Beobachteter Pfad und Argumentbindung | Callklassifikation / Folgewirkung |
|---|---|---|
| `0x64cc` / `0x164cc` | Lädt den Funktionszeiger aus `[*([ctx+0x61c])+0x30]`; ruft ihn mit `ctx+0x618` und `0` auf. | Indirekt, Ziel **OFFEN**. Ergebnis wird geprüft. Ungleich null springt zum Epilog und liefert `2`; null öffnet den Verarbeitungspfad. |
| `0x6508` / `0x16508` | Lädt den Funktionszeiger aus `[*([ctx+0x61c])+0x40]`; ruft ihn mit `ctx+0x618` und `0` auf, nachdem die äußere Folge beendet ist. | Indirekt, Ziel **OFFEN**. Rückgabewert wird verworfen; danach wird das unveränderte `sl` auf `0`/`2` abgebildet. |
| `0x6544` / `0x16544` | Für einen äußeren Eintrag mit Halbwort `0x8008`, solange `r8` null ist: ruft `FUN_0001590c` mit dem 32-Bit-Wert bei Eintrag+`0x14` und einer lokalen Adresse auf. | Direkter lokaler Call. Rückgabe wird in `r8` gespeichert; `r8` verhindert weitere solche Calls nur solange es ungleich null ist. Sie speist nicht `sl`. Der lokale 32-Bit-Wert wird anschließend in das Wort bei Eintrag+`0x4` geschrieben, nachdem Bit `0x100` gelöscht wurde. |
| `0x65c0` / `0x165c0` | Wenn der Zeiger aus innerem Eintrag+`0x10` dem zuvor gelesenen Objektzeiger entspricht: `FUN_00015b24(innerer_Eintrag, lokale_Adresse)`. | Direkter lokaler Call. Rückgabe wird bei `0x65c8` nach `r3` kopiert und anschließend als Basiswert für die Berechnung des Schreiborts verwendet; sie ist kein finaler Statuswert. |
| `0x65fc` / `0x165fc` | Alternativpfad, wenn Objektgröße null ist, die unteren 3 Bits des Halbworts bei innerem Eintrag+`0x0c` gesetzt sind oder die Prüfung mit dem Literal bei ELF-VA `0x6658` nicht null ergibt: `FUN_00015e38(objektzeiger, innerer_Eintrag)`. | Direkter lokaler Call. Rückgabe wird bei `0x664c` nach `sl` kopiert und bleibt bis zu einem späteren solchen Call oder Schreibcall erhalten. Danach folgt der innere Schleifenfortschritt. |
| `0x6610` / `0x16610` | Wenn der Zeiger aus innerem Eintrag+`0x10` nicht dem Objektzeiger entspricht: lädt einen weiteren Zeiger von diesem Ort und ruft dessen erstes Wort mit `(innerer_Eintrag, lokale_Adresse)` auf. | Indirekt, Ziel **OFFEN**. Rückgabe wird im gemeinsamen Folgeschritt nach `r3` kopiert und als Basiswert für die Berechnung des Schreiborts verwendet; sie ist kein finaler Statuswert. |
| `0x6648` / `0x16648` | Im Schreibpfad: lädt den Zeiger aus `[*([ctx+0x61c])+0x3c]`; Argumente sind der aus Objekt+`0x0c` plus Halbwort bei Eintrag+`0x8` geteilt durch 8 berechnete Ort, die berechnete Länge, ein Offset aus Halbwort Eintrag+`0x0a` geteilt durch 8 sowie der Zeiger auf das Objekt. | Indirekt, Ziel **OFFEN**. Rückgabe wird bei `0x664c` nach `sl` kopiert und bleibt bis zu einem späteren `0x65fc`- oder `0x6648`-Call erhalten. |

### Schleifen, Abzweigungen und Rückkehr

- Bei ELF-VA `0x64e0..0x64e8` wird die äußere Endadresse als Basis `+ 16 * Anzahl` gebildet; `0x64f0..0x64f4` prüft auf Schleifenende. Fortschritt ist `+16` bei `0x657c..0x6580`.
- Das äußere Eintrags-Halbwort bei Offset `0` wird bei `0x6528..0x6530` mit `0x8008` verglichen. Andere Werte überspringen den Eintrag.
- Die Verarbeitung der inneren Folge verwendet die bei äußerem Eintrag+`0x0c` gelesene Basis, die Anzahl bei +`0x08` und Schrittweite 20: Endadresse = Basis + 20 × Anzahl (`0x6564..0x6578`). Innerer Schritt ist +20 (`0x6650`); Schleifenrücksprung erfolgt bei `0x6654`.
- Für jeden inneren Eintrag wird über dessen erstes Wort ein Objektzeiger gelesen; dessen Wort bei +`0x10` wird geprüft. Null, falscher Kontextzeiger oder null Callback überspringen zur nächsten inneren Position (`0x6584..0x65ac`).
- Im gemeinsamen Verarbeitungspfad wird zunächst ein Callbackergebnis ermittelt (`0x65c0` oder `0x6610`). Dieses gelangt nach `r3` und dient im Schreibpfad als Basiswert für die Ortsberechnung. Wenn die Prüfungen bei `0x65d0..0x65f0` den Schreibpfad zulassen, folgt der indirekte Call bei `0x6648`; sonst folgt der lokale Call bei `0x65fc`. Nur diese beiden Calls schreiben ihren Rückgabewert nach `sl`.
- Der einzige beobachtete Rückkehr-Epilog liegt bei `0x6518..0x651c`: Vorbereitung nicht-null liefert direkt `2`; nach Schleifenende wird der Abschlussaufruf ausgeführt, dessen Rückgabe verworfen wird, und `sl` wird zu `0` bei null beziehungsweise `2` bei ungleich null abgebildet. `sl` startet bei null und bleibt null, wenn kein `0x65fc`- oder `0x6648`-Call ausgeführt wurde.
- **VERIFIZIERT** — Im beobachteten FunctionManager-Körper gibt es keinen weiteren Returnblock. Ghidra meldet vier nicht aufgelöste indirekte Call-Ziele: `0x164cc`, `0x16508`, `0x16610`, `0x16648` (Ghidra-VA). Diese Ziele bleiben **OFFEN**.

## Relevante Datenbindungen

Alle folgenden Beziehungen sind beobachtete Lese-/Schreiboperationen in diesem Funktionskörper; sie behaupten keine benannten C-Structs oder API-Verträge.

| Ort / Daten | Beobachtete Bindung | Befundstatus |
|---|---|---|
| `param_1`, erstes Wort | Wird als Zeiger auf den Kontext weiterverwendet. Kontext+`0x618` wird an vorbereitenden/abschließenden indirekten Call gebunden und für den inneren Zeigervergleich benutzt; Kontext+`0x61c` wird als Basis für drei Funktionszeiger-Felder verwendet. | VERIFIZIERT |
| Funktionszeigerfelder | Basiszeiger aus Kontext+`0x61c`, dann +`0x30`, +`0x40`, +`0x3c` für Vorbereitungs-, Abschluss- und Schreibcall. Die konkreten Ziele sind nicht statisch aufgelöst. | VERIFIZIERT / Ziele OFFEN |
| Äußere Folge (`param_2`) | Äußerer Schritt 16 Bytes; erster Zeigerwert ist ein Descriptorzeiger. Die Schleifengrenze nutzt `param_3` als Anzahl. | VERIFIZIERT |
| Descriptor | Halbwort +`0x0` muss `0x8008` sein. Wort +`0x4`: Bit `0x100` wird gelöscht und das lokale Wort hineingemischt. Wort +`0x14` wird an den Call bei `0x6544` übergeben. | VERIFIZIERT |
| Innere Folge | Basis wird aus äußerem Eintrag+`0x0c`, Anzahl aus +`0x08` gelesen; Schrittweite 20 Bytes. Das erste Wort eines inneren Eintrags wird dereferenziert; vom erhaltenen Objekt werden Wörter/Halbwords an +`0x0`, +`0x0c`, +`0x10` und vom Eintrag Halbwords an +`0x08`, +`0x0a`, +`0x0c` verwendet. | VERIFIZIERT |
| Literal bei ELF-VA `0x6658` | Wortwert `0x00070007`, Referenz kommt aus der Bedingung bei Ghidra-VA `0x165e8`. Numerik allein liefert keine Feld- oder Statusbezeichnung. | VERIFIZIERT (Wert), Bedeutung OFFEN |
| Zeichenketten | Keine Zeichenkettenreferenz im Funktionsdossier. | VERIFIZIERT (keine im Dossier) |

## Beobachtungen, Alternative und Restunsicherheit

1. **VERIFIZIERT** — Finale Null-/Nichtnullabbildung: `sl` wird nur durch die Rückgabe von `FUN_00015e38` bzw. des indirekten Calls bei `0x6648` überschrieben. Der letzte dieser ausgeführten Calls bestimmt den finalen Null-/Nichtnullwert; ohne diese Calls bleibt der Initialwert null. `r8` ist getrennt und wird nur vom Call bei `0x6544` beschrieben/verwendet. Die Rückgaben bei `0x65c0`/`0x6610` dienen als Basis-/Adresswert, nicht als finaler Status. Der Call bei `0x6508` verwirft seine Rückgabe.
2. **HYPOTHESE** — Ein Nichtnullwert in `sl` könnte einen Fehlerzustand bezeichnen. Aus dieser Funktion allein ist nur die Null-/Nichtnullbehandlung für den Rückgabecode belegt; die Bedeutung einzelner Werte bleibt unbenannt.
3. **OFFEN** — Ziele der vier indirekten Calls und deren Seiteneffekte/Rückgabeverträge.
4. **OFFEN** — Bedeutung von `0x8008`, `0x100`, `0x70007`, allen Offsets und der Schrittweiten im herstellerseitigen Typ-/API-System. Dieser Bericht vergibt keine solchen Namen.
5. **OFFEN** — Ob das vier Byte große Literal Teil eines vom Linker angehängten Funktionsliterals oder durch die ELF-Symbolgrößenkonvention anders klassifiziert werden sollte. Beobachtet ist nur: Dynsym-Größe umfasst es; Ghidra-Funktionskörper nicht; Instruktion bei `0x65e8` referenziert es.
6. **OFFEN** — Laufzeitbasis/Relokation im Prozess. Es wurde keine Runtime ausgeführt.

Alternative Erklärung für die Statusbeobachtung: Ein nichtnull `sl` könnte im konkreten Vertrag etwas anderes als „Fehler“ bedeuten. Daher lautet der verifizierte Befund bewusst nur „Null-/Nichtnullabbildung der letzten `sl`-schreibenden Callrückgabe“; die Interpretation als Fehler ist ohne Callee-Vertrag eine **HYPOTHESE**.

## Methode, Toolprofil und Scope

- Eingabehash wurde vor der Analyse neu berechnet und stimmte exakt mit dem vorgegebenen SHA-256 überein.
- REA zuerst: lokales Artefakt mit REA `open_binary` geöffnet; SHA-256 und ARM/ELF-Format bestätigt. Danach `analyze_function(idk_IoDrvWriteOutputs)` als einzige REA-Evidence-Erhebung verwendet.
- REA-Profil: Ghidra `12.1.4`, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`, ARM ELF, `ghidra-default`, Ephemeral-Import, unveränderliche Quellbytes. Der vollständige Evidence-Datensatz enthält Pseudocode, Instruktionslisting, CFG, Callreferenzen, Datenreferenzen, referenzierte Namen und Value-Flow.
- Zulässiger Lücken-Fallback: GNU readelf/objdump (`2.44`). `readelf -Ws` bestätigte Dynsym-Symbol/Größe; der begrenzte ARM-Disassemblybereich zeigte den instruktionsfreien Literalrest. Keine Funktion außerhalb des Zielkörpers wurde disassembliert oder analysiert.
- Pseudocode im Evidence-Bundle ist als Ghidra-Decompilerableitung zu lesen, nicht als Quelltext.
- Die drei direkten lokalen Ziele wurden ausschließlich an ihren Call-Sites als Ghidra-Funktionsziele klassifiziert. Ihre Bodies wurden nicht untersucht. Keine rekursive Calleeanalyse.
- Ausgeschlossen: Code vor ELF-VA `0x64a8` und nach `0x665b`, `idk_IoDrvReadInputs`, übrige Lifecycle-/Scan-/Diagnose-/Push-Pfade, Runtime, Geräte, Netzwerk, VM und Repository-Dateien.

## Dateien, Validierung und Hashes

Erzeugte Dateien in diesem Work-Package-Verzeichnis:

| Datei | Zweck | SHA-256 |
|---|---|---|
| `report.md` | Dieser Befundbericht samt Kontrollfluss-/Callsite-Tabelle | siehe `SHA256SUMS` |
| `evidence.json` | Kanonischer REA-Export; exakt 1 Evidence-Record für den Zielkörper | siehe `SHA256SUMS` |
| `validate.py` | Lokaler Scope-/Evidence-/Manifestvalidator | siehe `SHA256SUMS` |
| `SHA256SUMS` | Hashmanifest der drei obigen Dateien | nicht selbst im Manifest enthalten |

Validierung: `python3 validate.py` — erwartet **PASS**. Ergebnis wird separat durch Ausführung protokolliert; Laufzeitverhalten des ELF wurde nicht getestet.
