> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-119 — Herkunft des DAL-Globals `0x2A268`

## Befund

**VERIFIZIERT:** Im exakten DAL-Binary wird die globale Position `0x2A268` in `ComponentEntry` durch einen Blockstore initialisiert. Der Store bei Ghidra `0x14568` schreibt das Wort aus dem Eingabezeiger `param_1 + 0x34` an `0x2A268`. Das entspricht `param_1[0xD]`; der Wert ist damit statisch nicht als Konstante festgelegt. Die Quelle endet hier am an `ComponentEntry` übergebenen Eingabepointer.

**VERIFIZIERT:** `ComponentEntry` materialisiert einen zusammenhängenden 15-Wort-Bereich von `0x2A234` bis einschließlich `0x2A26C` aus Eingabeoffsets `+0x00` bis `+0x38`. Die Stores sind bei `0x1454C`, `0x14554`, `0x1455C` und `0x14568`. Damit liegt `0x2A268` im vierten und letzten Teilstore, vier Bytes nach dem beim ersten Store beschriebenen Basiswort `0x2A234`.

**VERIFIZIERT:** `0x2A234` hat im DAL-Binary genau zwei Ghidra-Xrefs: `0x130E8` und `0x1454C`. Der `ComponentEntry`-Store bei `0x1454C` ist als `WRITE` klassifiziert. Der Loader-Verweis bei `0x130E8` ist `DATA`: Dort wird die Adresse `&DAT_0002a234` in den bei WP-XE164-117 untersuchten Instanzpfad eingespeist, nicht der Inhalt von `0x2A234` gelesen. `0x2A268` hat genau einen direkten Ghidra-Xref, `0x14568`, als `WRITE`; für diese globale Position wurde kein direkter `READ`-Xref gefunden.

**VERIFIZIERT:** REA lehnt die Abbildung von `0x2A234` und `0x2A268` auf initialisierte Datei-Bytes mit „Address has no initialized file-backed memory“ ab. Der begrenzte GNU-`readelf`-Fallback bestätigt für dieses ARM-ELF `.bss` als `NOBITS`, ELF-Linkadresse `0x16088`, Dateifeld `0x6084`, Größe `0x4284`. Unter der für dieses Ziel bereits belegten Ghidra-RAM-Basis `ELF-VA + 0x10000` liegen die Globals bei ELF-Linkadressen `0x1A234` beziehungsweise `0x1A268`, also innerhalb `.bss`. Das Dateifeld einer `NOBITS`-Sektion ist kein Inhaltsoffset für diese Speicherpositionen; es wird daher kein Datei-Offset für die Globals behauptet. Aus der BSS-Klassifikation wird kein Laufzeit-Nullwert abgeleitet.

**OFFEN:** Der Inputwert ist an der Grenze von `ComponentEntry` ein extern angelieferter Wert. Ghidras eingehende Referenzen für `ComponentEntry` zeigen nur einen internen bedingten Kontrollflussverweis bei `0x14524`, keinen Aufruf der Funktion von einem anderen analysierten Codeort. Das entscheidet nicht, welcher externe Loader oder Aufrufer den Eingabepointer liefert. Außerdem liegt vor dem Blockstore der berechnete indirekte Call bei `0x1452C`; sein Ziel ist in den Procedure-Referenzen unresolved. Eine mögliche Änderung des Speichers hinter `param_1` durch diesen Call ist nicht ausgeschlossen. Belegt ist deshalb `param_1 + 0x34` als später gelesene Quelle, nicht der unveränderte Wert beim Funktionseintritt.

## Begrenzter Datenfluss und E122-Kontext

Ghidras Procedure `ComponentEntry` umfasst `0x14448..0x14623`. Die Instruktionen sichern bei `0x1444C` den Eingabezeiger `r0` in `r4`; bei `0x14530` wird er nach `r12` kopiert. Die Lade-/Store-Lanes lauten:

| Store in Ghidra | Quellbereich relativ zu `param_1` | Zielbereich |
|---|---:|---:|
| `0x1454C` | `+0x00..+0x0C` | `0x2A234..0x2A240` |
| `0x14554` | `+0x10..+0x1C` | `0x2A244..0x2A250` |
| `0x1455C` | `+0x20..+0x2C` | `0x2A254..0x2A260` |
| `0x14568` | `+0x30..+0x38` | `0x2A264..0x2A26C` |

Die letzte Lane beginnt mit `ldmia r12,{r0,r1,r2}` bei `0x14560`, nachdem `r12` durch die drei vorherigen Post-Inkrement-Ladevorgänge um `0x30` erhöht wurde. `stmia lr,{r0,r1,r2}` bei `0x14568` schreibt die drei Worte an die globalen Ziele `0x2A264`, `0x2A268`, `0x2A26C`; damit ist das mittlere Wort `r1`, Quelle `param_1 + 0x34`, der Wert an der untersuchten Position.

Der begrenzte E122-Kontext aus WP-XE164-113 auf dem separaten `libIoDrvKbus.so.0.0.1` beschreibt dessen `IoDrvKbus_Init`-Pfad: Eingabe-`+0x620` wird dereferenziert, anschließend wird am erhaltenen Pointer `+0x34` gelesen und der Slot bei `0x14CEC` indirekt aufgerufen. WP-XE164-117 belegt auf der DAL-Seite den Store von `&DAT_0002a234` nach Basis `+0x620`. Zusammengenommen qualifizieren diese Beobachtungen den hier untersuchten globalen Offset `0x34` als statische Quelle des von E122 adressierten Worts, unter den jeweils offenen Alias-/Seiteneffektgrenzen. Dieser Bericht rekonstruiert keine Struktur oder API und behauptet nicht, dass der Wert tatsächlich eine gültige Funktion ist.

## Adressräume, Artefakte und Methode

Ziel: `libIoDrvDal.so.1.0.2`, 25.976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. REA `rea-agents` 6.5.0, Provider Ghidra 12.1.4, ARM ELF, Analyseprofil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`.

| Gegenstand | Ghidra-Adresse | ELF-Link-VA | Datei-Offset |
|---|---:|---:|---:|
| DAL-Loader Xref `DATA` auf globale Basis | `0x130E8` | `0x30E8` | `0x30E8` |
| erster Blockstore | `0x1454C` | `0x454C` | `0x454C` |
| zweiter Blockstore | `0x14554` | `0x4554` | `0x4554` |
| dritter Blockstore | `0x1455C` | `0x455C` | `0x455C` |
| letzter Blockstore / Write auf `0x2A268` | `0x14568` | `0x4568` | `0x4568` |
| globaler Basisort | `0x2A234` | `0x1A234` | keine Dateiabbildung (`.bss`/`NOBITS`) |
| untersuchte Innenposition | `0x2A268` | `0x1A268` | keine Dateiabbildung (`.bss`/`NOBITS`) |

Für Codeadressen entspricht in diesem Ziel die ELF-Link-VA dem Datei-Offset; Ghidra verwendet die RAM-Basis `0x10000`. Die beiden Datenpositionen wurden nicht als Codeadressen behandelt.

**VERIFIZIERT:** REA-first. Direkt-Xrefs, Procedure-Pseudocode, Procedure-Assembly, typisierte Procedure-Referenzen und Procedure-Auflösung stammen aus demselben geöffneten Zielhash. GNU `readelf` wurde nur eingesetzt, nachdem REA für die Globals keine initialisierte Dateiabbildung meldete. Kein Binary wurde ausgeführt; kein VM-, Geräte- oder Netzwerkzugriff fand statt.

**Alternative Erklärung:** Der 32-Bit-Wert in `param_1 + 0x34` kann eine beliebige opake Eingabe oder Metadatenposition sein. Die getrennte E122-Analyse zeigt eine spätere Verwendung derselben relativen Position als indirektes Aufrufziel, beweist aber für sich allein nicht, dass der DAL-Eingabewert eine gültige Funktion bezeichnet oder zur Laufzeit unverändert weitergereicht wird.

## Evidence und Status

Primäre REA-Evidence im kanonischen Bundle `rea-bundle.json`:

- `ev_ee4b643c9fc443e3c7301b48fc7f45dd23b099ead83b1628215063a3c55f8b7c` — Xrefs auf `0x2A234`: `0x130E8`, `0x1454C`.
- `ev_c2c3affaebba45061a52db132a3fa470e802f7e309a1080dfd162e33ececb7a1` — Xref auf `0x2A268`: `0x14568`.
- `ev_7a38f6791cb84e2938be59a6ea1a81d53822b8667c37582789aee2469ef381a2`, `ev_9f54d376b25402f59289652060276d8190f1a11a8b6fd781f54603b536d520c9` — `ComponentEntry`-Pseudocode an den beiden Zielpositionen.
- `ev_e656ea59a91a152c0be5c4e7c1f9969be1edc08a10e5688922f0f544f9a16ed9` — Instruktionsliste von `ComponentEntry`.
- `ev_b52886c399777ed908f02ecc5773f6ef727c8e03a1570799a5743cd6c9172531` — typisierte ausgehende Referenzen von `ComponentEntry`, einschließlich der `WRITE`s in den Bereich `0x2A234..0x2A26C`.
- `ev_a2d153892ad3b44299d474032b1bd69b65eac125feaac7b00f1e6e5c2afa0cb2` — eingehende Procedure-Referenzen von `ComponentEntry`; keine externe Call-Referenz im analysierten Ziel.
- `ev_cef6081e549aa46ebb0dfc17ac1fde3bda78276279612ba0e207aa1444c50ca1`, `ev_a8877b1097d2f749d20cb3289ca59552a2da9c053c3a4f45b4f0672dea4fdb6a` — Loader-Pseudocode und typisierte Loader-Referenz auf `0x2A234` als `DATA`.
- `ev_164bf568b7ebd17e648e35d4b386e5b4901f59fe723e0708566d517cbee5cc39`, `ev_793d15597df6ce8f56c1ce28be70ad41a2db4255a68c0b89a0070963a3951d52`, `ev_f51eca0c1a1bf8696d252a530dbf08e4ca15fa9bc48127e0a110cbe399560e13` — Procedure-Auflösung der relevanten Source-Lanes.

Vorgegebene Kontext-Hashes vor Verwendung geprüft: WP-XE164-117 Bericht `6ac4a6e261a8d46bdac2ef1c069250ba6775f981f79189ec73e7fda629f491b1`, Bundle `344889b22f8bb2ba8eedad2f60263e7e8a8e3438923b61b0ff4641ccfbf7c487`; WP-XE164-113 Bericht `c9cf948b04dce517a38dbc85c55f7b56254daf5f772eac733ad8990a8389bc92`.

Tests: **NOT_RUN**. Artefaktvalidator: **PASS** — 12 REA-Records, 0 Unknowns, sechs erforderliche Evidence-IDs und sämtliche SHA-256-Einträge geprüft. Der Validator prüft Paketintegrität und Evidence-Referenzen, nicht die technische Analyse neu.

## Dateien

Dieses Arbeitspaket enthält `report.md`, das kanonische `rea-bundle.json`, `validate_evidence.mjs` und `SHA256SUMS`. Hashes stehen in `SHA256SUMS`.
