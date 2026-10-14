# XE164/C166-Analyse: Arbeits- und Übergabestruktur

Dieses Verzeichnis enthält ausschließlich die öffentliche, herstellerdateifreie
Arbeitsstruktur für die Offlineanalyse der `XE164L*.bin`-Dateien. Es enthält
keine Firmware, keinen dekompilierten Herstellerquelltext, keine privaten
Geräteinformationen und keinen Hardwarezugriff.

Der aktuell vorbereitete private Arbeitsbereich liegt auf der Analyse-VM unter:

```text
/home/developer/.codex/virtualwago-research/xe164-analysis
```

Dieser Pfad ist nicht Teil des Git-Repositories und ist mit Modus `0700`
abgeschirmt. Für eine andere Umgebung muss der Leitagent einen ausdrücklich
bereitgestellten privaten Root verwenden; er darf keinen Pfad aus alten
Dokumenten oder Logs ableiten.

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
