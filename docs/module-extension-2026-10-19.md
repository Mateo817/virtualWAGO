# Modulerweiterung, 19. Oktober 2026

**VERIFIZIERT / PASS:** Der neue Bytepufferprovider verarbeitet virtuelle
750-1405/750-1504 (16 DI/16 DO) sowie 750-430/750-530 (8 DI/8 DO) mit
Originalruntime, nativem I/O-Manager und originalen I/O-Treibern. Analog und
PWM sind weiter nur als Signalmodell beziehungsweise Engineeringprojekt
qualifiziert. Ihr nativer Lauf ist **NOT_RUN**, die Freischaltung wegen der
unten genannten Vertragslücken **BLOCKED**.

Implementierungscommit: `4faa51aa3ecb13a953e13d368f899ed15413a9b1`, auf
`e3047634b4af7cfffd6d79bd762713f2cfea9537`. Die
[bereinigte Evidence](../evidence/module-extension-2026-10-19.json) bindet
Quellen, private Artefakte, Prüfläufe und Rohbelege per SHA-256. Berichtscommits
ändern diese geprüften Implementierungsdateien nicht. Alte PASS wurden nicht
auf den neuen Provider übertragen.

## Abnahmestufen

| Profil | Eigenes Modell / Transport | CODESYS Build + Reopen | Originalruntime + Originaltreiber | Elektrischer Hardwarevergleich |
|---|---|---|---|---|
| 750-1405 / 750-1504 | PASS, neuer Bytepuffer/V2 | PASS, frisch gebaut | PASS, acht Muster | NOT_RUN |
| 750-430 / 750-530 | PASS, neuer Bytepuffer/V2 | PASS vom 18.10.; unveränderte APP wiederverwendet | PASS, frische Regression mit vier Mustern | NOT_RUN |
| 750-466 / 750-550 | PASS, normale Kanalwerte und getrennte angeforderte/wirksame Ausgänge | PASS, frisches Paarprojekt | NOT_RUN; Register-/Projektionsvertrag BLOCKED | NOT_RUN |
| 750-677 | PASS, vorhandenes eigenes PWM-Frq-Modell erneut getestet | PASS, frischer Mappingprobe | NOT_RUN; untere Projektion und Modusvertrag BLOCKED | NOT_RUN |
| CAN / DALI | Teilprofil weiterhin BLOCKED | Kein neues Teilnehmerprojekt | NOT_RUN | NOT_RUN |

## Bytepuffer und V2

Die Umsetzung folgt [ADR-0008](adr-0008.md). Input, Read-Latch, requested,
staged, Coverage und effective sind begrenzte Bytefelder. 256 Byte pro Richtung
sind eine eigene Implementierungsgrenze, kein Herstellermaximum. Nur DI8 und
DI16 sind im Runtimeprovider auswählbar. Größere Testprofile existieren nur
unter einem beim Runtimebuild ausgeschlossenen Testmakro. Vollständige Bytes
und positive Input-/Outputextents sind erforderlich; reine Input- oder
Outputprofile und Teilbyteprofile werden damit nicht neu freigeschaltet.

ReadStart übernimmt den gesamten Input atomar. WriteEnd veröffentlicht erst
nach vollständiger Bitabdeckung und gültiger Task-/Thread-/Generationsbindung.
Ein fehlendes Bit lässt den bisherigen requested-Frame und Framezähler
unverändert. Ein fremder Aufrufer darf die Transaktion ihres Eigentümers nicht
abbrechen; eine vom Eigentümer verlassene Transaktion benötigt dessen Abschluss
oder einen Lifecycle-Reset. Das ist eine eigene Modellregel.

Der eigene AF_UNIX-SOCK_SEQPACKET-Vertrag ergänzt:

```text
V2 INPUT <DI8|DI16> <generation> <length> <vollständiges lowercase hex>
V2 STATUS
```

INPUT verlangt exakte Profilbindung, kanonische Dezimalzahlen, aktuelle
Generation und vollständige Länge; Erfolg antwortet `OK FRAME`. STATUS
liefert Profil, Extents, sechs vollständige Bytefelder und Lifecyclezustand.
Requests sind auf 600, Antworten auf 4096 Byte begrenzt; abgeschnittene Pakete
werden verworfen. Der alte digitale INPUT/STATUS-Vertrag bleibt erhalten.

Der neue [Frameprüfer](../tools/native_frame_acceptance.py) liest einen
expliziten Vektorplan, öffnet kein Permit und enthält keine IEC-Logik. Nach
INPUT-ACK verlangt er einen beobachteten neuen Read-Latch und danach einen
weiteren vollständigen Ausgangsframe. Ein Prüfer-PASS allein belegt keinen
Originalverbraucher. Dafür wurden zusätzlich PID/Startzeit, Prozessabstammung,
private Namespaces, geladene Originaltreiber, gebundene APP/Provider und eine
native RUN-Abfrage im selben begrenzten Versuch geprüft.

## Tatsächliche digitale Läufe

Frisch gebundene Referenz: **750-8213**, Kernel `6.6.94-rt56-w05.08.02`,
Runtime/CODESYS `3.5.21.50`; vor beiden Versuchen Originalanwendung STOP.
Der ältere 750-8212-Aufbau ist nicht dieses Ziel. Beide Testprojekte verwenden
TCM 0 und einen 20-ms-Task. Die DI16-Descriptors 750-1405 und 750-1504 sind
jeweils `2.0.0.9`; ihre tatsächlich installierten Dateien wurden gehasht.
Der DI16-Builder bindet jetzt stabile Parameternamen statt lokalisierter
Anzeigetexte und prüft WORD-Adressen samt Bitkanälen vollständig.

Die IEC-Probe berechnet `InputWord XOR 16#A596`. Der neue Provider erhielt und
lieferte folgende vollständigen Little-Endian-Frames:

| Input hex | Angefordert hex | Wirksam hex | Akzeptierter Frame |
|---|---|---|---:|
| 0100 | 97a5 | 0000 | 314 |
| 8100 | 17a5 | 0000 | 316 |
| ff00 | 69a5 | 0000 | 318 |
| 0001 | 96a4 | 0000 | 320 |
| 0080 | 9625 | 0000 | 322 |
| 96a5 | 0000 | 0000 | 324 |
| ffff | 695a | 0000 | 326 |
| 0000 | 96a5 | 0000 | 328 |

Alle acht Samples: Generation 1, Permit 0, Fault 0, Watchdog gesund. Der
Frameprüfer benötigte 0,807 Sekunden Host-Monotonzeit bei sechs Sekunden Limit.
Die DI8-Regression prüfte `81→17`, `5a→cc`, `ff→69`, `00→96`; ebenfalls PASS
bei wirksamen Ausgängen 0. Ihr IEC-XOR ist `16#96`. Das ist ein begrenzter
Signalpfadtest, keine exhaustive Prüfung aller Eingangskombinationen und keine
Echtzeit-/Jitterqualifikation.

Die Originalruntime läuft jeweils in eigenen Mount-/Netz-/IPC-/PID-Namespaces.
Originaltreiber bleiben erhalten; der bestehende schreibgeschützte Broker
vermittelt ausschließlich genuine Metadaten derselben Platine. Seine Laufzeit
ist auf 30 Sekunden begrenzt. Physische Bus-/Aktorendpunkte fehlen. Praktische
Isolationsproben vor beiden Läufen bestanden, einschließlich unerreichbarer
eigener Hostlistener. SSH war auf die private exakte Allowlist begrenzt;
das geschützte andere Ziel wurde nie kontaktiert.

Rücknahme nach beiden Versuchen: **PASS**. Original-APP/CRC wurden nicht ersetzt;
der ursprüngliche Configinhalt wurde nach kontrolliertem STOP-Start exakt
wiederhergestellt. Sieben Originaldateien sind hashgleich. Eine zusätzliche
abschließende Abfrage bestätigte genau eine Originalruntime in STOP und keine
Testprozesse. Das frische Backup umfasst Runtimehome und Konfiguration, keinen
RAM-/Retain- oder vollständigen Maschinensnapshot. Die bereits vor Arbeitsbeginn
laufende gemeinsame Windows-VM bleibt entsprechend ihrer Nutzungsregel an;
abschließend waren keine CODESYS-IDE-Prozesse mehr aktiv.

## Analog: implementiert, aber noch kein nativer Zyklus

Der neue 750-550-Standardmodellpfad akzeptiert zwei Little-Endian-WORDs,
bildet dokumentierte Normalwerte auf 0–10 V ab und hält requested und effective
getrennt. Permit ist zunächst geschlossen. Permit-/Fault-Verlust entwaffnet den
Ausgang; Wiederfreigabe benötigt einen neuen vollständigen Modellframe.
Kanalunabhängigkeit, ungültige Werte, atomare Updates und Gate-Rückkehr sind
getestet. Elektrische Last, Status, Sondervarianten und Registerzugriffe werden
nicht simuliert.

Die Normalstützstellen stammen aus dem [WAGO-Handbuch 750-550 V1.1.0](https://www.wago.com/wagoweb/documentation/750/ger_manu/modules/m07500550_xxxxxxxx_0de.pdf).
Rundung zwischen Stützstellen ist eine eigene Modellannahme. Beim 750-466
werden die zwei WORDs ausdrücklich als Vierbyte-Payload bereitgestellt; die
bisherige eigene Sechsbyte-Forschungsdarstellung bleibt separat benannt.

Das frisch gebaute und schreibfrei wieder geöffnete Analogpaar bildet
`%IW1/%IW2` auf `%QW0/%QW1` ab, zwei WORDs pro Richtung, TCM 0, 20 ms.
Der gebundene FW31-Consumer prüft für beide Descriptorprofile zusätzlich
Register 16, 29 und 30. Seine Bedingungen `(R16 & 0x0300)==0`, `R29==0` und
`R30 % 10==0` sind keine semantisch belegten Registerdefaults. Die erneut
geprüften Modulunterlagen schließen diese Lücke nicht. Deshalb gibt es weder
pauschale Nullantworten noch ein freigeschaltetes natives Analogprofil.

Kleinster nächster Schritt: die Bedeutungen und konkrete Konfiguration dieser
Register sowie Status-/Control-/Dummybyte-Projektion am exakt gebundenen
FW31-Pfad belegen. Danach erst ein neuer, eigener 466/550-Nativversuch mit
Normalstützstellen und Kanalunabhängigkeit. Der jetzige Build ersetzt diesen
Versuch nicht.

## PWM: Engineeringprojektion jetzt gemessen

Der erste Buildversuch scheiterte im eigenen Prüfer: CODESYS exportiert die
doppelten reservierten Ausgangsnamen als `_RES 1@1` bis `_RES 4@1`.
Nach Korrektur anhand dieses tatsächlichen Exports bestanden Build und
schreibfreies Reopen. Alle 24 Feldzuordnungen, einschließlich reservierter
Bytes, wurden nativ zurückgelesen; Projekt und Mapping blieben unverändert.

Der genaue Descriptor `07500677000000001616`, Version `2.0.0.3`, ergibt in
diesem IDE-Projekt **16 Byte je Richtung**: Inputbytes 2 bis 17, Outputbytes
0 bis 15. Das schließt die bisher offene Engineering-Paddingfrage für dieses
Projekt. Es bestimmt noch nicht die untere ADI-Projektion gegenüber den
12 Prozessbytes des [WAGO-Handbuchs 750-677 V5](https://www.wago.com/wagoweb/documentation/750/eng_manu/modules/m07500677_00000000_0en.pdf)
und des eigenen Frq-Modells. DC ist der dokumentierte Default, keine hier
gemessene Hardwarekonfiguration. Frq-Moduswahl, Initialisierung, Register- und
Status-/Controlvertrag bleiben **OFFEN**; der native PWM-Lauf ist **NOT_RUN**.

## Tests und Review

- **PASS:** 281 lokale Unittests, keine Skips, mit authentischen lokal
  verfügbaren ADI-/libpackbus-Headern und praktischen Namespaceprüfungen.
- **PASS:** vier eigene ARMHF/QEMU-Harnesses und zwei zusätzlich geladene
  Shared-Provider-Harnesses; Bytegrößen 1/2/4/16/256, Read-Latch,
  vollständige Bit-/Bool-Coverage und fehlendes Bit geprüft.
- **PASS:** Kataloggeneratorprüfung und öffentliche XE164-Snapshotintegrität;
  diese beweist keine neue Firmwaresemantik.
- **Public CI:** Transport-/Pythonprüfungen laufen hardwarefrei. Der neue
  ADI-Bytepuffer-Harness benötigt private Header und ist dort explizit
  **NOT_RUN / skipped**, wenn diese fehlen. Kein Vendorupload als CI-Umgehung.
- **Review:** Root-Self-Review und tatsächlicher separater Offline-C-Review.
  Zwei Befunde wurden vor dem Live-Test behoben: Teilbyte-Extent zulässig trotz
  vollständigem Bytecommit; fehlende Bit-/Bool-Coverage-Prüfung und Testanbindung.
  Der erneute Review bestätigte die Korrekturen. Ein weiterer tatsächlicher
  Offline-Review prüfte das konkrete DI16-Versuchspaket; keine Zielaktionen
  wurden delegiert.

CAN blieb abschließend DOWN/STOPPED bei RX/TX 0. Keine reale oder virtuelle
CAN-/DALI-Kommunikation, kein nativer Analog-/PWM-Zyklus, kein elektrischer
Vergleich und keine allgemeine native Watchdog-/Fehlerqualifikation wurden
in diesem Block ausgeführt.
