> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-220: zwei `strb`-Schreiber

## Ergebnis

VERIFIZIERT: Für den Store bei ELF `0x1d50` ist der gespeicherte Low-Byte-Wert auf dem sichtbaren Store-Pfad `0x01`.

HYPOTHESE: Der Store bei ELF `0x1d50` wird lokal nur erreicht, wenn `r0 != 0` und der in `r5` geladene Wert aus `[r3,#0x14]` ungleich null ist; dies folgt aus der ARM-Flagsemantik der sichtbaren bedingten Instruktionen.

VERIFIZIERT: Für den Store bei ELF `0x1e70` ist der gespeicherte Low-Byte-Wert `0x00`: `r5` wird innerhalb des Fensters auf null gesetzt und bis zum Store nicht neu definiert. Der Store selbst ist auf dem sichtbaren linearen Pfad ab ELF `0x1e58` bedingungslos. Ob die Ausführung von außerhalb überhaupt in dieses Fenster gelangt, ist OFFEN.

Die Aussagen beruhen auf statischer Ghidra-Disassemblierung und Bytebeobachtung, nicht auf Laufzeitausführung. Die Referenzen der Stores auf Ghidra-Adresse `0x24208` wurden im ausgewählten Ghidra-Programm beobachtet; eine davon unabhängige globale Zielbindung wird hier nicht neu behauptet.

## Artefakt und Methode

- Eingabe: `libdal.so.1.0.1`, 18.076 Bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`.
- REA: `rea-agents` 6.5.0; Provider Ghidra 12.1.4; Linux x64 Host, erkannte ELF-Architektur ARM (`ARM:LE:32:v8`).
- Fenster: ELF `[0x1d30,0x1d58)` / Ghidra `[0x11d30,0x11d58)` und ELF `[0x1e58,0x1e78)` / Ghidra `[0x11e58,0x11e78)`.
- VERIFIZIERT: REA las je das vollständige Fenster und dekodierte jede 4-Byte-Instruktion darin. Kein objdump- oder sonstiger Disassembler-Fallback wurde verwendet; die REA-Ausgabe ließ keine für die Frage erforderliche Lücke.
- Beweis-IDs: Bytelesungen `ev_d6f5004d63437f09fc98fd02a3e702b0d43d7a6b555e0c9553535afea17effd8`, `ev_1a9ead33ae50cfb9cb871d034fe5bb094b2666fedcb995e90edc4139e249c2cf`. Instruktionen: `ev_c8db5e2240b59fb17d45ce4a30de83173221b831a710b4849b726acab3acd81b`, `ev_499f4cab55bb809cd506f020267f43fd6b0d6c0945b251f647bc631a6a1e75c2`, `ev_30c82d481c66b8d39bb97c2458b1f8f53c13118556d68e473cc8b798b57374c0`, `ev_0418adedd7cc36e619134847e244c290d07d3fb02c4afa3dd1e6ec98bbcb3ebe`, `ev_2f4ad05d0d6fbb8ef2a9a462d93b14964c71e7db2ac42b436094a7bac7f06414`, `ev_f59df3c6d09d45350be6fbb87f4e7efdf2cc2aa742e0c737b22c51faa072395e`, `ev_e2acdf86d6becfb091225a08a2eff28dc24eaa93cf4e250b6d22f46b2a9643d9`, `ev_0c22e4d6382f753b03d7cb24be0e6b6ddd41400da04693d79b05adcaa3c214a6`, `ev_913cd487fc66537b0e800f26480fdca06d0b833102b0df7d7ffbdd8ddfe9190b`, `ev_ecfa39625edd53cdbb08d719790dc1286513cfe37c2c32271d29fd068b290d63`, `ev_3b1e00a8fc64408795f876046b95e9e7a334adc996e1e6318ed39eb162106dbd`, `ev_59e30bd0f589eda80cf946552a11c5f157a9497054d65a07ef2430fc990c3ae2`, `ev_e8da0e25330f5baa29f8d8f518b8f7774a786ec292e433668b76c6025c22d0d3`, `ev_4e632e1229a2e25e7f5b31c8d86a750cdd21bdc2bdfb7356a63e45e733983f5e`, `ev_90d395b8e5ff1904a5a13c577ee9985c531d44f2ad93c32dda4e783ef2e754e7`, `ev_8d3e714387165a75066428ce9363a7c4fd04ac9faaf3af4c871b8b0aac61c8ce`, `ev_7417212fde7e097d5e4fda2d1eb4b51d5ae04dc7534a2027c8f85c0248908dcc`, `ev_74c2607997586f57d43e2d80d9c4011b59e1f85cee88525c97860e916bc6a6a4`.

## Fenster 1: ELF `0x1d30`–`0x1d57`

Die Maschinenwörter sind aus den beobachteten vier Bytes als little-endian 32-Bit-Wörter notiert. `r5` wird zunächst aus `[r3,#0x14]` geladen. `cmp r0,#0` setzt die Flags. `cmpne r5,#0` läuft nur bei vorherigem NE; die bedingten `mov`-Instruktionen aktualisieren selbst keine Flags. Das nachfolgende `beq` verwendet daher die durch das jeweils ausgeführte `cmp` gesetzten Flags.

| ELF-Adresse | Bytes | Maschinenwort | Ghidra-Disassemblierung |
|---|---|---|---|
| `0x1d30` | `14 50 93 e5` | `0xe5935014` | `ldr r5,[r3,#0x14]` |
| `0x1d34` | `00 00 50 e3` | `0xe3500000` | `cmp r0,#0x0` |
| `0x1d38` | `00 00 55 13` | `0x13550000` | `cmpne r5,#0x0` |
| `0x1d3c` | `01 50 a0 03` | `0x03a05001` | `moveq r5,#0x1` |
| `0x1d40` | `00 50 a0 13` | `0x13a05000` | `movne r5,#0x0` |
| `0x1d44` | `08 00 00 0a` | `0x0a000008` | `beq 0x00011d6c` |
| `0x1d48` | `01 20 a0 e3` | `0xe3a02001` | `mov r2,#0x1` |
| `0x1d4c` | `05 00 a0 e1` | `0xe1a00005` | `cpy r0,r5` |
| `0x1d50` | `28 20 c3 e5` | `0xe5c32028` | `strb r2,[r3,#0x28]` |
| `0x1d54` | `f0 87 bd e8` | `0xe8bd87f0` | `ldmia sp!,{r4,r5,r6,r7,r8,r9,r10,pc}` |

Lokale Def-Use- und Kantenableitung:

1. `0x1d30`: `r5 := load([r3 + 0x14])` (der geladene Wert wird im Fenster nicht anderweitig charakterisiert).
2. `0x1d34`: Flags aus `r0 - 0`.
3. Nur bei NE (`r0 != 0`) vergleicht `0x1d38` den geladenen Wert `r5` mit null und ersetzt die Flags.
4. Bei EQ setzt `0x1d3c` `r5 := 1`; bei NE setzt `0x1d40` `r5 := 0`. Beide `mov` behalten die vorherigen Flags.
5. `0x1d44` nimmt bei EQ die Kante zu `0x11d6c` (außerhalb des Fensters). Auf dem lokalen Nicht-EQ-Fall fällt der Kontrollfluss zu `0x1d48` durch.
6. `0x1d48` definiert `r2 := 1`; `0x1d4c` kopiert `r5` nach `r0` und verändert die Flags nicht. `0x1d50` speichert daher Byte `0x01` aus `r2` an der von Ghidra referenzierten Schreibadresse `0x24208`.

Äquivalent für den lokalen Store-Pfad: `r0 != 0` und der zuvor geladene Wert in `r5 != 0`. Ist `r0 == 0`, springt `beq` weg. Ist `r0 != 0`, aber der geladene Wert null, setzt `cmpne` EQ und `beq` springt weg. Nur der verbleibende NE-Fall erreicht den Store. Diese Auswertung setzt die üblichen ARM-Bedingungs-/Flagsemantiken der von Ghidra dekodierten Instruktionen voraus; sie ist keine beobachtete Ausführung.

## Fenster 2: ELF `0x1e58`–`0x1e77`

| ELF-Adresse | Bytes | Maschinenwort | Ghidra-Disassemblierung |
|---|---|---|---|
| `0x1e58` | `54 40 9f e5` | `0xe59f4054` | `ldr r4,[0x11eb4]` |
| `0x1e5c` | `00 50 a0 e3` | `0xe3a05000` | `mov r5,#0x0` |
| `0x1e60` | `04 40 8f e0` | `0xe08f4004` | `add r4,pc,r4` |
| `0x1e64` | `24 60 94 e5` | `0xe5946024` | `ldr r6,[r4,#0x24]` |
| `0x1e68` | `18 50 84 e5` | `0xe5845018` | `str r5,[r4,#0x18]` |
| `0x1e6c` | `05 00 56 e1` | `0xe1560005` | `cmp r6,r5` |
| `0x1e70` | `28 50 c4 e5` | `0xe5c45028` | `strb r5,[r4,#0x28]` |
| `0x1e74` | `08 00 00 0a` | `0x0a000008` | `beq 0x00011e9c` |

Lokale Def-Use- und Kantenableitung: `0x1e5c` definiert `r5 := 0`; zwischen dort und `0x1e70` gibt es keine weitere `r5`-Definition. `0x1e64` lädt `r6`; `0x1e68` schreibt zuvor das Wort aus `r5`; `0x1e6c` vergleicht `r6` mit `r5` und setzt Flags. `0x1e70` ist trotzdem ein unbedingtes `strb`, also erreicht Byte `0x00` den Store, sofern die Ausführung diese Instruktion im sichtbaren linearen Pfad erreicht. Der anschließende `beq` verzweigt auf `0x11e9c` (außerhalb des Fensters) und kann den bereits ausgeführten Store nicht verhindern.

## Alternativerklärung und Restunsicherheit

- VERIFIZIERT: Die Instruktion an ELF `0x1d50` speichert das Byte aus `r2`; die im Fenster sichtbare letzte Definition ist `mov r2,#1`.
- VERIFIZIERT: Die Instruktion an ELF `0x1e70` speichert das Byte aus `r5`; die im Fenster sichtbare letzte Definition ist `mov r5,#0`.
- HYPOTHESE: Die oben abgeleiteten Pfadbedingungen für ELF `0x1d50` folgen aus den ARM `EQ`/`NE`-Bedingungen und dem Erhalt der Flags durch die beiden `mov`-Instruktionen ohne `S`-Suffix.
- VERIFIZIERT (Alternativerklärung geprüft): Eine naheliegende Lesart wäre, dass der erste `beq` nur den Vergleich `r0` gegen null abbildet. Das gilt nur im Fall `r0 == 0`; für `r0 != 0` führt das sichtbare `cmpne r5,#0` zuvor eine zweite Flagprüfung aus. Für den zweiten Store könnte man `cmp r6,r5` als Store-Bedingung auffassen; die Instruktionsfolge zeigt jedoch, dass dieser Vergleich unmittelbar vor einem unbedingten `strb` und vor dem `beq` steht.
- OFFEN: Welche konkreten Eingabewerte `r0` bzw. der geladene Wert an `[r3,#0x14]` im Betrieb haben.
- OFFEN: Ob außerhalb des Fensters zusätzliche Einsprung-/Kontrollflusskanten existieren, die das Erreichen der Stores ändern. Für den zweiten Store ist nur die lokale Linearfolge bewertet.
- OFFEN: Bedeutung von Zieladresse, Speicherfeldern, Objektlayout, Aliasen und Laufzeitwirkungen; diese Punkte waren ausdrücklich ausgeschlossen.
- OFFEN: Die außerhalb des Fensters liegenden Branchziele `0x11d6c` und `0x11e9c` werden nicht analysiert.

## Validator und Manifest

`validate.py` überprüft die Identität und Größe des Eingabeartefakts, beide rohen Fenster an den angegebenen ELF-Dateioffsets sowie die im Manifest aufgeführten SHA-256-Werte. PASS: Der Fallback-Disassembler wurde nicht aufgerufen. `SHA256SUMS` enthält nur `report.md` und `validate.py`; das Manifest referenziert sich nicht selbst.
