> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-079 — exact-consumer instruction countercheck

Date: 2026-10-15
Review: GPT-6.1 SOL root Self-Review

## Inputs

- `libIoDrvDal.so.1.0.2`: 25,976 bytes, SHA-256
  `853d3ad6eb1b2477b43502d562a6bbfa854b8029e85989b6166f961167188c7d`
- `libIoDrvKbus.so.0.0.1`: 38,584 bytes, SHA-256
  `543e8b1d2d19352030fe804a7e667ca30c1d9ba80069f2df3158c77c544789b8`

Tool: GNU `arm-linux-gnueabihf-objdump`/`readelf` 2.44. No executable was
run. This is an explicitly overlapping Self-Review of WP-XE164-077/078, not an
independent review.

## Findings

**VERIFIZIERT:** IoDrvDal `ComponentEntry` at ELF VA/file offset `0x4448`
writes callback-valued fields, conditionally calls the pointer loaded from
input `+0x28`, calls `adi_GetApplicationInterface@plt` at `0x45a4`, and passes
the untested returned pointer to `memcpy` with length `0x88`. The callback at
`0x1704` returns `3` for a missing stored pointer, calls it first at `0x1734`,
returns the first nonzero result, and calls it a second time at `0x175c` only
after zero. `readelf` binds relocation `0x15e4c` to
`Dal_DiagnoseGetDeviceState`. These checks corroborate WP-XE164-077's bounded
registration mechanics, not host invocation order or a full ABI.

**VERIFIZIERT:** IoDrvKbus `IoDrvKbus_Init` at ELF VA/file offset `0x47fc`
returns numeric `2` on the observed null-input branch and writes callback-valued
fields at `+0x2c`, `+0x34..+0x54`, and `+0x624..`. The callback body at
`0x2650` calls the indirect target loaded from context offset `+0x70`; only a
zero status plus output word `2` reaches `idk_IoDrvScanModules@plt` at
`0x26e4`. The body at `0x6050` uses an indirect target at context offset
`+0x58`; its status and output select reset-diagnosis versus set-diagnosis,
while both branches return zero.

**VERIFIZIERT:** The phase callback at `0x3f98` has explicit numeric cases `4`
and `12`. In case `12`, the thread-stop call at `0x44c0` has its result stored
at `0x44cc`; a null event-state branch at `0x44d8` reaches the common epilogue,
which reloads that saved result at `0x3fc8`. Therefore the first WP078 wording
that this path returned unconditional zero was rejected. The corrected WP078
report and lifecycle table now state that the saved stop result is returned.

**OFFEN:** Numeric phase semantics, callback-field names, the external host's
callback order and runtime effects. Static code presence and exported names do
not establish execution, ABI completeness or hardware behavior.

## Tests

- Input size/SHA-256: PASS
- Exact instruction-token and relocation checks in `validate.py`: PASS
- Runtime, original host invocation and hardware: NOT_RUN
