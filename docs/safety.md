# Sicherheits- und Zugriffsvertrag

## Drei getrennte Bereiche

1. Hardwarefreier Emulator und CI.
2. Dedizierte neue Test-WAGO als Referenzgerät.
3. Geschützte produktive SPS und ihre Anlage.

Konkrete Adressen und Zugänge stehen im privaten lokalen Paket. Sie werden nicht im öffentlichen Repository gespeichert. Ohne diese lokale Richtlinie gilt für Gerätezugriffe Default-Deny.

## Harte Zielgrenzen

Die geschützte SPS ist kein Leseziel, kein Diagnoseziel, kein Quellgerät und kein Fallback. Auch Ping, Discovery, Portscan, Proxy, Redirect und Kontakt durch gestartete Container/PLC-Programme sind ausgeschlossen. Keine Subnetzscans. Software aus freigegebenen Git-Revisionen oder vorhandenen Offlineartefakten beziehen, nicht von der geschützten SPS kopieren.

Ein lokaler Agent muss vor Verbindungen effektive Zieladresse, Route und Geräteidentität prüfen. Vor Deployments zusätzlich SSH-Hostschlüssel, Artikel/Seriennummer oder gleichwertige Identität festhalten. Ein IP-Text allein reicht nicht für eine gefährliche Änderung. Hostkey-Prüfung nicht pauschal deaktivieren. Alle übernommenen Endpunkte, CODESYS-Ziele, Gateways, Modbus-/OPC-UA-Clients und Autostarts auf alte Zieladressen prüfen.

Diese Regeln allein sind **keine technische Sperre**. Vor aktiven Tests ist eine prozess-/VM-/Netzwerkbereich-begrenzte Egress-Absicherung zu etablieren und offline/mit harmlosen erlaubten Zielen zu prüfen. Geteilte Runner, Netze oder fremde Firewallregeln nicht global verändern. Die geschützte Anlage nicht zum Sperrtest kontaktieren.

Inzwischen setzt [reference_netns.py](network-isolation.md) diese Egress-Sperre für einen eigenen, geprüften Referenzwerkzeugprozess um. Der lokale Kernel-Selbsttest ist PASS für die dokumentierte Revision/Konfiguration. Die Zielrichtlinie allein bleibt eine Vorgabe; eine bloße Plananzeige installiert keine Sperre. Geräte-/Hostkeybindung, elektrische Trennung und sichere Firmware-Dateisystem-/Geräte-/IPC-Isolation sind separate Gates. Das Werkzeug darf keine ungeprüften Hostsocket-/Proxy-/Autostartpfade verwenden und reicht allein nicht zum Firmwarestart.

Die konkrete aktuelle Eigentümeranweisung hat Vorrang vor einer älteren lokalen Übergabe. Eine ausdrücklich gelockerte zusätzliche Windows-Prozessgrenze darf nicht als fortbestehender Blocker ausgegeben werden. Eine solche Änderung ist keine pauschale Erlaubnis zum Überschreiben anderer Geräte oder Originalbestände. Der Emulator-Isolationsvertrag und die private Gerätezuordnung bleiben getrennte Anforderungen.

## Freigaben und Rückfall

Der Eigentümer erlaubt bei Bedarf dieselbe SPS-Software, Gateway und zugehörige Software auf dem neuen Referenzgerät. Diese Softwareinstallation ist nach eindeutiger Gerätezuordnung, Bestandsaufnahme, Backup, physischer Isolation, Quellen-/Artefaktbindung, geprüften Zielparametern und Rollbackplan zulässig. Initialdaten, Autostart und Ausgangswerte vor Start prüfen. Den Ist-Zustand zuerst sichern; eine Installation darf keine relevante Referenzevidence vernichten.

Keine Passwordrotation: vorgegebene Zugangsdaten unverändert lassen. Passwörter nur aus lokalem Secretmaterial benutzen, nicht in Git, Prozessargumenten, Logs, CI oder öffentlichen PRs. Keine Freigabe der Standardzugänge ins Internet.

Firmware-/Bootloaderupdates, Kernel-/Originaltreiberersetzung, K-Bus-Masterumschaltung und physische Ausgangs-/Aktortests benötigen einen separat konkret freigegebenen Plan. Nie zwei K-Bus-Master gleichzeitig. Die Bezeichnung Test-WAGO beweist keine physische Abtrennung von Aktoren. Fehlt dieser Nachweis, ist nur der davon abhängige Versuch blockiert.

Backups mit privaten Schlüsseln, Netzkonfiguration, Lizenzdaten und Originalbinaries bleiben lokal geschützt. Keine Übernahme fremder Geräteidentität oder Lizenzcontainer. Keine unbereinigten Traces in Git.
