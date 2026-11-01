+++
id = "Q030"
question = "what does each value of CR_ISP_MSAA.MODE store in the target, and does a clear bit 31 still tile the triangle?"
unit = "isp"
phase = 10
evidence = ["E210", "E220", "E211", "E219"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "CR_ISP_MSAA.ENABLE", "CR_ISP_MULTISAMPLECTL", "CR_TE_AA", "programmable sample positions"]
+++

With the sample positions 0xeaa26e26 in place, 0x042c bits 1:0 at 0, 1 and 2 give three
different images of the 64x64 triangle (1086, 868 and 896 triangle pixels; 916, 1260 and 1248
with the TE anti-aliasing bits), and 3 hangs the job in both settings (E210). The reading of the
field as a sample count (1 two samples, 2 four, 3 eight) comes from another GPU's mode field and
is not measured (E220).

What does not fit a simple layout: in the mode 1 image without the TE bits the triangle's left
edge sits at twice the x of the mode 0 image with the same y, which is what two samples stored
side by side in x would give, but its rows are not twice as long (30 pixels at y 16 against 31),
so the image is not the single-sampled one stretched in x. The mode 2 image keeps neither the
position nor the size of either, so a four-sample 2x2 layout is not seen in it, and the counts
do not follow the sample count (from mode 1 to 2 they rise without the TE bits and fall with
them). No layout was fitted to the pixels, and each count is one run.

Bit 31 of the same register: with bits 1:0 at 2 it draws the triangle when set and nothing when
clear, in two multisample setups, and the word at 0 draws the unpoked image (E211, E219). Mode 1
with bit 31 clear, and a single-sampled word with bit 31 clear and other bits set, were not run.
Whether a clear bit 31 still tiles the triangle, so that it acts after tiling, needs the
render-memory dumps that are not in the data.

To settle it: draw a shape whose coverage is known at every sample, such as a vertical edge at a
chosen sub-pixel x and a horizontal edge at a chosen sub-pixel y, with the sample positions set
to four points far apart, at modes 0, 1 and 2, on targets of the base size and of twice and four
times its width and height; print every pixel and fit each mode's image to side by side, 2x2
and interleaved layouts. Repeat each case three times. Then run modes 1 and 2 with bit 31 clear
and with it set, saving the parameter buffer of each, and compare the objects and region lists;
mode 1 with bit 31 clear also shows whether the bit gates every multisample mode.
