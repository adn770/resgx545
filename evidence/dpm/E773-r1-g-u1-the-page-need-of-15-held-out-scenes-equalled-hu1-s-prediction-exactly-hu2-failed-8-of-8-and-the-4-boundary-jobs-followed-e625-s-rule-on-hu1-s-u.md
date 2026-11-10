+++
id = "E773"
claim = "R1-pixgeo stage g-u1 (21 jobs, P = 0x422 except the boundary jobs): the page need U of 17 scenes (the default triangle of the tool, one to four copies, moved or apart, at 640x480, 1024x768, 1280x1024, 2048x1536, 2048x2048 and 4096x4096) read as the peak of the low half of 0x0724 and as the free-list walk (head - 1) agreed in all 17 and equalled HU1's frozen prediction (sgx-pipe's TA model as it stands, 128 bytes a stream, a page per macrotile that has streams, plus 1 global page) with residual 0 in 15 of 15 held-out scenes (U = 21, 22, 22, 13, 24, 30, 21, 35, 11, 31, 79, 60, 7, 275 and 438), the two controls 19 and 29 passed, HU2 (macrotiles with streams plus 8) was refuted in 8 of 8 held-out scenes where it differs (and in 1 of 2 repeats), and E625's rule (overflow iff P - 0x22 is below U) with HU1's U held in the 4 boundary jobs (overflow at P = 0x39 and 0x36, completion at 0x3a and 0x37, 4 of 4, held out); the frozen verdict: controls pass, held out consistent HU1 (15) and E625's rule on HU1's U (4), refuted HU2 (8 of 8)"
unit = "dpm"
method = "R1-pixgeo stage g-u1 of the question-closing pass, round 2 (decision R2-12; 21 jobs: u-ctl-1 and u-ctl-2a the controls and the 0x072c trial, 15 held-out scenes, 4 boundary jobs b-2-m96-lo/hi at P = 0x39 and 0x3a and b-m32-lo/hi at P = 0x36 and 0x37, the commands in tables/g-u1.txt: tri --width W --height H -n K [--geometry 1..K-1] [--move k:DX,DY] --keep-going --keep-overflow --wait-ms 20000 --dump-render --dump-each --words --regs 0x0700-0x074c) of the dataset render-closing-r1-pixgeo, on the laptop (host cedar), 2026-11-10 from 09:40 laptop time (08:40 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053), regtimeline 0x0624-0x0628, 0x0654-0x0660 and 0x0720-0x0724 (+ 0x0728-0x072c once the gate passed), a debugfs reset before each job, all 21 of class ok (14 with rc 0 and 7 with rc 1, the multi-triangle scenes, whose tool line reads 'tri: 1 of 2 renders ok' because the first render is geometry only); the knob proof the job's own 0x0624 rows; U is the peak of the low half of 0x0724 and, as a cross-check, the free-list head less 1 walked in the PB dump (a disagreement would have voided the cell: none); the frozen predictions (predictions/g-u1.tsv) from the offline model of f0f8720's note on Q211 (a fit on the 16 measured U) with the proposal's HU2; the boundary pairs frozen on E625's rule with HU1's U (24 and 21), which corrects the proposal's pair for U = 24 (0x39 and 0x3a, not 0x45 and 0x46, PREFLIGHT.md section 5); scored by the frozen score/score_r1.py g-u1 (out/score-g-u1.txt), re-run on the kept files with the same SUMMARY"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r1-pixgeo:out/g-u1/"]
terms = ["Dynamic Parameter Management (DPM)", "Parameter Buffer (PB)", "ta3d_ctl"]
+++
**What ran.** f0f8720's note on Q211 recorded HU1, the TA model of sgx-pipe applied as it stands
(`tiling`, `tile_lists` per 16x16 half-region, `walk`, 128 bytes a stream, a page per macrotile that
has streams with pages = ceil(streams / 32), plus 1 global page), as a fit: residual 0 on the 16
measured U, with both constants picked from a small grid on those data. This stage is its first
held-out test: 15 scenes not measured before, frozen with HU1's U and HU2's (a macrotile count plus
8) before the first job.

**Frozen verdict.** `controls pass (u-ctl-1 = 19, u-ctl-2a = 29); held out: consistent ['HU1 (15)',
"E625 rule (HU1's U) (4)"], refuted ['HU2 (8 of 8)']; repeat only: consistent ['HU1 (2)'], refuted
['HU2 (1 of 2)']`. The repeat rows are the two controls, which are fit data run again.

**Results [HW].** U by the 0x0724 peak and by the walk, equal in every job, against HU1 (residual 0
in all 17): 1024x768 default 19 (control), two apart (0,288) 29 (control); moved (32,0) 21; moved
(0,96) 22; moved (-128,96) 22; moved (384,288) 13; two with the second at (-96,0) 24; two with the
second at (256,192) 30; three stacked 16 pixels apart 21; four at the corners (0,0), (512,0),
(0,384), (512,384) 35; 640x480 default 11; 1280x1024 default 31; 2048x2048 default 79; 2048x1536
default 60; 512x384 moved (128,0) 7; 4096x4096 moved (1024,0) 275; 4096x4096 two, the second 1024
down, 438. HU2 predicted 19, 19, 17, 12, 20, 22, 19 and 24 for the eight small held-out scenes it
covers (21, 22, 22, 13, 24, 30, 21 and 35 measured); it had no row for the others. The tool
accepted 640x480, 1280x1024 and 2048x1536, sizes it had never run, and every job completed or
overflowed as the class expects. Boundary jobs: two triangles with the second at (-96,0), U = 24:
P = 0x39 overflowed and 0x3a completed; one triangle moved (32,0), U = 21: P = 0x36 overflowed and
0x37 completed; E625's rule, overflow iff P - 0x22 is below U, with HU1's U (4 of 4).

**What it shows.** HU1 gives the page need of every scene of this family in 15 of 15 new cases,
over 7 target sizes (a 4096x4096 scene of 438 pages included), 1 to 4 copies of the triangle and
moves in both axes; the structure is E650's tiling, the two constants (128 bytes a stream, one
global page) are now held out once. U in this family is therefore computed by the TA model of
sgx-pipe plus the one global page, and E625's rule on it gives the overflow of a one-pass scene
(Q211's first clause).

**Not shown.** The scenes are copies of the one triangle of the tool (a fixed shape and set of
state words); wide scenes of many vertices (E630's 300 to 900 vertices, whose pages a vertex are a
lower bound of a model that did not close) and other triangle shapes were not run, so the clause
holds for this family only. The constants are not separated from a form of the same value (for
instance 128 bytes and one page read as 4 dwords and 32 streams). k and the spacing are not touched
by U (E779). The gate of the 0x072c reads is recorded in E775.
