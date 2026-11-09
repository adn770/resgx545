+++
id = "E734"
claim = "Below P = 0x422 the render_pb_pages knob takes effect (the job's own threshold register 0x0624 read P - 0x22 at P = 0x200, 0x300, 0x3e0, 0x400, 0x410 and 0x420, 15 jobs, and 0x400, the clamp, at 0x422 in the other 7), and at 4096x4096 the threshold was raised by 0x20 (TA3DCtl dwords 37 and 38 = 1 << 16 | thr0 and 0x20, the second abort at thr0 + 0x20) in exactly 2 of 22 jobs, 1350 vertices at P = 0x300 and 900 at 0x200, and in none of the 20 other jobs at P = 0x3e0 to 0x422, in 19 of which the second run reached thr0 (1500 vertices at 0x3e0 twice, 0x400, 0x410, 0x420 and 0x422; 1350 at 0x3e0; 1380 to 1497 at 0x3e0 and 0x422; the 20th, 1350 at 0x420, took one partial render and is void for the raise); the frozen scorer's verdict is METHOD BROKEN, nothing concluded, because the job that the design used as a positive control, 1350 vertices at 0x3e0, was predicted to raise by every frozen hypothesis and did not; dword 36 read 2 at 1350 vertices (at 0x3e0, 0x420 and 0x300) and 3 at 1380 to 1500 (at 0x3e0 and 0x422, 1500 also at 0x400 to 0x420)"
unit = "dpm"
method = "S1 stage g-e1 of the question-closing pass (22 jobs, one condition each but one repeat; paths below are relative to render/closing-s1/ of the dataset: probe --tri pixel --width 4096 --height 4096 --vertices V --dump-render with the plain green pixel program, render_pb_pages written, read back and marked before each job, a debugfs reset before each, regtimeline over 0x0624-0x0628, 0x0654-0x0660, 0x0700-0x0710, 0x0720-0x0724 and 0x0748, read-only), on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1 (sha256 d776afbcb9f26a3fccc8dc6be5fa513f8843a0b2185e78c66d2c4737ade0714e), regtimeline sha256 079f6359...; tables, predictions, scorer and runner frozen before the stage (FROZEN.sha256, PREDICTIONS.sha256; run/freeze_s1.sh verify passed before the stage and before scoring, attested by file times and hashes only); scored by the frozen score/score_s1.py g-e1 (out/score-g-e1.txt); the per-job dwords, peaks and the post-hoc readings by analysis/scripts/geo_e1_dwords.py, written after the run"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/g-e1/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** E704 left one scene against the raise rule R2 (E625, E630): 1500 vertices at
4096x4096 does not raise at P = 0x422, where the knob clamps. S1's g-e1 ran it below the clamp
(P = 0x3e0 twice, 0x400, 0x410, 0x420), E704's job as the control, ladders of 1380 to 1497 vertices
at 0x3e0 and 0x422, and three jobs of the design's positive controls (1350 at 0x3e0 and 0x300, 900
at 0x200), with 1350 at 0x420 expected void for the raise (one partial render). Frozen hypotheses:
HC (a ceiling at status 0x400: 1500 raises at 0x3e0 and not at 0x410 or above), HA (dword 36 = 3
blocks the raise, 2 or less raises at every P), HS (the 1500 scene never raises, for another
reason), R2 (a raise in every cell whose second run reaches thr0).

**Frozen verdict.** METHOD BROKEN: positive control p-1350-0x3e0 reaches thr0 and does not raise;
nothing is concluded (out/score-g-e1.txt). The scorer stops there, as the proposal's decision text
says it must.

**Results [HW].** Every job ran (rc 3, overflow, context kept; no hang, no fault). The knob proof
held in 22 of 22: the job's own 0x0624 equals P - 0x22 (0x1de, 0x2de, 0x3be, 0x3de, 0x3ee, 0x3fe;
0x400 at 0x422). The control equals E704 word for word (peaks 0x400, 0x400, 0x11c; dwords 35 to 39
0x3fe, 3, 0, 0, 6). Raised: 1350 at 0x300 (abort statuses 0x2de, 0x2fe; dwords 35, 37, 38 = 0x2fc,
0x102de, 0x20) and 900 at 0x200 (0x1de, 0x1fe, 0x1fe, three partial renders; 0x1fc, 0x101de, 0x20).
Not raised, with a second run that reached thr0 (19 jobs): 1500 at 0x3e0 (2 of 2), 0x400, 0x410,
0x420, 0x422; 1350 at 0x3e0 (dword 36 = 2); the twelve ladder jobs. 1350 at 0x420 took one partial
render (void for the raise, as declared). Dword 35 is thr0 - 2 in every non-raising job. Dword 36: 1
at 900 vertices, 2 at 1350 (at 0x3e0, 0x420 and 0x300), 3 at 1380 to 1500 (at 0x3e0 and 0x422, 1500
also at 0x400 to 0x420); at 0x3e0 both 1350 and 1380 take two partial renders.

**Why the control failed.** The hardware, not the scorer: the method reads the raise correctly in
the two jobs that raised, and the job that did not raise had a second run reaching thr0. The design
had made a held-out prediction (1350 raises at 0x3e0, every hypothesis's `yes`, set `heldout` in
the predictions) a condition of the method. The failure is itself the observation that a scene
with dword 36 = 2 and a reaching second run does not raise at thr0 = 0x3be, against HA, HS, R2 and
HC as worded (0x3be + 0x20 is under 0x400).

**Post hoc (read after the run; not held out).** [infer] The raise was seen at thr0 0x1de and 0x2de
and, of the 19 jobs whose second run reached thr0, at no thr0 from 0x3be up, at 900, 1350 (on both
sides) and 1380 to 1500 vertices: a limit on the raised threshold between 0x2fe and 0x3dd fits all
22 jobs (the 1350 job at 0x420 is void), and so does any rule in P that the vertex count does not
enter. E625's rule (raise iff 2 * thr0 < U + k) predicts a raise for 1350 at 0x3e0 when U is read as
the summed run peaks (2005 pages against 2 * 0x3be = 1916). The dword-36 step lies between 1350 and
1380 vertices (both at P = 0x3e0, where both take 2 partial renders) and, at 0x3e0, is not the step
of the partial-render count. A frozen run that confirms needs P between 0x300 and 0x3e0 (0x320 to
0x3c0) for two scene sizes, with the step P predicted equal for both.

**Not shown.** What the raise compares, why 0x20, whether the limit is the hardware's or the
firmware's, and what dword 36 or dword 39 (5 at 0x3e0 and in 1350 at 0x420, 6 in the other jobs)
count.