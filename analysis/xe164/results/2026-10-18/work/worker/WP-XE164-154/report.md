> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-154 — Direkte statische Transfers zu `SysDirOpen`

## Ergebnis

**VERIFIZIERT:** Die angegebene Eingabe `/usr/bin/codesys3` hat 5.181.396 Bytes und SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`. Ihre `.dynsym` enthält `SysDirOpen` als definiertes `FUNC GLOBAL DEFAULT`, VMA `0x002427ec`, Größe 40, Abschnitt 14. Ein gleichnamiger `SysDirOpen_`-Eintrag ist undefiniert und hat eine andere Adresse; er wurde nicht mit dem exakten Ziel verwechselt.

**VERIFIZIERT:** Die GNU-Binutils-2.44 Vollsuche über `objdump -D` findet genau 20 direkt codierte Transfers mit unmittelbarem Ziel `0x002427ec`. Alle 20 sind 32-Bit ARM `bl`; in diesem direkten Zieltrefferbestand gibt es keine `b`, `blx` oder sonstige Transfers. Die vollständigen Fundstellen, ELF-Dateioffsets und die 192-Byte-Fenster stehen in `direct-callers.csv`, `direct-target-search.txt`, `call-windows.txt` und `call-window-instructions.csv`.

**VERIFIZIERT, Korrektur des vorgegebenen Offsets:** Datei-Offset `0x39fe30` beginnt mit vier Nullbytes; der ASCII-Text `Components.Directory` beginnt erst bei `0x39fe34`. Der zweite angegebene Offset `0x39fe4c` ist der genaue Beginn von `/usr/lib/cds3-custom-components`. Der erste ausführbare `PT_LOAD` mit `p_offset=0`, `p_vaddr=0x10000`, `p_filesz=0x3a0340` bildet die tatsächlichen Stringanfänge auf VMA `0x003afe34` und `0x003afe4c` ab. Die `SysDirOpen`-VMA selbst liegt in demselben Segment bei Datei-Offset `0x002327ec`.

**VERIFIZIERT, auf die unmittelbaren Fenster begrenzt:** Für keine der 20 Call-Sites materialisieren die dort sichtbaren MOVW/MOVT-Paare oder aufgelösten ARM-PC-Literalwörter exakt die tatsächlichen Stringanfangsadressen `0x003afe34` oder `0x003afe4c`; diese Adressen erscheinen auch nicht als unmittelbare Adressen im disassemblierten Fenster. `literal-address-checks.csv` enthält 40 Vergleiche (20 Fenster × 2 tatsächliche Stringanfänge); `pc-literal-loads.csv` dokumentiert jedes in diesen Fenstern aufgelöste PC-Literal samt Datei-Offset und Wortinhalt. Die sichtbare Herkunft von `r0`–`r3` und dem ersten Stackargument `[sp]` ist je Fundstelle in `direct-callers.csv` zusammengefasst.

## Vollständige Direct-Caller-/Call-Window-Tabelle

Dateioffsets folgen im ersten `PT_LOAD` aus `VMA - 0x10000`. Der Window-Bereich ist `[Call-VMA-0x80, Call-VMA+4+0x40)`, also 128 Bytes vor dem 4-Byte-`bl` plus 64 Bytes danach. `call-window-instructions.csv` hat für diese 20 Fenster zusammen 980 geordnete GNU-objdump-Instruktions-/Datenzeilen. Das sind Bytefenster, keine behaupteten Ghidra-Funktionsgrenzen.

| Nr. | Callsite VMA | Datei-Offset | Transfer | Fenster VMA | Argumentzusammenfassung |
|---:|---:|---:|---|---|---|
| 1 | `0x00087b30` | `0x00077b30` | `bl` | `0x00087ab0..0x00087b73` | `r0=r3-0x100`, `r3=0x00512e18` aus Literalzelle; `r1` lokaler Puffer, `r2=100`, `[sp]` lokaler Puffer |
| 2 | `0x000b1f8c` | `0x000a1f8c` | `bl` | `0x000b1f0c..0x000b1fcf` | `r0=0x00352c14`; `r1` lokaler Puffer, `r2=255`, `r3=r7`, `[sp]` lokaler Puffer |
| 3 | `0x000b2164` | `0x000a2164` | `bl` | `0x000b20e4..0x000b21a7` | `r0=0x00352c14`; `r1` lokaler Puffer, `r2=255`, `r3=r7`, `[sp]` lokaler Puffer |
| 4 | `0x001a7f5c` | `0x00197f5c` | `bl` | `0x001a7edc..0x001a7f9f` | `r0=0x0037a1ec`; `r1` lokaler Puffer, `r2=255`, `r3`/`[sp]` lokaler Puffer |
| 5 | `0x001ab548` | `0x0019b548` | `bl` | `0x001ab4c8..0x001ab58b` | `r0=0x0037b08c`; `r1`,`r3`,`[sp]` lokale Puffer, `r2=255` |
| 6 | `0x001ab72c` | `0x0019b72c` | `bl` | `0x001ab6ac..0x001ab76f` | `r0=r6` (Eingabewert), `r1`,`r3`,`[sp]` lokale Puffer, `r2=255` |
| 7 | `0x001b6100` | `0x001a6100` | `bl` | `0x001b6080..0x001b6143` | `r0`,`r1`,`r3` lokale Puffer, `r2=255`, `[sp]=r5` |
| 8 | `0x001b64c8` | `0x001a64c8` | `bl` | `0x001b6448..0x001b650b` | wie Call 7 |
| 9 | `0x001be270` | `0x001ae270` | `bl` | `0x001be1f0..0x001be2b3` | `r0`,`r3`,`[sp]` lokale Puffer, `r1=0x00571590`, `r2=255` |
| 10 | `0x001e77f8` | `0x001d77f8` | `bl` | `0x001e7778..0x001e783b` | `r0=r4`, `r1=r2=r3=0`, `[sp]=r6` (im Fenster nullgesetzt) |
| 11 | `0x001e7a6c` | `0x001d7a6c` | `bl` | `0x001e79ec..0x001e7aaf` | `r0=r4+16`, `r1=r2=0`, `r3=0` auf erreichendem Pfad, `[sp]=r7` |
| 12 | `0x001e91b0` | `0x001d91b0` | `bl` | `0x001e9130..0x001e91f3` | `r0=r6`, `r1=r2=r3=0`, `[sp]` lokaler Puffer |
| 13 | `0x002078f4` | `0x001f78f4` | `bl` | `0x00207874..0x00207937` | `r0`,`r1`,`r3`,`[sp]` lokale Puffer, `r2=255` |
| 14 | `0x0021a9f4` | `0x0020a9f4` | `bl` | `0x0021a974..0x0021aa37` | `r0=0x00370440`; `r1=0x005ba6a0` aus Literalzelle, `r2=255`, `r3=r7`, `[sp]` lokaler Puffer |
| 15 | `0x0021aa4c` | `0x0020aa4c` | `bl` | `0x0021a9cc..0x0021aa8f` | `r0=r5`, `r1=r4+strlen(r4)`, `r2=255-r6`, `r3=r7`, `[sp]` lokaler Puffer |
| 16 | `0x0021ce74` | `0x0020ce74` | `bl` | `0x0021cdf4..0x0021ceb7` | `r0=r9` oder bedingt `0x0050ef4c` aus Literalzelle; `r1=r7`, `r2=255`, `r3`,`[sp]` lokale Puffer |
| 17 | `0x003077bc` | `0x002f77bc` | `bl` | `0x0030773c..0x003077ff` | `r0`,`r1`,`r3`,`[sp]` lokale Puffer, `r2=255` |
| 18 | `0x0033f6cc` | `0x0032f6cc` | `bl` | `0x0033f64c..0x0033f70f` | `r0`,`r1`,`r3`,`[sp]` lokale Puffer, `r2=255` |
| 19 | `0x0033f82c` | `0x0032f82c` | `bl` | `0x0033f7ac..0x0033f86f` | `r0`,`r1`,`r3`,`[sp]` lokale Puffer, `r2=r6` |
| 20 | `0x00342374` | `0x00332374` | `bl` | `0x003422f4..0x003423b7` | `r0=0x00345440`, `r1`,`r3` lokale Puffer, `r2=r4`, `[sp]=r10` |

Die Tabelle komprimiert nur die sichtbaren Quellen. Vollständige Register-/Stacknotizen samt Hinweisen auf weitergereichte Werte stehen im CSV; sämtliche dekodierten Zeilen und Bytes der Fenster sind in `call-window-instructions.csv` und `call-windows.txt` enthalten. Die Datei enthält keine Ghidra-Whole-Function-Disassemblies, da für den exakten Digest kein passender REA-Record verfügbar war.

## Symbol- und Segmentabbildung

`readelf -Ws` beobachtet den definierten Dynsym-Datensatz für `SysDirOpen` mit VMA `0x002427ec`, Größe 40 und `Ndx 14`; `readelf -lW` zeigt den ausführbaren `PT_LOAD` von Datei-Offset `0` nach VMA `0x00010000`. Daraus folgen:

| Objekt | Datei-Offset | VMA | Abbildung |
|---|---:|---:|---|
| `SysDirOpen` Dynsym-Adresse | `0x002327ec` | `0x002427ec` | `VMA = Offset + 0x10000` |
| `Components.Directory` Stringbytes (tatsächlicher Beginn; `0x39fe30` hat vier vorangehende Nullbytes) | `0x0039fe34` | `0x003afe34` | `VMA = Offset + 0x10000` |
| `/usr/lib/cds3-custom-components` Stringbytes | `0x0039fe4c` | `0x003afe4c` | `VMA = Offset + 0x10000` |

Vollständige `readelf`-Header, Segment-/Sectiontabellen, Dynsym-Zeilen und Rohbytes stehen in `symbol-segment-mapping.txt`.

## Methode und REA-Evidence

REA wurde zuerst geprüft. `binary_session` meldete die Ghidra-Route verfügbar, aber kein offenes Ziel; der hashgefilterte `get_evidence_bundle(detail="summary")` ergab null retained Records für den exakten Eingabe-SHA. Im WP-XE164-152-Arbeitskontext war die bekannte Autoanalyse-Lücke der Grund, keinen identischen langen Neuimport anzustoßen. Damit gibt es für dieses Paket keine REA-Evidence-ID und keine Ghidra-Funktionsgrenzen. Die konkrete Abweichung und die Rückgaben sind in `rea-evidence.md` festgehalten.

Der Fallback ist ein reproduzierbarer Offline-Aufruf von GNU `arm-linux-gnueabihf-objdump` 2.44 mit `-D -w -M reg-names-std` über alle ELF-Sektionen; vollständiger Suchauszug und rohe Call-Window-Disassemblies liegen im Ausgabeverzeichnis. `readelf`/Binutils 2.44 bindet Dynsym, Segmentabbildung, Abschnitte und Offsetkoordinaten. Keine Runtime-, Geräte-, Netzwerk- oder VM-Beobachtung wurde vorgenommen.

## Alternative Erklärung und Restunsicherheit

**OFFEN:** Ein nicht im lokalen Fenster materialisierter Zeiger könnte bereits vor dessen Beginn in einem Register oder Stackslot vorhanden sein. Dynamische Argumentwerte und indirekt aufgelöste Datenzeiger könnten daher zur Laufzeit auf einen der tatsächlichen Kandidaten (`0x003afe34`, `0x003afe4c`) zeigen. Das Ergebnis sagt ausschließlich, dass diese exakten Literale in den unmittelbaren Fenstern nicht als unmittelbare Adressen, MOVW/MOVT-Konstanten oder ARM-PC-Literalwörter auftauchen; es widerlegt nicht, dass ein Aufrufer oder vorgelagerter Code den Zeiger dynamisch zuführt.

**OFFEN:** Es wurden keine indirekten Aufrufer gesucht oder gezählt. Der Ganz-ELF-Negativbefund ist auf direkt statisch codierte B/BL-Familienziele beschränkt. Der Disassembler dekodiert Fensterbytes außerhalb einer Ghidra-Funktionsgrenze nach ARM-Objdump-Regeln; mögliche Daten-/Instruktionsmehrdeutigkeit bleibt bestehen. Die Call-Argumentregister werden als sichtbare Bit-/Registerherkunft beschrieben, nicht mit einer erfundenen API-Signatur oder Runtime-Semantik belegt.

## Tests und erzeugte Dateien

| Prüfung | Status | Umfang |
|---|---|---|
| Zielgröße und SHA-256 | PASS | exakte vorgegebene Datei |
| Dynsym und `PT_LOAD` | PASS | `readelf`, VMA-/Offsetabbildung |
| vollständige direkte Zielsuche | PASS | jede Sektion via GNU objdump `-D`; 20 Treffer |
| Call-Window-Instruktionstabellen | PASS | 20 Fenster, 980 Zeilen |
| Kandidatenadressvergleich | PASS | 40 Fenster-/Literalvergleiche plus PC-Poolworttabelle |
| REA Ghidra-Funktionsgrenzen | NOT_RUN | kein vorhandener exact-hash Evidence Record; identischer Neuimport wegen protokollierter Lücke ausgelassen |
| indirekte Aufrufer / Runtime | NOT_RUN | explizit außerhalb des Auftrags |

Erzeugte Inhaltsdateien: `report.md`, `generate.py`, `validate.py`, `validator-result.txt`, `direct-callers.csv`, `call-window-instructions.csv`, `call-windows.txt`, `direct-target-search.txt`, `literal-address-checks.csv`, `pc-literal-loads.csv`, `symbol-segment-mapping.txt`, `rea-evidence.md`, `rea-evidence.json`, `tool-versions.txt`. SHA-256 aller Inhaltsdateien sind in `SHA256SUMS` hinterlegt. Die Eingabedatei blieb unverändert.
