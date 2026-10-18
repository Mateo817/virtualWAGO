> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-199 — gezielte Gegenprüfung der Tabellenaufrufe

## Ergebnis

**VERIFIZIERT:** Im vollständigen Instruktionskörper von `idk_IoDrvReadInputs` gibt es vier `blx`-Aufrufe, deren aufgerufene Zielwörter aus einem bei `X+0x61c` geladenen Tabellenzeiger und einem hier sichtbaren Tabellenversatz stammen: `+0x44`, `+0x54`, `+0x58` und `+0x50`. Drei verwenden den Funktionskontext aus `*param_1` (`r9`); der `+0x58`-Aufruf verwendet den in einem Listeneintrag stehenden zweiten Kontext (`r8`). Die lokalen `r0`-Verwendungen sind unten ausschließlich syntaktisch beschrieben.

Eingabe: `libIoDrvKbus.so.0.0.1`, 38.584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` (**PASS**). Unveränderte Same-Hash-Vorarbeit: WP-XE164-092/`observations.md` und WP-XE164-082/`report.md`; das dortige Ghidra-Dossier E1 identifiziert denselben Funktionsnamen, dieselbe Grenze und dasselbe Profil. Diese fokussierte Prüfung fragt nur nach den aus `+0x61c` geladenen Tabellenpositionen, sichtbaren Argumenten und dem lokalen `r0`-Fluss.

## Adress- und Evidence-Bindung

- Symbol: ELF-VA `0x6120`, Größe `0x388`/904 Byte. `readelf -Ws` meldet `FUNC GLOBAL`; `.text` beginnt bei VA/Dateioffset `0x1eb8`.
- Ghidra 12.1.4 bildet den untersuchten Abschnitt in diesem ELF auf `0x16120..0x164a7` ab. REA `address_to_file_offset` bildet `0x16120` auf Datei-Offset `0x6120` und `0x1649c` auf `0x649c` ab. Der Funktionskörper ist `[0x16120,0x1649c)` (Ghidra-Body mit inklusivem Ende `0x1649b`); die direkt gelesenen zwölf Poolbytes sind `[0x1649c,0x164a8)`. Der Read von 904 Bytes ab `0x16120` war vollständig.
- Statischer Adressbias für diesen Abschnitt: Ghidra-Adresse = ELF-VA + `0x10000`. Das folgt hier aus den REA-Source-Mappings und der Offset-/VA-Gleichheit in `.text`; es wird nicht auf die Laufzeitadresse übertragen.
- Frische REA-Evidence: Dossier `ev_b7d4a4f8ff0b01666eb873a3a12548e96672c1ce1c1d6aaa27291851eaf591e6`; vollständiger Byte-Read `ev_e10e0f5af410b99e180c3bf7438224c0f41acfef1a2a949c804c906bfb34db70`; Adressabbildungen `ev_98ab0d8ed36730f5b1b28f3ae56947b7d45efb2f18fb744a227986c7e5be78a3` und `ev_913a5871cd907f2da8acc3434447bba21ddf3f53a3f2286722e7b19d94d760cc`.
- Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; REA 6.5.0, Provider Ghidra 12.1.4. Gezielter Fallback: GNU `arm-linux-gnueabihf-objdump` 2.44; `readelf` 2.44. Keine Ausführung des ELF.

## Qualifizierende Aufrufe

`r9` wird bei ELF `0x6128` aus `*param_1` geladen. `r8` wird bei ELF `0x61b4` aus dem Feld `+8` des aktuellen 16-Byte-Eintrags geladen. „Stackargument“ meint ausschließlich ein vor dem Call sichtbar auf dem Stack bereitgestelltes Wort; es wird keine API-Signatur angenommen.

| ELF-VA / Ghidra-VA | Tabellenherkunft und Position | Zielwort / Call-Wort | Unmittelbar sichtbare Registerargumente | Sichtbare Stackargumente | Lokaler `r0`-Fluss |
|---|---|---|---|---|---|
| `0x6144` / `0x16144` | `r9` aus `*param_1`; `ldr r3,[r9,#0x61c]` bei `0x6138`, danach `ldr r3,[r3,#0x44]` bei `0x6140` | Zielwort in `r3`; `blx r3`, Opcode `e12fff33` | `r0=[r9+0x618]`; `r1=0`. `r2` ist hier nicht neu gesetzt; `r3` enthält das Zielwort. | Keines sichtbar eingerichtet. | Rückgabe-`r0` wird bei `0x6148` mit `subs r4,r0,#0` getestet und in `r4` gespeichert. Nichtnull verzweigt bei `0x614c` zum gemeinsamen Rückgabepfad, der `2` setzt. Null lässt `r4=0` für den weiteren Ablauf. |
| `0x6188` / `0x16188` | dasselbe `r9`-Tabellenwort, bei `0x6178`; `ldr r3,[r3,#0x54]` bei `0x6184` | Zielwort in `r3`; `blx r3`, Opcode `e12fff33` | `r0=[r9+0x618]`; `r1=0`. `r2` ist hier nicht neu gesetzt; `r3` enthält das Zielwort. | Keines sichtbar eingerichtet. | Rückgabe-`r0` wird verworfen. Bei `0x618c` wird `r0` aus dem lokalen `r4` neu berechnet. Auf diesem erreichbaren Normalpfad ist `r4=0` aus dem vorherigen erfolgreichen Nulltest; die abschließende Verschiebung ergibt deshalb `r0=0`. |
| `0x61d8` / `0x161d8` | `r8` aus dem Eintragsfeld `+8`; `ldr r3,[r8,#0x61c]` bei `0x61c0`, danach `ldr r7,[r3,#0x58]` bei `0x61d0` | Zielwort in `r7`; `blx r7`, Opcode `e12fff37` | `r0=[r8+0x618]`; `r1=0`; `r2=0`; `r3=sp+0x24` (Adresse des lokalen Ausgabe-Worts). | Kein zusätzliches Argument in `[sp]`; `r3` zeigt auf den Stackausgabespeicher. | Rückgabe-`r0` wird bei `0x61dc` getestet. Bei Null wird `[sp+0x24]` geprüft: wenn das Wort `1` ist, bleibt `r0=0`; sonst wird `r0=1`. Bei Nichtnull wird ebenfalls `r0=1`. Dieses syntaktisch abgeleitete Byte wird bei `0x620c` nach `strb` gespeichert; es ist kein unverändert weitergereichter Rückgabewert. |
| `0x6470` / `0x16470` | `r9`-Tabellenwort wird bei `0x6444` in `lr` geladen; `ldr r4,[lr,#0x50]` bei `0x6468` | Zielwort in `r4`; `blx r4`, Opcode `e12fff34` | `r0=[r7]`; `r1=0`; `r2=[r7+0x0c] + (u16[r5+8] >> 3)`; `r3=min((u16[r5+0x0c] >> 3),[r7+0x10])`, nach dem vorherigen Vergleich bei `0x6448`. | `[sp]=r10 + (u16[r5+0x0a] >> 3)`, sichtbar gespeichert bei `0x6460`. | Rückgabe-`r0` wird bei `0x6478` nach `r4` kopiert. Der folgende Eintragscallback bei `0x6488` bekommt neue `r0/r1`-Werte; dessen Rückgabe wird nicht sichtbar nach `r4` kopiert. Der Körper prüft das bei Abschluss vorliegende `r4` bei `0x618c` auf Null/Nichtnull. Ob ein zwischenliegender Callee `r4` erhält, wird hier nicht aus einem Calling-Convention-Vertrag abgeleitet; spätere Transfers schreiben `r4` erneut. |

Die Tabelle ist direkt an ARM-Wörter aus dem selektiven GNU-Disassembly gebunden:

| Funktion des Worts | ELF-Adresse | 32-Bit-Opcodewort | Instruktion |
|---|---:|---:|---|
| Tabellenbasis aus `r9` | `0x6138` | `e599361c` | `ldr r3,[r9,#0x61c]` |
| Laden von `+0x44` | `0x6140` | `e5933044` | `ldr r3,[r3,#0x44]` |
| erster Call | `0x6144` | `e12fff33` | `blx r3` |
| Laden von `+0x54` | `0x6184` | `e5933054` | `ldr r3,[r3,#0x54]` |
| zweiter Call | `0x6188` | `e12fff33` | `blx r3` |
| Tabellenbasis aus `r8` | `0x61c0` | `e598361c` | `ldr r3,[r8,#0x61c]` |
| Laden von `+0x58` | `0x61d0` | `e5937058` | `ldr r7,[r3,#0x58]` |
| dritter Call | `0x61d8` | `e12fff37` | `blx r7` |
| Tabellenbasis aus `r9` | `0x6444` | `e599e61c` | `ldr lr,[r9,#0x61c]` |
| Laden von `+0x50` | `0x6468` | `e59e4050` | `ldr r4,[lr,#0x50]` |
| vierter Call | `0x6470` | `e12fff34` | `blx r4` |

## Ausschlussbilanz und lokale Behandlung übriger `r0`-Werte

Alle erkannten Call-Operationen im Körper sind in Ghidras aktuellem Dossier aufgeführt. Außer den vier qualifizierenden Calls sind sichtbar: `bl 0x1590c` bei `0x6344`, ein direkter lokaler Aufruf; `blx r3` bei `0x63d0` und `0x6488`, beide mit Ziel aus dem jeweiligen 20-Byte-Eintrag; `bl 0x15b5c` bei `0x6410`, ein direkter lokaler Aufruf; und `bl 0x11d40` bei `0x6434`, der PLT-Thunksprung zu `memset`. Keiner erhält sein Zielwort aus einem an `+0x61c` geladenen Tabellenwort.

Bei `0x6400` lädt der Körper zwar zusätzlich `[r9+0x61c]` und übergibt den Wert als Argument in `r2` an den direkten lokalen Call `0x6410`. Es wird daraus an dieser Stelle kein Tabellenwort geladen; daher ist `0x6410` keine Tabellenposition. Seine Rückgabe bleibt bis zum gemeinsamen Block `0x6478` in `r0` und wird dort nach `r4` kopiert; der Körper prüft das zu diesem Zeitpunkt vorliegende `r4` bei `0x618c` auf Null/Nichtnull. Ein Verhalten des zwischenliegenden Callees gegenüber `r4` wird nicht angenommen. Der Rückgabewert des direkten Calls `0x6344` wird bei `0x6348` nach `r8` kopiert und als lokales Gate weiterverwendet. Der `memset`-Rückgabewert in `r0` wird nach `0x6434` nicht als lokaler Transferstatus verwendet. Der erste Eintragscallback bei `0x63d0` liefert `r0`, das bei `0x63dc` in `r10` aufbewahrt und im Folgepfad weiterverwendet wird; das ist ein anderer Ursprung als das `+0x61c`-Tabellenwort. Die Rückgabe des zweiten Eintragscallbacks bei `0x6488` wird lokal verworfen.

Die `+0x58`-Tabelle stammt von `r8`, nicht vom ursprünglichen `r9`-Kontext. Falls „context“ enger nur `*param_1` meint, sind dessen Positionen `+0x44`, `+0x54` und `+0x50`; `+0x58` ist separat ausgewiesen, weil der Körper dieselbe `+0x61c`-Lade-/Tabellenderefenzierung für den anderen explizit sichtbaren Kontext ausführt.

## Beobachtung, Alternativerklärung und Restunsicherheit

- **VERIFIZIERT:** Die vier Positionsdisplacements und Call-Instruktionen sind aus dem exakten Körper direkt gebunden; Ghidra-Dossier und vollständiger Byte-Read besitzen dieselbe Artefaktidentität. Die gezielte ARM-Disassembly stimmt an den genannten Adressen samt Opcodewörtern mit REA überein.
- **HYPOTHESE:** Die syntaktischen Abläufe entsprechen indirekten Funktionsaufrufen über geladene Tabellenpositionen. Dies benennt keine API und beweist weder Objektlayout über die verwendeten Bytebezüge hinaus noch Laufzeitziele.
- **OFFEN:** Tatsächliche Zieladressen der vier geladenen Wörter, Semantik der Positionen, genaue Callee-Verträge/Nebenwirkungen und die Laufzeitwerte bleiben unbekannt. Es fand keine Ausführung statt.
- **OFFEN:** Die Bedeutung der beiden Kontextwerte und der in `r0` sichtbaren Rückgabewerte ist nicht durch die lokalen Instruktionen allein feststellbar.

## Validator und Ausgabedateien

`bash validate.sh` prüft den Eingabehash, den ELF-Symboleintrag, GNU-Toolversionen und zwölf qualifizierende Load-/Call-Opcodes an ihren angegebenen Adressen. **PASS** bedeutet ausschließlich, dass diese statischen Identitäts- und Instruktionsanker vorhanden sind; es ist kein Runtime- oder Geräte-Test. Validatorlauf: `PASS`; Runtime-Ausführung: `NOT_RUN`.

Self-Review: eigener Abgleich von REA-Dossier, vorhandener Same-Hash-Evidence, ELF-Symbol-/Sektionstabelle, selektiver ARM-Disassembly und vollständigem REA-Byte-Read; kein unabhängiges Review behauptet.

| Datei | Rolle |
|---|---|
| `report.md` | Befund, Argumente, `r0`-Fluss, Grenzen und Methode |
| `rea-evidence.bundle.json` | Vier frische REA-Datensätze: Dossier, Byte-Read und zwei Adressabbildungen |
| `validate.sh` | Reproduzierbarer Offline-Validator |
| `SHA256SUMS` | Prüfsummen der Eingabe, Aufgabenbeschreibung und drei erzeugten Dateien; Manifest-Selbsthash ausgenommen |
