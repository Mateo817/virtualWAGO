> Bereinigte historische Ergebniskopie. Maßgeblich für Korrekturen und Geltungsgrenzen ist der zentrale Evidence-Index; Originalhash siehe export-manifest.json.

# WP-XE164-362 — numeric buffer-index source and finite local transforms

Root **Self-Review**. **VERIFIZIERT** for109retainedREA/rawsourcewords, sourceindex/load/store relationships and36finite localtransform evaluations. Runtimeconstruction/binding, memoryallocationcontents, synchronization/API/ABI **OFFEN**. **PASS** source/finitearithmetic checks; native/VM/device/network/runtime **NOT_RUN**.

ExactFW31 libpackbus3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6. Metadatafirst actualbodies: create12608/244B61words,snapshot12790/76B19words,flip127dc/64B16words,get_read1281c/20B5words,get_write12830/20B5words,size12844/12B3words. Create's declaredsymbol256B includes separate bytesafterthe244Bbody: one nonbodyNOPword126fc, then twoVFP-literalwords12700=0/12704=1. Retained12Bread distinguishesNOPfromdata; no broaderbody invented.

Create'sselectedsuccesssource passes(0x38,1)toopaqueallocationPLT, gatesitsreturnnonnull, callslock-creation-namedPLT andrequiresreturn0, then writesword2atcurrentobject+20 and64-bitliteral(0,1)at+18/+1c. It calls threeopaqueallocations usingrequestedsizeentryr0/currentr5 and1, storesreturnwordsat+2c/+30/+34 andsizeat+28, andchecksall3nonnull. Failurecleanuptargeteffects/currentGP/framepremisesareopen. No explicitsourceinitializationofbyte+24 appears inthisbody; zero-fill cannot beinferredfromthecallocname.

Get_read returns0fornullentryr0; otherwise readsindexI18=[P+18] andreturnsword[P+2c+4*I18]. Get_write usesI1c=[P+1c] analogously. Size returnswordP28 or0fornull. Theleafbodieshavenoindexboundcheck: this acquisitiondoesnotproveI18/I1cwithin0..2 forarbitraryobjects orsafeaddressarithmetic.

Snapshot'snonnullpathcallsopaqueacquire,thenifcurrentbyteB24nonzero loadsI20/I18,setsB24=0andswapsthosewords. It callsopaqueunlockthenencodes0afteranormalreturn/framepremise; nullPreturns1. Flip'snonnullpathcallsopaqueacquire,loads64bitsatP1c,usesVREV64.32toswapI1c/I20,storesbackandsetsbyteB24=1,thencallsopaqueunlockandencodes0. NullPreturns1. GP/currentobject/frame/index/pending memoryvalidityafteracquireandbefore/afterunlock is conditional; atomicity/lockbehavior isnotinferredfromnames.

A finite source-transform matrix covers all6permutationsof(0,1,2) andB24in{0,1,128}, twooperations=36rows. It evaluatespost-acquire/pre-unlock numericstate:
flip:(I18,I1c,I20,B24)→(I18,I20,I1c,1);
snapshotnonzero:(I20,I1c,I18,0),zero:identity.
These localoperationspreservethepermutationundertheexplicitstate/memorypremises. This is finitearithmetic evaluation, notaninstructionstepper orconcurrencymodel. No constructedentrypendingbyteoropaqueeffectsareassumed.

StaticrelocationsinRoot310connectSSCbufferoperations356toMEM_get_read_buffer/get_write_buffer/snapshot_buffer/flip_buffer names. ActualruntimeGOTselection and commonobjectidentityremainopen. Lowerhardwareorphysicalsignalmeaningisnotprovidedbythese sourceindexoperations.
