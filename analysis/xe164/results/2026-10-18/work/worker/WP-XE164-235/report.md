> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-235 — bounded static search

## Finding

**VERIFIZIERT — Nein, innerhalb der angegebenen statischen Suchmethode wurde kein A32-Pfad gefunden, der `r0=15` ohne Wertfortschreibung über einen opaque Call an ein indirektes `blx` liefert, dessen Zielregister zuvor sichtbar aus `[Basisregister,#0x20]` geladen wurde.** Der Befund gilt nur für den file-backed `.text`-Bereich `[0x00180000,0x00280000)` und die unten beschriebene vollständige Wortdekodierung mit begrenzter direkter Branch-/Fallthrough-Suche. Er ist keine Aussage über Laufzeitverhalten oder sämtliche möglichen Datenflussformen.

## Eingabe und Bereichsbindung

- Eingabe: `WP-XE164-127/hit_files/usr/bin/codesys3`
- Größe: 5,181,396 Byte — **PASS**
- SHA-256: `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` — **PASS**
- REA `open_binary` identifizierte ein ELF/ARM-Ziel; `binary_overview` meldete Image Base `0x10000`, `.text` bei VA `0x7cb10` bis `0x344fc0`. Evidence: `ev_18da7f5b5afc61b65f731f9bc7f3b6ca14ec647f001fc860b43950422bced81c` (analysis profile digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`).
- GNU `readelf` 2.44: `.text` `PROGBITS`, VA `0x0007cb10`, Datei-Offset `0x0006cb10`, Größe `0x002c84b0`, `AX`.
- Gebundene Übersetzung: Datei-Offset = ELF-VA − `0x10000`. Damit deckt VA `[0x180000,0x280000)` exakt Datei-Offsets `[0x170000,0x270000)` ab; beide Grenzen liegen innerhalb des dateigebundenen `.text`.

## Methode, Gap und Abdeckung

REA wurde zuerst verwendet. Der konkrete beobachtete Gap: die verfügbaren REA-Abfragen boten entweder eine Funktion, eine einzelne Instruktionsadresse oder Bytes, aber keine bereichsvollständige Instruktions-/Datenflussabfrage für diesen 1-MiB-Bereich; der REA-objdump-Aufruf stellte keine Start-/Endbereichsparameter bereit. Daher wurde der in der Assignment erlaubte lokale Fallback einmalig verwendet: GNU ARM objdump 2.44, `-D -z -j .text --start-address=0x180000 --stop-address=0x280000`.

Der disassemblierte Strom enthält genau 262,144 32-Bit-Wörter an jeder Adresse von `0x180000` bis `0x27fffc`, ohne Lücken. `-D -z` decodiert alle Bytes des ausgewählten Abschnitts linear als A32; es gibt in den verfügbaren Symbolen keine `$a/$t/$d`-Mapping-Symbole. Dies gewährleistet Byte-/Bereichsabdeckung für die deklarierte Methode, beweist aber nicht, dass jedes Wort tatsächlich ausführbarer Code statt eingebetteter Daten ist. GNU `objdump -d` ließ acht 8-Byte-Bereiche aus; deshalb wurde zur Vollständigkeit `-D -z` verwendet. Die acht ausgelassenen Offsets lagen innerhalb des gewählten Bereichs und wurden in `-D -z` als Wörter mitdekodiert.

Der Validator prüft Eingabeidentität, Sektionsbindung, lückenlose Wortabdeckung, Trefferzahlen und die im Folgenden adressgebundenen Inventare. Die Kandidatensuche startet an jedem sichtbaren `ldr` mit `[base,#0x20]`, folgt direkter bedingter und unbedingter Branch-Zielkante sowie Fallthrough, verfolgt einfache `mov`-Kopien und stoppt an Calls. Sie wertet keine Call-Zielwirkung aus und propagiert keine Registerwerte über opaque Calls. Der Validatorstatus ist **PASS**.

## Kandidateninventar

Im linearen A32-Dekodierstrom wurden 686 `blx`-Instruktionen, 459 `ldr`-Instruktionen und 8 `ldrd`-Instruktionen mit Operand `[Register,#32]` gefunden (467 entsprechende Load-Wörter insgesamt). Die vollständige direkte Branch-/Fallthrough-Suche ergab 23 sichtbare `ldr [base,#32]` → `blx`-Ketten: die bisher inventarisierten 22 plus die unten markierte Kette mit direktem Branch zwischen Load und BLX. Die Adressen sind jeweils ELF-VA; Datei-Offset erhält man durch Subtraktion von `0x10000`.

| Lade-VA | BLX-VA | Zielregister | Sichtbarer r0-Wert bei BLX | Ausschluss |
|---|---|---|---|---|
| `0x187edc` | `0x187ef0` | `r5` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x188004` | `0x188010` | `r5` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x189764` | `0x189770` | `r3` | `ldr r0,[r0,#8]` | kein sichtbares `r0=15` |
| `0x189a94` | `0x189aa4` | `r7` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x189d70` | `0x189d80` | `r7` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x189e5c` | `0x189e70` | `r7` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x189fc0` | `0x189fd0` | `r6` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x18c364` | `0x18c374` | `r7` | `ldr r0,[r0,#8]` | kein sichtbares `r0=15` |
| `0x18c51c` | `0x18c528` | `r5` | `ldr r0,[r0,#8]` | kein sichtbares `r0=15` |
| `0x18c7f0` | `0x18c7fc` | `r3` | `ldr r0,[r0,#8]` | kein sichtbares `r0=15` |
| `0x18db3c` | `0x18db48` | `r3` | `ldr r0,[r1,#8]` | kein sichtbares `r0=15` |
| `0x18e308` | `0x18e314` | `r3` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x18e76c` | `0x18e778` | `r3` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x18eb94` | `0x18eba4` | `r5` | `ldr r0,[r0,#8]` | kein sichtbares `r0=15` |
| `0x18fb9c` | `0x18fba8` | `r3` | `ldr r0,[r1,#8]` | kein sichtbares `r0=15` |
| `0x190d70` | `0x190d78` | `r3` | `ldr r0,[r3]`, danach `[r0,#8]` | kein sichtbares `r0=15` |
| `0x193c5c` | `0x193c68` | `r3` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x19402c` (Datei `0x18402c`) | `0x19343c` (Datei `0x18343c`) | `r7` | `ldr r0,[r2,#8]` bei `0x19342c` | kein sichtbares `r0=15`; Speicherwert **OFFEN** |
| `0x194118` | `0x194128` | `r4` | `ldr r0,[r2,#8]` | kein sichtbares `r0=15` |
| `0x1950e4` | `0x1950f0` | `r5` | `ldr r0,[ip,#8]` | kein sichtbares `r0=15` |
| `0x1a790c` | `0x1a7924` | `r3` | `mov r0,r7` | kein sichtbares `r0=15` |
| `0x1bcbfc` | `0x1bcc08` | `r3` | `mov r0,#260` | kein sichtbares `r0=15` |
| `0x1d5400` | `0x1d5408` | `r3` | `ldr r0,[r0,#8]` | kein sichtbares `r0=15` |

Zusätzlich wurden alle 17 direkten `mov* r0,#15`-Sites im Bereich geprüft. Keine davon liefert den gesuchten Wert sichtbar an ein qualifizierendes indirektes `blx` vor einem opaque Call:

| VA | Lokale Pfadbeobachtung / Ausschluss |
|---|---|
| `0x181328` | anschließend `movt r0,#1`, danach direktes `bl` — r0 ist nicht mehr 15; kein `blx` |
| `0x181484` | anschließend `movt r0,#1`, danach direktes `bl` — r0 ist nicht mehr 15; kein `blx` |
| `0x187054` | bedingtes `movlt`; Pfad zum Epilog bei `0x1870f0`, kein `blx` |
| `0x1a75bc` | Rückkehr-Epilog |
| `0x1aeb60` | Rückkehr-Epilog |
| `0x1aebec` | Rückkehr-Epilog |
| `0x1c8b9c` | anschließend `movt r0,#1`, dann direkter `bl`-Aufruf |
| `0x1cdf0c` | Tail-Branch zu `0x184368`; Zielpfad überschreibt/speichert r0 und trifft zuerst einen opaque direkten `bl`-Aufruf |
| `0x1cdf30` | Tail-Branch zu `0x184138`; Zielpfad überschreibt/speichert r0 und trifft zuerst einen opaque direkten `bl`-Aufruf |
| `0x1d6bb0` | nach opaque direktem `bl` bei `0x1d6ba8`, anschließend Epilog |
| `0x1e0f3c` | anschließend `movt r0,#1`, direkter `bl`-Aufruf |
| `0x1e7764` | Rückkehr-Epilog |
| `0x1f17d4` | Rückkehr-Epilog |
| `0x1fcfb4` | anschließend `movt r0,#1`, direkter `bl`-Aufruf |
| `0x211af4` | bedingte Folge überschreibt r0 vor direktem `bl`; andere Kante speichert r0 und setzt vor einem weiteren direkten `bl` neues r0 |
| `0x21a848` | Rückkehr-Epilog |
| `0x237394` | speichert r0 nach `[r9,#16]`, danach Branch zum Epilog `0x2360dc` |

Die 17 Fundstellen sind nicht alle notwendigerweise Instruktionen in erreichbarem Code: die Methode ist eine lineare Dekodierung über den vollständigen Bytebereich. Die Pfad-Ausschlüsse oben beruhen auf den sichtbar dekodierten lokalen Instruktionen und Verzweigungen; es wurde keine allgemeine Pfad-/Wertanalyse behauptet.

Die zusätzlich entdeckte Kette ist adressgebunden wie folgt: Datei-Offset `0x18402c` / ELF-VA `0x19402c`: `ldr r7,[r3,#32]`; `0x194030`: direkter unbedingter Branch zu `0x19342c` (Datei-Offset `0x18342c`); dort `ldr r0,[r2,#8]`, gefolgt von `mov r3,r6`, `sub r2,fp,#300`, `mov r1,r9`; `0x19343c` (Datei-Offset `0x18343c`): `blx r7`. Damit ist der indirekte Zielwert sichtbar aus `[r3,#0x20]` geladen und über den direkten Branch erhalten. Für `r0` ist an dieser Stelle nur die Speicherladung sichtbar; der Speicherwert ist **OFFEN**, nicht statisch `15` belegt.

## Alternativerklärung und Restunsicherheit

**HYPOTHESE:** Ein entsprechender Laufzeitwert könnte aus Speicher stammen, durch eine andere nicht inventarisierte Berechnungsform entstehen, oder in einem anderen Bereich liegen. Insbesondere beweist ein `ldr` des r0-Arguments keine Laufzeitkonstante; der Speicherinhalt wurde nicht hergeleitet.

**OFFEN:** Ob eine der indirekten Aufrufstellen bei realer Ausführung mit `r0=15` erreicht wird, sowie semantische Rollen, ABI-/Struct-Bedeutungen und Datenwerte. Keine Laufzeit-, Geräte-, Netzwerk- oder VM-Beobachtung wurde vorgenommen. Der Nullbefund ist auf A32-32-Bit-Wortdekodierung im benannten file-backed Bereich sowie die expliziten sichtbaren Ziel- und r0-Setups begrenzt; keine Registerwerte werden über opaque Calls propagiert.

## Validator

Ausführung: `python3 validate.py` — **PASS** (siehe `validator-result.txt`). Der Validator kontrolliert Hash und Größe der Eingabe, `.text`-Grenzen, affine VA/Datei-Offset-Zuordnung, lückenlose A32-Wortabdeckung, entdeckt selbst die 23 Ziel-Lade-/BLX-Ketten über direkten Branch/Fallthrough und prüft das vollständige Inventar gegen die adressgebundenen Zeilen. Alle 17 direkten `mov* r0,#15`-Stellen bleiben separat geprüft. Eigenprüfung; kein unabhängiger Review behauptet.
