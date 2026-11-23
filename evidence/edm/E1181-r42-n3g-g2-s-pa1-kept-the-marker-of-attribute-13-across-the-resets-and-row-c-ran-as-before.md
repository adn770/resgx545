+++
id = "E1181"
claim = "r42-n3g-g2 stage s (row S, row C again, module 079DD0D1, fork ec6511d5de87, emitsb14s, image crumb3 at fw14, form=fw14, sideband 0x843, s2 0, flagged, user present): after row M (E1180), its watchdog's and the kit's resets and the session's begin reset: job 1's post pa1 = M13 0x005d3000 and the other odd pa unchanged; job 2's after-read equal to job 1's pre, the gate exact, BIF_FAULT 0 before and after each job, every control passed; 'Q128-N3G-S RULE: C-GATE, C-SAME, S-KEEP' as predicted, S-BACK failed: attribute 13 keeps the word written to it across resets, so 0x00043000 there was a stale word"
unit = "edm"
method = "r42-n3g-g2 (render/closing-r42-n3g-g2), stage s of the question-closing pass (round 42: row S, closing29/n3g/design.md section 3.3; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-21), dataset render-closing-r42-n3g-g2; attempt out/20261122-163902 (16:39:02; stage s ended rc 0 and the driver scored it, score-s.txt; stage q followed); on the laptop (kernel 7.3.0-resgx545, module srcversion 079DD0D13F231EEAC52FE0F installed and loaded alike, linux fork r42-kernel ec6511d5de87 built on cachix 2026-11-21 (closing29/kernel39c/deliver/ec6511d5de87/manifest, closing29/r42-n3g-logs/cachix-wait.log), the one-shot boot of 2026-11-22; stock firmware), the kit's owntask job kind with a job list per row, each job's BIF_INT_STAT and BIF_FAULT read before and after it (K5), the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 c0e2dc36, branch r42-n3g, its fwtask_run.py byte for byte): our task owntask/emitsb14s.blob (asm/fwtask/emitsb14s.s, sha256 c3f9ce90c2ea24208d6b8bcafef3a1f77e105c03bc8c51b4bee5fbcd04e7fb39, asm/fwtask/fwtask.map at c0e2dc36; emitsb14d with a cmd 6 branch in entry 0 that stores sa0-sa31 into dwords 224-255, writes M6 and the run id into slot 6 and emits nothing; entry 1 and cmd 1's path as emitsb14d's, emit word 0xfb20b10800c08184, sideband 0x843) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=fw14` after the stage's reset and health pair, then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on a GETMISCINFO kick (kick miscinfo); the results page, the registers (snap0, snap9), the record and the gate (fill, then triangle) kept; the round's blobs and arm lines accepted by the module's verifier unchanged: the fork's KUnit suite at ec6511d5de87 on the Mac shim with a suite of their own, 48 of 48 (closing29/r42-n3g-logs/shim-r42.log; r42-red 46 of 48, shim-r42-red.log; a wrong form fails, shim-r42-neg.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 2a31df2e5945735a83363ea52855e6a0dc6f08bd50345a69e6380a7cf8354e61 (86 files), PREDICTIONS.sha256 effaec4333424aa9eb28ec078d230dfa502ae4354af3aa17246bf4d2b92933cb (2 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at c0e2dc36; r35-sa's and round 41's kept files at data 5e9c84b2; t30's source 42c4de7); the frozen predictions predictions/s.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-s-20261122-163902.out, the same bytes as score-s.txt); the SURVEY, JOB, BIF, GATE and RBOOT lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW", "infer"]
date = "2026-11-22"
data = ["render-closing-r42-n3g-g2:out/20261122-163902/s/", "render-closing-r42-n3g-g2:fold/"]
terms = []
+++
**What ran.** Row C (E1179) again, first in session G2, after row M (E1180) had written M13 to
attribute 13 and after three resets: M's watchdog recovery, the kit's reset at M's end and G2's
begin reset. The question: does pa1 keep M13 (S-KEEP), or does a writer we do not run put 0x00043000
back (S-BACK)?

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: s: controls: every control passed
Q128-N3G-S RULE: C-GATE, C-SAME, S-KEEP
```

S-BACK and S-OTHER (printed) failed; C-DIFF and C-NOKICK failed.

**Results [HW].**

- Job 1 done (run id 1, state 2, T 0x005a3305, 9 ticks); its post pa1 = M13 0x005d3000, pa3-pa15's
  odd words as in E1179; the post pa0-pa15 the same 16 words as row M's.
- Job 2 done on the kick (answered after 214 us); its after-read equal to job 1's pre in all 32.
- K5: BIF_FAULT 0 before and after each job; the gate's fill and triangle exact, no devcoredump;
  health ok after the session (closing29/r42-n3g-logs/health-r42-n3g-g2.log).

**What it shows.** The word our program sent to attribute 13 stays there across resets and is the
started entry's pa1 in a later row of another sideband **[HW]**. With R-BOOT (E1179: 0x00043000 in
pa1 through the reboot) and M (E1180), the 0x00043000 that sa13 held and the fills and the triangle
faulted at in E1172 and E1174-E1178 was a stale word of attribute 13, left by a writer before our
rows, not a value bit 10 makes **[HW]**. With 0x843 that word does nothing: the EDM's own sa stay
and the gate runs **[HW]**. That one store holds the started entry's pa and keeps every word nobody
rewrites across resets is **[infer]** from pa1 and the odd pa (design section 0.1).

**What it does not show.** Who wrote 0x00043000 first; whether a cold power-off clears attribute 13;
whether other attributes keep their words the same way (only pa1 was written and read back).
