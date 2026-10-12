# Roadmap und objektive Abnahme

Die Roadmap ist optional zur Produktentwicklung. Ein Meilenstein ist kein PASS allein durch Dokumentation oder viele Mocktests. Pro Ergebnis Quellen-/Binärhashes, Konfiguration, Revision und Nachweisstufe festhalten.

| Stufe | Ergebnis | Abnahme |
|---|---|---|
| M0: Forschungsbasis | Befunde, Quellen, ADR, sichere lokale Übergabe | Dokumente konsistent; private Informationen nicht veröffentlicht |
| M1: Lokaler Bestand und Referenzisolation | Eigenentwicklungscode importiert; freigegebenes neues Gerät eindeutig inventarisiert; Offlinekopien und Backup vorhanden | Paketquellen gegen Manifest geprüft; aktuelle 92 hardwarefreie Tests PASS; Zielrichtlinie und Geräteidentität belegt; geschützte Anlage nicht kontaktiert |
| M2: Tatsächliche Schnittstellengrenze | ELF-/Header-/Konfigurationsanalyse und bounded Referenzbeobachtungen | Aufrufverbraucher, ABI und notwendige Funktionen belegt; Versionsabweichungen sichtbar; ADR bestätigt oder revidiert; dynamische Loader-/Servicekette und Komponentenverträge separat schließen |
| M3: Minimaler Originalverbraucher | Virtueller 750-1405-/750-1504-Strang unter belegter Grenze | Originalverbraucher akzeptiert Initialisierung und DI/DO; negative Kontrolle; keine physischen Endpunkte |
| M4: Originale Runtime | Unveränderte kleine IEC-Anwendung mit I/O-Mapping | Reale Runtimeausführung, Quelle/Binary gebunden; Ablauf, Restart, Watchdogs getrennt getestet; Rechte geklärt |
| M5: Relevante Klemmenverträge | Analog-/PWM-/Diagnose-/Registerpfade | Handbuch und Referenztraces für genaue Modulrevision; unbekannte Fälle scheitern sichtbar |
| M6: Parallelbetrieb und Regression | Isolierte echte Runtimeinstanzen, automatisierter Programmladevorgang, Trace-/Reset-Steuerung | Ressourcen und Lizenzen pro Instanz; keine Cross-Talk-Effekte; identische I/O-Verträge; Hardwarefreiheit in CI |
| M7: Höhere Originaltreue | Begründete Zeit-/Kernel-/Boarderweiterung | Nur bei nachgewiesenem Nutzen, eigene Abnahmekriterien; keine pauschale Echtzeitbehauptung |

## Nächster zusammenhängender Auftrag

M1 und M2 bleiben teilweise offen. Device-Descriptions für Controller und Digitalklemmen sind verfügbar; ein eigenes natives Projekt wurde inzwischen mit CODESYS 3.5.21.50 offline fehlerfrei kompiliert. Der [Engineeringbericht vom 12.10.2026](codesys-engineering-2026-10-12.md) bindet diesen Build und den getrennten Keep-Login an ihre Artefakte. Der frühere AppContainer-Test bleibt FAIL, ist nach der aktuellen Eigentümeranweisung aber keine Voraussetzung für die reguläre IDE mehr. Als nächstes fehlen die echten CmpIoDrvItf-/IoConfigConnectorMap- und Plattformheader sowie Lifecycle-/Mappingvertrag. Parallel Hardwareidentität und tatsächlichen Klemmenbestand vervollständigen. Ein begrenzter interner IEC-Lauf auf dem Referenzgerät ist eine gesonderte Engineering-Baseline; er schließt den virtuellen M3-Originalverbraucher nicht ab. Parser-, Compile- und Carrier-Prüfungen qualifizieren nur ihre eigenen Eingaben und Programme.

## Erster Testumfang

Originalconsumer statt selbst geschriebenem Ersatz-Client: Geräteinit und Enumeration, DI-Muster, vollständige DO-Frames, Scanreihenfolge, Stop/Restart sowie fehlendes Modul. Mindestens eine bewusst ungültige Geräte-/API-Konfiguration muss den erwarteten Fehler liefern. Ein Original-Herstellerbeispiel kann Vorbereitung sein, qualifiziert aber nicht allein die CODESYS-Runtime.

## Checkzustände

PASS = tatsächlich für den genannten Stand erfolgreich ausgeführt. FAIL = ausgeführt und fehlgeschlagen. NOT_RUN = nicht ausgeführt, Grund nennen. BLOCKED = konkrete Voraussetzung fehlt. Die 92 hardwarefreien Tests und begrenzten Carrier-/Parser-Probes sind PASS in ihrem jeweils engen Scope; sie sind kein pauschaler Firmware-Sandbox-PASS. Virtueller Originalverbraucher, virtuelle Originalruntime, physische Klemmen, PWM, elektrische Fehler und Last-/Timingmessungen bleiben BLOCKED, NOT_RUN oder OFFEN wie im jeweiligen Nachweis angegeben. Engineering- und Referenz-IEC-Ergebnisse werden getrennt im aktuellen Engineeringbericht geführt.
