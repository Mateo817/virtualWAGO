> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-105 — `FUN_00015564`

## Befund

**VERIFIZIERT:** Im untersuchten ARM-ELF hat `FUN_00015564` den durch Ghidra erkannten zusammenhängenden Körper `0x15564..0x155cf` (108 Bytes, inklusive Endadresse). Ghidra ordnet Adresse `0x15564` dem Datei-Offset `0x5564` zu. Die Adresse und der Dateioffset sind verschiedene Koordinaten; die Zuordnung stammt aus `address_to_file_offset`, nicht aus angenommener Basisaddition.

Der beobachtete Wertvertrag für einen über `r0` übergebenen Startzeiger ist:

1. Der Helper initialisiert den Akkumulator auf 0 und liest genau vier aufeinanderfolgende Bytes, `p[0]` bis `p[3]`. Die Schleifengrenze ist `p + 3`; es gibt in diesem Körper keine Längen- oder NUL-Prüfung.
2. Für jedes Byte wird der von `__ctype_b_loc()` gelieferte Tabellenwert betrachtet. Ist `flags & 0x1000 == 0`, endet der Helper sofort mit `-1` (`0xffffffff` in `r0`).
3. Andernfalls ist der Ziffernbeitrag entweder `byte - 0x30`, wenn `flags & 0x400 == 0`, oder `toupper(byte) - 0x37`, wenn `flags & 0x400 != 0`. Der zweite Pfad ruft `__ctype_toupper_loc()` auf.
4. Nach jedem gültigen Byte wird `acc = acc * 16 + contribution` berechnet; nach dem vierten Byte wird der Akkumulator zurückgegeben.

Damit ist die maschinennahe Regel präzise durch die beiden Tabellenmasken beschrieben. **HYPOTHESE, eng begrenzt:** Bei den üblichen GNU-`ctype`-Tabellen markieren `0x1000` und `0x400` Hexziffern bzw. alphabetische Zeichen. Dann kodieren ASCII-`0`–`9`, `A`–`F` und `a`–`f` jeweils den 16-Bit-Wert `0..65535`; Groß-/Kleinschreibung ist für `a`–`f` äquivalent. Die vierstellige Akkumulation kann bei diesem Zeichensatz nicht überlaufen. Die zugrunde liegenden Tabellen-/Locale-Inhalte zur Laufzeit wurden nicht geprüft; deshalb ist die Tabellenmasken-Regel der primäre exakte Vertrag.

Der Fehlerwert `-1` kollidiert nicht mit einem regulären vierstelligen Hexwert (`0..0xffff`). Ein ungültiges Byte wird an seiner ersten Position erkannt; ein darüber hinausgehender Fehlercode oder die Fehlerposition wird nicht geliefert. Der Code prüft nicht, ob `p` auf vier lesbare Bytes zeigt. Verhalten bei ungültigem Zeiger, nicht lesbarem Speicher oder zur Laufzeit abweichenden `ctype`-Tabellen ist durch diese statische Analyse nicht bestimmt.

## Fundstellen und Evidence

Quelle: ELF mit 38.584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`.
Toolversionen: REA CLI `6.5.0`; Ghidra `12.1.4`.

- `ev_028d313ef6f4f122f8ad41a78e5a9375753990e9241c34536d202df7cb537817` — `analyze_function`, Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; enthält Funktion, Pseudocode, Listing, Kontrollfluss, Helpernamen und die vier begrenzten direkten Call-Referenzen.
- `ev_f574f90baf1924891eedc75369c97f82dfddf1f8ad9ddedd80529469d3f08b12` — fokussiertes Ghidra-Listing für `0x15564`.
- `ev_1756a3a72248a984de471a3a0ee752aaf79845b067ab98aece8f236cfedac4ff` — Adresszuordnung `0x15564` → Datei-Offset 21860 dezimal (`0x5564`).

Entscheidende Listing-Stellen (Ghidra-Adressen):

- `0x1556c`: direkter Call zu `0x11e00`, von Ghidra als Thunk für `<EXTERNAL>::__ctype_b_loc` benannt.
- `0x15580`, `0x1558c`, `0x15590`, `0x15594`: Byte-Lese-/Tabellenzugriff, Test der Maske `0x1000` und Verzweigung zum Fehlerpfad `0x155c8`.
- `0x15598`, `0x155a0`, `0x155a4`: Test der Maske `0x400`, direkte Byte-Subtraktion `0x30` oder Zweig zum Tabellenpfad.
- `0x155a8`: direkter Call zu `0x11cec`, von Ghidra als Thunk für `<EXTERNAL>::__ctype_toupper_loc` benannt; `0x155b0..0x155b4` wendet den Tabellenwert minus `0x37` an.
- `0x155bc`: Akkumulatorbeitrag plus vorheriger Wert mal `0x10`; `0x155c0` wiederholt bis zum vierten Byte.
- `0x155c4`: Rückgabe des berechneten Werts; `0x155c8..0x155cc`: Rückgabe von `-1`.

`normalized_result`/Pseudocode und Listing sind Ghidra-Werkzeugbeobachtungen, kein Originalquelltext und kein Laufzeitnachweis. Keine GNU-ARM-Fallbackanalyse war nötig: REA lieferte Körper, Listing und beide unmittelbar aufgerufenen Helpernamen.

Der Dossier-Export nennt als direkte Referenzquellen zu `FUN_00015564` genau die vom Auftrag begrenzten Adressen `0x15640`, `0x15664`, `0x15674`, `0x15684` innerhalb des als `idk_Valid_ModuleCmpValue` benannten Callers. Der Caller-Körper wurde nicht erneut geprüft; aus den Referenzadressen allein werden keine zusätzlichen Aussagen über die dort übergebenen Werte abgeleitet.

## Alternativerklärung und Restunsicherheit

Eine rein wörtliche Interpretation der Instruktionen lässt die Bedeutung der `ctype`-Bitmasken offen. Die Decompiler-Darstellung benennt die beiden Tabellenzugriffe, aber nicht die konkrete Tabellenbelegung der späteren Runtime/Locale. Deshalb ist die stärkere Aussage „nur ASCII-Hexzeichen, Werte 0–65535“ als GNU-`ctype`-nahe Interpretation markiert; verifiziert ist die obige masken- und arithmetikgenaue Regel. Nicht analysiert wurden die Implementierungen der beiden externen Helper, der Caller-Körper, Runtime/Locale und tatsächlich ausgeführte Eingaben.

## Status und Prüfungen

- Zulässige Statusvokabulare: Befunde `VERIFIZIERT | HYPOTHESE | OFFEN | BLOCKED`; Tests `PASS | FAIL | NOT_RUN | BLOCKED`.
- Befundstatus: `VERIFIZIERT` für Körpergrenzen, vier Bytezugriffe, Maskentests, Rechenregel, Rückgabepfade, zwei direkte Helpernamen und die explizit vorgegebenen vier Call-Referenzen.
- Befundstatus: `HYPOTHESE` nur für die GNU-`ctype`-Interpretation der Masken und daraus abgeleitete ASCII-Hexnotation.
- Tests: `PASS` — eigener semantischer Validator prüft Artefaktidentität, kanonisches REA-Bundle, Evidence-IDs, Funktionsgrenzen, Listing-Anker, Masken-/Rechenpfade, Helpernamen, Callsite-Allowlist, Adress-/Offsetzuordnung und Statusvokabular.
- Tests: `PASS` — REA-Validator `rea inspect-evidence-bundle` erkennt den exportierten Bundleinhalt und seine Records.
- Tests: `NOT_RUN` — keine Ausführung des Helpers, kein Emulator und kein Runtime-/Gerätezugriff.
