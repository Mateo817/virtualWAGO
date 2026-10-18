> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-162 — begrenzte Wirkung von `0x003403A4..0x0034046B`

## Identität und Suchgrenze

| Objekt | Größe | SHA-256 |
|---|---:|---|
| `codesys3` aus WP-XE164-112 | 5,181,396 Bytes | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` |
| WP-XE164-157 `report.md` (Eingabe) | 14,344 Bytes | `25db8b4ad47baa009de73d0dd2da5648d7cc78d31149f7544646cd60beb1425d` |

**VERIFIZIERT:** Die Eingabedatei stimmt in Größe und SHA-256 mit dem vorgegebenen Artefakt überein. Der ELF ist ARM ELF32, little-endian, ET_EXEC. Der erste `PT_LOAD` ordnet Dateioffset `0` auf VMA `0x00010000` ab; für diesen Bereich gilt daher VMA = Dateioffset + `0x10000`. Der untersuchte Bereich `[0x003403A4,0x0034046C)` entspricht Dateioffsets `[0x003303A4,0x0033046C)` und enthält genau 50 A32-Instruktionen / 200 Bytes. `0x0034046C` ist exklusiv und wurde nicht disassembliert; der dort beginnende nächste Prolog ist ausgeschlossen. Keine Runtime-Adresse wurde bestimmt.

GNU objdump zeigt für den Einstieg lediglich eine vorhandene Symbolannotation `SettgExitServer@@Base+0x1198`; dies ist kein Funktionsprototyp oder Verhaltensbeleg. Es wurde kein Dynsym-Symbol als API-Vertrag verwendet.

## Ergebnis

**VERIFIZIERT:** Am Eintritt vergleicht der Body `r2` mit Null und, nur wenn `r2 != 0`, `r0` mit Null. Bei `r2 == 0` oder `r0 == 0` setzt er `r7=2` und kehrt mit `r0=2` zurück. Dieser Pfad schreibt keinen expliziten Wert durch Eingabepointer; der Prolog sichert Register auf dem Stack.

Auf dem übrigen Pfad kopiert der Body `r0` nach `r4`, `r1` nach `r6` und `r2` nach `r5`. Er liest signierte Bytes ab `[r4]`, vergleicht sie mit `9` sowie einen um Bit 1 bereinigten Wert mit `32` und erhöht `r4` in einer Schleife, solange die bedingten Gleichheitsprüfungen zutreffen. Daraus folgt nur die beobachtete Scanlogik; keine Text-/Whitespace-API wird behauptet.

Nach zwei Calls zum Ziel `0x0033F2CC` vergleicht er deren Rückgaben. Die Rückgabe des zweiten Calls wird als 32-Bit-Wert an `[input r2]` geschrieben. Bei Ungleichheit wird `r7=15` gesetzt; bei Gleichheit `r7=0`. Wenn `input r1 != 0`, ruft er danach den direkten PLT-Zielstub `0x0007B804` mit `r0=input r1`, `r1=Scanposition`, `r2=Rückgabe des zweiten Calls` auf und schreibt anschließend ein Nullbyte an `[input r1 + *input r2]`. Wenn `input r1 == 0`, setzt er `r7=0`, erhöht die Rückgabe des zweiten Calls um eins und schreibt diesen Wert als 32-Bit-Wert an `[input r2]`. Die sichtbaren lokalen Rückgaben sind damit `2`, `15` oder `0`; daraus wird kein weitergehender API-Statusvertrag abgeleitet.

Callnamen und PLT-Labels belegen keine zusätzlichen Speicherwirkungen. Wirkungen der drei ausgeschlossenen Callkörper, einschließlich möglicher Speicherzugriffe über ihre Argumente, Aliasbeziehungen und deren Seiteneffekte bleiben **OFFEN**.

## Eingangsregister und Caller-Substitution

Im lokalen Body beziehen sich `input r0`, `input r1`, `input r2` auf die Werte bei Eintritt in `0x003403A4`. Auf dem nicht-frühen Pfad werden sie in `r4`, `r6`, `r5` gesichert. `r4` wird anschließend als Scanzeiger verändert; `r5` bleibt der Pointerwert aus Eintritts-`r2`; `r6` bleibt der Pointerwert aus Eintritts-`r1`.

Die angegebene E-XE164-177-Erfolgspfad-Substitution lautet exakt:

| Eintritt in diesen Body | Caller-Kontext |
|---|---|
| `r1` | `input r2` des Callers |
| `r2` | `input r3` des Callers |
| `r0` | durch die vorgegebene Substitution nicht bestimmt |

Folglich ist im Body `r6 = caller input r2` und `r5 = caller input r3`. Eine Aussage über den Ausdruck, der Caller-`r0` liefert, oder über andere Caller-Instruktionen wird nicht gemacht.

## Alle direkten Writes im Bereich

| VMA | Breite / Ziel | geschriebener Wert | Pfad und Beleg |
|---:|---|---|---|
| `0x003403B0` | 36 Bytes Stack: `[S-36..S-1]`, `S=SP` beim Body-Eintritt | `push {r4,r5,r6,r7,r11,r12,lr,pc}` speichert die neun Registerwerte | Prolog, immer; kein Store an `[S]` |
| `0x00340418` | 4 Bytes an `[r5]` = `[input r2]` | Rückgabe des zweiten Calls `0x0033F2CC` (vorher `r0` dieses Calls) | Nach beiden Calls und Vergleich, immer auf dem nicht-frühen Pfad; auch wenn die Werte gleich sind |
| `0x00340440` | 1 Byte an `[r6+r3]` | `0`, via `strb r2,[r6,r3]` | Nur wenn der Pfad `0x34042C` erreicht wird (`input r1 != 0`); `r3` wurde zuvor aus `[r5]` geladen |
| `0x00340464` | 4 Bytes an `[r5]` = `[input r2]` | Rückgabe des zweiten Calls plus `1` | Nur bei `input r1 == 0`; kommt nach dem Store bei `0x340418` und überschreibt dort den vorherigen Wert |

Dies ist die vollständige Menge expliziter Store-Instruktionen innerhalb des Bereichs einschließlich des Register-Stack-Push. `bl`-Ziele sind keine lokal disassemblierten Stores. Speicher-Aliase zwischen `[r5]`, `[r6+r3]` oder dem Stack sind aus diesem Bereich nicht auflösbar. Der Epilog lädt Register und `pc` aus dem Stack; er erzeugt keinen lokalen Store.

### Größen-/Rückgabepfade

| Bedingung / Block | sichtbare lokale Folge |
|---|---|
| Eintritts-`r2 == 0` oder bei `r2 != 0`: Eintritts-`r0 == 0` | `r7=2`; direkter Return `r0=2`; keine Pointerschreibinstruktion |
| Nicht-früher Pfad | zweiter Call liefert `v` in `r0`; Body schreibt `v` nach `[input r2]` und kopiert `v` in `r2` |
| `v` ungleich erster Call-Rückgabe und `input r1 != 0` | `r7=15`; Call bei `0x340434` erhält `r2=v`; danach Nullbyte an `[input r1 + *input r2]`; Return `r0=15` |
| `v` gleich erster Call-Rückgabe und `input r1 != 0` | `r7=0`; gleicher Call und expliziter Nullbyte-Store; Return `r0=0` |
| `input r1 == 0` (unabhängig vom Vergleichsergebnis) | `r7=0`; `v` wird lokal in `r2` um eins erhöht; `[input r2] = v+1`; Return `r0=0` |

Das Verhalten der Callkörper ist bei diesen Folgerungen nicht vorausgesetzt. Insbesondere ist nicht behauptet, dass der PLT-Call selbst terminiert oder eine bestimmte Anzahl Bytes schreibt; nur `strb` bei `0x340440` ist als Body-Store belegt.

## Kontrollfluss (Callziele atomar)

| Block | Kante / Wirkung |
|---|---|
| `0x3403A4..0x3403C8` | Nullbedingung aus Eintritts-`r2` oder Eintritts-`r0` → `0x340444`; sonst `0x3403CC` |
| `0x3403CC..0x3403F0` | Byte-Lese-/Vergleichsschleife; bei Prüfungs-Mismatch → `0x3403F4`; Schleifenbedingung wahr → `0x3403E0` |
| `0x3403F4..0x3403FC` | Vorbereitet sichtbare Argumentregister und Call `0x33F2CC`; dann `0x340400` |
| `0x340400..0x34040C` | Lese `[r5]`, setze Scanpointer/gesicherten Rückgabewert, Call `0x33F2CC`; dann `0x340410` |
| `0x340410..0x340418` | Vergleiche Rückgaben, kopiere zweiten Rückgabewert in `r2`, schreibe ihn nach `[r5]`; gleich → `0x34044C`, ungleich → `0x340420` |
| `0x340420..0x340428` | Ungleicher Pfad setzt bei nicht-null `r6` `r7=15`; `r6==0` → `0x340458`, sonst `0x34042C` |
| `0x34042C..0x340440` | Call `0x7B804`; danach Nullbyte-Store an `r6 + [r5]`; weiter `0x340444` |
| `0x340444..0x340448` | `r0=r7`, gemeinsamer Return |
| `0x34044C..0x340454` | Gleicher-Werte-Pfad: `r6!=0` setzt `r7=0` und geht zu `0x34042C`; sonst fall-through `0x340458` |
| `0x340458..0x340468` | Setzt `r7=0`, erhöht `r2` um eins, `r0=r7`, schreibt `r2` nach `[r5]`; Return |

## Direkte Calls und sichtbare Registerwerte

`S` ist Body-Eintritts-SP. Nach dem Push ist `SP=S-36`. Fragezeichen kennzeichnet Werte, die nach einem direkten Call aus dem lokalen Body nicht sicher hergeleitet werden, da `r0-r3` caller-saved sind. Die Callkörper sind ausgeschlossen.

| Callsite → direktes Ziel | `r0` | `r1` | `r2` | `r3` | sichtbare Rückgabeverwendung |
|---|---|---|---|---|---|
| `0x3403FC → 0x33F2CC` | `r4`, Eintritts-`r0` nach dem Byte-Scan | `0xFFFFFFFF` (`mvn r1,#0`) | signiertes erstes Byte, bitweise `& 0xFFFFFFFD` | signiertes aktuelles Scanbyte | `r0` wird nach Rückkehr in `r7` kopiert |
| `0x34040C → 0x33F2CC` | `r4`, Scanposition | `[r5]` geladen bei `0x340400` | unbekannt nach erstem Call | unbekannt nach erstem Call | `r0` wird verglichen, dann in `r2` kopiert und nach `[r5]` geschrieben |
| `0x340434 → 0x7B804` (PLT) | `r6` = Eintritts-`r1` | `r4` = Scanposition | zweiter Call-Rückgabewert | unbekannt nach vorherigem Call | nach Rückkehr kein lokaler Gebrauch von `r0`; folgende Instruktionen lesen `[r5]` und schreiben das Nullbyte selbst |

Bei Call 1 stammen `r2/r3` aus den lokalen `ldrsb`-/`bic`-/Vergleichs- und Schleifeninstruktionen. Bei Call 2 werden `r2/r3` als unbekannt markiert, weil Call 1 sie überschreiben darf. Für Call 3 ist `r2` frisch mit dem gerade zurückgegebenen `r0` gesetzt; `r3` ist nach Call 2 clobberbar und wird als unbekannt behandelt. Die später weiterverwendeten Werte in `r4-r7` setzen die übliche ARM-Aufrufkonvention voraus; ohne die ausgeschlossenen Callkörper ist deren Registererhalt nicht unabhängig geprüft.

## REA, Fallback und Restunsicherheit

REA wurde zuerst anhand des exakten Zielhashes und der Adresse abgefragt. Der retained-Evidence-Filter lieferte `total_retained_records=0`, `matching_records=0`; es gibt daher kein passendes gespeichertes REA-Dossier für diesen Body. Die Session war zuvor geschlossen. Es wurde kein Ghidra-Import gestartet und kein hängender Import wiederholt.

Begrenzter Offline-Fallback: `/usr/bin/arm-linux-gnueabihf-objdump` mit `-d -w -M reg-names-std`, ausschließlich VMA-Range `[0x3403A4,0x34046C)`, Binutils 2.44. ELF-Header-/Program-Header-Metadaten wurden mit GNU `readelf` 2.44 gelesen. Der Header ordnet das Artefakt ARM ELF32 little-endian zu; Instruktionen und Dateibytes wurden für alle 50 Wörter gegengeprüft. `rizin` ist auf dem Host vorhanden, wurde aber nicht zusätzlich eingesetzt, da die begrenzte byteverankerte Dekodierung keinen ungelösten Instruktions-/Offsetwiderspruch hinterließ. Kein angrenzender Body, kein Callkörper, kein Caller-Body wurden expandiert.

Alternative / Rest: Die lokalen Instruktionen belegen Pointer-Lese-/Schreibzugriffe und konkrete Werte, nicht die Typen oder Rollen der Zeiger. Insbesondere kann der Body die von `[r5]` gelesenen/geschriebenen Werte lokal vergleichen und als Index verwenden; ein vollständiger Größen- oder Statusvertrag bleibt **OFFEN**. Callee-Speicherwirkungen, Aliasauflösung, Runtime-Verhalten und die Semantik der Symbolnamen bleiben **OFFEN**. Die Caller-Substitution wird nur so weit angewandt, wie sie vorgegeben wurde.

## Status und Validierung

| Aussage / Prüfung | Status | Begründung |
|---|---|---|
| Artefaktidentität | VERIFIZIERT | Größe und SHA-256 passen zum Sollwert. |
| ELF-VMA-/Dateioffsetabbildung | VERIFIZIERT | Erster `PT_LOAD`: Offset `0` → VMA `0x10000`; 200 Bytes im Bereich zugeordnet. |
| Instruktionsbytes und Grenze | VERIFIZIERT | 50 Wörter lückenlos aus `[0x3403A4,0x34046C)`; `0x34046C` exklusiv. |
| Stores, Calls, sichtbare Argumente, lokale Rückgaben | VERIFIZIERT | Aus den Instruktionen des Bereichs abgeleitet; Callee-Körper ausgeschlossen. |
| Semantik, Aliasauflösung, Callee- und Runtime-Wirkungen | OFFEN | Durch den begrenzten statischen Umfang nicht feststellbar. |
| passendes retained-REA-Dossier gefunden | VERIFIZIERT | Nein; exakter Zielhash-/Adressfilter hatte null Records. |
| `python3 validate.py` | PASS | Prüft Hash/Größe, Range, bytegenaue Tabelle, Callsites, Writes und Statuspfade. |
| `sha256sum -c SHA256SUMS` | PASS | Alle aufgeführten Workerdateien stimmen mit dem Manifest überein. |

Workerbericht mit Self-Review; kein unabhängiges Review und kein separater Worker-Lauf wird behauptet.

## Paketinhalt

- `report.md` — Befunde, Grenzen und Einordnung
- `instructions.tsv` — vollständige Instruktions-/Byte-Tabelle
- `calls.tsv` — direkte Calls und sichtbare Registerzustände
- `disassembly.raw.txt` — begrenzte GNU-objdump-Ausgabe
- `generate.py` — Tabellen-/Bytes-Prüfungsgenerator
- `validate.py` — unabhängiger Paketvalidator innerhalb dieses Workers
- `tool_versions.txt`, `validator_result.txt`, `SHA256SUMS`
