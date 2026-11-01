+++
id = "E215"
claim = "With ISP word 0 bit 28 set, the single-sampled triangle's coverage depends on 0x04c8 as well as 0x0520 (1122, 1134 and 1098 pixels for 0x04c8 at 0x88, 0xffffffff and 0 with 0x0520 at 0x0c0c0c0c, against 1098 with 0x0520 at 0), which the union of eight samples (0x04c8's four bytes and 0x0520's four) predicts in all four cases; a 4x render gives one image for three values of 0x0520, bit 28 under 4x hangs the job, and mode 3 hangs in every setting tried"
unit = "isp"
method = "the hand script sample-positions.sh of probes/isp/sample-positions.toml (function 0520_under_4x) on the laptop, linux fork with the debug option on: 0x0520 (rd:19) poked, cmd:16 (0x04c8), cmd:13 (0x042c), cmd:1 and the ISP word 0 (blk:1) set per case, a hash of the pixels and the triangle count printed; the whole script run twice in one session; the predictions from the offline fit of E214 extended to the eight samples"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-sample-positions"]
terms = ["CR_ISP_SAMPLE_POS", "CR_ISP_MULTISAMPLECTL", "CR_ISP_MSAA.MODE", "programmable sample positions", "hw_render_details.isp_sample_pos"]
+++

**What runs.** Three groups, each repeated once in the same session. The 4x setup (sample positions
0xeaa26e26 in cmd:16 and cmd:10, 0x042c = 0x80000002, the TE bits 0xe0000000) with 0x0520 at 0,
0x88888888 and 0xffffffff, with ISP word 0 as 0x01d00200 and with bit 28 set (0x11d00200). The
single-sampled triangle with bit 28 set, 0x0520 at 0x0c0c0c0c and 0x04c8 at 0x88, 0xffffffff and 0,
and with 0x0520 at 0 and the default 0x04c8. Mode 3 (0x042c = 0x80000003) with 0x0520 at 0 and at
0x2e62a6ea, with and without bit 28.

**Results.**

- 4x, bit 28 clear: 0x0520 at 0, 0x88888888 and 0xffffffff give one image (the same pixel hash,
  1248 triangle pixels), in both repeats.
- 4x, bit 28 set: the job hung in all 6 cases (3 values, 2 repeats).
- Single-sampled with bit 28: 1122 pixels (0x04c8 = 0x88, 0x0520 = 0x0c0c0c0c), 1134
  (0x04c8 = 0xffffffff), 1098 (0x04c8 = 0), and 1098 with 0x0520 = 0 and the default 0x04c8; the
  same hashes in the two repeats.
- Mode 3: the job hung in all 8 cases (4 settings, 2 repeats).

The offline model of E214 with eight samples (the four bytes of 0x04c8, then the four of 0x0520,
a pixel covered when any is inside, ties as in E214) predicts 1122, 1134, 1098 and 1098 for the
four single-sampled cases. A model in which 0x04c8 does not enter (the four samples of 0x0520
plus the centre) predicts 1122 for the 0x04c8 = 0 case and the same for the other two, so it fails
two of the three observed counts.

**Not shown.** The pixels of the 0x04c8 cases are in the data only as a hash and a count, so the
fit there is on counts, not on every pixel (E214's 55 images are fitted pixel for pixel, with the
default 0x04c8 only). Whether 4x multisampling reads 0x0520 for anything other than the image is
not shown; the three values give the same image. Whether mode 3 needs words this script does not
set is not shown: it hangs with 0x0520 at 0 and at a second grid, with and without bit 28. One
session, run twice.
