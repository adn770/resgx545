+++
id = "E888"
claim = "R6-render4x set A, stage t (4 jobs, one attempt, no fault): Q293's held-out rows, 3 of 3 decided, the control passing (t8, E827's pb-e40-m2-64a with its hash): with CR_TE_AA 0xc0000000 the TA inserts one zero dword right before the format word of the 11.31 line (dword 9) and point (dword 11) and the image is empty, as with 0x40000000 and 0x80000000 (H-PAD); on the 0x40000000 triangle the kernel's poke of 0x00000001 into the inserted dword 11 of render 2 landed (the format word 0x00040101 at dword 12) and render 2 drew nothing, 0 triangle and 4096 background pixels: the 3D reads the poked value as the format word (H-OLD, as E829's 0xffffffff)"
unit = "ta"
method = "R6-render4x set A, stage t (4 jobs, fault limit 1) of the question-closing pass, round 6 (decision R6-6 a; plan closing6/render4x/exp-render4x-r6.md section 5, Q293 as reworded on main), dataset render-closing-r6-render4x, attempt out/20261112-144822 (stage t 14:51:39 Mac time, after s0 and a; driver log run-r6x-A.log), on the laptop (host cedar), 2026-11-12, the boot, kernel, module (srcversion 99CD90DA26E3AFF9C450517), firmware and tool (sha256 e6951558...) of E887; t5 the 11.31 line (`probe --tri pixel` with p1131-green__0) and t6 the 11.31 point (`probe --tri vtxuse` with p1131-psizes__1) with `--cmd 1=0xc0000000`, t7 `tri --tri-full -n 2 --geometry 1` at 64 x 64 with E824's words, cmd:1=0x40000000 and `--kpoke-render 2:par:11=0x00000001`, t8 E827's row (one array), all at render_rgn_arrays 1 with --dump-render; a debugfs reset before each job, all 4 of class ok, health ok at the stage's end; the insertion's place and value, the images and t7's poke frozen in predictions/t.tsv before the first job (t5, t6 compared with the frozen heads of the kept 11.31 dumps, which r5's in-session baselines equalled, E865; t7 has no in-session own11 control), with the freeze of E887 (FROZEN.sha256 5fbd64f7..., PREDICTIONS.sha256 15e50eda...); the stage ran last of set A so that a stop on t7's new poke value could not cost stage a; scored by the frozen score/score_r.py in the run (score-t.txt) and re-run on the kept files on 2026-11-12 with byte-identical output"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-render4x:out/20261112-144822/t/", "render-closing-r6-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "PB_OBJ.FORMAT"]
+++
**What ran.** E728, E829, E847 and E865: with `CR_TE_AA` bit 29 clear and bit 30 or 31 set the TA
inserts one zero dword right before the object's format word, for a triangle, a line and a point,
and the 3D reads that zero as the format word and draws nothing. Q293, reworded to its bounded
items, kept three: 0xc0000000 on a line and a point (both bits), a non-zero value poked into the
inserted dword, and render 2's own object. The plan's four rows ran the first two; render 2's own
object was not among them.

**Frozen verdict (as printed).** `Q293: CR_TE_AA 0xc0000000 inserts one zero dword right before the
format word of a line and a point and draws nothing, as 0x40 and 0x80 do; a non-zero value poked
into the inserted dword of the triangle draws nothing (read as the format word) (3 of 3 rows
decided)`.

**Results [HW].**

| job | set | object, `CR_TE_AA` | row (as printed, shortened) |
|---|---|---|---|
| t8-ctl-te40-1array | control | triangle, 0x40, one array | PASS, hash 0xfc5ff15e0434a325 |
| t5-line-tec0 | held out | line, 0xc0 | one dword inserted at 9, 0x00000000, image empty |
| t6-point-tec0 | held out | point, 0xc0 | one dword inserted at 11, 0x00000000, image empty |
| t7-tri-te40-poke11 | held out | triangle, 0x40, dword 11 poked | dword 11 0x00000001 (applied), dword 12 0x00040101, render 2: 0 triangle, 4096 background |

**What it shows.** [HW] Bits 31 and 30 together give the insertion each gives alone: one zero
dword right before the format word, for a line and a point object, and an empty image. The 3D
reads the dword at the format word's place whatever it holds: a small non-zero value (0x00000001)
draws nothing, as 0xffffffff did in E829. [infer] The dword is padding the TA writes in this
configuration, and the 3D reads the object in the bit-29-set layout.

**What it does not show.** Render 2's own object (what the TA writes for the second render and how
it is read: not run; Q293); a poked value other than 0x00000001 and 0xffffffff, or one that is a
valid format word other than the twin's (E829 poked the twin's words); one run each, one boot.
