> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-022 — Seed E00808 vor E00888

## Ergebnis

VERIFIZIERT: Auf Basis der 17,110-Byte Composite mit SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` ist der Seed bei Fileoffset `0x0808` unter der angenommenen Basis `E00000` statisch bis einschließlich Instruktion `E00886` dekodierbar. Der abgegrenzte Seed-Bereich umfasst ausschließlich `0x0808..0x0887`; `E00888` wurde nicht dekodiert. Die vollständige Instruktionsfolge und alle statisch erreichbaren Kanten stehen in `instructions.tsv` und `edges.tsv`.

Der lokale Kontrollfluss enthält bedingte Abzweige bei `E00824`, `E0082C`, `E00832`, `E0085A`, `E00862`, `E0086A`, `E00870`, `E00878` und `E00882`. Alle direkten Ziele liegen im Seed-Bereich. Drei erreichbare Rückkehrinstruktionen liegen bei `E00838`, `E0087E` und `E00886`. Rückkehrgrenzen werden nur aufgrund der dekodierten `rets`-Instruktionen angenommen; keine Sprungkante verlässt den Bereich. Die Schleifenrückkanten sind `E0082C→E00822`, `E0086A→E00858` und `E00882→E0080A`.

Im Seed-Körper wurde kein direkter Call dekodiert. Die einzelne erlaubte Caller-Instruktion bei Fileoffset `0x0A16` ist bytegebunden als `calls 0xe00808` (`dae00808`) belegt und in `calls.tsv` isoliert. Caller-Body und Callee-Body wurden nicht traversiert.

Die numerischen Operanden und Adressausdrücke sind wortgetreu in `references.tsv` erfasst, darunter Immediate-Werte, die disassemblerseitigen Adressausdrücke `0xfe06:0x2a26`, `0xfe06:0x2a30`, `0xfe06:0x2a2c`, `0xfe06:0x30bc`, `0xf0e2`, Bit-Ausdrücke `0xf1b4.0`/`.11`, Registerbitindizes und lokale Sprungziele. Das sind ausschließlich statische Zahlen-/Operandbeobachtungen. Daraus werden keine DPP-, SFR-, Registerbank-, ABI- oder Hardwarebedeutungen abgeleitet.

## Methode und Evidence

- REA zuerst: `open_binary` auf dem gelieferten Composite scheiterte mit `target_unavailable` / `unsupported binary format`; die Datei blieb unverändert. Dieser Explorationsdatensatz wird nicht als Befundbeleg verwendet.
- Kanonischer fokussierter Befund: REA-Operation `execute_rizin_command`, Evidence-ID `ev_4c0f258b64150804c7e43d59e2197931ebb312b3aa1eaa26b7f4d53f91d3a294`, Provider `rizin`; `stdout` umfasst `pD 128 @ 0x0808` und `pd 1 @ 0x0a16`, ohne stderr, ohne Trunkierung und mit `artifact_changed=false`. Rizin-Datensatz meldet Provider-Version `null`.
- Lokaler Read-only Versionsnachweis: Rizin `0.9.1`, Build `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`, `linux-x86-64`.
- Exakte Decoder-Konfiguration im REA-Aufruf: MCP command `e asm.arch=c166; e asm.bits=16; e cfg.bigendian=false; e io.va=false; e asm.bytes=true; e scr.color=false; pD 128 @ 0x0808; pd 1 @ 0x0a16`; REA setzte CLI-Optionen `-N -q -c <command> <path>`. Das ist rohe Fileoffset-Analyse; keine Binärbasis wird für die Decoderadressen addiert. Die Befundtabellen übertragen Offset zu Analyseadresse ausdrücklich mit der vom Auftrag angenommenen Basis `E00000`.
- Referenzierter Ghidra-Replay-Nachweis: `composite-replay.md`, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`; dieser beschreibt Ghidra 12.1.4 / `C166:LE:16:default` / `tasking`. Ghidra wurde für dieses WP nicht erneut ausgeführt, da die angeforderte lokale CFG- und Caller-Dekodierung durch den fokussierten Rizin-Lauf abgedeckt war.
- PASS: `validate.py` prüft Input-SHA-256, Offset- und Adressabbildung, Bytebindung jeder Instruktion/Referenz, zusammenhängende Instruktionsdeckung genau bis `0x0887`, CFG-Endpunkte und Erreichbarkeit, Rückkehrterminals, Seed-interne Call-Abwesenheit sowie Caller-Bytes und -Ziel. Zusätzlich müssen die Output-Datei-Hashes in `SHA256SUMS` stimmen.
- SHA-256 des Evidence-Bundles und aller Dateien: `SHA256SUMS`.
- Der exportierte Bundle ließ sich über REA `import_evidence_bundle` erfolgreich validieren: `total=2`, `unknowns_added=0`; `imported=0`, weil beide Evidence-IDs bereits in derselben Sitzung vorhanden waren.

## Evidenzstatus, Alternativen und Grenzen

Status des statischen Befunds: VERIFIZIERT; Teststatus des zugehörigen lokalen Validators: PASS. HYPOTHESE: Ein alternatives Processorprofil oder eine Code-/Datenklassifikation könnte abweichende Dekodierungen erzeugen. OFFEN: dynamische Reachability, Semantik der Operanden und Verhalten außerhalb des geprüften Bereichs. BLOCKED: keiner der geforderten Offline-Nachweise.

Die Dekodierung ist Werkzeugableitung, kein Originalquelltext und keine Laufzeitbeobachtung. Direkte bedingte Ziele sind aus dem Rizin-Disassembly abgelesen; fall-through-Kanten folgen der Instruktionslänge und dem bedingten Fluss der Mnemonics. Der Validator verifiziert Adressen, Bytes, Zielmitgliedschaft und Graph-Erreichbarkeit gegen die Composite-Bytes, nicht die Semantik der C166-Instruktionen unabhängig von Rizin.

Alternativerklärung: Der Bereich könnte in einer anderen Daten-/Codeklassifikation oder einem abweichenden Processor-Profil teilweise als Daten statt als Code behandelt werden. Der reproduzierbare Ghidra-Replay liefert eine zweite, versions- und processorprofilgebundene Referenz für den Composite-Import, wurde hier aber nicht als zusätzlicher Funktions- oder Cross-Reference-Lauf wiederholt. Die angenommene Basis `E00000` stammt aus dem Auftrag/Replay und ist keine Eigenschaft von `io.va=false`.

Restunsicherheit: Rizin Evidence kennt die konkrete Binary-Version des Befehlsproviders nicht; die lokale Version wurde getrennt protokolliert. C166-Dekoderübereinstimmung, Sprungbedingungswahrheit und Semantik der numerischen Adressen wurden nicht unabhängig nachgewiesen. Dynamische Reachability, nichtdekodierte Laufzeitkanten, Interrupt-/Exception-Verhalten und alles nach `E00887` bleiben OFFEN. Die Caller-Bytes beweisen nur die einzelne statische Instruktion, keine Caller-Funktion oder Call-Konvention. Die gescheiterte REA-Standardformatöffnung und der erste, falsch als CLI-Argumentvektor übergebene Rizin-Aufruf sind Fehlversuche und keine Befunddaten.

Scope-Sperre: keine Auswertung der angrenzenden Bereiche `E007D4` oder `E00888`, keine Analyse des Caller-Bodys ab `E00972`, kein Traversieren eines direkten Calls, keine Interpretation von DPP/SFR/ABI/K-Bus, keine Geräte-, Netz- oder VM-Aktion, keine Änderung an Repository- oder gemeinsamen privaten Dateien. Arbeitsprodukte liegen nur im bezeichneten Worker-Verzeichnis.
