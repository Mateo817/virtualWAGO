> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-074 — independent Push-coordinate/result countercheck

## Result

**VERIFIZIERT**, bounded static countercheck: independent GNU readelf and ARM
objdump inspection corroborates the corrected WP-XE164-073 coordinates and
the handler's `0`/`-1` normalization. The exported dynsym begins at ELF-VA
`0x10130` and spans 424 bytes. Ghidra/REA's `0x20130` is an analysis address,
not the linked ELF address. ELF-VA `0x80f4` is a PLT stub whose GOT
`R_ARM_JUMP_SLOT` relocation at `0x33454` names `libpackbus_Push` at
`0x10130`.

The executable instructions end at ELF-VA `0x102cb`; the remaining 12 bytes
through dynsym end `0x102d8` are three PC-relative literal words. The return
sequence at `0x10248..0x10250` maps a retained helper result to zero if it was
zero and to minus one otherwise. Both the normal `SCPU_DataExchange` call and
the watchdog-reaction call feed that retained value. Early null branches reach
the `mvn r0,#0` minus-one return path.

Direct calls at ELF-VAs `0x10f44` and `0x1807c` target the PLT entry. The
second caller compares the Push return with zero and selects a longer sleep on
nonzero. This does not establish complete direct- or indirect-caller coverage.

The handler return is an inner-result candidate. This ELF does not by itself
establish the outer DAL `CallDeviceSpecificFunction`/`VCall` status or its
propagation, which remains **OFFEN**.

## Method and scope

Primary analysis was REA-first in WP-XE164-073. This deliberately overlapping
root countercheck independently used GNU readelf 2.44 and
`arm-linux-gnueabihf-objdump` 2.44 against the same hash-bound ELF. Exact checks
are encoded in `validate.sh`; the claim matrix is `countercheck.tsv`.

This is GPT-6.1 SOL root **Self-Review**, not an independent reviewer. No
Decompiler pseudocode is treated as source. No struct, field name, external
dispatcher contract or device effect is inferred from numeric displacements.
Binary execution, runtime, device, network, VM and hardware tests are
**NOT_RUN**.
