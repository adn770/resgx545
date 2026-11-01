+++
id = "E211"
claim = "With 0x042c bits 1:0 at 2, bit 31 set draws the 64x64 triangle (896 pixels, 1248 with the TE bits and the macrotile words) and bit 31 clear draws none of it (4096 background pixels), in both settings; with the whole word at 0 the unpoked 1062-pixel image comes back; that bit 31 acts after tiling is not shown, because the render-memory dumps are not in the data"
unit = "isp"
method = "the hand script msaa.sh of probes/isp/msaa.toml (functions 042c_bit31_dumps and closed_words_step_by_step) on the laptop, linux fork with the debug option on: the 64x64 triangle with the sample positions 0xeaa26e26 in cmd:16 and cmd:10, cmd:13 at 0x80000002 and 0x00000002, then the same with the TE bits (cmd:1 = 0xe0000000) and the macrotile words poked into the first render; one run"
tiers = ["HW"]
date = "2026-11-01"
data = ["isp-msaa"]
terms = ["CR_ISP_MSAA", "CR_ISP_MSAA.ENABLE", "CR_ISP_MSAA.MODE", "hw_render_details.isp_msaa", "CR_TE_AA"]
+++

**What runs.** Two pairs of jobs differing only in bit 31 of 0x042c (cmd:13), the other bits at
2. The first pair has the sample positions alone and was run twice by the script (once in the
function that also dumps the render memory, once in the step-by-step function); the second pair has
the TE anti-aliasing bits and the macrotile words as well. A last job sets the whole word to 0
with no other multisample word.

**Results.**

| cmd:13 | other multisample words | triangle pixels |
|---|---|---|
| 0x80000002 | positions | 896 (both runs of it) |
| 0x00000002 | positions | 0 (4096 background, both runs of it) |
| 0x80000002 | positions, TE bits, macrotile words | 1248 |
| 0x00000002 | positions, TE bits, macrotile words | 0 (4096 background) |
| 0x00000000 | none | 1062, the unpoked image |

Every job completed. With bit 31 clear and bit 1 set no pixel of the triangle is written in either
setting.

**Not shown.** The first function asks the tool to dump the render's parameter-buffer memory for
the two cases, but only the tool's message about the dump is in the data, not the dumps, so that the
triangle is tiled the same with bit 31 clear, and so that the bit acts after tiling, is not shown
here. The single-sampled path (bits 1:0 = 0) was run only with the whole word at 0, which also
clears bit 31; a single-sampled job with bit 31 clear and other bits set was not run. Bit 31 clear
with bits 1:0 = 1 was not run. One run.
