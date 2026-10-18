> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-330 — private vararg/marshaling source acquisition

Root **Self-Review**. **VERIFIZIERT** for exact retained REA scope, 168 A32 source words and the numeric source relationships below. **HYPOTHESE** for any source instance using these getter positions. **OFFEN**: runtime construction, resolved symbols, actual type-object identity, caller representation, API/prototype/ABI and opaque effects. **PASS**: source/relocation/dispatch/metadata checks; target/native/runtime/VM/network **NOT_RUN**.

Pinned provider libdal.so.1.0.1 SHA256 c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5. Code mapping ELF=file; Ghidra=ELF+0x10000. Data uses PT_LOAD mapping, with data ELF0x14154 at file0x4154. Getter offsets O+0x70/O+0x74 refer to ELF cells0x141c4/0x141c8, respectively. Each has one R_ARM_RELATIVE with raw addend0x29e4/0x2784; no actual runtime relocation is asserted.

The 11-word O+0x70 body saves entry r1/r2/r3, LR and eight local bytes. Before its BL to ELF0x2784, current SP=S-24, r0=entryr0, r1=entryr1 and r2=S-8, pointing to saved entryr2 followed by entryr3. The source later balances its24-byte frame and restores LR. Reading beyond those two saved words would require separate readable memory premises.

The common body ELF0x2784 has exactly152 words/608B. It captures entryr0/r1/r2 in r5/r6/r4 before opaque/helper calls. Global gate2180 precedes name lookup20b0, then2194 receives word[current lookup record+0x38]. Failed global/device gates encode0xffffffff; null name lookup encodes1. Any facts about GP/frame values after an unexpanded call remain conditional; no ABI preservation is inferred.

Helper20b0 has5words/20B and one separate literal at20c4, raw0x12120. PC+8 at20b8 gives20c0; sum gives141e0. It forwards entryr0 into r1, loads r0 from [ProviderBias+141e4] and tails through lookup PLT15f4. This is a distinct global word from integer-lookup helper2194's141e0 word. Hashtable/name/API semantics and resolved callback bodies remain unexpanded here.

Within the common body the source reads size from word[word[currentr5+0x14]+0], computes align8(max_unsigned(size,4)) with32-bit wrap, reserves stack bytes, and reads nargs at currentr5+0xc and argument-type pointer array at+0x10. Each type dispatch reads an unsigned halfword at typeobject+6. At Ghidra1282c and128bc the instruction is ADDLS pc,pc,tag,LSL2, with guard tag<=14. Each dispatch has15 inline A32 B stubs starting at12834 or128c4; these30words are executable code, not pointer tables.

Source case targets are numeric: argument tags1/9/10/14 reach12880 (word load/store),5/6 reach12918 (word load, byte store),7/8 reach12900 (word load, halfword store),11/12 reach12930 (align8,64-bit VFP load/store); 2 reaches12978 (64-bit load plus float conversion),3 reaches12958 (64-bit load/store),0 skips to12894,4/13/default set r7=0xffffffff then continue the loop. This is source behavior, not a claim of public C varargs encoding. In particular a nonzero r7 error does not itself skip the later ffi_call-named BL.

At128a0..128ac the current values passed to the ffi_call PLT are r0=currentr5+8, r1=[currentr5+4], r2=currentr8, with r3 inherited from the local argument-array setup/loop (or zero on the zero-nargs source path under its current-value premises). The PLT resolves by static JUMP_SLOT at1409c to ffi_call@LIBFFI_BASE_8.0; actual binding and effects remain OFFEN. After its normal return, the return-type dispatch loads typeobject at currentr5+14 and tag+6, then source-copies 1/2/4/8 bytes to currentr6 for supported cases; void0 returns without copy. Frame/GP/type/result memory validity after the call must be stipulated separately.

The retained evidence supports a bounded codec review and type-tag reconciliation with the exact installed libffi, rather than declaring the entire ABI closed. Future work should instantiate selected metadata rows with source-stepped integer/pointer cases and explicit opaque-return premises.
