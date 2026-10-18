> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-356 — lower SSC data and buffer source boundaries

Root **Self-Review**. **VERIFIZIERT** for178actualREA/rawsourcewords,8separateliteralwords and selected numeric relationships. Lowercalleeffects, completehandle/descriptorcontracts, runtimebinding/API/ABI/hardware **OFFEN**. **PASS** sourcechecks; native/VM/network/device/runtime **NOT_RUN**.

Exactbackendsource3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Metadatafirst: SSC_Get ELFe17c/240B60words+8Bpool; SSC_Put e370/200B50words+4Bpool; lengthqueryd5f8/180B45words+12Bpool; access_tx e8dc/64B16localwords+4Bpool and3farPLTwords at741c; access_rx e95c/16B4words+4Bpool. Actualaccess_tx Ghidrabody is noncontiguous [1741c,17428)+[1e8dc,1e91c),76B19words with29952Benclosing span. The spanisnotcodeextent; farPLT is separatefromprimarybody.

Get/Put compute E=U32(entryr1+entryr2), compareunsignedto0x2edf, andonHI returnnumeric3 beforehandle/data dereferences oranycall. The Get prologuemovesregisters/pushesframebeforethisgate; Put savestheentrysourcepointer onitsframe. They testthewrapped sum, not eachoperand separately. E=12000(0x2ee0) rejects; e.gentryr1=11999,r2=1 selects3. A wrapped sum suchasffffffff+1=0doesnotselectthisrejectiongate; nothingaboutlatermemory/loopvalidity follows. No generalrange-safety or applicationbugclaim is inferred.

On itsacceptedsourcepath Get callsMEM_get_read_buffer-namedPLT beforetestingcurrentlengthzero. Nonzero length walks indexed16Bdescriptorentries andcalls locald598(96Bmetadata) forselectedsubrecords,with globalreadbufferalternativescontrolledbybyteflags. Put skipscallsforzerolength,walks a differentdescriptorfamily andcalls locald4d0(200Bmetadata), skipping flaggedsubrecords. Their selectedepilogues encode0; unexpandedcalleeffects andlooptermination/currentGP/memory areopen. No memcpy/bittransfer semantics are inferred fromhelpernames.

Lengthquery uses currententryr0 in32-bit12*index toloadaglobalentry, passesittoSSC_parse_get_content_lengths-namedPLT, then conditionallycopies returnedpointer+0/+4/+8/+c words throughcurrentoutputpointers drawnfromregistersandentrySP. Twofurtheroutputpointers drawglobaldescriptorwordsandshiftleft3. The sixoutputs/returnvalue are sourcepositions only, notaprovenAPIstructorunits. Allopaquequery/currentGP/framepointervaliditypremisesremainexplicit.

access_rx loadsaglobalwordatbase+14 andtails throughMEM_snapshot_buffer-namedPLT. access_tx tests two loadedglobalwords forzero, otherwisecallsMEM_get_write_buffer, then memcpy-namedPLT withcurrentdestinationr0,currentr1=savedsource,currentr2=0x2ee0, reloads itsbufferobjectwordandtails throughfarMEM_*PLT741c. Exactcall/target namesandrawrelocationsareavailablefromRoot310; actualmemorycopy/buffersnapshot/swap effects are unexpanded. Earlierzero-returnlanes do not establishastatuscode because theyreturncurrentr0,withsourcereachingdefinitionsdistinctbylane.

The simpleE=12000rejection can becomposed next with theupperReadBytes/WriteBytes paths, whose source includes a0x2ee0lengthword anddiscardsselectedSSCreturnwords. Suchacomposition requiresreal source-steppedupper/lower/PLTpaths andexplicitinstance/GOT/global/framepremises; this acquisitionalone doesnotclaimthecomposedresult.
