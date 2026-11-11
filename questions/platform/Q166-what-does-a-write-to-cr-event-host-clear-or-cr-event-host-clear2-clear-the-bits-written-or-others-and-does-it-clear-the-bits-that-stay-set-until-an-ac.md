+++
id = "Q166"
question = "what does a write to CR_EVENT_HOST_CLEAR or CR_EVENT_HOST_CLEAR2 clear, the bits written or others, and does it clear the bits that stay set until an acknowledge (the timeline of a SW_EVENT lasts 4 to 136 microseconds)"
unit = "platform"
kind = "kernel"
phase = 11
evidence = ["E547", "E548", "E821", "E822", "E823"]
terms = ["CR_EVENT_HOST_CLEAR", "CR_EVENT_HOST_CLEAR2"]
+++

The hardware part of Q111 that needs a way for the host to write the clear registers, which the
kernel's debugfs does not offer: kreg writes a register at a time and kregnow only the two host
enables (E548); a clear cannot be read back, so the effect is seen in the status registers after the
write. The firmware acknowledges the bits it handles within 4 to 6 microseconds (E547), so the
experiment needs the firmware's handler stopped (own_arm is off and a debugfs `stop` exists) or a
bit the firmware does not acknowledge (the TIMER and bit 31, set whenever armed; STATUS2 TRIG_TA and
TRIG_3D after a hang, E357).

Open: what a write clears. To settle it: a debugfs write path for the two registers (a kernel
change, left for later), then writes of one bit and of the complement against a bit that is set and
held (TRIG_TA after a hang, TIMER), reading the two status registers; a hang is expected to need a
reset to clear (E357).

Narrowed 2026-11-10 (K1, E821 to E823). `CR_EVENT_HOST_CLEAR2`: after a loop fill latched
`CR_EVENT_STATUS2` at 0x440, a host write of bit 15 (`kregnow 0x0114`) left it, a write of bit 6
cleared it to 0x400, and a later fill latched it again, in 3 of 3 rounds (E821), and the same
through a task's `str #69` (E822, 3 of 3): the bits written are the bits cleared, by either route
(H-W; H-ALL, H-NONE refuted). `CR_EVENT_HOST_CLEAR`: in one stopped job (E823; post hoc, the frozen
rows refuted or cannot tell) a write of bit 18 cleared `CR_EVENT_STATUS` bit 18 and a write of bit
15 did not; a write of bit 29 left TIMER set at 1 and 3 ms. Open: CLEAR on more than one job and one
bit, whether a write of a set bit other than 6 and 18 clears others, `str #77`.
