> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-060 — Integrative original-stack boundary decision

## Result

**VERIFIZIERT, bounded scope:** The repository evidence already demonstrates
that the original runtime, native I/O manager and original WAGO I/O drivers can
process model-provided Digital-8 and Digital-16 inputs and corresponding
requested output frames while only the provider behind
`adi_GetApplicationInterface()` is replaced. The successful trials do not
emulate the XE164 firmware or a physical K-Bus. They therefore directly support
the intended goal: reproduce the interface visible to the preserved stack and
behave like a bus exists behind it.

**HYPOTHESE, architectural scope:** The 34-slot ADI/DAL provider seam is the
smallest currently evidenced replacement cut for that bounded digital use.
The seam itself, its 136-byte table copy, 22 observed slot uses and the native
Digital-8/16 behavior are evidence-backed. Its completeness for every original
stack feature is not. `libIoDrvKbus` retains parallel diagnostic and D-Bus
dependencies, and an earlier isolated startup exposed board-metadata/signature
dependencies outside the ADI table.

The operational classification is in `boundary-matrix.tsv`. Its essential
consequence is:

- Broad XE164 decompilation is no longer on the critical path for a bounded
  virtual digital K-Bus.
- Further XE164 analysis is justified only by a named upper-boundary gap that
  cannot be resolved in the exact ARM consumer/provider evidence—for example a
  register operation, timing/error behavior or module class that must be
  reproduced below ADI.
- The next useful static work is consumer-facing: close exact lifecycle,
  error, topology and parallel-service requirements, then audit the existing
  provider against that reduced contract.

This is not a proof that every XE164 path lies below the substituted boundary
or is irrelevant. The accepted E-XE164 evidence simply yields no additional
ADI signature, layout, phase, error or lifecycle requirement. Parallel
libpackbus/UIO/D-Bus/diagnosis visibility remains **OFFEN**.

## Observation, conclusion, unknown

### Observation

The exact FW31 `libIoDrvDal.so.1.0.2` and `libIoDrvKbus.so.0.0.1` evidence
reports indirect use of 22 ADI slots after the later VCall continuation. The
core digital path covers initialization/enumeration/open, type-III
configuration, framed bit/byte reads and writes, diagnosis, application state,
device-specific calls and watchdog operations. The installed `libdal` provider
is byte-identical to the separately inspected FW30 artifact, but the consumers
are distinct FW31 builds.

The recorded native trials are a separate, stronger evidence stage for the
bounded end-to-end behavior: original runtime + original manager + original
drivers accepted the own provider, consumed 8- and 16-bit input patterns, and
produced the expected requested outputs. Effective outputs remained zero
because the model gate stayed closed. These runs do not expose an exact
per-slot trace and do not validate physical or electrical equivalence.

### Conclusion

For the user's stated target, implement and validate the behavior seen at the
ADI seam rather than the internal K-Bus transport. The virtual model must
provide topology/configuration responses and cyclic process images, not replay
XE164 decisions. The original stack remains responsible for CODESYS mapping,
driver logic and PLC decisions. Model inputs, requested outputs and effective
outputs remain separate.

### Unknown

The following prevent promotion to a general K-Bus contract:

1. complete startup/rollback/close order and exact failure propagation;
2. callback threading, reentrancy and post-unregister lifetime;
3. full device-specific opcode and result behavior, including Push, UID and
   registers for arbitrary configurations;
4. complete diagnostic/D-Bus and board-service closure;
5. native active-output permit, lease loss, STOP/restart and watchdog-expiry
   behavior;
6. analog, PWM, serial, retain/time and multi-instance/concurrent behavior;
7. rights and deployment constraints for the exact original stack.

## Evidence binding

Inputs were read-only and rehashed before use:

| Input | Bytes | SHA-256 |
|---|---:|---|
| `docs/adi-contract-2026-10-12.md` | 23771 | `c3133e5269de7be5ac887ea1c126fde72b97ef9224b25f582b678446dcd9db9d` |
| `docs/adi-digital8-continuation-2026-10-12.md` | 7912 | `defe2e9da7e747674f32d37a9e17ff3bbfd52167b1d9405358263d9878f367c8` |
| `docs/native-cyclic-2026-10-12.md` | 6346 | `e7321024431727d710f6087d7c7588d9c2951a44c7692df0216ff6cc428e4c19` |
| `docs/native-digital-tests-2026-10-13.md` | 11184 | `1bc47976a9042ba4d82d44ee5b88bffe01b61ee73163b4baeefad75f03370135` |
| `docs/runtime-bridge-2026-10-12.md` | 8538 | `a2b55f2e1bb1d7139910fa777d369c58190c21d9669ee135f2d0ffa5f67ee538` |
| `docs/adr-0001.md` | 11540 | `7f979ff2414c0fee2fe21a7c579c52d78a8f760ad8a3b67f620831c11278a284` |
| `docs/next-originalstack-block.md` | 10069 | `ab401666205b37d093b24a4b5d18b0011681ba531fe99ea39d5733b3feb6db98` |
| `DERIVED-XE164-COMPOSITE-E00000` | 17110 | `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983` |

Relevant accepted private firmware evidence is E-XE164-001 through
E-XE164-066. Those items establish only the exact FW30 bytes and bounded static
loader/startup/function observations. E-XE164-008 itself keeps an end-to-end
K-Bus protocol reconstruction open; absence of that reconstruction does not
invalidate the separately demonstrated higher ADI replacement path.

## Method and review

Method: integrative static reconciliation of hash-bound reports, accepted
private evidence and the already recorded native evidence. No new REA operation
was run because the decision asks whether the already accepted lower-firmware
evidence adds a consumer-visible requirement; repeating the same binary
operations would add no prerequisite. No manufacturer binary was executed.

Tests: input size/hash checks **PASS**. Native results cited here retain their
original revisions and scopes; they were not rerun. Device, network, VM,
runtime and hardware tests in this work package are **NOT_RUN**.

Review: GPT-6.1 SOL root **Self-Review**. Worker reports are separate inputs
only after explicit root acceptance; they are not hardware/runtime evidence or
independent review of this decision.

Accepted worker inputs after root review: WP-XE164-057 corrected the historical
21-slot table to the later 22-slot scope while leaving the missing VCall
address/hash details open; WP-XE164-058 separated native behavior from own
provider telemetry; WP-XE164-059 supplied the conservative negative
countercheck stated above.
