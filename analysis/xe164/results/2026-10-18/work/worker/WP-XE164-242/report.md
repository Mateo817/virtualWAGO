> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-242: 44 indizierte PC-Dispatches

## Ergebnis

**OFFEN.** Alle 44 Tabellen sind auf Rohwortebene aufgelöst. Ein reproduzierbarer, syntaxbegrenzter Scan über die sieben Markerintervalle (`0x154dc4..0x180000`) fand genau drei sichtbare bedingte oder unbedingte `mov r0,#15`-Stellen (`0x15629c`, `0x161c1c`, `0x176e58`) und null same-segment Treffer für einen unmittelbaren `ldr`-Load mit Offset `#32`/`#0x20` in das BLX-Register plus sichtbares `r0=15` bis zum selben `blx`. Der begrenzte Parser erkennt Ziel-/Source-Register `r0..r15` sowie `ip/fp/sl/sp/lr/pc` und normalisiert diese Aliase. Segmentgrenzen erkennen die im Validator aufgeführten bedingten und unbedingten `b`, `bl`, `blx`, `bx`, `pop`, `ldm`, `stm` und `str`-Mnemonicformen; `stm`/`str` werden dabei konservativ als Segmentgrenzen behandelt. Der Scan trackt explizite ARM-Registerdestinationswrites; `cmp`, `cmn`, `tst` und `teq` gelten als nicht schreibende Tests. Registerwerte werden an den erkannten Transfergrenzen gelöscht. Die ersten zwei Stellen werden unmittelbar durch `movt r0,#1` geändert und führen zu direkten `bl EventOpen`-Calls; die dritte ist `movle` vor `ble` in einen Epilogpfad. Diese begrenzte Suche schließt nicht erkannte Kontrollflussformen, getrennte Blöcke, berechnete r0-Werte oder opaque Calls nicht aus. Alle 42 übrigen Tabellenziele bleiben für die vollständige Frage OFFEN; `0x171e2c`/`0x171ebc` haben zusätzlich vier bytegebundene, callfreie Load→BLX-Lanes.

## Identität und Methode

- Artifact: `codesys3`, 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`; lokale Datei ist die WP-XE164-127 extrahierte ELF-Kopie.
- Bereich: dispatch VA `[0x154dc4,0x180000)`; genau 44 `indexed_pc_dispatch`-Zeilen aus WP-XE164-234. Die zugehörigen sieben Symbolmarken stehen unten. Kein Geräte-, VM- oder Netzwerkzugriff.
- Eingaben: Gap-Inventur SHA-256 `da464c51810a1a728eccddd7b6141e56502b8f7368dec55b9149a418b8bc40f3`; bounded GNU objdump Listing SHA-256 `a0bcaec911083963c573bead0b28ee8c0b3106c3b8aa5eb595a556fbc5e75110`; Assignment und ELF erneut gehasht durch `validate.py`.
- REA: `rea-agents` 6.5.0, Ghidra 12.1.4. Read-only session status zunächst `open=false`; anschließend mit Autorisierung des Leads exakt dieselbe ELF-Datei geöffnet (SHA-256 wie oben). REA `analyze_function` wurde pro Dispatchadresse und pro Symbolmarke abgefragt. 54 vollständige Records wurden ohne Anbieter-/Targetwechsel exportiert; der Response-budget-Hinweis bei größeren Funktionsdossiers bedeutet retained full Evidence, nicht fehlende Aufzeichnung. Bundle: `rea-evidence.json`.
- Zwei exakte Dispatchadressen (`0x17b40c`, `0x17df3c`) hatten in Ghidra keinen Procedure-Eintrag; ihre jeweilige benannte Entry-Adresse wurde separat erfolgreich abgefragt. Für große Ghidra-Dossiers meldete der Transport ein Response-budget-Limit und hielt die kompletten Records im Session-Ledger. Einmal dokumentierter konkreter Gap: keine verlässliche inline Ausgabe für benötigte Instruktions-/Tabellendetails. Bounded objdump/raw-byte-Fallback blieb auf den zugewiesenen Dispatch-/Tabellen- und Call-Lane-Adressen.
- Verwendete REA-IDs und exakt ausgewertete Ghidra-Body-Bereiche stehen in `rea-scope.tsv`; die Matrix referenziert IDs pro Dispatch. Der vollständige Export ist nur Audit-Beleg. Für Codeaussagen wurden keine Bytes außerhalb `[0x154dc4,0x180000)` ausgewertet.
- Bounded GNU objdump 2.44 Listing wurde nach dem REA-Funktionsdossier nur zur Rohwort-/Tabellenauflösung verwendet. Direkte ELF-Worte wurden little-endian gelesen. Bei jeder Dispatchzeile stimmen Listing und rohe Datei-Worte überein.

## Tabellenvertrag

Jede Zeile der Matrix belegt getrennt den Dispatchwortwert, den unmittelbar vorausgehenden `cmp` derselben Indexregisterspur, die unter dessen unsigned `LS`-Bedingung zugelassenen Indizes `0..N`, die ARM-PC-Basis `dispatch+8`, jedes aus der Datei gelesene Tabellenwort und dessen rohe Zieladresse. Alle 44 Wortbereiche liegen vollständig im vereinbarten VA-Bereich. Die Guard-Aussage gilt konditional unter dem jeweiligen lokalen `cmp`→`ldrls`-Paar. Sie behauptet keine globale CFG-Reachability, keine Laufzeitnutzung und keine Bedeutung der Tabellenziele.

## Geprüfte direkte Lanes

`0x171e2c` hat CMP-Grenze 8 und neun Tabellenwörter; `0x171ebc` hat dieselbe Grenze und neun Wörter. Beide Tabellenziele sind vollständig gelesen. Die vier indirekten Ziel-Loads und Calls aus diesen direkten Lanes sind bytegebunden in `dispatch-call-lanes.tsv`: `0x171e58→0x171e68`, `0x171ea0→0x171ea4`, `0x171f2c→0x171f30` und `0x171f54→0x171f58`. In allen vier Fällen wird das BLX-Zielregister aus `[r4,#0x24]` geladen. Die jeweiligen r0-Loads stehen an `0x171e64` (`[r4,#0x3c]`), `0x171e98` (`[r4,#0x48]`), `0x171f14` (`[r4,#0x48]`) und `0x171f44` (`[r4,#0x30]`). Für jede Zeile enthält die Matrix sowohl das Ziel-Load→BLX-Fenster als auch das vollständige r0-Load→BLX-Fenster. Die geprüften Fenster enthalten keine erkannte Kontroll-/Callgrenze und überschreiben weder r0 noch das BLX-Zielregister. Der `+0x20`-Load bei `0x171e1c` bzw. `0x171eb0` liefert zuvor den um 1 reduzierten Dispatchindex und wird durch `sub r3,r3,#1` überschrieben; er ist nicht der BLX-Zielwert. Keine dieser vier geprüften direkten Lanes bindet sichtbares r0=15 mit einem +0x20-Zielwert am gleichen BLX.

Die drei sichtbaren `r0=15`-Initialisierungen sind in `selector15-audit.tsv` an ihren nächsten lokalen Branch-/Call-/Return-Kanten dokumentiert. Bei `0x15629c` und `0x161c1c` ist die Folgelinie jeweils `movt r0,#1` (Wort `e3400001`), gefolgt von direktem `bl EventOpen`; bei `0x176e58` folgt `ble 0x176ea8` (Wort `da000011`) und das Ziel beginnt mit Stackwiederherstellung `sub sp,fp,#28`, danach `ldm ... pc`. `selector15-segment-scan.tsv` listet alle sieben Markerintervalle und das Ergebnis des syntaxbegrenzten Screens; die Prüfung übernimmt keine Registerwerte über einen Call oder eine erkannte Branchkante.

Das begrenzt nur diese rohen Tabellenkanten und die unmittelbar zugehörigen Call-Lanes. Die Funktion enthält weitere opaque Calls, Ghidra berichtet für zwei terminale Calls eine modellierte nicht-fallthrough Kante, und weder Caller/Runtime-Bindung noch externe/indirekte Folgepfade sind hier erschöpfend untersucht. Daher wird auch für diese zwei lokalen Dispatches kein Programm- oder Runtime-Nullbefund erhoben.

## Sieben benannte Symbolmarken

- `InfoModel_GetConditionId@@Base` at `0x154dc4`.
- `ContinuationInfo_Free@@Base` at `0x1630bc`.
- `OPCUAClient_Call@@Base` at `0x16b854`.
- `OPCUA_Session_Process@@Base` at `0x16d688`.
- `OPCUAClient_ExceptionHandler@@Base` at `0x171d18`.
- `CmpChannelClientIec__Entry@@Base` at `0x17adf4`.
- `sysexceptdisableseh2@@Base` at `0x17def4`.


Die `.symtab`-/Objdump-Marken liefern Gruppierungsnamen, keine Begründung, dass jeder spätere Dispatch im Funktionskörper dieser Marke liegt. Ghidra bildet mehrere Dispatchbereiche als unabhängige bzw. nicht zusammenhängende Funktionskörper ab; daher bleibt die tabellenzeilenbasierte Matrix maßgeblich.

## Pro Dispatch

`dispatch-matrix.tsv` enthält genau 44 Zeilen. `dispatch_table_status` ist VERIFIZIERT, wenn die lokale Guardspur und alle zugelassenen Tabellenwörter einschließlich Zielbereiche zusammenpassen. `question_status` bleibt für 42 Zeilen OFFEN; bei den zwei direkt untersuchten Tabellen gilt VERIFIZIERT nur für die begrenzte Aussage zur dortigen direkten Call-Lane. Alternative Erklärung und Restunsicherheit stehen in jeder Zeile.

## REA Evidence

`rea-evidence.json` enthält 54 Records für denselben Hash und Ghidra-Provider. Relevante pro-Dispatch-IDs:

- `0x00155320`: `ev_ad58083217301b245ae9ae44f11a366c149118d816cfb1af480ca95e0fe6d54c`.
- `0x001554e4`: `ev_e480bf3d6f0c43525cccdc26fc85dfe9437693be48769bb79f9e92bb998a5cf4`.
- `0x001555c8`: `ev_9e2ac7cc327b71272a153354e1c62a58ccda2967619a5638c63627d583f543c0`.
- `0x001569ac`: `ev_17e3a47a1be985fb759c4c1a2fb7fef129e49e7d0eb51d8352b6eb8a8855b46d`.
- `0x00158830`: `ev_e3e610e5662cfb817c0eaa5df9aca6fff6076d719afce748ec3362324ea8387f`.
- `0x00158894`: `ev_5d9e1cefa50c93f702c79573b923a8022b122983261d5808d56b37f914c25f7c`.
- `0x00159e64`: `ev_1abbe84a3f6f51619b71c1c03452b15b8c07f95ec89aea951bf95860d989ef02`.
- `0x00159eac`: `ev_ba2882708a964fe62e43a4386ada93238204303ffcb8b7c7aeb0498d45861b0c`.
- `0x00159f54`: `ev_bdd2753e0d3ffe0b6c73d9e935163c2e0a56daf2a78ef39fe3763479e919ba6c`.
- `0x0015a104`: `ev_60e8648cb7bfd2ed755ce5c2dae58553083b1b03109c49958a355e086d9b155d`.
- `0x0015a158`: `ev_b84c9b9bf20206465e07e15aee811f50225ed355f0ed73872956f625ff140d0f`.
- `0x0015a2b0`: `ev_55638a2a54e59f9e0cbb9f27c10844efa3056a180b362cec33052634f2c9c181`.
- `0x0015af1c`: `ev_59a88490f8f8c1703775bc8930cab143f6b23422bf6ed77effee130e6e6e95df`.
- `0x0015b0a0`: `ev_39d1a85e0ad3694203daeb035875ad027f622f9865199f78d50bb8aa68cc1e42`.
- `0x0015b178`: `ev_3744a4620eb521b44e596962b45555212329389fdcf3ca9c814ee195188972a5`.
- `0x0015b1bc`: `ev_ad8ffa1142bb9bec7c20791762415af58f58f748ee61c6a853b6f49ae06150c1`.
- `0x0015b2fc`: `ev_cd150e2cfedf27b292d52790df473f601b8d9e97cafc8b910d62380064b9be67`.
- `0x0015b3e4`: `ev_dc4bb4c39a0907c666bf1029c181e68dcf5dc80a1de0b341508847c2f4c40e4f`.
- `0x0015b44c`: `ev_6d755a5cdb4c3556f20943c8c7c20da9ab03e211720f6f5f32c67190885f214d`.
- `0x0015b5bc`: `ev_a55e23395ef2759bc53b5aa86f8a0334edf50830e06fa7309d9deda66bf44ce6`.
- `0x0015b7d8`: `ev_af2229c0de3812604899132f1269373601126bc49b2eee14da465e11d0bb4308`.
- `0x0015c688`: `ev_e41ad46a8cb246e8f6f99e73e346f605aec4ac96d01d5d326975a4e21a8d89c2`.
- `0x0015c9f0`: `ev_3cf190d0b301c54d447956fffaaff66b190ec9a898013ca6f864e8d7ee090d55`.
- `0x0015cea0`: `ev_6107a4ed794a89c3d8a0001502eaed6a0fd55f41cc48d3ec31795449ce4fdc71`.
- `0x0015ebb8`: `ev_29f249104aef60407bdd3d967ed364afb2e9bb14534752e70a58f8e4f5834623`.
- `0x0015ef70`: `ev_88fedb6d26e31ca8661dcd48aec1e03c64c94fa978f61e66bb10a46a2685f7ad`.
- `0x0015f1b0`: `ev_921c543637d5f926bd9159ddc47023fbe8b88a51ef1c14845b0846e01270e253`.
- `0x00163138`: `ev_3974b9fa789a91b3e08f25c7a116b6fd8c4651d0c3fca1111f7237fd183eb361`, `ev_9ecc6f60be72749d3888e7125ba6745fe9c2c47eee2538726fd9f8e425438835`.
- `0x001633c4`: `ev_86bf1e9b63ba57f73d9a2b7c376cfec344f0c38afb3309aff346c7ee78db4ea6`.
- `0x00163b38`: `ev_cd71f582897c92fd500c02bd2956cfab7bf85726db4c0bec5d7f0a5e297c4c3c`.
- `0x00163c10`: `ev_c9f72c0654c6f3784348a6708d0a419813a444485d83f5b168afad68e1c6b407`.
- `0x00163e48`: `ev_0e0d0a1f14ff30519a551f6676cd8cda66ca3df5c06a82b58df49d369997f661`.
- `0x001647e8`: `ev_0323be254b522d24f913e18cad11a477e309bcba376a84dc697106d1f049b316`.
- `0x00164a48`: `ev_f6edf9709383cda27e323398cc768b229c20f161e9b6a333f67df224efadf2c7`.
- `0x00165008`: `ev_3d5351458217fb921eb4a443e0a7d022467637e0743e5afeab269f93e2ce3901`.
- `0x00165c70`: `ev_f8e3538ef0b71ad49c96514e11812c7c3d172fdf8cd77bc2ed827a49996063dc`.
- `0x00165d30`: `ev_7428755ba2dcf838c3f9b4928f4a52352e7e2daf48a4ddf2c3895946527cb5c3`.
- `0x00165e08`: `ev_3915ff46f033fdd8dbaef21a2dc8b9604f0fee5130bccd0f507e58d5444e2a8e`.
- `0x0016baec`: `ev_049ea4d263df5c9c24090c2dc0bca86a59beb8ac27c59bcc2bb16715cf6dbd7f`, `ev_5faca01eaa427cc15cfa98132131437b75dd0daaa277da3ec1759e7cb9c02482`.
- `0x0016d6b4`: `ev_241e51ab5c27ddecf9acb343bda10c9a4415101d0f4283f240c552173b9b5d3f`, `ev_255ce1759f96e28c7ed8b223538a4f5020cb2b5c81f03f852fd52cd301f6bc9b`.
- `0x00171e2c`: `ev_30677349ac3eba9fe458946ead465f67f651bd7b328988937b765b54972cc1ec`, `ev_57adf90f371609dacb2375d8804721599864f7906f6aa8413de7bc713a09f50f`.
- `0x00171ebc`: `ev_e6b1bda7ba355b7cdfba2391f407ffc42ead49459f0870b3f2b4b6279ec1ac30`.
- `0x0017b40c`: `ev_74f3e2730a6e8ad4fba40304e31f48c87ead72fab3d18c8fa6e8a45c195df54c`.
- `0x0017df3c`: `ev_4bd4b012f0d181e3a3b50e872dfca29cd0f6361d70c50d89babb2ad57514ce13`.


Symbolmarkenabfragen (Entry-Adressen) sind im Bundle als `analyze_function`-Records dokumentiert: `0x154dc4`, `0x1630bc`, `0x16b854`, `0x16d688`, `0x171d18`, `0x17adf4` und `0x17def4`. Zusätzlich wurden die relevanten Dispatchadressen abgefragt. Die nicht symbolisierten Ghidra-Funktionsgrenzen und nicht vorhandene Definitions-/CFG-Kanten sind keine Aussage über Laufzeitaufrufe.

## Validierung

`python3 validate.py` prüft Inputhashes, exakt 44 unique Dispatchzeilen, Range, CMP/Index- und LDRLS-Wortbindung, Tabellenbytes, Tabellenziele, Matrixstatus, Bundle-Zielidentität und vollständige ID-Abdeckung. Am 2026-10-18: PASS für Validator und self-reference-freies Manifest. Das ist Worker-Self-Review; eine unabhängige Prüfung wird nicht behauptet.
