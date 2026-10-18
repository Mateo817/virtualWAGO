> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-294 — bounded GLib integer callback proof

## Finding

**VERIFIZIERT** — For the exact source candidate pinned from WP280, the 8-byte `g_int_hash` body reads one 32-bit word at the address held in `r0` and returns that word in `r0`. It performs no source-level store. The conclusion assumes the addressed 4 bytes are readable; this is not a null-check or API-contract claim.

**VERIFIZIERT** — The 24-byte `g_int_equal` body reads 32-bit words at `[r0]` and `[r1]`, subtracts the second from the first, then returns `(CLZ(diff) >> 5)`. On 32-bit arithmetic this is `1` exactly when the words are equal and `0` otherwise: subtraction wraps modulo 2^32, and its result is zero exactly for equal operands. The body has no store. Both word locations must be readable; no argument validation is present in this body.

**VERIFIZIERT** — In the 32-byte `FUN_000cac64` body, the `r1 == 0` edge branches to `0xcac58`, which lies outside this function body and is excluded. On `r1 != 0`, it saves `r0`, `r1`, and `lr` in a 12-byte stack frame, calls `FUN_000caa78`, restores the saved values into `r1`, `r2`, and `lr`, computes `r3 = saved_r1 * nested_r0` modulo 2^32, and returns the subtraction `saved_r0 - r3` in `r1`. Thus the exact returned-value equation is source-derived, while the numeric meaning of `nested_r0` is intentionally left unspecified here.

**VERIFIZIERT** — The nested 492-byte `FUN_000caa78` body is uniquely contiguous in retained REA body metadata, with 123 4-byte instructions. The raw-word destination audit over those 123 instructions finds no writes to `r4-r11`, `sp`, or `lr`; this is a verified instruction-footprint fact. It establishes whole-execution preservation only when every executed PC remains within these audited instructions and execution reaches a normal `bx lr`. The closed `r1 == 1` entry path meets this condition: `subs r2,r1,#1` produces zero, the immediately following `bxeq lr` returns directly, and neither instruction writes `r4-r11`, `sp`, or `lr`. For general `r1 != 0`, the computed-PC dispatch at `0xcaaac` has no target-bound proof in this package, so whole-call control closure and preservation are **OFFEN**. The zero-divisor branch at `0xcaa80` targets handler `0xcac58` inside the body; it is not taken for `r1 != 0`, but only the `r1 == 1` path is claimed closed here. No complete quotient semantics are claimed.

## Register and memory effects

The exact raw source words for all four bodies are in `instruction-words.tsv`; the first three bodies are paired with the complete retained REA analyze-function results under root WP294. The nested helper's full 123-row assembly view is retained in `nested-assembly.json` and identifies parent analyze evidence `ev_ac3fce592aaccd0500fda5f7177e0620488d079c7963583ddef95fe2f2492fa1`, with complete assembly-view evidence `ev_30fedba43805e2bac6190a7a5001ac10b327ac342042c8b51d719d269fbda79b` (123/123 rows, exhausted). Ghidra image base is 0x10000, so each ELF VA is Ghidra VA minus 0x10000.

| Body | Read/write behavior derived from instructions | Preserved source-visible state |
|---|---|---|
| `g_int_hash` | Read 4 bytes at `[r0]`; no store | `r4-r11`, `sp`, `lr` |
| `g_int_equal` | Read 4 bytes at `[r0]`, then 4 bytes at `[r1]`; no store | `r4-r11`, `sp`, `lr` |
| `FUN_000cac64`, `r1 != 0` | Stack save `[sp-12,sp)` for `r0,r1,lr`, nested call, restore same 12 bytes; arithmetic only otherwise | On the closed nested `r1 == 1` direct-return route, `r4-r11`, `sp`, and `lr` are preserved by visible instructions. For general nonzero divisor values, whole-call preservation is **OFFEN** because nested computed-PC targets are not bounded here. |
| `FUN_000caa78`, raw 123-word body | Destination audit finds no writes to `r4-r11`, `sp`, or `lr` in the audited words | This is a bounded instruction-footprint result, not whole-call preservation for general inputs; whole-call preservation is verified only on the closed `r1 == 1` direct-return path |

These are instruction-derived effects for the bounded bodies and stated conditions, not ABI or calling-convention conclusions. The nested function's computed-PC dispatch means its general nonzero-input control closure and returned quotient are outside this package's claim.

## Dal-side boundary context

**VERIFIZIERT** — On the exact WP202 libdal file (SHA-256 pinned below), local `readelf -rW` and `readelf -sW` show `R_ARM_GLOB_DAT` at ELF `0x14140` for undefined dynamic symbol index 36 `g_int_equal`, and at `0x14144` for undefined dynamic symbol index 51 `g_int_hash`. The accepted WP223 body summary identifies loads at `0x1c80` (`r0 = [r6 + r3]`, with literal `r3=0x144`) and `0x1c88` (`r1 = [r6 + r1]`, literal `r1=0x140`). Therefore, **conditional on current `r6 == 0x14000` at those loads**, the values loaded from those GOT slots are passed as `r0=hash` and `r1=equal`. WP223 derives an earlier `r6=0x14000` (ELF VA) from its literal `0x123fc` added to the ARM PC value `0x1c04`; opaque intervening calls mean that current `r6` equality at `0x1c80/0x1c88` is **OFFEN**. This is a conditional register/value relationship only: no constructor implementation, callback-table field identity, or runtime binding was inspected. WP223's body at `0x1bec` is used only for its stated address/literal observations, not as the entry/callee implementation.

**HYPOTHESE** — If a lookup's callback slots are stipulated to contain these exact two source candidates and each callback input points to readable 32-bit storage, this source proof supplies their callback computation and bounded register effects. Actual slot binding, complete lookup behavior, and runtime selection remain **OFFEN**.

## Validation and limitations

The validator is read-only. It checks exact provider/source pins, ELF segment mapping, source-byte-to-REA-address correspondence and body coverage. A bounded A32 destination decoder checks `r4-r11`/SP/LR writes against raw instruction words for the hash/equality and nested bodies; the helper save/restore sequence is checked separately. It verifies the short callback instruction formulas and the WP202 relocation names. It does not execute ARM instructions or emulate GLib/Dal. Checks: **PASS** for source pins and instruction correspondence; **NOT_RUN** for runtime, ABI, lookup integration, and live Dal relocation/call binding; the static relocation names and the WP223 conditional address arithmetic were checked offline.

**VERIFIZIERT** — The `g_int_equal` arithmetic from its two readable 32-bit inputs yields `1` for equal words and `0` for unequal words. **OFFEN** — No API signature or callback contract is independently established here. **OFFEN** — The nested helper's result and whole-call control/register effects for general nonzero divisor inputs are not fully characterized. This work is not proof that the provider candidate is dynamically selected.
