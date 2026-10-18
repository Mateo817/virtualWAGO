> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-363 — call-free byte/bit helpers and content-length address leaf

Root **Self-Review**. **VERIFIZIERT** for81exactREA/sourcewords, one separateliteral and selected numeric control/memory ordering. Generalmemory/alias/descriptorcontracts, runtimebinding/API/ABI/hardware **OFFEN**. **PASS** sourcechecks; native/VM/network/device/runtime **NOT_RUN**.

Same pinned FW31 libpackbus3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Actualmetadata-first read-helperELFd598/96B24words,write-helperd4d0/200B50words,content-lengthPLT81cc/12B3words,getterbec4/16B4words plusliteralbed4. AllselectedcodeVA=file andGhidra=ELF+10000. Bothdatahelpers arecallfree. Their names here are local researchlabels,notexports/prototypes.

Read-helper receives currentbaseB=r0,recordM=r1,outputZ=r2. Itreadsword[M] as numericselector. Selectors2/5 copyonebyte[B+word(M+4)] toZ. Selector1 readsZ,clearsbitsselectedbybyteM9 andstoresZ, THEN readsbyte[B+word(M4)],testsbyteM8 andconditionallyORsbyteM9intotheclearedZ. Otherselectors returnwithoutselectedoutputstore. No returnedstatus interpretation isassigned. A disjointmemoryformula maycollapse this to bit transfer; ifZaliases thebufferbyte,the sourcebyte isreadAFTERtheclear,soan entry-memoryformula would bewrong. Descriptor/maskaliasingrequiresyetmorecurrent-memoryqualification.

Write-helper usesan executable5-caseBstubtable afterunsigned(selector-1)<=4. Selector1 clearsbyteM8 bitsinbuffer[B+wordM4],storesit,THEN readsbyteZ andtestsbyteM9 beforeconditionallyORingbyteM8intothebufferbyte. Againbuffer/sourcealiasingchangesthesourceobservedafterclear. Selector2 copiesbyteZdirectly;selector5writesbyteZ AND byteM8,overwritingotherbitsatdestination. Selector3/outofrangeselectorsreturnwithoutthesestores.

Selector4 interpretsword[M+4]ascurrentdescriptorD,loadsunsignedhalfNfromD+2,pointerAfromD+4,thenreads16-bitentryA+2*N-2 andbyteB+entryBEFOREtesting N-2 negative. ForpositiveN, sourcefoldsXORoverthereferencedbytesandstoresonebyteatthe16-bitdestinationoffsetD+8. N=0stillattemptstheA-2read beforeBMI; thereisnolocalzero-countguard. These are exact source accesses,not avalidateddescriptorlayoutorAPI. Alladdresses/counts/currentmemorymustbereadable/writable underselectedpremises.

The lengthgetter bec4 loadsconstant0x3426cfrombed4 andaddsarchitecturalPCbed0,yieldingimage-relativebase4013c; it returnsbase+U32(entryr0<<4) without dereferencingthatresult orcheckingindexbounds. The precedingPLT81cc referencesitsdefinedsymbolSSC_parse_get_content_lengths bystaticJUMP_SLOT. Runtimewinner/indexmeaning andtheglobalrecordcontentsareopen. Togetherwith356,thisidentifiesa sourceaddressproviderforfourqueriedlengthwords; itdoesnotestablishtheirvaluesorunits.

Further selectedsource models shouldcoverdisjoint andexplicitlyaliasedbitcases,selectors2/5,positivecountXORandzero-countpre-read, usingactualsourcePC/flags/memoryevents. Sourcewordchecks and arithmetic alonearenotfullinstructionreplay.
