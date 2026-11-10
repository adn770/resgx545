+++
id = "Q033"
question = "which hardware event sets bit 19 of the event word pa1 that the hardware hands a PDS event program, if any (none of the 138 job events of 14 jobs in E747 carried it, nor any of 8 4096x4096 jobs of E771 whether the TA's threshold was raised or not, with no rise of status bit 3 in the sampled timeline)"
unit = "edm"
kind = "hw"
value = "low"
phase = 10
evidence = ["E155", "E146", "E154", "E532", "E538", "E746", "E747", "E771"]
terms = ["CR_EVENT_STATUS", "CR_EVENT_HOST_CLEAR", "CR_EVENT_STATUS.DPM_INIT_END", "CR_EVENT_STATUS.DPM_STATE_STORE", "CR_EVENT_STATUS.DPM_CONTROL_LOAD", "CR_EVENT_STATUS.SW_EVENT", "CR_EVENT_KICK"]
+++

E146 reads PDS #13's `ir1` input, which the program passes on to the event task as `pa1`, as
`CR_EVENT_STATUS` bits at their own positions [infer]: its dispatch groups would then be
`DPM_INIT_END`, `DPM_CONTROL_STORE` and `DPM_STATE_STORE` (bits 22, 7, 4), `DPM_CONTROL_CLEAR`
(9), and so on. E155 reads the handlers that test those bits and finds that each acknowledges a
different status bit: in all seven acknowledged `pa1` bits (22, 21, 20, 10, 9, 7, 4) the value
written to `CR_EVENT_HOST_CLEAR` is status bit 22 minus the `pa1` bit. So `pa1` bit 22 clears
status bit 0, bit 9 clears bit 13 (`TA_FINISHED` in that reading) and bit 4 clears bit 18. E146
cannot be edited, so its reading of the positions stands corrected here as an open point: the
code favours the reversed order, and no run has fed the firmware an event.

Two `pa1` bits have no acknowledgement. Bit 19 is tested with the out-of-memory bits and posts
nothing (E154, E155); the reversed order makes it status bit 3. Bit 8 starts the kernel CCB
reader and writes no acknowledgement; the reversed order makes it status bit 14, the bit the
firmware raises itself as `SW_EVENT`, so the host's kick may be that bit seen from the other side
[infer]. Under the same-position reading bit 8 would be `DPM_CONTROL_LOAD`.

To settle it: run a firmware build whose event task first stores `pa0` and `pa1` to a free HostCtl
dword, then read that dword through the debugfs files after single events: a host kick through
`CR_EVENT_KICK` with no job queued, a TA job that finishes, and a job that overflows its parameter
buffer. A kick that reads as bit 8 and a TA finish as bit 9 confirm the reversed order; bits 14
and 13 confirm E146's. Sample `CR_EVENT_STATUS` around the same events to name the status bits
that set `pa1` bits 8 and 19, and whether bit 19's status bit stays set without an acknowledgement.

Narrowed in 11.21 to the hardware part. Which events the closed firmware's handlers acknowledge, and
what they do with bits 8 and 19, are the firmware's own behaviour and not the target; they stay
above as what is known. Open: the order and positions of the status bits in the word the hardware
passes to the PDS as its event input (the handlers' acknowledgements fit status bit 22 minus the
`pa1` bit [infer], and no run has fed the hardware an event while reading the word), and which
hardware events set input bits 8 and 19. Settling it needs a firmware build that stores the word
(the first step of the run above); the status bits as the host sees them, event by event, are Q111.

Narrowed again in 11.29 (not retired). The first step of the run above was made for one event: a
firmware task of ours in the general slot stored `pa0`, `pa1` and `pa2` of the 1 kHz tick, 2 of 2
runs, `pa0` = 2, `pa1` = 0x02000000 and `pa2` = 0x01061a70 (E532). The declared prediction, that a
tick has nothing in `pa1`, was falsified; bit 25 is outside PDS #13's 24-bit mask (the question on bit 25, answered by E746; the
reversed reading gives it no status bit, the same-position reading a status bit E146 does not
list), and neither bit 8 nor bit 19 was set by a tick. The kick through
`CR_EVENT_KICK`, the finishing TA job and the overflowing job were not run (the stage before them
stopped, E533), so the open part is as before for them: the order and positions of the status bits
in the word the hardware hands the PDS for a kick and for a job, and which events set bits 8 and 19.
Their run needs a logging wrapper that keeps the tick (Q152).

Narrowed in 11.30 (not retired). The kick through `CR_EVENT_KICK` with no job queued was run, three
times (a GETMISCINFO through the debugfs, E538): it reached the general slot only (slot 0, the
other three slots logged nothing, 3 of 3 runs) with `pa0` = 2, `pa1` = 0x03000000 and `pa2` =
0x01061a70, that is a tick's words (E532) with bit 24 added. The declared prediction, `pa1` bit 8 =
0x100 (the reversed reading: status bit 14 seen from the other side), failed, and so did its
falsifier, 0x4000 (E146's reading, bit 14): the kick sets neither bit 8 nor bit 14, and `pa1` bits
24 and 25 are above the 24 bits PDS #13 reads. A window of 50 ms of ticks logged nothing with bit
25 masked (3 of 3 windows, about 150 ticks). The TA job that finishes and the job that overflows
its parameter buffer were not run (the stage that would have run the first, Q2, did not run), so
the open part is as before for them: the order and positions of the status bits in the word the
hardware hands the PDS for a job, which events set input bits 8 and 19, and what bits 24 and 25
mean (the questions on bits 24 and 25, answered by E746).

Premise noted 2026-11-09 (from reading `asm/fwtask/events_m.s`, not a measurement). E538's stubs
keep, per slot, a hit flag and the last pa0, pa1 and pa2, not a count or a history: a second hit
in a slot overwrites the first. The kick's "pa1 bits 8 and 14 not set" is therefore for the last
non-tick hit of slot 0 in each of the 3 runs; a log that keeps every event in arrival order is
what would show whether a kick or a job delivers more than one.

Narrowed 2026-11-10 (S2, E746 and E747; the order and the positions are answered, bit 19 is not). A
task of ours that logs every pass of the four slots in arrival order, with a timer stamp, saw the
fill's end of render, the frozen witness, arrive in slot 3 with pa1 bit 4 in 3 of 3 fills (the
same-position reading predicted bit 18 in slot 0); the bit sets of the reversed order explained 132
of the 138 job events of 14 jobs and those of the same-position order 88, and every entry's slot was
PDS #13's dispatch of its own words (138 of 138, the instrument control): pa1 bit = 22 minus the
status bit, as E155 read the handlers. The host's kick through CR_EVENT_KICK is one event in slot 0
with pa0 = 0 and pa1 bit 8 (E746, a gated control, 3 of 3), a client job logs one such entry for
each command of the kernel's buffer that it causes, and E538's 'kick' words were the tick after the
kick; bits 24 and 25 are bits of a count byte that every event carries (the former questions on bits
25 and 24, answered by E746). A job's events reach the EDM one status bit at a time, each as a pass
of its own, in an order that was the same in every replicate of a kind (E747).

Open: the event that sets bit 19 (none of the 138 job events carried it, among them the two partial
renders that overflowed the parameter buffer, whose overflow path logged bits 21 and 10 in slot 2),
and the six entries outside E547's frozen sets (a copy's pa1 bit 4, a 64x64 triangle's bit 9). The
status registers as the host sees them, event by event, stay Q111's.

Note 2026-11-10 (an offline reading before the round 2 runs, not a measurement). The last write of
the init scripts, `EVENT_PDS_ENABLE` = 0x2204b00f (E006), has status bits 0, 1, 2, 3, 12, 13, 15,
18, 25 and 29 set [data]. Under pa1 bit = 22 minus the status bit (E155) those below 23 map to pa1
bits 22, 21, 20, 19, 10, 9, 7 and 4: E155's seven tested handlers plus bit 19, which E155 reads as
`DPM_REACHED_MEM_THRESH` (status bit 3) [infer]. So that event can arrive at the task: the enable
mask lets it through, which is not evidence that any job raises it. Lead [infer, no test]: status
bit 25 (`DPM_OUT_OF_MEMORY_ZLS`) would sit in `pa0` at bit 5 if pa0 bit = 30 minus the status bit,
a rule only the timer (pa0 bit 1) supports so far.

Narrowed 2026-11-10 (R1-events stages d0 and d1, E771; not retired). Neither candidate that the
note above allowed for the arrival of bit 19 held. In 8 jobs of a 4096x4096 render of 1500 vertices
under the ring of S2 (render_pb_pages 0x320, 0x3a0 and 0x422, 3, 3 and 2 runs) no entry of any ring
carried bit 19, no slot dropped an entry, and a register timeline read in parallel (about 5 us
between samples at the median, with a long tail) showed no rise of `CR_EVENT_STATUS` bit 3, while
the TA's threshold was raised at 0x320 in 3 of 3 (0x0624 0x2fe, dword 38 0x20) and not at 0x3a0 or
0x422, and the TA reached its threshold with 2 or 3 partial renders in every job. The bit-19 event
is therefore not tied to the raise (H-RAISE refuted) nor to the TA reaching its threshold
(H-THRESH refuted) on these jobs. The controls reproduced E747 (dispatch of every entry 100%).
Open: whether bit 19 ever reaches the task (H-NEVER, or an event shorter than the timeline's
sampling, or one the PDS does not hand on), and which hardware event sets it if so. The enable mask
of the note above lets it through, which is still not evidence that any job raises it.

**Correction 2026-11-10:** the value is lowered from medium to low. The only part still open is
whether any hardware event sets bit 19 of `pa1` (H-NEVER, untested): none of the 138 job events of
E747 carried it, nor any of the 8 jobs of E771, and no cheap row is left to reach it (E747, E771),
so the simulator loses little by not having the answer.
