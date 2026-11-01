+++
id = "E311"
claim = "Every triangle pixel of an overflowing scene is drawn by some render: with CR_ISP_CTL's PROCESS_EMPTY_TILES clear the partial-render jobs draw all of the triangle (207456 pixels at 1024x768, 4422528 at 4096x4096) at every buffer size; with it set (the kernel's value) the pixels missing are whole 32x16 regions of the macrotiles that held geometry at a partial render, painted with the background by the final render, which has no stream for them"
unit = "dpm"
method = "probes/dpm/partial-renders.toml on the laptop, linux fork with the debug option on: its script partial-renders.sh runs the triangle at 1024x768 with 0x422, 0x30, 0x28, 0x24 and 0x23 pages and at 4096x4096 with 0x422, 0x100, 0x40 and 0x23 pages, each with render details word 3 (CR_ISP_CTL) at 0xf0100 and at 0xf0000 through the kernel poke rd:3, every pixel read and reduced on the laptop to one character per 32x16 region by the colours in it (triangle, background, the 0xdeadbeef the target holds before the job); one run; read with dpm_words.py tiles against the whole-buffer image; the last case of probes/dpm/partial-timelines.toml prints the stray pixels"
tiers = ["HW", "infer"]
date = "2026-11-02"
data = ["dpm-partial-renders", "dpm-partial-timelines"]
terms = ["CR_ISP_CTL.PROCESS_EMPTY_TILES", "partial render", "Parameter Buffer (PB)"]
+++

**Results.**

| target, pages | job | triangle pixels, 0xf0100 | triangle pixels, 0xf0000 |
|---|---|---|---|
| 1024x768, 0x422 | ok | 207456 | 207456 |
| 1024x768, 0x30 | overflow | 51408 | 207456 |
| 1024x768, 0x28 | overflow | 162544 | 207456 |
| 1024x768, 0x24 | overflow | 205061 | 207456 |
| 1024x768, 0x23 | overflow | 207456 | 207456 |
| 4096x4096, 0x422 | ok | 4422528 | 4422528 |
| 4096x4096, 0x100 | overflow | 987008 | 4422528 |
| 4096x4096, 0x40 | overflow | 224448 | 4422528 |
| 4096x4096, 0x23 | overflow | 43872 | 4422528 |

The 0xf0100 counts are E202's images (the same differing pixels at every size). With 0xf0000
every triangle pixel is drawn, and the tool's own diff lines read 542720 differing pixels at
1024x768 and 12168192 at 4096x4096 in every case, as in the job that does not overflow (first at
(0, 0), the sentinel where background is expected); the region maps equal that job's but for the
one region the error message lands in (below). So with the bit clear the overflowing images are
the whole-buffer one [infer: equal counts and maps]. With 0xf0100 the lost pixels lie in regions
that are wholly background in the image and wholly or partly triangle in the whole-buffer image
(for example 96 regions of macrotile 5 and 94 of macrotile 9 at 1024x768 in 0x30 pages), and only
in the macrotiles the partial render's state page lists (E310): 0, 1, 2, 4, 5, 6, 8, 9 and 13 at
1024x768 in 0x30 pages, the same plus 10 at 4096x4096 in 0x100. With more partial renders more
macrotiles lose regions (4096x4096: ten at 0x100, eleven at 0x23, macrotile 7 added), and more
regions in each (macrotile 6: 576 at 0x100, 1818 at 0x40, and at 0x23 all 1944 of its triangle
regions).

The tallies of every overflowing job are off by the tool's error message, which it writes to
the same stream as the pixel rows: its 14 words land inside the last row (row 767, row 4095),
and the rest of that row falls on a line of its own that the reduction does not read. So each
overflowing case counts the 14 words as pixels of another colour, in one region of the last row,
and leaves 312 of that row's pixels uncounted at 1024x768 and 338 at 4096x4096: exactly the
sentinel and background pixels its 0xf0000 tallies lack against the whole-buffer job (280 + 32,
306 + 32). The tallies come to 298 and 324 fewer than the image's pixels; the triangle counts are
not affected.
The last case of probes/dpm/partial-timelines.toml prints the words at their place in row 767
(`other (753, 767) sgxfive-test:` and on). A later script should send the tool's error stream
apart from the pixel rows.

**Reading [infer].** The partial render draws what was tiled so far in every macrotile (E312: it
frees every macrotile's pages), and the final render, whose streams hold only what the TA tiled
after the last partial render, paints the background object over every region of the scene,
since the kernel's ISP_CTL processes empty regions. So the missing pixels are painted over, not
discarded geometry, and the amount drawn is the geometry tiled after the last partial render: it
does not follow the buffer size. At 1024x768 in 0x23 pages the job's TA3DCtl dword 35 reads
0xffff, page status 1 less 2, and dword 39 0x1f (E310): its last partial render came at the
first page, as the first one of 4096x4096 in 0x23 pages does in E312's timeline, before any
region holds geometry [infer], so the image is exact (no timeline of that job was taken).

**Not shown.** A colour reload in the background object (the scene's own remedy); a PB dump at
each partial render (a kernel hook, 11.10).
