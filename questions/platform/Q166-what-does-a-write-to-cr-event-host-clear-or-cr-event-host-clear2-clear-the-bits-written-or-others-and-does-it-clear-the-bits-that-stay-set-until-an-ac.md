+++
id = "Q166"
question = "what does a write to CR_EVENT_HOST_CLEAR clear, beyond the bit 18 of E823 (is it the bits written and no others, on more than one job and bit, and does a write of a bit that stays set until an acknowledge clear it)"
unit = "platform"
kind = "hw"
value = "low"
phase = 11
evidence = ["E547", "E548", "E821", "E822", "E823"]
terms = ["CR_EVENT_HOST_CLEAR", "CR_EVENT_HOST_CLEAR2"]
+++

`CR_EVENT_HOST_CLEAR2` is answered: the bits written are the bits cleared, by the host (E821,
`kregnow 0x0114`) and by a task's `str #69` (E822), 3 of 3 rounds each, a later fill latching the
bit again (H-W; H-ALL and H-NONE refuted). The route does not matter for CLEAR2, so a `str` of the
other register is not needed to ask the question.

`CR_EVENT_HOST_CLEAR` (retyped from kernel to hw 2026-11-11, round 4, decision R4-3; the debugfs
write path the first text waited on exists since E821, and the firmware route is dropped): in one
stopped job (E823; post hoc, the frozen rows refuted or cannot tell) a host write of bit 18 cleared
`CR_EVENT_STATUS` bit 18 and a write of bit 15 did not, with the bit held as a level 7.3 ms to the
end of the 50 ms watch with the slot 3 handler skipped; a write of bit 29 left TIMER set at 1 and 3
ms. The firmware acknowledges the bits it handles within 4 to 6 microseconds (E547), which is why a
clear is seen only with the handler stopped or on a bit it does not acknowledge (the TIMER and bit
31, set whenever armed; STATUS2 TRIG_TA and TRIG_3D after a hang, E357).

Open: CLEAR on more than one job and one bit, and whether a write of a set bit other than 6 and 18
clears others. To settle it: with the debugfs `kregnow` write of the register, writes of one bit and
of its complement against a bit that is set and held (bit 18 with the slot 3 pass skipped, TRIG_TA
after a hang, TIMER), reading the two status registers; a hang is expected to need a reset to clear
(E357). Dropped from the text: `str #77` of the register (the firmware route; E822 showed for CLEAR2
that the route does not matter).
