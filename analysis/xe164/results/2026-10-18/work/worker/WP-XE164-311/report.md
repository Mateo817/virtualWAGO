> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-311 — static callback-publication map for `libpackbus_open`

## Result

**VERIFIZIERT (bounded source claim):** Exact FW31 `libpackbus.so.1.0.1` bytes map the selected `libpackbus_open` body at Ghidra `0x20720` to 407 A32 words across `[0x20720,0x20cff]` and `[0x20dd8,0x20e53]`, with a separate 54-word pool at `[0x20d00,0x20dd7]`. The body stages 16 callback words from `R_ARM_GLOB_DAT` GOT slots, then conditionally writes them as four 16-byte vectors to current `r4+0x14`, `+0x24`, `+0x34`, and `+0x44`. It also writes two literal `0x2ee0` words at `+4/+8`, current `r6` at `+0x10`, and three separate GOT-derived callback words at `+0x54/+0x58/+0x5c`. Exact per-word mappings are in `callback-publication-matrix.tsv`; complete source instruction and pool words are retained separately.

The publication is reached only when the local compare at `0x209ec` sees current `r4 != r6`: equality takes `BEQ 0x20a58` around the publication sequence. This says nothing about whether a real runtime reaches the path. The local body copies entry `r0` to `r4` at `0x20738` and entry `r1` to `r6` at `0x20730`; later opaque calls mean neither entry identity nor the local zeroing of `r6` at `0x20938` is asserted to persist. The late three GOT reads additionally require current `r11==0x43000`. The vector GOT reads and D-register loads occur before the first BL at `0x20840`, but opaque calls follow those loads and precede publication; retention of `d8-d15` is conditional. No ABI preservation rule is assumed.

## Numeric callback positions

The exact relocated names and numeric offsets are reported as names exported by this object, not function prototypes or semantic contracts. The four vector stores contain:

| Store | Current base offsets and source lanes |
|---|---|
| `VST1.32 {d14,d15}` at `0x20a10` | `+0x14 ReadBit`, `+0x18 ReadBytes`, `+0x1c WriteBit`, `+0x20 WriteBytes` |
| `VST1.32 {d10,d11}` at `0x20a1c` | `+0x24 ReadStart`, `+0x28 ReadEnd`, `+0x2c WriteStart`, `+0x30 WriteEnd` |
| `VST1.32 {d12,d13}` at `0x20a24` | `+0x34 ConfigureSubdevice`, `+0x38 ConfigureDevice`, `+0x3c DiagGetDeviceState`, `+0x40 DiagGetSubdeviceState` |
| `VST1.32 {d8,d9}` at `0x20a2c` | `+0x44 Close`, `+0x48 GetDeviceSpecificFnList`, `+0x4c ApplicationStateChanged`, `+0x50 WatchdogSetTime` |

The six cyclic operation labels (ReadStart, ReadBytes, ReadEnd, WriteStart, WriteBytes, WriteEnd) are separately cross-referenced to the accepted WP057 consumer summary. That is a positional match between this provider’s exported relocation names/offsets and the summary’s consumer slots; it does not prove a selected runtime binding, prototypes, or callback effects. The `+0x54`, `+0x58`, and `+0x5c` WatchdogStart/Stop/Trigger words are late GOT loads and remain a separate backend callback group. `+4` and `+8` each receive `0x2ee0`; the “read-length” and “write-length” labels are contextual position labels only.

## Relocation and source calculation

The pool word at Ghidra `0x20d10` is `0x228b8`. The instruction at `0x2072c` loads it, and `add r11,pc,r11` at `0x20740` uses architectural PC `0x20748`, producing Ghidra-domain GOT base `0x43000` (ELF address `0x33000`). For every staged callback, the pool literal supplies a numeric offset; the code loads `[r11, offset]`; ELF `readelf -rW` reports an exact `R_ARM_GLOB_DAT` symbol at the corresponding ELF GOT slot. The full 16-entry literal-to-GOT table and three late backend entries are retained in separate TSVs.

At `0x209fc`, `VLDR.64 d16` reads pool Ghidra `0x20d08`, whose two little-endian words are `0x2ee0`; `VST1.32 {d16}` at `0x20a04` writes them at current `r4+4` and `r4+8`. The store table includes address setup and vector extents, while `instruction-words.tsv` preserves every decoded body word. The pool table is intentionally separate so pool contents are never counted as executable instructions.

## Consumer and possible address join

The accepted WP057 summary reports the six cyclic consumer operations at selected `IoDrvDal` callsites. The provider matrix preserves the exact offsets and relocation names, and the consumer summary is cited only for those reported callsites. Other offsets remain source mappings whether or not that summary reports a consumer.

WP301 separately reports that its `IoDrvDal` callsite at ELF `0x226c` forms current `r0=current r6+0x110`. The provider’s potential output expression is current `r4+0x110` only if the selected current `r4` is the provider record base. These expressions coincide if the two current base registers equal the same `T`; no evidence here establishes object identity, cross-call register preservation, or that the candidate provider and consumer are joined at runtime. This is an address-expression comparison only.

## Preservation and limits

`preservation.tsv` and `conditions.tsv` make the assumptions explicit. In particular, the 16 vector GOT values are fetched and staged before opaque calls, but the VFP values must survive those calls to reach the VST instructions. The late backend callback loads require the current GOT base in `r11`. `r4` must still name the intended output base; current `r6` controls the local lane gate and supplies the `+0x10` store. The bounded body later restores `d8-d15` at `0x20bd8` and returns through the saved core-register frame at `0x20bdc`; interpretation still assumes the opaque calls did not invalidate the active stack/frame or overwrite saved values. Non-aliasing with other live data is also a condition, not an inferred ABI guarantee.

The body includes further opaque calls and external state effects. This package does not expand any callee, infer callback prototypes or lifecycle semantics from names, establish that the 16 entries have a public C structure layout, prove callback target resolution at runtime, or claim a device/runtime path. WP310’s comparison establishes exact byte identity between the extracted FW31 candidate and the historical FW30 candidate only; it is not a general firmware or ABI equivalence claim.

## Inputs and validation

Source hashes and sizes, including the root310 REA body/procedure and retained symbol-resolution evidence, the historical candidate, WP057 consumer summary, and WP301 argument summary, are listed in `source-pins.tsv`. `validate.py` independently checks those pins, byte identity, complete body/pool word coverage, exact instruction bytes, relocation/symbol mappings, store coverage, and key branch/literal arithmetic. It performs static file/metadata checks only; no ELF is executed.

**Validation: PASS** — read-only static validator. **Target execution: NOT_RUN.** Review status: worker self-review; no independent review is claimed.
