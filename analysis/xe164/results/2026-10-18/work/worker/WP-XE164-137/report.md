> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-137 — exaktes Wort `0x10062001` in codesys3 und IoDrvDal

**Ergebnis.** Im vollständigen Rohdatei-Inventar von `codesys3` gibt es kein Little-Endian-Wort `01 20 06 10`. Die vollständige Rohdatei von `libIoDrvDal.so.1.0.2` enthält zwölf Vorkommen, alle in `.text`-Dateibytes und alle von Ghidra als Daten klassifiziert bis auf `0x133ec` (dort `undecodable`). Der direkte WP132-Anschluss ist der Datenplatz `0x1462c`, von dem die Instruktion `ldr r1,[0x1462c]` bei `0x14460` liest. Ein statischer Zielverweis dieser Callsite auf den WP134-Körper in `codesys3` wird dadurch nicht belegt.

## Eingaben und Identität

| Artefakt | Größe | SHA-256 | Domäne |
|---|---:|---|---|
| `codesys3` | 5,181,396 Byte | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | ARM ELF, Ghidra-Default-Addressraum; Loaderbasis `0x10000` in der REA-Suche |
| `libIoDrvDal.so.1.0.2` | 25,976 Byte | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` | ARM ELF, Ghidra-Default-Addressraum; Loaderbasis `0x10000` |
| WP132-`report.md` (nur Callsite-Kontext) | 9,578 Byte | `8050043d8dd16e7712fb41eda0e78a32440345e86446cc8e06d9fb84959537ae` | bereitgestellter Kontext, nicht erneut analysiert |
| WP134-`report.md` (nur Zielkörper-Kontext) | 11,805 Byte | `04efe7e92aa3ea89561fc9d41a9ea500f372386d9789f6e0f5b0d7a8eab60474` | bereitgestellter Kontext, nicht erneut analysiert |

`provider_address` bezeichnet die von Ghidra verwendete virtuelle Adresse. `file_offset` bezeichnet den nullbasierten Offset innerhalb der Originaldatei. Bei diesen IoDrvDal-Treffern gilt jeweils `file_offset = provider_address - 0x10000`; diese Beziehung ist keine allgemeine Adressregel.

## Vollständige Rohworttreffer

Die Rohdateien wurden vollständig und überlappend byteweise nach den vier Bytes `01 20 06 10` durchsucht. `codesys3`: null Treffer. IoDrvDal: genau die zwölf Treffer in [hits.csv](./hits.csv). Für IoDrvDal bestätigte die vollständige REA/Ghidra-Suche dieselben zwölf Orte in 22,410 Bytes initialisiertem Loader-Speicher, ausschließlich `.text`; Rohdateisuche deckt zusätzlich nicht geladene ELF-Metadaten und alle Dateibytes ab. Für `codesys3` bestätigte Ghidra null Treffer in 6,273,971 Bytes initialisiertem Loader-Speicher; die Rohsuche ist maßgeblich für vollständige Dateiabdeckung.

| Provider-Adresse | Datei-Offset | Ghidra-Klassifikation | Direkte Ghidra-Referenzen zur Wortadresse |
|---:|---:|---|---|
| `0x11774` | 6,004 | data | `0x1172c`, `0x11754` |
| `0x11b20` | 6,944 | data | `0x11afc` |
| `0x11b84` | 7,044 | data | `0x11b68` |
| `0x11be0` | 7,136 | data | `0x11bbc` |
| `0x11e9c` | 7,836 | data | `0x11c68`, `0x11cb8`, `0x11d04`, `0x11d94`, `0x11e70` |
| `0x125a4` | 9,636 | data | `0x1256c` |
| `0x12b44` | 11,076 | data | `0x129a0`, `0x129cc`, `0x12a28`, `0x12ac8` |
| `0x12cac` | 11,436 | data | `0x12c18` |
| `0x13328` | 13,096 | data | `0x12e0c` |
| `0x133ec` | 13,292 | undecodable | keine gemeldeten Referenzen |
| `0x1435c` | 17,244 | data | `0x13794`, `0x1398c`, `0x13b98`, `0x13bd8`, `0x13c04`, `0x13cd4`, `0x13d38`, `0x13e9c`, `0x13fb4`, `0x14094`, `0x140e8`, `0x14150` |
| `0x1462c` | 17,964 | data | `0x14460` |

Bei den als `data` klassifizierten Wörtern lieferte `inspect_native_instruction` für die Zieladresse typed incoming references (READ; Ghidra reference manager; Quelle `analysis`). `0x133ec` ist der genaue Rohbytesuchtreffer, aber Ghidra meldet dort `undecodable` und keine Referenz. Es wird nicht als Code oder Literalverbraucher interpretiert.

## Direkte Referenzfenster

Für alle referenzierten Trefferadressen sind die vom Ghidra-Referenzmanager gemeldeten Quelladressen disassembliert. Alle 29 Quellen außer dem WP132-Anschluss sind direkte `ldr`-Literalreferenzen auf die jeweiligen Wortadressen; das vollständige Inventar mit Instruktionsbytes, Operand und bekanntem Procedure-Eintrag steht in [refs.csv](./refs.csv). Der übrige direkte Anschluss:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

REA Evidence für diese beiden Stellen: `ev_3333b779d771755fff34092996976d96cdccdb4ec9aa32f384e9de8d88c7c055` (Instruktion), `ev_915afdb6fefad3834f5402ff81ab6faaa2f3c5b14764c163155a876a91c732ff` (Zielwort samt typed incoming reference) und `ev_d0bf94143a5b442f566b11176abbb92c8de6ce8385ae041c4df9db11b04a3f32` (`xrefs` zu `0x1462c`). WP132s bereitgestellter Bericht ordnet genau diesen Load der beschriebenen Callsite `ComponentEntry` bei `0x14448` zu; dort folgen laut diesem Kontext das Kopieren von `r1` nach `r0` und der indirekte `blx r2` bei `0x1452c`. `r2` stammt aus dem Eingabewort bei `+0x28`. Das Aufrufziel selbst ist dynamisch/indirekt und bleibt statisch offen.

## Codesys3: unmittelbare Materialisierung

REA/Ghidra v12.1.4 hat `01 20 06 10` in allen 6,273,971 initialisierten Bytes nicht gefunden (`ev_391fbef1397965dc8562496d69555010130c63fd084f881f077e6cbf534f0a45`, vollständige Suche; nicht geladene Sektionen `.ARM.attributes`, `.shstrtab`, `_elfSectionHeaders` ausdrücklich ausgenommen). Die komplette Rohdatei-Suche findet ebenfalls null Treffer, inklusive dieser nicht geladenen Bereiche.

Als begrenzte Instruktionsmaterialisierung wurde die übliche ARM-Form `movw Rd,#0x2001; movt Rd,#0x1006` gezielt geprüft. Die Ghidra-Maskensuche sieht in `codesys3` unabhängig passende `MOVW`-Low-Teiltreffer (`ev_0f685f5b71dbe02608f2d4a88b1a22be186b1a258952baf05726eb84074709b7`) und `MOVT`-High-Teiltreffer (`ev_e2700c017a4b72f43c508183856d3372e7577a7041bacda452cab157b716ac94`); ein einzelner Teiltreffer beweist die 32-Bit-Konstante nicht. GNU `arm-linux-gnueabihf-objdump` 2.44 lieferte auf beiden vollständigen ARM-Disassemblies kein volles Immediate. Der begrenzte Scanner verfolgte `movw` mit Low-Teil bis zum ersten dekodierten Schreibzugriff auf dasselbe Zielregister und fand kein anschließendes `movt` mit High-Teil. Damit ist diese direkte MOVW/MOVT-Materialisierung unter dem beschriebenen Scan nicht beobachtet. Das schließt keine beliebige arithmetische Rekonstruktion, Laufzeitberechnung oder Laufzeitladung aus; eine solche weitergehende Semantiksuche war nicht Teil des begrenzten WP-Umfangs.

WP134s bereitgestellter Kontext lokalisiert einen generischen Zielkörper in `codesys3` um `0x0030066C`, der eingehende Werte verarbeitet. Die statische Evidenz hier verbindet diesen Körper nicht mit der IoDrvDal-Aufrufstelle: WP132 beschreibt `blx r2` mit `r2 = *(input + 0x28)`, und keine statisch festgelegte Zieladresse. WP134 selbst stuft die Zuordnung dieses generischen Körpers zu IoDrvDal als Hypothese ein. Der Wert wird deshalb nicht als Komponenten-ID, API, Handle oder sonstige Semantik benannt.

## Beobachtung, Schlussfolgerung, Unbekanntes

**Beobachtung:** IoDrvDal enthält zwölf exakte Wörter. Die von Ghidra materialisierten direkten Leser sind alle in `refs.csv` aufgeführt; 29 Quellinstruktionen lesen elf als Daten klassifizierte Wortplätze, kein Leser wurde für `0x133ec` gemeldet. Für `0x1462c` ist die eine direkte Referenz der WP132-Literal-Load `0x14460`. `codesys3` enthält das Wort nicht als Rohbytes und die gezielte MOVW/MOVT-Folge wurde nicht beobachtet.

**Schlussfolgerung:** Der WP132-Lane-Wert wird in IoDrvDal aus dem Wort bei `0x1462c` in `r1` geladen. WP132 zufolge wird er später auch nach `r0` kopiert. Das belegt den bereitgestellten Registerwert vor einem indirekten Aufruf, aber nicht dessen Ziel oder eine Zuordnung zum WP134-Körper. Die weiteren IoDrvDal-Literalplätze sind gleichlautende Bytes mit eigenen direkten Leserlisten; ohne begrenzte Funktions-/Verbraucherkontexte folgt daraus keine Gleichheit des Programmzwecks.

**Unbekannt:** Laufzeitwert von `*(input + 0x28)`, tatsächlich aufgerufene Zieladresse, ob sie `0x0030066C` ist, ob einer der anderen elf Plätze auf derselben Pfad-/Objektverwendung liegt, sowie alle dynamischen Berechnungen oder externen Zustände.

**Alternativerklärung:** Die zwölf Treffer können wiederverwendete Konstanten oder dieselben Literalbytes in unterschiedlichen Routinen darstellen. Gleiche 32-Bit-Bytes allein beweisen weder semantische Gleichheit noch Laufzeitverwendung. Auch die unmittelbare Übergabe von `r0/r1` an den in WP134 beschriebenen Helper bleibt, sofern der indirekte Zielwert nicht statisch gebunden ist, nur eine bedingte Registerbeziehung.

## Werkzeug, Konfiguration und Evidenzgrenzen

- REA Server/Package `rea-agents 6.5.0`; Provider Ghidra `12.1.4`; Tool/Profil digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Profil: ARM ELF, Loader/Sprachvariante aus Header, Compiler-Spec auto-default, Ghidra default analyzer, ephemeraler unveränderlicher Quellimport.
- REA `search_bytes` zuerst für exakte Little-Endian-Rohworttreffer und gezielte bitmaskierte MOVW/MOVT-Kandidaten; `xrefs` und `inspect_native_instruction` danach für alle Ghidra-Referenzen. Evidence-IDs der 30 direkten Quellinstruktionen stehen in [instruction_evidence.csv](./instruction_evidence.csv). Ghidras Adressen sind virtuelle ELF-/Provideradressen, nicht Datei-Offsets.
- GNU `arm-linux-gnueabihf-objdump` 2.44 als begrenzter Fallback/Vollständigkeitsgegenprüfung: vollständige Rohbyte-Referenzinventare mit Perl-Byteindex; vollständige ARM-Disassembly nur gefiltert auf das genaue Immediate und das gleichregisterige direkte MOVW/MOVT-Paar. Das ist nicht Quellcode und liefert keine Ausführungsbeobachtung.
- Ein `binary_overview`-Aufruf für codesys3 lief einmal in REA nach 300 s in einen Timeout. Die identische Operation wurde nicht wiederholt. Er war für Trefferinventar oder Referenzprüfung nicht erforderlich.
- Kein Gerät, Netzwerk, VM oder Runtime wurde verwendet. WP132/WP134 Reports sind ausschließlich übergebener Kontext; keine Callee-Body-, IoDrvKbus- oder weitere Rootfs-Analyse.

## Tests und reproduzierbare Prüfung

| Prüfung | Status | Umfang |
|---|---|---|
| Vollständige exakte Rohbytesuche | PASS | Beide exakten Dateien; Perl-Index mit Schrittweite 1; Trefferzahlen 0/12 |
| REA/Ghidra exakte Suchabdeckung | PASS | codesys3 6,273,971 initialisierte Bytes; IoDrvDal 22,410 initialisierte Bytes; übersprungene/uninitialisierte Bereiche getrennt ausgewiesen |
| Direkte Xrefs und Instruktionen für Rohwortplätze | PASS | 12 IoDrvDal-Adressen; 30 direkte Referenzkanten; eine Adresse (`0x133ec`) ohne Ghidra-Referenz |
| Beschränkter ARM-Instruktionsfallback | PASS | GNU Binutils 2.44; exaktes Immediate sowie MOVW/MOVT same-register ohne dazwischenliegenden dekodierten Schreibzugriff auf beiden ARM-Disassemblies gefiltert; kein Treffer |
| Reproduzierbarer Rohbyte-Validator | PASS | Autor-Self-Review am 2026-10-15; Eingabeidentitäten, Größen, Trefferpositionen und Inventarzeilenzahlen bestanden |
| `sha256sum -c SHA256SUMS` | PASS | alle fünf darin gelisteten Ausgabedateien stimmen mit den aufgeführten SHA-256-Werten überein |
| Dynamische Zielbindung oder Runtime-Verhalten | NOT_RUN | ausdrücklich außerhalb des statischen Umfangs |
| Breite Semantiksuche/arbiträre Rechenpfade | NOT_RUN | nicht zur exakten Wortsuche erforderlich; bleibt außerhalb des begrenzten Umfangs |

Reproduzierbarer Validator: [validate.sh](./validate.sh). Er prüft Größe, SHA-256 und vollständige Rohbyte-Trefferpositionen beider Eingaben gegen dieses Inventar. Die Ausführung dieses Validators ist im Folgenden separat als Self-Review ausgewiesen.

## Erzeugte Dateien und Self-Review

Erzeugt wurden `report.md`, `hits.csv`, `refs.csv`, `instruction_evidence.csv` und `validate.sh` ausschließlich in diesem WP-Ausgabeordner. Self-Review: der Validator wurde vom Autor dieser Analyse ausgeführt; dies ist keine unabhängige Prüfung.

| Datei | SHA-256 |
|---|---|
| `hits.csv` | `7fed274465cf1a889a79a7dbe289ac8ba47989363ff65eb328663f5eb7953de7` |
| `refs.csv` | `04e2d75aa2c6d4ff3874880982d52ad9b281e57c78369622e59c383cd9b19684` |
| `instruction_evidence.csv` | `55643c1ccf5f7e43128c1f941062ff0b56efeeb4f6709dfa6210136d48544a1c` |
| `validate.sh` | `91b5b851f65c426433597cc424e80d7294355c43cc200f0d621c00c66bed67d4` |

Der SHA-256 von `report.md` selbst steht im WP-Abschluss zusammen mit den finalen Dateihashes.

`SHA256SUMS` enthält Hashes von `report.md`, `hits.csv`, `refs.csv`, `instruction_evidence.csv` und `validate.sh`; der Hash von `SHA256SUMS` selbst steht im WP-Abschluss.
