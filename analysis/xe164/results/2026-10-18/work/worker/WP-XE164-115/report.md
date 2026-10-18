> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-115 — Xref-/Call-/Result-Lane

## Befund

**VERIFIZIERT** — Für die rohe Zeichenfolge `IoMgrConfigGetParameterValuePointer` gibt es in der Ghidra-Analyse genau einen materialisierten statischen Xref: von `0x10ecc`. Er ist eine `PARAM`-Datenreferenz auf das Stringobjekt, kein direkter API-Aufruf. Das Stringobjekt wird im selben bounded Ghidra-Funktionskörper an einem berechneten `blx r5` übergeben. Das Ziel dieses Aufrufs bleibt statisch ungelöst.

## Artefakt, Adressen und Werkzeuge

- Ziel: `libIoDrvDal.so.1.0.2`, 25 976 Byte, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.
- WP112 `string_hits.csv`: SHA-256 `b4d0d2df7230aeb8005f94f5d7aeaceddbd99582de6746a9acb30a9ea2cbb358`; der Eintrag für `/usr/lib/libIoDrvDal.so.1.0.2` nennt Offset `0x4835`.
- WP112 `elf_findings.csv`: SHA-256 `43de6fb26d5335e0189cca0b9f71f397b7d2740d111971568b5623d8e8214a88`.
- REA 6.5.0, Provider Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; Ziel von REA als ARM-ELF erkannt.
- Für die ELF-VMA-/PT_LOAD-Koordinaten nutzte ich nach der beobachteten REA-Lücke (REA lieferte die Ghidra-Adress-zu-Dateioffset-Abbildung, aber keine ELF-Segmenttabelle) lokal GNU readelf aus Binutils 2.44: `readelf -lW -SW <Zieldatei>`. Der erste LOAD hat Offset und VirtAddr `0`; `.rodata` beginnt bei VMA/Dateioffset `0x4680`, `.text` bei `0x0a34`. Keine weitere ELF-Werkzeuganalyse wurde ausgeführt.

| Objekt | Dateioffset | ELF-VMA | Ghidra-Adresse |
|---|---:|---:|---:|
| Stringanfang | `0x4835` | `0x4835` | `0x14835` |
| Xref-Instruktion `add r0,pc,r0` | `0x0ecc` | `0x0ecc` | `0x10ecc` |
| Indirekter Aufruf `blx r5` | `0x0ed0` | `0x0ed0` | `0x10ed0` |
| Beginn enthaltender Körper | `0x0b58` | `0x0b58` | `0x10b58` |

Die Ghidra-Adressen wurden nicht durch pauschale Basisarithmetik als Dateioffsets ausgegeben: REA `address_to_file_offset` ordnete `0x14835` zu `0x4835`, `0x10ecc` zu `0xecc`, `0x10ed0` zu `0xed0` und den Funktionseinstieg `0x10b58` zu `0xb58` zu. Der Abgleich mit readelfs erstem LOAD bestätigt für diese file-backed Bereiche VMA=Dateioffset. Ghidra verwendet hier die um `0x10000` verschobenen Analyseadressen.

## String und Xrefs

**VERIFIZIERT** — REA fand bei Ghidra-Adresse `0x14835` exakt `IoMgrConfigGetParameterValuePointer`. REA las 36 vollständige Bytes einschließlich NUL-Terminator:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`xrefs(0x14835)` lieferte genau `0x10ecc`. `inspect_native_instruction(0x10ecc)` beobachtete `add r0,pc,r0`, Bytes `00 00 8f e0`, und den Ghidra-ReferenceManager-Eintrag `PARAM`, Datenreferenz, Operand 0, von `0x10ecc` nach `0x14835`. Die REA-Abdeckung gilt für die von Ghidra materialisierten Referenzen in dieser Analyse; sie beweist keine Laufzeitreferenzierung und keine Vollständigkeit außerhalb dieser Provideranalyse.

## Bounded Lane

**VERIFIZIERT** — Die kleinste von Ghidra zugeordnete enthaltende Funktion ist die anonyme `FUN_00010b58`, Start `0x10b58`, ein zusammenhängender Funktionskörper `0x10b58–0x1145f` (inklusive), 2 312 Byte. Die einzige String-Xref-Instruktion liegt bei `0x10ecc` innerhalb dieses Körpers. Name und Quellfunktion bleiben unbekannt; der Decompilertext ist Analyseausgabe, kein Originalquelltext oder Funktionsvertrag.

Unmittelbarer Call-Lane bei Ghidra-Adressen:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

**VERIFIZIERT** — Die Register-/Stackwerte am Call sind auf dem Nullpfad des vorigen Lookup-Schritts: `r0 = 0x14835` (Stringadresse), `r1 = 0x260f0`, `r2 = 0`, `r3 = 0`, `[sp,#0] = 0`. `r3` war am Funktionseinstieg auf null gesetzt und wird nach jedem vorherigen Call mit dessen Rückgabewert verglichen; erreicht die Ausführung `0x10ed0`, hat der vorherige `bne` nicht verzweigt, also ist der beobachtete Vergleichswert null. Die Werte sind Callsite-Beobachtungen, keine rekonstruierte API-Signatur.

**VERIFIZIERT** — Im bounded Funktionskörper wird `r4` PC-relativ auf Ghidra-Adresse `0x26090` berechnet. Bei `0x10ec0` lädt `ldr r5,[r1],#0x60` den Call-Zielwert aus `[0x26090]`; zugleich wird `r1` nach dem Postincrement zu `0x260f0`. Pseudocode an dieser Stelle zeigt `(*DAT_00026090)("IoMgrConfigGetParameterValuePointer", &DAT_000260f0, 0, 0, 0)`. Der Maschinenbefund stützt damit den String als `r0` und die Adresse `0x260f0` als zweites Callargument; die Bezeichnungen „Resolver“, „Ausgabewert“ oder eine konkrete API-Semantik wären weitergehende Interpretationen.

**VERIFIZIERT** — GNU readelf ordnet die ELF-Adressen `0x16090` und `0x160f0` der `.bss` zu (die Ghidra-Adressen sind `0x26090`/`0x260f0`). Ghidra-`read_bytes` meldete an beiden Ghidra-Adressen null zurückgegebene Bytes und `complete=false`; die Slot-Inhalte sind in dieser statischen Analyse unbekannt. Für `.bss` gibt es keine initialisierten Datei-Bytes, aus denen sich der Wert des Call-Ziels oder der Slotinhalt ableiten ließe.

**VERIFIZIERT** — `resolve_native_call_targets(0x10ed0)` meldete `mechanism=computed`, `status=unresolved`, keine Ziele. `inspect_native_instruction` sah `blx r5`, `computed=true` und keine direkte Destination. Der konkrete Wert von `r5` ist somit nur als Load aus `[0x26090]` hergeleitet; Zielprozedur oder Providerbindung werden nicht behauptet.

**VERIFIZIERT** — Der Rückgabewert von `blx r5` liegt unmittelbar in `r0`; `subs r3,r0,#0` prüft ihn und `bne 0x11454` führt bei Nichtnull zum gemeinsamen Endpfad. Bei null läuft die Sequenz bei `0x10edc` mit dem nächsten String-/Slot-Paar weiter. Der pseudocodebeschriebene Funktionskörper gibt `iVar1` zurück. Ob der Wert semantisch Fehlercode, Status oder etwas anderes ist, bleibt offen.

## Alternative Erklärung und Restunsicherheit

**HYPOTHESE** — Die Wiederholung des Musters mit anderen API-Namen und benachbarten BSS-Slots passt zu einer Initialisierungssequenz, die Namen und Zielslots an eine generische indirekte Hilfsfunktion übergibt. Das erklärt die beobachtete Form, legt aber weder Identität noch Vertrag der Funktion bei `[0x16090]` fest.

**OFFEN** — Unbekannt bleiben der Laufzeitwert des BSS-Slots `[0x16090]`, das tatsächliche indirekte Ziel, die Bedeutung von Argument 2 und Rückgabewert, ob und wann der Pfad ausgeführt wird, sowie ob die BSS-Slots zur Laufzeit beschrieben werden. Eine alternative Erklärung ist eine andere Callback-/Dispatcherfunktion mit derselben beobachteten Aufrufsignatur. Der String allein belegt keinen Aufruf des gleichnamigen Accessor-Bodys und keinen vollständigen Funktionsvertrag.

## REA Evidence und Abdeckung

Kanonisches REA-Bundle: `rea-evidence.json`, 21 Evidence-Records, 0 Unknowns. Wesentliche Evidence IDs:

- Stringsuche `ev_4a2473b07e7e1997fe24eac3e30ae9ff56f5a0d7b20875a3e3aaa4cde08be94c`; Bytes `ev_9bc5dbcadf0d5dd4fc8b201e8cc1c1a69b2f1128694af19620451b44aa2925c1`; Mapping `ev_913d2efd7a8cc3d07b3930063092d41b88d0acc88bd237048f935bbcf9cfbf0e`.
- Mapping des Funktionseinstiegs `ev_75ba2dca477d5baefdfc8e05a90070b166b4f8f7ff518f09eebaf693cb041cb8`.
- Exakter Xref `ev_deb0ac37720145fd77eabea7bac392b713d10c1507d9d05080da935bcb84f49b`; typisierte Instruktion `ev_989dc2640aa4155257962ebf58bbc8522f4c5d10a35f79e0d83f555a4872873a`.
- Containment `ev_20b42440f7ba84e59fb87529968615dee152f566b0f2109abb3bddd3d87ccfb9`; Dossier `ev_26406a105c4643ccf8cb7e7116cc9dd9a06264327dbd61dada501c4b7fe895fc`; Pseudocode `ev_ffedbb80e3b434db0304680d3e170f027580b5cffde386637cd169bf72c3a7bb`.
- Lokale Instruktionen `ev_325cc85aaced88cd201765723e55f8b7df3c01d8c9c2d620825134238d237913`; Callinstruktion `ev_916a16522ebae34c18779b5f50cba29edb26e08b51f4d9da4d02553e422aaf67`; unresolved Ziel `ev_d5c32a32c9604129c831c7c6f056dc810afccd58ee3b3df3f666c5b6a56824cc`.
- BSS-Leseversuche `ev_9cea9139db2a6be472240c173a1bb6bd828fd59ecdecffbb56c8620d3d2ef801`, `ev_3cb372a6bd99ee2d693014ae937d65db17d562ce2e0ab4b238982e7dc6ebb11b`; Xrefs der lokalen Global-Slots `ev_7108a899f893106750b0e06a338dd50e8e84543a51b8aa1e7fd759ad417e0fdd`, `ev_57c1d3dc18538d595ab00b36b067f30732e80fb5a15c5da8d9875b517cd05da8`.

REA begrenzt Referenzen auf Ghidra-materialisierte Referenzen; berechnete Calls ohne ReferenceManager-Ziel bleiben unbekannt. Das Dossier enthält im gesamten großen Funktionskörper weitere ungelöste Calls; nur der Call bei `0x10ed0` wurde für diese Frage ausgewertet. Keine Laufzeit-, Netzwerk-, VM- oder Gerätebeobachtung.

## Prüfläufe

- **PASS** — Eingabegröße und SHA-256 stimmen mit WP-Eingaben überein; die angegebene WP112-Xref-Tabelle und ELF-Findings-Tabelle wurden anhand ihrer Hashes verifiziert.
- **PASS** — `validate.py` prüft Bundle-Identität, exakten Stringtreffer und Bytes, den einzigen materialisierten String-Xref, Adressabbildungen, unresolved computed call, Funktionskörper, Ausgabedateien und deren SHA256SUMS-Einträge.
- **NOT_RUN** — Dynamische oder Hardwareprüfung; außerhalb des Work-Package-Umfangs.

## Erzeugte Dateien

- `rea-evidence.json` — SHA-256 steht in `SHA256SUMS`.
- `validate.py` — SHA-256 `ab84c66179d8b273e1679875ffe9854795cc3c639948029ccae8a72dbaa11ce0`.
- `report.md` — Hash steht in `SHA256SUMS`.
- `SHA256SUMS` — Hashmanifest für Bericht, Bundle und Validator (nicht selbst enthalten, um zirkuläre Selbstreferenz zu vermeiden).
