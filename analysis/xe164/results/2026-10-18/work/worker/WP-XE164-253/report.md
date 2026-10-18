> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-253 — bounded formatting-wrapper and PLT boundary

**VERIFIZIERT within the assigned static ranges.** On the hash-pinned `codesys3` executable, the two exact wrapper bodies are 84 bytes (`CMUtlsnprintf`, `[0x304b64,0x304bb8)`) and 120 bytes (`CMUtlvsnprintf`, `[0x304a30,0x304aa8)`). Together the wrappers contain 204 bytes (51 A32 words), bound to the supplied Ghidra assembly records and exact source offsets/bytes in `scoped-instructions.tsv`. Adding the one 12-byte PLT entry (3 A32 words) gives 54 total scoped words. The PLT entry `[0x7b5dc,0x7b5e8)` is independently bound to its `.rel.plt` slot and dynamic symbol. No neighboring function body, imported implementation, or runtime behavior was inspected.

## Flow and local stores

`CMUtlsnprintf` saves incoming r2/r3 as two words below entry SP `S`, then saves old r11, entry r12 (`S`), LR, and PC. It sets `r11=S-12`; its `ldr r2,[r11,#4]` reloads the saved entry r2 from `[S-8]`. Its guard rejects if entry r2, r1, or r0 is zero; the reject arm sets r0 to 2 and returns through the common epilogue. On the accepted arm, it sets r3 to `S-28`, r12 to `S-4`, and stores `S-4` at `[S-28]`. The local `BL 0x304a30` therefore receives r0=entry r0, r1=entry r1, r2=entry r2, and r3=`S-28` (the address of that local word). The helper's first local load through that pointer produces r3=`S-4`. The wrapper returns the helper's r0 unchanged on the local call-return edge.

The wrapper's explicit stores are 8 bytes for `{r2,r3}`, 16 bytes for `{r11,r12,lr,pc}`, and one 4-byte local word. Its epilogue loads old r11 from `[S-24]`, SP from `[S-20]=S`, and PC from `[S-16]` (the saved LR). It does not reload the two argument-save words into r2/r3. These are encoded local stack effects, not an ABI claim.

`CMUtlvsnprintf` rejects if incoming r1 or r0 is zero, then rejects if r3 or r2 is zero. Those local error edges set r0 to 2 and skip the external call. On the accepted edge, it copies incoming r0 to r6 and r1 to r4. It sets r5 to 0 on this edge, loads r3 from the caller's local word (yielding `S-4` if the caller stack slot is intact), computes r6=`entry_r0+entry_r1`, and stores r3 in its own local word `[T-36]`, where `T` is helper entry SP.

Immediately before the one external `BL 0x7b5dc`, the local register equations are r0=entry r0, r1=entry r1, r2=entry r2, and r3=`S-4` through the wrapper's saved-r3 slot. This records forwarding positions only; it does not assign C types or semantics to those values.

After that call, the helper executes `strb r5,[r6,#-1]`. The exact instruction expression is `MEM8[r6_after_call-1] := low8(r5_after_call)`. Before the call, r5 is zero and r6 is `entry_r0+entry_r1`; the byte is zero at `entry_r0+entry_r1-1` only if the external target preserves r5/r6 and local stack/memory state. No ABI rule or imported implementation effect is presumed.

The helper's local result calculation compares r4 with the opaque returned r0 using signed ARM GT/LE conditions, ORs the selected predicate with `r0[31]`, then sets r0 to 0 if the OR result is zero and 15 otherwise. Thus the exact local predicate is: **r0 becomes 0 iff signed(r4_after_call) > signed(r0_after_call) and `r0_after_call[31]==0`; otherwise it becomes 15.** Equating r4 after the call with incoming r1 requires external preservation that this package does not establish. The return 15 is a local conditional formatter result; no selector/hook/provider meaning follows from this wrapper evidence.

The wrapper helper saves seven registers (28 bytes), stores one 4-byte local word, and has the conditional one-byte store described above. Its epilogue reloads r4/r5/r6/r11, SP, and PC from stack slots; this restores the saved values only if the external call returns with the stack slots intact. The import is called before the code uses r4/r5/r6 again, so local save instructions alone do not establish their values after the external call.

## Exact import identity and remaining obligations

The call target is the single assigned PLT entry at `0x7b5dc`. The `.plt` entry index is 256 (20-byte PLT header followed by 12-byte entries). `.rel.plt` record 256 is `R_ARM_JUMP_SLOT`, relocation target `0x003c140c`, symbol index 3112. That `.dynsym` entry is undefined `vsnprintf`, versioned `GLIBC_2.4` from `libc.so.6`. `import-binding.tsv` records the ELF-derived indices, offsets, and names; `scoped-instructions.tsv` records all three PLT words.

This identifies the imported target label and version requirement, not its implementation or effects. The exact remaining proof obligations are in `preservation-obligations.tsv`: imported return meaning, preservation of r4/r5/r6, stack integrity, memory/buffer effects, and the interpretation of local r0=15 all remain **OFFEN**. The code's saved-register masks establish only conditional local restores from stack memory; they do not discharge those external obligations.

## Evidence and validation

The retained `root-rea.json` contains the complete supplied Ghidra records for both scoped bodies. `rea-bindings.tsv` binds each assembly record's evidence ID, source SHA-256, Ghidra version/profile digest, and exact covered range. The ELF SHA-256 is `b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5` (5,181,396 bytes). The table-route motivation comes from the binding assignment; this package does not inspect or reanalyze another helper body.

`python3 validate.py` is a read-only reconstruction check over the exact ranges, all 54 total scoped words (51 wrapper words plus 3 PLT words), REA record identity/ranges, the PLT relocation-to-dynsym/version binding, pinned input hashes, and generated TSVs. It passed in self-review. `python3 validate.py --write` is the explicit generator mode. No target execution, network, VM, device, or imported-library implementation inspection occurred.
