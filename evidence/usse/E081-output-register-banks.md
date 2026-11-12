+++
id = "E081"
claim = "A pixel's o0 lands on its own pixel (all 1062 covered pixels, in all four tables); o1-o3 write fewer pixels (508, 604, 400) and where they land is the instance's own pixel or one 16 or 32 rows and 0 or 32 columns away, a few at other offsets, for the plain table and for PDS_SIZE bits 17:16 = 0, 1, 2; the o4-o7 images (348, 348, 348, 312 pixels) equal the previous case's image at every non-background pixel and show no word of the o4-o7 write [corrected 2026-11-12, see Correction]"
unit = "usse"
method = "on the laptop, linux fork with the debug option on: probes/usse/output-registers.toml, probes oreg-x, oreg-y, oreg-size0/1/2-x and -y, a 64x64 triangle whose pixel shader writes pa0 (the pixel's x) or pa1 (y) to one register oN, one run; the source of each stored pixel found from its x,y pair in the o0 case"
tiers = ["HW", "infer"]
date = "2026-11-01"
data = ["usse-output-registers"]
terms = ["PDS_SIZE.BITS17_16", "tile"]
+++

**What runs.** The pixel program and a replaced iterator program give each pixel instance its
own x in pa0 and y in pa1. One shader writes oN = x and one oN = y, N = 0 to 7 (to 3 for
the three PDS_SIZE variants). Each stored pixel is a pair (x, y) from the two runs, which
names the instance that wrote it, because the o0 case lands every instance on its own pixel
and so gives the table from (x, y) to source pixel. The displacement is the stored pixel
minus the source pixel, in rows and columns.

**Results.** o0 lands on the instance's own pixel for all 1062 covered pixels, in the plain
table and in each of the three size tables. For o1 to o7 in the plain table 508, 604, 400, 348,
348, 348 and 312 pixels changed, of which 252, 203, 203, 203, 203, 178 and 178 are the
instance's own pixel. The others sit mostly at a displacement of 16 or 32 rows and 0 or 32
columns. For o1 the 227 displaced pixels are 74 at (-32, 0), 110 at (0, -32), 24 at (-16, 32),
8 at (16, 0) and 11 at (32, -32) in (rows, columns), and 29 pixels carry a pair that is no o0
pixel's. o2 adds (-20, 32) once, o3 adds (-12, 32) 6 times, (-4, 32) 11 times, (16, -32) 33
times and (16, -5) twice. Every displacement is at least 4 rows or 5 columns; no pixel lands
on a neighbour of its source.

With PDS_SIZE bits 17:16 at 0, 1 and 2 the same kinds of displacement appear in other numbers:
o1 changes 545, 705 and 747 pixels, o2 210, 383 and 495, o3 83, 211 and 392 (the plain table,
with the value 3, gives 508, 604 and 400).

**Not shown.** One run of each table: whether the destination varies from run to run is not
tested here. The dependence on PDS_SIZE bits 17:16 is only that the counts change; no value
of the field removes the displaced writes. What gives a pixel task more than one bank of
output registers is open. Reading as an inference **[infer]**: the output registers are banks
of one dword per pixel position, o0 the pixel's own, and oN past what the task was given
reaches the bank of another tile in flight, whose displacement is a multiple of the 32x16 tile
area.

**Correction 2026-11-12:** The claim read "A pixel's o0 lands on its own pixel (all 1062 covered
pixels, in all four tables); o1-o7 write fewer pixels (508, 604, 400, 348, 348, 348, 312) and where
they land is the instance's own pixel or one 16 or 32 rows and 0 or 32 columns away, a few at other
offsets, for the plain table and for PDS_SIZE bits 17:16 = 0, 1, 2". For `o4` to `o7` that is wrong.
Read offline from this record's own raw images (E871, `closing6/pixel/o47_e081.out`): the `o4`,
`o5`, `o6` and `o7` images equal the image of the case before at every non-background pixel, 348
of 348, 348 of 348, 348 of 348 and 312 of 312 in the x run and 348, 348, 312 and 276 of as many in
the y run. The cases ran in order, the shader wrote nothing to `o0`, and E373 showed that an output
a job does not write keeps what the job before left; so these pixels are what earlier cases left,
and the counts 348, 348, 348 and 312 and the own-pixel counts 203, 203, 178 and 178 are not counts
of the `oN` write. The [infer] reading "oN past what the task was given reaches the bank of another
tile in flight" rests on `o1` to `o3` only (E570 placed those displaced words). In E709's command
the own words of `o4` to `o7` reach no pixel either (E871: 0 of 12143 marked words of E858's walk).
The words carry no marker, so a write of the same value at an own pixel cannot be told from a
leftover; the claim line was edited to this reading (HACKING.md, Workflow).
