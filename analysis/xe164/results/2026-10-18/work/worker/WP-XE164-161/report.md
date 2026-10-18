> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-161 — interner Body `[0x00341934,0x00341a28)`

## Ergebnis

**VERIFIZIERT:** Beim hier untersuchten Eintritt ist `input r2` der vom Callsite gelieferte Wert `S_call-48`. Der Body kopiert ihn bei `0x00341948` nach `r8`. Der einzige spätere Datenfluss aus dieser Kopie ist `mov r3,r8` bei `0x003419b8`; damit wird derselbe Wert beim direkten Call bei `0x003419c8` als Argumentregister `r3` weitergereicht. Innerhalb des begrenzten Bodys wird `input r2` weder dereferenziert noch als Basis eines lokalen Speicherstores verwendet. Der Body schreibt daher lokal nicht direkt durch `input r2`; jede mögliche Wirkung über den weitergereichten Wert hängt vom ausgeschlossenen Callee `0x00340240` ab und bleibt **OFFEN**.

**VERIFIZIERT:** `input r0` wird bei `0x00341954` in `r6` gesichert. Es bleibt am ersten Call `0x00341958` in `r0`, wird an `0x003419a0` beziehungsweise `0x00341a0c` in `r1` übergeben. `input r1` wird bei `0x00341944` in `r7` gesichert und bei `0x003419bc` als `r2` an `0x003419c8` weitergereicht. Die Folge `r0=input r0`, `r1=input r1`, `r2=S_call-48` entspricht dem vorgegebenen Callsite-Zustand; der Wert aus dem dritten Eingangsregister geht im untersuchten Body als viertes Registerargument an einen direkten Call.

## Identität, Umfang und Grenze

| Gegenstand | Nachweis |
|---|---|
| Eingabe | `codesys3`, 5,181,396 Bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` |
| Body | VMA `[0x00341934,0x00341a28)`, 244 Bytes = 61 A32-Instruktionen |
| Nächste Grenze | `readelf -Ws` zeigt bei `0x00341a28` den globalen `FUNC`-Eintrag `SettgBeGetWStringValue`, Größe 856. Das angegebene Ende ist exklusiv; keine Instruktion ab dieser Adresse wurde dekodiert oder ausgewertet. |
| ELF-Abbildung | erster ausführbarer `PT_LOAD`: Offset `0` → VMA `0x00010000`; daher Dateioffsets `[0x00331934,0x00331a28)` = VMA minus `0x10000` |
| Ausrichtung/Deckung | 61 lückenlose 4-Byte-Wörter; letzte erfasste Instruktion bei `0x00341a24`; kein Literal-/Datenwort im Bereich |

Der Bereich beginnt mit `mov ip,sp; push {...,pc}` und einem unmittelbar folgenden Frame-Aufbau. Die nächste Symbolgrenze oben begründet die harte Oberkante; die zugehörige Symbolbezeichnung wird nicht als Funktionsvertrag verwendet. Die VMA ist ELF-Linkadresse, nicht Runtime-Adresse.

## Vollständige Instruktionen und Bytes

Bytes sind in Datei-Reihenfolge (little-endian) angegeben. GNU objdump-Wörter sind daneben zum Abgleich in der üblichen numerischen Schreibweise notiert.

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`disassembly.raw.txt` ist die vollständige unveränderte GNU-Ausgabe für denselben beschränkten Bereich; `instructions.tsv` enthält für jedes Wort VMA, abgeleiteten ELF-Dateioffset, Datei-Bytes, GNU-Wort und Dekodierung.

## Frame, Kontrollfluss und Writes

Mit `B` als SP bei Eintritt in diesen Body: `r12=B`, nach `push` und `sub sp,#20` ist `sp=B-64`; `r11=B-4`. Die lokalen Adressen sind `r11-48 = B-52` und `r11-52 = B-56`. Der gespeicherte zusätzliche Stack-Callwert bei `0x003419c4` liegt bei `[B-64]`. Das ist unabhängig vom Callsite-Ausdruck `S_call-48`, der hier lediglich der Wert des Eingangsregisters `r2` ist.

| Block / Bedingung | Kante und lokale Wirkung |
|---|---|
| `341934..341960` | Sichert Register, kopiert Eingaben, ruft `341818`; Rückgabe-R0 wird in R4/Flags geprüft. Null → `341a00`, nicht-null → `341968`. |
| `341968..341970` | Setzt R9=0, R10=−1 und springt zur Schleife `3419b4`. |
| `341974..341984` | Liest `[r4]`; wenn nicht −1, ruft `1e6674` mit diesem Wert in R0 auf und schreibt danach −1 nach `[r4]`; wenn −1, überspringt Call und Store. Beide Wege → `341988`. |
| `341988..3419b0` | Ruft `3415b0`; setzt R5=0, kopiert Rückgabe in R4. Rückgabe 0 → `341a1c`, sonst → `3419b4`. |
| `3419b4..3419d4` | Ruft `340240`; speichert dessen R0 nach `[B-56]`; nicht-null → Schleifenblock `341974`, null → Abschluss `3419d8`. |
| `3419d8..3419f4` | Wenn `[r4]==−1`, → Epilog `341a20`; sonst ruft `1e6674`, lädt `[B-56]` in R0, schreibt −1 nach `[r4]`, → Epilog `3419f8`. |
| `341a00..341a18` | Alternativpfad ruft `3415b0`; Rückgabe nicht-null → `341968`, null → `341a1c`. |
| `341a1c..341a24` | Lädt Rückgabewert aus `[B-56]` in R0 und kehrt über Epilog zurück. |

Alle sichtbaren Body-Stores: `push` bei `341938` sichert die aufgelisteten Register einschließlich Eintritts-R8; `str r10,[r4]` bei `341984` und `str r3,[r4]` bei `3419f4` schreiben −1 durch den von Call-R0 erhaltenen Wert R4; `str r9,[sp]` bei `3419c4` schreibt 0 in den lokalen Stack-Slot `[B-64]`; `str r0,[r11,#-52]` bei `3419d0` schreibt die Rückgabe des Calls `340240` nach `[B-56]`. Keine dieser Store-Basen ist der Eingangswert `input r2`/sein Alias R8. `r11`-relative Adressen sind lokale Frame-Slots.

## Direkte Callsites: Argumentregister und lokaler Rückgabeverbrauch

Nur sichtbare Registerzustände aus dem eingeschlossenen Body sind aufgeführt. Callee-Bodies, Signaturen und Effekte sind ausgeschlossen. `?` bedeutet, dass der Body vor dem Call keinen belastbaren Zustand für dieses Register erzeugt. Bei Call-Rückkehr werden R0–R3 als caller-clobbered behandelt; nur explizit nachfolgende Neuladungen/Kopien werden weiterverwendet. R4–R11 werden anhand des im Body sichtbaren Sichern/Wiederherstellen als lokal erhaltene Werte verfolgt, nicht als Aussage über Callee-Innenwirkung.

| Callsite → Ziel | R0 | R1 | R2 | R3 | Stackargument / Rückgabe |
|---|---|---|---|---|---|
| `341958 → 341818` | `input r0` | `B−52` | `B−56` | `?` | R0 nach Call für `subs r4,r0,#0`, anschließend Pfadentscheidung. |
| `341980 → 1e6674` | frisch geladen `[r4]` | `?` | `?` | `?` | Rückgabe lokal nicht verwendet; danach Store −1 via `[r4]`. |
| `3419a0 → 3415b0` | R4, außer wenn altes R5≠0: dann 0 | `input r0` (R6) | `B−52` | `B−56` | R0 wird verglichen und nach R4 kopiert; nächster Block entscheidet anhand dieser Rückgabe. |
| `3419c8 → 340240` | R4 | `[B−52]` | `input r1` (R7) | `input r2` (R8 = `S_call−48`) | `[sp]=[B−64]=0` aus R9; R0 wird verglichen, bei `3419d0` nach `[B−56]` gespeichert. |
| `3419e8 → 1e6674` | frisch geladen `[r4]` | `?` | `?` | `?` | Rückgabe lokal nicht verwendet; danach wird −1 nach `[r4]` geschrieben. |
| `341a0c → 3415b0` | 0 (erreichbar vom Nullrückgabepfad des Calls `341958`) | `input r0` (R6) | `B−52` | `B−56` | R0 wird geprüft/kopiert; Null → Rückgabeslot laden, nicht-null → Schleifeninitialisierung. |

Calls nach `0x00340240` und `0x003415b0` sind direkte Calls mit den im lokalen Code sichtbaren Zielen. Die Objdump-Symbolnamen der anderen Ziele oder des Funktionsumfelds werden nicht als Semantikbeleg verwendet. Insbesondere wird nicht behauptet, dass Call `340240` tatsächlich über `input r2` schreibt.

## Input-R2-Nachverfolgung und Antwort auf die Frage

| VMA | Instruktion | Nachweisbarer Effekt auf `input r2` |
|---:|---|---|
| `341948` | `mov r8,r2` | Wert des dritten Eingangs wird in R8 kopiert; R2 danach für andere lokale Argumente wiederverwendet. |
| `341938` / `341a24` | Push/Restore mit R8 im Registersatz | R8 wird für diesen Body gesichert und vor Rückkehr wiederhergestellt. |
| `3419b8` | `mov r3,r8` | Unveränderte Kopie wird als Call-Argument R3 gesetzt. |
| `3419c8` | `bl 0x340240` | Der Wert aus Eingangs-R2 erreicht das Ziel in R3. |

Es gibt im Intervall keine `ldr`/`str`/`ldm`/`stm`-Instruktion mit R8 als Speicherbasis, keine Registerindirektion über R8 und keine Kopie von R8 in eine andere lokale Speicherbasis. Damit ist lokale direkte Dereferenzierung/Schreibung durch den übergebenen Zeiger nicht beobachtet. Eine Aliasbeziehung zu `[r4]` oder den lokalen Adressen ist aus diesem Body nicht belegt. Ob das Callziel unter Nutzung des R3-Werts Speicher verändert, ist wegen der expliziten Callee-Grenze **OFFEN**.

## REA, Fallback, Alternativen und Status

REA wurde zuerst per `get_evidence_bundle` mit exaktem SHA-256 und `detail=summary` abgefragt: 0 retained records, 0 passende Records, 0 unknown revisions. Es gibt deshalb keine REA-Evidence-ID für diesen Body. Eine erneute oder hängende Ghidra-Erhebung wurde nicht gestartet.

Offline-Fallback: GNU ARM `objdump` und `readelf` (Binutils 2.44); unabhängige zweite Dekodierbestätigung mit lokalem Rizin, `pD 244 @ 0x00341934`. Beide liefern 61 aufeinanderfolgende A32-Instruktionen bis einschließlich `0x00341a24`. Das Start-/Endintervall wurde als exakte VMA-Grenze übergeben; Rizin-Bytes außerhalb dieser 244 Bytes wurden nicht angefordert. Werkzeugausgabe und exakte Dateiidentität sind neben diesem Bericht in den Begleitdateien festgehalten.

**Alternative/residual:** Der übergebene `S_call−48`-Wert könnte je nach außerhalb des Scopes liegendem Callerzustand auf andere Daten zeigen. Der Body beweist nur den Werttransport nach R3 beim Call `0x340240`; Pointer-Semantik und Callee-Wirkung sind nicht bestimmt. Caller-/Callee-Erweiterung ist für dieses Paket ausgeschlossen.

| Aussage / Prüfung | Status | Begründung |
|---|---|---|
| Eingabegröße und SHA-256 | VERIFIZIERT | stimmen mit dem vorgegebenen ELF überein |
| Body-Grenzen und nächster Symbolbeginn | VERIFIZIERT | inklusiv start, exklusiv Ende; nächster `FUNC` beginnt bei `0x341a28` |
| Bytebelegung und Dateiabbildung | VERIFIZIERT | 61 Instruktionen, jeder Bytewert gegen ELF und PT_LOAD geprüft |
| Input-R2-Lokalverwendung | VERIFIZIERT | R2→R8; R8 nur als R3 beim Call `0x340240`; kein lokaler Store-/Load-Basisgebrauch |
| Callee-Wirkung und Laufzeit-Aliase | OFFEN | direkte Callee-Bodies und Laufzeitverhalten außerhalb Scope |
| REA retained exact-hash Evidence | VERIFIZIERT | keine Records vorhanden; begrenzter GNU/Rizin-Fallback verwendet |
| `python3 generate.py` | PASS | 61 zusammenhängende Instruktionen aus exakter Eingabedatei |
| `python3 validate.py` | PASS | Identität, Bounds, Symbolgrenze, LOAD-Mapping und sämtliche Bytes |
| `sha256sum -c SHA256SUMS` | PASS | Manifestprüfung nach Erstellung |

Workerbericht und Self-Review, keine unabhängige Prüfung behauptet.
