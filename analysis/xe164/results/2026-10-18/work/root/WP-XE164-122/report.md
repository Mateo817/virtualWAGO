> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-122 — Doppelter `ComponentEntry +0x34`-Datenpfad

## Ergebnis

**VERIFIZIERT:** Das exakte IoDrvDal-`ComponentEntry` liest dieselbe relative
Eingabeposition `+0x34` zu zwei verschiedenen Zeitpunkten. Vor dem optionalen
indirekten Call bei Ghidra `0x1452C` laden `0x14500..0x14504` den aktuellen
Wert aus Eingabe `+0x34` nach BSS `0x26090`. Nach diesem Call lesen die
Blockoperationen `0x14560..0x14568` die dann aktuelle Eingabe `+0x34` erneut
und schreiben sie nach BSS `0x2A268`, also an Basis `0x2A234 + 0x34`.

**VERIFIZIERT:** Der frühere BSS-Slot `0x26090` ist das statische Zielwort des
IoDrvDal-Calls bei `0x10ED0`, der den exakten String
`IoMgrConfigGetParameterValuePointer` und die Adresse des BSS-Zielslots
`0x260F0` erhält. Der spätere globale Bereich wird über den separaten
IoDrvDal-Loader weitergereicht: Dieser speichert `&0x2A234` bei
Instanzbasis `+0x620` und ruft danach den aufgelösten Driver-Init-Einstieg mit
derselben Basis auf. IoDrvKbus-Init liest über Eingang `+0x620` die geschachtelte
Position `+0x34`, speichert den Wert in BSS `0x2A1C0` und verwendet diesen
später als ungelöstes indirektes Callziel.

Damit ist eine vollständige statische Positionskette belegt:

`ComponentEntry input +0x34 (späterer Lesezeitpunkt)` →
`IoDrvDal 0x2A268` → `&0x2A234` an Instanz `+0x620` →
`IoDrvKbus Init: *(+0x620)+0x34` → `IoDrvKbus 0x2A1C0` →
indirekter Call `0x14CEC`.

Separat ist belegt:

`ComponentEntry input +0x34 (früherer Lesezeitpunkt)` →
`IoDrvDal 0x26090` → indirekter Call `0x10ED0` mit dem exakten Accessornamen.

## Geltungsgrenze und Alternative

**OFFEN:** Zwischen den beiden Reads von Eingabe `+0x34` kann der optionale,
statisch ungelöste Call bei `0x1452C` ausgeführt werden. Er erhält einen
anderen sichtbaren Wert in `r0`, könnte aber über Aliase trotzdem den Speicher
hinter dem gesicherten Eingabezeiger verändern. Daher ist nicht verifiziert,
dass `0x26090` und `0x2A268` zur Laufzeit denselben 32-Bit-Wert enthalten.

**HYPOTHESE:** Wenn der indirekte Call den Eingabespeicher an `+0x34` nicht
verändert, verteilen beide Pfade denselben vom externen `ComponentEntry`-Aufrufer
gelieferten Zielwert an Dal und Kbus. Das passt zur zweimal beobachteten
Registrierungsform, beweist aber weder die Callbackidentität noch eine
Funktionssignatur oder einen vollständigen Service-/Structvertrag.

Für den geplanten virtuellen Backend-Ersatz ist diese Kette relevant, weil sie
den Resolverpfad innerhalb des beibehaltenen Originalstacks verortet. Sie ist
kein Beleg dafür, dass der Emulator diesen Resolver selbst implementieren muss;
die konkrete untere Ersatzgrenze und Laufzeitverdrahtung bleiben getrennte
Architektur-/Runtime-Nachweise.

## Methode und Quellenbindung

REA/Ghidra 12.1.4 war die Primärquelle der akzeptierten Einzelbefunde. Diese
Root-Synthese wiederholte keine bereits erfolgreiche breite Analyse, sondern
verband die hashgebundenen Befunde E-XE164-119, E-XE164-122, E-XE164-124,
E-XE164-126 und E-XE164-128 und prüfte die begrenzten ARM-Instruktionen mit GNU
ARM Binutils 2.44 gegen die unveränderten Binärdateien. Pseudocode aus den
Quellpaketen ist Werkzeugableitung, kein Originalquelltext.

Verwendete Paketidentitäten:

- WP-XE164-109 Bericht `2b4e7d9e0aed9b409b94920fa199d632ae9c401975cf1d71654b715f35b69125`,
  Bundle `feac800252b47b22613f468c9724e1a5780d91a3eee5147c82e2dac98d5fd0fe`.
- WP-XE164-113 Bericht `c9cf948b04dce517a38dbc85c55f7b56254daf5f772eac733ad8990a8389bc92`,
  Bundle `dc5fc082c1e64000845a2c015c0e490e5a9d0159b323738ec48fbc361da8bec0`.
- WP-XE164-115 Bericht `f92c53e659a5c1514fdc00f271f14075c013bbf803e9b5d3eb3ce17b11e101ea`,
  Bundle `a762fb531199bf10ea912f485de6d8b2a2c6e48b4990eba91f7ab7765374037c`.
- WP-XE164-117 Bericht `6ac4a6e261a8d46bdac2ef1c069250ba6775f981f79189ec73e7fda629f491b1`,
  Bundle `344889b22f8bb2ba8eedad2f60263e7e8a8e3438923b61b0ff4641ccfbf7c487`.
- WP-XE164-119 Bericht `417bb844320d64a3cda06754b3aa95e835e7b9b5225413d570c3ca653a747fb6`,
  Bundle `b72a0686b56d63653828a5d65e7a3119ad7900a7b58d17c4d26d270aa3fe715b`.

Tests: Paket-/Hashvalidator **PASS**. Statische Instruktionsgegenprüfung
**PASS**. Runtime, VM, Netzwerk, Zielgerät und Hardware **NOT_RUN**.
Self-Review: GPT-6.1 SOL root; kein unabhängiger Review wird behauptet.
