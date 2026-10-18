> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-134 — generischer ComponentEntry und Zielkörper `0x0030066C`

## Ergebnis

**VERIFIZIERT:** Im exakten `codesys3`-ELF setzt der Helper die lokale Objektadresse auf `fp-0x5C`. Bei `0x2FC5A4..0x2FC5AC` wird `0x0030066C` gebildet und bei `[fp-0x34]` gespeichert. Da `(fp-0x5C)+0x28 = fp-0x34`, wird das generische `ComponentEntry`-Objekt an `+0x28` mit `0x0030066C` initialisiert.

**HYPOTHESE (nur konditional an IoDrvDal gebunden):** WP-XE164-132 beobachtet am dortigen indirekten Aufruf `r0=r1=0x10062001` und `r3=&0x26090`; der Zielwert `r2` stammt aus `[input+0x28]`. Falls dieser Laufzeitwert tatsächlich auf den Helper-Eintrag `0x0030066C` zeigt, nimmt der Zielkörper beim Eintritt die ersten beiden Werte als `r0` und `r1` entgegen. Die konkrete Bindung des generischen Loaders an IoDrvDal ist hier nicht belegt.

**VERIFIZIERT:** Der Zielkörper führt eine begrenzte Listensuche durch: Er vergleicht `r1` mit dem Wort bei `+0x14` jedes Listeneintrags. Bei Treffer speichert er `r0` bei `+0x18`, ruft `CMGetComponent(r0)` auf, speichert den Rückgabewert bei `+0x10`, erhöht den globalen Zähler bei `0x005FC5C8` und gibt `entry+0x10` zurück. Ohne Treffer versucht er einen Speicherpoolblock zu beziehen; bei erfolgreicher Zuteilung speichert er `r1` und `r0` in den neuen Block, ruft `CMGetComponent(r0)` auf, erhöht den Zähler, hängt den Block an die Used-Liste und gibt ihn zurück. Die erkennbaren Fehlerpfade liefern `-1`.

Für die WP132-Registerwerte heißt das konditional: `0x10062001` wird als beide Eingabewerte verwendet, gegen Listeneinträge verglichen und als Argument an `CMGetComponent` weitergereicht. `r3=&0x26090` wird im Körper nicht als Eingabewert verwendet; `r3` wird überschrieben. Das belegt keine Abwesenheit anderer globaler oder indirekter Aliase. Die direkten Aufrufziele und ihre Namen sind Beobachtungen, kein vollständiger API-Vertrag.

## Identität und Eingaben

| Artefakt | Größe | SHA-256 | Verwendung |
|---|---:|---|---|
| `codesys3` unter WP-XE164-112 | 5.181.396 Byte | `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` | exaktes ARM-ELF, statische Analyse |
| WP-XE164-125 `function-disassembly.txt` | 3.392 Byte | `de11be1f744ffd81096202a80d8ec0c971049c9cfcd2357c8b47756b738f7621` | vorhandener Disassembly-/Adressraumkontext |
| WP-XE164-132 `report.md` | 9.578 Byte | `8050043d8dd16e7712fb41eda0e78a32440345e86446cc8e06d9fb84959537ae` | begrenzte IoDrvDal-Aufrufwerte und deren Herleitung |
| WP-XE164-132 `rea-bundle.json` | 667.498 Byte | `2b82ea5fc23d4d7839aaa79a61243f7d14649337552bcb790274ed2b81cf6434` | vorhandene REA-Evidence zur konditionalen Callsite-Zuordnung |

Die Eingabe-Hashes und Größen wurden vor der Analyse lokal bestätigt. REA öffnete `codesys3` mit SHA-256 `b56c…1ab5` als ELF/ARM. Provider: Ghidra 12.1.4; Profil-Digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`. Adressen in diesem Bericht sind Ghidra-Default-Space/ELF-Link-VA, nicht Dateioffsets. In diesem ELF stimmen sie numerisch überein: `0x30066C` ist ELF-Link-VA `0x30066C` und Datei-Offset `0x2F066C` (PT_LOAD-Abbildung mit VAddr `0x10000`, Offset `0`). Die numerischen Stellen werden deshalb explizit als Ghidra-Adressen geführt.

## Initializer

Die genaue Instruktionsfolge im Helper `FUN_002FC530`, dessen vollständiger REA-Body `0x2FC530..0x2FC707` ist:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Berechnung: `0x30 << 16 | 0x066C = 0x0030066C`; `fp-0x5C + 0x28 = fp-0x34`. Der Initializer schreibt somit die Adresse in das generische Feld bei `+0x28`. Das belegt den Wert in diesem Helper, aber allein noch nicht dessen tatsächliche Verwendung für IoDrvDal.

## Zielkörper und vollständige Instruktionen

REA/Ghidra meldet `FUN_0030066c` als nicht externen, nicht-thunk Funktionskörper mit vollständiger, zusammenhängender Range `0x30066C..0x3007BF` (340 Byte, inklusive Endadresse). Die nachstehende vollständige adressierte Instruktionsliste stammt aus dem zugehörigen REA-Dossier und deckt alle 85 Instruktionen dieses Ranges ab:

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Direkte aufrufziele laut REA/Ghidra: `0x0017F2D0 MemPoolGetBlock`, `0x00180608 MemPoolExtendDynamic`, `0x002FC820 CMGetComponent`, `0x0017FDEC MemPoolAppendUsedBlock`. Es werden hier keine Callee-Bodies behauptet. Die Konstante bei `0x300704/0x300708` wird als Argument an `MemPoolExtendDynamic` übergeben; ihre Bedeutung wird nicht über ihren Wert hinaus qualifiziert.

## Begrenzter Daten- und Kontrollfluss

- Einstieg: `r7 <- r0`, `r5 <- r1`; die gezeigte Funktion liest `r3` nicht als eingehenden Wert. `r3` wird später als temporäres Rechenregister genutzt. Für WP132 ist sein eingehender Wert `&0x26090`; der Körper zeigt keine direkte Dereferenzierung dieses Wertes.
- `r12` wird aus `[0x005108C8]` geladen; aus `[r12+0x1C]` stammt der Listenanfang. Die Kette wird über `[node]` weiterverfolgt. Für jeden Node wird `[node+0x14]` mit gesichertem `r1` verglichen.
- Trefferpfad (`0x3006B8 -> 0x300774`): `[node+0x18] <- r0`; `CMGetComponent(r0)`; Rückgabewert nach `[node+0x10]`; globaler Zähler `[0x005FC5C8]` wird erhöht; Rückgabe `node+0x10`.
- Kein Treffer: `MemPoolGetBlock([0x005108C8], &local_flag)` mit initialer Flag `1`; bei fehlendem Block oder Flag ungleich null folgt `MemPoolExtendDynamic([0x005108C8], 0x003A41F4, 10)` und ein erneuter `MemPoolGetBlock`. Ein fehlgeschlagener Extend, fehlender Block oder nicht-null Flag endet mit Rückgabe `-1`.
- Erfolgreicher Neuanlagepfad: speichert `r1` und `r0` in die zwei Wörter ab Blockbasis `+4` bzw. `+8`; `CMGetComponent(r0)` liefert das Wort an Blockbasis `+0`; erhöht `[0x005FC5C8]`, ruft `MemPoolAppendUsedBlock(block)` auf und gibt die Blockbasis zurück.

Mit den sichtbaren WP132-Werten sind `r0` und `r1` jeweils `0x10062001`. Damit ist der Listenvergleich konditional `node[+0x14] == 0x10062001`; der erste Wert `0x10062001` wird außerdem gespeichert und an `CMGetComponent` übergeben. Diese Aussage folgt statisch aus dem Dossier und beweist weder, was `CMGetComponent` intern tut, noch dass es sich bei den Werten tatsächlich um valide Pointer oder Identitäten handelt.

Direkte sichtbare Speichereffekte umfassen Reads aus der global referenzierten Pool-/Listenstruktur, Reads aus Listeneinträgen, bedingte Writes in Listeneinträge oder frisch gelieferte Poolblöcke sowie ein Inkrement an `0x005FC5C8`. Die Callziele können weitere Speicherwirkungen haben; die Funktionsanalyse verfolgt diese Call-Seiteneffekte nicht. Daraus folgt keine vollständige Aliasfreiheit oder globale Seiteneffektfreiheit. `r3` als eingehender Wert wird nicht bewahrt, aber unbekannte Callee- und globale Wege bleiben offen.

## REA Evidence, Alternativen und Restunsicherheit

REA-first: exaktes Binary geöffnet; Ghidra 12.1.4 auf ARM. Primäre Evidence:

- `ev_e54608bf45e5c33b3477ab49e771faf9f03e111e161cb3a9ed88a4dcd217a85b` — Dossier von `FUN_002FC530`; Assembly enthält die Initialisierungsfolge bei `0x2FC5A4..0x2FC5AC` und den lokalen Basiszeiger bei `0x2FC55C`.
- `ev_23ae2d91451f4c29cebc858c07226ad6de18b7ec8f2f3fb54e6053a56d6af12d` — vollständiges Dossier für `FUN_0030066c`, inklusive Ghidra-Funktionsrange, Assembly, Referenzen und begrenztem High-P-code-Datenfluss (`truncated=false`).
- `ev_646af8997a8f504d93e14747e2367c5e01340510c1629b534503f917baf9699a` — gepagte vollständige Instruktionsliste zum Zielkörper, 85/85.
- `ev_138fa44c99b1c139499d57da0af4bebb21738f4ded16f4e9441aaabf561d9f1c` — aufgelöste direkte Zielnamen/-adressen.
- `ev_a7fc2951f8462d378b6c0d56b3df3f927c539e5152e107d33becfd2c0230c958` — direkte outgoing references des Zielkörpers, einschließlich globaler Datenrefs.
- `ev_91a8ca228e0276c4f3856bffbb59930c8357848ae25ecc24efa02c1576bba841`, `ev_2d4c77bd0a50c8541a1529b39279a8c09698ca9daf11915d3ca1a6c4df0b3844`, `ev_a62a05af72385cb273a1787eaeabe8151d69d7948b2f90c1e6546633f11f460c` — direkte Effects, erkannte Eingangsparameter und Parameterverwendungen.
- WP132 IoDrvDal-Callsite-Evidence ist im übergebenen Report/Bündel dokumentiert; seine Übertragung auf `0x0030066C` bleibt **HYPOTHESE**.

Die beigefügte `rea-bundle.json` ist der exportierte komplette lokale REA-Sessionstand für dieses Paket (17 Evidence Records, 0 Unknowns). Ghidra-Pseudocode und High P-code sind Analyseprodukte, keine Originalquelle und keine Laufzeitbeobachtung. Alternativ könnte eine nicht erfasste Aufrufkonvention oder ein Callee über verborgene Zustände weiter auf Speicher zugreifen; der sichtbare Körper allein schließt das nicht aus. Es erfolgte kein REA-Timeout, daher war kein Disassembler-Fallback nötig.

| Prüfung | Status |
|---|---|
| Eingabeidentität, Größen und Hashes | PASS |
| Initializer-Feldwert und Offsetrechnung | PASS |
| Vollständiger Zielkörper `0x30066C..0x3007BF` | PASS |
| Direkte Calls und sichtbare Daten-/Kontrollflüsse | PASS |
| IoDrvDal-Bindung an den generischen Helper | OFFEN |
| Verborgene/globale Aliaswege und Callee-Seiteneffekte | OFFEN |
| Eigenständige Tests / Targetausführung | NOT_RUN |
| Runtime, VM, Netzwerk, Geräte und Hardware | NOT_RUN |
| Unabhängiger Review | NOT_RUN |
| Self-Review | PASS |

Die Symbolbezeichnung `FUN_0030066c` und die Adresse `0x0030066C` sind Identifizierungsmerkmale aus dieser Binary-Analyse, kein vollständiger API- oder ABI-Vertrag.
