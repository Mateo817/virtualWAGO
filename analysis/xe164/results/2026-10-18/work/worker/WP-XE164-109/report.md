> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-109 — PARAM-Xref bei Ghidra `0x14cdc`

## Ergebnis

**VERIFIZIERT:** Die einzige angefragte materialisierte PARAM-Referenz an `0x14cdc` zeigt auf die globale Objektzelle `pfIoMgrConfigGetParameterValuePointer`. Die Instruktion lädt deren Adresse aus der GOT-Zelle und stellt diesen Wert als `r1` für den unmittelbar folgenden indirekten Call `blx r6` bei `0x14cec` bereit. Der Call erhält außerdem als `r0` den String `IoMgrConfigGetParameterValuePointer` sowie drei Nullargumente (`r2`, `r3`, `[sp]`) auf dem erfolgreichen Vorgängerpfad.

Der Call ist als Setup-/Resolver-Muster statisch beschreibbar: Ghidra-Pseudocode zeigt den Aufruf `(*DAT_0002a1c0)("IoMgrConfigGetParameterValuePointer", &pfIoMgrConfigGetParameterValuePointer, 0, 0, 0)`. Die aufgerufene Funktion selbst ist **nicht** statisch auf einen benannten Codepunkt aufgelöst: REA meldet für `0x14cec` einen berechneten Call ohne Zielreferenz. `DAT_0002a1c0` wird im selben Pseudocode aus einem Aufruferfeld bei `param_1 + 0x620`, Offset `+0x34`, geladen. Das ist eine beobachtete Darstellung der Ghidra-Dekompilierung, kein rekonstruierter Funktionsvertrag.

Der unmittelbare Ergebnisguard ist exakt: `0x14cf0: subs r3,r0,#0x0`, danach `0x14cf4: bne 0x15314`. Ein von null verschiedener Rückgabewert verzweigt zum Fehler-/Abbruchpfad; nur bei null läuft die Folge weiter. Der Eintritt in `0x14cdc` ist seinerseits durch den vorherigen Guard `0x14ccc: bne 0x15314` auf den Erfolgsfall des vorherigen Calls beschränkt.

## Beobachtungen und Koordinaten

Zielartefakt: `libIoDrvKbus.so.0.0.1`, 38.584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`. Provider Ghidra 12.1.4, REA `rea-agents` 6.5.0, Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

Die Adressräume sind getrennt. In diesem LOAD liegt die Ghidra-Adresse um `0x10000` über der ELF-Link-VA; Ghidra-Quellbyteabbildung und GNU-Disassembly bestätigen für den ausgewählten Textbereich denselben Datei-Offset wie ELF-VA. Der Laufzeit-Load-Bias ist unbekannt.

| Gegenstand | Ghidra-Adresse | ELF-Link-VA | Datei-Offset | Nachweis |
|---|---:|---:|---:|---|
| PARAM-Load `ldr r1,[r5,r2]` | `0x14cdc` | `0x4cdc` | `0x4cdc` | REA-Offsetabbildung: 19.676 (`0x4cdc`); erster ELF-LOAD deckt VA/Offset ab 0 ab |
| indirekter Call `blx r6` | `0x14cec` | `0x4cec` | `0x4cec` | REA-Offsetabbildung: 19.692 (`0x4cec`); GNU-Disassembly |
| String `IoMgrConfigGetParameterValuePointer` | `0x186c3` | `0x86c3` | `0x86c3` | REA-Offsetabbildung: 34.499 (`0x86c3`); Bytes aus Ghidra-Speicher gelesen |
| GOT-Zelle mit Relocation | `0x290c4` | `0x190c4` | `0x90c4` | `.got` beginnt bei ELF-VA `0x19000`, Datei-Offset `0x9000`; Ghidra-Speicherbytes `24 a2 02 00` |
| benannte PARAM-Objektzelle | `0x2a224` | `0x1a224` | nicht dateigebunden (`.bss`, `NOBITS`) | Dynsym `OBJECT`, Größe 4; Relocationziel |
| Resolver-Funktionszeigerzelle laut Pseudocode | `0x2a1c0` | `0x1a1c0` | nicht dateigebunden (`.bss`) | `0x14cd8` liest `[r4,#0xfc4]`; Pseudocode weist Zuweisung aus `iVar1 + 0x34` aus |

Ghidra-Instruktionsfolge, ARM-Programmraum:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

`read_bytes(0x290c4, 4)` liefert `24a20200`; little-endian ist das `0x2a224`, die Ghidra-Adresse der Objektzelle. GNU ARM Binutils 2.44 bestätigt unabhängig die ELF-Relocation `r_offset 0x190c4`, `R_ARM_GLOB_DAT`, Dynsym #44, `pfIoMgrConfigGetParameterValuePointer`, Symbolwert `0x1a224`. Der String an Ghidra `0x186c3` beginnt mit den Bytes für genau `IoMgrConfigGetParameterValuePointer\0`.

Im ARM-Aufrufzustand ist `r0` der Stringzeiger, `r1` die Objektzellenadresse. Auf dem Pfad, der `0x14ccc` passiert, ist `r3` nach `subs` null; daher setzt `0x14ce4` `r2=0` und `0x14ce8` legt das fünfte Nullargument auf `[sp]` ab. `r3` bleibt null als viertes Argument. Dies beschreibt nur die unmittelbare Instruktionsfolge und Register-/Stackübergabe; es behauptet keine API-Signatur.

REA-Evidence-Anker im Bundle: PARAM/GOT-Xref an `0x14cdc` `ev_90484c605cb9b006ae7afe2aa752f6d0654ded6d0092aacfe559bd88dfbd23f6`; Codezellen-Load `0x14cd8` `ev_23e8e1560c3609e0f685ad2cb49fd5b42c8eda6b97e27b4fd97465bd0f5bc7aa`; Stringparameter `0x14ce0` `ev_b987b42a9b7b5ce8d1d31b0e78247d2edc8bfc5532b571fc2fb31891646a03ec`; indirekter Call `0x14cec` `ev_c5a83e45a1a35d06f258a5da9edc72bcec5c34ad2baf20513c935f4adeed30c8`; ungelöster Callee `ev_755d816f5a13e9ff7d1348a753af7ef203d1069e32d9d3e3c2263ea55a90448e`; Register-/Stackargumente `ev_db06dbb99cf14cd44ab80090f03217628f3534f1a79003186622043736bdf818` und `ev_371e42cdfd2775692aae87b53e467f95f880bff0aae1b272d53382b524a6f6d3`; Aufruf-Pseudocode und Slotdefinition `ev_6e0a9bd90e8763865f0c8924ae68ef34df7e6a7fbb810ee2b0810ad237d01d6c`; Rückgabeprüfung/Guard `ev_75179d26f0138b2c1f99952100d2dd7e48fde0d69a583b4f4f1562c77a74722e` / `ev_ca9490d07f2a65e08a82c360a855ea47270bb96d5e09a633048d8df736b08f57`; GOT-Bytes `ev_416406555dd741a8129708997f511f96322f38ead5a11f69b0da3b963b4cdc9b`; Stringbytes `ev_7fc7604809a75d17383fd68ff97a712835fdab4b02857af13de5079cb0f97313`; Dateiabbildungen für PARAM, Call und String `ev_fa4dd43e598cfb512fd6360342822e0e5469cb262dd9e4d60fae0f0ab890fef5`, `ev_1485df594cb7592e5b13f98d01e5672470a0a58545938da6f2b00f95d6d8e92b`, `ev_45fec5a20beefe205d710a87ee7231900af1cf894843534498270fbb96679c90`. Der vollständige Procedure-Pseudocode wurde nur als lokales Bindungsstück genutzt; Procedure-Evidence `ev_7e3f1552d56d71cb103353676196832c54caa65b25313f5768d4804898b2102e` bindet `0x14cdc` an `IoDrvKbus_Init`.

## Status, Alternative und Unsicherheit

- **VERIFIZIERT:** Ghidra markiert an `0x14cdc` das PARAM-Ziel `0x2a224` und einen READ auf `0x290c4`; die GOT-Relocation bindet im ELF zum Dynsym-Objekt `pfIoMgrConfigGetParameterValuePointer`.
- **VERIFIZIERT:** Ghidra-Pseudocode zeigt den benannten String plus Adresse dieser globalen Zelle als erste zwei Argumente des Calls über `DAT_0002a1c0`; die nächsten drei beobachteten Argumente sind auf dem erfolgreichen Pfad null.
- **VERIFIZIERT:** Der Call-Rückgabewert wird direkt auf null geprüft; nonzero verzweigt nach `0x15314`.
- **OFFEN:** Der konkrete Laufzeitwert der Zelle `DAT_0002a1c0`, das Ziel von `blx r6`, tatsächlicher Aufruf und die konkrete Laufzeitadresse der BSS-Zelle. REA löst den berechneten Call nicht auf; BSS hat keinen initialisierten Dateiinhalt und der Load-Bias ist nicht bekannt.
- **Alternative:** Die bekannte String-/Zelladresse legt einen Resolver-/Setup-Zweck nahe. Die ausgeführte Funktion könnte aber eine andere Implementierung sein, die dieselben Argumente annimmt; Symbolname und Pseudocode-Cast belegen allein weder Semantik noch ABI-Vertrag.
- **Unsicherheit:** Ghidra liefert für Operandtokens keine effektive Basis-/Indexzerlegung. Für genau dieses Fenster wurde die lokale GNU-ARM-Disassembly nach dem belegten ELF-/Ghidra-Adressversatz ergänzt. Die Interpretation der Literal-/Relocationkette hängt daher zusätzlich an der Ghidra-GOT-Referenz, den Loaderbytes, GNU-Relocation und der ELF-Symboltabelle. Es wurde kein Ziel ausgeführt.

## Methode und Tests

REA-first: Ziel mit Ghidra geöffnet; `inspect_native_instruction` im begrenzten Bereich `0x14c80..0x14d3c`, dazu gezielt Xrefs auf `0x2a224`, Procedure-Auflösung, Pseudocode der umgebenden Procedure, Zielauflösung des Calls, Ghidra-Speicherbytes und Quellbyteabbildungen. Pseudocode wurde nur für die unmittelbare Call-Zuordnung und die Definition des Callee-Slots herangezogen.

REA-Lücke: Die Operanddarstellung weist die effektive PC-/Registeradressierung nicht aus. Daher wurde nach der REA-Analyse ein begrenzter Fallback mit GNU ARM Binutils 2.44 verwendet: `objdump -d -w --start-address=0x4c80 --stop-address=0x4d40`, `readelf -lW`, `readelf -SW`, `readelf -rW` (gefiltert auf `0x190c4`) und `readelf -sW` (gefiltert auf den benannten Dynsym-Eintrag). Es gab keinen Netzwerkzugriff und keine Ausführung des Binaries.

| Prüfung | Status | Ergebnis |
|---|---|---|
| Zielhash | PASS | Stimmt mit dem vorgegebenen SHA-256 überein. |
| REA-Analyse mit Ghidra | PASS | Provider 12.1.4, Profil wie oben; kanonisches Bundle mit 59 Records und 0 Unknowns. |
| Semantischer Validator | PASS | Prüft Bundle-Identität, PARAM-/GOT-Referenzen, Callargumente aus Instruktionen und Pseudocode, Guards sowie Dateiabbildungen. |
| GNU ARM Fallback | PASS | Binutils 2.44; nur Callfenster, LOAD-/Sektionsmapping, Relocation und passendes Dynsym geprüft. |
| Runtime-/Firmware-/Hardwarebeobachtung | NOT_RUN | Offline statische Analyse gemäß Auftrag. |

## Erzeugte Dateien

- `rea-bundle.json` — vollständiger kanonischer REA-Evidence-Export; 59 Datensätze, 0 Unknowns.
- `validate_semantics.mjs` — semantischer Konsistenzvalidator für den Export.
- `report.md` — dieser Befundbericht.
- `SHA256SUMS` — SHA-256 der drei obigen Dateien.
