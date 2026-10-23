# XE164/C166-Analyse: Arbeits- und Übergabestruktur

**Fortsetzung, 23.10.2026:** [Gebundene Gerätebaum-, Kernel- und XE164-Analyse](../../docs/kbus-kernel-reconstruction-2026-10-23.md) mit [separater Evidence](../../evidence/kbus-kernel-reconstruction-2026-10-23.json). Die historische Ergebnissicherung unter `results/2026-10-18/` bleibt unverändert.

Dieses Verzeichnis enthält die öffentliche, herstellerdateifreie
Arbeitsstruktur und bereinigte Ergebnisse der Offlineanalyse der `XE164L*.bin`-Dateien. Es enthält
keine Firmware, keinen dekompilierten Herstellerquelltext, keine privaten
Geräteinformationen und keinen Hardwarezugriff.

Die [Ergebnissicherung vom 18.10.2026](results/2026-10-18/README.md) enthält
444 Evidence-IDs, 303 Funktionszuordnungen und 420 bereinigte Paketberichte,
einschließlich Korrekturen und offener Fragen. Exporthashes und eine
hardwarefreie Integritätsprüfung binden diese öffentliche Kopie; Originaldateien,
private Modelle und Rohtraces bleiben lokal. Die Gesamtanalyse ist nicht abgeschlossen.

Der private Arbeitsbereich wird dem Leitagenten außerhalb des Repositories
ausdrücklich bereitgestellt und mit Modus `0700` abgeschirmt. Sein konkreter
lokaler Pfad wird nicht veröffentlicht. Für eine andere Umgebung muss der
Leitagent einen neu bereitgestellten privaten Root verwenden; er darf keinen
Pfad aus alten Dokumenten oder Logs ableiten.

## Trennung der Ablagen

```text
Öffentliches Git: analysis/xe164/
├── README.md
├── prompts/
│   └── sol-lead.md
└── templates/
    ├── artifacts.tsv
    ├── current-handoff.md
    ├── evidence-index.md
    ├── function-map.csv
    ├── session.md
    └── work-queue.md

Privater Root: xe164-analysis/
├── README.private.md
├── scope.md
├── manifest/
│   ├── artifacts.tsv
│   ├── toolchain.md
│   └── sessions/
├── sources/<artifact-id>/
├── work/
│   ├── rea/
│   ├── ghidra/
│   ├── rizin/
│   └── worker/<work-package-id>/
├── derived/
│   ├── composites/
│   ├── disassembly/
│   ├── pseudocode/
│   └── callgraphs/
├── evidence/
│   ├── index.md
│   ├── rea/
│   ├── ghidra/
│   └── rizin/
├── notes/
│   ├── function-map.csv
│   ├── memory-map.md
│   ├── protocols.md
│   └── open-questions.md
├── handoff/
│   ├── CURRENT.md
│   └── snapshots/
├── logs/
└── scratch/
```

`sources/` enthält unveränderte, schreibgeschützte Eingaben. `work/` enthält
Werkzeugprojekte und voneinander getrennte Workerbereiche. `derived/` enthält
reproduzierbare Ableitungen. Nur der Leitagent schreibt in `evidence/index.md`,
`notes/` und `handoff/CURRENT.md`.

## Verbindlicher Analysezyklus

1. Repositoryzustand, `AGENTS.md` und die dort geforderten Dokumente frisch
   prüfen. Ältere Übergaben bleiben revisionsgebundene Quellen.
2. Privaten Root, Dateirechte, `manifest/artifacts.tsv`, Werkzeugstand und
   `handoff/CURRENT.md` lesen. Eingaben vor Verwendung erneut hashen.
3. Kleine, konfliktfreie Work Packages in `work-queue.md` festlegen. Jedes
   Paket bindet Frage, Artefakt-ID, SHA-256, Adressbereich, Ausschlüsse,
   Ausgabepfad und Abnahmekriterien.
4. REA zuerst verwenden. Wenn die benötigte C166-Funktion dort nicht
   unterstützt wird, den beobachteten Grund festhalten und direkten
   Ghidra-C166- beziehungsweise Rizin-Fallback mit exakter Importkonfiguration
   verwenden.
5. Worker schreiben ausschließlich unter `work/worker/<id>/`. Der Leitagent
   prüft und integriert Ergebnisse; ein Workerbericht ist keine unabhängige
   Hardware- oder Runtimeevidence.
6. Jede Aussage als `VERIFIZIERT`, `HYPOTHESE`, `OFFEN` oder `BLOCKED`
   klassifizieren. Tests verwenden `PASS`, `FAIL`, `NOT_RUN` oder `BLOCKED`.
7. Nach jedem integrierten Paket `evidence/index.md`, Funktionskarte,
   Arbeitsqueue und `handoff/CURRENT.md` aktualisieren. Übergabepunkte zusätzlich
   als datierten Snapshot sichern.

## Evidence-Regeln

Jeder wesentliche Befund bindet mindestens Artefakt-ID und SHA-256,
Dateioffset beziehungsweise Analyseadresse, Werkzeug und Version, Methode,
Geltungsbereich, alternative Erklärung und Restunsicherheit. Dateioffsets,
Analyseadressen, Laufzeitadressen und Hardwareadressen dürfen nicht ohne Beleg
gleichgesetzt werden.

FW30-Quellen qualifizieren keine FW31-ABI. C167-SFR-Namen qualifizieren keine
XE164-Registerbelegung. Pseudocode ist eine Werkzeugableitung, kein
Originalquelltext. Weder Exportnamen noch einzelne Strings belegen einen
vollständigen Funktionsvertrag.

Rohbinaries, Ghidra-Projekte, REA-Bundles und unbereinigte Logs bleiben im
privaten Root. Für öffentliche Git-Änderungen werden Dateien einzeln ausgewählt
und auf Herstellerinhalt, Gerätekennungen, Zugangsdaten und private Pfade
geprüft.

Der einsatzfertige Leitprompt steht in
[prompts/sol-lead.md](prompts/sol-lead.md).
