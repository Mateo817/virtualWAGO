> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-073 — original `Push` handler contract

## Ergebnis

**VERIFIZIERT (statische ELF-Analyse):** Der `Push`-Deskriptor hat laut hashgebundenem Forschungsstand null Varargs. Der exportierte Handler `int libpackbus_Push(void)` liegt bei ELF-VA `0x10130`, Dateioffset `0x10130`, Dynsym-Größe 424 Byte. Ghidra/REA analysiert ihn bei `0x20130`; diese Provider-Adresse liegt bei den untersuchten Codeadressen um `0x10000` über der verlinkten ELF-VA. Der `.plt`-Eintrag liegt bei ELF-VA `0x80f4` (Ghidra/REA `0x180f4`, Dateioffset `0x80f4`) und leitet über den GOT/JUMP_SLOT an den Export. Der Handler führt eine überwachte Austauschiteration aus. Er gibt `0` zurück, wenn der ausgewählte Austausch-/Reaktionshelper `0` liefert; bei einem Nichtnullresultat dieses Helpers normalisiert er auf `-1`. Ebenso endet er mit `-1`, wenn die globale Steuerreferenz fehlt, der Pointerwert bei `base+0xe0` null ist oder der Pointerwert bei `base+0x00` null ist. Diese Bedingungen sind Beobachtungen der dekompilierten Kontrollflüsse, keine Aussagen über Namen oder Layout eines C-Structs.

**VERIFIZIERT:** Im normalen Zweig ruft `Push` `SCPU_DataExchange(*G)` auf und bildet dessen Ergebnis auf `0` beziehungsweise `-1` ab. Im Watchdog-Reaktionszweig ruft es `SCPU_EvaluateWatchdogErrorReaction(*G, 10000)` auf und bestätigt danach die Reaktion; dessen Ergebnis wird auf dieselbe Weise normalisiert. Die eine erlaubte zusätzliche Call-Ebene zeigt für den gültigen Parameterpfad der untersuchten `SCPU_EvaluateWatchdogErrorReaction`-Implementierung einen Rückgabewert `0`; folglich erreicht `Push` auf diesem statisch gezeigten Pfad den Return `0`. Laufzeitverhalten wurde nicht ausgeführt.

**VERIFIZIERT:** Die direkten auflösbaren Caller des `.plt`-Stubs sind `libpackbus_TestApplicationStateChange` und `KBUS_dbus_thread`. Der Stub ist der einzige auflösbare direkte Codecaller des Exportkörpers. Die Relocation `R_ARM_JUMP_SLOT` am GOT-Eintrag ELF-VA `0x33454` (Ghidra/REA `0x43454`, Datei `0x23454`) bindet den Dynsym `libpackbus_Push` mit ELF-VA `0x10130`.

## Kontrollfluss und Zustand

Ghidra-Pseudocode und ARM-Disassemblierung zeigen folgenden Pfad:

1. `clock_gettime(1, &local_timespec)` wird aufgerufen. Bei einem Nichtnullresultat werden nur die lokale Zeitsekunden- und Nanosekundenfelder auf null gesetzt; der Austausch-Rückgabewert wird davon nicht direkt bestimmt.
2. `DAT_00054420` muss ungleich null sein und der gelesene Pointerwert bei `base+0xe0` ebenfalls. Andernfalls wird `-1` zurückgegeben.
3. Falls das Byte bei `base+0x78` ungleich null ist, ruft der Handler `MISC_threads_acquire_lock(base+0x7c)` und anschließend `pthread_mutex_unlock` für dieselbe berechnete Adresse auf. Die Rückgabe beider Lockoperationen wird im Handler nicht ausgewertet.
4. Der Handler nimmt einen Read-Lock an `base+0x10`, startet den DM-Observer mit dem Pointerwert bei `base+0xe0` und der lokalen Zeit, nimmt einen weiteren Mutex an `base+0x60` und startet Timer `3`.
5. Der gelesene Pointerwert bei `base+0x00` entscheidet über den Austauschpfad. Ist er null, werden Timer, Mutex, Observer und Read-Lock beendet/freigegeben und der Handler liefert `-1`.
6. Ist dieser Wert ungleich null, folgen `CallHook()` (Hook vor Push), `lpkb_CheckWatchdogTimeout` und `lpkb_GetWatchdogErrorReactionRequest`, jeweils mit dem gelesenen Pointerwert bei `base+0xdc` für Watchdog-Aufrufe. Bei Anforderungsbyte null erfolgt `SCPU_DataExchange(*(base+0x00))`. Andernfalls erfolgt `SCPU_EvaluateWatchdogErrorReaction(*(base+0x00), 10000)` und danach `lpkb_ConfirmWatchdogErrorReactionRequest`.
7. Danach folgt `CallHook(1)` (Hook nach Push), Timerstopp, Mutex-Unlock, Observerstopp und Read-Unlock. Der Rückgabewert des ausgewählten SCPU-Aufrufs wird zu `0` normalisiert, falls er null ist, sonst zu `-1`.

Der Handler selbst schreibt laut beobachtetem Pseudocode keinen globalen Wert direkt. Er schreibt lokale Stackwerte und übergibt Zustandsadressen/-werte an Helper. Auf der zusätzlich untersuchten Ebene ruft `libpackbus_CallHook` `PTP_pre_push` beziehungsweise `PTP_post_push` auf. `MISC_threads_acquire_lock` ruft `pthread_mutex_lock` auf und ruft nur beim beobachteten Resultat `0x82` zusätzlich `pthread_mutex_consistent` auf. Die internen Nebenwirkungen weiterer Helper und deren Laufzeitresultate sind außerhalb der hier belegten Grenze.

## Fundstellen und direkte Funktionen

Koordinaten werden getrennt angegeben: ELF-VA aus ELF-Header/Dynsym/Relocation; Ghidra/REA-Analyseadresse aus REA; Datei-Offset aus REA Source-Byte-Mapping beziehungsweise PT_LOAD. Der erste PT_LOAD hat `p_offset=0`, `p_vaddr=0`; der zweite hat `p_offset=0x22aa8`, `p_vaddr=0x32aa8`. Für alle hier gemappten Stellen liegt die Ghidra/REA-Analyseadresse `0x10000` über der ELF-VA. Der exportierte Push-Dynsym umfasst 424 Bytes `[0x10130,0x102d8)`. Der Ghidra-Instruktionskörper umfasst 412 Bytes und endet inklusive bei ELF-VA `0x102cb`; die folgenden 12 Bytes `[0x102cc,0x102d8)` sind die drei durch Handler-Instruktionen referenzierten Literalwörter (`bc42030084420300fc410300` am Ghidra-Ort `0x202cc`). Ghidra-Adressen des Körpers lauten `0x20130–0x202cb`.

| ELF-VA / Ghidra-Analyseadresse / Dateioffset | Beobachtung |
|---|---|
| `0x10130` / `0x20130` / `0x10130` | Exportierter `libpackbus_Push`, Dynsym 424 Bytes; Ghidra-Instruktionskörper 412 Bytes, 14 Basic Blocks |
| `0x80f4` / `0x180f4` / `0x80f4` | `.plt`-Eintrag `libpackbus_Push@plt`, 12 Bytes, Zielsymbol `0x10130` |
| `0x80fc` / `0x180fc` / `0x80fc` | Indirekter PLT-Transfer über den GOT/JUMP_SLOT-Eintrag, der auf den Push-Export bindet; kein direkter Code-Call zum Körper |
| `0x10e54` / `0x20e54` / `0x10e54` | Entry `libpackbus_TestApplicationStateChange`; Ghidra-Body 356 Bytes; callt PLT bei ELF-VA `0x10f44` |
| `0x10f44` / `0x20f44` / `0x10f44` | Call aus `libpackbus_TestApplicationStateChange` zum PLT-Stub |
| `0x17f58` / `0x27f58` / `0x17f58` | Entry `KBUS_dbus_thread`; Ghidra-Body 648 Bytes; callt PLT bei ELF-VA `0x1807c` |
| `0x1807c` / `0x2807c` / `0x1807c` | Call aus `KBUS_dbus_thread` zum PLT-Stub |
| `0x33454` / `0x43454` / `0x23454` | GOT-Eintrag mit `R_ARM_JUMP_SLOT`-Relocation für `libpackbus_Push` |

Direkte Aufrufziele des Handler-Bodys laut Ghidra-Callreferenzen und ARM-Instruktionen. Codecallsite und Ziele im ersten LOAD-Segment haben denselben ELF-VA und Datei-Offset; Ghidra-Adressen stehen in Klammern. Provider-Thunkziel-Adressen sind Ghidra-interne Beobachtungen und werden nicht als ELF-Adressen dieses Binarys ausgegeben.

| Callsite ELF-VA/Datei (Ghidra) | Ziel ELF-VA/Datei (Ghidra) / beobachteter Name |
|---|---|
| `0x10144` / `0x10144` (`0x20144`) | `0x7614` / `0x7614` (`0x17614`) — `<EXTERNAL>::clock_gettime` |
| `0x1018c` / `0x1018c` (`0x2018c`) | `0x79f8` / `0x79f8` (`0x179f8`) — `<EXTERNAL>::pthread_rwlock_rdlock` |
| `0x101a0` / `0x101a0` (`0x201a0`) | `0x8250` / `0x8250` (`0x18250`) — Stub `lpkb_ObserverStart_DM`; implementation ELF-VA `0x153d0` (Ghidra `0x253d0`) |
| `0x101ac`, `0x10280` / `0x101ac`, `0x10280` (`0x201ac`, `0x20280`) | `0x7650` / `0x7650` (`0x17650`) — Stub `MISC_threads_acquire_lock`; implementation ELF-VA `0x8624` (Ghidra `0x18624`) |
| `0x101b4` / `0x101b4` (`0x201b4`) | `0x7df4` / `0x7df4` (`0x17df4`) — Stub `MISC_start_timer`; implementation ELF-VA `0x12a78` (Ghidra `0x22a78`) |
| `0x101d0`, `0x10214` / `0x101d0`, `0x10214` (`0x201d0`, `0x20214`) | `0x7b60` / `0x7b60` (`0x17b60`) — `libpackbus_CallHook`; internes Ziel ELF-VA `0x10118` (Ghidra `0x20118`) |
| `0x101dc` / `0x101dc` (`0x201dc`) | `0x7fd4` / `0x7fd4` (`0x17fd4`) — Stub `lpkb_CheckWatchdogTimeout`; implementation ELF-VA `0x1502c` (Ghidra `0x2502c`) |
| `0x101ec` / `0x101ec` (`0x201ec`) | `0x8184` / `0x8184` (`0x18184`) — Stub `lpkb_GetWatchdogErrorReactionRequest`; implementation ELF-VA `0x1509c` (Ghidra `0x2509c`) |
| `0x10204` / `0x10204` (`0x20204`) | `0x8058` / `0x8058` (`0x18058`) — `SCPU_DataExchange`; internes Ziel ELF-VA `0x8d90` (Ghidra `0x18d90`) |
| `0x1021c`, `0x1029c` / `0x1021c`, `0x1029c` (`0x2021c`, `0x2029c`) | `0x7c2c` / `0x7c2c` (`0x17c2c`) — Stub `MISC_stop_timer`; implementation ELF-VA `0x12aa0` (Ghidra `0x22aa0`) |
| `0x1022c`, `0x1028c`, `0x102a8` / `0x1022c`, `0x1028c`, `0x102a8` (`0x2022c`, `0x2028c`, `0x202a8`) | `0x7a70` / `0x7a70` (`0x17a70`) — `<EXTERNAL>::pthread_mutex_unlock` |
| `0x10238`, `0x102b4` / `0x10238`, `0x102b4` (`0x20238`, `0x202b4`) | `0x7e60` / `0x7e60` (`0x17e60`) — Stub `lpkb_ObserverStop_DM`; implementation ELF-VA `0x15484` (Ghidra `0x25484`) |
| `0x10244`, `0x102c0` / `0x10244`, `0x102c0` (`0x20244`, `0x202c0`) | `0x7d1c` / `0x7d1c` (`0x17d1c`) — `<EXTERNAL>::pthread_rwlock_unlock` |
| `0x10264` / `0x10264` (`0x20264`) | `0x77ac` / `0x77ac` (`0x177ac`) — `SCPU_EvaluateWatchdogErrorReaction`; internes Ziel ELF-VA `0x8b78` (Ghidra `0x18b78`) |
| `0x10274` / `0x10274` (`0x20274`) | `0x7cec` / `0x7cec` (`0x17cec`) — Stub `lpkb_ConfirmWatchdogErrorReactionRequest`; implementation ELF-VA `0x150d4` (Ghidra `0x250d4`) |

Die zusätzlichen Wrapper `libpackbus_CallHook`, `MISC_threads_acquire_lock`, `SCPU_DataExchange` und `SCPU_EvaluateWatchdogErrorReaction` wurden genau eine Call-Ebene tiefer verfolgt, soweit dies Hook-/Lock- beziehungsweise Returnverträge klärt. `libpackbus_CallHook` ruft `PTP_pre_push` und `PTP_post_push`; `MISC_threads_acquire_lock` ruft `pthread_mutex_lock` und vergleicht das Ergebnis mit `0x82`, worauf `pthread_mutex_consistent` folgt. Die SCPU-Ergebnisse sind im Ergebnisabschnitt beschrieben.

## Status, Methoden, Evidence

Statusvokabular: **VERIFIZIERT**, **HYPOTHESE**, **OFFEN**, **BLOCKED**. Die obigen statischen ELF-Befunde sind VERIFIZIERT im Sinn von reproduzierbaren Analysebeobachtungen, nicht im Sinn beobachteter Ausführung.

- Zielidentität/Hash/Größe: VERIFIZIERT; der Zielhash stimmt mit der Vorgabe überein.
- Push-Symbol, Wrapper/Handler-Trennung, Kontrollfluss, direkte Calls und direkte auflösbare Caller: VERIFIZIERT; REA-Evidence `ev_76f8a6a7b51ad40e960143f28464cf468274df6fc700b8cde8b9572358dcded8`, `ev_95323479f0ebb933915bec9f00658d62b9b8813bdc2b5b19ff07890dea15c0ee`, `ev_fae0f3d376aa7fcb7b67800e251398688079415ada94e25434ec9e5188a527f9`, `ev_023c4b52c16da2a3d5f95a2d4fb4e330cc95c9cf988ade79a767a072e42a1d4e`, `ev_b20e1067435402c5530a09a3b03d49198463a0596435bf8e326b1fa272cd3372`, `ev_8e33873e7526143229a58ffa0a2d4a0f6aa3c3c55012a38febe7b420ba6f211f`, `ev_31bc86d8d10d58011e573843c27f395688ad1239c7092720ebcbbd7830038bdb`, `ev_5ca26df2bb0761897b036664bd92403de768ed9ef72ef0423489d23dd8c7e59e`.
- Callerdetails und Wrapperklassifikation: VERIFIZIERT; `ev_2eca8bf9ca8ccbe7937995feb805a1e0f50085a8befcc98f6ee0a73670bb5093`, `ev_d62fcc8460493087e2bf7f3f3b92a33a3a9df69dfd111c2768bf515b267a227d`, `ev_128e225fab27b010806a0330057038c946964aa8387179aea6d58b7233aa6e48`, `ev_b8576884865b8b50d83785fe5f530ee6aa9070215fc02319318caf5c5cfec235`.
- Eine zusätzliche Thin-Wrapper-Ebene für Ergebnis-/Hook-/Lock-Verträge: VERIFIZIERT als Pseudocodebeobachtung; `ev_c528f7d967b240c0f1e72f65f1c58eee54bc9b66ddd2e6ac542703aa0532acbd`, `ev_613931e8b3b41e240a755e1437356c6b4892e96abaea48023bb947e83aeaea08`, `ev_76597a73a56c9ce8a6916790abeddae460db040e3628ea1e45dcf814d8daacb5`, `ev_e4a2bb0f0e8a2e42e89b735d1514f4b962c1b02dffd9af7b4511db26ab093952`.
- VA/Fileoffset-Paare: VERIFIZIERT mit REA-Quellbyte-Mapping; zentrale Mappings `ev_6b5ebfb2119dc0f03ca8e77845e6eaeabbfb86f4fad72efe012265084ee2e982`, `ev_ac63c9bc97ab0d548c944717a51cafa511642aec6851b62f4bfba5e03db31172`; Callsite-Mappings wurden separat durch dieselbe REA-Operation erzeugt und sind im Evidence-Bundle enthalten.
- Null-Argument-Deskriptor: VERIFIZIERT als Inhalt des bereitgestellten `adi-contract`-Dokuments; dessen Zeile 75 bindet den FW31-Deskriptor an `Push` mit null Argumenten. ELF-Dynsym und `R_ARM_JUMP_SLOT` binden den PLT/GOT-Pfad an den Export, belegen aber keine äußere Ergebnispropagation.
- Outer-/Inner-Rückgabe: VERIFIZIERT ist hier nur der Export `libpackbus_Push` bei ELF-VA `0x10130` samt statischem `0/-1` Returnkandidaten im Handler. Ein `CallDeviceSpecificFunction`-/`VCall`-Dispatcher wird in diesem ELF durch Dynsym nicht ausgewiesen; das äußere DAL-Statusverhalten wird aus diesem Artefakt daher nicht belegt und ist OFFEN. Der dokumentgebundene Header-/Deskriptorvertrag (null Argumente) ist keine neue Prüfung oder Propagationsmessung des äußeren Returnwerts.
- Nichtnull-Resultate/0-Resultat bedeuten zur Laufzeit konkreten Geräteerfolg/-fehler: OFFEN. Nur statische Returnpfade und Helper-Aufrufe wurden untersucht.
- Nicht auflösbare indirekte Aufrufe/Referenzen sowie vollständige Laufzeit- und Zustandswirkung aller Helper: OFFEN. REA-Callgraph-Abdeckung nennt auflösbare Call-Referenzen; Ziel-adresslose indirekte Flüsse sind nicht belegt.

Methoden: REA zuerst; REA MCP `rea-agents 6.5.0`, Ghidra Provider `12.1.4`, ARM-ELF, Analyseprofil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Verwendet: `binary_session`, `open_binary`, `search_procedures`, `procedure_info`, `procedure_pseudo_code`, `procedure_callers`, `procedure_callees`, `analyze_function`, `procedure_references`, `address_to_file_offset`, `read_bytes`, `inspect_with_objdump`, `export_evidence_bundle`, `close_binary`. REA Ghidra lieferte Kontrollflüsse und Source-Byte-Mappings, aber keine dynamische Symboltabelle; REA-objdump `symbols` meldete `no symbols` (Evidence `ev_39a8f8189b4a4d3a8de2aeff60b42683b207baa5b3a1b82b66fe69e85dbf0200`). Dieser beobachtete Koordinaten-/Symbol-Gap begründet `readelf` als benannten Offline-Fallback für `-Ws`, `-lW`, `-SW`, `-rW`. GNU readelf 2.44 bestätigte Dynsym `libpackbus_Push` bei ELF-VA `0x10130`, Größe 424; PT_LOAD-Mappings; `.plt` und `R_ARM_JUMP_SLOT` bei ELF-VA `0x33454`; Dynsym-Suche zeigte keine Einträge namens `CallDeviceSpecificFunction`/`VCall`. Pseudocode ist Werkzeugableitung, kein Originalquelltext. Keine Ausführung des Zielcodes.

Alternativerklärungen/Restunsicherheit: Ghidra markiert den PLT-Call am Analyseort `0x180fc` als terminal und schließt Fallthrough aus; ELF-Sektion und GOT-Relocation zeigen unabhängig, dass `0x180f4` der `.plt`-Stub ist. Grund für Ghidras Terminalflussmarkierung nicht festgestellt. Der exportierte Dynsym-Name ist der Handler; der PLT-Stub ist dessen dynamischer Aufrufpfad, kein separater DAL-Handler. `DAT_00054420` und die beobachteten Displacements sind decompilerische globale-/Pointer-Ausdrücke; es wird weder ein Struct noch ein Feldname postuliert. Der Statuswert `0x82` wird nur als im Helper verglichener Zahlenwert wiedergegeben, nicht als plattformübergreifende Semantik. Threading-, Observer-, Watchdog- und Gerätewirkungen außerhalb beobachteter Calls bleiben unbestimmt.

Geltungsgrenzen: Nur die genannte hashgebundene `libpackbus.so.1.0.1`, Push-Symbol/Handler, direkte auflösbare Caller, direkte Funktionen und die genau eine zusätzliche Ebene ausgewählter Thin-Wrapper. Keine FW30-/XE164-Binaries, Hardware, Runtimeausführung, Geräte-/Netzwerk-/VM-Aktionen, vollständiger ADI-Lifecycle oder unabhängiger Review. Tests: **NOT_RUN** (keine Laufzeittests; ausschließlich Offline-Analyse und Hashprüfung). Dieser Workerbericht ist kein Hardware-/Runtime- und kein unabhängiger Reviewnachweis.

Automatische Evidence-Abdeckungsprüfung nach dem kanonischen Bundle-Export: **PASS** — alle in `report.md` und `push-flow.tsv` referenzierten `ev_`-IDs sind im `REA-Evidence-Bundle.json` enthalten (`referenced-IDs ⊆ bundle-IDs`).
