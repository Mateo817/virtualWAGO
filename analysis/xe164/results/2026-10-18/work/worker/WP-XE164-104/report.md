> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-104 — caller/Xrefs und Argumentquellen

## Ergebnis

**VERIFIZIERT:** Im von Ghidra erkannten Referenzbestand gibt es keinen aufgelösten Call direkt auf die Implementierung bei Ghidra-Adresse `0x155d0` (ELF-File-Offset `0x55d0`). Der statische Weg ist ein direkter Call von `FUN_0001277c` bei `0x12c1c` (File-Offset `0x2c1c`) auf den 12-Byte-Thunk `0x11e3c` (File-Offset `0x1e3c`); dessen Instruktion `0x11e44` (File-Offset `0x1e44`) ist ein von Ghidra auf `0x155d0` aufgelöster `COMPUTED_JUMP`. Der zweite Xref auf `0x155d0`, Quelle `0x29080` (File-Offset `0x9080`), ist eine `READ`/`DATA`-Referenz, kein Call.

Die drei beim Call an den Thunk beobachtbaren ARM-Argumente sind:

| Register am Call | Unmittelbare Definition | Beobachtete Herkunft und Gates |
|---|---|---|
| `r0` | `0x12c18: cpy r0,r10` | `r10` kommt aus `[r3+0x61c]`; davor lädt `r3` den bei `0x12794` gesicherten ersten Eingabewert. Der Pfad prüft diesen Eingabewert auf null und den geladenen Wert bei `0x12a58` ebenfalls auf null. |
| `r1` | bei `0x12bf8: cpy r1,r0` gesichert | `r0` ist der Rückgabewert des indirekten Calls bei `0x12bf0`, dessen unmittelbar davor gesetzte Eingaben `r0=r8` und `r1=sp+0x44` sind. Der Wert bei `[sp+0x44]` muss null sein; zusätzlich prüft der anschließende `clz/lsr`-Pfad den Rückgabepointer auf null, bevor `r1` benutzt wird. |
| `r2` | `0x12c14: uxtb r2,r6` | Niedriges Byte von `r6`. Bei Eingabewert 3 gleich 1 stammt `r6` aus dem Rückgabewert eines direkten Calls an `0x11d34` mit `r0=r4`. Im anderen Zweig wird `r6` aus dem Rückgabewert eines indirekten Calls gewonnen, nachdem ein über `r4` geholter Eintrag ungleich null und sein 16-Bit-Wert bei Offset `+8` gleich 2 ist; Status- und Bereichstests folgen. Für den gemeinsamen Callpfad muss `r6` signed nichtnegativ sein. |

Für den betrachteten Eintrag gelten unmittelbar vor der Argumentvorbereitung außerdem diese Guards: `[r8] == 10` (`0x12b40–0x12b48)); `r6 >= 0` (`0x12b4c–0x12b50)); der 16-Bit-Wert bei `[r8+8]` muss `0x10` sein (`0x12bd4–0x12bd8)); der indirekte Abruf muss Status null und einen nicht-null Rückgabepointer liefern (`0x12bf0–0x12c10)). Danach werden `r2`, `r0` gesetzt und der Call ausgeführt.

**OFFEN:** Im erlaubten Caller-Körper ist der aus dem indirekten Abruf kommende Wert nur als Pointer beobachtbar. Der Caller prüft Status und Nicht-Nullheit, aber keine Länge. Dass dieser Pointer auf einen exakt 16 Byte langen Vergleichsstring zeigt, ist in diesem Work-Package daher nicht verifiziert.

## Statische Caller-/Xref-Vollständigkeit

Die REA-Abfrage `xrefs(0x155d0)` listet exakt `0x11e44` und `0x29080`. Die Instruktionsreferenz bei `0x11e44` klassifiziert diese getrennt als `COMPUTED_JUMP` beziehungsweise `READ`/`DATA`. `procedure_callers(0x155d0)` liefert keine aufgelösten Call-Referenzen; `procedure_callers(0x11e3c)` liefert genau `0x1277c`. Der Ghidra-Funktionskörper von `FUN_0001277c` ist der kleinste umschließende Körper: einschließlich `0x1277c–0x12e7f`, 1,796 Bytes (File-Offsets `0x277c–0x2e7f)); er enthält Callsite `0x12c1c`.

**Vollständigkeitsstatus — VERIFIZIERT, begrenzte Domäne:** Dies ist die vollständige Liste der von Ghidras ReferenceManager in diesem Artefakt materialisierten exakten Referenzen und der aufgelösten Callers. **OFFEN:** REA weist darauf hin, dass ungelöste berechnete/indirekte Flüsse nicht als Caller-Kanten erscheinen; die Liste beweist deshalb keine globale Vollständigkeit über solche Flüsse oder Laufzeitverhalten. Der Xref-Endpunkt allein typisiert Referenzen nicht; die Trennung oben stammt aus der Instruktionsreferenz bei `0x11e44`.

## Identität, Adressbindung und Werkzeuge

- Artefakt: `libIoDrvKbus.so.0.0.1`, 38,584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`.
- Adressraum: Ghidra/ELF-Speicheradressen sind getrennt von ELF-File-Offsets ausgewiesen. Für die relevanten Adressen hat REA `address_to_file_offset` verwendet (Ghidra-Quelle-Mapping; nicht nur Subtraktion einer Basis).
- Stützstellen: Implementierungs-Xrefs Evidence `ev_93eebe5f5afb8f607eb07a8619879661f71c24079f84db9b8536207add5f0c20`; Thunk-Xref Evidence `ev_f250d4e3570c71df106790fc204a18ed23c81638b97ec0e88975b158f71c1cbe`; Thunk-Instruktion `ev_b4a1428ebeb6db00940b32c96b5b9863d5e8e833ac2d1fbbf4a810e32f80739e`; Caller-Instruktionen `ev_a681781f43af758110dd35b449702f688ff40799221038d0160aac1009816c49`; Caller-Assembly `ev_b128516631bac6180eb6fd8c38476da5475dd67bbcac66d505ea5b24d6a6d07d`; Call-Instruktion `ev_930c845932bf291bf5211a86594226570887e2d8a71e99e8a301a9dabf170397`.
- REA CLI `rea-agents 6.5.0`; Provider Ghidra `12.1.4`; Architektur `ARM:LE:32:v8`; Analysis-Profile-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- REA war die erste Methode. Es gab in den zulässigen Caller-Daten keine Lücke, die GNU-ARM-Disassembly als Fallback erforderte; kein Fallback verwendet.
- Kanonisches Bundle: `rea-bundle.json` (REA-Export plus `rea evidence-export`-Validierung), 34 Evidence-Datensätze. Es enthält keine `analyze_function`-Dossiers.

## Alternative Erklärung und Restunsicherheit

Die Referenz auf `0x29080` kann eine gelesene Pointer-/Tabellenzelle sein, deren Rolle über den statischen Namen und den `READ`-Verweis hinaus hier nicht semantisch festgelegt wird. Sie ist laut ReferenceManager kein Call. Ebenso bleibt der Rückgabewert des indirekten Abrufs semantisch unbenannt: die Caller-Belege zeigen einen nicht-null Pointer, aber weder Inhalt noch Zeichenkodierung oder Länge. Die genaue Laufzeitauflösung indirekter Ziele und alle nicht materialisierten Flüsse bleiben unbekannt.

## Tests

| Prüfung | Status | Ergebnis |
|---|---|---|
| Target-Hash und -Größe | PASS | Stimmen mit Eingabe überein. |
| Kanonischer REA-Bundle-Export/Validierung | PASS | 34 Datensätze, Ghidra 12.1.4, Zielhash stimmt. |
| Semantischer Validator | PASS | Prüft Xref-/Caller-Klassifikation, unmittelbare Argumentdefinitionen und Guards, Adress-/Fileoffset-Paare sowie Ausschluss eines Funktionsdossiers. |
| GNU-ARM-Fallback | NOT_RUN | Nicht benötigt. |

## Erzeugte Dateien und SHA-256

- `rea-bundle.json` — siehe Hashmanifest `SHA256SUMS`.
- `validate_semantics.mjs` — siehe Hashmanifest `SHA256SUMS`.
- `audit-tool-behavior.md` — siehe Hashmanifest `SHA256SUMS`.
- Dieser Bericht — sein SHA-256 steht ebenfalls in `SHA256SUMS`.
