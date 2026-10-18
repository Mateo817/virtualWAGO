> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-052 — Kontrollfluss ab Seed E0340E

## Ergebnis

**VERIFIZIERT (statische Byte-/Decoderbeobachtung):** Der isoliert vorgegebene Caller bei `E0361C` enthält einen direkten `CALLS E0340E` (`DA E0 0E 34`). Ab `E0340E` dekodiert Rizin im strikt begrenzten Fenster `E0340E..E03527` 110 lückenlos aneinander anschließende Instruktionen. Die letzte ist `RETS` bei `E03526` (`DB 00`); ihr Ende ist exakt `E03528`. Kein im Fenster dekodierter direkter Sprung zielt auf `E03528`.

**Reachability ist von linearem Decode getrennt:** Die 110 Instruktionen sind im aus `E0340E` gewurzelten, begrenzten CFG nur über explizit bedingte Call-Fortsetzungen erreichbar. Das Minimum der dafür erforderlichen Call-Rückkehrkanten verteilt sich wie folgt: 9 Instruktionen benötigen 0, 16 benötigen mindestens 1, 30 mindestens 2, 53 mindestens 3, und die Schlussinstruktionen `E03524`/`E03526` mindestens 4. Diese Kanten behaupten keine Rückkehr: `E033B8`, `E03ABA` und `E033F0` wurden nicht untersucht. Beide von Rizin ausgegebenen Kanten bedingter Sprünge bleiben im CFG erhalten. Das ist statische May-Reachability, keine Ausführungsaussage.

## Kontrollflussstruktur

- Eintrittsprolog `E0340E..E0341E`: acht aufeinanderfolgende 2-Byte-`MOV`-Instruktionen, darunter Speicheroperanden mit Prädekrement- und Postinkrement-Schreibweise. Erster direkter Call bei `E03420` nach `E033B8`; der Fortsetzungsblock ab `E03424` hängt von einer Rückkehr ab.
- Nach dem ersten Call folgt ein weiterer direkter Call bei `E03444` nach `E03ABA`. Danach enthält der Block vier von Rizin als bedingt dekodierte Vorwärtszweige: `E03450 → E03458/E03452`, `E0345A → E03462/E0345C`, `E03472 → E0347A/E03474`, `E0347C → E03484/E0347E`.
- Ein dritter Call bei `E03494` zielt ebenfalls auf `E03ABA`. Danach zeigt die Kante `E034BE → E034A8` eine Rückschleife; die alternative Kante erreicht `E034C0`. Der Schleifenkopf `E034A6` hat die von Rizin ausgegebenen Ziele `E034C0` und `E034A8`.
- Im anschließenden Block liegen die Rizin-Zweige `E034DC → E034F0/E034DE` und `E034EE → E034F2/E034F0`. Beim zweiten bleibt die Rohdekodierung `jmpr cc_UC` maßgeblich: Rizin klassifiziert beide Kanten als `cjmp`; ihre Architektursemantik wurde nicht durch eine unabhängige Quelle geprüft.
- Der Endblock enthält einen vierten direkten Call bei `E03520` nach `E033F0`, danach `MOV r6, [r0+]` bei `E03524` und `RETS` bei `E03526`. Es gibt aus dem untersuchten Code keinen beobachteten Sprung nach `E03528`; der nächste Bereich wurde nicht gelesen.

Die vollständigen Einzelinstruktionen und alle vom Decoder gelieferten CFG-Kanten stehen in [instructions.tsv](instructions.tsv) und [control-flow.tsv](control-flow.tsv). Branchziele, die Rizin als Offset im C166-Codefenster ausgibt, sind dort mit dem Composite-Basiswert `E00000` zu virtuellen Adressen abgebildet; die originale Dekodierung steht jeweils in der Instruktionstabelle. Die vier internen Calls und der eine vorgegebene Caller sind in [calls.tsv](calls.tsv) exakt aufgeführt.

## Methode und Status

Input geprüft: 17,110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.

REA 6.5.0 meldete im frischen Sitzungsinventar Ghidra 12.1.4 verfügbar, aber ohne offenes Ziel. `open_binary` lehnte das Composite mit `unsupported binary format` ab; ein C166-Rohbildformat ist im REA-Aufruf nicht angeboten. Entsprechend dem Auftrag wurde nach dieser beobachteten Lücke der Rizin-C166-Fallback verwendet. Die konkrete REA-Operation ist `execute_rizin_command`, Evidence-ID `ev_e921b667fcfdd402d36259e5d301233f451f85dd954709a1ef34f15ec7861a9a`. Rizin wurde mit `io.va=false`, `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false` aufgerufen; `p8` und `pDj` waren auf exakt 282 Bytes ab Offset `0x340e` begrenzt. Der isolierte Caller wurde mit einem einzelnen `pdj 1` bei Offset `0x361c` dekodiert. REA-Evidence meldet vollständige Ausgabe, Exitcode 0 und unveränderten Input-Hash.

REA meldet für den Rizin-Provider keine Version. Der lokale Rizin-Versionsaufruf ergab `0.9.1`, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`. Ghidra 12.1.4 wurde nicht zur Kontrollflussableitung verwendet. Die angegebene Ghidra-Funktionsgröße bleibt **HYPOTHESE** und wird hier weder bestätigt noch ersetzt.

Validatorstatus: **PASS** — [validate_and_render.py](validate_and_render.py) prüft Inputgröße/-Hash, genau einen passenden REA-Datensatz, Befehlsabschluss und Outputvollständigkeit, Caller-Ziel, lückenlose Instruktionsgrenzen, Fensterende `0x3528`, seed-gewurzelte CFG-Abdeckung, das Call-Rückkehr-Minimumprofil und das Fehlen einer direkten Sprungkante nach `E03528`; anschließend rendert es die drei TSV-Tabellen.

## Restunsicherheit und Grenzen

- Die Call-Ziele wurden nur als direkte Ziele notiert. Ob und wann sie zurückkehren, ist **OFFEN**; alle Fortsetzungsblöcke nach Calls sind entsprechend qualifiziert. Die bedingten Zweige wurden nicht anhand Register-/Flagwerten ausgewertet.
- Rizin kennzeichnet `atomic #2` und `extp #0x0081, #2` als Instruktionstyp `unk`. Die sequenziellen Kandidatenkanten nach solchen Instruktionen bleiben in der Tabelle ausdrücklich als nicht vom Typfeld klassifiziert markiert.
- Die Analyse belegt weder Bedeutung, ABI, SFRs, Laufzeitverhalten, Geräteverhalten noch Hardwarewirkung. Es wurden keine weiteren Caller, keine Callees, `E03528` oder Nachbarbytes untersucht.
- Aussagen beruhen auf einer einzelnen statischen Rizin-Dekodierung plus dem explizit isolierten Caller. Sie sind kein unabhängiger Review und kein Laufzeittest.

## Artefakte

- [rea-evidence.json](rea-evidence.json) — kanonisches, finding-only REA-Bundle mit genau einem Evidenzdatensatz.
- [instructions.tsv](instructions.tsv) — exakte 110 Instruktionszeilen, inklusive Erreichbarkeitsqualifikation.
- [control-flow.tsv](control-flow.tsv) — exakte vom Provider ausgegebene bzw. konservativ modellierte Nachfolgerkanten.
- [calls.tsv](calls.tsv) — Calls im Fenster und vorgegebener isolierter Caller.
- [validate_and_render.py](validate_and_render.py) — Validator und deterministischer Tabellenrenderer.
- [SHA256SUMS](SHA256SUMS) — Hashes der Bericht- und Ergebnisartefakte.
