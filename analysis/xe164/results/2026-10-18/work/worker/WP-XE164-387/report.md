> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-387 — explicit strcmp boundary correction for the selected lookup fixture

WP387 preserves WP374's 237-word subject scope and WP314/WP330/WP346-derived source lineage. It corrects the literal coordinate prose, labels the mismatch boundary as not returned, and makes the selected opaque strcmp boundary's necessary memory/register state explicit. WP374, WP381, and upstream packages remain unchanged.

## Source correction and lineage

The helper's literal is at ELF VA `0x20c4` and file offset `0x20c4`; its little-endian value is `0x00012120`. The value `0x12120` cannot be a file offset in this 18,076-byte object. The LDR at `0x20b0` has architectural PC `0x20b8` and displacement `0xc`, reaching VA/file offset `0x20c4`. The ADD at `0x20b8` uses architectural PC `0x20c0`, adds the literal value to form `0x141e0`, and the LDR at `0x20bc` reads `[r3,#4]`, i.e. DalBias+`0x141e4`. The `+0x141e0` fixture word is a distinct decoy. WP374's raw-byte validator checked file offset `0x20c4` and value `0x12120` correctly; only its report paired the value with the file-offset label.

`stepper.py` descends from the frozen WP374 source stepper, which in turn documents WP314's bounded A32 decoder ancestry. WP387 copies and pins the WP374 237-word ledger and exact libdal/GLib source bytes. It replays the four original synthetic traces in memory and confirms the pre-correction instruction histories remain identical. No ELF code executes.

## Explicit boundary state and memory

The chosen `strcmp` call is reached from `g_str_equal` with `r0=stored-key`, `r1=query-key`, `r6=table`, `r11=slot byte offset`, SP=`entrySP-48`, and LR/normal-return PC at the GLib `g_str_equal` continuation. For the four positive routes, `strcmp` return `r0=0` is stipulated. `r6`, `r11`, SP, and normal return to the recorded PC remain fixed across the boundary.

`opaque-memory-premises.tsv` records the exact post-call footprint for each case:

- the active 48-byte stack range `[SP, entrySP)`, containing the 8-byte `{r4,lr}` save used at `g_str_equal`'s pop and the 40-byte lookup save used by its final pop;
- the table bucket-array pointer word at `table+0x1c` and value-array pointer word at `table+0x20`;
- the bucket hash word at the selected slot and the value-pointer word at that same slot.

Each span has concrete bytes before/after the opaque event. The read-only validator checks these bytes against the exact subsequent source reads and stack restores in the source trace. No general memory-preservation behavior is asserted. Other memory may change; the model checks only that its finite probe leaves the listed spans intact.

A separate finite clobber probe changes one mapped, unrelated scratch word to `0xdeadbeef`, overwrites `r1-r5`, `r7-r10`, `r12`, `r14`, and NZCV at the opaque boundary, while retaining only result `r0`, live `r6/r11`, SP, the normal-return control transfer, and the listed memory spans. The fetched source continues to return T, and its own pops restore entry `r4-r11` and SP. This is a selected source-path witness about scratch state, not an ABI or actual strcmp claim.

## Controls and validation

The mismatch control has no source return: it stops before executing next-probe PC `0x45de0`. WP387's summary writes `return=NOT_RETURNED`, with no numeric return value. The empty-first-bucket control retains its real zero return.

The separate `run_cases.py` is the optional writer. Default `validate.py` imports `replay.py` with bytecode writing disabled, regenerates expected source histories and event ledgers in memory, compares all frozen baseline trace rows and new probe/boundary artifacts, checks exact raw words and literal arithmetic, verifies the protected memory values and scratch-clobber result, checks the control status, and verifies its own file inventory did not change. Native execution and runtime library resolution are **NOT_RUN**.

The positive T route is **HYPOTHESE** under the stipulated finite strcmp result and explicit boundary premises. Runtime provider selection, constructor/table reachability, actual strcmp memory effects, general lookup semantics, API/ABI guarantees, and physical effects remain **OFFEN**.
