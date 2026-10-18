> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-120 — Statische Referenzen auf Slot `0x00601670`

## Ergebnis

**VERIFIZIERT:** Im exakt gehashten ARM-ELF `codesys3` materialisiert Ghidra vier direkte Referenzen auf Default-Space-Adresse `0x00601670` (von Ghidra kanonisch als `0x601670` ausgegeben): Reads bei `0x330624`, `0x330634`, `0x330654` in `FUN_00330610` und ein Write bei `0x336b0c` in `CmpIoMgr__Entry`. Die drei Reads und der eine Write sind durch `procedure_references` mit Ghidra-Referenztyp READ/WRITE bestätigt. Es wurden keine weiteren direkten Xrefs durch `xrefs(0x00601670)` materialisiert.

**VERIFIZIERT:** Die Reader-Funktion berechnet die Basisadresse mit `movw r4,0x1520` (`0x330618`) und `movt r4,0x60` (`0x33061c`), also `r4 = 0x00601520`. Die Loads an `0x330624`, `0x330634` und `0x330654` greifen jeweils mit Displacement `0x150` zu, somit auf `0x00601520 + 0x150 = 0x00601670`. Der erste Load wird auf Null geprüft und verzweigt bei Null nach `0x330674`; der zweite lädt `r5`, das Ziel des indirekten Calls `blx r5` bei `0x330648`; der dritte lädt `r4`, das Ziel des indirekten Calls `blx r4` bei `0x330664`. Der Call-Lane `0x330610..0x33067b` wird hier nur als notwendiger Kontext verwendet; die Laufzeitwerte und Call-Ziele bleiben unbekannt.

**VERIFIZIERT:** Der Writer `CmpIoMgr__Entry` berechnet in `0x336af0`/`0x336af8` dieselbe Basis `r1 = 0x00601520`. Sein Prolog kopiert den Eingangsregisterwert `r0` bei `0x336ac8` nach `r12`; `ldr r4,[r12,#0x1c]` bei `0x336aec` lädt daraus vier Bytes in `r4`. Die Instruktion `str r4,[r1,#0x150]` bei `0x336b0c` schreibt diesen Registerwert in den Slot. Im statischen Kontrollfluss ist der Store vom Funktionseintritt aus erreichbar, bevor die spätere Bedingung bei `0x336ba4` geprüft wird. Damit ist der belegte minimale statische Initialisierungspfad: Funktionsparameter `r0` → Kopie nach `r12` → Load aus `[r12+0x1c]` → Store nach `[0x00601520+0x150]`. Das benennt keine Bedeutung für den Parameter oder Slot.

**VERIFIZIERT:** Die vier vom analysierten Ghidra-Speicher gelesenen Bytes am Slot sind `00 00 00 00` (`read_bytes`, vollständig). `readelf` zeigt, dass `0x00601670` innerhalb `.bss` liegt: `.bss` ist `NOBITS`, VMA `0x00510a50`, Größe `0x10bcf8`, damit Adressende exklusiv `0x0061c748`. Folglich hat der Slot keinen dateigestützten ELF-Offset. Ghidras einmalige `address_to_file_offset(0x00601670)`-Abfrage scheiterte exakt mit `Address has 0 authoritative target-file mappings: 0x601670`; der benannte GNU-`readelf`-Fallback bestätigte anschließend die `.bss`/`NOBITS`-Einordnung. Es wurde kein `objdump`-Fallback benötigt.

## Adressräume und Fundstellen

| Gegenstand | Ghidra Default Space / ELF VMA | ELF-Dateiabbildung | Beobachtung |
|---|---:|---|---|
| Slot | `0x00601670` | kein dateigestützter Offset, `.bss` / `NOBITS` | vier initialisierte Ghidra-Memory-Bytes `00000000`; Laufzeitinhalt unbekannt |
| Reader-Basis | `0x00601520` | `.bss`-Bereich | durch ARM `movw`/`movt`-Konstanten konstruiert |
| Reader-Xref 1 | `0x00330624` | Werkzeugableitung aus PT_LOAD: Datei-Offset `0x00320624` | `ldr r3,[r4,#0x150]`, READ; Nulltest folgt bei `0x330628` |
| Reader-Xref 2 | `0x00330634` | Werkzeugableitung aus PT_LOAD: Datei-Offset `0x00320634` | `ldr r5,[r4,#0x150]`, READ; `blx r5` bei `0x330648` |
| Reader-Xref 3 | `0x00330654` | Werkzeugableitung aus PT_LOAD: Datei-Offset `0x00320654` | `ldr r4,[r4,#0x150]`, READ; `blx r4` bei `0x330664` |
| Writer-Xref | `0x00336b0c` | Werkzeugableitung aus PT_LOAD: Datei-Offset `0x00326b0c` | `str r4,[r1,#0x150]`, WRITE |

Code- und Slotadressen oben sind Ghidra-Default-Space-Adressen, die bei diesem ELF denselben Zahlenwert wie die ELF-VMA haben. Die genannten Code-Dateioffsets sind arithmetisch aus `readelf -lW` hergeleitet: der erste `LOAD` hat Datei-Offset 0 und VMA `0x10000`, also `file offset = VMA - 0x10000`. Das ist eine Werkzeugableitung aus der beobachteten PT_LOAD-Abbildung. Für die Slotadresse gibt es keinen Dateioffset, da sie im `NOBITS`-Speicher liegt. Der Fallfehler in der Schreibweise (`0x601670` gegenüber `0x00601670`) ist ausschließlich führende Nullpadding; der numerische Wert ist identisch.

Ghidra ordnet `FUN_00330610` den vollständigen zusammenhängenden Body `0x330610..0x33067b` (inklusive, 108 Byte, fünf Basic Blocks) zu. `CmpIoMgr__Entry` hat den Body `0x336a84..0x336bdf` (inklusive, 348 Byte, drei Basic Blocks). Diese Prozedurgrenzen stammen aus `procedure_info` / Containment-Evidence, nicht aus einer Adressspanne-Vermutung.

Die unmittelbare Adressebildung in beiden Funktionen erfolgt über `MOVW`/`MOVT`-Konstanten und anschließenden Basis-plus-Offset-Zugriff. In den hier benötigten Instruktionslanes ist kein GOT-Ladevorgang oder PC-relativer Slotzugriff beobachtet. Diese Feststellung gilt nur für die analysierten Referenzen, nicht als Aussage zum gesamten ELF.

## Interpretation, Alternative und Restunsicherheit

**HYPOTHESE:** Weil zwei Loads des Slots unmittelbar die Registerziele zweier `blx`-Instruktionen bereitstellen, verhält sich der Slot an diesen Call-Sites als indirekte Call-Zielquelle. Das belegt weder die API noch die Funktion oder Identität eines tatsächlichen Ziels.

**Alternative Erklärung:** Der Writer könnte beim jeweiligen Aufruf einen Nullwert oder einen Wert mit anderer Bedeutung als ein gültiger Callback ablegen; der Reader überspringt den Call-Lane, falls der erste Slot-Load Null ergibt. Auch ein abweichender Aufrufablauf oder eine andere Reihenfolge von Writer und Reader ist durch statische Referenzen allein nicht ausgeschlossen.

**OFFEN:** Ob `CmpIoMgr__Entry` zur Laufzeit ausgeführt wird, welcher konkrete Wert aus `[r0+0x1c]` stammt, ob er nach dem Store unverändert bleibt, und welche Adressen die `blx`-Instruktionen tatsächlich anspringen. Der Nullwert ist der initiale Ghidra-Ladezustand aus dem ELF-BSS, keine Messung eines Laufzeitzustands. Der Slot ist nicht als benanntes Feld oder Strukturmember interpretiert.

**Restunsicherheit:** Direkte Xrefs sind die von Ghidra materialisierten statischen ReferenceManager-Beziehungen. Indirekte, dynamisch konstruierte oder vom Analysator nicht als exakte Slotreferenz repräsentierte Zugriffe sind durch diesen Xref-Query nicht ausgeschlossen. Die `address_to_file_offset`-Ablehnung ist einmal notiert; `readelf` zeigt, warum der ELF-Offset für NOBITS fehlt. Es wurde kein Geräte-, Netzwerk-, VM- oder Laufzeitzugriff ausgeführt.

## Evidence und Werkzeuge

| Beobachtung | Fundstelle / Evidence ID | Status |
|---|---|---|
| Eingabegröße 5.181.396 Byte und SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | lokal geprüft; Ghidra Evidence Subject | VERIFIZIERT |
| Ghidra-Version/Profil | Ghidra 12.1.4; Profil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de` | VERIFIZIERT |
| Vollständige direkte Xref-Liste zum Slot | `ev_da0e9b92d864bb334697d9fb66bb7a58c888cfa0f25107500c943ce20badf863` | VERIFIZIERT |
| Containment der drei Reader-Xrefs | `ev_d585f4656cf7ae2972c88dd0dd0b94a88901331d96685977c1632724d8d2f246`, `ev_bed2b600113a1ff499b7834d4d262bf41a7a15994b5d2d9c5d56418e8af46d4b`, `ev_d4fc2522ee78a119f3b469bdc11babd4391f29eb2d284314a6d6dade002ef94f` | VERIFIZIERT |
| Containment des Writer-Xrefs | `ev_c480adbf5b7f892cb010962269d5689d90e6d1a562c51fb90be073bafb962433` | VERIFIZIERT |
| Reader-Instruktionen und Slotdatenfluss | `ev_894c35a155c824207581cebb2034b90a0c2256bef8b83bcafb862ecdc76c14c3` | VERIFIZIERT |
| Reader ReferenceManager-Kinds, inkl. 3× READ und unresolved Calls | `ev_db2a6687e167cf713c2b010de79a0a22aa107bf80f64c94ebfbbafee8f542fb5` | VERIFIZIERT |
| Writer-Instruktionen und Eingangskette | `ev_a7649798481546843df735be12c2a42fb525a6be00b32e912f62edfb2400bf49` | VERIFIZIERT |
| Writer ReferenceManager-Kinds, inkl. WRITE am Slot | `ev_aba094e0a118f6fbd2267bba9c10c2cb9905035a4991b4618be822e2e7ce4678` | VERIFIZIERT |
| Procedure Metadata Reader / Writer | `ev_7132f19d7f4771fd953a76650d78bd327d595312edca72254b744b6f2a2b2bb9`, `ev_019adebe573fbbaefdf7371001ec8947a0001a93a6c91f7fec6c54279fc1b485` | VERIFIZIERT |
| Ghidra initialisierte Slotbytes | `ev_e072198411642d057576866a4df41b8e1f08a61b7e66cb3cbb4f1a802ac762bc` | VERIFIZIERT |
| ELF-Segment- und `.bss`-Koordinaten | GNU `readelf` 2.44, `readelf -lW` und `readelf -SW`; `.bss` NOBITS VMA `0x510a50`, Größe `0x10bcf8` | VERIFIZIERT |
| Fehlgeschlagene Dateioffset-Abbildung (genau ein REA-Fehler) | `address_to_file_offset(0x601670)`; Einzelmeldung siehe Beobachtung oben | BLOCKED für Dateioffset; `.bss`-Einordnung durch `readelf` verifiziert |

REA wurde vor dem GNU-Fallback genutzt. Ghidra öffnete das statische ELF als ARM-LE-32:v8 unter Standard-Autoanalyse; Profil-Digest siehe oben. GNU `readelf` war nur nötig, um den beobachteten Dateioffset-Mapping-Fehler mit der ELF-`NOBITS`-Sektion einzuordnen. Keine Hersteller-API, keine Struktur oder Feldsemantik wurde angenommen.

## Prüfstatus und Dateien

| Prüfung | Status |
|---|---|
| Eingabegröße und SHA-256 | PASS |
| Kanonisches REA-Bundle: Target-Hash, 12 Evidence-Records, eindeutige Evidence-IDs | PASS |
| Direkte Slot-Xrefs entsprechen genau drei Reads und einem Write | PASS |
| Reader-/Writer-Instruktionen und Slotadressarithmetik | PASS |
| BSS-Abgrenzung mit `readelf` gegen fehlenden Dateioffset | PASS |
| Laufzeit-Call-Ziele und dynamische Reihenfolge | NOT_RUN |
| Geräte / Netzwerk / VM / Zielausführung | NOT_RUN |

Erzeugt: `report.md`, `rea-evidence-bundle.json`, `validate.py`, `SHA256SUMS`. Der Validator wurde als Self-Review angelegt und gegen die Evidence-Daten ausgeführt; kein unabhängiger Review oder Worker-Lauf wird behauptet. Pseudocode wurde nicht verwendet.
