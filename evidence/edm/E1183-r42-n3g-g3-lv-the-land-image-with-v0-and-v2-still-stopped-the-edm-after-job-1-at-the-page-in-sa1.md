+++
id = "E1183"
claim = "r42-n3g-g3 stage lv (row LV, module 079DD0D1, fork ec6511d5de87, emitsb_sbc43s, image landv at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): LC2's row (E1178) with V0 and V2 sent to attributes 0 and 2: job 1 done with post sa0 = V0 and sa2 = V2, then, before job 2 was posted, BIF_FAULT 0x0440000f (list 15, page 0x04400000, the post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3G-LV RULE: LV-EARLY, LV-V', LV-V held as predicted, LV-EARLY held against its prediction; LV-REBASE, LV-FILL and LV-HEAL not reached, LV-FILLOK cannot tell: V0 and V2 do not prevent the early stop"
unit = "edm"
method = "r42-n3g-g3 (render/closing-r42-n3g-g3), stage lv of the question-closing pass (round 42: row LV, closing29/n3g/design.md section 3.5; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-21), dataset render-closing-r42-n3g-g3; attempt out/20261122-163956 (16:39:56; stage lv exited 4 at its one row, a runner stop, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest, closing29/r42-n3g-logs/cachix-wait.log), the one-shot boot of 2026-11-22; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 c0e2dc36, branch r42-n3g, its fwtask_run.py byte for byte): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad, asm/fwtask/fwtask.map at c0e2dc36; emitsb14s with only the emit word changed, emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=landv pdsat=fw14 form=sbc43` after the stage's reset and health pair, then one row of three jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on the next tick pass, and command 6 again after `sleep_ms` 2000; the results page, the registers (snap0, snap9, the runner stop dump) and the record kept; the round's blobs and arm lines accepted by the module's verifier unchanged: the fork's KUnit suite at ec6511d5de87 on the Mac shim with a suite of their own, 48 of 48 (closing29/r42-n3g-logs/shim-r42.log; r42-red 46 of 48, shim-r42-red.log; a wrong form fails, shim-r42-neg.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 6d30cf0a190fc4af44f15edf964aa1a6a715f0016e8d7d5d52b90cdacd6b820d (81 files), PREDICTIONS.sha256 c2e7ae3daf739e1ef02924b0f0b2225e5abee82a25162150df256cab6b09a369 (1 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at c0e2dc36; r35-sa's and round 41's kept files at data 5e9c84b2; t30's source 42c4de7); the frozen predictions predictions/lv.tsv, the rule score/score.py, run by hand on the kept directory (fold/reproduce-lv-20261122-163956.out); the SURVEY, JOB, BIF, GATE and RBOOT lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-22"
data = ["render-closing-r42-n3g-g3:out/20261122-163956/lv/", "render-closing-r42-n3g-g3:fold/"]
terms = []
+++
**What ran.** LC2's row (E1178: sideband 0xc43, three jobs, the timer left running) with a new
image, landv: land plus two `douta` of V0 and V2 to attributes 0 and 2, so that the started entry's
sa0 and sa2 (0 and 0x01030b00 in LC2) hold the TA3DCtl and CCB control words again. Run last, after
rows M, S and Q, so attribute 13 held M13. The question: does the early stop of LC come through sa0
or sa2, and if the EDM survives, does the rewrite heal on later stock passes?

**Frozen verdict (as printed).** The stage stopped, so the frozen scorer was run by hand on the kept
directory:

```
SUMMARY: lv: controls: lv1-a:B: FAILED; lv1-a:J2: FAILED
Q128-N3G-LV RULE: LV-EARLY, LV-V
PREDICTION LV-EARLY: predicted failed, read held: FAILED
PREDICTION LV-EARLY0: predicted failed, read FAILED: held
PREDICTION LV-V: predicted held, read held: held
```

PG, E0, T0 and J1 passed; B (BIF_FAULT 0 after the row) and J2 (job 2 done) failed, read by
LV-EARLY, which names the stop. LV-V held as predicted; LV-EARLY held, the design's weak prediction
(failed) failing; LV-EARLY0 (a stop at page 0) failed as predicted. LV-REBASE, LV-FILL and LV-HEAL
were not reached; LV-FILLOK cannot tell.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 8 ticks; K5 BIF_FAULT 0 before and after.
- Job 2's K5 pre read BIF_INT_STAT 0x000d0400, BIF_FAULT 0x0440000f (list 15, page 0x04400000)
  already; the tick stopped (the runner's alive check); job 2 not done (cmd_after 6, dwords 224-255
  still 0xdeadc0de); no gate ran. The kit's reset and health recovered it
  (closing29/r42-n3g-logs/health-r42-n3g-g3.log).

**Readings [HW], printed, not scored.** The post words are what the started entry read in job 1: sa0
= V0 0x32004000 and sa2 = V2 0x32002000 (their pre values), sa1 0x04400000, the fault page;
sa12-sa27 = pa0-pa15, sa13 = pa1 = M13 0x005d3000; pa12 and pa14 landv's markers 0x5a5a3a18 and
0x5a5a3a1a.

**What it shows.** With sa0 and sa2 restored the EDM still stops after the emit's pass, before any
later job is served, with a fault through its list **[HW]**: V0 and V2 do not prevent the early
stop. The fault came on a stock pass between job 1's end and job 2's post, at the page equal to the
post sa1 **[HW]**. LC (E1176, E1178) faulted at page 0 with sa0 0; LV at sa1's word with sa0 valid:
that the early stop follows a pointer through the first secondaries, faulting at the first unmapped
one, is **[infer]**. Whether bit 10's rewrite heals on stock passes is still not readable from our
task: with the tick running the EDM stops first.

**What it does not show.** Which access faulted; why sa1 holds 0x04400000; whether a valid sa1 would
let the EDM survive; whether the fill fails with the timer running; one run.
