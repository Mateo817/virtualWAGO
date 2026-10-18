> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-212 — Gegenprüfung der Vertragsmatrix

## Ergebnis

**PASS:** Alle neun Zeilen R1–R9 bleiben innerhalb der kanonischen Claims
E-XE164-230..236. Keine Zeile vermischt eine statische lokale Beobachtung mit
einem behaupteten Runtime-Nachweis; die Vertragsmatrix führt ihre verbundenen
Aussagen durchgehend als **HYPOTHESE**. Wo E-XE164-232/233 statische
Inventar-/Exportfakten als **VERIFIZIERT** belegen, werden diese nur für die
Kandidatenabgrenzung verwendet, nicht als Nachweis einer Runtime-Bindung.

Die neun Einzelbewertungen mit den geprüften Satzfragmenten, Evidence-IDs und
jeweiligen Grenzen stehen in `review.csv`. Es wurde keine Abweichung gefunden;
damit ist keine Korrektur oder BLOCKED-Einstufung erforderlich.

## Prüfung und Grenzen

Die Prüfung war textuell und offline. Geprüft wurden nur R1–R9 in der
WP-XE164-211-Matrix gegen E-XE164-230..236 in der kanonischen Evidence. Die
Matrix benennt keine API, Typen, Semantik, vollständigen Returnmengen oder
Runtime-Gewinner. Die offenen Bedingungen wie Target-Auswahl, Pointergültigkeit,
opake Call-Effekte, Stack-/Registererhalt und Aliasüberlappung sind je nach
Zeile ausdrücklich festgehalten.

## Eingabeidentitäten und Vorintegrationsprojektion

Der Validator liest den aktuellen `evidence/index.md`-Stand, bindet aber wegen
der enthaltenen WP-XE164-212-Output-Identitäten keinen Vollindexhash: Diese
Identitäten beziehen sich auf die Worker-Artefakte und würden eine
selbstreferenzielle Bindung erzeugen. Stattdessen erzeugt er bytegenau eine
selbstreferenzfreie Vorintegrationsprojektion, indem er genau eine
Tabellenzeile mit Präfix `| E-XE164-238 |` sowie genau vier
Output-Identity-Zeilen mit Präfix `- WP-XE164-212 ` entfernt. Die jeweiligen
Zeilenanzahlen werden geprüft. Die Projektion hat **312998 Bytes** und muss
den SHA-256
`376acf489c0f27a52b46103703ee0c4e09911fc7bfe8a5e8c1382a3aa883c450` ergeben;
dies ist der tatsächlich für den Gegencheck gebundene Evidence-Stand.

Die unveränderten WP-XE164-211-Eingaben stimmen weiterhin mit ihren
vorgegebenen Hashes überein:

- `work/root/WP-XE164-211/contract.csv`: `2b8fb49c36df6ff5ccb77197c70ad1776aeeb67e725f030e46bcf9950009868a`
- `work/root/WP-XE164-211/report.md`: `3c5234dc75201cca85499ba79c1da6d7d85f7d2dedc2b01b15709c5170ff6d19`

Validator: `validate.py` — **PASS**. Zeilenentfernung 1+4,
Projektionsgröße/-hash, weitere Eingabehashes, Reviewzeilen (**9**, IDs exakt
R1–R9), Ergebnisse (alle PASS) und SHA-256-Manifest: **PASS**.

Provenienz: WP-XE164-212 Textgegenprüfung, Self-Review. Der integrierte Index
enthält E-XE164-238 und vier WP-XE164-212 Output-Identity-Zeilen; deren exakt
gezählte Entfernung rekonstruiert den hashgebundenen, selbstreferenzfreien
Vorintegrationsstand. Keine Binärdateien, Disassembly, Geräte, Runtime oder
Netzwerk verwendet; kein unabhängiger Review.
