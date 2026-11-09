+++
id = "E745"
claim = "With the TA3D control block kept and buffers left out of the client directory's alias by alias_skip, leaving out the pairs {1,2}, {1,3}, {2,3}, {4,5} or {1,5}, or buffers 1 to 5 together, kept two-render jobs exact (2 of 2 runs each, 12 of 12), and leaving out 6, 7, 8, 10 and 11 kept a three-render job exact (2 of 2), while buffer 0 left out faulted 0x91000 at 0x3000b021 (2 of 2, the control: E573's status, which logged 0x3000b022): the frozen held-out verdict is that no pair among those is needed together (HJ refuted for them, HI holds); the 1024x768 partial-render jobs are labelled split and HJ by the frozen scorer, which read after the run are a regex miss (both runs exact, identical hashes, with both renders of each run overflowed) and a mask that included buffer 0 (its fault is buffer 0's)"
unit = "bif"
method = "S1 stage p-f (20 jobs, 10 conditions; paths relative to render/closing-s1/ of the dataset: tri -n 2 or -n 3, the debugfs knob alias_skip written, read back and marked in the kernel log before each job and put back to 0 after it, the two f-dpm jobs at 1024x768 with render_pb_pages 0x23 and --keep-overflow; the fault control f-ctl0 last), a debugfs reset before each job, on the laptop (direct cable), 2026-11-09, kernel 7.3.0-resgx545 (branch with alias_skip), module B21FDA82BD5E5CB5A627E3B, stock firmware, tool ~/sgxfive-test-s1 (sha256 d776afbc...); frozen before the stage; scored by the frozen score/score_s1.py p-f (out/score-p-f.txt); the partial-render jobs read after the run (analysis/pixel.md)"
tiers = ["HW", "infer"]
date = "2026-11-09"
data = ["render-closing-s1:out/p-f/"]
terms = ["CR_BIF_DIR_LIST_BASE1", "ta3d_ctl", "CR_BIF_FAULT"]
+++
**What ran.** E573 left out one buffer at a time: every one of 1 to 5 and 12 to 15 alone kept
renders exact, buffer 0 alone faulted. HI (a buffer is needed only if leaving it out alone faults)
against HJ (some pair is needed together: a pair left out faults). Held out: five pairs, 1 to 5
together, a three-render job without 6, 7, 8, 10 and 11, and two 1024x768 jobs with partial renders
(masks 0xdc0 and 0x1f). Control: buffer 0 left out must fault 0x91000 (E573), run last.

**Frozen verdict.** control reproduces E573; f-12, f-13, f-23, f-45, f-15, f-all15, f-3r: exact 2
of 2; f-dpm-dc0: split ['ok', 'ok'] (third run); f-dpm-1f: fault 0x91000 2 of 2 (needed: HJ)
(out/score-p-f.txt).

**Results [HW].** The 14 runs of the seven conditions: rc 0, `diff: 0` for every render, the
read-back marker of alias_skip in the kernel log for each. f-ctl0: `BIF fault 0x91000 at
0x3000b021`, recovered, 2 of 2 (E573 logged the same status at 0x3000b022, one byte higher; the
scorer compared the status only). f-dpm-dc0: both runs overflowed by design (P = 0x23), every render
`diff: 0 of 786432 pixels`, the same two target hashes in both runs. f-dpm-1f: the fault of f-ctl0,
word and address, 2 of 2.

**Read after the run [infer].** The f-dpm-dc0 label: the scorer calls a run exact only on `tri: N
renders ok`, the tool prints `tri: 0 of 2 renders ok, 2 overflowed` under --keep-overflow, and two
equal "ok" results fall to the split branch; the data are exact 2 of 2 under partial renders. The
f-dpm-1f label: mask 0x1f includes buffer 0, so its fault is buffer 0's and says nothing about a
pair among 1 to 4; the scorer labels any two faults HJ. Neither is held out.

**Not shown.** The partial-render case as a frozen result, a buffer reassigned within a job, which
list each requestor walks, pairs among 12 to 15.
