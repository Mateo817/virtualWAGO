# Open questions

1. Which exact XE164 derivative and matching SFR map apply to these bytes?
2. Where does the ARM-side `libpackbus` loader place each stage at runtime,
   and which configured serial steps are actually reached? Static L1/L2/L3
   raw/length/XOR/Ack stages are known, but destination placement, receiver
   behavior and execution transition remain open.
3. What semantic roles do the 128 decoded jump rows have? Their bounded form is
   known (121 self-targets, seven distinct non-self targets, no duplicate
   targets), and all six non-row-0 targets now have bounded `RETI`-terminated
   structural descriptions, but vector/unused/error-trap meaning remains open.
4. Does an exact XE164 source confirm the assumed DPP-page mapping that binds
   logical startup pointers `0x33A8`/`0x0B84` to the retained composite bytes?
5. What roles and call contracts apply to the five direct callees of the now
   bounded `E00F18..E00F37` startup-called sequence? All five callees now have
   bounded structural descriptions and exact callsites (`E00F18`, `E00F24`,
   `E00F28`, `E00F2C`, `E00F32`); shared callees `E0043C`, `E0045C` and
   `E03878` are also structurally bounded in E-XE164-024..026. Their numeric
   call/data graphs still have no qualified ABI, SFR or K-Bus semantics, and
   the inspected incoming callsite lists are not global Xref inventories.
6. Which functions implement cyclic K-Bus exchange, enumeration, module data,
   diagnostics and error recovery?
7. Which byte ranges are code, constant tables, initialization data or unused?
8. VERIFIZIERT for the three concrete FW31-image XE164 files: E-XE164-337/338
   bind fresh readonly inode dumps 782/783/784 to the retained image and confirm
   full-byte equality to the pinned FW30 counterparts. The derived composite is
   likewise byte-equal. This closes that file-version comparison only; runtime
   loading, E00000 placement, derivative/SFR identity and reference-device state
   remain OFFEN. No device was contacted.
9. Why does the observed secondary startup stream terminate in an unmatched
   zero word that reaches `E00F18` and the idle loop, and is that byte stream the
   runtime backing store under the exact derivative's mapping?
10. Is the statically matched ARM-row-7/8/9 and C166-L2 handshake actually
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
11. What bounds the runtime `r9` value for the six-word indirect dispatch in
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
12. What selects the adjacent `E0043C`/`E0045C` variants, and what do their
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
13. Is the exact adjacency of the `E00B42` return at `0x0B83` and the observed
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
14. Do the adjacent straight-line callees `E00ACC` and `E00B42` implement
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
15. What contracts apply to the five outgoing callees of the bounded
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
16. Do the three callees invoked from the `E007D4` decode return to their
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
17. Which runtime conditions select the three return terminals in the bounded
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
18. What owns or enters the bytes between the accepted `E006C4` CFG end at
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
19. Which runtime predicates select the two return terminals in the bounded
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
20. Does callee `E00926` return to `E008E4`, and under what state/ABI contract?
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
21. Are adjacent callees `E00720` and `E0077A` related variants, and do their
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
22. What calling convention relates the five `CALLA+` sites in E-XE164-019 to
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
23. Do the ten callees in the contiguous E03634 decode return to their listed
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
24. Do `E033B8`, `E03ABA` and now caller-linked `E033F0` actually return along
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
25. What enters or owns the separately decoded E0355C..E03585 component?
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
26. Which exact startup, rollback, close and restart order does the selected
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
27. Which device-specific calls beyond the bounded digital terminal-info,
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
28. Which `libwago_dbus`, `libdiagnostic`, board-metadata/signature and other
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
29. How should active output permit, lease loss, native STOP/restart and
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
30. Do analog, PWM, serial, retain/time or concurrent/multi-instance paths
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
31. Is `virtual_adi_reset()` intended to be callable in a bridge-enabled
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
32. Must `virtual_model_bridge_stop()` revoke a stored permit even when no
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
33. Can the original consumer ever deliver a delayed same-thread/same-task
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
34. Does the selected original consumer rely on Push after an earlier
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
35. Which selected original-manager function orders Init, Scan, enumeration,
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
36. Which exact provider/DAL functions occupy the unresolved start, finish,
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
37. What external callback-field contract names the fourth function value
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
38. What external field contract names the function value `0x2614` published
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
39. What external field contract names the function value `0x2eb8` published
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
40. What external field contract names the function value `0x24e4` published
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
41. What external field contract names the code value `0x33b0` published at
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
42. What external field contract names the function value `0x2120` published
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
43. Which initialization path supplies the runtime contents of the FW31
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
44. Which generic loader/manager code consumes the object populated by
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
45. Which of the bounded `get_uid` and `read_conf_reg` call paths are reachable
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]
46. Which original manager calls the generic IoDrvDal loader for index 0 and
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

Priority note: questions 26–46 are the current implementation-critical
consumer-boundary gaps. Questions 1–25 remain valid firmware-reconstruction
questions but are not automatically on the bounded digital critical path
(E-XE164-069/070/080). The 15-row WP-XE164-070 matrix assigns each bounded gap
to local source/document work, exact caller tracing, later runtime evidence or
a separate module scope; no current row requires broad XE164 work.

47. Does the provider-seam hypothesis cover more than the already demonstrated
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

48. Which minimum-contract rows still lack direct own-provider assertions?
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

49. Which minimum-contract mechanics are absent from the visible own provider
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

50. Which bounded own-provider checks are continuously exercised by current
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

51. Which remaining facts block a minimal implementation-ready provider
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

52. Who publishes the pointer read by WriteOutputs at context `+0x61c`, and
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

53. Do either of the two direct static callers of procedure `0x277c` establish
[Eingerückter Code-/Listingblock bleibt im privaten Nachweispaket.]

54. Selector-15 dispatch continuation (E-XE164-266): 34 of the 101 local table mappings are now accepted with all 593 case words, but complete downstream selector/value reachability is still OFFEN. WP241/242 are active on the original disjoint scopes. A missing simple MOV r0=15 is not absence of computed, other-form, incoming or memory-derived value 15. Provider +4 remains an optional prioritized candidate, without verified Exit naming/requirement.

- E-XE164-267 continuation to question 54: 23 additional raw-table mappings / 305 words accepted. Four absent REA bodies do not block raw-table validation or independent offline work. Full CFG, static arithmetic/other-form r0, incoming/memory values, aliases and opaque-call effects remain OFFEN. The combined selector-15 callback-path question remains OFFEN.

- E-XE164-268 continuation to question 54: 44 additional raw-table mappings / 643 words accepted. The three-site audit and same-segment screen are method-bounded; 42 downstream table/value paths are not closed. Even the two additional lane reviews do not close runtime or interprocedural paths; computed/incoming/memory r0 remains OFFEN. The combined selector-15 callback-path question remains OFFEN.

- Final 2026-10-18 status for question 54: E-XE164-266..268 bind all 101 local guarded table mappings / 1,541 case words, so the old unresolved-table-base/target count is superseded. The remaining question is downstream CFG and selector/value reaching definitions. WP241 has four local Ghidra procedure gaps; WP242 keeps 42 downstream cases open beyond its syntax-limited screen and two additional direct lane checks. All three packages are completed for their declared methods; no worker is active.

55. E-XE164-269 adds the exact CMCallHook helper BX-tail path, which BLX-only scans missed. Which direct CMCallHook callers (or CMCallHook2 route) supply selector15 or compute it? First inventory exact B/BL targets and bounded visible input definitions; preserve unknown/opaque values. Join only to the helper's locally verified forwarding, keeping runtime/object identity and the candidate callfree memory predicates open. Do not prioritize generic unrelated offset32 calls over this concrete manager route.

- E-XE164-270: 602 explicit method/control/effect gaps; predicate feasibility and memory aliases unresolved. Marker word starts are not code/function ownership. No proven15 in this limited model does not exclude15. Exact CMCallHook/helper provenance in question55 is now the priority; unrelated offset32 load sites do not establish a registered-block identity.

- E-XE164-271: 138 explicit gaps including15 unowned islands,116 widening states,4 unmapped direct branches,3 unresolved BX destinations,2 unsupported vector writes. Zero modeled witnesses under these limits is not a global absence or inequality15. Exact CMCallHook/helper provenance in question55 is now the priority; unrelated offset32 load sites do not establish a registered-block identity.

- E-XE164-272: Unproved code ownership, spill/reload/memory aliases, unsupported PC paths and unmodeled effects remain open. Node/constant categories describe a bounded model, not runtime or whole-program absence. Continue the exact table-derived CMCallHook routes (WP251) and saved service pointer routes (WP249), rather than treating generic offset32 or literal15 hits as a framework-call contract.

- E-XE164-273: Five true unknown selectors come from table/memory, entry and opaque values; no locally proven15 does not exclude15. Raw census omits Thumb/indirect routes and runtime. Extra Xref is untyped within WP247; accepted E160 independently binds publication of the same target at local+0x24. Continue the exact table-derived CMCallHook routes (WP251) and saved service pointer routes (WP249), rather than treating generic offset32 or literal15 hits as a framework-call contract.

- E-XE164-274: This checks static evidence consistency/conditional path compatibility only. J1 remains HYPOTHESE; actual memory/list/object validity, selector15 invocation, runtime/hardware remain OFFEN/NOT_RUN. Continue the exact table-derived CMCallHook routes (WP251) and saved service pointer routes (WP249), rather than treating generic offset32 or literal15 hits as a framework-call contract.

- E-XE164-275 VERIFIZIERT: Exact IoDrvDal ComponentEntry input+0x24 is loaded at ELF0x4508 and stored unchanged at0x450c to BSS0x163b8 (Ghidra0x263b8). The exact Ghidra direct-reference inventory contains only this WRITE; the adjacent BLX0x452c instead uses input+0x28 and locally supplies0x10062001. No direct hook consumer established; computed aliases/external/runtime consumption and actual published service identity remain OFFEN.

- E-XE164-276 VERIFIZIERT: Freshly rehashed40 installed ComponentEntry DSOs; Dal metadata-only and39 others interpreted. Their1572120 file-backed executable bytes in156 sections contain28 aligned A32 MOV-immediate15 writes to r0/r1 in5 DSOs and zero MOVW hits. All28 fixed windows decode at the word; this is syntax triage only. Thumb/computed/loaded values, code ownership/reachability, propagation, ABI/API and selector meaning remain OFFEN; no-hit does not establish semantic absence.

- E-XE164-277 VERIFIZIERT: Exact source table [0x3a30c0,0x3a31d0) contains34 stride8 numeric pairs, with firstword15 uniquely at index20/VA0x3a3160. Raw aligned A32 caller counts are2 to helper,3 to CMInitSequence,4 to CMExitSequence; REA Xrefs agree. Exact caller0x300f3c selects row16/count2 (12,13), excluding next14. Row20 membership does not prove15 delivery across opaque formatter/state effects. No ABI/runtime or mandatory provider+4 claim.

- E-XE164-278 VERIFIZIERT: Four exact bodies bind632 instruction words/2528bytes. The formerly window-unknown Hook site0x2ff368 receives20 on its sole local predecessor path;0x2ff6d4 likewise locally supplies20. Site0x2ff588 has20 only before an opaque call;0x2ff76c reloads unknown post-call memory. The exact subtract15/clear-bit1 gate accepts precisely15 or17. Post-opaque r8/r4/memory and CMExit table association remain conditional; direct-body predecessors do not exclude external interior entry. Runtime NOT_RUN.

- E-XE164-279 VERIFIZIERT: Exact84/120-byte formatting wrappers contain51 words, plus3 PLT words=54 total. Source relocation binds PLT0x7b5dc to undefined vsnprintf@GLIBC_2.4 from libc.so.6. Local stack/forwarding and post-import byte-store/result predicates are explicit, including conditional local result15. Import implementation/stack/register/buffer effects remain OFFEN. Formatter return15 is not a Hook selector. No ABI/runtime claim.

- E-XE164-280 VERIFIZIERT: Exact152/120-byte pool bodies bind68 words. Local GetBlock arithmetic forms payload P=N+16 and stores manager M at N+4; Append computes N=P-16 and reloads M at P-12=N+4. Its post-call head/tail slots are M+0x1c/+0x20. Numeric positions agree conditionally with registration copy and callback head+16. Same manager/node, memory lifetime, opaque lock/clear/unlock effects and actual registered callback remain HYPOTHESE/OFFEN. No invented schema/API semantics.

- E-XE164-281 HYPOTHESE: Conditional static entryvector CMCallHook(15,0,0,0) reaches helper call0x2fedd4 in68 callfree instruction addresses with args(firstHead+16,15,0,0), skipping optional BLX iff slot0x5fc5b0 is null. It never reads firstHead.next before this call. Under halfword2/4/5 and nonnull target, helper BX forwards(15,0,0). All global/slot/head/object/target/stack validity and noninterference predicates are assumptions. Table-to-entry delivery, runtime binding/order and mandatory provider+4 remain OFFEN/NOT_RUN.

- E-XE164-282 VERIFIZIERT: Exact71 sourcewords in CMGetHookName/CMGetHookEntries bind34-row table lookup and stop-exclusive ranges. Selector15 index20 secondword0x3a5830 points to exact terminated ASCII CH_EXIT_SYSTEM; selector17 maps CH_EXIT_SYSTEM2. Rangeexamples17..16->row19/count2,12..14->row16/count2,2..2->row2/count1,10..12->row13/count3. Binary-authored labels identify emitted names only; mandatory lifecycle/ABI/order/runtime binding remain OFFEN.

- E-XE164-283 VERIFIZIERT: Independent root raw-A32 subset mathematical replay reproduces all68 WP255 calleraddresses thenhelper through encoded stackrestore/BX, obtaining(15,0,0,target) at admittedhalfwords2/4/5. Threepositive andeightnegative syntheticcontrols pass, including invalidglobal/nullhead/nonnulloptionalslot/pathdivergence and nulltarget/invalidhalfword return1. No head-nextword read occurs. Syntheticmemoryfixtures are not observedlayout. Actualglobal/stack/head/target validity, aliasnoninterference, invocation andruntimebinding remain HYPOTHESE/OFFEN.

- E-XE164-284 VERIFIZIERT: Original Dal selector17 reaches default and selector15 returns from getter/+4 lane to same default; default sets r4=0. Common postlude returns0 without further calls when localglobalword+12 is nonzero, or when thatword and countword+16 are bothzero. Positivecount may invoke further indirectcallbacks and gives no unconditionalresult. Getter/target/object/runtimebinding and stackvalidity remainconditional; positivecount effects unresolved. Discarding +4 postcallr0 locally is not an unconditional routine result.

- E-XE164-285 HYPOTHESE: Corrected source-bound scan at301058 selects rows19(17)/20(15), excludesrow21(16), and passes(pointer3a3158,count2,0,0). Under explicit live-state/memory/return predicates, secondHook vector is(15,0,0,0). Completeeight-row argumenttable andthreeeffectivevectors now checked ratherthanpartial/tautologicalassertion. Timeimport and firstHook effects/live-state preservation, priorCMExit joins and actualtable/runtime/objectbinding remainassumptions. No globalexclusion fromselectedretrycontrol.

- E-XE164-286 VERIFIZIERT: At currentlocalframeF afterMainLoad, B=F-88 and callfreeinitSTRH2 writesB+44. HelperSTRH3 predicate is post-BLXr0!=r6, targetcurrentr4+44; entryBtargetrequirescurrentr4=B. Latecallerwordstores usecurrentr5; originalentryr3identityrequirespreservation. Any4bytestoreA overlapsB+44..45 iffA inB+41..45. Immediate2doesnotprove latergatevalue. Allopaqueeffects, frame/registeridentity acrosscalls, copy-source/payload/node/manageridentity, memory/stackvalidity andretention remainHYPOTHESE/OFFEN.

- E-XE164-287 VERIFIZIERT: Exact FW31 image interpreter path /lib/ld-linux-armhf.so.3 resolves through image /lib symlink to regular inode1396,175592B, SHA366d9f2f5584ce374cb1a7a2222067d0c99aabee4bac6a475c160ce04ed4dd33. Loader ELF32 ARM ET_DYN hardfloat metadata has42 declaredDynsym entries and no declared _dl_runtime_resolve/_dl_fixup names. Missingdeclarednames do not prove codeabsence. No resolver address/body/effects or runtime lookup/interposition verified; privatevendorfile notpublished.

- E-XE164-288 VERIFIZIERT: A closed synthetic selector17 instance traverses the exact core prefix/helper, the original Dal default path and core postlude, returning0 to2ff770 for halfwords2/4/5. Actualencoded push/pop restores callerliveGP/SP; ownDal argumentstores lie below savedregisters. Singlehead.next0 and Dalno-callbackglobalconditions are explicit. This proves a conditionalinstance of firstHookreturn, not actualmanagerlist/targetbinding, loadbias, memoryvalidity orruntime; nopreservation inferredfromABI.

- E-XE164-289 VERIFIZIERT: Exactinstalledlibcds3sys.so160364B SHA32e41d8e8132dfe4ebda603a6a273252e7dd04e83807aea0083d2045d13f8959 exportsoneSysTimeGetMs at e87c/72B. It passes1 andan8bytestackbuffer to clock_gettime@GLIBC_2.17; postcall current-framewords feed low32(1000*word0+signedreciprocal(word1)). Importstatusr0isnotchecked. Millisecond/clockdomain meaning needs actualoutputcontract; postcallframeidentity/stack/importeffects and actualproviderbinding remainOFFEN. No monotonicityfromID1alone.

- E-XE164-290 VERIFIZIERT: Provider+4 exact57wordbody eightdirectcalls bind sixPLTimportidentities: g_hash_table_destroy,LibraryLoader_Destroy,fileno,flock,fclose,free. Soleinternal3c34body76B clearsinputbyte+12 beforethreeopaque calls andtailB tofree. Four initialwordslots clearedbeforetheircallboundaries. Namesidentifyrequests, not runtimeimplementations/effects. r0afterfileno,currentr4/r6aftercalls andtailBreturneffects remainunbound. No foreigncallee expansion.

- E-XE164-291 VERIFIZIERT: Initialtimecallreturns toHooksetupdirectly via2ff750->2ff75c. OnlyafterHookr0=10 doeszero-baseline test2ff754 occur; baseline r6=0 canrepeatwithoutanother sample under explicitcall/statepreservation. Nonzero baseline unsigneddelta<=9999 retries,10000takesotheredge; separateBCS thresholdis>=32000;32bitwrapcasesPASS. Conditionalcycleisnotobservedruntimehang. Literal10 hasnoinventedstatusmeaning; clockunits/domain andopaquecallreturn/live/frameeffects remainOFFEN.

- E-XE164-292 HYPOTHESE: Reviewed originalstack selector15 chain: originalnameCH_EXIT_SYSTEM, conditionalCMExit17/15slice->Hook15->registeredcallbackBX->IoDrvDalgetter/+4->soleinstalledlibdalcandidate. Within that localDal15path, +4 is anunguardedcall-targetprecondition; universalmandatorylifecycle/ABI isnotproved. Combinedruntime/object/lookup/relocation/stateidentity, actualinvocation/order andcompleteABI remainHYPOTHESE/OFFEN; source labelsdonotproveuniversalsequence. Canonicalreviewedtext is work/root/continuation-2026-10-18-0858/selector15-synthesis-reviewed.md.

- E-XE164-293 VERIFIZIERT: The full476-byte ComponentEntry and84-byte pool bind the 136-byte call vector and all later stores. Its candidate destination is DalBias+1a270. The post-call vector begins at D+78 only when current r6 before ADD45c4 equals DalBias+1a2c4; scalar stores separately require current r5=DalBias+193c4. No local store is present at D+90 under that baseline. Copy effects, actual GOT target, relocation/load biases, memory/alias safety and runtime instance remain OFFEN. Source vector/address arithmetic does not infer semantics from memcpy name.

- E-XE164-294 VERIFIZIERT: Under a stipulated directly-resolved Dal GOT16030 pointing to the exact libdal getter, PLT/getter instructions return ProviderBias+14154 while preserving r5/r6/r7/d8/d9/SP by explicit operands. Caller45b8 updates r6 before the next call. Three source positions +30/+3c/+40 have unique R_ARM_RELATIVE addends2f98/2e5c/2e04 and file-backed executable target metadata. The exact route excludes lazy resolver and alternate GOT targets. It does not establish actual binding, table/API meaning or copy implementation; runtime NOT_RUN.

- E-XE164-295 HYPOTHESE: If the exact136-byte copy occurs from the relocated getter object to D=DalBias+1a270, and the separate current-r5/current-r6 premises hold, all10 subsequent local stores leave D+30..33,D+3c..3f,D+40..43 untouched. Conditional words are ProviderBias+2f98,+2e5c,+2e04. Changed-r6 vector and changed-r5 scalar counterexamples invalidate unconditional preservation. Copy implementation/preservation and memory conditions are explicit premises. Identity with IoDrvKbus context+61c, runtime publication and original API semantics remain OFFEN; no caller body reopened.

- E-XE164-296 VERIFIZIERT: Three complete provider candidate bodies at2f98/88B,2e5c/164B,2e04/88B have85 source-bound words. Each tests three helper results individually, returning ffffffff onzero. Simple candidates null-check slots at current third-return+2c/+30 before tailBX. Sized candidate null-checks +20, then requires unsignedmax(currentr5,currentr6)<=wrapped_sum and word[current_return+8]>=sum; currentr7 is forwarded to tailr2 only after that gate. Current values after opaque calls remain unknown. Relocation/copy/object/runtime identity and API meanings remain OFFEN.

- E-XE164-297 VERIFIZIERT: Exact helper2180 reads globalbyte ProviderBias+14208, ignores inputr0 and preserves r4-r7/SP/LR locally. Helpers2194/1ecc pass word[ProviderBias+141e0] and address of stack-saved key to PLT15f4. First returns byte[nonzero_nested_return+170]; second conditionally returns wrapped nested_return+110. Distinct nested results and r4/key retention are not equated. PLT symbol g_hash_table_lookup is metadata, not implementation/effect proof. Frames/readability/opaque preservation and complete success contract remain OFFEN.

- E-XE164-298 VERIFIZIERT: Exact FW31 installed libc.so.6 inode1548 was read-only extracted:1434296B SHAdc47ee066e2c2d73ff9186440787543c3020711611f09002b6ab187d97d9dfa2. Unique memcpy Dynsym2313 is GLOBAL/FUNC ELF919c0 size1248 versionGLIBC_2.4; exact contiguous Ghidra body and complete function evidence retained. Installed candidate metadata does not prove runtime winner or copy effects. Exact136-byte lane analysis is WP279; runtime NOT_RUN.

- E-XE164-299 VERIFIZIERT: Exact image installs one SONAME-family regular GLib candidate libglib-2.0.so.0.8200.2 inode1706,1199352B SHA3f927b8aae0e3e1b1296bde9009ba9fb9380f64ac26ebe8b7675638e3250cbc5, withtwo aliases. libdal needs libglib-2.0.so.0 and imports unversioned g_hash_table_lookup at GOT140ec; candidate exports exactname index944 ELF45d6c declared328B. Actual REA reports contiguous316B body plusunclassifiedsymboltail. Uniqueinstalled SONAMEfamily is not runtimewinner. Implementationbody is separatelyWP283; no functioneffect inferred from name.

- E-XE164-300 HYPOTHESE: For each of the threewrite-side candidates, readable globalbyte ProviderBias+14208=0 causes its first direct2180leaf toreturn0, thenlocalCMP/BEQ/MVN/POP returns ffffffff without2194/1ecc calls. Leafhasnostore/nestedcall and doesnotwriter4-r7/SP/LR. Byte1passesfirstgate andreaches nextdirectcall only. Readable sourcebyte mustnotaliassavedframewrites; valid8B/24Bframes/savedreturnandlargecandidateentrystackword required. Runtimebyte,providerbinding/objectidentity andlatercallbackeffects remainOFFEN.

- E-XE164-301 VERIFIZIERT: Corrected source-driven136-byte memcpy lane steps48 PCs over312boundwords: four32-byte source loads/four32-byte destination stores,8-byte tail and4-byte stack save/restore. Exactcarry branches and sixPLDhints include S+140. Immutable entry snapshots prove advertised GP/d8/d9 retention; injectedr5clobber control is rejected. Onlypagealigned assignedsource/destination offsets andnonwrapping,nonoverlapping,readable/writable,validstack/return,NEONsupported syntheticconditions. RuntimeGOT/provideridentity,concurrency/fault/cacheeffects remainOFFEN.

- E-XE164-302 VERIFIZIERT: Read-side getterpositions+44/+50/+54 bind three uniqueR_ARM_RELATIVE cells to2dac/88B,2c70/164B,2c18/88B. All85 sourcewords arechecked. Threehelperzero-gates returnffffffff; simplecallbackslots currentthirdreturn+24/+28 nullreturn1. Sizedcandidate firsttests callback+18 thenlength+4, with unsignedmax(currentr5,currentr6)<=wrapped_sum andlength>=sum; r7onlyforwardedafterpass. Helper/context/callbackeffects andactualruntimebinding/tablepublication remainOFFEN. Separatelist-entrycontext+58 isnotjoinedtogetterobject+58. Earlybyte0firstgatefollowsaccepted2180leafonlywithvalidframe/readability/nonalias conditions; noAPItypes/ABI inferred.

- E-XE164-303 VERIFIZIERT: Corrected GLib lookupbody79words/316B plus12Bliterals: initial-empty Ghidra55dc4 branchesdirect55e54 MOVr0=0 thenPOP, independentofcurrentr7/r8. Laterprobeempty55dfc->55e4c does testr7 andmayuse rememberedr8/status. Nulltablewarning andopaquehelper/callbackeffects remainqualified; saved40Bframe canrestoreGP/SP onlyif framebase/bytesretained. Runtimebinding/tablecontents andopaqueeffects remainOFFEN; nameg_hash_table_lookup notanAPI/ABIcontract. Original283frozenforaudit; address-table labelwarning_call_target forfirstarithmetictarget issemanticwordingonly, canonicalscopeusesnumericinternaltarget.

- E-XE164-304 VERIFIZIERT: Actual independent Luna review supports corrected28248-PCcopy136B source-model: raw312wordinventory,32/8BNEONpostindex,carrybranches,PC+8tail,source/destination/stackaccessorder,all6PLDhintsincludingS+140. Immutableentrysnapshots andmutationcontrolsforallclaimedpreservedGP/d8/d9 independentlychecked. Sameconditionalmappedranges/nonalias/NEONsupport/validreturn requirements asE301. Faults,concurrency/cache/prefetcheffects andactualruntimewinner remainOFFEN.

- E-XE164-305 VERIFIZIERT: Own C byte-range predicate a<=C and b<=C-a is mathematically equivalent to original sized-provider unsignedmax(a,b)<=u32(a+b) andC>=sum underexplicituint32 operandidentity. Owntransaction/readiness/fault behavior andoriginalhelper/nullcallback gates areseparatefacts. Existing ownsourceassertions enumerated; noheader/buildoffsetmapping ornumericmacrovalues invented. Operand/field/slotidentity remainsHYPOTHESE/OFFEN; mathagreement neither provescompatibility norrequiresreplicating originalinternals. Projecttests/build/runtimeNOT_RUN; publicrepo unchanged.

- E-XE164-306 VERIFIZIERT: Separate-context+58 candidate sourcecell141ac hasunique symbol0R_ARM_RELATIVE addend2ba8. Complete112B/28wordbody tests3helpers forzero=>ffffffff, thennullcurrent_return+3ccallback=>1, else tailBX withcurrentr5/r7/r6->r0/r1/r2. Conditionaloldconsumerinputs0,0,stackoutword maptotail0,0,outword onlyiflivevaluesretained. Separate listentrycontext not equated to primary/getterobject. Actualtarget/callbackidentity andoutputwordeffects remainOFFEN; noAPI/ABI inferred; runtimeNOT_RUN.

- E-XE164-307 VERIFIZIERT: Closed conditionalComponentEntry instance steps174PCs:117Dal+6PLT+3getter+48libccopy. Two distinct pagealignedbias fixtures withoptionalentry+28NULL, exactGOTtargets and7validglobaldatacells returnr0=0 viaencoded72Bframe/epilogue. All34providerRRELwords copied136B beforepoststores;60Bentrystage,vectorD+78 andsixcycliccells traced; exactSP/GP/d8/d9effects recorded. Fixturemapping/GOT/relocation/globaldata/optionalcallbackstate stipulated, notruntimeobserved. SourceandDtableleadingcellsdifferafteroverrides; noAPI/ABI/fullobjectidentity inferred.

- E-XE164-308 VERIFIZIERT: Actual independentLuna review supportsfull286174PCcomposition, cross-DSOBXnextPCtranslation, all34RRELcells, 60Bstage, sixfinalcells, entrysideeffects, eightbytealignment andstack/registerconditions. Reusespinnedstepper asgeneratorbutseparatelyderives sourcebranch/GOT/ELF/bias/spanoracles. SameexplicitfixturepremisesasE307; actualruntimeimportwinner/state, faults/cache/concurrency remainOFFEN. Independenceofreviewisnotindependentnativeexecution.

- E-XE164-309 HYPOTHESE: Reviewed nine-positionmatrix restores sourcefacts fororiginalgetterO+0c/+10 andsixcyclic/separatelistcontext58, withcorrectcallerreportsWP198/199 anduniqueheader. O=ProviderBias+14154 isdistinctfromconditionalcopyD=DalBias+1a270; laterD+0/+4 targetDalBias+209c andD+10/+14/+6c targetDalBias+20c8; thoseoverridesdonotchangeoriginalO. Numericmatrix isimplementationhypothesisonly. Runtimeprovider/object/contextidentity, completeeffects/API/ABI andbroaderprofiles remainOFFEN. Sourcebody/callerfacts do notmakeeveryinternalgate a replacementrequirement. Canonicalmatrix work/root/continuation-2026-10-18-0858/nine-position-matrix-reviewed.tsv.

- E-XE164-310 HYPOTHESE: Closed conditionalSelector15 instance reachesr0=0 atCore2ff770 forhalfwords2/4/5 throughhelperBX,Dal15,resolvedgetter andoriginalprovider+4bytezero leaf,thenDal/Coreencodedepilogues. Explicitinitialmanagerglobal/readability,exactGOT/RREL/nonalias/stack/Dalno-callbackpredicates required. Noactualruntimewinner/tableidentity/mandatorylifecycle/ABI claim; byte1 firstopaque call liesoutsideclosedresult.

- E-XE164-311 VERIFIZIERT: Actualindependentreview source-derivesleafr2=0,r3=P+141e0,PLTwritebackr12=G+16030,commonGP/SP/r0summary andconcretecorepostludeboundary. Actualboundaryplus12explicitvariations return0; wrongGOT/+4cellcontents followcounterfactualpointertransfers ratherthanscalarinequalitychecks. Twelve finitevariants arecontrolsonly; nopreciseuniversalcallpreservation inferred. Runtime/GOT/alias/frameconditions stillstipulated.

- E-XE164-312 VERIFIZIERT: Exact GLib integer callbacks comprise hash4756c/8B reading one word and equality47554/24B returning1 iff two readable32bit words equal. Helperbac64/32B returns saved_r0-saved_r1*nested_r0 in r1 on nonzero input. Nestedbaa78/492B has123 audited words; only divisor1 SUBS/BXEQ route is closed with GP/SP/LR retention. General nonzero computed-PC control closure and whole-call preservation remain OFFEN. No API/ABI, general quotient semantics, live callback binding or constructor field identity. Conditional libdal1c80/1c88 args require currentr6=14000 across opaque calls.

- E-XE164-313 VERIFIZIERT: Exact libdal1a3c/296B conditional candidate path explicitly stores7c8 at currentr5+110, currentr8 at+100/+11c, currentr9 at+104 and two opaque returns at+108/+10c. PC-relative literals derive global141e0 at two sites. Insertcall1b4c->PLT1414 locally supplies r0=[currentr6],r1=currentr5+100,r2=currentr5,r3=latest188creturn. Counter arithmetic wraps32bit; finite termination not proved. Opaque calls do not establish allocation/zeroing/registration/strcat effects or register retention.7c8 is a data word, not an executable callback. Runtime table/record identity and actual memory remain OFFEN.

- E-XE164-314 VERIFIZIERT: Source-local224c->PLT13f0/GOT14040 names LibraryLoader_LoadSymbol with r0=[currentr6+104],r1=currentr4,r2=currentfp-32. If local return!=-1,226c BLX uses loaded[currentfp-32],r0=currentr6+110 as an ADDRESS,r1=ProviderBias+141e8. Returnzero writes byte[currentr6+170]=1, nonzero0. Raw suffix3d40 is exact _open NUL; fullsymbol remains conditional. Later+158 is a distinct nullchecked callback. No opaque strlen/strcat/LibraryOpen/LoadSymbol effects or GP/frame preservation inferred. No complete symbol string, backend target, actual outputword initialization, callback population, ABI or runtime binding proved.

- E-XE164-315 VERIFIZIERT: Actual independent Luna302 finds original300 stepper misassigns55e60 as r11shift and55e64 as bucketload, omitting actualCMP flags. Raw55e60 is LDRr3,[r2,r11],55e64 CMPr3,1,55e68 BLS. Two fixed positive results remain T but intermediate fullstep claim is rejected. Arithmetic-only snapshot/frame assertions are tautologies; original300 frozen, corrective306 separate. Independent static review is not ELF execution. Divisor1 fixtures are stipulated; constructor reachability, actual binding and general semantics remain OFFEN.

- E-XE164-316 VERIFIZIERT: Exact constructorELF4584c/120B stores currentr5/currentr7 at currentr4+24/+28, after capturing entryr0/r1 before opaque calls. Exact initializer44fb4/84B writes+0=8,+4=7,+8=7 and byte+14lowbits3 before its first opaque call. Later allocator-named returns stored+18/+20 and+1c; effects remain opaque.51sourcewords plus2poolwords retained. Equating stored GP values to entry callback arguments requires preservation across earlier calls. Actual allocation, initialized bucket memory, table identity, fullconstructor reachability and preservation remain OFFEN. Initial divisor7 differs from stipulated300 divisor1.

- E-XE164-317 HYPOTHESE: Two stipulated61-PC source-derived lookup instances return T through exacthash/equal and nesteddivisor1 fastreturn. Correct55e60 LDRr3,[r2,r11],55e64 CMP7,1 setsNZCV0010,55e68 BLSnot-taken. Actualstackwrite/read/savedregister/SP state andstatus events checked; isolatedstatus1/0lanes takezero-return. Original300fullstepmodel rejected/frozen. This is a stipulated synthetic path only. Original phrase constructible provider table is not adopted. Constructor304 initializes divisor7; divisor1reachability, callback tokens/runtime binding, API/ABI, faults/concurrency and actualexecution remain OFFEN/NOT_RUN.

- E-XE164-318 VERIFIZIERT: Actualindependent309 rawPC/flag audit supports corrected306 statusload/CMP/BLS and statefulpositiveframe/memorychecks. Isolatedstatus1 setsNZCV0110 and0sets1000; bothBLSzero. Independentreviewqualifies constructibility andstipulated isolatedsavedframe; no constructionproof. Static independent review is not binaryexecution. Constructor/livecallbacks/generalGLibsemantics remain OFFEN. Upstream306 frozen; narrower canonical wording retained separately.

- E-XE164-319 HYPOTHESE: Four source-driven78-PC synthetic instances close libdal2194/1ecc via directly-resolved3wordPLT15f4/GOT140ec to exactGLib lookup/callback/divisor1 path. Helper keyentryr0=7 is storedSPentry-12, lookupreturnsT;2194readsbyte[T+170]=1,1eccreturnsu32(T+110). GP4..11/SP retain entry state andsavedreturnPCcontrol holds in Root313supplement; LRitself endsGLibBias+45e2c. ResolvedGOT/global141e0/tabledata/byte/callbackaddresses/nonaliasframe/nofault premises stipulated. Numericdivisor1 notconstructor-derived; actual provider/table/record/runtime/API/ABI identity remains OFFEN. Allwrites in selectedprivateframes, no ELFexecution.

- E-XE164-320 VERIFIZIERT: Exactinstalled liblibloader inode1772/13696B SHA8fe106f2...609cf2 exports LoadSymbolELF1ee4 Dynsym452B; actual396B/99wordbody plus56Bpool separate. Valid-input localroute storescurrent indirectresult to savedoutputpointer; nonzero localresult leadsreturn0, zero followsopaqueloglane. StaticGLOB_DAT13088->PosixHelper_DlSymobject130b0 andR_ARM_ABS32dlsym@GLIBC_2.34 pinned. Conditional301join yieldsnonnullcallbackword onreturn0 underframe/GP/output-memoryretention. Currentframe/GP/savedword retention and outputnonalias/writability explicit. OpaqueIsLibraryOpen/indirecthelper/log/assert effects, appliedrelocations/runtimewinner, actualcallbacktarget andAPI/ABI remain OFFEN. Ghidraassertterminalflag isnotverifiednonreturn. No calledimplementation expanded ornativeexecution.

- E-XE164-321 VERIFIZIERT: ReadonlyFW31partition2 inode1874 yields libpackbus.so.1.0.1/148792B SHA3b7b7ca4fa14e5994552040a7b40b1cfbbf43e0649a4ad9277ece421fd4bc5d6; threealiasesresolve tosameregularfile. Freshcompletebytecomparison equalspriorWP004FW30library. Exportlibpackbus_open ELF10720declared1844B; actualREA noncontiguousbodyGhidra[20720,20d00)+[20dd8,20e54)1628B/407words,216Bgapseparate. OneartifactbyteidentitydoesnotproveFWimage/device/ABI equivalence. Actualdynamicbinding/initialization/hardware/API semantics remain OFFEN. No vendorELF/VM/device/networkexecution.

- E-XE164-322 VERIFIZIERT: Exact131sourcewords comprise123wordnestedbaa78 and8wordcallerbac64. Selectedinputr0=77,r1=7 computesGhidraPCcabf8 andexecutes31nestedPCs, fiveLSL4..0/CMP/ADC/SUBCSstages, returnsr0=11. Caller saves77/7/LR, restoresintosavedr1/r2/LR, computesr3=77andr1=0, restoresSP/LR in2fixtures. Original305validatorread-onlyclaimFAIL: writes3artifacts; frozen315pureinmemoryreplay iscanonicalchecker. No generaldivision/quotienttheorem, arbitrarycomputedtargetclosure, zero-handlersemantics, actualconstructor/table/runtime/API/ABI proof. Stack/memory/nofault conditions explicit.

- E-XE164-323 VERIFIZIERT: Actualindependent312 auditsall131rawwords, computedPCcabf8, all31nestedPCs/flags/fivecomparestages and8callerwordeffects in2frames, supporting77/7->11andindex0. Detects305validatorwriteoperationsattrace/results/controls anddoesnotexecuteit. GeneralroutesremainOFFEN. Independentstaticreviewisnotnativeexecution. Original305operationalreadonlyFAIL retained. Constructorreachability/API/ABI/runtime/hardware semantics OFFEN.

- E-XE164-324 VERIFIZIERT: Corrective315 moves305boundedreplayinto puregenerate_outputs(), disablesbytecodewrites, verifiesexactpins/copies, andbytecompares3inmemoryserializedoutputs withfrozen305trace/results/controls.41checks andbefore/afterpackagehashinventoryPASS; defaultvalidator/importhasnofileoutputsideeffect. Original305/312unchanged. Operationalcheckerfixonly; no newarithmetic/runtime/constructor/API/ABI conclusion. NativeELF/device/networkexecutionNOT_RUN.

- E-XE164-325 VERIFIZIERT: Exactlibpackbus_open407wordbody plus54poolwords stage16callbackwords throughGOT/stack/D8..15 then4vectorstores at currentr4+14/+24/+34/+44. ThreefurtherGOTstoresat+54/+58/+5c; +4/+8 each2ee0. CMPcurrentr4,r6 equalityskips publication. All19callbacknames haveexactR_ARM_GLOB_DAT source relocations. Original311IoDrvDal226c attribution/base+110 comparison notadopted; use318andRoot323. D8..15/currentGP/frame/GOTpreservation acrossopaque calls explicit. Actualpublication/runtimebinding/API/ABI/hardwareOFFEN.

- E-XE164-326 VERIFIZIERT: Actualindependent318 reproduces19callbackpositions/relocations,16vectorlanes,2ee0words andpublicationguard. Corrects sourcejoin:226c belongs libdal.so, r0=currentlibdalr6+110; backendinitialr4=entryr0. Ifretained,publicationcell=currentbackendr4+fieldoffset=T+110+offset; never addsecond110. BackendGOT ELF33000/Ghidra43000/runtimePackbusBias+33000 separated. Pointerequationconditionalonly; actualcalledprovider, GP/Dreg/stackmemoryretention, actualTandproviderwinner remainOFFEN. Staticindependentreviewnotruntimeexecution.

- E-XE164-327 HYPOTHESE: Reviewed7rowmatrix links6primaryproviderpositions30/3c/40/44/50/54 andseparatelistcontext58 conditionallythroughlibdalmethodstoC+2c/20/30/24/18/28/3c,withC=T+110. Exactbackendexports WriteStart/WriteBytes/WriteEnd/ReadStart/ReadBytes/ReadEnd/DiagGetDeviceState andELFentries derivedfrom318relocs+310dynsym. C+4/+8conditional2ee0 words retained; O,D,primary/separatecontexts remain distinct. Composedinstancenotobservedruntime. Identicalnumericpositionsdonotproveobjectidentity,API/ABIorconstructorreachability. Originalinternalmechanicsnotautomaticallyreplacementrequirements. No vendor/runtime/VM/device/networkexecution.

- E-XE164-328 HYPOTHESE: Two distinctbias/datafixtures withtable numeric+0=8,+4=7,+8=7 close2194/1ecc throughdirectresolved3wordPLT, exactGLiblookup/hash/equal and31PCselected77/7arithmetic. Four107PCprimaryroutes returnbyte[T+170]=1 oru32(T+110), restoreGP4..11/SP andsavedreturnPCcontrol; exactNZCV/PC/register/memoryeffects recorded. Fivefinitecontrolsspan500rows. Matching8/7/7initializationwordsdoesnotproveconstructedtable/callback/arraypopulation/actualruntimebinding. Allmemory/GOT/frame/nofault/nonconcurrency conditionsstipulated. No generalquotient/probe/API/ABI proof ornativeexecution.

- E-XE164-329 VERIFIZIERT: Actualindependent322bytechecks249sourcewords, four107PCprimaryroutes and500controlrows againstsourcewhitelist; independentlyderives77/7computedPCcabf8and31PCflags/stages using312route, confirmshelperbyte/T+110results andexplicitinitializer8/7/7scope. Generalconstructor/runtime/API/ABI conclusions remainOFFEN. Independentsourcereviewnotnativeexecution. Modelgenerationreused314butarithmetic/sourceoraclesseparate312/rawbytes. Allinstance/binding/alias/fault/concurrency limits retained.

- E-XE164-330 VERIFIZIERT: Actual independent raw-source audit of original317 confirms 178 words and conditional empty-branch/store deductions but rejects complete instruction replay: omitted31 nested PCs, early quotient injection, wrong NZCV/next-PC continuity and fixture mismatch. Original317 frozen, not canonical full replay; local source deductions conditional on opaque normal return. Corrective327 replaces replay evidence.

- E-XE164-331 HYPOTHESE: Corrective source-stepper binds301words, two135-fetched-PC routes each119 executed/16 skipped, including31 nested77/7 PCs. K>T flags0010, real BL at456e0 passesB,32 to bias+7f11c; separate stipulated return r0=V yields H20=V,B0=K,V0=T, three counters1, return1. Three source controls checked. Fixture/opaque continuation only, not construction/runtime. Canonical normalization per333: columns r0-r14 plus nonarchitectural r15 sentinel and separate PC; H/C/frame retention stipulated, no B-retention requirement. All memory/fault/alias premises explicit.

- E-XE164-332 VERIFIZIERT: Independent checks301sourcewords/270 positiveinstructionrows, raw branch predicates/computed targetbabf8, quotient11/index0, source stores and3controls. Representative volatile clobbers preserve selected suffix; r15 sentinel and opaque B-label qualifications recorded. Static source audit only; finite clobber probes not arbitrary-clobber proof. Upstream327 decoder reused for probes, independent raw source/ALU checks; no native execution/API/ABI.

- E-XE164-333 HYPOTHESE: Seven libdal candidate methods source-step through2180/2194/1ecc, resolvedPLT and divisor7 GLib route:14paths3392fetchedPCs/1778memoryevents,10controls,451sourcewords. Exact BXr3 tails preserve selected SP/LR/GP4..11 and record numericr0..3/backenddynsym pointers. Stops before backend fetch. Callback cells/table/GOT/frame/record identity stipulated. Six cyclic getter cells and separate58 candidate/context remain distinct; no runtime producer binding, API or ABI.

- E-XE164-334 VERIFIZIERT: Independent audit verifies451rawsourcewords, getter R_ARM_RELATIVE addends,7backenddynsyms,14tails3392PCs/1778events and10controls; backend not fetched. Shared303/314 stepper lineage disclosed. Numeric conditional source join only; original runtime publication, constructed object/table identity, callee effects and physical I/O remain OFFEN.

- E-XE164-335 VERIFIZIERT: Exact7backend bodies415words/11poolwords plus optionalReadStartGate26+1. All derive cellG=BackendBias+44420;32mainBLs and4helperPLTs pinned. Source local status gates, byte-method unsigned segmented arithmetic,2ReadBytes memset sites/noWriteBytes memset, numeric diagnostic3/0/2/1 stores recorded. Canonical336 corrections apply: G is cell address; source tests S=[G], then needed[S]/[S4], no G-null/readability guard. Post-opaque ReadBytes requires live r4/F,r5/X,r10/E,r11/A, conditionalr7/S,r8/Z/frame/query/state preservation. No API/ABI/callee effects inferred.

- E-XE164-336 VERIFIZIERT: Independent raw-source review checks415+11 words, optional26+1, eightcelladdress equations,32mainBLs/4helpercalls and PLT relocs; ReadStart helperzero→clock,ffffffff→directreturn. ReadBytes/WriteBytes arithmetic/call vectors and diag local status verified. G terminology and live preservation qualifications supersede324 prose. Source-state predicates/segment equations only, no semantics from names, broader range correctness/runtime binding/concurrency/fault guarantees remain OFFEN.

- E-XE164-337 VERIFIZIERT: Fresh readonly exact FW31 partition2 inode dumps782/783/784 produceXE164L1/L2/L3 sizes32/266/16598, each fully byte-equal pinnedFW30source. Composite recipe32+266+214zero+16598 yields17110B SHA5ab9fec0977c26ed4895f8e3d61009f0b371fe46fa9dc76017d6f31eff2f3983 equal priorcomposite. Four source/additioncatalogrows separately retained. Only these precise files/composite identity; E00000 placementHYPOTHESE. No loader/startup/SFR/ABI equivalence, no FW31 C166 execution or transfer of earlierPASS.

- E-XE164-338 VERIFIZIERT: Independent audit binds image/inventory/partition/inode records and byte-equality of three FW31/FW30payloads; independently reconstructs17110Bcomposite without335builder and confirms old/newhash. Extraction itself notrerun; preserved recipe/stat/dumps inspected. Currentcataloghash recorded, no prior snapshot proves historical immutability. E321 backendcomparison outside337scope. E00000mappingHYPOTHESE/runtimeNOT_RUN.

- E-XE164-339 VERIFIZIERT: Exact getterELFec88/12B plusliteralec94 returnsimage-relative337f8. 28nonnull52Brecords plusrow28zerosentinel: name32,+20word,+24function,+28argc,+2cargtypes,+30returntype. 110 argument slots and28returnslots bound to raw ARMrelocations, separate observedREAfixups and candidate libffi versioned12Bobjects. Canonical339 corrects prose: argspan file23ddc..23f98, not25ddc; argument types includeuint32 (3) besidesuint8(50),pointer(42),uint16(15). Raw TSVs correct. Ghidra external tokens notruntimepointers; API/ABI/reachabilityOFFEN.

- E-XE164-340 VERIFIZIERT: Independent raw ELF PT_LOAD/table/reloc audit checks29rows,110argumentcells, both334TSVs, getterequation, candidate libffi symbolvalues/versions; alltabledata correct. Threeuint32args are row21arg0,row22arg0,row24arg0. Returnrefs26sint32/2uint32; all138typecells zero-addendABS32. Two334proseerrors correctedwithoutupstreammutation. Raw symbolrefs/localcandidate match doesnotprove binding/prototype/ABI. Report finalself-reviewboilerplate doesnotnegate actual distinctauthor audit; Root recordsactualscope.

- E-XE164-341 VERIFIZIERT: Exact AppStateChanged142words plusfourwatchdogbodies39words and12PLTwords=193;9separateliterals all deriveGcell44420. Twelveapplicationstores/18opaquecalls/fourwatchdogrelocs pinned. WatchdogsnullSreturnffffffff; nonnullr0=[S+dc], SetTime forwardsentryr0→r1/entryr1→r2; otherwrapperspreserver1/r2locally. Original state2report/storeledger reversedroute and is supersededby338: policy1/freshprior1directlystores1 at+a0 withno+a1read; otherselectedstate2routesnormalize+a1. Freshloadsnotassumedidentical. Opaquecallpreservation/currentstate conditional, retry no convergence; no stateenum/API/physicalwatchdogclaims.

- E-XE164-342 VERIFIZIERT: Independent193word/9pool audit derives3state2routes: policy!=1 andpolicy1/freshprior!=1 read+a1 andnormalize0/1; policy1/freshprior1 bypasses+a1 andstoresr2=1 directly. Numeric correctedmatrix/sourcepaths retained. Fourwatchdogtails/PLTGOTarithmetic/relocs verified. Selected sourceconditionsonly; entryr4/global/frame preservation acrossopaque calls mustbestipulated. Earlier/laterpriorwordloads distinct, nofinalstate/convergence/API/ABI/physicaleffectproof.

- E-XE164-343 VERIFIZIERT: 168words exact O70wrapper29e4/common2784/helper20b0,2getterRRELcells and30executableinlineBstubs. Wrapperr2=S-8 points2savedwords; helper20b0 loads distinctglobal141e4 andforwardsname. Commoncase widths/callvector/returncopy bounded; ffi_callstaticJUMP_SLOT1409c. All currentGP/memory/frame mapping after opaque helpers conditional. Unsupportedtag4/13/>14 setsr7=-1 butcontinues, noinputadvance/vectorstore. Tag0 likewise skipsstorewithoutmarker. NoAPI/ABI/runtimecallerrepresentation inferred.

- E-XE164-344 VERIFIZIERT: Independent168rawword/30branchstub audit confirms wrapper24Bframe, both15casedispatches, zero-nargsr3=0 andnonzeror3vectorbase. Unsupportedargcases leavevectorcelluninitializedbythispath yetadvancevectorcursor and reachffi_call. Global/device labels shorthand observedcalltests. GP4/5/6 across earlierhelpers andr7survivalacrossffi_call OFFENwithoutexplicitpremises. No nativeexecution.

- E-XE164-345 VERIFIZIERT: Exact46764B FW31libffi SHAd162a9b2...17c4f5,803REA/rawsourcewords incl326noncontiguousprep/7wrapper/300internal/4+11thunks/48+107helpers,10versioned12Btypeobjects. Prep guardnumeric1/2 accepts,othersreturn2;sourceCIFfieldstores. BLX8010targetcurrententryr2 andcurrentr11framecontinuation; bounded7returnslots0..6 rawfallback. No completeconstructor/ffi_call/ABI closure. Ghidra nofunction18040 errorretained,128Breadcontextafter8078notpromoted. All target normalreturn/frame/currentr11/memory dependencies explicit; runtimebindingOFFEN.

- E-XE164-346 VERIFIZIERT: Independent803word/PT_LOAD/typeobject/version audit confirmsnoncontigprep235c..2468+7644..7a50,tail240c→7644,guard/fieldstores,wrapper andBLX/currentframe mechanics;7rawreturnslots. Canonical caller erratum:8000callatGhidra174f0 belongs internal17194body, NOTffi_prep_cif as343prose says. Independentlyreconfirmedbyreviewer349;343 frozen. Completefunction/ABI/runtimeeffects remainOFFEN.

- E-XE164-347 HYPOTHESE: 28namedrecords/110args map candidate libffitypes5(50),7(15),9(3),14(42) tosource wordinputadvance4/staging8/stores1,2,4,4;28returns9/10copy4. Selectedstackbeforecall40+align8(4n)+8n, max128 atn7, excludesouter24/callees. Requiresmatchingcandidatebinding/recordconstruction, successful earliergate/name/helperpaths andliveGP/frame/memory continuity. No publicprototype,callerABI,pointervalidity or runtimeproof. Generalunsupporteduninitializedslotpaths remainpossible forothermetadata.

- E-XE164-348 VERIFIZIERT: Independent recomputation checks28nonsentinelrecords/110rawrefs, exacttypefields, handlerwidths/targets andall28ret4bytecopy cases; stackarithmetic0args40/max128; no upstreambuilderoracle. All110supportedhandlers is conditional onbinding AND reachingselecteddispatch withvalidlivevalues acrossopaquehelpers. Synthetic compatibility notexecution or constructedrecordproof.

- E-XE164-349 HYPOTHESE: Source-stepper startsstipulatedpost2194successat27c8: args5/7/9/14write low1/2/4/4bytes into8Bslots, exactBL28ac/1504numericr0..3. Zeroargsr3=0; unsupported4setsr7ffffffff/vectorcellunwritten yetcalls. Separatepostopaque28b0return5/7/9/14/4 copies1/2/4/4/none,stops2878beforeepilogue. Startsselectedsyntheticstate; r11/SP relation fromactualprologue notestablished, no reachability proof. Earlier2180/20b0/2194 andffi_call opaque. Exact result/register/frame premises explicit; noABI/API/actualnativeexecution.

- E-XE164-350 VERIFIZIERT: Independent frozen340audit checksrawbytes/PCcontinuity/computedbranches, both15Bstubtables, argument/returncases, sourcewrites andunwrittenunsupportedcell; validatesactualcallr0..3 andseparateopaque-returnconditions. Finite selectedsourcepaths only. Initial27c8syntheticstate notshownreachable frombodyprologue; returnedSP/GPepilogue notmodeled. No hidden helper/callee/ABI preservation.343callererratumconfirmedwithoutediting343.

- E-XE164-351 VERIFIZIERT: 407wordopen/54pools deriveG=BackendBias+44420; uniqueidentifiedSTRr8[r9]at10ba8publishescurrentallocationword undercurrentGP/opaquehelpergates. ExtraORRSr4|r6 gate afteropaquecall required; existingSskipsallocation. Directlocalzeros+a0/+a1/+a2 andopaque-returnwrites+0/+4 inventoried. Frozen342 '325/338distinctprovider' prosefalse: sameexactbackend/globaladdress; corrected351. EqualGnotpersistentSidentity. No allocatorzeroing, helperwrites, callorder/termination, runtimebinding/ABI inferred.

- E-XE164-352 VERIFIZIERT: Two22worddefinedbodies plus2x3wordPLTs=50words/4pools. CreateWatchdog source storesopaquereturnthroughcurrententryoutput, returns0on nonzero; vGet copies6currentwordsfromELF47bac+18..2c tocurrentoutput+0..14. ExactstaticPLT/JUMP_SLOTtargets14c68/14a50. Register/frame/outputvalidity acrossopaqueallocator/once/lock/unlock calls conditional. Callback14774hadnoGhidraprocedure; no inventedbodyin348. Staticbindingnotactualwinner/API contract.

- E-XE164-353 VERIFIZIERT: Underexplicitlocaltarget/currentGP/memory premises openhelpercallentryA+dc receivesopaqueallocationreturn; nonzero→helper0→opengatepasses. vGet6words landA+a4,a8,ac,b0,b4,b8; openimmediatelypublishescurrentr8throughr9 withouttestingvGetr0. SameimageReadStart+d4 distinctDiag+dc consumer. No+d4producerfromthesebodies. Currentglobalwordorigins/actualcallback14774effects unexpandedhere; later352sourceevidence separate. Instance/lifetime/ABI/allocationzeroing/synchronization notestablished.

- E-XE164-354 VERIFIZIERT: Independent407+50word chainreview rawchecks bothGaddresscalculations/publication, entry/currentregister/helperreturngates,2PLT/GOTrelocs,helperstorevectors andfieldcoverage. Correct342sameprovidererratum explicitly; 325/338samehash/G. Conditionalproducerassociationonly. Normalreturn/currentGP/frame/globalword/destinationnonalias/readabilitypremises required; nopersistence, objectidentity, actualrelocation orfunctionsemantics inferred.

- E-XE164-355 HYPOTHESE: Six source-driven entry235c preparationfixtures use326prep+107classifierwords; numericmode2zero/2/3/7args setCIFfields and16FFbytes at+20..2f, true6fe8classifierpaths return0for5/7/9/14; mode1acceptedwithoutNEON/classifier,mode3returns2beforeCIFwrites. ActualsyntheticSP/GP snapshots retained. Frozen347proseELF16fe8..17094 erroneous; correctELF6fe8..7194/Ghidra16fe8..17194, tables/tracescorrect. SyntheticCIF/type/stack/memoryonly; no constructor/runtimebinding/ABI/type meaning.

- E-XE164-356 VERIFIZIERT: Independent433rawsourceword/typebyte audit checks6traces, source-updatedNZCVconditions/computedbranches, actual6fe8→7044classifierreturn,16FFNEONstore andnumericmodecontrols, GP4..12/SP snapshots. Source/classifieraddresserratum explicitlycorrected. Finite selectedpaths only; notseparatefullCPUvalidation norunselectedsignature/ABIproof. First347rangeend17094also typo, canonicaluses17194Ghidra. Upstreamfrozenunchanged.

- E-XE164-357 HYPOTHESE: Two fixtures beginactualffi_call7a64entry withmode2records byte-matched347, run84/145fetchedPCs through7194/69ec byte-wordhandlers/8010BLXtarget, separateopaqueeventresult, raw8060store andfullframe/wrapperrestore. 817sourcewords bound; classifier6fe8/memcpy14dc notfetched. Canonical361 correction mandatory: original353eventlists4preservedframewords butsuffix needs15. Required r11/r0 pluswordsat+ranges0..c,24,54..74(nine),84; otherGP/SP/flags/memoryfiniteclobberprobechecked361. Targeteffects/runtimebinding/reachability/ABI stillOFFEN.

- E-XE164-358 VERIFIZIERT: Independent817rawword binding and84/145selectedsourcePCreplay checksflags/branches/helperloads/stores/targetstate/fullreturn. Derives15postBLXreadwords; preservingonlythese plusr11/numericr0whileclobberingallothermappedbytes andr1..10/r12/LR/SP/NZCVstillcompletesselectedsuffix. Four-word353target-eventpremise incomplete, notpromoted. 15wordpremise/path-specificfiniteprobe, notgeneralcalleeclobber/ABI guarantee. No actualtargetcode/nativeexecution.

- E-XE164-359 VERIFIZIERT: 178actualsourcewords/8pools: Get60/Put50/length45/accessTX19inclfarPLT3/accessRX4. Get/PutgateE=U32(r1+r2)>2edf returnsnumeric3 beforehandle/data/othercall. Sourceacceptedloops/queryoutputs/bufferPLTboundaries inventoried. Rawsumwrapacceptedgate notmemorysafety. accessTXnoncontigspan29952isnot76Bcodeextent. Importedcallee/memory/callbacksemantics unexpanded; pointer/currentGP/framepremises explicit; noAPI/hardwareclaim.

- E-XE164-360 VERIFIZIERT: Exact6sourcewords GetPLT777c→GOT3312c/staticSSC_Gete17c andPut7cb0→332e8/staticSSC_Pute370; actualretainedmetadata/body records andrawrelocs agree. RuntimeGOTcontents/preemption/loaderwinner mustbestipulated; names/relocsnotruntimebindingorprototype.

- E-XE164-361 HYPOTHESE: Fourfullsourcepaths at2biases startactualbackendReadBytes/WriteBytesentries, passX11999/Y1 viaexact3wordPLTs tolowerGet/Put, gateE12000→r0=3, actualupperthenreturns0 withSP/GP4..11restored. NoZaccessorO-dereferenceonselectedrejectpath. Twelvefinitecontrolsstopaccepted/wrappedgate orreturndisabledwithoutSSC. Canonical365corrects358prose O=S+4: OiswordstoredATaddressS+4, numericallydifferentpointer. FixtureG/S/flags/halfwords/GOT/sourceframesonly; noruntimecaller/APIbug/statussemantics/memorysafety claim.

- E-XE164-362 VERIFIZIERT: IndependentrawA32replay verifies4primarytraces,8acceptedgatecontrols,4disabledcontrols andallmemoryevents; audits150+137upper/60+50lowerwords/6PLTwords. Lower3/upper0/noZorOobjectextentaccess andactualframe/GP restoration confirmed. Acceptedcontrolsstopbeforefollowinglowerinstruction, soacceptedbranchnotacceptedmemorybehavior. Oloadproseerratumrecordedwithout358mutation. ExplicitresolvedGOT/instancepremises; noABI/API/runtimeclaims.

- E-XE164-363 VERIFIZIERT: 19exactsourcewords hash11/equal5/strcmpPLT3. HashsignedLDRSBrecurrence U32(33h+signedbyte), initial5381, finite28ASCIIfunction-namevaluesderived; equalCLZ>>5mapsopaque32bitr0zero→1/nonzero→0. PLTGOTELF134044/GLIBC2.4 bound. Finitearithmetic notinstructionreplay/lookup. strcmpimplementation/equalitysemantics notassumed; returnframe validity afteropaquetargetconditional. Actualcallbacktableconstruction/symbolbinding/ABI/runtimeOFFEN.

- E-XE164-364 VERIFIZIERT: Independentraw19wordaudit and28namehashrecomputation excludezerosentinel, confirm signed0x80/ffcontrols andempty5381; PLTrotatedimmediatearithmetic/staticGOTrelocationverified. Onlyboundedsource andfinitevalues; no actuallookup/callbackbinding/stringmemoryvalidity/ABI/APIproof. Opaquereturnvalue/equalityframepremises retained.

- E-XE164-365 VERIFIZIERT: 163 complete-body words plus9 bounded callback words/11 pools establish numeric base47bac, callback14774, getter/setter/reset source. Callback slice zeroes48B before opaque tail; reset zeroes24B after once-named call. Bounded callback has no recovered complete procedure. Current GP/frame/memory after opaque calls conditional; no initialization/lock/API/ABI semantics.

- E-XE164-366 VERIFIZIERT: Get stores min(Q>>3,ffff), local return2 at Q>=80000; zero-global fallback performs clear then reload, so aliases matter. Set unsigned BHI means r5>Q>>3; equality zeroes selected block, below returns1. r5=65536,Q=524280 selects update but STRH stores0. Reset returns current opaque r0 unchanged. Numeric branch/store matrices and finite controls, not full instruction replay. Query/frame/GP/current-memory premises explicit; no value units/status/API or runtime binding.

- E-XE164-367 VERIFIZIERT: Independent172 raw-word/11-pool audit recomputes base/callback arithmetic, unsigned branch gates, threshold equality, partial store gaps, 65536 truncation witness, getter alias ordering and reset opaque-r0 flow. No actual callback execution or general alias/runtime/opaque-callee contract. Zero comparison does not prove pointer validity.

- E-XE164-368 VERIFIZIERT: 81 source words: read24/write50/lengthPLT3/getter4. Read/write selector1 clear destination BEFORE reading possibly aliased source. Write selector4 attempts halfword A+2N-2 before N-2 negative gate. Getter returns4013c+U32(index<<4), no result dereference/guard. Source positions only, not descriptor/API layout. N0 access is ordered source fact, not native fault prediction. Length-record contents/producer still open.

- E-XE164-369 HYPOTHESE: 48 finite traces at2 biases cover alias/disjoint clear-copy-mask paths, numeric selectors0..6, XOR N1/2/3, N0 attempted A-2 read and actual stack operations. Alias source reads observe post-clear f0/read or f3/write fixture values. Model interprets retained REA assembly strings after raw-word binding; not an independent complete A32 decoder. N0 unmapped model stops before BMI; no native exception/reachability claim.

- E-XE164-370 VERIFIZIERT: Independent raw branch decoding checks5 computed-PC B stubs, LS/default routing, flags/access widths and all48 trace source fetches. Alias post-clear values, N1..3 XOR iterations, N0 pre-branch attempted read and encoded stack events agree. Bounded selected audit does not turn assembly interpreter into arbitrary-input CPU emulator. Descriptor semantics/runtime/physical behavior remain open.

- E-XE164-371 VERIFIZIERT: 140 source words include128 noncontiguous registration words, helper6 and2 PLTs. Local path requests60B, passes prep P+8/mode2 with row-derived operands, then return-zero stores P0/P4/P38. Selected48B prep interval P8..37 fits request beside device word P38..3b. CIF/consumer offset compatibility conditional on same P/current row/GP/frame and actual binding. Original O10 candidate327c is overwritten in copied D10; no manager-to-registration runtime join.

- E-XE164-372 VERIFIZIERT: Independent ELF PT_LOAD mapping verifies140 raw words, actual128-word two-range extent, branch/PLT GOT equations and static relocations. Numeric60B/48B overlay agrees with selected347/357 prep and330 consumer loads; E309 copied-D10 override retained. Reviewer discloses347 ancestry. Complete ABI/constructed object/table insertion/runtime reachability/allocator and prep opaque effects remain open.

- E-XE164-373 VERIFIZIERT: 263 source words/18 pools cover SetTime54,Start92,Stop15,Trigger38 and callfree comparison64. Nonnull SetTime uses wrapped N=U32(r1*r2), accepts1..3fffffff, stores1/N/Q/(N-Q*1e6)*1000/8zero bytes; full-range reciprocal bound proves Q=floor(N/1e6). Stop nonnull writesbyte18=0. Other methods retain explicit opaque/current-state premises. Null-P branch precedes MUL; multiply precedes N range guard only. Signed strict>1e9 normalization differs from equality. No units/lifecycle/API/ABI/physical watchdog meaning.

- E-XE164-374 VERIFIZIERT: Finite wrapped-product/reciprocal/store fixtures and two callfree helper paths support selected numeric predicates, equality-at1e9 no carry, signed comparisons and unsigned counterflag. Original SetTime snapshots are manually scripted and NOT accepted as complete instruction replay. Its replay.py writes and was not rerun.373 verifies helper histories;375/378 supersede SetTime-history gap.

- E-XE164-375 VERIFIZIERT: Independent263word/18pool audit proves selected U32/MUL/UMULL/MLS outputs and full accepted-range reciprocal bound; actual raw interpreter reproduces both helper traces including PC/NZCV/register/frame/memory events. Full SetTime snapshots in360 remain unverified by373. Numeric conclusions accepted separately. Invalid lanes stop before logger BL; no opaque-return or ABI claim.

- E-XE164-376 HYPOTHESE: Corrective raw-word stepper executes18 selected paths at2 address mappings,394 fetched rows/132 memory events, full r0..14/PC/NZCV/D16 and actual frame restore;3 invalid routes stop before logger BL. Selected numeric/store outputs agree with360. Independent378 qualifies36 push preimages: zeros are implicit model fill for absent preloaded stack bytes, not established initial memory. Post-push/frame/pop/return and numeric transitions accepted; no runtime/API/ABI claim.

- E-XE164-377 VERIFIZIERT: Independent raw decoder reproduces all394 rows and132 ordered effects across18 paths, checks54words/6pools, arithmetic, conditions, SP/r4/PC restore and invalid stop boundaries. Identifies36 model-default zero push preimages. Accepts zero preimages only as model default, not source-derived data. No other selected transition/store/return mismatch; finite synthetic source evidence only.

- E-XE164-378 VERIFIZIERT: 1004 freshly retained ARM words,172B excluded gap,11 initial44B rows/9relative path fixups and four complete FW31/worker004 artifact identities verified. Static REV length candidate000040d6 and exact L3 XOR83 computed; all initialselectors0. Canonical qualification379: row9 XOR/Ack fields verified, but frozen370 stronger no-resend sentence is not yet independently established by table/source-access audit. Reader/file reuse versus selected output-call vector needs separate follow-up384. No actual boot/transfer/placement or general FW/ABI equivalence.

- E-XE164-379 VERIFIZIERT: 2104 independent checks confirm four wholefile byte identities,1004words/noncontiguous extents,11 raw/fixed rows/nine RREL fixups, selected field accesses and finite size/XOR candidate. Flags row9 exclusivity/no-resend as unclosed stronger claim. Row9 retains same L3 path/sentinel as8, so table alone cannot settle reread/output. Rows4/10 remain only raw null-path/word1 records. Candidate sequence is arithmetic, not capture/runtime/reachability.

- E-XE164-380 VERIFIZIERT: 109 raw words cover Create61,snapshot19,flip16,leaves5/5/3. Create explicitly writes index words0/1/2, but no byteP24 initialization; separate nonbodyNOP and0/1 pool retained.36 finite permutation formulas use post-acquire/pre-unlock state. Allocator zero-fill/construction/actual locks not proved. Finite formulas not instruction replay; leafindex has no bounds. First source validator opcode typo fixed before freeze without changing source/formulas.

- E-XE164-381 HYPOTHESE: Original48-word selected models provide6 leaf cases,36 permutation endpoints,2 null controls and unmapped0x3048 read boundary; source routes and local formulas agree. No per-step GPR/NZCV/memory/frame histories. Object preservation across opaque calls initially implicit. validate.py IS A WRITER; Root inspected and did not rerun frozen369. Corrective377/382 canonical for complete histories.

- E-XE164-382 VERIFIZIERT: Independent109word audit confirms Create0/1/2 stores and no P24 store, pool/NOP boundary, leaf formulas/branch PCs and36 transforms. Identifies missing histories and missing acquire/unlock object-memory premises in369. Verified local pre-unlock writes do not establish returned object memory without unlock preservation. Actual allocator/locking/ABI/runtime remain open.

- E-XE164-383 HYPOTHESE: Raw-word stepper records45 scenarios/562 instruction rows,290 source-memory events plus180 stipulated opaque-memory events/72 call boundaries. Post-acquire tuple is explicitly installed; unlock preserves objectP18..24 and savedframe/SP while clobberingr0/r4. Actual MOV/pop thenreturn0 andrestore frame. 382 qualifies broad scratch wording: concrete fixture leavesr5..11 unchanged. D16 is implicitly unchanged at opaque boundaries, but selected outputs do not depend on that preservation (overwritten/unused). No actual callee contract.

- E-XE164-384 VERIFIZIERT: Independent23052 checks reproduce562 raw steps/290 source-memory effects/180 premise effects/72 opaque boundaries; actual push/pop restoresr4/SP/savedPC. Confirms pendingbyte supplied only post-acquire and no CreateP24 store. Concrete scratch clobber vector narrower than377 prose; D16 across opaque calls fixture-only and source-liveness-insensitive. All final object values conditional on explicit unlock memory preservation.

- E-XE164-385 VERIFIZIERT: 957 actual GetCnfFromRail words/10 separate pools,6 PC/literal equations. Four yieldB4013c, distinct4017c/GOT33000. Selected lane r6!=1 stores U32(r10<<3) atB+U32(I<<4),zero+8; r6==1 stores+4,zero+c; optional round via c974.176B source frame. Laterc89c/ca4c current-address increments have no whole-body invariantB+index proof: reusedSP24/SP28 overwritten elsewhere. Complete value provenance/descriptor/API/units/runtime remain open.

- E-XE164-386 VERIFIZIERT: Independent PT_LOAD/raw mapping confirms957word body/10 pool refs/6 equations and B4013c lies in BSS memory extent beyond file-backed data. Selected store fields/lane gates/rounding/frame exact. Source-local address relationships do not prove later live stack bases or complete constructor/producer path. Explicit overwritten stack slots preclude global pointer invariant.

- E-XE164-387 VERIFIZIERT: 111 selected raw words establish local row8 nonzeroN call vector(F,P,N), row9 prefix0/XOR1 seed0 fold over P..P+N-1 then vector(F,SP+d8,1), both ELF7998/Ghidra17998. N0 row8 skipscall,row9 calls withzero scratch. ExactL3 finite XOR83. Conditional selected call-vector distinction only, not guaranteed transfer/no other sends/runtime reachability. Reader can reread same L3 path; sentinel continuation needs current helperr0!=ffffffff/readableSP34 and frame/GP. No full CPU replay claim.

- E-XE164-388 VERIFIZIERT: Independent111word/table/loop audit confirms CMP flags survive EOR(S0)/STRB toBNE, N bounded byte reads and finite L3 fold83; reader sentinel continuation premises explicit. Root rejects386 alleged384 prose address typo: actual frozen384 report SHA c7ebaaa84d2126dbdee8dac31c01a724c9419c159ff346582c8341fe32bec2c2 already says7998 twice, no17998. Reviewer acknowledged error;386 frozen, correction recorded next389. Raw validator target correct.

- E-XE164-389 HYPOTHESE: 237 exact words and four selected name routes/1096 rows join helper20b0 through tablecell141e4, GLib signed-byte hash, full131word divide, equality and fixtureT. Canonical381 rejects mismatch-summary return0 because control stops before45de0; literal VA/file20c4 versusvalue12120 corrected; strcmp event originally omitted needed memory. PositiveT accepted only with stronger387 premises.

- E-XE164-390 VERIFIZIERT: Independent237word/PT_LOAD/source/flags/stack audit identifies literal prose error, fabricated stopped-control return and missing active48Bframe/fourpostcalltable words; source routes/numeric hashes/divide endpoints agree. No actual table construction/provider binding. Original implicit unchanged memory not promoted to callee contract; corrective387/391 required.

- E-XE164-391 HYPOTHESE: Corrective237word model preserves1096 baseline histories, adds finite scratch-clobber probe (1350 total rows), explicitly records25 protected spans across5 opaque events:48B activeframe plus4 source-derived postcall words each. Mismatch summary NOT_RETURNED; literal20c4/value12120 corrected. Selected opaque return stipulatesr0=0/r6/r11/SP/normalcontrol and protectedbytes. Probe clobbers one unusedword,selectedscratchGP/LR/NZCV; finite witness not universal ABI. Scratcheffect pc/address columns overloaded; dedicated probe TSV supplies actual labels.

- E-XE164-392 VERIFIZIERT: Independent237rawword/1096baseline/25span audit checks actual reads45ea0/45e60/45e6c/45e70 and both stackpopregions. NOT_RETURNED control and finite clobber route/T/frame restoration consistent. Independent ledger/source audit, no replay-builder import and no actual strcmp implementation/ABI/tableconstruction claim. Scratch serialized field-label ambiguity disclosed.

- E-XE164-393 HYPOTHESE: 45query+3PLT+4getter words/4pools form four selected cases. Optional source order L0/L4/Lc/L8 then2 shifted sourcewords; output0=L4 alias changes laterread. Returnr0 remainsgetterL=4014c under fixtureentry1→mapped1. Fixture mapping is synthetic, distinct from raw initialrow1→mapped2 later397. Original validator checks storedtraces, not fresh regeneration;392 transition review uses recorded reads;395/396 close selected memory/regeneration gap.

- E-XE164-394 VERIFIZIERT: Independent ELF/PT_LOAD/raw52words/4pools and recorded transition audit checks GPR/NZCV/conditions/branches/eventwidths/actualstack/outputorder/alias/finalr0=L; no selected source defect. Uses recorded memory-read values as inputs, does not independently rebuild fixturememory. No fresh serialization regeneration by original388validator; additional395/396 required for that stronger scope.

- E-XE164-395 VERIFIZIERT: Fresh pure388 run_case recreates all four resultobjects/186rows/86reads/48stores and fullfinalmaps without writer. Separate initialized byte-map oracle derives everyread from initialbytes+priorstores and checks finalmap equality; upstreaminventoryunchanged. Fresh CPU uses same388 model, not independent decoder. Root byteoracle does not enforce store permissions; writable output/frame ranges are explicit fixtures, independently bounded by396. Entry/mappedindex1 only.

- E-XE164-396 VERIFIZIERT: Independent fixture byte-map audit reproduces86reads/48stores, exactstackcycle, actual337dc=1→L4014c mapping and alias worda0a0a001 read-after-write. All48stores lie within stipulated writableoutput orsavedframe ranges. No runtime mapping/permission claim; output writability stipulated, not proved for processmemory. Complements392 rawtransitionreview and395 same-model regeneration.

- E-XE164-397 VERIFIZIERT: 130 exact words/5pools: Init62,Desc18,Count14,12PLTs36. G4442c distinctsnapshotB44448; Desc freshS1 afteropaqueacquire calls memcpy(B,S1+18,36b0); CountreadsS1+36c8,mirrorsG16/reloadsafterunlock. Initnumeric370c/1 publishesreturnedword beforelaterlockcalls. S0/S1 not assumedidentical, freshS1 not recheckednonnull. Call vectors not memcpy/lock/allocator semantics. Copy14000Bendswherecountstarts, not complete ABI/layout. Root source checks run with PYTHONDONTWRITEBYTECODE=1.

- E-XE164-398 HYPOTHESE: 16 actual-entry synthetic GetCnf routes2bias×mode1/2×config0/20×optionalpointer, currentRAILG0 and localPLTbindings. Four getters return0 locally beforefurtheropaque calls; index2 lanezeros C24/C2c vsC20/C28, oppositecanaries preserved; selected sourceepilogue returns0/restoresSP. Trace snapshots are postinstruction states with memory/control effects. ActualG0/runtime/API/emptydevice not established. Separate397 Update guard can rejectnull descriptor beforethiscallee whenstatepreserved; no wholeUpdate-success claim. Corrects386 ownfalseproseerratum.

- E-XE164-399 VERIFIZIERT: Independent1102source/pool values viaPT_LOAD, fixturemem reconstruction,16routes/GOT/conditions/rawbranches/loadstore/stack/output/bias audit agree. Verifies389 correction:384prose already7998,386falseerratumwithdrawn. Does not implement second complete ALU engine; arithmetic generation supported by389stepper, separate independent memory/predicate oracle. All runtime/binding/API implications open.

- E-XE164-400 VERIFIZIERT: 224sourcewords/3pools: Init165/Open23/12PLTs. G443f4 publishcurrentallocationreturn afterrequest(1,74hex), beforelocks. OpenunsignedI<=3 uses freshS1 slots5c+8I/60+8I. I3 spanS74..S7c lies beyond numericalrequest[S,S74); concrete backendcallsetsI0. No actual memoryfault/bug/allocator-size claim; intervaljoin conditional sameS. Opengates needr5=G/r4=I/currentG/frame afteracquire andr4result/frame afterunlock. Default validator can write Pythoncache; Root ran only envPYTHONDONTWRITEBYTECODE=1; new397fixes own default pattern.

- E-XE164-401 VERIFIZIERT: Independent rawPT_LOAD224words/3pools/12relocs confirms Initvector/publication, unsignedOpen gate/S0→freshS1, I3numericinterval andbackendI0. EnumeratescurrentGP/frame/memory premises. Discovers390ordinaryPythonimportcreates__pycache__, so unqualifieddefaultreadonlyclaimfalse; generatedcache removed, frozenmanifestrestored. r5/r4/currentstate preservation conditional, not ABI. No actualbugclaim.

- E-XE164-402 VERIFIZIERT: 283 words/8 pools bind Update210, Set15, Get14, Count2 and14 PLTs. Three initial12B rows map entries0/1/2 to1/2/3; Set changes only row+8. Update eight nonnull gates precede calls. Raw VST Rm13 advances16 then Rm15 stores8, yielding24B span. Current opaque state is conditional; preserved null RAIL descriptor rejects before main Update loop, so earlier389 local GetCnf success is not whole Update success. No runtime mapping/ABI.

- E-XE164-403 VERIFIZIERT: Independent raw283word/PT_LOAD audit confirms three initial rows, unsigned setters/getters, eight Update null gates and VST writeback24B span. Numeric source relationships only; opaque call effects/current GP and runtime ownership remain open.

- E-XE164-404 HYPOTHESE: 86words/6pools;19 actual-entry fixtures430steps241events exercise Set/Get/Count and all-null Query against actual three initial mapping rows, two stages before/after row+8 setter. Synthetic memory/PLT bindings; non-S SUB preserves seeded NZCV. Selected source model does not establish process memory or runtime calls.

- E-XE164-405 VERIFIZIERT: Independent source/predicate/PC/event/frame review agrees with19 routes and setter-only word8 changes while initial entry mapping remains unchanged. Not a second complete independent ALU engine; fixtures and runtime binding remain conditional.

- E-XE164-406 HYPOTHESE: 23raw words/15 full Open fixtures cover indices0..3, rejection4/ffffffff, fresh state after acquire, and index3 numeric request-boundary read before stores; explicit GP/frame/opaque events. Index3 unmapped fixture is a modeled boundary, not actual allocation fault. S0/S1 may differ; negative current r4/r5/result clobber controls retain conditional premises.

- E-XE164-407 VERIFIZIERT: Independent initialized-memory/raw-control/event audit confirms15 Open routes, state reload after acquire and index3 boundary. No full independent ALU engine, allocator extent, real lock semantics or runtime identity claim.

- E-XE164-408 VERIFIZIERT: 274words/14pools: producer247, cleanup15, four PLTs. Kind1 builds one-hot masks; Kind2/5 position V and Kind4 group D/A fields are raw source relationships. Cleanup clears outer+8 before free-named call. Opaque allocation/current-register premises explicit. Group capacity48 has no local bound check; initial count not proved zero. No reachability of earlier N0 fixture or actual bug/ownership claim.

- E-XE164-409 VERIFIZIERT: Independent raw274word/arithmetic/store audit confirms producer masks, numeric request sizes, group append positions and cleanup outer-slot order. Not full CPU replay; allocation effects, initial group count and whole-object ownership remain open.

- E-XE164-410 HYPOTHESE: 321words/14pools;64 full producer fixtures enumerate16 n values/K0,7/two biases, and16 separate read/write helper entries consume the actual generated records. Existing eight-slot array and synthetic source memory stipulated. Separate helper invocation is not actual native caller chain; selected corner helper coverage only.

- E-XE164-411 VERIFIZIERT: Independent raw source, masks, event/formula/stack/gate audit agrees with64 producer and16 helper histories. No second full independent CPU reexecution or actual allocator/ABI/runtime claim.

- E-XE164-412 VERIFIZIERT: 181words/7pools bind ReadWrite request40184b01 with24B sixword stack vector, Command401c4b02 with28B sevenword vector, and Open40084b03 eightbyte configuration10010000002d3101. Requests/bytes are numeric call positions, not kernel UAPI. Nonnegative ioctl outcome requires current r4=0; Open malloc stores require current r6/r5. Device string is read only, no device operation.

- E-XE164-413 VERIFIZIERT: Independent181word/7pool/8relocation audit confirms vector widths/positions, status-byte initialization, signed return branches and Open configuration bytes. Current GP/frame conditions remain necessary; no actual ioctl provider, ABI, errno implementation or device execution.

- E-XE164-414 VERIFIZIERT: 562words/42pools bind SCPU G34018, Open/Exchange/Command/Init source and three SPI PLTs. Command568B frame builds requests/reply and tags0..10 receive lengths, passing five-position numeric SPI_Command vector. Init and Exchange not fully replayed; helper92c8 and clock/config/boot/reset/system effects unexpanded. SPI-only substitution is not a complete Init boundary. Artifact command strings never executed.

- E-XE164-415 VERIFIZIERT: Independent PT_LOAD562words/42pools, G34018 equations,11 stubs, frame and three SPI GOT targets confirm bounded caller vectors. No full CPU replay, actual transport binding, response semantics or runtime/hardware effect.

- E-XE164-416 HYPOTHESE: 324words/14pools;48 full producer cases4008steps plus960 helpersteps generate malloc16 Kind2/5 records across banks/flags/masks/two biases and consume generated records in separate helper entries. Allocator normal return, preserved current GP/frame/input bytes and output memory are explicit fixtures, not ABI. Helper entries are separate invocations. Source allocation validity unknown.

- E-XE164-417 VERIFIZIERT: Independent raw/predicate/recorded-ledger/formula audit supports selected Kind2/5 records and helper outcomes. REJECT only-SP+c postcall-read claim: numeric PC>=return filtering misses backward branches c284/c224/c268. Original no-op route assertion adds no evidence. Frozen review retained;416 supplies event-order correction. No second full CPU.

- E-XE164-418 VERIFIZIERT: Event-order audit finds12 postopaque reads per48case: SP+c, source+d/source+12 and nine saved frame words. Actual values derived from fixture initial bytes and prior stack writes. Outer0/4/c preservation is output postcondition rather than subsequent source read.407 already explicitly supplies required input/frame premises; correction concerns413 review, no actual allocator ABI.

- E-XE164-419 HYPOTHESE: 90raw words/15 full ReadWrite/Command fixtures cover null/negative handles, positive ioctl outcomes, errno branches/logger mutation and current-r4 clobber counterexample; exact24/28B buffers. Frozen412 event contract omits saved-frame preservation and explicit logger errno-memory effects; results require stronger implicit memory premises. Fixture.handle incorrectly derives final r0 in successes;419 corrects label and contracts without changing histories.

- E-XE164-420 VERIFIZIERT: Independent raw/predicate/critical-ALU/PC/args/results review agrees with15 source histories and identifies missing saved-frame and errno-memory opaque premises. Original modeled memory implicitly survives calls; no actual callee preservation. Corrective419 pending independent420 before promoting explicit boundary completeness.

- E-XE164-421 VERIFIZIERT: 122raw words/4pools/13opcode halfwords bind four callfree codec bodies. Noargs zeroHalf@O2 precedes opcodebytes; OneArg stores then reads currentArg halfword. Reply status storeE44410+Tag precedes gate, truncates count8bit, uses fullExpected, and raw NEON Rm13 load/store eachadvance16. Reply lacks local Tag/R guards; getter guard does not apply to decoder. Alias order and unsigned vector gate are numeric source behavior, not public protocol/API/actual buffers. Source only, fullmodels separate417.

- E-XE164-422 VERIFIZIERT: Independent122word/4pool/13halfword/PT_LOAD review confirms encoder order and Arg=O2 alias, status-before-gate, unsigned copy predicate and both NEON Rm13 writebacks/counts. No public API/tag names, complete protocol, runtime binding, pointer validity or hardware semantics.

- E-XE164-423 HYPOTHESE: 15 unchanged SPI histories and26explicit opaque events now bind actual pushed SP20/SP24 words, normalreturn/currentSP, currentGP and errno pointer/readableword effects including logger mutation. Entry_handle now reflects inputr0. 420 finds current_register_reads omits r0 consumed by actual CMP r0,r4 afterioctl; return value exists in traces, outcomes unchanged. Canonical consumed set requires BOTH currentr0/currentr4. These are synthetic per-event premises, not actual callee effects/ABI.

- E-XE164-424 VERIFIZIERT: Independent source/initialmem/event-order audit confirms15 matching baseline histories,26opaque contracts, savedframe POP values, logger errno writes and inputhandle correction; pins CMP e1500004 consumingr0 AND r4 atbothioctlreturn sites. Rejects419 only-r4 consumed-register completeness statement; traces/results agree. Actual errno/ioctl/ABI/device effects remain open; no new CPU/nativeexecution.

- E-XE164-425 HYPOTHESE: 113raw bodywords/4pools/13opcode halfwords;63 full selected traces plus two separate shared-E entries cover alltags, rejects, Arg=Out2 alias, Reply status/count gating, N1/7/8/9/16/255, scalaroverlap and inplaceNEON, rawRm13 writebacks16. Reject frozen report noargs temporal description: actualzeroHalfO2 precedes opcodebytes. Three source-pin paths omit xe164-analysis;421 binds correct existing files/hashes. Modelresults/validator usecorrectsource, broad63routes same-modelreplay; nofullindependentCPU.

- E-XE164-426 VERIFIZIERT: Independent raw eac4STRHzero beforeead0LDRH/ead8/eadcSTRB and selectedtrace checks confirm trueorder. Three malformed417paths corrected by bound actualfiles. N25531vectorpairs+7scalarpairs and two aliases spotchecked. No complete second CPU engine. Frozen417report/orderandpathledger retained as errata; finalbyteoutcomes unchanged. Noactualprotocol/ABI/runtimeclaim.

- E-XE164-427 VERIFIZIERT: Six-stage private synthesis separates manager/provider/ffi/SSC/SCPU/kernel evidence and open contracts. NumericSPIvectors24/28/8B do not establish kernelUAPI or completeInitreplacement; no newarchitecture/APIdecision. Only12 enumerated immutableinputs pinned directly; further cited WPs contextual, not wholefrozencitationchain (424). Statement helper92c8unexpanded historical to423;425 laterexpandsbody whileSPI_Init/boot/effectsopen. NoendtoendKind4appendlink.

- E-XE164-428 VERIFIZIERT: Independent12input identity/sixstage claim audit confirms preserved lifecycle/runtime/kernellimits and conditionalobjectidentity; identifies unpinned contextualcitationIDs. NoCPUreplay or actual architecture/transport/runtimecontract.422report pinned asinterimcontextonly, nofullproducerclaim.423fullcitationchain not frozen byits12pins.

- E-XE164-429 HYPOTHESE: Six source-block compositions1/2/3appends×2biases start explicit existingD/A,N0 and halfcapacity48; storecurrentr8@A+2N thenincrementhalfN. Helper firstread arithmetic becomesA/A2/A4 versusseparateN0→A-2. NOTfullCPU. ActualbranchJ>11999reachesc284/appendthen c2c0→c504logger→c224; validJfollowsc3b4/c3f4. Noactualappend→validKind4consumerlink. GroupallocationrequirescurrentS+e afteropaque logger; fixturecapacitynotcheckedsourcebound.

- E-XE164-430 VERIFIZIERT: Independent247raw producerwords andexactbranchdecode confirmout-of-rangeappend/loggerlane; recomputes6fixtures andselector4pre-readorderA+2N-2. Noestablishedobjectidentity/nativecallchain;D0=48ishalfwordfixture, notfullword norenforcedcapacity. Opaquelogger/currentmemorypremisesexplicit.

- E-XE164-431 VERIFIZIERT: 97raw words/7pools/17BL/11PLT completehelper92c8..944b. FourG34018eq,32Bframe, selectedlocal0/3/6outcomes andsixSCPUCommandnumericpositions; true8B d16literal9450=0100000000000000. Opaque calls/currentGP/frame/state required; nofullCPU/ABI/effects. Historical423helper-contentgapclosed. SPI_Initbodylater428/429closed, wholeInit/boot/resetstillopen. Padding944cnotvectorliteral.

- E-XE164-432 VERIFIZIERT: IndependentPT_LOAD97words/7literals/17BL/11PLT/GOT/reloclabels,5PCeq andD16bytesconfirmselectedbranches/localreturnpaths. Calllabelsnotcontracts; currentstateandGPconditional. Thisclosesonebody'ssourcecontent, notactualinitialization.

- E-XE164-433 VERIFIZIERT: ExactSPI_Init DynsymELFa960size8/raw e3a00000,e12fff1e implementsMOVr0,0(noS),BXLR; noexplicitmemory/stack/BL/otherGPRwrites. ValidcurrentLR/interworkingneeded. ActualGOT33250runtimebindingunknown; onlywhenboundlocalbodycan425SPI_Initopaqueeffectsberefined. Wholeboot/init/resetnotclosed.

- E-XE164-434 VERIFIZIERT: IndependentDynsymFUNC8B/uniquePT_LOAD/rawA32field/REAidentity/inventoryaudit confirmsMOV0withoutflagwrite andBXLR, noexplicitmemorycall. CurrentLRtarget/statepremise andruntimeGOTbindingremainopen; noactualnative/deviceexecution.

- E-XE164-435 VERIFIZIERT: 262raw words/28pools/39BL identify16PLTtargets+2local9618/9a78 in complete1048B Bootbody. G40028 distinctSCPU34018. Artifact/dev/ttyKbus numericopen0x102→isatty/termios/write/select/read/close chain and selectedD5/DA bytegates are present;216Bframe/configthreshold10000000. Source/callvectors only; no actual TTY opened. CurrentGP/frame/errno/bytevalues acrossopaque calls conditional. D8rawwords0/4000 notactualtimecontract; 430 itself does not expand9618/9a78;9a78 source already retained370/379 and selectedcalls384/386.432 newly scopes9618;433 joins retainedorchestrator/currentboot.430/431 is fresh narrower source/call-vector review, not new discovery of allbootbytes. SPI3callsalone do not cover this observedchain.

- E-XE164-436 VERIFIZIERT: Independent rawPT_LOAD262word/28literal/39BL/16PLT+2local audit confirmsG40028, path/configbytes, numericguards and selectedhandshakepredicates. VLDRa618+8+268=a888 givesraw0/4000words. NotfullCPU/actualserial/protocol/firmwareoperation. Two localhelpers/currentopaqueeffects/loadedruntime stillopen. NoWP430orolderpackagechanges.

- E-XE164-437 VERIFIZIERT: Four exactFW31 readonlydebugfs inode dumps bind modules.builtin/modinfo/devname/alias under6.6.94-rt56-w05.08.02. builtin lists drivers/spi/spi-kbus.ko and matching spi_kbus path/description/license/major parameter fields. Metadata candidate only; .ko listedbuilt-in isnotseparateloadedmoduleproof. Noactualkernelstart/device/major/UAPI/ioctl/TTYbinding ordriverimplementationcontract. Author/addressstringhitsnotinterfaces; /boot/linuxinventoryonlyin434, later437extracts.

- E-XE164-438 VERIFIZIERT: Independent fullimage/inventoryhashes+temporarypartition/debugfs stat/dump reproduceall4files byte-for-byte,10boundedhitsandspi_kbusfields; packageinventoriesunchanged. devnameonlycuse/uinputandnoaliasmatcharefinitefileabsence, notglobalbindingabsence. Artifactsnotactivekernel; nojoin408ioctl/430TTYtospi_kbus. Header/licensefieldnotrightstobroaderredistribution.

- E-XE164-439 VERIFIZIERT: Boota75c calls retained370orchestrator9a78 (595words/noncontiguous172Bgapexcluded) withcurrentSP20/[SP14], pre-store1@G40028. Orchestratorsavesargsandcallsreader97f0with0/SP38/SP3c; selectedreaderretffffffff→localhelperret0→callerconditionalstore2. Requires normalnestedreturns/currentframes/r4andnowritetoGfororiginal1→2stateclaim. Noactualreaderselection/payloadtransfer/protocolsuccess. Reuses370source, notnew638wordcontiguousacquisition; staticfile/compositeidentitiesnotruntime.

- E-XE164-440 VERIFIZIERT: Independent rawsource joins430→370→reader, pinscall9ae0/test9ae4/-1branch9ae8→a208local0 andcallerNEstore2; staticpayloadcandidatebytesagree. OriginalG40028/prior1needintactsavedr4/frame/nointerveningwrite. Non-minus1readerroutesoutsideboundedclaim; noactualserial/nativeexecution.

- E-XE164-441 VERIFIZIERT: ExactFW31inode50/boot/linux8213856B SHA f6e03d6452e4648cd86f58ff5c869af0ebdcc6e8f3123458c73d6e81ccfede65 extractedreadonly. uImage64B CRCS75c25a9e/5f20e326and8213792payloadcheck; innerARMzImage magic016f2818/endlengthcheck. Outercompression0notuncompressedkernelproof; LZOsignatures467cstaticliteral/488ccandidateclassificationonly, no validstream/decompression yet. Noactualkernelstart/driverUAPI. Directsourcebytebasis, notruntime.

- E-XE164-442 VERIFIZIERT: Independent image/inventoryhashes+freshreadonlydebugfsinode50dump byteequal; alluImagefields/CRCs,zImagemagiclengthandLZOoffsetsrecomputed,inventoryunchanged. Hostfile'slzopclassificationat488cisheuristiccandidate, notstreamvalidity/decompression. Noactivekernel/driverbinding/deviceeffect.

- E-XE164-443 VERIFIZIERT: 108raw selectedcodewords9618..97c4/10literalwords and18BL bindserialconfigslice. Callerinputr0/r1savedr8/r5;120Blocalzerofootprint with4Boverlaps52..55/112..115; fourconfigurationcallsplusmemcmp=5primarycalls. No matchingnewREAextent; boundedrawslice notproviderfullbodyrecord. PUSHr4-r8/LR=6wordstotal+120local=144Bframe. Currentr5/r6afteropaque tcgetattr neededforcfsetspeed(SP,14); laterFD/buffer/returnstatesconditional. MatrixC3fourprimarycountincorrect (5). NoABI/actualtermioslayout/baudunit/deviceeffect.

- E-XE164-444 VERIFIZIERT: Independent rawslice/BL/PT_LOAD/caller review confirms120Bzeroingwithtwo4Boverlaps, signed-negativeandmemcmpreturnlanes. Specifies6savedwords andfiveprimarysites; currentr5/r6/r7/r8premisesexplicit. Noactualtcgetattr/cfsetspeedeffects/realbaudmeaning/runtimecall. No providerextentconfirmation. Frozen432ambiguousprologueandmatrixwordingqualifiedwithoutmutation.
