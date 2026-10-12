# Nächster Originalstack-Block und Übergabe

Stand: 12.10.2026. Diese Reihenfolge setzt [ADR-0003](adr-0003.md) um. Erstes Ziel ist der Originalstack auf der autorisierten realen Referenz-WAGO: vorhandene CODESYS-Runtime, nativer I/O-Manager und originale WAGO-I/O-Treiber. Eine eigene I/O-Schicht oder ein Ersatzconsumer ist kein Ziel. Eine Simulation wird erst nach Nachweis und Freigabe unterhalb der kleinsten vollständigen Hardwaregrenze eingesetzt. Vollständige Controller-Virtualisierung ist nachgelagert.

## Gegenwärtig bekannte Grenzen

Der [Eigentümerfotobeleg](reference-module-photo-2026-10-12.md) zeigt die Frontartikel und Reihenfolge 750-430 → 750-530 → 750-600. Revisionen, elektronische Zuordnung und Kommunikationszustand bleiben offen. Die 750-1405/750-1504-Kandidaten in bisherigen Offlineprojekten sagen nichts über den echten Bestand aus. Eine Anwendung ist im RAM geladen und gestoppt. Das Arbeitsverzeichnis wurde gelöscht und ein wiederherstellbares Bootprojekt ist nicht gesichert. Deshalb sind Neustart, Löschen, Download oder Überschreiben bis zur sicheren Bestands- und Wiederherstellungsklärung ausgeschlossen.

Softwarearbeit auf dem autorisierten Referenzgerät ist weiterhin erlaubt. Diese Erlaubnis schließt keine Veränderung der geschützten Bus-/Bibliotheksgrenze ein: deren Ersatz benötigt einen konkreten, separat freigegebenen Plan. Eine zusätzliche Lizenz für eine spätere virtuelle Runtimeinstanz ist kein pauschaler Blocker des ersten realen Referenzziels. Root bleibt alleiniger Geräte-/VM-Integrator; kein Netzwerkzugriff aus alten Dokumenten ableiten.

## Block A: Zustand erhalten und Bestand read-only binden

Zuerst aktuellen Gerätezustand, Runtime-/Treiber-/DAL-Versionen und Hashes, laufende Prozesse, Anwendung/STOP-Zustand, verfügbare persistente Projekt-/Bootartefakte und vorhandene Rückkehrmöglichkeiten dokumentieren. Keine Handlung, die RAM-Anwendung oder Wiederherstellungschance verändert. Kläre mit sicheren, nicht-invasiven Quellen die tatsächlichen zwei Module einschließlich Typ, Revision, Position/Reihenfolge und Kommunikation. Keine unklare EEPROM-/Typenschildabfrage und keine Busumschaltung. Halte pro Befund Quelle, Zeit, Version/Hash, Konfiguration, Evidenzstatus und Scope fest.

**Abnahme:** Identität und Zustand sind belastbar gebunden oder jeweilige Lücken explizit OFFEN/BLOCKED; keine zustandsverändernde Operation fand statt. Misslingt eine sichere Identifikation, bleibt diese Teilfrage offen und Offlinearbeit läuft weiter. Der aktuelle Befund wird in [real-controller-observation-2026-10-12.md](real-controller-observation-2026-10-12.md) protokolliert.

## Block B: nativen Original-I/O-Pfad verstehen

Anhand der aktuellen Anwendung, tatsächlich installierten Komponenten, Projekt-/Gerätebeschreibung und sicher lesbarer Runtimebeobachtung klären, welche I/O-Knoten und Originaltreiber aktiv sind und wie Ein-/Ausgänge die Anwendung erreichen. Zuerst nur lesende/risikoarme Beobachtung. Einen eigenen internen IEC-Lauf oder Download nicht beginnen, solange RAM-/Bootzustand und Auswirkungen nicht verstanden sind. Outputwerte und reale Aktorwirkung bleiben getrennt; ohne bestätigte sichere Verdrahtung keine physische Ausgabe.

Vor einem konkreten Test dokumentiert der Integrator Trigger, erwartete Zustände, erlaubte Lese-/Schreibaktionen, sichere Ausgangswerte, Stop-/Rückkehrweg und Abbruchbedingungen. Eigentümerfreigabe für Software gilt; geschützte Bus-/Bibliotheksersetzung, K-Bus-Masterwechsel und Aktortests bleiben eigene Freigabegates.

**Abnahme:** konkreter Originalstack und Anwendungspfad sind versions-/hashgebunden; jede Beobachtung besitzt eng abgegrenzten Scope. Keine Mock-, Offline-Build- oder Adapter-Evidence wird als realer I/O-Nachweis ausgegeben.

## Block C: kleinste ersetzbare Hardwaregrenze belegen

Die bisherigen FW30-Header-, FW31-Verbraucher- und ADI/DAL-Befunde sind historische, quell- und hashgebundene Evidenz. Für genau den aktuellen Stack müssen Verbraucher, Provider, Signaturen/Layout, Aufrufphasen, Größen/Offsets, Rückgaben, Fehlerfälle, Lifecycle, Callback-Lebensdauer, Synchronisation sowie relevante Async-/Register-/Zeit-/Diagnosepfade neu zugeordnet werden. Keine unbekannten Strukturen, Offsets, Modulkennungen oder APIs erraten. ADI/DAL bleibt Kandidat, bis alle für den angestrebten Strang nötigen Pfade belegt sind.

**Abnahme:** jede für den begrenzten realen I/O-Strang benötigte Funktion hat authentische Quelle oder ausreichend begrenzte direkte Evidence; verbleibende Lücken und Auswirkungen sind benannt. Vor Ersetzung der geschützten Bus-/Bibliotheksgrenze liegt ein konkreter separat freigegebener Versuch mit Sicherung und Rollback vor. Fehlt diese Freigabe, bleibt Einbau BLOCKED, während Analyse weitergehen kann.

## Block D: gezielte Simulation unterhalb des Originalstacks

Der reale Zielstrang für die Offline-Vertragsarbeit ist nach Fotobeleg 750-430/750-530 (je acht Kanäle); Abschluss 750-600. Authentische Device Descriptions, Parameter und aktive Mappingbindung sind noch zu schließen. Erst nach Block A–C und Freigabe den qualifizierten Adapter/Modellkern einsetzen. Originalruntime, nativer Manager und originale Treiber bleiben erhalten. Ein bewusst gewählter virtueller 1405/1504-Testbaum bleibt möglich; er wird nicht ohne Gerätebeleg zur Zuordnung des realen Bestands erklärt. Modell beschreibt Signale und physikalische Reaktionen, keine nachgeschriebene SPS-Logik. Angeforderte und wirksame Ausgänge sowie Fehler-/Watchdogreaktion bleiben getrennt.

Zuerst mit vollständiger Isolation gegen den Originalconsumer, dann den originalen Runtime-I/O-Pfad qualifizieren. Keine Hostgeräte, realen Klemmen, Host-D-Bus, Hostservices oder physischen Busse als Fallback. Praktische Netz-, Datei-, Geräte- und IPC-Isolation wird für den konkreten Prozess geprüft; Dokumentation allein implementiert keine Sperre.

**Abnahme:** originale Komponentenpfade bleiben nachweislich aktiv; erwartete Eingangsdaten, vollständige Ausgangsframes, negative Kontrolle und definierte Fehler-/Rückkehrfälle stimmen mit dem belegten Modulvertrag überein. Jeder PASS gilt nur für konkrete Revision, Hashes, Konfiguration und Scope.

## Später: vollständig virtuelle Steuerung

Eine eigenständige virtuelle Runtime/Controllerinstanz folgt erst nach dem realen Referenzpfad. Für sie sind Lizenz-/Ausführungsrechte, Loader-/Service-/Dateisystem-/IPC-/Geräteabhängigkeiten, Zeitverhalten, Ressourcen und Isolation separat zu qualifizieren. Eine zusätzliche Runtime-Lizenz ist kein pauschales Hindernis für die Schritte A–D.

## Historische Befunde

Der [Engineeringbericht](codesys-engineering-2026-10-12.md), [Referenz-ABI-Bericht](reference-abi-2026-10-11.md), [Offline-Blockbericht](originalstack-block-2026-10-12.md) und [Carrier-/Isolationsbericht](offline-carrier-2026-10-11.md) belegen jeweils nur ihren damaligen Stand und Scope. Sie enthalten keinen neuen Nachweis über die aktuell verbundenen Module, den aktuellen RAM-/Bootprojektzustand oder die Simulation unter dem gegenwärtigen Originalstack. Die historische Ausführung einer internen Testanwendung ist kein virtueller I/O-Nachweis.
