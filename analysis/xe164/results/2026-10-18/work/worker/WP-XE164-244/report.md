> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-244 — bounded downstream target and r0 flow

Status: **OFFEN**. Scope is the exact ELF VA interval `[0x154dc4,0x1630bc)` in the hash-bound `codesys3` file. `InfoModel_GetConditionId@@Base` is the assignment marker only; Ghidra body ownership is used only where retained records explicitly provide it.

## Evidence and graph model

The original WP242 matrix contributes 27 assigned table dispatches (377 words), each checked against raw ELF bytes, local instruction words, and the root countercheck. Two additional indexed PC-load dispatches omitted from the prior inventory were found locally at `0x1619a0` and `0x162f0c`; adjacent same-index `CMP`/conditional `LDRLS`, in-range default branch, exact bounds, and raw word targets close 17 and 8 words respectively. They are explicitly separated as supplemental local findings in `dispatch-scope.tsv`. Total graph-excluded table/literal words: 426 (24 PC-relative literal words). No table bytes are treated as code.

The bounded listing has 14526 decoded rows, 14100 code-graph nodes, 70 REA function-body queries, 15315 modeled local edges, 138 unresolved-gap records, and 2 unsupported register writes. Unowned linear islands use bounded GNU disassembly with unknown-entry state; they are not Ghidra ownership claims. Direct calls are opaque, invalidate all register/memory facts at return, and carry no ABI assumption. Predicated instructions and table false-condition fallthroughs retain separate conditional lanes.

## Indirect-transfer results

The inventory contains 27 register BLX calls, 3 register BX transfers, 29 indexed PC dispatches, 1320 direct opaque calls, and 189 restored-PC returns. Across all 30 BLX/BX rows, the bounded model found 0 explicit same-register `[base,#0x20]` load-to-transfer path witnesses. This describes modeled graph coverage, not a global selector-path exclusion. The exact reaching r0 facts and alternatives for every BLX/BX are in `load-blx-r0-flow.tsv`; unknown, memory-derived and opaque-call values remain unknown, not unequal to 15. Within modeled may-facts, proven constant 15 reaches 0 transfer rows; other constants reach 3 rows; computed or symbolic computed values reach 4 rows. Rows labelled `OFFEN-GAP` or `unreachable-or-uninitialized` are unresolved.

## Remaining limitations

The gap inventory has 15 unowned linear islands, 116 explicitly widened node/register states, 4 out-of-range/unmapped direct-branch targets, and 3 unresolved BX destinations. The widened facts are not silently discarded: affected node/register and provenance are listed in `unresolved-gaps.tsv`. The flow matrix keeps unowned-site call states as gaps. Consequently the package makes no global negative claim about a selector path or runtime behavior. Unsupported writes appear separately in `unsupported-writes.tsv`.

The default `python3 validate.py` reconstructs expected TSV/report/manifest content in memory and compares bytes without writing; `python3 validate.py --write` is the explicit generator mode. This is a self-review artifact, not an independent review.
