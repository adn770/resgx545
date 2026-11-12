+++
id = "E865"
claim = "R5-render4x stages s0 and t (12 jobs, one attempt, no fault): s0's three controls passed as frozen (1x 1024 x 768 hash 0xc9e301d225fe2325, 4x 288 x 144 0x4a61860dcb4ab325, 4x 1024 x 768 0xde0b9233c9822325, 0 wrong pixels each); in stage t the controls passed (t6, E827's pb-e40-m2-64a with its hash; the unpoked 11.31 line and point t3b and t4b with their frozen heads), and with CR_TE_AA bit 29 clear the TA inserted one zero dword right before the object's format word: at dword 9 of the line and dword 11 of the point with 0x80000000 (t3c, t4c, held out) as with 0x40000000 (t3, t4, replicates of E847), and at dword 11 of the triangle on a context made for 4x targets with 0x40000000 and 0x80000000 (t1, t2, format word 0x00040101 at dword 12, empty image); the frozen verdict: the dword is zero and sits right before the format word, padding, not a field [infer] (6 of 6 rows decided)"
unit = "ta"
method = "R5-render4x stages s0 (3 controls, fault limit 1) and t (9 jobs, fault limit 1) of the question-closing pass, round 5 (decisions R5-3 a and the render plan's 5 a), dataset render-closing-r5-render4x, attempt out/20261112-100112 (s0 10:01:12, t 10:01:55 Mac time; driver log run-r5x.log), on the laptop (host cedar), 2026-11-12, kernel 7.3.0-resgx545, module srcversion 99CD90DA26E3AFF9C450517 (fork resgx545 a2788bd8, the rgn4 test kernel; installed = loaded, debugfs defaults checked at each stage start), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-rgn4 (sha256 e6951558a93b4b7bc750eeae302997992d7ec6e26719bc527ba1ffc9c6fb779a); s0 the three controls of E845 unchanged; t1 and t2 `tri --tri-full` at 64 x 64 with --aa4 and E824's words with cmd:1 = 0x40000000 or 0x80000000, t6 the same at one array (render_rgn_arrays 1, no --aa4), t3b, t3, t3c the 11.31 line (`probe --tri pixel` with p1131-green__0) and t4b, t4, t4c the 11.31 point (`probe --tri vtxuse` with p1131-psizes__1), t3/t4 with `--cmd 1=0x40000000`, t3c/t4c with 0x80000000, at render_rgn_arrays 1, all with --dump-render and --pixels where the probe takes them; a debugfs reset before each job, all 12 of class ok, health ok after each stage; the words, the insertion's place and value and the images frozen in predictions/t.tsv before the first job (FROZEN.sha256 e24977b3..., 297 files; PREDICTIONS.sha256 6c700fa8...; FROZEN.commits pins every resgx545 file the freeze names to a commit on main: FREEZE.txt names main 7a30713, a commit the lead later amended to f0d5b39, and the pinned files are the same at f0d5b39); the scorer finds a probe's dump by the verb of its argv (NAME.PROG.param.bin.gz), the fix of E847's slip, replayed on round 4's kept t files before the run; scored by the frozen score/score_r.py in the run (score-s0.txt, score-t.txt) and re-run on the kept files on 2026-11-12 with byte-identical output"
tiers = ["HW", "infer"]
date = "2026-11-12"
data = ["render-closing-r5-render4x:out/20261112-100112/s0/", "render-closing-r5-render4x:out/20261112-100112/t/", "render-closing-r5-render4x:postrun/"]
terms = ["CR_TE_AA", "Parameter Buffer (PB)", "PB_OBJ.FORMAT"]
+++
**What ran.** E728 and E829: with `CR_TE_AA` bit 29 clear and bit 30 or 31 set the TA inserts a
zero dword before the triangle object's format word and the 3D, reading the zero as the format word,
draws nothing. E847 read, after the run and under a closed gate (its scorer looked for the probe
rows' dumps under the wrong name), that 0x40000000 does the same to a line and a point object. Stage
t froze that reading as H-PAD (the inserted dword is zero and sits right before the format word),
against H-FIELD (non-zero), with the unpoked line and point as baselines in the same boot, E827's
row as the control, E847's four rows as replicates and the line and the point at 0x80000000, never
run, held out. s0 is the session's gate (E845's three controls).

**Frozen verdict (as printed).** s0: `controls {'s0-1x-1024x768': 'PASS', 's0-4x-288x144': 'PASS',
's0-4x-1024x768': 'PASS'}; later stages open`. t: `Q293: the dword CR_TE_AA bits 31:30 insert is
zero and sits right before the object's format word: at 0x80 on a line and a point (held out), at
0x40 and on a four-array context as E847 read them; padding, not a field [infer] (6 of 6 rows
decided)`.

**Results [HW].**

| job | set | object, `CR_TE_AA` | row (as printed, shortened) |
|---|---|---|---|
| t6-ctl-te40-1array | control | triangle, 0x40, one array | PASS, hash 0xfc5ff15e0434a325 |
| t3b-line-base | control | line, 0x20 | PASS (frozen head) |
| t4b-point-base | control | point, 0x20 | PASS (frozen head) |
| t1-aa4-te40 | replicate | triangle, 0x40, four arrays | dword 11 0, dword 12 0x00040101, empty |
| t2-aa4-te80 | replicate | triangle, 0x80, four arrays | dword 11 0, dword 12 0x00040101, empty |
| t3-line-te40 | replicate | line, 0x40 | one dword inserted at 9, 0x00000000 |
| t4-point-te40 | replicate | point, 0x40 | one dword inserted at 11, 0x00000000 |
| t3c-line-te80 | held out | line, 0x80 | one dword inserted at 9, 0x00000000 |
| t4c-point-te80 | held out | point, 0x80 | one dword inserted at 11, 0x00000000 |

t1 and t2's images are the background only (0 triangle, 4096 background); the four probe rows
returned rc 0. The s0 controls reproduced E845's hashes with 0 wrong pixels.

**What it shows.** [HW] With bit 29 clear and bit 30 or 31 set the TA inserts exactly one dword,
zero, right before the object's format word, for a triangle, a line and a point, at 0x80000000 as
at 0x40000000 (held out at 0x80 on the line and the point), and the same on a context made for 4x
targets as on one array. E847's post hoc reading now holds under a frozen scorer. [infer] The dword
is padding the TA writes in this configuration rather than a field of the object.

**What it does not show.** What the dword is for, or any setting under which the 3D reads the
displaced layout; 0xc0000000 on a line or a point, a non-zero value poked into the dword, and render
2's own object were not run. One object of each kind, one run each, one boot (Q293).
