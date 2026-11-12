+++
id = "E902"
claim = "Round 7 offline fold (Q111's 0x0694 clause and Q294): the six held TA jobs of r6-held were each the first render of a new context, so by the module's fork the kicks carried TA flag 0x1 (flags 0x73) and the firmware's Clear wrote (index << 3) | 2 to CR_DPM_TASK_STATE (0x0694) before the fault [RE]; the debugfs peek of 0x0694 read 0 before each job, during each hold and after each reset (18 of 18, and 3 of 3 in stage s0), so the register does not read back what the Clear writes and E890's reads could not tell a reached store from an unreached one [infer]: the peek is exhausted; the refrozen oracle O4 (pysgx running the stock microkernel after E814's own writer alias2.blob, seeded with 0x0728 = 0 and the writer's measured entry state) kept the tick on D0 and E812's four words with the next entry's pclink 0x98 as measured, but D1 (0xb009c4dc) and D2 (0x02000100) ended in refusals of the simulator, not modelled hangs, so O4 fails its controls, and all seven of Q294's test words were refused at the same point (an emitted PDS program reading the running timer), so it does not separate them and no Q294 laptop rows follow"
unit = "edm"
method = "Offline, no run (round 7, area faults, decision R7-1 a; plan closing7/c/exp-faults-r7.md sections 2.1 (step F6) and 3 (oracle O4)). F6: the kept job texts of render-closing-r6-held stage q (out/20261112-154536/q: cases.tsv, <cell>.txt, <cell>.peek0/1/3.txt, the kernel slices) read for the six held jobs a0, a1, b0, b1 (640 x 480) and a2, b2 (288 x 144), and the fork's branch resgx545 at 3f0b3e74 (the r6 kernel, read with git show: sgxfive_render_job_scene sets first = !scene_open, sgx_render_scene_kick sets the TA flags SGX_RENDER_TA_FIRST 0x01, _LAST 0x02 and _INVAL 0x70) against doc/specs/3d.md section 4.5 step 2 (Clear, on TA flags 0x1 or 0x8, [RE]); the session's --poke words (cmd:1, 10, 13, 16) are TA register words (cmd:1 is CR_TE_AA, E788), not the flags. O4: closing7/c/o4/PREDICTIONS.md and o4_oracle.py frozen (PREDICTIONS.sha256) before the first run; pysgx from resgx545 at 3251b4f (this fold's sgx-sim change: a code window that reaches our page at instruction 0x4000 and a carry of the task state that outlives a task, E536, both off by default; tests first), the microkernel booted as test_sgx_ccb booted_sgx(2, 0x01061A7F) does with the movs assumption, two GETMISCINFO (count byte 2), edm-closing-r3x-events bins/alias2.blob (sha256 c41bd078...) placed at instruction 0x4000 with its patches applied by tools/fwtask (cont0 = 6, the slot's record target) and slot 0's start dword re-evaluated by tools/fwtask/overlay_model (0x0800006f to 0x0804000f), seeds [HW] listed before the run: register 0x0728 = 0 (0 in 83 kept dumps) and the writer's entry state as E814's D0 reader read it (pclink 0x98, p0 to p3 1 1 0 0, r20 0, r21 0x4000, i0, i1); rows D0, D1, D2, E812's C1 to C4 (controls) and the seven words of O3, each 6 ticks with 2,000,000 steps of budget per run; output o4_oracle.json, the verdict and post hoc reading in RESULT.md; firmware-derived, so published under cited/ of resgx545-data-private. Re-run from its published copy: byte-identical"
tiers = ["HW", "RE", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-held", "edm-closing-r3x-events", "cited-scratch-private"]
terms = ["CR_DPM_TASK_STATE", "CR_DPM_PAGE", "CR_EVENT_STATUS", "Event Data Master (EDM)"]
+++
**What was done.** E890 read `CR_DPM_TASK_STATE` (0x0694) as 0 at the arm, at the lockup stop
and after it, against R-6's reading that the lockup path stores 2 there; the round 6 session
r6-held added a host `peek` of the register to every held cell. The round 7 plan asked first
whether the register keeps a written value at all (F6), and refroze Q294's oracle with the two
reads O3 refused (O4).

**F6, results [HW, RE].** The six held cells each ran `tri` on a new context ("render context
for targets up to W x H") whose first render faulted ("FAILED after 0 renders"): a first kick
of a new scene, so the kernel's TA flags were 0x73 and bit 0 ran the firmware's Clear, which
writes `(index << 3) | 2` to 0x0694 for each render target before the TA starts. The peek read
`reg 0x0694 0x00000000` before each job (peek0), during each hold (peek1, about 2.8 s after the
fault) and after each reset (peek3): 18 of 18; s0's three peeks read 0 too.

**O4, frozen verdict (RESULT.md).** O4 fails its controls (D1 and D2 refused, not HANG) and does
not separate the words (7 of 7 REFUSED, one outcome). Controls: D0 PASS (KEEP 6 of 6 ticks; the
reader at tick 2 read pclink 0x98 and p0 to p3 1 1 0 0), C1 to C4 PASS (KEEP, reader pclink 0x98,
4 of 4), D1 FAILED and D2 FAILED (refused on tick 1).

| row | outcome | where it ended |
|---|---|---|
| D0, C1 to C4 | KEEP | - |
| D1 0xb009c4dc | REFUSED | an emitted PDS program reads the timer (tim), unknown while it runs |
| D2 0x02000100 | REFUSED | the task reads `CR_EVENT_STATUS` (0x012c), never written |
| bits 4, 7, 10 and their four combinations | REFUSED (7 of 7) | the same PDS program as D1 |

**Read after the run [RE, infer; post hoc].** The seeds moved every refusal of O3: no row
stopped at 0x0728 or at pclink, the writer ran in every row and the closed pass ended in D1 and
the test words (HostCtl dword 12 + 1) before the refusal. D1 and the seven words, each holding bit
4, 7 or 10, end the closed pass with an emitted PDS program that D0 and the kept words of E812
(bits 2, 3, 6, 14 to 16, 19, 23 and the count byte 0xb0) do not emit, as the hardware kept the
tick on those (E812, 13 of 13) and stopped it on D1 (E814). D2 left both of E814 D2's marks
before its refusal (CCB read offset 3 against write offset 2, HostCtl dword 14 0xad002600). At
the C rows' next entry p1 read 0 and p2, p3 1, the writer's own setting, as E536 measured.

**What it shows.** 0x0694 does not read back what the TA kick's Clear writes, at least not while
a TA job is held, before a job or after a reset [infer: the Clear's write is RE, the reads HW], so
a host read of it cannot tell whether the lockup path's store was reached; E890's reading stands
as measured and says nothing about the store. No more peek rows. With the measured seeds the
simulator runs E814's writer and the closed pass as the hardware did for the words that kept the
tick, and reproduces D2's two marks; for every word with bit 4, 7 or 10 it reaches a PDS program
it cannot run, so it cannot say which of those bits stops the tick.

**What it does not show.** Whether the store at the lockup stop is reached (stage L, `lock #0`
twice, or the kernel option K1); what 0x0694 reads while a task that wrote it is still pending.
O4's post hoc split (bits 4, 7 and 10 against the kept words) is a reading of one simulated pass
with the movs assumption, not a frozen outcome and not a hardware result. The next refusals are
the running timer an emitted PDS program reads (not host-readable at that instant) and
`CR_EVENT_STATUS` at the closed task's later read (E814's stop dumps read 0x20000000); per the
frozen rule no seed was added after the result.
