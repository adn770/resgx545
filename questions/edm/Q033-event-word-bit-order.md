+++
id = "Q033"
question = "does the event word PDS #13 hands the EDM as pa1 carry CR_EVENT_STATUS bits in reverse order, and which events set its bits 8 and 19, that no handler acknowledges?"
unit = "edm"
phase = 10
evidence = ["E155", "E146", "E154"]
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
