> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-180 — responsibility synthesis

## Result

The bounded contract does **not** require reimplementing the retained
IoDrvKbus/IoDrvDal consumer control flow inside the mock. The provider must
offer the observable reactions at the selected seam; enumeration and cyclic
call order, status aggregation, Write gate/position consumption, and the final
outer/inner Push conjunction remain behavior of the retained original layers.

Two rows are direct mock responsibilities within the present evidence:
AC-06's externally visible bounded Push failure/zero/nonzero reaction, without
copying the physical helper interior, and AC-07's requested/effective-output
separation. Five rows are mixed because the mock supplies reactions while the
retained consumer supplies ordering or aggregation (AC-01..05). AC-08 is
outside the bounded target, AC-09 is a review rule, and AC-10..12 remain open.

This is an architectural decomposition and therefore `HYPOTHESE`, not a new
binary contract or implementation approval. The key alternative explanation
is that a presently unresolved dynamic binding or parallel service path could
require an additional provider reaction. E-XE164-069/070 and E-XE164-201 keep
that possibility open.

## Consequence

The next useful engineering work is narrow: statically specify and later test
only provider-visible inputs, outputs and result propagation. Do not reproduce
the physical K-Bus state machine, the original consumer's callback ordering,
or its internal result-combination logic in the mock. Rows AC-04, AC-10 and
AC-11 remain gates because their concrete provider return/binding requirements
are not fully established.

No tests, builds, runtime, VM, network, device or hardware action was
performed. All such tests are `NOT_RUN`. This is a GPT-6.1 SOL root
integrative Self-Review, not an independent review.

## Reproducibility

`validate.py` checks all five input sizes/hashes, exact AC-01..AC-12 coverage,
allowed ownership categories and status words. `SHA256SUMS` binds the generated
artifacts. Tool versions: Python 3.13.5 and GNU sha256sum 9.7.
