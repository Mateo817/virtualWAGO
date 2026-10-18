> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-211 — minimaler bedingter Zweifunktionsvertrag

## Ergebnis

**HYPOTHESE:** Für die statisch installierte, aber zur Laufzeit nicht
beobachtete IoDrvDal→libdal-Bindung ergibt sich ein kleinster
positionsgebundener Vertrag zwischen Objektpositionen `+0x0c` und `+0x10`.
`+0x0c` erhält sichtbar `10`, einen aktuellen `r5`-Wert und einen aktuellen
`r8`-Wert. Sein statisches Ziel schreibt ein 32-Bit-Rückgabewort durch den
dritten Eingang und kann über den zweiten Eingang höchstens zehn geordnete
8-Byte-Paare schreiben. Der Consumer läuft lokal in 8-Byte-Schritten, verwendet
das zweite Wort eines Eintrags als Vergleichseingang und bei Vergleichserfolg
das erste Wort als Eingang für `+0x10`.

Diese Aussage ist kein Originalquelltext, kein API-/Structvertrag und keine
Runtimebeobachtung. Die vollständige zeilenweise Minimalmatrix steht in
`contract.csv`.

## Beobachtung

- E-XE164-230 bindet unter der Zielbedingung die `+0x0c`-Argumente, einen
  separaten 32-Bit-Write sowie höchstens zehn Paar-Writes an Positionen
  `8*i+0` und `8*i+4`.
- E-XE164-231 bindet für `+0x10` nur incoming `r0`; sein statisches Ziel reicht
  den ursprünglichen Wert an einen opaken Call weiter, dessen eigener nonnull
  Rückgabewert den Sekundärkörper erreicht.
- E-XE164-234 pinnt den lokalen 8-Byte-Scan, Vergleich über Eintrag `+4` und
  Verwendung von Eintrag `+0` auf dem Matchpfad.
- E-XE164-235 stärkt nur den callfreien ersten Scanabschnitt durch sichtbare
  Push-/Pop-Pfade; opake Stackeffekte bleiben offen.
- E-XE164-236 zeigt für einen konditional bereits aufgelösten exakten
  Getterpfad keine sichtbare `r7`-Änderung oder Storewirkung. Aliasüberlappung
  und Lazy Resolution bleiben offen.
- E-XE164-232/233 machen exact libdal zum einzigen installierten
  Partition-2-Definitionskandidaten und direkten SONAME-Kandidaten, aber nicht
  zum beobachteten Runtimegewinner.

## Schlussfolgerung und Veröffentlichungsgrenze

Für einen virtuellen Provider ist damit als **Implementierungshypothese**
prüfbar: Eine erste Position liefert eine beschränkte Folge positionsgleicher
Zweiwort-Einträge; der originale Consumer wählt anhand des zweiten Worts und
reicht das erste Wort an die zweite Position weiter. Die Wortbedeutungen,
Pointee-Typen, Seiteneffekte der opaken Calls, vollständigen Returns und
Lebenszyklusbedingungen sind nicht belegt und dürfen nicht benannt werden.

Die alternative Erklärung bleibt, dass zur Laufzeit ein anderes Objekt, eine
andere Definition, ein Lazy Resolver oder veränderte Register-/Speicherwerte
den beobachteten statischen Pfad ersetzt. Auch ein Alias zwischen
`[r4+0x618]` und dem aktuellen Eintragswort ist statisch nicht ausgeschlossen.

Status: Matrix und Gesamtschlussfolgerung **HYPOTHESE**; lokale Pins in den
zitierten Evidenzen teils **VERIFIZIERT**; Runtimebindung, ABI, Semantik und
Hardware **OFFEN**; Runtime-/Hardwaretests **NOT_RUN**.

Provenienz: GPT-6.1 SOL Root-Synthese, Self-Review. Kein unabhängiger Review
und kein Worker-, Runtime- oder Hardwarenachweis.
