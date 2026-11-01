+++
id = "Q030"
question = "where do a multisampled render's tiles past the first land in the target, and what do the TE anti-aliasing bits change?"
unit = "isp"
phase = 10
evidence = ["E210", "E211", "E219", "E220", "E281"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "CR_ISP_MSAA.ENABLE", "CR_ISP_MULTISAMPLECTL", "CR_TE_AA", "programmable sample positions"]
+++

What each value of `CR_ISP_MSAA.MODE` stores is answered (E281): mode 1 stores two samples of each
pixel side by side in x and mode 2 four in a 2x2 block, the samples of `CR_ISP_MULTISAMPLECTL` in
byte order, fitted with no pixel missed over eight positions of a known edge, one run each (that
mode 1 takes its samples from `CR_ISP_MULTISAMPLECTL` and not the MTE's word is read from mode 2);
mode 3 hangs (E210). A clear bit 31 still tiles the triangle: the parameter buffer and TA data are
the same as with it set, and only the stored image loses the triangle, in modes 1 and 2.

What is open: the fit holds inside the target's first 16x16 tile, where the small triangle lies. On
the library triangle the stored images of modes 1 and 2 are cut to whole tiles and shifted against
the 2x1 and 2x2 images, so how each tile's samples are placed in the target is not shown. The TE
anti-aliasing bits (`CR_TE_AA` 31:29) remove the triangle when bit 31 or 30 is set without bit 29,
give each mode's baseline with bit 29 alone, and give other images with 29 and 30 or 31 (E281); what
each bit selects is not shown.

To settle it: the small triangle moved tile by tile across a 64x64 target under modes 1 and 2,
fitted per tile with isp_words.py layout --joint, to find each tile's place; the same with each
combination of the TE bits, with the render memory dumped to see whether the TA's region headers
change with them.
