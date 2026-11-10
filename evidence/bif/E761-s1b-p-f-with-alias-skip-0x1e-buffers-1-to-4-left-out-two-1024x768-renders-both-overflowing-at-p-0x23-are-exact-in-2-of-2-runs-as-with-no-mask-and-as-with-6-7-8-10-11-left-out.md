+++
id = "E761"
claim = "With the debugfs alias_skip mask 0x1e (buffers 1, 2, 3 and 4 left out of the client directory's alias together) two 1024x768 renders that both overflow the parameter buffer at render_pb_pages = 0x23 (`tri: 0 of 2 renders ok, 2 overflowed`) were exact in 2 of 2 runs (every diff 0 of 786432, the same two target hashes as the run with no mask), as were the same jobs with the mask 0xdc0 (buffers 6, 7, 8, 10, 11 left out) in 2 of 2 runs, and buffer 0 left out faulted at BIF fault 0x91000 at 0x3000b021 (the control, 1 of 1, as in S1 and E573); the frozen verdict: controls reproduce (f-ctl0, f-dpm-0); held out: f-dpm-1e exact 2 of 2; repeat only: f-dpm-dc0 exact 2 of 2"
unit = "bif"
method = "S1b stage p-f of the question-closing pass (6 jobs; paths relative to render/closing-s1b/ of the dataset: tri -n 2 --keep-going --wait-ms 6000 --width 1024 --height 768 --keep-overflow at render_pb_pages 0x23 with debugfs alias_skip 0x0 (f-dpm-0), 0x1e (f-dpm-1e, two runs), 0xdc0 (f-dpm-dc0, two runs), and tri -n 2 --keep-going --wait-ms 6000 with alias_skip 0x1 (f-ctl0, last); the mask written, read back and marked in the kernel log before each job (`resgx545 s1b readback NAME alias_skip=...`) and put back to 0 after it, a debugfs reset before each job), run 1794266690-29826 on 2026-11-10 00:24, a resumed attempt after the runner stopped the session at p-d (out-s1b.log, out-s1b-2.log), on the laptop (direct cable), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware (sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a), tool ~/sgxfive-test-s1b (sha256 46a2d06380814fdb07e7d711376f41fee4af8e6b3f75698d3e2ce52acfd6cc71), linux fork's debugfs alias_skip (commit 42); tables, predictions, scorer and runner frozen before the session (FROZEN.sha256, PREDICTIONS.sha256; verified before the stage and before scoring); verdict by the frozen score/score_s1.py p-f (out/score-p-f.txt, reproduced on the kept files)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-s1b:out/p-f/"]
terms = ["CR_BIF_DIR_LIST_BASE1", "ta3d_ctl", "CR_BIF_FAULT"]
+++
**What ran.** E745 (S1) left one case without a clean reading: its 1024x768 jobs under partial
renders were scored "split" by a pattern that did not match `tri: 0 of 2 renders ok, 2 overflowed`,
and its mask 0x1f contained buffer 0, whose own fault it reproduced. S1b ran the partial-render case
as a frozen row: HI (a buffer is needed only if leaving it out alone faults) against HJ (some pair
or set is needed together, so a mask of several buffers faults), with the mask 0x1e (buffers 1 to 4,
S1's 0x1f without buffer 0) as the held-out condition and 0xdc0 (S1's post-hoc exact job) as a
repeat. Controls: f-dpm-0 (no mask: both renders overflow and are exact, the reading the masks need)
and f-ctl0 (buffer 0 left out faults 0x91000: the knob bites), last.

**Frozen verdict.** controls reproduce (f-ctl0, f-dpm-0); held out: f-dpm-1e: exact 2 of 2; repeat
only: f-dpm-dc0: exact 2 of 2 (out/score-p-f.txt). The scorer's fixes since S1: a partial-render run
is exact when `tri: K of N renders ok, M overflowed` has K + M = N and every diff is 0, and two
faults read as HJ only when the mask contains buffer 0.

**Results [HW].** All five render jobs rc 0, class ok. Each printed `tri: 0 of 2 renders ok, 2
overflowed`, `scene overflowed the parameter buffer, context kept`, `diff: 0 of 786432 pixels` for
both renders, and the same two target hashes, 0xc9e301d225fe2325 and 0xed1bce7108aded25, as the
control f-dpm-0 (5 of 5 jobs identical); the alias_skip read-back marker was 0x0, 0x1e (twice) and
0xdc0 (twice) in the kernel log, each before its job. f-ctl0: rc 1, class fault, `BIF fault 0x91000
at 0x3000b021 (PD 0x9119000) stalls job 8832, recovering`, the registers after the reset `BIF_FAULT
0x0 EVENT_STATUS 0x20000000/0x400`; the health read after the stage shows render_pb_pages back at
0x422. The fault address is S1's (0x3000b021; E573 logged 0x3000b022).

**Read after the run [infer, not held out].** With P = 0x23 the two renders overflow the parameter
buffer and are rendered in partial passes (a job that overflows the parameter buffer and keeps its
scene); none of the buffers 1 to 4 together, and none of 6, 7, 8, 10 and 11 together, is needed in
the client directory for that case in the 1024x768 two-render job, as it was not for the complete
renders of E745. HJ (a set needed together) is not supported for these masks. The overflow shows
the knob P took effect (the jobs overflowed as the control did); the scorer does not read P back,
the markers name the value written.

**Caveats.** The conditions are one scene (1024x768, two renders, both overflowing at 0x23); the
partial renders are those of a render context that keeps its scene on overflow (--keep-overflow),
not a DPM reload under memory pressure of a different kind. The mask 0x1e is held out only as a
frozen row of S1b: S1's near-identical job (0x1f) was dominated by buffer 0. f-dpm-dc0 is a repeat
of S1's post-hoc exact job, so it reproduces and does not test.

**Not shown.** Pairs among the buffers 12 to 15 under partial renders; a buffer reassigned within a
job; which list each requestor walks; what the TA, 3D and EDM requestors do when their list is given
to another directory while the job runs; masks other than those, and other scenes.
