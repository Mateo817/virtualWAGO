> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-380 — Quelle der numerischen SSC-Längenpositionen

Root **Self-Review**. **VERIFIZIERT** sind die 957 Instruktionswörter der tatsächlich von Ghidra beobachteten Routine und zehn getrennte Literalwörter sowie die unten begrenzten Adress- und Schreibbeziehungen. **OFFEN** bleiben die vollständige Berechnung aller Werte, die Aufrufbarkeit, tatsächliche Eingabedaten, Effekte opaker Aufrufe und die Bedeutung der Positionen. Quellenprüfung: **PASS**; native Ausführung, Runtime, VM, Netzwerk und Geräte: **NOT_RUN**.

Untersucht wurde ausschließlich die konkrete FW31-Datei libpackbus.so.1.0.1 mit SHA-256 3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Die beiden frischen Metadatenabfragen an Ghidra 0x1c734 und 0x1c77c führen zur Routine mit Einstieg 0x1c5b4, Namen GetCnfFromRail und genau einem beobachteten Bereich [0x1c5b4,0x1d4a8): 3828 Bytes beziehungsweise 957 Wörter. Name und dekompilierte Signatur begründen keinen API-Vertrag. Die zehn nachfolgenden Literalwörter sind kein Bestandteil dieses Codebereichs.

Alle folgenden Adressen sind ELF-VAs; für diese ausgewählten Code-/Literalbereiche entspricht der Dateioffset der ELF-VA, überprüft über die PT_LOAD-Abbildung. Ghidra benutzt zusätzlich 0x10000. Die globale Basis B=0x4013c liegt im BSS; es werden keine Dateibytes an dieser BSS-Adresse erfunden.

Die Literal-/PC-Kombinationen bei c724/c728, c75c/c764, c774/c77c und c988/c990 ergeben unabhängig jeweils B. Zum Beispiel ergibt (c728+8)+word[d4b0] = c730+33a0c = 4013c. Dagegen ergibt c5e4/c5f0 die benachbarte Basis 4017c und c5f8/c5fc die Basis 33000. Diese Adressfamilien werden getrennt geführt.

Nach dem ersten Schleifenabschnitt lädt c71c den aktuellen Index I aus [SP+3c]. Der anschließend ausgewählte Nicht-1-Pfad schreibt bei c734 U32(r10<<3) nach B+U32(I<<4) und bei c740 null an die zugehörige Position +8. Der alternative Pfad ab c984 schreibt bei c9a0 den entsprechend gebildeten Wert an +4 und bei c9a8 null an +c. Die Auswahl benutzt den aktuellen r6 nach den vorgelagerten Abschnitten und gegebenenfalls die Rundung bei c974/c978. Damit ist keine pauschale Abbildung von Eintrittsargumenten auf diese Werte bewiesen.

Der folgende Abschnitt legt B+U32(I<<4) bei c770 in [SP+24] und B bei c780 in [SP+28] ab. Ausgewählte spätere Quellstellen addieren Werte an Position +8 (c894..c89c) beziehungsweise +c (ca44..ca4c). Diese Stores liegen in einem komplexeren Schleifen-/Verzweigungsgraphen. Andere Abschnitte verwenden dieselben Stackpositionen für andere aktuelle Werte; insbesondere dürfen [SP+24] oder [SP+28] nicht im gesamten Funktionskörper als unveränderliche Zeiger behandelt werden. Die tatsächliche Erreichbarkeit und Herkunft jedes aktuellen Registers verlangen eine getrennte Pfadanalyse.

E368s Getter bec4 bildet genau dieselbe Basis B und liefert B+U32(Eintrittsr0<<4). Das ist eine bedingte numerische Produzenten-/Verbraucherbeziehung, kein Beweis für dieselbe Laufzeitinstanz oder die Einheit der vier Wörter. Lokale Indexgrenzen, Aufruferkonfiguration, die beiden RAIL-namigen PLT-Ziele sowie die Helfer bcac/bd74/1c6e8 sind hier nicht aufgeklärt. Aus Namen werden weder Schienendatenformate noch Gerätezugriffe abgeleitet.

Der Quellrahmen reserviert 36 Bytes durch PUSH und weitere 140 Bytes durch SUB SP,#8c. Der ausgewählte Rückkehrblock c8ac..c8b4 setzt r0=0, gibt diese 140 Bytes frei und lädt r4-r11/PC aus dem aktuellen Rahmen. Rahmeninhalt, SP und aktuelle Register nach opaken Aufrufen sind ausdrückliche Bedingungen; keine ABI-Erhaltung wird angenommen.

build_source.py ist der getrennte Schreiber. validate.py importiert nur dessen lesende Funktion, rekonstruiert alle Quelltabellen im Speicher, prüft die Dateiidentität und sechs Literal-/PC-Gleichungen anhand roher A32-Felder sowie die ausgewählten Store-/Epilogwörter. Der Validator schreibt keine Ausgaben. Ein vollständiges Instruktionsmodell oder allgemeiner Konfigurationsvertrag wird damit nicht beansprucht.
