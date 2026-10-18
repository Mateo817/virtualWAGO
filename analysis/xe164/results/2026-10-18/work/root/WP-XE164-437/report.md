> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-437 — statische Kernelcontainer-Basis

Root Self-Review. VERIFIZIERT ist /boot/linux inode50/8213856B aus demselben FW31-Image49aa85c3..7051c und der gepinnten145-Inventarquelle. Vollständiger extrahierter SHA256:f6e03d6452e4648cd86f58ff5c869af0ebdcc6e8f3123458c73d6e81ccfede65. Readonly debugfs stat/dump auf temporärer begrenzter Partitionskopie, ohne Mount und ohne Gerätezugriff. Kernel wurde weder gestartet noch dekomprimiert.

Der64B-uImage-Header beginnt mit27051956. Gemeldete Nutzlänge8213792 stimmt mit der Restdatei überein; Header-CRC32 nach Nullung des CRC-Felds75c25a9e und Daten-CRC325f20e326 stimmen beide. Rohfelder OS5/Arch2/Type2/Compression0 sowie Name Linux-6.6.94-rt56-w05.08.02 sind in container.json bytegenau gebunden. Load und Entry sind jeweilsffffffff; daraus wird kein realer Startzustand abgeleitet.

Der innere Nutzbereich enthält bei+24hex die ARM-zImage-Kennung016f2818 sowie Start0 und Ende7d5520, dessen Differenz genau8213792B beträgt. Das äußere Compression0-Feld beweist daher keinen bereits dekomprimierten Kernelcode. Zwei Vorkommen der endlichen LZO-Signatur894c5a4f000d0a1a0a liegen bei Dateioffsets467c und488c. Das erste liegt bei statischen Decompressor-Zeichenfolgen und wird nicht als gültiger Stream gewertet. Host-file klassifiziert den zweiten Ausschnitt als lzop1.040/LZO1X-999/Unix; dies ist eine Werkzeugbeobachtung über Kandidatenbytes, kein validierter oder dekomprimierter Stream.

Die Extraktion bindet eine konkrete spätere statische Analysegrundlage an denselben Imagekontext wie434s Built-in-spi_kbus-Metadaten. Sie beweist weder gestarteten Kernel noch tatsächliches Driverbinding, Handleradressen, UAPI/ioctl-Verträge, Gerätezuordnung oder eine zulässige Ersetzung. LZO-Nutzdaten, Code-/Symbolrekonstruktion und Treibervertrag bleiben OFFEN. Native Ausführung, VM, Netzwerk und Hardware NOT_RUN.

validate.py prüft die Artefakthash-/Inode-/Größenbindung, beide CRCs, die inneren Headergleichungen und die endlichen Signaturoffsets ohne Paketveränderung. CRCs sind interne Containerkonsistenz; die Quellenidentität beruht auf den kryptografischen Hashes und der beschriebenen Extraktion. extract_kernel.py und inspect_container.py sind getrennte Schreiber. Ein unabhängiger Review ist separat zu benennen.
