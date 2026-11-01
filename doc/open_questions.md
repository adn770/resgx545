<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# Open questions

*Generated from `questions/` by `tools/records/questions.py`; do not edit.*

128 open: 114 hw (high 13, medium 60, low 41, unrated 0), 10 fw, 4 kernel.

## Work queue: hardware

### bif

- `Q076` (phase 11, hw, high): which pages does each bus-interface requestor of a render (the TA, the 3D, the EDM's PB load) need in the directory of the list it translates through (TA3DCtl writable; each of the buffers 6, 7, 8, 10 and 11 alone is not needed: E457), which of the 16 directory lists does each use, and what does a job do whose list was given to another context while it ran? (E021, E023, E151, E303, E314, E315, E316, E319, E360, E457)
- `Q108` (phase 11, hw, medium): what do the page table entry flags WRITEONLY, CACHECONSISTENT and EDMPROTECT do on the hardware, which of the bus interface's requestors do they stop, and what does the fault report? (E021, E151, E319)
- `Q109` (phase 11, hw, low): do page directory entries whose page-size field (bits 3:1) names 16 KiB to 4 MiB translate on the hardware, and with which address mask and which table layout? (E021, E151)
- `Q110` (phase 11, hw, low): what do the bus interface's tiled address ranges (BIF_TILE0 and up: start, end, stride) do to the addresses of a requestor whose accesses fall inside one? (E021, E151, E246)

### dpm

- `Q038` (phase 10, hw, high): what does the final render read back of a partial render's depth (a depth buffer stored by ZLS, the 3D kick's RT status bit 1), now that a background object that reloads the target's colour gives an overflowing scene's whole image? (E202, E204, E160, E310, E311, E312, E442, E461, E465, E467, E468)
- `Q045` (phase 11, hw, high): what sets the fields of register 0x0740 that the TA kick turns into DPM store and load tasks (a host write reads back 0: E456), does a load task read back the macrotile lists a partial render stores in the RT data's state page, and what accesses the state page (0x20003000 for a context of up to 64x64) when a render follows a kept owner's gone context? (E158, E256, E310, E312, E456, E458, E462, E464)
- `Q081` (phase 11, hw, medium): what does CR_DPM_REG_074C bit 8 make the DPM read or write near offset 0x6010 of the context's TA-data space, and what fixes that place? (E203, E206, E313, E362, E447)
- `Q103` (phase 11, hw, medium): why does a scene of 100 to 500 triangles hang where the one-triangle scene overflows the parameter buffer and recovers, at 4096x4096 in 0x40 or 0x23 pages from 300 vertices and in 0x100 pages from 900? (E438, E310, E312)

### edm

- `Q002` (phase 3, hw, low): is the 399.0 MHz reference that times the EDM tick and TIMER the clock the USSE runs from? (E009, E084, E124, E377)
- `Q033` (phase 10, hw, medium): does the event input the hardware hands a PDS event program (ir1, seen as pa1 by the event task) carry CR_EVENT_STATUS bits in reverse order, and which hardware events set its bits 8 and 19? (E155, E146, E154)
- `Q082` (phase 11, hw, medium): what do CR_EVENT_STATUS2 bits 6 and 7 mean, bit 6 set while a job hangs in its pixel task and bit 7 while a TA job hangs or faults? (E317, E318, E319, E357, E431)
- `Q096` (phase 11, hw, low): does the sampler cache erratum of host bridge revisions below 4 show when a texture and other data have addresses that differ only above bit 28? (E002, E011, E013, E033, E035, E041, E114, E432)

### isp

- `Q030` (phase 11, hw, medium): what do CR_TE_AA bits 31 and 30 do when bit 29 is clear, where the triangle is gone, and does the sample layout of E281 hold in the tiles and windows past the first? (E210, E211, E219, E220, E281, E415, E502, E503, E504)
- `Q031` (phase 10, hw, medium): why does ISP word 0 bit 28 hang a multisampled render, when single-sampled it widens coverage to the union of eight samples? (E214, E215, E278, E416)
- `Q032` (phase 10, hw, medium): what does pcoeff hand the ISP in the punch-through pass, when the kept pixels' depth is the same without it and moves between runs only when it runs without the iteration it reads? (E217, E416)
- `Q066` (phase 11, hw, high): what do the three background-object words the 3D kick writes mean to the ISP, and what are the other words of a render's background object? (E069, E162, E209, E216, E410)
- `Q071` (phase 11, hw, medium): what do the bits of the ZLS control word that change nothing seen (12, 15, 16, 20 to 23, 27 to 31) do, and how does the ISP use the control in a render with a stencil test? (E057, E169, E216, E228, E284, E337, E411, E465, E466, E467)
- `Q072` (phase 11, hw, low): what does bit 1 of CR_ISP_REG_04DC do to a punch-through pass, when it hangs every one tried and changes no opaque or translucent pass? (E068, E073, E213, E222, E290, E416)
- `Q073` (phase 11, hw, medium): what does o0 hold at the start of an opaque pass's pixel shader? (E077, E283, E417)
- `Q089` (phase 11, hw, high): where does the closed driver's 4x multisampled render become a 64x64 image, when its PBE words are those of a single-sampled 64x64 target and the hardware stores 4x samples as 2x2 blocks; and do alpha to coverage and sample coverage reach the hardware at all? (E333, E339, E439, E502, E503, E508, E510)
- `Q138` (phase 11, hw, high): how does the closed driver's 4x render of a 64 x 64 texture fill a 64 x 64 image when one render with CR_TE_AA 0xe0000000 stores only a 16 x 8 window of each 32 x 16 tile (E503): are the four windows (0x20000000, 0x60000000, 0xa0000000, 0xe0000000) four renders of one frame, and what combines them (E503, E508, E510, E339, E439)
- `Q141` (phase 11, hw, low): why does a handful of pixels in one tile stay background when the full triangle covers the target, with CR_TE_AA bits 30 or 31 set in mode 1 (64 pixels at 64 x 64, tile (1, 2)) or at 96 x 80 in modes 1 and 2 (9 to 39 pixels), and 136 pixels at (32, 32) in mode 0 with 0xe0000000 (E502, E503, E504)

### mte

- `Q039` (phase 10, hw, medium): where is a user clip plane's state held between jobs, what resets it, and when do the vertex's distance dwords decide a plane? (E198, E280, E418)
- `Q069` (phase 11, hw, medium): what do OUTSEL bit 13 and the state block's presence bits 16-31 select? (E061, E066, E192, E193, E198, E286, E287, E419)
- `Q116` (phase 11, hw, medium): what does the MTE state's region clip (enable bit, first and last 32-pixel tile column, first and last 16-pixel tile row) do to the objects and the clear when it covers part of the target, and what does it do beyond a scissor? (E340, E347, E348)

### pbe

- `Q012` (phase 6, hw, medium): what float formats are pack modes 22 and 34, given that both read o0 as an IEEE single (sign, NaN and exponent) and store it at some of the triangle's dwords while the rest change with the job before? (E032, E270, E387, E406, E429)
- `Q040` (phase 11, hw, medium): what do EMIT2 bits 15:8 count, given that 4v pixels of each tile are stored for an even v up to 0x80, odd values hang and values above 0x80 change the image, and what do EMIT2 bits 6:0 select? (E046, E265, E266, E267, E382)
- `Q044` (phase 11, hw, low): what do bits 11:0 of CR_REG_0400 (0x80 as built) do, when no value of them changes a stored pixel in pack modes 0 to 3, and does bit 25 act on the other pack modes? (E029, E028, E031, E251, E268, E385)
- `Q046` (phase 11, hw, medium): do SIDEBAND bits 8:6 select the channel only in pack mode 8, or in the other one-channel modes too (24, 25 and those that store G8B8), and what do sideband bits 11 and 12 do? (E030, E031, E210, E269, E383)
- `Q074` (phase 11, hw, medium): why does a second end-of-tile emit in a tile leave the next job's image wrong, and does SIDEBAND bit 9 mark an emit that counts against a PBE tile? (E030, E130, E239, E240, E386)

### pds

- `Q013` (phase 6, hw, low): what does bit 18 of the copy's pixel-event data word 2 do, when it leaves the copy unchanged and changes a few pixels of the fill and the triangle? (E043, E046, E388)
- `Q019` (phase 7, hw, medium): what does the secondary attribute size (bits 24:18 of dword 1 of the background object) limit, given that all sixteen douta words reach sa0 to sa15 with 0, 1 and 4 rows, or does the task take its size from elsewhere? (E125, E391)
- `Q020` (phase 7, hw, medium): what does a douta in the triangle's primary pixel program do, when its markers never reach the USE task and the readback is the memory table's inputs for markers A in both runs, and other values for markers B in the first? (E125, E381)
- `Q021` (phase 7, hw, medium): with 4 components (DOUTI0 bits 23:22 = 3) where does the texel land, given pa3 reads 1.0 on most pixels? (E132, E420)
- `Q023` (phase 7, hw, high): what do PDS_SIZE bits 17:16 do, given that they move where the output registers o1 to o3 land? (E139, E081, E406)
- `Q024` (phase 7, hw, low): does CR_PDS_REG_0A78 change timing, when two of its values were slower in one timing run? (E141, E045, E396)
- `Q025` (phase 7, hw, medium): what does the SB field of CR_BIF_FAULT encode in the PDS faults, and why did a store of one dword fault in the follow-up run only, and a store of two dwords then eight in the first run only? (E143, E144, E145, E395)
- `Q026` (phase 7, hw, medium): why do the per-tile stores of the grid pixel-event probes leave empty slots and mixed copies, different ones per run? (E130, E394)
- `Q027` (phase 7, hw, medium): where do the values of a no-wait iteration go, given that pa0 never holds the iterated value and holds 0, 2, 6 and a few other values instead? (E131, E048, E393, E430)
- `Q057` (phase 11, hw, medium): what do doutc, douts, slc, mr and ir0 do as move destinations, and movsa on ports other than doutd, and does an enabled small count in tim hang the job, and why? (E127, E128, E264, E421)
- `Q058` (phase 11, hw, medium): what sets the input flags if0 and if1 outside a vertex program, since neither tests true in any primary pixel or pixel-event task tried? (E128, E130, E262, E263, E389)
- `Q059` (phase 11, hw, low): why do PDS stores totalling 2, 3 or 4 dwords fault the job, and why does an rwfence after a store, or after a faulted job, touch page 0? (E143, E144, E145, E395)
- `Q060` (phase 11, hw, medium): what do mr01, mr23, ir1 and the .h specials read in the vertex-side programs? (E128, E130, E262, E263, E390)
- `Q062` (phase 11, hw, low): what makes the PDS fetch pc read one or two below the reading instruction's index plus 3, at instructions 26-27 back to back (the end of a 64-dword block) in most runs? (E128, E142, E143, E260, E261, E384)
- `Q063` (phase 11, hw, low): what does bit 9 of a mov16 or mov32 special source select on the rest of the SGX family, when on SGX545 it only makes mov16 read 0? (E128)
- `Q093` (phase 11, hw, medium): does DOUTU1 bit 24 (wait for iterations) hang a job under the fetch wait, as it did in 4 of 126 jobs with both bits in colour and coordinate shapes, and why does the closed driver set it with bit 25? (E345, E364, E436, E454, E459, E460)

### platform

- `Q001` (phase 3, hw, medium): what do 0x0810, 0x0814 and 0x0818, set once by the init script to 0x1, 0xffff and 0x7ff, control? (E006, E010, E122, E401, E403, E404, E405)
- `Q075` (phase 11, hw, low): what does each HWPerf counter the firmware records (0x0044-0x0064, 0x0e84-0x0e90 and 0x0eb4-0x0ec0) count, and how does the group in CR_HWPERF_CTRL select them? (E149, E150, E152, E359, E434)
- `Q111` (phase 11, hw, high): which hardware event sets which bit of CR_EVENT_STATUS and CR_EVENT_STATUS2 in an ordinary TA, 3D, DPM or transfer job, how long does each stay set, and what does a write to CR_EVENT_HOST_CLEAR do to it? (E006, E154, E155, E357, E431, E435, E444)

### render

- `Q014` (phase 6, hw, low): why does a background object whose first PDS word has a high bit wrong render part or all of the first 32x16 tile before the job faults? (E029, E301, E363, E433)
- `Q043` (phase 11, hw, medium): what does bit 0 of CR_REG_0148, which the firmware loads for every render, partial render and transfer, change, when no bit of the word changes a triangle, five copies, a fill or a copy? (E056, E163, E160, E015, E028, E252, E302, E412, E406)
- `Q065` (phase 11, hw, low): what does the 3D wait for when render flag bit 0 hangs a kernel-built triangle job (the TA finishes and the 3D takes the render: E361, E435)? (E050, E156, E164, E165, E184, E303, E304, E361, E435)
- `Q085` (phase 11, hw, low): does our tri job's image or time change with the closed driver's two other 3D register values, CR_ISP_CTL bit 8 clear and 0x04c4 bit 25 set? (E326, E408)
- `Q099` (phase 11, hw, low): what do bits 25, 8 and 19:12 of 0x04c4 (render details dword 18) hold, which move with a texture target and the parameter buffer's size in the closed driver's frames? (E326, E408)

### ta

- `Q064` (phase 11, hw, medium): what does the region header mark that CR_TE_PSG bit 21 makes the TA write mean to the 3D, and is bit 1 of CR_DPM_STATE_CONTEXT_ID the 3D's DPM slot as bit 2 is the TA's? (E158, E172, E305, E409, E424)
- `Q068` (phase 11, hw, medium): do the twelve TA register words that are zero in our jobs save and resume the state of an interrupted TA? (E054, E056, E182, E183, E245)
- `Q070` (phase 11, hw, high): what do the TA object's format word bits 15:8 and above and its set masks select beyond the settings seen, and does the fitted region test hold for lines and points? (E176, E177, E180, E181, E185, E306, E307, E308, E414)
- `Q086` (phase 11, hw, medium): what rule gives CR_TE_MTILE1, CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE for a 4x multisampled target, whose 64x64 words are 0x802002, 0x802002 and 0x4 against the single-sampled rule's 0x1004004, 0x1004004 and 0x10? (E331, E329, E507, E511)
- `Q100` (phase 11, hw, medium): what do the fields of CR_TE_MTILE1 and CR_TE_MTILE2 mean, given that flips of their bits change the image or fault the job at 256x256 and 1024x768? (E247, E257, E407, E505, E506, E509)
- `Q117` (phase 11, hw, medium): where does a point's size come from, what footprint does the 3D cover for a point object (E181 shows the TA writes one), and does the closed driver's extra output row carry the size? (E181, E340, E346, E414)
- `Q139` (phase 11, hw, medium): what does a macrotile row's boundary do beyond the first, second and third fields of the macrotile words: what is bit 31, what is the stride's relation to the RT data, why is B2 at or past B3 exact in CR_TE_MTILE2 at 640 x 480, and what do the wrong images show per macrotile (E505, E506, E509, E407)
- `Q142` (phase 11, hw, medium): what do the 76 parameter-buffer and 132 TA-data dwords that change with CR_TE_AA bits 30 and 31 hold, and why do 0x60000000 and 0xa0000000 change the same number of dwords by different values (E504)

### texture

- `Q008` (phase 6, hw, low): how is the luma compared at the luma key's high cut, where five colours with the weighted sum 1000 to 1016 above the cut are outside the band while others up to 1016 above are inside, and what do bits 31:16 of the alpha word and the offset's precision do? (E039, E275, E426)
- `Q010` (phase 6, hw, low): what clears the colour-space words between jobs, given that a copy that does not load set 0 converts with the last loaded words, and the first job of a session after hung jobs converts with zeros? (E037, E039, E046, E271, E399)
- `Q078` (phase 11, hw, high): what do T3 bits 10, 14, 18-19 and 27-28 and T0 bit 27 select, given a copy that reads one texel, a sheared read, coordinates scaled by 2 and 4, smaller images after the source, and values of no texel? (E274, E397)
- `Q104` (phase 11, hw, medium): do T0's maximum level, LOD bias and MIPFILTER read a non-square chain (32x16) as they read the square ones, and how many levels does such a chain have? (E276, E441)
- `Q113` (phase 11, hw, medium): how does the sampler address the six faces of a cube map: which TEXTYPE and word layout name one, how are the faces laid out in memory, and how are they picked from the coordinates? (E342, E345, E364)
- `Q114` (phase 11, hw, low): how does the sampler read a 3D (volume) texture: which TEXTYPE or words name one, how are its slices laid out, and how do the third coordinate and the filter combine the slices? (E342)
- `Q115` (phase 11, hw, low): does the sampler filter anisotropically on this core, and which bits of the texture words or the smp operands select it and its ratio? (E041, E342)

### transfer

- `Q003` (phase 4, hw, medium): which event (if any) does a bus-interface fault raise, and what do the fault-request bits of CR_BIF_INT_STAT name, and what clears a latched fault in CR_BIF_INT_STAT and CR_BIF_FAULT while leaving the bus usable? (E021, E024, E317, E318, E319, E320, E354, E355, E357, E444)
- `Q011` (phase 6, hw, medium): why does a copy whose background-object tag (transfer word 0) is wrong read one texel, the source's last, for every pixel, and what stores the samples of CR_ISP_MSAA mode 2 in a copy? (E028, E272, E398)

### usse

- `Q016` (phase 6, hw, medium): which part of the smoa, smbo and smr sequences that fault the job makes it fault: the moest selectors, the changed state or the mirror mode? (E087, E369, E370)
- `Q017` (phase 6, hw, low): why does g19 read 0x1a as a store's source but 0 through a mov and as the pixel? (E085, E086, E372)
- `Q048` (phase 11, hw, low): do the MADD0 and MADD1 clock gates follow the USSE pipes' floating-point arithmetic, or their cache and texture traffic? (E006, E008, E011, E365, E445, E452)
- `Q050` (phase 11, hw, high): what do the visibility group's instructions do, and how do smp's mipmaps and LOD values, the border address modes, the compressed and YUV formats and firh's edge modes past the line and fixed banks 1 and 2 behave? (E083, E091, E123, E147, E292, E293, E294, E298)
- `Q051` (phase 11, hw, medium): what state do smoa, smbo, smr, imo and setfc set in the MOE, and what does moest return, beyond the smlsi increments the probes pinned? (E087, E097, E105, E109, E294, E296, E369, E370, E483, E515, E516)
- `Q052` (phase 11, hw, medium): what do .skipinv, .syncs, .nosched and the other scheduling flags change, and how many instructions after a write can a dependent instruction read the result, with or without an interlock? (E100, E104, E111, E113, E124, E371, E470, E472, E475, E478, E495, E497, E517)
- `Q053` (phase 11, hw, high): what do the global registers g18 to g20 and g39 to g43 hold in a triangle's pixel task, a vertex task and the end-of-tile task? (E085, E086, E372, E374)
- `Q054` (phase 11, hw, medium): what do #incp, .cut and .tasks/.taske do on the emits, and what do sideband bits 11 and 12 select, beyond the pack mode, bits 8:6, 9, 10 and 13 that the end-of-tile emit reads? (E030, E102, E106, E239, E269, E376, E488)
- `Q055` (phase 11, hw, medium): what do idf's modes other than bif, lock and release, setm and the cache-control operands do? (E088, E098, E099, E103, E107, E110, E117, E375)
- `Q080` (phase 11, hw, low): what do the USSE words no form decodes (classes 2, 22 and 26) do: which stop the stores after them, and which write registers? (E297, E368)
- `Q098` (phase 11, hw, medium): why do pa_n and sa_n read one value in a fill's pixel task, a mov to pa_n being lost, and why does an unwritten one read the job's pixel colour? (E366, E380, E484, E496)
- `Q123` (phase 11, hw, medium): does lapc reach instruction indices past the first 65536 words of a code base and the 18th bit of the program counter, and every index from 256 to 8191 in a fill? (E475, E476, E492)
- `Q125` (phase 11, hw, low): which code leaves 0xeb3 and 0x98 in pclink and 1101, 0101, 0001 or 1111 in p0-p3 of the instances that do not read the last job's value, and why do they come in aligned 2 x 2 quads of pixels? (E475, E477, E484, E500)
- `Q126` (phase 11, hw, low): which extension of a source 1 above 0x7fff does the test of iaddu32 read, and does the value it writes zero-extend source 1 with a repeat, an immediate or a constant in source 2, or with other destinations (E472, E498, E521)
- `Q127` (phase 11, hw, low): what do the extra i register of ima32, ima32 as a dual-issue secondary, and imae with a repeat, a u16 or z16 source or a .rsN shift do with the carry flags and with the 32-bit result? (E469, E470, E471, E493, E494, E495, E496, E501, E525, E526, E527, E528)
- `Q128` (phase 11, hw, medium): why does a client emitpds fault the job at page 0xd2000 or hang it, what do the s0, s1 and s2 operands of the started PDS program become (it saw ir0.0 2 or 3 whatever s2 was), and what in the control word's addend the PDS uses (0xFFF to 0x2000 left the fill's own value, 0x100 did not) (E488, E513, E520)
- `Q129` (phase 11, hw, low): why do 12 pixels (4 each of three values) of every fill that writes sa1, sa5 and sa7 show those sa values as their output, and how long does an sa written by one job stay readable (one job, or until the next job that writes it) (E484)
- `Q130` (phase 11, hw, low): when does a load on one counter land while a wdf waits on another: why four ldad on drc0 issued after a wdf drc1 that waited for four ldad on drc1 landed in 8 of 10 runs, and four ldad on drc1 after two ldr on drc2 never did in 10 (E479)
- `Q132` (phase 11, hw, low): where does a write to a temporary past the task's allocation go, and which instances' registers do the pixels that do not read the wrapped register read (E486)
- `Q133` (phase 11, hw, low): what bounds a phas request (it runs when T mod 256 is 4 to 192 and hangs the job when it is 0 or 196 to 252, whatever the task was started with: E519) and is the limit the same for a firmware task (E487, E519)
- `Q134` (phase 11, hw, medium): which register does a client str change, is str then ldr of one register ordered without a fence, and when is an idf drcN, bif required beyond an instance's own store (the host reading during the job, a texture fetch of the stored data) (E480, E481, E512, E513, E514)
- `Q135` (phase 11, hw, low): what does the high-word form of ima32, ima32 d, iK, a, b, c, do with immediates and constants other than c56, with cie on the same instruction, with .neg, in the dual-issue form and with the selector 3, and what does bit 46 of an ima32 word do to r14? (E493, E494, E495, E501, E525, E526, E528)
- `Q136` (phase 11, hw, low): how long does a value written to sa0 last across jobs, why is pa0 not written by ima32 or mov, and is the 0xff00ff00 and 0xff203040 mixture that pa0 reads in the first jobs of a table the colour left by the job before it? (E496, E484)
- `Q137` (phase 11, hw, low): do the rules of the test field of a class 9 test (zero part: bits 41 over 40; sign part: bits 43 over 42; the parts ANDed under join `a`, E499, ORed with an absent part true under join `o`, E529) hold for the shifts, the 8-bit and 16-bit lane operations, the other forms of the bitwise group and the other classes' tests, and is a word with several conditions, greater than zero among them, usable from compiler output? (E499, E498, E529, E530)
- `Q143` (phase 11, hw, medium): when does another instance's unfenced stad reach a load, what orders the tiles and quads (the left 32 columns before the right, a quad together), and when is an idf drcN, bif needed for another reader (the host during the job, a texture fetch of the stored data, a firmware task) (E512, E513, E514)
- `Q144` (phase 11, hw, low): how many registers does a phase get from a phas request above 256 (a request runs when it is 4 to 192 modulo 256 and hangs the job when it is 0 or 196 to 252), and what bounds it (E519)
- `Q145` (phase 11, hw, low): why does the control word's addend of an emitpds, from 0xFFF to 0x2000, leave the fill's own dword 0x403 where 0x100 gives 3 or 2, and what 0x800 does (E520)
- `Q146` (phase 11, hw, low): when does a load that is not waited for land, why did a load not waited for hold the loaded value after 40, 100 and 128 `nop` but not after 48 and 64, and in what order two loads and a `mov` to one register land (E517)
- `Q147` (phase 11, hw, medium): does a write to a register past the task's allocation land in the register whose index is the register's modulo the allocation, or is it dropped, and do E486 and E519 disagree (E486, E519)
- `Q150` (phase 11, hw, low): do the raw test words with the chan field enc[38:36] = 1 to 7 on 8-bit and 16-bit lane operations, on the fields other than the six run and with the o join read as the rule of the Test channels page says (E530, E499)
- `Q151` (phase 11, hw, low): does the o join rule of E529 (enc[39] = 0: the two parts of the test field ORed, an absent part true) hold for the shifts, the 8-bit and 16-bit lane operations and the other classes' tests, and with a chan other than chan0, and does any compiler output need it? (E529, E499)

### vdm

- `Q036` (phase 10, hw, medium): what do the DPM's status words hold (the high half of the STATUS2 registers 0x0710 and 0x071c, 0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS' high half, and the owner words 0x0700 to 0x0728 a kept owner changes), what do CR_DMS_CTRL bits 2:0 and the signature and settle registers report about the two pipes, and what DPM or page-table-builder state does a base-only builder fault leave that a core reset does not clear? (E153, E160, E184, E200, E201, E256, E309, E310, E312, E316, E358, E362, E438, E443, E446, E448, E451, E453, E458, E462, E463)
- `Q042` (phase 11, hw, medium): what do bits 27:24 of the index list's first trailing word (VDM_INDEX2) do, when its low bits move the list's first index and 0x0f000000 drops two of five triangles? (E188, E300, E307, E308, E414)
- `Q047` (phase 11, hw, high): what do VDM_STATE1 bit 8, bits 11:9 and bits 15:13 select for a state task, when on the one-triangle job bit 8 changes nothing, bits 11:9 at 0 stop the triangle before tiling and bits 15:13 at 0, 5 or 6 hang it? (E060, E185, E186, E187, E299, E414, E427, E440)
- `Q092` (phase 11, hw, medium): what do bits 31:28 of the index list's first trailing word count, which the closed driver writes as 0xf on 1886 captured lists and 0xd on a draw of eight vertex attributes? (E346, E348, E414)
- `Q094` (phase 11, hw, medium): what hardware capacity bounds VDM_TASK0.MAX_VERTICES as a function of the task's output rows and attribute rows (the captures have 15, 13, 9, 7 or 2), and what does a vertex task do when the field is above it? (E346)
- `Q102` (phase 11, hw, medium): what state does a completed job with VDM state word 1 bits 11:9 = 7 leave that makes the next such job hang, and why does the reset after a hang clear it? (E060, E185, E299, E413)
- `Q112` (phase 11, hw, medium): what do bits 25:24 of the index list header do, which are clear in all 1888 captured lists, and does the TA take indices wider than the 16 bits the captured lists use? (E188, E346, E414)

### zls

- `Q101` (phase 11, hw, low): what does bit 19 (the negated float) do with the integer stored formats (CR_ISP_ZLSCTL bits 26:24 = 1 and 2)? (E057, E284, E411, E465, E466, E490)
- `Q107` (phase 11, hw, medium): why does the final render of a job that overflows store zeros for the first row of macrotiles and the depth with its sign bit set for the rest, and in what order are the tiles stored? (E461, E058, E411, E465, E468, E489)
- `Q120` (phase 11, hw, medium): what do the stored depth formats 3 to 7 (CR_ISP_ZLSCTL bits 26:24) hold and how are they laid out, given that they store depth and stencil packed or nothing? (E466, E490)
- `Q121` (phase 11, hw, medium): what is the in-tile order of the stencil store (one byte a pixel, 128 dwords a 32 x 16 tile) and what does the stencil test do against a loaded stencil? (E466, E467)
- `Q122` (phase 11, hw, low): what does the ZLS store write for the pixels of an edge tile that lie outside the target, and for the 16 x 16 blocks outside it? (E465)

## Parked: not hardware knowledge

### closed firmware

#### dpm

- `Q084` (phase 11, fw): how does the closed driver turn its PBSize app hint into the parameter buffer's page count and thresholds, given 1 MiB and 8 MiB both give 98 pages and 768 KiB fails? (E327)

#### edm

- `Q034` (phase 10, fw): does the EDM hold back a TA command whose destination sync is incomplete when another context is queued (source and transfer-queue syncs: E450)? (E161, E154, E320, E450)

#### render

- `Q029` (phase 9, fw): what does the render context's own cleanup wait for once its RT data set is cleaned up (the PB is released by the PB step of the donor's cleanup: E449)? (E148, E023, E156, E164, E289, E303, E304, E314, E315, E318, E354, E355, E449)
- `Q049` (phase 11, fw): does the firmware or the hardware ever read dword 7 (offset 0x01c) of the render context, which the EDM dataflow reaches on no path? (E013, E021, E156, E165, E361, E448)
- `Q118` (phase 11, fw): how does the firmware's kick tell that its context's page directory is in none of the bus interface's directory lists (a compare against the lists' registers, or a per-context record)? (E360)
- `Q119` (phase 11, fw): does one TA command carrying both FIRST_KICK and LAST_KICK act as two commands in the firmware (a kick and a closing kick)? (E156, E165)

#### transfer

- `Q004` (phase 4, fw): can a transfer context whose flag bit 4 is set be released, which agent but the host sets flag bits 1 and 4, and which priorities above 0 have queue slots of their own (a priority 1 or 2 hangs a job and 3 faults it: E455)? (E015, E455)

#### usse

- `Q124` (phase 11, fw): do p0-p3 and pclink survive from one firmware (EDM) task to the next, and does a task start with them clear, set or as the last task left them? (E475, E477, E484)
- `Q131` (phase 11, fw): can the hardware run two firmware (EDM) tasks at once, and does a wdf with nothing outstanding or an unfenced store at the end of a task behave as it does in a fill (E478, E480)

#### zls

- `Q088` (phase 11, fw): what reads the render details' unpatched ZLS control word that the closed driver writes between frames (0x0011700a), now that bit 14 is known to load the depth and bit 13 the stencil? (E335, E336, E337, E411, E467)

### kernel

#### edm

- `Q005` (phase 6, kernel): should the kernel ask the firmware for its identity on every boot, so DEV_QUERY reports it without the debug option? (E017, E022, E321, E402)

#### platform

- `Q095` (phase 11, kernel): does giving the EDM a page directory of its own, rather than gma500's default one, change anything beyond the coupling of their teardowns? (E008, E018, E021)

#### ta

- `Q140` (phase 11, kernel): why does our stack's 4x render fault the job (BIF fault at pages 0x20006, 0x20008, 0x2000a) at 320 x 160 and above while 256 x 128 and 192 x 96 complete, and what size does the kernel allocate for a multisampled target (E507)

#### vdm

- `Q037` (phase 10, kernel): why did one of E186's runs find no object after the job hung in its pixel task, when a dump taken before recovery always holds it? (E186, E318, E422)
