> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-286 — conditional synthetic ComponentEntry composition

## Result

**VERIFIZIERT — bounded source-word mathematical replay.** The validator follows one explicitly synthetic path through the exact Dal `ComponentEntry` body and literal pool, both Dal PLTs, the exact provider getter and literal, the 136-byte provider object with its 34 in-object `R_ARM_RELATIVE` cells, the pinned 48-PC WP282 memcpy path, the Dal poststores and encoded epilogue. It reaches the stipulated return PC with `r0 = 0` in both fixtures. This is a conditional instance proof; it does not establish an API, structure layout, ABI, loader state, required lifecycle, or actual runtime behavior.

The source identity and boundaries are pinned in [source-pins.tsv](./source-pins.tsv). The exact Dal entry is ELF `[0x4448,0x4624)` (119 words) and its adjacent literal pool is `[0x4624,0x4678)` (21 words). The copied PLT window is `[0x9c8,0x9d4)`, the getter PLT is `[0x9d4,0x9e0)`, and the provider getter plus literal is `[0x3464,0x3474)`. The provider object occupies `[0x14154,0x141dc)`; the libc lane is the already accepted WP282 body `[0x919c0,0x91ea0)`. The validator rereads every scoped Dal word against the retained WP272 witness and verifies the 34 relative-relocation records against the provider ELF. It imports the hash-pinned WP282 `Machine` without changing it or executing the ELF.

The selected input is a 64-byte synthetic object with field `+0x28` set to zero. That makes the conditional branch at Dal `0x4524` go to `0x4530`; the callback setup and `BLX r2` words at `0x4528/0x452c` are not executed. The two GOT cells are directly stipulated to contain `provider_bias+0x3464` and `libc_bias+0x919c0`. Seven Dal global-pointer cells at offsets `+0x50/+0x54/+0x58/+0x5c/+0x60/+0x64/+0x68` each contain a separately stipulated valid mapped data address. These are fixture conditions, not claims about actual symbol resolution or the meaning of those cells.

## Fixtures and derived values

Both fixtures use page-aligned, mutually disjoint Dal/provider/libc biases. The actual arguments derived by the stepped Dal path are `D = DalBias+0x1a270`, `S = ProviderBias+0x14154`, and `r2 = 0x88` (136). Consequently `D mod 16 = 0` and `S mod 16 = 4`; both ranges are mapped, readable/writable as needed, nonoverlapping, and disjoint from the mapped stack. The source bias is deliberately left page aligned, preserving the observed `+4` low-nibble difference.

| Fixture | Dal bias | Provider bias | libc bias | D | S |
|---|---:|---:|---:|---:|---:|
| A | `0x50000000` | `0x62000000` | `0x71000000` | `0x5001a270` | `0x62014154` |
| B | `0x43000000` | `0x58000000` | `0x70000000` | `0x4301a270` | `0x58014154` |

For each fixture, the nested memcpy destination immediately at its return equals all 136 bytes of the relocated provider object, and the source remains unchanged. The six candidate words survive the subsequent Dal stores and retain the relocation-derived values:

| Object offset | Provider ELF cell | Raw REL addend | Fixture A final word | Fixture B final word |
|---:|---:|---:|---:|---:|
| `+0x30` | `0x14184` | `0x2f98` | `0x62002f98` | `0x58002f98` |
| `+0x3c` | `0x14190` | `0x2e5c` | `0x62002e5c` | `0x58002e5c` |
| `+0x40` | `0x14194` | `0x2e04` | `0x62002e04` | `0x58002e04` |
| `+0x44` | `0x14198` | `0x2dac` | `0x62002dac` | `0x58002dac` |
| `+0x50` | `0x141a4` | `0x2c70` | `0x62002c70` | `0x58002c70` |
| `+0x54` | `0x141a8` | `0x2c18` | `0x62002c18` | `0x58002c18` |

These equalities derive from the raw object words plus the explicitly modeled `bias + addend` relocation arithmetic. Dal writes later overwrite other locations inside the 136-byte copied range: `+0x00/+0x04` receive `DalBias+0x209c`; `+0x10/+0x14/+0x6c` receive `DalBias+0x20c8`; and `+0x88` receives zero just beyond the 136-byte range. Three global-pointer values used at `+0x8c/+0x94/+0x98` are also stored beyond the copied range. These poststores are traced instruction effects, not part of the memcpy equality.

Before the getter call, the four actual `STMIA` blocks stage exactly 60 bytes from the then-current entry-object bytes into `[D-0x3c,D)`. A separate Dal `VST1` writes 16 bytes at entry `[+0x04,+0x14)`; the later `VST1 {d8,d9}` writes 16 bytes at `D+0x78..D+0x88`. The vector bytes at the latter location equal the two local 8-byte values actually loaded by the scoped `VLDR` instructions. The `VLD1.64` source word uses a 64-bit (8-byte) alignment qualifier, not a 64-byte alignment. Fixture entry SP is 8-byte aligned; after the observed 72-byte Dal frame adjustment, local SP remains 8-byte aligned. The copy itself writes `[D,D+0x88)`; poststores at `D+0x88`, `D+0x8c`, `D+0x94`, and `D+0x98` are separate and outside that 136-byte destination.

The Dal prologue saves five GPR words (20 bytes), then `d8/d9` (16 bytes), then reserves 36 local bytes, for 72 bytes total. The nested WP282 machine adds its separately evidenced 4-byte stack save. The trace shows the incoming Dal LR saved at `[SP-4,SP)` and loaded into PC by the final `LDMIA`; SP returns to its entry value. In these fixtures the final observed register values include `r0=0`, `r1=S+136`, `r2=0`, `r3` equal to the stipulated pointer at global cell `+0x68`, and `r12=D+136`. Dal-saved `r4-r7`, the live `r8-r11` sentinels, and Dal-saved `d8/d9` retain their initial fixture values. No ABI conclusion is inferred from those local instruction effects.

The full 174-step synthetic mapped-address trace is [execution-trace.tsv](./execution-trace.tsv): 117 executed Dal-body instructions (the two callback words are skipped), six PLT instructions, three getter instructions, and all 48 nested WP282 instructions through return. Its addresses are the synthetic fixture biases plus the scoped ELF offsets, not observed runtime addresses. [effects.tsv](./effects.tsv) records event order, kind, address, and length; PLD advice is separate from ordinary reads/writes. It intentionally contains no final-memory payload column. The read-only default validator freshly replays Fixture A and compares every trace row and every event span with the checked-in files; `--emit` explicitly regenerates the trace and effects from Fixture A.

## Negative controls and limits

The validator rejects nonmatching getter and memcpy GOT targets when control leaves the scoped code map. It also rejects a source pointer with the wrong selected low-nibble lane and an overlapping source/destination pair. Positive fixtures check all mapped ranges and stack separation before stepping. The model has byte-addressed memory and derives register values by decoding each executed scoped instruction; it is a bounded decoder for this path, with exact encodings for the reached VFP/NEON forms, rather than a general ARM emulator. WP282 supplies the separately reviewed memcpy body. Prefetch/cache behavior is only recorded as advice, and external loader, callback, global-cell meaning, hardware, and runtime behavior remain outside scope.

## Validation

`python3 validate.py` — **PASS**. It verifies source pins, all 119 entry words and 21 literal words, all 34 provider relative cells, both full synthetic executions, candidate-cell results, staged and vector writes, stack/register effects, and the negative route/lane/alias controls. This is the worker's own source-bound mathematical replay and self-review, not an independent review or native execution.
