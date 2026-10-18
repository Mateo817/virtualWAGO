> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-118 — Call-Lane und 18-Record-Extent

## Ergebnis

**VERIFIZIERT:** Ghidra ordnet die Call-Site `0x330664` und das Tabellenliteral im selben ARM-ELF `codesys3` der Procedure `FUN_00330610` zu. Der beobachtete Procedure-Body ist zusammenhängend `0x330610..0x33067b` (inklusive), 108 Byte, fünf Basic Blocks. Die 32-Bit-Literalzelle bei `0x33067c` liegt direkt nach dem beobachteten Body, ist aber kein Bestandteil dieses Body-Intervalls.

**VERIFIZIERT:** Der Call bei `0x330664` ist `blx r4`, statisch ein indirekter/berechneter Call ohne von Ghidra aufgelöstes Ziel. Sein Zielregister `r4` stammt unmittelbar aus `ldr r4,[r4,#0x150]` bei `0x330654`; der Basiswert in `r4` war zuvor aus `movw r4,0x1520; movt r4,0x60` aufgebaut (`0x00601520`). Der geladene Funktionszeiger liegt damit im statisch adressierten Slot `0x00601670`. Der Slotinhalt zur Laufzeit und die Callee-Semantik bleiben unbelegt.

**VERIFIZIERT:** Unmittelbar vor `blx r4` sind die ARM-Registerargumente: `r0 = 0x003add1c`, `r1 = 0`, `r2 = 0`, `r3 = 0x12` (dezimal 18). `r0` wird aus der Wortzelle bei `0x33067c` geladen; ihre Ghidra-Bytes sind `1c dd 3a 00`, also little-endian `0x003add1c`. `r1` erhält den Wert aus `r2`; `r2` wurde nach dem ersten Call mit `subs r2,r0,#0` aus dessen Rückgabewert gebildet. Der Kontrollfluss erreicht den zweiten Call ausschließlich bei erstem Call-Ergebnis null. `r3` wird danach explizit auf `0x12` gesetzt. Der erste Call selbst ist ebenfalls indirekt: `blx r5` bei `0x330648`, wobei `r5` bei `0x330634` aus demselben Feld `[0x00601520+0x150]` geladen wird. Ghidra löste auch dieses Ziel nicht auf.

**VERIFIZIERT:** Unmittelbar nach dem zweiten Call wird `r0` nicht mehr geändert, sondern der gemeinsame Epilog ausgeführt. Auf dieser Rückkehrkante wird daher der Call-Rückgabewert in `r0` als Rückgabewert dieser Procedure durchgereicht.

## Abgrenzung der 18 Slots

REA las vollständig 288 Byte ab Ghidra-Default-Space-Adresse `0x3add1c`; die exakte Quellenabbildung von Ghidra ergibt ELF-Datei-Offset `0x39dd1c` (dezimal 3.792.156). Das ist ein ARM-ELF32-EXEC. Die separat protokollierten Koordinaten stehen in der CSV als Ghidra-Adresse, ELF-VMA und Datei-Offset. Hier haben die Ghidra-Adresse und ELF-VMA denselben Zahlenwert: der ELF `PT_LOAD` für Text/RO lädt Offset `0` nach VMA `0x10000`, so dass die Abbildung zu den betreffenden geladenen Bytes `VMA = Datei-Offset + 0x10000` ergibt. Diese Segmentbeziehung wurde ergänzend mit GNU `readelf` aus Binutils 2.44 gelesen. Das Literal liegt bei Ghidra-/ELF-VMA `0x33067c`, ELF-Datei-Offset `0x32007c`.

Die 288 beobachteten Byte bilden genau 18 direkt aufeinanderfolgende 16-Byte-Rohblöcke. Der exklusive Ende-Zeiger der rein arithmetischen Sequenz ist `0x3add1c + 18*16 = 0x3ade3c`; der letzte enthaltene 16-Byte-Block beginnt bei `0x3ade2c` und endet inklusiv bei `0x3ade3b`. Jeder Record enthält vier little-endian 32-Bit-Wörter. Die dazugehörige vollständige Tabelle ist [table-18-records.csv](table-18-records.csv).

Der WP116-Accessor-Pointer-Rohrecord bei `0x3ade1c` liegt `0x100` Byte nach dem Start. Damit ist er nullbasierter Index 16, also der 17. Record in einsbasierter Ordinalzählung; sein Paarinhalt lautet `[0x0032e814, 0x003ae618, 0, 0]`. Der benachbarte ValueByte-Rohrecord bei `0x3ade2c` liegt bei nullbasiertem Index 17 (18. Record) und lautet `[0x00333ed8, 0x003ae63c, 0, 0]`. Beide liegen im rechnerisch abgedeckten 18×16-Byte-Fenster; der ValueByte-Record wäre dessen letzter Record.

Root-Audit-Korrektur: Die frühere Formulierung „Accessor-Datensatz an Index 17“ vermischte nullbasierte Indizes mit der 17. Record-Ordinalzahl. Korrekt ist: Pointer-Accessor bei Index 16 / ordinal 17; ValueByte-Nachbar bei Index 17 / ordinal 18. Die Recordadressen und Werte in der CSV wurden gegen die Quelldatei nachgerechnet. `r3=18` bleibt ein unmittelbar beobachtetes Argument; die Aussage über den 18-Record-Extent ist daher bedingt auf die nicht belegte Interpretation dieses Arguments als Recordanzahl.

**OFFEN:** Der Registerwert `0x12` ist als unmittelbarer Zahlenwert im Argumentregister `r3` verifiziert. Ohne aufgelöstes Ziel und belegten Callee-Vertrag lässt sich nicht verifizieren, dass er eine Recordanzahl, Byteanzahl oder sonstige konkrete Maßeinheit bedeutet. Daher ist `18` hier nicht als semantisch bewiesene Tabellenlänge oder -count benannt. Bedingt auf die Hypothese „`r3` ist eine Anzahl von 16-Byte-Records“ schließt der Bereich nullbasierte Indizes 0..17 ein und reicht exklusiv bis `0x3ade3c`; somit lägen sowohl der Pointer-Accessor bei Index 16 als auch der ValueByte-Record bei Index 17 darin. Dass der Callee diesen Registerwert tatsächlich als genau diesen Record-Extent auswertet, bleibt **OFFEN**.

## Befundstatus und alternative Erklärung

**HYPOTHESE:** Der zweite Callback könnte einen Tabellenzeiger zusammen mit einem Grenz-/Moduswert erhalten und darüber Einträge verarbeiten; der sichtbare Call-Site-Datenfluss allein legt diese Bedeutung nicht fest. Alternative Erklärungen sind, dass `r3=18` eine andere Konfiguration bezeichnet oder dass der Callback die 18 nur als Obergrenze in einer anderen Einheit nutzt. Auch kann der Bereich eine strukturierte Paarliste sein, ohne dass dieser Call alle 18 Records verarbeitet.

**OFFEN:** Eine konkrete Semantik des Calls oder tatsächliche Laufzeit-Call-Zielzuordnung ist statisch nicht geklärt. Dieses Arbeitspaket nimmt keine Callee- oder Runtime-Schlüsse vor.

## Evidenz, Werkzeuge und Grenzen

| Beobachtung | Fundstelle / Evidenz | Status |
|---|---|---|
| Eingabedatei 5.181.396 Bytes; SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | `codesys3`; SHA-256 lokal geprüft | VERIFIZIERT |
| Ghidra 12.1.4, ARM, Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de` | kanonisches `rea-evidence-bundle.json`; Evidence `ev_3069…`, `ev_2ef8…` | VERIFIZIERT |
| Containing Procedure / Grenzen / 5 Blocks | `0x330610..0x33067b`; Evidence `ev_3069a2592ec3babd0a7966ae6900e3c82ba13f9a9c4a7cb358d525a52f1472e6`, `ev_59f4d7f32d2e7e7e36867b17d57da1a2fad070d770dc1b5d2ef37125b9ae7cb8` | VERIFIZIERT |
| Instruktionen und unmittelbarer Registerfluss | `0x330630..0x330678`; Evidence `ev_2ef865b1276f0ea2db90b46c77b176abddc89f8b1d5ee7f47198edacb02b3967`, `ev_8f3f6dfa3bcf0a33eb35e0232822707d85e4565e95b21285cf99d160c328fb79` | VERIFIZIERT |
| Zweiter Call statisch berechnet, ohne Zielreferenz | Site `0x330664`; Evidence `ev_19f66062751c32682ff618aba4c6f7b9c25a362eb915bd5ff6c3a7c4ebe01c7b`; erster Call Site `0x330648`, Evidence `ev_9bc025c95eb6e9910f78381d405aab090e12debfcc69a79237443fcd0c172420` | VERIFIZIERT |
| Literalwort `0x003add1c` | Ghidra-Rohbytes an `0x33067c`; Evidence `ev_eebe2eff642c7e8516d40a38dc7fe49deb7b32835401453bccaec95de906096a` | VERIFIZIERT |
| Vollständiger 18×16-Byte-Datenbereich | REA-Bytes ab `0x3add1c`, 288/288 Bytes; Evidence `ev_6b9668fa7d2c15f0eaf2ae3a518f68cf0015210bfc484921cc3636edd035d310` | VERIFIZIERT |
| Quellenabbildung Tabellenanfang und Literal | `0x3add1c → 3.792.156`, `0x33067c → 3.278.460`; Evidence `ev_ce8153883f9867ae783cde26c39fe1265e36379d20073c8f45a1c0df75b17a5d`, `ev_9cfebcbe7d5d843ff7bf27af886713dc2cc904f8b56f8d582044aafc15d7bbf9` | VERIFIZIERT |
| Accessor- und ValueByte-Paarabgleich | WP116 korrigierter Bericht SHA-256 `e0195fd44d465984082b71b1a7fc70a6b13cedf94f23f3e69ed09088b4299e88`; Bundle SHA-256 `9272ec61f1347fe722893c082cec4ef138a47408c610ad2fca21ad7e4dca1389`; WP116 identifiziert `0x333ed8` als ValueByte-Entry | VERIFIZIERT |

REA wurde zuerst verwendet; es gab für die entscheidenden Instruktions- und Bytebeobachtungen keine Lücke, daher war kein Disassembler-/Raw-Byte-Fallback erforderlich. `readelf` wurde nur zur ELF-PT_LOAD-Koordinatenbeziehung verwendet. Die binäre Eingabe wurde nicht verändert. Callee-Body, reale Callback-Adresse, Runtime und Geräte wurden nicht untersucht.

## Prüfstatus und erzeugte Dateien

| Prüfung | Status |
|---|---|
| Eingabegröße und Hash | PASS |
| REA-Evidence-Bundle: Zielhash, Recordzahl, eindeutige Evidence-IDs | PASS |
| CSV gegen exakt 288 Input-Bytes und Little-Endian-Wörter | PASS |
| Endpunkt und Accessor-Slotindex (null- und einsbasiert) | PASS |
| Semantik von `r3=18` im Callee | NOT_RUN |
| Runtime / Zielgerät / Netzwerk / VM | NOT_RUN |

Erzeugt: `report.md`, `rea-evidence-bundle.json` (12 Records, 0 Unknowns), `table-18-records.csv`, `validate.py`, `SHA256SUMS`. SHA-256 aller erzeugten Inhaltsdateien stehen in `SHA256SUMS`. Self-Review: Validator und Bericht wurden gegen die Eingabe und REA-Evidence geprüft; kein unabhängiger Review oder Worker-Lauf wird behauptet.
