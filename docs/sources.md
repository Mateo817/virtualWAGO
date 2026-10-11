# Öffentliche Quellen und Aussagegrenzen

Aus dem Quelleninventar der Forschungsfassung vom 11.10.2026 übernommen; keine neue Live-Verifikation im Dokumentationsbootstrap. Mutable Seiten vor weiterer Entwicklung erneut prüfen. Private Quellen S01–S10 bleiben im lokalen Paket. Ein Buildrezept belegt keine ausgeführte FW31-Aufrufkette; Handbuchrevision und konkrete Modulvariante gehören zu jeder Behauptung.

## WAGO-Stack

- **S11 SDK-Anker:** [FW30-V04.08.09](https://github.com/WAGO/pfc-firmware-sdk-G2/tree/FW30-V04.08.09), Commit `252209115885442bac7359a2ff1cfa4efb3a9c84`.
- **S12 Plattform:** [platformconfig](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/configs/wago-pfcXXX/platformconfig): ARM/ABI, Kernel, DTS, barebox/MLO, Toolchain.
- **S13 SDK und Rechte:** [README](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/README.md) und LICENSE derselben Revision. Keine pauschale Lizenz aller Firmwarebestandteile.
- **S14 Historie:** [Changelog](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/Changelog), unter anderem Änderungen der DAL-/Runtimeintegration. Historie nicht mit aktuellem Gerät gleichsetzen.
- **S15 Runtimekomponenten:** [wago-codesys3-002-wagocmp.in](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/rules/wago-codesys3-002-wagocmp.in).
- **S16 K-Bus-Bibliothek:** [wago-libs-pac-kbus.make](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/rules/wago-libs-pac-kbus.make), Paketpfade, interne Quellen, Binär-/Headerpakete, Installationsorte.
- **S17 Gerätepfade:** [link_devices](https://github.com/WAGO/pfc-firmware-sdk-G2/blob/252209115885442bac7359a2ff1cfa4efb3a9c84/ptxproj/projectroot/etc/init.d/link_devices).
- **S18 ADI-C-Beispiel:** [kbusdemo.c](https://github.com/WAGO/pfc-howtos/blob/master/HowTo_ADI-MyKBusApplikation/ptxproj/src_kbusdemo/kbusdemo.c), gelesener Git-Blob `c6af1246395d525d8340ce4616aa9e8c9c09d390`. Historisches Beispiel, keine FW31-Headerdefinition.
- **S19 Anleitung:** [ADI-MyKBus](https://github.com/WAGO/pfc-howtos/blob/master/HowTo_ADI-MyKBusApplikation/README.md).
- **S20 Gerätefunktionen:** [adi_functions.txt](https://github.com/WAGO/pfc-howtos/blob/master/HowTo_ADI-MyKBusApplikation/ptxproj/src_kbusdemo/adi_functions.txt), gelesener Blob `c9fc10d017f6d4f895a86c0341feb1ed3154edf7`.
- **S21 Beispiellizenz:** [License](https://github.com/WAGO/pfc-howtos/blob/master/HowTo_ADI-MyKBusApplikation/License). Lizenzumfang und abweichende Quellheader vor Wiederverwendung prüfen.
- **S22 Reale K-Bus-Anbindung aus Docker:** [pfc-modbus-server](https://github.com/WAGO/pfc-modbus-server/blob/master/README.md), kein Emulator.
- **S23 Firmwareverteilung:** [WAGO/pfc-firmware](https://github.com/WAGO/pfc-firmware). Exakte Pakete, Hashes und Rechte gesondert erfassen.

## Runtime und Emulator

- **S24:** [CODESYS Driver FB](https://forge.codesys.com/drv/io-drivers/doc/Driver%20FB/).
- **S25:** [CODESYS Virtual Control](https://store.codesys.com/en/codesys-virtual-control.html). Produktversion, Lizenz-/Instanzbedingungen frisch prüfen; keine ungeprüften Preisangaben übernehmen.
- **S26:** [QEMU ARM-Systememulation](https://www.qemu.org/docs/master/system/target-arm.html).
- **S27:** [QEMU virt](https://www.qemu.org/docs/master/system/arm/virt.html).
- **S28:** [QEMU Userspace](https://www.qemu.org/docs/master/user/main.html).
- **S29:** [TCG Instruction Counting](https://www.qemu.org/docs/master/devel/tcg-icount.html).

## Module und weitere Implementierungen

- **S30:** [750-466 Herstellerhandbuch auf Dokumentenspiegel](https://manualzz.com/doc/59452885/wago-4-20ma--single-ended-manual). Spiegel, kein Nachweis der aktuellen Revision.
- **S31:** [750-677 Herstellerhandbuch auf Dokumentenspiegel](https://www.manualslib.de/manual/909172/Wago-750-677.html). Originaldokument und Modulrevision nachbeschaffen.
- **S32:** [WAGO 750-1405](https://www.wago.com/gb/io-systems/16-channel-digital-input/p/750-1405).
- **S33:** [WAGO 750-1504](https://www.wago.com/global/i-o-systems/16-channel-digital-output/p/750-1504).
- **S34:** [WAGO 750-677](https://www.wago.com/de/io-systeme/4-pulsweitenausgaenge/p/750-677).
- **S35:** [CDP Studio Wago PFC I/O](https://cdpstudio.com/manual/cdp/wagopfcio/um-wagopfcioserver.html).
- **S36:** [Eclipse 4diac/FORTE Wago PFC200](https://eclipse.dev/4diac/doc/io_config/wago_pfc200.html).
- **S37:** [WAGO Community: I/O über MQTT](https://www.wago.community/t/how-to-control-io-directly-over-mqtt-pfc200-100/58), Communityhinweis, keine OEM-ABI-Garantie.

## Rechteprüfung

- **S38:** [Im Store verlinkte Engineering-EULA](https://store.codesys.com/media/n98_media_assets/files/000138/4/CODESYS_EULA_Engineering_en.pdf). Nicht automatisch die Lizenz der Runtime oder aller virtuellen Instanzen.
- **S39:** [UrhG §69e](https://www.gesetze-im-internet.de/urhg/__69e.html), Ausgangspunkt einer gesonderten Rechteprüfung, keine pauschale Rechtsfreigabe dieses Vorhabens.
