> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-227 — lokale Aufrufkette in ELF-VA `[0x36b0,0x36f4)`

## Ergebnis

**VERIFIZIERT** — Das Fenster enthält die drei expliziten Feldloads relativ zu `r0` mit Offsets `+0`, `+8` und `+0xc`, jeweils gefolgt von einem indirekten Aufruf über `r3`. Für `+0` und `+8` folgt innerhalb des Fensters ein lokales Null-Gate auf dem nach `blx` sichtbaren `r0`; ein Nichtnullwert verzweigt jeweils zu `0x36f4`, außerhalb des Fensters. Der `+0xc`-Aufruf hat im Fenster kein entsprechendes Gate; direkt danach wird der sichtbare `r0`-Wert nach `r5` kopiert.

**OFFEN** — Die Instruktionen allein belegen nicht, dass diese Feldpositionen semantisch bestimmte Slots einer Struktur oder einer API-Tabelle sind. Die Zuordnung zur von `adi_GetApplicationInterface()` zurückgegebenen Position wird hier nur als durch die Frage vorgegebene Arbeitshypothese betrachtet. Die Bedeutung der drei Werte bleibt unbekannt.

## Quelle und Werkzeug

**VERIFIZIERT** — Eingabe: `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`, 25,976 Byte, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.

**VERIFIZIERT** — REA `open_binary` identifizierte ELF/ARM mit diesem Hash. Der Provider war Ghidra 12.1.4; die dekodierte Variante meldet `ARM:LE:32:v8`. REA `list_segments` meldete Image-Base `0x10000`, und der ausführbare `.text`-Bereich enthält das Fenster nach der entsprechenden Abbildung. Deshalb wurden die Instruktionen bei Provider-VA `0x136b0` bis `0x136f0` abgefragt, entsprechend ELF-VA `0x36b0` bis `0x36f0` (`Provider-VA = ELF-VA + 0x10000`). Die anfängliche Abfrage unverschobener VAs ergab `outside-memory`; die Segmentbeobachtung klärte dies als Adressabbildung auf. Kein objdump-/Ghidra-Fallback wurde benötigt.

**VERIFIZIERT** — Evidenz: `open_binary` bestätigte Artefaktidentität; Segment-Evidenz `ev_cd2cf5d558dd27b52c198df044b7ae0e6f920c8a0b2001a5d5d5bbb913194140`; die folgende Tabelle nennt die jeweilige `inspect_native_instruction`-Evidenz-ID. Ghidra meldete bei jedem dekodierten Befehl 4 Bytes und A32/ARM-Variantenmodus `v8`.

## Vollständige Instruktionstabelle

**VERIFIZIERT** — Diese 17 Instruktionen belegen genau die 68 Bytes `[0x36b0,0x36f4)`. Die Bytes sind in der Reihenfolge aus REA/Ghidra wiedergegeben.

| ELF-VA | Bytes | A32-Disassemblierung | Lokaler Flow / Evidenz |
|---|---|---|---|
| `0x36b0` | `c7f4ffeb` | `bl 0x000109d4` | Call; Fallthrough `0x36b4`; `ev_c3d68250d5e1258c8f2854e40219ec0e8e583462fc3fd5f71d7fb26e581fec18` |
| `0x36b4` | `003090e5` | `ldr r3,[r0,#0x0]` | Fallthrough `0x36b8`; `ev_17a3d1719f6e497915f8fb93d5bca1163f8520f469dac94153019c809263879c` |
| `0x36b8` | `33ff2fe1` | `blx r3` | berechneter Call; Fallthrough `0x36bc`; `ev_f33f986f0d339c6acd1ddd91845b73bbf616cf121198d50da57929a183c9b269` |
| `0x36bc` | `005050e2` | `subs r5,r0,#0x0` | Fallthrough `0x36c0`; setzt Flags aus der Subtraktion; `ev_d42f8ccca5eb649fd6d152083518e8ca506cc2a0fa835e50e07941398d2fa34e` |
| `0x36c0` | `0b00001a` | `bne 0x000136f4` | bedingter Branch nach ELF-VA `0x36f4` (Fensterende); Fallthrough `0x36c4`; `ev_810f6694253fa10abe5a3626b03685cd3a95a47408283798542e46f9a733e33c` |
| `0x36c4` | `c2f4ffeb` | `bl 0x000109d4` | Call; Fallthrough `0x36c8`; `ev_38e1a6ef9201f7471f1169af55f34901f386fa2c745d2475bd1c97ed72f28c03` |
| `0x36c8` | `083090e5` | `ldr r3,[r0,#0x8]` | Fallthrough `0x36cc`; `ev_7b87a3de9c9e5966c223d8c2c12341fced5b2b7788ecbab38b8a6ad5a389a8a0` |
| `0x36cc` | `33ff2fe1` | `blx r3` | berechneter Call; Fallthrough `0x36d0`; `ev_e4e1e9dd9687f674a49a5d7439c495802e2db8d2753e83a8e26fce3a04e947c8` |
| `0x36d0` | `005050e2` | `subs r5,r0,#0x0` | Fallthrough `0x36d4`; setzt Flags aus der Subtraktion; `ev_2db9f80c1da57c29eb7778af6538d05cbc5780fc6cd922f81cb8a129c3c23f56` |
| `0x36d4` | `0600001a` | `bne 0x000136f4` | bedingter Branch nach ELF-VA `0x36f4` (Fensterende); Fallthrough `0x36d8`; `ev_b76d27e4ba64614ba539802f39690556ec3911eb4399558220066277898c08e0` |
| `0x36d8` | `bdf4ffeb` | `bl 0x000109d4` | Call; Fallthrough `0x36dc`; `ev_72b69e1553fea073614c64c1e82910523b5430da48ebd7376b3690712ed1243b` |
| `0x36dc` | `5c208de2` | `add r2,sp,#0x5c` | Fallthrough `0x36e0`; `ev_2789697b48ca964147f46dac9181ee617cd12bcda00aba609e5d1f6325fc479d` |
| `0x36e0` | `60108de2` | `add r1,sp,#0x60` | Fallthrough `0x36e4`; `ev_fed279708069290b36b3a51deea4b6601bbf5215e4054dba16c0783e19d846f8` |
| `0x36e4` | `0c3090e5` | `ldr r3,[r0,#0xc]` | Fallthrough `0x36e8`; `ev_8a3dfddc0c22db6b91d9c82beb4485a323a244cd4ae6dd6a62686b15e95e0d3a` |
| `0x36e8` | `0a00a0e3` | `mov r0,#0xa` | Fallthrough `0x36ec`; `ev_2299b46f78638d6791d1d3262ef2d315f4b631d0659156d97fc439b9c83af460` |
| `0x36ec` | `33ff2fe1` | `blx r3` | berechneter Call; Fallthrough `0x36f0`; `ev_b756612c48248240fb8b9e3a8d0c0ff01be48699f34e57d49869792e3d45bd3a` |
| `0x36f0` | `0050a0e1` | `cpy r5,r0` | Fallthrough `0x36f4` (Grenze, nicht untersucht); `ev_cfecaa33c3a9ff7d654575e9d3e54ec5610b08846794843ba59a4408190fe898` |

## Lokaler Kontrollfluss

**VERIFIZIERT** — Kanten innerhalb des Fensters verlaufen linear über Fallthrough, außer den beiden bedingten BNE-Kanten. Beide Branchziele sind `0x36f4`, direkt hinter dem abgegrenzten Bereich; die Analyse behauptet weder Zielinhalt noch Zielwirkung. Der `bl`- und `blx`-Kanten sind Call-Kanten mit sichtbarem Rückkehr-Fallthrough; Callee-Effekte bleiben opaque.

| Eintritt / Pfad | Bedingung und Folge | Evidenz |
|---|---|---|
| `0x36b0 → 0x36b4 → 0x36b8 → 0x36bc → 0x36c0` | sichtbare Sequenz aus direktem Call, Load bei `+0`, indirektem Call, Nullvergleich | Instruktionen `ev_c3d682…`, `ev_17a3d1…`, `ev_f33f98…`, `ev_d42f8c…`, `ev_810f66…` |
| `0x36c0` BNE genommen | Sprung nach `0x36f4`, außerhalb; übrige Slots werden über diesen lokalen Pfad ausgelassen | `ev_810f6694253fa10abe5a3626b03685cd3a95a47408283798542e46f9a733e33c` |
| `0x36c0` Fallthrough → `0x36c4…0x36d4` | direkter Call, Load bei `+8`, indirekter Call, Nullvergleich | Instruktionen `ev_38e1a6…`, `ev_7b87a3…`, `ev_e4e1e9…`, `ev_2db9f8…`, `ev_b76d27…` |
| `0x36d4` BNE genommen | Sprung nach `0x36f4`, außerhalb; `+0xc`-Load und Aufruf werden über diesen lokalen Pfad ausgelassen | `ev_b76d27e4ba64614ba539802f39690556ec3911eb4399558220066277898c08e0` |
| `0x36d4` Fallthrough → `0x36d8…0x36f0` | direkter Call, Setzen von `r2` und `r1` auf `sp+0x5c` und `sp+0x60`, Load bei `+0xc`, `r0=0xa`, indirekter Call, `cpy r5,r0` | Instruktionen `ev_72b69e…` bis `ev_cfecaa…` |
| `0x36f0` Fallthrough | `0x36f4`, außerhalb des Bereichs | `ev_cfecaa33c3a9ff7d654575e9d3e54ec5610b08846794843ba59a4408190fe898` |

## Slotbezogene Bindung

**VERIFIZIERT** — `bl` bedeutet hier nur einen im Fenster direkt codierten Aufruf zu `0x109d4`; der Zielcode wurde nicht untersucht und der Name/die Semantik wird nicht behauptet. Bei allen Loads setzt das lokale Disassembly `r3 := Mem32[r0 + Offset]` (als syntaktische Lesart der Instruktion), und der folgende `blx r3` verwendet den dann sichtbaren `r3` als berechnetes Call-Ziel.

| Fragliche Position | Load / indirekter Call (ELF-VA) | Sichtbare Register-/Argumentbelegung | Sichtbare Nachaufrufverwendung und Gate |
|---|---|---|---|
| `+0` | `0x36b4 ldr r3,[r0,#0]`; `0x36b8 blx r3` | Vor dem Load ist keine lokale Definition von `r0` nach dem opaque `bl 0x36b0` vorhanden. `r3` wird direkt aus `[r0]` geladen und im nächsten Befehl indirekt aufgerufen. | `0x36bc subs r5,r0,#0` verwendet den sichtbaren Nachaufrufwert in `r0`, schreibt den Subtraktionsergebniswert in `r5` und setzt Flags. `0x36c0 bne 0x36f4` verzweigt, wenn Ergebnis ungleich null ist; andernfalls Fallthrough zu `0x36c4`. Dies ist keine Behauptung über einen ABI-Rückgabevertrag. |
| `+8` | `0x36c8 ldr r3,[r0,#8]`; `0x36cc blx r3` | Vor dem Load liegt ein lokales `bl 0x36c4`; `r0` danach wird als Basis benutzt, ohne Aussagen über Callee-Vertrag oder Registerkontinuität innerhalb des Calls. `r3` wird direkt aus `[r0+8]` geladen und im nächsten Befehl indirekt aufgerufen. | `0x36d0 subs r5,r0,#0` verwendet den sichtbaren Nachaufrufwert in `r0` und setzt Flags. `0x36d4 bne 0x36f4` verzweigt, wenn Ergebnis ungleich null ist; andernfalls Fallthrough zu `0x36d8`. Kein ABI-Rückgabevertrag abgeleitet. |
| `+0xc` | `0x36e4 ldr r3,[r0,#0xc]`; `0x36ec blx r3` | Nach `bl 0x36d8` definiert `0x36dc` `r2=sp+0x5c`, `0x36e0` definiert `r1=sp+0x60`; `0x36e4` lädt `r3` aus `[r0+0xc]`; `0x36e8` überschreibt `r0` lokal mit `0xa`. Damit sind unmittelbar vor `blx r3` genau diese lokalen Definitionen für `r0`, `r1`, `r2`, `r3` sichtbar. Die Basis `r0` des Loads ist seit dem opaque direkten Call bei `0x36d8` nicht lokal neu definiert. | `0x36f0 cpy r5,r0` kopiert den nach dem Aufruf sichtbaren `r0`-Wert nach `r5`. Im Fenster folgt darauf kein Gate. Das Ende des Fensters verhindert Aussagen über spätere Verwendung. Kein ABI-Rückgabevertrag abgeleitet. |

## Beobachtung, Schlussfolgerung, Unbekanntes

**VERIFIZIERT — Beobachtung:** Die Instruktionsfolge zeigt Feldzugriffe aus `r0` bei den drei Offsets und `blx r3` nach jedem Load. Die ersten beiden Aufrufsequenzen besitzen lokal sichtbare `subs`/`bne`-Paare. Der dritte besitzt lokale Argumentvorbereitung, indirekten Call und `r5`-Kopie.

**VERIFIZIERT — Schlussfolgerung im engen Instruktionssinn:** Es gibt eine bedingte lokale Kette: der Fortgang zu den Offsets `+8` und `+0xc` hängt jeweils davon ab, dass der vorangehende sichtbare Vergleich `r0 - 0` null ergibt. Der Fortgang zu `+0xc` erfolgt nach derselben sichtbaren Bedingung bei der Sequenz `+8`.

**OFFEN — Unbekannt:** Ob `0x109d4` tatsächlich `adi_GetApplicationInterface()` oder ein anderer Getter/Thunk ist; ob `r0` dessen API-definierte Rückgabe ist; die Identität/Semantik des Objekts, der drei Felder oder der durch `r3` aufgerufenen Funktionen; ABI-Verträge; Werte zur Laufzeit; Callee-Effekte; und Kontrollfluss nach `0x36f4`.

**HYPOTHESE — Alternative Erklärung:** Dieselben Bytes passen zu einer Struktur mit drei Funktionszeigern, aber ebenso zu generischen Callback- oder Dispatch-Feldern eines beliebigen Objekts, das in `r0` ankommt. Positionsfolge, Aufrufziel oder Feldoffset allein legen keine API-Semantik fest.

## Einschränkungen und Restunsicherheit

**VERIFIZIERT** — Die Betrachtung ist auf das gelieferte ELF, den Hash oben und das Fenster `[0x36b0,0x36f4)` beschränkt. Die drei direkten Call-Ziele und die zwei Branchziele liegen außerhalb und wurden nicht semantisch analysiert. Die Ghidra-Token enthalten keine detaillierte effektive Speicheradressierungszerlegung; die Basis- und Offset-Lesart stammt aus der sichtbaren ARM-Disassemblierung. Ghidras globale Modusangabe `v8` belegt für sich keine Runtime-Ausführung.

**OFFEN** — Es wird keine Registerkontinuität über opaque Calls angenommen, sofern das Fenster keine neue Definition zeigt. Post-`blx` `r0` wird nur als der lokal sichtbare Registerwert beschrieben, nicht als vertraglich zurückgegebener Wert. Die entscheidende Restunsicherheit ist die fehlende Bedeutung der Objektquelle/Felder und der nicht inspizierten Zielbereiche.

## Validator und Manifest

**VERIFIZIERT** — `validate.py` ist ein Python-3-Validator ohne Drittanbieterpakete. Er prüft Eingabegröße und SHA-256, mappt die 17 erwarteten Bytes über einen ELF32-`PT_LOAD`-Header auf Datei-Offsets, prüft Tabellenvollständigkeit sowie die SHA-256-Werte der Ergebnisdateien aus `manifest.sha256`. Das Manifest ist self-reference-frei: Es enthält nur `evidence.json`, `report.md` und `validate.py`.

Teststatus: **PASS** — Offline-Validator auf der angegebenen Eingabe und den erzeugten Dateien ausgeführt; die Prüfung muss bei jeder Ergebnisdatei im Ausgabeverzeichnis reproduzierbar sein mit `python3 validate.py`.
