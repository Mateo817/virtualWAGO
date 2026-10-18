> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-278 — exakter installierter libc-Kandidat

VERIFIZIERT: Das exakt gehashte FW31-Abbild enthält /usr/lib/libc.so.6 als reguläre Datei inode1548 mit1434296 Bytes. Nur dieser Inode wurde per read-only debugfs aus einer temporären Kopie der exakten Partition2 extrahiert; kein Mount, keine Ausführung. SHA-256 dc47ee066e2c2d73ff9186440787543c3020711611f09002b6ab187d97d9dfa2. Imagehash49aa85c3…051c und Inventarhash16badcba…d23e wurden unmittelbar geprüft. extract_one.py/extraction.json und debugfs-Ausgaben erhalten die Herkunft.

VERIFIZIERT: Die ELF32-ARM-Dynsym enthält genau einen Namen memcpy, Index2313, GLOBAL/FUNC, ELF-VA919c0, Größe1248, Abschnitt12.text. Versionindex2 ohne hiddenbit referenziert GLIBC_2.4. Dieser deklarierte Typ ist FUNC, nicht IFUNC; daraus folgt keine Aussage über mögliche externe Interposition. Die vollständige Spanne [919c0,91ea0) ist file-backed und ausführbar markiert.

REA inspect_binary_layout war wegen nicht gesetztem REA_PWNTOOLS_PYTHON BLOCKED; keine Installation/Konfiguration wurde verändert. GNU readelf lieferte daraufhin nur Metadaten. Anschließend tatsächliche Ghidra12.1.4 procedure_info vor Körperanalyse: ev_9a0615d1e9a9d9ed712be255379521e69e2f6b487e8d751ea6a072da2c1225bf bindet einen zusammenhängenden1248B-Körper Ghidra[a19c0,a1ea0), entsprechend ELF+10000. Vollständige REA-Analyse ev_977f29df110262769b1209b9fbbe36522f1740e472ec20af22e75e2f35bcab66 ist roh erhalten und an WP279 zur genauen136B-Pfadprüfung übergeben. Eine angezeigte Decompiler-Signatur ist kein eigener API-/ABI-Nachweis.

OFFEN: tatsächliche GOT-Auflösung, geladenes Objekt, Laufzeitadressen und Implementierungswirkung. Diese Metadaten alleine schließen keine Kopier- oder Registerprämisse aus E295. Keine Systembibliothek des Analysehosts wurde als Firmwarequelle eingesetzt. Runtime/VM/Gerät/Zielnetz NOT_RUN; private Artefakte ausschließlich.

validate.py prüft unabhängig aus ELF-Tabellen Quelle/Inode/Symboltyp/Version/Abschnitt und aus vollständiger REA die Körpergrenzen; PASS. Root Self-Review, keine unabhängige Prüfung dieses Pakets behauptet.
