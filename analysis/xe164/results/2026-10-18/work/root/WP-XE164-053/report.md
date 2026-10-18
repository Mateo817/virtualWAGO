> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-053 — E0340E direct-target return capability

## Ergebnis

VERIFIZIERT, begrenzte statische Synthese: Alle vier in E-XE164-063
beobachteten direkten Calls zielen auf drei bereits akzeptierte Decodes mit
mindestens einem statischen Return-Terminal:

- E03420→E033B8: lineares Ziel E033B8..E033EF, `RETS` E033EE
  (E-XE164-049).
- E03444/E03494→E03ABA: begrenzte CFG E03ABA..E03B4D, erreichbare `RETS`
  E03AE6 und E03B4C (E-XE164-061).
- E03520→E033F0: lineares Ziel E033F0..E0340D, `RETS` E0340C
  (E-XE164-049). Dieser direkte Call schließt die in E-XE164-049 noch offene
  statische Eintrittsverknüpfung für E033F0.

HYPOTHESE/OFFEN: Das Vorhandensein statischer Return-Terminals beweist weder,
dass ein konkreter Aufruf zurückkehrt, noch welche Register oder Speicherwerte
erhält, verändert oder als Argument/Rückgabe verwendet werden. Deshalb bleiben
die vier Fortsetzungskanten und die E03526-Erreichbarkeit bedingt.

## Methode und Grenzen

Root-SOL-Self-Review der akzeptierten, hashgebundenen Tabellen aus
WP-XE164-038, -050 und -052. Keine neue Disassembly und keine externe Quelle.
`validate.py` bindet Input- und Tabellenhashes, gleicht die vier Callpaare ab
und prüft die vier beobachteten Return-Terminaladressen. Der Befund qualifiziert
keine ABI-, SFR-, DPP-, Protokoll-, Runtime- oder Hardwaresemantik.

Tests: Die ersten beiden Validatorläufe waren FAIL wegen fehlerhafter lokaler
Textnormalisierung (`0xe...` zu `EE...`, danach fehlende führende Null bei
E03AE6/E03B4C); der Firmwarebefund war davon nicht betroffen. Nach Korrektur
muss der Validator PASS melden. Geräte-, Netzwerk-, VM-, Runtime- und
Hardwaretests: NOT_RUN und außerhalb des Scopes.
