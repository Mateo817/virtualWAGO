# Protocol notes

## Staged loader

- VERIFIZIERT: L1 contains an exact `0x10a`-byte copy span and a transfer to
  `E0:0020`.
- VERIFIZIERT: L2 contains receive/write/checksum-like code and a transfer to
  `E0:0200`.
- HYPOTHESE: these instructions load L2 and then L3 at the addresses used by
  the derived composite.
- VERIFIZIERT (ARM FW30 static configuration): `SCPU_boot_slave` reaches a
  table-driven file reader/orchestrator. The parsed static rows configure L1
  raw stages, L2 raw-plus-Ack stages, and L3 four-byte byte-swapped length,
  raw, one-byte XOR and Ack stages. Prefix (`+20`), Ack (`+21`) and XOR (`+32`)
  are separate byte flags; transfer selector `+12` is zero in every parsed
  static row. E-XE164-014 records exact scope and Evidence IDs.
- VERIFIZIERT (negative, bounded): the separate `type == 1` SPI branch exists,
  but none of the parsed static rows selects it. This does not exclude runtime
  mutation or other callers/configuration.
- HYPOTHESE: the ARM stages and exact Composite `0200..03FF` ↔ L3 source
  `0000..01FF` equality are parts of one loader/payload chain (E-XE164-015).
- VERIFIZIERT (matching static contract): ARM L3 rows 7/8/9 configure a
  four-byte byte-swapped length with four-byte echo expectation, raw data, then
  a one-byte XOR with expected reply `0x81`. The bounded C166 L2 path reads and
  echoes four bytes, receives the nonzero second-word count into `E0:0200`
  while XOR-accumulating, compares the following byte, sends `0x81` and jumps
  to `E0:0200` on equality, or sends `0x7e` and restarts the header receive on
  mismatch (E-XE164-018).
- OFFEN: actual step reachability, successful serial transfer, physical/runtime
  placement, post-jump execution, meaning of the C166 nonzero-first-word path,
  alternate ARM rows, baud/SFR identity and persistence/flash behavior. The
  earlier preliminary claim that the ARM table configured no L2/L3 payload
  stage is discarded.

## K-Bus behavior

OFFEN. No end-to-end K-Bus transaction, register map or module protocol has yet
been reconstructed from L3. Do not infer UART, FPGA or MCU boundaries from the
loader alone.

## Startup initialization mechanics

- VERIFIZIERT: the bounded startup reader has explicit static mechanics for
  tags 1, 5, 6 and 7, including fixed record strides and byte copy/zero loops.
- VERIFIZIERT: the observed primary byte stream has one tag-1 record and then
  word 0; the default path selects the secondary reader. The secondary byte
  stream has twelve tag-5 records and then word 0, whose unmatched path reaches
  the numeric call anchor `E00F18` and an idle loop.
- HYPOTHESE: DPP/composite mapping binds the logical pointers to the retained
  bytes at assumed analysis addresses `E033A8` and `E00B84`.
- OFFEN: runtime reachability/result, the reason for the terminal unmatched
  word, target-memory meaning, and any K-Bus relevance.
- VERIFIZIERT (bounded static structure): shared callees `E0043C` and
  `E0045C` are adjacent return-terminated bodies with ten and twelve
  instructions respectively; the supplied callsites bind them to the
  `E004CA` and `E00BEE` candidates. `E03878` is a one-instruction `RETS`
  callee reached by five inspected calls in `E004CA` (E-XE164-024..026).
- OFFEN: these structural repetitions do not establish initialization purpose,
  register/SFR meaning, ABI, K-Bus behavior, complete callers or runtime use.
- VERIFIZIERT (byte comparison): the `E0043C` and `E0045C` bodies share a
  23-byte prefix and eight-byte branch/bit-set/return suffix; the latter body
  differs at the next byte and inserts six bytes before that suffix
  (E-XE164-027). A common-template interpretation remains HYPOTHESE.
- VERIFIZIERT (bounded static structure): `E00B42..E00B83` is a straight-line
  seventeen-instruction callee ending in `RETS` exactly before the retained
  secondary startup-record bytes at `0x0B84`; caller `E004DA` is byte-bound
  (E-XE164-028). This adjacency does not prove a semantic relationship.
- VERIFIZIERT (bounded static structure): adjacent predecessor
  `E00ACC..E00B41` is another straight-line callee, with 32 instructions and
  terminal `RETS`; caller `E004D0` is byte-bound (E-XE164-029). Its segmented
  numeric operands remain syntax only, not an address-space contract.
- VERIFIZIERT (bounded static structure): `E00972..E00ACB` is a larger
  112-instruction reachable CFG with 135 local edges, five outgoing direct
  calls and terminal `RETS`; caller `E004D4` is byte-bound (E-XE164-030).
  This structural graph does not qualify its callees or numeric operands.
- VERIFIZIERT (bounded decode): `E007D4..E00807` contains 23 body
  instructions, three direct calls, local branches and a decoded terminal
  `RETS`; caller `E009E8` is byte-bound (E-XE164-031). Seed reachability after
  the first call remains OFFEN without callee-return evidence.
- VERIFIZIERT (bounded static structure): the `E00808` CFG has 39 reachable
  instruction starts, 45 local edges, no direct calls and three reachable
  `RETS` terminals; caller `E00A16` is byte-bound (E-XE164-032). No branch or
  operand meaning is inferred.
- VERIFIZIERT (bounded static structure): the `E006C4` CFG has 27 reachable
  instruction starts, 34 local edges, no direct calls and two reachable
  `RETS` terminals; caller `E0098A` is byte-bound (E-XE164-033). The broader
  decode after `0x071F` is excluded and no operand meaning is inferred.
- VERIFIZIERT (bounded static structure): the `E00888` CFG has 20 reachable
  instruction starts, 21 local edges, no direct calls and two reachable
  `RETS` terminals; caller `E00AAE` is byte-bound (E-XE164-034). Numeric
  address and bit operands remain syntax only.
- VERIFIZIERT (bounded decode): `E008C2..E00925` contains 37 body
  instructions, bounded local branches, two decoded `RETS` instructions and a
  call to the excluded boundary `E00926`; caller `E00ABA` is byte-bound
  (E-XE164-035). Post-call continuation reachability remains OFFEN.
- VERIFIZIERT (bounded static structure): the `E00926` CFG has 23 reachable
  instruction starts, 28 local edges, no direct calls and two reachable
  `RETS` terminals; caller `E007F4` is byte-bound (E-XE164-036). This does not
  by itself establish the dynamic return/ABI contract used by E-XE164-035.
- VERIFIZIERT (bounded static structure): adjacent callees `E00720` and
  `E0077A` each have 28 reachable instruction starts, no direct calls and two
  return terminals; callers `E007EA` and `E007DC` are byte-bound
  (E-XE164-037/038). Adjacency and repeated shapes do not prove a shared
  semantic contract.
- VERIFIZIERT (bounded decode): `E0054A..E00555` is a five-instruction linear
  callee ending in `RET`; caller `E0064C` is a byte-bound `CALLA+` instruction
  (E-XE164-039). The return/call convention and immediate `00E0` meaning remain
  OFFEN.
- VERIFIZIERT (bounded decode): `E0340E..E03527` contains 110 contiguous
  instructions, four direct calls, local conditional flow and decoded terminal
  `RETS` immediately before the distinct E03528 seed; caller `E0361C` is
  byte-bound (E-XE164-063). Only the first nine instructions are reachable
  without assuming callee returns; the terminal needs four unverified
  call-return continuations. All three targets contain static return terminals,
  and E03520 supplies a direct entry link to E033F0 (E-XE164-064), but actual
  return and state preservation remain OFFEN. No protocol, ABI, SFR or K-Bus
  meaning follows.
- VERIFIZIERT (bounded negative syntax): the complete composite contains no
  `DA E0 5C 35` sequence, the observed direct `CALLS E0355C` encoding form
  (E-XE164-065). Other direct encodings, indirect or external entry into the
  separately decoded E0355C component remain OFFEN. Together with the absent
  E03528-seed edge, this is a two-channel negative link result, not proof of
  unreachability (E-XE164-066); no protocol meaning follows.

## Original-stack emulation boundary

- VERIFIZIERT (static consumer scope): the current revision-bound reports
  account for 22 of 34 ADI slots used or forwarded by the exact FW31
  `libIoDrvDal`/`libIoDrvKbus` consumers. Slot 29 is limited to the later
  documented VCall argument-list forwarding; its exact address and binary hash
  are not restated by that delta source (E-XE164-067).
- VERIFIZIERT (bounded native evidence): original runtime, native manager and
  original drivers processed model-supplied Digital-8 and Digital-16 inputs and
  produced the expected requested-output values at the own provider. Permit
  stayed zero and effective output stayed zero. Provider status/frame values
  are own telemetry, not an internal slot trace (E-XE164-068).
- HYPOTHESE: the 34-slot provider returned by
  `adi_GetApplicationInterface()` is the smallest evidenced replacement cut
  for that bounded digital behavior. The virtual side must supply the selected
  topology/configuration and cyclic process images; it need not reproduce the
  XE164 transport for the behavior already demonstrated (E-XE164-070).
- HYPOTHESE (current minimum boundary matrix): the evidence-only WP-XE164-174
  reconciliation preserves that provider cut after incorporating the exact
  cyclic, Push, DeviceSpecific, status and loader findings through
  E-XE164-201. For the demonstrated Digital-8/16 scope, the mock must preserve
  the observed provider-facing reactions and requested/effective-output
  separation while the original runtime, manager and I/O drivers remain. It
  need not model physical K-Bus/XE164 transport internals. This does not close
  the complete ABI, lifecycle, dynamic binding, arbitrary-module, runtime or
  hardware contract (E-XE164-202).
- VERIFIZIERT (loader-chain countercheck): an independent five-extent GNU ARM
  review reproduces the conditional `L+0x18 -> B+0x20 -> allocated block+0x20
  -> CMLoad return -> AppLoad input -> CMInit indirect-target` position chain
  and its entry, allocation/status, AppLoad and null-target gates. It does not
  identify the selected DSO or target semantics; the IoDrvDal substitution in
  E-XE164-201 remains HYPOTHESE (E-XE164-203).
- HYPOTHESE (bounded acceptance contract): the minimum provider-facing
  Digital-8/16 contract now has twelve explicit rows. Only the historical
  bounded native demonstration is PASS. Enumeration/open ordering, cyclic
  start-transfer-end and last-status behavior, separated Write gate/position
  returns, and separated Push results are static acceptance requirements and
  remain NOT_RUN. The physical K-Bus interior is excluded only from this
  bounded target, not disproved or reconstructed (E-XE164-204).
- VERIFIZIERT (test-source inventory): pinned own-provider assertions directly
  cover selected read/write, Push, DeviceSpecific and error/safety reactions;
  provider shape, original registration and lifecycle remain only indirect,
  and no supplied assertion covers the physical K-Bus/XE164 interior. All
  tests remain NOT_RUN and do not qualify original consumers or runtime
  behavior (E-XE164-205).
- VERIFIZIERT (own implementation mapping): exact current adapter source
  visibly implements the requested/effective-output separation. The original
  WriteOutputs gate/position-return handling and original provider-Push helper
  normalization are not visible in that file; the remaining minimum-contract
  rows are partial or concern external consumer/runtime behavior. This is a
  source mapping only, with builds/tests/runtime NOT_RUN (E-XE164-206).
- VERIFIZIERT (current CI wiring): the clean tracked tree wires only the bridge
  transport C test into the hardware-free unittest workflow, via a Python test
  that can skip when `cc` is absent. The four pinned adapter/default/integration
  C harnesses have no current tracked build/compiler/import edge in that
  workflow. This is not a CI execution result (E-XE164-207).
- HYPOTHESE (responsibility at the seam): retained original layers keep their
  enumeration/cyclic order, status aggregation, Write gate/position handling
  and Push-result combination. The replacement provider supplies only the
  provider-visible model inputs/outputs and bounded result reactions. In
  particular it must reproduce visible Push pointer/error/zero-nonzero behavior,
  not the physical exchange helper or consumer state machine (E-XE164-208).
- The exact WriteOutputs body obtains three indirect targets from a pointer read
  at context position `+0x61c`, then positions `+0x30`, `+0x40`, and `+0x3c`.
  This is a local positional observation only; no table/API identity or return
  contract follows (E-XE164-209).
- Exact IoDrvKbus ELF-VA `0x277c` has two statically materialized direct A32
  callsites. Their fixed windows expose constants `r2=2,r3=0x8008` and
  `r2=1,r3=zero_extend16([r5])`, respectively, but source objects, caller
  ownership and profile meaning remain OFFEN (E-XE164-210).
- Extended but fixed caller windows do not recover the provider object roots:
  the first site inherits both `r6/r7`; the second inherits `r7` and its
  initial `r5`, while locally setting only comparison value `r8=0x8008` and
  loop-stepping `r5` by 24 (E-XE164-211/212).
- Exact IoDrvDal contains one direct immediate store at displacement `+0x61c`
  (`0x2f94`) among nine syntactic same-displacement memory operands. This is a
  candidate for instance-field publication, but the target base and written
  address are not yet bound to the IoDrvKbus consumer object (E-XE164-213).
- The direct IoDrvDal `+0x61c` store writes exact numeric value `0x1a270`,
  reconstructed from bounded literal/PC arithmetic. The target remains
  relative to unresolved `r4`; the value is not yet a named table or object
  (E-XE164-214).
- Exactly two direct A32 transfers target the local IoDrvDal entry candidate
  `0x2ddc`, but neither fixed caller window exposes `r4`. The implicit target
  base therefore cannot yet be assigned a calling-convention or object meaning
  (E-XE164-215).
- Within IoDrvDal, numeric VA `0x1a270` is unnamed NOBITS `.bss`, not a
  file-backed table and not a Dynsym/relocation-bound object. A same-numbered
  symbol in IoDrvKbus is a different ELF and cannot qualify it (E-XE164-216).
- In the early IoDrvDal lane, two calls to the imported
  `adi_GetApplicationInterface` name feed indirect calls through returned
  positions `+0x0c/+0x10`; their result gates precede publication at instance
  positions `+0x618/+0x61c`. The name does not define a contract (E-XE164-217).
- The disjoint late lane computes instance candidate base
  `r4=r0+0x63c*fp` and initializes thirteen exact relative regions, including
  `+0x620/+0x628/+0x62c`; its absolute base remains open (E-XE164-218).
- Conditional cross-range synthesis carries the computed IoDrvDal basis
  through explicit zero/success gates to `+0x618/+0x61c/+0x620` publication and
  then as the first argument of the resolved Init call. Opaque-call `r4`
  preservation and runtime execution remain assumptions, so the combined
  result is HYPOTHESE (E-XE164-219).
- HYPOTHESE/OFFEN: E-XE164-001..066 yield no additional ADI contract, but do
  not prove all XE164 code irrelevant or below every parallel service path.
  `libwago_dbus`, `libdiagnostic`, board metadata/signature helpers,
  callback/lifecycle behavior and unmodeled module classes remain separate
  closure gates (E-XE164-069/070).
- VERIFIZIERT (source scope): the own adapter assigns all 34 table entries and
  implements every one of the 22 observed/forwarded slots. No contradiction to
  the bounded digital matrix is visible in the source. This is not an ABI or
  runtime PASS; device-specific outer/inner results and unobserved callbacks
  remain open (E-XE164-071).
- VERIFIZIERT (test-source inventory): local assertions exist for the main own
  digital state machine, transaction, diagnosis, VCall, watchdog, permit,
  fault, lease and basic lifecycle paths. They were not executed in this
  static-only package, and several systematic failure/lifecycle cases remain
  uncovered in the supplied source set (E-XE164-072).
- HYPOTHESE: preserve authentic Board/SysTarget/diagnostic/runtime services for
  the bounded native target. The successful isolated Digital-8 run hid Host
  D-Bus and physical K-Bus/UIO/Mem endpoints, but did not individually trace
  every surrounding service or qualify a fully virtual replacement
  (E-XE164-073).
- VERIFIZIERT (source scope): the own adapter's effective-output state is
  fail-closed across the visible four gates: application running, explicit
  permit, healthy watchdog and no latched fault. Only a complete owned write
  frame can publish a nonzero value; requested output remains separately
  observable (E-XE164-074).
- VERIFIZIERT (source scope): the bridge control plane has no SPS-output write
  command. Active-session teardown revokes permit, but an ordinary stop with
  no connected client contains no unconditional revoke. Watchdog expiry clears
  effective output without clearing the stored permit bit (E-XE164-076).
- VERIFIZIERT (source scope): bridge-enabled reset is outside the lifecycle
  lock/stop sequence. It can clear adapter initialization while leaving the
  bridge worker marked started, after which Exit rejects before reaching
  bridge stop. This is not an observed runtime failure (E-XE164-075).
- VERIFIZIERT (document/test reconciliation): the public unconditional
  Bridge-STOP/permit wording and claimed parallel Init/Exit coverage are not
  supported by the pinned source/test paths. The concrete native rollback PASS
  remains a separate operational result (E-XE164-077).
- VERIFIZIERT (own source scope): DeviceSpecific Call and VCall share one
  dispatcher and separate outer DAL status from the inner operation result.
  Terminal-info32 and read-table-9 are bounded model operations; UID and
  config-register are explicit rejections, not partial emulations. Original
  Push and full slot-29 behavior remain open (E-XE164-078).
- VERIFIZIERT (original-consumer report scope): only enumeration-to-open and
  the local Start/transfer/End read and write orders are established. A full
  Init-to-Exit order, Watchdog order and Close path are still open
  (E-XE164-079).
- HYPOTHESE (bounded architecture): remaining Digital-8/16 gaps should be
  resolved at the nearest evidence layer: local Reset/STOP policy in the own
  adapter, full lifecycle/Push in an exact ARM caller trace, and active-output
  behavior only in a later authorized runtime test. None currently requires a
  broad lower XE164 trace (E-XE164-080).
- HYPOTHESE (local remediation design): Reset can follow the existing Exit
  lifecycle/state/unlocked-join order, and a started worker's successful stop
  can revoke permit after join while no bridge-control lock is held. This is a
  proposed own-model repair shape only; no code or tests were changed
  (E-XE164-081).
- VERIFIZIERT (artifact identity): the provider extracted from the manifested
  FW30 IPK has the exact byte size and SHA-256 recorded for the backed-up FW31
  `libpackbus.so.1.0.1`. It can therefore answer bounded original-provider
  questions such as Push. The package has no `libIoDrvDal`/`libIoDrvKbus`, and
  no other FW30 artifact is promoted to FW31 ABI by this match (E-XE164-082).
- VERIFIZIERT (FW31-identical provider static scope): original
  `libpackbus_Push` returns `-1` on the three observed missing-pointer paths;
  otherwise it selects normal data exchange or watchdog-error reaction and
  maps the selected helper's zero result to `0` and any nonzero result to
  `-1`. Hooks, timer, lock and observer cleanup surround the selected call.
  Two local callers reach it through the PLT; one treats nonzero as the slower
  retry/sleep path. The outer DeviceSpecific DAL result is not implemented by
  this ELF and remains OFFEN (E-XE164-083/084).
- VERIFIZIERT (exact FW31 DAL dispatcher static scope):
  `Dal_CallDeviceSpecificFunction` selects a cached pointer or its fallback,
  calls it once, and performs no observed post-call mapping or normalization.
  The callback's `r0` survives the outer epilogue, but no direct caller or
  declaration establishes that register as a semantic API status
  (E-XE164-090).
- VERIFIZIERT (exact FW31 IoDrvKbus Push-caller scope): the published
  `0x2704` callback reaches a `libpackbus_Push`-named indirect call after
  observed guards and returns zero only when both the outer return and the
  pointer-result cell are zero. Its second input and global guard field are
  not statically proven to be a prior WriteEnd result (E-XE164-091).
- VERIFIZIERT (exact FW31 cyclic consumer scope): ReadInputs and WriteOutputs
  each reject a nonzero start-call result with numeric `2`, discard their
  finish-call return, and map the last status-setting transfer's zero/nonzero
  value to final `0`/`2`. This is overwrite/last-result behavior, not an OR of
  all transfer results. WriteOutputs separately retains one gate result and
  uses two callback returns as address/base values rather than final status
  (E-XE164-092/093).
- HYPOTHESE (bounded Digital-8/16 lower-boundary contract): retain separate
  outer/pointer Push results, preserve start/finish side effects, and reproduce
  last-status overwrite rather than cumulative first-error/OR aggregation.
  The indirect provider/DAL bindings and manufacturer type/status semantics
  are still OFFEN (E-XE164-094).
- VERIFIZIERT (exact FW31 fragment scope): the code at `0x2614..0x264f`
  returns numeric `2` for either zero among the observed second/third incoming
  registers or for sentinel `0xffffffff` in the first; otherwise it performs
  an unconditional tail-transfer to `idk_CalculateSlotNumber@plt` after
  moving the second/third inputs into `r0`/`r1`. Init publishes this code value
  at output displacement `+0x62c`, but all external field/parameter/status
  meanings remain OFFEN (E-XE164-088/097).
- VERIFIZIERT (exact FW31 candidate scope): Init publishes `0x2eb8` at
  output displacement `+0x634`. Its bounded entry reaches the main body only
  for the observed `r2==2` and nonzero-`r1` register case; otherwise it returns
  numeric `2`. The body contains explicit constant and call-derived status
  paths, including a later call result that replaces the retained status only
  when that status is zero. Field, parameter and status semantics remain OFFEN
  (E-XE164-098).
- VERIFIZIERT (exact FW31 candidate scope): Init publishes `0x24e4` at
  output displacement `+0x630`. Its bounded body enforces observed
  null/sentinel and `0x8008` guards, writes one table-derived word through an
  input pointer, conditionally computes a maximum over 96 strided words, and
  retains an earlier nonzero status instead of replacing it with the final
  direct-call result. Field, parameter, table and numeric status semantics
  remain OFFEN (E-XE164-099).
- VERIFIZIERT (bounded exact FW31 candidate scope): Init directly publishes
  code value `0x33b0` at output displacement `+0x44`. The bounded bytes contain
  a computed dispatch, loopbacks, one observed return, one direct and six
  register-indirect calls; Ghidra supplies no containing procedure. Field,
  complete-function and target semantics remain OFFEN (E-XE164-100).
- VERIFIZIERT (exact FW31 procedure scope): Init publishes code value `0x2120`
  at output displacement `+0x638`. The procedure applies observed guards,
  preserves an earlier nonzero status through its loops, dispatches two
  indirect-call results, and adopts the final direct-call result only while
  the retained status is zero. Its own `+0x10` stores are separate from this
  Init lane. Field, parameter, table and status semantics remain OFFEN
  (E-XE164-101).
- VERIFIZIERT (exact FW31 helper scope): the common entry/leave wrappers call
  values loaded from ELF object cells named `pfSysSemEnter` and
  `pfSysSemLeave`, log only a nonzero result through the loaded `pfLogAdd`
  value, and return the original result unchanged. Object names do not prove
  runtime targets, signatures or synchronization semantics (E-XE164-102).
- VERIFIZIERT (exact FW31 stored-rootfs scope): `IoDrvDal.cfg` statically maps
  `libIoDrvKbus` to `IoDrvKbus_Init`. A complete scoped name/content scan found
  no foreign ELF importing the named Init/ReadInputs/WriteOutputs exports.
  Loader execution and generic/indirect consumption of the initialized object
  remain OFFEN (E-XE164-103).
- VERIFIZIERT (exact FW31 named-dispatch scope): IoDrvKbus reaches the four
  scoped `libpackbus_*` operation names through a callable loaded from the
  observed dispatch field at `+0x70`. Its bounded sites jointly check the
  outer return and separate inner-result word; terminal-info preflight instead
  requires outer zero plus inner numeric `2`. Normal terminal-info passes
  observed capacity `0xfa0`; four read-conf-reg sites use selectors
  `0x1e/0x1c/0x10/0x1d`. Full provider ABI and profile reachability remain
  OFFEN (E-XE164-104).
- VERIFIZIERT (exact FW31 generic-loader scope): IoDrvDal computes an
  instance basis as `input_base + index * 0x63c`, reads `ConfigLibrary` and
  `EntryFunction` into that instance region, opens the selected library,
  resolves the selected symbol and calls it with the same basis pointer as
  the only visible argument. The stored instance-0 values select
  `libIoDrvKbus` and `IoDrvKbus_Init`, but actual instance-0 execution is
  OFFEN. The observed `0x63c` is a stride, not a proven allocation size or
  complete structure contract (E-XE164-103/105).
- VERIFIZIERT (exact FW31 record-validation scope): one IoDrvKbus procedure
  iterates `0x14`-byte records and conditionally requires the named get-uid
  and read-conf-reg provider operations. The former is limited by observed
  discriminator/type/slot guards and contributes accumulator bit `0x20` only
  after outer/inner success plus DWORD equality. The latter is limited by a
  different discriminator/type/flag set and applies one of four verified
  masked comparisons. Their scoped failure paths converge on numeric status
  `0x10`; completed iteration adds `0x40`, and only combined `0x70` reaches a
  terminal-size branch. Raw values are not semantic module identifiers, and
  reachability for a selected Digital profile remains OFFEN (E-XE164-106).
- VERIFIZIERT (current own-source/evidence scope): get-uid and read-conf-reg
  share an intentionally unsupported adapter branch: outer success, inner
  `-1`, own fault latch. Only get-uid has a direct assertion in the inspected
  own C test. The corrected Digital-8/16 reports show successful bounded
  originalconsumer signal processing with regular fault value zero, but no
  named-dispatch trace. Thus those trials do not evidence a conflict, nor do
  they prove the calls unreachable. If reached, inner `-1` would fail the
  E-XE164-106 inner-zero condition (conditional HYPOTHESE; E-XE164-107).
- VERIFIZIERT (exact FW31 static manager/loader chain): named export
  `ComponentEntry` publishes a dispatcher pointer at output `+0x18`; numeric
  selector `3` can conditionally reach a loop that calls the configured
  IoDrvDal loader with a base pointer, literal `0x10062001`, a preincrement
  global counter and an output pointer. Neither field nor selector has a
  proven lifecycle name, and execution remains OFFEN (E-XE164-105/108).
- VERIFIZIERT (loader preincrement storage): the word read and incremented
  before the generic loader call is exact IoDrvDal `.bss` ELF `0x163d4`
  (Ghidra `0x263d4`). Six materialized direct Xrefs include a separate path
  that can store zero and the call lane's read-plus-one/write. Their first-run
  ordering is not established, so a first value or first loader index remains
  OFFEN rather than inferred from `.bss` or the zero-store alone
  (E-XE164-155/156).
- VERIFIZIERT (selector-3 predecessor separation): selector `3` enters through
  table slot `0x3650 -> 0x3738`, whereas the possible zero-store belongs to
  distinct slot `0x367c -> 0x3684`. The first bounded loader iteration has
  local loop register `r4=0`, but call register `r2` independently receives
  the unknown prior `.bss` word before increment. Therefore neither the
  bypassed zero-store nor the zero loop variable proves a first loader
  argument of zero (E-XE164-157).
- VERIFIZIERT (exact FW31 static validation-caller chain): the record validator
  has two direct callers. One lies in the candidate Init publishes at `+0x634`
  and passes numeric mode `2` after a `0x8008` guard; the other lies in the
  candidate published at `+0x40` and passes mode `1` on a record-halfword
  equality path. Profile reachability and field semantics remain OFFEN
  (E-XE164-096/098/106/109).
- HYPOTHESE (consolidated bounded architecture): retain original IoDrvDal and
  IoDrvKbus and emulate the provider returned by `adi_GetApplicationInterface`
  for the exact demonstrated Digital-8/16 profiles. The minimum surface is
  discovery/open/configuration, bounded terminal description, separate outer
  and inner DeviceSpecific results, cyclic read/write transactions,
  diagnosis/state/watchdog and fail-closed model output handling. No accepted
  evidence makes a physical K-Bus or XE164 behavioral model necessary for
  this bounded milestone. This does not cover other profiles, surrounding
  services or general K-Bus completeness (E-XE164-110).
- VERIFIZIERT (exact FW31 scan, fixed values): the named Table-9 result is
  interpreted as signed 16 bit. Values `0x8801/0x8802/0x9001/0x9002` take the
  negative formatting branch and bypass all four local read-conf helper calls
  in `idk_IoDrvScanModules`. This does not prove runtime value production or
  success of that branch (E-XE164-111).
- VERIFIZIERT (current profile and recorded-trial scope): current own
  Digital-8/16 profile files consistently contain those four high-bit values,
  and accepted reports record the bounded native trials (E-XE164-112).
- OFFEN (profile provenance): embedded trial-time source hashes do not equal
  the current profile/catalog hashes; byte-exact revision binding and
  equivalence were not established by that package alone (E-XE164-112).
- VERIFIZIERT (scoped provenance closure): the older hashes are exact
  path-bound local Git blobs, and the Digital-8/16 profile, four model and four
  descriptor fields relevant here are unchanged in the current revision.
  Unrelated catalog sections changed; no trial was rerun (E-XE164-115).
- VERIFIZIERT (exact FW31 comparison validator, conditional):
  `idk_Valid_ModuleCmpValue` performs Table-9 first, requires outer and inner
  zero plus equality with the parsed 4-character field at input `+4`, then
  returns true on bit 15 before its four local read-conf dispatches. The body
  has no named get-uid dispatch. Caller construction, parser semantics and
  actual runtime values remain OFFEN (E-XE164-113).
- VERIFIZIERT (exact four-byte helper mechanics): the comparison helper reads
  four bytes, enforces runtime ctype mask `0x1000`, selects one of two
  mask-`0x400` contribution formulas, accumulates in base 16 and returns `-1`
  on the first rejected byte. Treating the masks as ordinary GNU ASCII-hex
  classes is HYPOTHESE until runtime ctype/locale tables are bound
  (E-XE164-114).
- VERIFIZIERT (exact comparison caller lane): the record validator reaches
  `idk_Valid_ModuleCmpValue` through a 12-byte thunk only on the observed
  discriminator-10, nonnegative-slot and record-halfword-16 path, passing the
  object at first input `+0x61c`, a guarded nonnull accessor result pointer and
  the low slot byte. Record halfword values 4 or 12 instead feed the separate
  get-uid path. Which record form a selected profile constructs remains OFFEN
  (E-XE164-106/116).
- VERIFIZIERT (exact accessor object binding): the comparison-string pointer
  is obtained through the `.bss` object named
  `pfIoMgrConfigGetParameterValuePointer`, reached by a literal/GOT/
  `R_ARM_GLOB_DAT` chain. The loaded object content is called indirectly;
  name, relocation and call mechanics do not establish the concrete runtime
  callback or complete signature (E-XE164-118).
- VERIFIZIERT (exact Init setup shape): `IoDrvKbus_Init` passes the exact name
  `IoMgrConfigGetParameterValuePointer` and address of the global pointer
  object to an unresolved indirect resolver-like call, with three further
  observed zero arguments, and treats a nonzero result as failure. The
  resolver target and successful runtime population remain OFFEN
  (E-XE164-119).
- VERIFIZIERT (Init resolver-slot provenance): the unresolved call target is
  loaded from BSS slot `0x1a1c0`, which the same Init previously populates from
  the 32-bit value reached through input offset `+0x620` and nested offset
  `+0x34`. These are positional memory accesses only; field/API meaning,
  intervening alias writes and the runtime target remain OFFEN (E-XE164-122).
- VERIFIZIERT (complete FW31 name inventory): exact `/usr/bin/codesys3` defines
  `IoMgrConfigGetParameterValuePointer` as an 84-byte dynamic `FUNC` symbol at
  ELF `0x32e814`. Seven driver DSOs separately define the `pf...` four-byte
  dynamic `OBJECT`; no exact undefined symbol for either name was found in the
  nine hit ELFs. This makes `codesys3` a concrete static provider candidate,
  not proof of the resolver result or a complete contract (E-XE164-123).
- VERIFIZIERT (parallel IoDrvDal setup form): a separate exact Dal lane passes
  the same accessor name, a BSS-slot address and three observed zeros to an
  unresolved computed target loaded from another BSS slot. Nonzero return
  exits the sequence; zero continues to the next name/slot pair. This repeated
  registration-like shape still does not prove the target, API signature or
  runtime binding (E-XE164-124).
- VERIFIZIERT (exact named provider body): the 84-byte `codesys3` function
  checks 32-bit bit `0x2` at input `+0x0c`; on that path it returns the 32-bit
  value at input `+4` and optionally stores status `0`. Otherwise it returns
  zero and optionally stores status `2`. The body has no calls. Field/status
  meanings and dynamic binding into driver pointer slots remain OFFEN
  (E-XE164-125).
- VERIFIZIERT (Dal-to-driver service-data handoff): the generic Dal loader
  stores global address `0x2a234` at computed instance basis `+0x620`, then
  passes that basis to the resolved driver Init. Kbus Init subsequently follows
  that input position before reading nested `+0x34`. `ComponentEntry` fills the
  15-word global range from current input `+0x00..+0x38`; specifically global
  `0x2a268` (`base+0x34`) receives input `+0x34`. The external input source,
  prior indirect-call alias effects and semantic field names remain OFFEN
  (E-XE164-122/126/128).
- VERIFIZIERT (two timed copies of the same input position): before the optional
  `ComponentEntry` call, current input `+0x34` is stored to Dal BSS `0x26090`,
  which later supplies the target of Dal's own accessor-name call. After that
  optional call, current input `+0x34` is copied to `0x2a268` and follows the
  established Dal-to-Kbus path. Equality of those two stored values is only
  HYPOTHESE because the intervening call may alias input memory
  (E-XE164-131/132).
- VERIFIZIERT (static accessor name/body pair): a corrected 16-byte
  `codesys3` rodata record contains function pointer `0x32e814`, a pointer to
  the separate exact `IoMgrConfigGetParameterValuePointer` literal and two
  zero words. Neighbor records corroborate `[function,name,0,0]` phasing.
  A bounded `codesys3` call lane passes the containing table start `0x3add1c`
  with numeric `r3=18` to an unresolved target; the exact 18-record raw window
  places this accessor at zero-based index 16 and ValueByte at index 17. Treating
  `18` as a record count is HYPOTHESE, and resolver-to-driver runtime binding
  remains OFFEN (E-XE164-127/129/130).
- VERIFIZIERT (table-call target-slot provenance): the shared `codesys3` target
  slot for both indirect table calls has one materialized writer.
  `CmpIoMgr__Entry` copies its input `+0x1c` into BSS `0x00601670`; the later
  procedure null-checks and reloads it for both calls. External source,
  callback identity/signature and runtime order remain OFFEN (E-XE164-133).
- VERIFIZIERT (entry-local source and export boundary): the complete bounded
  `CmpIoMgr__Entry` body reads the 32-bit value at input `+0x1c` before the
  slot store, has no materialized direct caller or exact entry Xref, and is a
  348-byte `GLOBAL DEFAULT FUNC` in ELF `.dynsym`. REA reports conflicting
  `dynamic:false` name metadata. Dynamic name-based invocation is therefore
  only HYPOTHESE; the export proves neither caller nor API contract
  (E-XE164-138/139).
- VERIFIZIERT (exact-name inventory bound): across all 3,058 regular files in
  exact FW31 partition 2, `CmpIoMgr__Entry` occurs once and only in `codesys3`;
  that sole hit is the known defined Dynsym entry and has no matching standard
  relocation row. This closes only the exact-literal/regular-file search, not
  indirect or dynamic invocation without another stored copy of the name
  (E-XE164-140).
- VERIFIZIERT (paired raw collections): the first indirect call receives a
  separate 18-record window at `0x3ad9fc` with `r2=1`, `r3=18`; after zero it
  calls the same slot with the later window, `r2=0`, `r3=18`. All 18 same-index
  function/name pairs differ, and only the first window has the observed
  nonzero fourth-word pattern. A two-mode collection-submission interpretation
  is HYPOTHESE, not a callback/API contract (E-XE164-134/135).
- VERIFIZIERT (same-position entry bodies are not direct aliases): the first
  collection's `iomgrconfiggetiodriver` target `0x334790` is a frame stub that
  tail-branches to `0x334648`, whereas the second collection's
  `IoMgrConfigGetDriver` target `0x32ea90` is a distinct no-call body with a
  bounded `r0/+8` value path and optional numeric status stores `0`/`2`.
  No direct relation between these two bodies is observed; similar names and
  table position do not establish one contract (E-XE164-141).
- VERIFIZIERT (module-entry resolution boundary): `MainLoadComponent` resolves
  the exact `ComponentEntry` name through `SysModuleGetFunctionPointer`; its
  immediate caller places the result at local-block `+0x10` and passes that
  block to helper `0x2fc530`. Neither bounded function calls the resolved value
  or constructs a visible `+0x34` input position. That provenance remains OFFEN
  at the exact helper boundary (E-XE164-136/137).
- VERIFIZIERT (module-entry invocation boundary): helper `0x2fc530` loads the
  resolved pointer from its incoming block `+0x10`, prepares a local stack
  object at `fp-0x5c`, and invokes the pointer with that object's address in
  `r0`. In the exact caller context this is the resolved `ComponentEntry`.
  A nonzero result unconditionally stores halfword `3` at caller-block `+0x2c`;
  object-field semantics and runtime execution remain OFFEN (E-XE164-142).
- VERIFIZIERT (module-entry result copyback): after a zero entry result, the
  helper copies selected local positions into caller block `+0x00`, `+0x14`
  through `+0x1c`, and `+0x20` through `+0x28`. Local `+0x0c` is itself an
  optional indirect target; its returned `r0` is stored at caller `+0x0c`.
  A nonzero entry result instead writes halfword `3` at caller `+0x2c` and
  returns `1`. These are positional mechanics, not named fields or semantic
  status definitions (E-XE164-159).
- VERIFIZIERT (complete bounded pre-call initialization): before the resolved
  entry call, the helper zeroes local `+0x04..+0x0c` and `+0x18`, leaves local
  `+0x00` without a bounded initializer, and installs eight exact code-pointer
  values across `+0x1c..+0x38`. Seven are exact Dynsym addresses; `+0x28`
  points to the already bounded but unexported `0x30066c` body. These address
  identities and symbol names are not full service/API contracts
  (E-XE164-160).
- VERIFIZIERT (downstream positional consumption): only a zero helper result
  reaches `CMLoadComponent3`'s two null-guarded consumers at caller block
  `+0x14` and `+0x18`. Each nonnull word is called with `r0=0`, and each call
  must return zero before the later hook/component path continues. The caller
  does not establish `r1/r2` in this lane. Target values, signatures and
  semantics remain OFFEN (E-XE164-161).
- VERIFIZIERT (joined positional lifecycle): local `+0x04/+0x08` are zero
  before the resolved entry call, copied after zero return, and then consumed
  as the two guarded caller targets. Any later nonzero value therefore differs
  during or as a side effect of the entry call. Treating these as lifecycle
  publication slots is HYPOTHESE; the mechanics do not identify the writer,
  concrete component, callback names or signatures (E-XE164-162/163).
- VERIFIZIERT (exact IoDrvDal publication positions): IoDrvDal
  `ComponentEntry` unconditionally replaces input `+0x04/+0x08` with
  link-relative code addresses at ELF `0x1704` and `0x0b58`; four further
  code-address values occupy `+0x0c..+0x18`, while `+0x00` receives
  `0x10062001`. The one local branch only guards the later input-`+0x28`
  indirect call, and both lanes return zero. Connecting these writes to the
  generic codesys3 pipeline still requires the concrete dynamic module binding
  (E-XE164-164).
- VERIFIZIERT (static module-name inventory limit): the exact FW31 image has
  the full IoDrvDal symlink chain and the target DSO exports Dynsym
  `ComponentEntry`, but no single configuration/manifest record in the
  complete partition-2 scan pairs an exact `libIoDrvDal` token with that entry
  name. `IoDrvDal.cfg` instead contains `ConfigLibrary="libIoDrvDali"`, whose
  relationship is OFFEN. Artifact co-location does not close runtime binding
  (E-XE164-165).
- VERIFIZIERT (DALI near-name scope): `libIoDrvDali` occurs in the coherent
  DALI-labelled `[IoDrvDal.8]` record alongside `libdali`, `WAGO_SRC_DALI` and
  `IoDrvDali_Init`; it is therefore not an exact pairing record for
  `libIoDrvDal`/`ComponentEntry`. No matching DALI library/symlink basename is
  present in partition 2, so whether the record is intended, stale, aliased or
  misspelled remains OFFEN (E-XE164-168).
- VERIFIZIERT (first published target mechanics): exact IoDrvDal target ELF
  `0x1704` ignores the caller's incoming `r0`, returns `3` if its global target
  is null, otherwise submits link-relative argument objects `0x15e28` and—only
  after a zero result—`0x15e4c` to the same reloaded indirect target. It
  returns the first nonzero result or the second result. Target signature,
  argument-object meaning and status semantics remain OFFEN
  (E-XE164-166; explicit agreement with E-XE164-087).
- VERIFIZIERT (ComponentEntry symbol/body split): the 560-byte Dynsym span is
  a 476-byte Ghidra procedure followed by 84 bytes/21 words of referenced data.
  Every tail word has one direct body read, the body ends in a return before
  the tail, and `_DT_FINI` begins after it. Thus the symbol size must not be
  used as a 560-byte executable-body boundary (E-XE164-167).
- VERIFIZIERT (second published target mechanics): exact IoDrvDal target ELF
  `0x0b58` ignores incoming `r0` and performs 62 unresolved calls using observed
  name-string/output-cell pairs. The first two results are ignored; calls
  3–61 fail fast on the first nonzero result, and call 62 supplies the result
  otherwise. Names and positional arguments do not establish API signatures
  or contracts (E-XE164-169; corrected countercheck of E-XE164-087).
- VERIFIZIERT (custom-component path inventory): exact FW31 `codesys3`
  contains NUL-separated literals `Components.Directory` and
  `/usr/lib/cds3-custom-components`; the only other partition-2 occurrences
  are package installation lists. No explicit startup/config/service record
  passes that path to the runtime in the complete exact-string scan. Literal
  adjacency alone leaves key/value interpretation and loader execution OFFEN
  (E-XE164-170).
- VERIFIZIERT (path direct-Xref scope): exact `.rodata` addresses for the full
  custom-component path and its basename substring yield no direct incoming
  Xref under the bounded REA/Rizin/objdump/raw-pointer methods. Therefore no
  consuming function or call argument is established by this route. Computed,
  relocated, table-mediated and runtime uses remain OFFEN; the null result is
  not nonuse evidence (E-XE164-172).
- VERIFIZIERT (key/default call setup): a separate bounded ARM pattern builds
  the exact `Components.Directory` address in `r1`, stores the exact adjacent
  custom-component path address at `[sp]`, and immediately calls the Dynsym
  target `SettgGetStringValue`. This establishes one static call-level
  correlation, not the argument meanings, returned value, override precedence
  or runtime execution (E-XE164-173).
- VERIFIZIERT (direct directory-open separation): exact `SysDirOpen` has 20
  direct `bl` callers, but none of their immediate 192-byte windows
  materializes either exact key/path address in the checked forms. This rules
  out only an immediate local literal link; earlier, indirect or dynamic path
  propagation remains OFFEN (E-XE164-174).
- VERIFIZIERT (settings wrapper mechanics): exact `SettgGetStringValue` is a
  92-byte wrapper that preserves its four register inputs, compares the second
  entry-stack word with one, conditionally calls `SettgBeUpdateCache`, and
  otherwise restores the original inputs before a tail transfer to
  `SettgBeGetStringValue`. Names and the numeric predicate do not establish an
  API contract or semantic mode (E-XE164-175).
- VERIFIZIERT (settings-to-directory address flow): after the first key/path
  call, its `r0` return is overwritten. The exact local address `fp-1324` that
  entered that call in `r2` nevertheless reaches `r0` at both direct
  `SysDirOpen` lanes chosen after a second settings call. This establishes
  static address continuity only; the local contents, default/override choice,
  producer and runtime lane remain OFFEN (E-XE164-176).
- VERIFIZIERT (backend transport): exact `SettgBeGetStringValue` preserves the
  concrete caller's `r2=fp-1324`, reads its entry-stack word containing the
  default-path address and supplies those two values together as `r0` and `r2`
  to direct target `0x304760`. The body does not directly store through
  `fp-1324`; actual target effects and selected contents remain OFFEN. A
  separate input-r3 pointee receives bounded length/default-related direct
  stores (E-XE164-177).
- VERIFIZIERT: In the default-lane count and terminator path, exact target `0x304760`
  rejects any zero register input with return `2`. On its valid-input path it
  prepares two direct calls, directly writes byte zero at
  `input r0+input r1-1`, and selects local return `15` or `0` by an unsigned
  count comparison. The caller derives `input r1` from a raw call return plus
  one, optionally caps and stores it, then supplies `fp-1324` as input r0 and
  the entry-stack default pointer as input r2. This proves only a conditional
  direct terminator; the preceding bytes and named-call effects remain OFFEN
  (E-XE164-181/184).
- VERIFIZIERT: In the other bounded backend lanes, internal body `0x341934` does not itself
  write through the caller local passed in its input r2; it forwards that
  value as r3 to `0x340240` with stack argument zero. Exact `0x340240`
  conditionally writes a computed pointer through that forwarded local and,
  on the reached success completion, returns the zero stack word. The backend
  then reloads the local as input r0 of exact `0x3403A4`, alongside original
  input r2/r3 as its destination/count positions. That final body writes a raw
  call result through its input r2 and conditionally directly zeroes byte
  `input r1+*input r2`. In the concrete key/path caller those outer addresses
  are `fp-1324` and `fp-1356`. Success reachability, pointer roles, callee
  effects and selected runtime lane remain OFFEN (E-XE164-182/183/187/188).
- VERIFIZIERT: A separate exact consumer lane supplies raw bytes
  `ComponentManager`, a generated-local address, output local `fp-180`, a
  count-local address, empty default and numeric zero to
  `SettgGetStringValue`. A direct zero return passes the same `fp-180` address
  to `0x2FCB48`; a nonzero return follows a bounded local counter loop or an
  out-of-range edge. Exact `0x2FCB48` preserves that value without local
  dereference/comparison and conditionally passes it as r1 to its sole direct
  call; its direct-call result selects local return 1 or continued iteration,
  while exhaustion returns zero. This is downstream address continuity, not
  proof of local contents or any callee semantics (E-XE164-185/186).
- VERIFIZIERT: On that exhaustion/zero fall-through, the same `fp-180`
  address reaches exact Dynsym `MainLoadComponent` in r0, with `fp-196` and
  `fp-192` in r2/r3. Exact MainLoad directly stores a module-load raw return
  through r2 and passes r3 with exact string `ComponentEntry` to the named
  resolver target. If MainLoad returns zero, the caller copies current values
  from those two slots into local block `B+8/B+16`, puts `fp-180` at `B+4`,
  and calls exact Dynsym `CMAddComponent` with `B`. This is a static
  settings-to-loader/export-name position chain; successful load/resolution,
  resolver output, entry invocation, selected library, block meanings and
  runtime remain OFFEN (E-XE164-136/189/190).
- VERIFIZIERT: Exact `CMAddComponent` copies 52 bytes from its entry block
  into a newly obtained block. Therefore the preceding caller's current
  `B+16=[fp-192]` reaches new-block `+16`. The complete 130-instruction
  body has no indirect call, so it does not invoke that word locally.
  Resolver output effect/value, field meaning, later consumer or invocation,
  runtime and hardware remain OFFEN (E-XE164-191/192).
- VERIFIZIERT: Exact direct-A32-`BL` inventory for `CMAddComponent` has
  seven sites. Only four lie within exact Dynsym extents; three remain
  unowned rather than inheriting a nearest objdump label. Their bounded input
  forms differ, and only three immediately compare the return with `-1`.
  This is a static direct-call inventory, not runtime reachability or a
  semantic component lifecycle (E-XE164-193/194).
- VERIFIZIERT: Exact `CMInitComponent` is not the sought `+16`
  consumer: its complete 329-instruction body never loads entry-r0 `+0x10`.
  Its eight indirect calls instead have ten visible reaching loads from
  entry-r0 `+0x20`. Caller/input binding and all value semantics remain
  OFFEN (E-XE164-195).
- VERIFIZIERT: A separate `CMInit3` local block passed to
  `CMAddComponent` at `0x301F30` has three path-dependent writes at
  `+0x10`: one VSTR and two later exact alias stores. It is not equated with
  the settings caller's local block. The unsuperseded VSTR word being zero is
  only HYPOTHESE because an opaque call intervenes (E-XE164-196/197).
- VERIFIZIERT: The exact original-loader position chain reaches a later
  consumer on one static success lane. Resolved `ComponentEntry` receives
  local object `L`; helper success copies `L+0x18` to `B+0x20`;
  `CMAddComponent` copies that to allocated block `+0x20`;
  `CMLoadComponent3` returns the allocated block on its non-`-1`,
  zero-status lane; exact `AppLoadCIntegrationModule` then passes it to
  `CMInitComponent`, whose eight indirect sites load from `+0x20`.
  Callback names/signatures, concrete values, selected DSO, execution and
  hardware remain OFFEN/NOT_RUN (E-XE164-200).
- HYPOTHESE: If that dynamically resolved entry is exact IoDrvDal
  `ComponentEntry`, its verified `L+0x18 = 0x362c` publication follows the
  E-XE164-200 position chain to registered block `+0x20` and the
  `CMInitComponent` indirect-call source. Concrete DSO binding, relocation,
  selected call, signature and runtime execution remain OFFEN
  (E-XE164-164/201).
- VERIFIZIERT (post-directory argument/filter mechanics): on the direct setup
  edge, exact `.so` and `.so.` addresses enter `r4/r8` before two named
  substring-call sites. The continuation has a literal three-byte `lib` test,
  a direct zero store through a prior call's returned `r0`, post-call branch
  checks and caller-output/count call arguments plus two direct `[r7]` stores.
  No named callee's compare/copy/termination effect is promoted (E-XE164-178).
- HYPOTHESE (bounded resolver role): the contiguous candidate
  `0x33F548..0x33F993` fits a dynamic-component filename/path resolver below
  the settings backend and above directory enumeration. This does not yet
  prove the produced bytes or their later consumption by the module loader
  (E-XE164-180).
- VERIFIZIERT (installed component convention): all 40 direct symlinks under
  exact `/usr/lib/cds3-custom-components` resolve to distinct regular ELF32
  DSOs and all 40 export exactly one Dynsym `ComponentEntry`. IoDrvDal follows
  the same convention and is not a bounded-population outlier. Whether the
  runtime scans the directory, loads this DSO and invokes that export remains
  OFFEN (E-XE164-171).
- VERIFIZIERT (generic entry-object initializer): the helper's local argument
  base is `fp-0x5c`; it composes `0x002fe12c` and stores it at `fp-0x28`, exactly
  relative `+0x34`, before the resolved entry call. Connecting that generic
  call to exact IoDrvDal is HYPOTHESE. Carrying the value farther through the
  post-callback Dal copy into Kbus additionally requires unproved alias safety
  (E-XE164-143/144).
- VERIFIZIERT (direct generic-loader callers): exact `CMLoadComponent3` has two
  direct `bl` sites and two tail-branch wrappers. Their immediate argument
  sources contain no IoDrvDal literal/path or Dal-specific static reference.
  This does not disprove a later dynamic Dal binding; it keeps that binding
  OFFEN rather than upgrading E-XE164-144 (E-XE164-146).
- VERIFIZIERT (generic object `+0x34` target body): numeric target
  `0x002fe12c` is the 44-byte `CMGetAPI2` body, which repackages stack/register
  arguments and directly calls `CMGetAPI3`. No direct executable call targets
  `CMGetAPI2`; its use in the entry object remains an indirect handoff. Names
  and mechanics still do not establish a full API contract (E-XE164-147).
- VERIFIZIERT (Dal intervening-call arguments): the optional call target comes
  from entry input `+0x28` and is null-guarded. At the call, visible ordinary
  values are `r0=r1=0x10062001` and `r3=&0x26090`; no explicit stack argument
  or direct input/`+0x34` alias is visible. Hidden/global alias routes remain
  OFFEN, so post-call `+0x34` equality stays HYPOTHESE (E-XE164-148).
- VERIFIZIERT (untyped rodata occurrence): a separate `0x002fe12c` word begins
  one observed 16-byte raw group in `.rodata`, but exact REA and focused Rizin
  queries materialize no direct consumer. The repeated adjacency is only a
  table-like HYPOTHESE and adds no API contract (E-XE164-149).
- VERIFIZIERT (generic object `+0x28` target): helper `0x2fc530` initializes
  local entry-object position `+0x28` to exact `0x0030066c`. The complete
  target body uses incoming `r0/r1` for bounded list/pool registration,
  overwrites incoming `r3` before use, calls the named component lookup and
  updates a global counter. Connecting this target to the exact Dal optional
  call remains HYPOTHESE; if connected, the visible body does not consume
  Dal's `r3=&0x26090`, but callee/global alias paths remain OFFEN
  (E-XE164-150/151).
- VERIFIZIERT (generic object `+0x34` callee body): exact `CMGetAPI3` has a
  complete 1,028-byte body plus two referenced literal words in the trailing
  eight bytes of its Dynsym span. In the immediate `CMGetAPI2` context, its
  `r3` points to a local copy of the original `CMGetAPI2` `r3` value. The body
  reads and can conditionally replace that local word once; `CMGetAPI2` does
  not copy it back before returning. Two indirect target identities and one
  returned indirect result remain OFFEN, so no complete API/status contract is
  inferred (E-XE164-152).
- VERIFIZIERT (generic `+0x28` target's lookup callee): exact
  `CMGetComponent` compares its incoming word against linked-node position
  `+0x10`, returns that field's address on equality, and returns zero after
  list exhaustion. Applying observed `0x10062001` to those comparisons remains
  conditional on the unproved loader-to-Dal mapping; the value and field are
  not semantically named (E-XE164-153/154).
- VERIFIZIERT (exact `0x10062001` provenance scope): the WP132 call lane loads
  its value from IoDrvDal data word Ghidra `0x1462c` at instruction
  `0x14460`. IoDrvDal has twelve exact raw-word occurrences and 30 direct
  materialized reader edges; exact `codesys3` has no raw occurrence and no
  bounded direct same-register MOVW/MOVT construction. This does not bind the
  indirect Dal target to `codesys3` `0x30066c` or name the value
  (E-XE164-158).
- VERIFIZIERT (bounded negative rootfs inventory): none of the eight exact
  selected comparison/Description ASCII strings occurs in any of the 3,058
  regular files in the exact FW31 rootfs partition. Dynamic/application input,
  other encodings and other storage scopes remain OFFEN (E-XE164-117).
- VERIFIZIERT (native-report scope): accepted Digital-8/16 trial artifacts do
  not record record-halfword values, a 16-byte parameter payload, named
  packbus operation calls/results or accessor activity. They do record the
  bounded own-provider signal/gate/fault/frame telemetry. Report silence is
  not runtime nonexecution evidence (E-XE164-120).
- VERIFIZIERT (two further accessor consumers): one record-validation lane
  calls the same config accessor object only after nonnegative-selector and
  record-halfword-5 guards, then combines callback nullness with its output
  slot. A separate selector-129..132 lane calls it under halfword-28/16 guards
  and dereferences returned `r0` for one 16-bit load. These are local static
  use forms, not a complete callback or record contract (E-XE164-121).
- VERIFIZIERT (bounded IoDrvDal resolver-to-call mechanics): in exact window
  `[0x2fa8,0x3018)`, `LibraryLoader_LoadSymbol` receives visible
  `r0=r7,r1=r10,r2=r5` and its return is zero-tested. Only on the zero lane is
  the later call target loaded separately from `[sp+0x70]`; the code supplies
  `r0=r4`, publishes `r7` at relative `+0x614`, then performs `blx r3`.
  Equality or causality between `r5`, the resolver return and `[sp+0x70]` is
  not established, so this is not a loader API contract (E-XE164-220).
- VERIFIZIERT (three exact unnamed-BSS positions, negative scope): ELF-VMAs
  `0x1a2a0/0x1a2ac/0x1a2b0` lie in IoDrvDal `.bss`; corrected REA Xref
  queries and exact raw-literal scans find no direct reference. This does not
  exclude computed pointers, aliases, external writes or runtime population
  and therefore does not identify or disprove a provider table
  (E-XE164-221).
- HYPOTHESE (resolver output-slot alias): the complete local body defines
  `r5=sp+0x70`, later supplies `r5` as resolver argument `r2`, and on the
  resolver's zero lane loads the dynamic call target from `[sp+0x70]`.
  Those pins are VERIFIZIERT, but the combined alias remains conditional on
  opaque intervening calls preserving `r5` and the stack basis
  (E-XE164-222).
- HYPOTHESE (resolver second-argument provenance): local arithmetic builds
  `r10=r4+0x512`, passes the current value as `r2` to an earlier indirect call,
  and later copies the then-current `r10` to resolver `r1`. The local pins are
  VERIFIZIERT; cross-call identity, buffer contents and whether the earlier
  callee populates the buffer remain OFFEN (E-XE164-223).
- VERIFIZIERT (WriteOutputs local provider-return handling): position `+0x30`
  nonzero takes an early local return `2`; position `+0x40` has its `r0`
  result immediately overwritten; position `+0x3c` replaces `r10`, and the
  last local `r10`-setting transfer is mapped zero/nonzero to return `0/2` at
  the sole epilogue. This is local register flow only; non-`r0` callee effects
  and numeric status meaning remain OFFEN (E-XE164-224).
- VERIFIZIERT (ReadInputs provider-position extraction): primary context
  `r9=*param_1` calls positions `+0x44`, `+0x54` and `+0x50`; a separate
  list-entry context calls `+0x58`. Locally, `+0x44` nonzero takes numeric `2`,
  `+0x54`'s `r0` is overwritten, `+0x58` combines result and local output word
  into a derived byte, and `+0x50` feeds the later last-status flow. The two
  contexts are not equated and no slot semantics are inferred (E-XE164-225).
- HYPOTHESE (minimal provider acceptance matrix): nine numerical call
  positions are now separately recorded with visible arguments and local
  reactions: `+0x0c/+0x10`, Write `+0x30/+0x3c/+0x40`, Read
  `+0x44/+0x50/+0x54`, and separate-context `+0x58`. Consumer-owned Dal
  stores at `context+0x618/+0x61c` are not provider requirements and are not
  proven to feed the Kbus contexts. This is not a full ABI (E-XE164-226).
- VERIFIZIERT (installed definition census): among all 3,058 regular files and
  803 ELFs in exact FW31 partition 2, `adi_GetApplicationInterface` has one
  Dynsym definition, in `/usr/lib/libdal.so.1.0.1` at ELF value `0x3464`, and
  two imports, in IoDrvDal and `dalshell`. Static definition does not prove
  runtime binding or function contract (E-XE164-227).
- VERIFIZIERT (exact interface getter body): the 16-byte libdal definition
  consists of three A32 instructions plus literal and returns ELF-relative
  address `0x14154`. That slot is `R_ARM_RELATIVE` with raw addend `0x1bec`;
  the getter returns the slot address, not its relocated content. Runtime bias,
  pointed-object contract and actual binding remain OFFEN (E-XE164-228).
- VERIFIZIERT (returned-object `+0x0c/+0x10` targets): exact relocation slots
  resolve statically to unnamed libdal entries `0x32bc` and `0x327c`; their
  complete observed Ghidra AddressSets contain local zero/`-1` gates and
  further bounded work. This binds implementation targets but still does not
  supply source-level names, prototypes or runtime binding (E-XE164-229).
- HYPOTHESE (conditional `+0x0c` positional contract): if the IoDrvDal getter
  returns the exact examined libdal object, its call arguments `10,r5,r8`
  enter target `0x32bc`. The complete observed local path stores a 32-bit
  return word through incoming `r2`, zero-tests it, and can write at most ten
  ordered pairs through incoming `r1`: a word loaded from `current+0x100`
  followed by `current`. Visible returns are `0` or `0xffffffff`. The target
  instructions are verified, but object identity, binding, callees, pointer
  validity and all semantic names remain OFFEN (E-XE164-230).
- HYPOTHESE (conditional `+0x10` positional contract): if the same runtime
  object binding holds, IoDrvDal supplies one locally known value, a 32-bit
  word loaded from `[r7]`; `r1/r2` remain unbound. Target `0x327c` passes that
  word to an opaque call, then forwards that call's separate nonnull result to
  secondary body `0x21d0` after a byte-at-`+0x170` zero gate. The complete
  observed body has nine stores and returns the then-current `r8` at both
  epilogues. Intervening opaque calls prevent a complete return contract or
  semantic field interpretation (E-XE164-231).
- VERIFIZIERT (local `+0x10` search/result gate): the directly called libdal
  helper copies the forwarded input word to a local stack slot. When a separate
  32-bit global value is nonzero, its address-form argument to the imported-name
  call points to that local copy. The returned `r0` reaches the caller's null
  test and, only when nonnull, supplies the base of byte read `+0x170`; nonzero
  byte rejects the path. Imported naming does not establish lookup semantics,
  table type or object meaning (E-XE164-242).
- VERIFIZIERT (local `+0x0c` gate source): the pre-tail helper returns one byte
  from memory-only ELF position `0x14208`. The caller falls through only when
  both saved input pointers are nonnull and that byte equals `1`. The package
  ends before the already separately evidenced pair-producer tail, and the
  byte's initialization/value/meaning remain OFFEN (E-XE164-243).
- VERIFIZIERT (method-bound direct references to that byte): Ghidra 12.1.4
  materializes five READ and two WRITE operand references to exact analysis
  address `0x24208`. The writer opcodes at `0x11d50` and `0x11e70` are concrete
  `strb` instructions and independently decode from the pinned ELF bytes.
  Ghidra did not expose the base-register memory-address derivation, so exact
  target binding remains reference-database-bound; stored values, lifecycle,
  aliases and semantics remain OFFEN (E-XE164-244).
- VERIFIZIERT (bounded byte values): in the two fixed writer windows, the
  reaching definitions supply constant byte `1` to `0x1d50` and constant byte
  `0` to `0x1e70`. This is static value flow, not observed execution. The
  first store's locally derived two-value gate remains HYPOTHESE; global
  target binding, lifecycle and meaning remain OFFEN (E-XE164-246).
- VERIFIZIERT (direct references to the adjacent word): Ghidra 12.1.4
  materializes 19 READ, two WRITE and 18 PARAM/OTHER references to exact
  analysis address `0x241e0`. Store `0x11df0` is independently target-bound by
  exact PC-plus-literal arithmetic; store `0x11c9c` remains target-bound only
  by Ghidra's WRITE reference because its base provenance is outside the
  allowed window. Values, lifecycle, aliases and semantics remain OFFEN
  (E-XE164-245).
- VERIFIZIERT (bounded word-writer value flow): `0x1c9c` stores the visible
  post-call `r0` without an intervening caller-window overwrite; this is not a
  return-value or ABI claim. Independently target-bound `0x1df0` stores zero
  only after the same base's byte `+0x28` and current word `+0` both test
  nonzero. Callee meaning and global lifecycle remain OFFEN (E-XE164-247).
- VERIFIZIERT (leading returned-object targets): exact returned-object data
  positions `+0` and `+4` contain target candidates ELF `0x1bec` and `0x1dc0`.
  Each target has only its data-cell Ghidra Xref, while a complete aligned
  file-backed A32 B/BL scan finds no direct branch to either entry. Indirect
  invocation, position names, signatures and lifecycle semantics remain OFFEN
  (E-XE164-228; E-XE164-248).
- VERIFIZIERT (bounded returned-object `+4` target mechanics): the complete
  target body first gates on byte `+0x28`; its active path conditionally
  zeroes four word positions before opaque calls, then zeroes word `+0x18` and
  byte `+0x28`. All visible exits set `r0=0`. This is a static state-transition
  description, not a named cleanup/lifecycle contract (E-XE164-249).
- VERIFIZIERT (bounded returned-object `+0` target mechanics): the complete
  body returns visible zero when byte `+0x28` is already nonzero. Its later
  independently rebound gate requires words `+0/+4/+0x18/+0x14` plus current
  `r0` nonzero, stores byte `1` at `+0x28`, and returns zero; bounded failure
  lanes return `-1`. Opaque call effects and intermediate addresses prevent a
  complete named startup/lifecycle contract (E-XE164-250).
- HYPOTHESE (minimum leading-position pair): because exact returned-object
  positions `+0/+4` target bounded bodies that establish complementary values
  `1/0` in the same gate byte, they form a lifecycle-like candidate phase
  pair. This may extend the virtual-provider boundary beyond positions
  `+0x0c/+0x10`, but it is not a verified requirement until the original
  indirect consumer and call order are bound (E-XE164-251).
- VERIFIZIERT (leading-pair documentation countercheck): R1–R5 of the
  seven-row synthesis are bounded by the supplied reports. R6 must retain the
  exact negative-scan limit: no aligned A32 B/BL target was found in
  file-backed `SHF_EXECINSTR` sections; indirect/computed calls and other
  encodings remain OFFEN. R7 was not independently reviewable because its
  E-XE164-237 report was not among this countercheck's hash-bound inputs. The
  lifecycle-like pair therefore remains HYPOTHESE (E-XE164-252).
- VERIFIZIERT (originalconsumer selector lanes): the published IoDrvDal
  dispatcher maps visible selector `2` to a fresh-getter chain that invokes
  post-getter positions `+0`, then conditionally `+8`, then conditionally
  `+0x0c`. Selector `15` maps through a distinct table cell to a fresh
  getter followed by position `+4`, after which the local lane ignores
  visible post-call `r0` and branches to the common destination
  (E-XE164-253..255).
- HYPOTHESE (exact-libdal leading-position consumer join): exact libdal is the
  sole installed static getter-export candidate and exposes first cells
  `+0/+4`; if runtime binding and the visible `r0` object match that
  candidate, IoDrvDal selectors `2/15` invoke those two positions. They are
  separate dispatcher cases, so no temporal order, mandatory execution or
  init/exit meaning follows (E-XE164-256).
- VERIFIZIERT (complete manager callback inventories): exact
  `CMInitComponent [0x301394,0x3018b8)` has eight indirect sites reached by
  ten input-object `+0x20` loads, with visible local `r0` values
  `2,3,7,4,500,5,6,1000`. Exact `CMExitComponent [0x300b10,0x300e38)` has six
  sites reached by seven such loads, with visible constants
  `10,11,2200,12,13,14`; no immediate `15` reaches those six sites. These are
  bounded static register forms, not selector meanings or executed order
  (E-XE164-257; E-XE164-258).
- HYPOTHESE (asymmetric manager support): under the conditional registered
  block `+0x20` to IoDrvDal-dispatcher binding, the init body's visible `2`
  reaches the getter-followed provider `+0` lane. The exit body does not
  establish the selector-`15` provider `+4` lane. This weakens a simple
  init/exit naming for the leading pair without excluding another consumer,
  a computed value or a runtime sequence (E-XE164-259).
- OFFEN (whole-text selector-15 consumer search): corrected middle/high
  inventories contain 23 and eight direct-CFG `+0x20`-target chains with no
  visible constant-15 match. The low partition's direct-edge scan also finds
  no match, but 101 indexed PC dispatches in 222 load-bearing symbol marks
  remain unresolved; several accepted calls use entry/register/memory-derived
  `r0`. Therefore no other selector-15 consumer is established or globally
  excluded. Provider `+4` remains a prioritized candidate, not a mandatory
  exit contract (E-XE164-260; E-XE164-261; E-XE164-262; E-XE164-263;
  E-XE164-264; E-XE164-265).
- VERIFIZIERT (static ELF candidate chain): exact IoDrvDal directly needs
  SONAME `libdal.so`; its unversioned undefined getter symbol is carried by one
  `R_ARM_JUMP_SLOT`, while exact libdal declares that SONAME and exports the
  matching unversioned function name. This makes exact libdal a direct static
  dependency/export candidate for E-XE164-230/231, but does not observe the
  loaded path, lookup order, interposition or relocated GOT value
  (E-XE164-232).
- VERIFIZIERT (installed candidate path): in the complete exact partition-2
  census, `/usr/lib/libdal.so` resolves by relative symlink to the hash-bound
  `/usr/lib/libdal.so.1.0.1`, and that file is the sole defined Dynsym
  candidate for the getter name; the only other two rows are undefined
  imports. This closes installed-image candidate identity, not runtime loading
  or interposition (E-XE164-233).
- HYPOTHESE (cross-position entry chain): the exact IoDrvDal window locally
  passes `r5` to `+0x0c`, then scans from the then-current `r5` through `r7`
  in 8-byte steps. Each body compares the `+4` word; on equality it stores the
  `+0` word and, after another getter call, reloads that `+0` word as the
  `+0x10` call's `r0`. The addresses and arithmetic are verified, but no
  register or memory preservation across the opaque calls is bound, so the
  end-to-end value chain remains conditional (E-XE164-234).
- HYPOTHESE (first-entry base preservation): conditional target `0x32bc`
  visibly pushes and later pops physical `r5` on its local entry/error/tail and
  secondary return paths. After its zero return, IoDrvDal has no further call
  between `r7=r5`, the initial bound test and first `[r7+4]` load. This
  strengthens the first-entry address chain, but opaque calls can still affect
  saved stack words/control flow and no calling convention is asserted
  (E-XE164-235).
- HYPOTHESE (matched-word getter gap): between the matched entry's first
  `[r7]` load/store and its reload as `+0x10` argument, the conditionally
  already-resolved exact PLT/getter path contains no `r7` write and no store.
  Exact ELF metadata now shows that the file does not mandate eager binding:
  the getter `R_ARM_JUMP_SLOT` remains outside `PT_GNU_RELRO` and no NOW
  tag/flag is present. A first lazy route is therefore statically permitted,
  and its local getter-stub/PLT0 portion has no visible `r7` write. PLT0 does
  store incoming `lr` at `[sp_in-4]` before transferring to the still
  unexamined dynamic loader. Caller store `[r4+0x618]` may also overlap `[r7]`.
  Address preservation is consequently still stronger than word-value
  equality (E-XE164-236/239/241).
- HYPOTHESE (minimum two-position provider contract): conditional `+0x0c`
  produces one separate word plus at most ten positional two-word entries;
  IoDrvDal compares each entry's second word and, on a zero comparison result,
  passes its first word to conditional `+0x10`. This nine-row synthesis is the
  smallest currently evidenced implementation shape, not an ABI, named
  structure, runtime binding or complete lifecycle contract (E-XE164-237).
- VERIFIZIERT (text-only matrix audit): a separate Luna HIGH package checked
  R1–R9 against their cited E-XE164-230..236 claims and found every row bounded
  with material conditions retained. This supports documentation consistency
  only and does not promote the HYPOTHESE contract or qualify runtime/hardware
  (E-XE164-238).
- VERIFIZIERT (getter binding mode encoded by IoDrvDal): the exact ELF has one
  unversioned getter `R_ARM_JUMP_SLOT` at GOT VA `0x16030`, no dynamic NOW
  tag/flag, and a `PT_GNU_RELRO` range ending at `0x16000`. Thus IoDrvDal does
  not itself require eager binding and a first lazy-resolution route remains
  statically permitted. Loader environment/state, resolver effects and actual
  runtime binding remain OFFEN/NOT_RUN (E-XE164-239).
- OFFEN (store/scan alias): both direct loader callers can expose the same
  PC-relative input expression `0x163d8` (caller 2 only if its excluded loop
  continuation preserves `r7`). The loader derives `r4` from that input and an
  index, whereas the visible scan base begins as `sp+0x70`. Opaque calls and
  the absent runtime relation between stack and PC-relative expressions mean
  that `[r4+0x618]` and `[r7]` are neither proven equal nor disjoint. This
  blocks word-value equality independently of the lazy-resolver gap
  (E-XE164-240).
- VERIFIZIERT (local lazy trampoline writes): under the exact on-disk getter
  GOT word, the getter stub and PLT0 write no `r7`. PLT0 does update `sp/lr/pc`
  and stores one word at `[sp_in-4]`; the target reached through `0x16008` and
  all subsequent dynamic-loader effects remain OFFEN/NOT_RUN (E-XE164-241).

- VERIFIZIERT (E-XE164-266, local dispatch mechanics only): WP240 resolves 34 assigned comparison/table mappings and all 593 case words. The limited simple-immediate MOV text scan finds no literal r0=15 in its eleven parser-bound marker intervals. The requested combined +0x20/r0=15/BLX path stays OFFEN, including computed/other-form r0 and opaque-call effects. No lifecycle meaning or mandatory provider +4 follows.

- VERIFIZIERT (E-XE164-267, bounded local mechanics): 19 SCANNED dispatch rows in 14 unique REA bodies, four not_in_procedure gaps, and zero candidates under the declared bounded constant/load/BLX scan; mov/movw immediate-15 scan also has zero hits. Calls invalidate all general registers. Four absent REA bodies do not block raw-table validation or independent offline work. Full CFG, static arithmetic/other-form r0, incoming/memory values, aliases and opaque-call effects remain OFFEN. No mandatory provider +4/Exit contract follows; runtime/hardware NOT_RUN.

- VERIFIZIERT (E-XE164-268, bounded local mechanics): Seven parser-bound intervals contain three simple-MOV15 sites: two immediately changed by MOVT to 0x1000f before direct calls, one conditional return lane. Four byte-bound local BLX lanes reached through two tables reload their targets from current r4+0x24 and r0 from other fields; the prior +0x20 load supplies the dispatch index. The three-site audit and same-segment screen are method-bounded; 42 downstream table/value paths are not closed. Even the two additional lane reviews do not close runtime or interprocedural paths; computed/incoming/memory r0 remains OFFEN. No mandatory provider +4/Exit contract follows; runtime/hardware NOT_RUN.

- 2026-10-18 synthesis (E-XE164-266..268): all 101 assigned local CMP/LS tables / 1,541 case words are now byte-bound. This closes that raw-table inventory gap only. No accepted new chain supplies both a +0x20-loaded BLX target and visible r0=15 at the same call; its global absence is also not established. Provider +4 remains an optional prioritized candidate, without Exit naming/requirement.

- VERIFIZIERT E-XE164-269: a registered-hook helper uses an indirect BX tail, loading its target from input+0x20 and forwarding inputr1 as r0. Earlier BLX-only censuses did not cover this form. Forwarded15 passes its local numeric gate for halfword2/4/5, but actual external caller15 and runtime/object binding remain OFFEN. The pointer-offset-mismatch hypothesis is refuted; the missing transfer class is BX, not a different helper load displacement.

- OFFEN E-XE164-270: Four former not_in_procedure intervals now have a bounded raw graph with 3281 listed A32 word nodes / 3696 edges, four closed indexed tables, 111 register transfers (all BLX; zero BX), 36 literal-displacement +0x20 loads and 173 PC/indirect-transfer records. Thirteen load-to-BLX connections have local callfree address witnesses, zero remaining abstract-only matches; relevant r0 values remain computed/incoming/memory/opaque unknown. 602 explicit method/control/effect gaps; predicate feasibility and memory aliases unresolved. Marker word starts are not code/function ownership. No proven15 in this limited model does not exclude15. No new selector15 original-manager invocation follows.

- OFFEN E-XE164-271: Exact [0x154dc4,0x1630bc) has 27 inherited indexed tables plus two newly byte-bound local CMP/LDRLS tables at0x1619a0 and0x162f0c, adding17+8 case words. Total402 case words and24 direct literal words are excluded from the code graph. The graph has14100 nodes /15315 edges, 30 BLX/BX transfer rows and zero modeled exact +0x20-load target witnesses. 138 explicit gaps including15 unowned islands,116 widening states,4 unmapped direct branches,3 unresolved BX destinations,2 unsupported vector writes. Zero modeled witnesses under these limits is not a global absence or inequality15. No new selector15 original-manager invocation follows.

- E-XE164-272 OFFEN: Exact [0x1630bc,0x180000) bounded graph consumes17 tables/266 words and accounts for60 BLX with local abstract states,84 +0x20 loads,34181 edges and3754 gaps. No register-only load-to-BLX witness or modeled r0=15 token is found; the sole literal MOVLE15 at0x176e58 follows its same-condition BLE into an LDM/PC epilogue. Unproved code ownership, spill/reload/memory aliases, unsupported PC paths and unmodeled effects remain open. Node/constant categories describe a bounded model, not runtime or whole-program absence.

- E-XE164-273 VERIFIZIERT: Complete declared aligned-A32 B/BL scan finds23 direct BL sites to CMCallHook plus2 to CMCallHook2. In fixed96-byte-before/20-byte-end caller windows,18 Hook selectors and2 Hook2 selectors are other constants under that local model;5 Hook selectors remain unknown. Exact312-byte CMCallHook2 body forwards its entry r1 as helper entryr1, the selector position of E269. Five true unknown selectors come from table/memory, entry and opaque values; no locally proven15 does not exclude15. Raw census omits Thumb/indirect routes and runtime. Extra Xref is untyped within WP247; accepted E160 independently binds publication of the same target at local+0x24.

- E-XE164-274 VERIFIZIERT: Independent Luna HIGH nine-row countercheck accepts bounded WP246 H1-H5/C1-C3 and retains J1 as HYPOTHESE. An independently derived unsigned Boolean gate accepts halfwords2/4/5 (forwarded20 only5); exact inputr1->tailr0 /+0x20->BX and three local argument windows match. The71-address candidate caller path is compatible with original incomingr2=0, so both predicated r9 pointee accesses skip. This checks static evidence consistency/conditional path compatibility only. J1 remains HYPOTHESE; actual memory/list/object validity, selector15 invocation, runtime/hardware remain OFFEN/NOT_RUN.

- E-XE164-275 VERIFIZIERT: Exact IoDrvDal ComponentEntry input+0x24 is loaded at ELF0x4508 and stored unchanged at0x450c to BSS0x163b8 (Ghidra0x263b8). The exact Ghidra direct-reference inventory contains only this WRITE; the adjacent BLX0x452c instead uses input+0x28 and locally supplies0x10062001. No direct hook consumer established; computed aliases/external/runtime consumption and actual published service identity remain OFFEN.

- E-XE164-276 VERIFIZIERT: Freshly rehashed40 installed ComponentEntry DSOs; Dal metadata-only and39 others interpreted. Their1572120 file-backed executable bytes in156 sections contain28 aligned A32 MOV-immediate15 writes to r0/r1 in5 DSOs and zero MOVW hits. All28 fixed windows decode at the word; this is syntax triage only. Thumb/computed/loaded values, code ownership/reachability, propagation, ABI/API and selector meaning remain OFFEN; no-hit does not establish semantic absence.

- E-XE164-277 VERIFIZIERT: Exact source table [0x3a30c0,0x3a31d0) contains34 stride8 numeric pairs, with firstword15 uniquely at index20/VA0x3a3160. Raw aligned A32 caller counts are2 to helper,3 to CMInitSequence,4 to CMExitSequence; REA Xrefs agree. Exact caller0x300f3c selects row16/count2 (12,13), excluding next14. Row20 membership does not prove15 delivery across opaque formatter/state effects. No ABI/runtime or mandatory provider+4 claim.

- E-XE164-278 VERIFIZIERT: Four exact bodies bind632 instruction words/2528bytes. The formerly window-unknown Hook site0x2ff368 receives20 on its sole local predecessor path;0x2ff6d4 likewise locally supplies20. Site0x2ff588 has20 only before an opaque call;0x2ff76c reloads unknown post-call memory. The exact subtract15/clear-bit1 gate accepts precisely15 or17. Post-opaque r8/r4/memory and CMExit table association remain conditional; direct-body predecessors do not exclude external interior entry. Runtime NOT_RUN.

- E-XE164-279 VERIFIZIERT: Exact84/120-byte formatting wrappers contain51 words, plus3 PLT words=54 total. Source relocation binds PLT0x7b5dc to undefined vsnprintf@GLIBC_2.4 from libc.so.6. Local stack/forwarding and post-import byte-store/result predicates are explicit, including conditional local result15. Import implementation/stack/register/buffer effects remain OFFEN. Formatter return15 is not a Hook selector. No ABI/runtime claim.

- E-XE164-280 VERIFIZIERT: Exact152/120-byte pool bodies bind68 words. Local GetBlock arithmetic forms payload P=N+16 and stores manager M at N+4; Append computes N=P-16 and reloads M at P-12=N+4. Its post-call head/tail slots are M+0x1c/+0x20. Numeric positions agree conditionally with registration copy and callback head+16. Same manager/node, memory lifetime, opaque lock/clear/unlock effects and actual registered callback remain HYPOTHESE/OFFEN. No invented schema/API semantics.

- E-XE164-281 HYPOTHESE: Conditional static entryvector CMCallHook(15,0,0,0) reaches helper call0x2fedd4 in68 callfree instruction addresses with args(firstHead+16,15,0,0), skipping optional BLX iff slot0x5fc5b0 is null. It never reads firstHead.next before this call. Under halfword2/4/5 and nonnull target, helper BX forwards(15,0,0). All global/slot/head/object/target/stack validity and noninterference predicates are assumptions. Table-to-entry delivery, runtime binding/order and mandatory provider+4 remain OFFEN/NOT_RUN.

- E-XE164-282 VERIFIZIERT: Exact71 sourcewords in CMGetHookName/CMGetHookEntries bind34-row table lookup and stop-exclusive ranges. Selector15 index20 secondword0x3a5830 points to exact terminated ASCII CH_EXIT_SYSTEM; selector17 maps CH_EXIT_SYSTEM2. Rangeexamples17..16->row19/count2,12..14->row16/count2,2..2->row2/count1,10..12->row13/count3. Binary-authored labels identify emitted names only; mandatory lifecycle/ABI/order/runtime binding remain OFFEN.

- E-XE164-283 VERIFIZIERT: Independent root raw-A32 subset mathematical replay reproduces all68 WP255 calleraddresses thenhelper through encoded stackrestore/BX, obtaining(15,0,0,target) at admittedhalfwords2/4/5. Threepositive andeightnegative syntheticcontrols pass, including invalidglobal/nullhead/nonnulloptionalslot/pathdivergence and nulltarget/invalidhalfword return1. No head-nextword read occurs. Syntheticmemoryfixtures are not observedlayout. Actualglobal/stack/head/target validity, aliasnoninterference, invocation andruntimebinding remain HYPOTHESE/OFFEN.

- E-XE164-284 VERIFIZIERT: Original Dal selector17 reaches default and selector15 returns from getter/+4 lane to same default; default sets r4=0. Common postlude returns0 without further calls when localglobalword+12 is nonzero, or when thatword and countword+16 are bothzero. Positivecount may invoke further indirectcallbacks and gives no unconditionalresult. Getter/target/object/runtimebinding and stackvalidity remainconditional; positivecount effects unresolved. Discarding +4 postcallr0 locally is not an unconditional routine result.

- E-XE164-285 HYPOTHESE: Corrected source-bound scan at301058 selects rows19(17)/20(15), excludesrow21(16), and passes(pointer3a3158,count2,0,0). Under explicit live-state/memory/return predicates, secondHook vector is(15,0,0,0). Completeeight-row argumenttable andthreeeffectivevectors now checked ratherthanpartial/tautologicalassertion. Timeimport and firstHook effects/live-state preservation, priorCMExit joins and actualtable/runtime/objectbinding remainassumptions. No globalexclusion fromselectedretrycontrol.

- E-XE164-286 VERIFIZIERT: At currentlocalframeF afterMainLoad, B=F-88 and callfreeinitSTRH2 writesB+44. HelperSTRH3 predicate is post-BLXr0!=r6, targetcurrentr4+44; entryBtargetrequirescurrentr4=B. Latecallerwordstores usecurrentr5; originalentryr3identityrequirespreservation. Any4bytestoreA overlapsB+44..45 iffA inB+41..45. Immediate2doesnotprove latergatevalue. Allopaqueeffects, frame/registeridentity acrosscalls, copy-source/payload/node/manageridentity, memory/stackvalidity andretention remainHYPOTHESE/OFFEN.

- E-XE164-287 VERIFIZIERT: Exact FW31 image interpreter path /lib/ld-linux-armhf.so.3 resolves through image /lib symlink to regular inode1396,175592B, SHA366d9f2f5584ce374cb1a7a2222067d0c99aabee4bac6a475c160ce04ed4dd33. Loader ELF32 ARM ET_DYN hardfloat metadata has42 declaredDynsym entries and no declared _dl_runtime_resolve/_dl_fixup names. Missingdeclarednames do not prove codeabsence. No resolver address/body/effects or runtime lookup/interposition verified; privatevendorfile notpublished.

- E-XE164-288 VERIFIZIERT: A closed synthetic selector17 instance traverses the exact core prefix/helper, the original Dal default path and core postlude, returning0 to2ff770 for halfwords2/4/5. Actualencoded push/pop restores callerliveGP/SP; ownDal argumentstores lie below savedregisters. Singlehead.next0 and Dalno-callbackglobalconditions are explicit. This proves a conditionalinstance of firstHookreturn, not actualmanagerlist/targetbinding, loadbias, memoryvalidity orruntime; nopreservation inferredfromABI.

- E-XE164-289 VERIFIZIERT: Exactinstalledlibcds3sys.so160364B SHA32e41d8e8132dfe4ebda603a6a273252e7dd04e83807aea0083d2045d13f8959 exportsoneSysTimeGetMs at e87c/72B. It passes1 andan8bytestackbuffer to clock_gettime@GLIBC_2.17; postcall current-framewords feed low32(1000*word0+signedreciprocal(word1)). Importstatusr0isnotchecked. Millisecond/clockdomain meaning needs actualoutputcontract; postcallframeidentity/stack/importeffects and actualproviderbinding remainOFFEN. No monotonicityfromID1alone.

- E-XE164-290 VERIFIZIERT: Provider+4 exact57wordbody eightdirectcalls bind sixPLTimportidentities: g_hash_table_destroy,LibraryLoader_Destroy,fileno,flock,fclose,free. Soleinternal3c34body76B clearsinputbyte+12 beforethreeopaque calls andtailB tofree. Four initialwordslots clearedbeforetheircallboundaries. Namesidentifyrequests, not runtimeimplementations/effects. r0afterfileno,currentr4/r6aftercalls andtailBreturneffects remainunbound. No foreigncallee expansion.

- E-XE164-291 VERIFIZIERT: Initialtimecallreturns toHooksetupdirectly via2ff750->2ff75c. OnlyafterHookr0=10 doeszero-baseline test2ff754 occur; baseline r6=0 canrepeatwithoutanother sample under explicitcall/statepreservation. Nonzero baseline unsigneddelta<=9999 retries,10000takesotheredge; separateBCS thresholdis>=32000;32bitwrapcasesPASS. Conditionalcycleisnotobservedruntimehang. Literal10 hasnoinventedstatusmeaning; clockunits/domain andopaquecallreturn/live/frameeffects remainOFFEN.

- E-XE164-292 HYPOTHESE: Reviewed originalstack selector15 chain: originalnameCH_EXIT_SYSTEM, conditionalCMExit17/15slice->Hook15->registeredcallbackBX->IoDrvDalgetter/+4->soleinstalledlibdalcandidate. Within that localDal15path, +4 is anunguardedcall-targetprecondition; universalmandatorylifecycle/ABI isnotproved. Combinedruntime/object/lookup/relocation/stateidentity, actualinvocation/order andcompleteABI remainHYPOTHESE/OFFEN; source labelsdonotproveuniversalsequence. Canonicalreviewedtext is work/root/continuation-2026-10-18-0858/selector15-synthesis-reviewed.md.

- E-XE164-293 VERIFIZIERT: The full476-byte ComponentEntry and84-byte pool bind the 136-byte call vector and all later stores. Its candidate destination is DalBias+1a270. The post-call vector begins at D+78 only when current r6 before ADD45c4 equals DalBias+1a2c4; scalar stores separately require current r5=DalBias+193c4. No local store is present at D+90 under that baseline. Copy effects, actual GOT target, relocation/load biases, memory/alias safety and runtime instance remain OFFEN. Source vector/address arithmetic does not infer semantics from memcpy name.

- E-XE164-294 VERIFIZIERT: Under a stipulated directly-resolved Dal GOT16030 pointing to the exact libdal getter, PLT/getter instructions return ProviderBias+14154 while preserving r5/r6/r7/d8/d9/SP by explicit operands. Caller45b8 updates r6 before the next call. Three source positions +30/+3c/+40 have unique R_ARM_RELATIVE addends2f98/2e5c/2e04 and file-backed executable target metadata. The exact route excludes lazy resolver and alternate GOT targets. It does not establish actual binding, table/API meaning or copy implementation; runtime NOT_RUN.

- E-XE164-295 HYPOTHESE: If the exact136-byte copy occurs from the relocated getter object to D=DalBias+1a270, and the separate current-r5/current-r6 premises hold, all10 subsequent local stores leave D+30..33,D+3c..3f,D+40..43 untouched. Conditional words are ProviderBias+2f98,+2e5c,+2e04. Changed-r6 vector and changed-r5 scalar counterexamples invalidate unconditional preservation. Copy implementation/preservation and memory conditions are explicit premises. Identity with IoDrvKbus context+61c, runtime publication and original API semantics remain OFFEN; no caller body reopened.

- E-XE164-296 VERIFIZIERT: Three complete provider candidate bodies at2f98/88B,2e5c/164B,2e04/88B have85 source-bound words. Each tests three helper results individually, returning ffffffff onzero. Simple candidates null-check slots at current third-return+2c/+30 before tailBX. Sized candidate null-checks +20, then requires unsignedmax(currentr5,currentr6)<=wrapped_sum and word[current_return+8]>=sum; currentr7 is forwarded to tailr2 only after that gate. Current values after opaque calls remain unknown. Relocation/copy/object/runtime identity and API meanings remain OFFEN.

- E-XE164-297 VERIFIZIERT: Exact helper2180 reads globalbyte ProviderBias+14208, ignores inputr0 and preserves r4-r7/SP/LR locally. Helpers2194/1ecc pass word[ProviderBias+141e0] and address of stack-saved key to PLT15f4. First returns byte[nonzero_nested_return+170]; second conditionally returns wrapped nested_return+110. Distinct nested results and r4/key retention are not equated. PLT symbol g_hash_table_lookup is metadata, not implementation/effect proof. Frames/readability/opaque preservation and complete success contract remain OFFEN.

- E-XE164-298 VERIFIZIERT: Exact FW31 installed libc.so.6 inode1548 was read-only extracted:1434296B SHAdc47ee066e2c2d73ff9186440787543c3020711611f09002b6ab187d97d9dfa2. Unique memcpy Dynsym2313 is GLOBAL/FUNC ELF919c0 size1248 versionGLIBC_2.4; exact contiguous Ghidra body and complete function evidence retained. Installed candidate metadata does not prove runtime winner or copy effects. Exact136-byte lane analysis is WP279; runtime NOT_RUN.

- E-XE164-299 VERIFIZIERT: Exact image installs one SONAME-family regular GLib candidate libglib-2.0.so.0.8200.2 inode1706,1199352B SHA3f927b8aae0e3e1b1296bde9009ba9fb9380f64ac26ebe8b7675638e3250cbc5, withtwo aliases. libdal needs libglib-2.0.so.0 and imports unversioned g_hash_table_lookup at GOT140ec; candidate exports exactname index944 ELF45d6c declared328B. Actual REA reports contiguous316B body plusunclassifiedsymboltail. Uniqueinstalled SONAMEfamily is not runtimewinner. Implementationbody is separatelyWP283; no functioneffect inferred from name.

- E-XE164-300 HYPOTHESE: For each of the threewrite-side candidates, readable globalbyte ProviderBias+14208=0 causes its first direct2180leaf toreturn0, thenlocalCMP/BEQ/MVN/POP returns ffffffff without2194/1ecc calls. Leafhasnostore/nestedcall and doesnotwriter4-r7/SP/LR. Byte1passesfirstgate andreaches nextdirectcall only. Readable sourcebyte mustnotaliassavedframewrites; valid8B/24Bframes/savedreturnandlargecandidateentrystackword required. Runtimebyte,providerbinding/objectidentity andlatercallbackeffects remainOFFEN.

- E-XE164-301 VERIFIZIERT: Corrected source-driven136-byte memcpy lane steps48 PCs over312boundwords: four32-byte source loads/four32-byte destination stores,8-byte tail and4-byte stack save/restore. Exactcarry branches and sixPLDhints include S+140. Immutable entry snapshots prove advertised GP/d8/d9 retention; injectedr5clobber control is rejected. Onlypagealigned assignedsource/destination offsets andnonwrapping,nonoverlapping,readable/writable,validstack/return,NEONsupported syntheticconditions. RuntimeGOT/provideridentity,concurrency/fault/cacheeffects remainOFFEN.

- E-XE164-302 VERIFIZIERT: Read-side getterpositions+44/+50/+54 bind three uniqueR_ARM_RELATIVE cells to2dac/88B,2c70/164B,2c18/88B. All85 sourcewords arechecked. Threehelperzero-gates returnffffffff; simplecallbackslots currentthirdreturn+24/+28 nullreturn1. Sizedcandidate firsttests callback+18 thenlength+4, with unsignedmax(currentr5,currentr6)<=wrapped_sum andlength>=sum; r7onlyforwardedafterpass. Helper/context/callbackeffects andactualruntimebinding/tablepublication remainOFFEN. Separatelist-entrycontext+58 isnotjoinedtogetterobject+58. Earlybyte0firstgatefollowsaccepted2180leafonlywithvalidframe/readability/nonalias conditions; noAPItypes/ABI inferred.

- E-XE164-303 VERIFIZIERT: Corrected GLib lookupbody79words/316B plus12Bliterals: initial-empty Ghidra55dc4 branchesdirect55e54 MOVr0=0 thenPOP, independentofcurrentr7/r8. Laterprobeempty55dfc->55e4c does testr7 andmayuse rememberedr8/status. Nulltablewarning andopaquehelper/callbackeffects remainqualified; saved40Bframe canrestoreGP/SP onlyif framebase/bytesretained. Runtimebinding/tablecontents andopaqueeffects remainOFFEN; nameg_hash_table_lookup notanAPI/ABIcontract. Original283frozenforaudit; address-table labelwarning_call_target forfirstarithmetictarget issemanticwordingonly, canonicalscopeusesnumericinternaltarget.

- E-XE164-304 VERIFIZIERT: Actual independent Luna review supports corrected28248-PCcopy136B source-model: raw312wordinventory,32/8BNEONpostindex,carrybranches,PC+8tail,source/destination/stackaccessorder,all6PLDhintsincludingS+140. Immutableentrysnapshots andmutationcontrolsforallclaimedpreservedGP/d8/d9 independentlychecked. Sameconditionalmappedranges/nonalias/NEONsupport/validreturn requirements asE301. Faults,concurrency/cache/prefetcheffects andactualruntimewinner remainOFFEN.

- E-XE164-305 VERIFIZIERT: Own C byte-range predicate a<=C and b<=C-a is mathematically equivalent to original sized-provider unsignedmax(a,b)<=u32(a+b) andC>=sum underexplicituint32 operandidentity. Owntransaction/readiness/fault behavior andoriginalhelper/nullcallback gates areseparatefacts. Existing ownsourceassertions enumerated; noheader/buildoffsetmapping ornumericmacrovalues invented. Operand/field/slotidentity remainsHYPOTHESE/OFFEN; mathagreement neither provescompatibility norrequiresreplicating originalinternals. Projecttests/build/runtimeNOT_RUN; publicrepo unchanged.

- E-XE164-306 VERIFIZIERT: Separate-context+58 candidate sourcecell141ac hasunique symbol0R_ARM_RELATIVE addend2ba8. Complete112B/28wordbody tests3helpers forzero=>ffffffff, thennullcurrent_return+3ccallback=>1, else tailBX withcurrentr5/r7/r6->r0/r1/r2. Conditionaloldconsumerinputs0,0,stackoutword maptotail0,0,outword onlyiflivevaluesretained. Separate listentrycontext not equated to primary/getterobject. Actualtarget/callbackidentity andoutputwordeffects remainOFFEN; noAPI/ABI inferred; runtimeNOT_RUN.

- E-XE164-307 VERIFIZIERT: Closed conditionalComponentEntry instance steps174PCs:117Dal+6PLT+3getter+48libccopy. Two distinct pagealignedbias fixtures withoptionalentry+28NULL, exactGOTtargets and7validglobaldatacells returnr0=0 viaencoded72Bframe/epilogue. All34providerRRELwords copied136B beforepoststores;60Bentrystage,vectorD+78 andsixcycliccells traced; exactSP/GP/d8/d9effects recorded. Fixturemapping/GOT/relocation/globaldata/optionalcallbackstate stipulated, notruntimeobserved. SourceandDtableleadingcellsdifferafteroverrides; noAPI/ABI/fullobjectidentity inferred.

- E-XE164-308 VERIFIZIERT: Actual independentLuna review supportsfull286174PCcomposition, cross-DSOBXnextPCtranslation, all34RRELcells, 60Bstage, sixfinalcells, entrysideeffects, eightbytealignment andstack/registerconditions. Reusespinnedstepper asgeneratorbutseparatelyderives sourcebranch/GOT/ELF/bias/spanoracles. SameexplicitfixturepremisesasE307; actualruntimeimportwinner/state, faults/cache/concurrency remainOFFEN. Independenceofreviewisnotindependentnativeexecution.

- E-XE164-309 HYPOTHESE: Reviewed nine-positionmatrix restores sourcefacts fororiginalgetterO+0c/+10 andsixcyclic/separatelistcontext58, withcorrectcallerreportsWP198/199 anduniqueheader. O=ProviderBias+14154 isdistinctfromconditionalcopyD=DalBias+1a270; laterD+0/+4 targetDalBias+209c andD+10/+14/+6c targetDalBias+20c8; thoseoverridesdonotchangeoriginalO. Numericmatrix isimplementationhypothesisonly. Runtimeprovider/object/contextidentity, completeeffects/API/ABI andbroaderprofiles remainOFFEN. Sourcebody/callerfacts do notmakeeveryinternalgate a replacementrequirement. Canonicalmatrix work/root/continuation-2026-10-18-0858/nine-position-matrix-reviewed.tsv.

- E-XE164-310 HYPOTHESE: Closed conditionalSelector15 instance reachesr0=0 atCore2ff770 forhalfwords2/4/5 throughhelperBX,Dal15,resolvedgetter andoriginalprovider+4bytezero leaf,thenDal/Coreencodedepilogues. Explicitinitialmanagerglobal/readability,exactGOT/RREL/nonalias/stack/Dalno-callbackpredicates required. Noactualruntimewinner/tableidentity/mandatorylifecycle/ABI claim; byte1 firstopaque call liesoutsideclosedresult.

- E-XE164-311 VERIFIZIERT: Actualindependentreview source-derivesleafr2=0,r3=P+141e0,PLTwritebackr12=G+16030,commonGP/SP/r0summary andconcretecorepostludeboundary. Actualboundaryplus12explicitvariations return0; wrongGOT/+4cellcontents followcounterfactualpointertransfers ratherthanscalarinequalitychecks. Twelve finitevariants arecontrolsonly; nopreciseuniversalcallpreservation inferred. Runtime/GOT/alias/frameconditions stillstipulated.

- E-XE164-312 VERIFIZIERT: Exact GLib integer callbacks comprise hash4756c/8B reading one word and equality47554/24B returning1 iff two readable32bit words equal. Helperbac64/32B returns saved_r0-saved_r1*nested_r0 in r1 on nonzero input. Nestedbaa78/492B has123 audited words; only divisor1 SUBS/BXEQ route is closed with GP/SP/LR retention. General nonzero computed-PC control closure and whole-call preservation remain OFFEN. No API/ABI, general quotient semantics, live callback binding or constructor field identity. Conditional libdal1c80/1c88 args require currentr6=14000 across opaque calls.

- E-XE164-313 VERIFIZIERT: Exact libdal1a3c/296B conditional candidate path explicitly stores7c8 at currentr5+110, currentr8 at+100/+11c, currentr9 at+104 and two opaque returns at+108/+10c. PC-relative literals derive global141e0 at two sites. Insertcall1b4c->PLT1414 locally supplies r0=[currentr6],r1=currentr5+100,r2=currentr5,r3=latest188creturn. Counter arithmetic wraps32bit; finite termination not proved. Opaque calls do not establish allocation/zeroing/registration/strcat effects or register retention.7c8 is a data word, not an executable callback. Runtime table/record identity and actual memory remain OFFEN.

- E-XE164-314 VERIFIZIERT: Source-local224c->PLT13f0/GOT14040 names LibraryLoader_LoadSymbol with r0=[currentr6+104],r1=currentr4,r2=currentfp-32. If local return!=-1,226c BLX uses loaded[currentfp-32],r0=currentr6+110 as an ADDRESS,r1=ProviderBias+141e8. Returnzero writes byte[currentr6+170]=1, nonzero0. Raw suffix3d40 is exact _open NUL; fullsymbol remains conditional. Later+158 is a distinct nullchecked callback. No opaque strlen/strcat/LibraryOpen/LoadSymbol effects or GP/frame preservation inferred. No complete symbol string, backend target, actual outputword initialization, callback population, ABI or runtime binding proved.

- E-XE164-315 VERIFIZIERT: Actual independent Luna302 finds original300 stepper misassigns55e60 as r11shift and55e64 as bucketload, omitting actualCMP flags. Raw55e60 is LDRr3,[r2,r11],55e64 CMPr3,1,55e68 BLS. Two fixed positive results remain T but intermediate fullstep claim is rejected. Arithmetic-only snapshot/frame assertions are tautologies; original300 frozen, corrective306 separate. Independent static review is not ELF execution. Divisor1 fixtures are stipulated; constructor reachability, actual binding and general semantics remain OFFEN.

- E-XE164-316 VERIFIZIERT: Exact constructorELF4584c/120B stores currentr5/currentr7 at currentr4+24/+28, after capturing entryr0/r1 before opaque calls. Exact initializer44fb4/84B writes+0=8,+4=7,+8=7 and byte+14lowbits3 before its first opaque call. Later allocator-named returns stored+18/+20 and+1c; effects remain opaque.51sourcewords plus2poolwords retained. Equating stored GP values to entry callback arguments requires preservation across earlier calls. Actual allocation, initialized bucket memory, table identity, fullconstructor reachability and preservation remain OFFEN. Initial divisor7 differs from stipulated300 divisor1.

- E-XE164-317 HYPOTHESE: Two stipulated61-PC source-derived lookup instances return T through exacthash/equal and nesteddivisor1 fastreturn. Correct55e60 LDRr3,[r2,r11],55e64 CMP7,1 setsNZCV0010,55e68 BLSnot-taken. Actualstackwrite/read/savedregister/SP state andstatus events checked; isolatedstatus1/0lanes takezero-return. Original300fullstepmodel rejected/frozen. This is a stipulated synthetic path only. Original phrase constructible provider table is not adopted. Constructor304 initializes divisor7; divisor1reachability, callback tokens/runtime binding, API/ABI, faults/concurrency and actualexecution remain OFFEN/NOT_RUN.

- E-XE164-318 VERIFIZIERT: Actualindependent309 rawPC/flag audit supports corrected306 statusload/CMP/BLS and statefulpositiveframe/memorychecks. Isolatedstatus1 setsNZCV0110 and0sets1000; bothBLSzero. Independentreviewqualifies constructibility andstipulated isolatedsavedframe; no constructionproof. Static independent review is not binaryexecution. Constructor/livecallbacks/generalGLibsemantics remain OFFEN. Upstream306 frozen; narrower canonical wording retained separately.

- E-XE164-319 HYPOTHESE: Four source-driven78-PC synthetic instances close libdal2194/1ecc via directly-resolved3wordPLT15f4/GOT140ec to exactGLib lookup/callback/divisor1 path. Helper keyentryr0=7 is storedSPentry-12, lookupreturnsT;2194readsbyte[T+170]=1,1eccreturnsu32(T+110). GP4..11/SP retain entry state andsavedreturnPCcontrol holds in Root313supplement; LRitself endsGLibBias+45e2c. ResolvedGOT/global141e0/tabledata/byte/callbackaddresses/nonaliasframe/nofault premises stipulated. Numericdivisor1 notconstructor-derived; actual provider/table/record/runtime/API/ABI identity remains OFFEN. Allwrites in selectedprivateframes, no ELFexecution.

- E-XE164-320 VERIFIZIERT: Exactinstalled liblibloader inode1772/13696B SHA8fe106f2...609cf2 exports LoadSymbolELF1ee4 Dynsym452B; actual396B/99wordbody plus56Bpool separate. Valid-input localroute storescurrent indirectresult to savedoutputpointer; nonzero localresult leadsreturn0, zero followsopaqueloglane. StaticGLOB_DAT13088->PosixHelper_DlSymobject130b0 andR_ARM_ABS32dlsym@GLIBC_2.34 pinned. Conditional301join yieldsnonnullcallbackword onreturn0 underframe/GP/output-memoryretention. Currentframe/GP/savedword retention and outputnonalias/writability explicit. OpaqueIsLibraryOpen/indirecthelper/log/assert effects, appliedrelocations/runtimewinner, actualcallbacktarget andAPI/ABI remain OFFEN. Ghidraassertterminalflag isnotverifiednonreturn. No calledimplementation expanded ornativeexecution.

- E-XE164-321 VERIFIZIERT: ReadonlyFW31partition2 inode1874 yields libpackbus.so.1.0.1/148792B SHA3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6; threealiasesresolve tosameregularfile. Freshcompletebytecomparison equalspriorWP004FW30library. Exportlibpackbus_open ELF10720declared1844B; actualREA noncontiguousbodyGhidra[20720,20d00)+[20dd8,20e54)1628B/407words,216Bgapseparate. OneartifactbyteidentitydoesnotproveFWimage/device/ABI equivalence. Actualdynamicbinding/initialization/hardware/API semantics remain OFFEN. No vendorELF/VM/device/networkexecution.

- E-XE164-322 VERIFIZIERT: Exact131sourcewords comprise123wordnestedbaa78 and8wordcallerbac64. Selectedinputr0=77,r1=7 computesGhidraPCcabf8 andexecutes31nestedPCs, fiveLSL4..0/CMP/ADC/SUBCSstages, returnsr0=11. Caller saves77/7/LR, restoresintosavedr1/r2/LR, computesr3=77andr1=0, restoresSP/LR in2fixtures. Original305validatorread-onlyclaimFAIL: writes3artifacts; frozen315pureinmemoryreplay iscanonicalchecker. No generaldivision/quotienttheorem, arbitrarycomputedtargetclosure, zero-handlersemantics, actualconstructor/table/runtime/API/ABI proof. Stack/memory/nofault conditions explicit.

- E-XE164-323 VERIFIZIERT: Actualindependent312 auditsall131rawwords, computedPCcabf8, all31nestedPCs/flags/fivecomparestages and8callerwordeffects in2frames, supporting77/7->11andindex0. Detects305validatorwriteoperationsattrace/results/controls anddoesnotexecuteit. GeneralroutesremainOFFEN. Independentstaticreviewisnotnativeexecution. Original305operationalreadonlyFAIL retained. Constructorreachability/API/ABI/runtime/hardware semantics OFFEN.

- E-XE164-324 VERIFIZIERT: Corrective315 moves305boundedreplayinto puregenerate_outputs(), disablesbytecodewrites, verifiesexactpins/copies, andbytecompares3inmemoryserializedoutputs withfrozen305trace/results/controls.41checks andbefore/afterpackagehashinventoryPASS; defaultvalidator/importhasnofileoutputsideeffect. Original305/312unchanged. Operationalcheckerfixonly; no newarithmetic/runtime/constructor/API/ABI conclusion. NativeELF/device/networkexecutionNOT_RUN.

- E-XE164-325 VERIFIZIERT: Exactlibpackbus_open407wordbody plus54poolwords stage16callbackwords throughGOT/stack/D8..15 then4vectorstores at currentr4+14/+24/+34/+44. ThreefurtherGOTstoresat+54/+58/+5c; +4/+8 each2ee0. CMPcurrentr4,r6 equalityskips publication. All19callbacknames haveexactR_ARM_GLOB_DAT source relocations. Original311IoDrvDal226c attribution/base+110 comparison notadopted; use318andRoot323. D8..15/currentGP/frame/GOTpreservation acrossopaque calls explicit. Actualpublication/runtimebinding/API/ABI/hardwareOFFEN.

- E-XE164-326 VERIFIZIERT: Actualindependent318 reproduces19callbackpositions/relocations,16vectorlanes,2ee0words andpublicationguard. Corrects sourcejoin:226c belongs libdal.so, r0=currentlibdalr6+110; backendinitialr4=entryr0. Ifretained,publicationcell=currentbackendr4+fieldoffset=T+110+offset; never addsecond110. BackendGOT ELF33000/Ghidra43000/runtimePackbusBias+33000 separated. Pointerequationconditionalonly; actualcalledprovider, GP/Dreg/stackmemoryretention, actualTandproviderwinner remainOFFEN. Staticindependentreviewnotruntimeexecution.

- E-XE164-327 HYPOTHESE: Reviewed7rowmatrix links6primaryproviderpositions30/3c/40/44/50/54 andseparatelistcontext58 conditionallythroughlibdalmethodstoC+2c/20/30/24/18/28/3c,withC=T+110. Exactbackendexports WriteStart/WriteBytes/WriteEnd/ReadStart/ReadBytes/ReadEnd/DiagGetDeviceState andELFentries derivedfrom318relocs+310dynsym. C+4/+8conditional2ee0 words retained; O,D,primary/separatecontexts remain distinct. Composedinstancenotobservedruntime. Identicalnumericpositionsdonotproveobjectidentity,API/ABIorconstructorreachability. Originalinternalmechanicsnotautomaticallyreplacementrequirements. No vendor/runtime/VM/device/networkexecution.

- E-XE164-328 HYPOTHESE: Two distinctbias/datafixtures withtable numeric+0=8,+4=7,+8=7 close2194/1ecc throughdirectresolved3wordPLT, exactGLiblookup/hash/equal and31PCselected77/7arithmetic. Four107PCprimaryroutes returnbyte[T+170]=1 oru32(T+110), restoreGP4..11/SP andsavedreturnPCcontrol; exactNZCV/PC/register/memoryeffects recorded. Fivefinitecontrolsspan500rows. Matching8/7/7initializationwordsdoesnotproveconstructedtable/callback/arraypopulation/actualruntimebinding. Allmemory/GOT/frame/nofault/nonconcurrency conditionsstipulated. No generalquotient/probe/API/ABI proof ornativeexecution.

- E-XE164-329 VERIFIZIERT: Actualindependent322bytechecks249sourcewords, four107PCprimaryroutes and500controlrows againstsourcewhitelist; independentlyderives77/7computedPCcabf8and31PCflags/stages using312route, confirmshelperbyte/T+110results andexplicitinitializer8/7/7scope. Generalconstructor/runtime/API/ABI conclusions remainOFFEN. Independentsourcereviewnotnativeexecution. Modelgenerationreused314butarithmetic/sourceoraclesseparate312/rawbytes. Allinstance/binding/alias/fault/concurrency limits retained.

- E-XE164-330 VERIFIZIERT: Actual independent raw-source audit of original317 confirms 178 words and conditional empty-branch/store deductions but rejects complete instruction replay: omitted31 nested PCs, early quotient injection, wrong NZCV/next-PC continuity and fixture mismatch. Original317 frozen, not canonical full replay; local source deductions conditional on opaque normal return. Corrective327 replaces replay evidence.

- E-XE164-331 HYPOTHESE: Corrective source-stepper binds301words, two135-fetched-PC routes each119 executed/16 skipped, including31 nested77/7 PCs. K>T flags0010, real BL at456e0 passesB,32 to bias+7f11c; separate stipulated return r0=V yields H20=V,B0=K,V0=T, three counters1, return1. Three source controls checked. Fixture/opaque continuation only, not construction/runtime. Canonical normalization per333: columns r0-r14 plus nonarchitectural r15 sentinel and separate PC; H/C/frame retention stipulated, no B-retention requirement. All memory/fault/alias premises explicit.

- E-XE164-332 VERIFIZIERT: Independent checks301sourcewords/270 positiveinstructionrows, raw branch predicates/computed targetbabf8, quotient11/index0, source stores and3controls. Representative volatile clobbers preserve selected suffix; r15 sentinel and opaque B-label qualifications recorded. Static source audit only; finite clobber probes not arbitrary-clobber proof. Upstream327 decoder reused for probes, independent raw source/ALU checks; no native execution/API/ABI.

- E-XE164-333 HYPOTHESE: Seven libdal candidate methods source-step through2180/2194/1ecc, resolvedPLT and divisor7 GLib route:14paths3392fetchedPCs/1778memoryevents,10controls,451sourcewords. Exact BXr3 tails preserve selected SP/LR/GP4..11 and record numericr0..3/backenddynsym pointers. Stops before backend fetch. Callback cells/table/GOT/frame/record identity stipulated. Six cyclic getter cells and separate58 candidate/context remain distinct; no runtime producer binding, API or ABI.

- E-XE164-334 VERIFIZIERT: Independent audit verifies451rawsourcewords, getter R_ARM_RELATIVE addends,7backenddynsyms,14tails3392PCs/1778events and10controls; backend not fetched. Shared303/314 stepper lineage disclosed. Numeric conditional source join only; original runtime publication, constructed object/table identity, callee effects and physical I/O remain OFFEN.

- E-XE164-335 VERIFIZIERT: Exact7backend bodies415words/11poolwords plus optionalReadStartGate26+1. All derive cellG=BackendBias+44420;32mainBLs and4helperPLTs pinned. Source local status gates, byte-method unsigned segmented arithmetic,2ReadBytes memset sites/noWriteBytes memset, numeric diagnostic3/0/2/1 stores recorded. Canonical336 corrections apply: G is cell address; source tests S=[G], then needed[S]/[S4], no G-null/readability guard. Post-opaque ReadBytes requires live r4/F,r5/X,r10/E,r11/A, conditionalr7/S,r8/Z/frame/query/state preservation. No API/ABI/callee effects inferred.

- E-XE164-336 VERIFIZIERT: Independent raw-source review checks415+11 words, optional26+1, eightcelladdress equations,32mainBLs/4helpercalls and PLT relocs; ReadStart helperzero→clock,ffffffff→directreturn. ReadBytes/WriteBytes arithmetic/call vectors and diag local status verified. G terminology and live preservation qualifications supersede324 prose. Source-state predicates/segment equations only, no semantics from names, broader range correctness/runtime binding/concurrency/fault guarantees remain OFFEN.

- E-XE164-337 VERIFIZIERT: Fresh readonly exact FW31 partition2 inode dumps782/783/784 produceXE164L1/L2/L3 sizes32/266/16598, each fully byte-equal pinnedFW30source. Composite recipe32+266+214zero+16598 yields17110B SHA5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983 equal priorcomposite. Four source/additioncatalogrows separately retained. Only these precise files/composite identity; E00000 placementHYPOTHESE. No loader/startup/SFR/ABI equivalence, no FW31 C166 execution or transfer of earlierPASS.

- E-XE164-338 VERIFIZIERT: Independent audit binds image/inventory/partition/inode records and byte-equality of three FW31/FW30payloads; independently reconstructs17110Bcomposite without335builder and confirms old/newhash. Extraction itself notrerun; preserved recipe/stat/dumps inspected. Currentcataloghash recorded, no prior snapshot proves historical immutability. E321 backendcomparison outside337scope. E00000mappingHYPOTHESE/runtimeNOT_RUN.

- E-XE164-339 VERIFIZIERT: Exact getterELFec88/12B plusliteralec94 returnsimage-relative337f8. 28nonnull52Brecords plusrow28zerosentinel: name32,+20word,+24function,+28argc,+2cargtypes,+30returntype. 110 argument slots and28returnslots bound to raw ARMrelocations, separate observedREAfixups and candidate libffi versioned12Bobjects. Canonical339 corrects prose: argspan file23ddc..23f98, not25ddc; argument types includeuint32 (3) besidesuint8(50),pointer(42),uint16(15). Raw TSVs correct. Ghidra external tokens notruntimepointers; API/ABI/reachabilityOFFEN.

- E-XE164-340 VERIFIZIERT: Independent raw ELF PT_LOAD/table/reloc audit checks29rows,110argumentcells, both334TSVs, getterequation, candidate libffi symbolvalues/versions; alltabledata correct. Threeuint32args are row21arg0,row22arg0,row24arg0. Returnrefs26sint32/2uint32; all138typecells zero-addendABS32. Two334proseerrors correctedwithoutupstreammutation. Raw symbolrefs/localcandidate match doesnotprove binding/prototype/ABI. Report finalself-reviewboilerplate doesnotnegate actual distinctauthor audit; Root recordsactualscope.

- E-XE164-341 VERIFIZIERT: Exact AppStateChanged142words plusfourwatchdogbodies39words and12PLTwords=193;9separateliterals all deriveGcell44420. Twelveapplicationstores/18opaquecalls/fourwatchdogrelocs pinned. WatchdogsnullSreturnffffffff; nonnullr0=[S+dc], SetTime forwardsentryr0→r1/entryr1→r2; otherwrapperspreserver1/r2locally. Original state2report/storeledger reversedroute and is supersededby338: policy1/freshprior1directlystores1 at+a0 withno+a1read; otherselectedstate2routesnormalize+a1. Freshloadsnotassumedidentical. Opaquecallpreservation/currentstate conditional, retry no convergence; no stateenum/API/physicalwatchdogclaims.

- E-XE164-342 VERIFIZIERT: Independent193word/9pool audit derives3state2routes: policy!=1 andpolicy1/freshprior!=1 read+a1 andnormalize0/1; policy1/freshprior1 bypasses+a1 andstoresr2=1 directly. Numeric correctedmatrix/sourcepaths retained. Fourwatchdogtails/PLTGOTarithmetic/relocs verified. Selected sourceconditionsonly; entryr4/global/frame preservation acrossopaque calls mustbestipulated. Earlier/laterpriorwordloads distinct, nofinalstate/convergence/API/ABI/physicaleffectproof.

- E-XE164-343 VERIFIZIERT: 168words exact O70wrapper29e4/common2784/helper20b0,2getterRRELcells and30executableinlineBstubs. Wrapperr2=S-8 points2savedwords; helper20b0 loads distinctglobal141e4 andforwardsname. Commoncase widths/callvector/returncopy bounded; ffi_callstaticJUMP_SLOT1409c. All currentGP/memory/frame mapping after opaque helpers conditional. Unsupportedtag4/13/>14 setsr7=-1 butcontinues, noinputadvance/vectorstore. Tag0 likewise skipsstorewithoutmarker. NoAPI/ABI/runtimecallerrepresentation inferred.

- E-XE164-344 VERIFIZIERT: Independent168rawword/30branchstub audit confirms wrapper24Bframe, both15casedispatches, zero-nargsr3=0 andnonzeror3vectorbase. Unsupportedargcases leavevectorcelluninitializedbythispath yetadvancevectorcursor and reachffi_call. Global/device labels shorthand observedcalltests. GP4/5/6 across earlierhelpers andr7survivalacrossffi_call OFFENwithoutexplicitpremises. No nativeexecution.

- E-XE164-345 VERIFIZIERT: Exact46764B FW31libffi SHAd162a9b2...17c4f5,803REA/rawsourcewords incl326noncontiguousprep/7wrapper/300internal/4+11thunks/48+107helpers,10versioned12Btypeobjects. Prep guardnumeric1/2 accepts,othersreturn2;sourceCIFfieldstores. BLX8010targetcurrententryr2 andcurrentr11framecontinuation; bounded7returnslots0..6 rawfallback. No completeconstructor/ffi_call/ABI closure. Ghidra nofunction18040 errorretained,128Breadcontextafter8078notpromoted. All target normalreturn/frame/currentr11/memory dependencies explicit; runtimebindingOFFEN.

- E-XE164-346 VERIFIZIERT: Independent803word/PT_LOAD/typeobject/version audit confirmsnoncontigprep235c..2468+7644..7a50,tail240c→7644,guard/fieldstores,wrapper andBLX/currentframe mechanics;7rawreturnslots. Canonical caller erratum:8000callatGhidra174f0 belongs internal17194body, NOTffi_prep_cif as343prose says. Independentlyreconfirmedbyreviewer349;343 frozen. Completefunction/ABI/runtimeeffects remainOFFEN.

- E-XE164-347 HYPOTHESE: 28namedrecords/110args map candidate libffitypes5(50),7(15),9(3),14(42) tosource wordinputadvance4/staging8/stores1,2,4,4;28returns9/10copy4. Selectedstackbeforecall40+align8(4n)+8n, max128 atn7, excludesouter24/callees. Requiresmatchingcandidatebinding/recordconstruction, successful earliergate/name/helperpaths andliveGP/frame/memory continuity. No publicprototype,callerABI,pointervalidity or runtimeproof. Generalunsupporteduninitializedslotpaths remainpossible forothermetadata.

- E-XE164-348 VERIFIZIERT: Independent recomputation checks28nonsentinelrecords/110rawrefs, exacttypefields, handlerwidths/targets andall28ret4bytecopy cases; stackarithmetic0args40/max128; no upstreambuilderoracle. All110supportedhandlers is conditional onbinding AND reachingselecteddispatch withvalidlivevalues acrossopaquehelpers. Synthetic compatibility notexecution or constructedrecordproof.

- E-XE164-349 HYPOTHESE: Source-stepper startsstipulatedpost2194successat27c8: args5/7/9/14write low1/2/4/4bytes into8Bslots, exactBL28ac/1504numericr0..3. Zeroargsr3=0; unsupported4setsr7ffffffff/vectorcellunwritten yetcalls. Separatepostopaque28b0return5/7/9/14/4 copies1/2/4/4/none,stops2878beforeepilogue. Startsselectedsyntheticstate; r11/SP relation fromactualprologue notestablished, no reachability proof. Earlier2180/20b0/2194 andffi_call opaque. Exact result/register/frame premises explicit; noABI/API/actualnativeexecution.

- E-XE164-350 VERIFIZIERT: Independent frozen340audit checksrawbytes/PCcontinuity/computedbranches, both15Bstubtables, argument/returncases, sourcewrites andunwrittenunsupportedcell; validatesactualcallr0..3 andseparateopaque-returnconditions. Finite selectedsourcepaths only. Initial27c8syntheticstate notshownreachable frombodyprologue; returnedSP/GPepilogue notmodeled. No hidden helper/callee/ABI preservation.343callererratumconfirmedwithoutediting343.

- E-XE164-351 VERIFIZIERT: 407wordopen/54pools deriveG=BackendBias+44420; uniqueidentifiedSTRr8[r9]at10ba8publishescurrentallocationword undercurrentGP/opaquehelpergates. ExtraORRSr4|r6 gate afteropaquecall required; existingSskipsallocation. Directlocalzeros+a0/+a1/+a2 andopaque-returnwrites+0/+4 inventoried. Frozen342 '325/338distinctprovider' prosefalse: sameexactbackend/globaladdress; corrected351. EqualGnotpersistentSidentity. No allocatorzeroing, helperwrites, callorder/termination, runtimebinding/ABI inferred.

- E-XE164-352 VERIFIZIERT: Two22worddefinedbodies plus2x3wordPLTs=50words/4pools. CreateWatchdog source storesopaquereturnthroughcurrententryoutput, returns0on nonzero; vGet copies6currentwordsfromELF47bac+18..2c tocurrentoutput+0..14. ExactstaticPLT/JUMP_SLOTtargets14c68/14a50. Register/frame/outputvalidity acrossopaqueallocator/once/lock/unlock calls conditional. Callback14774hadnoGhidraprocedure; no inventedbodyin348. Staticbindingnotactualwinner/API contract.

- E-XE164-353 VERIFIZIERT: Underexplicitlocaltarget/currentGP/memory premises openhelpercallentryA+dc receivesopaqueallocationreturn; nonzero→helper0→opengatepasses. vGet6words landA+a4,a8,ac,b0,b4,b8; openimmediatelypublishescurrentr8throughr9 withouttestingvGetr0. SameimageReadStart+d4 distinctDiag+dc consumer. No+d4producerfromthesebodies. Currentglobalwordorigins/actualcallback14774effects unexpandedhere; later352sourceevidence separate. Instance/lifetime/ABI/allocationzeroing/synchronization notestablished.

- E-XE164-354 VERIFIZIERT: Independent407+50word chainreview rawchecks bothGaddresscalculations/publication, entry/currentregister/helperreturngates,2PLT/GOTrelocs,helperstorevectors andfieldcoverage. Correct342sameprovidererratum explicitly; 325/338samehash/G. Conditionalproducerassociationonly. Normalreturn/currentGP/frame/globalword/destinationnonalias/readabilitypremises required; nopersistence, objectidentity, actualrelocation orfunctionsemantics inferred.

- E-XE164-355 HYPOTHESE: Six source-driven entry235c preparationfixtures use326prep+107classifierwords; numericmode2zero/2/3/7args setCIFfields and16FFbytes at+20..2f, true6fe8classifierpaths return0for5/7/9/14; mode1acceptedwithoutNEON/classifier,mode3returns2beforeCIFwrites. ActualsyntheticSP/GP snapshots retained. Frozen347proseELF16fe8..17094 erroneous; correctELF6fe8..7194/Ghidra16fe8..17194, tables/tracescorrect. SyntheticCIF/type/stack/memoryonly; no constructor/runtimebinding/ABI/type meaning.

- E-XE164-356 VERIFIZIERT: Independent433rawsourceword/typebyte audit checks6traces, source-updatedNZCVconditions/computedbranches, actual6fe8→7044classifierreturn,16FFNEONstore andnumericmodecontrols, GP4..12/SP snapshots. Source/classifieraddresserratum explicitlycorrected. Finite selectedpaths only; notseparatefullCPUvalidation norunselectedsignature/ABIproof. First347rangeend17094also typo, canonicaluses17194Ghidra. Upstreamfrozenunchanged.

- E-XE164-357 HYPOTHESE: Two fixtures beginactualffi_call7a64entry withmode2records byte-matched347, run84/145fetchedPCs through7194/69ec byte-wordhandlers/8010BLXtarget, separateopaqueeventresult, raw8060store andfullframe/wrapperrestore. 817sourcewords bound; classifier6fe8/memcpy14dc notfetched. Canonical361 correction mandatory: original353eventlists4preservedframewords butsuffix needs15. Required r11/r0 pluswordsat+ranges0..c,24,54..74(nine),84; otherGP/SP/flags/memoryfiniteclobberprobechecked361. Targeteffects/runtimebinding/reachability/ABI stillOFFEN.

- E-XE164-358 VERIFIZIERT: Independent817rawword binding and84/145selectedsourcePCreplay checksflags/branches/helperloads/stores/targetstate/fullreturn. Derives15postBLXreadwords; preservingonlythese plusr11/numericr0whileclobberingallothermappedbytes andr1..10/r12/LR/SP/NZCVstillcompletesselectedsuffix. Four-word353target-eventpremise incomplete, notpromoted. 15wordpremise/path-specificfiniteprobe, notgeneralcalleeclobber/ABI guarantee. No actualtargetcode/nativeexecution.

- E-XE164-359 VERIFIZIERT: 178actualsourcewords/8pools: Get60/Put50/length45/accessTX19inclfarPLT3/accessRX4. Get/PutgateE=U32(r1+r2)>2edf returnsnumeric3 beforehandle/data/othercall. Sourceacceptedloops/queryoutputs/bufferPLTboundaries inventoried. Rawsumwrapacceptedgate notmemorysafety. accessTXnoncontigspan29952isnot76Bcodeextent. Importedcallee/memory/callbacksemantics unexpanded; pointer/currentGP/framepremises explicit; noAPI/hardwareclaim.

- E-XE164-360 VERIFIZIERT: Exact6sourcewords GetPLT777c→GOT3312c/staticSSC_Gete17c andPut7cb0→332e8/staticSSC_Pute370; actualretainedmetadata/body records andrawrelocs agree. RuntimeGOTcontents/preemption/loaderwinner mustbestipulated; names/relocsnotruntimebindingorprototype.

- E-XE164-361 HYPOTHESE: Fourfullsourcepaths at2biases startactualbackendReadBytes/WriteBytesentries, passX11999/Y1 viaexact3wordPLTs tolowerGet/Put, gateE12000→r0=3, actualupperthenreturns0 withSP/GP4..11restored. NoZaccessorO-dereferenceonselectedrejectpath. Twelvefinitecontrolsstopaccepted/wrappedgate orreturndisabledwithoutSSC. Canonical365corrects358prose O=S+4: OiswordstoredATaddressS+4, numericallydifferentpointer. FixtureG/S/flags/halfwords/GOT/sourceframesonly; noruntimecaller/APIbug/statussemantics/memorysafety claim.

- E-XE164-362 VERIFIZIERT: IndependentrawA32replay verifies4primarytraces,8acceptedgatecontrols,4disabledcontrols andallmemoryevents; audits150+137upper/60+50lowerwords/6PLTwords. Lower3/upper0/noZorOobjectextentaccess andactualframe/GP restoration confirmed. Acceptedcontrolsstopbeforefollowinglowerinstruction, soacceptedbranchnotacceptedmemorybehavior. Oloadproseerratumrecordedwithout358mutation. ExplicitresolvedGOT/instancepremises; noABI/API/runtimeclaims.

- E-XE164-363 VERIFIZIERT: 19exactsourcewords hash11/equal5/strcmpPLT3. HashsignedLDRSBrecurrence U32(33h+signedbyte), initial5381, finite28ASCIIfunction-namevaluesderived; equalCLZ>>5mapsopaque32bitr0zero→1/nonzero→0. PLTGOTELF134044/GLIBC2.4 bound. Finitearithmetic notinstructionreplay/lookup. strcmpimplementation/equalitysemantics notassumed; returnframe validity afteropaquetargetconditional. Actualcallbacktableconstruction/symbolbinding/ABI/runtimeOFFEN.

- E-XE164-364 VERIFIZIERT: Independentraw19wordaudit and28namehashrecomputation excludezerosentinel, confirm signed0x80/ffcontrols andempty5381; PLTrotatedimmediatearithmetic/staticGOTrelocationverified. Onlyboundedsource andfinitevalues; no actuallookup/callbackbinding/stringmemoryvalidity/ABI/APIproof. Opaquereturnvalue/equalityframepremises retained.

- E-XE164-365 VERIFIZIERT: 163 complete-body words plus9 bounded callback words/11 pools establish numeric base47bac, callback14774, getter/setter/reset source. Callback slice zeroes48B before opaque tail; reset zeroes24B after once-named call. Bounded callback has no recovered complete procedure. Current GP/frame/memory after opaque calls conditional; no initialization/lock/API/ABI semantics.

- E-XE164-366 VERIFIZIERT: Get stores min(Q>>3,ffff), local return2 at Q>=80000; zero-global fallback performs clear then reload, so aliases matter. Set unsigned BHI means r5>Q>>3; equality zeroes selected block, below returns1. r5=65536,Q=524280 selects update but STRH stores0. Reset returns current opaque r0 unchanged. Numeric branch/store matrices and finite controls, not full instruction replay. Query/frame/GP/current-memory premises explicit; no value units/status/API or runtime binding.

- E-XE164-367 VERIFIZIERT: Independent172 raw-word/11-pool audit recomputes base/callback arithmetic, unsigned branch gates, threshold equality, partial store gaps, 65536 truncation witness, getter alias ordering and reset opaque-r0 flow. No actual callback execution or general alias/runtime/opaque-callee contract. Zero comparison does not prove pointer validity.

- E-XE164-368 VERIFIZIERT: 81 source words: read24/write50/lengthPLT3/getter4. Read/write selector1 clear destination BEFORE reading possibly aliased source. Write selector4 attempts halfword A+2N-2 before N-2 negative gate. Getter returns4013c+U32(index<<4), no result dereference/guard. Source positions only, not descriptor/API layout. N0 access is ordered source fact, not native fault prediction. Length-record contents/producer still open.

- E-XE164-369 HYPOTHESE: 48 finite traces at2 biases cover alias/disjoint clear-copy-mask paths, numeric selectors0..6, XOR N1/2/3, N0 attempted A-2 read and actual stack operations. Alias source reads observe post-clear f0/read or f3/write fixture values. Model interprets retained REA assembly strings after raw-word binding; not an independent complete A32 decoder. N0 unmapped model stops before BMI; no native exception/reachability claim.

- E-XE164-370 VERIFIZIERT: Independent raw branch decoding checks5 computed-PC B stubs, LS/default routing, flags/access widths and all48 trace source fetches. Alias post-clear values, N1..3 XOR iterations, N0 pre-branch attempted read and encoded stack events agree. Bounded selected audit does not turn assembly interpreter into arbitrary-input CPU emulator. Descriptor semantics/runtime/physical behavior remain open.

- E-XE164-371 VERIFIZIERT: 140 source words include128 noncontiguous registration words, helper6 and2 PLTs. Local path requests60B, passes prep P+8/mode2 with row-derived operands, then return-zero stores P0/P4/P38. Selected48B prep interval P8..37 fits request beside device word P38..3b. CIF/consumer offset compatibility conditional on same P/current row/GP/frame and actual binding. Original O10 candidate327c is overwritten in copied D10; no manager-to-registration runtime join.

- E-XE164-372 VERIFIZIERT: Independent ELF PT_LOAD mapping verifies140 raw words, actual128-word two-range extent, branch/PLT GOT equations and static relocations. Numeric60B/48B overlay agrees with selected347/357 prep and330 consumer loads; E309 copied-D10 override retained. Reviewer discloses347 ancestry. Complete ABI/constructed object/table insertion/runtime reachability/allocator and prep opaque effects remain open.

- E-XE164-373 VERIFIZIERT: 263 source words/18 pools cover SetTime54,Start92,Stop15,Trigger38 and callfree comparison64. Nonnull SetTime uses wrapped N=U32(r1*r2), accepts1..3fffffff, stores1/N/Q/(N-Q*1e6)*1000/8zero bytes; full-range reciprocal bound proves Q=floor(N/1e6). Stop nonnull writesbyte18=0. Other methods retain explicit opaque/current-state premises. Null-P branch precedes MUL; multiply precedes N range guard only. Signed strict>1e9 normalization differs from equality. No units/lifecycle/API/ABI/physical watchdog meaning.

- E-XE164-374 VERIFIZIERT: Finite wrapped-product/reciprocal/store fixtures and two callfree helper paths support selected numeric predicates, equality-at1e9 no carry, signed comparisons and unsigned counterflag. Original SetTime snapshots are manually scripted and NOT accepted as complete instruction replay. Its replay.py writes and was not rerun.373 verifies helper histories;375/378 supersede SetTime-history gap.

- E-XE164-375 VERIFIZIERT: Independent263word/18pool audit proves selected U32/MUL/UMULL/MLS outputs and full accepted-range reciprocal bound; actual raw interpreter reproduces both helper traces including PC/NZCV/register/frame/memory events. Full SetTime snapshots in360 remain unverified by373. Numeric conclusions accepted separately. Invalid lanes stop before logger BL; no opaque-return or ABI claim.

- E-XE164-376 HYPOTHESE: Corrective raw-word stepper executes18 selected paths at2 address mappings,394 fetched rows/132 memory events, full r0..14/PC/NZCV/D16 and actual frame restore;3 invalid routes stop before logger BL. Selected numeric/store outputs agree with360. Independent378 qualifies36 push preimages: zeros are implicit model fill for absent preloaded stack bytes, not established initial memory. Post-push/frame/pop/return and numeric transitions accepted; no runtime/API/ABI claim.

- E-XE164-377 VERIFIZIERT: Independent raw decoder reproduces all394 rows and132 ordered effects across18 paths, checks54words/6pools, arithmetic, conditions, SP/r4/PC restore and invalid stop boundaries. Identifies36 model-default zero push preimages. Accepts zero preimages only as model default, not source-derived data. No other selected transition/store/return mismatch; finite synthetic source evidence only.

- E-XE164-378 VERIFIZIERT: 1004 freshly retained ARM words,172B excluded gap,11 initial44B rows/9relative path fixups and four complete FW31/worker004 artifact identities verified. Static REV length candidate000040d6 and exact L3 XOR83 computed; all initialselectors0. Canonical qualification379: row9 XOR/Ack fields verified, but frozen370 stronger no-resend sentence is not yet independently established by table/source-access audit. Reader/file reuse versus selected output-call vector needs separate follow-up384. No actual boot/transfer/placement or general FW/ABI equivalence.

- E-XE164-379 VERIFIZIERT: 2104 independent checks confirm four wholefile byte identities,1004words/noncontiguous extents,11 raw/fixed rows/nine RREL fixups, selected field accesses and finite size/XOR candidate. Flags row9 exclusivity/no-resend as unclosed stronger claim. Row9 retains same L3 path/sentinel as8, so table alone cannot settle reread/output. Rows4/10 remain only raw null-path/word1 records. Candidate sequence is arithmetic, not capture/runtime/reachability.

- E-XE164-380 VERIFIZIERT: 109 raw words cover Create61,snapshot19,flip16,leaves5/5/3. Create explicitly writes index words0/1/2, but no byteP24 initialization; separate nonbodyNOP and0/1 pool retained.36 finite permutation formulas use post-acquire/pre-unlock state. Allocator zero-fill/construction/actual locks not proved. Finite formulas not instruction replay; leafindex has no bounds. First source validator opcode typo fixed before freeze without changing source/formulas.

- E-XE164-381 HYPOTHESE: Original48-word selected models provide6 leaf cases,36 permutation endpoints,2 null controls and unmapped0x3048 read boundary; source routes and local formulas agree. No per-step GPR/NZCV/memory/frame histories. Object preservation across opaque calls initially implicit. validate.py IS A WRITER; Root inspected and did not rerun frozen369. Corrective377/382 canonical for complete histories.

- E-XE164-382 VERIFIZIERT: Independent109word audit confirms Create0/1/2 stores and no P24 store, pool/NOP boundary, leaf formulas/branch PCs and36 transforms. Identifies missing histories and missing acquire/unlock object-memory premises in369. Verified local pre-unlock writes do not establish returned object memory without unlock preservation. Actual allocator/locking/ABI/runtime remain open.

- E-XE164-383 HYPOTHESE: Raw-word stepper records45 scenarios/562 instruction rows,290 source-memory events plus180 stipulated opaque-memory events/72 call boundaries. Post-acquire tuple is explicitly installed; unlock preserves objectP18..24 and savedframe/SP while clobberingr0/r4. Actual MOV/pop thenreturn0 andrestore frame. 382 qualifies broad scratch wording: concrete fixture leavesr5..11 unchanged. D16 is implicitly unchanged at opaque boundaries, but selected outputs do not depend on that preservation (overwritten/unused). No actual callee contract.

- E-XE164-384 VERIFIZIERT: Independent23052 checks reproduce562 raw steps/290 source-memory effects/180 premise effects/72 opaque boundaries; actual push/pop restoresr4/SP/savedPC. Confirms pendingbyte supplied only post-acquire and no CreateP24 store. Concrete scratch clobber vector narrower than377 prose; D16 across opaque calls fixture-only and source-liveness-insensitive. All final object values conditional on explicit unlock memory preservation.

- E-XE164-385 VERIFIZIERT: 957 actual GetCnfFromRail words/10 separate pools,6 PC/literal equations. Four yieldB4013c, distinct4017c/GOT33000. Selected lane r6!=1 stores U32(r10<<3) atB+U32(I<<4),zero+8; r6==1 stores+4,zero+c; optional round via c974.176B source frame. Laterc89c/ca4c current-address increments have no whole-body invariantB+index proof: reusedSP24/SP28 overwritten elsewhere. Complete value provenance/descriptor/API/units/runtime remain open.

- E-XE164-386 VERIFIZIERT: Independent PT_LOAD/raw mapping confirms957word body/10 pool refs/6 equations and B4013c lies in BSS memory extent beyond file-backed data. Selected store fields/lane gates/rounding/frame exact. Source-local address relationships do not prove later live stack bases or complete constructor/producer path. Explicit overwritten stack slots preclude global pointer invariant.

- E-XE164-387 VERIFIZIERT: 111 selected raw words establish local row8 nonzeroN call vector(F,P,N), row9 prefix0/XOR1 seed0 fold over P..P+N-1 then vector(F,SP+d8,1), both ELF7998/Ghidra17998. N0 row8 skipscall,row9 calls withzero scratch. ExactL3 finite XOR83. Conditional selected call-vector distinction only, not guaranteed transfer/no other sends/runtime reachability. Reader can reread same L3 path; sentinel continuation needs current helperr0!=ffffffff/readableSP34 and frame/GP. No full CPU replay claim.

- E-XE164-388 VERIFIZIERT: Independent111word/table/loop audit confirms CMP flags survive EOR(S0)/STRB toBNE, N bounded byte reads and finite L3 fold83; reader sentinel continuation premises explicit. Root rejects386 alleged384 prose address typo: actual frozen384 report SHA c7ebaaa84d2126dbdee8dac31c01a724c9419c159ff346582c8341fe32bec2c2 already says7998 twice, no17998. Reviewer acknowledged error;386 frozen, correction recorded next389. Raw validator target correct.

- E-XE164-389 HYPOTHESE: 237 exact words and four selected name routes/1096 rows join helper20b0 through tablecell141e4, GLib signed-byte hash, full131word divide, equality and fixtureT. Canonical381 rejects mismatch-summary return0 because control stops before45de0; literal VA/file20c4 versusvalue12120 corrected; strcmp event originally omitted needed memory. PositiveT accepted only with stronger387 premises.

- E-XE164-390 VERIFIZIERT: Independent237word/PT_LOAD/source/flags/stack audit identifies literal prose error, fabricated stopped-control return and missing active48Bframe/fourpostcalltable words; source routes/numeric hashes/divide endpoints agree. No actual table construction/provider binding. Original implicit unchanged memory not promoted to callee contract; corrective387/391 required.

- E-XE164-391 HYPOTHESE: Corrective237word model preserves1096 baseline histories, adds finite scratch-clobber probe (1350 total rows), explicitly records25 protected spans across5 opaque events:48B activeframe plus4 source-derived postcall words each. Mismatch summary NOT_RETURNED; literal20c4/value12120 corrected. Selected opaque return stipulatesr0=0/r6/r11/SP/normalcontrol and protectedbytes. Probe clobbers one unusedword,selectedscratchGP/LR/NZCV; finite witness not universal ABI. Scratcheffect pc/address columns overloaded; dedicated probe TSV supplies actual labels.

- E-XE164-392 VERIFIZIERT: Independent237rawword/1096baseline/25span audit checks actual reads45ea0/45e60/45e6c/45e70 and both stackpopregions. NOT_RETURNED control and finite clobber route/T/frame restoration consistent. Independent ledger/source audit, no replay-builder import and no actual strcmp implementation/ABI/tableconstruction claim. Scratch serialized field-label ambiguity disclosed.

- E-XE164-393 HYPOTHESE: 45query+3PLT+4getter words/4pools form four selected cases. Optional source order L0/L4/Lc/L8 then2 shifted sourcewords; output0=L4 alias changes laterread. Returnr0 remainsgetterL=4014c under fixtureentry1→mapped1. Fixture mapping is synthetic, distinct from raw initialrow1→mapped2 later397. Original validator checks storedtraces, not fresh regeneration;392 transition review uses recorded reads;395/396 close selected memory/regeneration gap.

- E-XE164-394 VERIFIZIERT: Independent ELF/PT_LOAD/raw52words/4pools and recorded transition audit checks GPR/NZCV/conditions/branches/eventwidths/actualstack/outputorder/alias/finalr0=L; no selected source defect. Uses recorded memory-read values as inputs, does not independently rebuild fixturememory. No fresh serialization regeneration by original388validator; additional395/396 required for that stronger scope.

- E-XE164-395 VERIFIZIERT: Fresh pure388 run_case recreates all four resultobjects/186rows/86reads/48stores and fullfinalmaps without writer. Separate initialized byte-map oracle derives everyread from initialbytes+priorstores and checks finalmap equality; upstreaminventoryunchanged. Fresh CPU uses same388 model, not independent decoder. Root byteoracle does not enforce store permissions; writable output/frame ranges are explicit fixtures, independently bounded by396. Entry/mappedindex1 only.

- E-XE164-396 VERIFIZIERT: Independent fixture byte-map audit reproduces86reads/48stores, exactstackcycle, actual337dc=1→L4014c mapping and alias worda0a0a001 read-after-write. All48stores lie within stipulated writableoutput orsavedframe ranges. No runtime mapping/permission claim; output writability stipulated, not proved for processmemory. Complements392 rawtransitionreview and395 same-model regeneration.

- E-XE164-397 VERIFIZIERT: 130 exact words/5pools: Init62,Desc18,Count14,12PLTs36. G4442c distinctsnapshotB44448; Desc freshS1 afteropaqueacquire calls memcpy(B,S1+18,36b0); CountreadsS1+36c8,mirrorsG16/reloadsafterunlock. Initnumeric370c/1 publishesreturnedword beforelaterlockcalls. S0/S1 not assumedidentical, freshS1 not recheckednonnull. Call vectors not memcpy/lock/allocator semantics. Copy14000Bendswherecountstarts, not complete ABI/layout. Root source checks run with PYTHONDONTWRITEBYTECODE=1.

- E-XE164-398 HYPOTHESE: 16 actual-entry synthetic GetCnf routes2bias×mode1/2×config0/20×optionalpointer, currentRAILG0 and localPLTbindings. Four getters return0 locally beforefurtheropaque calls; index2 lanezeros C24/C2c vsC20/C28, oppositecanaries preserved; selected sourceepilogue returns0/restoresSP. Trace snapshots are postinstruction states with memory/control effects. ActualG0/runtime/API/emptydevice not established. Separate397 Update guard can rejectnull descriptor beforethiscallee whenstatepreserved; no wholeUpdate-success claim. Corrects386 ownfalseproseerratum.

- E-XE164-399 VERIFIZIERT: Independent1102source/pool values viaPT_LOAD, fixturemem reconstruction,16routes/GOT/conditions/rawbranches/loadstore/stack/output/bias audit agree. Verifies389 correction:384prose already7998,386falseerratumwithdrawn. Does not implement second complete ALU engine; arithmetic generation supported by389stepper, separate independent memory/predicate oracle. All runtime/binding/API implications open.

- E-XE164-400 VERIFIZIERT: 224sourcewords/3pools: Init165/Open23/12PLTs. G443f4 publishcurrentallocationreturn afterrequest(1,74hex), beforelocks. OpenunsignedI<=3 uses freshS1 slots5c+8I/60+8I. I3 spanS74..S7c lies beyond numericalrequest[S,S74); concrete backendcallsetsI0. No actual memoryfault/bug/allocator-size claim; intervaljoin conditional sameS. Opengates needr5=G/r4=I/currentG/frame afteracquire andr4result/frame afterunlock. Default validator can write Pythoncache; Root ran only envPYTHONDONTWRITEBYTECODE=1; new397fixes own default pattern.

- E-XE164-401 VERIFIZIERT: Independent rawPT_LOAD224words/3pools/12relocs confirms Initvector/publication, unsignedOpen gate/S0→freshS1, I3numericinterval andbackendI0. EnumeratescurrentGP/frame/memory premises. Discovers390ordinaryPythonimportcreates__pycache__, so unqualifieddefaultreadonlyclaimfalse; generatedcache removed, frozenmanifestrestored. r5/r4/currentstate preservation conditional, not ABI. No actualbugclaim.

- E-XE164-402 VERIFIZIERT: 283 words/8 pools bind Update210, Set15, Get14, Count2 and14 PLTs. Three initial12B rows map entries0/1/2 to1/2/3; Set changes only row+8. Update eight nonnull gates precede calls. Raw VST Rm13 advances16 then Rm15 stores8, yielding24B span. Current opaque state is conditional; preserved null RAIL descriptor rejects before main Update loop, so earlier389 local GetCnf success is not whole Update success. No runtime mapping/ABI.

- E-XE164-403 VERIFIZIERT: Independent raw283word/PT_LOAD audit confirms three initial rows, unsigned setters/getters, eight Update null gates and VST writeback24B span. Numeric source relationships only; opaque call effects/current GP and runtime ownership remain open.

- E-XE164-404 HYPOTHESE: 86words/6pools;19 actual-entry fixtures430steps241events exercise Set/Get/Count and all-null Query against actual three initial mapping rows, two stages before/after row+8 setter. Synthetic memory/PLT bindings; non-S SUB preserves seeded NZCV. Selected source model does not establish process memory or runtime calls.

- E-XE164-405 VERIFIZIERT: Independent source/predicate/PC/event/frame review agrees with19 routes and setter-only word8 changes while initial entry mapping remains unchanged. Not a second complete independent ALU engine; fixtures and runtime binding remain conditional.

- E-XE164-406 HYPOTHESE: 23raw words/15 full Open fixtures cover indices0..3, rejection4/ffffffff, fresh state after acquire, and index3 numeric request-boundary read before stores; explicit GP/frame/opaque events. Index3 unmapped fixture is a modeled boundary, not actual allocation fault. S0/S1 may differ; negative current r4/r5/result clobber controls retain conditional premises.

- E-XE164-407 VERIFIZIERT: Independent initialized-memory/raw-control/event audit confirms15 Open routes, state reload after acquire and index3 boundary. No full independent ALU engine, allocator extent, real lock semantics or runtime identity claim.

- E-XE164-408 VERIFIZIERT: 274words/14pools: producer247, cleanup15, four PLTs. Kind1 builds one-hot masks; Kind2/5 position V and Kind4 group D/A fields are raw source relationships. Cleanup clears outer+8 before free-named call. Opaque allocation/current-register premises explicit. Group capacity48 has no local bound check; initial count not proved zero. No reachability of earlier N0 fixture or actual bug/ownership claim.

- E-XE164-409 VERIFIZIERT: Independent raw274word/arithmetic/store audit confirms producer masks, numeric request sizes, group append positions and cleanup outer-slot order. Not full CPU replay; allocation effects, initial group count and whole-object ownership remain open.

- E-XE164-410 HYPOTHESE: 321words/14pools;64 full producer fixtures enumerate16 n values/K0,7/two biases, and16 separate read/write helper entries consume the actual generated records. Existing eight-slot array and synthetic source memory stipulated. Separate helper invocation is not actual native caller chain; selected corner helper coverage only.

- E-XE164-411 VERIFIZIERT: Independent raw source, masks, event/formula/stack/gate audit agrees with64 producer and16 helper histories. No second full independent CPU reexecution or actual allocator/ABI/runtime claim.

- E-XE164-412 VERIFIZIERT: 181words/7pools bind ReadWrite request40184b01 with24B sixword stack vector, Command401c4b02 with28B sevenword vector, and Open40084b03 eightbyte configuration10010000002d3101. Requests/bytes are numeric call positions, not kernel UAPI. Nonnegative ioctl outcome requires current r4=0; Open malloc stores require current r6/r5. Device string is read only, no device operation.

- E-XE164-413 VERIFIZIERT: Independent181word/7pool/8relocation audit confirms vector widths/positions, status-byte initialization, signed return branches and Open configuration bytes. Current GP/frame conditions remain necessary; no actual ioctl provider, ABI, errno implementation or device execution.

- E-XE164-414 VERIFIZIERT: 562words/42pools bind SCPU G34018, Open/Exchange/Command/Init source and three SPI PLTs. Command568B frame builds requests/reply and tags0..10 receive lengths, passing five-position numeric SPI_Command vector. Init and Exchange not fully replayed; helper92c8 and clock/config/boot/reset/system effects unexpanded. SPI-only substitution is not a complete Init boundary. Artifact command strings never executed.

- E-XE164-415 VERIFIZIERT: Independent PT_LOAD562words/42pools, G34018 equations,11 stubs, frame and three SPI GOT targets confirm bounded caller vectors. No full CPU replay, actual transport binding, response semantics or runtime/hardware effect.

- E-XE164-416 HYPOTHESE: 324words/14pools;48 full producer cases4008steps plus960 helpersteps generate malloc16 Kind2/5 records across banks/flags/masks/two biases and consume generated records in separate helper entries. Allocator normal return, preserved current GP/frame/input bytes and output memory are explicit fixtures, not ABI. Helper entries are separate invocations. Source allocation validity unknown.

- E-XE164-417 VERIFIZIERT: Independent raw/predicate/recorded-ledger/formula audit supports selected Kind2/5 records and helper outcomes. REJECT only-SP+c postcall-read claim: numeric PC>=return filtering misses backward branches c284/c224/c268. Original no-op route assertion adds no evidence. Frozen review retained;416 supplies event-order correction. No second full CPU.

- E-XE164-418 VERIFIZIERT: Event-order audit finds12 postopaque reads per48case: SP+c, source+d/source+12 and nine saved frame words. Actual values derived from fixture initial bytes and prior stack writes. Outer0/4/c preservation is output postcondition rather than subsequent source read.407 already explicitly supplies required input/frame premises; correction concerns413 review, no actual allocator ABI.

- E-XE164-419 HYPOTHESE: 90raw words/15 full ReadWrite/Command fixtures cover null/negative handles, positive ioctl outcomes, errno branches/logger mutation and current-r4 clobber counterexample; exact24/28B buffers. Frozen412 event contract omits saved-frame preservation and explicit logger errno-memory effects; results require stronger implicit memory premises. Fixture.handle incorrectly derives final r0 in successes;419 corrects label and contracts without changing histories.

- E-XE164-420 VERIFIZIERT: Independent raw/predicate/critical-ALU/PC/args/results review agrees with15 source histories and identifies missing saved-frame and errno-memory opaque premises. Original modeled memory implicitly survives calls; no actual callee preservation. Corrective419 pending independent420 before promoting explicit boundary completeness.

- E-XE164-421 VERIFIZIERT: 122raw words/4pools/13opcode halfwords bind four callfree codec bodies. Noargs zeroHalf@O2 precedes opcodebytes; OneArg stores then reads currentArg halfword. Reply status storeE44410+Tag precedes gate, truncates count8bit, uses fullExpected, and raw NEON Rm13 load/store eachadvance16. Reply lacks local Tag/R guards; getter guard does not apply to decoder. Alias order and unsigned vector gate are numeric source behavior, not public protocol/API/actual buffers. Source only, fullmodels separate417.

- E-XE164-422 VERIFIZIERT: Independent122word/4pool/13halfword/PT_LOAD review confirms encoder order and Arg=O2 alias, status-before-gate, unsigned copy predicate and both NEON Rm13 writebacks/counts. No public API/tag names, complete protocol, runtime binding, pointer validity or hardware semantics.

- E-XE164-423 HYPOTHESE: 15 unchanged SPI histories and26explicit opaque events now bind actual pushed SP20/SP24 words, normalreturn/currentSP, currentGP and errno pointer/readableword effects including logger mutation. Entry_handle now reflects inputr0. 420 finds current_register_reads omits r0 consumed by actual CMP r0,r4 afterioctl; return value exists in traces, outcomes unchanged. Canonical consumed set requires BOTH currentr0/currentr4. These are synthetic per-event premises, not actual callee effects/ABI.

- E-XE164-424 VERIFIZIERT: Independent source/initialmem/event-order audit confirms15 matching baseline histories,26opaque contracts, savedframe POP values, logger errno writes and inputhandle correction; pins CMP e1500004 consumingr0 AND r4 atbothioctlreturn sites. Rejects419 only-r4 consumed-register completeness statement; traces/results agree. Actual errno/ioctl/ABI/device effects remain open; no new CPU/nativeexecution.

- E-XE164-425 HYPOTHESE: 113raw bodywords/4pools/13opcode halfwords;63 full selected traces plus two separate shared-E entries cover alltags, rejects, Arg=Out2 alias, Reply status/count gating, N1/7/8/9/16/255, scalaroverlap and inplaceNEON, rawRm13 writebacks16. Reject frozen report noargs temporal description: actualzeroHalfO2 precedes opcodebytes. Three source-pin paths omit xe164-analysis;421 binds correct existing files/hashes. Modelresults/validator usecorrectsource, broad63routes same-modelreplay; nofullindependentCPU.

- E-XE164-426 VERIFIZIERT: Independent raw eac4STRHzero beforeead0LDRH/ead8/eadcSTRB and selectedtrace checks confirm trueorder. Three malformed417paths corrected by bound actualfiles. N25531vectorpairs+7scalarpairs and two aliases spotchecked. No complete second CPU engine. Frozen417report/orderandpathledger retained as errata; finalbyteoutcomes unchanged. Noactualprotocol/ABI/runtimeclaim.

- E-XE164-427 VERIFIZIERT: Six-stage private synthesis separates manager/provider/ffi/SSC/SCPU/kernel evidence and open contracts. NumericSPIvectors24/28/8B do not establish kernelUAPI or completeInitreplacement; no newarchitecture/APIdecision. Only12 enumerated immutableinputs pinned directly; further cited WPs contextual, not wholefrozencitationchain (424). Statement helper92c8unexpanded historical to423;425 laterexpandsbody whileSPI_Init/boot/effectsopen. NoendtoendKind4appendlink.

- E-XE164-428 VERIFIZIERT: Independent12input identity/sixstage claim audit confirms preserved lifecycle/runtime/kernellimits and conditionalobjectidentity; identifies unpinned contextualcitationIDs. NoCPUreplay or actual architecture/transport/runtimecontract.422report pinned asinterimcontextonly, nofullproducerclaim.423fullcitationchain not frozen byits12pins.

- E-XE164-429 HYPOTHESE: Six source-block compositions1/2/3appends×2biases start explicit existingD/A,N0 and halfcapacity48; storecurrentr8@A+2N thenincrementhalfN. Helper firstread arithmetic becomesA/A2/A4 versusseparateN0→A-2. NOTfullCPU. ActualbranchJ>11999reachesc284/appendthen c2c0→c504logger→c224; validJfollowsc3b4/c3f4. Noactualappend→validKind4consumerlink. GroupallocationrequirescurrentS+e afteropaque logger; fixturecapacitynotcheckedsourcebound.

- E-XE164-430 VERIFIZIERT: Independent247raw producerwords andexactbranchdecode confirmout-of-rangeappend/loggerlane; recomputes6fixtures andselector4pre-readorderA+2N-2. Noestablishedobjectidentity/nativecallchain;D0=48ishalfwordfixture, notfullword norenforcedcapacity. Opaquelogger/currentmemorypremisesexplicit.

- E-XE164-431 VERIFIZIERT: 97raw words/7pools/17BL/11PLT completehelper92c8..944b. FourG34018eq,32Bframe, selectedlocal0/3/6outcomes andsixSCPUCommandnumericpositions; true8B d16literal9450=0100000000000000. Opaque calls/currentGP/frame/state required; nofullCPU/ABI/effects. Historical423helper-contentgapclosed. SPI_Initbodylater428/429closed, wholeInit/boot/resetstillopen. Padding944cnotvectorliteral.

- E-XE164-432 VERIFIZIERT: IndependentPT_LOAD97words/7literals/17BL/11PLT/GOT/reloclabels,5PCeq andD16bytesconfirmselectedbranches/localreturnpaths. Calllabelsnotcontracts; currentstateandGPconditional. Thisclosesonebody'ssourcecontent, notactualinitialization.

- E-XE164-433 VERIFIZIERT: ExactSPI_Init DynsymELFa960size8/raw e3a00000,e12fff1e implementsMOVr0,0(noS),BXLR; noexplicitmemory/stack/BL/otherGPRwrites. ValidcurrentLR/interworkingneeded. ActualGOT33250runtimebindingunknown; onlywhenboundlocalbodycan425SPI_Initopaqueeffectsberefined. Wholeboot/init/resetnotclosed.

- E-XE164-434 VERIFIZIERT: IndependentDynsymFUNC8B/uniquePT_LOAD/rawA32field/REAidentity/inventoryaudit confirmsMOV0withoutflagwrite andBXLR, noexplicitmemorycall. CurrentLRtarget/statepremise andruntimeGOTbindingremainopen; noactualnative/deviceexecution.

- E-XE164-435 VERIFIZIERT: 262raw words/28pools/39BL identify16PLTtargets+2local9618/9a78 in complete1048B Bootbody. G40028 distinctSCPU34018. Artifact/dev/ttyKbus numericopen0x102→isatty/termios/write/select/read/close chain and selectedD5/DA bytegates are present;216Bframe/configthreshold10000000. Source/callvectors only; no actual TTY opened. CurrentGP/frame/errno/bytevalues acrossopaque calls conditional. D8rawwords0/4000 notactualtimecontract; 430 itself does not expand9618/9a78;9a78 source already retained370/379 and selectedcalls384/386.432 newly scopes9618;433 joins retainedorchestrator/currentboot.430/431 is fresh narrower source/call-vector review, not new discovery of allbootbytes. SPI3callsalone do not cover this observedchain.

- E-XE164-436 VERIFIZIERT: Independent rawPT_LOAD262word/28literal/39BL/16PLT+2local audit confirmsG40028, path/configbytes, numericguards and selectedhandshakepredicates. VLDRa618+8+268=a888 givesraw0/4000words. NotfullCPU/actualserial/protocol/firmwareoperation. Two localhelpers/currentopaqueeffects/loadedruntime stillopen. NoWP430orolderpackagechanges.

- E-XE164-437 VERIFIZIERT: Four exactFW31 readonlydebugfs inode dumps bind modules.builtin/modinfo/devname/alias under6.6.94-rt56-w05.08.02. builtin lists drivers/spi/spi-kbus.ko and matching spi_kbus path/description/license/major parameter fields. Metadata candidate only; .ko listedbuilt-in isnotseparateloadedmoduleproof. Noactualkernelstart/device/major/UAPI/ioctl/TTYbinding ordriverimplementationcontract. Author/addressstringhitsnotinterfaces; /boot/linuxinventoryonlyin434, later437extracts.

- E-XE164-438 VERIFIZIERT: Independent fullimage/inventoryhashes+temporarypartition/debugfs stat/dump reproduceall4files byte-for-byte,10boundedhitsandspi_kbusfields; packageinventoriesunchanged. devnameonlycuse/uinputandnoaliasmatcharefinitefileabsence, notglobalbindingabsence. Artifactsnotactivekernel; nojoin408ioctl/430TTYtospi_kbus. Header/licensefieldnotrightstobroaderredistribution.

- E-XE164-439 VERIFIZIERT: Boota75c calls retained370orchestrator9a78 (595words/noncontiguous172Bgapexcluded) withcurrentSP20/[SP14], pre-store1@G40028. Orchestratorsavesargsandcallsreader97f0with0/SP38/SP3c; selectedreaderretffffffff→localhelperret0→callerconditionalstore2. Requires normalnestedreturns/currentframes/r4andnowritetoGfororiginal1→2stateclaim. Noactualreaderselection/payloadtransfer/protocolsuccess. Reuses370source, notnew638wordcontiguousacquisition; staticfile/compositeidentitiesnotruntime.

- E-XE164-440 VERIFIZIERT: Independent rawsource joins430→370→reader, pinscall9ae0/test9ae4/-1branch9ae8→a208local0 andcallerNEstore2; staticpayloadcandidatebytesagree. OriginalG40028/prior1needintactsavedr4/frame/nointerveningwrite. Non-minus1readerroutesoutsideboundedclaim; noactualserial/nativeexecution.

- E-XE164-441 VERIFIZIERT: ExactFW31inode50/boot/linux8213856B SHA f6e03d6452e4648cd86f58ff5c869af0ebdcc6e8f3123458c73d6e81ccfede65 extractedreadonly. uImage64B CRCS75c25a9e/5f20e326and8213792payloadcheck; innerARMzImage magic016f2818/endlengthcheck. Outercompression0notuncompressedkernelproof; LZOsignatures467cstaticliteral/488ccandidateclassificationonly, no validstream/decompression yet. Noactualkernelstart/driverUAPI. Directsourcebytebasis, notruntime.

- E-XE164-442 VERIFIZIERT: Independent image/inventoryhashes+freshreadonlydebugfsinode50dump byteequal; alluImagefields/CRCs,zImagemagiclengthandLZOoffsetsrecomputed,inventoryunchanged. Hostfile'slzopclassificationat488cisheuristiccandidate, notstreamvalidity/decompression. Noactivekernel/driverbinding/deviceeffect.

- E-XE164-443 VERIFIZIERT: 108raw selectedcodewords9618..97c4/10literalwords and18BL bindserialconfigslice. Callerinputr0/r1savedr8/r5;120Blocalzerofootprint with4Boverlaps52..55/112..115; fourconfigurationcallsplusmemcmp=5primarycalls. No matchingnewREAextent; boundedrawslice notproviderfullbodyrecord. PUSHr4-r8/LR=6wordstotal+120local=144Bframe. Currentr5/r6afteropaque tcgetattr neededforcfsetspeed(SP,14); laterFD/buffer/returnstatesconditional. MatrixC3fourprimarycountincorrect (5). NoABI/actualtermioslayout/baudunit/deviceeffect.

- E-XE164-444 VERIFIZIERT: Independent rawslice/BL/PT_LOAD/caller review confirms120Bzeroingwithtwo4Boverlaps, signed-negativeandmemcmpreturnlanes. Specifies6savedwords andfiveprimarysites; currentr5/r6/r7/r8premisesexplicit. Noactualtcgetattr/cfsetspeedeffects/realbaudmeaning/runtimecall. No providerextentconfirmation. Frozen432ambiguousprologueandmatrixwordingqualifiedwithoutmutation.
