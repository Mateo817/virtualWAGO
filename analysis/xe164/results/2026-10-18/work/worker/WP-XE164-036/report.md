> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-036 — E03634 bis E0369B: bounded control-flow structure

## Ergebnis

**VERIFIZIERT, statische Werkzeugbeobachtung:** Im gebundenen Bereich `[0x3634,0x369C)` wurden 29 aneinander anschließende C166-Instruktionen decodiert. Die einzige explizite Kontrollflussstruktur darin sind zehn direkte `calls`, deren von Rizin ausgegebene Fortsetzungen jeweils bei der folgenden Instruktion liegen, sowie `rets` an `E0369A`. Es gibt in diesem linearen Dekodierfenster keinen bedingten oder unbedingten Sprung. Die Fortsetzungen nach Calls setzen Rückkehr der jeweiligen, hier nicht untersuchten Ziele voraus; dies ist keine Aussage, dass jedes Ziel tatsächlich zurückkehrt.

Der separat angefragte Caller-Befund ist eine einzelne Instruktion: `E036A8: calls 0xe03634`, Bytes `dae03436`. Damit ist der direkte Aufrufszieloperand mit `E03634` vereinbar. Es wurde kein weiterer Caller-Code geöffnet.

## Umfang und Eingabe

- Composite: `derived/composites/XE164-composite-e00000.bin`, 17,110 Bytes.
- SHA-256: `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Callee-Fenster: Dateioffsets `[0x3634,0x369C)` (dezimal `13876..13979`), auf der syntaktischen Composite-Abbildung `E03634..E0369B`.
- Isolierter Caller-Punkt: Dateioffset `0x36A8`, Abbildung `E036A8`; genau ein 4-Byte-Aufruf dekodiert.
- Keine Instruktion ab `0x369C` wurde disassembliert. Keine weiteren Caller oder Aufrufziele wurden verfolgt. Die Basisabbildung `E00000` dient nur der Adressbeschriftung.

## Instruktions- und Kontrollflussbefunde

Die vollständige Instruktionstabelle liegt in `instructions.tsv`; direkte Aufrufziele und jeweils von Rizin ausgegebene Fortsetzungen stehen in `calls.tsv`. `flow.tsv` listet die beobachteten Call-Zielkanten, bedingten Call-Return-Fortsetzungen und das terminale Return. Bytes, Offset, Instruktionslänge und Disassembly stammen aus REA-Evidence `ev_a6efd1f87f63dac5e2890d624c6f208d97b6ed4a66607b988ed226e7cb5d16f5`. Dieselbe Observation enthält den vollständigen 104-Byte-Byte-Dump am Callee-Fenster und den einzelnen Caller-Dump/-Decode.

| Kennzahl | Beobachtung |
|---|---:|
| Bereich | `[0x3634, 0x369C)` = 104 Bytes |
| Instruktionsstarts | 29, lückenlos |
| direkte Calls im Callee-Fenster | 10 |
| bedingte/unkonditionale Sprünge im linearen Fenster | 0 |
| Return | `E0369A`, Bytes `db00` (`rets`) |
| Caller-Instruktion | `E036A8`, Bytes `dae03436`, Ziel `E03634` |

Die `call-return continuation`-Kanten sind bedingt formuliert: der Instruktionsdecoder markiert bei jedem `calls` die nächste Adresse als `fail`/Fortsetzung, sagt aber nichts über Verhalten oder Rückkehr des aufgerufenen Codes. Es gibt keinen aus diesem Fenster gewonnenen CFG-Nachweis über die Bodies der Aufrufziele.

## Tool, Status und Alternative

1. REA `open_binary` wurde zuerst mit dem exakten Composite-Pfad versucht. Es scheiterte mit `unsupported binary format` für das headerlose C166-Raw-Image; REA bietet in der geprüften Raw-Binary-Aufnahme keine C166-Auswahl. Dafür wurde kein x86/anderes ISA-Profil erfunden.
2. Dokumentierter Offline-Fallback: REA `execute_rizin_command`, Provider Rizin, explizite Einstellungen `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, `io.va=false`. Eine einzelne zusammengefasste Observation führte `pdj 29 @ 0x3634`, `p8 0x68 @ 0x3634`, `pdj 1 @ 0x36a8`, `p8 4 @ 0x36a8` aus. Evidence-ID: `ev_a6efd1f87f63dac5e2890d624c6f208d97b6ed4a66607b988ed226e7cb5d16f5`.
3. Rizin-Version wurde lokal separat mit `rizin -v` ermittelt: `0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. REA selber meldet den Provider-Versionswert als `null`.

Ein kanonischer Sessionexport wurde temporär als Auditbasis erzeugt (33 Records auf diesem Composite-Hash). Daraus enthält `evidence/rea-evidence-bundle.json` nur die zwei finding-tragenden Records `ev_a6efd1f87f63dac5e2890d624c6f208d97b6ed4a66607b988ed226e7cb5d16f5` (vollständige Bereichs- und Caller-Observation) und `ev_3f955c2de2ce6efa33219436914ce4fbed9f096f4c76d5502ededbd77a2e0b44` (alternative Einzeladress-Operanddarstellung). Andere Sessionrecords wurden aus dem Teilbundle ausgeschlossen; der temporäre Vollsessionexport wurde nach der Filterung entfernt. REA `import_evidence_bundle` akzeptierte das Teilbundle zur kanonischen Prüfung (`imported=0`, da dieselben IDs bereits im Sitzungskatalog vorhanden waren; `total=33`, `unknowns_added=0`).

Status: **VERIFIZIERT** nur für die gebundenen Bytes, lineare Decodergebnisse und die direkte Call-Zielkodierung. Keine Laufzeit-, Geräte-, SFR-, API-, ABI- oder semantischen Aussagen.

## Alternative Disassemblydarstellung

Einzelne `pdj 1 @ address`-Aufrufe ergaben für `E0363E` den Text `mov 0xfe00:0x0a0c, r12`, während die zusammenhängende `pdj 29`-Darstellung im obigen kanonischen Befund `mov 0x00204a0c, r12` ausgab (Einzelrecord `ev_3f955c2de2ce6efa33219436914ce4fbed9f096f4c76d5502ededbd77a2e0b44`). Die Bytes und Länge stimmen überein. Wegen dieser kontextabhängigen Operanddarstellung wird keine Speicher- oder SFR-Bedeutung daraus abgeleitet; der Kontrollflussbefund hängt nicht davon ab.

## Restunsicherheit

- Das lineare Fenster zeigt keine direkten Branches; indirekter Kontrollfluss oder ein anderer Einstiegspunkt ist damit nicht ausgeschlossen.
- Die zehn direkten Call-Ziele und ihre Rückkehrbedingungen sind out of scope und ungeprüft.
- C166-Disassembly ist werkzeugabgeleitet, kein Originalquelltext. Rizin-Evidence dokumentiert, dass Plugins oder Konfiguration externe Dateien/Netzwerkzugriffe grundsätzlich nicht an den Digest bindet; dieser Auftrag selbst verwendete ausschließlich lokalen Artefaktpfad und führte keine Geräte-, Netz- oder VM-Aktion aus.
- Rizin's vom Provider gelieferter Versionswert ist unbekannt; die lokale CLI-Version ist separat belegt.

## Validierung

`python3 validate.py` prüft Composite-Größe und SHA-256, exakte Instruktionsabdeckung von `[0x3634,0x369C)`, alle tabellierten Bytes, den Call-Return-Zielpunkt, den einzelnen Caller-Call, die finding-only Evidence-Menge und SHA256SUMS. Dies ist eine Analysten-Selbstprüfung, keine unabhängige Prüfung.

- `python3 validate.py`: **PASS**.
- `sha256sum -c SHA256SUMS`: **PASS** für alle sechs gelisteten Dateien.
- Statusvokabular: `VERIFIZIERT | HYPOTHESE | OFFEN | BLOCKED`; Testvokabular: `PASS | FAIL | NOT_RUN | BLOCKED`.
