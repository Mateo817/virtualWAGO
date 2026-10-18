> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-191 — begrenzte Kontroll-/Datenflussanalyse

## Ergebnis

**VERIFIZIERT:** Im ELF32-Little-Endian-ARM-Objekt rufen `0x2f08` und `0x2f4c` direkt denselben PLT-Eintrag für den dynamischen Symbolnamen `adi_GetApplicationInterface` auf. Der Rückgabewert in `r0` wird in beiden Sequenzen als Basis für einen 32-Bit-Load genutzt: am Offset `+0x0c` bei `0x2f14`, am Offset `+0x10` bei `0x2f50`. Das geladene Wort in `r3` wird jeweils mit `blx r3` aufgerufen.

Beim ersten indirekten Aufruf setzt der sichtbare Code unmittelbar zuvor `r0=10`, `r1=r5`, `r2=r8`; `r3` stammt aus `[r0+0x0c]` vor dem Überschreiben von `r0`. Dessen Rückgabe-`r0` wird nach `r6` kopiert und bei `0x2f20` auf null geprüft. Ein von null verschiedener Wert verzweigt nach `0x32f0` (Zieladresse beobachtet, Zielcode nicht gelesen).

Bei einem späteren `strcmp`-Treffer ist `r0=0`; der sichtbare Code lädt `[r7]` in `r3` und speichert dasselbe Wort in `[r4+0x618]` (`0x2f48`). Danach erfolgt der zweite direkte Dynsym/PLT-Aufruf. Sein Rückgabe-`r0` ist Basis für den Load `[r0+0x10]`; anschließend setzt der Code `r0=[r7]` und ruft das geladene Ziel in `r3` indirekt auf (`0x2f58`). Das Ergebnis wird nach `r6` kopiert. `r1` und `r2` an diesem zweiten indirekten Aufruf sind nicht durch die sichtbare Sequenz bestimmt, da kein in-range Setup nach dem Provideraufruf erfolgt und die vorherige `strcmp`-Rückgabe sie nicht bindet.

Nach der Schleife führt `r6==0` zum Storepfad, `r6!=0` verzweigt nach `0x32f0`. Der Store `[r4+0x61c]` erhält den aus Literal `0x00013438` gebildeten Wert: `0x2f84` addiert das Literal zu ARM-PC `0x2f8c`, dann addieren `0x2f88` und `0x2f90` zusammen `0x3eac`; Ergebnis `0x163c4 + 0x3eac = 0x1a270`. Das Literal liegt bei VA/Dateioffset `0x3360`; seine exakten Bytes sind `38 34 01 00`. Damit stimmt das lokale Rechenresultat mit dem zuvor akzeptierten Kontext überein.

Das errechnete Ziel `0x1a270` ist eine ELF-Linkzeit-VA innerhalb der als `NOBITS` markierten `.bss`-Sektion; es ist kein Dateioffset und für diese Adresse wurde kein Symbol/Name beobachtet. Der im Auftrag übergebene akzeptierte Kontext E-XE164-213..216 nennt zusätzlich zwei direkte Transfers nach `0x2ddc`; ihre Quellinstruktionen liegen außerhalb dieser Analyse und wurden nicht neu eingesehen. Die Herkunft von `r4` bleibt offen.

## Kontrollfluss und Guards

Der am Bereichsanfang sichtbare Pfad prüft `r3` bei `0x2dec`. Gleichheit zu null springt exakt auf die Bereichsgrenze `0x30a0`, deren Instruktion nicht untersucht wurde. Der Fall `r3!=0` fällt zu `0x2ed8`; dort vergleicht der Code `r1` mit `r3`, setzt den über `[sp+0x0c]` geladenen Zeiger auf null und springt bei Gleichheit nach `0x3304`. Bei Ungleichheit schreibt er `2` über diesen Zeiger und kehrt bei `0x2f04` zurück. Die sichtbaren Bytes bei `0x2f08` folgen damit nicht als normaler Fallthrough auf diesem Rückkehrpfad. Die Eintrittsbedingung für `0x2f08` liegt außerhalb des zugelassenen Fensters und bleibt **OFFEN**.

Im sichtbaren Abschnitt `0x2f28–0x2f78` wird `r7` mit `r5` initialisiert und durch Einträge im Schritt `8` geführt. `strcmp([r7+4], [sp+0x1c])` wird bei Gleichheit mit null über `0x2f40` geprüft; nur dann erfolgen Store `[r4+0x618]`, zweiter direkter Aufruf und zweiter indirekter Aufruf. Nach jedem Eintrag wird `r7` erhöht. Die Endadresse ist `r5 + ([sp+0x6c] << 3)`; `r7 < end` wiederholt die Schleife. Danach entscheidet `r6==0` über den Pfad zum Store bei `0x2f94`.

## Argument-/Rückgaberegister und Stores

| Stelle | Direkt belegte Registerwirkung |
|---|---|
| `0x2f08` direkter Aufruf | `r0-r3` unmittelbar vor dem Call bleiben **OFFEN**: die vorherige lokale Sequenz ist Rückkehrcode; die erreichende Kante ist außerhalb des Bereichs. |
| `0x2f14–0x2f1c` erster indirekter Call | Return `r0` des Dynsym/PLT-Aufrufs → Load `r3=[r0+0x0c]`; `r2=r8`, `r1=r5`, `r0=10`; `blx r3`. |
| `0x2f20` | Indirekte Rückgabe `r0` → `r6`; Flags aus `r0-0`; `r6!=0` verzweigt nach `0x32f0`. |
| `0x2f44–0x2f4c` Treffer | `r3=[r7]`; gleicher Wert nach `[r4+0x618]`; beim direkten Call `r0=0` aus dem erfolgreichen Vergleich und unverändert seit `0x2f3c`; `r3=[r7]`. `r1/r2` sind nicht als Callargumente gesichert. |
| `0x2f50–0x2f58` zweiter indirekter Call | Return `r0` des zweiten Dynsym/PLT-Aufrufs → Load `r3=[r0+0x10]`; `r0=[r7]`; `blx r3`. `r1/r2` bleiben durch diese Sequenz unbestimmt. |
| `0x2f5c–0x2f78` | Rückgabe-`r0` des zweiten indirekten Calls → `r6`; Schleifenvergleich; nach Schleife `r6==0` erlaubt Folgepfad, `r6!=0` verzweigt nach `0x32f0`. |
| `0x2f7c–0x2f94` | Literal `0x13438` plus PC und Additionskonstanten → `0x1a270`; Store nach `[r4+0x61c]`. `r4`-Ursprung bleibt unbekannt. |

Die Instruktionen nach dem Store bei `0x2f94` rufen bei `0x2f9c` einen weiteren Loader-Eintrag auf und prüfen dessen Rückgabe; diese Kante liegt nach den hier untersuchten Stores und ist nicht erforderlich, um deren Herkunft abzuleiten. Kein Callee-Vertrag oder Callee-Effekt wird behauptet.

## Alternativen und Unsicherheit

- Die zwei direkten Calls könnten aufgrund von ELF-Symbol-/Relocationseinträgen beide als Aufrufe desselben importierten Dynsym-Namens gebunden werden; das ist der belegte Fall. Es wird daraus kein semantischer Vertrag des Namens abgeleitet.
- Für `[r4+0x618]` ist die konkrete Quelle sichtbar: `[r7]` im Vergleichstrefferpfad. Für `[r4+0x61c]` ist die konkrete arithmetische Quelle sichtbar: Literal plus PC- und Immediate-Adds. `r4` selbst wird im Bereich nicht hergeleitet.
- Die Anzahl möglicher Treffer und die Bedeutung von Listeneinträgen, Vergleichsstring, Provider-Rückgabe oder indirekten Zielen bleiben offen. `r5`, `r8`, Stackwerte und `r4` haben keine weitergehende Herkunftsbehauptung.
- Der Code von Zieladressen `0x30a0`, `0x32f0`, `0x3304` sowie der restlichen Routine wurde nicht gelesen. Diese Adressen erscheinen nur als direkte Branchziele der innerhalb des Bereichs decodierten Instruktionen; es wurden keine dortigen Bytes oder Instruktionen angefordert.
- Das REA-Evidence-Bundle enthielt für den Zielhash null Einträge. Diese Lücke wird nicht durch alte, nicht gebundene Belege ersetzt.

## Identität, Werkzeuge und Verifikation

- Eingabegröße: `25976` Bytes; SHA-256: `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` (frisch berechnet, stimmt mit Vorgabe überein).
- ELF: ELF32, little-endian, ARM, EABI5 hard-float. `.text` VA/Dateioffset `0x0a34`; der komplette Bereich liegt in dieser dateigebundenen Sektion, sodass VA `0x2ddc` auf Dateioffset `0x2ddc` abbildet.
- Exakter Instruktionsbereich: `[0x2ddc,0x30a0)`, 708 Bytes; SHA-256 `fa518ed59b6999a094716b1f80123c129d2be8b5d79652ed28c827e34db436d7`.
- Einzige für die Ableitung von `[r4+0x61c]` gelesene externe Literalstelle: VA/Dateioffset `0x3360`, genau 4 Bytes `38 34 01 00`, Little-Endian-Wert `0x00013438`.
- GNU ARM objdump und GNU readelf aus Binutils `2.44`; `sha256sum`, Python 3-Standardbibliothek. REA Server `rea-agents 6.5.0`; Bundle-Abfrage per exaktem Zielhash ergab `matching_records=0`. Keine Ghidra-Importoperation.
- Validator: `python3 validate.py` — **PASS**. Er prüft Eingabe- und Bereichshash, Literalbytes, sämtliche Instruction-Adressen in `flow.tsv` innerhalb des erlaubten Codefensters und die Manifest-Hashes. Das ist eine lokale Integritäts-/Scopeprüfung, keine unabhängige Analyse.
- Status: statische Instruktions-/Edge-Aussagen **VERIFIZIERT**; Eintrittsbedingungen, Werteherkunft von `r4/r5/r8`, Callee-Verhalten und Semantik **OFFEN**. Scope: PASS, da keine out-of-range Instruktionen oder Literalbytes außerhalb des einzigen angegebenen 4-Byte-Worts gelesen wurden.
