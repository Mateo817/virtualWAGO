> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-080 — FW31 `Dal_CallDeviceSpecificFunction`

## Ergebnis

Für das untersuchte Artefakt implementiert der Export einen Dispatcher mit einem bedingten Cache-Fallback und genau einem indirekten Callback-Aufruf. Der Outer-Body prüft nur, ob der Dispatch-Zeiger an ELF-VA `0x163ac` null ist. Bei null lädt er den Zeiger aus ELF-VA `0x1a2e4` und speichert ihn in `0x163ac`; sonst wird der bereits gespeicherte Zeiger verwendet. Danach ruft er den Zeiger indirekt auf.

Der Callback erhält sechs beobachtbare Argumente: `r0` und `r1` sind die ersten zwei Eingaben des Exportes; `r2` zeigt auf ein Stack-Paar mit Kopien der ursprünglichen `r2`/`r3`-Eingaben; `r3` enthält den aufgelösten Dispatch-Zeiger; die zwei Stackargumente sind eine Kopie der ursprünglichen ersten Eingabe und derselbe Stack-Paarzeiger. Die gleiche Adresse des Paars wird also als Callback-Argument 3 und 6 übergeben. Das ist eine Register-/Stack-Beobachtung, keine Struct- oder Feldlayout-Aussage.

Es gibt keinen beobachteten Statusvergleich auf den Rückgabewert des Callbacks und keine explizite Outer-Status-Zuweisung. Nach `blx r3` verändert der Export `r0` nicht mehr; sein Epilog stellt Stack und `lr` wieder her und springt zurück. Wenn der Callback normal zurückkehrt, bleibt sein `r0`-Wert daher im ARM-Rückgaberegister des Exportes erhalten. Ghidras Pseudocode typisiert den Export dennoch als `void`; die erhaltene Registerbelegung ist ein instruktionsgebundener Maschinenbefund und kein Beleg für einen deklarierten C-Rückgabetyp oder einen semantischen Statusvertrag.

Das Callback-Stackpaar ist ein lokaler, initialisierter Kopienbereich, den der Callback über zwei Aliasargumente erreichen kann. Der Export liest die beiden Wörter nach dem Callback nicht erneut und leitet sie nicht als Outer-Rückgabewert weiter. Ob der Callback sie als Ergebnis- oder In/Out-Speicher interpretiert, bleibt offen. Der Export validiert, übersetzt oder normalisiert weder den Callback-`r0`-Wert noch das Stackpaar.

## Beobachtung, Schlussfolgerung, Alternativerklärung, Restunsicherheit

| Aspekt | Beobachtung | Schlussfolgerung | Alternativerklärung / Restunsicherheit | Status |
|---|---|---|---|---|
| Guard und Fallback | `cmp r3,#0` bei Ghidra-VA `0x12ccc`, `bne 0x12ce8`; Nullpfad lädt aus ELF-VA `0x1a2e4`, speichert nach `0x163ac`. | `0x163ac` ist ein gecachter Dispatch-Zeiger; Null führt zum Pointer-Fallback. | Zieladresse des geladenen Zeigers ist zur Laufzeit nicht statisch belegt; Speicher in BSS kann Laufzeitinitialisierung erhalten. | VERIFIZIERT |
| Callback-Aufruf | `blx r3` bei Ghidra-VA `0x12d00`, mit den in `flow.tsv` aufgeführten Register- und Stackargumenten. | Ein indirekter Aufruf wird in beiden Guard-Zweigen erreicht. | Die aufgerufene Funktion und ihre interne Statussemantik sind nicht Teil dieses Befunds. | VERIFIZIERT |
| Inneres Stackpaar | Bei `0x12cec` wird `sp+0x10` als Zeiger gebildet; bei `0x12cf8` als zweites Stackargument abgelegt; ursprüngliche `r2`/`r3` lagen durch Prolog-Saves an dieser Adresse. | Derselbe Pointer adressiert zwei lokale Kopien und wird zweimal an den Callback gereicht. | Ob die aufgerufene Implementierung das Paar als Resultat, In/Out oder anders nutzt, ist unbekannt; kein Layout wird behauptet. | VERIFIZIERT |
| Outer-Rückgabe | Nach `blx r3`: `add sp`, `pop {lr}`, `add sp`, `bx lr`; kein Schreiben nach `r0`. | Bei normaler Callback-Rückkehr bleibt dessen `r0` im äußeren Rückgaberegister erhalten. | Ghidra dekompiliert den Export als `void`; Aufrufer und Quelltyp fehlen. Der erhaltene `r0` kann unbeabsichtigt/ABI-seitig undefiniert sein. | VERIFIZIERT |
| Statusbehandlung im beobachteten Body | Im Funktionskörper kein Test des Callback-`r0`, kein Fehlerpfad und kein Schreiben oder Normalisieren eines Statuswerts. | Im beobachteten Body gibt es kein Outer-Mapping oder Normalisieren des Callback-Status; nach normaler Rückkehr bleibt nur der `r0`-Registerwert erhalten. | Ob Aufrufer diesen Registerwert als Status behandeln oder ob dies dem API-Vertrag entspricht, ist nicht belegt. | VERIFIZIERT |
| Semantischer API-Statusvertrag | Kein aufgelöster direkter Caller und keine Typ-/Headerquelle im Scope; Ghidra-Pseudocode typisiert den Export als `void`. | Aus dem Funktionskörper allein folgt kein semantischer API-Statusvertrag. | Caller-seitige oder externe Deklarationen könnten einen Statusvertrag festlegen. | OFFEN |

## Koordinaten und Methode

Eingang: `FW31-IODRVDAL-1.0.2`, ELF32 ARM little-endian, 25 976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. Dynsym meldet Symbol-VA `0x2cb8`, Größe 104 (`0x2cb8..0x2d1f`). REA/Ghidra 12.1.4 meldet Funktions-VA `0x12cb8..0x12d13`, 92 Bytes; bei diesem ELF-Load-Image ist das Ghidra-VA = ELF-VA + `0x10000` und File-Offset = ELF-VA im ersten LOAD-Segment. Der abgefragte Funktionskörper stimmt mit dem instruktionsbelegten Code `0x2cb8..0x2d13` überein; die Dynsym-Größe umfasst zusätzlich die nachfolgenden Literalwörter bis `0x2d1f`.

REA-first: `open_binary`; danach Funktion-Pseudocode, Assembly, vollständige Instruktionslesung und direkte Caller-Abfrage. Pseudocode wird nur als Navigationshilfe verwendet. Die anfängliche Anfrage an Adresse `0x2cb8` als Ghidra-VA verfehlte die Funktion, weil Ghidra die Basis `0x10000` meldete; die korrekte beobachtete Analyseadresse `0x12cb8` wurde verwendet. Es wurde nicht dieselbe fehlgeschlagene Anfrage wiederholt. Als eng begrenzter Fallback wurde ARM-`objdump` ausschließlich über ELF-VA `0x2cb8..0x2d1f` gelesen, um Literaladressen und Rückkehr-Epilog unabhängig zu kontrollieren; `readelf` wurde zur Prüfung von ELF-Segmenten, Symbolgröße und Relokationen verwendet.

REA-Evidence-IDs: `ev_6e9cef3f939eba3422c6676ea35de630729215b5357457bde47fd023f6effec4` (Pseudocode), `ev_6f9218b6d9dc1cfe717d0338eda275738cd845946a08a2412d2e721690752ad2` (Assembly), `ev_c99b02400642766046adf9f0508eeeccb2770cb18f45f3e138862766269138ca` (Instruktionen/Body), `ev_373fdae8ea355d1f39a9612e3d3da39e48a3171331f57ee61e2f6ceac080d533` (Caller-Abfrage). Alle vier Records sind im kanonischen `evidence.bundle.json` enthalten.

## Toolprofil und Grenzen

REA-Provider: Ghidra 12.1.4; Architektur ARM; Analyseprofil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; Ephemeral-Import, Quellartefakt unverändert. Fokussierter Fallback: GNU `readelf` (GNU Binutils for Debian 2.44) und `arm-linux-gnueabihf-objdump` (GNU Binutils for Debian 2.44). Keine Ausführung des Binaries, kein Runtime-/Geräte-/Netzwerkzugriff.

Die direkte Caller-Abfrage ergab keine aufgelösten direkten Aufrufer (`relationship_coverage=complete` für aufgelöste Ghidra-Call-Referenzen). Ghidra weist ausdrücklich darauf hin, dass nicht aufgelöste berechnete/indirekte Calls unbekannt bleiben. Deshalb enthält `callers.tsv` keine Caller-Instruktionsfenster und klassifiziert keine Caller-seitige Verwendung. Die Call-Argumentform ist aus dem Dispatcher selbst beobachtet. Der Register-Rückgabebefund belegt die erhaltene `r0`-Belegung, nicht die Absicht oder Deklaration eines API-Statuswerts.

## Tests

Lokaler Validator prüft Eingangs-Hash, erforderliche Dateien, zulässige Statuszellen und das Vorhandensein der referenzierten Evidence-IDs im Bundle. Ergebnis: PASS. Keine Implementierungstests oder Laufzeitversuche durchgeführt (NOT_RUN; nicht Teil dieses statischen Befunds).
