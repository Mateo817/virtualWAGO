> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-233 — Managerselektoren gegen die führenden Providerpositionen

## Ergebnis

**VERIFIZIERT:** Der vollständige `CMInitComponent`-Körper enthält acht indirekte Aufrufstellen, die von zehn sichtbaren Loads aus Eingangsobjekt `+0x20` erreicht werden. Die lokal gesetzten `r0`-Werte sind `2, 3, 7, 4, 500, 5, 6, 1000`. Beim `r0=2`-Aufruf wird das Ziel aus `+0x20` geladen und nullgeprüft; lokal sichtbar sind außerdem `r1=frame-0x20` sowie statusabgeleitete `r2/r3`-Formen. Später wird der sichtbare Post-Call-`r0`-Wert lokal kopiert, ohne dass daraus ein ABI-Rückgabevertrag folgt.

**HYPOTHESE:** Nur unter der bereits bedingten E-XE164-201/203-Verbindung des registered-block-Felds `+0x20` mit exact IoDrvDal `0x362c` wählt dieser Manageraufruf IoDrvDal-Selektorfall `2` und damit die getter-gefolgte Position `+0`. Das ist jetzt die engste statische Manager→IoDrvDal→Provider-Kette für die führende Position, aber weiterhin kein Laufzeitbindungs- oder Signaturnachweis.

**VERIFIZIERT:** Der vollständige, disjunkte `CMExitComponent`-Körper enthält sechs indirekte Aufrufstellen, erreicht von sieben Loads aus Eingangsobjekt `+0x20`. Die sichtbaren `r0`-Konstanten sind `10, 11, 2200, 12, 13, 14`; sichtbares `15` tritt an keiner dieser Stellen auf. Da IoDrvDals `+4`-Lane vom sichtbaren Dispatcherwert `15` gewählt wird, stellt dieser Exit-Körper allein die `+4`-Invocation nicht her.

## Konsequenz

Die bisherige lifecycle-artige `+0/+4`-Paarhypothese ist statisch asymmetrisch gestützt: Für `+0` existiert eine bedingte Managerkette über `CMInitComponent`; für `+4` fehlt in `CMExitComponent` genau der benötigte sichtbare Selektor `15`. Das verbietet eine einfache Benennung als Init/Exit-Paar. Es widerlegt nicht, dass ein anderer Managerkörper, ein berechneter Wert oder eine Runtime-Sequenz Selektor `15` auslöst.

Für virtualWAGO bleibt `+0/+4` eine priorisierte Kandidatenoberfläche, aber nur `+0` hat jetzt diesen zusätzlichen bedingten Managerpfad. Der nächste statische Schritt ist eine begrenzte Inventur anderer Verbraucher des registered-block-Ziels beziehungsweise des sichtbaren Selektors `15`; physische K-Bus- oder XE164-Innenlogik liefert die fehlende Evidenz nicht.

## Methode und Grenzen

Die acht Zeilen in `manager-selector-matrix.tsv` wurden aus den fünf exakt hashgebundenen Eingaben synthetisiert. Root führte die Worker-Validatoren und Manifeste erneut aus und wiederholte die kompletten Load/`blx`-Inventare mit GNU ARM objdump 2.44. Keine Registerwerte wurden über opaque Calls propagiert.

Dies ist GPT-6.1-SOL-Self-Review. Runtime und Hardware sind **NOT_RUN**. Calling Convention, dynamische DSO-/Getterbindung, semantische Phasennamen, tatsächlich ausgeführte Pfade und zeitliche Reihenfolge bleiben **OFFEN**.
