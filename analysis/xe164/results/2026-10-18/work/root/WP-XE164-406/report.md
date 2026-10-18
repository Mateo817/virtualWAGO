> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-406 — SCPU-Aufrufkette zur SPI-Grenze

Root **Self-Review**. **VERIFIZIERT** sind562 Quellwörter,42 getrennte Literalwörter und die begrenzten Handle-/Call-Vektorbeziehungen unten. Vollständige Init-/Exchangeausführung, Hardware-/Kernelvertrag, opake Call-Effekte und Runtime/API/ABI bleiben **OFFEN**. Quellenprüfung **PASS**; Target-/native Ausführung, Runtime, VM, Netzwerk und Geräte **NOT_RUN**.

Quelle ist das genaue FW31-libpackbus3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Tatsächliche Metadaten: SCPU_Init ELF946c..95d8 (364B/91 Wörter), SCPU_Open87b4..8848 (148B/37), SCPU_DataExchange8d90..91ec (1116B/279), SCPU_Command8854..8a9c (584B/146), dazu drei SPI-PLTs je3 Wörter. Symboltabellenlängen enthalten zusätzliche getrennte Literale. Ghidra=ELF+10000; Quellen-/Dateizuordnung wird über PT_LOAD geprüft. Diese Aufnahme übernimmt keine alten FW30-Funktionsverträge pauschal.

Drei Literal-/PC-Gleichungen von Open/Command/Exchange ergeben G=34018. Diese SCPU-Zellfamilie ist verschieden von SSC443f4, Backend44420 und RAIL4442c. Der zunächst von Open gelesene SCPU-Zustandszeiger S0=[G] wird nullgeprüft. Auf dem nullen Pfad liefert Open lokal0 ohne weitere Calls. Sonst folgen acquire-namiger Call(S0+c) und malloc-namiger Request4. Der danach frisch geladene Zustand S1=[currentG] wird im aktuellen nonnull4B-Handle H an H+0 gespeichert.

Open liest den aktuellen Zähler S1+4. Bei0 erreicht es den SPI_Open-PLT75f0; der aktuelle Rückgabewert wird an S1+24hex gespeichert. Danach wird G erneut geladen und das aktuelle SPI-Handlewort auf null geprüft. Auf dem ausgewählten nonnull-Pfad wird der aktuelle Zähler um1 erhöht. Diese Register-/Objektbeziehungen verlangen die jeweiligen aktuellen GP-/Rahmen-/Speicherwerte nach opaken Calls; S0/S1 sind nicht als identisch bewiesen. Das4B-SCPU-Handle und das8B-SPI-Handle aus408 werden ausdrücklich nicht gleichgesetzt.

DataExchange lädt am tatsächlichen Einstieg ohne eigenen Nulltest word[Eintrittsr0] als aktuellen SCPU-Zustand und daraus das Wort+24 als SPI-Handle. Später ruft der ausgewählte Hauptpfad den SPI_ReadWrite-PLT79a4 mit den aktuellen r0..r3-Werten auf. Unmittelbar vor dem Call bei8e7c sind die Moves r0=r10,r1=r8,r2=r11,r3=r9. Früher wurde r9 aus dem Niedrigwortprodukt der beiden RAIL-namigen Rückgaben gebildet. Eine Gleichsetzung dieser späteren aktuellen Register mit ursprünglichen Callrückgaben über alle vorangegangenen opaken Calls wäre eine zusätzliche Bedingung. Die vollständige Puffer-/Retry-/Watchdoglogik wird hier nicht ausgeführt oder als geschlossen behauptet.

Command sichert die vier Eintrittswörter in r6/r5/r7/r4 und reserviert mit36B-Push plus214hex Lokalbereich insgesamt568B. Es bildet die beiden aktuellen Stackadressen Request=SP+8 und Reply=SP+10hex, setzt lokal acht Requestbytes0 und fordert über einen memset-namigen Call das Nullschreiben von200hex Replybytes an. Die tatsächliche Memsetwirkung ist hier opak. Danach liest die Quelle [G]; dessen Nullwert führt zur lokalen Rückgabe4. Deshalb ist diese Nullfortsetzung kein vollständig callfreier Einstiegspfad: der Memset-Call liegt davor.

Unter den aktuellen Register-/Rahmenbedingungen wählt Command anhand des aktuellen r4-Werts den encode-one-arg- oder encode-no-args-namigen Call und setzt den aktuellen Sendelängenwert r10 auf6 beziehungsweise4. Erst danach erfolgt die unsigned Auswahl anhand des aktuellen r5-Tags0..10. Die lokale11-Wort-B-Tabelle bei88c8..88f0 wird getrennt als ausführbarer Code gezählt. Ihre ausgewählten Empfangslängen r11 und Datenzähler r7 lauten:
Tag0/1/4: r11=6,r7=0;
Tag2: r11=8,r7=2;
Tag3/5: r11=24,r7=18;
Tag6/7/8/9: nach einem weiteren RAIL-Count-Call r7=U32(2*currentr0),r11=U32(r7+6);
Tag10: r11=18,r7=12.
Diese Zahlen sind reine Call-Vektorwerte, kein nachgewiesenes Protokollformat oder öffentlicher Kommandonamensatz.

Vor SPI_Command-PLT82b0 bei8944 lädt die Quelle das aktuelle S=word[currentr6], dann r0=word[S+24hex], r1=Request,r2=Reply,r3=currentr10 und word[SP]=currentr11. Damit passen die numerischen Positionen zu408s lokal aufgebautem28B-ioctl-Paket: Handlewort+4 liefert dort einen FD-Wert, die zwei Adressen/Sendelänge/Stacklänge werden in dessen Übergabebereich weitergereicht. Gemeinsamkeit von Runtimehandle, Binding, Speicher und aktuellen Registern ist nicht aus Symbolnamen oder ABI bewiesen.

Nach SPI_Command werden weitere Rückgabe-/Decode-/Loggerpfade durchlaufen. Dieses Paket schließt diese Postcallsemantik nicht; insbesondere sind weder erfolgreiche Antwortbytes noch die tatsächliche Kernelgröße oder ein unabhängiger End-to-End-Status belegt. Die lokale Replyregion hat512B; der berechnete Countpfad weist in diesem Körper keinen danebenstehenden Vergleich der angeforderten Empfangslänge mit512 auf. Daraus wird keine tatsächliche Schreibgröße oder Speicherfehleraussage abgeleitet.

Init enthält clock-/conf-/sleep-/boot-reset-/system-namige Calls und einen internen388B-Helfer bei92c8, dessen Körper hier unexpandiert bleibt. Der gelesene Artefaktstring enthält eine sysfs-Resetkommandozeile. Diese Zeichenfolge wurde nur als Zieldateidatum gelesen: weder sie noch irgendein Geräte-/Reset-/VM-Befehl wurde ausgeführt. SPI-Aufrufe allein beweisen deshalb keinen vollständigen Ersatz aller Init-Nebenwirkungen. Die tatsächlich zu ersetzende untere Grenze braucht weiterhin einen separat belegten Init-Vertrag.

validate.py deaktiviert Bytecode vor dem Builderimport, rekonstruiert562Wort-/42Pooltabellen im Speicher und prüft G-Gleichungen, die drei rohen SPI-PLT-Bindungen, die ausgewählte Command-B-Tabelle und konkrete Move-/Callpositionen. Paketdateien bleiben beim Standardaufruf unverändert. Ein vollständiger CPU-/Runtime-Replay wird nicht beansprucht.
