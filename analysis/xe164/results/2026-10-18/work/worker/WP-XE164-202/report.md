> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-202 — `adi_GetApplicationInterface`

## Status and scope

**VERIFIZIERT** — statischer Kontroll- und Datenfluss innerhalb des Dynsym-Bereichs `[ELF-VA 0x3464, 0x3474)` im exakt gebundenen FW31-ELF. Keine Ausführung, keine Geräte-, VM- oder Netzaktivität. Es wurden weder Aufrufer noch Nachbarfunktionen untersucht.

## Identität und Koordinaten

- SD-Image: `FW31-PFC100-PFC200-040901-31-SD`, 287,309,824 Bytes, SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c` — **PASS**.
- Extrahierte Datei aus Partition 2, Pfad `/usr/lib/libdal.so.1.0.1`: 18,076 Bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` — **PASS**.
- `readelf --dyn-syms -W` bestätigt genau das Ziel: `adi_GetApplicationInterface`, `st_value=0x3464`, `st_size=16`, Typ `FUNC`.
- ELF: ELF32, little-endian, `EM_ARM`, `ET_DYN`. Der erste PT_LOAD bildet ELF-VA `0x3464` auf Datei-Offset `0x3464` ab. Ghidras Importbasis ist hier `0x10000`: ELF-VA `0x3464` erscheint als Ghidra-Adresse `0x13464`; ELF-VA `0x3470` als `0x13470`. Diese Zuordnung wird durch REAs `address_to_file_offset` belegt (`0x13464 -> 0x3464`, `0x13470 -> 0x3470`), nicht durch ungesicherte VA-Arithmetik.
- Der berechnete Zielwert `ELF-VA 0x14154` erscheint bei Ghidra als `0x24154` und wird auf Datei-Offset `0x4154` abgebildet. Ghidras Primärname dort lautet `PTR_FUN_00024154`; das ist ein Analyse-Label und keine bestätigte API- oder Datenstruktursemantik.

## Beobachtungen

REA/Ghidra 12.1.4 meldet den Funktionskörper als zusammenhängenden Bereich `0x13464..0x1346f` (12 Codebytes) mit drei Instruktionen. Der Dynsym-Eintrag umfasst 16 Bytes; an `0x13470` erkennt REA Daten und eine eingehende Lese-Referenz von `0x13464`. Die vier 32-bit-Wörter der vollständigen Dynsym-Spanne sind:

| ELF-VA | Datei-Offset | Bytes (little-endian) | Wort | Beobachtung |
|---|---:|---|---:|---|
| `0x3464` | `0x3464` | `04 00 9f e5` | `0xe59f0004` | `ldr r0, [pc, #4]` |
| `0x3468` | `0x3468` | `00 00 8f e0` | `0xe08f0000` | `add r0, pc, r0` |
| `0x346c` | `0x346c` | `1e ff 2f e1` | `0xe12fff1e` | `bx lr`; REA klassifiziert den Fluss als Rückkehr |
| `0x3470` | `0x3470` | `e4 0c 01 00` | `0x00010ce4` | Literal-Datenwort, kein vierter Instruktionsschritt |

Die ersten 12 Bytes sind durch REA-Funktionskörper und Einzelinstruktionsanalyse belegt. Der letzte Wortwert wird von Ghidra als Datenbereich ausgewiesen und von der Instruktion bei `0x3464` gelesen. GNU-Objdump gibt die Bytes bei `0x3470` bei untypisierter Disassembly zwar als `andeq` aus; das ist eine alternative Decoder-Interpretation der Literalbytes, keine Evidenz für einen vierten ausgeführten Befehl.

## Abgeleitete Rückgabekette

Der LDR liest das Literal bei ELF-VA `0x3470` in `r0`. Für A32 ist die sichtbare PC-Adresse bei der Instruktion `0x3464` `0x346c`; mit Offset `#4` liegt der gelesene Wert bei `0x3470`. Die ADD-Instruktion bei `0x3468` verwendet PC=`0x3470` und addiert den geladenen Wert `0x10ce4`:

`r0 = 0x3470 + 0x10ce4 = ELF-VA 0x14154`

`bx lr` beendet den sichtbaren Kontrollfluss mit diesem Wert in `r0`. Der statisch ableitbare lokale Rückgabewert ist somit die Adresse `0x14154` relativ zur ELF-Ladebasis. In Ghidras Importdarstellung entspricht das `0x24154`, Datei-Offset `0x4154`. Für eine geladene Shared Library ist die tatsächliche Laufzeitadresse `load_bias + 0x14154`; der konkrete Load Bias und damit der absolute Laufzeitwert bleiben **OFFEN**.

`readelf -rW` zeigte keine Relocation auf den drei Instruktionswörtern oder dem Literal bei `0x3464..0x3470`. Am berechneten Zielslot `ELF-VA 0x14154` steht dagegen `R_ARM_RELATIVE`. Dessen vier Quellbytes am Datei-Offset `0x4154` sind `ec 1b 00 00`, also REL-Addend `0x1bec`. Ghidras initialisierter Speicher liefert dort `ec 1b 01 00` (`0x11bec`), konsistent mit der Ghidra-Importbasis `0x10000` plus Addend. Das Literal bei `0x3470` bleibt unverändert `0x10ce4`. Der Slotinhalt ist damit load-bias-abhängig; der vom Funktionskörper zurückgegebene Slotzeiger bleibt statisch als ELF-VA `0x14154` bestimmbar.

## Schlussfolgerung und Grenzen

**VERIFIZIERT:** Der sichtbare Körper besteht aus drei A32-Instruktionen, gefolgt von einem direkt gelesenen 32-bit-Literal innerhalb des 16-Byte-Dynsym-Umfangs. Er lädt `0x10ce4`, addiert den PC-Wert `0x3470` und kehrt mit ELF-relativer Adresse `0x14154` in `r0` zurück.

**HYPOTHESE:** Die Adresse könnte im Datenbereich eine Pointer-Variable oder einen funktionsbezogenen Eintrag bezeichnen, was Ghidras automatisch erzeugtes Label `PTR_FUN_00024154` nahelegt. Aus dem Symbolnamen allein folgt das nicht; der Wert an dieser Adresse wurde nicht gelesen und ihre Semantik bleibt **OFFEN**.

**OFFEN:** Laufzeit-Load-Bias, absoluter Prozesszeiger und tatsächlicher Laufzeitinhalt des relocationsabhängigen Zielslots. Der REL-Addend `0x1bec` ist statisch beobachtet; der Laufzeitwert des Slots ist daher ohne Load Bias nicht bestimmbar. Es wurde keine Runtime-Ausführung vorgenommen. Die Instruktionsinterpretation stützt sich auf Ghidras REA-Evidence plus die begrenzte GNU-ARM-Objdump-Ausgabe; die `andeq`-Deutung des letzten Wortes bleibt als alternative Rohbytes-Interpretation dokumentiert, wird aber durch die Datenreferenz und das 12-Byte-Funktionskörper-Fact nicht als Code übernommen.

## Evidence und Werkzeuge

- REA Evidence `ev_5434cc7c83781cb3e913ce46220c4cd6ed5bec32d35a9294e7172628d80e097c`: exakter Ghidra-Funktionskörper und Instruktionsfolge.
- REA Evidence `ev_842dcac001e3527b873091fb16e7e17b2d4d9eb9afec6af0a590d9ff2ce47a94`: 16 Bytes aus Ghidras initialisiertem Speicher.
- REA Evidence `ev_66a5e09e9fbe6aff5d898554a004e71183f8bf0ce8450d9f9b11ef3b51dbc762`: LDR und Datenreferenz auf `0x13470`.
- REA Evidence `ev_1b1e2ae4b8c7a487bed50f89334cfcd1584a0506605fe0f2bdc6f66b6edf048c`: ADD und Datenreferenz auf `0x24154`.
- REA Evidence `ev_f3d7d9fc97ce3f352c9331c77a8fb9e7ec4338af650a64335888f9d17f025f4d`: `bx lr`, Rückkehr-Fluss.
- REA Evidence `ev_ef7c9e27599f23958fc8d65eab66159a724a43fd4d730647bb7d8ea0f3226231`: Zieladresse `0x13470` ist Daten; eingehende Lese-Referenz von `0x13464`.
- REA Evidence `ev_3fcb40398d38d66b5c97908086611c847b6ba27900285d20bde838e3ef6704ec`, `ev_a20159cf7737482a9fd82b1f58d47fcdef3d2978c10725d978b90c8ca376eebf`, `ev_830f748f5171ffdd90b1c8b8ba2a0dcb446301edaa85b4d334fd1d8ecbc6f119`: Adress-zu-Datei-Offset-Abbildungen für Code, Literal und berechnetes Ziel.
- REA Evidence `ev_3ab058c3bad85cbfb7f95d824560d9c3ff5c7cacd8a7764c6aaf3c19e0dd5b0e`: automatischer Primärname des Zielortes.
- REA Evidence `ev_288ea2248dc4a92cda4f9097cd3068f4882933b6db96f7417c6dc59da4d513aa`: vier vom Ghidra-Loader initialisierte Bytes am berechneten Zielslot (`0x11bec` im Importbild).
- REA Evidence `ev_90bbfdf96c484c9aa475c0d81fc10fadcbcc77099073cdfea9a976da1b798cf5`: Zielslot als Datenort und eingehende Referenz von der ADD-Instruktion.
- Ghidra 12.1.4, importierter Provider `ghidra`, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- GNU Binutils 2.44: `arm-linux-gnueabihf-objdump` gezielt auf `[0x3464,0x3474)`, `readelf` für den einzelnen Dynsym-Eintrag, Segmentmapping und Relocation-Trefferprüfung. Kein Disassembly-Bereich außerhalb der 16 Bytes wurde ausgegeben.

## Dateien und Prüflauf

- `input/libdal.so.1.0.1` — unverändertes extrahiertes ELF, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`.
- `extract_validate.py` — reproduzierbarer, hashgebundener Extraktor/Validator für genau diesen Imagepfad, ELF-Identität, Dynsym-Bytebereich, vier Wörter, lokale PC-Addition und rohen REL-Addend am berechneten Ziel.
- `report.md` — diese Befunde.
- `SHA256SUMS` enthält die SHA-256-Werte für Bericht, Validator und Eingabe-ELF.

Prüflauf: `python3 extract_validate.py` — **PASS** für Image- und ELF-Hash, Dateigröße, ELF-Klasse/Endian/Maschine/Typ, vollständige 16 Bytes, lokal berechnete ELF-VA und rohen Zielslot-Addend. **Self-review**; keine unabhängige Prüfung oder Worker-Ausführung behauptet.
