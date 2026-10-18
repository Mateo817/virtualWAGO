> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-210 — bedingte r7-/Speichererhaltung beim Getter-PLT-Aufruf

## Befund und Status

**VERIFIZIERT — lokale Instruktionspins:** Im begrenzten IoDrvDal-Fenster
`[0x2f44,0x2f5c)` wird `r7` durch keine Instruktion beschrieben. Es gibt dort
genau einen expliziten Store: `str r3,[r4,#0x618]` bei `0x2f48`. Der
getter-spezifische PLT-Eintrag `[0x9d4,0x9e0)` schreibt `ip`/`pc`, nicht `r7`,
und enthält keinen Store. Der exakte libdal-Getter `[0x3464,0x3474)` besteht
aus drei Instruktionen, die `r0` lesen/beschreiben und über `lr` zurückkehren;
sein vierter Wortbereich ist ein Literal, keine Instruktion. In diesen
Instruktionen gibt es weder einen `r7`-Write noch einen Speicher-Store.

**HYPOTHESE — bedingter bereits-aufgelöster direkter PLT→Getter-Pfad:** Wenn
der bereits relocatierte GOT-Slot `0x16030` auf den exakten Getter bei
`load_bias + 0x3464` zeigt, führt der PLT-Eintrag über diesen Slot zu diesem
Getter. Für genau diese Bedingung zeigen die gelisteten Instruktionen keinen
`r7`-Write zwischen erstem `[r7]`-Load bei `0x2f44` und zweitem `[r7]`-Load bei
`0x2f54`. Das ist eine bedingte statische Instruktionsaussage, kein Beleg des
Laufzeit-Slotwerts, der Laufzeitauflösung oder einer Calling Convention.

Die Gleichheit des bei `0x2f54` erneut gelesenen Wortes mit dem bei `0x2f44`
geladenen und bei `0x2f48` gespeicherten Wort ist **HYPOTHESE**, nicht
VERIFIZIERT. Der Store bei `0x2f48` liegt zwischen den Loads und schreibt über
`r4+0x618`. Dieses Ziel könnte mit `[r7]` ganz oder teilweise überlappen; der
begrenzte Ausschnitt belegt weder Überlappung noch Disjunktheit. Auch die
Register-/Speicherwirkungen des möglichen Lazy-Resolverpfads sind nicht
untersucht. Daher wird keine externe Speicherstabilität behauptet.

**OFFEN:** Ob Slot `0x16030` zur Laufzeit bereits auf den exakten Getter zeigt;
ob der Store bei `0x2f48` `[r7]` überlappt; ob außerhalb dieses bedingten
Direktpfads andere Effekte auftreten. Resolver, Runtime und Concurrency sind
OFFEN. Runtime/Hardware: **NOT_RUN**.

## Eingaben und Provenienz

IoDrvDal ist `FW31-IODRVDAL-1.0.2`, 25,976 Bytes, SHA-256
`853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` (PASS).
Die exakt beauftragte Eingabe ist die bereits akzeptierte WP202-Datei
`PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-202/input/libdal.so.1.0.1`:
18,076 Bytes, SHA-256
`c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` (PASS).
Die statische Getteranalyse E-XE164-228 stammt aus dieser Hash-gebundenen
Datei. Kein Input wurde verändert.

Akzeptierte Evidenz wurde zuerst abgeglichen: E-XE164-228 belegt den exakten
Getterkörper; E-XE164-232 belegt die Import-/`R_ARM_JUMP_SLOT`-Zuordnung von
IoDrvDal auf GOT-Position `0x16030` und den passenden Exportkandidaten bei
libdal `0x3464`; E-XE164-233 belegt den installierten Dateipfad/Kandidatenstand;
E-XE164-234 liefert den bereits disassemblierten Callerbereich und seine
Opcodewörter. Diese Beobachtungen wurden nicht nochmals über REA angefragt.
Die frühere REA-Abdeckung lieferte für diesen kleinen Worker kein direkt
auswertbares REA-Bytepaket. Für die fest begrenzten Rohbytes/Opcodewörter wurde
der dokumentierte Fallback GNU `arm-linux-gnueabihf-objdump`/`readelf` 2.44
verwendet. Python 3.13.5 führt den beigefügten Offline-Validator aus.

## Vollständige Instruktions- und Write-Matrix

Alle Opcodewörter sind die ARM little-endian Darstellung aus dem exakt
begrenzten objdump-Fenster. `r7 write` bewertet jede aufgeführte Instruktion.
Der explizite Speicher-Store im Caller ist eigens markiert; der PLT- und
Gettercode enthält keinen Store.

| ELF VA | Opcode | Instruktion / Bereich | Registerwirkung sichtbar in Instruktion | Speicherzugriff / Store | `r7` write |
|---:|---:|---|---|---|---|
| `0x2f44` | `e5973000` | `ldr r3,[r7]` | schreibt `r3` | liest Wort `[r7]` | nein |
| `0x2f48` | `e5843618` | `str r3,[r4,#0x618]` | keine explizite GPR-Zielschreibung | schreibt Wort `[r4+0x618]` | nein |
| `0x2f4c` | `ebfff6a0` | `bl 0x9d4` | Kontrolltransfer; schreibt Rücksprungadresse in `lr` | kein expliziter Store | nein |
| `0x2f50` | `e5903010` | `ldr r3,[r0,#0x10]` | schreibt `r3` | liest Wort `[r0+0x10]` | nein |
| `0x2f54` | `e5970000` | `ldr r0,[r7]` | schreibt `r0` | liest Wort `[r7]` | nein |
| `0x2f58` | `e12fff33` | `blx r3` | indirekter Kontrolltransfer; schreibt Rücksprungadresse in `lr` | kein expliziter Store | nein |
| `0x9d4` | `e28fc600` | `add ip,pc,#0` | schreibt `ip` | kein Zugriff | nein |
| `0x9d8` | `e28cca15` | `add ip,ip,#0x15000` | schreibt `ip` | kein Zugriff | nein |
| `0x9dc` | `e5bcf654` | `ldr pc,[ip,#0x654]!` | schreibt `ip` durch Pre-Index-Writeback und lädt `pc` | liest Zielwort an berechnetem Slot; kein Store | nein |
| `0x3464` | `e59f0004` | `ldr r0,[pc,#4]` | schreibt `r0` | liest Literalwort bei `0x3470` | nein |
| `0x3468` | `e08f0000` | `add r0,pc,r0` | schreibt `r0` | kein Zugriff | nein |
| `0x346c` | `e12fff1e` | `bx lr` | Kontrolltransfer über `lr` | kein Zugriff | nein |
| `0x3470` | `00010ce4` | Literal-Datenwort, keine Instruktion | — | vom `ldr` bei `0x3464` gelesen | — |

### PLT/GOT-Bedingung und Pfadtrennung

Der PLT-Code wird hier nur bis zum berechneten Relocation-Slot verfolgt. Mit
ARM-A32-PC-Werten berechnet `0x9d4` zunächst `ip=0x9dc`; `0x9d8` addiert
`0x15000`, und die Pre-Index-Adressierung bei `0x9dc` addiert `0x654` und
lädt `pc` aus `0x16030`. E-XE164-232 identifiziert `0x16030` als die
`R_ARM_JUMP_SLOT`-Relocationposition für den Import. Diese Rechnung belegt
den PLT-Zielslot, nicht dessen Inhalt.

**(a) Bedingter bereits-aufgelöster Pfad.** Unter der zusätzlichen Annahme,
dass der Slotwert zur Laufzeit genau auf `libdal.so.1.0.1`-Getter `0x3464`
bezogen auf dessen Load Bias zeigt, ist das Ziel der obige Getter. E-XE164-228
belegt für diesen Getter die drei Befehle `ldr r0,[pc,#4]`, `add r0,pc,r0`,
`bx lr`; das Literal `0x10ce4` liegt bei `0x3470`. Diese Befehle ändern nur
`r0`/Kontrollfluss und lesen das Literal. Der konditionale Pfad erhält daher
den in diesem begrenzten Maschinencode sichtbaren `r7`-Wert bis zum Load bei
`0x2f54`.

**(b) Möglicher Lazy-Resolverpfad.** Vor einer Auflösung kann dieselbe PLT-
Instruktion über denselben GOT-Slot auf einen Resolverpfad führen. Dieser
Pfad und Resolvercode sind ausdrücklich ausgeschlossen. Es wird keine
Annahme über seine Register- oder Speicherwirkungen getroffen und aus den
PLT-Bytes allein wird keine bereits erfolgte Auflösung gefolgert.

### Lokaler Datenfluss und Alternativen

Der lokale Datenfluss ist: `[r7]` → `r3` bei `0x2f44` → Store von `r3` an
`[r4+0x618]` bei `0x2f48` → bedingter Getter-PLT-Aufruf → Laden von `[r0+0x10]`
nach `r3` bei `0x2f50` → erneutes `[r7]` in `r0` bei `0x2f54` → indirekter
Aufruf bei `0x2f58`. Die Instruktionen zwischen den zwei Loads schreiben
`r7` nicht. Die erste ist ein direkter Store in den separaten Ausdruck
`[r4+0x618]`; statisch ist unbekannt, ob dieser Ausdruck dieselbe oder eine
überlappende Speicheradresse wie `[r7]` bezeichnet. Das Ergebnis der zweiten
Speicherlesung kann deshalb nicht aus der ersten Lesung garantiert werden.

**Beobachtung:** lokale `r7`-No-Write-Pins und exakt ein Store im Callerfenster;
PLT-Ziel ist Slot `0x16030`; Getterkörper ist ein Drei-Instruktionspfad mit
Literal-Lesezugriff.

**Bedingte Schlussfolgerung:** Bei bereits aufgelöstem GOT-Slot, der auf genau
den untersuchten Getter zeigt, enthält der sichtbare PLT-/Getter-Maschinencode
keine Instruktion, die `r7` beschreibt, und keinen Store durch diesen Pfad.

**Alternative:** Falls die Slotauflösung noch in einem Resolverpfad landet,
ist dessen Wirkung hier unbekannt. Selbst im angenommenen Getterpfad kann der
explizite Caller-Store `[r4+0x618]` `[r7]` überlappen; damit ist die lokale
Wertgleichheit nicht bewiesen.

**Restunsicherheit:** Runtime-Slotinhalt, Resolververhalten, mögliche
Speicherüberlappung sowie konkrete Laufzeitwirkungen bleiben außerhalb dieser
statischen Evidence. Keine Calling Convention, Concurrency-Eigenschaft oder
Runtimeauflösung wird behauptet.

## Validator und Hashmanifest

`python3 validate.py` prüft beide Eingabegrößen/-Hashes, die exakten Rohbytes
aller drei Grenzen und jede im jeweiligen Codefenster dekodierte Instruktion
gegen die erwarteten Opcodewörter. Die Literalbytes werden separat durch den
rohen 16-Byte-Hash gebunden; E-XE164-228 klassifiziert sie als Daten. Der
Validator führt keines der ELF-Objekte aus. `manifest.tsv` hält Status,
Größen, Hashes, Werkzeug- und Scopeangaben fest. `SHA256SUMS` enthält alle
erzeugten Paketdateien außer sich selbst.

**Provenienz:** GPT-6 Luna, HIGH reasoning, Worker-Self-Check. Kein
unabhängiger Review. Runtime/Hardware: **NOT_RUN**.
