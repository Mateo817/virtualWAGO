> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-090 — begrenzter Kontroll-/Datenfluss und Init-Publikation

## Ergebnis

**VERIFIZIERT:** Das Ghidra-Verfahren bei Adresse `0x124e4` hat als beobachteten Körper die inclusive Range `0x124e4..0x12607` (292 Byte). Der Start ist per Ghidra-Source-Mapping ELF-VA `0x24e4` = Dateioffset `0x24e4`; das letzte Maschinenwort beginnt bei Dateioffset `0x2604` und endet bei `0x2607`. Damit endet der Körper exklusiv bei `0x2608`. Ghidra meldet 15 Basic Blocks. Keine Anweisung oder kein Byte ab Dateioffset `0x2614` wurde in das Evidence-Bundle aufgenommen.

**VERIFIZIERT:** In `IoDrvKbus_Init` wird der Kandidatenwert PC-relativ gebildet, in den Stack-Lane-Offset `+0x1c` geschrieben, ab `sp+0x18` in Vektorregister geladen und als zweites 32-Bit-Element eines gepackten Stores nach `r0+0x630` publiziert. Das belegt einen statischen Datenfluss zur Displacement-Position, keine Ausführung als Callback.

## Identität, Koordinaten und Werkzeuge

Eingabe: `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvKbus.so.0.0.1`, 38 584 Byte. Vor Analyse geprüft: SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`.

| Koordinate | Befund |
|---|---|
| ELF-VA des Kandidaten | `0x24e4..0x2607` inclusive; letzter Instruktionsanfang `0x2604`; Ende exklusiv `0x2608` |
| Ghidra-Adresse | `0x124e4..0x12607` inclusive; in diesem geladenen Image `Ghidra = ELF-VA + 0x10000` |
| Dateioffset | Start `0x24e4`; Pool `0x2608..0x2613`; kein Mapping zu Laufzeit- oder Hardwareadresse behauptet |
| Laufzeit-/Hardwareadresse | OFFEN; statische ELF/Ghidra-Mappings legen sie nicht fest |

REA wurde zuerst verwendet: Ghidra `12.1.4`, Architektur ARM little-endian, Analyseprofil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Das Evidence-Bundle stammt aus einer frischen, nach Abschluss geschlossenen REA-Sitzung. REA gibt `procedure_assembly` unpaginiert zurück; als dokumentierter Fallback wurde `/usr/bin/arm-linux-gnueabihf-objdump` GNU Binutils `2.44` nur zum Suchen nach einer unmittelbaren `#0x630`-Form im begrenzten Initializer-Adressraum `0x147fc..0x15320` benutzt. Diese Textsuche ergab keinen Treffer; daher stützt sich die Tabelle unten ausschließlich auf die fokussierten Ghidra-Instruktionsbeobachtungen. Kein readelf/objdump-Ergebnis wird als Evidence behauptet.

## Kandidatenkörper: fokussierte Instruktions- und Kontrollflusstabelle

Die vollständige von Ghidra gelieferte Instruktionsliste und der vollständige CFG sind in `rea-session-evidence.json`, Evidence `ev_6704b6900a8f92f0f0ad79312d64c338575e4a6b8c42d84d4488b9e66ce2322b` enthalten. Die folgende Tabelle fokussiert auf Guards, Rückgabekette, Tabellenzugriff und Schleife. Pseudocode ist ausschließlich Ghidra-Ableitung, keine Originalquelle.

| Ghidra-Adresse (ELF-VA) | Instruktionen / Kante | Beobachteter Effekt |
|---|---|---|
| `124e4..1250c` (`24e4..250c`) | Prolog; `cmn r0,#1`; bedingte Vergleiche von `r1`, `r2`, `r3`; Branch nach `12600` | Wenn erster Eingang `-1`, zweiter Eingang null, vierter Eingang null oder dritter Eingang null ist: Pfad setzt `r4=2` und kehrt zurück. |
| `12510..12524` (`2510..2524`) | `ldrh r2,[r1]`; `movw r3,#0x8008`; Vergleich; bei mismatch `r4=0x20` | Vergleicht 16-Bit-Wert an `param_2` mit Konstante `0x8008`; mismatch ergibt `0x20`. |
| `12528..12534` (`2528..2534`) | `movw r0,#0x916`; direkter `bl 0x11fdc`; `subs r4,r0,#0`; Branch falls nicht null | Rückgabe des direkten Calls wird übernommen; ein nicht-null Wert beendet die weitere Kandidatenlogik. Zielkörper nicht untersucht. |
| `12538..1254c` (`2538..254c`) | PC-relativer Literalzugriff, `add r3,pc,r3`, `ldr r3,[r3,#8]`, Test auf null | Nullwert setzt Rückgabekandidat `3`; sonst wird fortgesetzt. Die aus der Instruktion und dem Pool gebildete Adresse ist `0x29204`. |
| `12550..12560` (`2550..2560`) | `r0` erhält `param_2`, `r1=&[sp+4]`; direkter `bl 0x11ddc`; `subs r4,r0,#0` | Call-Rückgabe wird übernommen; nicht-null überspringt den Tabellenpfad. Zielkörper nicht untersucht. |
| `12564..12584` (`2564..2584`) | Stackwert lesen, lokaler Wert minus eins gegen `0xf9` unsigned prüfen; Poolzugriff auf Grenzwert; Vergleich | Zulässigkeitsprüfung entspricht `1 <= lokaler Wert <= 250` sowie `lokaler Wert <= *0x291d0`; Fehlerpfad setzt `0x28`. |
| `12588..125a0` (`2588..25a0`) | `slot-1` mal `0xc00`; PC-relativer Basiswert; `[base + stride + 0x14]` lesen; `str` über `r7` | Der gelesene 32-Bit-Wert wird an die über `param_3` gelieferte Adresse geschrieben. |
| `125a4..125b0` (`25a4..25b0`) | Prüft gelesenen Wert: `value-1 <= 1`; `str r4,[r5]`; andernfalls zum finalen Call | `param_4` wird zunächst auf null gesetzt. Die Wiederholung läuft nur bei Wert `1` oder `2`; sonst wird sie ausgelassen. |
| `125b4..125d8` (`25b4..25d8`) | Indexstart; Load `[base + index*0x20]`; compare mit aktuellem `*param_4`; `strcc`; Index bis `0x60` | 96 32-Bit-Kandidaten werden mit Schrittweite `0x20` gelesen. Ein Wert überschreibt `*param_4` genau dann, wenn er größer ist. Dies ist ein Maximum-Update, keine belegte first-nonzero-Suche. |
| `125dc..125ec` (`25dc..25ec`) | Direkter `bl 0x12074` mit `0x94c`; wenn `r4==0`, übernimmt `r0` den Call-Rückgabewert; sonst bleibt `r4` | Der letzte Call liefert nur dann den zurückgegebenen Wert, wenn zuvor kein nicht-null Rückgabekandidat vorliegt. Zielkörper nicht untersucht. |
| `125f8..12608` (`25f8..2608`, exklusiv) | Fehler setzt `0x28`; gemeinsamer Return; Guard-Pfad setzt `2` | Konstanten `0x28` und `2` kehren über die gemeinsamen Return-Instruktionen zurück. Letzter Instruktionsanfang ist `0x12604` (`0x2604` ELF-VA/Dateioffset). |

### Vollständiger CFG (Ghidra BasicBlockModel)

`end` ist die vom Provider gelieferte Block-Endadresse; die Procedure-Body-Range oben ist separat und inclusive.

| Start | Ende | Successors |
|---|---|---|
| `124e4` | `12500` | `12500`, `12600` |
| `12500` | `12510` | `12510`, `12600` |
| `12510` | `12528` | `12528`, `125ec` |
| `12528` | `12538` | `12538`, `125ec` |
| `12538` | `12550` | `12550`, `125dc` |
| `12550` | `12564` | `12564`, `125dc` |
| `12564` | `12574` | `12574`, `125f8` |
| `12574` | `12588` | `12588`, `125f8` |
| `12588` | `125b4` | `125b4`, `125dc` |
| `125b4` | `125c0` | `125c0` |
| `125c0` | `125dc` | `125c0`, `125dc` |
| `125dc` | `125ec` | `125ec` |
| `125ec` | `125f8` | — |
| `125f8` | `12600` | `125dc` |
| `12600` | `12608` | `125ec` |

Die Tabelle übernimmt die Ghidra-Adressen aus Procedure-Evidence. Zusammen mit `+0x10000` ergeben sich die korrespondierenden ELF-VA/File-Offsets.

## Fokussierter Datenfluss und Rückgabeauswahl

| Quelle / Bedingung | Schreib-/Rückgabepfad | Status |
|---|---|---|
| Eingangsguard | `r4=2` | VERIFIZIERT |
| 16-Bit-Wert ungleich `0x8008` | `r4=0x20` | VERIFIZIERT |
| Direkter Call bei `1252c` liefert ungleich null | Wert bleibt als Kandidat in `r4`; weitere Kandidatenlogik entfällt | VERIFIZIERT |
| Call bei `1252c` liefert null; geladener Grenzwert null | `r4=3`; späterer `12074`-Rückgabewert wird nicht übernommen | VERIFIZIERT |
| Call bei `12558` liefert ungleich null | Wert bleibt als Kandidat in `r4`; Tabellenpfad entfällt, späterer `12074`-Wert wird ignoriert | VERIFIZIERT |
| Call bei `12558` liefert null; Range-Check scheitert | `r4=0x28`; späterer `12074`-Wert wird ignoriert | VERIFIZIERT |
| Call bei `12558` liefert null; Range gültig | Speichert `[base+0x14]` über `param_3`, initialisiert `*param_4=0`; bei Wert 1 oder 2 folgt die 96-Element-Maximumsschleife | VERIFIZIERT |
| Alle vorherigen Werte null | Rückgabe von Call bei `125e0` wird übernommen | VERIFIZIERT |

Die Auswahlmechanik erhält den ersten von null verschiedenen Kandidaten aus den belegten Status-/Callpfaden. Diese Aussage beschreibt die Kontrollfluss-/Registermechanik, keine Bedeutung der Werte. Der Loop-Schreibpfad überschreibt unabhängig davon den Ausgabewert mit jedem strikt größeren gelesenen Wert.

## Literalpool und Init-Publikationslane

Der vollständige Kandidatenpool `0x12608..0x12613` wurde mit genau 12 Byte gelesen. Der direkte Ghidra-Source-Mapping-Befund ist `0x12608 -> Datei 0x2608`; der Kandidaten-Instruktionsanfang `0x12604 -> Datei 0x2604`. Die vier Little-Endian Wörter des Pools sind:

| Ghidra-Adresse | Dateioffset | Bytes / dekodierter Wert | Benutzung |
|---|---:|---|---|
| `12608` | `2608` | `b8 6c 01 00` → `0x00016cb8` | Bei `1253c` zu `0x29204` plus Load-Displacement `8` |
| `1260c` | `260c` | `50 6c 01 00` → `0x00016c50` | Bei `12578` zu `0x291d0` |
| `12610` | `2610` | `2c 7d 01 00` → `0x00017d2c` | Bei `12594` zu Tabellenbasis `0x2a2c8` |

Die dritte Pool-Zeile endet bei Dateioffset `0x2613`; `0x2614` ist exklusiv außerhalb dieser Lesespanne.

**Init-Lane, direkt beobachtete Instruktionen:**

| Ghidra-Adresse | Instruktion / Rohbytes | Lane-Effekt |
|---|---|---|
| `14818` | `ldr r3,[0x15328]` / `08 3b 9f e5` | Liest den 32-Bit-Literalwert bei Ghidra `0x15328`. |
| `14820` | `add r3,pc,r3` / `03 30 8f e0` | PC-relative Bildung; der gelesene Literalwert `0xffffdcbc` ist als signed `-0x2344` interpretierbar. ARM-PC (`Instruktionsadresse+8`) ist `0x14828`; `0x14828 - 0x2344 = 0x124e4`. |
| `14824` | `str r3,[sp,#0x1c]` / `1c 30 8d e5` | Schreibt den so gebildeten Kandidatenwert an Stack-Displacement `+0x1c`. Ghidra meldet am Instruktionsoperand eine DATA-Referenz auf `0x124e4`. |
| `14844` | `vldr.64 d16,[sp,#0x18]` / `06 0b dd ed` | Liest 64 Bit ab `sp+0x18`; der Kandidatenwert bei `sp+0x1c` ist das zweite 32-Bit-Element in `d16` (ARM little-endian). |
| `148dc` | `add r3,r0,#0x620` / `62 3e 80 e2` | Beginn der effektiven Publikationsadresse. |
| `148e0` | `add r3,r3,#0xc` / `0c 30 83 e2` | `r3 = r0 + 0x62c`. |
| `148e4` | `vst1.32 {d16,d17},[r3]` / `8f 0a 43 f4` | Schreibt vier 32-Bit-Elemente sequenziell ab `r0+0x62c`; das zweite, aus `d16` stammende Element liegt bei `r0+0x630` und enthält `0x124e4`. |

Die Ausgabe-Displacement-Herleitung lautet damit `0x620 + 0xc + 4 = 0x630`. Das ist **VERIFIZIERT** als Instruktions-/Datenflussableitung. Die Bezeichnung des Ziels als Feld, Slot, Callback oder Struktur bleibt **OFFEN**.

## Direkte Calls und Grenzen der Aussage

Im Kandidatenkörper sind drei direkte Calls beobachtet: `0x1252c -> 0x11fdc`, `0x12558 -> 0x11ddc` und `0x125e0 -> 0x12074`. Nur Instruktionsadresse, Zieladresse, übergebene Konstanten/Register-/Stackwerte und bedingte Übernahme ihrer Rückgaben werden verwendet. Keine Call-Zielinstruktionen oder -Pseudocode wurden untersucht. Die Initialisierungslane belegt eine gespeicherte Adresse; ein Laufzeitaufruf ist nicht statisch beobachtet.

Ghidra weist die Initialisierungsfunktion bei `0x147fc` als Quelle der Datenreferenz auf den Kandidaten aus. Die finalen Init-Evidence-Records enthalten ausschließlich die sieben explizit gelisteten Instruktionsadressen und die exakt benötigte 4-Byte-Literalprobe bei `0x15328`. Ein Verweis auf den harten Nachbarn wird nicht in das Bundle aufgenommen. Die frühere explorative Suche über `objdump` lieferte keinen direkten `#0x630`-Treffer; sie ist keine Befundquelle.

### Alternativerklärung und Restunsicherheit

Die `+0x630`-Position könnte Teil eines generischen gepackten 16-Byte-Blocks statt eines eigenständigen benannten Funktionsfeldes sein. Die Instruktionen belegen nur die Reihenfolge und Zieladresse des Stores. Auch sind Ghidras Parameter-/Pseudocode-Typen decompiler-abgeleitet; Feldbedeutungen, Call-Zielsemantik, dynamische Load-Basis, Laufzeit- und Hardwareadresse sowie Verhalten bei realer Ausführung bleiben **OFFEN**. Die Statuskonstanten werden daher ohne externe oder FW30-Semantik benannt.

## Evidence-Inventar

Das unveränderte kanonische REA-Bundle `rea-session-evidence.json` enthält 14 Records, 0 Unknowns, 229 504 Byte; SHA-256 `41a89f438660d4196b4e7977170844208e38c85149293bb8cb387b3ef4c1ca8a`.

| Evidence-ID | Operation | Beitrag |
|---|---|---|
| `ev_6704b6900a8f92f0f0ad79312d64c338575e4a6b8c42d84d4488b9e66ce2322b` | `analyze_function` | Vollständige Kandidaten-Instruktionen, Pseudocode-Ableitung, CFG, Calls, Literalreferenzen und High-p-code-Teilfluss |
| `ev_cf613e28e1f0a1cb6c1c14a7c386e38b457aa6d0bd9769798899bef675074321` | `procedure_info` | Procedure-Grenze und 15 Basic Blocks |
| `ev_8e1b0b8ff5262326770c6badeac605e4468e5f76aafb550b51e1b7e559946787` | `address_to_file_offset` | Kandidatenstart `0x124e4 -> 0x24e4` |
| `ev_241909c5cbd137b14ea6b145217e810d9732dc06362b5526977bcc8e85d8c445` | `address_to_file_offset` | Letzter Instruktionsanfang `0x12604 -> 0x2604` |
| `ev_c66f6c7075688bddd50058b822d558128416b57e69c186c80d63a01e8408881f` | `address_to_file_offset` | Literalpoolstart `0x12608 -> 0x2608` |
| `ev_d40393f7c3fdcca5c653ab220a0d6ed56766dcae145b08bbf405f1112d5a4a35` | `read_bytes` | Poolbytes `0x12608..0x12613` |
| `ev_f5387dd99e012d0551a9182666f2c362c617426d2ced58bebe976de5aa4556ae` | `read_bytes` | Init-Literal `0x15328`, vier Byte |
| `ev_4d355865240fa4c148d2265210462f68ca24c9bfac16ed1e9118112fa1fbe04f` | `inspect_native_instruction` | Init-Literal laden bei `0x14818` |
| `ev_fac27d9b38b03d70795d48bd452ac5aca3953e203780c868098bce068b67f8c4` | `inspect_native_instruction` | PC-relative Bildung bei `0x14820` |
| `ev_0c19e06cf7a44894d00f7d6f8bef3e963e1911db394e3d5c08c3c26cbb6edea6` | `inspect_native_instruction` | Stack-Lane und DATA-Referenz bei `0x14824` |
| `ev_3605a1d9d83f95dbf4dd943360fa84f9c94757cd3dee79b7fe3663805ddeaff9` | `inspect_native_instruction` | 64-Bit-Lane-Laden bei `0x14844` |
| `ev_8bbd192c125cf17527f2224c1e60d52c4efd25823e23d570ec853e5dd6e7fd25` | `inspect_native_instruction` | Basis `r0+0x620` bei `0x148dc` |
| `ev_b7b52647bb557c6471e089aef6f9edddb2f89bda16315202ddd719df57c18bac` | `inspect_native_instruction` | Zusatzdisplacement `+0xc` bei `0x148e0` |
| `ev_227edb89be0fc3a2d2f4c279fba4d9c2c4d6646601e5ae9d5ed61fe53435b394` | `inspect_native_instruction` | Gepackter Store bei `0x148e4` |

Alle analysierten Records haben Zielhash `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`. Es gibt im Bundle keine fremden Zielkörper-Analysen und keine Instruction-/Byte-Reads am oder nach dem Dateioffset `0x2614`.

## Tests und Reproduktion

| Test | Status | Grund |
|---|---|---|
| Eingangshash und Eingabegröße | PASS | Vor Analyse geprüft und durch Validator erneut geprüft |
| Procedure-Grenze und Dateioffset-Mapping | PASS | Ghidra-Procedure-Evidence plus drei Source-Mappings |
| Literalpool-Lesespanne | PASS | 12 Byte ab `0x2608`, exklusives Ende `0x2614` |
| Bundle-Scope, Evidence-IDs und Hash | PASS | `validate_bundle.py` |
| Prüfungen/Werkzeugläufe über Scope hinaus | NOT_RUN | Keine unabhängige externe Review behauptet |

Reproduktion im Ausgabeordner:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`validate_bundle.py` prüft Zielidentität, Dateigröße, kanonischen Bundle-Hash, Recordzahl und IDs, Operationen, zulässige Init-Instruktionsadressen, den Kandidatenkörper, Poolspanne und das Fehlen von `0x2614`-Reads/Records. Die Hashes in `SHA256SUMS` decken die endgültigen Bericht-, Bundle- und Validator-Dateien ab.
