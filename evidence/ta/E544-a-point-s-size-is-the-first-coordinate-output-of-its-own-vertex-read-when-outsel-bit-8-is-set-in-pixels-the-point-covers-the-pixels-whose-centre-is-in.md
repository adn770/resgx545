+++
id = "E544"
claim = "A point's size is the first coordinate output of its own vertex, read when OUTSEL bit 8 is set, in pixels: the point covers the pixels whose centre is in [v - S/2, v + S/2) in x and y, in 40 of 42 sized jobs (sizes 0.5 to 256, pixel-centre, corner and fractional vertices) and in 4 of 4 jobs with a different size a vertex; without bit 8 a point draws no pixel (16 of 16 jobs with the pixels read), and its tile list is that of a footprint of at most one pixel"
unit = "ta"
method = "script tables ta-points (44 jobs), ta-points-vertex (4), ta-risky (38, of them 20 OUTSEL flips and 18 size jobs) and the points of ta-line-point (28 jobs), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 7ED723C25D78D7FCB3C08C1 (installed equal to loaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written, a 64 x 64 triangle drawing exactly before and after every script: `probe --tri vtxuse` with `--vtx-coords 1`, blk:1 = 0x01d18200 (ISP word 0 with the points marker 0x18000), `--vdm 2=0x88c00003` (topology 2, three points), blk:13 ^= 0x100 (OUTSEL bit 8) and a vertex program writing a constant S (p1131-psizes) or 16 * C + 20 (p1131-psizev, C the clip x or y) to o4; pixels counted and compared with an own union of squares; tile lists from the control stream; the vertex programs and the size of each case are in probes/ta/p1131-progs.toml, the size itself resting on the case name (the programs are not in the data); output.txt prints rc 0 for every job, also for a job that hung or faulted (the tool returns 0 on a failed job), so the failures are read from the failed line of each kept txt; H117-S1, H70-P1, H117-V declared before the runs (plan.md sections 8 and 13)"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-points", "ta-line-point"]
terms = ["CSTREAM.PRIM_POINTS", "ISP0.OBJ_TYPE", "OUTSEL", "VDM_INDEX0.PRIMITIVE_TOPOLOGY", "PB_OBJ.FORMAT"]
+++

**Points draw pixels with OUTSEL bit 8.** [HW] ta-line-point's 28 point jobs (E181's three points,
boundaries, widths of ISP word 1, size rows) all completed and wrote a point object (primitive word
0x64800101, ISP word 0 0x01d18200) but, in the 16 with the pixels read, drew none; the declared
pixel model (H117-W: a square of ISP word 1's width round the vertex, declared for 14 of them) was
right in 4 of 14. In ta-risky, blk:13 ^= 0x100 with the one-output vertex program (size 1.0 and 8.0)
drew 3 and 192 pixels: 3 points of 1 x 1 and of 8 x 8 pixels. With the bit set and no size row the
job faulted (of-outsel-b8). The object holds the size packed [HW]: the last two non-zero dwords of
the packed block are 0x00100010 at S = 1 and 0x00800080 at S = 8 (S in sixteenths of a pixel, twice
a dword) and its first dword holds the lower corner v - S/2 in 1/256 pixel (0x0a00 = 10.0 at S = 1,
0x0680 = 6.5 at S = 8); the parameter-buffer dumps of the two jobs differ in 28 dwords (8 in the
object, 20 in the streams).

**The footprint (H117-S1).** [HW] Pixels with centre in [v - S/2, v + S/2) in x and y, S in
sixteenths: right in the pixel counts of 40 of 42 completed jobs of ta-points, and the pixel sets
equal the model's in 40 of 42: sizes 0.5, 1, 1.5, 2, 2.5, 3, 4, 5, 6, 7, 8, 9, 11, 12, 16, 20, 24,
32, 48, 63, 64, 100, 255, 256 and 1/16 at vertices on pixel centres (10.5, 10.5), (34.5, 16.5),
(16.5, 34.5); sizes 1, 2, 3, 4, 5, 8, 16 at corners (10.0, ...) and 1, 2, 3, 4, 8, 11 at fractional
vertices (10.3125 ...); the ISP word 1 width 0x80 with S = 4 changes nothing (48 of 48). The sizes
100, 255 and 256 cover the whole 64 x 64 target (4096 pixels; so would any size of 95 or more at
these vertices): they show only that the field reaches at least 95 pixels, not its width. The low
side is closed: S = 8 at 10.5 covers x 6 to 13 (centre 6.5 counted) and not 14 (centre 14.5). The
declared model for the no-row jobs said "strictly inside" (a centre at S/2 from the vertex
excluded): for the sized jobs the rule that fits is the half-open one, and at the pixel-centre
placement it differs from the strict one in every size that is an even number of pixels (S = 8 at
10.5 counts the centre 6.5). Each point reads its own vertex's row (H117-V): a vertex program
writing 16 * C + 20 gives sizes 8, 32 and 14 (by clip x) or 8, 14 and 32 (by clip y) at the three
vertices and the covered pixels equal the union of those squares in 4 of 4 jobs (1259 pixels each,
against 192, 588 or 2176 if one size served all). The size comes from o4, the first coordinate
output [infer: no completed job puts a value in another output; the two-output size program hung in
4 of 4 jobs, 3 with bit 8 (both orders of A and B, and a repeat) and 1 without].

**The misses.** [HW] S = 1/32 draws 3 pixels (one a point; declared none) and S = 0 none, so a size
below 1/16 draws a pixel at least when it is not 0 [infer: rounding up to 1/16, or a floor of 1/16
for a non-zero size]; S = -4 draws 2704 pixels (declared none): x and y from 12 to 63, the square
from v - S/2 = v + 2 to past the target's far edge [infer: the size field read unsigned].

**Tile lists (H70-P1).** [HW] A point's tiles are those [v - S/2, v + S/2] meets (high end closed,
the tile's high side open): reading every object of every region, 41 of 42 completed jobs (the tiles
and, in the 39 single-object jobs, the points of each tile); the miss is S = -4, whose square runs
to the target's far edge (all 16 tiles). The first score, 36 of 40 jobs, read only each region's
first object: its four misses are S = 1/32 and 0 (tiles listed with a footprint of at most one
pixel; declared none for S < 1/16) and S = 63 and 64, where the three points are written as two
objects (0x405 with two points, 0x804 with one), so a decoder that reads the first object alone
finds a point fewer per tile; S = 100 also splits (0x404 with one point, 0x805 with two) and 255 and
256 do not: Q161. Without a size row the three-point jobs' tile lists equal a footprint of s in (0,
1] (18 of 18 jobs, mismatches 0; 4 label-only): a vertex on a tile line is in both tiles. The
declared region test of ta-line-point (H70-P0, the vertex's own tile, low side half-open) was right
in 4 of 4 fit jobs and 11 of 24 held out.

**OUTSEL flips with the plain triangle.** [HW] 20 jobs: bits 9, 13, 14, 23 to 31 leave the object's
format word 0x00040101 (12 of 12 completed, declared the same); bit 12 clears the format word to
0x00000000 (declared 0x00000101: bits 7:0 clear too, one vertex dword fewer); bits 20, 21 and 22
complete and write no primitive list and no stream (bits 20 and 21 leave 1066 non-zero dwords in the
parameter buffer, bit 22 1471); bits 8, 10, 11 and 15 fault the job (4 of 4: declared complete).
With the one-output size program and the points: bit 8 draws (above), bits 9, 14 and 20 to 23 draw
nothing (12 jobs), bits 10 and 15 hang (4 of 4). Q162.

The first two clauses of the point question that Q161 now carries (size source and footprint) are
answered for our own program: where the size comes from (the vertex's first coordinate output, with
OUTSEL bit 8), its unit (pixels, in sixteenths) and the footprint (a square centred on the vertex),
read from the object's own vertex data and not from the primitive word. Its third clause, whether
the closed driver's extra output row carries the size, is not answered and is carried by Q161.

**What it does not show.** Where the size lies when a vertex has more than one coordinate output; a
size from a second row; larger targets than 64 x 64; sizes between 64 and 95 at other vertices;
whether a per-point size reaches the closed driver's points the same way (E346 has only the extra
output row).
