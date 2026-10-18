> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-225 — minimum leading-position synthesis

## Result

**HYPOTHESE:** Exact libdal returned-object positions `+0` and `+4` form a lifecycle-like structural pair. The `+0` target can set the shared memory-only gate byte at base `+0x28` to `1` on its bounded success lane; the `+4` target can set that same byte to `0` on its bounded active path. Their static placement as the first two returned-object target candidates and their complementary gate transitions make them a plausible phase pair.

**OFFEN:** The original consumer that indirectly invokes either position, invocation order, inputs, signatures, semantic names, runtime binding and execution are not established. Consequently this synthesis does not promote `+0/+4` to named startup/shutdown callbacks and does not yet make them a verified virtual-provider requirement.

## Evidence reconciliation

The seven-row `lifecycle-matrix.tsv` preserves the distinction between observations and synthesis:

- E-XE164-228 verifies only that the getter returns the slot address ELF `0x14154`.
- E-XE164-248 verifies the static `+0/+4` target cells and the absence of direct aligned file-backed A32 B/BL callers.
- E-XE164-250 verifies the complete bounded `+0` target mechanics, including its byte-1 success store and visible `0/-1` result lanes.
- E-XE164-249 verifies the complete bounded `+4` target mechanics, including its byte-0 store and visible zero exits.
- The lifecycle-like pairing in R5 and virtual-provider extension in R7 remain HYPOTHESE because no original-consumer indirect call or order is bound.

This is materially useful for virtualWAGO: it narrows the next question to the original consumer of two leading object positions, rather than further physical K-Bus decompilation. If the consumer and order are later verified, the emulator-facing contract can be extended with the exact bounded reactions already recorded. Until then, implementing those positions as mandatory would outrun the evidence.

## Method and limits

Method: GPT-6.1 SOL root integrative Self-Review of the four hash-bound accepted reports listed in `assignment.md` and canonical E-XE164-228/E-XE164-248..250. No new binary disassembly, runtime, device, network, VM or hardware action was performed.

Alternative explanation (**OFFEN**): the two leading positions may be optional maintenance operations, error recovery, test hooks or another phase relation. Complementary writes alone do not establish their names or ordering.

Test: `python3 validate.py` checks all input hashes, the seven-row matrix schema/status/evidence coverage and required report boundaries. Expected result: **PASS**. This validator is a consistency check, not an independent review.
