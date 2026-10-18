> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-065 — Transaktionsownership, Generation und Lockreihenfolge

## Ergebnis

**VERIFIZIERT (begrenzter Source-Level-Befund):** In den sichtbaren Quellen ist kein belegbarer Lockorder-Deadlock zwischen Adapter-State, Adapter-Lifecycle, Bridge-Control und Worker-Callbacks erkennbar. Beim Bridge-Stop wird `bridge_control_mutex` vor `pthread_join` freigegeben; der Worker nimmt weder Lifecycle- noch Bridge-Control-Lock. Die Worker-Callbacks können `state_mutex` nehmen, während Exit auf den Worker wartet.

**VERIFIZIERT:** Write-/Read-Transaktionen speichern Tasknummer, `pthread_self()` und Lifecycle-Generation. Alle Fortsetzungs-/Endpunkte prüfen aktiven Zustand, Task, Owner-valid-Flag, `pthread_equal` und Generation unter `state_mutex`. Ein gleichzeitig anderer pthread kann daher den sichtbaren WriteEnd-Pfad nicht committen. Exit, Reset und erfolgreicher Close beseitigen aktive Transaktionsmarker oder verhindern Close bei aktiver Transaktion.

**VERIFIZIERT (Lifecycle-Lücke):** `virtual_adi_reset()` nimmt nur `state_mutex`, erhöht die Generation und löscht den Zustand; im Bridge-Build nimmt es nicht `lifecycle_mutex` und stoppt die Bridge nicht. Ein Reset kann daher eine laufende Bridge in den Zustand „Worker gestartet, Adapter nicht initialisiert“ bringen. Ein folgendes `adapter_exit()` gibt bei `!initialized` zurück, bevor `virtual_model_bridge_stop()` erreicht wird. Spätere Init-Aufrufe sehen den Worker als bereits gestartet und starten keinen zweiten. Das ist ein belegbarer Bridge-/Lifecycle-Inkonsistenzpfad, aber kein belegter Lock-Deadlock.

**OFFEN/HYPOTHESE:** Ein alter, verspätet aufgerufener Write-End-Aufruf trägt keinen Transaktions-Token. Wenn derselbe pthread nach Reset/Exit und neuer Init eine neue WriteStart-Transaktion mit derselben Tasknummer begonnen hat, kann ein verspätetes WriteEnd dieses neue Transaktionsobjekt anhand der sichtbaren Kriterien nicht von einem legitimen aktuellen WriteEnd unterscheiden. Das ist ein Alias-Risiko für alte Aufrufe, kein Nachweis, dass ein externer Caller solche Aufrufe erzeugt. Ein ähnlicher begrenzter Identitätsvorbehalt besteht, falls POSIX eine beendete Thread-ID wiederverwendet und die alte Transaktion bis dahin aktiv blieb; tatsächliche Caller-/Thread-Lebensdauer und Plattformverhalten sind hier nicht belegt.

## Lock- und Callback-Befund

Der endliche gerichtete Graph steht in `lock-graph.tsv`. Sichtbare Mutexes: `state_mutex` (immer), `lifecycle_mutex` (nur `VIRTUALWAGO_ENABLE_MODEL_BRIDGE`) und `bridge_control_mutex` (Bridge-Build); dazu die Bridge-Control-Condition-Variable. Die Adapter-Init-Reihenfolge ist Lifecycle → State → Bridge-Control, wobei Bridge-Control innerhalb `virtual_model_bridge_start()` gehalten wird. Exit nimmt Lifecycle → State, gibt State am Ende des inneren Blocks frei, ruft danach Stop auf und hält Lifecycle dabei weiter. Stop hält Bridge-Control nur bis zur Markierung/Wakeup-/Worker-ID-Übernahme und gibt es vor `pthread_join` frei. Erfasst sind außerdem alle sichtbaren pthread-Wartepunkte sowie die drei Worker-`poll()`-Pfade (Listener, Client und Schreibbereitschaft); sie halten keine dieser Mutexes und reagieren auf die Wake-Pipe bzw. Stop-Flag.

Der Worker kann über STATUS, INPUT, PERMIT, FAULT, Disconnect oder fatalen Exit Adapter-Hooks aufrufen; diese nehmen `state_mutex`. In den Callback-Pfaden ist kein Erwerb von Lifecycle- oder Bridge-Control-Lock sichtbar. Somit gibt es für die beobachtete Join-Abhängigkeit Worker → State und Exit → Join keinen Gegenpfad, bei dem Exit State während des Joins hält oder Worker Lifecycle/Bridge-Control braucht. Die Condition-Variable-Wartekante gibt Bridge-Control konventionell während `pthread_cond_wait` frei. Der Destructor ruft denselben Stop-Pfad auf.

**Alternativerklärung:** `virtual_adi_reset()` ist als eigene Modell-/Test-Erweiterung gedacht und könnte per nicht sichtbarem Aufrufer nur bei gestoppter Bridge verwendet werden. Das ist aus Header und Aufrufstellen nicht nachweisbar. Die Funktion ist in `adi_digital_adapter.h` öffentlich deklariert; daher wird der Reset-Befund als konkrete Quellpfad-Eigenschaft festgehalten, ohne einen Produktionscaller zu behaupten.

## Transaktions- und Generation-Befund

WriteStart/ReadStart setzen `*_active`, Task, Owner-valid, pthread und aktuelle Generation unter State-Lock. Jeder Read-/Write-Fortsetzungsaufruf und Endpunkt ruft `owns_read`/`owns_write` auf, die alle fünf Kriterien einschließlich Generation vergleichen. Andere Threads mit abweichendem `pthread_equal` scheitern; ein falscher Task scheitert ebenfalls. Fehlgeschlagene Ownership-Checks verändern die aktive Transaktion in den sichtbaren Endpunkten nicht. Erfolgreiches WriteEnd und ReadEnd löschen Active-/Owner-valid; fehlgeschlagenes oder unvollständiges WriteEnd löscht die aktive Write-Transaktion. Close ist bei aktiven Lese-/Schreibtransaktionen abgewiesen. Reset und Exit löschen mit `memset` auch aktive Marker; Generation wird vor dem Löschen erhöht.

Generation ist ein globaler Modellzähler und kein Aufruf-Token: Aufrufer übergeben beim Endpunkt keine Generation. Er verhindert, dass ein noch unverändert vorhandener aktiver Datensatz nach einer Generationserhöhung anerkannt wird; Reset/Exit löschen aber diesen Datensatz ohnehin. Der Zähler überspringt Null beim Wrap (`:111-114`), doch ein Gleichstand nach vollständigem 64-Bit-Umlauf ist im begrenzten statischen Review nicht weiter ausgeschlossen. `pthread_t`-Wiederverwendung nach Threadende kann mangels Caller-/Join-Vertrag ebenfalls nicht abschließend behandelt werden.

## Status und Grenzen

- Lockorder-Deadlock: **VERIFIZIERT — kein belegbarer Zyklus in sichtbaren Erwerbs-/Wait-/Callback-Kanten gefunden**. Dies ist ein begrenzter No-Issue-Found-Befund, kein unbeschränkter Beweis.
- Cross-thread Commit: **VERIFIZIERT — kein Pfad für gleichzeitig verschiedene pthreads bei üblicher `pthread_equal`-Semantik**.
- Stale aktive Transaktion nach Reset/Exit: **VERIFIZIERT — aktive Marker werden gelöscht; kein aktiver Datensatz bleibt über diese Übergänge bestehen**.
- Verspäteter tokenloser Endaufruf nach neuem Start: **OFFEN/HYPOTHESE — gleicher pthread und gleicher Task können eine neue Transaktion matchen; Aufrufervertrag nicht sichtbar**.
- Reset/Bridge-Inkonsistenz: **VERIFIZIERT auf Source-Level**; Auswirkungen außerhalb sichtbarer Adapter-/Bridge-Aufrufe bleiben offen.
- Annahmen: POSIX pthread Mutex-/Condition-/Join-Verträge wie üblich; erfolgreicher `pthread_join` wartet auf Worker-Ende; `pthread_equal` liefert für gleichzeitige, verschiedene Threads false. Es werden keine Hersteller- oder Laufzeitverträge angenommen.
- Restunsicherheit: keine Aufrufer außerhalb der vier C/H-Dateien verfolgt; kein Caller-Vertrag für Reset/Exit; keine Beurteilung von dynamischem Loader-/Destructorkontext, pthread-ID-Wiederverwendung in der Zielumgebung oder Datenrennen außerhalb dieser sichtbaren Funktionen; keine Laufzeit- oder Schedulerbeweise.

## Inputs, Werkzeuge und Tests

Alle fünf Eingaben stimmen exakt mit den angegebenen Bytes und SHA-256-Werten überein; siehe `inputs.tsv`. Quellreferenzen beziehen sich auf diese Revisionen. Werkzeugversionen: GNU coreutils `sha256sum 9.7`, ripgrep `15.2.0`, mawk `1.3.4 20250131`; Zeilenreferenzen mit `nl -ba`. Kein REA, da nur gewöhnliche Quelltext-Lock-/Callgraph-Analyse erforderlich ist.

Build, Unit-/Integrationstests, Fuzzer, Ausführung, Geräte-, Netzwerk-, VM- und Runtime-Prüfungen: **NOT_RUN** wie vorgegeben. Dies ist ein **Worker-Self-Review**; keine unabhängige Review oder Laufzeitbeobachtung wird behauptet. Es wurden ausschließlich die fünf geforderten Ausgabedateien in diesem Work-Package-Verzeichnis angelegt.
