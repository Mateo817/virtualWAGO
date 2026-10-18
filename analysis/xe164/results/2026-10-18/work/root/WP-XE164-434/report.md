> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-434 — gebundener Built-in-Kandidat für die Kernelgrenze

Root Self-Review. VERIFIZIERT sind vier Dateien aus dem exakten FW31-Image49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c, Partition2 Offset25165824/Länge262144000, mit Pfad-/Inode-/Größenbindung aus dem gepinnten145-Inventar16badcbae1785928eb38afbc9329c4dfb75743c979b95dbf6b4706519d90d23e. Extraktion erfolgte über debugfs stat/dump ohne Schreiboption, in einer temporären begrenzten Partitionskopie, ohne Mount. Keine VM, Netzwerk-, Gerät-, Kernel- oder native Herstellerprogrammausführung.

Die gemeinsame Metadatenpfadfamilie lautet /usr/lib/modules/6.6.94-rt56-w05.08.02/. Dies ist eine Artefaktpfadbezeichnung, kein Nachweis des tatsächlich gestarteten Kernels. Gebunden sind modules.builtin inode2197/13128B, modules.builtin.modinfo inode2200/86756B, modules.devname inode2203/92B und modules.alias inode2195/1150B; vollständige Hashes und Pfade stehen in extraction.json.

In modules.builtin steht kernel/drivers/spi/spi-kbus.ko. Die modulbezogenen NUL-Felder der eingebauten Metadaten enthalten spi_kbus.file=drivers/spi/spi-kbus, spi_kbus.description=WAGO KBUS SPI Driver und den Lizenztext GPL v2. Der Parametertext für major beschreibt eine statische Major-Nummer bei nonzero, ansonsten eine dynamische Wahl; parmtype lautet int. Damit existiert ein konkret gebundener Built-in-Metadatenkandidat. Der .ko-Pfad innerhalb modules.builtin bedeutet nicht, dass eine separat vorhandene oder geladene .ko-Datei nachgewiesen wurde.

Die endliche Suche nach kbus/wago/scpu/xe164 betrifft nur die vier gebundenen Dateien und ist in bounded-name-hits.json gespeichert. Einige Treffer betreffen bloße Autoren-/Adresszeichenfolgen; diese werden nicht als Treiberschnittstelle gewertet. Der konkrete Spi-Kandidat ergibt sich aus den zusammengehörigen spi_kbus-Feldern und dem modules.builtin-Eintrag, nicht aus irgendeinem isolierten Namensfund.

OFFEN bleiben: tatsächlicher Kernelstart/Driverbinding, Gerätezuordnung /dev/kbus0 oder /dev/ttyKbus, ioctl-Handler und Requestcodes, Strukturlayout, Callback-/IRQ-/DMA-/Zeitverhalten, konkrete Major-Nummer, Gerätebaumzuordnung und gültiger unterer Ersatzvertrag. Insbesondere werden408s numerische ioctl-Werte und430s TTY-Pfad nicht allein anhand dieses Namens mit dem Kandidaten verknüpft.

Der Inventarstand enthält außerdem /boot/linux inode50/8213856B. Diese Datei wurde in diesem Paket weder extrahiert noch dekomprimiert oder ausgeführt. Eine spätere strikt statische Analyse könnte nach erneuter Identitätsbindung diesen Kandidaten weiter verfolgen. Das ist eine offene nächste Offlinefrage und keine Ermächtigung zu Firmware-/Kernelersetzung.

validate.py kontrolliert Metadatenbytes/Hashes, Inode-/Pfad-/Größenbindung, den endlichen Suchtrefferbestand und die spi_kbus-Felder sowie unverändertes Paketdateiinventar. Die eigentliche Extraktion ist als eigener Schreiber extract_metadata.py getrennt. Ein unabhängiger Review oder eine erneute Extraktion ist separat zu benennen. Integritäts-/Quellenprüfung PASS; tatsächlicher Kernel-/Hardwaretest NOT_RUN.
