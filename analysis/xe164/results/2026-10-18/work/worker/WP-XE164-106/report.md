> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-106 — lokale Blob-Suche

## Ergebnis

**Befundstatus: VERIFIZIERT.** Beide älteren Ziel-SHA-256-Werte entsprechen vollständigen Blob-Inhalten im lokalen Git-Objektspeicher und sind in Commit `df75c3005d8de71647f11ddd4f8effa264326446` exakt an die benannten Pfade gebunden. Die aktuellen Eingabe-SHA-256-Werte sind in Commit `cbe23a53910e41d9daaee30358c635a3b4ce89eb` an dieselben Pfade gebunden; diese Blob-IDs stimmen auch mit den Pfad-Blob-IDs von HEAD `e56bb8ed488137f3d9276bfcbec6f33d2917114a` überein.

| Pfad | Historischer Blob (SHA-256 / Git-SHA-1) | Aktueller Blob (SHA-256 / Git-SHA-1) |
| --- | --- | --- |
| `tools/adi_catalog_profiles.h` | `3e2c62c302add32418b861ae37b276f8b15353978d2f30762ead8c12558127ba` / `103d8cec0638071d0ec8bf02cb3ada63ed12c12f` | `332e030aa1274aadb7e92314b2c7d3419c0d4357eb3b7fe6a60ac3d069af66c0` / `e8e330a95872bb60dc9c564b4a7d41513d21ab47` |
| `config/module-catalog.json` | `1415eb043e4d2295c82d6e7c1d2e9a2e1ba8121681868b29aa564e013521a89c` / `ee164ad28086fbe83d26920fcd35f250bb3cf647` | `938575e620fdc292d5ea674db5eeb95d8115c6f00e659aadc184719e2bc58831` / `5b1c2f32642672c536f6a9d1aef9d38e8ab6a081` |

## Relevante Semantik

Zwischen Revisionen gibt es **keine inhaltliche Änderung** an den untersuchten Digital-8/16-Profilfeldern oder an den Modell- und Descriptor-Feldern der vier Artikel.

- `digital8`: Artikel `750-430`, `750-530`; 8 Eingangs- und 8 Ausgangsbits; Modul-IDs `34817, 34818` (`0x8801, 0x8802`); Parameter10 `UUUU8801UUUUUUUU`, `UUUU8802UUUUUUUU`; Prozessfeldtyp `stdBYTE8bools`; Eingangs-Offsets `0, 0`, Ausgangs-Offsets `0, 0`.
- `digital16`: Artikel `750-1405`, `750-1504`; 16 Eingangs- und 16 Ausgangsbits; Modul-IDs `36865, 36866` (`0x9001, 0x9002`); Parameter10 und Prozessfeldtyp jeweils `null`; Eingangs-Offsets `0, 16`, Ausgangs-Offsets `0, 0`.
- Modellwerte bleiben gleich: `750-430` hat 1 Eingangsbyte und Maske 255; `750-530` hat 1 Ausgangsbyte und Maske 255; `750-1405` hat 2 Eingangsbytes und Maske 65535; `750-1504` hat 2 Ausgangsbytes und Maske 65535. Die jeweils nicht anwendbaren Bytes/Masks bleiben 0 bzw. `null` wie im JSON-Modell.
- Descriptor-Zuordnung bleibt gleich: `750-430` ID `8801_0750043000000000`, SHA-256 `26d302678905d2e8f4c7e34880cf830c4ad56361ebd647e6ed82a9e02c81dd91`; `750-530` ID `8802_0750053000000000`, SHA-256 `84b4043d448c44155a36916a1b65a39f20ba0560459d3c0ffac53fba351daa5d`; `750-1405` ID `9001_0750140500000000`, SHA-256 `2ea6fb96d1db35228450ccd94454f1e51b562a6e1982e416f34eed2feb056273`; `750-1504` ID `9002_0750150400000000`, SHA-256 `207e7d654f98a180b06cb75117e282ac2a85f956cbb5d057113d76846a6dc991`.
- Im Header sind sämtliche Deklarationen und Digital-8/16-Konstanten bytegleich. Nur die generierte Kommentarzeile zum kanonischen Katalog-Hash unterscheidet sich (`e001c8f610e2b677e9833fd6d9cbc650e3bdd65572366e9f8b91e2485edc8694` historisch, `3b1a618c9807893308eaa3f5de8c42a27ac4093bb8ea91660921634db8636340` aktuell). Der Katalog als Ganzes hat sich geändert (Revision `2026-10-12.1` zu `2026-10-14.1`, 14600 zu 15581 Bytes); diese Änderung ändert die oben verglichenen vier Artikel und zwei Profile nicht.

## Suchumfang und Grenzen

Git meldet Objektformat SHA-1, Version 2.47.3, 465 lokale Objekte insgesamt; die vollständige `git cat-file --batch-all-objects`-Auflistung enthielt 317 Blob-Objekte, die alle durch SHA-256 ihrer entpackten Inhalte geprüft wurden. Die Suche umfasste damit auch lokale, nicht erreichbare Objekte. `search-scope.txt` hält HEAD, alle von `git show-ref --head` gemeldeten Refs, die eindeutigen Commit-IDs aus allen Reflogs sowie die gefundene Pfad-Historie fest. Für die zwei Pfade erscheinen dort die Commits `df75c300…` und `cbe23a539…`. Keine Netzwerk-, VM-, Geräte- oder Fremdrepository-Abfrage wurde ausgeführt.

Alternativerklärung: Der ältere Header-Hash könnte isoliert als bloße Generator-Metadatenänderung missverstanden werden. Der Bytevergleich zeigt, dass genau diese Kommentarzeile auf den geänderten Gesamtkatalog verweist; die Profildeklarationen sind gleich. Ebenso erklärt die größere Katalogdatei Änderungen an anderen Katalogbereichen, nicht Änderungen an den ausgewählten Digital-8/16-Daten.

Restunsicherheit: Der Befund beschreibt den vollständigen derzeit lokalen Git-Objektspeicher und seine derzeit vorhandenen Refs/Reflogs. Er belegt nicht, ob weitere, inzwischen entfernte oder niemals lokal gespeicherte Objekte anderswo existieren. Der Vergleich weist Dateiinhalte und Git-Pfadbindung nach, nicht unabhängige fachliche Richtigkeit.

## Tests und Reproduktion

**Tests: PASS.** `validate.py` verifiziert alle vier SHA-256-Werte, Git-Tree-Pfadbindungen, Gleichheit der zwei JSON-Profile, Gleichheit der vier Artikel-Descriptor-/Modell-Felder und Gleichheit der Header-Inhalte ohne die Katalog-Hash-Kommentarzeile. Ergebnis: `PASS: target blob hashes, tree/path bindings, 2 profile objects, 4 article descriptors/models, and header values validated`.

Werkzeuge: Git 2.47.3; GNU coreutils `sha256sum` 9.7; Python `validate.py` nutzt die Standardbibliothek `json`, `hashlib`, `pathlib` (Version in der Laufzeitumgebung: Python 3.13, laut Ausführungs-Traceback). Befehl aus dem Repository: `bash PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-106/search.sh && python3 PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-106/validate.py`.

`search.sh` ist das reproduzierbare lokale Such- und Extraktionsprotokoll; `search-scope.txt`, `object-hits.tsv` und `tree-bindings.tsv` enthalten die vollständige relevante Inventur bzw. Trefferbindung. Die extrahierten historischen und aktuellen Dateien liegen unverändert als eigene Ausgabeartefakte bei. `repository-status-after.txt` ist leer; das Repository blieb unverändert. `SHA256SUMS` listet alle Ausgabedateien außer sich selbst, `SHA256SUMS.sha256` hasht diese Summendatei.
