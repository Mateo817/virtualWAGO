> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-169 root remediation report

## Result

Input identity is **VERIFIZIERT**: 5,181,396-byte ELF32 little-endian ARM
`codesys3`, SHA-256
`b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5`.
Exact Dynsym `CMAddComponent` is VMA `0x002FD0F0`, size 520.

REA was already tried first by WP-XE164-168 against the exact hash; its xref
request returned no usable callsite view in time. The identical long operation
was not repeated. Root independently repeated the local fallback: a raw
aligned A32-`BL` target scan over all four executable sections and GNU ARM
objdump yield the same exact seven sites.

| Call | word | exact window | window SHA-256 | Dynsym owner by exact extent |
|---|---|---|---|---|
| `0x00086BFC` | `0xEB09D93B` | `[0x00086BAC,0x00086C0C)` | `a2935149cd9a7b92874c0bea557f6300318143ff4afea0983030d767215b1e4a` | none |
| `0x002FE298` | `0xEBFFFB94` | `[0x002FE248,0x002FE2A8)` | `e293918ede96bae5f115a9c94aac54ca3b5b13b8dfbe70bf0fa8f706fca98ef9` | none |
| `0x002FE574` | `0xEBFFFADD` | `[0x002FE524,0x002FE584)` | `b3c7a3fee8312b7017188b7a3724d05808d2a60cf3cf8457fb2ca0a2739d44bc` | `cmaddcomponent [0x2FE514,0x2FE594)` |
| `0x002FE6D4` | `0xEBFFFA85` | `[0x002FE684,0x002FE6E4)` | `f7629e9e341c5bc6d5a62f7f046a6f9ecda68f0c61e137dbd552b60a415c9c63` | `cmaddcomponent2 [0x2FE594,0x2FE6F4)` |
| `0x002FEC08` | `0xEBFFF938` | `[0x002FEBB8,0x002FEC18)` | `5db559c2efe60a85be5e07f3821b7535af9fedc5aa52629b90eeaf665d5089d2` | none |
| `0x002FFDA0` | `0xEBFFF4D2` | `[0x002FFD50,0x002FFDB0)` | `7362eb711ac510a267eb7d7e8c22cb34a6c1d31500ef4273d519bef13718c2e0` | `CMLoadComponent3 [0x2FFC84,0x2FFE08)` |
| `0x00301F30` | `0xEBFFEC6E` | `[0x00301EE0,0x00301F40)` | `50e23306d5175ea7ea6a1d5a0b246a89c37ce1d29cddb73f6901c3c112a07b49` | `CMInit3 [0x301A50,0x3021E4)` |

Each window is 96 bytes/24 contiguous A32 instructions. The three `none`
rows are not assigned the nearest preceding objdump label because the site is
outside that Dynsym's declared extent.

## Bounded call state

| Call | r0 at call | r1 at call | immediate r0 use through call+0x0C |
|---|---|---|---|
| `0x00086BFC` | window-entry value, not defined in scope | window-entry value, not defined in scope | stored to `[r4+4]` at +0x0C; no prior test |
| `0x002FE298` | `fp-88` | `fp-100` | no visible use |
| `0x002FE574` | `fp-72` | raw word `[r4+12]` | compare with `-1`, store to `[r4+16]`, conditional branch using compare flags |
| `0x002FE6D4` | `fp-80` | raw word `[r4+12]` | compare with `-1`, store to `[r4+16]`, conditional branch using compare flags |
| `0x002FEC08` | `fp-96` | `fp-184` | unconditional branch; no visible r0 use |
| `0x002FFDA0` | `fp-88` | `fp-92` | compare with `-1`, copy to r6, conditional branch using compare flags |
| `0x00301F30` | current r8, origin before window and OFFEN | `fp-124` | no visible use |

These are register/address forms only. In particular, `0x2FE6C8` overwrites
the earlier r0 load with `fp-80`. At `0x86BFC`, the prior `fp-848` and
`fp-852` definitions are outside the allowed window and are not evidence.

## Rejected worker draft and limits

WP-XE164-168's first report is **FAIL** for scope/accuracy: it read
`0x86B94/0x86B98` before the assigned window, propagated the overwritten
r0 value at `0x2FE6D4`, and used nearest objdump labels as ownership outside
Dynsym extents. Its corrected report preserves these failures and corrected
bounded outputs, but this root report—not the rejected worker judgment—is the
canonical basis.

Direct A32 `BL` completeness in the four executable sections is
**VERIFIZIERT**. Indirect transfers, Thumb/BLX forms, runtime reachability,
argument meaning, callee effects, fields/structs, component lifecycle,
runtime and hardware remain **OFFEN** or **NOT_RUN**. No device, VM, network or
runtime action occurred.

Tool versions: GNU ARM objdump/readelf 2.44; Python 3.13.5. Review:
root lead-agent Self-Review; no independent review claimed.
