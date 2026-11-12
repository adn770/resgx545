+++
id = "E856"
claim = "R5 stage h2, the dose (r5-events, ring_skip3p.s; Q295): with HostCtl dword 6 set through the timer_clock knob to 800000 and to 1600000 (read back and read in each arm dump), the fill without the skip completed with the tick alive on a grid of 50000 and of 100000 CR_TIMER units (b0a, b0b, controls; b0b the first measurement of E084's rule at 1600000), and with slot 3's first end-of-render pass skipped once and ended with the phase end and no host write before the stop (b1pa x2 at 800000, b1pb x2 at 1600000, held out) the tick stopped in 4 of 4 jobs after exactly 20 slot 0 passes after the fill's kick entry, about 40 and 80 ms after it, with the lockup marks of E855 (HostCtl dword 3 stop minus arm 1, dword 8 1, sw_events 1, TA3DCtl dword 57 0 and dword 58 0xaac267c2, CR_EVENT_STATUS 0x20040000) and bit 18 set in every watch read; frozen verdict 'H-HWR consistent (24 row groups), H-NOMARK REFUTED; H-TICKS consistent (2 row groups), H-TIME REFUTED; H-LEVEL consistent (2 row groups), H-PULSE REFUTED' (H-TIME: 10 +-1 passes at 800000 and 5 +-1 at 1600000, the stop about 19.3 ms after the kick), every control passing (52)"
unit = "edm"
method = "R5 session r5-events stage h2 (round 5, decisions R5-3 a, R5-4 a; plan closing5/events/exp-events-r5.md section 5), dataset edm-closing-r5-events, attempt out/a1 (run 2026-11-12 09:16:18 Mac time, gated on h1's kept stage.json), the laptop, module, firmware, tool and task of E855; per job the timer_clock knob (debugfs; HostCtl dword 6, which the kernel copies at the firmware's boot, E084) written to 800000 (0x000c3500) or 1600000 (0x00186a00) and read back before the job's reset, the arm (its rate judged against +-10% of 399.0 MHz / dword 6 when only the landed 900 to 1100 Hz band failed it, ok_landed recorded false in 6 of 6: 485 to 499 Hz at 800000, 242 to 251 Hz at 1600000), the arm dump (dword 6), hold_recovery Y in the B1P jobs, one fill, the slot 3 entry waited for, a status watch of 100 ms at 800000 (16 or 17 reads) and 150 ms at 1600000 (24 reads), no host write before the watch ended, the tick checked, a stop signed (signature twice, stop dumps before any write), P3, then reset, gate and health; B0A and B0B controls that gate their clock's rows, every B1P's own tick gap a control; the stage went on after each of its four predicted stops (R5-4 a, no lead decision needed), stage exit 0, clock_back at the end (timer_clock 0 read back, gap 25000, 993 Hz); predictions frozen in predictions/h2.tsv before the run (H-TICKS from E849 and R-6, which reads the count as tick passes against HostCtl dword 5; H-TIME, a stop 19.3 ms after the kick whatever the tick, frozen as its rival with no mechanism in the code); scored by the frozen score/score_r5e.py h2 (out/a1/score-h2.txt), re-run on the kept files on 2026-11-12 with byte-identical output"
tiers = ["HW", "RE", "infer"]
date = "2026-11-12"
data = ["edm-closing-r5-events:out/a1/h2/", "cited-scratch-private:cited/closing5/r6/"]
terms = [
    "Event Data Master (EDM)", "host_ctl.ukernel_timer_clock", "host_ctl.hw_recovery_sample_rate",
    "host_ctl.ukernel_detected_lockups", "host_ctl.interrupt_flags", "ta3d_ctl.kick_clear_3d",
    "CR_EVENT_STATUS.PIXELBE_END_RENDER", "CR_DPM_TASK_STATE",
]
+++
**What ran.** At the stock `timer_clock` (HostCtl dword 6 = 400000, a tick every 25000 `CR_TIMER`
units) 20 slot 0 passes and about 19.3 ms after the fill's kick are the same stop (E849, E855).
Stage h2 slows the tick by 2 and by 4 through the knob and freezes H-TICKS (the stop after 20
passes at both clocks: the count R-6 reads in the code [RE], dword 57 + 1 per tick pass against
HostCtl dword 5) against H-TIME (the stop about 19.3 ms after the kick: 10 +-1 passes at 800000,
5 +-1 at 1600000). No host write comes before the watch ends, so nothing but the clock differs
from h1's B1P.

**Frozen verdict (as printed).** `SUMMARY: h2: B0 held; H-HWR consistent (24 row groups), H-NOMARK
REFUTED; H-TICKS consistent (2 row groups), H-TIME REFUTED; H-LEVEL consistent (2 row groups),
H-PULSE REFUTED; stops 4 ['b1pa', 'b1pa-r2', 'b1pb', 'b1pb-r2']; every control PASS (52); 92 of 96
non-control rows decided; Q295/Q166 rows: held out: 68 held, 24 FAILED, 4 cannot tell/void;
refuted ['H-NOMARK', 'H-PULSE', 'H-TIME (the stop about 19.3 ms after the kick whatever the tick:
10 +-1 ticks at 800000; no mechanism in the code, R-6)', 'H-TIME (... 5 +-1 ticks at 1600000;
...)']; cannot tell ['R6-DPM [not in a family: the rgn4 kernel cannot read it] (...)']; control:
52 held, 0 FAILED, 0 cannot tell/void` (out/a1/score-h2.txt). The 24 FAILED rows are the rivals'
(H-NOMARK 16, H-PULSE 4, H-TIME 4); the 4 cannot tell are `CR_DPM_TASK_STATE`.

**Results [HW].**

| job | dword 6 | tick gap | class | bit 18 | ring before / after, dw 16 | passes | marks |
|---|---|---|---|---|---|---|---|
| b0a | 800000 | 50000 | ok | 0 of 17 | | alive | none |
| b1pa | 800000 | 50000 | stop | 16 of 16 | 3 / 12, 8 | 20 | 1, 1, 1 |
| b1pa-r2 | 800000 | 50000 | stop | 16 of 16 | 2 / 13, 7 | 20 | 1, 1, 1 |
| b0b | 1600000 | 100000 | ok | 0 of 24 | | alive | none |
| b1pb | 1600000 | 100000 | stop | 24 of 24 | 1 / 14, 6 | 20 | 1, 1, 1 |
| b1pb-r2 | 1600000 | 100000 | stop | 24 of 24 | 1 / 14, 6 | 20 | 1, 1, 1 |

Columns: the watch reads with bit 18 set; the slot 0 ring's ticks before and after the fill's kick
entry, and dword 16 (passes counted with the ring full); marks: HostCtl dword 3 stop minus arm,
dword 8, `sw_events`. The tick gaps of the stopped jobs' rings were 49990 to 50001 and 99986 to
100003 units; each stop had dword 9 0, dword 14 0, TA3DCtl dword 57 0 and dword 58 0xaac267c2, CCB 3
and 3, `CR_EVENT_STATUS` 0x20040000, and P3 was not answered (504 ms, 0 new ring entries). Each was
recovered by one reset, the gate and the health exact (4 of 4). The ring logs the ticks after the
kick until it is full and dword 16 counts the rest, so at the slower clocks more of the 20 are
logged and fewer counted, the sum 20 every time.

**What it shows.** The EDM's 3D lockup check counts tick passes, not time: at half and a quarter of
the stock tick rate the stop came after the same 20 slot 0 passes after the fill's kick, about 40
and 80 ms after it, 4 of 4 held out, where a time of about 19.3 ms predicted 10 and 5 (H-TIME
refuted at both clocks). So the stop's time is 2 x `host_ctl.hw_recovery_sample_rate` ticks, as
R-6 reads in the code [RE]. The marks and bit 18 as a level do not depend on the clock (H-HWR,
H-LEVEL, 4 of 4). At `timer_clock` 1600000 the tick lands on a 100000-unit grid (b0b and 4 rings):
E084's rule (the gap is dword 6 / 16 units) holds at a clock it had not measured.

**What it does not show.** A count against another `hw_recovery_sample_rate` (dword 5 stayed 10;
the knob that would set it is a kernel change, not made). Anything about the clears (none in h2),
`CR_DPM_TASK_STATE` (cannot tell, as in E855), or which state arms the check.
