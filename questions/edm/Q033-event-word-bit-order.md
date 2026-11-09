+++
id = "Q033"
question = "does the event input the hardware hands a PDS event program (ir1, seen as pa1 by the event task) carry CR_EVENT_STATUS bits in reverse order, and which hardware events set its bits 8 and 19?"
unit = "edm"
kind = "hw"
value = "medium"
phase = 10
evidence = ["E155", "E146", "E154", "E532", "E538"]
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
tick has nothing in `pa1`, was falsified; bit 25 is outside PDS #13's 24-bit mask (Q153; the
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
mean (Q157 and Q153).

Premise noted 2026-11-09 (from reading `asm/fwtask/events_m.s`, not a measurement). E538's stubs
keep, per slot, a hit flag and the last pa0, pa1 and pa2, not a count or a history: a second hit
in a slot overwrites the first. The kick's "pa1 bits 8 and 14 not set" is therefore for the last
non-tick hit of slot 0 in each of the 3 runs; a log that keeps every event in arrival order is
what would show whether a kick or a job delivers more than one.
