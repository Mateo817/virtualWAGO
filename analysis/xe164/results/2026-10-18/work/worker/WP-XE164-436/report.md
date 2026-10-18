> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-436 — independent audit of the WP433 source join

**VERIFIZIERT (bounded source join):** I independently checked the pinned FW31 words and PT_LOAD mappings underlying WP433's selected `SCPU_boot_slave` call at ELF `0xa75c` and the local reader-result lane in the existing WP370 orchestrator. The direct BL at `0xa75c` targets `0x9a78`. The orchestrator evidence is noncontiguous: `[0x9a78,0x9e78)` and `[0x9f24,0xa470)`, 595 words / 2,380 bytes; the 172-byte interval between is not part of the body. This is a source-level join, not a closed execution trace.

At the boot callsite, `0xa748` sets current `r0=SP+0x20`; `0xa74c` loads `r1=[SP+0x14]`; `0xa754` forms current `r4=PC+8+literal[0xa8c8]=0x40028`; and `0xa758` stores numeric 1 to `[r4]`. The BL then enters `0x9a78`. The orchestrator prologue saves r4-r11/LR and d8-d9, allocates 0x15c bytes, and at `0x9aac` stores its incoming r0/r1 to its own SP+0x14/+0x18. At `0x9ae0` it BLs to the already-inventoried reader `0x97f0` with current arguments `(r0=0, r1=SP+0x38, r2=SP+0x3c)`. These are address/register equations only, not parameter or structure declarations.

The conditional path is precisely: if the reader call at `0x9ae0` returns normally with `r0=0xffffffff`, `CMN r0,#1` at `0x9ae4` sets Z and the `BEQ` at `0x9ae8` reaches `0xa208`. That local epilogue sets current r0 to zero, adds back 0x15c bytes, restores d8-d9, and loads r4-r11/PC from the stack at `0xa214`. On the caller side, `0xa764` computes `r0+1`; for helper return zero, NE is true, so `0xa76c/0xa770` conditionally write numeric 2 through current r4.

The final store is to the original numeric address `0x40028` only under explicit continuity premises: the nested call chain returns normally; the helper's stack pointer and saved frame remain valid and its saved r4 word is not changed; its epilogue consequently restores the caller's r4 value `0x40028`; and no intervening operation changes the word at `0x40028` if describing the transition specifically as `1 → 2`. The raw source proves the local save/restore instructions and conditional store, not that opaque calls preserve those conditions. Without these premises, the post-call store is only to the current, unproven r4-relative address, and even if the store occurs, its prior contents need not be 1.

WP370's file ledger and configured-byte summary are independently hash-checked and the candidate concatenation is rebuilt from the exact prefix, exact retained L3 bytes and XOR byte. This establishes static artifact identity for that candidate only. It does not establish which row is selected, that the join is runtime-reachable, or that bytes are transferred. The reader call at `0x9ae0` is an invocation point; the returned r0 is tested at `0x9ae4` (not at the call instruction itself).

| Claim | Status | Independent basis | Boundary |
|---|---|---|---|
| Caller arguments, G address, pre-call store, and BL target | VERIFIZIERT | Raw FW31 words, literal equation and ARM branch target | One source lane; no runtime reachability |
| Orchestrator entry saves incoming r0/r1 and calls reader with local addresses | VERIFIZIERT | Raw prologue/setup/call words and target calculation | Numeric positions; no API/ABI inference |
| Reader `0xffffffff` normal return reaches local helper return zero | VERIFIZIERT, conditional | CMN/BEQ and local epilogue words | Reader result and normal return are premises |
| Helper return zero reaches caller conditional store of 2 | VERIFIZIERT, conditional | Caller CMN/NE/store words | Current r4 may be called-address only under frame/preservation premises |
| Store changes `G` from 1 to 2 | HYPOTHESE, conditional on continuity | Caller pre-call store plus conditional post-call store | Requires saved r4 restored and no intervening G mutation |
| Runtime reader result, selected payload, transfer, reset, or semantic meaning of values | OFFEN / NOT_RUN | Not established by source join | No execution or device evidence |

No frozen upstream file was modified. The independent validator verifies source manifests, exact source words and file offsets, branch/literal equations, noncontiguous extent, frame-size arithmetic, artifact equality, and the conditional truth table. It is a read-only source/integrity validator, not a full CPU replay.
