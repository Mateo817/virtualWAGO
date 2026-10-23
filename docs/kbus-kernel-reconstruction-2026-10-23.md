# FW31 K-Bus: Gerätebaum, Kernel und XE164-Grenze

Stand: 23.10.2026. **VERIFIZIERT** sind die unten begrenzten statischen
Artefakt-, Format- und Aufrufbefunde. **OFFEN** bleiben der vollständige untere
Ersatzvertrag und die tatsächliche Geräte-/Runtimebindung. Kernelboot,
Herstellerprogrammausführung, VM-, Zielnetzwerk- und Hardwaretests:
**NOT_RUN**. Rohbinaries, Herstellerquelltext, Disassemblierungen und private
Analysewerkzeuge bleiben außerhalb von Git.

Die [Ergebnissicherung vom 18.10.2026](../analysis/xe164/results/2026-10-18/README.md)
mit 444 Evidence-IDs bleibt unverändert. Die Fortsetzung integriert zuerst die
damals fertigen WP440–442 und untersucht danach gezielt die Gerätebaum- und
Kernelgrenze. Quellenidentitäten, Paket-/Berichthashes und Prüfscopes stehen in
der [neuen Evidence](../evidence/kbus-kernel-reconstruction-2026-10-23.json).

## Gerätebaum: Properties statt Zeichenfolgen

**VERIFIZIERT:** Zehn exakt aus dem gebundenen FW31-Image gesicherte DTBs
wurden mit lokal gebautem libfdt 1.7.2 dekodiert: 4.446 Knoten und 25.934
Properties. Knoten-/Propertywerte sind an Dateioffsets gebunden; 80 Abgleiche
mit `fdtget`, zehn mit `fdtdump` und 60 Fehler-/Mutationskontrollen sind
**PASS**.

Alle zehn Dateien enthalten denselben K-Bus-Knoten unter
`/ocp/interconnect@48000000/segment@0/target-module@30000/spi@0/kbus@0`.
Sein `compatible` lautet `wago,spi-kbus`; Knoten und unmittelbarer SPI-Elternknoten
haben `status="okay"`. `spi-max-frequency` enthält 10.000.000.

`kbus,tty-device` ist eine NUL-terminierte **Zeichenkette**:

| Dateifamilie | Anzahl | Wert | GPIO-Propertyschreibweise |
|---|---:|---|---|
| PFC100 | 2 | `ttyO4` | sechs `kbus,*-gpios` |
| PFC200 | 8 | `ttyO5` | entsprechende sechs `kbus,*-gpio` |

Die tatsächlichen GPIO-/Pinctrl-Phandlereferenzen sind getrennt aufgelöst.
Aktiv geladener Baum, GPIO-Core-Auflösung und physische Signalwirkung bleiben
**OFFEN**. Im untersuchten Kernel ruft `kbus_probe_dt` für genau
`kbus,tty-device` den gebundenen `of_property_read_string` auf. Damit ist die
statische String-Lesergrenze zusätzlich an Originalcode gebunden.

## Kernel erstmals geprüft entpackt

**VERIFIZIERT:** Die bisher nur containergeprüfte Datei `/boot/linux`
(8.213.856 Byte, SHA-256 `f6e03d6452e4648cd86f58ff5c869af0ebdcc6e8f3123458c73d6e81ccfede65`)
enthält ab Dateioffset `0x488c` einen nun validierten lzop-Stream. 74 Blöcke,
Header- und sämtliche erforderlichen Blockprüfsummen sind **PASS**. Der Stream
endet exklusiv bei `0x7d552f`; 49 nachfolgende Containerbytes bleiben separat.

Das rohe Kernelimage umfasst **19.239.516 Byte**, SHA-256
`dfa54a5a3ea91893bfd2a39add40fee571c0c653ad26e65c22b0c9d2cc9cbe78`.
Eine lokal gebaute LZO-2.10-Bibliothek und ein unabhängig gebauter
BusyBox-1.37-C-Decoder erzeugen byteidentische Ergebnisse. Beide Wege und ihre
Fehlerkontrollen sind **PASS**. Die lokale SDK-Linuxdatei ist lediglich ein
Git-LFS-Zeiger; zusätzliche Quelldownloads waren nicht nötig.

Die eingebettete Konfiguration und **46.282 komprimierte Symbole** sind
rekonstruiert. Die tatsächlichen Leseroutinen im selben Image bestätigen
Namens-/Tokendekodierung und relative Symboladressen. Fünf Leserreferenzen und
weitere Datenzeiger ergeben denselben statischen Zusammenhang:
`Linkadresse = Image-Dateioffset + 0xC0008000`.
Dies ist keine beobachtete Laufzeitadresse.

## Originaler ioctl-Handler und Transfergrenze

`kbus_ioctl` liegt bei Image-Dateioffset `0x76a5d4`, statische Linkadresse
`0xc07725d4`. **VERIFIZIERT** sind folgende numerischen Zweige:

| Request, hex | Lokale Argumentbytes | Ausgewählter Folgepfad |
|---|---:|---|
| `0x40184b01` | 24 | `kbus_data_txrx` |
| `0x401c4b02` | 28 | `kbus_cmd_txrx` |
| `0x40084b03` | 8 | lokale Zustandsübernahme und `spi_setup` |
| `0x40184b04` | 24 | `kbus_binary_txrx` |

Die ersten drei Request-/Größenpaare entsprechen exakt den zuvor untersuchten
Aufrufbildern des FW31-`libpackbus` aus **E-XE164-412**. Der vierte Zweig ist
zusätzlich gebunden. Das ist ein statischer Aufrufabgleich; ein vollständiges
C-Struct-/UAPI-Layout oder ein geladenes Gerät wird daraus nicht abgeleitet.

Die untersuchten Datenpfade übergeben Benutzerpuffer und Längen an die
gebundene Kopierroutine und bauen interne Transfers auf. Tatsächliche
Byteweitergabe setzt Kopiererfolg und erhaltene Puffer-/Objektzustände voraus.
Der Commandpfad bildet zwei Empfangsteile mit Länge sechs und `RX−6`.
Die lokalen Längenprüfungen belegen keine allgemeine Mindestlänge `RX≥6`.

Weitere relevante Grenzen:

- Der generische ioctl-Fallback prüft den Typbytewert `0x4b` nicht sichtbar
  und schreibt bereits vor seinen Auswahlprüfungen lokale Zustandspositionen.
  Eine pauschale Zurückweisung unbekannter Requests wäre keine korrekte
  Nachbildung dieses Codes.
- `kbus_spi_sync` führt über `spi_async` und einen Completion-Wait. Dieser
  Wait erhält hier kein Timeoutargument. Die früheren Zahlen 1.500/5.000
  werden deshalb nicht als qualifizierte Millisekundenverträge ausgegeben.
- Callbacktabellenrolle, wirkliche Dateisystem-/Gerätebindung, Nebenläufigkeit,
  Pointerlebensdauer und SPI-/IRQ-/DMA-Verhalten bleiben **OFFEN**.

## Gezielter Anschluss an XE164

Die über den bestehenden C166-Aufrufgraphen ausgewählte Routine im
Composite-Dateibereich `[0x31c4,0x33a8)` vergleicht dieselbe Folge von elf
Opcodewerten wie der gebundene ARM-Codec. Request-/Antwortfelder weisen eine
konkrete statische Formatübereinstimmung auf: insbesondere liegen Status,
Länge und Antwortnutzdaten bei den relativen Positionen `+2`, `+4`, `+6`.
Caller und Transferhelfer binden die logischen Puffer zusätzlich an numerische
Transferpositionen und Wortzähler. Deren Hardware-/SFR-Identität bleibt offen.
Die genaue Einordnung ist in der Evidence
mit ihren Speicher-/Registerbedingungen festgehalten.

Die Interpretation als dieselbe tatsächlich kommunizierende Befehlsfamilie
bleibt **HYPOTHESE**: Sie benötigt erhaltene aktuelle Register, die passende
DPP-/Pufferabbildung und die tatsächliche SPI-Pfadbindung. Die lokalen
Opcode-, Feld- und Transferinstruktionen sind davon getrennte statische
**VERIFIZIERTE** Befunde.

**Ein Gegenbefund verhindert die pauschale Gleichsetzung:** Beim Opcode
`0xd0` beschreibt der untersuchte L3-Zweig 24 Halbwort-Nutzdaten, während der
ausgewählte ARM-Tag-10-Pfad sechs Halbwort-Nutzdaten erwartet. Unter einer
direkten gemeinsamen Pufferabbildung passen diese Längen nicht zusammen.
Erreichbarkeit, anderer Pfad oder zusätzlicher Kontext bleiben mögliche
Erklärungen; ein tatsächlich auftretender Fehler wird nicht behauptet.

**OFFEN** bleibt insbesondere, welche physische SPI-/DMA-/SFR-Anbindung die
belegten logischen C166-Puffer tatsächlich füllt. Bloße Treffer für sechs oder
`0xa3` schließen diese Grenze nicht.

## Prüfung und nächster Arbeitspunkt

Die akzeptierten privaten Pakete besitzen feste Eingabe-/Ausgabehashes und
schreibfreie Validatoren. Root-Integration und eigene Quellprüfung sind
**Self-Review**; unabhängige Decoder- und Schnittstellenprüfungen sind in der
Evidence gesondert benannt. Die öffentliche Sicherung prüft keine private
Firmware erneut.

Als Nächstes sind der `0xd0`-Aufrufkontext und die konkrete C166-Transfergrenze
zu klären: aktuelle Register-/Pufferzustände, Auswahl des Senders/Empfängers
und deren numerische Transferpositionen. Der gebundene nächste C166-Bereich
ist `[0x1ffc,0x2192)` samt Zählerblättern bis `0x21aa`; dafür fehlen noch die
passende XE164-Derivat-/SFR- und DPP-Qualifikation. Erst ein belegter vollständiger
Vertrag trägt eine tiefere Ersatzimplementierung. Eine Architektur- oder
Emulatoränderung ist nicht Teil dieses Analyseblocks.
