+++
id = "E427"
claim = "In a stream of two objects, each with its own state task, flipping the fields of the second state word (VDM word 9) while the first block stays as built gives the same completions and hangs as flipping the first block's (word 1) for bits 15:13 (0, 5, 6 and 7 hang in 16 of 16 jobs, 2, 3 and 4 complete in 12 of 12) and for bits 11:9 at 3 and 4 (8 of 8 complete); bits 11:9 at 0 in the second block draws the first object only (2 of 2), at 1 hangs in the second block and completes in the first; bit 8 changes nothing in either"
unit = "vdm"
method = "probes/vdm/state2-fields.toml on the laptop (direct cable), linux fork f1fad0ed9d0e with the debug option on, sgxfive-test probe --tri with --vertices 12 --obj2 6 (two objects in one kick, the second with its own state block and a green pixel shader, the first blue; VDM words 0-1 and 8-9) and --vdm 1^=X or 9^=X (the stream's words set after the second object is built): bit 8 set, bits 11:9 at 0, 1 and 3 to 7 and bits 15:13 at 0 and 2 to 7 of each block, plus controls, two runs each (62 jobs), the pixels and the render's PB and TA data dumped"
tiers = ["HW", "infer"]
date = "2026-11-07"
data = ["vdm-state2-fields"]
terms = ["VDM_STATE1.BIT8", "VDM_STATE1.BITS11_9", "VDM_STATE1.BITS15_13"]
+++

**What ran.** The second object is drawn after the first with its own state block, a copy of the
first's (11:9 = 2, 15:13 = 1, bit 8 clear); its triangles lie only 0.1 to 0.2 pixel from the first
object's, so the second (green) covers the first (blue): in a completed job the pixels show the
second object, or the first when the second is not drawn. The controls (2 of 2) draw 1098 green
pixels over 2998 of the background.

- Bit 8 set, either block: complete, the control's image and TA data (4 of 4).
- Bits 15:13 at 2, 3 and 4, either block: complete, the control's image and TA data (12 of 12); at
  0, 5, 6 and 7, either block: hang (16 of 16 jobs).
- Bits 11:9 at 3 and 4: complete, the control's image and TA data, either block (8 of 8).
- Bits 11:9 at 0: in the first block complete with the control's pixels (the first object lies
  under the second, so nothing shows), 2 of 2; in the second block complete with 1098 blue pixels
  and no green, the second object missing, 2 of 2, the TA data the control's.
- Bits 11:9 at 1: first block complete (2 of 2), second block hang (2 of 2).
- Bits 11:9 at 5, 6 and 7: each of the six cases hangs in one of its two runs (the first block: 5
  in the first run, 6 and 7 in the second; the second block alike), as E299 and E413 found a hang
  every second job.

**What it shows.** A state word's fields act on the objects after its own state task: the second
block's 11:9 = 0 removes the second object alone. The values that hang are those of the one-block
job (E414) in both blocks, so a hang comes from the state task and not from a unit downstream that
the other block shares [infer]. With both blocks the same MTE state block, the fields' meanings
(units named or sizes) are not separated: no completed job's image or TA data differs except by
the missing object.

**What it does not show.** A second block whose program loads pixel-side constants, which the tool
does not build, and the first block's 11:9 = 0 (hidden under the second object). Q047 stays open.
