> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-310 — installed libpackbus candidate

**VERIFIZIERT:** Exact FW31 image SHA256 `49aa85c3801cb9d445bf900462bc235fa0ee9b7bbaf6f282341f05d9c9d7051c`, partition2 offset25165824/length262144000, readonly inode1874 `/usr/lib/libpackbus.so.1.0.1`, 148792 bytes. Extracted SHA256 `3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6`. No mount or whole-filesystem extraction. The fixed WP145 inventories bind `/usr/lib/dal/libpackbus.so` -> `../libpackbus.so` -> `libpackbus.so.1.0.1`; `/usr/lib/libpackbus.so.1` is a second direct alias to the same regular file. Aliases are not independent byte candidates.

A fresh complete byte comparison with the prior WP004 FW30-extracted library is equal across all148792bytes. This establishes the identity of this one artifact. It does not establish equality of the FW30/FW31 images, actual device state, selected runtime provider or a general ABI.

The exact dynamic export `libpackbus_open` index421 has ELF VA0x10720 and declared size1844. Name-only REA lookup was ambiguous between a PLT/thunk entry and the implementation; selecting Ghidra0x20720 resolves the implementation. Complete REA function-body AddressSet is Ghidra[0x20720,0x20d00) plus[0x20dd8,0x20e54), **1628codebytes/407words**, enclosing span1844bytes. The 216-byte gap[0x20d00,0x20dd8) is separately classified as nearby pool/source data for WP311, not407 additional code words. ELF VA=GhidraVA-0x10000 for these ranges. Both body/procedure metadata and full analyzed function are retained.

**OFFEN:** Actual loader path/runtime binding, constructor/object identity, backend initialization success, API/ABI semantics and hardware behavior. The source body contains hardware/OS-related named calls; none is executed or expanded in this acquisition. WP311 is restricted to the body/pool and callback stores with opaque call effects.

**PASS:** full image/inventory/source hashes, exact path/inode/size, aliases, complete byte comparison, Dynsym symbol metadata and actual REA source/body identities. **NOT_RUN:** vendor ELF, device, runtime, VM or network execution. Root Self-Review; no independent review claimed.
