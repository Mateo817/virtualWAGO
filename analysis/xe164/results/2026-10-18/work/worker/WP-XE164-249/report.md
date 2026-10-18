> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-249 — `ComponentEntry` +0x24 gespeicherter Hook-Wert

## Ergebnis

**VERIFIZIERT (lokale Instruktionen):** In dem gebundenen `libIoDrvDal.so.1.0.2` liest `ComponentEntry` bei Ghidra `0x14508` ein 32-bit-Wort aus dem Eingabeobjekt `[r0,#0x24]` in `r2`. Die unmittelbar folgende Instruktion bei `0x1450c` speichert genau `r2` nach `[r3,#0x328]`. Der lokale Basisaufbau ergibt ELF-VMA `0x16090` bzw. Ghidra `0x26090`; damit ist das Ziel ELF-VMA `0x163b8` bzw. Ghidra `0x263b8`. Dieses Ziel liegt im `.bss` des selben ELF (`0x16088..0x1a30c`, zero-fill; kein file-backed initialer Wortwert). Es gibt keine passende Relocation auf `0x163b8`.

Der Assignment-Kontext sagt, dass der vorgelagerte E160-Code den `ComponentEntry`-Eingabewert `+0x24` vor dem Aufruf mit `CMCallHook` an ELF-Adresse `0x2fecc4` belegt; die Laufzeitbindung ist dort ausdrücklich konditional. **Wenn** dieser Aufruf so gebunden ist, schreibt diese Funktion den eingehenden Wert unverändert nach `.bss`-Adresse `0x163b8`. Dieser Report re-prüft oder erweitert den fremden Aufrufer nicht.

**VERIFIZIERT (direkte lokale Referenzen):** Ghidra-Xrefs auf die korrigiert gemappte globale Adresse `0x263b8` liefern genau einen Verweis, den `WRITE` bei `0x1450c`. Die native Adressprüfung meldet ebenfalls genau diesen einen eingehenden WRITE. Kein direkter Read dieser gespeicherten Zelle und kein lokaler indirekter Transfer aus ihrem Inhalt ist damit belegt. Insbesondere ist kein `blx`/`bx`-Verbraucher des gespeicherten +0x24-Werts in den statisch erfassten direkten Referenzen dieses ELF gefunden.

Der Funktionskörper enthält einen anderen, unabhängigen indirekten Aufruf: `ldr r2,[r0,#0x28]` bei `0x14510`; bei nicht-null führt `blx r2` bei `0x1452c` aus. `r0` wird direkt davor bei `0x14528` aus `r1` kopiert; `r1` stammt aus dem Literal `0x10062001` (Ladevorgang bei `0x14460`). Das ist nicht der +0x24-Wert. Deshalb belegt dieser Aufruf keinen Call des gespeicherten Hooks und liefert keinen provablen +0x24-bezogenen Selector-15-Pfad.

## Ghidra/ELF-Abbildung und Evidence

Das Ziel ist ELF32 little-endian ARM, 25,976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. ELF-Symbol `ComponentEntry` hat `st_value=0x4448`, Größe 560. Die passende, gleich gehashte WP144-REA-Aufzeichnung hat den vollständigen Funktionskörper Ghidra `0x14448..0x14623` (476 Bytes), woraus zunächst `0x14448 - 0x4448 = 0x10000` folgt. Die eigene Ghidra-Abfrage `address_to_file_offset(0x14448)` gibt Datei-Offset `0x4448`; `address_to_file_offset(0x14508)` gibt `0x4508`. Die verwendeten REA-Abfragen enthalten daher ausschließlich bereits um `0x10000` verschobene Ghidra-Adressen. Der anfängliche Explorationsfehler `0x163b8` als Ghidra-Adresse wurde nicht verwendet: er ergab außerhalb des Ghidra-Memory-Blocks; die korrekte Adresse ist `0x263b8`.

Die verwendete Ghidra 12.1.4-Evidence liegt vollständig in `rea-wp249-evidence.json` (13 Records); die vollständige WP144-Funktions-Evidence einschließlich Literalpool liegt in `rea-wp144-evidence.json` (1 Record). `rea-scope.tsv` weist jede verwendete ID, Anfrage und das ausgewertete Adressfenster aus und markiert die beiden anfänglich unverschobenen Abfragen als ausgeschlossen. Der WP144-Record hat denselben Zielhash, denselben Ghidra-Provider und dieselbe Funktionsbody-Abgrenzung. Für `0x14508`, `0x1450c`, `0x1452c`, `0x263b8`, `0x26090`, den Entry und dessen ausgehende Referenzen wurden REA-Abfragen durchgeführt.

Ein gezielter GNU-Objdump-Fallback wurde nur zur Bindung des lokalen Literal-/Basiswegs und zur begrenzten Suche nach direkten Offsets verwendet. Er bestätigt die Instruktionswörter und den Literalpool. Im vollständigen Disassembly von `.text` ist `#0x328`/`#808` nur am bekannten Store vorhanden; `#0x3b8`/`#952` kommt nicht vor. Die vollständigen ELF-Relocationstabellen enthalten keinen Eintrag für `0x163b8`. Diese Fallback-Suche ist kein Alias- oder Pointer-Analysis-Beweis.

## Tabellen

- `entry-global.tsv`: Eingabewert, Store, gebildete Basis und Zielzelle.
- `consumer-selector.tsv`: belegte Zellreferenzen und der getrennte +0x28-Call-Lane.
- `xref-gaps.tsv`: genaue REA-Xref-Befunde sowie nicht aufgelöste Referenzklassen.
- `rea-scope.tsv`: Abnahmeprotokoll der verwendeten Evidence.
- `source-inputs.json`: gebundene Artefakte, Hashes und Zuordnungsbasis.

## Status und Grenzen

**VERIFIZIERT:** der örtliche +0x24-Lese-/Store-Weg, die berechnete `.bss`-Adresse `0x163b8`, der einzige direkte Ghidra-Xref (WRITE) und die Trennung vom +0x28-`blx r2`-Lane.

**OFFEN:** statische Xrefs schließen berechnete Aliaswege, zur Laufzeit gebildete Pointer, externes Beschreiben/Lesen des `.bss`-Worts oder Verbraucher außerhalb dieses exakten ELF nicht aus. Der hier verwendete begrenzte Offset-Fallback findet nur direkte immediate-basierte Zugriffe in `.text`; Split-adds, indirekte Basen, dynamische Kontroll-/Speichereffekte und nicht aufgelöste Transfers sind dadurch nicht global ausgeschlossen. Deshalb ist „kein +0x24-bezogener Selector-15-Call belegt“ der Befund; ein globaler Abwesenheitsbeweis wird nicht behauptet. Es wird keine ABI für opake Calls angenommen.

REA ist statische Analyse, kein Laufzeitnachweis. Keine Geräte-, VM-, Netzwerk- oder Codeausführung. Review: Self-review; unabhängige Prüfung **NOT_RUN**. Laufzeittests **NOT_RUN**.
