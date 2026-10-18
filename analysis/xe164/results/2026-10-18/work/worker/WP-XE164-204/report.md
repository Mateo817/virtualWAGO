> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-204 — positionsgebundener Vertrag für `+0x0c`

## Ergebnis und Reichweite

**VERIFIZIERT (statisch, bedingt gebunden):** IoDrvDal ruft an `0x2f08` den importierten Getter auf, lädt danach bei `0x2f14` das 32-Bit-Wort an Rückgabe-`r0 + 0x0c` und ruft dieses Ziel bei `0x2f1c` mit `r0=10`, `r1=r5`, `r2=r8` auf. Im getrennt analysierten libdal-ELF enthält der REL-Slot an Objektbasis `0x14154 + 0x0c` den `R_ARM_RELATIVE`-Addend und statischen ELF-Zielwert `0x32bc` (E-XE164-229). **Nur falls** der vom IoDrvDal-Getter gelieferte Gegenstand zur selben libdal-Objektinstanz gehört, führt dieser indirekte Aufruf zum hier analysierten Ziel `0x32bc`. E-XE164-217/229 belegen keine Laufzeitbindung oder Objektidentität.

Für diesen bedingten Fall gilt folgender lokaler Positionsvertrag, ohne Slot-, API- oder Struktursemantik:

| Eingang am Aufruf `0x32bc` | Verwendung im Zielkörper |
|---|---|
| `r0=10` | In `0x32c8` gesichert; nach lokalem Gate als `r0=10` an den Sekundärkörper `0x20c8` weitergegeben. Dort Schleifenobergrenze `i < 10` (unsigned); sie begrenzt die Anzahl der Element-Schreibpaare auf höchstens zehn. |
| `r1=r5` des IoDrvDal-Aufrufers | In `0x32c4` gesichert und nach erfolgreichem ersten Gate als Basis an den Sekundärkörper übergeben. Muss dort ungleich null sein. Zieldaten werden positionsgebunden ab dieser Adresse geschrieben. |
| `r2=r8` des IoDrvDal-Aufrufers | In `0x32c0` gesichert und nach erfolgreichem ersten Gate als Zeiger an den Sekundärkörper übergeben. Muss dort ungleich null sein. Ein 32-Bit-Rückgabewort des direkten Aufrufs bei `0x2118` wird an genau dieser Adresse geschrieben. |

`r5` und `r8` bezeichnen hier Registerwerte am IoDrvDal-Aufrufpunkt; ihre Herkunft oder Bedeutung ist **OFFEN**. Die Eingangsregisterbezeichnungen werden nicht als Typen oder Prototyp behauptet.

## Exakte bedingte Writes und Rückgaben

Die Schreibadressen sind relativ zum an `0x32bc` eingehenden `r1`/`r2`, nach deren Weitergabe an `0x20c8`. `i` beginnt auf dem erfolgreichen Gate-Pfad bei null. Die Offsets bezeichnen Byteadressen; Stores sind 32 Bit.

| Write | Exakte Herleitung | Bedingung |
|---|---|---|
| `*(incoming_r2 + 0) = return_r0_at_0x14bc` | Der direkte Aufruf bei `0x2118` liefert lokal `r0`; `0x2120` speichert dieses Rückgabewort über `r9`, das bei `0x210c` aus incoming `r2` gesichert wurde. | Nach Guards und dem vorherigen direkten Aufruf bei `0x2110`; immer vor dem Nulltest bei `0x211c`. |
| `*(incoming_r1 + 8*i + 0) = *(current + 0x100)` | `0x213c` lädt das Wort an `[r3+0x100]`; `0x2140` speichert es an `[r6 + (r4<<3)]`, `r6=incoming_r1`, `r4=i`. | Für jedes Element, für das der Iterator-Next-Aufruf ungleich null liefert und `i < 10`. |
| `*(incoming_r1 + 8*i + 4) = current` | `0x2138` lädt `r3` aus dem Iterator-Ausgabeslot `[sp+4]`; `0x2144` speichert `r3` an `[r9 + (i<<3)]`, `r9=incoming_r1+4`. | Dieselbe Bedingung wie das vorige Element-Write; danach wird `i` bei `0x2148` um eins erhöht. |

Damit schreibt der Körper zunächst das 32-Bit-Rückgabewort von `0x14bc` an incoming `r2`, dann bis zu zehn geordnete 8-Byte-Paare ab incoming `r1`: bei Offset `8*i` das geladene Wort von `current+0x100`, bei Offset `8*i+4` den `current`-Wert. Sind keine Elemente vorhanden, entstehen keine Element-Writes. Es gibt keinen belegten Element-Write außerhalb dieser beiden Stores. Da die Herkunft und Gültigkeit der Zeiger nicht bekannt ist, sind dies beobachtete bedingte Stores, keine Aussage über Speichersicherheit.

| Rückgabepfad | Bedingung / Instruktionen | `r0` beim Return |
|---|---|---|
| Früher Fehler im Zielkörper | Nach direktem Aufruf bei `0x32cc`: `r1==0` oder `r2==0`, oder `(return_r0 & 0xff) != 1`; `eor` bei `0x32e0` und `uxtb` bei `0x32e8` begrenzen den Returntest auf das Low-Byte. Gate `0x32d0..0x32f0`, setzt `0x3308`. | `0xffffffff` (`-1` als 32-Bit-Wort), Return bei `0x330c`. |
| Fehler im Sekundärkörper | Nach Tail-Transfer `0x3304 -> 0x20c8`: globales Byte an der über PC gebildeten Basis `+0x28` ist nicht `1`, oder incoming `r1==0` oder `r2==0`; Gate `0x20d8..0x20f4`, setzt `0x2174`. | `0xffffffff`, gemeinsamer Epilog `0x216c..0x2170`. |
| Erfolgsabschluss | Sekundärkörper hat die lokale Prüfung passiert und entweder das Rückgabewort von `0x14bc` als null geprüft (`0x2124`) oder die Iteration beendet: Next-Rückgabe null oder `i >= 10` (`0x215c..0x2164`). | `0`, gesetzt bei `0x2168`, Return bei `0x2170`. |

Der erste Return-Gate-Aufruf bei `0x32cc` wird nicht als semantischer Test interpretiert: belegt ist nur, dass das Low-Byte seines zurückgegebenen `r0` gleich `1` sein muss. Auf dem Erfolgszweig stellt der Code die gesicherten Originalwerte wieder her und tail-transfert bei `0x3304` nach `0x20c8`. Ein Returnwert aus dem Sekundärkörper wird somit direkt zum Rückgabewert von `0x32bc`.

## Schleifenbedingung und opake Aufrufabhängigkeiten

`0x20fc` sichert das eingehende `r0` als `r5`; am konkreten Aufruf ist dies `10`. Das Indexregister `r4` ist auf diesem Pfad null, da der Eintritts-Guard in `0x20f0` nur bei `r4==0` fortfährt. Nach jedem Element-Write erhöht `0x2148` den Index um eins. `0x215c` prüft die Next-Rückgabe; falls nicht null, vergleicht `0x2160` unsigned `i` mit der gespeicherten Obergrenze. `0x2164` wiederholt zum Write-Körper genau bei `i < 10`. Somit ist der Bound exakt zehn, und die Zahl geschriebener Elemente ist durch zehn gedeckelt. Die genaue Zahl hängt zusätzlich von den Rückgaben/Iteratorausgaben der opaken Aufrufe ab.

Direkte Aufrufe und ausschließlich beobachtete Abhängigkeiten:

| Callsite im libdal-ELF | Direkte Ziel-VA | Lokal beobachtete Abhängigkeit | Callee-Effekte |
|---|---:|---|---|
| `0x32cc` | `0x2180` | Rückgabe-`r0` fließt in den `==1`-Gate-Ausdruck an `0x32e0`; keine andere Wirkung wird für den Vertrag benötigt. | **OFFEN** |
| `0x2110` | `0x14d4` | Aufruf zwischen lokaler Iterator-Adressbildung und dem nachfolgenden direkten Aufruf bei `0x2118`. | **OFFEN** |
| `0x2118` | `0x14bc` | Rückgabe-`r0` wird an incoming `r2` geschrieben und gegen null geprüft. | **OFFEN** |
| `0x2158` | `0x14c8` | Rückgabe-`r0` steuert, ob ein aktueller Eintrag verarbeitet wird; der Iterator-Ausgabeslot `[sp+4]` wird danach gelesen. | **OFFEN** |

Für keine dieser Callsites werden Register-, Speicher-, Iterator- oder globale Callee-Effekte jenseits der sichtbaren anschließenden lokalen Nutzung behauptet. Der Zeiger `current` und das an `current+0x100` gelesene Wort werden nicht semantisch benannt.

## Exakte Instruktionsnachweise

GNU ARM objdump 2.44 disassemblierte ausschließlich die Caller-Spanne `[0x2f08,0x2f24)` im IoDrvDal-ELF sowie `[0x32bc,0x3310)` und `[0x20c8,0x217c)` im separaten libdal-ELF. Vollständige Adress-/Opcode-Sequenzen liegen in `instructions.tsv`; der Validator vergleicht jede Adresse und jedes Wort mit der jeweils hashgebundenen Eingabe. Die folgenden Schlüsselinstruktionen zeigen die Übergänge:

| ELF-Adressraum | VA | Opcode | Instruktion / sichtbare Wirkung |
|---|---:|---|---|
| IoDrvDal | `0x2f08` | `ebfff6b1` | `bl 0x9d4` (importierter Getter, E-XE164-217) |
| IoDrvDal | `0x2f0c` | `e1a02008` | `mov r2,r8` |
| IoDrvDal | `0x2f10` | `e1a01005` | `mov r1,r5` |
| IoDrvDal | `0x2f14` | `e590300c` | `ldr r3,[r0,#0x0c]` |
| IoDrvDal | `0x2f18` | `e3a0000a` | `mov r0,#10` |
| IoDrvDal | `0x2f1c` | `e12fff33` | `blx r3` |
| libdal | `0x32cc` | `ebfffbab` | `bl 0x2180` (Rückgabe wird lokal geprüft) |
| libdal | `0x3304` | `eafffb6f` | Branch nach `0x20c8` mit restaurierten Eingaben |
| libdal | `0x2120` | `e5890000` | Store des Rückgabeworts aus `0x14bc` über gesichertes incoming `r2` |
| libdal | `0x2140` | `e7862184` | Store `[current+0x100]`-Wort an incoming `r1+8*i` |
| libdal | `0x2144` | `e7893184` | Store `current` an incoming `r1+8*i+4` |
| libdal | `0x2164` | `3afffff3` | Wiederhole bei unsigned `i < incoming_r0` |
| libdal | `0x2170` | `e8bd87f0` | Gemeinsamer Return des Sekundärkörpers |

Adressräume bleiben getrennt: `0x2f08..0x2f24` gehört ausschließlich zu `libIoDrvDal.so.1.0.2`; `0x32bc..0x3310` und `0x20c8..0x217c` gehören ausschließlich zu `libdal.so.1.0.1`. Die einzige Verknüpfung ist die statische Positions-/Slotbeobachtung E-XE164-229 zusammen mit dem Caller-Load und den Argument-Setups aus E-XE164-217.

## Beobachtung, Schlussfolgerung, Alternative, Restunsicherheit

- **Beobachtung — VERIFIZIERT:** Die beiden hashgebundenen ELFs und die Adress-/Opcode-Sequenzen stimmen mit den Eingabeidentitäten und dem Offline-Validator überein. E-XE164-229 meldet für libdal-Slot `+0x0c` den statischen REL-Addend `0x32bc`; E-XE164-217 meldet Caller-Load `+0x0c` sowie die Argumente `10,r5,r8`.
- **Schlussfolgerung — VERIFIZIERT, bedingt:** Falls der Getter im IoDrvDal-Pfad genau die untersuchte libdal-Objektinstanz liefert, erhält der Zielkörper `0x32bc` die drei oben ausgewiesenen Werte und erfüllt den tabellierten lokalen Positionsvertrag. Die ersten beiden Zeiger müssen ungleich null sein; zusätzlich müssen das Low-Byte der Rückgabe aus `0x2180` gleich `1` und das aus globalem Byte `+0x28` gebildete Byte gleich `1` sein.
- **Alternative:** Der Getter kann zur Laufzeit ein anderes Objekt, eine andere libdal-Instanz oder einen anders relocatierten Gegenstand liefern. Dann folgt aus dem statischen Slotwert keine Aussage, dass dieser Caller tatsächlich `0x32bc` ausführt. Die hier abgeleiteten Writes und Returns gelten in diesem Fall nicht für den tatsächlichen Laufzeitpfad.
- **Restunsicherheit — OFFEN:** Laufzeitauflösung/Objektidentität, Eintritts- und Statuswerte, globale Basis und Byte `+0x28`, Herkunft/Gültigkeit von `r5` und `r8`, alle Effekte der direkten Ziele, tatsächlicher Iteratorzustand, erreichbare Anzahl an Elementen und semantische Bedeutung sämtlicher Positionen/Werte.

## Provenienz und Status

- Eingaben: `work/worker/WP-XE164-202/input/libdal.so.1.0.1` (18,076 Bytes; SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`); `sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2` (25,976 Bytes; SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`). Beide SHA-256-Prüfungen: **PASS**.
- Wiederverwendete Evidence: E-XE164-217 (Callersequenz/Import- und Registerbeobachtung) und E-XE164-229 (separater Slot, Relocation und statisches Ziel). Diese Evidenzen liefern keine Laufzeitbindung.
- Werkzeuge: `arm-linux-gnueabihf-objdump` / GNU Binutils 2.44; Python 3.13.5 Standardbibliothek; `sha256sum` aus GNU coreutils. Keine Netzwerk-, VM-, Geräte-, Runtime- oder Repositoryaktion.
- Validator: `python3 validate.py` aus diesem Verzeichnis. Er prüft beide Inputhashes, die erwarteten Rohwörter an Slot `0x14160`, und alle Adress-/Opcode-Paare in den drei ausdrücklich begrenzten ELF-Bereichen durch getrennte GNU ARM Disassembly-Aufrufe. Ergebnis **PASS**; dies ist eine reproduzierbare statische Integritäts-/Scopeprüfung, kein Laufzeittest und kein unabhängiger Review.
- Tests: **NOT_RUN** (keine Produkt- oder Runtime-Tests angefordert; statischer Validator PASS).
- Status: lokale Writes und Returns bei statisch gebundenem Ziel **VERIFIZIERT**; Laufzeitbindung **OFFEN**; konkrete Ausführung **NOT_RUN**.
