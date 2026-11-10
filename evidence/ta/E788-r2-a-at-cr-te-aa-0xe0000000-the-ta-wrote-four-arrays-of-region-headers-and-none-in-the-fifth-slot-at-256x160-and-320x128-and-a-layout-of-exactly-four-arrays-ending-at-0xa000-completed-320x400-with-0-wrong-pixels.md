+++
id = "E788"
claim = "R2-pixel stages r2-a-safe and r2-a-fault, Q286 (6 jobs, mode 2, --tri-full, the tool's triangle with CR_TE_AA 0xe0000000 unless noted): the controls passed (a4, 320x400 at CR_TE_AA 0x20000000 in a render context made for 544x400: TA data 0xa000 bytes, one array of region headers from 0x4000, nothing below 0x4000 or from 0x5800, and the image of E727's region model, 28 of 128000 pixels wrong with the first at (304, 128), the control value frozen from the model; a6, 320x400 at 0xe0000000 in a context made for 320x400, held: BIF_INT_STAT 0x90004 at page 0x20008), the TA data of the two completing sizes held four arrays and nothing in a fifth (a1, 256x160, own context: 0 of 40960 wrong, non-zero dwords in the slots of 0x600 bytes from 0x4000: 256, 160, 256, 160, 0, 0; a2, 320x128: 0 of 40960 wrong, 256, 256, 160, 160, 0, 0; nothing below 0x4000; the replicate a3 of a1 had a1's TA data sha256, eaa6c96c0b8d7739), so f = 4 for what the TA writes, and the held-out sufficiency job a5 (320x400 at 0xe0000000 in the context made for 544x400, whose TA data is 0xa000 bytes = 0x4000 + 4 x 0x1800 and has no room for a fifth array at the 0x1800 spacing) completed with 0 of 128000 pixels wrong and four arrays written (non-zero dwords per array 1024, 800, 640 and 584), where a context made for 320x400 alone faulted (a6): four arrays suffice at 320x400; H4 (f = 4) held on the three frozen rows it predicted (slot 4 zero in a1 and a2, a5 completes in 0xa000) and H5 (a fifth array written or needed) was not supported by any"
unit = "ta"
method = "R2-pixel stages r2-a-safe (4 jobs: a4 control, a1, a2 held out, a3 replicate of a1) and r2-a-fault (2 jobs: a5 held out, held; a6 control, held, last) of the question-closing pass, round 2 (decisions R2-7 to R2-9 and R2-17), dataset render-closing-r2-pixel (attempt 20261110-105258), on the laptop (host cedar), 2026-11-10 from 10:54:17 laptop time (09:54 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053, not rebuilt); each job tri --tri-full --keep-going --width W --height H --max-width --max-height --wait-ms 20000 with the poke words --poke cmd:1=0xe0000000 (0x20000000 for a4), cmd:10=0xeaa26e26, cmd:13=0x80000002 and cmd:16=0xeaa26e26 and --dump-render, a debugfs reset before each job, the knob proof the tool's own echo `render context for targets up to WxH` (544x400 for a4 and a5, 320x400 for a6) and the TA data dump's size; a4 refrozen after S3 (E762) to the model's 28 pixels, the first (304, 128), not to the 'diff 0' that failed there; the held jobs a5 and a6 with hold_recovery Y (always restored to N and read back), a6 last because a 4x fault can leave the next triangle faulting (E729); the conditional slack pair (288x656 in a context for 544x656) was not run, its gate printed 'not needed (a5 completed with four arrays: H4)'; scored by the frozen score/score_r2.py (out/20261110-105258/score-r2-a-safe.txt, score-r2-a-fault.txt and verdict.txt); the lengths of the arrays in non-zero dwords were read by the scorer's slot reader from the kept TA data"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r2-pixel:out/20261110-105258/r2-a-safe/", "render-closing-r2-pixel:out/20261110-105258/r2-a-fault/"]
terms = ["CR_TE_AA", "CR_ISP_MSAA"]
+++
**What ran.** E729 bounded the number f of region-header arrays the TA writes at `CR_TE_AA`
0xe0000000 to 4 or 5; E728's dumps showed four and nothing in the fifth slot at 64 x 64 and 128 x
128, which does not show that a layout of four is enough. S3's rerun of the decisive job failed
its control by a design error (E762), the model gives 28 wrong pixels at 320 x 400 at TE 0x20 and
not 0. This session reruns S3's design: a4 with the model's value, a1 and a2 (completing sizes,
their TA data read for the number of arrays), a replicate, a5 (the held-out sufficiency: 320 x
400 at 0xe0000000 in the context made for 544 x 400, whose TA data of 0xa000 bytes ends after four
arrays at the 0x1800 spacing) and a6 (the same size in a context made for 320 x 400, held, which
faults).

**Frozen verdict.** `Q286: closed H4: four arrays written at three layouts and sufficient at
320x400 (a5)`; the stage lines `a4 control: PASS`, `a1-256x160-dump: ... slot 4 zero (H4 zero, H5
written)`, `a2-320x128-dump: ... slot 4 zero (H4 zero, H5 written)`, `a3 replicate: TA data
sha256 equals a1's (eaa6c96c0b8d7739)`, `a6-320x400-max320 control: PASS`, `a5-320x400-max544:
completed, 0 of 128000, slots [1024, 800, 640, 584]` and the summaries `r2-a-safe: a4 control PASS
(TA data 0xa000, 28 wrong pixels as E727); slot 4 zero at 256x160 and 320x128: H4 for what the TA
writes (f = 4)` and `r2-a-fault: a6 PASS; a5 COMPLETES with 4 arrays in 0xa000: four arrays
suffice at 320x400 (H4 sufficiency); E1 TA write: HE`. The last clause is E789's.

**Results [HW].** a4: 28 of 128000 wrong, first (304, 128) 0xff203040 where 0xff00ff00 was
expected, the pixels E727's model puts in the background; TA data 0xa000. a1: 0 of 40960 wrong;
a2: 0 of 40960 wrong; their slot counts are in the claim, the first four slots written and the fifth
and sixth empty, nothing below 0x4000. a5: 0 of 128000 wrong, completed with rc 0, the TA data
0xa000 with four arrays. a6: the held fault 0x90004 at 0x20008 [infer: the layout made for 320 x 400
alone is shorter than the four arrays need there; the job's own layout was not dumped].

**What it shows and does not.** For what the TA writes at TE 0xe0 and mode 2, f = 4 is now held
out at two sizes (a1, a2) and a layout with room for exactly four arrays completes 320 x 400, where
the context made for that size alone faults (a6): the fifth array is not needed there. It is one
size: the tall slack case
(a layout with a page of slack past four arrays, 288 x 656 in a context for 544 x 656) was not run
because a5 completed. What the kernel's `sgx_render_layout` must allocate at other sizes, and why
the health triangles after a 4x fault fault again (E729's contamination note), are the kernel's
and are not answered by these jobs (Q140, Q286).
