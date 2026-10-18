> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-175 — unabhängiger Instruktions-Countercheck

## Ergebnis

**PASS — E-XE164-200s Kette wird innerhalb der angegebenen statischen Bereiche durch Instruktionen getragen.** Die beobachtete Kette lautet: Helper-Lokalwort `L+0x18` wird auf dem erfolgreichen Entry-Call-Lane in den CMLoad-Block `B+0x20` kopiert; `CMAddComponent` kopiert 52 Byte ab `B` in den bezogenen Block und schließt daher `+0x20` ein; auf dem erfolgreichen CMAdd-/Status-Lane wird der rohe CMAdd-Rückgabewert gesichert und über den gemeinsamen CMLoad-Rückgabepfad ausgegeben; AppLoad erhält dieses Rückgabewort in `r0`; AppLoad ruft CMInit nur bei `r0 != -1` und Ausgabe-Statuswort `==0`; CMInit lädt alle im geprüften Bereich beobachteten indirekten Call-Ziele aus `[input+0x20]`.

Das ist ein **statischer Codeflussbefund**, kein Laufzeitbeleg dafür, dass die Bedingungen tatsächlich eintreten oder dass irgendein konkreter Modul-/Treibername an diesen Pfad gebunden ist. E201 / DSO- oder IoDrvDal-Identität bleibt **HYPOTHESE** und ist nicht Gegenstand dieses Pakets.

## Bytegebundene Kette

Die genauen Instruktionsbytes, Quell-/Zielpositionen und Bedingungen stehen in `chain.tsv`. Wesentliche Offsetrechnung:

- Im Helper setzt `0x2FC55C` (`e24b005c`) den lokalen Basiszeiger `L = fp-0x5c`. `0x2FC654` (`e51b1044`) lädt `[fp-0x44] = L+0x18`; `0x2FC664` (`e5841020`) speichert dieses Wort nach `[r4+0x20]`. `r4` wurde am Helper-Eintritt aus `r0` übernommen. CMLoad setzt seine Blockbasis `B=fp-0x58` mit `0x2FFD04` und reicht `B` bei `0x2FFD44` an den Helper. Helper-Copyback ist nur nach dem rohen Entry-Call-Ergebnis `r0==0` erreichbar (`0x2FC5CC`/`0x2FC5D0`).
- `CMAddComponent` erhält `B` in `r5` (`0x2FD108`) und den Poolblock in `r4` (`0x2FD1AC`). Bei `0x2FD228..0x2FD23C` bewegen drei LDM/STM-Paare 48 Byte; `0x2FD244`/`0x2FD250` bewegen das abschließende Wort. Gesamtumfang: exakt 52 Byte `[B,B+52)`, darunter `B+0x20`.
- CMLoad speichert das CMAdd-Rohresultat bei `0x2FFDA8` in `r6`, testet vorher `-1`, dann testet es den vom Helper gespeicherten lokalen Status. Auf dem Lane mit CMAdd-Rohresultat ungleich `-1` und Status null wird `r6` nach `r4` bewegt (`0x2FFDC0`); nach dem direkten CMGetAPI-Aufruf führt der Branch bei `0x2FFDD0` zum gemeinsamen Pfad `0x2FFCC4`, der `r4` nach `r0` bewegt. Der CMAdd-Rückgabewert wird somit auf diesem Lane common-returned. Die Call-clobber-Regel wird beachtet: der relevante Wert liegt vor dem späteren Call in callee-saved `r4`/`r6`, nicht in volatilem `r0`.
- AppLoad ruft CMLoad bei `0x31A648` auf und prüft bei `0x31A650` den rohen Rückgabewert `r0` gegen `-1`; nur der Nicht-`-1`-Lane prüft das Outputwort `[fp-0x10]` auf null. Nur bei beiden Erfolgsbedingungen wird CMInit bei `0x31A66C` aufgerufen.
- CMInit übernimmt Eingabe `r0` in `r4` bei `0x3013AC`. Acht identifizierte indirekte Aufrufslots werden aus `[r4+0x20]` geladen; jeder Slot wird auf Null geprüft und nur ein Nichtnullslot an entsprechender Stelle indirekt aufgerufen. Die genauen Sites stehen in `chain.tsv` und `gate-table.tsv`.

## Beobachtete Abbruch-Gates

Die Kette kann vor beziehungsweise nach der Kopie an mehreren klaren Branches enden. Dazu gehören: Helper-Entry-Rückgabe ungleich Null; CMLoad-Initialsuche ungleich `-1` (früher Rückweg); MainLoad-Fehler-/Output-Null-Pfad; Helper-Rückgabe ungleich Null; nicht-null Ergebnisse der zwei früheren Blockslots; CMAdd-Rückgabe `-1` oder gespeicherter Status ungleich Null; AppLoad-Rückgabe `-1` oder Outputwort ungleich Null; CMInit-Eingabe `-1` oder Status-Halfword ungleich 2; sowie null gesetzte CMInit-Callslots. Innerhalb CMInit können außerdem gespeicherte Rückgabewerte früherer indirekter Calls und die erneut berechnete Halfword-Predicate spätere `+0x20`-Calls überspringen und in den gemeinsamen Ergebnis-/Hook-Lane führen. Details einschließlich Instruktionsbytes und beobachtetem Zielpfad sind in `gate-table.tsv` festgehalten.

## Alternativbefund und Restunsicherheit

Gegen eine uneingeschränkte Lesart spricht, dass diese Kette **bedingt** ist: Der Helper kopiert `L+0x18` nur nach rohem Entry-Ergebnis Null zurück; AppLoad kann vor CMInit durch zwei unabhängige Bedingungen zurückkehren; und CMInit ruft einen `+0x20`-Wert nur auf, wenn er nicht Null ist. Daher ist nicht belegt, dass ein Wert aus `L+0x18` in jedem Lauf im CMInit-Call tatsächlich ausgeführt wird. Auch lässt sich aus dem copy/noalias-Layout allein kein Datentyp oder API-/Callback-Vertrag ableiten.

Die vorgegebenen Ausschnitte belegen weder die konkreten Laufzeitwerte der Call-Ergebnisse noch Identität oder Semantik eines Moduls. Für die zwei früheren CMLoad-Blockslots ist nur das gelesene, bewachte Ziel und der Rückgabegate ausgewiesen; `r1`/`r2` werden nach dem Helper beziehungsweise ersten indirekten Call vom Caller nicht neu gesetzt und sind wegen Call-Clobber nicht bestimmbar. Unbekannte globale Aliase, Callee-Seiteneffekte und Ausführungsreihenfolge dynamischer Pfade bleiben außerhalb dieser Instruktionsprüfung.

## Reproduzierbarkeit und Status

- Binärhash und Größe stimmen mit der Zuweisung überein; GNU ARM objdump 2.44, GNU readelf 2.44. Ziel ist ELF32 little-endian ARM; Disassembly-Adressen sind Link-VA.
- Vollständige, nur auf die freigegebenen Extents begrenzte Instruktionsextrakte: `extract-helper.txt`, `extract-cmload.txt`, `extract-cmadd.txt`, `extract-appload.txt`, `extract-cminit.txt`.
- Keine Originalquelle, keine zusätzliche Runtime-/VM-/Netz-/Geräte-/Hardwareaktion. Keine gemeinsamen Dateien geändert.
- E200 Positionskette: **PASS** (statischer bedingter Instruktionsbefund).
- `validate.py`: **PASS** nach Ausführung; `SHA256SUMS`: **PASS** nach Ausführung.
- Tests/Ausführung auf Runtime oder Ziel: **NOT_RUN**. Geräte-/Netz-/VM-/Hardwareprüfung: **NOT_RUN**.
- E201 DSO-/IoDrvDal-Identität: **HYPOTHESE** (ausdrücklich außerhalb Scope).
- Restunsicherheiten zu Laufzeitbedingungen und nicht untersuchten Callee-Wirkungen: **OFFEN**.
