# Roadmap und objektive Abnahme

Die Roadmap ist optional zur Produktentwicklung. Ein Meilenstein ist kein PASS allein durch Dokumentation oder viele Mocktests. Pro Ergebnis Quellen-/Binärhashes, Konfiguration, Revision und Nachweisstufe festhalten.

| Stufe | Ergebnis | Abnahme |
|---|---|---|
| M0: Forschungsbasis | Befunde, Quellen, ADR, sichere lokale Übergabe | Dokumente konsistent; private Informationen nicht veröffentlicht |
| M1: Lokaler Bestand und Referenzisolation | Eigenentwicklungscode importiert; freigegebenes neues Gerät eindeutig inventarisiert; Offlinekopien und Backup vorhanden | Paketquellen gegen Manifest geprüft; Tests frisch; Zielrichtlinie und Geräteidentität belegt; geschützte Anlage nicht kontaktiert |
| M2: Tatsächliche Schnittstellengrenze | ELF-/Header-/Konfigurationsanalyse und bounded Referenzbeobachtungen | Aufrufverbraucher, ABI und notwendige Funktionen belegt; Versionsabweichungen sichtbar; ADR bestätigt oder revidiert |
| M3: Minimaler Originalverbraucher | Virtueller 750-1405-/750-1504-Strang unter belegter Grenze | Originalverbraucher akzeptiert Initialisierung und DI/DO; negative Kontrolle; keine physischen Endpunkte |
| M4: Originale Runtime | Unveränderte kleine IEC-Anwendung mit I/O-Mapping | Reale Runtimeausführung, Quelle/Binary gebunden; Ablauf, Restart, Watchdogs getrennt getestet; Rechte geklärt |
| M5: Relevante Klemmenverträge | Analog-/PWM-/Diagnose-/Registerpfade | Handbuch und Referenztraces für genaue Modulrevision; unbekannte Fälle scheitern sichtbar |
| M6: Parallelbetrieb und Regression | Isolierte echte Runtimeinstanzen, automatisierter Programmladevorgang, Trace-/Reset-Steuerung | Ressourcen und Lizenzen pro Instanz; keine Cross-Talk-Effekte; identische I/O-Verträge; Hardwarefreiheit in CI |
| M7: Höhere Originaltreue | Begründete Zeit-/Kernel-/Boarderweiterung | Nur bei nachgewiesenem Nutzen, eigene Abnahmekriterien; keine pauschale Echtzeitbehauptung |

## Nächster zusammenhängender Auftrag

M1 und M2 abschließen und soweit die belegte Schnittstelle und Nutzungsrechte reichen einen begrenzten M3-Kandidaten entwickeln. Nicht beim ersten FW-/Modulunterschied abbrechen: Unterschiede dokumentieren und unabhängig mögliche Offlinearbeit fortsetzen. Keine vorschnelle Voll-Board-Implementierung.

## Erster Testumfang

Originalconsumer statt selbst geschriebenem Ersatz-Client: Geräteinit und Enumeration, DI-Muster, vollständige DO-Frames, Scanreihenfolge, Stop/Restart sowie fehlendes Modul. Mindestens eine bewusst ungültige Geräte-/API-Konfiguration muss den erwarteten Fehler liefern. Ein Original-Herstellerbeispiel kann Vorbereitung sein, qualifiziert aber nicht allein die CODESYS-Runtime.

## Checkzustände

PASS = tatsächlich für den genannten Stand erfolgreich ausgeführt. FAIL = ausgeführt und fehlgeschlagen. NOT_RUN = nicht ausgeführt, Grund nennen. BLOCKED = konkrete Voraussetzung fehlt. Original-Runtime, physische Klemmen, PWM, elektrische Fehler und Last-/Timingmessungen sind beim Bootstrap NOT_RUN. Nutzungsrecht oder fehlende Dateien können einzelne Ausführungen BLOCKED machen.
