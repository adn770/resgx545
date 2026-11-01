+++
id = "E160"
claim = "On a DPM out-of-memory (request 0x30, handler at 0xb50) the EDM waits for a render that can free memory, or grows the TA's global-list share once, or raises the ZLS page threshold, or aborts the macrotile; after an abort the TA stops (TA_TERMINATE, handler at 0xc23) and the EDM starts a partial render of what was tiled, using the render-details register block and the partial-region base, and its completion (request 0x80000, handler at 0xdbf) marks the macrotile's RT status word and restarts the TA"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand, as a summary: the out-of-memory handler (0xb50-0xc22), its sync test at 0xb0b, the terminate handler (0xc23-0xdbe), the resume handler (0xdbf-0xe08) and the alloc pause and resume routines (0x1765, 0x1773); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "infer"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_GBL", "CR_EVENT_STATUS.DPM_OUT_OF_MEMORY_MT", "CR_EVENT_STATUS.TA_TERMINATE", "hw_rt_data_set.num_out_of_mem_signals", "hw_rt_data_set.num_spm_renders", "hw_rt_data.state", "CR_DPM_TA_GLOBAL_LIST", "CR_DPM_ZLS_PAGE_THRESHOLD", "CR_MTE_OTPM_OP", "CR_DPM_ABORT_STATUS_MTILE", "CR_ISP_PARTIAL_REGION_BASE", "hw_render_details.isp_partial_region_base", "CR_ISP_START_RENDER", "CR_DPM_TASK_CONTROL", "CR_DPM_OUTOFMEM", "CR_DPM_PARTIAL_RENDER", "CR_DMS_CTRL", "hw_rt_data.rt_status_dev_vaddr"]
+++

**What was read.** Instruction numbers are indices in hex. `sa8` and `sa9` are the TA and 3D
state words (E154). Registers are named by address. This is a summary of three long handlers;
the steps below are those I could follow, in order, and where I give a reading it is marked.

**Results.**

*Out of memory (`0xb50`).* PDS #14's task `0xae8` acknowledges with `0x6` (E154), sets bit 19 of
`sa8` when `pa1` bit 20 (`DPM_OUT_OF_MEMORY_GBL`) was set and clears it for bit 21, then enters.

1. It sets bit 11 of `sa8` (out-of-memory pending).
2. If the 3D is idle (bit 0 of `sa9` clear) and the current context has a render on its ready
   list (context dword 10 not zero, test at `0xb46`), it sets bits 6 and 14 of `sa9` and bit 6 of
   `sa8`, posts the 3D scheduler request and ends: it waits for that render to run and finish.
3. Otherwise (the 3D is running, or is idle with no ready render), unless bit 5 of `sa8` is set (a
   partial render is already under way), it clears TA3DCtl dword 55, adds 1 to dword 3 of the RT
   data set (`num_out_of_mem_signals`) and sets bit 7 of the RT data's dword 13. If the 3D is
   running it sets bit 6 of `sa9` and ends. If it is idle it calls `0xb0b`, which returns whether
   the render details' destination sync entry for the macrotile's RT index (taken from
   `CR_DPM_ABORT_STATUS_MTILE`, bits 13:5) or any source sync is not yet complete; if one is not, it
   sets bit 6 of `sa8`, posts the 3D request and ends.
4. Otherwise it clears bit 6 of `sa8` and reads `0x0734`. If bit 0 of that register is set it
   goes straight to the decision below. If it is clear:
   - with bit 19 of `sa8` clear (the other kind, `pa1` bit 21) it *grows the global list*: it saves
     `CR_DPM_TA_GLOBAL_LIST` (`0x0628`) in TA3DCtl dword 33, pauses the TA's allocation (`0x1765`:
     sets bit 0 of `CR_DMS_CTRL` and waits for `0x0700` to read the same twice), writes the global
     list with the upper half of `0x072c` and bit 16, resumes (`0x1773`), sets bit 22 of
     `sa8`, writes `CR_DPM_OUTOFMEM` (`0x069c`) = 1 and ends;
   - with bit 19 set (the global kind) it pauses, writes the saved global list (dword 33) with
     bit 16 back, resumes, clears bit 22 of `sa8` and goes on to the decision.
5. *Decision (`0xbbf`).* If bit 7 of `sa8` is clear, or bit 9 is set, it aborts (step 6). Otherwise
   it compares a page count saved by an earlier abort with the current one (dword 35 with the upper
   half of `0x0724`, or, with bit 8 of `sa8` set, dword 36 with that of `0x072c`); if the saved
   count is not smaller it clears bits 8 and 7 and aborts. Otherwise it *raises the threshold*: it
   sets bit 9 of `sa8`, sets `CR_TE_PSG` bits 20 and 22 if bit 2 of `sa8` is set, pauses the
   allocation, adds `0x20` to `CR_DPM_ZLS_PAGE_THRESHOLD` (`0x0624`) saving the `0x20` in dword 38,
   saves the global list in dword 37 and writes it back multiplied by 16 (low half) with bit 16,
   resumes, and restarts the TA with `CR_DPM_OUTOFMEM` = 1.
6. *Abort the macrotile.* It writes `CR_MTE_OTPM_OP` (`0x024c`) = 1, waits for status bit 20,
   sets bit 5 of `sa8`, saves `CR_DPM_ABORT_STATUS_MTILE` (`0x0720`) in TA3DCtl dword 39 and its
   bits 13:5 in dword 40, sets bit 1 of `sa8`, writes dwords 35 and 36 from the page counts of
   `0x0724` and `0x072c` less 2, writes `CR_DPM_OUTOFMEM` = 4 and sets bit 0 of `CR_DMS_CTRL`.
   The TA then stops by itself.

*Terminate (`0xc23`).* The TA stops (`pa1` bit 10, acknowledged with `0x1000`) and request `0x40`
runs this handler. It sets bit 12 of `sa8`. If the 3D is running it sets bit 17 of `sa8`, clears
bit 6 of `sa9` and ends (the end of that render posts `0x40` again, E154). Otherwise it adds 1 to
dword 4 of the RT data set (`num_spm_renders`), copies the render details' frame number to
TA3DCtl dword 42, stores the TA's DPM state and loads the 3D's PB if needed, and writes the render
details' register block to the ISP in the sequence the 3D kick uses (E163), except that: the
region header base (`0x0408`) is offset by the RT index of dword 40 times RT data dword 11, the
partial-region base (`CR_ISP_PARTIAL_REGION_BASE`, `0x050c`) is the region header base plus an
offset worked out from the saved abort status (dword 39) and RT data dword 2 (equal to it when bit
1 of `sa8` is clear), and `CR_DPM_3D_DEALLOCATE` is written 2 or 3 by bit 1 of `sa8`. It writes
`CR_ISP_START_RENDER` (`0x0428`) = 1 at `0xdb3`, after an HWPerf record of type 8 if the status
asks for it, and sets `sa9` bits 0, 1, 4 and 5 (plus bit 8 if bit 22 of `sa8` is set).

*Resume (`0xdbf`).* The render's completion posts request `0x80000` (E164). It clears bit 1 of `sa9`
and bits 11 and 12 of `sa8`, may set bits 7 and 8 of `sa8` by comparing the page counts saved at the
abort with the current ones, clears bit 0 of `CR_DMS_CTRL`, writes `CR_DPM_TASK_CONTROL` = 2 (a
clear), brackets it with `0x065c` = 1 (only if bit 1 of `sa8` is clear) then 0, writes
`CR_DPM_PARTIAL_RENDER` = 0 and waits for status bit 9. It sets bit 1 of the macrotile's RT status
word (the word of index dword 40) and clears TA3DCtl dword 28 and `sa8` bits 1, 5 and 17. If bit 8
of `sa9` was set it posts request `0x80` (the TA-finished handler, E156); otherwise it writes
`CR_DPM_OUTOFMEM` = 1 to restart the TA. That bit 1 of the status word means "depth stored", so that
the final render loads it, is a reading **[infer]**.

**Not shown.** What the thresholds, the global list and the page counts mean to the DPM; whether the
grow step helps; the meaning of bits 7 and 8 of `sa8` (the resume handler sets them when a page
count rose across the partial render); the part of the terminate handler that stores the DPM state;
which hardware events cause the out-of-memory. The only host input I can name is the PB descriptor's
thresholds. Nothing here runs the firmware.
