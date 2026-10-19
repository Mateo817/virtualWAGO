# PWM: begrenzter asynchroner Kanal, 19. Oktober 2026

**VERIFIZIERT:** Mit dem explizit synthetischen Erkundungsmodus erreicht der
unveränderte Originalstack RUN und überträgt sieben wechselnde angeforderte
Ausgangsframes korrekt an den Modellkanal. Der frühere Blocker `async_com_open`
ist für diesen begrenzten Versuch geschlossen. Das ist keine vollständige
750-677-Emulation und kein Nachweis fehlerfreier Original-Moduldiagnose.

## Implementierung und Vertrag

[ADR-0011](adr-0011.md) beschreibt den Opt-in-Schalter
`VIRTUALWAGO_PWM_ASYNC_EXPLORATION` im [Adapter](../tools/adi_digital_adapter.c).
Er erfordert `VIRTUALWAGO_ADI_TRACE` und gilt nur für PWM677. Der normale Build
behält seine bisherige Behandlung nicht unterstützter UID-/Async-Aufrufe.

- Slot 1 erhält die ausdrücklich synthetische UID 750677. Andere Slots erhalten
  weiterhin inner `-1`, ohne ihren Ausgabepuffer zu verändern. Nur in diesem
  Erkundungsmodus löst diese bekannte Metadatenablehnung keinen globalen
  Modellfehler aus. Andere unbekannte Dienste bleiben sichtbar und unbehandelt.
- Open vergibt höchstens vier eigene, nicht wiederverwendete 32-Bit-Tokens.
  Close erhält den pointertypisierten Token **als Wert**. Kein Token verweist
  auf Provider-Speicher. Die Argumentformen stammen aus exaktem FW31-Code und
  authentischen Headern; Poolgröße und Lebensdauer sind eigene Modellregeln.
- Scalar StartRead/PollRead unterstützen eine ausstehende Anfrage pro Token.
  Der passende Poll schreibt genau ein synthetisches UINT16 mit Wert 0.
  Die eigene Null-Registerbank akzeptiert Slot 1 und 8-Bit-Kanal-/Registerindizes;
  nativ beobachtet wurde ausschließlich Kanal 0/Register 29. Sofortige
  Fertigstellung ist eigene Testpolitik, keine Messung von Hardwarelatenz.
- Ungültiger Handle: inner 15; NULL-Ausgabepuffer: inner 16; abweichender
  abgeschlossener Leseschlüssel: inner 22. Diese Ergebnisse sind quellgebunden.
  Eigene Grenzen wie voller Pool oder doppelter Start liefern äußeren Fehler.
- Reset, Init/Exit und DeviceClose verwerfen Tokens und ausstehende Leseanfragen.
  DeviceClose ist ausdrücklich eigene Abbruchpolitik, inzwischen lokal getestet.
  Async-Schreiben, Listen und Parameterdienste bleiben unimplementiert.
- Der Erkundungsmodus verweigert `permit=true` für PWM. Angeforderte und
  wirksame Ausgänge bleiben getrennt; wirksame Ausgänge waren stets null.

## Tatsächlich beobachtete Aufrufe

Im erfolgreichen vierten Versuch:

1. UID Slot 1 → synthetisch 750677, Erfolg.
2. AsyncOpen → eigener Token 1, Erfolg.
3. StartRead Slot 1/Kanal 0/Register 29 → Erfolg.
4. Passender PollRead → synthetischer Registerwert 0, Erfolg.
5. AsyncClose Token 1 → Erfolg.
6. UID Slot 2 → explizit abgewiesen (`inner=-1`, Ausgabepuffer vorhanden).
7. Zyklische Frameabnahme: **PASS**, sieben Muster.

Das frühere Blockieren nach dem Registerlesen entstand durch unseren globalen
Fault-Latch bei der zusätzlichen UID-Anfrage. Dass dieser abgegrenzte Fehler
jetzt lokal bleibt, reicht für den beobachteten Prozessdatenpfad. Daraus folgt
**nicht**, dass CODESYS jede UID oder jeden Modulfehler grundsätzlich ignoriert.
Zwei vorherige Startup-Aufrufe `bac_PROXY_*` wurden weiterhin zurückgewiesen;
der nachfolgende reguläre Lifecycle setzte deren Modellfehler zurück. Es wurde
kein allgemeiner Erfolgspfad für unbekannte APIs hinzugefügt.

## Testaufbau und Ergebnisse

FW31-Originalruntime, originaler I/O-Manager und Originaltreiber; PWM-Descriptor
2.0.0.3 und WagoSysModule_75x_677 1.0.0.3. Die unveränderte APP kopiert vier
Eingangs-WORDs auf vier Ausgangs-WORDs in einem 20-ms-Zyklus. Das verwendete
virtuelle Prozessabbild umfasst 16 Byte pro Richtung. Control-/Reservebytes
blieben null. Testmuster: vier einzelne Kanäle, alle vier gemeinsam, umgekehrte
Wertefolge und abschließend null. Die Prüflogik verlangte jeweils einen neuen
Frame nach Eingangsübernahme; ein unveränderter alter Frame genügte nicht.

| Versuch | Änderung / Befund | RUN | Frameabnahme | Automatische Rücknahme |
| --- | --- | --- | --- | --- |
| 1 | Open/Close vorhanden; nächster Aufruf StartRead noch unbekannt | PASS | BLOCKED, Modellfehler, 0 Muster | PASS |
| 2 | Synthetisches Registerlesen vorhanden; späterer Modellfehler | PASS | BLOCKED, 0 Muster | PASS |
| 3 | Zusätzliche Diagnose lokalisiert Fehler auf weitere UID-Anfrage | PASS | BLOCKED, 0 Muster | PASS |
| 4 | UID-Ablehnung bleibt lokaler Dienstfehler | PASS | **PASS, 7 Muster** | PASS |

Die sieben Muster wurden an den Frames 682, 684, 686, 688, 690, 692 und 694
abgenommen. Drei Sekunden nach Abnahme zeigte die Originalruntime weiterhin
RUN und der Modellstatus `fault=0`, `permit=0`, `frames=881`. Diese begrenzte
Beobachtung ist kein Dauertest. Der native Versuch dauerte einschließlich
Prozesswechsel und Rücknahme rund 58 Sekunden.

**PASS:** 286 lokale Tests ohne Skip mit autorisierten privaten Headern;
zusätzlich ARM-Harness unter QEMU in isoliertem Namespace. Der neue Harness
prüft aktivierten und deaktivierten Modus, Canary-Puffer, Poolgrenze,
Tokenlebensdauer, Leseschlüssel, Fehlerfälle, DeviceClose mit ausstehendem Read
und Profiltrennung. Öffentliche CI überspringt die drei Tests mit privaten
Headerabhängigkeiten ausdrücklich; Herstellerdateien werden nicht publiziert.

**PASS:** praktische Netzwerk-/Prozessisolation und abschließender Original-STOP,
sieben unveränderte Originaldateien, keine eigenen laufenden Hilfsprozesse oder
privater D-Bus, CAN STOPPED ohne Pakete. Die private Rücknahme wurde gegen das
Verschwinden des eigenen Wrappers zwischen Prozessprüfung und `readlink`
gehärtet; die genaue Ursache des früheren Rücknahmefehlers bleibt unbewiesen.
Alle vier Rücknahmen dieses Blocks waren erfolgreich.

Ein tatsächlich ausgeführter separater Offline-Workerreview fand keinen
ABI-/Varargs-Widerspruch. Seine Hinweise zu DeviceClose und zur breiten
synthetischen Registerbank sind durch Test/ausdrückliche Modellpolitik behandelt.
Root führte zusätzlich einen **Self-Review** durch. Das ist keine unabhängige
Hardwarequalifikation. [Evidence](../evidence/pwm-async-exploration-2026-10-19.json)
bindet Quellstände, vier Provider, APP und private Receipts durch SHA-256.

## Offen und nicht ausgeführt

- **OFFEN:** vollständige Diagnose/Ready-Zustände der originalen Modul-FBs.
  RUN, erfolgreiche Dienste und korrekte Frames ersetzen diese Abnahme nicht.
  Die verfügbaren Bibliotheksmetadaten liefern noch keinen nachgewiesenen
  konkreten IEC-Instanzpfad zum Auslesen dieser Diagnosen.
- **OFFEN:** echte elektronische UID/Klemmtypkennung, reale Bedeutung und
  Standardwerte des gelesenen Registers sowie weitere Initialisierungszweige.
- **OFFEN:** belastbare Zuordnung des nativen 16-Byte-Abbilds zu Betriebsart,
  Frequenz, Tastgrad und dem vorhandenen eigenen 12-Byte-PWM-Frq-Modell. Die
  vier Roh-WORDs lassen sich jetzt beobachten, aber noch nicht allgemein als
  physische PWM-Kommandos interpretieren.
- **NOT_RUN:** echte PWM-Hardware, elektrische Ausgänge, Flanken-/Timingvergleich,
  Langzeitlauf, Registerschreiben und vollständige Diagnose-/Fehlermatrix.
- **NOT_RUN in diesem Block:** neue native Digital-/Analogläufe und neuer IDE-Build.
  Frühere Ergebnisse bleiben revisionsgebunden; lokal liefen ihre Regressionstests.

Nächster sinnvoller Schritt ist die explizite Projektion der beobachteten
Ausgangswerte und Betriebsart in das Signalmodell sowie die getrennte Abnahme
der originalen Moduldiagnose. Hardwareabgleich kann anschließend folgen.
