> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-375 — selected SetTime paths fetched and replayed from raw words

**VERIFIZIERT, bounded source model:** A read-only model fetches and decodes each instruction on nine selected SetTime inputs using the frozen 54-word body and six literal-pool words, bound to exact FW31 ELF bytes. It records complete before/after GPR0–14, source PC and architectural PC, next PC, NZCV, D16 state, and individual read/write effects. It reproduces all eight WP360 numeric cases and its stored bytes, and adds a null-pointer route. Two synthetic pointer/stack bias fixtures produce the same numeric state and memory values at different addresses. All three invalid paths stop before their actual logger BL; the BL instruction itself is not executed and no return is assumed.

**PASS:** raw source mapping, 18 machine traces, 394 fetched instruction rows, 132 memory effects, cross-checks against the frozen WP360 numeric/store tables, and fresh in-memory serialization checks. **OFFEN:** the external meaning of the parameters and stored fields, units, ABI, runtime, lifecycle, logger effects, and hardware behavior. No target/native execution occurred.

## Source identity and method

The subject is `libpackbus.so.1.0.1`, 148,792 bytes, SHA-256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. The raw instruction inventory contains exactly 54 SetTime words at ELF `0x14cc8..0x14d9c`; the six adjacent literal words are at ELF `0x14da0..0x14db4`. Every word and pool value is checked against the ELF file bytes. The Ghidra address relation is ELF address plus `0x10000`, also checked. WP354 and WP360 source-manifest hashes are retained alongside the copied WP360 case and memory tables.

`model.py` starts at Ghidra `0x24cc8` and fetches an instruction only when its PC is present in the pinned source map. Its bounded A32 decoder handles encoded conditions and branches, data-processing immediate and shifted-register forms, MOVW/MOVT, MUL, UMULL, MLS, word LDR/STR, block save/restore, and the two exact NEON words for zeroing D16 and storing it. Branch targets use the encoded displacement and current NZCV; PC-relative reads and ADDs use the architectural `PC+8`. The six pool values are mapped into the matching Ghidra address domain. The NEON path models D16 as a 64-bit value and VST as its eight little-endian bytes.

The fixtures use two explicit writable buffer/stack address pairs: `P=0x20000000, SP=0x71001000` and `P=0x31002000, SP=0x72003000`. Each output buffer starts with `0xa5` sentinels, and each stack has a synthetic entry frame with r4=`0x44444444` and LR=`0x12345678`. The frame and output range are disjoint. These are model preconditions, not observed runtime addresses or ABI claims.

The optional `generate.py` creates `trace.tsv`, `results.tsv`, and `memory-events.tsv`. The default `validate.py` does not call it or open output files for writing. Instead, it fetches and replays every fixture in memory, serializes those fresh results for comparison with the frozen generated tables, checks raw-word identity at every fetched PC, independently verifies conditional branch destinations, compares numeric rows and memory bytes to WP360, and checks that file hashes are unchanged across validation.

## Selected paths and results

The nine fixtures are N=1, 999,999, 1,000,000, 1,000,001, the maximum accepted `0x3fffffff`, `0xffffffff * 0xffffffff`, `65536 * 65536`, first above-limit `0x40000000 * 1`, and a null pointer. Each runs under both bias fixtures, yielding 18 traces. For non-null inputs, `MUL` supplies the actual low-word N in r2. The zero check and `CMN`/unsigned-BHI gate determine whether the quotient path is fetched. For the null fixture, the source null branch occurs first; the product is marked `NOT_REACHED_NULL` rather than treated as a machine result.

The source-derived successful stores match WP360: `P+4=N`, `P=1`, `P+8=Q`, `P+0x0c=R*1000`, and eight zero bytes at `P+0x10..0x17`. `VST1.32 {d16},[r1]` writes exactly eight bytes from zeroed D16 in this selected path. The `0xa5` tail at `P+0x18..0x1f` has no write event. The pushed r4/LR words are recorded separately from output memory; successful `LDMIA sp!,{r4,pc}` restores r4 and the entry SP and branches to the saved local return address `0x12345678`. This describes the instruction path, not a calling-convention promise.

For wrapped zero, above-limit, and null-pointer inputs, trace fetching ends immediately before the respective raw BL at `0x24d4c`, `0x24d70`, or `0x24d94`. The BL encodings resolve to Ghidra `0x175cc`, but the call is not executed. The trace records argument setup and the still-pushed frame; it does not model logger effects, any later return value, or frame cleanup after that call.

## Evidence limits

The replay proves the listed state transitions only for these selected source paths and stipulated memory fixtures. It does not prove that actual callers provide these registers, buffers, or stack frames. It assigns no semantics to the function name, fields, parameters, values, or opaque logger. API contract, units, ABI, runtime, lifecycle, and physical watchdog behavior remain **OFFEN**. WP360 and WP373 remain unchanged; this package compares against their frozen numeric and store evidence without treating their manually scripted SetTime trace states as the execution oracle.
