+++
id = "Q153"
question = "which state sets bit 25 of the event word pa1 that a 1 kHz tick hands the general task (E532: pa0 = 2, pa1 = 0x02000000, pa2 = 0x01061a70 in 2 of 2 runs), when PDS #13 looks only at ir1 bits 23:0 (E146) and E155 has the tick with nothing in ir1"
unit = "edm"
kind = "hw"
value = "low"
phase = 11
evidence = ["E532", "E146", "E155", "E538"]
terms = ["Event Data Master (EDM)"]
+++

E532 measured the tick's event words from a firmware task of ours: `pa1` is not 0. Bit 25 is outside
the 24-bit mask the PDS applies (E146), so it does not change the task chosen; under Q033's reversed
reading (status bit 22 minus the `pa1` bit) it has no status bit, and under the same-position
reading it is a status bit that E146 does not list. Open: whether the bit is set on every tick (each
run read one), whether other events carry it, and what it is. A logger for Q033's events must mask
it before it decides which slot an event is.

Narrowed in 11.30 (not retired). The host kick carries bit 25 too: its `pa1` was 0x03000000 in 3 of
3 runs, bit 24 as well (Q157), and the three runs and the two of E532 give `pa1` bit 25 in 5 of 5
events. In a 50 ms window of ticks nothing other than bit 25 was set in `pa1` (the stubs log only
when another bit is, 3 of 3 windows, E538), but the stubs mask bit 25, so whether every tick has it
is not shown. Open: whether any event lacks it, whether TA and 3D events carry it, and what it is.
