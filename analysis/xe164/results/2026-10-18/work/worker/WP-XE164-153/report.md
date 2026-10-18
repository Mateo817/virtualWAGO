> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-153 — `Components.Directory` in FW31 `codesys3`

## Ergebnis

**VERIFIZIERT:** Das hashgebundene ELF enthält genau eine exakte ASCII-Fundstelle von `Components.Directory\0`. Ihr Dateioffset ist `0x39fe34`, nicht der in der Vorbeobachtung genannte `0x39fe30`: bei `0x39fe30..0x39fe33` liegen vier Nullbytes. Der erste `PT_LOAD` bildet `p_offset=0` auf `p_vaddr=0x10000` ab; daher liegt die Key-Adresse bei ELF-VA `0x3afe34`.

**VERIFIZIERT im begrenzten Disassembler-Fallback:** Im ARM-Code werden zwei direkte Adresskonstanten aufgebaut: `0x3afe4c` (benachbarter Pfadstring) durch `movw/movt` bei `0x33f5a8/0x33f5b0`, und `0x3afe34` (Key) durch `movw/movt` bei `0x33f5b8/0x33f5bc`. Der Pfadzeiger wird bei `0x33f5b4` auf `[sp]` geschrieben. Der Key bleibt bei der folgenden Call-Site `0x33f5d4` in `r1`. Diese Instruktionen belegen eine unmittelbare adressgebundene Korrelation beider Strings im selben Codeabschnitt; die Pfadbeobachtung ist keine unabhängige Path-Xref-Gegenprüfung.

Beim ersten nachfolgenden direkten Call steht `bl 0x33ce44 <SettgGetStringValue@@Base>`. Sichtbarer Zustand unmittelbar davor: `r0=0x00345440`, `r1=0x003afe34`, `r2=fp-1324`, `r3=fp-1356`, `[sp]=0x003afe4c`, `[sp+4]=r8` (Wert unbekannt). Dies ist nur Maschinenzustand. Weder Argumentrollen noch API-/Parsersemantik oder Runtimeverhalten werden daraus abgeleitet.

**BLOCKED:** Ein Ghidra-FunctionManager-Xref und die vollständige providerbestätigte Funktion wurden nicht gewonnen. Die vorhandene exakte Hash-Evidence aus WP-XE164-118 behandelt eine andere Funktion (`0x330610`), nicht den Key. Die aktuelle REA-Sitzung war geschlossen. Ein neuer REA-Import hätte die bereits für WP152 beobachtete hängende Autoanalysevoraussetzung wiederholt; daher wurde er nicht erneut gestartet. Der einzelne Rizin-`aaa`-Versuch lieferte binnen 30 Sekunden keine Daten und wurde unterbrochen. Der begrenzte Rizin-Lauf wird nicht als vollständige Xref-Auswertung gewertet.

**OFFEN:** Ob über die ausgewerteten Fallback-Muster hinaus weitere direkte Xrefs oder nicht modellierte Adressdatenflüsse existieren, ist nicht geklärt. Die vorhandenen Such- und Disassemblerbefunde sind auf die in `fallback_scope.txt` beschriebenen Muster begrenzt.

Im vollständigen `objdump -d`-Text dieser ELF wurden keine rohen little-endian 32-Bit-Wörter mit den Zieladressen gefunden. Der unten dokumentierte Instruktionsscanner fand je einen passenden `movw/movt`-Aufbau für Key und benachbarten Pfad sowie keine weiteren passenden `movw/movt`- oder PC-relativen `ADD/SUB/ADR`-Muster. Das Ergebnis ist an diese Muster und die objdump-Decodierung gebunden; beliebige Registerdatenflüsse, Tabellenindizierung und indirekte Referenzen bleiben außerhalb der Abdeckung. Es ist deshalb kein provider-unabhängiger Beweis, dass es im ELF keine weiteren direkten Xrefs gibt.

## Fundstellen- und Xref-Tabellen

`key_occurrences.tsv` ist die vollständige exakte ASCII-/NUL-Suche über alle 5.181.396 Eingabebytes. Sie enthält genau eine Fundstelle. `direct_address_candidates.tsv` enthält alle Musterkandidaten des begrenzten Fallbacks: einen Key-Kandidaten und eine separate Pfad-Adresskorrelation. Der Pfadstring selbst wurde nicht eigenständig gesucht.

| ID | Source-VA | Materialisierung | Ziel-VA | Einordnung |
|---|---:|---|---:|---|
| XREF-K1 | `0x33f5b8` + `0x33f5bc` | `movw r1,#0xfe34`; `movt r1,#0x3a` | `0x3afe34` | Key-Adresskandidat; direkter Aufruf folgt bei `0x33f5d4` |
| KORRELATION-P1 | `0x33f5a8` + `0x33f5b0` | `movw r1,#0xfe4c`; `movt r1,#0x3a` | `0x3afe4c` | nur benachbarte Pfadadresse im selben Setup; keine unabhängige Xref-Gegenprüfung |

`instruction_table.tsv` enthält jeden ARM-Befehl vom unmittelbar vorbereiteten lokalen Zeigerzustand bis einschließlich des ersten Call-Befehls nach Key-Materialisierung. `function_candidate_disassembly.txt` erhält einen exakt 256 Byte umfassenden objdump-Ausschnitt `0x33f548..0x33f647` am Xref, inklusive eines erkennbaren Prologs bei `0x33f550`. Das ist kein Ghidra-Bodynachweis; weder Funktionsanfang noch Funktionsende oder Funktionsname werden als verifiziert behauptet.

## String- und ELF-Mappingbeleg

| Objekt | Dateioffset | ELF-VA | Nachweis |
|---|---:|---:|---|
| `Components.Directory\0` | `0x39fe34` | `0x3afe34` | Bytes im ersten `PT_LOAD`, `p_offset=0`, `p_vaddr=0x10000`; Mapping `VA = offset + 0x10000` |
| `/usr/lib/cds3-custom-components\0` | `0x39fe4c` | `0x3afe4c` | am vorgegebenen Nachbaroffset bytegenau geprüft; derselbe `PT_LOAD` |

`readelf_program_headers.txt` und `readelf_sections.txt` enthalten Rohbelege der ELF-Tabellen. Beide exakten Bytefolgen werden am bekannten Offset verifiziert; für den Key wird zusätzlich die vollständige Datei nach der NUL-terminierten Bytefolge durchsucht. Die ASCII-Pfadfolge wurde nicht global gesucht.

## REA-Evidence und Toolgrenzen

Das beibehaltene `rea-existing-WP-XE164-118.json` bindet dieselbe SHA-256 an Ghidra 12.1.4 und Analysis-Profile `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Seine Rohrecords enthalten keine Referenz zum Key. `rea_evidence_ids.tsv` listet die hier relevanten Record-IDs; beispielsweise bindet `ev_1d4fa6c829e6e2d43e8f869e8f32d28bd83cd651c010d697796b564bc6ac65d2` die fremde Codeadresse `0x330664` an `FUN_00330610`.

Aktueller `binary_session`-Befund: `open=false`; Ghidra 12.1.4 ist auf diesem Linux/x64-Host verfügbar, aber weder target noch Providerbindung sind aktiv. Kein `open_binary` erfolgte. `fallback_scope.txt` hält den einzigen abgebrochenen Rizin-Autoanalyselauf, die verwendeten Adressdomänen und die Fallback-Abdeckung fest. Werkzeugstände: REA `6.5.0`; Ghidra `12.1.4`; Rizin `0.9.1`; GNU binutils/readelf/objdump `2.44`; Python `3.13.5`.

## Alternative Erklärung und Restunsicherheit

Die sichtbare Instruktionsfolge passt dazu, dass der Key-Zeiger zusammen mit einem benachbarten Pfadzeiger vor dem Aufruf von `SettgGetStringValue` bereitgestellt wird. Sie beweist nicht, dass diese Funktion den Key interpretiert oder den Stackwert als Pfad benutzt; ebenso bleibt offen, ob beide Zeiger in einer gemeinsamen Parameterstruktur oder für unterschiedliche Zwecke übergeben werden. Der Exportname allein begründet keinen vollständigen Vertrag.

Nicht verifiziert sind die Ghidra-Referenzart, vollständige FunctionManager-Bodygrenzen, mögliche weitere Referenzen über nicht modellierte Instruktions-/Datenflussformen, der Inhalt von `r8`, die Übergabesemantik der Stackslots sowie Laufzeitnutzung oder Konfigurationsüberschreibung.

## Eingabe, Tests und Status

| Feld | Wert | Status |
|---|---|---|
| Eingabe | `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-112/hit_files/usr/bin/codesys3`; 5.181.396 Bytes; SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | VERIFIZIERT |
| Ghidra-Xref/Funktionskörper | gleicher Hash im WP118-Bundle, aber kein Key-Xref; keine erneute Importanalyse wegen bekannter Hängerbeobachtung | BLOCKED |
| Direkte Adressmuster | eine MOVW/MOVT-Keymaterialisierung und eine benachbarte Pfadmaterialisierung; null rohe Full-Word-Treffer. Gilt für die in `fallback_scope.txt` beschriebenen Fallback-Muster. | VERIFIZIERT |
| `python3 validate.py` | erwartete Hashes, NUL-Fundstellen, ELF-VA-Mappings, Tabellenkandidaten und Instruktionsfenster geprüft | PASS |
| `sha256sum -c SHA256SUMS` | alle Paketdateien geprüft | PASS |
| Review | Self-Review; keine unabhängige Prüfung und kein Worker-/Runtime-/Hardwarelauf behauptet | VERIFIZIERT |

## Paketdateien

Alle erzeugten Dateien liegen ausschließlich in diesem Ausgabeverzeichnis. `SHA256SUMS` enthält Größe und Digest nicht; Größe ist oben beziehungsweise im Validator festgehalten. Vollständige SHA-256 aller Paketdateien stehen im Manifest.

| Datei | Zweck |
|---|---|
| `report.md` | Befund, Adressdomänen, Grenzen und Status |
| `key_occurrences.tsv` | vollständige NUL-terminierte Key-Fundstellen |
| `direct_address_candidates.tsv` | Key-Xref-Kandidat plus ausdrücklich überlappende Pfadkorrelation |
| `instruction_table.tsv` | vollständige begrenzte Setup-/Argumentinstruktionen bis zum ersten Call |
| `function_candidate_disassembly.txt` | begrenzter lineare Disassemblierungsfallback; Funktionsgrenzen nicht providerbestätigt |
| `readelf_program_headers.txt`, `readelf_sections.txt` | ELF-Mapping-Rohbelege |
| `fallback_scope.txt` | Rizin-/objdump-/Adressmustergrenzen und Versionen |
| `rea-existing-WP-XE164-118.json`, `rea_evidence_ids.tsv` | hashgebundene bestehende REA-Rohrecords und IDs, als Key-Xref-negativ begrenzt |
| `scan.py`, `validate.py` | reproduzierbarer Offline-Scanner und Validator |
| `SHA256SUMS` | Hashmanifest für Paketdateien außer dem Manifest selbst |
