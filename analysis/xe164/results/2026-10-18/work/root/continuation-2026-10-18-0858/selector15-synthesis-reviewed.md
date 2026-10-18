# WP-XE164-268 — geprüfte Originalstack-Kette für Selektor 15

Diese geprüfte Fassung ergänzt nach der unabhängigen Luna-HIGH-Prüfung WP270 die bisher nur über WP255 verknüpfte anfängliche Globalbedingung. Der ursprüngliche Root268-Bericht und WP270s Eingabepins bleiben unverändert. Die Ergänzung ist Root Self-Review. Vergleichsstand: E287, 2026-10-18.

Die Suche hat jetzt einen konkreten statischen Pfad: Die Originaltabelle enthält `15 → CH_EXIT_SYSTEM`. Ein Ausschnitt aus `CMExit` wählt die zwei aufeinanderfolgenden Zeilen `17,15`. Unter den einzeln dokumentierten Zustands-, Rückkehr- und Speicherbedingungen erreicht die zweite Zeile `CMCallHook(15,0,0,0)`. Dessen belegter Managerpfad kann den registrierten Callback über einen indirekten **BX** aufrufen. Genau diese Transferform fehlte in der früheren BLX-Suche.

Das ist eine **HYPOTHESE für die zusammenhängende Laufzeitkette**, gestützt auf **VERIFIZIERTE lokale Instruktionen, Daten und Bedingungen**. Eine beobachtete Ausführung, die konkrete DSO-Auflösung und die Identität des registrierten Objekts sind weiterhin OFFEN. Dieser Bericht ist Root Self-Review einer Synthese; die tatsächlichen Luna-HIGH-Worker und unabhängigen Gegenprüfungen sind in den Eingaben benannt.

## Belegte Stücke und ihre Verbindungen

| Stück | Lokaler Befund | Grenze der Verbindung |
|---|---|---|
| Originale Namen | Der 34-Zeilen-Lookup ordnet 2 dem Text `CH_INIT`, 17 `CH_EXIT_SYSTEM2` und 15 `CH_EXIT_SYSTEM` zu. | Die Zeichenfolgen sind binärseitige Bezeichnungen; sie liefern keine C-Signatur. |
| Manager-Sequenz | Der lokale `CMExit`-Scan liefert Zeile 19, Count 2: 17 und 15; die Stop-Zeile 16 ist ausgeschlossen. | Frühere opake Aufrufe können Register und Zustand verändern. |
| Aufrufargument | Der Zweizeilenpfad kann zuerst `(17,0,0,0)`, danach `(15,0,0,0)` an `CMCallHook` übergeben. | Die Zeitaufrufe und der erste Hook müssen an die genannten Fortsetzungen zurückkehren und den benötigten Zustand erhalten. |
| Callback-Dispatch | Der ausgewählte callfreie Managerpfad lädt den ersten Listenkopf, bildet `head+16` und übergibt Selektor 15 an den Helper. Der Helper lädt den Targetwert bei Objekt `+32` und transferiert mit BX. | Zusätzlich zu gültigen Speicherbereichen muss der anfängliche Wert bei [0x00510868] von 0xffffffff verschieden sein und eine lesbare Basis für den Load bei +0x1c ergeben. Zulässiges Halfword 2/4/5, Target ungleich null, null optionaler Callback und Nichtüberlappung sind weitere Voraussetzungen. |
| Veröffentlichung | Das exakte IoDrvDal-`ComponentEntry` veröffentlicht den ELF-relativen Dispatcher `0x362c` bei seinem Eingabeblock `+0x18`. Der Originalmanager kopiert diese Position konditional nach Registrierungsblock `+0x20`. | Das ausgewählte DSO, der kopierte Block und das spätere Listenelement müssen tatsächlich dieselben Objekte betreffen; opake Effekte bleiben offen. |
| IoDrvDal-Verbraucher | Dispatcher-Eingang 15 wählt Zelle `0x3680 → 0x42f4`: Getter-Aufruf, Load aus aktuellem `r0+4`, indirekter Aufruf. Eingang 2 wählt den getrennten Getter/`+0`-Pfad. | Getter-Auflösung und Objektidentität sind nicht zur Laufzeit beobachtet. |
| Installierter Provider | Das exakte libdal ist der einzige installierte Definitionskandidat für den Getter. Dessen lokaler Körper liefert den Tabellenbasiskandidaten `0x14154`; Positionen `+0/+4` haben relocation-gebundene Targetkandidaten `0x1bec/0x1dc0`. | Installierter Kandidat und tatsächlicher Lookup-Gewinner sind unterschiedliche Nachweise. |
| Nachlauf | Nach Rückkehr vom `+4`-Aufruf setzt IoDrvDal lokal `r4=0`. Ein gemeinsamer Nachlauf kann dennoch weitere Callbacks ausführen. | Eine bedingungslose Null-Rückgabe des gesamten Dispatchers folgt daraus nicht. |

## Präziser Stand der Providergrenze

**VERIFIZIERT:** Auf dem belegten lokalen Selektor-15-Pfad lädt IoDrvDal das Wort bei Position `+4` und ruft es ohne sichtbare Nullprüfung auf. Falls ein Ersatzobjekt genau diesen Pfad bedient, muss dieser Wortwert ein für den Transfer gültiges Target sein. Das ist eine bedingte Aufrufvorbedingung dieser Position.

**HYPOTHESE:** Unter den genannten Bindungsbedingungen ist `+4` der vom Originalmanager unter der binären Bezeichnung `CH_EXIT_SYSTEM` erreichbare Provider-Eintritt. Für die Existenz des Originalverbrauchers und eines passenden Selektorwerts ist damit mehr belegt als durch einen Exportnamen oder eine Backend-Attrappe. Die statischen Pfade begründen weiterhin keine universelle Pflicht, dass jede Laufzeitkonfiguration beide führenden Positionen aufruft, und keine ungeprüfte Ersatzsignatur.

**OFFEN:** konkrete Lookup-/Relocation-Werte, Manager-/Listen-/Payload-Identität, Fortbestand des Halfwords und der Targetfelder, Register- und Speicherwirkungen der übrigen Aufrufe, tatsächliche Aufrufreihenfolge einer Sitzung und zulässige Semantik eines Ersatzes. Namen, Positionen und lokale Registerwerte ersetzen keinen vollständigen ABI-Vertrag.

Die vorherige Aussage, ein Selektor-15-Aufrufer sei vollständig unbekannt, ist durch die bedingte Manager-Sequenz überholt. Die vollständige Laufzeitbindung ist dadurch nicht geschlossen. Die 101 alten Roh-Dispatchtabellen sind bereits inventarisiert; weitere breite Suche nach einfachen MOV15/BLX-Mustern hat gegenüber diesen konkreten Grenzen keinen Vorrang.

## Prüfung

`inputs.json` bindet die herangezogenen Berichte und drei Originalartefakte. `validate.py` prüft diese Pins, die primären Tabellen-/Namensbytes, die IoDrvDal-Zelle und direkten Branchziele sowie den Getter-Basisausdruck und die zwei libdal-Tabellenworte. Die Synthese-Verbindungen selbst bleiben ausdrücklich konditional und werden nicht durch Hashprüfungen zu Laufzeitbeweisen. Tests: PASS für diese begrenzte statische Prüfung; Runtime, VM, Geräte und Zielnetz: NOT_RUN.
