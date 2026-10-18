> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-271 — conditional timer edges in `FUN_002ff594`

## Result

**VERIFIZIERT (bounded local instruction and arithmetic facts):** In the exact `codesys3` body `[0x2ff594,0x2ff84c)`, after the local sample at `0x2ff748` is copied from `r0` to `r6`, instruction `0x2ff750` branches directly to Hook setup at `0x2ff75c`; it does not test `r6`. After the Hook call at `0x2ff76c`, exact return value `10` branches to the zero test at `0x2ff754`. If `r6` is zero there, the local path returns to Hook setup at `0x2ff75c` without taking another time sample. Therefore, a repeated retry cycle without resampling is possible under the stated return, register-preservation, frame, and memory conditions, but the initial sample always precedes the first Hook call on this path.

For nonzero `r6`, the local path branches to an opaque time call at `0x2ff7b8`, computes a 32-bit difference, then takes `BLS` back to the Hook setup when the unsigned difference is at most 9,999. A difference of 10,000 or more leaves that retry edge and reaches the subsequent selector gate; selector words 15 or 17 pass the visible gate to the row update at `0x2ff788`. Subtraction wraps modulo (2^{32}). A separate sequence compares another locally calculated delta with `0x7d00` and uses `BCS`, so its branch is taken for unsigned values greater than or equal to 32,000.

These are conditional source-level control-flow and arithmetic results. **The value 10 is only the literal tested by `CMP`; no busy/error meaning is assigned.** Clock units, domain, progression, and successful output writes remain conditional. The corrected WP-267 report is used only as a hash-bound summary: it describes an installed provider candidate and an arithmetic result consistent with milliseconds under an unverified output contract; it does not establish the runtime import winner or clock domain.

## Source, bounds, and scope

The source ELF is the pinned `codesys3`, 5,181,396 bytes, SHA-256 `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`. Accepted WP-252 bounds the exact core body as `[0x2ff594,0x2ff84c)` (696 bytes, 174 A32 words), and its instruction matrix binds the source words. This package checks only this body and the exact instruction sites needed for the timer transitions. It does not inspect other function implementations. The installed timer-provider report WP-267 is cited by report hash only; no WP-267 DSO body, helper, import implementation, or loader path is reopened here.

The core's call at `0x2ff748` targets encoded address `0x7b1d4`; `0x2ff7b8` has the same target. These are static call destinations. Runtime symbol resolution and effects are not observed. The WP-267 summary hash is `e994d116833051519fea291db8922630fd3bfc1acfe03c02e138c95db3581051` and its relevant limits are retained: provider candidate is not runtime binding; a millisecond interpretation requires a suitable provider/output contract; monotonicity and clock domain remain **OFFEN**.

## Exact zero-`r6` retry cycle

The path begins on the local edge where `r9==0` at `0x2ff740`: `BNE 0x2ff620` is not taken, the direct call at `0x2ff748` returns to `0x2ff74c`, and `MOV r6,r0` records the returned word. The unconditional `B 0x2ff75c` at `0x2ff750` bypasses the zero test entirely, so this sample is followed by a first Hook call regardless of whether the sampled word was zero. After a Hook return, `CMP r0,#10` at `0x2ff770` controls the branch at `0x2ff774`. If the return equals 10, the branch goes to `0x2ff754`; if `r6` is zero, `BNE 0x2ff7b8` is not taken and execution returns to `0x2ff75c`, preparing another Hook call without sampling time.

On a Hook return, `CMP r0,#10` at `0x2ff770` controls the branch at `0x2ff774`. If the return equals 10, the branch returns to `0x2ff754`. If `r6` is still zero, the code again skips `0x2ff7b8` and prepares another Hook. Thus, repeating this local cycle requires all of the following:

- the relevant path reaches the first sample with `r9==0`, and that call returns to `0x2ff74c`; its returned value becomes local `r6` (zero is required only for the later no-resample edge, not for the first Hook call);
- each Hook call returns to `0x2ff770` with `r0==10` and preserves `r6==0`;
- the stack/frame, row fields, and loop registers used by the subsequent instructions remain usable and retain the values needed to repeat the local path.

Those call effects and state conditions are **HYPOTHESES**, not established ABI behavior. If a Hook result is not exactly 10, the equality branch is not taken and execution enters the separate selector-gate sequence at `0x2ff778`; this countercase shows why the source does not make every Hook return a timer retry. The source does not define what 10 means.

## Nonzero timestamp and unsigned wraparound

With nonzero current `r6`, `BNE` at `0x2ff758` reaches the call at `0x2ff7b8`. After it returns, `SUB r0,r0,r6` at `0x2ff7c0` computes the low 32 bits of the difference. The code compares that result against `0x270f` (9,999) and uses `BLS` at `0x2ff7c8` to retry at `0x2ff75c` when the unsigned difference is **≤ 9,999**. Exactly 9,999 retries; exactly 10,000 does not take this branch. If a word at `[current r4-4]` is 15 or 17, the later `(word-15)&~2` gate at `0x2ff7cc..0x2ff7d8` reaches `0x2ff788`, where the body increments its local row counter and row pointer. This identifies a local exit from the timer-retry edge, not a system-level completion or error state.

The arithmetic is modular: `D = (new_sample - old_r6) mod 2^32`. Examples checked by the validator:

| Old value | New value | Modular delta | `BLS` at 9,999 | Resulting local edge |
|---:|---:|---:|---|---|
| `0x000003e8` (1,000) | `0x00002af7` (10,999) | 9,999 | taken | retry |
| `0x000003e8` (1,000) | `0x00002af8` (11,000) | 10,000 | not taken | selector gate follows |
| `0xfffffff0` | `0x00000020` | 48 | taken | retry after wrap |
| `0xfffff000` | `0x0000170f` | 9,999 | taken | retry after wrap |
| `0xfffff000` | `0x00001710` | 10,000 | not taken | selector gate follows |

The paired examples exercise both sides of the exact threshold; no observed samples are claimed.

This countercase requires the `0x2ff7b8` call to return with a usable current sample in `r0`, and `r6` to still contain the intended old sample. The Hook and timer calls must also return to their local continuations and preserve the live state needed by the row scan. No such preservation follows from register syntax or an assumed calling convention. Without these conditions, the local code still computes from then-current registers; the elapsed-time interpretation is not justified.

## Separate `0x7d00` / 32,000 gate

The separate local sequence first gets a value at `0x2ff6a4` and copies its returned `r0` to `r6` at `0x2ff6a8`. Another edge reaches the call at `0x2ff6b0`; after that call, `r0` is copied to `r12`, then `r12-r6` is formed at `0x2ff6c4`. `CMP r12,#0x7d00` is at `0x2ff6c8`; the immediate is exactly 32,000. `BCS 0x2ff708` at `0x2ff6d0` is taken iff the unsigned subtraction result is at least 32,000, including equality. Values below 32,000 fall through to the next instruction at `0x2ff6d4`.

This is a distinct gate from the 9,999 `BLS` sequence. It uses its own local `r6` baseline and another opaque sample call. Interpreting it as elapsed time requires both calls to return suitable samples, the old value in `r6` to survive the second call, and compatible sample units. The local arithmetic alone does not identify either the clock domain or subsequent branch meaning.

## Evidence and validation

- `source-pins.tsv` pins the exact `codesys3`, WP-252 core report and instruction matrix, and WP-267 report summary. The WP-267 report is a summary-only input.
- `instruction-witness.tsv` contains selected exact WP-252 rows for `0x2ff6a4..0x2ff6d0`, `0x2ff740..0x2ff790`, `0x2ff7a0`, and `0x2ff7b8..0x2ff7d8`.
- `state-transitions.tsv` enumerates the sample, zero retry cycle, nonzero threshold path, wraparound, separate 32,000 comparison, and each opaque-call obligation.
- `validate.py` is read-only and standard-library-only. It checks hashes and sizes for the exact source and summary inputs, confirms the accepted 174-word body is contiguous and matches its source bytes, reconstructs the selected witness, checks branch targets/opcodes at the timer edges, and runs fixed mathematical tests for 9,999/10,000, modular wrap, and 31,999/32,000. It does not launch code or inspect other function bodies.
- **PASS:** `python3 validate.py`; **PASS:** `sha256sum -c manifest.sha256`. This is self-review, not an independent worker run.
- Runtime/import selection, actual Hook effects, time source behavior, execution counts, and real-world units remain **OFFEN**; runtime/VM/device/network checks are **NOT_RUN**.
