+++
id = "E543"
claim = "Lines run through the TA with ISP word 0 + 0x8000 and index list topology 1 (26 of 26 jobs complete: the 20 one-line jobs write one object of 2 vertices, the 6 multi-line jobs one or two objects of 2, 4 or 6 vertices): a one-line object's regions are those a thickened segment meets, not those the exact segment meets (right in 4 of 23 held-out jobs), the reach being 0.5 pixel at ISP word 1 width 0x10 (near-vertical: listed at 0.4375, not at 0.5), and at the widths 0x20 to 0xf0 (28 near-vertical jobs) between 0 and 1.0 pixel at 0x20, 1.497 and 2.0 at 0x40, 3.493 and 4.0 at 0x80, 6.487 and 8.0 at 0xf0 (listed up to the first, not at the second; w / 32 fits, as does any reach inside those brackets), but not by one distance at width 0x10 (near-vertical and near-horizontal lines differ by about 0.12 pixel); the multi-line objects are not predicted"
unit = "ta"
method = "script tables ta-line-point (54 jobs, 26 of them lines), ta-line-bisect (27) and ta-line-width (30 jobs, 28 of them lines), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion 7ED723C25D78D7FCB3C08C1 (installed equal to loaded), stock firmware (own_arm off), tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e, unchanged), no kernel or module change, no reboot, no clock-gate register written, a 64 x 64 triangle drawing exactly before and after every script: `probe --tri pixel` with blk:1 = 0x01d08200 (ISP word 0 with the line marker), `--vdm 2=0x84c0000K` (the index list's topology 1 and K indices), the viewport words placing one line near the boundary of a 32 x 16 region at distances 0.3125 to 8 pixel and at ISP word 1 widths 0x10 to 0xf0 (blk:2); the regions with a stream counted; H70-L2, H70-L3 and H70-L5 declared before the runs (plan.md sections 1, 8, 11); the files of H70-L3 (declared-followup4.tsv and predictions-followup4.tsv, hashes in plan.md section 8) carry the file time 23:38:53, five minutes after ta-line-bisect ran (23:33:43), because gen_followup7 rewrote them with the same 27 cases: their hashes match the files as kept, but the files alone do not show that they existed before the run, so the declaration of H70-L3 rests on the plan.md text and hash; the files of H70-L5 (followup7) precede ta-line-width; output.txt prints rc 0 for every job, also for a job that hung or faulted (the tool returns 0 on a failed job), so the failures are read from the failed line of each kept txt"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["ta-line-point"]
terms = ["ISP0.OBJ_TYPE", "ISP1.LINE_WIDTH", "PB_OBJ.LINE_WIDTHS", "VDM_INDEX0.PRIMITIVE_TOPOLOGY", "CSTREAM.PRIM_TILES"]
+++

**Lines run.** [HW] E414 saw topology 1 hang the job when only the index list was changed. With ISP
word 0 = 0x01d08200 (the line marker 0x8000, E181) as well, all 26 line jobs of ta-line-point
completed and wrote an object. The 20 one-line jobs wrote one object of 2 vertices (primitive word
0x4290ffff), the primitive list entry (16, 17, 17) (0x4630), ISP words 0x01d08200 and 0x000010f0,
the line widths dword 0x00001010 and the format word 0x00040101 (the same in all one-line objects);
the 6 multi-line jobs are described below.

**The region test, one line.** [HW] The exact closed segment against the 32 x 16 region (H70-L2,
declared) is right in 3 of 3 fit jobs and 4 of 23 held-out: it never misses a region (0 missing) and
lists too few (19 of 23 held-out jobs list regions it does not). Over 20 one-line jobs of
ta-line-point, 27 of ta-line-bisect and 28 of ta-line-width the list is the regions within a
distance of the segment: at ISP word 1 width 0x10, a region 0.4375 pixel from a near-vertical line
(v0 inside the region's band) is listed and one at 0.5 is not (distances 0.3125 to 2.0 in 12 jobs);
the same width with a near-horizontal line lists regions at 0.4375 and 0.5 pixel and not 0.5625 (the
nearest point of the segment taken at the region's left edge: 0.5625 and 0.625 for a second region
of the same job, listed, 0.6875 not), so the reach is about 0.5 pixel in x and, by the line's own
extreme y, also 0.5 [infer: a guess, not a measured quantity: the second region lies 0.125 pixel
nearer along the line's slope than the segment's extreme point]. H70-L3 (reach 0.5 at every width,
declared for ta-line-bisect) was right in 22 of 27 jobs; the five misses are the three width-0x80
jobs and two regions of the horizontal jobs just described. H70-L5 (reach max(w / 32, 0.5) pixel
with w the byte 15:8 of ISP word 1, a region listed iff the segment is nearer, '?' within 0.2 pixel
of the reach) was declared after that, with the widths 0x20, 0x40, 0x80 and 0xf0 at distances 1, 2,
3, 4, 5, 6 and 8 (28 jobs): 28 of 28 as declared, every region of every job scored apart from those
within 0.2 pixel of the reach (which are not counted). A polygon model (the segment widened to a
flat-ended rectangle of half-width hw) is inconsistent at width 0x10 (the vertical jobs need hw <
0.5, the horizontal ones hw >= 0.625): the rule between 0.4 and 0.7 pixel is open (Q159).

What the 28 jobs of ta-line-width give is a bracket for each width, not the rule. All 28 are
near-vertical lines (x moving 0.75 pixel over y 12) and the distance is that from the segment to
each 32 x 16 region rectangle:

| width (ISP word 1 bits 15:8) | jobs | listed up to (pixel) | first not listed (pixel) | w / 32 |
|---|---|---|---|---|
| 0x20 | 7 | the line's own regions only | 1.0 | 1.0 |
| 0x40 | 7 | 1.497 | 2.0 | 2.0 |
| 0x80 | 7 | 3.493 | 4.0 | 4.0 |
| 0xf0 | 7 | 6.487 | 8.0 | 7.5 |

So w / 32 fits, and so does any reach inside the brackets (a constant 0.5 fits the seven 0x20 jobs;
the reach at 0xf0 is bracketed only to 6.49 to 8.0). Only 10 of the 28 jobs list a region beyond 0.5
pixel (1 at 0x40, 3 at 0x80, 6 at 0xf0). The max(., 0.5) of H70-L5 never acted: w / 32 is at least
0.5 for every width run (0x10 is 0.5 itself) and no width under 0x10 was run on a line. The
horizontal orientation, which differs at width 0x10, was not run at the wide widths. Nothing is
stated here as a rule beyond these brackets.

**Several lines.** [HW] The six multi-line jobs (index counts 4 and 6, two or three lines) write:
ln-ctl64-two (64 x 64) one object of 4 vertices and two primitives (0x407); ln-two128 and
ln-two128-w40 (128 x 128) two objects of 2 vertices each (0x405 and 0x805); ln-two128-shift (128 x
128) one object of 4 vertices (0x407); ln-three128 two objects, of 2 and 4 vertices (0x405 and
0x807); ln-three64 one object of six vertices and three primitives (0x409). The second object of
ln-two128 lists 12 regions, 2 more than the segment from vertex 2 to vertex 0 (10 regions; the index
buffer wraps; the pair (0, 2) is the best of the 15 vertex pairs) and the first lists 10, 4 more
than its segment (v0 to v1, 6 regions); the 64-pixel job's single object of 8 regions differs by 4
from its best single segment. H70-L2 on the six multi-line jobs (ln-ctl64-two fit, five held out): 1
of 6, the 64-pixel fit job. Q160.

**Tile classes.** [HW] A line's region lists its tiles by the forms of E542: 0x90 (both) in most
regions, 0x80 and 0x98 where the segment keeps to one tile (the form 0x88 in the multi-line jobs);
at reach 0.5 the tile classes of the 20 one-line jobs of ta-line-point fit except one region of
E181's geometry that lists both tiles where the left alone is met (2 of the 70 listed regions; the
20 targets hold 592 regions).

**What it does not show.** The line's pixels (these jobs read the stream, not the image; ln-ctl64
draws 48 pixels in a box x 8-55, y 8-19 with the green shader); caps; widths other than ISP word
1's; negative or zero widths.
