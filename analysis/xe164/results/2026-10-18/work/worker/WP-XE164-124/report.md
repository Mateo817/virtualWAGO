> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-124 — Provenienz des ersten Arguments von `CmpIoMgr__Entry`

## Ergebnis

**VERIFIZIERT:** Im ELF mit SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` erkennt Ghidra 12.1.4 bei `0x00336a84` die Funktion `CmpIoMgr__Entry`, Body `0x00336a84..0x00336bdf` (348 Byte, inklusiv). Die dekompilierte, vom Werkzeug erzeugte Signatur ist `undefined4 CmpIoMgr__Entry(undefined4 *param_1)`; High-P-code führt denselben Parameter als Ordinal 0, `undefined4 *`. Diese Typangabe ist eine Werkzeugrekonstruktion, kein Header- oder Quellbeleg.

**VERIFIZIERT:** Der beim Eintritt in `r0` beobachtete erste Parameter wird bei `0x336ac8` nach `r12` kopiert. Die Instruktion `ldr r4,[r12,#0x1c]` bei `0x336aec` liest genau vier Bytes vom relativen Versatz `+0x1c`; der Store `str r4,[r1,#0x150]` bei `0x336b0c` legt diesen Wert in Default-Space/ELF-VMA `0x00601670` ab (`r1` wurde bei `0x336af0`/`0x336af8` aus `0x00601520` gebildet). Ghidras Pseudocode bildet dies als `DAT_00601670 = param_1[7]` ab. Die Gleichheit `+0x1c = 7 * 4` ist eine arithmetische Ableitung aus der von Ghidra rekonstruierten `undefined4 *`-Darstellung und der Vier-Byte-Ladeinstruktion, keine Semantik eines Feldnamens.

**VERIFIZIERT:** Vor dem Lesen von `+0x1c` schreibt dieselbe Funktion Werte in den übergebenen Speicherblock, unter anderem bei `+0x0`, `+0x14` und `+0x18`. Der Code behandelt den Parameter also statisch als beschreibbaren Zeiger und liest anschließend den Vier-Byte-Wert bei `+0x1c`. Die Herkunft dieses Zeigers oder der Bedeutung des gelesenen Werts vor dem Funktionseintritt wird durch die gefundenen lokalen Caller-/Xref-Daten nicht belegt.

**VERIFIZIERT mit widersprüchlicher Provider-Metadatenklassifikation:** `readelf -Ws` (GNU Binutils 2.44) listet `CmpIoMgr__Entry` in der Tabelle `.dynsym` als `GLOBAL DEFAULT FUNC`, Wert `0x00336a84`, Größe 348, Abschnittsindex 14. Der vollständige REA-`list_names`-Datensatz enthält denselben Namen und die Adresse, markiert das Symbol aber `dynamic:false`, `source:imported`. Daher stützt sich die Aussage zur ELF-Dynsym-Exportmetadatenlage auf die tabellarische `readelf`-Beobachtung; die REA-Klassifikation wird als Widerspruch offengelegt, nicht stillschweigend gleichgesetzt. Ein dynamischer Tabelleneintrag belegt keine konkrete Signatur, keinen API-Vertrag und keinen bestimmten Aufrufer.

**VERIFIZIERT:** Es wurden keine materialisierten direkten Caller gefunden. `procedure_callers(0x336a84)` liefert vollständig `[]`; das Funktionsdossier hat `callers:[]` und `incoming_references:[]`; `xrefs(0x336a84)` liefert `[]`. Die vollständigen eingehenden Referenzen auf den Funktionsbody enthalten nur den internen bedingten Kontrollfluss `0x336bc8 -> 0x336bd4`; er ist kein eingehender Call. Folglich lässt sich der erste Parameter statisch nicht über einen direkten Caller bis zu einer Erzeugungsstelle zurückverfolgen. Indirekte/aufgelöste Laufzeitaufrufe sind damit nicht ausgeschlossen.

## Begrenzte Suchabdeckung

- Exakter Ghidra-Einstieg `0x336a84` wurde als `CmpIoMgr__Entry` analysiert. Exakte Xrefs auf diese Adresse: 0. Aufgelöste direkte Caller des Eintrags: 0. Funktionsdossier: 0 eingehende Referenzen auf den Body und 0 direkte Caller. Für den vollständigen Body wurde die eingehende ReferenceManager-Richtung abgefragt; einziges Ergebnis ist der oben genannte interne Sprung. Ausgehende Body-Referenzen: 47; sie dienen hier nicht als zusätzliche API- oder Strukturinterpretation.
- `list_names` wurde ohne Filter als vollständiges Ghidra-Symbolinventar angefordert (im exportierten Bundle 87.473 Einträge); darin wurde der exakte Wert `CmpIoMgr__Entry` gefunden. Der MCP-Transport meldete bei der Inline-Antwort `resource_constraint`, da die vollständige Antwort die Transportgrenze überstieg; der Datensatz blieb als `complete-record` erhalten und ist im Bundle enthalten. Als gezielter Fallback für diese beobachtete Antwortlücke wurde genau einmal `readelf -Ws` ausgeführt; Ergebnis: `.dynsym`-Eintrag `00336a84`, Größe `348`, `FUNC GLOBAL DEFAULT`, Index `14`. Kein anderer Disassembler-Fallback wurde verwendet.
- Höchstens zwei unmittelbare Caller-/Dispatch-Lanes: keine Caller-Lanes materialisiert, daher keine Lane über den Funktionsblock hinaus verfolgt. Der ausgeschlossene generische Loader-Pfad wurde nicht untersucht. Keine `0x3AD9FC`/`0x3ADD1C`-Analyse und kein Slot-Reader-Reanalysis.
- Adressdomäne für `0x336a84`, `0x336ac8`, `0x336aec`, `0x336af0`, `0x336af8`, `0x336b0c` und `0x00601670`: Ghidra Default Space, numerisch identisch zur ELF-VMA. Kein Laufzeitwert wurde beobachtet.

## Interpretation, Alternative und Restunsicherheit

**HYPOTHESE:** Weil das Symbol `GLOBAL DEFAULT` in `.dynsym` steht, kann es für dynamische Symbolauflösung sichtbar sein. Welche Komponente den Eintrag sucht oder aufruft, ist in diesem Arbeitsumfang nicht belegt. Die naheliegende Alternative ist, dass ein externer/indirekter Aufrufer den exportierten Entry unter einer anderen Dispatch-Mechanik nutzt oder dass der Export einer anderen Laufzeitfunktion dient; die ELF-Metadaten entscheiden das nicht.

**OFFEN:** Die konkrete Adresse und Erzeugungsstelle des eingehenden `r0`; der Wert von `[r0+0x1c]` bei einem Aufruf; ein semantischer Feldname oder Datentyp über `undefined4`; ob und wann die Funktion tatsächlich aufgerufen wird; und ob der Slotwert anschließend unverändert bleibt. Der Header-/ABI-Vertrag ist aus Dynsym-Name, Symbolgröße und Ghidra-Rekonstruktion nicht ableitbar.

**Restunsicherheit:** Caller- und Xref-Abdeckung betrifft materialisierte statische Beziehungen in Ghidra. Nicht aufgelöste indirekte Referenzen, dynamische Symbolsuche und zur Laufzeit konstruierte Callpfade bleiben unbekannt. REA meldet für native Calls nicht durch Ziele aufgelöste Ziele explizit als nicht abgedeckt. Der bekannte Widerspruch `dynamic:false` vs. `.dynsym` ist auf unterschiedliche Providerklassifikation begrenzt; seine interne Ursache wurde nicht untersucht.

## Evidence, Eingaben und Werkzeuge

| Aussage | Fundstelle / Evidence | Status |
|---|---|---|
| Binäridentität und ARM-ELF | `codesys3`, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`; Größe 5.181.396 Byte | VERIFIZIERT |
| Vorbericht-Eingabe | `WP-XE164-120/report.md`, SHA-256 `636bb574979de68d90fb7d648ad1c6ea279269dc9c3e1bb2c5b544146b65df82` | VERIFIZIERT |
| REA/Ghidra Profil | Ghidra 12.1.4; Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; REA 6.5.0 | VERIFIZIERT |
| Eintragsidentität, Pseudocode, High-Pcode und Argument-Uses | `ev_749f48fa58dfc171476f7b04f41e0ecce265889d225c2286cfe1b9709f7b61f4` | VERIFIZIERT als statische REA-Beobachtung |
| Instruktionen des Entry-Blocks | `ev_901ad988fd25cb19a4026554faae3560c54fe6e207a801e33a468d18a9762d56` | VERIFIZIERT |
| Aufgelöste direkte Caller (leer) | `ev_14947926367cc616005830a7d63423ba19966f3fc2fbde064005e8e36c80b979` | VERIFIZIERT, begrenzte statische Abdeckung |
| Exakte Xrefs auf Einstieg (leer) | `ev_285eef07b1d78a9300ba76f3f341eb4141bf64aef2999890397cbc7ee08e2ddd` | VERIFIZIERT, begrenzte statische Abdeckung |
| Eingehende Referenzen des Bodys: interner Sprung | `ev_12249510d8ad6fca17c0d2ce55851dbdee5bf7a46ac8afd714e68184c19c4112` | VERIFIZIERT |
| Ausgehende Referenzen des Bodys | `ev_aba094e0a118f6fbd2267bba9c10c2cb9905035a4991b4618be822e2e7ce4678` | VERIFIZIERT; 47 Kanten |
| REA-Namensinventar | `ev_a109c01f038b67a875d15913e9a8854d87be2542184151d79acf9d62311b4fcc`; enthält den Symbolwert, Ghidra-Flag `dynamic:false` | VERIFIZIERT; MCP-Inlineantwort wegen Transportgröße begrenzt, vollständiger Record im Bundle |
| ELF-Dynsym-Exportmetadaten | GNU `readelf -Ws`, Binutils 2.44; `.dynsym` enthält Index 3631, Wert `00336a84`, `FUNC GLOBAL DEFAULT`, Abschnitt 14, Name `CmpIoMgr__Entry` | VERIFIZIERT durch den gezielten Fallback |
| Bundle-Integrität und Semantik | `validate.py` (Self-Review-Validator); vollständiges REA-Bundle mit 7 Records, 0 Unknown-Revisionen | siehe Prüftabelle |

REA wurde zuerst verwendet. Das ELF wurde nur statisch analysiert. Es gab keine Geräte-, Netzwerk-, VM-, Prozess- oder Zielausführung. Keine Firmware-/Treiber-/Hersteller-API und kein Struktur- oder Feldname wurde erfunden.

## Prüfstatus und Dateien

| Prüfung | Status |
|---|---|
| Eingabegrößen und SHA-256 | PASS |
| REA Evidence: Zielhash, Provider, Profil und eindeutige IDs | PASS |
| Entry-Adresse/Name/Body und Werkzeugparameter | PASS |
| `+0x1c`-Load bis Slot-Store, Register- und Adressableitung | PASS |
| Keine direkten Caller/exakten Entry-Xrefs; eingehender interner Branch korrekt getrennt | PASS |
| Dynsym-Zeile plus offener REA-Metadatenwiderspruch dokumentiert | PASS |
| Laufzeitaufruf, eingehender Parameterwert und tatsächliches Slotverhalten | NOT_RUN |
| Geräte / Netzwerk / VM / Zielausführung | NOT_RUN |

REA Evidence Bundle: `rea-evidence-bundle.json`, 25.478.378 Byte, 7 vollständige Records; SHA-256 `3059da24bb40a056073d03c4741629a6fcb1bfe782affc1d4db1c4eb12b8764a`. Der Bericht und Validator werden nach ihrer Erstellung in `SHA256SUMS` aufgeführt. Der Validator ist eine eigene semantische Selbstprüfung, kein unabhängiger Review oder Worker-Lauf.
