+++
id = "E502"
claim = "Under multisampling the pixel program's iterated position is the pixel's x + 0.375 and y + 0.125, the same as in mode 0 and for the five CR_TE_AA values tried (0, 0x20000000, 0x60000000, 0xa0000000, 0xe0000000; mode 0 only with 0x20000000), not the pixel centre: in 48 identity-map runs (40 configurations of modes 0, 1, 2 and CR_TE_AA 0 to 0xe0000000 at five target sizes from 64 x 64 to 128 x 128, four of them run three times; 96 jobs, an x job and a y job a run) 401977 of the 402432 stored pixels of the x jobs decode to a pixel with those offsets, the other 455 hold the background colour, none holds any other value, a CR_TE_AA of 0 and of 0x20000000 give byte-identical outputs in 10 of 10 pairs of configurations (20 of 20 jobs) and the 8 repeat runs are byte-identical to their first runs (16 of 16 jobs)"
unit = "isp"
method = "on the laptop (direct cable), linux fork 6ee9501832af, module srcversion 14D099861204842EA496D85, tool sgxfive-test-1126 (sha256 751f7223c8c731a08d75cfc3920a5d1050488ca3bdc426be45b7c431e600f82e), probes/isp/msaa-ident.toml (script msaa-ident.sh): probe --tri pixpds:12 --tri-full with E437's PDS program (source 0, two components, pa0 = x and pa1 = y iterated) and a pixel shader writing pa0 (an x job) or pa1 (a y job) as the colour, two jobs a configuration, CR_ISP_MSAA mode in cmd:13, the sample words 0xeaa26e26 in cmd:10 and cmd:16, CR_TE_AA in cmd:1; 40 configurations run once and the four 64 x 64 configurations of modes 1 and 2 with CR_TE_AA 0 and 0xe0000000 run twice more (48 runs); the decode of the recompute script written before the run (recompute_p1126.py, x + 0.5) found no pixel, so the offsets were read from the mode 0 control and the reading repeated by analysis/an_ident.py of the dataset; recompute_p1126.py crashed on a faulted job of another dataset (a tool message in a row line) and recompute_p1126b.py, which differs from it only by skipping tokens that do not parse, is the one whose output the datasets keep"
tiers = ["HW", "infer"]
date = "2026-11-08"
data = ["isp-msaa-ident"]
terms = ["CR_ISP_MSAA", "CR_TE_AA"]
+++

**What ran.** The 48 runs of the declared set (96 jobs, every one exited 0; the declared fit size
is 64 x 64 and the declared held-out sizes are 128 x 128, 128 x 64, 64 x 128 and 96 x 80): A (64 x
64, the fit: mode 0 with CR_TE_AA 0x20000000, modes 1 and 2 with 0, 0x20000000, 0x60000000,
0xa0000000, 0xe0000000: 11), B (the same at 128 x 128: 11, held out), C (128 x 64, 64 x 128 and 96
x 80, modes 1 and 2, 0, 0x20000000, 0xe0000000: 18, held out) and D (four of A's configurations,
modes 1 and 2 with 0 and 0xe0000000, twice more: 8 repeat runs), every job's whole output kept
(gzip).  The tool of the run is the 11.24 tool with `probe --tri ... --tri-full` (the triangle
covers the target, every tile has pixels); the fallback triangle was not used.

**Result.** [HW] The position iteration works under multisampling: every stored pixel of every job
holds a float, and in the mode 0 control at 64 x 64 (4096 of 4096 pixels) the x job reads x + 0.375
and the y job y + 0.125 (0x3ec00000 and 0x3e000000 for the first pixel). Over the 48 x jobs 402432
pixels are stored, 45056 in the fit, 324608 in the held-out sizes and 32768 in the repeats; 401977
decode to a pixel with those offsets (44992, 324217, 32768), 455 are the background colour
0xff203040 in both jobs and none is another value (every sample slot of a pixel holds the same
iterated value, so an average equals that value and these pixels cannot show a resolve). The offsets
do not change with the mode or with the five CR_TE_AA values tried (mode 0 only with 0x20000000), so
the iterated position is not a sample's position (a sample would move with the mode) [infer]. The
declared recompute decodes x + 0.5 and found 0 decodable pixels in 48 of 48 runs (it prints
"off-centre" for all): that is a fault of the declared decode, kept in the dataset
(analysis/recompute-b.txt), and the declared H30a test (0 of 48 decodable) did not run as written.
The reading here and in E503 is post hoc (the offsets came from the control of the fit set, the rule
of E503 from the fit set's 64 x 64 jobs; the held-out sizes were then compared with it and, by the
author's statement, not used to adjust it).

**Repeatability.** [HW] CR_TE_AA 0 and 0x20000000 give the same raw output in 10 of 10 pairs (modes
1 and 2 at 64 x 64, 128 x 128, 128 x 64, 64 x 128 and 96 x 80); the D repeats are identical to the
fit's outputs in 8 of 8 (modes 1 and 2, CR_TE_AA 0 and 0xe0000000).

**What it does not show.** The position at a sample (every pixel's samples hold the same iterated
value, so the samples themselves cannot be named by this probe); the 455 background pixels (13
tiles in 8 configurations, E503).
