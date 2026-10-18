> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-390 — SSC-Initialisierung und numerische Handlepositionen

Root **Self-Review**. **VERIFIZIERT** sind 224 exakte Quellwörter und drei getrennte Literale, ausgewählte Allokations-/Publikations- und Handlepositionen sowie die statischen PLT-Beziehungen. Vollständiger Initialisierungsvertrag, tatsächliche Allokationen und I/O, Runtimebindung, API/ABI und physische Wirkung bleiben **OFFEN**. Quellprüfung **PASS**; native Ausführung, Runtime, VM, Netzwerk und Geräte **NOT_RUN**.

Quelle ist ausschließlich FW31 libpackbus.so.1.0.1, SHA-256 3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Frische tatsächliche Metadaten: SSC_Init ELFdd6c..e000, 660B/165 Wörter; SSC_Open e008..e064, 92B/23 Wörter. Die Symboltabellenumfänge enthalten nachfolgende Literale. Zwölf tatsächliche PLTs liefern weitere36 Wörter. Die alten identischen PLT-Aufnahmen aus385 sind in diesem neuen Paket kopiert und ihre Herkunft wird gepinnt. Kein Zielcode wurde ausgeführt.

Die beiden Routinen bilden die Zelladresse G=443f4. Sie ist verschieden von Backend44420, RAIL4442c und SSC-Längenbasis4013c. Init bildet außerdem die statische Adresse1e6a0 für den konfigurationsnamigen Call; damit wird keine aktuelle Konfigurationsdatei gelesen oder ausgewertet.

Init setzt den numerischen Call-Vektor r0=1,r1=74hex für den calloc-namigen PLT. Nach dem opaken Call berechnet es G, schreibt den aktuellen r0-Wert nach G und prüft dessen Nullwert. Der veröffentlichte Wert liegt somit vor den folgenden locknamigen Calls vor. Zwei create-lock-namige Call-Vektoren verwenden die aktuellen Worte[ G ]+2c beziehungsweise+44. Nach dem acquire-namigen Call wird ein Stackwort0 vorbereitet, ein conf-namiger Call mit Adresse1e6a0 und Zahl44ae7hex aufgerufen und das aktuelle Stackwort als zweite Position an den set-description-namigen PLT mit erster Position1 weitergegeben. Diese Calls bleiben hier opak.

Auf dem ausgewählten Null-Rückgabepfad von set-description schreibt der Code3 an die aktuelle Instanzposition+28. Er fordert dreimal numerisch(2ee0hex,1) beim calloc-namigen Ziel an und speichert die aktuellen Rückgabewörter an G+4/+8/+c; diese drei Rückgabewörter werden jeweils auf null geprüft. Anschließend folgen zwei MEM_create_buffer-namige Calls mit erster Position2ee0; deren Rückgaben werden an G+10/+14 gespeichert, ohne lokalen Nullvergleich in diesem Abschnitt.

Dann wird der aktuelle Wert von Instanz+28 mit2ee0 multipliziert. Dieser aktuelle Niedrigwortwert wird zweimal mit zweiter Position10hex an den calloc-namigen PLT übergeben; die Rückgaben werden an den aktuellen Instanzpositionen+8/+c gespeichert. Auch dafür findet zwischen Rückgabe und nachfolgendem Update-Call kein lokaler Nullvergleich statt. Nur wenn die aktuellen Instanz-/GP-Werte nach den opaken Calls noch den zuvor geschriebenen Wert3 enthalten, ist der erste Wert36000 und das Produkt der beiden numerischen Positionen576000. Das ist keine garantierte Speichergröße oder Initialisierungswirkung.

Der folgende SSC_Update-namige Call liefert ein aktuelles r0, das inr7 erfasst wird. Nach dem unlock-namigen Call gibt Init den aktuellen r7 zurück. Fehlerpfade verwenden destroy/free-namige Calls und Nullstores mit aktuellen Registern. Keine Freigabe-, Lock- oder ABI-Wirkung wird aus diesen Namen unterstellt. Die Quelle garantiert hier auch kein durchgängiges identisches Objekt oder voll initialisierte Felder nach jedem opaken Call.

Open prüft **unsigned** Eintrittsr0>3 und liefert auf diesem lokalen Pfad0 ohne weiteren Call. Andernfalls wird I=Eintrittsr0 inr4 gesichert. Es lädt S0=word[G], bildet S0+2c und ruft den acquire-namigen PLT. Nach dessen normaler Rückkehr lädt es S1=word[currentG] neu. Es bildet Q=S1+U32(I<<3), liest word[Q+60] und prüft diesen auf null. Bei null schreibt es I nachQ+5c und S1 nachQ+60 und bereitet den lokalen Ergebniszeiger Q+5c vor. Bei nonnull bereitet es Ergebnis0 vor. Nach unlock wird der aktuelle Ergebniswert zurückgegeben. GleichheitS0/S1, erforderliche GP-/Rahmenwerte und die Bytes nach unlock sind Bedingungen; es gibt vor diesen Quelloperationen keinen lokalen Null-/Bereichstest für S.

Die konkreten positionsweisen Bereiche lauten:
I0: Handlewörter S+5c undS+60;
I1: S+64/S+68;
I2: S+6c/S+70;
I3: S+74/S+78.
Der numerische Init-Request ist74hex=116B, also der Requestbereich[S,S+74). Der von Open zugelassene I3-Pfad adressiert zwei Worte im Intervall[S+74,S+7c), außerhalb dieses numerischen Requestbereichs. Dies ist ein überprüfbarer Vergleich von Request- und Zugriffsoffsets, **kein** Beweis für einen tatsächlichen Speicherfehler: reale Allokationsgröße, Aufrufer, Laufzeitobjektidentität und Call-Erreichbarkeit sind nicht belegt.

Der bereits gepinnte Backend-open-Quellkörper in Root310 enthält vor seinem SSC_Open-PLT831c-Call bei ELF10918 den expliziten MOV r0,#0 bei10910. Somit ist für diese konkrete Callstelle unter normalem Quellweiterlauf I0 die numerische Position, nicht I3. Davor erfolgt ein SSC_Init-PLT7f50-Call bei108e0, dessen Rückgabewort dort nicht durch einen unmittelbaren Vergleich ausgewertet wird; die folgenden globalen Loads gehören einer getrennten Backendzelle. Diese Beobachtung etabliert weder tatsächliche Initialisierung noch einen erfolgreichen Open-Rückgabewert. Andere SSC_Open-Aufrufer sind hier nicht inventarisiert.

Die Source-Getter aus356 benutzen ausgewählte Handlewörter; für deren Anbindung müssen dieselbe Laufzeitinstanz und gültige aktuelle Felder extra bewiesen werden. Ein vollständiger rekonstruierter C-Struct oder öffentlicher Indexvertrag wird aus diesen numerischen Beziehungen nicht definiert. build_source.py schreibt getrennte Tabellen, validate.py rekonstruiert sie nur im Speicher und prüft zusätzlich rohe Instruktionsfelder, PLT-Zellen und die Intervallrechnung.
