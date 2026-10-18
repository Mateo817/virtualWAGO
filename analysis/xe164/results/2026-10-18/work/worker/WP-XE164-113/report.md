> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-113 — Eingabe-zu-Slot-Pfad für Call `0x14CEC`

## Ergebnis

**VERIFIZIERT:** In `IoDrvKbus_Init` ist der statisch belegte Schreibpfad zum von Call `0x14CEC` gelesenen Zielslot:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Damit werden die bisher geprüften Offsets `param1 + 0x620` und danach `+0x34` durch konkrete Instruktionen bestätigt. `0x2A1C0` ist der beobachtete gemeinsame Store-/Load-Ort. `+0xFC4` ist der Displacement, mit dem die Funktion diesen Ort über zwei unterschiedliche Register anspricht; es ersetzt nicht die Eingabeoffsets. Das belegt einen statischen Eingabe-zu-Slot-Pfad, aber weder die Semantik eines Feldes noch einen vollständigen Strukturvertrag.

**OFFEN:** REA löst `blx r6` als berechneten Call ohne Zielreferenz auf. Der statische Slot wird in `.bss` geschrieben und später gelesen. Ob frühere indirekte Aufrufe den Slot zur Laufzeit verändern oder welcher Wert beim Call tatsächlich geladen wird, ist mit dieser rein statischen Evidenz nicht entschieden. Es wurde kein Code ausgeführt.

## Exakte Instruktionen und Registerfluss

REA ordnet den Bereich der Procedure `IoDrvKbus_Init` am Ghidra-Einstieg `0x147FC` zu. Die Procedure-Disassemblierung bindet `param_1` an ARM-Eingaberegister `r0`; die ersten Instruktionen vergleichen `r0` mit null. Die relevante Sequenz lautet:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Die Referenzmetadaten von `0x14910` melden `WRITE -> 0x2a1c0`; jene von `0x14cd8` melden `READ -> 0x2a1c0`. Bei `0x14cec` klassifiziert Ghidra den Flow als `COMPUTED_CALL`, ohne direkte Zieladresse oder Call-Referenz. Für den hier relevanten Datenfluss ist `r2` zuerst der aus `[r3,#0x34]` geladene Eingabewert; vor dem Call wird `r2` dann durch `cpy r2,r3` neu gesetzt. Der Zielzeiger selbst kommt über `ldr r6,[r4,#0xfc4]` aus dem gemeinsamen Slot.

## Guards und Erreichbarkeit

- **VERIFIZIERT:** Bei `r0 == 0` setzt `0x14880` `r3=2` und `0x14884` springt zum gemeinsamen Rückkehr-/Fehlerpfad `0x15314`. Der Datenpfad zum Slot liegt daher auf dem Nichtnull-Pfad des Eingabearguments.
- **VERIFIZIERT:** Unmittelbar nach dem Call prüft `0x14cf0` den Rückgabewert in `r0`; `0x14cf4` verzweigt bei Nichtnull nach `0x15314`.
- **VERIFIZIERT:** Der Eintritt in `0x14cdc` setzt voraus, dass der davorliegende Call bei `0x14cc4` den Nullfall geliefert hat: `0x14cc8: subs r3,r0,#0x0`, `0x14ccc: bne 0x15314`. Auf dem Fallthrough ist `r3=0`; die Folgeinstruktionen kopieren diesen Wert nach `r2` und speichern ihn zusätzlich auf `[sp]`.

## Adressräume und Objekt

Zielbinary: `libIoDrvKbus.so.0.0.1`, 38.584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`. Ghidra verwendet RAM-Imagebasis `0x10000`; die ELF-Link-VA der gezeigten Textadressen ergibt sich hier aus Ghidra-Adresse minus `0x10000`. REA hat die Textadressen separat auf die Quelldatei abgebildet; für diese Text-LOAD-Adressen entsprechen ELF-Link-VA und Datei-Offset einander.

| Gegenstand | Ghidra-Adresse | ELF-Link-VA | Datei-Offset |
|---|---:|---:|---:|
| Load Eingabepointer `0x148e8` | `0x148e8` | `0x48e8` | `0x48e8` |
| Slot-Store `0x14910` | `0x14910` | `0x4910` | `0x4910` |
| Slot-Load `0x14cd8` | `0x14cd8` | `0x4cd8` | `0x4cd8` |
| indirekter Call `0x14cec` | `0x14cec` | `0x4cec` | `0x4cec` |
| gemeinsamer Slot | `0x2a1c0` | `0x1a1c0` | keine dateigebundenen Bytes |

REA listet den Slot innerhalb des uninitialisierten Ghidra-`.bss`-Blocks `0x291f8..0xecad8` (Endadresse exklusiv). Das ELF meldet `.bss` als `NOBITS`, Link-VA `0x191f8`, Größe `0xc38e0`; `0x1a1c0` liegt darin. Ein Datei-Offset für den initialisierten Laufzeitinhalt dieses BSS-Orts existiert nicht. Die Adresse ist ein Objekt-/Speicherort, nicht ein aus der Datei gelesener initialer Funktionszeiger.

## Bewertung der Ghidra-Hypothese

- **VERIFIZIERT:** `0x148e8` lädt den Wert an Eingabe-Offset `+0x620` in `r3`; `0x1490c` lädt aus diesem Wert an Offset `+0x34` nach `r2`; `0x14910` speichert diesen Wert an der Ghidra-Zieladresse `0x2a1c0`.
- **VERIFIZIERT:** `0x14cd8` lädt bei einem späteren Pfad denselben Ort `0x2a1c0` nach `r6`; `0x14cec` ruft den Inhalt dieses Registers indirekt auf.
- **VERIFIZIERT:** Die Ghidra-Pseudocodezeilen `iVar1 = *(int *)(param_1 + 0x620)` und `DAT_0002a1c0 = *(code **)(iVar1 + 0x34)` stimmen mit der Instruktionskette überein. Die Offsets werden als reine Speicherzugriffe bestätigt.
- **OFFEN:** Es ist nicht belegt, dass das bei `0x14cec` geladene Wort weiterhin exakt dem bei `0x14910` gespeicherten Eingabewert entspricht. Zwischen Store und Load liegen weitere indirekte Calls; deren Schreib-/Aliaswirkung auf globalen Speicher ist außerhalb dieses Arbeitspakets und bleibt ungeklärt.

**Alternative Erklärung:** Die Offsets `+0x620` und `+0x34` können lediglich beobachtete Speicherfeldpositionen in einem aufrufseitig gelieferten Objekt sein. Der Code belegt weder deren Namen noch Zweck. Ebenso beweist der Slot-Load `0x14cd8` keine bestimmte Resolver-, Callback- oder API-Semantik. Eine frühere aufgerufene Funktion könnte den Slot überschrieben haben; es gibt hier keinen statischen Beleg dafür, dass dies geschieht.

## Evidence, Methode und Tests

REA-first mit REA `rea-agents` 6.5.0, Provider Ghidra 12.1.4, Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Das kanonische Bundle enthält 42 Records und 0 Unknowns. Wichtige Evidence-IDs:

- Procedure-Pseudocode: `ev_8f9c3853ed48db95d57752cad10b60780a6b45fbd84423dd0a0fc3b91790a45b`
- vollständige Instruktionsliste der `IoDrvKbus_Init`-Procedure: `ev_4ae4a73688ae48904c8bb85ffd1fa03e91650f31ff2f05c2c04d592934ded9a2`
- Eingabepointerload `0x148e8`: `ev_5a695a9a28c07bbc7b42320172ee346d4d37be75c1be1e46614204bfd31d1a5f`
- Feldload `0x1490c` und Slotstore `0x14910`: `ev_373845e4a460b860b286a810a0306387540390cdf32a1a6f2f863f04d324a276`, `ev_e8f1107ef0911dc1547057e8983210501da8be9bb757a3fab498d1a0aeab3007`
- Slotload `0x14cd8` und Call `0x14cec`: `ev_23e8e1560c3609e0f685ad2cb49fd5b42c8eda6b97e27b4fd97465bd0f5bc7aa`, `ev_c5a83e45a1a35d06f258a5da9edc72bcec5c34ad2baf20513c935f4adeed30c8`
- ungelöste Zielauflösung: `ev_755d816f5a13e9ff7d1348a753af7ef203d1069e32d9d3e3c2263ea55a90448e`
- Guard nach dem Call: `ev_75179d26f0138b2c1f99952100d2dd7e48fde0d69a583b4f4f1562c77a74722e`, `ev_ca9490d07f2a65e08a82c360a855ea47270bb96d5e09a633048d8df736b08f57`
- Dateiabbildungen `0x148e8`, `0x14910`, `0x14cec`: `ev_b23d9b4aa5f355ef72e5a7cdd44b87b9ef6817c94cfb1eee4196a78a3cb26e91`, `ev_4c3ec701899c73a3c7e542a066cca65c5887091a656e857da97a3a0371bca7d0`, `ev_1485df594cb7592e5b13f98d01e5672470a0a58545938da6f2b00f95d6d8e92b`
- Ghidra `.bss`-Block: `ev_2952335942560bdf6fa3ea2982035c9f8771409337dd9f727e216a84bb54e34b`

REA stellte für effektive Register-/Offsetoperanden nur Token bereit. Ein einmaliger, auf ELF-VA `0x4be0..0x4d20` und Program-/Sektionsabbildung begrenzter Fallback nutzte GNU ARM Binutils 2.44 (`arm-linux-gnueabihf-objdump -d -w --start-address=0x4be0 --stop-address=0x4d20`, `readelf -lW`, `readelf -SW`). Der Disassembler bestätigt im Callfenster die Reihenfolge und Offsets; die Loader-/Sektionsausgabe bestätigt ausführbaren ersten LOAD mit VA/Dateioffset-Basis 0 und `.bss` als `NOBITS`. Es wurde keine zweite Fallback-Ausführung durchgeführt.

| Prüfung | Status | Ergebnis |
|---|---|---|
| Zielidentität | PASS | Dateigröße und SHA-256 stimmen mit dem Arbeitspaket überein. |
| WP109-Kontextbundle | PASS | SHA-256 stimmt mit der autoritativen Auftragsvorgabe überein. |
| WP109-Kontextbericht | PASS | Lokaler Bericht ist durch den autoritativ bestätigten SHA-256 gebunden. |
| REA/Ghidra statischer Pfad | PASS | Eingabe-Load, Feld-Load, Store/Read derselben Zieladresse und Callsite sind in den exportierten Records verankert. |
| Calltarget-Auflösung | PASS | REA klassifiziert `0x14cec` als berechnet und ungelöst, mit null Zielkandidaten. |
| GNU ARM/readelf-Fallback | PASS | Einmalig und begrenzt gemäß beobachteter REA-Operandlücke. |
| Semantischer Validator | PASS | `validate_semantics.mjs` prüft Bundle-Identität, Instruktionskette, Guards, gemeinsame BSS-Adresse, Auflösungsstatus und Dateiabbildungen. |
| Runtime, Firmware, Gerät oder Hardware | NOT_RUN | Offlineumfang; kein Ziel wurde ausgeführt oder kontaktiert. |

## Eingabeintegrität und erzeugte Dateien

**PASS:** Zielbinary-Größe und SHA-256 stimmen mit der Auftragsvorgabe überein. **PASS:** Der WP109-Bundle-Hash ist `feac800252b47b22613f468c9724e1a5780d91a3eee5147c82e2dac98d5fd0fe`. **PASS:** Der für diesen Bericht verwendete WP109-Kontext ist an die lokale Datei `WP-XE164-109/report.md` mit SHA-256 `2b4e7d9e0aed9b409b94920fa199d632ae9c401975cf1d71654b715f35b69125` gebunden.

Auditprovenienz: Die ursprüngliche WP-XE164-113-Auftragsübergabe enthielt für den WP109-Bericht einen fehlerhaft rekonstruierten Erwartungshash. Die spätere autoritative Korrektur durch Root bestätigt, dass der lokale Bericht exakt `2b4e7d9e0aed9b409b94920fa199d632ae9c401975cf1d71654b715f35b69125` hat. Der in der ersten Fassung dieses Berichts genannte Ist-Hash `2b4e8b9e...` war zusätzlich ein Tippfehler. Es liegt damit keine ungeklärte Artefaktabweichung vor. Die REA-Auswertung und der inhaltliche Befund wurden nicht erweitert oder wiederholt.

| Datei | Inhalt | SHA-256 |
|---|---|---|
| `report.md` | Dieser Befundbericht; Prüfsumme steht in `SHA256SUMS`. | siehe `SHA256SUMS` |
| `rea-bundle.json` | Kanonischer REA-Evidence-Export; 42 Records, 0 Unknowns. | `dc5fc082c1e64000845a2c015c0e490e5a9d0159b323738ec48fbc361da8bec0` |
| `validate_semantics.mjs` | Lokaler Konsistenzvalidator für Export und WP109-Eingabeintegrität. | `d2909faa81d2ab79a3116fcd13dd7de0521217465bf652124aa86cfffd161c38` |
| `SHA256SUMS` | Prüfsummenmanifest für Bericht, Bundle und Validator. | manifestiert die drei Payload-Dateien; nicht selbst referenziert |
