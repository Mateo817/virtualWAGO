> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-193 — bedingte Instanzbasis-/Publikationskette

## Ergebnis

**HYPOTHESE:** Ein konkreter statischer CFG-Pfad verbindet die bei `0x30c0` berechnete Basis `r4=r0+0x63c*fp` mit drei belegten Positionswerten und dem späteren dynamischen Init-Aufruf: `r4+0x620=0x1a234`, auf der Provider-/Trefferlane `r4+0x618=[r7]`, anschließend `r4+0x61c=0x1a270`, und nach erfolgreicher Symbolauflösung `r0=r4` vor `blx r3` bei `0x3010`.

Die Positions- und CFG-Mechanik ist jeweils **VERIFIZIERT**. Die End-to-End-Gleichheit bleibt **HYPOTHESE**, weil zwischen `0x30c0`, dem Rücksprung `0x32ec -> 0x2f08` und den Stores mehrere opake direkte/indirekte Calls liegen. Im sichtbaren Code gibt es auf diesem Pfad keine weitere `r4`-Definition; die Synthese setzt jedoch voraus, dass diese Aufrufe die vom Binary erwartete Registererhaltung einhalten. Das ist keine Runtime-Beobachtung.

Der Pfad ist:

1. `0x30b8` setzt `r3=0x63c`; `0x30c0` bildet `r4=r0+r3*fp`.
2. Die korrigierte E-XE164-218-Arithmetik schreibt bei `0x30e8` exakt `0x1a234` an `r4+0x620`.
3. Nach der späten Initialisierungsfolge ruft `0x32e4` indirekt auf. Nur wenn `0x32e8` einen Nullwert feststellt, verzweigt `0x32ec` direkt nach `0x2f08`.
4. Die E-XE164-217-Lane ruft den importierten Namen `adi_GetApplicationInterface` auf, lädt aus Rückgabe `+0x0c` und ruft dieses Wort. Nur dessen Nullergebnis setzt den Pfad fort.
5. Auf einem Vergleichstreffer wird `[r7]` an `r4+0x618` gespeichert; ein zweiter gleichnamiger Importaufruf liefert die Basis für den indirekten `+0x10`-Call. Nur ein Nullergebnis nach dem Loop erreicht den nächsten Store.
6. Exakte Literal-/PC-Arithmetik schreibt `0x1a270` an `r4+0x61c`. E-XE164-216 bindet diese Zahl in demselben ELF nur als unbenannte NOBITS-`.bss`-Position.
7. Nach erfolgreichem `LibraryLoader_LoadSymbol` setzt `0x3008` `r0=r4`; `0x3010` ruft das aus `[sp+0x70]` geladene Wort indirekt. E-XE164-126 bindet diesen generischen Pfad unabhängig als dieselbe berechnete Basis, die an den aufgelösten Init-Einstieg geht; E-XE164-122 zeigt, dass der konkrete IoDrvKbus-Init-Pfad Eingabe `+0x620` liest.

Damit ist statisch unterstützt, dass die ursprüngliche Loaderinstanz die Provider-/Loaderreaktionen und die später vom Originaltreiber verwendeten relativen Positionen zusammenführt. Das ist für den virtuellen Provider-Cut relevant: Es spricht dafür, den originalen Manager-/Treiberpfad zu behalten und nur die beobachteten Providerreaktionen bereitzustellen. Es beweist weder eine komplette ABI noch, dass `0x1a270` schon korrekt befüllt ist.

## Grenzen und Alternative

- Export- und Importnamen sind keine Funktionsverträge. Die Bedeutungen von `+0x0c/+0x10/+0x618/+0x61c/+0x620` bleiben unbenannt.
- Eine alternative Erklärung ist, dass ein opaker oder nichtkonformer Aufruf `r4` verändert oder relevante Speicherbereiche aliasiert. Dann wäre die lokale Positionskette nicht end-to-end derselbe Laufzeitwert.
- Der dynamisch aufgelöste Zielwert an `0x3010` ist in diesem Paket nicht erneut identifiziert. Die IoDrvKbus-Bindung bleibt an die Bedingungen der akzeptierten E-XE164-122/126 gebunden.
- Der spätere IoDrvKbus-Callback-Kontext und `r4` werden hier nicht als identische Runtimeobjekte behauptet. Runtime, VM, Netzwerk, Gerät und Hardware sind **NOT_RUN**.

## Methode und Prüfung

Offline Root-Synthese aus E-XE164-122/126/217/218 plus erneuter Prüfung der exakt aufgeführten ARM-Wörter. Keine neue REA-/Ghidra-Operation; die bestehenden REA-first-Lücken bleiben erhalten. GNU ARM Objdump 2.44 und Python 3.13.5. `validate.py` prüft Eingabehash, 22 relevante Wörter/Branchziele, `0x1a234`-Arithmetik, Evidence-IDs und alle acht Tabellenzeilen. Validator: **PASS**. Review: Root Self-Review; kein unabhängiger Review behauptet.
