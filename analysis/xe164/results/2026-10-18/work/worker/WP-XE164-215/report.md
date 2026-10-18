> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-215 — statischer Getter-PLT/PLT0-Pfad

## Ergebnis

**Befundstatus: VERIFIZIERT** für die statisch sichtbaren Instruktionen, Bytes, die eine passende JUMP_SLOT-Relokation und den Dateiinhalt des zugehörigen GOT-Slots. Der Pfad schreibt `r7` vor dem indirekten Transfer nicht. Er schreibt aber das eingehende `lr` über den eingehenden `sp` auf den Stack: `push {lr}` in PLT0 speichert ein Wort an der Adresse `sp_in - 4` und aktualisiert `sp` auf diesen Wert. Das ist ein Speicherzugriff über einen vom Aufrufer übernommenen Stackzeiger, kein beobachteter Zugriff über einen beliebigen Caller-Pointer.

## Identität, Werkzeuge und Geltungsbereich

Eingabedatei: `FW31-IODRVDAL-1.0.2`, 25.976 Bytes, SHA-256 `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`. ELF32 little-endian, ET_DYN, ARM, EABI5 hard-float. Der GNU ARM Fallback meldet GNU binutils `objdump` und `readelf` Version 2.44.

REA wurde zuerst mit `mcp__rea__inspect_binary_layout` für genau diese Datei aufgerufen. Die beobachtete Lücke war `provider_unavailable`: `REA_PWNTOOLS_PYTHON` war nicht konfiguriert (`executable_path` leer); REA verlangte ein caller-supplied Python mit pwntools 4.15.0, pyelftools 0.33 und Unicorn 2.1.2. Es wurde keine Installation oder Konfigurationsänderung versucht. Danach kam der lokale GNU ARM/readelf/Rohbyte-Fallback zum Einsatz.

Die Prüfung ist auf Datei-/ELF `[0x0954,0x0968)` (PLT0 einschließlich Literalwort bei `0x0964`), `[0x09d4,0x09e0)` (Getter-PLT-Stub), genau die `adi_GetApplicationInterface`-JUMP_SLOT-Relokation und den zugehörigen GOT-Slot ELF-VA `0x16030` / Datei-Offset `0x6030` begrenzt. Es wurden keine anderen PLT-Stubs und keine Instruktionen außerhalb dieser beiden PLT-Bereiche disassembliert.

## Beobachtungen und statische Ableitung

1. Der Getter-Stub `0x09d4` addiert `pc` (im ARM-Zustand gilt für diese Instruktion `pc = 0x09dc`) auf `ip`. Damit wird `ip = 0x09dc`; `0x09d8` addiert `0x15000`, also `ip = 0x159dc`.
2. `ldr pc, [ip, #0x654]!` an `0x09dc` liest von `0x159dc + 0x654 = 0x16030`, schreibt zugleich `ip = 0x16030` zurück und lädt den gelesenen Wert nach `pc`. Der exakte dynamische Symbolbezug ist durch `R_ARM_JUMP_SLOT` bei `0x16030` auf den undefinierten globalen Funktionssymbolnamen `adi_GetApplicationInterface` gebunden.
3. Der statische Dateiinhalt des Slots `0x16030` (Datei-Offset `0x6030`) ist `54 09 00 00`, also im Little-endian-Format `0x00000954`. Das bindet den Datei-/Linkzeitpfad bei diesem anfänglichen Slotinhalt an PLT0 bei `0x0954`; es beweist keine tatsächlich erfolgte Lazy-Auflösung.
4. PLT0 an `0x0954` führt zuerst `push {lr}` aus. In ARM-Stack-Schreibweise wird das eingehende `lr` an `[sp_in - 4]` gespeichert, und `sp` wird auf `sp_in - 4` aktualisiert.
5. `ldr lr, [pc, #4]` an `0x0958` liest das Literalwort bei `0x0964`, dessen beobachtete Bytes `9c 56 01 00` den Wert `0x0001569c` ergeben. `add lr, pc, lr` an `0x095c` verwendet `pc = 0x0964` und ergibt `lr = 0x16000`. Das nächste `ldr pc, [lr, #8]!` liest über die effektive Adresse `0x16008`, aktualisiert `lr = 0x16008` und lädt den neuen `pc` daraus. Der geladene Inhalt bei `0x16008` wurde nicht untersucht.

## Sichtbare Schreibmenge bis zum indirekten Transfer aus PLT0

- Register: Der Getter-Stub schreibt `ip` und `pc`; PLT0 schreibt `sp`, `lr` und `pc`. In den abgedeckten Instruktionen ist kein Schreibziel `r7`.
- Speicher: eine explizite Wortschreibung von eingehendem `lr` nach `[sp_in - 4]` durch `push {lr}`. Die anderen abgedeckten Speicherzugriffe sind Lesezugriffe: Getter-GOT-Slot `0x16030`, PLT0-Literal `0x0964` und das von PLT0 adressierte Wort `0x16008` für den letzten indirekten Transfer.
- Nicht erfasst sind Effekte, die der Zielcode am geladenen `pc` auslöst, sowie Laufzeitänderungen am GOT nach dem Dateiabbild. Der Inhalt von `0x16008` und sein Ziel wurden nicht inspiziert.

## Alternativerklärung und Restunsicherheit

Der Dateiinhalt `0x16030 = 0x954` ist konsistent mit einem noch nicht aufgelösten JUMP_SLOT-Einstieg in PLT0. Eine bereits umgeschriebene GOT-Seite im Prozess könnte zur Laufzeit einen anderen Wert enthalten. Diese statische Prüfung beobachtet weder Lazy-Ausführung noch Laufzeit-GOT-Inhalte, dynamischen Loader-Code oder Registererhaltung nach dem PLT0-Transfer. Sie spezifiziert keinen ABI-/Calling-Convention-Vertrag. Der Push betrifft den aus dem Aufrufer übernommenen Stackzeiger; aus dem Bytecode folgt kein zusätzlicher caller-sourced Puffer- oder Objektzeiger-Schreibzugriff.

## Validator und Status

**Validator: PASS** — `python3 validate.py` reproduzierbar prüft die Eingabegröße und den SHA-256, GNU-ARM-Toolversionen, die drei Rohbytebereiche, beide begrenzten Disassemblierungen, die Getter-Relokation samt Dynsym, den GOT-Dateiwert und die Hashes von Bericht, Rohdatensatz und Validator. Anschließend `sha256sum -c sha256sums.txt` prüfen; dieses selbstreferenzfreie Manifest enthält auch den Hash von `validation.txt` (das Manifest hasht sich nicht selbst).

Teststatus: **PASS** für diese statische, begrenzte Prüfung; tatsächliche Ausführung bleibt **NOT_RUN**.

## Erzeugte Dateien

- `report.md` — Befund und Grenzen.
- `disassembly.raw.txt` — exakte Fallback-Ausgaben und Rohbyte-Fundstellen.
- `validate.py` — deterministischer Offline-Validator; erzeugt `validation.txt`.
- `validation.txt` — vom Validator erzeugtes Ergebnisprotokoll.
- `sha256sums.txt` — SHA-256-Manifest für Eingabedatei und erzeugte Ergebnisdateien außer dem Manifest selbst.
