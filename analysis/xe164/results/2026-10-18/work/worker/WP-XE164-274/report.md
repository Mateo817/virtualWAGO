> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-274 — three provider target candidates at table-relative positions

## Finding

**VERIFIZIERT (bounded source):** The exact provider ELF has three relocation-bearing words at `0x14184`, `0x14190`, and `0x14194`, whose relative offsets from the getter's returned ELF VA `0x14154` are `+0x30`, `+0x3c`, and `+0x40`. WP-273 records their `R_ARM_RELATIVE` addends as `0x2f98`, `0x2e5c`, and `0x2e04`. REA procedure metadata confirmed a unique, contiguous body at each corresponding Ghidra entry (`ELF VA + 0x10000`), with lengths 88, 164, and 88 bytes. Each body was within the 512-byte cap. The three bodies are separate and nonoverlapping.

The exact candidates are therefore `P+0x2f98`, `P+0x2e5c`, and `P+0x2e04` if the relative relocations are applied to a loaded provider with bias `P`. They are candidate code addresses from metadata and raw bytes; no API identity or runtime table use is claimed.

**VERIFIZIERT (local register and branch mechanics):** Each body calls local target addresses `0x2180`, `0x2194`, and `0x1ecc` in sequence, tests the current `r0` return after each, and reaches its later local branch only when all three returns are nonzero. If a tested return is zero, the body sets `r0=0xffffffff` and returns through its local epilogue. The bodies explicitly reset `r0` from the then-current `r4` before calls at `0x2194` and `0x1ecc`; they do not reload `r4` between opaque calls. Thus the second and third `r0` values equal the original entry `r0` only if the opaque calls leave `r4` unchanged. Their other register and memory effects remain unknown.

For the `+0x30` candidate (`0x2f98`), after those tests the body reads a word from `[current r0+0x2c]`. If that word is zero, it returns `1`. If nonzero, it restores its saved stack/register state and transfers control with `BX r3`; at that instruction `r0` remains the current nonzero return from the `0x1ecc` call and `r3` is the loaded branch target. No values for current `r1` or `r2` are claimed after the opaque calls.

For the `+0x40` candidate (`0x2e04`), the same three-call gate is followed by a read from `[current r0+0x30]`. A zero word returns `1`; a nonzero word is used as the `BX r3` target after local restore. The same post-call register qualifications apply.

The `+0x3c` candidate (`0x2e5c`) reads a transfer word from `[current r0+0x20]`; if it is zero, it returns `1`. Otherwise it reads a second word from `[current r0+8]` and applies an unsigned gate to the then-current `r5`, `r6`, and `r7`. Let `a=current r5`, `b=current r6`, `s=(a+b) mod 2^32`, `m=max_unsigned(a,b)`, and `n=word[current r0+8]`. The branch to the local `-1` return is taken when `m>s` or `n<s`; the transfer branch requires `m<=s` and `n>=s`. Before transfer, the body sets `r0=a`, `r1=b`, `r2=current r7`, `r3=word[current r0+0x20]`, restores its local save area, then executes `BX r3`. The entry prologue initially copies incoming `r2`, incoming `r3`, and the entry stack word `[entry SP]` into `r5`, `r6`, and `r7`, but three opaque calls intervene before these values are compared or forwarded. Their relation to those entry values is therefore **OFFEN**, unless independently established call effects show preservation. No ABI assumption is made.

These bodies contain no directly visible non-stack stores and no 8-byte pair loop or queue processing. That is a bounded observation of these three bodies only. The bodies' opaque callees may have memory effects, and the eventual `BX` targets are not inspected.

## Conditional position join

WP-273's cell/addend report is the direct source for the cell relationships. The accepted caller summaries WP-209/WP-224 and root WP-183 are used only as hash-bound context: they place the positions `+0x30/+0x3c/+0x40` in the original consumer-path discussion. This package does not reopen their caller bodies, and it does not prove that the runtime object at `P+0x14154` is the object published to or consumed by IoDrvKbus. The position join is conditional on the same provider instance, loader relocation, table/object identity, publication/copy path, and runtime selection all holding. It does not identify source-level field names, prototypes, an I/O API, or physical bus behavior.

| Relative table position | Provider data word | Relative target candidate | Body behavior at the local boundary |
|---:|---:|---:|---|
| `+0x30` | `0x14184` | `P+0x2f98` | Three nonzero call-return gates; then `[current r0+0x2c]` null check and conditional `BX r3` |
| `+0x3c` | `0x14190` | `P+0x2e5c` | Three nonzero call-return gates; then `[current r0+0x20]` null check and unsigned range gate using current `r5/r6/r7` and `[current r0+8]` |
| `+0x40` | `0x14194` | `P+0x2e04` | Three nonzero call-return gates; then `[current r0+0x30]` null check and conditional `BX r3` |

The exact relocations, their raw addends, and target `.text` metadata are already source-bound in WP-273. This report independently validates source bytes for all three complete local bodies and reconstructs each candidate/table offset. It makes no statement that those addresses execute.

## REA and source bounds

Source identity: `/work/worker/WP-XE164-202/input/libdal.so.1.0.1`, 18,076 bytes, SHA-256 `c163ac57805409921ce783f9c4f17f52891864be333c3df4945a128d253994f5`. REA 6.5.0 / Ghidra 12.1.4, profile digest `7e46711069eea041af1b9b99e34115c13332795e5cda76e584a722f529ec70de`, analyzed the already-open hash-matching ELF. Procedure-info IDs and complete function-analysis IDs are in `rea-evidence.tsv`; the full body ranges are in the evidence and repeated there. The first query for each address was `procedure_info`. Only after each reported one unique body of at most 512 bytes was `analyze_function` used. Ghidra addresses are ELF VA + `0x10000`, as also established by WP-202. `instructions.tsv` records the raw A32 words and bytes for all 85 body instructions.

The exact per-instruction local listing and CFG are in the retained full-function REA evidence IDs. No nested callee body was opened. Local helper destinations are recorded only as numeric addresses; nearby disassembler labels are not used as identities. WP-273, WP-183, WP-209, and WP-224 reports are pinned by SHA-256 in `source-pins.tsv` and treated as summaries only.

## Status and limits

Local source words, body bounds, direct branch conditions, reads, constant local return values, and register setup at the `BX` boundaries are **VERIFIZIERT**. The call target at each `BX`, opaque helper return behavior/effects, cross-ELF runtime binding, publication/copy identity, original consumer's runtime object, function/API semantics, and physical I/O are **OFFEN**. Runtime, VM, device, network, and native execution are **NOT_RUN**. This package is a self-review.
