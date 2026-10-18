> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-243 bounded downstream flow analysis

Status: **OFFEN**. This is an offline static analysis of exact target bytes, not runtime or ABI evidence.

## Source and scope

Target `codesys3` is bound by SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` (5,181,396 bytes) and is sourced from the exact FW31 SD-image artifact SHA-256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c`. The target-file hash identifies the analyzed bytes. Original bounded GNU listing SHA-256 `a0bcaec911083963c573bead0b28ee8c0b3106c3b8aa5eb595a556fbc5e75110`. Only these half-open ELF-VA intervals were analyzed: `[0x12e6f0,0x12fa58) OpcUa_TcpConnection_CheckProtocolVersion@@Base; [0x135a9c,0x13629c) OpcUa_ServerApi_HistoryUpdate@@Base; [0x136cf4,0x1375d0) OpcUa_Endpoint_GetPeerInfo@@Base; [0x143d68,0x144d10) OpcUa_SecureListener_ProcessSessionCallRequest@@Base`. These are parser-bound symbol-marker intervals for grouping; they do not establish code/function ownership. “Word start” means a linearly parsed A32 objdump word boundary only, not proof of executable code ownership. Assigned table words are excluded from code nodes; their exact case/default edges come from the four scoped WP241 matrix rows and are cross-checked against the root countercheck plus source bytes.

## Evidence and method

REA was queried in WP241 at the four exact dispatch addresses; the retained hash-bound IDs are recorded in `inputs.tsv` and verified against target/profile/query/result by this validator. All four returned `not_in_procedure`, so the bounded fallback uses original GNU objdump words plus ELF32 little-endian PT_LOAD mapping. The four scoped WP241 matrix target lists are cross-checked against the root raw-table countercheck; its table-specific status is `VERIFIZIERT`. No other rows are semantically read. Register BLX, BX, LDR-to-PC, multiple-load-to-PC, and explicit PC destination transfers are separately inventoried. `cfg-edges.tsv` labels calls as opaque and makes no ABI assumptions. The value analysis conservatively represents incoming, memory, computed, and opaque values; a call invalidates modeled core-register state (`r0-r12`, `sp`, `lr`) and leaves memory effects unknown. Conditional predicates are over-approximated. Candidate target loads require a `TLOAD` value plus a local call-free instruction-address witness. `load-blx-r0-flow.tsv` includes both every register BLX/BX and every decoded `LDR [base,#0x20]`, including loads with no matched call.

## Results

The validator emits 111 register BLX/BX rows, 36 `LDR [base,#0x20]` rows and 173 explicit indirect/control-transfer rows across the scope. Of the register calls, 13 have a callfree address witness from a `+0x20` load; Only-merged matches without a local witness: 0. The modeled r0 classes observed at these calls are `COMPUTED, INCOMING_UNKNOWN, MEMORY_UNKNOWN, OPAQUE_UNKNOWN`. No call row establishes a constant-15 r0 value in this model; incoming, memory, opaque and computed values remain distinguished. Load rows connect downstream candidate calls and their exact r0 reaching definitions. The explicit VFP writeback at `0x1374bc` (`vldmia ip!, D-register-list`) is retained as an unsupported `ip` effect. `gaps.tsv` enumerates retained REA gaps, marker/ownership limits, unresolved PC transfers, unsupported writes, out-of-interval/unlisted edges, and linear-listing holes. Any proven constant is only a local static value result under the bounded abstract model; it does not establish runtime behavior or a calling convention.

## Remaining limits

The parser covers listed A32 words and the explicit instruction families implemented in `validate.py`; flags and path predicates are not solved, memory aliasing is unknown, and unsupported write forms are emitted as gaps. r0 categories are not exhaustive for statically computed values produced through unmodeled forms such as some `movw`/`movt` combinations, alternate encodings, or other register-write instructions; those remain **OFFEN**, not evidence of absence or inequality to 15. Register BX/tail transfers and PC-writing loads are transfer classes, not calls. No statement is made about runtime targets, function ownership, API contracts, or opaque-call ABI preservation.

## Validation

Run `python3 validate.py` for read-only validation; `python3 validate.py --write` explicitly regenerates the four TSV inventories and report. `manifest.sha256` binds the validator and generated outputs, excluding itself.
