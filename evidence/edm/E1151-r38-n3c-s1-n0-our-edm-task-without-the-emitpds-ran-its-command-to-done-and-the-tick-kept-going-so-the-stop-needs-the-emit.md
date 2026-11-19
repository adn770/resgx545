+++
id = "E1151"
claim = "r38-n3c-s1 stage own (N3c R1 n0, module 77917296, fork 4f35fc20ffa9, no emit image, flagged, user present): our EDM task emitsn, emitsb's entry 0 with the emitpds and its operands taken out, ran E1149's job word for word: X0 0x5a5a3303, M4 0x5a5a3302 and run id 1, state 2, done, 40 ticks in a 38.1 ms window, the tick still advancing after it and the gate's fill and triangle exact: every control passed, 'N3c-R1 RULE: N0-OK: the stop needs the emit (expected)'; so the cmd-1 path of E1148-E1150 without the emitpds does not stop the tick"
unit = "edm"
method = "r38-n3c-s1 (render/closing-r38-n3c-s1), stage own of the question-closing pass (round 38: session S1 of closing29/n3c/design.md, N3c, row R1 n0, the user's flagged decision; flagged class, the user present with a reset ready), dataset render-closing-r38-n3c-s1; attempt out/20261119-092626 (09:26:26, rc 0; stages own, tim and post in that order); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 77917296568EB311B89B0DA installed and loaded alike, linux fork r37-kernel 4f35fc20ffa9, no build and no boot for the session (closing29/kernel37/deliver/4f35fc20ffa9/manifest); stock firmware), the kit's owntask job kind (kit/ = resgx545 2ce7fc7, its fwtask_run.py byte for byte): our task owntask/emitsn.blob (asm/fwtask/emitsn.s, sha256 31f75ec5194fbabb7b1e4b433009ad9ef74d1bb105fac4f10810a1da572103ff as asm/fwtask/fwtask.map at 2ce7fc7 gives) armed once with own_arm `slots=0x1 entry=0` (no pds= word; the kernel logged `emit image 0x0 (0: none)`) after the stage's reset and health pair, then one row n0 of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the gate kept, then the disarm; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 327cdaea6ef7f8eedd077410687714f6ed0b6c029173804436119d1c1e5a9412 (57 files), PREDICTIONS.sha256 adecdbe9a12d6db25dbb1a3cb72335099057edb1df1a2c79e533ef822346373e (3 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsn.s and fwtask.map at 2ce7fc7; r37-n3b-a's kept registers at data 31ec9b2f; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by the driver (out/score-own.txt) and again by hand on the kept directory (fold/reproduce-own.out, the same lines); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen"
tiers = ["HW"]
date = "2026-11-19"
data = ["render-closing-r38-n3c-s1:out/20261119-092626/own/", "render-closing-r38-n3c-s1:fold/"]
terms = []
+++
**What ran.** emitsn is emitsb (E1149, E1150) with the three `pds` immediates and the
`emitpds` taken out, one entry: on command 1, entry 0 stores the marker 0x5a5a3301 (M1) and the
run id in slot 1, clears the command, fences, stores **X0** 0x5a5a3303 at page dword 70, fences,
then stores what E1149's entry 1 would have stored last, **M4** 0x5a5a3302 and the run id at
dwords 80-81, the echo and state 2, and tail-calls the closed task as emitsb does. The arm took
the blob (`own_code: 346 bytes accepted`), logged `emit image 0x0 (0: none) pds=v1` (the module's
default word, unused with no emit) and was healthy (ticks 209, 238, 265). One row, E1149's job
word for word: command 1, run id 1, timeout 200 ms, `ticks` on.

**Frozen verdict (as printed).** By the driver (out/score-own.txt) and again by hand
(fold/reproduce-own.out):

```
SUMMARY: own: controls: every control passed
N3c-R1 RULE: N0-OK: the stop needs the emit (expected)
X0 qualifier: 0x5a5a3303 (the task stored past cmd 0)
SIGNATURE (printed, not scored): snap0: bit 16 1, count - tick 5; snap9: bit 16 1, count - tick 6
```

**Results [HW].**

- Controls: PG (page dword 0 = 0x4e574f53), E0 (slot 1 = 0x5a5a3301 and run id 1, cmd 0), T0
  (snap0's 0x0acc 0x010110d3, running) and B (BIF_FAULT 0 in snap9) all passed.
- n0: done (runner rc 0, class ok), echo 1, slot 1 = 0x5a5a3301, 1, X0 0x5a5a3303; slot 4 = M4
  0x5a5a3302 and run id 1; state 2; the fill's other dwords unchanged.
- The tick: 40 ticks over a 38.1 ms window (37.9 expected at the arm's rate), where E1149 and
  E1150 counted 10 in about 237 ms; after the job, `alive` read the tick advancing (2121, 2148,
  2175) with `USE0_SERV_EVENT`'s count moving. snap9's 0x0acc 0x0105f638, running.
- The gate after the row: t30 fill `diff: 0 of 2048` and triangle `diff: 0 of 4096`; the stage's
  end health pair exact too. BIF_FAULT 0 in every read; no bad kernel line.
- `USE0_SERV_EVENT` bit 16 set at snap0 (0x00010613) and at snap9 (0x00010974) of a job that did
  not stop, as at the snap0 of E1148, E1149 and E1150: the bit marks nothing about these stops
  (printed, not scored, as frozen).

**What it shows.** With everything of E1149's job but the `emitpds` (the same arm, slot, entry,
command, stores, fences and tail call into the closed task), our task ran its command to done
and the EDM's tick kept its rate through the job and after it. So the stop of E1148, E1149 and
E1150 needs the emit: our cmd-1 path, its stores and the tail call do not stop the tick by
themselves (N0-STOP refuted).

**What it does not show.** Which part of the emit stops the tick (the program, its page or
flags, the control word's rows, the operands or the issuing pass: the design's V1-V5); why the
emitted program does not start (E1150, Q128); one job only.
