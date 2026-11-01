<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 open glossary rows

*Generated from `glossary/` by `tools/records/open_rows.py`; do not edit.*

The glossary terms whose meaning our evidence has not established: each has the status `inferred`,
and its meaning is our best reading, a hypothesis to test, never a name. Names stay neutral
(`REG_xxxx`, `BITSn_m`) until a test settles them. Each entry gives the term's glossary id, where it
sits, the reading, and the evidence records it rests on.

## registers: (no unit)

- `G0151` `CR_REG_0148` (0x0148): a one-bit (bit 0) per-job mode of the 3D and transfer paths for a
  feature these clients leave off: no value changes a triangle, five copies, a fill or a copy.
  Measured: per-render word the host supplies with the 3D registers (transfer command and render
  details); 0 in captures [infer]. Evidence: E056.
- `G0432` `CR_REG_0324` (0x0324): context store/resume state of an interrupted TA: a state base
  (16-byte aligned, E182), unused while the TA runs to the end. Measured: TA command word; 0 in
  captures [infer]. Evidence: E030, E056, E071, E072, E159, E182, E183.
- `G0433` `CR_REG_0364` (0x0364): context store/resume state of an interrupted TA: a 32-bit resume
  task word, unused while the TA runs to the end. Measured: TA command word; 0 in captures [infer].
  Evidence: E030, E056, E071, E072, E159, E182, E183.
- `G0434` `CR_REG_0368` (0x0368): context store/resume state of an interrupted TA: a 15-bit size or
  count of the stored state. Measured: TA command word; 0 in captures [infer]. Evidence: E030, E056,
  E071, E072, E159, E182, E183.
- `G0435` `CR_REG_0370` (0x0370): context store/resume state of an interrupted TA: a 32-bit resume
  task word. Measured: TA command word; 0 in captures [infer]. Evidence: E030, E056, E071, E072,
  E159, E182, E183.
- `G0436` `CR_REG_0374` (0x0374): context store/resume state of an interrupted TA: a 32-bit resume
  task word. Measured: TA command word; 0 in captures [infer]. Evidence: E030, E056, E071, E072,
  E159, E182, E183.
- `G0152` `CR_REG_0400` (0x0400): a pixel output conversion control: bit 25 inverts the alpha
  channel of every pixel stored, wherever the pack mode puts it (CR_REG_0400.INVERT_BYTE3); bits 7:0
  are the threshold of the one-bit alpha of ARGB1555 (pack mode 4) and change no pixel in pack modes
  0 to 3, bits 11:8 change no pixel in modes 0 to 4 (E385), 0x80 the default of the other
  conversions. Measured: per-render word from the render details or transfer command; 0x80 in
  captures [infer]. Evidence: E028, E029, E330, E385.
- `G1030` `CR_REG_0400.BITS11_0` (0x0400[11:0]): twelve bits the register takes (0x80 as the library
  and the closed stack write them) of which bits 7:0 are the threshold of ARGB1555's one-bit alpha
  (pack mode 4, E385) and change no stored pixel in pack modes 0 to 3, and bits 11:8 change no
  stored pixel in pack modes 0 to 4 [infer]. Evidence: E385.
- `G0154` `CR_REG_0800` (0x0800): an on-chip resource limit (bits 5:0 = 48, bits 23:8) for work
  other than pixel tasks (vertex or state tasks, context switches); pixel-bound renders ignore it
  (E136). Measured: set by the init script and per render; 0x30 everywhere [infer]. Evidence: E006,
  E066, E067, E068, E073, E136, E225.
- `G0155` `CR_REG_0810` (0x0810): a tuning enable left at 1. Measured: set once by the init script
  to 0x1; implemented bits 0; no effect on a fill, copy or triangle in any value [infer]. Evidence:
  E006, E026.
- `G0156` `CR_REG_0814` (0x0814): an enable mask or upper limit left at or near its widest (0xffff
  of 17 implemented bits). Measured: set once by the init script to 0xffff; implemented bits 16:0;
  no effect on a fill, copy or triangle in any value [infer]. Evidence: E006, E026.
- `G0157` `CR_REG_0818` (0x0818): an enable mask or upper limit left at its widest (11 bits all
  ones). Measured: set once by the init script to 0x7ff; implemented bits 10:0; no effect on a fill,
  copy or triangle in any value [infer]. Evidence: E006, E026.

## registers: DPM

- `G1080` `CR_DPM_REG_0730` (0x0730): the 3D side's global page count: 1 while the 3D holds the
  global page, from the first render or partial render of a job until the final render frees its
  last page, the TA's runs between partial renders included; 0 otherwise [infer].
- `G1081` `CR_DPM_REG_0738` (0x0738): a DPM flag that reads 1 when no render runs and 0 from a
  render's (or a partial render's) start to its end [infer].
- `G1082` `CR_DPM_REG_0748` (0x0748): a DPM state word: 0x1f idle and from the last TA's end, 0xf
  while the TA holds pages and through a partial render, 0x7 in some samples while the TA takes
  pages, the 1024x768 abort among them; its bits one by one are not shown [infer].
- `G0378` `CR_DPM_REG_074C` (0x074c): the enable (bit 8) of a DPM access near offset 0x6010 of the
  context's TA-data space, fixed whatever CR_DPM_STATE_BASE1 holds; with that place mapped the job
  is unchanged; off in every client. Measured: TA command word; 0 in captures [infer]. Evidence:
  E030, E056, E071, E072, E159, E203, E206.

## registers: ISP

- `G0128` `CR_ISP_POLY_OFFSET_FACTOR` (0x0420): the polygon offset's factor, an IEEE single
  (glPolygonOffset factor) [infer]. Evidence: E071, E291, E330, E338.
- `G0131` `CR_ISP_REG_04E8` (0x04e8): what it does is not shown: no value tried changes an image or
  a count in any scene; not the background's stencil or mask (E216); 0x100 from the init script and
  per render [infer]. Evidence: E006, E066, E067, E068, E073, E216, E285.

## registers: PDS

- `G0148` `CR_PDS_REG_0A78` (0x0a78): a PDS tuning value (6 bits, 0x2c) with no visible effect at
  our loads. Measured: set once by the init script to 0x2c; not the SGX535 register at this offset;
  implemented bits 5:0; no effect on a fill, copy or triangle in any value [infer]. Evidence: E006,
  E026, E045, E141.
- `G0150` `CR_PDS_REG_0ABC.BITS4_1` (0x0abc[4:1]): the number of PDS task slots shared by every data
  master (E140): 0 leaves none, so every job hangs. Measured: 7 from the init script; 0 hangs the
  next job, any other value changes nothing seen [infer]. Evidence: E045, E134, E140.

## registers: TA

- `G0440` `CR_TA_REG_02B0` (0x02b0): context store/resume state of an interrupted TA: an 8-bit field
  in 31:24 (state flags). Measured: TA command word; 0 in captures [infer]. Evidence: E030, E056,
  E071, E072, E159, E182, E183.
- `G0441` `CR_TA_REG_02B4` (0x02b4): TA context status: reads 0xff after any job, a valid or done
  mask of the stored state. Measured: TA command word; 0 in captures [infer]. Evidence: E030, E056,
  E071, E072, E159, E182, E183.
- `G0442` `CR_TA_REG_02D0` (0x02d0): the TA's context state base (a dword address), read only when
  an interrupted TA resumes. Measured: TA command word; 0 in captures [infer]. Evidence: E030, E056,
  E071, E072, E159, E182, E183.
- `G0443` `CR_TA_REG_02D4` (0x02d4): context store/resume state of an interrupted TA: a 26-bit size
  or offset. Measured: TA command word; 0 in captures [infer]. Evidence: E030, E056, E071, E072,
  E159, E182, E183.

## registers: TE

- `G0447` `CR_TE_MACROTILE_STRIDE` (0x0214): macrotile stride of the tiling engine, from the TA
  command (0x10 for 64x64) [infer]. Evidence: E159, E175, E328.
- `G0452` `CR_TE_REG_02A8` (0x02a8): the tiling engine's resume position after an interrupted TA: an
  8-bit field in 19:12. Measured: TA command word; 0 in captures [infer]. Evidence: E030, E056,
  E071, E072, E159, E182, E183.

## registers: TPU

- `G0162` `CR_TPU_LUMA_KEY_ALPHA` (0x0868): Register 0x0868: with the copy's luma-key mode on, a
  luma band and two alphas: bits 7:0 its low end and bits 15:8 its high end (the threshold),
  alpha_below (bits 23:16) for a luma inside the band and alpha_above (bits 31:24) outside it; it
  starts at 0xff008000 (a band of 0 to 128, alpha 0 inside, 0xff outside). Evidence: E038, E039.
- `G0163` `CR_TPU_LUMA_KEY_B_OFFSET` (0x0864): Register 0x0864: with the copy's luma-key mode on,
  the B weight in bits 9:0 (1024ths) and an offset in bits 23:16 that enters the sum as 512 times
  its value; it starts at 0x00210064 (weight 100, offset 33). Evidence: E038, E039.
- `G0164` `CR_TPU_LUMA_KEY_RG` (0x0860): Register 0x0860: with the copy's luma-key mode on, the R
  weight in bits 9:0 and the G weight in bits 25:16, in 1024ths, of the weighted sum that decides
  the alpha; it starts at 0x02020106 (weights 262 and 514). Evidence: E038, E039.
- `G0170` `CR_TPU_YUV_CSC1_0` (0x0834): Word 0 of colour-space set 1, loaded like set 0; in the UYVY
  copy tried no value or bit of it selected the set, so what it converts is not shown. Evidence:
  E038, E040.
- `G0171` `CR_TPU_YUV_CSC1_1` (0x0838): Word 1 of colour-space set 1, loaded like set 0; in the UYVY
  copy tried no value or bit of it selected the set, so what it converts is not shown. Evidence:
  E038, E040.
- `G0172` `CR_TPU_YUV_CSC1_2` (0x083c): Word 2 of colour-space set 1, loaded like set 0; in the UYVY
  copy tried no value or bit of it selected the set, so what it converts is not shown. Evidence:
  E038, E040.
- `G0173` `CR_TPU_YUV_CSC1_3` (0x0840): Word 3 of colour-space set 1, loaded like set 0; in the UYVY
  copy tried no value or bit of it selected the set, so what it converts is not shown. Evidence:
  E038, E040.
- `G0174` `CR_TPU_YUV_CSC1_4` (0x0844): Word 4 of colour-space set 1, loaded like set 0; in the UYVY
  copy tried no value or bit of it selected the set, so what it converts is not shown. Evidence:
  E038, E040.

## registers: USE

- `G0456` `CR_USE_REG_0A04` (0x0a04): the USSE's context store/resume state base (a 16-byte address)
  for an interrupted TA's vertex tasks. Measured: USSE word from the TA command; 0 in captures
  [infer]. Evidence: E030, E056, E071, E072, E159, E182, E183.
- `G0457` `CR_USE_REG_0AA0` (0x0aa0): a USSE resume task word for an interrupted TA's vertex tasks.
  Measured: USSE word from the TA command; 0 in captures [infer]. Evidence: E030, E056, E071, E072,
  E159, E182, E183.

## structs: FRAG_FLAGS

- `G0232` `FRAG_FLAGS.BIT10` (render flags bit10 (0x400)): count this render in its RT data set: at
  the render's completion the EDM adds one to the executed count of the set render details word 54
  points at; without it the render is drawn and adds nothing, so the set's cleanup completes only if
  the host's pending count leaves the render out too (the kernel's does since it counts each kick);
  set by the client on the scene's last kick [infer]. Evidence: E051, E052, E164, E166, E314, E315,
  E324.
- `G0233` `FRAG_FLAGS.BIT2` (render flags bit2 (0x4)): Bit 2 of the render flags word: when each job
  ends with its render, set or clear it changed no image; after the render it keeps TA3DCtl dword
  20, the DPM slot's RT data, as NO_DEALLOCATE does; a later render with it clear clears the word,
  and a new context at the same addresses renders exactly and clears it; a context at another
  address is not tried. Evidence: E051, E052, E053, E316.

## structs: GEOM_FLAGS

- `G0630` `GEOM_FLAGS.BIT2` (CMDTA+0x004 bit2 (0x4)): tested together with GEOM_FLAGS.FIRST_KICK
  (mask 0x5): when either is set the EDM keeps the stores that link the command's render details
  into the context; no run sets the bit alone [infer]. Evidence: E172.

## structs: cmd_ta

- `G0302` `cmd_ta.dpm_reg_074c` (CMDTA+0x29c): as CR_DPM_REG_074C's: the enable (bit 8) and setup of
  a DPM structure that follows the TA data (a second list, as a partial-render or context-switch
  arrangement would need), off in every client. Measured: value the EDM copies verbatim into
  CR_DPM_REG_074C (0x074c); 0 in every capture [infer]. Evidence: E054, E159, E203, E206.
- `G0306` `cmd_ta.reg_0324` (CMDTA+0x288): as CR_REG_0324's: context store/resume state of an
  interrupted TA: a state base (16-byte aligned, E182), unused while the TA runs to the end.
  Measured: value the EDM copies verbatim into CR_REG_0324 (0x0324); 0 in every capture [infer].
  Evidence: E054, E056, E159, E182, E183.
- `G0307` `cmd_ta.reg_0364` (CMDTA+0x290): as CR_REG_0364's: context store/resume state of an
  interrupted TA: a 32-bit resume task word, unused while the TA runs to the end. Measured: value
  the EDM copies verbatim into CR_REG_0364 (0x0364); 0 in every capture [infer]. Evidence: E054,
  E159, E182, E183.
- `G0308` `cmd_ta.reg_0368` (CMDTA+0x28c): as CR_REG_0368's: context store/resume state of an
  interrupted TA: a 15-bit size or count of the stored state. Measured: value the EDM copies
  verbatim into CR_REG_0368 (0x0368); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0309` `cmd_ta.reg_0370` (CMDTA+0x294): as CR_REG_0370's: context store/resume state of an
  interrupted TA: a 32-bit resume task word. Measured: value the EDM copies verbatim into
  CR_REG_0370 (0x0370); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0310` `cmd_ta.reg_0374` (CMDTA+0x298): as CR_REG_0374's: context store/resume state of an
  interrupted TA: a 32-bit resume task word. Measured: value the EDM copies verbatim into
  CR_REG_0374 (0x0374); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0567` `cmd_ta.stencil_rt_stride` (CMDTA+0x050): TA command word 20, copied by the TA kick to
  render details word 71, the stencil stride per render target [infer]. Evidence: E158, E163.
- `G0311` `cmd_ta.ta_reg_02b0` (CMDTA+0x278): as CR_TA_REG_02B0's: context store/resume state of an
  interrupted TA: an 8-bit field in 31:24 (state flags). Measured: value the EDM copies verbatim
  into CR_TA_REG_02B0 (0x02b0); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0312` `cmd_ta.ta_reg_02b4` (CMDTA+0x284): as CR_TA_REG_02B4's: TA context status: reads 0xff
  after any job, a valid or done mask of the stored state. Measured: value the EDM copies verbatim
  into CR_TA_REG_02B4 (0x02b4); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0313` `cmd_ta.ta_reg_02d0` (CMDTA+0x280): as CR_TA_REG_02D0's: the TA's context state base (a
  dword address), read only when an interrupted TA resumes. Measured: value the EDM copies verbatim
  into CR_TA_REG_02D0 (0x02d0); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0314` `cmd_ta.ta_reg_02d4` (CMDTA+0x27c): as CR_TA_REG_02D4's: context store/resume state of an
  interrupted TA: a 26-bit size or offset. Measured: value the EDM copies verbatim into
  CR_TA_REG_02D4 (0x02d4); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0655` `cmd_ta.te_macrotile_stride` (CMDTA+0x248): TA command word 146, which the TA kick writes
  to CR_TE_MACROTILE_STRIDE (0x0214); its reading is the register's [infer]. Evidence: E159.
- `G0315` `cmd_ta.te_reg_02a8` (CMDTA+0x2a0): as CR_TE_REG_02A8's: the tiling engine's resume
  position after an interrupted TA: an 8-bit field in 19:12. Measured: value the EDM copies verbatim
  into CR_TE_REG_02A8 (0x02a8); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0317` `cmd_ta.use_reg_0a04` (CMDTA+0x26c): as CR_USE_REG_0A04's: the USSE's context store/resume
  state base (a 16-byte address) for an interrupted TA's vertex tasks. Measured: value the EDM
  copies verbatim into CR_USE_REG_0A04 (0x0a04); 0 in every capture [infer]. Evidence: E054, E159,
  E182, E183.
- `G0318` `cmd_ta.use_reg_0aa0` (CMDTA+0x270): as CR_USE_REG_0AA0's: a USSE resume task word for an
  interrupted TA's vertex tasks. Measured: value the EDM copies verbatim into CR_USE_REG_0AA0
  (0x0aa0); 0 in every capture [infer]. Evidence: E054, E159, E182, E183.
- `G0568` `cmd_ta.z_rt_stride` (CMDTA+0x04c): TA command word 19, copied by the TA kick to render
  details word 70, the depth stride per render target [infer]. Evidence: E158, E163.

## structs: hw_render_context

- `G1103` `hw_render_context.param_obj_dev_vaddr` (HWRENDERCONTEXT+0x01c): the address of a
  0x40-byte object in the parameter heap, at the DPM page table's base plus 0x40000 in both stacks;
  no path run (a render, a scene, a partial render, a cleanup) uses the word's value; the word and
  the object are unchanged (Q049) [infer]. Evidence: E323, E361.

## structs: hw_render_details

- `G0693` `hw_render_details.isp_reg_04dc` (HWRENDERDETAILS+0x054): as CR_ISP_REG_04DC's: a
  punch-through mode word (bit 1 hangs every punch-through pass, E222). Measured: value the EDM
  copies verbatim into CR_ISP_REG_04DC (0x04dc) [infer]. Evidence: E163, E213, E222.
- `G0694` `hw_render_details.isp_reg_04e8` (HWRENDERDETAILS+0x0cc): as CR_ISP_REG_04E8's: what it
  does is not shown; not the background's stencil or mask (E216). Measured: value the EDM copies
  verbatim into CR_ISP_REG_04E8 (0x04e8) [infer]. Evidence: E163, E216.
- `G0322` `hw_render_details.isp_sample_pos` (HWRENDERDETAILS+0x04c): value the EDM copies verbatim
  into CR_ISP_SAMPLE_POS (0x0520): the four sample positions (0 in the capture) [infer]. Evidence:
  E066, E067, E073, E120, E163, E214, E224.
- `G0326` `hw_render_details.poly_offset_factor` (HWRENDERDETAILS+0x018): value the EDM copies into
  CR_ISP_POLY_OFFSET_FACTOR [infer]. Evidence: E071, E338.
- `G0696` `hw_render_details.reg_0148` (HWRENDERDETAILS+0x024): render details word 9, which the 3D
  kick writes to CR_REG_0148 (0x0148); what it holds is not shown [infer]. Evidence: E163.
- `G0328` `hw_render_details.reg_0400` (HWRENDERDETAILS+0x008): The render-side word that loads
  register 0x0400: bit 25 inverts bits 31:24 of every pixel the job writes, and no other bit changed
  a pixel; the data come from the render command's word 11, which loads the same register, not from
  the render-details word itself. Evidence: E029.
- `G0697` `hw_render_details.reg_0800` (HWRENDERDETAILS+0x058): as CR_REG_0800's: an on-chip
  resource limit (bits 5:0 = 48, bits 23:8) for work other than pixel tasks (vertex or state tasks,
  context switches); pixel-bound renders ignore it (E136). Measured: value the EDM copies verbatim
  into CR_REG_0800 (0x0800) (it holds 0x30 outside a render, E225) [infer]. Evidence: E163, E225.
- `G0583` `hw_render_details.stencil_rt_stride` (HWRENDERDETAILS+0x11c): render details word 71: for
  a render target other than the first the 3D kick adds its index times this word to the stencil
  load and store bases (0x048c, 0x0490) [infer]. Evidence: E158, E163.
- `G0590` `hw_render_details.z_rt_stride` (HWRENDERDETAILS+0x118): render details word 70: for a
  render target other than the first the 3D kick adds its index times this word to the Z load and
  store bases (0x0484, 0x0488) [infer]. Evidence: E158, E163.

## structs: hw_rt_data

- `G1106` `hw_rt_data.blocks_per_mtile` (HWRTDATA+0x008): a size word of the RT data that follows
  the macrotile rule: the blocks of one macrotile [infer]. Evidence: E331.
- `G1109` `hw_rt_data.mtile_region_bytes` (HWRTDATA+0x00c): a size word of the RT data: 0xc0 bytes
  per block of hw_rt_data.blocks_per_mtile [infer]. Evidence: E331.
- `G0592` `hw_rt_data.region_header_rt_stride` (HWRTDATA+0x02c): RT data word 11: for a render
  target other than the first the 3D kick adds its index times this word to the region header base
  (0x0408) [infer]. Evidence: E163.

## structs: hw_rt_data_set

- `G1113` `hw_rt_data_set.tiles_across` (HWRTDATASET+0x008): the number of macrotiles across times
  the macrotile's width in tiles, as the size rule of the TA words gives it [infer]. Evidence: E325,
  E331.

## structs: pb_block

- `G0593` `pb_block.first_page`: a PB block's third word: the closed client and our kernel both hold
  the PB descriptor's own address there; how the page-table builder uses it is a reading [infer].
  Evidence: E200, E201.
- `G1115` `pb_block.stack_top`: head (15:0) and tail (31:16) page of this PB block [infer].
  Evidence: E200, E327.

## structs: ta3d_ctl

- `G0722` `ta3d_ctl.abort_page_count0` (TA3D_CTL+0x08c): a page count saved at a macrotile abort,
  from 0x0724 (CR_DPM_PAGE_STATUS) less 2, which a later out-of-memory compares with the current one
  [infer]. Evidence: E160.
- `G0723` `ta3d_ctl.abort_page_count1` (TA3D_CTL+0x090): a page count saved at a macrotile abort,
  from 0x072c less 2, which a later out-of-memory compares with the current one [infer]. Evidence:
  E160.
- `G0730` `ta3d_ctl.kick_clear_3d` (TA3D_CTL+0x0e4): a word the 3D kick clears; what sets it is not
  shown [infer]. Evidence: E163.
- `G0731` `ta3d_ctl.kick_clear_ta` (TA3D_CTL+0x0dc): a word the TA kick, the TA-finished handler and
  the out-of-memory path clear; what sets it is not shown [infer]. Evidence: E156, E158, E160.
- `G0732` `ta3d_ctl.kick_marks` (TA3D_CTL+0x0d8): kick marks: bit 0 set by the TA kick and the
  TA-finished handler, bit 1 by the 3D kick; what reads them is not shown [infer]. Evidence: E156,
  E158, E163.
- `G1076` `ta3d_ctl.render_context_count` (TA3D_CTL+0x0c4): TA3DCtl dword 49: the bus interface
  directory list (0 to 14) the EDM last gave a render context's page directory: a kick whose
  directory is in no list writes it into the next list's CR_BIF_DIR_LIST_BASEn (BASE0 for 0) and
  advances the word, mod 15 because list 15 is the EDM's own; the name is older than the reading
  [infer]. Evidence: E314, E316, E319, E360.
- `G0735` `ta3d_ctl.saved_ta_global_list` (TA3D_CTL+0x084): CR_DPM_TA_GLOBAL_LIST as the
  out-of-memory path saves it before it grows the TA's global list; the global kind of out-of-memory
  writes it back [infer]. Evidence: E160.
- `G0740` `ta3d_ctl.threshold_ta_global_list` (TA3D_CTL+0x094): the TA global list as the
  out-of-memory path saves it when it raises the ZLS page threshold [infer]. Evidence: E160.
- `G0741` `ta3d_ctl.zls_threshold_step` (TA3D_CTL+0x098): the step (0x20) the out-of-memory path
  adds to CR_DPM_ZLS_PAGE_THRESHOLD when it raises the threshold [infer]. Evidence: E160.

## structs: transfer_cmd

- `G0340` `transfer_cmd.reg_0400` (TRANSFERCMD+0x038): Transfer command word 14, which loads
  register 0x0400: bit 25 inverts bits 31:24 of every pixel a fill or copy writes, and no other bit
  changed a pixel; over the every-value source exactly the 128 values of bits 31:24 with bit 25 set
  changed the image. Evidence: E029.

## units

- `G0607` `MADD` (0x0004[13:12] (MADD0)): per the SGX540's technical reference manual, the wrapper
  of the main cache: arbitrates the PDS, USSE and texture requests, caches them at level 0 and
  decompresses textures; one of two readings (Q048) [infer].

## words: FEEDBACK_CTL

- `G0228` `FEEDBACK_CTL.DEPTH_ALWAYS` (atst8/depthf src1 [3:2]): either bit set makes the kept
  pixel's depth win unconditionally (its depth test as always) [infer]. Evidence: E083, E218.
- `G0229` `FEEDBACK_CTL.ENABLE` (atst8/depthf src1 bit 14): the punch-through feedback is valid;
  clear, the pixel is discarded whatever bit 0 says [infer]. Evidence: E083, E218.
- `G0230` `FEEDBACK_CTL.KEEP` (atst8/depthf src1 bit 0): with FEEDBACK_CTL.ENABLE, the punch-through
  feedback keeps the pixel; clear, it discards it [infer]. Evidence: E083, E218.

## words: ISP state words

- `G1059` `ISP0.BIT9` (isp0 bit 9): set in every ISP word 0 the library builds; clearing it changes
  no image of five overlapping copies, so what it selects is not shown, and the block's layout does
  not move with it [infer].
- `G1062` `ISP0.ISP2_PRESENT` (isp0 bit 8): ISP word 2 follows [infer]. Evidence: E332.
- `G0246` `ISP1` (ISP word 1): ISP colour-mask and line-width word of the MTE state [infer].
  Evidence: E117, E332.

## words: MTE state block words

- `G0252` `OUTSEL.PLANES` (outsel [7:0]): user clip-plane enables, bit N plane N: each enabled plane
  removes the triangle whole while its held state is outside: fdpc on cpN sets the state, and it
  outlives the job; the vertex's distance dwords after the position (plane 0 the first, planes 0 and
  1 the first two) decided in one session and decided nothing in another [infer]. Evidence: E096,
  E198.
- `G0261` `SIDEBAND.BIT9` (sideband bit 9): marks the emit that completes the tile: the PBE counts
  the emits with it against its tiles. Measured: needed for an emit to complete its tile: with it
  clear the only emit hangs; an extra emit with it set leaves the PBE queue one emit behind, with it
  clear for one job only; not tile-relative addressing [infer]. Evidence: E030, E239, E240, E333.
- `G0262` `SIDEBAND.BITS8_6` (sideband [8:6] [infer]): the channel a one-channel pack mode stores:
  in mode 8, 0 alpha, 1 red, 2 green, 3 reads as blue and 4 to 7 give the same bytes (both colours
  run have blue 0x40, so blue is not told apart from another source of that byte); no effect seen in
  the modes that store several channels, under multisampling or on several tiles. Measured: 0 in
  every closed program and capture [infer]. Evidence: E030, E031.

## words: PDS DOUT words

- `G1098` `DOUTD1.STRIDE` (doutd word 1 [29:22]): distance between burst lines - 1 [infer].
  Evidence: E347.
- `G0219` `DOUTU1.BIT2` (doutu U1 [2]): a scheduling hint of pixel and secondary tasks: set or
  clear, no image changes, punch-through included (E137); the ISP visibility counter differs between
  the two punch-through runs and nothing is concluded from it (E137). Measured: set (U1 = 4) in the
  pixel tasks of our fill, copy and triangle jobs [infer]. Evidence: E046, E137, E138.

## words: PDS/pixel task words

- `G1039` `EMIT2.BIT28` (EMIT2 (emit2 src0) [28]): set, the end-of-tile emit stores the image
  rotated by 90 degrees (bits 29:28 at 1): on a 64x64 target the pixel stored at (X, Y) is the one
  from (Y, 63 - X); with bit 29 as well (3) the rotation is by 270 degrees (E382). Evidence: E382.
- `G1040` `EMIT2.BIT29` (EMIT2 (emit2 src0) [29]): set, the end-of-tile emit stores the image
  rotated by 180 degrees (bits 29:28 at 2): on a 64x64 target the pixel stored at (X, Y) is the one
  from (63 - X, 63 - Y); with bit 28 as well (3) the rotation is by 270 degrees (E382). Evidence:
  E382.
- `G1041` `EMIT2.BIT30` (EMIT2 (emit2 src0) [30]): set, the end-of-tile emit stores each 32x16 tile
  downscaled by 2 in x and y into the tile's top-left 16x8 pixels, each pixel the 2x2 box average of
  its four (each byte summed, divided by 4, the remainder dropped), and leaves the rest of the tile
  unwritten [infer]. Evidence: E382.
- `G0226` `EMIT2.BITS15_8` (EMIT2 (emit2 src0) [15:8]): a count, in units of four pixels, of what an
  emit stores of its 32x16 tile: 0 stores nothing, every odd value hangs the job, an even value v up
  to 0x80 stores 4v pixels of each tile, and above 0x80 the tile is stored with other values over
  it. Measured: 0x80 in every closed program and capture [infer]. Evidence: E046.
- `G0254` `PDS_SIZE.BITS17_16` (PDS_SIZE [17:16]): a size or count of output register banks: at 0, 1
  and 2 the triangle's o1-o3 land elsewhere while o0 does not change, 3 the plain value [infer].
  Evidence: E046, E139, E343.
- `G0636` `PDS_SIZE.BITS24_18` (PDS_SIZE [24:18]): bits 24:18 of the PDS size word; at 4, 1 and 0 a
  fill's secondary program still passes all sixteen douta words, so what they size is not shown
  [infer]. Evidence: E125.
- `G0257` `PIXEL_EVENT.PT_OFF` (pixel event input ir1 bit 3): Input bit 3 of the pixel-event program
  is named in the punch-through probes but no probe used it, so the 6.1 data show nothing about it
  beyond its name. Evidence: E083.

## words: PDS_MOV128

- `G1151` `PDS_MOV128.LASTPAIR` (mov128 [15]): Bit 15 of a mov128 word, which the assembler spells
  `, lastpair`: set, the instruction writes to both halves of its destination row the ds0 pair that
  the last mov32 or movs read from a data row, whatever its source row and swap (E379); measured
  only after the instructions E379 lists [infer]. Evidence: E379.

## words: SR

- `G0266` `SR.SLOT_NUM` (g22 (source bank 5, number 86)): a per-slot id the scheduler assigns,
  constant over a quad. Evidence: E086.
- `G0267` `SR.TASK_ID` (g21 (source bank 5, number 85)): a per-task id the scheduler assigns,
  constant over a 4x4 block of a fill. Evidence: E086.

## words: VDM stream words

- `G0498` `VDM_INDEX2.WORD` (index list, the first trailing word): the index list's first trailing
  word: an offset of the list's first index in its low bits [infer: 1, 2, 3, 5 and 0xff fit;
  0x0f000000 drops two of five triangles, which such an offset does not explain]; bits 31:28 change
  nothing seen. Measured: 0xf0000000 in every capture. Evidence: E188.
- `G0291` `VDM_STATE1.BIT8` (VDM_STATE1 bit 8): marks the constant or no-op state blocks. Measured:
  set on the captured state blocks whose PDS program loads a constant block or starts a no-op USE
  task, clear on the MTE-state and vertex blocks [infer]. Evidence: E060, E187, E349.
- `G0292` `VDM_STATE1.BITS11_9` (VDM_STATE1 [11:9]): Bits 11:9 of the state task's second word: 0
  removes the 64x64 triangle (4096 background pixels), 1, 3, 4, 5 and 6 give the baseline image, and
  7 hangs some runs of either job and completes others, tiling as 2 when it completes; the job
  writes 2. Evidence: E060.
- `G0293` `VDM_STATE1.BITS15_13` (VDM_STATE1 [15:13]): Bits 15:13 of the state task's second word:
  0, 5 and 6 hang the job, 2, 3, 4 and 7 give the baseline image; the job writes 1. Evidence: E060.

## words: texture words T0-T3

- `G1045` `T0.BIT27` (T0 [27]): changes the form texels are read in: set in a copy, every pixel
  takes a value of no source texel (0x00000000, 0x0cf90cf9, 0x10f910f9, ...) [infer].
- `G0639` `T0.BIT30` (T0 [30]): with it TEXFORMAT 26 reads one byte per texel, written as grey;
  without it TEXFORMAT 26 gives values that differ from run to run; no other format is tried with it
  [infer]. Evidence: E040.
- `G0278` `T0.NO_MIPMAPS` (T0 bit 18): bit 1 of T0.MAX_LEVEL (20:17), not a mipmap disable: values
  of the field with this bit set (2, 3, 6, 7, ...) read the chain up to that level [infer].
  Evidence: E041.
- `G1047` `T3.BIT10` (T3 [10]): set in a copy, every pixel reads texel (0, 0); what it selects is
  not decoded [infer].
- `G1048` `T3.BIT14` (T3 [14]): set in a copy, pixel (x, y) reads texel (x + 32, y + x), past the
  source at the sentinel; what it selects is not decoded [infer].
- `G1049` `T3.BITS19_18` (T3 [19:18]): a scale of the texel coordinates: bit 18 reads (2x, 2y), bit
  19 (4x, 4y) in a copy [infer].
- `G1050` `T3.BITS28_27` (T3 [28:27]): in a copy, bit 27 reads a half-size image packed 32 rows (8
  KiB) after the source and bit 28 a quarter-size one 40 rows after it, at the source's stride: a
  level select of strided textures [infer].
- `G1051` `T3.BITS7_0` (T3 [7:0]): a texel offset: bits 7:4 in x and 3:0 in y, each a signed 4-bit
  count (single bits move the read by 1, 2, 4 and -8 texels), clamped at the texture's edge [infer].
- `G0284` `T3.DATA_SIZE` (T3 [26:23]): Bits 26:23 of the fourth sampler word are named in the
  sampler sweep but that sweep varied only the conversion fields; the sampler data show nothing
  about this field beyond its name. Evidence: E034, E242.

## words: the TA's parameter buffer and TA data

- `G1073` `PB_OBJ.FORMAT` (TA object, the dword after the line widths): the object's format word:
  bits 7:0 the dwords a vertex takes in the object, bits 15:8 the dwords it iterates; bit 18 with
  the 1/w output select, bit 19 with the vertex colour; the other bits are not shown [infer].
- `G0487` `PB_OBJ.RHW` (TA object TSP data, first dword of each vertex): 1/w of the vertex, before
  its outputs, which are stored undivided [infer]. Evidence: E176, E196.
