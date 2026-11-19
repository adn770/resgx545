+++
id = "E1154"
claim = "r38-n3c-s3 stage own (N3c R4 M, module 88ADCEB5, fork e1cf9d2b43ab, image crumb3 at fw14, flagged, user present): our EDM task emitsb emitted E1150's crumb program with 3 data rows (crumb's 8 dwords and four zeros) and the control word 0x01800100, placed at 0x30011100, offset 0x100 of the firmware's own PDS #14 page with that page's PTE and flags; X0 0x5a5a3303 was written, T (0x0acc) kept counting (none of crumb's tim markers), S1, M4 and slots 2-4 kept the host's fill, state 0, and the EDM's tick stopped 9 ticks after the command write with no BIF fault: every control passed, 'N3c-M RULE: M-NEVER: the program never started (T running, S1 fill): page, flags and rows are not the cause'; the kit's reset recovered it (fill and triangle exact)"
unit = "edm"
method = "r38-n3c-s3 (render/closing-r38-n3c-s3), stage own of the question-closing pass (round 38: session S3 of closing29/n3c/design.md, N3c, row R4 M, the firmware's #14 mirror; flagged class, the user present with a reset ready), dataset render-closing-r38-n3c-s3; attempt out/20261119-112717 (11:27:17; stage own exited 4 at its one row, a runner stop; post did not run); on the laptop at home (kernel 7.3.0-resgx545, module srcversion 88ADCEB5AD9F055D077A99C installed and loaded alike, linux fork r38-kernel e1cf9d2b43ab (closing29/kernel38/deliver/e1cf9d2b43ab/manifest; series KUnit all pass), the same one-shot boot of 2026-11-19 as r38-n3c-s4 (E1153), which ran first; stock firmware), the kit's owntask job kind (kit/ = resgx545 94a7de5, its fwtask_run.py byte for byte): our task owntask/emitsb.blob (asm/fwtask/emitsb.s, sha256 83c25ac3cfc0a87473649979a41b8ddd0b49441d52a8eb9a7f405bb2866d7c2c as asm/fwtask/fwtask.map at 94a7de5 gives) armed once with own_arm `slots=0x1 entry=0 pds=crumb3 pdsat=fw14` after the stage's reset and health pair (the arm's log: `emit image 0x30011100 ... pds=crumb3 pdsat=fw14`; the kernel writes our 19-dword image at offset 0x100 of #14's page, past #14's 0x68 bytes, and zeroes the rest of the page's slack; the page's firmware bytes are neither read nor kept), then one row c1-a of tester command 1 (`fwtask_run.py run`, timeout 200 ms, `ticks` on; the host first writing 0xdeadc0de into result slots 2-5), the results page, the registers (snap0, snap9) and the runner's stop dump kept; health tool ~/sgxfive-test-t30 (t30, sha256 b5ea288d273f0da50884bbeec38f784a5d19773b8ed20efc7937dd455c1b87a5, resgx545 42c4de7); freezes: FROZEN.sha256 9354c82c87816a1f43e5f152e83df52cd592f3670711d4b60156c96f6c4c825c (48 files), PREDICTIONS.sha256 19cb5e01cb88e9f8f06eefb8d166dcd6faf39d3bacf05e0f1dc141a6f9d6739a (2 files), pins in FROZEN.commits (the kit, asm/fwtask/emitsb.s and fwtask.map at 94a7de5; r35-sa's kept snap0 and E1148's kept snapshots at data 5fa30750; t30's source 42c4de7); the frozen predictions predictions/own.tsv (gen/make.py), the rule score/score.py, run by hand on the kept directory (fold/reproduce-own.out: the stage stopped at its one row, rc 4, so the driver did not score it); readings past the scorer's from the kept files, by hand (fold/FOLD-NOTES.md), not frozen; stage post (the t30 triangle and fill) did not run. R6 P and R7 W (sessions r38-n3c-s5 and r38-n3c-s6, built) were not run: the design runs them only after M-T1 to M-DONE"
tiers = ["HW", "infer"]
date = "2026-11-19"
data = ["render-closing-r38-n3c-s3:out/20261119-112717/own/", "render-closing-r38-n3c-s3:fold/"]
terms = []
+++
**What ran.** E1150's job, word for word, with two changes at the arm, `pds=crumb3 pdsat=fw14`.
The image crumb3 (asm/fwtask/pds/crumb3.s) is crumb's 8 data dwords, four zero dwords and crumb's
7 instructions (E1150: `movs tim` of a stopped 0 first, the two `douta`, a `tim` of 0x200, the
`doutu` naming emitsb's entry 1, a `tim` of 0x005a3305, `halt`), 19 dwords; its control word is
`(3 << 23) | 0x100` = 0x01800100, 3 data rows, the firmware's own word for its PDS #14. `pdsat=fw14`
placed it in the firmware's PDS #14 buffer page, past #14's own image at the next 0x100: address
0x30011100, so the page is the one the firmware emits #14 from on every kick, with its PTE and
flags (read-write for the EDM), where E1148-E1150 and E1153 used the kernel's own read-only page
at 0x30022000. The emit's `s1` named it (address >> 4); `s2` and the form (`.tasks.taske`, from
our task's pass) were as before. The arm logged `own_code: 644 bytes accepted` and `emit image
0x30011100 ... pds=crumb3 pdsat=fw14`, `own_arm` read `... pds=crumb3 pdsat=fw14 blob=644`, and
the arm was healthy (ticks 217, 246, 274, at 986 Hz). One row, as frozen.

**Frozen verdict (as printed).** By hand on the kept directory (fold/reproduce-own.out):

```
SUMMARY: own: controls: every control passed
ARM (printed, not scored): emit image 0x30011100 pds=crumb3 pdsat=fw14
N3c-M RULE: M-NEVER: the program never started (T running, S1 fill): page, flags and rows are not the cause
X0 qualifier: 0x5a5a3303 (the issuer went on past the emit)
TICK: T1 stops the tick by design: the tick readings say nothing about what stopped it whenever T1 ran; only the M-NEVER row (T running) reads as r37's step A
TICK: Δtick 9 from the command write to 30 ms after the window (237.4 ms)
SIGNATURE (printed, not scored): snap0: bit 16 1, count - tick 5; snap9: bit 16 1, count - tick 5; stop0-regs: bit 16 1, count - tick 5
```

**Results [HW].**

- Controls: PG (page dword 0 = 0x4e574f53), E0 (slot 1 = 0x5a5a3301 and run id 1, cmd 0), T0
  (snap0's 0x0acc 0x0104d5e4, running) and B (BIF_FAULT 0 in snap9) all passed.
- c1-a: no done within 200 ms (`fwtask_run.py run` rc 1, `firmware hung: the tick stopped`), the
  kit classed the job `hang` and stopped the stage (rc 4).
- The page: X0 = 0x5a5a3303; S1, M4 and slots 2-4 all 0xdeadc0de; state 0, echo 0.
- T = 0x0acc after the stop: 0x0102837d in snap9 and 0x010565ab in the stop dump, bit 24 set,
  bits 23:0 at most 400000, the two reads different, so counting: none of crumb's 0, 0x200 or
  0x005a3305.
- The tick: Δtick 9 over a 237.4 ms window; `alive_at_stop` false: the tick 2114 and
  `USE0_SERV_EVENT`'s count 67655 in each of the runner's three reads at the stop.
- BIF_FAULT 0 in every read; the kit's reset and its health pair after the stop: t30 triangle
  `diff: 0 of 4096` and fill `diff: 0 of 2048`, exact.

**What it shows.** In the firmware's own PDS page, with that page's flags, 3 data rows and #14's
control word, our emit behaved as with the kernel's page, 2 rows and 0x01000100 (E1150): the issuer
went on, entry 1 never stored and the tick stopped within 9 ticks **[HW]**. crumb's first `movs
tim` never showed at 0x0acc, so the emitted program never executed its first instruction
**[infer]**: as E1150's, that rests on an emitted program's `tim` write landing in the host's
0x0acc as a client program's does (E1152). On it, the page, its flags, the rows field and the
control word are not why the program does not start, and with E1153 none of the program's
instructions is why the tick stops. What the design leaves (its V4 and V5): our emit's `s2`
operand or encoding form, and emitting from our task's timer pass where the firmware emits from
its kick pass.

**What it does not show.** Which of V4 and V5 is the cause (the design's next step, a user
decision, is not designed); whether the PDS fetched the image at all; that an emitted program's
`tim` write lands at 0x0acc (never seen to run); one job only. R6 and R7 were not run (planned
only after M-T1 to M-DONE).
