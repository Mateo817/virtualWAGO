> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-015 — Statische Struktur von E0045C

## Ergebnis

**VERIFIZIERT (statisch, begrenzter Umfang):** Im gebundenen Composite ist der Seed bei Datei-Offset `0x45C` (Replay-Adressraum `E0045C`) ein C166-Befehlsstrom mit 12 Instruktionen über `[0x45C, 0x482)`. `jnb` an `0x47A` besitzt ein beobachtetes Sprungziel `0x480` und Fallthrough `0x47E`; beide Wege erreichen `rets` bei `0x480`. Der unmittelbar folgende Strom ab `0x482` ist unerreichbar von diesem Seed nach der beobachteten Rückkehr und wurde aus dem Body ausgeschlossen. Die Ausgabegrenze liegt damit exakt nach dem Zwei-Byte-`rets` bei `0x480`; keine überlaufenden Bytes wurden gebündelt.

Die beiden separat vorgegebenen Einzelinstruktions-Kandidaten bei `0x542` und `0xC0A` dekodieren als `calls 0xe0045c`, jeweils mit Bytes `dae05c04`. Es wurden keine Caller-Bodies verfolgt. Im begrenzten Body sind keine Call-Instruktionen beobachtet.

Explizite direkte Adressoperanden im Body stehen in `references.tsv`: `0xff10.11` bei `0x45C`, `0x460`, `0x47E`; `0xf0c0` bei `0x464`, `0x476`; `0xfec0` bei `0x468`, `0x46C`, `0x470`. Dies sind Operand-Referenzen, keine SFR-/Hardwarebedeutungen oder Register-/ABI-Aussagen. Eine Zugriffsrichtung wird für `bmov` nicht behauptet.

## Fundstellen und Methode

- Composite: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`, 17110 Bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Replay-Hinweis: `PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md`, 2169 Bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`; dokumentiert Ghidra 12.1.4 mit `C166:LE:16:default`, `tasking`, Loader-Basis `0xE00000`.
- REA `execute_rizin_command` war das erste Analysewerkzeug. Provider meldet `rizin`, ausführbare Version nicht verfügbar. Aufrufprofil `-N -q`; Konfiguration `io.va=false`, `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`; keine globale Analyse (`aaa`) ausgeführt.
- Für den Body: `pdj 14 @ 0x45c`; Tabellen übernehmen nur Offsets `0x45C` bis einschließlich `0x480`. Die Bytes `0x482..` im Werkzeugfenster wurden verworfen. Für die Callsite-Kandidaten jeweils `pdj 1 @ 0x542` und `pdj 1 @ 0xc0a`.
- Kanonischer, vollständiger REA-Export: [evidence/rea-bundle.json](evidence/rea-bundle.json), 51,377 Bytes, SHA-256 `fb80addd2bd3f5cda71e16fe0e20c9d1735e7fa91989730fb334a53513375e01`; Exporter meldete 5 Records und 0 Unknowns. Das frühere handgefertigte Beobachtungsschema ist unverändert als Auditbeilage [evidence/selected-rea-observations.json](evidence/selected-rea-observations.json) erhalten (SHA-256 `1899934a5c9823eea2da38dba1478d5cca9eb67240362f51c0a0cbf3711003da`); es ist ausdrücklich kein kanonischer REA-Export. Rizin-Tabellen in `instructions.tsv`, `edges.tsv`, `calls.tsv`, `references.tsv`.
- WP-strukturevidenz-IDs im kanonischen Export: Body `ev_966bb35975081ba793add049d255b8e1d7e5bdb1d9607f8beb96c4ed31c72a1e`; Einzelinstruktion bei `0x542` `ev_344e5a059b2833ea1846dd985c46a507a0d4e0d0b1468dd18e20f55e5aaf8f53`; Einzelinstruktion bei `0xC0A` `ev_9c7e7a19069780ba5ee4eaeb02c45ef229dda731100448fafcc2dd667eb8dd4a`. Der Export enthält außerdem den anfänglichen Suchlauf `ev_d6ec3ad8957bccef252e7e378b34db7d63be33c6d460474c545af9bed4914295` (`pd 80 @ 0x45c`) und den fehlgeschlagenen Versionsversuch `ev_07ff84b036c984c15c00d966b296a59e534e86bcb2b78e894036a1c1d9e1c8b7` (`?V`). Der anfängliche Lauf reichte im Werkzeugfenster über den später festgelegten Umfang hinaus; seine über `0x480` hinausgehenden Zeilen wurden nicht in Tabellen oder strukturelle Aussagen übernommen. Die vollständige Evidence-Aufbewahrung bewahrt diese Sessionbeobachtung dennoch unverändert.

Die Kontrollflusskanten sind direkte Dekodierbeobachtungen: lineare Fallthroughs, zwei Kanten des bedingten Sprungs, und terminale Rückkehr. Der Rücksprung ist nicht als Kante mit erfundenem Ziel dargestellt. Werkzeug-Pseudocode/CFG-Lesart: „Initialisierungssequenz; Bedingungstest; bei genommenem Sprung Rückkehr, sonst Bit-Operation und Rückkehr.“ Dies ist nur strukturelle Paraphrase von Instruktionsform und Kanten, keine Verhaltens- oder Hardwaresemantik.

## Evidenzstatus und Grenzen

- Kontrollfluss, Callsite-Bytes/-Ziele und explizite Operanden: **VERIFIZIERT** für die angegebene Composite-Revision und die begrenzte C166-Dekodierung.
- Zweck der Speicheradressen, Bedeutung der Bitfelder/Register, ABI/Parametervertrag und FW31-Übertragbarkeit: **OFFEN**; nicht zugewiesen.
- Untersuchte Caller-Logik, andere Callers/Callees sowie Laufzeit-/Geräteverhalten: **OFFEN** und außerhalb dieses Pakets.
- Rizin-Versionsnummer: **OFFEN**; REA lieferte keine Version, der unterstützte Versuch `?V` wurde als Parserfehler zurückgegeben. Dies beeinträchtigt nicht die dokumentierten Ausgaben, schränkt aber Reproduzierbarkeit auf Provider-Versionsebene ein.
- Ghidra-Fallback: **NOT_RUN**. Für die hier gestellte CFG-/Call-/Operandenfrage lieferte die begrenzte Dekodierung die benötigten Kanten und Referenzen; es verblieb keine konkrete Analyse-Lücke.
- Statische Beobachtung, keine Emulation und keine Aussage über erreichbare Laufzeitzustände.

## Alternativen und Restunsicherheit

Ein begrenzter Ghidra-Fallback mit den Replay-Parametern wäre eine unabhängige Dekodierprüfung, wurde hier aber nicht zur Schließung einer konkreten Lücke benötigt. Die Body-Ende-Entscheidung folgt dem beobachteten `rets` bei `0x480`; ein anderer Einstieg in angrenzende Bytes oder andere absichtsvoll überlappende Codepfade sind nicht Teil dieses Seeds und wurden nicht gesucht. Rizin hat kein globales CFG-Modell für diese Funktion erzeugt; die Kanten sind manuell aus den begrenzten Instruktionszeilen und den Feldern `jump`/`fail` transkribiert.

## Validierung

`validate.py` prüft Composite-Größe und SHA-256, Instruktionsanzahl und -Offsets, Größen und Bytes direkt am Composite, erwartete CFG-Kanten, die beiden Callsite-Bytes/Ziele und die Offsets sowie Operanden der Referenztabelle. Erneute Ausführung nach Export: **PASS**. `sha256sum -c SHA256SUMS`: **PASS**. SHA256SUMS bindet Bericht, Tabellen, Validator, kanonischen REA-Export und Auditbeilage.
