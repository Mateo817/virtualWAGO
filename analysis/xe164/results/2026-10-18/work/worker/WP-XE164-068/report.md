> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-068 — eigener DeviceSpecific-Vertrag

## Ergebnis und Scope

**VERIFIZIERT (statische Quelltextanalyse):** Im eigenen digitalen Adapter liefern `CallDeviceSpecificFunction` und `VCallDeviceSpecificFunction` dieselbe Implementierung `device_specific(name, ret, args)`. Der äußere Rückgabewert ist der DAL-Status der Dispatch-/Argumentübergabe; bei den unterstützten bzw. ausdrücklich abgewiesenen Operationen steht das operationsbezogene Resultat separat als `int32_t` in `*return_value`. Für unbekannte Namen kommt `DAL_NOTUSED` zurück und das Resultatfeld bleibt unverändert.

Dies beschreibt ausschließlich den eigenen In-Memory-Adapter, nicht den Hersteller-DAL-/`libpackbus`-Vertrag. Scope: `tools/adi_digital_adapter.c` DeviceSpecific-Helfer und Slot-28/29-Wrapper, passende Harness-Assertions sowie die vorgegebene Consumer-Evidenz für Slot 28/29. Keine Lifecycle-, Bridge-, Register-/Analog-, Firmware- oder SFR-Semantik.

## Dispatcher-Vertrag

Beide Wrapper rufen unter `STATE_GUARD` zuerst `refresh_watchdog_locked()` auf. Slot 28 startet mit `va_start(args, ret)`, übergibt die `va_list` an `device_specific`, beendet sie mit `va_end` und gibt deren `int32_t` zurück. Slot 29 übergibt die empfangene `va_list` direkt an dieselbe Funktion und propagiert deren Status. Der Dispatcher prüft den Namen vor den Operationen. Für jede erkannte Operation gilt: falls `state.initialized` falsch ist, liefert er unmittelbar `DAL_FAILURE`; in diesem Pfad liest er keine Operationsargumente und schreibt `return_value` nicht. Für einen erkannten, initialisierten Aufruf mit `return_value == NULL` latcht er einen Modellfault und liefert `DAL_FAILURE`; auch dort werden keine Varargs gelesen.

`latch_fault_locked()` setzt `fault_latched`, setzt `effective_outputs` auf null und markiert einen aktiven Schreibframe als fehlgeschlagen. Das ist eine eigene Modellregel. Ein erfolgreicher äußerer Status kann deshalb mit einem inneren Fehlerwert zusammen auftreten. Einzelheiten und Assertions stehen in [device-specific-matrix.tsv](device-specific-matrix.tsv).

## Operationsübersicht

- `LIBPACKBUS_DAL_FUNCTION_PUSH`: keine Argumente. Bei initialisiertem Modell und nicht-null Resultatpointer ist der äußere Status `DAL_SUCCESS`; inner wird `DAL_FAILURE` bei gelatchtem Modellfault, sonst `DAL_SUCCESS` geschrieben. Ein fehlender Resultatpointer latcht den Fault und ergibt äußerlich `DAL_FAILURE`. Die Harness-Assertions prüfen den inneren Wert über VCall im Fault- und Recovery-Fall. Das ist die ausdrücklich als eigene Policy kommentierte Sichtbarmachung eines Modellfaults, keine abgeleitete Hersteller-Push-Semantik.
- `LIBPACKBUS_DAL_FUNC_GET_TERMINAL_INFO_32`: Argumente in sichtbarer Reihenfolge `uint32_t capacity`, `void *records`, `void *count_out`. Inner `1` wenn `records` oder `count_out` null ist; dann wird auch `count_out` nicht beschrieben. Diese Argumentvalidierung latcht einen Fault. Bei gültigen Pointern wird zuerst die modellierte Terminalanzahl in `count_out` geschrieben. Inner `2` bei `capacity < terminal_count * sizeof(tKBUS_TERMINAL_INFO_32)`; Records bleiben unverändert und dieser Fall latcht im Dispatcher keinen Fault. Inner `0` bei ausreichender Kapazität: Modellrecords werden kopiert und überschüssige Kapazitätsbytes genullt. Outer ist in diesen Operationsergebnisfällen `DAL_SUCCESS`.
- `LIBPACKBUS_DAL_FUNC_READ_TAB_9`: Argumente `terminal` als `int` (Kommentar im Adapter: `uint8_t` wird zu `int` promoviert) sowie `uint16_t *module_id`. Inner `-1` für Terminal `<1` oder `> selected_profile->terminal_count`; inner `-2` bei gültigem Terminal aber null Outputpointer; andernfalls wird das ausgewählte Modell-Modulwort geschrieben und inner `0` zurückgegeben. Jede Nichtnull-Innenantwort latcht einen Fault. Die beobachteten Profilwerte im Test sind 0x9001/0x9002 für Digital16 bzw. 0x8801/0x8802 für Digital8; das ist Modellkonfiguration, kein Herstelleridentitätsbeleg. Outer für diese inneren Ergebnisse `DAL_SUCCESS`.
- `LIBPACKBUS_DAL_FUNC_GET_UID` und `LIBPACKBUS_DAL_FUNC_READ_CONF_REG`: explizit erkannte, aber nicht unterstützte Namen. Der Adapter liest für diese Pfade keine Varargs, obwohl die externe Evidenz für Originaldeskriptoren andere Formen nennt. Bei initialisiertem Zustand und nicht-null Resultatpointer latcht er einen Fault, schreibt inner `-1` und gibt outer `DAL_SUCCESS` zurück. Bei null Resultatpointer latcht er einen Fault und gibt outer `DAL_FAILURE` zurück. Dies implementiert keinen UID- oder Registervertrag.
- Nullname und jeder sonst unbekannte Name: inner bleibt unberührt; outer `DAL_NOTUSED`. Bei initialisiertem Zustand latcht der Dispatcher einen Fault. Vor Initialisierung gibt es keinen Fault-Latch. Für diese nicht erkannten Namen wird kein Vararg konsumiert.

## Getrennte Original-Consumer-Beobachtung

Die vorgegebene statische Evidenz bindet Slot 28 (Offset `0x70`) an direkte `IoDrvKbus`-Aufrufe an `0x26ac`, `0x2754`, `0x2ba4`, `0x2d64`, `0x3084`, `0x3a3c`, `0x5614`, `0x56a4`, `0x56f0`, `0x5730`, `0x5770`, `0x67ac`, `0x7324` sowie an Helper `0x6d24`, aufgerufen bei `0x7394`, `0x73b0`, `0x73d0`, `0x7408`. Nur einige Namen sind in der Evidence aufgelöst. Terminal-Info32-Preflight erwartet inner `2`; der normale Pfad kombiniert äußeren und inneren Status per OR und behandelt ungleich null als Fehler. Weitere Dispatch-/Resultatinterpretationen sind teilweise unbekannt. Die Quellenbeschreibung präzisiert konkrete Kbus-Aufrufe für Terminal-Info32, Push, get_uid, read_conf_reg und read_table_9; die übrigen Auswahl-/Reachability-Fragen bleiben offen.

Für Slot 29 (Offset `0x74`) sagt die übergebene Evidence nur, dass `Dal_CallDeviceSpecificFunction` die Argumentliste durch Slot 29 weiterleitet. Sie nennt weder exakten FW31-Binaryhash noch Callsite-Adresse, Argumentinhalte, Rückgabebehandlung oder Rückgabepropagation. Die Harness-Funktion `call_through_vcall` ist dagegen ein eigener variadischer Wrapper mit echter `va_list`-Übergabe an den eigenen Adapter; sie emuliert nicht den Originalwrapper.

Die Quelltextverträge oben sind daher nicht mit dem Original-Consumer-Vertrag gleichzusetzen. Insbesondere liefert die eigene Unsupported-UID-/Config-Implementierung inner `-1`, während die mitgelieferte Original-Provider-Zusammenfassung für `read_conf_reg` und `get_uid` weitere Fälle beschreibt. Für Push ist die Original-Handlerinterpretation ausdrücklich nicht vollständig analysiert.

## Evidence, Ausführung und Restunsicherheit

- **Statische Analyse, VERIFIZIERT:** Implementierung und Def/Use/Varargs-Weitergabe aus den in `inputs.tsv` hashgebundenen Dateien; Scope beschränkt auf benannte Bereiche.
- **Teststatus: NOT_RUN.** Keine Tests oder Builds ausgeführt. Harness-Assertions wurden nur gelesen; sie sind direkte Assertions im Quelltext, kein in diesem Arbeitspaket ausgeführter Lauf.
- **Harness-Abdeckung:** direkte Call-Assertions für Terminal-Info32 (Kapazität 0, exakt 2 Records, 31 Bytes, großer Puffer/Zero-Tail) und gültige `read_table_9`-Terminals in `adi_digital_adapter_test.c:73-116`; zusätzlich Digital8 Call-/VCall-Erfolgsfälle und VCall Push in `:304-344`; VCall Push-Fehler-/Recoveryinnerwerte in `:397-413`; unsupported GET_UID-Aufruf und Faultwirkung in `:263-268`.
- **Nicht direkt getestet (OFFEN als Testabdeckung):** null Name, unbekannter Name, null `return_value`, null Terminal-Info-Records-/Countpointer, `read_table_9` Terminal 0/out-of-range, null `module_id`, die explizit nicht unterstützte `READ_CONF_REG`-Operation und erkannte Operationen vor `Init`. Quellcodeverhalten ist trotzdem sichtbar, aber es gibt dazu in den inspizierten Assertions keinen direkten Nachweis.
- **Alternativerklärungen / Grenzen:** Namen sind nur über Makrovergleiche in der eigenen Quelle identifiziert; daraus folgt kein Herstellervertrag. Die eigene Profil-/Terminalanzahl, Modul-IDs, Buffer-Copy-/Zero-Fill-Regeln und fault-latched Push-Antwort sind Modellpolicy. Die Slot-28/29-Consumerangaben bleiben auf die im Boundary-TSV/docs genannte statische Evidenz begrenzt; sie belegen keine Laufzeitreachability, ein FW31-Slot-29-ABI im vollständigen Umfang oder Originalprovider-Akzeptanz.
- **Toolversionen:** GNU coreutils `sha256sum 9.7`, ripgrep `15.2.0`, GNU sed `4.9`, GNU Bash `5.2.37`; nur zum Hashabgleich und statischen Lesen/Suchen. Keine Compiler- oder Testwerkzeuge ausgeführt.

## Fundstellen

- Adapter-Dispatcher und Operationen: `tools/adi_digital_adapter.c:155-159`, `:694-799`.
- Slot-28/29-Wrapper: `tools/adi_digital_adapter.c:784-800`.
- Harness-VCall-Wrapper: `tools/adi_digital_adapter_test.c:19-30`.
- Harness Terminalinfo / read_table_9: `tools/adi_digital_adapter_test.c:73-116`.
- Harness unsupported UID: `tools/adi_digital_adapter_test.c:263-268`.
- Harness Digital8 und VCall: `tools/adi_digital_adapter_test.c:304-344`; Push-Fault/-Recovery: `:397-413`.
- Slot-28/-29-Beobachtung: `boundary-static.tsv` Zeilen 30-31; ergänzende Originaldeskriptor-/Consumerzusammenfassung in `docs/adi-contract-2026-10-12.md:75-81`.

## Arbeitsstatus

**VERIFIZIERT:** Alle fünf vorgegebenen Eingabedateien stimmen bytegenau mit ihren übergebenen SHA-256-Werten überein (siehe `inputs.tsv`). Nur dieses Ausgabeverzeichnis wurde angelegt/beschrieben. Keine Geräte-, Netzwerk-, VM-, Build- oder Testaktion.
