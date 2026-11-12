+++
id = "E890"
claim = "R6 session r6-held part P (stage p1, E855's job on the r6 kernel with a debugfs peek of 0x0694; Q111, and the lockup rows of E855 to E857): the fill without the skip (b0, control) completed with the tick alive and no marks; with slot 3's first end-of-render pass skipped and ended with the phase end (b1p, b1p-r2, held out, hold_recovery Y) the tick stopped in 2 of 2 jobs after exactly 20 slot 0 passes after the fill's kick with E855's lockup marks (HostCtl dword 3 + 1, dword 8 1, sw_events 1, TA3DCtl dword 57 0 and dword 58 0xaac267c2, CR_EVENT_STATUS 0x20040000 with bit 6 clear, P3 not answered), a host write of bit 15 to CR_EVENT_HOST_CLEAR left bit 18 and of bit 18 cleared it; CR_DPM_TASK_STATE (0x0694) read 0x00000000 at the arm, at the stop before any write, after the clears and after the recovery in both, and 0x00000000 in every other read of the session; frozen verdict 'H-HWR consistent (12 row groups), H-NOMARK REFUTED; H-TICKS consistent; H-LEVEL consistent, H-PULSE REFUTED; H-W consistent (2 row groups), H-ALL REFUTED, H-NONE REFUTED; H-R6 REFUTED, H-IDLE consistent; H-RESET consistent', every control passing (29), 64 of 64 non-control rows decided; so the store of 2 to CR_DPM_TASK_STATE that the firmware reading R-6 places before the lockup's poll is not seen in a host read of the register"
unit = "edm"
method = "R6 session r6-held part P (round 6, decisions R6-3 a, R6-4 a, R6-5 a; plan closing6/rank/rank-round6.md section 4 and session B), dataset render-closing-r6-held (p/), attempt p/out/a1 (run 2026-11-12, load step 15:44:50 and stage p1 15:44:53 Mac time, before part H on the same boot, the second session on the new kernel), host cedar, kernel 7.3.0-resgx545, module of the linux fork's branch r6-kernel at 3f0b3e74 (srcversion 41E2F5C756F96D20F7109A4, installed = loaded; the peek is commit db7faabc: one plain read of 0x0694 under the device lock, refused for every other offset), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, fill tool sha256 46a2d063... (E855's), the task ring_skip3p.s of E836 byte for byte (sha256 3b35d3af...); E855's job and sequence (timer_clock 0 written and read back before a debugfs reset and the arm, hold_recovery Y in the B1P jobs, one fill, the slot 3 entry waited for, a 50 ms status watch of 9 reads, the tick checked, a stop signed, the stop dumps before any write, the host's clears of bits 15 and 18, P3, then reset, gate and health) with the peek read at the arm, at the stop right after the signature and before any write, after the clears and after the recovery (b0: at the arm and after the watch); 3 jobs, 2 predicted stops, each explained by the marks and a readable count and recovered by one reset, the gate and the health exact, the stage going on as R6-5 (a) rules (stage exit 0, timer_clock 0 at the end); the laptop's files under ~/scratch/r6h/p/; predictions frozen in p/predictions/p1.tsv (p/PREDICTIONS.sha256) before the run from landed text only (E855 for R-6's reading, E836, E837, E849, E084): H-R6 (the stop's read is 2 and differs from the arm's, decided only when the arm read is not 2) against H-IDLE (the stop leaves 0x0694 as the arm read it), H-RESET [infer] (the read after the recovery equals the arm's); scored by the frozen p/score/score_p.py p1 (p/out/a1/score-p1.txt, scorekit from resgx545 d9b2969), re-run on the kept files on 2026-11-12 with byte-identical output; the freeze (p/FROZEN.sha256, p/FROZEN.commits at d9b2969) verified by tools/closing/session_tests.sh; the firmware reading R-6 (cited/closing5/r6/reading-r6.md of resgx545-data-private) read after the run to say what the refutation bears on"
tiers = ["HW", "RE", "infer"]
date = "2026-11-12"
data = ["render-closing-r6-held:p/out/a1/p1/", "cited-scratch-private:cited/closing5/r6/"]
terms = [
    "Event Data Master (EDM)", "CR_DPM_TASK_STATE", "CR_EVENT_STATUS.DPM_STATE_CLEAR",
    "host_ctl.ukernel_detected_lockups", "host_ctl.interrupt_flags", "ta3d_ctl.kick_clear_3d",
    "CR_EVENT_HOST_CLEAR", "CR_EVENT_STATUS.PIXELBE_END_RENDER",
]
+++
**What ran.** E855 left one row of the EDM's lockup stop cannot tell: R-6 [RE] reads that after
the `SW_EVENT` write the lockup path takes `lock #0` twice, stores 2 to `CR_DPM_TASK_STATE`
(0x0694) and polls `CR_EVENT_STATUS` bit 6 (`DPM_STATE_CLEAR`) with no exit, and the rgn4 kernel's
regs file never reads 0x0694 (it skips the registers whose write starts work). The r6 kernel adds a
debugfs `peek` that reads that one register. Part P runs E855's control and two of its held-out
jobs again with the peek around each stop: H-R6 (the stop reads 2, unlike the arm) against H-IDLE
(the stop reads what the arm read), and E855's own rows as replicates.

**Frozen verdict (as printed).** `SUMMARY: p1: B0 held; H-HWR consistent (12 row groups), H-NOMARK
REFUTED; H-TICKS consistent (1 row groups); H-LEVEL consistent (1 row groups), H-PULSE REFUTED; H-W
consistent (2 row groups), H-ALL REFUTED, H-NONE REFUTED; H-R6 REFUTED, H-IDLE consistent (1 row
groups); H-RESET consistent (1 row groups); stops 2 ['b1p', 'b1p-r2']; every control PASS (29); 64
of 64 non-control rows decided; Q111/... rows: held out: 46 held, 18 FAILED, 0 cannot tell/void;
refuted ['H-ALL', 'H-NOMARK', 'H-NONE', 'H-PULSE', "H-R6 (...)", "H-R6 (...)"]; control: 29 held, 0
FAILED, 0 cannot tell/void` (p/out/a1/score-p1.txt; the elided question ids after Q111 are the two
E857 answered; the two H-R6 entries name its two rows, the stop's value and the stop against the
arm). The 18 FAILED rows are the rivals' (H-NOMARK, H-PULSE, H-ALL, H-NONE and H-R6's).

**Results [HW].**

| job | class | slot 3 | bit 18 | marks at the stop | passes | bit 15 / 18 | 0x0694 reads |
|---|---|---|---|---|---|---|---|
| b0 | ok | 4.58 ms | 0 of 9 | none | alive | not written | 0, after the watch 0 |
| b1p | stop | 4.73 ms | 9 of 9 | 1, 1, sw 1, 0, 0xaac267c2 | 20 | set / clear | 0, 0, 0, 0 |
| b1p-r2 | stop | 4.67 ms | 9 of 9 | 1, 1, sw 1, 0, 0xaac267c2 | 20 | set / clear | 0, 0, 0, 0 |

Marks: HostCtl dword 3 less the arm's, dword 8, `sw_events`, TA3DCtl dwords 57 and 58. 0x0694 reads:
at the arm, at the stop, after the clears, after the recovery. Each stop had
`CR_EVENT_STATUS` 0x20040000 (bit 6 clear), the CCB 3 and 3, 5 ticks before the fill's kick and 10
after it with dword 16 = 10 (20 in all), and P3 not answered in 505 and 504 ms with 0 new ring
entries. The stop's peek came about 0.34 s after the arm's, after the signature, so well after the
20th pass. Every peek line was `reg 0x0694 0x00000000` (its format a control; 10 reads in the 3 jobs
and the preflight's), each read taking about 11 ms; the reads of part H on the same boot gave the
same (E891, E892: before, during and after six held TA faults).

**Read after the run [RE, post hoc].** R-6's prediction (ii) is the store and the poll after the
`SW_EVENT` write; (i), the count against HostCtl dword 5 and the arm sa9 bit 0, and (iii), what
the skipped handler would have cleared, are separate and are what E856 and E857 tested. R-6 marks
open whether the second `lock #0` already blocks. The static listing of the EDM's stores
(doc/specs/edm_dataflow.md) has 0x0694 written with 2 at the same place, and with
`(index << 3) | 2` in the TA kick's clear (doc/specs/3d.md).

**What it shows.** The lockup stop after a skipped slot 3 pass is replicated on the r6 kernel with
every mark, count and clear of E855 (2 of 2 held out; with E855 to E857, 12 of 12 jobs). A host
read of `CR_DPM_TASK_STATE` at that stop gives 0, as at the arm and after the recovery (H-IDLE,
H-RESET), so H-R6, the row that turned R-6's store of 2 into a register read, is refuted: the
store is not seen. `CR_EVENT_STATUS` bit 6 read clear, which agrees with a wait on it or with no
DPM state clear having been started.

**What it does not show.** Why the store is not seen. Each of these fits the reads: the EDM never
reaches the store (it waits before it, at the second `lock #0`, which R-6 leaves open); the store
reaches another register than 0x0694 (R-6's `str #421` read as dword 421); 0x0694 does not read back
what is written (a task register that starts work and reads 0, as every read on record has, during
held TA faults too); or the plain read the peek makes does not see the register (the same read path
gives the live values of the regs file's other registers, so this is the least likely). So the
refutation is of the register read, not of the firmware reading: whether the lockup path stores to
the DPM, and what the busy EDM waits on (the poll of bit 6 or a lock), are open. Nothing here
writes 0x0694 or reads it while the firmware's own TA kick clear runs.
