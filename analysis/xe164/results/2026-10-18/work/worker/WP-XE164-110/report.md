> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-110 — zwei weitere indirekte Aufrufe am GOT-Objekt

## Ergebnis

**VERIFIZIERT:** Die erste Lane liegt in Ghidra-Prozedur `0x1277c`. Der indirekte Aufruf erfolgt bei `0x12c64` über `r3`; unmittelbar davor wird `r0` aus `r8` kopiert und `r1` auf `sp+0x44` gesetzt. Die vorherige Record-Verzweigung lässt den Call-Pfad nur zu, wenn `r6 >= 0` und das Halfword `[r8+8] == 5` ist. Nach dem Call wird `[sp+0x44]` gelesen; die Rückgabe in `r0` wird lokal auf Null/Nichtnull reduziert und zusammen mit diesem Slot für eine weitere Verzweigung verwendet.

**VERIFIZIERT:** Die zweite Lane ist in Ghidra als Instruktionen vorhanden, aber `0x13d08`, `0x13d0c` und `0x13d10` liegen laut `resolve_containing_procedure` außerhalb jeder erkannten Prozedur. Ghidra dekodiert trotzdem `ldr r12,[r11,r12]`, `ldr r4,[r12]`, `blx r4`; die ersten beiden Reads zeigen auf dieselben referenzierten Ziele wie WP-XE164-108. Für das begrenzte Rückwärts-/Vorwärtsfenster wurde deshalb der dokumentierte GNU-ARM-Fallback verwendet.

**VERIFIZIERT:** Im zweiten Pfad ist `r0` beim Call die Adresse `sl−20`, zuvor bei `0x3bdc` berechnet; `r1` ist `r8 = sp+52`, zuvor bei `0x3bc4` berechnet. Der Pfad liegt im Selector-Zweig `128 < [sl−20] <= 132` und hat zusätzliche Halfword-Guards: `[sl−12] == 28` nimmt den Callpfad direkt; andernfalls überspringt `[sl−10] == 16` den Call. Nach der Rückkehr wird `r0` als Adresse für `ldrh r0,[r0]` benutzt und das Halfword in einen lokal berechneten Slot geschrieben. Das ist ein statischer Hinweis auf einen Rückgabewert, der hier als Adresse eines 16-Bit-Werts verwendet wird.

**HYPOTHESE:** Die erste Lane behandelt die Rückgabe wie einen Null-/Nichtnullindikator; die zweite verwendet die Rückgabe als Halfword-Adresse. Daraus folgt keine allgemeingültige API-Signatur: derselbe benannte Import kann an den Callsites unterschiedlich verarbeitet werden, oder der lokale Kontrollfluss/Outputslot kann weitere Bedeutung tragen. Keine Record-Struktur, kein Feldlayout und kein Laufzeitwert wird daraus abgeleitet.

**OFFEN:** Der konkrete zur Laufzeit in der BSS-Objektzelle stehende Callback, die vollständige API-Signatur, die Semantik der Halfword-Guards und die Bedeutung der übergebenen Pointer bleiben unbekannt. Diese Analyse beobachtet keine Ausführung.

## Artefakt, Eingaben und Werkzeuge

- Ziel: `libIoDrvKbus.so.0.0.1`, 38.584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`.
- Kontext: WP-XE164-108 `report.md`, SHA-256 `9daa5c205d6a71e5b9709008119eecd975cafba5a88e967a367700672a895948`.
- REA: `rea-agents` 6.5.0; Provider Ghidra 12.1.4; Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- GNU-Fallback nur nach der oben genannten Prozedurgrenzenlücke: `arm-linux-gnueabihf-objdump`, GNU Binutils 2.44. Genaues Kommando und vollständiges begrenztes Listing: [gnu-arm-window.txt](./gnu-arm-window.txt), ELF-Linkadressbereich `0x3b80..0x3d50`.
- Semantic-Validator: Node.js `v24.22.0`, [validate_semantics.mjs](./validate_semantics.mjs).

REA war die erste Methode: `open_binary`, Funktionsdossier/Instruktionsfenster für die erste Lane, exakte Instruktions- und Prozedurauflösung für beide Lanes sowie REA-Dateioffsetabfragen. Der Ghidra-Funktionskörper `0x1277c..0x12e7f` wurde für die Antwort auf das minimale lokale Fenster beschränkt. In der zweiten Lane meldete Ghidra für die konkreten Instruktionen `procedure=null`, und die Prozedurauflösung ergab `found=false, reason=not_in_procedure`; daher deckt GNU Binutils ausschließlich das lokale Rückwärts-/Vorwärtsfenster ab. Kein Binary wurde ausgeführt.

## Beobachtungen und Adressen

Ghidra-Standardraumadressen und Datei-Offsets stammen aus REA `address_to_file_offset`. Der genaue GNU-Fallback ordnet die zweite Lane der ELF-Linkadresse durch Subtraktion von `0x10000` zu; der Dateioffset ist für diese Instruktionen separat durch REA belegt.

| Lane / Beobachtung | Ghidra-Adresse | ELF-Link-VA (zweite Lane) | Datei-Offset | Statische Beobachtung |
|---|---:|---:|---:|---|
| erste Guard: `cmp r6,#0`; `blt 0x127b0` | `0x12c3c` | — | `0x2c3c` | negativer Selectorpfad springt aus dem Lane-Fenster |
| Record-Halfword und Vergleich `#5` | `0x12c44..0x12c4c` | — | `0x2c44..0x2c4c` | bei ungleich 5 Sprung nach `0x127b0` |
| Call-Argumentvorbereitung | `0x12c54..0x12c58` | — | `0x2c54..0x2c58` | `r1=sp+0x44`; `r0=r8` |
| GOT-Zellenread | `0x12c5c` | — | `0x2c5c` | `ldr r3,[r9,r3]`; REA-READ-Referenz auf `0x290c4` |
| BSS-Objektread | `0x12c60` | — | `0x2c60` | `ldr r3,[r3,#0]`; REA-READ-Referenz auf `0x2a224` |
| indirekter Call | `0x12c64` | — | `0x2c64` | `blx r3`, computed call |
| unmittelbare Rückgabeverwendung | `0x12c68..0x12c84` | — | `0x2c68..0x2c84` | lädt `[sp+0x44]`; normalisiert Call-Rückgabe auf Null/Nichtnull; verzweigt bei kombinierten Bedingungen |
| zweite Lane, Guard-Block | `0x13ce8..0x13cfc` | `0x3ce8..0x3cfc` | — | `128 < selector <= 132`; Halfword-Guards `28` / `16` |
| Call-Argumentvorbereitung | `0x13d00..0x13d04` | `0x3d00..0x3d04` | `0x3d00..0x3d04` | `r1=r8`, `r8=sp+52`; `r0=sl−20` bleibt aus `0x3bdc` erhalten |
| GOT-Zellenread | `0x13d08` | `0x3d08` | `0x3d08` | `ldr r12,[r11,r12]`; REA-READ-Referenz auf `0x290c4` |
| BSS-Objektread | `0x13d0c` | `0x3d0c` | `0x3d0c` | `ldr r4,[r12]`; REA-READ-Referenz auf `0x2a224` |
| indirekter Call | `0x13d10` | `0x3d10` | `0x3d10` | `blx r4`, computed call |
| unmittelbarer Rückgabeverbrauch | `0x13d14..0x13d2c` | `0x3d14..0x3d2c` | `0x3d14..0x3d2c` | Halfword an Adresse aus `r0` laden und in lokal indizierten Slot schreiben |

Die Datei-Offsets beider Calls sind `0x2c64` und `0x3d10`. Die zwei Instructions vor dem zweiten Call und die nachfolgenden Halfword-Verbraucher liegen im privaten `gnu-arm-window.txt`; Ghidra-Instruktionsbelege für `0x13d08`, `0x13d0c` und `0x13d10` bleiben im kanonischen REA-Bundle.

## Lokaler Kontrollfluss und Unsicherheit

Für die erste Lane weist das Ghidra-Dossier den Block `0x12c50..0x12c88` mit Nachfolgern `0x12c88` und `0x12cfc` aus. Die unmittelbaren Präbedingungen stehen im davorliegenden Block: `r6 < 0` geht zurück auf `0x127b0`; `[r8+8] != 5` ebenfalls. Nach dem indirekten Call wird das Halfword/Word aus `sp+0x44` gelesen. Die Folge `clz r0,r0; mov r0,r0,lsr #5; cmp r3,#0; orrne r0,r0,#1` bildet aus der Rückgabe und dem Stackslot einen lokalen Verzweigungswert. Hier folgt keine Rückgabestruktur und kein `r0`-Deref.

Für die zweite Lane ist der Selector bei `0x3c24` aus `[sl−20]` gelesen. `128` wird verglichen, dann führen Werte oberhalb `128` (nach dem vorherigen Ausschluss `>132`) in den Block `0x3ce8`. Dort ruft `[sl−12] == 28` direkt auf; andernfalls führt `[sl−10] == 16` zum Skip-Pfad, alle anderen Werte passieren zur Call-Vorbereitung. Die `r0`-Definition `sl−20` und `r1`-Definition `sp+52` sind direkte Datenflussbeobachtungen im bounded Listing; die Benennung dieser Speicherbereiche als Felder oder Records wäre zusätzliche Semantik und bleibt OFFEN. Unmittelbar nach dem Call wird `r0` tatsächlich dereferenziert, aber nur mit einem 16-Bit-Load (`ldrh`).

Alternative: die Guards können lediglich Auswahlbedingungen in einem internen Dispatch sein und müssen keine öffentliche Record-Kennung darstellen. Auch der 16-Bit-Load beweist nur diese konkrete Verbraucheroperation; er beweist keinen API-weiten WORD-/UINT16-Vertrag, die Pointergültigkeit oder Endianness jenseits der beobachteten ARM-LE-Instruktionen.

## Evidenz und Prüfstatus

Kanonisches REA-Bundle: [rea-bundle.json](./rea-bundle.json), 56 Evidence-Datensätze, 0 Unknowns. Relevante REA-IDs:

- Erste Prozedur/Dossier: `ev_25b965e867e7e080ae7f538d2d3c8494926026183f299d60218f09bbc6802002`; Instruktionsfenster: `ev_a681781f43af758110dd35b449702f688ff40799221038d0160aac1009816c49`.
- Erste Lane-Call-Bytes: `0x12c5c` `ev_6f675247c1daa85b48f00c431e97a45661d6278ea019b20dc0a6a2220cca21ec`, `0x12c60` `ev_0bf36afbb027f1f6716c079f9ba84209f884bf85f397e53636237243cc413874`, `0x12c64` `ev_71381ac5c1728fb9990dc2ee0e970b1a8617c16fcb07ef069295db2893507084`.
- Zweite Lane: `0x13d08` `ev_a661b024559c790048089f24ed6e7d8da2692561f5bae78e89591e9942cd0f93`, `0x13d0c` `ev_9d6e7e7072ca89c518c70b890866fae592786cd1c7471f6b1294eeb886dcf619`, `0x13d10` `ev_f86432ca56d444bb15c7f2d70d4f4d8280cea60b6ad33979a3eb094d8e1202ec`.
- Prozedurgrenzenlücke: `0x13d08` `ev_f7c101cd5073fed7f36678beac73713ac25e6f06740b1abe267971ce96b78aaf`, `0x13d0c` `ev_babba1cd3482882c27a0bc8f01e3167de305002d299a4398bc4ac1c03cdbc4fa`, `0x13d10` `ev_5d9d2de5fd70f481cd7ba0c940b92c535c7c737dbefe24064e2fadf0c4f1210a`.

| Prüfung | Status | Ergebnis |
|---|---|---|
| Artefaktidentität | PASS | Zielhash entspricht dem vorgegebenen Hash; WP-XE164-108 Reporthash stimmt exakt. |
| Ghidra-Lane und Call-Bytes | PASS | REA-Instruktionsdatensätze plus erste lokale Funktionsinstruktionsfolge stimmen mit dem Bericht überein. |
| Prozedurgrenze zweite Lane | PASS | REA liefert decodierte Instruktionen; Containing-Procedure-Auflösung ist explizit `not_in_procedure`. |
| GNU ARM Fallback | PASS | Einmalig begrenzte Disassembly `0x3b80..0x3d50` nach dokumentierter Ghidra-Gap; keine Ausführung. |
| Semantischer Validator | PASS | `validate_semantics.mjs` prüft Hash-/REA-Record-Identität, Call-/Guard-/Consumer-Instruktionen, Offsetbelege und Ghidra-Gap. |
| Runtime/VM/Hardware/Netzwerk | NOT_RUN | Außerhalb des Auftrags; keine dieser Ebenen wurde verwendet. |

## Erzeugte Dateien und Hashes

Die SHA-256-Werte aller erzeugten Forschungsartefakte stehen in [SHA256SUMS](./SHA256SUMS); das Hashmanifest selbst ist aus naheliegenden Gründen nicht in sich selbst eingetragen. Es wurden keine gemeinsamen Repository-Dateien geändert.
