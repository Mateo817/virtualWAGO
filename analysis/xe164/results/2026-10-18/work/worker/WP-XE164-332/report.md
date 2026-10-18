> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-332 — independent audit of WP319's method-to-backend tails

## Result

**VERIFIZIERT**, conditional on WP319's two synthetic address/memory fixtures and the stipulated backend callback words: the seven selected libdal method bodies reach their encoded `BX r3` tail with source-derived register and frame state. The six cyclic getter candidates map to the six C-relative callback words listed in `matrix.tsv`; `+0x58` remains a distinct getter-object candidate with its own source body and a separately documented list-entry context. **HYPOTHESE** for any runtime publication or common record binding. **OFFEN** for constructor reachability, actual loader relocation winners, callback API contracts/behavior, and physical I/O. Test status: **PASS** for source pins, WP319's read-only replay validator and its 14-path/10-control trace regeneration; **NOT_RUN** for native execution, runtime, VM, device, network, or backend-body execution.

## Source and replay checks

The frozen WP319 manifest verified before and after its default validator. I independently ran that validator with bytecode writes disabled. It checked the exact 451-word source ledger against the pinned libdal and GLib ELF files, regenerated all 14 primary traces and memory-effect rows in memory, checked seven `libpackbus` dynamic-symbol values, and compared all ten source-stepped controls. It passed with 3,392 primary PC rows and 1,778 primary memory events. Before/after package-file inventories matched; WP319 was not modified and its artifact generator was not run.

The executed decoder path in WP319 is based on the bounded A32 model from WP314, which itself records WP303 source composition/decoder ancestry. This review treats that shared decoder lineage as disclosed evidence, not as an independent native execution. I separately checked its raw source-word binding, actual per-PC traces, critical branches, memory reads/writes, target values, and tail frame snapshots. There are seven selected libdal bodies (six cyclic + one separately qualified `+0x58` candidate), the three direct helpers, the exact lookup PLT, and the selected GLib lookup/hash/equality/arithmetic route. The 451-word ledger contains 233 libdal words and 218 GLib words. The trace paths stop on `BX r3`; the backend target body is never fetched.

For every primary trace, the terminal fetched word is `0xe12fff13`, the source `BX r3`. The decoded next object is `backend` at the stipulated pointer `BackendBias + dynsym st_value`; no `backend` object appears among fetched instructions. The trace shows SP and LR restored to each method entry value and r4-r11 restored to the actual entry-register snapshot for that selected source path. Tail r0-r3 remain in `tail-boundaries.tsv` and `matrix.tsv`; these values are instruction-state evidence, not ABI arguments. The full PC and memory-event count by fixture and position is recorded in `trace-audit.tsv`.

The three helper gates are executed from source: helper `0x2180` reads the stipulated global byte; `0x2194` runs the selected divisor-7 source path and reads `[T+0x170]`; `0x1ecc` performs the second exact table lookup. Under those fixture inputs their outputs make the method-local gates pass. Sized bodies retain current r5=`0x100`, r6=`0x40`, and r7=`0x35000000` at the source comparison; the source-derived unsigned gate accepts the selected fixture lengths and returns to the caller for short or wrapped cases. The null-callback controls reach local return before length-word reads. None of these steps assigns a public prototype or ABI.

## Callback-position and publication boundary

Raw libdal relocations at the getter cells are `R_ARM_RELATIVE`, with addends matching the exact candidate body addresses. The six cyclic local bodies read, respectively, `C+0x2c`, `C+0x20`, `C+0x30`, `C+0x24`, `C+0x18`, and `C+0x28`. Those numeric cells align with WP311's reviewed six-callback record positions and exact `libpackbus` symbol names. The separate `+0x58` getter body reads `C+0x3c`, with a separately pinned DiagGetDeviceState dynamic symbol. WP291's list-entry `+0x58` call context is kept distinct; it is not used to claim the same record, getter object, or allocation.

The seven exact backend dynsym values are pinned and rechecked against the local `libpackbus.so.1.0.1` dynamic-symbol table. WP319 stipulates each backend pointer as backend bias plus that symbol value and places it in the corresponding synthetic C cell. This proves the numeric source join used by the traces. It does not prove that runtime relocation or publication wrote those values, that C is the provider's current record, or that any callback behaves according to its symbol name.

## Controls and scope

All ten controls are source-stepped and checked in `control-audit.tsv`: null simple callback, helper byte zero, helper global-gate byte zero, short and equal sized lengths for both sized methods, null sized callbacks before length loads, and unsigned sum wrap. They establish only their recorded branch, source memory, and return/tail outcomes for those fixtures.

The six cyclic positions plus the separate `+0x58` candidate are source-position evidence under a conditional producer/consumer join. Constructor reachability, common allocation identity, actual `GLOB_DAT`/`R_ARM_RELATIVE` runtime resolution, backend effects, API semantics, ABI, and hardware behavior remain outside the evidence.
