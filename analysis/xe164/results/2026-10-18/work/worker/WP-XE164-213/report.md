> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-213 — Store/Scanwort-Alias

## Ergebnis

**Status: OFFEN.** Caller 1 übergibt im zugelassenen Equality-Zweig `r0 = 0x163d8`. Caller 2 bildet denselben Ausdruck `r0 = 0x163d8`, sofern `r7` auf dem außerhalb des Codefensters liegenden Schleifenpfad seinen bei `0x379c` gesetzten Wert behält. Der vollständige Loaderkörper berechnet zunächst `r4 = r0 + r11*0x63c`; den Scan-Zeiger `r7` setzt er aus dem dann aktuellen Wert von `r5`, dessen sichtbare frühere Definition `sp+0x70` lautet. Das genügt weder zum Beweis tatsächlicher Überlappung noch zur Disjunktheit von Storeadresse `[r4+0x618]` und Scanwortadresse `[r7]`. Für den Vergleich fehlen eine gebundene Relation zwischen Laufzeit-`sp` und dem aus Literalen berechneten Basis-Ausdruck sowie Belege für Registerwerte über opake Calls hinweg. Kein Laufzeitverhalten wurde beobachtet.

## Identität, Methode und Koordinaten

- Eingabe `FW31-IODRVDAL-1.0.2`: frisch gemessen 25,976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.
- REA 6.5.0, Ghidra 12.1.4, GNU ARM objdump / GNU Binutils 2.44. REA öffnete das exakte ELF. REA-Evidence-Bundle: neun Datensätze, null Unknowns.
- REA/Ghidra Bildbasis `0x10000`; die folgenden Ranges sind ELF-VA und hier identische Datei-Offsets. In Ghidra-Adressen ist jeweils `0x10000` zu addieren. Laufzeitadresse/Load-Bias ist nicht bestimmt.
- REA-Prozedurassembly deckte den Loaderkörper vollständig ab (`0x12ddc..0x1331b` Ghidra, inkl. Ghidra-Offset `+0x10000`). Der auf ELF-VA `0x1331c` normalisierte Anfangsbereich der ersten Callergrenze ist Literalpool, nicht Instruktionscode.
- REA-Caller-Inventar meldete für den Loader keine aufgelösten Caller und ausdrücklich eine fehlende Caller-Referenz. REA-Instruktionsinspektion an der ersten Callergrenze bestätigte Daten bei Ghidra `0x1331c`; somit war das vollständige Auslesen der Callerfragmente eine konkrete REA-Abdeckungslücke. Einmaliger benannter Fallback: `arm-linux-gnueabihf-objdump` 2.44, offline, auf ausschließlich beauftragten Ranges. Der generische `objdump`-Fallback wurde einmal versucht, scheiterte mit `can't disassemble for architecture UNKNOWN`; nicht wiederholt.
- Kanonischer Ausgangsindex wurde nicht verändert: 314,535 Bytes, SHA-256 `12258b123467d67f4c90c0781ea3ddc112734cc831e1a1b678222ccff0fa81d1`.

## Beobachtete Definitionen und Speicherzugriffe

Rohwörter sind die GNU ARM objdump 2.44 Maschinenwörter. REA/Ghidra stützt den Loaderkörper; die Caller- und Literaldecode stammt aus dem benannten objdump-Fallback. Vollständige relevante Tabelle liegt in [provenance.tsv](provenance.tsv).

| ELF-VA / Datei | Ghidra-Adresse | Rohwort | Instruktion / beobachteter Zusammenhang |
|---|---:|---:|---|
| `0x2ddc` | `0x12ddc` | `e92d4ff0` | `push {r4,r5,r6,r7,r8,r9,sl,fp,lr}` |
| `0x2de0` | `0x12de0` | `e1a0b002` | `mov fp,r2`; initial definition of the loader index register in the visible entry sequence |
| `0x30b8` | `0x130b8` | `e300363c` | `movw r3,#0x63c` |
| `0x30bc` | `0x130bc` | `e28d5070` | `add r5,sp,#0x70` — SP-relativer Ausdruck |
| `0x30c0` | `0x130c0` | `e0240b93` | `mla r4,r3,fp,r0`; damit lokal `r4 = incoming-r0 + index*0x63c` (Indexregister im Fallback als `fp`, derselbe Ghidra-Disassembler-Registername wie `r11`) |
| `0x31a8` | `0x131a8` | `e12fff3a` | `blx sl`; opaque call after the `r4`/`r5` setup |
| `0x31e4` | `0x131e4` | `e12fff3c` | `blx ip`; opaque call |
| `0x3220` | `0x13220` | `e12fff3c` | `blx ip`; opaque call |
| `0x3258` | `0x13258` | `e12fff3c` | `blx ip`; opaque call |
| `0x3298` | `0x13298` | `e12fff3c` | `blx ip`; opaque call |
| `0x32c0` | `0x132c0` | `e12fff3c` | `blx ip`; opaque call |
| `0x32e4` | `0x132e4` | `e12fff37` | `blx r7`; opaque call immediately before branch back to `0x2f08` on zero combined result |
| `0x32ec` | `0x132ec` | `0affff05` | `beq 0x2f08`, returns to scan setup on the observed zero-result branch |
| `0x2f08` | `0x12f08` | `ebfff6b1` | `bl 0x9d4`; opaque getter call before scan-loop pointer setup |
| `0x2f1c` | `0x12f1c` | `e12fff33` | `blx r3`; opaque call before `mov r7,r5` at `0x2f28` |
| `0x2f28` | `0x12f28` | `e1a07005` | `mov r7,r5` auf dem Null-Ergebniszweig des vorherigen indirekten Aufrufs |
| `0x2f30` | `0x12f30` | `e59d101c` | `ldr r1,[sp,#0x1c]` |
| `0x2f34` | `0x12f34` | `e5970004` | `ldr r0,[r7,#4]` |
| `0x2f38` | `0x12f38` | `ebfff6b1` | `bl 0xa04` (`strcmp@plt`) |
| `0x2f3c` | `0x12f3c` | `e3500000` | `cmp r0,#0` |
| `0x2f44` | `0x12f44` | `e5973000` | `ldr r3,[r7]` |
| `0x2f48` | `0x12f48` | `e5843618` | `str r3,[r4,#0x618]` — Store an der untersuchten Basis |
| `0x2f4c` | `0x12f4c` | `ebfff6a0` | `bl 0x9d4` (`adi_GetApplicationInterface@plt`) zwischen Store und erneutem Wortload |
| `0x2f50` | `0x12f50` | `e5903010` | `ldr r3,[r0,#0x10]` |
| `0x2f54` | `0x12f54` | `e5970000` | `ldr r0,[r7]` — anschließend aus derselben hier angezeigten Zeigerbasis gelesenes Wort |
| `0x2f58` | `0x12f58` | `e12fff33` | `blx r3` |
| `0x2f60` | `0x12f60` | `e2877008` | `add r7,r7,#8` nach dem Zugriffspfad |
| `0x2f64` | `0x12f64` | `e59d306c` | `ldr r3,[sp,#0x6c]` |
| `0x2f68` | `0x12f68` | `e0853183` | `add r3,r5,r3,lsl #3`; Schleifenendadresse aus `r5` und stackgeladenem Zähler |
| `0x2f6c` | `0x12f6c` | `e1570003` | `cmp r7,r3` |
| `0x2f70` | `0x12f70` | `3affffee` | `bcc 0x2f30`, Schleifenrückkante |
| `0x2f7c` | `0x12f7c` | `e59f33dc` | nach der Scan-Schleife weiterer Literalload; gehört nicht zur Aliasgleichung |
| `0x33b4` | `0x133b4` | `e59f2030` | erster Caller: `ldr r2,[pc,#0x30]`, Literaladresse `0x33ec` |
| `0x33b8` | `0x133b8` | `e1a03001` | `mov r3,r1` |
| `0x33bc` | `0x133bc` | `e1500002` | `cmp r0,r2` |
| `0x33c0` | `0x133c0` | `1a000007` | `bne 0x33e4`; tail-transfer-Pfad nur bei equality |
| `0x33c4` | `0x133c4` | `e59fc024` | `ldr ip,[pc,#0x24]`, Literaladresse `0x33f0` |
| `0x33c8` | `0x133c8` | `e08fc00c` | `add ip,pc,ip`; ELF PC hier `0x33d0` |
| `0x33cc` | `0x133cc` | `e59c2010` | `ldr r2,[ip,#0x10]` — Zugriff über den berechneten `ip`-Ausdruck |
| `0x33d0` | `0x133d0` | `e2821001` | `add r1,r2,#1` |
| `0x33d4` | `0x133d4` | `e58c1010` | `str r1,[ip,#0x10]` — Zugriff über den berechneten `ip`-Ausdruck |
| `0x33d8` | `0x133d8` | `e1a01000` | `mov r1,r0` |
| `0x33dc` | `0x133dc` | `e28c0014` | `add r0,ip,#20` |
| `0x33e0` | `0x133e0` | `eafffe7d` | `b 0x2ddc`, direkter Tail-Transfer zum Loader |
| `0x37bc` | `0x137bc` | `ebfffd86` | zweiter Caller: direkter `bl 0x2ddc` |
| `0x3790` | `0x13790` | `e59f5bc0` | `ldr r5,[pc,#0xbc0]`, Literaladresse `0x4358` |
| `0x3794` | `0x13794` | `e59f6bc0` | `ldr r6,[pc,#0xbc0]`, Literaladresse `0x435c` |
| `0x3798` | `0x13798` | `e08f5005` | `add r5,pc,r5`; ELF PC `0x37a0` |
| `0x379c` | `0x1379c` | `e2857014` | `add r7,r5,#20` |
| `0x37a0` | `0x137a0` | `ea000011` | `b 0x37ec`; Pfad zur Call-Iteration verlässt den zugelassenen Codebereich |
| `0x374c` | `0x1374c` | `e59f2bf8` | `ldr r2,[pc,#0xbf8]`, Literaladresse `0x434c` |
| `0x3750` | `0x13750` | `e59f1bf8` | `ldr r1,[pc,#0xbf8]`, Literaladresse `0x4350` |
| `0x3754` | `0x13754` | `e08f2002` | `add r2,pc,r2`; ELF-PC `0x375c`, ergibt Ausdruck `0x16090` |
| `0x3758` | `0x13758` | `e59f0bf4` | `ldr r0,[pc,#0xbf4]`, Literaladresse `0x4354` |
| `0x3760` | `0x13760` | `e08f1001` | `add r1,pc,r1`; ELF-PC `0x3768`, ergibt Ausdruck `0x5054` |
| `0x3764` | `0x13764` | `e5924098` | `ldr r4,[r2,#0x98]` |
| `0x3768` | `0x13768` | `e08f0000` | `add r0,pc,r0`; ELF-PC `0x3770`, ergibt Ausdruck `0x5038` |
| `0x3770` | `0x13770` | `e12fff34` | `blx r4`; opaque call before the later `r0` definition at `0x37ac` |
| `0x3774` | `0x13774` | `e2504000` | `subs r4,r0,#0` |
| `0x3778` | `0x13778` | `0a000001` | `beq 0x3784`; success lane to later literal setup |
| `0x3784` | `0x13784` | `e59d3060` | `ldr r3,[sp,#0x60]` |
| `0x3788` | `0x13788` | `e353000a` | `cmp r3,#10` |
| `0x378c` | `0x1378c` | `8afffffa` | `bhi 0x377c`; count-like value greater than ten leaves lane |
| `0x3790` | `0x13790` | `e59f5bc0` | `ldr r5,[pc,#0xbc0]`, Literaladresse `0x4358` |
| `0x37a4` | `0x137a4` | `e5952010` | loop-body load `[r5,#0x10]` |
| `0x37a8` | `0x137a8` | `e1a01006` | `mov r1,r6` |
| `0x37ac` | `0x137ac` | `e1a00007` | `mov r0,r7` — lokale `r0`-Definition für den direkten Call |
| `0x37b0` | `0x137b0` | `e2823001` | `add r3,r2,#1` |
| `0x37b4` | `0x137b4` | `e5853010` | `str r3,[r5,#0x10]` |
| `0x37b8` | `0x137b8` | `e28d305c` | `add r3,sp,#0x5c` |
| `0x37bc` | `0x137bc` | `ebfffd86` | `bl 0x2ddc`; `r0` ist der an `0x37ac` gelesene Registerwert |

Zugelassene Literalwörter (rohe Bytes in Little-Endian-Reihenfolge): `0x33ec=01 20 06 10` (`0x10062001`), `0x33f0=f4 2f 01 00` (`0x00012ff4`), `0x434c=34 29 01 00` (`0x00012934`), `0x4350=ec 18 00 00` (`0x000018ec`), `0x4354=c8 18 00 00` (`0x000018c8`), `0x4358=24 2c 01 00` (`0x00012c24`), `0x435c=01 20 06 10` (`0x10062001`). PC-relative Add-Ausdrücke ergeben für den jeweils zugelassenen Callerzweig bei ELF-Koordinaten denselben beobachteten Ausdruck `0x163c4`; Addition `+0x14` ergibt `0x163d8`. Diese sind ELF-Adressausdrücke der Instruktionsarithmetik, keine belegten Laufzeitadressen; Load-Bias bleibt unbekannt.

## Getrennte Pfadurteile

### Caller 1 — bedingter Tail-Transfer `0x33e0`

**Beobachtung:** Der Caller-Pfad testet bei `0x33bc` den aktuellen `r0` gegen das direkt geladene Wort `0x10062001`; nur der Equality-Zweig fällt durch `0x33c0` hindurch. Der Literalwert bei `0x33f0` ist `0x12ff4`; `0x33c8` addiert ihn zu ELF-PC `0x33d0`, `0x33dc` addiert `0x14` und `0x33e0` springt zum Loader. Somit ist das lokal übergebene Loader-`r0` in diesem Pfad der Ausdruck `0x163d8`. Im Loader berechnet `0x30bc` `r5=sp+0x70`, und `0x2f28` kopiert den dann aktuellen Wert von `r5` auf `r7`; Store und spätere Lesung sind bei `0x2f48`/`0x2f54`.

**Schlussfolgerung:** Vor dem Scanpfad berechnet `0x30c0` im direkten Weg `r4 = 0x163d8 + r11*0x63c`, und `0x2f28` kopiert syntaktisch den aktuellen Wert von `r5` nach `r7`. Zwischen diesen Definitionen und den fraglichen Zugriffen stehen mehrere direkte oder indirekte Aufrufe (`0x31a8`, `0x31e4`, `0x3220`, `0x3258`, `0x3298`, `0x32c0`, `0x32e4`, `0x2f08`, `0x2f1c` und im Schleifenpfad `0x2f38`/`0x2f4c`). Ohne Callee-Effekte oder Calling-Convention dürfen aktuelle `r4`, `r5`/`r7` daraus nicht über die Calls hinweg abgeleitet werden. Selbst wenn die Werte erhalten blieben, fehlt die gebundene Laufzeitrelation zwischen `sp` und `0x163d8` (sowie tatsächlicher Index-/Adressabbildungswert). Eine statische Alias- oder Disjointness-Aussage folgt nicht. Urteil für diesen Caller: **OFFEN**.

**Pfadbedingung und Alternativerklärung:** Dieser Tail-Transfer ist nur im Gleichheitszweig statisch zugelassen; der Ungleichheitszweig verlässt das Fenster bei `0x33e4`. Gleichheit des Vergleichswerts könnte als Zielprofilfilter dienen, ändert aber keine Adresse. Selbst wenn die beiden Basisausdrücke im konkreten Prozess nie kollidieren, ist das durch die abgegrenzte statische Evidenz nicht belegt. Umgekehrt ist ein Überlappen bei passendem Stack-/Load-Bias nicht ausgeschlossen.

### Caller 2 — direkter Call `0x37bc`

**Beobachtung:** Vor den Literalen `0x4358=0x12c24` und `0x435c=0x10062001` lädt der Caller die ebenfalls freigegebenen Wörter `0x434c/0x4350/0x4354` und bildet bei `0x3754/0x3760/0x3768` die Ausdrücke `0x16390/0x5054/0x5038`. Ein opaker indirekter Call bei `0x3770` folgt; sein Ergebnis steuert einen bedingten Pfad, aber sein Ziel wird hier nicht analysiert. Später werden `0x4358/0x435c` bei `0x3790/0x3794` geladen. Der PC-relative Add bei `0x3798` verwendet ELF-PC `0x37a0`, woraus bei unmodifiziertem `r5` der Ausdruck `0x163c4` entsteht; `0x379c` bildet `r7 = r5+0x14`. Im sichtbaren Call-Block setzt `0x37ac` `r0=r7`, nach einem Registerargument bei `0x37a8` und vor `0x37bc`. Kein Call zwischen dieser lokalen Definition und `0x37bc` schreibt sichtbar `r0`. Das Loader-`r4` wird wie im ersten Pfad bei `0x30c0` aus dem ankommenden `r0` plus `r11*0x63c` berechnet; `r7` wird bei `0x2f28` aus dem dann aktuellen `r5` gesetzt.

**Schlussfolgerung:** Auf einem Callpfad mit unmodifiziertem `r7` ab `0x379c` erhält Caller 2 dieselbe Loader-`r0`-Basis `0x163d8`. Die Callergrenze enthält bei `0x37a0` aber einen Sprung zu `0x37ec`, außerhalb des beauftragten Codefensters; deshalb belegt der Auftrag nicht alle möglichen Definitionen auf jeder Rückkehr zur Call-Iteration. Zusätzlich gilt im Loader auch hier: aktuelle `r4`-/`r7`-Werte über die opaken Calls hinweg sind ungebunden und die Relation des Loader-Stacks zur Basis fehlt. Urteil für diesen Caller: **OFFEN**.

**Pfadbedingung und Alternativerklärung:** Wenn die außerhalb des Fensters liegende Schleifenfortsetzung `r7` verändern könnte, wäre selbst der genaue Caller-`r0`-Ausdruck beim Call bedingt. Er kann ebenso erhalten bleiben; dies darf ohne die ausgeschlossene Nachbarcodeanalyse nicht entschieden werden. Auch unter der Erhaltungsannahme ist keine Disjunktheit zwischen Loader-SP-Ausdruck und PC-relativ berechneter Storeadresse bewiesen.

## Unbekanntes und Restunsicherheit

Nicht gebunden sind Laufzeit-`sp`, Laufzeit-Load-Bias/Memory-Mappings, die Relation zwischen Loader-Aufrufbasis und SP, der Wert von `r11` an der Loaderstelle (keine Index-/Semantikaussage daraus abgeleitet), die Effekte aller opaken indirekten Aufrufe im Loader auf Register-/Speicherwerte, sowie der im zweiten Caller außerhalb des Bereichs liegende Rückkehr-/Schleifenpfad. Insbesondere beweist ein PC-relativer Basis-Ausdruck gegenüber einem SP-relativen Ausdruck keine physische Trennung. Der Store liegt textlich vor dem Call `0x2f4c` und dem späteren Wortload `0x2f54`; ob ein opaker Call den Speicher oder Register beeinflusst, wird nicht angenommen. Die beobachteten Instruktionen legen nur Zugriffsadressen über die jeweiligen aktuellen Registerwerte fest.

**Alternativerklärung:** In einer konkreten Laufzeitumgebung können der SP-relative und der PC-relative Ausdruck auf disjunkte Bereiche zeigen; diese Trennung ist hier nicht als Evidenz vorhanden. Auch ein konkreter SP-Wert könnte die Storeadresse treffen. Beides bleibt Hypothese, nicht Resultat dieser Analyse.

## Validator und Checks

`validate.py` verifiziert Eingabegröße/SHA-256, GNU ARM objdump-Version, beauftragte disassembly-Grenzen, zitierte Instruktionsrohbytes sowie alle sieben freigegebenen Literalwörter und die PC-Berechnungskonstanten. Ausführung: `python3 validate.py`. Erwarteter Status: `PASS`. Der Validator testet keine Laufzeitsemantik und ist kein unabhängiger Review.

| Check | Status | Umfang |
|---|---|---|
| Eingabeidentität | PASS | Bytegröße und SHA-256 exakt |
| REA-Analyse | PASS | Exaktes ELF geöffnet; Loaderassembly vollständig für analysierte Prozedur; Caller-Inventarlimit im Bundle festgehalten |
| GNU ARM objdump | PASS | Binutils 2.44; drei zugelassene Codefenster und ausschließlich sieben zugelassene 4-Byte-Literalwörter |
| Aliasurteil | OFFEN | Beide Caller separat beurteilt; keine unbelegte Stack-/Laufzeitannahme |
| Laufzeit/Hardware | NOT_RUN | Außerhalb dieses Offline-Auftrags |

## Erzeugte Dateien

`SHA256SUMS` enthält Hashes für diese Reportdatei, `provenance.tsv`, `validate.py`, das REA-Evidence-Bundle und die unveränderte Zuweisungsdatei. Die Manifestdatei führt ihren eigenen Hash nicht, da dies einen selbstreferenziellen Hash erfordern würde. Das Evidence-Bundle enthält die REA-Sitzungsdatensätze; GNU-objdump-Fallbackzeilen sind zusätzlich durch den deterministischen Worker-Validator und die Instruktionstabelle gebunden.
