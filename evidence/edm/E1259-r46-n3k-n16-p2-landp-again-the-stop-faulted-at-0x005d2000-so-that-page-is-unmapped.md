+++
id = "E1259"
claim = "r46-n3k-n16 stage p2 (row P2, module 10BBF3BF, fork c5094783eb88, emitsb_sbc43s, image landp at fw14, form=sbc43, sideband 0xc43, s2 0, flagged, user present): after the plant W16 (E1258) and no draws: landp wrote V0 to attribute 0 and 0x005d2000 to attribute 1; job 1 done with post sa0 = V0 0x32004000, sa1 0x005d2000, sa2 = V2 0x32002000, sa12 = V0, sa13 = M13; then, before job 2 was served, BIF_FAULT 0x005d200f (list 15, page 0x005d2000; the scorer: job 1's post sa1), the tick stopped and job 2 was never served; the runner stopped (class hang, rc 4) and the kit's reset recovered it; 'Q128-N3K-P2 RULE: P2-E12, P2-UNMAP, P2-WRITE'; every prediction held (P2-MAPPED and P2-SUM failed as predicted, P2-OTHER (printed) read failed): with V0 in sa0 the stop faulted at 0x005d2000, so that page is unmapped where the stop reads it, P's read and stop (E1255) a second time"
unit = "edm"
method = "r46-n3k-n16 (render/closing-r46-n3k-n16), stage p2 of the question-closing pass (round 46's addendum: row P2, closing29/n3k/design.md section 4.9 and 11.4; flagged class, the user present with a reset ready; the user's decisions of the design, section 11.9: G=a, H=a, I=a, J=a, K=a; run after section 11.8's stop for the user (LFK and LFK2 disagreed), the user choosing N13-N16 and skipping N12), dataset render-closing-r46-n3k-n16; attempt out/20261126-080355 (08:04:16; stage p2 exited 4 at its one row, the runner's stop the design planned, so the driver did not score it); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 and of its addendum on that one boot, no rebuild, install or boot since N4, post sa12 = V0 in every row of the addendum (the outcome E12); stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK), K10's arm words pds=landr and pds=landp and K11's PAD control, armed in N12 only, which did not run (kit/ = resgx545 b4e31c76, branch r46-n3k2 on r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sbc43s.blob (asm/fwtask/emitsb_sbc43s.s, sha256 987b0e4e1dc0ba9ec6e2583bb0edd77afef230d7121070daa18a8171dd4a86ad; emit word 0xfb20b18800c08184, sideband 0xc43) armed once with own_arm `slots=0x1 entry=0 pds=landp pdsat=fw14 form=sbc43` after the stage's reset and its begin health (begin_draws none), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on the next tick pass (no kick); the results page, the registers (snap0, snap9, the runner's stop dump) and the record kept; the blob and form of rounds 42-46 and the mark, land, landr and landp images of the running module (round 46's build, E1234-E1245); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 de917b873928dca0894e4254be31e873d5853940dcfd845d157b7c7f9d116929 (144 lines), PREDICTIONS.sha256 0fa7de8bf45b5ce6723fa338a5cb2238e25d3bcf55283fced589ae5249ae9196 (2 files), pins in FROZEN.commits (the kit and the blob sources at b4e31c76; round 45's kept stages of r45-n3j-n2 to -n6, the scorer's fixtures, at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/p2.tsv, the rule score/score.py, scored after the session (closing29/r46-n3k-logs/score-r46-n3k-n16-p2.txt) and again by hand on the kept directory (fold/reproduce-p2-20261126-080355.out), the same bytes; the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-26"
data = ["render-closing-r46-n3k-n16:out/20261126-080355/p2/", "render-closing-r46-n3k-n16:fold/"]
terms = []
+++
**What ran.** landp (landv with Mb changed to Q0 0x005d2000 and its control to attribute 1's: the
kernel's V0 and V2 to attributes 0 and 2, Ma to attribute 24, Q0 to attribute 1, then landv's
`doutu` and `halt`; no `tim`, so the tick runs) right after the plant W16 (E1258), with `begin_draws
= "none"`: between the plant's emit and the image's ran the plant's disarm and exit resets, this
stage's begin reset with the register health (no draw) and the arm [HW, the stages' kernel logs; DR
and DK read ok, printed: KC begin delta 2]. Jobs: LM's two (E1198): job 1 the emit on the tick pass,
job 2 command 6 on the next tick pass. The question: row P again (decision J (a)), byte for byte but
its names: with V0, a mapped page (LV, V and LM ran with it in sa0, E1183, E1185, E1198), in sa0 and
Q0 0x005d2000 in sa1, is 0x005d2000 unmapped where the stop reads it (P-UNMAP) or not (P-MAPPED),
and does the stop fault at V0 + V0 = 0x64008000 (P-SUM: C-E0+)?

**Frozen verdict (as printed).** The stage stopped, so the driver did not score it; the frozen
scorer was run after the session (closing29/r46-n3k-logs/score-r46-n3k-n16-p2.txt) and again by hand
on the kept directory, the same bytes:

```
SUMMARY: p2: controls: p21-a:B: FAILED; p21-a:J2: FAILED
Q128-N3K-P2 RULE: P2-E12, P2-UNMAP, P2-WRITE
PREDICTION P2-E12: predicted held, read held: held
PREDICTION P2-MAPPED: predicted failed, read FAILED: held
PREDICTION P2-OTHER: predicted printed, read FAILED: printed
PREDICTION P2-SUM: predicted failed, read FAILED: held
PREDICTION P2-UNMAP: predicted held, read held: held
PREDICTION P2-WRITE: predicted held, read held: held
```

PG, E0, T0, J1 and SV passed, PLANT (W-SA1 of stage w16) too, printed only (landp writes sa0 and sa1
itself); DR and DK read ok (printed in the ROW line); B (BIF_FAULT 0 after the row) and J2 (job 2
done) failed, read by P2-UNMAP, P2-MAPPED and P2-SUM (the outcomes that name the stop). Every
prediction held: P2-WRITE, P2-UNMAP and P2-E12 held; P2-MAPPED and P2-SUM failed as predicted;
P2-OTHER (printed) read failed.

**Results [HW].**

- Job 1 done: X0 0x5a5a3303, run id 1, cmd_after 0, 9 ticks; K5 BIF_FAULT 0 before and after.
- Job 1's post sa0 = V0 0x32004000, sa1 0x005d2000, sa2 = V2 0x32002000 (landp's, sa02kind ONE),
  sa12 = pa0 = V0, sa13 = pa1 = M13, sa24 = pa12 Ma and sa26 = pa14 Mb; the other post sa3-sa31 and
  pa equal W16's word for word.
- Job 2's K5 pre already BIF_INT_STAT 0x000d0400, BIF_FAULT **0x005d200f** (list 15, page
  0x005d2000; the scorer: job 1's post sa1), post the same; job 2 not done; the tick stopped; snap9
  and the stop dump the same fault. The kit's reset and both draws recovered it (health ok,
  closing29/r46-n3k-logs/health-r46-n3k-n16.log).
- The kernel: the arm with no draws "0 events seen"; KC begin N0 532, delta 2; the end KC cannot
  tell.

**What it shows.** Row P's read and stop came back in a session of their own: with V0 in sa0 the
stop faulted at 0x005d2000 in sa1 **[HW, P E1255 and P2]**: 0x005d2000 is unmapped where the stop
reads it, two reads agreeing and none disagreeing.

**What it does not show.** Which access of the tick pass read 0x005d2000; one run of this stage.
