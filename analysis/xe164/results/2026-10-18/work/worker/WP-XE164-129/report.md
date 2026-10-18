> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-129 — `codesys3` Routine `0x002FE12C`

## Befund

**VERIFIZIERT, begrenzter statischer Kontroll-/Datenfluss:** Der exakte ELF-Entry `0x002fe12c` ist als dynamisches Symbol `CMGetAPI2@@Base` bezeichnet; der Symboltabelleneintrag meldet `FUNC`, Größe 44 Bytes. Der von Rizin abgegrenzte vollständige Werkzeug-Body umfasst elf ARM-Instruktionen und die inklusive Spanne `0x002fe12c..0x002fe154` (44 Bytes), passend zur ELF-Symbolgröße. Der Body reserviert 16 Stackbytes, speichert das eingehende `r3` bei `fp-0x10`, speichert `fp+4` am aktuellen Stacktop und übergibt `fp-0x10` in `r3` an den direkten Aufruf bei `0x002fe14c` nach `0x002fdd20` (`CMGetAPI3@@Base`). Danach wird `sp` auf `fp-0x0c` gesetzt und über `ldm` zurückgekehrt. Diese Beschreibung ist aus den Instruktionen abgeleitet; sie ist kein Quelltext oder vollständiger ABI-Vertrag.

Im Body ist genau dieser eine direkte Call materialisiert. Der `ldm`-Epilog stellt den Rücksprung her. Es gibt keine bedingten Sprünge im Body. `r0` wird in den elf Instruktionen nicht explizit beschrieben; eine Bedeutung als Rückgabewert oder API-Parameter wird daraus nicht festgelegt.

**VERIFIZIERT, direkte Caller:** Der vollständige GNU ARM `objdump -d`-Vollscan enthält keinen `BL`-/`BLX`-Call mit direktem Ziel `0x002fe12c`/`CMGetAPI2`. Die bekannte exakte Referenz aus WP-XE164-128 ist eine Pointer-Erzeugung, kein direkter Call: `0x002fc58c: movw r3,#0xe12c`, `0x002fc590: movt r3,#0x2f`, danach Store an `fp-0x28` und später `blx r2` bei `0x002fc5c8`. WP128 belegt den gespeicherten Pointer in der lokalen Argumentposition `+0x34`; es belegt damit eine indirekte Übergabelane an einen zuvor im generischen Loaderkontext aufgelösten Entry, aber keine zur Laufzeit konkrete Zielidentität.

Ein Byte-Scan fand zusätzlich zwei exakte 32-Bit-Wörter `0x002fe12c`: bei ELF-VA `0x0002eb8c` im `.dynsym`-Bereich und bei ELF-VA `0x003a3640` im `.rodata`-Bereich. Der `.dynsym`-Treffer ist Symboltabelleninhalt und kein Caller. Der `.rodata`-Treffer ist ohne Consumer-Xref untypisiert; daraus folgt kein Aufruf. Die Details stehen in [xrefs.tsv](./xrefs.tsv).

## Adressdomäne und Grenzen

Ziel ist ausschließlich die geladene ELF-Default-Adresse des 32-bit little-endian ARM-Binaries `codesys3`; `objdump` zeigt die Instruktionen im `.text`-Bereich, Rizin meldet den Entry als `sym.CMGetAPI2`. Die Instruktionsadressen sind ELF-VMAs, keine Dateioffsets. Die beiden Rohdaten-Offset/VA-Zuordnungen folgen der ELF-LOAD-Abbildung (Dateioffset `0x1eb8c` → VA `0x2eb8c`; Dateioffset `0x393640` → VA `0x3a3640`). Der Körperbereich endet inklusiv bei `0x2fe154`; er ist kein angrenzender Bytebereich über `0x2fe158` hinaus.

Der erwartete Ghidra-Weg erreichte nach 300 Sekunden keinen Ergebnisdatensatz: `tool call failed for rea/procedure_info; Caused by: timed out awaiting tools/call after 300s`. Dieser identische Vorgang wurde nicht wiederholt. Deshalb sind keine Ghidra-Procedure- oder Xref-Datensätze vorhanden. GNU objdump hat den kompletten ausführbaren Inhalt dekodiert und nach direkten Callzielen gesucht; der rohe `.rodata`-Treffer besitzt weiterhin keinen typisierten Verbraucher. Indirekte Calls und nicht in diesen statischen Formen gespeicherte Referenzen können durch den Vollscan nicht als Caller ausgeschlossen werden.

Alternative Erklärung für den `.rodata`-Pointer: Er kann ein Daten-/Dispatch-Tabelleneintrag sein, oder unverbrauchte Metadaten; die vorliegenden Befunde entscheiden das nicht. Die WP128-Lane kann dynamisch auf eine andere Komponente zeigen. Der Name `CMGetAPI2` und die Adresse sind Symbol-/Disassemblerbezeichnungen und bilden keinen Funktionsvertrag.

## Werkzeuge, Eingaben und Prüfung

- REA `open_binary`, Provider Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; Import erkannte ELF / ARM. `procedure_info` einmal timeout nach 300s.
- Lokaler Fallback: Rizin 0.9.1 (`af`/`pdf` nur für `0x2fe12c`), GNU ARM binutils `arm-linux-gnueabihf-objdump` 2.44 (adressbegrenztes Disassembly und Vollscan für Calls), `readelf` (ELF-Abschnitte und LOAD-Segmente), Python 3 Bytevergleich zur Suche exakt ausgerichteter little-endian Wörter. Keine Runtime, VM, Netzwerk-, Geräte- oder Hardwareaktion.
- Eingabe-Hashes wurden vor Analyse geprüft. Das vollständige Body-Disassembly steht in [function-instructions.tsv](./function-instructions.tsv).

| Prüfschritt | Status |
|---|---|
| Vorgegebene Eingabe-SHA-256 | PASS |
| Rizin- und GNU-objdump-Bodygrenze/Instruktionsfolge abgeglichen | PASS |
| Direkter Call im Body bei `0x2fe14c` | PASS |
| Vollständiger GNU-objdump-Suchlauf nach direkten `BL`-/`BLX`-Callern | PASS (keiner gefunden) |
| Pointer-Lane aus WP128 und Rohdaten-Treffer getrennt klassifiziert | PASS |
| Ghidra Procedure-/Xref-Ergebnis | BLOCKED (300s Timeout) |
| Runtime, VM, Geräte, Netzwerk, Hardware | NOT_RUN |
| Unabhängiger Review | NOT_RUN |
| Self-Review | PASS |

`VERIFIZIERT` bezieht sich nur auf die adressierten Instruktionen und beobachteten statischen Treffer. Pseudocode/Prosa oben sind Werkzeugableitung und Register-/Stackbeobachtung, keine rekonstruierte Originalquelle. Ein ausführbarer Validator ist [validate.sh](./validate.sh); SHA-256-Werte der erzeugten Dateien sind in [SHA256SUMS](./SHA256SUMS).
