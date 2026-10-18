> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-132 — IoDrvDal `ComponentEntry`-Callsite `0x1452C`

## Ergebnis

**VERIFIZIERT:** Im exakten IoDrvDal-Binary lädt `ComponentEntry` vor dem optionalen indirekten Call `0x1452C` den Callzielwert aus dem Eingabezeiger an `+0x28` nach `r2` (`0x14510`). `cmp r2,#0` prüft diesen Wert; `beq 0x14530` überspringt den Call, wenn er null ist. Im nicht-null Pfad kopiert `0x14528` den Registerwert `r1` nach `r0`; `0x1452C` ist `blx r2`. Der Zielwert stammt daher statisch aus `*(input + 0x28)`, während die tatsächlich aufgerufene Adresse zur Laufzeit **OFFEN** bleibt.

**VERIFIZIERT:** Am Call sind die sichtbaren Registerwerte aus der lokalen Instruktionsfolge:

| Register | Wert/Quelle unmittelbar bei `blx r2` | Callsite-Rolle |
|---|---|---|
| `r0` | `0x10062001`, durch `cpy r0,r1` bei `0x14528` | erstes Registerargument (belegt durch den bis dahin unveränderten Literalwert, den `ComponentEntry` auch bei `0x14498` in Eingabewort 0 schreibt) |
| `r1` | `0x10062001`, geladen aus Literalreferenz bei `0x14460`, danach bis zum Call nicht geändert | sichtbarer Registerwert; keine vollständige Callee-Signatur belegt |
| `r2` | `*(input + 0x28)`, geladen bei `0x14510` | **indirektes Callziel**, nicht als gewöhnliches Argument gezählt |
| `r3` | Adresse `DAT_00026090` (Ghidra-Adresse), berechnet bei `0x144E8`; zuvor wird `*(input + 0x34)` an `[r3]` gespeichert | sichtbarer Registerwert; zeigt auf den globalen Slot, nicht auf die Eingabebasis |
| Stackargumente | keine explizite Übergabe zusätzlicher Argumentwörter für diesen Call beobachtet | Funktionsprototyp und Zahl erwarteter Stackargumente bleiben unbekannt; der Frame enthält lokale temporäre Werte |

**VERIFIZIERT (nur sichtbare direkte Argumentaliasse): NEIN.** Die sichtbaren direkten Quellen für `r0`, `r1` und `r3` sind der Literalwert `0x10062001` beziehungsweise die globale Adresse `DAT_00026090`; keine dieser Quellen ist datenflussgleich mit der gesicherten Eingabebasis oder mit `input + 0x34`. Für zusätzliche Stackargumente wurde keine explizite Einrichtung beobachtet. `r2` ist der Callzielregisterwert und stammt aus dem Inhalt bei `input + 0x28`; er ist nicht selbst ein sichtbares gewöhnliches Argument. Die frühere Lade-/Storefolge `0x14500..0x14504` übergibt den Inhalt von `input + 0x34` nicht direkt in ein Callargumentregister; sie schreibt ihn an `[r3]`, also den globalen Slot `DAT_00026090`. Der numerische Wert der Laufzeit-Eingabebasis ist hier nicht bestimmt; zufällige numerische Überlappung von Eingabebereich und globaler Adresse wird daher nicht ausgeschlossen.

**OFFEN:** Das ist keine Aussage vollständiger Aliasfreiheit. Der indirekte Callee könnte über den sichtbaren globalen Zeiger `r3`, andere globale Zustände, weitere nicht modellierte Register-/Stackkonventionen oder indirekte Aliaswege auf den Eingabespeicher zugreifen. Ob er Eingabe `+0x34` verändert, bleibt offen. Der Callzielkörper und sein Vertrag wurden nicht untersucht.

## Begrenzte Instruktionsspur

REA/Ghidra meldet `ComponentEntry` bei `0x14448`, Körper `0x14448..0x14623`. Die adressierte Spur bis zur Rückkehr aus dem Call lautet:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Die Zeile `0x14510` setzt `r2` aus Eingabe `+0x28`; `0x14514` überschreibt dagegen `r0` mit dem Wert aus Eingabe `+0x2C`, der bei `0x14520` nach `[r3+0x330]` gespeichert wird. Nach dem Nullguard setzt `0x14528` `r0` wieder auf den Literalwert `0x10062001`. `r1` bleibt seit dem Literal-Ladevorgang unverändert. `r3` bleibt die für den vorherigen globalen Store berechnete Basis `DAT_00026090`. Zwischen `blx r2` und der Fortsetzung liegt kein weiterer Instruktionsblock; das Aufrufziel ist dynamisch und hat in der analysierten Instruktion keine direkte Zielreferenz.

### Adressräume

| Gegenstand | Ghidra-Adresse | ELF-Link-VA | Datei-Offset |
|---|---:|---:|---:|
| `ComponentEntry`-Einstieg | `0x14448` | `0x4448` | `0x4448` |
| Nullguard `beq` | `0x14524` | `0x4524` | `0x4524` |
| indirekter `blx r2` | `0x1452C` | `0x452C` | `0x452C` |
| Callfortsetzung | `0x14530` | `0x4530` | `0x4530` |
| `DAT_00026090` (BSS-Zeigerziel) | `0x26090` | `0x16090` | keine Dateiabbildung behauptet |

Für Code wurde die bereits in den WP119-Kontextbefunden belegte Ghidra-RAM-Basis `ELF-Link-VA + 0x10000` verwendet; die Codeposition ist in diesem ELF dateigebunden an denselben numerischen Offset wie die ELF-Link-VA. Das BSS-Ziel ist eine Ghidra-Adresse und kein initialisierter Dateiinhalt.

## Eingaben und Methode

| Eingabe | Größe | SHA-256 | Verwendung |
|---|---:|---|---|
| `libIoDrvDal.so.1.0.2` | 25.976 Byte | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` | exakt analysiertes ARM-ELF |
| WP-XE164-119 `report.md` | 8.459 Byte | `417bb844320d64a3cda06754b3aa95e835e7b9b5225413d570c3ca653a747fb6` | Eingabepointer, BSS-Slot und vorherige `+0x34`-Ladefolge |
| WP-XE164-122 `report.md` | 4.295 Byte | `d66a5be8d965d77d381860c77d9d5985c4fe5efcc9d8bd90f1646c65e1641aec` | Trennung früher Eingabe-Read und späterem Blockstore |
| WP-XE164-128 `report.md` | 4.907 Byte | `9bc728298381283b376eadb1a6448cbb1219f8af5d1cdc343245707ce79241b4` | begrenzter Kontext zum lokal aufgebauten Entry-Argument |

REA-first: `open_binary` mit Ghidra und hashgebundenes `analyze_function(0x14448)`, anschließend fokussierte REA-Instruktionsbeobachtungen für die Spur oben. REA: `rea-agents` 6.5.0, Ghidra 12.1.4, ARM `ARM:LE:32:v8`, Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Keine REA-Lücke erforderte einen GNU-/Rizin-Fallback; daher wurde keiner eingesetzt. Keine Ausführung des ELF.

REA-Pseudocode ist eine Decompilerdarstellung, kein Originalquelltext. Die Callee-ABI ist nicht vollständig signiert: Die Tabelle trennt daher den Callzielwert `r2` von den Registerinhalten und erfindet keine Funktionsparameterzahl. Stackargumente sind in diesem Callsite-Ausschnitt nicht als solche eingerichtet; das sagt nichts über versteckte Seitenkanäle oder einen nichtstandardmäßigen Zugriff des Zielkörpers auf den aktuellen Stackframe aus.

## REA Evidence

Kanonischer Sessionexport: `rea-bundle.json` (23 Records, 0 Unknowns). Primäre IDs:

- `ev_83dd313f76e8abe38946a299a444f5b337faca6e5bf8ac8619cb65ba98f53ede` — `ComponentEntry`-Dossier, Pseudocode, Instruktionsliste und begrenzte Register-/Datenflussbeobachtung.
- `ev_8460f96dbaa80e2f2c8f157edbd99deb0a53da296a8abd68ea280435a4344b25` — Read `[r0+0x34]` bei `0x14500`.
- `ev_7a9da1e7f626914461d97697d0d20467f3b286a42f2dbaa0e4f8e773ef13b834` — Store nach `[r3]` bei `0x14504`.
- `ev_804faa6916ca023554285b18c58e31923a7ed255f53a507d610134fb4f6a5bbb` — Callzielwert laden aus `[r0+0x28]` bei `0x14510`.
- `ev_6b402f2a126ba6303719e4a34a8922c3fb588ce528dc94b10f31a06d4d3ff0c5` — unabhängiger Wert laden aus `[r0+0x2c]` bei `0x14514`.
- `ev_2eb6d62563afe104d0deabaa17095a453f7cadddc81fd82f410326bc0b2688c0` — Nullvergleich bei `0x14518`.
- `ev_95e6018b081540745ba6beba8e44ebf35a6a3205dad85e6b4a7317691bb95d99` — Nullpfad-Zweig bei `0x14524`.
- `ev_a6799d335e35d4ffce0963168516e51063ae01b30d7b48499bdb287cf592fe6b` — `r0 <- r1` bei `0x14528`.
- `ev_aee2cd4f09db26202d2e6c2832f2c35a74616fe613faae44c45b53ebcb60925f` — `blx r2` bei `0x1452C`, berechneter Call ohne direkte Zielreferenz.
- `ev_55bd303031f5bd14a9bf1b1ad89b1e839b6c4406d87a4ecddf7e57e092bbad66` — Fortsetzung bei `0x14530`.
- `ev_bc78ddad706097b2c2e5c79b9237a31929ded68020c2e9046414399138d6da1a` und `ev_94e2a9f28fe7f0ed7c9206f8d12526092904942ca5b1e28f82ec812aaf70987c` — Literal-Lade- und Eingabewort-Store-Kontext für `0x10062001`.
- `ev_8c49ee23e9cf981e70092297f6ec1497ceb8a7705774db2b89338bccc16ec503` — Bildung der `r3`-Basis; in Verbindung mit der Dossier-Beobachtung zu `[r3]` als `DAT_00026090`.

## Alternativen, Restunsicherheit und Status

**HYPOTHESE:** Der Zielcode könnte `r3` als Zeiger benutzen und dadurch indirekt den von `input + 0x34` gespeicherten Wert lesen oder verändern. Diese Möglichkeit folgt aus der sichtbaren globalen Weitergabe, nicht aus einer Analyse des Zielkörpers. Ebenso kann der Zielwert an `input + 0x28` auf beliebige Laufzeitadressen zeigen; dieser Bericht qualifiziert keine Zielidentität.

| Prüfung | Status |
|---|---|
| Eingabegrößen und -Hashes | PASS |
| Registerspur, Nullguard, Callzielquelle | PASS |
| sichtbarer direkter Aliasvergleich für Argumentregister / explizite Stackargumente | PASS |
| versteckte/globale Aliaswege | OFFEN |
| Tests oder Ausführung | NOT_RUN |
| Runtime, VM, Netzwerk, Zielgerät und Hardware | NOT_RUN |
| unabhängiger Review | NOT_RUN |
| Self-Review | PASS |

## Dateien

`report.md`, `rea-bundle.json`, `validate_evidence.mjs` und `SHA256SUMS`. Validatorstatus und SHA-256 dieser Dateien sind in `SHA256SUMS` festgehalten.
