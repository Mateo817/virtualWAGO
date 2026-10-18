> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-128 — Herkunft des lokalen `ComponentEntry`-Arguments `+0x34`

## Ergebnis

**VERIFIZIERT (exakter `codesys3`-Pfad):** `FUN_002fc530` setzt bei
`0x2fc55c` das erste Argument des späteren indirekten Entry-Aufrufs auf
`r0 = fp - 0x5c`. Die Instruktionen `0x2fc58c..0x2fc590` bilden mit
`movw r3,#57644` und `movt r3,#47` den 32-Bit-Wert `0x002fe12c`. Der Store
`0x2fc594: str r3,[fp,#-40]` schreibt ihn an `fp-0x28`. Relativ zur lokalen
Argumentbasis gilt exakt:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Damit enthält das lokal aufgebaute Argument beim indirekten Aufruf an Position
`+0x34` den Wert `0x002fe12c`. Zwischen diesem Store und `blx r2` bei
`0x2fc5c8` gibt es im vollständigen adressierten Ausschnitt keinen weiteren
Store an diese Position und keine Änderung von `r0`. WP-XE164-125 bindet `r2`
im exakten generischen Loaderkontext an den zuvor unter dem Namen
`ComponentEntry` aufgelösten Zeiger. Der Zahlenwert `0x002fe12c` ist damit als
statischer Objektinhalt belegt; seine Funktionssemantik ist hier ausdrücklich
**OFFEN**.

**HYPOTHESE (Cross-DSO-Verbindung):** Der untersuchte Loader ist generisch.
Die vorliegenden statischen Daten binden seinen konkreten Laufzeit-Aufruf nicht
an die exakte IoDrvDal-Datei. Falls `r2` bei diesem Aufruf auf deren
`ComponentEntry` zeigt, liest der bereits akzeptierte Dal-Pfad dieselbe
Argumentposition `+0x34` vor seinem optionalen indirekten Call und speichert
damit `0x002fe12c` in Dal-BSS `0x26090`. Das ist eine bedingte Komposition der
beiden verifizierten Binärpfade, kein Beleg einer tatsächlich erfolgten
dynamischen Auflösung oder Ausführung.

**VERIFIZIERT (Dal-interne Positionsfolge):** Unabhängig vom konkreten
Eingangswert liest IoDrvDal `ComponentEntry` seine Eingabeposition `+0x34`
zweimal: vor dem optionalen Call `0x1452c` nach `0x26090`, danach erneut nach
`0x2a268`. Die zweite Position wird über die akzeptierte Dal/Kbus-Kette als
Basis `0x2a234 + 0x34` weitergereicht und in IoDrvKbus für den indirekten Call
`0x14cec` verwendet.

**HYPOTHESE (Wertgleichheit bis Kbus):** Nur falls (1) der generische Loader
die exakte Dal-`ComponentEntry` aufruft und (2) der dazwischenliegende Dal-Call
den Argumentspeicher an `+0x34` nicht verändert, erreicht `0x002fe12c` auch
Dal-BSS `0x2a268`, den verschachtelten Instanzpfad und den Kbus-Zielslot
`0x2a1c0`. Die Alias-Sicherheit ist statisch nicht belegt. Deshalb wird weder
die Gleichheit der beiden Dal-Slots noch ein ausgeführter Kbus-Call mit diesem
Ziel als VERIFIZIERT ausgegeben.

## Eingaben und Methode

| Eingabe | Größe | SHA-256 | Verwendung |
|---|---:|---|---|
| `codesys3` | 5.181.396 | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | exakter ARM-Code |
| WP-XE164-125 `report.md` | 7.604 | `5008f6d6f1ff8b5259c3a59543bd73e210a655fe1865861a201581d1c5dece16` | Loader-/Entry-Handoff |
| WP-XE164-125 `function-disassembly.txt` | 3.392 | `de11be1f744ffd81096202a80d8ec0c971049c9cfcd2357c8b47756b738f7621` | vollständige adressierte Helper-Instruktionen |
| WP-XE164-119 `report.md` | 8.459 | `417bb844320d64a3cda06754b3aa95e835e7b9b5225413d570c3ca653a747fb6` | Dal-Entry-Kopie `+0x34` |
| WP-XE164-122 `report.md` | 4.295 | `d66a5be8d965d77d381860c77d9d5985c4fe5efcc9d8bd90f1646c65e1641aec` | akzeptierte Dal/Kbus-Flusssynthese |

Methode: integrative GPT-6.1-SOL-Self-Review akzeptierter, hashgebundener
statischer Befunde. Die neue Ableitung ist reine ARM-Konstanten- und
Stackoffsetarithmetik über `0x2fc55c..0x2fc5c8`; es wurde keine neue
Decompilation benötigt. `flow.tsv` trennt jede verifizierte lokale Kante von
den zwei bedingten Cross-DSO-/Alias-Schritten. Pseudocode oder Feldnamen werden
nicht als Originalquelle behandelt.

## Alternative Erklärung und Restunsicherheit

Der generische Loader kann im betrachteten Laufzeitkontext eine andere
Komponente laden; dann erhält deren `ComponentEntry` zwar dasselbe lokal
initialisierte Objekt, aber die IoDrvDal-spezifische Weiterleitung folgt nicht.
Auch bei Dal kann der optionale indirekte Call den Argumentspeicher über einen
Alias verändern. Schließlich kann `0x002fe12c` eine statische Codeadresse sein,
ohne dass ihre konkrete Zielroutine im Scope dieses Pakets qualifiziert ist.

**OFFEN:** konkrete dynamische Bindung des Loaderaufrufs an IoDrvDal,
Zielkörper/Vertrag von `0x002fe12c`, Aliaswirkung des Dal-Zwischencalls,
Ausführung, Runtime und Hardware.

## Prüfstatus

| Prüfung | Status |
|---|---|
| Eingabegrößen und SHA-256 | PASS |
| `movw`/`movt`-Komposition zu `0x002fe12c` | PASS |
| Stackarithmetik `(fp-0x28) - (fp-0x5c) = 0x34` | PASS |
| Kein Überschreiben von lokal `+0x34` bis `blx r2` im begrenzten Ausschnitt | PASS |
| Trennung lokaler Befund / dynamische Dal-Bindung / Aliasannahme | PASS |
| Runtime, VM, Geräte, Netzwerk und Hardware | NOT_RUN |
| Unabhängiger Review | NOT_RUN |
| GPT-6.1-SOL Self-Review | PASS |
