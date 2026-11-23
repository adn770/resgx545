+++
id = "E1178"
claim = "r41-n3f-lc2 stage lc (row LC rerun with control E0 read in job 1's record, module 83FBFD86, fork 423b436e7f80, emitsb_sbc43s, image land at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): job 1 done, then BIF_FAULT 0x0000000f (list 15, page 0) in snap9, the tick stopped and job 2 (command 6) was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3F-LC RULE: LC-EARLY', the prediction held, PG, E0, T0 and J1 passed, B read by LC-EARLY; LC-FILL, LC-FILLOK and LC-HEAL cannot tell, LC-REBASE not reached; the printed survey reads post sa0 0, sa1 0x04400000, sa2 0x01030b00, sa12-sa27 = pa0-pa15; that the copy came before the stop is inferred"
unit = "edm"
method = "r41-n3f-lc2 (render/closing-r41-n3f-lc2), stage lc of the question-closing pass (round 41: row LC, closing29/n3f/design.md section 3.4, a rerun of r41-n3f-h3 (E1176) whose control E0 is read in job 1's record (its slot and cmd_after, as the runner read them when job 1 ended, before job 2 was posted) and not on the page after the row, every other prediction and control H3's; flagged class, the user present with a reset ready; the user's OK for the rerun), dataset render-closing-r41-n3f-lc2; attempt out/20261121-073816 (07:38:16, 2026-11-21; stage lc exited 4 at its one row, a runner stop, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest), the one-shot boot of 2026-11-19, no rebuild and no boot in round 41; stock firmware), the kit's owntask job kind with a job list per row (kit/ = resgx545 0cfe29a7, branch r41-lc2: r41-n3f e516a7aa plus the fake runner posting each job, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, H3's bytes; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=sbc43` after the stage's reset and health pair, then one row of three jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on the next tick pass, and command 6 again after `sleep_ms` 2000; the results page, the registers (snap0, snap9, the runner stop dump) kept; the round's three after-read blobs accepted by the module's verifier unchanged: the fork's KUnit suite at 423b436e7f80 on the Mac shim with a suite of their own, 43 of 43 (closing29/r41-n3f-logs/shim-r41.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 ec3ec7c749dc1d52091ddf886ba261a093f3ddba56bb97196186a81ec4b10f58 (87 files), PREDICTIONS.sha256 5003dc39e29fa45bcb18569d786b4f6198d372890bcea8134cda0729bd2bc604 (1 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at 0cfe29a7; r35-sa's and r40-n3e's kept files at data b5b95bff; t30's source 42c4de7); the frozen predictions predictions/lc.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-lc-20261121-073816.out); the SURVEY, JOB and GATE lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-21"
data = ["render-closing-r41-n3f-lc2:out/20261121-073816/lc/", "render-closing-r41-n3f-lc2:fold/"]
terms = []
+++
**What ran.** H3's row LC again (E1176): sideband 0xc43 with the land image (E1163's image: `douta`
of markers to attributes 24 and 26, the timer left running, no V0 or V2), three jobs: the emit
(command 1), the after-read (command 6) on the next tick pass and again 2 s later, then the gate.
Only control E0 changed: H3 read it on the page after the row, where job 2's posted and unserved
command 6 made it fail; LC2 reads job 1's own record (slot 1 and cmd_after), as the runner read it
when job 1 ended. The question: does bit 10's state heal on later stock passes, and is the timer
stop of crumb3 needed for the fill to fail.

**Frozen verdict (as printed).** The stage stopped, so the frozen scorer was run by hand on the kept
directory:

```
SUMMARY: lc: controls: lc1-a:B: FAILED
Q128-N3F-LC RULE: LC-EARLY
PREDICTION LC-EARLY: predicted held, read held: held
PREDICTION LC-REBASE: predicted held if not LC-EARLY, read FAILED: not reached (LC-EARLY)
```

PG, E0, T0 and J1 passed. Control B (BIF_FAULT 0 after the row) failed and is read by LC-EARLY,
which names the fault, as the frozen rule says. LC-FILL, LC-FILLOK and LC-HEAL read cannot tell: no
after-read and no gate ran. LC-EARLY held; the others were not reached.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, S1 and M4 with run id 1, cmd_after 0, 10 ticks.
- snap9 and the stop dump: BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0000000f (list 15, page 0); the tick
  stopped (the runner's alive check: the tick count 2159 three times, not advancing); job 2 not done
  (cmd_after 6, dwords 224-255 still 0xdeadc0de); no gate ran. The kit's reset and health recovered
  it (closing29/r41-lc2-logs/health-r41-n3f-lc2.log).

**Readings [HW], printed, not scored.** The survey's post words are what the started entry read in
job 1, not an after-read of the EDM's own bank (job 2 never ran):

- post sa0 0x32004000 -> 0x00000000, sa1 0x32005000 -> 0x04400000, sa2 0x32002000 -> 0x01030b00 (H3:
  0x0104b95b), sa3-sa10 as H3's;
- sa12-sa27 equal to the started entry's pa0-pa15: sa12 = pa0 = 0x00000003, sa13 = pa1 = 0x00043000,
  sa16 = pa4 = 0x32411000 (H3: 0x32004000), pa12 and pa14 0x5a5a3a18 and 0x5a5a3a1a, land's markers.

**What it shows.** LC-EARLY, the design's prediction (a): with the land image, which writes no V0 or
V2 and leaves the timer running, the EDM stopped after the emit's pass with a fault at page 0
through its list (CID 15), before any later job was served **[HW]**. So whether bit 10's rewrite
heals on later stock passes cannot be read with land: the EDM does not survive to a second job. The
post readings repeat H3's pattern, sa12-sa27 = pa0-pa15, sa0 0 and sa2 neither its pre value nor
H3's.

**What it does not show.** That the copy into sa12-sa27 happened before the early stop, and that
0x00043000 in sa13 comes from pa1 in this run, are **[infer]**: the post words are the started
entry's view, and round 41's fold found that the started entry's pa can hold words of earlier rows
across resets (E1177: land's markers in pa12 and pa14 after H3), so a post pa may be stale. Which
pointer faulted at page 0 (a stale sa0 or sa2 is not read); why sa0 became 0 and sa2 0x01030b00;
whether the fill fails with the timer running; the sa past sa31.

**H3 under this scorer (information).** H3's kept stage, copied into the session's tests/h3/ and
rescored with this scorer, reads E0 PASS and LC-EARLY too
(closing29/r41-lc2-logs/rescore-h3-under-lc2.txt); H3's frozen verdict stays CANNOT TELL (E1176).

**Correction 2026-11-23:** Which pointer faults with land: row LV of round 42 (E1183), land with V0
and V2, stopped early too, at page 0x04400000, the post sa1, with sa0 = V0 and sa2 = V2 **[HW]**: V0
and V2 do not prevent the early stop. This record's page 0 fits a stop through sa0 = 0, and LV's
through sa1, the next one: that the early stop follows a pointer through the first secondaries is
**[infer]**. The 0x00043000 in this record's sa13 was a stale word of attribute 13 that none of our
rows wrote (E1179-E1181) **[HW]**. This record's verdict and readings stand.

**Correction 2026-11-23:** Row V of round 43 (E1185), landv with M1 planted in attribute 1, stopped
early at the page in sa1 (0x005d1000), as LV (E1183) at its sa1 **[HW]**: with landv the early stop
follows sa1. This record's printed sa1 was 0x04400000 too, yet it faulted at page 0: if that word is
what the pass read (the record infers that the copy came before the stop), land's early stop does
not follow sa1. Why it faults at page 0 is not explained; a stop through sa0 = 0 stays **[infer]**.
This record's verdict and readings stand.
