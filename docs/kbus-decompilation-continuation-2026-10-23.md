# Fortgesetzte K-Bus-Dekompilierung

Fortsetzung nach dem [ersten Kernel-/XE164-Block](kbus-kernel-reconstruction-2026-10-23.md).
Die bereitgestellten Offlineartefakte wurden auf Eigentümerauftrag bis zum
Abschluss der konkret belegten Quellenaufgaben untersucht. Der abschließende
Audit identifiziert im untersuchten Umfang keine weitere solche Aufgabe.
Die Ergebnisse sind statische, versionsgebundene Befunde. Vollständiger K-Bus,
aktive Firmware-/Gerätebindung und physisches Verhalten bleiben **OFFEN**.
Keine Geräte-, VM-, Zielnetzwerk- oder Herstellerprogrammausführung.

Neue Quellenbindungen und Prüfungen stehen in der
[separaten Evidence](../evidence/kbus-decompilation-continuation-2026-10-23.json).
Alte eingefrorene Analysepakete und der öffentliche Snapshot vom 18.10. bleiben
erhalten; notwendige Präzisierungen werden ausdrücklich als solche dokumentiert.

## Korrektur der C166-Bitbewegung und Transferzeiger

**VERIFIZIERT:** Für 36 ausgewählte `BMOV`-/`BMOVN`-Instruktionen zeigt
Rizin 0.9.1 Quelle und Ziel gegenüber dem Rohencoding und der lokalen
C166-ISA-Referenz vertauscht an. Die Datenwirkung der installierten
C166-SLEIGH-Definition stimmt mit der Referenz überein; ihre Flagberechnung
verwendet jedoch den alten Zielbitwert, während die Referenz den alten
Quellbitwert verlangt. Daraus wird kein beobachteter Hardwarefehler abgeleitet.
Die installierten Werkzeuge wurden nicht verändert.

Die Korrektur erklärt, dass der Helfer den DPP-Lookup tatsächlich verwendet:
Er übernimmt dessen Bits in den Zeiger. Die vorherige Beschreibung
`7A06→EC40` beziehungsweise `780A→EC46` bezeichnet den **logischen Ursprung**,
keinen unverändert geschriebenen Zeigerwert.

Unter den aktuellen Bedingungen **DPP1=2** und **DPP3=3** sowie der passenden
Lookup-Speicherabbildung ohne Override ergibt sich `7A06→BA06` und
`780A→B80A`. DPP3 ist zusätzlich nötig, weil der Lookup über indirekte
Adressierung bei `FE00+Index` erfolgt. Die statischen Startup-Schreibstellen
allein beweisen diese späteren Zustände nicht. Diese berechneten Adressen sind
**HYPOTHESE** für reale Transferpuffer; exakte Derivat-/SFR-Identität und
physische SPI-/DMA-Zuordnung bleiben offen.

Opcode-/Feldabstände und der `0xd0`-Längengegenbefund des ersten Blocks werden
durch diese Zeigerpräzisierung nicht aufgehoben.

## `0xd0`: vorhandener Code, bislang kein ausgewählter Aufrufer

**VERIFIZIERT, begrenzter Scope:** Acht lokale direkte ARM-Aufrufstellen von
`SCPU_Command` liefern unmittelbar Tags 1/2/3/5 oder lesen Tags 6/7/8/9 aus
einer festen 16-Zeilen-Tabelle. Keine dieser ausgewählten Routen belegt Tag 10.
Die D0-Funktion ist weiterhin exportiert; indirekte, berechnete und externe
Aufrufer bleiben möglich. Sie wird deshalb nicht als global unerreichbar
bezeichnet.

Alle 3.058 regulären Dateien der gebundenen FW31-Partition wurden erneut
schreibgeschützt nach den exakten SCPU-Command-/Codec-Namen untersucht.
Darunter sind 803 Dateien mit ELF-Kennung. Nur `libpackbus` enthält diese
Literalnamen und die passenden Dynsym-/Relokationseinträge. Komprimierte
Mitglieder, berechnete Namen und nicht bereitgestellte Verbraucher sind damit
nicht ausgeschlossen.

Der Export `libpackbus_get_uid` führt zum gebundenen
`GFD_GetModuleIdentNumber`-Aufruf, nicht zu D0. Der D0-Zweig wird daher nicht
allein anhand dieses Exportnamens als UID-Abfrage interpretiert. Konkrete
Registererhaltungsbefunde stützen weiterhin den **bedingten** Host-Erwartungswert
sechs Halbwort; eine tatsächliche D0-Konversation bleibt unbewiesen.

## Kernel: Anmeldung, Steuerbyte und statische Modusauswahl

**VERIFIZIERT, bedingt statisch:** Anmeldecode und tatsächliche Leseroutinen
binden die gefundene Tabelle über `cdev_init`, die Speicherung im aktuellen
cdev und die Übernahme in das aktuelle File an die ioctl-/open-Dispatchstellen.
Die File-Operations-Rolle ist damit stärker belegt als durch benachbarte
Funktionszeiger allein. Dass diese konkreten Objekte auf einem laufenden Gerät
ausgewählt werden, folgt daraus nicht.

Der ausgewählte `kbus_write`-Pfad verwendet `__get_user_1`: Er liest ein
Benutzerbyte und steuert abhängig von Null/Nichtnull den ausgewählten
IRQ-Zustand. Der vier Byte große Userspace-Schreibaufruf ist deshalb kein
Beleg eines vier Byte langen Nutzdatentransfers in diesem Callback.

In allen zehn dekodierten DTBs fehlen `kbus,renesas` und
`kbus,use-dma-always`; `kbus,dma-boost` ist vorhanden. Unter den dokumentierten
Property-/Zustandsbedingungen wählt der Kernel den Infineon-ISR. Aktiver Baum,
Overlays, tatsächliches DMA-Verhalten und elektrischer Zustand bleiben offen.

## Initialisierung und Dateikonfiguration

Der ausgewählte Hauptaufrufer übergibt `SCPU_Init` den Wert 0, ein Testaufrufer
den Wert 1. Im untersuchten Helfer entscheidet dieser Null/Nichtnull-Wert über
den Bootpfad; daraus wird keine Infineon-/Renesas-Auswahl abgeleitet.
`SCPU_GetMode` liest einen aktuellen Zustandswert und selbst keine Hardware-ID.

Die exakte FW31-Datei `kbusconf.xml` ist zusätzlich an Inode, Größe und Hash
gebunden und geparst. Ihre ausgewählten Werte beschreiben PI-/DBus-/Retry- und
Bootwarteparameter. Ein Dateiwert beweist weder Parserpräzedenz noch den
tatsächlich verwendeten Runtimewert.

## Descriptorzählung und tatsächlicher Hostanschluss

**VERIFIZIERT:** Der ausgewählte C166-Scanner erkennt Startmarker aus
Zweibitzellen und legt Datensätze mit sechs Byte Abstand an. Seine Grenze
beträgt 250 Einträge. Vor vollständiger Trailerprüfung veröffentlicht er den
gezählten Wert und die Größe `2*ceil(Markerbitposition/16)` in Byte.
Ein später Fehler kann veröffentlichte Werte stehen lassen; ein erfolgreicher
Null-Startmarker-Pfad kann einen vorherigen Zähler behalten. Die Routine ist
deshalb keine bedingungslose Beschreibung einer aktuellen physischen Bestückung.

Der C0-Zweig kopiert neun Halbwortfelder aus genau diesem Statusbereich.
Der Host speichert sie im Bereich, dessen erstes Halbwort sein Count-Getter
liest. Tags 6 bis 9 berechnen daraus `2*N+6` Empfangsbytes und erwarten
`N` Nutzdatenhalbwörter. Eine feste Tabelle mit 16 Zeilen verteilt diese Werte
auf Hostdatensätze mit 56 Byte Abstand. Bei `N=250` ergeben sich 500 Byte
Nutzdaten, 506 Empfangsbytes und 14.000 Byte Descriptorbereich.

Separate Getter und Schleifentests lesen den aktuellen Zähler erneut.
Die Größen-/Multiplikationsprüfung verwendet außerdem einen vorzeichenbehafteten
32-Bit-Vergleich. Weder ein unveränderlicher Snapshot noch beliebig große
mathematische Produkte werden stillschweigend angenommen. D0 verwendet seinen
festen Erwartungswert weiterhin unabhängig von diesem Count-Getter.

## C166-Arbeitstabellen und Hauptzustände

**VERIFIZIERT, statisch:** Die ausgewählte Initialisierung schreibt vier
veränderliche Datensätze mit je zwölf Byte. Ihre aktuellen Werte beeinflussen
Zähler und latched Statusbits; sie sind keine belegte Identitätstabelle.
Der D0-Code wird dadurch weiterhin nicht als Hardware-ID-Abfrage interpretiert.

Die korrigierte Hauptschleife hat sechs aus ihrer tatsächlichen Sprungtabelle
abgeleitete Zustände für ausgewählte Command-/zyklische Empfangs- und
Sendepfade. Ihre beiden Puffer werden in getrennten logischen Bereichen mit
je 508 Byte explizit genullt. Ein Helfer wertet fünf Bitproben aus; die durch
die ISA-Referenz korrigierten Flags ergeben vier von fünf statt drei von fünf.
Physische Signalnamen, Takt und tatsächliche Abtastwerte bleiben offen.

## Kernel: Completion, Header und begrenzte Wartezeiten

**VERIFIZIERT, bedingt statisch:** Tatsächliche Callback-Schreibstellen verbinden
den ausgewählten OMAP-Treiber mit SPI-Queue, aktuellem Message-/Transferobjekt,
Status-/Längenergebnis und dem oberen Completion-Callback. Erfolgreiche Transfers
addieren die jeweils aktuelle Transferlänge; die ursprünglichen Längen sind
kein unveränderlicher Gesamtvertrag.

Im Commandpfad prüft das ausgewählte Header-Gate Opcode und zwei
Komplementpaare. Die Länge des folgenden Transfers wird ausschließlich auf
`min(aktuelle Länge, 2*Lowbyte(Antwortanzahl))` verkleinert. Bei D0 und einem
angeforderten zwölf Byte langen Tail führt eine Antwortanzahl von 24 deshalb
weiterhin zu zwölf Byte. Dieser Pfad löst den Gegenbefund Firmware 24 gegenüber
Host sechs Halbwort nicht auf.

Die ausgewählte untere Busy-Wartezeit wandelt nichtnegative Parameter mittels
`ceil(n/10)` in Ticks um. Der gebundene Kernel verwendet `HZ=100`; die
Parameter 1.500 und 5.000 entsprechen hier nominell 150 und 500 Ticks.
Queuezeit, obere Completion und weitere Warteabschnitte sind damit nicht
insgesamt begrenzt.

Im PIO-Rohcode sind zusätzlich Statuspolls mit jeweils 100 Tick Budget
vorhanden, einschließlich Gleichheitsfall und letzter Statusnachlese.
Der ergänzende Ghidra-Pseudocode entfernt mehrere dieser Zweige als
unerreichbar. Für diesen Befund gelten daher die erhaltenen Rohinstruktionen.
Steht die Zeitquelle, ist daraus keine reale Sekundengrenze ableitbar.

Der tatsächliche `SPI_Open`-Pfad fordert 16 Bit, Modus 1 und numerisch
20.000.000 an. Die Konfigurationsroute schreibt die Gerätebreite; der belegte
OMAP-Setupanschluss übernimmt sie in den vom PIO-Helfer gelesenen Kanalzustand.
Die getrennte 8-Bit-Metadatenangabe im Command-Transfer überschreibt dieses
Gerätefeld dort nicht. Der bedingte Zustand Kanalbreite 16 / Transfermetadaten 8
ist deshalb quellkonsistent. CPU-Zugriffsbreite, numerische Konfiguration und
physisches Drahtformat bleiben getrennte Nachweisstufen.

Der Takteingang stammt aus einem aktuellen Getter oder dem ausgewählten
48.000.000-Fallback. Die folgende Ganzzahldivision ist inzwischen aus den
Instruktionen belegt; ihre erste Summe verwendet 32-Bit-Wraparound. Das
Rechenbeispiel 48.000.000 / angefordert 20.000.000 ergibt intern 16.000.000.
Es ist keine Messung. Die DMA-Schwelle bleibt ein veränderlicher Parameter.

## DMA, Freigabe und aktuelle Transferlängen

**VERIFIZIERT, bedingt statisch:** Tatsächliche Methodenschreibstellen binden
Konfiguration, SG-Vorbereitung, Submit und Issue an den ausgewählten EDMA-Pfad.
Gemappte und ursprüngliche SG-Eintragszahlen werden an verschiedenen Stellen
verwendet. Der Breitenwert 16 ergibt hier numerisch zwei Byte pro Einheit;
gespeicherte SG-Länge und daraus abgeleitete Parameterfelder bleiben getrennt.
RX-Klone enthalten Metadaten, keine eigenen Kopien des Nutzdatenpuffers.
Ist der Quotient einer einzelnen SG-Länge durch die Einheit 0, schreibt der
Helfer einen besonderen Parameterwert. Die frühere allgemeine
Quotientenformulierung wurde deshalb um diesen Fall ergänzt. Eine große
Gesamttransferlänge beweist keine entsprechende Mindestlänge jedes SG-Eintrags.

Die spätere Freigabe fragt die DMA-Eignung mit der **dann aktuellen**
Transferlänge erneut ab. Der Antwortheader kann diese Länge zwischen Mapping
und Freigabe verkleinern. Bei einem Teilfehler bereinigt der Mapper außerdem
den aktuellen TX-Teil, ohne lokal alle vorherigen Transfers zurückzurollen.
Die erhaltenen Zustandsbeispiele zeigen diese Bedingungen; sie sind keine
ausgeführten Speicherlecks, Fehler oder Race-Nachweise.

Abbruch, Synchronisation, Tasklet-Callback und verwaltete Ressourcenfreigabe
sind bis zu ihren tatsächlichen Methoden-/Objektlesern angeschlossen. Ein
Completion-Signal beweist weiterhin nicht, dass kein Callback mehr folgt oder
dass jede beliebige Teardown-Verschachtelung sicher ist.

## Kopier- und Fehlerrouten der ioctl-Familie

Die Binary-Route und der generische Defaultzweig löschen die aktuelle
K-Bus-Zuordnung im SPI-Objekt bereits **vor** der Anforderungskopie.
Konfiguration, gerahmte Daten und gerahmte Commands schreiben dagegen die
erfasste Zuordnung vor ihrer jeweiligen Kopie zurück. Eine spätere
Kopierfehlermeldung beweist daher keinen unveränderten Modus. Nach der Kopie
neu geladene globale Objekte benötigen weiterhin ihre Identitätsprämisse.

Die Rückgaben unterscheiden sich: Der Binary-Pfad kann auch bei negativem
Sync-Ergebnis eine RX-Kopie über die angeforderte Länge versuchen. Der
generische Nachrichtenpfad überspringt RX bei negativem Ergebnis; jedes
nichtnegative Ergebnis kann dagegen die volle aktuelle Anforderungslänge
kopieren. Sein abschließender Erfolgscount stammt aus der angeforderten Summe,
deren Addition 32-Bit-Wraparound verwendet. Ein lokaler Nullpuffer-Grenzvektor
bleibt ausdrücklich ein bedingtes Quellenmodell, kein beobachteter Angriff
oder Hardwarefehler.

Auch die beiden einfachen Byte-Exporte und ihr 250-Byte-Discardbereich sind
belegt. Der erneute vollständige Dateizensus bindet keinen gewöhnlichen
benannten Verbraucher. Die Puffergröße allein beweist daher keinen erreichten
Überlauf. Die separat gebundene Reset-Sysfs-Route wurde ausschließlich statisch
untersucht; kein Reset wurde ausgelöst.

## C166: Payload, Prüfungen und erzeugte Kopierroutinen

Die C4-Payloadhelfer, drei Descriptorprüfungen, Längen-/Mux-Gates und der
vollständige zyklische Pfad sind jetzt mit ihren tatsächlichen Aufrufern
ausgearbeitet. Prüfgröße in Byte und programmierte Transferanzahl sind an
mehreren Stellen numerisch gleich, ohne dass dies die Einheit des Engines
beweist. Teilweise veröffentlichte Zustände, nicht geprüfte Hilferrückgaben,
erneute Größenlesevorgänge und die Lowword-Multiplikationsgrenze bleiben im
Vertrag erhalten. Ein Initialisierungsreturn 0 beweist deshalb nicht den
Erfolg aller abschließenden Helfer.

Die erzeugten Kopierroutinen laden aus dem Basispuffer und schreiben in den
phasenabhängigen Zielbereich. Die tatsächlichen Stackargumente und der
Far-Aufruf über eine `RETS`-Sequenz sind belegt. Die frühere umgekehrte
Richtungsbeschreibung wurde nach einem unabhängigen **FAIL** korrigiert und
separat erfolgreich nachgeprüft. Das ist keine ausgeführte generierte Firmware.

## Startup, Sprungzeilen und Registerproduzenten

Der Startcode übergibt tatsächlich 128 an den Relokationshelfer. Dieser liest
die Sprungzeilen bei numerisch `E0:0200`, schreibt sie nach `E0:0000` und passt
121 Selbstverweise auf die jeweilige neue Zeilenadresse an. Die sieben anderen
Ziele bleiben erhalten. Das schließt die Software-Verlegung; physische
Interruptauswahl und IRQ-Nummern folgen daraus nicht.

Weitere Initialisierer liefern nun die festen Gegenstellen der beiden
Transferregisterpaare und die Präfixwörter aus aktuellem Kurzregisterwert und
Literal `DEAD`. Die Counterkonfiguration, zwei Register-Schreibprotokolle und
die beiden numerischen Divider-Aufrufe sind getrennt belegt. Ihre Zahlen
ergeben keine gemessenen Baudraten oder Zeitdomänen.

Der Loader verarbeitet einen 16-Bit-Zähler, eine XOR-Summe und Wiederholung
bei Abweichung. Seine Polls besitzen keinen lokalen Timeout und verwenden
teilweise geerbte Registerzeiger. Der Far-Übergang setzt konkrete DPP-Werte,
bevor das Hauptprogramm beginnt. Das ist kein unveränderlicher DPP-Nachweis
für jeden späteren Aufruf.

Die zuvor nur strukturell erfasste Startup-Registerhierarchie ist vollständig
durch ihre tatsächlichen direkten Helfer verfolgt. Ein Nichtnullstatus führt
unter stabilen Registerbedingungen in eine Schleife ohne erneute Prüfung;
der Restore setzt einzelne Felder zurück und verknüpft ein anderes mit einer
Maske. Die echte Tabelle bei `0414` ist an ihren Leser gebunden. Der A0-Zweig
kann außerdem ein RAM-Flag setzen, das die Hauptschleife unter einer weiteren
Bitbedingung später zur Software-Resetinstruktion führt. Quellenkette und
physisch wirksamer Reset bleiben getrennt; diese Analyse führt sie nicht aus.

Der ausgewählte Divider liefert den belegten Quotienten, überschreibt aber
im High-Divisor-Zweig R11 nach einem zwischenzeitlichen Rückladen erneut.
Die frühere Erhaltungsaussage war falsch. Der zweite tatsächliche
Setup-Aufruf setzt R11 ausdrücklich neu auf 0; die ausgewählten numerischen
Setup-Ergebnisse benötigen die falsche Erhaltungsannahme nicht.

## Korrekturen und Reviewgeschichte

Die eingefrorenen Originalpakete und ihre damaligen Validatorergebnisse
bleiben erhalten. Vier unabhängige Befunde werden ausdrücklich fortgeführt:

| Ursprünglicher Befund | Korrektur | Nachprüfung |
|---|---|---|
| Generierte Kopierrichtung in WP470, übernommen in WP471: **FAIL** WP474 | WP478: Basispuffer → Phasenziel | **PASS** WP480 |
| Fehlende Konfigurations-Reassoziation in WP479: **FAIL** WP484 | WP486: tatsächlicher Store vor Kopie | **PASS** WP489 |
| R11-Erhaltung in WP488, übernommen in WP487: **FAIL** WP495 | WP497: tatsächlicher Return-Footprint | **PASS** WP498 |
| Allgemeine SG-Parameterformel in WP490: **FAIL** WP501 | WP506: eigener Fall für Quotient 0 | **PASS** WP507 |

Ein erfolgreicher eigener Validator ersetzt keine Prüfung einer Aussage,
die sein Modell nicht abdeckt. Eigene Quellen-/Modellprüfungen bleiben als
**Self-Review** gekennzeichnet. Die genannten unabhängigen Reviews stammen
von tatsächlich getrennten Workern.

## Prüfstand und weitere Arbeit

Der private kanonische Stand enthält 510 eindeutige Evidence-IDs und 369
Funktionszuordnungen mit zwölf Spalten. Diese Fortsetzung umfasst 55
eingefrorene Pakete mit frisch ausgeführten schreibgeschützten Validatoren:
**PASS**. Mehrere Einträge können dieselbe Routine unter verschiedenen
Versionen, Fragen oder Reviewgrenzen betreffen. Der historische öffentliche
Snapshot vom 18.10.2026 bleibt unverändert.

Der Abschlussaudit gleicht 58 historische C166-Adresseinträge, 91 numerische
Navigationsziele mit 319 Kandidaten-Aufruffeldern und 21 konkrete
Datenwirkungsfragen gegen die Quellenpakete ab. Die Navigationszahlen sind
kein vollständiger Kontrollfluss- oder Codebesitznachweis. Der unabhängige
Audit WP505 ließ die damals noch zugewiesenen Aufgaben ausdrücklich aktiv;
WP504 gleicht deren endgültige Ergebnisse und Korrekturen anschließend ab.
Danach ist im untersuchten Umfang keine weitere konkret belegte, autorisierte
Offline-Dekompilierungsaufgabe identifiziert.

Repositorytests und CI werden an den tatsächlichen Commit beziehungsweise
dessen Baum gebunden; die Ergebnisse stehen beim Draft-PR 11. Eigene
mathematische Modelle bleiben Quellenprüfungen. Tatsächlich geladene Firmware,
aktuelle native Objekte und Policies, Derivat-/SFR-Zuordnung, physischer
Speicher, Interruptauswahl, Drahtformat, Takt und Hardwareverhalten bleiben
**OFFEN / NOT_RUN**. Neue passende Artefakte oder eine separat autorisierte
zielkonkrete Beobachtung können neue Quellenfragen eröffnen.
