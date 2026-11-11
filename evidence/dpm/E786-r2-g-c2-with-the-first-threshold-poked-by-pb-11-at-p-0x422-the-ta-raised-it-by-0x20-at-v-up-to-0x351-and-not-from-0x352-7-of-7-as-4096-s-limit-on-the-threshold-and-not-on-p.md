+++
id = "E786"
claim = "R2-geo stage g-c2 (9 jobs at P = 0x422, the knob that clamps the first threshold at 0x400 and above which nothing raised in E704, with the first threshold set instead by a poke of word 11 of the render context's parameter-buffer descriptor, `pb:11` = V, applied once to the next render): the two E625 controls passed on the tool's default triangle (V = 0x80 raised, V = 0x100 did not), the poke landed in 9 of 9 (the first partial render's status and the job's own 0x0624 read V), and at 4096x4096 with 1500 vertices the threshold was raised by 0x20 (dword 38 = 0x20, run peaks V, V + 0x20, ...) at V = 0x300, 0x33e and 0x351 and not at 0x352, 0x35e, 0x3a0 and 0x3de: H-abs (the limit C = 0x371 applies to the threshold the TA runs: raise iff V + 0x20 <= 0x371, frozen before the run from E774) held in 7 of 7 held-out cells with the flip exactly between 0x351 and 0x352, H-P (the limit is on the knob P = 0x373 at its value 0x422, so nothing raises) refuted 3 of 7 and H-rel (the limit follows P, so every poke raises) refuted 4 of 7; dword 37 read 0x10400 in all 5 raised jobs (the unpoked clamp value, not V)"
unit = "dpm"
method = "R2-geo stage g-c2 of the question-closing pass, round 2 (last of the five stages, run in a later driver call after R2-pixel with the stage restaged in between: g-c2 from 10:56:15 laptop time, the other four from 10:48:25; 9 jobs: k-tri-0x80 and k-tri-0x100, E625's two controls through probe tri rows with --kpoke-render, and k-1500-0x300, 0x33e, 0x351, 0x352, 0x35e, 0x3a0 and 0x3de through the tool's triangle rows with --kpoke pb:11=0xV), dataset render-closing-r2-geo, on the laptop (host cedar), 2026-11-10 (09:56 UTC), kernel 7.3.0-resgx545 (the linux-resgx545 branch's debugfs kpoke file present), module srcversion B21FDA82BD5E5CB5A627E3B (installed = loaded), stock firmware, tool ~/sgxfive-test-r1 (sha256 bf4f8be2d8a8fe50034559450928e05695dc96d396d4892f9b00ea6bc0d4f053); the only poke any job wrote is pb:11 (the generator, the runner and the static guard refuse any other), a 75 s watchdog on each poke row writing the kernel's debugfs reset (no job was class hang), all 9 of class ok (rc 3 'scene overflowed' for 7, rc 0 for the two tri controls), a debugfs reset before each job which clears any armed poke; the knob proof the first partial render's status (the poked threshold) and the 0x0624 rows; the raise read from the control block and the run peaks as in E774; scored by the frozen score/score_r2.py g-c2 (out/score-g-c2.txt); the reading of E774's ladder as a limit on P or on the threshold is the stage's question, the lead's combined reading of the three is in Q210"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["render-closing-r2-geo:out/g-c2/"]
terms = ["Dynamic Parameter Management (DPM)", "ta3d_ctl", "CR_DPM_ZLS_PAGE_THRESHOLD"]
+++
**What ran.** E774's ladder moved P and the first threshold together (thr0 = P - 0x22), so a
limit C = 0x371 on thr0 + 0x20 and a limit tied to P gave the same flip. E625's `pb:11` poke sets
the threshold in the descriptor without moving P. The stage holds P at 0x422 (where the knob's own
threshold is clamped to 0x400 and E704 saw no raise) and pokes V across the flip: V = 0x300, 0x33e
and 0x351 (V + 0x20 at most 0x371) and 0x352, 0x35e, 0x3a0 and 0x3de (above), at 1500 vertices and
4096x4096.

**Frozen verdict.** `controls pass; held out: consistent [H-abs (7)], refuted [H-P (3 of 7), H-rel
(4 of 7)]; repeat only: consistent none, refuted none; raise at 0x351, none at 0x352; D36 unraised
3/5, raised 2/4`. The D36 part is E790's (a side table, never gating).

**Results [HW].**

| job | V | first status | 0x0624 | run peaks | dword 36, 37, 38 | raise |
|---|---|---|---|---|---|---|
| k-tri-0x80 (control) | 0x80 | 0x80 | 0x80 | 0x80, 0xa0, 0x2 | 0, 0x10400, 0x20 | raised |
| k-tri-0x100 (control) | 0x100 | 0x100 | 0x100 | 0x100, 0x20 | 0, 0, 0 | none |
| k-1500-0x300 | 0x300 | 0x300 | 0x300 | 0x300, 0x320, 0x320 | 1, 0x10400, 0x20 | raised |
| k-1500-0x33e | 0x33e | 0x33e | 0x33e | 0x33e, 0x35e, 0x23e | 3, 0x10400, 0x20 | raised |
| k-1500-0x351 | 0x351 | 0x351 | 0x351 | 0x351, 0x371, 0x23d | 3, 0x10400, 0x20 | raised |
| k-1500-0x352 | 0x352 | 0x352 | 0x352 | 0x352 x 3 | 1, 0, 0 | none |
| k-1500-0x35e | 0x35e | 0x35e | 0x35e | 0x35e, 0x35e, 0x124 | 2, 0, 0 | none |
| k-1500-0x3a0 | 0x3a0 | 0x3a0 | 0x3a0 | 0x3a0, 0x3a0, 0x121 | 3, 0, 0 | none |
| k-1500-0x3de | 0x3de | 0x3de | 0x3de | 0x3de, 0x3de, 0x11e | 3, 0, 0 | none |

The poked ladder: raise at 0x300, 0x33e and 0x351; none at 0x352 and above. The second run reached
V in every 1500-vertex cell (the scorer voids a cell where it does not). The tri control at 0x100
is E625's own "none" (its second run peaks at 0x20 and does not reach the threshold, which is why
the row is a control for the poke and not a cell of the limit's ladder).

**What it shows and does not.** With P fixed at 0x422, the limit's flip lies at the poked
threshold 0x351 / 0x352, the same place E774 found with P and thr0 moving together (thr0 0x351 /
0x352, P 0x373 / 0x374): the raise follows the threshold the TA runs, not P and not the descriptor's
unpoked value. A limit tied to P's value 0x422 would have raised nothing (H-P) and a limit
relative to P would have raised every poke (H-rel); both fail.
Dword 37, which E774 read as 0x10000 | thr0 with thr0 = P - 0x22, read 0x10400 here in every raised
job: the clamp value of the knob at P = 0x422, not the poked V [infer: the firmware saves the
descriptor's own threshold word or the knob, and not the register that the poke changed; E774's
reading of dword 37 as "the first threshold" holds only when the two are equal]. What the stage
does not separate: whether C depends on the scene or the target (E785 gives a different C at
2048x2048) and what the DPM compares with C; and one scene and target only were poked.

**Correction 2026-11-11:** This adds a reading of the kept pair k-1500-0x351 (last raise) and
k-1500-0x352 (first silent), made offline in round 4 with the guard of the firmware's out-of-memory
routine read from the instructions (reading R-5, `closing4/p7/reading-r5.md`, with `flips.py`,
`flips.out`, `guard.py` and `sweep_last.out` beside it), and leaves the claim as is. [data, SEMI]
Both have 3 global pages at the abort; the resume reads 2 in the first and 1 in the second, and the
next entry 4 and 3, so the guard predicts raise and no raise, 2 of 2 as observed. The poked
threshold changes where the TA runs and so where the partial render drops the count, not the
firmware's compare (Q210).
