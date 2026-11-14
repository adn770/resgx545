+++
id = "E1056"
claim = "r15-isp stage zcut (11 jobs, E1045's form on six held-out triangles with one vertex depth at 1.25 or -0.25): the triangle is clipped as a polygon at z = 1 and z = 0 and each made vertex is rounded half away from zero to 1/256 pixel, then covered by E606's rule (frozen H-POLYCLIP held 6 of 6 target images pixel for pixel and the count of background dwords, and all 4608 band dwords of each kept dump as words or planes; the per-pixel cut H-PIXCUT and the unrounded polygon H-POLYCLIP-NR, one image on these rows, FAILED 6 of 6, on 8 to 11 pixels a row), so the cut shares E1037's rounding; and ISP word 0 bit 16 or 17 flipped on the library triangle removes every pixel (H-NONE held 2 of 2, H-EQUIV, the 48 pixels bit 15 leaves, FAILED 2 of 2); the three controls (E1045's wind-zhi and wind-zlo and E065's bit 15 job) read their kept values"
unit = "isp"
method = "r15-isp (render/closing-r15-isp), stage zcut of the question-closing pass (round 15's session r15-isp, decisions R15-1 to R15-9 (a): safe class only, no tool change, one stage; the round 15 ranking plan, sections 2 and 3, row zcut (Q241)), built on the session kit (resgx545 main 158bdc5, data cddc7b60b) and frozen before the run, dataset render-closing-r15-isp; attempt out/20261114-073059 (scores score-zcut.txt); on the laptop (host cedar, module srcversion B60AB0B475DD1E8972419B5, fork 2a650d74, loaded = installed, the kit's preflight, stock firmware), tool ~/sgxfive-test-t10 (sha256 9bedc2d6db70b2691698478572e311cf2b9b54acfaf8d714ed4db47852e322eb, source resgx545 a581c06, recipe data:render/closing-r10-st1/lead/build_tool10.sh, every row replayed on the library mock built from it before the freeze), every job one process of the kit runner (kit/run_stage.sh) with a debugfs reset and the health fill and triangle between jobs, every output kept gzipped; the rows are tables/zcut.txt, the frozen predictions predictions/zcut.tsv and predictions/zcut/ (gen/make.py, gen/zcut.py); run by the lead with the kit's driver, 2026-11-14 (logs fold/run-r15i.log, fold/stage-r15i.log), no stop, every job `job: ok`; the frozen score/score.py re-run on the kept files is byte-identical (fold/reproduce.out); fold/dumpcheck.py (fold/dumpcheck.out) and fold/rust_rows.py (fold/rust_rows.out) added at the fold; freezes: FROZEN.sha256 73e34189ff820e52b8e0b494ebb7e7541fa02a87c9837f00e0bbab705f6af2ee (67 lines), PREDICTIONS.sha256 8b190155addb227cf593f3405c1c3c7b96655cfe4a7ff9cf1445526696fb1956 (63 lines); FROZEN.commits pins the kit and every input at resgx545 158bdc5 and resgx545-data cddc7b60b (tool built from a581c06bb24d2f77e03d9b64f7ca1b2d5487b59f); stops in the logs: none; lead decisions in the logs: none"
tiers = ["HW", "infer"]
date = "2026-11-14"
data = ["render-closing-r15-isp:out/20261114-073059/zcut/", "render-closing-r15-isp:fold/"]
terms = ["ISP0", "ISP0.DCMP_MODE"]
+++
**What ran.** E1045's setting (80 x 40, CR_ISP_ZLSCTL 0x00171014, the depth buffer pre-filled
0xdeadbeef and dumped, ISP word 0 0x01c00200 = compare always with the depth written, every row
`--pixels`) on six triangles with one vertex depth at 1.25 (cut at z = 1: zcut-hi1 to hi3) or -0.25
(cut at 0: zcut-lo1 to lo3), the other two depths 0 to 1. The vertices were found by a seeded
search so that the cut line, built on the pixel-centre lattice, passes within 1/512 pixel of 8 to
10 pixel centres and the made vertices fall up to half a unit off the 1/256 grid; every vertex
lies inside H-VP's guard (E1036), two rows have the vertex order reversed. Three frozen forms:
H-PIXCUT (the plane is drawn and a pixel is removed iff its depth at the centre lies past [0, 1]),
H-POLYCLIP (the MTE clips the polygon at the plane, E287, each made vertex the exact intersection
rounded half away from zero to 1/256 pixel on both coordinates, E1037's CLIP-HA, then E606's
coverage with its tie rule) and H-POLYCLIP-NR (the made vertices unrounded). H-PIXCUT and
H-POLYCLIP-NR are one image on every row (they part only on an exact tie, which H-PIXCUT leaves
undetermined); H-POLYCLIP parts from them on 8 to 11 target pixels and 8 to 11 background dwords a
row, none undetermined. The scorer decides on the target image and the count of 0x3f800000 dwords
of the `depth #1:` line; the dumps are kept and were checked at the fold. Controls: E1045's
wind-zhi and wind-zlo (drawn 1600, hash and `depth #1:` line) and E065's `blk:1^=0x8000` job on
the library's 64 x 64 triangle (48 pixels, hash 0x7e7562918f5b5125). Two more rows flip ISP word 0
bit 16 and bit 17 (`blk:1^=V`, E065's form) on that triangle with `--pixels`: H-EQUIV (the pixels
bit 15 leaves) against H-NONE (none).

**Frozen verdict (as printed).** `out/20261114-073059/score-zcut.txt`: "SUMMARY: zcut: H-POLYCLIP:
... (6 of 6 rows decided)"; "H-PIXCUT: ... is not supported: 0 held, 6 FAILED, 0 cannot tell of
6"; "H-POLYCLIP-NR: ... is not supported: 0 held, 6 FAILED, 0 cannot tell of 6"; "H-NONE: ... (2 of
2 rows decided)"; "H-EQUIV: ... is not supported: 0 held, 2 FAILED, 0 cannot tell of 2". The three
CONTROL lines PASS.

**Results [HW].** Every cut row drew the H-POLYCLIP image on all 3200 target pixels and the
form's count of background dwords (3859, 4035, 3842, 3160, 3387 and 4025 for the six rows); on
each the 8 to 11 pixels where H-POLYCLIP parts from the exact cut (10, 8, 8, 11, 11, 10) were
drawn as H-POLYCLIP 10, 8, 8, 11, 11 and 10 times and as the exact cut 0 times. The kept dumps
(fold/dumpcheck.out): every one of the 4608 band dwords of each row that H-POLYCLIP says is 1.0 is
1.0, and every drawn dword matches the plane of the original vertices within 7.8e-5 (E1045's two
rows, whose cut crosses the grid exactly, within 1e-7): the stored depth of a clipped polygon is
not the original plane to the last bit, and no plane through three vertices of the rounded
polygon fitted better than 1e-5 (a scratch fit of the six rows: the depth is not modelled). Bits
16 and 17 each left no pixel (drawn 0, hash 0xfc5ff15e0434a325, E065's two jobs byte for byte:
H-NONE 2 of 2); the pixel set of the bit 15 control (48 pixels) differs from theirs by those 48
pixels. The builder predicted H-POLYCLIP and H-NONE [infer]; both held.

**What it shows.** A vertex depth past [0, 1] is cut by clipping the polygon at the plane with
the made vertices rounded half away from zero to 1/256 pixel, the rounding the guard clip showed
(E1037), and not pixel by pixel nor with an unrounded made vertex: the two rival cuts draw the
exact line and differ from the hardware at pixel centres within about 1/366 pixel of it
(rounding moves a made vertex by up to half a unit on each axis), on every one of six rows with
both signs of the cut, three vertex orders and slopes 1/4 to 2/3 [infer: the clip's coverage is
E606's, which this reads again]. Bits 16 and 17 of ISP word 0 remove the library triangle whole,
as they removed E977's ramp in both vertex orders (E1045): the bits are not a winding on either
triangle, and bit 15 leaves 48 pixels of the library triangle only (E065, again).

**What it does not show.** What bit 15 keeps (the 48 pixels are one kept set, its rule is not
read), bit 18 (it faulted, E065), the depth of the clipped polygon's stored plane (within 7.8e-5
of the original, no model), the order of this clip and the guard clip (E1045's ramp has vertices
past the guard and its rows agree either way), a cut at both planes of one triangle, the
visibility counter and the polygon offset's units, the pass types over several triangles and the
gate pairs.
