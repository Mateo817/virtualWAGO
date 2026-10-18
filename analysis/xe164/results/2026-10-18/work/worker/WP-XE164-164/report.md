> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-164 — Body `[0x00340240, 0x003403a4)`

## Ergebnis

**VERIFIZIERT:** Der statische Body-Fluss belegt: Der Eintrittswert `r3` wird bei `0x00340260` vor dem ersten direkten Call nach `r9` kopiert. Im selben Body wird `r9` später bei `0x00340338` auf null geprüft und — nur auf dem erfolgreichen Pfad durch die vorangehenden Prüfungen und Calls — bei `0x00340350` als Store-Basis verwendet. Der gespeicherte Wert ist der bei `0x00340344` erhaltene Call-Rückgabewert plus eins, danach addiert zu `r4`: `*(entry_r3) = r4 + (R0_return_from_call_0x00340344 + 1)`. Das ist ein bedingter lokaler Store durch den Eingangszeiger, keine Speicherung des Eingangszeigerwerts selbst. Die Wirkung aller aufgerufenen Bodies bleibt außerhalb dieses Befunds.

**VERIFIZIERT:** Die WP-XE164-161-Substitution belegt: Für den dort belegten Call erhält dieser Body `entry_r3 = S_call−48` und `[S]=0`. Auf jedem lokal erreichbaren Abschluss, der den Stackslot bei `0x00340354` prüft, ist wegen `[S]=0` der Pfad über `0x0034039c` gewählt und `r0=0` zurückgegeben. Der andere lokale Rückgabepfad `r0=0` über `0x00340360..0x00340368` ist mit `[S]=0` nicht erreichbar. Frühe Rückgaben `2` und `16` bleiben möglich, abhängig von vorangehenden Vergleichs-/Callrückgaben. Der bedingte Store an `[S_call−48]` ist auf dem Erfolgszweig möglich, wenn `S_call−48 != 0`; der Bericht belegt keinen konkreten numerischen Stackwert und entscheidet daher den Nulltest dieses Ausdrucks nicht.

## Identität und Grenzen

| Gegenstand | Nachweis |
|---|---|
| ELF | `codesys3`, 5,181,396 Bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` |
| WP-XE164-161-Bericht | 13,300 Bytes, SHA-256 `7b8da88127a6e699e6e908a837439d3091de706eeb84db4c25b20ee22480b1a7` |
| Angefragter VMA-Bereich | `[0x00340240,0x003403a4)`, 356 Bytes, 89 A32-Wörter |
| ELF-Format / Mapping | ELF32 little-endian ARM; ausführbarer `PT_LOAD`: `p_offset=0`, `p_vaddr=0x00010000`; damit `file_offset = VMA−0x10000`, Byteintervall `[0x00330240,0x003303a4)` |
| Harte Scope-Grenze | Erstes dekodiertes Wort `0x00340240`; letztes `0x003403a0`; kein Wort ab exklusivem Ende `0x003403a4` dekodiert oder ausgewertet |

Die Instruktionsfolge wurde mit der ARM-GNU-Objdump-Variante ausgelesen; ELF-Header und `PT_LOAD`-Mapping wurden separat mit GNU `readelf` geprüft. Die zum Erzeugen der Instruktionstabelle abgerufenen Disassemblierungsdaten wurden auf das angeforderte Intervall begrenzt. Die folgende Tabelle nennt keine Ziel-Symbole und verwendet keine Namen als Funktionsvertrag.

## Vollständige Instruktions-/Byte-Tabelle

Datei-Bytes stehen in little-endian Datei-Reihenfolge; `objdump_word` ist das dekodierte 32-Bit-Wort. Alle 89 Zeilen decken 356 Bytes lückenlos ab.

| VMA | Datei-Offset | Datei-Bytes | Objdump-Wort | Instruktion |
|---|---|---|---|---|
| `0x00340240` | `0x00330240` | `0d c0 a0 e1` | `e1a0c00d` | `mov ip, sp` |
| `0x00340244` | `0x00330244` | `f0 db 2d e9` | `e92ddbf0` | `push {r4, r5, r6, r7, r8, r9, fp, ip, lr, pc}` |
| `0x00340248` | `0x00330248` | `04 b0 4c e2` | `e24cb004` | `sub fp, ip, #4` |
| `0x0034024c` | `0x0033024c` | `01 c0 a0 e1` | `e1a0c001` | `mov ip, r1` |
| `0x00340250` | `0x00330250` | `00 80 a0 e1` | `e1a08000` | `mov r8, r0` |
| `0x00340254` | `0x00330254` | `5d 10 a0 e3` | `e3a0105d` | `mov r1, #93 @ 0x5d` |
| `0x00340258` | `0x00330258` | `0c 00 a0 e1` | `e1a0000c` | `mov r0, ip` |
| `0x0034025c` | `0x0033025c` | `02 70 a0 e1` | `e1a07002` | `mov r7, r2` |
| `0x00340260` | `0x00330260` | `03 90 a0 e1` | `e1a09003` | `mov r9, r3` |
| `0x00340264` | `0x00330264` | `5e ec f4 eb` | `ebf4ec5e` | `bl 0x0007b3e4` |
| `0x00340268` | `0x00330268` | `00 00 50 e3` | `e3500000` | `cmp r0, #0` |
| `0x0034026c` | `0x0033026c` | `48 00 00 0a` | `0a000048` | `beq 0x00340394` |
| `0x00340270` | `0x00330270` | `01 50 80 e2` | `e2805001` | `add r5, r0, #1` |
| `0x00340274` | `0x00330274` | `5b 10 a0 e3` | `e3a0105b` | `mov r1, #91 @ 0x5b` |
| `0x00340278` | `0x00330278` | `05 00 a0 e1` | `e1a00005` | `mov r0, r5` |
| `0x0034027c` | `0x0033027c` | `58 ec f4 eb` | `ebf4ec58` | `bl 0x0007b3e4` |
| `0x00340280` | `0x00330280` | `00 00 50 e3` | `e3500000` | `cmp r0, #0` |
| `0x00340284` | `0x00330284` | `3e 00 00 0a` | `0a00003e` | `beq 0x00340384` |
| `0x00340288` | `0x00330288` | `00 00 55 e1` | `e1550000` | `cmp r5, r0` |
| `0x0034028c` | `0x0033028c` | `00 60 a0 31` | `31a06000` | `movcc r6, r0` |
| `0x00340290` | `0x00330290` | `14 00 00 2a` | `2a000014` | `bcs 0x003402e8` |
| `0x00340294` | `0x00330294` | `d0 30 d0 e1` | `e1d030d0` | `ldrsb r3, [r0]` |
| `0x00340298` | `0x00330298` | `01 00 40 e2` | `e2400001` | `sub r0, r0, #1` |
| `0x0034029c` | `0x0033029c` | `0a 00 53 e3` | `e353000a` | `cmp r3, #10` |
| `0x003402a0` | `0x003302a0` | `0d 00 53 13` | `1353000d` | `cmpne r3, #13` |
| `0x003402a4` | `0x003302a4` | `03 00 00 0a` | `0a000003` | `beq 0x003402b8` |
| `0x003402a8` | `0x003302a8` | `3b 00 53 e3` | `e353003b` | `cmp r3, #59 @ 0x3b` |
| `0x003402ac` | `0x003302ac` | `2e 00 00 0a` | `0a00002e` | `beq 0x0034036c` |
| `0x003402b0` | `0x003302b0` | `00 00 55 e1` | `e1550000` | `cmp r5, r0` |
| `0x003402b4` | `0x003302b4` | `f6 ff ff 3a` | `3afffff6` | `bcc 0x00340294` |
| `0x003402b8` | `0x003302b8` | `06 00 55 e1` | `e1550006` | `cmp r5, r6` |
| `0x003402bc` | `0x003302bc` | `09 00 00 2a` | `2a000009` | `bcs 0x003402e8` |
| `0x003402c0` | `0x003302c0` | `05 00 a0 e1` | `e1a00005` | `mov r0, r5` |
| `0x003402c4` | `0x003302c4` | `07 10 a0 e1` | `e1a01007` | `mov r1, r7` |
| `0x003402c8` | `0x003302c8` | `db 10 ff eb` | `ebff10db` | `bl 0x0030463c` |
| `0x003402cc` | `0x003302cc` | `00 00 50 e3` | `e3500000` | `cmp r0, #0` |
| `0x003402d0` | `0x003302d0` | `06 00 50 11` | `11500006` | `cmpne r0, r6` |
| `0x003402d4` | `0x003302d4` | `01 50 80 e2` | `e2805001` | `add r5, r0, #1` |
| `0x003402d8` | `0x003302d8` | `00 40 a0 e1` | `e1a04000` | `mov r4, r0` |
| `0x003402dc` | `0x003302dc` | `03 00 00 3a` | `3a000003` | `bcc 0x003402f0` |
| `0x003402e0` | `0x003302e0` | `00 00 50 e3` | `e3500000` | `cmp r0, #0` |
| `0x003402e4` | `0x003302e4` | `f3 ff ff 1a` | `1afffff3` | `bne 0x003402b8` |
| `0x003402e8` | `0x003302e8` | `10 00 a0 e3` | `e3a00010` | `mov r0, #16` |
| `0x003402ec` | `0x003302ec` | `f0 ab 9d e8` | `e89dabf0` | `ldm sp, {r4, r5, r6, r7, r8, r9, fp, sp, pc}` |
| `0x003402f0` | `0x003302f0` | `08 10 a0 e1` | `e1a01008` | `mov r1, r8` |
| `0x003402f4` | `0x003302f4` | `d5 fb ff eb` | `ebfffbd5` | `bl 0x0033f250` |
| `0x003402f8` | `0x003302f8` | `00 00 50 e3` | `e3500000` | `cmp r0, #0` |
| `0x003402fc` | `0x003302fc` | `ed ff ff 1a` | `1affffed` | `bne 0x003402b8` |
| `0x00340300` | `0x00330300` | `08 20 a0 e1` | `e1a02008` | `mov r2, r8` |
| `0x00340304` | `0x00330304` | `04 10 a0 e1` | `e1a01004` | `mov r1, r4` |
| `0x00340308` | `0x00330308` | `07 00 a0 e1` | `e1a00007` | `mov r0, r7` |
| `0x0034030c` | `0x0033030c` | `8d ff ff eb` | `ebffff8d` | `bl 0x00340148` |
| `0x00340310` | `0x00330310` | `00 00 50 e3` | `e3500000` | `cmp r0, #0` |
| `0x00340314` | `0x00330314` | `e7 ff ff 0a` | `0affffe7` | `beq 0x003402b8` |
| `0x00340318` | `0x00330318` | `07 00 a0 e1` | `e1a00007` | `mov r0, r7` |
| `0x0034031c` | `0x0033031c` | `af ee f4 eb` | `ebf4eeaf` | `bl 0x0007bde0` |
| `0x00340320` | `0x00330320` | `07 10 a0 e1` | `e1a01007` | `mov r1, r7` |
| `0x00340324` | `0x00330324` | `00 20 a0 e1` | `e1a02000` | `mov r2, r0` |
| `0x00340328` | `0x00330328` | `04 00 a0 e1` | `e1a00004` | `mov r0, r4` |
| `0x0034032c` | `0x0033032c` | `95 10 ff eb` | `ebff1095` | `bl 0x00304588` |
| `0x00340330` | `0x00330330` | `00 00 50 e3` | `e3500000` | `cmp r0, #0` |
| `0x00340334` | `0x00330334` | `df ff ff 1a` | `1affffdf` | `bne 0x003402b8` |
| `0x00340338` | `0x00330338` | `00 00 59 e3` | `e3590000` | `cmp r9, #0` |
| `0x0034033c` | `0x0033033c` | `04 00 00 0a` | `0a000004` | `beq 0x00340354` |
| `0x00340340` | `0x00330340` | `07 00 a0 e1` | `e1a00007` | `mov r0, r7` |
| `0x00340344` | `0x00330344` | `a5 ee f4 eb` | `ebf4eea5` | `bl 0x0007bde0` |
| `0x00340348` | `0x00330348` | `01 30 80 e2` | `e2803001` | `add r3, r0, #1` |
| `0x0034034c` | `0x0033034c` | `03 30 84 e0` | `e0843003` | `add r3, r4, r3` |
| `0x00340350` | `0x00330350` | `00 30 89 e5` | `e5893000` | `str r3, [r9]` |
| `0x00340354` | `0x00330354` | `04 30 9b e5` | `e59b3004` | `ldr r3, [fp, #4]` |
| `0x00340358` | `0x00330358` | `00 00 53 e3` | `e3530000` | `cmp r3, #0` |
| `0x0034035c` | `0x0033035c` | `0e 00 00 0a` | `0a00000e` | `beq 0x0034039c` |
| `0x00340360` | `0x00330360` | `00 00 a0 e3` | `e3a00000` | `mov r0, #0` |
| `0x00340364` | `0x00330364` | `00 40 83 e5` | `e5834000` | `str r4, [r3]` |
| `0x00340368` | `0x00330368` | `f0 ab 9d e8` | `e89dabf0` | `ldm sp, {r4, r5, r6, r7, r8, r9, fp, sp, pc}` |
| `0x0034036c` | `0x0033036c` | `01 00 86 e2` | `e2860001` | `add r0, r6, #1` |
| `0x00340370` | `0x00330370` | `5b 10 a0 e3` | `e3a0105b` | `mov r1, #91 @ 0x5b` |
| `0x00340374` | `0x00330374` | `1a ec f4 eb` | `ebf4ec1a` | `bl 0x0007b3e4` |
| `0x00340378` | `0x00330378` | `00 60 50 e2` | `e2506000` | `subs r6, r0, #0` |
| `0x0034037c` | `0x0033037c` | `06 00 a0 11` | `11a00006` | `movne r0, r6` |
| `0x00340380` | `0x00330380` | `ca ff ff 1a` | `1affffca` | `bne 0x003402b0` |
| `0x00340384` | `0x00330384` | `0c 60 98 e5` | `e598600c` | `ldr r6, [r8, #12]` |
| `0x00340388` | `0x00330388` | `08 30 98 e5` | `e5983008` | `ldr r3, [r8, #8]` |
| `0x0034038c` | `0x0033038c` | `03 60 86 e0` | `e0866003` | `add r6, r6, r3` |
| `0x00340390` | `0x00330390` | `c8 ff ff ea` | `eaffffc8` | `b 0x003402b8` |
| `0x00340394` | `0x00330394` | `02 00 a0 e3` | `e3a00002` | `mov r0, #2` |
| `0x00340398` | `0x00330398` | `f0 ab 9d e8` | `e89dabf0` | `ldm sp, {r4, r5, r6, r7, r8, r9, fp, sp, pc}` |
| `0x0034039c` | `0x0033039c` | `04 00 9b e5` | `e59b0004` | `ldr r0, [fp, #4]` |
| `0x003403a0` | `0x003303a0` | `f0 ab 9d e8` | `e89dabf0` | `ldm sp, {r4, r5, r6, r7, r8, r9, fp, sp, pc}` |

## Register-, Frame- und Kontrollflussbefund

Sei `S` der SP direkt bei Body-Eintritt. `mov ip,sp` setzt `ip=S`; das Push mit zehn Registern setzt anschließend `sp=S−40`; `fp=ip−4=S−4`. Deshalb adressiert `ldr r3,[fp,#4]` bei `0x00340354` genau `[S]`. Der Body reserviert nach dem Push keinen zusätzlichen Frame-Slot. Die Eingänge `r0/r1/r2/r3` werden bei `0x00340250/24c/25c/260` vor dem ersten `bl` in `r8/ip/r7/r9` kopiert. Somit überstehen die später verwendeten Eingangskopien den ersten Call unter der A32/EABI-Konvention für die im Body gesicherten callee-saved Register; nach jedem `bl` werden `r0-r3` als clobbered behandelt und nur explizit kopierte Rückgabewerte weiterverfolgt.

CFG (Kanten durch lokale Bedingung; Calls werden als opaque, eventuell zurückkehrende Call-Knoten behandelt):

[Code-/Listingblock bleibt im privaten Nachweispaket.]

### Direkte lokale Speicherwrites

| Adresse | Operation | lokaler Effekt / Bedingung |
|---:|---|---|
| `0x00340244` | `push {r4,r5,r6,r7,r8,r9,fp,ip,lr,pc}` | Sichert zehn Register im Intervall `[S−40,S)`; kein durch `r3` gebildeter Schreibzugriff. |
| `0x00340350` | `str r3,[r9]` | Ein 32-Bit-Store an die Adresse in `r9`; ausgeführt nur nach Eintritt in Block `338`, wenn `r9 != 0`. Gespeicherter Wert ist `r4+(R0_return_0x00340344+1)`. Vorher wird `r0=r7` gesetzt und der Call bei `344` ausgeführt. |
| `0x00340364` | `str r4,[r3]` | Ein 32-Bit-Store an die zuvor bei `354` geladene Adresse `[S]`; nur wenn der geladene Wert nicht null ist. Für die WP161-Substitution `[S]=0` unerreichbar. |

Kein anderer eingeschlossener `str`/Mehrfachregister-Store schreibt über einen Body-Eingang. Der Push ist ein lokaler Sicherungsstore, nicht die Ausgabe durch `input r3`. Externe Call-Memoryeffekte werden nicht beurteilt.

### Callsites: Argumentregister und lokaler Rückgabeverbrauch

`?` bezeichnet Register, deren Wert am Call nicht aus dem vorherigen lokalen Code bestimmt werden kann, insbesondere nach Caller-clobber. Für R4–R11 wird die EABI-preserved-Konvention als notwendige lokale Datenflussannahme verwendet. Es werden keine Callee-Effekte behauptet.

| Callsite → Zieladresse | R0 | R1 | R2 | R3 | lokale Verwendung von R0 nach Rückkehr |
|---|---|---|---|---|---|
| `264 → 7b3e4` | Eingang `r1` | `93` | Eingang `r2` | Eingang `r3` | bei `268` getestet; Null → `394`; sonst `r5=R0+1`. `r2/r3` waren vorher bereits nach `r7/r9` kopiert. |
| `27c → 7b3e4` | `r5` | `91` | ? | ? | Null → `384`; sonst Vergleich mit `r5` und möglicher Werttransport nach `r6`. |
| `2c8 → 30463c` | `r5` | `r7` | ? | ? | Auf Null und gegen `r6` verglichen; als `r4` gespeichert und mit Flags für Kante zu `2f0` ausgewertet. |
| `2f4 → 33f250` | `r4` | `r8` | ? | ? | Nullprüfung; nicht-null → Rückkante `2b8`, null → `300`. |
| `30c → 340148` | `r7` | `r4` | `r8` | ? | Null → Rückkante `2b8`; nicht-null → `318`. |
| `31c → 7bde0` | `r7` | ? | ? | ? | Rückgabe wird bei `324` nach `r2` kopiert und als drittes Registerargument des Calls `32c` verwendet. |
| `32c → 304588` | `r4` | `r7` | Returnwert von `31c` | ? | Nicht-null → Rückkante `2b8`; Null → `338`. |
| `344 → 7bde0` | `r7` | ? | ? | ? | Rückgabe wird bei `348` um eins erhöht und bei `34c` zu `r4` addiert; Resultat wird bei `350` gespeichert. |
| `374 → 7b3e4` | `r6+1` | `91` | ? | ? | Bei `378` mit Null verglichen; nicht-null → R0=`r6`, Rückkante `2b0`; Null → `384`. |

### Konkrete Substitution aus WP-XE164-161

WP161 belegt für den direkten Call bei dessen `0x003419c8`: das Callee-Eingangstriple ist `r0=R4`, `r1=[caller_B−52]`, `r2=caller_input_r1`, `r3=caller_input_r2=S_call−48`; das Stackargument bei Call-Eintritt ist `[S]=0`. Für genau diese Substitution gilt hier:

| Body-Fakt | Substitution / Folge |
|---|---|
| Sicherung vor erstem Call | `r9 := entry_r3 := S_call−48` bei `0x00340260`; anders als `r0-r3` bleibt die lokale Kopie in `r9` über spätere Calls unter der EABI-Konvention verfügbar. |
| Nulltest des Ausgabezeigers | `0x00340338` testet `r9`; Store bei `350` nur, wenn der erfolgreiche CFG-Pfad bis `338` erreicht ist und `S_call−48 != 0`. |
| Ausgabeadresse/-wert | Unter obiger Store-Bedingung: Adresse `S_call−48`; Wert `r4+(R0_return_0x00340344+1)`. Der Wert des Call-Rückgaberegisters wird nicht semantisch interpretiert. |
| Stackausgabe | `0x00340354` lädt `[fp+4]=[S]=0`; deshalb Branch zu `39c`, nicht zum Store bei `364`. |
| lokaler Rückgabewert nach `354` | `0x0034039c` lädt `[S]` in `r0`, somit `r0=0`; `0x003403a0` kehrt zurück. |
| frühe lokale Rückgaben | Vor Erreichen von `354` können die lokalen Fehlerpfade `r0=2` (`394`) oder `r0=16` (`2e8`) enden; ob Bedingungen dafür eintreten, hängt unter anderem von opaken Call-Rückgaben ab. |

Somit beweist dieser Body bedingten Store durch den substituierten Wert `S_call−48`, nicht aber einen Store auf jedem Aufruf. Auf dem späteren Erfolgsabschluss ist `r0=0` durch `[S]=0` lokal zwingend. Ob der erfolgreiche Zweig mit den tatsächlichen Eingabedaten erreicht wird, bleibt offen. Falls `S_call−48=0`, wird der Store durch `350` übersprungen; ohne konkrete Runtime-Adresse ist dieser Vergleich nicht weiter entscheidbar.

## REA, Fallback, Status und Grenzen

REA wurde zuerst per `get_evidence_bundle(detail=summary)` für den exakten SHA-256 und Procedure-Adresse `0x00340240` abgefragt. Antwort: `total_retained_records=0`, `matching_records=0`, `unknown_revisions=0`; daher existiert keine passende retained exact-hash/address Evidence-ID. Der bekannte hängende Ghidra-Import wurde nicht wiederholt und keine neue Ghidra-Analyse gestartet.

Begrenzter Fallback: `arm-linux-gnueabihf-objdump -D -m arm --start-address=0x00340240 --stop-address=0x003403a4 <ELF>`; GNU Binutils 2.44. GNU `readelf` 2.44 bestimmte ELF-Header und LOAD-Abbildung. Der host-native `objdump` hatte keine ARM-Unterstützung; deshalb wurde der installierte ARM-Cross-Objdump verwendet. REA-Server 6.5.0 wurde nur für Session-/Evidence-Status abgefragt. Es gab keine Laufzeit-, Hardware-, Geräte-, Netzwerk- oder VM-Aktion.

| Aussage / Prüfung | Status | Begründung |
|---|---|---|
| ELF-Eingabegröße und SHA-256 | VERIFIZIERT | stimmen mit den Vorgaben überein |
| REA retained exact hash/address | VERIFIZIERT | exakte Abfrage ergab null passende Datensätze; kein frischer Providerimport |
| VMA-/Dateioffset-Abbildung | VERIFIZIERT | ELF-Header und erster ausführbarer `PT_LOAD` aus `readelf`; Offset `VMA−0x10000` |
| Instruktionszahl und Abdeckung | VERIFIZIERT | 89 lückenlose 4-Byte-Wörter = 356 Bytes; letzter Start `0x003403a0` |
| Dekodierte Wörter vs. ELF-Bytes | VERIFIZIERT | validatorischer Bytevergleich für exakt 356 Quellbytes |
| lokaler Fluss des Eingangswerts `r3` | VERIFIZIERT | `r3→r9` vor erstem Call; Nulltest und bedingter Store durch `r9` |
| konkrete Rückgabe bei `[S]=0` nach Stacktest | VERIFIZIERT | `ldr r0,[fp,#4]` lädt 0 und Epilog kehrt mit `r0=0` zurück |
| konkrete Erreichbarkeit erfolgreicher Ausgabe | OFFEN | Daten und opake Callee-Rückgaben bestimmen, ob die Kette bis `338` gelangt; kein Runtimebeleg |
| Nullheit von `S_call−48` als konkrete Adresse | OFFEN | nur symbolischer Callerwert vorgegeben, keine konkrete Runtime-Stackadresse |
| Effekte der direkten Callees / mögliche Call-Memorywrites | OFFEN | Callee-Bodies ausdrücklich außerhalb des Scopes |
| `validate.sh` | PASS | Identität, Größe, Mapping, 89 contiguous Instruktionen, Bytes geprüft |
| `sha256sum -c SHA256SUMS` | PASS | Manifestprüfung nach Erstellung |

**Alternative und Restunsicherheit:** Ein nicht-null `S_call−48` erlaubt auf dem Erfolgszweig einen einzelnen 32-Bit-Store an genau diese Adresse; ein nuller Wert unterdrückt ihn. Die statische Eingabe substituiert keine konkrete Stackadresse. Rückgabewerte `2`/`16` und `0` sind lokale Register-/Epilogpfade, keine beobachteten Ausführungen. Callee-Wirkung, tatsächliche Inputbytes, Aliasfolgen, Laufzeit- und Hardwareverhalten bleiben **OFFEN**.

## Erzeugte Worker-Dateien

| Datei | Inhalt | SHA-256 |
|---|---|---|
| `report.md` | Befund, vollständige Tabelle, CFG, Stores, Callsite-Flüsse und Substitution | im `SHA256SUMS`-Manifest |
| `instructions.tsv` | maschinenlesbare vollständige Instruktions-/Byte-Tabelle | `c8b40120be4fd53237089e26c27486f251a05fdde0d80ef3a439b44beaa4918b` |
| `readelf.header.txt` | ELF-Headerausgabe | `5fa767de739644f02a32239ef7382422842438eed248cc4d8bb7adee4f80657b` |
| `readelf.program-headers.txt` | LOAD-Abbildungsausgabe | `065848dd98815be3b05560d350f751cd4df5bd64745166da9bfa29403c384472` |
| `validate.sh` | reproduzierbarer lokaler Validator | `2f07fe7c16fc9cb948edadf5e4093f4c651eb2de0befd6682cd34e88b0bfb856` |
| `SHA256SUMS` | SHA-256 aller obigen Dateien | Manifest enthält Hash von `report.md`; sein eigener Hash wird separat an Parent gemeldet |

Self-Review: eigene Dekodier-/Datenflussprüfung; kein unabhängiger, Runtime- oder Hardware-Review behauptet.
