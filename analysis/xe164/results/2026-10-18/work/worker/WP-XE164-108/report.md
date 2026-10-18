> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-108 — ELF-Literal/GOT-Kette bei `0x12bf0`

## Ergebnis

**VERIFIZIERT:** Der indirekte Call wird über eine PIC/GOT-Kette gespeist. In Ghidra/REA (ARM-Programmadresse) lädt `0x12bdc` aus dem Literal `0x12eb4` den Wert `0xc4`; `0x12be8` liest mit dem im selben Caller aufgebauten GOT-Basisregister `r9` den GOT-Eintrag bei `0x290c4`; `0x12bec` dereferenziert den dort geladenen Objektzeiger; `0x12bf0` führt den resultierenden Wert als `blx r3` aus.

Die ELF-Relocation bei ELF-VA `0x190c4` ist `R_ARM_GLOB_DAT` auf Dynsym-Eintrag 44 / Symbol `pfIoMgrConfigGetParameterValuePointer` (ELF-Symbolwert `0x1a224`, Größe 4, `OBJECT`, `.bss`). Damit ist die beim zweiten Load gelesene globale Objektzelle statisch benennbar. Ein konkreter Laufzeit-Callback ist aus der Datei statisch nicht benennbar: die Objektzelle ist `.bss`, direkte Ghidra-Xrefs zeigen keine `WRITE`-Referenz, und kein Laufzeitwert wurde beobachtet.

**HYPOTHESE:** Die globale Objektzelle stellt an dieser Callsite einen Funktionszeiger bereit. Das folgt aus dem Load aus der Objektzelle unmittelbar vor `blx r3`, nicht aus der Symbolbezeichnung. Welcher Codezeiger zur Laufzeit darin steht, bleibt unbekannt.

## Beobachtungen und Adressrechnung

Artefakt: `libIoDrvKbus.so.0.0.1`, 38.584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`. Der Caller-Kontext WP-XE164-104 stimmt mit dem vorgegebenen SHA-256 `2608135b3c3d67b4d9a26ccf953c1a5b2e0cfaa5a6e6f32529e342250f2c5a51` überein.

Ghidra/REA verwendet hier für den analysierten LOAD einen Bildversatz von `0x10000` gegenüber den ELF-Linkadressen. Für den Literalbezug wurde die Ghidra-Quelle direkt durch REA auf Datei-Offset `11956 = 0x2eb4` abgebildet. Für diese erste LOAD-Region sind ELF-VA und Datei-Offset gleich. Die Koordinaten bleiben getrennt:

| Objekt/Instruktion | Ghidra-Adresse | ELF-Link-VA | Datei-Offset | Befund |
|---|---:|---:|---:|---|
| PIC-Basisliteral `0x16860` | `0x12e80` | `0x2e80` | `0x2e80` | von `0x1278c` geladen |
| Caller-PIC-Basisdefinition | `0x12798` | `0x2798` | `0x2798` | `add r9,pc,r9`; ARM-State-PC `0x27a0` plus `0x16860` ergibt ELF-VA `0x19000`, in Ghidra `0x29000` |
| Literal-Ladeinstruktion | `0x12bdc` | `0x2bdc` | `0x2bdc` | `ldr r3,[pc,#0x2d0]`; ARM-State-PC `0x2be4` plus `0x2d0` ergibt `0x2eb4` / Ghidra `0x12eb4` |
| Literal | `0x12eb4` | `0x2eb4` | `0x2eb4` | little-endian Bytes `c4 00 00 00` → `r3=0xc4` |
| GOT-Cell | `0x290c4` | `0x190c4` | `0x90c4` | `r9 + r3 = 0x29000 + 0xc4` |
| benannte `.bss`-Objektzelle | `0x2a224` | `0x1a224` | kein Dateibyte (`NOBITS`) | Dynsym `OBJECT`, Größe 4, Name `pfIoMgrConfigGetParameterValuePointer` |

Die Call-Sequenz aus GNU-Disassembly (ELF-Adressen, keine Ghidra-Adressen):

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Die .got-Sektion beginnt bei ELF-VA `0x19000`, Datei-Offset `0x9000`, Größe `0x1cc`. Der Eintrag `0x190c4` liegt damit bei Sektionsoffset `0xc4`, Datei-Offset `0x90c4`. Seine statischen Dateibytes sind `00 00 00 00`. REA-initialisierte Speicherbytes an Ghidra-Adresse `0x290c4` sind `24a20200`; das ist das von Ghidra angewendete statische Loader-/Relocationbild für den Symbolwert `0x1a224`, kein beobachteter Laufzeitwert.

ELF-Relocation und Symbolbindung:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Das ELF ist `ELF32`, little-endian, `ET_DYN`, `EM_ARM`, EABI hard-float. Der statische Symbolwert ist die Linkadresse. Die dynamische Loaderauflösung hängt vom Load-Bias und der Symbolauflösung ab; kein absoluter Laufzeitwert wird behauptet. `R_ARM_GLOB_DAT` belegt die dynamische Relocation des GOT-Eintrags, nicht den tatsächlich zur Laufzeit eingetragenen Callback.

## Direkte statische Xrefs zur Zelle

Ghidra ReferenceManager für GOT-Zelle `0x290c4` listet vier direkte `READ`-Referenzen, keine `WRITE`-Referenz:

| Ghidra-Quelle | Instruktion | Referenzziel |
|---:|---|---|
| `0x12be8` | `ldr r3,[r9,r3]` | GOT-Zelle `0x290c4` (`READ`) |
| `0x12c5c` | `ldr r3,[r9,r3]` | GOT-Zelle `0x290c4` (`READ`) |
| `0x13d08` | `ldr r12,[r11,r12]` | GOT-Zelle `0x290c4` (`READ`) |
| `0x14cdc` | `ldr r1,[r5,r2]` | GOT-Zelle `0x290c4` (`READ`) |

Für die benannte `.bss`-Objektzelle `0x2a224` meldet die gezielte Instruktions-Xrefansicht `READ` bei `0x12bec`, `0x12c60`, `0x13d0c`, dazu `DATA` von GOT-Zelle `0x290c4`, und eine `PARAM`-Referenz bei `0x14cdc`. Keine dieser materialisierten Referenzen ist als `WRITE` markiert. Das ist ein begrenzter negativer Befund zum analysierten Ghidra-Referenzbestand; er beweist nicht, dass es keine aliasierte, ungelöste oder zur Laufzeit ausgeführte Initialisierung gibt. Die GOT-Zellenreferenz selbst und die BSS-Zielzelle sind verschiedene Objekte.

## Befundstatus und Restunsicherheit

- **VERIFIZIERT:** Literalwert, r9-GOT-Basis, Ziel-GOT-Zelle, deren einzelne `R_ARM_GLOB_DAT`-Relocation, Dynsym-Objektname und direkte materialisierte Xrefs wie oben.
- **OFFEN:** Laufzeit-Load-Bias, dynamische Symbolpräemption/konkrete Auflösung, Inhalt von `pfIoMgrConfigGetParameterValuePointer` zum Callzeitpunkt und tatsächliche Zieladresse von `blx r3`.
- **OFFEN:** Direkte Ghidra-`WRITE`-Referenzen auf `0x2a224` wurden in der exakten Xrefmenge nicht gefunden; nicht aufgelöste indirekte Stores und vom Ghidra-ReferenceManager nicht materialisierte Kanten bleiben außerhalb der Aussage.
- **Alternative Erklärung:** `pfIoMgrConfigGetParameterValuePointer` kann ein globales, zur Laufzeit durch Setup oder einen anderen Alias befülltes Objekt sein; außerdem kann ELF-Symbolpräemption die Loaderauflösung beeinflussen. Der Name allein bestimmt weder Wert noch API-Semantik.

## Methode, Tools und Fallback

REA war die erste Methode: `open_binary` mit Ghidra, gefolgt von Instruktions-, Literal-, Fileoffset- und gezielten Xrefabfragen. Ghidra 12.1.4, REA `rea-agents` 6.5.0, Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

**Konkrete REA-Lücke (einmalig):** die Ghidra-Instruktionsantwort bewahrt Operandtokens, stellt aber keine effektive PC-/Registeradressauswertung bereit; außerdem liefert der verfügbare REA-ELF-Layoutdecoder auf diesem Linux-Host nur ELF64/x86-64. Deshalb wurden genau der benannte Callerbereich, der dazu nötige Literalpool, ELF-Header/LOAD-/`.got`-Metadaten sowie `.rel.dyn`/`.dynsym` mit GNU ARM Binutils 2.44 gelesen. Kein Binary ausgeführt. Eine erste `objdump`-Abfrage mit der Ghidra-Adresse wurde nicht als ELF-Adresse interpretiert und ergab keine Disassembly; nach Anwendung des nachgewiesenen `+0x10000`-Adressversatzes wurde die begrenzte Abfrage bei ELF-VA `0x277c..0x2c00` ausgeführt. Es gab keine Wiederholung derselben fehlerhaften Anfrage.

Verwendete Fallbacks:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

## Tests

| Prüfung | Status | Ergebnis |
|---|---|---|
| Ziel-/Caller-Hashes | PASS | Beide stimmen mit den vorgegebenen SHA-256 überein. |
| REA-Bundle-Export | PASS | Kanonisches Bundle exportiert; 21 Evidence-Datensätze, 0 Unknowns. |
| Semantischer Validator | PASS | Prüft die REA-Instruktions-/Literal-/Xrefkette und die direkt materialisierten Schreib-/Lesearten gegen das Bundle. |
| GNU ARM Fallback | PASS | Begrenzte Disassembly, Relocation, Dynsym und Abschnitts-/Adressmetadaten aus Binutils 2.44. |
| Firmwareausführung/Runtimebeobachtung | NOT_RUN | Explizit offline und statisch; kein Targetstart. |

## Kanonisches REA-Bundle und Dateien

Das Bundle `rea-bundle.json` enthält die vollständigen REA-Evidence-Records dieser Untersuchung. Ein semantischer Konsistenzprüfer liegt in `validate_semantics.mjs`. SHA-256 für alle erzeugten Nutzdateien steht in `SHA256SUMS`.
