> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-021 — E007D4 local CFG, calls, and numeric references

## Result

The supplied composite decodes at file offsets `0x07d4..0x0807` into a bounded local instruction sequence. With the stated image base `0xE00000`, these are analysis addresses `0xE007D4..0xE00807`. The last decoded instruction is `rets` at `0xE00806` (bytes through `0xE00807`); no instruction at or beyond `0xE00808` was inspected. The one allowed caller instruction is `calls 0xE007D4` at file offset `0x09e8` / analysis address `0xE009E8`.

Three direct calls originate within the seed: `0xE007DC -> 0xE0077A`, `0xE007EA -> 0xE00720`, and `0xE007F4 -> 0xE00926`. Their destinations are numeric direct-call references only; no callee body was traversed. Two conditional branches at `0xE007E6` and `0xE007F0` target `0xE007FC`; the branch at `0xE007FA` conditionally targets `0xE00800`; `0xE007FE` unconditionally targets `0xE00802`. Local fallthrough and branch edges are recorded in `edges.tsv`.

The bytes and local edge shape are verified through the terminal return, but this does not make every node unconditionally reachable from the seed. The prefix through the call at `0xE007DC` is reached from the supplied seed; its continuation at `0xE007E0` is `OFFEN` because the callee's return behavior is outside scope. Later branch sites, calls, and the terminal return are decoded, while their reachability from the seed remains conditional on earlier call returns. This report does not infer DPP/SFR meaning, ABI, calling convention, K-Bus semantics, or behavior.

## Evidence and method

- Input: `DERIVED-XE164-COMPOSITE-E00000`, 17,110 bytes; SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.
- Replay context: `composite-replay.md`, 2,169 bytes; SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`. It records the composite base `0xE00000` and language `C166:LE:16:default`.
- REA provider: Rizin, local CLI version `0.9.1` (`c3a90e9226d977f58f4e9c75f78fa6b07afe13c7`), Linux x86-64. The first REA command was rejected because CLI options were supplied as Rizin commands; it yielded no disassembly and was not used as evidence for instruction claims. The corrected, successful REA command was exactly:

  `e asm.arch=c166; e asm.bits=16; e cfg.bigendian=false; e asm.bytes=true; e io.va=false; pD 52 @ 0x7d4; pD 4 @ 0x9e8`

- Rizin ran with REA's user-settings/script-suppression profile (`-N -q`); `io.va=false` retained raw file-offset addressing. The decoded range and the caller instruction were cross-checked against the supplied composite bytes. No Ghidra session or runtime was used.
- Evidence identifiers: successful Rizin observation `ev_935d7f4a32f827cabc7aa9e518648f6d0ddb3fd4d4872553486e57ee7f107be1`; rejected-command observation `ev_c98dcce13018644ab5b2b1745b87dfbb0a87f4e11c798e744ca251ff58c2ee4` (method-history only).

## Status and remaining uncertainty

- Instructions, byte offsets, direct destinations, and numeric branch targets: `VERIFIZIERT` against the named composite bytes and successful Rizin decode.
- Local branch/fallthrough structure and the in-scope terminal `rets`: `VERIFIZIERT` as static decoder output. Call-return continuations: `OFFEN` because callees were not analyzed.
- Validator and artifact hash checks: `PASS` when run from this directory using `python3 validate.py` and `sha256sum -c SHA256SUMS`.
- Alternative explanation: without source-level ownership metadata, the decoded region could be a compiler-generated fragment or a function body with another entry path; direct branch targets and the observed return still describe the bytes from the specified seed. The analysis does not prove global reachability from every caller or that this is the sole function entry.
- Residual uncertainty: indirect entries, alternate instruction interpretations under a different ISA/profile, called-function return behavior, and any address-space semantics beyond literal/static numeric references are unexamined. Addresses shown as `0xE0xxxx` are obtained by adding the replay's stated base to raw offsets/targets; no ABI or memory mapping is inferred.

## Output integrity

`instructions.tsv`, `edges.tsv`, `calls.tsv`, `references.tsv`, and `validate.py` are bound by `SHA256SUMS`. The canonical REA Evidence bundle is `rea-evidence-bundle.json`; its SHA-256 is listed there. `SHA256SUMS` itself is the final manifest and is not self-hashed.
