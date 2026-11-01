+++
id = "E074"
claim = "With the multisample positions set in cmd:16 and cmd:10, 0x042c (cmd:13) bits 1:0 = 1 and 2 each change the 64x64 triangle's image (868 and 896 triangle pixels against 1086 with the positions alone), 3 hangs the job, TE anti-aliasing bits 31:30 change it again (1248 pixels), and bit 48 of an emit does nothing, while bit 31 of 0x042c clear removes the triangle only when bit 1 is set; that the image holds each pixel's samples is not shown by these counts"
unit = "isp"
method = "the hand script msaa.sh of probes/isp/msaa.toml (042c_bit31_dumps, 042c_modes and the step-by-step part) and the ten probes of the table (eot_plain, eot_bit48_1, eot_bit48_2 and pack modes 9 and 10, each single and 4x), on the laptop with the linux fork and the debug option on; one run"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["isp-msaa"]
terms = [
    "CR_ISP_MSAA", "CR_ISP_MSAA.MODE", "CR_ISP_MSAA.ENABLE", "hw_render_details.isp_msaa",
    "CR_ISP_MULTISAMPLECTL", "CR_MTE_MULTISAMPLECTL", "CR_TE_AA", "programmable sample positions",
    "SIDEBAND.PACKMODE",
]
+++

**What runs.** The 64x64 triangle with four settings added one at a time: the sample positions
0xeaa26e26 in cmd:16 and cmd:10; 0x042c (cmd:13) at 0x8000000N for N = 0 to 3; the TE anti-aliasing
bits (cmd:1 = 0xe0000000); and the macrotile words (`ta:143`, `ta:144`, `ta:146` through the
kernel's poke of the first render). The probes render the plain end-of-tile program, two variants
with bit 48 set on an emit, and pack modes 9 and 10, each without and with the multisample words
(cmd:1, 10, 13 = 0x80000002 and 16 as above, so TE anti-aliasing included).

**Results.** Triangle pixels in the image (1062 for the unpoked job, 4096 pixels in all):

| setting | triangle pixels |
|---|---|
| unpoked | 1062 |
| sample positions alone (N = 0) | 1086 |
| + 0x042c = 0x80000002 | 896 (746 pixels differ from the CPU image) |
| + 0x042c = 0x80000001 | 868 |
| + 0x042c = 0x80000003 | job hung, context lost |
| + TE bits, N = 0 / 1 / 2 | 916 / 1260 / 1248 |
| + TE bits, N = 2, + macrotile words | 1248, same hash as without them |
| N = 2 with bit 31 clear (0x00000002), with and without the TE bits | 0 (background only) |
| 0x042c = 0 alone | 1062, the unpoked image |

The two bit-31 dumps agree: 0x80000002 gives 896 pixels, 0x00000002 gives none. The bit-48 probes
give the same image as the plain end-of-tile program, both single-sampled (1062 triangle pixels) and
with the multisample words (1248). Pack mode 9 leaves 3072 pixels unwritten in both renders and
splits the other 1024 into 120 triangle and 904 background (single) and 640 and 384 (multisampled);
pack mode 10 leaves 2048 unwritten and splits the rest into 714 and 1334 (single), 1216 and 832
(multisampled).

**What it does not show.** Bit 1 changes the image and needs bit 31 to draw, and bit 0 alone changes
it too (868 pixels): the data do not single out bit 1 as the 4x bit. That the image is four samples
a pixel stored in the tile with no resolve is a reading [infer] from the counts growing with the TE
bits and from the partial pack layouts; this record did not compare the images pixel by pixel with a
model. What resolves the samples is not tested. N = 3 hangs the job, with and without the TE bits.
One run.
