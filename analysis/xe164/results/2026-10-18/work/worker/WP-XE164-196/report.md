> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-196 — `r5` and stack slot `[sp+0x70]`

## Frage und Ergebnis

Belegt der vollständige IoDrvDal-Körper `[0x2ddc,0x331c)`, dass das bei `0x2fe0` in `r2` kopierte Wort die Adresse des bei `0x3004` gelesenen Stackslots `[sp+0x70]` ist?

**HYPOTHESE.** Der Körper enthält die direkte Definition `r5 := sp+0x70` bei ELF-VA `0x30bc` und später `r2 := r5` bei `0x2fe0`. Auf dem erfolgreichen Pfad lädt `0x3004` anschließend ein Wort aus `[sp+0x70]`. Der Körper selbst beweist aber nicht, dass der Wert von `r5` und `sp` über die dazwischenliegenden externen bzw. indirekten Calls unverändert erhalten bleibt. Die Gleichheit ist daher aus diesem Körper allein nicht **VERIFIZIERT**.

## Identität und Methode

- Eingabe: `sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`
- SHA-256: `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` — **PASS**
- REA: `rea-agents 6.5.0`; Ghidra `12.1.4`; Architektur `ARM:LE:32:v8`; ELF shared object.
- Ghidra Image Base ist `0x10000`: in diesem Bericht wird die ELF/Ghidra-Adresse angegeben. Die zugehörige ELF-VA/file offset ist die angezeigte Adresse minus `0x10000`. Der untersuchte Offsetbereich `[0x2ddc,0x331c)` entspricht somit Ghidra `[0x12ddc,0x1331c)`.
- REA Dossier: `ev_97f0686f7d6be484340fdfaa6fbc1538921260faeb2bfdae04b732260c614608`, beobachteter vollständiger Funktionskörper `[0x12ddc,0x1331b]`, 1344 Bytes.
- REA Assembly: `ev_c384b3fa751d09bd0489acbfeb8f53366a78dafcf7607dfd1592644396435ca6`.
- Same-Hash-REA-Evidence wurde vor der Analyse abgefragt: keine Treffer im damaligen REA Evidence-Ledger. Danach wurde das Ziel mit REA/Ghidra geöffnet und die konkrete Funktion analysiert. GNU-Objdump 2.44 wurde als gezielter Rohbyte-/Disassembly-Abgleich für genau `[0x2ddc,0x331c)` verwendet.
- `0x331c` wird von einer in-range-LDR-Literal-Instruktion direkt referenziert. Der Literalwert und Bytes/Code hinter `0x331c` wurden nicht analysiert.

## Vollständige in-scope Definitionen von `r5`

| ELF-VA | Opcode word | Instruktion | Beobachtung |
|---|---:|---|---|
| `0x2f04` / Ghidra `0x12f04` | `e8bd8ff0` | `pop {r4,r5,r6,r7,r8,r9,sl,fp,pc}` | Epilog lädt `r5` aus dem gespeicherten Registerblock; liegt auf Rückkehrpfaden, nicht auf dem Pfad nach `0x2fe0`. |
| `0x30bc` / Ghidra `0x130bc` | `e28d5070` | `add r5,sp,#112` | Einzige explizite lokale Zuweisung an `r5` im Körper. |

Die Prolog-Instruktion `0x2ddc: e92d4ff0 push {...,r5,...}` speichert den anfangs eingehenden `r5`; sie schreibt den Registerwert nicht als lokale Berechnung. Weitere syntaktische `r5`-Vorkommen sind Quellen/Lesen. Der Validator durchsucht den vollständigen begrenzten Disassembly und prüft, dass nur `0x2f04` und `0x30bc` in-range-Ziele von Instruktionen mit `r5` als Ziel sind.

## Vollständige Zugriffe auf `[sp+0x70]`

| ELF-VA | Opcode word | Instruktion | Beobachtung / lokale Kontrollflussrolle |
|---|---:|---|---|
| `0x2fb0` / Ghidra `0x12fb0` | `e59d0070` | `ldr r0,[sp,#112]` | Liest das Wort aus diesem Stack-Offset. Danach wird es in `r0` an den direkten Call bei `0x2fb8` übergeben. |
| `0x3004` / Ghidra `0x13004` | `e59d3070` | `ldr r3,[sp,#112]` | Nur auf dem Zweig `0x2ff4 -> 0x3004` nach Rückkehr `r0==0` von `0x2fec`. Der geladene Wert wird bei `0x3010` als indirektes Callziel benutzt. |

`0x30bc` bildet eine Adresse mit demselben unmittelbaren Offset (`sp+112`), ist aber kein Speicherzugriff auf diesen Slot. Im vollständigen in-range-Disassembly gibt es keine weitere Speicherinstruktion mit Basis `sp` und Offset `0x70`.

## Erreichbarkeitsgebundene Kette

Beobachtete Instruktionen und Kanten:

1. `0x30bc: e28d5070 add r5,sp,#112` bildet lokal die Adresse `sp+0x70` und schreibt sie nach `r5`.
2. Der lokale Kontrollfluss führt durch Initialisierung und danach über `0x32ec -> 0x2f08` in den Bibliotheksladepfad. Auf dem erfolgreichen Weg steht `0x2fb0: e59d0070 ldr r0,[sp,#112]`; anschließend ruft `0x2fb8: ebfff68b bl 0x9ec` mit diesem geladenen Wort in `r0` auf.
3. Nach Rückkehr und den Tests bei `0x2fbc`/`0x2fc0`, sowie dem Aufruf `0x2fd4`, führt der Erfolgszweig über `0x2fdc` nach `0x2fe0`.
4. `0x2fe0: e1a02005 mov r2,r5`, `0x2fe4: e1a0100a mov r1,sl`, `0x2fe8: e1a00007 mov r0,r7` bereiten drei Argumentregister vor; `0x2fec: ebfff66c bl 0x9a4` ist der Call. Der Symbolname `LibraryLoader_LoadSymbol` stammt aus der ELF/REA-Auflösung, nicht aus einer angenommenen Funktionseffekt-Semantik.
5. `0x2ff4: 0a000002 beq 0x3004` führt nur bei Rückgabewert null nach `0x3004`; andernfalls liegt der Call `0x2ffc` auf einem Fehlerpfad, der nach `0x32f0` abzweigt.
6. Auf dem Erfolgszweig liest `0x3004: e59d3070 ldr r3,[sp,#112]` erneut denselben syntaktischen Stackoffset; `0x3010: e12fff33 blx r3` verwendet das gelesene Wort als indirektes Callziel.

Schlussfolgerung aus diesen Beobachtungen: Ohne zwischenzeitliches Register-/Stack-Verändern wäre der in `r2` übergebene Wert dieselbe Adresse `sp+0x70`, die `0x3004` relativ zu seinem `sp` liest. Die Instruktionen beweisen allein die nötige Erhaltung über die Calls nicht.

## Call-Inventar zwischen Definition und `0x3010`

Alle nach `0x30bc` im begrenzten Bereich liegenden Call-Instruktionen, die vor/nach der beschriebenen Kette auf den lokalen Pfaden vorkommen. Die Tabelle ist absichtlich auf Call-Ort, Opcode und lokale Transparenz begrenzt; es wird keine Callee-Wirkung behauptet.

| ELF-VA | Opcode word | Form/Ziel im lokalen Listing | Bedeutung für den Beweis |
|---|---:|---|---|
| `0x316c` | `ebfff609` | `bl 0x998` | Call vor dem Übergang `0x32ec -> 0x2f08`; Callee-Wirkung nicht im Körper belegt. |
| `0x31a8` | `e12fff3a` | `blx sl` | Indirektes Ziel, nicht aufgelöst; Wirkung auf `r5`/`sp` unbekannt. |
| `0x31e4` | `e12fff3c` | `blx ip` | Indirektes Ziel, nicht aufgelöst; Wirkung unbekannt. |
| `0x3220` | `e12fff3c` | `blx ip` | Indirektes Ziel, nicht aufgelöst; Wirkung unbekannt. |
| `0x3258` | `e12fff3c` | `blx ip` | Indirektes Ziel, nicht aufgelöst; Wirkung unbekannt. |
| `0x3298` | `e12fff3c` | `blx ip` | Indirektes Ziel, nicht aufgelöst; Wirkung unbekannt. |
| `0x32c0` | `e12fff3c` | `blx ip` | Indirektes Ziel, nicht aufgelöst; Wirkung unbekannt. |
| `0x32e4` | `e12fff37` | `blx r7` | Indirektes Ziel, nicht aufgelöst; Rückkehrpfad führt bei Erfolg zu `0x2f08`. |
| `0x2f08` | `ebfff6b1` | `bl 0x9d4` | Direkter Call im nachfolgenden Bibliothekspfad; Wirkung auf `r5`/`sp` nicht belegt. |
| `0x2f1c` | `e12fff33` | `blx r3` | Indirektes Ziel, nicht aufgelöst; Wirkung unbekannt. |
| `0x2f38` | `ebfff6b1` | `bl 0xa04` | Direkter Call im Listendurchlauf; Wirkung nicht belegt. |
| `0x2f4c` | `ebfff6a0` | `bl 0x9d4` | Direkter Call im Listendurchlauf; Wirkung nicht belegt. |
| `0x2f58` | `e12fff33` | `blx r3` | Indirektes Ziel, nicht aufgelöst; Wirkung unbekannt. |
| `0x2f9c` | `ebfff68f` | `bl 0x9e0` | Direkter Call vor erstem Slot-Load `0x2fb0`; Wirkung nicht belegt. |
| `0x2fb8` | `ebfff68b` | `bl 0x9ec` | Direkter Call nach `r0 := [sp+0x70]`; Wirkung auf `r5`/`sp` nicht belegt. |
| `0x2fd4` | `ebfff687` | `bl 0x9f8` | Direkter Call vor `r2 := r5`; Wirkung nicht belegt. |
| `0x2fec` | `ebfff66c` | `bl 0x9a4` | Symbol-Lade-Call; Return steuert den Zweig zu `0x3004`. Wirkung jenseits des beobachteten Rückgabevergleichs offen. |
| `0x2ffc` | `ebfff662` | `bl 0x98c` | Nur Fehlerzweig nach nicht-null Rückgabe bei `0x2ff0`; dieser Zweig erreicht `0x3004` nicht. |
| `0x3010` | `e12fff33` | `blx r3` | Verwendet das bei `0x3004` geladene Wort als Callziel; liegt nach dem zweiten Slot-Load. |

Für die Wertgleichheit sind insbesondere die Calls `0x316c` bis `0x32e4`, `0x2f08` bis `0x2f9c`, `0x2fb8` und `0x2fd4` zwischen Definition und Argumentkopie sowie `0x2fec` zwischen Argumentkopie und zweitem Stack-Load relevant. Die Callees werden hier nicht als transparent angenommen. Der bedingte `0x2ffc` gehört nicht zum Pfad, der `0x3004` erreicht; `0x3010` liegt nach dem späteren Load.

## Beobachtung, Schlussfolgerung, Alternative, Restunsicherheit

- **Beobachtung:** `r5` wird lokal bei `0x30bc` mit `sp+0x70` beschrieben und lokal erst im Epilog `0x2f04` wieder aus dem gesicherten Registerblock geladen. `r2` erhält bei `0x2fe0` den momentanen Wert von `r5`. `0x2fb0` und `0x3004` lesen denselben notierten Stackoffset. **Status: VERIFIZIERT.**
- **Schlussfolgerung:** Diese Folge ist mit `r2` als Adresse desselben später gelesenen Slots konsistent und spricht stark dafür. **Status: HYPOTHESE.**
- **Alternative:** Ein Call zwischen Definition und `0x2fe0` könnte unter einem außerhalb dieses Körpers nicht belegten Effekt `r5` verändern; Änderungen von `sp` in/über Calls könnten außerdem den relativen Slot bei `0x3004` verschieben. Dann wäre `r2` nicht dieselbe Adresse wie die später aus `sp+0x70` gebildete Adresse. Das ist keine Behauptung, dass ein konkreter Callee dies tut.
- **Restunsicherheit:** Es fehlen in diesem Scope verifizierte Callee-Körper bzw. ein anderweitig belegter Register-/Stack-Erhaltungsvertrag für alle aufgeführten Calls. Es wurde keine Ausführung beobachtet. Deshalb bleibt die Gleichheit **OFFEN** als strikte Beweisfrage; Gesamtergebnis **HYPOTHESE**.

## Reproduzierbare Validierung

`python3 validate.py` prüft Eingabehash, genauen bounded objdump-Disassembly, die vollständigen `r5`-Vorkommen/Definitionen, beide `[sp+0x70]`-Loads und ausgewählte Opcodewörter. Ergebnisdatei: `validation.txt`. Teststatus: **PASS**.

## Erzeugte Dateien und SHA-256

Die Hashes stehen in `SHA256SUMS`. `rea-evidence-bundle.json` enthält die 19 während dieses Auftrags erfassten REA-Evidence-Datensätze (Dossier, Assembly und gezielte Instruktionsbeobachtungen).
