> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-091 — FW31 Kandidat 0x2120..0x24e3

## Ergebnis und Scope

**VERIFIZIERT** — Der Hash des Eingangsartefakts stimmt mit der Vorgabe überein. REA/Ghidra bildet den Prozedurkörper als zusammenhängenden, inklusiven Bereich ELF-Dateioffset `0x2120..0x24cb` ab (940 Bytes); das exklusive Körperende ist `0x24cc`. Der Literalpool liegt separat bei `0x24cc..0x24e0`; die angeforderte Obergrenze `0x24e4` wurde nicht überschritten. Der letzte Body-Befehl ist bei `0x24c8`; es wurde kein Byte/Record bei oder ab `0x24e4` gelesen oder analysiert.

Der Kandidatenbody enthält einen eigenen GOT-/Jump-Table-Pfad mit Store-Instruktionen bei `0x2464` und `0x24bc`. Dieser Fluss ist **kandidatenintern** und ist nicht die Init-Publikation. Die tatsächliche, separat begrenzte Init-Lane ist unten nur an den ausdrücklich freigegebenen Stellen beschrieben. ELF-VA und Dateioffset stimmen für die Kandidatenbefehle wegen der beobachteten `.text`-Zuordnung überein; Ghidra zeigt diese Adressen mit `+0x10000`.

## Eingangs- und Adressidentität

| Aspekt | Beobachtung | Status / Evidence |
|---|---|---|
| Eingang | 38,584 Bytes; SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` | **VERIFIZIERT**, lokal vor REA geprüft; alle REA-Records binden denselben Digest |
| Format / Architektur | ELF32 little-endian ARM | **VERIFIZIERT**, GNU objdump 2.44; REA/Ghidra 12.1.4 |
| ELF-VA / Dateioffset | `.text` startet ELF-VA `0x1eb8`, Datei `0x1eb8`; Kandidatenbereich wurde von objdump mit `File Offset` ausgegeben | **VERIFIZIERT**, Readelf 2.44 / objdump 2.44 |
| Ghidra-VA | `0x12120..0x124e3` für ELF-Dateioffset/ELF-VA `0x2120..0x24e3`, beobachtete +`0x10000`-Basis | **VERIFIZIERT** an den Grenzen durch Ghidra-Mapping: `0x12120→0x2120`, `0x124cb→0x24cb`, `0x124cc→0x24cc` |
| Laufzeit-/Hardwareadresse | Nicht aus statischem ELF, Ghidra-Mapping oder PC-relativer Rechnung festgestellt | **OFFEN** |
| Prozedurgrenze | `FUN_00012120`, Ghidra Body `0x12120..0x124cb` inklusiv, 940 Bytes, 60 Basic Blocks, nicht diskontiguierlich | **VERIFIZIERT**, `ev_81dcc442…` und `ev_41a1bfa1…` |

## Begrenzter Kontrollfluss und Datenfluss

Parameterbezeichnungen sind ausschließlich Ghidra-Decompiler-Ableitungen (`param_1..param_4`), keine ABI- oder Quelltextverifikation. Rückgabewerte sind konstante bzw. call-abgeleitete Registerwerte; ihre fachliche Bedeutung bleibt unbenannt.

| Kontrollpfad | Beobachtete Bedingung / Datenfluss | Rückgabe-/Folgewert | Evidence |
|---|---|---|---|
| Eingangsguards | `r1==0` oder `r2-1 > 1` (unsigned) verzweigt von `0x2134/0x2148` zum gemeinsamen Returnpfad | `r4=2`, Return an `0x23d0..0x23d8` | `ev_2acd61b7…`, `ev_41a1bfa1…` |
| Bereichsprüfung | `r0-1`, `cmn #3`, `HI` setzt `r4=0x14` und beendet | konstantes `0x14` | `ev_2acd61b7…` |
| Eingabewort-Prüfung | Bei `r2!=1` wird `*(r5+0)==-1` erwartet; sonst wird `*(r5+0xc)` geprüft. Nicht-`-1` führt zu `0xd` | konstantes `0xd` oder Fortsetzung | `ev_2acd61b7…`, `ev_73026634…` |
| Äußere Schleife | `r11` läuft gegen `r8` (übernommen aus `r2`), Zeilenschritt `r3 += 0xc`; vorheriger Fehler beendet zuerst | erster gesetzter Fehler bleibt bis Exitpfad erhalten | `ev_2acd61b7…` |
| Eintragsvalidierung | `[r3+8]` muss nicht null, Halfword `[r3+6]` muss `1`; danach werden die drei Folgezellen bei `r2+0`, `+8`, `+0xc` geprüft. Struktur-/Feldbedeutungen werden nicht benannt | fehlende/ungültige Einträge setzen `r4=2` und springen zur nächsten äußeren Zeile | `ev_2acd61b7…` |
| Kennung / Modus | Halfword über geladenem Zeiger muss `0x8008`; sonst `r4=0xd`. `r6` wird mit `0` und `3` verglichen; andere Werte setzen `r4=0x18` | konstante `0xd` bzw. `0x18` | `ev_2acd61b7…` |
| Erster indirekter Call | `0x22ac: blx r4`; Ziel wird aus Basis `r7` plus Literalwert an `0x24d4` (`0x110`) geladen. Zielkörper nicht untersucht | Ergebnis `r0`: `0` wertet das Halfword bei `[r2+0xe]` gegen `0x1a` mit Bits `0x2` maskiert aus und setzt `0` oder `0x20`; `1`/`2` → `0`; Werte `>2`, außer `4` → `0x36`; `4` → `0` | `ev_90340f96…`, `ev_2acd61b7…` |
| Innere Schleife / Stop | `r10` zählt gegen zuvor geladenen Grenzwert; bei Fehler oder Erreichen des Werts verlässt die innere Schleife. `r2 += 0x14`; Statusfehler wird nicht durch späteren Erfolg überschrieben | Weiter zur nächsten äußeren Zeile oder in spätere Prüfung | `ev_2acd61b7…` |
| Konstante Setup-Call | `0x21a8: bl 0x1fdc` mit `r0=0xaca`; Zielkörper ausgeschlossen. Nicht-nuller Callwert wird in `r4` übernommen und zum Returnpfad geführt | Call-abgeleiteter, unveränderter Wert | `ev_2acd61b7…`, direkte Zielreferenz im Dossier `ev_41a1bfa1…` |
| Globaler Gate-Load | Literal bei `0x24d0` liefert `0x17038`; PC-relative Bildung führt im ELF-Koordinatensystem zum Ladeort `0x19204` (Ghidra `0x29204`). Null an diesem Ladeort setzt `r4=3`, andernfalls Fortsetzung | konstantes `3` oder Fortsetzung | `ev_ea85c22c…`, `ev_ce59cae4…`, `ev_54c56bd3…`, `ev_e6c0dafb…`; Ziel ist Referenzfakt, keine Laufzeitmessung |
| Schleife vor Publikation | Bei Status 0 werden bis zu `r2` Einträge und je Eintrag dessen `+8`-Anzahl über Records mit Schritt `0x14` geprüft. Ein weiterer indirekter Datenzugriff liest `[...+0x18]`; abhängig vom Vergleich gegen `2` wird `0x27` gesetzt. Jump-/Loop-Backedges sind im vollständigen REA-Assembly enthalten | `0x27` kann als erster Fehler gesetzt werden; danach Ende mit abschließendem Call | `ev_2acd61b7…` |
| Zweiter indirekter Call / Jump-Table | Nur bei `r6==3`: `0x2428: blx r1`, Ziel aus `r7 + word[0x24d4]` und einem geladenen Zeiger; `0x2438` dispatcht `r0<=4` über fünf von Ghidra beobachtete Ziele | `r0=0,1→0x2454`; `2→0x248c`; `3→0x249c`; `4→0x2494`; `>4→0x249c` (Standardpfad). Zielkörper nicht untersucht | `ev_98c9d97f…`, `ev_65c73cac…`, `ev_41a1bfa1…` |
| Abschließender direkter Call | `0x23c4: bl 0x12074` mit `r0=0xb64`; Zielkörper ausgeschlossen. Wenn bisher `r4==0`, wird Call-Rückgabe in `r4` übernommen; bei bestehendem Fehler bleibt dieser vorrangig | Call-abgeleiteter Wert oder vorheriger Fehler | `ev_2acd61b7…`, Zielbeziehung `ev_41a1bfa1…` |

**CFG-Abdeckung:** Ghidra beobachtet 60 Blöcke über den vollständigen inklusiven Body. Der vollständige Assembly-Text liegt in `ev_2acd61b7…`, Pseudocode (nur Werkzeugableitung) in `ev_73026634…`, vollständiges CFG im Dossier `ev_41a1bfa1…`. Kernschleifen: äußere Rückkante `0x2310→0x2180`; Eintrags-/Statusschleife `0x2304→0x2278`; Prüfung `0x237c→0x2344`; zweite Pass-Schleife `0x23bc→0x2394` und Datensatzschleife `0x2488→0x23a8`. Die Rückgabeauswertung bei `0x2438` besitzt fünf beobachtete Ziele plus Default; keine Zielkörper wurden geöffnet.

## Kandidateninterner GOT-/Jump-Table-Datenfluss

Alle folgenden Kandidatenzahlen sind ELF-VA/Dateioffset. Ghidra-Adresse ist jeweils `+0x10000`. Diese Tabelle beschreibt ausschließlich Datenfluss innerhalb `0x2120..0x24cb` und darf nicht als Init-Publikation ausgelegt werden.

| ELF/Datei | Instruktion bzw. Poolwort | Exakte Bildung / Wirkung | Evidence |
|---|---|---|---|
| `0x2128` / Ghidra `0x12128` | `ldr r7,[pc,#0x39c]`, effektive Literaladresse `0x24cc` | Poolwort `0x00016ec8` | `ev_6be79418…`, `ev_ea85c22c…` |
| `0x2130` / `0x12130` | `add r7,pc,r7` | ARM-PC `0x2138` + `0x16ec8` = `0x19000`, `.got`-Start aus Readelf. Ghidra-äquivalente Basis `0x29000` | `ev_f41eb47d…`; Readelf 2.44 Abschnittstabelle |
| `0x2494` / `0x12494` | `ldr r1,[pc,#0x44]`, effektive Literaladresse `0x24e0` | Poolwort `0x00000120` | `ev_301566e3…`, `ev_ea85c22c…` |
| `0x2438..0x2450` / `0x12438..0x12450` | `addls pc,pc,r0,lsl #2` plus relative Sprünge | Rückgabewerte `0..4` wählen die dokumentierten Ziele; Fall 4 erreicht `0x2494`; außerhalb `0..4` Standard `0x249c` | `ev_65c73cac…`, `ev_41a1bfa1…` |
| `0x2454..0x2460` / `0x12454..0x12460` | Poolword `0x1ac` (Fall 0/1), danach GOT-Index und ein Pointer-Dereferenzieren | Gemeinsame Ladefolge für Fälle 0/1/2/4; Fall 4 setzt vorher Index `0x120` aus `0x24e0` | `ev_5ba8325c…`, `ev_93af3c45…`, `ev_301566e3…`, `ev_d58b9976…` |
| `0x2464` / `0x12464` | `str r1,[r8,#0x10]` | Kandidateninterner 32-Bit-Store auf `[r8+0x10]` | `ev_d58b9976…` |
| `0x2474`, `0x247c` / `0x12474`, `0x1247c` | `str r1,[r5,#0x1c]`, bedingtes `streq r1,[r5,#0x18]` | Begleitende bedingte Stores; keine semantischen Felder zugeordnet | `ev_f7f6561a…`, `ev_8febb42e…` |
| `0x24bc` / `0x124bc` | `str r10,[r8,#0x10]` | Zweite kandidateninterne Spur schreibt denselben syntaktischen Displacement `+0x10`; zugelieferter Wert ist `r10` | `ev_6200572b…` |

Das im vorigen Lauf betrachtete Label `__cxa_finalize@plt+0x638` für Kandidatenliteral `0x24e0` ist nur eine Disassembler-Symbolanzeige. Die Kandidatenstores `0x2464` und `0x24bc` verwenden beide `[r8,#0x10]`; sie sind nur ein kandidateninterner Lane-Countercheck und werden nicht mit der tatsächlichen Init-Publikation gleichgesetzt.

## Tatsächliche Init-Publikation: minimaler Stack-/Packed-Store-Pfad

Nur die ausdrücklich freigegebenen Init-Stellen wurden abgefragt: ELF-VA/Dateioffset `0x4834`, `0x4838`, `0x483c`, `0x4840`, `0x4844`, `0x4848`, `0x48dc`, `0x48e0`, `0x48e4` und das 4-Byte-Literal bei `0x5330`. Ghidra-Adressen liegen bei den Codebytes jeweils `+0x10000`; das Literal erscheint bei `0x15330`. Kein weiterer Init-Body wurde analysiert.

| ELF/Datei | Ghidra | Beobachtung | Datenfluss |
|---|---:|---|---|
| `0x5330` | `0x15330` | Bytes `e0 d8 ff ff` = little-endian signed `-0x2720` | Literaloperand der PC-relativen Load-Instruktion |
| `0x4834` | `0x14834` | `ldr r3,[0x15330]` | `r3 := -0x2720`; REA-Referenz zeigt exakt auf `0x15330` |
| `0x4838` | `0x14838` | `add r3,pc,r3` | ARM-PC `0x4840` plus `-0x2720` ergibt Codewert `0x2120` |
| `0x483c` | `0x1483c` | `str r3,[sp,#0x24]` | Codewert `0x2120` wird in Stackadresse `sp+0x24` geschrieben; Ghidra DATA-Referenz zeigt auf Kandidatenbeginn `0x12120` |
| `0x4840` | `0x14840` | `ldr r3,[0x15334]` | Nur Register-Load aus Literaladresse; kein Stackwrite |
| `0x4844` | `0x14844` | `vldr.64 d16,[sp,#0x18]` | 64-Bit-Read aus `sp+0x18..0x1f`, disjunkt zu `sp+0x24`; kein Stackwrite |
| `0x4848` | `0x14848` | `vldr.64 d17,[sp,#0x20]` | 64-Bit-Lane lädt Bytes `sp+0x20..sp+0x27`, also auch das zuvor adressierte Wort `sp+0x24..sp+0x27` |
| `0x48dc` | `0x148dc` | `add r3,r0,#0x620` | temporäre Store-Basis `r0+0x620` |
| `0x48e0` | `0x148e0` | `add r3,r3,#0xc` | Store-Basis wird `r0+0x62c` |
| `0x48e4` | `0x148e4` | `vst1.32 {d16,d17},[r3]` | geordneter 4×32-Bit-Packed-Store ab `r0+0x62c`; `d17` ist das dritte/vierte 32-Bit-Wort. Das aus `sp+0x24` gelesene obere 32-Bit-Wort von `d17` liegt damit bei `r0+0x638` |

**VERIFIZIERT (statische Lane-Bindung):** Die explizit beobachtete PC-relative Rechnung ergibt `0x2120`; sie wird durch den Stackstore in die zweite 32-Bit-Hälfte von `d17` geladen und der Packed-Store legt diese Lane bei Output-Displacement `+0x638` ab. Beide dazwischenliegenden Instruktionen wurden gezielt geprüft: `0x4840` lädt nur ein Register aus einer Literaladresse, `0x4844` liest nur den getrennten Stackbereich `sp+0x18..0x1f`; keine schreibt `sp+0x24`. Damit ist der Stacklane-Pfad an den zugelassenen Befehlsstellen geschlossen. Es wird keine Laufzeitadresse oder physische Wirkung behauptet.

### Kandidaten-Literalpool (exakte Bytes und Little-Endian-Wörter)

| ELF-VA = Dateioffset | Ghidra-VA | Bytes | Wort | Statische Verwendung |
|---|---:|---|---:|---|
| `0x24cc` | `0x124cc` | `c8 6e 01 00` | `0x00016ec8` | PC-relativer GOT-Basisaufbau bei `0x2128/0x2130` |
| `0x24d0` | `0x124d0` | `38 70 01 00` | `0x00017038` | PC-relativer Zugriff zum Gate-Ladeort `0x19204` |
| `0x24d4` | `0x124d4` | `10 01 00 00` | `0x00000110` | Indirekte Call-Zielauswahl bei `0x229c` und `0x2420` |
| `0x24d8` | `0x124d8` | `ac 01 00 00` | `0x000001ac` | GOT-Index Fälle 0/1 |
| `0x24dc` | `0x124dc` | `8c 01 00 00` | `0x0000018c` | GOT-Index Fall 2 |
| `0x24e0` | `0x124e0` | `20 01 00 00` | `0x00000120` | GOT-Index Fall 4; angefragtes `+0x638`-Label |

Die 24 Bytes wurden als ein REA-Read bei Ghidra `0x124cc`, vollständig bis `0x124e3`, aufgenommen (`ev_ea85c22c…`). Kein Byte von `0x24e4` oder später war Teil dieses Reads. `inspect_native_instruction` erkennt die sechs Pooladressen als Daten, nicht als Instruktionen.

## Calls, Alternativerklärung und Grenzen

- **VERIFIZIERT:** Im Body sind zwei direkte Calls zu `0x1fdc` und `0x2074` sichtbar; ihre Zielkörper wurden nicht analysiert. Zwei `blx`-Stellen (`0x22ac`, `0x2428`) sind berechnete/indirekte Calls ohne statisch ausgegebenes Ziel. Das Dossier weist deswegen eingeschränkte Callee-Abdeckung aus (zwei nicht aufgelöste Callziele); keine Callback-Semantik wird abgeleitet.
- **VERIFIZIERT:** Ghidra-Auswertung weist an `0x2438` fünf Jump-Table-Ziele aus. Es wurde keine darüber hinausgehende Tabelle oder fremder Body untersucht.
- **Alternativerklärung (HYPOTHESE):** `+0x638` kann beim Blick auf GNU-Objdump als Symboloffset zur von objdump gewählten Nachbarsymbolbasis gelesen werden. Ein gleichnamiger Datenmember oder ABI-Slot ist dafür nicht belegt. Ebenso beweist der statische Store in `[r8,#0x10]` keine zur Laufzeit gültige Ausgabeadresse oder Veröffentlichung an externe Verbraucher.
- **Restunsicherheit (OFFEN):** Laufzeit-Bias, konkrete Registerwerte, Inhalte der referenzierten Zeiger, Verhalten der Call-Ziele, Aliasbeziehungen zwischen den beiden Lane-Stores und Hardwarewirkung. Keine ABI-/FW30-Übertragung, Struct-/Feld-/Slot-/Callback-Namen oder Laufzeitbehauptung.

## Werkzeuge, Evidence und Bundle

REA 6.5.0 / Ghidra 12.1.4 (Provider `ghidra`; Analyseprofil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`); GNU `arm-linux-gnueabihf-objdump` 2.44 und `arm-linux-gnueabihf-readelf` 2.44. REA war primär; GNU-Werkzeuge wurden nur zur begrenzten Auflösung der im REA-Instruktionsresultat explizit nicht verfügbaren Speicheradresszerlegung verwendet. Kein Netzwerk-, Geräte-, VM- oder Runtimezugriff.

Zentrale Evidence-IDs (vollständig im Bundle):

- Prozedurgrenze/Locals: `ev_81dcc442d9c0e91073681a52c41adecca8a2f94beff177fa16037147001bfe6e`
- Vollständige fokussierte Funktion, CFG, Call- und High-pcode-Daten: `ev_41a1bfa1d3991be3a5d1fbbfb3c1a00e336809670e4224cd45fb9d456de1be38`
- Ghidra-Assembly: `ev_2acd61b78f70c1b4a5babae154c5c175dd4bc6d84d1cce75f208c14675cfdddf`
- Pseudocode, ausdrücklich Werkzeugableitung: `ev_73026634e6ff7af708581a7d083ab3a4b9f9eab2fa8a4fd4f576baf10cdaa57a`
- Literalpool-Read: `ev_ea85c22c8d9d99ac7194bb87c4edbea961b6bf7871bffc1634983aca35dcb7ec`
- Init/GOT/Dispatch/Store-Instruktionen: `ev_6be79418fd97fce90eff5713c2ba05d74083b8b90d777f8bab188c3dacc32b8c`, `ev_f41eb47d1e06bdbfdfbe2769ea5c35c14117dce34175a68917be536ab188746d`, `ev_301566e3a9d4314a37d7f2d57399e9fc56ea968093c205dee054db1b389aa3eb`, `ev_65c73cacd13af7dd3d330ec3daac3e728bd5d7b2014f7f0760cd8c8b35300bcd`, `ev_d58b99763bb8f5d641ccbbbb0436c44f223f230f9345c2da81cfab56f7ac273e`, `ev_6200572b4f5378a148e6db2b829f2c4d4af4ec1fee1a835957e7b3b3c8853689`

Das kanonische, unveränderte REA-Bundle liegt in `evidence.bundle.json`: 52 Records, 782,934 Bytes, 0 Unknowns; ein Artefakt (Eingangs-SHA oben), ein Provider (Ghidra 12.1.4). Es enthält den Kandidatenbereich sowie ausschließlich die neun freigegebenen Init-Codeadressen und das eine freigegebene Init-Literal. Der reproduzierbare Validator prüft Digest, Scope-Metadaten, Recordzahl/-größe, Provider, Operationsmenge, erlaubte Quellenadressen und Evidence-IDs. `SHA256SUMS` bindet Bericht, Bundle und Validator.

## Tests

- Eingangshash und Größe: **PASS**
- Ghidra-Prozedurgrenze und File-Offset-Abbildung: **PASS**
- Literalpool-Länge 24 Bytes, Ende `0x24e3`: **PASS**
- Bundle-Scope/Metadaten/Evidence-IDs: **PASS** (reproduzierbarer Validator)
- Unabhängiger Review oder Laufzeittest: **NOT_RUN**

## Vollständiges Evidence-ID-Register

Die oben verkürzten Verweise bezeichnen die folgenden vollständigen IDs; die Prüfroutine verlangt, dass jeder Bundle-Record hier exakt vorkommt.

| Evidence-ID | Operation / Selektor |
|---|---|
| `ev_017ac41a289820bf8b8b361e7e5a87bee03d92285c10c317a46c774034f6ef60` | inspect_native_instruction `0x1229c` |
| `ev_27e0ebf2bdef2e76d2a51ad9cae6147f0f676468c34ceb7262fb10a0d7f9a1cc` | inspect_native_instruction `0x12414` |
| `ev_2acd61b78f70c1b4a5babae154c5c175dd4bc6d84d1cce75f208c14675cfdddf` | procedure_assembly `0x12120` |
| `ev_301566e3a9d4314a37d7f2d57399e9fc56ea968093c205dee054db1b389aa3eb` | inspect_native_instruction `0x12494` |
| `ev_38c1f7cd6916ac0567da0a0b1afa49493cd93d0dba96bdd4639ceab165f31722` | address_to_file_offset `0x124cb` |
| `ev_41a1bfa1d3991be3a5d1fbbfb3c1a00e336809670e4224cd45fb9d456de1be38` | analyze_function `0x12120` |
| `ev_496767e5e6f1a8e9ccb172527c21e21b6283b64da0989094b936ebeca16b289f` | address_to_file_offset `0x124cc` |
| `ev_4bca2bf21667c6540d1fdc9144b972887bbf08cbee6f06070b0418672ebdfe1c` | inspect_native_instruction `0x124d4` |
| `ev_54c56bd3e408a041002828c57490bd07b9fcd5123b178f8535a28662c299d1b8` | inspect_native_instruction `0x121bc` |
| `ev_5ba8325c691a0d3e8a03bbbeb71fcf8b741658812351ce718c9afec7804deef5` | inspect_native_instruction `0x12454` |
| `ev_6200572b4f5378a148e6db2b829f2c4d4af4ec1fee1a835957e7b3b3c8853689` | inspect_native_instruction `0x124bc` |
| `ev_65c73cacd13af7dd3d330ec3daac3e728bd5d7b2014f7f0760cd8c8b35300bcd` | inspect_native_instruction `0x12438` |
| `ev_6be79418fd97fce90eff5713c2ba05d74083b8b90d777f8bab188c3dacc32b8c` | inspect_native_instruction `0x12128` |
| `ev_73026634e6ff7af708581a7d083ab3a4b9f9eab2fa8a4fd4f576baf10cdaa57a` | procedure_pseudo_code `0x12120` |
| `ev_7b321d1b3ffd2607f29c7e17e6c6a1e71f30cb6fc7cf1c6f59686ffcb9a77077` | inspect_native_instruction `0x12420` |
| `ev_7c459212d5590a9da0c6d530cbb765cba730b04374ba55b8505781843a2cc7f8` | inspect_native_instruction `0x124cc` |
| `ev_81dcc442d9c0e91073681a52c41adecca8a2f94beff177fa16037147001bfe6e` | procedure_info `0x12120` |
| `ev_8febb42e012409966192404464cc867cc35b157bc820e364090d44f93a4925de` | inspect_native_instruction `0x1247c` |
| `ev_90340f964e887a46a460bdd10eddc0d879d32d3833757c8896da137a792b5db0` | inspect_native_instruction `0x122ac` |
| `ev_904c45324e1aaa0dc7f7cc61752cfe02af497e652d596d34d6816b66ca96ffe4` | address_to_file_offset `0x12120` |
| `ev_916a83f4b8315a862b80536cfe66fe851bbebe3fa823032b178668c44983a830` | inspect_native_instruction `0x124d0` |
| `ev_93af3c4582e15db23fd449737852a460cb01b770faf72470e4433d0577e01166` | inspect_native_instruction `0x1248c` |
| `ev_98c9d97f81219fcaa7eb2988018938a941240499cf373374752dabfdee65bfe5` | inspect_native_instruction `0x12428` |
| `ev_9a8862b376e051f811a4e83b70229136f18810ca7b492c5ad173e9ad3a7bd180` | inspect_native_instruction `0x124d8` |
| `ev_bfaab738cc7444e82156f015ab9ea58c29cb593ac5cc23b704d0b07d31d01768` | inspect_native_instruction `0x12290` |
| `ev_ce59cae4276da0b997b412479394451e57475499ea4202e0d1373a9ad28b78c8` | inspect_native_instruction `0x121b8` |
| `ev_d58b99763bb8f5d641ccbbbb0436c44f223f230f9345c2da81cfab56f7ac273e` | inspect_native_instruction `0x12464` |
| `ev_e0afe8d6259bb5d4a966b17e821b34116af489c19bc6c8c2fd25477380dc7d8b` | inspect_native_instruction `0x124dc` |
| `ev_e6c0dafb2aa10f9e75e7a39317aaf8664c1d1c807a51fbd5d2597b0163fd3093` | inspect_native_instruction `0x121c0` |
| `ev_e6c9461eefa5d91deb2e1e3b2f5f43a71462dc154d03a6cc7235d40cf7398f51` | inspect_native_instruction `0x124e0` |
| `ev_ea85c22c8d9d99ac7194bb87c4edbea961b6bf7871bffc1634983aca35dcb7ec` | read_bytes `0x124cc`, length 24 |
| `ev_f41eb47d1e06bdbfdfbe2769ea5c35c14117dce34175a68917be536ab188746d` | inspect_native_instruction `0x12130` |
| `ev_f7f6561abd753340a4e03a962fda6bbc8bc6ca05605e2a02d22ac5618676ac54` | inspect_native_instruction `0x12474` |
| `ev_73028aeb7351813a5294a089a8c97446731efac66beb67d15cb49af47b49bec2` | Init inspect_native_instruction `0x14834` (ELF `0x4834`) |
| `ev_8e54fcf5a8eb537a2e0d9e4dee9e25e4207d9ea1c273b2ac86a86ac38ff6989f` | Init inspect_native_instruction `0x14838` (ELF `0x4838`) |
| `ev_5bbcf56acddede56d3e03b81c2638a64348876587e0bdc09843eab8de6395a13` | Init inspect_native_instruction `0x1483c` (ELF `0x483c`) |
| `ev_6ca90d8548ac4d0aa0b3905ad0eaff58240556db307d4742122b99486dc522c8` | Init inspect_native_instruction `0x14848` (ELF `0x4848`) |
| `ev_8bbd192c125cf17527f2224c1e60d52c4efd25823e23d570ec853e5dd6e7fd25` | Init inspect_native_instruction `0x148dc` (ELF `0x48dc`) |
| `ev_b7b52647bb557c6471e089aef6f9edddb2f89bda16315202ddd719df57c18bac` | Init inspect_native_instruction `0x148e0` (ELF `0x48e0`) |
| `ev_227edb89be0fc3a2d2f4c279fba4d9c2c4d6646601e5ae9d5ed61fe53435b394` | Init inspect_native_instruction `0x148e4` (ELF `0x48e4`) |
| `ev_635c9391ae91a1ab9270c9832f52ac87683f70775dd963772f1c9ff1b8a9fb4e` | Init address_to_file_offset `0x14834` |
| `ev_d6b62abe10ea5b5dd67f570c236197438b233266033078c3cc7f6ef110e7dfc7` | Init address_to_file_offset `0x14838` |
| `ev_e2103aa54dd2f74dae290d2972d0590af7bfe0a822d78796ba4d35b130d4578e` | Init address_to_file_offset `0x1483c` |
| `ev_c63f2dc402e824f52fa5fa77bbae7d306cdb20d3f283813c430a8b69db33c4ee` | Init address_to_file_offset `0x14848` |
| `ev_7ad13b329b5f4c61e3a4a388e00f56ab0bcd76bd3cab1e09be95aa584f80c967` | Init address_to_file_offset `0x148dc` |
| `ev_8306e290beb5c0632ab5fc1e628a93e1a6d19e68afc51c94f95704180ecfea03` | Init address_to_file_offset `0x148e0` |
| `ev_8679dcde4024ba6fcf3c5c63f4aa66c73bc1b528be8a31b5f6e9b5677d260962` | Init address_to_file_offset `0x148e4` |
| `ev_edc88cdbf2e500ae7e39a7b3f2ca44089ac282a7cdf43b22c1de463b1944a07a` | Init read_bytes `0x15330`, length 4 (ELF `0x5330`) |
| `ev_cd396b932b1f6310b8842fe6c4c22475645c01c61eb6b9be2011d071a1846b80` | Init inspect_native_instruction `0x14840` (ELF `0x4840`) |
| `ev_3605a1d9d83f95dbf4dd943360fa84f9c94757cd3dee79b7fe3663805ddeaff9` | Init inspect_native_instruction `0x14844` (ELF `0x4844`) |
| `ev_a322167cb8abe3ced2c6be00d56a0aa0f75fb860d91f9ee6d3db059d7691b9c4` | Init address_to_file_offset `0x14840` |
| `ev_8ac91678d5a8c6ef9f0cb70ea4f39fea435c80c8acf37a12754fb6ee12acad61` | Init address_to_file_offset `0x14844` |
