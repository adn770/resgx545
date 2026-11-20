+++
id = "E1173"
claim = "r41-n3f-h1 stage c (row C, the control, module 83FBFD86, fork 423b436e7f80, emitsb14s, image crumb3 at fw14, form=fw14, sideband 0x843, s2 0, flagged, user present): B0's job (E1162) then a second job of command 6 on a GETMISCINFO kick, in which entry 0 stored its own sa0-sa31: job 2 done, its after-read equal to job 1's pre sa0-sa31 in all 32, the gate's fill and triangle exact, BIF_FAULT 0, every control passed, 'Q128-N3F-C RULE: C-GATE, C-SAME' as predicted: with 0x843 the EDM's own secondaries are left as they were and the next transfer and render run"
unit = "edm"
method = "r41-n3f-h1 (render/closing-r41-n3f-h1), stage c of the question-closing pass (round 41: row C, closing29/n3f/design.md section 3.2; flagged class, the user present with a reset ready; the user's decisions A-F of the design all (a), 2026-11-20), dataset render-closing-r41-n3f-h1; attempt out/20261120-161456 (16:14:56; stage c ended rc 0 and the driver scored it, score-c.txt; stage x followed); on the laptop (kernel 7.3.0-resgx545, module srcversion 83FBFD860D4E0D4CE691F48 installed and loaded alike, linux fork r40-kernel 423b436e7f80 built on cachix 2026-11-19 (closing29/kernel39c/deliver/423b436e7f80/manifest), the one-shot boot of 2026-11-19, no rebuild and no boot in round 41; stock firmware), the kit's owntask job kind with a job list per row, the gate's whole tool outputs and the devcoredumps kept (kit/ = resgx545 e516a7aa, branch r41-n3f, its fwtask_run.py byte for byte): our task owntask/emitsb14s.blob (asm/fwtask/emitsb14s.s, sha256 c3f9ce90c2ea24208d6b8bcafef3a1f77e105c03bc8c51b4bee5fbcd04e7fb39, asm/fwtask/fwtask.map at e516a7aa; emitsb14d with a cmd 6 branch in entry 0 that stores sa0-sa31 into dwords 224-255, writes M6 and the run id into slot 6 and emits nothing; entry 1 and cmd 1's path as emitsb14d's, emit word 0xfb20b10800c08184, sideband 0x843) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14 form=fw14` after the stage's reset and health pair, then one row of two jobs: command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on, no kick: the emit on the first tick pass that sees the command; the host first writing 0xdeadc0de into result slots 2-5 and dwords 128-223), then command 6 (the after-read: entry 0 stores sa0-sa31 into dwords 224-255, which the host first fills with 0xdeadc0de; ticks, 200 ms) on a GETMISCINFO kick (`\"kick\": \"miscinfo\"`); the results page, the registers (snap0, snap9) and, after an ok end, the gate (fill, then triangle) kept; the round's three after-read blobs accepted by the module's verifier unchanged: the fork's KUnit suite at 423b436e7f80 on the Mac shim with a suite of their own, 43 of 43 (closing29/r41-n3f-logs/shim-r41.log); health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 9c0f4ecbbb1dbdcab0055423075007ac7d02cee61b719208888683ff57f1b7de (69 files), PREDICTIONS.sha256 f9dd397b8522828a3e5a5d41f2a661f9d30c786ac953c4df9018a5bf79563f9a (2 files), pins in FROZEN.commits (the kit, the blob sources and fwtask.map at e516a7aa; r35-sa's and r40-n3e's kept files at data b5b95bff; t30's source 42c4de7); the frozen predictions predictions/c.tsv, the rule score/score.py, rescored by hand on the kept directory (fold/reproduce-c-20261120-161456.out, the same bytes as score-c.txt); the SURVEY, JOB and GATE lines are printed, not scored; readings by hand in fold/FOLD-NOTES.md, not frozen; the sideband values are facts of the data-private read of the firmware's emits, no firmware byte"
tiers = ["HW"]
date = "2026-11-20"
data = ["render-closing-r41-n3f-h1:out/20261120-161456/c/", "render-closing-r41-n3f-h1:fold/"]
terms = []
+++
**What ran.** B0's job (E1162: emitsb14d, crumb3 at fw14, sideband 0x843) with a second job: command
6 on a GETMISCINFO kick, which our entry 0 serves by storing its own sa0-sa31 into dwords 224-255
(the after-read). The control of session H1: the same two jobs as row X with #14's sideband.

**Frozen verdict (as printed).** The driver's score, reproduced by hand byte for byte:

```
SUMMARY: c: controls: every control passed
Q128-N3F-C RULE: C-GATE, C-SAME
```

**Results [HW].**

- Controls PG, E0, T0, B (BIF_FAULT 0 in snap9) and J1 passed. Job 1: X0 0x5a5a3303, S1 and M4 with
  run id 1, state 2, T 0x005a3305, 9 ticks.
- Job 2 done on the kick (GETMISCINFO answered after 200 us), slot 6 0x5a5a3306 and run id 2; its
  after-read of sa0-sa31 equal to job 1's pre in all 32 (sa0 0x32004000, sa1 0x32005000, sa2
  0x32002000, sa22 0x32000000, sa23 0x03ed8000, the rest 0); job 1's post (the started entry's sa)
  equal to the pre too.
- The gate: fill exact, triangle exact, no devcoredump.

**What it shows.** With #14's sideband the EDM's own sa0-sa31 after the emitted program and the
entry it started are what they were before **[HW]**, and the next fill and triangle run: the after-
read and the gate work as built, so row X's readings (E1174) are bit 10's.

**What it does not show.** The sa past sa31; anything about bits 6, 10 or 11; one run.
