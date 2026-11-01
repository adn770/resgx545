+++
id = "E163"
claim = "The EDM's 3D kick (0x112b-0x12db) records the job in TA3DCtl, picks a DPM slot for the RT data and loads its context unless it is resident, loads the 3D's parameter buffer unless it is loaded, sets the deallocation mode from render flag 0x8, writes the 52 dwords of the render details to 52 registers in structure order with no change except for the render-target index, flag 0x10 and the depth and stencil flags, invalidates the caches, writes the background object (E162) and starts the render with a write of 1 to CR_ISP_START_RENDER; it does not write CR_PDS_EXEC_BASE"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the 3D kick from 0x112b to 0x12da, with the DPM and PB routines it calls (0x17be, 0x16d4, 0x16e9, 0x168d, 0x15ad, 0x15bc) and a scan of every write to register 0x0ab8; fetch offsets read by the rule of the instruction-set specification (a fetch with base plus offset starts one dword after the printed offset, a post-increment fetch starts at the printed offset); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["ta3d_ctl", "CR_DPM_STATE_CONTEXT_ID", "ta3d_ctl.hw_pb_desc_3d", "CR_DPM_3D_DEALLOCATE", "FRAG_FLAGS.NO_DEALLOCATE", "hw_render_details.isp_msaa", "hw_render_details.isp_multisamplectl", "CR_ISP_REG_04DC", "CR_ISP_MULTISAMPLECTL", "CR_ISP_ZLSCTL", "CR_ISP_ZLOAD_BASE", "CR_ISP_ZSTORE_BASE", "CR_ISP_STENCIL_LOAD_BASE", "CR_ISP_STENCIL_STORE_BASE", "CR_ISP_BGOBJDEPTH", "CR_EVENT_PIXEL_PDS_CODE", "CR_EVENT_PIXEL_PDS_DATA", "CR_EVENT_PIXEL_PDS_INFO", "CR_DPM_3D_RT_INDEX", "CR_ISP_REGION_HEADER_BASE", "hw_render_details.zload_base", "hw_render_details.zstore_base", "hw_render_details.stencil_load_base", "hw_render_details.stencil_store_base", "hw_render_details.rt_patch_dev_vaddr", "hw_render_details.rt_patch_list_dev_vaddr", "CR_DMS_CTRL.MAX_NUM_PIXEL_PARTITIONS", "CR_DPM_PARTIAL_RENDER", "FRAG_FLAGS.DEPTH_BUFFER", "FRAG_FLAGS.STENCIL_BUFFER", "CR_ISP_START_RENDER", "CR_PDS_EXEC_BASE"]
+++

**What was read.** Instruction numbers are indices in hex. The 3D pick (E165) calls the kick
with `r0` the context, `r1` the render details, `r2` the queue index, `r13` the render-target
index (render details dword 66) and `r14` the RT data (render details dword 55). Registers are
named by address. The kick's step 12, the background object, is E162.

**Results.** In order:

1. *Record (`0x112b`-`0x1137`).* TA3DCtl dword 51 = context dword 16 (PID), dword 30 = `r13`,
   dword 29 = the render details, dword 42 = render details dword 80 (the frame number); `sa7`
   = context, `sa6` = queue index, `sa5` = 0.
2. *DPM slot (`0x1138`-`0x118c`).* As for the TA (E158), with TA3DCtl dwords 20 and 21 and
   the slot written in bit 1 of `CR_DPM_STATE_CONTEXT_ID`: this RT data's slot, else a free one,
   else the one the TA is not using (bit 2). A previous owner of a different RT data is stored
   only if bit 5 of its dword 13 is set (the scene closed at TA finished, E156). The kick then
   loads this RT data's DPM state through the 3D's address space (`0x17be`, bit 9 of
   `CR_BIF_BANK_SET`), or, if the RT data is already in the slot, only maps the 3D's address
   space (`0x17ec`, `0x184c`).
3. *Parameter buffer (`0x118d`-`0x11ad`).* If TA3DCtl dword 47 (the PB loaded for the 3D) is
   not already the context's PB (context dword 6): the old one, if any and not also the TA's,
   is stored (`0x16d4`); if the context's PB is the one loaded for the TA, the settle routine of
   E153 (argument 2) and the TA's store (`0x168d`) run next; the context's PB is then loaded
   (`0x16e9`) and the nesting count released (`0x15ad`).
4. *Deallocation (`0x11ae`-`0x11ba`).* With render flag `0x8` (render details dword 53,
   `NO_DEALLOCATE`) clear: `sa9` |= `0x30` and `CR_DPM_3D_DEALLOCATE` (`0x063c`) = 3. With it set:
   `sa9` |= `0x10` and `CR_DPM_3D_DEALLOCATE` = 0.
5. *Visibility and box.* `0x0494` (`CR_ISP_VISIBILITY_CTRL`) = `0xff`; `0x040c`, `0x0410` and
   `0x0404` = 0.
6. *The register block (`0x11bf`-`0x1211`).* Render details dwords 0 to 51 are written, one str
   each, in structure order, from fetches that run through the structure from dword 0:

   | render details dwords | registers written, in order |
   |---|---|
   | 0 to 7 | `0x0cac`, `0x0cb0`, `0x0400`, `0x0414`, `0x042c`, `0x041c`, `0x0420`, `0x0424` |
   | 8 to 10 | `0x0408` (region header base), `0x0148`, `0x050c` (partial region base) |
   | 11 to 15 | `0x0480` (ZLS control), `0x0484`, `0x0488` (Z), `0x048c`, `0x0490` (stencil) |
   | 16 to 19 | `0x04b8`, `0x04bc`, `0x04c4` (background depth, values, tag), `0x0520` |
   | 20 to 25 | `0x04c8`, `0x04dc`, `0x0800`, `0x0a5c`, `0x0a60`, `0x0a64` |
   | 26 to 28 | `0x0418`, `0x0a84`, `0x0a88` |
   | 29 to 36 | `0x0a8c`, `0x0a90`, `0x0a94`, `0x0a98`, `0x0b24`, `0x0b28`, `0x0b2c`, `0x0a9c` |
   | 37 to 44 | `0x0820`, `0x0824`, `0x0828`, `0x082c`, `0x0834`, `0x0838`, `0x083c`, `0x0840` |
   | 45 to 47 | `0x0830`, `0x0844`, `0x0848` |
   | 48 to 51 | `0x0860`, `0x0864`, `0x0868`, `0x04e8` |

   The values are copied; the EDM gives no field layout for them. `CR_PDS_EXEC_BASE` (`0x0ab8`) is
   not among the registers: the only write to it in the firmware is the transfer kick's (`0x13db`),
   so the pixel programs of a render are relative to the value a transfer or the init script left.
7. *Render-target index (`0x1212`-`0x1237`).* `CR_DPM_3D_RT_INDEX` (`0x073c`) = `r13`. For
   `r13` not zero: `0x0408` gets `r13` times RT data dword 11 added; the Z load and store bases
   (`0x0484`, `0x0488`) get `r13` times render details dword 70 added and the stencil bases
   (`0x048c`, `0x0490`) `r13` times dword 71. If render details dword 67
   (`hw_render_details.rt_patch_dev_vaddr`) is not zero, the two dwords at dword 68 (the list)
   plus 8 times `r13` are written to the address in dword 67, through the 3D's address space.
8. *Flag `0x10` and partitions (`0x123c`-`0x124b`).* With render flag `0x10`, bit 0 of
   `0x0480` is set. Bits 26:22 of `CR_DMS_CTRL` (`0x0a74`) are replaced by render details
   dword 79 as it is. `CR_DPM_PARTIAL_RENDER` (`0x0658`) = 0.
9. *Caches (`0x124c`-`0x1264`).* Bit 28 of `CR_CACHE_CTRL` (`0x0804`) is set and the EDM waits
   for status bit 26 and acknowledges it; a global cache invalidate; `0x043c` = 1; `CR_USE_CACHE`
   (`0x0a08`) = 1 once per task; `0x0ad4` and `0x0ae0` = 1, wait for `0x0138` & `0x4b` to be
   `0x4b`, acknowledge with `0x0140` = `0x4b`.
10. *ZLS control (`0x1265`-`0x1288`).* From render flags `0x80` (`FRAG_FLAGS.DEPTH_BUFFER`) and
    `0x100` (`FRAG_FLAGS.STENCIL_BUFFER`) and bit 1 of the RT status word of the render-target
    index (set by an earlier partial render, E160), it changes bits of the value now in
    `0x0480`. With the status bit clear: if the flags word has no bit outside `0x180` nothing
    changes; otherwise a clear flag `0x80` removes the bits `0x44000`, a clear flag `0x100`
    removes `0x22000`, and with neither flag set bits 2:1 go as well. With the status bit set,
    flag `0x80` adds `0xc000` and flag `0x100` adds `0x2000`.
11. *Background object* (E162), then TA3DCtl dword 57 = 0, bit 1 of dword 54 set, dword 28 =
    the RT data, `sa9` bit 0 set, the context moved to the head of the 3D queue of its index,
    a type-4 HWPerf record with the page count (E149) if the status asks for it, and
    **`0x0428` (`CR_ISP_START_RENDER`) = 1** (`0x12da`).

**Not shown.** What any of the register values mean: the dwords are copied, so the EDM gives no
bitfield information about them. How the hardware uses the ZLS control bits of step 10. Nothing
here runs the firmware.
