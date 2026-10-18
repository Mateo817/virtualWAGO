> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-070 — bounded acceptance and repair synthesis

## Result

The bounded Digital-8/16 path does not currently require additional broad
XE164 decompilation. The accepted evidence places the smallest demonstrated
replacement at the ADI provider, and the remaining gaps separate into three
different kinds rather than one firmware problem:

1. Local own-source/document issues: bridge-enabled Reset is lifecycle-
   incoherent, and no-client Bridge STOP does not satisfy the unconditional
   public permit-revoke wording.
2. Original-consumer contracts: complete manager lifecycle order and original
   Push result handling require an exact hash-bound ARM consumer/provider
   caller trace. Slot presence, telemetry and own-model tests cannot replace
   that trace.
3. Later runtime evidence: active permit, lease loss, native STOP/restart and
   watchdog effects cannot be proved statically. The accepted native runs kept
   model permit zero.

This synthesis is `HYPOTHESE` for architecture prioritization and
`VERIFIZIERT` only for the individual evidence/status mappings in
`acceptance-repair-matrix.tsv`. It does not authorize a source fix or runtime
experiment.

## Smallest defensible next sequence

- First define the intended local Reset and standalone Bridge-STOP contracts.
  The present source already proves where the inconsistency lies; no firmware
  analysis is needed for that decision.
- Then obtain or reuse a lawfully available, exact-hash original-manager trace
  only for the complete lifecycle caller and Push result path. Do not infer
  missing edges from the 34-slot table or native provider telemetry.
- Preserve authentic board/runtime/diagnostic services for the bounded native
  target. UID/config-register and other side services remain explicit
  rejections or conditional traces, not fabricated emulation.
- Keep later active-output validation distinct from static acceptance. It
  requires separate authorization and cannot be replaced by XE164 pseudocode.

## Why broad XE164 work remains deferred

E-XE164-069 found no accepted firmware evidence that adds a currently required
ADI signature, lifecycle phase or error contract. E-XE164-070 therefore places
broad XE164 work outside the bounded digital critical path. E-XE164-074..079
made the remaining gaps more specific, and none of them presently names a
missing lower firmware behavior: two are own-source issues, two need an ARM
caller trace, and one is a later runtime test. This does not prove the whole
XE164 irrelevant and does not apply to general K-Bus, analog, PWM or serial
coverage.

## Method, alternatives and limits

Root GPT-6.1 SOL integrative Self-Review of eight exact-hash accepted package
artifacts. No REA operation was needed because this package synthesizes
accepted matrices rather than inspecting a new binary. Alternative explanation:
a future selected module or service may expose a consumer-visible requirement
below ADI; row A14 retains that conditional route instead of asserting global
irrelevance. No firmware, source repository, device, network, VM or runtime
mutation occurred.

Tests: input hash validation and matrix consistency validator `PASS`. Builds,
unit/integration tests, runtime and hardware: `NOT_RUN`.
