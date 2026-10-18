> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-131 — exakte Caller von `CMLoadComponent3`

## Ergebnis

**VERIFIZIERT — direkte statische Aufrufstellen:** Für den Entry `CMLoadComponent3` bei `0x002ffc84` enthält die vollständige ARM-Objdump-Suche zwei direkte Call-Link-Referenzen: `0x002ffe48` aus `cmloadcomponent` und `0x0031a648` aus `AppLoadCIntegrationModule`. Zusätzlich finden sich zwei direkte Tail-Transfers (`b`, kein `bl`) aus `CMLoadComponent` bei `0x002ffe28` und `CMLoadComponent2` bei `0x002ffe74`. Der vollständige Trefferbestand steht in [fallback-evidence.md](fallback-evidence.md), Evidence-IDs `FB-XE164-131-01` und `FB-XE164-131-02`.

**VERIFIZIERT — Argumentquellen an der Funktionsgrenze:** `cmloadcomponent` übergibt Register `r0` und `r3` aus zwei Wörtern des eingehenden Zeigers und die Konstanten `r1=0`, `r2=2`. `AppLoadCIntegrationModule` übergibt `r0` aus seinem eingehenden `r1`, `r1` aus seinem eingehenden `r2`, `r2=16` und `r3=&local(fp-16)`. Die beiden Tail-Wrapper reichen `r0` unverändert durch und setzen/übergeben die übrigen Register entsprechend der Tabelle im Evidenzbeleg. Die nicht im Funktionskörper sichtbare Herkunft eingehender Parameter oder Speicherinhalte wurde nicht weiter interpretiert.

**Dal-Bezug:** **Nein** in den unmittelbar sichtbaren Argumentquellen aller vier direkten statischen Transferstellen: keine enthält einen Dal-Modulnamen, einen konkreten Dal-Pfad oder einen Dal-spezifischen Datenverweis. Die direkten `bl`-Caller übergeben entweder opake Funktionsparameter oder Werte aus einem eingehenden Zeiger. Es wurde kein konkreter Dal-relevanter Literal-/Datenverweis sichtbar; deshalb wurde keine Name-/Pfad-Lane weiterverfolgt.

**Auflösung des späteren `ComponentEntry` auf IoDrvDal:** **OFFEN.** Der exakte statische Aufrufbestand bindet den generischen `CMLoadComponent3`-Aufruf nicht an IoDrvDal. Daraus folgt keine Aussage über spätere dynamische Namensauflösung oder Laufzeit; diese wurden nicht untersucht. Insbesondere werden weder ein Modulname aus einer Funktionsbezeichnung noch die Verfügbarkeit eines Symbols als Bindingvertrag verwendet.

## Eingaben und Identität

| Eingabe | Größe | SHA-256 | Verwendung |
|---|---:|---|---|
| `codesys3` | 5.181.396 Byte | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | exaktes Ziel-ELF |
| WP-XE164-123 `report.md` | 6.524 Byte | `b96bf455d44125ed91835119399cd90fd04410888e74ee48afaf3525a4b513ee` | vorheriger Loaderkontext; Hash/Größe verifiziert |
| WP-XE164-128 `report.md` | 4.907 Byte | `9bc728298381283b376eadb1a6448cbb1219f8af5d1cdc343245707ce79241b4` | vorheriger Argument-/Handoff-Kontext; Hash/Größe verifiziert |

Die anfängliche Angabe `12.780` Byte für WP123 wurde durch die während der Arbeit erhaltene Korrektur auf `6.524` Byte ersetzt und nicht übernommen.

## Methode und Evidence

REA wurde zuerst benutzt. Die Zielidentität wurde mit REA `open_binary` hash-gebunden geöffnet: ELF, ARM, SHA-256 wie oben. REA-Server/Client: `rea-agents 6.5.0`, Codex MCP client `0.162.1`; Ghidra `12.1.4`, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

REA `procedure_callers(0x2ffc84)` endete nach 300 Sekunden mit `timed out awaiting tools/call`. Der identische Aufruf wurde nicht wiederholt. Gemäß Fallbackregel wurde stattdessen GNU ARM-cross-objdump verwendet: `arm-linux-gnueabihf-objdump`, GNU Binutils for Debian `2.44`. Die direkte Transfer-Suche lief über die vollständige disassemblierte Datei; anschließend wurden nur die vier schmalen Caller-/Argumentfenster gelesen. Rizin `0.9.1` war verfügbar, wurde aber nicht benötigt. Es gibt deshalb in diesem Paket keine REA-Caller-Evidence-ID oder REA-Bundle; die dokumentierten Fallback-Belege mit Befehlen und rohen Ausschnitten sind `FB-XE164-131-01` und `FB-XE164-131-02` in [fallback-evidence.md](fallback-evidence.md).

Die Suche ist auf materialisierte direkte statische `b`/`bl`-Ziele im disassemblierten ARM-ELF begrenzt. Indirekte Caller und zur Laufzeit erzeugte oder über Daten aufgelöste Funktionszeiger sind ausgeschlossen. Die ursprüngliche Aufrufanalyse timeoutete; der fallback-basierte statische Befund ersetzt keine Behauptung über dynamische Vollständigkeit.

## Alternative Erklärungen und Restunsicherheit

- Die opaken Parameter und der durch `cmloadcomponent` dereferenzierte Zeiger können upstream einen Pfad oder Namen enthalten; diese Werte sind am untersuchten Funktionsrand nicht statisch sichtbar.
- Die Funktion kann zur Laufzeit durch indirekten Aufruf oder dynamische Auflösung von weiteren Stellen erreicht werden; solche Kanten liegen außerhalb der exakten direkten statischen Caller-Suche.
- Ein konkreter `ComponentEntry`-Zeiger und seine Zuordnung zu IoDrvDal werden durch diese Caller-Fenster nicht belegt.

## Prüfstatus

| Prüfung | Status |
|---|---|
| Zielgröße und SHA-256 | PASS |
| WP123-Größe und SHA-256 (korrigierte Größe) | PASS |
| WP128-Größe und SHA-256 | PASS |
| Direkte statische `b`/`bl`-Treffer auf exakt `0x2ffc84` vollständig im Fallback-Suchlauf | PASS |
| Unmittelbare Registerargumente an den vier Transferstellen | PASS |
| Dal-Literal/-Pfad in diesen Argumentfenstern | PASS — keines sichtbar |
| REA `procedure_callers` | BLOCKED — Timeout nach 300 Sekunden; einmaliger Fallback dokumentiert |
| Laufzeit, VM, Netzwerk, Geräte und Hardware | NOT_RUN |
| Tests | NOT_RUN |
| Validator | PASS (siehe `validator-result.txt`) |

Self-Review durchgeführt. Kein unabhängiger Review oder weiterer Workerlauf wird behauptet.
