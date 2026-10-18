> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-098 — Statische Referenzen auf `FUN_0001277c`

## Gegenstand und Ergebnis

**VERIFIZIERT** — Eingabe ist `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/rootfs/usr/lib/libIoDrvKbus.so.0.0.1`, ELF/ARM, 38.584 Byte, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8` (vor Analyse geprüft). Ghidra 12.1.4 über REA 6.5.0 meldet für den exakten Einstieg `0x1277c` den nur standardmäßig erzeugten Namen `FUN_0001277c` (`dynamic=false`, `external=false`, Quelle `default`; Evidence `ev_2f7a5f7345b02ec38ff57694c3d15ee9f90e690582195d9d8f55c2c62dd8cd20`). An dieser exakten Adresse wurde kein dynamisches/exportiertes Symbol beobachtet.

Die vollständigen exakten eingehenden Adress-Xrefs lauten `0x130cc` und `0x13de0` (Ghidra-Xrefs `ev_d3937398d76059c286de9abdc53ca0fd3baefb923c86855b3c612197ff73ebe9`). Die Referenzdetails klassifizieren beide als direkte `UNCONDITIONAL_CALL`-Codekanten (`call=true`, `computed=false`, `indirect=false`, `data=false`), Quelle `default`, primär; es gibt an diesem Einstieg keine beobachtete Datentabellenreferenz (`ev_8991dd3cbe61f86396d14de3c5b74c6d4f8c1d5ec62ed4106d02f08a3bf0d40e`). Das ist eine Aussage über die von Ghidra erfassten statischen Referenzen dieser Datei und Analyse, nicht über globale Unerreichbarkeit.

## Adressräume

| Objekt | Ghidra-Adresse | ELF-Dateioffset | Laufzeitadresse |
| --- | ---: | ---: | --- |
| Ziel-Einstieg | `0x1277c` | `0x277c` (10.108) | OFFEN; nicht beobachtet |
| direkter Aufruf 1 | `0x130cc` | `0x30cc` (12.492) | OFFEN; nicht beobachtet |
| direkter Aufruf 2 | `0x13de0` | `0x3de0` (15.840) | OFFEN; nicht beobachtet |

Die Offsets stammen aus Ghidras Source-Byte-Zuordnung, Evidence `ev_b49ea0718e30a563d01f8175780fe304ded01b09528e57f95387d2ff19dcf865`, `ev_e124c5075e320df356acdb29f8594227d2e8158142c4645dc36a98c5a47d50b3` und `ev_dcdfcc93e3539529e5c3ddc908d319a7d9356d598fe1655f358f7c7dadc66b6b`. Ghidra-Adresse und ELF-Dateioffset sind verschiedene Koordinaten; die hier gemessenen Zuordnungen setzen keine Laufzeitbasis voraus. Es wurde keine Runtime beobachtet.

## Unmittelbare Vorgängerwerte

Die folgenden Registerstände sind statische, bedingte Beobachtungen am jeweiligen `bl`; sie benennen keine Funktionssignatur oder Feldsemantik.

1. **Aufruf bei Ghidra `0x130cc` / Datei `0x30cc`**: Die Folge `ldrh r2,[r5,#0x18]` (`0x130ac`), `movw r3,#0x8008` (`0x130b0`), `cmp r2,r3` (`0x130b4`) und `bne 0x130d0` (`0x130bc`) rahmt den Pfad. Beim nicht übersprungenen Pfad setzt der Code `r2=2` (`0x130c0`), `r1=r7` (`0x130c4`) und `r0=r6` (`0x130c8`) und ruft bei `0x130cc` direkt `0x1277c` auf. Sichtbarer Zustand unmittelbar am Aufruf: `r0=r6`, `r1=r7`, `r2=2`, `r3=0x8008`; der Pfad ist durch Gleichheit des zuvor verglichenen `r2` und `r3` bedingt. Evidence für den Call: `ev_8760fc6594b13842515c3d0c114eabb033ab61fd84615bbcd60880020e45294d`; Registeraufbau ist im Bundle pro Instruktionsadresse enthalten.

2. **Aufruf bei Ghidra `0x13de0` / Datei `0x3de0`**: Im unmittelbar davor sichtbaren Pfad laden `0x13da4` und `0x13db0` Werte aus `[r5,#0x14]` bzw. `[r5,#0x4]`; nach `ldrh r3,[r5]` bei `0x13dbc` vergleicht `cmp r3,r8` bei `0x13dc0` und `beq 0x13dd4` bei `0x13dc4`. Auf dem genommenen Gleichheitspfad setzt der Code `r2=1` (`0x13dd4`), `r1=r5` (`0x13dd8`) und `r0=r7` (`0x13ddc`), bevor `bl 0x1277c` bei `0x13de0` ausgeführt wird. Sichtbarer Zustand unmittelbar am Aufruf: `r0=r7`, `r1=r5`, `r2=1`, `r3` ist der zuvor geladene Halbwortwert aus `[r5]` und auf diesem Pfad gleich `r8`. Das ist eine Pfadbedingung, keine Laufzeitmessung. Evidence für den Call: `ev_ec28fa12e0577dd55b9cdd246790f0ce98f78e35234c60bcb660e088584fcd2a`.

## Kandidatengrenzen und Init-Publikationslanes

Die fehlende Ghidra-Prozedurzuordnung an den Call-Sites hebt die bereits unabhängig belegten Kandidatenbereiche und ihre statischen Init-Publikationslanes nicht auf. Die Kandidaten bleiben Bereiche/Einträge; dieser Bericht weist ihnen keine formale Funktionsidentität oder Feldsemantik zu.

| Call-Site | Zugeordneter begrenzter Kandidat | Statische Init-Publikation | Einordnung |
| --- | --- | --- | --- |
| Ghidra `0x130cc` / Datei `0x30cc` | E-XE164-098: Datei/ELF-Code `[0x2eb8,0x313c)` (letzte Instruktion bei `0x3138`); zugeordneter Literalpool `[0x313c,0x3158)`, also Envelope bis Dateioffset `0x3157` inklusive | `IoDrvKbus_Init` bildet `0x2eb8`, speichert die Adresse bei Ghidra `0x14830` mit DATA-Referenz auf `0x12eb8`, staged sie in d17 und publiziert d17-Lane 0 am Store Ghidra `0x148e4` nach `r0+0x634` | Der Call-Site-Dateioffset `0x30cc` liegt im Codebereich. Unmittelbare Aufrufform: `r2=2` nach dem beobachteten `0x8008`-Gleichheitsguard. |
| Ghidra `0x13de0` / Datei `0x3de0` | E-XE164-096: begrenzter Datei/ELF-Kandidat `[0x36c0,0x3e54)`; letzte inklusive Grenze `0x3e53`, nächste Dynsym-Grenze exklusiv `0x3e54` | `IoDrvKbus_Init` stellt den Eintrag `0x136c0` zusammen und publiziert ihn mit den drei Nachbareinträgen am Store Ghidra `0x148a8` in der vierten 32-Bit-Position ab Basis `r0+0x34`, also `r0+0x40` | Der Call-Site-Dateioffset `0x3de0` liegt innerhalb des begrenzten Kandidaten. Unmittelbare Aufrufform: `r2=1` im beobachteten Record-Halbwort-Gleichheitspfad. |

Fresh-REA-Instruktionsbelege bestätigen die Kandidateneinstiege samt Init-Datenreferenzen: `0x12eb8` hat eine DATA-Referenz von `0x14830` (`ev_c276b44f9b7f78688c283a46c289bd8d800d92599f71e66dd3828f79c6718c52`); `0x136c0` hat eine DATA-Referenz von `0x14874` (`ev_fb250a617831a7c58a7f676d4d972cd6736d73f3486473ab463ca0c3709df5e2`). Fresh-REA bestätigt außerdem die Instruktionen `vst1.32 {d16,d17},[r3]` bei `0x148e4` (`ev_227edb89be0fc3a2d2f4c279fba4d9c2c4d6646601e5ae9d5ed61fe53435b394`) und `vst1.32 {d18,d19},[r3]` bei `0x148a8` (`ev_be89f84e738bbf6b26d28719ef4b1a540b10b9752aaf1a41015db9a238cefce7`). Die Kandidaten-/Lane-Ableitungen selbst stammen aus den vorher akzeptierten privaten Evidenzpaketen E-XE164-098 und E-XE164-096:

- E-XE164-098 / [WP-XE164-088](../WP-XE164-088/report.md): `report.md` SHA-256 `b9a782decc090c683e9f86fb8f5c2a52ba607b4d3da6349853261049e1351d1e`; `rea-evidence.json` SHA-256 `a20bfb32dc55a85abdce9c98e3b949a2767074b2e474464292e19c673723f7d4`; `init-publication.tsv` SHA-256 `02d22b87ac793b7d482074b297a7b11f9dbe36ed4d00f1b864cba04792a29ae0`. Das Paket begrenzt den Code auf Datei/ELF `[0x2eb8,0x313c)` und den Literalpool auf `[0x313c,0x3158)`, und belegt die DATA-/Stack-/Lane-Kette bis `r0+0x634`.
- E-XE164-096 / [WP-XE164-084](../WP-XE164-084/report.md): `report.md` SHA-256 `4a35564871102f9936f4923269fa2baa5ad5e49b20fd0a5ba195da862011004c`; `rea-evidence.json` SHA-256 `aa2cc6ed2200df0ef1fe8ea227e7cd5fc32de984e60a5586ff63c6f2ac5773b3`; `controlflow-callsites.tsv` SHA-256 `5032866011035fbf122510c549d59885b55bb3ca391c798bc0c17bd62d6a1464`. Das Paket begrenzt den Kandidaten auf `[0x36c0,0x3e54)` und belegt die Init-Publikation an `r0+0x40`.

Die SHA256SUMS beider Quellpakete wurden in ihrem jeweiligen Paketverzeichnis erfolgreich geprüft. Die tatsächliche Laufzeit-Ausführung dieser Init-Stores und die Frage, ob eine Zielprofilkonfiguration einen dieser Aufrufpfade erreicht, bleiben außerhalb der Evidenz und werden hier nicht behauptet.

## Geltungsgrenze, Alternativerklärung und Restunsicherheit

**VERIFIZIERT** — `resolve_containing_procedure` findet für beide Call-Sites keine zugeordnete formale Ghidra-Prozedur (`not_in_procedure`; Evidence `ev_4826f1893cc733a48ab508ccb67df750ef3d20cc928a4fd27a8f3e63ce8615fd` und `ev_5e89d919ec9b6c4e529a6430f8957f0bc69c9f8b646a43acd980eb68224415b9`). Die Candidate-Zuordnung und Init-Publikation sind über die separat akzeptierten Evidence-Pakete belegt (siehe vorherigen Abschnitt); sie vergeben keine formale Ghidra-Prozeduridentität. Die Caller-Abfrage liefert eine leere Liste mit **partieller** Abdeckung und meldet ausdrücklich, dass sie Quellen von zwei Call-Referenzen in den Zielkörper auslässt (`ev_a5e9e2282c7510ae0514479e994398b9ddd5da2e958f8d4178289162b6c5901a`).

**Alternativerklärung / OFFEN** — Ghidra ordnet beide Quelladressen keiner formalen Prozedur zu; die angenommenen Kandidatenidentitäten und Grenzen stammen aus den separat akzeptierten, ausdrücklich begrenzten Instruktionspaketen. Ein Kandidatenbereich mit statischem Init-Store belegt eine statische Adressbindung, aber nicht die Laufzeit-Ausführung des Init-Pfads oder spätere Aufrufe unter einem bestimmten Zielprofil. Fehlende Prozedurzuordnung und partielle Caller-Liste beweisen keine globale Unerreichbarkeit.

Nicht untersucht wurden der Funktionskörper `0x1277c..0x12e7f`, andere Bibliotheksoperationen, Providerkörper, Zielprofilsemantik, Runtime, Geräte, Netzwerk, VM oder Hardware. Es wurden keine Repositorydateien oder gemeinsamen privaten Dateien geändert.

## Werkzeuge und Prüfstatus

- REA `rea-agents` / Server 6.5.0; Ghidra 12.1.4; Analyseprofil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.
- **PASS** — Eingabe-SHA-256 stimmt mit dem vorgegebenen Wert überein.
- **PASS** — Semantischer Validator prüft Eingabeidentität, beide direkten Call-Xrefs samt bedingten Vorgängerwerten, Adresszuordnungen, begrenzte Symbol-/Caller-Aussagen und Statussprache gegen das kanonische REA-Bundle.
- **PASS** — `sha256sum -c SHA256SUMS` für die Worker-Ausgabe.
- **NOT_RUN** — Laufzeit-, Integrations-, Geräte- und Hardwaretests; für diese ausschließlich statische Xref-Frage nicht ausgeführt.

## Evidenz

Das kanonische REA-Xref-/Registerbundle liegt in `rea-evidence-bundle.json` (43 Records, 373.310 Byte, 0 gespeicherte Unknowns). Der zweite kanonische Export `rea-publication-fresh-evidence.json` ergänzt acht frische REA-Records zu Kandidateneinstiegen, Init-Storeinstruktionen und Source-Mappings (33.162 Byte, 0 gespeicherte Unknowns). Die akzeptierten privaten Quellpakete bleiben an ihren absoluten Pfaden und SHA-256-Identitäten zitiert; sie wurden nicht in diese Ausgabe kopiert oder verändert.
