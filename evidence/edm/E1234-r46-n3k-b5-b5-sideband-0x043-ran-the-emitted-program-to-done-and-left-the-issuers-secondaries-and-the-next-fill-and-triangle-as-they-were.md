+++
id = "E1234"
claim = "r46-n3k-b5 stage b5 (row B5, module 10BBF3BF, fork c5094783eb88, emitsb_sb043s, image crumb3 at fw14, form=sb043, sideband 0x043, s2 0, flagged, user present): crumb3 emitted with sideband 0x043 ran to done (S1, M4 with run id 1, state 2), post sa0-sa31 = pre, job 2's after-read on a kick = pre = post, the gate's fill and triangle exact, K5 BIF_FAULT 0 before and after each job and in snap9; every control passed, 'Q128-N3K-B5 RULE: B5-DONE, B5-GATE, B5-HID, B5-QUIET, B5-RUN, B5-SAME', every prediction held; landing (printed) NONE"
unit = "edm"
method = "r46-n3k-b5 (render/closing-r46-n3k-b5), stage b5 of the question-closing pass (round 46: row B5, closing29/n3k/design.md section 10.1; flagged class, the user present with a reset ready; the user's decisions of the design, section 10: A=a, B=b, C=a, D=a, E=a, F=b), dataset render-closing-r46-n3k-b5; attempt out/20261125-150329 (15:03:30; stage b5 ended rc 0 and the driver scored it, score-b5.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 on that one boot; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and K10's arm words pds=landr and pds=landp, which no stage of these sessions used (kit/ = resgx545 eaee04a4, branch r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sb043s.blob (asm/fwtask/emitsb_sb043s.s at eaee04a4, sha256 1d2be92bce7ee0c05a4705d9df412b30d75780530b93262e6d38e72ff6568d99; emitsb_sbc43s with only the emit's sideband changed, 0x043) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb043` after the stage's reset and its begin health (fill and triangle), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on a GETMISCINFO kick; then the gate (on_gate_fail score: the fill and triangle read by the outcomes); the results page, the registers (snap0, snap9) and the record kept; crumb3's bytes unchanged since round 40 (E1161-E1172); both sidebands on the module's list since round 40; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 cf818b8f70a1a13b73df30397161ef48c61f3d53bb166a6075ad56f1fca8df63 (103 lines), PREDICTIONS.sha256 796bfa518c7b6a2f410824e00723af0cad2d34f7f2f4fd2cf4bfa6b747570d60 (1 files), pins in FROZEN.commits (the kit and the blob sources at eaee04a4; round 41's and round 45's kept stages at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/b5.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-b5-20261125-150329.out, the same bytes as score-b5.txt and as closing29/r46-n3k-logs/score-r46-n3k-b5-b5.txt); the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r46-n3k-b5:out/20261125-150329/b5/", "render-closing-r46-n3k-b5:fold/"]
terms = []
+++
**What ran.** Round 40's B5 (n3e section 3.3, built and never run then) rebuilt on today's kit
(decision B (b), closing29/n3k/design.md section 10.1): crumb3 (V0 to attribute 0, V2 to attribute
2, T3 stopping the tick) emitted by our task with sideband 0x043 (bit 6 with bits 1:0 = 3), the
session's only stage, after the stage's reset and the default begin draws, fill then triangle. Job 1
the emit on the tick pass; job 2 command 6 on a GETMISCINFO kick (crumb3 stops the tick, so the
after-read needs a kick pass, as row C, E1173); then the kit's gate, a fill and a triangle. The
first stage on the r46 module, after the boot's post-boot fill and triangle.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: b5: controls: every control passed
Q128-N3K-B5 RULE: B5-DONE, B5-GATE, B5-HID, B5-QUIET, B5-RUN, B5-SAME
PREDICTION B5-AOTHER: predicted printed, read FAILED: printed
PREDICTION B5-DONE: predicted held, read held: held
PREDICTION B5-E1: predicted failed, read FAILED: held
PREDICTION B5-FILL: predicted failed, read FAILED: held
PREDICTION B5-GATE: predicted held, read held: held
PREDICTION B5-HID: predicted held, read held: held
PREDICTION B5-LAND4: predicted printed, read FAILED: printed
PREDICTION B5-LANDNONE: predicted printed, read held: printed
PREDICTION B5-NEVER: predicted failed, read FAILED: held
PREDICTION B5-NOKICK: predicted failed, read FAILED: held
PREDICTION B5-QUIET: predicted held, read held: held
PREDICTION B5-REBASE: predicted failed, read FAILED: held
PREDICTION B5-RUN: predicted held, read held: held
PREDICTION B5-SAME: predicted held, read held: held
PREDICTION B5-T1: predicted failed, read FAILED: held
PREDICTION B5-T2: predicted failed, read FAILED: held
PREDICTION B5-T3: predicted failed, read FAILED: held
```

Every control passed (PG, E0, T0, B, J1, J2, SV); DR and DK read ok (printed in the ROW line). Every
prediction held: B5-DONE, B5-RUN, B5-HID, B5-SAME, B5-GATE and B5-QUIET held; B5-NEVER, -T1, -T2,
-T3, -E1, -REBASE, -NOKICK and -FILL failed as predicted; B5-AOTHER (printed) read failed. The
landing outcomes are printed, not scored: B5-LAND4 read failed, B5-LANDNONE read held.

**Results [HW].** Job 1 done (S1, M4 with run id 1, state 2, T 0x005a3305, 10 ticks); K5 BIF_FAULT 0
before and after each job, snap9 0. Post sa0-sa31 equal pre sa0-sa31 (sa0 V0, sa1 0x32005000, sa2
V2, sa22 0x32000000, sa23 0x04039000, the rest 0). Job 2 done on its kick (GETMISCINFO answered
after 199 us), its after-read equal to both pre and post. The gate's fill and triangle exact. KC
begin 10 and end 10, as K9 expects; the kernel's "3 events seen" at each stop of the stage. Post
pa0-pa15 (printed): 0x4b1f374b, 0x005d3000, 0x74b1dd97, 0x4d2817d1, 0x04156c77, 0xcc48604d,
0x55957f57, 0x03c3cda4, 0x1051761b, 0xdc5f1a54, 0xd51f0703, 0x5d50716d, Ma 0x5a5a3a18, 0x82f351b5,
Mb 0x5a5a3a1a, 0x11b1d77a: no V0 or V2 (landing NONE); pa1 is M13, the word in attribute 13 (E1181),
and pa12 and pa14 landq's markers of round 45's last row (E1233), so these pa are words of earlier
runs, kept through the boot as E1179 read [infer].

**What it shows.** Sideband 0x043 from our task ran crumb3 and the entry it started to done, left
the issuer's secondaries as they were and the next fill and triangle exact, as 0x003 and 0x843 did
(E1164, E1162, E1173) **[HW, one run]**: bit 6 with bits 1:0 = 3 changes neither the start nor the
bank, so the start rule's 0x043 is now read, not inferred (E1162-E1172's rule held). crumb3's V0 and
V2 stood in no pa of pa0-pa15, as with 0x843 (E1162) and unlike 0x003 (E1164) **[HW, printed]**;
whether the douta landed nowhere or the started entry's pa were not this run's is not told by one
read **[infer]**.

**What it does not show.** What bit 6 means; whether crumb3's V0 and V2 reach any pa with 0x043; one
run of this row.
