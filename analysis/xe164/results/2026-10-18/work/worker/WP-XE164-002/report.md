> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-002 — statische Analyse bei 0xE00F18

## Ergebnis

**VERIFIZIERT (innerhalb des unten beschriebenen Ghidra-Replays):** Ghidra bildet bei Analyseadresse `0xE00F18` die Funktion `FUN_e00f18` mit genau einem zusammenhängenden Function-Body-Bereich `0xE00F18–0xE00F37` (inklusive) ab. Das sind 32 adressierte Bytes und 10 dekodierte Instruktionen. Der Funktionskörper ruft fünf direkte Ziele auf, enthält einen Datenzugriff auf `0x00FF10`, und hat eine eingehende direkte Call-Referenz bei `0xE03A8C` aus `startup_candidate` (`0xE0387A`).

Die fünf unmittelbaren Callees wurden jeweils nur bis zu ihrer eigenen Body-Grenze, ihren unmittelbaren Call-Kanten und ihren Datenreferenzen zusammengefasst. Es gibt keine Rekursion in Ziele dieser Callees. Der Bericht vergibt keine Hardware-, K-Bus- oder SFR-Rollenbezeichnungen.

## Eingabeidentität und Koordinaten

Die Eingaben wurden erneut gehasht:

| Eingabe | Größe | SHA-256 | Status |
|---|---:|---|---|
| `derived/composites/XE164-composite-e00000.bin` | 17,110 Byte | `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` | VERIFIZIERT |
| `work/ghidra/composite-replay.md` | 2,169 Byte | `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5` | VERIFIZIERT |
| `work/ghidra/scripts/Xe164Probe.java` | 4,315 Byte | `9289f41396180a3478ce3e64e70f54d38a397e5f4f7247b89bd8e8bf2808490f` | VERIFIZIERT |

Koordinaten bleiben getrennt: Die Zieladresse in der Frage ist die Analyseadresse `0xE00F18`. Das Replay konfiguriert `BinaryLoader` mit Basis `0xE00000`; unter genau dieser linearen Replay-Zuordnung entspricht die Zielstelle dem Dateioffset `0xF18` (`0xE00F18 - 0xE00000`). `0xF18` ist eine abgeleitete Dateikoordinate, keine zweite Analyseadresse. Die Mappingkonfiguration ist im gebundenen Replay dokumentiert und wurde in der Replay-Ausgabe erneut als angewandte Basis bestätigt.

## Verfahren und Konfiguration

1. REA-Sitzungsinventar und gespeicherte Evidence wurden zuerst geprüft. Für den Eingabehash gab es zuvor keine gespeicherten Records. Danach wurde ein fokussierter `REA execute_rizin_command`-Versuch auf dem lokalen Composite mit `e asm.arch=c166; e asm.bits=16; e io.va=true; s 0xE00F18; pd 256` ausgeführt. Dieser lieferte wiederholtes `bset r15.15` und `Failed to read chunk of size 0x101 at 0xe00f18 from io`; diese Ausgabe ist **nicht** Grundlage der Funktions- oder Kantenbefunde. REA-Version: `rea-agents 6.5.0`; der Rizin-Versionswert war nicht zuverlässig verfügbar.
2. Der ausdrücklich zugelassene direkte Ghidra-C166-Fallback verwendete Ghidra `12.1.4`, Java `21.0.12.1`, Sprache `C166:LE:16:default`, Compiler Spec `tasking`, `BinaryLoader`, Basis `0xE00000`, `-analysisTimeoutPerFile 45`, `-max-cpu 1`, `-readOnly`, `-deleteProject`. Das Programm wurde in einem temporären Projekt unter `/tmp` importiert; die aufbewahrten Protokolle und der angepasste Probe-Skriptstand liegen in diesem exklusiven WP-Ordner. Der Replayprozess lief mit `unshare -Un --map-current-user`; es wurden keine Netzwerk-, Geräte-, VM- oder Zielaktionen vorgenommen.
3. Der Probeablauf übernimmt die im Replaydokument beschriebenen Seed- und Analyseentscheidungen: Seeds bei `E00000`, `E00020`, `E00200`, danach Reset-Kandidat bei `E00400`; anschließend `analyzeChanges`, Markierung der vorhandenen Funktion bei `E03A96` als no-return, Startup-Kandidat bei `E0387A`, dann erneut `analyzeChanges`. Der angepasste `Xe164FunctionProbe.java` liest danach Ghidra-FunctionManager, Listing und ReferenceManager. Keine Programmbytes wurden geschrieben.

Die Rizin-Evidence-ID lautet `ev_55c75f88b7df178b1c31d339bf4e6011dc2d7018b48865a39a2868675b488f97`. Der vollständige aktuelle REA-Bundle-Export liegt als `rea-evidence-bundle.json` vor und enthält genau diesen einen Record; er dokumentiert die verworfene Rizin-Ausgabe, nicht die separate direkte Ghidra-Ausführung. Der Bundle-Export ist in `SHA256SUMS` gehasht.

## Beobachtungen

Ghidras Replayausgabe nennt `e00f18` als Funktionsentry und bestätigt, dass die angefragte Adresse im Body liegt. Der Body ist ein einzelner inklusiver Range `e00f18–e00f37`, `bodyBytes=32`; Ghidra listet darin 10 Instruktionen. Der genaue dekodierte Ablauf steht im finalen Probe-Log. Die wichtigsten Kanten mit Quellinstruktionen stehen in [edges.csv](edges.csv); Datenreferenzen samt Operandindex und Listingtext stehen in [references.csv](references.csv).

| Befund | Konkrete Ghidra-Fundstelle | Status |
|---|---|---|
| Funktionseintritt und exakte konfigurierte Grenze | `0xE00F18`, Body-Range inkl. `0xE00F37`, 32 Bytes | VERIFIZIERT |
| Eingehender direkter Caller | Instruktion `0xE03A8C: calls 0xe00f18`, Quelle in `startup_candidate` bei `0xE0387A` | VERIFIZIERT |
| Direkte Callees des Zielkörpers | `0xE00F18 → 0xE004CA`; `0xE00F24 → 0xE00634`; `0xE00F28 → 0xE00BEE`; `0xE00F2C → 0xE03586`; `0xE00F32 → 0xE0369C` | VERIFIZIERT |
| Direkte Datenreferenz im Zielkörper | `0xE00F30: bset 0xff10.0xb`, Referenzart `READ_WRITE`, Operand 0, Ziel `0x00FF10` | VERIFIZIERT |
| Unaufgelöste berechnete Calls/Jumps im Ziel und in den fünf Callees | Probe durchlief alle Instruktionen jedes dieser sechs Bodies; je Body `unresolvedComputedEdges=0`; keine unaufgelösten direkten Calls | VERIFIZIERT innerhalb dieses Ghidra-Modells |

Die fünf unmittelbaren Callee-Bodies und ihre Instruktionszahlen:

| Callee | Body-Range inklusiv | adressierte Bytes | Instruktionen | unmittelbare Calls im Callee-Body |
|---|---|---:|---:|---|
| `FUN_e004ca` | `0xE004CA–0xE00549` | 128 | 43 | 10 Call-Edges |
| `FUN_e00634` | `0xE00634–0xE006C3` | 144 | 54 | 5 Call-Edges |
| `FUN_e00bee` | `0xE00BEE–0xE00C0F` | 34 | 9 | 2 Call-Edges |
| `FUN_e03586` | `0xE03586–0xE03633` | 174 | 50 | 1 Call-Edge |
| `FUN_e0369c` | `0xE0369C–0xE036B1` | 22 | 10 | 1 Call-Edge |

Die „unmittelbaren Calls im Callee-Body“ sind lediglich die Kanten dieser Callee-Zusammenfassung. Ihre Zieladressen sind in `edges.csv` enthalten; über diese Funktionsziele wird keine Aussage zu Grenzen, Datenzugriffen oder weiteren Nachfahren gemacht.

## Beobachtung, Schlussfolgerung und Alternativen

**Beobachtung:** Ghidra dekodiert am Zielentry fünf direkte Calls, dazwischen zwei Register-Ladevorgänge, einen bitadressierten `bset`-Zugriff auf `0x00FF10`, danach `rets`. Die konkreten Befehle sind bei `0xE00F18`, `0xE00F1C`, `0xE00F20`, `0xE00F22`, `0xE00F24`, `0xE00F28`, `0xE00F2C`, `0xE00F30`, `0xE00F32`, `0xE00F36` im finalen Probe-Log protokolliert.

**Schlussfolgerung — HYPOTHESE:** Innerhalb dieses statischen Funktionsmodells ist `FUN_e00f18` ein kurzer Ablauf, der mehrere direkte Unterprogrammziele nacheinander aufruft und zusätzlich ein Bit an `0x00FF10` setzt. Das belegt keine Bedeutung dieser Adresse, keinen Aufrufvertrag und keine physikalische Wirkung. Die Datenreferenz wird daher ausschließlich numerisch bezeichnet.

**Alternativerklärungen / Restunsicherheit — OFFEN:** `FUN_e00f18`, `FUN_e004ca` usw. sind Ghidra-generierte Defaultnamen. Funktionsgrenzen und Caller hängen am dokumentierten, absichtlich gesetzten Replaykontext; ein anderer Entry-Seed, eine andere C166-Analyse oder abweichende No-return-Annahme kann Ownership und Graph ändern. Leere Ghidra-Ausgaben für unaufgelöste berechnete Kanten beweisen nicht, dass es im Binärprogramm zur Laufzeit keine indirekten Transfers gibt. Die Ausgabe belegt ebenfalls keine vollständigen Datenfluss-, ABI- oder Hardwaresemantiken. Eine Adresse oder ein Listingtext allein rechtfertigt keine Register-, SFR-, K-Bus- oder Gerätezuschreibung.

## Umfang und Status

- **VERIFIZIERT:** Eingabehashes/-größe, Replayparameter, Ghidra-Funktionsentry/Range, eine direkte eingehende Call-Referenz, fünf direkte Calls aus dem Zielkörper, Datenreferenz `0x00FF10`, unmittelbare Body-Zusammenfassungen der fünf Callees und deren in-scope Calls/Datenreferenzen.
- **HYPOTHESE:** beschreibende Aussage, dass der Zielkörper ein kurzer sequenzieller Unterprogrammablauf mit zusätzlichem Bitzugriff ist.
- **OFFEN:** semantische Bedeutung der Adressen und Instruktionen; Vollständigkeit indirekter Transferziele außerhalb der von Ghidra aufgelösten Referenzen; Stabilität der Grenze unter anderer Analyse-/Seed-Konfiguration.
- **BLOCKED:** keiner für den vorgegebenen statischen Umfang.

Es wurde kein unabhängiger Review- oder Worker-Lauf behauptet. `REA execute_rizin_command` war **kein PASS** und wurde entsprechend nicht zur Schlussfolgerung hochgestuft.

## Erzeugte Artefakte

`edges.csv`, `references.csv`, dieses `report.md`, angepasster Probe `Xe164FunctionProbe.java`, finaler Ghidra-Lauf (`final-headless.stdout`, `final-headless.stderr`, `final-ghidra.log`, `final-script.log`), REA-Ausgabeexport `rea-evidence-bundle.json`, sowie die früheren Probeprotokolle `headless.stdout`, `headless.stderr`, `ghidra.log`, `script.log`. Die früheren Protokolle zeigen einen zunächst nicht erfolgreichen Skriptkompilierlauf und einen ersten Lauf ohne Replay-Seeds; sie sind Diagnoseverlauf und keine Ergebnisgrundlage. Der fehlgeschlagene fokussierte Rizin-Aufruf ist vollständig im REA-Bundle enthalten. `SHA256SUMS` enthält die SHA-256-Werte aller abgegebenen Dateien außer sich selbst; der Manifesthash wird separat beim Handoff ausgewiesen.
