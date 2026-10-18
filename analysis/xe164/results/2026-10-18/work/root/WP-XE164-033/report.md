> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-033 — five-callee callsite/data-flow synthesis

## Result

**VERIFIZIERT, bounded static syntax:** The five direct callsites already
recorded in E-XE164-019 divide into two observable shapes.

1. `E0064C→E0054A` and `E00654→E00556` are followed immediately by stores of
   `r4` to `[r0+0x0006]` and `[r0+0x0004]`. Their bounded callees each build an
   immediate through `r13` and `r12`, then assign `r4`: `0x00E0` in E0054A and
   `0x0200` in E00556. This is a static cross-call def/use candidate, not a
   verified return-value calling convention.
2. Before `E0067A→E005A2`, `E00698→E00562` and `E0069E→E005EC`, the caller
   explicitly executes `mov r12, r0`. All three bounded callees then use `r12`
   as the starting register for overlapping relative accesses within
   `+0x02..+0x0E`. E005A2 and E00562 contain no assignment to `r12`; E005EC
   assigns `r12` from `[r13+]` at E0061A before its final indirect store.

The caller itself reserves a 16-byte `r0`-relative window with
`sub r0,#0x0010`, accesses even offsets `0x00..0x0E`, then restores the value
with `add r0,#0x0010`. Calling that window a stack frame or assigning field
types is **HYPOTHESE/OFFEN**, because the exact C166 calling convention and
register role are not qualified here.

## Inputs and method

- Composite: 17,110 bytes, SHA-256
  `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Parent: WP-XE164-010 `instructions.tsv` and `calls.tsv`, accepted by
  E-XE164-019.
- Callees: accepted tables/reports from WP-XE164-028..032, bound by
  E-XE164-039 through E-XE164-043.
- Method: exact instruction-row correlation only. No new broad decode, global
  Xref claim, decompiler type recovery, runtime or hardware action.

`call-interface.csv` records the five callsite/callee/post-call correlations.
`relative-window.csv` records only directly derived `r12`-relative offsets; an
`R` or `W` describes decoded read/write syntax, not an address-space or field
contract. Indirect accesses after a register is loaded from memory are not
relabelled as accesses to the original relative window.

## Exact observations

- The parent saves `r9`, `r8`, `r7`, `r6`, subtracts `0x10` from `r0`, and
  later performs the inverse add and four restores before `RETS`. This repeated
  shape supports, but does not prove, a stack-frame interpretation.
- E0054A contains `mov r13,#0x00E0`, `mov r12,r13`, `mov r4,r12`, `ret`; the
  next decoded parent instruction after its call stores `r4` at `[r0+6]`.
- E00556 contains the same register-transfer shape with immediate `0x0200`;
  the next decoded parent instruction stores `r4` at `[r0+4]`.
- E00678, E00696 and E0069C each assign `r12=r0` immediately before the three
  larger calls. Those callees directly reference overlapping even relative
  offsets from the seeded `r12` value, as enumerated in the CSV files.
- The parent initializes or writes all eight even offsets `0x00..0x0E` before
  or within its loop. The callees do not all touch every slot.

## Inference, alternative explanations and unknowns

- **HYPOTHESE:** The first two callees are constant-producing helpers and `r4`
  is their result register. The verified basis is only the callee assignment
  followed by the caller-side store. An alternative is a broader convention
  in which `r4` is merely preserved/communicated state; static bytes alone do
  not decide this.
- **HYPOTHESE:** `r12` communicates the base of a caller-created local context
  to the three larger callees. The verified basis is the immediate seed plus
  the bounded relative accesses. An alternative is that `r0`/`r12` denote a
  non-stack scratch object under a compiler-specific convention.
- **OFFEN:** source-level field widths/types, signedness, pointer identity,
  ownership, complete callers, condition truth, return mechanism, clobber set,
  DPP/address-space binding, SFR meaning, K-Bus purpose and runtime behavior.
- No observation in this package upgrades FW30 findings to FW31 or hardware.

## Verification

`validate.py` rechecks the composite identity, the five parent call rows,
selected exact parent/callee instruction rows, CSV shape and the stated
relative-offset sets. This is root **Self-Review**, not an independent review.
Device, target-network, VM, runtime and hardware tests are **NOT_RUN**.
