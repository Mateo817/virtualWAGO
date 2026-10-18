> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-059 — Relevanz akzeptierter FW30-XE164-Evidence für den ADI-Ersatzvertrag

## Ergebnis

**HYPOTHESE:** Keiner der akzeptierten Befunde E-XE164-001..066 belegt eine zusätzliche Signatur, Datenstruktur, Aufrufphase, Fehlerregel oder Lifecycle-Anforderung für den minimalen ADI-Ersatzvertrag. Die Befunde reichen aber auch nicht aus, um die gesamte XE164-Firmware als funktional unterhalb der Providergrenze oder als irrelevant für den angestrebten Original-I/O-Strang einzustufen.

Eng begrenzt **VERIFIZIERT** sind statische FW30-Lade-/Empfängermechaniken und statische C166-Codefenster. Die Evidenz verbindet diese nicht mit der ADI-Provider-ABI, den tatsächlichen Runtime-Aufrufpfaden, dem libpackbus-/UIO-/D-Bus-/Diagnosepfad oder einem ausgeführten zyklischen I/O-Strang. Für den Ersatzvertrag folgt daher: **kein zusätzlicher belegter Vertrag aus dieser Evidence**, nicht „ADI ist sicher vollständig“ und nicht „XE164 ist belegt irrelevant“.

Architekturanker: ADR-0001 hält die ersetzte Grenze unter Runtime, I/O-Manager und Originaltreibern und lässt einen tieferen Endpunkt ausdrücklich offen, falls ADI/DAL nicht die vollständige relevante Grenze bildet (ADR-0001.md:17, 21, 71–75). Es verlangt für tatsächlich ersetzte Funktionen belegte Signatur/Layout-, Verhaltens-, Fehler- und Callbackverträge (ADR-0001.md:25, 73). Der aktuelle Arbeitsblock fordert eine frische Zuordnung von Verbraucher, Provider, Phasen, Fehlern, Lifecycle, Synchronisation sowie Async-/Register-/Zeit-/Diagnosepfaden; ADI/DAL bleibt Kandidat bis die benötigten Pfade belegt sind (next-originalstack-block.md:65–69). Diese Anforderungen setzen den Rahmen, werden aber durch die XE164-Evidence nicht selbst erfüllt.

## Relevanzmatrix

| Kategorie | Akzeptierte E-IDs und Fundstellen | (a) Loader/Transport unterhalb ADI | (b) Mögliches sichtbares Verhalten | (c) Vertragsableitung für ADI |
|---|---|---|---|---|
| loader | E-XE164-001..006, 012, 014, 015, 018; evidence/index.md:5–22 | **VERIFIZIERT** für statische L1/L2- und ARM-seitige L3-Lademechanik in den jeweils begrenzten Scopes (001, 003–004, 014, 018); Zuordnung als einzelner Laufzeitpfad/unterhalb der ADI-Grenze bleibt **HYPOTHESE/OFFEN** (005, 015, 018). | **OFFEN**: beobachteter erfolgreicher Transfer, Empfängerplatzierung, Startwechsel und zur Runtime sichtbare Wirkung sind nicht belegt. Statische Transferbestätigung/Retry kann im Bootpfad sichtbar sein. | **VERIFIZIERT: keine zusätzliche ADI-Funktion ableitbar.** Das Loaderprotokoll ist kein belegter ADI-Vertrag. Es ist ebenso wenig belegt irrelevant, bis Prozess-/Aufrufpfadzuordnung vorliegt. |
| startup | E-XE164-007, 009–011; E-XE164-019–066 nur als angrenzende/begrenzte C166-Fenster und Callsite-Befunde, nicht als Startup-Klassifikation; evidence/index.md:11, 13–15, 23–71 | **VERIFIZIERT** sind begrenzte Startup-/Record-Befunde (007, 010) und Callsite-/Codefenster. Ihre Zuordnung zu Init des Original-I/O-Strangs oder zu Code unterhalb ADI ist **OFFEN**; DPP-/Adress- und Zweckdeutungen sind teils ausdrücklich **HYPOTHESE**. | **OFFEN**: Start-/Tabellen-/Hilfsroutinen könnten Zustand, Enumeration oder Konfiguration beeinflussen, aber die akzeptierten Einzelfunde qualifizieren ihre Funktion nicht durchgängig. | **Kein zusätzlicher belegter Vertrag.** Kein akzeptierter Befund bindet die C166-Fenster an ADI-Callbacks, Argumentlayouts oder Rückgaben. **Nicht belegt irrelevant**, weil tatsächliche Caller und Runtimezuordnung unvollständig sind. |
| cyclic | E-XE164-012–013, 016–017; evidence/index.md:16–17, 20–21 | Vektortabellen und `RETI`-Terminals sind statisch **VERIFIZIERT**; Interruptrolle, Dispatch, Laufzeitreachability und zyklische I/O-Beteiligung sind **HYPOTHESE/OFFEN**. | **Möglich** bei Interrupt-/Zeitverhalten, jedoch nicht als ausgeführter Zyklus oder DI/DO-Übernahme belegt. | Keine Ableitung von ADI-Zyklusaufrufen, Pollingraten, Synchronisation oder Callbackvertrag. Daher **kein zusätzlicher belegter Vertrag**, nicht „zyklisch irrelevant“. |
| protocol | E-XE164-004, 008, 014–015, 018; evidence/index.md:8, 12, 18–22 | L2-Empfang und komplementäre ARM-Transferstufen samt Länge/XOR/ACK/Retry sind im statischen Pfad **VERIFIZIERT** (014, 018); die Zuordnung dieses Transfers zu K-Bus/libpackbus oder ADI bleibt **OFFEN** (008, 015). | **Möglich**: ACK `0x81` und Retry-Antwort `0x7e` sind für den begrenzten Transferpfad statisch belegt. Keine beobachtete Runtime-/Anlagenwirkung. | Der Transfer-/Empfängermechanismus erzwingt keinen belegten ADI-Ersatzaufruf. Die K-Bus-Protokollfrage bleibt ausdrücklich **OFFEN**; parallele Software-/Buspfade nicht ausgeschlossen. |
| diagnosis | E-XE164-003, 007, 009–011, 013, 016–017, 019–066; evidence/index.md:7, 11, 13–71 | Kein akzeptierter E-XE164-Befund weist die begrenzten C166-Fenster eindeutig als Diagnosepfad oder als Providerunterbau aus. Numerische Operanden/SFR-/Zwecksemantik bleiben überwiegend **OFFEN**. | **Möglich, aber nicht klassifiziert**: einzelne Interrupt- oder Statusroutinen könnten beobachtbare Diagnose-/Statuswirkung haben; kein spezifischer Diagnoseablauf ist durch diese IDs verifiziert. | **Keine Vertragsableitung.** ADR-0001 dokumentiert separate Diagnose-/D-Bus-/Async-Pfade außerhalb dieses E-XE164-Scope (ADR-0001.md:37, 47); diese XE164-Auswertung schließt sie nicht. |
| error | E-XE164-004, 014–015, 018; evidence/index.md:8, 18–22 | Im engen Loaderpfad sind `0x7e` bei XOR-Mismatch und Rückkehr zum Vierbyte-Empfang statisch **VERIFIZIERT** (018); weitere Fehlerfälle, Fehlerpropagierung und Providerkopplung bleiben **OFFEN**. | **VERIFIZIERT, statisch begrenzt:** Loaderantwort bei Mismatch. Laufzeitwirkung und Beziehung zu Runtime-/Anwendungsfehlern **OFFEN**. | Kein ADI-Fehlercode, Rückgabevertrag oder Providerfehlerverhalten folgt daraus. Nur bei späterem Beleg eines gemeinsamen Aufruf-/Fehlerpfads wäre eine Zuordnung neu zu prüfen. |
| lifecycle | E-XE164-003–007, 009–011, 014–018, 019–066; evidence/index.md:7–23, 24–71 | Boot-/Startkontext ist durch statische Übergabe- und Startsequenzfragmente plausibel, aber Transfer, Ausführung und Ende sind nicht dynamisch verbunden (**HYPOTHESE/OFFEN**). Viele akzeptierte Fenster enden mit `RETS`/`RETI`; das ist kein Komponenten-Lifecycle-Beleg. | **Möglich** für Reset/Start/Interrupt-/Fehlerzustand, ohne Nachweis von Initialisierung, Wiederanlauf, Stop, Retain oder Callbacklebensdauer im Originalstack. | Keine ADI-Init-/Shutdown-/Callback- oder Ressourcenregel ableitbar. Lifecycle-Vertrag bleibt nach next-originalstack-block.md:67 offen und muss am tatsächlichen Consumer/Provider-Pfad belegt werden. |

### Aussage zu E-XE164-019..066

Diese IDs belegen jeweils begrenzte statische Fenster, direkte Callsite-Beobachtungen, Rückkehrterminals oder eng abgegrenzte strukturelle Beziehungen. Sie weisen im akzeptierten Index keine Funktionen als ADI-Provideraufrufe, Runtime-I/O-Callbacks, Diagnosevertrag oder K-Bus-Consumer aus. Die Selbstbeschränkungen der Befunde lassen Zweck, vollständige Xrefs, ABI, DPP/SFR-Bedeutung und Runtimeverhalten ausdrücklich offen. Diese Befunde sind deshalb **nicht als zusätzlicher ADI-Vertrag verwertbar**, aber auch **kein Beweis funktionaler Irrelevanz**.

E-XE164-001 bindet FW30-Artefaktidentität, E-XE164-002 die geprüfte Toolroute; beide sind keine Firmware-Funktionsverträge. E-XE164-005, -008, -011 und -015 enthalten ausdrücklich Hypothesen/offene Verknüpfungen, die nicht zu verifizierter Laufzeitsemantik hochgestuft werden.

## Beobachtungen und verwendete Fundstellen

- Evidence index, kanonische IDs E-XE164-001..066: `PRIVATE_ANALYSIS_ROOT/evidence/index.md`. Die Einträge benennen Artefakt-/Decodergrenzen und für fast alle C166-Fenster offene ABI-, Operand-, SFR-, Laufzeit- oder Zweckfragen.
- Architektur: `docs/adr-0001.md:17,21,25,29,37,43–47,71–75`; `docs/next-originalstack-block.md:65–69,78–87`.
- Vorgegebene Prüfsummen/Größen sämtlicher sieben Eingaben stimmen exakt; Details in `sha256sums.txt`.
- Exakte Composite-Bytes wurden nicht gelesen oder dekodiert; nur Dateigröße und SHA-256 wurden kontrolliert.

## Status, Alternativerklärung und Restunsicherheit

- **HYPOTHESE — Gesamtaussage:** Kein zusätzlicher ADI-Vertrag ist aus E-XE164-001..066 belegt; die Aussage ist keine Vollständigkeitsbestätigung für ADI und keine Irrelevanzklassifikation der ganzen Firmware.
- **VERIFIZIERT — begrenzte Beobachtungen:** Die akzeptierten statischen Loader-/L2-Transfermechaniken (insbesondere E-XE164-014/-018) sowie die im Index angegebenen begrenzten C166-Fenster und Callsite-/Terminalbeziehungen bestehen innerhalb ihrer Hash- und Scope-Bindungen.
- **OFFEN — Vertragsebene:** ob irgendein solcher Pfad über den Originalconsumer/Runtime aufgerufen wird, ob er parallel zu ADI durch libpackbus, UIO, D-Bus oder Diagnose-/Async-Komponenten verläuft, welche Pfade der angestrebte I/O-Strang benötigt und ob sie die substituierte Grenze berühren.
- **Alternativerklärung:** Die XE164-Firmware kann einen überwiegend autonomen Controller-/Boot-/Buspfad bilden, der für den minimalen ADI-Ersatz irrelevant ist; ebenso kann ein statisch nicht zugeordneter Teil durch parallele Bus-, Status-, Zeit- oder Diagnosepfade für den Zielstrang sichtbar werden. Die vorliegende Evidenz unterscheidet diese Erklärungen nicht.
- **Restunsicherheit:** FW30 ist kein FW31-ABI-Nachweis. Keine Laufzeitbeobachtung, vollständige dynamische Aufrufkette, authentische FW31-XE164-Bindung oder vollständige Zuordnung der Firmwarepfade zur Providergrenze ist Teil dieses Pakets. Daher ist „gesamte XE164-Firmware liegt unterhalb der substituierten Providergrenze“ **OFFEN**, nicht verifiziert.

## Tools, Prüfungen und Self-Review

Offline-Prüfung mit GNU coreutils `stat`/`sha256sum` 9.7, ripgrep 15.2.0 und GNU sed 4.9. Nur Datei-Metadaten, Prüfsummen und Textsuche/-anzeige; keine REA-Ausführung, keine Disassembly, keine Geräte-, Netzwerk- oder VM-Aktion, keine Repositoryänderung.

Prüfstatus: Eingabegrößen/SHA-256 **PASS**. Relevanzmatrix und Fundstellen wurden als Worker-Self-Review erstellt; unabhängiges Review **NOT_RUN**. Tests **NOT_RUN** (keine Softwareänderung und keine Funktionsausführung).

**Worker-Self-Review:** Die Schlussfolgerung unterscheidet „kein zusätzlicher belegter Vertrag“ von „belegt irrelevant“, lässt parallele libpackbus-/UIO-/D-Bus-/Diagnosepfade ausdrücklich offen und verwendet keine FW31-Gleichsetzung. Keine neuen Firmwarefunktionen, APIs, Registersemantiken oder Strukturen wurden erschlossen.

## Erzeugte Dateien

- `report.md` — SHA-256 in `sha256sums.txt`.
- `relevance-matrix.tsv` — maschinenlesbare Kurzmatrix; SHA-256 in `sha256sums.txt`.
- `inputs.tsv` — geprüfte Eingabegrößen und SHA-256; SHA-256 der Datei in `sha256sums.txt`.
- `sha256sums.txt` — sha256sum-kompatibles Manifest der drei übrigen erzeugten Dateien.
