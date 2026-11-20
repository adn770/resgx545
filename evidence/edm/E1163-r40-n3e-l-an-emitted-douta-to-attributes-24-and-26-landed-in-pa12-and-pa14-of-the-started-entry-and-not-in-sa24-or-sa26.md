+++
id = "E1163"
claim = "r40-n3e-l stage own (row L, module 83FBFD86, fork 423b436e7f80, emitsb14d, image land at fw14, no tim, douta of Ma 0x5a5a3a18 with control 0x1800 (attribute 24) and Mb 0x5a5a3a1a with 0x1a00 (attribute 26), form=fw14, sideband 0x843, s2 0, flagged, user present): B0's job with the land image: S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2, T running (0x0100fc26, no tim in the image): every control passed (PG, E0, T0, B, P0, P1); 'Q128-L RULE: L-PA' held where L-SA was predicted: the started entry read Ma in pa12 and Mb in pa14 and in no other of pa0-pa15, sa24 and sa26 read 0 before the emit and after and no sa of sa0-sa31 changed; so the emitted program's douta landed in the primary attributes of the task its doutu started, attribute 24 at pa12 and 26 at pa14, not in the secondaries; one rule that fits both is pa = n - 12 (inferred from two points; n/2 fits 24 but not 26); the tick kept counting; post's triangle and fill exact"
unit = "edm"
method = "r40-n3e-l (render/closing-r40-n3e-l), stage own and post of the question-closing pass (round 40: row L, closing29/n3e/design.md section 3.3 row L; flagged class, the user present with a reset ready), dataset render-closing-r40-n3e-l; attempt out/20261119-230429 (23:04:29, rc 0; stages own and post); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest; red rc 1 and series 12 of 12 PASS, closing29/r40-n3e-logs/cachix-wait.log; the fork's KUnit suite on the Mac shim 40 of 40, closing29/r40-n3e-logs/shim-r40-kernel.log), the one-shot boot of 2026-11-19 at about 23:00, post-boot draws ok; stock firmware), the kit's owntask job kind (kit/ = resgx545 b8528c0, branch r40-n3e, its fwtask_run.py byte for byte): our task owntask/emitsb14d.blob (asm/fwtask/emitsb14d.s, sha256 52c6c8a23db4540d338799ac2b73438f5a0b92dbc68a2b51e8fb0119990867d1, asm/fwtask/fwtask.map at b8528c0; emit word 0xfb20b10800c08184, sideband 0x843) armed once with own_arm `slots=0x1 entry=0 pds=land pdsat=fw14 form=fw14` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 fbd2f35c3e9ddac26e1d483cc46075d3d2879c200f240ad1a639c5265fd80da7 (48 files), PREDICTIONS.sha256 f27084a78b6a94380bc31313d1c796e01de90491ea0ea035a6b86fcd7378598c (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s, asm/fwtask/pds/land.s and fwtask.map at b8528c0; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv, the rule score/score.py, run by the driver (score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-19"
data = ["render-closing-r40-n3e-l:out/20261119-230429/own/", "render-closing-r40-n3e-l:out/20261119-230429/post/", "render-closing-r40-n3e-l:fold/"]
terms = []
+++
**What ran.** B0's job (E1162) with the image `land` (asm/fwtask/pds/land.s) instead of crumb3:
crumb3's three rows and control word 0x01800100, its two `douta`, `doutu` and `halt`, no `tim`;
the `douta` write constants of the image, Ma 0x5a5a3a18 with douta control 0x00001800 (control
bits 19:8 = 24) and Mb 0x5a5a3a1a with 0x00001a00 (26); the kernel fills U0 only. The design
predicted the secondaries (L-SA: sa24 = Ma, sa26 = Mb), as `douta` from a fill's secondary
program reaches `sa` (doc/specs/pds_isa.md section 3).

**Frozen verdict (as printed).**

```
SUMMARY: own: controls: every control passed
Q128-L RULE: L-PA: all ran; landing PA: Ma and Mb in post pa0-pa15, no sa pair [predicted: failed]
L-TICK (printed, not scored): T 0x0100fc26 (running); Δtick 39 from the command write; state 2 (after a DONE with no tim in the image)
LAND-L (printed): lland PA; pre sa24 0x00000000 sa26 0x00000000; post sa24 0x00000000 sa26 0x00000000; Ma at sa [] pa [12]; Mb at sa [] pa [14]
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls PG, E0, T0, B, P0 and P1 passed; X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302 and run
  id 1, state 2; T 0x0100fc26, bit 24 set and counting.
- pa0-pa15 of the started entry: Ma at pa12, Mb at pa14, the other fourteen the words B0 read
  there (pa13 0x82e151b5 as in B0).
- sa0-sa31 identical before and after; sa24 and sa26 zero both times.
- The owntask gate passed; post exact.

**What it shows.** From our task with sideband 0x843, an emitted program's `douta` does not land
in the issuing EDM's secondaries: the two markers stood in the primary attributes of the entry
its `doutu` started, attribute 24 at pa12 and attribute 26 at pa14 **[HW]**. A rule for other
attributes is **[infer]** from two points: pa = n - 12 fits both (n/2 fits 24 but not 26, and
D0's reading contradicts it, see E1161's correction). With pa = n - 12, crumb3's attributes 0 and
2 fall below pa0, which fits D0 and B0 seeing no V0 or V2 in pa0-pa15. With no `tim` in the
image, T kept counting after the DONE: the earlier DONE rows' stopped T was crumb3's markers.

**What it does not show.** Where attributes 0 to 11 land with 0x843; whether the offset is 12 for
every attribute; why the other sidebands put crumb3's V0 and V2 in every fourth pa (E1164);
one job only.
