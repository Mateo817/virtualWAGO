> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-173 root direct-caller remediation

Input identity is **VERIFIZIERT**: 5,181,396-byte little-endian ARM ELF,
SHA-256
`b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.
Exact Dynsym `CMInitComponent` is `[0x301394,0x3018B8)`.

REA exact-hash records `ev_2b93...44e7`, `ev_5ad6...4843` and
`ev_d6d2...75837` bind two references and their exact direct-BL
instructions. Root's independent aligned raw scan and GNU ARM decode over all
four executable sections agree on exactly two sites:

| call | word | effective window | SHA-256 | exact Dynsym owner |
|---|---|---|---|---|
| `0x3018D8` | `0xEBFFFEAD` | `[0x3018B8,0x3018E8)` (clipped) | `b2f1ebc592e809d6585d32479e99d5d5a1f58757cb149219f481ef8c2b18932f` | `cminitcomponent [0x3018B8,0x3018E4)` |
| `0x31A66C` | `0xEBFF9B48` | `[0x31A61C,0x31A67C)` | `7ccffdd7f5392810854c235759f1da8cb706625d2e658ebcf23e107e4abf0aa7` | `AppLoadCIntegrationModule [0x31A628,0x31A680)` |

The first nominal window would begin at `0x301888`; it is clipped to avoid
the excluded target body. Its effective 12 instructions show entry-window r0
saved in r4, then `r0=[window-entry r0]`. Only the nonzero loaded-value path
calls `CMInitComponent`; r1 is not defined in scope. The raw return is stored
to `[r4+4]`.

The second 24-instruction window calls `CMLoadComponent3` at `0x31A648`.
At `0x31A66C`, r0 is that opaque callee's raw return, constrained locally to
`r0 != -1`; the target call is reached only when the separately loaded local
r3 is zero. r1 was defined before the opaque call and is not redefined, so its
value is **OFFEN**. The target return is copied to r3 and back to r0 within the
window; the actual return instruction lies at its exclusive boundary.

WP-XE164-172's first version is **FAIL** for scope because it decoded 48 bytes
inside the expressly excluded WP170 body; it also discarded the visible raw
r0 return at the second site. Its corrected history is retained, but this
root repetition is the canonical basis.

The two-site direct-A32-BL inventory and bounded register/control facts are
**VERIFIZIERT**. Indirect/Thumb/dynamic transfers, runtime reachability,
argument meaning, callee effects, API/layout semantics, runtime and hardware
remain **OFFEN/NOT_RUN**. Tool versions: REA/Ghidra 12.1.4 retained evidence;
GNU ARM objdump/readelf 2.44; Python 3.13.5. Review is root Self-Review only.
