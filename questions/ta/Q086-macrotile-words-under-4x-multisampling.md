+++
id = "Q086"
question = "what rule gives CR_TE_MTILE1, CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE for a 4x multisampled target, whose 64x64 words are 0x802002, 0x802002 and 0x4 against the single-sampled rule's 0x1004004, 0x1004004 and 0x10?"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E331", "E329"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE", "CR_TE_AA", "CR_TE_SCREEN"]
+++

Over 222 single-sampled sizes the macrotile words follow one rule (E331). The only multisampled
targets captured are 64x64 textures with 2 or 4 samples asked (both give 4x: `CR_TE_AA`
0xe0000000, `CR_MTE_MULTISAMPLECTL` 0xeaa26e26), and there `CR_TE_MTILE1` and `CR_TE_MTILE2` are
0x802002 and the stride 4, with `CR_TE_SCREEN` the single-sampled 0x3001 (E329). In the rule's
terms that is a macrotile of 2 tiles, not rounded up to a 4-tile block, a block field of 0 and
bit 23 set, and a stride of a quarter block.

What is open: the rule over sizes (whether the macrotile counts tiles of a 2x2 sample grid,
whether n = 4 starts at a quarter of the area, what bit 23 marks) and the RT data's size words
(tiles across, blocks, region-header bytes, tail pointer cache) for such a target.

To settle it: capture 4x multisampled texture targets over the sizes of sizes3d.txt's s* and t*
lists (a gaps3d.txt-style line per size: fbo=WxH fbosamples=4), and read the words with
tiling3d.py and the RT data set as E331 does.
