> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-165 — input `r0` im internen Body `0x002FCB48..0x002FCBCB`

## Befund

**VERIFIZIERT:** Der exakt abgegrenzte Body `[0x002FCB48,0x002FCBCC)` umfasst 132 Bytes und 33 fortlaufende 4-Byte-ARM-Instruktionen. Die vollständige VMA-, Datei-Offset-, Byte- und Instruktionstabelle steht in [`instructions.tsv`](instructions.tsv). Byteabdeckung und Quellidentität werden durch [`validate.py`](validate.py) geprüft.

Unter der ausdrücklich angeforderten Caller-Substitution wird der von WP-XE164-163 übergebene lokale Wert `r11−0xB4` als Eingangswert `r0` gesichert: `0x002FCB68: mov r6,r0`. Der Body dereferenziert `r6` nicht und vergleicht `r6` nicht. Auf dem Pfad zum einzigen direkten Call wird bei `0x002FCB84` `r1 := r6` gesetzt. Damit steht der Caller-Wert als sichtbares zweites Registerargument des Calls bei `0x002FCBA8` bereit. Der Callee-Body von `strcmp@plt` ist ausgeschlossen; aus diesem Callzustand allein wird keine Wirkung behauptet.

Der Body führt zusätzlich direkte Loads aus: aus der von `movw/movt` gebildeten Adresse `0x00510868` wird ein Pointer geladen, danach wird von diesem Pointer `+0x1c` geladen. Dieser Wert wird als Startwert in `r5` gehalten und später in `r4` übernommen. Die Listeniteration lädt `[r4]`; für einen nichtnull `r4`-Wert wird ein Halbwort von `[r4+0x3c]` gelesen und als Bedingung lokal um `−2`, Maskierung `bic #2` und `uxth` verarbeitet. Nur wenn das Ergebnis null ist, folgt `ldr r0,[r4+0x14]` und der direkte Call mit `r1=r6`.

Die beobachteten Rückgaben des lokalen Bodys sind `r0=0` auf den Null-/Abbruchpfaden und `r0=1` nach dem Gleichheitszweig des direkten Calls. Die Rückgaben erfolgen durch die zwei sichtbaren `ldm...pc`-Instruktionen. Die Caller-Substitution bleibt eine vom Aufrufer gelieferte Wertidentität: Dieser Body zeigt nur, dass der Wert als zweites Registerargument weitergereicht wird.

## Artefakt und Adressabbildung

| Eingabe | Größe | SHA-256 | Status |
|---|---:|---|---|
| `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3` | 5.181.396 Byte | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | **VERIFIZIERT** |

GNU `readelf -l` zeigt einen ausführbaren `PT_LOAD` mit Dateioffset `0`, VMA `0x00010000` und Dateigröße `0x3a0340`. Daher gilt im untersuchten Bereich `file_offset = VMA − 0x10000`: `[0x002FCB48,0x002FCBCC)` wird zu `[0x002ECB48,0x002ECBCC)` in der Datei. Das exklusive Ende ist nicht dekodiert. Die ELF ist ARM ELF32 little-endian, EABI5.

Die Tabelle `instructions.tsv` enthält für jede Adresse genau die vier Rohbytes direkt aus dem gebundenen Input sowie die korrespondierende begrenzte GNU-objdump-Dekodierung. Keine Daten nach `0x002FCBCC` werden zur Analyse herangezogen.

## Caller-Substitution und Value Flow

WP-XE164-163 dokumentiert bei seinem Call zu `0x002FCB48`: `r0 = r11−0xB4`. Nur dieser konkrete Inputwert wird hier substituiert. Register `r6` wird in diesem Body nach Prolog/Initialisierung nicht erneut beschrieben, bevor es bei `0x002FCB84` in `r1` kopiert wird. Die Schleifenrücksprünge führen durch `0x002FCB6C` und verändern `r6` nicht.

| Stelle | Beobachtung | Aussage zum substituierten Wert |
|---|---|---|
| `0x002FCB68` | `mov r6,r0` | Eingangswert `r0` wird unverändert in `r6` kopiert |
| `0x002FCB84` | `mov r1,r6` | Wert wird in `r1` als zweites Registerargument vorbereitet |
| `0x002FCBA8` | `bl 0x0007C218 <strcmp@plt>` | direkter Call; sichtbare lokale Argumente unten |
| sonst im Body | keine Leseadressierung mit `r6` als Basis/Index, kein `cmp` gegen `r6` | keine direkte Dereferenzierung oder lokale Vergleichsoperation auf dem Caller-Wert belegt |

Zum direkten Call ist lokal sichtbar: `r0 = [r4+0x14]`, `r1 = ursprüngliches Eingangsr0`, `r2 = Eingangs-r2` (im Body nicht neu gesetzt), `r3 = 0` auf dem Callpfad (der Pfad verlangt unmittelbar zuvor `cmp r3,#0` mit Gleichheit). `sp` zeigt auf den durch `push` angelegten Frame. Weitere Stackargumente werden im Body nicht explizit vorbereitet und daher nicht behauptet. Das ist ein Registerzustand, kein rekonstruierter C-Prototyp.

## Direkte Speicherzugriffe

| Adresse | Instruktion | Zugriff |
|---|---|---|
| `0x002FCB54` | `ldr r3,[r3]` | 32-Bit-Load von der Adresse, die aus `movw/movt` in `r3` gebildet wurde (`0x00510868`) |
| `0x002FCB58` | `push {r4,r5,r6,r7,fp,ip,lr,pc}` | schreibt Registerwerte auf den Stack |
| `0x002FCB60` | `ldr r5,[r3,#28]` | 32-Bit-Load von `[r3+0x1c]` |
| `0x002FCB74` | `ldr r4,[r4]` | 32-Bit-Load aus dem von `r4` adressierten Speicher |
| `0x002FCB88` | `ldmeq sp,{r4,r5,r6,r7,fp,sp,pc}` | bedingtes Laden vom Stack; bei Gleichheit Rückkehr über geladenes `pc` |
| `0x002FCB8C` | `ldrh r3,[r4,#60]` | 16-Bit-Load von `[r4+0x3c]` |
| `0x002FCBA4` | `ldr r0,[r4,#20]` | 32-Bit-Load von `[r4+0x14]` als `r0` des direkten Calls |
| `0x002FCBB8` | `ldm sp,{r4,r5,r6,r7,fp,sp,pc}` | Laden vom Stack und Rückkehr über geladenes `pc` |

Es gibt im Bereich keine `str`-Instruktion und keine direkte Store-Instruktion über den substituierten Caller-Pointer. `push` ist der einzige direkte Speicher-Schreibzugriff im Instruktionskörper. Die Loads `[r4]`, `[r4+0x3c]` und `[r4+0x14]` benutzen den lokal geführten Listenwert `r4`, nicht `r6`/den Caller-Pointer.

## Kontrollfluss und Rückgabepfade

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Der Call-Return-Test ist `cmp r0,#0` bei `0x002FCBAC`; ungleich null geht bei `0x002FCBB0` zurück zur Iteration, Gleichheit fällt durch `mov r0,#1` bei `0x002FCBB4` und erreicht den Return bei `0x002FCBB8`. Beim Head-/Listen-Nullpfad normalisiert `subs` plus bedingtes `movne` den Rückgabewert auf `0` oder `1`, bevor der gemeinsame Nulltest folgt. Der Kontrollfluss ist lokal belegt; keine Aussage über den Zweck des gelesenen Feldes oder die Wirkung des Callees wird daraus abgeleitet.

## Toolweg, Tests und Grenzen

REA wurde zuerst mit exaktem Ziel-SHA-256 und Prozeduradresse `0x002FCB48` nach retained Evidence gefragt. Ergebnis: `total_retained_records=0`, `matching_records=0`, `unknown_revisions=0`; es gibt für diese Abfrage keine verwendbare REA Evidence-ID. Danach wurde der erlaubte GNU-Fallback genutzt; kein Ghidra-Import wurde gestartet.

| Prüfung / Aussage | Status | Evidence |
|---|---|---|
| Eingabe SHA-256 und Größe | **PASS** | [`validator_result.txt`](validator_result.txt) |
| Exakter Bereich und 132-Byte-Abdeckung | **PASS** | 33 fortlaufende Zeilen in `instructions.tsv`; exklusives Ende `0x002FCBCC` |
| Instruktionsdekodierung und Rohbytes | **PASS** | GNU objdump 2.44; Bytes separat direkt aus dem ELF gelesen |
| lokale Loads, Stackzugriffe, Call- und Rückgabepfade | **VERIFIZIERT** | Instruktionen ausschließlich im geforderten Body |
| Wirkung von `strcmp@plt` und Bedeutung der lokalen Felder | **OFFEN** | Callee und semantische Interpretation ausgeschlossen |
| `sha256sum -c SHA256SUMS` | **PASS** | Manifest enthält alle Paketdateien außer sich selbst |
| Laufzeit-/Gerätetest | **NOT_RUN** | Offline-Statischanalyse, wie beauftragt |

Alternative Erklärung: Der lokale Kontrollfluss verwendet die geladenen Werte nur nach den sichtbaren Registeroperationen und Bedingungen; Feldbedeutungen oder Listen-/Objektsemantik lassen sich aus diesen Instruktionen allein nicht feststellen. Die Disassemblerannotation `strcmp@plt` wird nur als Callziel-Annotation berichtet, nicht als Vertrag des Callees.

Restunsicherheit: keine retained REA Evidence für diesen Hash/Adressbereich; Register `r2` am direkten Call ist nur als unverändert gegenüber Body-Eingang bekannt; ABI- und Callee-Wirkungen sind nicht untersucht. Das Paket ist Worker-Self-Review; unabhängige Prüfung wird nicht behauptet. Tests des Zielprogramms sind **NOT_RUN**.

## Paketdateien

- `report.md` — Befunde, Datenfluss, Calls, Speicherzugriffe, CFG und Grenzen
- `instructions.tsv` — vollständige Instruktions-/Byte-Tabelle
- `build_evidence.py` — deterministische TSV-Erzeugung aus dem gebundenen ELF
- `validate.py` — Paketvalidator
- `validator_result.txt` — Ergebnis des Validators
- `tool_versions.txt` — Analysewerkzeugversionen
- `disassembly.raw.txt` — begrenzte objdump-Ausgabe
- `SHA256SUMS` — Hashmanifest

SHA-256 der Ausgabedateien stehen in `SHA256SUMS`.
