> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-138 — Auflösung des Speicherworts bei `[r5+0x10]`

## Ergebnis

**VERIFIZIERT:** In der Loader-Call-Lane liest `0x37a4` das Wort bei ELF-VMA `0x163d4` und `0x37b4` schreibt den gelesenen Wert plus eins dorthin. In Ghidras Adressraum ist das `0x263d4`, im ELF liegt es in `.bss` bei Sektionsoffset `0x34c`. Für das Wort gibt es keine gespeicherten ELF-Bytes. Die materialisierten direkten Referenzen zeigen außerdem einen bedingten Schreibpfad, der bei `0x136a4` null in `r4` lädt und bei `0x136a8` auf dieselbe Adresse schreibt. Die vorliegenden Belege zeigen jedoch nicht, dass dieser Pfad vor dem ersten Call bei `0x37bc` ausgeführt wird.

Damit ist **kein erster Wert vor dem Call statisch belegt**. Insbesondere folgt weder aus dem `NOBITS`-Status noch aus Ghidras nicht initialisiertem `.bss`-Block ein hier beobachteter Laufzeitwert.

## Eingabeidentität

| Eingabe | Größe | SHA-256 |
|---|---:|---|
| ELF `libIoDrvDal.so.1.0.2` | 25,976 Byte | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` |
| WP097 `report.md` (akzeptierter Kontext) | 9,161 Byte | `d0378dfe088702c8193b07e854519d4843ad22d48d64136a9b26f1cc60cbbd94` |
| WP097 `objdump-bounded.txt` (akzeptierter Kontext) | 2,489 Byte | `9f865a44610c9d633235b1c8bfd0b40094102b7bdfac39eb4bfe8edd4da2736a` |

Der Hash des WP097-Berichts wurde frisch gemessen und korrigiert; er weicht vom fehlerhaften, im Startauftrag ergänzten Wert ab. Der Hash von `objdump-bounded.txt` wurde vor Verwendung frisch gemessen.

## Literalarithmetik und Adressdomänen

REA/Ghidra 6.5.0 / Ghidra 12.1.4 analysierte den ELF als `ARM:LE:32:v8`, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`, Image Base `0x10000`.

1. Die Instruktion bei Ghidra `0x13790` (ELF-VMA/Datei `0x3790`) lädt den 32-Bit-Literalwert aus Ghidra `0x14358` (ELF-VMA/Datei `0x4358`). REA `read_bytes` meldet dort `24 2c 01 00`, also little-endian `0x00012c24` (`ev_37dec38ad0d1f6bc4838b84d92aeb4d311e010a3fda3861ecd49a18794144d5d`).
2. Bei `add r5,pc,r5` an ELF `0x3798` ist ARM-PC `0x37a0`; im Ghidra-Raum ist es `0x137a0`. Also `0x137a0 + 0x12c24 = 0x263c4` für `r5`, äquivalent ELF-VMA `0x163c4` nach Abzug der Ghidra Image Base `0x10000`.
3. Das Displacement `+0x10` der LDR/STR ergibt exakt Ghidra `0x263d4` / ELF-VMA `0x163d4`.

Ghidras Blockinventar weist `.bss` als Ghidra `0x26088..0x2a30c` (Ende exklusiv), beschreibbar und `initialized=false` aus (`ev_cd2cf5d558dd27b52c198df044b7ae0e6f920c8a0b2001a5d5d5bbb913194140`). Um Typ und ELF-VMA unabhängig vom Ghidra-Speicherblock zu verankern, war ein eng begrenzter `readelf`-Fallback nötig: REA lieferte keine ELF-Sektionsart und `address_to_file_offset(0x263d4)` antwortete ausdrücklich „Address has no initialized file-backed memory“. GNU `readelf` 2.44 meldet für `.bss`: `NOBITS`, ELF-Adresse `0x16088`, Metadaten-Offset `0x6084`, Größe `0x4284`. `0x163d4` liegt darin bei `0x34c`. Der Sektions-Metadaten-Offset ist kein Datei-Offset für Wortbytes; `NOBITS` enthält diese Bytes nicht.

Die Bereiche sind daher getrennt: Literaldateibytes bei Datei `0x4358`; Ziel als ELF-VMA `0x163d4`; Ziel im Ghidra-Import `0x263d4`; kein Datei-Offset für Zielwortbytes; Runtime-Adresse/Ladebias und Laufzeitwert unbekannt.

## Vollständige materialisierte direkte Xrefs zum Zielwort

REA `xrefs(0x263d4)` gab sechs Adressen zurück (`ev_b7cd6d66d449399cf4dca9e9754915bb3c93d84ba696548354442286c3023fae`). Die Adressinspektion als Datenobjekt bestätigte dieselben sechs eingehenden Referenzen mit Ghidra-Typ `READ` oder `WRITE` (`ev_9e064c97159d638907b56978e8e73a94ae418fc40aac3c81f2f4dd3d174702d8`). Die Dateizuordnungen der `.text`-Quellen wurden separat durch REA `address_to_file_offset` bestätigt. `Ghidra`- und ELF-Adresse unterscheiden sich jeweils um `0x10000`; für diese dateigebundenen `.text`-Instruktionen stimmen ELF-VMA und Datei-Offset überein.

| Ghidra | ELF-VMA / Datei | Typ | Instruktion | Begrenzter Datenfluss |
|---:|---:|---|---|---|
| `0x12d44` | `0x2d44` | READ | `ldr r5,[r4,#-0x4]` | lädt nach `r5`; Basiswert im Xref-Fenster nicht belegt. Evidence `ev_a386dc7d…`; Mapping `ev_591b71ba…`. |
| `0x13698` | `0x3698` | READ | `ldr r3,[r6,#0x10]` | lädt nach `r3`. Evidence `ev_087258ac…`; Mapping `ev_77204c16…`. |
| `0x136a8` | `0x36a8` | WRITE | `str r4,[r6,#0x10]` | direkt davor `0x136a4: mov r4,#0`; wenn ausgeführt, schreibt es null. Danach `0x136ac: b 0x13710`. Evidence `ev_57491457…`; Mapping `ev_a3b847d7…`. |
| `0x137a4` | `0x37a4` | READ | `ldr r2,[r5,#0x10]` | lädt den Vor-Update-Wert nach `r2`. Evidence `ev_511ab16b…`; Mapping `ev_7f64b642…`. |
| `0x137b4` | `0x37b4` | WRITE | `str r3,[r5,#0x10]` | `0x137b0: add r3,r2,#1`; danach folgen `0x137b8: add r3,sp,#0x5c` und `0x137bc: bl 0x12ddc`. Schreibt also vor dem Call den gelesenen Wert plus eins. Evidence `ev_7298fb86…`; Mapping `ev_e3511393…`. |
| `0x1432c` | `0x432c` | READ | `ldr r3,[r7,#0x10]` | lädt nach `r3`; begrenztes Fenster danach vergleicht `r3` mit `r6` und verzweigt. Evidence `ev_58585f06…`; Mapping `ev_e7febee3…`. |

Die vollständigen Beleg-IDs, Maschinenbytes, Instruktionsfenster und Xref-Metadaten stehen in [evidence.json](evidence.json). Die Auslassung in der Tabelle betrifft nur die Anzeige der IDs, nicht die Xref-Tabelle.

## Klassifikation, Beobachtung und Schlussfolgerung

**Beobachtet:** Vier der sechs materialisierten Xrefs sind Reads und zwei sind Writes. `0x136a8` ist ein direkter Store von `r4`, dem im lokalen Fenster der Wert null zugewiesen wurde. `0x137a4` liest das Zielwort; `0x137b0..0x137b4` addiert eins und schreibt es zurück. Dieser Store liegt vier Instruktionsbytes vor dem direkten Call bei `0x137bc`.

**Schlussfolgerung:** Der Write bei `0x137b4` ist eine Aktualisierung eines zuvor gelesenen Werts, kein Beleg dafür, was vor der ersten Iteration im Speicher lag. Der Store bei `0x136a8` ist ein möglicher expliziter Null-Store, aber sein Ausführungs- und Reihenfolgeverhältnis zum Call bei `0x137bc` ist durch die hier begrenzten Xref-Fenster nicht belegt. Die übrigen drei direkten Reads liefern keinen Anfangswert. Deshalb beweisen die materialisierten direkten Zugriffe weder eine statische Initialisierung noch einen ersten Wert vor dem Call.

**Alternativerklärung:** Falls der Code bei `0x136a8` vor der Loader-Call-Lane ausgeführt wird, kann er den ersten Wert auf null setzen. Eine ELF-Laufzeit könnte `.bss` außerdem gemäß ihren Lade-/Initialisierungsregeln behandeln. Beide Erklärungen sind mit den statischen Daten vereinbar, aber weder die Kontrollflussreihenfolge des ersten Stores noch eine konkrete Laufzeitbeobachtung ist in diesem WP nachgewiesen.

**Unbekannt / Restunsicherheit:** Kontrollfluss und Ausführungsreihenfolge von `0x136a8` zum ersten `0x137bc`; tatsächliche Laufzeitinitialisierung bzw. ein Runtime-Ladebias; Zugriffe über nicht materialisierte oder indirekte Aliase; API-/Feldsemantik. Die sechs Einträge sind vollständig für die von Ghidra materialisierten direkten Referenzen zum exakten Ziel, aber nicht als Vollständigkeitsbeweis für indirekte Runtime-Zugriffe zu verstehen.

## Methode, Abdeckung und Status

REA war die primäre Methode: Target geöffnet, Literalbytes gelesen, Xrefs zum berechneten Ziel abgefragt, jede direkte Xref-Instruktion in einem begrenzten Fenster inspiziert, Speicherblöcke klassifiziert und dateigebundene Instruktionen auf Datei-Offsets abgebildet. Der einzige Fallback war `readelf -SW` 2.44 für die ELF-Sektionsart/-adresse, weil REA diese ELF-Rohmetadaten nicht ausgab und das Ziel ausdrücklich nicht file-backed war. Kein GNU-Disassembly-Fallback wurde für diese Xrefs neu ausgeführt. WP097-Bericht und dessen begrenzter ARM-`objdump`-Auszug wurden nur als akzeptierter, frisch gehashter Kontext verwendet; der generische Loader-Body und Dispatcher außerhalb der genannten Instruktionsfenster wurden nicht erneut untersucht.

**Tests:** `PASS` — reproduzierbarer Validator `python3 validate.py`; `NOT_RUN` — zusätzliche Tests (nicht Bestandteil dieses Offline-Analysepakets).

**Self-Review:** durchgeführt; kein unabhängiger Review behauptet. Es wurden nur Dateien in diesem WP-Ausgabeverzeichnis angelegt. Keine Repository-, gemeinsame Evidenz-, Geräte-, Netzwerk- oder VM-Datei wurde geändert.
