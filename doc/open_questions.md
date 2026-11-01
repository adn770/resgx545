<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# Open questions

*Generated from `questions/` by `tools/records/questions.py`; do not edit.*

## dpm

- `Q038` (phase 10): when a scene overflows its parameter buffer, are the missing pixels geometry the partial render discards or pixels a later background object paints over, and why does the amount drawn not follow the buffer size? (E202, E204, E160)

## edm

- `Q002` (phase 3): is the 399.0 MHz reference that times the EDM tick and TIMER the clock the USSE runs from? (E009, E084, E124)
- `Q005` (phase 6): should the kernel ask the firmware for its identity on every boot, so DEV_QUERY reports it without the debug option? (E017, E022)
- `Q006` (phase 6): can a render client's VM do without a writable mapping of the device-wide TA/3D control block? (E023)
- `Q033` (phase 10): does the event word PDS #13 hands the EDM as pa1 carry CR_EVENT_STATUS bits in reverse order, and which events set its bits 8 and 19, that no handler acknowledges? (E155, E146, E154)
- `Q034` (phase 10): does the EDM start a TA command whose destination or source sync is incomplete when its context is the only one in the TA queue? (E161, E154)

## isp

- `Q030` (phase 10): what does each value of CR_ISP_MSAA.MODE store in the target, and does a clear bit 31 still tile the triangle? (E210, E220, E211, E219)
- `Q031` (phase 10): with ISP word 0 bit 28 set, is a pixel covered by any of eight samples placed by 0x04c8 and 0x0520, or by the four samples of 0x0520 plus the pixel centre? (E214, E215)
- `Q032` (phase 10): what does pcoeff hand the ISP in the punch-through pass, when the kept pixels' depth is the same without it and moves between runs only when it runs without the iteration it reads? (E217)

## mte

- `Q039` (phase 10): which vertex dword does user clip plane 1 read as its distance when it is enabled without plane 0? (E198)

## pbe

- `Q012` (phase 6): what do pack modes 22 and 34 encode, given a single value in 727 of the triangle's 1062 pixels and backgrounds that vary from run to run? (E032)

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

## platform

- `Q001` (phase 3): what do 0x0810, 0x0814 and 0x0818, set once by the init script to 0x1, 0xffff and 0x7ff, control? (E006, E010, E122)

## render

- `Q014` (phase 6): why does render command word 23 bit 27 (cmd:23^=0x8000000) fault with the same 3936 pixels differing in both runs, while bit 28 gives 4000 and then 3968? (E029)
- `Q029` (phase 9): does clearing bit 8 of the render context's isp_ipfmisc word skip untouched tiles above 64x64, and what do the EDM's render target and render context cleanups wait for? (E148, E023)

## ta

- `Q035` (phase 10): which tiling words does the macrotile rule set at target sizes other than the sixteen tried, and does register 0x0208 ever change with the size? (E174, E175)

## texture

- `Q007` (phase 6): what does bit 12 of the copy's texture address word read, and why does bit 14 complete with nothing written while bit 15 faults? (E036, E041)
- `Q008` (phase 6): what do bits 7:0 of the luma-key word that the TPU loads into 0x0868 do? (E039)
- `Q009` (phase 6): what do T0 bits 20:17 do for mipmaps, when bits 26:21 = 0x3f enable the chain only for some of their values? (E041)
- `Q010` (phase 6): which field of the copy's T1 word is bit 28, that setting it writes opaque black whatever the source and the luma-key words? (E037, E039, E046)

## transfer

- `Q003` (phase 4): why does a transfer render that faults on a read-only page raise no BIF-fault interrupt the host sees, and how does a host recover the EDM in place afterwards? (E021)
- `Q004` (phase 4): what do a transfer context's flag bits 1 and 4 and a priority other than 0 do on the hardware? (E015)
- `Q011` (phase 6): why do the plain and every-value copies differ in pixel count for xfer:0 bits 24 to 30 and =0, and xfer:7 bit 1? (E028)
- `Q028` (phase 9): what does a faulting job leave wedged when the kernel does not recover, and which reset steps does the recovery need? (E024)

## usse

- `Q016` (phase 6): which part of the smoa, smbo and smr sequences that fault the job makes it fault: the moest selectors, the changed state or the mirror mode? (E087)
- `Q017` (phase 6): why does g19 read 0x1a as a store's source but 0 through a mov and as the pixel? (E085, E086)
- `Q018` (phase 6): where does the 0xff00ff00 colour left in the opaque pass and the punch-through phase scene come from, and why does its pixel count vary from run to run? (E077, E082)

## vdm

- `Q015` (phase 6): why does VDM state word 1 with bits 11:9 = 7 hang the triangle sweep but render in the probe job that sets the same word? (E060)
- `Q036` (phase 10): what do the DPM status registers 0x0700, 0x070c, 0x0710 and 0x071c count, when they change on every render but not as a running page count? (E184)
- `Q037` (phase 10): does a hung job's saved render memory show how far the TA got, when the control hung in its pixel task leaves its object in one run and none in the next? (E186)
