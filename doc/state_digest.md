<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# State digest

*Generated from the tracked tree by `tools/records/digest.py`; do not edit.*

Where the project stands, on one page: the open questions, the newest records, the published closing
sessions, the tool and fork versions, the known tool weaknesses and the simulator's unmodelled
baseline. The records, questions and manifests themselves hold the detail.

## Open questions

164 open: 154 hw, 10 parked. Each with its unit, value and the last three records of its evidence
list.

- `Q076` bif, high: which pages does each bus-interface requestor of a render (the TA, the 3D, the
  EDM's PB load) need in the directory of the list it ... (E592, E745, E761)
- `Q038` dpm, high: what does the final render read back of a partial render's depth (a depth buffer
  stored by ZLS, the 3D kick's RT status bit 1), now that a ... (E625, E628, E629)
- `Q045` dpm, high: what does the DPM store in the state page, does a load task read back the
  macrotile lists a partial render stores in the RT data's state ... (E625, E627, E631)
- `Q191` dpm, high: what are the words that land in a kept owner's control page (0x00200047), OTPM
  page (0x04000417) and state page (0x00020001, 2) after the ... (E462, E591, E631)
- `Q210` dpm, high: what keeps the second global page past A_k, the page count once the object block
  straddling global pages k - 1 and k is tiled, at band 6 of ... (E915, E917, E918)
- `Q211` dpm, high: does the page need U of HU1 (E773, E863, E883, E916: exact for 26 held-out
  scenes made of the tool's triangle) hold for wide scenes of many ... (E883, E899, E916)
- `Q066` isp, high: what do the three background-object words the 3D kick writes mean to the ISP,
  and what are the other words of a render's background object? (E216, E410, E590)
- `Q089` isp, high: where does the closed driver's 4x multisampled render become a 64x64 image, when
  its PBE words are those of a single-sampled 64x64 target ... (E508, E510, E727)
- `Q199` isp, high: what is the integer range and the behaviour at the limits (saturation, wrap,
  removal) of the ISP's 1/256-pixel vertex format (E607: window ... (E607, E683, E684)
- `Q202` isp, high: do the coverage rule (centre sample, vertices on the 1/256 grid, top-left ties)
  and the attribute and depth planes of E606 hold with ... (E281, E502, E606)
- `Q205` isp, high: what is the arithmetic by which the ISP decides the coverage and the depth of a
  pixel for an arbitrary triangle, and the iterators' ... (E215, E307, E542)
- `Q260` isp, high: the tie of a negative window coordinate 1/512 above the 1/256 grid rounds away
  from zero on five of six sweeps (E914): what makes the y ... (E681, E683, E914)
- `Q023` pds, high: how many output dwords does a pixel task get per setup, and what do the data
  rows limit (E406) (E742, E759, E880)
- `Q276` pds, high: in E709's command (state block word 4 at 0x00030001), why is the o3 word in the
  tag-5 OR that of lane 0 of the quad in a job whose words ... (E878, E880, E905)
- `Q111` platform, high: which hardware event sets which bit of CR_EVENT_STATUS and CR_EVENT_STATUS2
  in an ordinary TA, 3D, DPM or transfer job, and how long does ... (E890, E902, E921)
- `Q070` ta, high: what do the TA object's format word bits 15:8 and above and its set masks select
  beyond the settings seen, and does the fitted region test ... (E543, E544, E777)
- `Q078` texture, high: what do T3 bits 10, 14, 18-19 and 27-28 and T0 bit 27 select, given a copy
  that reads one texel, a sheared read, coordinates scaled by 2 ... (E564, E566, E722)
- `Q050` usse, high: what do the visibility group's instructions do, and how do smp's mipmaps and
  LOD values, the border address modes, the compressed and YUV ... (E563, E565, E568)
- `Q047` vdm, high: what do VDM_STATE1 bit 8, bits 11:9 and bits 15:13 select for a state task, when
  on the one-triangle job bit 8 changes nothing, bits 11:9 ... (E427, E440, E545)
- `Q108` bif, medium: what do the page table entry flags WRITEONLY, CACHECONSISTENT and EDMPROTECT
  do on the hardware, which of the bus interface's requestors do ... (E021, E151, E319)
- `Q081` dpm, medium: what does CR_DPM_REG_074C bit 8 make the DPM read or write near offset 0x6010
  of the context's TA-data space, and what fixes that place? (E313, E362, E447)
- `Q103` dpm, medium: why does a scene of 100 to 500 triangles take 35 or more partial renders where
  the one-triangle scene overflows the parameter buffer and ... (E438, E630, E706)
- `Q192` dpm, medium: does the store that follows the next context's render replace the state page a
  partial-render owner left (18 non-zero dwords after its ... (E464, E591, E631)
- `Q082` edm, medium: what does CR_EVENT_STATUS2 bit 6 follow in a pixel task (a fill without a
  load: a tile's time near 125 us, E805; a program that waits on a ... (E839, E840, E841)
- `Q030` isp, medium: does the sample layout of E281 hold in the tiles and windows past the first
  (what CR_TE_AA bits 31 and 30 do when bit 29 is clear is ... (E504, E728, E829)
- `Q031` isp, medium: why does ISP word 0 bit 28 hang a multisampled render, when single-sampled it
  widens coverage to the union of eight samples? (E215, E278, E416)
- `Q032` isp, medium: what does pcoeff hand the ISP in the punch-through pass, when the kept pixels'
  depth is the same without it and moves between runs only ... (E217, E416)
- `Q071` isp, medium: what do the bits of the ZLS control word that change nothing seen (12, 15, 16,
  20 to 23, 27 to 31) do, alone and set together, what does ... (E466, E467, E665)
- `Q073` isp, medium: what does o0 hold at the start of an opaque pass's pixel shader? (E417, E739,
  E757)
- `Q190` isp, medium: does a render's background object with texture layers (the 23-dword form of a
  transfer copy: the six words after the PDS words, the layer's ... (E069, E209, E590)
- `Q200` isp, medium: why do the dyadic controls of E731 store one or two ulps below the truncated
  exact plane, below binade 0, in a region bounded by a diagonal ... (E758, E912, E913)
- `Q240` isp, medium: does the coverage rule of E606 (vertices on the 1/256 pixel grid, exact centre
  test, left and top edges owning ties) hold for random ... (E682, E912, E913)
- `Q261` isp, medium: how large is the error band of the ISP's edge evaluation (E684: 16 pixels in
  14 of 208 cases within 5.6e-4 pixel of an edge line) as a ... (E682, E684)
- `Q262` isp, medium: what bounds the error of the stored depth and of the iterated clip z on E680's
  targets, where E606's tolerances fail for some triangles of ... (E684, E912, E913)
- `Q288` isp, medium: what rule gives the stored depth of a plane with a non-dyadic gradient in x
  (class b and c of E731) when the tile-corner value T by ... (E606, E731, E740)
- `Q039` mte, medium: where is a user clip plane's state held between jobs, what resets it, and when
  do the vertex's distance dwords decide a plane? (E198, E280, E418)
- `Q069` mte, medium: what do OUTSEL bit 13 and the state block's presence bits 16-31 select? (E286,
  E287, E419)
- `Q116` mte, medium: what does the MTE state's region clip (enable bit, first and last 32-pixel
  tile column, first and last 16-pixel tile row) do to the objects ... (E340, E347, E348)
- `Q012` pbe, medium: what float formats are pack modes 22 and 34, given that both read o0 as an
  IEEE single (sign, NaN and exponent) and store it at some of the ... (E387, E406, E429)
- `Q040` pbe, medium: what do EMIT2 bits 15:8 count, given that 4v pixels of each tile are stored
  for an even v up to 0x80, odd values hang and values above 0x80 ... (E266, E267, E382)
- `Q046` pbe, medium: do SIDEBAND bits 8:6 select the channel only in pack mode 8, or in the other
  one-channel modes too (24, 25 and those that store G8B8), and ... (E210, E269, E383)
- `Q074` pbe, medium: why does a second end-of-tile emit in a tile leave the next job's image wrong,
  and does SIDEBAND bit 9 mark an emit that counts against a ... (E239, E240, E386)
- `Q019` pds, medium: what does the secondary attribute size (bits 24:18 of dword 1 of the
  background object) limit, given that all sixteen douta words reach sa0 ... (E125, E391)
- `Q020` pds, medium: what does a douta in the triangle's primary pixel program do, when its markers
  never reach the USE task and the readback is the memory ... (E125, E381)
- `Q025` pds, medium: what does the SB field of CR_BIF_FAULT encode in the PDS faults, and why did a
  store of one dword fault in the follow-up run only, and a ... (E144, E145, E395)
- `Q026` pds, medium: why do the per-tile stores of the grid pixel-event probes leave empty slots
  and mixed copies, different ones per run? (E130, E394)
- `Q027` pds, medium: where do the values of a no-wait iteration go, given that pa0 never holds the
  iterated value and holds 0, 2, 6 and a few other values ... (E131, E393, E430)
- `Q057` pds, medium: what do doutc, douts, slc, mr and ir0 do as move destinations, and movsa on
  ports other than doutd, and does an enabled small count in tim ... (E128, E264, E421)
- `Q058` pds, medium: what sets the input flags if0 and if1 outside a vertex program, since neither
  tests true in any primary pixel or pixel-event task tried? (E262, E263, E389)
- `Q060` pds, medium: what do mr01, mr23, ir1 and the .h specials read in the vertex-side programs?
  (E262, E263, E390)
- `Q093` pds, medium: does DOUTU1 bit 24 (wait for iterations) hang a job under the fetch wait, as
  it did in 4 of 126 jobs with both bits in colour and ... (E454, E459, E460)
- `Q207` pds, medium: what do the PDS programs of a transfer do with the inputs and instructions no
  record measured: if0 and if1, ir2, a movs reading ir1.l and ... (E263, E265, E620)
- `Q001` platform, medium: what do 0x0810, 0x0814 and 0x0818, set once by the init script to 0x1,
  0xffff and 0x7ff, control? (E403, E404, E405)
- `Q043` render, medium: what does bit 0 of CR_REG_0148, which the firmware loads for every render,
  partial render and transfer, change, when no bit of the word ... (E302, E406, E412)
- `Q064` ta, medium: what does the region header mark that CR_TE_PSG bit 21 makes the TA write mean
  to the 3D, and is bit 1 of CR_DPM_STATE_CONTEXT_ID the 3D's ... (E305, E409, E424)
- `Q068` ta, medium: do the twelve TA register words that are zero in our jobs save and resume the
  state of an interrupted TA? (E182, E183, E245)
- `Q086` ta, medium: what rule gives CR_TE_MTILE1, CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE for a 4x
  multisampled target, whose 64x64 words are 0x802002, ... (E824, E886, E908)
- `Q100` ta, medium: what do the fields of CR_TE_MTILE1 and CR_TE_MTILE2 mean, given that flips of
  their bits change the image or fault the job at 256x256 and ... (E506, E509, E877)
- `Q139` ta, medium: in what order does the TA write a macrotile's region headers (row by row fits
  20 of E907's 21 dumped cases and misses stride 4, 4 x 4 tile ... (E509, E877, E907)
- `Q142` ta, medium: which control-stream form does the TA write in a region of the grid that
  CR_TE_AA bits 30 and 31 halve (16 x 16, 32 x 8 and 16 x 8 ... (E504, E893)
- `Q159` ta, medium: what rule lists the 32 x 16 regions of a one-line object: at ISP word 1 width
  0x10 the list reaches a near-vertical segment at 0.4375 pixel ... (E543)
- `Q230` ta, medium: what does the TA write in the cases of the clip, the target's edge and the
  numeric formats that E776 to E783 and E795 to E798 left open: ... (E859, E872, E879)
- `Q296` ta, medium: which mantissas of w whose exact 1/w lies half an ulp or more above RZ of 1/w
  store RZ + 1 as a kept vertex's 1/w word (106 of the 189 read ... (E859, E872, E879)
- `Q180` texture, medium: why did all 28 triangle jobs of the four-component DOUTI0 probes hang
  (E569), the two controls with the old source word 0x40800801 included ... (E420, E541, E569)
- `Q284` texture, medium: what are the (s, t) orientation of each cube face, the edge filtering
  across faces and the face size limits of TEXTYPE 2 (E567, E726, E844)
- `Q003` transfer, medium: which event (if any) does a bus-interface fault raise, and what do the
  fault-request bits of CR_BIF_INT_STAT name, what clears a latched ... (E901, E919, E920)
- `Q011` transfer, medium: why does a copy whose background-object tag (transfer word 0) is wrong
  read one texel, the source's last, for every pixel, and what stores ... (E028, E272, E398)
- `Q206` transfer, medium: what do the words of a transfer job that no record explains do: the 17
  register words of the command beyond the render box (words 12 and ... (E876, E884, E909)
- `Q016` usse, medium: which part of the smoa, smbo and smr sequences that fault the job makes it
  fault: the moest selectors, the changed state or the mirror mode? (E087, E369, E370)
- `Q051` usse, medium: what state do smoa, smbo, smr, imo and setfc set in the MOE, and what does
  moest return, beyond the smlsi increments the probes pinned? (E483, E515, E516)
- `Q052` usse, medium: what do .skipinv, .syncs, .nosched and the other scheduling flags change, and
  how many instructions after a write can a dependent ... (E495, E497, E517)
- `Q053` usse, medium: what sets the global registers g18 and g21 in a vertex task, and what do g17,
  g18, g21 to g25 and g39 hold in the end-of-tile task of each ... (E571, E572, E708)
- `Q054` usse, medium: what do #incp, .cut and .tasks/.taske do on the emits? (E269, E376, E488)
- `Q055` usse, medium: what do idf's modes other than bif, lock and release, setm and the
  cache-control operands do? (E110, E117, E375)
- `Q098` usse, medium: why do pa_n and sa_n read one value in a fill's pixel task, a mov or ima32 to
  pa_n being lost, and why does an unwritten one read the job's ... (E496, E748, E820)
- `Q123` usse, medium: does lapc reach instruction indices past the first 65536 words of a code base
  and the 18th bit of the program counter, and every index from ... (E475, E476, E492)
- `Q128` usse, medium: why does a client emitpds fault the job at page 0xd2000 or hang it, what do
  the s0, s1 and s2 operands of the started PDS program become ... (E488, E513, E520)
- `Q132` usse, medium: where does a write to a temporary or a register past the task's allocation go
  (does it land in the register whose index is the register's ... (E486, E519, E535)
- `Q134` usse, medium: which register does a client str change, and when is an idf drcN, bif
  required beyond an instance's own store (the host reading during the ... (E514, E533, E534)
- `Q143` usse, medium: when does another instance's unfenced stad reach a load, what orders the
  tiles and quads (the left 32 columns before the right, a quad ... (E512, E513, E514)
- `Q154` usse, medium: does str then ldr of one register stay ordered for a register whose write
  starts work or that another writer changes, with a job running, ... (E445, E534)
- `Q183` usse, medium: which store forms in the end-of-tile task fault the job and why does E572's
  fault not reproduce in E707 (a program equal to E572's but for ... (E572, E707)
- `Q036` vdm, medium: what do the DPM's status words hold (the high half of the STATUS2 registers
  0x0710 and 0x071c, 0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS' ... (E626, E630, E631)
- `Q042` vdm, medium: what do bits 27:24 of the index list's first trailing word (VDM_INDEX2) do,
  when its low bits move the list's first index and 0x0f000000 ... (E307, E308, E414)
- `Q092` vdm, medium: what do bits 31:28 of the index list's first trailing word count, which the
  closed driver writes as 0xf on 1886 captured lists and 0xd on a ... (E348, E414, E546)
- `Q112` vdm, medium: what do bits 25:24 of the index list header do, which are clear in all 1888
  captured lists, and does the TA take indices wider than the 16 ... (E414, E737, E756)
- `Q163` vdm, medium: what is the state the jobs leave that decides whether a job with VDM_STATE1
  bits 11:9 other than 2 hangs (E700: a counter c, cleared by a ... (E545, E700, E701)
- `Q271` vdm, medium: what does VDM_TASK1 bits 31:24 do when it is forced to differ from the natural
  (4 + N + 3) / 4 of the vertex's N outputs (E703: the render ... (E546, E702, E703)
- `Q107` zls, medium: why does the final render of a job that overflows store zeros for the first
  row of macrotiles and the depth with its sign bit set for the ... (E489, E628, E629)
- `Q120` zls, medium: what do the stored depth formats 3 to 7 (CR_ISP_ZLSCTL bits 26:24) hold and
  how are they laid out, given that they store depth and stencil ... (E466, E490)
- `Q121` zls, medium: what is the in-tile order of the stencil store (one byte a pixel, 128 dwords a
  32 x 16 tile) and what does the stencil test do against a ... (E466, E467)
- `Q109` bif, low: do page directory entries whose page-size field (bits 3:1) names 16 KiB to 4 MiB
  translate on the hardware, and with which address mask and ... (E021, E151)
- `Q110` bif, low: what do the bus interface's tiled address ranges (BIF_TILE0 and up: start, end,
  stride) do to the addresses of a requestor whose accesses ... (E021, E151, E246)
- `Q002` edm, low: is the 399.0 MHz reference that times the EDM tick and TIMER the clock the USSE
  runs from? (E084, E124, E377)
- `Q033` edm, low: which hardware event sets bit 19 of the event word pa1 that the hardware hands a
  PDS event program, if any (none of the 138 job events of ... (E746, E747, E771)
- `Q096` edm, low: does the sampler cache erratum of host bridge revisions below 4 show when a
  texture and other data have addresses that differ only above ... (E041, E114, E432)
- `Q158` edm, low: which sa, i and temporaries of a firmware task keep their value across a debugfs
  reset and across a firmware reload and boot (E536's ... (E537, E809, E810)
- `Q168` edm, low: what limits the temporaries of a firmware task above TRC 48 (E540 predicted a
  hang for 49 and 64; E550 armed 32 to 48 with trc_hazard=1 and ... (E540, E550)
- `Q194` edm, low: does a load that is not waited for land by itself in a firmware (EDM) task, at
  what distance, and is that a property of the task, of the ... (E517, E602)
- `Q196` edm, low: do the client results of 11.36 for the compare and the high word of ima32 (E595,
  E597), the predicated register moves and ba (E596) and the ... (E598, E599, E601)
- `Q290` edm, low: what does a write to CR_EVENT_KICK with the kicker word unchanged start in the
  EDM (E834: no event and no command read, before or after a ... (E819, E834, E835)
- `Q294` edm, low: which of bits 4, 7 and 10 of the sa65 word of E537 (0xb009c5dc, without bit 8)
  stop the tick through the closed task (E814: that word ... (E812, E814, E902)
- `Q072` isp, low: what does bit 1 of CR_ISP_REG_04DC do to a punch-through pass, when it hangs
  every one tried and changes no opaque or translucent pass? (E222, E290, E416)
- `Q141` isp, low: why does a handful of pixels in one tile stay background when the full triangle
  covers the target, with CR_TE_AA bits 30 or 31 set in mode ... (E502, E503, E504)
- `Q201` isp, low: why does the position source (E437, E502: x + 0.375, y + 0.125 in mode 0 and
  every multisampling mode tried) differ from the point at which ... (E437, E502, E606)
- `Q241` isp, low: what do ISP word 0 bits 15, 16, 17 and 18, the depth compares 2, 3, 5 and 6
  against equal depths, the visibility test (ISP word 1 bit 3), ... (E660, E739, E757)
- `Q044` pbe, low: what do bits 11:0 of CR_REG_0400 (0x80 as built) do, when no value of them
  changes a stored pixel in pack modes 0 to 3, and does bit 25 act ... (E251, E268, E385)
- `Q013` pds, low: what does bit 18 of the copy's pixel-event data word 2 do, when it leaves the
  copy unchanged and changes a few pixels of the fill and the ... (E043, E046, E388)
- `Q024` pds, low: does CR_PDS_REG_0A78 change timing, when two of its values were slower in one
  timing run? (E045, E141, E396)
- `Q059` pds, low: why do PDS stores totalling 2, 3 or 4 dwords fault the job, and why does an
  rwfence after a store, or after a faulted job, touch page 0? (E144, E145, E395)
- `Q062` pds, low: what makes the PDS fetch pc read one or two below the reading instruction's index
  plus 3, at instructions 26-27 back to back (the end of a ... (E260, E261, E384)
- `Q063` pds, low: what does bit 9 of a mov16 or mov32 special source select on the rest of the SGX
  family, when on SGX545 it only makes mov16 read 0? (E128)
- `Q075` platform, low: what does each HWPerf counter the firmware records (0x0044-0x0064,
  0x0e84-0x0e90 and 0x0eb4-0x0ec0) count, and how does the group in ... (E152, E359, E434)
- `Q014` render, low: why does a background object whose first PDS word has a high bit wrong render
  part or all of the first 32x16 tile before the job faults? (E301, E363, E433)
- `Q065` render, low: what does the 3D wait for when render flag bit 0 hangs a kernel-built triangle
  job (the TA finishes and the 3D takes the render: E361, ... (E304, E361, E435)
- `Q099` render, low: what do bits 25, 8 and 19:12 of 0x04c4 (render details dword 18) hold, which
  move with a texture target and the parameter buffer's size in ... (E326, E408)
- `Q160` ta, low: how does the TA split an index list of several lines into objects and regions: two
  lines at 128 x 128 give two objects of 2 vertices (the ... (E543)
- `Q161` ta, low: what does a point do at the edges of its size field: sizes under 1/16 pixel (1/32
  draws one pixel), zero (tiles listed, no pixel), negative ... (E346, E544)
- `Q162` ta, low: what do OUTSEL bits 10, 11 and 15 select, which fault (bits 8 without a size row,
  10, 11, 15 on the plain triangle) or hang (10 and 15 with ... (E544)
- `Q164` ta, low: what does bit 21 of the control-stream primitive word mean, which puts one dword
  (0x00000400 in 336 cases and 0x00001000 in 30) after the ... (E702, E738, E755)
- `Q165` ta, low: why does a coordinate size and format word that describes sets the vertex program
  does not write (size code 5 over two or three outputs, a ... (E541)
- `Q231` ta, low: what do the words of a render job that the vertex side and the TA read or ignore
  and no record explains do: the command's CR_MTE_CTRL ... (E180, E650, E652)
- `Q008` texture, low: how is the luma compared at the luma key's high cut, where five colours with
  the weighted sum 1000 to 1016 above the cut are outside the ... (E039, E275, E426)
- `Q010` texture, low: what clears the colour-space words between jobs, given that a copy that does
  not load set 0 converts with the last loaded words, and the ... (E046, E271, E399)
- `Q104` texture, low: does a mip chain of a 1D texture, of a texture with a side of 1 at level 0,
  or of a format other than 32 bits read as the non-square chains ... (E276, E441, E562)
- `Q114` texture, low: how does the sampler read a 3D (volume) texture: which TEXTYPE or words name
  one, how are its slices laid out, and how do the third ... (E342, E567)
- `Q115` texture, low: does the sampler filter anisotropically on this core, and which bits of the
  texture words or the smp operands select it and its ratio? (E564, E720, E723)
- `Q177` texture, low: what do T0 address modes 4 to 7 read along the u axis of a 16x16 twiddled
  texture (indices 324 to 366 past the 256 texels, a period of 6 or ... (E033, E565)
- `Q178` texture, low: what does TEXTYPE 5 compute from the texture memory it reads (two values, 0
  and 0x0000ffff, that follow the stored dwords, a 16-column step ... (E726, E894, E911)
- `Q179` texture, low: how are the blocks and the data bits of formats 23 to 26 laid out (a data bit
  changes 7 to 13 pixels, the blocks of 23 and 24 do not differ ... (E342, E568, E724)
- `Q181` texture, low: does the fill's transfer command load a colour-space set at all (xfer:17^=1
  and xfer:18 to 22 made no difference for formats 28 and 29, ... (E037, E040, E568)
- `Q280` texture, low: what makes up to 56 of 2048 pixels of a gradient job differ from the
  Euclidean footprint of the pairs (op0, op2) and (op1, op3) with a LOD ... (E563, E721, E744)
- `Q282` texture, low: what arithmetic gives the bilinear sample of an sRGB texel (T0 bit 27) given
  that decode-then-filter in float fits 43% to 56% of the pixels ... (E720, E723)
- `Q283` texture, low: what layout does type 4 read past 32 texels wide (32 x 32 blocks of 1024
  dwords read post hoc at 64 and 128, E910) and in what order are ... (E567, E725, E910)
- `Q017` usse, low: why does g19 read 0x1a as a store's source but 0 through a mov and as the pixel?
  (E085, E086, E372)
- `Q048` usse, low: do the MADD0 and MADD1 clock gates follow the USSE pipes' floating-point
  arithmetic, or their cache and texture traffic? (E365, E445, E452)
- `Q080` usse, low: what do the USSE words no form decodes (classes 2, 22 and 26) do: which stop the
  stores after them, and which write registers? (E297, E368)
- `Q125` usse, low: which code leaves 0xeb3 and 0x98 in pclink and 1101, 0101, 0001 or 1111 in p0-p3
  of the instances that do not read the last job's value, ... (E477, E484, E500)
- `Q126` usse, low: which extension of a source 1 above 0x7fff does the test of iaddu32 read, and
  does the value it writes zero-extend source 1 with a repeat, ... (E472, E498, E521)
- `Q127` usse, low: what do the extra i register of ima32, ima32 as a dual-issue secondary, and imae
  with a repeat, a u16 or z16 source or a .rsN shift do with ... (E528, E595, E597)
- `Q129` usse, low: why do 12 pixels (4 each of three values) of every fill that writes sa1, sa5 and
  sa7 show those sa values as their output, and how long ... (E484)
- `Q130` usse, low: when does a load on one counter land while a wdf waits on another: why four ldad
  on drc0 issued after a wdf drc1 that waited for four ldad ... (E479)
- `Q133` usse, low: what bounds a phas request (it runs when T mod 256 is 4 to 192 and hangs the job
  when it is 0 or 196 to 252, whatever the task was started ... (E519, E535, E540)
- `Q135` usse, low: what does the high-word form of ima32, ima32 d, iK, a, b, c, do with immediates
  and constants other than c56, with cie on the same ... (E525, E526, E528)
- `Q136` usse, low: how long does a value written to sa0 last across jobs, and is the 0xff00ff00 and
  0xff203040 mixture that pa0 reads in the first jobs of a ... (E484, E496)
- `Q137` usse, low: do the rules of the test field of a class 9 test (zero part: bits 41 over 40;
  sign part: bits 43 over 42; the parts ANDed under join `a`, ... (E499, E529, E530)
- `Q146` usse, low: when does a load that is not waited for land, why did a load not waited for hold
  the loaded value after 40, 100 and 128 `nop` but not after ... (E517)
- `Q193` usse, low: what holds a temporary a task did not write: which earlier job's value does it
  read, per instance, and what clears it (a power cycle, a ... (E484, E485, E593)
- `Q195` usse, low: what do the narrow memory forms do that the 11.36 fills did not run: a register
  or negative offset, the pre- and post-increment forms, ... (E598, E599)
- `Q275` usse, low: why do g20, g41 and g42 read 0 in the end-of-tile task's per-tile stores of E708
  (the `[r4,+r5]` form, 8 temporaries, 128x128 and 256x128) ... (E374, E572, E708)
- `Q272` vdm, low: what makes three vertices of one job read as a constant row (E702: cap-n8-f10-a7,
  ids 55, 66 and 77 at R * V = 33 and 7 attribute rows; 3 ... (E702, E738, E755)
- `Q101` zls, low: what does bit 19 (the negated float) do with the integer stored formats
  (CR_ISP_ZLSCTL bits 26:24 = 1 and 2)? (E465, E466, E490)
- `Q242` zls, low: how is the 16-bit stored depth format laid out at a pitch G other than 33 and at
  an edge, what do the 24-bit and 16-bit formats store for a ... (E466, E490, E663)
- `Q243` zls, low: what does the ZLS load do with an integer stored format (bits 26:24 = 1 or 2), at
  an address other than the one the store writes, and when ... (E467, E628, E664)
- `Q004` transfer, fw (parked): can a transfer context whose flag bit 4 is set be released, which
  agent but the host sets flag bits 1 and 4, and which priorities above 0 ... (E015, E455)
- `Q029` render, fw (parked): what does the render context's own cleanup wait for once its RT data
  set is cleaned up (the PB is released by the PB step of the donor's ... (E354, E355, E449)
- `Q034` edm, fw (parked): does the EDM hold back a TA command whose destination sync is incomplete
  when another context is queued (source and transfer-queue syncs: ... (E161, E320, E450)
- `Q049` render, fw (parked): does the firmware or the hardware ever read dword 7 (offset 0x01c) of
  the render context, which the EDM dataflow reaches on no path? (E165, E361, E448)
- `Q084` dpm, fw (parked): how does the closed driver turn its PBSize app hint into the parameter
  buffer's page count and thresholds, given 1 MiB and 8 MiB both give ... (E327)
- `Q088` zls, fw (parked): what reads the render details' unpatched ZLS control word that the closed
  driver writes between frames (0x0011700a), now that bit 14 is ... (E337, E411, E467)
- `Q118` render, fw (parked): how does the firmware's kick tell that its context's page directory is
  in none of the bus interface's directory lists (a compare against ... (E360)
- `Q119` render, fw (parked): does one TA command carrying both FIRST_KICK and LAST_KICK act as two
  commands in the firmware (a kick and a closing kick)? (E156, E165)
- `Q277` dpm, fw (parked): what sets the fields of register 0x0740 that the TA kick turns into DPM
  store and load tasks (a host write reads back 0: E456; 0 in every ... (E312, E456, E574)
- `Q095` platform, kernel (parked): does giving the EDM a page directory of its own, rather than
  gma500's default one, change anything beyond the coupling of their teardowns? (E008, E018, E021)

## Recent records

89 records of 2026-11-11 to 2026-11-12 (the last 2 days to the newest record's date), newest first;
the claims are cut at 200 characters.

- `E921` usse, 2026-11-12: R7 session r7-faults stage L (Q111's lockup stop, read by R-6 as two
  `lock #0` and no release; E088's counter fill, 64 x 32, each pixel instance adding 1 to one
  scratch dword): with `lock #0` ... ...
- `E920` bif, 2026-11-12: R7 session r7-faults stage m (Q003; E848's held TA write fault at 288 x
  144, page 0x20006, with a manipulation while held, before the reset: none, CR_BIF_CTRL.CLEAR_FAULT
  set then cleared through ...
- `E919` bif, 2026-11-12: R7 session r7-faults stage d (Q003; E848's held 4x TA write fault, one
  array, at seven sizes whose fault pages are 0x2000a, 0x20006, 0x20008 and 0x20009, then the held
  reset and triangles until one ...
- `E918` dpm, 2026-11-12: R7-dpm stage s-k, set B, on module 37EC97AB after the lead's one-shot boot
  (Q210; our own task oomring2 armed before each of 10 jobs, logging pa1, sa8, sa9 and, new, the two
  DPM page status registers ...
- `E917` dpm, 2026-11-12: R7-dpm stage s-v, set A, on the test module 41E2F5C7 (Q210, larger
  objects; exploration, no verdict frozen: E900 froze no step rule for them): the 2048x2048
  calibration of the tool's triangle with ...
- `E916` dpm, 2026-11-12: R7-dpm stage s-b, set A, on the test module 41E2F5C7 (Q211; one default
  triangle moved to five places never run, one kick): held out, E875's page replay with the regions
  walked in E899's order ...
- `E915` dpm, 2026-11-12: R7-dpm stages s-a0 and s-m, set A, on the test module 41E2F5C7 (Q210; the
  tool's triangle with 1500 vertices, frozen from E874's step replay and E900's straddling-block
  rule H-SPAN): the premise ...
- `E914` isp, 2026-11-12: R7-geo stage zs (Q260; 230 jobs on 512 x 256, vertices in 1/4096 pixel, no
  fault): no frozen rounding is exact on the 143 held-out rows (half away from zero for negative
  coordinates, HA, and SETUP ...
- `E913` isp, 2026-11-12: R7-geo stage zf (Q240; 242 depth jobs, no fault): on ten targets E606 did
  not run, 64 x 128, 128 x 64, 256 x 64, 128 x 96, 128 x 144, 32 x 16 and 16 x 8 (below one tile),
  4096 x 16, and the odd ...
- `E912` isp, 2026-11-12: R7-geo stages zd and zi (Q262; 128 jobs on 512 x 256, 640 x 480, 1024 x
  768, 2048 x 1024 and 4096 x 4096, random triangles with vertices inside the target on the 1/256
  grid and depth planes of ...
- `E911` texture, 2026-11-12: R7-geo stage tx, type 5 (Q178; E725's 64 x 32 map-texture fill, dword
  i of the texture 0xD0000000 | i; 6 jobs, no fault): TEXTYPE 5 reads the texture memory: with the
  program zeroing the texture's ...
- `E910` texture, 2026-11-12: R7-geo stage tx, types 1, 3 and 4 (Q283; E725's 64 x 32 map-texture
  fill, dword i of the texture 0xD0000000 | i, pixel (x, y) sampling texel (x mod w, y mod h); 11
  held-out jobs and E725's type 3 ...
- `E909` transfer, 2026-11-12: R7-geo stage xf (Q206's both-fields clause, 10 fills at 128 x 64, no
  fault): with the fill's end-of-tile DOUTU1 x field (bits 11:3) and y field (bits 21:12) XORed in
  one poke, H-INDEP (each 32 x 16 ...
- `E908` ta, 2026-11-12: r7-rp stage q086 (Q086, 11 4x jobs on contexts made for 4x targets, module
  41E2F5C7): a 4x render with poked macrotile words completes exactly when their grid (B3 + B1 tiles
  per axis) covers the ...
- `E907` ta, 2026-11-12: r7-rp stage q139 (Q139, 24 TA-dump jobs at E877's missed macrotile cases,
  256 x 256 and 640 x 480): every case replicated its dataset's wrong-tile map (21 of 21), and the
  frozen H-MOVED, a tile is ...
- `E906` ta, 2026-11-12: r7-rp stage q293 (Q293, 4 jobs, three renders of one scene with CR_TE_AA
  0x40000000): the 3D reads render 2's own object as it reads render 1's: with the kernel's poke
  before render 3 putting render ...
- `E905` pds, 2026-11-12: r7-rp stages p7-rdc and p7-rd (Q276, 48 jobs, E878's readback rerun with
  the class share taken over the own-source words): in E709's command (state block word 4 at
  0x00030001) a `mov` from o1 to o3 ...
- `E904` zls, 2026-11-12: r7-rp stages q291g and q291 (Q291, 27 jobs with t6): the pixel tasks past
  the target run over the ZLS store's band and nowhere else, with the attribute iterated linearly
  there: with E898's ...
- `E903` zls, 2026-11-12: r7-rp stage q287 (Q287, 25 depth-dump jobs at H 18, odd widths through t7,
  the tool built from main 1c64f3a): at odd target widths the ZLS store's band past the target is
  rule A (x + 0.5 < 1.25 W), ...
- `E902` edm, 2026-11-12: Round 7 offline fold (Q111's 0x0694 clause and Q294): the six held TA jobs
  of r6-held were each the first render of a new context, so by the module's fork the kicks carried
  TA flag 0x1 (flags 0x73) ...
- `E901` bif, 2026-11-12: Round 7 offline reading of every kept kernel log of resgx545-data (Q003;
  post hoc scans, then one rule frozen as a fit and scored on r6-held, which the planner's scans had
  already read: SEMI, not ...
- `E900` dpm, 2026-11-12: Round 7 offline stage G3 and G5 to G7 (Q210; no run): for the tool's
  1500-vertex triangle the first partial render leaves 2 global pages iff S_k < thr0 < A_k, else 1,
  A_k being the page count of ...
- `E899` dpm, 2026-11-12: Round 7 offline stage G1, G2 and G4 (Q211; no run): the TA takes a
  region's 128-byte stream block walking the target in strips of 64 pixel rows, each strip in 64 x
  64-pixel blocks left to right and a ...
- `E898` usse, 2026-11-12: Round 7 offline, a program and tool record, no hardware run (Q291): the
  position-store pixel program pix_posstore.s (17 instructions, landed as
  probes/pds/templates/pix_posstore.s), assembled with ...
- `E897` ta, 2026-11-12: Round 7 offline reading of the kept parameter-buffer dumps (Q293; post hoc,
  nothing held out): in 13 of 13 kept two-object dumps of `tri --tri-full -n 2 --geometry 1` at 64 x
  64 with CR_TE_AA ...
- `E894` texture, 2026-11-12: Round 7 offline reading of E567's kept TEXTYPE 5 dumps (rt5-2d,
  rt5-3d-w5, rt5-3d-w15; a 16 x 16 texture whose dword i is 0xD0000000 | i, a 64 x 32 fill) [HW,
  post hoc]: no pixel of the 3 x 2048 ...
- `E893` ta, 2026-11-12: Round 7 offline decode of E504's dumps (Q142): with CR_TE_AA bit 29 set,
  bit 31 halves the TA's region width (32 to 16 pixels) and bit 30 its height (16 to 8), a macrotile
  keeping its pixel area and ...
- `E892` bif, 2026-11-12: R6 session r6-held part H stage q, the flush rows (Q003; the cells of E891
  with the r6 kernel's debugfs bif_flush, CR_BIF_CTRL.INVAL_DC set and cleared with the other bits
  kept, written while E848's ...
- `E891` bif, 2026-11-12: R6 session r6-held part H stage q, the list rows (Q003's health-triangle
  clause; E848's held 4x job on one array, a TA write fault BIF_INT_STAT 0x90004, then the debugfs
  reset, the cell's follow-up ...
- `E890` edm, 2026-11-12: R6 session r6-held part P (stage p1, E855's job on the r6 kernel with a
  debugfs peek of 0x0694; Q111, and the lockup rows of E855 to E857): the fill without the skip (b0,
  control) completed with the ...
- `E889` dpm, 2026-11-12: R6-render4x set B on the r6-kernel module (fork r6-kernel 3f0b3e74,
  srcversion 41E2F5C756F96D20F7109A4; 21 jobs, one attempt, 3 faults, all predicted): with four
  times the 4 side^2 tail room for a ...
- `E888` ta, 2026-11-12: R6-render4x set A, stage t (4 jobs, one attempt, no fault): Q293's held-out
  rows, 3 of 3 decided, the control passing (t8, E827's pb-e40-m2-64a with its hash): with CR_TE_AA
  0xc0000000 the TA inserts ...
- `E887` dpm, 2026-11-12: R6-render4x set A, stages s0 and a (16 jobs, one attempt, 6 faults, no
  stop): H-TPM held out, 11 of 11 rows decided: on the rgn4 module a four-array 4x job of the full
  triangle faults iff the end of ...
- `E886` ta, 2026-11-12: R6-misc stage q086 (Q086, 10 of 21 4x jobs run, 11 skipped by the frozen
  fault budget, one attempt): on contexts made for 4x targets (four region-header arrays) a render
  with CR_TE_MTILE1, ...
- `E885` zls, 2026-11-12: R6-misc stage q287 (Q287, 20 depth-dump jobs at W 34, rerun as a second
  attempt on freeze 2 after freeze 1's runner kept no dump): at odd target heights the ZLS store's
  band past the target is rule A ...
- `E884` transfer, 2026-11-12: R6-misc stage q289 (Q289, 23 fills, one attempt, no fault): with the
  fill's end-of-tile DOUTU1 x field (bits 11:3) or y field (bits 21:12) poked by XOR, M-OR (each 32
  x 16 tile t stored at (2t | f) ...
- `E883` dpm, 2026-11-12: R6-dpm stage r-b on the rgn4 module (Q211; 4096x4096, one default triangle
  moved to four new places, single kick): every frozen headline printed 'cannot tell', gated by
  r-a0's control without a ...
- `E882` dpm, 2026-11-12: R6-dpm stage r-v on the rgn4 module (Q210, the cause of the bursts;
  2048x2048, the tool's triangle with 1500 vertices and --vtx-coords 4 or 8, objects larger than
  E874's 67 dwords): the frozen ...
- `E881` dpm, 2026-11-12: R6-dpm stages r-a0, r-m, r-n and r-k on the rgn4 module (Q210; the tool's
  triangle with 1500 vertices; attempt a2 under freeze 2, after attempt a1 stopped in r-a0 on a
  runner slip): every frozen ...
- `E880` pds, 2026-11-12: R6-pixel stages p6-l3 and p6-s (Q276 and Q023, 8 and 22 jobs; frozen
  verdicts 'H-Y1; x jobs 5:1, 5:1 (frozen 5:1)' and 'H-OR: 5:3 5:2 5:2 5:3 5:2 5:2 5:2 5:2 5:0;
  restore check (r-u G-o1) PASS'): in ...
- `E879` ta, 2026-11-12: R6-pixel stages g6-rwa and g6-rw (Q230, 8 and 106 jobs in E859's shape with
  every vertex inside the viewport; frozen verdicts 'part a: PASS' and 'H-FRAC PASS (0 RZ + 1 of 117
  below 0.5); H-SMOOTH 2^1 ...
- `E878` pds, 2026-11-12: R6-pixel stage p6-rd (Q276, 58 jobs in E709's command: a triangle's pixel
  program writes R5's walk words to o0 to o7, then `mov.skipinv r10, oJ` and `mov.skipinv.end o0,
  r10`, so the own pixel shows ...
- `E877` ta, 2026-11-12: Round 6 offline reading of the kept images of Q100's macrotile-word pokes
  (Q139): all 67 wrong images (8 of ta/mtile-fields, 59 of ta/mtile-fields-risky) are wrong in whole
  32 x 16 tiles, no tile ...
- `E876` transfer, 2026-11-12: Round 6 offline reading of the two kept sweeps of the fill's
  end-of-tile DOUTU1 x field (bits 11:3, 512 cases) and y field (bits 21:12, 1024 cases) (Q289; post
  hoc, nothing held out): every job ...
- `E875` dpm, 2026-11-12: Round 6 offline replay of the partial-render count of one-triangle scenes
  (Q211; no numeric constant fitted, one walk order picked from a closed family of six on E832's 22
  g-qf cells, the rest SEMI ...
- `E874` dpm, 2026-11-12: Round 6 offline replay of the TA's page take for the tool's triangle with
  1500 vertices (Q210; read from kept dumps and timelines that had been seen, so post hoc and SEMI,
  nothing held out in the ...
- `E873` dpm, 2026-11-12: Round 6 offline reading of the kept DPM timelines (Q210, A2b; a reading
  rule applied to data already seen, post hoc, nothing held out): a step of the global page count
  between two samples of the ...
- `E872` ta, 2026-11-12: Offline fit and test on E859's kept 1/w words (Q230; no new job): the fit
  E859 left undone was run on the FIT mantissas only (every mantissa read except the 30 of the dense
  table E859's frozen hash ...
- `E871` pds, 2026-11-12: Offline reading of kept images (Q276; no new job, post hoc counts, no
  held-out row): in E709's command the own words of o4 to o7 reach no pixel of any kept image: in
  E858's walk rows w-4 to w-7, ...
- `E870` dpm, 2026-11-12: Round 6 offline reading of E869's held dump and of the 26 four-array 4x
  outcomes on record (Q292; post hoc, one dump, nothing held out): H-TPM, the tail pointers of a 4x
  job are one dword per tile of ...
- `E869` dpm, 2026-11-12: R5-render4x row d (1 held job): the 4x full triangle at 1280 x 1024 on its
  own maximum faulted with E845's word (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011), replicating
  E845, and the held dumps were ...
- `E868` dpm, 2026-11-12: R5-render4x stages l and x (8 jobs on their own maximum, 6 faults): the 4x
  full triangle on four arrays faulted with E845's word (BIF_INT_STAT 0x90100, BIF_FAULT 0x10000011)
  at 2048 x 240, 768 x ...
- `E867` dpm, 2026-11-12: R5-render4x stage m (5 jobs, 1 fault): the 4x full triangle on four
  arrays, at target sizes that fault on their own maximum (E845), completed with 0 wrong pixels on a
  context made for a larger ...
- `E866` dpm, 2026-11-12: R5-render4x stage o (11 jobs, no fault): the controls passed (the tool's
  default 1x triangle at 1024 x 768 completed at render_pb_pages 0x35 with 19 scene pages and
  overflowed at 0x34; the 4x full ...
- `E865` ta, 2026-11-12: R5-render4x stages s0 and t (12 jobs, one attempt, no fault): s0's three
  controls passed as frozen (1x 1024 x 768 hash 0xc9e301d225fe2325, 4x 288 x 144 0x4a61860dcb4ab325,
  4x 1024 x 768 ...
- `E864` dpm, 2026-11-12: R5-dpm stage d-a3 on the rgn4 module (Q210; 2048x2048, the tool's triangle
  with 1500 vertices, our own firmware task oomring armed in the four event slots, logging pa0, pa1,
  sa8, sa9 and CR_TIMER at ...
- `E863` dpm, 2026-11-12: R5-dpm stage d-b on the rgn4 module (Q211; 4096x4096, one triangle of the
  tool, single kick): the five g-qf controls repeated E832's counts (9, 4, 3, 2, 1 at P 0x24, 0x53,
  0x54, 0xa2, 0xa3; 10 of 10 ...
- `E862` dpm, 2026-11-12: R5-dpm stage d-t on the rgn4 module (Q210; exploratory; 2048x2048, the
  tool's triangle with 1500 vertices, thr0 S3 - 7 to S3 - 4 = 0x96 to 0x99 and S5 - 7 to S5 - 4 =
  0x12b to 0x12e): the global ...
- `E861` dpm, 2026-11-12: R5-dpm stages d-a2 and d-a2b on the rgn4 module (Q210; the tool's triangle
  with 1500 vertices, cells picked by frozen rules from the session's own calibrations, none run
  before): at 2048x2048 and ...
- `E860` dpm, 2026-11-12: R5-dpm stages d-a0 and d-a1 on the rgn4 module (Q210; 2048x2048 and
  4096x4096, the tool's triangle with 1500 vertices, thr0 = P - 0x22 read back from the job's own
  0x0624, 16 registers sampled with ...
- `E859` ta, 2026-11-12: R5-pixel stages g5-rwa and g5-rw (Q230, 12 and 36 jobs in E842's shape with
  every vertex inside the viewport; frozen verdicts 'part a: PASS' and 'H-MANT held: 42 of 42 m
  words equal R4's delta at ...
- `E858` pds, 2026-11-12: R5-pixel stage p5-o4 (Q276, 58 jobs in E838's shape: a triangle's pixel
  program writing tagged words to o0 to o7 in E709's command, state block word 4 at 0x00030001;
  frozen verdict 'the tag-5 word is ...
- `E857` edm, 2026-11-12: R5 stage h3 (r5-events, ring_skip3p.s at timer_clock 1600000; Q295, Q166):
  the fill without the skip (b0, control) completed with the tick alive and bit 18 never set; with
  slot 3's first ...
- `E856` edm, 2026-11-12: R5 stage h2, the dose (r5-events, ring_skip3p.s; Q295): with HostCtl dword
  6 set through the timer_clock knob to 800000 and to 1600000 (read back and read in each arm dump),
  the fill without the skip ...
- `E855` edm, 2026-11-12: R5 stage h1 (r5-events, ring_skip3p.s of E836 at the stock timer_clock;
  Q295, Q166): the fill without the skip (b0, control) completed with the tick alive, bit 18 never
  set and HostCtl dwords 3 and 8 ...
- `E854` dpm, 2026-11-12: Round 5 offline fit of the partial-render count (Q211; a FIT, nothing held
  out by a frozen prediction): for the tool's triangle at 4096x4096 the count n at the first
  threshold thr0 = P - 0x22 fits n ...
- `E853` dpm, 2026-11-12: Round 5 offline test of R-5's guard of the firmware's raise (Q210, Q211):
  the guard as written on 2026-11-11 (closing4/p7/guard.py, imported unchanged) on the kept
  timelines of R3-geo-c that R-5 ...
- `E852` dpm, 2026-11-12: Round 5 offline reading of the kept DPM timelines (Q210; post hoc, a FIT
  on one positive, nothing held out): in the first TA run of every kept job the high half of 0x072c
  (the global page count) ...
- `E851` ta, 2026-11-12: Offline reading of E842's kept words (Q230; no new job): the frozen
  analysis of g4-rw is decided without its 18 unread words: its rule adopts a model only at 30 of 30
  FIT words, and none of the 225 ...
- `E850` pds, 2026-11-12: Offline reading of kept images (Q276; no new job, post hoc against E838's
  reading, no held-out row): E838's reading 'the path that brings o4 out clears bits 5:3 of the
  word' is refuted on the kept ...
- `E849` edm, 2026-11-12: Read offline after the hypothesis (post hoc, no frozen prediction; round 5
  plan closing5/events, step F0): E836's b1p stop dump, taken at the stop's signature before the
  host's clears, holds HostCtl ...
- `E848` bif, 2026-11-11: R4-render4x stage h (4 held cells, each a 4x job on one array of region
  headers that faulted with a TA write, BIF_INT_STAT 0x90004, as frozen, then the debugfs reset, the
  cell's follow-up and health ...
- `E847` ta, 2026-11-11: R4-render4x stage t (7 jobs, 64 x 64): the frozen verdict for Q293 is
  cannot tell, because its two baseline controls (the line and the point object of the 11.31
  sessions without a poke) are NODATA: ...
- `E846` dpm, 2026-11-11: R4-render4x stage o (7 of 8 jobs run, o6 skipped by its condition): the
  frozen verdict is cannot tell for Q292 and for H-SPM4 because the control o2 (1x 1024 x 768 at
  render_pb_pages 0x82, frozen to ...
- `E845` dpm, 2026-11-11: R4-render4x stages s0 and p: the three controls reproduced as frozen (1x
  1024 x 768 hash 0xc9e301d225fe2325; 4x 288 x 144 hash 0x4a61860dcb4ab325, 12 parameter pages; 4x
  1024 x 768 hash ...
- `E844` texture, 2026-11-11: R4-render4x stage c (3 probe fills of 64 x 32, TEXTYPE 2 sampled with
  smp3d): E726's own cu-xn program, run again as the control, read face 1 (-x) on 2048 of 2048
  pixels with E726's pixels byte for ...
- `E842` ta, 2026-11-11: R4-pixel stage g4-rw (Q230, 24 jobs: R2's t3-nocut shape, z = 0 and w = C x
  + D on the tool's three vertices, a table of 60 w split 30 FIT and 30 HELD OUT by the sha256 of
  their bits before the run): ...
- `E841` edm, 2026-11-11: R4-pixel stage q4-t (Q082 bit 6 in triangles, 54 jobs: E806's relative
  8-instruction loop with a MARK as the pixel program of the tool's triangle covering a W x H
  target, `--tri-full`): the 12 ...
- `E840` edm, 2026-11-11: R4-pixel stage q4-f (Q082 bit 6, 16 fills of 64 x 32 whose pixel program
  ends in a MARK only when its loop counters end): the five bridge controls to E804 and E805 passed
  on the rgn4 module (the ...
- `E839` edm, 2026-11-11: R4-pixel stage q4-v (Q082 bit 7, 28 jobs, 27 scored: a vertex program on
  the tool's triangle looping N times on a relative br, the stored depth word 0x3f200000 + N the
  loop proof, every job under ...
- `E838` pds, 2026-11-11: R4-pixel stage p4-o4 (Q276, 36 jobs in E808's p-c3 shape: a triangle's
  pixel program writing tagged words to o0 to o7 in E709's four-output setup, the words at bits 3:0,
  a job marker at bits 15:6, x ...
- `E837` platform, 2026-11-11: R4 stage e3p, the status bits (r4-events, the same two jobs as E836;
  Q166, Q111): in b0 (the fill without the skip, control) CR_EVENT_STATUS read 0x20000000 in 9 of 9
  watch reads from the slot 3 ...
- `E836` edm, 2026-11-11: R4 stage e3p, the end of the pass (r4-events, ring_skip3p.s, 2 of its 4
  jobs run, the stage ended by its stop rule at its first B1P; Q152's slot 3 clause): the fill
  without the skip (b0, control, ...
- `E835` edm, 2026-11-11: R4 stage kp (r4-events, 4 jobs of ring_exit2.s, no stop; Q152): with the
  controls passing (e0, 14 entries on the 25000-unit grid, nothing acted; fk, a plain tick pass
  ended idf, wdf, phas #0, #0, ...
- `E834` edm, 2026-11-11: R4 stage kb2 (r4-events, 10 jobs of ring_hold.s, each a reset and an arm,
  the writes made before the logging window and one miscinfo 1 ms after it opened, no stop; Q290):
  the ordinary kicks (g0p x2, ...
- `E833` usse, 2026-11-11: Converted from the published closing-pass sessions (R3-pixel, R3-geo,
  R3-geo-c, R3k-pixel) as vectors, sgx-sim replays all 204 pixel-loop proofs of R3-pixel (q-f0 10,
  q-f1a 54, q-f1b 54, q-t 86) and ...
- `E830` edm, 2026-11-11: R4-B stage fr (Q152 replicate of E817's FCF, 21 jobs in 3 blocks and 3
  recoveries, ring_exit.s as in E817, module srcversion 99CD90DA, no reset between the arm and fcf
  in a block, one stop a block): ...
- `E829` isp, 2026-11-11: R4-A stages a-pb0 and a-pb (Q285 rerun, 8 jobs, split flow -n 2 --geometry
  1 at 64 x 64, CR_TE_AA 0x40000000, forced render_rgn_arrays 1, module srcversion 99CD90DA,
  controls frozen from E827's ...
- `E828` ta, 2026-11-11: R3-rgn4 (the laptop check of the linux fork's 4x render contexts, fork
  resgx545 a2788bd8, module srcversion 99CD90DA): at render_rgn_arrays 0 (automatic) a 288 x 144 job
  at CR_TE_AA 0xe0000000, mode ...

## Closing sessions

31 published sessions (dataset manifests of `<area>/closing-*`), newest first: date, module
srcversion, fork tip, laptop tools.

- `render/closing-r7-rp`: 2026-11-12; module 41E2F5C756F96D20F7109A4; tools ~/sgxfive-test-rgn4
- `render/closing-r7-geo`: 2026-11-12; module 41E2F5C756F96D20F7109A4; tools ~/sgxfive-test-rgn4
- `render/closing-r7-faults`: 2026-11-12; module 41E2F5C756F96D20F7109A4; fork r6-kernel at
  3f0b3e74; tools ~/sgxfive-test-rgn4
- `render/closing-r7-dpm`: 2026-11-12; module 41E2F5C756F96D20F7109A4; tools ~/sgxfive-test-rgn4
- `render/closing-r6-render4x`: 2026-11-12; module 41E2F5C756F96D20F7109A4, 99CD90DA26E3AFF9C450517;
  fork r6-kernel at 3f0b3e74, resgx545 at a2788bd8; tools ~/sgxfive-test-rgn4
- `render/closing-r6-pixel`: 2026-11-12; module 99CD90DA26E3AFF9C450517; tools ~/sgxfive-test-rgn4
- `render/closing-r6-misc`: 2026-11-12; module 99CD90DA26E3AFF9C450517; tools
  ~/scratch/r6m/bin/sgxfive-test, ~/sgxfive-test-rgn4
- `render/closing-r6-held`: 2026-11-12; module 41E2F5C756F96D20F7109A4; fork r6-kernel at 3f0b3e74;
  tools ~/sgxfive-test-rgn4
- `render/closing-r6-dpm`: 2026-11-12; module 99CD90DA26E3AFF9C450517; fork resgx545 at a2788bd8;
  tools ~/sgxfive-test-rgn4
- `render/closing-r5-render4x`: 2026-11-12; module 99CD90DA26E3AFF9C450517; fork resgx545 at
  a2788bd8; tools ~/sgxfive-test-rgn4
- `render/closing-r5-pixel`: 2026-11-12; module 99CD90DA26E3AFF9C450517; tools ~/sgxfive-test-rgn4
- `render/closing-r5-dpm`: 2026-11-12; module 99CD90DA26E3AFF9C450517; fork resgx545 at a2788bd8;
  tools ~/sgxfive-test-rgn4
- `edm/closing-r5-events`: 2026-11-12; module 99CD90DA26E3AFF9C450517; fork resgx545 at a2788bd8;
  tools ~/sgxfive-test-s1b
- `render/closing-r4-render4x`: 2026-11-11; module 99CD90DA26E3AFF9C450517; fork resgx545 at
  a2788bd8; tools ~/sgxfive-test-rgn4
- `render/closing-r4-q285`: 2026-11-11; module 99CD90DA26E3AFF9C450517; fork resgx545 at a2788bd8;
  tools ~/sgxfive-test-rgn4
- `render/closing-r4-pixel`: 2026-11-11; module 99CD90DA26E3AFF9C450517; fork resgx545 at a2788bd8;
  tools ~/sgxfive-test-rgn4
- `render/closing-r3-rgn4`: 2026-11-11; module 99CD90DA26E3AFF9C450517; fork resgx545 at a2788bd8;
  tools ~/sgxfive-test-rgn4
- `edm/closing-r4-q152`: 2026-11-11; module 99CD90DA26E3AFF9C450517; fork resgx545 at a2788bd8;
  tools ~/sgxfive-test-s1b
- `edm/closing-r4-events`: 2026-11-11; module 99CD90DA26E3AFF9C450517; fork resgx545 at a2788bd8;
  tools ~/sgxfive-test-s1b
- `render/closing-r3k-regress`: 2026-11-10; module 230E0EF50FFFD606C53AE3C; tools ~/sgxfive-test-r1
- `render/closing-r3k-pixel`: 2026-11-10; module 230E0EF50FFFD606C53AE3C; tools ~/sgxfive-test-r1
- `render/closing-r3-pixel`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-r1
- `render/closing-r3-geo-c`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-r1
- `render/closing-r3-geo`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-r1
- `render/closing-r2-pixel`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-r1
- `render/closing-r2-geo`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-r1
- `render/closing-r1-pixgeo`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-r1
- `edm/closing-r3x-events`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-s1b
- `edm/closing-r3x-c3`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-s1b
- `edm/closing-r3k-events`: 2026-11-10; module 230E0EF50FFFD606C53AE3C; tools ~/sgxfive-test-r1,
  ~/sgxfive-test-s1b
- `edm/closing-r3-events`: 2026-11-10; module B21FDA82BD5E5CB5A627E3B; tools ~/sgxfive-test-s1b

## Tool and fork versions

- fork pin (`tools/forkpin.py`): 664fd0d00765
- module srcversion 41E2F5C756F96D20F7109A4: last named 2026-11-12, 6 sessions, fork r6-kernel at
  3f0b3e74
- module srcversion 99CD90DA26E3AFF9C450517: last named 2026-11-12, 14 sessions, fork resgx545 at
  a2788bd8
- module srcversion 230E0EF50FFFD606C53AE3C: last named 2026-11-10, 3 sessions
- module srcversion B21FDA82BD5E5CB5A627E3B: last named 2026-11-10, 9 sessions
- `tools/closing/scorekit.py` sha256 cc918255382e022e
- `tools/closing/sessioncheck.py` sha256 6816ff3f316ba139

## Known tool weaknesses

From HACKING.md, "Known tool weaknesses":

Weaknesses of our tools that a session or a fold has found and that are not fixed yet. Each
round reviews this list: an entry leaves it with the commit that fixes it (and its test), or
stays with what a session must do around it.

- `tri --depth` (`userspace/libsgxfive/tools/sgxfive-test.c`): `depth_min_pages` sizes the
  depth buffer, and the floor of `--depth-pages`, as W x H dwords, below the depth store's tile
  extent (tiles of 32 x 16), so a target that is not a whole number of tiles gets fewer pages
  than the store writes, `DEPTH_MARGIN_PAGES` aside (found by closing7/r7-rp's builder).
- sgx-sim refusals that block oracles: the sim refuses what is not modelled, and some of those
  refusals stop a replay that would otherwise serve as an oracle, e.g. `0x0728` and the `pclink`
  path before E902's seeds. A session that needs the sim as an oracle checks first that its
  path does not hit one.

## Simulator coverage baseline

125 entries in `crates/SIM_UNMODELLED.toml` (what the simulator does not model).
