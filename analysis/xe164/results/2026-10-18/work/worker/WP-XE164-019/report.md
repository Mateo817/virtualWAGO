> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-019: bounded static analysis of seed E00B42

## Result

Status: **VERIFIZIERT** for the byte-bound local instruction sequence and its local control flow. Test status: **PASS** for the input digest, table bindings, protected boundary, checksum verification, and validator. This is static disassembly evidence only.

Input: `DERIVED-XE164-COMPOSITE-E00000`, 17,110 bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`. The validator independently checks this exact digest and checks every listed instruction byte against the composite.

Analysis interval: file offsets `0x0B42..0x0B83`, mapped by the stated base to analysis addresses `E00B42..E00B83`. The last decoded instruction begins at `E00B82` and is the two-byte `rets` (`db00`), ending at `0x0B83`. The body therefore has one observed basic block, `E00B42..E00B83`, with a return edge and no local conditional or unconditional branch. No body instruction starts at or extends into `0x0B84`.

The sole separately allowed caller instruction is at file offset `0x04DA`, analysis address `E004DA`. Its bytes `dae0420b` decode as `calls 0xe00b42`, binding a direct incoming call to the seed. No caller-body traversal was performed. No direct calls occur within the bounded E00B42 body.

The body exposes 13 address-like numeric operand occurrences and three immediate literals. The exact spellings and source instructions are tabulated in `references.tsv`; these values are reported as decoder output and are not assigned DPP, SFR, ABI, memory-map, or device meaning. The instruction sequence includes `#0x0500`, `#0x4000`, and `#0x8882` as immediate operands.

## Method and evidence

REA was used first. The accepted Rizin observations used Rizin 0.9.1 (local `rizin -v`; REA's Evidence wrapper did not resolve its own version field) with command configuration `e io.va=false; e asm.arch=c166; e asm.bits=16; e cfg.bigendian=false`. The bounded instruction capture was `pdj 17 @ 0xb42`; the caller capture was `pdj 1 @ 0x4da`. REA invokes Rizin as `rizin -N -q -c <command> <input>`; `-N` suppresses user settings/scripts. No Ghidra fallback was needed because Rizin decoded the complete bounded straight-line path through a return and the byte-bound validator passes.

Accepted REA evidence IDs:

- `ev_e4febb384aefca077ff265da7fb5eac03634ea633fc8508ebfa8bf404e93c3bc`: body instructions in `0x0B42..0x0B83` only.
- `ev_98ef159674231ae0eac8a5a454ca18e1fa06648129a35c9a2beb5a7b748e623a`: the single caller instruction at `0x04DA`.

### Exploratory overscope, rejected from accepted evidence

The first REA command requested `pd 48 @ 0xb42`. Its output continued past `0x0B84`, into the separately identified startup-data region. Those post-boundary lines are explicitly rejected: they are not used in the tables, CFG, calls, numeric references, or conclusions above, and no interpretation is made from them. This exploratory command is retained in the canonical REA bundle because REA exports all currently retained records; its evidence ID is `ev_7a204e5f1d8687dcccbcbfc969aa72066063b4ce25714c7f53ee9578c81db35f`. The bounded `pdj 17` capture then ended exactly at `0x0B83`. The canonical bundle also retains that bounded capture and the separate caller capture.

## Alternatives and remaining uncertainty

The alternative that this byte run is data accidentally decoded as code is weakened by the authorized direct `calls E00B42` at `E004DA`, a consistent instruction sequence, and a decoded return exactly before the known data boundary. This does not prove that every runtime path reaches the return, or that the selected interpretation is the only possible instruction alignment. No incoming-reference census, surrounding caller analysis, callee traversal, or independent decoder comparison was performed. The numeric operand meanings and runtime effects remain **OFFEN** and outside this work package.

No APIs, register/stack calling convention, DPP/SFR meaning, K-Bus behavior, device behavior, or startup-record interpretation is claimed.

## Tests and artifacts

Test outcomes: input SHA-256 **PASS**; instruction byte/address/extents and table bindings **PASS**; boundary exclusion **PASS**; `sha256sum -c SHA256SUMS` **PASS**; worker validator **PASS**. These are self-checks, not an independent review. Canonical REA evidence bundle exported by `export_evidence_bundle` (4 records, 0 unknowns); it is not a hand-authored import bundle. Bundle SHA-256 and all artifact hashes are recorded in `SHA256SUMS`. `report.md`'s own SHA-256 is recorded there as well.

Files in this work package: `report.md`, `instructions.tsv`, `edges.tsv`, `calls.tsv`, `references.tsv`, `validate.py`, `rea-evidence-bundle.json`, and `SHA256SUMS`.
