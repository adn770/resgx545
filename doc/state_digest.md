<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# State digest

*Generated from the tracked tree by `tools/records/digest.py`; do not edit.*

Where the project stands, on one page: the open questions, the newest records, the published closing
sessions, the tool and fork versions, the known tool weaknesses and the simulator's unmodelled
baseline. The records, questions and manifests themselves hold the detail.

## Open questions

145 open: 135 hw, 10 parked. Each with its unit, value and the last three records of its evidence
list.

- `Q076` bif, high: which pages does each bus-interface requestor of a render (the TA, the 3D, the
  EDM's PB load) need in the directory of the list it ... (E745, E761, E980)
- `Q038` dpm, high: what does the final render read back of a partial render's depth (a depth buffer
  stored by ZLS, the 3D kick's RT status bit 1), now that a ... (E629, E996, E1020)
- `Q045` dpm, high: what does the DPM store in the state page, does a load task read back the
  macrotile lists a partial render stores in the RT data's state ... (E625, E627, E631)
- `Q191` dpm, high: what are the words that land in a kept owner's control page (0x00200047), OTPM
  page (0x04000417) and state page (0x00020001, 2) after the ... (E462, E591, E631)
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
  in an ordinary TA, 3D, DPM or transfer job, and how long does ... (E890, E902, E921)
- `Q070` ta, high: what do the TA object's format word bits 15:8 and above and its set masks select
  beyond the settings seen, and does the fitted region test ... (E543, E544, E777)
- `Q050` usse, high: what do the visibility group's instructions do, and how do smp's mipmaps and
  LOD values, the border address modes, the compressed and YUV ... (E563, E565, E568)
- `Q047` vdm, high: what do VDM_STATE1 bit 8, bits 11:9 and bits 15:13 select for a state task, when
  on the one-triangle job bit 8 changes nothing, bits 11:9 ... (E427, E440, E545)
- `Q108` bif, medium: what do the page table entry flags WRITEONLY, CACHECONSISTENT and EDMPROTECT
  do on the hardware, which of the bus interface's requestors do ... (E964, E965, E1046)
- `Q081` dpm, medium: what does CR_DPM_REG_074C bit 8 make the DPM read or write near offset 0x6010
  of the context's TA-data space, and what fixes that place? (E313, E362, E447)
- `Q192` dpm, medium: does the store that follows the next context's render replace the state page a
  partial-render owner left (18 non-zero dwords after its ... (E464, E591, E631)
- `Q082` edm, medium: what does CR_EVENT_STATUS2 bit 6 follow in a pixel task (a fill without a
  load: a tile's time near 125 us, E805; a program that waits on a ... (E839, E840, E841)
- `Q031` isp, medium: why does ISP word 0 bit 28 hang a multisampled render, when single-sampled it
  widens coverage to the union of eight samples? (E215, E278, E416)
- `Q032` isp, medium: what does pcoeff hand the ISP in the punch-through pass, when the kept pixels'
  depth is the same without it and moves between runs only ... (E217, E416)
- `Q071` isp, medium: what do the bits of the ZLS control word that change nothing seen (12, 15, 16,
  20 to 23, 27 to 31) do, alone and set together, what does ... (E1053, E1063, E1069)
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
  background object) limit, given that all sixteen douta words reach sa0 ... (E125, E391, E973)
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
- `Q139` ta, medium: what is the stride's relation to the RT data, and why do the macrotile words
  that fault (E509) fault, given that every kept fault at fx 2 ... (E1007, E1011, E1048)
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
  sizes and modes that sgx-sim's tex::sample refuses, where a ... (E1049, E1058, E1067)
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
- `Q036` vdm, medium: what do the DPM's status words hold (0x0748 bit by bit, CR_DPM_3D_PAGE_COUNTS'
  high half, and the owner words 0x0700 to 0x0728 a kept owner ... (E1032, E1044, E1057)
- `Q042` vdm, medium: what do bits 27:24 of the index list's first trailing word (VDM_INDEX2) do,
  when its low bits move the list's first index and 0x0f000000 ... (E307, E308, E414)
- `Q092` vdm, medium: what do bits 31:28 of the index list's first trailing word count, which the
  closed driver writes as 0xf on 1886 captured lists and 0xd on a ... (E348, E414, E546)
- `Q112` vdm, medium: what do bits 25:24 of the index list header do, which are clear in all 1888
  captured lists, and does the TA take indices wider than the 16 ... (E414, E737, E756)
- `Q163` vdm, medium: what is the state the jobs leave that decides whether a job with VDM_STATE1
  bits 11:9 other than 2 hangs (E700: a counter c, cleared by a ... (E701, E1021, E1035)
- `Q107` zls, medium: why does the final render of a job that overflows store zeros for the first
  row of macrotiles and the depth with its sign bit set for the ... (E996, E997, E1020)
- `Q120` zls, medium: what do the stored depth formats 3 to 7 (CR_ISP_ZLSCTL bits 26:24) hold and
  how are they laid out, given that they store depth and stencil ... (E1031, E1043, E1054)
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
  E1045 and E1056: bits 15 to 17 select no winding, and bits 16 ... (E998, E1045, E1056)
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
- `Q114` texture, low: does a texture word other than TEXTYPE name a 3D (volume) texture (no TEXTYPE
  value does, E567, E726), and if one does, how are its slices ... (E941, E942, E958)
- `Q115` texture, low: does the sampler filter anisotropically on this core, and which bits of the
  texture words or the smp operands select it and its ratio? (E564, E720, E723)
- `Q177` texture, low: which dword do texture types 1, 3 and 4 read, each byte halved, in u address
  modes 4 to 7 at a size other than 16 x 16 and 32 x 32 (E1055's ... (E1039, E1055, E1065)
- `Q179` texture, low: how are the blocks and the data bits of formats 23 to 26 laid out (a data bit
  changes 7 to 13 pixels, the blocks of 23 and 24 do not differ ... (E342, E568, E724)
- `Q181` texture, low: does the fill's transfer command load a colour-space set at all (xfer:17^=1
  and xfer:18 to 22 made no difference for formats 28 and 29, ... (E037, E040, E568)
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
- `Q126` usse, low: which extension of a source 1 above 0x7fff does the test of iaddu32 read (no
  test tells it, E498), and what value does iaddu32 write into ... (E498, E521, E1061)
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
- `Q299` zls, low: does a ZLS store whose extent runs past its buffer fault the job (E411's G 5 to
  17 in a 16-page buffer), and what does a load pass store ... (E1051, E1064, E1068)
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
  driver writes between frames (0x0011700a), now that bit 14 is ... (E989, E997, E1014)
- `Q118` render, fw (parked): how does the firmware's kick tell that its context's page directory is
  in none of the bus interface's directory lists (a compare against ... (E360, E592)
- `Q119` render, fw (parked): does one TA command carrying both FIRST_KICK and LAST_KICK act as two
  commands in the firmware (a kick and a closing kick)? (E156, E165)
- `Q277` dpm, fw (parked): what sets the fields of register 0x0740 that the TA kick turns into DPM
  store and load tasks (a host write reads back 0: E456; 0 in every ... (E312, E456, E574)
- `Q095` platform, kernel (parked): does giving the EDM a page directory of its own, rather than
  gma500's default one, change anything beyond the coupling of their teardowns? (E008, E018, E021)

## Recent records

133 records of 2026-11-13 to 2026-11-14 (the last 2 days to the newest record's date), newest first;
the claims are cut at 200 characters.

- `E1069` zls, 2026-11-14: r17-zls rows zb20- (Q071, 9 jobs in stage zb20, t10): with bit 20
  cleared, formats 6 and 7 at 96 x 48 G 2 and 128 x 64 G 3 store their per-tile records one after
  another from dword 2048 whatever the ...
- `E1068` zls, 2026-11-14: r17-zls rows zo2- (Q299, 8 jobs in stages zovp2 and zovs2, t10): the
  depth load pass over overlapping tiles with edge tiles (65 x 33 G 1 and 63 x 31 G 0, E996's plane
  over a 0.2 load) loads each ...
- `E1067` texture, 2026-11-14: r17-tw stage tw17 (14 probe fills on t14 with a 1 MiB scratch,
  E1047's tx_map form; safe class, no fault, no stop): T3 bit 14 on a twiddled 32-bit texture
  samples a texture W' = W + 4096 texels wide ...
- `E1066` mte, 2026-11-14: r16-zls rows zw2- (Q069, 9 jobs in stage zoff, t10): on E987's ramp (256
  x 128, t = x / 512, format 0) the viewport's z offset w at 0, 1/16, 3/16, 5/16, 3/8 and 7/16
  stored (1.6 w + 0.2) t (frozen ...
- `E1065` texture, 2026-11-14: r16-tex stage ty on module B60AB0B4 (Q177; texture types 1 and 4 at 8
  x 8, 64 x 64 and type 1 at 64 x 16, with the mode 0 reference of each size, 15 probe fills at base
  0 of a 32-page named scratch): ...
- `E1064` zls, 2026-11-14: r16-zls rows zo- (Q299, 11 jobs in stages zovp and zbits4, t10): a load
  pass over overlapping tiles (64 x 32 G 0 and 160 x 48 G 2) loads each tile's slot by E465, passes
  each tile on its own and ...
- `E1063` zls, 2026-11-14: r16-zls rows zb4- (Q071, 14 jobs in stages zbits4, zovp and zoff, t10):
  bit 0 under E988's stencil row, E1030's bit 16 cleared and E1031's flat format-6 and F7K rows
  writes no colour pixel and leaves ...
- `E1062` usse, 2026-11-14: r16-usse stage utest on module B60AB0B4 (Q137; 20 client fills, one form
  and one join a program, the 16 values of the test field enc[43:40] packed one bit a field from p0
  by `p0 or`, with the ...
- `E1061` usse, 2026-11-14: r16-usse stages uadd and urpt on module B60AB0B4 (Q126; client fills,
  `iaddu32.testtaz.chan0 DST, p0, r1, SRC2` over eight (r1, source 2) pairs a program, r1's low half
  0x8000 to 0xffff in seven of ...
- `E1060` mte, 2026-11-14: r16-mte stage rclip on module B60AB0B4 (Q116; the MTE state's region
  clip, presence bit 7 and its two words, added to the probe triangle's block by t10's --blk-add
  7=C0,C1, 0xdf43 becoming the closed ...
- `E1059` zls, 2026-11-14: r16-zls rows zp2- (Q297, 15 jobs in stage zpass2, t10): E1050's load pass
  (64 x 32, the bit:9 load of 0.25 and 0.75, depth less) at the flat depths 0.125, 0.0625, 0.1, 0.3,
  0.375, 0.625 and 0.5 + ...
- `E1058` texture, 2026-11-14: r16-tw stage tw16 (17 probe fills on t14 with a 1 MiB scratch,
  E1047's tx_map form; safe class, no fault, no stop): T3 bit 14 on twiddled 32-bit textures point
  sampled at 32 and 128 by 8, 32 and 128 ...
- `E1057` dpm, 2026-11-14: r15-dpm stage pr4 on module B60AB0B4 (Q036: r14-dpm's pr3 re-run with the
  sampling-period gate at 2000 ns; 0x0748 sampled alone at 0, 1, 4 and 7 partial renders, 10 jobs,
  all ran, rc 0): the period ...
- `E1056` isp, 2026-11-14: r15-isp stage zcut (11 jobs, E1045's form on six held-out triangles with
  one vertex depth at 1.25 or -0.25): the triangle is clipped as a polygon at z = 1 and z = 0 and
  each made vertex is rounded ...
- `E1055` texture, 2026-11-14: r15-tex stage ty on module B60AB0B4 (Q177; texture types 1, 3 and 4
  in u modes 4 to 7, 15 probe fills at base 0 of a 32-page named scratch): both controls passed
  (E1000's addr3-16x64-u4 and E1039's ...
- `E1054` zls, 2026-11-14: r15-zls rows zl2- (Q120, 13 jobs in stage zflat2, t10): format 6 stores
  E1031's 44-dword block with row 0's record carrying the depth where the plane is one float at
  every pixel: frozen H-FLATPLANE 3 ...
- `E1053` zls, 2026-11-14: r15-zls rows zb3- (Q071, 10 jobs in stage zbits3, t10): E1042's post hoc
  forms held out: bit 15 alone fails E988's stencil test at every pixel and stores the loaded bytes
  unchanged, at 96 x 32 G 2 ...
- `E1052` texture, 2026-11-14: r15-tex stage chain on module B60AB0B4 (Q104; 18 probe fills, the
  scratch as the texture, dword i named 0xD0000000 | i, LOD (y >> 2) + c down the rows): both
  controls passed (E562's shp-32x16-l5 and ...
- `E1051` zls, 2026-11-14: r15-zls rows zv- (Q298, 16 jobs in stage zovl, t10): overlapping stores
  in the 16-bit format (64 x 32 G 0, 160 x 48 G 2) and in the 24-bit one with edge tiles (65 x 33 G
  1) and four macrotiles a side ...
- `E1050` zls, 2026-11-14: r15-zls rows zp- (Q297, 13 jobs in stages zpass and zbits3, t10): over 34
  x 18 edge tiles the ZLS load pass tests E831's band against the loaded depth and the loaded
  stencil and keeps the loaded ...
- `E1049` texture, 2026-11-14: r15-tw stage tw14 (14 probe fills on t14 with a 1 MiB scratch,
  E1047's tx_map form; safe class, no fault): T3 bit 14 on twiddled W x 32 32-bit textures at W 16,
  64 and 128, with u in (0, 1), (1, 2) ...
- `E1048` ta, 2026-11-14: r14-flag stage f2 (6 TA-dump jobs, t10: the unpoked 256 x 256 and 768 x
  640 baselines and four CR_TE_MTILE1 words never run, the first macrotile 14 and 15 tiles wide at
  256 x 256 and 26 and 27 at 768 ...
- `E1047` texture, 2026-11-14: r14-flag stage f1 (5 probe fills on E566's twiddled 32 x 32 32-bit
  texture in the tx_map form, t14 with a 1 MiB scratch (probe --scratch-pages 256) that maps E1033's
  two fault pages; 3 planned ...
- `E1046` bif, 2026-11-14: R14-bif stage refill (Q108's stale-data clause; E1029's zb-c-id depth
  form, 64 x 32, depth test never so the store holds the load, run twice on one context, 6 jobs,
  every control passed): when the ...
- `E1045` isp, 2026-11-14: r14-isp stage wind (8 jobs, E998's form: E977's ramp at 80 x 40, the
  depth dumped): ISP word 0 bit 15, 16 or 17 set alone removes the ramp triangle in the reversed
  vertex order too (no pixel, the ...
- `E1044` dpm, 2026-11-14: r14-dpm stage pr3 on module B60AB0B4 (Q036: 0x0748 sampled alone at 0, 1,
  4 and 7 partial renders, 10 planned jobs): ONE job ran, the PR 0 control pr3-c0-1, and the stage
  stopped by its own rule (rc ...
- `E1043` zls, 2026-11-14: r14-zls rows zl- (Q120, 9 jobs in stage zflat, t10): format 6 on flat
  planes at 0.25, 0.75, 1.0 and 0.0 stores E1031's 44 dwords a block, the four blocks alike and the
  0x9e markers in place, with the ...
- `E1042` zls, 2026-11-14: r14-zls rows zb2- (Q071, 20 jobs in stages zbits2, zgran and zodd, t10):
  no frozen model of the set half held all 11 rows (best Z-ONE-23 and Z-GRP-21-23, 9 of 11): bits 21
  to 23 set together make ...
- `E1041` zls, 2026-11-14: r14-zls rows zo- (Q242, 11 jobs in stage zodd, t10): past odd targets (63
  x 31 at G 1, 65 x 33 at G 2) formats 1 and 2 store, at every dword of the edge tiles, the floor
  rule of the float the same ...
- `E1040` zls, 2026-11-14: r14-zls rows zg- (Q243, 12 jobs in stages zgran and zbits2, t10): the ZLS
  depth load base (render details dword 12) is rounded down to 16 bytes: frozen G16 held 5 of 5
  held-out moves (+8 loaded ...
- `E1039` texture, 2026-11-14: r14-tex stage addr5 on module B60AB0B4 (Q177; 14 probe fills of
  twiddled 32-bit textures): both controls passed (E1000's 16 x 64 mode 4 and E565's bd-uv5, their
  kept images, 2048 of 2048); with u and ...
- `E1038` texture, 2026-11-14: r14-tex stage srgb4 on module B60AB0B4 (Q282; sRGB, T0 bit 27, 13
  probe fills): the three controls passed (E723's g-bl-st-a, r13-tex's srgb3-tri and srgb3-x1's
  channel 0 read through the second ...
- `E1037` isp, 2026-11-14: r14-isp stage clipr (10 jobs): a vertex the guard-band clip makes is
  rounded half away from zero to 1/256 pixel (frozen CLIP-HA held 3 of 3 rows with the clip vertex
  on an exact 1/512 tie at x = 80: ...
- `E1036` isp, 2026-11-14: r14-isp stage g14 (21 jobs): the guard the ISP clips far edges to is a
  quarter of the viewport past each edge (clip x and y within 1.5 w): frozen H-VP drew every
  held-out far triangle pixel for ...
- `E1035` vdm, 2026-11-13: r13-flag stage f3 (19 jobs, 8 recovered hangs, the kit's noreset and
  idle:S): E700's counter held on every clause row at v = 7 and failed below 2: a v = 7 job after a
  completed one hung on a 128 x ...
- `E1034` pbe, 2026-11-13: r13-flag stage f2 (4 jobs, E383's probe --tri form; planned faults): the
  frozen control failed, so every row is cannot tell ('controls FAILED: f2-ctl: FAILED'): E383's
  bit-12 mode 0 job (sideband ...
- `E1033` texture, 2026-11-13: r13-flag stage f1 (4 probe fills on a twiddled 32 x 32 32-bit texture
  in E566's tx_map form, the default 16-page scratch; planned faults): T3 bit 14 faulted both
  twiddled rows, E566's own tw32-t3b14 ...
- `E1032` dpm, 2026-11-13: r13-dpm stage pr2 on module B60AB0B4 (Q036: does 0x0748 bit 2 clear with
  partial renders; one scene, 3072x2048 with 1500 vertices, at 0, 1, 2 and 4 partial renders, two
  replicates each, 8 jobs): both ...
- `E1031` zls, 2026-11-13: r13-zls stage zfmt (6 jobs, t10): E1015's format-7 template F7K holds
  held out at the stencil fills 0x3f and 0x1f, equal to its markers (48 of 48 dwords each, no other
  dword changed; the fixed-byte ...
- `E1030` zls, 2026-11-13: r13-zls stage zbits (16 jobs, t10): of the ZLS control's bits 12, 16 and
  20 cleared alone and in pairs, bit 16 alone turns E977's tiled ramp store into E997's linear image
  (frozen L-BIT-16 held 6 of ...
- `E1029` zls, 2026-11-13: r13-zls stage zbase (11 jobs, E977's z243 form on t10 with the depth test
  never and the load buffer filled with its own dword indices, render details dword 12 poked after
  the tool's own pokes): the ...
- `E1028` pbe, 2026-11-13: r13-tex stage sb12 on module B60AB0B4 (Q046 sideband bit 12; E383's probe
  --tri form, sideband 0x1200 | mode, modes 0 to 6, colours 0xc0804020 and 0x13579bdf, one moved
  triangle; 16 jobs): the mode 0 ...
- `E1027` texture, 2026-11-13: r13-tex stage t3c on module B60AB0B4 (Q078; T3 bits 11, 12 and 14, 16
  probe fills): the control passed (E564's an-t3b11, its kept image); on twiddled chains with
  smp2dreplace, T3 bits 12:11 = 00 read ...
- `E1026` texture, 2026-11-13: r13-tex stage addr4 on module B60AB0B4 (Q177; T0 u address modes 4 to
  7 on twiddled textures, 12 probe fills): both controls passed (E1000's 16 x 64 mode 4 and E565's
  bd-uv5, their kept images); ...
- `E1025` texture, 2026-11-13: r13-tex stage srgb3 on module B60AB0B4 (Q282; bilinear sRGB, T0 bit
  27, 9 probe fills): both controls passed (E723's g-bl-st-a and p1132's an-t0b27, their kept
  images, 2048 of 2048); 'FTZ-OUT ...
- `E1024` isp, 2026-11-13: r13-isp stage far (8 jobs, last, ascending distance): one far vertex at
  +2^26 and +2^30 pixels in x, -2^28 in x, -2^26 and -2^30 in y and +2^28 in y on a 64 x 64 target
  (--tri-unit 0, the near ...
- `E1023` isp, 2026-11-13: r13-isp stage q261 (16 jobs): every held-out far vertex draws E1012's
  clip (the far edges clipped to a guard, each new vertex rounded half up to 1/256 pixel, the edges
  then exact) at some value of ...
- `E1022` isp, 2026-11-13: r13-isp stage q201 (23 jobs, one 64 x 64 triangle that is not the tool's
  default): under CR_ISP_MULTISAMPLECTL byte 0 = 0x3c, 0x0f, 0xf0, 0x5a and 0x26 (bytes 1 to 3 at 0)
  both the position source ...
- `E1021` vdm, 2026-11-13: Round 12 offline (Q163; no run): on the 11.31 VDM state sweeps
  (vdm/state-units: 133 jobs of three scripts in run order, E545's two-block stream; c taken as 0 at
  each script's start, every script ...
- `E1020` zls, 2026-11-13: Round 12 offline (Q107, Q038; no run): predicting each G = 1 depth dump
  of the 11.38 batch's overflowed 1024x768 jobs (dpm/partial-model-batch depth-safe.c1 and .c26: z =
  0.5 at 0x23, 0x28 and 0x30 ...
- `E1019` dpm, 2026-11-13: Round 12 offline (Q036; no run): over every kept closing-pass job with a
  DPM register timeline (697 jobs, 285824 timeline lines of closing r1-pixgeo, r2-geo, r3-geo,
  r3-geo-c, r5, r6 and r7-dpm, r8 ...
- `E1018` isp, 2026-11-13: Round 12 offline (Q201, on E064's kept sweep; no run): E606/E607's exact
  coverage test with each pixel (x, y) sampled at (x + lo/16, y + hi/16), lo = bits 3:0 and hi =
  bits 7:4 of cmd:16 ...
- `E1017` texture, 2026-11-13: Round 11 offline (Q177; no run): of the 31 kept twiddled jobs with T0
  u mode 4 to 7 outside E1000's own (p1132 tx-border 16, r8-geo addr 4, r9-geo addr2 11), 27 are
  squares and 4 are E565's 32 x 8 ...
- `E1016` texture, 2026-11-13: Round 11 offline (Q282; no run): E982's bilinear sRGB stage rule
  R10-BF11 with every stage result below 2^-14 flushed to +0 (FTZ-OUT, E1004's post hoc form),
  frozen by hash before any held-out pixel ...
- `E1015` zls, 2026-11-13: Round 11 offline (Q120; no run): two of E986's 'store less' layouts
  decode byte for byte from r10-zls zst2's kept dumps, rules frozen by hash (c7_rule.py,
  4d87c5ad...): format 7 under a constant ...
- `E1014` isp, 2026-11-13: Round 11 offline (Q071; no run): under E989's control (0xf8e6a00e: the
  bits E411 flipped singly to no effect flipped together, so bits 12, 16 and 20 cleared as in E997's
  linear store), the stencil ...
- `E1013` dpm, 2026-11-13: Round 11 offline (Q210; no run): over every kept DPM run of r5 to r10
  with a published replay of E874's 1500-vertex scene (520 jobs read; 53 calibrations and 118
  partial-render cells of the standard ...
- `E1012` isp, 2026-11-13: Round 11 offline (Q261, post hoc on E1005's and E979's kept rows; no run,
  no held-out row): none of 236 declared edge set-up arithmetics (float coefficients of 8 to 24
  bits, round to nearest or ...
- `E1011` ta, 2026-11-13: Round 11 offline (Q139; no run): on r7-rp stage q139's 21 poked TA dumps
  (E907's run on module 41E2F5C7, 10 fit, 10 held-out and 1 replicate row, never read for the flag)
  and its poked control, ...
- `E1010` isp, 2026-11-13: r10-x stage win0 (14 jobs, E502's identity maps: E437's primary PDS
  program iterating the position, a shader writing pa0 or pa1, --tri-full): in CR_ISP_MSAA mode 0
  with CR_TE_AA 0x60000000, ...
- `E1009` dpm, 2026-11-13: r10-dpm stage s6rep on module B60AB0B4 (Q210: is E874's step replay low
  at S6 by noise or by bias; 3 calibration replicates at each of five targets, 17 jobs): the a0
  premise pair passed ('s6rep: the ...
- `E1007` ta, 2026-11-13: r10-geo stage q139c (Q139; 6 TA-dump jobs, no fault): the 256 x 256 and
  640 x 480 baselines draw exactly with one header a target tile (controls); at the y-side macrotile
  words 0x0200b008 (fy 11) and ...
- `E1006` isp, 2026-11-13: r10-geo stage bgw (Q066; 18 jobs, the layered 64 x 64 render, no fault):
  words 12, 14 and 11 of the one-layer background object at 0.25, 0.5, 1.5 and -1.0 and words 9 and
  13 at 2.0 and -1.0 leave ...
- `E1005` isp, 2026-11-13: r10-geo stage pivot (Q261; 37 jobs on a 64 x 64 target, no fault): with
  E979's far-x23p, far-x24p and far-x25n moved by d = 0 to -544 pixels in the far vertex's y, every
  pixel outside E684's 1e-3 ...
- `E1004` texture, 2026-11-13: r10-tex stage srgb2 (6 probe fills of E723's bilinear sRGB form, T0
  bit 27): 'R10-BF11 (heldout) is not supported: 4 held, 1 FAILED, 0 cannot tell of 5': the stage
  rule fitted offline on r9-x's rows ...
- `E1003` texture, 2026-11-13: r10-tex stage t3b (15 probe fills on strided named memory: six
  held-out bit-14 geometries each followed by its bit-clear reference, E566's two controls, E975's
  b14-u01 replicated): 'R-4096TX ...
- `E1002` texture, 2026-11-13: r10-tex stage cube3, edges (2 probe fills, bilinear T0 0x07fe1400, 16
  x 16 faces, the across coordinate 15 + (x + 1/2) / 64 texels, the along coordinate 7.75 on +z/+x
  and 8.25 on -y/+x, 512 out ...
- `E1001` texture, 2026-11-13: r10-tex stage cube3, ties (13 probe fills of TEXTYPE 2, 16 x 16
  faces, point-sampled, 2048 two-axis tie pixels in each of 12 new rows): 'H-HIGHAXIS (heldout) is
  not supported: 9 held, 3 FAILED, 0 ...
- `E1000` texture, 2026-11-13: r10-tex stage addr3 (11 probe fills of twiddled 32-bit textures at
  page 12 of a 32-page named scratch, the swept u over 128 positions at one texel a step, v on texel
  H / 2, no fault): every frozen ...
- `E999` pbe, 2026-11-13: r10-x stage sb (18 jobs, E383's 64 x 64 triangle with eot_plain and two
  colours whose bytes all differ): pack modes 20 and 27 store, at sideband bits 8:6 = 0 to 3 and for
  both colours, the image ...
- `E998` isp, 2026-11-13: r10-x stage isp0x (6 jobs, E977's z242-c ramp at 80 x 40 under depth less
  with writes): ISP word 0 bit 15, 16 or 17 set alone removes the triangle: no pixel drawn (0 of
  3200, the background colour ...
- `E997` zls, 2026-11-13: r10-x stage zbits (11 jobs, E977's z242-c ramp at 80 x 40 G 2 and its
  z243-ctl load): ZLS control bit 0 stores the depth exactly as without it and writes no colour
  pixel under formats 0, 1 and 2 at G ...
- `E996` zls, 2026-11-13: r10-x stage zov (11 jobs): with the ZLS pitch G below the tiles across
  minus one, so that tiles share 512-dword slots, every shared slot holds the 512 dwords of the tile
  visited last in the region ...
- `E995` isp, 2026-11-13: r10-x stage dcmp (31 jobs, 64 x 32, a flat triangle over a loaded depth
  buffer, the drawn count of 2048): ISP word 0's compares 0 to 7 follow the GL order never, less,
  equal, lequal, greater, ...
- `E992` isp, 2026-11-13: Round 10 offline (Q202, the perspective clause; no run): on r6-pixel's 114
  kept jobs with w other than 1 (stages g6-rwa 8 and g6-rw 106, E859; 64 x 64, w from 2.5e-4 to
  8027, 58 distinct snapped ...
- `E991` zls, 2026-11-13: Round 10 offline (Q242; no run): past the target of r9-x's z242-c (80 x
  40, G 2, a tile area of 96 x 48, E977 scored only its 3200 in-target pixels), stored format 1 is
  min(floor(z0 * 2^24), ...
- `E990` isp, 2026-11-13: Round 10 offline (Q030; no run): on the 48 kept --pixels images of
  r9-geo's stages seam1 and seam4 (E953, E954: tri-full renders 64 x 96 to 128 x 96 and six single
  triangles of new slopes, ...
- `E989` isp, 2026-11-13: r10-st1 rows q071-b0 and q071-l1 (2 jobs): with CR_ISP_ZLSCTL's bits that
  E411 flipped singly to no effect flipped together under a stencil test (0xf8e6a00e: bits 15, 21 to
  23 and 27 to 31 set, 12, ...
- `E988` zls, 2026-11-13: r10-st1 stage st1 (16 jobs of 18, tool t10, `tri --isp2`): against a
  loaded stencil (CR_ISP_ZLSCTL 0x0017300e) ISP word 2's test reads, for pixel (x, y), byte j of its
  tile slot's 512 with j the ...
- `E987` zls, 2026-11-13: r10-zls stages zbgc, zbg and zw (13 jobs, 256 x 128, G 7): render details
  dword 16 (CR_ISP_BGOBJDEPTH) is the background depth, 1.0 and 0.25 poked stored at all 28279
  background pixels, and at 0.25 a ...
- `E986` zls, 2026-11-13: r10-zls stage zst2 (26 jobs, the stencil loaded and stored): E985's
  layouts held out byte for byte on 13 of 16 rows, formats 3 and 4 on every plane (E978's x ramp
  with stencil fills 0x00000000, ...
- `E985` zls, 2026-11-13: Round 10 offline (Q120, Q121; no run): E978's kept dumps (a loaded index
  stencil, one x depth ramp, 64 x 32 and 96 x 48) decode for stored depth formats 3, 4, 5 and 6,
  every changed dword at both ...
- `E984` isp, 2026-11-13: Round 10 offline (Q261, post hoc on E979's kept rows; no run): of the 46
  pixels of E979's 11 rows whose centre lies within 1e-3 pixel of an edge line (E684's band), the 26
  that lie on a far edge ...
- `E983` texture, 2026-11-13: Round 10 offline (Q177; no run): on E565's kept 32 x 8 twiddled jobs
  bd-hb-ns-uv4, uv6 and uv7 (u and v in mode 4, 6, 7), never read for the offset, every pixel reads
  the dword the v rule names plus ...
- `E982` texture, 2026-11-13: Round 10 offline (Q282; no run): one lerp stage of a bilinear sRGB
  sample (T0 bit 27) on two decoded halves A (weight 64 - k) and B (weight k) returns A unchanged at
  k = 0 and otherwise floors both ...
- `E981` zls, 2026-11-13: r9-z2 stage z2 (10 jobs, 256 x 128, G 7): with the viewport's z offset
  (state-block word 10) at -0.25, so a modelled depth of -0.75 to -0.25, format 0 stored 0.0 at
  every dword and formats 1 and 2 ...
- `E980` bif, 2026-11-13: R9-faults stage bif (Q076; debugfs alias_skip on tri -n 2 --keep-going on
  a new VM, E457's form, 14 jobs, every control passed): with the pairs and the three of buffers 12
  to 14 left out of the ...
- `E979` isp, 2026-11-13: r9-x stage far (11 jobs): with one vertex at +2^22, +2^23, +2^24 or -2^25
  pixels in x, -2^22, +2^23, -2^24 or -2^25 in y (the other coordinate up to 2^23), or two at +-2^23
  or +-2^24, and the rest ...
- `E978` zls, 2026-11-13: r9-x stage zst (12 jobs): with E466's x ramp and a stencil buffer of each
  dword's index loaded (bits 1 and 13) and stored (bit 17), at 64 x 32 (4 tiles) and 96 x 48 (9
  tiles), format 4 changed 640 ...
- `E977` zls, 2026-11-13: r9-x stage zls (16 jobs): stored depth format 1 is min(floor(z * 2^24),
  0xffffff) of the format-0 float at every dword (frozen H-FLOOR held 3 of 3: 32768, 76800 and 3200
  dwords at 256 x 128 G 7 over ...
- `E976` texture, 2026-11-13: r9-x stage srgb (8 jobs): with T0 bit 27 (sRGB) and bilinear filtering
  on injected strided texels, each lerp stage alone (fy = 0 on two jobs, fx = 0 on two, every 1/64
  weight) and both (two jobs at ...
- `E975` texture, 2026-11-13: r9-x stage t3 (19 jobs): with T3 bit 14 set in smp on named memory, on
  six held-out strided geometries (W 16, 32, 48 at strides 32, 64, 128, u off the texel centres and
  past the texture) each with ...
- `E974` texture, 2026-11-13: R9-k1 stages s1 and s2, read post hoc at the fold (not frozen): at
  every background pixel whose layer coordinate lies outside [0, 1) under the plane that held (E971,
  E972), 1/64 texel off a texel ...
- `E973` isp, 2026-11-13: R9-k1 stage s3 (Q066 explore; 21 jobs, the layered 64 x 64 render, no
  fault): words 9 and 11 to 14 at 1.0, word 9 and word 13 at 0xffffffff, the format word 10 at 0,
  0x202, 0x404, 0x101, 0xffff, ...
- `E972` isp, 2026-11-13: R9-k1 stage s2 (Q066, and the anchor E971 left open; 20 held-out jobs, the
  layered 64 x 64 render with kernel pokes of the vertex words 15 to 22: a move of 16 pixels and a
  bit flip each, four ...
- `E971` isp, 2026-11-13: R9-k1 stage s1 (Q190; 44 jobs, the layered 64 x 64 render with kernel
  pokes of the object's words 3 to 8, 1 to 3 words a job at k/8 values, 14 fit and 30 held out drawn
  with the seed r9-k1 after the ...
- `E970` isp, 2026-11-13: R9-k1 stages s0t and s0p (Q190; the 64 x 64 one-triangle render with
  debugfs render_bg_layer on and render_bg_src at a mapped 64 x 64 source, 7 controls, no fault):
  the render details' background tag ...
- `E968` texture, 2026-11-13: Round 9 offline (Q078; no run): with T3 bit 14 set, smp on a strided
  texture reads dword i + K + M c, i the dword the same job reads without the bit and c its column,
  read on E566's fit job ...
- `E965` bif, 2026-11-13: R9-faults stage tri2 (Q108; the 64 x 64 triangle with PTE flags on its
  colour target or the ZLS buffers of tri --depth --depth-store, 7 renders, the three knob-free
  controls passed): WRITEONLY and ...
- `E964` bif, 2026-11-13: R9-faults stage xf2 (Q108; a fill's destination and a copy's read-only
  source with one PTE flag, 12 jobs, every control passed, E946's nine rows rerun token for token):
  WRITEONLY on a fill's ...
- `E963` dpm, 2026-11-13: r9-ldpm stage f9b on module B60AB0B4 (Q211's count of the 1500-vertex
  scene, Q210's raise at band 4): the three calibrations held as controls (1280x1280, 1792x1792 and
  2560x2048 never run: steps in ...
- `E962` dpm, 2026-11-13: r9-ldpm stage w on module B60AB0B4 (Q211, the need of wide scenes of many
  vertices): held out at four targets wider than 2:1 never run, E874's replay gave the need of the
  1500-vertex scene at each ...
- `E961` dpm, 2026-11-13: r9-ldpm stages a0 and m6b on module B60AB0B4 (Q210; band 6 of the tool's
  1500-vertex triangle): the premise held, r8-ldpm's six a0 controls repeated ('a0: the premise held
  (E935's a0 controls repeat ...
- `E960` dpm, 2026-11-13: Round 9 offline steps of r9-ldpm (Q210, Q211; no run), each frozen by hash
  before its scoring: OD-1, E874's replay gives the need of the 1500-vertex scene at all nine kept
  calibrations (E915, E935, ...
- `E959` ta, 2026-11-13: R9-lgeo stage q139b (Q139; 4 TA-dump jobs at 1280 x 720 and 768 x 640, the
  datasets' own commands, no fault): the unpoked baselines draw exactly and hold one header with a
  stream for every target ...
- `E958` texture, 2026-11-13: R9-lgeo stage tx6 (Q283; E725's 64 x 32 map-texture fill, dword i of
  the scratch 0xD0000000 | i; 14 jobs, 2 controls, no fault): type 4 at widths that are not
  multiples of 32 keeps ceil(w / 32) whole ...
- `E957` texture, 2026-11-13: R9-geo stage addr2 (Q177; 11 probe fills of twiddled 32-bit textures
  at page 12 of a 32-page named scratch, the swept axis over 128 positions at one texel a step, no
  fault): E932's u reading ...
- `E956` texture, 2026-11-13: R9-geo stage cube2, ties and edges (Q284; 8 probe fills, no fault): a
  tie of the two largest coordinates went to the face of the higher axis (z over y over x) on 4 of 4
  held-out sweeps of x = y and y ...
- `E955` texture, 2026-11-13: R9-geo stage cube2, sizes (Q284; 8 probe fills of TEXTYPE 2
  point-sampled by smp3d, E726's cu-xn the control, no fault): with E923's face and (s, t) rule, the
  face-local index of 32 x 32 and 64 x 64 ...
- `E954` isp, 2026-11-13: R9-geo stage seam4 (the seam holes, E953's question; the same 24 renders
  with --aa4 alone, the 4x context's automatic four region-header arrays, never run before in modes
  0 and 1, and E828's j1r as a ...
- `E953` isp, 2026-11-13: R9-geo stage seam1 (Q141; 24 tri renders with E504's pokes, each with
  --aa4 and debugfs render_rgn_arrays 1, a context made for 4x targets whose region headers are
  forced to one array, E502's, E504's ...
- `E952` isp, 2026-11-13: Round 9 offline (Q260; no run), on E683's 240 S3 cases (negative
  coordinates at 1/4096, kept images, never read by E914's or E943's readings): E943's post hoc
  reading 'a sweep misses half away from ...
- `E951` texture, 2026-11-13: Round 9 offline (Q284; no run): the face-local index E930 read post
  hoc on its three 32 x 32 cube jobs (4831 of 4831 predicted pixels: E923's Morton interleave of (s,
  t) with t in bit 0, and bit 8 = ...
- `E950` ta, 2026-11-13: Round 9 offline (Q139; no run): with the first macrotile fx tiles wide, a
  block row of it takes 8 floor(fx / 2) region-header slots (H-EVEN) where R7-BLK (E907) has 16
  floor(fx / 4); with E944's ...
- `E946` bif, 2026-11-13: R8-k2 stage xf (Q108; a fill's destination and a copy's read-only source
  with one PTE flag, 9 jobs): every frozen verdict 'cannot tell: controls: xf-c-end: cannot tell',
  since the stage's fourth ...
- `E945` bif, 2026-11-13: R8-k2 stage tri (Q108; the 64 x 64 triangle with one PTE flag on its
  colour target or its GENERAL page, 7 renders, both knob-free controls exact): WRITEONLY faulted
  both rows, the colour target after ...
- `E944` ta, 2026-11-13: R8-lgeo stage q139 (Q139; 20 TA-dump jobs at 256 x 256, 640 x 480 and 1280
  x 720, one --kpoke-render of the stride or a macrotile word inside the ranges that drew without a
  fault in the kept data, no ...
- `E943` isp, 2026-11-13: R8-lgeo stage zs2 (Q260; 160 sweep steps and 5 controls, 512 x 256 and 256
  x 512, vertices in 1/4096 pixel, no fault): a negative coordinate 1/512 above the grid rounds away
  from zero at -1/256, ...
- `E942` texture, 2026-11-13: R8-lgeo stage tx5 (Q178; type 5 on E725's map-texture fill and on
  stored dwords, 28 jobs, no fault): TEXTYPE 5 with format 12 returns 0x0000ffff for a texel t = (y
  mod h) w + (x mod w) iff bit 0 of ...
- `E941` texture, 2026-11-13: R8-lgeo stage tx4 (Q283; E725's map-texture fill moved over type 4
  textures by window offsets, 20 jobs, no fault): type 4 stores 32 x 32 blocks of 1024 dwords, (y
  mod 32) 32 + (x mod 32) inside a ...
- `E940` texture, 2026-11-13: R8-lgeo stages tx3 and tx4 (Q283; E725's 64 x 32 map-texture fill,
  dword i of the scratch 0xD0000000 | i; 12 jobs and 3 controls, no fault): below 8 texels wide type
  3 reads rows max(8, w) dwords ...
- `E939` dpm, 2026-11-13: r8-ldpm stages k and u on module 37EC97AB (Q211, the U clause): HU1's page
  need of the union of a scene's triangles (a region counted once, 128 bytes a stream, a page per 32
  streams of a macrotile, ...
- `E938` dpm, 2026-11-13: r8-ldpm stages f9 and k on module 37EC97AB (Q211, the partial-render count
  of scenes of many objects and of several kicks): held out, F9's replay of the 1500-vertex scene
  gave the count at 13 of 15 ...
- `E937` dpm, 2026-11-13: r8-ldpm stage v on module 37EC97AB (Q210, larger objects): the tool's
  1500-vertex triangle with --vtx-coords 8 and our vertex program vtx_coord8.s writing o4 to o11
  (plan P3: the default program ...
- `E936` dpm, 2026-11-13: r8-ldpm stage m6 on module 37EC97AB (Q210; band 6 of the tool's
  1500-vertex triangle): held out at seven targets, H-SPAN (the first partial render leaves 2 global
  pages iff S_6 < thr0 < A_6, cells ...
- `E935` dpm, 2026-11-13: r8-ldpm stages a0 and sp on module 37EC97AB (Q210; the tool's triangle
  with 1500 vertices): the premise held, R7-dpm's six s-a0 controls repeated on this module ('a0:
  the premise held (R7's s-a0 ...
- `E934` isp, 2026-11-13: R8-geo stage seam (Q141; 24 tri renders with E504's pokes, CR_TE_AA in
  cmd:1): every job whose CR_TE_AA had bit 31 or 30 set (0x60000000, 0xa0000000, 0xe0000000: 23 of
  24) was rejected at submission ...
- `E933` vdm, 2026-11-13: R8-geo stage vdm (Q271; 8 renders of E703's capacity form, probe --tri
  pixpds:12 with 126 vertices, VDM word 7 SET by --vdm 7=V rather than xored, no fault or hang):
  word 7 set to its natural value ...
- `E932` texture, 2026-11-13: R8-geo stage addr (Q177; 9 probe fills of E565's 16 x 16 twiddled
  texture at page 12 of a 24-page scratch whose every dword is named, the swept axis over 128
  positions at one texel a step, no fault): ...
- `E931` texture, 2026-11-13: R8-geo stage cube, ties and edges (Q284; 8 probe fills of TEXTYPE 2 by
  smp3d, no fault, readings of the frozen plan with no rule frozen but the edge rivals): at a face
  tie |w| = |u| (column 32 of two ...
- `E930` texture, 2026-11-13: R8-geo stage cube (Q284; 13 probe fills of TEXTYPE 2 point-sampled by
  smp3d, E726's cu-xn as the control, no fault): the cube-face (s, t) rule frozen offline (E923,
  q284_rule.json 52162471...) held ...
- `E923` texture, 2026-11-13: Round 8 offline (Q284; no run): the (s, t) of TEXTYPE 2's cube faces
  under smp3d is the public cube-map table (+x s = -w, t = -v; -x s = +w, t = -v; +y s = +u, t = +w;
  -y s = +u, t = -w; +z s = +u, t ...
- `E922` isp, 2026-11-13: Round 8 offline (Q141; no run, in sample): the landed region model
  (resgx545-data texture/p1141/recompute/msaa_model.py, sha256 1c0e8205..., E727's freeze,
  unchanged) with its two-halves rule gives ...

## Closing sessions

71 published sessions (dataset manifests of `<area>/closing-*`), newest first: date, module
srcversion, fork tip, laptop tools.

- `usse/closing-r16-usse`: 2026-11-14; module B60AB0B475DD1E8972419B5; tools ~/sgxfive-test-t10
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

- fork pin (`tools/forkpin.py`): 2a650d74b3a1
- module srcversion B60AB0B475DD1E8972419B5: last named 2026-11-14, 37 sessions, fork r8-kernel at
  2a650d74
- module srcversion 37EC97AB0CB37213C42FCCC: last named 2026-11-13, 3 sessions
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

## Simulator coverage baseline

41 entries in `crates/SIM_UNMODELLED.toml` (what the simulator does not model).
