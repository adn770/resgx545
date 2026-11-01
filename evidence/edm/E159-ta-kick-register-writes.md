+++
id = "E159"
claim = "The first half of the EDM's TA kick (0x8e9-0x9b6) records the job in TA3DCtl, resets the TA on a FIRST_KICK, loads the context's parameter buffer unless it is already loaded (or applies a pending threshold update), writes the command's 28 TA register dwords, one str each in structure order, then the vertex partition count, maps the context's address space and invalidates caches as the TA flags ask"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the kick routine from 0x8e9 to 0x9b6 with the PB routines it calls (0x168d, 0x16a2, 0x16d4, 0x170d, 0x1665), the BIF index routine at 0x1864 and the map routine at 0x184c; fetch offsets read by the rule of the instruction-set specification (a fetch with base plus offset starts one dword after the printed offset, a post-increment fetch starts at the printed offset); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["ta3d_ctl", "cmd_ta.hw_render_details_dev_vaddr", "hw_rt_data.hw_render_details_dev_vaddr", "GEOM_FLAGS.FIRST_KICK", "CR_SOFT_RESET.TA_RESET", "hw_render_context.hw_pb_desc_dev_vaddr", "cmd_ta.te_aa", "CR_TE_AA", "CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_SCREEN", "CR_TE_MACROTILE_STRIDE", "CR_TE_PSG", "CR_VDM_CTRL_STREAM_BASE", "CR_MTE_CTRL", "CR_TE_PSGREGION_ADDR", "CR_TE_TPC_ADDR", "CR_PPP_SCREEN", "CR_BIF_TA_REQ_BASE", "CR_USE_REG_0AA0", "CR_TA_REG_02B0", "CR_TA_REG_02B4", "CR_TA_REG_02D0", "CR_TA_REG_02D4", "CR_REG_0324", "CR_REG_0364", "CR_REG_0368", "CR_REG_0370", "CR_REG_0374", "CR_DPM_REG_074C", "CR_TE_REG_02A8", "CR_MTE_MULTISAMPLECTL", "CR_USE_REG_0A04", "CR_DMS_CTRL.MAX_NUM_VERTEX_PARTITIONS", "cmd_ta.num_vertex_partitions", "CONTEXT_FLAGS.NEW", "GEOM_FLAGS.INVALIDATE_DATA_CACHE", "GEOM_FLAGS.INVALIDATE_PDS_CACHE", "GEOM_FLAGS.INVALIDATE_USE_CACHE"]
+++

**What was read.** Instruction numbers are indices in hex. The kick is entered from the TA pick
(E161) with `r0` the context, `r1` the TA command, `r2` the queue index and `r14` the RT data
(command dword 17). E158 has the second half.

**Results.** In order:

1. *Record (`0x8e9`-`0x8f7`).* TA3DCtl dword 27 = context, 24 = command, 26 = command dword 14
   (the render details, `cmd_ta.hw_render_details_dev_vaddr`), 50 = context dword 16 (the PID);
   `sa4` = the queue index, `sa5` = 0. The render details address is also stored in RT data
   dword 1 (`hw_rt_data.hw_render_details_dev_vaddr`), so a client need not fill that field.
2. *Previous RT data (`0x8f8`-`0x918`).* If TA3DCtl dword 25 holds an RT data other than this
   one, the slot that holds it is cleared (dword 20 or 21, chosen by bit 2 of
   `CR_DPM_STATE_CONTEXT_ID`) and its DPM state is stored in its own context's address space.
3. *Reset (`0x919`-`0x91e`).* With `GEOM_FLAGS.FIRST_KICK` (command dword 1, bit 0) it writes
   `CR_SOFT_RESET` (`0x0080`) = 4 (`TA_RESET`) and then 0.
4. *Parameter buffer (`0x91f`-`0x959`).* The context's PB is context dword 6
   (`hw_render_context.hw_pb_desc_dev_vaddr`); TA3DCtl dwords 46 and 47 are the PB loaded for the
   TA and for the 3D. If dword 46 is already the context's PB, and the PB's flags (its dword 0) have
   bit 1, the routine at `0x1665` writes the thresholds from PB dwords 10-13 to the DPM
   threshold registers `0x0620`, `0x0624`, `0x0628` (low 16 bits, with bit 16) and `0x0668`
   and clears flag bits 1:0. Otherwise: the PB loaded for the TA, if any and not also
   loaded for the 3D, is stored (`0x168d`, four DPM registers into PB dwords 6 to 9); if the
   context's PB is the one loaded for the 3D, the settle routine (E153, argument 1) and
   `0x16d4` run first; then the PB is loaded (`0x170d`, `0x16a2`: free list and page table
   registers `0x0618`, `0x061c`, `0x0648`, `0x0638`, the thresholds, `0x0664`), with the EDM's
   BIF index switched by `0x1864` to the context's address space for the loads and back to the
   EDM's own (`CR_BIF_BANK0` low nibble `0xf`) after, and the nesting count released (`0x15ad`).
5. *TA registers (`0x95a`-`0x985`).* Command dwords 142 to 169 are written, one `str` each, in
   structure order, no table:

   | command dwords | registers written, in order |
   |---|---|
   | 142 to 147 | `0x0204`, `0x0208`, `0x020c`, `0x0210`, `0x0214`, `0x0218` (`CR_TE_AA` first) |
   | 148, 149 | `0x0238` (VDM_CTRL_STREAM_BASE), `0x023c` (MTE_CTRL) |
   | 150, 151 | `0x021c` (TE_PSGREGION_ADDR), `0x0220` (TE_TPC_ADDR) |
   | 152 to 154 | `0x0240` (MTE_RHW_MIN), `0x0244` (MTE_RHW_CLAMP), `0x0248` (PPP_SCREEN) |
   | 155 to 157 | `0x0a04`, `0x0aa0`, `0x0c90` (BIF_TA_REQ_BASE) |
   | 158 to 163 | `0x02b0`, `0x02d4`, `0x02d0`, `0x02b4`, `0x0324`, `0x0368` |
   | 164 to 166 | `0x0364`, `0x0370`, `0x0374` |
   | 167, 168 | `0x074c`, `0x02a8` |
   | 169 | `0x0230` (MTE_MULTISAMPLECTL) |

6. *Vertex partitions (`0x986`-`0x98c`).* Bits 31:27 of `CR_DMS_CTRL` (`0x0a74`) are replaced by
   command dword 5 as it is (`cmd_ta.num_vertex_partitions`, already shifted: `0x50000000` is 10).
7. *Map (`0x98d`-`0x994`).* The context's address space is mapped for the TA (`0x17ec`, `0x184c`),
   which sets the TA's BIF index; with `CONTEXT_FLAGS.NEW` it clears the flag and invalidates
   the caches (the same routine the transfer path uses for the 3D index).
8. *Invalidations (`0x995`-`0x9b6`, by command flags).* `0x40`: bit 28 of `CR_CACHE_CTRL`
   (`0x0804`), wait for status bit 26, acknowledge, a global cache invalidate. `0x20`: `0x0ad0`
   and `0x0ae0` = 1, wait for `0x0138` & `0x27` to be `0x27`, acknowledge with `0x0140` = `0x27`.
   `0x10`: `CR_USE_CACHE` (`0x0a08`) = 1, once per task.

**Not shown.** Which of the TA register values the hardware needs, and what the registers
`0x0a04`, `0x0aa0` and the `0x02b0`-`0x0374` group do: the dwords are copied, so the firmware gives
no field layout. The map routine is only described by what it is called for. Nothing here
runs the firmware.
