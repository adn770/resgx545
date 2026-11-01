<!-- SPDX-License-Identifier: MIT -->
<!-- SPDX-FileCopyrightText: 2026 Josep Torra -->
# SGX545 open glossary rows

*Generated from `glossary/` by `tools/records/open_rows.py`; do not edit.*

The glossary terms whose meaning our evidence has not established: each has the status `inferred`,
and its meaning is our best reading, a hypothesis to test, never a name. Names stay neutral
(`REG_xxxx`, `BITSn_m`) until a test settles them. Each entry gives the term's glossary id, where it
sits, the reading, and the evidence records it rests on.

## registers: (no unit)

- `G0151` `CR_REG_0148` (0x0148): a per-job base address or mode of the 3D and transfer paths for a
  feature these clients leave off. Measured: per-render word the host supplies with the 3D registers
  (transfer command and render details); 0 in captures [infer]. Evidence: E056.
- `G0152` `CR_REG_0400` (0x0400): a pixel output conversion control: bit 25 inverts byte 3 of every
  pixel written (CR_REG_0400.INVERT_BYTE3), 0x80 the default of the other conversions. Measured:
  per-render word from the render details or transfer command; 0x80 in captures [infer]. Evidence:
  E028, E029.
- `G0154` `CR_REG_0800` (0x0800): Register 0x0800: held 0x30 outside a render, 22 bits (0 to 5 and 8
  to 23) take a write, and in every transfer, depth scene and overlapping-triangle scene tried no
  value of it changed an image; what it does is not shown. Evidence: E066, E067, E068, E073.
- `G0155` `CR_REG_0810` (0x0810): a tuning enable left at 1. Measured: set once by the init script
  to 0x1; implemented bits 0; no effect on a fill, copy or triangle in any value [infer]. Evidence:
  E006, E026.
- `G0156` `CR_REG_0814` (0x0814): an enable mask or upper limit left at or near its widest (0xffff
  of 17 implemented bits). Measured: set once by the init script to 0xffff; implemented bits 16:0;
  no effect on a fill, copy or triangle in any value [infer]. Evidence: E006, E026.
- `G0157` `CR_REG_0818` (0x0818): an enable mask or upper limit left at its widest (11 bits all
  ones). Measured: set once by the init script to 0x7ff; implemented bits 10:0; no effect on a fill,
  copy or triangle in any value [infer]. Evidence: E006, E026.

## registers: ISP

- `G0123` `CR_ISP_MSAA.MODE` (0x042c[1:0]): Bits 1:0 of register 0x042c: 0 leaves the single-sample
  image, 1 and 2 each change the 64x64 triangle's image, and 3 hangs the job; the sample count each
  value selects is not shown by the pixel counts. Evidence: E066, E074.
- `G0128` `CR_ISP_POLY_OFFSET_FACTOR` (0x0420): Register 0x0420, loaded from render-details word 6:
  set to 4.0 with the offset in word 5 at 0 it left the flat triangle's stored depth unchanged, so
  what it multiplies is not shown by a triangle with no depth slope. Evidence: E071.
- `G0131` `CR_ISP_REG_04E8` (0x04e8): Register 0x04e8: held 0x100 outside a render, bits 0 and 8
  take a write, and in every transfer, depth scene, overlapping-triangle scene and textured triangle
  tried no value of it changed an image; what it does is not shown. Evidence: E066, E067, E068,
  E073.

## registers: PDS

- `G0148` `CR_PDS_REG_0A78` (0x0a78): a PDS tuning value (6 bits, 0x2c) with no visible effect at
  our loads. Measured: set once by the init script to 0x2c; not the SGX535 register at this offset;
  implemented bits 5:0; no effect on a fill, copy or triangle in any value [infer]. Evidence: E006,
  E026, E045, E141.
- `G0150` `CR_PDS_REG_0ABC.BITS4_1` (0x0abc[4:1]): the number of PDS task slots shared by every data
  master (E140): 0 leaves none, so every job hangs. Measured: 7 from the init script; 0 hangs the
  next job, any other value changes nothing seen [infer]. Evidence: E045, E134, E140.

## registers: TPU

- `G0162` `CR_TPU_LUMA_KEY_ALPHA` (0x0868): Register 0x0868: with the copy's luma-key mode on, the
  threshold in bits 15:8, the alpha written at or below it in bits 23:16 and the alpha written above
  it in bits 31:24; it starts at 0xff008000 (alpha 0 below 128, 0xff above). Bits 7:0 are not
  explained: values 64, 128 and 255 fit no threshold. Evidence: E038, E039.
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

## structs: FRAG_FLAGS

- `G0232` `FRAG_FLAGS.BIT10` (render flags bit10 (0x400)): count this render as the scene's
  completion (the scene's last kick). Measured: at scene-done the EDM increments the RT data set's
  executed_count; set by the client on the scene's last kick [infer]. Evidence: E051, E052.
- `G0233` `FRAG_FLAGS.BIT2` (render flags bit2 (0x4)): Bit 2 of the render flags word: when each job
  ends with its render, set or clear it changed no image; what it keeps in a scene left open is not
  shown. Evidence: E051, E052, E053.

## structs: cmd_ta

- `G0302` `cmd_ta.dpm_reg_074c` (CMDTA+0x29c): as CR_DPM_REG_074C's: the enable (bit 8) and setup of
  a DPM structure that follows the TA data (a second list, as a partial-render or context-switch
  arrangement would need), off in every client. Measured: value the EDM copies verbatim into
  CR_DPM_REG_074C (0x074c); 0 in every capture [infer]. Evidence: E054.
- `G0306` `cmd_ta.reg_0324` (CMDTA+0x288): TA command word 162, loaded into register 0x0324; the job
  leaves it at 0, no value changed the triangle's image, a page address in six numberings made no
  write, and a register readback after 0xffffffff shows only the implemented bits (0xfffffff0).
  Evidence: E054, E056.
- `G0307` `cmd_ta.reg_0364` (CMDTA+0x290): as CR_REG_0364's: context store/resume state of an
  interrupted TA: a 32-bit resume task word, unused while the TA runs to the end. Measured: value
  the EDM copies verbatim into CR_REG_0364 (0x0364); 0 in every capture [infer]. Evidence: E054.
- `G0308` `cmd_ta.reg_0368` (CMDTA+0x28c): as CR_REG_0368's: context store/resume state of an
  interrupted TA: a 15-bit size or count of the stored state. Measured: value the EDM copies
  verbatim into CR_REG_0368 (0x0368); 0 in every capture [infer]. Evidence: E054.
- `G0309` `cmd_ta.reg_0370` (CMDTA+0x294): as CR_REG_0370's: context store/resume state of an
  interrupted TA: a 32-bit resume task word. Measured: value the EDM copies verbatim into
  CR_REG_0370 (0x0370); 0 in every capture [infer]. Evidence: E054.
- `G0310` `cmd_ta.reg_0374` (CMDTA+0x298): as CR_REG_0374's: context store/resume state of an
  interrupted TA: a 32-bit resume task word. Measured: value the EDM copies verbatim into
  CR_REG_0374 (0x0374); 0 in every capture [infer]. Evidence: E054.
- `G0311` `cmd_ta.ta_reg_02b0` (CMDTA+0x278): as CR_TA_REG_02B0's: context store/resume state of an
  interrupted TA: an 8-bit field in 31:24 (state flags). Measured: value the EDM copies verbatim
  into CR_TA_REG_02B0 (0x02b0); 0 in every capture [infer]. Evidence: E054.
- `G0312` `cmd_ta.ta_reg_02b4` (CMDTA+0x284): as CR_TA_REG_02B4's: TA context status: reads 0xff
  after any job, a valid or done mask of the stored state. Measured: value the EDM copies verbatim
  into CR_TA_REG_02B4 (0x02b4); 0 in every capture [infer]. Evidence: E054.
- `G0313` `cmd_ta.ta_reg_02d0` (CMDTA+0x280): as CR_TA_REG_02D0's: the TA's context state base (a
  dword address), read only when an interrupted TA resumes. Measured: value the EDM copies verbatim
  into CR_TA_REG_02D0 (0x02d0); 0 in every capture [infer]. Evidence: E054.
- `G0314` `cmd_ta.ta_reg_02d4` (CMDTA+0x27c): as CR_TA_REG_02D4's: context store/resume state of an
  interrupted TA: a 26-bit size or offset. Measured: value the EDM copies verbatim into
  CR_TA_REG_02D4 (0x02d4); 0 in every capture [infer]. Evidence: E054.
- `G0315` `cmd_ta.te_reg_02a8` (CMDTA+0x2a0): as CR_TE_REG_02A8's: the tiling engine's resume
  position after an interrupted TA: an 8-bit field in 19:12. Measured: value the EDM copies verbatim
  into CR_TE_REG_02A8 (0x02a8); 0 in every capture [infer]. Evidence: E054.
- `G0317` `cmd_ta.use_reg_0a04` (CMDTA+0x26c): as CR_USE_REG_0A04's: the USSE's context store/resume
  state base (a 16-byte address) for an interrupted TA's vertex tasks. Measured: value the EDM
  copies verbatim into CR_USE_REG_0A04 (0x0a04); 0 in every capture [infer]. Evidence: E054.
- `G0318` `cmd_ta.use_reg_0aa0` (CMDTA+0x270): as CR_USE_REG_0AA0's: a USSE resume task word for an
  interrupted TA's vertex tasks. Measured: value the EDM copies verbatim into CR_USE_REG_0AA0
  (0x0aa0); 0 in every capture [infer]. Evidence: E054.

## structs: hw_render_details

- `G0322` `hw_render_details.isp_sample_pos` (HWRENDERDETAILS+0x04c): Render-details word 19, loaded
  into register 0x0520 (all 32 bits implemented, held 0 outside a render); no value of it changed
  any image tried, and no bit of it made a 4x triangle's pixel shader run per sample. Evidence:
  E066, E067, E073, E120.
- `G0326` `hw_render_details.poly_offset_factor` (HWRENDERDETAILS+0x018): Render-details word 6,
  loaded into register 0x0420: set to 4.0 with the units word at 0 it left the flat triangle's
  stored depth unchanged; what it multiplies is not shown. Evidence: E071.
- `G0328` `hw_render_details.reg_0400` (HWRENDERDETAILS+0x008): The render-side word that loads
  register 0x0400: bit 25 inverts bits 31:24 of every pixel the job writes, and no other bit changed
  a pixel; the data come from the render command's word 11, which loads the same register, not from
  the render-details word itself. Evidence: E029.

## structs: transfer_cmd

- `G0340` `transfer_cmd.reg_0400` (TRANSFERCMD+0x038): Transfer command word 14, which loads
  register 0x0400: bit 25 inverts bits 31:24 of every pixel a fill or copy writes, and no other bit
  changed a pixel; over the every-value source exactly the 128 values of bits 31:24 with bit 25 set
  changed the image. Evidence: E029.

## words: FEEDBACK_CTL

- `G0228` `FEEDBACK_CTL.DEPTH_ALWAYS` (atst8/depthf src1 [3:2]): Bits 3:2 of the control word the
  punch-through pass passes in src1: clear in 0xe001, which keeps the nearest copy's pixels (1062
  and 36 pixels), and set in 0xffffffff, which keeps the last copy's (1074 and 24 pixels, the
  depth-always result). Evidence: E083.
- `G0229` `FEEDBACK_CTL.ENABLE` (atst8/depthf src1 bit 14): Bit 14 of the control word the
  punch-through pass passes in src1: set in both words that draw (0xe001, 0xffffffff), clear in
  seven of the nine words that draw nothing; set with bit 0 clear (0xe000, 0xe002) still draws
  nothing. Evidence: E083.
- `G0230` `FEEDBACK_CTL.KEEP` (atst8/depthf src1 bit 0): Bit 0 of the control word the punch-through
  pass passes in src1: set in both words that draw (0xe001, 0xffffffff) and clear in 0xe000 and
  0xe002, which draw nothing; set alone (0x1, 0x3, 0xf, 0x80000001) it draws nothing either.
  Evidence: E083.

## words: ISP state words

- `G0246` `ISP1` (ISP word 1): The second word of the render's ISP state; bits 13 to 25 set one at a
  time left a 4x triangle at the sample rate unchanged, so those bits do not turn per-sample shading
  on. Evidence: E117.

## words: MTE state block words

- `G0252` `OUTSEL.PLANES` (outsel [7:0]): Low bits of the output-select word that turn user clip
  planes on: 0x53001 has plane 0 on and 0x63003 has planes 0 and 1 on; for an enabled plane the
  clip-plane value from the fdpc instruction replaces the distance dword the vertex wrote, and a
  disabled plane ignores it. Evidence: E096.
- `G0261` `SIDEBAND.BIT9` (sideband bit 9): marks the emit that completes the tile: the PBE counts
  the emits with it against its tiles. Measured: needed for an emit to complete its tile: with it
  clear the only emit hangs; an extra emit with it set leaves the PBE queue one emit behind, with it
  clear for one job only; not tile-relative addressing [infer]. Evidence: E030.
- `G0262` `SIDEBAND.BITS8_6` (sideband [8:6] [infer]): a PBE sub-format, downscale or rotation
  field, 0 for plain output (Rogue downscale/source_pos, AGX rotate/flip). Measured: 0 in every
  closed program and capture [infer]. Evidence: E030, E031.

## words: PDS DOUT words

- `G0219` `DOUTU1.BIT2` (doutu U1 [2]): a scheduling hint of pixel and secondary tasks: set or
  clear, no image changes, punch-through included (E137); the ISP visibility counter differs between
  the two punch-through runs and nothing is concluded from it (E137). Measured: set (U1 = 4) in the
  pixel tasks of our fill, copy and triangle jobs [infer]. Evidence: E046, E137, E138.

## words: PDS/pixel task words

- `G0226` `EMIT2.BITS15_8` (EMIT2 (emit2 src0) [15:8]): an emit control field: bit 7 valid, bit 0
  with it (0x81) an emit that writes nothing (a mask or count of 0). Measured: 0x80 in every closed
  program and capture [infer]. Evidence: E046.
- `G0254` `PDS_SIZE.BITS17_16` (PDS_SIZE [17:16]): a size or count of output register banks: at 0, 1
  and 2 the triangle's o1-o3 land elsewhere while o0 does not change, 3 the plain value [infer].
  Evidence: E046, E139.
- `G0257` `PIXEL_EVENT.PT_OFF` (pixel event input ir1 bit 3): Input bit 3 of the pixel-event program
  is named in the punch-through probes but no probe used it, so the 6.1 data show nothing about it
  beyond its name. Evidence: E083.

## words: SR

- `G0266` `SR.SLOT_NUM` (g22 (source bank 5, number 86)): a per-slot id the scheduler assigns,
  constant over a quad. Evidence: E086.
- `G0267` `SR.TASK_ID` (g21 (source bank 5, number 85)): a per-task id the scheduler assigns,
  constant over a 4x4 block of a fill. Evidence: E086.

## words: VDM stream words

- `G0291` `VDM_STATE1.BIT8` (VDM_STATE1 bit 8): marks the constant or no-op state blocks. Measured:
  set on the captured state blocks whose PDS program our current term a constant block or starts a
  no-op USE task, clear on the MTE-state and vertex blocks [infer]. Evidence: E060.
- `G0292` `VDM_STATE1.BITS11_9` (VDM_STATE1 [11:9]): Bits 11:9 of the state task's second word: 0
  removes the 64x64 triangle (4096 background pixels), 1, 3, 4, 5 and 6 give the baseline image, and
  7 hangs the job in the sweep but renders in a probe job, so that value is unsettled; the job
  writes 2. Evidence: E060.
- `G0293` `VDM_STATE1.BITS15_13` (VDM_STATE1 [15:13]): Bits 15:13 of the state task's second word:
  0, 5 and 6 hang the job, 2, 3, 4 and 7 give the baseline image; the job writes 1. Evidence: E060.

## words: texture words T0-T3

- `G0284` `T3.DATA_SIZE` (T3 [26:23]): Bits 26:23 of the fourth sampler word are named in the
  sampler sweep but that sweep varied only the conversion fields; the 6.1 data show nothing about
  this field beyond its name. Evidence: E034.
