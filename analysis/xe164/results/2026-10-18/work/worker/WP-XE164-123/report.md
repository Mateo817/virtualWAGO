> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-123 — codesys3 `ComponentEntry` loader path

## Befund

**OFFEN / nicht belegt:** Im exakten FW31-Programm ist eine statische Auflösung des Exportnamens `ComponentEntry` auf einen Modulfunktionszeiger sichtbar. Die zwei untersuchten Procedures belegen jedoch keinen Aufruf dieses Zeigers mit einem ersten Argument, dessen Position `+0x34` aus einer konkreten statischen Quelle hergeleitet werden kann.

Der einzige exakte ASCII-Treffer liegt in `.rodata` bei Ghidra-Adresse `0x345abc` (Dateioffset `3365564`). Vollständige Suche in den geladenen, initialisierten Ghidra-Speicherblöcken fand genau diesen Treffer. Der String hat einen materialisierten Dateneingangsverweis von `0x7d3fc` in `MainLoadComponent` (`0x7d36c..0x7d433`). `find_xrefs_to_name("ComponentEntry")` bleibt ungelöst: es gibt in Ghidras adressierbarem Namensinventar keinen gleichnamigen Symbolnamen; die statisch beobachtete Verwendung ist ein String für die Namensauflösung.

In `MainLoadComponent` setzt `0x7d3f4..0x7d3fc` `r1` auf `0x345abc`. Bei `0x7d400` folgt ein direkter Aufruf des Thunks `<EXTERNAL>::SysModuleGetFunctionPointer` (`0x7c500`, Thunkziel `0x61d0a4`). Die Instruktion `0x7d3f8` speichert zuvor den Modul-Ladewert aus `r0` via `*param_3`; das spätere `r0` des Funktionsauflösers wird in der Procedure als Status behandelt. `param_4` wird unverändert als drittes Registerargument `r2` an `0x7c500` weitergegeben. Der unmittelbare Aufrufer reicht als `param_4` die Adresse von `local_64` weiter und liest diese Stackposition anschließend als Callback-Ziel. Daraus folgt, dass über diesen Zeiger ein aufgelöster Wert bereitgestellt wird; der Export wird in `MainLoadComponent` selbst nicht aufgerufen. Der Body enthält keinen Zugriff mit Displacement `+0x34`.

Der unmittelbare Aufrufer `CMLoadComponent3` (`0x2ffc84..0x2ffe07`) reserviert bei `0x2ffce0` zwei lokale Ausgabewörter und ruft `MainLoadComponent(param_1,param_2,&local_68,&local_64)`. Der Wert aus `local_64` wird später bei `0x2ffd2c` in den Stackslot `[r11-0x48]` übernommen und die Adresse des umgebenden lokalen Blocks an `FUN_002fc530` (`0x2fc530`) übergeben. In derselben Procedure sind indirekte Calls bei `0x2ffd60` und `0x2ffd78` sichtbar; deren Zielwerte werden unmittelbar zuvor aus den verschiedenen Stackslots `[r11-0x44]` und `[r11-0x40]` geladen. Die disassemblierte Procedure bindet diese Aufrufziele nicht an den bei `[r11-0x48]` gespeicherten `ComponentEntry`-Zeiger. Das kann statisch nicht ausschließen, dass `FUN_002fc530` Speicherinhalte oder Callbacks ändert.

In den zwei untersuchten Procedures ist weder ein Lesen/Setzen eines Zeigers an relativem Offset `+0x34` noch ein konkreter Quellwert für eine solche Position sichtbar. Daher lautet die Antwort auf die gestellte kombinierte Frage **nicht verifiziert**; dies ist kein Nachweis, dass es in weiteren Aufrufstufen oder Modulcode keinen solchen Pfad gibt.

## Beobachtungen und Scope

- Eingabe `codesys3`: 5,181,396 Bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`; REA erkannte ELF / ARM.
- Eingabe `libIoDrvDal.so.1.0.2`: 25,976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. Nur Hash-/Grenzkontext; in diesem Paket nicht analysiert.
- Root-Synthese WP-XE164-122 vor Verwendung verifiziert: SHA-256 `d66a5be8d965d77d381860c77d9d5985c4fe5efcc9d8bd90f1646c65e1641aec`. Deren Aussagen wurden nicht als Ersatz für neue Zielbefunde verwendet.
- REA/Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- Exakte ASCII-Suche: REA `search_bytes` für `43 6F 6D 70 6F 6E 65 6E 74 45 6E 74 72 79`; vollständig über 6,273,971 Bytes geladenen initialisierten Speicher, eine Übereinstimmung bei `0x345abc`, kein Cursorrest. Nicht geladen waren ausschließlich `.ARM.attributes`, `.shstrtab` und `_elfSectionHeaders`; der uninitialisierte `EXTERNAL`-Block wurde ausgelassen. Somit gilt die Vollständigkeit für geladene initialisierte Speicherbereiche, nicht für nicht geladene Sektionsmetadaten oder zur Laufzeit erzeugte Speicherinhalte.
- REA `search_strings` findet denselben einen definierten String. `xrefs(0x345abc)` liefert nur `0x7d3fc`; `inspect_native_instruction(0x345abc)` bestätigt den Quellverweis als `PARAM`/Dateneingangsreferenz von `0x7d3fc`. Dieser Typ ist kein Aufrufbeweis.
- Begrenzte Procedure-Untersuchung: genau `MainLoadComponent` und unmittelbarer Aufrufer `CMLoadComponent3`. Für beide liegen REA-Pseudocode, Assembler, Aufrufbeziehungen und Wertfluss im Bundle. Keine breitere Manageranalyse.
- Statische Adressräume sind Ghidra-Adressen von `codesys3`; das Modul-Thunkziel `0x61d0a4` ist ebenfalls nur als addressiertes externes Importziel klassifiziert.

## Alternative und Restunsicherheit

`CMLoadComponent3` übergibt den Block mit dem aufgelösten Zeiger an `FUN_002fc530`; diese ausgelassene Procedure könnte den Zeiger indirekt verwenden, Callback-Felder umschreiben oder Werte aus anderen Quellen vorbereiten. Auch ein späterer Wrapper oder der geladene Modulcode könnte ein Argument mit relativem Offset `+0x34` erzeugen. Das wäre zusätzliche Stufe außerhalb der vorgegebenen Obergrenze von zwei Loader-/Call-Procedures und ist hier weder bestätigt noch widerlegt. Ferner legt Ghidras ABI-/Typinferenz keine vollständige Funktionstyp- oder Structsemantik fest; es werden daher keine Funktionssignatur für den Export und keine Feldnamen behauptet.

## Validator und Status

- Semantischer Validator: `semantic_validator.js`; soll die Hashbindung, eindeutigen ASCII-Treffer, Xref, Loaderauflösung, analysierten Procedure-Bodies sowie das Fehlen eines beobachteten `+0x34`-Displacements in den zwei gebundenen Assemblies prüfen.
- Validatorlauf: **PASS** (siehe nachfolgendes `validator-result.txt`).
- Tests: **NOT_RUN** (keine Softwaretests angefordert oder ausgeführt).
- Laufzeit-/Geräte-/Netzwerk-/VM-/Hardwareprüfung: **NOT_RUN**.
- Befundstatus: **OFFEN** hinsichtlich des gesuchten vollständigen `+0x34`-Callpfads; die obigen Loader-/String-Beobachtungen sind **VERIFIZIERT** als statische Artefaktbefunde.
- Self-Review: durchgeführt; kein unabhängiger Review oder Workerlauf behauptet.

## Dateien

- `rea-evidence-bundle.json`: kanonisches REA-Bundle, 8 Records, 0 Unknowns.
- `report.md`: dieser Bericht.
- `semantic_validator.js`: semantischer Paketvalidator.
- `validator-result.txt`: Ergebnis des Validators.
- `SHA256SUMS`: Hashes der Paketdateien außer dieser Hashliste selbst.
