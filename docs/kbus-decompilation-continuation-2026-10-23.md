# Fortgesetzte K-Bus-Dekompilierung

Fortsetzung nach dem [ersten Kernel-/XE164-Block](kbus-kernel-reconstruction-2026-10-23.md).
Die Analyse läuft auf Eigentümerauftrag weiter, solange sinnvolle Aufgaben
mit den bereitgestellten Offlineartefakten möglich sind. Die folgenden
Ergebnisse sind statische, versionsgebundene Befunde. Vollständiger K-Bus,
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

Der Gerätedefault schreibt 16 Bit, die Command-Transferobjekte fordern 8 Bit
an. Der PIO-Helfer liest eine aktuelle Kanalzustandsbreite. Deren vollständiger
Override-/Setupanschluss ist noch in Arbeit; CPU-Zugriffsbreite und
physisches Drahtformat werden bis dahin nicht gleichgesetzt.

## Prüfstand und weitere Arbeit

Der private kanonische Stand dieses Zwischenstands enthält 466 eindeutige
Evidence-IDs und 325 Funktionszuordnungen. Alle elf neu aufgenommenen Pakete
besitzen unveränderte Manifeste und frisch ausgeführte schreibgeschützte
Validatoren: **PASS**. Die BMOV-/DPP-Korrektur wurde von einem zweiten
tatsächlichen Worker unabhängig geprüft. Die übrigen neuen Befunde sind als
**Self-Review** samt Root-Integrationsprüfung gekennzeichnet.

Aktiv bleiben Descriptorflags/-checks, C4-Payloadhelfer, DMA-Abbruch und
Ressourcenfreigabe, Transferbreiten-/Taktübernahme sowie die aktuellen
C166-CP-/DPP-Zustände. Eigene mathematische Modelle und Validatoren sind
Quellenprüfungen, keine ausgeführte Firmware. Ein Teilblocker bei
Hardwareidentität stoppt diese unabhängige Analyse nicht.
