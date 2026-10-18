> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-348 — two backend initialization source boundaries

Root **Self-Review**. **VERIFIZIERT** for50rawREA/sourcewords (two3-wordPLTs/two22-wordbodies), four literalpool words, exact static relocations and local store relationships. Runtimebinding/instanceidentity/API/ABI/opaqueeffects **OFFEN**. **PASS** checks; native/VM/device/network **NOT_RUN**.

Pinned source is Root310's FW31 libpackbus.so.1.0.1 SHA3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. WP342 identified open's exact encoded calls10b40→8220 and10ba4→7d7c. Both are PLTs. StaticJUMP_SLOT cells334b8/3332c refer to defined dynamic symbols lpkb_CreateWatchdog at14c68 andvGetVPI_Values at14a50 respectively. Runtimepreemption/GOTcontents are not established.

CreateWatchdog has22words/88B[14c68,14cc0), with two separate poolwords14cc0/14cc4. It savesentryr0 into r4, calls calloc-namedPLT withr0=1,r1=0x2c, then stores currentr0 through currentr4. A nonzero currentr0 returns source0; zero reaches opaque error/logging calls then sourceffffffff. Treating currentr4 as the original destination requires explicitcall/framepreservation premises. Neither allocation nor zero-filled bytes follow merely from the symbol name.

vGetVPI_Values has22words/88B[14a50,14aa8), two separatepoolwords14aa8/14aac. PC-relative equations yield data base ELF47bac and callbacksourceaddress14774. It savesentryr0 into r4, calls pthread_once-namedPLT withr0=base+30,r1=callbackaddress, calls acquire-lock-namedPLT withr0=base, then loads six words from currentr5+18..2c and stores them at currentr4+0..14. It restores its own saved registers and tails to pthread_mutex_unlock-namedPLT withr0=currentr5. Global/base/destination/register/frame validity after opaque calls is an explicitcondition, not an ABI guarantee. The callback is a numeric argument; once/lock/init semantics are not inferred.

Under342's separate explicit open-call premises, passing S+dc to the first helper makes its source store target S+dc. Passing S+a4 to the second yields destinations S+a4,a8,ac,b0,b4,b8 from the six words above. This supplies the source relation missing from open's local direct-store inventory. The values' origins and actual backend instance identity remain open.

Ghidra reports no procedure at callbackaddress24774 in analysis coordinates. The metadata error is retained, and callbackbody extent/effects are not invented. No body expansion or callback execution is part of this package.
