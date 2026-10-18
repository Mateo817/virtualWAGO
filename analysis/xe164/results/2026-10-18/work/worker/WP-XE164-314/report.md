> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-314 — bounded lookup composition

## Result

**VERIFIZIERT (source-local):** Under the explicit numeric-memory, callback-address, GOT-target, frame, and non-alias premises in the two synthetic fixtures, the selected instructions compose from each wrapper through `g_hash_table_lookup`, `g_int_hash`, `g_int_equal`, the selected GLib arithmetic route, and the lookup return. Both fixtures start with the initializer-matching numeric words `table+0=8`, `table+4=7`, and `table+8=7`. The selected callback route produces query hash 7, a table hash modulus of 7, and a first bucket comparison hit; the GLib lookup returns stipulated target word `T`. The 0x2194 wrapper then reads byte `[T+0x170]` and returns 1; the 0x1ecc wrapper returns `T+0x110`.

This is a bounded instruction model over pinned bytes and two stipulated address mappings. It does not show that a constructor/allocator creates these arrays or callback slots, that runtime relocation resolves this binding, or that any loaded process reaches the synthetic state. The numeric initializer writes alone do not establish object identity or array population. Those questions remain **OFFEN**.

## Source and route

The code bytes are pinned to private FW31 `libdal.so.1.0.1` SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5` and private GLib `libglib-2.0.so.0.8200.2` SHA-256 `3f927b8aae0e3e1b1296bde9009ba9fb9380f64ac26ebe8b7675638e3250cbc5`. The complete contributing source-word and initialization tables are hash-pinned in `source-pins.tsv`. Fixture A uses DalBias `0x60000000`, GLibBias `0x61000000`; fixture B uses DalBias `0x68000000`, GLibBias `0x69000000`. Each has separate, explicitly mapped table, arrays, key, T, and stack ranges. No binary was executed.

`source-words.tsv` contains 249 exact words: the two 14-word libdal wrappers, 3 PLT words, 79 lookup words, 2 `g_int_hash` words, 6 `g_int_equal` words, 8 caller arithmetic words, and 123 nested arithmetic words. Each instruction PC is in this pinned ledger. The wrappers' PC-relative literal loads at ELF 0x2194/0x1ecc and ADD instructions at 0x219c/0x1ed4 compute DalBias+0x141e0. The stipulated table global points to the fixture table. The PLT words load the stipulated GOT cell DalBias+0x140ec; its fixture contents point to GLibBias+0x45d6c.

At lookup entry, r0 is the table pointer and r1 is the key pointer at entry SP-12. `g_int_hash` loads the key word 7. On this selected path, the retained arithmetic words receive 77 and 7; the recorded instructions compute the selected nested target at ELF 0xbabf8 (Ghidra 0xcabf8), return 11 to the selected caller. Its following multiply/subtract instructions produce r1=0 for these operands. This statement is specific to the recorded operands and branch route; it does not define general quotient semantics or an API-level index. The stipulated callback slots point to the exact source bodies at GLibBias+0x4756c and GLibBias+0x47554. The first bucket word is 7; the comparison callback returns nonzero for equal stored/query words, so the selected lookup path reaches its value load and returns T.

For both wrappers, the function prologue writes the query key at entry SP-12 and the recorded epilogue restores SP and r4-r11. These are source-path observations under the mapped writable stack and normal-return premises, not an ABI claim. The complete trace records register state and NZCV before/after each executed word, object-relative and runtime PCs, and next PC. Each primary trace contains 107 executed source words; four primary traces cover both wrappers under two distinct fixture biases.

## Finite controls

`route-conditions.tsv` records the conditional inputs and outputs at each composition boundary. In the positive route, the stipulated table numeric words match the retained initializer writes. Separate stipulated pointer words then map the callback slots, arrays, selected bucket, key and value. This is a deliberately complete synthetic mapping premise; the actual source does not establish that a real allocated object has these pointer relationships.


The controls are individual source-path witnesses, not a general correctness suite. With table+4 changed to 1, the selected nested arithmetic path takes its direct fast return; the wrapper returns 1 after 78 executed words. With `[T+0x170]=0`, wrapper 0x2194 returns the byte value 0. With table value word zero, each wrapper returns zero under its visible conditional path. With bucket[0]=6 and bucket[1]=0, the finite lookup route takes the probe lane and reaches its empty-slot zero return. These cases verify only their listed initial states and paths.

## Evidence boundary

| Claim | Status | Limit |
|---|---|---|
| Source words, literal arithmetic, branch targets, and selected local instructions | VERIFIZIERT | Exact pinned bytes and bounded PCs only |
| Initializer stores numeric words +0=8,+4=7,+8=7 | VERIFIZIERT | Does not prove construction or surrounding table identity |
| Two fixtures' lookup-to-T and wrapper returns | VERIFIZIERT | Conditional on every stipulated mapping, readable/writable range, callback word, and ordinary source return |
| Callback slots/arrays are populated this way by a reachable constructor | OFFEN | No construction/allocator proof in this package |
| Runtime loader chooses these exact provider bytes and addresses | OFFEN | No process binding evidence |
| General hash-table quotient/probing semantics or all input states | OFFEN | Only listed finite selected routes were traced |
| Runtime/API/ABI contract or physical behavior | OFFEN | Not in scope |

Tests: source-pin/word-ledger, mapping, finite control, and deterministic trace checks in `validate.py` report PASS (3,315 read-only checks). No vendor execution, runtime test, VM, network, device, or physical test was run (**NOT_RUN**).
