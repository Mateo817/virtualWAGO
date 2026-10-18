> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-075 — FW31 WUP-Inventar

## Ergebnis

**Befundstatus: OFFEN.** Aus dem hashgebundenen WUP ist eine vollständige äußere ZIP-Inventur und die unveränderte Materialisierung des enthaltenen RAUC-Payloads gelungen. Dieser Payload ist ein SquashFS 4.0. Wegen fehlendem REA-Unblob-Provider und fehlendem lokalem SquashFS-Extraktor konnte dessen Inhalt nicht vollständig inventarisiert werden. Deshalb ist weder die Anwesenheit noch die Abwesenheit von `libIoDrvDal.so.1.0.2` oder `libIoDrvKbus.so.0.0.1` verifiziert; es wurden keine Bibliotheken extrahiert.

## Eingangsidentität

**Status: VERIFIZIERT.** Vor der Analyse wurde der Eingang erneut geprüft:

- Pfad: `PRIVATE_ANALYSIS_ROOT/sources/fw31-040901-31/PFC-G2-Linux_update_V040901_31_r9d0900aaed.wup`
- Größe: `101767197` Bytes
- SHA-256: `b6d3ec75d90e781154b57668561085223345779857944af904043a94bcc79f07`
- Ergebnis: PASS

REA `open_binary` klassifizierte diese Bytes als ZIP-Archiv mit genau diesem SHA-256.

## Beobachtete Containerkette und Inventar

**Status: VERIFIZIERT** für den vollständigen ZIP-Central-Directory-Inhalt und die extrahierten Bytes der beiden äußeren Einträge. REA-Inventory: `ev_54dab9ba5b499b5629420ed363ad032f154e2f753614c36198fd7529e4cc78fd`; Manifest-ID `agm_967885a82dfa30ac4ff2cbbd49ea60847e7f63100a8bbf0a6790a26c572f203b`; Graph-SHA-256 `8049ec861ef224d878eb87329a3038567a8a75758ef499df2bcf8a392bb2d753`.

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Die SHA-256-Werte der zwei materialisierten äußeren Einträge stimmen mit den von REA für die entsprechenden ZIP-Mitglieder gemeldeten Werten überein. `package-info.xml` bindet den Payload als RAUC-Datei an `PRIVATE_LOCAL_PATH` und nennt Revision `4.9.1`, Release-Index `31` sowie System `PFC-Linux`.

## Bibliothekssuche und Symlinks

**Status: OFFEN.** Eine wörtliche Byte-Suche nach `libIoDrvDal.so.1.0.2` und `libIoDrvKbus.so.0.0.1` in den vollständigen Bytes des WUP, in `package-info.xml` und in den vollständigen rohen SquashFS-Bytes ergab jeweils keinen Treffer. Das ist keine erschöpfende Suche im Dateisystem: SquashFS-Dateinamen und Dateiinhalte können komprimiert vorliegen. Die REA-ZIP-Inventur enthält genau zwei äußere reguläre Dateien und keine ZIP-Symlinks; zu inneren SquashFS-Pfaden, Symlinks oder Paketmetadaten liegen keine Beobachtungen vor.

Exakte Bibliothekspfade, Dateigrößen und Hashes sind daher **OFFEN**. Alternative Erklärung: Eine Bibliothek kann im komprimierten Dateisystem enthalten sein, aber im rohen SquashFS keine Klartextnamensfolge bilden; möglich sind außerdem andere Namen oder Versionen. Der Dateiname eines möglichen Treffers wäre allein kein Funktionsvertrag.

## REA-Evidence und Toolstatus

- `ev_6b2664617efe1c5a60d76c27d7a1014ddc49afa5c0808e0677b4e442e4734ce4` — `inspect_artifact`, kompletter äußerer ZIP-Graph.
- `ev_54dab9ba5b499b5629420ed363ad032f154e2f753614c36198fd7529e4cc78fd` — zugehöriges `inventory_artifact`-Evidence.
- `rea-evidence-bundle.json` — kanonischer REA-Bundle, 2 Records; SHA-256 steht in `manifest.tsv`.
- `inspect_firmware_regions`: **BLOCKED**; REA meldete fehlendes absolutes `REA_BINWALK_COMMAND`.
- `extract_firmware` auf dem WUP: **BLOCKED**; REA meldete fehlendes absolutes `REA_UNBLOB_COMMAND`.
- `inspect_artifact` dokumentiert ZIP-Coverage über Central-Directory-Einträge; nicht erfasste ZIP-Nicht-Eintragsbytes bleiben außerhalb dieses Inventars.

REA-Version: `rea 6.5.0`. REA-Artifact-Graph-Provider: `1`. Lokale formatbezogene Prüfung: Python `3.13.5`, Standardbibliothek `zipfile`, zlib `1.3.1`; `file` `5.46`; GNU tar `1.35`. `unsquashfs`, `squashfuse`, `sasquatch`, `mksquashfs`, `bsdtar` und Python-Module `unsquashfs`, `squashfs`, `libarchive`, `py7zr` waren nicht verfügbar. Es wurde nichts installiert oder heruntergeladen.

Verwendete Kommandos / Operationen:

1. `stat -c '%n %s bytes' <WUP>` und `sha256sum <WUP>` — Eingangshash und Größe.
2. REA `inspect_firmware_regions(path=<WUP>)` — BLOCKED wie oben.
3. REA `open_binary(path=<WUP>)`, danach `inspect_artifact(detail="complete")` — ZIP-Graph.
4. `python3 -c '... zipfile.ZipFile(...); ... infolist() ...'` — nur die zwei ZIP-Einträge mit Größe, komprimierter Größe, CRC und Flags ausgegeben.
5. `python3 -c '... zipfile.ZipFile(...); ... read(...) ... write_bytes(...)'` — genau `package-info.xml` und den `.raucb`-Eintrag nach diesem Paketpfad materialisiert.
6. `file <extrahierter .raucb>` und `od -An -tx1 -N64 <extrahierter .raucb>` — Formatbestimmung anhand Magic / Header.
7. `sha256sum <package-info.xml> <.raucb>` — Materialisierung gegen REA-Eintragshashes geprüft.
8. REA `extract_firmware(path=<WUP>, output_directory=<Paketpfad>/firmware-extract)` — BLOCKED wie oben; kein Ausgabeordner wurde durch REA erzeugt.
9. `python3 -c '... Path.read_bytes().find(...) ...'` — die beiden exakten Namen in WUP, XML und rohem `.raucb` gesucht; je Datei kein direkter Treffer.
10. REA `export_evidence_bundle(path=<Paketpfad>/rea-evidence-bundle.json)` — 2 Records, 13243 Bytes.

## Reproduzierbare Validierung

Arbeitsverzeichnis: `PRIVATE_ANALYSIS_ROOT/work/worker/WP-XE164-075`.

Die folgenden Befehle prüfen Paketdateien, Größen und Hashes anhand `manifest.tsv` (Manifestdatei selbst ist aus der eigenen Hashliste ausgeschlossen):

[Code-/Listingblock bleibt im privaten Nachweispaket.]

Der Eingangshash ist unabhängig davon mit dem oben festgehaltenen Originalpfad zu prüfen. Eine zukünftige erschöpfende Negativfeststellung erfordert einen formatgerechten SquashFS-Inhaltsextraktor und anschließend vollständige Pfad-/Symlinkinventur plus Suche nach beiden exakten Namen.
