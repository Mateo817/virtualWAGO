> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-239 — selector-15 consumer synthesis

## Ergebnis

**OFFEN:** Die korrigierte, in drei Partitionen aufgeteilte statische Suche belegt keinen weiteren codesys3-Verbraucher, der sichtbar konstantes `r0=15` an einen indirekten Aufruf liefert, dessen Ziel aus Basis `+0x20` geladen wurde. Sie schließt einen solchen Verbraucher aber nicht global aus.

**VERIFIZIERT:** Der mittlere Bereich enthält 23 direkt per Branch/Fallthrough verbundene Zielketten und 17 unmittelbare `r0=15`-Stellen; keine Kette verbindet beides sichtbar. Der hohe Bereich enthält acht entsprechende plain-`ldr`-Ketten und zwölf unmittelbare `r0=15`-Stellen; ebenfalls keine sichtbare Verbindung. Die unabhängigen Gegenprüfungen fanden eine ausgelassene mittlere Kette, einen falschen Datei-Offset und eine überbreite `ldr`-Zählung. Alle drei Punkte wurden in den Ursprungsberichten korrigiert, ohne einen sichtbaren Selector-15-Treffer zu erzeugen.

**OFFEN:** Im niedrigen Bereich fand der direkte, call-clobber-aware Scan keinen Treffer, löste aber 101 parsergebundene indizierte PC-Dispatches in 222 loadtragenden Symbolmarken nicht als CFG-Kanten auf. Außerdem stammt `r0` bei mehreren akzeptierten mittleren/hohen Calls aus Speicher, Eingang oder einem unbekannten Register. Diese Werte sind nicht statisch als 15 belegt, aber auch nicht als ungleich 15 verifiziert.

## Schlussfolgerung für den virtualWAGO-Provider

**HYPOTHESE:** Der führende Providerplatz `+0` hat mit `CMInitComponent`→sichtbarer Selector `2`→IoDrvDal-Lane eine stärkere Originalconsumer-Kette als `+4`. Für `+4` bleibt nur IoDrvDals sichtbarer Selector-15-Fall plus die bedingte exact-libdal-Bindung; ein Manager/Consumer, der diesen Wert tatsächlich liefert, ist weiter **OFFEN**.

Damit darf `+4` nicht als verpflichtende „Exit“-Operation implementiert oder benannt werden. Es bleibt eine priorisierte optionale Kandidatenposition. Der nächste statische Schritt ist eng: die 101 indizierten Dispatches nur soweit auflösen, wie sie einen `+0x20`-Load zu einem `blx`-Ziel und eine mögliche `r0=15`-Definition verbinden können. Alternativ würde runtimegebundene Loader-/Objekt-/Aufrufreihenfolge die statische Restunsicherheit direkt adressieren; Runtime bleibt in dieser Aufgabe **NOT_RUN**.

## Geltungsgrenzen

Pseudocode/Disassembly sind Werkzeugableitungen. Es wird weder ein ABI noch eine Struct-, Feld-, Selector- oder Lifecycle-Semantik behauptet. Sichtbare Konstanten sind keine beobachteten Laufzeitwerte. Diese Synthese ist GPT-6.1-SOL-Self-Review; Workerberichte sind keine Runtime-, Hardware- oder unabhängigen Drittprüfungen.
