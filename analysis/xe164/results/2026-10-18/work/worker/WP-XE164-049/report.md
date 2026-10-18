> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-049 — Kontrollfluss ab E00C72

## Finding

**VERIFIZIERT (begrenzte statische Dekodierung; Kontrollfluss daraus abgeleitet):** Unter Rizin 0.9.1 mit der gesetzten C166/16-Bit/Little-Endian-Konfiguration dekodieren die 158 Bytes `[0x0C72, 0x0D10)` als 49 lückenlos aneinander anschließende Instruktionen. Vom Seed `E00C72` ergibt sich innerhalb dieses Intervalls eine einzelne lineare Fall-through-Kette mit 48 Kanten. Die letzte Instruktion ist `rets` bei `E00D0E`, deren zwei Bytes genau bis zum benachbarten, ausgeschlossenen Ziel `E00D10` reichen. Im Intervall ist kein Call, bedingter Sprung oder unbedingter Sprung dekodiert; `E00D10` ist daher kein Ziel einer im Slice beobachteten Kante. Diese Aussage ist keine Ghidra-Funktionsgrößenbestätigung.

Der isolierte Caller bei `E00D12` hat Bytes `DA E0 72 0C`; Rizin dekodiert `calls 0xe00c72`. Die statische Zieladresse stimmt numerisch mit dem Seed überein. Es wird nicht angenommen, dass dieser Call zurückkehrt oder welcher Code danach ausgeführt würde.

## Input und Methode

Eingabe: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`, 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`. Hash und Größe wurden vor der Analyse und der unveränderte Hash nach beiden Rizin-Aufrufen beobachtet.

REA `open_binary` wurde zuerst aufgerufen und lehnte das unbekannte Rohformat als `unsupported binary format` ab. Wegen dieser beobachteten Lücke wurde der dokumentierte Rizin-C166-Fallback über REA `execute_rizin_command` verwendet. Lokale Version: Rizin 0.9.1, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`; REA-Provider meldet `Rizin`, Version `null`. Aufrufe liefen mit `-N -q`, `e io.va=false`, `e asm.arch=c166`, `e asm.bits=16`, `e cfg.bigendian=false` und `e asm.bytes=true`; die erste Abfrage deaktivierte zusätzlich Farbe. Es wurde keine globale Analyse und kein Xref-Lauf gestartet.

REA-Evidence `ev_cda26cf0c90311ac4faa6adf7010c8aa38df75a99783452818c8ebe1ec7083f3` enthält die exakten Bytes des Intervalls, den Decode von `0x0C72` bis einschließlich der Instruktion bei `0x0D08` sowie den einzelnen Caller bei `0x0D12`. Die Abfrage begrenzte `pD` auf 152 Bytes; die letzten drei Instruktionen vor `0x0D10` wurden separat mit je einer Instruktion pro Adresse dekodiert. Evidence `ev_1ffa554db7229d13046e8d3729c3a1a565e243ecb6c4c4619095f57099b2ab42` zeigt für `0x0D0A`, `0x0D0C` und `0x0D0E` die jeweiligen Bytes und Dekodes. Beide Evidence-Einträge berichten vollständige Ausgabe, Exit-Code 0 und unveränderten Eingabehash.

## Tabellen und Prüfbarkeit

- `instructions.tsv`: vollständige Instruktionsfolge, Datei-Offsets, angenommene E-Adressen, Bytes, Längen, Rizin-Text und Reachability ab Seed.
- `edges.tsv`: alle 48 aus Instruktionslängen und linearem Flow abgeleiteten Fall-through-Kanten sowie der einzelne, separat erfasste Caller.
- `rea-evidence-bundle.json`: kanonischer REA-Export mit genau den beiden begrenzten Records `ev_cda26cf0c90311ac4faa6adf7010c8aa38df75a99783452818c8ebe1ec7083f3` und `ev_1ffa554db7229d13046e8d3729c3a1a565e243ecb6c4c4619095f57099b2ab42`; Export meldet 2 Records und 0 Unknowns.
- `validate.py`: prüft Eingabegröße/-hash, lückenlose Tabellenabdeckung, Bytes gegen Eingabe, Endgrenze, Return-Ende, Kantenanzahl sowie kanonische Record-IDs, Input-Digest, Operation, Exit-Code und Abfrage-Scope.

## Alternative und Restunsicherheit

Die Datei ist ein Header-loses Composite; die Abbildung Datei-Offset `n` auf Adresse `E00n` folgt dem im Auftrag benannten E-Adressraum und Dateinamen, nicht einer durch REA festgestellten Load-Map. C166-Modus, Little-Endian-Einstellung und der Seed als Instruktionsbeginn sind Analyseannahmen. Eine andere Code-/Daten-Deutung oder Dekodierkonfiguration kann die Struktur ändern. Die Größenhypothese von Ghidra ist nicht geprüft. Diese Ausgabe belegt weder Laufzeitverhalten noch Semantik oder ABI; sie belegt ausschließlich Bytefolge und Werkzeugdekodierung unter den genannten Einstellungen sowie den daraus abgeleiteten Kontrollfluss im begrenzten Slice.

## Status

Eingabehash-Prüfung: **PASS**. REA-Formataufnahme: **FAIL** (`unsupported binary format`, erwartete Capability-Lücke). Begrenzter Rizin-C166-Decode: **PASS**. Kontrollflussableitung: **VERIFIZIERT**, statisch und nur innerhalb `[E00C72, E00D10)`. Worker-Eigenprüfung des Validators und der kanonischen Bundle-Records: **PASS**; keine unabhängige Prüfung oder weitere Worker-Ausführung wird beansprucht. Keine Netzwerk-, Geräte-, VM- oder Hardwareaktionen.
