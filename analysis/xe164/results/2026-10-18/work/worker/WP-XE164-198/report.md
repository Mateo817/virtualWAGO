> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-198 — Returnfluss der drei indirekten Positionsaufrufe

## Befund

**VERIFIZIERT:** Im exakten Instruktionskörper von `idk_IoDrvWriteOutputs` wird die Rückgabe bei ELF-VA `0x64cc` sofort auf null gegen nichtnull geprüft. Null führt in die Verarbeitung; nichtnull setzt `r0` lokal auf `2` und verzweigt zum einzigen Epilog. Die Rückgabe bei `0x6648` wird unmittelbar nach dem Call aus `r0` nach `r10` kopiert. Am gemeinsamen Abschluss wird der aktuelle `r10`-Wert auf null/nichtnull geprüft und als `r0=0` beziehungsweise `r0=2` ausgegeben. Die Rückgabe bei `0x6508` hat dagegen keinen lokalen Datenfluss: ihr `r0` wird im nächsten Befehl mit `r10` überschrieben.

**VERIFIZIERT:** Wenn mehrere für `r10` relevante Calls ausgeführt werden, ist die lokale Abbildung keine Akkumulation: Jeder `0x6648`-Call und auch der separate direkte Call bei `0x65fc` schreibt seinen Rückgabewert nach `r10`; ein späterer solcher Call kann damit einen früheren Wert ersetzen. Ein Pfad, der keinen dieser beiden Calls erreicht, behält lokal den zuletzt gesetzten `r10`-Wert. Die Bedeutung der numerischen Ausgaben wird nicht gedeutet.

**OFFEN:** Die drei indirekten Ziele sowie sämtliche nicht-Rückgaberegister- und Speichereffekte ihrer Callees sind nicht belegt. Insbesondere beweist das lokale Überschreiben des `r0` nach `0x6508` nicht, dass dieser Callee keinen anderen Effekt auf `r10` oder andere für den Ablauf relevante Zustände hat. Die Aussage „Rückgabe ignoriert“ bezieht sich ausschließlich auf dessen `r0`-Rückgabewert im Instruktionsstrom dieses Körpers.

## Identität und Adressabbildung

Eingabe ist `libIoDrvKbus.so.0.0.1`, ELF32 little-endian ARM, 38 584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` (**PASS**). REA/Ghidra meldet Image-Base `0x10000`; damit ist die beobachtete Ghidra-Adresse `0x164a8` die ELF-VA `0x64a8 + 0x10000`. `address_to_file_offset(0x164a8)` lieferte Datei-Offset `0x64a8`. Die Ghidra-FunctionManager-Range ist inklusiv `[0x164a8,0x16657]` (432 Bytes), entsprechend der hier verlangten ELF-Range `[0x64a8,0x6658)`.

Wiederverwendete Same-Hash-Evidence: WP-XE164-083, Evidence `ev_6194ece0a7a14aec68e5779961be70c5f415e05d5ad28a9fdb09d461539ae983`, bestätigt dieselbe Funktion und Abbildung. Frische, auf diesen Auftrag begrenzte REA-Abfragen sind `ev_d74d65af1ef2dd9abc6c9234afdecf81a783faea7c3f7f0b95a04c3ca662b2a5` (Image-Base/Abschnitte), `ev_691cfab32edcf1a11efe37507a25ed9bd9fa39fefde963b59b728d23e94ceaa6` (Adressmapping), `ev_6565099795a9fbdf17e00ecb7f3f5b9cb894ba1522543848202341dc4d566eaf` (vollständiges Funktionsdossier), `ev_3e45b1df3683cdd7b14458eb68e4c6d30f0b6e9231df089304c74c858bf2df96` (Instruktionslisting/CFG-Projektion) und `ev_07d492dc6d0c5c16f53a3eafc533e09b754c4626a694638620e60263b7adc11c` (432 initialisierte Bytes).

Der vollständige sessionlokale Evidence-Export liegt als `rea-evidence-bundle.json` vor (9 Records, 0 Unknowns). Das Bundle bindet Quellhash, Ghidra-Profil und aufgelistete Evidence-IDs.

Toolprofil: REA mit Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; GNU ARM objdump 2.44; Python 3.13.5. Der begrenzte GNU-Disassembly wurde ausschließlich für `[0x64a8,0x6658)` ausgegeben und stimmt mit dem REA-Instruktionsstrom überein. Opcodewörter in `call-flow.tsv` sind little-endian aus den zugehörigen Datei-Bytes validiert.

## Call-Rückgaben und unmittelbare Registerbelegung

Die Argumentspalten halten nur die unmittelbar vor den drei verlangten Calls sichtbaren Registerwerte fest. Sie bezeichnen keine API-Parameter oder Calling Convention. Registerwerte mit `*` sind der im Befehl sichtbare Speicherladeausdruck.

| ELF-VA / Ghidra-VA | Opcodewort | r0 | r1 | r2 | r3 | Wirkung der Call-Rückgabe im Körper |
|---|---:|---|---|---|---|---|
| `0x64cc / 0x164cc` | `0xe12fff33` | `*[r7+0x618]` | `0` | ursprüngliches Eintritts-`r2` (vorher in `r4` kopiert; kein lokales `r2`-Update vor diesem Call) | `*(*(r7+0x61c)+0x30)` | Bei `0x64d0` `r10=r0`, zugleich Test auf null/nichtnull. Nichtnull: `0x64d4` setzt `r0=2`, `0x64d8` verzweigt zum Epilog. Null: Verarbeitungspfad. **Propagiert und gemappt.** |
| `0x6508 / 0x16508` | `0xe12fff33` | `*[r7+0x618]` | `0` | pfadabhängiger Registerrest (bei direktem Leerlaufpfad das Eintritts-`r2`; nach Verarbeitung nicht lokal konstant) | `*(*(r7+0x61c)+0x40)` | Der Call-Rückgabewert in `r0` wird bei `0x650c` durch `subs r0,r10,#0` überschrieben, bevor ein lokaler Gebrauch erfolgt. **`r0`-Rückgabe ignoriert/überschrieben.** Danach `0x6510` setzt bei aktuellem `r10!=0` den Wert `1`; `0x6514` verschiebt links um eins: `r0=0` oder `r0=2`. |
| `0x6648 / 0x16648` | `0xe12fff3a` | `*[r6]` | `0` auf dem einzigen lokalen Eintrittspfad (das getestete `ANDS` bei `0x65ec` ergab null) | `*[r6+0x0c] + (uint16[r4+0x8] >> 3)` | `min_u(uint16[r4+0x0c] >> 3, r11)` | `0x664c` kopiert zurückgegebenes `r0` in `r10`. Wenn der Ablauf später die Abschlussprüfung erreicht, wird der zu diesem Zeitpunkt gültige `r10`-Wert auf `0`/`2` gemappt. Ein späterer `0x6648`- oder `0x65fc`-Call kann ihn lokal überschreiben. **Propagiert und gemappt.** |

Die vollständigen Register-Snapshots und Belegungsinstruktionen stehen in `call-flow.tsv`. Insbesondere sind `r2` und `r3` bei `0x6508` nicht als stabile Argumentliste ausgegeben, sondern als sichtbare Registerbelegung mit Pfadabhängigkeit.

## CFG- und Return-Bilanz

`cfg.tsv` enthält alle 24 von Ghidra gemeldeten Basisblöcke, ihre Endgrenzen und alle Nachfolger. Die Übergänge umfassen drei Schleifenrückkanten: äußerer Schritt `0x6580 -> 0x64ec`, Callback-Schleife `0x6614 -> 0x65c4` und innere Folge `0x6654 -> 0x6568`. Jeder bedingte Zweig, Fallthrough, Call-Fallthrough und Exit des Bereichs ist in der Tabelle enthalten. Es gibt genau einen beobachteten Funktions-Exit: Block `0x16518..0x16520`, wobei `ldmia` bei Ghidra-VA `0x1651c` `pc` lädt.

| Pfadbedingung im Körper | Rückkehrregister-Vorbereitung | Call-Rückgabe, die lokal wirksam ist |
|---|---|---|
| Rückgabe bei `0x64cc` ist nichtnull | `r0=2` bei `0x64d4`; dann direkter Weg zum Epilog | Nur `0x64cc` bestimmt diesen frühen Exit. |
| Rückgabe bei `0x64cc` ist null; Folge erreicht Abschluss | `r0=(r10==0 ? 0 : 2)` durch `0x650c..0x6514`; Epilog `0x651c` | `r0` von `0x6508` wird überschrieben. `r10` ist der Wert, den der Körper am `0x650c` vorfindet; seine Erhaltung über den Call ist mangels Callee-Evidence **OFFEN**. |
| Ein Verarbeitungspfad erreicht `0x6648`, danach endet die äußere Folge | `r0=(r10==0 ? 0 : 2)`; `r10` erhält nach dem Call bei `0x664c` zunächst den `0x6648`-Rückgabewert | Der letzte lokal ausgeführte `0x6648`- oder `0x65fc`-Rückgabewert vor dem Abschluss ist die lokale Quelle von `r10`; spätere passende Aufrufe überschreiben frühere. |
| Verarbeitungspfade überspringen Elemente oder enden ohne `0x6648`/`0x65fc` | dieselbe `r10`-Null-/Nichtnullabbildung am Abschluss | Lokal bleibt der vorherige `r10`-Wert bestehen; unbekannte Callee-Effekte werden nicht ausgeschlossen. |

Die Schleifenrückkanten und sämtlichen branch-basierten Wege zum einzigen Exit sind in `cfg.tsv` prüfbar. Das dort gelistete Ende `0x16658` ist exklusiv und liegt direkt nach dem letzten Körperbefehl; es wird nicht als Teil des analysierten Körpers behandelt.

## Alternative Erklärung und Restunsicherheit

Eine alternative Erklärung für einen von `0x6508` beeinflussten finalen Wert wäre ein nicht-r0-Effekt seines Callees, etwa eine Änderung von `r10` oder eines später gelesenen Speicherwerts. Dafür liegt keine Evidence vor; daher ist nur die Aussage zum Überschreiben des zurückgegebenen `r0` **VERIFIZIERT**, eine Aussage zur vollständigen Wirkung des Calls bleibt **OFFEN**. Entsprechend ist die finale Null-/Nichtnullabbildung beobachtet, die semantische Bedeutung von `0` und `2` aber **OFFEN**.

Weitere Grenzen: Die indirekten Ziele sind nicht aufgelöst; weder Zielvertrag, Laufzeitwerte noch Effekte auf andere Register/Speicherzellen werden abgeleitet. Der zusätzliche direkte Call bei `0x65fc` ist nur insoweit einbezogen, wie sein Rückgabewert lokal an `r10` weitergereicht und damit für die Abschlussabbildung relevant wird. Die Rückgaben anderer Calls, Typnamen, Feldnamen, API-Semantik und Caller-Kontext sind nicht Teil dieses Befunds.

## Reproduzierbare Prüfung

`python3 validate.py` prüft Eingabegröße und SHA-256, die Abbildung `Ghidra-VA = ELF-VA + 0x10000`, alle im Call-/Return-Trace gelisteten Opcodewörter gegen rohe Eingabebytes, 24 zusammenhängende CFG-Blöcke, die drei Schleifenrückkanten und genau drei Call-Flow-Zeilen. Ergebnis: **PASS**. Laufzeit- und Geräteprüfungen: **NOT_RUN**. Unabhängiger Review: **NOT_RUN**; dies ist ein Worker-Self-Review.
