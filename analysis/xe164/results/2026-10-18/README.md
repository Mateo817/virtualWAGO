# XE164-Ergebnissicherung — 18. Oktober 2026

Dieser unveränderlich gedachte Snapshot sichert die bereinigten, selbst verfassten Ergebnisse der privaten XE164-/virtualWAGO-Offlineanalyse: **444 Evidence-IDs, 303 Funktionszuordnungen und 420 Paketberichte**. Die Gesamtanalyse ist noch nicht abgeschlossen. Eine vollständige virtuelle WAGO oder ein durchgehend qualifizierter Originalstack wird nicht behauptet.

## Einstieg

- [Fachlicher Stand und nächste Schritte](handoff.md)
- [Evidence-Index mit Status, Methoden und Grenzen](evidence/index.md)
- [Funktionskarte, CSV mit zwölf Spalten](notes/function-map.csv)
- [Schnittstellen-/Protokollnotizen](notes/protocols.md)
- [Offene Fragen](notes/open-questions.md)
- [Speicher- und Adressnotizen](notes/memory-map.md)
- [Arbeitsqueue](work-queue.md)
- [Eingabeartefakte: Metadaten und Hashes](manifest/artifacts.tsv)
- [Exportmanifest mit Original- und Exporthashes](export-manifest.json)

Die Berichte liegen unter work/root/WP-XE164-*/report.md und work/worker/WP-XE164-*/report.md. Sie sind historische Ergebnisse ihrer jeweiligen Revision. Der zentrale Evidence-Index enthält auch Ablehnungen, spätere Korrekturen und stärkere Prämissen; ein einzelner alter PASS ersetzt diese Einordnung nicht. Die Arbeitsqueue und ältere Notizen behalten ihren datierten Scope; für den letzten konsolidierten Zustand gilt handoff.md.

## Umfang der Sicherung

Enthalten sind selbst verfasste Analyseberichte, Zusammenfassungen, Tabellen, Quellenidentitäten, Reviewbefunde und offene Fragen. Alle 444 kanonischen Evidence-Zeilen und alle 303 CSV-Datenzeilen sind erhalten. WP440/WP441/WP442 sind als fertige, noch nicht kanonisch integrierte Berichte mitgesichert; sie erhöhen die Evidence-Zahl nicht.

Die öffentliche Kopie entfernt lokale Benutzer-/Arbeitsverzeichnisse sowie Code- und Listingblöcke. Redaktionen sind im Exportmanifest je Datei gezählt. PRIVATE_ANALYSIS_ROOT, PRIVATE_LOCAL_PATH und REPOSITORY_ROOT sind Platzhalter; relative work/- und sources/-Namen können weiterhin logische Verweise auf das private Nachweispaket sein. Sie versprechen keine hier vorhandene Eingabedatei.

Originalbinaries, Firmware-/SDK-Archive, Herstellerquelltext, vollständige Disassemblierungen, Rohtraces, Werkzeugprojekte und private Ausführungsumgebungen werden nicht mitgesichert. Die privaten Modelle und Validatoren benötigen teilweise solche Eingaben und bleiben ebenfalls lokal. Dieser Snapshot ist eine Sicherung der Forschungsergebnisse; vollständige Wiederholung der ursprünglichen Analysen benötigt das private Eingabepaket.

Original- und Exporthash sind bewusst verschieden, wenn ein Bericht bereinigt wurde. Die im Evidence-Index genannten ursprünglichen Prüfergebnisse und Hashes beziehen sich auf ihre damaligen privaten Dateien. Das Exportmanifest bindet zusätzlich die hier tatsächlich gespeicherten Bytes. Die Veröffentlichung führt keine historischen Firmware-/Runtimeprüfungen neu aus.

## Prüfung des öffentlichen Snapshots

Vom Repository-Root: python3 tools/validate_xe164_results.py

Diese hardwarefreie Prüfung kontrolliert Exporthashes, Dateiauswahl, 444 eindeutige Evidence-IDs, 303 CSV-Zeilen mit zwölf Spalten, Referenzen und begrenzte Prüfungen auf versehentlich übernommene private Inhalte. Sie belegt die Integrität der Ergebnissicherung, keine Runtime-, ABI-, Kernel- oder Hardwarefunktion.

Die Publikationsprüfung ist Root-Self-Review; ein tatsächlich durchgeführter zusätzlicher Publikationsreview wird im PR ausgewiesen. Die einzelnen Forschungsreviews sind in den jeweiligen Nachweisen getrennt benannt.
