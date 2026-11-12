+++
id = "E847"
claim = "R4-render4x stage t (7 jobs, 64 x 64): the frozen verdict for Q293 is cannot tell, because its two baseline controls (the line and the point object of the 11.31 sessions without a poke) are NODATA: the scorer reads a job's dump as NAME.tri.param.bin.gz and the probe rows kept theirs under the program's name (NAME.p1131-green__0.param.bin.gz, NAME.p1131-psizes__1.param.bin.gz), so neither the baselines nor the poked line and point were compared; the control t6 (E827's pb-e40-m2-64a) passed and on a context made for 4x targets CR_TE_AA 0x40000000 and 0x80000000 gave dword 11 = 0, the format word 0x00040101 at dword 12 and an empty image, as on one array (rows held, gated); read after the run from the kept dumps with the frozen insertion check, the baselines equal their frozen heads and CR_TE_AA 0x40000000 inserted one zero dword right before the format word of the line (dword 9) and of the point (dword 11), the image then empty: H-PAD's frozen positions and value, post hoc"
unit = "ta"
method = "R4-render4x (R4-G) stage t (fault limit 1) of the question-closing pass, round 4, dataset render-closing-r4-render4x, second attempt out/20261111-211649 (stage t 21:18:37 Mac time; the lead's `run/k.sh --from o` after E845's stop), laptop host cedar, 2026-11-11, the boot, kernel, module (srcversion 99CD90DA26E3AFF9C450517), firmware and tool (sha256 e6951558...) of E845; t1 and t2 `tri --tri-full --keep-going --keep-overflow --wait-ms 20000` at 64 x 64 with --aa4 (a context made for 4x targets) and E824's words with cmd:1 = 0x40000000 or 0x80000000, --dump-render; t6 the same at one array (render_rgn_arrays 1, no --aa4), E827's pb-e40-m2-64a; t3b and t3 the 11.31 line (`probe --tri pixel` with the program p1131-green__0, block words 1, 6 to 9 and VDM word 2 of resgx545-data ta/line-point), t4b and t4 the 11.31 point (`probe --tri vtxuse` with p1131-psizes__1, ta/points), t3 and t4 with `--cmd 1=0x40000000` at render_rgn_arrays 1, all with --dump-render; a debugfs reset before each job, all 7 of class ok, health ok after the stage; the words, positions and images frozen in predictions/t.tsv before the first job (FROZEN.sha256 80a16d2b..., PREDICTIONS.sha256 7ceff7ba...); scored by the frozen score/score_r.py t (out/20261111-211649/score-t.txt), re-run on the kept files on 2026-11-11 with byte-identical output; the probe rows' dumps read after the run (post hoc) by a scratch script that applies the frozen scorer's own insertion() and predictions to them, not in the copy"
tiers = ["HW", "infer"]
date = "2026-11-11"
data = ["render-closing-r4-render4x:out/20261111-211649/t/", "render-closing-r4-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "PB_OBJ.FORMAT"]
+++
**What ran.** E728 and E829 found that with `CR_TE_AA` bit 29 clear and bit 30 or 31 set the TA
inserts a zero dword before the triangle object's format word and the 3D, reading dword 11 as the
format word, draws nothing. Q293 asks what the dword is. Stage t froze H-SAME (a context made for
4x targets reads the displaced layout as one array does: dword 11 zero, empty image), H-PAD (for
a line and a point object, objects with a width, the inserted dword is zero and sits right before
the format word) against H-FIELD (non-zero), with the unpoked line and point run in the same boot
as baselines (t3b, t4b) and E827's row as the control (t6).

**Frozen verdict (as printed).** `t: cannot tell: controls: t3b-line-base: NODATA;
t4b-point-base: NODATA` (score-t.txt adds s0's three controls as NODATA, s0 being in the first
attempt). Rows: t6 `PASS: as frozen (hash 0xfc5ff15e0434a325, diff 3969 of 4096 pixels, ...)`;
t3b and t4b `NODATA (nothing read for par_0_32: the output or a dump is missing)`; t1 and t2
`H-SAME held: dword 11 0x00000000, dword 12 0x00040101, image: 0 triangle, 4096 background, 0
other`; t3 and t4 `cannot tell: the dump is not the baseline's with one dword inserted (no single
insertion in dwords 0-63)`.

**Why the baselines are NODATA (read after the run).** Every dump was kept: the tri rows as
`NAME.tri.param.bin.gz`, the probe rows as `NAME.<program>.param.bin.gz`, the name the tool gives
a probe's dump. The scorer looks only for `NAME.tri.param.bin.gz`, so for t3b, t3, t4b and t4 it
had no dump: the baselines' frozen heads could not be compared (NODATA), and the insertion check
of t3 and t4 ran on no data at all, which its message reports as "no single insertion". It is a
naming mismatch between the runner and the scorer, not a hardware result, and it gates the stage.

**Results [HW].** t1 (0x40) and t2 (0x80) on the four-array context: dwords 8 to 13 read
0x000010f0, 0x4e224830, 0x000e1010, 0, 0x00040101, 0 as t6's on one array, and all three images
are the background only, hash 0xfc5ff15e0434a325. The four probe jobs returned rc 0.

**Read after the run [HW, post hoc; not rescored].** With the frozen `insertion()` and the frozen
predictions applied to the probe rows' own dumps:

| job | dwords 0 to 31 vs frozen | one dword inserted | image (o0) |
|---|---|---|---|
| t3b-line-base | equal | - | 4048 background, 48 line pixels, as frozen |
| t3-line-te40 | - | at 9, 0x00000000 (frozen 9, 0) | 4096 of 4096 background |
| t4b-point-base | equal | - | 4093 background, 3 point pixels, as frozen |
| t4-point-te40 | - | at 11, 0x00000000 (frozen 11, 0) | 4096 of 4096 background |

So with 0x40000000 the line's format word moves from dword 9 to 10 and the point's from 11 to 12,
a zero before each, everything else one later in the first 64 dwords, and both images are empty.

**What it shows.** [HW, post hoc] The inserted dword is zero and sits right before the format
word for a line and a point object as for the triangle, at 0x40 (H-PAD's frozen positions and
value; H-FIELD not seen); the triangle's insertion and empty image are the same on a context made
for 4x targets as on one array (rows held under a closed gate). [infer] The dword reads as padding
the TA writes in this configuration rather than a field of the object.

**What it does not show.** No frozen claim: the stage's gate is closed by the scorer's dump name.
One value of the poke for the line and the point (0x40), one object each, one run; other values
at dword 11, render 2's own object, and whether some other setting makes the 3D read the
displaced layout, stay open (Q293).

**Correction 2026-11-12:** (after R5-render4x, E865) The post hoc reading of this record holds
under a frozen verdict: with the scorer finding a probe's dump by its program's name, the baselines
passed and 0x40000000 inserted one zero dword at 9 for the line and at 11 for the point, as read
here (replicates), and 0x80000000, never run on them before, did the same (held out): 6 of 6 rows
decided (E865). Of the open items above, 0x80 on the line and the point is now measured; the other
values at the dword, render 2's own object and a setting that makes the 3D read the displaced
layout stay open (Q293).
