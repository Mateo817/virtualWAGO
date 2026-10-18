> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-295 — independent review of WP286

## Result

**VERIFIZIERT for the bounded synthetic instance; no material unsupported conclusion found in the reviewed WP286 report.** The current report incorporates the prereview corrections: three pointer-valued poststores at `+0x8c/+0x94/+0x98`, nine non-copy instructions across the two 3-word PLTs and 3-word getter, and the VLD1 alignment qualifier is 64 bits (8 bytes). `effects.tsv` is an ordered `(kind,address,length)` span ledger with no memory payload. WP286's default validator replays Fixture A and byte-compares both its trace and event ledger against the retained files.

This review does not establish that the modeled source mapping, GOT values, biases, BSS cells, or callback state occur in any installed runtime. The report correctly limits its result to one explicitly stipulated path and makes no API, structure, ABI, lifecycle, loader, or runtime claim.

## Independent checks

The review validator pins WP286's current report, stepper, trace, and effects plus the exact Dal/provider/libc inputs and accepted instruction witnesses. It does not call WP286's validator entry point. It checks that the 174 trace rows partition as 117 Dal instructions, six PLT instructions, three getter instructions, and 48 nested WP282 instructions. It rereads the selected PLT/getter words and getter literal, decodes the raw `0x4524` branch, and checks the two GOT traversals as separate address domains.

For Fixture A the observed control-flow chain is Dal `+0x45a4 -> +0x9d4`, getter PLT `+0x9dc -> provider +0x3464`, provider getter `+0x346c -> Dal +0x45a8`; then Dal `+0x45bc -> +0x9c8`, memcpy PLT `+0x9d0 -> libc +0x919c0`, nested `BX LR -> Dal +0x45c0`. The source getter loads literal `0x10ce4`; its PC-relative add yields provider `+0x14154`. For the WP282 return, its body PCs are translated by `libc_bias`, while its BX target is already an absolute Dal return address and is kept in the Dal domain. This is exactly the distinction needed at the DSO boundary.

The validator reparses the provider ELF and independently requires 34 contiguous `R_ARM_RELATIVE` words at `[0x14154,0x141dc)`. Across both pinned synthetic bias tuples, it builds the expected 136-byte object from `provider_bias + raw_addend`, then checks actual replayed memory. All six requested candidate cells match the separately enumerated addends. It also checks the 60-byte pre-call stage as fifteen consecutive word stores over `[D-0x3c,D)`, and compares those bytes with entry bytes after the prior entry mutations.

The Dal input-object writes in the selected trace are exactly `+0x00` (4 bytes), `+0x04..+0x14` (16 bytes), `+0x14..+0x18` (4 bytes), and `+0x18..+0x1c` (4 bytes). The `+0x14` store follows the vector write and does not overlap its exclusive end. The later destination effects include the three pointer stores at `+0x8c/+0x94/+0x98`, zero at `+0x88`, stores at `+0x6c/+0x10/+0x14`, and the 16-byte vector store at `+0x78`. The review compares event spans and final bytes separately, so no earlier event is inferred from final-memory contents.

The trace supports the frame accounting: five GPR words (20 bytes), `d8/d9` (16 bytes), and 36 local bytes make a 72-byte Dal frame; WP282 adds a 4-byte local save. The final Dal LDM restores SP and transfers the saved LR to PC. The chosen 8-byte-aligned input SP remains aligned after 72 bytes. These are observed effects in the modeled fixture, not ABI assertions.

## Limits and residuals

WP286 stipulates the direct GOT targets and seven global pointer cell values, uses page-aligned nonoverlapping mappings, chooses `entry+0x28 = NULL`, and supplies writable destination/stack ranges. Its strict `D mod 16 = 0`, `S mod 16 = 4` statements describe these chosen biases and offsets; they are not promoted here to a general callee precondition. The raw WP282 lane is separately bounded by its own pinned contract. Neither the synthetic result nor the negative controls establish which provider is loaded or whether real process mappings satisfy the fixture.

The review's replay reuses the pinned bounded source-word machine and its fixture constructor as an input generator. The independent checks are the explicit PC/address route, raw word decoding, ELF relocation reconstruction, two-bias arithmetic oracle, and separate span/memory assertions. No native ELF execution, VM, device, network, or additional body expansion was performed.
