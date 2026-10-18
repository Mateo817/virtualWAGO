> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-346 — exact string callback source and finite metadata hashes

Root **Self-Review**. **VERIFIZIERT** for19rawREA/sourcewords, local arithmetic/transfer relations and finite evaluation of28 retained ASCII names. **OFFEN**: callback/table construction, runtime binding, actual lookup, arbitrary memory validity and public API/ABI. **PASS** source/arithmetic checks; vendor/native/VM/network/runtime **NOT_RUN**.

Pinned GLib source3f927b8aae0e3e1b1296bde9009ba9fb9380f64ac26ebe8b7675638e3250cbc5,1199352B. g_str_hash ELF47518 is44B/11words; g_str_equal47504 is20B/5words. Retained metadata confirms these exact contiguous bodies before expansion. Their strcmpPLT Ghidra2c0c4 has12B/3words; together19words. ELF/file and Ghidra+10000 code domains are separate.

The hash leaf initializes numeric5381 (MOVW0x1505), reads a signed byte viaLDRSB, returns immediately forzero, otherwise computes h=U32(h+(h<<5)+signedbyte), advancesonebyte and repeats untilzero. It writesr0,r2,r3 and flags, without stack/call use. A source-derived recurrence evaluation for the28 static ASCII function names is retained in named-string-hash-values.tsv. This is finite arithmetic evaluation, not an instruction replay, lookup execution or a bound on unbounded/nonterminated inputs. The signed load matters for bytes>=128; the tested names are ASCII, and a separate0x80 control distinguishes signed from unsigned recurrence. Missing zero terminators, faults, concurrent writes or aliasing are not modeled.

The equality wrapper savesr4/LR and BLs strcmp-namedPLT, then CLZr0/LSR5 yields1 iff the returned current32-bitword is0, otherwise0. Its result follows from that opaque currentword; actual stringcomparison semantics are not inferred. Continuing through its pop requires the savedframe/stackto remainvalid after the opaque target. Source PLT arithmetic yieldsGOT ELF134044/Ghidra144044; the raw JUMP_SLOT namesstrcmp@GLIBC_2.4. Runtimewinner, calleeimplementation, input-memory effects and equalitycontract remainopen.

These callbacks correspond bystaticnames to libdal's versionlessGLOB_DAT symbols g_str_hash/g_str_equal, but the actual loaderbinding and sourceproducer instance are not closed here. The integer-key table and name-key table globalwords remain distinct. Future source composition may use the exact hash leaf with explicitcallback/GOT/memorypremises; no such lookup is asserted by this acquisition.
