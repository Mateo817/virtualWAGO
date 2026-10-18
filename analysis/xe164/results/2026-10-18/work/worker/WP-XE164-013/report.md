> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-013 — statischer Kontrollfluss ab E0369C

## Ergebnis

**VERIFIZIERT:** Die gezielte Callsite liegt bei Analyseadresse `E00F32`, Fileoffset `0x0F32`, Bytes `DA E0 9C 36`. Rizin decodiert dort `CALLS E0369C`; der Folgebefehl liegt bei `E00F36`. Es wurden keine umgebenden Caller-Instruktionen in die Befundtabellen aufgenommen.

**VERIFIZIERT:** Mit Rizin/C166 bildet `E0369C` einen lokal erkannten Bereich von 318 Bytes mit 33 Basicblocks bis einschließlich des Instruktionsendes bei `E037DA`. Der Seed enthält einen indirekten Sprung bei `E036C0`. Ein Zweig bei `E036B2` führt direkt zu `E03804`. Der indirekte Dispatch lädt einen 16-Bit-Wert aus einer indizierten Tabelle an Fileoffset `0x3B62 + 2*(r9-1)`.

**VERIFIZIERT (Rohdaten):** Die sechs Wörter bei Fileoffsets `0x3B62..0x3B6D` sind little-endian `36C2, 36DE, 3748, 3778, 37DA, 37FA`. **HYPOTHESE (Edge-Deutung):** Unter dem Composite-Image-Basiswert `E00000` sind dies sechs mögliche Dispatch-Ziele `E036C2, E036DE, E03748, E03778, E037DA, E037FA`. Alle sechs Ziele dekodieren im Composite als Instruktionsstarts. Die Indexwahl ist statisch nicht bestimmbar.

Der direkte Zweig nach `E03804` und die sechs aus der Tabelle abgeleiteten Ziele erweitern den untersuchten Kontrollflussbereich bis Fileoffset `0x3877` / Analyseadresse `E03877` (Ende exklusiv `E03878`). Die zusammengeführte, begrenzte Darstellung enthält 49 Basicblockstarts und 168 decodierte Instruktionen. Die Blockliste enthält nur vom Seed aus über direkte Zweige, Fallthroughs oder die sechs begrenzten Tabelleneinträge erreichbare Blöcke. Direkte Calls werden in `calls.tsv` als Adress-Edges festgehalten und nicht rekursiv verfolgt.

Die elf direkten Calls innerhalb des Bereichs stehen einzeln in `calls.tsv`; ihre Ziele sind ausschließlich Adressen. Sieben verschiedene Callee-Adressen kommen vor: `E03634, E0219E, E02344, E01FFC, E02192, E031C4, E03C2A`. Der Eintrag für `E00F32 → E0369C` ist separat als angeforderte Caller-Callsite aufgeführt.

## Fundstellen und Datenreferenzen

- Entry-Prolog und erster Call: Fileoffset `0x369C..0x36AB`, Analyseadresse `E0369C..E036AB`; Call bei `0x36A8 / E036A8`.
- Grenzenprüfung und direkter Zweig: `0x36AC..0x36B5 / E036AC..E036B5); bedingter Zweig bei `0x36B2 / E036B2` nach `E03804`, Fallthrough `E036B6`.
- Tabellenadressbildung: Instruktionen bei `E036AC`, `E036AE`, `E036B6`, `E036B8`, `E036BC`; indirekter Sprung `E036C0`. Das berechnete Wortziel ist `2*(r9-1)+0x3B62); die sechs Rohwörter stehen bei Fileoffset `0x3B62..0x3B6D`.
- Weitere tabellengestützte Ziele: `E036C2`, `E036DE`, `E03748`, `E03778`, `E037DA`, `E037FA`. Direkte Folgeblöcke führen unter anderem nach `E03804); die Instruktions- und Edge-Tabellen enthalten einzelne Fundstellen.
- Direkte Zieloperanden an Instruktionen bleiben in `references.tsv` wörtliche Operanden. Es wird keine SFR-, Interrupt-, K-Bus- oder Registerbedeutung behauptet.

## Verfahren und Evidence

Die Eingabebindung wurde vor der Analyse geprüft:

- Composite: 17 110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Replay-Konfiguration: 2 169 Bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`.

REA zuerst: `execute_rizin_command`, Artefakt lokal, `e asm.arch=c166; e asm.bits=16; e cfg.bigendian=false; e io.va=false`; Seek `0x369C`, danach gezielte JSON-Disassembly-/CFG-Abfragen an den Seed, den direkt erreichbaren Block `0x3804`, die tabellengestützten Starts und die Tabellenbytes `0x3B62). Kein `open_binary`, kein globales `aaa`. Rizin-Version und Profil-Digest wurden vom REA-Provider nicht ausgegeben; ein Versionsprobe-Kommando war nicht unterstützt. Deshalb wird keine konkrete Rizin-Versionsnummer behauptet.

Die beobachtete CFG-Lücke war, dass Rizin `pdfj` bei `E037D6` einen unbedingten Sprung nach `E036AC` decodiert, während `afbj` für den Endblock `E037D4` keine ausgehende Kante ausgibt. Daher wurde der verlangte direkte Ghidra-C166-Fallback ausgeführt: Ghidra 12.1.4, `C166:LE:16:default`, Compiler-Spec `tasking`, Raw Binary Loader `BinaryLoader`, Basis `0xE00000`, `-noanalysis`, ein Seed `E0369C`, begrenzte Adressmenge `E0369C..E03877`, Netzwerk-Namespace isoliert. Der eigene Probe-Script-Hash ist in der Ausgabeliste festgehalten.

Der Ghidra-Probe dekodierte mit dieser C166-Konfiguration zehn Instruktionen bis `E036B0`, konnte `E036B2` trotz `DisassembleCommand` nicht in eine Instruktion überführen und endete mit `UNDECODED_COUNT=1`. Das ist **BLOCKED** für den unabhängigen Ghidra-CFG-Abgleich; die begrenzte Kontrollflussdarstellung stützt sich daher auf die REA/Rizin-Disassembly, afbj-Befunde und die separat beobachteten Rohwörter. Es wird kein unabhängiger Review beansprucht.

## Status und Restunsicherheit

- **VERIFIZIERT:** Eingabegrößen und Hashes; CALLS-Callsite `E00F32 → E0369C`; Rizin-C166-Instruktionen, direkte Sprungadressen und Rohbytes der sechs Wörter.
- **HYPOTHESE:** Die sechs Tabellenwörter sind mögliche indirekte Codeziele unter Basis `E00000`; die Bytes liegen vor, aber der Laufzeitwert in `r9` wurde nicht beobachtet.
- **OFFEN:** Welcher Tabellenindex tatsächlich gewählt wird und ob alle statisch möglichen Ziele im Laufzeitpfad auftreten.
- **BLOCKED:** Ghidra-Fallback-Decode ab `E036B2`; die Fehlstelle ist in `logs/ghidra-script-final.log` sichtbar.
- **PASS:** Eingabehash-Prüfung, Ausgabe-Validator und `sha256sum -c SHA256SUMS` (nach Erstellung des Manifests).
- **NOT_RUN:** Laufzeittests; sie liegen außerhalb dieses statischen Pakets.

Alternative Erklärung: Die auf `E037DA` und `E037FA` zeigenden Wörter könnten ohne Runtime-Kontext als 16-Bit-Werte statt als auf `E00000` bezogene Codeziele gemeint sein. Dass sie im Composite genau auf decodierbare Instruktionsstarts zeigen, stützt die Zieldeutung, beweist aber nicht die Laufzeitverwendung. Auch die von Rizin getrennten Funktionsgrenzen bei `E037DA` und `E03804` können Analysegrenzen sein; die direkte Sprungkante und Tabellenwerte bleiben die konkrete statische Verbindung.

## Tests

| Prüfung | Status | Beobachtung |
|---|---|---|
| Gebundene Eingabegrößen und SHA-256 | PASS | Beide Werte stimmen exakt mit den Aufgabenbindungen überein. |
| Rizin-C166-lokale Decode-Abfragen | PASS | Befehle abgeschlossen; Composite-Hash nach Rizin unverändert. Rizin-Version nicht berichtet. |
| Begrenzter Ghidra-C166-Fallback | BLOCKED | Konfiguration/Import bestätigt; Decoder liefert `UNDECODED` für `E036B2`. |
| `validate.py` | PASS | TSV-Spalten, Tabs/Zeilen, Bundle und zentrale Adressmarker geprüft. |
| `sha256sum -c SHA256SUMS` | PASS | Manifestprüfung nach finaler Hashaufnahme. |

## Ausgabedateien und SHA-256

Alle Pfade sind relativ zu diesem Paketverzeichnis. `report.md` und `SHA256SUMS` sind gegenseitig nicht selbstreferenziell gelistet; ihr endgültiger SHA-256 steht jeweils in `SHA256SUMS`.

| Datei | Größe | SHA-256 |
|---|---:|---|
| `instructions.tsv` | 15 479 B | `cf268a98b7c472f011aeabada0ceaf9042b3de8196ed3c35bf1949550046bb1f` |
| `edges.tsv` | 9 649 B | `ceec96cee6671bbb6108913760fc377f36f1bee17350b336b42d3bd8d3e38553` |
| `calls.tsv` | 1 548 B | `e3b1f4647e09fe735fbc24bc4d26ac02db8716503fa8e47b08ae8fb61c77ff17` |
| `references.tsv` | 7 994 B | `689b4a44664deec6c09397492d55060d0fbbee5a9ed8b3e491d0ee05aff0b05a` |
| `REA-Evidence-Bundle.json` | 332 955 B | `424421dcfbe75701ffe6f7b09a02a7013e83fc1a77798118bff3622ea1c3120d` |
| `validate.py` | 1 999 B | `da1797ed3b73b4864349e9e90689691fad38016912693c065e92a1fe5699086f` |
| `ghidra/WP_XE164_013_Probe.java` | 3 710 B | `dfa8ebcebf923f87d9901def59344879f7c9c2b5f4297a53d01850b3afa2ef93` |
| `logs/ghidra-final.log` | 8 216 B | `835dab8325c76d0ec1e95562272ab4f87ec0e2ef23fb006fa71dc488e857df50` |
| `logs/ghidra-script-final.log` | 1 996 B | `d3a8531a7a18aa43e1629aa009872774b7e0a89f8ca8469344ea3c02fd9bd2e5` |
| `logs/ghidra-rerun.log` | 8 027 B | `cf9161d2eca02a98361272e68474ed4e70a0406858ec3c77d0dc091c2054e216` |
| `logs/ghidra-script-rerun.log` | 1 836 B | `1697b6c4e76e08d5b1c85dc8ad6562942bede537bf180f8702695894769ce84a` |
| `logs/ghidra.log` | 7 938 B | `c57ae6c75320d9cddac840db4ffb6a23288d9097286458ab276d9f75a172ea90` |
| `logs/ghidra-script.log` | 1 768 B | `f042af26ab91edd4855646c3f97a856c7be0e4cc75b2a0cab24639312da091a1` |

REA-Evidence-IDs im Bundle (11 Records):

`ev_053e59ba82e44772625f73e8dc7b22eb256761159306c498a3d99d7b687e9238`,
`ev_134d99d295c0d66254a9c6bff87fb86291e95c88c541af4a6603571cf402f317`,
`ev_1852e09f8c79fd11a67e38831980c982484949fa2681fd402659abc45fb7c7e5`,
`ev_353a3d1f63175435fb54ee94df5096eac8546e315a6ed07f16761528f5313874`,
`ev_3a7b40f91dfb4e58611966b63eb97101566ca2c6fa4830307579c3ac878fb117`,
`ev_40bf751d61c8da3fc102a2bf1558239459bbddc8d883e6f8edd74165674aed70`,
`ev_545689938e7840ead97b59a811f4323fa5123c2255b0425fd263cf9b56631031`,
`ev_58b0d846f3e861941b1abf13feb7488b8ab84d1fe89504754b732c473a824dee`,
`ev_7ccc89bddc2f09830ac1e259bc53d09ebee0793bddf80016bccd492b481b95ab`,
`ev_941687852a1cf601b717e6c4b6e51e70a271614770fcaa10d5bc4427b2cf73f5`,
`ev_f6cc0ebc125d47dee17dfc255281b063b7113ccd0425c3f856d9f72e80693be6`.
