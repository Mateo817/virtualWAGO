> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-146 — FW31 `IoDrvDal`-Zielkörper `0x1704..0x176B`

## Frage, Befund und Status

Welche Registerargumente, indirekten Calls, Ergebnistests und Rückgabepfade verwendet der bei `ComponentEntry` an Eingabeoffset `+0x04` publizierte Zielkörper? Beeinflusst ein am Eintritt anliegendes `r0=0` den Ablauf?

**VERIFIZIERT — statische Instruktionssemantik:** Der von `ComponentEntry` an Eingabeoffset `+0x04` publizierte Wert `0x00011704` erreicht in diesem ELF den vollständigen ARM-Body Ghidra `0x11704..0x1176B` (inklusive), entsprechend ELF-VA und Dateioffset `0x1704..0x176B`. Der Body liest nicht den bei Eintritt anliegenden Wert in `r0`. Er testet stattdessen einen global gespeicherten indirekten Zielwert. Ist dieser Null, gibt der Body `3` zurück. Sonst ruft er ihn zunächst mit den Registern `r0=0x25E28`, `r1=0`, `r2=1`, `r3=0x10062001` auf. Ein von diesem ersten Call zurückgelieferter Nichtnullwert wird unverändert zurückgegeben. Nur bei Null erfolgt der zweite indirekte Call mit `r0=0x25E4C`, `r1=0`, `r2=0`, `r3=0x10062001`; dessen `r0`-Ergebnis wird unverändert zurückgegeben.

**VERIFIZIERT:** Damit beeinflusst das vom aufrufenden `codesys3`-Kontext vorgegebene Eintrittsregister `r0=0` diese Mechanik im Zielkörper nicht: kein Eintrittsregister wird ausgewertet, und `r0` wird vor dem ersten indirekten Call mit dem berechneten ersten Argument überschrieben. Die Herkunftsangabe `r0=0` ist hier ausschließlich als vorgegebener Caller-Kontext übernommen und wurde nicht neu analysiert.

## Artefakt, Adressen und Methode

- Eingabe: `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvDal.so.1.0.2`, 25.976 Byte, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`.
- REA/Ghidra: `analyze_function(0x11704)`, Evidence-ID `ev_f3e40c0469848d42f28508fbdd3ff141b89e5a209a55daccb5ff5978870c7908`; Ghidra 12.1.4, ARM:LE:32:v8, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- REA meldet einen einzelnen zusammenhängenden inklusiven Funktionsbereich von 104 Byte, genau Ghidra `0x11704..0x1176B`; 26 Instruktionen; vollständigen CFG-/Assembly-/Pseudocode-Dossier; Value-Flow `truncated=false`, `omitted_operations_lower_bound=0`. Zwei indirekte Calls bleiben ohne aufgelöste Ziele.
- Adressabbildung für diesen Bereich: Ghidra-Adresse = ELF-VA + `0x10000`; im hier ausführbaren `.text`-Bereich sind ELF-VA und Dateioffset gleich. Diese drei Spalten stehen für jede Instruktion in `instructions.tsv`.
- `ComponentEntry`-Positionskontext stammt ausschließlich aus WP-XE164-144: dort wird `0x11704` als erster der vier 32-Bit-Werte ab Eingabeoffset `+0x04` publiziert. Die Größe im übergebenen WP144-Prompt war falsch; eigenständig gemessen sind dessen Report 7.521 Byte mit dem unveränderten SHA-256 `ed6dfcec73f4bb1e74b711a0304fa150809c19514422a5391da7a96a9d5060ab`. WP-XE164-077 wurde ebenfalls erneut gemessen: 6.798 Byte, SHA-256 `578a98557944915b188b7a6ab9d8177e2324ff1b99a630ff3bf6c31645878e42`. Diese Korrektur der Prompt-Metadaten ändert keinen Reportinhalt.
- REA-first Methode: `open_binary` auf das angegebene ELF, dann `analyze_function(0x11704)`. Kein Disassembler-/readelf-Fallback wurde benötigt. Keine Datei ausgeführt; keine VM, kein Netzwerk, kein Gerät und keine Hardware verwendet.
- Ein einmaliger REA-Bundle-Export scheiterte zunächst, weil das angeforderte Ausgabeverzeichnis noch nicht existierte. Nach einmaligem Anlegen des Zielverzeichnisses wurde derselbe Export erfolgreich ausgeführt (1 Record, 0 Unknowns); der Fehler führte zu keiner Zielanalyse außerhalb des Scopes. `jq` und der Alias `python` waren lokal nicht vorhanden; Bundle-Prüfung und Validator verwenden `python3`.

## Argument- und Zielmechanik

Die folgende Zuordnung beobachtet Registerwerte beim indirekten Übergang. Sie ist keine Rekonstruktion einer Quellsprachensignatur. Das globale Ziel liegt an Ghidra-Adresse `0x2618C` (ELF-VA `0x1618C`, BSS ohne Dateioffset). Der Body prüft und lädt den dort gespeicherten Wert; REA löst die zwei `blx`-Zieladressen nicht auf. Der Zielkörper dieses Werts und die Semantik der übergebenen Adressen werden nicht untersucht.

| Callsite | Indirektes Ziel | `r0` | `r1` | `r2` | `r3` | Weiterer lokaler Ablauf |
|---|---|---|---|---|---|---|
| Ghidra `0x11734` / ELF-Datei `0x1734` | Wert aus globaler Zelle `0x2618C` | `0x25E28` (ELF-VA `0x15E28`, Datei `0x5E28`) | `0` | `1` | `0x10062001` | Ergebnis aus `r0` wird bei `0x11738` nach `r2` kopiert und auf Null getestet. |
| Ghidra `0x1175C` / ELF-Datei `0x175C` | derselbe Wert, an `0x11750` erneut aus `0x2618C` geladen | `0x25E4C` (ELF-VA `0x15E4C`, Datei `0x5E4C`) | `0` (Kopie des zuvor getesteten Null-Ergebnisses) | `0` (getestetes erstes Ergebnis) | `0x10062001` | Das `r0`-Ergebnis dieses Calls wird direkt über das gemeinsame Register-restoring-Epilog zurückgegeben. |

Argumentregister werden explizit durch Instruktionen gesetzt. Die erste Callvorbereitung lädt `r0`, setzt `r2=1`, lädt das Ziel, setzt `r1=0`, lädt `r3=0x10062001` und berechnet den ersten PC-relativen Argumentwert. Nach dem Call überschreibt `subs r2,r0,#0` das Argumentregister `r2` mit dem Rückgabewert. Im Nullzweig wird `r1` aus diesem nun bekannten Nullwert gebildet; `r2` bleibt ebenfalls Null. Für den zweiten Call wird das Ziel aus derselben Zelle neu geladen.

## Tests, Kontrolle und Rückgabepfade

| Bedingung/Pfad | Instruktionsfolge | Beobachteter Rückgabewert in `r0` |
|---|---|---|
| Globaler Zielwert ist Null | `0x11710..0x11718`: load, `cmp`, `beq 0x11764`; `0x11764: mov r0,#3`; `0x11768` stellt Register wieder her und kehrt zurück | exakt `3`; kein indirekter Call |
| Globaler Zielwert ist nicht Null; erster Call liefert `R1 != 0` | `blx` `0x11734`; `subs r2,r0,#0`; `beq` bei `0x1173C` wird nicht genommen; `cpy r0,r2`; Epilog bei `0x11744` | exakt `R1`; zweiter Call wird übersprungen |
| Globaler Zielwert ist nicht Null; erster Call liefert `R1 = 0` | Nullzweig `0x1173C -> 0x11748`; zweiter `blx` bei `0x1175C`; Epilog bei `0x11760` | exakt Rückgabewert des zweiten Calls; kein weiterer Ergebnistest |

Das erste Ergebnis ist das einzige Call-Ergebnis, das lokal getestet wird. Für den zweiten Rückgabewert gibt es keinen nachfolgenden Vergleich. Alle drei Rückgabepfade stellen `r4`, `r5`, `r6` wieder her und kehren über den zuvor gesicherten `lr`-Wert zurück.

### Vollständige Instruktions-/Kontrollflusstabelle

`instructions.tsv` führt sämtliche 26 Instruktionen dieses vollständigen Ghidra-Bodys mit Ghidra-Adresse, ELF-VA, Dateioffset und semantischer Wirkung auf. Die bedingten Kanten sind `0x11718 -> 0x11764` für Nullziel und `0x1173C -> 0x11748` für Nullergebnis des ersten Calls; sonst fällt die Ausführung jeweils auf den folgenden Pfad durch. Die beiden indirekten Calls sind `0x11734` und `0x1175C`. Direkte Rückkehren liegen bei `0x11744`, `0x11760` und `0x11768`.

## Countercheck E-XE164-087

**VERIFIZIERT — Übereinstimmung:** WP-XE164-077, auf dessen Befund E-XE164-087 beruht, beschreibt denselben Bereich `0x1704..0x176B`: Rückgabe `3` bei Null im gespeicherten Ziel; erster indirekter Call mit `(&0x25E28, 0, 1, 0x10062001)`; erster Nichtnullstatus wird zurückgegeben; zweiter Call nur nach erstem Null mit `(&0x25E4C, 0, 0, 0x10062001)`; dessen Ergebnis wird zurückgereicht. Der frische REA/Ghidra-Dossier und vollständige Instruktionsfolge stimmen mit jeder dieser Aussagen überein. Es wurde kein Konflikt gefunden.

WP-XE164-077 und E-XE164-087 begrenzen die Rollenzuordnung der zwei Adressen und des globalen Werts und geben ihnen keine Quellnamen oder Callverträge. Der vorliegende Bericht folgt derselben Grenze. Der zusätzliche Punkt hier ist die explizite Gegenprüfung, dass Eintritts-`r0` nicht verwendet wird und durch die Argumentvorbereitung überschrieben ist.

## Alternative Erklärung und Restunsicherheit

**HYPOTHESE:** Die beobachtete Folge kann als Registrierung zweier aneinander gereihter Bereiche verstanden werden, bei der ein erster Nichtnullstatus den zweiten Aufruf unterdrückt. Die Zahlen `0`, `1`, `3`, `0x10062001` und die beiden Tabellenadressen identifizieren aus dieser Instruktionsfolge allein weder einen API-Vertrag noch eine Statusbedeutung oder Quellfeldnamen.

**OFFEN:** Der tatsächliche Inhalt oder Vertrag der globalen indirekten Zieladresse, die Semantik beider an `r0` übergebenen Adressen, ob und wann der Host den Callback ausführt, Laufzeitabbildung/Relokation und reales Laufzeitverhalten. Der Befund beweist nur statische Register- und Kontrollflussmechanik im identifizierten ELF; er beweist keine dynamische Ausführung.

**Grenze des `r0=0`-Befunds:** Belegt ist, dass dieser Maschinenkörper keinen bei Eintritt gelieferten `r0`-Wert liest und `r0` vor seinem ersten indirekten Call selbst auf die erste Argumentadresse setzt. Nicht belegt ist, dass außerhalb dieses Körpers oder in der indirekten Callfunktion der ursprüngliche Wert beobachtbar wäre.

## Validierung und erzeugte Dateien

Der reproduzierbare Validator `validate.py` bindet die SHA-256-Hashes des ELF und der Reports WP144, WP077, WP087, prüft den REA-Record samt Evidence-ID, Provider, Bodyrange, vollständiger Instruktionsliste, Value-Flow-Vollständigkeit und beiden indirekten Callkanten sowie die Adressfolge der Instruktionstabelle. Ausgabe: `validation.txt`.

- Statischer Validator: **PASS** (siehe `validation.txt`).
- Laufzeittest und Callee-Verhalten: **NOT_RUN**.
- Hardwaretest: **NOT_RUN**.
- Unabhängiges Review: **NOT_RUN**; diese Prüfung ist eine eigenständige Offline-Gegenprüfung und keine unabhängige Reviewbehauptung.

Alle generierten Dateihashes außer dem Manifest selbst sind in `SHA256SUMS` festgehalten; der Validator prüft außerdem die extern gebundenen Eingabehashes.
