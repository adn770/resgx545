+++
id = "E1156"
claim = "r39-n3d-z stage own (N3d Z, module 0CDFCDB7, fork f9453424bf71, emitsk14, image crumb3 at fw14, pds2=req form=fw14, flagged, user present): our EDM task emitsk14 emitted, on the pass of a host GETMISCINFO kick, our word with the 14-bit sideband 0x843 (0xfb20b10800c08184) and s2 0x00020000 (the request bit), with R4's crumb3 image in the firmware's PDS #14 page; T (0x0acc) read 0x005a3305, crumb3's last tim marker, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2, done: every control passed, 'N3d-Z RULE: Z-DONE: all ran'; the first program emitted from our task that ran, its doutu starting our entry 1 to done; post's triangle and fill exact; which of the sideband, s2 and the kick pass decides is open"
unit = "edm"
method = "r39-n3d-z (render/closing-r39-n3d-z), stages own and post of the question-closing pass (round 39: session S3 of closing29/n3d/design.md, N3d, row Z, the full mirror of #14's emit, the user's flagged decision; flagged class, the user present with a reset ready), dataset render-closing-r39-n3d-z; first frozen as conditional on r39-n3d-k reading K-NEVER, refrozen before it ran at the user's choice after K read CANNOT TELL (E1155), without the 8-11 tick band (Z-NEVER reads T and S1, Δtick printed; README 'When'); attempt out/20261119-153429 (15:34:29, rc 0; stages own and post); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 0CDFCDB73D76F39FE9E593C installed and loaded alike, linux fork r39-kernel f9453424bf71 built on cachix (closing29/kernel39c/deliver/f9453424bf71/manifest; series check passed), its one-shot boot of 2026-11-19; stock firmware), the kit's owntask job kind (kit/ = resgx545 7d1aa9e5, its fwtask_run.py byte for byte, with the runner's `kick` step): our task owntask/emitsk14.blob (asm/fwtask/emitsk14.s, sha256 d3c2ab1e056d03f871581223eaecfff71861cd7ccc49783709d35c3d2d3c5a45, asm/fwtask/fwtask.map at 7d1aa9e5) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 pds2=req form=fw14` after the stage's reset and health pair (the arm's log: `own_code: 684 bytes accepted`, `emit image 0x30011100 ... pds=crumb3 pdsat=fw14 pds2=req form=fw14`), then one row c1-a of tester command 1 (`fwtask_run.py run`, `\"kick\": \"miscinfo\"`, timeout 200 ms counted from the kick, `ticks` on; the host first writing 0xdeadc0de into result slots 2-5; K0 read right after the command write, then one debugfs `miscinfo` read), the results page, the registers (snap0, snap9) and the gate kept, then the disarm; stage post the t30 triangle and fill; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes (the second): FROZEN.sha256 00a976d9789e1dc2c356bc6b5971c18b5bb89eaff4305060b018119852688bdf (48 files), PREDICTIONS.sha256 9254d090849e8486894881c23cfa77458d8c2c1b3b7e37ad3b023b14f9616065 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsk14.s and fwtask.map at 7d1aa9e5; r35-sa's kept snap0 and E1148's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv and post.tsv (gen/make.py), the rule score/score.py, run by the driver (out/20261119-153429/score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; the sideband 0x843 and s2 0x00020000 are facts of the data-private reads of the firmware's emits (O1, O2), no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-19"
data = ["render-closing-r39-n3d-z:out/20261119-153429/own/", "render-closing-r39-n3d-z:out/20261119-153429/post/", "render-closing-r39-n3d-z:fold/"]
terms = []
+++
**What ran.** E1155's job (row K) with the emit made the firmware's: emitsk14
(asm/fwtask/emitsk14.s) is emitsk with one word changed, the emit
0xfb20b10800c08184 (`emitpds.tasks.taske #0, r2, r3, r4, #0x843`), ours with the 14-bit
sideband 0x843, the value the firmware's #12 and #14 emits carry where ours carried 0; every other
field of the word is equal to theirs (facts of the data-private O1 read). `pds2=req` made the
kernel write 0x00020000 into the blob's `pds2` limm, so the emit's `s2` was the request #14's
emit carries (the data-private O2 fact; E1130, E146) where ours was 0; `form=fw14` is the arm
word that lets the kernel's verifier take the second emit word. The pass (a GETMISCINFO kick, as
K), the image (crumb3, 3 data rows, control 0x01800100) and its place (0x30011100, offset 0x100
of the firmware's PDS #14 page) were K's and E1154's. Against E1154 (M-NEVER) three things
changed at once: the sideband, `s2` and the pass. The row wrote command 1, read K0 6.7 ms later
(cmd 1, slot 1 the fill, HostCtl dword 12 at 2488), read debugfs `miscinfo` once (`GETMISCINFO
answered after 204 us`, printed, not scored) and polled.

**Frozen verdict (as printed).** By the driver (score-own.txt, score-post.txt) and again by hand
(fold/reproduce-own.out, reproduce-post.out, the same lines):

```
SUMMARY: own: controls: every control passed
ARM (printed, not scored): emit image 0x30011100 pds=crumb3 pdsat=fw14 pds2=req form=fw14
N3d-Z RULE: Z-DONE: all ran (Z-RUN: s2 or the form decides, alone or with the kick pass: run S)
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: Δtick 6 from the kick (K0) to 30 ms after the window; 15 from the command write (47.7 ms); 9 between the command write and K0
LANDING (one exploratory row, not N3's rule): pa0-pa3 0x00000000 0x00043000 0x3727c5ac 0x01555620; sa0-sa3 0x32004000 0x32005000 0x32002000 0x00000000; V0-V3 0x32004000 0x32005000 0x32002000 0x00000000; pa0 = V0 no, pa2 = V2 no
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls: PG, K0 (cmd 1 and slot 1 the fill at the kick: no tick pass emitted), K1 (slot 1 =
  M1 and run id 1, cmd 0), T0 (snap0's 0x0acc 0x01023f19, running) and B (BIF_FAULT 0 in snap9)
  all passed.
- c1-a: done after 10.5 ms, echo 1, cmd 0; class ok, stage rc 0.
- The page: X0 = 0x5a5a3303; S1 = 0x5a5a3304; M4 = 0x5a5a3302 and run id 1; state 2.
- T = 0x0acc in snap9: 0x005a3305, crumb3's last `tim` marker (its first, a stopped 0, and its
  0x200 lie before it on the way).
- The tick: Δtick 6 from the kick, 15 from the command write, over a 47.7 ms window; alive false
  (2494 three times), as crumb3's first `tim` write (a stopped 0) stops the tick by design.
- The owntask gate, run with the tick stopped, drew the triangle (`diff: 0 of 4096`) and the fill
  (`diff: 0 of 2048`) exactly; the disarm's reset brought the tick back (293, 322, 349); stage
  post: p1-tri and p2-fill `diff 0`, exact.
- LANDING (printed, not scored): entry 1's pa0 and pa2 were not V0 and V2 (snap0's TA3DCtl dwords
  0 and 2, crumb3's two `douta` values); sa0-sa3 equalled V0-V3.

**What it shows.** For the first time a PDS program emitted from our EDM task ran: all three of
crumb3's `tim` markers reached 0x0acc in order (the last one read), its `doutu` started emitsk14's
entry 1, and entry 1 ran to its last store and state 2 **[HW]**. With E1152 (a PDS `movs tim` is
the host's 0x0acc) this also measures, for an emitted program, what E1150 and E1154 could only
infer: an emitted program's `tim` write lands at 0x0acc. The combination that ran is the
sideband 0x843, `s2` = 0x00020000 (the request bit) and an issue from a kick pass; with E1154
(sideband 0, `s2` 0, a tick pass: never started) one or more of those three decides **[HW]**.
Which one, alone or together, is **[open]**: row S of closing29/n3d/design.md (`emitsb`
from a tick pass with the same word and `s2`) and the rows that split the sideband from `s2`
are the next step. The issuer went on past the emit as before (X0 written).

**What it does not show.** Which of the sideband, `s2` and the pass is needed; whether E1155's
stop was the kick pass's alone (K is CANNOT TELL); where crumb3's two `douta` landed: not pa0 or
pa2, but sa0 and sa2 hold V0 and V2 in the EDM's tasks anyway (E002, E1148), so the equal sa
values tell nothing **[infer]**; what entry 1's pa0-pa3 values are; one job only.
