> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-078 — FW31 IoDrvKbus lifecycle reachability

## Scope and evidence identity

**VERIFIZIERT:** The input is the supplied `libIoDrvKbus.so.0.0.1`, 38,584 bytes, SHA-256 `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`. The recorded preflight and REA `open_binary` agree. ELF32 ARM hard-float is from the task's input description; REA independently identifies an ARM ELF. The Ghidra image base is `0x10000`, so for `.text` `ELF VA = file offset`, and `Ghidra address = ELF VA + 0x10000`. Example: Init is Ghidra `0x147fc`, ELF VA/file offset `0x47fc`.

Static analysis used REA with Ghidra 12.1.4. Analysis profile digest: `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`; REA composed workflow profile digest observed in overview: `ea780488a923abf4b1f7cfdef0655bfb803975af068010f080c0e9c9dc8917c6`, workflow revision 3. Tool-derived pseudocode is not source or execution evidence.

## Finding

**VERIFIZIERT:** `IoDrvKbus_Init` has one null-argument path returning `2`. With a non-null interface pointer, it writes code addresses into fields at offsets `+0x2c`, `+0x34..+0x54`, and `+0x624..+0x63b`, then obtains a resolver function pointer from the nested pointer at `arg+0x620` (nested offset `+0x34`). It uses that resolver to populate imported function-pointer cells. This is evidence of callback-valued field assignments and symbol-resolution attempts; absent the interface contract, field roles and whether the consumer later invokes each target are **OFFEN**. No runtime callback order is established.

The ordered nonzero-checked resolution chain in Init is: `CMUtlSafeStrCpy`; `IecTaskGetCurrent`; `IecTaskRegisterSlotCallbacks`; `IecTaskRegisterSlotCallback`; `EventPost`; `EventRegisteredCallbacks`; `EventUnregisterCallbackFunction`; `EventRegisterCallbackFunction`; `EventUnregisterCallback`; `EventRegisterCallback`; `EventClose`; `EventOpen`; `EventDelete`; `EventCreate`; `IoMgrCopyInputBE`; `IoMgrCopyOutputBE`; `IoMgrCopyInputLE`; `IoMgrCopyOutputLE`; `IoMgrStartBusCycle`; `IoMgrConfigResetDiagnosis`; `IoMgrConfigSetDiagnosis`; `IoMgrConfigGetParameterValuePointer`; `IoMgrConfigGetParameterValueDword`; `IoMgrConfigGetParameterValueWord`; `IoMgrConfigGetParameterValueByte`; `IoMgrConfigGetNextChild`; `IoMgrConfigGetFirstChild`; `IoMgrConfigGetNextConnector`; `IoMgrConfigGetFirstConnector`; `IoMgrConfigGetParameter`; `CMRegisterInstance`; `SupervisorOperationGetEntry`; `SupervisorOperationGetNext`; `SupervisorOperationGetFirst`; `SupervisorOperationGetState2`; `SettgGetIntValue`; `SettgSetIntValue`; `SettgGetStringValue`; `SettgSetStringValue`; `SysSemLeave`; `SysSemEnter`; `SysSemDelete`; `SysSemCreate`; `SysTimeGetUs`; `SysTaskWaitInterval`; `SysTaskWaitSleep`; `SysTaskExit`; `SysTaskEnd`; `SysTaskLeave`; `SysTaskEnter`; `SysTaskResume`; `SysTaskCreate`; `SysMemFreeArea`; `SysMemAllocArea`; `SysMemFreeData`; `SysMemAllocData`; `SysGetTypeSize`; `TscExtTaskUnregisterExternalEvent`; `TscExtTaskRegisterExternalEvent`; finally `TscExtTaskPostExternalEvent`.

**VERIFIZIERT:** The `arg+0x2c` field is assigned `idk_GetModuleDiagnosis` (Ghidra `0x16050`, ELF VA/file offset `0x6050`). It checks the first two inputs and returns `2` on null. Its DAL dispatch call at `0x16094` is through `*(ctx+0x61c)+0x58`; the return is tested at `0x160a0`, then an output word at `0x160a8/0x160ac`. Only status zero plus output value `1` reaches `IoMgrConfigResetDiagnosis(arg2,0x100)` at `0x160c4`, clears a local-bus diagnostic flag, and returns zero. Other dispatch results select `IoMgrConfigSetDiagnosis(arg2,0x100)` at `0x160f4`, set that flag, and also return zero. Thus the DAL status controls a diagnostic branch but is not returned to the caller. This describes observed routing only; neither dispatch slot is assigned an undocumented ABI here.

The first two resolver calls, `LogAdd` and `CMUtlMemCpy`, have their return values ignored in the decompilation. The following resolution calls test for zero and short-circuit to the common return block on the first nonzero result. If the chain reaches the last call, its result is returned. Thus the observed branch predicate is numerical zero/nonzero; the meaning of each nonzero value is not defined here. These names are lookup strings passed to the observed resolver, not complete function contracts.

**VERIFIZIERT:** The callback-valued field at `arg+0x624` is assigned `FUN_00013f98` (Ghidra `0x13f98`, ELF VA/file offset `0x3f98`). That routine's observed phase dispatch has `param_1==4` and `param_1==12` branches; other values return zero. This identifies two numeric phase cases only, not their external lifecycle semantics.

- For phase `4`, it registers five named external events (`LocalBusCycleEvent`, `LocalBusEvent_1` through `_4`) using the resolved `TscExtTaskRegisterExternalEvent` pointer and stores each returned event handle. It retains the first nonzero status encountered, but continues through subsequent operations: start of `rIdk_KbusCtrlCyclicThread`, four `FUN_0001332c` calls with constants `0x10001`, `0x10003`, `0x1000f`, `0x10017`; module-count setting reads/parsing and range handling; `idk_InitModuleScan`; `idk_InitCalculateSlotNumber`; and semaphore setup. Invalid/missing `MARKING`/`MAXTERM` conditions are logged and represented by numeric `0x28` or `0x1a`; the routine still reaches module-scan and slot-number initialization. The first-error accumulator is returned, with a final semaphore output status adopted only if no earlier error was retained.
- For phase `12`, the stop call is at Ghidra `0x144c0` and its result is saved at `0x144cc`. The event-state null guard at `0x144d4/0x144d8` branches to the common epilogue at `0x13fc8`, which reloads and returns that saved thread-stop result. With event state present, it unregisters five stored events, then proceeds through semaphore deletion, `idk_ExitModuleScan`, `idk_ExitCalculateSlotNumber`, and four `FUN_000132a8` calls with the same constants. Each later nonzero result is retained only if no earlier nonzero status has already been saved, so the earliest nonzero result across the stop and teardown calls is returned. It frees and clears the event-state pointer before returning. The semaphore branch has unusual status checks and should not be assigned stronger semantics than the pseudocode shows. This correction is supported by the existing function assembly Evidence `ev_8778676aaae209ebfc6f734b1a2d99d05d091204e6145130d3168ba486323960`.

**VERIFIZIERT:** The callback target at Ghidra `0x12650` (ELF VA/file offset `0x2650`, `FUN_00012650`) performs argument/context guards, then invokes a function pointer at `*(ctx+0x61c)+0x70` with the lookup string `libpackbus_get_terminal_info_32`. It proceeds to `idk_IoDrvScanModules` only if that call returns zero and an output word equals `2`; otherwise it returns `1`. Guard failure returns `2`. This is the only statically characterized, in-scope callback in this pass with a direct DAL-style terminal-info call. The lookup string and dispatch slot do not establish a complete ABI or contract.

The scan-callback edges are anchored by assembly: Init writes the slot at `0x148a8`; the indirect DAL-style call is at `0x126b8`, status test/branch at `0x126bc/0x126c0`, output-word test/branch at `0x126c8/0x126cc`, and the conditional `idk_IoDrvScanModules` call at `0x126e4` (Ghidra addresses).

The field `arg+0x62c` includes `FUN_000124e4` at Ghidra `0x124e4` (ELF VA/file offset `0x24e4`). It validates arguments and a type marker, calls `FUN_00011fdc(0x916)`, then conditionally calls `idk_CalculateSlotNumber` and `FUN_00012074(0x94c)`. It propagates the first nonzero status in that path; other observed numeric returns include `2`, `3`, `0x20`, and `0x28`. The field `arg+0x634` includes `FUN_00012120` at Ghidra `0x12120` (ELF VA/file offset `0x2120`). It has input and configuration guards, calls `FUN_00011fdc(0xaca)` and `FUN_00012074(0xb64)`, and on one branch uses resolved `SysGetTypeSize`; the terminal helper status is returned when prior validation succeeds. The callback's specific interface roles are **OFFEN**.

Other callback-valued writes whose executable target identity/body was not established in the REA function graph are preserved as raw addresses in `function-map.tsv`. A focused ARM objdump fallback confirmed instruction bytes at several such addresses after Ghidra returned no containing function for `0x133b0`; this is not enough to infer callback role or whole-function behavior. Notably the table writes do not prove every target is actually invoked by the consumer.

## Lifecycle ordering and limits

The defensible graph is: `IoDrvKbus_Init` writes callback-valued fields and resolves imports; the host-side invocation ordering is unknown; if the `0x13f98` callback is invoked with numeric `4` or `12`, the sequences above are reachable. The `0x12650` scan-like callback independently has the terminal-info → conditional `idk_IoDrvScanModules` sequence. `FUN_000124e4` and `FUN_00012120` are further statically referenced callback candidates. This is not a complete lifecycle ordering because no external caller/invocation edge for those interface fields is proved, some callback targets have no REA procedure body, and indirect calls may be unresolved.

**Alternativerklärung:** the host may populate/use these fields according to a lifecycle contract that assigns different names or order than their offsets suggest; numeric phase values may be interpreted elsewhere. The table-shaped writes alone do not prove registration in a particular host API.

**Restunsicherheit:** REA reports that Init has 62 calls/references without resolved destinations. The interface's field layout and callback names, indirect dispatch targets, the invocation order imposed by the host, and runtime status meanings remain open. The fallback disassembly was deliberately bounded to the unresolved entries; it does not close these gaps.

## Methods and canonical evidence

REA was used first: `open_binary`, `binary_overview`, `analyze_function`, `get_call_graph`, focused pseudocode and assembly, and `resolve_containing_procedure`. A scoped `arm-linux-gnueabihf-objdump` fallback was run only after the callback target at `0x133b0` resolved to no Ghidra procedure. It inspected `.text` near ELF VA/file offsets `0x210c`, `0x2614`, `0x2eb8`, `0x33b0`, and `0x36c0`. No device, network, VM, runtime, or hardware action occurred.

The complete retained REA bundle is `evidence-bundle.json` in this work-package directory (17 in-scope records, 2,190,796 bytes at export; zero unknown records). Principal Evidence IDs:

- Input/overview: `ev_d74d65af1ef2dd9abc6c9234afdecf81a783faea7c3f7f0b95a04c3ca662b2a5`
- Init function dossier: `ev_5959ab945c4e15c6d011169876dbb4659cf754c2dfee61e41b49f02876e430ce`
- Init forward call graph (partial due unresolved indirect calls): `ev_8134f7234ec33aa9ac9637dfbef1e64c258943aef345e7240234d0b4c493612a`
- Init pseudocode: `ev_6e0a9bd90e8763865f0c8924ae68ef34df7e6a7fbb810ee2b0810ad237d01d6c`
- Init assembly: `ev_47c967acc90ecb7ca7d85c6b1478946d11e8898f4105f19a3004b7301c44518c`
- `FUN_00012650` pseudocode: `ev_0494505a50857ad1e5bffc59cabe6ad1125ea8eccefc023722b886db9e658460`
- `FUN_00013f98` pseudocode: `ev_b386a44d6aa0b19a67a6aee6732aeaff546ff1e53c44b0a1522161e9302413dc`
- `FUN_000124e4` pseudocode: `ev_4c40527b89d855db2c995c005fca4d73cb0c41e5b70a16ce2d0bb00b579af641`
- `FUN_00012120` pseudocode: `ev_73026634e6ff7af708581a7d083ab3a4b9f9eab2fa8a4fd4f576baf10cdaa57a`
- Missing procedure at candidate `0x133b0`: `ev_2702ba52fd4ac6c7e763e0d38bbfe9c64171367d4a67c3708ff9733d2530530c`
- `idk_GetModuleDiagnosis` address: `ev_38d56b0081ec2d641ad9b5350bf5d5d1a4c47daccbb35f6f28416443f5282d9e`
- `idk_GetModuleDiagnosis` pseudocode: `ev_90037ba06064447a19f0dd7c62dfc76980420387c0ea7e65571241379cea6078`
- `idk_GetModuleDiagnosis` assembly: `ev_821f5c1800ea8085326a854d9fe0ceabec953d1f69c6189e9c443795da1ea968`

Additional focused records include FUN_00012650 assembly ev_19e410eb1552035605d8e6615fcc16f90c47e4ba2877d2a991e8cabe288a710a, FUN_00013f98 assembly ev_8778676aaae209ebfc6f734b1a2d99d05d091204e6145130d3168ba486323960, FUN_000124e4 assembly ev_5aa15942dfec017c972462283a6abad28218b154cb9479bcb9f064ee6de386dc, and FUN_00012120 assembly ev_2acd61b78f70c1b4a5babae154c5c175dd4bc6d84d1cce75f208c14675cfdddf. The complete serialized canonical records are in the evidence bundle; do not treat filtered or provider-generated pseudocode as source.

## Test status

`PASS` — supplied artifact SHA-256 and size matched before analysis and REA open. `NOT_RUN` — runtime/host lifecycle behavior; outside this static offline scope.
