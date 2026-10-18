> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-077 — FW31 `libIoDrvDal.so.1.0.2`

## Befund

**VERIFIZIERT:** Eingangshash PASS: SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`, 25,976 Bytes. `ComponentEntry` (Ghidra `0x14448..0x14623`; ELF-VA/File-Offset `0x4448..0x4623`) publiziert sechs Funktionszeiger in einem Ausgabedatensatz. Daraus allein folgt keine Aufrufreihenfolge: Caller von `ComponentEntry` und Reihenfolge des extern konsumierten Datensatzes sind statisch nicht beobachtet.

**VERIFIZIERT:** Der publizierte Callback `FUN_00011704` ruft über einen aus dem Caller übernommenen Funktionszeiger höchstens zwei Tabellen nacheinander auf. Der zweite Call erfolgt nur, wenn der erste Status Null ist. **OFFEN:** Der Host-Slotname und ob dieser Pfad Start oder Stop repräsentiert. Eine Shutdown-/Deregistrierungsreihenfolge ist im hier abgegrenzten Graph nicht belegt.

## Identität, Werkzeuge, Adressdomänen

REA-first: `open_binary`, `binary_overview`, `analyze_function`, procedure/reference/Xref- und Instruktionsabfragen. REA: Ghidra 12.1.4, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; Überblick-Workflow `rea-workflow` v1. Da REA vier publizierte Callback-Adressen nicht als Prozeduren auflösen konnte, wurde read-only als benannter Fallback `arm-linux-gnueabihf-objdump`/`arm-linux-gnueabihf-readelf`, GNU Binutils 2.44, benutzt. Kein Target wurde ausgeführt.

Ghidra Image Base ist `0x10000`: Ghidra-Adresse = ELF-VA + `0x10000`. In `.text` ist ELF-VA = File-Offset. In `.data.rel.ro` ist ELF-VA = File-Offset + `0x10000`; BSS besitzt keinen File-Offset. Codebereiche unten sind inklusiv.

## Beobachtungen

- `ComponentEntry` schreibt ID `0x10062001` nach `param_1+0`, danach Callbackwerte: `+4=0x11704`, `+8=0x10b58`, `+12=0x11570`, `+16=0x133b4`, `+20=0x1157c`, `+24=0x1362c`. Store-Callsites: Ghidra `0x14490`, `0x14498`, `0x144cc..0x144e0`; ELF/File `0x4490`, `0x4498`, `0x44cc..0x44e0`. Das belegt Zeigerpublikation, keine dynamische Ausführung.
- Bei Ghidra `0x145a4` (ELF/File `0x45a4`) wird der importierte `adi_GetApplicationInterface`-PLT-Thunks `0x109d4` (ELF/File `0x09d4`) aufgerufen. Sein Rückgabewert wird ungeprüft als memcpy-Quelle für 0x88 Bytes bei `0x145bc` verwendet. Einzelne globale Tabellenfelder werden danach überschrieben. Kein Null-/Statuszweig ist vorhanden; ein ABI der ganzen Tabelle folgt daraus nicht.
- Zusätzlich ruft `ComponentEntry` bedingt den Caller-Zeiger aus `param_1+0x28` bei Ghidra `0x1452c` (ELF/File `0x452c`) mit Argument `0x10062001` auf. Guard: `0x14518..0x14524`. Der Rückgabewert wird ignoriert. Kein Name/Vertrag ist gebunden; dies ist ein Call in `ComponentEntry`, kein nachgewiesener späterer Lifecycle-Aufruf.
- `ComponentEntry` setzt BSS-Zelle `DAT_0002618c` aus Input `+0x1c` (Ghidra `0x144e8..0x144ec`, ELF/File `0x44e8..0x44ec`). Für den Zeiger ist kein API-Name gebunden. `FUN_00011704` (Ghidra `0x11704..0x1176b`, ELF/File `0x1704..0x176b`) liest und ruft genau diese Zelle auf:
  - Null: Rückgabe `3`, kein Call (Branch `0x11714..0x11718`).
  - Nichtnull: erster Call bei Ghidra `0x11734` (ELF/File `0x1734`), Argumente beobachtet als `r0=&DAT_00025e28, r1=0, r2=1, r3=0x10062001`. Nichtnullstatus wird unverändert zurückgegeben; nur Null erreicht Call zwei (`0x11738..0x11748`).
  - Call zwei bei Ghidra `0x1175c` (ELF/File `0x175c`) über denselben Zeiger, `r0=&PTR_Dal_DiagnoseGetDeviceState_00025e4c, r1=0, r2=0, r3=0x10062001`; Ergebnis direkt zurück (`0x11760`).
  - Tabellen: Ghidra `0x25e28` = ELF-VA `0x15e28`, File `0x5e28`; Ghidra `0x25e4c` = ELF-VA `0x15e4c`, File `0x5e4c`. `readelf -rW` belegt für den zweiten Tabellenanfang `R_ARM_ABS32` auf `Dal_DiagnoseGetDeviceState` (ELF/File `0x2d20`). Tabellenprotokoll und Start-/Stop-Zuordnung bleiben offen.
- `ComponentEntry` setzt BSS-Zelle `DAT_00026090` aus Input `+0x34` (Ghidra `0x14500..0x14504`, ELF/File `0x4500..0x4504`). Der publizierte Callback `FUN_00010b58` (Ghidra `0x10b58..0x1145f`, ELF/File `0x0b58..0x145f`) nutzt sie als Symbolauflöser. Kein Nullcheck beobachtet. Erste Aufrufe für Stringnamen `LogAdd` und `CMUtlMemCpy` verzweigen ihre Rückgaben nicht. Ab `CMUtlSafeStrCpy` setzt nur Null die Kette fort; erster Nichtnullstatus wird zurückgegeben. Die aufgelistete geordnete Folge endet mit `TscExtTaskPostExternalEvent`. Dies belegt fail-fast Symbolauflösung, kein Rollback und keinen Shutdownpfad.

  Jede Statuskante dieser Resolverfolge ist einzeln in `status-branches.tsv` gebunden: die ersten zwei Calls haben keinen Statusbranch; alle Zwischen-Calls haben jeweils ein `BNE` bei Callsite +8 zum gemeinsamen Return bei Ghidra `0x11454`; der letzte Call bei `0x1144c` wird direkt zurückgegeben. ELF-VA/File-Offset stehen je Zeile daneben.
- Ziele `0x11570`, `0x1157c`, `0x133b4`, `0x1362c` sind publiziert, aber REA meldet `not in procedure` für die exakten Zieladressen. Objdump dekodiert einzelne Instruktionen. Ohne stabile Grenze/Caller-Bedeutung wird keines als Startup/Shutdown eingestuft. `0x1362c` wurde nicht verfolgt (Zyklus-/Gerätepfad ausgeschlossen).

## Schlussfolgerung, Alternativerklärung, Unsicherheit

**VERIFIZIERT:** In `FUN_00011704` lautet die belegte Reihenfolge Nullcheck → Tabellenargument `0x25e28` → bei Nullstatus Tabellenargument `0x25e4c` → Rückgabe. Bei erstem Nichtnull wird dieser Status durchgereicht. In `FUN_00010b58` werden die ersten zwei Resolverstatus ignoriert; anschließend wird beim ersten Nichtnull abgebrochen und dieser Status zurückgegeben.

**HYPOTHESE:** `FUN_00011704` kann eine allgemeine Zweitabellenregistrierung sein; die zwei Tabellen müssen keine getrennten Start-/Stop-Phasen kodieren. Die Binärdatei allein liefert diese Klassifikation nicht. Diese Alternativerklärung begrenzt die Lifecycle-Deutung der beobachteten Reihenfolge.

**OFFEN:** Hostseitige Aufrufreihenfolge/-zeitpunkt/-anzahl, Bedeutung der nicht klassifizierten Callbackfelder, Name und ABI der caller-supplied Slots `DAT_0002618c` und `DAT_00026090`, sowie jegliche Shutdownordnung außerhalb dieses Graph-Scope. Fehlende Kante in diesem Bericht bedeutet nicht globale Abwesenheit.

Tests/Status: Eingangshash PASS; statische Offlinebeobachtung PASS; Runtime NOT_RUN; Host-Ordnung NOT_RUN; Shutdown OFFEN; unabhängiger Review NOT_RUN. Pseudocode ist Ghidra-Werkzeugableitung; Callsite- und Branchangaben zusätzlich mit REA-Assembly/Instruktionen abgeglichen.

## Evidence

Kanonisches vollständiges Bundle: `rea-evidence-bundle.json`. Die Evidence-ID-Liste für das gesamte exportierte Bundle steht in `evidence-ids.txt`. Der Report referenziert nur IDs aus diesem Bundle.

`manifest.tsv` erfasst alle übrigen Paketdateien und das Eingabe-Artefakt; die Manifestdatei selbst ist wegen des selbstreferenziellen Hashes ausgenommen.
