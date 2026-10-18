> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-414 — Anfragebytes und lokale Antwortauswertung

Root **Self-Review**. **VERIFIZIERT** sind122 rohe Quellwörter, vier Literalwörter,13 initiale Opcode-Halfwords sowie die begrenzten Byte-/Prädikatbeziehungen unten. Vollständiger öffentlicher Protokoll-/API-Vertrag, Runtimebindung, gültige tatsächliche Eingaben, Kernel-/Gerätewirkung und ABI bleiben **OFFEN**. Quellprüfung **PASS**; Target-/native Ausführung, Runtime, VM, Netzwerk und Geräte **NOT_RUN**.

Quelle ist FW31 libpackbus.so.1.0.1 mit SHA-256 3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Tatsächliche Metadaten: no-args eaa4..eaec (72B/18 Wörter), one-arg eaf0..eb58 (104B/26), reply eb5c..ec50 (244B/61), last-error ec54..ec74 (32B/8), dazu drei12B-PLTs. Alle vier lokalen Körper sind callfrei. Ghidra=ELF+10000. Nachfolgende Literale sind keine weiteren Codewörter.

Beide Encoder bilden die rohe Tabellenbasis1e6c8 und prüfen unsigned Tag<=12 und nonnull Zieladresse O. One-arg prüft zusätzlich die dritte Position A auf nonnull. Diese Nulltests beweisen keine Lesbarkeit/Schreibbarkeit. Der Ablehnungspfad liefert2 ohne die ausgewählten Ausgabe-Stores.

Die13 initialen Tabellen-Halfwords sind der Reihe nach:
0000,00a0,00a1,00b0,00b1,00c0,00c1,00c2,00c3,00c4,00d0,00fe,00ff.
Ohne Argument schreibt die Quelle Halfword0 nach O+2 und die beiden Bytes des ausgewählten Tabellenwerts low/high nach O+0/+1; lokale Rückgabe0. Mit Argument schreibt sie zunächst die beiden Tabellenbytes, dann Halfword1 nach O+2, liest erst danach das aktuelle Halfword[A] und schreibt dessen low/high Bytes nach O+4/+5; lokale Rückgabe0. Die Quelle beweist dadurch vier beziehungsweise sechs beschriebene Bytes. Sie beweist keinen außerhalb dieser Körper liegenden Header-/CRC-/Kommandonamensatz.

Die Reihenfolge ist bei Aliasen wesentlich: ist A=O+2, wird das gerade geschriebene Halfword1 gelesen, nicht ein früherer Argumentwert. Die gewählten Werte und Adressen brauchen eigene Speicherbedingungen. Die Encoder erlauben Tags11/12; die getrennte SCPU_Command-Auswahl aus406 umfasst aktuell nur Tags0..10. Daraus wird keine Austauschbarkeit ihrer vollständigen Verträge abgeleitet.

Reply liest ohne lokalen Nulltest das Halfword[R+2] und Halfword[R+4]. Vor seiner Statusverzweigung schreibt es low8(word16[R+2]) an die globale Position E+Tag mit E=44410. Erst danach prüft es diesen Bytewert: nonzero liefert1; andernfalls wird N=low8(word16[R+4]) mit der vollständigen aktuellen dritten Position Expected verglichen. Ungleich liefert2. Bei Gleichheit und (N=0 oder vierte Position O=0) liefert die Quelle0 ohne Payloadcopy. Die erste Halfwordposition R+0 wird in diesem Körper nicht geprüft.

Für passende nonzero N und nonnull O kopiert der ausgewählte weitere Pfad N Halfwords von R+6 nach O. Die tatsächliche Reihenfolge ist quellenbestimmt; ein allgemeines Memmove-Verhalten wird nicht angenommen. Insbesondere können überlappende Ziele spätere Reads verändern. Die fast/scalar-Auswahl benutzt U32(O-R-7)>14 und N>=8 als lokale Bedingungen. Dabei ist der zweite Vergleich konditional; die Rohbedingungen, keine ausgedachte Aliasregel, bestimmen den Pfad.

Die Vektorwörter ebd4=f4620a4d und ebdc=f44e0a4d verwenden beide Rm13 und erhöhen den aktuellen Quell-/Zielzeiger jeweils16. GNU objdump zeigt [r2]!/[lr]!, während die behaltene Ghidra-Assembly das Ausrufezeichen auslässt. Unter gültigen aktuellen Adressen verarbeitet die Vektorschleife8*floor(N/8) Halfwords und der folgende skalare Rest N mod8. Der maximale Bytecopyumfang aus dem8-Bit-N-Wert ist510B; damit wird keine reale Puffergröße oder sichere Eingabe bewiesen.

Last-error bildet dieselbe Basis E=44410, liefert für unsigned Tag0..12 den aktuellen Bytewert und für größere Werte0. Reply selbst hat vor dem Store E+Tag keinen solchen Tagbereichstest. Der von SCPU_Command aufgerufene Tag und die Bytefamilie müssen deshalb separat gebunden werden; aus dem lokalen Gettertest wird kein Guard in den Decoder hineingelesen. E ist getrennt von Backend44420 und SCPU34018.

Die konkreten Anfragebytes und Antwortpositionen ergänzen406s Call-Vektoren und408s ioctl-Aufbau. Eine tatsächlich ausgeführte Kerneloperation, eine Antwort des XE164 oder eine vollständige Init-/Transportemulation ist nicht belegt. Weitere Modelle dürfen nur die ausgewählten Quellkörper mit expliziten synthetischen Speicherbildern verbinden.

validate.py schaltet Bytecode vor dem Builderimport aus, vergleicht122Wort-/4Pooltabellen mit den Originalbytes, prüft13 Opcodewerte über PT_LOAD, vier Literal-/PC-Gleichungen, ausgewählte Guard-/Storewörter und Vektor-Writebacks. Es erzeugt keine Ausgaben und kontrolliert sein vollständiges Paketdateiinventar. build_source.py ist der getrennte Schreiber.
