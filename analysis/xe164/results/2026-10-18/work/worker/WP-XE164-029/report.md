> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-029 — begrenzter Kontrollfluss ab E00556

## Ergebnis

**VERIFIZIERT (statische Dekodierung unter Rizin-C166):** Im ausschließlich untersuchten Bereich Datei-Offsets `0x0556..0x0561` besteht der Callee aus fünf aufeinanderfolgenden Instruktionen in einem Basic Block: vier `mov`-Instruktionen, danach `ret`. Es gibt in diesem Bereich keinen bedingten oder unbedingten Sprung und keinen weiteren Call. Der isoliert untersuchte Caller bei Offset `0x0654` dekodiert als `calla+ cc_UC, 0x0556`; Rizin annotiert das direkte Ziel `0x556`. Damit ist die begrenzte CFG ein einzelner linearer Block, der mit Rückkehr endet.

Das beschreibt nur die statisch dekodierte Struktur. `E00000 + Datei-Offset` ist hier ausschließlich die vorgegebene syntaktische Adressbindung; dies belegt keine geladene Speicherabbildung. Aus den Operanden werden keine ABI-, DPP-, SFR- oder Gerätebedeutungen abgeleitet.

## Eingabe und Methode

- Eingabe: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`
- Größe: 17,110 Bytes; SHA-256: `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- **PASS:** Größe und SHA-256 wurden lokal gegen die Zuweisung geprüft.
- REA `open_binary` lehnte das rohe Abbild mit `unsupported_target` / `file_format_rejected` ab. Daher wurde der in der Zuweisung zugelassene direkte Rizin-C166-Fallback verwendet.
- Rizin wurde über REA `execute_rizin_command` auf genau dieser Datei gestartet. Erfolgreicher Callee-Befehl: `e asm.arch=c166; e asm.bits=16; p8 12 @ 0x556; e asm.arch=c166; e asm.bits=16; pD 12 @ 0x556; pd 1 @ 0x654`.
- Caller-Bytes und -Dekodierung wurden anschließend separat mit `e asm.arch=c166; e asm.bits=16; p8 4 @ 0x654; pd 1 @ 0x654` gelesen.
- Der Rizin-Anbieter meldete `provider.version: null`; die genaue Toolversion ist **OFFEN**. Ein Versions-/Konfigurationsprobeversuch scheiterte am Rizin-Befehlsparser und wurde nicht wiederholt.
- Kanonischer REA-Evidence-Export: `rea-evidence.json`, drei Rizin-Befehlsbeobachtungen. Der erste erfolgreiche Befehl enthält den Callee-Dump und Caller-Ziel; der letzte liefert Caller-Bytes. Die dazwischenliegende fehlgeschlagene Probe ist ebenfalls erhalten.

## Instruktionstabelle

Offsets sind Datei-/Analyseoffsets. `E00000 + Offset` erscheint nur zur syntaktischen Bindung.

| Offset | Syntaktische Adresse | Bytes | Rizin-C166-Dekodierung | Kontrollfluss |
|---:|---:|---|---|---|
| `0x0556` | `E00556` | `e0 0c` | `mov r12, #0x00` | Fallthrough `0x0558` |
| `0x0558` | `E00558` | `e6 fd 00 02` | `mov r13, #0x0200` | Fallthrough `0x055c` |
| `0x055c` | `E0055C` | `f0 cd` | `mov r12, r13` | Fallthrough `0x055e` |
| `0x055e` | `E0055E` | `f0 4c` | `mov r4, r12` | Fallthrough `0x0560` |
| `0x0560` | `E00560` | `cb 00` | `ret` | Rückkehr; Ziel nicht statisch bestimmt |

**VERIFIZIERT:** Rizin lieferte für den exakt begrenzten 12-Byte-Dump `e00ce6fd0002f0cdf04ccb00`; die fünf Instruktionslängen summieren sich auf 12 Bytes. Die Textdekodierungen sind die im REA-Evidence erhaltenen Rizin-Ausgaben, ohne semantische Umdeutung.

## CFG-Tabelle

| Block | Bereich | Instruktionen | Nachfolger | Endbedingung |
|---|---|---|---|---|
| `B0` | `0x0556..0x0561` | `mov; mov; mov; mov; ret` | keiner im Callee-Bereich | `ret` an `0x0560` |

`B0` besitzt innerhalb des betrachteten Ausschnitts genau einen linearen Eintritt bei `0x0556`. Der Block erreicht die Rückkehr ohne sichtbare Verzweigung. Es werden keine Bytes ab `0x0562` dekodiert oder zur Aussage herangezogen.

## Call- und Referenztabellen

| Caller-Offset | Bytes | Dekodierung | Direktes Ziel | Status |
|---:|---|---|---:|---|
| `0x0654` | `ca 00 56 05` | `calla+ cc_UC, 0x0556` | `0x0556` (`E00556` syntaktisch) | **VERIFIZIERT:** Rizin-Ausgabe annotiert `; 0x556` |

| Quelle im Callee | Referenzklasse | Ziel | Befund |
|---|---|---|---|
| `0x0556` | Kontrollfluss-Eintritt aus isoliertem Caller | `0x0556` | Caller-Operand ist direkt dekodiert |
| `0x0556..0x0561` | interne Sprung-/Call-Referenzen | — | keine in den fünf dekodierten Instruktionen |
| `0x0560` | Return | dynamisch / nicht bestimmt | `ret`; Ziel nicht aus diesem Byteausschnitt ableitbar |

## Abgrenzung, Alternativerklärung und Restunsicherheit

- **VERIFIZIERT:** Der erfolgreiche Callee-Disassembly-Befehl bat Rizin um exakt 12 Bytes ab `0x0556`; der Caller-Lesezugriff war auf Offset `0x0654` begrenzt. Die Bytes nach `0x0561` wurden nicht analysiert.
- **VERIFIZIERT:** Der gemessene Eingabehash nach Rizin stimmt mit dem vorgegebenen Hash überein; Rizin meldete `artifact_changed: false`.
- **OFFEN:** REA/Rizin identifiziert in diesem Evidence-Datensatz die genaue ausführbare Rizin-Version nicht (`version: null`).
- **HYPOTHESE:** Die sichtbaren C166-spezifischen Mnemonics und Registerbezeichnungen zeigen, dass die gesetzte C166-Dekodierung für diesen Ausschnitt wirksam war. Der erfolgreiche REA-Datensatz enthält keine separate Konfigurations-Rücklesung; die Parser-Probe für eine solche Rücklesung scheiterte.
- **OFFEN:** Statische Instruktionsdekodierung belegt weder tatsächliche Ausführung noch die Laufzeitwirkung von `ret`, Registerzuständen oder Caller-Kondition. Keine ABI-/Hardwareaussage.
- Alternativerklärung: Ohne akzeptierte C166-Dekodierung könnte dieselbe Bytesequenz anders interpretiert werden. Der gezielte Rizin-Aufruf setzte `asm.arch=c166` und erzeugte C166-spezifische Ausgabe; mangels erfolgreicher Rücklesung bleibt die Konfigurationsbestätigung schwächer als ein unabhängiger Decodervergleich.

## Evidence und Abnahme

- REA-Evidence-ID Callee + Caller-Ziel: `ev_59b3ea0387ee95d4a6ea25a8b062dd9a6cf77be1df92156de530e4e52ab31845`.
- REA-Evidence-ID fehlgeschlagene Versions-/Konfigurationsprobe: `ev_cb070d3d9c7b26638f881c359c8fb83e99ae60457cb80c9ef098befe498bac3f`.
- REA-Evidence-ID Caller-Bytes: `ev_56c129b0577e11579cbaaa9630a089d563050a722bda1fac81bb760295cb8810`.
- **PASS:** Der reproduzierbare Validator `validate.py` prüft Eingabegröße/-hash, Evidence-IDs und Exportinhalt, Rizin-Ergebnis, Offset-/Byte-/Dekodierungs- und Caller-Zielbindung sowie die Dateihashes in `SHA256SUMS`.
- Repository-/Geräte-/Netz-/VM-Zugriffe: **NOT_RUN**.
