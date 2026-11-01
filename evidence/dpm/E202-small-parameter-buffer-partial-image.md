+++
id = "E202"
claim = "A scene larger than its parameter buffer is reported by the kernel as an overflow with the context kept, no fault or hang; at 4096x4096 it draws only part of the image from 0x100 pages down, at 1024x768 from 0x30 to 0x24 pages, while at 0x23 pages and 1024x768 the job still reports an overflow but the image is exact; the image is the same in both repeats of every size, and the amount missing does not follow the buffer size"
unit = "dpm"
method = "the two sweeps of probes/dpm/parameter-buffer.toml (the triangle at 1024x768 and 4096x4096, render_pb_pages 0x422, 0x200, 0x100, 0x80, 0x62, 0x40, 0x30, 0x28, 0x24, 0x23, each twice, registers 0x0400-0x07fc sampled around each job), on the laptop with the linux fork and the debug option on"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["dpm-parameter-buffer"]
terms = ["Parameter Buffer (PB)", "PBSize", "partial render", "TAThreshold", "ZLSThreshold", "GlobalThreshold", "PDSThreshold"]
+++

**What runs.** The 20 cases of each sweep give the render context a parameter buffer of the stated
number of 4 KiB pages (0x422 is the full size) and render the triangle; the target is read back and
compared with the expected image (4422528 triangle pixels of 16777216 at 4096x4096, 207456 of 786432
at 1024x768). Each size ran twice in a row on the same context.

**Results.**

| pages | 1024x768: job | pixels differing | 4096x4096: job | pixels differing |
|---|---|---|---|---|
| 0x422, 0x200 | ok | 0 | ok | 0 |
| 0x100 | ok | 0 | overflow | 3429571 |
| 0x80 | ok | 0 | overflow | 3387235 |
| 0x62 | ok | 0 | overflow | 3904419 |
| 0x40 | ok | 0 | overflow | 4190851 |
| 0x30 | overflow | 154574 | overflow | 4266819 |
| 0x28 | overflow | 44191 | overflow | 3999843 |
| 0x24 | overflow | 2225 | overflow | 4032611 |
| 0x23 | overflow | 0 | overflow | 4370787 |

"Overflow" is the tool's report "scene overflowed the parameter buffer, context kept (No space left
on device)"; it reports no fault, hang or lost context, and the next case ran on the same context.
The two repeats of each size give the same pixel difference and the same image hash in all 20 pairs.
The first differing pixel is (513, 513) at 4096x4096 and (130, 97) at 1024x768, where the background
colour stands in place of the triangle's. At 4096x4096 3.4 to 4.4 million of the triangle's 4.4
million pixels differ; if each is a missing triangle pixel, 993 thousand are drawn at 0x100 and 52
thousand at 0x23, and the amount does not fall steadily with the buffer (0x100 and 0x80 draw more
than 0x62, 0x28 and 0x24 more than 0x30). At 1024x768 the differing pixels fall as the buffer
shrinks, from 154574 at 0x30 to none at 0x23, where the job still reports an overflow with the exact
image. In the successful jobs the DPM threshold registers read back 0x10 above the page count
(0x620), 0x22 below it (0x624) and that minus 0x100 (0x668, zero when that is negative).

**Reading [infer].** The partial-render routine of the EDM ran in these jobs (E204 counts its runs:
1 at 1024x768, 1 to 10 at 4096x4096 as the buffer shrinks). Two readings fit the partial image: that
an aborted macrotile's geometry is discarded, or that each partial render paints the whole
background object over what earlier ones stored, since the scene has no colour reload. The exact
image at 0x23 and 1024x768 favours neither.

**Not shown.** Which reading holds; the out-of-memory counters of the RT data set (the visibility
counters were recorded, none counted); that a correct partial render with a colour reload would draw
the scene. Where the kernel's overflow report comes from is not examined here. Two repeats per size;
4096x4096 took about 12 s a case.
