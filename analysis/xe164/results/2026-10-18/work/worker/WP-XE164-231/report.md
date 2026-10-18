> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-231 — Eingangsobjekt `+0x20` und indirekte Aufrufe in `CMInitComponent`

## Identität, Methode und Adressdomäne

**VERIFIZIERT** — Eingabe `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-127/hit_files/usr/bin/codesys3`, 5.181.396 Byte, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.

**VERIFIZIERT** — REA 6.5.0 / Ghidra 12.1.4 (ARM) lieferte `analyze_function` Evidence `ev_533d81cd32b566a04525860f9ffbb2f4f6bc503b1f91d9b8d0490585ced9674e` und vollständige Instruktionen in `read_function_instructions` Evidence `ev_ff0e5973f3593f094462d926343b86f650489c73d4dad473fe21aa776babd86c`. Der exakte Dynsym-Einstieg ist `CMInitComponent`, VA `0x301394`, Größe 1316 (`0x524`) Byte, inklusive Ende `0x3018b7`, exklusives Ende `0x3018b8`; dies stimmt mit dem beauftragten Bereich überein. Der Funktionskörper ist als ein zusammenhängender Ghidra-Adressbereich gemeldet.

**VERIFIZIERT** — ELF-Metadaten wurden mit GNU `readelf` (GNU Binutils for Debian 2.44) geprüft.

**VERIFIZIERT** — `readelf` meldet ELF `EXEC`, erstes relevantes `PT_LOAD` mit Offset `0x000000`, VA `0x00010000`; für den Funktionsbereich gilt die Segmentabbildung `VA = Datei-Offset + 0x10000`, also VA `0x301394` ↔ Datei-Offset `0x2f1394`. Diese Abbildung ist nur die ELF-Adressdomänenprüfung; die Analyseadresse wurde nicht durch Addition einer angenommenen Image-Base konstruiert. Ein Disassembler-Fallback war nicht nötig: REA lieferte sowohl den kompletten Körper als auch die Rohinstruktionen.

## Vollständige `+0x20 → blx`-Inventur

`r4` wird bei `0x3013ac` aus Eingangs-`r0` kopiert und dient danach als sichtbarer Basisalias. Die Tabelle zählt statische Load-zu-Aufruf-Pfade; zwei Aufrufstellen haben je zwei alternative sichtbare Loads. Registerwerte werden über keinen der undurchsichtigen Aufrufe fortgeschrieben. „Status“ bezeichnet hier ausschließlich den bei `+0x2c` geladenen 16-Bit-Rohwert, keine Feldsemantik.

| Load → Aufruf | Zielregister/Quelle | Sichtbare `r0`, `r1`, `r2`, `r3` unmittelbar vor `blx` | Direkt sichtbare Nachaufrufverwendung | Lokales Gate / Relation |
|---|---|---|---|---|
| `0x301474 ldr r5,[r4,#0x20]` → `0x301488 blx r5` | `r5` aus Eingangsobjekt `+0x20` | `r0=2`; `r1=r11-0x20` (durch `sub r1,r11,#0x20`); `r2` = zuvor berechneter 0/1-Temp aus Statusprüfungen; `r3` = halfword aus `[r4+0x2c]` | `0x30148c` lädt Status erneut; `0x3014a4 cpy r5,r0` hält Post-Call-`r0` lokal; `0x3014a8 bhi 0x3018ac` | Vorher `0x301470 bhi 0x301528` kann den ersten indirekten Aufrufpfad umgehen; danach `0x3014a8` kann den weiteren Pfad umgehen. `r0=2` ist nur der beobachtete Literalwert. |
| `0x3014ac ldr r6,[r4,#0x20]` → `0x3014c0 blx r6` | `r6` aus `+0x20` | `r0=3`; `r1=r2`; `r2` = Status-Temp; `r3` = erneut geladener Status-halfword | `0x3014c4` lädt Status erneut; `0x3014e0 cpy r6,r0`; anschließend `cmp r5,#0`, `cmp r2,#0` und bedingte Pfade | `0x3014b0 cmp r6,#0`; Nullpfad `beq 0x301800`. Vorheriges Ergebnis in `r5` bleibt erhalten; aktuelles `r0` wird nicht als ABI-Rückgabe bezeichnet. |
| `0x3015ac ldr r5,[r4,#0x20]` → `0x3015c4 blx r5` | `r5` aus `+0x20` | `r0=7`; `r1=0`; `r2=0`; `r3` = Status-halfword aus `0x3014c4` | `0x3015c8` lädt Status erneut; `0x3015e4/0x3015e8` wählen `r5` aus gespeichertem `r6` oder aktuellem `r0` | `0x3015b0 cmp r5,#0`; Nullpfad `beq 0x301884`. Danach `cmp r2,#0`, bedingter Sprung zu `0x30152c`. |
| `0x3015f4 ldr r6,[r4,#0x20]` → `0x301608 blx r6` | `r6` aus `+0x20` | `r0=4`; `r1=r2`; `r2` = Status-Temp; `r3` = Status-halfword | `0x30160c` lädt Status erneut; `0x301628` prüft gespeichertes `r5`; `0x30162c` prüft neu berechnetes `r2` | `0x3015f8 cmp r6,#0`; Nullpfad `beq 0x301734`. Danach je nach den beiden lokalen Vergleichen Zweige zu `0x301754` bzw. `0x301898`. |
| `0x301634 ldr r6,[r4,#0x20]` **oder** `0x30175c ldr r6,[r4,#0x20]` → `0x301650 blx r6` | `r6` aus `+0x20`; zweiter Load erreicht über Rücksprungpfad | `r0=0x1f4`; `r1=0`; `r2=0`; `r3` = Status-halfword | `0x301654` lädt Status erneut; `0x301670 cpy r6,r0` hält Post-Call-`r0`; danach `bne 0x3017a8` oder Status-Temp-Gate | Primär `0x301638 cmp r6,#0; beq 0x301870`; Alternativroute `0x30175c` → `0x301764 bne 0x301644` → Call. Nachaufruf-Gates bei `0x301674` und `0x301678`. |
| `0x301680 ldr r5,[r4,#0x20]` → `0x301698 blx r5` | `r5` aus `+0x20` | `r0=5`; `r1=0`; `r2=0`; `r3` = Status-halfword | `0x30169c cmp r6,#0`; `0x3016a0 ldrh r3,[r4,#0x2c]`; danach bedingte Statusberechnung | `0x301684 cmp r5,#0`; Nullpfad `beq 0x301824`. `bne 0x301784` omits later setup path. |
| `0x3016bc ldr r5,[r4,#0x20]` → `0x3016d4 blx r5` | `r5` aus `+0x20` | `r0=6`; `r1=0`; `r2=0`; `r3` = Status-halfword aus `0x3016a0` | `0x3016d8` lädt halfword nach `r2`; `0x3016f4 cpy r7,r0` hält Post-Call-`r0`; nach Berechnung folgen Zweige bei `0x3016f8/0x3016fc` | `0x3016c0 cmp r5,#0`; Nullpfad `beq 0x301848`. Danach lokale Vergleiche können zu `0x3017c8` oder `0x301858` verzweigen. |
| `0x301704 ldr r3,[r4,#0x20]` **oder** `0x3017d4 ldr r3,[r4,#0x20]` → `0x30171c blx r3` | `r3` selbst ist Zielwert aus `+0x20`; zweiter Load erreicht über Rücksprungpfad | `r0=0x3e8`; `r1=0`; `r2=0`; `r3=Zielwert` (durch Zielregister belegt, kein separater `r3`-Argumentwert) | `0x301720 cpy r5,r0`; dann `cmp r7,#0` und `beq 0x3014f8`, sonst `cpy r5,r7` | Primär `0x301708 cmp r3,#0; beq 0x301858`; Alternativroute `0x3017d4` → `0x3017dc bne 0x301710` → Call. |

Damit sind acht unterschiedliche `blx`-Stellen und zehn `+0x20`-Loadpfade abgedeckt. Diese Zählung behauptet keine dynamische Aufrufreihenfolge.

## Kontrollfluss rund um den `r0=2`-Aufruf

**VERIFIZIERT** — Lokale Instruktionsrelation, nicht Laufzeitreihenfolge: Am Funktionseinstieg wird `r0` in `r4` gesichert (`0x3013ac`). `cmn r0,#1` mit anschließendem `beq 0x301798` bildet einen frühen Pfad. Auf dem anderen Pfad liest `0x3013b8 ldrh r3,[r0,#0x2c]`; `cmp r3,#2` mit `movne r5,#1` und `beq 0x3013d4` führt bei Nichtgleichheit zum Returnpfad `0x3013c8–0x3013d0`. Danach läuft der lokale Listen-/Vergleichscode bis `0x301458`.

**VERIFIZIERT** — Am `0x301458` wird `[r4+0x2c]` erneut geladen und in `r3` gehalten; `r2` erhält Rechen-/Vergleichstemp-Werte. `0x301470 bhi 0x301528` kann den ersten indirekten Aufrufpfad überspringen. Auf dem nicht überspringenden Pfad lädt `0x301474` `[r4+0x20]` in `r5`, `0x301478 cmp r5,#0` verzweigt bei Null zu `0x3017e4`; nur im verbleibenden Pfad werden `r1=r11-0x20` (Instruktion `sub r1,r11,#0x20`), `r0=2` gesetzt und bei `0x301488` `blx r5` ausgeführt. Direkt danach folgt Status-Reload/Berechnung, Sicherung des sichtbaren Post-Call-`r0` in `r5` und das Gate `0x3014a8 bhi 0x3018ac`.

**VERIFIZIERT** — Im Körper sind vor diesem Aufruf außerdem die Einstiegstore sichtbar: der frühe Vergleich von Eingangs-`r0` gegen `-1` und der Vergleich des halfword bei `+0x2c` mit numerisch `2`. Die gezeigten direkten Zweige belegen lokale Kontrollrelationen, aber keine tatsächliche Laufzeitpfadwahl.

**HYPOTHESE** — Die Folge ist mit mehreren zustandsabhängigen Callback-Aufrufen vereinbar. Eine solche funktionale Einordnung geht über die beobachteten Register-/Kontrollflussfakten hinaus und ist nicht erforderlich, um `r0=2` zu dokumentieren.

**OFFEN** — Bedeutung von `r0=2`, `r0=3`, `0x1f4`, `0x3e8`, Statuswerten, Stackadresse und geladenem Zielwert; jede Benennung als Initialisierungssemantik, Funktionssignatur, Struct-Layout oder ABI-Vertrag; Verhalten der indirekt aufgerufenen Ziele; dynamische Reihenfolge und tatsächlich ausgeführte Gates.

**OFFEN** — Ghidra meldet acht Calls ohne auflösbares Ziel in der Callee-Beziehung. Das ändert die acht sichtbaren `blx`-Instruktionsstellen nicht, begrenzt aber Aussagen über deren Zielidentität.

## Beobachtung, Schlussfolgerung, Alternativerklärung

**VERIFIZIERT (Beobachtung)** — Vollständiger Ghidra-Funktionsbereich `[0x301394,0x3018b8)`, 329 A32-Instruktionen gemäß Funktionsevidenz; alle direkten Ladeformen `[r4,#0x20]` und die dazu sichtbaren `blx`-Register sind in der Tabelle aufgeführt. `r4` ist der im Körper etablierte Alias des Eingangsregisters.

**VERIFIZIERT (begrenzte Schlussfolgerung)** — Innerhalb dieses vollständigen statischen Körpers gibt es acht `blx`-Stellen, denen insgesamt zehn sichtbare Loads aus Eingangsobjekt `+0x20` zugeordnet sind. Die gezeigten Argumentregisterwerte beschreiben ausschließlich den jeweiligen lokalen Instruktionszustand vor dem Call; nach einem undurchsichtigen Call wird kein Caller-saved Registerwert fortgeschrieben. Post-Call-`r0` wird lediglich als lokal sichtbarer Wert beschrieben.

**HYPOTHESE (Alternativerklärung)** — Der gleiche sichtbare Code kann abhängig von unbekannten Eingabedaten, globalem Listeninhalt und Call-Ergebnissen unterschiedliche lokale Pfade nehmen; das disambiguieren statische Bytes nicht.

**OFFEN (Restunsicherheit)** — Keine Runtime-, Callee-, DSO-, Hardware- oder Feldsemantik untersucht. Keine Behauptung zu ausgeführten Aufrufen oder ihrer dynamischen Reihenfolge. REA-Ausgabe ist Ghidra-Disassembler-/Decompiler-Evidenz und kann interpretative Artefakte enthalten; für die Tabelle wurde nur die Instruktionsrepräsentation und kein dekompilierter Funktionsvertrag verwendet.

## Validator und Manifest

**PASS** — `validate.py` prüft Eingabehash/-größe, Dynsym-Start/Größe, die ELF-`PT_LOAD`-Adressabbildung, acht eindeutige Callstellen, zehn explizit erfasste `+0x20`-Loadpfade einschließlich der beiden alternativen Routen, die tabellierten Register-/Nachlaufkontexte, die gezielte `r0=2`-Gatefolge und die self-reference-freien Hashes in `manifest.sha256`.

**PASS** — Der Validator ist ein nachgelagerter Konsistenzcheck der protokollierten REA-Evidenz und `readelf`-Metadaten; er startet weder Zielcode noch Geräte-, Netzwerk- oder VM-Zugriffe und verwendet keinen Disassembler-Fallback.
