> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-133 — Rohwort bei `codesys3` `.rodata` `0x003A3640`

## Befund

**VERIFIZIERT (Rohdaten/Adressbindung):** Das 64-Byte-Fenster `0x003A3620..0x003A365F` enthält vier direkt aufeinanderfolgende 16-Byte-Blöcke mit jeweils vier little-endian 32-Bit-Wörtern. `0x002FE12C` steht als erstes Wort des dritten Blocks bei VMA `0x003A3640` (Dateioffset `0x393640`). Die übrigen Wörter sind ausschließlich als rohe Nachbarwerte erfasst; aus dem Muster wird kein Recordtyp oder Feldvertrag abgeleitet.

| ELF VMA | Dateioffset | Rohbytes (little-endian) | `u32le` |
|---:|---:|---|---:|
| `0x003A3620` | `0x393620` | `00 c3 2f 00` | `0x002FC300` |
| `0x003A3624` | `0x393624` | `48 4f 3a 00` | `0x003A4F48` |
| `0x003A3628` | `0x393628` | `00 00 00 00` | `0x00000000` |
| `0x003A362C` | `0x39362C` | `00 00 00 00` | `0x00000000` |
| `0x003A3630` | `0x393630` | `20 dd 2f 00` | `0x002FDD20` |
| `0x003A3634` | `0x393634` | `5c 4f 3a 00` | `0x003A4F5C` |
| `0x003A3638` | `0x393638` | `00 00 00 00` | `0x00000000` |
| `0x003A363C` | `0x39363C` | `00 00 00 00` | `0x00000000` |
| `0x003A3640` | `0x393640` | `2c e1 2f 00` | `0x002FE12C` |
| `0x003A3644` | `0x393644` | `68 4f 3a 00` | `0x003A4F68` |
| `0x003A3648` | `0x393648` | `00 00 00 00` | `0x00000000` |
| `0x003A364C` | `0x39364C` | `00 00 00 00` | `0x00000000` |
| `0x003A3650` | `0x393650` | `58 e1 2f 00` | `0x002FE158` |
| `0x003A3654` | `0x393654` | `74 4f 3a 00` | `0x003A4F74` |
| `0x003A3658` | `0x393658` | `00 00 00 00` | `0x00000000` |
| `0x003A365C` | `0x39365C` | `00 00 00 00` | `0x00000000` |

**VERIFIZIERT (Abschnitt/LOAD):** `readelf` meldet `.rodata` als `PROGBITS`, VMA `0x00344FC8`, Dateioffset `0x334FC8`, Größe `0x06B36C`, alloc-only. Der Treffer liegt darin. Der ihn abdeckende erste `PT_LOAD` hat Offset `0`, VMA `0x00010000`, Dateigröße `0x003A0340`, Flags `R E`; deshalb gilt hier `VMA = Dateioffset + 0x10000`, also `0x003A3640 = 0x00393640 + 0x10000`. Die zweite `PT_LOAD` beginnt erst bei Offset `0x3A0EC4` / VMA `0x003C0EC4` und ist nicht der Treffer.

**VERIFIZIERT, methodenbegrenzt (direkte Xrefs):** REA/Ghidra 12.1.4 `xrefs` für exakt `0x003A3640` lieferte eine leere Referenzliste (`ev_156084ea0d4552053ec80a56208e20d215ff69a7c717a960e8195de3ff0ea04e`). Es wurde damit kein direkter statischer Verbraucher/Xref an dieser Zieladresse materialisiert. `relationship_coverage` war `null`; das Ergebnis ist daher auf diese Providerabfrage und deren modellierte Referenzen begrenzt. Als eng begrenzte Gegenprobe gab Rizin 0.9.1 `axt @ 0x3a3640` ohne Ausgabe zurück (ohne vorgeschaltete globale Analyse). Auch diese Nullbeobachtung beweist nicht die Abwesenheit indirekter, berechneter oder zur Laufzeit gebildeter Zugriffe. Es gibt keine belegte Consumer-Lane, die für diesen Rohort berichtet werden kann.

## Alternative und Restunsicherheit

Das wiederholte 16-Byte-Rohmuster kann auf tabellarisch angeordnete Einträge hindeuten; das bleibt **HYPOTHESE**, keine verifizierte Recordgrenze oder Semantik. Die Wörter könnten Metadaten oder ungenutzte Werte sein, und ein Verbraucher könnte auf anderem Weg (z. B. über berechnete Adressen oder einen Bereichsscan) zugreifen. Name, Zahlenwert und positionsähnliche Nachbarwerte sind kein API-, Pointer- oder ABI-Vertrag. Keine Runtime- oder Hardwareaussage wird getroffen.

## Methode und Evidenz

- Ziel: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`; Größe `5,181,396` Byte; SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` (bestätigt).
- REA `open_binary`: ELF, ARM; Provider Ghidra `12.1.4`, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- REA `read_bytes(0x003A3620, 64)`: vollständig, 64/64 Byte; Evidence `ev_dde35e9a0ee633e45f1c1a0ca2e3efedd0a0f67fffcf2c9433073dd8cae27ad5`. Das gelesene Initial-Memory-Fenster stimmt byteweise mit dem unten genannten Dateifenster überein.
- REA `xrefs(0x003A3640)`: leere Liste; Evidence `ev_156084ea0d4552053ec80a56208e20d215ff69a7c717a960e8195de3ff0ea04e`.
- REA `inspect_binary_layout` war wegen nicht konfiguriertem `REA_PWNTOOLS_PYTHON` nicht verfügbar (`BLOCKED`); deshalb einmaliger fokussierter lokaler Fallback: GNU `readelf` aus GNU Binutils `2.44`, `od` (rohe Dateibytes) und Rizin `0.9.1` (`axt` exakt an Zieladresse). Rizin lieferte ohne globale Analyse keine Ausgabe. Kein identischer fehlgeschlagener Toolaufruf wurde wiederholt.
- Vorangegangene WP129-Referenz: `report.md` SHA-256 `e7b87195cf01718c18792ec83cbe14c306e8f88706d3229a1db02741bd59cc72`; `xrefs.tsv` SHA-256 `56ffd42f7dfa2fbcebde2a43a064423c90603874f770d43902a3414d18c22724`.

| Prüfschritt | Status |
|---|---|
| Zielgröße und SHA-256 gegen Vorgabe | PASS |
| REA-Fenster vollständig 64/64 Byte | PASS |
| REA-Fenster mit rohen Dateibytes abgeglichen | PASS |
| `.rodata`-VMA/Dateioffset und `PT_LOAD`-Abbildung per `readelf` | PASS |
| Exakte REA-Xref-Abfrage auf `0x003A3640` | PASS (keine Referenz geliefert; provider-/methodenbegrenzt) |
| Begrenzte Rizin-`axt`-Gegenprobe | PASS (ohne globale Analyse; keine Ausgabe) |
| Direkte Consumer-Lane | NOT_RUN (kein Xref materialisiert; keine weitergehende Verbraucherbehauptung) |
| Runtime, VM, Netzwerk, Geräte, Hardware | NOT_RUN |
| Unabhängiger Review | NOT_RUN |
| Self-Review | PASS |

Der ausführbare [Validator](./validate.sh) prüft Eingabeidentität, Dateimenge und die in [SHA256SUMS](./SHA256SUMS) geführten Ausgabe-Hashes.
