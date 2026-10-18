> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-050 — Kontrollfluss ab Seed E03ABA

## Ergebnis

**VERIFIZIERT (statisch, Rizin-C166-Dekodierung; Umfang [0x3ABA, 0x3B4E)):** Der Seed dekodiert als zusammenhängende Folge von 61 Instruktionen über exakt 148 Bytes. Jede der 61 Instruktionen ist vom Seed aus im aus direkten Branchzielen, Fallthroughs und terminalen Rückkehren abgeleiteten Graphen erreichbar.

Bei `0x3ABE` teilt ein bedingter Sprung den Strom: Der Fallthrough-Weg endet mit `rets` bei `0x3AE6`; der Sprungpfad setzt bei `0x3AE8` fort. Bei `0x3AF2` verzweigt die Folge erneut. Der Fallthrough-Pfad führt über den direkten unbedingten Sprung bei `0x3AF8` zu `0x3B0E`; der bedingte Zielpfad über `0x3AFA..0x3B0C` konvergiert dort. Im letzten Abschnitt liegen bedingte Sprünge bei `0x3B3A` und `0x3B44`; `0x3B3E` ist ein direkter unbedingter Sprung zu `0x3B46`. Die Pfade konvergieren bei `0x3B48` und enden mit `rets` bei `0x3B4C`. Innerhalb des Umfangs ist kein Call dekodiert.

Der isolierte Einzelbefehl bei Caller-Offset `0x0D68` lautet `calls 0xe03aba`, Bytes `dae0ba3a`. Er belegt einen direkten Call-Operand zum Seed; eine Rückkehrkante im Caller wird nicht behauptet.

## Exakte Tabellen

- [instructions.tsv](instructions.tsv): 61 beobachtete Instruktionen mit Bytes, Länge, Kontrollflussklasse, Reachability und Nachfolgern.
- [edges.tsv](edges.tsv): direkte Sprung- und Fallthroughkanten; Rückkehrinstruktionen haben kein erfundenes Ziel.
- [calls.tsv](calls.tsv): ausschließlich der vorgegebene isolierte Caller.

Instruktions- und Sprung-Offsets sind Composite-Dateioffsets. `E03ABA` entspricht der syntaktischen Replay-Adressschreibweise `0xE00000 + 0x3ABA`; daraus wird keine Laufzeit- oder ABI-Aussage abgeleitet.

## Methode, Fundstellen und Toolstatus

- Eingabe: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`; frisch geprüft: 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- REA `open_binary` wurde zuerst versucht und meldete `unsupported_target / unsupported binary format`. Die beobachtete Providerlücke begründete den dokumentierten Rizin-C166-Fallback via REA `execute_rizin_command`.
- Begrenzter erfolgreicher Aufruf: `e asm.arch=c166; e asm.bits=16; p8 148 @ 0x3aba; e asm.arch=c166; e asm.bits=16; pD 148 @ 0x3aba; e asm.arch=c166; e asm.bits=16; pdj 1 @ 0x0d68`. REA-Aufrufprofil `-N -q`; Provider Rizin; Evidence `ev_a6b658ee338e15bd1c65468c1356f719836ed6955457e0e4a9ac52ea884c9ad0`; Exit-Code 0, leere Stderr-Ausgabe, Eingabe danach unverändert. Byte-Dump und `pD` decken exakt 148 Bytes ab; der Caller-Dump ist eine einzelne Instruktion.
- Die Evidence meldet keine ausführbare Rizin-Version (`provider.version=null`). Ein Versionsprobeversuch scheiterte am Befehlsparser. Toolversion: **OFFEN**. Es gab keinen unabhängigen Decodervergleich.
- Die 61 Instruktionsanfänge sind lückenlos; ihre Längen summieren sich auf 148. `0x3B4C` ist `rets` und endet bei der exklusiven Grenze `0x3B4E`.
- Seed-Reachability wurde manuell aus den in `pD` beobachteten C166-Sprungzielen, den unmittelbar folgenden Instruktionsadressen und terminalen `rets` abgeleitet. `cc_UC` ist als unbedingter Sprung behandelt. Calls werden nicht als zurückkehrend angenommen. Es lief kein globaler CFG-/Xref-Lauf.

## Status, Alternative und Restunsicherheit

- Bytes, Instruktionsgrenzen im begrenzten Decoderoutput und Direktkanten: **VERIFIZIERT** für diese Composite-Revision und Rizin-C166-Dekodierung; ohne unabhängige Gegenprüfung.
- Die 148-Byte-Ghidra-Grenze bleibt Eingabeprämisse/**HYPOTHESE**, hier nicht neu bestätigt.
- Alternative: Eine abweichende C166-Dekodierung oder Deutung der Bedingungssuffixe könnte Instruktionsgrenzen oder Kanten ändern. Der exakte 148-Byte-Rohdump ist in der Evidence enthalten.
- Restunsicherheit: Rizin-Version fehlt; keine unabhängige Dekodierung; statische Kanten sind keine Laufzeitbeobachtung. Bedeutung/ABI/SFR, Runtime/Hardware und weitere Caller bleiben **OFFEN** und ausgeschlossen.
- [rea-bundle.json](rea-bundle.json) enthält ein finding-only kanonisches REA-Bundle mit genau einer passenden, exakt begrenzten erfolgreichen Beobachtung. [validate.py](validate.py) validiert Identität, Umfang, Tabellen gegen die Evidence, Kanten und Seed-Reachability.

## Dateien und Hashes

Die Paketdateien sind in `SHA256SUMS` gehasht; die Liste selbst wird nicht selbstgehasht.
