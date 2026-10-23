# K-Bus: erweiterte Offlineanalyse vom 23. Oktober 2026

Stand des erweiterten Blocks: **16 neue eingefrorene Pakete; 526 private Evidence-IDs / 385 versionierte Funktionszuordnungen**. Die zuletzt identifizierte Codekapazitätsfrage ist einschließlich unabhängiger Prüfung geschlossen.

## Bezug und Nachweisgrenze

Der Eigentümer hat nach dem begrenzten [Abschlussaudit der bisherigen Hauptpfade](kbus-decompilation-continuation-2026-10-23.md) weitere Arbeit beauftragt. Dieser neue Block erweitert den Umfang um den alternativen SPI-Aufteilungspfad, tatsächliche Speicherpolicy-Schreiber, eine Interpretation des originalen C166-Builders sowie weitere Initialisierungs- und Resetverbindungen. Der frühere Stand bei Commit `e16e8b1badaa6ca28944e954355e48c7906beab1` bleibt ein historischer, begrenzter Prüfstand.

Die [separaten Evidence-Metadaten](../evidence/kbus-offline-extensions-2026-10-23.json) binden jedes neue Paket an Bericht und eingefrorenes Manifest. Die Anzahl der Evidence-IDs und Funktionszuordnungen bezeichnet versionierte Aussagen und Prüfungen; sie ist keine Anzahl einzigartiger vollständig rekonstruierter Funktionen.

Alle neuen Aussagen sind statische, bedingte Quellenverträge oder ausdrücklich eigene Softwaremodelle. Originalprogramme, Kernel, Erfassungsengine, CPU, VM und Geräte wurden nicht ausgeführt. Es gab keinen Zielnetzwerkzugriff, Reset oder Firmwareladevorgang. Herstellerartefakte, Rohlistings, private Modelle und erzeugte Programme bleiben außerhalb des öffentlichen Repositorys. Der öffentliche Snapshot vom 18.10.2026 bleibt unverändert.

## Tatsächlicher Builder statt nachgebildetem Generator

WP510 folgt im eigenen eingeschränkten Interpreter den tatsächlichen Rohinstruktionen des Builders einschließlich seiner Descriptor-, Phasen-, Cache- und Emitterpfade. Die veröffentlichten erzeugten Programme werden anschließend getrennt interpretiert und gegen eine unabhängige bitweise Referenz verglichen. Damit stammen die geprüften Programme aus dem interpretierten Originalbuilder; die frühere Richtung Baseline → Phase wird erneut bestätigt.

**PASS im erklärten Modellumfang:** 305 Referenzvergleiche, alle 445 zugelassenen Instruktionspositionen und 88 von 89 statischen Verzweigungsausgängen. Der fehlende Ausgang benötigt eine zwischen zwei Zugriffen veränderte Anzahl und wird durch die stabilen Eingaben nicht ausgeübt. Emissionsgrenzen, Cachewechsel, leere Intervalle und ein vollständiger Cursorfehlerpfad sind zusätzlich geprüft. Beim untersuchten Cursorfehler wird die voreingestellte Rückkehrroutine veröffentlicht; der unvollständige Programmrest wird im Modell nicht aufgerufen.

Die tatsächlichen `EA?1`-Sprungvarianten benötigen eine erklärte C166S-V2-Prämisse. Das öffentliche Infineon-Handbuch beschreibt Bit 8 als Vorhersageattribut, Bit 9 als gesonderten Prefetch-Hinweis. Das Minuszeichen der Disassemblerdarstellung kehrt die Sprungbedingung damit nicht um. Die generische C166-Konfiguration lehnt diese Variante weiterhin ausdrücklich ab. Das belegt weder die vollständige Identität eines realen Kerns noch Timing oder ISA-Konformität. [Primärquelle: Infineon, Architecture Overview V1.1, gedruckte Seite 49](https://www.infineon.com/assets/row/public/documents/10/56/c166sv2-ao-0103.pdf).

Die unabhängige Prüfung WP517 bestätigt die 305 Ergebnisvergleiche und reproduziert die gesamte ausgewählte Coverage. Sie findet zugleich einen wirklichen Fehler im partiellen Flagzustand des eigenen Modells: AND, OR und BMOV löschen Carry im Handbuch, während WP510 es stehen lässt. **Flagzustandskonformität: FAIL.** Im ausgewählten Call-/Return-Graph wird dieser Carrywert vor seinem nächsten Verbraucher neu definiert; daraus wird kein erfundener Fehler der 305 Ergebnisvergleiche abgeleitet.

Die separate Korrekturschicht WP520 lässt das eingefrorene Original unverändert und löscht Carry für die zehn betroffenen tatsächlichen Instruktionspositionen. 60 neue Zustandskontrollen und die vollständige Wiederholung der ursprünglichen Suite bestehen; deren gesamte Findings bleiben identisch. Das macht den Flagfehler nicht rückwirkend zu PASS. Die unabhängige Prüfung der Korrektur liegt gesondert in WP521.

Aktuelle DPP-/CP-/MD-Zuordnung, gültige getrennte Frames, initialisierte Speicherbereiche, zulässige Phasenzahlen und stabile Werte sind Eingangsprämissen. Ein eigener Rohinstruktionsinterpreter ist keine native Firmwareausführung. Die unabhängigen Prüfungen und Modellkorrekturen sind in den Evidence-Metadaten getrennt ausgewiesen.

## Descriptoren: spätere Flags reparieren keine frühere Rundung

WP515 verfolgt die Erzeugerkette durch frische Initialisierung, Längenerzeugung, spätere Flagbeobachtung und Builder. Bei gesetztem damaligem Bit 7 rundet der Längenerzeuger eine Startdistanz auf ein Vielfaches von acht ab. Der spätere Flagleser ersetzt das ganze Flagwort. Er kann Bit 7 löschen und die Builder-Auswahl setzen, ohne die zuvor gekürzte Länge wiederherzustellen. Ein abschließender Scan im Modus 0 kann diese alten Längen behalten.

Eine ausdrücklich synthetische Zusammensetzung mit erfolgreich angesetzten Helpern, Wartevorgängen und getrennten Eingangswerten passiert die untersuchten lokalen Initialisierungsgates ohne Wiederholung oder Fallback. Dabei endet eine ausgewählte Beschreibung vor dem Start der nächsten ebenfalls ausgewählten Beschreibung. Die unabhängige Prüfung WP518 bestätigt die Quellengates und diese bedingte Zusammensetzung mit eigenen Scan-, Flag- und Bitarithmetikprüfungen.

Der Builder summiert bei solchen aufeinanderfolgenden ausgewählten Beschreibungen die Längen, ohne die nächste Startadresse auf Adjazenz zu prüfen. Deshalb unterscheiden sich das gruppierte Intervall und die einzelnen Descriptorintervalle. Die im Hauptvergleich verwendete Adjazenzprämisse ist notwendig und darf nicht aus einem erfolgreichen Initialisierungsrückgabewert abgeleitet werden.

**OFFEN:** Ob die reale Erfassungsengine die dafür getrennt angesetzten Beobachtungen liefert oder zusätzliche Zusammenhänge erzwingt. Der Quellenmodellfall ist kein Nachweis einer physisch erreichbaren Eingabe und keine Firmwarefehlerbehauptung.

WP519 trennt zusätzlich die Skalargates von den Kopierintervallen. Unter der belegten frischen Normalgeschichte und stabilen späteren Werten sind Stride und Phasenoffsets gerade; die Phasenzahl liegt zwischen eins und vier. Die lokale Produktprüfung begrenzt den nominalen Gesamtbereich auf 4096 Byte, ohne den sonst möglichen Low-Word-Überlauf der Multiplikation. Das beweist zunächst nur die nominale Aufteilung.

Ein weiterer ausdrücklich synthetischer letzter Modus-0-Scan kann Starts und spätere Auswahlflags ändern, während alte Längen und die frühere Mux-Bestimmung bleiben. Die lokalen Produkt-/Trailervergleiche bestehen trotzdem. Das anschließend gruppierte Intervall kann seinen nominalen Stride überschreiten; Quell- und Zielwortmengen können sich überlappen. Die untersuchten Zugriffe bleiben dabei innerhalb eines größeren bekannten RAM-Bereichs. Daraus folgt kein belegter Allokationsfehler, physischer Fehler oder Überschreiten einer nachgewiesenen realen Speichergrenze. Selbst gemeinsame Wörter bedeuten nicht automatisch gemeinsame ausgewählte Bits.

Für die getrennte Baseline-/Phasenreferenz benötigt jede nichtleere Gruppe deshalb zusätzlich einen tatsächlich adjustierten Start und eine nicht übergelaufene Längensumme, deren Intervall vollständig in den `8 × Stride` Bits liegt. Bei geradem Stride liegen dann auch die berührten ganzen Wörter im jeweiligen Abschnitt. Eine Referenz über einzelne Descriptoren braucht darüber hinaus die zuvor erklärte Adjazenz oder einen gesonderten Äquivalenznachweis. Ein erfolgreicher Initialisierungsrückgabewert ersetzt diese Fixturebedingungen nicht.

## Alternativer SPI-Pfad und Rückgabe von Besitz

WP508 untersucht den vorher ausgesparten Modusbit-`1000`-Zweig. Der belegte normale K-Bus-Setupmodus wählt ihn nicht; ein aktiver anderer Schreiber ist damit weder bewiesen noch global ausgeschlossen.

Für stabile gewöhnliche Eingaben zerlegt der tatsächliche Helper längere Transfers in begrenzte Teilstücke. Er verwendet den realen spezialisierten Ersatzhelper, kopiert die Transferrecords und ändert nur die belegten Felder und Listenverbindungen. Nichtnullzeiger und die ausgewählten Metadatenadressen werden um den bisherigen Teilstückoffset erhöht. Das ist zunächst Adressarithmetik; reale DMA-Übersetzung folgt daraus nicht.

Der echte Finalizer verarbeitet die angehängten Ersatzressourcen vom Listenende aus. Diese umgekehrte Reihenfolge erhält die gespeicherten Vorgänger, auch wenn ein Vorgänger selbst ein früheres Ersatzrecord ist. Die Rückgabe stellt die ursprüngliche Listen-/Besitzbeziehung wieder her. Sie ist kein vollständiges Zurückrollen aller Messagebytes: Änderungen an nicht ersetzten Records können bestehen bleiben.

Schlägt eine spätere Ersatzallokation fehl, bleiben frühere Ersetzungen angehängt. Auch eine spätere Validierungsablehnung belegt keine bereits erfolgte Finalisierung. Diese Aussagen gelten unter gültigen nativen Objekten, Speicher-/Kopiereffekten und sequenzieller Besitzführung. Die ausgewählten Partitionsmodelle verwenden positive Maxima 1–32 und stabile Längen 1–4096. Allgemeine Überläufe, Maximalwert 0, beliebige Aliase und die aktuelle Auswahl des Zweigs sind keine stillschweigend geprüften Fälle.

## Speicherinitialisierung: Schreiber und genauer Nullungsumfang

WP509 bindet die tatsächlichen Export- und Bootoptionsrecords für Init-on-Alloc und Init-on-Free, ihre Parser und die konkreten Policy-Schreiber. Zusammen mit dem belegten BSS-Nullungsauftrag ergibt sich ein bedingter 0/1-Verlauf bei erhaltener normaler Bootgeschichte. Ein weiterer Bootschreiber ändert die Allokationsmaske. Das sind mögliche belegte Erzeuger, keine aus der Datei gelesenen aktuellen Laufzeitwerte. Die begrenzte Zeiger-/Registrierungssuche bindet keine konkrete Sysctl-Registrierung an diese vier Eingaben; berechnete Aliase und Module bleiben außerhalb dieser Negativaussage.

WP514 ergänzt den zuvor nur vorausgesetzten Init-on-Free-Vertrag: Bei positiv erfasster Policy, akzeptierter Vorbereitung, passender Seiteneigentümerschaft und erfolgreichen nativen Mapping-/Nullungsvorgängen erhält jede ursprüngliche Seite einen 4096-Byte-Nullungsauftrag. Die ausgewählten unmittelbaren Listenübergaben ändern unter der erklärten Trennung Metadaten und erhalten diesen Nutzdatenumfang.

Das beweist weder den ganzen Freelistbestand noch jede spätere Allokation als null. Ein Buddy-Merge kann unbewiesene Nachbarseiten hinzufügen. Ebenso ersetzt ein späterer positiver Policywert keinen Nachweis, dass gerade diese Seiten zuvor mit aktiver Nullung freigegeben wurden. Mappinggeneration, Seitenidentität, Besitz, weitere Schreiber und tatsächliche native Effekte bleiben Bedingungen.

## Boot, lokale Zustandsrücksetzung und äußere Resetanforderung

WP511 bindet alle tatsächlichen lokalen Guardzugriffe über ihre PIC-Berechnungen. Getter und lokaler Reset betreffen denselben Softwarezustand; die Resetfunktion selbst schreibt nur diesen Guard. Der äußere Initialisierungsfehlerpfad stellt zusätzlich eine getrennte Systemanforderung an den Kernel-Resetpfad.

Die Handshakeanalyse unterscheidet drei abgeschlossene Select-Timeouts von einer garantierten Gesamtdauer. Ein Schreibfehler führt über Logging weiter zu Select. Ein Lesefehler führt weiter zur Prüfung des aktuellen Empfangsbytes. Die Quelle erzwingt an dieser Stelle keine positive Lese-Rückgabe vor dem Bytevergleich. Importeffekte und Erhaltung des zuvor initialisierten Bytes bleiben ausdrücklich Voraussetzungen.

WP516 bestätigt diese kritischen Ketten unabhängig. Der Reviewer inventarisiert auch alle 28 tatsächlichen Speicher-Schreibinstruktionen mit Breite und Bereich. Dabei bestätigt er den ursprünglichen Befund zum lokal ungebundenen Feld und dokumentiert eine Schwäche der alten isolierten Validatorbedingung: Sie erfasste nur einen bestimmten unbedingten Registerstore. Das ist keine Widerlegung der Quellenaussage und kein Umgehen der vollständigen Hash-/Replayprüfungen; WP511 bleibt eingefroren und die stärkere Prüfung liegt separat vor.

WP512 verbindet die äußere Resetanforderung mit den echten Erzeugern von Klasse, Gerät, exportiertem Gerätezeiger und Resetattribut. Erfolgreiche native Registrierung, aktuelle Objektidentität, Sysfs-Mount und Dateierstellung bleiben Voraussetzungen. Nicht jeder Rückgabewert der Erzeugerkette wird lokal geprüft. Aus passenden Quellenidentitäten folgen deshalb weder das aktuelle Vorhandensein der Datei noch ein erfolgreicher physischer Reset.

## Codekapazität bei eingehaltenen Datenbereichsgrenzen

**VERIFIZIERT im erklärten Quellen-/Modellumfang; unabhängiger Review PASS (WP522/WP523).** Ein frischer, zu den belegten Erzeugern passender Quellenzustand kann trotz zulässiger Anzahl, Skalar- und Intervallgrenzen den 8-KiB-Codebereich ausschöpfen. Der frühere direkte Cursorfehlerfall überschreitet die frische Produktgrenze und beantwortet diese Zulässigkeitsfrage nicht.

Der neue bedingte Quellenzustand verwendet 250 Beschreibungen: 125 ausgewählte Gruppen mit je 30 Bit, dazwischen kurze nicht ausgewählte Beschreibungen und zuletzt eine 32-Bit-Beschreibung mit dem belegten Mux-4-Flagmuster. Gemeinsame numerische Flagbeobachtungen und gültige Scantrailer passen zusammen. Die kurzen Beschreibungen ergeben unabhängig vom Wert der ausgewählten 16-Bit-Maskenquelle das angesetzte Flag 0. Der letzte Rundungsschritt erhält die bereits durch acht teilbare Länge 32. Erklärte erfolgreiche Helper-/Wartebedingungen und die übrigen Kontextprämissen bleiben notwendig; eine physische Engineeingabe ist damit nicht nachgewiesen.

Ein Phasenabstand (Stride) von 504 Byte und vier Phasen ergeben nominal 2016 Byte. Alle 125 ausgewählten Gruppen liegen innerhalb der 4032 Bits ihres Stride. Der tatsächliche Builder erzeugt für eine vollständige Phase jedoch `125 × 48 + 10 = 6010` Codebyte. Drei vollständige erzeugte Phasen würden 18030 Byte benötigen. Die Datenbereichsgates liefern deshalb keine Garantie für die getrennte Codekapazität.

Im ausdrücklich eigenen Modell wird Phase 1 vollständig aufgebaut. Phase 2 erreicht die tatsächliche Emissionsgrenze; 957 weitere vierbytegroße Emissionsanforderungen werden abgewiesen. Die Guards verhindern weitere Schreibzugriffe in den erzeugten Code, der Builder kehrt mit Status 2 zurück. Nach dieser Rückkehr steht im fehlgeschlagenen Phasenrecord die voreingestellte Rückkehrroutine; die gespeicherte Position bleibt hinter der vollständigen ersten Routine. Phase 3 wurde beim Abbruch nicht neu aufgebaut. Ihr Default folgt nur aus der ausdrücklich angesetzten vorherigen Initialisierung und deren Erhaltung.

Die Harnesse führen anschließend nur die tatsächlich ausgewählten gültigen Routinen und Defaults in Software aus. Unvollständige Codefragmente werden nicht aufgerufen. Das belegt auch keine tatsächliche zyklische Auswahl bei Fehlerstatus. Aktuelle Phasenpointer werden bereits während des Aufbaus in getrennten Halbwortstores geschrieben. Ein Ausschluss von Zwischenlesern ist damit nicht belegt. Die beschriebene Defaultsicht gilt nach normaler Rückkehr mit den erklärten Erhaltungsbedingungen.

Der bereits in den früheren Paketen 475/476 belegte Initialisierungstail ignoriert den Builder-Rückgabewert. Damit ersetzt Initialisierungsrückgabe 0 weder erfolgreiche Codeerzeugung noch Builderstatus 0. Der neue Fall verbindet diese bekannte Rückgaberegel mit einer zu den Quellenbedingungen passenden Kapazitätsbelastung. Ein beobachteter Gerätefehler oder eine beabsichtigte Hardwaresemantik folgt daraus nicht. Die eingefrorenen Source-/Modellprüfungen und der unabhängige Review bestätigen diesen begrenzten Vertrag. Der Review findet keine weitere konkret gebundene Quellenkante in dieser Erzeuger-/Builderkette; die vollständige Rekonstruktion der Firmware oder Hardwareanbindung bleibt offen.

## Verifikation und Fortsetzung

Jedes angenommene neue Paket besitzt eine frische schreibgeschützte Prüfung seines eingefrorenen Manifests. Eigenprüfung und unabhängige Reviewaussagen sind getrennt. Historische FAILs und ihre früheren Korrekturpakete bleiben erhalten; neue Pakete überschreiben sie nicht. Die maschinenlesbaren Metadaten enthalten den jeweiligen Stand, die Grenzen und die konkrete weitere Frage.

Prüfung dieses veröffentlichten Dateistands: lokal 233 Tests ausgeführt, 232 PASS und ein ausdrücklich ausgewiesener Skip wegen fehlendem bubblewrap. Die Prüfung des unveränderten öffentlichen Snapshots besteht mit 444 IDs, 303 Zeilen, 420 Berichten und 431 Exporthashes. Die Self-Review der fünf einzeln ausgewählten öffentlichen Dateien findet keine privaten Pfade, Gerätedaten, Rohlistings oder Herstellerartefakte. CI wird an den neuen Commit gebunden; frühere CI-PASS werden nicht übertragen.

Die vollständige untere Hardwareanbindung bleibt **OFFEN**. Dazu fehlen insbesondere eine aktuell gebundene Firmware-/Geräte-/Objektidentität, die konkrete Register- und Speicheranbindung, reale Enginebeobachtungen sowie gemessene Zeit-, Draht- und physische Effekte. Weitere Offlinearbeit wird an konkrete noch ungeschlossene Quellenkanten gebunden; dieser Block behauptet keine vollständige Rekonstruktion aller Bytes oder aller möglichen Zustände.
