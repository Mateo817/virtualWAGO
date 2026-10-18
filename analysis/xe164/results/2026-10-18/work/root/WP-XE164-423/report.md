> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-423 — Stand der belegten unteren Ersatzgrenze

Root Self-Review, private Offline-Synthese. VERIFIZIERT ist die unten referenzierte Quellen- und Nachweiskette in den ausdrücklich begrenzten Stufen. Ein durchgehend laufender Originalstack mit ersetzter Hardwareanbindung ist OFFEN. Runtime, VM, Netzwerk, Kernel, Zielgerät und native Herstellerprogramme: NOT_RUN.

Die bevorzugte Zielrichtung bleibt Runtime plus originaler I/O-Manager und originale I/O-Treiber mit Ersatz nur der belegten unteren Hardwareanbindung. Diese Synthese trifft keine neue Architekturentscheidung und definiert keine öffentliche API. Sie grenzt ab, welche zuvor untersuchten Quellen bereits zusammenpassen und wo ein Vertrag weiterhin fehlt.

## Belegte Stufen und jeweilige Grenze

| Stufe | Tragfähiger Nachweis | Noch fehlende Verbindung |
| --- | --- | --- |
| Manager / Provider | Originale Tabelle O und kopierte Dal-Tabelle D sind getrennt, D+10 wird überschrieben; ausgewählter selector15-Pfad unter expliziten Speicherbedingungen | Tatsächliche Managerobjekt-/Listenidentität, gestarteter Aufrufer und wirksame Laufzeitbindung |
| Provider / Backend | Root323 positioniert sechs zyklische Ziele plus separate Diagnose; C=T+110 genau einmal | Tatsächlicher geladener Backendzustand und gültiger Objektlebenszyklus |
| Dynamischer Aufruf | libffi331/343 sowie353/361 legen ausgewählte Vorbereitung und Zielrückkehr offen; 15 nachfolgend gelesene Wörter sind die stärkere Rückkehrprämisse | Tatsächlicher Fremdfunktionsvertrag, Register-/Stackzustand und nicht ausgewählte Wege |
| SSC-Konfiguration / Kopiertabellen |397/399,400/403,401/402 und405/409/407/416 verbinden reale Anfangszeilen und ausgewählte produzierte Datensätze mit getrennten Hilfereinträgen | Vollständige Eingabeproduktion, Gruppeninitialisierung, Allokatorwirkung und kompletter Update-Erfolg |
| SCPU / Transport |406/411 bindet drei SPI-Ziele und konkrete fünfstellige Command-Aufrufpositionen;414/418 und417 Modelle binden lokale Anfrage-/Antwortbytes | Vollständige Init-/Exchange-/Antwortpfade und aktuelle Zustände über opake Aufrufe |
| SPI / Kernel |408/410 plus412/415/419/420 belegt numerische ioctl-Werte und24/28/8B Argumentbilder | Kernelhandler, tatsächlich gültige UAPI-Strukturen, Seiteneffekte, Zeitverhalten, Fehler-/Resetzustände und reale Antworten |

Die unteren drei numerischen ioctl-Werte lauten ReadWrite 0x40184b01, Command 0x401c4b02 und Open-Konfiguration 0x40084b03. Die Größen24/28/8B sind die lokal beschriebenen Argumentbilder. Sie werden nicht aus Namen oder ioctl-Bitfeldern zu einem vollständigen Kernelvertrag erhoben. Die Open-Konfiguration enthält die Bytes10010000002d3101; deren öffentliche Feldnamen oder Einheiten bleiben unbestimmt.

Ein Ersatz allein dieser drei SPI-Aufrufe ist bislang keine vollständig belegte Init-Ersatzgrenze. SCPU_Init referenziert zusätzlich den unexpandierten lokalen Helfer0x92c8 sowie Konfigurations-/Zeit-/Boot-/Reset-/systembenannte Wege. Die enthaltenen Kommandozeichenfolgen wurden ausschließlich als Artefaktbytes gelesen. Weder ihre tatsächlichen Seiteneffekte noch ihre vollständige Ersetzbarkeit sind aus den SPI-Vektoren bewiesen.

Auch ein erfolgreiches isoliertes GetCnf-Modell beweist keinen gesamten Update-Durchlauf. Root397 zeigt vorgelagerte Nullprüfungen; unter unverändert null bleibendem RAIL-Descriptor kann dieser Aufrufer vor dem modellierten GetCnf stoppen. Die numerische Anfangszuordnung der drei12B-Zeilen ist1/2/3. Ältere künstliche Zuordnung entry1→mapped1 darf nicht mit der tatsächlichen Anfangszeile1→mapped2 gleichgesetzt werden.

Die Trennung von Aufruf und Wirkung bleibt praktisch: Die SPI-Modelle erzeugen exakt beschriebene Stackpuffer und beobachten synthetische Rückgaben; sie erzeugen keine Kernel-/Hardwareantwort. Nach ioctl verbraucht CMP r0,r4 beide aktuellen Register.419s explizite Registerliste nennt nur r4, während die Historien r0 korrekt tragen;420 und die kanonische Qualifikation ergänzen r0. Gesicherte Stackwörter und aktuelle errno-Speicherwerte sind ebenfalls Prämissen, kein aus Symbolnamen abgeleitetes ABI.

Bei den callfreien Codec-Blättern ist eine stärkere lokale Prüfung möglich: Die tatsächlichen Opcodebytes, Store-Reihenfolge, Status-vor-Count-Auswahl,8-Bit-Länge und NEON-Writebacks sind direkt gebunden. Das ersetzt keine zulässigen realen Puffergrößen, keine vollständige Kommandosemantik und keine Antwort des XE164.417s Noargs-Prosa nennt die Store-Reihenfolge falsch;414s Rohquelle schreibt O+2 zuerst. Der getrennte Review421 entscheidet die Modellhistorien; diese Synthese übernimmt nur die Rohquellenreihenfolge.

## Konkrete verbleibende Offlinefragen

1. Die zusätzlichen unteren Init-Wege einschließlich Helfer92c8 müssen eingegrenzt werden, bevor ein vollständiger Transportersatz behauptet wird.
2. Für einen Kernelersatz fehlen eindeutig gebundene Handler/UAPI und die tatsächlich gelesenen/geschriebenen Puffer einschließlich Fehler-, Timeout- und Lebenszyklusbedingungen.
3. Gruppeninitialisierung und Appends benötigen getrennte Nachweise; aus einem Modell mit bestehendem D/A und N=0 folgt keine reale Erreichbarkeit des zuvor untersuchten Nullzählerpfades.
4. Die tatsächliche Originalmanager-/Provider-/Backendbindung bleibt von Dateigleichheit und ausgewählten synthetischen Pfaden getrennt.

Die Quellenbindung verwendet ausschließlich unveränderliche Paketberichte und das exakte FW31-Backend. validate.py prüft deren Hashes und die endliche Sechsstufen-Tabelle; dies ist eine Integritätsprüfung der Synthesebasis, keine erneute unabhängige CPU-, Protokoll- oder Hardwareprüfung. Ein unabhängiger Review der Synthese ist gesondert zu benennen.
