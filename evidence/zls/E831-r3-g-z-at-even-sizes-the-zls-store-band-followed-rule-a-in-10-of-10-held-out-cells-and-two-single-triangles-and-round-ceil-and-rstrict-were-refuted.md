+++
id = "E831"
claim = "R3-geo-c stage g-z (15 jobs, E730's isp-a-guard rows: a depth ramp drawn by the full-screen triangle or by one placed triangle, the depth buffer pre-filled with 0xdeadbeef, a dword stored iff it is not 1.0f as E465 reads it): the three controls reproduced E730 (924, 924 and 3444 stored, rule A's sets), and on the 10 held-out full-screen cells at even sizes (widths 20, 36, 44, 76, 32 and 64 at H 18; heights 20, 28, 36 and 32 at W 34) the stored set was the frozen rule A's, x + 0.5 < 1.25 W and y + 0.5 < 1.25 H cut at the target's tile area, in 10 of 10 (FLOOR, x < floor(1.25 W), gives the same sets at every even size and was consistent too), while ROUND and CEIL were refuted in 10 of 10 and RSTRICT (x + 1 < 1.25 W) in 6 of 10; where 1.25 W or 1.25 H passes the tile area (W 32 and 64, H 28 and 32) the store stopped at the last tile (extents 32, 64, 32 and 32); two single triangles that do not cover the band stored exactly their own pixel-centre raster cut by the band (z-tri-in 96 of 96 at 34x18, wholly inside the band; z-tri-cross 357 of 357 at 36x20, crossing its edge; RSTRICT's raster refuted by 37 pixels): the band rule of E730 holds held out at every even alignment, and only the fraction .75 of 1.25 W, which needs odd sizes, still separates rule A from FLOOR"
unit = "zls"
method = "R3-geo-c stage g-z of the question-closing pass, round 3 (session L1b, the add-on C1 of decision R3-R1 a, with R3-R5 c and the even-size deviation R3-50 a; first of three stages, 15 jobs: 3 controls at E730's sizes and 12 held out), dataset render-closing-r3-geo-c, on the laptop (host cedar, direct cable), 2026-11-10, stage started 16:53:04 laptop time (out/g-z.log), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job tri --keep-overflow --wait-ms 20000 --width W --height H, either --tri-full (the triangle (0,0), (3W,0), (0,3H)) or --tri-v with three vertices in 1/256 pixel, --tri-z 0.25,0.75,0.25 --depth --depth-ctl 0x17100c (0x171014 at 66 wide, the tile row pitch) --depth-fill 0xdeadbeef --depth-dump --depth-pages 18 --poke blk:1=0x00400200, E730's options token for token on the controls, a debugfs reset before each job, all 15 of class ok (rc 0, the tool's 'diff: 0 of W*H pixels' on every full-screen job); the stored set, extents and verdicts by the frozen score/score_r3.py g-z (out/score-g-z.txt), re-run on the kept files on 2026-11-11 with byte-identical output; the five rules and the raster model (pixel centre inside the triangle, centres within 1/16 pixel of an edge ambiguous) frozen in gen/r3_geo.py and predictions/g-z.tsv before the run; the dump dwords outside the target's tiles read after the run with the session's own dump index (gen/r3_geo.py dword_index) by a scratch script, not in the copy"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3-geo-c:out/g-z/"]
terms = ["CR_ISP_ZLSCTL"]
+++
**What ran.** E730 found the stored triangle depth of the ZLS store to be the band x < 1.25 W and
y < 1.25 H, re-scored post hoc on 12 jobs whose widths were all 2 mod 4 and heights 2 mod 8, so
that the edge form was not determined. Q287 asked for the other alignments, for targets whose band
passes the tile area and for a triangle that does not cover the band. G-z froze rule A
(x + 0.5 < 1.25 W, i.e. x < ceil(1.25 W - 0.5), likewise in y) against FLOOR (x < floor(1.25 W)),
ROUND (x < floor(1.25 W + 0.5)), CEIL (x < ceil(1.25 W)) and RSTRICT (x + 1 < 1.25 W), each cut
at the tile area (32 x 16 tiles), and predicted the stored count and the set's hash of every cell.
The tool refuses odd sizes (`render.c`, `width % 2 || height % 2`), so the fractions .25 and .75
of 1.25 W could not run (deviation R3-50 a, decided before the run): the cells are W = 0 mod 4
(1.25 W an integer) and the band past the tile area.

**Frozen verdict (as printed).** `controls pass (E730's 924, 924, 3444 and rule A's sets); held
out: consistent ['A (10)', 'FLOOR (10)', 'A raster (2)', 'FLOOR raster (1)', 'ROUND raster (1)',
'CEIL raster (1)'], refuted ['ROUND (10 of 10)', 'CEIL (10 of 10)', 'RSTRICT (6 of 10)',
'RSTRICT raster (1 of 1)']; repeat only: consistent none, refuted ['ROUND (3 of 3)', 'CEIL (3 of
3)']; rule A 10 of 10 held-out full-screen cells`.

**Results [HW].** Stored = tile-area dwords that are not 1.0f; extent = (max x + 1, max y + 1).

| job | set | size | stored | extent | rule A's extent before the tile cut |
|---|---|---|---|---|---|
| z-ctl-34x18-x | control | 34x18 | 924 | 42, 22 | 42, 22 |
| z-ctl-34x18-y | control | 34x18 | 924 | 42, 22 | 42, 22 |
| z-ctl-66x34-x | control | 66x34 | 3444 | 82, 42 | 82, 42 |
| z-w20 | held out | 20x18 | 550 | 25, 22 | 25, 22 |
| z-w36 | held out | 36x18 | 990 | 45, 22 | 45, 22 |
| z-w44 | held out | 44x18 | 1210 | 55, 22 | 55, 22 |
| z-w76 | held out | 76x18 | 2090 | 95, 22 | 95, 22 |
| z-h20 | held out | 34x20 | 1050 | 42, 25 | 42, 25 |
| z-h28 | held out | 34x28 | 1344 | 42, 32 | 42, 35 |
| z-h36 | held out | 34x36 | 1890 | 42, 45 | 42, 45 |
| z-w32 | held out | 32x18 | 704 | 32, 22 | 40, 22 |
| z-w64 | held out | 64x18 | 1408 | 64, 22 | 80, 22 |
| z-h32 | held out | 34x32 | 1344 | 42, 32 | 42, 40 |
| z-tri-in | held out | 34x18 | 96 | 39, 20 | 42, 22 |
| z-tri-cross | held out | 36x20 | 357 | 45, 25 | 45, 25 |

No tile-area dword was left at 0xdeadbeef in any job. In the 10 held-out full-screen cells the
stored set equals rule A's (and FLOOR's) by hash. In the six cells with W or H = 0 mod 4 below
the tile edge (W 20, 36, 44, 76; H 20, 36) RSTRICT stops one pixel short and is refuted; in all 10
the other dimension (H 18 or W 34, 1.25 H = 22.5 or 1.25 W = 42.5) stops at 22 or 42, one short of
ROUND and CEIL. Where the band passes the tile area (W 32 and 64, H 28 and 32) every pixel of the
tile area up to the band in the other dimension is stored, so the cut is the tile area's edge.

The single triangles (`--tri-v`, vertices in pixels): z-tri-in (24, 8), (40, 8), (24, 20) at
34 x 18, past the target and wholly inside the band (42 x 22); z-tri-cross (24, 8), (80, 8),
(24, 56) at 36 x 20, crossing the band's edge (45 x 25) at its corner. Each stored exactly the
pixel-centre raster of the triangle cut by rule A's band, with no ambiguous pixel (96 of 96, 357 of
357, nothing missing and nothing beyond); RSTRICT's cut leaves 320 and the store wrote 37 more.

**Read after the run [HW, not held out].** In all 15 dumps every dword outside the target's tiles
(15872 to 16384 dwords a job: the pages past the last tile and the pitch gap where there is
one) still held the 0xdeadbeef pre-fill: the store wrote the target's tiles and nothing else, so
a band that passes the tile area is not stored past it.

**What it shows.** [HW] At every even alignment the ZLS store keeps the triangle's depth in a
tile at x + 0.5 < 1.25 W and y + 0.5 < 1.25 H (equivalently x < floor(1.25 W) at even sizes),
cut at the target's tile area, and the background depth 1.0 elsewhere in the target's tiles; a
triangle that does not reach the band's edge is stored as its own raster, pixels past the target
included. With E730 this answers Q122's rule (what an edge tile holds past the target) held out,
for even sizes. [infer] The band reads as a guard band at 1.25 times the target, as E730 said; no
clip measurement was made.

**What it does not show.** Odd sizes: 1.25 W with the fraction .75 is the only case where rule A
(n + 1) and FLOOR (n) differ, .25 is a confirmation (Q287). One depth format and one control word
(0x17100c / 0x171014); the iterated attributes are Q291. The raster model is exact on two
triangles and has no tie rule.
