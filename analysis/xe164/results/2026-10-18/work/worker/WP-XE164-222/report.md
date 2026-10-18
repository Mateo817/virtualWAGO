> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-222 — file-backed references to two libdal entries

## Ergebnis

**VERIFIZIERT** — Für das Artefakt `FW31-LIBDAL-1.0.1` (18,076 Bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`) lieferte Ghidra je ein direktes Xref auf die exakten Ziele ELF `0x1bec` / Ghidra `0x11bec` und ELF `0x1dc0` / Ghidra `0x11dc0`. Beide Xref-Quellen sind materialisierte 32-Bit-Werte in `.data`, keine dort dekodierbaren Kontrollflussinstruktionen. Der unabhängige, vollständige A32-`B`/`BL`-Opcode-Scan aller file-backed `SHF_EXECINSTR`-Sektionen fand **keine** direkte Branchinstruktion auf eines der beiden Ziele.

Damit ist die vollständige Menge der Ghidra-Xrefs je Ziel ein Element; die vollständige, methodengebundene Menge direkter A32-`B`/`BL`-Sites im gescannten Codebereich ist leer. Das sagt nichts über indirekte Aufrufe, computed control flow oder Laufzeitverhalten aus.

## Getrennte Inventare

| ELF-Ziel | Ghidra-Ziel | Direkte Ghidra-Xrefs (Quelladresse) | ELF-Quelle / Datei-Offset | Site-Klassifikation |
|---|---|---|---|---|
| `0x1bec` | `0x11bec` | `0x24154` | VMA `0x14154`, Offset `0x4154` | `.data`, gespeicherter Wert `0x00001bec`; Ghidra-Instruktionsprüfung meldet `data` |
| `0x1dc0` | `0x11dc0` | `0x24158` | VMA `0x14158`, Offset `0x4158` | `.data`, gespeicherter Wert `0x00001dc0`; Ghidra-Instruktionsprüfung meldet `data` |

Ghidras Xref-Projektion gibt keine Referenztypen aus. Die getrennte Prüfung der exakten Xref-Quelladressen ergibt `status=data`, jeweils ohne Mnemonic, Instruktionsbytes oder Control-Flow-Ziel. Die kleinen ausführbaren ELF-Sektionen sind `.init` (VMA/Offset `0x1334`, Größe `0x0c`), `.plt` (`0x1340`, `0x1340`, `0x374`), `.text` (`0x16b4`, `0x16b4`, `0x25cc`) und `.fini` (`0x3c80`, `0x3c80`, `0x08`). Der Validator prüft die `SHF_EXECINSTR`-Flags selbst aus der ELF-Sektionstabelle und überspringt `SHT_NOBITS`.

### Xref-Quellfenster

Die Fenster sind jeweils exakt `[site-8, site+12)` in Ghidra-Adressierung; der Dateioffset ist identisch mit ELF-VMA minus dem für dieses ELF beobachteten Ghidra-Load-Bias `0x10000`.

| Ziel | Ghidra-Fenster | ELF-VMA-Fenster | Datei-Offset-Fenster | Rohbytes (aufsteigende Adresse) | 32-Bit-Wörter an den relevanten Xref-Quellen |
|---|---|---|---|---|---|
| `0x11bec` | `[0x2414c,0x24160)` | `[0x1414c,0x14160)` | `[0x414c,0x4160)` | `30 51 02 00 50 41 02 00 ec 1b 01 00 c0 1d 01 00 a4 1f 01 00` | Site `0x24154` / Offset `0x4154`: raw word `0x00001bec` (Little-Endian Bytes `ec 1b 01 00`) |
| `0x11dc0` | `[0x24150,0x24164)` | `[0x14150,0x14164)` | `[0x4150,0x4164)` | `50 41 02 00 ec 1b 01 00 c0 1d 01 00 a4 1f 01 00 bc 32 01 00` | Site `0x24158` / Offset `0x4158`: raw word `0x00001dc0` (Little-Endian Bytes `c0 1d 01 00`) |

### Direkte A32-Branch-Sites

| ELF-Ziel | Ghidra-Ziel | Sites aus `SHF_EXECINSTR`-Opcode-Scan | Site-Fenster / Rohwort |
|---|---|---|---|
| `0x1bec` | `0x11bec` | keine | kein Treffer, daher kein Site-Fenster |
| `0x1dc0` | `0x11dc0` | keine | kein Treffer, daher kein Site-Fenster |

Der Scan betrachtet aligned 32-Bit-Wörter in jedem file-backed ausführbaren ELF32-LE-ARM-Abschnitt. Er akzeptiert A32-Encoding `cond:101:L:imm24`, schließt `cond=0xf` (BLX immediate) aus, berechnet das Ziel als `site + 8 + SignExtend(imm24 << 2)` und vergleicht exakt mit `0x1bec` und `0x1dc0`. Direkte `B`- und `BL`-Treffer: null.

## Adressbindung und begrenzte Entry-Bytes

Die Zielbindung folgt den beobachteten ELF-Sektionen und Ghidra-Xrefs: `.text` hat ELF VMA/Datei-Offset-Identität; die Ghidra-Zieladressen liegen für beide Ziele bei ELF-VMA `+0x10000`. Die Xref-Quellen bei Ghidra `0x24154`/`0x24158` binden entsprechend an `.data` ELF `0x14154`/`0x14158` und Datei-Offsets `0x4154`/`0x4158`. Die am Entry gelesenen vier Bytes lauten bei Ghidra `0x11bec`: `f0 47 2d e9` (A32-Wort `0xe92d47f0`), sowie bei `0x11dc0`: `dc 30 9f e5` (A32-Wort `0xe59f30dc`). Hier endet die Entry-Instruktionsbindung; nachfolgende Entry-Body-Instruktionen wurden nicht ausgewertet.

## Methode und Nachweise

- **REA zuerst:** `open_binary` band das unveränderte Artefakt (SHA-256 wie oben), Format ELF, Architektur ARM. `xrefs(0x11bec)` ergab exakt `[0x24154]`; `xrefs(0x11dc0)` ergab exakt `[0x24158]`. Ghidra `12.1.4`, Analysis-Profile-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Ghidra-Evidence: Xrefs `0x11bec`: `ev_cf32e5f52d35be46b4af7d6d2898d716d12dc0739505737f311f3f21f11e2002`; `0x11dc0`: `ev_21b82c980663325f7a51bdfb2025e89b0b52317faf26d6732d470b1c1c3695c6`. Quelladressen geprüft mit `inspect_native_instruction`: `0x24154` (`ev_90bbfdf96c484c9aa475c0d81fc10fadcbcc77099073cdfea9a976da1b798cf5`) und `0x24158` (`ev_70f6ee327f2798492a6f3355dfe9cb6bbeb98dc3c4a0a1686e980b273490d733`), jeweils `status=data`.
- Entry-Instruktionsbytes: `read_bytes(0x11bec,4)`, Evidence `ev_b02352cc630d2975ae44eb5472a79607b68b04beb1453bc5f2b3b299d6104b61`; `read_bytes(0x11dc0,4)`, Evidence `ev_2afca4b03ba2d34c1335a5f51377073a6e068aac6851d25d39740a0a4181e411`.
- **Beobachtete REA-Lücke:** Die direkte Xref-Liste projiziert Referenzadressen ohne Referenzart, und die Xref-Quelladressen sind Daten statt Instruktionen. Sie beantwortet daher nicht die verlangte unabhängige code-seitige Branch-Vollständigkeit. Daraufhin begrenzter lokaler Fallback: GNU `readelf` 2.44 zur Sektionstabelle, GNU ARM objdump `arm-linux-gnueabihf-objdump` 2.44 zu Formaterkennung/Disassemblierung sowie der unten bereitgestellte ELF-Rohwort-Validator unter Python 3.13.5. Netzwerk, Geräte und VM wurden nicht verwendet.

## Validator und Status

Reproduzierbarer Befehl:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Der Validator erzwingt SHA-256, ELF32 little-endian und `EM_ARM`, liest alle file-backed `SHF_EXECINSTR`-Sektionen direkt aus der ELF-Tabelle, protokolliert ihre Grenzen und listet Treffer mit Datei-Offset, Rohwort, berechnetem ELF-Ziel sowie exakt `[site-8,site+12)`-Fenster. Ergebnis: erwartete ausführbare Sektionen `.init`, `.plt`, `.text`, `.fini`, keine Branch-Treffer.

**PASS** — Validator auf dem gebundenen Artefakt gelaufen; Hash und ELF-Merkmale stimmen, Branch-Trefferzahl `0`. Dies ist ein Self-Check, keine unabhängige Prüfung.

## Alternativerklärung und Restunsicherheit

**HYPOTHESE** — Die zwei `.data`-Einträge können eine Funktionszeiger-/Dispatch-Tabelle oder eine andere Tabelle mit Adresswerten sein. Ihre Lage und die direkt passenden Wörter zeigen materialisierte Adressreferenzen, belegen aber nicht, ob oder wann Verbraucher diese Werte laden oder als Kontrollflussziel verwenden. Die Bezeichnung „direktes Xref“ ist hier Ghidras Referenzprojektion und keine Aussage, dass die Speicherzelle selbst Kontrollfluss ausführt.

**OFFEN** — Nicht abgedeckt sind indirekte/computed Aufrufe, Laufzeitverhalten, nicht file-backed Code, Code außerhalb `SHF_EXECINSTR`, andere ARM-Modi bzw. Thumb-Encoding, Relokationsverhalten zur Laufzeit sowie Funktions- oder Lifecycle-Semantik. Der negative Befund ist auf Ghidras Xrefs zur exakten Zieladresse und den dokumentierten A32-Rohwort-Scan des genannten unveränderten Artefakts beschränkt.
