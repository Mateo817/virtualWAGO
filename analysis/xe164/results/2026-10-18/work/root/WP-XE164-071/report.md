> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-071 — Reset/Bridge-STOP remediation design analysis

## Outcome

No source change is made. The narrowest source shape consistent with the
current safety intent is `R1 + S1` in `remediation-options.tsv`:

- make bridge-enabled Reset follow the already visible Exit lock structure:
  lifecycle serialization, state clear/generation bump under `state_mutex`,
  release the state lock, then stop/join the bridge while lifecycle remains
  serialized;
- after a successful standalone bridge-worker join, revoke permit while no
  `bridge_control_mutex` is held and before stop completion permits a new start.

This is a `HYPOTHESE` design recommendation, not an implemented or tested
contract and not a reconstruction of manufacturer behavior.

## Lock reasoning

The accepted graph contains Init's order `lifecycle_mutex -> state_mutex ->
bridge_control_mutex`. Exit holds lifecycle, clears state, releases state and
then enters bridge stop; the stop path releases bridge control before joining,
so worker callbacks can still acquire state. A Reset shaped like Exit preserves
those visible directions. It must not join while holding `state_mutex` because
the worker may need that mutex during disconnect/permit cleanup.

An unconditional permit setter must not be inserted while bridge control is
held: that would add `bridge_control_mutex -> state_mutex`, opposing Init's
visible `state_mutex -> bridge_control_mutex` edge. Calling it after successful
join while control is not held avoids that inversion. The existing
`bridge_stopping` state must continue preventing a concurrent start until stop
completion is published. Exact placement and join-failure behavior require code
review when implementation is authorized.

## Alternatives and limits

`R2` is viable only if the Reset precondition is enforced, not merely written
in documentation; the current `void` API and absence of an exposed bridge-state
query make that a broader API decision. `S2` is a documentation-only correction
but weakens the present fail-closed intent and would require proving every
standalone stop caller clears/revokes first.

Necessary future assertions are listed as `T1`, but tests are `NOT_RUN` here.
No scheduler proof, compiled-binary proof, runtime behavior or manufacturer
semantics is claimed. `pthread_join` failure recovery and destructor context
remain OFFEN. No repository, firmware, device, network or VM mutation occurred.

## Method and review

Root GPT-6.1 SOL integrative Self-Review of the two hash-bound sources and the
accepted WP065/WP067 reports. REA is not applicable because no new binary is
being analyzed. Input hash and five-row/status validation: PASS. Builds, tests,
runtime and hardware: NOT_RUN.
