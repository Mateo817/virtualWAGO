> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-014 — begrenzter Kontrollfluss von E0043C

## Ergebnis

**VERIFIZIERT:** Der mehrfach beobachtete direkte Callee `E0043C` besitzt im Composite einen zusammenhängenden, statisch erreichbaren Body von Fileoffset `0x043C` bis einschließlich der `rets`-Instruktion bei `0x045A`; das Ende ist exklusiv `0x045C` (32 Bytes, 10 Instruktionen). Der bedingte Zweig bei `E00454` hat die zwei lokal beobachteten Nachfolger `E0045A` (Ziel) und `E00458` (Fallthrough). Beide Pfade enden bei `rets` an `E0045A`. Keine Instruktion nach `E0045A` ist Teil dieses Bodies; insbesondere wurden Bytes ab `0x045C` verworfen und nicht gebündelt.

**VERIFIZIERT:** Die zwei vorgegebenen eingehenden Callsite-Kandidaten bestehen jeweils aus genau einer bei `E004CC` beziehungsweise `E00BEE` dekodierten `calls E0043C`-Instruktion. Caller-Bodies wurden nicht untersucht.

**VERIFIZIERT (syntaktische Referenzen):** Im Body stehen direkte absolute Operanden `0xFF10.11`, `0xF0C0` und `0xFEC0`; der bedingte Sprung verweist auf `E0045A`. `references.tsv` hält diese Operandreferenzen inklusive Instruktionsbytes fest. Dies weist keine Register-, SFR-, Peripherie- oder sonstige Semantik zu.

## Beobachtungen und Grenzen

Die Erstabfrage dekodierte ab Fileoffset `0x043C` mit C166/16/little und `io.va=false`. Rizin zeigte die Kante `0x0454 → 0x045A`, den Fallthrough über `0x0458` sowie `rets` bei `0x045A`. Da direkt bei `0x045C` eine weitere Instruktion beginnt, wurde der genaue Body zusätzlich auf 32 Bytes begrenzt mit `p8 32 @ 0x43c`; die dadurch gebundene Bytefolge endet in `db00` (`rets`). Die Ergebnisse der einzelnen REA-Abfragen samt IDs sind selektiv in `REA-Evidence-Bundle.json` abgelegt.

Die Rizin-Version wurde lokal mit `rizin -v` als 0.9.1, Commit `c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`, festgestellt; REA selbst berichtete keinen Provider-Versionswert. Profil: `-N -q`, `e asm.arch=c166`, `e asm.bits=16`, `e cfg.bigendian=false`, `e io.va=false`, jeweils Offset-Seek/Abfrage. Es wurde kein globales `aaa` und kein Ghidra-Fallback eingesetzt: Die gezielte lokale Decode-Ausgabe deckte die hier benötigten Instruktionsstarts, beide Zweigziele, Returngrenze und direkten Callsites ab, also keine konkrete CFG-/Referenzlücke blieb.

## Kanonischer REA-Export und Abnahmekorrektur

Der ursprünglich handgefertigte, kuratierte Bundle-Inhalt wurde unverändert als `selected-rea-observations.json` archiviert (SHA-256 `6b043024b06c516d5224508856aad7d0e47bae470434dffdd417c37acc42a838`). Anschließend wurde im REA-Sessionkontext `export_evidence_bundle` mit `overwrite=true` ausgeführt. Das kanonische `REA-Evidence-Bundle.json` enthält 7 deterministisch exportierte Records, 0 Unknowns, umfasst 27 225 Bytes und hat SHA-256 `07f32626588bf9af8e490a387ed4b7a550b183d3542ce05fcdc2b533a075c7eb`.

WP-relevante kanonische Evidence-IDs (alle 7 Bundle-Records):

- `ev_11c4b89d68cf00ee4c6b8b5f5a950c2aa110855721188837d84e42350f068bf5` — anfänglicher Decode ab `0x43C`; Provider-Ausgabe schließt Nachbarinstruktionen ein, die nicht in den WP-Tabellen übernommen wurden.
- `ev_5d14b2d08144f612a1bed935db6dc61f4f660a1d6974f9ec379aa375ee2ae1ca` — einzelne Callsite `0x4CC`.
- `ev_5e4752d4998cdd7a9b00af9b0a34561cacac60f8480d6623c5369595ddd60166` — exakte 32-Byte-Rohdatenfolge des Bodys.
- `ev_7569fa90a78643d79ed528a8015e7b06fc9001eab641c3cc7a951e994a4d1688` — Bytes beider einzeln geprüften Callsite-Instruktionen.
- `ev_a19471d31d731a7a32b0192fe5792f343029cd8c03e09dfcf5ea9d0309837f58` — einzelne Callsite `0xBEE`.
- `ev_ace93261815fb9ccdcff42de83b5e1511dda366b43d1eaa1af46f7ae4db81677` — 30-Byte-Rohdatenprobe; ließ die zwei Bytes der Return-Instruktion am Ende aus.
- `ev_e87955e5b451fb0bf360699e24d9aaf399b700f46f53cd3eb7aab786b288dce1` — exakte 32-Byte-Bodyfolge und Bytes beider Callsite-Instruktionen.

Der anfängliche Decode-Evidence-Record enthält naturgemäß den umgebenden Tool-Output nach `rets`; die selektierte Auditdatei begrenzt dessen Übernahme ausdrücklich, und die eigentlichen Instruktions-/Edge-Tabellen enden bytegenau bei `0x45C` exklusiv.

**HYPOTHESE:** `E0043C` wird hier als Startadresse des betrachteten Callee-Bodies verstanden, gestützt durch die zwei direkten `calls`-Instruktionen und den vorgegebenen Seed. Das statische Material allein beweist keine Laufzeitaufrufhäufigkeit.

**OFFEN:** Laufzeitpfade und Wirkungen der absoluten Operanden sind nicht bestimmt. Es wird kein ABI-, SFR-, K-Bus-, Register- oder FW31-Vertrag behauptet.

## Werkzeugableitung (Pseudocode)

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Diese Skizze beschreibt die statische Auswertung, nicht Programmsemantik. Der konkrete Body wurde am lokalen Return bei `0x45A` abgeschlossen; angrenzende Instruktionen wurden ausgeschlossen.

## Status und Tests

| Prüfung | Status | Beobachtung |
|---|---|---|
| Composite-Größe und SHA-256 | PASS | 17 110 Bytes; stimmt mit Aufgabenbindung überein. |
| Replay-Datei-Größe und SHA-256 | PASS | 2 169 Bytes; stimmt mit Aufgabenbindung überein. |
| REA Rizin-Abfragen | PASS | Decode, exakte 32-Byte-Sequenz, beide Callsite-Instruktionen und deren Bytes wurden gelesen; Artefakthash blieb unverändert. |
| Ausgabe-Validator | PASS | Prüft Datei-Offsets, Adressen, Zeilen/Spalten, Instruktionsbytes, Bodylänge/-abdeckung, Kanten, Callsites und Referenzbytes gegen Composite. |
| `sha256sum -c SHA256SUMS` | PASS | Manifestprüfung nach Erstellung durchgeführt. |
| Laufzeittests / Hardware | NOT_RUN | Nicht Teil dieses statischen Offlinepakets. |
| Ghidra-Fallback | NOT_RUN | Keine konkrete lokale CFG-/Referenzlücke nach Rizin-Decode. |

## Alternative und Restunsicherheit

Eine lineare Disassemblierung über `0x045C` hinaus könnte benachbarte Bytes fälschlich in denselben Funktionsbereich aufnehmen. Hier begrenzen der direkt vom Zweig erreichte Return bei `0x045A` und der exklusive Folgeoffset `0x045C` den untersuchten Body. Rizin-Disassembly ist Werkzeugbeobachtung, keine Laufzeitvalidierung; ein unabhängiger Decodervergleich wurde nicht ausgeführt.

## Eingaben

- Composite: 17 110 B, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Replay: 2 169 B, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`.
