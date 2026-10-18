> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-140 — Initialisierung des lokalen Objekts vor `blx r2`

## Ergebnis

**VERIFIZIERT (statische Artefaktbeobachtung):** Vor `0x002FC5C8: blx r2` schreibt der Helper Werte in genau diese relativen Positionen des lokalen Objekts mit Basis `fp - 0x5c`:

| Relativer Offset | Breite | Geschriebener Wert | Quellinstruktion(en) | Zielidentität aus Symbolmetadaten |
|---:|---:|---:|---|---|
| `+0x04..+0x0b` | 8 Byte | `0x0000000000000000` | `0x2fc534 vmov.i32 d16,#0`; `0x2fc564 vst1.32 {d16},[ip]`, mit `ip=fp-0x58` | Nullinitialisierung |
| `+0x0c` | 4 Byte | `0x00000000` | `0x2fc56c str r6,[fp,#-80]`, nach `mov r6,#0` | Nullinitialisierung |
| `+0x18` | 4 Byte | `0x00000000` | `0x2fc574 str r6,[fp,#-68]` | Nullinitialisierung |
| `+0x1c` | 4 Byte | `0x003007c0` | `movw r3,#0x7c0`; `movt r3,#0x30`; `str r3,[fp,#-64]` | `CMRegisterAPI` (ELF dynsym) |
| `+0x20` | 4 Byte | `0x002fe158` | `movw r3,#0xe158`; `movt r3,#0x2f`; `str r3,[fp,#-60]` | `CMGetAPI` (ELF dynsym) |
| `+0x24` | 4 Byte | `0x002fecc4` | `movw r3,#0xecc4`; `movt r3,#0x2f`; `str r3,[fp,#-56]` | `CMCallHook` (ELF dynsym) |
| `+0x28` | 4 Byte | `0x0030066c` | `movw r3,#0x66c`; `movt r3,#0x30`; `str r3,[fp,#-52]` | Kein exakter ELF-Symboltreffer; Adresse belegt, symbolische Identität offen |
| `+0x2c` | 4 Byte | `0x003004f4` | `movw r3,#0x4f4`; `movt r3,#0x30`; `str r3,[fp,#-48]` | `CMCreateInstance` (ELF dynsym) |
| `+0x30` | 4 Byte | `0x002fdbb0` | `movw r3,#0xdbb0`; `movt r3,#0x2f`; `str r3,[fp,#-44]` | `CMRegisterAPI2` (ELF dynsym) |
| `+0x34` | 4 Byte | `0x002fe12c` | `movw r3,#0xe12c`; `movt r3,#0x2f`; `str r3,[fp,#-40]` | `CMGetAPI2` (ELF dynsym) |
| `+0x38` | 4 Byte | `0x0030057c` | `movw r3,#0x57c`; `movt r3,#0x30`; `str r3,[fp,#-36]` | `CMDeleteInstance2` (ELF dynsym) |

Die Stackbasis wird durch `0x2fc55c: sub r0,fp,#92` als `fp - 92` Dezimal, also `fp - 0x5c`, bestimmt. ARM-Disassembler-Immediates in dieser Tabelle sind dezimal dargestellt, sofern nicht ausdrücklich hexadezimal markiert. Beispiel: Operand `#64` in `[fp,#-64]` ist `-64` dezimal (`-0x40`), somit relativ zur Basis `fp-92` der Offset `+28` dezimal (`+0x1c`). Der letzte Store im abgegrenzten Bereich schreibt nach `fp-36`, also `+56` dezimal (`+0x38`).

Die Aufrufregister unmittelbar bei `blx r2` sind hier nur Grenzmarke: `r2` wurde bei `0x2fc554` aus dem übergebenen Block `+0x10` geladen, `r0` hält seit `0x2fc55c` die lokale Basis. Die Semantik der oben genannten Funktionsadressen wird nicht aus den Adressen abgeleitet. Sieben Adressen sind exakt durch ELF-Dynsym benannt; für `0x0030066c` fand `readelf -Ws` keinen Symbolwertgleichstand. Es wird dafür kein Name oder Vertrag ergänzt.

## Eingabebindung und Adressdomänen

| Eingabe | Größe | SHA-256 | Verwendung |
|---|---:|---|---|
| `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3` | 5,181,396 Byte | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | Zielbinärdatei |
| `WP-XE164-125/report.md` | 7,604 Byte | `5008f6d6f1ff8b5259c3a59543bd73e210a655fe1865861a201581d1c5dece16` | Nur akzeptierter Helper-/Adresskontext; keine neue Semantik daraus |
| `WP-XE164-125/function-disassembly.txt` | 3,392 Byte | `de11be1f744ffd81096202a80d8ec0c971049c9cfcd2357c8b47756b738f7621` | Kontext/Gegenprüfung; Pre-call-Instruktionen separat mit begrenztem Fallback reproduziert |

Die drei vorgegebenen Größen und Hashes wurden lokal erneut geprüft und stimmten überein. ELF `.text`-VMA beginnt bei `0x0007cb10`, Dateioffset `0x0006cb10`; deshalb ist für diesen Bereich Dateioffset = VMA − `0x10000`. Die Instruktionsadressen in diesem Bericht sind ELF virtuelle Adressen und keine Dateioffsets. Der untersuchte VMA-Bereich `0x2fc530..0x2fc5cc` (Ende exklusiv, einschließlich `blx` bei `0x2fc5c8`) entspricht Dateioffset `0x2ec530..0x2ec5cc`.

## Methode, Evidence und Werkzeugkonfiguration

REA wurde zuerst verwendet: `open_binary` auf genau der angegebenen ELF-Datei mit `provider_id=ghidra`; REA meldete `elf`, Architektur `arm` und die passende SHA-256. Der Vorgängerbericht WP-XE164-125 dokumentiert für Ghidra `12.1.4`, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de` und einen Startup-Deadline-Timeout bei Helper-Funktionsabfragen (REA-Run `d1de8b2a-f129-4ac2-aaab-fcc85d5802ef`). In dieser Bearbeitung `read_function_instructions(0x002FC530)` lief bis zum REA-Timeout bei 330000 ms (Run `5c753247-f0c8-49ae-a51f-6bc261350acc`); `procedure_info` und die adressierten Namensabfragen lieferten ebenfalls keine nutzbaren Resultate. Daher wurde der nachweislich eng begrenzte Fallback verwendet; keine gleiche fehlgeschlagene Anfrage wurde wiederholt.

Fallback: GNU `arm-linux-gnueabihf-objdump` / `arm-linux-gnueabihf-readelf`, GNU Binutils `2.44`, ARM-ELF little-endian. Der Disassembly-Aufruf beschränkte sich auf `--start-address=0x2fc530 --stop-address=0x2fc5cc` und `--no-show-raw-insn`; die Symboldaten wurden nur per `readelf -Ws` abgefragt, ohne Zielkörper zu disassemblieren. Die statisch sichtbaren `movw`/`movt`-Teile werden zu 32-bit Zahlen zusammengesetzt: `((imm16_movt << 16) | imm16_movw)`. Symbolzuordnung ist ein exakter Vergleich dieses Werts mit dem ELF-Symbolwert. Für `0x0030066c` ist die numerische Adresse belegt, eine symbolische Zielidentität dagegen offen.

Das beigelegte [`rea-evidence-bundle.json`](rea-evidence-bundle.json) wurde über REA `import_evidence_bundle` aus dem WP-XE164-125 Kontextbundle (SHA-256 `e4835580ec10347a93f7271d0638cb9bf302f0d4d8eb20d32dba99d49bea5a32`) geladen und anschließend exportiert: 8 vorhandene Records, 0 Unknowns. Es enthält nur übernommene Loader-/Caller-Kontextevidenz, keinen neuen Helper-Body-Record. Die darin enthaltenen Evidence-IDs wurden unverändert erhalten: `ev_0cf9f4b5877a009c8bf610cc122e9234d1c5da4a1b964fc482a5f05ab100e211`, `ev_157ab758baa60e437ab6cef9a40f2a3261343163577c633a87d2c70225185515`, `ev_3255ab9024dd5f9517abcce92366adc81a345307f7ccfb57fbe8b3e9d4681666`, `ev_460a34c9aa551bceef068e66b01f21bbf2be0362eb055649bbd752d9b0848b5f`, `ev_4f2dd15410d2b7317c7e1c0fc0465a2e70aa66ae92ef629b2dc96168fa24d130`, `ev_bc6d54fc1eddcfec46be7b3beb8e8c69576303b809727a975e05bb8dbad87f2f`, `ev_c267eac2bdd4a75459f410e21bc6e7787b1322db3c427f055f0e5660bb6af1b7`, `ev_deabf162e0ffa3eb4279fa240e9d941054498ae47a68fd61916d41e5e84289a3`.

## Beobachtung, Schlussfolgerung und Unbekanntes

Beobachtet: die oben gelisteten Store-Instruktionen und Werte vor `0x2fc5c8`; vier Nullbereiche/Wörter und acht konstante Zeigerwörter. Schlussfolgerung: diese Schreibvorgänge initialisieren die genannten relativen Bytepositionen des per `r0` übergebenen lokalen Stackbereichs. Die Ableitung „relativer Offset“ ist reine Arithmetik aus dem direkten Basiswert `fp-92` und den direkten Stackdisplacements.

Unbekannt bleibt die deklarierte Struktur, die Feldnamen und Feldsemantik sowie die symbolische Identität des Ziels bei `0x0030066c`. Kein Laufzeitwert und keine API-Vertragssemantik ist hier belegt. `+0x28` und `+0x34` liegen innerhalb der bereits im akzeptierten Vorgängerbericht genannten Positionen; ihre Erwähnung hier beschränkt sich auf den verlangten numerischen Gegencheck.

Alternative Erklärung: falls ein Wert außerhalb dieses Codes als nicht-Code oder als alternativer Funktionszeiger interpretiert würde, ändern die Maschineninstruktionen daran nichts; die Objektinitialisierung enthält numerisch die Werte, und nur ELF-Symboldaten erlauben die hier genannten Namensbindungen. Keine semantische API-Deutung folgt daraus.

Restunsicherheit: die Ghidra-Abfrage wurde wegen des bekannten und erneut beobachteten Antwortausbleibens nicht als Beleg für auto-generierte `FUN_...`-Namen benutzt. Der nicht benannte Wert kann daher eine analysierte Funktion ohne Export-Symbol sein; der Name bleibt **OFFEN**. Der Disassembly-Beleg ist statisch und kein Laufzeittest.

## Status und Validierung

- Ergebnis: **VERIFIZIERT** für Store-Adressen, Breiten, numerische Werte und relative Offsets.
- ELF-Namensbindung: **VERIFIZIERT** für sieben exakte Dynsym-Treffer; **OFFEN** für eine adressierte, unbenannte Zieladresse.
- Tests: **NOT_RUN** (keine Produkttests; der reproduzierbare statische Paketvalidator wurde separat ausgeführt).
- Self-Review: durchgeführt; unabhängige Prüfung oder Workerläufe werden nicht behauptet.
- Validator: [`validate_wp_xe164_140.js`](validate_wp_xe164_140.js); Ausgabe [`validator-result.txt`](validator-result.txt).

## Paketdateien

`SHA256SUMS` enthält SHA-256 für alle Paketdateien außer sich selbst. Es wurden keine gemeinsamen Dateien verändert.
