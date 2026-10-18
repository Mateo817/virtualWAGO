> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-374 — selected string-name lookup composition

**Result:** VERIFIZIERT (source-local finite routes only). In four synthetic traces (two exact names under two distinct load-bias mappings), the pinned source instructions in libdal `helper20b0` load a table pointer through the cell at DalBias+0x141e4, branch through the exact `g_hash_table_lookup` PLT words, and enter the pinned local GLib lookup at GLibBias+0x45d6c. The traced lookup computes each query string hash from its signed-byte loads, executes the complete selected 131-word divide source range, compares the selected first bucket, calls the selected equality body, and returns the fixture value word T after the equality result is stipulated as zero at the strcmp boundary. The traces do not establish a real constructor, table population, dynamic loader winner, or process reachability.

## Evidence and source scope

The exact libdal source file is 18,076 bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. The locally extracted GLib candidate is 1,199,352 bytes, SHA-256 `3f927b8aae0e3e1b1296bde9009ba9fb9380f64ac26ebe8b7675638e3250cbc5`; candidate identity is source-bound, but runtime provider selection is OFFEN. `source-words.tsv` records 237 exact words: 5 from libdal helper20b0; 3 from libdal PLT 0x15f4; 79 from GLib lookup; 11 from `g_str_hash`; 5 from `g_str_equal`; 3 from GLib `strcmp` PLT; and the full 8+123-word division helper/body. The validator maps each word back through the source ELF PT_LOAD file mapping and verifies its bytes. Source lineage for the reused bounded decoder is WP314; this package adds and executes the reached MOVW/LDRSB forms. No new body was imported.

The helper literal word is at libdal ELF 0x20c4 (file offset 0x12120, value 0x12120). The PC-relative sequence uses PC 0x20c0 to form ELF-relative 0x141e0, then loads the word at +4, address DalBias+0x141e4. Fixture memory deliberately maps a decoy at DalBias+0x141e0 and the table pointer at +0x141e4. This distinguishes the table pointer from the separate integer value at the preceding cell without inferring object identity.

The libdal PLT at ELF 0x15f4 computes its GOT address at 0x140ec. Its relocation metadata names `g_hash_table_lookup`; each fixture stipulates that the GOT cell resolves to GLibBias+0x45d6c. The chosen GLib candidate’s `strcmp` PLT words at ELF 0x1c0c4..0x1c0cc compute GOT cell ELF 0x134044 (Ghidra 0x144044), whose relocation is `strcmp@GLIBC_2.4`. Each fixture stipulates that cell’s target token and a normal return from the opaque target. No implementation or semantics for strcmp are inferred from its name.

The two exact query names are copied from WP334’s bounded name inventory. Their local source-derived hashes are `libpackbus_Push` → 0x106b2344 and `libpackbus_read_table_9` → 0xc703821f. The corresponding U32 multiplication by 11 yields 0xb49a83ec and 0x8d269755. The selected encoded division route uses divisor 7 and returns quotient/remainder; in these cases the remainders are 2 and 3. This is a traced finite arithmetic path, not a general API or indexing claim.

## Preconditions and trace result

Fixture A uses DalBias 0x60000000 and GLibBias 0x61000000. Fixture B uses 0x68000000 and 0x69000000. Each has distinct mapped table, bucket, key, value, and stack addresses. For each positive route the stipulated numeric table words are 8, 7, and 7 at offsets +0,+4,+8; callback words at +0x24/+0x28 point to the exact selected GLib bodies. Explicit bucket, key, and value arrays place the query hash at the computed slot, the stored-key pointer at that slot, and value T there. The query and stored-key bytes are each the exact name plus a terminating zero. These are numeric memory premises, not proof that a constructor can create this state.

The lookup allocates/restores its source frame and performs the visible callback paths. At the `strcmp` PLT call boundary, r0 is the stored-key pointer and r1 the query-key pointer; SP is entrySP-48, r6 holds the table pointer and r11 the selected slot byte offset. Each fixture stipulates an ordinary return with r0=0 while the needed saved frame and route registers remain as recorded. The actual `g_str_equal` continuation at ELF 0x4750c executes CLZ and the following shift, producing 1; that result takes the found path and loads T. The full trace follows each executed PC and records NZCV, registers, mapped reads/writes, calls, returns, and next PC. Source-level preservation observed on this path is conditional on the explicit frame mapping and ordinary-return premises; no ABI claim follows.

The four positive traces contain 1,096 aggregate source steps. The division source range is fully stepped for each name; the trace’s PC-step count includes conditionally skipped instructions. The read-only validator regenerates all four traces and checks every saved event and summary row.

## Finite controls

`empty_first_bucket` supplies zero as the current first bucket word and stipulates the lookup’s current r7 as zero. The source branch reaches its initial-empty return at GLib ELF 0x45e54 and returns zero without calling equality. This control does not establish behavior for other empty/probe layouts.

`unequal_to_probe_edge` uses the same fixture hash slot but stores a different final character in the key and stipulates opaque strcmp return r0=1. The source equality wrapper returns zero; lookup reaches the next-probe edge at ELF 0x45de0, where this finite control stops. It does not invent further table contents or force a termination result.

## Claim matrix

| Claim | Status | Evidence and boundary |
|---|---|---|
| Pinned instructions, literal arithmetic, branch/GOT addresses, and selected local bodies | VERIFIZIERT | Exact raw ELF bytes and PT_LOAD mappings in source ledger; bounded PCs only |
| Helper reads the table-pointer word at DalBias+0x141e4 | VERIFIZIERT | Encoded PC-relative arithmetic and load; fixture distinguishes preceding decoy cell |
| Selected string hashes and arithmetic slots 2 and 3 | VERIFIZIERT | Full signed-byte hash source and full selected divide source traced for the two exact names |
| Four conditional source routes return their stipulated T | VERIFIZIERT | Requires all stated memory, callback, GOT, frame, non-alias, and normal-return premises |
| Initial-empty and mismatch-to-probe-edge controls | VERIFIZIERT | Two finite source witnesses only; mismatch stops before the next probe executes |
| Actual table construction/population and callback reachability | OFFEN | Numeric synthetic mappings do not prove an allocator/constructor can produce them |
| Runtime provider identity and relocation winner | OFFEN | Local source candidate and relocation metadata do not prove loaded-process binding |
| General table/hash/probing semantics, ABI, error behavior, or physical effects | OFFEN | Outside this bounded source route and fixtures |

## Validation

`python3 validate.py` is read-only and passes after regenerating in-memory traces and comparing all evidence tables, including trace, effect, route, fixture, strcmp-boundary, and control summaries. It also independently checks raw source bytes, hashes, file mappings, exact body counts, relocation/address calculations, hashes of the two names, and route values. The trace writer `run_cases.py` is explicitly separate and writes only package outputs. No ELF execution, runtime test, VM, network, device, constructor analysis, or hardware test was run (NOT_RUN).
