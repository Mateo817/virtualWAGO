> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-218: exakte libdal-Referenzen auf ELF `0x141e0`

## Ergebnis

**VERIFIZIERT — Ghidra-materialisierte Xrefs.** Für das gebundene Artefakt lieferte Ghidra 12.1.4 insgesamt 39 eingehende Xrefs auf exakt `0x241e0`: 19 `READ`, 2 `WRITE` und 18 `PARAM`, hier als `OTHER` geführt. Das ist die vollständige von REA/Ghidra für diese exakte Adresse materialisierte Liste; es ist keine Aussage über nicht materialisierte Laufzeit- oder Aliaszugriffe.

**VERIFIZIERT — direkte Schreibinstruktion mit rekonstruierter Zielarithmetik.** `0x11df0` ist `str r2,[r3]` und die ELF-Adressrechnung für `r3` bindet den Basispointer an exakt `0x141e0` (Ghidra `0x241e0`). Der statische Code zeigt damit einen direkten Schreiber. Das sagt nicht, dass der Store zur Laufzeit ausgeführt wird.

**VERIFIZIERT — Ghidra-WRITE-Xref; OFFEN — unabhängige Effektivadresse.** `0x11c9c` ist `str r0,[r4]` und Ghidra materialisiert dafür eine `WRITE`-Xref auf exakt `0x241e0`. Das exakte Sitefenster zeigt die Herkunft des Wertes in `r4` nicht; nach den Vorgaben bleibt dessen Effektivadress-Arithmetik offen. Die Xref wird deshalb als methodengebundener WRITE-Befund geführt, aber nicht als zusätzlich unabhängig rekonstruierter Schreiber bestätigt.

## Ziel- und Segmentbindung

**VERIFIZIERT.** Eingabe: `FW31-LIBDAL-1.0.1`, 18.076 Byte, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. ELF32 little-endian ARM, `ET_DYN`. `readelf -SW` weist `.bss` als `NOBITS`, ELF-VA `[0x141dc,0x1420c)`, Größe `0x30` aus. Ziel `0x141e0` ist `.bss+4`, hat daher keinen file-backed Byte-Offset. REA/Ghidra bindet das ELF mit Image Base `0x10000`; daraus folgt die Zieladresse `0x241e0`. Der Nachbar `0x14208` ist nicht Gegenstand der Referenzklassifikation.

**VERIFIZIERT.** Ghidras Segmentliste markiert `.bss` als lesbar/schreibbar, nicht ausführbar und `initialized=false`; `.text` ist `[0x116b4,0x13c80)`, ausführbar und initialisiert. Die vollständigen file-backed `SHF_EXECINSTR`-Abschnitte aus `readelf -SW` sind `.init` `[0x1334,0x1340)`, `.plt` `[0x1340,0x16b4)`, `.text` `[0x16b4,0x3c80)` und `.fini` `[0x3c80,0x3c88)`. Bereiche sind ELF-VA mit exklusivem Ende.

## Vollständige Ghidra-Xref-Liste

Die Sites stehen in Ghidras Adressraum. `ELF-VA` ist jeweils `Site - 0x10000`. Das letzte Feld ist der exakte 20-Byte-Rohbereich `[Site-8, Site+12)`, als gespeicherte Bytefolge (Little Endian), also fünf 32-Bit-Wörter. Die disassemblierte Siteinstruktion ist aufgenommen, damit der `WRITE`-Typ unmittelbar an einer Store-Instruktion geprüft werden kann.

**VERIFIZIERT — Evidence `ev_20b1cb17b425b5e0ae86b5463375d6a4641bb4bd26514e157593cc0a1367abc2` (Xrefs) und `ev_3c504ab05519a1f937edc46666fa6b1aadc97f498004c02e4865c39e4abdb4f0` (Zielinstruktion / typed incoming references).** Ghidras `inspect_native_instruction(0x241e0)` weist dieselben 39 Quellen mit `READ`/`WRITE`/`PARAM` aus. Der Zieladressbefund wird hier als `OTHER` ausgegeben, wenn die Referenzart `PARAM` ist; daraus wird kein Speicherzugriff abgeleitet.

| Site (Ghidra) | ELF-VA | Klasse | Instruktion an Site | Rohbytes `[Site-8, Site+12)` |
|---:|---:|---|---|---|
| `0x1198c` | `0x198c` | READ | `ldr r0,[r12,#0]` | `0040a0e108d04de200009ce504408de5000050e3` |
| `0x119f4` | `0x19f4` | READ | `ldr r0,[r7,#0]` | `07708fe00c408de5000097e5000050e30b00000a` |
| `0x11a70` | `0x1a70` | OTHER | `add r3,pc,r3` | `04809de50c708de203308fe00500a0e108608de2` |
| `0x11a7c` | `0x1a7c` | READ | `ldr r1,[r3,#0]` | `0500a0e108608de2001093e593feffeb040000ea` |
| `0x11ad8` | `0x1ad8` | READ | `ldr r0,[r6,#0]` | `10309de5013083e2000096e50510a0e110308de5` |
| `0x11b44` | `0x1b44` | READ | `ldr r0,[r6,#0]` | `0520a0e10030a0e1000096e50c3185e530feffeb` |
| `0x11ba0` | `0x1ba0` | OTHER | `add r3,pc,r3` | `0000a0e344109fe503308fe07001c4e5002194e5` |
| `0x11c9c` | `0x1c9c` | WRITE | `str r0,[r4]` | `00219fe500319fe5000084e5021096e7030096e7` |
| `0x11d08` | `0x1d08` | READ | `ldr r2,[r3,#0]` | `b0309fe503308fe0002093e5000052e31c0083e5` |
| `0x11dc4` | `0x1dc4` | OTHER | `add r3,pc,r3` | `b41f0000dc309fe503308fe02820d3e5000052e3` |
| `0x11de0` | `0x1de0` | READ | `ldr r0,[r3,#0]` | `1eff2fe170402de9000093e5000050e30200000a` |
| `0x11df0` | `0x1df0` | WRITE | `str r2,[r3]` | `0200000a0020a0e3002083e56efdffeba8309fe5` |
| `0x11dfc` | `0x1dfc` | OTHER | `add r3,pc,r3` | `6efdffeba8309fe503308fe0040093e5000050e3` |
| `0x11e1c` | `0x1e1c` | OTHER | `add r3,pc,r3` | `66fdffeb8c309fe503308fe01c0093e5000050e3` |
| `0x11e3c` | `0x1e3c` | OTHER | `add r3,pc,r3` | `b8fdffeb70309fe503308fe0140093e5000050e3` |
| `0x11ed4` | `0x1ed4` | OTHER | `add r3,pc,r3` | `30309fe504e02de503308fe00cd04de204008de5` |
| `0x11ee0` | `0x1ee0` | READ | `ldr r0,[r3,#0]` | `0cd04de204008de5000093e5000050e30300000a` |
| `0x11f10` | `0x1f10` | OTHER | `add r3,pc,r3` | `28309fe504e02de503308fe00cd04de204008de5` |
| `0x11f1c` | `0x1f1c` | READ | `ldr r0,[r3,#0]` | `0cd04de204008de5000093e5000050e30100000a` |
| `0x11f54` | `0x1f54` | OTHER | `add r3,pc,r3` | `4c309fe510402de903308fe008d04de204008de5` |
| `0x11f60` | `0x1f60` | READ | `ldr r0,[r3,#0]` | `08d04de204008de5000093e5000050e30a00000a` |
| `0x1204c` | `0x204c` | OTHER | `add r3,pc,r3` | `60309fe504008de503308fe0000093e5000050e3` |
| `0x12050` | `0x2050` | READ | `ldr r0,[r3,#0]` | `04008de503308fe0000093e5000050e30f00000a` |
| `0x120b8` | `0x20b8` | OTHER | `add r3,pc,r3` | `0c309fe50010a0e103308fe0040093e54bfdffea` |
| `0x12104` | `0x2104` | READ | `ldr r1,[r8,#0]` | `0050a0e10160a0e1001098e50700a0e10290a0e1` |
| `0x12114` | `0x2114` | READ | `ldr r0,[r8,#0]` | `0290a0e1effcffeb000098e5e7fcffeb000050e3` |
| `0x1219c` | `0x219c` | OTHER | `add r3,pc,r3` | `30309fe504e02de503308fe00cd04de204008de5` |
| `0x121a8` | `0x21a8` | READ | `ldr r0,[r3,#0]` | `0cd04de204008de5000093e5000050e30300000a` |
| `0x123cc` | `0x23cc` | OTHER | `add r3,pc,r3` | `0000a0e330109fe503308fe07001c4e5002194e5` |
| `0x12410` | `0x2410` | OTHER | `add r3,pc,r3` | `f0412de920d04de203308fe008408de20070a0e1` |
| `0x12420` | `0x2420` | READ | `ldr r1,[r3,#0]` | `0070a0e104608de2001093e50400a0e129fcffeb` |
| `0x124a4` | `0x24a4` | OTHER | `add r3,pc,r3` | `f0432de924d04de203308fe008408de20080a0e1` |
| `0x124b8` | `0x24b8` | READ | `ldr r1,[r3,#0]` | `0170a0e10400a0e1001093e504fcffeb04608de2` |
| `0x12540` | `0x2540` | OTHER | `add r3,pc,r3` | `f0402de924d04de203308fe008408de204608de2` |
| `0x12550` | `0x2550` | READ | `ldr r1,[r3,#0]` | `04608de20d50a0e1001093e50400a0e1ddfbffeb` |
| `0x125cc` | `0x25cc` | OTHER | `add r3,pc,r3` | `f0402de924d04de203308fe008408de204608de2` |
| `0x125dc` | `0x25dc` | READ | `ldr r1,[r3,#0]` | `04608de20d50a0e1001093e50400a0e1bafbffeb` |
| `0x12658` | `0x2658` | OTHER | `add r3,pc,r3` | `f0402de924d04de203308fe008408de204608de2` |
| `0x12668` | `0x2668` | READ | `ldr r1,[r3,#0]` | `04608de20d50a0e1001093e50400a0e197fbffeb` |

Die fünf Rohwörter jedes Fensters (32-Bit little-endian, in Adressreihenfolge) sind:

| Site | Rohwörter `[Site-8, Site+12)` |
|---:|---|
| `0x1198c` | `e1a04000 e24dd008 e59c0000 e58d4004 e3500000` |
| `0x119f4` | `e08f7007 e58d400c e5970000 e3500000 0a00000b` |
| `0x11a70` | `e59d8004 e28d700c e08f3003 e1a00005 e28d6008` |
| `0x11a7c` | `e1a00005 e28d6008 e5931000 ebfffe93 ea000004` |
| `0x11ad8` | `e59d3010 e2833001 e5960000 e1a01005 e58d3010` |
| `0x11b44` | `e1a02005 e1a03000 e5960000 e585310c ebfffe30` |
| `0x11ba0` | `e3a00000 e59f1044 e08f3003 e5c40170 e5942100` |
| `0x11c9c` | `e59f2100 e59f3100 e5840000 e7961002 e7960003` |
| `0x11d08` | `e59f30b0 e08f3003 e5932000 e3520000 e583001c` |
| `0x11dc4` | `00001fb4 e59f30dc e08f3003 e5d32028 e3520000` |
| `0x11de0` | `e12fff1e e92d4070 e5930000 e3500000 0a000002` |
| `0x11df0` | `0a000002 e3a02000 e5832000 ebfffd6e e59f30a8` |
| `0x11dfc` | `ebfffd6e e59f30a8 e08f3003 e5930004 e3500000` |
| `0x11e1c` | `ebfffd66 e59f308c e08f3003 e593001c e3500000` |
| `0x11e3c` | `ebfffdb8 e59f3070 e08f3003 e5930014 e3500000` |
| `0x11ed4` | `e59f3030 e52de004 e08f3003 e24dd00c e58d0004` |
| `0x11ee0` | `e24dd00c e58d0004 e5930000 e3500000 0a000003` |
| `0x11f10` | `e59f3028 e52de004 e08f3003 e24dd00c e58d0004` |
| `0x11f1c` | `e24dd00c e58d0004 e5930000 e3500000 0a000001` |
| `0x11f54` | `e59f304c e92d4010 e08f3003 e24dd008 e58d0004` |
| `0x11f60` | `e24dd008 e58d0004 e5930000 e3500000 0a00000a` |
| `0x1204c` | `e59f3060 e58d0004 e08f3003 e5930000 e3500000` |
| `0x12050` | `e58d0004 e08f3003 e5930000 e3500000 0a00000f` |
| `0x120b8` | `e59f300c e1a01000 e08f3003 e5930004 eafffd4b` |
| `0x12104` | `e1a05000 e1a06001 e5981000 e1a00007 e1a09002` |
| `0x12114` | `e1a09002 ebfffcef e5980000 ebfffce7 e3500000` |
| `0x1219c` | `e59f3030 e52de004 e08f3003 e24dd00c e58d0004` |
| `0x121a8` | `e24dd00c e58d0004 e5930000 e3500000 0a000003` |
| `0x123cc` | `e3a00000 e59f1030 e08f3003 e5c40170 e5942100` |
| `0x12410` | `e92d41f0 e24dd020 e08f3003 e28d4008 e1a07000` |
| `0x12420` | `e1a07000 e28d6004 e5931000 e1a00004 ebfffc29` |
| `0x124a4` | `e92d43f0 e24dd024 e08f3003 e28d4008 e1a08000` |
| `0x124b8` | `e1a07001 e1a00004 e5931000 ebfffc04 e28d6004` |
| `0x12540` | `e92d40f0 e24dd024 e08f3003 e28d4008 e28d6004` |
| `0x12550` | `e28d6004 e1a0500d e5931000 e1a00004 ebfffbdd` |
| `0x125cc` | `e92d40f0 e24dd024 e08f3003 e28d4008 e28d6004` |
| `0x125dc` | `e28d6004 e1a0500d e5931000 e1a00004 ebfffbba` |
| `0x12658` | `e92d40f0 e24dd024 e08f3003 e28d4008 e28d6004` |
| `0x12668` | `e28d6004 e1a0500d e5931000 e1a00004 ebfffb97` |

## Statische Adressrechnung und beide WRITE-Sites

**VERIFIZIERT.** Die für beide WRITE-Sites ausgewerteten REA-Instruktionen lauten:

| Ghidra-Site | ELF-Site | REA-Typ | Siteinstruktion | Ergebnis |
|---:|---:|---|---|---|
| `0x11c9c` | `0x1c9c` | WRITE | `str r0,[r4]` | Ghidra-Xref auf `0x241e0`; `r4`-Effektivadresse im erlaubten Fenster nicht unabhängig hergeleitet (`OFFEN`). |
| `0x11df0` | `0x1df0` | WRITE | `str r2,[r3]` | Ghidra-Xref auf `0x241e0`; `r3` wird durch die unten belegte PC+Literal-Rechnung auf exakt `0x141e0` gesetzt (`VERIFIZIERT`). |

**VERIFIZIERT.** Für `0x11df0`: die Dateiwörter bei ELF-VA `0x1dc0` und `0x1dc4` sind `e59f30dc` (`ldr r3,[pc,#0xdc]`) und `e08f3003` (`add r3,pc,r3`). Beim LDR ist ARM-PC `0x1dc8`, damit liegt das Literal bei `0x1ea4`; das file-backed Literalwort dort ist `0x00012414`. Beim ADD ist ARM-PC `0x1dcc`. Somit wird `r3 = 0x1dcc + 0x12414 = 0x141e0`. Die überlappenden erlaubten Sitefenster zeigen danach den Zugriff `ldr r0,[r3]` bei ELF `0x1de0` und den konkreten Store `str r2,[r3]` bei ELF `0x1df0`, ohne dazwischen eine Instruktion, die `r3` neu belegt. Mit der Image-Base-Zuordnung entspricht `0x141e0` dem Ghidra-Ziel `0x241e0`.

**VERIFIZIERT.** Der vollständige A32-Scan über file-backed `SHF_EXECINSTR`-Abschnitte fand zehn benachbarte PC-literal-`LDR`/`ADD rd,pc,rd`-Konstruktionen, die arithmetisch `0x141e0` materialisieren. Die Sites sind ELF-VA; die Literalwörter liegen in `.text` und sind file-backed. Die Site-Zuordnung zu Ghidras exakten Xrefs ist separat angegeben; keine Bedeutung wird aus Namen abgeleitet.

| LDR | ADD | Register | Literalstelle | Literalwort | Ghidra-Xref-Zuordnung |
|---:|---:|---:|---:|---:|---|
| `0x1d00` | `0x1d04` | `r3` | `.text:0x1db8` | `0x000124d4` | ADD-Site kein eigener Xref; folgende `ldr r2,[r3]` bei ELF `0x1d08` ist die Ghidra-READ-Xref `0x11d08`. |
| `0x1dc0` | `0x1dc4` | `r3` | `.text:0x1ea4` | `0x00012414` | Ghidra `0x11dc4`, `PARAM` → OTHER. |
| `0x1df8` | `0x1dfc` | `r3` | `.text:0x1ea8` | `0x000123dc` | Ghidra `0x11dfc`, `PARAM` → OTHER. |
| `0x1e18` | `0x1e1c` | `r3` | `.text:0x1eac` | `0x000123bc` | Ghidra `0x11e1c`, `PARAM` → OTHER. |
| `0x1e38` | `0x1e3c` | `r3` | `.text:0x1eb0` | `0x0001239c` | Ghidra `0x11e3c`, `PARAM` → OTHER. |
| `0x1eb8` | `0x1ebc` | `r0` | `.text:0x1ec8` | `0x0001231c` | Kein exakter Ghidra-Xref an ADD-Site. |
| `0x1fac` | `0x1fb0` | `r4` | `.text:0x202c` | `0x00012228` | Kein exakter Ghidra-Xref an ADD-Site. |
| `0x20d0` | `0x20d4` | `r8` | `.text:0x217c` | `0x00012104` | Kein exakter Ghidra-Xref an ADD-Site. |
| `0x2180` | `0x2184` | `r3` | `.text:0x2190` | `0x00012054` | Kein exakter Ghidra-Xref an ADD-Site. |
| `0x22ac` | `0x22b0` | `r7` | `.text:0x2398` | `0x00011f28` | Kein exakter Ghidra-Xref an ADD-Site. |

**VERIFIZIERT — begrenzte Nullfunde.** Der Validator fand in den untersuchten A32-Formen keine PC-relativen LDR/STR-Effektivadresse direkt auf das Ziel, kein Literalwort `0x141e0` in den ausführbaren Abschnitten, keine A32-ADR-artige ADD/SUB-immediate-Materialisierung und kein direkt benachbartes MOVW/MOVT-Paar, das `0x141e0` bildet. Diese Nullfunde widerlegen weder die zehn gefundenen LDR+ADD-Rechnungen noch die registerbasierten Ghidra-READ/WRITE-Xrefs. Der Nullfund gilt ausschließlich für die im Validator aufgeführten Formen und ist kein Beleg für Nichtbenutzung zur Laufzeit.

## Methode, Toolversionen und Restunsicherheit

**VERIFIZIERT.** REA `open_binary` band die Eingabe per SHA-256; Provider Ghidra `12.1.4`, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Xref-Evidence: `ev_20b1cb17b425b5e0ae86b5463375d6a4641bb4bd26514e157593cc0a1367abc2`. Zielinstruktions-Evidence `ev_3c504ab05519a1f937edc46666fa6b1aadc97f498004c02e4865c39e4abdb4f0`: Zielstatus `data`, 39 eingehende Referenzen. Overview-Evidence `ev_a40e925ba5e6499cd86d0c350ecb767487473d9b374e0de0522a6091e924252f`; Segment-Evidence aus `list_segments`. REA stellte Operandtokens bereit, aber keine Effektivadresszerlegung für registerbasierte Speicheroperanden. Deshalb war der lokale Fallback für die festgestellte Adressarithmetik-Lücke erforderlich.

**VERIFIZIERT.** Fallback-Werkzeuge: GNU readelf 2.44 und GNU ARM objdump `arm-linux-gnueabihf-objdump` 2.44. Das generische `objdump` 2.44 konnte die ARM-Architektur nicht dekodieren; der installierte ARM-spezifische GNU-Disassembler war verfügbar. `validate.py` liest ausschließlich die lokale Eingabe, bindet ELF-Identität und Abschnittsgrenzen, prüft alle 39 gespeicherten Rohfenster und scannt die vollständigen file-backed `SHF_EXECINSTR`-Abschnitte für die im Skript explizit decodierten A32-Formen.

**OFFEN.** Die Effektivadresse von `str r0,[r4]` bei `0x11c9c` bleibt in der reservierten Fenstergrenze unrekonstruiert. Computed/indirect Aliasauflösung, nicht aufgeführte Instruction-Encoding-Modi und Laufzeitbeobachtung waren ausgeschlossen. Das schränkt die stärkere unabhängige Store-Bindung an dieser einen Site ein, ändert aber den Ghidra-`WRITE`-Xrefbefund nicht.

**OFFEN.** Statische Referenzen belegen keine Ausführung, keine Runtime-Nichtbenutzung und keine Semantik oder Typen des Wortes. Die zehn PC+Literal-Konstruktionen sind nur als berechnete Zieladressen klassifiziert; außer den separat belegten exakten Lese-/Schreibinstruktionen wird keine Speichersemantik daraus abgeleitet.

## Validator-Ausführung

**PASS.** `python3 validate.py` — ELF-Identität, Ziel-/Segmentbindung, 39 Fenster, Kategorien und exakte Kandidatenliste der spezifizierten A32-Formen geprüft. Sollausgabe: 19 READ, 2 WRITE, 18 OTHER; zehn PC-literal-ADD-Konstruktionen; leere Resultate für direkte PC-relative Speicher-Effektivadresse, Literalwort `0x141e0`, PC-immediate-Materialisierung und benachbartes MOVW/MOVT-Paar.

## Self-reference-freies Manifest

`SHA256SUMS` enthält die Hashes der Eingabe sowie der beiden Ergebnisdateien `report.md` und `validate.py`; das Manifest selbst ist absichtlich nicht enthalten.
