> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-099 — Get-UID-/Read-Config-Dispatch und Digitalprofile

## Ergebnis

**VERIFIZIERT:** Für die genau dokumentierten Digital-8- und Digital-16-Profile ist kein Widerspruch zwischen den Antworten des Eigenadapters und den erfolgreichen Originalconsumer-Läufen belegt. Die Sourceprüfung zeigt für `GET_UID` und `READ_CONF_REG` ein absichtlich negatives inneres Ergebnis (`-1`) bei äußerem `DAL_SUCCESS`, verbunden mit einem gesetzten Fehler-Latch. Der Originalconsumer-Lauf belegt für die getesteten Signalfolgen funktionierende angeforderte Ausgänge, Permit `0` und Fehlerstatus `0`. Weder Report noch JSON belegen, dass die konkreten Dispatch-Zweige `get_uid` oder `read_conf_reg` in diesen Läufen erreicht wurden.

Die Aussage ist daher begrenzt: **kein nachgewiesener Widerspruch für die exakt demonstrierten Profile**. Das ist keine Vollständigkeits- oder Unerreichbarkeitsaussage. Falls einer der Zweige unter den im WP096 beschriebenen Guards tatsächlich aufgerufen wird, passt die Adapterantwort nicht zu den dort beschriebenen Erfolgsprädikaten; ob das in den Digital-8/16-Trials geschah, ist **OFFEN**.

## Quellen-/Nachweisstufenmatrix

| Stufe / Quelle | Beobachtung | Schlussfolgerung | Status und Grenze |
|---|---|---|---|
| Eigenadapter-Source, `tools/adi_digital_adapter.c:769-778` | Beide Namen laufen in denselben Zweig. Bei initialisiertem Adapter und nicht-null `return_value` wird der Fehler-Latch gesetzt, `-1` in `return_value` geschrieben und `DAL_SUCCESS` zurückgegeben. Vor Initialisierung bzw. bei null `return_value` gelten separate Fehlerpfade. | Sourcevertrag des Eigenadapters ist für beide Funktionen „äußerer Aufruf erfolgreich angenommen, inneres Ergebnis unsupported/Fehler, Fehler-Latch“. | **VERIFIZIERT** als Sourceverhalten. Kein Laufzeitbeleg daraus allein. |
| WP096 statische Dispatchanalyse, `report.md:13-14` | Für `get_uid` beschreibt WP096 die Gates, inneren/äußeren Ergebnisse und Fortsetzungsbedingungen; Fortsetzen erfordert äußeren Rückgabewert `0`, Ausgabe `local_30 == 0` und Gleichheit des gelesenen DWORD mit `local_2c[0]`. Für `read_conf_reg` sind zusätzliche Record-, Pointer-, Flag- und Comparator-Guards dokumentiert; Fortsetzen verlangt äußeren Rückgabewert `0`, `local_2c[0] == 0` und den beschriebenen 16-Bit-Vergleich. | Ein Aufruf mit dem Adapterzweig erhält zwar äußerlich `0`, setzt aber den vom Adapter bedienten inneren Ergebniszeiger auf `-1`; damit ist mindestens das jeweilige dokumentierte Null-Erfolgsprädikat nicht erfüllt. Der Originalconsumer würde unter dieser bedingten Pfadannahme keinen erfolgreichen Recordfortschritt erhalten. | **VERIFIZIERT** als bedingte statische Pfadfolge in WP096; keine Dispatch-Reachability und keine Laufzeit-Ausführung. |
| Eigenständiger Adaptertest, `tools/adi_digital_adapter_test.c:263-268` | Der eigene C-Vertragstest ruft `GET_UID` direkt auf: äußerer Rückgabewert `DAL_SUCCESS`, innerer Wert `-1`; anschließend ist die effektive Ausgabe null. Ein direkter `READ_CONF_REG`-Aufruf kommt im angegebenen Test nicht vor. | `GET_UID`-Verhalten ist im eigenen Harness ausdrücklich geprüft. Für den gemeinsam implementierten `READ_CONF_REG`-Namen belegt der Test den konkreten Zweig nicht separat. | **VERIFIZIERT** für beobachtete Testassertion; Testausführung dieses Work-Package: **NOT_RUN**. `READ_CONF_REG`-Testdeckung: **OFFEN**. |
| Dokumentierter Originalconsumer-Runtimelauf, `docs/native-digital-tests-2026-10-13.md:15-28,44-63`; JSON `native_trials` | Hashgebundene Digital-8- und Digital-16-Trials verwenden den Eigenprovider mit Originalruntime, nativem I/O-Manager und originalen WAGO-I/O-Treibern. Die getesteten Eingangswerte erzeugten dokumentierte angeforderte Ausgänge; Permit blieb `0`, effektive Ausgabe `0`, und regulärer Faultstatus `0`. | Der Originalconsumer verarbeitete die demonstrierten Muster in diesen Profilen erfolgreich. Das belegt keine konkrete Ausführung von `get_uid` oder `read_conf_reg`; der Bericht enthält weder Dispatch-Trace noch Record-Guard-Beobachtung. | **VERIFIZIERT** nur für berichteten Lauf und Scope. Reachability beider konkreten Zweige: **OFFEN**. Keine Aussage über physische I/O-Äquivalenz. |
| WP096 Reachability-Aussage | WP096 klassifiziert Zielprofil-Reachability als `NOT_RUN`; eine Mappingquelle lag dort nicht vor. | Aus statischen Pfadbedingungen und den erfolgreichen Trials kann weder tatsächliche Erreichbarkeit noch Unerreichbarkeit dieser konkreten Calls für Digital-8/16 abgeleitet werden. | **OFFEN**. |
| Nicht demonstrierte Anforderungen | Die vorliegenden erfolgreichen Profile decken Digital-8 und Digital-16 mit den dokumentierten Testmustern ab. | Jenseits dieser Profile bleibt offen, ob und welche durch den Originalconsumer verlangten `get_uid`-/`read_conf_reg`-Antworten unterstützt werden müssen und welche konkreten Records/Guards sie erreichen. Für eine Anforderungserweiterung wäre zunächst ein belastbarer Mapping-/Dispatch-Nachweis und ein dazu passender Vertragstest erforderlich. | **OFFEN**; keine Übertragung auf Analog, PWM, seriell oder allgemeinen K-Bus. |

## Beobachtung, Schlussfolgerung, Unbekanntes

- **Beobachtung — VERIFIZIERT:** Der Quellzweig gruppiert beide Namen und liefert für den normalen initialisierten/nicht-null-Ausgabepointer-Fall `DAL_SUCCESS` außen, `-1` innen und latcht einen Fehler.
- **Beobachtung — VERIFIZIERT:** Der Eigenadaptertest enthält einen direkten `GET_UID`-Fall mit genau diesem äußeren/inneren Ergebnis und prüft die dadurch ausbleibende effektive Ausgabe. Er enthält keinen direkt identifizierten `READ_CONF_REG`-Fall.
- **Beobachtung — VERIFIZIERT:** Dokumentierte finale Digital-8/16-Trials liefen mit dem Eigenprovider durch Originalruntime, nativen I/O-Manager und originale Treiber und erzielten die angegebenen angeforderten Ausgänge bei Permit `0`, effektiver Ausgabe `0` und Faultstatus `0`.
- **Schlussfolgerung — VERIFIZIERT, begrenzt:** Diese Laufresultate widersprechen der Adapterantwort nicht nachweislich, weil kein Quellenbeleg die Dispatch-Aufrufe den Trials zuordnet. Die Aussage, der Pfad sei nicht erreicht worden, wäre ebenso unbelegt.
- **Bedingte Folgerung — HYPOTHESE:** Falls einer der beiden Adapterzweige bei einem Record der demonstrierten Profile tatsächlich aufgerufen wurde, verfehlt `-1` die in WP096 beschriebenen inneren Null-Erfolgsbedingungen; das wäre für diesen Record ein Konflikt mit erfolgreichem Fortschritt.
- **Unbekannt — OFFEN:** Konkrete Dispatch-Reachability, Argument-/Recordwerte zur Laufzeit, separate `READ_CONF_REG`-Testabdeckung und Anforderungen anderer Profile.

## Alternativerklärung und Restunsicherheit

Eine mit den Quellen vereinbare Alternative ist, dass die für beide Dispatches nötigen Record-Discriminatoren und Guards in den getesteten Digital-8/16-Konfigurationen nicht vorlagen oder dass der Originalconsumer diese Dispatches für die gezeigten Signalfolgen nicht aufrief. Das ist eine mögliche Erklärung, kein beobachteter Sachverhalt. Andere Record-/Profilpfade oder nicht protokollierte Aufrufe sind mit den vorliegenden Quellen ebenfalls nicht ausgeschlossen.

Die WP096-Auswertung ist statische, decompiler-/assemblygestützte Analyse. Sie bindet die benannten Guards und Statusfolgen, aber keine Zielprofilzuordnung. Die öffentlichen Digitalberichte fassen hashgebundene private Runtimetrials zusammen; sie enthalten keinen Aufruftrace für diese beiden Funktionsnamen. Der Eigenadaptertest ist ein eigener Vertragstest und emuliert weder den Original-I/O-Treiber noch den Originalconsumer. Diese vier Nachweisstufen dürfen nicht zusammengezogen werden.

## Test-/Prüfstatus

- Eingabe-SHA-256-Prüfung: **PASS**.
- Statische Prüfung der genannten Source-, Test- und Reportbereiche: **PASS**.
- Eigenständiger Adaptertest in diesem Work-Package ausgeführt: **NOT_RUN**.
- Originalconsumer-Runtime in diesem Work-Package ausgeführt: **NOT_RUN**; nur der hashgebundene dokumentierte Nachweis ausgewertet.
- Konkrete `get_uid`-/`read_conf_reg`-Dispatch-Reachability für Digital-8/16: **NOT_RUN** laut WP096, hier weiterhin **OFFEN**.
- Binary-Neuanalyse, Geräte-, Netzwerk-, VM- oder Runtimezugriff: **NOT_RUN**.

## Eingabe-Hashes

| Eingabe | SHA-256 | Prüfung |
|---|---|---|
| `tools/adi_digital_adapter.c` | `c0e1de356de1bc2be11b70bca8812971a9deaa4a17c9ce740e323d2e24c57e6b` | **PASS** |
| `tools/adi_digital_adapter_test.c` | `03638b5688ea818eb3a9f8c758a7009d91ed1d2335715e3cef33e60f816642f3` | **PASS** |
| `docs/native-digital-tests-2026-10-13.md` | `1bc47976a9042ba4d82d44ee5b88bffe01b61ee73163b4baeefad75f03370135` | **PASS** |
| `evidence/native-digital-tests-2026-10-13.json` | `c090697b84ca95604a9431fc6ab5517b9f7fdf4941cdda7025956b5569dce842` | **PASS** |
| `WP-XE164-096/report.md` | `d7fd351d7a3452e44a85a0c151959dbf0fc4fd0bb6f2a797a8f4e48c66ec756d` | **PASS** |

## Artefakte

Alle folgenden Dateien liegen ausschließlich im WP-XE164-099-Ausgabeverzeichnis. `SHA256SUMS` führt die drei inhaltlichen Artefakte und den Validator auf.

- `report.md`
- `evidence-matrix.tsv`
- `validate.py`
- `SHA256SUMS`
