> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-192 report

Status: VERIFIZIERT
Test/validator: PASS

## Ergebnis

Die vollständige Inventur enthält **36 direkte Store-Instruktionen** in `[0x30a0,0x33b0)`: 13 Stores mit effektiver Adresse relativ zum innerhalb des Fensters berechneten Instanzbasiswert `r4`, sowie 23 Stores relativ zu `sp`. Keine effektive Store-Adresse ist statisch auf `[0x1a270,0x1a30c)` reduzierbar. Alle einzelnen Stores, Größen, Adressbasen und Displacements stehen in `stores.tsv`.

Die entscheidende In-window-Definition lautet `r4 = r0 + 0x63c * fp` (`mla` bei `0x30c0`): `r0` und `fp` sind an dieser Stelle nicht durch innerhalb des erlaubten Fensters definierte Konstanten gebunden. Daher bleibt `r4` eine sichtbare, aber absolute Adresse nicht reduzierbare Basis. Die `STR`-Stores verwenden `r4+0x00c`, `+0x010`, `+0x014`, `+0x01c`, `+0x050`, `+0x054`, `+0x058`, `+0x620` und `+0x628`. Vier `VST1.32` verwenden durch unmittelbar vorhergehendes `ADD` gebildete Adressen `r4+0x020`, `+0x030`, `+0x040` und `+0x62c` (je 16 Bytes). Die Stores bei `+0x01c` und `+0x050` schreiben den Wert von `r4` in den relativen Zielslot; auch daraus folgt keine absolute Zieladresse.

Eine literalgestützte, innerhalb des Fensters vollständig reduzierbare Wertbildung erzeugt bei `0x30d0` bis `0x30e0` den Wert `0x1a234`, der anschließend bei `0x30e8` nach `[r4+0x620]` geschrieben wird. Der Rechenweg ist: Literal `[0x3374]=0x000132ec`; A32-PC bei `0x30d0` ist `0x30d8`, also `0x30d8+0x132ec=0x163c4`; dann `+0x3e40=0x1a204`; dann `+0x30=0x1a234`. `0x1a234` liegt **vor** der abgefragten Range `[0x1a270,0x1a30c)`. Die Rechnung belegt nur den gespeicherten Zahlenwert; ohne Semantikbeleg wird er nicht als Pointer oder Feldinhalt benannt. Die übrigen PC-relativen Literalwerte, die in Werten für `r4`-Stores münden, ergeben `0x1590`, `0x15a8`, `0x15c0`, `0x17dc` bzw. `0x1814`; `validate.py` prüft deren jeweilige Opcodes, Literalbytes und PC-Rechnung.

Ergebnis für die NOBITS-Range: **kein direkter Store im Fenster zielt statisch nachweisbar in `[0x1a270,0x1a30c)`**. Ebenso weist das Fenster keinen absoluten Store auf den Basiswert `r4` hin. Es weist 13 relative Store-Adressen aus, die aus `r4` plus exaktem Displacement folgen; diese bleiben mangels absoluter Definition von `r4` relativ. Die zuvor akzeptierte Beobachtung `[r4+0x61c]` (E-XE164-214) ist außerhalb dieses Fensters und wird hier nicht nachgeprüft oder erweitert.

## Inventur und Klassifikation

`stores.tsv` listet die 36 Instruktionen vollständig und adressgeordnet. Die 13 `r4`-relativen Stores sind die Klasse (b). Die 23 `sp`-relativen Stores sind Klasse (c): ihr Basis-plus-Displacement ist bekannt, ihre absolute Laufzeitadresse jedoch nicht innerhalb der Scope-Grenze ableitbar. Klasse (a) hat null Einträge.

## Alternative und Unsicherheit

Alternative Lesart: Ein `r4`-relativer Slot könnte zur NOBITS-Range gehören, falls der unbekannte absolute Wert von `r4` plus sein Displacement in diese Range fällt. Der In-window-Code liefert dafür keine absolute Basisdefinition; diese Möglichkeit ist daher **OFFEN**, nicht widerlegt. Die geprüfte Aussage „kein statisch auf die Zielrange reduzierbarer direkter Store“ bleibt davon unberührt.

Weitere Unsicherheit: Disassemblierung und unmittelbare ARM32-Adressarithmetik belegen die Instruktionsform und die hier genannten effektiven relativen Adressen. Sie belegen keine Laufzeitwerte von `r0`/`fp`, keine Objekt- oder Feldsemantik und keine Wirkung von Callees. Literal-Wörter werden ausschließlich als 32-bit little-endian Werte interpretiert, wenn sie direkt von einer in-window `LDR [pc,#imm]` referenziert werden.

## Eingabe, Umfang und Werkzeuge

- Eingabe: `sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`; 25,976 Bytes; SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.
- ELF: ELF32, little-endian, `ET_DYN`, ARM, EABI5 hard-float. `.text` hat Adresse/Offset `0x0a34`/`0x0a34`; die in-window Adressen sind dadurch zugleich die Rohdatei-Offsets. `.bss` ist NOBITS ab `0x16088`, Größe `0x4284`; Ende exklusiv `0x1a30c`. Der relevante unnamed Bereich `[0x1a270,0x1a30c)` entspricht dem akzeptierten E-XE164-216-Befund.
- Codefenster SHA-256, Rohbytes `[0x30a0,0x33b0)`: `b2e3ce972bc3c553377da8c915fe8cc10f7cbbbcf4881cade8382c073a040b40`.
- Direkt referenzierte Literalwörter: 16 Wörter an `0x3374`, `0x3378`, `0x337c`, `0x3380`, `0x3384`, `0x3388`, `0x338c`, `0x3390`, `0x3394`, `0x3398`, `0x339c`, `0x33a0`, `0x33a4`, `0x33a8`, `0x33ac`, `0x33b0`. Geordnete Konkatenation, je 4 Rohbytes: SHA-256 `4332d1f53ae43ff59dad30627682a6eee3e6ca6d97d6e3ae85e14574f6303568`.
- REA: `open_binary` (Ghidra 12.1.4; Zielhash bestätigt) und ein exakt begrenztes `read_bytes`; letzteres lieferte 0/784 Bytes, `complete=false`. Einmalige Lücke notiert.
- Fallback: `arm-linux-gnueabihf-objdump -D --start-address=0x30a0 --stop-address=0x33b0 <input>`; anschließend Roh-Literalabruf per `dd`/`od` und little-endian Relativarithmetik. Kein Ghidra-Import hing ab. Kein code außerhalb des Fensters wurde zur Kontrolle gelesen oder interpretiert.

## Manifest und Prüfung

`validate.py` prüft Store-Anzahl, eindeutige/adressgeordnete Instruktionen, zugelassene Klassifikationen, `r4`-Displacements, die beiden Bytebereich-Hashes, den Eingabehash und die SHA256SUMS-Datei. Ergebnis: `PASS`.
