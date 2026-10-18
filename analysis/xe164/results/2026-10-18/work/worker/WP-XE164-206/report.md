> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-206 — statische ELF-Bindungskette

## Befund

**ELF-Metadaten: VERIFIZIERT.** `libIoDrvDal.so.1.0.2` hat eine direkte
`DT_NEEDED`-Abhängigkeit `libdal.so`. Sein undefinierter dynamischer
Funktionssymbol-Eintrag `adi_GetApplicationInterface` (Dynsym-Index 14) wird
durch einen `R_ARM_JUMP_SLOT`-Eintrag referenziert. `libdal.so.1.0.1` exportiert
denselben Namen als globale, sichtbare Funktion in seinem `.dynsym` (Index 81).
Sein SONAME ist `libdal.so`, passend zum benötigten Namen. Damit ist eine
statische, direkte ELF-Bindungskette von Import zu passendem Export belegt.

**Konkrete Laufzeitwahl: OFFEN. Runtime/Hardware: NOT_RUN.** Die Metadaten
beweisen nicht, dass die Datei `libdal.so.1.0.1` zur Laufzeit geladen wird oder
dass genau ihr Export den PLT/GOT-Eintrag von IoDrvDal erfüllt. Pfadauflösung,
geladene Instanzen, globale Symbolreihenfolge/Interposition und tatsächliche
Relokationswerte wurden nicht beobachtet.

## Identität und Methoden

| Datei | Größe | SHA-256 | Identitätsprüfung |
|---|---:|---|---|
| `libIoDrvDal.so.1.0.2` | 25,976 | `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d` | PASS |
| `libdal.so.1.0.1` | 18,076 | `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` | PASS |

REA wurde zuerst für beide hashgebundenen ELF-Übersichten und Symbolinventare
verwendet. Ghidra 12.1.4 / REA composed workflow 1 erkannte Architektur ARM,
`.dynsym`, `.dynstr`, Versions-, Hash- und Relokationsbereiche. REA listete
`adi_GetApplicationInterface` als importiertes externes Symbol in IoDrvDal und
als Namen bei `0x13464` in libdal. Die REA-Symbolinventare kennzeichnen die
betroffenen Einträge jedoch nicht zuverlässig als dynamische Symbole
(`dynamic=false`) und liefern in diesem Workflow keine vollständige
`.dynamic`-/Relocation-/Versym-Korrelation. Diese einmalige Metadatenlücke ist
der dokumentierte Grund für den Fallback.

Anschließend wurde ausschließlich GNU `readelf` aus GNU Binutils 2.44 zur
Inspektion der vorgegebenen beiden ELF-Dateien verwendet, dazu `readelf -x`
für rohe Hash-Tabellenbytes. Kein weiterer Bibliotheks- oder Rootfs-Inhalt
wurde geöffnet. Toolversionen: GNU readelf 2.44; Python 3.13.5 für den lokalen
Validator; REA Ghidra 12.1.4 / Workflow 1. Die REA-Belege sind
`ev_ddee1478ba5248cbad795f24d4cdafc4e66b58e9a3e75c61501cf2e345ab4a46`
(IoDrvDal-Übersicht),
`ev_537d0f2ffa8b02fae9f6548896ba40e64ad4e20dd5f4d269f5425930ecbe4e33`
(IoDrvDal-Namen),
`ev_a40e925ba5e6499cd86d0c350ecb767487473d9b374e0de0522a6091e924252f`
(libdal-Übersicht) und
`ev_c995d97ca58a333d0544f8a888aafcae4dd3c4d641c2d0fddf4394796b242b6a`
(libdal-Namen).

## Direkt beobachtete Metadaten

### IoDrvDal: benötigter Name und Relocation

ELF32 little-endian, `ET_DYN`, ARM, EABI5 hard-float. `.dynamic` ist virtuell
bei `0x15ebc`, Datei-Offset `0x5ebc`, Größe `0x140` (320 Bytes). Die vollständige
`DT_NEEDED`-Liste in Tabellenreihenfolge lautet:

1. `liblibloader.so.0`
2. `libdal.so`
3. `libffi.so.8`
4. `libtypelabel.so`
5. `libglib-2.0.so.0`
6. `libgthread-2.0.so.0`
7. `liboslinux.so.0`
8. `libstdc++.so.6`
9. `libm.so.6`
10. `libgcc_s.so.1`
11. `libc.so.6`

`DT_SONAME` ist `libIoDrvDal.so.1`. Es gibt kein `DT_RPATH` und kein
`DT_RUNPATH` in IoDrvDal.

Die maßgeblichen Tabellenzeilen und Rohwerte:

| Tabelle | Zeile / Wert |
|---|---|
| `.dynsym` | Index `14`; `Value=0`, `Size=0`, `FUNC GLOBAL DEFAULT UND adi_GetApplicationInterface` |
| `.dynsym`-Eintragsoffset | `.dynsym` beginnt bei Datei-Offset `0x220`, `ELF32`-Eintrag `16` Bytes; Index 14 liegt bei `0x300` |
| `.rel.plt` | Offset `0x16030`; `r_info=0x00000e16`; `R_ARM_JUMP_SLOT`; Symbolindex `0x0e` / 14; Name `adi_GetApplicationInterface` |
| Relocationtabellenposition | `.rel.plt` beginnt bei Datei-Offset `0x8c0`, Eintrag 9 (nullbasiert), 8 Bytes pro `Elf32_Rel`, daher Datei-Offset `0x908` |
| Zielslot | `.got` virtuelle Basis `0x16000`, Datei-Offset `0x6000`; Slot bei virtuellem `0x16030`, Datei-Offset `0x6030` |
| Versionsymbol | `.gnu.version` Index 14 ist `1 (*global*)`; kein versionsgebundener Suffix/Anforderungsindex am Import |
| Hashabschnitte | `.hash`: Datei-Offset `0x118`, Größe `0xc8`; `.gnu.hash`: Datei-Offset `0x1e0`, Größe `0x40` |

`readelf -d` zeigt die zwei Hash-Tags (`DT_HASH=0x118`, `DT_GNU_HASH=0x1e0`),
`DT_SYMTAB=0x220`, `DT_STRTAB=0x410`, `DT_VERSYM=0x738`,
`DT_JMPREL=0x8c0`, `DT_PLTRELSZ=136`, `DT_PLTREL=REL`. Der Rohkopf von
`.hash` ist little-endian `nbucket=23`, `nchain=31`; `.gnu.hash` beginnt mit
`nbuckets=3`, `symoffset=24`, `bloom_size=2`, `bloom_shift=6`. Der Import hat
Index 14 und liegt damit vor dem GNU-Hash-`symoffset`; das ist kein
Laufzeitauflösungsbeleg.

### libdal: übereinstimmende Definition

ELF32 little-endian, `ET_DYN`, ARM, EABI5 hard-float. `.dynamic` ist virtuell
bei `0x13ee0`, Datei-Offset `0x3ee0`, Größe `0x120` (288 Bytes). Vollständige
`DT_NEEDED`-Liste:

1. `libgcc_s.so.1`
2. `libm.so.6`
3. `libglib-2.0.so.0`
4. `libffi.so.8`
5. `liblibloader.so.0`
6. `libc.so.6`

`DT_SONAME` ist `libdal.so` und stimmt damit exakt mit IoDrvDals direktem
`DT_NEEDED`-Namen überein. `DT_RPATH` ist als String `--library=pthread`
vorhanden; `DT_RUNPATH` fehlt. Dieser ungewöhnliche statische Wert wird nur
wiedergegeben, nicht als funktionierender Suchpfad interpretiert.

| Tabelle | Zeile / Wert |
|---|---|
| `.dynsym` | Index `81`; `Value=0x3464`, `Size=16`, `FUNC GLOBAL DEFAULT 12 adi_GetApplicationInterface` |
| `.dynsym`-Eintragsoffset | `.dynsym` beginnt bei Datei-Offset `0x394`, Eintragsoffset `0x394 + 81*16 = 0x8a4` |
| Sichtbarkeit/Bindung | `GLOBAL`, `DEFAULT`; definiert in Abschnitt 12 (`.text`) |
| Versionsymbol | `.gnu.version` Index 81 ist `1 (*global*)`; keine symbolversionsspezifische Definition (`@VERSION`) angezeigt |
| Hashabschnitte | `.hash`: Datei-Offset `0x118`, Größe `0x25c`; `.gnu.hash`: Datei-Offset `0x374`, Größe `0x20` |

Der rohe `.hash`-Kopf ist little-endian `nbucket=67`, `nchain=82`; `.gnu.hash`
beginnt mit `nbuckets=2`, `symoffset=81`, `bloom_size=1`, `bloom_shift=5`.
Beide Hashverfahren sind also als dynamische ELF-Metadaten vorhanden. Ihre
Existenz beschreibt Suchindizes im jeweiligen Objekt, aber weder den zur
Laufzeit ausgewählten Objektpfad noch das Ergebnis der Symbolauflösung.

## Kette, Alternativerklärung und Grenzen

Die belegte statische Kette ist: IoDrvDal hat `DT_NEEDED "libdal.so"`;
IoDrvDal-Dynsym 14 ist ein unversionierter undefinierter `FUNC GLOBAL DEFAULT`
mit Namen `adi_GetApplicationInterface`; seine `.rel.plt`-Relocation ist
`R_ARM_JUMP_SLOT` auf GOT-Adresse `0x16030`; libdals SONAME lautet `libdal.so`;
libdal-Dynsym 81 ist die namensgleiche definierte `FUNC GLOBAL DEFAULT` mit
Größe 16 und Wert `0x3464`. Es gibt somit einen direkt benötigten, passenden
Exportkandidaten in der angegebenen libdal-Datei.

Eine alternative Laufzeitquelle bleibt möglich: Ein anderes bereits
aufgelöstes/global sichtbares Objekt könnte denselben unversionierten Namen in
der tatsächlichen Lookup-Reihenfolge bereitstellen. Zusätzlich zeigen beide
Dynsym-Inventare Importe von `LibraryLoader_LoadSymbol`; das macht einen
separaten dynamischen Symbolsuchpfad als Möglichkeit sichtbar, beweist aber
nicht, dass dieser Pfad gerade den hier untersuchten PLT-Aufruf bedient. Keine
Disassemblierung oder Funktionssemantik wurde untersucht.

Offen bleiben mindestens: welcher konkrete Pfad/Dateiinhalt als `libdal.so`
geladen würde; ob ein anderes Objekt den unversionierten Namen interponiert;
welche Suchpfade und Loaderzustände gelten; und welcher Wert nach Relokation im
GOT-Slot steht. Deshalb bleibt die konkrete Runtimebindung **OFFEN**. Es werden
keine Aussagen zu API-/ABI-Verträgen, Funktionsprototypen, Hardware oder
Busverhalten abgeleitet.

## Validator und Integrität

`python3 validate.py` prüft Eingabehashes und die in diesem Bericht
behaupteten `DT_NEEDED`-/SONAME-/RPATH-/RUNPATH-, Dynsym-, Relocation-,
Versions- und Hashkopf-Metadaten mit GNU `readelf` gegen die beiden Dateien.
Der erwartete Endstatus ist PASS. `SHA256SUMS` deckt die erzeugten
Berichtsdateien ab; Prüfergebnis und alle Hashwerte werden beim Abschluss
protokolliert. Der Validator führt die ELF-Dateien nicht aus.
