> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-148 — `ComponentEntry` Tail `0x4624..0x4677`

## Ergebnis

**VERIFIZIERT:** Die 84 Dateibytes `0x4624..0x4677` (inklusive) sind 21 vier Byte breite little-endian Datenwörter. REA/Ghidra meldet alle 84 Einzeladressen als `data`, ohne Instruktionsdekodierung oder prozedurale Zuordnung. Jeder Wortanfang hat genau eine direkte statische `READ`-Referenz; jede kommt aus einer Instruktion in `ComponentEntry` und zielt auf genau diesen Wortanfang. Es gibt in der vollständigen Byteadressabfrage keine weiteren eingehenden Referenzen in diesem Fenster. Das belegt statisch referenzierte Datenwörter; es belegt keine semantischen Feld- oder API-Namen.

**VERIFIZIERT:** Die rohe Datei stimmt bytegenau mit dem 84-Byte-REA-Speicherread überein. Ghidras Speicherread war vollständig (`84/84`); der eng auf genau diese 84 Datei-Bytes begrenzte `od`-Fallback ergab denselben Hexstrom. Der SHA-256 des abgeschnittenen Bereichs ist `3abaa5e0b04555898cab955c83e86be30ae9359c5dba7f4e828eebae87ee6208`.

**VERIFIZIERT:** Der unmittelbare Vorgänger bei Ghidra `0x14620` / Datei `0x4620` ist `ldmia sp!,{r4,r5,r6,r7,pc}` und hat von REA die Flussklassifikation `return`. REA listet `0x14678` / Datei `0x4678` als nächste Prozeduradresse mit dem Symbolnamen `_DT_FINI`. Das ist hier ausschließlich die folgende Startgrenze; ihr Funktionskörper wurde nicht untersucht.

## Vollständige Wort- und Byte-Tabelle

Jede Zeile deckt exakt vier aufeinanderfolgende Bytes ab. `u32 LE` ist lediglich die little-endian numerische Lesart der gespeicherten Bytes, keine Aussage über den Zweck oder Typ des Werts. `Ghidra-Klassifikation` gibt die beobachtete statische Klassifikation wieder. Referenzquellen sind die REA/Ghidra-Instruktionsadressen.

| Datei-Offset | Ghidra-Adresse | Bytes (Dateireihenfolge) | u32 LE | Ghidra-Klassifikation | Direkte Quelle → Ziel |
|---:|---:|---|---:|---|---|
| `0x4624..0x4627` | `0x14624` | `38 dc ff ff` | `0xffffdc38` | Daten; `READ` | `0x14454 → 0x14624` |
| `0x4628..0x462b` | `0x14628` | `88 dc ff ff` | `0xffffdc88` | Daten; `READ` | `0x14458 → 0x14628` |
| `0x462c..0x462f` | `0x1462c` | `01 20 06 10` | `0x10062001` | Daten; `READ` | `0x14460 → 0x1462c` |
| `0x4630..0x4633` | `0x14630` | `80 1b 01 00` | `0x00011b80` | Daten; `READ` | `0x1446c → 0x14630` |
| `0x4634..0x4637` | `0x14634` | `98 f1 ff ff` | `0xfffff198` | Daten; `READ` | `0x14480 → 0x14634` |
| `0x4638..0x463b` | `0x14638` | `60 d2 ff ff` | `0xffffd260` | Daten; `READ` | `0x14494 → 0x14638` |
| `0x463c..0x463f` | `0x1463c` | `a8 c6 ff ff` | `0xffffc6a8` | Daten; `READ` | `0x144a4 → 0x1463c` |
| `0x4640..0x4643` | `0x14640` | `b4 d0 ff ff` | `0xffffd0b4` | Daten; `READ` | `0x144b0 → 0x14640` |
| `0x4644..0x4647` | `0x14644` | `ec ee ff ff` | `0xffffeeec` | Daten; `READ` | `0x144bc → 0x14644` |
| `0x4648..0x464b` | `0x14648` | `98 d0 ff ff` | `0xffffd098` | Daten; `READ` | `0x144d4 → 0x14648` |
| `0x464c..0x464f` | `0x1464c` | `a0 1b 01 00` | `0x00011ba0` | Daten; `READ` | `0x144e4 → 0x1464c` |
| `0x4650..0x4653` | `0x14650` | `80 1e 01 00` | `0x00011e80` | Daten; `READ` | `0x14534 → 0x14650` |
| `0x4654..0x4657` | `0x14654` | `50 00 00 00` | `0x00000050` | Daten; `READ` | `0x14564 → 0x14654` |
| `0x4658..0x465b` | `0x14658` | `54 00 00 00` | `0x00000054` | Daten; `READ` | `0x1457c → 0x14658` |
| `0x465c..0x465f` | `0x1465c` | `60 00 00 00` | `0x00000060` | Daten; `READ` | `0x1458c → 0x1465c` |
| `0x4660..0x4663` | `0x14660` | `64 00 00 00` | `0x00000064` | Daten; `READ` | `0x14598 → 0x14660` |
| `0x4664..0x4667` | `0x14664` | `f4 da ff ff` | `0xffffdaf4` | Daten; `READ` | `0x145c0 → 0x14664` |
| `0x4668..0x466b` | `0x14668` | `ac da ff ff` | `0xffffdaac` | Daten; `READ` | `0x145e0 → 0x14668` |
| `0x466c..0x466f` | `0x1466c` | `58 00 00 00` | `0x00000058` | Daten; `READ` | `0x145f4 → 0x1466c` |
| `0x4670..0x4673` | `0x14670` | `5c 00 00 00` | `0x0000005c` | Daten; `READ` | `0x14600 → 0x14670` |
| `0x4674..0x4677` | `0x14674` | `68 00 00 00` | `0x00000068` | Daten; `READ` | `0x1460c → 0x14674` |

## Direkte Referenzen

Die Quell- und Zieladressen sind die im Ghidra-Referenzmanager beobachteten Referenzen. Für jeden Zielwortanfang klassifiziert Ghidra den eingehenden Eintrag als `READ`, `data=true`, `read=true`, `write=false`, `call=false`, `jump=false`, `indirect=false`, `computed=false`, `operand_index=1`, `primary=true`, `provenance=ghidra-reference-manager`, `source=analysis`. Diese Angaben beschreiben statische Analysemetadaten und beweisen keinen Laufzeitzugriff. Eine Abfrage jeder einzelnen Byteadresse des Fensters fand an den 63 übrigen Adressen keine eingehende Referenz.

| Quelle (Ghidra) | Ziel (Datei / Ghidra) | Typ | Zieladresse im Fenster |
|---:|---|---|---|
| `0x14454` | `0x4624 / 0x14624` | Daten-`READ` | Wortanfang |
| `0x14458` | `0x4628 / 0x14628` | Daten-`READ` | Wortanfang |
| `0x14460` | `0x462c / 0x1462c` | Daten-`READ` | Wortanfang |
| `0x1446c` | `0x4630 / 0x14630` | Daten-`READ` | Wortanfang |
| `0x14480` | `0x4634 / 0x14634` | Daten-`READ` | Wortanfang |
| `0x14494` | `0x4638 / 0x14638` | Daten-`READ` | Wortanfang |
| `0x144a4` | `0x463c / 0x1463c` | Daten-`READ` | Wortanfang |
| `0x144b0` | `0x4640 / 0x14640` | Daten-`READ` | Wortanfang |
| `0x144bc` | `0x4644 / 0x14644` | Daten-`READ` | Wortanfang |
| `0x144d4` | `0x4648 / 0x14648` | Daten-`READ` | Wortanfang |
| `0x144e4` | `0x464c / 0x1464c` | Daten-`READ` | Wortanfang |
| `0x14534` | `0x4650 / 0x14650` | Daten-`READ` | Wortanfang |
| `0x14564` | `0x4654 / 0x14654` | Daten-`READ` | Wortanfang |
| `0x1457c` | `0x4658 / 0x14658` | Daten-`READ` | Wortanfang |
| `0x1458c` | `0x465c / 0x1465c` | Daten-`READ` | Wortanfang |
| `0x14598` | `0x4660 / 0x14660` | Daten-`READ` | Wortanfang |
| `0x145c0` | `0x4664 / 0x14664` | Daten-`READ` | Wortanfang |
| `0x145e0` | `0x4668 / 0x14668` | Daten-`READ` | Wortanfang |
| `0x145f4` | `0x466c / 0x1466c` | Daten-`READ` | Wortanfang |
| `0x14600` | `0x4670 / 0x14670` | Daten-`READ` | Wortanfang |
| `0x1460c` | `0x4674 / 0x14674` | Daten-`READ` | Wortanfang |

## Grenzen

| Ghidra-Adresse | Datei-Offset | Beobachtung | Status |
|---:|---:|---|---|
| `0x14620` | `0x4620` | `ldmia sp!,{r4,r5,r6,r7,pc}`; dekodiert, Fluss `return`, Procedure `0x14448` | **VERIFIZIERT** |
| `0x14624..0x14677` | `0x4624..0x4677` | 84 Bytes in Ghidra als `data`, keine Stelle wird als Instruktion dekodiert | **VERIFIZIERT** |
| `0x14678` | `0x4678` | erste danach gelistete Prozeduradresse `_DT_FINI`; ausschließlich als Startgrenze verwendet | **VERIFIZIERT** |

REA-Zuordnung an allen 84 Byteadressen innerhalb des Fensters war `procedure=null`. Der Vorgänger-Return schließt den Ghidra-Body von `ComponentEntry` unmittelbar bei `0x14620`; der Tail ist außerhalb dieses Bodies. Ghidra listet `_DT_FINI` als Prozedurstart bei `0x14678`. Es wurden keine Bytes oder Instruktionen ab dieser Startadresse gelesen oder analysiert.

## Methode, Identität und Reproduzierbarkeit

REA-first: Das exakte ELF wurde schreibgeschützt geöffnet und an Ghidra 12.1.4 (ARM, Analysis-Profile-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`) gebunden. `read_bytes` lieferte bei `0x14624` exakt 84/84 Bytes. `inspect_native_instruction` wurde an jeder Adresse `0x14624..0x14677` abgefragt, um Datenstatus und eingehende Referenzen vollständig auf Byteadressenebene zu erfassen. `inspect_native_instruction` an `0x14620` lieferte den Rücksprung. `list_procedures` lieferte die benachbarte Prozeduradresse `_DT_FINI` bei `0x14678`; deren Körper blieb außerhalb des Scopes.

Nur der Facet-Abgleich zwischen initialisiertem Ghidra-Speicher und exakter Dateiherkunft wurde per begrenztem Shell-Fallback ergänzt: GNU `od` (coreutils 9.7), `-j 17956 -N 84`, nur die Tail-Bytes. Der zurückgegebene Hexstrom ist identisch zum vollständigen REA-Read. GNU `readelf` und `objdump` waren nicht nötig. Keine weiteren Fehler oder Blocker.

| Eingabe | Gemessene Größe | SHA-256 | Befund |
|---|---:|---|---|
| FW31 DSO `libIoDrvDal.so.1.0.2` | 25.976 Bytes | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` | **VERIFIZIERT** |
| WP-XE164-144 `report.md` | 7.521 Bytes | `ed6dfcec73f4bb1e74b711a0304fa150809c19514422a5391da7a96a9d5060ab` | **VERIFIZIERT** |
| WP-XE164-145 `report.md` | 9.374 Bytes | `898935f0f69c2cbcb08d9f7497c05c77becfe01a54031e10ca846d10932174fd` | **VERIFIZIERT**; vorgeschlagene 9.929 Bytes waren falsche Metadaten |
| REA Evidence Bundle | 380.422 Bytes | `d2be061f4bb6b99caedc4df47f56c47826274ee775ea64abf74d0c092a56fc88` | 89 Datensätze, 0 Unknowns |

**Beobachtung:** die Bytes sind Daten nach Ghidra-Klassifikation und jedes Wort hat eine statische Lese-Referenz. **Schluss:** der Tail ist ein von `ComponentEntry` referenzierter Datenbereich, kein Teil des von Ghidra erkannten Funktionskörpers. **OFFEN:** ob einzelne Wörter Offsets, Adressen, Flags oder andere Werte darstellen; ihre Zwecksemantik, Relokationsverwendung und Laufzeitnutzung. Alternative Erklärung: ein Wort kann ein numerischer Konstantenwert oder eine kodierte Adresse/Offset sein; weder seine Form noch eine statische Referenz weist eine konkrete Feldbedeutung nach.

Keine Firmware oder DSO wurde ausgeführt. Keine VM-, Netzwerk-, Geräte- oder Hardwareaktion. Keine gemeinsame Datei wurde bearbeitet. Der Validator prüft die Quellhashes/-größen, exakten Tail-Bytes, alle 84 REA-Datenklassifikationen und Referenzziele, den Vorgänger-Return und den nächsten Prozedurstart. Ausführung: `python3 validate.py`, danach `sha256sum -c SHA256SUMS`. Prüfung ist Self-Review; unabhängiger Review/Workerlauf: **NOT_RUN**. Tests: **NOT_RUN** (außer semantischer Paketvalidator).

## Dateien

- `report.md` — Findings mit vollständiger Byte-/Wort- und Referenztabelle.
- `validate.py` — reproduzierbarer, read-only semantischer Validator.
- `validation.txt` — Ergebnis des aufgezeichneten Validatorlaufs.
- `rea-evidence-bundle.json` — komplettes Bundle der REA-Beobachtungen dieses Arbeitspakets.
- `SHA256SUMS` — SHA-256-Manifest aller übrigen Paketdateien.
