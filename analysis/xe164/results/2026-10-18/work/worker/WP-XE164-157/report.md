> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-157 — `SettgBeGetStringValue` bei ELF-VMA `0x00341F44`

## Eingabeidentitäten

| Artefakt | Größe | SHA-256 |
|---|---:|---|
| `codesys3` aus WP-XE164-112 | 5,181,396 Bytes | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` |
| WP-XE164-155 `report.md` | 9,387 Bytes | `fa66a058699e00236bcc9ced98bb0a1f3248cb5bc9b2759531fe74a076ce32a8` |
| WP-XE164-153 `report.md` | 8,764 Bytes | `fab40a1259ae5fe2c9a0d3e692f61f6c60486353619fab5a71bf6bc420b39489` |

## Ergebnis

**VERIFIZIERT:** Der definierte Dynsym-Eintrag ist `FUNC GLOBAL DEFAULT`, Abschnitt 14, VMA `0x00341f44`, Größe 524 dezimal (`0x20c`). Der bytegenaue Bereich ist `[0x00341f44,0x00342150)`, inklusive letztem Byte `0x0034214f`. Der erste `PT_LOAD` bildet Datei-Offset 0 auf VMA `0x10000` ab: Body-Dateioffsets `[0x00331f44,0x00332150)`. 130 A32-Instruktionen plus ein zum Dynsym-Extent gehörendes 4-Byte-Literalwort decken lückenlos alle 524 Bytes ab. Die letzte Instruktionssequenz lädt dieses Wort bei `0x34210c` als Literal.

**VERIFIZIERT:** Eingangsregister werden zu `r6=input r0`, `r5=input r1`, `r7=input r2`, `r4=input r3` gesichert. Bei Eintritts-SP `S` setzt der Prolog `r11=S-4`, sichert 36 Bytes und reserviert weitere 12; lokaler SP ist danach `S-48`. `[entry_sp]` (`[r11,#4]`) wird gelesen, aber vom Body nicht direkt beschrieben. Der geladene Wert wird an den direkten Call `0x00304760` als `r2` übergeben (Callsite `0x342050`); am selben Call ist `r0=input r2` (über `r7`). Damit sind beide sichtbaren Registerwerte belegt, nicht die Semantik oder Wirkung des Callees.

**VERIFIZIERT:** Am Callsite `0x342050` wird der gespeicherte Eingangswert `input r2` (`r7`) als `r0` weitergegeben; der dort frisch von `[entry_sp]` geladene Wert geht als `r2`. Lokal gibt es keinen Store mit `r2`/`r7` als Basis. Eine Speicherwirkung durch das ausgeschlossene Callziel ist aus diesem Body nicht bestimmbar. Separat schreibt der Body `r2` als Wert nach `[input r3]`, aber nur auf dem Pfad `input r2==0` und `input r3!=0`; dort ist der gespeicherte Wert Null.

**VERIFIZIERT:** Der Pointee von `input r3` erhält in lokalen Pfaden einen vom direkten Call bei `0x342020` abgeleiteten und lokal angepassten Wert (`str r1,[r4]` bei `0x342040`), den Rückgabewert des direkten Calls bei `0x342068` (`str r0,[r4]`) oder das gelesene Wort `[entry_sp]` (`str r3,[r4]` bei `0x3420e4`). Mögliche Aliasierung dieser Ziele mit `[entry_sp]` ist nicht bestimmbar. Der normale lokale Rückgabepfad lädt `r0=[fp-40]=[S-44]`; frühe Nullprüfungen geben konstant `2` zurück; der abschließende Fehlerpfad gibt konstant `3` zurück. Ein Pfad speichert `15` in `[S-44]` und läuft zum gemeinsamen abschließenden Call-/Returnblock.

## Beobachtungen, CFG und Eingangsdatenfluss

Die bedingten Kanten im Dynsym-Extent ergeben für den hier relevanten Kontrollfluss folgende Blockübersicht. `S` bezeichnet den Eintritts-SP. Kanten sind aus den jeweiligen Branch-Instruktionen abgeleitet; Callziele werden als atomare Übergänge behandelt, ihre Körper nicht interpretiert.

| Blockstart / Bereich | Bedingung bzw. Wirkung | Folgekante(n) |
|---|---|---|
| `0x341f44..0x341f74` | Vor Prolog: `cmp r1,0`, dann nur bei `r1!=0` `cmp r0,0`; BEQ | Nullbedingung → `0x34208c` (Return 2); sonst `0x341f78` |
| `0x341f78..0x341f7c` | `cmp input_r2,0`; BEQ | Null → `0x342098`; nicht-null → `0x341f80` |
| `0x341f80..0x341f90` | `cmp input_r3,0`; bei nicht-null zusätzlich `cmp [input_r3],0`; beide mit BEQ | Null → `0x34208c`; gültige Nichtnullwerte → `0x341f94` |
| `0x342098..0x3420a0` | Falls `input_r3!=0`, `str input_r2,[input_r3]`; dieser Block ist über `input_r2==0` erreicht | `0x341f94` |
| `0x341f94..0x34200c` | Globale Prüfungen, bedingter direkter Call bei `0x341fc8`, danach weitere direkte Calls; Callrückgabe wird in `[S-44]` gesichert | `0x34200c` oder Prüfzweig `0x3420a4`; Rückgabe-Null kann zu `0x3420ec` führen |
| `0x342010..0x342044` | Lädt `[S]`; Null → `0x3420e0`, sonst direkter Call bei `0x342020` mit `r0=[S]`; Callrückgabe wird lokal angepasst und über `r4=input_r3` gespeichert; prüft `r7=input_r2` | `0x342044` → `0x342078` wenn `r7==0`, sonst `0x342048` |
| `0x342048..0x342074` | Lädt erneut `[S]`, ruft direkt `0x00304760` mit `r0=input_r2`, `r2=[S]`; abhängig von Rückgabe ggf. weiterer direkter Call bei `0x342068` und Store über `r4` | `0x342060`/`0x342074` können zu `0x342140`; andernfalls `0x342078` |
| `0x342078..0x342088` | Direkter Call bei `0x34207c`; lädt `[S-44]` in `r0`; gemeinsamer Epilog | Return über `0x342088` |
| `0x34208c..0x342094` | Setzt `r0=2`; gemeinsamer Epilog | Return über `0x342094` |
| `0x3420a4..0x3420dc` | Vergleichs-Call; direkter Call mit `r0=input_r1`, `r1=input_r2`, `r2=input_r3`; sichert Rückgabe | Rückgabe ungleich 1 → `0x342090`; gleich 1 → `0x341fdc` |
| `0x3420e0..0x3420e8` | Schreibt den Nullwert `[S]` nach `[input_r3]` | `0x342078` |
| `0x3420ec..0x342108` | Bei nicht-null `input_r3` direkter Call mit `r1=input_r2`, `r2=input_r3`; sichert Rückgabe | `0x342078` |
| `0x34210c..0x342134` | Pool-Initialisierungscall; Rückgabe wird global gesichert und geprüft | Erfolg plus lokaler Nullstatus → `0x341fa8`; sonst `0x342138` |
| `0x342138..0x34213c` | Setzt `r0=3` | `0x342090` |
| `0x342140..0x342148` | Setzt `[S-44]=15` | `0x342078` |

Die frühen Prüfungen beobachten `r1`, `r0`, `r2`, `r3` und das Wort `[input_r3]`; sie belegen keine Argumentrollen. Nach dem Prolog bleibt `r7` eine unveränderte Kopie des Eingangs `r2`, während `r4` die Kopie des Eingangs `r3` hält. Der Call bei `0x342050` transportiert `r7` in `r0` und das frisch von `[S]` geladene Wort in `r2`; ein lokaler Store mit `r7` als Basisregister steht im Body nicht.

| VMA | Beobachtung |
|---:|---|
| `0x341f44..0x341f4c` | `ip=S`; bedingte Vergleiche zuerst `r1` mit 0, dann (nur wenn `r1!=0`) `r0` mit 0. |
| `0x341f50..0x341f70` | Prolog; `fp=S-4`, SP=`S-48`; Eingänge gesichert; `[S-48]=0`. |
| `0x341f74` | Wenn erster Vergleichspfad Null ergab: `r0=2`, Return bei `0x342094`. |
| `0x341f78..0x341f90` | `r2`-Nullprüfung springt zu `0x342098`; `r3`-Null und `*[r3]`-Null führen zum Return `2`. |
| `0x342098..0x3420a0` | Auf `r2==0`: falls `r3!=0`, schreibt `r2` (hier 0) nach `[r3]`; springt zu Initialisierung `0x341f94`. |
| `0x341f94..0x342008` | Globale gelesene Werte, bedingter Call bei `0x341fc8`, weitere Calls bei `0x341fe0` und `0x341ff0`; Pfade setzen/lesen lokale `[S-44]`. Callee-Körper ausgeschlossen. |
| `0x342010..0x342044` | Liest `[S]`; wenn nicht null, direkter Call mit `r0=[S]`; der Rückgabewert wird lokal angepasst und bei `0x342040` nach `[r4]` geschrieben. |
| `0x342048..0x342074` | Lädt erneut `[S]`; direkter Call mit `r0=r7=input r2`, `r2=[S]`; danach möglicher weiterer direkter Call mit `r0=r7` und Store an `[r4]`. |
| `0x342078..0x342094` | Direkter Call bei `0x34207c`, Laden von `r0=[S-44]`, gemeinsamer Epilog/Return. |
| `0x3420a4..0x3420dc` | Vergleichs-Call und direkter Call mit `r0=input r1`, `r1=input r2`, `r2=input r3`; Ergebnis wird lokal gespeichert/geprüft. |
| `0x3420e0..0x342108` | Schreibt `[S]` nach `[r4]`, oder direkter Call mit `r0=[S-48]`, `r1=input r2`, `r2=input r3`; speichert dessen Rückgabe lokal. |
| `0x34210c..0x34213c` | Initialisiert global referenzierten Pool via Call; speichert Rückgabe über globalen Zeiger; Fehlerpfad setzt `r0=3`. |
| `0x342140..0x342148` | Setzt `[S-44]=15`, dann Zweig zum gemeinsamen finalen Call-/Returnpfad. |

Die vollständige Tabelle in `instructions.tsv` enthält alle 131 Wörter des Extents, mit Index, VMA, ELF-Dateioffset, exakten Bytes und Dekodierung; der letzte Eintrag ist ausdrücklich als Literal-Datum markiert. `disassembly.raw.txt` ist der begrenzte Roh-Disassembly-Text für den vollständigen Dynsym-Extent.

## Alle sichtbaren Speicherwrites

| VMA | Effektive Speicheradresse | Wert | Bezug |
|---:|---|---|---|
| `0x341f50` | `S-36..S-1` via `push` | r4-r8, r11, r12, LR, PC | Prolog-Sicherung, nicht `[S]`. |
| `0x341f70` | `[S-48]` | 0 | Lokalslot. |
| `0x341fd8` | `[S-44]` | 1 | Lokalslot. |
| `0x341ff8` | `[S-44]` | zurückgekehrtes `r0` | Lokalslot. |
| `0x342008` | `[S-44]` | 1 | Lokalslot. |
| `0x342040` | `[input r3]` via `r4` | `r0` aus Call `0x342020`, lokal um 1 erhöht und ggf. durch vorher geladenes Wort begrenzt | Kein direkter `[S]`-Store; Alias offen. |
| `0x342070` | `[input r3]` via `r4` | Rückgabewert aus Call `0x342068` | `r7=input r2` war zuvor Call-Eingabe, nicht Store-Basis. |
| `0x34209c` | `[input r3]` via `r3`, bedingt | `r2=0` | r2 nur als gespeicherter Wert. |
| `0x3420d0` | `[S-44]` | Rückgabe von `0x0033f548` | Lokalslot. |
| `0x3420e4` | `[input r3]` via `r4` | geladener Wert `[S]` | Potenzieller unbekannter Alias. |
| `0x342108` | `[S-44]` | Rückgabe von `0x003403a4` | Lokalslot. |
| `0x342120` | `[r8]` | Rückgabe von `0x0018027c` | Global/indirektes Ziel. |
| `0x342144` | `[S-44]` | 15 | Lokalslot. |

`[S]` wird lokal ausschließlich gelesen; ein direkter Store an diese Adresse ist nicht vorhanden. Im Body steht kein lokaler Store mit Basisregister `r2`/`r7`. Der Wert aus `r7` wird an `0x00304760` übergeben, aber der Callee ist ausgeschlossen und seine Speicherwirkung bleibt offen. Stores über `[input r3]` könnten bei Aliasierung `[S]` treffen; Aliasbeleg fehlt, daher bleibt dies **OFFEN**.

## Instruktionsgebundene Rückgabepfade

| VMA(s) | lokaler `r0`-Wert vor Epilog | Einordnung |
|---|---|---|
| `0x341f74 → 0x34208c`; `0x341f84 → 0x34208c`; `0x341f90 → 0x34208c` | `mov r0,#2` bei `0x34208c` | frühe Nullprüfungen; Rückkehr über `ldm` bei `0x342094` |
| regulärer Pfad nach `0x342078` | `ldr r0,[r11,#-40]` bei `0x342080`, also lokaler Slot `[S-44]` | Rückkehr über `ldm` bei `0x342088`; Slot kann durch gelistete lokale Stores oder Callrückgaben beeinflusst sein |
| `0x342138 → 0x342090` | `mov r0,#3` bei `0x342138` | Initialisierungsfehlerpfad; Rückkehr über `ldm` bei `0x342094` |
| `0x342140 → 0x342078 → 0x342080` | `15` wird bei `0x342144` in `[S-44]` geschrieben, danach in `r0` geladen | gemeinsamer Call-/Rückkehrpfad über `0x342088` |

Dies sind statisch sichtbare Registerwerte unmittelbar vor den lokalen Epilogen. Ein vollständiger Sprach- oder API-Vertrag ist daraus nicht abgeleitet.

## Direkte Calls und Zustand

Direkte Kanten, Körper ausgeschlossen; `S=entry_sp`, `?` bedeutet aus lokalem Code nicht sicher bestimmbar, oft wegen Callee-Clobber. SP ist bei allen Calls `S-48`.

| Callsite → Ziel | r0 | r1 | r2 | r3 |
|---|---|---|---|---|
| `0x341fc8 → 0x0007c218` | input r0 | `0x003a41a8` | input r2 | global geladener Prüfwert |
| `0x341fe0 → 0x0017f1a4` | `[r8]` | unbekannt / durch vorherigen Call clobberbar | unbekannt / durch vorherigen Call clobberbar | unbekannt / durch vorherigen Call clobberbar |
| `0x341ff0 → 0x00341934` | input r0 | input r1 | `S-48` | ? |
| `0x342020 → 0x0007bde0` | `[S]` | ? | ? | ? |
| `0x342050 → 0x00304760` | input r2 (`r7`) | ? | `[S]` | ? |
| `0x342068 → 0x0007bde0` | input r2 (`r7`) | ? | ? | ? |
| `0x34207c → 0x0017f108` | `[r8]` | ? | ? | ? |
| `0x3420b4 → 0x0007afe8` | `0x003a4ec0` | input r1 | 9 | ? |
| `0x3420cc → 0x0033f548` | input r1 | input r2 | input r3 | ? |
| `0x342100 → 0x003403a4` | `[S-48]` | input r2 | input r3 | ? |
| `0x34211c → 0x0018027c` | 536 | 608 | Literalwort von `0x0034214c` | `S-44` |

Die vollständigen direkten Call-Instruktionen, Bytes und aufgelösten Zustände sind außerdem in `calls.tsv` enthalten. Keine Dynsym-Namen werden als Signatur- oder Semantikbeleg verwendet.

## REA und begrenzter Fallback

REA wurde zuerst anhand vorhandener Records mit dem exakten ELF-Hash geprüft. Der frische retained-record-Befund in WP-XE164-158 nennt für diesen Zielhash null Records und null Evidence-IDs. Die älteren hashgleichen WP-XE164-118-Records betreffen unter anderem `0x00330610`/`0x00330664`; WP-XE164-153/155/156 behandeln andere Funktionsbereiche oder Caller-Setup. Es wurde kein retained Record zum exakten Body `0x341f44..0x342150` gefunden. Eine unabhängige Neuimport-/Ghidra-Erhebung ist wegen des dokumentierten Hängers **BLOCKED** und wurde nicht wiederholt.

Fallback: GNU `readelf` und `/usr/bin/arm-linux-gnueabihf-objdump`, GNU Binutils 2.44; gezieltes Listing nur für den Dynsym-Extent. Dateioffset und VMA sind oben getrennt angegeben; eine Runtime-Adresse wurde nicht bestimmt. Das Listing dekodiert als ARM A32 little-endian. Kein Netzwerk, VM, Gerät oder Hardwarezugriff.

Alternative Erklärung: `[S]` kann ein Zeiger oder ein anderes Wort sein; lokale Instruktionen belegen nur seinen Transport in Register und an Calls. Namen `strlen`, `CMUtlSafeStrCpy`, `SettgBeGetStringValue` und andere Symbole bestimmen keinen vollständigen Vertrag. Caller-/Callee-Semantik und Laufzeit-Aliase bleiben offen.

## Status, Validator und Paket

| Aussage/Prüfung | Status | Ergebnis / Begründung |
|---|---|---|
| Zielgröße und SHA-256 | VERIFIZIERT | Hash und Größe stimmen mit der vorgegebenen Eingabe überein. |
| frisch ermittelter Dynsym-Extent/Ende | VERIFIZIERT | Dynsym-Größe 524 Bytes; Ende exklusiv `0x342150`. |
| VMA-/Dateioffsetabbildung und 524 Bytes | VERIFIZIERT | Offsetabbildung und vollständige Tabellenabdeckung geprüft. |
| lokaler Kontrollfluss, Datenfluss, Writes, Calls, Returns | VERIFIZIERT | Aus Instruktionen des begrenzten Extents abgeleitet. |
| Semantik, Aliasauflösung, Callee-Wirkung und Runtime | OFFEN | Nicht aus dem begrenzten statischen Befund bestimmbar. |
| retained exact-hash record für diesen Body gefunden | VERIFIZIERT | Nein; hashgefilterter retained-record-Befund ergab null Treffer. |
| unabhängige Neuimport-/Ghidra-Erhebung | BLOCKED | Dokumentierter identischer Import hängt; nicht wiederholt. |
| `python3 validate.py` | PASS | Validator erfolgreich. |
| `sha256sum -c SHA256SUMS` | PASS | Manifestprüfung erfolgreich. |

Workerbericht, Self-Review; kein unabhängiger Reviewer behauptet. Pseudocode beziehungsweise Ablaufbeschreibungen sind Analystenableitungen aus den Instruktionen.

Dateien: `report.md`, `instructions.tsv`, `calls.tsv`, `disassembly.raw.txt`, `generate.py`, `validate.py`, `tool_versions.txt`, `validator_result.txt`, `SHA256SUMS`. Das Hashmanifest listet alle Dateien außer sich selbst.
