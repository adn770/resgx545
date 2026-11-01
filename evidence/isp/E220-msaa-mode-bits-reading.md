+++
id = "E220"
claim = "Naming 0x042c bits 1:0 the multisample mode (1 two samples, 2 four, 3 eight) agrees with three different images for 0, 1 and 2 and a hang at 3, but the sample counts are not measured"
unit = "isp"
method = "comparison of E210's jobs with the open descriptions of other GPUs' anti-aliasing mode fields (no citation record of this tree covers them, so the reading is ours), hardware run on the laptop, linux fork with the debug option on; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-msaa"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "hw_render_details.isp_msaa", "CR_ISP_MULTISAMPLECTL"]
+++

**The reading.** Register 0x042c holds, in bits 1:0, a small number that changes the image when
the sample positions are set. Open descriptions of other GPUs' anti-aliasing control give such a
field the values 0 none, 1 two samples, 2 four, 3 eight; that is where the name and the counts
come from (ours; the descriptions are not a citation record of this tree).

**What the data show.** E210: values 0, 1 and 2 give three different images (1086, 868 and 896
triangle pixels without the TE bits; 916, 1260 and 1248 with them), and value 3 hangs the job in
both settings. E211: with value 2 the triangle is drawn only while bit 31 of the same register is
set. So the field takes the values 0 to 3, three of them draw, and the numbering fits the reading
in that a larger value is a further, different image and the last hangs.

**Not shown.** That value 1 stores two samples a pixel and value 2 four is not measured: the
images were not fitted to a layout, and the pixel counts do not follow the sample count (from
value 1 to 2 they rise without the TE bits, 868 to 896, and fall with them, 1260 to 1248). That
value 3 means eight samples is not shown, since it only hangs, with or without the TE bits. The
names rest on this one run and on the analogy, which is a hypothesis for this hardware.
