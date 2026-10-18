> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-177 report

## Result

The pinned own-provider sources directly assert the bounded model's input/output cycle behavior, selected device-specific calls, provider acquisition non-nullness, and parts of own-model status/error and safety reactions. Assertions around initialization/lifecycle, manager registration, complete interface shape, and surrounding services are only indirect with respect to the WP174 original-stack boundary. No supplied assertion covers the physical K-Bus/XE164 interior.

This classification describes source text only. Every cited assertion is in an own adapter, own bridge, or synthetic descriptor test. None is evidence that the assertion ran, that an original consumer called the provider, or that original runtime or hardware behavior is reproduced. All test statuses are `NOT_RUN`.

## Phase reconciliation

| WP174 phase | Classification | Static observation and exact assertion/setup locations |
|---|---|---|
| Replacement cut / provider | INDIREKT | Own tests acquire `adi_GetApplicationInterface()` and assert non-NULL (`tools/adi_digital_adapter_test.c:507-512`, `tools/adi_model_bridge_integration_test.c:88-101`). They exercise selected callbacks but make no complete 34-slot table/layout or ABI assertion; coverage of selected behavior is detailed in the cycle and dispatch rows. |
| Init and registration | INDIREKT | Own adapter `Init`/`ScanDevices` and device opening/configuration are asserted (`tools/adi_digital_adapter_test.c:507-522`); bridge integration exercises concurrent own `Init`/`Exit` and socket liveness (`tools/adi_model_bridge_integration_test.c:59-85`). No supplied test asserts IoDrvDal configuration parsing, component registration positions, dynamic library selection, or original-manager callback binding. |
| ReadInputs cycle | DIREKT | Own callback assertions cover start/read/end, latched input bytes, bit extraction, bounds, task selection, and repeat-end failure (`tools/adi_digital_adapter_test.c:129-148`). Digital-8 and Digital-16 defaults assert masking and byte order (`tools/adi_digital_adapter_test.c:346-353`, `tools/adi_digital16_default_test.c:34-39`); bridge integration checks byte and word delivery (`tools/adi_model_bridge_integration_test.c:110-117`, `:156-168`). These do not assert the original consumer's complete transfer sequence. |
| WriteOutputs cycle | DIREKT | Own callback calls assert staged publication, rejected transfer, frame completion and requested/effective values (`tools/adi_digital_adapter_test.c:151-186`, `:230-236`). Default tests assert Digital-8/16 output values (`tools/adi_digital8_default_test.c:36-46`, `tools/adi_digital16_default_test.c:50-68`); bridge integration checks published status (`tools/adi_model_bridge_integration_test.c:121-125`). No assertion binds these to original consumer callback positions. |
| Push / provider reaction | DIREKT | The own VCall wrapper is explicitly declared as an own wrapper, with assertions for Push inner result in healthy/fault paths (`tools/adi_digital_adapter_test.c:19-29`, `:328-344`, `:388-413`). Bridge integration asserts outer DAL success separately from inner `DAL_FAILURE` (`tools/adi_model_bridge_integration_test.c:126-135`). This directly covers own exposed behavior; it does not test original provider internals or the original callback's pointer-result mechanics. |
| DeviceSpecific Call / VCall | DIREKT | Direct calls assert terminal-info32 bounds/content and READ_TAB_9 values (`tools/adi_digital_adapter_test.c:73-116`); Digital-8 profile and own VCall wrapper assert corresponding selected calls/results (`tools/adi_digital_adapter_test.c:304-344`). Unknown-name and unsupported UID paths are asserted (`tools/adi_digital_adapter_test.c:238-279`). Original DAL dispatch completeness, slot-29 ABI and unsupported-operation reachability are not asserted. |
| Status, validation and error paths | DIREKT | Own tests assert invalid arguments, transfer bounds, fault diagnosis, watchdog/permit gates, distinct outer/inner results and fault recovery (`tools/adi_digital_adapter_test.c:118-127`, `:169-203`, `:238-283`, `:388-415`; `tools/adi_model_bridge_test.c:232-260`). Descriptor tests assert declared-width and malformed-input handling while explicitly keeping process-image/register contract OFFEN (`tests/test_native_descriptor_contract.py:22-67`). Numeric values remain assertions, not inferred manufacturer semantics. |
| Lifecycle and surrounding services | INDIREKT | Own adapter close/reopen/exit/reinit and bridge concurrency/liveness are asserted (`tools/adi_digital_adapter_test.c:463-547`, `tools/adi_model_bridge_integration_test.c:59-85`, `:136-175`). These do not assert original Init-to-Exit ordering, Close callsites, watchdog order, manager rollback, or parallel original services. |
| Physical K-Bus/XE164 interior (explicit exclusion) | KEINE | No supplied own-provider test asserts a physical bus transaction, register map, XE164 protocol or device response. The descriptor contract tests explicitly avoid claiming native process-image/register contract (`tests/test_native_descriptor_contract.py:22-29`). |

## Classification rule and interpretation

`DIREKT` means at least one pinned own-provider test contains an assertion of the named bounded reaction at the provider/model boundary. `INDIREKT` means adjacent own-provider behavior is asserted, but the specific WP174 original-manager, registration, or lifecycle reaction is not. `KEINE` means no supplied test assertion addresses the phase's named reaction. A row may therefore be direct for an own model behavior while still leaving original-provider semantics open; see Push and dispatch rows.

The separately pinned WP062 inventory is contextual and was not treated as a substitute for reading the seven supplied source files. The evidence index and WP174 matrix remain the scope authority. No implementation source was used to infer a contract.

## Tooling and status

- `rg 15.2.0 (e89fff89ac)`; `python3 3.13.5`; GNU `sha256sum 9.7`.
- Method: hash-bound local text inspection with `rg`, `nl`, `sed`, `sha256sum`, and `wc`; no build or test command was run.
- Findings: `VERIFIZIERT` as to source presence, line locations, and classification under the stated rule.
- Test status: `NOT_RUN` for every referenced test source.
- Alternative explanation: these tests may have been designed only to pin own-model contracts and transport fixtures, not to cover the original-stack phases. Lack of an assertion here does not prove the repository has no other evidence or test; this assignment is limited to exactly the pinned sources.
- Residual uncertainty: tests were not executed; assertion behavior can be disabled by build configuration; no inference is made about test discovery, current build graph, original callback ABI, dynamic binding, runtime or hardware.

## Outputs

Created in this work-package directory: `assignment.md`, `report.md`, `coverage-matrix.tsv`, `uncovered-cases.tsv`, `validate.py`, and `SHA256SUMS`. Their hashes are recorded in `SHA256SUMS`.

SHA-256 of generated artifacts (the report's own digest is in `SHA256SUMS`):

| File | SHA-256 |
|---|---|
| `assignment.md` | `80b9c177b3b9bb1c5046603c43e3ea27364b6ca5ac5419115e916bf283b1547a` |
| `coverage-matrix.tsv` | `7e3d0cc67d21d86a067bbda421743cd22604477c38001e61fa88e4c914a87b43` |
| `uncovered-cases.tsv` | `a62c5ffdf70de902c31d7ed286262d29a2f4f32c1be38aeb1f36c6911e454047` |
| `validate.py` | `d7ce428eb1c7014b331361130eac4a3e77c11d91407449066bc53b2196725eba` |
