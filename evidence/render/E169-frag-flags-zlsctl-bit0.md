+++
id = "E169"
claim = "Bit 4 of the render flags word the TA kick copies into the render details (render details dword 53) makes both of the firmware's code paths that start a render, the 3D kick and the partial-render restart, set bit 0 of CR_ISP_ZLSCTL; with the bit clear they skip that write"
unit = "render"
method = "the cut ukernel (00_ukernel.bin of the firmware-images dataset) disassembled with our usse-dis, read from the writer of the flags word to its readers, with the register rows of the firmware-edm-dataflow table as a cross-check; our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["HW", "RE", "infer"]
date = "2026-11-01"
data = ["firmware-images", "firmware-edm-dataflow"]
terms = ["cmd_ta.frag_flags", "FRAG_FLAGS.SET_ZLSCTL_BIT0", "CR_ISP_ZLSCTL"]
+++

**What was read.** Instruction indices below are those of the stored image (byte offset = index
times 8); a routine is named by its first and last index in the table's notation.

**Results.**

- *The writer.* In the TA kernel-CCB handler (instructions 0x7b1 to 0x7fb) the firmware reads
  dword 14 of the TA command (an address) and dword 7 of it (the render flags word, `ta:7` in
  E050), and stores dword 7 into dword 53 (byte offset 0xd4) of the structure at that address.
  It is the only store to a dword 53 in the image; the image has nine loads from a dword 53
  through various base registers, two of them the ones below.
- *The 3D kick.* The routine at instruction 0x112b (byte 0x8958; the routine that binds the DPM
  context, loads the 3D parameter buffer and programs the 3D registers, in the table's
  comments) loads dword 53 of the structure it was handed, tests bit 4 (mask 0x10) and, with the
  bit clear, goes on without touching `CR_ISP_ZLSCTL` (register 0x0480) at that point. With the
  bit set it reads the register, ORs 1 into it and writes it back (instructions 0x1240 to 0x1243,
  where the firmware-edm-dataflow table lists the write of the register ORed with 0x1).
- *The partial-render restart.* The routine at instructions 0xc23 to 0xdbe (reached after a
  TA terminate, byte 0x6118) does the same with the same word: bit 4 clear skips (instruction
  0xd5f goes to 0xd67), bit 4 set reads register 0x0480, ORs 1 into it and writes it back (0xd63
  to 0xd66). In this routine the register is also written with other masks, earlier, in a
  separate block that tests the register's own bits 21 to 23; that block is not the one bit 4
  selects.
- Both routines also test the word against other masks in neighbouring blocks (0x180 in the
  restart routine); those blocks are not read here.
- The firmware-edm-dataflow table agrees: `CR_ISP_ZLSCTL` has two writes of "ORed with 0x1", at
  0xd66 and 0x1243, and no other write that ORs only bit 0.

**What the hardware adds.** Flipping bit 4 of the render flags word in the kernel-built command
(E050) completes the triangle job with no pixel written, the same outcome as flipping bit 0 of
the render details' ZLS control word (E057), which is what two routes into the same bit predict
**[infer]**.

**Not shown.** What bit 0 of `CR_ISP_ZLSCTL` does inside the ISP beyond the pixel-less outcome of
E057. Which structure the 3D kick's argument is, by its contents: that it is the render details
rests on the dword 14 address the writer uses and on the label the 3D path carries, not on a
run. The depth/stencil buffer bits of the same word (bits 7 and 8) were not read.
