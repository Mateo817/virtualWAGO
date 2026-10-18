> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-086 — exact-consumer contract synthesis

Date: 2026-10-15 UTC
Review: GPT-6.1 SOL root Self-Review

## Question

Which minimum caller-visible Push and cyclic result mechanics are supported by
the accepted exact FW31 static findings, and which cross-library bindings still
prevent an end-to-end API claim?

## Inputs

The six revision-bound reports and their exact SHA-256 values are listed in
`inputs.tsv`. They cover the FW31-identical provider Push body, a direct
provider countercheck, exact IoDrvDal DeviceSpecific dispatch, the exact
IoDrvKbus published Push caller, and exact IoDrvKbus ReadInputs/WriteOutputs.
No runtime, VM, device, network or hardware evidence is introduced here.

## Result

Befundstatus: **VERIFIZIERT** for the instruction-bound mechanics listed below;
**HYPOTHESE** for the bounded emulator implications; unresolved bindings remain
**OFFEN**.

### Statically verified mechanics

- The FW31-identical provider `libpackbus_Push` maps its selected inner helper
  result to numeric `0` or `-1` after its observed cleanup path
  (E-XE164-083/084).
- Exact `Dal_CallDeviceSpecificFunction` performs one indirect callback and
  neither compares nor rewrites `r0` afterward. The callback register result
  survives the outer epilogue (E-XE164-090).
- The exact published IoDrvKbus Push caller passes a pointer-result cell to a
  `libpackbus_Push`-named indirect call. It returns numeric `0` only when both
  the indirect-call `r0` and the reloaded cell are zero; other post-call
  combinations return `1` (E-XE164-091).
- Exact ReadInputs and WriteOutputs take numeric `2` paths when their respective
  start-table call returns nonzero. Their finish-table return is discarded.
  On normal completion, the last status-setting transfer value—not an OR of
  all transfer results—is mapped from zero/nonzero to final numeric `0`/`2`
  (E-XE164-092/093).
- WriteOutputs has additional distinct flows: one helper result gates later
  repetitions, and two callback returns are used as an address/base value.
  Those values are not the final status (E-XE164-093).

These are instruction-bound numeric/control-flow observations. They do not
name numeric `0`, `1`, `2`, `3`, `12` or `-1` with manufacturer semantics.

### Bounded emulator implication

**HYPOTHESE:** For the bounded Digital-8/16 original-stack path, a compatible
lower-boundary implementation will need to preserve the observed separation of
outer return and pointer result, return zero on the consumer-selected normal
paths, and reproduce last-status overwrite behavior rather than cumulative
first-error/OR aggregation. A finish operation may still require side effects
even though these two consumers discard its return value.

This is the smallest implementation-facing interpretation of the verified
branches. It is not yet an end-to-end ABI contract because the static evidence
does not resolve the indirect table entries to exact provider/DAL symbols, does
not prove that the Push caller's second input is WriteEnd, and does not provide
manufacturer types for the record fields.

## Alternatives and limits

- The unresolved table pointers may bind to wrappers that transform arguments,
  results or side effects. Therefore direct provider-to-consumer equivalence is
  OFFEN even where names and shapes fit.
- A finish return can be ignored while finish side effects remain mandatory;
  omitting the call would not be justified by the caller's discarded `r0`.
- Last-status overwrite can mask an earlier nonzero transfer result when a
  later status-setting transfer returns zero. Replacing it with fail-fast or
  cumulative aggregation would change the observed caller mechanics.
- Callback/base results in WriteOutputs cannot be modeled as status solely
  because they are returned in `r0`; their subsequent use is address-like.
- Runtime loading, concrete table contents, concurrent behavior and hardware
  effects remain NOT_RUN/OFFEN.

## Acceptance

`contract-matrix.tsv` separates each observation from its bounded emulation
interpretation and unresolved binding. `validate.py` checks all input hashes,
the status vocabulary and exact matrix width. Validation result: PASS.
