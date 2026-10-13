# Native Digital Tests, 13 October 2026

This report records bounded native Digital-8 and Digital-16 runtime tests and the separate offline Digital-16 project build. It does not report a hardware comparison. Module identities below refer to engineering descriptions used in the project, not verified physical module revisions.

## Digital-8: earlier provider run

**Result: PASS for the recorded native Digital-8 runtime scope.** The provider used for this earlier run was loaded by the original CODESYS runtime, native I/O manager, and original WAGO I/O drivers. Four input/requested-output patterns were processed. The observed input bytes were `0`, `129`, `90`, and `255`; the corresponding requested output bytes were `150`, `23`, `204`, and `105`. For every sample the model permit remained `0`, effective output remained `0`, watchdog status was `1`, fault status was `0`, and the provider remained opened, configured, and running. The frame counter advanced from `372` to `576` over the recorded samples.

This establishes native processing of model-provided input and requested output frames with the model-output gate closed. It does not establish physical output actuation, electrical behavior, general watchdog or fault semantics, or equivalence to physical 750-430/750-530 modules. The observed module data came from the model; the real module revisions remain **OFFEN**.

The original application was restored to STOP. The original runtime and driver binaries, application, CRC, and configuration were hash-checked; the post-restore read was recorded. Physical outputs remained blocked by permit 0. This run does not qualify native STOP behavior as a general lifecycle contract.

**Evidence:** Root's private runtime validation receipt records `PASS`, the four samples, process identity, original-file hashes, isolation snapshot, and restore check (receipt SHA-256 `8a80ebc695180ff1144a5fa752065590d734d9f4a1b137bd605187b4dd454ef8`). The staged own provider SHA-256 was `c4aa9da51b20722fb2bcb8f4a718d1624627a701507dd02209687fb5e4e49641`. The corrected-source regression below is separately bound; this earlier PASS does not cover that source. The public repository contains this bounded summary only; it does not contain raw private traces, local paths, credentials, or device identifiers.

## Digital-8: final corrected-source regression

**PASS** with the corrected full-width bridge and the eight-channel adapter profile. This run reused the earlier hash-bound own XOR150 BootAPP/CRC; it performed a fresh runtime trial with the corrected provider, with no new Digital-8 IDE build in this block. Original native RUN was confirmed; inputs `0/129/90/255` produced requested outputs `150/23/204/105`. Model permit stayed0; opened/configured/running and watchdog were1, fault0.

| Input | Requested output (XOR150) | Effective output | Frames |
|---:|---:|---:|---:|
| 0 | 150 | 0 | 389 |
| 129 | 23 | 0 | 457 |
| 90 | 204 | 0 | 519 |
| 255 | 105 | 0 | 582 |

The own FAULT observation reports requested105, effective0, fault1 and650 frames. It qualifies only the own flag and closed gate. Original application STOP restoration and seven unchanged hashes were independently checked afterward.

Provider SHA-256: `f4bacffbbbaf48bda97ef0a967d63fe08ca07194e323738ed6f930643e214c26`; raw trial SHA-256: `715881550851a9c88f642933c09fbfbee49e8844f1a43fb10e2993184baf605d`; private validation receipt SHA-256: `cfa03351915e5c748b70c4ca870c420c6f20fd54d816294dc2fa69486d0d618e`. The new eight- and16-channel binaries use the same corrected bridge source with different explicit default profiles. Their native PASS is separate from the older provider.

## Digital-16: offline native IDE project

**Offline build and read-only reopen: PASS.** Private receipt SHA-256: `bbc0725c0a5f8b5f960cb18e21de27b9dd42922333bac4823f25ce342057ed8e`. The source SHA-256 was `1b954ff156e2b1cedecd77a4e7152ee2ac774ef93da8b5cd65f5dc9c93d2cef6`; the native IDE builder script SHA-256 was `3de979a473c9ad5c20941352ece7777d1cab306929821ce8dd7ec1cc82448117`. The native IDE built an offline project with the engineering-description entries for 750-1405 and 750-1504, each at version `2.0.0.14`. The project mapped the two 16-bit parent words to the existing `InputWord` and `OutputWord` variables, with 16 child fields in each direction. The requested test transform is `InputWord XOR WORD#16#A596`. The build reported zero errors and warnings. A read-only reopen confirmed the cyclic task at 20 ms, the same module order and mappings, a byte-identical exported mapping, and unchanged project/source hashes. The TCM control parameter read back as zero in the offline project.

This verifies project generation, mapping persistence, build, and read-only reopen only. It does not verify target download, native runtime execution, module revisions, electrical behavior, or physical output actuation. The initial output permit configured in the project is not evidence that outputs were enabled on a device.

### Native Digital-16 runtime trial: first attempt

**Overall result: FAIL.** The native application ran through input values `0`, `1`, `129`, and `255`; requested output words matched `InputWord XOR 42390` (`42390`, `42391`, `42263`, `42345`). At input `256`, the own INPUT parser rejected the value because its maximum was 255. A separate `STATUS` mask of `0xff` was also identified in the own bridge code; that mask was not the cause of the `ERRCOMMAND` for input 256. The full 16-bit input range was therefore not accepted, and the trial did not meet the Digital-16 acceptance criterion. This was an own bridge parser/code failure, not evidence that the original runtime or a physical module rejected a valid WORD value.

Root restored the original application to STOP and verified seven original hashes unchanged. Physical outputs remained blocked. This is a partial native-runtime observation ending in a failed trial, not a hardware comparison or qualification of physical 750-1405/750-1504 modules. The real module revisions remain **OFFEN**.

**Evidence:** private V1 validation receipt SHA-256 `02331bf28391a748ef5124005ff63a120928b000e8afd1458348c129ccd046fa`; private raw-trial SHA-256 `892f251d1ab283771beb8a3de5918e58d511d087e38f46845ae298ca598195de`. The retry below uses a fresh source-bound provider.

### Native Digital-16 corrected-source runtime

**Result: PASS for native requested-output processing with model permit 0.** The corrected own provider ran through the original runtime, native I/O manager, and original I/O drivers. The eight 16-bit input patterns and requested outputs were:

| Input word | Requested output (`input XOR 42390`) | Effective output | Frames |
|---:|---:|---:|---:|
| 0 | 42390 | 0 | 406 |
| 1 | 42391 | 0 | 490 |
| 129 | 42263 | 0 | 574 |
| 255 | 42345 | 0 | 658 |
| 256 | 42134 | 0 | 737 |
| 32768 | 9622 | 0 | 805 |
| 42390 | 0 | 0 | 868 |
| 65535 | 23145 | 0 | 931 |

Across these samples permit stayed `0`, watchdog status was `1`, fault status was `0`, and the provider remained opened, configured, and running. Frame counts increased throughout. An additional own `FAULT` flag check at input `65535` produced `fault=1` while permit and effective output remained `0`; this checks only the own latched flag, not native STOP or general watchdog/fault semantics.

The original application was restored to STOP; the receipt records seven unchanged original hashes and a post-restore read. The isolation record confirms the bound own provider and original driver mappings, with no physical bus/device endpoints in the observed process snapshot. The isolated trial process had no physical module access. No physical module behavior comparison or actuator test was performed. These observations do not establish electrical behavior or equivalence to physical modules. Real module revisions remain **OFFEN**.

**Evidence:** private V2 validation receipt SHA-256 `0c5f7bf18969f61de8992a1c934a84d81f4226b5babf4d5daa61a12a1d139306`; corrected own provider SHA-256 `855a09bae90dfa1de54e47ffc02734e49813b93b674bb78204332481d76d216e`; raw trial SHA-256 `642eb280b506e844c3a3540cc371fc266a24e1e62800ba58059694d57419ec84`. The repository carries this bounded summary; private raw outputs and local identities remain in the owner's handoff.

### Corrected offline build history

The first offline IDE rebuild attempt **FAIL**ed: a hexadecimal UDINT literal used decimal maximum digits and was out of range. That attempt produced one compiler error and two warnings (failure receipt SHA-256 `0628ad864f51d9f04902e79c1a1ad7ec73dd1f47a012bc90fed51779e59b6891`); it generated no application and had no runtime execution. The source was corrected to the documented existing successful literal `UDINT#16#FFFFFFFF`. A read-only reopen of the saved source at the time of the failure was a separate PASS for source/TCM/mapping inspection only, not a build PASS. The later corrected offline build and reopen are the PASS recorded above; they remain separate from both native runtime attempts. No compiler PASS is attributed to the failed V1 attempt.

## Evidence and handoff boundary

The public Git repository may contain this report and the corresponding source/project-builder changes that have been explicitly selected for review. Private evidence remains in the owner's local handoff: raw IDE transcripts, project/application artifacts, runtime transaction output, validation receipts, hashes, and any device-specific records. Do not copy private addresses, credentials, device identifiers, vendor binaries, or unredacted traces into Git. The report does not embed private handoff paths or claim GitHub CI results.

Original runtime, native I/O manager, and original I/O drivers were retained for both digital runtime tests. No physical module behavior comparison is claimed. Physical outputs remained blocked. Real module revisions remain **OFFEN**. A corrected-source Digital-16 runtime PASS is recorded above, and the final corrected-source Digital-8 regression is separately recorded above.

## Local verification and remaining tests

All185 local hardware-free Python tests passed without skips, including actual own C transport/namespace tests. Fresh private ARM builds and three own harnesses (contract, shared-linked default16/monotonic, bridge integration8/16) passed in isolated local QEMU with GNU loader/libc; original IoDrv/Runtime were not used in those own harnesses. The native trials above provide a separate evidence level. The default16 harness requires a provider compiled with `VIRTUALWAGO_DEFAULT_CLOCK_MONOTONIC`; the integration harness uses its own logical clock.

[Bounded public evidence](../evidence/native-digital-tests-2026-10-13.json) binds sources, artifacts, failed attempts, actual samples, independent offline reviews and restoration receipts. Native active-model-gate/lease-loss/STOP tests, real hardware comparisons, module revisions and native analog/PWM/serial contracts remain open. The configured20ms task and frame counters are not an electrical or real-time frequency proof. Root paused the IDE VM to disk after offline use. CI remains hardware-free; its result must be checked against the exact pushed commit separately.
