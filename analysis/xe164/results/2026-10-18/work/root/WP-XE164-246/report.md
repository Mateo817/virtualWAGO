> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-246 — registered-hook helper tail transfer

## Result and revised hypothesis

VERIFIZIERT (bounded local bytes/flow): exact helper ELF-VA [0x2fec58,0x2fecc4) forwards incoming r1 to tail r0, incoming r2 to r1, and incoming r3 to r2. It loads its indirect target from [incoming r0+0x20], rejects null, explicitly restores its frame and tail-transfers with BX r3 at 0x2fecb8. This is not a BLX instruction. The earlier BLX-only global searches therefore did not cover this transfer form.

The original pointer-displacement-mismatch hypothesis is refuted locally: the helper itself really uses displacement +0x20. The important new distinction is the BX tail-transfer and the entry-r1 to tail-r0 shift. No structure, API type, lifecycle name or calling convention is assigned.

The local halfword read at incoming r0+0x2c accepts values 2/4/5 for the target lane. If forwarded r0 is 20, only halfword5 survives; for forwarded15, all three values survive. A null target rejects. Each visible rejected exit sets r0=1. validate.py binds every one of the 27 words and evaluates the exact local arithmetic/conditions for all 65,536 halfword values at forwarded 0/15/20 and zero/nonzero target: 393,216 cases. This is mathematical analysis of static instructions, not execution of the supplied ELF or a hardware test.

## Caller relation and limits

Exact CMCallHook body [0x2fecc4,0x2ff0a0), 988 bytes, has three direct calls to the helper: 0x2fedd4, 0x2fee7c and 0x2fefd0. Their immediate callfree setup windows pass current r6/r6/r5 as r0, current r7 as r1, current [fp-0x38] as r2, and current r9 as r3. No preservation across earlier opaque calls follows from these windows.

HYPOTHESE: candidate-caller-path.tsv gives an address-exact callfree lane from CMCallHook entry to 0x2fee7c, skipping its optional earlier BLX. Its predicates include incoming r0=15, incoming r2=0, incoming r3!=0, the global gate word not -1, optional target at fixed global+0xa8 being zero, nonnull list head with current next word zero, and readable object/target words with the helper gate passing. The current r7 is set from incoming r0 and has no opaque call on this selected lane before it reaches helper r1. The path validator checks each branch/fallthrough edge and absence of earlier calls; root reviewed the stated local branch predicates. Memory/list/object validity and alias relations, actual invocation with15 and identity of the registered callback remain OFFEN. This is not an observed call or a complete runtime-object binding.

The helper's 108-byte body and caller's complete 988-byte body are confirmed by two complete REA Ghidra12.1.4 instruction records, matching source SHA-256 b56c6296faabae9eb73f0463fd068c535c03109ced347f0c2a643b69a7ee1ab5 (5,181,396 bytes). GNU ARM objdump2.44 independently reproduces both exact word windows. Root Self-Review only; no independent reviewer claimed. The initial exploratory GNU-only caller read was not accepted evidence; the formal package repeats exact windows after REA admission.

The next narrow questions are exact callers/reaching selectors of CMCallHook and direct tail transfers through +0x20, rather than another BLX-only whole-text negative search. Runtime, hardware, VM and target network NOT_RUN.
