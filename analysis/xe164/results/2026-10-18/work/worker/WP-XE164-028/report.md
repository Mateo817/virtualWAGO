> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-028 — E0054A local static control flow and references

## Status

- **VERIFIZIERT (bounded observation):** With the assumed image base `E00000`, raw offsets `0x054A..0x0555` decode as four `mov` instructions followed by `ret`; the observed local path is linear and terminates at `E00554`.
- **VERIFIZIERT (direct caller instruction only):** Raw offset `0x064C` contains `calla+ cc_UC, 0x054a`, encoded as `ca 00 4a 05`. This directly targets raw offset `0x054A`, hence `E0054A` under the same base assumption.
- **OFFEN:** The meaning of immediate `0x00E0` is not established. It is recorded as a numeric immediate, not promoted to a pointer, SFR, ABI, or memory reference.
- **NOT_RUN / out of scope:** No callee traversal, caller-body analysis, runtime behavior, DPP/SFR interpretation, or hardware conclusion was attempted. These are not blockers for this bounded offline task.

## Identity and bounds

Composite: `PRIVATE_ANALYSIS_ROOT/derived/composites/XE164-composite-e00000.bin`, 17,110 bytes, SHA-256 `5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983`.

Replay context: `PRIVATE_ANALYSIS_ROOT/work/ghidra/composite-replay.md`, 2,169 bytes, SHA-256 `842e13e9739b9898c96f68e62be2e75c40bc8f6dd1bf477a674cc22746212af5`. Its stated Ghidra language is `C166:LE:16:default`; this worker used Rizin for the tightly bounded reads below. The address conversion from raw offset to `E` address is an explicit assumed base mapping, not a provider load-map observation.

Analysis window: raw `0x054A..0x0555` inclusive, displayed as `E0054A..E00555`; additionally only the single instruction at raw `0x064C` (`E0064C`). No caller body was read. The initial REA disassembly request mistakenly requested one extra instruction at `0x0556`; that output is excluded from all findings and tables. No further query crossed the requested target interval.

## Findings

Rizin decoded the bounded target bytes as:

| Address | Bytes | Instruction | Local flow |
| --- | --- | --- | --- |
| `E0054A` | `e0 0c` | `mov r12, #0x00` | fall through to `E0054C` |
| `E0054C` | `e6 fd e0 00` | `mov r13, #0x00e0` | fall through to `E00550` |
| `E00550` | `f0 cd` | `mov r12, r13` | fall through to `E00552` |
| `E00552` | `f0 4c` | `mov r4, r12` | fall through to `E00554` |
| `E00554` | `cb 00` | `ret` | return terminator; no successor asserted |

This supports a bounded linear CFG with four fallthrough edges and one observed return boundary. It does not establish any caller-side return continuation or function-body ownership beyond these bytes.

The sole inspected caller instruction is `E0064C: calla+ cc_UC, 0x054a` (`ca 00 4a 05`). Rizin labels `cc_UC`; the direct target operand is `0x054a`. The instruction was observed in isolation only. No subsequent caller instruction or callee body was followed.

Numeric operands in scope: immediate `0x00` at `E0054A`; immediate `0x00e0` at `E0054C`; direct call target `0x054a` at `E0064C`. The two immediates are literal operands only. The call target is an address operand under the stated raw-offset/base interpretation. No other address-like reference is asserted from this bounded window.

## Tool profile and evidence

REA `execute_rizin_command`, provider `rizin` (version not reported), invoked on the exact composite SHA-256. Commands set `asm.arch=c166`, `asm.bits=16`, `cfg.bigendian=false`, and `io.va=false`; disassembly was limited to `pd 5 @ 0x54a` and `pd 1 @ 0x64c`, with byte dumps `px 12 @ 0x54a` and `px 4 @ 0x64c`. REA preserved the full command arguments and pre/post artifact digest. Rizin reported no stderr on the bounded calls. Version and format support were not independently established.

Evidence IDs:

- Bounded target disassembly: `ev_b73ff5f99afd34b5b3e4bf9b1768c388ee35442a9cc336a80ba69bbb505264dd`
- Target bytes `0x054A..0x0555`: `ev_f1d9cec2b3912c018dc2ac1fc4980823ce1101bd09c715969d72168ad8f5791a`
- Caller instruction and bytes at `0x064C`: `ev_3735bad1c8cb616b26b028fc46fc9246f84e1e8608025cdd5056c9b3f6042804`

`evidence-bundle.json` is the accepted filtered, importable selection with the exact out-of-scope evidence record `ev_0aedde1d4229e9004ea40c5b5c1eb08ac101c0ef3a30af24ab0c0cd61a99ccae` omitted. It contains the three bounded evidence records cited above and was parsed with `rea inspect-evidence-bundle`. `rea-evidence-bundle-full-audit.json` is the separate complete canonical export from the unchanged REA session: four records, including the retained oversized preview at `0x0556`, preserved for audit and counter-evidence review. The preview remains excluded from findings, accepted selection, and TSVs.

## TSVs and validation

`instructions.tsv`, `cfg.tsv`, `calls.tsv`, and `numeric_references.tsv` are bound to raw bytes and address mapping by `validate.py`. Run `python3 validate.py` from this directory. Expected result: `PASS`. Hashes for all deliverables are in `SHA256SUMS`.
