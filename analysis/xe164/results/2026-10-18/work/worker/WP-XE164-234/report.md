> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-234 — bounded A32 path check

## Ergebnis

**OFFEN** für die globale Frage. In der deklarierten, vollständigen Instruktionsdekodierung wurden 4.159 registerindirekte `blx`-Sites und 473 direkte `ldr`-Loads mit `[Basisregister + 0x20]` inventarisiert. Die implementierte, pfadinsensitive Auswertung direkter Kontrollflusskanten fand null Ketten, bei denen `r0=15` und ein solcher Loadwert gemeinsam an einer registerindirekten `blx`-Site anliegen. Das ist kein globaler Nullbeweis: Nach der im Validator wörtlich implementierten Symbol-/Operandenprädikaten liegen 101 PC-relativ indizierte `ldr pc,[pc,register,lsl #2]`-Dispatches in 222 loadtragenden Symbolmarken. Ihre Tabellenziele wurden im Value-Flow nicht als CFG-Kanten verfolgt. Daher bleibt die globale Pfadfrage **OFFEN**.

## Bindung und Abdeckung

Eingabe: `codesys3`, ELF32 little-endian ARM, 5.181.396 Byte, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`. REA `open_binary` band dieselbe Eingabe an denselben SHA-256. REA-Segmentinventar (`ev_9b85e6f5e8af5904586ab0f770b0c64c4fbe51175a6643b3bc81aacf7871c13e`) weist `.text` ab VA `0x7cb10`, ausführbar und initialisiert, sowie Image-Base `0x10000` aus. `readelf -SW` bestätigt `.text`-Fileoffset `0x6cb10`, Größe `0x2c84b0`; für die gesamte Untersuchung gilt VA = Fileoffset + `0x10000`.

**REA-Gap (einmal dokumentiert):** `search_bytes`-Evidence `ev_50d5ae330427e09d1bc3a03d3db2b796691cba8e648906c91a0ba32c20d47295` deckte bei der A32-Byte-Signaturabfrage nur den ersten Page von `0x7cb10` bis `0x7d2eb` ab (`complete=false`, Fortsetzungscursor vorhanden). Diese API lieferte weder eine bereichsvollständige Instruktionsdekodierung noch Register-/CFG-Datenfluss. Daher wurde ausschließlich als benannter lokaler Fallback GNU ARM objdump verwendet.

Fallback: `GNU objdump (GNU Binutils for Debian) 2.44`, Aufruf `-D --disassemble-zeroes -j .text --start-address=0x0007cb10 --stop-address=0x00180000`. Die vollständige Ausgabe `bounded.objdump.txt` umfasst genau 265.532 fortlaufende 4-Byte-Wörter = 1.062.128 Byte, VA `[0x0007cb10,0x00180000)`, Fileoffset `[0x0006cb10,0x00170000)`. `--disassemble-zeroes` ist erforderlich, damit die Nullbytes in `.text` die Bereichsabdeckung nicht unterbrechen. `readelf` stammt ebenfalls aus GNU Binutils 2.44; Validator-Laufzeitumgebung: Python 3.13.5.

## Kandidaten und adressgebundene Ausschlüsse

Die vollständige, reproduzierbare Liste aller 4.159 Register-`blx`- und 473 `+0x20`-Load-Sites steht in `candidate-inventory.tsv`; jede Zeile enthält Typ, ELF-VA, Fileoffset, Symbolmarke und kodierte Instruktion. `cfg-gap-inventory.tsv` bindet zusätzlich alle 222 Symbolmarken und alle 101 dispatchenden Instruktionen an Adresse, Fileoffset, Kodierung und Operanden. Die Zählregel für loadtragende Symbole ist `strip_condition(mnemonic) == "ldr"` und Operand enthält exakt ein Register aus `r0..r12, ip, sp, lr, fp, sl` gefolgt von Immediate `32` oder `0x20` in `[base, #imm]`. Dispatchregel: dieselbe Symbolmarke, `strip_condition(mnemonic) == "ldr"`, Ziel `pc` und Operand `[pc, rN/ip/sl/fp, lsl #2]`. Die Zählungen sind somit parser- und regex-gebunden; breitere Syntaxnormalisierung ist nicht behauptet. Fileoffsets verwenden durchgehend die obige Image-Base-Zuordnung.

Die vier sichtbaren direkten Instruktionen `mov{cond} r0,#15` im Bereich sind:

| VA | Fileoffset | Beobachteter Kontext | Ausschluss |
|---|---|---|---|
| `0x7d040` | `0x6d040` | `mov r0,#15` | Bei `0x7d054` folgt direkt `bl sigaction@plt`; keine `blx`-Site. Die umgebende Funktion enthält keinen direkten `+0x20`-Load und liegt damit nicht in der oben gezählten 211-Funktionenmenge. |
| `0x15629c` | `0x14629c` | `mov r0,#15`; danach `movt r0,#1` bei `0x1562a0` | Vor dem direkten `bl EventOpen@@Base` bei `0x1562a4` wird der Registerwert zu `0x0001000f`, nicht 15. |
| `0x161c1c` | `0x151c1c` | `mov r0,#15`; danach `movt r0,#1` bei `0x161c20` | Vor dem direkten `bl EventOpen@@Base` bei `0x161c24` wird der Registerwert zu `0x0001000f`, nicht 15. |
| `0x176e58` | `0x166e58` | bedingtes `movle r0,#15` | Bedingter Folgezweig `ble 0x176ea8` führt zum Epilog; auf dem Nicht-`LE`-Pfad wird `r0` später überschrieben. Im untersuchten Block folgt kein `blx`. |

Adressgebundene Instruktionszeilen und angrenzender Kontrollfluss sind in `bounded.objdump.txt` enthalten. Die Auswertung ließ Bedingungen und direkte Zweige pfadinsensitiv zu (überapproximerend), propagierte jedoch **keine Registerwerte über opaque Calls**: nach `bl`/`blx` wurden `r0-r3` und `r12` als unbekannt behandelt. `+0x20`-Loads wurden als eindeutiger Marker der Ladeinstruktion fortgeschrieben; der Marker zählt nur dann als Treffer, wenn er bei einem registerindirekten `blx` im Zielregister liegt und am selben abstrakten Pfad `r0=15` vorliegt.

## Alternativerklärung und Restunsicherheit

Der beobachtete Nullbefund kann durch übersehene Pfade aus den nicht modellierten PC-relativ indizierten Sprungtabellen erklärt werden: ein Tabellenziel kann nach dem Dispatch `r0` oder das `blx`-Zielregister setzen. Die Tabellen erscheinen als A32-Instruktionen/Adresswörter in derselben `.text`-Dekodierung, wurden aber nicht als Kanten aufgelöst. Ebenfalls nicht bewiesen sind Laufzeitwerte, indirekte Ziele außerhalb des statischen Scopes oder Pfade, deren benötigte Werte bereits vor Eintritt in eine analysierte Funktion gesetzt wurden. Es wurden keine Aussagen zu ABI, Struktur/Feldbedeutung oder Laufzeitsemantik abgeleitet.

**Befundstatus:** **OFFEN** global; **VERIFIZIERT** sind Eingabeidentität, vollständige gebundene A32-Byteabdeckung, die Site-Inventare und die oben adressierten lokalen Ausschlüsse. **Self-review** durch diesen Worker; kein unabhängiger Review und kein Hardware-/Runtime-Lauf.

## Validator

`validate.py` reproduziert Eingabehash/-größe, ELF-VA-/Offsetabbildung, Toolversion, exakte vollständige Fallbackdekodierung, Site-Zahlen, Value-Flow-Lauf, Kandidateninventar sowie die oben exakt definierten Symbol-/Dispatchzahlen und deren vollständige adressgebundene Liste; es prüft zusätzlich Berichtspflichtstellen sowie das self-reference-freie Manifest. Erwarteter Validatorstatus: `PASS` für diese Reproduzierbarkeits- und Artefaktprüfungen. Das ersetzt nicht die oben genannte **OFFEN**-Restunsicherheit der Sprungtabellenpfade.
