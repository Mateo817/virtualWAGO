> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-229 — A32-Dispatcher im begrenzten Bereich

## Identität und Methode

**VERIFIZIERT** — Eingabe: `libIoDrvDal.so.1.0.2`, 25.976 Byte, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.

**VERIFIZIERT** — REA 6.5.0 öffnete die Datei als ARM ELF; der gebundene Provider war Ghidra 12.1.4. Ghidras Segmentinventar meldete Image Base `0x10000` und `.text` bei Provider-VA `0x10a34..0x14678`. Daher entsprechen die angefragten ELF-VAs `[0x362c,0x3680)` den Provider-VAs `[0x1362c,0x13680)`, mit Mapping `Provider-VA = ELF-VA + 0x10000`.

**VERIFIZIERT** — Der erste REA-Versuch verwendete unverschobene ELF-VAs und bekam `outside-memory`; das war ein Adressdomänenfehler. Der korrigierte `inspect_native_instruction`-Durchlauf fragte ausschließlich die 21 erlaubten Instruktionsstarts `0x1362c..0x1367c` ab. Alle 21 wurden von Ghidra als Instruktionen dekodiert. Der Eintrag `0x13644` enthält Referenzmetadaten für berechnete Ziele bis einschließlich `0x13680`; an dieser letzten Adresse wurde keine Inspektionsanfrage gestellt und kein Inhalt gelesen oder dekodiert.

**VERIFIZIERT** — GNU ARM objdump 2.44 (`arm-linux-gnueabihf-objdump`) wurde ausschließlich als begrenzter Gegencheck für `[0x362c,0x3680)` verwendet. Seine Stoppadresse war exklusiv; die Ausgabe endete bei `0x367c`. Der Fallback wurde nicht als REA-Toollücke gewertet.

## 21 Instruktionen

**VERIFIZIERT** — Ghidra meldet die Bytes in Dateireihenfolge (Little Endian). Disassembly-Ziele sind unten als ELF-VA angegeben; die von Ghidra gemeldeten Provider-Adressen sind um `0x10000` höher. objdump bestätigte den gesamten Wortstrom innerhalb des begrenzten Bereichs.

| ELF-VA | Provider-VA | Bytes | Ghidra A32-Disassembly (Ziel als ELF-VA) |
|---:|---:|---:|---|
| `0x362c` | `0x1362c` | `f04f2de9` | `stmdb sp!,{r4,r5,r6,r7,r8,r9,r10,r11,lr}` |
| `0x3630` | `0x13630` | `bcd04de2` | `sub sp,sp,#0xbc` |
| `0x3634` | `0x13634` | `023040e2` | `sub r3,r0,#0x2` |
| `0x3638` | `0x13638` | `fc02cde1` | `strd r0,r1,[sp,#0x2c]` |
| `0x363c` | `0x1363c` | `34208de5` | `str r2,[sp,#0x34]` |
| `0x3640` | `0x13640` | `0d0053e3` | `cmp r3,#0xd` |
| `0x3644` | `0x13644` | `03f18f90` | `addls pc,pc,r3, lsl #0x2` |
| `0x3648` | `0x13648` | `d10200ea` | `b 0x4194` |
| `0x364c` | `0x1364c` | `170000ea` | `b 0x36b0` |
| `0x3650` | `0x13650` | `380000ea` | `b 0x3738` |
| `0x3654` | `0x13654` | `c40200ea` | `b 0x416c` |
| `0x3658` | `0x13658` | `cf0200ea` | `b 0x419c` |
| `0x365c` | `0x1365c` | `cc0200ea` | `b 0x4194` |
| `0x3660` | `0x13660` | `cb0200ea` | `b 0x4194` |
| `0x3664` | `0x13664` | `ca0200ea` | `b 0x4194` |
| `0x3668` | `0x13668` | `c90200ea` | `b 0x4194` |
| `0x366c` | `0x1366c` | `c80200ea` | `b 0x4194` |
| `0x3670` | `0x13670` | `030300ea` | `b 0x4284` |
| `0x3674` | `0x13674` | `c60200ea` | `b 0x4194` |
| `0x3678` | `0x13678` | `090300ea` | `b 0x42a4` |
| `0x367c` | `0x1367c` | `000000ea` | `b 0x3684` |

**VERIFIZIERT** — Die direkten Branchziele oben wurden dekodiert, aber ihre Zielkörper wurden nicht betreten oder untersucht.

## PC-Arithmetik und Abbildung

**VERIFIZIERT** — `0x3634` berechnet im 32-Bit-Register `r3` den Wert `r0−2`. `0x3640` vergleicht `r3` mit 13. `addls` bei `0x3644` führt den PC-Dispatch nur für unsigned `r3≤13` aus; andernfalls verzweigt `0x3648` direkt nach ELF-VA `0x4194`.

**VERIFIZIERT** — Der von A32 gelesene PC bei Instruktionsadresse `0x3644` ist `0x364c` (Instruktionsadresse plus 8). Die effektive Zellenadresse lautet somit `0x364c + 4×(r0−2)`. Die 13 dekodierten Zellen ergeben:

| Sichtbares Eingangs-`r0` | `r3` | berechnete ELF-Zellenadresse | Direktziel (ELF-VA) |
|---:|---:|---:|---:|
| 2 | 0 | `0x364c` | `0x36b0` |
| 3 | 1 | `0x3650` | `0x3738` |
| 4 | 2 | `0x3654` | `0x416c` |
| 5 | 3 | `0x3658` | `0x419c` |
| 6 | 4 | `0x365c` | `0x4194` |
| 7 | 5 | `0x3660` | `0x4194` |
| 8 | 6 | `0x3664` | `0x4194` |
| 9 | 7 | `0x3668` | `0x4194` |
| 10 | 8 | `0x366c` | `0x4194` |
| 11 | 9 | `0x3670` | `0x4284` |
| 12 | 10 | `0x3674` | `0x4194` |
| 13 | 11 | `0x3678` | `0x42a4` |
| 14 | 12 | `0x367c` | `0x3684` |

**VERIFIZIERT** — Die Zelle bei ELF-VA `0x364c` (Provider-VA `0x1364c`) ist für sichtbares `r0=2` erreichbar und enthält einen direkten Branch nach ELF-VA `0x36b0`. Sie ist die erste Zelle des PC-Dispatchs.

## Ausgeschlossene Folgeadresse `0x3680`

**VERIFIZIERT** — Für `r0=15` ist `r3=13`; die Rechnung ergibt `0x364c + 4×13 = 0x3680`. Das unsigned Bounds-Gate lässt diesen Index passieren. Ghidras berechneter Referenzsatz vom Dispatch schließt Provider-Adresse `0x13680` als folgende mögliche Zieladresse ein.

**OFFEN** — Inhalt, Instruktionsstatus und Direktziel der Zelle an ELF-VA `0x3680` wurden nicht als adressbezogener REA/objdump-Lesevorgang angefragt, ausgegeben oder dekodiert. Der vollständige SHA-256-Lauf liest die Eingabedatei für Identitätsprüfung; er liefert keine Interpretation des Zellinhalts. Der für `r0=15` folgende Pfad ist bezüglich des Zellinhalts offen.

## Beobachtung, Schlussfolgerung und Restunsicherheit

**VERIFIZIERT — Beobachtung:** Der korrigierte Provider-VA-Durchlauf liefert die 21 Instruktionen und deren Bytes; objdump bestätigt begrenzt denselben Wortstrom. Der Dispatcher subtrahiert zwei von `r0`, prüft unsigned gegen 13 und bildet bei bestandenem Gate einen wortweise skalierten Offset zum PC.

**VERIFIZIERT — Schlussfolgerung:** Für `r0=2..14` gilt die oben aufgeführte genaue Zuordnung. Für `r0=0` oder `1` entsteht beim 32-Bit-Subtrahieren ein großer unsigned Wert; für `r0≥16` liegt `r3` ebenfalls über 13. Diese Fälle folgen dem beobachteten Default-Branch nach `0x4194`. Für `r0=15` wird die ausgeschlossene Adresse `0x3680` berechnet und das Gate passiert.

**HYPOTHESE — Alternativerklärung:** Eine um acht Byte verschobene Indexzuordnung entstünde, wenn der PC bei A32 fälschlich als Instruktionsadresse `0x3644` statt als `0x364c` angesetzt würde. Sie passt nicht zur A32-PC-Regel und der unmittelbar nach dem Dispatcher beginnenden Zellfolge.

**OFFEN — Restunsicherheit:** Die semantische Bedeutung der numerischen Auswahlwerte, Verhalten der Zielkörper und Inhalt/Wirkung der ausgeschlossenen Zelle bleiben unbekannt. Keine Aussage zu Calling Convention, Callee-Effekten, Runtime oder Hardware.

## Validator und Manifest

**PASS** — `python3 validate.py` prüft Größe und berechnet den vollständigen SHA-256 der Eingabe gemäß Auftrag. Anschließend prüft es mit objdump und exklusiver Stoppadresse `0x3680` genau die 21 erlaubten Adressen und Instruktionswörter. Der objdump-Lauf ist ein begrenzter Gegencheck; der Inhalt bei `0x3680` wird nicht dekodiert oder ausgegeben.

**VERIFIZIERT** — `manifest.sha256` enthält Hashes von `report.md` und `validate.py`, nicht von sich selbst.
