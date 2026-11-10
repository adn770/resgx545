+++
id = "E825"
claim = "R3k stage k-pb0 (K2, 3 jobs, Q285, controls of the parameter-buffer pokes, split flow -n 2 --geometry 1 at 64 x 64, mode 2): TE 0x40 (the dump run pb-d0 and p1) reproduced E728's empty image (3969 of 4096 pixels wrong, 0 triangle pixels, first wrong pixel (1, 1) 0xff000080) and its parameter buffer words 0 to 26 (stream 04000004 00030001 04000000 at 0 to 2, E728's stretch at 11 to 26), with parameter buffer and TA data identical between the two jobs; TE 0x60 (p0, the twin) drew the whole triangle (4096 pixels, 0 wrong) with dwords 0 to 25 as the twin's; the three controls nevertheless FAILED against values frozen from jobs of another shape (E728's and the twin's one-render jobs; this stage ran two renders and the tool checks the image of render 2, which it draws on background 0xff000080, so an all-background hash differs by construction): the target hash of d0 and p1 0x8ea26cdfee74a325 against 0xfc5ff15e0434a325, p0's target hash 0xd2bfb75560f4c325 against 0xd0530839d87ea325, and p0's dword 26 0x04000004 against 0; the gate closed, which says nothing about the module ('closed: k-pb0 controls pb-d0-te40 FAIL, pb-p0-te60 FAIL, pb-p1-te40 FAIL') and stage k-pb (5 jobs, Q285's pokes) was skipped; frozen verdict 'Q285: not run (no kept k-pb)'"
unit = "isp"
method = "R3k session K2 (R3K-pixel; decisions R3-K4, R3-K6 and R3-K7), dataset render-closing-r3k-pixel, 2026-11-10, attempt out/20261110-193547 (one driver call, run/k.sh, from 19:35:47 Mac time: k-f4 19:35:48, k-pb0 19:37:30, k-pb skipped by its gate, k-bif 19:38:04; out/k.log), kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok), tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053, R1's build, not rebuilt) with the pinned tool source (TOOLSRC.sha256); preflight per stage: srcversion loaded = installed = 230E0EF5..., the debugfs files, the defaults (hold_recovery N, render_pb_pages 0x422, alias_skip 0, render_rgn_arrays 1), the six kregnow rows; a debugfs reset before each job, render_rgn_arrays written per row (read back, written back to 1 at every exit and checked by the driver), 5 fault-class events at most per stage, health after every fault and stage; 24 jobs frozen (k-f4 11, k-pb0 3, k-pb 5, k-bif 5), 19 run, 5 skipped; FROZEN.sha256 2ff760c33774cd3e7666a284ad0d986dbb7e71ec97b542c50d3bacfc8f6f9af5 and PREDICTIONS.sha256 0d2138ffdd52feef33cf80be21b579d8f00d4b44a40bec37db804158e802c179 written before the first job and verified at each stage; no failed attempt, no refreeze; stage k-pb0 (the controls that gate k-pb): `tri --tri-full --keep-going --wait-ms 20000 --width 64 --height 64 --max-width 64 --max-height 64 -n 2 --geometry 1 --poke cmd:1=TE --poke cmd:10=0xeaa26e26 --poke cmd:13=0x80000002 --poke cmd:16=0xeaa26e26 --dump-render DIR` with TE 0x40000000 (pb-d0-te40, the dump run whose dwords fix the index of the pokes; pb-p1-te40, the same job again) and TE 0x60000000 (pb-p0-te60); the dump is of the parameter buffer after the last render, the tool has no dump between the TA and the 3D (DEVIATION 3); frozen from E728's single-render jobs (texture/p1141 msaa-b-te29 t29-m2-40-64x64 on module B21FDA82, `tri --keep-going --dump-render`) and the landed twin (isp/msaa-te-dumps te-m2-60-64x64), words in gen/data/pb_words.tsv, hashes EMPTY_HASH and FULL_HASH in gen/kgen.py; the jobs ran with class ok (rc 1, 0, 1 as the image checks); the gate (score/score_k.py gate k-pb, out/20261110-193547/gate-k-pb.txt) closed and the driver skipped k-pb without running it; scored by the frozen score/score_k.py k-pb0 (out/20261110-193547/score-k-pb0.txt) and verdict (verdict.txt). The comparison of the dump words with the frozen words (d0 and p1 equal at dwords 0 to 26; p0 equal except dword 26) was made after the run on the kept dumps (gzip) with a scratch script. The frozen verify of this session pins the landed userspace/libsgxfive/tools/sgxfive-test.c (sha256 4250ca36...) by absolute path; main's file changed afterwards (8a2e8c5, libsgxfive: refuse a ba in a placed --tri slot) so the scorer refuses on main today (FROZEN FILES CHANGED); the three stage scores, the gate and the verdict were rescored from the copy in resgx545-data in a scratch copy with the pinned file (main's parent of 8a2e8c5) and the path rewritten in a scratch FROZEN.sha256, and are byte-identical to the kept ones"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3k-pixel:out/20261110-193547/k-pb0/", "render-closing-r3k-pixel:out/20261110-193547/gate-k-pb.txt", "render-closing-r3k-pixel:out/20261110-193547/verdict.txt"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "PB_OBJ.FORMAT"]
+++
**What ran.** E728: with `CR_TE_AA` bit 29 clear and bit 30 or 31 set the parameter buffer equals
the bit-29-set job's except that dwords 11 to 26 (the format word, the set masks, the packed
vertices) are one dword later, and the image is empty. Q285 asks what the displaced stretch is and
why the image is empty. Stage k-pb was to poke dwords of the parameter buffer between the TA and
the 3D (the kernel's new `par` poke space, `--kpoke-render 2:par:INDEX=VALUE`) and read H-OLD (the
3D reads the old layout: the twin's words make the twin's image) against H-FIELD (a field the ISP
expects). It runs only if k-pb0's three controls pass, so that a poke is judged against an unpoked
job that is known.

**Frozen verdict (as printed).** `SUMMARY: k-pb0: controls {'pb-d0-te40': 'FAIL', 'pb-p0-te60':
'FAIL', 'pb-p1-te40': 'FAIL'}`; the gate: `gate k-pb: closed: k-pb0 controls {'pb-d0-te40':
'FAIL', 'pb-p0-te60': 'FAIL', 'pb-p1-te40': 'FAIL'} (rerun: run/k.sh --only k-pb0)`; the verdict:
`SUMMARY: Q285: not run (no kept k-pb)`.

**Results [HW].**

| job | TE | image | parameter buffer dwords 0 to 26 | target hash | frozen hash | verdict |
|---|---|---|---|---|---|---|
| pb-d0-te40 | 0x40000000 | 3969 of 4096 wrong, 0 triangle, 4096 background | E728's own, all 27 | 0x8ea26cdfee74a325 | 0xfc5ff15e0434a325 | FAIL |
| pb-p1-te40 | 0x40000000 | as d0 | as d0; parameter buffer and TA data identical to d0's | 0x8ea26cdfee74a325 | 0xfc5ff15e0434a325 | FAIL |
| pb-p0-te60 | 0x60000000 | 0 of 4096 wrong, 4096 triangle | the twin's at 0 to 25; dword 26 0x04000004, frozen 0x00000000 | 0xd2bfb75560f4c325 | 0xd0530839d87ea325 | FAIL |

So the image and stretch controls reproduce (E728's empty image and displaced stretch at TE 0x40,
the twin's full image at TE 0x60) and the values the controls compare differ: the hash of the 64 x
64 target and p0's dword 26. The two TE 0x40 jobs agree with each other exactly (same hash, same
parameter buffer, same TA data).

**Why they failed.** The frozen values were taken from E728's one-render jobs (`tri --keep-going
--dump-render`; its hash 0xfc5ff15e0434a325 is a job whose image reads '0 triangle, 4096
background' with first pixel 0xff203040) and from the landed twin; the stage used the split flow
(-n 2 --geometry 1: two renders, the image checked and the dump taken after the second). The tool
draws render 2 on background 0xff000080 (first wrong pixel (1, 1) 0xff000080), so an
all-background hash differs from the one-render job's by construction. The controls were frozen
from a job of another shape (a design error of the stage), so the gate closing says nothing about
the module (the lead checked the one-render file of E728's dataset). The lead's follow-up, a
separate session not part of K2's freeze (closing3/overnight/r3k-regress, attempt 20261110-222647,
to be folded by the lead): on the new module 7 of 7 rows in E728's one-render shape reproduced
E728's hash, diff, dwords and dump sha256s, and 3 of 3 rows in this stage's -n 2 --geometry 1
shape gave 0x8ea26cdfee74a325 again, so the failure of the controls is the job shape, measured
there, and not a difference of the module. Two further observations: p0's image is exactly right
(0 of 4096 wrong, 4096 triangle pixels) and its hash still differs from the twin's, so the hash is
not a function of the picture alone [infer: it covers more of the target buffer, or an address];
and p0's dword 26 is 0x04000004, the value of the stream's first word, where the twin's was 0,
which reads as the header of a following object after the twin's 15-dword object in a two-render
job [infer; the landed twin job is not known to have been a two-render job].

**What it shows and does not.** The empty image at TE 0x40 and the displaced stretch reproduce on
the new module with the split flow (2 of 2 jobs), and the twin draws; nothing here is a difference
of the module. Nothing about Q285's cause: k-pb did not run, no poke was made. Whether the
controls would pass had they been frozen from this job shape is the open item: the dwords of the
dump run now give the index of the pokes and the three values to freeze, but freezing them after
seeing them is post hoc by definition, a decision for the user.
