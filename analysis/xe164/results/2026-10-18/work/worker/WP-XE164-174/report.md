> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-174 — evidence-bound replacement boundary

## Answer

For the demonstrated Digital-8/16 behavior, the smallest currently supported cut is the provider returned by `adi_GetApplicationInterface()`, with the original runtime, native manager and original I/O drivers retained. The virtual side supplies the selected model topology/configuration and cyclic process images. This is an evidence-backed bounded architecture hypothesis, not a verified complete K-Bus contract: E-XE164-070 and its integrated continuation E-XE164-110 are HYPOTHESE; E-XE164-068 records bounded native runs, while static consumer mechanics do not establish every callback's dynamic reachability. The cut must not be generalized to arbitrary modules, all services, active physical outputs or complete K-Bus behavior.

No physical K-Bus internal state needs to be reproduced to satisfy that bounded cut: the replacement point is above the physical transport, and the recorded native Digital-8/16 behavior used original manager/drivers plus the own provider. The provider processed model inputs and exposed requested-output values while permit and effective output stayed zero (E-XE164-068). The boundary synthesis explicitly says the demonstrated behavior does not require reproducing physical K-Bus/XE164 transport (E-XE164-070/110). This establishes a bounded model/provider seam only. The XE164 protocol remains OFFEN (E-XE164-008); broader profiles, services and physical/electrical behavior remain OFFEN/NOT_RUN (E-XE164-069/073/110).

## Evidence reading rules

- `VERIFIZIERT` here describes the bounded claim and method stated by that Evidence ID, often static source/binary scope. It does not imply runtime execution.
- `HYPOTHESE` stays a hypothesis. In particular E-XE164-201 is only a conditional IoDrvDal-to-generic-loader binding; no concrete dynamic DSO selection is established.
- Static, harness/source, native runtime and hardware tiers are separate. The reviewed package contains static evidence and a record of prior bounded native trials; it did not rerun a harness, runtime or hardware trial. The tests/assertions noted by E-XE164-071/072 are source inventory, NOT_RUN.
- Numeric returns and positions are retained as observed values/positions. No semantic API, structure or field names are inferred beyond names already present in the evidence.
- The matrix distinguishes required observable reactions for the bounded mock from open call binding and broader completeness questions.

## Boundary and limits

E-XE164-067 records 22 of 34 ADI slots as directly called or forwarded by the exact FW31 consumers. E-XE164-071 says the current own adapter assigns all 34 entries and implements each of those 22, but that is source scope, not ABI/runtime certification. The provider cut is therefore the smallest *currently evidenced* replacement boundary for the recorded Digital-8/16 behavior, not a claim that every slot, callback or module class is understood. E-XE164-069 explicitly retains the possibility of parallel service paths and does not prove that all XE164 behavior lies below the provider.

Within the bound, preserve the observed consumer mechanics: enumeration-to-open and local read/write Start-transfer-End order (E-XE164-079); distinct outer and inner DeviceSpecific results (E-XE164-078, E-XE164-090); the distinct Push result positions and the last-status overwrite behavior (E-XE164-091..094); and the provider's fail-closed requested/effective output distinction for the current model (E-XE164-074). The accepted static evidence does not supply a complete Init-to-Exit or watchdog sequence, Close path, full slot-29 contract, complete original Push binding, or physical K-Bus protocol (E-XE164-078/079/094; E-XE164-008).

## Explicitly retained uncertainty and rejected promotion

The exact configuration has `ConfigLibrary="libIoDrvKbus"` and `EntryFunction="IoDrvKbus_Init"`, but static configuration and artifact presence do not establish runtime load or execution (E-XE164-086, E-XE164-165). The exact IoDrvDal publication positions and generic loader path are statically observed (E-XE164-164, E-XE164-200); tying them to the same dynamically resolved `ComponentEntry` is conditional only (E-XE164-201 HYPOTHESE). The name spelling `libIoDrvDali` in another config record is a near-name discrepancy, not evidence of the target binding (E-XE164-165/168). No status meaning is assigned to numeric 2, 3, 17, 18, `0x10`, `0x20`, `0x40` or `0x70` beyond the exact bounded mechanics in its cited evidence.

E-XE164-106's `get_uid`/`read_conf_reg` path is an observed static dispatch with numeric status mechanics; the model-value branch in E-XE164-113 does not reach the four local read-conf calls for the listed high-bit values under its stated equality condition. E-XE164-107 leaves actual profile-bound dispatch reachability open and retains a conditional conflict hypothesis if those calls occur. Therefore do not claim either universal need or universal irrelevance for those operations.

The physical K-Bus internal protocol, module electrical reactions, arbitrary analog/PWM/serial classes, all manager/runtime services, active permit/effective-output cases, complete lifecycle, and complete DeviceSpecific VCall/slot-29 propagation are not required by the *bounded demonstrated Digital-8/16 cut*, but remain open for a general virtual K-Bus claim (E-XE164-008/069/070/073/078/079/094/110). No physical trial or hardware equivalence is claimed.

See [boundary-matrix.tsv](boundary-matrix.tsv) for the per-phase minimum and [evidence-coverage.tsv](evidence-coverage.tsv) for every cited ID's retained status and scope.
