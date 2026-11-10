+++
id = "E823"
claim = "R3k stage e3b (K1, 4 jobs run of ring_skip3.s, 1 stop, last stage; Q111, Q166): the fill without the skip (B0 x3, controls) completed with one slot-3 end-of-render entry and the tick alive; with the end-of-render pass of slot 3 skipped once (B1: our own end in place of the closed handler, hold_recovery Y) the fill never completed (the tool timed out, job hung), the tick stopped with E537's busy signature (CR_CLKGATESTATUS 0x000ccfa0; the signature's EVENT_STATUS 0x20040000), CCB offsets 3 and 3, dword 14 0, the miscinfo of P3 not answered (504 ms): frozen verdict 'H-STOP3 (a skipped end-of-render handler stops the tick)'; the readings of CR_EVENT_STATUS bit 18 and of the host writes of CR_EVENT_HOST_CLEAR are frozen 'refuted [H-FREE3, H-LEVEL, H-PULSE, H-REFIRE, H-W (stop only: ... bit 29)], cannot tell [H-ALL, H-NONE, H-W]' because bit 18 read clear in the first of 9 watch reads; read after the run, bit 18 was set in 8 of 9 reads from 7.3 ms to the end of the 50 ms watch, a write of bit 15 left it set at 1 and 3 ms, a write of bit 18 cleared it at 1 and 3 ms and a write of bit 29 left CR_EVENT_STATUS bit 29 set; B2 (the firmware route) did not run"
unit = "platform"
method = "R3k session K1 (stage e3b; decisions R3-E1 and R3-E2, Q111 and Q166), dataset edm-closing-r3k-events, 2026-11-10, kernel 7.3.0-resgx545, the new module of round 3 (fork resgx545 8fc748b0, srcversion 230E0EF50FFFD606C53AE3C, installed = loaded, checked at each preflight; gma500_gfx.ko sha256 06bf58db6e1c78f2bd9858bcc7b9e63d752786e098e50b5c67345ce69f2ceb78 as recorded in env.json), stock firmware sha256 6a00268e9d4ca552c02e52651a42a2b4db3887d7fe626f209888369985162b0a, the laptop (host cedar) on the home LAN, not the direct cable, rebooted into the new module at 18:48 (boot-test-kernel.sh then test-session.sh, health ok); the final run of session K1 in one driver call from 19:29:52 Mac time (out/r3-kev.log: f 19:29:52, t 19:30:07, kb 19:30:19, e2b 19:30:56, e3h 19:31:10, e3a 19:31:23, e3b 19:31:39), each stage gated on the previous stage's kept stage.json, gated on e3a's kept stage.json; the task ring_skip3 (sha256 d0671a5f10eb2ad2..., 681 instructions, the ring task with a skip-once flag for slot 3's end-of-render pass, one `str #77` for the B2 route) armed in slots 0xf at each job after a reset; jobs B0 x3 (a 64x32 fill by the pinned ~/sgxfive-test-s1b, hold_recovery N, 50 ms of reads of CR_EVENT_STATUS and STATUS2 as fast as the debugfs reads), B1 once (skip 1, hold_recovery Y for the job, the same watch, then the tick checked and a stop signed first: the signature twice, the host writes through debugfs kregnow of 0x0134 with bit 15, then bit 18, then (after a stop) bit 29, each read 1 and 3 ms later, then P3 (one miscinfo) and the reset; hold_recovery read back N before the tool is collected), B2 (str #77, only if B1 kept the tick: not run); B1 is not replicated after a stop (the lead's fix before the freeze, R3-E2 a; PREFLIGHT.md DEVIATION 5); stop budget 2, one used; exit 0, 4 of 5 jobs run, health ok after the stage; the kernel log of the stage holds the expected hung and recovery lines of B1 (job 68 hung, recovering); scored by the frozen score/score_r3.py e3b (out/score-e3b.txt). Freeze history of the session (FROZEN.sha256 over every generator, scorer, runner, table, blob and prediction; PREDICTIONS.sha256 1f32e767... throughout): 1527b62e... (FROZEN.pre-logfix.sha256) until K0's second attempt, 463c251b... (FROZEN.pre-armlog.sha256; K0's four stages and K1's first attempt ran under it) until K1's first attempt, 1d6a3ad2... (FROZEN.sha256; K1 ran under it); each refreeze was made after a failed attempt and before the next one, with the mock test first, and changed no prediction file. The watch and CLEAR readings quoted below were read from the kept b1.json after the run (scratch reading, the values are those the runner recorded)"
tiers = ["HW", "infer"]
date = "2026-11-10"
data = ["edm-closing-r3k-events:out/e3b/"]
terms = ["CR_EVENT_HOST_CLEAR", "CR_EVENT_STATUS", "CR_EVENT_STATUS.PIXELBE_END_RENDER", "CR_EVENT_STATUS.TIMER", "Event Data Master (EDM)", "CR_CLKGATESTATUS"]
+++
**What ran.** The end of a render raises `CR_EVENT_STATUS` bit 18 (PIXELBE_END_RENDER) for 4 to 6
microseconds in ordinary jobs, which E547 reads as the time to the firmware's acknowledgement
[infer], and the end-of-render event reaches the EDM as an entry of slot 3 (E747). Stage e3b has
our task skip that slot-3 pass once (our own end, not the closed handler: nothing acknowledges),
reads the status for 50 ms (is bit 18 a pulse or a level held until acknowledged), checks whether
the tick survives (E793 and E817 say a pass ended without the exit's `phas` stops it), and then
writes the clear register from the host: bit 15 (not set), bit 18, and after a stop bit 29 (TIMER,
which a stopped EDM does not acknowledge). Frozen readings: H-STOP3 or H-FREE3 for the tick;
H-LEVEL (bit 18 reads 1 throughout) or H-PULSE (never); H-W, H-ALL, H-NONE for the writes.

**Frozen verdict (as printed).** `SUMMARY: e3b: H-STOP3 (a skipped end-of-render handler stops the
tick); stops 1 ['b1']; Q111 rows: held out: 3 held, 5 FAILED, 6 cannot tell/void; refuted
['H-FREE3', "H-LEVEL (bit 18 holds until acknowledged: E547's inference)", 'H-PULSE', 'H-REFIRE',
'H-W (stop only: the one unacknowledged bit of a stop clears and returns within 1 ms)']; cannot
tell ['H-ALL', 'H-NONE', 'H-W']; control: 12 held, 0 FAILED, 0 cannot tell/void`.

**Results [HW].**

| job | skip | watch of 50 ms (9 reads) | tool | tick | notes |
|---|---|---|---|---|---|
| b0, b0-r2, b0-r3 | 0 | bit 18 never; STATUS 0x20000000 | rc 0, fill ok | alive (1003 Hz) | slot-3 end-of-render entries 1, SKIPPED 0 |
| b1 | 1 | read 1 (0.01 ms): 0x20000000; reads 2 to 9 (7.31 to 55.95 ms): 0x20040000; bit 18 'mixed' | rc 1, 'job hung, context lost' after 1.02 s | stopped (tick and service-event counters not advancing in 3 samples) | slot-3 entries 1, SKIPPED 1 |
| b2 | - | - | - | - | not run (B1 did not keep the tick) |

B1's stop: signature busy, CR_CLKGATESTATUS 0x000ccfa0, USE0_SERV_EVENT 0x3f8, EVENT_TIMER
0x102b397, EVENT_STATUS 0x20040000; CCB write 3, read 3, dword 14 0; P3's miscinfo wrote the CCB
write offset to 4 (read offset 3) and was not answered (504 ms). The kernel logged 'job 68 hung,
recovering' (hold_recovery Y); hold_recovery read back N; the reset recovered; health ok.

The host writes of CR_EVENT_HOST_CLEAR (kregnow 0x0134), CR_EVENT_STATUS read 1 ms and 3 ms after:

| write | CR_EVENT_STATUS at 1 ms and 3 ms | bit 18 | TIMER bit 29 |
|---|---|---|---|
| bit 15 (0x8000) | 0x20040000, 0x20040000 | set | set |
| bit 18 (0x40000) | 0x20000000, 0x20000000 | clear | set |
| bit 29 (0x20000000) | 0x20000000, 0x20000000 | clear | set (no clear seen) |

**Why the frozen readings of bit 18 say refuted and cannot tell.** The watch's first read (0.01 ms
after its start) came before the fill's end of render, so bit 18 was clear in 1 of 9 reads and set
in the other 8, 'mixed'; the frozen rule scores H-LEVEL as 'all' reads set and H-PULSE as 'never'
and calls the CLEAR readings of a job with a not held bit 18 cannot tell. That is the frozen
verdict above. Post hoc and not frozen, reading the same records by the intent of the rows: bit 18
was set from the second read (7.31 ms) to the last (55.95 ms) while the handler was skipped, a
level held for at least 48 ms; a write of bit 15 left it set, a write of bit 18 cleared it (H-W;
H-ALL would have cleared it at bit 15 and H-NONE would not have cleared it at bit 18, so both
disagree); a write of bit 29 did not clear TIMER at 1 or 3 ms (H-W's 'clears and returns within 1
ms' not seen). These post hoc readings rest on the one job (B1, a stopped EDM, the register read
through debugfs 1 and 3 ms after the writes).

**What it shows and does not.** A skipped end-of-render pass stops the tick (1 job; with E817 the
reading is that nothing ended the pass with a phase end [infer]). While nothing acknowledges it,
bit 18 of CR_EVENT_STATUS stays set (post hoc: 48 ms and more), so the 4 to 6 microseconds of the
ordinary pulse are the firmware's acknowledgement and not the event's own duration [infer, E547's
reading, now with a held case]; a host write of the bit clears it, a write of another bit does
not. Not shown: whether the TIMER bit can be cleared (the write at 1 and 3 ms did not), the
firmware route (B2 not run), anything for a job with the closed handler (B0 only reads: bit 18
never seen by 9 reads about 7 ms apart, as E547's pulses are too short for that sampling).
