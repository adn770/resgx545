+++
id = "E857"
claim = "R5 stage h3 (r5-events, ring_skip3p.s at timer_clock 1600000; Q295, Q166): the fill without the skip (b0, control) completed with the tick alive and bit 18 never set; with slot 3's first end-of-render pass skipped once and ended with the phase end (b1e, b1e-r2, b1e-r3, held out), CR_EVENT_STATUS read 0x20040000 at the slot 3 entry, a host write of bit 15 to CR_EVENT_HOST_CLEAR left bit 18 set and a write of bit 18 about 18 ms later cleared it (0x20000000), one GETMISCINFO sent about 36 ms after the entry was answered in 147 to 206 us with its kick entry in the slot 0 ring and ticks after it (the EDM running), and still the tick stopped in 3 of 3 jobs after exactly 20 slot 0 passes after the fill's kick entry with the lockup marks (HostCtl dword 3 stop minus arm 1, dword 8 1, sw_events 1, TA3DCtl dword 58 0xaac267c2, CR_EVENT_STATUS 0x20000000, CCB 4 and 4); frozen verdict 'H-STATE consistent (4 row groups), H-ACK18 REFUTED; H-TICKS consistent; H-LEVEL consistent; H-W consistent (2 row groups), H-ALL REFUTED, H-NONE REFUTED', every control passing (39), 51 of 51 non-control rows decided"
unit = "edm"
method = "R5 session r5-events stage h3 (round 5, decisions R5-3 a, R5-4 a; plan closing5/events/exp-events-r5.md section 5), dataset edm-closing-r5-events, attempt out/a1 (run 2026-11-12 09:16:49 Mac time, gated on h2's kept stage.json, the session's last stage), the laptop, module, firmware, tool and task of E855, timer_clock 1600000 written and read back before each job's reset (dword 6 1600000 in each arm dump); B1E = h1's B1P with the clears moved: at the slot 3 entry seen in the page, one status read, then debugfs kregnow 0x0134 of bit 15 (0x8000) with reads asked 1 and 3 ms after it, then of bit 18 (0x40000) with the same reads (at the debugfs pace each read landed 10 to 18 ms after its write), then one GETMISCINFO through the kernel's miscinfo file, then the 150 ms watch (23 or 24 reads), the tick checked, a stop signed (signature twice, stop dumps before any write), P3, then reset, gate and health; b0 had no clears and no miscinfo; controls per B1E (they can fail): the miscinfo answered, its kick entry in the ring with a tick after it (the EDM running at the clears), the knob read back, the tick gap 100000 +-40, hold_recovery back to N; the stage went on after each of its three predicted stops (R5-4 a, no lead decision needed), stage exit 0, clock_back at the end (timer_clock 0 read back, gap 25000, 994 Hz), and the session's last line read timer_clock 0; predictions frozen in predictions/h3.tsv before the run: H-STATE (the arm is firmware state, sa9 bit 0 in R-6 [RE], which no host write to CR_EVENT_HOST_CLEAR touches and GETMISCINFO does not reset; R-6 and S0 read that dword 57 is written only by the two 3D kicks and the tick) against H-ACK18 (the unacknowledged bit 18 keeps the check armed: the tick alive at 150 ms, lockups 0); scored by the frozen score/score_r5e.py h3 (out/a1/score-h3.txt), re-run on the kept files on 2026-11-12 with byte-identical output"
tiers = ["HW", "RE", "infer"]
date = "2026-11-12"
data = ["edm-closing-r5-events:out/a1/h3/", "cited-scratch-private:cited/closing5/r6/"]
terms = [
    "Event Data Master (EDM)", "CR_EVENT_HOST_CLEAR", "CR_EVENT_STATUS.PIXELBE_END_RENDER",
    "host_ctl.ukernel_detected_lockups", "host_ctl.interrupt_flags", "ta3d_ctl.kick_clear_3d",
    "CR_EVENT_STATUS.SW_EVENT",
]
+++
**What ran.** E855 and E856 stop with the lockup marks after 20 passes whatever the clock, the
host's clears coming after the stop. Two readings of what keeps the check armed remained: the
handler's acknowledgement of bit 18, which the skipped handler never wrote (H-ACK18: a host clear
of bit 18 before the 20th pass ends the check, the tick survives), and firmware state that only
the skipped end-of-render path clears (H-STATE: R-6 reads it as sa9 bit 0 [RE]; a host write and a
GETMISCINFO change nothing, the stop comes at 20 with the marks). Stage h3 writes the clears at the
slot 3 entry, while the EDM still runs, and sends one GETMISCINFO after them, at the slowest clock
(1600000, the 20th pass about 80 ms after the kick) so that all of it lands well before the stop.
The same writes test Q166's H-W on a running EDM.

**Frozen verdict (as printed).** `SUMMARY: h3: B0 held; H-STATE consistent (4 row groups), H-ACK18
REFUTED; H-TICKS consistent (1 row groups); H-LEVEL consistent (1 row groups); H-W consistent (2
row groups), H-ALL REFUTED, H-NONE REFUTED; stops 3 ['b1e', 'b1e-r2', 'b1e-r3']; every control
PASS (39); 51 of 51 non-control rows decided; Q295/Q166 rows: held out: 36 held, 15 FAILED, 0
cannot tell/void; refuted ['H-ACK18', 'H-ACK18 (the unacknowledged bit 18 keeps the check armed:
the clears end it)', 'H-ALL', 'H-NONE']; control: 39 held, 0 FAILED, 0 cannot tell/void`
(out/a1/score-h3.txt). The 15 FAILED rows are the rivals' (H-ACK18 9, H-ALL 3, H-NONE 3).

**Results [HW].** Times in ms from the status read at the slot 3 entry (b1e; the replicates within
2 ms of it):

| step | b1e | b1e-r2 | b1e-r3 |
|---|---|---|---|
| slot 3 entry seen after the fill began | 4.53 | 4.58 | 4.59 |
| `CR_EVENT_STATUS` at the entry | 0x20040000 | 0x20040000 | 0x20040000 |
| after bit 15 (two reads) | 0x20040000 x2 | 0x20040000 x2 | 0x20040000 x2 |
| bit 18 written at | 18.3 | 18.3 | 18.3 |
| after bit 18 (two reads) | 0x20000000 x2 | 0x20000000 x2 | 0x20000000 x2 |
| GETMISCINFO sent at, answered after | 36.5, 147 us | 36.3, 206 us | 36.2, 205 us |
| kicks in ring; ticks after the fill's kick, logged + dw 16 | 2, 13 + 7 | 2, 13 + 7 | 2, 12 + 8 |
| watch after the miscinfo: bit 18 | 0 of 23 | 0 of 24 | 0 of 24 |
| stop: passes after the fill's kick | 20 | 20 | 20 |
| stop: dword 3, 8, `sw_events`, dword 58 | 1, 1, 1, 0xaac267c2 | the same | the same |
| stop: `CR_EVENT_STATUS`, CCB | 0x20000000, 4 4 | the same | the same |

b0 (the fill without the skip, no clears, no miscinfo) completed, its tick alive on the
100000-unit grid, bit 18 never set in 24 reads. Each stop had HostCtl dword 9 0 and dword 14 0,
TA3DCtl dword 57 0, and P3 was not answered (504 or 505 ms, 0 new ring entries); each was recovered
by one reset, the gate and the health exact (3 of 3). The CCB's 4 and 4 are the arm's two
GETMISCINFO, the fill and h3's miscinfo, all read.

**What it shows.** What keeps the EDM's 3D lockup check armed after the skipped slot 3 pass is not
the unacknowledged `PIXELBE_END_RENDER`: clearing bit 18 from the host 18 ms after the slot 3 entry,
with the EDM running, and a command served after it did not prevent the stop, which came at the
same 20 passes after the fill's kick with the same marks (H-STATE, 3 of 3 held out; H-ACK18
refuted). The arm is state of the firmware's own that a host clear and a GETMISCINFO leave alone,
as R-6 reads it [RE]: sa9 bit 0, set by the 3D kicks and cleared only by the end-of-render path the
skipped handler would have run (or by the recovery); and the GETMISCINFO kick did not restart the
count (dword 57 is written only by the 3D kicks and the tick, R-6 [RE]). On a running EDM a host
write to `CR_EVENT_HOST_CLEAR` clears the bits written and no others that were set: bit 15 left
bit 18 (and TIMER), bit 18 cleared bit 18 and left TIMER (H-W, 3 of 3; H-ALL and H-NONE refuted).
With E855 (the clears after the stop, 3 of 3) and E823 and E837, the clear is the bits written on
8 jobs, stopped or running. [infer] In an ordinary job the closed slot 3 handler's own write of
bit 18 is the acknowledgement of E547's short pulses, and its end-of-render path the end of the
3D's lockup check.

**What it does not show.** Bits of `CR_EVENT_HOST_CLEAR` other than 15 and 18, and statuses with
other bits set (only TIMER and bit 18 were set; Q111 holds the other bits). sa9 itself (no debugfs
file reads the EDM's sa registers): that the state is sa9 bit 0 rests on R-6's reading [RE], the
hardware showing only that it survives a host clear and a command. `CR_DPM_TASK_STATE` and the
poll after the lockup (cannot tell on the rgn4 kernel, E855). Whether a task of ours that clears
sa9 bit 0 at the end of a skipped slot 3 pass would keep the tick: not run (the verifier's rules on
writing sa9 were not read for it).
