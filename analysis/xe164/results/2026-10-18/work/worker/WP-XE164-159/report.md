> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-159 — begrenzter Prolog bei VMA `0x0033f548`

## Ergebnis

**VERIFIZIERT:** Die Eingabe ist das ELF mit 5.181.396 Bytes und SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`. Das Ergebnislisting deckt den inklusiven VMA-Bereich `0x0033f548..0x0033f597` (80 Bytes) ab. Der bereitgestellte Nachbarbericht WP-XE164-153 hat SHA-256 `fab40a1259ae5fe2c9a0d3e692f61f6c60486353619fab5a71bf6bc420b39489` und markiert die Grenze bei `0x0033f598`; bei seiner anfänglichen Sichtung wurden versehentlich auch Nachbarbytes ab dieser Grenze ausgegeben (siehe Prozessabweichung). Für das erste LOAD-Segment gilt `p_offset=0`, `p_vaddr=0x10000`; damit ist der Dateioffset hier VMA minus `0x10000`. Laufzeitadressen wurden nicht bestimmt.

**VERIFIZIERT:** Beim Eintritt werden `r0`, `r1`, `r2`, `r3` und `S=entry_sp` als beobachtete Eingangsgrößen behandelt. In diesem Fenster bleibt der eingehende Wert in `r0` bis zum `strchr`-Aufruf erhalten. `r1` wird nach `r3` kopiert und anschließend mit 46 (`0x2e`) überschrieben; vor dem Überschreiben wird der kopierte Wert bei `[fp-1368]` gespeichert. `r2` wird nach `r7` kopiert. Das eingehende `r3` wird vor diesem Store überschrieben und ist im Fenster nicht mehr verfügbar. Der Inhalt von `[S]` wird nicht gelesen oder beschrieben.

**VERIFIZIERT:** Der Prolog setzt `ip=S`, sichert 11 Registerwörter (44 Bytes) mit `push`, setzt `fp=S-4`, reserviert 1328 Bytes und anschließend weitere 12 Bytes. Der lokale `sp` ist danach `S-1384` beziehungsweise `fp-1380`. Die beiden sichtbaren lokalen Stores adressieren `[fp-1368]=[S-1372]` und `[fp-1360]=[S-1364]`. Die Stores belegen nur diese Werte und Adressen; Feld- oder Variablenrollen werden nicht behauptet.

**VERIFIZIERT:** Der erste sichtbare Call ist `bl 0x7b3e4 <strchr@plt>` bei `0x33f56c`. Direkt davor stehen `r0=incoming r0`, `r1=46`, `r2=incoming r2`, `r3=incoming r1`, `r7=incoming r2`, `fp=S-4`, `sp=S-1384`, `[fp-1368]=incoming r1`. Das ist Register-/Stackzustand, keine Rollen- oder API-Vertragsbehauptung.

**VERIFIZIERT:** Nach dem `strchr`-Call wird `r4=1` gesetzt und nach `[fp-1360]` gespeichert. Bei `r0==0` wird `r0=1` gesetzt und der bedingte Branch bei `0x33f580` geht nach `0x33f7dc`, außerhalb des erlaubten Fensters. Damit ist im Fenster eine frühe ausgehende Kante unter dieser Bedingung belegt; ob das Ziel tatsächlich ein gemeinsamer Returnblock ist, bleibt hier ungeprüft.

**VERIFIZIERT:** Auf dem sichtbaren Nichtnull-Pfad wird `r2=10`, `r1=0`, `r0=r0+1` und `r8=0` gesetzt; unmittelbar danach liegt der `strtol@plt`-Call bei `0x33f594` nach `0x7c5e4`. Unmittelbar davor ist somit `r0=(Rückgabewert von strchr)+1`, `r1=0`, `r2=10`, `r3` nach dem vorangegangenen Call unbekannt, `r7=incoming r2`, `r8=0`, `[fp-1360]=1`. Die Byteaddition ist genau `+1`; darüber hinaus wird keine Parser- oder Argumentsemantik behauptet. Die Call-Rückkehr und alle späteren Instruktionen liegen außerhalb des erlaubten Fensters und wurden nicht untersucht.

**OFFEN:** Ob `strchr` den Punkt als Trennzeichen sucht und `strtol` den folgenden Teil als Zahl konvertiert, ist als übliche Symbolinterpretation plausibel, aber durch diese Anweisung nur als sichtbarer Registerzustand und die PLT-Namen begrenzt. Es werden keine Signatur, Stringstruktur, Zahlenbedeutung oder Erfolgssemantik behauptet. Ebenso offen sind der Inhalt von `incoming r0`, `incoming r2`, `incoming r3`, `[S]`, Rückgabewert/-fehler von `strtol` und die Bedeutung des Zweigziels `0x33f7dc`.

## Vollständige Instruktionstabelle

`instruction_table.tsv` führt lückenlos alle 20 4-Byte-Instruktionen innerhalb des Fensters mit VMA, ELF-Dateioffset und Bytes in Dateireihenfolge auf. Kein Byte ab `0x33f598` ist in die Tabelle aufgenommen.

## Kontrollflusskanten aus dem Fenster

| Adresse | sichtbare Bedingung/Aktion | Ziel | Status |
|---|---|---|---|
| `0x33f56c` | direkter Call `strchr@plt` | `0x7b3e4` | Zielkante sichtbar; Callee ausgeschlossen |
| `0x33f580` | `beq`, nach `r0=1` bei vorherigem Vergleich `r0==0` | `0x33f7dc` | außerhalb des Fensters; Ziel nicht expandiert |
| `0x33f594` | direkter Call `strtol@plt` | `0x7c5e4` | Zielkante sichtbar; Callee und Rückkehr ausgeschlossen |

Im Fenster gibt es keine Instruktion, die direkt `lr` lädt oder einen Rücksprung ausführt. Der Nullpfad wird daher nur als bedingte ausgehende Kante berichtet, nicht als verifizierter Return.

## REA, Methode und Evidenzgrenzen

Vor dem Disassemblieren wurden vorhandene retained REA-JSON-Records mit passendem SHA-256 und Adressbezug geprüft. Kein vorhandener Record liefert Instruktions-/Prolog-Evidence für `0x33f548..0x33f597`; es gibt dafür folglich keine passende REA-Evidence-ID. `rea_evidence_ids.tsv` hält die Lücke und zwei ausdrücklich ausgeschlossene IDs fest: WP153 nennt `ev_1d4...` für Adresse `0x330664`; der retained WP124-Record `ev_749...` analysiert `0x336a84`. Die vorhandenen WP-XE164-153-Records binden andere Adressen; der Report-Hash wurde als Nachbargrenze herangezogen. Die vorhandenen WP-XE164-118-Records betreffen laut WP153 einen fremden Codebereich. Ein neuer Ghidra-Import wurde wegen des dokumentierten früheren Hängers nicht wiederholt.

**Prozessabweichung:** Bei der anfänglichen Sichtung von WP153 wurde versehentlich dessen `instruction_table.tsv` ab `0x33f598` ausgegeben. Diese Nachbarbytes wurden nicht für Befunde, Instruktionen oder Zustandsableitungen dieses Pakets herangezogen. Das WP159-Eingabelisting selbst verwendete die exklusive Stop-Adresse `0x33f598`; Validator und Tabelle begrenzen das Paket auf `0x33f548..0x33f597`. Der versehentliche Zugriff wird dennoch als Abweichung von der strikten Lesebereichsvorgabe offengelegt.

Fallback: GNU ARM `objdump` 2.44 mit exklusiver Stop-Adresse `0x33f598`; außerdem `readelf` zur LOAD-Abbildung. Werkzeuge: GNU binutils/readelf/objdump 2.44, Rizin 0.9.1 (nicht für eine Analyse aufgerufen), Python 3.13.5 (nur Paketvalidator); REA 6.5.0 ist in den erhaltenen WP-XE164-Artefakten dokumentiert. Keine VM-, Netzwerk-, Geräte-, Runtime- oder Hardwarezugriffe. Keine Caller-/Callee-Körper, keine Bytes ab `0x33f598`.

Alternative Deutung: Die sichtbare Folge passt zu einer Punkt-Suche und einer anschließenden Zahl-Parsing-Vorbereitung. Das bleibt eine Interpretation von Symbolnamen und Maschinenzuständen. Der belastbare Befund beschränkt sich auf Immediate-Werte, Register-/Stackzustände, den bedingten Branch und direkte Call-Kanten.

## Status und Prüfungen

| Aussage/Prüfung | Status | Ergebnis |
|---|---|---|
| Eingabehash und -größe | VERIFIZIERT | — |
| Bytefenster und Instruktionsgrenzen | VERIFIZIERT | — |
| Frame-/Registerzustände aus den Instruktionen | VERIFIZIERT | — |
| Callzustände und frühe bedingte Kante | VERIFIZIERT | — |
| API-/Parsersemantik, Zielblocksemantik, Runtime | OFFEN | — |
| retained exact-range record result | VERIFIZIERT | keiner gefunden |
| unabhängiger Ghidra-Neuimport | BLOCKED | — |
| `python3 validate.py` | PASS | siehe `validator_result.txt` |
| `sha256sum -c SHA256SUMS` | PASS | — |
| Work-package scope compliance | FAIL | ausgeschlossene Nachbarbytes wurden versehentlich gelesen |

Workerbericht mit Self-Review; keine unabhängige Gegenprüfung, Runtime- oder Hardwareprüfung.
