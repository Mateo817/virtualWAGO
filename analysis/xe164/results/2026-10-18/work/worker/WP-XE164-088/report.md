> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-088 — begrenzter FW31-Codekandidat

## Ergebnis und Grenzen

**VERIFIZIERT — statischer Umfang:** Die Datei stimmt mit SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` überein und ist 38.584 Bytes groß. Für das ELF-Mapping gilt im ersten `LOAD`-Segment Datei-Offset = ELF-VA; REA bildet diese VA mit Image-Base `0x10000` auf Ghidra-Adresse `VA + 0x10000` ab. Die angefragte Codegrenze ist daher Datei/ELF-VA `0x2eb8..0x313b` (letzte Instruktion bei `0x3138`) und Ghidra `0x12eb8..0x1313b`. Der Literalpool ist Datei/ELF-VA `0x313c..0x3157`, Ghidra `0x1313c..0x13157`; das exklusive Ende ist jeweils `0x3158` / `0x13158`.

**VERIFIZIERT — Procedure-Grenze:** Ghidra dekodiert die Instruktion an `0x12eb8`, meldet für diese Adresse aber `procedure: null`; `resolve_containing_procedure` liefert `not_in_procedure`. `analyze_function(0x12eb8)` wurde einmal versucht und wegen „No procedure exists“ abgewiesen. Deshalb stammt die lineare Instruktionsliste innerhalb der vorgegebenen Grenze aus dem gezielten GNU-objdump-Fallback. Ghidra-Instruktionsbefunde bestätigen wichtige Grenzen, Verzweigungen, Aufrufe und Publikationsinstruktionen. Es gibt keine von Ghidra gemeldete vollständige Function-Body-/CFG-Grenze für den Kandidaten.

**VERIFIZIERT — begrenzte statische Init-Lane:** In `IoDrvKbus_Init` wird an Ghidra `0x14828` ein Wort aus Literaladresse `0x1532c` gelesen. Die vier Bytes dort sind `84 e6 ff ff`, also little-endian `-0x197c`. Die Addition an `0x1482c` verwendet ARM-PC (`ELF-VA 0x4834`) und ergibt `0x2eb8`. Der Wert wird an `0x14830` nach `[sp,#0x20]` geschrieben; Ghidra verzeichnet an genau dieser Store-Instruktion eine DATA-Referenz auf Kandidat `0x12eb8`. `vldr.64 d17,[sp,#0x20]` lädt diese Stack-Lane. Danach berechnen `0x148dc/0x148e0` die Zielbasis `r0+0x62c`, und `vst1.32 {d16,d17},[r3]` schreibt den Registerblock. Unter ARM little-endian Lane-Reihenfolge liegt das Wort aus `[sp,#0x20]` in d17-Lane 0 und wird nach Zielwort `r0+0x634` geschrieben. Das ist eine statische Ableitung der Lane-Adresse, keine Laufzeitbeobachtung und keine Benennung eines Felds oder Callbacks.

Die Init-Beobachtung ist auf diese PC-relative Wertbildung, Stack-Staging und den konkreten VST1-Store begrenzt. Sie beweist nicht, dass der Init-Pfad zur Laufzeit ausgeführt wird oder dass der Store bei jedem Pfad stattfindet. Keine aufgerufene Zielroutine wurde untersucht.

## Adressräume und Identität

| Status | Raum | Bereich / Bezug | Beobachtung |
|---|---|---|---|
| VERIFIZIERT | Datei-Offset | `0x2eb8..0x313b` | Codekandidat einschließlich Instruktion bei `0x3138`; exklusives Ende `0x313c` |
| VERIFIZIERT | ELF-VA | `0x2eb8..0x313b` | Im ersten ELF-LOAD ab Offset/VA 0 identisch zum Datei-Offset |
| VERIFIZIERT | Ghidra | `0x12eb8..0x1313b` | Ghidra-Image-Base `0x10000`; einzelne source mapping evidence vorhanden |
| VERIFIZIERT | Datei-Offset / ELF-VA / Ghidra | `0x313c..0x3157` / `0x313c..0x3157` / `0x1313c..0x13157` | Zugeordneter 28-Byte-Literalpool; keine Candidate-Bytes ab `0x3158` gelesen |
| OFFEN | Laufzeitadresse | nicht beobachtet | Ladebias/Prozessabbild nicht untersucht; nicht aus Ghidra-Adresse ableiten |
| OFFEN | Hardwareadresse | nicht beobachtet | Kein Geräte-, Runtime- oder Hardwarezugriff |

Datei: `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvKbus.so.0.0.1`; Größe `38584`; SHA-256 wie oben. REA/Ghidra bestätigt dieselbe Identität (`ev_dc329bb6e195943fb72af4ef5c2ddf26edea2fa41b384ed240f165c461d67b90`). Adressübersetzung `0x12eb8 -> Datei-Offset 0x2eb8`: `ev_3850aa7da94acfe8251757648b8e0d1738004ca3d1ababfe975f7adc21e20b01`. Pool-Übersetzung `0x1313c -> Datei-Offset 0x313c`: `ev_3a61f059717aeda44ce67befd148bc68c56b0c3653ac7b213897c7f89af8d58c`.

## Werkzeugversionen und Vorgehen

| Status | Werkzeug | Version / Nutzung |
|---|---|---|
| VERIFIZIERT | REA CLI / MCP | `rea 6.5.0`; zuerst für ELF-Öffnung, Ghidra-Instruktionsprüfung, Adressübersetzung und Evidence-Export |
| VERIFIZIERT | Ghidra | `12.1.4`, ARM:LE:32:v8, Image-Base `0x10000` |
| VERIFIZIERT | GNU objdump | GNU Binutils `2.44`; gezielter Fallback nur wegen Ghidra-`not_in_procedure` am Kandidaten; Disassembly begrenzt auf `--start-address=0x2eb8 --stop-address=0x313c`, Literalpool auf `0x313c..0x3157` |
| VERIFIZIERT | GNU readelf | GNU Binutils `2.44`; `readelf -lW`, nur zur Bestätigung des LOAD-Source-Mappings |

Der GNU-Fallback war konkret erforderlich, weil Ghidra die angefragte Adresse als Instruktion dekodiert, aber keine Procedure dafür bereitstellt und `analyze_function` deshalb keine Function-Body-/CFG-Antwort liefern konnte. Die abgewiesene Operation wurde nicht wiederholt. Der Fallback endet vor dem Literalpool; der separate Datendump ist genau 28 Bytes. Nach dem ersten vorläufigen Bundle-Export wurden zehn weitere fokussierte REA-Instruktionsbeobachtungen für Status-/Call-Sites und die candidate-spezifische Init-Lane in dieselbe laufende Session aufgenommen und der Export neu erstellt. Die finale, unveränderte Datei `rea-evidence.json` enthält `137` Records und `0` Unknowns, umfasst `688250` Bytes und hat SHA-256 `a20bfb32dc55a85abdce9c98e3b949a2767074b2e474464292e19c673723f7d4`.

## Adressgebundene Instruktionsbeobachtungen

Adressen in der Tabelle sind Ghidra-Adressen. ELF-VA und Datei-Offset ergeben sich durch Abzug von `0x10000` in diesem ersten LOAD-Segment. Die Instruktionstexte sind disassembler-/providerseitige Darstellung, kein Originalquelltext. Für die vollständige begrenzte lineare Disassembly siehe Fallback-Kommando und Toolgrenze oben; die fokussierten Belege unten sind direkt im REA-Export enthalten.

| Status | Ghidra-Adresse | Instruktion / Datenbezug | Wirkung im begrenzten Datenfluss | Evidence |
|---|---:|---|---|---|
| VERIFIZIERT | `0x12eb8` | `subs r2,r2,#2` | Eintrittsflags aus Registerwert minus 2 | `ev_c276b44f9b7f78688c283a46c289bd8d800d92599f71e66dd3828f79c6718c52` |
| VERIFIZIERT | `0x12ee0` | `movne r0,#2` | Setzt `r0=2` auf nichtgleichem Entry-Guard-Pfad | `ev_f83e127dd95ac8219bff0d5a6654b6d8ab28ea8ea33ccbc7a801880638e9e29d` |
| VERIFIZIERT | `0x12ee8` | `bne 0x130ec` | Entry-Guard-Fehlerpfad überspringt Kandidatenkern und geht zum Epilog | `ev_7a8eb807e22565ed9a1c817d7edad2f27eeb43f281cd56c305157505428b9de1` |
| VERIFIZIERT | `0x12efc` | `bhi 0x13134` | Frühe unsigned Grenzprüfung | `ev_bf6a80c0216073dcc397f6c82412a6977194c9e4ffa038fe51839ac9115cfa28` |
| VERIFIZIERT | `0x12f10`, `0x12f20` | `bne 0x1312c` | Zwei Header-/Markervergleiche führen auf gemeinsamen Statuspfad | `ev_43dad9592b4f7d67634f9a71c2ac1705ba2105f23c184020a08aeafaf3a8f5ca`, `ev_badfb82f0f2ded01b2bcf16ca2d01799ae0220f7f12c4872e159f6841dd24c57` |
| VERIFIZIERT | `0x12f2c` | `beq 0x130e8` | Bit-Test-Fehler führt zur bereits gesetzten Status-Rückgabe | `ev_058fc5817b383c7dbe3496548e2b4d7fc15851cf418f61915ed6384cc616055b` |
| VERIFIZIERT | `0x12f64`, `0x12f70`, `0x12fa8`, `0x12fb0` | `blx r2/r3/r3/r11` | Indirekte Call-Sites; Ziele und Semantik nicht untersucht | `ev_3643c5d2679ca39d5181801b9597083ffaa862a456af1e174dd18db8ec64dcd8`, `ev_73fc720889358ab1b575916077d52ae0c9afdb017c5ef9a3420c5faa857976f9`, `ev_267ff2c52812c0bd31e0be0281be4fdefcf600754edbdc35b0bd8af364bb02c1`, `ev_b3f75bcd0859660cfe0bc549744df3b1726b56fc93590450b0f8ab2655767777` |
| VERIFIZIERT | `0x12f8c`, `0x12f90` | `streq r11,[sp,#8]`; `beq 0x130e8` | Bedingtes Statussetzen auf 1, dann ggf. Epilog | `ev_06fb91b25aed3b9186ca2df58212fa77342ba9cc0e150773f226a037b445a023`, `ev_38988136bac9122c40f78fd6e952854544f027c390ae80b38449c334f8566cde` |
| VERIFIZIERT | `0x12fc0`, `0x12fd0`, `0x12fe4` | `bne 0x13124`; `bhi 0x13120`; `bhi 0x13120` | Stackstatus 2 bzw. Grenzfehlerpfad | `ev_9fe819a505fe47b2cb3cb223b431e5580c36687cf26f13baa903d90129ade962`, `ev_27707fc5c9a99e8d0f703959f8f32d1bcc117f9baab568825af5995f634b5be6`, `ev_288eb688409a0d230fdb23c2b78306f7c0e4c3a1c187c676e7082f6075c19640` |
| VERIFIZIERT | `0x12ff8` | `movw r0,#0x9a6`; folgt `bl 0x11fdc` an `0x12ffc` | Direkter Call-Site, Zielkörper ausgelassen | `ev_e1121de22df2b61a59e73901d747521400dc56b083941698b85b3ea5f68293f4`, `ev_d69abcd0b52cbbf102b5af1ad5ae1d5bf6c25ceaff36b16b51ad8ad05afde8952` |
| VERIFIZIERT | `0x13004` | `str r0,[sp,#8]` | Speichert Resultat des vorigen direkten Calls als Stackstatus | `ev_2dd7c861444d919b52440bb3eeba56b63e2f259d6e659430c251b939cf138561` |
| VERIFIZIERT | `0x13024`, `0x1302c`, `0x13034`, `0x1303c` | Branches zu `0x13114`, `0x130fc`, `0x130d4`, `0x130d4` | Drei aus dem geladenen Zustandswort abgehende Fälle; Bedingungsziele im CFG | `ev_776962cc92d6bbe2711779071f1e48b47bc661164891a8462fe7cd431277d0a5`, `ev_432b9171db4d50e6afa182f907fb9ce0dabf983968ef775c3bd6e4b0e512dc22`, `ev_e7801af3885cbe35f6db7cbe30235d1c41f7ba9caafb688cb57ee70454fee9fd`, `ev_48d1ded5b78e6acd0423632decf8203ea65c6480b1eb5d6e62a9bfa2d5eb3cc5` |
| VERIFIZIERT | `0x13058`, `0x13060`, `0x13090` | `blx r3`, `blx r4`, `blx r8` | Indirekte Call-Sites; Ziele und Semantik nicht untersucht | `ev_3b68fc3c7a72b01a47ebf35bcebd2b9f73a8d5acb3214c6460a33e0f0539beea`, `ev_755f3d2019ea2f84cb296a45223eee014992425708ba1b3e40b1ac4dfcba7b03`, `ev_e2cc911207bff8d76a5aefb93852ff38ff2423830009987ac52f6fe742af1bdf` |
| VERIFIZIERT | `0x1309c`, `0x130a8`, `0x130bc` | Branches zu `0x130f4`, `0x130f4`, `0x130d0` | Validierungsfehler-/Resultatpfade | `ev_f9d8751969d52620de575a42035a7a5387e1fb0545adbbc17e467fc56980f237`, `ev_d73099c5ce4df03359b2b41038bc6b0d8c08de67dc12c936f7d89d8feb127653`, `ev_b70d1c452c89ab78da5d1b519e677feb02439e0d7820b5ae6d82381aba7b3984` |
| VERIFIZIERT | `0x130cc`, `0x130d8`, `0x13108` | Direkte `bl` zu `0x1277c`, `0x12074`, `0x11d40` | Call-Sites dokumentiert; Zielkörper ausgelassen | `ev_8760fc6594b13842515c3d0c114eabb033ab61fd84615bbcd60880020e45294d`, `ev_63fe3866db193696c1c42135e2124b129e5552fa5588af45be787114e149cacb`, `ev_8548e887d3263bb15c540950a34799d4d08a04c7b52077324c586c8d121d7edc` |
| VERIFIZIERT | `0x130f4`, `0x13114`, `0x13120`, `0x1312c`, `0x13134` | `r0=40`, Statusworte `r3=39/2/32/20` | Konstante Zuweisungen; `0x13124` schreibt `r3` nach `[sp,#8]` | `ev_76e7ff39340457d79f9340fe6254244c3abf502f2cdc8656e0f1ed8c3c7381ff`, `ev_47ea1013547689fdab4b26e7ffe48f177c6a8d1a853407168ede879ac462bd71`, `ev_b80e754a1d3a81b74c41c388fc1e4c51f15ed9a22588a81b7588d46dcc58fed7`, `ev_713eaf8e07823d6071ddb037de6b646207783ca050743f2ecd239188c0204f7c`, `ev_6f5cfc379d9ec9c366dc7a560b194da5d1db712b277f4bd3254fb568fe726046`, `ev_efd561346c6156f5bd46283d15b73e88cf4594991fe6965fe80d320e55a5ed5b` |
| VERIFIZIERT | `0x130e8`, `0x130ec`, `0x130f0` | `ldr r0,[sp,#8]`; Stack freigeben; `ldmia ... pc` | Gemeinsamer Rückgabepfad, Ghidra klassifiziert `0x130f0` als RETURN | `ev_c0a48b8da65b22bc096a06cd23c77e58208adb06dbff711dbaeb31918151e147`, `ev_4ba59fc30d47f754ba96b82c86cddab5b3d2e814b1e19eaf918de7f6128ce537`, `ev_d97b236b81b2211e974394fb4710cc9b0155db56a2c315d4699f81b7c36ed630` |

## CFG und begrenzter Datenfluss

| Status | Start / Bedingung | Ziel / Effekt | Evidence |
|---|---|---|---|
| VERIFIZIERT | Eintritt: `subs r2,r2,#2`; danach `movne r2,#1`, `cmp r1,#0`, `orreq r2,r2,#1`, `cmp r2,#0` | Wenn finales `r2 != 0`, setze `r0=2`, branch zu Epilog `0x130ec`; andernfalls Eintritt in Body bei `0x12eec`. Das ist eine Register-/Flag-Aussage, keine ABI-Parameterbenennung. | `ev_c276b44f9b7f78688c283a46c289bd8d800d92599f71e66dd3828f79c6718c52`, `ev_f83e127dd95ac8219bff0d5a6654b6d8ab28ea8ea33ccbc7a801880638e9e29d`, `ev_7a8eb807e22565ed9a1c817d7edad2f27eeb43f281cd56c305157505428b9de1` |
| VERIFIZIERT | Unsigned Check nach `sub r3,r0,#1`; `bhi` | `0x12efc -> 0x13134`: `r3=20`, dann Stackstatus und gemeinsamer Rückgabepfad | `ev_bf6a80c0216073dcc397f6c82412a6977194c9e4ffa038fe51839ac9115cfa28`, `ev_6f5cfc379d9ec9c366dc7a560b194da5d1db712b277f4bd3254fb568fe726046` |
| VERIFIZIERT | Vergleiche an `0x12f0c` und `0x12f1c` | Ungleichheit beiderseits zu `0x1312c`: `r3=32`, danach Status-Store | `ev_43dad9592b4f7d67634f9a71c2ac1705ba2105f23c184020a08aeafaf3a8f5ca`, `ev_badfb82f0f2ded01b2bcf16ca2d01799ae0220f7f12c4872e159f6841dd24c57`, `ev_713eaf8e07823d6071ddb037de6b646207783ca050743f2ecd239188c0204f7c` |
| VERIFIZIERT | Bit-Test an `0x12f28`; Nullpfad | Branch zu `0x130e8`, gibt aktuellen `[sp,#8]`-Wert zurück | `ev_058fc5817b383c7dbe3496548e2b4d7fc15851cf418f61915ed6384cc616055b`, `ev_c0a48b8da65b22bc096a06cd23c77e58208adb06dbff711dbaeb31918151e147` |
| VERIFIZIERT | Indirekte Calls `0x12f64`, `0x12f70`, `0x12fa8`, `0x12fb0` | Call-Rückläufe und Stackwort `sp+12` beeinflussen nachfolgende Tests; der Pfad setzt teils den Stackstatus auf 1 oder springt zum Status 2 | Call-Evidence aus Instruktionstabelle; `ev_9fe819a505fe47b2cb3cb223b431e5580c36687cf26f13baa903d90129ade962` |
| VERIFIZIERT | `0x12fc0` / `0x12fd0` / `0x12fe4` | Ungleichheit des Stackwerts führt zu 2; `uxtb(r0-1)>0xf9` oder `r0` größer als geladenes Wort führt ebenfalls zu 2 via `0x13120 -> 0x13124 -> 0x130e8` | `ev_9fe819a505fe47b2cb3cb223b431e5580c36687cf26f13baa903d90129ade962`, `ev_27707fc5c9a99e8d0f703959f8f32d1bcc117f9baab568825af5995f634b5be6`, `ev_288eb688409a0d230fdb23c2b78306f7c0e4c3a1c187c676e7082f6075c19640` |
| VERIFIZIERT | `0x12fe8` / `0x12fec` / `0x12ff0` / `0x12ff4` | Wenn Register r4 weder 0 noch 3: r3=24 und gemeinsamer Statuspfad zu `0x13124`; sonst direkter Call `0x11fdc` | `ev_f8860fdf115ef1a41e2bdb2ac1f60101de46143ca3fc676c5941132fd9ca5619`, `ev_d69abcd0b52cbbf102b5af1ad5ae1d5bf6c25ceaff36b16b51ad8ad05afde8952` |
| VERIFIZIERT | Direkter Call `0x11fdc`; danach `cmp r0,0`, Store in `sp+8` | Call-Resultat ersetzt hier den vorherigen Statuswert; bei nicht-null zu `0x130e8`, bei null weiter | `ev_d69abcd0b52cbbf102b5af1ad5ae1d5bf6c25ceaff36b16b51ad8ad05afde8952`, `ev_71deb9a46da92f5c44061a23bfb6b83d96be372dc83693bca759963185987377`, `ev_2dd7c861444d919b52440bb3eeba56b63e2f259d6e659430c251b939cf138561` |
| VERIFIZIERT | Zustandswort an `0x1301c`; Vergleiche bei `0x13020/28/30`, Register r4 bei `0x13038` | Fälle zu `0x13114` (Status 39), `0x130fc`, oder gemeinsam `0x130d4`; `r4!=0` nach Zustand 2 führt zu 39, `r4==0` geht über direkten Call `0x11d40` und setzt Stackstatus auf 0 | `ev_776962cc92d6bbe2711779071f1e48b47bc661164891a8462fe7cd431277d0a5`, `ev_432b9171db4d50e6afa182f907fb9ce0dabf983968ef775c3bd6e4b0e512dc22`, `ev_574f718ff091fa6456616d7eb87d23f31757467961f322fcebaaacf1e938f464`, `ev_8548e887d3263bb15c540950a34799d4d08a04c7b52077324c586c8d121d7edc` |
| VERIFIZIERT | Zustand 0 und Register r4=3: Calls `0x13058`, `0x13060`, dann `0x13090` | Indirekte Calls; bei nichtnull OR-Verknüpfung oder Ungleichheit Stackwort führt `0x130f4` zu `r0=40`; weiterer Markerfehler setzt `r0=16`; sonst Call `0x1277c` und weiter zu `0x130d4` | `ev_3b68fc3c7a72b01a47ebf35bcebd2b9f73a8d5acb3214c6460a33e0f0539beea`, `ev_755f3d2019ea2f84cb296a45223eee014992425708ba1b3e40b1ac4dfcba7b03`, `ev_e2cc911207bff8d76a5aefb93852ff38ff2423830009987ac52f6fe742af1bdf`, `ev_76e7ff39340457d79f9340fe6254244c3abf502f2cdc8656e0f1ed8c3c7381ff`, `ev_b70d1c452c89ab78da5d1b519e677feb02439e0d7820b5ae6d82381aba7b3984`, `ev_8760fc6594b13842515c3d0c114eabb033ab61fd84615bbcd60880020e45294d` |
| VERIFIZIERT | `0x130d4 -> 0x130d8 -> 0x130dc..0x130e4` | Direkter Call `0x12074`; sein `r0` wird nur dann nach `[sp,#8]` kopiert, wenn der bisherige Stackstatus Null ist. Ein bereits nichtnuller Status bleibt bestehen. | `ev_5660466ac460c67e0bc81c845cd397162dea4668b2681d6782562bf9644f3dca`, `ev_63fe3866db193696c1c42135e2124b129e5552fa5588af45be787114e149cacb`, `ev_f7593d30370d402db4108430ccf8d97d6ece6daefaac779ec9faf58caa22a87b`, `ev_bf5650480f330007640689dd34bb0d88020709ed759ac79419f40ada56a899d4`, `ev_380f0b644d23a545f2aef2ce2939e909aacf900e6dab7d37c185117d7e1fa671` |
| VERIFIZIERT | `0x13124`, `0x13128`, `0x130e8`, `0x130ec`, `0x130f0` | Fehlerwerte `2/20/32` landen im Stackstatus; gemeinsamer Load und Epilog führen zum RETURN. Direkter Entry-Guard-Pfad verlässt mit `r0=2`. | Evidence aus Instruktions- und CFG-Tabellen |

Der aus Instruktionen abgeleitete konstante `r0`-Wertebereich an beobachteten Rückgabewegen ist `{1, 2, 16, 20, 24, 32, 39, 40}`: insbesondere bleibt die initiale Status-1-Zuweisung über den Pfad `0x130e8` erhalten. Außerdem können Ergebnisse der genannten Calls im `r0`-Register bzw. Stackstatus zurücklaufen; der Nullwert ist in einem expliziten Pfad als Status-Store belegt. Das ist keine Fehlercode-Semantikzuordnung. Die Stackstatusstelle `[sp,#8]` startet mit 1; der Call `0x11fdc` überschreibt sie mit seinem `r0`; am gemeinsamen Pfad `0x12074` wird dessen Ergebnis nur bei bisherigem Status 0 gespeichert. Nichtnullige Vorwerte werden dort erhalten. Diese Überschreibungsbeobachtung ist auf die konkreten Stores und Bedingungen beschränkt.

## Init-Publikationslane: nur candidate-spezifischer Pfad

| Status | Ghidra-Adresse (ELF-VA/Datei) | Instruktion / Wort | Ableitung | Evidence |
|---|---:|---|---|---|
| VERIFIZIERT | `0x1532c` (`0x532c`) | Bytes `84 e6 ff ff` | Little-endian signed displacement `-0x197c` | `ev_8e2bb442d1239538e3d15d5db4b8efb75f1bf4c079cb1387bba949b8273c6fa5` |
| VERIFIZIERT | `0x14828` (`0x4828`) | `ldr r3,[0x1532c]` | PC-relative Literal-Lesezugriff | `ev_dfb668aebb99d5bae879781c7a6201f1fa5786a44edc9e03e2f3fdc8e4a1f3b8` |
| VERIFIZIERT | `0x1482c` (`0x482c`) | `add r3,pc,r3` | ARM PC `0x4834` + `-0x197c` = ELF-VA `0x2eb8`, Ghidra `0x12eb8` | `ev_a47df2233da504ab207a54290ce5c1dd9bb20c0228ca2b972b355ed442466578` |
| VERIFIZIERT | `0x14830` (`0x4830`) | `str r3,[sp,#0x20]` | Exakte DATA-Referenz des Registers auf Kandidat; kein Name/Slot abgeleitet | `ev_cd95abeda7bc709ad72cb5835439db39e429a9f57b8d3b11e6c0598cd64938d5` |
| VERIFIZIERT | `0x14848` (`0x4848`) | `vldr.64 d17,[sp,#0x20]` | Holt das gespeicherte 64-bit Stackfenster in d17 | `ev_6ca90d8548ac4d0aa0b3905ad0eaff58240556db307d4742122b99486dc522c8` |
| VERIFIZIERT | `0x148dc/0x148e0` (`0x48dc/0x48e0`) | `add r3,r0,#0x620`; `add r3,r3,#0xc` | Zielbasis `r0+0x62c` | `ev_8bbd192c125cf17527f2224c1e60d52c4efd25823e23d570ec853e5dd6e7fd25`, `ev_b7b52647bb557c6471e089aef6f9edddb2f89bda16315202ddd719df57c18bac` |
| VERIFIZIERT | `0x148e4` (`0x48e4`) | `vst1.32 {d16,d17},[r3]` | ARM little-endian 32-bit Lane-Reihenfolge schreibt d16 an `+0x62c/+0x630`, d17 an `+0x634/+0x638`; Candidate aus d17-Lane 0 somit genau `r0+0x634` | `ev_227edb89be0fc3a2d2f4c279fba4d9c2c4d6646601e5ae9d5ed61fe53435b394` |

`0x14830` ist innerhalb der von Ghidra gemeldeten Init-Procedure `0x147fc..0x1531f` (`IoDrvKbus_Init`); diese Grenzbeobachtung stammt aus `ev_5b194052b08533fe297e469a50f901d6df2752074bf83b609a22002f24819f68`. Die candidate-spezifische Kette endet beim konkreten Storewort an `r0+0x634`. `r0` als Laufzeitbasis und die Bedeutung des Zielworts bleiben offen. Andere Instruktionen derselben Init-Funktion und deren Publikationsfelder wurden nicht untersucht.

## Literalpool und Call-Scope

Der Kandidatenliteralpool wurde als exakt 28 Bytes bei Ghidra `0x1313c` gelesen; `read_bytes` meldet vollständig und die eingehende Referenz bei `0x12ecc` zeigt auf `0x1313c` (`ev_6835ff14327d29dd3fda3288b44bd651c0db9e5c49bf4f20665eb4347970f38a`, `ev_9a083e044538636d70999a7e7a0ee51f83dd58d30d972614f5fffad98f399e24`). Rohbytes nach Wortadresse:

| Datei/ELF-VA | Ghidra | Rohbytes | Status |
|---:|---:|---|---|
| `0x313c` | `0x1313c` | `20 61 01 00` | VERIFIZIERT |
| `0x3140` | `0x13140` | `dc 00 00 00` | VERIFIZIERT |
| `0x3144` | `0x13144` | `88 01 00 00` | VERIFIZIERT |
| `0x3148` | `0x13148` | `f0 61 01 00` | VERIFIZIERT |
| `0x314c` | `0x1314c` | `ac 72 01 00` | VERIFIZIERT |
| `0x3150` | `0x13150` | `b4 01 00 00` | VERIFIZIERT |
| `0x3154` | `0x13154` | `c0 50 00 00` | VERIFIZIERT |

Die begrenzte Disassembly endet nach dem Branch bei `0x3138`. Der nächste zugeordnete Bereich ist Literal-Daten, nicht Function-Code. Es wurde kein Byte, Instruktionsbody oder Nachbarkandidat ab Datei/ELF-VA `0x3158` angefordert oder exportiert. Direkte und indirekte Calls sind nur als Call-Sites erfasst; Zielkörper wurden nicht untersucht.

## Alternativerklärungen und Restunsicherheit

- **OFFEN:** Ghidras fehlende Procedure-Grenze kann bedeuten, dass die erkannte Procedure-Definition unvollständig ist oder der Einstieg Teil eines größeren/anders abgegrenzten Blocks ist. Die ARM-Disassembly, Guards und Return-/Branch-Ziele im expliziten Fenster sind dadurch nicht automatisch widerlegt, aber eine vollständige Procedure-Analyse ist nicht belegt.
- **VERIFIZIERT:** Der dekodierte Register-Store `vst1.32 {d16,d17},[r3]`, die vorangehende Basisrechnung und das Laden des Kandidatenworts in d17 ergeben für ARM little-endian statisch das Zielwort `r0+0x634`. Offen bleibt ausschließlich, ob und wann dieser Init-Pfad zur Laufzeit ausgeführt wird; die konkrete Lane-Adresse hängt nicht von einer Laufzeitbeobachtung ab.
- **OFFEN:** Ein `r0`-Wert kann eine Basis, ein Zeiger oder etwas anderes sein. Kein Struktur-, Slot-, Callback- oder API-Name wird daraus abgeleitet.
- **OFFEN:** Entry-Register, Aufrufkonvention, Laufzeit-Ladebias, Relokationszustand zur Ausführung und tatsächlicher Initialisierungspfad sind nicht untersucht.
- **OFFEN:** Indirekte Call-Ziele sowie die Bedeutungen direkter Call-Ziele und der beobachteten Konstanten bleiben unbekannt.
- **OFFEN:** Das Verhalten bei Hardwarezuständen, Zeitdomänen, Fehlern außerhalb dieser statischen Pfade und physikalische Wirkung wurden nicht geprüft.

## Tests / Validator

| Status | Prüfung |
|---|---|
| PASS | Eingangshash und Dateigröße gegen Arbeitsauftrag |
| PASS | Ghidra-Adresse `0x12eb8` auf Datei-Offset `0x2eb8` und Pool `0x1313c` auf `0x313c` abgebildet |
| PASS | Literalpool-Lesung vollständig: 28/28 Bytes; Stop vor exklusivem Ende `0x3158` |
| PASS | `validate.sh` prüft Quelldigest, Evidence-IDs, erlaubte Adressbereiche und `SHA256SUMS` |
| NOT_RUN | Laufzeit-, VM-, Netzwerk-, Geräte- und Hardwaretests; für diese rein statische Offlinefrage nicht ausgeführt |

Reproduzierbar aus diesem Verzeichnis: `./validate.sh`. Die REA-Datei `rea-evidence.json` ist der unveränderte Tool-Export; Report und Tabellen enthalten nur die hier referenzierten Ausschnitte und Ableitungen.
