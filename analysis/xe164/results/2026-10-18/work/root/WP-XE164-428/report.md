> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-428 — SPI_Init ist lokal callfrei

Root Self-Review, VERIFIZIERT: Im exakten FW31-Backend 3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6 hat SPI_Init laut ELF-Dynsym und REA den8B-Körper ELF a960..a967, Ghidra1a960..1a967. Die beiden Rohwörter sind e3a00000 (MOV r0,0 ohne S) und e12fff1e (BX LR). Bei normalem gültigem Rücksprung setzt dieser lokale Körper ausschließlich r0=0 und verzweigt über den aktuellen LR. Es gibt keinen lokalen Speicherzugriff, keinen Stackaufbau, keinen BL-Aufruf und keine lokale Hardwareoperation. Flags und andere GPR werden von diesen beiden Wörtern nicht verändert; die interworking Rücksprungwirkung des BX richtet sich nach aktuellem LR.

Damit ist die vorherige Offenheit hinsichtlich des Inhalts genau dieses lokalen SPI_Init-Körpers geschlossen. Das allein beweist keine tatsächliche PLT-/Runtimebindung:425s Callsite→PLT→GOT33250-Zuordnung und dieser Symbolkörper müssen zur Laufzeit separat gelten. 425s allgemeine opake SPI_Init-Wirkung darf bei ausdrücklich auf diesen Körper gebundener lokaler Analyse auf diese zwei Instruktionen verfeinert werden. Das macht den gesamten SCPU_Init-/Boot-/Resetvertrag nicht vollständig; Boot, aktuelle Zustände, weitere Aufrufe und externe Seiteneffekte bleiben OFFEN.

validate.py prüft ELF-PT_LOAD-Dateizuordnung und beide Originalwörter sowie REA-Körper/Instruktionsidentität ohne Dateiveränderung. Es ist eine vollständige Prüfung dieses8B-Blatts, keine Laufzeit-/Geräteprüfung. Vendor-native Ausführung, VM, Netzwerk, Hardware NOT_RUN.
