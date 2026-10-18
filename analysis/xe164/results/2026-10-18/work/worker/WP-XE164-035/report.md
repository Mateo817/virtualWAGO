> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-035 — Begrenzte Kontrollflussstruktur bei E0219E

## Ergebnis

**VERIFIZIERT (statisch, begrenzter Umfang):** Bei Datei-Offset `0x219E` beginnt im gebundenen Composite eine lineare Folge aus vier C166-Instruktionen: `mov` bei `0x219E`, `sub` bei `0x21A2`, `shr` bei `0x21A6` und terminales `rets` bei `0x21A8`. Die Instruktionen belegen exakt `[0x219E, 0x21AA)`, ohne interne Verzweigung oder Call. Damit ist die beobachtete lokale Struktur drei Fallthrough-Kanten bis zu `rets`; die Rückkehr hat in diesem Modell kein erfundenes Ziel. Die zwei isoliert untersuchten Callsites `0x36E2` und `0x3778` enthalten beide `calls E0219E`.

Die Aussage gilt ausschließlich für den angegebenen Hash, die sequenzielle C166-Dekodierung und diesen Eintrittspunkt. Sie bestimmt weder Funktionseinstieg noch Prototyp, Parameter, ABI oder Semantik der Operanden.

## Eingabe, Methode und Fundstellen

- Composite: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`; 17,110 Bytes; SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- REA zuerst: `open_binary` lehnte das rohe Composite als nicht unterstütztes Binärformat ab. Danach wurde REAs dokumentierter `execute_rizin_command`-Weg mit `-N -q`, `io.va=false`, `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false` genutzt. Es wurde keine globale Analyse ausgeführt. Die zwölf Zielbytes wurden zunächst als begrenzter Hexdump gelesen; jede Instruktion danach einzeln mit `pdj 1` am jeweils beobachteten Folgeoffset, damit kein Dekodierschritt den Endoffset `0x21AA` überschreitet.
- REA meldet Provider `rizin`, ausführbare Versionsnummer **OFFEN** (`version: null`). Der dokumentierte Versuch `?V` ergab einen Parserfehler; eine Versionsnummer wurde nicht abgeleitet. Provider-Profil und Laufzeitumgebung sind nicht verfügbar.
- Replay-Bindung für die Tabellen: Datei-Offset plus Basis `0xE00000` ergibt die dort gezeigte Replay-Adresse. Diese arithmetische Bindung ist die hier verwendete Adresskonvention, keine Aussage über Runtime-Mapping.
- Zielbytes und vier Dekodierungen: `ev_be1acec2d641894206d1c09d66c679c0906782a697be466374ed2940e51d94fa`, `ev_40ec3fde56cef383ede527a75c7e5327ae42510b7de1cec36ffbe07b919e66b0`, `ev_aef08103553c6a551b52461deb73b8df83e1a37c799fc6b2144639afafbee2a8`, `ev_b0103794ad242496abfc19109d1eb71e41a5e265a92579d7fcc4271234b0b4a2`, `ev_af06acaec52112abba5572c7db1e6d1f79faa4096ea1e587a5535b33ff42c8c5`.
- Isolierte Callsites: `ev_846562632fb95aee3dbf1345e5f3c4291594593609c1695cd528c12c83bd2dad` und `ev_1cdcb81ff766f0516c912840a2fa9d8cc2eb8b53f0ae34661e08ed7d18ed3137`.
- Versionsprobe: `ev_07ff84b036c984c15c00d966b296a59e534e86bcb2b78e894036a1c1d9e1c8b7`; sie dokumentiert nur den fehlgeschlagenen Versionsabruf.
- Das akzeptierte kanonisch gefilterte REA-Teilbundle liegt in [evidence/rea-finding-bundle.json](evidence/rea-finding-bundle.json). Es enthält genau die sieben eigenen, finding-tragenden Records (Ziel-Hexdump, vier Dekodierungen und zwei Caller-Dekodierungen) sowie die benötigten Top-Level-Manifeste; fremde und nicht finding-tragende Records sind ausgeschlossen. REA-Importprüfung: **PASS** (sieben IDs bereits im lokalen REA-Speicher vorhanden; keine Duplikate importiert, keine Unknowns hinzugefügt).

## Status und Restunsicherheit

- **VERIFIZIERT:** Vier Instruktionsstarts, Bytes, Größen, Kontiguität und drei lokale Fallthrough-Kanten; ein terminales `rets`; beide explizit vorgegebenen Callerziele. Belegt nur für den angegebenen Composite-Hash und den begrenzten Einstieg.
- **OFFEN:** Bedeutungen der in Rizin angezeigten Operanden (`0xfe06:0x2c46`, `0xfe02:0x2800`), Speicher-/Registersemantik, C166-Untervariante, Funktionseinbettung, Calling Convention, Caller-Logik und Laufzeitwirkung.
- **OFFEN:** Vollständigkeit globaler Caller-Xrefs. Nur `E-XE164-023`-Callsites `E036E2` und `E03778` waren vorgegeben und geprüft; keine weiteren Caller wurden gesucht.
- **NOT_RUN:** Unabhängige Ghidra-Dekodierprüfung. Sie wurde für die Frage nach der sichtbaren lokalen Struktur nicht benötigt; die fehlende Toolversion bleibt eine Reproduzierbarkeitsgrenze.
- **Alternative:** Ghidra `C166:LE:16:default` könnte die Instruktionslängen unabhängig vergleichen. Eine solche Abweichung würde den Befund offenhalten, bis sie geklärt ist.
- Keine Hardware-, Runtime-, Geräte-, Netzwerk- oder VM-Analyse; keine SFR-, ABI- oder Firmware-31-Aussage.

## Validierung

`validate.py` prüft Eingabegröße und SHA-256, die exakten 12 Zielbytes, dekodierte Größen/Bytes, lückenlose Offsetfolge, Basis-/Offsetbindung, Bereichsgrenze, CFG-Tabelle, beide Callerbytes/-ziele und die Tabellen-Evidence-IDs im kanonischen Export. Ergebnis: **PASS**. `sha256sum -c SHA256SUMS`: **PASS**.
