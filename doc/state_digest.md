<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# State digest

*Generated from the tracked tree by `tools/records/digest.py`; do not edit.*

Where the project stands, on one page: the open questions, the newest records, the published closing
sessions, the tool and fork versions, the known tool weaknesses and the simulator's unmodelled
baseline. The records, questions and manifests themselves hold the detail.

## Open questions

136 open: 126 hw, 10 parked. Each with its unit, value and the last three records of its evidence
list.

- `Q076` bif, high: which pages does each bus-interface requestor of a render (the TA, the 3D, the
  EDM's PB load) need in the directory of the list it ... (E745, E761, E980)
- `Q191` dpm, high: what are the words that land in a kept owner's control page (0x00200047), OTPM
  page (0x04000417) and state page (0x00020001, 2) after the ... (E1091, E1092, E1100)
- `Q210` dpm, high: why does band 6's margin end at the page count once the object after the
  straddling block (b_6 + 1) is tiled (E960, E961: held out at four ... (E963, E1009, E1013)
- `Q211` dpm, high: does E874's replay give the need of wide scenes of other vertex counts than 1500
  (E630's 300 to 900; at 1500 it gave the need of four ... (E960, E962, E963)
- `Q066` isp, high: what do the three background-object words the 3D kick writes mean to the ISP,
  and what are the other words of a render's background object? (E972, E973, E1006)
- `Q089` isp, high: where does the closed driver's 4x multisampled render become a 64x64 image, when
  its PBE words are those of a single-sampled 64x64 target ... (E510, E727, E893)
- `Q200` isp, high: why do the dyadic controls of E731 store one or two ulps below the truncated
  exact plane, below binade 0, in a region bounded by a diagonal ... (E758, E912, E913)
- `Q202` isp, high: do the attribute and depth planes of E606 hold with perspective (w other than
  1), which arithmetic forms the window x / w (an exact divide, ... (E979, E990, E992)
- `Q260` isp, high: the tie of a negative window coordinate 1/512 above the 1/256 grid rounds away
  from zero wherever the aimed pixel is clear of E914's band ... (E943, E952, E984)
- `Q023` pds, high: how many output dwords does a pixel task get per setup, and what do the data
  rows limit (E406) (E742, E759, E880)
- `Q276` pds, high: in E709's command (state block word 4 at 0x00030001), why is the o3 word in the
  tag-5 OR that of lane 0 of the quad in a job whose words ... (E878, E880, E905)
- `Q111` platform, high: which hardware event sets which bit of CR_EVENT_STATUS and CR_EVENT_STATUS2
  in an ordinary TA, 3D, DPM or transfer job, and how long does ... (E1121, E1122, E1123)
- `Q070` ta, high: what do the TA object's format word bits 15:8 and above and its set masks select
  beyond the settings seen, and does the fitted region test ... (E543, E544, E777)
- `Q050` usse, high: what do the visibility group's instructions do, and how do smp's mipmaps and
  LOD values, the border address modes, the compressed and YUV ... (E568, E1097, E1103)
- `Q047` vdm, high: what do VDM_STATE1 bit 8, bits 11:9 and bits 15:13 select for a state task, when
  on the one-triangle job bit 8 changes nothing, bits 11:9 ... (E427, E440, E545)
- `Q108` bif, medium: what do the page table entry flags WRITEONLY, CACHECONSISTENT and EDMPROTECT
  do on the hardware, which of the bus interface's requestors do ... (E1046, E1071, E1108)
- `Q081` dpm, medium: what does CR_DPM_REG_074C bit 8 make the DPM read or write near offset 0x6010
  of the context's TA-data space, and what fixes that place? (E313, E362, E447)
- `Q082` edm, medium: what does CR_EVENT_STATUS2 bit 6 follow in a pixel task (a fill without a
  load: a tile's time near 125 us, E805; a program that waits on a ... (E839, E840, E841)
- `Q031` isp, medium: why does ISP word 0 bit 28 hang a multisampled render, when single-sampled it
  widens coverage to the union of eight samples? (E215, E278, E416)
- `Q032` isp, medium: what does pcoeff hand the ISP in the punch-through pass, when the kept pixels'
  depth is the same without it and moves between runs only ... (E217, E416)
- `Q071` isp, medium: what do the bits of the ZLS control word that change nothing seen (12, 15, 16,
  20 to 23, 27 to 31) do, alone and set together, what does ... (E1069, E1088, E1093)
- `Q073` isp, medium: what does o0 hold at the start of an opaque pass's pixel shader? (E417, E739,
  E757)
- `Q240` isp, medium: does the coverage rule of E606 (vertices on the 1/256 pixel grid, exact centre
  test, left and top edges owning ties) hold for random ... (E682, E912, E913)
- `Q262` isp, medium: what bounds the error of the stored depth and of the iterated clip z on E680's
  targets, where E606's tolerances fail for some triangles of ... (E684, E912, E913)
- `Q288` isp, medium: what rule gives the stored depth of a plane with a non-dyadic gradient in x
  (class b and c of E731) when the tile-corner value T by ... (E606, E731, E740)
- `Q039` mte, medium: where is a user clip plane's state held between jobs, what resets it, and when
  do the vertex's distance dwords decide a plane? (E198, E280, E418)
- `Q069` mte, medium: what do OUTSEL bit 13 and the state block's presence bits 16-31 select, and
  why does the viewport's z offset (state-block word 10) scale ... (E981, E987, E1066)
- `Q012` pbe, medium: what float formats are pack modes 22 and 34, given that both read o0 as an
  IEEE single (sign, NaN and exponent) and store it at some of the ... (E387, E406, E429)
- `Q040` pbe, medium: what do EMIT2 bits 15:8 count, given that 4v pixels of each tile are stored
  for an even v up to 0x80, odd values hang and values above 0x80 ... (E266, E267, E382)
- `Q046` pbe, medium: what are the words sideband bit 12 stores in pack modes 0 to 6 (post hoc,
  E1028 and E1034: a high half fixed pixel for pixel, a low half ... (E999, E1028, E1034)
- `Q074` pbe, medium: why does a second end-of-tile emit in a tile leave the next job's image wrong,
  and does SIDEBAND bit 9 mark an emit that counts against a ... (E239, E240, E386)
- `Q019` pds, medium: what does the secondary attribute size (bits 24:18 of dword 1 of the
  background object) limit, given that a fill's douta reaches attributes ... (E391, E1096, E1104)
- `Q020` pds, medium: what does a douta in the triangle's primary pixel program do, when its markers
  never reach the USE task and the readback is the memory ... (E381, E440, E545)
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
- `Q139` ta, medium: what is the stride's relation to the RT data, and what places the TA's region
  header write of a macrotile word with an axis whose bounds ... (E1073, E1074, E1109)
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
- `Q284` texture, medium: what does a TEXTYPE 2 cube sample read at an exact texel boundary when
  |ma| is not a power of two (E923, E931, E956: up or down by the ... (E956, E1001, E1002)
- `Q300` texture, medium: what does a texture sample read and return for the sampler words, formats,
  sizes and modes that sgx-sim's tex::sample refuses, where a ... (E1058, E1067, E1105)
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
- `Q036` vdm, medium: what do the DPM's status words hold (0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS'
  high half, and the owner words 0x0700 to 0x0728 a kept owner ... (E1032, E1044, E1057)
- `Q042` vdm, medium: what do bits 27:24 of the index list's first trailing word (VDM_INDEX2) do,
  when its low bits move the list's first index and 0x0f000000 ... (E307, E308, E414)
- `Q092` vdm, medium: what do bits 31:28 of the index list's first trailing word count, which the
  closed driver writes as 0xf on 1886 captured lists and 0xd on a ... (E348, E414, E546)
- `Q112` vdm, medium: what do bits 25:24 of the index list header do, which are clear in all 1888
  captured lists, and does the TA take indices wider than the 16 ... (E737, E756, E1075)
- `Q163` vdm, medium: what is the state the jobs leave that decides whether a job with VDM_STATE1
  bits 11:9 other than 2 hangs (E700: a counter c, cleared by a ... (E1035, E1076, E1113)
- `Q107` zls, medium: why does the final render of a job that overflows store zeros for the first
  row of macrotiles and the depth with its sign bit set for the ... (E1088, E1090, E1095)
- `Q120` zls, medium: what do the stored depth formats 3 to 7 (CR_ISP_ZLSCTL bits 26:24) hold and
  how are they laid out, given that they store depth and stencil ... (E1031, E1043, E1054)
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
  hang for 49 and 64; E550 armed 32 to 48 with trc_hazard=1 and ... (E540, E550, E603)
- `Q194` edm, low: does a load that is not waited for land by itself in a firmware (EDM) task, at
  what distance, and is that a property of the task, of the ... (E517, E602)
- `Q196` edm, low: do the client results of 11.36 for the compare and the high word of ima32 (E595,
  E597), the predicated register moves and ba (E596) and the ... (E599, E600, E601)
- `Q290` edm, low: what does a write to CR_EVENT_KICK with the kicker word unchanged start in the
  EDM (E834: no event and no command read, before or after a ... (E819, E834, E835)
- `Q294` edm, low: which of bits 4, 7 and 10 of the sa65 word of E537 (0xb009c5dc, without bit 8)
  stop the tick through the closed task (E814: that word ... (E812, E814, E902)
- `Q072` isp, low: what does bit 1 of CR_ISP_REG_04DC do to a punch-through pass, when it hangs
  every one tried and changes no opaque or translucent pass? (E222, E290, E416)
- `Q241` isp, low: what does ISP word 0 bit 15 keep (E065: 48 pixels of the library's triangle;
  E1045 and E1056: bits 15 to 17 select no winding, and bits 16 ... (E1045, E1056, E1072)
- `Q044` pbe, low: what do bits 11:0 of CR_REG_0400 (0x80 as built) do, when no value of them
  changes a stored pixel in pack modes 0 to 3, and does bit 25 act ... (E251, E268, E385)
- `Q013` pds, low: what does bit 18 of the copy's pixel-event data word 2 do, when it leaves the
  copy unchanged and changes a few pixels of the fill and the ... (E043, E046, E388)
- `Q024` pds, low: does CR_PDS_REG_0A78 change timing, when two of its values were slower in one
  timing run? (E1114, E1124, E1125)
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
- `Q010` texture, low: which job clears colour-space set 0 between jobs, given that a copy that does
  not load it converts with the last loaded words across a ... (E1097, E1103, E1112)
- `Q115` texture, low: does the sampler filter anisotropically on this core, and which bits of the
  texture words or the smp operands select it and its ratio? (E564, E720, E723)
- `Q177` texture, low: which dword do texture types 1, 3 and 4 read, each byte halved, in u address
  modes 4 to 7 at a size other than 16 x 16 and 32 x 32 (E1055's ... (E1039, E1055, E1065)
- `Q179` texture, low: how are the blocks and the data bits of formats 23 to 26 laid out (a data bit
  changes 7 to 13 pixels, the blocks of 23 and 24 do not differ ... (E342, E568, E724)
- `Q280` texture, low: what makes up to 56 of 2048 pixels of a gradient job differ from the
  Euclidean footprint of the pairs (op0, op2) and (op1, op3) with a LOD ... (E563, E721, E744)
- `Q017` usse, low: why does g19 read 0x1a as a store's source but 0 through a mov and as the pixel?
  (E085, E086, E372)
- `Q048` usse, low: do the MADD0 and MADD1 clock gates follow the USSE pipes' floating-point
  arithmetic, or their cache and texture traffic? (E365, E445, E452)
- `Q080` usse, low: what do the USSE words no form decodes (classes 2, 22 and 26) do: which stop the
  stores after them, and which write registers? (E297, E368)
- `Q125` usse, low: which code leaves 0xeb3 and 0x98 in pclink and 1101, 0101, 0001 or 1111 in p0-p3
  of the instances that do not read the last job's value, ... (E477, E484, E500)
- `Q127` usse, low: what do the extra i register of ima32, ima32 as a dual-issue secondary, and imae
  with a repeat, a u16 or z16 source or a .rsN shift do with ... (E528, E595, E597)
- `Q129` usse, low: why do 12 pixels (4 each of three values) of every fill that writes sa1, sa5 and
  sa7 show those sa values as their output, and how long ... (E484)
- `Q130` usse, low: when does a load on one counter land while a wdf waits on another: why four ldad
  on drc0 issued after a wdf drc1 that waited for four ldad ... (E479)
- `Q133` usse, low: what bounds a phas request (it runs when T mod 256 is 4 to 192 and hangs the job
  when it is 0 or 196 to 252, whatever the task was started ... (E535, E540, E594)
- `Q136` usse, low: how long does a value written to sa0 last across jobs, and is the 0xff00ff00 and
  0xff203040 mixture that pa0 reads in the first jobs of a ... (E484, E496)
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
- `Q118` render, fw (parked): how does the firmware's kick tell that its context's page directory is
  in none of the bus interface's directory lists (a compare against ... (E360, E592)
- `Q119` render, fw (parked): does one TA command carrying both FIRST_KICK and LAST_KICK act as two
  commands in the firmware (a kick and a closing kick)? (E156, E165)
- `Q277` dpm, fw (parked): what sets the fields of register 0x0740 that the TA kick turns into DPM
  store and load tasks (a host write reads back 0: E456; 0 in every ... (E312, E456, E574)
- `Q301` zls, fw (parked): what does the closed driver write the unpatched ZLS control word
  0x0011700a into the render details for between frames, and why does a ... (E1093, E1094, E1101)
- `Q095` platform, kernel (parked): does giving the EDM a page directory of its own, rather than
  gma500's default one, change anything beyond the coupling of their teardowns? (E008, E018, E021)

## Recent records

36 records of 2026-11-15 to 2026-11-16 (the last 2 days to the newest record's date), newest first;
the claims are cut at 200 characters.

- `E1125` pds, 2026-11-16: r31-kreg2 on module 7CE8E38E (Q024), stage k2, cannot tell by its frozen
  premise: CR_PDS_REG_0A78 at each of its 64 values on two shuffled passes before a job of six
  renders of 500 small triangles ...
- `E1124` pds, 2026-11-16: r31-kreg2 on module 7CE8E38E (Q024), stage k1: CR_PDS_REG_0A78 written to
  each of its 64 values 0x00-0x3f on two shuffled passes before a 256x256 triangle job of six
  renders; by the frozen rule (the ...
- `E1123` platform, 2026-11-16: r31-cc on module 7CE8E38E (Q111, the fwsim read of CR_CACHE_CTRL
  after a kick), stages c4 (CR_EVENT_STATUS, CR_CACHE_CTRL, CR_DMS_CTRL, CR_USE0_SERV_EVENT and
  CR_BIF_CTRL at 1766 to 1789 ns a sample, ...
- `E1122` platform, 2026-11-16: r31-cc on module 7CE8E38E (Q111, the fwsim read of CR_CACHE_CTRL
  after a kick), stages c1, c2, c3 (CR_CACHE_CTRL alone at 540 to 542 ns a sample, with
  CR_USE0_SERV_EVENT, with CR_BIF_CTRL, both at ...
- `E1121` platform, 2026-11-16: r30-evst2 on module 7CE8E38E (Q111), stages e1 and e5
  (CR_EVENT_STATUS alone at 539 to 548 ns a sample, every control passed, every row held out against
  E1115): CR_EVENT_STATUS reads 0x20000000 ...
- `E1120` platform, 2026-11-16: r30-evst2 on module 7CE8E38E (Q111, the fwsim read rules), stages
  e2, e3, e4 (CR_EVENT_STATUS with CR_EVENT_STATUS2, CR_CACHE_CTRL and CR_USE0_SERV_EVENT, and with
  27 registers), every control ...
- `E1119` bif, 2026-11-16: r30-pde stage f67 (Q109, a size field the BIF does not take; every s0
  control passed): a client directory entry with the unnamed size codes 6 and 7 is walked as 4 KiB
  entries like codes 0 to 5: four ...
- `E1118` bif, 2026-11-16: r30-pde stages f2 and f45 (Q109, the table's layout and address bits,
  every s0 control passed): over codes 1 to 4 a table laid out with each entry 4 KiB past its block
  (misalign) and a table at + ...
- `E1117` bif, 2026-11-16: r30-pde stages s0, f1 and f45 (Q109, module 7CE8E38E, every control
  passed): a client page directory entry whose size field (bits 3:1) names 16 KiB, 64 KiB, 256 KiB,
  1 MiB or 4 MiB (codes 1 to 5), ...
- `E1116` platform, 2026-11-16: r30-evst on module E0CC4027, stages e2, e3, e4 (CR_EVENT_STATUS with
  CR_EVENT_STATUS2, CR_CACHE_CTRL and CR_USE0_SERV_EVENT, and with 27 registers), readings only, no
  verdict: every frozen headline ...
- `E1115` platform, 2026-11-16: r30-evst on module E0CC4027 (Q111), stages e1 and e5
  (CR_EVENT_STATUS alone at 541 ns a sample, every control passed): in plain 64x64 triangles
  CR_EVENT_STATUS reads 0x20000000 in every sample ...
- `E1114` pds, 2026-11-16: r29-kreg on module E0CC4027 (Q024), readings only, no verdict:
  CR_PDS_REG_0A78 written to each of its 64 values 0x00-0x3f on two shuffled passes before a 256x256
  triangle job of six renders; the mean ...
- `E1113` vdm, 2026-11-16: r29-flag2 stage h2 (Q163, 9 rows of E700's two-block stream on t10 in
  three triples from a reset, the kit's noreset, 2 planned hangs): a block-2 v = 1 job completed at
  c = 8 after (6,2) (h2-a3) and ...
- `E1112` texture, 2026-11-16: r29-flag2 stage h1 and h2's first row (Q010, 7 copies on t22 and
  E737's bit-24 hang twice on t10, 2 planned hangs, both recovered): a copy without the load read
  black 0xd3522437a14b6325 after each ...
- `E1109` ta, 2026-11-16: r29-flag stage f2 (2 jobs, t10, E1074's form at 512 x 512 (n = 2, TA data
  32768 bytes by the kernel's layout, c-512's reading), the size's own CR_TE_MTILE1 and CR_TE_MTILE2
  with B2 cleared, words ...
- `E1108` bif, 2026-11-16: r29-flag stage f1 (2 jobs, t14, the debugfs knobs vm_pte_addr and
  vm_pte_flags = 0x12, WRITEONLY and EDMPROTECT together, on a mapping only read, held out; 2
  planned faults): r14-bif's ZLS load of ...
- `E1107` pds, 2026-11-15: sgx-sim replays the kept vectors of two published sessions exactly:
  r25-sa64's 58 jobs (E1104; stages pk64 and q019, one vector a job) replay 58 of 58 with each set's
  sixteen markers read exactly at ...
- `E1106` usse, 2026-11-15: r26-sa0 stages uc and us (8 jobs, t24 `probe --coords`) on module
  E0CC4027: a single writer alone writes iaddu32's value into sa0 and it is the zero-extended one:
  eight (r1, source 2) pairs a ...
- `E1105` texture, 2026-11-15: r26-vol on module E0CC4027 (Q114): with each of 19 sampler-word bits
  flipped one at a time on E567's twiddled 16 x 16 format 12 texture (T0 bits 14, 15, 16, 27, 28,
  29, 30; T3 bits 8, 9, 10, 11, 12, ...
- `E1104` pds, 2026-11-15: r25-sa64 stages pk64 and q019 (58 jobs) on t24, whose probe
  --scratch-show 64 prints all 64 scratch dwords sa64_dump.s stores: E391's 40 jobs and 16 held-out
  jobs at 3 and 6 rows read the markers of ...
- `E1103` texture, 2026-11-15: r25-csc stage csc (16 jobs): a fill's transfer command loads
  colour-space set 0 when its load flag is set (xfer:17 bit 0, the set's words xfer:18 to 22), and a
  fill without the flag keeps the set the ...
- `E1102` usse, 2026-11-15: r25-q123 stages q123s and q123w (21 jobs), held out and frozen before
  the run: E492's read and jump programs placed at four new offsets (0x0c3010, 0x2ca7f8, 0x3d0100,
  0x1c8008) read the links the ...
- `E1101` zls, 2026-11-15: r23-dpm stage zn (Q088, 5 jobs): after a geometry kick that overflowed
  without a raised abort (P 0x2e, 0x30, 0x32, 0x34), a moved final with the load bits (0x0017510e)
  and the host's 0.75 refill of ...
- `E1100` dpm, 2026-11-15: r23-dpm stage og (Q191, 6 jobs): with the second context's render 1 split
  into a geometry kick and a closing render (t22b --ctx2-geometry 1), the kept 64x64 owner's words
  0x00200047, 0x04000417, ...
- `E1099` dpm, 2026-11-15: r23-dpm stage rl (Q038, 10 jobs): with E442's reload background (a pixel
  shader fetching the target at the pixel) in every render of a geometry kick and a moved final on
  its own PB, and the target ...
- `E1098` usse, 2026-11-15: r23-pk stages q123 and q123h (10 jobs): in placed programs whose every
  word outside the code ends the task with its own number, the instruction index counts as an 18-bit
  counter across the ...
- `E1097` texture, 2026-11-15: r23-pk stage q181 (8 jobs) and pk-e568 gave no frozen verdict: the
  control c-copy-none (E037's UYVY copy, load flag clear) read 0xb6067a95fa98de2d, the hash of
  c-copy-csc that ran just before it with ...
- `E1096` pds, 2026-11-15: r23-pk stages pk and q019 (44 jobs) on t22, whose probe echoes every poke
  as sent: bg:1 left the library as 0x00130000 (4 rows) and reached the fill's job as poked in every
  poked job (0x30000, ...
- `E1095` zls, 2026-11-15: r21-zls stage zz (Q107, 4 jobs): on E629's ramp with the final on its own
  PB the final's G 33 store (depth.2) holds 184320 zero window dwords in tile rows 0-11 after a
  raised kick (0x24, 0x38) and ...
- `E1094` zls, 2026-11-15: r21-zls stage zw (Q088, 3 jobs): during the partial renders CR_ISP_ZLSCTL
  (0x0480) reads the render details' word rd:11 with bits 14, 18 and 19 ORed in (rd:11 | 0x000c4000)
  in every sample, on E336's ...
- `E1093` zls, 2026-11-15: r21-zls stages zc and zl (Q088, 9 jobs): with the host's 0.75 refill of
  the load buffer between an overflowing geometry kick and a moved final on its own PB, after a
  raised kick (0x24, 0x28, 0x2c ...
- `E1092` dpm, 2026-11-15: r20-own stage owp (5 jobs, t18b under regtimeline, render_keep armed, a
  1024x768 owner closed early after its overflowing render, the second context drawing the default
  triangle): the kept owner's ...
- `E1091` dpm, 2026-11-15: r20-own stages ow and owt (6 jobs, t18b under regtimeline, render_keep
  armed, a 1024x768 owner at P 0x422 closed early, the second context drawing the library's default
  triangle): with the owner's ...
- `E1090` zls, 2026-11-15: r20-zls stage zq (Q107, 4 jobs): on E629's ramp at P 0x44 and 0x4c the
  kick overflows once without a raise (TA3DCtl dword 38 0, E625 with U 49) and the final render on
  its own PB still keeps the zero ...
- `E1089` dpm, 2026-11-15: r20-zls stage zm (Q038, 3 jobs): a final render on its own PB without a
  depth buffer, its triangle moved 96 px right, painted every target pixel after a raised kick
  (H-REPAINT 2 of 2 at 0x28 and ...
- `E1088` zls, 2026-11-15: r20-zls stages zc and zr (Q088, Q038, 11 jobs): after a host refill of
  the load buffer with 0.25 between an overflowing geometry kick and a moved final on its own PB, no
  frozen form of the separate ...

## Closing sessions

96 published sessions (dataset manifests of `<area>/closing-*`), newest first: date, module
srcversion, fork tip, laptop tools.

- `render/closing-r31-kreg2`: 2026-11-16; module 7CE8E38EDB97FC5EA4F6C90; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t30
- `render/closing-r31-cc`: 2026-11-16; module 7CE8E38EDB97FC5EA4F6C90; tools ~/sgxfive-test-t10
- `render/closing-r30-pde`: 2026-11-16; module 7CE8E38EDB97FC5EA4F6C90; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t30
- `render/closing-r30-evst2`: 2026-11-16; module 7CE8E38EDB97FC5EA4F6C90; tools ~/sgxfive-test-t10
- `render/closing-r30-evst`: 2026-11-16; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10
- `render/closing-r29-kreg`: 2026-11-16; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10
- `render/closing-r29-flag2`: 2026-11-16; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t22
- `render/closing-r29-flag`: 2026-11-16; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t14, ~/sgxfive-test-t22
- `render/closing-r26-vol`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t24
- `render/closing-r26-sa0`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t24
- `render/closing-r25-sa64`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t24
- `render/closing-r25-q123`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t22
- `render/closing-r25-csc`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t22
- `render/closing-r23-pk`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t22
- `render/closing-r23-dpm`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t22b
- `render/closing-r21-zls`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t18b
- `render/closing-r20-zls`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t18b
- `render/closing-r20-own`: 2026-11-15; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t18b
- `usse/closing-r16-usse`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r19-own1b`: 2026-11-14; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t18b
- `render/closing-r19-own`: 2026-11-14; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t18b
- `render/closing-r19-k0b`: 2026-11-14; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t18b
- `render/closing-r19-k0`: 2026-11-14; module E0CC40275493F8AEAD8180B; tools not named
- `render/closing-r19-flag`: 2026-11-14; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t18b
- `render/closing-r19-dpm`: 2026-11-14; module E0CC40275493F8AEAD8180B; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t18b
- `render/closing-r18-flag`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t14
- `render/closing-r17-zls`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r17-tw`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t14
- `render/closing-r16-zls`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r16-tw`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t14
- `render/closing-r16-tex`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r16-mte`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r15-zls`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r15-tw`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t14
- `render/closing-r15-tex`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r15-isp`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r15-dpm`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r14-zls`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r14-tex`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r14-isp`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r14-flag`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10,
  ~/sgxfive-test-t14
- `render/closing-r14-dpm`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r14-bif`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t14
- `render/closing-r9-z2`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t9
- `render/closing-r9-x`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4
- `render/closing-r9-lgeo`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4
- `render/closing-r9-ldpm`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4
- `render/closing-r9-k1`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4,
  ~/sgxfive-test-t9
- `render/closing-r9-geo`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4
- `render/closing-r9-faults`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4
- `render/closing-r8-lgeo`: 2026-11-13; module 37EC97AB0CB37213C42FCCC; tools ~/sgxfive-test-rgn4
- `render/closing-r8-ldpm`: 2026-11-13; module 37EC97AB0CB37213C42FCCC; tools ~/sgxfive-test-rgn4
- `render/closing-r8-k2`: 2026-11-13; module B60AB0B475DD1E8972419B5; fork r8-kernel at 2a650d74;
  tools ~/sgxfive-test-rgn4
- `render/closing-r8-geo`: 2026-11-13; module 37EC97AB0CB37213C42FCCC; tools ~/sgxfive-test-rgn4
- `render/closing-r13-zls`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r13-tex`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r13-isp`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r13-flag`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r13-dpm`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r10-zls`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4,
  ~/sgxfive-test-t9
- `render/closing-r10-x`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4
- `render/closing-r10-tex`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4
- `render/closing-r10-st1`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
- `render/closing-r10-geo`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4,
  ~/sgxfive-test-t9
- `render/closing-r10-dpm`: 2026-11-13; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-rgn4
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

- fork pin (`tools/forkpin.py`): 8bc0877e8603
- module srcversion 7CE8E38EDB97FC5EA4F6C90: last named 2026-11-16, 4 sessions
- module srcversion E0CC40275493F8AEAD8180B: last named 2026-11-16, 20 sessions
- module srcversion B60AB0B475DD1E8972419B5: last named 2026-11-14, 38 sessions, fork r8-kernel at
  2a650d74
- module srcversion 37EC97AB0CB37213C42FCCC: last named 2026-11-13, 3 sessions
- module srcversion 41E2F5C756F96D20F7109A4: last named 2026-11-12, 6 sessions, fork r6-kernel at
  3f0b3e74
- module srcversion 99CD90DA26E3AFF9C450517: last named 2026-11-12, 14 sessions, fork resgx545 at
  a2788bd8
- module srcversion 230E0EF50FFFD606C53AE3C: last named 2026-11-10, 3 sessions
- module srcversion B21FDA82BD5E5CB5A627E3B: last named 2026-11-10, 9 sessions
- `tools/closing/scorekit.py` sha256 a10bcec039edeefe
- `tools/closing/sessioncheck.py` sha256 75546a6e5ea0b3e1

## Known tool weaknesses

From HACKING.md, "Known tool weaknesses":

Weaknesses of our tools that a session or a fold has found and that are not fixed yet. Each
round reviews this list: an entry leaves it with the commit that fixes it (and its test), or
stays with what a session must do around it.

- `tri --depth`'s default size (`userspace/libsgxfive/tools/sgxfive-test.c`): since round 22
  the floor of `--depth-pages` is the depth store's tile extent (W and H rounded up to tiles of 32
  x 16), but the default size stays W x H dwords and `DEPTH_MARGIN_PAGES` (16) over, so that
  earlier controls keep their layouts (R22-7 a). The margin covers the pad of every target up to
  16 pages of pad dwords; a wider pad (e.g. 31 pad columns at 4095 rows) is not covered: such a
  session passes `--depth-pages` of the tile extent or more.
- `probe` prints the first 32 changed scratch dwords (t22 and every tool before t24): E391's and
  E1096's `sa64_dump.bin` rows stored sa0-sa63 to scratch dwords 0-63 and every row counted
  `scratch 32 more changed`, so sa32-sa63 were never read (E391 and E1096 say so under what they
  do not show; Q019). t24's `probe --scratch-show N` (1 to 64, default 32 with the earlier output
  byte for byte; fill and copy probes, refused with `--tri`, which prints every dword) prints up to
  N. The entry stays until r25-sa64 has read them; no session before t24 reads sa32-sa63 from a
  probe's print.
- sgx-sim refusals that block oracles: the sim refuses what is not modelled, and some of those
  refusals stop a replay that would otherwise serve as an oracle, e.g. `0x0728` and the `pclink`
  path before E902's seeds. A session that needs the sim as an oracle checks first that its
  path does not hit one.

- the `edm/closing-r5-events` mock (resgx545-data, `tests/mockfw/`): its simulated EDM counts
  ticks on the wall clock (`time.monotonic()` since the boot, a tick every `clock / 399 MHz`), so
  the fill has about 16 ms to reach it from the fake tool's start before the slot 0 ring is full
  of ticks (the margin `tests/fake_tool.sh` was written to hold), and `t_trap_restores_knobs`
  polls the knob files with a 30 s bound. Under `pytest -n auto` or a busy Mac a late start
  fails it. The session is published and frozen, so the mock is not fixed; the runner works
  around it: `tools/closing/session_tests.sh` tries a session named in
  `tools/closing/timing_sensitive.txt` up to its number of tries (3 for this one) and passes on
  the first that passes (a real failure fails every try; the PASS line names the attempt). Still
  run it alone when it matters, not beside the suite. New sessions use the kit's argv-driven
  mock, which has no such margin.
- the 11.32 sampler model `texmodel.py` (resgx545-data `texture/p1141/support/`, and this tree's
  `tools/texture/p1132/recompute/`, the same bytes, sha256 ffa41eb9...) addresses a twiddled
  texture by plain Morton order over the whole side, where E561 says tiles of up to 16 x 16:
  wrong when both sides are above 16 (r13-tex: E564's an-t3b11 at pixel 16). Both copies are
  frozen (11.32's declared predictions, the p1141 batch) and stay as they are. A session that
  needs twiddled textures above 16 a side pins `resgx545:tools/texture/tilemodel.py` with its
  input `tools/texture/p1132/recompute/texmodel.py`: the same model with E561's address
  (`tilemodel.tm`, tested on E564's an-t3b11, 2048 of 2048, `tools/texture/test_tilemodel.py`).

- a page directory entry with a size field other than 4 KiB is mapped only by the fork's debugfs
  `vm_pde_addr`, `vm_pde_size` and `vm_pde_layout` (branch `r30-kernel` 8bc0877e8603, landing
  with the r30-pde fold; read back by `vm_large`, t30's `copy --src-addr`, `fill --dst-addr` and
  `--large-copy DIR`), over a region the driver owns, not a buffer's pages. r30-pde found the
  field not taken: every code 0 to 7 walks 4 KiB entries (E1117 to E1119), so a row there
  measures the 4 KiB walk of that region. The fork's KUnit safety case holds the GPU to the region
  only for r30-pde's VA windows (code 0 [0, 16K) and [4M - 8K, 4M); codes 1-4 [S - 8K, S + 8K)
  and [2S - 8K, 2S + 8K); code 5 [4M - 16K, 4M); codes 6 and 7 [16K, 32K), read only): a row
  outside them changes that test first.

## Simulator coverage baseline

44 entries in `crates/SIM_UNMODELLED.toml` (what the simulator does not model).
