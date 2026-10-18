> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-289 — own adapter and bounded provider-contract reconciliation

**Result:** The own C source has a safe range predicate whose accepted-request arithmetic is equivalent to the provider’s bounded unsigned range gate only under an explicit uint32 operand mapping. The artifacts do not establish that mapping, a shared table layout, or that the six named own function members implement provider positions `+0x30/+0x3c/+0x40/+0x44/+0x50/+0x54`. Broader differences in state, callbacks, and transaction effects are separate from that arithmetic result; the evidence does not make them a compatibility requirement or defect.

Repository: `REPOSITORY_ROOT`, clean at HEAD `e56bb8ed488137f3d9276bfcbec6f33d2917114a`. Read-only scope was `tools/adi_digital_adapter.c`, `.h`, `tools/adi_digital_adapter_test.c`, `tools/adi_digital8_default_test.c`, and `tools/adi_digital16_default_test.c`, plus required project documentation. Source sizes and SHA-256 values are in `source-pins.tsv`. The included `<dal/adi_application_interface.h>` supplies the external table declaration; no exact included-header/build-offset pin was available in this evidence package to bind own named C members to provider numeric offsets. The adapter header describes these as an own in-memory model. `DAL_SUCCESS`/`DAL_FAILURE` remain dependency macro tokens here; their numeric expansions are not inferred.

## Range arithmetic

The output byte path (`adapter_write_bytes`, `adi_digital_adapter.c:470-494`) rejects when `offset > output_bytes` or `size > output_bytes - offset`; the input path (`:570-588`) uses the corresponding `input_bytes`. The subtraction is reached only after `offset <= capacity`, so it cannot underflow. Both arguments and capacities in these functions are `uint32_t`. A zero size succeeds after the range and pointer checks; a null data pointer is rejected only for nonzero size. An invalid byte range latches this model’s fault before returning its failure macro.

The corrected provider write-side sized body at relative position `+0x3c` is summarized in E-XE164-296: let `a=current r5`, `b=current r6`, `s=u32(a+b)`, `m=max_unsigned(a,b)`, and `L=word[current third-return+8]`. The local range gate passes when `m<=s && L>=s`; current `r7` is forwarded only after the gate passes, not included in it. E-XE164-302 describes the read-side sized candidate at `+0x50` with a callback-null test before reading its length at current third-return `+4`, then the same unsigned `r5/r6` sum gate. These remain numeric, current post-opaque-call values; the reports do not name them offset, size, or capacity.

Under the explicit identity `a=offset`, `b=size`, `C=capacity=L`, the acceptance predicates are equivalent:

- Own C accepts iff `a<=C` and `b<=C-a`, equivalent to the mathematical integer inequality `a+b<=C`.
- Provider `m<=u32(a+b)` first excludes 32-bit addition overflow. If `a+b` overflows, the wrapped sum is strictly smaller than `max(a,b)`, so this test fails. Without overflow, `max(a,b)<=a+b` holds. The second provider test then reduces to `C>=a+b`.

The validator checks this proof with exhaustive small uint32 triples and boundary values including zero, exact-capacity, `UINT32_MAX`, and wrapping sums. The conclusion is conditional because the provider uses current registers and a word loaded from an opaque returned pointer, while the own adapter uses explicit caller parameters and profile capacities. No evidence equates these values or proves the provider position is reached for this adapter.

## Six positions and caller-visible behavior

`position-reconciliation.tsv` separates source facts for each side. E-XE164-296 (corrective accepted WP276 review) covers write-side positions `+0x30/+0x3c/+0x40`; E-XE164-302 (accepted independent WP285 review) covers read-side positions `+0x44/+0x50/+0x54`. Their body paths have three helper-result zero gates that locally return `0xffffffff`; later simple callback slots can return `1` when null, and sized slots conditionally reach `BX` after unsigned gates. Helpers, callback targets, table publication, runtime binding, and ABI semantics remain outside those body reports.

The original consumer summaries constrain only local use of each return: on WriteOutputs, `+0x30` nonzero maps to caller return 2 and zero continues; `+0x3c` enters the local status flow where the latest qualifying result maps to 0/2; `+0x40`’s returned `r0` is overwritten before local use. On ReadInputs, `+0x44` nonzero selects a local result 2 and zero continues; `+0x50` contributes to later status processing; `+0x54`’s `r0` is overwritten. These are caller requirements on the observed path, not mandates that the own adapter’s operations reproduce provider internals. A discarded `r0` does not prove a callee is effect-free. WP200’s `+0x58` belongs to a separate list-entry context and is not joined to getter-object `+0x58` or the six cycle positions.

The own interface initializer assigns its named function pointers directly (`adi_digital_adapter.c:860-879`). Own `WriteStart/WriteBytes/WriteEnd` implement a same-thread/task/generation-owned staged-frame transaction; `ReadStart/ReadBytes/ReadEnd` snapshot, copy from, and close an input latch. Invalid reads/writes can latch the own model fault. The write end publishes only after the touched-bit mask covers the selected output mask, then calculates effective output from own app/permit/watchdog/fault gates. None of that behavior follows from numeric provider offsets, and no source evidence in this task requires extending the own code to mimic every helper/callback gate.

## Existing source-assertion coverage

The byte-specific cases actually present in the source tests are listed in `test-coverage.tsv`. They include a successful full two-byte transfer, a successful one-byte profile transfer, an invalid `UINT32_MAX` offset with positive size, wrong-task rejection, duplicate end rejection, incomplete staged-frame rejection, and fault behavior after invalid byte/bit operations. The test files were inspected only. Project builds and tests were **NOT_RUN**. The source assertions do not cover all exact-end/just-over-capacity/zero-length and near-wrap cases, so no coverage claim is made for those tests.

## Status and verification

- **VERIFIZIERT:** repository/source hashes; own function-pointer assignments and local state/range guards; bounded assertions present in the listed test sources; mathematical uint32 range equivalence under the stated operand identity.
- **HYPOTHESE:** any mapping from the own six named members to the provider’s numeric offsets.
- **OFFEN:** exact public header version/build layout linking those offsets, runtime object/table identity, actual consumer invocation, provider helper/callback effects, and wider behavior compatibility.
- **NOT_RUN:** builds, unit tests, runtime, device, hardware, VM, and network actions.

The read-only validator checks all source/report pins, checks source anchors for the predicate, interface assignments and recorded tests, and validates the arithmetic equivalence against boundary/exhaustive synthetic cases. It is a consistency self-check, not a build or test run and not an independent review. Run from the XE164 research root: `python3 work/worker/WP-XE164-289/validate.py` and `sha256sum -c work/worker/WP-XE164-289/SHA256SUMS`.
