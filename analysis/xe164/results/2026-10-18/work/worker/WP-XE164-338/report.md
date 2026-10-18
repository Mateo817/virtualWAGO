> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-338 — independent numeric transition and watchdog-tail review

**VERIFIZIERT, source-local and conditional:** the state-2 sentence in frozen WP-XE164-325 reverses which branch reads `P+0xa1`. There are three state-2 routes in the reviewed slice. Two reach `fcb4`, read the byte at `P+0xa1`, normalize zero/nonzero to 0/1, and store that value at `P+0xa0`. The remaining route—policy `[P+0x9c]==1`, the fresh `[P+0x0c]` load at `fd30` equals 1, and current `r4==2`—branches from `fd40` directly to `fcc0`; it does not read `P+0xa1`. On that path `r2` still contains the loaded numeric 1, so `STRB` writes 1 to `P+0xa0`.

The review uses WP325’s frozen package and the accepted WP321 source-word/REA records, bound in `source-pins.tsv`. The exact FW31 provider ELF is 148,792 bytes with SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. The 193 selected source words and nine pool words match the accepted WP321 ledgers and are checked against the raw ELF. No native code was executed.

## Corrected state-2 paths

The relevant encoded path is:

| Predicate | Source route | `P+0xa1` read? | Value at `STRB [P+0xa0]` |
|---|---|---|---|
| `r4==2`, policy word differs from 1 | `fca8` not taken; `fcb0` not taken; `fcb4` | Yes | 0 if the loaded byte is zero, otherwise 1 |
| `r4==2`, policy is 1, fresh prior word at `fd30` is 1 | `fca8 -> fd30`; `fd38` not taken; `fd40 -> fcc0` | No | 1, still in `r2` from `fd30` |
| `r4==2`, policy is 1, fresh prior word at `fd30` differs from 1 | `fca8 -> fd30`; `fd38 -> fe14`; `fe18 -> fcb4` | Yes | 0 if the loaded byte is zero, otherwise 1 |

The branch words and recomputed targets are checked in `validate.py`. In particular, the direct path’s only instructions between `LDR r2,[r3,#0xc]` and `STRB r2,[r3,#0xa0]` are comparisons and conditional branches. They do not write `r2`. The original WP325 report’s sentence at its state-2 paragraph says the direct path reads `P+0xa1`; that is incorrect. The corresponding route predicate and store ledger also fail to distinguish the direct `r2=1` store from the byte-normalizing routes. WP325 remains untouched; `application-state-matrix-reviewed.tsv` and `state2-paths.tsv` give the corrected account.

The `P+0xc` value at `fd30` is a new load. It is distinct from the earlier retry-gate read at `fc94` and later continuation read at `fcd4`; equality between those reads is not assumed. After the `a0` store, further source-local stores include `P+0xa2=1` and `P+0xc=2`; the latter is not described as final state after later opaque calls. Entry `r0` is copied into `r4`, but preserving `r4`, the current pointer/registers, stack data, or object memory across earlier opaque calls is a condition for the route. The global pointer cell is source-relative ELF address `0x44420`; its runtime contents and object identity remain open.

The retry lane for a non-3 current state whose observed prior word is 3 calls opaque targets and then rereads state. This package claims no convergence or termination. No enum or API meaning is assigned to the numeric states or stores.

## Watchdog wrapper tails

The four wrappers use the same source-relative pointer-cell address. A null pointer follows a local `BEQ` to `MVN r0,#0` and `BX LR`, yielding the locally established `0xffffffff` return word. For a nonnull pointer each loads `[P+0xdc]` into `r0` and transfers with a direct branch to the corresponding three-word PLT stub. `WatchdogSetTime` additionally copies entry `r0` to `r12`, entry `r1` to `r2`, then copies saved entry `r0` to `r1` before transfer. The other three wrapper bodies do not write `r1` or `r2` before the transfer.

The raw PLT sequences are `ADR r12`, `ADD r12,r12,#0x2b000`, then pre-indexed `LDR pc,[r12,#offset]!`. Their computed GOT slots and the exact `R_ARM_JUMP_SLOT`/dynamic-symbol records are checked against the pinned ELF. The wrappers themselves have no local frame adjustment; the stubs do not write `r0-r3`, SP or LR. These facts establish only the local transfer boundary. They say nothing about the target’s contract, ABI, runtime GOT contents, return behavior or physical watchdog effect.

## Validation and scope

`validate.py` is read-only. It rehashes every pinned input, confirms the frozen WP325 manifest, compares the WP321 and WP325 source ledgers, checks each source word at its ELF file offset, checks state-2 branch destinations and numeric route controls, and checks watchdog forwarding, veneer arithmetic, dynamic relocations and symbol values. It does not load or execute the ELF. `claim-matrix.tsv` records the bounded findings and open dependencies. The machine-readable status vocabulary is `VERIFIZIERT | HYPOTHESE | OFFEN | BLOCKED`; no runtime claim is made.
