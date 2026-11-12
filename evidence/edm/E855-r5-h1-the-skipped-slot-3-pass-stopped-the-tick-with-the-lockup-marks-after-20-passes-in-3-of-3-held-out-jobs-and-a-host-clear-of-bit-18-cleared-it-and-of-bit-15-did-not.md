+++
id = "E855"
claim = "R5 stage h1 (r5-events, ring_skip3p.s of E836 at the stock timer_clock; Q295, Q166): the fill without the skip (b0, control) completed with the tick alive, bit 18 never set and HostCtl dwords 3 and 8 at 0 after the watch; with slot 3's first end-of-render pass skipped once and ended with the phase end (b1p, b1p-r2, b1p-r3, held out, hold_recovery Y) the tick stopped in 3 of 3 jobs after exactly 20 slot 0 passes after the fill's kick entry, each stop with the lockup marks (HostCtl dword 3 stop minus arm 1, dword 8 1, dword 9 0, dword 14 0, sw_events 1, TA3DCtl dword 57 0 and dword 58 0xaac267c2, CCB 3 and 3, CR_EVENT_STATUS 0x20040000 with bit 6 clear) and P3 not answered; CR_EVENT_STATUS bit 18 read set in 9 of 9 watch reads of each job, and after the stop a host write of bit 15 to CR_EVENT_HOST_CLEAR left it set and a write of bit 18 cleared it, in 3 of 3; frozen verdict 'H-HWR consistent (12 row groups), H-NOMARK REFUTED; H-TICKS consistent; H-LEVEL consistent, H-PULSE REFUTED; H-W consistent (2 row groups), H-ALL REFUTED, H-NONE REFUTED', every control passing (33), CR_DPM_TASK_STATE cannot tell (the rgn4 kernel never reads 0x0694)"
unit = "edm"
method = "R5 session r5-events stage h1 (round 5, decisions R5-3 a, R5-4 a; plan closing5/events/exp-events-r5.md section 5), dataset edm-closing-r5-events, attempt out/a1 (run 2026-11-12 09:15:52 Mac time, the session's first stage, the first session of round 5 and alone on the laptop), host cedar, kernel 7.3.0-resgx545, module of the linux fork's branch resgx545 at a2788bd8 (srcversion 99CD90DA26E3AFF9C450517, installed = loaded), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, fill tool ~/sgxfive-test-s1b (sha256 46a2d063...); the task ring_skip3p.s of r4-events byte for byte (sha256 3b35d3af...), which logs every entry of the four PDS #13 slots in rings and, with the host's flag set, skips slot 3's first end-of-render pass once and ends it with idf, wdf, phas #0, #0, pixel, end, parallel, nop.end; each job timer_clock written 0 and read back before a debugfs reset and the arm, a status dump at the arm (HostCtl dwords 3, 6 and 8), hold_recovery Y in the B1P jobs (put back to N and read back after), one fill, a bounded wait for the slot 3 entry in the page, the status watch of 50 ms (CR_EVENT_STATUS and STATUS2 through the regs file, 9 reads), the tick checked; a stop was signed at once (signature twice, the stop dumps stop-NAME-status.txt, -regs.txt and -own_res.json before any write), then the host's CLEAR by debugfs kregnow 0x0134 of bit 15 (status read 1 and 3 ms after) and of bit 18 (1, 3 and 20 ms after), P3 (one miscinfo), the tool collected, then reset, gate and health; under R5-4 (a) a stop explained by the marks and a readable count was the predicted outcome and the stage went on after each of the three, as it did with no lead decision needed (stage exit 0, clock_back at the end: timer_clock 0 read back, the ring's gap 25000 and 1006 Hz); predictions frozen in predictions/h1.tsv (PREDICTIONS.sha256) before the run, from landed text (E836, E837, E849, E353, E084) and from the firmware reading R-6 and the pysgx oracle S0 (cited/closing5/r6/reading-r6.md and s0/RESULT.md of resgx545-data-private, closing5/r6/), whose own three predictions were frozen first (closing5/r6/PREDICTIONS.md, sha256 in PREDICTIONS.sha256, 2026-11-12T07:30:27Z); every B1P row held out; scored by the frozen score/score_r5e.py h1 (out/a1/score-h1.txt, scorekit from resgx545 f0d5b39), re-run on the kept files on 2026-11-12 with byte-identical output; the freeze verified against main f0d5b39 before the re-run; the per-row table below printed after the run by a scratch script that calls the frozen scorer's own score() (not in the copy)"
tiers = ["HW", "RE", "infer"]
date = "2026-11-12"
data = ["edm-closing-r5-events:out/a1/h1/", "cited-scratch-private:cited/closing5/r6/"]
terms = [
    "Event Data Master (EDM)", "host_ctl.ukernel_detected_lockups", "host_ctl.interrupt_flags",
    "host_ctl.hw_recovery_sample_rate", "ta3d_ctl.kick_clear_3d", "CR_EVENT_STATUS.SW_EVENT",
    "CR_EVENT_HOST_CLEAR", "CR_EVENT_STATUS.PIXELBE_END_RENDER", "CR_DPM_TASK_STATE",
]
+++
**What ran.** E836's b1p (slot 3's end-of-render pass skipped and ended with the phase end) stopped
the tick; E849 read its stop dump after the hypothesis: the EDM's lockup marks after exactly 20
slot 0 passes after the fill's kick, one job, the fit. Before this session the firmware reading
R-6 (its three predictions frozen at 07:30:27Z, before the listing was opened) named the path [RE]:
the 3D half of the tick routine runs while sa9 bit 0 ("3D running") is set, which the 3D kicks set
and the end-of-render path clears; it counts tick passes in TA3DCtl dword 57 against HostCtl dword
5, stores a register signature in dword 58 at the 10th, compares at the 20th and, equal, runs the
lockup (dword 3 + 1, dword 8 bit 0, `SW_EVENT`, `CR_DPM_TASK_STATE` = 2, then a poll of
`CR_EVENT_STATUS` bit 6 with no exit); the oracle run S0 ran that path in pysgx with the arm set
by hand. Stage h1 repeats E836's job three times, held out, against H-NOMARK (no marks: E537's
kind of stop), with H-TICKS (the count 20), H-LEVEL against H-PULSE (bit 18 in the watch) and the
host's clears after the stop (H-W against H-ALL and H-NONE, E837's rows).

**Frozen verdict (as printed).** `SUMMARY: h1: B0 held; H-HWR consistent (12 row groups),
H-NOMARK REFUTED; H-TICKS consistent (1 row groups); H-LEVEL consistent (1 row groups), H-PULSE
REFUTED; H-W consistent (2 row groups), H-ALL REFUTED, H-NONE REFUTED; stops 3 ['b1p', 'b1p-r2',
'b1p-r3']; every control PASS (33); 84 of 87 non-control rows decided; Q295/Q166 rows: held out:
63 held, 21 FAILED, 3 cannot tell/void; refuted ['H-ALL', 'H-NOMARK', 'H-NONE', 'H-PULSE'];
cannot tell ['R6-DPM [not in a family: the rgn4 kernel cannot read it] (...)']; control: 33 held,
0 FAILED, 0 cannot tell/void` (out/a1/score-h1.txt). The 21 FAILED rows are the rivals' (H-NOMARK
12, H-PULSE 3, H-ALL 3, H-NONE 3); the 3 cannot tell are `CR_DPM_TASK_STATE`.

**Results [HW].**

| job | class | slot 3 | bit 18 | dw 3, 8, 9, 14 | sw_ev | dw 57, 58 | passes | bit 15 / 18 |
|---|---|---|---|---|---|---|---|---|
| b0 | ok | 4.65 ms | 0 of 9 | 0, 0 after it | 0 | 0, 0 | alive | not written |
| b1p | stop | 4.64 ms | 9 of 9 | 1, 1, 0, 0 | 1 | 0, 0xaac267c2 | 20 | set / clear |
| b1p-r2 | stop | 4.74 ms | 9 of 9 | 1, 1, 0, 0 | 1 | 0, 0xaac267c2 | 20 | set / clear |
| b1p-r3 | stop | 5.00 ms | 9 of 9 | 1, 1, 0, 0 | 1 | 0, 0xaac267c2 | 20 | set / clear |

Columns: the slot 3 entry seen after the fill began; the watch reads with bit 18 set; HostCtl
dwords 3, 8, 9 and 14 at the stop (b0: after the watch); `sw_events`; TA3DCtl dwords 57 and 58;
slot 0 passes after the fill's kick entry; bit 18 after the host's write of bit 15, then of 18.

Every arm dump read HostCtl dword 6 400000, dword 5 10 and dwords 3, 8 and TA3DCtl 57, 58 at 0
(the reset rebuilds the firmware's buffers). The count: each stop's page held 5 ticks before the
fill's kick entry, 10 after it on the 25000-unit grid (gaps 24990 to 25003) and dword 16 = 10 with
the ring full, 20 in all. At the signature `CR_CLKGATESTATUS` read 0x000ccfa0, the CCB 3 and 3,
`CR_EVENT_STATUS` 0x20040000 (bit 6 clear) and P3, one miscinfo after the clears, was not answered
in 504 or 505 ms with 0 new ring entries. The clears came about 2.2 s into each job: after bit 15
the status read 0x20040000 at 1 and 3 ms, after bit 18 0x20000000 at 1, 3 and 20 ms. The rows the
scorer printed per hypothesis: H-HWR 12 quantities x 3 jobs held (lockups, dword 8, dword 9,
`sw_events`, dword 57, dword 58 non-zero, dword 14, CCB, `EVENT_STATUS` bit 6 clear, tick stopped,
P3 not answered, and TA3DCtl dword 28 = 0, the last an [infer] row); H-TICKS 3 of 3; H-LEVEL 3 of
3; H-W 2 x 3 of 3. Each stop was recovered by one reset, the gate and the health exact (3 of 3),
which is the marked stop's second, third and fourth recovery on record.

**Read after the run [HW, post hoc].** TA3DCtl dword 58 read the same word, 0xaac267c2, in the
three stops, as in E849's: at the three clocks of h2 (E856) and in h3 (E857) too. [infer, with R-6:
a signature of the USE pixel service counters and four other registers] the 3D was idle in the
same state at the 10th and the 20th pass of every job.

**What it shows.** The stop after a skipped slot 3 end-of-render pass ended with the phase end is
the EDM's 3D lockup check, held out and replicated: 3 of 3 jobs stop after exactly 20 slot 0 passes
after the fill's kick with the lockup counted, the recovery request in `host_ctl.interrupt_flags`
and one `SW_EVENT`, which E537's kind of stop (H-NOMARK) never shows. The count is 2 x
`host_ctl.hw_recovery_sample_rate` (10). `CR_EVENT_STATUS` bit 18 is a level from the slot 3
entry to the stop (H-LEVEL, 3 of 3, with E837's job 4), and a host write to `CR_EVENT_HOST_CLEAR`
clears the bits written: bit 15 leaves bit 18, bit 18 clears it (H-W, 3 of 3 held out; with E823
and E837, 5 jobs, all with the EDM stopped). The marks and the count are the ones R-6 read in the
code [RE]; the hardware agrees with the reading on every row it could read.

**What it does not show.** That the count is in passes and not in time (at 400000, 20 passes are
about 19.3 ms; E856). `CR_DPM_TASK_STATE` = 2 and the poll of `EVENT_STATUS` bit 6 under the lock
[RE, R-6, S0]: the rgn4 kernel's regs file lists 0x0694 as skip and never reads it, so the row is
cannot tell, and bit 6 read clear is all the hardware says of the poll. Which register state
dword 58 samples (R-6 reads the registers; no row varied them). Whether the arm is sa9 bit 0 on the
hardware: no row reads sa9 (E857 tests what a host write and a command do not change). The clears
on a running EDM (E857), and on bits other than 15 and 18.
