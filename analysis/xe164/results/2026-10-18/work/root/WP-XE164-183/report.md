> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-183 — direkte Caller von ELF-VA `0x277c`

## Ergebnis

**Befundstatus: VERIFIZIERT für den begrenzten statischen Rohscan; Caller-Eigentum und Semantik: OFFEN.** Ein vollständiger aligned A32-`BL`-Zielscan über die vier file-backed executable sections des exakten ELF findet genau zwei Wörter mit Ziel `0x277c`: `0x30cc: 0xebfffdaa` und `0x3de0: 0xebfffa65`. GNU ARM Objdump 2.44 dekodiert beide im jeweils erlaubten Fenster ebenfalls als `bl 0x277c`.

| Callsite | Exaktes Fenster | Sichtbare Inputs direkt vor dem Call | Unmittelbare Rückgabeverwendung |
|---|---|---|---|
| `0x30cc` | `[0x309c,0x30fc)`, 96 Bytes | `r3=0x8008` bei `0x30b0`; `r2=2` bei `0x30c0`; `r1=r7` bei `0x30c4`; `r0=r6` bei `0x30c8` | `r0` wird bei `0x30d0` nach `[sp,#8]` gespeichert |
| `0x3de0` | `[0x3db0,0x3dec)`, 60 Bytes | `r3=zero_extend16([r5])` bei `0x3dbc`; der Gleichheitszweig bei `0x3dc4` erreicht `r2=1`, `r1=r5`, `r0=r7` bei `0x3dd4..0x3ddc` | `r0` wird bei `0x3de4` mit null verglichen; bei null verzweigt `0x3de8` nach `0x3dcc` |

Die Ursprünge von `r6`, `r7`, `r5` und `r8` liegen außerhalb der festgelegten Fenster und bleiben **OFFEN**. Die nächstgelegenen Objdump-Beschriftungen belegen keine FunctionManager-Grenzen und werden nicht als Caller-Namen verwendet.

## Methode und Grenzen

Eingabe: `libIoDrvKbus.so.0.0.1`, 38.584 Bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`, ELF32 little-endian ARM. Der Validator liest ausschließlich die vier in `assignment.md` festgelegten executable-section-Bereiche als 32-Bit-Wörter und berechnet für bedingte A32-Branch-Class-Wörter mit Link-Bit das Ziel `site + 8 + sign_extend(imm24 << 2)`. Genau die beiden obigen Treffer zielen auf `0x277c`. Anschließend prüft er nur die für die zwei erlaubten Fenster relevanten Wörter direkt gegen die Eingabebytes.

REA-first ist durch die akzeptierte, hashgleiche WP096-Evidence erfüllt (Bericht `d7fd351d...756d`, Bundle `97e8916c...69cb`). Sie bindet den Zielkörper, enthält aber keine Caller-Abfrage. Ein neuer Ghidra-Import wurde wegen des dokumentierten identischen Hängers nicht wiederholt. Der gezielte Fallback verwendet Python 3.13.5, GNU ARM Objdump 2.44 und SHA-256, vollständig offline.

Alternative Erklärung: Ein branchförmiges Wort in einer executable section könnte eingebettete Daten sein. Beide Treffer sind aligned, werden im eng begrenzten Umfeld als `bl` dekodiert, besitzen unmittelbar sichtbare Registervorbereitung und nachfolgende Ergebnisverwendung. Das stützt die statische Callsite-Klassifikation, beweist aber weder Ausführung noch Erreichbarkeit.

**OFFEN/NOT_RUN:** Caller-Funktionsgrenzen und -namen, Record-/Profil-/API-Bedeutung, Herkunft der Objektregister, Zielwirkung, Laufzeit, VM, Netzwerk, Gerät und Hardware. Kein Workerbefund aus WP-XE164-182 dient als Evidenzbasis; jenes Paket bleibt wegen seiner offengelegten Bereichsverletzung `FAIL`.

## Prüfung

- Eingabeidentität: **PASS**.
- Vollständiger Rohscan der vier festgelegten Abschnitte und Zielarithmetik: **PASS**.
- Exakte Wörter in beiden erlaubten Fenstern: **PASS**.
- Laufzeit/Hardware: **NOT_RUN**.
- Review: Root Self-Review; kein unabhängiger Review behauptet.
