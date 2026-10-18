> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-130 — begrenzte Gegenprüfung der WP128-Ableitung

## Urteil

Die lokale Ableitung von WP-XE164-128 wird durch eine begrenzte, unabhängige
Byte-/Disassembly-Gegenprüfung bestätigt. „Unabhängig“ meint hier eine von der
WP128-Textableitung getrennte Prüfung derselben vorgelegten Binärdatei und
Disassembly. Dies ist weder ein unabhängiger externer Review noch ein
Runtimebeleg.

| WP128-Behauptung | Urteil | Begründung und Grenze |
|---|---|---|
| Bei `0x2fc55c` wird `r0 = fp - 0x5c` gesetzt; das ist die lokale Argumentbasis des späteren Calls. | **VERIFIZIERT** | Rohinstruktion `e24b005c` disassembliert als `sub r0, fp, #92`; WP125 zeigt `blx r2` bei `0x2fc5c8`. Die Beschreibung als Argumentbasis folgt aus diesem Registerwert am Callsite. Ein weitergehendes Objektlayout wird nicht behauptet. |
| `movw r3,#57644` und `movt r3,#47` bilden `0x002fe12c`. | **VERIFIZIERT** | Rohinstruktionen `e30e312c` und `e340302f`; die unmittelbaren Felder sind `0xe12c` und `0x002f`. |
| `str r3,[fp,#-40]` speichert nach `fp-0x28`, relativ zur lokalen Basis `+0x34`. | **VERIFIZIERT** | Rohinstruktion `e50b3028`. Rechnung: `(fp - 0x28) - (fp - 0x5c) = 0x34`. Der resultierende Slotwert ist `0x002fe12c`. |
| Der Slot und `r0` bleiben zwischen dem Store und `blx r2` unverändert. | **VERIFIZIERT** | Der vollständige Ausschnitt `0x2fc598..0x2fc5c4` enthält nur `r3`-Konstantenaufbau und Stores an `[fp,#-56]`, `-52`, `-48`, `-36`. Es gibt dort keinen Store nach `[fp,#-40]` und keine Instruktion, die `r0` ändert. Am `blx` folgt also `r0 = fp-0x5c`, und `+0x34` enthält weiterhin `0x002fe12c`. Aussage gilt nur für diesen begrenzten Instruktionspfad. |
| `r2` ist im generischen Loaderkontext der zuvor aufgelöste `ComponentEntry`-Zeiger. | **VERIFIZIERT** als statische Kontextzuordnung aus WP125/WP123; **OFFEN** für eine konkrete Laufzeitauflösung. | WP125 belegt das Laden des Caller-Blockworts `+0x10` nach `r2` und `blx r2`; dessen Loader-Handoff bindet die Position an den so bezeichneten Exportzeiger. Eine tatsächliche Laufzeitbelegung oder konkrete IoDrvDal-Zielidentität folgt daraus nicht. |
| Der Aufruf bindet den konkreten WP128-Stackblock an IoDrvDal `ComponentEntry`. | **HYPOTHESE** | Statische Dal- und Loaderpfade belegen eine kompatible Positionsfolge, aber nicht, dass dieser generische Loaderaufruf zur Laufzeit gerade das konkrete IoDrvDal-Binary adressiert. |
| Der Wert bleibt nach dem Dal-Callback gleich und erreicht `0x2a268` bzw. Kbus. | **HYPOTHESE** | WP119/WP122 zeigen einen Dal-Read vor und einen zweiten nach dem optionalen indirekten Call. Der Call könnte den Speicher hinter dem Eingabezeiger über einen Alias ändern. Wertgleichheit und Ausführung mit `0x002fe12c` sind daher nicht verifiziert. |

## Eigene Rechen- und Instruktionsprüfung

Gegenprüfung mit `arm-linux-gnueabihf-objdump` GNU Binutils 2.44 direkt auf
dem hashgebundenen `codesys3` ELF, `-d --show-raw-insn --start-address=0x2fc55c
--stop-address=0x2fc5cc`:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Zusammensetzung: `(0x002f << 16) | 0xe12c = 0x002fe12c`.
Relative Lage: `(fp - 0x28) - (fp - 0x5c) = -0x28 + 0x5c = 0x34`.
Der adressierte Bereich enthält alle Instruktionen zwischen Store und Call;
keine davon schreibt `[fp-0x28]` oder `r0`. Dies bestätigt die konkrete
WP128-Ableitung ohne Funktionsdecompilation und ohne Analyse jenseits der
vorgegebenen Grenze.

## Beobachtung und Schlussfolgerung

Beobachtet sind die oben gelisteten ARM-Instruktionen im exakten `codesys3`
ELF sowie die in WP125 dokumentierte Übergabe des lokalen Blocks als `r0` und
Aufruf des in `r2` gehaltenen Werts. Die Relativposition `+0x34` und der
konkrete Slotwert bis zum Call sind unmittelbare arithmetische Folgerungen aus
diesen Instruktionen.

Die WP119/WP122-Berichte beschreiben unabhängig davon den Dal-internen Ablauf:
Eingabe `+0x34` wird einmal vor und einmal nach einem optionalen Callback
gelesen; der spätere Wert wird nach Dal-BSS `0x2a268` kopiert. Das belegt den
Dal-Positionspfad, aber nicht die konkrete Loaderbindung an Dal und nicht die
Gleichheit des Eingabewerts über den Callback hinweg. Die WP128-Einstufung
dieser beiden zusammengesetzten Aussagen als **HYPOTHESE** ist angemessen.

## Alternative Erklärung und Restunsicherheit

Der generische Loader kann in einem betrachteten Lauf eine andere Komponente
aufrufen. Dann ist der lokale Block zwar weiterhin wie oben initialisiert,
aber die Dal-spezifische Folgekette gilt nicht für diesen Call. Falls Dal
aufgerufen wird, kann der optionale Call bei Dal `0x1452c` Eingabespeicher
über einen Alias ändern; der zweite `+0x34`-Read muss dann nicht den beim
Eintritt vorliegenden Wert liefern. `0x002fe12c` ist hier nur eine
zusammengesetzte numerische Adresse; Semantik und Zielkörper bleiben **OFFEN**.

Nicht untersucht wurden der Zielkörper `0x2fe12c`, neue Callgraph-Lanes,
Runtime, VM, Netzwerk, Geräte oder Hardware. Die Gegenprüfung reproduziert
keinen früheren REA-Timeout und behauptet keine Laufzeitausführung.

## Eingaben und Identität

| Eingabe | Größe (Bytes) | SHA-256 | Verwendung |
|---|---:|---|---|
| WP112 `hit_files/usr/bin/codesys3` | 5.181.396 | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | direkter Byte-/Cross-`objdump`-Gegencheck |
| WP125 `function-disassembly.txt` | 3.392 | `de11be1f744ffd81096202a80d8ec0c971049c9cfcd2357c8b47756b738f7621` | Abgleich der adressierten vollständigen Helper-Instruktionen |
| WP125 `report.md` | 7.604 | `5008f6d6f1ff8b5259c3a59543bd73e210a655fe1865861a201581d1c5dece16` | `r2`-/Loaderhandoff-Kontext |
| WP119 `report.md` | 8.459 | `417bb844320d64a3cda06754b3aa95e835e7b9b5225413d570c3ca653a747fb6` | Dal-Eingabe- und BSS-Store-Befund |
| WP122 `report.md` | 4.295 | `d66a5be8d965d77d381860c77d9d5985c4fe5efcc9d8bd90f1646c65e1641aec` | Dal-Doppelread- und Kbus-Positionsfolge |
| WP128 `report.md` | 4.907 | `9bc728298381283b376eadb1a6448cbb1219f8af5d1cdc343245707ce79241b4` | geprüfte Claims und Schlussfolgerungen |
| WP128 `flow.tsv` | 1.317 | `92869d689a033098594807479d2ae19143454977f9d12777563b24da4a5920cd` | Zuordnung lokaler und bedingter Kanten |

Hinweis: WP122 wurde unter `work/root/WP-XE164-122/report.md` gefunden; der
im Auftrag angegebene `work/worker/`-Pfad existiert nicht. Größe und SHA-256
entsprechen den vorgegebenen Identitätswerten.

## Validator und Status

Validator: `validate.sh`, Ergebnis **PASS**. Er prüft ausschließlich die
angegebenen Dateigrößen und SHA-256-Hashes sowie die lokale Offset-/Konstanten-
Arithmetik. Die Rohinstruktionen wurden separat mit Cross-`objdump` direkt aus
dem Binary geprüft; der Validator ersetzt diese Gegenprüfung nicht.

| Prüfung | Status |
|---|---|
| Eingabegrößen und Hashes gegen die vorgegebenen Identitäten | **PASS** |
| Instruktionsanker `0x2fc55c`, `0x2fc58c`, `0x2fc590`, `0x2fc594`, `0x2fc5c8` per Cross-`objdump` | **PASS** |
| Konstanten- und Relativoffsetrechnung | **PASS** |
| Lokaler No-overwrite-/No-`r0`-change-Befund bis `blx r2` | **PASS** |
| Konkrete dynamische Dal-Bindung | **HYPOTHESE** |
| Wertgleichheit hinter Dal-Zwischencallback / Kbus-Wert | **HYPOTHESE** |
| Semantik von `0x002fe12c` | **OFFEN** |
| Runtime, VM, Netzwerk, Geräte und Hardware | **NOT_RUN** |
| Externer unabhängiger Review | **NOT_RUN** |

Nur WP-XE164-130-Ausgabedateien wurden angelegt. Keine Eingabedatei wurde
verändert.
