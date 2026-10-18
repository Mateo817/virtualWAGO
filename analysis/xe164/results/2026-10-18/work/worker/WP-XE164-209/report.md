> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-209 — lokale r5-Save/Restore-Pfade und erster callfreier Scanabschnitt

## Befund

**VERIFIZIERT — lokale Stack-Slot-Mechanik:** Im untersuchten libdal-Ziel
`0x32bc` wird das beim Eintritt vorhandene physische `r5` in der Prolog-Instruktion
`push {r4,r5,r6,lr}` auf dem Stack gesichert. Sowohl der lokale Fehlerreturn
über `0x330c` als auch der erfolgreiche Tail-Pfad über `0x3300`/`0x3304`
stellen dieses Register mit `pop {r4,r5,r6,lr/pc}` wieder her. Der sekundäre
Körper `0x20c8` sichert sein eingehendes physisches `r5` ebenfalls bei Eintritt,
verwendet das Register lokal neu und restauriert es am gemeinsamen Epilog für
Fehler- und Erfolgsreturn. Die `add sp,#32`-Instruktion liegt vor diesem Pop.

**Bedingte Schlussfolgerung — HYPOTHESE:** Falls der IoDrvDal-Getter im
untersuchten Pfad tatsächlich die statisch untersuchte libdal-Objektinstanz
liefert und deren `+0x0c`-Ziel `0x32bc` erreicht, zeigen die lokalen
Save/Restore-Pfade, dass die lokalen libdal-Epiloge den bei `0x32bc`
eingetretenen physischen `r5`-Wert wiederherstellen. Unter dieser Bedingung
führt IoDrvDal nach der erfolgreichen Nullrückgabe ohne weiteren Call `r7=r5`
aus und bindet `r7` bis zum ersten Eintragsload `[r7+4]` positionsgleich an
diesen wiederhergestellten Registerwert. Das ist eine bedingte statische
Register-/Adressbeziehung, keine Runtimebindung.

Die Bedingung setzt unbeschädigte lokale Stack-Slots und den beobachteten
Kontrollfluss voraus. Calls innerhalb von libdal sind opak. Aus den lokalen
Push-/Pop-Instruktionen folgt nicht, dass ein opaker Call Stackpointer,
gesicherte Stackwörter oder sonstige Speicherinhalte unverändert lässt. Ebenso
folgt daraus keine Aussage, dass der Getter zur Laufzeit diese Bibliothek oder
Objektinstanz liefert.

## Pfadmatrix: `r5`-Erhaltung im bedingt gebundenen Ziel

| Bereich / Pfad | Lokale Instruktionsfolge | Beobachteter `r5`-Effekt | Grenze |
|---|---|---|---|
| Eintritt `0x32bc` | `0x32bc push {r4,r5,r6,lr}`; `0x32c0 mov r5,r2` | Eingehendes physisches `r5` wird lokal gesichert, danach wird `r5` neu belegt. | Stackslot-Integrität über opake Calls nicht belegt. |
| Fehlerreturn | `0x32f0 bne 0x3308`; `0x3308 mvn r0,#0`; `0x330c pop {r4,r5,r6,pc}` | Pop lädt das gesicherte `r5` in den Returnzustand. | Gilt lokal bei intaktem Stack/Kontrollfluss. |
| erfolgreicher Tailpfad | `0x32f4..0x32fc` Argumentregister setzen; `0x3300 pop {r4,r5,r6,lr}`; `0x3304 b 0x20c8` | Vor dem Tailbranch wird das beim Eintritt gesicherte `r5` restauriert. | Der Branch selbst transferiert lokal; keine ABI-Annahme über Tailcalls. |
| Sekundäreintritt `0x20c8` | `0x20c8 push {r4,r5,r6,r7,r8,r9,sl,lr}`; `0x20cc sub sp,#32`; `0x20fc mov r5,r0` | Eingehendes physisches `r5` wird gesichert, danach lokal überschrieben. | Opaque Calls können möglicherweise Speicher/Stack beeinflussen; deren Effekte sind OFFEN. |
| Sekundärer Fehlerreturn | `0x20f4 bne 0x2174`; `0x2174 mvn r0,#0`; `0x2178 b 0x216c`; `0x216c add sp,#32`; `0x2170 pop {r4,r5,r6,r7,r8,r9,sl,pc}` | Gemeinsamer Epilog stellt das gesicherte `r5` wieder her. | Stackslot- und Epilogvoraussetzungen wie oben. |
| Sekundärer Erfolgsreturn | `0x2124 beq 0x2168` oder Iterationsende bei `0x2164`; `0x2168 mov r0,#0`; `0x216c add sp,#32`; `0x2170 pop {...,r5,...,pc}` | Derselbe lokale Epilog restauriert `r5`. | Rückgaben opaker Calls und deren Speicherwirkungen bleiben außerhalb. |

Die für diese Matrix verwendeten libdal-Instruktionen stehen in der
hashgebundenen Tabelle `WP-XE164-204/instructions.tsv` (SHA-256 unten im
Manifest). Für `0x32bc` sind alle 21 Instruktionen von `0x32bc` bis `0x330c`
und für `0x20c8` alle 45 Instruktionen von `0x20c8` bis `0x2178` im dortigen
Tabelle/Validator-Scope enthalten. Die lokale Prüfung reproduziert beide
Bereiche zusätzlich mit GNU ARM objdump 2.44.

## Pfadmatrix: IoDrvDal bis vor `strcmp`

| Callerpfad | Instruktionen | Beobachtung / Reichweite |
|---|---|---|
| Argumentübergabe und opaker `+0x0c`-Call | `0x2f08 bl getter`; `0x2f0c mov r2,r8`; `0x2f10 mov r1,r5`; `0x2f14 ldr r3,[r0,#0x0c]`; `0x2f18 mov r0,#10`; `0x2f1c blx r3` | `r5` wird als Wert in `r1` kopiert. Der Call ist opak. Die statische Zielzuordnung `0x32bc` gilt nur unter der akzeptierten E-XE164-230-Bedingung. |
| Erfolgsbedingung und Alias | `0x2f20 subs r6,r0,#0`; `0x2f24 bne 0x32f0`; `0x2f28 mov r7,r5` | Auf dem lokalen Nullrückgabezweig folgt `r7` dem dann aktuellen physischen `r5`. Die libdal-Save/Restore-Kette begründet die bedingte Gleichheit zum am Call vorhandenen `r5`, unter den genannten Stack-/Kontrollflussgrenzen. |
| Boundtest `[0x2f64,0x2f74)` | `0x2f64 ldr r3,[sp,#0x6c]`; `0x2f68 add r3,r5,r3,lsl #3`; `0x2f6c cmp r7,r3`; `0x2f70 bcc 0x2f30` | Exakt vier Caller-Instruktionen laden ein lokales Stackwort, bilden den sichtbaren Endwert, vergleichen und verzweigen unsigned zurück zum ersten Eintragsload. Der Wert und seine Bedeutung bleiben unbenannt. |
| Eintritt in Body und erster Eintragsload | `0x2f2c b 0x2f64`; danach bei erfüllter Branchbedingung `0x2f30 ldr r1,[sp,#0x1c]`; `0x2f34 ldr r0,[r7,#4]` | Auf dem Callerpfad zwischen erfolgreicher `+0x0c`-Rückkehr und `[r7+4]` liegt kein weiterer Call. Die lokale Prüfung bindet nur Registerkopie, Rechenweg und ersten Load; sie wertet Stackwörter oder Eintragsinhalte nicht semantisch aus. |

Die Berichtsspur endet bei `0x2f34`, dem ersten Load `[r7+4]`, unmittelbar vor
der `strcmp`-Instruktion bei `0x2f38`. Weder deren Ausführung/Rückweg noch
spätere `+0x10`-Aufrufe werden hier ausgewertet.

## Beobachtung, Alternative und Restunsicherheit

- **Beobachtung — VERIFIZIERT:** Alle ausgewiesenen `push`/`pop`-Paare,
  `sub/add sp`, lokalen Branches und Return-/Tail-Edges sind in den exakten
  hashgebundenen Fenstern sichtbar. Caller `r5` wird vor `+0x0c` als `r1`
  kopiert; nach erfolgreichem Nullreturn folgt lokal `r7=r5` und der erste
  Scanload ist `[r7+4]`.
- **Alternative:** Liefert der Getter eine andere Objektinstanz/ein anderes
  Ziel oder verändert ein opaker Effekt einen gesicherten Stack-Slot bzw. den
  Rückkehrkontrollfluss, dann belegt die statische libdal-Kette nicht, dass
  IoDrvDal nach dem Call denselben ursprünglichen `r5`-Wert besitzt. Dann ist
  `r7` lediglich eine lokale Kopie des nach dem Call aktuellen `r5`.
- **OFFEN:** Runtime-Ziel und Objektidentität; Register-/Speicher-/Stackeffekte
  der opaken Calls; Integrität und konkrete Belegung der Stack-Slots; Werte der
  Caller-Stackwörter; Inhalt, Typ und Bedeutung der Einträge; tatsächlicher
  Scanverlauf und Runtime-/Hardwareverhalten.
- **Keine Calling Convention/ABI-Annahme:** Die Aussagen stützen sich nur auf
  sichtbare Registerkopien, Stackoperationen, Branches und Loads. Es wird kein
  Callee-Save-Vertrag aus einer Konvention abgeleitet.

## Provenienz, Tooling und Status

- FW31 IoDrvDal 1.0.2: 25,976 Bytes, SHA-256
  `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.
- FW31 libdal 1.0.1: 18,076 Bytes, SHA-256
  `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`.
- Akzeptierte Eingaben: `WP-XE164-204/instructions.tsv` SHA-256
  `b3d69411cd8c08cab9dd925e2a431ba86df5c050239bdcf21a51f03f3478ccba`;
  `WP-XE164-208/manifest.tsv` SHA-256
  `0226093a540fa31b02f4296441e5377e350780b5c097f8df36c605b8c4320255`.
- GNU ARM objdump: GNU Binutils for Debian 2.44. Validator reproduziert
  IoDrvDal `[0x2f08,0x2f38)` und `[0x2f64,0x2f74)` sowie libdal
  `[0x32bc,0x3310)` und `[0x20c8,0x217c)`. Die IoDrvDal-Tabelle für den
  Ersteintritt stoppt vor dem `strcmp`-Aufruf; die vier Instruktionen des
  zweiten Callerspalts gehören zum ausdrücklich freigegebenen Boundtest-Fenster.
- Validator: `python3 validate.py` — PASS; Details in `manifest.tsv`.
- Status: lokale Save/Restore- und Caller-Instruktionspfade **VERIFIZIERT**;
  kombinierte cross-ELF/runtimegebundene Erhaltung **HYPOTHESE**; opake
  Speicher-/Stackeffekte und Runtimebindung **OFFEN**; Runtime/Hardware
  **NOT_RUN**.
- Provenienz: GPT-6 Luna, HIGH. Worker-Self-Check; kein unabhängiger Review.
