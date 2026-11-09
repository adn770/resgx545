+++
id = "Q023"
question = "how many output dwords does a pixel task get per setup, and what do the data rows limit (E406)"
unit = "pds"
kind = "hw"
value = "high"
phase = 7
evidence = ["E139", "E081", "E406", "E570", "E709", "E742"]
terms = ["PDS_SIZE.BITS17_16"]
+++

With the field at 3 (the plain value of our jobs) the output register o1 of a triangle shader
changes 508 pixels (a pixel is changed when it holds a value the shader wrote to that register), o2
604 and o3 400, mostly displaced by 16 or 32 rows and 0 or 32 columns (E081). At 0, 1 and 2 the
counts become 545, 705 and 747 for o1, 210, 383 and 495 for o2, and 83, 211 and 392 for o3, while o0
lands on the pixel's own position for all 1062 covered pixels in every table (E081, E139). One run
of each table.

E139 reads this as a size or count of output register banks a pixel task is given. That is our
inference. Not shown: whether the field is a size or a count, whether 3 means all, why no value
removes the displaced writes, and whether other banks (inputs, attributes) depend on it.

To settle it: a shader that writes a distinct value to each of o0 to o7, with the field at 0, 1,
2 and 3, read back every pixel and map which destination each oN reaches; run each table twice to
see whether the destinations are fixed. A second shader that reads its own inputs back would show
whether the field affects the other banks.

Narrowed in 11.15 (E406, 1797 jobs, one per case): the four-output search the user asked for found a
setup. With ISP word 0 bit 26 or 27 set, CR_REG_0148 (render details dword 9) bit 0 set and the
state block's word 4 at 0x00030001 (PDS_SIZE 3 and one data row), a shader writing o0 to o7 with a
tag in each leaves o0 on its own pixel and o4 alone on other pixels (tags 1 and 5; tags 2 to 4, o1
to o3, on no pixel at all) in 27 of 27 jobs, where the plain job shows o1 to o3 on 447 to 600 other
pixels. Room for four output dwords a pixel is the reading of that [infer]. With 2 to 4 data rows
the pattern is tags 1, 3, 5, 7 (two dwords [infer]) and with 5 to 7 rows the job hangs. The size
field alone never does it: at 0, 1, 2 and 3 with the plain setup o1 stays on 447 to 516 other pixels
(two runs, x and y tags). With the setup, size 3 gives tags 1 and 5 (the four-dword reading), sizes
2 and 1 the tags 1, 3, 5, 7 pattern, and size 0 tags 1, 3, 5 (tag 7 on one pixel in one of six
jobs; 3 runs, bits 26 and 27). The "four" tables, whose program has three data rows, gave the tags
1, 3, 5, 7 pattern at size 3 (20 of 20 jobs): that is the three-row case above, not a second
reading of size 3. No single flip of the VDM stream, the state block, the PDS program's U1 or 20
render details words gives the setup's pattern; ISP word 0 bit 26 or 27 and CR_REG_0148 bit 0 each
give the tags 1, 3, 5, 7 pattern. So the field takes part (size 3 is the one that gives tags 1 and
5) but is not a size by itself [infer]; why the room needs one data row, and what bits 26 and 27 of
ISP word 0 select, is open. Status: narrowed, not answered.

Narrowed in 11.33 (E570, 68 jobs at 13 configurations of 7 shapes from 32x96 to 256x128, and 8
more of 3 other shapes, PDS_SIZE 0 to 3, x and y runs): o1's writes land at the pixel's own place in
the tile one position later in the raster order of the target's 32x16 tiles in 6362 of 6995 pairs
(91 percent); the order of the TA data's region headers gives 6110 (87 percent) and 559 of 688 on
the shapes it was not built from. The raster rule fails at 64x128 (300 of 402) and 256x128 (184 of
362), the header order is the better one only at 256x128 and 192x96 size 0, and no rule fits every
pair. o2 and o3 land one to three positions back with no setting that fixes it (743 one, 318 two,
91 three of 2094 for o2); the same table run twice gives different counts. Not shown: what decides
the offset of o2 and o3, the part of the size field, o4 to o7, and why some writes land two tiles
back. Status: narrowed, not answered.

Reworded in 11.39: the question line asked what PDS_SIZE bits 17:16 do; it now asks what the
setup and the data rows give a pixel task, and the lane reading of o4 to o7 (which pixels write,
and which lane an output comes from) moves to Q276. The value stays high for both.

Narrowed in 11.39 (E709, 5 configurations, an x and a y job each, none repeated). With o4 guarded
by a test of g25 against k = 0 to 3 or no guard, o4 writes pairs (120 in all, 24, 25, 25, 17 and
29) for every k, all from even-even source pixels (as the 2007 pairs of tags 5 to 7 in E570's
tables by this session's pairing; plan.md's 2393 is the Opus report's pairing): the lane-0-only
model was right in 4 of 10 jobs and wrong in 6, and the predicate shows no visible effect on
whether o4 is written; the pair counts differ between configurations (17 at k = 3) and no repeat
says whether that is noise. Nothing here says what g25 selects (no guard that cannot hold was
run, Q276). Plain-job spills of o1 to o3 stay a refusal in the simulator.

Post hoc 2026-11-09 (S1, E742; an oddity, not a result): in one run of the order control (both o1
writes unpredicated) five contiguous source pixels, (16,25), (16,27) and (17..19,27), kept the first
write where 492 of 497 kept the second; one run, not repeated.
