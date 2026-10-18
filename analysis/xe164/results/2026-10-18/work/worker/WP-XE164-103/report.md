> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-103 — `idk_Valid_ModuleCmpValue`

## Ergebnis

**VERIFIZIERT (statische Analyse des angegebenen Artefakts):** Für jeden der vier Rohwerte `0x8801`, `0x8802`, `0x9001` und `0x9002` ist der nachfolgende `read_conf_reg`-Pfad **nicht erreichbar**, wenn der jeweilige Wert der von `FUN_00015564(param_2 + 4)` gelieferte Vergleichswert ist. Die Funktion vergleicht diesen Wert zuerst mit dem `uint16`-Wert aus dem Dispatch `libpackbus_read_table_9`. Bei Ungleichheit geht sie zum `false`-Return; bei Gleichheit ist Bit 15 gesetzt und sie kehrt unmittelbar mit `true` zurück. Keiner der vier Werte kann unter dieser Feldzuordnung `read_conf_reg` erreichen.

Der frühe Rücksprung umgeht **nicht** den ersten Dispatch `libpackbus_read_table_9`, und auch nicht den Parser-Aufruf für `param_2 + 4`. Er umgeht die nachfolgenden Parser-Aufrufe für `param_2`, `param_2 + 8` und `param_2 + 0xc`, den Aufruf `FUN_00017ffc` und alle vier `libpackbus_read_conf_reg`-Dispatchstellen.

Die Funktion enthält im analysierten Körper keinen benannten Dispatch `get_uid`. Die einzigen benannten Dispatchziele sind `libpackbus_read_table_9` und `libpackbus_read_conf_reg`; die vier direkten `FUN_00015564`-Aufrufe bleiben unbenannte Helper-Aufrufe. Daher wird `get_uid` hier nicht als Alias oder Semantik eines Helpers behauptet.

### Rohwertentscheidungen

Zuordnung für diese Tabelle: Testwert ist der rohe 16-Bit-Rückgabewert des Parser-Aufrufs bei `param_2 + 4`. Der Parserkörper liegt außerhalb des Auftrags. Die Ghidra-Dekompilierung weist den Vergleichswert als `ushort` aus; der Maschinenpfad testet `tst r9, #0x8000`, also Bit 15 ohne signed-Vergleich.

| Rohwert | signed16-Darstellung | Bit 15 | `get_uid` im Export | `libpackbus_read_conf_reg` |
|---|---:|---:|---|---|
| `0x8801` | `-30719` | 1 | Nicht vorhanden / nicht entscheidbar als Alias | **Not-reachable** |
| `0x8802` | `-30718` | 1 | Nicht vorhanden / nicht entscheidbar als Alias | **Not-reachable** |
| `0x9001` | `-28671` | 1 | Nicht vorhanden / nicht entscheidbar als Alias | **Not-reachable** |
| `0x9002` | `-28670` | 1 | Nicht vorhanden / nicht entscheidbar als Alias | **Not-reachable** |

Die signed16-Werte oben dienen nur der Darstellung. Der relevante Branch ist ein Bitmaskentest auf dem geladenen 16-Bit-Tabellenwert; die Rückgabewerte der übrigen Parser werden dagegen mit `subs`/`bge` als 32-Bit signed-Werte geprüft. Es wird keine Profil- oder Modulbedeutung der Testwerte angenommen.

## Exportidentität und Analysegrenze

- Quelldatei: `libIoDrvKbus.so.0.0.1`
- SHA-256: `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`
- Größe: 38,584 Bytes
- ELF/ARM, Ghidra-Speicheradresse: `0x155d0`
- Dynsym/File-Offset laut Auftrag: `0x55d0`, Länge 484 Bytes, Intervall `[0x55d0, 0x57b4)`
- Ghidra-Körper: einschließlich `0x155d0–0x157a3`, 468 Bytes; entspricht File-Offsets `0x55d0–0x57a3` und liegt vollständig in der angegebenen Dynsym-Grenze.
- Gleichnamiger zusätzlicher Eintrag: Ghidra meldet einen Thumb-Thunk bei `0x11e3c`, der auf `0x155d0` springt. Für die Untersuchung wurde ausschließlich der angeforderte vollständige Körper bei `0x155d0` ausgewertet.
- REA: `rea-agents 6.5.0` (installierter Bridge-Pfad); Provider Ghidra `12.1.4`; Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Kanonischer Nachweis: `rea-bundle.json`, ein retained `analyze_function`-Datensatz, Evidence-ID `ev_344e29e814103740d060400401ff2946b44e85202d5317ebe679fead48f8ac22`.
- Der REA-Datensatz enthält den vollständigen zusammenhängenden Funktionskörper, Pseudocode, Instruktionen, Basic Blocks, Referenzen, Strings/Namen, Calls und High-P-code. Kein objdump/readelf-Fallback wurde benötigt.
- Ghidra markiert die Callee-Inventur als teilweise: fünf Call-Referenzen haben keine aufgelösten Ziele. Die vollständigen Instruktionen zeigen die fünf hier relevanten indirekten `blx`-Sites; die übergebenen benannten Strings erlauben die Dispatch-Namen, aber keine Aussage über die zur Laufzeit aufgelösten Zieladressen.

## Kontrollfluss- und Guard-Tabelle

Adressangaben sind Ghidra-Adressen. Ziele `0x15758`/`0x1579c` sind die gemeinsamen `false`- bzw. Nullargument-Rückgaben. „Parser“ bezeichnet nur den direkten Call an `FUN_00015564`; über dessen Verhalten wird keine Aussage getroffen.

| Adresse / Instruktion | Bedingung bzw. Operation | wahr/genommen | falsch/nicht genommen |
|---|---|---|---|
| `0x155d0–0x155d8` `cmp/cmpne/beq` | `param_2 == 0 || param_1 == 0` | `0x1579c` → false | Funktionsprolog bei `0x155dc` |
| `0x155f8`, `0x155fc–0x15604` | `strnlen(param_2, 0x11) == 0x10` | weiter zu Tabellen-Dispatch | `0x15758` → false |
| `0x15628`, `0x1562c–0x15634` | `read_table_9`; Rückgabewert `== 0` und `local_2c[0] == 0` | Parser +4 | Fehler → false |
| `0x15640`, `0x15644–0x15648` | Parser(`param_2+4`) ist gleich `local_2e` | Bit-15-Test | ungleich → false |
| `0x1564c–0x15650` | `local_2e & 0x8000` | `0x15654`: true-Return | weiter bei `0x15660` |
| `0x15664–0x1566c` | Parser(`param_2`); 32-Bit signed `< 0` | `0x1571c`: Dispatch für Index `0x10` wird übersprungen | Index `0x10` an `0x15738` lesen |
| `0x15738`, `0x1573c–0x15754` | `read_conf_reg(0x10)`; Erfolgstatus und `((local_2e ^ value) & 0x300) == 0` | weiter zu Parser +8 | Fehler/Abweichung → false |
| `0x15674–0x1567c` | Parser(`param_2+8`); 32-Bit signed `< 0` | Index `0x1d` wird übersprungen | Index `0x1d` bei `0x1577c` lesen |
| `0x1577c`, `0x15780–0x15794` | `read_conf_reg(0x1d)`; Erfolgstatus und exakte Gleichheit | weiter zu Parser +0xc | Fehler/Abweichung → false |
| `0x15684–0x1568c` | Parser(`param_2+0xc`); 32-Bit signed `< 0` | `0x15654`: true-Return | Index `0x1e` lesen |
| `0x156b0`, `0x156b4–0x156bc` | `read_conf_reg(0x1e)`; Erfolgstatus | `FUN_00017ffc(local_2e, 10)` | Fehler → false |
| `0x156c8–0x156e0` | Low-16-Bit des Helper-Ergebnisses ungleich `9` | true genau dann, wenn Helper-Ergebnis == Parser +0xc | bei Gleichheit `9`: Index `0x1c` lesen |
| `0x156fc`, `0x15700–0x15714` | `read_conf_reg(0x1c)`; Erfolgstatus und exakte Gleichheit mit Parser +0xc | `0x15654`: true-Return | Fehler/Abweichung → false |
| `0x15758–0x1575c` | gemeinsamer Fehlerpfad | false-Return | — |
| `0x1579c–0x157a0` | Nullargument-Return | false-Return | — |

## Calls im Exportkörper

| Callsite | Art / beobachtetes Ziel | Argumentfluss bzw. Guard |
|---|---|---|
| `0x155f8` | direkt: `<EXTERNAL>::strnlen` | `param_2`, Limit `0x11`; nur exakte Länge `0x10` passiert |
| `0x15628` | indirekt via `[param_1+0x70]`, Name `libpackbus_read_table_9` | vor dem Vergleich +4; `param_3`, Ausgabepuffer `local_2c`, `&local_2e` |
| `0x15640`, `0x15664`, `0x15674`, `0x15684` | direkt: `FUN_00015564` | Parser-Aufrufe bei `param_2+4`, `param_2`, `param_2+8`, `param_2+0xc` |
| `0x15738` | indirekt via `[param_1+0x70]`, Name `libpackbus_read_conf_reg` | Index `0x10`; nur wenn Parser(`param_2`) nicht signed-negativ |
| `0x1577c` | indirekt via `[param_1+0x70]`, Name `libpackbus_read_conf_reg` | Index `0x1d`; nur wenn Parser(`param_2+8`) nicht signed-negativ |
| `0x156b0` | indirekt via `[param_1+0x70]`, Name `libpackbus_read_conf_reg` | Index `0x1e`; nur wenn Parser(`param_2+0xc`) nicht signed-negativ und vorige Gates passieren |
| `0x156c8` | direkt: `FUN_00017ffc` | `local_2e`, Konstante `10`; nur nach erfolgreichem Index-`0x1e`-Read |
| `0x156fc` | indirekt via `[param_1+0x70]`, Name `libpackbus_read_conf_reg` | Index `0x1c`; nur wenn Low-16-Bit des vorherigen Helper-Ergebnisses `9` ist |

## Alternativerklärung, Status und Restunsicherheit

Die Aussage „Not-reachable“ ist an die oben explizite Feldzuordnung gebunden: Der Testwert ist der rohe 16-Bit-Wert aus Parser(`param_2+4`). Aus dem Funktionskörper allein folgt nicht, wie `FUN_00015564` Texte oder andere Eingaben in Werte umwandelt. Sollte mit „Testwert“ stattdessen ein Wert am Feld `param_2`, `param_2+8` oder `param_2+0xc` gemeint sein, entscheidet dort jeweils ein signed 32-Bit `bge`-Pfad über einzelne Conf-Reads; ein rohes uint16 allein legt das Vorzeichen des Helper-Rückgaberegisters nicht ohne Helperkörper fest. Diese andere Feldzuordnung wird deshalb nicht als Ergebnis der vier Tabellenzeilen ausgegeben.

**Restunsicherheit:** statische Analyse sagt nicht, welche Werte die indirekten Dispatches zur Laufzeit liefern, ob deren Funktionszeiger valide sind, oder wie die außerhalb des Exports liegenden Helper arbeiten. `get_uid` ist als benannter Dispatch im untersuchten Körper nicht beobachtet. Keine Geräte-, Runtime- oder Hardwareaussage.

Tests:

| Prüfung | Status | Ergebnis |
|---|---|---|
| Eingabeidentität (SHA-256 und Dateigröße) | PASS | Hash und 38,584 Bytes stimmen mit Vorgabe überein. |
| Dynsym-Grenze gegen REA-Körper | PASS | vollständiger Körper endet bei File-Offset `0x57a3`, vor exklusivem `0x57b4`. |
| Semantischer Validator | PASS | `validate_semantics.mjs` prüft Bundle-Identität, Provider, Evidence, vollständige Grenze, Callsites, Dispatchnamen und alle vier Bit-15-Fälle. |
| `sha256sum -c SHA256SUMS` | PASS | alle mitgelieferten Artefakte stimmen. |
