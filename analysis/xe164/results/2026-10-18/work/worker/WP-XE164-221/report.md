> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-221 — Wertquellen und lokale Store-Bedingungen

## Befund

**VERIFIZIERT — Site ELF `0x1c9c` / Ghidra `0x11c9c`.** Die WRITE-Instruktion ist `str r0,[r4,#0x0]` (`str r0,[r4]`), Rohwort `0xe5840000`, gespeicherte Bytes `00 00 84 e5`. Der Store speichert den unmittelbar nach `bl 0x114e0` sichtbaren `r0`-Wert: auf den Call bei `0x11c90` folgen im erlaubten Bereich nur `ldr r2,[0x11d9c]` und `ldr r3,[0x11da0]`, die `r0` nicht überschreiben, dann der Store. Somit ist die lokal beobachtete Wertquelle der unverändert weitergereichte post-call-`r0`-Wert; es ist keine Konstante. Im sichtbaren Fenster gibt es zwischen Call und Store keine Bedingungsinstruktion oder bedingte Kante; Store-Site `0x11c9c` liegt auf dem linearen Fallthrough-Pfad. Die WRITE-Zielbindung an Ghidra `0x241e0` wird ausschließlich methodengebunden aus WP-XE164-218 übernommen (dort materialisierte exakte Ghidra-WRITE-Xref); die lokale `r4`-Effektivadresse bleibt **OFFEN**. Bedeutung des post-call-Werts und sein Callee-/Calling-Convention-Vertrag bleiben **OFFEN**.

**VERIFIZIERT — Site ELF `0x1df0` / Ghidra `0x11df0`.** Die WRITE-Instruktion ist `str r2,[r3,#0x0]` (`str r2,[r3]`), Rohwort `0xe5832000`, gespeicherte Bytes `00 20 83 e5`. `r2` ist unmittelbar davor definiert durch `mov r2,#0x0` bei `0x11dec` (Rohwort `0xe3a02000`, Bytes `00 20 a0 e3`), daher storet die Site die Konstante zero. Lokaler Wert- und Zielpfad: `ldr r3,[0x11ea4]` (`0xe59f30dc`) → Literal bei `0x11ea4` = Bytes `14 24 01 00` = Wort `0x00012414` → `add r3,pc,r3` (`0xe08f3003`), wobei A32-PC am ADD `0x11dcc` ist → `r3=0x11dcc+0x12414=0x241e0` Ghidra-Adressraum (ELF-VA `0x141e0`) → `ldr r0,[r3,#0]` (`0xe5930000`) → `cmp r0,#0` (`0xe3500000`) → `beq 0x11df8` (`0x0a000002`) → Fallthrough `mov r2,#0` → `str r2,[r3]`. Der Store wird erreicht, wenn der Vergleich nicht gleich ist (`r0 != 0`): `beq` nimmt bei Gleichheit die Kante zu `0x11df8`, außerhalb des erlaubten Fensters, und überspringt den Store. Ziel `0x241e0` ist hier lokal durch die Literalrechnung belegt.

Der Store-2-Block selbst wird nur erreicht, wenn auch die frühere sichtbare Bedingung erfüllt ist: `ldrb r2,[r3,#0x28]` bei `0x11dc8`, `cmp r2,#0` bei `0x11dcc`, `bne 0x11ddc` bei `0x11dd0`. Bei Bytewert `0` führt der Fallthrough über `mov r0,#0` und `bx lr` (0x11dd4–0x11dd8) aus dem Block heraus. Somit ist die vollständig sichtbare lokale Store-Bedingung: geladenes Byte bei `[r3+0x28] != 0` und anschließend geladenes Wort bei `[r3] != 0`. Diese Feststellung klassifiziert nur Kanten und Flag-Vergleiche, nicht die Semantik der Daten.

## Instruktionen und Rohwörter

REA/Ghidra meldete Architektur `ARM:LE:32:v8`, Modus `v8`, Instruktionslänge 4 Byte. Die gespeicherten Bytes stehen in Speicherreihenfolge; Rohwörter sind daraus als 32-bit little-endian notiert.

| Ghidra-Adresse | ELF-VA | Bytes | Rohwort | Instruktion | Lokaler Def-Use / Kante |
|---:|---:|---|---|---|---|
| `0x11c90` | `0x1c90` | `12 fe ff eb` | `0xebfffe12` | `bl 0x114e0` | Unmittelbare Call-Stelle vor Store 1; danach kein lokaler `r0`-Schreiber vor dem Store. |
| `0x11c94` | `0x1c94` | `00 21 9f e5` | `0xe59f2100` | `ldr r2,[0x11d9c]` | Definiert `r2`; verändert `r0` nicht. |
| `0x11c98` | `0x1c98` | `00 31 9f e5` | `0xe59f3100` | `ldr r3,[0x11da0]` | Definiert `r3`; verändert `r0` nicht. |
| `0x11c9c` | `0x1c9c` | `00 00 84 e5` | `0xe5840000` | `str r0,[r4,#0]` | Store 1; linearer Fallthrough ab Call. |
| `0x11dc0` | `0x1dc0` | `dc 30 9f e5` | `0xe59f30dc` | `ldr r3,[0x11ea4]` | Lädt Literalwort aus zugelassenem `0x1ea4`-Literalort. |
| `0x11dc4` | `0x1dc4` | `03 30 8f e0` | `0xe08f3003` | `add r3,pc,r3` | `r3 := 0x11dcc + 0x12414 = 0x241e0`. |
| `0x11dc8` | `0x1dc8` | `28 20 d3 e5` | `0xe5d32028` | `ldrb r2,[r3,#0x28]` | Definiert `r2`, im weiteren Pfad vor Store 2 erneut überschrieben. |
| `0x11dcc` | `0x1dcc` | `00 00 52 e3` | `0xe3520000` | `cmp r2,#0` | Setzt Flags für folgenden `bne`. |
| `0x11dd0` | `0x1dd0` | `01 00 00 1a` | `0x1a000001` | `bne 0x11ddc` | Bei `r2 != 0` zum Block `0x11ddc`; bei Gleichheit Fallthrough zu `0x11dd4` und `bx lr` bei `0x11dd8`. Diese vorgelagerte Kante entscheidet nur, ob der zweite lokale Block betreten wird. |
| `0x11dd4` | `0x1dd4` | `00 00 a0 e3` | `0xe3a00000` | `mov r0,#0` | Alternative des vorangehenden Checks; nicht auf dem Pfad zum Store 2. |
| `0x11dd8` | `0x1dd8` | `1e ff 2f e1` | `0xe12fff1e` | `bx lr` | Rückkehr auf der vorangehenden Gleichheitskante. |
| `0x11ddc` | `0x1ddc` | `70 40 2d e9` | `0xe92d4070` | `stmdb sp!,{r4,r5,r6,lr}` | Eintritt in den Store-2-Block über `bne`. |
| `0x11de0` | `0x1de0` | `00 00 93 e5` | `0xe5930000` | `ldr r0,[r3,#0]` | Liest ein Wort über lokal berechnetes `r3`. |
| `0x11de4` | `0x1de4` | `00 00 50 e3` | `0xe3500000` | `cmp r0,#0` | Flags entscheiden unmittelbare Store-Erreichbarkeit. |
| `0x11de8` | `0x1de8` | `02 00 00 0a` | `0x0a000002` | `beq 0x11df8` | Wenn `r0 == 0`, Sprung zum Ziel außerhalb des Fensters; Store bei `0x11df0` wird ausgelassen. |
| `0x11dec` | `0x1dec` | `00 20 a0 e3` | `0xe3a02000` | `mov r2,#0` | Store-Wertquelle, Konstante zero. |
| `0x11df0` | `0x1df0` | `00 20 83 e5` | `0xe5832000` | `str r2,[r3,#0]` | Store 2, erreicht im Fallthrough von `beq`, also wenn `r0 != 0`. |

## Beobachtung, Alternativerklärung, Restunsicherheit

**VERIFIZIERT — Beobachtung.** REA `open_binary` band die Eingabedatei mit SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` an Ghidra 12.1.4 (`ARM:LE:32:v8`; Image Base `0x10000`). `inspect_native_instruction` Evidence für die Site-/Def-/Kanteninstruktionen umfasst `ev_8b49f8964d43223f1f1ad41f6d1fce7621b7a61aabe95bf19687cffd6cf18f1c` (`0x11c90`), `ev_339f94f6ad079107bae4244015fe2a54df2cf98893101a6533d78056de860432` (`0x11c94`), `ev_9b8648c888163eabab7c50c6e02be5cce9b5614727e5c7cec5078d910abf801b` (`0x11c98`), `ev_6fe7bb26f48e4c5bde0bfc2f0ab67b9552151c365f22a8b9c53922b8eb17b25f` (`0x11c9c`), `ev_eff86526a2415f33bd9f967e3d430de86c1c97d07422c5faef3bd2a6163264b7` (`0x11dc0`), `ev_d9fb240d7bc42313225364db91a76c62dbff69fac072d30f976dff3572de8bf7` (`0x11dc4`), `ev_198e48b294a11e8fdd44cd222e4932990d4238ee36a575b40b9ee9165821d27d` (`0x11dc8`), `ev_8f5242b9829c70baa0fb9e381179b0e7d3f162185e7a108739e5d13c8aa971f2` (`0x11dcc`), `ev_8f32240f6cdbf984dc506307c9417e4fbc458af91f813ed926cb327551e6d1bd` (`0x11dd0`), `ev_cfc0fe9043cfab323ef68496b3d5085f5792079178ab3c1f684da85df4886027` (`0x11dd4`), `ev_c0717410909f47a60595a5359b091064b38f87a55a90312207569990bbfc2acb` (`0x11dd8`), `ev_7d8cf7194fe72de66935f369b11420a887f3fa3d962b0c10d384683c39f842a0` (`0x11ddc`), `ev_778965212e7ccb1aa09081f580e077a3153dcdb9d397dbaf87bfe6673714efe2` (`0x11de0`), `ev_6a8466423b2b94f4cfb09d9e64af4d6df2d26c0ca1c504b5dae897d0e030c438` (`0x11de4`), `ev_5e956397bb5a3fecff35dbc9df5e5a4fe75d0d0ba529c3aa217cecdf56e6937b` (`0x11de8`), `ev_9613da6408a34996be4aae02cbe478665712ccb74c0841682e4551e545bb0cbc` (`0x11dec`) und `ev_b699aaac80df22a49f0fa2e0b5a79a1045e23546f3e2d28af9f49a99c55f475a` (`0x11df0`). Direkt benötigtes Literal: `read_bytes(0x11ea4,4)` Evidence `ev_393e5117a45394333f05bc2d872ae03787b3066e770d6df84e1727acc95d1d55`, Bytes `14240100`. Ghidra liefert zu den Speicheroperanden keine Effektivadresszerlegung; beim ersten Store wird deshalb die Zielbindung ausdrücklich aus WP-XE164-218 übernommen. Es wurde kein lokaler Disassembler-/Rohbyte-Fallback verwendet, da REA die relevanten Instruktionen und Literalbytes vollständig lieferte.

**HYPOTHESE — Alternativerklärung.** Der unmittelbar nach dem Call sichtbare `r0`-Wert kann abhängig vom nicht untersuchten Vertrag einen callee-seitig erzeugten Wert darstellen; ebenso bleibt möglich, dass er einen vorher gesetzten oder anderweitig übergebenen Wert fortführt. Callee-Wirkung und Calling-Convention-Vertrag sind außerhalb des Auftragsbereichs und bleiben **OFFEN**. Die lokale Beobachtung bleibt: im Fenster wird der nach dem Call sichtbare `r0`-Wert bis zum Store nicht überschrieben. Der Store selbst ist statisch im sichtbaren Fenster unbedingt auf dem Fallthrough-Pfad; Laufzeit-Ausführung ist dadurch nicht belegt.

**OFFEN — Restunsicherheit.** Die Bedeutung des Aufrufs bei `0x114e0`, Semantik und Typ des geschriebenen Wortes, frühere Zustände der Argumentregister, Herkünfte vor Fensteranfängen, Wirkung des Sprungziels `0x11df8`, Runtime-Erreichbarkeit und computed/indirekte Aliase sind ausgeschlossen. Bei Store 1 bleibt seine unabhängige lokale Effektivadresse `r4` offen; nur die ausdrücklich methodengebundene WP218-Ghidra-Xref bindet das Ziel `0x241e0`. Der genaue A32 Call-Return-Registervertrag wird nicht separat geprüft oder als weitergehende ABI-Aussage verwendet.

## Methode und Validator

**VERIFIZIERT.** Methode: REA zuerst (`open_binary`, `binary_overview`, `inspect_native_instruction`, `read_bytes`), Provider Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`, REA Workflow Revision 3. REA deckt Dekodierung, Instruktionsbytes, flow-type und direkte Kanten für die genannten Adressen ab. Kein Fallback erforderlich.

**PASS.** `python3 validate.py` prüft Eingabe-SHA, die im Befund angeführten exakten Instructions-/Rohwort-Zeilen, die Literalrechnung, die beiden Wertquellen und sichtbaren Zweigbedingungen anhand des Berichts. Es dekodiert das Artefakt nicht erneut und benutzt keine Netzwerk-/Geräte-/VM-Zugriffe.

## Self-reference-freies SHA-Manifest

`SHA256SUMS` umfasst die Eingabedatei, `report.md` und `validate.py`; das Manifest selbst wird nicht gehasht.
