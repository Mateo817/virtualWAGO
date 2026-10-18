> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-034 — begrenzte C166-Struktur E02192..E0219D

## Ergebnis

**VERIFIZIERT (statische, begrenzte Dekodierung):** Unter der in REA/Rizin gesetzten C166-Konfiguration dekodieren die 12 Bytes an Composite-Datei-Offsets `0x2192..0x219D` lückenlos als vier Instruktionen in einem linearen Block. Die letzte Instruktion ist `rets` bei `0x219C` und endet genau bei `0x219E`. Im begrenzten Slice gibt es davor keinen dekodierten Sprung oder Call. Der einzelne Caller bei Datei-Offset `0x3752` wird als `calls 0xe02192` dekodiert und zielt damit numerisch auf Offset `0x2192`.

Die Adressnotation `E02192`/`E03752` bildet die Rohdateioffsets syntaktisch auf die vorgegebene Basis `E00000` ab. Sie belegt keine reale Ladeadresse oder Laufzeitbelegung.

## Methode und Identität

- Eingabe: `XE164-composite-e00000.bin`, 17 110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` (**PASS**).
- REA `open_binary` wurde zuerst aufgerufen und lehnte das headerlose Composite mit `target_unavailable`, `unsupported binary format` / `file_format_rejected` ab. Das ist die dokumentierte REA-C166-Lücke; derselbe Versuch wurde nicht wiederholt.
- Danach wurde der dokumentierte REA `execute_rizin_command` C166-Fallback verwendet. Jede Dekodierabfrage setzte `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false` und `io.va=false`; REA führte Rizin mit `-N -q` aus. Die Datei wurde bei allen vier Evidence-Aufrufen nachher mit demselben Hash gemeldet und als unverändert markiert.
- REA-Provider: Rizin, `provider.version: null`. Separater lokaler Versionsaufruf `rizin -v` meldete Rizin `0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. Diese Versionszeile ist kein REA-Evidence-Record.
- Kanonisches REA-Bundle: [evidence/rea-evidence-bundle.json](evidence/rea-evidence-bundle.json), REA-exportiert, 4 Records, 0 Unknowns. Alle enthaltenen Records tragen entweder die vier Instruktionsbefunde, den begrenzten Rohbyte-Slice oder den isolierten Caller.

## Instruktionen und Kontrollfluss

`instructions.tsv` enthält die exakten Bytes, Offset-/Adressbindung, Längen und Rizin-Mnemonics. Die Größen summieren sich auf 12 Bytes ohne Lücke oder Überlappung. `cfg.tsv` hält den bounded Kontrollfluss fest: ein linearer Block, terminal bei `rets`, ohne internen Call oder Sprung.

| Offset | Adresse | Bytes | Rizin-Ausgabe | Kontrollfluss |
|---|---|---|---|---|
| `0x2192` | `E02192` | `f2 f4 42 ec` | `mov r4, 0xfe06:0x2c42` | Folgeinstruktion |
| `0x2196` | `E02196` | `22 f4 fe 67` | `sub r4, 0xfe02:0x27fe` | Folgeinstruktion |
| `0x219A` | `E0219A` | `7c 14` | `shr r4, #0x01` | Folgeinstruktion |
| `0x219C` | `E0219C` | `db 00` | `rets` | Rückkehr; Blockende `0x219E` exklusiv |

## Caller und Evidence

Die bei Datei-Offset `0x3752` isoliert dekodierte Instruktion ist `dae09221`, Rizin-Ausgabe `calls 0xe02192`, Größe 4, Typ `call`. `calls.tsv` bindet sie an den Callee-Offset `0x2192`. Es wurden keine weiteren Caller-Instruktionen oder Caller-Pfade verfolgt.

- `ev_01f406f17996d4c767a84f15693c727f20826e6ff0bfa30aba1a6030db654f42` — Rohbytes des exakt 12 Byte langen Slices, erste Instruktion und isolierter Caller.
- `ev_3745b3b02f1bd68118e2697e6f9b962ad4c10815ce347f87d44d711c1cf37c3e` — Instruktion bei `0x2196`.
- `ev_0bf2e72a510095867b8cad6fdabf4488d476e22d8b6cc9dcc13ebcbabe83cc42` — Instruktion bei `0x219A`.
- `ev_b54d6b9b9995b784e1290495deb980be3574b3cc36b3ffccc91786fe040e49fb` — `rets` bei `0x219C`.

## Grenzen, Alternative und Unsicherheit

**OFFEN:** Ob diese Bytes in einer konkreten Ausführung tatsächlich als C166-Code verwendet werden, ob die angegebene Basis der realen Abbildung entspricht und welche Semantik die numerischen Operanden im Gerät haben. Die Rizin-Textausgabe begründet keine Register-, SFR-, API-, ABI- oder Calling-Convention-Deutung. Eine abweichende Instruktions-/Dateninterpretation oder andere Adressabbildung verändert die Einordnung; es gab keine Runtime-, Hardware-, VM- oder Gerätebeobachtung.

Die CFG ist ausschließlich der angefragte Slice `0x2192..0x219D`; der nächste Offset `0x219E`, Code vor `0x2192`, andere Caller und alle nichtlinearen Ziele außerhalb des Slice sind nicht untersucht. Die Dekodierung belegt keinen Quellcode-Funktionsanfang und keine vollständige Funktion über die Slice-Grenze hinaus. Der Caller-Befund ist auf genau eine Instruktion begrenzt.

## Prüfstatus

- Eingabegröße und SHA-256: **PASS**.
- Rohbytes, Instruktionsgrößen und lückenlose Abdeckung `[0x2192, 0x219E)`: **PASS**.
- C166-Bindung, Callerziel `0x2192`, CFG-Grenze und Tabellen-/Evidence-Abgleich: siehe `validate.py`.
- SHA-256-Manifest: siehe `SHA256SUMS`.
- Self-review: durchgeführt. Kein unabhängiges Review oder nicht beobachteter Workerlauf wird beansprucht.

Statusvokabular: `VERIFIZIERT | HYPOTHESE | OFFEN | BLOCKED`; Testvokabular: `PASS | FAIL | NOT_RUN | BLOCKED`.
