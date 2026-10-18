> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-156 — Bounded value flow to both `SysDirOpen` calls

## Ergebnis

**VERIFIZIERT:** In beiden erreichbaren direkten `SysDirOpen`-Calls im Bereich erreicht denselbe Frame-relative Zeiger `fp-1324` das Register `r0`:

| Callsite | Kontrollflussbedingung innerhalb des Bereichs | `r0` bei Call-Eintritt |
|---|---|---|
| `0x33F6CC` | Rückkehr aus `0x33F634` mit `r0 != r8`; Pfad über `0x33F638..0x33F6C8` | `r11 - 0x52c` = `fp-1324`, aus `0x33F6B0/0x33F6B8` |
| `0x33F82C` | Rückkehr aus `0x33F634` mit `r0 == r8`; bedingter Sprung zu `0x33F808` | `r11 - 0x52c` = `fp-1324`, aus `0x33F80C/0x33F81C` |

Die Instruktionsfolge nach dem Setting-Call `0x33F5D4` überschreibt `r0` sofort mit Frame-Adressen und später Konstanten. Kein sichtbarer Def-Use-Pfad führt den Rückgabewert aus `0x33F5D4` zu einem der beiden `r0`-Argumente. Beide Calls erhalten `fp-1324`, welches WP-153 beim Eintritt in `0x33F5D4` als `r2` zeigte. Daraus folgt nur Gleichheit der statischen Adresse, nicht der Inhalt des lokalen Speichers.

Der bounded GNU objdump-Fallback dekodierte 167 Instruktionen von `0x33F5D4` bis `0x33F86C`; das vollständige rohe Ergebnis liegt in `disassembly.raw.txt`, jede Instruktion mit VMA, abgeleitetem Datei-Offset und Maschinenwort in `instructions.tsv`. Funktionsgrenzen sind nicht durch einen Ghidra-Dossierbefund belegt. Der exakte REA-Hashfilter ergab null retained Records; es gibt folglich keine REA-Evidence-ID für diese Lane. Der bekannte identische hängende Import wurde gemäß Aufgabenhinweis nicht wiederholt.

## Eingaben und Provenienz

| Eingabe | SHA-256 | Verwendung |
|---|---|---|
| `codesys3`, 5.181.396 Bytes | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | Disassembly-Ziel |
| WP-XE164-153 `report.md` | `fab40a1259ae5fe2c9a0d3e692f61f6c60486353619fab5a71bf6bc420b39489` | Eintrittsregister / lokaler Setup-Beleg vor `0x33F5D4` |
| WP-XE164-154 `direct-callers.csv` | `ce281e7ab15b0277a2be52a1d00a089e2f8945dfb1a69c6b782fc72149548e5c` | Identität und Callsite-Adressen; Fensterzusammenfassung |

WP-153 belegt für den Setting-Call `0x33F5D4` beim Eintritt: `r0=0x00345440`, `r1=0x003afe34`, `r2=fp-1324`, `r3=fp-1356`, `[sp]=0x003afe4c`, `[sp+4]=r8` (Inhalt von `r8` dort nicht bestimmt). Diese unmittelbare Setup-Beobachtung liegt vor dem hiesigen Bereich. Die Stackwerte werden hier als Maschinenwerte referenziert; keine API-Signatur oder Feldsemantik wird behauptet.

## Begrenzte Instruktions- und CFG-Tabelle

Die vollständige chronologische Instruktionstabelle ist `instructions.tsv`; `disassembly.raw.txt` ist das unveränderte GNU objdump-Ergebnis für `[0x33F5D4, 0x33F870)`. Die Kontrollflusskanten innerhalb dieses Bereichs, soweit sie die beiden Calls erreichen oder von ihnen ausgehen:

| Quelle | Kante / Bedingung | Ziel / Ergebnis |
|---|---|---|
| `0x33F5D4` | `bl` | `0x33CE44`; Rückkehr zur nächsten Instruktion `0x33F5D8` (Call-Körper ausgeschlossen) |
| `0x33F600` | `bl` | `0x304B64`; Rückkehr `0x33F604` (Call-Körper ausgeschlossen) |
| `0x33F634` | `bl` | `0x33CE44`; Rückkehr `0x33F638` (Call-Körper ausgeschlossen) |
| `0x33F63C` | `beq` bei `r0 == r8` | `0x33F808` → Callsetup `0x33F80C..0x33F828` → `SysDirOpen` `0x33F82C` |
| `0x33F63C` | Fallthrough bei `r0 != r8` | `0x33F640..0x33F6C8` → `SysDirOpen` `0x33F6CC` |
| `0x33F6D8` | `beq` bei `r0 == -1` | `0x33F7D8` → epilog/return block `0x33F7DC..0x33F7E0` |
| `0x33F6D8` | Fallthrough bei `r0 != -1` | `0x33F6DC..` weiterer Block innerhalb Scope |
| `0x33F808` | fallthrough | zweites Setting-abhängiges Setup und Call `0x33F82C` |
| `0x33F838` | `beq` bei `r0 == -1` | `0x33F640`; führt zu erstem `SysDirOpen`-Lane und kann zurück in dessen Logik gelangen |
| `0x33F838` | Fallthrough bei `r0 != -1` | `0x33F83C..0x33F86C`; `0x33F868` kann zu `0x33F92C` außerhalb der Grenze springen |
| `0x33F680`, `0x33F6AC` | lokale bedingte Kanten | `0x33F6B0` wird bei beiden einschlägigen Ausgängen erreicht |
| `0x33F6FC`, `0x33F750`, `0x33F75C`, `0x33F76C` | bedingte Back-edges | `0x33F6FC` oder nächster Block `0x33F760`; keine Kante muss für den ersten Call erneut `r0` definieren |

Vollständige branch-/call-Zielinventur für das bounded Listing:

| VMA | Opcode / Bedingung | internes Ziel / Fallthrough | Scope-Hinweis |
|---:|---|---|---|
| `0x33F5D4` | `bl` | Call-Ziel `0x33CE44`; Rückkehr `0x33F5D8` | Call-Körper ausgeschlossen |
| `0x33F600` | `bl` | Call-Ziel `0x304B64`; Rückkehr `0x33F604` | Call-Körper ausgeschlossen |
| `0x33F634` | `bl` | Call-Ziel `0x33CE44`; Rückkehr `0x33F638` | Call-Körper ausgeschlossen |
| `0x33F63C` | `beq`, `r0 == r8` | Ziel `0x33F808`; sonst `0x33F640` | Zwei SysDirOpen-Lanes |
| `0x33F64C` | `beq`, `r0 == 0` | Ziel `0x33F7E4`; sonst `0x33F650` | lokaler return/epilogzweig |
| `0x33F680` | `beq` | Ziel `0x33F6B0`; sonst `0x33F684` | lokaler Kontrollfluss vor Call 1 |
| `0x33F6AC` | `bne` | Ziel `0x33F688`; sonst `0x33F6B0` | Schleifenrückkante |
| `0x33F6CC` | `bl` | Call-Ziel `SysDirOpen`; Rückkehr `0x33F6D0` | erster Zielcall |
| `0x33F6D8` | `beq`, `r0 == -1` | Ziel `0x33F7D8`; sonst `0x33F6DC` | testet Call-Returnwert |
| `0x33F6F8` | `b` | Ziel `0x33F718` | lokaler unbedingter Sprung |
| `0x33F70C` | `bl` | Call-Ziel `SysDirRead`; Rückkehr `0x33F710` | Körper ausgeschlossen |
| `0x33F714` | `bne` | Ziel `0x33F7D0`; sonst `0x33F718` | lokaler Zweig |
| `0x33F720` | `bl` | Call-Ziel `0x30463C`; Rückkehr `0x33F724` | Körper ausgeschlossen |
| `0x33F72C` | `beq` | Ziel `0x33F740`; sonst `0x33F730` | lokaler Zweig |
| `0x33F734` | `bl` | Call-Ziel `0x30463C`; Rückkehr `0x33F738` | Körper ausgeschlossen |
| `0x33F73C` | `beq` | Ziel `0x33F760`; sonst `0x33F740` | lokaler Zweig |
| `0x33F750` | `bne` | Ziel `0x33F6FC`; sonst `0x33F754` | Schleifenrückkante |
| `0x33F75C` | `bne` | Ziel `0x33F6FC`; sonst `0x33F760` | Schleifenrückkante |
| `0x33F76C` | `bne` | Ziel `0x33F6FC`; sonst `0x33F770` | Schleifenrückkante |
| `0x33F77C` | `bl` | Call-Ziel `0x7BA74`; Rückkehr `0x33F780` | Körper ausgeschlossen |
| `0x33F78C` | `bl` | Call-Ziel `0x7AC58`; Rückkehr `0x33F790` | Körper ausgeschlossen |
| `0x33F79C` | `beq` | Ziel `0x33F984` außerhalb; sonst `0x33F7A0` | Grenze notiert, nicht expandiert |
| `0x33F7A8` | `bl` | Call-Ziel `0x7BDE0`; Rückkehr `0x33F7AC` | Körper ausgeschlossen |
| `0x33F7B4` | `bcs` | Ziel `0x33F948` außerhalb; sonst `0x33F7B8` | Grenze notiert, nicht expandiert |
| `0x33F7C4` | `bl` | Call-Ziel `0x7B804`; Rückkehr `0x33F7C8` | Körper ausgeschlossen |
| `0x33F7D4` | `bl` | Call-Ziel `0x242048`; Rückkehr `0x33F7D8` | Körper ausgeschlossen |
| `0x33F82C` | `bl` | Call-Ziel `SysDirOpen`; Rückkehr `0x33F830` | zweiter Zielcall |
| `0x33F838` | `beq`, `r0 == -1` | Ziel `0x33F640`; sonst `0x33F83C` | Rückkante in den bounded Bereich |
| `0x33F850` | `b` | Ziel `0x33F870` | exklusive Stopgrenze; nicht expandiert |
| `0x33F864` | `bl` | Call-Ziel `0x242090`; Rückkehr `0x33F868` | Körper ausgeschlossen |
| `0x33F86C` | `bne` | Ziel `0x33F92C` außerhalb; sonst `0x33F870` | Grenze notiert, nicht expandiert |

Die Vorwärtswege zu beiden Call-Sites sind durch die branch- und fallthrough-Kanten oben abgedeckt. Der Bereich enthält auch Schleifen und andere Folgepfade; außerhalb liegende Ziele (etwa `0x33F948`, `0x33F984`, `0x33F92C`) wurden nicht verfolgt. Ein statischer May-Reachability-Pfad ist belegt; es wird keine tatsächliche Ausführung behauptet.

## Callargumente und lokale Quellen

Registerquellen sind unmittelbar vor `bl` ausgewertet. `fp` bezeichnet hier `r11`. `r8`/`r6` tragen Registerwerte, deren konkrete Inhalte aus dem begrenzten Fenster nicht bestimmt sind.

| Callsite | `r0` | `r1` | `r2` | `r3` | Sichtbare Stackargumente bei Call |
|---|---|---|---|---|---|
| `0x33F6CC` | lokal: `fp-1324` (`r11-0x52c`), gebildet aus `fp-1312` minus `12` | lokal: `fp-556` (`r11-0x22c`) | direkte Konstante `255` | lokal: `fp-812` (`r11-0x32c`) | `[sp]=fp-1360` (`r11-0x550`), geschrieben bei `0x33F6BC`; `[sp+4]=r8`, geschrieben bei `0x33F62C` |
| `0x33F82C` | lokal: `fp-1324` (`r11-0x52c`), gebildet aus `fp-1312` minus `12` | lokal: `fp-300` (`r11-0x12c`) | dynamisch/behalten: `r6` | lokal: `fp-1344` (`r11-0x540`) | `[sp]=fp-1352` (`r11-0x548`), geschrieben bei `0x33F820`; `[sp+4]=r8`, zuletzt geschrieben bei `0x33F62C` |

An beiden SysDirOpen-Callsites wird `[sp]` unmittelbar neu gesetzt; der letzte sichtbare explizite Store nach `[sp+4]` ist `r8` bei `0x33F62C`. Davor setzte der Setting-Call `0x33F634` `[sp]=0x00370440` und `[sp+4]=r8`; anschließend wird `[sp]` für die jeweiligen SysDirOpen-Calls neu gesetzt. Mögliche Speicherwirkungen der aufgerufenen Funktionen auf aliasierte Caller-Stackadressen sind außerhalb dieses Ausschnitts nicht bestimmbar.

### Werte nach `0x33F5D4` und lokale Status-/Pufferreferenzen

| VMA | Instruktionseffekt | Herkunft / Folge |
|---:|---|---|
| `0x33F5D8..0x33F5E0` | `r0=fp-1068`; `r1=r6` | Der Rückgabewert des Calls bei `0x33F5D4` wird durch Frame- bzw. beibehaltene Registerwerte überschrieben. |
| `0x33F5E4..0x33F5F0` | `r3=0x003AFE6C`; `r2=0x00348EFC` | Direkte MOVW/MOVT-Adressen; keine Aussage über Inhalt oder Bedeutung. |
| `0x33F5F4` | `[sp]=r5` | Das Stackslot wird für den Call bei `0x33F600` neu belegt. |
| `0x33F5F8`, `0x33F5FC` | `[fp-1352]=r4`; `[fp-1348]=r6` | Lokale Speicherwrites vor `0x33F600`; die Inhalte von r4/r6 bleiben dynamisch. |
| `0x33F600` | `bl CMUtlsnprintf`; vor dem Call: `r0=fp-1068`, `r1=r6`, `r2=0x00348EFC`, `r3=fp-1348`, `[sp]=r5` | Call-Körper und Effekte sind nicht untersucht; der lokale Zeiger `fp-1348` wird als Registerargument übergeben. |
| `0x33F604..0x33F630` | `r3=fp-1348`, `r1=fp-1068`, `r2=0x00370440`, `r0=0x00345440`; `[sp]=0x00370440`, `[sp+4]=r8`; danach `r2=fp-812` | Vorbereitung des zweiten Setting-Calls. |
| `0x33F634` | `bl SettgGetStringValue`; Rückkehrwert `r0` wird bei `0x33F638` mit `r8` verglichen | Dieser Vergleich bestimmt die statischen May-Reachability-Pfade. Inhalt und Semantik der aufgerufenen Funktion sind ausgeschlossen. |
| `0x33F640`, `0x33F648` | `r0=[fp-1352]`; danach `[fp-1360]=r0` | Der Wert aus der lokalen Zelle `fp-1352` wird in die lokale Statuszelle kopiert; Inhalt unbekannt. |
| `0x33F650..0x33F67C` | Zugriff über globale Adresse `0x00602130`, Registervergleiche und -writes | Kein frame-relativer Zugriff auf `fp-1324` oder `fp-1356` sichtbar. |
| `0x33F6B0..0x33F6C8` | `r0=fp-1324`; `r3=fp-1360` wird bei `0x33F6BC` an `[sp]` geschrieben; `r1=fp-556`; `r3=fp-812`; `r2=255` | Vollständige Setupfolge für den ersten SysDirOpen-Call. Das finale `r3` überschreibt den zuvor gesetzten r3-Wert; `[sp]` behält fp-1360. |
| `0x33F6CC` | `bl SysDirOpen` | `r0` enthält beim Call-Eintritt die lokale Adresse fp-1324. Der Rückgabewert in `r0` wird bei `0x33F6D4` in `r8` übernommen. |
| `0x33F6F4` | `[fp-1360]=21` | Die lokale Statuszelle wird mit der direkten Konstante überschrieben. |
| `0x33F700..0x33F70C` | `r3=fp-812`; `r1=fp-556`; `r2=255`; `r0=r8`; `bl SysDirRead` | Der Registerwert `r8` und die lokalen Argumentzeiger werden weiterverwendet. |
| `0x33F7CC`, `0x33F7D8` | `[fp-1360]=0`; anschließend `r0=[fp-1360]` | Die Statuszelle erhält die Konstante 0 und wird danach als späterer Rückgabewert gelesen. |
| `0x33F808..0x33F828` | `r0=fp-1324`; `r2=r6`; `[sp]=fp-1352`; `r1=fp-300`; `r3=fp-1344` | Vollständige Setupfolge für den zweiten SysDirOpen-Call. |
| `0x33F82C` | `bl SysDirOpen`; bei `0x33F834` `r6=r0` | Derselbe lokale Zeiger fp-1324 erreicht `r0`; der Rückgabewert in `r0` wird in `r6` gehalten. |

Im begrenzten disassemblierten Bereich gibt es keine direkte `ldr/str`-Referenz zu `[fp-1324]` oder `[fp-1356]`; beide erscheinen als berechnete Zeiger/Argumentwerte, nicht als direkt gelesene oder geschriebene Slotadressen. Der Inhalt von fp-1324 kann durch den ausgeschlossenen Setting-Call, durch Alias-Schreibzugriffe oder durch nicht sichtbare Vorgeschichte beeinflusst sein; das ist mit diesem Scope nicht auflösbar. Für fp-1356 ist nach dem Setup am ersten Call keine erneute explizite Verwendung in diesem Bereich decodiert. Als frame-relative lokale Statusadresse in den SysDirOpen-Stackslots wird stattdessen `fp-1360` beim ersten Call und `fp-1352` beim zweiten übergeben.

## Quellenklassen und alternative Erklärungen

| Klasse | Beobachtung |
|---|---|
| Direkte Konstante | `r2=255` vor `0x33F6CC`; direkte MOVW/MOVT-Adressen `0x003AFE6C`, `0x00348EFC`, `0x00370440` im vorbereitenden Code; in der hier gefragten r0-Herkunft ist keine direkte Konstante. |
| Lokale Adresse | `r0=fp-1324` an beiden Calls; `r1/r3` und Stackargumente sind ebenfalls Frame-Adressen gemäß Tabellen. |
| Dynamisch/behalten | `r2=r6` an `0x33F82C`; die Branchbedingung `r0==r8` nach dem Settings-Call nutzt ein unbekanntes Registerargument/Rückgabe; Statuswerte aus `[fp-1352]` sind unbekannt. |
| Vorheriger Setup-Kontext | Bei `0x33F5D4` wurde `[sp]=0x003AFE4C` im WP-153-Befund als direkter Pfadzeiger beobachtet; der zugehörige frühere Pfad liegt außerhalb dieses Disassembly-Scope. Diese Konstante wird nicht als `r0` an SysDirOpen weitergetragen. |

Alternative Erklärung: `fp-1324` kann zur Laufzeit Inhalte enthalten, die von aufgerufenen Routinen oder aliasierten Zeigern erzeugt wurden. Ein direkter Zeigerwert an `r0` beweist weder Stringinhalt noch, dass der Wert aus `0x33F5D4` als Return stammt. Auch das `r0==r8`-Prädikat wird hier nur als Registervergleich beschrieben; keine Default-/Fallback-Semantik wird behauptet.

## REA und Rohbelege

REA 6.5.0 `binary_session`: keine offene Binärdatei; Ghidra 12.1.4 verfügbar. Hashgefiltertes `get_evidence_bundle(detail="summary")` für den exakten Zielhash: null retained Records, null Evidence-IDs. Ergebnisdatensatz in `rea-evidence.json`. WP-153 und WP-154 sind benannte Eingabeberichte, aber keine REA-Evidence-IDs. Die Instruktions-Rohbelege sind daher der reproduzierbare lokale objdump-Output. Es wurde kein neuer identischer Ghidra-Import durchgeführt.

## Validator und Status

`python3 validate.py` prüft den Zielhash, Tabellenbereich, ersten/letzten Instruktionswert, genaue zwei Call-Sites und erforderliche Dateien. `sha256sum -c SHA256SUMS` validiert die Paketdateien.

| Prüfung | Status | Umfang |
|---|---|---|
| Eingabehash / Bytezahl | VERIFIZIERT | exact hash, 5.181.396 Bytes |
| begrenzte objdump-Instruktionen | PASS | 167 Zeilen von `0x33F5D4` bis `0x33F86C`; Stopgrenze exklusiv `0x33F870` |
| CFG und Argumentdatenfluss | VERIFIZIERT | statische bounded May-Reachability und sichtbare Instruktionsquellen |
| REA retained Evidence | NOT_RUN | kein passender Record; keine REA-ID |
| Laufzeit/Hardware/VM | NOT_RUN | ausgeschlossen |
| Validator | PASS | nach `python3 validate.py` in `validator-result.txt` |
| SHA-256-Manifest | PASS | `sha256sum -c SHA256SUMS` |

Verbleibende Unsicherheit: Funktionsgrenzen außerhalb des begrenzten Listings, Call-Körperwirkungen, tatsächlicher lokaler Pufferinhalt, Alias-/Seiteneffekte, Eingangsregisterwerte und erreichter Laufzeitpfad. Workerbericht; keine unabhängige Gegenprüfung und keine Hardwarebehauptung.

Paketdateien: `instructions.tsv` (alle Instruktionen mit Koordinaten), `disassembly.raw.txt` (Rohdisassembly), `rea-evidence.json` (hashgefilterter REA-Befund ohne passende IDs), `tool-versions.txt`, `validator-result.txt`, `generate.py`, `validate.py` und `SHA256SUMS`. SHA-256 aller Inhaltsdateien außer dem selbstreferenziellen Manifest stehen in `SHA256SUMS`.
