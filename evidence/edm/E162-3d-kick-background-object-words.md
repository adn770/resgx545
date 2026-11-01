+++
id = "E162"
claim = "At each 3D kick the EDM writes dwords 0, 1 and 2 of the RT data's background object, in the 3D's address space, from render details dwords 76 and 77 and from the word of the render-target-indexed list that render details dword 69 points at (list base plus 4 times the RT index); the TA kick has copied render details dwords 76 to 78 from command dwords 2 to 4"
unit = "edm"
method = "the ukernel of the cut firmware (00_ukernel.bin of firmware-images, 6637 instructions) disassembled with our usse-dis and read by hand: the 3D kick from 0x128d to 0x1296, and the TA kick's copy routine at 0x7b1; fetch offsets read by the rule of the instruction-set specification (a fetch with base plus offset starts one dword after the printed offset, a post-increment fetch or store starts at the printed offset); our disassembly of the firmware, for interoperability; facts only, no code"
tiers = ["RE"]
date = "2026-11-01"
data = ["firmware-images"]
terms = ["hw_rt_data.bgobj_dev_vaddr", "hw_render_details.pds_bgnd", "hw_render_details.pds_bgnd_list_dev_vaddr", "cmd_ta.pds_bgnd"]
+++

**What was read.** Instruction numbers are indices in hex. In the 3D kick (E163) `r1` is the render
details, `r13` the render-target index and `r14` the RT data.

**Results.**

- *The writes.* After the register block, the cache invalidations and the sync steps (E163), the
  kick switches the EDM's BIF index to the 3D's address space (`0x1864`, argument 1). It takes RT
  data dword 4 (`hw_rt_data.bgobj_dev_vaddr`), the background object's address, writes render
  details dwords 76 and 77 (`pds_bgnd`) to its dwords 0 and 1 (one two-dword fetch and store with
  post-increment), reads render details dword 69 (`pds_bgnd_list_dev_vaddr`), adds `4 * r13`,
  reads the word there and writes it to dword 2. It then switches the index back (argument 2).
  Nothing tests that the list address is not zero.
- *Where the words come from.* The TA kick's copy routine (E158) copies command dwords 2 to 4
  (`cmd_ta.pds_bgnd`) to render details dwords 76 to 78; the 3D kick uses the first two. The
  list that render details dword 69 points at is not copied by the EDM: it is read as the render
  details hold it.
- *Order.* The background object is written after the register block (`0x11bf`-`0x1211`),
  the RT-index offsets and the update of the PBE end-of-tile words (E163), and before
  `CR_ISP_START_RENDER` is written (`0x12da`), so the ISP reads the object after the three
  dwords are in place.

**Not shown.** What the background object holds when the client has written it, what the three
words mean to the ISP, and whether a client may leave dwords 0 to 2 zero: the firmware writes
them whatever they hold, and no run of the hardware is part of this record. The firmware's
copy tells how the words arrive, not what a client writes there.
