> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-230 — Originalconsumer-Selektoren für die führenden Providerpositionen

## Ergebnis

**VERIFIZIERT** ist die statische IoDrvDal-Verbraucherform: Der von `ComponentEntry` veröffentlichte Zielkandidat `0x362c` beginnt einen numerischen Dispatcher. Sichtbares Eingangs-`r0=2` führt über Zelle `0x364c` nach `0x36b0`; dort folgt auf den Getter-PLT-Aufruf ein Load bei Position `+0` und ein indirekter Aufruf. Sichtbares Eingangs-`r0=15` adressiert Zelle `0x3680`; deren getrennt gebundener Inhalt führt nach `0x42f4`, wo auf den Getter-PLT-Aufruf ein Load bei `+4` und ein indirekter Aufruf folgt.

**HYPOTHESE** bleibt die ELF-übergreifende Identität: Exact libdal ist der einzige installierte statische Exportkandidat, sein Getterkörper liefert den Objektbasiskandidaten mit genau den Zellen `+0/+4`, und die IoDrvDal-Importmetadaten passen dazu. Nicht beobachtet sind aber die konkrete Laufzeitauflösung, Interposition, Relokation und ein Calling-Convention-Vertrag für `r0`. Nur unter diesen Bedingungen verbinden sich die lokalen IoDrvDal-Aufrufe mit den exact-libdal-Zielkörpern.

**OFFEN** bleibt jede zeitliche Reihenfolge. `+0` und `+4` liegen nicht in einer linearen lokalen Kette, sondern in getrennten Fällen desselben Dispatchers. Die statischen Befunde belegen weder, dass beide Fälle zur Laufzeit auftreten, noch welcher zuerst kommt, noch dass die Zahlen `2/15` oder die Positionen semantisch Startup/Shutdown bedeuten.

## Enger statischer Vertrag

- **VERIFIZIERT:** Selektor `2` wählt lokal die `0x36b0`-Kette. Nach Position `+0` führt nur sichtbares Post-Call-`r0=0` weiter zu einem frischen Getter/`+8`; nur dessen sichtbares Post-Call-`r0=0` führt zu frischem Getter/`+0x0c`. Vor dem letzten indirekten Call sind lokal `r0=10`, `r1=sp+0x60`, `r2=sp+0x5c` sichtbar.
- **VERIFIZIERT:** Selektor `15` wählt lokal `0x42f4`. Nach Getter und Load `[r0+4]` folgt der indirekte Aufruf; danach verzweigt der Bereich unbedingt nach `0x4194` und verwendet sichtbares Post-Call-`r0` lokal nicht.
- **OFFEN:** Post-Call-`r0` ist jeweils nur der sichtbare Registerwert und keine behauptete ABI-Rückgabe. Bedeutungen, Signaturen, Callee-Effekte und Zielkörper jenseits der gebundenen Bereiche sind unbekannt.

## Bedeutung für virtualWAGO

**HYPOTHESE:** Für die bereits ausgewählte Providergrenze sind `+0` und `+4` nun konkrete, vom originalen IoDrvDal statisch adressierte Kandidatenpositionen und nicht mehr nur aus libdal-internen Zielkörpern erschlossen. Das ist Implementierungspriorität, aber noch keine Freigabe, beide Positionen als zwingenden oder benannten Lifecycle-Vertrag zu implementieren. Dafür fehlen wenigstens Laufzeitbindung, konkrete Aufrufreihenfolge und verifizierte Ein-/Ausgabeverträge.

Der Befund verlangt keine Nachbildung des physischen K-Bus oder weitere breite XE164-Dekompilation. Er verengt den nächsten sinnvollen Offline-Schritt auf die sichtbaren Eingaben/Nachläufe dieser beiden Originalconsumer-Fälle und ihre bereits vorhandenen Akzeptanzmodelle.

## Methode und Grenzen

Die neun Matrixzeilen wurden ausschließlich aus den acht hashgebundenen Reports in `inputs.tsv` synthetisiert. WP227/228/229 stammen von disjunkten Luna-HIGH-Paketen; der Leitagent hat Validatoren/Manifeste erneut ausgeführt und die exakten Fenster mit GNU ARM objdump 2.44 gegengeprüft. Dies ist GPT-6.1-SOL-Self-Review, kein unabhängiger Runtime- oder Hardware-Review.

Tests: Eingabehash-/Matrix-/Manifestvalidator **PASS**; Runtime und Hardware **NOT_RUN**.
