+++
id = "E824"
claim = "R3k stage k-f4 (K2, 11 jobs, Q140): with the new debugfs knob render_rgn_arrays at 4 (four region-header arrays), mode 2 and CR_TE_AA 0xe0000000, 8 of 8 held-out sizes (288 x 144, 256 x 288, 384 x 384, 320 x 160, 512 x 384, 640 x 480, 320 x 400, 1024 x 768) completed with 0 wrong pixels of 41472 to 786432 and the TA data size the four-array layout gave (0x8000, 0x8000, 0xb000, 0x8000, 0xb000, 0x13000, 0xc000, 0x1e000); the controls passed (64 x 64 at knob 1 and at knob 4 complete with the same TA data size 0x6000, and 288 x 144 at knob 1 faulted at BIF_INT_STAT 0x90004, page 0x20006, as E729 did): frozen verdict 'k-f4: 8 of 8 held-out rows complete with 0 wrong pixels and four arrays in the four-array layout; controls PASS'"
unit = "ta"
method = "R3k session K2 (R3K-pixel; decisions R3-K4, R3-K6 and R3-K7), dataset render-closing-r3k-pixel, 2026-11-10, attempt out/20261110-193547 (one driver call, run/k.sh, from 19:35:47 Mac time: k-f4 19:35:48, k-pb0 19:37:30, k-pb skipped by its gate, k-bif 19:38:04; out/k.log), kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok), tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053, R1's build, not rebuilt) with the pinned tool source (TOOLSRC.sha256); preflight per stage: srcversion loaded = installed = 230E0EF5..., the debugfs files, the defaults (hold_recovery N, render_pb_pages 0x422, alias_skip 0, render_rgn_arrays 1), the six kregnow rows; a debugfs reset before each job, render_rgn_arrays written per row (read back, written back to 1 at every exit and checked by the driver), 5 fault-class events at most per stage, health after every fault and stage; 24 jobs frozen (k-f4 11, k-pb0 3, k-pb 5, k-bif 5), 19 run, 5 skipped; FROZEN.sha256 2ff760c33774cd3e7666a284ad0d986dbb7e71ec97b542c50d3bacfc8f6f9af5 and PREDICTIONS.sha256 0d2138ffdd52feef33cf80be21b579d8f00d4b44a40bec37db804158e802c179 written before the first job and verified at each stage; no failed attempt, no refreeze; stage k-f4: c3 (64 x 64, knob 1), c2 (64 x 64, knob 4), h1 to h8 (knob 4, the sizes above, h8 with --keep-overflow), c1 (288 x 144, knob 1, held: hold_recovery Y, the fault read, a debugfs reset, health) last; each job `tri --tri-full --keep-going --wait-ms 20000 --width W --height H --max-width W --max-height H --poke cmd:1=0xe0000000 --poke cmd:10=0xeaa26e26 --poke cmd:13=0x80000002 --poke cmd:16=0xeaa26e26 --dump-render DIR` with a context made for the size; the knob proof of each h row is its TA data size (the knob-1 layout's size would mean the knob did not apply: cannot tell, none); the model (the kernel's layout formula with four arrays) fits all 19 rows on record post hoc (closing3/kernel/layout_f4.out), the frozen predictions come from it and the 8 h rows are the held-out part (h8 is the largest 4x context run); scored by the frozen score/score_k.py k-f4 (out/20261110-193547/score-k-f4.txt). The frozen verify of this session pins the landed userspace/libsgxfive/tools/sgxfive-test.c (sha256 4250ca36...) by absolute path; main's file changed afterwards (8a2e8c5, libsgxfive: refuse a ba in a placed --tri slot) so the scorer refuses on main today (FROZEN FILES CHANGED); the three stage scores, the gate and the verdict were rescored from the copy in resgx545-data in a scratch copy with the pinned file (main's parent of 8a2e8c5) and the path rewritten in a scratch FROZEN.sha256, and are byte-identical to the kept ones"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r3k-pixel:out/20261110-193547/k-f4/"]
terms = ["CR_TE_AA", "region header", "Tile Accelerator (TA)"]
+++
**What ran.** E507, E729 and E788 had 4x renders at 320 x 160 and above (and 288 x 144, 256 x 288,
384 x 384) fault at pages 0x20006 to 0x2000a with the kernel's layout, which has one array of
region headers; four arrays complete a context made for 544 x 400 (E788, 0 of 128000 pixels wrong
at 320 x 400). The kernel's layout formula with four arrays fits all 19 rows on record post hoc.
The new module's `render_rgn_arrays` (1, 2 or 4, default 1, contexts made from now on) lets the
kernel itself allocate four, so the sizes that fault at one array are rerun with the kernel's own
layout, held out.

**Frozen verdict (as printed).** `SUMMARY: k-f4: 8 of 8 held-out rows complete with 0 wrong pixels
and four arrays in the four-array layout; controls {'c3-64x64-k1': 'PASS', 'c2-64x64-k4': 'PASS',
'c1-288x144-k1': 'PASS'}`.

**Results [HW].**

| job | knob | size | outcome | wrong pixels | TA data size | arrays |
|---|---|---|---|---|---|---|
| c3 | 1 | 64 x 64 | complete | 0 | 0x6000 | 4 |
| c2 | 4 | 64 x 64 | complete | 0 | 0x6000 (the same TA data and target as c3) | 4 |
| h1 | 4 | 288 x 144 | complete | 0 of 41472 | 0x8000 | 4 |
| h2 | 4 | 256 x 288 | complete | 0 of 73728 | 0x8000 | 4 |
| h3 | 4 | 384 x 384 | complete | 0 of 147456 | 0xb000 | 4 |
| h4 | 4 | 320 x 160 | complete | 0 of 51200 | 0x8000 | 4 |
| h5 | 4 | 512 x 384 | complete | 0 of 196608 | 0xb000 | 4 |
| h6 | 4 | 640 x 480 | complete | 0 of 307200 | 0x13000 | 4 |
| h7 | 4 | 320 x 400 | complete | 0 of 128000 | 0xc000 | 4 |
| h8 | 4 | 1024 x 768 | complete | 0 of 786432 | 0x1e000 | 4 |
| c1 | 1 | 288 x 144 | held fault, BIF_INT_STAT 0x90004, BIF_FAULT 0x20006061 (page 0x20006) | - | - | - |

**After c1's fault.** The reset of the held job returned an error to the runner (tee: Connection
timed out, status 1) with the registers reading clear after it; the kernel log has 'SGX recovery
failed: -110' and then 'render context cleanup failed, resetting' (a second reset). The first two
health triangles after it faulted (job faulted, context lost; 4096 of 4096 wrong) and the third
passed ('health: recovered on the retry'); the stage ended with health ok and render_rgn_arrays
back at 1. The same two failed health triangles then a pass followed the 4x fault of E826's f2
(320 x 400 at knob 1), and none followed the 3 other faults of that stage (a TA read, a texture
fetch).

**What it shows and does not.** The sizes that fault with one array complete with four, at every
size run up to 1024 x 768 (8 of 8, the knob proof held), and with exactly the TA data size the
layout model gave; a 4x job at 288 x 144 with one array faults at the page E729 gave. So the fault
of E507 and E729 is the layout's one array and not the multisampling by itself, and the kernel can
allocate four. Not shown: a default of four (the knob is debug only, default 1), four arrays at
4096 x 4096 (the layout needs 0x223000 bytes, over the 2 MiB TA-data slot, design), whether the
ZLS buffer, which keeps one array's size, is enough (it was at all 8), and the cause of the two
failing health triangles after a failed 4x job (reproduced twice, not explained).
