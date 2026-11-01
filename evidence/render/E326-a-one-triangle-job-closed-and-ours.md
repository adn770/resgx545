+++
id = "E326"
claim = "The closed GLES2 stack's one-triangle frame and our tri job are built from the same objects (render context, client CCB and control, TA commands, render details with their 3D register block, an RT data set, PB descriptor and block, parameter buffer and 0x40000-byte page table, TA data: tail pointer cache, DPM control, OTPM, DPM state and region headers, background object and its primary-program word list, control stream, PDS and USSE programs, status and sync words); against the closed frame ours differs in using one kick for the scene, the background object for the clear, one RT data, no OWN_PB, CR_ISP_CTL bit 8 set and 0x04c4 bit 25 clear, and in words the firmware or the kernel fills; every other TA register and render-details word compared holds the closed driver's value"
unit = "render"
method = "the base run of the render-state-variations capture (the closed GLES2 stack under the harness: a 64x64 pbuffer, one constant-colour triangle, glFinish), every object of its two kicks given a role by harness/ukernel-extract/kickwalk.py and read with state3d.py and kick3d.py; against our tri job: its render_words after one render (render-pending-counts, case one-render, tools/usse-asm/render_words.py) and its TA register words (userspace/libsgxfive/src/render.c, render_cmd)"
tiers = ["CAP", "HW"]
date = "2026-11-03"
data = ["render-state-variations", "render-pending-counts", "render-closed-compare"]
terms = [
    "hw_render_context.context_flags", "CONTEXT_FLAGS.OWN_PB", "cmd_ta.geom_flags",
    "GEOM_FLAGS.FIRST_KICK", "GEOM_FLAGS.LAST_KICK", "CR_ISP_CTL.PROCESS_EMPTY_TILES",
    "hw_render_details.pds_bgnd_list_dev_vaddr", "hw_render_details.num_pixel_partitions",
    "hw_render_details.frag_flags", "CR_ISP_BGOBJDEPTH", "CR_ISP_BGOBJVALS",
    "CR_ISP_MULTISAMPLECTL", "CR_REG_0800", "CR_REG_0400",
]
+++

**What runs.** The closed frame is the base run: tri clears to blue and draws one constant-colour
triangle into a 64x64 RGB565 pbuffer; ours is sgxfive-test tri, one 64x64 triangle drawn and
checked pixel by pixel on the laptop (render-pending-counts, one-render: "diff: 0 of 4096
pixels").

**Results.** The objects each job needs, and how the two compare word by word (addresses left
out: every heap sits elsewhere in the two stacks):

| object | closed frame | ours |
|---|---|---|
| kicks | two: draws (FIRST_KICK), then the scene's close (LAST_KICK, FRAG_FLAGS.BIT10), E324 | one, both flags |
| HW render context | 0x44 bytes, NEW and OWN_PB, PID (E323) | NEW only, PID 0 |
| client CCB, its control | a 0x10420-byte CCB, commands 0x2c0 bytes apart | ours |
| TA command | E328 | the same TA register values |
| render details | one per scene (two in turn) | one |
| RT data set | header and two RT data (E325) | header and one |
| PB descriptor and block | 0x422 pages, the same thresholds (E327) | the same |
| parameter buffer, page table | 0x422000 and 0x40000 bytes, a 0x40-byte object after them | the same sizes and rule |
| TA data | tail pointer cache 0x100, DPM control 0x40, OTPM 0x50, two DPM states 0x88, two region-header buffers 0x300 | one DPM state, region headers and a partial region buffer |
| background object | 0x200 bytes in the parameter heap | ours |
| background primary-program word list | one word, the TA command's third PDS word | one word (the kernel's) |
| clear | a state block and an index list drawn in the first kick | the background object's colour |
| control stream | state blocks, index lists, the end-of-scene blocks, terminate | ours |
| status and sync words | 7 TA and 3 3D status updates, a destination sync | one 3D status pair |

The render details' 3D register block, word by word against ours after one render (the 52
words; the address words aside):

- equal: `reg_0400` 0x80, `CR_ISP_MSAA` 0x80000000, the polygon offset words 0, 0x0148 0, the
  ZLS words (control 0, load and store bases 0, stencil bases 0x80000000), `CR_ISP_BGOBJDEPTH`
  0x3f800000, `CR_ISP_BGOBJVALS` 0x300, `CR_ISP_MULTISAMPLECTL` 0x88, 0x04dc 0, `CR_REG_0800`
  0x30, the pixel-event data size 5 and info 1, the line sample position 1, the USSE
  coefficients, colour-space and luma-key words 0, 0x04e8 0x100;
- different: `CR_ISP_CTL` 0xf0000 closed, 0xf0100 ours (`PROCESS_EMPTY_TILES`); 0x04c4
  0x2046400 closed, 0x46400 ours (bit 25).

The render details' other words: the pixel partitions 0x7c00000 in both; the words the EDM
copies at the TA kick (render flags, background PDS words, frame number, 3D status pairs) are 0
in the closed client's render details and the command's values in ours, read after the kick.

Our fresh run (render-closed-compare, one render, "diff: 0 of 4096 pixels"; a scene of two
kicks and two renders exact as well) reads the 3D registers back after the render: every
render-details register in 0x0400-0x0560 holds its render-details word, among them 0x0400 0x80,
0x0414 (`CR_ISP_CTL`) 0xf0100, `CR_ISP_MSAA` 0x80000000, `CR_ISP_BGOBJDEPTH` 0x3f800000,
`CR_ISP_BGOBJVALS` 0x300, 0x04c4 0x46400, `CR_ISP_MULTISAMPLECTL` 0x88, 0x04e8 0x100 and
`CR_ISP_SAMPLE_POS` (0x0520) 0, the closed driver's values but for 0x0414 and 0x04c4.

**What it shows.**

- Our tri job holds every object the closed driver builds for one triangle, with the closed
  driver's values in every register word but two of the render details: `CR_ISP_CTL` bit 8,
  which our job sets and the closed driver leaves clear, and 0x04c4 bit 25, which the closed
  driver sets and ours leaves clear [CAP][HW]. Since our job draws exactly with both, neither is
  needed for a 64x64 triangle; a hardware run of our job with the closed values would show
  whether either changes anything there.
- The closed frame's extra parts are for throughput and API semantics, not for the render: a
  second RT data, render details and region-header buffer to overlap scenes, a separate closing
  kick, status words for buffer reuse, and the clear drawn as geometry [CAP].
