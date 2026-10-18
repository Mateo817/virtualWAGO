> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-117 — Def/Use von Basis `+0x620` im IoDrvDal-Generic-Loader

## Ergebnis

**VERIFIZIERT:** Der Generic-Loader `FUN_00012ddc` schreibt im Körper `0x12ddc..0x1331b` den konstanten Datenzeiger `&DAT_0002a234` nach `Basis + 0x620`, bevor er über den nach `IoDrvKbus_Init` aufgelösten Entry dieselbe Basis als Argument übergibt. Der Zeiger wird also im untersuchten Pfad explizit gesetzt; dieses Feld wird dort nicht bloß aus einem zuvor angelieferten Instanzbereich übernommen.

Der relevante Datenfluss im Ghidra-Pseudocode lautet: `param_1 = param_3 * 0x63c + param_1`, danach `*(undefined4 **)(param_1 + 0x620) = &DAT_0002a234`, und nach erfolgreichem Symbol-Load `(*local_78[0])(param_1)`. In der Instruktionsansicht wird `r4 = r0 + r11 * 0x63c` bei `0x130c0` berechnet und bei `0x130e8` `r3` nach `[r4,#0x620]` geschrieben. Der spätere indirekte Call steht bei `0x13010`; die Ghidra-CFG/Pseudocode zeigen die Loaderinitialisierung vor diesem Call. Die bloße numerische Adressreihenfolge bildet den Kontrollfluss hier nicht ab.

**OFFEN:** Die lokale Initialisierung belegt den Store der Adresse `0x2a234`, nicht den Inhalt des Speicherorts, auf den diese Adresse zeigt. Zwischen dem Store und dem Init-Call liegen weitere indirekte/dynamische Aufrufe. Ihre möglichen Alias-Schreibwirkungen auf `Basis + 0x620` sind durch diese Analyse nicht ausgeschlossen; daher ist der unveränderte Wert exakt am Call nicht unabhängig von solchen Seiteneffekten bewiesen.

## Fundstellen und Adressräume

Ziel: `libIoDrvDal.so.1.0.2`, 25.976 Byte, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. REA 6.5.0, Ghidra 12.1.4, ARM ELF, Profil `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Der Befund basiert auf `analyze_function` mit vollständigem, zusammenhängendem Procedure-Body `0x12ddc..0x1331b`; High-Pcode ist nicht abgeschnitten (`truncated=false`, keine ausgelassenen Operationen).

Die angegebenen Funktionsadressen sind Ghidra-Adressen. Für diese Textadressen ordnet REA sie durch Quellabbildung auf Datei-Offsets ab; im ELF liegt die Ghidra-RAM-Adresse um `0x10000` über der ELF-Link-VA. Die Datei-Offsets für Code entsprechen hier der ELF-Link-VA.

| Vorgang | Ghidra | ELF-Link-VA | Datei-Offset |
|---|---:|---:|---:|
| Stride-Konstante `0x63c` | `0x130b8` | `0x30b8` | `0x30b8` |
| Basisberechnung `mla r4,r3,r11,r0` | `0x130c0` | `0x30c0` | `0x30c0` |
| Store von `r3` bei `[r4,#0x620]` | `0x130e8` | `0x30e8` | `0x30e8` |
| indirekter Init-Call `blx r3` | `0x13010` | `0x3010` | `0x3010` |
| gespeicherte Zieladresse `DAT_0002a234` | `0x2a234` | nicht abgebildet | kein Datei-Offset |

Eine gezielte REA-Dateiabbildungsabfrage für `0x2a234` meldete `Address has no initialized file-backed memory`; deshalb wird dafür weder ein Datei-Offset noch ein ELF-Link-VA behauptet. Der Loader speichert die Ghidra-Datenadresse in der Instanz, nicht aus der Datei gelesene Zielbytes. Aus dem Offset wird keine API- oder Strukturfeldsemantik abgeleitet.

## Belegter Pfad und Abgrenzung

- **VERIFIZIERT:** Der in `param_3` gewählte Instanzschritt ist `0x63c` Byte. `0x130c0` bildet aus Eingangszeiger `r0`, Schrittindex `r11` und Konstante `0x63c` die Basis in `r4`. Das bestätigt die Basis-Stride-Beziehung, aber keine Allokationsgröße.
- **VERIFIZIERT:** Ghidra-Pseudocode setzt die Adresse `&DAT_0002a234` an `Basis + 0x620`; die Instruktion `0x130e8: str r3,[r4,#0x620]` bestätigt das Ziel im ARM-Code. Das High-Pcode am Store enthält als Zeigerkonstante `0x2a234` und als Ziel `r4 + 0x620`.
- **VERIFIZIERT:** Nach den Konfigurations- und Loaderprüfungen wird der durch `LibraryLoader_LoadSymbol` befüllte Stackslot indirekt aufgerufen. Pseudocode lautet `(*local_78[0])(param_1)`; ARM-Code enthält den berechneten Call `0x13010: blx r3`. Der Basiswert wird als einzig sichtbares Argument übergeben. Die Statische Argumentbindung ergibt sich aus Pseudocode und dem dem Call vorangehenden Registertransfer; eine API-Signatur wird daraus nicht abgeleitet.
- **VERIFIZIERT:** Der untersuchte Funktionskörper enthält damit eine konkrete Definition für `+0x620`; eine Prüfung materialisierter direkter Caller und weiterer upstream-Lanes war nach der Aufgabenbedingung nicht erforderlich. Für die Zielbestimmung wurden nur diese Definition, die Basisberechnung und der zugehörige Call im selben Körper verfolgt.
- **OFFEN:** Wegen dynamischer Seiteneffekte zwischen Store und Call ist nicht bewiesen, dass `0x2a234` am exakten Callzeitpunkt noch in `Basis + 0x620` steht. Es wurde keine Laufzeitbeobachtung vorgenommen.

WP-XE164-095 stützt unabhängig die Loadersequenz und dieselbe Basisübergabe, benennt aber den `+0x620`-Store nicht in seinem damaligen Fokus. WP-XE164-113/E-XE164-122 belegt auf der Empfängerseite für das separate, hashgebundene `libIoDrvKbus.so.0.0.1`, dass dessen Init-Einstieg von Eingabe `+0x620` weiterliest. Diese beiden Kontextquellen ersetzen nicht die hier gezogene direkte Store-Evidence des DAL-Binaries.

## Evidence und Teststatus

Primär-Evidence ist der kanonische REA-Record `ev_97f0686f7d6be484340fdfaa6fbc1538921260faeb2bfdae04b732260c614608` (`analyze_function`, Ghidra, Body und Assembly/Pseudocode/High-Pcode). REA-Dateiabbildungen: `0x130b8 → 0x30b8` (`ev_813b28edb0b87a7e262500e308557e817b53699f5e0d7ab25eb807c9290f2e28`), `0x130c0 → 0x30c0` (`ev_1caed202d6b47bf8ba83de9f5834bfcca58f3105f5dab87574e030e737125e58`), `0x130e8 → 0x30e8` (`ev_a07ce57604823758fd3322465fe1de5e3a2d1a4593849da54f9b1b7b40975048`), `0x13010 → 0x3010` (`ev_3b861408efd47c3b409bb4c6417d2461a70d7a7eeef2ad247c39f567b82bd4ab`). Bundle: 5 Records, 0 Unknowns.

| Prüfung | Status | Ergebnis |
|---|---|---|
| Zielgröße und SHA-256 | PASS | Stimmen mit der vorgegebenen ELF-Identität überein. |
| WP-XE164-095 Beobachtung/Bundle | PASS | Beide bereitgestellten Hashes stimmen. |
| WP-XE164-113 Kontextbericht | PASS | Hash stimmt mit der vorgegebenen E-XE164-122 Kontextbindung überein. |
| REA-Funktionsdossier und direkte Definition | PASS | Pseudocode, Instruktion und High-Pcode stimmen beim Store- und Basisziel überein. |
| REA-Dateiabbildungen | PASS | Alle vier relevanten Codeadressen haben eindeutige Datei-Offsets im Textbereich. |
| Lokaler Bundle-/Semantikvalidator | PASS | `validate_evidence.mjs` prüft Artefaktidentität, Kontextdateien, Dossier, Basisberechnung, Store, Call und Abbildungen. |
| Laufzeit, VM, Gerät oder Netzwerk | NOT_RUN | Offlinearbeit; nichts wurde ausgeführt oder kontaktiert. |

**Alternative Erklärung:** Der Code könnte absichtlich einen stabilen Zeiger auf eine separat initialisierte globale Speicherstruktur in jeder Instanz ablegen. Der Befund zeigt nur das Speichern ihrer Adresse an `+0x620`; ob oder wie die Zielstruktur vor diesem Loaderaufruf befüllt wird, liegt außerhalb des geprüften Ausschnitts.

## Erzeugte Dateien

| Datei | Beschreibung | SHA-256 |
|---|---|---|
| `report.md` | Dieser Bericht. | siehe `SHA256SUMS` |
| `rea-bundle.json` | Kanonischer REA-Export, 5 Records, 0 Unknowns. | siehe `SHA256SUMS` |
| `validate_evidence.mjs` | Lokaler Identitäts- und Evidence-Validator. | siehe `SHA256SUMS` |
| `SHA256SUMS` | Prüfsummenmanifest. | nicht selbst referenziert |

Self-Review: `validate_evidence.mjs` und die Prüfsummen kontrollieren Zielbindung sowie Schlussfolgerung im angegebenen statischen Scope. Kein unabhängiger Review oder Laufzeitnachweis wird behauptet.
