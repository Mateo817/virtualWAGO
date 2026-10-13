# Native 750-466: Description, FW31-Verbraucher und offene Grenze

Stand: 13.10.2026. **Self-Review, ausschließlich statische Offlineanalyse.** Keine originale Komponente ausgeführt, keine Geräte-, Netzwerk- oder VM-Aktion in diesem Analyseblock. Originalruntime, nativer Manager und Originaltreiber bleiben gemäß [ADR-0001](adr-0001.md), [ADR-0003](adr-0003.md) und [ADR-0007](adr-0007.md) erhalten. Dieser Bericht implementiert keine native Analogunterstützung.

**VERIFIZIERT:** Die jetzt bereitgestellte originale Description `750-466#04` deklariert zwei Eingangs-WORDs, zusammen vier Prozessbytes. Das ist eine andere Projektion als die sechs Byte des bisherigen Python-Forschungsmodells. Der FW31-Kbus-Verbraucher verlangt für diese nichtdigitale Modulkennung zusätzliche Konfigurationsregister. Der bestehende C-Digitaladapter weist diese Aufrufe ausdrücklich zurück. Ein größerer Bytepuffer allein schließt die native Grenze deshalb nicht.

## Quellenbindung

SHA-256 wurde in diesem Block frisch über die lokalen Originaldateien berechnet. Die zuvor gesicherten Disassemblies von Kbus, packbus und AsyncCom wurden jeweils mit einem frisch erzeugten `arm-linux-gnueabihf-objdump -d`-Ergebnis bytegleich verglichen. Binäradressen unten sind ausschließlich Fundstellen in diesen ELFs, keine Prozessabbild- oder Hardwareoffsets. Herstellerdateien und Rohdisassembly bleiben privat.

| Quelle / Versionsscope | SHA-256 |
|---|---|
| Description `07500466000000000400`, Version `2.0.0.9`, OrderNumber `750-466` | `aa9bb802e2d2656ec9e101f1537aebc23f79487437513bdc9588f0d283ecca51` |
| FW31 `libIoDrvKbus.so.0.0.1` | `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` |
| FW31 `libIoDrvDal.so.1.0.2` | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` |
| FW31 `libpackbus.so.1.0.1` | `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6` |
| FW31 `libCmpKbusAsyncCom.so.0.0.1` | `2564394a5925e6af923843edf8fa93be6a47bdf640d0b6567ed2c3d386e205a7` |
| FW31 `libTscIoDrvKbus.so.0.0.1` | `a861472653c71ff0698497707bb99bfc5b622af89127f928df75517d0c05fdaf` |
| FW31 `libdal.so.1.0.1`, bytegleich mit separat gebundenem FW30-Provider | `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` |
| Gesicherte `kbusconf.xml` | `c840da670a32255f20000621a5cc00b5a5fe8731c6e8b9f916d34b45b1195ca2` |

Der ursprüngliche lokale Descriptionbestand vom 11.10.2026 enthielt noch keine 466-Description. Der Root-Integrator stellte die oben gebundene Datei während dieser Fortsetzung bereit; XML-Inhalt und Hash wurden hier erneut geprüft. Die Descriptorversion und der Name `#04` beweisen keine Revision einer real vorhandenen Klemme. Die gesicherte Firmwarezuordnung ist `04.09.01(31)` gemäß [Referenzbericht](reference-abi-2026-10-11.md). Nur die bytegleiche DAL-Datei erlaubt den dort dokumentierten FW30-Headervergleich; für Kbus, packbus und AsyncCom werden ausschließlich die exakten FW31-Binaries ausgewertet.

## Exakter Descriptorvertrag

**VERIFIZIERT, XML-Deklarationen:** Device Type und ModuleType `32776`; Geräte-ID `07500466000000000400`; Connector `0`, Rolle `child`, Interface `Wago.Kbus`, `alwaysmapping=false`, Slot `allowEmpty=false`; Kategorie `Analog_Input`. Die Beschreibung bezeichnet `2AI 4-20mA SE (4 Bytes)`. Kein anderer 466-/753-466-/Sonderformatdescriptor ist damit eingeschlossen.

| ParameterId | Typ | Richtung / Zugriff | deklarierter Inhalt |
|---|---|---|---|
| `10` | `std:STRING` | `channel=none`, online/offline `none` | Module compare value, Default `'000001D200000000'` |
| `16777216` (`0x01000000`) | `std:WORD` | `channel=input`, online/offline `read` | Input word 1 (`_IW 1`) |
| `16777217` (`0x01000001`) | `std:WORD` | `channel=input`, online/offline `read` | Input word 2 (`_IW 2`) |

Zwei 16-Bit-Eingangsparameter ergeben vier deklarierte Nutzbytes. Es gibt in diesem Connector keine Ausgangsparameter, keine separaten Statusbyteparameter und keine Registerparameter. **OFFEN:** daraus folgen weder tatsächliche ADI-Gesamtgrößen noch Terminalinfo32-Offsets/-Größen, native IEC-Adressen außerhalb des unten gebundenen Offlineprojekts, Railpadding, Prozessbyteordnung oder ein vollständiger Diagnosevertrag. Insbesondere bedeutet „keine Ausgangsparameter“ nicht, dass alle unteren Control-/Registerkanäle der Klemme null Bytes benötigen.

Das [vorher geprüfte Handbuch V1.4.0](module-catalog-sources-2026-10-12.md) beschreibt Statusbyte und Datenwort sowie Diagnosebits im Wort und controllerabhängige Projektion. Dieses Offlineaudit hat das Handbuch nicht neu recherchiert. [ADR-0007](adr-0007.md) bezeichnet sechs Python-Modellbytes `status0/word0LE/status1/word1LE` ausdrücklich als eigene Forschungsprojektion. Diese sechs Bytes dürfen nicht als die vier nativen Descriptionbytes oder als gemessene ADI-Größe übernommen werden. **OFFEN:** welche Wortbits die native Projektion unverändert enthält, wie Status-/RegCom-Bytes gefiltert werden und wie die Originaltreiber Diagnose daraus ableiten.

## FW31-Modulvergleich und Registerpfade

**VERIFIZIERT, statischer Consumerpfad:** `idk_Valid_ModuleCmpValue` ab ELF-Adresse `0x55d0` verlangt 16 Zeichen für den Vergleichsstring. Der interne Parser ab `0x5564` verarbeitet vier Hexzeichen je Gruppe; nichthexadezimale Gruppen ergeben einen negativen Wert. Der Consumer fragt `libpackbus_read_table_9` ab, prüft äußeren und inneren Rückgabewert und vergleicht dessen uint16-Ergebnis mit Gruppe 2. Erst danach entscheidet Bit 15 des Modulwerts, ob die folgenden Konfigregisterprüfungen übersprungen werden.

Für den exakten Default `0000 | 01D2 | 0000 | 0000` ergibt sich folgende **Consumeranforderung**, keine Hardwaremessung und keine Kennungsberechnung aus der Artikelnummer:

| Prüfung | FW31-Fundstelle | konkrete Bedingung dieses Defaults |
|---|---|---|
| `read_table_9(slot, uint16_out)` | `0x5614–0x5648` | Ergebnis muss `0x01D2` sein; äußeres und inneres Ergebnis null |
| Digitalabkürzung | `0x564c–0x565c` | `0x01D2` hat Bit 15 nicht gesetzt; Registerpfad wird erreicht |
| `read_conf_reg(slot, 16, uint16_out)` | `0x571c–0x5754` | `(Register16 XOR 0x0000) AND 0x0300` muss null sein; beide Rückgaben null |
| `read_conf_reg(slot, 29, uint16_out)` | `0x5760–0x5798` | vollständiger uint16-Wert muss `0x0000` sein; beide Rückgaben null |
| `read_conf_reg(slot, 30, uint16_out)` | `0x5690–0x56e0` | Rest der Division durch 10 muss `0` sein; beide Rückgaben null |
| zusätzlicher Register-28-Weg | `0x56e4–0x5718` | nur wenn Register30-Rest `9`; dann Vergleich von Register28 mit Gruppe 4 |

Der Division-/Resthelper `0x7ffc–0x8018` liefert den Rest in `r1`; Register30 wird hier **nicht** pauschal vollständig gegen null verglichen. Die Werte dürfen nicht zu vermeintlichen Fabrikdefaults hochgestuft werden. Register16 außerhalb Maske `0x0300` und Register30 außerhalb der Restbedingung bleiben unbestimmt.

**VERIFIZIERT, statisch:** Der separate Modulsuchpfad `idk_IoDrvScanModules` ab `0x70a4` prüft das Table9-Ergebnis als vorzeichenbehafteten 16-Bit-Wert. Negative Werte nehmen den digitalen Zweig. Nichtnegative Werte erreichen die Registerabfragen 16, 30 und 29, bei Register30-Rest 9 zusätzlich 28 (`0x7384–0x7410`). Der Helper `0x6d24` erhöht den nullbasierten internen Index um 1, ruft `libpackbus_read_conf_reg` auf und vereinigt äußeren/inneren Fehler. Das ist ein weiterer tatsächlich belegter nichtdigitaler Consumerpfad; ein erfolgreicher digitaler Scan qualifiziert ihn nicht.

Der [ADI-Vertrag](adi-contract-2026-10-12.md) bindet für den exakten FW31-packbus die variadischen Argumentformen und Handlerfehler: `read_table_9(uint8 → int, uint16*)`, `read_conf_reg(uint8 → int, uint8 → int, uint16*)`. Table9 meldet unter anderem ungültige Slots/null-Ausgabe/fehlende Kennung; read_conf_reg unterscheidet fehlende Rail, ungültigen Slot, null-Ausgabe und nicht unterstützte Terminal-/Registerkombination. Ein Eigenprovider muss äußeren Dispatchstatus und inneres Operationsergebnis getrennt erhalten. Ein Headername oder ein Erfolgswert für alle Register genügt nicht.

## Zyklus, Status und RegCom bleiben getrennt

**VERIFIZIERT, allgemeiner FW31-Zykluspfad:** `idk_IoDrvReadInputs` verwendet ReadStart (`0x6140/0x6144`) und ReadEnd (`0x6184/0x6188`). Der ausgerichtete Bytepfad verwendet ReadBytes (`0x6468/0x6470`) mit aus nativen Mappingobjekten gewonnenem Offset, begrenzter Größe und Zielpuffer. `idk_IoDrvWriteOutputs` verwendet WriteStart (`0x64c8/0x64cc`) und WriteEnd (`0x6504/0x6508`). Der Treiber besitzt daneben Bit-/Ausrichtungswege. Dieser Bericht rekonstruiert keine CODESYS-Objekte und setzt keine numerischen Prozessoffsets ein. **OFFEN:** die ausgewählte 466-Projektkonfiguration muss diesen allgemeinen Pfad und seine konkreten Datenregionen erst binden.

Das Snapshot-`kbusconf.xml` enthält PI_DESC-Werte CS2 `16611`, CS3 `82147`, CS3_II `721091` und DBUS_IO_CHECK `281319`; DBus-Autopush ist `1`, Intervall `1000`. **VERIFIZIERT** sind genau diese XML-Werte. Sie sind weder Modulgrößen noch eine gemessene wirksame Konfiguration. Das FW31-packbus enthält getrennte PI-Modi mit Controlfilter-/Dummybyte-/Ausrichtungsoptionen; welche Option die vier 466-Nutzbytes tatsächlich auf die untere Rail abbildet, bleibt **OFFEN**. Aus dem CS3-Wert wird hier keine sechs- oder vierbytegroße ADI-Region erfunden.

**VERIFIZIERT, zusätzlich statisch:** FW31-packbus besitzt echte RegCom-Hilfspfade:

- `libpackbus_UpdateInputPiRegCom` (`0x10590`) kann ReadStart aufrufen; der alternative Weg prüft TCM und monotone Zeit und erreicht einen separaten Refresh/ReadEnd-Zweig.
- `libpackbus_UpdateOutputPiRegCom` (`0x10640`) und `libpackbus_LockOutputPiRegCom` (`0x10690`) können WriteStart aufrufen; die Alternative prüft TCM. Release (`0x106e0`) entsperrt zwei ursprüngliche Locks.
- Ein interner Eingangsdispatcher (`0x18544`) benutzt SSC_Open/Get/Close, verdoppelt Offset/Anzahl und kann UpdateInputPiRegCom/ReadEnd einschließen. Der Ausgangsdispatcher (`0x185c0`) benutzt je nach Selektor SSC_PutGet mit Lock/Release oder SSC_Put mit UpdateOutputPiRegCom/WriteEnd. Die Verdoppelung belegt dort Wort-zu-Byte-Umrechnung, keine 466-Region.
- `libCmpKbusAsyncCom` enthält getrennte Kanal- und Start/Poll-Funktionen für Register-/Parameterlesen und -schreiben. Für `fustartrdreg` (`0x0d08`) und `fupollrdregdata` (`0x0d78`) sind indirekte Aufrufe der aufgelösten Originalfunktion mit getrenntem inneren Ergebnis tatsächlich sichtbar; äußere Fehler werden auf 20 abgebildet. Die entsprechenden packbus Start/Poll-Funktionen sind vorhanden, beispielsweise `eAsyncCom_StartReadRegister` (`0x13330`) und `eAsyncCom_StartWriteRegister` (`0x137a8`).

Diese Aufrufbefunde beweisen die Existenz zusätzlicher Zustand-/Zeit-/Lockpfade. Sie liefern **keinen vollständigen ersetzbaren Async-/RegCom-Vertrag**: Operationscodes, Argumenttabellen, Kanalzuordnung, Registerwerte, Start/Poll-Lebensdauer, Timeout, Nebenwirkungen und Callback-/Zyklusüberschneidung bleiben für das ausgewählte 466-Profil offen. Die Behauptung, jeder dieser Pfade werde durch die zwei WORDs zwingend erreicht, wäre ebenfalls unbelegt. Busdiagnose, Analogstatus im Wort, Controlfilter und Registerkommunikation dürfen nicht zusammengefasst werden.

## Self-Review: uint16-Kanal zu begrenzten Bytepuffern

Prüfstand des bestehenden Eigen-C-Codes, frisch gehasht:

| Datei | SHA-256 |
|---|---|
| `tools/adi_digital_adapter.c` | `c0e1de356de1bc2be11b70bca8812971a9deaa4a17c9ce740e323d2e24c57e6b` |
| `tools/adi_digital_adapter.h` | `6c949fcbba1ba3a9925c5c29eac53faac9db10cd8265d36a1d7deacaf64c92ad` |
| `tools/adi_model_bridge.c` | `0aa7bb093b2a8815de235779a3c54f52565d7d20d51262bc8aeb57d92b4ed662` |
| `tools/adi_model_bridge.h` | `cf770961a04cabe086810cc613d7fa78357c8ee361d39831134d4c834511d433` |
| `tools/adi_model_client.c` | `bfdd68636c87f39ea54a204eb314419011da718ce2fae38108f1fb83fde10e79` |
| `tools/adi_catalog_profiles.h` | `3e2c62c302add32418b861ae37b276f8b15353978d2f30762ead8c12558127ba` |

**VERIFIZIERT, Eigenimplementierung:** Eingang, Read-Latch, angeforderte/staged/wirksame Ausgänge und Touchedmaske sind uint16; ReadBytes/WriteBytes serialisieren über lokale Zweibyteframes. Der IPC-Parser akzeptiert ausschließlich dezimales `INPUT` bis UINT16_MAX, und STATUS/Snapshot übertragen uint16. Terminalinfo ist auf zwei digitale Records festgelegt. Größere Größen im Profil ohne die übrigen Änderungen wären speicherunsicher. Header und API sind eigene Modellverträge, keine WAGO-Erweiterung.

**HYPOTHESE, begrenzter Erweiterungsplan:** Eine allgemeine eigene Bytepufferbasis ist offline sinnvoll, sofern sie weiterhin ausschließlich die zwei qualifizierten Digitalprofile freischaltet. [ADR-0008](adr-0008.md) beschließt die gestufte Umsetzung und ihre Abnahmekriterien. Die folgenden Transaktionen und Ablehnungen sind erforderlich:

1. Profile/Modulliste/Größen/Quellhashes vor Init unveränderlich binden. Eingangs-/Ausgangsextents und Terminalzahl mit festen Obergrenzen prüfen. Nicht unterstützte Module einschließlich 466 bis zur vollständigen nativen Bindung ausdrücklich ablehnen; keine automatisch aus dem Pythonkatalog freigeschalteten Kennungen.
2. Ein IPC-Inputframe enthält Protokollversion, Profilbindung, Lebenszyklusgeneration, genaue Länge und begrenzte Bytes. Vollständigen Frame atomar validieren und unter dem bestehenden Lock übernehmen; keine partiell sichtbaren Analogeingänge. Trunkierte/überlange Records, falsche Länge/Generation/Profil, unbekannte Befehle und unzulässige Bytes ablehnen. Bestehende sichere Same-UID-/Socket-/Stopregeln erhalten. Digitales INPUT kann ein expliziter kompatibler Wrapper bleiben.
3. ReadStart kopiert einen vollständigen Inputframe in den Latch; jedes ReadBytes liest daraus. Bereiche mit `offset <= extent` und `size <= extent-offset` prüfen, null Zeiger nur für Nullgröße, Bitzugriffe separat. Task-, Thread- und Lebenszyklusbindung bleiben erhalten. Kein Read darf einen neuen Eingangszustand mitten im Frame sehen.
4. WriteStart eröffnet einen Stagingframe. Byte-/Bitwrites markieren tatsächliche geschriebene Bits in einem begrenzten Coveragepuffer; ein Byteflag allein genügt bei Bitwrites nicht. WriteEnd committet nur die vollständig erforderliche Ausgangsregion atomar. Ungültiger Bereich, fremder Owner, Gateverlust, Watchdogablauf, Reset/Close und unvollständiger Frame dürfen keinen Teilcommit erzeugen. Angeforderte und wirksame Bytepuffer sowie Framecount bleiben getrennt. Verhalten bei null Ausgangsbytes und überlappenden Writes ausdrücklich festlegen und testen.
5. Watchdog-/Permit-/STOP-/Fehlerreaktion auf die gesamte wirksame Region anwenden. Alle Transaktionen bei Generationwechsel invalidieren. Wiederfreigabe verlangt gemäß eigener bestehender Policy einen neuen vollständigen Frame; alte staged Bytes dürfen nicht wieder wirksam werden. Für künftige Analog-/PWM-Ausgänge ist eine Nullbytefolge erst nach Beleg ihrer sicheren modusspezifischen Bedeutung verwendbar.
6. Terminalinfo32, GetIoSizes, Table9, Registerantworten und Profile müssen dieselbe native Projektion beschreiben. Die vier 466-WORD-Nutzbytes weder als sechs Pythonbytes noch als ungeprüfte Railgesamtgröße übernehmen. Nicht modellierte Register/UID/TCM-/RegCom-Operationen bleiben explicit reject; keine Null-/Erfolgsstubs als scheinbare Abnahme.

Nötige Mappingbeweise vor einer späteren 466-Freischaltung: exakter Descriptor plus Projekt-/Konfiguration-/Buildbindung, unveränderter nativer I/O-Baum, beide WORD-Mappings, Reopen-/Buildprüfung, tatsächliche GetIoSizes-/Terminalinfo32-Projektion, native Byteordnung und Status-/Controlfilter, tatsächlich aufgerufene Register mit Werte-/Fehlervertrag und Negativkontrollen. Originalmanagerobjekte bleiben original; fehlende interne Header allein blockieren diesen Pfad nicht. Eigenpuffertests qualifizieren weder Originalconsumer noch Hardware.

## Ergebnis und Restgates

| Prüfung / Aussage | Status dieses Analyseblocks |
|---|---|
| Description-Hash, XML-Parameter, Größen/Richtung | **PASS / VERIFIZIERT**, Offlineparse der exakten bereitgestellten Datei |
| FW31-Binaryhashes und frische Disassemblybindung | **PASS / VERIFIZIERT**, statisch; keine Originalausführung |
| Param10-/Table9-/Registervergleichspfad | **VERIFIZIERT**, statische Consumeranforderung; Registerwerte der Hardware nicht gemessen |
| Self-Review des Bytepuffer-Erweiterungsplans | **VERIFIZIERT**, Reviewstand oben; Umsetzung und neue Tests **NOT_RUN** |
| Native 466 IDE Build und Reopen | **PASS**, separate tatsächliche Root-Engineeringprüfung der unten gebundenen V2-Quelle |
| Vollständiger 466 ADI-/Status-/RegCom-/Mappingvertrag | **OFFEN**; Projektion, Registerwerte/Fehler, relevante Service-/Async-Lebensdauer fehlen |
| Native 466 Originalconsumer-/Runtimequalifikation | **BLOCKED** auf diesen konkreten unteren Verträgen; Ausführung **NOT_RUN** |
| Revision realer 466 / Hardwarevergleich | **OFFEN / NOT_RUN** |

Kein Native466-Stub wurde eingeführt. Die nativen Digital-PASS aus [13.10.2026](native-digital-tests-2026-10-13.md) bleiben auf ihre eigenen Profile und Revisionen beschränkt.

## Separate Root-Engineeringprüfung

**PASS, CODESYS 3.5.21.50:** Ein frisches eigenes Projekt wurde mit der exakten `750-466#04`-Description gebaut, Code und privates Bootartefakt erzeugt und anschließend in einem getrennten IDE-Prozess ohne Save/Build/Onlineaktion wieder geöffnet. Beide Prozesse endeten mit0; keine eigene IDE blieb zurück. Null Fehler und Warnungen, eine zyklische20-ms-Task, TCM41 `std:UDINT` Wert0, beide Moduleingänge als `std:WORD` ohne Unterfelder, Mapping auf vorhandene `Application.PLC_PRG.InputWord1`/`InputWord2` bestätigt. Der gespeicherte CSV-Export enthält `%IW1`/`%IW2`; diese Adressen gelten ausschließlich für dieses Projekt und sind keine unteren Busoffsets. Die eigene IEC-Probe berechnet nur eine Wortsignatur und einen Zähler, keine Ausgangslogik oder Statusantwort.

V2-Builder SHA-256 `d1e7600aa1977c1fd9579a9bf453c25f5191a32fdc2dd89707bd5755fd7e4fd8`; IEC-Quelle `f499b6c11e97e7f520b8008191eb95fc7efe224b98d86d9ec800550bf51766f8`; vorhandener eigener Builderhelper `3de979a473c9ad5c20941352ece7777d1cab306929821ce8dd7ec1cc82448117`. Die ursprüngliche V1-Quelle bestand den Build, enthielt aber einen im unabhängigen Offline-CodeReview gefundenen Reopen-Cleanupfehler. Dieser Pfad wurde mit V1 nicht ausgeführt. V2 korrigiert ihn; eine synthetische Negativkontrolle bestätigt den Erhalt eines vorhandenen temporären Exports. Der V2-Build wurde frisch wiederholt, der folgende Reopen verwendet dieselbe V2-Quelle.

| Privates V2-Artefakt | SHA-256 nach Build und unverändert nach Reopen |
|---|---|
| Projekt | `a42aff27c84173794a2b66e20420f0491fa2239a86ee5167c62d6c0e1d1d3b3f` |
| Mapping-CSV | `14d6342e12896b3085626f530cbab4483adb937b74273fc38b81f3cc460ff9cc` |
| APP | `795e8407b5779dc160bebd4a7fac61441168b02200c3551b6e3a715cdfb1b6d7` |
| CRC | `4f58b4bf60cb313571177fef4806741ec2a1757d10a0cf7dc2736766b287732b` |

Der Reopen exportierte bytegleiches Mapping und prüfte gespeicherten Quelltext, Task, TCM, Geräteidentität sowie alle vier unveränderten Artefakte. Die [bereinigte Evidence](../evidence/native-contracts-2026-10-13.json) bindet Details und private Rawreceipt-Hashes. Projekt/APP/CRC, Rohprotokolle und Herstellerdescriptors bleiben privat. Root kontaktierte in diesem Block keine SPS; der Gerätestatus wurde nicht neu gelesen. Die verwendete IDE-VM wurde anschließend auf Datenträger pausiert und dieser Status frisch bestätigt. Diese tatsächliche Engineeringprüfung ergänzt die statische Analyse; Native466-Provider, Runtimeausführung und Hardwarevergleich bleiben **NOT_RUN**.

## Reproduktion und Offlineprüfung

[`native_descriptor_contract.py`](../tools/native_descriptor_contract.py) liest eine explizite lokale XML-Datei nur bei passendem SHA-256 und gibt ausschließlich Deklarationen sowie unterstützte IEC-Skalarbreiten aus. Unaufgelöste lokale Typen behalten Größe OFFEN; insbesondere werden Serial-Arraygrößen nicht aus Typnamen erraten. Aufruf: `python3 tools/native_descriptor_contract.py PRIVATE_XML --sha256 PIN` mit eigenen privaten Quellenwerten.

[`codesys_native_analog466_probe.py`](../tools/codesys_native_analog466_probe.py) läuft in der installierten ScriptEngine mit `VIRTUALWAGO_PRIVATE_BUILD_DIR` auf einem frischen privaten Verzeichnis und `VIRTUALWAGO_DESCRIPTOR_FILE` auf der gepinnten installierten Beschreibung. Für den getrennten schreibfreien Reopen derselben gespeicherten Artefakte wird `VIRTUALWAGO_REOPEN_ONLY=1` gesetzt. Der verwendete private Launcher prüft zusätzlich IDE-, Profil-, Controller-/Localbusdescriptor- und eigene Quellhashes, lehnt eine bereits benutzte IDE ab und startet keine Online-API.

197 lokale hardwarefreie Tests bestanden ohne Skips, einschließlich tatsächlicher eigener C-/Namespaceprüfungen. Die [Evidence](../evidence/native-contracts-2026-10-13.json) bindet Quellhashes, Testlog und den Scope der als Root ausgeführten Suite. Zwei vorherige Setupaufrufe scheiterten an einem nicht vorhandenen Bubblewrap-Pfad und anschließend am synthetischen TMPDIR unter einem privaten Elternverzeichnis. Der finale Lauf benutzt das vorhandene lokale Bubblewrap und ein eigenes traversierbares Testverzeichnis; private Verzeichnisrechte wurden nicht verändert. Diese Tests belegen weder Native466-Runtime noch Hardware.
