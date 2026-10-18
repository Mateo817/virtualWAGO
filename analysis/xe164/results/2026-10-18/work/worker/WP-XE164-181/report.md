> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-181 — Positionsbezug der indirekten Calls

## Ergebnis

**Befundstatus: OFFEN. Teststatus: NOT_RUN.** Die drei Callziele lassen sich innerhalb des exakt betrachteten Funktionskörpers positionell an aufeinanderfolgende Loads aus einem Zeiger binden, der zuvor aus dem Feld bei Kontextbasis `+0x61c` gelesen wurde. Eine Herkunfts- oder Publikationskette für diesen Feldwert und damit die Identität der Tabelle ist nicht belegt.

Die beobachtete Reihenfolge ist:

| ELF-VA / Dateioffset | Ghidra-VA | Position gelesen | Indirekter Call | Ergebnis der Positionsprüfung |
|---|---|---|---|---|
| `0x64c8` | `0x164c8` | `+0x30` nach Load aus Kontextbasis `+0x61c` bei `0x64c0` | `0x64cc` (`blx r3`) | Positionell verifiziert |
| `0x6504` | `0x16504` | `+0x40` nach Load aus Kontextbasis `+0x61c` bei `0x64f8` | `0x6508` (`blx r3`) | Positionell verifiziert |
| `0x663c` | `0x1663c` | `+0x3c` nach Load aus Kontextbasis `+0x61c` bei `0x65cc` | `0x6648` (`blx sl`) | Positionell verifiziert |

Die 19 im `.text`-Disassembly gefundenen positiven unmittelbaren Loads mit Displacement `0x61c` sind sämtlich LDR-artige Lesezugriffe; in diesem Scan wurde kein entsprechender direkter Store gefunden. Das ist ein begrenzter Befund zum materialisierten `.text`-Code dieses ELF, kein Nachweis über indirekte Writes, fremde Module oder Laufzeitänderungen. Gleiche numerische Offsets begründen weder gleiche Feldbedeutung noch eine ADI-Tabellenidentität.

## Adressräume und exakte Reichweite

Artefakt `libIoDrvKbus.so.0.0.1`, ELF32 little-endian ARM, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`.

| Begriff | Beobachtung |
|---|---|
| Symbolbereich | `readelf -Ws`: Dynsym-Eintrag `idk_IoDrvWriteOutputs`, ELF-VA `0x64a8`, Größe `436` (`0x1b4`), Symbolende exklusiv `0x665c`. |
| Hier benötigter Instruktionskörper | WP083-Ghidra FunctionManager-Bereich `[0x164a8,0x16658)` in Ghidra-Adresse. Entspricht ELF-VA `[0x64a8,0x6658)` und Dateioffsetbereich `[0x64a8,0x6658)`. Das angehängte Wort bei ELF-VA/Dateioffset `0x6658` liegt außerhalb dieses Instruktionsbereichs. |
| Abbildung | Erster `PT_LOAD` hat Offset und VirtAddr `0`; daher fallen ELF-VA und Dateioffset in diesem Bereich numerisch zusammen. WP083 beobachtet für die Ghidra-Ansicht die Verschiebung `+0x10000`; Ghidra-Adressen sind keine Laufzeitadressen. |
| Laufzeitadressen | OFFEN; keine Laufzeitmessung oder Relokationsanalyse. |

Im Funktionskörper lädt `0x64b0` das erste Wort des ersten Arguments nach `r7`. Danach lesen `0x64c0`, `0x64f8` und `0x65cc` jeweils ein Wort von `[r7,#0x61c]`. Für jeden der drei Calls wird das geladene Wort als Basis für genau den beobachteten Positionsload verwendet, der unmittelbar vor dem passenden indirekten Branch steht. Die einzelnen Instruktionsbindungen stehen vollständig in `position-chain.tsv`.

## Beobachtungen und Abgrenzung

- **VERIFIZIERT** — Im WP083-Evidence-Record (`ev_6194ece0a7a14aec68e5779961be70c5f415e05d5ad28a9fdb09d461539ae983`) sind Funktion, Instruktionen, Ghidra-Adresse, Bodybereich und Artefaktidentität dokumentiert. Der Evidence-Record wurde in REA importiert und als Quelle der Instruktionsbelege wiederverwendet.
- **VERIFIZIERT** — Die punktuelle GNU-Objdump-Suche über `.text` findet 19 Instruktionen mit unmittelbarem `[Register,#0x61c]`; jede ist ein Load. Exakte Adressen und Instruktionen stehen in `reference-inventory.tsv`. Für alle anderen Funktionen belegt das Vorkommen desselben Displacements keine gemeinsame Kontextstruktur.
- **VERIFIZIERT** — Die Tabelle enthält die gefundenen nicht-PC-basierten Speicheroperand-Verwendungen mit den numerischen Displacements `0x30`, `0x3c`, `0x40` in der `.text`-Ausgabe. Andere Basen sind als ungebunden oder Stack-relativ markiert. PC-relative Literalloads sind aus dieser Positionsinventur ausgeschlossen, weil deren Basis PC statt eines aus Kontext `+0x61c` geladenen Zeigers ist; sie belegen keine der hier geprüften Tabellenpositionen.
- **OFFEN** — Woher der von `[r7,#0x61c]` gelesene Zeiger stammt, wer ihn kopiert oder publiziert und ob die drei Positionswerte Teil einer bestimmten gemeinsamen Tabelle sind.
- **OFFEN** — Ob andere Dateien/Module, externe Aufrufer oder indirekte Speicheroperationen den Wert bei `+0x61c` setzen oder ändern.
- **OFFEN** — Semantik, Benennung und Rückgabevertrag der indirekten Ziele. Dieser Bericht vergibt keine API-/Slotnamen oder Rückgabesemantik.

Alternative Erklärung: Die übereinstimmenden Zahlen `0x61c`, `0x30`, `0x3c` und `0x40` könnten in anderem Code andere Felder oder Speicherbereiche bezeichnen. Innerhalb der Zielroutine ist die Load-zu-Call-Positionierung direkt belegt; die Tabelle als Ganzes und ihr Publikationsursprung bleiben unidentifiziert.

## Methode, Coverage und Toolstand

Offline. Eingaben wurden zuerst per SHA-256 und Bytezahl geprüft. WP083-Evidence wurde per REA `import_evidence_bundle` übernommen; die zusammenhängende Instruktionsdarstellung wurde über `inspect_analysis_view` aus dem retained Evidence projiziert. Die REA-Funktionsevidence deckt 108 von 108 Instruktionen im dokumentierten Ghidra-Körper ab. Für eine globale Census der unmittelbaren Offsets bietet dieser importierte Funktionsrecord keine ELF-weiten Xrefs; dies wurde als einmalige, dokumentierte Coverage-Lücke mit GNU ARM Objdump geschlossen. Es wurde kein Ghidra-Importpfad erneut ausgeführt.

Verwendete Versionen: Ghidra `12.1.4` (WP083-Profil, Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`); GNU ARM objdump `2.44`; GNU readelf `2.44`; Python `3.13.5`; ripgrep `15.2.0`. Keine Netzwerk-, Runtime-, VM-, Geräte- oder Hardwareaktion; keine Repositoryänderungen.

## Validator und Dateien

Der lokale Validator prüft alle vier Inputpins erneut, symbolische und Body-Ranges, die zehn erforderlichen Kettenstationen, die erwartete ELF-weite Referenzzahl samt zulässigen Kategorien/Status, sowie alle Datei-Hashes im Manifest. Validator: **PASS**. `sha256sum -c SHA256SUMS`: **PASS**. Eigene Prüfung ist Self-Review; es gab keinen unabhängigen Review oder Worker-Lauf.

Dateien: `assignment.md`, `report.md`, `reference-inventory.tsv`, `position-chain.tsv`, `validate.py`, `SHA256SUMS`. Teststatus bleibt **NOT_RUN** für ELF-Verhalten; Validatorstatus wird erst durch tatsächlichen Lauf verifiziert.
