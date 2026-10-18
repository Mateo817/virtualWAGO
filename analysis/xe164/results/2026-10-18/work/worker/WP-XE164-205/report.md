> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-205 — bedingter Positionsvertrag bei Getter +0x10

## Befund

**VERIFIZIERT (lokal, statisch):** Im Caller-Fenster `IoDrvDal [0x2f44,0x2f60)` wird das indirekte Ziel in `r3` aus `[r0+0x10]` geladen. Das `r0` für den anschließenden indirekten Call bei `0x2f58` wird unmittelbar davor durch `ldr r0,[r7]` gesetzt. Die `r0`-Quelle ist damit exakt ein 32-Bit-Wert aus der Speicherstelle `[r7+0]`; Herkunft/Wert von `r7` außerhalb des Fensters ist **OFFEN**.

**HYPOTHESE (ELF-übergreifend und ausdrücklich bedingt):** Falls dieser Getter-Wert zur Laufzeit auf das statische libdal-Ziel `0x327c` aufgelöst wird, kopiert `0x3280` dessen incoming `r0` nach `r4`. Nach dem opaken Call bei `0x3284` prüft der Körper dessen aktuelles `r0`. Vor dem opaken Call bei `0x3294` stellt `0x3290` den gespeicherten ursprünglichen Eingangswert aus `r4` wieder in `r0`; das belegt nur, dass dieser Wert als Argument an den Call weitergereicht wird. Dessen Rückgabewert wird bei `0x3298` nach `r3` kopiert und anschließend auf null bzw. das Byte `[r3+0x170]` geprüft. Beim Branch `0x32b0` nach `0x21d0` ist das dortige incoming `r0` weiterhin der nonnull Rückgabewert des opaken Calls `0x1f08`/Callsite `0x3294`; die Instruktionen dazwischen schreiben `r0` nicht um. Es wird nicht behauptet, dass dieser Wert mit dem ursprünglichen IoDrvDal-`r0` identisch ist.

**OFFEN:** Es gibt keinen Beleg für die Runtime-Belegung des Getter-Slots, die tatsächliche Bibliotheksbindung, die Semantik der Ziele, einen Prototyp, Typen oder eine Calling Convention. `r1`–`r3` beim IoDrvDal-Aufruf sind nicht als Eingaberegister belegt. Für libdal sind die eingehenden Werte von `r1`–`r3` nicht Teil eines beobachteten Aufrufvertrags; Effekte und Registererhalt der opaken Callees sind unbekannt. Es wird keine Kontinuität von Registern über Calls angenommen.

## Beobachtete Instruktionen und Fluss

Die vollständige maschinenlesbare Instruktionstabelle steht in `instructions.csv`: 7 Einträge für das Caller-Fenster sowie 128 Einträge für die zwei vollständigen libdal-Addressbereiche. ELF-Adressen sind statische Linkadressen; Ghidras Analyseadressen liegen in dieser Eingabe um `0x10000` höher. Die exakten Grenzen lauten `[0x2f44,0x2f60)`, `[0x327c,0x32bc)` und `[0x21d0,0x2390)`.

### Caller-Fenster `[0x2f44,0x2f60)`

| ELF-Adresse | Opcode-Wort | Beobachtung |
|---:|---:|---|
| `0x2f44` | `e5973000` | `ldr r3,[r7]` |
| `0x2f48` | `e5843618` | `str r3,[r4,#0x618]` |
| `0x2f4c` | `ebfff6a0` | direkter Call `0x9d4`; Zielwirkung opak |
| `0x2f50` | `e5903010` | `ldr r3,[r0,#0x10]` |
| `0x2f54` | `e5970000` | `ldr r0,[r7]`; unmittelbare Definition des incoming `r0` am nächsten Call |
| `0x2f58` | `e12fff33` | `blx r3`; indirekter Call, kein statischer Callee im Caller-Fenster |
| `0x2f5c` | `e1a06000` | `mov r6,r0`; sichtbare Übernahme des zurückgelieferten `r0` |

Die Zeile `0x2f50` verwendet das `r0`, das nach dem opaken direkten Call `0x9d4` vorliegt. Ob `r0` dort durch den Callee gesetzt, erhalten oder anderweitig beeinflusst wurde, bleibt offen. Für `0x2f58` ist dagegen die direkte, lokale Definition von incoming `r0` sichtbar: der Load aus `[r7]` an `0x2f54`. `r1`, `r2`, `r4`–`r12` sind im Fenster nicht vollständig hergeleitet; `r3` enthält beim Call das indirekte Ziel. Das sagt nichts über eine ABI aus.

### Zielkörper `0x327c` und `0x21d0`

REA/Ghidra meldet für den Einstieg `0x1327c` (ELF-Linkadresse `0x327c`) die vollständige, nicht zusammenhängende AddressSet `[0x121d0,0x12390)` und `[0x1327c,0x132bc)`, insgesamt 512 Bytes/128 Instruktionen. Die Bereiche decken hier ausschließlich den freigegebenen Zielkörper ab.

Im kurzen Eingangsbereich liegt der Gate-Ablauf:

| Ghidra-Adresse (ELF) | Beobachtung |
|---|---|
| `0x1327c` (`0x327c`) | Einstieg; Register werden gesichert |
| `0x13280` (`0x3280`) | `r0` nach `r4` kopiert |
| `0x13284` (`0x3284`) | direkter Call `0x12180`; Effekte opak |
| `0x13288` (`0x3288`) / `0x1328c` (`0x328c`) | `r0` wird auf null geprüft; Nullpfad zu `0x132b4` |
| `0x13290` (`0x3290`) | gespeicherter Eingang aus `r4` nach `r0` kopiert |
| `0x13294` (`0x3294`) | direkter Call `0x11f08`; Effekte opak |
| `0x13298` / `0x1329c` | Rückgabewert in `r3` kopiert; Nullpfad zu `0x132b4` |
| `0x132a0` / `0x132a4` / `0x132a8` | Byte aus `[r3+0x170]` laden, auf null prüfen; Nichtnullpfad zu `0x132b4` |
| `0x132ac` / `0x132b0` | Register wiederherstellen und zu `0x121d0` verzweigen |
| `0x132b4` / `0x132b8` | `r0` auf `0xffffffff` setzen und zurückkehren |

Im längeren AddressSet sind alle Stores: `0x121fc strb r3,[sp,#8]`, `0x12228 str r0,[r4,r3]`, `0x12230 strh r2,[r1,#4]`, `0x1227c strb r3,[r6,#0x170]`, `0x122cc str r12,[sp]`, `0x122ec str r4,[r5]`, `0x122f8 str r9,[r5,#0x38]`, `0x122fc str r3,[r5,#4]` und `0x12370 strb r3,[r6,#0x170]`. Das sind sichtbare Adress-/Breitenbeobachtungen ohne Typ- oder Feldzuordnung.

Im längeren AddressSet sind die sichtbaren Rückkehrpfade ELF `0x2364`/Ghidra `0x12364` und ELF `0x2378`/Ghidra `0x12378` (Stackkorrektur, Registerwiederherstellung, Rückkehr über `pc`). Unmittelbar davor kopieren ELF `0x235c`/Ghidra `0x1235c` bzw. ELF `0x236c`/Ghidra `0x1236c` den dann aktuellen `r8` nach `r0`; daher geben diese lokalen Pfade den jeweiligen dann aktuellen `r8`-Wert in `r0` zurück. ELF `0x2354`/Ghidra `0x12354` setzt `r8` lokal auf `0xffffffff`, danach liegt jedoch der opake Call ELF `0x2358`/Ghidra `0x12358` bei `0x12358` vor dem Kopieren nach `r0`; ohne belegte Calling Convention ist die Fortgeltung dieses Werts über den Call offen. ELF `0x2388`/Ghidra `0x12388` setzt ebenfalls `r8` auf `0xffffffff` und verzweigt ohne weiteren Call zu `0x1235c`. ELF `0x2370`/Ghidra `0x12370` setzt das Byte `[r6+0x170]` auf `1`. ELF `0x237c–0x2384`/Ghidra `0x1237c–0x12384` ruft ein opakes Ziel ELF `0x148c`/Ghidra `0x1148c` und verzweigt danach zum Pfad `0x12350`. Eingangs-Gates aus `0x12238`, `0x12254`, `0x12270`, `0x12288`, `0x12298`, `0x122a4`, `0x122e0`, `0x12308`, `0x12330` und `0x12344` kontrollieren die im vollständigen Instruktionstable sichtbaren Äste. Keine Wirkung der dortigen Callees wird vorausgesetzt.

Direkte/indirekte Callziele innerhalb dieser AddressSets werden ausschließlich als Zieladressen notiert. Es werden keine Effekte opaker Callziele behauptet. PC-relative Loads bei `0x12210`, `0x1225c` und `0x122ac` referenzieren Literalwörter außerhalb der Instruktionsbereiche; ihre Inhalte sind für den Positionsvertrag nicht nötig und wurden nicht erweitert untersucht.

## Bedingte Schlussfolgerung und Alternativerklärung

Die angenommene statische Zuordnung stammt aus der akzeptierten WP-XE164-203-Evidence: libdal-Wort bei ELF-VA `0x14164`/Dateioffset `0x4164` hat Bytes `7c 32 00 00`, der zugehörige `.rel.dyn`-Eintrag ist `R_ARM_RELATIVE` mit implizitem Addend `0x327c`; Ghidras Analysebasis `0x10000` bildet es auf `0x1327c` ab. Das ist ein statischer Addend/Analysewert, keine gemessene Ladeadresse. WP-XE164-203s Ergebnis wird hier als vorhandene akzeptierte Eingabe verwendet; die Retention-Abfrage in der aktuellen Sitzung fand dazu keine Record, daher wurden Zielkörper und Instruktionen zusätzlich neu hashgebunden geprüft.

Unter der Bedingung, dass der Wert bei Caller `0x2f50` aus Getter-Position `+0x10` zur Laufzeit tatsächlich auf den statischen libdal-Linkwert `0x327c` gebunden wird, sind folgende lokale Eingangs-/Ausgangsbeobachtungen belegt; sie ergeben wegen der opaken Calls keinen vollständigen `0`/`-1`-Vertrag:

- sichtbarer incoming Wert: `r0 := *(uint32_t *)r7` unmittelbar vor `blx r3` bei `0x2f58`;
- der Zielkörper kopiert diesen Eingang in `r4` und stellt ihn bei `0x3290` als `r0` für den opaken Call `0x1f08` wieder her. Nach diesem Call wird der aktuelle `r0`-Rückgabewert nonnull geprüft; falls auch das Byte-Gate passiert, erreicht genau dieser Rückgabewert als aktuelles `r0` den Branch `0x32b0` → `0x21d0`. Keine Identität mit dem ursprünglichen IoDrvDal-`r0` wird behauptet;
- lokal kopiert Ghidra `0x12270` (ELF `0x2270`) den aktuellen Rückgabewert des opaken Calls bei Ghidra `0x1226c` (ELF `0x226c`) nach `r8`. Spätere opake Calls im Sekundärkörper können `r8` beeinflussen; ebenso liegt beim Pfad ELF `0x2354` der opake Call ELF `0x2358` zwischen lokalem Setzen von `r8=-1` und dem Kopieren nach `r0`. Die Epiloge ELF `0x235c`/`0x236c` (Ghidra `0x1235c`/`0x1236c`) kopieren jeweils den dann aktuellen `r8` lokal nach `r0` und kehren bei ELF `0x2364`/`0x2378` (Ghidra `0x12364`/`0x12378`) über `pc` zurück. Der Pfad ab ELF `0x2388` setzt `r8=-1` und erreicht ELF `0x235c` ohne weiteren Call. Daraus folgt kein vollständiger `0`/`-1`-Vertrag über alle Pfade. Die indirekten und direkten Callee-Effekte sowie Registererhalt bleiben opak.

Alternativerklärung: `0x327c` kann ein statischer Addend/Ziel innerhalb der ELF sein, ohne dass der IoDrvDal-Getter bei einer konkreten Runtimeinstanz auf diesen Code zeigt. Die statische Instruktionsanalyse beweist die lokale Positions-/Datenflussbeobachtung in keiner Runtime-Bindung. Runtimeadresse, Loaderentscheidung, dynamischer Slotinhalt und Hardware-/Anwendungssemantik bleiben **OFFEN / NOT_RUN**.

## Provenienz und Status

- Eingabe libIoDrvDal: 25,976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` — **PASS**.
- Eingabe libdal: 18,076 Bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` — **PASS**.
- REA/Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; libIoDrvDal-Binary-Overview Evidence `ev_ddee1478ba5248cbad795f24d4cdafc4e66b58e9a3e75c61501cf2e345ab4a46`; Caller-Instruktionen Evidence `ev_e9aa55cbd040e066c19a25467f4c5f849e90be121677920f82a140fc98a2fcf4`, `ev_b0efa46778be67cdd9414573e0cef623f64598b55dbc4fbb3b39cf5a7d98e20d`, `ev_93ff93e35a808f658d4554b19eb903c7e85de2620dd6ae5494c9c2d467859254`, `ev_57190bff5d841f5f1b8c1850e0a73623d6f885cdfac7ffefda29cb8140a9ab18`, `ev_48f9318975ad339db04a38c748b4807fa85f755c3610337dee9f6cd0bc2e6f0c`, `ev_0d5126dc355cffabc63958c340d6c04bc412ae79e02b65a06c383f567d6fa3fd`, `ev_058679b347d68e4f81a5bf3d44e48e94ef492a987bc9d8b1dd65159664d78337`; libdal vollständige Funktion Evidence `ev_42dcbbc7b73dd94863f03732927df9372550a077fb0f0a59841c7793f883610d`; libdal Overview Evidence `ev_a40e925ba5e6499cd86d0c350ecb767487473d9b374e0de0522a6091e924252f`.
- REA-Retention-Prüfung für beide SHA-256 ergab zunächst null Records. Die nicht verfügbare Wiederverwendung der älteren WP-XE164-203-Records wurde einmal festgehalten; die aktuellen Analysebeobachtungen wurden neu für die hashgebundenen Eingaben erhoben.
- Benannter roher Disassembler-Fallback: `arm-linux-gnueabihf-objdump` GNU Binutils 2.44; GNU `readelf` 2.44 prüft `.text`-Mappings; Python 3.13.5. Der Validator vergleicht alle Wörter zusätzlich mit den rohen little-endian Bytes an den aus ELF-Sektions-VA und Datei-Offset berechneten Stellen.
- Tests: **NOT_RUN** (kein Laufzeit-, Geräte-, Netzwerk- oder Produkttest angefragt oder durchgeführt). Statische Evidence-Validierung: `python3 validate.py` — **PASS**; Prüfsummen: `sha256sum -c SHA256SUMS` — **PASS**.

## Ausgabedateien und SHA-256

Die vom Auftrag erzeugten Dateien und ihre Prüfsummen stehen in `SHA256SUMS` (Manifest ausgenommen). Die Instruktionstabelle ist maschinenlesbar; `validate.py` prüft Hashes, erlaubte Grenzen, vollständige Instruktionsadressen/Opcodewörter sowie alle Tabellenzeilen.
