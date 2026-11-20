+++
id = "E1166"
claim = "r40-n3e-b3 stage own (row B3, module 83FBFD86, fork 423b436e7f80, emitsb_sb842, image crumb3 at fw14, form=sb842, sideband 0x842, s2 0, flagged, user present): B0's job with bit 0 of the sideband cleared: T read 0x005a3305, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1, state 2: every control passed, 'Q128-B3 RULE: B3-DONE' where H-DM (bits 1:0 = 3, the event data master, needed) and H-ALL predicted NEVER: both failed; sa0-sa31 read the same before the emit and after; the started entry read V0 (0x32004000) in pa0, pa4, pa8 and pa12 and V2 (0x32002000) in pa2, pa6, pa10 and pa14, where the rows with 0x843 read neither (E1161, E1162); post exact"
unit = "edm"
method = "r40-n3e-b3 (render/closing-r40-n3e-b3), stage own and post of the question-closing pass (round 40: row B3, closing29/n3e/design.md section 3.3; flagged class, the user present with a reset ready), dataset render-closing-r40-n3e-b3; attempt out/20261119-230732 (23:07:32, rc 0; stages own and post); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest; red rc 1 and series 12 of 12 PASS, closing29/r40-n3e-logs/cachix-wait.log; the fork's KUnit suite on the Mac shim 40 of 40, closing29/r40-n3e-logs/shim-r40-kernel.log), the one-shot boot of 2026-11-19 at about 23:00, post-boot draws ok; stock firmware), the kit's owntask job kind (kit/ = resgx545 b8528c0, branch r40-n3e, its fwtask_run.py byte for byte): our task owntask/emitsb_sb842.blob (asm/fwtask/emitsb_sb842.s, sha256 45459114ddc80b74e0c10c078b16488164ef89d4599188e4948c6c4df0c81e65, asm/fwtask/fwtask.map at b8528c0; emitsb14d with only the emit word changed, emit word 0xfb20b10800808184, sideband 0x842) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=sb842` after the stage's reset and health pair (the kernel's arm line: pds2=0, emit image 0x30011100), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), the results page, the registers (snap0, snap9) and the gate kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 bea3ef3f01c2446e235b91ed3c0bfa1e4ab472dd67cecf704a404b23172186d7 (49 files), PREDICTIONS.sha256 13c065184688095b2244a48f7c053edb7950fa641ab7f90c788cbdaa557b0443 (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb14d.s, asm/fwtask/emitsb_sb842.s and fwtask.map at b8528c0; r35-sa's and r36-n3's kept snapshots at data 9fce0b99; t30's source 42c4de7); the frozen predictions predictions/own.tsv, the rule score/score.py, run by the driver (score-own.txt, score-post.txt) and again by hand (fold/reproduce-own.out, reproduce-post.out, the same lines); the SURVEY lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r40-n3e-b3:out/20261119-230732/own/", "render-closing-r40-n3e-b3:out/20261119-230732/post/", "render-closing-r40-n3e-b3:fold/"]
terms = []
+++
**What ran.** B0's job (E1162) with one change, the emit word: blob emitsb_842 (emitsb14d with only
the word changed), armed at `form=sb842`, sideband 0x842.

**Frozen verdict (as printed).**

```
SUMMARY: own: controls: every control passed
Q128-B3 RULE: B3-DONE: all ran (sideband 0x842 reads RUN; H-DM predicts NEVER; H-ALL predicts NEVER)
SUMMARY: post: the stock firmware drew the triangle and the fill exactly after the disarm
```

**Results [HW].**

- Controls PG, E0, T0 and B passed; X0 0x5a5a3303, S1 0x5a5a3304, M4 0x5a5a3302 and run id 1,
  state 2, T 0x005a3305.
- SURVEY: sa0-sa31 identical before and after. pa0-pa15 of the started entry: pa0, pa4, pa8 and
  pa12 read 0x32004000 (V0), pa2, pa6, pa10 and pa14 0x32002000 (V2), the odd pa the words B0 read
  there (pa1 0x00043000, pa3 0x01555620, ...); the LANDING line 'pa0 = V0 yes, pa2 = V2 yes'.
- The owntask gate passed; post exact.

**What it shows.** Bits 1:0 = 3 are not needed: 2 with bits 6 and 11 runs **[HW]**, so H-DM's reading of bits 1:0 as the event data master (3) fails. With this sideband the started entry reads crumb3's `douta` values
where 0x843's rows (D0, B0) read none: V0 (attribute 0) in every fourth pa from pa0 and V2
(attribute 2) in every fourth from pa2 **[HW]**; that these are crumb3's `douta` values and not
copies of sa0 and sa2 (which hold the same words) is **[infer]**.

**What it does not show.** Why the landing differs from 0x843's; what bits 6 and 11 do; one job
only.
