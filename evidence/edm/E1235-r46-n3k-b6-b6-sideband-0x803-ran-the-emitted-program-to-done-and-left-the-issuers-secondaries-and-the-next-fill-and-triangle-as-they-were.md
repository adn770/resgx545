+++
id = "E1235"
claim = "r46-n3k-b6 stage b6 (row B6, module 10BBF3BF, fork c5094783eb88, emitsb_sb803s, image crumb3 at fw14, form=sb803, sideband 0x803, s2 0, flagged, user present): crumb3 emitted with sideband 0x803 ran to done (S1, M4 with run id 1, state 2), post sa0-sa31 = pre, job 2's after-read on a kick = pre = post, the gate's fill and triangle exact, K5 BIF_FAULT 0 before and after each job and in snap9; every control passed, 'Q128-N3K-B6 RULE: B6-DONE, B6-GATE, B6-HID, B6-QUIET, B6-RUN, B6-SAME', every prediction held; landing (printed) EVERY4"
unit = "edm"
method = "r46-n3k-b6 (render/closing-r46-n3k-b6), stage b6 of the question-closing pass (round 46: row B6, closing29/n3k/design.md section 10.1; flagged class, the user present with a reset ready; the user's decisions of the design, section 10: A=a, B=b, C=a, D=a, E=a, F=b), dataset render-closing-r46-n3k-b6; attempt out/20261125-150427 (15:04:27; stage b6 ended rc 0 and the driver scored it, score-b6.txt); on the laptop (kernel 7.3.0-resgx545, module srcversion 10BBF3BFBD51D559106589F installed and loaded alike (control SV), linux fork r46-kernel c5094783eb88, r45-kernel plus the landr and landp images, built on cachix 2026-11-25 (closing29/kernel39c/deliver/c5094783eb88/manifest, closing29/kernel39c/r46-kernel-check.pass, closing29/r46-n3k-fork-logs/cachix-wait.log), installed and booted once on 2026-11-25 (closing29/r46-n3k-logs/install.log, closing29/r46-n3k-logs/boot.log, closing29/r46-n3k-logs/postboot.log, closing29/r46-n3k-logs/step1-test-session.log); every session of round 46 on that one boot; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), K7's per-stage draws, K8's draw lists, K9's command count (the control DK) and K10's arm words pds=landr and pds=landp, which no stage of these sessions used (kit/ = resgx545 eaee04a4, branch r46-n3k, its fwtask_run.py byte for byte); the round's blob and arm lines accepted by the module's verifier: the fork's KUnit suite at c5094783eb88 on the Mac shim, 51 of 51 (closing29/r46-n3k-fork-logs/shim-r46-green-fork.log; r46-red 48 of 51, closing29/r46-n3k-fork-logs/shim-r46-red-fork.log), with the round's own suite 54 of 54 (closing29/r46-n3k-fork-logs/shim-r46-green.log; r46-red 50 of 54, closing29/r46-n3k-fork-logs/shim-r46-red.log; a wrong expected word fails, 53 of 54, closing29/r46-n3k-fork-logs/shim-r46-neg.log): our task owntask/emitsb_sb803s.blob (asm/fwtask/emitsb_sb803s.s at eaee04a4, sha256 8df8f978087cbbe3fbff02fff941c6f2f74a3ed0569166864304f05534bf8f51; emitsb_sbc43s with only the emit's sideband changed, 0x803) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb803` after the stage's reset and its begin health (fill and triangle), then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de) on a GETMISCINFO kick; then the gate (on_gate_fail score: the fill and triangle read by the outcomes); the results page, the registers (snap0, snap9) and the record kept; crumb3's bytes unchanged since round 40 (E1161-E1172); both sidebands on the module's list since round 40; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 cc67e6b7a7271723d9a0ecf5187f0907bdbe8761da62a347e112c6c6ebc9b83a (103 lines), PREDICTIONS.sha256 8bfcd93f02363a86ba5e3ab4630217c67152fc8575768486f76326c72d83c8aa (1 files), pins in FROZEN.commits (the kit and the blob sources at eaee04a4; round 41's and round 45's kept stages at data 72e07b2d6; t30's source 42c4de7); the frozen predictions predictions/b6.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-b6-20261125-150427.out, the same bytes as score-b6.txt and as closing29/r46-n3k-logs/score-r46-n3k-b6-b6.txt); the JOB, BIF, FAULT, SURVEY, ATTR, EVENTS, AFTER, KC and HKC lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen"
tiers = ["HW", "infer"]
date = "2026-11-25"
data = ["render-closing-r46-n3k-b6:out/20261125-150427/b6/", "render-closing-r46-n3k-b6:fold/"]
terms = []
+++
**What ran.** Round 40's B6 (n3e section 3.3, built and never run then) rebuilt on today's kit
(decision B (b), closing29/n3k/design.md section 10.1): crumb3 (V0 to attribute 0, V2 to attribute
2, T3 stopping the tick) emitted by our task with sideband 0x803 (bit 11 with bits 1:0 = 3), the
session's only stage, after the stage's reset and the default begin draws, fill then triangle. Job 1
the emit on the tick pass; job 2 command 6 on a GETMISCINFO kick (crumb3 stops the tick, so the
after-read needs a kick pass, as row C, E1173); then the kit's gate, a fill and a triangle. Right
after B5's session and its health draw.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: b6: controls: every control passed
Q128-N3K-B6 RULE: B6-DONE, B6-GATE, B6-HID, B6-QUIET, B6-RUN, B6-SAME
PREDICTION B6-AOTHER: predicted printed, read FAILED: printed
PREDICTION B6-DONE: predicted held, read held: held
PREDICTION B6-E1: predicted failed, read FAILED: held
PREDICTION B6-FILL: predicted failed, read FAILED: held
PREDICTION B6-GATE: predicted held, read held: held
PREDICTION B6-HID: predicted held, read held: held
PREDICTION B6-LAND4: predicted printed, read held: printed
PREDICTION B6-LANDNONE: predicted printed, read FAILED: printed
PREDICTION B6-NEVER: predicted failed, read FAILED: held
PREDICTION B6-NOKICK: predicted failed, read FAILED: held
PREDICTION B6-QUIET: predicted held, read held: held
PREDICTION B6-REBASE: predicted failed, read FAILED: held
PREDICTION B6-RUN: predicted held, read held: held
PREDICTION B6-SAME: predicted held, read held: held
PREDICTION B6-T1: predicted failed, read FAILED: held
PREDICTION B6-T2: predicted failed, read FAILED: held
PREDICTION B6-T3: predicted failed, read FAILED: held
```

Every control passed (PG, E0, T0, B, J1, J2, SV); DR and DK read ok (printed in the ROW line). Every
prediction held: B6-DONE, B6-RUN, B6-HID, B6-SAME, B6-GATE and B6-QUIET held; B6-NEVER, -T1, -T2,
-T3, -E1, -REBASE, -NOKICK and -FILL failed as predicted; B6-AOTHER (printed) read failed. The
landing outcomes are printed, not scored: B6-LAND4 read held, B6-LANDNONE read failed.

**Results [HW].** Job 1 done (S1, M4 with run id 1, state 2, T 0x005a3305, 9 ticks); K5 BIF_FAULT 0
before and after each job, snap9 0. Post sa0-sa31 equal pre sa0-sa31 (sa0 V0, sa1 0x32005000, sa2
V2, sa22 0x32000000, sa23 0x044aa000, the rest 0). Job 2 done on its kick (GETMISCINFO answered
after 209 us), its after-read equal to both pre and post. The gate's fill and triangle exact. KC
begin 10 and end 10, as K9 expects; the kernel's "3 events seen" at each stop of the stage. Post
pa0-pa15 (printed): V0 0x32004000 at pa0, pa4, pa8 and pa12 and V2 0x32002000 at pa2, pa6, pa10 and
pa14 (landing EVERY4), pa1 M13; the odd pa3-pa15 equal B5's word for word.

**What it shows.** Sideband 0x803 from our task ran crumb3 and the entry it started to done, left
the issuer's secondaries as they were and the next fill and triangle exact, as 0x003 and 0x843 did
(E1164, E1162, E1173) **[HW, one run]**: bit 11 with bits 1:0 = 3 changes neither the start nor the
bank, so the start rule's 0x803 is now read, not inferred (E1162-E1172's rule held). crumb3's V0 and
V2 stood in every fourth pa, as with 0x003, 0x002, 0x842 and 0xc43 (E1164, E1166, E1168, E1172), and
B5's run a minute earlier left none there with the odd pa the same **[HW, printed]**; that B6's own
douta put them there, so that bit 11 does not change where crumb3's words land and bit 6 without bit
10 does (0x043, 0x843 NONE; 0x003, 0x803, 0xc43 EVERY4), is **[infer]**: one read each, unscored,
and the started entry's pa can hold words of earlier runs (E1174, E1175, E1177).

**What it does not show.** What bit 11 means; whether the every-fourth pa were this run's; one run
of this row.
