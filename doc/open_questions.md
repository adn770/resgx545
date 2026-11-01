<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# Open questions

*Generated from `questions/` by `tools/records/questions.py`; do not edit.*

## bif

- `Q076` (phase 11): which page directory do a render's TA and 3D requestors translate through, and do read-only aliases of the EDM's buffers suffice there as they do for the transfer path? (E021, E023, E151)

## dpm

- `Q038` (phase 10): does a background object with a colour reload, or a host that renders the scene's partial renders into a stored target, give the whole image of an overflowing scene, and what does the final render read back of a partial render's depth? (E202, E204, E160, E310, E311, E312)
- `Q045` (phase 11): what sets the fields of register 0x0740 that the TA kick turns into DPM store and load tasks, and does a load task read back the macrotile lists a partial render stores in the RT data's state page? (E158, E256, E310, E312)
- `Q067` (phase 11): how does the EDM's page-table builder (PB_FLAGS.INIT_PAGE_TABLE) scale its store offset, and does the settle routine wait for the other pipe to go idle? (E153, E200, E201, E309)
- `Q081` (phase 11): what does CR_DPM_REG_074C bit 8 make the DPM read or write near offset 0x6010 of the context's TA-data space, and what fixes that place? (E203, E206, E313)

## edm

- `Q002` (phase 3): is the 399.0 MHz reference that times the EDM tick and TIMER the clock the USSE runs from? (E009, E084, E124)
- `Q005` (phase 6): should the kernel ask the firmware for its identity on every boot, so DEV_QUERY reports it without the debug option? (E017, E022)
- `Q006` (phase 6): can a render client's VM do without a writable mapping of the device-wide TA/3D control block? (E023)
- `Q033` (phase 10): does the event word PDS #13 hands the EDM as pa1 carry CR_EVENT_STATUS bits in reverse order, and which events set its bits 8 and 19, that no handler acknowledges? (E155, E146, E154)
- `Q034` (phase 10): does the EDM start a TA command whose destination or source sync is incomplete when its context is the only one in the TA queue? (E161, E154)

## isp

- `Q030` (phase 10): where do a multisampled render's tiles past the first land in the target, and what do the TE anti-aliasing bits change? (E210, E211, E219, E220, E281)
- `Q031` (phase 10): why does ISP word 0 bit 28 hang a multisampled render, when single-sampled it widens coverage to the union of eight samples? (E214, E215, E278)
- `Q032` (phase 10): what does pcoeff hand the ISP in the punch-through pass, when the kept pixels' depth is the same without it and moves between runs only when it runs without the iteration it reads? (E217)
- `Q066` (phase 11): what do the three background-object words the 3D kick writes mean to the ISP, and what are the other words of a render's background object? (E069, E162, E209, E216)
- `Q071` (phase 11): how does the ISP use the ZLS control word's bits in a render with depth or stencil buffers? (E057, E169, E216, E228, E284)
- `Q072` (phase 11): what does bit 1 of CR_ISP_REG_04DC do to a punch-through pass, when it hangs every one tried and changes no opaque or translucent pass? (E068, E073, E213, E222, E290)
- `Q073` (phase 11): what does o0 hold at the start of an opaque pass's pixel shader? (E077, E283)

## mte

- `Q039` (phase 10): where is a user clip plane's state held between jobs, what resets it, and when do the vertex's distance dwords decide a plane? (E198, E280)
- `Q069` (phase 11): what do OUTSEL bit 13 and the state block's presence bits 16-31 select? (E061, E066, E192, E193, E198, E286, E287)

## pbe

- `Q012` (phase 6): what float formats are pack modes 22 and 34, given that both read o0 as an IEEE single (sign, NaN and exponent) and store it at some of the triangle's dwords while the rest change with the job before? (E032, E270)
- `Q040` (phase 11): what do EMIT2 bits 15:8 count, given that 4v pixels of each tile are stored for an even v up to 0x80, odd values hang and values above 0x80 change the image, what do EMIT2 bits 6:0 and 31 select, and is bit 29 a rotation by 180 degrees or an anti-transpose? (E046, E265, E266, E267)
- `Q044` (phase 11): what do bits 11:0 of CR_REG_0400 (0x80 as built) do, when no value of them changes a stored pixel in pack modes 0 to 3, and does bit 25 act on the other pack modes? (E029, E028, E031, E251, E268)
- `Q046` (phase 11): do SIDEBAND bits 8:6 select the channel only in pack mode 8, or in the other one-channel modes too (24, 25 and those that store G8B8), and what do sideband bits 11 and 12 do? (E030, E031, E210, E269)
- `Q074` (phase 11): why does a second end-of-tile emit in a tile leave the next job's image wrong, and does SIDEBAND bit 9 mark an emit that counts against a PBE tile? (E030, E130, E239, E240)

## pds

- `Q013` (phase 6): what does bit 18 of the copy's pixel-event data word 2 do, when it leaves the copy unchanged and changes a few pixels of the fill and the triangle? (E043, E046)
- `Q019` (phase 7): what does the secondary attribute size (bits 24:18 of dword 1 of the background object) limit, given that all sixteen douta words reach sa0 to sa15 with 0, 1 and 4 rows, or does the task take its size from elsewhere? (E125)
- `Q020` (phase 7): what does a douta in the triangle's primary pixel program do, when its markers never reach the USE task and the readback is the memory table's inputs for markers A in both runs, and other values for markers B in the first? (E125)
- `Q021` (phase 7): with 4 components (DOUTI0 bits 23:22 = 3) where does the texel land, given pa3 reads 1.0 on most pixels? (E132)
- `Q022` (phase 7): why do about 30 percent of the pixels keep the previous case's value in the vertex-colour iteration cases, in both runs? (E133)
- `Q023` (phase 7): what do PDS_SIZE bits 17:16 do, given that they move where the output registers o1 to o3 land? (E139, E081)
- `Q024` (phase 7): does CR_PDS_REG_0A78 change timing, when two of its values were slower in one timing run? (E141, E045)
- `Q025` (phase 7): what does the SB field of CR_BIF_FAULT encode in the PDS faults, and why did a store of one dword fault in the follow-up run only, and a store of two dwords then eight in the first run only? (E143, E144, E145)
- `Q026` (phase 7): why do the per-tile stores of the grid pixel-event probes leave empty slots and mixed copies, different ones per run? (E130)
- `Q027` (phase 7): what does the no-wait iteration deliver to pa0: stale values in the first run, and the pixel's own clip x on 60 to 115 pixels per case in the follow-up run? (E131, E048)
- `Q057` (phase 11): what do doutc, douts, slc, mr and ir0 do as move destinations, and movsa on ports other than doutd, and does an enabled small count in tim hang the job, and why? (E127, E128, E264)
- `Q058` (phase 11): what sets the input flags if0 and if1 outside a vertex program, since neither tests true in any primary pixel or pixel-event task tried? (E128, E130, E262, E263)
- `Q059` (phase 11): why do PDS stores totalling 2, 3 or 4 dwords fault the job, and why does an rwfence after a store, or after a faulted job, touch page 0? (E143, E144, E145)
- `Q060` (phase 11): what do mr01, mr23, ir1 and the .h specials read in the vertex-side programs? (E128, E130, E262, E263)
- `Q061` (phase 11): does a DOUTU word's EXE field stop at bit 19, leaving CBASE in bits 3:0, or do the 18 program-counter bits reach bit 21? (E004)
- `Q062` (phase 11): what makes the PDS fetch pc read one or two below the reading instruction's index plus 3, at instructions 26-27 back to back (the end of a 64-dword block) in most runs? (E128, E142, E143, E260, E261)
- `Q063` (phase 11): what does bit 9 of a mov16 or mov32 special source select on the rest of the SGX family, when on SGX545 it only makes mov16 read 0? (E128)
- `Q077` (phase 11): what does bit 15 of a mov128 word select, which makes it write the data's row 4 ds0 pair to both halves of its destination whatever its source row (and with swap at row 2)? (E259, E261)

## platform

- `Q001` (phase 3): what do 0x0810, 0x0814 and 0x0818, set once by the init script to 0x1, 0xffff and 0x7ff, control? (E006, E010, E122)
- `Q075` (phase 11): what does each HWPerf counter the firmware records (0x0044-0x0064, 0x0e84-0x0e90 and 0x0eb4-0x0ec0) count, and how does the group in CR_HWPERF_CTRL select them? (E149, E150, E152)

## render

- `Q014` (phase 6): why does a background object whose first PDS word has a high bit wrong render part or all of the first 32x16 tile before the job faults? (E029, E301)
- `Q029` (phase 9): what does the EDM's render context cleanup wait for, and which cleanup releases the parameter buffer in the TA/3D control block? (E148, E023, E156, E164, E289, E303, E304)
- `Q041` (phase 11): what does a later job do with the DPM slot word that FRAG_FLAGS.BIT2 or NO_DEALLOCATE leaves set after a render, when no image changes with either bit? (E164, E158, E051, E052, E053, E303)
- `Q043` (phase 11): what does bit 0 of CR_REG_0148, which the firmware loads for every render, partial render and transfer, change, when no bit of the word changes a triangle, five copies, a fill or a copy? (E056, E163, E160, E015, E028, E252, E302)
- `Q049` (phase 11): does the firmware or the hardware ever read dword 7 (offset 0x01c) of the render context, which the EDM dataflow reaches on no path? (E013, E021, E156, E165)
- `Q065` (phase 11): why does render flag bit 0 hang a kernel-built triangle job when the firmware completes a NO_RENDER render without rendering, and does one command with FIRST_KICK and LAST_KICK act as two? (E050, E156, E164, E165, E184, E303, E304)

## ta

- `Q035` (phase 10): does the tiling engine read CR_TE_MTILE1 (0x0208) at all, and does any set of tiling words other than the macrotile rule's also draw a target exactly? (E174, E175, E247, E257)
- `Q064` (phase 11): what does the region header mark that CR_TE_PSG bit 21 makes the TA write mean to the 3D, and is bit 1 of CR_DPM_STATE_CONTEXT_ID the 3D's DPM slot as bit 2 is the TA's? (E158, E172, E305)
- `Q068` (phase 11): do the twelve TA register words that are zero in our jobs save and resume the state of an interrupted TA? (E054, E056, E182, E183, E245)
- `Q070` (phase 11): what do the TA object's format word bits 15:8 and above and its set masks select beyond the settings seen, and does the fitted region test hold for lines and points? (E176, E177, E180, E181, E185, E306, E307, E308)

## texture

- `Q007` (phase 6): where do the copy's source, its destination and the page before the source lie, given that T2 bits 12, 13 and 14 read those buffers rather than the source's continuation? (E036, E041, E273)
- `Q008` (phase 6): how is the luma compared at the luma key's low cut (bits 7:0 of the word that loads 0x0868), where 8 pixels in 2 of 274 copies, 4/1024 above the cut, fall the other way, and what do bits 31:16 of the alpha word and the offset's precision do? (E039, E275)
- `Q009` (phase 6): what do T0's maximum level 15 and the LOD bias (bits 26:21) do beyond a five-level chain read with nearest filtering at whole LODs? (E041, E276)
- `Q010` (phase 6): what clears the colour-space words between jobs, given that a copy that does not load set 0 converts with the last loaded words, and the first job of a session after hung jobs converts with zeros? (E037, E039, E046, E271)
- `Q078` (phase 11): what do T3 bits 10, 14, 18-19 and 27-28 and T0 bit 27 select, given a copy that reads one texel, a sheared read, coordinates scaled by 2 and 4, smaller images after the source, and values of no texel? (E274)

## transfer

- `Q003` (phase 4): why does a transfer render that faults on a read-only page raise no BIF-fault interrupt the host sees, and how does a host recover the EDM in place afterwards? (E021)
- `Q004` (phase 4): what do a transfer context's flag bits 1 and 4 and a priority other than 0 do on the hardware? (E015)
- `Q011` (phase 6): why does a copy whose background-object tag (transfer word 0) is wrong read one texel, the source's last, for every pixel, and what stores the samples of CR_ISP_MSAA mode 2 in a copy? (E028, E272)
- `Q028` (phase 9): what does a faulting job leave wedged when the kernel does not recover, and which reset steps does the recovery need? (E024)

## usse

- `Q016` (phase 6): which part of the smoa, smbo and smr sequences that fault the job makes it fault: the moest selectors, the changed state or the mirror mode? (E087)
- `Q017` (phase 6): why does g19 read 0x1a as a store's source but 0 through a mov and as the pixel? (E085, E086)
- `Q018` (phase 6): where does the 0xff00ff00 colour left in the opaque pass and the punch-through phase scene come from, and why does its pixel count vary from run to run? (E077, E082)
- `Q048` (phase 11): do the MADD0 and MADD1 clock gates follow the USSE pipes' floating-point arithmetic, or their cache and texture traffic? (E006, E008, E011)
- `Q050` (phase 11): what do the visibility group's instructions do, and how do smp's mipmaps and LOD values, the border address modes, the compressed and YUV formats and firh's edge modes past the line and fixed banks 1 and 2 behave? (E083, E091, E123, E147, E292, E293, E294, E298)
- `Q051` (phase 11): what state do smoa, smbo, smr, imo and setfc set in the MOE, and what does moest return, beyond the smlsi increments the probes pinned? (E087, E097, E105, E109, E294, E296)
- `Q052` (phase 11): what do .skipinv, .syncs, .nosched and the other scheduling flags change, and how many instructions after a write can a dependent instruction read the result, with or without an interlock? (E100, E104, E111, E113, E124)
- `Q053` (phase 11): what do the global registers g18 to g20 and g39 to g43 hold in a triangle's pixel task, a vertex task and the end-of-tile task? (E085, E086)
- `Q054` (phase 11): what do #incp, .cut and .tasks/.taske do on the emits, and what do sideband bits 11 and 12 select, beyond the pack mode, bits 8:6, 9, 10 and 13 that the end-of-tile emit reads? (E030, E102, E106, E239, E269)
- `Q055` (phase 11): what do idf's modes other than bif, lock and release, setm and the cache-control operands do? (E088, E098, E099, E103, E107, E110, E117)
- `Q056` (phase 11): where does a write to destination bank 6 with value 0 (printed i.) land? (E091, E147)
- `Q079` (phase 11): what does idiv's enc[47], a bit outside every field of the form, select? (E295)
- `Q080` (phase 11): what do the USSE words no form decodes (classes 2, 22 and 26) do: which stop the stores after them, and which write registers? (E297)

## vdm

- `Q015` (phase 6): what makes VDM state word 1 with bits 11:9 = 7 hang some runs of a job and complete others? (E060, E185, E299, E300)
- `Q036` (phase 10): what do the high half of the DPM STATUS2 registers (0x0710, 0x071c) and the DPM's other status words (0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS' high half) hold, now that STATUS1 and STATUS2's low half are the free list's tail, head and page before the tail? (E160, E184, E256, E309, E310, E312)
- `Q037` (phase 10): does a hung job's saved render memory show how far the TA got, when the control hung in its pixel task leaves its object in one run and none in the next? (E186)
- `Q042` (phase 11): what do bits 27:24 of the index list's first trailing word (VDM_INDEX2) do, when its low bits move the list's first index and 0x0f000000 drops two of five triangles? (E188, E300, E307, E308)
- `Q047` (phase 11): what do VDM_STATE1 bit 8, bits 11:9 and bits 15:13 select for a state task, when on the one-triangle job bit 8 changes nothing, bits 11:9 at 0 stop the triangle before tiling and bits 15:13 at 0, 5 or 6 hang it? (E060, E185, E186, E187, E299)
