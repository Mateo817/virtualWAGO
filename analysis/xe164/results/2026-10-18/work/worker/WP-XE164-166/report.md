> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-166 — lokale Argument-, Speicher- und Rückgabekette bis `MainLoadComponent`

## Befund

**VERIFIZIERT:** Das exakt gebundene ELF enthält im erlaubten VMA-Bereich `[0x002FEB78,0x002FEC58)` genau 56 lückenlose 4-Byte-Instruktionen (224 Bytes). Die vollständige Tabelle mit VMA, Datei-Offset, little-endian Bytes und Disassemblierung steht in [`instructions.tsv`](instructions.tsv); `disassembly.raw.txt` bewahrt die begrenzte objdump-Ausgabe. Der ELF `PT_LOAD` bei Datei-Offset `0`, VMA `0x10000` ergibt für diesen Bereich `file_offset = VMA - 0x10000`, also `[0x002EEB78,0x002EEC58)`.

Der Eingang in `0x002FEB78` ist der Fall-through des vorherigen `bne` bei `0x002FEB74`. Laut exakt gebundenem WP163-Bericht wurde unmittelbar davor `r1 := r0` ausgeführt, mit Flags für denselben Vergleich zu null; der `bne` springt bei nicht-null zurück zu `0x002FEB60`. Daher gilt am Eintritt in diesen Bereich **nur auf dem Fall-through-Pfad** `r1 = 0`. WP163 bindet den lokalen Wert-/Adressausdruck `r11-0xB4` an den zuvor an `0x002FCB48` übergebenen Caller-local Pointer. Im aktuellen Bereich ist der ARM-Framepointer als `fp` aliasiert (`r11`), und `fp-0xB4` ist dieselbe lokale Adresse, hier auch `fp-180` notiert. Es wird keine Bedeutung für den Callee-Rückgabewert außer dem lokalen Nulltest behauptet.

Bei `0x002FEB94` liegt ein direkter `bl` auf `0x0007D36C`. Die ELF-Dynsym-Tabelle führt an dieser Zieladresse `MainLoadComponent` als `GLOBAL DEFAULT FUNC` (Index 4544). **VERIFIZIERT ist damit die Symbolidentität und das direkte Ziel; der Vertrag dieses Symbols bleibt OFFEN.** Der lokal sichtbare Call-Zustand ist `r0=fp-180`, `r1=0`, `r2=fp-196`, `r3=fp-192`. Vor dem Call schreibt der Code `0` nach `[fp-192]` und `[fp-200]`, sowie `0xffffffff` nach `[fp-196]`; `r2` bzw. `r3` zeigen auf die ersten beiden lokalen Slots. Die Aufrufinstruktion verändert `lr`, nicht die als Argumente sichtbaren Werte. Über zusätzliche Stackargumente wird nichts behauptet; im begrenzten Bereich erfolgt vor diesem Call kein Store relativ zu `sp`.

Nach dem Call wird der dann aktuelle Rohwert von `[fp-200]` nach `r1` geladen, dann wird der unveränderte Call-Rückgabewert `r0` auf null getestet und nach `[fp-184]` gespeichert. Das Nullflag verzweigt bei Nichtnull zu `0x002FEC18`; der Nullpfad fällt zu `0x002FEBA8` durch. Die lokale Speicherablage des Rückgabewerts erfolgt nach dem `cmp`, ändert dessen Flags also nicht. `[fp-200]` war vor dem opaken Call auf null initialisiert; seine Retention über `MainLoadComponent` ist **OFFEN**, da dessen Calleepfad und mögliche Speicherwirkungen in diesem WP ausgeschlossen sind.

## Caller-local-Substitution separat

WP163 belegt: Vor dem untersuchten Range lädt `0x002FEB68` `r0 := r11-0xB4`, und `0x002FEB6C` ruft direkt `0x002FCB48` auf. Damit ist der Call-Eingabewert `r0` dieselbe lokale Adresse, die im aktuellen Range als `fp-180` erneut in `r0` gesetzt und an `MainLoadComponent` übergeben wird (`fp`/`r11` Framepointer-Alias). Der Rückgabewert von `0x002FCB48` ist eine getrennte Größe: nach dem Call kopiert `subs r1,r0,#0` diesen Rückgabewert nach `r1`; auf dem Fall-through bei Rückgabewert null erreicht `r1=0` den `MainLoadComponent`-Call. Es gibt keine Instruktion, die den Rückgabewert von `0x002FCB48` als `MainLoadComponent`-Pointer übernimmt.

## Kontrollflussgraph

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Zusätzlicher eingehender Rand aus dem vorherigen Bereich: WP163 belegt den `r4 > 1`-Branch von `0x002FEB58` nach `0x002FEC10`; dort wird `sp` angepasst und `0x002FEC14` lädt die gespeicherten Register einschließlich `pc` vom Stack. Das ist der lokale Epilog-/Rückkehrpfad. Innerhalb der hier erlaubten Range gibt es keinen Branch zu `0x002FEC10`; der Zielrand kommt ausschließlich aus dem vorherigen Bereich.

Im zweiten Vergleichszweig ist der lokal gelesene Bytewert `0x73` (ASCII `s` als Bytegleichheit, ohne daraus Semantik abzuleiten). Beide Wege führen zum Call bei `0x002FEC08`; sie unterscheiden, ob der Code den kleinen lokalen Wert vor diesem Call bei `0x002FEBEC` oder `0x002FEBFC` schreibt. Keine der Instruktionen wertet einen `CMAddComponent`-Rückgabewert aus. Der nicht-null `MainLoadComponent`-Pfad ruft `LogAdd` auf, wertet dessen Rückgabe ebenfalls nicht aus und verzweigt zurück außerhalb des erlaubten Bereichs.

## Direkte Calls: clobber-aware Argument- und Return-use

| Callsite / direktes Ziel | sichtbare Argumentregister am Call | sichtbare Stackargumente | Return-/Fehlerfluss innerhalb des Bereichs |
|---|---|---|---|
| `0x002FEB94 → 0x0007D36C` (`MainLoadComponent`, Dynsym) | `r0=fp-180`; `r1=0` aus dem vorherigen, im WP163-Report gebundenen Fall-through; `r2=fp-196` (Slot enthält zuvor `0xffffffff`); `r3=fp-192` (Slot enthält zuvor `0`) | keine im Bereich vor diesem Call geschriebenen `sp`-Slots; weitere Argumente unbekannt | `r0` direkt mit `0` verglichen; `r1` wird vorher aus `[fp-200]` geladen; `r0` wird nach dem Vergleich auf `[fp-184]` gespeichert. `r0==0` führt zu Initialisierung und dem Call `CMAddComponent`; `r0!=0` führt zum `LogAdd`-Pfad. Keine Aussage über Callee-Wirkung auf Pointerzielen. |
| `0x002FEC08 → 0x002FD0F0` (`CMAddComponent`, ELF-Dynsym) | `r0=fp-96`; `r1=fp-184` (Adresse, kein Wert-load); `r2` bleibt der in `0x002FEBB4` aus `[fp-180]` geladene 16-Bit-Rohwert; `r3=fp-180` | kein neuer `sp`-relativer Store im Bereich direkt vor dem Call; zusätzliche Argumentwerte daher unbekannt | Rückgabe wird innerhalb des Bereichs nicht geprüft oder weiterverwendet; direkter Branch nach `0x002FEB60` (außerhalb). |
| `0x002FEC3C → 0x00178C2C` (`LogAdd`, ELF-Dynsym) | `r0=[fp-200]` als der bei `0x002FEB98` nach dem `MainLoadComponent`-Call geladene aktuelle Rohwert (Retentionswert unbekannt); `r1=1`; `r2=4`; `r3` ist der nicht-null `MainLoadComponent`-Rückgabewert aus `r0` | `[sp]=12` (`0x0c`), `[sp+4]=sl`, `[sp+8]=fp-180`, jeweils im Bereich direkt vor dem Call geschrieben | Rückgabe wird nicht gelesen oder getestet; direkter Branch nach `0x002FEB60` (außerhalb). |

Caller-saved Registerwerte werden über Calls nicht fortgeschrieben. Für `CMAddComponent` stützt sich `r2` darauf, dass nach dem lokalen `ldrh` bis zum Call keine Instruktion `r2` überschreibt; für `LogAdd` ist `r3` lokal vom aktuellen MainLoad-Rückgabewert gesetzt. Der rohe Stackwert `[sp+4]` ist `sl` (`r10`), aber dessen konkreter Wert wird hier nicht etabliert und sein Fortbestand über den vorangehenden Call wird nicht ohne ABI-Annahme behauptet. Aussagen über Callee-Clobber-Verhalten oder ABI-Konformität werden nicht benötigt und nicht vorausgesetzt.

## Direkte Speicherzugriffe im gesamten Bereich

Alle Offsets relativ zu `fp` sind vorzeichenbehaftete Byte-Offsets. VFP `vstr d16` speichert 8 Bytes; `vst1.8 {d16-d17}` speichert 16 Bytes. Der Code setzt `q8` mit `vmov.i32 q8,#0`; die darauffolgenden Stores aus `d16`/`d17` schreiben daher lokal sichtbare Nullbytes.

| VMA | Zugriff |
|---|---|
| `0x2FEB88` | `str r1,[fp-192]` |
| `0x2FEB8C` | `str r1,[fp-200]` |
| `0x2FEB90` | `str ip,[fp-196]` (`ip` wurde unmittelbar davor auf `0xffffffff` gesetzt) |
| `0x2FEB98` | `ldr r1,[fp-200]` |
| `0x2FEBA0` | `str r0,[fp-184]` nach Returnvergleich |
| `0x2FEBAC` | `ldr r1,[fp-192]` |
| `0x2FEBB0` | `ldr r3,[fp-196]` |
| `0x2FEBB4` | `ldrh r2,[fp-180]` |
| `0x2FEBB8` | `vstr d16,[fp-80]`, 8 Nullbytes |
| `0x2FEBBC` | `str r1,[fp-80]`, 4 bytes; überlagert die ersten 4 Bytes des vorigen Nullstores |
| `0x2FEBC4` | `vstr d16,[fp-56]`, 8 Nullbytes |
| `0x2FEBC8` | `vstr d16,[fp-72]`, 8 Nullbytes |
| `0x2FEBCC` | `vstr d16,[fp-52]`, 8 Nullbytes |
| `0x2FEBD0` | `vstr d16,[fp-64]`, 8 Nullbytes |
| `0x2FEBD4` | `vst1.8 {d16-d17},[r1]`, 16 Nullbytes bei `r1=fp-96` |
| `0x2FEBD8` | `str r3,[fp-88]` |
| `0x2FEBE8` | `strh r3,[fp-52]` |
| `0x2FEBFC` | `strh r3,[fp-50]` |
| `0x2FEC04` | `str r3,[fp-92]` |
| `0x2FEC14` | `ldm sp,{r4,r5,r6,r7,r8,r9,sl,fp,sp,pc}` reads the listed register words from the stack beginning at current `sp` |
| `0x2FEC20` | `str r2,[sp+8]` |
| `0x2FEC30` | `str r2,[sp]` |
| `0x2FEC38` | `str sl,[sp+4]` |
| `0x2FEC44` | `ldrb r3,[fp-178]` |

## Artefakt, Tools, Validierung

| Eingabe | Größe | SHA-256 | Status |
|---|---:|---|---|
| `.../WP-XE164-112/hit_files/usr/bin/codesys3` | 5.181.396 Bytes | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | VERIFIZIERT |
| WP163 `report.md` | 11.474 Bytes | `cbd18b62a4a3992d47837e8aa9d549cf096375b82ffeb80edc9d76ce281ca4d8` | VERIFIZIERT |

REA retained-Evidence wurde zuerst nach exakt diesem Target-Hash abgefragt: `total_retained_records=0`, `matching_records=0`, `unknown_revisions=0`. Diese Evidence-Lücke ist dokumentiert. Danach erfolgte der begrenzte Fallback: GNU `arm-linux-gnueabihf-objdump` 2.44 nur für die angegebene VMA-Range; GNU `arm-linux-gnueabihf-readelf` 2.44 für LOAD-Mapping und Dynsym-Identität. Werkzeugstände und Aufrufgrenzen stehen in [`tool_versions.txt`](tool_versions.txt). Kein Ghidra-Import und kein Zielprogramm-Lauf.

`generate.py` baut die Tabelle aus genau diesem begrenzten Disassembly und prüft Größe, Hash, VMA-Kontinuität sowie jedes Instruktionswort gegen Datei-Bytes. `validate.py` wiederholt diese Bindungs-/Dekodierprüfung, verifiziert den WP163-Eingabehash und prüft den Dynsym-Eintrag. Der ausgeführte Validator steht in [`validator_result.txt`](validator_result.txt); Paketdatei-Hashes stehen in [`SHA256SUMS`](SHA256SUMS).

## Status, Alternative, Restunsicherheit

| Aussage / Prüfung | Status | Grund |
|---|---|---|
| ELF-Hash, Größe, 224 Bytes und 56 Instruktionen | VERIFIZIERT | direkter Hash-/Byte-/Adresscheck |
| `fp-180` als an MainLoadComponent übergebener Caller-local Pointer | VERIFIZIERT | WP163 bindet den unmittelbar vorherigen `r0=fp-180` Call-Input; aktueller `r0=fp-180` wird lokal vor `bl` erneut gesetzt |
| `MainLoadComponent`-Symbolidentität | VERIFIZIERT | direkter Call auf Adresse des globalen Dynsym-Eintrags |
| Symbolvertrag, Bedeutungen der lokalen Slots, Aliasbeziehungen | OFFEN | nicht aus Instruktionen oder Symbolnamen bestimmbar |
| Alternativerklärung | HYPOTHESE | `fp-180` kann schlicht ein opaker lokaler Zwei-Byte-Wert-/Ausgabebereich sein; der Code reicht dessen Adresse weiter und liest später zwei Bytes daraus, ohne dass daraus ein Feldtyp oder Zweck folgt |
| Retention von `[fp-200]` über `MainLoadComponent`, weitere Stackargumente bei MainLoad/CMAddComponent, Laufzeitpfad | OFFEN | Callee-Body und mögliche Speicherwirkungen sind ausgeschlossen; `LogAdd r0` ist nur als nach dem Call geladener Slot-Rohwert belegt |
| Paketvalidator | PASS | `validator_result.txt` |
| Zielprogramm-Tests / Runtime-Beobachtung | NOT_RUN | nicht Teil der Offlineanalyse |

Self-Review: Die Registerargumente werden aus unmittelbar gesetzten Werten oder lokal unüberschriebenen Zuständen abgeleitet. Über den Bereichsanfang wird ausschließlich die im WP163-Report belegte Fall-through-Substitution übernommen. Es wird keine Wirkung aus `MainLoadComponent`, `CMAddComponent` oder `LogAdd` abgeleitet. Unabhängiges Review wird nicht behauptet.
