> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-357 — independent review of WP347 fixture paths

**VERIFIZIERT (selected static source paths, under synthetic fixture memory premises):** I independently matched WP347's 433 copied instruction words to the exact pinned FW31 `libffi.so.8.1.4` bytes, checked all six recorded traces' fetched PC/word sequence against those maps, and re-evaluated the reached conditional instructions from source-updated NZCV. The three nonempty numeric-mode-2 fixtures reach and return from the actual classifier at ELF `0x6fe8`; each selected tag route returns numeric `r0=0`. The zero-argument mode-2 fixture takes the source's zero-count route without a classifier call. All recorded mode-2 paths restore their synthetic entry SP. The selected source executes `VMOV.I8 q8,#0xff` at ELF `0x76fc` then `VST1.8 {d16,d17},[r3]` at `0x7710`, writing sixteen `0xff` bytes at synthetic CIF `+0x20`. The accepted mode-1 fixture takes a separate source lane with no classifier call or NEON initialization; the numeric mode-3 control rejects before CIF writes. Selected type-object words match the raw local object bytes.

These are numeric observations on the recorded cases, not CIF/API/ABI contracts. Synthetic entry premises are record `0x10000`, SP `0x9000`, and type-object pointers at `ELF object RVA + 0x500000`; the argument array is at `0x30000` and contains the listed raw type pointers. The replay snapshots show r4-r12 restored for these six cases and SP returned to `0x9000`; this says only what the selected instruction trace and frame contents show, not what any ABI requires. No constructor reachability or runtime loader behavior is established.

The local trace checker re-derives condition outcomes for reached A32 instructions from CMP/TST/SUBS flag effects, checks computed/branch next PCs and return-to-call-site behavior, and verifies every trace word is at its raw-source address. It is an independent audit of the frozen trace artifact; it does not claim a separately implemented full CPU or validate unselected paths. The frozen WP347 validator itself imports its stepper and compares trace JSON with that same module's cases, so that check is an internal replay consistency check rather than an independent implementation comparison.

## Frozen WP347 prose erratum

WP347's report labels the classifier range as ELF `[0x16fe8,0x17094)`. Those addresses are the Ghidra range. The actual ELF code range is `[0x6fe8,0x7194)` (107 words); the Ghidra range is `[0x16fe8,0x17194)`. The copied word table, traces, classifier call target, and actual path are correctly based at ELF `0x6fe8`; this is a report-only address-domain error. WP347 remains untouched.

## Limits

**OFFEN:** meaning of the numeric mode, tags, field values and result words; public ABI/prototype/type contract; constructor reachability of the synthetic record and arrays; runtime identity/relocation selection; all other flags, modes, type tags, argument counts, error cases, and unselected source paths. **NOT_RUN:** native/runtime, VM, device, network, hardware. No generator was run.
