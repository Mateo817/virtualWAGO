> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-097 — Referenzen und Veröffentlichung des IoDrvDal-Loader-Einstiegs

## Identität und Methode

**VERIFIZIERT** — Eingabe `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`, 25,976 Bytes; SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. Vor der Analyse geprüft. REA 6.5.0 / Ghidra 12.1.4, ARM:LE:32:v8, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

**REA-Lücke und begrenzter Fallback** — Ghidra erkennt `0x1362c` nur als `LAB_0001362c`, meldet bei `resolve_containing_procedure(0x1362c)` `not_in_procedure` und lehnt `procedure_info(0x1362c)` mit „No procedure exists“ ab. Auch `0x137bc` liegt laut Ghidra in keiner Prozedur. Damit sind Kontrollflusskörper und umgebende Dispatch-Tabelle in der REA-Funktionserkennung nicht als Prozedur abgrenzbar. Der generische GNU-`objdump` 2.44 konnte den ARM-ELF nicht disassemblieren („architecture UNKNOWN“); deshalb wurde der installierte Cross-Target `arm-linux-gnueabihf-objdump` 2.44 nur auf den Bereich ELF-VMA `0x362c..0x3800` begrenzt angewendet. Der relevante Ausgabeauszug steht in `objdump-bounded.txt`. Für Exportstatus wurde zusätzlich dessen dynamische Symboltabelle verwendet, da Ghidras `address_name`/`procedure_info` den Exportstatus nicht ausweisen. Keine Datei wurde geändert.

Das kanonische REA-Bundle `rea-evidence.json` enthält die Ghidra-Analyse samt Xrefs, Einzelinstruktionen, Adressabbildungen, `ComponentEntry`-Prozedurdossier und Pseudocode, sowie den REA-generischen objdump-Versuch. Für die gebundene Veröffentlichung sind u.a. relevant: `ev_22022d7746e2676e4b29bae4772678beaa26a7b9e6d6290c3991e5e5080f3104` (ComponentEntry-Prozedur), `ev_8afb35f6de2ccfaa95a3ca13f7ab95388e2a8b49756c5090269acb95e0558425` (Pseudocode), `ev_c9e4c3a74e83ad75a4b98d94a61d2e6413f168bc7645c401e705347055d663e4` (Store bei 0x14490), `ev_559d86ac3f92f050f72d798f489af9c75f1be187460f42564d91f920ad030197` (Literalbytes), `ev_0a50b88262089651ff8aa3d837d2dca34379ed8a742a8bfe52ea5c507ddbaf39` (Fallzweig bei 0x13650), `ev_57b0db97c6961be0399ff36e36887ffee5c5d63818c49251faaad4f996a068b7` (direkter Loader-Call) und `ev_644275f515ebb97931852ec39747d0d18df86156a57ff2b6cf71643932bea96d` (Xrefs zum Loader).

## Adressräume

Die REA/Ghidra-Adressabbildungen sind dateigebunden; Ghidra meldet Image Base `0x10000`. Für die hier beobachteten `.text`-Stellen stimmen ELF-VMA und Datei-Offset numerisch überein; die Ghidra-Adresse liegt um `0x10000` darüber. Beispiele: Loader ELF-VMA/Datei `0x2ddc`, Ghidra `0x12ddc`; Dispatcher `0x362c` / `0x362c` / `0x1362c`; Call `0x37bc` / `0x37bc` / `0x137bc`; Export `0x4448` / `0x4448` / `0x14448`. Eine mögliche Laufzeitadresse bzw. ein Laufzeit-Ladebias wurde nicht beobachtet.

## Beobachtungen

**VERIFIZIERT** — Ghidra-Xrefs zu exakt `0x12ddc` melden zwei Quellen: `0x12e34` als DATA (Datei-Offset `0x2e34`) und `0x137bc` als direkter `UNCONDITIONAL_CALL` (Datei-Offset `0x37bc`). Die Call-Instruktion ist ARM-`bl 0x00012ddc`, Bytes `86fdffeb`, direkt und nicht berechnet. `0x12ddc` trägt in Ghidra nur den automatisch vergebenen Namen `FUN_00012ddc`; der erste Befehl hat Bytes `f04f2de9`. Der DATA-Verweis `0x12e34` liegt im ausgeschlossenen Loader-Body und wurde außer Xref-Typ/-Adresse und Byteabbildung nicht erneut untersucht. Der Caller-Index bleibt **partial** und meldet eine ausgelassene Call-Referenzquelle; die Einzelinstruktion bei `0x137bc` belegt den direkten Call unabhängig davon.

**VERIFIZIERT** — GNU ARM-Cross-`objdump -T` weist `ComponentEntry` als dynamisches globales Funktionssymbol bei ELF-VMA `0x4448` aus. Ghidra benennt die Prozedur `ComponentEntry` bei `0x14448` (zu Datei-Offset `0x4448`). Im beobachteten Veröffentlichungspfad lädt die Instruktion bei Ghidra `0x14480` ein PC-relatives Literal, `0x1448c` addiert es zu `pc`, und `0x14490` speichert den so errechneten Zeiger mit `str r3,[r0,#0x18]`. Ghidras dekompilierte Sicht des Store-Werts lautet `&LAB_0001362c`; dies stimmt mit dem Dispatcher-Label und dem Ghidra-DATA-Xref `0x14490 -> 0x1362c` überein. Damit veröffentlicht die benannte dynamische Exportfunktion einen Zeiger auf den Dispatcher an Ausgabe-Offset `+0x18`. Das benennt die Exportfunktion und den numerischen Store-Ort; es gibt dem Feld keine semantische Bezeichnung.

Ghidra-Xrefs zu `0x1362c` enthalten zusätzlich `0x14554` als sekundäre DATA-Referenz (Datei-Offset `0x4554`). Dort liegt `stmia lr!,{r0,r1,r2,r3}`; eine konkrete Pointer-Publikation zu `0x1362c` lässt sich aus diesem register-indirekten Operand nicht ableiten. **OFFEN** bleibt daher die Rolle dieser zweiten Referenz.

**VERIFIZIERT** — Der begrenzte ARM-Disassemblyauszug zeigt am Dispatcher-Anfang `sub r3,r0,#2`, danach `cmp r3,#13` und `addls pc,pc,r3,lsl #2`. Für eingehendes `r0=3` ergibt sich `r3=1`; nach ARM-PC-Relativierung adressiert der berechnete Sprung die Tabelleneintragung bei ELF/Ghidra `0x3650/0x13650`, welche direkt nach `0x3738/0x13738` verzweigt. Das ist ein numerisch belegter Dispatch-Fall, keine Behauptung über die API-Bedeutung von `r0`.

Bei `0x13738` beginnt ein bedingter Pfad: der dort gelesene Wert wird bei `0x13744` gegen null geprüft; bei Nicht-Null verzweigt `bne` nach `0x13800`. Der Nullpfad erreicht einen berechneten Call bei `0x13770`; nur für dessen Null-Rückgabepfad setzt `subs r4,r0,#0` den Laufzähler auf null. Nach den Schrankenprüfungen beginnt die Schleife bei `0x137a4`:

- `r2` erhält den vor der Aktualisierung gelesenen Wert `[r5 + 0x10]` (`ldr` bei `0x137a4`); unmittelbar danach wird `[r5 + 0x10]` auf `r2 + 1` geschrieben (`0x137b0..0x137b4`). Der initiale Speicherwert ist aus diesem Nachweis **OFFEN**; es wird kein erster Loader-Index behauptet.
- `r1` erhält `r6` (`cpy r1,r6` bei `0x137a8`). Der Literalwert bei Ghidra `0x1435c` ist durch vollständige REA-Bytes `01 20 06 10` little-endian als `0x10062001` belegt.
- `r0` erhält `r7` (`cpy r0,r7` bei `0x137ac`); zuvor wurde `r7 = r5 + 0x14` berechnet (`0x1379c`).
- `r3` erhält `sp + 0x5c` (`0x137b8`). Dann ruft `bl` bei `0x137bc` direkt `0x12ddc` auf. Nach Rückkehr führt die Schleife die Zählerprüfung aus und erhöht `r4` bei `0x137e8`.

Diese positionalen Registerflüsse sind Instruktionsbeobachtungen. Sie belegen weder Prototyp noch Feld-/Parametersemantik. Der Pfad kann den Loader erreichen; die bedingten Abzweige und der indirekte Aufruf schließen eine pauschale Behauptung aus, dass jeder `r0=3`-Fall dort ankommt.

## Lifecycle-Bindung, Alternativerklärung und Restunsicherheit

**VERIFIZIERT** — Es gibt eine benannte externe Bindung auf der Ebene des ELF-Exports: `ComponentEntry` ist als dynamisches globales Funktionssymbol identifiziert und veröffentlicht im beobachteten Store bei `+0x18` den Dispatcher-Zeiger `0x1362c`; ein numerischer Dispatch-Fall erreicht dessen Bereich und kann bedingt in die Schleife mit Call bei `0x137bc` gelangen.

**OFFEN** — Die semantische Lifecycle-Rolle des Felds `+0x18`, die Bedeutung des Registers `r0` laut API, und die Identität der aufrufenden Laufzeit bleiben unbewiesen. Daher wird keine benannte Lifecycle-Funktion/Phase behauptet. Ghidra-Funktionsbereich für `ComponentEntry` ist `0x14448..0x14623`, während die dynamische ELF-Symboltabelle Größe `0x230` meldet; die Unterschiedlichkeit ist dokumentiert und wird nicht als gleichwertige Body-Grenze interpretiert. `ComponentEntry`-Pseudocode wurde nur zur Ermittlung der Veröffentlichungszuweisung gelesen; dessen übrige Initialisierung ist nicht Gegenstand dieser Schlussfolgerung.

**HYPOTHESE (Alternativerklärung)** — `ComponentEntry` könnte einen allgemeinen Rückruf-/Dispatcherzeiger in einem Exportvertrag bereitstellen; ohne Vertragstext, aufrufende Runtime oder ein belegtes Feldlayout sagt `+0x18` nicht, dass es sich um eine Lifecycle-Route handelt. Der beobachtete Register- und Kontrollfluss ist mit dieser und anderen Verwendungen vereinbar.

## Abdeckung, Ausschlüsse und Review

Loader-Xrefs: zwei von Ghidra zurückgelieferte Quellen, mit direktem Einzelinstruktionsnachweis des Calls. Dispatcher-Xrefs: `0x14490` und `0x14554`; nur `0x14490` wird als Veröffentlichung belegt. Der Dispatcher-Einstieg und `0x137bc` sind von Ghidra nicht in einer Prozedur abgegrenzt; begrenzter Cross-objdump deckt ELF-VMA `0x362c..0x3800` ab, nicht den restlichen Dispatcher. Keine leere oder partielle Abdeckung wird als Negativbeweis verwendet.

Ausgeschlossen: Analyse des Loader-Bodys `0x12ddc..0x1331b` außer Eintrittsidentität und Xref-Adresse; vollständige Dispatchersemantik außerhalb des nötigen `r0=3`-Pfads; weitere Rootfs-Dateien, IoDrvKbus, Geräte/Netz/VM, Runtime/Hardware, API-/Structsemantik. Keine gemeinsamen Dateien oder Repositorydateien geändert.

Validator: `validate.py` bindet Eingabehash, REA-Bundle, beide Xref-Mengen, Export-/Publikationslane, ausgewählte Dispatcher-/Schleifenbefehle, Literalwert und bounded objdump-Auszug semantisch. **Self-Review (Workerprüfung): PASS**; Validator und `sha256sum -c SHA256SUMS` liefen erfolgreich. Andere Tests: **NOT_RUN**.
