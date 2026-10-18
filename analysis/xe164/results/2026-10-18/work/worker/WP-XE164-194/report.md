> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-194 — direkte Referenzen des IoDrvDal-ELF auf Provider-Slots

## Ergebnis

Für keine der drei vorgegebenen Adressen wurde in der statischen Prüfung eine direkte oder literalgebundene Referenz im untersuchten `libIoDrvDal.so.1.0.2` festgestellt. Der Befund ist für direkte Xrefs und absolute Little-Endian-Literale `VERIFIZIERT`, jeweils nur innerhalb der unten beschriebenen Methoden. Ob Code die Slot-Adressen über mehrstufige Laufzeitberechnungen, externe Daten oder vom Loader gelieferte Werte herleitet, bleibt `OFFEN`.

Die Slot-Adressen werden hier ausschließlich als vorgegebene Werte behandelt. Das Ergebnis weist ihnen keine Semantik zu.

Diese Fassung ersetzt die erste Berichtsfassung: Für die Ghidra-Abfragen werden nun die ELF-VMAs mit der nachgewiesenen Image-Base `0x10000` auf den Ghidra-Adressraum abgebildet. Die Xref-Befunde unten stammen aus neuen Abfragen an den übersetzten Adressen; die früheren Abfragen an unübersetzten Adressen werden nicht als Befund verwendet.

## Eingabe und Identität

- Datei: `sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`
- Größe: 25.976 Bytes
- Erwarteter und beobachteter SHA-256: `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`
- Eingabehash: `PASS`
- ELF: ELF32, little-endian, `ET_DYN`, ARM, GNU EABI5, hard-float
- Slot-Adressen separat bilanziert:

| Slot (ELF-VA) | Ghidra-Adresse (+`0x10000`) | Ghidra Xrefs | Absolute Bytefolge (ELF-VA, Little-Endian) | Direkter Xref-Befund | Literal-Befund |
|---|---:|---:|---|---|---|
| `0x1a2a0` | `0x2a2a0` | 0 | `a0 a2 01 00` | `VERIFIZIERT`: Xref-Liste am rebasierten Ziel leer | `VERIFIZIERT`: Bytefolge im gesamten ELF nicht gefunden |
| `0x1a2ac` | `0x2a2ac` | 0 | `ac a2 01 00` | `VERIFIZIERT`: Xref-Liste am rebasierten Ziel leer | `VERIFIZIERT`: Bytefolge im gesamten ELF nicht gefunden |
| `0x1a2b0` | `0x2a2b0` | 0 | `b0 a2 01 00` | `VERIFIZIERT`: Xref-Liste am rebasierten Ziel leer | `VERIFIZIERT`: Bytefolge im gesamten ELF nicht gefunden |

## Beobachtungen und genaue Fundstellen

1. REA `open_binary` band genau die Eingabedatei mit Provider `ghidra`; erkannte Identität: ELF, ARM und der oben genannte SHA-256.
2. Die Auftragswerte sind ELF-VMAs. REA `list_segments` meldet Image-Base `0x10000`; daher sind die Ghidra-Ziele `ELF-VA + 0x10000`: `0x2a2a0`, `0x2a2ac` und `0x2a2b0`. REA/Ghidra 12.1.4 lieferte bei `xrefs(address)` an diesen drei rebasierten Zielen jeweils `normalized_result: []` und `locations: []`. Evidence-IDs:
   - `0x2a2a0`: `ev_20a2196a0bbfa0ae601555a40c84d074ed1a0dad288b6ca3441e96eca34d21bf`
   - `0x2a2ac`: `ev_fa1438558fbf1174410490940b87eb458b2ccea91ff2129ea26eac216609ce14`
   - `0x2a2b0`: `ev_bc231e3118b13a3dfdc44743c6cabcbc638a9b11d4bd701762d35f55a58f55b7`
3. Dieselbe Segmentliste weist `.bss` als nicht initialisierten, les-/schreibbaren Block `[0x26088,0x2a30c)` aus. Alle drei korrekt rebasierten Ghidra-Ziele liegen innerhalb dieses Blocks, bei Offsets `0x4218`, `0x4224` und `0x4228` ab dessen Anfang. Das Ende des Blocks ist exklusiv. Evidence-ID für Image-Base und Blockgrenze: `ev_cd2cf5d558dd27b52c198df044b7ae0e6f920c8a0b2001a5d5d5bbb913194140`.
4. ELF `PT_LOAD`-Header: ausführbarer LOAD-Bereich hat Datei-Offset `0x0`, VMA `0x0`, `FileSiz=0x552c`, Flags `R E`; der weitere LOAD-Bereich ab Datei-Offset/VMA `0x5e20` ist `RW`, nicht ausführbar. Die ELF-Sektionen mit `SHF_EXECINSTR` sind `.init` (VMA/Offset `0x948`, Größe `0x0c`), `.plt` (`0x954`, `0xe0`), `.text` (`0xa34`, `0x3c44`) und `.fini` (`0x4678`, `0x08`).
   Die ELF-Sektion `.bss` ist `NOBITS` bei VMA `0x16088` mit Größe `0x4284`; folglich enthält sie die ELF-VMAs `[0x16088,0x1a30c)`, darunter alle drei Slots. Dies wird durch `readelf -SW` verifiziert; die Ghidra-Adresse entsteht durch die belegte Image-Base `0x10000`.
5. GNU ARM objdump 2.44 wurde über genau diese vier `SHF_EXECINSTR`-Sektionen mit `-d -r` ausgeführt. Eine fokussierte Suche in dieser Disassemblierung fand weder die drei ELF-VA-Zielwerte noch ihre Kurzformen `0xa2a0`, `0xa2ac`, `0xa2b0` als Text. Die Ausgabe zeigte ARM/ARMv7-PIC-Muster mit PC-relativen Literalen. `movw` kommt für andere Konstanten vor; es wurde aber kein `movw`-Immediate `0xa2a0`, `0xa2ac` oder `0xa2b0` und kein `movt`-Immediate `0x1` beobachtet, die zusammen jeweils einen der drei ELF-VA-Werte bilden würden.
6. Unabhängig davon wurde das gesamte file-backed Eingabe-ELF byteweise auf die drei exakten 32-Bit-Little-Endian-Folgen für ELF-VMAs durchsucht. Keine Folge wurde gefunden. Auch die drei Little-Endian-Folgen für die Ghidra-rebasierten Ziele `0x2a2a0`, `0x2a2ac`, `0x2a2b0` wurden nicht gefunden. Dieser Test deckt absolute 32-Bit-Literale auch dann ab, wenn der Pool außerhalb der `.text`-Sektion liegt; er erfasst keine Laufzeitinhalte in der `NOBITS`-Sektion `.bss`.
7. REA `inspect_with_objdump(operation="disassemble_all")`: `FAIL` (Exit-Code `1`, `objdump: can't disassemble for architecture UNKNOWN!`); Evidence-ID `ev_32e5f8d839553f1e0f61573c16f725ad5561fad2bbfb288b6dc30a08d82d8efe`. Das war eine REA-Provider-Lücke, kein ELF-Befund. Dieser identische REA-Aufruf wurde nicht wiederholt.

## Direkte und hergeleitete Referenzen

- **Direkt / Ghidra-Xrefs:** drei leere Xref-Ergebnisse an den korrekt rebasierten Ghidra-Adressen `0x2a2a0`, `0x2a2ac` und `0x2a2b0`. Das ist eine Beobachtung des Ghidra-Referenzmodells; sie beweist allein keine Abwesenheit sämtlicher indirekter oder nicht erkannter Kanten.
- **Literalgebunden / absolute 32-Bit-Pointer:** die drei Little-Endian-Folgen fehlen im ganzen ELF. Damit gibt es in diesem ELF kein unverändertes absolutes 32-Bit-Literal, das genau einen dieser drei Werte trägt.
- **Lokal hergeleitet / Instruction- und Wertfluss:** keine MOVW/MOVT-Halbkombination für die vorgegebenen Werte wurde in der textuellen ARM-Disassemblierung identifiziert. Ein vollständiger symbolischer Wertflussbeweis über alle Pfade wurde nicht durchgeführt; dieser Teilbefund bleibt `OFFEN`.

## Suchvollständigkeitsgrenze

Die rohe Literalsuche umfasste alle 25.976 file-backed Bytes, also auch nicht ausführbare Pools, und prüfte getrennt die ELF-VA- und die Ghidra-rebasierte Form jedes Slot-Zeigers. `NOBITS`-Speicher in `.bss` hat keine Bytes im Eingabefile und kann durch diesen Suchlauf nicht als Inhalt untersucht werden. Die Disassemblierung umfasste alle vier ELF-Sektionen mit `SHF_EXECINSTR` und deren eingebettete Wörter, soweit GNU objdump sie als Code oder Daten ausgab. Die ausführbare LOAD-Region `0x0..0x552c` wurde durch die Dateiidentität und ELF-Header abgegrenzt; das ist keine Behauptung, dass jede Byteposition der LOAD-Region eine Instruktion ist.

Die Xref-Ergebnisse sind auf Ghidras geladenes ELF beschränkt. Ghidra bildet die korrekt rebasierten Ziele in `.bss` ab; der direkte Xref-Aufruf liefert dennoch je Ziel keine eingehenden Referenzen. Die lokale Disassemblierungssuche ist textuell und keine vollständige symbolische Ausführung. Insbesondere bleiben dynamisch geladene Werte, externe Basen, Laufzeitrelokationen mit nicht eingebetteten Symbolwerten und indirekte Datenflüsse unbewertet.

## Alternativerklärung und Restunsicherheit

Eine plausible Alternative zu eingebetteten Slot-Zeigern ist eine zur Laufzeit symbolisch oder über eine vom Host bereitgestellte Basis aufgelöste Funktionstabelle. Das ist eine mögliche Erklärung für das Fehlen absoluter Zeiger, keine verifizierte Aussage über dieses ELF. Ob diese Bibliothek die Slots zur Laufzeit überhaupt benutzt, ist mit diesem statischen, adresseingeschränkten Paket `OFFEN`.

## Werkzeuge und Versionen

- REA `rea-agents` 6.5.0; Session-Client Codex MCP 0.163.0.
- Ghidra 12.1.4, Provider `ghidra`, Analyseprofil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- GNU ARM objdump `arm-linux-gnueabihf-objdump`, GNU Binutils 2.44.
- GNU `readelf`, GNU Binutils 2.44.
- Rizin war lokal mit Version 0.9.1 vorhanden, wurde für diesen Befund nicht benötigt.

## Tests und reproduzierbarer Validator

Alle Tests in [validate.sh](validate.sh) sind Offline- und Read-only-Prüfungen. Letzter Lauf:

- Eingabeidentität: `PASS`
- ARM-ELF-Identität: `PASS`
- `.bss`-Layout und Zugehörigkeit der drei ELF-VMAs sowie korrekt rebasierten Adressen: `PASS`
- alle drei exakten Little-Endian-Literale im gesamten ELF: `PASS` (keines gefunden)
- alle drei Ghidra-rebasierten absoluten Little-Endian-Literale im gesamten ELF: `PASS` (keines gefunden)
- Zielwerte in ARM-Disassemblierung der ausführbaren Sektionen: `PASS` (keine textuelle Erwähnung)
- zielwertige MOVW/MOVT-Halbkombination in ausführbaren Sektionen: `PASS` (nicht gefunden; MOVW-Instruktionen für andere Werte sind vorhanden)

Diese Tests verifizieren nur die jeweils bezeichneten Suchmethoden. Sie behaupten nicht, dass indirekter Wertfluss oder Laufzeitverhalten ausgeschlossen wurde.

Erzeugte Dateien: `report.md`, `validate.sh`. Ihre SHA-256-Werte sind in [SHA256SUMS](SHA256SUMS) festgehalten.
