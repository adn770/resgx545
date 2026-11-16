+++
id = "Q044"
question = "does bit 25 of CR_REG_0400 act on pack modes 22 and 34, whose stored values vary between runs (Q012), given that it inverts the alpha in exactly modes 0 to 2 and 4 to 6 of the others run (E268, E385, E1135), and do bits 11:8 one at a time change a pixel outside modes 0 and 4, when together they change none in any class run (E1136)?"
unit = "pbe"
kind = "hw"
value = "low"
phase = 11
evidence = ["E029", "E028", "E031", "E251", "E268", "E385", "E1135", "E1136"]
terms = ["CR_REG_0400", "CR_REG_0400.INVERT_BYTE3", "SIDEBAND.PACKMODE"]
+++

Answered in its main part (E385): the low byte of the word that loads CR_REG_0400 is the threshold
of
ARGB1555's one-bit alpha (pack mode 4): with an alpha ramp over x the stored bit is set above the
low byte and clear below it (0x00, 0x40, 0x80, 0xc0, 0xff, every triangle pixel, two runs). The
threshold was run in mode 4 only, and bit 25 in modes 4, 5 and 8 (it inverts the alpha in modes 4
and 5 and changes nothing in mode 8; E268 covers modes 0 to 3). Bits 11:8 change nothing in modes 0
and 4 and bits 7:0 nothing in mode 0.

What is left: an alpha equal to the low byte (no pixel had it); the low byte in the other modes with
one or more alpha bits, and bit 25 in the pack modes not run; what bits 11:8 do, if anything.

Narrowed 2026-11-16 (round 34, session r34-q044, E1135 and E1136; the question line is reworded).
It read "what do bits 11:0 of CR_REG_0400 (0x80 as built) do, when no value of them changes a
stored pixel in pack modes 0 to 3, and does bit 25 act on the other pack modes?". Bit 25, run in
every pack mode 4 to 63 but 14 against the mode's own 0x80 reference (E1135): it inverts the alpha
in modes 4, 5 and 6 (xor 0x80008000, 0xf000f000, 0xff00ff00) and changes nothing in 7 to 13, 15
to 21, 23 to 33 and 35 to 63 (H-SUBSET 51 of 52 held out, the failure mode 6; H-INV25, inverting
every alpha field, not supported). With E268 it acts in exactly modes 0 to 2 and 4 to 6. The low
byte (E1136): mode 4's alpha bit is set at an alpha equal to it, at nine values (H-GE 9 of 9, H-GT
refuted), so alpha >= low byte; it changes no pixel in modes 5 to 11 (H-THR1 26 of 26); 0xf80
changes none in modes 1, 2, 3, 5 to 11, 15, 20, 24, 26 and 27 (H-NULL 15 of 15). The frozen retire
rule (closing29/r34-q044 README) printed RETIRE. Left: modes 22 and 34, read only on the dwords
their two references repeat (22: 3 of 4091 change, of the 0x88 constant that varies between runs;
34: none of 4092), whose formats are Q012's; mode 14, which faults (E031); bits 11:8 one at a time
outside modes 0 and 4.
