> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-195 — IoDrvDal loader-to-indirect-call window

## Ergebnis

**VERIFIZIERT (statisch, exakt begrenztes Fenster):** Im ELF32-ARM-Objekt führt `0x2fec` einen direkten `BL` auf `LibraryLoader_LoadSymbol@plt` aus. Unmittelbar davor setzt der sichtbare Code `r0=r7`, `r1=r10`, `r2=r5`. Danach wird das zurückgegebene `r0` bei `0x2ff0` mit null verglichen. Der Nullpfad verzweigt bei `0x2ff4` nach `0x3004`; dort lädt `ldr r3,[sp,#0x70]`, setzt `r0=r4`, speichert `r7` nach `[r4,#0x614]` und ruft bei `0x3010` das in `r3` geladene Ziel mit `blx r3` auf. Der Nichtnullpfad läuft über `0x2ff8`/`0x2ffc` zum direkten `LibraryLoader_LibraryClose@plt`-Aufruf und springt bei `0x3000` nach `0x32f0`.

Das Hash des exakt untersuchten Codefensters ist `0ff2d728b7ac89b5a721c8614a0572cb1db71100d5b95dc1467f6f1c53d4b703` (112 Bytes bei Datei-/ELF-VA `0x2fa8`).

Resolver-Rückgabe, drittes Argument und indirektes Call-Target sind verschiedene sichtbare Werte:

- Resolver-Rückgabe: `r0` nach dem direkten Aufruf bei `0x2fec`; der Code testet nur, ob dieses Wort null ist.
- Drittes Argument an `LibraryLoader_LoadSymbol`: `r2`, gesetzt aus `r5` bei `0x2fe0`. Eine Rolle als Ausgabezeiger ist im Fenster nicht belegt; sie folgt nicht aus dem Exportnamen.
- Indirektes Call-Target bei `0x3010`: `r3`, geladen separat aus `[sp,#0x70]` bei `0x3004`. Das Fenster zeigt nicht, dass dieser Stackwert aus dem Resolver-Aufruf oder aus `r5` stammt.

Die Interpretation „Resolver schreibt ein Symbolziel über `r5`, und `[sp+0x70]` enthält dasselbe Ziel“ bleibt **HYPOTHESE**. Die getrennte Register- und Stackbehandlung ist **VERIFIZIERT**; eine Datenabhängigkeit zwischen ihnen ist nicht sichtbar. `0x3014` vergleicht die Rückgabe des indirekten Aufrufs mit null. Der anschließende Zweig liegt bei `0x3018` und damit außerhalb des beauftragten Fensters.

## Lückenlose Instruktionsliste

Die Adressen sind ELF-VA und Dateioffset (der `.text`-Bereich ist dateigebunden und beide Werte stimmen hier überein). REA/Ghidra verwendet für dieselben Bytes jeweils `+0x10000`; die REA-Adresse steht in Klammern. Alle 28 A32-Instruktionen des halb offenen Bereichs `[0x2fa8,0x3018)` sind erfasst.

| ELF-VA / Datei | REA/Ghidra | Wort | Instruktion | lokale Wirkung und Kontrollfluss |
|---:|---:|---:|---|---|
| `0x2fa8` | `0x12fa8` | `e59f23b4` | `ldr r2,[pc,#0x3b4]` | Lädt Literalwort von `0x3364` in `r2`. |
| `0x2fac` | `0x12fac` | `e59d1018` | `ldr r1,[sp,#0x18]` | Stackwert nach `r1`. |
| `0x2fb0` | `0x12fb0` | `e59d0070` | `ldr r0,[sp,#0x70]` | Stackwert nach `r0`. |
| `0x2fb4` | `0x12fb4` | `e08f2002` | `add r2,pc,r2` | Verwendet ARM-PC `0x2fbc` plus geladenes Literal `0xfffffdf0`; ergibt lokal `r2=0x2dac`. |
| `0x2fb8` | `0x12fb8` | `ebfff68b` | `bl 0x9ec` | Direkter PLT-Aufruf `g_slist_find_custom`; Rückgabe in `r0`. |
| `0x2fbc` | `0x12fbc` | `e3500000` | `cmp r0,#0` | Prüft vorherige Rückgabe. |
| `0x2fc0` | `0x12fc0` | `0a0000ca` | `beq 0x32f0` | Bei `r0==0` Sprung nach `0x32f0`. |
| `0x2fc4` | `0x12fc4` | `e5907000` | `ldr r7,[r0]` | Lädt Wort über `r0` nach `r7`. |
| `0x2fc8` | `0x12fc8` | `e3570000` | `cmp r7,#0` | Prüft geladenes Wort. |
| `0x2fcc` | `0x12fcc` | `0a0000c7` | `beq 0x32f0` | Bei `r7==0` Sprung nach `0x32f0`. |
| `0x2fd0` | `0x12fd0` | `e1a00007` | `mov r0,r7` | Argumentregister für folgenden Aufruf. |
| `0x2fd4` | `0x12fd4` | `ebfff687` | `bl 0x9f8` | Direkter PLT-Aufruf `LibraryLoader_LibraryOpen`; Rückgabe in `r0`. |
| `0x2fd8` | `0x12fd8` | `e3500000` | `cmp r0,#0` | Prüft vorherige Rückgabe. |
| `0x2fdc` | `0x12fdc` | `1a0000c3` | `bne 0x32f0` | Bei `r0!=0` Sprung nach `0x32f0`. |
| `0x2fe0` | `0x12fe0` | `e1a02005` | `mov r2,r5` | Drittes Registerargument für `LibraryLoader_LoadSymbol`. |
| `0x2fe4` | `0x12fe4` | `e1a0100a` | `mov r1,r10` | Zweites Registerargument. |
| `0x2fe8` | `0x12fe8` | `e1a00007` | `mov r0,r7` | Erstes Registerargument. |
| `0x2fec` | `0x12fec` | `ebfff66c` | `bl 0x9a4` | Direkter PLT-Aufruf `LibraryLoader_LoadSymbol`; Rückgabe in `r0`. |
| `0x2ff0` | `0x12ff0` | `e3500000` | `cmp r0,#0` | Prüft Resolver-Rückgabe. |
| `0x2ff4` | `0x12ff4` | `0a000002` | `beq 0x3004` | Bei `r0==0` zum indirekten Aufrufpfad; bei `r0!=0` Fallthrough in den Close-Pfad. |
| `0x2ff8` | `0x12ff8` | `e1a00007` | `mov r0,r7` | Argument für den Close-Aufruf. |
| `0x2ffc` | `0x12ffc` | `ebfff662` | `bl 0x98c` | Direkter PLT-Aufruf `LibraryLoader_LibraryClose`. |
| `0x3000` | `0x13000` | `ea0000ba` | `b 0x32f0` | Unbedingter Sprung; verbindet den Nichtnullpfad nicht mit `0x3010`. |
| `0x3004` | `0x13004` | `e59d3070` | `ldr r3,[sp,#0x70]` | Lädt das separate Stackwort nach `r3`; es ist das Registerziel des folgenden `blx`. |
| `0x3008` | `0x13008` | `e1a00004` | `mov r0,r4` | Setzt `r0` für den indirekten Aufruf auf den vor dem Fenster bestimmten Wert `r4`. |
| `0x300c` | `0x1300c` | `e5847614` | `str r7,[r4,#0x614]` | Speichert `r7` nach `[r4+0x614]` vor dem Aufruf. |
| `0x3010` | `0x13010` | `e12fff33` | `blx r3` | Indirekter Call über `r3`; Rückgabe in `r0`. |
| `0x3014` | `0x13014` | `e3500000` | `cmp r0,#0` | Vergleicht die indirekte Rückgabe. Folgekontrolle nicht im Fenster. |

## Literal und importierte Symbole

- **VERIFIZIERT:** Die `ldr`-Referenz bei `0x2fa8` adressiert `0x3364`. REA/Ghidra meldet dort die vollständigen vier Bytes `f0fdffff` (Evidence `ev_4ead3a20a71729bbf00223338777ca7188b3eca45c6471690f8ef8e166e64583`); Little-Endian-Wort `0xfffffdf0`. Die Addition bei `0x2fb4` ergibt mit ARM-PC `0x2fbc` den Wert `0x2dac`. Dieses Literalargument gehört zum früheren direkten Aufruf `g_slist_find_custom`, nicht zum späteren `LibraryLoader_LoadSymbol`-Aufruf, dessen `r2` bei `0x2fe0` aus `r5` kommt.
- **VERIFIZIERT:** GNU ARM objdump decodiert den direkten Aufruf bei `0x2fec` als `bl 0x9a4 <LibraryLoader_LoadSymbol@plt>`. REA/Ghidra adressiert den Import als `0x109a4` (Datei-/ELF-Adresse `0x9a4`) und benennt ihn `<EXTERNAL>::LibraryLoader_LoadSymbol` (Evidence `ev_a9e06218f7ca82247e0a2af9a8605445d69ec00a7e56f90c2dd9198fac71fd88`; vollständiger Datensatz im Evidence-Bundle). `readelf -Ws` zeigt `LibraryLoader_LoadSymbol` als undefinierten globalen Funktionsimport; `readelf -rW` zeigt `R_ARM_JUMP_SLOT` an `0x16020` für denselben Namen.
- **VERIFIZIERT:** Der frühe Aufruf bei `0x2fb8` ist ein anderer Import: `g_slist_find_custom`; `readelf -rW` führt dessen `R_ARM_JUMP_SLOT` bei `0x16038`. Ebenso sind `LibraryLoader_LibraryOpen` (`0x2fd4`) und `LibraryLoader_LibraryClose` (`0x2ffc`) getrennte direkte Aufrufe.

Der Export-/Importname ist kein vollständiger Funktionsvertrag. Die Analyse behauptet weder Quellsprachensignatur noch Typ oder Semantik des dritten Arguments. `r5` ist im Fenster nur dessen beobachteter Wert im Register `r2`; der Zielwert für `blx` ist separat `[sp+0x70]` in `r3`.

## Eingehende Kante, Grenzen und Alternativerklärung

Die einzige notwendige eingehende Kante wird als vorhandene Kontrollflusskante in diesem Funktionskörper benannt: beim Eintritt in die Teilsequenz liegt der Ausführungspfad auf `0x2fa8`; ihre Herkunft wird nicht rückwärts verfolgt. Das REA-Inventar ordnet die Instruktionen der Ghidra-Prozedur `0x12ddc` zu, aber es wird kein vorheriger Code gelesen.

**Alternativerklärung (HYPOTHESE):** `r5` könnte an `LibraryLoader_LoadSymbol` einen Ausgabepuffer übergeben, während `[sp+0x70]` zuvor unabhängig initialisiert worden sein könnte und nach dem Resolver-Aufruf auf denselben Funktionszeigerwert zeigt. Der Codeausschnitt lässt beides zu; er belegt weder die Schreibwirkung des Imports noch Gleichheit/Herkunft der Zielwörter.

**OFFEN:** Herkunft von `r4`, `r5`, `r7`, `r10` und `[sp+0x70]`; ob `r5` ein Ausgabezeiger ist; ob der Import den Stackwert beeinflusst; die Bedeutung der Rückgabecodes; die Argumente `r1/r2` des indirekten Aufrufs nach dem externen Aufruf; Laufzeitverhalten. Für `r1/r2` am `0x3010` belegt das Fenster keine Werte, da der Import sie ändern kann und danach keine Neu-Definition sichtbar ist. Die Zieldresse des `blx` bleibt dynamisch/unbekannt, weil kein Wert aus `[sp+0x70]` vorliegt. Zielcode ab `0x3018` und Branchziele außerhalb des Fensters wurden nicht untersucht.

## REA-Lücke und Methode

**VERIFIZIERT:** Der vorangehende Same-Hash-Bericht WP-XE164-190/191 dokumentiert für das ELF `get_evidence_bundle` mit exaktem Hashfilter und null passende Retained Records. Diese identische Bundle-Abfrage wurde nicht wiederholt. `open_binary` gelang diesmal und bestätigte Eingabehash und ELF/ARM-Klassifikation.

Die ersten 28 punktgenauen REA-Instruktionsabfragen adressierten ELF-VA direkt als Ghidra-Adresse. Ghidra meldete `outside-memory` für diese Adressen. Die gezielte Mappingabfrage `address_to_file_offset(0x12fa8)` bestätigte Ghidra-Adresse `0x12fa8` → Dateioffset `0x2fa8` (Evidence `ev_7bf8eb4f8dbba17f9c04587b8f0d47db17be890a08055f1c78b952ac01ae70c9`). Danach wurden die 28 Instruktionen punktgenau bei `0x12fa8..0x13014` abgefragt; ihre Evidence-IDs stehen im Bundle. Die unverschobenen Fehlabfragen werden dokumentiert und nicht als Belege verwendet.

Lokaler, zielgebundener Fallback: GNU ARM objdump 2.44 mit `--start-address=0x2fa8 --stop-address=0x3018`; `readelf -Ws`/`-rW` nur für die hier referenzierten Imports; die vier Literalbytes bei `0x3364` wurden durch REA `read_bytes` belegt. Kein Lauf, keine Geräte-, VM- oder Netzwerkaktion. REA: `rea-agents 6.5.0`; Ghidra: `12.1.4`; Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

**Tests: PASS** — der lokale Validator prüft Eingabegröße/-hash, `.text`-Abdeckung, durchgehende Adressfolge, jedes 32-Bit-Instruktionswort und die referenzierten vier Literalbytes. Er ersetzt keine unabhängige semantische Prüfung. Statussprache im Bericht: `VERIFIZIERT`, `HYPOTHESE`, `OFFEN`; es wird kein Status als unabhängiger Review ausgegeben.

## Erzeugte Dateien

Nur in diesem Work-Package-Verzeichnis erzeugt:

| Datei | Zweck | SHA-256 |
|---|---|---|
| `report.md` | Befund, Instruktionsliste, Beleggrenzen | in `SHA256SUMS` aufgeführt |
| `validate.py` | Reproduzierbare ELF-/Wort-/Literalprüfung | `8f12457ad75e78300ade7e420d845bb562b15d17ad0fdc1476c414765fb31409` |
| `rea-evidence-bundle.json` | Vollständiger Same-Session-REA-Belegexport, 61 Records | `123d1616a928d51e4d7b5b1f185960a0019fffc9a1d76efc797c6cfe2252d01d` |
| `SHA256SUMS` | Hashmanifest der drei vorstehenden Artefakte | Manifesthash im finalen Handoff |
