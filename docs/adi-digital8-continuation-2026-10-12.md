# Fortsetzung: Digital-8-Kandidat und gesichertes Bootprojekt

Stand: 12.10.2026 UTC; Ausgangscommit `676289b002438d3cb947c83f250b2c6045853756`. Root führte die Geräte-/VM-Aktionen aus; Luna arbeitete an Offlinecode und Dokumenten, Sol an statischen Verträgen und Review. [Bereinigte Evidence](../evidence/adi-digital8-continuation-2026-10-12.json) bindet Quellen, Artefakte und enge Testscopes. Rohdaten und Herstellerdateien bleiben privat. **Kein Adaptereinbau; Original-I/O gegen Simulation NOT_RUN.**

## Vorhandene Anwendung erhalten

Die frühere eigene Anwendung `VirtualWAGO_Research` und die bereits vorher vorhandene `Application` sind verschiedene Anwendungen. Erstere wurde aus dem gesicherten eigenen IEC-Quelltext erzeugt, getestet und entfernt; die Herkunft der zweiten bleibt offen.

**VERIFIZIERT / PASS im Sicherungsscope:** Ein gezielter `Keep, False`-Login beobachtete die vorhandene `Application` als STOP und geladen. Die tatsächliche Onlinefunktion `create_boot_application()` kehrte erfolgreich zurück; anschließend blieb sie STOP. Kein Download, Anwendungsstart, Reset, Löschen oder Runtime-Neustart. Der bestehende Runtimeprozess und seine Originalbibliotheken blieben erhalten; sein CWD ist weiterhin gelöscht.

Der Runtime wurden damit persistente Bootdateien hinzugefügt. Root kopierte die begrenzten regulären Dateien privat und bestätigte bytegleiche Hashes vor/nach der Kopie:

| Bestand der vorhandenen Anwendung | Byte | SHA-256 |
|---|---:|---|
| Application.app | 117064 | `62251e107b19b9fcb9fb82608d29e01a4c9b3e768ee7bbe9ea0569d64d24aca3` |
| Application.crc | 20 | `8ccb854bb678b999334741c1683450f37f14b42a1094099dbbd9a0ad37cd9bc6` |
| CODESYSControl.cfg nach Booterzeugung | 112 | `477570fef50ac4fcbd2fa6906ea88190e4a95dba2343f943b109e518d3dd0e8b` |

Die Konfiguration enthält nun `[CmpApp] Application.1=Application`. Dieser Vorgang war eine autorisierte Software-/Sicherungsaktion, keine reine Leseabfrage. Er verändert zukünftige Startpersistenz. **Restore-/Reboottest NOT_RUN**; STOP nach der Speicherung garantiert kein STOP nach einem späteren Prozessstart. Quellprojekt, Retain-/Persistenzumfang und ursprüngliches Startverhalten dieser Anwendung bleiben offen. Das frühere Fehlen eines Bootbestands ist behoben; ein blinder Neustart ist daraus nicht abzuleiten.

## Tatsächlich gebauter 8-Kanal-Kandidat

Eigentümerfoto: 750-430 → 750-530 → 750-600. Revisionen und aktuelle zyklische Kommunikation bleiben offen. Der passive Cache hat zwei Records mit acht Eingangs- beziehungsweise Ausgangsbits, jeweils Offset null in der eigenen Richtung. Foto und Cache sind getrennte Belege.

Root las die authentischen installierten Beschreibungen: 750-430 `8801_0750043000000000`, Version `2.0.0.14`, SHA-256 `26d302678905d2e8f4c7e34880cf830c4ad56361ebd647e6ed82a9e02c81dd91`; 750-530 `8802_0750053000000000`, Version `2.0.0.15`, SHA-256 `84b4043d448c44155a36916a1b65a39f20ba0560459d3c0ffac53fba351daa5d`. Diese Versionsnummern sind Device-Description-Versionen, keine gelesenen Modulrevisionen. Der passive Abschluss 750-600 bekommt keinen erfundenen Prozessdatenknoten.

**PASS, tatsächlicher nativer Offlinebuild:** [Builder](../tools/codesys_mapped_digital8_candidate.py) und [IEC-Quelle](../prototype/iec/minimal_io_8.st) wurden mit CODESYS 3.5.21.50 gebaut: vor Build, Rebuild, Codegenerierung und Offline-Booterzeugung jeweils null Fehler/Warnungen. Native Parent-BYTE-Rücklesung bestätigt `Application.PLC_PRG.InputByte` und `OutputByte`, jeweils acht ungemappte BOOL-Kinder. Export: Eingang `%IB1` (K-Bus-Diagnose liegt bei `%IB0`), Ausgang `%QB0`; diese IEC-Adressen sind keine ADI-Busoffsets. Task 20 ms, IEC-OutputPermit initial FALSE. Kein Download.

| Eigenes Offlineartefakt | Byte | SHA-256 |
|---|---:|---|
| mapped-digital8-offline.project | 258400 | `19dfae3ac4db36a3e70982908c64d661fc2115936d788be1335ea59dbb74bc2a` |
| mapped-digital8.app | 119780 | `a6d51932a5971d82781ed69cc167a4b7161d3f514feba84f7386368865c6b2a0` |
| mapped-digital8.crc | 28 | `55acdc4eb3c95fbdb46293296dbec917e112fba652aff1f318e3cbae92abd820` |
| mapped-digital8-mapping.csv | 1109 | `0e03637896870e8e38ab74eaac0c680fdb5aea87b53c0d916750fa37c2c75cca` |

**FAIL, separates Wiederöffnen:** Das Prüfsystem öffnete das gespeicherte Projekt und passierte Text-, Reihenfolge-, Enable-, native Mapping- und CSV-Vergleichsassertions. Die Berichtsausgabe griff anschließend auf bereits geschlossene Projektobjekte zu und scheiterte mit `InvalidProjectHandleException` (IDE-Exit 1). Root korrigierte diesen Skriptfehler. **BLOCKED, Wiederholung:** eine inzwischen vorhandene IDE verhinderte den korrigierten Lauf vor dessen Start; sie wurde nicht beendet. Deshalb kein vollständiger Wiederöffnungs-PASS. Eigene IDE-Prozesse sind beendet, VM-Sitzung freigegeben; die bereits vor eigener Nutzung laufende VM blieb laufend.

## Statisches Vertragsdelta und eigenes Adaptermodell

Die exakten FW31-Verbraucher belegen jetzt **22 beobachtete ADI-Slots**. Neu: `Dal_CallDeviceSpecificFunction` reicht die Argumentliste über Slot 29 `VCallDeviceSpecificFunction` (Offset `0x74`) weiter; siehe Evidence mit Callsites und Binaryhashes. Die frühere [21-Slot-Matrix](adi-contract-2026-10-12.md) ist eine historische Teilanalyse.

Die Modulvergleichswerte `0x8801`/`0x8802` sind aus den Beschreibungen gebunden. Sie nehmen im originalen digitalen Scan denselben Bit-15-Schnellpfad wie die alten `0x9001`/`0x9002`; der Pfad ist nicht auf diese alten Werte beschränkt. Terminalinfo32 verwendet intern Selektor 1 und vier 32-Bit-Felder; der Originalverbraucher wählt bei achtbitiger Ausrichtung Byteübertragungen. Das ist ein statischer Pfadbeleg, keine Ausführung mit dem Adapter.

`CmpKbusAsyncCom` nennt `libpackbus.so.1` als DT_NEEDED, importiert aber keine packbus-Funktionen direkt: die betrachteten Wrapper gehen über die originale Managerauflösung zu Dal/VCall. Die eigenen Loaderkonstruktoren des gebundenen packbus initialisieren keinen Bus. Das Mapping der Bibliothek allein beweist daher keinen Hardwarezugriff und rechtfertigt keinen zusätzlichen Originaltreiberersatz. Transitive Dienste und alle erreichbaren Aufrufpfade sind damit noch nicht geschlossen.

[ADR-0004](adr-0004.md) trennt eigene Modellregeln: je ein DI-/DO-Byte, Profile 8/16 getrennt, Mutex plus Thread-/Generationsbindung, logische oder monotone Uhr, vollständige Ausgangsframes, verriegelte Fehler und explizite Recovery. Gültiger neuer Frame allein entriegelt einen Operationsfehler nicht; angeforderte Werte bleiben beobachtbar, wirksame Werte fallen auf null. Diese Regeln sind keine bestätigte WAGO-Semantik. Ein eigener Runtime-Build kann DIGITAL8 und CLOCK_MONOTONIC vorgeben, ohne vom Originalmanager eine eigene Profilwahl-API zu verlangen.

Aktuelle eigene ARM-/Shared-/Defaultprüfungen und Isolationskontrollen stehen im Evidence-JSON. Sie führen ausschließlich Eigenclients/Eigenprovider sowie originalen GNU-Loader/libc aus. **Originaltreiber-, Runtime- und Hardwareakzeptanz NOT_RUN.** Die Python-Suite besteht mit 121 Tests; CI wird am veröffentlichten Commit separat frisch gebunden.

## Konkrete nächste Grenze

Der [Versuchsplan](real-controller-plan-2026-10-12.md) unterscheidet vorhandene Sicherung von noch ungeprüftem Wiederanlauf. Es fehlen der prozessgebundene Loader-/Start-/Stop-Payload mit technisch ausgeschlossenen K-Bus-/UIO-Endpunkten, der sichere Umgang mit Boot-Autostart und eine eigene Modellbrücke: Die originale Runtime ruft unsere `virtual_adi_set_inputs/get_outputs`-Erweiterungen nicht selbst auf. Eigene Harnessaufrufe liefern noch keinen steuerbaren Modellkanal für den Realversuch. Diese konkreten Lücken blockieren den Einbau, nicht weitere Offlinearbeit. Erst ein vollständig gebundener Payload wird separat für Provider-/Busumschaltung vorgelegt; bereits erteilte Softwarefreigaben werden nicht pauschal erneut abgefragt.
