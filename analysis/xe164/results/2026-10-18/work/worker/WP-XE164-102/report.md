> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-102: Digital profile and native-evidence consistency

Review date: 2026-10-15. Scope: static reading of the five supplied files only. No device, network, VM, runtime, binary, or vendor-file access was performed. REA is not applicable because binary analysis is excluded.

## Finding

**VERIFIZIERT, within supplied source/config scope:** the current C profile declarations and `native_profiles` catalog entries consistently associate the own Digital-8 model with `0x8801`/`0x8802` and the own Digital-16 model with `0x9001`/`0x9002`. Digital-8 Parameter10 strings carry the same four-character hex tokens; Digital-16 Parameter10 is null. The catalog descriptor references and continuation report explicitly scope the 880x identifiers to engineering descriptions, not physical revisions. The catalog labels its layouts as own research metadata, not native bus mappings.

**VERIFIZIERT, aufgezeichnete Trial-Fakten:** the 2026-10-13 Nativevidence records native trials for profile 8 with articles 750-430/750-530 and profile 16 with articles 750-1405/750-1504. The Digital-16 offline-build section records exact 9001/9002 description identifiers and descriptor hashes. The Digital-8 trial entry names the profile and articles, but does not include the 8801/8802 descriptor identifiers or hashes. These are claims about what the supplied report records and its stated scope, not independent reruns.

**OFFEN, Quellenbindung:** its `current_source_sha256` values for `tools/adi_catalog_profiles.h` and `config/module-catalog.json` are `3e2c62c3…58127ba` and `1415eb04…521a89c`, not the supplied current-file hashes `332e030a…af66c0` and `938575e6…58831`. Therefore exact byte-binding of the recorded trials to the current profile/header files is absent. Functional equivalence of the old and current revisions is also unknown.

**OFFEN:** the five inputs do not establish physical module identity, hardware revision, or that the tested descriptions correspond to installed physical modules. They also do not establish concrete call-path reachability, dispatch selection, or runtime semantics for any specific ID. The continuation note describes a static bit-15 fast-path result as static analysis; this work package does not inspect the binaries or independently validate that route.

## Explicit bit-15 and signed-16 calculation

For unsigned 16-bit value `u`, bit 15 is `(u >> 15) & 1`. Its two's-complement signed-16 interpretation is `u - 65536` when bit 15 is one, otherwise `u`.

| Model value | Unsigned decimal | Bit 15 | Signed-16 decimal |
|---|---:|---:|---:|
| `0x8801` | 34817 | 1 | -30719 |
| `0x8802` | 34818 | 1 | -30718 |
| `0x9001` | 36865 | 1 | -28671 |
| `0x9002` | 36866 | 1 | -28670 |

All four values have bit 15 set and are negative under signed-16 interpretation. This arithmetic is a property of the numeric values only; it does not imply a binary branch, route, dispatch, identity, or hardware behavior.

## Evidence-stage matrix summary

See `evidence-matrix.tsv` for row-level observations, conclusions, statuses, and boundaries. The key layers remain distinct:

1. **Model values:** own catalog/profile identifiers and masks/widths.
2. **Engineering-description references:** catalog IDs, version/hash references, and the Digital-8 continuation's description note.
3. **Native-profile/trial records:** recorded profile-number/article pairs and Digital-16 terminal Description references in the evidence JSON, with source-hash provenance mismatch against current files.
4. **Physical identity:** no claim supported; `hardware_evidence` is null and source texts state comparison/revision limits.
5. **Concrete dispatch reachability:** not established by this offline work package. Static-route language in the continuation is reported as an existing assertion, not reproduced as a conclusion here.

## Alternative explanation and residual uncertainty

The differing source hashes may simply mean the 2026-10-13 trial used an earlier, functionally equivalent profile/catalog revision and later catalog generation changed metadata or ordering. The supplied evidence does not include a complete source diff or a trial-time profile dump, so equivalence cannot be verified here. Conversely, the mismatch could conceal a behaviorally relevant change. Trial facts remain **VERIFIZIERT** at the scope recorded by the evidence; exact source binding and equivalence remain **OFFEN**.

The catalog describes each high-bit prefix as a model/description binding. A future reader could conflate the matching numeric prefix with physical module identity or infer that it selects a reachable code path. Neither inference follows from the profile fields, engineering-description IDs, or native trial labels alone.

## Checks and status

- Input SHA-256 precheck: **PASS** (all five supplied hashes matched).
- Validator: **PASS** (profile/model value alignment, Parameter10 references, trial article/profile labels, Digital-16 terminal references, four arithmetic cases, and allowed status vocabulary checked).
- `sha256sum -c SHA256SUMS`: **PASS** after artifact generation.
- Physical comparison / physical revision: **NOT_RUN**; also outside supplied evidence scope.
- Binary dispatch/reachability: **NOT_RUN** in this package; expressly excluded.
- Runtime/hardware claims: **NOT_RUN** here; this report relies only on what the supplied report records and does not independently reproduce those trials.

Self-review: this is a static evidence reconciliation, not an independent binary review or native trial rerun.

## Generated files and hashes

| Generated file | SHA-256 |
|---|---|
| `evidence-matrix.tsv` | `4e77baa74de1cb498932f9a6a88ff7f650e8a344e8e5d234ce9cc1dca0d864fa` |
| `validate.js` | `a12a0475fd47236d47b8c0904be9c4bdd14eabfa801ad0c26813012f24654099` |

`SHA256SUMS` records the hashes for all three payload files, including this report, and passes `sha256sum -c`. The manifest excludes itself, as usual for a self-referential checksum list.
