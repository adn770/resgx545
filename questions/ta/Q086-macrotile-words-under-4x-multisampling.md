+++
id = "Q086"
question = "what rule gives CR_TE_MTILE1, CR_TE_MTILE2 and CR_TE_MACROTILE_STRIDE for a 4x multisampled target, whose 64x64 words are 0x802002, 0x802002 and 0x4 against the single-sampled rule's 0x1004004, 0x1004004 and 0x10?"
unit = "ta"
kind = "hw"
value = "medium"
phase = 11
evidence = ["E331", "E329", "E507", "E511", "E824"]
terms = ["CR_TE_MTILE1", "CR_TE_MTILE2", "CR_TE_MACROTILE_STRIDE", "CR_TE_AA", "CR_TE_SCREEN"]
+++

Over 222 single-sampled sizes the macrotile words follow one rule (E331). The only multisampled
targets captured are 64x64 textures with 2 or 4 samples asked (both give 4x: `CR_TE_AA` 0xe0000000,
`CR_MTE_MULTISAMPLECTL` 0xeaa26e26), and there `CR_TE_MTILE1` and `CR_TE_MTILE2` are 0x802002 and
the stride 4, with `CR_TE_SCREEN` the single-sampled 0x3001 (E329). In the rule's terms that is a
macrotile of 2 tiles, not rounded up to a 4-tile block, a block field of 0 and bit 23 set, and a
stride of a quarter block.

What is open: the rule over sizes (whether the macrotile counts tiles of a 2x2 sample grid, whether
n = 4 starts at a quarter of the area, what bit 23 marks) and the RT data's size words (tiles
across, blocks, region-header bytes, tail pointer cache) for such a target.

To settle it: capture 4x multisampled texture targets over the sizes of sizes3d.txt's s* and t*
lists (a gaps3d.txt-style line per size: fbo=WxH fbosamples=4), and read the words with tiling3d.py
and the RT data set as E331 does.

Run in 11.26 (E507, 13 jobs, one run each): our stack's 4x render with the unpoked rule words draws
exactly at 64 x 64, 128 x 64, 128 x 128, 256 x 128, 96 x 48 and 192 x 96 and faults the job at the
six held-out sizes from 320 x 160 to 640 x 480, so the declared test of H86i (the image does not
depend on the words once they are valid) could run only at the fit sizes, where U2 at 64 x 64
equals R. The closed driver's rule over sizes needs the capture batch (`sizes/ms4-sizes3d.txt`, not
run). Status: narrowed, not answered; missing: the capture batch, and a 4x render of our stack that
completes past 256 x 128 (Q140).

Run in the 11.26 resume (E511, 6 of 26 risky jobs; the 20 at 320 x 160 and larger and the safe
script's 1024 x 768 job were not run, because 4x faults there with the rule's own words): the
closed 64 x 64 words draw exactly at 96 x 48 and 128 x 64 and fault the job at 128 x 128, 192 x 96
and 256 x 128, a two-tile macrotile in CR_TE_MTILE1 alone draws exactly at 128 x 128, and the tile
signature of the 3 jobs that complete equals R's, which cannot fail in this form because every
completing job is all green (with E507's U2 job at 64 x 64, 4 of 4 U2 jobs;
the 6 R jobs of E507 are the rule itself). The rule over sizes still needs the capture batch.

Note 2026-11-11: the missing 4x render of our stack past 256 x 128 exists. The faults at 320 x 160
and above were our kernel's one-array layout (E788): with the new module's `render_rgn_arrays` at
4, 8 of 8 held-out sizes up to 1024 x 768 complete with 0 wrong pixels (E824). H86i and the poked
families U2, U2Q, HS and FX of E511's 20 skipped cases can run at 320 x 160 and larger with four
arrays (not run yet); the closed driver's rule over sizes still needs the capture batch.
