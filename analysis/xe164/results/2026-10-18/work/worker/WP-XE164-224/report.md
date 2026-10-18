> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-224 — body [0x1dc0,0x1ea4)

## Ergebnis und Status

**VERIFIZIERT**: Der im Assignment angegebene lokale Binärinhalt `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-202/input/libdal.so.1.0.1` ist 18.076 Bytes groß und hat SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. REA wurde mit genau diesem Artefakt geöffnet. Kein Artefakt außerhalb dieses Pakets wurde geändert.

**VERIFIZIERT**: REA 6.5.0 / Ghidra 12.1.4 las die 0xf8 Bytes ab Ghidra-Adresse `0x11dc0` vollständig (Evidence `ev_56329af8c9efd9677c3848ecaa8075cc1ebcab28b35b1ac560fe3e7423268802`). Ghidra meldete für `0x11dc0` **keine** Procedure und `resolve_containing_procedure` meldete `not_in_procedure` (Evidence `ev_bdfbec00b3f2e7e830043e9b996eee0a1e71c9fb8a97c4a6f7342a0e80dc9b3f`). Daher wurde nach dieser beobachteten REA-Lücke als benannter lokaler Fallback GNU `arm-linux-gnueabihf-objdump` 2.44 verwendet. Seine Instruktionsgrenzen decken `[0x1dc0,0x1ea4)` ohne Lücke ab; der vollständige Listing steht unten. Die Assignment-Zuordnung ELF-Offset + `0x10000` zu Ghidra-Adresse ist durch den Bytevergleich über alle 0xf8 Bytes bestätigt.

**VERIFIZIERT**: `[0x1dc0,0x1ea4)` enthält 57 ARM-32-Bit-Instruktionen (228 Bytes), 13 lokale Basic Blocks und 17 lokale Kontrollflusskanten. Davon sind acht direkte `bl`-Instruktionen. `[0x1ea4,0x1eb8)` enthält fünf unmittelbar gebrauchte 32-Bit-Literalwörter. Namen an Symbol-/Call-Zielen werden hier nicht als Funktionsvertrag oder Semantik verwendet.

## Basisadressrechnung

ARM-32-Bit-LDR-literal verwendet hier die Instruktionsadresse + 8 als PC; das folgende `add Rd, pc, Rm` verwendet ebenfalls die Adresse dieser ADD + 8. Die rohen Literalbytes sind little-endian:

| LDR literal bei | Literaldatei-Offset | Wort | folgende ADD | ADD-PC | Rechnung | Ergebnis |
|---|---:|---:|---:|---:|---|---:|
| `0x1dc0` | `0x1ea4` | `0x00012414` | `0x1dc4` | `0x1dcc` | `0x1dcc + 0x12414` | `0x141e0` |
| `0x1df8` | `0x1ea8` | `0x000123dc` | `0x1dfc` | `0x1e04` | `0x1e04 + 0x123dc` | `0x141e0` |
| `0x1e18` | `0x1eac` | `0x000123bc` | `0x1e1c` | `0x1e24` | `0x1e24 + 0x123bc` | `0x141e0` |
| `0x1e38` | `0x1eb0` | `0x0001239c` | `0x1e3c` | `0x1e44` | `0x1e44 + 0x1239c` | `0x141e0` |
| `0x1e58` | `0x1eb4` | `0x00012378` | `0x1e60` | `0x1e68` | `0x1e68 + 0x12378` | `0x141e0` |

All five visible local literal computations therefore produce `0x141e0` before any subsequent direct call. This is only a locally calculated address; it does not assign an object, lifecycle, or hardware meaning to that address.

## Body-owned memory accesses

Widths are bytes. Direction is from the instruction's perspective. For `r3`/`r4`, an access is called base-relative only while the local definition is not separated from it by a call. No calling convention or call-preservation rule is assumed. A call's effects on registers are unknown; uses after it are marked **OFFEN** where needed.

| Instruction | Access expression / address status | Width, direction | Value source / qualification |
|---|---|---|---|
| `0x1dc8 ldrb r2,[r3,#0x28]` | `0x141e0 + 0x28` | 1, read | memory value becomes `r2`; exact local base |
| `0x1de0 ldr r0,[r3]` | `0x141e0 + 0x00` | 4, read | memory value becomes `r0`; exact local base |
| `0x1df0 str r2,[r3]` | `0x141e0 + 0x00` | 4, write | `r2=0` from `0x1dec`; exact local base |
| `0x1e00 ldr r0,[r3,#4]` | `0x141e0 + 0x04` | 4, read | memory value becomes `r0`; base recomputed at `0x1dfc` after preceding call site |
| `0x1e10 str r2,[r3,#4]` | `0x141e0 + 0x04` | 4, write | `r2=0` from `0x1e0c`; exact local base |
| `0x1e20 ldr r0,[r3,#0x1c]` | `0x141e0 + 0x1c` | 4, read | memory value becomes `r0`; base recomputed at `0x1e1c` |
| `0x1e30 str r2,[r3,#0x1c]` | `0x141e0 + 0x1c` | 4, write | `r2=0` from `0x1e2c`; exact local base |
| `0x1e40 ldr r0,[r3,#0x14]` | `0x141e0 + 0x14` | 4, read | memory value becomes `r0`; base recomputed at `0x1e3c` |
| `0x1e50 str r2,[r3,#0x14]` | `0x141e0 + 0x14` | 4, write | `r2=0` from `0x1e4c`; exact local base |
| `0x1e64 ldr r6,[r4,#0x24]` | `0x141e0 + 0x24` | 4, read | memory value becomes `r6`; `r4` defined as base at `0x1e60` |
| `0x1e68 str r5,[r4,#0x18]` | `0x141e0 + 0x18` | 4, write | `r5=0` from `0x1e5c`; exact local base |
| `0x1e70 strb r5,[r4,#0x28]` | `0x141e0 + 0x28` | 1, write | `r5=0` from `0x1e5c`; exact local base |
| `0x1e8c str r5,[r4,#0x24]` | syntactically `[r4+0x24]`; effective base **OFFEN** after calls at `0x1e7c` and `0x1e84` | 4, write | `r5` was set to zero at `0x1e5c`, but its post-call value is **OFFEN**; no preservation claim |
| `0x1e94 ldr r0,[r4,#0x20]` | syntactically `[r4+0x20]`; effective base **OFFEN** after calls at `0x1e7c`, `0x1e84`, and `0x1e90` | 4, read | loaded into `r0`; no call effect or base-preservation claim |

Thus 12 accesses have a body-visible, uninterrupted base derivation to `0x141e0`; two later accesses retain only the encoded `[r4+immediate]` form because direct-call effects on `r4` are unknown. All 14 instructions are body-owned loads/stores. The four literal-pool words are data and are not counted as body accesses.

## Lokaler Kontrollfluss

Blockgrenzen sind inklusive. Branch-Konditionen beschreiben nur die von den unmittelbar vorangehenden `cmp`-Instruktionen gesetzten Flags.

| Block | Bereich | Ende / lokale ausgehende Kante(n) |
|---|---|---|
| B0 | `0x1dc0–0x1dd0` | `bne 0x1ddc`: ungleich → B2; gleich → B1 |
| B1 | `0x1dd4–0x1dd8` | sichtbarer früher Exit über `bx lr` |
| B2 | `0x1ddc–0x1de8` | `beq 0x1df8`: gleich → B4; ungleich → B3 |
| B3 | `0x1dec–0x1df4` | danach B4 (Call-Rückkehrkante unter der lokalen Disassemblierung) |
| B4 | `0x1df8–0x1e08` | `beq 0x1e18`: gleich → B6; ungleich → B5 |
| B5 | `0x1e0c–0x1e14` | danach B6 (Call-Rückkehrkante unter der lokalen Disassemblierung) |
| B6 | `0x1e18–0x1e28` | `beq 0x1e38`: gleich → B8; ungleich → B7 |
| B7 | `0x1e2c–0x1e34` | danach B8 (Call-Rückkehrkante unter der lokalen Disassemblierung) |
| B8 | `0x1e38–0x1e48` | `beq 0x1e58`: gleich → B10; ungleich → B9 |
| B9 | `0x1e4c–0x1e54` | danach B10 (Call-Rückkehrkante unter der lokalen Disassemblierung) |
| B10 | `0x1e58–0x1e74` | `beq 0x1e9c`: gleich → B12; ungleich → B11 |
| B11 | `0x1e78–0x1e98` | danach B12 (Call-Rückkehrkanten unter lokaler Disassemblierung) |
| B12 | `0x1e9c–0x1ea0` | sichtbarer gemeinsamer Exit über `pop {...,pc}` |

Kantenzahl: 2 + (B2: 2, B3: 1, B4: 2, B5: 1, B6: 2, B7: 1, B8: 2, B9: 1, B10: 2, B11: 1) = 17 lokale Kanten. Die Calls erzeugen zusätzlich folgende direkte Zielkanten, nicht in den 17 lokalen CFG-Kanten enthalten: `0x1df4 → 0x13b4`, `0x1e14 → 0x13b4`, `0x1e34 → 0x151c`, `0x1e54 → 0x3c34`, `0x1e7c → 0x1378`, `0x1e84 → 0x163c`, `0x1e90 → 0x1408`, `0x1e98 → 0x148c`. **OFFEN** bleiben alle Effekte und Rückkehr-/Nicht-Rückkehrbedingungen dieser Zieladressen; nur der lokale Listing-Kontrollfluss wird beschrieben.

## Sichtbare Exitregister und Registergrenzen

- Pfad B0→B1: `r0` wird an `0x1dd4` auf `0` gesetzt und `bx lr` verlässt den Body bei `0x1dd8`. Die von der Instruktion gelesene Zielregister-/Rücksprungquelle ist `lr`; keine Aufrufkonvention wird behauptet.
- Aktiver Pfad: `r4`, `r5`, `r6`, `lr` werden bei `0x1ddc` gespeichert. B10→B12 und B11→B12 erreichen `0x1e9c`; dort wird `r0=0` an `0x1e9c` gesetzt und `0x1ea0` lädt `r4`, `r5`, `r6`, `pc` aus dem Stack. Damit ist der sichtbare Exitwert von `r0` für den aktiven Bodypfad `0`.
- **OFFEN**: Die Registerwirkungen aller direkten Calls sind nicht analysiert. Insbesondere werden weder Werte noch effektive Basisadressen nach einem Call aus ABI-/Calling-Convention-Annahmen abgeleitet. Der Wert in `r0` am Call-Rückkehrpunkt ist jeweils **OFFEN**; sichtbare spätere lokale Instruktionen können ihn erneut definieren.

## Vollständiges Listing (57 Instruktionen)

[Code-/Listingblock bleibt im privaten Nachweispaket.]

## Alternativerklärung und Restunsicherheit

**HYPOTHESE**: Die frühere Kante prüft ein einzelnes Byte am errechneten Basisoffset `+0x28` und lässt den Body bei gelöschtem Byte sofort mit `r0=0` enden. Begründung ist nur `ldrb`, `cmp #0`, `bne` und die sichtbaren Instruktionen. Eine semantische Bezeichnung des Bytes ist nicht belegt.

**HYPOTHESE**: Die vier Nulltests steuern jeweils einen bedingten Null-Store und direkten Call; die Abschrift zeigt die Reihenfolge und Instruktionen. Dass die Calls die Zielwerte zerstören, freigeben oder sonst wie behandeln, wird nicht aus Zielnamen abgeleitet und bleibt **OFFEN**.

**OFFEN**: Beim Pfad ab `0x1e78` können die späteren Operanden/Adressen nach direkten Calls durch Call-Effekte beeinflusst sein. Das Listing belegt die Registerverwendungen, aber nicht deren Werte nach Rückkehr. Deshalb sind die beiden späteren Speicherzugriffe nicht als bewiesen basisrelativ ausgewiesen.

## Werkzeuge, Tests und Reproduktion

- REA: Version 6.5.0; ausgewählter Provider Ghidra 12.1.4; Profile digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Lokaler Fallback: GNU `arm-linux-gnueabihf-objdump` / Binutils 2.44. Kommando: `arm-linux-gnueabihf-objdump -D -M reg-names-std --start-address=0x1dc0 --stop-address=0x1eb8 <Artefakt>`.
- **PASS**: `python3 validate.py` prüft Quellgröße, SHA-256, Byteabbildung der fünf Literale, 57 dekodierte Instruktionsadressen in der angegebenen Bodyspanne, acht direkte Calls und genau die 0xf8-Byte-Abdeckung von Body plus Literalbereich.
- **NOT_RUN**: Laufzeit-, Hardware-, Netzwerk- oder VM-Prüfungen; sie liegen außerhalb dieses Pakets und waren nicht nötig.
- Eigene Dokument-/Validatorprüfung: Self-Review, kein unabhängiges Review behauptet.

## SHA-256-Manifest

Das separate `manifest.sha256` führt die Hashes dieses Berichts und `validate.py`; die Manifestdatei selbst ist nicht in sich selbst gehasht.
