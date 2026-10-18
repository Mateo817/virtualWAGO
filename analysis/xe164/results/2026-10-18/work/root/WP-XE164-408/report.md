> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-408 — Numerische SPI-/ioctl-Aufrufgrenze

Root **Self-Review**. **VERIFIZIERT** sind181 exakte Quellwörter, sieben getrennte Literalwörter und die drei ausgewählten ioctl-Call-Vektoren mit den lokal geschriebenen Bytepositionen. **OFFEN** sind Kernelhandler, tatsächliche Deskriptoren/Speicherinhalte, Runtimebindung, UAPI-/C-Typen und physische Wirkung. Quellprüfung **PASS**; Target-/native Ausführung, Runtime, Geräte, VM und Netzwerk **NOT_RUN**.

Quelle ist FW31 libpackbus.so.1.0.1 mit SHA-256 3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Tatsächliche Metadaten: SPI_ReadWrite ELF aad4..aba0 (204B/51 Wörter), SPI_Command acf8..ad94 (156B/39), SPI_Open adec..aef8 (268B/67), acht externe PLTs zu je3 Wörtern. Ghidra=ELF+10000. Code, Literale, Pfadstring und PLT-Zellen werden an rohen ELF-Bytes geprüft. Alle folgenden Feldpositionen sind reine beobachtete Speicherpositionen, kein erfundener öffentlicher Struct.

ReadWrite und Command speichern r4/LR und reservieren32 weitere Stackbytes; aktuelles SP am ioctl-Call ist EintrittsSP-40. Beide prüfen zuerst Eintrittsr0 auf null und dann signed word[Eintrittsr0+4]<0. Der jeweilige lokale Ablehnungspfad liefert1 ohne ioctl-Call. Ein nonnull Handle ist damit nicht auf Lesbarkeit oder Besitz geprüft.

ReadWrite bereitet r0=aktuelles word[Handle+4], r1=40184b01hex, r2=A=SP+8 vor. Die lokale Region[A,A+24) enthält sechs Worte:
A+0=Eintrittsr1;
A+4=Eintrittsr2;
A+8=Eintrittsr3;
A+c=SP+6;
A+10=SP+7;
A+14=5dchex (1500).
Die beiden adressierten Einzelbytes SP+6/+7 werden vor dem Call0 geschrieben. Die Quelle belegt keine Einheit des letzten Worts. Der tatsächliche Call bei ab30 geht über PLT7b0c; dessen statische JUMP_SLOT-Identität ist ioctl.

Command bereitet r0=aktuelles word[Handle+4], r1=401c4b02hex, r2=A=SP+4 vor. [A,A+28) enthält:
A+0=Eintrittsr1;
A+4=Eintrittsr2;
A+8=Eintrittsr3;
A+c=word[EintrittsSP];
A+10=SP+2;
A+14=SP+3;
A+18=1388hex (5000).
Die adressierten Einzelbytes SP+2/+3 sind lokal0. Das bei ad30 geladene Wort[SP+28hex] ist wegen des40B-Rahmens exakt das Eintritts-Stackwort. Eine fünfte Position ist hier eine numerische Callposition, kein nachgewiesener C-Prototyp.

Nach dem opaken ioctl-Call vergleichen beide Routinen den aktuellen r0 signed gegen den aktuellen r4. Vor dem Call setzt die Quelle r4=0; die Interpretation als Vergleich gegen0 verlangt dessen Erhaltung. Unter dieser Bedingung führen nonnegative Rückgaben lokal zu0. Die Einzelbytes werden im verbleibenden Körper nicht ausgewertet. Command ruft im negativen Fall den errno-location-namigen PLT auf und liefert2 genau bei anschließend gelesenem Wort6ehex, sonst1. ReadWrite besitzt zusätzlich strerror-/syslog-namige Calls vor einem neuen Lesen der aktuellen errno-Zelle; das dann gelesene Wort3dhex oder6ehex ergibt2, andere Werte1. Register-/Rahmen-/Zeigerkontinuität und aktuelle errno-Zellen nach diesen Calls sind Bedingungen. Keine Fehlerkonstanten-Semantik wird aus den Zahlen abgeleitet.

Open bildet den rohen String /dev/kbus0 und übergibt ihn mit zweiter Position2 an den open-namigen PLT. Das ist ein gelesener Artefaktpfad; hier wird keine Gerätedatei geöffnet. Der lokale nonnegative Rückgabepfad erfasst den aktuellen F-Wert inr5 und baut die8B-Region A=SP+10hex:
Halfword A+0=110hex;
Halfword A+2=0;
Word A+4=01312d00hex (20000000).
Die vollständigen8LE-Bytes sind10010000002d3101. Der ioctl-Vektor ist(r0=F,r1=40084b03hex,r2=A).

Wenn die aktuelle ioctl-Rückgabe den lokalen Vergleich mit aktuellem r4=0 besteht, folgt ein write-namiger Call mit(r0=currentr5,r1=SP+c,r2=4), wobei word[SP+c] vorab1 geschrieben wurde. Sein Rückgabewort wird vor der anschließenden numerischen malloc-Anforderung8 nicht getestet. Ein nonnull aktueller Allokationswert bekommt word+0=currentr6 und word+4=currentr5; vor den opaken Calls war r6=1. Die Zuordnung zu1/F erfordert aktuelle GP-/Rahmenwerte nach diesen Calls. Eine tatsächliche Ressourcen- oder Handle-Lebensdauer wird nicht behauptet.

Die numerischen Requestwerte und die lokal beschriebenen Bereiche sind eine konkrete Kandidatengrenze für weitere Originalstackanalyse. Sie belegen noch keinen Kernelvertrag: insbesondere ist nicht bewiesen, welche adressierten Puffer gelesen, geschrieben, zeitlich gehalten oder validiert werden. Die null/negativen lokalen Pfade, das errno-Mapping und die Übergabebytes sind von tatsächlicher SPI-/K-Bus-Wirkung getrennt. Herstellerdateien bleiben privat; keine Implementierung oder Emulatoränderung ist Teil dieses Pakets.

validate.py setzt sys.dont_write_bytecode vor dem lokalen Import, rekonstruiert die181Wort-/7Pooltabellen im Speicher, prüft rohe MOVW/MOVT-Requestwerte, ausgewählte Storeoffsets, den Pfadstring per PT_LOAD und statische PLT-Relokationen. Vollständiges lokales Dateiinventar bleibt beim Standardaufruf unverändert. Der getrennte Builder ist ein Schreiber.
