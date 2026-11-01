+++
id = "Q166"
question = "what does a write to CR_EVENT_HOST_CLEAR or CR_EVENT_HOST_CLEAR2 clear, the bits written or others, and does it clear the bits that stay set until an acknowledge (the timeline of a SW_EVENT lasts 4 to 136 microseconds)"
unit = "platform"
kind = "kernel"
phase = 11
evidence = ["E547", "E548"]
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
