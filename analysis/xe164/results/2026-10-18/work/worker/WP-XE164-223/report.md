> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-223 — Body `0x1bec..0x1d7f`

## Ergebnis und Umfang

**VERIFIZIERT** — Untersuchte Datei `FW31-LIBDAL-1.0.1`, Größe 18.076 Bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. REA band sie als ARM-ELF ein. Der untersuchte vollständige Body ist ELF `[0x1bec,0x1d80)` = Ghidra `[0x11bec,0x11d80)`, 404 Bytes / 101 dekodierte 4-Byte-Instruktionen. Ghidras Body-Adressmenge ist zusammenhängend und enthält den Entry. Die 64 benötigten Literalbytes liegen in ELF `[0x1d80,0x1dc0)` = Ghidra `[0x11d80,0x11dc0)`.

**VERIFIZIERT** — REA zuerst: Ghidra 12.1.4, REA-Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`, Image Base `0x10000`; keine lokale Disassemblierung als Ersatz. `0x11bec - 0x10000 = 0x1bec` und analog für alle aufgeführten Adressen.

Primärbelege: `ev_224cd8537e561549b547cafbdf58d9b3c7f425731480033dc5016f983c9a7b9c` (`analyze_function`), `ev_d55afe189ad209aacaa620f81e8e02731e0e00afb06f77b7b279e5ddd858626a` (vollständige CFG-Projektion), `ev_10db06ab263cdf77f4bbdd1b804ea59324a73800d4eff5e532b3569d930694d0` (Instruktionsliste), `ev_ff7dfe9442a46a3c098bfe96c5a4806b049a06b438808a104380b6f5f22b0926` (Assembly), `ev_56eca35898b9c7e8b745d7e62e1f5b3223eade8bd1d7f325e75ee6e1055c3c5f` (Literalbytes), `ev_f9b157d67705feac02dc29b25fc375c1645f26c58040e919b6b897838722b827` (Body-/Blockmetadaten), `ev_8c2d152df08359541395c0d2cc862c91efdc45d7d841b1626cbbf956fcafe0f2` (vollständige Callee-Liste), `ev_686347c1f8872c433505b0323fa5b7ef12dfdfcf794a02d1233228d23b130853` (High-P-Code-Abdeckung: 214 Operationen, nicht abgeschnitten).

## Basisadressrechnung

**VERIFIZIERT** — Little-Endian-Literalwörter und Rechenweg:

| ELF-Literaloffset | Bytes | geladenes Wort | Instruktion / ARM-PC-Wert | Ergebnis |
|---|---|---:|---|---:|
| `0x1d80` | `e0 25 01 00` | `0x000125e0` | `ldr r4` bei `0x11bf0`; dann `add r4,pc,r4` bei `0x11bf8`, PC=`0x11c00` | `r4 = 0x11c00 + 0x125e0 = 0x241e0` |
| `0x1d84` | `fc 23 01 00` | `0x000123fc` | `ldr r6` bei `0x11bf4`; dann `add r6,pc,r6` bei `0x11bfc`, PC=`0x11c04` | `r6 = 0x11c04 + 0x123fc = 0x24000` |

ARM-PC-Werte in dieser Tabelle sind jeweils aktuelle Instruktionsadresse plus 8. Die Gleichsetzungen beschreiben die sichtbare Berechnung; sie benennen weder ein Objekt noch eine ABI-Struktur. Ein späterer direkter Aufruf kann Registerwirkungen haben. Da Callee-Effekte hier nicht untersucht und keine ABI-Annahmen benutzt werden, bleibt das Fortbestehen dieser Registerwerte über Calls **OFFEN**.

Die für lokale Indizes und PC-relative Werte verwendeten Wörter sind ebenfalls vollständig im angegebenen Literalbereich enthalten:

| ELF-Offset | Wort (signed, falls negativ) | sichtbare Verwendung |
|---|---:|---|
| `0x1d88` | `0x20f8` | `ldr r9`; bei `add` an `0x11c2c`: PC `0x11c34`, Ergebnis `0x13d2c` |
| `0x1d8c` | `0x20f0` | `ldr r1`; bei `add` an `0x11c30`: PC `0x11c38`, Ergebnis `0x13d28` |
| `0x1d90` | `0x144` | Index für `[r6,r3]` an `0x11c80` |
| `0x1d94` | `0x140` | Index für `[r6,r1]` an `0x11c88` |
| `0x1d98` | `-0x128` | `add r3,pc,r3` an `0x11c8c`: PC `0x11c94`, Ergebnis `0x11b6c` |
| `0x1d9c` | `0x148` | Index für `[r6,r2]` an `0x11ca0` |
| `0x1da0` | `0x12c` | Index für `[r6,r3]` an `0x11ca4` |
| `0x1da4` | `-0x398` | `add r2,pc,r2` an `0x11cb0`: PC `0x11cb8`, Ergebnis `0x11920` |
| `0x1da8` | `-0x3a8` | `add r3,pc,r3` an `0x11cb4`: PC `0x11cbc`, Ergebnis `0x11914` |
| `0x1dac` | `-0x300` | `add r3,pc,r3` an `0x11cd4`: PC `0x11cdc`, Ergebnis `0x119dc` |
| `0x1db0` | `-0x370` | `add r2,pc,r2` an `0x11ce0`: PC `0x11ce8`, Ergebnis `0x11978` |
| `0x1db4` | `-0x3cc` | `add r3,pc,r3` an `0x11ce8`: PC `0x11cf0`, Ergebnis `0x11924` |
| `0x1db8` | `0x124d4` | `add r3,pc,r3` an `0x11d04`: PC `0x11d0c`, Ergebnis `0x241e0` |
| `0x1dbc` | `0x1fb4` | `add r3,pc,r3` an `0x11d5c`: PC `0x11d64`, Ergebnis `0x13d18` |

## Instruktionen und CFG

**VERIFIZIERT** — 101 Instruktionen, 15 Basisblöcke, 23 gerichtete CFG-Kanten, neun direkte Call-Instruktionen. Blockgrenzen und Nachfolger (Ende exklusiv, alle Adressen Ghidra) sind:

| Block | Bereich | Nachfolger |
|---|---|---|
| B0 | `[0x11bec,0x11c10)` | B1, B2 |
| B1 | `[0x11c10,0x11c18)` | — (Exit) |
| B2 | `[0x11c18,0x11c24)` | B3, B13 |
| B3 | `[0x11c24,0x11c44)` | B4, B13 |
| B4 | `[0x11c44,0x11c5c)` | B5, B14 |
| B5 | `[0x11c5c,0x11c74)` | B6, B13 |
| B6 | `[0x11c74,0x11cf8)` | B7, B12 |
| B7 | `[0x11cf8,0x11d18)` | B8, B13 |
| B8 | `[0x11d18,0x11d24)` | B9, B13 |
| B9 | `[0x11d24,0x11d30)` | B10, B13 |
| B10 | `[0x11d30,0x11d48)` | B11, B13 |
| B11 | `[0x11d48,0x11d58)` | — (Exit) |
| B12 | `[0x11d58,0x11d6c)` | B7 |
| B13 | `[0x11d6c,0x11d74)` | B1 |
| B14 | `[0x11d74,0x11d80)` | B1 |

**VERIFIZIERT** — Die folgende vollständige Ghidra-Instruktionsliste deckt den Body ohne Lücke ab; Mnemoniktext bleibt provider-spezifisch:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

## Speicherzugriffe auf literalberechnete Basen

**VERIFIZIERT** — Die Tabelle unterscheidet Adressoperanden, deren konkrete effektive Adresse lokal belegt ist, von bloßen späteren Registeroperanden. Vor dem ersten direkten Call bei `0x11c38` sind `r4+0x28` und `r4+0x24` konkret auflösbar. Der bei `0x11d04` neu aus Literal `0x1db8` berechnete `r3`-Wert ist bis zum letzten `r3`-Speicherzugriff bei `0x11d50` ohne intervenierenden Call. Für spätere `r4`-/`r6`-Operanden wird keine frühere Entry-Definition über Calls fortgeschrieben; ihre Effektivadressen bleiben **OFFEN**. Es wurden keine zusätzlichen per-site Ghidra-Xrefs zur Auflösung dieser Adressen herangezogen.

| Ghidra-Adresse / Instruktion | Operand / effektive Adresse | Breite / Richtung | Wertquelle oder Zweck auf Maschinenebene |
|---|---|---|---|
| `0x11c00 ldrb r3,[r4,#0x28]` | `r4+0x28` = `0x241e0+0x28` = `0x24208` | 1 B, Lesen | Byte am lokal berechneten Entry-Basisoperand, dann Vergleich mit 0 |
| `0x11c18 ldr r8,[r4,#0x24]` | `r4+0x24` = `0x241e0+0x24` = `0x24204` | 4 B, Lesen | Wort am lokal berechneten Entry-Basisoperand, dann Vergleich mit 0 |
| `0x11c60 str r7,[r4,#0x24]` | Operand `r4+0x24`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r7`; Laufzeitinhalt nicht beobachtet |
| `0x11c6c str r0,[r4,#0x20]` | Operand `r4+0x20`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r0` nach Call bei `0x11c64`; Call-Wirkung **OFFEN** |
| `0x11c80 ldr r0,[r6,r3]` | Operand `r6+r3`; effektive Adresse **OFFEN** | 4 B, Lesen | Indexregister zuvor aus Literalwort bei `0x11d90` geladen; effektiver Laufzeitindex wegen Call-Grenze **OFFEN** |
| `0x11c88 ldr r1,[r6,r1]` | Operand `r6+r1`; effektive Adresse **OFFEN** | 4 B, Lesen | Indexregister zuvor aus Literalwort bei `0x11d94` geladen; effektiver Laufzeitindex **OFFEN** |
| `0x11c9c str r0,[r4,#0]` | Operand `r4+0`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r0` nach Call bei `0x11c90`; Call-Wirkung **OFFEN** |
| `0x11ca0 ldr r1,[r6,r2]` | Operand `r6+r2`; effektive Adresse **OFFEN** | 4 B, Lesen | Indexregister zuvor aus Literalwort bei `0x11d9c` geladen; effektiver Laufzeitindex **OFFEN** |
| `0x11ca4 ldr r0,[r6,r3]` | Operand `r6+r3`; effektive Adresse **OFFEN** | 4 B, Lesen | Indexregister zuvor aus Literalwort bei `0x11da0` geladen; effektiver Laufzeitindex **OFFEN** |
| `0x11cbc str r0,[r4,#4]` | Operand `r4+4`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r0` nach Call bei `0x11cb8`; Call-Wirkung **OFFEN** |
| `0x11cc4 ldr r1,[r4,#0x18]` | Operand `r4+0x18`; effektive Adresse **OFFEN** | 4 B, Lesen | Registeroperand; Speicherinhalt und effektive Adresse nicht beobachtet |
| `0x11cd8 str r3,[r4,#0xc]` | Operand `r4+0xc`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r3`; Operand wurde lokal bei `0x11cd4` PC-relativ gebildet |
| `0x11ce4 str r2,[r4,#0x10]` | Operand `r4+0x10`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r2`; Operand wurde lokal bei `0x11ce0` PC-relativ gebildet |
| `0x11cec str r3,[r4,#8]` | Operand `r4+8`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r3`; Operand wurde lokal bei `0x11ce8` PC-relativ gebildet |
| `0x11cf0 str r0,[r4,#0x14]` | Operand `r4+0x14`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r0` nach Call bei `0x11cc0`; Call-Wirkung **OFFEN** |
| `0x11d08 ldr r2,[r3,#0]` | `r3+0` = `0x241e0+0` = `0x241e0` | 4 B, Lesen | `r3` wurde bei `0x11d04` aus Literal `0x1db8` berechnet; Wort in `r2`, Vergleich mit 0 |
| `0x11d10 str r0,[r3,#0x1c]` | `r3+0x1c` = `0x241e0+0x1c` = `0x241fc` | 4 B, Schreiben | Store-Quellenoperand `r0` nach Call `0x11cfc`; neu berechnetes `r3` selbst liegt ohne intervenierenden Call vor |
| `0x11d18 ldr r2,[r3,#4]` | `r3+4` = `0x241e0+4` = `0x241e4` | 4 B, Lesen | wortweiser Ladezugriff nach `0x11d04`, danach Vergleich mit 0 |
| `0x11d24 ldr r2,[r3,#0x18]` | `r3+0x18` = `0x241e0+0x18` = `0x241f8` | 4 B, Lesen | wortweiser Ladezugriff nach `0x11d04`, danach Vergleich mit 0 |
| `0x11d30 ldr r5,[r3,#0x14]` | `r3+0x14` = `0x241e0+0x14` = `0x241f4` | 4 B, Lesen | Wort in `r5`; wird mit `r0` verglichen/bedingt überschrieben |
| `0x11d50 strb r2,[r3,#0x28]` | `r3+0x28` = `0x241e0+0x28` = `0x24208` | 1 B, Schreiben | unmittelbar davor `r2←1` an `0x11d48`; keine Call-Instruktion seit `r3`-Berechnung |
| `0x11d60 str r3,[r4,#0x18]` | Operand `r4+0x18`; effektive Adresse **OFFEN** | 4 B, Schreiben | Store-Quellenoperand `r3`, bei `0x11d5c` lokal zu `0x13d18` berechnet; der Basisoperand `r4` liegt nach Calls |

Die ersten beiden Instruktionen lesen die Basis-Literalwörter selbst; die weiteren LDRs aus `0x11d88..0x11dbc` lesen die oben tabellierten Literalwörter. Diese Literalzugriffe liegen außerhalb des berechneten Bereichs und sind nicht als Zugriffe auf ihn gezählt.

Zusätzlich enthält der Body einen `stmdb sp!` bei `0x11bec` (32 B Stack-Schreibtransfer für die in der Instruktion gelisteten acht Register) und zwei mögliche `ldmia sp!`-Exittransfers bei `0x11c14` bzw. `0x11d54` (je 32 B Stack-Lesetransfer). Die konkrete absolute Stackadresse ist nicht sichtbar und wird nicht behauptet.

## Calls und sichtbare Exitwerte

**VERIFIZIERT** — Neun direkte Calls, ausschließlich durch Zieladresse identifiziert:

| Call-Instruktion | Ziel | post-call-`r0`-Operandfluss (ABI-neutral) |
|---|---|---|
| `0x11c38` | `0x11438` | `r0` wird bei `0x11c3c` getestet und in `r7` geschrieben |
| `0x11c44` | `0x11378` | vor einem späteren Vergleich folgt Call `0x1163c`; separater Wert daraus bleibt **OFFEN** |
| `0x11c4c` | `0x1163c` | `r0` wird bei `0x11c50` verglichen und bei `0x11c54` nach `r5` kopiert |
| `0x11c64` | `0x115b8` | `r0` wird getestet und bei `0x11c6c` gespeichert |
| `0x11c90` | `0x114e0` | aktuelles `r0` wird bei `0x11c9c` gespeichert |
| `0x11cb8` | `0x114e0` | aktuelles `r0` wird bei `0x11cbc` gespeichert |
| `0x11cc0` | `0x13bcc` | aktuelles `r0` wird bei `0x11cf0` gespeichert |
| `0x11cfc` | `0x11468` | `r0` wird bei `0x11d10` gespeichert und später getestet/kopiert |
| `0x11d78` | `0x11408` | Folgepfad liest das nach Rückkehr in `r0` stehende Ergebnis nicht weiter; `0x11c10` kopiert danach den aktuellen Registeroperanden `r5` nach `r0` |

**OFFEN** — Call-Effekte, einschließlich Speicherwirkungen, Registerzerstörung/-bewahrung und nach Rückkehr gelieferter Werte, sind nicht Teil dieser Untersuchung. Direkte Zieladressen belegen keine vollständigen Funktionsverträge.

**VERIFIZIERT** — Body-eigene Rückkehrstellen sind `0x11c14` und `0x11d54`. An beiden lädt `ldmia` Register einschließlich PC; der sichtbare Wert in `r0` beim Verlassen des Bodys ergibt sich aus dem lokalen Pfad:

| Pfadbedingung / Instruktionskette | sichtbarer `r0`-Wert an Exit |
|---|---|
| `0x11c00..0x11c0c`: gelesenes Byte ungleich 0; `movne r5,#0`; `0x11c10: cpy r0,r5`; Exit `0x11c14` | `0` |
| Fehlerzweige bei `0x11c20`, `0x11c40`, `0x11c70`, `0x11d14`, `0x11d20`, `0x11d2c` oder `0x11d44` → `0x11d6c: mvn r5,#0` → `0x11d70` → `0x11c10` | `0xffffffff` |
| Vergleich an `0x11c50` führt zu `0x11d74`; dort `cpy r0,r7`, dann Call `0x11408`, Branch `0x11d7c` → `0x11c10` | aktuelles `r5` nach dem Call an `0x11d78`, weil `0x11c10: cpy r0,r5` den früheren Argumentwert `r7` überschreibt; Bezug zum vor dem Call bei `0x11c54` kopierten Wert bleibt wegen unbekannter Call-Wirkung **OFFEN** |
| Pfad bis `0x11d48`: `r0` und das bei `0x11d30` geladene `r5` sind jeweils ungleich 0; `movne r5,#0` bei `0x11d40`; `0x11d4c: cpy r0,r5`; `0x11d50` speichert Byte `1`; Exit `0x11d54` | `0` |

Die beiden Rückkehrstellen sind alle in der analysierten Body-Adressmenge beobachteten Returns. Das ist eine statische Aussage zu Ghidras vollständiger Body-/CFG-Beobachtung, keine Ausführungsmessung.

## Befundstatus, Alternativerklärung und Grenzen

**VERIFIZIERT** — Die beschriebenen Instruktionen, Literalwörter, Bodygrenze, 15 Blöcke, 23 Kanten, neun direkten Call-Sites, lokalen Zugriffsausdrücke und zwei Rückkehrstellen sind im REA/Ghidra-Beleg enthalten oder durch die ausgewiesene arithmetische Ableitung daraus gewonnen.

**HYPOTHESE** — Die beiden berechneten Basen könnten von Code als Tabellen-/Speicherbereiche verwendet werden. Das ist nur eine alternative neutrale Erklärung der Maschinenzugriffe; daraus werden weder Objekttyp noch Zweck abgeleitet.

**OFFEN** — Semantische Bedeutung von Speicherfeldern, Zielobjekten und Call-Zielen; alle Call-Wirkungen; tatsächliche Laufzeitwerte/-pfade; die Fortgeltung einer Registerdefinition über einen Call; indirekte Aliase, sofern nicht aus der Body-Arithmetik sichtbar. Der Bericht leitet aus Importnamen, Caller/Nachbarbody oder Speicherlayout keine Bedeutung ab.

Ghidras High-P-Code-Abdeckung für diesen Dossierbeleg ist vollständig nach den dort gemeldeten Zählern (214 Operationen, 243 Def-Use-Kanten, 19 Effekte, `truncated=false`); diese Abdeckung ersetzt keine Laufzeitbeobachtung und löst Call-Wirkungen oder Speicheraliasing nicht auf. Es wurden keine Callee-Körper, Caller, Nachbarbody ab ELF `0x1dc0`, Runtime, Geräte, Netzwerk oder VM untersucht.

## Reproduzierbare Prüfung

`validate.py` prüft offline die Zieldatei per SHA-256, Größe, Body-/Literal-Bytefenster und die Kerndeklarationen dieses Reports. Aus dem Verzeichnis `WP-XE164-223` ausführen:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Erwarteter Teststatus: `PASS`. Das Skript ist ein Konsistenzvalidator, kein Disassembler und kein unabhängiger zweiter Review. Selbstprüfung: **PASS** nach Ausführung des Validators. Der self-reference-freie SHA-256-Manifest-Eintrag steht in `SHA256SUMS`; er hasht Bericht und Validator, nicht sich selbst.
