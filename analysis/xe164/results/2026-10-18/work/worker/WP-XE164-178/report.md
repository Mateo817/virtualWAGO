> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-178 – statischer Abgleich AC-01..AC-12

## Ergebnis

Der untersuchte Quelltext ist ein eigenes In-Memory-ADI-Modell. Sichtbar implementiert sind darin vor allem getrennte angeforderte/wirksame Modell-Ausgänge und ein PUSH-Callback mit getrenntem äußerem und innerem Modellstatus. Mehrere AC-Zeilen beschreiben hingegen Original-Consumer- oder Providerpfade, die diese Quelldatei nicht enthält. Keine Sichtung qualifiziert FW31-ABI, Originalruntime oder Hardware.

Die Matrix klassifiziert AC-07 als `IMPLEMENTIERT` auf Ebene der eigenen Modellzustände; AC-08 als `NICHT_ANWENDBAR` für dieses explizit hardwarefreie Modell; AC-04 und AC-06 als `NICHT_SICHTBAR`; die übrigen Zeilen als `PARTIELL`. Diese Kategorien beziehen sich ausschließlich auf direkte Sichtbarkeit in genau der geprüften Datei. Alle zwölf Teststatuswerte sind `NOT_RUN`.

## Beobachtungen und Fundstellen

- Der Dateiheader beschreibt ein „own in-memory“ Modell und grenzt es von byte-identischem DAL-Verhalten und einem Hardware-/Gerätebackend ab (Zeilen 3–5).
- Digital-8/16 Auswahl wird als Profilzeiger sichtbar (34–38); Eingaben werden auf das Profilmaskenfeld begrenzt (234–239). `requested_outputs` und `effective_outputs` sind getrennte Zustandsfelder (65–71), getrennte Snapshot-Werte (181–188) und werden in WriteEnd unterschiedlich aktualisiert (547–550). `effective_permit()` verlangt App Running, Permit, gesundes Watchdog und keinen Modellfehler (150–153).
- Eigene Read-/Write-Methoden sind vorhanden und in einer Interface-Tabelle gebunden (456–622, 854–888), aber die im Vertrag beschriebene Consumer-Reihenfolge und die ReadInputs/WriteOutputs-Statusaggregation erscheinen in dieser Datei nicht.
- Der Modell-PUSH-Zweig schreibt bei gültigem `return_value` einen inneren DAL-Status und liefert außen DAL_SUCCESS (721–731). Das belegt nur die lokale Trennung zweier Rückgaben; die Kbus-Auswertung aus AC-05 fehlt.
- GET_UID und READ_CONF_REG sind als nicht unterstützt kommentiert, latchen einen eigenen Modellfehler und schreiben -1 als inneren Status (769–778). Das belegt keine dynamische Originalcaller-Reichweite.
- Init/Exit, App-State und Watchdog-Zustände haben Modellcode (307–323, 679–691, 802–851), schließen aber weder Originalruntime-Lifecycle noch die in AC-12 genannten Trials.

## Evidenz- und Teststatus

`VERIFIZIERT` gilt nur für die jeweils angegebenen Quelltextbeobachtungen oder die begrenzte Feststellung, dass ein Kriterium in dieser Datei nicht sichtbar ist. Aussagen zu Original-ABI, Herstellersemantik, Runtime-Bindung, Provider-Erreichbarkeit und Hardware bleiben `OFFEN`; sie wurden nicht durch Header-, Runtime- oder Binaryanalyse ergänzt. Für alle AC-Zeilen gilt `NOT_RUN`: es wurden keine Builds oder Tests ausgeführt.

## Alternativerklärungen

Die Abwesenheit eines Pfades in dieser einzelnen Datei kann bedeuten, dass er in einem anderen eigenen Modul oder in einem nicht eingesehenen Originalconsumer implementiert ist. Umgekehrt beweisen passende Namen und Interfaceeinträge keine ABI-Kompatibilität oder dynamische Erreichbarkeit. Modellzustände und Kommentartext können eine beabsichtigte Modellgrenze ausdrücken, jedoch keine Laufzeit- oder Hardwarewirkung bestätigen.

## Restunsicherheit

Es bleibt offen, ob und wie die eigenen Interfacefunktionen außerhalb dieser Datei aufgerufen werden; diese Aufgabe schloss Caller, Header und Tests explizit aus. Ebenso ungeklärt bleiben die im Abnahmevertrag genannten Original-Consumer-Mechaniken, private ABI-/Slot-Verträge, Runtime-Propagation, Profil-Trials sowie alle Geräte- und Hardwareeffekte. Die Matrix trifft deshalb keine Slot-, Struct-, API- oder Herstellersinn-Aussagen.

## Tooling und Eingaben

Hash-/Größenprüfung: `sha256sum`, `wc -c`; Textsuche/-sichtung: `rg`, `nl -ba`, `sed`. Versionen: ripgrep 15.2.0, GNU coreutils 9.7, GNU Bash 5.2.37, GNU sed 4.9. REA ist für diesen begrenzten Quelltextabgleich nicht einschlägig. Die gemessenen Eingaben entsprechen den in [assignment.md](assignment.md) dokumentierten Hashes und Größen.

## Erzeugte Dateien und SHA-256

Die Prüfsummen für sämtliche erzeugten Artefakte einschließlich dieses Reports stehen in `SHA256SUMS` (der Manifestdatei selbst nicht, da sie keine nicht-rekursive eigene Prüfsumme enthalten kann). `validate.py` prüft Eingabeidentität, genau AC-01..AC-12, Kategorien/Status, Existenz aller referenzierten Quelldateizeilen und Manifestintegrität.
