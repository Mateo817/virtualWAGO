> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-344 — conditional table-to-marshaler type and width join

Root **Self-Review**. **VERIFIZIERT**: metadata and machine-source compatibility of the pinned symbols/objects and numeric dispatch targets. **HYPOTHESE**: applying the join to an actual record requires runtime symbol binding, successful record construction and readable memory. API/ABI/prototypes, actual invocation and hardware **OFFEN/NOT_RUN**.

This joins frozen WP334's complete raw-field/type inventories, independently corrected by WP339, to exact candidate libffi type bytes in Root331 and exact libdal common-body source in Root330/independent341. The zero sentinel is excluded: 28 named records reference 110 arguments and28 returns. No public files or vendor code are executed.

Under the explicit premise that every external type reference resolves to the matching pinned libffi object, argument tags are5(uint8,50cells),7(uint16,15),9(uint32,3),14(pointer,42). All110 enter supported handlers. The metadata references no argument tag0,4,13 or >14, so the unsupported/uninitialized-slot paths found by341 are not selected under that premise. This is a source/metadata condition; it does not establish the actual runtime type pointers or exclude corrupted/other tables.

All four selected handlers load one current32-bit word from the source cursor and advance it4 bytes. They reserve8 stackbytes per staged value, then store the low1,low2 or all4 bytes through that slot and store the slot address into the current pointer-vector element. Numeric tag14 receives a word-copy handler. This does not establish external C pointer validity, varargs promotions or semantics. The unused bytes in each8-byte value slot remain unspecified by these handlers.

All28 return references are candidate tag9(two uint32) or10(26sint32), size4, and source-return dispatch reaches ELF299c: one32-bit load from currentr8, one32-bit store through currentr6. No sign or application meaning is inferred. A stipulated normal ffi_call return must supply readable result bytes and preserve the exact live registers/frame/type pointers needed by this source suffix.

The common body reserves32entry-frame bytes,8return-scratch bytes, align8(4*nargs) pointer-vector bytes and8*nargs staging bytes on the selected paths, giving40+align8(4*nargs)+8*nargs bytes below its entrySP immediately before the call. The pinned n range0..7 yields a maximum128 bytes. These figures exclude the optional outer wrapper's24-byte frame and any callees' additional stack. They require normal finite selected source execution and safe valid stack space; they are not an ABI stack bound. For zero arguments the pointer vector is not allocated, and r3=0 at the call.

The optional O70wrapper explicitly provides only two saved input words (entryr2/r3) before the original entrySP. Metadata rows with more than two input words require further readable-memory premises; no caller convention is inferred from that fact. O74's direct cursor likewise needs enough readable words.

The28-row and110-row machine-readable joins retain exact names, type-symbol references, tags, widths, source handler targets, raw external relocation cell addresses and stack arithmetic. Their validator rereads pinned data and the actual selected load/store words. It is a static compatibility check, not a native test or complete full-loop replay. Selected source replay WP340 is separate evidence and not assumed in this package.
