+++
id = "E784"
claim = "R2-geo stage g-t5v (13 jobs frozen, 11 run: a vertex program on the tool's triangle that loops N times on a backward br with an 8-instruction body, the loop count carried into the depth so that every vertex's stored depth word is 0x3f200000 + N if the loop ran N times; CR_EVENT_STATUS2 read from the debugfs registers after each job's reset and after the job): the controls passed (t5v-ctl0 without a loop, t5v-n1 and t5v-n3 with loops of 1 and 3: the stored depth words 0x3f200000, 0x3f200001, 0x3f200003 at every vertex, so a backward br loop in a vertex program runs on this hardware; STATUS2 0x400 after the reset and 0x400 after the job in all three), and the held-out ladder N = 28, 53, 55, 110, 220, 440 and 880 ran to its end on every vertex (stored depth words 0x3f20001c, 0x3f200035, 0x3f200037, 0x3f20006e, 0x3f2000dc, 0x3f2001b8, 0x3f200370) with STATUS2 0x400 before and after each; N = 1760 (0x3f2006e0 at every vertex) ran to its end and STATUS2 read 0x480 after it (bit 7 set; 0x400 before): bit 7 first set at N = 1760 and last clear at 880, so the frozen H-ITER and H-INSTR (bit 7 set from 55 iterations, as the pixel latch of E769, clear at 53) are refuted, H-NEVER (never set) is refuted, and H-TIME (monotone in the run's length) is consistent, with the point between 880 and 1760 iterations (about 7000 and 14000 instructions a vertex) not placed; the sweep stopped at the first set bit, so N = 3520 and 7040 were skipped"
unit = "edm"
method = "R2-geo stage g-t5v of the question-closing pass, round 2 (third of five stages, 13 frozen jobs of which 11 ran, the last two recorded as skipped by the sweep stop; template vtx_loop.s: 8 instructions an iteration, `p1 br -#7`, relative branch as E075, the loop count added to z so that the stored depth is 0x3f200000 + N, checked offline in sgx-sim at five code indices; pixel program pix_green), dataset render-closing-r2-geo, on the laptop (host cedar), 2026-11-10 at 10:49:51 laptop time (09:49 UTC), kernel 7.3.0-resgx545, module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); each job probe --temps 16 --pixels --tri vtxuse --width 64 --height 64 --vtx-coords 2 --dump-render, all 11 of class ok (rc 0), a debugfs reset before each job and CR_EVENT_STATUS2 (reg 0x0118) read from the debugfs regs after that reset and after the job (knob s2), the sweep stopped by the runner at the first post-job STATUS2 with bit 7 set (knob sweep:t5v), the loop proof the stored depth words of the decoded object; scored by the frozen score/score_r2.py g-t5v (out/score-g-t5v.txt); the instruction counts per vertex are 14 + 8 N from the template and were not measured"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r2-geo:out/g-t5v/"]
terms = ["Event Data Master (EDM)", "CR_EVENT_STATUS2"]
+++
**What ran.** Q082 asks what `CR_EVENT_STATUS2` bit 7 (set while a TA job hangs or faults) counts.
E769 found that bit 6, the pixel latch, is not a threshold in iterations or in instructions, and
left bit 7's condition untried. The stage runs the vertex program in a loop of known length, with
no fault and no hang, and reads the register after the reset and after the job. Whether a backward
`br` loops in a vertex program on this core was not known (every `br` in the data was a forward
offset); the loop proof, the depth word, answers it first.

**Frozen verdict.** `controls pass (loop proof n1, n3; STATUS2 0x400 after the reset and bit 7
clear on t5v-ctl0, n1, n3); bit 7 first set at N = 1760 (last clear 880): H-ITER / H-INSTR (set
from 55) REFUTED; H-TIME consistent (monotone); H-NEVER REFUTED; skipped by the sweep stop
['t5v-i3520', 't5v-i7040']; void ['t5v-i3520', 't5v-i7040']`. The two skipped lengths are not
readings.

**Results [HW].** Per job: N, the stored depth word at every vertex, STATUS2 before and after.

| job | N | depth word | STATUS2 before | after |
|---|---|---|---|---|
| t5v-ctl0 | none | 0x3f200000 | 0x400 | 0x400 |
| t5v-n1 | 1 | 0x3f200001 | 0x400 | 0x400 |
| t5v-n3 | 3 | 0x3f200003 | 0x400 | 0x400 |
| t5v-i28 | 28 | 0x3f20001c | 0x400 | 0x400 |
| t5v-i53 | 53 | 0x3f200035 | 0x400 | 0x400 |
| t5v-i55 | 55 | 0x3f200037 | 0x400 | 0x400 |
| t5v-i110 | 110 | 0x3f20006e | 0x400 | 0x400 |
| t5v-i220 | 220 | 0x3f2000dc | 0x400 | 0x400 |
| t5v-i440 | 440 | 0x3f2001b8 | 0x400 | 0x400 |
| t5v-i880 | 880 | 0x3f200370 | 0x400 | 0x400 |
| t5v-i1760 | 1760 | 0x3f2006e0 | 0x400 | 0x480 |

Every job's loop ran on every vertex (the scorer found no `LOOP FAILED`). Bit 7 stayed clear
through 880 iterations of the 8-instruction body, sixteen times the 55 iterations at which the
pixel latch of E431 had set bit 6, and set at 1760.

**What it shows and does not.** A backward `br` loop works in a vertex program on this core (the
relative offset of the ISA table). Bit 7 does not follow the pixel latch's threshold: a vertex
program of 55 to 880 iterations (440 to 7000 instructions a vertex) leaves it clear, so the TA
side's condition is not "an instance past a short count". It sets between 880 and 1760
iterations, a factor of two wide, so a quantity of the whole job (time, the three vertices'
instructions together, the TA's wait) is the reading that fits a single monotone point [infer:
H-TIME is consistent and was not given a point; the job times of the two jobs either side are not
compared here]. Not placed: the point inside (880, 1760], whether it is time or instructions
(a second body length would separate them: E769 did that for the pixel side), whether a fault,
which sets bit 7 121 us later (E764), shares the condition, and whether the bit's setting changes
the job (it did not: the objects and depth words are intact).

**Correction 2026-11-10:** (R3-pixel, E807, held out) The point inside (880, 1760] is placed: with
this body on the tool's three vertices bit 7 was clear at 1045 and set at 1100 iterations in both
orders of a 15-point ladder. The [infer] above, that a quantity of the whole job fits better than
one of a vertex, does not survive as a count: the per-job count HV-JOB missed at 12 vertices (set
between 554 and 698 iterations) and 48 (between 329 and 538), and a fixed count of a vertex's
instructions missed with a 16-instruction body (between 601 and 649) and at 12 and 48 vertices, as
did a count of its multiply-adds everywhere; bit 7 showed 184 to 195 us after the burst began in
every set job of E807 [HW].
