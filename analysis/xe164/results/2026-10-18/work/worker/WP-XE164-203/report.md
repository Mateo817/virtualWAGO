> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-203 — slots +0x0c/+0x10

## Ergebnis

Status: VERIFIZIERT für beide REL-Addends, Relocationstypen, Ghidra-importierten Werte und die von Ghidra beobachteten Funktionskörper; OFFEN für eine Runtimeadresse und die Semantik der aufgerufenen Funktionen.

Die hashgebundene Eingabe libdal.so.1.0.1 hat SHA-256 c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5 (PASS). Sie ist ELF32 little-endian ARM ET_DYN / ARM EABI5. Objektbasis aus E-XE164-228: ELF-Linkadresse 0x14154. Daher sind die ausgewählten Wörter 0x14160 (+0x0c) und 0x14164 (+0x10).

| Position | Datei-Offset | Rohbytes (little-endian) | REL-Eintrag | Raw REL-Addend A / ELF-Ziel-VA | Ghidra-importierter Wert |
|---|---:|---|---|---:|---:|
| Basis +0x0c = 0x14160 | 0x4160 | bc 32 00 00 | R_ARM_RELATIVE, r_offset=0x14160, r_info=0x00000017, Symbolindex 0 / kein Symbol | 0x000032bc | 0x000132bc bei Ghidra-Adresse 0x132bc |
| Basis +0x10 = 0x14164 | 0x4164 | 7c 32 00 00 | R_ARM_RELATIVE, r_offset=0x14164, r_info=0x00000017, Symbolindex 0 / kein Symbol | 0x0000327c | 0x0001327c bei Ghidra-Adresse 0x1327c |

Rohbytes in .data bei Datei-Offsets 0x4160/0x4164 und gleichadressierte Einträge in .rel.dyn belegen die Slots. R_ARM_RELATIVE verwendet den impliziten Addend im Zielwort. Die Ghidra-Werte entsprechen 0x10000 + A; Ghidras beobachtete Image Base ist 0x10000. Das ist die Analyseabbildung, keine gemessene Runtimebasis. Der Runtimewert hängt von der tatsächlichen, unbekannten Ladebasis ab; eine Runtimeadresse wird nicht angegeben.

## Direkte Ziele und Körpergrenzen

Ghidra 12.1.4 identifiziert beide Ziele als nicht extern und nicht thunk. Die Namen FUN_000132bc und FUN_0001327c sind automatisch erzeugte Analysebezeichner und keine API-Verträge. In der Symboltabelle gibt es keinen exakten benannten Symboltreffer für 0x32bc oder 0x327c.

- Addend 0x32bc → ELF-Ziel-Link-VA 0x32bc; Ghidra-Adresse 0x132bc; FUN_000132bc. Beobachteter, nicht zusammenhängender Funktionskörper: inklusive Bereiche 0x120c8–0x1217b und 0x132bc–0x1330f, insgesamt 264 Bytes, 11 Basic Blocks. Beide Bereiche sind unten vollständig wiedergegeben. Der zweite Bereich verzweigt zum ersten.
- Addend 0x327c → ELF-Ziel-Link-VA 0x327c; Ghidra-Adresse 0x1327c; FUN_0001327c. Beobachteter, nicht zusammenhängender Funktionskörper: inklusive Bereiche 0x121d0–0x1238f und 0x1327c–0x132bb, insgesamt 512 Bytes, 22 Basic Blocks. Beide Bereiche sind unten vollständig wiedergegeben.

Lokale Register-/Speicherbeobachtung ohne ABI-Zuschreibung:

FUN_000132bc liest am Einstieg Werte aus r0, r1 und r2 in erhaltene Register. Der Körper ruft direkte Ziele bei 0x12180, 0x114d4, 0x114bc und 0x114c8 auf. Er enthält bedingte Speicherzugriffe und schreibt an eine über r9 gebildete Adresse. Sichtbare Rückkehrpfade setzen r0 auf 0 oder -1, restaurieren Register und kehren über pc zurück. Parameterarten und Callee-Effekte bleiben offen.

FUN_0001327c kopiert am Einstieg r0 nach r4. Der Körper ruft direkte Ziele bei 0x12180 und 0x11f08 sowie weitere Ziele innerhalb 0x121d0–0x1238f auf. Er enthält bedingte Speicherzugriffe, darunter Stores relativ zu r6 und Stackzugriffe. Sichtbare Rückkehrpfade restaurieren Register und kehren über pc zurück; Fehlerpfade setzen r0 auf -1. Aufrufkonvention, Typen, Strukturfelder und Callee-Effekte werden nicht behauptet.

## Vollständige begrenzte Instruktionskörper

Die oben wiedergegebenen Funktionskörper stammen aus REA read_function_instructions (Ghidra Listing). Zusätzlich wurden die beiden von Ghidra gemeldeten AddressSets für jedes Ziel getrennt mit GNU ARM cross-objdump in ELF-Linkadressen disassembliert. Die vier begrenzten Listings liegen in den Dateien unten. GNU objdump verwendet jeweils die statische ELF-Adresse (Ghidra-Adresse minus 0x10000). Seine Labels mit Symbolname plus/minus Distanz sind nächstgelegene Symbol-Kontexte, keine exakten Ziel-Symbole und keine Funktionsverträge.

### FUN_000132bc — Evidence ev_629808c62d0e582d7381bb9939e38c5df4b44ada220aa1f6a1b5298dd7433cd1

[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

### FUN_0001327c — Evidence ev_bb25976ff99418cc3a5835aeb7a62a74b8f259408a4d937a895de8cb70a34761

[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

## Alternative explanation and remaining uncertainty

HYPOTHESE: ELF R_ARM_RELATIVE plus the exact words makes 0x32bc / 0x327c the static addends. Ghidra's 0x10000 image base explains the imported values. These are static linked targets. Since the object is ET_DYN, runtime values depend on its loader base, which was not observed.

OFFEN: source-level meaning, exact prototypes/calling convention, and callee effects are unestablished. No named symbol occurs at either exact linked target VA in the symbol-table output. Ghidra boundaries are its observed FunctionManager AddressSets; both are non-contiguous and are reported exactly as returned. Complete bodies here mean the full instruction lists returned across those two ranges for each target; they do not establish whole-program behavior.

## Provenance, versions, validator

- REA used first on the hash-bound ELF. REA package/server rea-agents 6.5.0; Ghidra 12.1.4; selected profile digest 7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de.
- GNU readelf: Binutils 2.44. Generic GNU objdump: Binutils 2.44, without ARM support in objdump -i. GNU ARM cross-objdump arm-linux-gnueabihf-objdump: Binutils 2.44. No process, runtime, network, VM, or device was used.
- Evidence: binary_overview ev_a40e925ba5e6499cd86d0c350ecb767487473d9b374e0de0522a6091e924252f (image base and segments); loaded bytes ev_252a827298aa87b31786383f95db5c0c2c032c093cc9f17cccc486d26fa45354; target 1 function metadata ev_ebd0fc50c7c7c8171a866b3da9fb95459d7e0c8156c6141c8b8a73c214264ebf; target 1 instructions ev_629808c62d0e582d7381bb9939e38c5df4b44ada220aa1f6a1b5298dd7433cd1; target 2 metadata ev_dbbdba5d9f4a441ae7202e9dd30b0777a497e7db2be2d41d1e1772f68bb2ecd5; target 2 instructions ev_bb25976ff99418cc3a5835aeb7a62a74b8f259408a4d937a895de8cb70a34761.
- Input hash: sha256sum matched the assignment's expected digest (PASS).
- Slot validator: raw bytes at offsets 0x4160/0x4164 decode little-endian to 0x32bc/0x327c. readelf -SW maps .data VA 0x14150 to offset 0x4150; readelf -rW shows R_ARM_RELATIVE at both exact VAs (PASS).
- Imported-value validator: Ghidra overview reports image base 0x10000; read_bytes(0x24160, 8) returned bc3201007c320100 completely (PASS), giving 0x132bc/0x1327c. A read at ELF VA 0x14160 is unmapped in the rebased Ghidra address space and returned zero bytes; it is not used as value evidence.
- Body validator: Ghidra reports available bodies: target 1 ranges total 264 bytes, target 2 ranges total 512 bytes. Ghidra instruction counts are 66 and 128. Four GNU ARM cross-objdump listings separately cover all four inclusive ELF ranges; their output and exact address sequences are regenerated and checked by validate.py (PASS).
- Reproducible validator: run python3 validate.py from this directory. It checks input identity, .data mapping, both relocations and implicit addends, loaded values, target entry bytes, report instruction counts, regenerated bounded cross-disassembly, and all SHA256SUMS entries. This validation is a static evidence check, not a product test.
- Tests: NOT_RUN (static evidence validation only).

## Output files and SHA-256

The generated files are listed in SHA256SUMS (the manifest intentionally does not checksum itself). slots-targets.csv is the machine-readable slot/target table. The four FUN-*-ELF-*.objdump.txt files give separate ELF-address ranges for each observed Ghidra body. validate.py reproduces and checks those listings offline.
