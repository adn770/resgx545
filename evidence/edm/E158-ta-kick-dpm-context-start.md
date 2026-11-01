+++
id = "E158"
claim = "The second half of the EDM's TA kick (0x9b7-0xacc) picks a DPM context slot for the RT data, clears (first kick, or flag 0x8) or reloads (slot held another RT data) its DPM state, control and OTPM, restores the tiling engine state, sets two TE_PSG bits, zeroes the RT status words on a first kick or flag 0x4, marks the TA running, copies the command into the render details, and starts the TA with a write of 1 to CR_VDM_START"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the kick routine from 0x9b7 to 0xacc and the copy routine at 0x7b1, with the DPM task routines at 0x1741-0x1755 and the context routines at 0x1778 and 0x17be; fetch offsets read by the rule of the instruction-set specification (a fetch with base plus offset starts one dword after the printed offset); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE", "infer"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["CR_DPM_STATE_CONTEXT_ID", "CR_DPM_STATE_BASE0", "CR_DPM_STATE_BASE1", "CR_DPM_CONTROL_BASE", "hw_rt_data.dpm_state_dev_vaddr", "hw_rt_data.dpm_control_dev_vaddr", "hw_rt_data.otpm_dev_vaddr", "CR_DPM_TASK_STATE", "CR_DPM_TASK_CONTROL", "CR_MTE_OTPM_BASE", "CR_MTE_OTPM_OP", "CR_TE_CONTEXT_STATE", "hw_render_details.te_context_state", "CR_TE_PSG", "hw_rt_data.state", "hw_rt_data.rt_status_dev_vaddr", "FRAG_FLAGS.TA3D_DEPENDENCY", "cmd_ta.pds_bgnd", "cmd_ta.num_patches_3d", "cmd_ta.patches_3d", "CR_VDM_START", "CR_USE_CACHE", "CR_PDS_CACHE_HOST_CLEAR", "CR_DMS_CTRL"]
+++

**What was read.** Instruction numbers are indices in hex. `r0` is the context, `r1` the TA
command, `r14` its RT data (command dword 17) and the render details are TA3DCtl dword 26.
The kick starts at `0x8e9` (E159 has its first half). Task codes of the DPM task registers
(`0x0694` and `0x0698`): the routines at `0x1741`, `0x1748` and `0x174f` write 2, 1 and 4 and wait
for status bits 6, 4 and 5, so 2 is a clear, 1 a store and 4 a load of the state.

**Results.** In order:

1. *Slot (`0x9b7`-`0x9f6`).* TA3DCtl dwords 20 and 21 hold which RT data owns each of two DPM
   context slots. The TA takes the slot that already holds its RT data; else slot 0 if it is
   free, else slot 1 if it is free; else the slot the 3D is not using (it reads bit 1 of
   `CR_DPM_STATE_CONTEXT_ID` and takes the other). It records the RT data in dword 20 or 21 and
   in TA3DCtl dword 25, and writes the slot in bit 2 of `CR_DPM_STATE_CONTEXT_ID`. If the slot's
   previous RT data differs, it is stored first (`0x17ec`, `0x184c`, `0x1778`). So bit 2 is the
   TA's slot, and by the 3D kick's use of bit 1, bit 1 is the 3D's **[infer]**.
2. *Clear (flags `0x9`, `0xa0e`-`0xa60`).* With command flags `0x1` or `0x8` it writes bit 0 of
   `CR_DPM_STATE_CONTEXT_ID` with the slot (the slot DPM tasks address), then the RT data's dword 5
   (`hw_rt_data.dpm_state_dev_vaddr`) to `CR_DPM_STATE_BASE0` (slot 0) or `_BASE1`, and dword 6 to
   `CR_DPM_CONTROL_BASE`. For each render target counted by RT data dword 10 it writes
   `(index << 3) | 2` to both task registers and waits for status bits 6 and 9. It then does a store task with an
   index taken from register `0x0740` (bits 17:9, shifted down 9 more for slot 1) and a load task,
   each only if that field is not zero, then writes RT data dword 7 (`hw_rt_data.otpm_dev_vaddr`) to
   `CR_MTE_OTPM_BASE` and the value 9 to `CR_MTE_OTPM_OP`, waits for status bit 20 (and the load
   bits) and for bit 12 of the second status register, and acknowledges them.
3. *Reload (`0x9fc`-`0xa0d`).* With neither flag, if the slot already held this RT data nothing
   is done (`0xa61`); if it did not (it was free or held another), the context routine at
   `0x17be` loads this RT data's state, control and OTPM through the TA's address space.
4. *State.* `CR_TE_CONTEXT_STATE` (`0x0274`) is written from render details dword 73, on every
   kick. `CR_TE_PSG` (`0x0218`) is read, `0x01000000` is ORed in, and `0x00200000` also if bit 8
   of RT data dword 13 is set, and it is written back.
5. *Marks.* TA3DCtl dword 55 is cleared and bit 0 of dword 54 set. With flags `0x1` or `0x4`
   it clears bits 11:4 of RT data dword 13 (`hw_rt_data.state`) and zeroes the RT status words
   (`hw_rt_data.rt_status_dev_vaddr`, one per render target).
6. *Running.* It sets bit 0 of `sa8`, moves the context to the head of the TA queue of its
   priority (unlinking it first), then calls the copy routine `0x7b1`.
7. *Copy (`0x7b1`).* In dwords, command to render details: dword 7 (the render flags) to 53; if
   render flag `0x200` is set, dwords 68 and 69 to 63 and 64 (the TA to 3D dependency,
   `FRAG_FLAGS.TA3D_DEPENDENCY`); dword 8 (the frame number) to 80 and to TA3DCtl dword 41;
   dwords 29-32 to 57-60 and then dword 15 over 56; dword 33 (the source sync count) to 90 and
   that many 4-dword entries from dword 34 to 91 on; dword 18 to 72; dwords 19 and 20 to 70 and 71;
   dwords 2-4 (`cmd_ta.pds_bgnd`) to 76-78; dword 24 to 81 and that many 2-dword pairs from
   dword 134 to 82 on. The pairs counted by dword 21 (`cmd_ta.num_patches_3d`) and listed from
   dword 170 (`cmd_ta.patches_3d`) are **memory writes**, the first dword the address and the
   second the value, not register writes.
8. *Record, flag, start.* With bit 1 of the HWPerf status it appends a type-3 HWPerf record with
   the page count (E149). With TA flag `0x1000` (command dword 1) it writes HostCtl dword 16 =
   500. Its last instruction (`0xacc`) writes 1 to register `0x0200`, `CR_VDM_START`.

The cache invalidations of the kick, just before `0x9b7` (E159, step 8): flag `0x40` the data cache,
flag `0x20` the PDS caches (`0x0ad0`, `0x0ae0`, wait for `0x0138` & `0x27`, acknowledge with
`CR_PDS_CACHE_HOST_CLEAR` = `0x27`), flag `0x10` `CR_USE_CACHE` (`0x0a08`) = 1, once per task.

**Not shown.** What the two `0x0740` tasks do (whose index the field holds, why a
store then a load); what the TE_PSG bits mean; that the instruction number `0xacc` is not the
register `0x0acc` (`CR_EVENT_TIMER`), which the same kick never touches. Nothing here runs
the firmware.
