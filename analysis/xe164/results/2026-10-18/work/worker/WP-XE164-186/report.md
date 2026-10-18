> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-186 — FW31 IoDrvDal direkte ARM-Zugriffe mit `+0x61c`

## Ergebnis und Befundstatus

**VERIFIZIERT:** Die vollständigen file-backed `SHF_EXECINSTR`-Abschnitte des angegebenen FW31-ELF enthalten 9 Treffer für dekodierte ARM-Lade-/Speicherinstruktionen mit unmittelbarem, positivem Displacement `0x61c` (dezimal 1564): acht Loads und 1 direkter Store. Der Store ist `0x2f94: str r2, [r4, #1564]` in `.text`. Seine unmittelbare Instruktionssemantik ist, den sichtbaren Wert aus `r2` nach Speicher relativ zu `r4` plus `0x61c` zu schreiben.

Damit ist ein lokaler direkter Schreibzugriff mit dem gesuchten Displacement belegt. Ob dieser Zugriff einen von einem anderen Verbraucher gelesenen Wert publiziert, bleibt **OFFEN**: das Zielregister `r4` hat innerhalb des vorgeschriebenen Fensters keine sichtbare Definition. Es wird daher weder eine Feld-/Structbedeutung noch eine Verbindung zu anderem Binärcode behauptet.

## Artefakt, Coverage und Adressräume

- Eingabe: `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`
- Größe: 25.976 Byte; SHA-256: `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`
- `readelf -SW` meldet vier file-backed `PROGBITS`-Abschnitte mit Flag `AX`. Tabelle zeigt jeweils ELF-VA, Datei-Offset und halb-offenes Ende. Bei allen vier sind ELF-VA und Datei-Offset gleich.

| Abschnitt | ELF-VA / Datei-Offset | Größe | Exklusives Ende | Vollständig dekodierte A32-Wörter |
|---|---:|---:|---:|---:|
| `.init` | `0x948` | 12 Byte | `0x954` | 3 |
| `.plt` | `0x954` | 224 Byte | `0xa34` | 56 |
| `.text` | `0xa34` | 15.428 Byte | `0x4678` | 3.857 |
| `.fini` | `0x4678` | 8 Byte | `0x4680` | 2 |
| **Summe** | — | **15.672 Byte** | — | **3.918** |

Die angesprochenen Codeadressen in `hits.tsv` sind ELF-Link-VA und zugleich Datei-Offset. Es wird keine Ghidra-Adressabbildung verwendet. Die `clipped_window`-Spalte enthält pro Treffer ausschließlich disassemblierte Zeilen in `[site-0x20, site+0x24)`; beim Treffer `0xa30` reicht das erlaubte Fenster über `.plt` hinaus in `.text` und enthält daher Zeilen aus beiden Abschnitten.

## Trefferinventar

`hits.tsv` ist das vollständige Inventar mit Opcode und Operand, Basis-/Datenregister, Load/Store-Klassifikation, sichtbaren Registerdefinitionen innerhalb des geclippten Fensters und dem exakten Fenstertext.

| ELF-VA = Datei-Offset | Abschnitt | Opcode | Basis | Daten | Zugriff |
|---:|---|---|---|---|---|
| `0xa30` | `.plt` | `ldr pc, [ip, #1564]!` | `ip` | `pc` | Load |
| `0x214c` | `.text` | `ldr r3, [r9, #1564]` | `r9` | `r3` | Load |
| `0x2178` | `.text` | `ldr r3, [r9, #1564]` | `r9` | `r3` | Load |
| `0x2200` | `.text` | `ldr r2, [r9, #1564]` | `r9` | `r2` | Load |
| `0x2f94` | `.text` | `str r2, [r4, #1564]` | `r4` | `r2` | **Store** |
| `0x3410` | `.text` | `ldr r3, [r7, #1564]` | `r7` | `r3` | Load |
| `0x3434` | `.text` | `ldr r3, [r7, #1564]` | `r7` | `r3` | Load |
| `0x34c0` | `.text` | `ldr r3, [r7, #1564]` | `r7` | `r3` | Load |
| `0x3d38` | `.text` | `ldr r1, [pc, #1564]` | `pc` | `r1` | Load |

Die letzte Spalte in `hits.tsv` unterscheidet ELF-VA und Datei-Offset nicht, weil die Abschnittsabbildungen in dieser Trefferabdeckung identisch sind. Der Treffer bei `0xa30` ist ein Load mit Writeback-Markierung; `pc` ist der Datenregisteroperand. Beim Treffer bei `0x3d38` ist `pc` die architektonische Basis. Es sind beides unmittelbare Speicheroperanden, keine bloßen Symbol-/Kommentartreffer.

### Sichtbarer Ausschnitt des direkten Stores

Im Fenster `[0x2f74,0x2fb8)` zeigen die Instruktionen vor dem Store, dass `r2` in diesem Ausschnitt durch aufeinanderfolgende `add`-Instruktionen berechnet wird. Der Zielbasiswert `r4` wird im selben Fenster nicht definiert. Die disassemblierte Sequenz lautet:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Diese Instruktionsfolge ist keine Aussage über die Bedeutung der Zieladresse oder die Identität des von `r4` referenzierten Objekts.

## Methode, REA-Evidence und Toolversionen

**REA-first:** Die aktive REA-Evidence-Suche mit Filter auf den exakten SHA-256 lieferte `0` Records. Danach wurden lokale akzeptierte IoDrvDal-Reports und -Bundles durchsucht. WP-XE164-117 bindet dasselbe ELF und belegt darin einen begrenzten `+0x620`-Store im Generic-Loader; sein Funktionsdossier umfasst `0x12ddc..0x1331b`, nicht die vollständigen ausführbaren Abschnitte. Die vorhandenen begrenzten IoDrvDal-Dossiers enthalten somit keine vollständige Suche nach unmittelbarem `+0x61c` über sämtliche file-backed ausführbaren Abschnitte. **Diese Abschnitts-Coverage-Lücke ist hier einmalig dokumentiert.** Die vorhandene WP117-Evidence-ID für den Loaderdossier lautet `ev_97f0686f7d6be484340fdfaa6fbc1538921260faeb2bfdae04b732260c614608`.

Danach wurde `readelf -SW` für Abschnittsgrenzen verwendet. GNU ARM `objdump` disassemblierte alle Bytes der vier ausführbaren Abschnitte; der Validator prüft für jeden Abschnitt die lückenlose 4-Byte-Adressfolge vom Beginn bis zum exklusiven Ende. Als Treffer gelten nur direkte `ldr`-/`str`-Familienoperanden mit eckiger Basisregisteradressierung und positivem unmittelbarem Wert 1564. Symbolnamen und Kommentare, die zufällig `0x61c` enthalten, sind keine Treffer. Die Erfassung der Trefferfenster ist begrenzt und interpretiert keine Instruktionen außerhalb der je 68-Byte-Spanne.

Werkzeuge: GNU `readelf` 2.44; GNU `arm-linux-gnueabihf-objdump` 2.44; Python 3.13.5 für den lokalen Validator. Der vollständige breit angelegte Disassembler-Output wurde nur intern vom Validator ausgewertet, um Abschnittscoverage und Treffer zu zählen; im Paket stehen ausschließlich die vorgeschriebenen geclippten Trefferfenster. Es wurden keine anderen ELF-Dateien geöffnet oder disassembliert.

## Alternative Erklärung und Restunsicherheit

**HYPOTHESE:** Die direkte Storeinstruktion bei `0x2f94` könnte innerhalb der geprüften Bibliothek Daten für einen späteren Codepfad bereitstellen. Der disassemblierte Ausschnitt allein bestimmt jedoch weder, welche Datenstruktur relativ zu `r4` vorliegt, noch ob ein anderer Verbraucher denselben Speicher liest.

**OFFEN:** Die Bedeutung des Displacements, Laufzeitwerte und Objektidentität von `r4`, Alias- oder Nebenwirkungen außerhalb des Fensters sowie eine Verbindung zum getrennt berichteten IoDrvKbus-Load bleiben ungeprüft. Ein negativer Befund für andere Arten von Stores, andere Displacements, indirekte Schreibpfade oder Laufzeitverhalten folgt daraus nicht. Der Kontext zu IoDrvKbus aus dem Auftrag wurde nicht selbst geprüft. Keine Runtime-, VM-, Netzwerk-, Geräte- oder Hardwareaktion wurde ausgeführt.

## Prüfstatus und erzeugte Dateien

| Prüfung | Status | Umfang |
|---|---|---|
| Zielgröße und SHA-256 | PASS | Exakte Eingabeidentität geprüft |
| File-backed `SHF_EXECINSTR`-Coverage | PASS | Vier Abschnitte, 15.672 Byte, 3.918 lückenlos dekodierte ARM-Wörter |
| Vollständigkeit der direkten `+0x61c`-Treffer | PASS | Neun Treffer; acht Loads, ein Store |
| Trefferfenster | PASS | Alle Inventarzeilen auf `[site-0x20, site+0x24)` begrenzt |
| Datei-Manifest | PASS | Ausgabehashes durch `validate.py` geprüft |
| Laufzeit, VM, Netzwerk, Gerät, Hardware | NOT_RUN | Offlineumfang |
| Review | PASS | Worker Self-Review; unabhängige Prüfung NOT_RUN |

- `assignment.md` — Auftrag und Grenzen.
- `report.md` — Befund, Quellenbindung, Coverage, Grenzen und Hashes.
- `hits.tsv` — vollständiges Trefferinventar einschließlich Fenstertext.
- `validate.py` — reproduzierbare Offlineprüfung von Eingabeidentität, Abschnittscoverage, Treffervollständigkeit, Fenstern und Manifest.
- `SHA256SUMS` — SHA-256 der vier übrigen Paketdateien.

Die konkreten Dateihashes stehen in `SHA256SUMS`; der Validator prüft das Manifest gegen die Inhalte.
